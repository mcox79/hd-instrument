"""substrate_query.py -- CLI front-door for substrate self-knowledge queries.

Per FINDINGS #18 Gap 3 + Research Q3 CLI-FIRST endorsement 2026-06-11:
substrate must be USABLE knowledge base, not read-only literature. This CLI
exposes the 8 self_knowledge.py query functions as subcommands.

USER-asked question: "after this massive ingestion - how will the substrate
know what it has and how to use it?"

Usage:
    python tools/substrate_query.py corpus-summary
    python tools/substrate_query.py universal-levers [--min-caps N]
    python tools/substrate_query.py recent-lifts [--min-metric F] [--top K]
    python tools/substrate_query.py what-serves <cap_qid>
    python tools/substrate_query.py what-have-you-not-tried <cap_qid> [--corpus C]
    python tools/substrate_query.py coverage-report
    python tools/substrate_query.py composition-paths <src_qid> <tgt_qid> [--max-depth N]
    python tools/substrate_query.py what-do-you-know-about <topic_string> [--top K]
    python tools/substrate_query.py ask <free-form NL question>   # routes via heuristic

The free-form `ask` subcommand routes via simple keyword heuristics until
Gap 4 intent router lands.

NO encoder load EXCEPT for what-do-you-know-about and ask (semantic retrieval).
All other subcommands are pure index walks (local-allowed per
[[feedback-all-cpu-compute-on-remote-desktop-2026-06-11]]).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.self_knowledge import (
    corpus_summary,
    universal_levers,
    recent_lifts,
    what_serves,
    what_have_you_not_tried,
    coverage_report,
    composition_paths,
    what_do_you_know_about,
    which_solutions_use_atom,
    atom_contribution_log,
)

DATA_ROOT = Path("data/substrate_index")


def _print_dict(d, indent=0):
    pad = "  " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                print(f"{pad}{k}:")
                _print_dict(v, indent + 1)
            else:
                print(f"{pad}{k}: {v}")
    elif isinstance(d, list):
        for item in d:
            if isinstance(item, (dict, list)):
                _print_dict(item, indent)
                print()
            else:
                print(f"{pad}- {item}")


def _format_atom(a, max_desc=80):
    desc = (a.description or "").strip().split("\n")[0]
    if len(desc) > max_desc:
        desc = desc[:max_desc] + "..."
    return f"  {a.qualified_id:60s} tier={a.tier.value:5s} {desc}"


def cmd_corpus_summary(pstore, args):
    s = corpus_summary(pstore)
    print(f"\n=== SUBSTRATE CORPUS SUMMARY ===")
    print(f"  total atoms: {s['total_atoms']}")
    print(f"  total relations: {s['total_relations']}")
    print(f"\n  by tier: {s['by_tier']}")
    print(f"\n  by kind: {s['by_kind']}")
    print(f"\n  partitions:")
    for cn, p in s["partitions"].items():
        if p["n_atoms"] > 0:
            print(f"    {cn:20s}  {p['n_atoms']:5d} atoms / {p['n_relations']:5d} relations")
    print(f"\n  top universal levers:")
    for lever in s["top_universal_levers"]:
        print(f"    {lever['atom']:55s} serves {lever['serves_n']} caps  ({lever['name'][:40]})")


def cmd_universal_levers(pstore, args):
    levers = universal_levers(pstore, min_caps=args.min_caps)
    print(f"\n=== UNIVERSAL LEVERS (serves >= {args.min_caps} capabilities) ===")
    if not levers:
        print(f"  (none with >= {args.min_caps} caps)")
        return
    for atom, n in levers:
        print(f"  {atom.qualified_id:60s} serves {n} caps  ({atom.name[:40]})")


def cmd_recent_lifts(pstore, args):
    lifts = recent_lifts(pstore, min_metric=args.min_metric)
    print(f"\n=== RECENT LIFTS (empirical_metric >= {args.min_metric}) -- top {args.top} ===")
    if not lifts:
        print(f"  (none above threshold)")
        return
    for r in lifts[:args.top]:
        sol = (r["solution"] or "")[:40]
        date = r.get("date") or ""
        print(f"  {r['capability_name'][:30]:32s} via {sol:42s} +{r['metric']:.3f}  ({date})")


def cmd_what_serves(pstore, args):
    atoms = what_serves(pstore, args.cap_qid)
    print(f"\n=== ATOMS SERVING {args.cap_qid} ===")
    if not atoms:
        print(f"  (none indexed; either cap doesn't exist or serves_capability not yet backfilled)")
        return
    for a in atoms:
        print(_format_atom(a))


def cmd_what_have_you_not_tried(pstore, args):
    atoms = what_have_you_not_tried(pstore, args.cap_qid, corpus=args.corpus)
    print(f"\n=== {args.corpus.upper()} ATOMS NOT YET LINKED TO {args.cap_qid} ===")
    print(f"  (showing top 20 by tier; total {len(atoms)})")
    for a in atoms[:20]:
        print(_format_atom(a))


def cmd_coverage_report(pstore, args):
    cr = coverage_report(pstore)
    print(f"\n=== CAPABILITY COVERAGE REPORT ===")
    print(f"  total capabilities (with solution_history or current_best): {cr['total_caps']}")
    print(f"  caps with serves_capability backfilled: {cr['caps_with_coverage']} ({100*cr['caps_with_coverage']/max(1,cr['total_caps']):.1f}%)")
    print(f"  caps empty: {cr['caps_empty']}")
    if cr["empty_cap_qids"]:
        print(f"  empty cap qids:")
        for q in cr["empty_cap_qids"]:
            print(f"    - {q}")
    if args.verbose:
        print(f"\n  per-capability:")
        for cap, info in cr["coverage_per_cap"].items():
            print(f"    {cap:55s} {info['n_servers']:3d} servers")


def cmd_composition_paths(pstore, args):
    paths = composition_paths(pstore, args.src, args.tgt, max_depth=args.max_depth)
    print(f"\n=== COMPOSITION PATHS {args.src} -> {args.tgt} (max depth {args.max_depth}) ===")
    if not paths:
        print(f"  (no path found via USES/COMPOSES/DEPENDS_ON/USES_SUBPROC)")
        return
    for i, p in enumerate(paths):
        print(f"  path {i+1} (len {len(p)}):")
        for step in p:
            print(f"    -> {step}")


def cmd_what_do_you_know_about(pstore, args):
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    print("(loading bge encoder + retriever -- requires remote CPU; skipping if standing rule active)")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    retriever.rebuild_index()
    results = what_do_you_know_about(retriever, args.topic, top_k=args.top)
    print(f"\n=== WHAT SUBSTRATE KNOWS ABOUT \"{args.topic}\" ===")
    for r in results:
        print(f"  {r['atom']:55s} [{r['corpus']}/{r['tier']}] score={r['score']:.3f}")
        print(f"    {r['name']}")


def cmd_which_solutions_use(pstore, args):
    entries = which_solutions_use_atom(pstore, args.atom_qid)
    print(f"\n=== SOLUTIONS USING {args.atom_qid} ===")
    if not entries:
        print(f"  (atom is not listed in any solution_history.atoms_used)")
        return
    for e in entries:
        m = f"+{e['metric']:.3f}" if e["metric"] is not None else "n/a"
        print(f"  {e['capability_name'][:30]:32s} via {(e['solution'] or '')[:35]:37s} {m:8s} ({e.get('date') or 'no date'})")


def cmd_atom_contributions(pstore, args):
    stats = atom_contribution_log(pstore, args.atom_qid)
    print(f"\n=== ATOM CONTRIBUTION LOG: {args.atom_qid} ===")
    print(f"  appearances in solution_history.atoms_used: {stats['n_appearances']}")
    print(f"  total lift sum: +{stats['total_lift_sum']:.3f}")
    print(f"  mean lift: +{stats['mean_lift']:.3f}")
    print(f"  max lift: +{stats['max_lift']:.3f}")
    print(f"  current solutions: {stats['current_count']}")
    print(f"  superseded solutions: {stats['superseded_count']}")
    print(f"  capabilities touched: {len(stats['capabilities'])}")
    for c in stats["capabilities"][:10]:
        print(f"    - {c}")


def cmd_ask(pstore, args):
    """Free-form NL routing via simple keyword heuristics (Gap 4 stub)."""
    q = args.question.lower()
    if any(kw in q for kw in ["what do i have", "what's in the corpus", "summary", "how big"]):
        return cmd_corpus_summary(pstore, args)
    if any(kw in q for kw in ["universal lever", "best", "most used", "reusable", "92%", "across capabilities"]):
        args.min_caps = 3
        return cmd_universal_levers(pstore, args)
    if any(kw in q for kw in ["recent lift", "what worked", "what's working", "biggest gain", "cliff"]):
        args.min_metric = 0.10
        args.top = 10
        return cmd_recent_lifts(pstore, args)
    if any(kw in q for kw in ["coverage", "how well do i know", "how complete"]):
        args.verbose = False
        return cmd_coverage_report(pstore, args)
    if "not tried" in q or "haven't tried" in q or "what else" in q:
        print(f"  (need capability id; try: substrate_query.py what-have-you-not-tried <cap_qid>)")
        return
    # Default: semantic search
    print(f"  routing to semantic retrieval (loads encoder)...")
    args.topic = args.question
    args.top = 8
    return cmd_what_do_you_know_about(pstore, args)


SUBCOMMANDS = {
    "corpus-summary": cmd_corpus_summary,
    "universal-levers": cmd_universal_levers,
    "recent-lifts": cmd_recent_lifts,
    "what-serves": cmd_what_serves,
    "what-have-you-not-tried": cmd_what_have_you_not_tried,
    "coverage-report": cmd_coverage_report,
    "composition-paths": cmd_composition_paths,
    "what-do-you-know-about": cmd_what_do_you_know_about,
    "which-solutions-use": cmd_which_solutions_use,
    "atom-contributions": cmd_atom_contributions,
    "ask": cmd_ask,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("corpus-summary", help="High-level: partition counts, tiers, kinds, top levers")

    p = sub.add_parser("universal-levers", help="Atoms serving >= N capabilities (Gap 1 powered)")
    p.add_argument("--min-caps", type=int, default=3)

    p = sub.add_parser("recent-lifts", help="Solution-history entries above empirical-metric threshold")
    p.add_argument("--min-metric", type=float, default=0.10)
    p.add_argument("--top", type=int, default=15)

    p = sub.add_parser("what-serves", help="List atoms serving a given capability")
    p.add_argument("cap_qid", help="Qualified id, e.g. concept::CAP_cleanup")

    p = sub.add_parser("what-have-you-not-tried", help="Atoms NOT yet linked to capability")
    p.add_argument("cap_qid")
    p.add_argument("--corpus", default="math", choices=["math", "concept", "science", "school"])

    p = sub.add_parser("coverage-report", help="Per-capability serves_capability coverage")
    p.add_argument("-v", "--verbose", action="store_true")

    p = sub.add_parser("composition-paths", help="BFS over USES/COMPOSES/DEPENDS_ON edges")
    p.add_argument("src", help="Source atom qualified id")
    p.add_argument("tgt", help="Target atom qualified id")
    p.add_argument("--max-depth", type=int, default=4)

    p = sub.add_parser("what-do-you-know-about", help="Semantic retrieval over all partitions (LOADS ENCODER)")
    p.add_argument("topic", help="Free-text topic")
    p.add_argument("--top", type=int, default=8)

    p = sub.add_parser("which-solutions-use", help="Solutions whose atoms_used includes this atom (Gap 5)")
    p.add_argument("atom_qid", help="Qualified id, e.g. math::T2/cleanup")

    p = sub.add_parser("atom-contributions", help="Aggregate lift contributions of an atom across capabilities (Gap 5)")
    p.add_argument("atom_qid", help="Qualified id, e.g. math::T2/cleanup")

    p = sub.add_parser("ask", help="Free-form NL question routed via heuristics (Gap 4 stub)")
    p.add_argument("question", help="Plain English question")

    args = ap.parse_args()
    pstore = PartitionedStore(DATA_ROOT)
    SUBCOMMANDS[args.cmd](pstore, args)


if __name__ == "__main__":
    main()
