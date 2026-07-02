"""Build the substrate-Director-KB v2 (content-chunk) at canonical path.

DEPRECATED 2026-07-02 (UNIFIED-KB): chunk emission is now folded into the
primary KB ingest (hdlab/director_kb.py::run_ingest); the continuous-ingest
daemon builds ONE unified KB at data/substrate_director_kb_v1/. This tool
still functions and rebuilds a parallel chunk-only KB at
data/substrate_director_kb_chunk_v1/, but that KB is redundant and stale
by design. New code should query the unified KB via tools/substrate_query.sh
or tools/director_kb_query.py without --chunk-content. Kept for one-off
reproducibility of prior chunk-KB experiments.

USER 2026-06-27: build substrate v2 chunk KB locally for substrate-vs-MD A/B
test. Persists to data/substrate_director_kb_chunk_v1/ which is the canonical
path that tools/director_kb_query.py --chunk-content reads from.

Composes only on chain-grade primitive hdlab.director_kb_chunk_ingest
(ANCHOR 1 v2; 2026-06-26) per Principle 11. Text-mode source classes only
(note, memory, prereg, director_plan, fleet_state); JSONL classes (atoms,
cert_ledger) are not chunkable per the primitive's design and are excluded
here (they remain in the v1 filename-index KB which is also queryable).

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

from hdlab.director_kb_chunk_ingest import (  # noqa: E402
    DEFAULT_CHUNK_CLASSES,
    build_chunk_plan,
    run_chunk_ingest,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-dir",
        default=str(REPO / "data" / "substrate_director_kb_chunk_v1"),
        help="Output dir for chunk KB (default: canonical path).",
    )
    ap.add_argument(
        "--schema",
        default=str(REPO / "config" / "director_kb_schema.json"),
        help="Director-KB schema (default: config/director_kb_schema.json).",
    )
    ap.add_argument("--n-dim", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument(
        "--max-files-per-class",
        type=int,
        default=None,
        help="Cap files per class (smoke). Default: schema-defined or unlimited.",
    )
    args = ap.parse_args()

    schema_path = Path(args.schema)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    print(f"[build] schema={schema_path.name} version={schema.get('schema_version')}",
          flush=True)
    print(f"[build] chunk_classes={DEFAULT_CHUNK_CLASSES}", flush=True)
    print(f"[build] out_dir={args.out_dir}", flush=True)
    print(f"[build] n_dim={args.n_dim} seed={args.seed}", flush=True)

    t0 = time.perf_counter()
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=args.max_files_per_class,
    )
    plan_elapsed = time.perf_counter() - t0
    print(f"[build] plan built in {plan_elapsed:.2f}s", flush=True)
    for cname, p in plan.items():
        n_files = len(p["files"])
        root = str(p["root"]) if p["root"] else "<unreachable>"
        marker = " SKIPPED" if p["skipped_unreachable"] else ""
        print(f"  {cname}: n_files={n_files} root={root}{marker}", flush=True)

    out_dir = Path(args.out_dir)
    manifest = run_chunk_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=args.n_dim,
        seed=args.seed,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )

    total_elapsed = time.perf_counter() - t0
    print(f"\n[build] DONE manifest:", flush=True)
    print(f"  n_entities={manifest['n_entities']}", flush=True)
    print(f"  n_relations={manifest['n_relations']}", flush=True)
    print(f"  n_triples={manifest['n_triples']}", flush=True)
    print(f"  n_chunks={manifest['n_chunks']}", flush=True)
    print(f"  n_discovered={manifest['n_discovered']}", flush=True)
    print(f"  n_skipped={manifest['n_skipped']}", flush=True)
    print(f"  coverage_ratio={manifest['coverage_ratio']}", flush=True)
    print(f"  avg_chunks_per_file={manifest['avg_chunks_per_file']}", flush=True)
    print(f"  elapsed_s={manifest['elapsed_s']}", flush=True)
    print(f"  total_wall_s={total_elapsed:.2f}", flush=True)
    print(f"  manifest_path={out_dir / 'manifest.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
