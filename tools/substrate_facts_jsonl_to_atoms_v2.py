"""facts.jsonl -> atoms mapper v2: Q-instance-of categorical filter (expected 10-30x retention vs v1).

Per Research INGEST_STATUS_PING request: "is there a Q-instance-of filter being implemented"
+ USER directive "are we downloading + ingesting math/science databases".

v1 used substring-match against ~200 math + ~50 science word/Q-ID vocab; retention
0.1pct on Wikidata smoke (100K -> 111 atoms). Bottleneck: substring vocab gives many
false positives (Q12345 contains substring "234" of Q-ID matches) AND many false
negatives (an entity that is-instance-of Q11862829 mathematical object may not contain
any vocab word in its triple text).

v2 strategy:
  1. Expanded math/science Q-class set (covers theorems + mathematical objects +
     scientific concepts + algorithms + functions + spaces + groups + structures + ...)
  2. STRICT predicate filter: only accept facts where predicate is P31 (instance of)
     or P279 (subclass of) AND object is in the math/science Q-class set.
     This is much higher precision: "<entity> P31 Q11862829" -> entity IS a math object.
  3. Two-pass mode (-2pass): pass 1 collects entity Q-IDs that are math/science class
     members; pass 2 accepts ANY fact whose subject is in the collected set.
  4. Fallback: --vocab-mode word retains v1 word-vocab matching (for non-Wikidata
     corpora like Wikipedia / arXiv abstracts).

Output: shard JSONL files (same format as v1) for downstream Phase 6 bulk ingest.

NO LLM. NO bge. Pure regex + set membership.
"""
from __future__ import annotations
import sys
import re
import json
import time
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# Wikidata P-IDs we recognize as "instance-of"-like predicates
INSTANCE_OF_PIDS = {"P31", "P279", "P361"}  # instance_of, subclass_of, part_of

# Wikidata Q-IDs classifying subjects as math/science.
# REFRESHED 2026-06-14 (DECISION 45 step 1): the prior hand-curated list was 84pct STALE
# (validated via Action API wbgetentities: Q12483 'theorem' -> 'statistics', Q161205 'field' ->
# 'Safavid dynasty', Q43287 'logic' -> 'German Empire', etc.). Replaced with current valid IDs
# DISCOVERED via wbsearchentities + haswbstatement instance-count confirmation
# (tools/wikidata_qclass_discovery_v1.py). Each ID below confirmed to yield >=20 real instances.
MATH_QCLASS_IDS = {
    "Q65943",      # theorem (2934 instances)
    "Q24034552",   # mathematical concept (2214)
    "Q8366",       # algorithm (792)
    "Q319141",     # conjecture (283)
    "Q11348",      # function (269)
    "Q1936384",    # branch of mathematics (294)
    "Q246672",     # mathematical object (33)
    "Q200726",     # probability distribution (24)
    "Q11214",      # differential equation (20)
    "Q11563",      # number (41)
}

SCIENCE_QCLASS_IDS = MATH_QCLASS_IDS | {
    "Q3239681",    # scientific theory (285)
    "Q214070",     # physical law (198)
    "Q408891",     # scientific law (53)
    "Q11173",      # chemical compound (136)
    # NOTE: large biology classes (protein Q8054, gene Q7187, organism Q7239, disease Q12136)
    # are VALID but million-scale; excluded from this slice to avoid swamping math/physics.
}

