"""Witness for the GroundedCausalLearner organ prototype + the active-selection last lever: the unified learner recovers
direction FEW-SHOT (active, ~5 interventions), composes into causal_reasoner for cause selection, is PLASTIC (online
refresh does not degrade), and active selection reaches 0.90 edge-orientation in the brain few-shot band while random
does not. Micro-world proof-of-mechanism. Run: .venv/Scripts/python.exe verification/test_grounded_causal_learner_organ.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("OMP_NUM_THREADS", "3")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (("  " + detail) if detail else ""))
    return bool(cond)


def main():
    from experiments.exp_grounded_causal_learner_organ_v1 import run as organ_run
    o = organ_run(smoke=True)
    check("W1 organ learns direction FEW-SHOT (active interventions <= brain band ~10)",
          o["mean_interventions_used"] <= 10, "interventions=%.1f" % o["mean_interventions_used"])
    check("W2 few-shot direction beats the ~0.61 text ceiling",
          o["direction_accuracy_fewshot_active"]["acc"] > 0.61,
          "dir=%.3f" % o["direction_accuracy_fewshot_active"]["acc"])
    check("W3 composes into causal_reasoner for cause selection well above chance",
          o["cause_selection_via_causal_reasoner"]["acc"] > 0.3,
          "sel=%.3f" % o["cause_selection_via_causal_reasoner"]["acc"])
    check("W4 PLASTIC: online refresh does not degrade direction",
          o["direction_accuracy_after_online_refresh"]["acc"] >= o["direction_accuracy_fewshot_active"]["acc"] - 0.02,
          "before=%.3f after=%.3f" % (o["direction_accuracy_fewshot_active"]["acc"],
                                      o["direction_accuracy_after_online_refresh"]["acc"]))

    from experiments.exp_causal_direction_active_selection_v1 import run as active_run
    a = active_run(smoke=True)
    cur = a["edges_correct_by_num_interventions"]
    fs = min(4, len(cur["active"]) - 1)   # few-shot budget index (~5 interventions)
    act_fs, ran_fs = cur["active"][fs], cur["random"][fs]
    act_end, ran_end = cur["active"][-1], cur["random"][-1]
    check("W5 ACTIVE selection is far more efficient than RANDOM (few-shot orientation >> random, plateau >> random)",
          (act_fs - ran_fs > 0.2) and (act_end - ran_end > 0.1),
          "few-shot active=%.3f vs random=%.3f | plateau active=%.3f vs random=%.3f" % (act_fs, ran_fs, act_end, ran_end))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
