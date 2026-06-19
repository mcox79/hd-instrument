"""
exp_concept_drift_misragries_v1 -- concept-drift detection via Misra-Gries window comparison -- CPU.

ROUTING: concept_drift_detection Anchor 1. Validates that the L1 frequency distance D between Misra-Gries counter snapshots
  is sensitive to a moderate topic-distribution shift (the v1.1 drift-detection mechanism + a customer-facing alert frontier
  LLMs can't offer). Synthetic topic stream: baseline windows from P; drift window from P' (30% topic mass shifted to new
  topics). Compare D_baseline (P-vs-P) to D_drift (P-vs-P'). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS D_drift / D_baseline > 3.0 (drift clearly separable). MIDDLE 1.5-3.0. HARD-FAIL < 1.5 (mechanism
  needs larger K / finer epsilon).
FORMULA SELF-TESTS (PROT-022): 1. misra-gries finds heavy hitters. 2. L1 distance symmetric. 3. drift > baseline.
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

ANCHOR_NAME = "concept_drift_misragries_v1"; K_TOPICS = 200; MG_K = 64; SHIFT = 0.30
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
WINDOW = 2000 if RUN_MODE == "smoke" else 10000; TRIALS = 5 if RUN_MODE == "smoke" else 20


def zipf_probs(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()


def misra_gries(stream, k):
    cnt = {}
    for x in stream:
        if x in cnt:
            cnt[x] += 1
        elif len(cnt) < k:
            cnt[x] = 1
        else:
            for key in list(cnt):
                cnt[key] -= 1
                if cnt[key] == 0:
                    del cnt[key]
    return cnt


def mg_dist(stream, k, V):
    cnt = misra_gries(stream, k); v = np.zeros(V)
    for key, c in cnt.items():
        v[key] = c
    s = v.sum(); return v / s if s > 0 else v


def l1(a, b):
    return float(np.abs(a - b).sum())


def _selftest():
    s = [1] * 80 + [2] * 5 + [3] * 3; mg = misra_gries(s, 4); assert 1 in mg, "misra-gries finds heavy hitters"
    a = np.array([0.5, 0.5]); b = np.array([0.2, 0.8]); assert abs(l1(a, b) - l1(b, a)) < 1e-9, "L1 distance symmetric"
    assert l1(np.array([1.0, 0]), np.array([0, 1.0])) > l1(np.array([1.0, 0]), np.array([0.9, 0.1])), "drift > baseline"
    print("[selftest] PASS: concept-drift-misragries", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(202); P = zipf_probs(K_TOPICS)
    # P' = 30% mass shifted onto NEW topics (a fresh permutation's head)
    newperm = g.permutation(K_TOPICS); Pn = np.zeros(K_TOPICS); Pn[newperm] = zipf_probs(K_TOPICS)
    Pp = (1 - SHIFT) * P + SHIFT * Pn; Pp = Pp / Pp.sum()
    d_base = []; d_drift = []
    for _ in range(TRIALS):
        w0 = g.choice(K_TOPICS, size=WINDOW, p=P); w1 = g.choice(K_TOPICS, size=WINDOW, p=P); w2 = g.choice(K_TOPICS, size=WINDOW, p=Pp)
        v0 = mg_dist(w0, MG_K, K_TOPICS); v1 = mg_dist(w1, MG_K, K_TOPICS); v2 = mg_dist(w2, MG_K, K_TOPICS)
        d_base.append(l1(v0, v1)); d_drift.append(l1(v0, v2))
    db = float(np.mean(d_base)); dd = float(np.mean(d_drift)); ratio = dd / (db + 1e-9)
    print("  D_baseline=%.4f D_drift=%.4f ratio=%.2f (shift=%.0f%%, MG_K=%d, window=%d, trials=%d)" % (db, dd, ratio, SHIFT * 100, MG_K, WINDOW, TRIALS), flush=True)
    return {"d_baseline": db, "d_drift": dd, "ratio": ratio}


def verdict(r) -> Tuple[str, str]:
    rt = r["ratio"]; s = "D_baseline=%.4f D_drift=%.4f ratio=%.2f" % (r["d_baseline"], r["d_drift"], rt)
    if rt > 3.0:
        return ("HARD_PASS", "HARD_PASS: Misra-Gries L1 distance separates drift from baseline by >3x -- v1.1 concept-drift alerting confirmed (a customer-visible capability LLMs lack). " + s)
    if rt > 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: drift/baseline ratio 1.5-3.0 -- detectable but weak; larger K or finer epsilon. " + s)
    return ("HARD_FAIL", "HARD_FAIL: ratio <1.5 -- Misra-Gries snapshots not sensitive enough to a 30%% shift. " + s)


print("[config] anchor=%s mode=%s K_topics=%d MG_K=%d window=%d shift=%.2f" % (ANCHOR_NAME, RUN_MODE, K_TOPICS, MG_K, WINDOW, SHIFT), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
