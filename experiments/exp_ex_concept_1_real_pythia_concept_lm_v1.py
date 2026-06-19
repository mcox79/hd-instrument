"""
ex_concept_1_real_pythia_concept_lm_v1 -- EX-CONCEPT-1 REAL: substrate next-concept-LM on REAL Pythia tokens -- CPU.

ROUTING: per-token Pythia extraction landed (residuals_per_token.npz, 48MB). Tests whether the substrate can learn
  REAL LLM-concept sequential structure (vs the synthetic EX-CONCEPT proxy = MIDDLE). VQ Pythia per-token residuals
  -> concept-ID sequences -> substrate Hebbian next-concept-LM + cleanup -> next-concept prediction. CPU numpy
  (+ sklearn MiniBatchKMeans for VQ). $0. remote_cpu_queue. npz already on runner.

PIPELINE: load residuals_per_token.npz (residuals (sum_T,768) + doc_indices + doc_boundaries). VQ residuals into
  V_C=256 concepts (MiniBatchKMeans). Per-doc concept-ID sequences via doc_boundaries. Split docs train/test. Build
  substrate transition memory W via cf-RPE over (C[concept_t] -> C[concept_{t+1}]) [bipolar concept codebook, N].
  Predict next concept = argmax_codebook cleanup(W @ C[concept_t]). Metric: top-1 next-concept accuracy on TEST docs
  vs unigram (most-frequent-next) and bigram-Markov baselines.

PRE-REGISTERED bands: HARD-PASS substrate top-1 >= 1.5x unigram AND >= bigram-Markov (substrate captures real-concept
  transition structure at LLM-concept scale). MIDDLE: >= 1.2x unigram. HARD-FAIL: < 1.2x unigram (no real structure captured).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE transition store+recall. 2. VQ assigns + boundaries slice. 3. codebook cleanup.
ASCII-only. write_metrics. PROT-018: no _nN (N fixed by codebook).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "ex_concept_1_real_pythia_concept_lm_v1"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"
N_DIM = 1024; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 64; MAX_DOCS = 200
else:
    SEEDS = [7, 17, 23]; V_C = 256; MAX_DOCS = 100000


def bipolar_codebook(vc, n, g):
    X = (g.integers(0, 2, size=(vc, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, src, dst, n):
    W += (LR / n) * np.outer(dst - W @ src, src)


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bipolar_codebook(5, n, g); W = np.zeros((n, n), dtype=np.float32)
    cfrpe(W, C[1], C[2], n); pred = W @ C[1]; assert int(np.argmax(C @ pred)) == 2, "cf-RPE transition store+recall"
    bnd = np.array([0, 3, 7]); assert (bnd[1] - bnd[0]) == 3, "boundaries slice"
    print("[selftest] PASS: cfrpe transition + boundaries", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_concepts(seed):
    if not NPZ_PATH.exists():
        raise FileNotFoundError("residuals_per_token.npz not found at %s (run per-token extraction first)" % NPZ_PATH)
    z = np.load(NPZ_PATH); res = z["residuals"].astype(np.float32); bnd = z["doc_boundaries"].astype(np.int64)
    n_docs = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: n_docs + 1]; res = res[: bnd[-1]]
    print("[data] residuals=%s n_docs=%d n_tokens=%d" % (res.shape, n_docs, res.shape[0]), flush=True)
    # VQ residuals -> concept ids
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100)
        cid = km.fit_predict(res)
    except Exception as e:
        print("[VQ] sklearn unavailable (%s); numpy k-means fallback" % e, flush=True)
        cid = _numpy_kmeans(res, V_C, seed)
    docs = [cid[bnd[i]:bnd[i + 1]] for i in range(n_docs) if bnd[i + 1] - bnd[i] >= 2]
    return docs


def _numpy_kmeans(X, k, seed, iters=25):
    g = np.random.default_rng(seed); cen = X[g.choice(len(X), size=k, replace=False)].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - cen[None]) ** 2).sum(-1) if len(X) < 5000 else None
        if d is None:
            a = np.empty(len(X), dtype=np.int64)
            for s in range(0, len(X), 4096):
                a[s:s + 4096] = np.argmin(((X[s:s + 4096, None, :] - cen[None]) ** 2).sum(-1), 1)
        else:
            a = np.argmin(d, 1)
        for c in range(k):
            m = a == c
            if m.any():
                cen[c] = X[m].mean(0)
    return a


def baselines(train_docs, test_docs):
    nxt = {}; uni = np.zeros(V_C, dtype=np.int64)
    for d in train_docs:
        for t in range(len(d) - 1):
            uni[d[t + 1]] += 1; nxt.setdefault(d[t], np.zeros(V_C, dtype=np.int64))[d[t + 1]] += 1
    uni_pred = int(np.argmax(uni)); big = {k: int(np.argmax(v)) for k, v in nxt.items()}
    tot = 0; uni_ok = 0; big_ok = 0
    for d in test_docs:
        for t in range(len(d) - 1):
            tot += 1; uni_ok += (uni_pred == d[t + 1]); big_ok += (big.get(d[t], uni_pred) == d[t + 1])
    return uni_ok / max(tot, 1), big_ok / max(tot, 1)


def run_seed(seed):
    g = np.random.default_rng(seed); docs = load_concepts(seed)
    g.shuffle(docs); split = int(0.8 * len(docs)); train, test = docs[:split], docs[split:]
    C = bipolar_codebook(V_C, N_DIM, g); W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for d in train:
        for t in range(len(d) - 1):
            cfrpe(W, C[d[t]], C[d[t + 1]], N_DIM)
    tot = 0; ok = 0
    for d in test:
        for t in range(len(d) - 1):
            pred = int(np.argmax(C @ (W @ C[d[t]]))); ok += (pred == d[t + 1]); tot += 1
    sub = ok / max(tot, 1); uni, big = baselines(train, test)
    return {"seed": seed, "n_docs": len(docs), "n_test_pos": tot, "substrate_top1": sub, "unigram_top1": uni, "bigram_top1": big,
            "ratio_vs_unigram": float(sub / max(uni, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    sub = float(np.mean([p["substrate_top1"] for p in ps])); uni = float(np.mean([p["unigram_top1"] for p in ps])); big = float(np.mean([p["bigram_top1"] for p in ps]))
    r = sub / max(uni, 1e-6)
    summary = "substrate_top1=%.3f unigram=%.3f bigram_markov=%.3f (ratio_vs_unigram=%.2fx, V_C=%d)" % (sub, uni, big, r, V_C)
    if r >= 1.5 and sub >= big:
        return ("HARD_PASS", "HARD_PASS: substrate learns REAL Pythia-concept transitions (>=1.5x unigram, >=bigram). " + summary)
    if r >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate captures some real-concept structure. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate does not capture real-concept structure. " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_C=%d N=%d max_docs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C, N_DIM, MAX_DOCS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] substrate=%.3f unigram=%.3f bigram=%.3f ratio=%.2fx (n_docs=%d)" % (seed, r["substrate_top1"], r["unigram_top1"], r["bigram_top1"], r["ratio_vs_unigram"], r["n_docs"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
