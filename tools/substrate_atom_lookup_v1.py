"""Atom lookup CLI helper -- substrate introspection for Research convenience.

Quick CLI for querying atom metadata + serves_capability + in/out neighbors +
algebra dict without navigating substrate_query.py's full subcommand surface.

Use cases:
  - "what does T2/cleanup depend on?"
  - "which atoms reference cauchy_schwarz_inequality?"
  - "what capabilities does discriminative_perceptron serve?"
  - "show me the full atom dict for fhrr_bind"

Usage:
  python tools/substrate_atom_lookup_v1.py <atom_qid_or_name>
      [--show deps,in,caps,algebra]
      [--max-neighbors 20]
      [--json]

Examples:
  python tools/substrate_atom_lookup_v1.py T2/cleanup
  python tools/substrate_atom_lookup_v1.py math::T1/inner_product --show deps,caps
  python tools/substrate_atom_lookup_v1.py fhrr_bind --json

NO LLM. NO bge. Read-only substrate query. Milliseconds wall.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# DECISION 124b: UTF-8-safe stdout so atoms carrying imported proper-name diacritics
# (Erdos double-acute, Mobius umlaut, ...) or math symbols (lambda, perp) do NOT crash
# the Windows cp1252 default codec. errors='replace' is a last-resort fallback.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


def resolve_atom(ps: PartitionedStore, query: str):
    """Try to resolve query as qualified id, then atom-id substring, then name."""
    # Direct qualified id
    if "::" in query and ps.has_atom(query):
        return ps.get_atom(query)
    # Try each corpus prefix
    for corpus in ("math", "concept", "science", "meta", "school"):
        qid = f"{corpus}::{query}"
        if ps.has_atom(qid):
            return ps.get_atom(qid)
    # Try suffix match across all atoms (slower)
    for a in ps.all_atoms():
        if a.id == query or a.id.endswith("/" + query) or a.name.lower() == query.lower():
            return a
    # Try alias match
    for a in ps.all_atoms():
        if a.aliases and any(query.lower() == al.lower() for al in a.aliases):
            return a
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("query", help="Qualified id, atom id, or name to look up")
    ap.add_argument("--show", default="all",
                    help="Comma-separated sections: deps,in,caps,algebra,all")
    ap.add_argument("--max-neighbors", type=int, default=20)
    ap.add_argument("--json", action="store_true", help="JSON output instead of pretty-print")
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    atom = resolve_atom(ps, args.query)
    if atom is None:
        print(f"NOT FOUND: '{args.query}' -- try qualified id (e.g. math::T2/cleanup)")
        sys.exit(2)

    qid = atom.qualified_id
    sections = set(args.show.split(",")) if args.show != "all" else {"deps", "in", "caps", "algebra"}

    out = {
        "qid": qid,
        "name": atom.name,
        "corpus": atom.corpus.value if hasattr(atom.corpus, "value") else str(atom.corpus),
        "tier": atom.tier.value if hasattr(atom.tier, "value") else str(atom.tier),
        "kind": atom.kind.value if hasattr(atom.kind, "value") else str(atom.kind),
        "description": (atom.description or "")[:300],
        "aliases": list(atom.aliases or ()),
    }
    if "caps" in sections:
        out["serves_capability"] = list(atom.serves_capability or ())
    if "algebra" in sections:
        out["algebra"] = atom.algebra
        if atom.metadata:
            out["metadata"] = atom.metadata
    if "deps" in sections:
        out_deps = {}
        for rt in (RelationType.DEPENDS_ON, RelationType.USES, RelationType.INSTANCE_OF,
                   RelationType.SPECIALIZES, RelationType.DEFINED_OVER, RelationType.DUAL):
            try:
                ns = ps.out_neighbors(qid, rt) or set()
                if ns:
                    out_deps[rt.name] = sorted(ns)[: args.max_neighbors]
            except Exception:
                pass
        out["out_neighbors"] = out_deps
    if "in" in sections:
        in_neighbors = {}
        for rt in (RelationType.DEPENDS_ON, RelationType.USES, RelationType.INSTANCE_OF,
                   RelationType.SPECIALIZES, RelationType.DEFINED_OVER, RelationType.DUAL):
            try:
                ns = ps.in_neighbors(qid, rt) or set()
                if ns:
                    in_neighbors[rt.name] = sorted(ns)[: args.max_neighbors]
            except Exception:
                pass
        out["in_neighbors"] = in_neighbors

    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return

    # Pretty print
    print(f"=== {qid} ===")
    print(f"name: {out['name']}")
    print(f"tier: {out['tier']}  corpus: {out['corpus']}  kind: {out['kind']}")
    if out["aliases"]:
        print(f"aliases: {out['aliases']}")
    if out["description"]:
        print(f"\ndescription: {out['description']}")
    if "caps" in sections and out.get("serves_capability"):
        print(f"\nserves_capability ({len(out['serves_capability'])}):")
        for c in out["serves_capability"]:
            print(f"  - {c}")
    if "algebra" in sections and out.get("algebra"):
        print(f"\nalgebra:")
        for k, v in (out["algebra"] or {}).items():
            vs = str(v)
            if len(vs) > 80:
                vs = vs[:80] + "..."
            print(f"  {k}: {vs}")
    if "deps" in sections and out.get("out_neighbors"):
        print(f"\nout-neighbors (this atom -> X):")
        for rt, nlist in out["out_neighbors"].items():
            print(f"  {rt} ({len(nlist)}):")
            for n in nlist:
                print(f"    -> {n}")
    if "in" in sections and out.get("in_neighbors"):
        print(f"\nin-neighbors (X -> this atom):")
        for rt, nlist in out["in_neighbors"].items():
            print(f"  {rt} ({len(nlist)}):")
            for n in nlist:
                print(f"    <- {n}")


if __name__ == "__main__":
    main()
