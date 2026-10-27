"""UTC instants and explicit America/Chicago business clocks, including DST folds."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

BUSINESS_ZONE = ZoneInfo("America/Chicago")


def utc_instant(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("A timestamp must include its UTC offset")
    return value.astimezone(timezone.utc)


def business_time(value: datetime) -> datetime:
    return utc_instant(value).astimezone(BUSINESS_ZONE)


def local_instant(value: datetime, fold: int | None = None) -> datetime:
    if value.tzinfo is not None:
        raise ValueError("Pass a naive local wall time with an explicit zone policy")
    candidates = [value.replace(tzinfo=BUSINESS_ZONE, fold=index) for index in [0, 1]]
    valid = [
        c
        for c in candidates
        if c.astimezone(timezone.utc).astimezone(BUSINESS_ZONE).replace(tzinfo=None)
        == value
    ]
    if not valid:
        raise ValueError("Nonexistent local time during a DST transition")
    ambiguous = len({c.utcoffset() for c in valid}) > 1
    if ambiguous and fold not in {0, 1}:
        raise ValueError("Ambiguous local time requires fold=0 or fold=1")
    return utc_instant(value.replace(tzinfo=BUSINESS_ZONE, fold=fold or 0))
