"""Deterministic patient calendar constraints before source facts are published."""
from datetime import timedelta


def patient_slot(desired, duration, occupied, lower, cutoff, *, allow_backwards=False, fallback_weekday_zone=None):
    """Preserve forward placement; resolve a boundary trap in earlier free time.

    This plans an unpublished visit, not a retroactive edit to a delivered
    appointment. A visit is never dropped, overlapped or moved past cutoff to
    satisfy a cohort budget. Urgent linked admission chains cannot move backward.
    """
    if duration.total_seconds() <= 0 or not lower <= desired < cutoff:
        raise ValueError('invalid patient calendar interval')
    def free(at):
        return all(not (at < end and begin < at+duration) for begin,end in occupied)
    cursor = desired
    while not free(cursor):
        cursor += timedelta(days=1)
        if cursor >= cutoff:
            break
    if cursor < cutoff:
        return cursor
    if allow_backwards:
        cursor = desired-timedelta(days=1)
        while cursor >= lower:
            weekday = fallback_weekday_zone is None or cursor.astimezone(fallback_weekday_zone).weekday()<5
            if weekday and free(cursor):
                return cursor
            cursor -= timedelta(days=1)
    raise ValueError('connected trajectory has no free in-window slot')
