"""CalendarDayUtc — pure UTC calendar slice for 24/7 assets (contract §5)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .exceptions import TimestampSemanticsMismatch


def _coerce_date(value) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise TimestampSemanticsMismatch(
                f"CalendarDayUtc requires YYYY-MM-DD; cannot parse {value!r}: {exc}"
            ) from exc
    raise TimestampSemanticsMismatch(
        f"CalendarDayUtc requires date or YYYY-MM-DD str; got {type(value).__name__}"
    )


@dataclass(frozen=True)
class CalendarDayUtc:
    date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "date", _coerce_date(self.date))

    def to_iso(self) -> str:
        return self.date.isoformat()

    def _guard(self, other: object) -> None:
        if not isinstance(other, CalendarDayUtc):
            raise TimestampSemanticsMismatch(
                f"cannot compare CalendarDayUtc with {type(other).__name__}"
            )

    def __lt__(self, other: object) -> bool:
        self._guard(other)
        return self.date < other.date

    def __le__(self, other: object) -> bool:
        self._guard(other)
        return self.date <= other.date

    def __gt__(self, other: object) -> bool:
        self._guard(other)
        return self.date > other.date

    def __ge__(self, other: object) -> bool:
        self._guard(other)
        return self.date >= other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CalendarDayUtc):
            return False
        return self.date == other.date

    def __hash__(self) -> int:
        return hash(("calendar_day_utc", self.date))
