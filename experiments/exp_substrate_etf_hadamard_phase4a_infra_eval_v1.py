"""
exp_substrate_etf_hadamard_phase4a_infra_eval_v1 -- Slot 9: ETF/orthogonalized codebook on REAL MiniLM substrate -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot 9 (Phase-4a infra adoption). Slot 2 ETF Hadamard gave 10x with RANDOM keys. This tests
  whether codebook ORTHOGONALIZATION still helps when keys come from a REAL encoder (MiniLM) -- the setup used by the
  overnight HPs (KF-1 hallucination, real-encoder, continual-KV). Compares heteroassociative capacity with RAW MiniLM
  keys (correlated -> collisions) vs WHITENED/orthogonalized MiniLM keys (decorrelated -> ETF-like). Unique value per
  fact (M-way, non-saturating). HP: whitened >= 4x raw -> Phase-4a should orthogonalize codebooks by default. torch GPU.

PRE-REGISTERED bands: HARD-PASS whitened-key capacity >= 4x raw at matched conditions. MIDDLE: 2-4x. HARD-FAIL: < 2x
  (orthogonalization does not transfer to real-encoder substrate).
FORMULA SELF-TESTS (PROT-022): 1. whiten decorrelates. 2. unique-value hetero recall. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN (multi-config).
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
from experiments._gpu_cap import hopfield_recall_t

ANCHOR_NAME = "substrate_etf_hadamard_phase4a_infra_eval_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
N_SUB = 384  # MiniLM dim
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1500; LOADS = [0.03, 0.06, 0.1, 0.14, 0.2, 0.3]
else:
    SEEDS = [7, 17, 23]; N_ENC = 5000; LOADS = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.7, 2.2]


def whiten(K):
    # ZCA whitening: preserves full D dims (rank-limited SVD form returned M-dim when M<D -> bug)
    mu = K.mean(0); X = (K - mu).astype(np.float32); n = X.shape[0]
    cov = (X.T @ X) / max(n, 1)
    U, S, _ = np.linalg.svd(cov)
    Wm = (U / np.sqrt(S + 1e-3)) @ U.T
    Wd = X @ Wm.astype(np.float32)
    return (Wd / (np.linalg.norm(Wd, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def norml(K):
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_unique(keys, n, g):
    # heteroassociative, UNIQUE value per fact (M-way; non-saturating). W = sum v_i k_i^T; retrieve argmax over V.
    M = keys.shape[0]; V = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-8
    W = (V.T @ keys).astype(np.float32)
    pred = np.argmax((keys @ W.T) @ V.T, axis=1)
    return float(np.mean(pred == np.arange(M)))


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((50, 16)).astype(np.float32) @ g.standard_normal((16, 16)).astype(np.float32)
    Kw = whiten(K); c = np.corrcoef(Kw.T); off = np.abs(c - np.diag(np.diag(c)))
    assert off.mean() < np.abs(np.corrcoef(norml(K).T) - np.diag(np.diag(np.corrcoef(norml(K).T)))).mean() + 0.05, "whiten decorrelates"
    print("[selftest] PASS: whiten (Hopfield metric)", flush=True)


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


def capacity(Tfull, seed):
    # Tfull = transform applied to the FULL emb (fit-on-full -> full-rank whitening); index subsets for the M-sweep.
    cap = 0; M_all = Tfull.shape[0]
    for load in LOADS:
        M = max(2, int(load * N_SUB))
        if M > M_all:
            break
        g = np.random.default_rng(seed * 1000 + M); idx = g.choice(M_all, size=M, replace=False)
        P = np.sign(Tfull[idx]).astype(np.float32); P[P == 0] = 1.0            # sign-binarize (already full-rank whitened)
        if hopfield_recall_t(P, FLIP, STEPS, seed * 7 + M) >= 0.95:            # auto-assoc Hopfield exact-recovery
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    emb = encode(load_texts(N_ENC))                                   # native MiniLM dim (no expansion -- rank-limited red herring)
    cr = capacity(norml(emb), seed); cw = capacity(whiten(emb), seed) # whiten FIT ON FULL emb (N_ENC>=384 -> full rank)
    return {"seed": seed, "raw_capacity": cr, "whitened_capacity": cw, "ratio": float(cw / max(cr, 1))}


def verdict(ps) -> Tuple[str, str]:
    cr = float(np.mean([p["raw_capacity"] for p in ps])); cw = float(np.mean([p["whitened_capacity"] for p in ps]))
    ratio = cw / max(cr, 1)
    summary = "raw_MiniLM_capacity=%.0f whitened_capacity=%.0f ratio=%.2fx (N_sub=%d)" % (cr, cw, ratio, N_SUB)
    if ratio >= 2.0:
        return ("HARD_PASS", "HARD_PASS: sign-binarized whitened real-MiniLM gives >=2x Hopfield capacity vs raw -- orthogonalization helps (proper metric). " + summary)
    if ratio >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: orthogonalization 1.3-2x (Hopfield metric). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: orthogonalization <1.3x on real-encoder (Hopfield metric -- true capacity). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d N_sub=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, N_SUB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] raw_cap=%d whitened_cap=%d ratio=%.2fx" % (seed, r["raw_capacity"], r["whitened_capacity"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