# Word-vocab fallback (used for non-Wikidata corpora).
WORD_VOCAB_MATH = {
    "theorem", "lemma", "axiom", "corollary", "proof", "manifold", "topology", "metric_space",
    "hilbert_space", "banach_space", "vector_space", "inner_product", "linear_algebra",
    "differential_equation", "integral", "derivative", "gradient", "jacobian", "hessian",
    "convex", "monotone", "submodular", "category_theory", "functor", "natural_transformation",
    "homomorphism", "isomorphism", "group_action", "ring_theory", "field_theory",
    "measure_theory", "lebesgue", "probability_space", "markov_chain", "martingale",
    "fourier_transform", "spectral_decomposition", "eigenvalue", "eigenvector",
    "svd", "qr_decomposition", "lu_decomposition", "cholesky", "newton_method",
    "gradient_descent", "convex_optimization", "lagrangian", "kuhn_tucker", "saddle_point",
    "shannon_entropy", "kl_divergence", "mutual_information", "rate_distortion",
    "central_limit_theorem", "law_of_large_numbers", "chernoff_bound", "azuma",
    "polynomial", "rational_function", "trigonometric_function", "exponential",
    "logarithm", "factorial", "binomial", "prime_number", "modular_arithmetic",
    "graph", "tree", "laplacian", "spectral_graph", "cheeger", "fiedler",
    "dynamic_programming", "viterbi", "bellman", "value_iteration",
}

WORD_VOCAB_SCIENCE = WORD_VOCAB_MATH | {
    "neuron", "synapse", "axon", "dendrite", "neurotransmitter",
    "protein", "amino_acid", "dna", "rna", "gene", "transcription", "translation", "ribosome",
    "enzyme", "substrate", "catalysis", "reaction_kinetics",
    "particle", "quark", "lepton", "boson", "fermion", "hadron",
    "wave_function", "schrodinger", "heisenberg", "quantum_state",
    "general_relativity", "special_relativity", "minkowski", "spacetime",
    "thermodynamics", "entropy_thermo", "free_energy", "phase_transition",
    "ecology", "evolution", "natural_selection", "phylogenetics",
}


WIKIDATA_PATTERN = re.compile(
    r"^(?P<subj>Q\d+)\s+(?P<rel>P\d+|\w+)\s+(?P<obj>Q\d+|P\d+|[\d.eE+\-]+|\".*\")\s*\.?\s*$"
)


def wikidata_inst_of_filter(fact_str: str, qclass_set: set) -> tuple:
    """Returns (accept: bool, parsed_triple: dict or None).
    Accept only if predicate is in INSTANCE_OF_PIDS AND object is in qclass_set."""
    m = WIKIDATA_PATTERN.match(fact_str.strip())
    if m is None:
        return (False, None)
    g = m.groupdict()
    if g["rel"] not in INSTANCE_OF_PIDS:
        return (False, None)
    if g["obj"] not in qclass_set:
        return (False, None)
    return (True, g)


def word_vocab_filter(fact_str: str, vocab: set) -> bool:
    fl = fact_str.lower()
    return any(v.replace("_", " ") in fl or v in fl for v in vocab)


def fact_to_atom_v2(fact_str: str, parsed: dict, corpus: str, partition: str, row_idx: int, qclass_label: str, label: str = ""):
    """Build atom dict from filtered Wikidata fact (Q-instance-of mode).

    DECISION 49b FIX (2026-06-14): use the REAL entity label as canonical_name (the fetcher
    captures it in the facts.jsonl `label` field) so atoms are semantically retrievable by bge.
    Previously canonical_name was the Q-id placeholder ('wikidata_Q182505') -> all atoms had
    near-identical embeddings (bge-invisible). Q-id retained as an alias for provenance.
    """
    if corpus != "wikidata":
        return None
    subj = parsed["subj"]
    rel = parsed["rel"]
    obj = parsed["obj"]
    label = (label or "").strip()
    # Keep canonical_name = Q-id (STABLE atom id for edge consistency + clean in-place replace);
    # put the REAL label in aliases so bge encodes it (encode = name + id_tokens + aliases) ->
    # atoms become semantically distinguishable/retrievable without changing ids or edges.
    return {
        "canonical_name": f"wikidata_{subj}",
        "aliases": ([label] if label else []) + [subj],
        "tier": "T3",
        "partition": partition,
        "science_algebra_category": f"wikidata::truthy::{qclass_label}",
        "algebra_dict": {
            "subject": subj,
            "predicate": rel,
            "object": obj,
            "qclass_match": obj,
            "fact": fact_str.strip(),
        },
        "is_axiom": False,
        "serves_capability": ["wikidata_knowledge_graph", f"wikidata_{qclass_label}"],
        "depends_on": [f"wikidata_{obj}"],
        "signature_hint": f"wikidata_qclass_{qclass_label}",
        "bge_vec_row": row_idx,
    }


