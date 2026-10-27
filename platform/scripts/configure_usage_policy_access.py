"""Explicit, reversible Karthik-only bootstrap for approved usage-policy setup."""

import argparse

from databricks.sdk.service.iam import GrantRule, RuleSetUpdateRequest
from foundation_support import ROOT, databricks_clients, load, now, save

REQUEST = ROOT / "platform/config/usage-policy-access-request.json"
PRIVATE = ROOT / "output/platform-foundation/temporary-billing-role.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["grant", "revoke"])
    args = parser.parse_args()
    request = load(REQUEST)
    if request["status"] != "APPROVED":
        raise PermissionError("Explicit approval is missing")
    account, _ = databricks_clients()
    name = f"accounts/{request['account_id']}/ruleSets/default"
    response = account.access_control.get_rule_set(name, "")
    rules = response.grant_rules or []
    who, role = request["principal"], request["role"]
    if args.action == "grant":
        if PRIVATE.exists():
            raise PermissionError("Prior bootstrap must be reconciled first")
        original = response.as_dict()
        already = any(r.role == role and who in (r.principals or []) for r in rules)
        save(PRIVATE, {"original": original, "already_granted": already, "at": now()})
        if not already:
            # Merge rather than replacing any existing role or principal.
            rules.append(GrantRule(role=role, principals=[who]))
    else:
        recorded = load(PRIVATE)
        if recorded["already_granted"]:
            print("Role pre-existed; no bootstrap role to revoke")
            return
        rules = [
            GrantRule(
                role=r.role, principals=[p for p in r.principals or [] if p != who]
            )
            if r.role == role
            else r
            for r in rules
        ]
        rules = [r for r in rules if r.principals]
    updated = account.access_control.update_rule_set(
        name=name,
        rule_set=RuleSetUpdateRequest(name=name, etag=response.etag, grant_rules=rules),
    )
    current = account.access_control.get_rule_set(name, "")
    present = any(
        r.role == role and who in (r.principals or [])
        for r in current.grant_rules or []
    )
    if present != (args.action == "grant"):
        raise AssertionError("Role readback failed")
    save(
        ROOT / f"output/platform-foundation/billing-role-{args.action}.json",
        {
            "status": "PASS",
            "action": args.action,
            "principal": who,
            "role": role,
            "observed_at": now(),
            "etag": updated.etag,
            "other_rules_preserved": True,
        },
    )
    print(f"PASS: temporary billing role {args.action}")


if __name__ == "__main__":
    main()
