"""
exp_substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1 -- Slot DAMB1 (HIGHEST PRIORITY gating) -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot DAMB1. Disambiguates WHY real-encoder orthogonalization lift attenuates with N:
  H1 (N-dependent encoder noise) -> Q_real/Q_synthetic decays SUB-linearly with N; H2 (Hadamard N-saturation) -> LINEAR.
  Sweeps N_sub; at each N: M_50 capacity for REAL whitened MiniLM keys (Q_real) vs SYNTHETIC Hadamard (Q_synthetic).
  Ratio curve shape picks the hypothesis. Routes ALL real-encoder rescue investment. M_50 key-collision metric, torch GPU.

PRE-REGISTERED: H2 if ratio decays ~linearly (slope <= -0.10 per log2 N); H1 if sub-linear (-0.10..-0.02); flat = neither.
FORMULA SELF-TESTS (PROT-022): 1. recall helper. 2. hadamard orthogonal. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN.
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
from experiments._gpu_cap import recall_unique_t

ANCHOR_NAME = "substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; LOADS = [0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 4000; N_GRID = [512, 1024]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; N_GRID = [512, 1024, 2048, 4096]


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def expand(emb, D, g):
    R = g.standard_normal((emb.shape[1], D)).astype(np.float32) / np.sqrt(emb.shape[1]); return np.sign(emb @ R).astype(np.float32)


def whiten(K):
    mu = K.mean(0); X = K - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False)
    W = (X @ (Vt.T / (S + 1e-6))); return (W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def syn_hadamard(M, n, g):
    H = hadamard(n); idx = g.choice(n, min(M, n), replace=False); P = H[idx]
    if M > n:
        P = np.vstack([P, (g.integers(0, 2, (M - n, n)) * 2 - 1).astype(np.float32)])
    return (P / np.sqrt(n)).astype(np.float32)


def fixed_load_recall(keyfn, maxM, n, seed):
    # Option (b): RAW recall at fixed load M = 2*N (no M-search -> never censors to 1.0=1.0)
    M = min(6 * n, maxM)
    return recall_unique_t(keyfn(M), n, seed * 7 + M, flip=FLIP)


def _selftest():
    g = np.random.default_rng(0); H = hadamard(8); G = H @ H.T; assert np.allclose(G - np.diag(np.diag(G)), 0), "hadamard orthogonal"
    K = g.standard_normal((30, 64)).astype(np.float32); K = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)
    assert recall_unique_t(K, 64, 1, flip=0.0) >= 0.9, "recall helper"
    print("[selftest] PASS: damb1", flush=True)


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
    emb = encode(load_texts(N_ENC)); by_N = {}
    for n in N_GRID:
        real_fn = lambda M, n=n: whiten(expand(emb[np.random.default_rng(seed * 1000 + M).choice(emb.shape[0], M, replace=False)], n, np.random.default_rng(seed * 31 + n)))
        syn_fn = lambda M, n=n: syn_hadamard(M, n, np.random.default_rng(seed * 17 + M))
        qr = fixed_load_recall(real_fn, emb.shape[0], n, seed); qs = fixed_load_recall(syn_fn, 10 * n, n, seed)
        by_N["N%d" % n] = {"real_recall": qr, "synth_recall": qs, "ratio": float(qr / max(qs, 1e-6))}
        print("    [seed=%d N=%d M=6N] real_recall=%.3f synth_recall=%.3f ratio=%.3f" % (seed, n, qr, qs, qr / max(qs, 1e-6)), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    ns = N_GRID; rat = [float(np.mean([p["by_N"]["N%d" % n]["ratio"] for p in ps])) for n in ns]
    slope = float(np.polyfit(np.log2(ns), rat, 1)[0]) if len(ns) > 1 else 0.0
    summary = "Q_real/Q_synth by N=%s: %s | slope/log2N=%.3f" % (ns, [round(r, 3) for r in rat], slope)
    if slope <= -0.10:
        return ("HARD_PASS", "HARD_PASS(H2): ratio decays ~LINEARLY with N -- Hadamard N-saturation; partial pre-structure dominates at large N. " + summary)
    if slope < -0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND(H1-leaning): ratio decays SUB-linearly -- N-dependent encoder noise. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ratio ~flat -- real tracks synthetic; no attenuation in this range. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    ps.append(run_seed(seed))
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
