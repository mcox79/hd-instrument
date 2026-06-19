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
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", choices=["smoke", "full"], default="smoke",
                    help="smoke = 50 research_drill; full = all research_drill + history partitions")
    ap.add_argument("--top-k", type=int, default=30, help="top-K proposals to surface")
    ap.add_argument("--pos-filter", action="store_true",
                    help="Option B: enable substrate POS filter (slow first run; ~30-60s cache build)")
    args = ap.parse_args()

    DATA_ROOT = Path("data/substrate_index")
    NOTES_DIR = Path("notes")

    print(f"=== Phase-2-light {args.scale} (top-K={args.top_k}) ===\n")

    if args.scale == "smoke":
        # 50 most-recent research_drill_*.md files (Snowball bootstrap)
        drill_files = sorted(
            NOTES_DIR.glob("research_drill_*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:50]
    else:
        # FULL corpus per Research direction: research_drill + history partitions
        drill_files = list(NOTES_DIR.glob("research_drill_*.md"))
        # History partitions per Phase-1 evolve.py auto-classification:
        # research_history / decision_history / results_history / findings_history /
        # verdict_history / memory_history -- inferred via filename prefix conventions:
        history_globs = [
            "research_*.md",       # research_history
            "research_to_*.md",
            "*to_research_*.md",
            "*to_exp_dev_*.md",    # results_history
            "exp_dev_to_*.md",
            "testbed_to_*.md",     # findings_history
            "*to_testbed_*.md",
            "strategy_decisions_*.md",  # decision_history / verdict_history
            "strategy_request_*.md",
            "visibility_decisions_*.md",
        ]
        seen = set(f.resolve() for f in drill_files)
        for glob in history_globs:
            for f in NOTES_DIR.glob(glob):
                rp = f.resolve()
                if rp not in seen:
                    drill_files.append(f)
                    seen.add(rp)
        drill_files = sorted(drill_files, key=lambda f: f.stat().st_mtime, reverse=True)

    print(f"input: {len(drill_files)} files ({args.scale} scale)")
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
    proposals = run_phase_2_light_pipeline(drill_files, pstore, ai,
                                            top_k=args.top_k,
                                            use_pos_filter=args.pos_filter)
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
