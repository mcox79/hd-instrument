"""Operator + Research analysis CLI for substrate self-index.

Subcommands:
  ingest      Load atoms / relations / queries from JSONL
  stats       Print partition + relation stats
  query       Direct semantic query against the index
  related     Show structural neighbors of an atom
  paths       BFS shortest paths between two qualified ids
  gaps        List atoms with no incoming/outgoing of a given relation type
  centrality  Top-N atoms by degree centrality (or betweenness)
  algebraic   Substrate-algebraic query: atom_id + rel_type -> ranked answers
  bench       Run pre-registered benchmark + emit report

Examples:
  python -m backend.substrate_index.cli stats
  python -m backend.substrate_index.cli ingest --atoms math_atoms.jsonl --source math_corpus_v1
  python -m backend.substrate_index.cli query "operations similar to FHRR cleanup"
  python -m backend.substrate_index.cli related math::T2/fhrr_bind --rel DUAL
  python -m backend.substrate_index.cli paths math::T2/fhrr_bind concept::PP-364
  python -m backend.substrate_index.cli gaps --rel HAS_USERS --corpus math --direction out
  python -m backend.substrate_index.cli centrality --top 20
  python -m backend.substrate_index.cli bench --queries data/substrate_self_index/queries.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.ingest import ingest_corpus_bundle
from backend.substrate_index.metrics import diagnose, render_report, score_query
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.relate import (
    degree_centrality,
    gap_atoms,
    shortest_path,
)
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import (
    Corpus,
    RelationType,
    Tier,
    load_test_queries,
)


DEFAULT_ROOT = Path("data/substrate_index")


def _build_retriever(root: Path) -> tuple[PartitionedStore, Retriever]:
    """Construct partitioned store + retriever. NOTE: retriever build is
    expensive (loads bge-large + encodes all atoms); each CLI invocation pays
    this cost. Acceptable for interactive operator use.
    """
    pstore = PartitionedStore(root)
    encoder = AtomEncoder()
    # Build a per-partition retriever stack would be cleaner; for now combine
    # all atoms into one retrieval index for cross-partition semantic search
    from backend.substrate_index.store import Store
    combined = Store(root / "_combined_view")
    for atom in pstore.all_atoms():
        # Use qualified id as the combined-store local id to avoid collisions
        from backend.substrate_index.schema import Atom
        combined_atom = Atom(
            id=atom.qualified_id,
            name=atom.name,
            corpus=atom.corpus,
            tier=atom.tier,
            kind=atom.kind,
            description=atom.description,
            aliases=atom.aliases,
            metadata=atom.metadata,
        )
        combined._index_atom(combined_atom)  # bypass audit-log overhead for view
    retriever = Retriever(combined, encoder)
    retriever.rebuild_index()
    return pstore, retriever


def _cmd_stats(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    print(json.dumps(pstore.stats(), indent=2))


def _cmd_ingest(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    report = ingest_corpus_bundle(
        pstore,
        atoms_path=Path(args.atoms) if args.atoms else None,
        relations_path=Path(args.relations) if args.relations else None,
        source=args.source,
        note=args.note or "",
    )
    print(json.dumps(report.to_dict(), indent=2))


def _cmd_query(args) -> None:
    pstore, retriever = _build_retriever(Path(args.root))
    t0 = time.perf_counter()
    corpus_filter = Corpus(args.corpus) if args.corpus else None
    tier_filter = Tier(args.tier) if args.tier else None
    candidates = retriever.semantic(
        args.text, top_k=args.top, corpus_filter=corpus_filter, tier_filter=tier_filter
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(json.dumps({
        "query": args.text,
        "latency_ms": round(elapsed_ms, 1),
        "results": [
            {
                "atom_id": c.atom_id,
                "score": round(c.score, 4),
                "via": c.via,
                "name": (pstore.get_atom(c.atom_id) or _PlaceholderAtom()).name,
            }
            for c in candidates
        ],
    }, indent=2))


def _cmd_related(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    if not pstore.has_atom(args.atom_id):
        print(f"atom not found: {args.atom_id}", file=sys.stderr)
        sys.exit(1)
    rel = RelationType(args.rel) if args.rel else None
    direction = args.direction
    if direction == "out":
        neighbors = pstore.out_neighbors(args.atom_id, rel)
    elif direction == "in":
        neighbors = pstore.in_neighbors(args.atom_id, rel)
    else:
        print(f"direction must be 'in' or 'out', got {direction}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({
        "atom": args.atom_id,
        "direction": direction,
        "rel_type": args.rel or "ANY",
        "neighbors": sorted(neighbors),
    }, indent=2))


def _cmd_paths(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    # Build a within-partition view from the qualified ids for the path search
    # The PartitionedStore exposes out/in_neighbors using qualified ids so the
    # BFS in relate.py works against either a partition Store or our wrapper
    # if we adapt the call -- here we just walk the qualified ids ourselves.
    if not pstore.has_atom(args.src) or not pstore.has_atom(args.tgt):
        print("src or tgt not found", file=sys.stderr)
        sys.exit(1)
    rel_types = {RelationType(r) for r in args.rel} if args.rel else None
    path = _path_partitioned(pstore, args.src, args.tgt, rel_types, args.max_depth)
    print(json.dumps({"src": args.src, "tgt": args.tgt, "path": path}, indent=2))


def _path_partitioned(pstore, src: str, tgt: str, rel_types, max_depth: int):
    """BFS over qualified ids using the partitioned wrapper's neighbor calls."""
    from collections import deque
    if src == tgt:
        return [src]
    queue = deque([(src, [src])])
    visited = {src}
    rels = rel_types if rel_types else list(RelationType)
    while queue:
        node, path = queue.popleft()
        if len(path) > max_depth:
            continue
        for rt in rels:
            for nxt in pstore.out_neighbors(node, rt):
                if nxt in visited:
                    continue
                if nxt == tgt:
                    return path + [nxt]
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None


