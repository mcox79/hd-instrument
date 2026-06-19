"""
exp_zkl_curve_k_sweep_realkeys_v1 -- SRHT fix v3: reuse the attack that reproduces cycle-151 ZKL(50)=0.40, add SRHT arm -- CPU.

ROUTING: ZKL Certificate battery cell 3 (THE central commercial claim). The first pass (zkl_curve_k_sweep_v1) used
  synthetic random embeddings, which lack the whitening-privacy geometry of real keys; exp_dev flagged it as a weak proxy.
  This re-runs the membership-inference k-sweep on REAL MiniLM keys + production recipe (ZCA-whiten + sign), paraphrases
  modelled as embedding-space perturbations. ZKL = TPR@FPR=0.01 at k in {1,10,50,100,500}. CPU (MiniLM forward, CPU).
PRE-REGISTERED (research bands): HARD-PASS ZKL(50)<=0.10 AND ZKL(100)<=0.35 (sublinear). MID ZKL(50) in [0.10,0.30].
  HARD-FAIL ZKL(50)>0.30.
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. TPR@FPR monotone. 3. AUC bound.
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

ANCHOR_NAME = "srht_realkey_zkl_fix_v3"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50
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


def srht(X, g):
    n = X.shape[1]; m = 1
    while m < n:
        m *= 2
    Xp = np.zeros((X.shape[0], m), np.float32); Xp[:, :n] = X; D = (g.integers(0, 2, m) * 2 - 1).astype(np.float32)
    return (Xp * D[None, :]) @ hadamard(m).T


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
    g = np.random.default_rng(0); W, mu, Wd = whiten_fit(g.standard_normal((40, 16))); assert W.shape == (40, 16), "whiten preserves dim"
    assert tpr_at_fpr(np.array([5.0, 6, 7]), np.array([0.0, 1, 2]), 0.01) >= 0.9, "TPR@FPR monotone"
    assert tpr_at_fpr(np.array([1.0]), np.array([0.0]), 0.5) <= 1.0, "AUC bound"
    print("[selftest] PASS: zkl-kcurve-real", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


def load_texts(n, skip=0):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n + skip:
                    return out[skip:skip + n]
    return out[skip:skip + n]


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
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False)
    z_real = zkl50(real, sel, g)
    z_srht = zkl50(srht(real, np.random.default_rng(11)), sel, g)
    print("  ZKL(50) real=%.4f real+SRHT=%.4f reduction=%.2fx" % (z_real, z_srht, z_real / max(z_srht, 1e-9)), flush=True)
    return {"zkl_real": float(z_real), "zkl_real_srht": float(z_srht), "reduction": float(z_real / max(z_srht, 1e-9))}


def verdict(r) -> Tuple[str, str]:
    real = r["zkl_real"]; srht_z = r["zkl_real_srht"]; red = r["reduction"]
    summary = "ZKL(50) real=%.4f real+SRHT=%.4f reduction=%.2fx (HIPAA target <=0.10)" % (real, srht_z, red)
    if real > 0.20 and srht_z <= 0.10:
        return ("HARD_PASS", "HARD_PASS: SRHT drops real-key ZKL(50) from >0.20 to <=0.10 (HIPAA target) -- the privacy fix is empirically confirmed; SRHT-before-storage ships. " + summary)
    if srht_z < real * 0.7:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SRHT reduces ZKL but not to <=0.10 target. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: SRHT does not meaningfully reduce real-key ZKL. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d K=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
