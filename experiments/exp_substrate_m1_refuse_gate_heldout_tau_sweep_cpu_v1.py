"""
exp_substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1.py -- DECISION 34a: M1 confidence-gate (tau on bge similarity) on held-out, decomposed -- does a tau exist where COVERAGE-GAP refuse-rate >= 0.95 while IN-COVERAGE F1 drops <= 0.05? -- runs on BGE machine (remote).

ROUTING: Director DECISION 34a. M1 = my F1-BRIDGE H1 tau-gate (tau=0.80 cut FP 70.6pct). Apply to held-out q54-q65, sweep tau, decompose by
  coverage (gold-in-index). For each tau: predicted = atoms with bge cosine >= tau (refuse if none). IN-COVERAGE F1 scored vs PRESENT-gold
  subset (isolates capability from coverage); COVERAGE-GAP refuse-rate = frac of questions where the gate returns nothing.
  Falsifier (10th+22nd): HARD-PASS iff exists tau with COVERAGE-GAP refuse-rate >= 0.95 AND IN-COVERAGE F1 drop <= 0.05 vs ungated.
  HARD-FAIL iff no such tau (in-coverage drops > 0.05 to reach 0.95 refuse, OR can't reach 0.85 refuse). Substrate-internal (bge primitive; no LLM).
  NOTE: M1 is a SOUNDNESS-only fix (Cause 2); it does NOT address Cause 3 (capability-transfer; IN-COVERAGE already ~0.03). ASCII; --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
TAUS = [round(x, 2) for x in np.arange(0.50, 0.96, 0.05)]


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def f1_present(pred: set, present_gold: set) -> float:
    if not present_gold:
        return 1.0 if not pred else 0.0
    inter = len(pred & present_gold)
    p = inter / len(pred) if pred else 0.0; r = inter / len(present_gold)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def _selftest():
    assert abs(f1_present({"a", "b"}, {"a"}) - (2 * 0.5 * 1 / 1.5)) < 1e-6
    assert f1_present(set(), set()) == 1.0 and f1_present({"x"}, set()) == 0.0
    print("[selftest] PASS: substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout_file"}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:100]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    # bucket + cache per-question (qualified_id, score) lists once
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {g for g in gold if _short(g) in sset}
        in_cov = bool(present)
        try:
            cands = r.semantic(q["question"], top_k=20)
        except Exception:
            cands = []
        ranked = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        perq.append({"qid": q["qid"], "in_cov": in_cov, "present": present, "ranked": ranked})
    inc = [x for x in perq if x["in_cov"]]; gap = [x for x in perq if not x["in_cov"]]

    def eval_tau(tau):
        inc_f1 = []
        for x in inc:
            pred = {cid for cid, sc in x["ranked"] if sc >= tau}
            inc_f1.append(f1_present(pred, x["present"]))
        gap_refuse = []
        for x in gap:
            pred = [cid for cid, sc in x["ranked"] if sc >= tau]
            gap_refuse.append(1.0 if not pred else 0.0)
        return (round(sum(inc_f1) / len(inc_f1), 4) if inc_f1 else 0.0,
                round(sum(gap_refuse) / len(gap_refuse), 4) if gap_refuse else 1.0)
    ungated_inc, ungated_ref = eval_tau(0.0)
    rows = []
    for tau in TAUS:
        f, ref = eval_tau(tau); rows.append({"tau": tau, "in_cov_f1": f, "gap_refuse_rate": ref})
    print("  held-out: in-coverage=%d, coverage-gap=%d | UNGATED in-cov-F1=%.4f gap-refuse=%.4f" % (len(inc), len(gap), ungated_inc, ungated_ref), flush=True)
    print("  tau   in_cov_F1   gap_refuse_rate", flush=True)
    for r_ in rows:
        print("  %.2f   %.4f      %.4f" % (r_["tau"], r_["in_cov_f1"], r_["gap_refuse_rate"]), flush=True)
    # find tau meeting HARD-PASS: gap_refuse >= 0.95 AND in_cov drop <= 0.05
    ok = [r_ for r_ in rows if r_["gap_refuse_rate"] >= 0.95 and (ungated_inc - r_["in_cov_f1"]) <= 0.05]
    best = min(ok, key=lambda r_: r_["tau"]) if ok else None
    return {"n_in_cov": len(inc), "n_gap": len(gap), "ungated_in_cov_f1": ungated_inc, "ungated_gap_refuse": ungated_ref,
            "sweep": rows, "hard_pass_tau": best}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    best = r["hard_pass_tau"]
    s = ("M1 tau-gate on held-out (DECISION 34a). Ungated: in-cov-F1=%.4f, gap-refuse=%.4f. Sweep tau in [0.50,0.95]. HARD-PASS needs a tau with "
         "gap-refuse>=0.95 AND in-cov-F1 drop<=0.05. Best qualifying tau: %s. NOTE: M1 is a SOUNDNESS-only fix (Cause 2); IN-COVERAGE is already "
         "~%.3f (Cause 3 capability-transfer gap -- M1 does not fix it).") % (
        r["ungated_in_cov_f1"], r["ungated_gap_refuse"], (best["tau"] if best else "NONE"), r["ungated_in_cov_f1"])
    if best is not None:
        return ("HARD_PASS", "HARD_PASS (M1 viable for soundness): at tau=%.2f, COVERAGE-GAP refuse-rate=%.4f>=0.95 AND IN-COVERAGE F1=%.4f (drop "
                "%.4f<=0.05 from ungated %.4f). A confidence gate generalizes the refuse-discipline to unknown topics without sacrificing the "
                "(already-low) in-coverage capability. Cause-2 soundness fixable by a tau gate. " % (
                    best["tau"], best["gap_refuse_rate"], best["in_cov_f1"], r["ungated_in_cov_f1"] - best["in_cov_f1"], r["ungated_in_cov_f1"]) + s)
    return ("HARD_FAIL", "HARD_FAIL (M1 insufficient in this regime): no tau achieves gap-refuse>=0.95 without dropping in-coverage F1 >0.05 -- "
            "the substrate cannot separate present-gold-paraphrased from absent-gold by bge confidence alone (the categorical failure mode). "
            "Refuse-robustness needs more than a similarity threshold (composes with Cause-3 query-side work). " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
