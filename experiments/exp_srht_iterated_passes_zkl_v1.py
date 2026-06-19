"""
exp_srht_iterated_passes_zkl_v1 -- SRHT option 1 (iterated passes) self-decided follow-up -- CPU.

ROUTING: follows srht_realkey_zkl_fix_v3 (single SRHT = 1.74x, ZKL 0.41->0.24, short of HIPAA <=0.10). Tests whether
  ITERATING SRHT (independent random-sign-Hadamard mixing applied P times before storage) stacks toward <=0.10. Uses the
  validated cycle-150 sign-grounding LiRA attack. Sweeps P in {0,1,2,3}. Cheap decisive answer to "does iterated SRHT reach
  the HIPAA target" -- run it rather than wait. MiniLM proxy. CPU.
PRE-REGISTERED: HARD-PASS some P reaches ZKL(50) <= 0.10. MIDDLE monotone decrease but min > 0.10. HARD-FAIL no further gain
  past P=1 (iteration does not stack).
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. iterated srht preserves norm. 3. tpr@fpr monotone.
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

ANCHOR_NAME = "srht_iterated_passes_zkl_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50; PASSES = [0, 1, 2, 3]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 80
else:
    N_KB = 2000; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H / np.sqrt(H.shape[0])


def srht_iter(X, passes, g):
    n = X.shape[1]; m = 1
    while m < n:
        m *= 2
    Xp = np.zeros((X.shape[0], m), np.float32); Xp[:, :n] = X; H = hadamard(m)
    for _ in range(passes):
        D = (g.integers(0, 2, m) * 2 - 1).astype(np.float32); Xp = (Xp * D[None, :]) @ H.T   # independent mix each pass
    return Xp


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def stat_sign(targets, kb_sign, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
    return np.array(out)


def _selftest():
    H = hadamard(8); assert np.allclose(H @ H.T, np.eye(8), atol=1e-5), "hadamard orthogonal"
    g = np.random.default_rng(0); X = g.standard_normal((4, 6)).astype(np.float32); Y = srht_iter(X, 2, g)
    assert abs(np.linalg.norm(Y[0]) - np.linalg.norm(np.r_[X[0], np.zeros(2)])) < 1e-3, "iterated srht preserves norm"
    assert tpr_at_fpr(np.array([5.0, 6]), np.array([0.0, 1]), 0.01) >= 0.9, "tpr@fpr monotone"
    print("[selftest] PASS: srht-iterated", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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
    return np.concatenate(out, 0).astype(np.float32)


def zkl50(keys_raw, sel, g):
    Wkb, mu, Wd = whiten_fit(keys_raw[:N_KB]); kb_sign = np.sign(unit(Wkb)).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
    mem = unit((keys_raw[sel] - mu) @ Wd); non = unit((keys_raw[N_KB:N_KB + N_TGT] - mu) @ Wd)
    return tpr_at_fpr(stat_sign(mem, kb_sign, K, np.random.default_rng(1)), stat_sign(non, kb_sign, K, np.random.default_rng(2)), FPR)


def run() -> Dict:
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False); by = {}
    for p in PASSES:
        keys = real if p == 0 else srht_iter(real, p, np.random.default_rng(10 + p))
        by["P%d" % p] = zkl50(keys, sel, g); print("  [SRHT passes=%d] ZKL(50)=%.4f" % (p, by["P%d" % p]), flush=True)
    return {"by_passes": by}


def verdict(r) -> Tuple[str, str]:
    vals = [r["by_passes"]["P%d" % p] for p in PASSES]; mn = min(vals); best_p = PASSES[int(np.argmin(vals))]
    summary = "ZKL(50) by SRHT passes: %s | min=%.4f at P=%d (HIPAA<=0.10)" % ({("P%d" % p): round(r["by_passes"]["P%d" % p], 4) for p in PASSES}, mn, best_p)
    if mn <= 0.10:
        return ("HARD_PASS", "HARD_PASS: iterated SRHT reaches ZKL(50)<=0.10 at P=%d -- HIPAA target achievable by stacking SRHT passes. " % best_p + summary)
    if vals[-1] < vals[1]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: iteration keeps reducing ZKL but min %.4f still >0.10 -- more passes or SRHT+whiten needed. " % mn + summary)
    return ("HARD_FAIL", "HARD_FAIL: iteration does not stack past P=1 -- SRHT saturates; need a different mechanism for HIPAA target. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d passes=%s device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, PASSES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
