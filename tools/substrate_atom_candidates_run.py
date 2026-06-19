"""Run Tier 3 atom-candidate generation against the current 74-atom corpus.

Per Research 5-tier progression Tier 3 = "substrate-native atom-candidate
generation pipeline." Substrate looks at its own corpus and proposes atoms
that should exist but don't.

Output: per-source candidate list + JSON report + markdown summary.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.atom_candidates import generate_candidates
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.partition import PartitionedStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("atom_candidates_run")

DATA_ROOT = Path("data/substrate_index")


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("corpus: %d atoms", len(pstore.all_atoms()))

    log.info("building algebra_index for centroid analysis...")
    aidx = AlgebraIndex(dim=1024)
    aidx.build(pstore)

    # Source #5 inputs: all research notes
    NOTES_DIR = Path("notes")
    source_files = []
    for prefix in ("research_drill_", "research_to_", "exp_dev_to_research_", "testbed_to_research_"):
        source_files.extend(sorted(NOTES_DIR.glob(f"{prefix}*.md")))
    log.info("source #5 inputs: %d notes", len(source_files))

    log.info("generating atom candidates (all 4 sources)...")
    report = generate_candidates(pstore, aidx=aidx, source_files=source_files)
    log.info("total: %d candidates; by source: %s", report.n_candidates, dict(report.by_justification))

    print(f"\n{'='*80}")
    print(f"Substrate-proposed atom candidates (Tier 3) on {len(pstore.all_atoms())} atoms")
    print(f"{'='*80}\n")
    print(f"Total candidates: {report.n_candidates}")
    print(f"By justification source:")
    for j, n in report.by_justification.items():
        print(f"  {j:40s}  {n}")

    # Per-source detail
    sources = {}
    for c in report.candidates:
        sources.setdefault(c.justification_type, []).append(c)

    for j_type, cands in sources.items():
        print(f"\n--- {j_type} ({len(cands)} candidates; top 15 by confidence) ---")
        for c in cands[:15]:
            print(f"  conf={c.confidence:.2f}  {c.proposed_id}")
            print(f"    referenced_by ({len(c.referenced_by)}): {[r.split('::')[-1] for r in c.referenced_by[:5]]}{'...' if len(c.referenced_by) > 5 else ''}")
            print(f"    note: {c.notes}")

    out = DATA_ROOT / "bench_reports" / f"atom_candidates_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
