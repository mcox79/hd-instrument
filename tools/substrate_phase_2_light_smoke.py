"""Smoke test for Phase-2-light pipeline (50-file Snowball bootstrap).

Per Research design pre-reg:
- HARD-PASS: P@30 >= 0.60 (>= 18 of top-30 proposals are bona-fide substrate atom additions)
- MIDDLE: P@30 0.40-0.60
- HARD-FAIL: P@30 < 0.40

The smoke uses the 50 most-recent research_drill_*.md files.

Note: this smoke produces the proposal batch + outputs to JSON for Research to
judge ACCEPT/REJECT per proposal. The P@30 metric requires Research review;
this smoke produces the candidate batch for that review.

Usage: python tools/substrate_phase_2_light_smoke.py
Output: data/substrate_index/phase_2_light_smoke_<timestamp>.json
"""
from pathlib import Path
import sys
import json
import time
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.phase_2_light import run_phase_2_light_pipeline


def main():
    DATA_ROOT = Path("data/substrate_index")
    NOTES_DIR = Path("notes")

    print("=== Phase-2-light smoke (50-file Snowball bootstrap) ===\n")

    # Pick 50 most-recent research_drill_*.md files
    drill_files = sorted(
        NOTES_DIR.glob("research_drill_*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )[:50]
    print(f"input: {len(drill_files)} research_drill files (most recent first)")
    if drill_files:
        print(f"  newest: {drill_files[0].name}")
        print(f"  oldest: {drill_files[-1].name}")

    print("\nbuilding substrate index...")
    pstore = PartitionedStore(DATA_ROOT)
    ai = AlgebraIndex(dim=1024)
    ai.build(pstore)
    print(f"  {len(pstore.all_atoms())} atoms; algebra index built")

    print("\nrunning pipeline...")
    t0 = time.time()
    proposals = run_phase_2_light_pipeline(drill_files, pstore, ai, top_k=30)
    elapsed = time.time() - t0
    print(f"  pipeline elapsed: {elapsed:.2f}s")
    print(f"  ranked top-{len(proposals)} proposals\n")

    # Display top-30
    print("=== TOP-30 PROPOSAL BATCH ===\n")
    print(f"{'#':>3s} {'route':<12s} {'cluster':>7s} {'density':>7s} {'novelty':>7s} {'z':>4s} {'score':>6s}  canonical_name")
    for i, p in enumerate(proposals, 1):
        print(f"  {i:>2d} {p.route:<12s} {p.nearest_cluster!s:>7s} {p.nearest_density:>7d} {p.novelty:>7.2f} {p.candidate.z_count:>4d} {p.rank_score:>6.3f}  {p.candidate.canonical_name}")

    # Save proposal batch JSON
    out = {
        "smoke_run_ts": int(time.time()),
        "n_input_files": len(drill_files),
        "n_atoms_baseline": len(pstore.all_atoms()),
        "elapsed_s": elapsed,
        "proposals": [
            {
                "rank": i + 1,
                "canonical_name": p.candidate.canonical_name,
                "z_count": p.candidate.z_count,
                "source_files": p.candidate.source_files[:5],
                "raw_mentions": p.candidate.raw_mentions[:5],
                "distant_supervision_score": p.distant_supervision_score,
                "similarity_to_existing_T3": p.similarity_to_existing_T3,
                "nearest_cluster": p.nearest_cluster,
                "nearest_density": p.nearest_density,
                "novelty": p.novelty,
                "route": p.route,
                "rank_score": p.rank_score,
                "algebra_additions_template": p.algebra_additions_template,
            }
            for i, p in enumerate(proposals)
        ],
    }
    out_file = DATA_ROOT / f"phase_2_light_smoke_{int(time.time())}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved proposal batch to: {out_file}")

    # Pre-reg verdict requires Research review (ACCEPT / REJECT per proposal)
    print("\n=== PRE-REG VERDICT ===")
    print(f"  P@30 measurement requires Research review of the {len(proposals)} proposals")
    print(f"  Pre-reg: HARD-PASS >= 0.60 / MIDDLE 0.40-0.60 / HARD-FAIL < 0.40")
    print(f"  Routes by category: CREATE={sum(1 for p in proposals if p.route == 'CREATE')}  "
          f"UPDATE={sum(1 for p in proposals if p.route == 'UPDATE')}  "
          f"SKIP={sum(1 for p in proposals if p.route == 'SKIP')}  "
          f"SHARES_MATH_MULTI={sum(1 for p in proposals if p.route == 'SHARES_MATH_MULTI')}  "
          f"PROPOSE={sum(1 for p in proposals if p.route == 'PROPOSE')}")


if __name__ == "__main__":
    main()
