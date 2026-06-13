"""Common mapper: facts.jsonl -> substrate Atom JSONL shards.

Per research_to_testbed_exp_dev_4_MILESTONES_ACK_..._EXTRACT_FROM_FACTS_COMMON_MAPPER_SKELETON_*_2026-06-13.md

Maps the 5 production corpora (arxiv_2m + conceptnet_8m + pubmed_5m + wikidata_truthy_50m
+ wikipedia_100k) to substrate atom JSONL via Q2+Q3 convention. Optional bge vector reuse
via keys.npy memory-map.

Each fact.jsonl line is JSON of form {"fact": "<string>"} (per inspection of arxiv_2m's
sample). String content interpreted per corpus-specific parser.

Output: data/substrate_index/<corpus>_atoms.shard_NNNN.jsonl shards (10K atoms each by
default) for downstream substrate_evolve_phase6_bulk_jsonl.py ingest.

Filter modes:
- math: keep facts mentioning math vocabulary (BATCH 01-16 atoms + extension)
- science: math + science vocab
- all: keep all parseable facts (warning: massive output for wikidata 3.4M)

Usage smoke:
  python tools/substrate_facts_jsonl_to_atoms_v1.py \\
    --facts-jsonl data/substrate_state/wikidata_truthy_50m/facts.jsonl \\
    --corpus wikidata --partition wikidata::truthy \\
    --output data/substrate_index/external/wikidata_atoms \\
    --filter math --max-facts 100000
"""
from __future__ import annotations
import argparse
import glob
import json
import re
import sys
import time
from pathlib import Path


# Per-corpus fact-string parsers (regex applied to the .fact field of each JSONL line)
FACT_PARSERS = {
    "wikidata": re.compile(
        r"^(?P<subj>Q\d+)\s+(?P<rel>P\d+|\w+)\s+(?P<obj>Q\d+|P\d+|[\d.eE+\-]+|\".*\")\s*\.?\s*$"
    ),
    "conceptnet": re.compile(
        r"^(?P<subj>/[ac]/[\w/]+)\s+(?P<rel>/r/\w+)\s+(?P<obj>/[ac]/[\w/]+)"
    ),
    "arxiv": re.compile(
        r"^(?P<paper_id>\d{4}\.\d{4,5}|[a-z\-]+/\d{7})\s+(?P<rel>\w+)\s+(?P<obj>.+)$"
    ),
    "pubmed": re.compile(r"^(?P<pmid>\d+)\s+(?P<rel>\w+)\s+(?P<obj>.+)$"),
    "wikipedia": re.compile(r"^(?P<article>[^\t]+)\t(?P<sentence>.+)$"),
}


MATH_VOCAB = {
    "vector_space", "inner_product", "kl_divergence", "shannon_entropy", "central_limit_theorem",
    "topology", "metric_space", "compactness", "completeness", "banach_space", "hilbert_space",
    "convex_function", "concave_function", "monotonicity", "linear_independence", "basis", "span",
    "derivative", "gradient", "jacobian", "hessian", "SVD", "eigendecomposition", "QR_decomposition",
    "gradient_descent", "convex_optimization", "lebesgue_measure", "lebesgue_integral",
    "brownian_motion", "martingale", "markov_chain", "fubini_tonelli", "radon_nikodym",
    "graph", "tree", "laplacian_matrix", "cheeger_inequality", "fiedler_vector",
    "newton_method", "monte_carlo", "kalman_filter", "em_algorithm", "viterbi_algorithm",
    "dynamic_programming", "variational_inference", "belief_propagation",
    "Q11862829", "Q5878", "Q333", "Q12483",
    "mathematics", "algebra", "calculus", "geometry", "logic", "set theory",
    "category theory", "functional analysis", "measure theory", "probability theory",
    "complex analysis", "real analysis", "differential geometry",
    "theorem", "lemma", "axiom", "corollary", "proof", "integer", "number",
    "function", "matrix", "vector", "manifold", "lie group", "ring", "field",
    "homomorphism", "isomorphism", "functor", "category", "metric",
}


SCIENCE_VOCAB = MATH_VOCAB | {
    "physics", "chemistry", "biology", "neuroscience", "biochemistry",
    "ecology", "evolution", "genetics", "molecular biology",
    "thermodynamics", "quantum mechanics", "relativity", "electromagnetism",
    "Q11471", "Q420", "Q42490",
    "neuron", "protein", "DNA", "RNA", "enzyme", "cell",
    "particle", "atom", "molecule", "wave", "field theory",
}


def matches_filter(fact_text: str, filter_mode: str) -> bool:
    if filter_mode == "all":
        return True
    vocab = MATH_VOCAB if filter_mode == "math" else SCIENCE_VOCAB
    fact_lower = fact_text.lower()
    return any(v.lower() in fact_lower for v in vocab)


