"""Witness: the bridge loop CLOSED on real science concepts. Simulated intervention on the runnable grounded model
recovers physical-law causal DIRECTION (~0.99) that the text-mined store (chance on these reaction pairs) and
observation-under-confounding cannot; twin at chance. Non-circular: the learner infers structure from interventional
samples, ground-truthed against physical law. Run: .venv/Scripts/python.exe verification/test_causal_bridge_science_learn.py
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
    from experiments.exp_causal_bridge_science_learn_v1 import run, TEXT_STORE_CEILING
    o = run(smoke=True)
    d = o["direction_recovery_on_real_science_concepts"]
    g = d["grounded_simulated_intervention"]["acc"]
    check("W1 grounded simulated-intervention recovers physical-law direction on real science concepts (>0.9)",
          g > 0.9, "grounded=%.3f (nodes=%d edges=%d)" % (g, o["n_nodes"], o["n_edges"]))
    check("W2 it beats the ~0.61 text-store ceiling by >=0.15", g >= TEXT_STORE_CEILING + 0.15,
          "grounded=%.3f ceiling=%.2f" % (g, TEXT_STORE_CEILING))
    check("W3 the TEXT STORE is near chance on these real science concept pairs (text cannot orient reactions)",
          d["text_store"]["acc"] <= 0.6 and d["text_store_coverage"] > 0.2,
          "text_store=%.3f cov=%.2f" % (d["text_store"]["acc"], d["text_store_coverage"]))
    check("W4 observation-under-confounding and the twin are at chance (the signal is the INTERVENTION)",
          abs(d["observational_cooccurrence"]["acc"] - 0.5) < 0.06 and abs(d["random_twin"]["acc"] - 0.5) < 0.08,
          "obs=%.3f twin=%.3f" % (d["observational_cooccurrence"]["acc"], d["random_twin"]["acc"]))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
