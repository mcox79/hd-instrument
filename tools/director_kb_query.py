"""CLI for Director-KB query (ANCHOR 2; v1).

Usage:
  python tools/director_kb_query.py "what is the current substrate-product positioning?"
  python tools/director_kb_query.py --k 10 --tau 0.3 "what cells addressed cortex selectivity?"
  python tools/director_kb_query.py --json "..."
  python tools/director_kb_query.py --source-class=notes,memory "post-compaction digest"
  python tools/director_kb_query.py --filename-contains POST_COMPACTION_BACKUP --source-class=notes

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb_query import DirectorKBQuery, load_default_kb  # noqa: E402


def _print_human(result: dict) -> None:
    print(f"Q: {result['question']}")
    print(f"  kb_version={result['kb_version']} schema={result['schema_version']} "
          f"encoder={result['encoder']} confidence={result['confidence']} "
          f"refused={result['refused']} elapsed={result['elapsed_s']}s")
    scf = result.get("source_classes_filter")
    if scf:
        print(f"  source_class_filter={','.join(scf)}")
    fnf = result.get("filename_contains_filter")
    if fnf:
        print(f"  filename_contains_filter='{fnf}' (cosine bypass; recency-sorted)")
    if result.get("refused"):
        print(f"  REFUSAL: {result.get('refusal_reason')}")
        print(f"  fallback: {result.get('fallback_recommendation')}")
    print(f"  top-{result['k']} atoms (filtered superseded={'no' if result.get('debug_include_superseded') else 'yes'}):")
    for i, a in enumerate(result["top_k_atoms"]):
        marker = " [SUPERSEDED]" if a.get("superseded") else ""
        print(f"    {i+1}. entity='{a['entity']}'{marker}")
        print(f"       cosine={a['cosine']}")
        if a.get("source_classes"):
            print(f"       source_classes: {','.join(a['source_classes'])}")
        if a["source_paths"]:
            print(f"       sources: {', '.join(a['source_paths'][:3])}"
                  + ("..." if len(a["source_paths"]) > 3 else ""))
        if a["relations"]:
            rel_strs = [f"{r}->{o}" for r, o in a["relations"][:4]]
            print(f"       edges: {' | '.join(rel_strs)}"
                  + ("..." if len(a["relations"]) > 4 else ""))
    print(f"  paths_consulted={len(result['paths_consulted'])} files")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("question", nargs="?", default=None, help="Natural-language question")
    ap.add_argument("--kb-dir", default=None, help="KB dir (default: ANCHOR 1.5 full-arm path)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--tau", type=float, default=0.2,
                    help="Confidence floor (refuse below). Default 0.2 calibrated for "
                         "char_trigram_v1 encoder cosine distribution at v1 corpus size "
                         "(strong matches typically 0.22-0.35; 0.5 would over-refuse).")
    ap.add_argument("--schema-version", default="v1")
    ap.add_argument("--encoder", default="default")
    ap.add_argument("--debug-include-superseded", action="store_true")
    ap.add_argument("--source-class", default=None,
                    help="Filter atoms by source_class. Comma-separated for multiple "
                         "(e.g. --source-class=notes,memory). Schema values: note, memory, "
                         "metrics, prereg, cert_ledger, atoms, director_plan, fleet_state, "
                         "wordnet, verbnet, framenet, gene_ontology, kegg_pathway, neurolex. "
                         "Common plurals (notes, preregs, kegg) auto-aliased to singulars.")
    ap.add_argument("--filename-contains", default=None,
                    help="Case-insensitive substring matched against entity strings; "
                         "BYPASSES cosine ranking and returns all hits sorted by most-recent "
                         "embedded date (YYYY-MM-DD) descending, ties alphabetical. Use when "
                         "atom entities are filenames (notes/, memory/) and cosine is too noisy "
                         "to surface a known doc. Composes with --source-class.")
    ap.add_argument("--json", action="store_true", help="Emit raw JSON instead of human-readable")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        # Smoke load: just instantiate; verifies KB on disk + load path
        kb = load_default_kb(REPO)
        assert kb.n_dim >= 256
        assert len(kb.entity_names) > 0
        assert len(kb.relation_names) > 0
        print(f"[selftest] director_kb_query load PASS n_ent={len(kb.entity_names)} "
              f"n_rel={len(kb.relation_names)}")
        return 0

    # filename_contains bypass: question becomes optional when filter is the entry point
    if not args.question and not args.filename_contains:
        print("ERROR: question is required (or use --self-test, or --filename-contains)",
              file=sys.stderr)
        return 2

    if args.kb_dir:
        kb = DirectorKBQuery(kb_dir=Path(args.kb_dir))
    else:
        kb = load_default_kb(REPO)

    src_class_filter = None
    if args.source_class:
        src_class_filter = [s.strip() for s in args.source_class.split(",") if s.strip()]

    # When using filename-contains-only mode, supply empty question (cosine path skipped)
    effective_question = args.question if args.question else ""

    result = kb.query(
        question=effective_question,
        schema_version=args.schema_version,
        encoder=args.encoder,
        k=args.k,
        confidence_floor=args.tau,
        debug_include_superseded=args.debug_include_superseded,
        source_classes=src_class_filter,
        filename_contains=args.filename_contains,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
