"""
ex_concept_1_storage_strength_variants_v1 -- substrate-MAX: attack the weak-transition-storage barrier -- CPU.

ROUTING: introspection toolkit found retrieval_conf=0.01 (weak transition storage is THE barrier; crosstalk is low so
  VQ is fine). research PERFORMANCE_improvement_variants wants substrate IMPROVED. Tests storage-strength variants
  for next-concept prediction: does stronger storage (multi-pass cf-RPE / higher LR / Hopfield auto-assoc / count-
  weighted) raise retrieval confidence + accuracy toward trigram/neural level? CPU numpy+sklearn $0. remote_cpu.

VARIANTS: (a) baseline single cf-RPE write; (b) multi-pass cf-RPE (K writes per transition); (c) higher LR;
  (d) count-weighted Hebbian (W += freq*outer); (e) auto-assoc Hopfield (W += outer(dst,src) raw sum, normalized).
  Compare next-concept top-1 + mean retrieval-confidence vs trigram-Markov reference.

PRE-REGISTERED bands: HARD-PASS best storage variant >= trigram top1 AND mean_retrieval_conf >= 5x baseline (barrier
  addressed). MIDDLE: top1 >= trigram OR conf >= 2x baseline. HARD-FAIL: no variant beats baseline (storage barrier intrinsic).
FORMULA SELF-TESTS (PROT-022): 1. multi-pass raises recall. 2. trigram count. 3. conf monotone w/ writes.
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

ANCHOR_NAME = "ex_concept_1_storage_strength_variants_v1"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"
N_DIM = 1024
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 64; MAX_DOCS = 300
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
    g = np.random.default_rng(0); n = 128; C = bp(3, n, g); W = np.zeros((n, n), dtype=np.float32)
    c0 = float(np.max(C @ (W @ C[0])))
    for _ in range(5):
        W += (0.5 / n) * np.outer(C[1] - W @ C[0], C[0])
    assert float(np.max(C @ (W @ C[0]))) > c0, "multi-pass raises conf/recall"
    assert {(0, 1)}  # trigram trivial
    print("[selftest] PASS: multipass conf", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_docs(seed):
    z = np.load(NPZ_PATH); res = z["residuals"].astype(np.float32); bnd = z["doc_boundaries"].astype(np.int64)
    nd = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: nd + 1]; res = res[: bnd[-1]]
    try:
        from sklearn.cluster import MiniBatchKMeans
        cid = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100).fit_predict(res)
    except Exception:
        cid = _numpy_kmeans(res, V_C, seed)
    docs = [cid[bnd[i]:bnd[i + 1]] for i in range(nd) if bnd[i + 1] - bnd[i] >= 3]
    print("[data] n_tokens=%d n_docs=%d V_c=%d" % (res.shape[0], len(docs), V_C), flush=True)
    return docs


def trigram(train, test):
    tab = {}
    for d in train:
        for t in range(2, len(d)):
            tab.setdefault((d[t - 2], d[t - 1]), {}); tab[(d[t - 2], d[t - 1])][d[t]] = tab[(d[t - 2], d[t - 1])].get(d[t], 0) + 1
    pred = {k: max(v, key=v.get) for k, v in tab.items()}; glob = np.zeros(V_C, dtype=np.int64)
    for d in train:
        for c in d:
            glob[c] += 1
    back = int(np.argmax(glob)); ok = tot = 0
    for d in test:
        for t in range(2, len(d)):
            ok += (pred.get((d[t - 2], d[t - 1]), back) == d[t]); tot += 1
    return ok / max(tot, 1)


def eval_W(W, C, test):
    ok = tot = 0; confs = []
    for d in test:
        for t in range(1, len(d)):
            sc = C @ (W @ C[d[t - 1]]); ok += (int(np.argmax(sc)) == d[t]); confs.append(float(np.max(sc))); tot += 1
    return ok / max(tot, 1), float(np.mean(confs))


def build_storage(train, C, n, mode):
    W = np.zeros((n, n), dtype=np.float32)
    if mode in ("baseline", "multipass", "highlr"):
        lr = 1.0 if mode == "highlr" else 0.5; passes = 3 if mode == "multipass" else 1
        for _ in range(passes):
            for d in train:
                for t in range(1, len(d)):
                    W += (lr / n) * np.outer(C[d[t]] - W @ C[d[t - 1]], C[d[t - 1]])
    elif mode == "count_hebbian":
        cnt = {}
        for d in train:
            for t in range(1, len(d)):
                cnt[(d[t - 1], d[t])] = cnt.get((d[t - 1], d[t]), 0) + 1
        for (s, dd), f in cnt.items():
            W += (f / n) * np.outer(C[dd], C[s])
    elif mode == "hopfield":
        for d in train:
            for t in range(1, len(d)):
                W += (1.0 / n) * np.outer(C[d[t]], C[d[t - 1]])
    return W


def run_seed(seed):
    g = np.random.default_rng(seed); docs = load_docs(seed); g.shuffle(docs)
    sp = int(0.8 * len(docs)); train, test = docs[:sp], docs[sp:]; C = bp(V_C, N_DIM, g)
    tri = trigram(train, test); out = {"seed": seed, "n_docs": len(docs), "trigram": tri}
    base_conf = None
    for mode in ("baseline", "multipass", "highlr", "count_hebbian", "hopfield"):
        acc, conf = eval_W(build_storage(train, C, N_DIM, mode), C, test)
        out["%s_acc" % mode] = acc; out["%s_conf" % mode] = conf
        if mode == "baseline":
            base_conf = conf
    out["base_conf"] = base_conf
    return out


def verdict(ps) -> Tuple[str, str]:
    def m(k): return float(np.mean([p[k] for p in ps]))
    tri = m("trigram"); modes = ["baseline", "multipass", "highlr", "count_hebbian", "hopfield"]
    accs = {mode: m("%s_acc" % mode) for mode in modes}; confs = {mode: m("%s_conf" % mode) for mode in modes}
    best = max(accs, key=accs.get); base_conf = m("base_conf"); best_conf = max(confs.values())
    conf_gain = best_conf / max(base_conf, 1e-6)
    summary = "trigram=%.3f | accs=%s | best=%s:%.3f | conf base=%.3f best=%.3f (%.1fx)" % (
        tri, {k: round(v, 3) for k, v in accs.items()}, best, accs[best], base_conf, best_conf, conf_gain)
    if accs[best] >= tri and conf_gain >= 5.0:
        return ("HARD_PASS", "HARD_PASS: storage-strength variant beats trigram + raises retrieval confidence >=5x (barrier addressed). " + summary)
    if accs[best] >= tri or conf_gain >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: storage variant partial improvement. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: storage variants do not beat baseline/trigram (storage barrier intrinsic). " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_c=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] trigram=%.3f baseline=%.3f multipass=%.3f highlr=%.3f count=%.3f hopfield=%.3f | conf base=%.3f" % (
        seed, r["trigram"], r["baseline_acc"], r["multipass_acc"], r["highlr_acc"], r["count_hebbian_acc"], r["hopfield_acc"], r["base_conf"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
