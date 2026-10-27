"""Explicitly targeted Azure/Databricks helpers and destructive-plan guardrails."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/foundation-validation"
CONFIG = ROOT / "platform/config/infrastructure.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_binding() -> dict:
    """Bind bounded execution reports to code/config, never to state or patient data."""
    paths = set()
    for pattern in [
        "platform/infra/**/*.tf",
        "platform/infra/**/backend.hcl",
        "platform/infra/**/.terraform.lock.hcl",
        "platform/scripts/*foundation*.py",
        "platform/tests/unit/test_foundation.py",
    ]:
        paths.update(ROOT.glob(pattern))
    paths.update(
        ROOT / name
        for name in [
            "platform/config/infrastructure.json",
            "platform/config/identity-provisioning.json",
            "platform/config/foundation-resources.json",
            "platform/scripts/bootstrap-scim-credential.ps1",
            "platform/docs/prerequisite-readiness.md",
            ".github/workflows/foundation-validation.yml",
        ]
    )
    hashes = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(
            path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        for path in sorted(paths)
    }
    return {
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "input_hashes": hashes,
    }


def azure(arguments: list[str], subscription: str, *, timeout=120):
    """No implicit default subscription and no shell-constructed JSON."""
    if subscription not in {
        load(CONFIG)["workspace_subscription"],
        load(CONFIG)["model_subscription"],
    }:
        raise ValueError("Unapproved Azure subscription")
    executable = shutil.which("az")
    if not executable:
        raise RuntimeError("Azure CLI unavailable")
    result = subprocess.run(
        [executable, *arguments, "--subscription", subscription, "--output", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        # Never print a token-bearing command or raw credential response.
        raise RuntimeError(
            f"Azure {' '.join(arguments[:3])} failed (exit {result.returncode}): {result.stderr[:800]}"
        )
    return json.loads(result.stdout) if result.stdout.strip() else None


class CloudHttpError(RuntimeError):
    def __init__(self, status: int, code: str):
        self.status = status
        self.code = code
        super().__init__(f"Cloud request failed: HTTP {status} / {code}")


class AzureRest:
    """OAuth tokens remain process-local; HTTPS destinations are explicitly scoped."""

    def __init__(self, subscription: str, audience: str, allowed_hosts: set[str]):
        self.subscription = subscription
        self.audience = audience
        self.allowed_hosts = allowed_hosts
        self._token = None

        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        # Never forward an OAuth header to a redirect target, even on a read.
        self.opener = build_opener(NoRedirect())

    def request(self, method: str, url: str, *, body=None, headers=None, retries=3):
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname not in self.allowed_hosts
            or parsed.username
            or parsed.password
            or parsed.port not in {None, 443}
        ):
            raise ValueError("Unapproved cloud destination")
        if self._token is None:
            self._token = azure(
                ["account", "get-access-token", "--resource", self.audience],
                self.subscription,
            )["accessToken"]
        extra = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            **(headers or {}),
        }
        payload = (
            body
            if isinstance(body, bytes)
            else json.dumps(body).encode()
            if body is not None
            else None
        )
        for attempt in range(retries + 1):
            try:
                with self.opener.open(
                    Request(url, data=payload, headers=extra, method=method), timeout=60
                ) as response:
                    data = response.read()
                    return response.status, dict(response.headers), data
            except HTTPError as error:
                data = error.read()
                try:
                    code = json.loads(data).get("error", {}).get("code", "UNKNOWN")
                except (ValueError, AttributeError):
                    code = error.headers.get("x-ms-error-code", "UNKNOWN")
                if (
                    error.code in {429, 500, 502, 503, 504}
                    and attempt < retries
                    and (
                        method in {"GET", "HEAD"}
                        or method == "POST"
                        and "/Microsoft.CostManagement/query?" in url
                    )
                ):
                    # POST retries are used only for read-only Cost Management queries.
                    time.sleep(min(10, 2**attempt))
                    continue
                raise CloudHttpError(error.code, code) from None
        raise RuntimeError("Unreachable retry state")


def databricks_clients():
    from databricks.sdk import AccountClient, WorkspaceClient

    target = load(ROOT / "platform/config/workspace.json")
    os.environ["ARM_SUBSCRIPTION_ID"] = target["subscription_id"]
    return AccountClient(profile=target["account_profile"]), WorkspaceClient(
        profile=target["workspace_profile"]
    )


def review_plan(plan: dict, module: str) -> list[dict]:
    """Require a closed resource/type/name scope; never apply a destroy/replacement."""
    if module not in load(CONFIG)["terraform_modules"]:
        raise ValueError("Unknown Terraform module")
    allowed = {
        "foundation": {
            "azurerm_resource_group",
            "azurerm_storage_account",
            "azurerm_storage_container",
            "azurerm_storage_management_policy",
            "azurerm_key_vault",
            "azurerm_databricks_access_connector",
            "azurerm_role_assignment",
            "azuread_group",
            "azuread_application",
            "azuread_service_principal",
            "azuread_application_federated_identity_credential",
            "azurerm_consumption_budget_subscription",
        },
        "model-access": {
            "azurerm_resource_group",
            "azurerm_cognitive_account",
            "azurerm_cognitive_deployment",
            "azurerm_databricks_access_connector",
            "azurerm_role_assignment",
            "azurerm_consumption_budget_resource_group",
        },
        "workspace": {"databricks_storage_credential", "databricks_external_location"},
    }
    result = []
    for item in plan.get("resource_changes", []):
        if item.get("mode") == "data":
            continue
        actions = item["change"]["actions"]
        if "delete" in actions or any(
            action not in {"no-op", "read", "create", "update"} for action in actions
        ):
            raise ValueError(f"Destructive/unknown plan action: {item['address']}")
        if item["type"] not in allowed[module]:
            raise ValueError(f"Resource outside approved foundation: {item['type']}")
        after = item["change"].get("after") or {}
        exact_names = {
            "azurerm_resource_group": "rg-hcp-model-access"
            if module == "model-access"
            else "rg-hcp-dev",
            "azurerm_storage_account": "sthcpd054dev",
            "azurerm_key_vault": "kv-hcp-d054-dev",
            "azurerm_cognitive_account": "aoai-hcp-luna-0725fcd1",
        }
        if (
            item["type"] in exact_names
            and after.get("name") != exact_names[item["type"]]
        ):
            raise ValueError("Resource identity escaped its approved name")
        if (
            item["type"] == "azurerm_storage_container"
            and after.get("name") not in load(CONFIG)["containers"]
        ):
            raise ValueError("Unapproved storage container")
        if item["type"] == "azurerm_role_assignment":
            allowed_roles = {
                "Storage Blob Data Contributor",
                "Contributor",
                "Reader",
                "Key Vault Secrets Officer",
                "Cognitive Services OpenAI User",
            }
            if after.get("role_definition_name") not in allowed_roles:
                raise ValueError("Unapproved privilege escalation")
            scope = (after.get("scope") or "").lower()
            config = load(CONFIG)
            approved_groups = [
                f"/subscriptions/{config['workspace_subscription']}/resourcegroups/rg-hcp-dev",
                f"/subscriptions/{config['model_subscription']}/resourcegroups/rg-hcp-model-access",
            ]
            if not (
                any(
                    scope == group or scope.startswith(group + "/")
                    for group in approved_groups
                )
                or scope
                == load(ROOT / "platform/config/workspace.json")[
                    "workspace_resource_id"
                ].lower()
            ):
                raise ValueError("Role assignment escaped healthcare scope")
        if item["type"] == "azuread_application_federated_identity_credential":
            identity = load(ROOT / "platform/config/foundation-resources.json")
            if (
                after.get("subject") != identity["oidc_subject"]
                or after.get("issuer") != "https://token.actions.githubusercontent.com"
                or after.get("audiences") != ["api://AzureADTokenExchange"]
            ):
                raise ValueError("Federated trust widened beyond main branch")
        group = after.get("resource_group_name")
        if group and group != (
            "rg-hcp-model-access" if module == "model-access" else "rg-hcp-dev"
        ):
            raise ValueError("Resource escaped its healthcare resource group")
        if item["type"] == "azurerm_storage_management_policy":
            rules = after.get("rule", [])
            if len(rules) != 1 or rules[0]["filters"][0]["prefix_match"] != [
                "landing/"
            ]:
                raise ValueError("Lifecycle policy must scope only landing/")
            base = rules[0]["actions"][0]["base_blob"][0]
            if base.get(
                "tier_to_cool_after_days_since_modification_greater_than"
            ) != 90 or any(
                key.startswith("delete_") and value not in {None, -1}
                for key, value in base.items()
            ):
                raise ValueError("Unexpected lifecycle retention/deletion")
        if (
            module == "model-access"
            and item["type"] == "azurerm_cognitive_deployment"
            and actions != ["no-op"]
        ):
            raise ValueError("Phase 1 must preserve the tested exact-model deployment")
        result.append(
            {"address": item["address"], "type": item["type"], "actions": actions}
        )
    return result
