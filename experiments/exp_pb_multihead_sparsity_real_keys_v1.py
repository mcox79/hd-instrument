"""
exp_pb_multihead_sparsity_real_keys_v1 -- propose-back (does synthetic multi-head x sparsity compound hold on REAL keys) -- GPU.

ROUTING: Exp-Dev propose-back. The synthetic multi-head-sparse-key battery found multi-head composes with sparse keys
  (MMV sqrt(M) gain). Open question: does that compound survive REAL encoder-key statistics (dense, correlated)? Encodes
  real MiniLM keys, applies the production recipe (ZCA-whiten + sign), then measures exact-recovery capacity for
  {1,2,4}-head x {dense, sparse-top20pct} on the SAME real keys. Multi-head = split load across independent pinv heads;
  sparsity = keep top-20pct |whitened| dims per key. GPU (encoder forward).
PRE-REGISTERED: HARD-PASS 4-head capacity >= 3x single-head AND sparse >= dense at matched heads (both levers transfer to
  real keys). MID one lever transfers. HARD-FAIL neither (real-key correlation kills the compound).
FORMULA SELF-TESTS (PROT-022): 1. pinv projector. 2. whiten preserves dim. 3. sparse mask keeps k.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pb_multihead_sparsity_real_keys_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; HEADS = [1, 2, 4]; SPARSE_FRAC = 0.20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_ENC = 800; M_GRID = [20, 50, 100, 200, 400]
else:
    N_ENC = 4000; M_GRID = [40, 100, 200, 400, 700, 1000, 1400, 1900, 2500]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def sparsify(W, frac):
    k = max(1, int(frac * W.shape[1])); out = np.zeros_like(W)
    idx = np.argpartition(-np.abs(W), k - 1, axis=1)[:, :k]
    np.put_along_axis(out, idx, np.take_along_axis(W, idx, axis=1), axis=1); return out


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); return (P.T @ np.linalg.solve(G, P)).astype(np.float32)


def recall(P, seed):
    W = W_pinv(P); np.fill_diagonal(W, 0.0); g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(8):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return np.all(s == P, axis=1)


def capacity(keys, n_heads, seed):
    # multi-head = split the load across n_heads independent pinv heads; recall = each pattern by its own head
    c = 0
    for M in M_GRID:
        if M > keys.shape[0]:
            break
        P = keys[:M]; ok = np.zeros(M, bool)
        for h in range(n_heads):
            idx = np.arange(h, M, n_heads)
            if len(idx) == 0:
                continue
            ok[idx] = recall(P[idx], seed * 100 + M * 10 + h)
        if ok.mean() >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = (g.integers(0, 2, (20, 128)) * 2 - 1).astype(np.float32)
    W = W_pinv(P); assert np.allclose(W @ W, W, atol=1e-2), "pinv projector"
    assert whiten_fit(g.standard_normal((40, 16))).shape == (40, 16), "whiten preserves dim"
    sp = sparsify(g.standard_normal((5, 100)), 0.2); assert (np.abs(sp) > 0).sum(1).max() <= 20, "sparse keeps k"
    print("[selftest] PASS: multihead-sparse-real", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def signkeys(emb, sparse):
    W = whiten_fit(emb)
    if sparse:
        W = sparsify(W, SPARSE_FRAC)
    s = np.sign(W).astype(np.float32); s[s == 0] = 1.0; return s


def run() -> Dict:
    emb = encode(load_texts(N_ENC)); res = {}
    for sparse in [False, True]:
        keys = signkeys(emb, sparse)
        for H in HEADS:
            cap = capacity(keys, H, 7); res["%s_H%d" % ("sparse" if sparse else "dense", H)] = cap
            print("  [%s H=%d] capacity=%d" % ("sparse" if sparse else "dense", H, cap), flush=True)
    res["D"] = int(emb.shape[1]); return res


def verdict(r) -> Tuple[str, str]:
    d1 = r["dense_H1"]; d4 = r["dense_H4"]; s1 = r["sparse_H1"]
    head_gain = d4 / max(d1, 1e-9); sparse_gain = s1 / max(d1, 1e-9)
    summary = "dense: H1=%d H2=%d H4=%d | sparse: H1=%d H2=%d H4=%d | 4head/1head=%.2fx sparse/dense=%.2fx (D=%d)" % (
        r["dense_H1"], r["dense_H2"], r["dense_H4"], r["sparse_H1"], r["sparse_H2"], r["sparse_H4"], head_gain, sparse_gain, r["D"])
    if head_gain >= 3.0 and sparse_gain >= 1.0:
        return ("HARD_PASS", "HARD_PASS: BOTH levers transfer to real keys -- multi-head ~Hx and sparsity >= dense. " + summary)
    if head_gain >= 2.0 or sparse_gain > 1.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one lever transfers to real keys. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: neither lever transfers (real-key correlation kills the compound). " + summary)


print("[config] anchor=%s mode=%s encoder=%s N_enc=%d heads=%s" % (ANCHOR_NAME, RUN_MODE, ENCODER, N_ENC, HEADS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
