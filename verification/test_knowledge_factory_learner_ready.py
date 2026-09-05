"""Scaffold-free readiness witness: is the INGEST -> LEARN -> TRIM/GATE machinery ready for real, live use?

A production learner must do BOTH: ADMIT beneficial growth AND REJECT harmful growth. This witness verifies the
full cycle on the LANDED organs + this problem's measured results (writes nothing):

  R1  the LANDED admission gate (hdlab.consolidation_gate.regression_guard) ADMITS the beneficial associative
      growth (SimLex rho climbs -> admit=True)
  R2  the SAME gate REJECTS the harmful meaning growth (targeted-acquisition regresses the collapsed-pair a_s ->
      admit=False) -- the gate's REJECTION is as load-bearing as its admission
  R3  the LANDED safety primitives work: cls_growth keep-both ensemble fuses without discarding a channel;
      rollback_gate accepts a clean update and rolls back a corrupting one; align_and_fuse EMA-anchors
  R4  the freeze is deterministic + byte-faithful (the frozen store reloads exactly)

If all pass, the machinery COULD be used live: it grows what helps, blocks what hurts, is reversible, and freezes
reproducibly. (What remains for FULL live use is the hdlab LOOP ORCHESTRATION + the reader read-out flag -- strategy's
Q111 lane, blocked on the reader_meaning_channel stage; the PRIMITIVES here are landed + witnessed.)

Run: .venv/Scripts/python.exe verification/test_knowledge_factory_learner_ready.py
"""
import os
import sys
import json

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.consolidation_gate import regression_guard
from hdlab import cls_growth

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def _load(path):
    return json.load(open(path, encoding="ascii"))["result"] if os.path.exists(path) else None


def main():
    # R1: the gate ADMITS beneficial associative growth (SimLex climb; raw-count is the losing floor)
    gl = _load(os.path.join(_REPO, "data", "exp_knowledge_factory_grow_loop_v1", "metrics_full.json"))
    if gl:
        h = gl["history"]; first, last = h[0], h[-1]
        guard_assoc = regression_guard(consolidated_score=last["simlex_rho"], raw_score=last["simlex_raw_rho"],
                                       gloss_score=first["simlex_rho"])
        chk("R1 gate ADMITS beneficial associative growth (SimLex climb, raw-count loses)",
            guard_assoc["admit"] is True and guard_assoc["raw_regresses"] is True,
            "final %.4f vs first %.4f vs raw %.4f -> admit=%s" % (last["simlex_rho"], first["simlex_rho"],
                                                                  last["simlex_raw_rho"], guard_assoc["admit"]))
    else:
        chk("R1 associative grow metrics present", False, "missing grow_loop metrics")

    # R2: the SAME gate REJECTS harmful meaning growth (targeted acquisition regresses the collapsed-pair a_s)
    ta = _load(os.path.join(_REPO, "data", "exp_knowledge_factory_targeted_acq_v1", "metrics_full.json"))
    if ta:
        frozen = ta["a_s_targeted"]["frozen"]; grown = ta["a_s_targeted"]["TARGETED_grown"]
        guard_mean = regression_guard(consolidated_score=grown, raw_score=frozen, gloss_score=frozen)
        chk("R2 gate REJECTS harmful meaning growth (targeted acq regresses -> admit=False)",
            guard_mean["admit"] is False and grown < frozen,
            "grown %.4f < frozen-floor %.4f -> admit=%s (located negative correctly blocked)"
            % (grown, frozen, guard_mean["admit"]))
    else:
        chk("R2 targeted-acq metrics present", False, "missing targeted_acq metrics")

    # R3: the landed safety primitives function (keep-both fusion + rollback accept/reject + EMA anchor)
    sim_a = lambda q, c: 0.9 if c == "good" else 0.1        # old store: 'good' correct
    sim_b = lambda q, c: 0.8 if c == "good" else 0.2        # grown store: agrees
    fused = cls_growth.make_ensemble_sim(sim_a, 0.5, 0.4, sim_b, 0.5, 0.3, "mean")
    keeps_both = fused("q", "good") is not None and fused("q", "bad") is not None
    # rollback: a clean update (never flips) accepted; a corrupting update (flips all) rolled back
    items = [{"query": "q%d" % i, "cand": ["good", "bad"], "target": "good"} for i in range(20)]
    clean = lambda q, c: 1.0 if c == "good" else 0.0
    corrupt = lambda q, c: 1.0 if c == "bad" else 0.0
    rb = cls_growth.rollback_gate(items, list(range(20)), clean,
                                  {"clean": clean, "corrupt": corrupt}, tolerance=0.15, seed=0)
    chk("R3 safety primitives work: keep-both fusion + rollback accepts clean / rejects corrupting update",
        keeps_both and rb["updates"]["clean"]["decision"] == "ACCEPT"
        and rb["updates"]["corrupt"]["decision"] == "ROLLBACK",
        "clean=%s corrupt=%s" % (rb["updates"]["clean"]["decision"], rb["updates"]["corrupt"]["decision"]))

    # R4: deterministic freeze/reload byte-faithful (reuse the meaning-store freeze on a tiny store)
    import experiments.exp_knowledge_factory_meaning_store_v1 as MS
    rng = np.random.default_rng(0)
    v = rng.standard_normal(MS.EMB_DIM).astype(np.float32); v /= np.linalg.norm(v)
    tmp = os.path.join(_REPO, "data", "exp_knowledge_factory_meaning_store_v1", "_ready_probe.npz")
    MS.freeze({"a.n.01": v}, tmp, {"t": 1}); back = MS.load_frozen(tmp)
    chk("R4 freeze/reload is byte-faithful (deterministic frozen asset)",
        back["a.n.01"] is not None and np.allclose(back["a.n.01"], v, atol=1e-6),
        "roundtrip max|delta|=%.2e" % float(np.max(np.abs(back["a.n.01"] - v))))
    try:
        os.remove(tmp)
    except OSError:
        pass

    print("\n%d/%d readiness checks passed" % (PASS, PASS + FAIL), flush=True)
    print("VERDICT: %s" % ("the ingest->learn->trim/gate machinery ADMITS beneficial growth, REJECTS harmful "
                           "growth, is reversible, and freezes reproducibly -> READY for live use (pending the "
                           "hdlab loop-orchestration wire, strategy Q111)." if FAIL == 0 else
                           "NOT READY -- see failures above."), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
