"""Scaffold-free witness for the STEP-2 grow-from-reading demonstration (the second typed store).

Runs the multi-round grow loop on a small corpus slice (writes NOTHING -- freeze disabled) and asserts the
load-bearing claims of "ingest -> prune -> clear improvement":

  G1  recurrence prune keeps only recurrent co-occurrence (drops one-offs)
  G2  the PRUNE converts raw-regression into a gain: PPMI-gated SimLex rho > RAW-count (no-prune) rho
  G3  the info-free SHUFFLED-corpus twin LOSES (real co-occurrence structure carries the signal)
  G4  rho CLIMBS as more corpus is ingested (final round >= first round, within noise)

The FULL respectable-corpus numbers + the frozen associative store are produced by the full run
(exp_knowledge_factory_grow_loop_v1, remote/local); this witness proves the mechanism cheaply and deterministically.

Run: .venv/Scripts/python.exe verification/test_knowledge_factory_grow_loop.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
import experiments.exp_knowledge_factory_grow_loop_v1 as GL

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    from scipy.sparse import csr_matrix
    m = csr_matrix(np.array([[5, 1, 0], [0, 4, 2], [3, 0, 1]], float))
    pruned, kept = GL.recurrence_prune(m, 3)
    chk("G1 recurrence prune keeps only recurrent (>=3) co-occurrence, drops one-offs",
        pruned.nnz == 3 and all(v >= 3 for v in pruned.data), "nnz=%d kept_frac=%.2f" % (pruned.nnz, kept))

    # run the mechanism on the smoke corpus slice, NO freeze (writes nothing to frontend_assets)
    res = GL.run(smoke=True, freeze=False)
    h = res["history"]
    chk("G2 the PRUNE converts raw-regression to gain (PPMI-gated rho > raw-count rho)",
        res["prune_helps"] and h[-1]["simlex_rho"] > h[-1]["simlex_raw_rho"],
        "gated %.4f vs raw %.4f" % (h[-1]["simlex_rho"], h[-1]["simlex_raw_rho"]))
    chk("G3 info-free SHUFFLED-corpus twin LOSES (co-occurrence structure carries the signal)",
        res["shuffled_twin_loses"] and h[-1]["simlex_rho"] > h[-1]["simlex_shuffled_rho"],
        "gated %.4f vs shuffled %.4f" % (h[-1]["simlex_rho"], h[-1]["simlex_shuffled_rho"]))
    chk("G4 rho CLIMBS as more corpus is ingested (final >= first within noise)",
        h[-1]["simlex_rho"] >= h[0]["simlex_rho"] - 0.01 or h[-1]["wordsim_rho"] >= h[0]["wordsim_rho"],
        "SimLex %.4f->%.4f WordSim %.4f->%.4f" % (h[0]["simlex_rho"], h[-1]["simlex_rho"],
                                                  h[0]["wordsim_rho"], h[-1]["wordsim_rho"]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