def fact_to_atom(fact_str: str, corpus: str, partition: str, row_idx: int):
    """Parse a fact string into substrate atom dict (Q2+Q3 convention)."""
    parser = FACT_PARSERS.get(corpus)
    if parser is None:
        return None
    m = parser.match(fact_str.strip())
    if m is None:
        return None
    g = m.groupdict()

    if corpus == "wikidata":
        subj, rel, obj = g["subj"], g["rel"], g["obj"]
        return {
            "canonical_name": f"wikidata_{subj}",
            "aliases": [subj],
            "tier": "T3",
            "partition": partition,
            "science_algebra_category": f"wikidata::truthy::triple",
            "algebra_dict": {"subject": subj, "predicate": rel, "object": obj, "fact": fact_str.strip()},
            "is_axiom": False,
            "serves_capability": ["wikidata_knowledge_graph", "structured_triple_substrate"],
            "depends_on": [f"wikidata_{obj}"] if obj.startswith(("Q", "P")) else [],
            "signature_hint": "wikidata_truthy_triple",
            "bge_vec_row": row_idx,
        }
    if corpus == "conceptnet":
        subj, rel, obj = g["subj"], g["rel"], g["obj"]
        clean = lambda s: s.replace("/", "_").replace(" ", "_")
        return {
            "canonical_name": f"conceptnet_{clean(subj)}",
            "aliases": [subj.split("/")[-1]],
            "tier": "T3",
            "partition": partition,
            "science_algebra_category": f"conceptnet::{rel.lstrip('/r/')}",
            "algebra_dict": {"subject": subj, "relation": rel, "object": obj},
            "is_axiom": False,
            "serves_capability": ["conceptnet_commonsense", "relation_typed_edges"],
            "depends_on": [f"conceptnet_{clean(obj)}"],
            "signature_hint": "conceptnet_triple",
            "bge_vec_row": row_idx,
        }
    if corpus in ("arxiv", "pubmed"):
        paper_id = g.get("paper_id") or g.get("pmid")
        return {
            "canonical_name": f"{corpus}_{paper_id}",
            "aliases": [paper_id],
            "tier": "T3",
            "partition": partition,
            "science_algebra_category": f"{corpus}::paper",
            "algebra_dict": {"paper_id": paper_id, "extracted_fact": fact_str.strip()},
            "is_axiom": False,
            "serves_capability": [f"{corpus}_corpus_breadth"],
            "depends_on": [],
            "signature_hint": f"{corpus}_paper_fact",
            "bge_vec_row": row_idx,
        }
    if corpus == "wikipedia":
        article = g["article"]
        clean = article.replace(" ", "_")[:80]
        return {
            "canonical_name": f"wikipedia_{clean}_{row_idx}",
            "aliases": [article[:100]],
            "tier": "T3",
            "partition": partition,
            "science_algebra_category": "wikipedia::article_sentence",
            "algebra_dict": {"article": article, "sentence": g["sentence"][:1000]},
            "is_axiom": False,
            "serves_capability": ["wikipedia_breadth", "prose_corpus"],
            "depends_on": [],
            "signature_hint": "wikipedia_article_sentence",
            "bge_vec_row": row_idx,
        }
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts-jsonl", required=True, help="Path to facts.jsonl input")
    ap.add_argument("--corpus", required=True, choices=list(FACT_PARSERS.keys()))
    ap.add_argument("--partition", required=True, help="Partition string, e.g. wikidata::truthy")
    ap.add_argument("--output", required=True, help="Output path prefix (will write shard_NNNN.jsonl files)")
    ap.add_argument("--filter", default="math", choices=["all", "math", "science"])
    ap.add_argument("--shard-size", type=int, default=10000)
    ap.add_argument("--max-facts", type=int, default=None, help="Max input facts to process (smoke)")
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    rejected_filter = 0
    rejected_parse = 0
    shard_idx = 0
    shard_path = out_path.with_name(out_path.stem + f".shard_{shard_idx:04d}.jsonl")
    shard_file = shard_path.open("w", encoding="utf-8")
    t0 = time.time()

    with open(args.facts_jsonl, "r", encoding="utf-8", errors="ignore") as f:
        for row_idx, line in enumerate(f):
            if args.max_facts and row_idx >= args.max_facts:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                fact_str = obj.get("fact", "")
            except Exception:
                fact_str = line

            if not matches_filter(fact_str, args.filter):
                rejected_filter += 1
                continue
            atom = fact_to_atom(fact_str, args.corpus, args.partition, row_idx)
            if atom is None:
                rejected_parse += 1
                continue
            shard_file.write(json.dumps(atom) + "\n")
            written += 1
            if written % args.shard_size == 0:
                shard_file.close()
                shard_idx += 1
                shard_path = out_path.with_name(out_path.stem + f".shard_{shard_idx:04d}.jsonl")
                shard_file = shard_path.open("w", encoding="utf-8")
                elapsed = time.time() - t0
                rate = written / max(elapsed, 0.001)
                print(f"  shard {shard_idx-1}: written {written} ({rate:.0f}/s; row {row_idx+1})")

    shard_file.close()
    elapsed = time.time() - t0
    total_processed = written + rejected_filter + rejected_parse
    retention = (100 * written / max(total_processed, 1)) if total_processed else 0
    print(f"\n=== MAPPER SUMMARY ({args.corpus}) ===")
    print(f"  elapsed: {elapsed:.1f}s")
    print(f"  written: {written} atoms across {shard_idx + 1} shards")
    print(f"  rejected (filter): {rejected_filter}")
    print(f"  rejected (parse): {rejected_parse}")
    print(f"  retention: {retention:.1f}%")
    print(f"  output prefix: {out_path}")


if __name__ == "__main__":
    main()
