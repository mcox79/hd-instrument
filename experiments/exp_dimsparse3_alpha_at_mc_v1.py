"""
exp_dimsparse3_alpha_at_mc_v1 -- Batch B: 4-arm capacity rescue on real keys at M near M_c -- CPU.

ROUTING: Research Batch B. The earlier DIMSPARSE tested at M=50 (far above M_c) -> sparse-VALUES gave 0 gain (key-collision
  limited). This re-tests at M NEAR the critical load M_c with the CORRECTED metric: Hopfield exact-recovery on
  ZCA-whitened (fit-on-full) SIGN-binarized real keys. 4 arms: baseline / dim-expansion(x2) / sparse-KEY(top-k) /
  compound. Question: does any rescue raise M_c on real encoder keys? (d_eff caps the ceiling; expect weak per d_eff=82
  framework, but tested honestly at the right operating point.)
PRE-REGISTERED: HARD-PASS a rescue arm raises M_c >= 1.5x baseline. MID 1.2-1.5x. HARD-FAIL all <=1.2x (key-collision /
  rank-limited; confirms d_eff ceiling).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. Hopfield recovers low load. 3. deps.
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

ANCHOR_NAME = "dimsparse3_alpha_at_mc_v1"
ENCODER = "EleutherAI/pythia-160m"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 800; LOADS = [2, 4, 8, 16, 32]
else:
    SEEDS = [7, 17, 23]; N_ENC = 4000; LOADS = [2, 4, 8, 12, 16, 24, 32, 48, 64, 96]
ARMS = ["baseline", "dim_expand_x2", "sparse_key", "compound"]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K.mean(0), Wd


def hop_recall_sign(Kw, seed):
    g = np.random.default_rng(seed); P = np.sign(Kw).astype(np.float32); P[P == 0] = 1.0; M, n = P.shape
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0)
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((100, 64)); Kw, _, _ = whiten_fit(K); assert Kw.shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall_sign(P, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: dimsparse3", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
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
    tok = AutoTokenizer.from_pretrained(ENCODER); tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(ENCODER, output_hidden_states=True).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            h = m(**t).hidden_states[-1][:, -1, :]                     # last-token pool (causal LM)
        out.append(h.cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def arm_transform(K, arm, seed):
    g = np.random.default_rng(seed + 5)
    if arm == "dim_expand_x2" or arm == "compound":
        R = g.standard_normal((K.shape[1], K.shape[1] * 2)).astype(np.float32) / np.sqrt(K.shape[1]); K = K @ R
    if arm == "sparse_key" or arm == "compound":
        thr = np.quantile(np.abs(K), 0.8, axis=1, keepdims=True); K = np.where(np.abs(K) >= thr, K, 0.0)  # top-20% keys
    return K


def cap_arm(Kfull, arm, seed):
    Kt = arm_transform(Kfull, arm, seed); Kw, _, _ = whiten_fit(Kt); c = 0
    for M in LOADS:
        if M > Kw.shape[0]:
            break
        if hop_recall_sign(Kw[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def run_seed(seed, Kfull) -> Dict:
    caps = {arm: cap_arm(Kfull, arm, seed) for arm in ARMS}
    print("  [seed=%d] M_c by arm: %s" % (seed, caps), flush=True); return {"seed": seed, "Mc": caps}


def verdict(ps) -> Tuple[str, str]:
    agg = {arm: float(np.mean([p["Mc"][arm] for p in ps])) for arm in ARMS}
    base = max(agg["baseline"], 1e-6); best_rescue = max(agg["dim_expand_x2"], agg["sparse_key"], agg["compound"]); g = best_rescue / base
    summary = "M_c by arm: %s | best_rescue/baseline=%.2fx" % ({k: round(v, 1) for k, v in agg.items()}, g)
    if g >= 1.5:
        return ("HARD_PASS", "HARD_PASS: a rescue raises M_c >=1.5x on real keys at M_c -- capacity lever on real encoder. " + summary)
    if g >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: rescue 1.2-1.5x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no rescue >1.2x -- real-key capacity rank/collision-limited (confirms d_eff ceiling). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d arms=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, ARMS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); Kfull = encode(load_texts(N_ENC)); print("[encoded] %s" % (Kfull.shape,), flush=True)
ps = [run_seed(s, Kfull) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
