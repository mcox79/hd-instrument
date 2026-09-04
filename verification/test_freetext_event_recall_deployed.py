"""Scaffold-free witness: the DEPLOYED, dependency-free glass-box-CRF detector recovers free-text 19c events
end-to-end at a precision-guarded threshold, twin losing -- the deployment-loop closure.

  W1  DEPLOYED ASSET == VALIDATED: the pure-numpy GlassBoxCRF reproduces the crfsuite P(VERB) marginals to < 1e-4
      (so the deployed, dependency-free recovery is identical to the validated one by construction).
  W2  PRECISION-GUARDED DEPLOYED RECOVERY on FREE-TEXT 19c: at a modern-fixed FP<=0.25 threshold applied unchanged
      to raw LitBank prose (spaCy-oracle event gold), recovery of perceptron-dropped events beats the info-free
      random-verbhood twin CI-separated.
  W3  END-TO-END EVENT-RECALL LIFT: (perceptron + deployed recovery) / spaCy-oracle events > perceptron alone.

Run: .venv/Scripts/python.exe verification/test_freetext_event_recall_deployed.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import json
import experiments.exp_freetext_event_recall_deployed_v1 as FT

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    if ok:
        PASS += 1
    else:
        FAIL += 1


def main():
    print("[witness] recomputing deployed free-text event recall (spaCy offline; a few minutes) ...", flush=True)
    sys.argv = ["ft", "--max-sents", "800"]
    FT.main()
    res = json.load(open(os.path.join(_REPO, "data/exp_freetext_event_recall_deployed_v1/metrics.json")))["results"]

    chk("W1 deployed asset == validated (GlassBoxCRF reproduces crfsuite P(VERB) to <1e-4)",
        res["glassbox_vs_crfsuite_maxerr"] < 1e-4, "max|dP(VERB)|=%.2e" % res["glassbox_vs_crfsuite_maxerr"])

    d = res["freetext_recovery_deployed"]
    chk("W2 precision-guarded deployed recovery beats the info-free twin CI-separated on free-text 19c",
        d["ci"][0] > 0, "recovery=%.4f @FP=%.3f delta_vs_twin=%.4f CI[%.4f,%.4f] twin=%.4f"
        % (d["recovery"], d["false_verbs_per_sent"], d["delta_vs_twin_mean"], d["ci"][0], d["ci"][1], d["twin_recovery_mean"]))

    er = res["event_recall"]
    chk("W3 end-to-end event recall lifts vs perceptron alone (deployed > perceptron)",
        er["deployed_recall"] > er["perceptron_recall"],
        "perceptron=%.4f -> deployed=%.4f (+%.4f; recovered %d/%d)"
        % (er["perceptron_recall"], er["deployed_recall"], er["deployed_recall"] - er["perceptron_recall"],
           er["n_dropped_recovered"], er["n_dropped_total"]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