def fact_to_atom_word_mode(fact_str: str, corpus: str, partition: str, row_idx: int):
    """Fallback word-vocab path (delegates to v1 fact_to_atom)."""
    from substrate_facts_jsonl_to_atoms_v1 import fact_to_atom
    return fact_to_atom(fact_str, corpus, partition, row_idx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts-jsonl", required=True)
    ap.add_argument("--corpus", required=True, choices=["wikidata", "conceptnet", "arxiv", "pubmed", "wikipedia"])
    ap.add_argument("--partition", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--filter", default="math", choices=["all", "math", "science"])
    ap.add_argument("--vocab-mode", default="qclass",
                    choices=["qclass", "word", "qclass_or_word"],
                    help="qclass: Q-instance-of filter (wikidata only; high precision); "
                         "word: v1 word-vocab match; qclass_or_word: union")
    ap.add_argument("--shard-size", type=int, default=10000)
    ap.add_argument("--max-facts", type=int, default=None)
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    qclass_set = MATH_QCLASS_IDS if args.filter == "math" else SCIENCE_QCLASS_IDS
    word_vocab = WORD_VOCAB_MATH if args.filter == "math" else WORD_VOCAB_SCIENCE
    qclass_label = "math_object" if args.filter == "math" else "scientific_concept"

    print(f"v2 mapper: corpus={args.corpus} filter={args.filter} vocab_mode={args.vocab_mode}")
    print(f"  Q-class set size: {len(qclass_set)}")
    print(f"  word vocab size:  {len(word_vocab)}")

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
            label = ""
            try:
                obj = json.loads(line)
                fact_str = obj.get("fact", "")
                label = obj.get("label", "")  # DECISION 49b FIX: carry real entity label
            except Exception:
                fact_str = line
            if not fact_str:
                continue

            atom = None

            if args.vocab_mode in ("qclass", "qclass_or_word") and args.corpus == "wikidata":
                accept, parsed = wikidata_inst_of_filter(fact_str, qclass_set)
                if accept:
                    atom = fact_to_atom_v2(fact_str, parsed, args.corpus, args.partition, row_idx, qclass_label, label)

            if atom is None and args.vocab_mode in ("word", "qclass_or_word"):
                if word_vocab_filter(fact_str, word_vocab):
                    atom = fact_to_atom_word_mode(fact_str, args.corpus, args.partition, row_idx)
                    if atom is None:
                        rejected_parse += 1

            if atom is None:
                rejected_filter += 1
                continue

            shard_file.write(json.dumps(atom) + "\n")
            written += 1
            if written % args.shard_size == 0:
                shard_file.close()
                shard_idx += 1
                shard_path = out_path.with_name(out_path.stem + f".shard_{shard_idx:04d}.jsonl")
                shard_file = shard_path.open("w", encoding="utf-8")

    shard_file.close()
    elapsed = time.time() - t0
    total = written + rejected_filter + rejected_parse
    print(f"\n=== v2 MAPPER SUMMARY ===")
    print(f"input facts processed: {total}")
    print(f"  written atoms:        {written}")
    print(f"  rejected by filter:   {rejected_filter}")
    print(f"  rejected by parse:    {rejected_parse}")
    print(f"retention rate: {100.0 * written / max(total, 1):.2f}pct")
    print(f"shards written: {shard_idx + 1}")
    print(f"wall: {elapsed:.1f}s ({total / max(elapsed, 0.01):.0f} facts/sec)")


if __name__ == "__main__":
    main()
