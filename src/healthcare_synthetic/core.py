"""Deterministic generation primitives; independent validators do not import this module."""
from __future__ import annotations

import calendar
import hashlib
import heapq
import hmac
import json
import unicodedata
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from importlib import metadata, resources
from io import BytesIO
from zoneinfo import ZoneInfo

UTC = timezone.utc
TZ_HASH = "c27b739ff46a7df0594e120d725b439217e11e44ea9a50cdc49130383b5482e7"


def _normal(value):
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("nonfinite decimal")
        return format(value, "f")
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("naive instant")
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list) or isinstance(value, tuple):
        return [_normal(v) for v in value]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise ValueError("JSON keys must be text")
        result = {}
        for key, item in value.items():
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in result:
                raise ValueError("Unicode-normalized key collision")
            result[normalized_key] = _normal(item)
        return result
    raise ValueError(f"unsupported canonical value: {type(value).__name__}; use exact decimal strings")


def canonical(value) -> str:
    return json.dumps(_normal(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def ordered_rows(rows):
    """Sort whole scalar rows, preserving duplicates for validators to find."""
    return sorted((_normal(row) for row in rows), key=canonical)


def stable_id(namespace: str, *key) -> str:
    if not namespace or not key or any(k is None for k in key):
        raise ValueError("identity requires a namespace and nonnull typed keys")
    return namespace + "_" + digest([namespace, *key])[:32]


def draw(seed: int, entity: str, stream: str, index: int = 0, upper: int = 2**32) -> int:
    """Counter stream with rejection sampling (no mutable/global RNG or modulo bias)."""
    if (type(seed) is not int or type(index) is not int or type(upper) is not int
            or index < 0 or not 0 < upper <= 2**256 or not entity or not stream):
        raise ValueError("invalid stream parameters")
    ceiling = 2**256 - (2**256 % upper)
    attempt = 0
    while True:
        payload = canonical([entity, stream, index, attempt]).encode("utf-8")
        sample = int.from_bytes(hmac.new(str(seed).encode("ascii"), payload, hashlib.sha256).digest(), "big")
        if sample < ceiling:
            return sample % upper
        attempt += 1


def money(value) -> Decimal:
    if isinstance(value, float):
        raise ValueError("binary float is not money")
    amount = Decimal(value)
    if not amount.is_finite():
        raise ValueError("nonfinite money")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def allocate_cents(total, weights: dict[str, str]) -> dict[str, Decimal]:
    """Largest remainder; deterministic key tie breaks; supports signed reversals."""
    amount = money(total)
    if not weights or any(not Decimal(w).is_finite() or Decimal(w) < 0 for w in weights.values()):
        raise ValueError("nonnegative nonempty weights required")
    denominator = sum(map(Decimal, weights.values()))
    if denominator <= 0:
        raise ValueError("zero allocation denominator")
    cents = int(abs(amount) * 100)
    raw = {k: Decimal(cents) * Decimal(w) / denominator for k, w in weights.items()}
    floor = {k: int(v.to_integral_value(rounding=ROUND_FLOOR)) for k, v in raw.items()}
    remainder = cents - sum(floor.values())
    for key in sorted(raw, key=lambda k: (-(raw[k] - floor[k]), k))[:remainder]:
        floor[key] += 1
    sign = -1 if amount < 0 else 1
    return {k: Decimal(sign * v) / 100 for k, v in sorted(floor.items())}


def instant(text: str) -> datetime:
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("UTC offset is required")
    return value.astimezone(UTC)


def chicago() -> ZoneInfo:
    if metadata.version("tzdata") != "2025.2":
        raise ValueError("runtime lock requires tzdata==2025.2")
    data = resources.files("tzdata").joinpath("zoneinfo/America/Chicago").read_bytes()
    if hashlib.sha256(data).hexdigest() != TZ_HASH:
        raise ValueError("Chicago time-zone bytes differ from runtime lock")
    return ZoneInfo.from_file(BytesIO(data), key="America/Chicago")


def local_instant(text: str, fold: int | None = None) -> datetime:
    naive = datetime.fromisoformat(text)
    if naive.tzinfo is not None or fold not in (None, 0, 1):
        raise ValueError("local input must be naive and fold must be 0/1")
    zone = chicago()
    candidates = {}
    for f in (0, 1):
        candidate = naive.replace(tzinfo=zone, fold=f).astimezone(UTC)
        if candidate.astimezone(zone).replace(tzinfo=None) == naive:
            candidates[f] = candidate
    if not candidates:
        raise ValueError("nonexistent local time")
    if len(set(candidates.values())) > 1 and fold is None:
        raise ValueError("ambiguous local time requires explicit fold")
    return candidates[0 if fold is None else fold]


def age_on(birth: str, service_date: str) -> int:
    dob, day = date.fromisoformat(birth), date.fromisoformat(service_date)
    # Frozen Phase 0 convention: February 28 in non-leap years.
    if day < dob:
        raise ValueError("service precedes birth")
    birthday = (2, 28) if (dob.month, dob.day) == (2, 29) and not calendar.isleap(day.year) else (dob.month, dob.day)
    return day.year - dob.year - ((day.month, day.day) < birthday)


def temporal_lookup(rows, key: str, identity: str, valid_at: str, known_at: str):
    valid, known = instant(valid_at), instant(known_at)
    candidates = [row for row in rows if row[key] == identity
                  and instant(row["valid_from"]) <= valid
                  and (row.get("valid_to") is None or valid < instant(row["valid_to"]))
                  and instant(row["known_from"]) <= known
                  and (row.get("known_to") is None or known < instant(row["known_to"]))]
    if len(candidates) != 1:
        raise ValueError(f"temporal reference resolves {len(candidates)} rows")
    return candidates[0]


def code_at(rows, domain, code, service_date, known_at):
    day, known = date.fromisoformat(service_date), instant(known_at)
    matches = [r for r in rows if r["domain"] == domain and r["code"] == code
               and date.fromisoformat(r["valid_from"]) <= day < date.fromisoformat(r["valid_to"])
               and instant(r["published_at"]) <= known]
    if len(matches) != 1:
        raise ValueError(f"code resolves {len(matches)} released versions")
    return matches[0]


class Clock:
    """Monotonic UTC clock. Equal-time events use explicit priority and stable ID."""
    def __init__(self, start: str, end: str):
        self.now, self.end = instant(start), instant(end)
        if self.now > self.end:
            raise ValueError("invalid clock boundary")
        self._queue, self._ids = [], set()

    def schedule(self, event_id, at, priority, payload):
        when = instant(at)
        if event_id in self._ids or not self.now <= when <= self.end:
            raise ValueError("duplicate event or event outside clock boundary")
        self._ids.add(event_id)
        heapq.heappush(self._queue, (when, priority, event_id, _normal(payload)))

    def pop(self):
        when, priority, event_id, payload = heapq.heappop(self._queue)
        self.now = when
        return {"event_id": event_id, "at": _normal(when), "priority": priority, "payload": payload}

    def __bool__(self):
        return bool(self._queue)
