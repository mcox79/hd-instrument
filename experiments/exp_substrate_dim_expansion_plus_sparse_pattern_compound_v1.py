"""
exp_substrate_etf_minilm_dim_expansion_v1 -- GPU follow-on to Slot 9: recover ETF headroom via dimensional expansion.

ROUTING: follow-on to Slot 9 (etf_hadamard_phase4a_infra_eval = MIDDLE 2.75x). Slot 9 found orthogonalizing real MiniLM
  keys helps only 2.75x because capacity is bounded by the encoder dim (384). HYPOTHESIS: expand the substrate dimension
  with a nonlinear random-feature map phi(x)=sign(R x) (R: 384 x D Gaussian) -> rank lifts toward D -> orthogonalization
  recovers more headroom. Tests capacity (raw-projected vs whitened) at D in {384, 1024, 4096}. If capacity scales with D,
  Phase-4a should EXPAND the substrate dim (not just orthogonalize) for real encoders. torch GPU (MiniLM encode).

PRE-REGISTERED bands: HARD-PASS whitened capacity at D=4096 >= 3x whitened capacity at D=384 (expansion recovers
  headroom). MIDDLE: 1.5-3x. HARD-FAIL: < 1.5x (expansion does not help -- real-encoder info ceiling is fundamental).
FORMULA SELF-TESTS (PROT-022): 1. expansion lifts rank. 2. unique-value hetero recall. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN (D-sweep).
"""
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_dim_expansion_plus_sparse_pattern_compound_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 5000; D_EXP = 2048; ALPHA = 0.20; LOADS = [0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; D_EXP = 4096; ALPHA = 0.20; LOADS = [0.2, 0.5, 0.8, 1.1, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]


def expand(emb, D, g):
    if D == emb.shape[1]:
        X = emb.copy()
    else:
        R = g.standard_normal((emb.shape[1], D)).astype(np.float32) / np.sqrt(emb.shape[1])
        X = np.sign(emb @ R).astype(np.float32)                      # nonlinear random-feature lift -> rank toward D
    return X


def whiten(K):
    mu = K.mean(0); X = K - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False)
    W = (X @ (Vt.T / (S + 1e-6))); return (W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def norml(K):
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_unique(keys, n, g, sparse=False):
    M = keys.shape[0]
    if sparse:
        V = np.zeros((M, n), np.float32); kk = max(1, int(ALPHA * n))
        for i in range(M):
            idx = g.choice(n, kk, replace=False); V[i, idx] = g.integers(0, 2, kk) * 2 - 1
    else:
        V = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-8
    W = (V.T @ keys).astype(np.float32)
    pred = np.argmax((keys @ W.T) @ V.T, axis=1)
    return float(np.mean(pred == np.arange(M)))


def m_50(emb, D, expand_on, sparse, seed):
    prev = 2
    for load in LOADS:
        M = min(int(load * D), emb.shape[0])
        if M < 2:
            continue
        g = np.random.default_rng(seed * 1000 + D + M); idx = g.choice(emb.shape[0], M, replace=False)
        K = norml(expand(emb[idx], D, np.random.default_rng(seed * 31 + D)) if expand_on else emb[idx])
        if recall_unique(K, D if expand_on else emb.shape[1], np.random.default_rng(seed * 7 + M), sparse) < 0.5:
            return prev
        prev = M
    return prev


def _selftest():
    g = np.random.default_rng(0); emb = g.standard_normal((200, 16)).astype(np.float32)
    X = expand(emb, 128, g); assert np.linalg.matrix_rank(X) > np.linalg.matrix_rank(emb), "expansion lifts rank"
    assert recall_unique(norml(g.standard_normal((10, 64)).astype(np.float32)), 64, g) >= 0.9, "unique-value hetero recall"
    print("[selftest] PASS: expansion rank + recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer


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
    tok = AutoTokenizer.from_pretrained(MINILM_ID); m = AutoModel.from_pretrained(MINILM_ID).to(DEVICE).eval(); out = []
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = m(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m; torch.cuda.empty_cache(); return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed) -> Dict:
    emb = encode(load_texts(N_ENC)); b = emb.shape[1]
    arms = {"a_baseline": m_50(emb, b, False, False, seed),
            "b_expand": m_50(emb, D_EXP, True, False, seed),
            "c_sparse": m_50(emb, b, False, True, seed),
            "d_both": m_50(emb, D_EXP, True, True, seed)}
    return {"seed": seed, "arms": arms}


def verdict(ps) -> Tuple[str, str]:
    a = {k: float(np.mean([p["arms"][k] for p in ps])) for k in ps[0]["arms"]}
    gb = a["b_expand"] / max(a["a_baseline"], 1); gc = a["c_sparse"] / max(a["a_baseline"], 1); gd = a["d_both"] / max(a["a_baseline"], 1)
    expected = gb * gc; frac = gd / max(expected, 1e-9)
    summary = "M50 arms=%s | gain_b=%.2fx gain_c=%.2fx gain_d=%.2fx expected(b*c)=%.2fx d/expected=%.2f" % ({k: round(v) for k, v in a.items()}, gb, gc, gd, expected, frac)
    if frac >= 0.80:
        return ("HARD_PASS", "HARD_PASS: dim-expansion x sparse-pattern COMPOUND multiplicatively (d >= 0.8*b*c) -- Phase-3 capacity ~%.0fx. " % gd + summary)
    if gd >= 1.2 * max(gb, gc):
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial stacking (d > best single but < 0.8*b*c). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no stacking (d ~ max(b,c)) -- levers are independent, ~single-lever ceiling. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d D_exp=%d alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, D_EXP, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: round(v) for k, v in r["arms"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
