"""Phase-2-light Option C targeted MATH-FOUNDATION run.

Per Research direction (research_to_testbed_SUBSTRATE_SELF_MATHEMATICAL_UNDERSTANDING_BACKGROUND_ATOMS_BACKFILL_PRIORITY_PHASE_2_LIGHT_OPTION_C_TARGETED_MATH_FOUNDATION_2026-06-12.md):
- SCOPE: research_drill_*_2026-06-12.md files (today's drill notes; ~22 files)
- EXPECTED: ~80-100 math primitive candidates across 10 mathematical-foundation dimensions
- PRE-REG: P@30 >= 0.70 (high-SNR scope; math-primitive references are explicit)
- OUTPUT: ranked proposal batch JSON for Research formal P@30 review + ACCEPT/REJECT

Usage: python tools/substrate_phase_2_light_targeted_math_foundation.py [--top-k 100] [--pos-filter]
Output: data/substrate_index/phase_2_light_math_foundation_<ts>.json
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
    ap.add_argument("--top-k", type=int, default=100, help="top-K proposals to surface")
    ap.add_argument("--pos-filter", action="store_true",
                    help="enable substrate POS filter (Option B/C; slow first run)")
    ap.add_argument("--scope", choices=["default", "math-foundation"], default="default",
                    help="scope mode: 'math-foundation' drops Z>=3 to Z>=1 + relaxes PoS per Research direction")
    ap.add_argument("--min-z", type=int, default=None,
                    help="override min Z count threshold (default 3; math-foundation scope auto-sets to 1)")
    args = ap.parse_args()

    if args.scope == "math-foundation":
        min_z = 1 if args.min_z is None else args.min_z
        use_pos = False  # relax PoS per Research math-foundation direction
        print(f"=== Phase-2-light MATH-FOUNDATION SCOPE MODE (top-K={args.top_k}; min_z={min_z}; pos_filter=OFF) ===\n")
    else:
        min_z = 3 if args.min_z is None else args.min_z
        use_pos = args.pos_filter
        print(f"=== Phase-2-light TARGETED MATH-FOUNDATION default scope (top-K={args.top_k}; min_z={min_z}; pos_filter={use_pos}) ===\n")

    DATA_ROOT = Path("data/substrate_index")
    NOTES_DIR = Path("notes")

    # Scope: research_drill_*_2026-06-12.md (today's drill notes)
    drill_files = sorted(
        NOTES_DIR.glob("research_drill_*_2026-06-12.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    print(f"input: {len(drill_files)} drill files (research_drill_*_2026-06-12.md)")
    if drill_files:
        print(f"  newest: {drill_files[0].name}")
        print(f"  oldest: {drill_files[-1].name}")

    if len(drill_files) == 0:
        print("ERROR: no research_drill_*_2026-06-12.md files found in notes/")
        sys.exit(1)

    print("\nbuilding substrate index...")
    pstore = PartitionedStore(DATA_ROOT)
    ai = AlgebraIndex(dim=1024)
    ai.build(pstore)
    print(f"  {len(pstore.all_atoms())} atoms; algebra index built")

    print("\nrunning pipeline...")
    t0 = time.time()
    proposals = run_phase_2_light_pipeline(drill_files, pstore, ai,
                                            top_k=args.top_k,
                                            use_pos_filter=use_pos,
                                            min_z_count=min_z)
    elapsed = time.time() - t0
    print(f"  pipeline elapsed: {elapsed:.2f}s")
    print(f"  ranked top-{len(proposals)} proposals\n")

    # Display top-30
    print("=== TOP-30 PROPOSAL BATCH ===\n")
    print(f"{'#':>3s} {'route':<12s} {'cluster':>7s} {'density':>7s} {'novelty':>7s} {'z':>4s} {'score':>6s}  canonical_name")
    for i, p in enumerate(proposals[:30], 1):
        print(f"  {i:>2d} {p.route:<12s} {p.nearest_cluster!s:>7s} {p.nearest_density:>7d} {p.novelty:>7.2f} {p.candidate.z_count:>4d} {p.rank_score:>6.3f}  {p.candidate.canonical_name}")

    # Save proposal batch JSON
    out = {
        "smoke_run_ts": int(time.time()),
        "scope": f"research_drill_*_2026-06-12.md (Cycle 51 math-foundation; scope_mode={args.scope}; min_z={min_z}; pos_filter={use_pos})",
        "n_input_files": len(drill_files),
        "n_atoms_baseline": len(pstore.all_atoms()),
        "elapsed_s": elapsed,
        "scope_mode": args.scope,
        "min_z_count": min_z,
        "use_pos_filter": use_pos,
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
    out_file = DATA_ROOT / f"phase_2_light_math_foundation_{int(time.time())}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved proposal batch to: {out_file}")

    # Pre-reg verdict
    print("\n=== PRE-REG VERDICT ===")
    print(f"  P@30 measurement requires Research formal review")
    print(f"  Pre-reg: P@30 >= 0.70 HARD-PASS / 0.50-0.70 MIDDLE / <0.50 HARD-FAIL")
    print(f"  Routes by category: CREATE={sum(1 for p in proposals if p.route == 'CREATE')}  "
          f"UPDATE={sum(1 for p in proposals if p.route == 'UPDATE')}  "
          f"SKIP={sum(1 for p in proposals if p.route == 'SKIP')}  "
          f"SHARES_MATH_MULTI={sum(1 for p in proposals if p.route == 'SHARES_MATH_MULTI')}  "
          f"PROPOSE={sum(1 for p in proposals if p.route == 'PROPOSE')}")


if __name__ == "__main__":
    main()
