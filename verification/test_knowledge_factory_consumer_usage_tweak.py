"""Scaffold-free witness: the consumer-usage tweak (AvgSim mean-centroid -> MaxSim/top-k nearest-exemplar) for the
LIVE hub consumer composed_hub_predictor, measured on the which-argument task in the DISTRIBUTIONAL HUB SPACE it uses.

  U1  MaxSim/top-k exemplar BEATS AvgSim mean-centroid CI-separated on the AMBIGUOUS slice (the tweak helps)
  U2  the verb-SHUFFLED-exemplar twin LOSES (the win is the verb-keyed instance distribution, not a generic scorer)
  U3  the tweak is above the chance floor (it is a real selection, not a shape artifact)

Run: .venv/Scripts/python.exe verification/test_knowledge_factory_consumer_usage_tweak.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_knowledge_factory_consumer_usage_tweak_v1 as T

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    res = T.run(smoke=False)
    a = res["AMBIGUOUS"]
    chk("U1 MaxSim/top-k exemplar BEATS AvgSim mean-centroid CI-sep on the ambiguous slice",
        a["TWEAK_vs_centroid"]["sep"] and a["MaxSim_topk"] > a["AvgSim_centroid"],
        "AvgSim %.4f -> MaxSim %.4f d=%+.4f" % (a["AvgSim_centroid"], a["MaxSim_topk"],
                                                a["TWEAK_vs_centroid"]["delta"]))
    chk("U2 verb-SHUFFLED-exemplar twin LOSES CI-sep (verb-keyed instance distribution, not a generic scorer)",
        a["TWEAK_vs_shuffled_twin"]["sep"] and a["MaxSim_topk"] > a["verb_shuffled_twin"],
        "MaxSim %.4f vs twin %.4f" % (a["MaxSim_topk"], a["verb_shuffled_twin"]))
    chk("U3 the tweak is above the chance floor",
        a["MaxSim_topk"] > a["chance_floor"] + 0.05,
        "MaxSim %.4f vs chance %.4f" % (a["MaxSim_topk"], a["chance_floor"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
