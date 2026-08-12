"""Local smoke suite — probes 6 mechanisms quickly while big experiments run remote.

Each probe runs in <30s on laptop CPU. Purpose: cheap empirical signal on mechanisms
that have cells in flight OR are candidates for next dispatch. Avoid waiting for
17-30h remote runs to inform direction.

Probes:
1. Random Indexing on real ConceptNet entities (cat-dog > cat-car?)
2. Iterative attractor cleanup on existing KGStore (does iter help over argmax?)
3. Templated response prototype on HotpotQA (entity-sequence -> English)
4. Substrate intent classifier sanity (Hebbian-bind queries -> categories)
5. Predictive-coding write-skip count (how many writes WOULD be skipped if residual-gated)
6. Cross-backend KG query consistency (does same query yield consistent shape across ConceptNet/HotpotQA/FB15k?)
"""

from __future__ import annotations

import json
import pickle
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np
import torch

from hdlab.kg_traversal import KGStore
from hdlab.char_trigram_encoder import CharTrigramEncoder
from hdlab.random_indexing import RandomIndexingEncoder as RandomIndexer

CACHE_DIR = REPO / "data" / "substrate_repl_cache"


def load_backend(short: str) -> dict:
    """Load chat backend by short name."""
    for p in CACHE_DIR.glob("kg_m*.pkl"):
        nm = p.name.lower()
        if short == "hotpotqa" and ("hotpot" in nm):
            with open(p, "rb") as f:
                return pickle.load(f)
        elif short == "fb15k" and "fb15k" in nm:
            with open(p, "rb") as f:
                return pickle.load(f)
        elif short == "conceptnet" and "conceptnet_100k" in nm:
            with open(p, "rb") as f:
                return pickle.load(f)
    raise FileNotFoundError(f"backend {short} not found")


