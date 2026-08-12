"""CLI for explicit Director-KB re-ingest (ANCHOR 1; v1).

The Director invokes this when a re-ingest is needed (schema change, drift
suspected, recovery from corruption, wipe-and-rebuild). Composes the same
ingest pipeline as the experiment cell, but without the arm/verdict
machinery.

Usage:
    python tools/director_kb_ingest.py
    python tools/director_kb_ingest.py --schema config/director_kb_schema.json \\
        --out data/substrate_director_kb_v1 --wipe
    python tools/director_kb_ingest.py --only-classes note,metrics --max-files 500
    python tools/director_kb_ingest.py --dry-run

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb import (  # noqa: E402
    SCHEMA_PATH_DEFAULT,
    build_ingest_plan,
    load_schema,
    run_ingest,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schema", default=SCHEMA_PATH_DEFAULT,
                    help=f"Schema JSON relative to repo root (default: {SCHEMA_PATH_DEFAULT})")
    ap.add_argument("--out", default=None,
                    help="Output KB dir (default: data/substrate_director_kb_<kb_version>/ from schema)")
    ap.add_argument("--n-dim", type=int, default=2048,
                    help="HD vector dimension (default 2048)")
    ap.add_argument("--seed", type=int, default=17,
                    help="PRNG seed for entity/relation codebooks (default 17)")
    ap.add_argument("--max-files", type=int, default=None,
                    help="Cap files-per-class (default: no cap; uses schema per-class cap)")
    ap.add_argument("--only-classes", default=None,
                    help="Comma-separated subset of source class names")
    ap.add_argument("--wipe", action="store_true",
                    help="Wipe out_dir before ingest (the safe wipe-and-rebuild move)")
    ap.add_argument("--no-wipe", action="store_true",
                    help="Refuse to wipe out_dir (overlay mode; for partial re-ingest)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print plan summary and exit without writing")
    args = ap.parse_args()

    if args.wipe and args.no_wipe:
        print("ERROR: --wipe and --no-wipe are mutually exclusive", file=sys.stderr)
        return 2

    schema = load_schema(REPO, args.schema)
    kb_ver = schema.get("kb_version", "v1")
    kb_path = schema.get("kb_path", f"data/substrate_director_kb_{kb_ver}")
    out_dir = Path(args.out) if args.out else (REPO / kb_path)

    only = None
    if args.only_classes:
        only = [c.strip() for c in args.only_classes.split(",") if c.strip()]

    plan = build_ingest_plan(
        schema=schema,
        repo_root=REPO,
        max_files_per_class=args.max_files,
        only_classes=only,
    )

    print(f"[director-kb-ingest] schema={args.schema} kb_version={kb_ver}")
    print(f"[director-kb-ingest] out_dir={out_dir}")
    for cname in sorted(plan.keys()):
        info = plan[cname]
        root = info["root"]
        n = len(info["files"])
        unreachable = info["skipped_unreachable"]
        print(f"  class={cname} root={root} n_files={n} unreachable={unreachable}")

    if args.dry_run:
        print("[director-kb-ingest] dry-run; not ingesting")
        return 0

    wipe = args.wipe or (not args.no_wipe)
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=args.n_dim,
        seed=args.seed,
        wipe=wipe,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    print(f"[director-kb-ingest] DONE elapsed={elapsed:.2f}s")
    print(f"  n_entities={manifest['n_entities']} n_relations={manifest['n_relations']} "
          f"n_triples={manifest['n_triples']} n_skipped={manifest['n_skipped']} "
          f"coverage={manifest['coverage_ratio']}")
    print(f"  manifest written to {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
