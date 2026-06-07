"""
exp_pb_neg_whiten_pinv_recipe_v1 -- propose-back (does the production recipe help negation/contradiction) -- CPU.

ROUTING: Exp-Dev propose-back. KF-1 negation/contradiction was historically weak (needs NLI). Open question: does the
  converged recipe (ZCA-whiten on real keys) sharpen contradiction discrimination vs raw cosine? Synthetic model: facts as
  bipolar vectors; a CONTRADICTION = a fact with one key attribute flipped (opposite polarity) but most context shared.
  Measures AUC of distinguishing entailed vs contradicting claims under raw vs whitened representations. CPU $0.
PRE-REGISTERED: HARD-PASS whitened contradiction-AUC >= raw + 0.05 (recipe sharpens negation). MID within +-0.05.
  HARD-FAIL whitened worse (whitening hurts contradiction).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. AUC bounds. 3. contradiction differs from entailment.
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

ANCHOR_NAME = "pb_neg_whiten_pinv_recipe_v1"
N = 2048; K_ATTR = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 400; N_Q = 150
else:
    SEEDS = [7, 17, 23]; N_KB = 2000; N_Q = 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))); return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((40, 16)); assert whiten_fit(K).shape == (40, 16), "whiten preserves dim"
    assert auc([1, 1], [0, 0]) == 1.0, "AUC bounds"
    print("[selftest] PASS: neg-recipe", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    attrs = unit(g.standard_normal((K_ATTR, N)).astype(np.float32))      # attribute basis
    # facts = sum of +-attr_j; contradiction = same fact with attr_0 polarity flipped
    signs = (g.integers(0, 2, (N_KB, K_ATTR)) * 2 - 1).astype(np.float32)
    facts = unit(signs @ attrs)
    q_idx = g.choice(N_KB, N_Q, replace=False)
    entail = facts[q_idx]                                                 # same fact (entailed)
    contra_signs = signs[q_idx].copy(); contra_signs[:, 0] *= -1; contra = unit(contra_signs @ attrs)  # one attr flipped
    def disc(rep_facts, rep_q):
        # contradiction score = how UNLIKE the query is to its matching fact (lower sim = contradiction)
        return -(rep_q * rep_facts[q_idx]).sum(1)
    raw_auc = auc(disc(facts, contra), disc(facts, entail))               # contra should score higher (less similar)
    Wf = whiten_fit(facts); we = whiten_fit(np.vstack([facts, entail, contra]))
    fW = we[:N_KB]; eW = we[N_KB:N_KB + N_Q]; cW = we[N_KB + N_Q:]
    wh_auc = auc(-(cW * fW[q_idx]).sum(1), -(eW * fW[q_idx]).sum(1))
    print("  [seed=%d] raw_contradiction_AUC=%.3f whitened_AUC=%.3f" % (seed, raw_auc, wh_auc), flush=True)
    return {"seed": seed, "raw_auc": raw_auc, "whitened_auc": wh_auc}


def verdict(ps) -> Tuple[str, str]:
    r = float(np.mean([p["raw_auc"] for p in ps])); w = float(np.mean([p["whitened_auc"] for p in ps]))
    summary = "raw_contradiction_AUC=%.3f whitened_AUC=%.3f delta=%+.3f" % (r, w, w - r)
    if w >= r + 0.05:
        return ("HARD_PASS", "HARD_PASS: ZCA-whitening sharpens contradiction discrimination (+0.05 AUC) -- recipe helps negation. " + summary)
    if w >= r - 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: whitening neutral for contradiction (within +-0.05). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: whitening hurts contradiction discrimination. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d k_attr=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, K_ATTR), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
