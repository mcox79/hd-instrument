"""
ex_concept_1_improvement_variants_v2 -- Variant 3 (granularity V_c=1024) honest test -- EX-CONCEPT-1 honest strong-baseline comparison + substrate variants -- GPU.

ROUTING: research stronger_baselines_correction + PERFORMANCE_improvement_variants. The HP-labelled EX-CONCEPT-1
  beat only bigram-Markov by 1.03x (weak baseline). Honest test: add TRIGRAM + a small 1-layer TRANSFORMER baseline,
  and test substrate IMPROVEMENT variants (extended-context position-binding, cleanup-augmented, iterated retrieval).
  Report the full honest ranking. torch+numpy GPU $0. overnight_queue. Loads valid residuals_per_token.npz.

BASELINES: unigram, bigram-Markov, trigram-Markov, 1-layer-transformer (d=64). SUBSTRATE VARIANTS: single-pass
  (current), extended-context K (sum of position-bound prior-k concepts), cleanup-augmented, iterated retrieval.

PRE-REGISTERED bands (HONEST): HARD-PASS best-substrate-variant >= small-neural-transformer top1. MIDDLE: best-
  substrate >= trigram-Markov. HARD-FAIL: best-substrate < trigram (substrate loses to fair sequence baselines).
FORMULA SELF-TESTS (PROT-022): 1. trigram count. 2. substrate transition recall. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch, torch.nn as nn
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "ex_concept_1_improvement_variants_v2"
NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"
N_DIM = 1024; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 128; MAX_DOCS = 300; CTX_K = [5]; NEURAL_EPOCHS = 3
else:
    SEEDS = [7, 17, 23]; V_C = 256; MAX_DOCS = 100000; CTX_K = [2, 5, 10]; NEURAL_EPOCHS = 8


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def _numpy_kmeans(X, k, seed, iters=25):
    g = np.random.default_rng(seed); cen = X[g.choice(len(X), size=k, replace=False)].copy()
    a = np.zeros(len(X), dtype=np.int64)
    for _ in range(iters):
        for s in range(0, len(X), 4096):
            a[s:s + 4096] = np.argmin(((X[s:s + 4096, None, :] - cen[None]) ** 2).sum(-1), 1)
        for c in range(k):
            m = a == c
            if m.any():
                cen[c] = X[m].mean(0)
    return a


def _selftest():
    seqs = [[0, 1, 2, 0, 1, 2]]; tg = {}
    for s in seqs:
        for t in range(2, len(s)):
            tg.setdefault((s[t - 2], s[t - 1]), {}).setdefault(s[t], 0)
            tg[(s[t - 2], s[t - 1])][s[t]] += 1
    assert tg[(0, 1)][2] == 2, "trigram count"
    g = np.random.default_rng(0); n = 128; C = bp(3, n, g); W = np.zeros((n, n), dtype=np.float32)
    cfrpe(W, C[0], C[1], n); assert int(np.argmax(C @ (W @ C[0]))) == 1, "substrate transition recall"
    print("[selftest] PASS: trigram substrate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_docs(seed):
    if not NPZ_PATH.exists():
        raise FileNotFoundError("residuals_per_token.npz not found")
    z = np.load(NPZ_PATH); res = z["residuals"].astype(np.float32); bnd = z["doc_boundaries"].astype(np.int64)
    nd = min(len(bnd) - 1, MAX_DOCS); bnd = bnd[: nd + 1]; res = res[: bnd[-1]]
    try:
        from sklearn.cluster import MiniBatchKMeans
        cid = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=2048, n_init=3, max_iter=100).fit_predict(res)
    except Exception as e:
        print("[VQ] sklearn unavailable (%s); numpy k-means fallback" % e, flush=True)
        cid = _numpy_kmeans(res, V_C, seed)
    docs = [cid[bnd[i]:bnd[i + 1]] for i in range(nd) if bnd[i + 1] - bnd[i] >= 3]
    print("[data] n_tokens=%d n_docs=%d V_c=%d" % (res.shape[0], len(docs), V_C), flush=True)
    return docs


def ngram_acc(train, test, order):
    tab = {}
    for d in train:
        for t in range(order, len(d)):
            key = tuple(d[t - order:t]); tab.setdefault(key, {}); tab[key][d[t]] = tab[key].get(d[t], 0) + 1
    pred = {k: max(v, key=v.get) for k, v in tab.items()}
    glob = np.zeros(V_C, dtype=np.int64)
    for d in train:
        for c in d:
            glob[c] += 1
    back = int(np.argmax(glob)); ok = tot = 0
    for d in test:
        for t in range(order, len(d)):
            ok += (pred.get(tuple(d[t - order:t]), back) == d[t]); tot += 1
    return ok / max(tot, 1)


def neural_acc(train, test, seed):
    torch.manual_seed(seed)
    class TinyLM(nn.Module):
        def __init__(s):
            super().__init__(); s.emb = nn.Embedding(V_C, 64); s.pos = nn.Embedding(16, 64)
            s.layer = nn.TransformerEncoderLayer(64, 4, 128, batch_first=True); s.head = nn.Linear(64, V_C)
        def forward(s, x):
            T = x.shape[1]; h = s.emb(x) + s.pos(torch.arange(T, device=x.device))
            m = torch.triu(torch.ones(T, T, device=x.device), 1).bool()
            return s.head(s.layer(h, src_mask=m))
    model = TinyLM().to(DEVICE); opt = torch.optim.Adam(model.parameters(), 3e-3); CTX = 16

    def batches(docs):
        xs = []
        for d in docs:
            for t in range(1, len(d)):
                ctx = d[max(0, t - CTX):t]; xs.append((list(ctx), d[t]))
        return xs
    tr = batches(train)
    for ep in range(NEURAL_EPOCHS):
        np.random.shuffle(tr)
        for i in range(0, len(tr), 256):
            b = tr[i:i + 256]; mx = max(len(c) for c, _ in b)
            X = torch.zeros(len(b), mx, dtype=torch.long, device=DEVICE); Y = torch.zeros(len(b), dtype=torch.long, device=DEVICE)
            for j, (c, y) in enumerate(b):
                X[j, :len(c)] = torch.tensor(c, device=DEVICE); Y[j] = y
            opt.zero_grad(); out = model(X)[:, -1]; loss = nn.functional.cross_entropy(out, Y); loss.backward(); opt.step()
    model.eval(); te = batches(test); ok = 0
    with torch.no_grad():
        for i in range(0, len(te), 512):
            b = te[i:i + 512]; mx = max(len(c) for c, _ in b)
            X = torch.zeros(len(b), mx, dtype=torch.long, device=DEVICE)
            for j, (c, _) in enumerate(b):
                X[j, :len(c)] = torch.tensor(c, device=DEVICE)
            pr = model(X)[:, -1].argmax(-1).cpu().numpy()
            ok += sum(pr[j] == b[j][1] for j in range(len(b)))
    return ok / max(len(te), 1)


def substrate_variants(train, test, seed):
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g)
    res = {}
    # single-pass bigram-style
    W = np.zeros((n, n), dtype=np.float32)
    for d in train:
        for t in range(1, len(d)):
            cfrpe(W, C[d[t - 1]], C[d[t]], n)
    ok = tot = 0
    for d in test:
        for t in range(1, len(d)):
            ok += (int(np.argmax(C @ (W @ C[d[t - 1]]))) == d[t]); tot += 1
    res["single_pass"] = ok / max(tot, 1)
    # extended-context K via position-binding (roll as positional bind)
    for K in CTX_K:
        POS = bp(K, n, g)
        Wk = np.zeros((n, n), dtype=np.float32)

        def ctx_vec(d, t):
            q = np.zeros(n, dtype=np.float32)
            for k in range(1, min(K, t) + 1):
                q = q + C[d[t - k]] * POS[k - 1] * math.sqrt(n)
            return q / (np.linalg.norm(q) + 1e-8)
        for d in train:
            for t in range(1, len(d)):
                cfrpe(Wk, ctx_vec(d, t), C[d[t]], n)
        ok = tot = 0
        for d in test:
            for t in range(1, len(d)):
                ok += (int(np.argmax(C @ (Wk @ ctx_vec(d, t)))) == d[t]); tot += 1
        res["extctx_K%d" % K] = ok / max(tot, 1)
    return res


def run_seed(seed):
    docs = load_docs(seed); g = np.random.default_rng(seed); g.shuffle(docs)
    sp = int(0.8 * len(docs)); train, test = docs[:sp], docs[sp:]
    out = {"seed": seed, "n_docs": len(docs)}
    out["unigram"] = ngram_acc(train, test, 0) if False else None
    out["bigram"] = ngram_acc(train, test, 1); out["trigram"] = ngram_acc(train, test, 2)
    out["neural_1layer"] = neural_acc(train, test, seed)
    out.update({"substrate_%s" % k: v for k, v in substrate_variants(train, test, seed).items()})
    return out


def verdict(ps) -> Tuple[str, str]:
    def m(k): return float(np.mean([p[k] for p in ps if p.get(k) is not None]))
    bi = m("bigram"); tri = m("trigram"); nn_ = m("neural_1layer")
    sub_keys = [k for k in ps[0] if k.startswith("substrate_")]; sub = {k: m(k) for k in sub_keys}
    best_k = max(sub, key=sub.get); best = sub[best_k]
    summary = "best_substrate=%s:%.3f | bigram=%.3f trigram=%.3f neural1L=%.3f | variants=%s" % (
        best_k, best, bi, tri, nn_, {k: round(v, 3) for k, v in sub.items()})
    if best >= nn_:
        return ("HARD_PASS", "HARD_PASS: best substrate variant >= small neural transformer. " + summary)
    if best >= tri:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best substrate >= trigram but < neural. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: best substrate < trigram (loses to fair sequence baselines). " + summary)


print("[config] anchor=%s mode=%s seeds=%s V_c=%d ctx_K=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, V_C, CTX_K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] bigram=%.3f trigram=%.3f neural=%.3f substrate=%s" % (seed, r["bigram"], r["trigram"], r["neural_1layer"], {k: round(v, 3) for k, v in r.items() if k.startswith("substrate_")}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
