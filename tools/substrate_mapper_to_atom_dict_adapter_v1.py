"""Adapter: convert mapper-shape JSONL -> Atom.from_dict-compatible JSONL.

Per Research INGEST_STATUS_PING question 3: "does substrate_evolve_phase6_bulk_jsonl.py
pipeline auto-ingest [mapper] shards? Or is there a manual step?"

ANSWER: Phase 6 pipeline EXISTS but mapper output schema does NOT match Atom.from_dict
expectations. This adapter is the missing step.

Mapper output (v1/v2) shape:
  { canonical_name, aliases, tier, partition, science_algebra_category, algebra_dict,
    is_axiom, serves_capability, depends_on, signature_hint, bge_vec_row }

Atom.from_dict expected shape:
  { id, name, corpus, tier, kind, description, aliases, metadata, algebra, signature,
    complexity, concept_links, current_best_solution, solution_history, serves_capability }

Transformation (per mapper-output -> Atom-dict mapping):
  canonical_name -> id (with optional Tier prefix like "T3/<name>" if not already prefixed)
  canonical_name -> name (humanized fallback)
  partition -> corpus (split on "::"; first segment maps to MATH/CONCEPT/SCIENCE/SCHOOL/META)
  tier -> tier (string passes through; Atom.from_dict normalizes)
  algebra_dict -> algebra (renamed)
  is_axiom + signature_hint + science_algebra_category + bge_vec_row -> metadata
  depends_on -> SEPARATE relations file (not Atom field; Phase 6 wires from solution_history,
                  so we additionally emit a sibling _relations.jsonl for downstream)
  serves_capability -> serves_capability (passes through)

Outputs:
  <out>.jsonl          - Atom.from_dict-compatible atoms ready for substrate_evolve_phase6_bulk_jsonl.py
  <out>_relations.jsonl - DEPENDS_ON edges ready for substrate_ingest_math_batch03_relations.py
"""
from __future__ import annotations
import sys
import json
import re
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


_BARE_QID_RE = re.compile(r"^Q\d+$")


PARTITION_TO_CORPUS = {
    "wikidata": "math",
    "conceptnet": "concept",
    "arxiv": "science",
    "pubmed": "science",
    "wikipedia": "concept",
}


def partition_to_corpus(partition: str) -> str:
    """Map mapper partition (e.g. 'wikidata::truthy') to substrate corpus enum value."""
    if not partition:
        return "math"
    head = partition.split("::")[0]
    return PARTITION_TO_CORPUS.get(head, "math")


def humanize_name(canonical_name: str, aliases: list | None = None) -> str:
    """Humanize a canonical_name for atom.name field.

    Prefers aliases[0] when present and not a bare Q-id (e.g. 'Q182505') — the
    wikidata mapper leaves canonical_name as 'wikidata_Q182505' but stores the
    real English label at aliases[0] ('Bayes\\' theorem'). Falls back to the
    underscore-humanized canonical_name (backward-compatible).
    """
    if aliases:
        first = aliases[0]
        if isinstance(first, str) and first and not _BARE_QID_RE.match(first):
            return first[:120]
    raw = canonical_name.replace("_", " ")
    return raw[:120]


def adapt_atom(mapper_rec: dict) -> tuple:
    """Adapt one mapper-output dict to (atom_dict, deps_edges_list).

    Returns (None, []) if record is unparseable."""
    cn = mapper_rec.get("canonical_name")
    if not cn:
        return None, []

    tier = str(mapper_rec.get("tier", "T3"))
    partition = mapper_rec.get("partition", "")
    corpus = partition_to_corpus(partition)

    # Build id: if canonical_name already has a tier prefix (e.g. "T1/recursion") use as-is;
    # otherwise prefix with tier.
    if "/" in cn:
        atom_id = cn
    else:
        atom_id = f"{tier}/{cn}"

    metadata = {}
    sac = mapper_rec.get("science_algebra_category")
    if sac:
        metadata["science_algebra_category"] = sac
    sh = mapper_rec.get("signature_hint")
    if sh:
        metadata["signature_hint"] = sh
    if "is_axiom" in mapper_rec:
        metadata["is_axiom"] = mapper_rec["is_axiom"]
    bgv = mapper_rec.get("bge_vec_row")
    if bgv is not None:
        metadata["bge_vec_row"] = bgv
    if partition:
        metadata["partition_origin"] = partition

    atom_dict = {
        "id": atom_id,
        "name": humanize_name(cn, mapper_rec.get("aliases")),
        "corpus": corpus,
        "tier": tier,
        "kind": "PRIMITIVE",
        "description": json.dumps(mapper_rec.get("algebra_dict", {}))[:500],
        "aliases": list(mapper_rec.get("aliases", [])),
        "metadata": metadata,
        "algebra": mapper_rec.get("algebra_dict") or None,
        "serves_capability": list(mapper_rec.get("serves_capability", [])),
    }

    # Build DEPENDS_ON edges (separate file)
    deps_edges = []
    src_qid = f"{corpus}::{atom_id}"
    for dep_name in mapper_rec.get("depends_on", []):
        # Dep name may be unqualified ("wikidata_Q12345") or qualified
        if "::" in dep_name:
            tgt_qid = dep_name
        else:
            if "/" not in dep_name:
                tgt_local = f"{tier}/{dep_name}"
            else:
                tgt_local = dep_name
            tgt_qid = f"{corpus}::{tgt_local}"
        deps_edges.append({
            "src": src_qid,
            "rel_type": "DEPENDS_ON",
            "tgt": tgt_qid,
            "source": "mapper_v2_adapter",
            "note": f"mapped from {partition or 'unknown_partition'}",
        })
    return atom_dict, deps_edges


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mapper-jsonl", required=True,
                    help="Path to mapper-output JSONL (one shard or merged)")
    ap.add_argument("--output", required=True,
                    help="Output prefix; writes <output>.jsonl + <output>_relations.jsonl")
    args = ap.parse_args()

    out_atoms = Path(args.output + ".jsonl")
    out_rels = Path(args.output + "_relations.jsonl")
    out_atoms.parent.mkdir(parents=True, exist_ok=True)

    atom_count = 0
    edge_count = 0
    fail_count = 0
    with open(args.mapper_jsonl, "r", encoding="utf-8") as fin, \
         out_atoms.open("w", encoding="utf-8") as fout_a, \
         out_rels.open("w", encoding="utf-8") as fout_r:
        for line_no, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                fail_count += 1
                continue
            atom, edges = adapt_atom(rec)
            if atom is None:
                fail_count += 1
                continue
            fout_a.write(json.dumps(atom) + "\n")
            atom_count += 1
            for e in edges:
                fout_r.write(json.dumps(e) + "\n")
                edge_count += 1

    print(f"=== ADAPTER SUMMARY ===")
    print(f"  input lines:    {atom_count + fail_count}")
    print(f"  atoms emitted:  {atom_count} -> {out_atoms}")
    print(f"  edges emitted:  {edge_count} -> {out_rels}")
    print(f"  failed/skipped: {fail_count}")
    print(f"\nNext steps:")
    print(f"  1. ingest atoms: python tools/substrate_evolve_phase6_bulk_jsonl.py '{out_atoms}'")
    print(f"  2. ingest edges: python tools/substrate_ingest_math_batch03_relations.py '{out_rels}'")


if __name__ == "__main__":
    main()