def probe1_random_indexing_on_conceptnet():
    """Does Random Indexing produce cat-dog cosine > cat-car cosine on real ConceptNet entities?"""
    t0 = time.time()
    print("\n=== PROBE 1: Random Indexing on ConceptNet entities ===")
    cn = load_backend("conceptnet")
    triples = cn["triples_raw"]
    # Build a context-window stream from triples (subject occurs in context of object via predicate)
    stream = []
    for s, p, o in triples[:30000]:  # 30k triples ~= moderate vocab
        stream.append(s)
        stream.append(o)
    print(f"  stream tokens: {len(stream)}; unique vocab: {len(set(stream))}")
    ri = RandomIndexer(N=2048, sparsity=10, window=2, min_count=1, seed=7)
    ri.fit_corpus(stream)
    # Test pairs
    test_pairs = [("cat", "dog"), ("cat", "car"), ("happy", "sad"), ("happy", "house"),
                  ("teacher", "student"), ("teacher", "elephant")]
    print("  cosine similarities:")
    for a, b in test_pairs:
        try:
            sim = ri.similarity(a, b)
            print(f"    {a:12} ~ {b:12} = {sim:.4f}")
        except KeyError:
            print(f"    {a:12} ~ {b:12} = N/A (not in vocab)")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe2_iterative_attractor_vs_argmax():
    """Does iterative attractor cleanup (softmax over codebook) beat single-step argmax at high noise?"""
    t0 = time.time()
    print("\n=== PROBE 2: Iterative attractor vs argmax cleanup ===")
    rng = np.random.RandomState(7)
    N = 4096
    M = 500
    codebook = rng.choice([-1, 1], size=(M, N)).astype(np.float32)
    codebook = codebook / np.linalg.norm(codebook, axis=1, keepdims=True)
    for noise_level in [0.05, 0.20, 0.35, 0.45]:
        correct_argmax = 0
        correct_iter = 0
        for i in range(50):
            true_key = codebook[i].copy()
            noisy = true_key + noise_level * rng.randn(N).astype(np.float32)
            noisy = noisy / np.linalg.norm(noisy)
            # Argmax single-step
            sims = codebook @ noisy
            argmax_idx = int(np.argmax(sims))
            if argmax_idx == i:
                correct_argmax += 1
            # Iterative attractor (softmax + iterate)
            state = noisy.copy()
            for _ in range(5):
                sims = codebook @ state
                weights = np.exp(2.0 * sims)  # softmax with beta=2
                weights = weights / np.sum(weights)
                state = (codebook.T @ weights).astype(np.float32)
                state = state / (np.linalg.norm(state) + 1e-8)
            final_sims = codebook @ state
            iter_idx = int(np.argmax(final_sims))
            if iter_idx == i:
                correct_iter += 1
        print(f"  noise={noise_level:.2f}: argmax_recall={correct_argmax/50:.3f} iter_recall={correct_iter/50:.3f} lift={correct_iter-correct_argmax}")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe3_templated_response_hotpotqa():
    """Quick template-based response prototype on a few HotpotQA-style queries."""
    t0 = time.time()
    print("\n=== PROBE 3: Templated response prototype on HotpotQA ===")
    hp = load_backend("hotpotqa")
    kg = hp["kg"]
    ent2idx = hp["ent2idx"]
    rel2idx = hp["rel2idx"]
    idx2ent = sorted(ent2idx, key=lambda e: ent2idx[e])
    encoder = CharTrigramEncoder(n_dim=kg.n_dim)
    ent_codebook = encoder.encode_batch(idx2ent)
    test_queries = [
        ("doctor strange", "DIRECTED_BY"),
        ("doctor strange", "PRODUCED_BY"),
        ("ed wood", "IS_A"),
        ("scott derrickson", "IS_A"),
    ]
    for q_text, rel_name in test_queries:
        nearest = encoder.nearest(q_text, ent_codebook, idx2ent, k=1)
        anchor = nearest[0]["entity"]
        anchor_idx = ent2idx.get(anchor)
        if rel_name not in rel2idx:
            print(f"  '{q_text}' --{rel_name}--> N/A (relation absent in HotpotQA)")
            continue
        r_idx = rel2idx[rel_name]
        ti, ts = kg.predict_one_hop_topk(anchor_idx, r_idx, k=1)
        obj_name = idx2ent[int(ti[0])]
        # Template render
        templates = {
            "DIRECTED_BY": f"{anchor} was directed by {obj_name}.",
            "PRODUCED_BY": f"{anchor} was produced by {obj_name}.",
            "IS_A": f"{anchor} is a {obj_name}.",
            "WRITTEN_BY": f"{anchor} was written by {obj_name}.",
            "BORN_IN": f"{anchor} was born in {obj_name}.",
        }
        rendered = templates.get(rel_name, f"{anchor} -- {rel_name} --> {obj_name}")
        print(f"  Q: '{q_text}'  ->  {rendered}  (score={float(ts[0]):.1f})")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe4_intent_classifier_sanity():
    """Does Hebbian-bind queries -> categories work AT ALL on synthetic 7-category set?"""
    t0 = time.time()
    print("\n=== PROBE 4: Substrate intent classifier sanity ===")
    categories = {
        "WHO_DID": ["who directed X", "who wrote X", "who founded X", "who created X"],
        "WHAT_IS": ["what is X", "what does X mean", "define X"],
        "WHERE": ["where is X", "where was X born", "where is X located"],
        "WHEN": ["when did X happen", "when was X released", "when did X start"],
        "LIST": ["list X members", "what are X's children", "name X parts"],
        "COMPARE": ["are X and Y the same", "is X bigger than Y", "compare X and Y"],
        "COUNT": ["how many X", "count X", "number of X"],
    }
    N = 2048
    encoder = CharTrigramEncoder(n_dim=N)
    cat_names = list(categories.keys())
    # Encode each category as average of its training examples
    cat_vecs = {}
    for c, examples in categories.items():
        ex_vecs = encoder.encode_batch(examples)
        cat_vec = np.array(ex_vecs).sum(axis=0) if not isinstance(ex_vecs, np.ndarray) else ex_vecs.sum(axis=0)
        # Handle torch tensor case
        if hasattr(cat_vec, "numpy"):
            cat_vec = cat_vec.numpy()
        cat_vec = cat_vec / (np.linalg.norm(cat_vec) + 1e-8)
        cat_vecs[c] = cat_vec
    # Test on held-out (template variations not in training)
    test_q = {
        "who directed the new film": "WHO_DID",
        "what is photosynthesis": "WHAT_IS",
        "where is paris": "WHERE",
        "when did the war end": "WHEN",
        "list the planets": "LIST",
        "are dogs and cats similar": "COMPARE",
        "how many people live here": "COUNT",
    }
    correct = 0
    for q, expected in test_q.items():
        q_vec = encoder.encode(q)
        if hasattr(q_vec, "numpy"):
            q_vec = q_vec.numpy()
        q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        sims = {c: float(np.dot(cat_vecs[c], q_vec)) for c in cat_names}
        pred = max(sims, key=sims.get)
        match = "OK" if pred == expected else "XX"
        print(f"  {match} '{q[:40]:<40}' -> {pred:8} (expected {expected})")
        if pred == expected:
            correct += 1
    print(f"  accuracy: {correct}/{len(test_q)} = {correct/len(test_q):.2%}")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe5_predictive_coding_skip_count():
    """If we residual-gated ConceptNet ingest, how many writes would be skipped?"""
    t0 = time.time()
    print("\n=== PROBE 5: Predictive-coding write-skip count on ConceptNet ===")
    cn = load_backend("conceptnet")
    kg_existing = cn["kg"]  # Already ingested; we'll simulate residual-gating on a fresh small set
    triples = cn["triples_raw"]
    # Sample 500 triples; for each, compute current prediction error (residual)
    # before adding it. If residual < threshold, count as "would-skip"
    ent2idx = cn["ent2idx"]
    rel2idx = cn["rel2idx"]
    skips_at = {0.1: 0, 0.3: 0, 0.5: 0, 0.7: 0}
    n_tested = 0
    rng = np.random.RandomState(7)
    sample_indices = rng.choice(len(triples), size=500, replace=False)
    for ti in sample_indices:
        s, p, o = triples[ti]
        if s not in ent2idx or p not in rel2idx or o not in ent2idx:
            continue
        s_idx = ent2idx[s]
        p_idx = rel2idx[p]
        # What does substrate predict for (s, p)?
        try:
            predicted_idx = kg_existing.predict_one_hop(s_idx, p_idx)
            # Residual: how dissimilar is predicted_idx to true o?
            o_idx = ent2idx[o]
            if predicted_idx == o_idx:
                residual = 0.0  # perfectly predicted
            else:
                # Use score-based residual: how much higher is true score than predicted score?
                key = kg_existing.key(s_idx, p_idx)
                all_scores = kg_existing.score_all(key)
                true_score = float(all_scores[o_idx])
                pred_score = float(all_scores[predicted_idx])
                # Normalize: residual = (max - true) / max if true < max
                max_score = float(all_scores.max())
                residual = (max_score - true_score) / (abs(max_score) + 1e-8) if max_score > 0 else 0.0
            for thresh in skips_at:
                if residual < thresh:
                    skips_at[thresh] += 1
            n_tested += 1
        except Exception:
            continue
    print(f"  tested: {n_tested} triples")
    for thresh, count in skips_at.items():
        pct = count / max(n_tested, 1) * 100
        print(f"  residual < {thresh}: would skip {count}/{n_tested} = {pct:.1f}%")
    print(f"  wall: {time.time()-t0:.1f}s")


