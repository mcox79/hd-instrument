"""SKUNKWORKS DECISION 102b -- atom-MERGE inventory re-audit data dump.
Loads PartitionedStore ONCE; for each candidate name resolves the atom and prints
tier + description + the relations that decide MERGE vs SPECIALIZES vs composed_of.
Read-only. NO LLM. NO bge. ASCII only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

REL_SET = [RelationType.DEPENDS_ON, RelationType.USES, RelationType.INSTANCE_OF,
           RelationType.SPECIALIZES, RelationType.DUAL, RelationType.RELATES]

# candidate names to resolve (one per line; duplicates fine)
NAMES = [
    "cleanup", "cosine_cleanup", "cleanup_retrieval",
    "kullback_leibler_divergence", "kl_divergence",
    "viterbi_decoder", "viterbi_decoding",
    "collins_structured_perceptron", "structured_perceptron_collins", "structured_perceptron",
    "forward_algorithm", "backward_algorithm", "forward_backward_algorithm",
    "global_discrete_optimization", "convex_optimization", "discrete_optimization",
    "matrix_decomposition", "svd", "singular_value_decomposition",
    "group_homomorphism", "homomorphism", "ring_homomorphism",
]

def resolve(ps, query):
    if "::" in query and ps.has_atom(query):
        return ps.get_atom(query)
    for corpus in ("math", "concept", "science", "meta", "school"):
        qid = f"{corpus}::{query}"
        if ps.has_atom(qid):
            return ps.get_atom(qid)
    hits = []
    for a in ps.all_atoms():
        if a.id == query or a.id.lower().endswith("/" + query.lower()) or a.name.lower() == query.lower():
            hits.append(a)
    if hits:
        return hits[0] if len(hits) == 1 else hits
    return None

def relmap(ps, qid, fn):
    out = {}
    for rt in REL_SET:
        try:
            ns = fn(qid, rt) or set()
            if ns:
                out[rt.name] = sorted(ns)[:25]
        except Exception:
            pass
    return out

def show(ps, a):
    qid = a.qualified_id
    tier = a.tier.value if hasattr(a.tier, "value") else str(a.tier)
    corpus = a.corpus.value if hasattr(a.corpus, "value") else str(a.corpus)
    print(f"\n@@ {qid}  | tier={tier} corpus={corpus}")
    print(f"   name: {a.name}")
    print(f"   desc: {(a.description or '')[:240]}")
    if a.aliases:
        print(f"   aliases: {list(a.aliases)}")
    outn = relmap(ps, qid, ps.out_neighbors)
    inn = relmap(ps, qid, ps.in_neighbors)
    print(f"   OUT: {outn}")
    print(f"   IN : {inn}")

def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    seen = set()
    for name in NAMES:
        r = resolve(ps, name)
        print(f"\n===== query: {name} =====")
        if r is None:
            print("   NOT FOUND")
            continue
        if isinstance(r, list):
            print(f"   {len(r)} matches:")
            for a in r:
                if a.qualified_id in seen:
                    continue
                seen.add(a.qualified_id)
                show(ps, a)
        else:
            if r.qualified_id in seen:
                print(f"   (already shown above: {r.qualified_id})")
                continue
            seen.add(r.qualified_id)
            show(ps, r)

if __name__ == "__main__":
    main()
