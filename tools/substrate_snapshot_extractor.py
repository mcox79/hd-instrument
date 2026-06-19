"""Substrate snapshot extractor for TRACK D 3D substrate visualization.

READ-ONLY: scans data/substrate_index/<corpus>/{atoms,relations}.jsonl across
the corpora requested (default: math + concept per DECISION 187c Q3 ruling),
computes per-node degree, and emits data/substrate_snapshot.json in the
3d-force-graph schema:
    {"nodes": [{"id", "label", "corpus", "tier", "kind", "degree", ...}],
     "links": [{"source", "target", "type", "metadata"}]}

Bare IDs in JSONL records (e.g. "T1/vector_space") get the corpus prefix
applied (-> "math::T1/vector_space"); cross-corpus refs (e.g. "math::T2/cleanup"
in concept/relations.jsonl) are preserved as-is.

Usage:
    python tools/substrate_snapshot_extractor.py
    python tools/substrate_snapshot_extractor.py --corpus math --min-degree 1
    python tools/substrate_snapshot_extractor.py --tier T1 T2 T3
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"
DEFAULT_OUTPUT = REPO / "data" / "substrate_snapshot.json"
DEFAULT_CORPORA = ("math", "concept")


def qualify(node_id: str, corpus: str) -> str:
    return node_id if "::" in node_id else f"{corpus}::{node_id}"


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out: list[dict] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"  WARN: skipping bad line in {path.name}: {exc}", file=sys.stderr)
    return out


def derive_node_kind(atom: dict, corpus: str) -> str:
    raw_kind = (atom.get("kind") or "").strip()
    if raw_kind:
        return raw_kind
    if corpus == "concept":
        return "capability"
    return "atom"


def derive_ratify_status(atom: dict) -> str:
    metadata = atom.get("metadata") or {}
    if atom.get("current_best_solution"):
        return "current_best_solution"
    history = atom.get("solution_history") or []
    if history:
        last = history[-1]
        status = (last.get("status") or "").lower()
        if status:
            return status
    distillation = metadata.get("distillation_class")
    if distillation:
        return f"distill:{distillation}"
    return "atom_present"


def derive_label(atom: dict) -> str:
    return (atom.get("name") or atom.get("id") or "?").strip()


def collect(corpora: list[str]) -> tuple[dict[str, dict], list[dict]]:
    nodes: dict[str, dict] = {}
    links: list[dict] = []
    for corpus in corpora:
        atom_path = SUBSTRATE_INDEX / corpus / "atoms.jsonl"
        relation_path = SUBSTRATE_INDEX / corpus / "relations.jsonl"
        if not atom_path.is_file():
            print(f"  WARN: corpus '{corpus}' atoms.jsonl missing; skipping", file=sys.stderr)
            continue
        for atom in read_jsonl(atom_path):
            raw_id = atom.get("id")
            if not raw_id:
                continue
            qid = qualify(raw_id, corpus)
            if qid in nodes:
                continue
            nodes[qid] = {
                "id": qid,
                "label": derive_label(atom),
                "corpus": corpus,
                "tier": (atom.get("tier") or "?").strip(),
                "kind": derive_node_kind(atom, corpus),
                "ratify_status": derive_ratify_status(atom),
                "serves_capability": atom.get("serves_capability") or [],
                "current_best_solution": atom.get("current_best_solution"),
                "metadata_summary": {
                    "domain": (atom.get("algebra") or {}).get("domain"),
                    "structure": (atom.get("algebra") or {}).get("structure"),
                    "distillation_class": (atom.get("metadata") or {}).get("distillation_class"),
                },
            }
        for rel in read_jsonl(relation_path):
            src = rel.get("src_id")
            tgt = rel.get("tgt_id")
            if not src or not tgt:
                continue
            links.append(
                {
                    "source": qualify(src, corpus),
                    "target": qualify(tgt, corpus),
                    "type": (rel.get("rel_type") or "?").strip(),
                    "metadata": rel.get("metadata") or {},
                }
            )
    return nodes, links


def compute_degree(links: list[dict]) -> dict[str, int]:
    degree: dict[str, int] = defaultdict(int)
    for link in links:
        degree[link["source"]] += 1
        degree[link["target"]] += 1
    return degree


def apply_filters(
    nodes: dict[str, dict],
    links: list[dict],
    min_degree: int,
    tier_filter: set[str] | None,
    kind_filter: set[str] | None,
) -> tuple[dict[str, dict], list[dict]]:
    if tier_filter:
        nodes = {nid: n for nid, n in nodes.items() if n.get("tier") in tier_filter}
    if kind_filter:
        nodes = {nid: n for nid, n in nodes.items() if n.get("kind") in kind_filter}
    links = [l for l in links if l["source"] in nodes and l["target"] in nodes]
    if min_degree > 0:
        degree = compute_degree(links)
        keep = {nid for nid in nodes if degree.get(nid, 0) >= min_degree}
        nodes = {nid: n for nid, n in nodes.items() if nid in keep}
        links = [l for l in links if l["source"] in nodes and l["target"] in nodes]
    return nodes, links


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract substrate snapshot for 3D viz.")
    ap.add_argument("--corpus", nargs="+", default=list(DEFAULT_CORPORA),
                    help="Corpora to include (default: math concept).")
    ap.add_argument("--tier", nargs="+", default=None,
                    help="Tier filter (e.g. T1 T2 T3). Default: all.")
    ap.add_argument("--kind", nargs="+", default=None,
                    help="Kind filter (e.g. primitive capability). Default: all.")
    ap.add_argument("--min-degree", type=int, default=0,
                    help="Drop nodes with degree below this. Default: 0 (keep all).")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT),
                    help=f"Output JSON path (default: {DEFAULT_OUTPUT.relative_to(REPO)}).")
    ap.add_argument("--include-orphans", action="store_true",
                    help="Keep degree-0 nodes (off by default if --min-degree>0).")
    args = ap.parse_args()

    print(f"[extractor] reading corpora: {args.corpus}")
    nodes, links = collect(args.corpus)
    print(f"[extractor] loaded {len(nodes)} nodes, {len(links)} links pre-filter")

    tier_filter = set(args.tier) if args.tier else None
    kind_filter = set(args.kind) if args.kind else None
    nodes, links = apply_filters(nodes, links, args.min_degree, tier_filter, kind_filter)

    degree = compute_degree(links)
    for nid, node in nodes.items():
        node["degree"] = degree.get(nid, 0)

    output_payload = {
        "schema_version": "3d-force-graph/v1",
        "generated_corpora": list(args.corpus),
        "filters": {
            "tier": sorted(tier_filter) if tier_filter else None,
            "kind": sorted(kind_filter) if kind_filter else None,
            "min_degree": args.min_degree,
        },
        "summary": {
            "node_count": len(nodes),
            "link_count": len(links),
            "tier_breakdown": _breakdown(nodes, "tier"),
            "kind_breakdown": _breakdown(nodes, "kind"),
            "link_type_breakdown": _breakdown_list(links, "type"),
        },
        "nodes": sorted(nodes.values(), key=lambda n: (n.get("corpus", ""), n.get("tier", ""), n["id"])),
        "links": links,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024.0
    print(f"[extractor] wrote {output_path} ({size_kb:.1f} KB)")
    print(f"[extractor] summary: {len(nodes)} nodes / {len(links)} links")
    for label, breakdown in output_payload["summary"].items():
        if label.endswith("_breakdown"):
            top = sorted(breakdown.items(), key=lambda kv: -kv[1])[:6]
            print(f"[extractor]   {label}: " + ", ".join(f"{k}={v}" for k, v in top))
    return 0


def _breakdown(nodes: dict[str, dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for n in nodes.values():
        counts[n.get(field) or "?"] += 1
    return dict(counts)


def _breakdown_list(items: list[dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        counts[item.get(field) or "?"] += 1
    return dict(counts)


if __name__ == "__main__":
    sys.exit(main())
