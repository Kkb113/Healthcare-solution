"""Structured operational logs carry identifiers and counts, never payloads."""

import json
import logging

SAFE_FIELDS = {
    "event",
    "component",
    "environment",
    "run_id",
    "request_id",
    "status",
    "row_count",
    "duration_ms",
    "code",
    "resource_id",
    "contract_version",
}


def event(logger: logging.Logger, name: str, **fields):
    if set(fields) - SAFE_FIELDS:
        raise ValueError(
            "Unreviewed log field; payload/token/PHI logging is prohibited"
        )
    logger.info(json.dumps({"event": name, **fields}, sort_keys=True))
