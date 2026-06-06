"""
exp_substrate_pca_prewhitening_codebook_v1 -- SSOT DAMB4 (cheap universal real-encoder rescue) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot DAMB4 (drill A Cell 4). Apply PCA whitening to encoder output BEFORE sign-projection;
  measure Hopfield exact-recovery capacity vs UNWHITENED Hadamard-sign at N=384 on real MiniLM keys. Attacks BOTH H1
  (anisotropy) and H2 (isotropic-ization makes Hadamard near-optimal). Independent of DAMB1. If HP -> ships as one-line
  offline-PCA + O(d^2) per-query preprocessing; multiplicative improvement across ALL downstream real-encoder experiments.
PRE-REGISTERED: HARD-PASS PCA-whitened-sign capacity >= 2x unwhitened-sign at N=384 real keys. MID 1.2-2x. HF <1.2x.
FORMULA SELF-TESTS (PROT-022): 1. PCA whiten decorrelates. 2. Hopfield recovers low load. 3. deps.
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

ANCHOR_NAME = "substrate_pca_prewhitening_codebook_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6; N = 384
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1500; LOADS = [0.01, 0.03, 0.06, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 5000; LOADS = [0.005, 0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]


def pca_whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def cap(signed_keys, seed):
    c = 0
    for load in LOADS:
        M = max(2, int(load * N))
        if M > signed_keys.shape[0]:
            break
        if hop_recall(signed_keys[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((200, 64)) @ g.standard_normal((64, 64))  # correlated
    W = pca_whiten_fit(K); cov = (W - W.mean(0)).T @ (W - W.mean(0)) / 200
    assert (cov - np.diag(np.diag(cov))).std() < 0.2, "PCA whiten decorrelates"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: pca-prewhiten", flush=True)


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
            o = m(**t); h = o.last_hidden_state; mask = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, emb) -> Dict:
    raw = np.sign(emb).astype(np.float32); raw[raw == 0] = 1.0       # unwhitened Hadamard-sign (raw)
    pw = np.sign(pca_whiten_fit(emb)).astype(np.float32); pw[pw == 0] = 1.0  # PCA-whitened then sign
    c_raw = cap(raw, seed); c_pca = cap(pw, seed)
    print("  [seed=%d] cap_unwhitened=%d cap_pca_whitened=%d" % (seed, c_raw, c_pca), flush=True)
    return {"seed": seed, "cap_unwhitened": c_raw, "cap_pca_whitened": c_pca, "ratio": c_pca / max(c_raw, 1e-9)}


def verdict(ps) -> Tuple[str, str]:
    cr = float(np.mean([p["cap_unwhitened"] for p in ps])); cp = float(np.mean([p["cap_pca_whitened"] for p in ps])); g = cp / max(cr, 1e-9)
    summary = "cap unwhitened=%.1f pca_whitened=%.1f | ratio=%.2fx (N=%d real MiniLM keys)" % (cr, cp, g, N)
    if g >= 2.0:
        return ("HARD_PASS", "HARD_PASS: PCA-prewhitening >=2x unwhitened capacity -- ships as one-line universal real-encoder rescue. " + summary)
    if g >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: PCA-prewhitening 1.2-2x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: PCA-prewhitening <1.2x (no real-encoder rescue). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
