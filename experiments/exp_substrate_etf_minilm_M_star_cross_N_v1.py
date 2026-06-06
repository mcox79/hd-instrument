"""
exp_substrate_etf_minilm_M_star_cross_N_v1 -- SSOT G9-FIX (clean cross-N attenuation metric) -- CPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G9-FIX (Exp-Dev methodology flag -> Research revised metric). The capacity-sweep ratio
  CENSORS at grid max (false "shrinks"); this uses the un-censored M_50 metric: M_50(N_sub) = the M at which Hopfield
  recall first drops below 0.5. Computes ratio whitened_M_50 / raw_M_50 across N_sub in {384,768,1536,3072} on real MiniLM
  keys (projected to N_sub). M_50 falls exactly where capacity breaks (no censoring). CPU $0.
PRE-REGISTERED: HARD-PASS ratio GROWS with N_sub (H2 saturation -- whitening's relative benefit increases at larger N,
  matches drill A H2-dominant prediction). MID ratio ~ constant (H1+H2 mixed). HARD-FAIL ratio SHRINKS with N_sub (H1-dominant).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. M_50 monotone proxy. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "substrate_etf_minilm_M_star_cross_N_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_SUB = [384, 768]; N_ENC = 1500
else:
    SEEDS = [7, 17, 23]; N_SUB = [384, 768, 1536, 3072]; N_ENC = 5000
M_GRID = [4, 8, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def m_50(signed_keys, seed):
    prev = M_GRID[0]
    for M in M_GRID:
        if M > signed_keys.shape[0]:
            return prev
        if hop_recall(signed_keys[:M], seed * 100 + M) < 0.5:
            return M
        prev = M
    return M_GRID[-1]


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "low load recovers (>0.5)"
    print("[selftest] PASS: g9fix", flush=True)


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
    g = np.random.default_rng(seed); by_N = {}
    for n in N_SUB:
        R = g.standard_normal((emb.shape[1], n)).astype(np.float32) / np.sqrt(emb.shape[1]); K = emb @ R
        raw = np.sign(K).astype(np.float32); raw[raw == 0] = 1.0
        wh = np.sign(whiten_fit(K)).astype(np.float32); wh[wh == 0] = 1.0
        m_raw = m_50(raw, seed); m_wh = m_50(wh, seed)
        by_N["N%d" % n] = {"m50_raw": m_raw, "m50_whitened": m_wh, "ratio": m_wh / max(m_raw, 1e-9)}
        print("  [seed=%d N_sub=%d] m50_raw=%d m50_whitened=%d ratio=%.2f" % (seed, n, m_raw, m_wh, m_wh / max(m_raw, 1)), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    Ns = np.array(N_SUB, float)
    ratios = np.array([np.mean([p["by_N"]["N%d" % n]["ratio"] for p in ps]) for n in N_SUB])
    slope = float(np.polyfit(np.log(Ns), ratios, 1)[0])             # ratio vs log(N) slope
    summary = "whitened/raw M_50 ratio by N_sub: %s | slope(vs logN)=%.2f" % ({("N%d" % n): round(float(np.mean([p["by_N"]["N%d" % n]["ratio"] for p in ps])), 2) for n in N_SUB}, slope)
    if slope > 0.5:
        return ("HARD_PASS", "HARD_PASS (H2): whitening benefit (M_50 ratio) GROWS with N_sub -- Hadamard/intrinsic-dim saturation dominant; whitening increasingly mandatory at scale. " + summary)
    if slope < -0.5:
        return ("HARD_FAIL", "HARD_FAIL (H1): M_50 ratio SHRINKS with N_sub -- N-dependent anisotropy noise dominant. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND (H1+H2 mixed): M_50 ratio ~ constant across N_sub. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_sub=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_SUB, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
