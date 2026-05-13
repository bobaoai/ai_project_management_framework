"""Comparison helpers — fail-loud per contract §0 R1 + charter §IV.

Two timestamps may be compared only if their typed wrapper matches exactly.
For SessionDateMarket that includes matching `market_tz` (handled by the wrapper).
"""

from __future__ import annotations

from typing import Any

from .exceptions import TimestampSemanticsMismatch


def assert_compatible(a: Any, b: Any) -> None:
    if type(a) is not type(b):
        raise TimestampSemanticsMismatch(
            f"incompatible timestamp types: {type(a).__name__} vs {type(b).__name__}"
        )


def gt(a: Any, b: Any) -> bool:
    assert_compatible(a, b)
    return a > b


def lt(a: Any, b: Any) -> bool:
    assert_compatible(a, b)
    return a < b


def eq(a: Any, b: Any) -> bool:
    assert_compatible(a, b)
    return a == b
