"""Layer 1 attribution sweep on tier_tag and corpus_tag weights.

Per methodology rule 6 + FINDINGS_04 commitment: every encoding choice in
the substrate-self-index composite must earn its weight empirically. We
caught algebra-vec as NET NEGATIVE. tier_tag (0.3) and corpus_tag (0.3)
haven't been audited.

This script runs Q1-Q5 with the composite varying:
  weights tested = [(1.0, 0.0, 0.0),  # semantic only
                    (1.0, 0.3, 0.0),  # +tier_tag
                    (1.0, 0.0, 0.3),  # +corpus_tag
                    (1.0, 0.3, 0.3),  # current default
                    (1.0, 0.5, 0.5),  # heavier
                    (1.0, 1.0, 1.0),  # equal weight]

For each (semantic_w, tier_w, corpus_w) combo, computes rank-of-expected for
each query. Reports attribution: did tier_tag move ranks up, down, or
neutral? Same for corpus_tag.

Per [[feedback-literature-is-not-oracle-2026-06-11]]: include literature
prediction as a hypothesis. Default 0.3 weights are guess + convention. The
empirical sweep may reveal substrate-self-index prefers different weights.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.encode import AtomEncoder, _atom_id_vector
from backend.substrate_index.schema import Atom, Corpus, RelationType, Tier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("layer1_tier_corpus")

DATA_ROOT = Path("data/substrate_index")
BATCH02_QUERIES_PATH = DATA_ROOT / "math_corpus_batch02_disclosed_queries.json"


def compute_composite(semantic: np.ndarray, tier_tag: np.ndarray, corpus_tag: np.ndarray,
                      sem_w: float, tier_w: float, corpus_w: float) -> np.ndarray:
    """Compute composite from sub-vectors at custom weights."""
    v = sem_w * semantic + tier_w * tier_tag + corpus_w * corpus_tag
    norm = np.linalg.norm(v)
    if norm < 1e-12:
        return v
    return v / norm


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("loading encoder...")
    encoder = AtomEncoder()
    atoms = pstore.all_atoms()
    log.info("encoding %d atoms (batched bge)", len(atoms))
    # Get semantic vectors via the encoder
    av_dict = encoder.encode_atoms(atoms)
    # Re-extract semantic from each (composite includes tier/corpus already; want raw)
    atom_ids = []
    semantics = []
    tier_tags = []
    corpus_tags = []
    for a in atoms:
        av = av_dict[a.id]
        atom_ids.append(a.qualified_id)
        semantics.append(av.semantic)
        tier_tags.append(encoder._tier_tags[a.tier])
        corpus_tags.append(encoder._corpus_tags[a.corpus])
    semantic_mat = np.stack(semantics)
    tier_mat = np.stack(tier_tags)
    corpus_mat = np.stack(corpus_tags)

    # Load disclosed queries
    with BATCH02_QUERIES_PATH.open("r", encoding="utf-8") as f:
        queries_raw = json.load(f)
    if isinstance(queries_raw, dict):
        queries_raw = queries_raw.get("queries", []) or queries_raw.get("disclosed_queries", [])

    weight_combos = [
        ("semantic_only",        1.0, 0.0, 0.0),
        ("plus_tier",            1.0, 0.3, 0.0),
        ("plus_corpus",          1.0, 0.0, 0.3),
        ("default",              1.0, 0.3, 0.3),
        ("heavy_tier_corpus",    1.0, 0.5, 0.5),
        ("equal",                1.0, 1.0, 1.0),
    ]

    # For each combo, run each query and record top-3
    print(f"\n{'='*80}")
    print("Layer 1 attribution on tier_tag + corpus_tag")
    print(f"{'='*80}")
    print(f"\nAtoms: {len(atoms)} | Queries: {len(queries_raw)}\n")

    all_results = {}
    for combo_name, sem_w, tier_w, corpus_w in weight_combos:
        # Build composite matrix for this combo
        composite_mat = np.zeros_like(semantic_mat)
        for i in range(len(atom_ids)):
            composite_mat[i] = compute_composite(
                semantic_mat[i], tier_mat[i], corpus_mat[i],
                sem_w, tier_w, corpus_w,
            )
        # Run each query
        per_query = {}
        for q_rec in queries_raw:
            qid = q_rec.get("qid", q_rec.get("id", "Q?"))
            query_text = q_rec.get("query_text") or q_rec.get("text") or q_rec.get("question")
            if not query_text:
                continue
            q_vec = encoder.encode_query_text(query_text)
            sims = composite_mat @ q_vec
            order = np.argsort(-sims)[:5]
            top_5 = [atom_ids[i] for i in order]
            per_query[qid] = top_5
        all_results[combo_name] = per_query

    # Render attribution table
    print(f"{'combo':<25s}  Q1  Q2  Q3  Q4  Q5")
    print(f"{'-'*70}")
    for combo_name, _, _, _ in weight_combos:
        line = f"{combo_name:<25s}"
        for q_rec in queries_raw:
            qid = q_rec.get("qid", q_rec.get("id", "Q?"))
            top = all_results[combo_name].get(qid, [])
            short = top[0].split("::")[-1] if top else "-"
            short = short[:12]
            line += f"  {short:<12s}"
        print(line)

    # Per-query: did adding tier or corpus move the top result?
    print(f"\n=== Attribution decomposition (per query) ===")
    for q_rec in queries_raw:
        qid = q_rec.get("qid", q_rec.get("id", "Q?"))
        query_text = q_rec.get("query_text") or ""
        top_sem = all_results["semantic_only"].get(qid, ["-"])[0]
        top_tier = all_results["plus_tier"].get(qid, ["-"])[0]
        top_corpus = all_results["plus_corpus"].get(qid, ["-"])[0]
        top_default = all_results["default"].get(qid, ["-"])[0]
        tier_change = "CHANGED" if top_tier != top_sem else "neutral"
        corpus_change = "CHANGED" if top_corpus != top_sem else "neutral"
        default_change = "CHANGED" if top_default != top_sem else "neutral"
        print(f"  {qid}: tier={tier_change} corpus={corpus_change} default={default_change}")
        if any(c == "CHANGED" for c in (tier_change, corpus_change, default_change)):
            print(f"    semantic-only: {top_sem.split('::')[-1]}")
            print(f"    +tier:         {top_tier.split('::')[-1]}")
            print(f"    +corpus:       {top_corpus.split('::')[-1]}")
            print(f"    default(both): {top_default.split('::')[-1]}")

    # Persist
    out = DATA_ROOT / "bench_reports" / f"layer1_tier_corpus_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "weight_combos": [{"name": n, "sem": sw, "tier": tw, "corpus": cw}
                          for n, sw, tw, cw in weight_combos],
        "per_combo_query_results": all_results,
    }, indent=2), encoding="utf-8")
    log.info("wrote attribution report -> %s", out)


if __name__ == "__main__":
    main()
