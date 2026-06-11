"""Run the discovery engine against the current substrate_index state and dump findings."""
from __future__ import annotations
import json
from pathlib import Path

from backend.substrate_index.cli import _build_retriever
from backend.substrate_index.discover import discover_all


def main():
    pstore, retr = _build_retriever(Path("data/substrate_index"))
    report = discover_all(pstore, retriever=retr, centrality_baseline=None)
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
