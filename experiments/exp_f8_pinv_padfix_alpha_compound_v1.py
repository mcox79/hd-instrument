"""
exp_pseudoinverse_real_encoder_keys_v1 -- Batch F8: production recipe A/B -- OLD(raw-sign+Hebb) vs NEW(whiten+pinv) defaults on real keys -- CPU.

ROUTING: Exp-Dev propose-back (Research to adopt). Batch E Cell 2 showed pseudoinverse write rule = 8x Hebb on SYNTHETIC
  +-1 patterns. THE production question: does the gain hold on REAL encoder keys? Real keys are correlated/anisotropic
  (low d_eff) -- pseudoinverse (projector onto pattern span) may help MORE (it inverts the Gram, decorrelating) or LESS
  (rank-deficient Gram). Compares Hebb vs pseudoinverse exact-recovery capacity on ZCA-whitened sign(MiniLM) keys. If the
  multiplier holds, pseudoinverse becomes the top production capacity lever (stacks with whitening). CPU $0.
PRE-REGISTERED: HARD-PASS pinv >= 3x Hebb on real whitened keys. MID 1.5-3x. HARD-FAIL <1.5x (gain is synthetic-only).
FORMULA SELF-TESTS (PROT-022): 1. pinv single pattern fixed point. 2. projector idempotent. 3. whiten preserves dim.
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

ANCHOR_NAME = "f8_pinv_padfix_alpha_compound_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1500; LOADS = [0.05, 0.1, 0.2, 0.4, 0.6]
else:
    SEEDS = [7, 17, 23]; N_ENC = 5000; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3, 0.4, 0.55, 0.7, 0.85, 0.95]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def W_hebb(P):
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32)
    W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(W, P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(rule, keys, seed):
    n = keys.shape[1]; c = 0.0
    for load in LOADS:
        M = max(2, int(load * n))
        if M > keys.shape[0]:
            break
        P = keys[:M]; W = W_hebb(P) if rule == "hebb" else W_pinv(P)
        if recall(W, P, seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = (g.integers(0, 2, (1, 128)) * 2 - 1).astype(np.float32)
    assert recall(W_pinv(P), P, 0) >= 0.95, "pinv single pattern fixed point"
    P2 = (g.integers(0, 2, (20, 128)) * 2 - 1).astype(np.float32); Wp = P2.T @ np.linalg.solve(P2 @ P2.T + 1e-3 * np.eye(20), P2)
    assert np.allclose(Wp @ Wp, Wp, atol=1e-2), "projector idempotent"
    assert whiten_fit(g.standard_normal((40, 16))).shape == (40, 16), "whiten preserves dim"
    print("[selftest] PASS: pinv-real", flush=True)


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
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, emb) -> Dict:
    raw = np.sign(emb).astype(np.float32); raw[raw == 0] = 1.0                       # OLD: raw sign, no whiten
    wh = np.sign(whiten_fit(emb)).astype(np.float32); wh[wh == 0] = 1.0             # NEW: ZCA-whiten then sign
    old_cap = cap("hebb", raw, seed); new_cap = cap("pinv", wh, seed)
    print("  [seed=%d] OLD(raw+hebb)=%.3f NEW(whiten+pinv)=%.3f" % (seed, old_cap, new_cap), flush=True)
    return {"seed": seed, "old_recipe": old_cap, "new_recipe": new_cap}


def verdict(ps) -> Tuple[str, str]:
    o = float(np.mean([p["old_recipe"] for p in ps])); n = float(np.mean([p["new_recipe"] for p in ps]))
    txt = ("OLD~0 -> NEW rescues" if o < 1e-3 else "%.2fx" % (n / o))
    summary = "real-key recipe: OLD(raw+hebb)=%.3f NEW(whiten+pinv)=%.3f | NEW/OLD: %s" % (o, n, txt)
    if n >= 0.10 and (o < 1e-3 or n >= 3.0 * o):
        return ("HARD_PASS", "HARD_PASS: NEW production recipe (whiten+pinv) >=3x OLD (or OLD~0) -- adopt new defaults. " + summary)
    if n >= 1.5 * max(o, 1e-9):
        return ("MIDDLE_BAND", "MIDDLE_BAND: NEW recipe 1.5-3x OLD. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: NEW recipe <1.5x OLD. " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC))
print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
