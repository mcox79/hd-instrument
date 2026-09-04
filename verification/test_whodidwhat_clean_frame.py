"""Scaffold-free witness: the 19c who-did-what "wall" is a GOLD-CONTAMINATION artifact, and on a correct ruler our
reader is AT/ABOVE the competent-reader proxy.

Recomputes from source (core-constrained; spaCy offline-diagnostic only, never at inference):
  W1  THE GOLD IS CONTAMINATED: true-direct-object share < 0.25 of the who-did-what gold (rest = PP-oblique/copular/
      pre-verbal roles a patient-selector structurally should not pick).
  W2  THE WALL DISSOLVES ON A CORRECT RULER: on the clean direct-object subset, the landed NP-head reader scores >= 0.90
      (vs the contaminated full-gold ~0.44).
  W3  THE INVERSION: on the clean-DO subset our NP-head reader BEATS the competent-reader proxy (spaCy) CI-separated --
      the earlier "spaCy beats us at the parse stage" was purely the contaminated ruler.

Run: .venv/Scripts/python.exe verification/test_whodidwhat_clean_frame.py
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
import experiments.exp_whodidwhat_clean_frame_ladder_v1 as CF

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
    print("[witness] recomputing who-did-what under a correct ruler (spaCy offline; a few minutes) ...", flush=True)
    sys.argv = ["cf", "--cap", "2500"]
    CF.main()
    res = json.load(open(os.path.join(_REPO, "data/exp_whodidwhat_clean_frame_ladder_v1/metrics.json")))["results"]

    do_share = res["shares"]["DIRECT_OBJECT"]
    chk("W1 the who-did-what gold is contaminated (true direct-object share < 0.25)",
        do_share < 0.25, "DO=%.3f oblique=%.3f copular=%.3f preverbal=%.3f"
        % (do_share, res["shares"]["PP_OBLIQUE"], res["shares"]["COPULAR"], res["shares"]["PRE_VERBAL"]))

    allnp = res["acc"]["ALL"]["nphead"]; cdnp = res["acc"]["CLEAN_DO"]["nphead"]; cdpos = res["acc"]["CLEAN_DO"]["pos"]
    chk("W2 the wall dissolves on a correct ruler (clean-DO NP-head >= 0.90 vs contaminated ALL ~0.44)",
        cdnp >= 0.90, "ALL=%.4f -> CLEAN_DO pos=%.4f nphead=%.4f" % (allnp, cdpos, cdnp))

    inv = res["clean_do_nphead_vs_spacy"]
    chk("W3 INVERSION: on clean-DO our NP-head reader BEATS the competent-reader proxy CI-separated",
        inv["sep"] and inv["delta"] > 0, "NP-head - spaCy = %+.4f CI%s" % (inv["delta"], inv["ci"]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
