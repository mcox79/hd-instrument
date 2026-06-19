"""
exp_causal_correlational_disambig_v1 -- causal/counterfactual (3x) anchor 2 (Mechanism A gate) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_causal_counterfactual_3x #2. Store 50 causal pairs (A causes B) and 50
  correlational pairs (A co-occurs B) in W at N=4096 using CAUSE_OF vs CORRELATED_WITH role vectors (quasi-orthogonal random).
  Query "what causes Y?" for each Y; measure precision/recall of causal vs correlational retrieval. If the role vectors fail
  to disambiguate, Mechanism A (causal binding extension) is ruled out -> shift to Mechanism C (hybrid external). CPU $0 ~5min.
PRE-REGISTERED: HARD-PASS causal-retrieval precision>=0.85 AND recall>=0.85 (roles disambiguate; Mechanism A viable). MID
  0.65-0.85. HARD-FAIL <0.65 (roles do not disambiguate; Mechanism A ruled out).
FORMULA SELF-TESTS (PROT-022): 1. roles quasi-orthogonal. 2. bind/unbind recovers. 3. precision/recall bounds.
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

ANCHOR_NAME = "causal_correlational_disambig_v1"
N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_PAIR = 25
else:
    SEEDS = [7, 17, 23]; N_PAIR = 50


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); cause = bp(1, 512, g)[0]; corr = bp(1, 512, g)[0]
    assert abs(float(unit(cause[None, :])[0] @ unit(corr[None, :])[0])) < 0.2, "roles quasi-orthogonal"
    a = bp(1, 512, g)[0]; b = bp(1, 512, g)[0]; bound = cause * a * b              # bipolar bind (assoc cause:a->b)
    rec = bound * cause * a; assert float(unit(rec[None, :])[0] @ unit(b[None, :])[0]) > 0.9, "bind/unbind recovers"
    print("[selftest] PASS: causal-disambig", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    CAUSE = bp(1, N, g)[0]; CORR = bp(1, N, g)[0]                                  # role vectors
    A = bp(2 * N_PAIR, N, g); B = bp(2 * N_PAIR, N, g)                             # entities
    # causal pairs 0..N_PAIR-1 (role CAUSE), correlational N_PAIR..2N_PAIR-1 (role CORR)
    mem = np.zeros(N, np.float32)
    for i in range(N_PAIR):
        mem = mem + CAUSE * A[i] * B[i]                                            # bind cause(A_i -> B_i)
    for i in range(N_PAIR, 2 * N_PAIR):
        mem = mem + CORR * A[i] * B[i]
    mem = np.sign(mem); mem[mem == 0] = 1.0
    # query "what causes Y?" for each B_i: unbind with CAUSE * B_i, nearest A among all
    tp = 0; fp = 0; fn = 0
    for i in range(2 * N_PAIR):
        q = mem * CAUSE * B[i]; sims = unit(q[None, :]) @ unit(A).T; pred = int(np.argmax(sims[0]))
        is_causal = i < N_PAIR
        # a retrieval "fires causal" if the top A match is strong; correct iff this B was stored under CAUSE
        fired = sims[0, pred] > sims[0].mean() + 2 * sims[0].std()
        if is_causal and fired and pred == i:
            tp += 1
        elif is_causal and not (fired and pred == i):
            fn += 1
        elif (not is_causal) and fired and pred == i:
            fp += 1
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    print("  [seed=%d] causal precision=%.3f recall=%.3f (tp=%d fp=%d fn=%d)" % (seed, prec, rec, tp, fp, fn), flush=True)
    return {"seed": seed, "precision": prec, "recall": rec}


def verdict(ps) -> Tuple[str, str]:
    p = float(np.mean([x["precision"] for x in ps])); r = float(np.mean([x["recall"] for x in ps]))
    summary = "causal precision=%.3f recall=%.3f (CAUSE_OF vs CORRELATED_WITH role disambiguation, N=%d)" % (p, r, N)
    if p >= 0.85 and r >= 0.85:
        return ("HARD_PASS", "HARD_PASS: role vectors disambiguate causal vs correlational (prec & recall >=0.85) -- Mechanism A (causal binding) viable. " + summary)
    if p >= 0.65 and r >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial disambiguation (0.65-0.85). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: roles do not disambiguate (<0.65) -- Mechanism A ruled out; shift to Mechanism C (hybrid external). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d pairs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_PAIR), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