def probe6_cross_backend_query_consistency():
    """Same query across 3 backends — what does each surface?"""
    t0 = time.time()
    print("\n=== PROBE 6: Cross-backend query consistency ===")
    backends = {}
    for short in ("conceptnet", "hotpotqa", "fb15k"):
        try:
            backends[short] = load_backend(short)
        except FileNotFoundError:
            print(f"  {short}: backend missing")
    queries = ["paris", "computer", "love"]
    for q in queries:
        print(f"  Query: '{q}'")
        for short, payload in backends.items():
            ent2idx = payload["ent2idx"]
            idx2ent = sorted(ent2idx, key=lambda e: ent2idx[e])
            encoder = CharTrigramEncoder(n_dim=payload["kg"].n_dim)
            ent_codebook = encoder.encode_batch(idx2ent)
            nearest = encoder.nearest(q, ent_codebook, idx2ent, k=3)
            top = [n["entity"] for n in nearest[:3]]
            print(f"    {short:12} top-3: {top}")
    print(f"  wall: {time.time()-t0:.1f}s")


def main():
    t0 = time.time()
    print("LOCAL SMOKE SUITE 2026-06-22 — 6 mechanism probes")
    print("=" * 60)
    try:
        probe1_random_indexing_on_conceptnet()
    except Exception as e:
        print(f"  ERROR probe1: {type(e).__name__}: {e}")
    try:
        probe2_iterative_attractor_vs_argmax()
    except Exception as e:
        print(f"  ERROR probe2: {type(e).__name__}: {e}")
    try:
        probe3_templated_response_hotpotqa()
    except Exception as e:
        print(f"  ERROR probe3: {type(e).__name__}: {e}")
    try:
        probe4_intent_classifier_sanity()
    except Exception as e:
        print(f"  ERROR probe4: {type(e).__name__}: {e}")
    try:
        probe5_predictive_coding_skip_count()
    except Exception as e:
        print(f"  ERROR probe5: {type(e).__name__}: {e}")
    try:
        probe6_cross_backend_query_consistency()
    except Exception as e:
        print(f"  ERROR probe6: {type(e).__name__}: {e}")
    print(f"\n{'=' * 60}")
    print(f"TOTAL WALL: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
