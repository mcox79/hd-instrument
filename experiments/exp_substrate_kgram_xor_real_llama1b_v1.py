"""
substrate_kgram_xor_real_llama1b_v1 -- K2-XOR rescue on REAL Llama-1B concept sequences -- CPU.

ROUTING: research phase2_ack (K2-XOR-1B BUILDING NEXT). Synthetic K2-XOR-1 showed XOR k-gram context binding rescues
  bigram-level prediction 4.54x. Does it hold on REAL Llama-1B concept sequences? VQ the 1B per-token residuals into
  concept-IDs; per-doc sequences; test K1 (single-token query) vs K2/K3 (XOR k-gram context). Retrieval-side only,
  all moats preserved. CPU numpy+sklearn $0. Loads 1B npz.

PRE-REGISTERED bands: HARD-PASS acc(K2) >= 1.20x acc(K1) on real 1B sequences (rescue robust across LLM tiers).
  MIDDLE: 1.05-1.20x. HARD-FAIL: <=1.02x (rescue does not transfer to real data -> drill).
FORMULA SELF-TESTS (PROT-022): 1. XOR bind self-inverse. 2. k-gram key distinguishes contexts.
ASCII-only. write_metrics. PROT-018: no _nN.
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

ANCHOR_NAME = "substrate_kgram_xor_real_llama1b_v1"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"
N_DIM = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 128; MAX_DOCS = 400
else:
    SEEDS = [7, 17, 23]; V_C = 256; MAX_DOCS = 100000


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _numpy_kmeans(X, k, seed, iters=25):
    g = np.random.default_rng(seed); cen = X[g.choice(len(X), size=k, replace=False)].copy(); a = np.zeros(len(X), dtype=np.int64)
    for _ in range(iters):
        for s in range(0, len(X), 4096):
            a[s:s + 4096] = np.argmin(((X[s:s + 4096, None, :] - cen[None]) ** 2).sum(-1), 1)
        for c in range(k):
            m = a == c
            if m.any():
                cen[c] = X[m].mean(0)
    return a


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bp(3, n, g) * math.sqrt(n)
    b = C[0] * C[1]; assert np.allclose((b * C[1]) / n, C[0] / n, atol=1e-4), "XOR bind self-inverse"
    k_ab = C[0] * C[1]; k_cb = C[2] * C[1]
    assert float((k_ab * k_cb).sum()) < float((k_ab * k_ab).sum()), "k-gram key distinguishes contexts"
    print("[selftest] PASS: xor kgram", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_concept_seqs(seed):
    if not NPZ_PATH.exists():
        raise FileNotFoundError("Llama-1B npz not found at %s" % NPZ_PATH)
    d = np.load(NPZ_PATH); res = d["residuals"].astype(np.float32); bnd = d["doc_boundaries"].astype(np.int64)
    nd = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: nd + 1]; res = res[: bnd[-1]]
    try:
        from sklearn.cluster import MiniBatchKMeans
        cid = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100).fit_predict(res)
    except Exception:
        cid = _numpy_kmeans(res, V_C, seed)
    seqs = [cid[bnd[i]:bnd[i + 1]] for i in range(nd) if bnd[i + 1] - bnd[i] >= 3]
    print("[data] n_tokens=%d n_docs=%d V_c=%d" % (res.shape[0], len(seqs), V_C), flush=True)
    return seqs


def ngram_acc(train, test, order):
    tab = {}
    for d in train:
        for t in range(order, len(d)):
            key = tuple(int(x) for x in d[t - order:t]); tab.setdefault(key, {}); tab[key][int(d[t])] = tab[key].get(int(d[t]), 0) + 1
    pred = {k: max(v, key=v.get) for k, v in tab.items()}; glob = np.zeros(V_C, dtype=np.int64)
    for d in train:
        for c in d:
            glob[int(c)] += 1
    back = int(np.argmax(glob)); ok = tot = 0
    for d in test:
        for t in range(order, len(d)):
            ok += (pred.get(tuple(int(x) for x in d[t - order:t]), back) == int(d[t])); tot += 1
    return ok / max(tot, 1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g) * math.sqrt(n); Cn = C / math.sqrt(n)
    seqs = load_concept_seqs(seed); g.shuffle(seqs); sp = int(0.8 * len(seqs)); train, test = seqs[:sp], seqs[sp:]
    bi = ngram_acc(train, test, 1); tri = ngram_acc(train, test, 2)

    def acc_k(k):
        Wm = np.zeros((n, n), dtype=np.float32)
        for d in train:                                   # build XOR k-gram context keys per doc, batched per doc
            if len(d) <= k:
                continue
            da = np.asarray(d); keys = Cn[da].copy()
            for j in range(1, k):
                keys[j:] = keys[j:] * Cn[da[:-j]]
            keys /= (np.linalg.norm(keys, axis=1, keepdims=True) + 1e-8)
            Wm += Cn[da[k:]].T @ keys[k - 1:len(da) - 1]
        ok = tot = 0
        for d in test:
            if len(d) <= k:
                continue
            da = np.asarray(d); keys = Cn[da].copy()
            for j in range(1, k):
                keys[j:] = keys[j:] * Cn[da[:-j]]
            keys /= (np.linalg.norm(keys, axis=1, keepdims=True) + 1e-8)
            sc = keys[k - 1:len(da) - 1] @ Wm.T @ C.T; ok += int(np.sum(sc.argmax(1) == da[k:])); tot += len(da) - k
        return ok / max(tot, 1)

    k1 = acc_k(1); k2 = acc_k(2); k3 = acc_k(3)
    return {"seed": seed, "K1_acc": k1, "K2_acc": k2, "K3_acc": k3, "bigram": bi, "trigram": tri, "ratio_K2_K1": float(k2 / max(k1, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    k1 = float(np.mean([p["K1_acc"] for p in ps])); k2 = float(np.mean([p["K2_acc"] for p in ps])); k3 = float(np.mean([p["K3_acc"] for p in ps]))
    bi = float(np.mean([p["bigram"] for p in ps])); tri = float(np.mean([p["trigram"] for p in ps])); r = k2 / max(k1, 1e-6)
    summary = "K1=%.3f K2=%.3f K3=%.3f (K2/K1=%.2fx) | bigram=%.3f trigram=%.3f (real Llama-1B concepts, V=%d)" % (k1, k2, k3, r, bi, tri, V_C)
    if r >= 1.20:
        return ("HARD_PASS", "HARD_PASS: XOR k-gram rescue holds on REAL Llama-1B concepts (>=1.2x K1; robust across LLM tiers). " + summary)
    if r >= 1.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: XOR rescue modest on real 1B. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: XOR rescue does not transfer to real 1B sequences. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] K1=%.3f K2=%.3f K3=%.3f (K2/K1=%.2fx) bigram=%.3f trigram=%.3f" % (seed, r["K1_acc"], r["K2_acc"], r["K3_acc"], r["ratio_K2_K1"], r["bigram"], r["trigram"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
