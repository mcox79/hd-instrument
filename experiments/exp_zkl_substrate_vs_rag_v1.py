"""
exp_zkl_substrate_vs_rag_v1 -- SZA protocol anchor 1 (substrate vs RAG baseline ZKL @k=50) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_chain1_drill2_SZA_protocol (#1). Comparative membership leakage: SUBSTRATE
  (ZCA-whiten + SIGN quantization) vs a simulated RAG baseline (raw float cosine, no quantization) under the same paraphrase
  attack at k=50. Quantifies the predicted "substrate ~64%% leakage of RAG" from the sign-quantization 2/pi factor. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS ZKL_substrate/ZKL_rag <= 0.70 (substrate leaks >=30%% less). MID 0.70-0.90.
  HARD-FAIL > 1.0 (substrate does NOT leak less; advantage gone).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. TPR@FPR monotone. 3. sign quantization bounded.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "zkl_substrate_vs_rag_v1"
N = 768; PARA_NOISE = 0.35; FPR = 0.01; K = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 60
else:
    N_KB = 3000; N_TGT = 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def stat_sign(targets, kb_sign, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
    return np.array(out)


def stat_raw(targets, kb, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        out.append(float((paras @ kb.T).max(axis=1).mean()))
    return np.array(out)


def _selftest():
    g = np.random.default_rng(0); W, mu, Wd = whiten_fit(g.standard_normal((40, 16))); assert W.shape == (40, 16), "whiten preserves dim"
    assert tpr_at_fpr(np.array([5.0, 6, 7]), np.array([0.0, 1, 2]), 0.01) >= 0.9, "TPR@FPR monotone"
    assert set(np.unique(np.sign(g.standard_normal(50)))) <= {-1.0, 0.0, 1.0}, "sign quantization bounded"
    print("[selftest] PASS: zkl-vs-rag", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); raw = g.standard_normal((N_KB + N_TGT, N)).astype(np.float32)
    Wkb, mu, Wd = whiten_fit(raw[:N_KB]); kb_w = unit(Wkb)
    kb_sign = np.sign(kb_w).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
    sel = g.choice(N_KB, N_TGT, replace=False)
    mem = unit((raw[sel] - mu) @ Wd); non = unit((raw[N_KB:N_KB + N_TGT] - mu) @ Wd)
    sub = tpr_at_fpr(stat_sign(mem, kb_sign, K, np.random.default_rng(100)), stat_sign(non, kb_sign, K, np.random.default_rng(200)), FPR)
    rag = tpr_at_fpr(stat_raw(mem, kb_w, K, np.random.default_rng(300)), stat_raw(non, kb_w, K, np.random.default_rng(400)), FPR)
    print("  ZKL_substrate=%.4f ZKL_rag=%.4f ratio=%.3f" % (sub, rag, sub / max(rag, 1e-9)), flush=True)
    return {"zkl_substrate": float(sub), "zkl_rag": float(rag), "ratio": float(sub / max(rag, 1e-9))}


def verdict(r) -> Tuple[str, str]:
    ratio = r["ratio"]; summary = "ZKL_substrate=%.4f ZKL_rag=%.4f substrate/rag=%.3f (k=%d)" % (r["zkl_substrate"], r["zkl_rag"], ratio, K)
    if ratio <= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate leaks <=70%% of RAG (sign-quantization 2/pi factor) -- quantitative privacy advantage vs incumbent. " + summary)
    if ratio <= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate/rag in [0.70,0.90] (qualify). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate does NOT leak meaningfully less than RAG -- commercial privacy advantage gone. " + summary)


print("[config] anchor=%s mode=%s N=%d n_kb=%d n_tgt=%d k=%d" % (ANCHOR_NAME, RUN_MODE, N, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
