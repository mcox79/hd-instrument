"""5-query smoke test for the substrate self-index after first corpus drop.

Runs against the on-disk PartitionedStore at data/substrate_index and reports
each query's top-5 retrievals + latency.
"""
from __future__ import annotations
import time
from pathlib import Path

from backend.substrate_index.cli import _build_retriever
from backend.substrate_index.schema import Tier


def main():
    t0 = time.perf_counter()
    pstore, retr = _build_retriever(Path("data/substrate_index"))
    print(f"--- index load: {(time.perf_counter() - t0) * 1000:.0f} ms ---")

    queries = [
        ("what is the dual of FHRR binding", None),
        ("global discrete optimization algorithms", None),
        ("sequence decoding via dynamic programming", None),
        ("probabilistic inference for structured predictions", None),
        ("Tier-2 substrate primitives only", Tier.TIER_2_PRIMITIVE),
    ]

    for q, tf in queries:
        t1 = time.perf_counter()
        cands = retr.semantic(q, top_k=5, tier_filter=tf)
        elapsed = (time.perf_counter() - t1) * 1000
        print(f"\nQ: {q}  ({elapsed:.0f} ms)")
        for c in cands:
            a = pstore.get_atom(c.atom_id)
            print(f"  {c.score:.3f}  {c.atom_id}  ({a.name if a else '?'})")


if __name__ == "__main__":
    main()
