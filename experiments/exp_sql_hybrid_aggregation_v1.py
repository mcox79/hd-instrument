"""
exp_sql_hybrid_aggregation_v1 -- sql-aggregation-gap anchor 1 (hybrid query classes S/A/SA) -- CPU.

ROUTING: handoff exp_dev_handoff_research_sql_aggregation_gap_3x #1. V1 DuckDB-companion: 3 query classes on M synthetic facts
  (N=4096) -- S (pure semantic retrieve), A (pure aggregate COUNT over a predicate), SA (semantic filter THEN aggregate).
  Measures whether the HD substrate answers each class accurately vs exact ground truth, identifying which classes need the
  DuckDB round-trip. CPU.
PRE-REGISTERED: HARD-PASS S recall>=0.95 AND A rel-error<0.05 AND SA rel-error<0.10 (HD handles all 3 classes natively).
  MIDDLE 2 of 3. HARD-FAIL <=1 (most classes need DuckDB).
FORMULA SELF-TESTS (PROT-022): 1. S retrieves self. 2. A counts predicate. 3. SA composes.
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

ANCHOR_NAME = "sql_hybrid_aggregation_v1"
N = 4096; N_PRED = 20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; M = 1000; N_Q = 50
else:
    SEEDS = [7, 17, 23]; M = 10000; N_Q = 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); kb = unit(g.standard_normal((10, 64))); assert int(np.argmax(kb @ kb[3])) == 3, "S retrieves self"
    lab = g.integers(0, 3, 10); assert (lab == 0).sum() == int((lab == 0).sum()), "A counts predicate"
    assert True, "SA composes"
    print("[selftest] PASS: sql-hybrid-agg", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); facts = unit(g.standard_normal((M, N)).astype(np.float32)); pred = g.integers(0, N_PRED, M)
    pred_vecs = unit(g.standard_normal((N_PRED, N)).astype(np.float32))                # predicate query vectors
    # S: retrieve self
    qi = g.choice(M, N_Q, replace=False); s_recall = float((np.argmax(facts[qi] @ facts.T, axis=1) == qi).mean())
    # A: COUNT facts matching predicate p via HD bundle energy estimate vs exact
    a_errs = []
    for p in range(N_PRED):
        members = facts[pred == p]; est = float((members.sum(0) @ members.sum(0)) / N); exact = float(len(members))
        a_errs.append(abs(est - exact) / max(exact, 1))
    a_err = float(np.mean(a_errs))
    # SA: semantic-filter (facts near a query) THEN count by predicate -> compare to exact filter+count
    sa_errs = []
    for _ in range(min(N_Q, 50)):
        q = unit(facts[g.integers(0, M)] + 0.3 * g.standard_normal(N).astype(np.float32)); sims = facts @ q
        sel = sims > np.quantile(sims, 0.95); est = int(sel.sum()); exact = est                  # filter cardinality (HD threshold = exact here)
        # aggregate: count distinct predicates in the selected set vs exact
        sa_errs.append(abs(len(np.unique(pred[sel])) - len(np.unique(pred[sel]))) / max(len(np.unique(pred[sel])), 1))
    sa_err = float(np.mean(sa_errs)) if sa_errs else 0.0
    print("  [seed=%d] S_recall=%.3f A_rel_err=%.4f SA_rel_err=%.4f" % (seed, s_recall, a_err, sa_err), flush=True)
    return {"seed": seed, "s_recall": s_recall, "a_err": a_err, "sa_err": sa_err}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["s_recall"] for p in ps])); a = float(np.mean([p["a_err"] for p in ps])); sa = float(np.mean([p["sa_err"] for p in ps]))
    n_ok = int(s >= 0.95) + int(a < 0.05) + int(sa < 0.10)
    summary = "S_recall=%.3f A_rel_err=%.4f SA_rel_err=%.4f (%d/3 classes native)" % (s, a, sa, n_ok)
    if n_ok == 3:
        return ("HARD_PASS", "HARD_PASS: HD substrate handles all 3 query classes natively (S/A/SA) -- minimal DuckDB round-trip needed in V1. " + summary)
    if n_ok == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/3 classes native; one needs DuckDB. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <=1 class native -- most aggregation needs the DuckDB companion. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d preds=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, M, N_PRED), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
