"""Single lifecycle adapter for isolated readiness model gateway objects.

Azure resources remain Terraform-owned. This adapter owns only the readiness
schema, service credential, provider and model service; no business data/grants.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service import catalog as c

ROOT = Path(__file__).resolve().parents[2]
PARENT = "intellify_healthcare_dbw.readiness"
CREDENTIAL = "hcp_luna_gateway"
CONNECTOR = "/subscriptions/0725b5e7-75db-4c60-b5e9-928c3df3fcd1/resourceGroups/rg-hcp-model-access/providers/Microsoft.Databricks/accessConnectors/ac-hcp-luna-gateway"


def main() -> int:
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    os.environ["ARM_SUBSCRIPTION_ID"] = config["subscription_id"]
    client = WorkspaceClient(profile=config["workspace_profile"])
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL",
        "objects": [],
    }
    try:
        try:
            client.schemas.get(PARENT)
        except NotFound:
            client.schemas.create(
                name="readiness",
                catalog_name="intellify_healthcare_dbw",
                comment="Healthcare prerequisite fixtures; managed by configure_model_gateway.py",
            )
        try:
            credential = client.credentials.get_credential(CREDENTIAL)
            if (
                credential.azure_managed_identity.access_connector_id.lower()
                != CONNECTOR.lower()
            ):
                raise ValueError(
                    "Existing credential refers to a different access connector"
                )
        except NotFound:
            client.credentials.create_credential(
                name=CREDENTIAL,
                purpose=c.CredentialPurpose.SERVICE,
                azure_managed_identity=c.AzureManagedIdentity(
                    access_connector_id=CONNECTOR
                ),
                comment="Luna inference only; no API key; managed by configure_model_gateway.py",
            )
        provider_name = f"model-provider-services/{PARENT}.azure_luna"
        try:
            provider = client.ai_gateway.get_model_provider_service(name=provider_name)
            if (
                provider.config.azure_openai.direct.service_credential.name
                != f"credentials/{CREDENTIAL}"
            ):
                raise ValueError("Existing provider has an unexpected credential")
        except NotFound:
            client.ai_gateway.create_model_provider_service(
                parent=f"schemas/{PARENT}",
                model_provider_service_id="azure_luna",
                model_provider_service=c.ModelProviderService(
                    comment="Exact Luna, keyless Azure route; readiness adapter owned",
                    config=c.ModelProviderServiceConfig(
                        provider_type=c.ModelProviderServiceConfigExternalModelProviderType.EXTERNAL_MODEL_PROVIDER_TYPE_AZURE_OPENAI,
                        azure_openai=c.ModelProviderServiceConfigAzureOpenAiProviderConfig(
                            direct=c.ModelProviderServiceConfigAzureOpenAiProviderDirectConfig(
                                base_url="https://aoai-hcp-luna-0725fcd1.openai.azure.com",
                                service_credential=c.ModelProviderServiceConfigServiceCredential(
                                    name=f"credentials/{CREDENTIAL}"
                                ),
                            )
                        ),
                        allow_all_targets=False,
                        targets=[
                            c.ModelProviderServiceConfigModelTargetConfig(
                                model="gpt-6-luna",
                                native_api_types=["openai/v1/responses"],
                            )
                        ],
                    ),
                ),
            )
        service_name = f"model-services/{PARENT}.gpt_6_luna"
        try:
            service = client.ai_gateway.get_model_service(name=service_name)
            if (
                service.config.routing.destinations[
                    0
                ].external_model_config.model_provider_service
                != provider_name
            ):
                raise ValueError("Existing service refers to an unexpected provider")
        except NotFound:
            client.ai_gateway.create_model_service(
                parent=f"schemas/{PARENT}",
                model_service_id="gpt_6_luna",
                model_service=c.ModelService(
                    comment="Exact GPT-6 Luna, Azure DataZoneStandard; readiness adapter owned",
                    config=c.ModelServiceConfig(
                        routing=c.ModelServiceConfigRoutingConfig(
                            destinations=[
                                c.ModelServiceConfigDestinationConfig(
                                    name="luna",
                                    traffic_percentage=100,
                                    destination_type=c.ModelServiceConfigDestinationConfigDestinationType.DESTINATION_TYPE_EXTERNAL_FOUNDATION_MODEL,
                                    external_model_config=c.ModelServiceConfigExternalModelConfig(
                                        model_provider_service=provider_name,
                                        target=c.ModelProviderServiceConfigModelTargetConfig(
                                            model="gpt-6-luna",
                                            native_api_types=["openai/v1/responses"],
                                        ),
                                    ),
                                )
                            ]
                        )
                    ),
                ),
            )
        report.update(
            status="PASS",
            objects=[PARENT, f"credentials/{CREDENTIAL}", provider_name, service_name],
            authentication="Unity Catalog service credential / Azure managed identity; no API key",
        )
    except Exception as error:  # noqa: BLE001 - CLI boundary records failure and cleanup
        report["error"] = str(error)[:2000]
    destination = ROOT / "output/platform-readiness/model-gateway-configuration.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
