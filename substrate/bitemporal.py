"""
substrate.bitemporal -- "as-of" temporal queries.

Port of exp_bitemporal_asof_1M_v1.py + exp_api_as_of_checkpoint_v1.py.

CORE IDEA:
Each fact has a (valid_time, value) tuple. An as-of(t) query returns the latest version
with valid_time <= t. Implemented via sorted-index bisect over (valid_time, value) array.

Properties (validated cycle 145):
- as-of correctness = 1.000 at N=1M versions
- per-query latency = 0.003 ms at 1M versions

Demo enabling: temporal consistency, audit trails ("what did we believe last Tuesday?")

KNOWN LIMITATION (v1 demo): ties on valid_time are broken by INSERTION ORDER, not by
transaction_time. PP-104 bitemporal_asof_1M HP did not stress test ties, so this is
acceptable for v1 demo correctness. Production bitemporal proper requires (valid_time,
transaction_time) tuples; ties broken by transaction_time. FLAGGED for v1.1 fix per
Research VERIFY response 2026-06-08.
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TemporalIndex:
    """Sorted (valid_time, value, sequence) index for one entity-relation pair."""
    entity_relation: str
    valid_times: list[int] = field(default_factory=list)   # sorted ascending
    values: list[Any] = field(default_factory=list)        # values aligned to valid_times
    sequence: list[int] = field(default_factory=list)      # original insertion order (tie-break)

    def add(self, valid_time: int, value: Any) -> None:
        """Insert a new version. Maintains sorted order via bisect."""
        idx = bisect.bisect_right(self.valid_times, valid_time)
        self.valid_times.insert(idx, valid_time)
        self.values.insert(idx, value)
        self.sequence.insert(idx, len(self.sequence))

    def as_of(self, t: int):
        """Return the latest value with valid_time <= t, or None if t precedes the earliest."""
        if not self.valid_times:
            return None
        idx = bisect.bisect_right(self.valid_times, t) - 1
        if idx < 0:
            return None
        return self.values[idx]

    def latest(self):
        if not self.values:
            return None
        return self.values[-1]

    def history(self) -> list[tuple[int, Any]]:
        return list(zip(self.valid_times, self.values))


def _self_test():
    idx = TemporalIndex(entity_relation="OpenAI:ceo")
    idx.add(valid_time=20210101, value="Sam_Altman")
    idx.add(valid_time=20231117, value="Mira_Murati_interim")
    idx.add(valid_time=20231122, value="Sam_Altman")

    assert idx.as_of(20210101) == "Sam_Altman"
    assert idx.as_of(20231117) == "Mira_Murati_interim"
    assert idx.as_of(20231121) == "Mira_Murati_interim"
    assert idx.as_of(20231122) == "Sam_Altman"
    assert idx.as_of(20240101) == "Sam_Altman"
    assert idx.as_of(20200101) is None, "before earliest"
    assert idx.latest() == "Sam_Altman"

    # Out-of-order insert maintained sorted
    idx.add(valid_time=20211201, value="Sam_Altman")
    assert idx.valid_times == sorted(idx.valid_times)

    print("[substrate.bitemporal] self-test PASS")


if __name__ == "__main__":
    _self_test()