def _cmd_gaps(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    rel = RelationType(args.rel)
    corpus = Corpus(args.corpus) if args.corpus else None
    tier = Tier(args.tier) if args.tier else None
    # gap_atoms operates on a single Store; iterate per partition + filter
    results = []
    for c, store in pstore._stores.items():
        if corpus is not None and c != corpus:
            continue
        from backend.substrate_index.relate import gap_atoms as _gap
        for g in _gap(store, rel_type=rel, direction=args.direction, tier_filter=tier):
            results.append({
                "atom": f"{c.value}::{g.atom_id}",
                "kind": g.gap_kind,
                "rel": g.rel_type.value if g.rel_type else None,
            })
    print(json.dumps({"gaps": results, "count": len(results)}, indent=2))


def _cmd_centrality(args) -> None:
    pstore = PartitionedStore(Path(args.root))
    # Walk all partitions' relations into a single degree count over qualified ids
    out_deg = {}
    in_deg = {}
    for src, rt, tgt in pstore.iter_all_relations():
        out_deg[src] = out_deg.get(src, 0) + 1
        in_deg[tgt] = in_deg.get(tgt, 0) + 1
    all_ids = pstore.all_qualified_ids()
    reports = sorted(
        [
            {
                "atom": aid,
                "in": in_deg.get(aid, 0),
                "out": out_deg.get(aid, 0),
                "total": in_deg.get(aid, 0) + out_deg.get(aid, 0),
            }
            for aid in all_ids
        ],
        key=lambda r: -r["total"],
    )
    print(json.dumps({"top": reports[: args.top]}, indent=2))


def _cmd_algebraic(args) -> None:
    pstore, retriever = _build_retriever(Path(args.root))
    rt = RelationType(args.rel)
    cands = retriever.algebraic(args.atom_id, rt, top_k=args.top)
    print(json.dumps({
        "atom": args.atom_id,
        "rel": rt.value,
        "results": [
            {
                "atom_id": c.atom_id,
                "score": round(c.score, 4),
                "name": (pstore.get_atom(c.atom_id) or _PlaceholderAtom()).name,
            }
            for c in cands
        ],
    }, indent=2))


def _cmd_bench(args) -> None:
    pstore, retriever = _build_retriever(Path(args.root))
    queries_path = Path(args.queries)
    queries = load_test_queries(queries_path)
    if not queries:
        print(f"no queries loaded from {queries_path}", file=sys.stderr)
        sys.exit(1)
    known_ids = pstore.all_qualified_ids()
    scores = []
    for q in queries:
        t0 = time.perf_counter()
        cands = retriever.semantic(q.query_text, top_k=10)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = retriever.as_query_result(q.qid, cands, latency_ms=elapsed_ms)
        scores.append(score_query(q, result, known_ids))
    diag = diagnose(scores)
    report = render_report(diag, scores, title="Substrate Self-Index Benchmark")
    print(report)
    out_dir = Path(args.root) / "bench_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    json_path = out_dir / f"bench_{stamp}.json"
    md_path = out_dir / f"bench_{stamp}.md"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "diagnostic": diag.to_dict(),
            "scores": [s.to_dict() for s in scores],
        }, f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nreports written to {json_path} and {md_path}", file=sys.stderr)


class _PlaceholderAtom:
    name = "(unknown)"


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="substrate_index", description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT),
                        help=f"index root dir (default: {DEFAULT_ROOT})")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_stats = sub.add_parser("stats")
    p_stats.set_defaults(func=_cmd_stats)

    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("--atoms")
    p_ing.add_argument("--relations")
    p_ing.add_argument("--source", default="manual")
    p_ing.add_argument("--note", default="")
    p_ing.set_defaults(func=_cmd_ingest)

    p_q = sub.add_parser("query")
    p_q.add_argument("text")
    p_q.add_argument("--top", type=int, default=10)
    p_q.add_argument("--corpus")
    p_q.add_argument("--tier")
    p_q.set_defaults(func=_cmd_query)

    p_r = sub.add_parser("related")
    p_r.add_argument("atom_id")
    p_r.add_argument("--rel")
    p_r.add_argument("--direction", default="out", choices=["out", "in"])
    p_r.set_defaults(func=_cmd_related)

    p_p = sub.add_parser("paths")
    p_p.add_argument("src")
    p_p.add_argument("tgt")
    p_p.add_argument("--rel", nargs="*")
    p_p.add_argument("--max-depth", type=int, default=6)
    p_p.set_defaults(func=_cmd_paths)

    p_g = sub.add_parser("gaps")
    p_g.add_argument("--rel", required=True)
    p_g.add_argument("--direction", default="out", choices=["out", "in"])
    p_g.add_argument("--corpus")
    p_g.add_argument("--tier")
    p_g.set_defaults(func=_cmd_gaps)

    p_c = sub.add_parser("centrality")
    p_c.add_argument("--top", type=int, default=20)
    p_c.set_defaults(func=_cmd_centrality)

    p_a = sub.add_parser("algebraic")
    p_a.add_argument("atom_id")
    p_a.add_argument("rel")
    p_a.add_argument("--top", type=int, default=5)
    p_a.set_defaults(func=_cmd_algebraic)

    p_b = sub.add_parser("bench")
    p_b.add_argument("--queries", required=True)
    p_b.set_defaults(func=_cmd_bench)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
