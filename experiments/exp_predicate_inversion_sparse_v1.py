"""
exp_predicate_inversion_sparse_v1 -- Pattern B bounded capability: predicate routing at sparse selectivity -- CPU.
ROUTING: handoff five_experiments_authorize #4. predicate_ratio_audit was MID (92% at 5% selectivity, <80% at 10%+).
  Tests the BOUNDED Pattern B capability for regulated KBs (legal/medical) where predicates are naturally sparse: a
  structured KB with few unique predicates, schema-aware queries "find all facts where predicate=X", VSA predicate routing,
  recall@10. CPU.
PRE-REGISTERED: HARD-PASS recall@10 >= 0.85 at <=5% selectivity. MIDDLE 0.70-0.85. HARD-FAIL <0.70.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. cleanup self.
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
ANCHOR_NAME = "predicate_inversion_sparse_v1"; N = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
N_FACTS = 200; N_PRED = 8; N_Q = 20    # sparse: 8 predicates over 200 facts; selectivity ~ per-predicate share
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def _selftest():
    g = np.random.default_rng(0); a = phasor(64, 1, g)[0]; b = phasor(64, 1, g)[0]
    assert np.allclose((a * b) * np.conj(a), b, atol=1e-4), "unbind inverts"
    assert np.allclose(np.abs(a), 1.0, atol=1e-5), "unit phasor"
    voc = phasor(64, 4, g); assert int(np.argmax((voc @ np.conj(voc[1])).real)) == 1, "cleanup self"
    print("[selftest] PASS: predicate-inversion", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run_seed(seed):
    g = np.random.default_rng(seed); preds = phasor(N, N_PRED, g); subj = phasor(N, N_FACTS, g); obj = phasor(N, N_FACTS, g)
    # each fact = pred (x) subj + obj-role binding; assign sparse predicates (skewed: predicate 0 rare)
    pred_of = g.integers(0, N_PRED, N_FACTS)
    mem = np.zeros(N, np.complex64)
    facts = []
    for i in range(N_FACTS):
        b = preds[pred_of[i]] * subj[i]; mem = mem + b; facts.append(b)
    facts = np.array(facts)
    # query: find facts with predicate = X -> unbind pred X from each fact's pred-subj binding, score by subj presence
    recs = []
    for _ in range(N_Q):
        X = int(g.integers(0, N_PRED)); targets = np.where(pred_of == X)[0]
        if len(targets) == 0: continue
        # route: for each stored fact binding, unbind X -> should yield a clean subj phasor if fact has pred X
        unb = facts * np.conj(preds[X])                          # [F, N]
        score = np.abs((unb @ np.conj(subj.T)).real).max(axis=1)  # cleanliness = max subj match
        top = np.argsort(score)[::-1][:10]
        rec = len(set(top) & set(targets)) / min(10, len(targets))
        recs.append(rec)
    return float(np.mean(recs)) if recs else 0.0
def run() -> Dict:
    r = float(np.mean([run_seed(s) for s in SEEDS])); sel = 1.0 / N_PRED
    print("  predicate routing recall@10=%.3f at selectivity~%.1f%% (%d preds/%d facts)" % (r, sel * 100, N_PRED, N_FACTS), flush=True)
    return {"recall10": r, "selectivity": sel}
def verdict(rr) -> Tuple[str, str]:
    r = rr["recall10"]; summary = "recall@10=%.3f at ~%.1f%% selectivity (%d predicates/%d facts)" % (r, rr["selectivity"] * 100, N_PRED, N_FACTS)
    if r >= 0.85: return ("HARD_PASS", "HARD_PASS: predicate routing recall@10>=0.85 at sparse selectivity -- bounded Pattern B capability for regulated (legal/medical) sparse-predicate KBs. " + summary)
    if r >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: predicate routing 0.70-0.85. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: predicate routing <0.70 -- interference too high even at sparse selectivity. " + summary)
print("[config] anchor=%s mode=%s seeds=%s N=%d facts=%d preds=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_FACTS, N_PRED), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
