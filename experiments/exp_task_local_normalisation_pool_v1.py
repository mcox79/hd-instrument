"""exp_task_local_normalisation_pool_v1 -- is the brain's normalisation POOL (the concurrently
active population) the thing the predecessor's global-field pool got wrong?

PRE-REG: preregs/2026-08-13_task_local_normalisation_pool.md, COMMITTED (e07d8ffb3) BEFORE this
file existed and BEFORE any arm was scored. Every arm, band, floor and gate is frozen there.
PARENT AUDIT row C4: notes/comparator_component_fidelity_audit_2026-08-13.md.
PREDECESSOR: exp_graded_divisive_comparator_v1 HARD_PASS (0f6459309), wired at 542fb7754.

WHY THIS CELL EXISTS
MEASURED@data/exp_graded_divisive_comparator_v1/metrics.json: removing the two quantisers is worth
+0.0585 of a +0.0602 total, but GLOBAL-FIELD divisive normalisation on top of it is NULL
(+0.0018, CI [-0.0030,+0.0065]) despite removing a shared component worth 58% of every anchor norm.
HYPOTHESIZED@prereg sec 1: a component shared by BOTH candidates contributes near-equally to both
cosines and nearly CANCELS in a two-candidate argmax, so the failure was the POOL, not the
operation.
CITED@Carandini & Heeger 2012 Nat Rev Neurosci 13:51-62 -- the normalisation denominator is the
CONCURRENTLY ACTIVE population, which at decision time is the two candidates, not the 2377-anchor
store. CITED@Chiou & Lambon Ralph 2018 Cortex (DCM, F(2,34)=3.86 p=.03) -- semantic control applies
multiplicative GAIN to task-relevant dimensions. CITED@Cree/McNorgan/McRae; Tyler & Moss CSA --
distinctive features (present in FEW concepts) are privileged. All three are the SAME OPERATION
here: dividing by the active pool suppresses dimensions where BOTH candidates are strong (shared
features) and preserves those where only one is (distinctive features).

THE DECISIVE CONTROL is W_WRONGPOOL -- the identical operation with the gain computed from a
DIFFERENT item's candidate pair. If it reproduces the win, the gain is a generic variance filter,
and HARD_FAIL_GENERIC_NOT_TASK_LOCAL OUTRANKS the pass.

NOTHING UNDER hdlab/ IS MODIFIED BY THIS CELL.

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import platform
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, ConceptSpace, canonicalize_fast, context_vector_masked, normalize_lemma,
)

# ---- the two predecessors, imported wholesale. Items/leak controls/split/donors come from the
#      grandparent; encoders, normalisation and the read-out come from the parent. Nothing here
#      re-implements either.
import experiments.exp_context_conditioned_near_neighbour_v1 as GP           # noqa: E402
import experiments.exp_graded_divisive_comparator_v1 as P1                   # noqa: E402

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_task_local_normalisation_pool_v1"
PREREG_PATH = "preregs/2026-08-13_task_local_normalisation_pool.md"
PREREG_COMMIT = "e07d8ffb3"
AMENDMENT_PATH = "preregs/2026-08-13_task_local_normalisation_pool_AMENDMENT_A1.md"
AMENDMENT_COMMIT = "0b445b3bf"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260813
BOOTSTRAP_SEED = 20260813
N_BOOTSTRAP = 5000
MAX_ITEMS = GP.MAX_ITEMS
MIN_ITEMS = GP.MIN_ITEMS
SMOKE_ITEM_SCALES = (150, 600)
STRICT_MARGIN_FRAC = 0.05
CHANCE = 0.50

R_LIVE, R_BASE = "R_LIVE", "R_BASE"
P_CONTROL = "P_CONTROL"      # AMENDMENT A1 primary: g = |a-b| (semantic control gain)
P_LOCAL = "P_LOCAL"          # AMENDMENT A1: DEMOTED, no verdict weight, still scored
W_WRONGPOOL = "W_WRONGPOOL"
F_LOCAL_SCRAM, F_BASE_SCRAM, B_FREQ = "F_LOCAL_SCRAM", "F_BASE_SCRAM", "B_FREQ"
ARMS = (R_LIVE, R_BASE, P_CONTROL, P_LOCAL, W_WRONGPOOL, F_LOCAL_SCRAM, F_BASE_SCRAM,
        B_FREQ)

HP_DELTA = 0.03
FLOOR_MAX = 0.55
LANDED_LIVE, LANDED_BASE, LANDED_TOL = 0.6395, 0.6997, 0.02
SIGMA_SWEEP = (0.25, 0.5, 1.0, 2.0, 4.0)
D_SWEEP = (1024,)                      # d=256 is the primary; this is the fair-test diagnostic
_EPS = 1e-9


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))
    with open(os.path.join(output_dir, "_pid"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def _heartbeat(output_dir: str, stage: str, done: int, total: int, elapsed_s: float) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage, "done": done,
           "total": total, "elapsed_s": round(elapsed_s, 3)}
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0, "run_mode": "crash",
        "failure_class": type(exc).__name__, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# THE OPERATION UNDER TEST
# ---------------------------------------------------------------------------------------------
def pool_sigma(A: np.ndarray, items: Sequence[dict], wpos: Dict[str, int]) -> float:
    """sigma = mean of pool_j = |a_j| + |b_j| over ALL dimensions and ALL items. Derived from the
    field, never tuned (pre-reg sec 2)."""
    tot, cnt = 0.0, 0
    for it in items:
        p = np.abs(A[wpos[it["target"]]]) + np.abs(A[wpos[it["distractor"]]])
        tot += float(p.sum())
        cnt += p.size
    return tot / max(cnt, 1)


def score_gain_arm(items: List[dict], wpos: Dict[str, int], A: np.ndarray, Q: np.ndarray,
                   mode: str, sigma: float, donors: Optional[Sequence[int]] = None
                   ) -> Tuple[np.ndarray, dict]:
    """2AFC with a per-dimension GAIN applied to the query and both candidate anchors.

    mode="local": g = 1/(sigma + |a_t| + |a_d|)   -- divisive normalisation, pool = ACTIVE SET
    mode="diff" : g = |a_t - a_d| / mean(...)     -- AMENDMENT A1 PRIMARY: control gain
    mode="wrong": g as in "local" but computed from the DONOR item's candidate pair (the control
                  that reproduces the win from the WRONG source)
    Tie-break replicates canonicalize_fast: the alphabetically earlier candidate wins.
    """
    correct = np.zeros(len(items), dtype=bool)
    n_tie = 0
    margins = np.zeros(len(items), dtype=np.float64)
    for i, it in enumerate(items):
        at = A[wpos[it["target"]]]
        ad = A[wpos[it["distractor"]]]
        if mode == "local":
            # pool computed FIRST so it is bitwise commutative in the two candidates:
            # `sigma + |a| + |b|` parses as `(sigma + |a|) + |b|` and is
            # order-dependent by floating-point ASSOCIATIVITY, which would make the
            # gain (microscopically) depend on which candidate is called the target.
            # Self-test S1 asserts the symmetry that this line buys.
            g = 1.0 / (sigma + (np.abs(at) + np.abs(ad)))
        elif mode == "diff":
            g = np.abs(at - ad)
            m = float(g.mean())
            g = g / m if m > _EPS else np.ones_like(g)
        elif mode == "wrong":
            # AMENDMENT A1: the wrong-source control for the NEW primary -- the SAME |a-b|
            # gain, computed from a DIFFERENT item's candidate pair.
            dj = items[donors[i]]
            g = np.abs(A[wpos[dj["target"]]] - A[wpos[dj["distractor"]]])
            m = float(g.mean())
            g = g / m if m > _EPS else np.ones_like(g)
        else:
            raise ValueError("unknown gain mode %r" % mode)
        q = Q[i] * g
        s = P1._cos_rows(q, np.stack([at * g, ad * g]))
        st, sd = float(s[0]), float(s[1])
        margins[i] = st - sd
        if st == sd:
            n_tie += 1
            correct[i] = (it["target"] < it["distractor"])
        else:
            correct[i] = st > sd
    return correct, {"n_ties": n_tie, "gain_mode": mode, "sigma": round(float(sigma), 6),
                     "mean_abs_margin": round(float(np.mean(np.abs(margins))), 6)}


def decide_verdict(bs: dict, accs: Dict[str, float], readout_disagreements: int,
                   self_retrieval: Dict[str, float]) -> Tuple[str, List[str]]:
    """Bands frozen in preregs/2026-08-13_task_local_normalisation_pool.md sec 4."""
    d = bs["deltas"]["d_PCONTROL_minus_RBASE"]
    dw = bs["deltas"]["d_PCONTROL_minus_WRONGPOOL"]
    if readout_disagreements > 0:
        return "INSTRUMENTATION_SUSPECT_READOUT_FORK", [
            "read-out disagreed with hdlab.canonicalize_fast on %d LIVE items" % readout_disagreements]
    if abs(accs[R_LIVE] - LANDED_LIVE) > LANDED_TOL or abs(accs[R_BASE] - LANDED_BASE) > LANDED_TOL:
        return "INSTRUMENTATION_SUSPECT_BASELINE_DRIFT", [
            "R_LIVE=%.4f (want %.4f+/-%.2f) R_BASE=%.4f (want %.4f+/-%.2f): the harness changed, "
            "not the hypothesis" % (accs[R_LIVE], LANDED_LIVE, LANDED_TOL,
                                    accs[R_BASE], LANDED_BASE, LANDED_TOL)]
    for k, v in sorted(self_retrieval.items()):
        if v < GP.SELF_RETRIEVAL_FLOOR:
            return "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR", [
                "SELF_RETRIEVAL(%s)=%.4f < %.2f" % (k, v, GP.SELF_RETRIEVAL_FLOOR)]
    if accs[F_LOCAL_SCRAM] > FLOOR_MAX:
        return "HARD_FAIL_FLOOR_BREACH", [
            "F_LOCAL_SCRAM=%.4f > %.2f" % (accs[F_LOCAL_SCRAM], FLOOR_MAX)]
    if d["delta"] < 0.0 and d["ci_excludes_zero"]:
        return "HARD_FAIL_GAIN_HURTS", [
            "d(P_CONTROL-R_BASE)=%.4f CI=[%.4f,%.4f] excludes 0 and is NEGATIVE: suppressing shared "
            "dimensions destroys signal the comparator needs"
            % (d["delta"], d["ci_lo"], d["ci_hi"])]
    if not d["ci_excludes_zero"]:
        return "HARD_FAIL_GAIN_ADDS_NOTHING", [
            "d(P_CONTROL-R_BASE)=%.4f CI=[%.4f,%.4f] INCLUDES 0: audit row C4 is refuted on this task"
            % (d["delta"], d["ci_lo"], d["ci_hi"])]
    # the wrong-pool control OUTRANKS the pass (pre-reg sec 4)
    if d["delta"] >= HP_DELTA and not (dw["delta"] > 0 and dw["ci_excludes_zero"]):
        return "HARD_FAIL_GENERIC_NOT_TASK_LOCAL", [
            "d(P_CONTROL-R_BASE)=%.4f clears the band, but the WRONG-POOL control reproduces it "
            "(d(P_CONTROL-W_WRONGPOOL)=%.4f CI=[%.4f,%.4f]): the gain is a generic variance filter, "
            "not task-local control" % (d["delta"], dw["delta"], dw["ci_lo"], dw["ci_hi"])]
    hp = (d["delta"] >= HP_DELTA and d["ci_excludes_zero"]
          and dw["delta"] > 0 and dw["ci_excludes_zero"]
          and accs[F_LOCAL_SCRAM] <= FLOOR_MAX)
    if hp:
        if d["delta"] < HP_DELTA * (1.0 + STRICT_MARGIN_FRAC):
            return "MIDDLE_BAND_FLOOR_HUGGING", [
                "META_RULE_L: d=%.4f clears the %.4f floor by < 5%%"
                % (d["delta"], HP_DELTA * (1.0 + STRICT_MARGIN_FRAC))]
        return "HARD_PASS", [
            "d(P_CONTROL-R_BASE)=%.4f CI=[%.4f,%.4f] clears +%.2f strictly above floor; the "
            "wrong-pool control does NOT reproduce it (d=%.4f CI=[%.4f,%.4f]); scrambled floor "
            "%.4f" % (d["delta"], d["ci_lo"], d["ci_hi"], HP_DELTA, dw["delta"], dw["ci_lo"],
                      dw["ci_hi"], accs[F_LOCAL_SCRAM])]
    return "MIDDLE_BAND_REAL_BUT_SMALL", [
        "d(P_CONTROL-R_BASE)=%.4f CI=[%.4f,%.4f] excludes 0 but is below +%.2f"
        % (d["delta"], d["ci_lo"], d["ci_hi"], HP_DELTA)]


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}

    # S1 -- the gain is SYMMETRIC in the two candidates, so it cannot leak the answer.
    rng = np.random.default_rng(11)
    at, ad = rng.normal(size=16), rng.normal(size=16)
    g1 = 1.0 / (0.5 + (np.abs(at) + np.abs(ad)))
    g2 = 1.0 / (0.5 + (np.abs(ad) + np.abs(at)))
    assert np.array_equal(g1, g2), ("the gain is not BITWISE symmetric in the candidates: "
                                    "an asymmetric gain can encode which one is the target")
    # and the DECISION must be invariant to swapping the two candidates
    A_ = np.stack([rng.normal(size=16), rng.normal(size=16)])
    Q_ = rng.normal(size=(1, 16))
    c1, _ = score_gain_arm([{"target": "a", "distractor": "b"}], {"a": 0, "b": 1},
                           A_, Q_, "local", 0.5)
    c2, _ = score_gain_arm([{"target": "b", "distractor": "a"}], {"a": 0, "b": 1},
                           A_, Q_, "local", 0.5)
    assert bool(c1[0]) != bool(c2[0]), ("swapping target and distractor did not flip the "
                                        "verdict: the arm is not scoring the pair")
    res["gain_symmetric"] = True

    # S2 -- the gain does what it is claimed to do: SUPPRESS shared dimensions, PRESERVE
    #       dimensions where only one candidate is active. This is the mechanism, asserted.
    shared = np.array([10.0, 10.0, 0.2, 0.0])
    distinct = np.array([10.0, 10.0, 0.0, 5.0])
    g = 1.0 / (1.0 + np.abs(shared) + np.abs(distinct))
    assert g[0] < g[3], "the pool gain does not suppress a shared dimension relative to a distinctive one"
    assert g[3] / g[0] > 3.0, "the suppression ratio is negligible (%.2f)" % (g[3] / g[0])
    res["gain_suppresses_shared"] = {"g_shared": round(float(g[0]), 4),
                                     "g_distinctive": round(float(g[3]), 4),
                                     "ratio": round(float(g[3] / g[0]), 3)}

    # S3 -- IMPLEMENTATION CORRECTNESS AND SENSITIVITY. Deliberately NOT a claim that the
    #       mechanism wins: synthetic pre-checks run before this cell did NOT favour it (see the
    #       note below), so a self-test asserting a win would be rigging the construction. What is
    #       asserted here is (a) the gained score is EXACTLY the hand-computed weighted cosine and
    #       (b) the arm is SENSITIVE -- it changes a non-trivial fraction of decisions relative to
    #       the ungained comparison. An arm that changes nothing cannot produce a result either way.
    #
    #       DISCLOSED PRIOR (honest, recorded before the run): on three synthetic constructions the
    #       control gain scored at or slightly below the plain comparison, and the DEMOTED
    #       pool-inverse gain scored clearly below it. I hold no expectation that the primary will
    #       pass. HARD_FAIL_GAIN_ADDS_NOTHING and HARD_FAIL_GAIN_HURTS are both live.
    d = 32
    r = np.random.default_rng(77)
    A_ = r.normal(size=(2, d))
    q = r.normal(size=d)
    g = np.abs(A_[0] - A_[1])
    g = g / float(g.mean())
    st_hand = float((q * g) @ (A_[0] * g)
                    / (np.linalg.norm(q * g) * np.linalg.norm(A_[0] * g)))
    sd_hand = float((q * g) @ (A_[1] * g)
                    / (np.linalg.norm(q * g) * np.linalg.norm(A_[1] * g)))
    got, _dg = score_gain_arm([{"target": "a", "distractor": "b"}], {"a": 0, "b": 1},
                              A_, q[None, :], "diff", 1.0)
    assert bool(got[0]) == bool(st_hand > sd_hand), \
        "the gained arm does not implement the hand-computed weighted cosine"
    # the gain must put its weight where the two anchors DIFFER (that is the whole mechanism)
    hi = int(np.argmax(np.abs(A_[0] - A_[1])))
    lo = int(np.argmin(np.abs(A_[0] - A_[1])))
    assert g[hi] > g[lo], "the control gain is not weighting the dimensions that differ"

    # sensitivity: over random pairs, the gained arm must disagree with the plain arm sometimes
    n = 400
    A2 = np.random.default_rng(5).normal(size=(2 * n, 16))
    Q2 = np.random.default_rng(6).normal(size=(n, 16))
    it2 = [{"target": "t%d" % i, "distractor": "d%d" % i} for i in range(n)]
    wp2 = {}
    for i in range(n):
        wp2["t%d" % i] = 2 * i
        wp2["d%d" % i] = 2 * i + 1
    c_gain, _ = score_gain_arm(it2, wp2, A2, Q2, "diff", 1.0)
    c_plain, _ = P1.score_arm(it2, wp2, A2, Q2)
    frac_changed = float((c_gain != c_plain).mean())
    assert 0.01 < frac_changed < 0.99, (
        "the gained arm changed %.3f of decisions -- outside (0.01, 0.99), so it is either inert "
        "or a different task" % frac_changed)
    res["implementation_and_sensitivity"] = {
        "matches_hand_weighted_cosine": True,
        "frac_decisions_changed_vs_plain": round(frac_changed, 4),
        "disclosed_prior": "synthetic pre-checks did NOT favour the primary; no expectation of a "
                           "pass is held, and both HARD_FAIL directions are live"}

    # S4 -- the WRONG-POOL control actually differs from the real one (a control that cannot
    #       differ is not a control).
    items = [{"target": "a", "distractor": "b"}, {"target": "c", "distractor": "d"}]
    wpos = {"a": 0, "b": 1, "c": 2, "d": 3}
    r = np.random.default_rng(3)
    A_ = r.normal(size=(4, 32))
    Q_ = r.normal(size=(2, 32))
    sig = 1.0
    _cl, dl = score_gain_arm(items, wpos, A_, Q_, "local", sig)
    _cw, dw = score_gain_arm(items, wpos, A_, Q_, "wrong", sig, donors=[1, 0])
    gl = 1.0 / (sig + np.abs(A_[0]) + np.abs(A_[1]))
    gw = 1.0 / (sig + np.abs(A_[2]) + np.abs(A_[3]))
    assert not np.allclose(gl, gw), "the wrong-pool gain equals the real one"
    res["wrongpool_differs"] = True

    # S5 -- every verdict branch reachable.
    def _mk(dd, dwv, exd=True, exw=True):
        def c(v, e):
            return {"delta": v, "ci_lo": v - 0.01 if e else -abs(v) - 0.01, "ci_hi": v + 0.01,
                    "ci_excludes_zero": e}
        return {"deltas": {"d_PCONTROL_minus_RBASE": c(dd, exd),
                           "d_PCONTROL_minus_WRONGPOOL": c(dwv, exw)}}
    ok = {R_LIVE: LANDED_LIVE, R_BASE: LANDED_BASE, F_LOCAL_SCRAM: 0.50}
    sr = {R_BASE: 0.90}
    seen = sorted({
        decide_verdict(_mk(0.08, 0.06), ok, 0, sr)[0],
        decide_verdict(_mk(0.0305, 0.06), ok, 0, sr)[0],
        decide_verdict(_mk(0.02, 0.02), ok, 0, sr)[0],
        decide_verdict(_mk(0.00, 0.00, exd=False), ok, 0, sr)[0],
        decide_verdict(_mk(-0.05, 0.00), ok, 0, sr)[0],
        decide_verdict(_mk(0.08, 0.00, exw=False), ok, 0, sr)[0],
        decide_verdict(_mk(0.08, 0.06), {R_LIVE: LANDED_LIVE, R_BASE: LANDED_BASE,
                                         F_LOCAL_SCRAM: 0.80}, 0, sr)[0],
        decide_verdict(_mk(0.08, 0.06), {R_LIVE: 0.40, R_BASE: LANDED_BASE,
                                         F_LOCAL_SCRAM: 0.50}, 0, sr)[0],
        decide_verdict(_mk(0.08, 0.06), ok, 5, sr)[0],
        decide_verdict(_mk(0.08, 0.06), ok, 0, {R_BASE: 0.1})[0]})
    want = sorted(["HARD_PASS", "MIDDLE_BAND_FLOOR_HUGGING", "MIDDLE_BAND_REAL_BUT_SMALL",
                   "HARD_FAIL_GAIN_ADDS_NOTHING", "HARD_FAIL_GAIN_HURTS",
                   "HARD_FAIL_GENERIC_NOT_TASK_LOCAL", "HARD_FAIL_FLOOR_BREACH",
                   "INSTRUMENTATION_SUSPECT_BASELINE_DRIFT", "INSTRUMENTATION_SUSPECT_READOUT_FORK",
                   "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["verdict_branches_reachable"] = seen

    # S6 -- the predecessors are the real ones.
    assert P1.PREREG_COMMIT == "d6c56353c" and GP.PREREG_COMMIT == "42792834c"
    res["predecessors"] = {"parent": P1.ANCHOR_NAME, "grandparent": GP.ANCHOR_NAME}

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def _build_field(words_used, profile_pool, d, output_dir, t0, want_space):
    """Graded + signed anchor sums at dimensionality `d`, one pass. Returns
    (sum_S, sum_G, qmu_S, qsd_S, qmu_G, qsd_G, space_or_None, n_prof)."""
    nw = len(words_used)
    sum_S = np.zeros((nw, d), dtype=np.float64)
    sum_G = np.zeros((nw, d), dtype=np.float64)
    s1 = np.zeros(d); s2 = np.zeros(d); g1 = np.zeros(d); g2 = np.zeros(d)
    n_prof = 0
    space = ConceptSpace(d=d) if want_space else None
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            vs = P1._signed(sent, drop, d)
            vg = P1._graded(sent, drop, d)
            sum_S[i] += vs
            sum_G[i] += vg
            s1 += vs; s2 += vs * vs; g1 += vg; g2 += vg * vg
            n_prof += 1
            if space is not None:
                space.observe(w, context_vector_masked(sent, w))
        if (i + 1) % 250 == 0:
            _heartbeat(output_dir, "anchors_d%d" % d, i + 1, nw, time.time() - t0)
    m = max(1, n_prof)
    qmu_S, qmu_G = s1 / m, g1 / m
    qsd_S = np.sqrt(np.maximum(s2 / m - qmu_S ** 2, 0.0))
    qsd_G = np.sqrt(np.maximum(g2 / m - qmu_G ** 2, 0.0))
    return sum_S, sum_G, qmu_S, qsd_S, qmu_G, qsd_G, space, n_prof


def _queries(items, donors, d):
    qg = np.zeros((len(items), d)); qs = np.zeros((len(items), d))
    sg = np.zeros((len(items), d)); ss = np.zeros((len(items), d))
    for i, it in enumerate(items):
        drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                          it["target"], it["distractor"]})
        qg[i] = P1._graded(it["sentence"], drop, d)
        qs[i] = P1._signed(it["sentence"], drop, d)
        dj = items[donors[i]]
        dd = drop | frozenset({normalize_lemma(dj["target"]), normalize_lemma(dj["distractor"]),
                               dj["target"], dj["distractor"]})
        sg[i] = P1._graded(dj["sentence"], dd, d)
        ss[i] = P1._signed(dj["sentence"], dd, d)
    return qg, qs, sg, ss


def run(run_mode: str, output_dir: str, max_items: int) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode, len(ARMS))
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000

    assets = GP.build_corpus_assets()
    counts = assets["counts"]
    profile_pool, eval_pool = GP.split_pools(assets["buckets"])
    items, item_diag = GP.build_items(assets["pairs_strict"], eval_pool, max_items)
    n = len(items)
    print("[items] n=%d" % n, flush=True)
    if run_mode == "full" and n < MIN_ITEMS:
        m = {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "verdict_msg": "only %d items" % n,
             "summary": "item gate stopped the run", "elapsed_s": round(time.time() - t0, 3),
             "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "n_items": n,
             "ts_iso": datetime.now(timezone.utc).isoformat()}
        _atomic_write_metrics(output_dir, m)
        return m

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    nw = len(words_used)
    donors = GP.assign_donors(items)

    sum_S, sum_G, qmu_S, qsd_S, qmu_G, qsd_G, space, n_prof = _build_field(
        words_used, profile_pool, CTX_D, output_dir, t0, True)
    print("[space] anchors=%d profile_sentences=%d (%.1fs)" % (nw, n_prof, time.time() - t0),
          flush=True)

    A_SS = np.stack([P1._sign_anchor(sum_S[i]) for i in range(nw)])
    hd_anchors, hd_mat = space.anchor_matrix()
    assert hd_anchors == words_used, "anchor order drifted"
    anchor_identical = bool(np.array_equal(A_SS, hd_mat))
    assert anchor_identical, "A_SS is not hdlab's own anchor matrix -- the cell is a fork"

    qg, qs, sg, ss = _queries(items, donors, CTX_D)

    # R_BASE representation = the predecessor's A_GGZ: graded field + graded query, both
    # normalised against their own population pool.
    A_GGZ = P1._normalise(sum_G, sum_G.mean(axis=0), sum_G.std(axis=0), "Z")
    Q_GGZ = P1._normalise(qg, qmu_G, qsd_G, "Z")
    S_GGZ = P1._normalise(sg, qmu_G, qsd_G, "Z")
    A_SSN, Q_SSN = A_SS, qs

    sigma = pool_sigma(A_GGZ, items, wpos)
    print("[sigma] pre-registered sigma = mean pool = %.6f" % sigma, flush=True)

    correct: Dict[str, np.ndarray] = {}
    diag: Dict[str, dict] = {}
    correct[R_LIVE], diag[R_LIVE] = P1.score_arm(items, wpos, A_SSN, Q_SSN)
    correct[R_BASE], diag[R_BASE] = P1.score_arm(items, wpos, A_GGZ, Q_GGZ)
    correct[P_CONTROL], diag[P_CONTROL] = score_gain_arm(
        items, wpos, A_GGZ, Q_GGZ, "diff", sigma)
    correct[P_LOCAL], diag[P_LOCAL] = score_gain_arm(items, wpos, A_GGZ, Q_GGZ, "local", sigma)
    correct[W_WRONGPOOL], diag[W_WRONGPOOL] = score_gain_arm(
        items, wpos, A_GGZ, Q_GGZ, "wrong", sigma, donors=donors)
    correct[F_LOCAL_SCRAM], diag[F_LOCAL_SCRAM] = score_gain_arm(
        items, wpos, A_GGZ, S_GGZ, "diff", sigma)
    correct[F_BASE_SCRAM], diag[F_BASE_SCRAM] = P1.score_arm(items, wpos, A_GGZ, S_GGZ)
    correct[B_FREQ], diag[B_FREQ] = P1.arm_frequency(
        items, counts, np.random.default_rng(MASTER_SEED + 4))
    accs = {k: round(float(correct[k].mean()), 6) for k in ARMS}
    print("[arms] %s" % json.dumps(accs), flush=True)

    # non-fork control: read-out agreement with hdlab on the LIVE arm
    n_disagree = 0
    for i, it in enumerate(items):
        msk = np.zeros(nw, dtype=bool)
        msk[wpos[it["target"]]] = True
        msk[wpos[it["distractor"]]] = True
        pick, _c = canonicalize_fast("__slot__", Q_SSN[i], space, thresh=-1.0, eligible_mask=msk)
        if bool(pick == it["target"]) != bool(correct[R_LIVE][i]):
            n_disagree += 1
    print("[control] read-out disagreements: %d/%d" % (n_disagree, n), flush=True)

    # positive control: self-retrieval on R_BASE
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    n_sr = min(300, nw)
    sr_words = [words_used[int(i)] for i in np.sort(rng_sr.choice(nw, size=n_sr, replace=False))]
    hits, tot = 0, 0
    for w in sr_words:
        sents = profile_pool.get(w, [])
        if not sents:
            continue
        other = words_used[int(rng_sr.integers(nw))]
        while other == w:
            other = words_used[int(rng_sr.integers(nw))]
        q = P1._graded(sents[0], frozenset({w, other, normalize_lemma(w), normalize_lemma(other)}),
                       CTX_D)
        q = P1._normalise(q[None, :], qmu_G, qsd_G, "Z")[0]
        s = P1._cos_rows(q, A_GGZ[np.array([wpos[w], wpos[other]])])
        hits += int(s[0] > s[1] or (s[0] == s[1] and w < other))
        tot += 1
    self_retrieval = {R_BASE: round(hits / max(1, tot), 4)}
    print("[positive-control] self_retrieval %s" % json.dumps(self_retrieval), flush=True)

    # ---- SECONDARY: sigma sensitivity (NO VERDICT WEIGHT) --------------------------------------
    sigma_sweep = {}
    for f in SIGMA_SWEEP:
        c, _d = score_gain_arm(items, wpos, A_GGZ, Q_GGZ, "local", sigma * f)
        sigma_sweep["sigma_x%.2f" % f] = round(float(c.mean()), 6)
    print("[secondary] sigma sweep %s" % json.dumps(sigma_sweep), flush=True)

    # ---- SECONDARY: far-distractor (NO VERDICT WEIGHT) ------------------------------------------
    sib = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    rng_far = np.random.default_rng(MASTER_SEED + 11)
    far_items: List[dict] = []
    far_qidx: List[int] = []
    for i, it in enumerate(items):
        c = words_used[int(rng_far.integers(nw))]
        tries = 0
        while tries < 20 and (c == it["target"] or c in sib[it["target"]]
                              or GP._is_variant(c, it["target"])):
            c = words_used[int(rng_far.integers(nw))]
            tries += 1
        if c == it["target"] or c in sib[it["target"]]:
            continue
        far_items.append({"target": it["target"], "distractor": c})
        far_qidx.append(i)                     # keeps the query aligned with its own sentence
    far = {}
    if far_items:
        Qf = Q_GGZ[np.array(far_qidx, dtype=np.int64)]
        cb, _ = P1.score_arm(far_items, wpos, A_GGZ, Qf)
        cg, _ = score_gain_arm(far_items, wpos, A_GGZ, Qf, "diff", sigma)
        far = {R_BASE: round(float(cb.mean()), 4), P_CONTROL: round(float(cg.mean()), 4),
               "n": len(far_items)}
    print("[secondary] far-distractor %s" % json.dumps(far), flush=True)

    # ---- SECONDARY: FAIR-TEST capacity diagnostic at higher d (NO VERDICT WEIGHT) --------------
    d_sweep = {"d256": {R_BASE: accs[R_BASE], P_CONTROL: accs[P_CONTROL]}}
    if run_mode == "full":
        P1._WORD_VEC.clear()               # the d=256 draws are no longer needed
        for dd in D_SWEEP:
            t1 = time.time()
            s_S, s_G, _m1, _s1, m2, s2v, _sp, _np2 = _build_field(
                words_used, profile_pool, dd, output_dir, t0, False)
            qg2, _qs2, _sg2, _ss2 = _queries(items, donors, dd)
            A2 = P1._normalise(s_G, s_G.mean(axis=0), s_G.std(axis=0), "Z")
            Q2 = P1._normalise(qg2, m2, s2v, "Z")
            cb, _ = P1.score_arm(items, wpos, A2, Q2)
            sg2v = pool_sigma(A2, items, wpos)
            cg, _ = score_gain_arm(items, wpos, A2, Q2, "diff", sg2v)
            d_sweep["d%d" % dd] = {R_BASE: round(float(cb.mean()), 6),
                                   P_CONTROL: round(float(cg.mean()), 6),
                                   "elapsed_s": round(time.time() - t1, 1)}
            print("[secondary] d=%d %s" % (dd, json.dumps(d_sweep["d%d" % dd])), flush=True)
            P1._WORD_VEC.clear()
    print("[secondary] d sweep %s" % json.dumps(d_sweep), flush=True)

    # ---- bootstrap -------------------------------------------------------------------------------
    contrasts = [("d_PCONTROL_minus_RBASE", P_CONTROL, R_BASE),
                 ("d_PCONTROL_minus_WRONGPOOL", P_CONTROL, W_WRONGPOOL),
                 ("d_PCONTROL_minus_RLIVE", P_CONTROL, R_LIVE),
                 ("d_PCONTROL_minus_CHANCE", P_CONTROL, "__CHANCE__"),
                 ("d_PCONTROL_minus_SCRAM", P_CONTROL, F_LOCAL_SCRAM),
                 ("d_PLOCAL_minus_RBASE_DEMOTED", P_LOCAL, R_BASE),
                 ("d_WRONGPOOL_minus_RBASE", W_WRONGPOOL, R_BASE),
                 ("d_RBASE_minus_RLIVE", R_BASE, R_LIVE)]
    bs = P1.paired_bootstrap(correct, ARMS, n_boot, BOOTSTRAP_SEED, contrasts)
    tw = sorted({it["target"] for it in items})
    twi = {w: i for i, w in enumerate(tw)}
    clusters = np.array([twi[it["target"]] for it in items], dtype=np.int64)
    bs_cluster = P1.paired_bootstrap(correct, ARMS, min(n_boot, 2000), BOOTSTRAP_SEED + 1,
                                     contrasts[:3], clusters)

    digests = {k: hashlib.sha256(correct[k].tobytes()).hexdigest() for k in ARMS}
    if digests[P_CONTROL] == digests[R_BASE]:
        raise AssertionError("META_RULE_AF: P_CONTROL and R_BASE are bit-identical")

    done = completed_units(output_dir)
    for k in ARMS:
        key = unit_key(ANCHOR_NAME, run_mode, str(n), k)
        if key not in done:
            record_unit(output_dir, key, {"arm": k, "acc": accs[k], "n": n, "digest": digests[k]})
    units = load_units(output_dir)
    cardinality_ok = len(units) >= len(ARMS)

    verdict, notes = decide_verdict(bs, accs, n_disagree, self_retrieval)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    d = bs["deltas"]["d_PCONTROL_minus_RBASE"]
    dw = bs["deltas"]["d_PCONTROL_minus_WRONGPOOL"]
    msg = ("n=%d | R_LIVE=%.4f R_BASE=%.4f P_CONTROL=%.4f | d(P_CONTROL-R_BASE)=%.4f "
           "CI=[%.4f,%.4f] | WRONGPOOL=%.4f d=%.4f CI=[%.4f,%.4f] | P_LOCAL(demoted)=%.4f | "
           "floors: F_LOCAL_SCRAM=%.4f "
           "F_BASE_SCRAM=%.4f FREQ=%.4f | readout_disagreements=%d | %s"
           % (n, accs[R_LIVE], accs[R_BASE], accs[P_CONTROL], d["delta"], d["ci_lo"],
              d["ci_hi"], accs[W_WRONGPOOL], dw["delta"], dw["ci_lo"], dw["ci_hi"],
              accs[P_LOCAL],
              accs[F_LOCAL_SCRAM], accs[F_BASE_SCRAM], accs[B_FREQ], n_disagree, "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "is the brain's normalisation POOL (the concurrently active candidates) what "
                   "the predecessor's global-field pool got wrong? task-local divisive "
                   "normalisation == semantic-control gain == distinctive-feature privileging",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "amendment": AMENDMENT_PATH, "amendment_commit": AMENDMENT_COMMIT,
        "parent_cell": P1.ANCHOR_NAME, "grandparent_cell": GP.ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "hdlab_modified": False,
        "n_items": n, "n_anchors": nw, "chance": CHANCE,
        "arm_accuracy": accs,
        "arm_labels": {
            R_LIVE: "fully quantised live comparator (reference; must reproduce 0.6395)",
            R_BASE: "predecessor HARD_PASS arm A_GGZ (baseline; must reproduce 0.6997)",
            P_CONTROL: "AMENDMENT A1 PRE-DESIGNATED PRIMARY: semantic control gain "
                       "g = |a_t - a_d| / mean(|a_t - a_d|); no free parameter",
            P_LOCAL: "DEMOTED by AMENDMENT A1, NO VERDICT WEIGHT, still scored because the "
                     "base pre-reg predicted it would win: g = 1/(sigma + |a_t| + |a_d|). "
                     "Registered prediction: at or below R_BASE (it up-weights "
                     "jointly-low-evidence dimensions)",
            W_WRONGPOOL: "THE DECISIVE CONTROL: the same |a-b| gain from a DIFFERENT pair",
            F_LOCAL_SCRAM: "P_LOCAL with another item's real sentence as the query (floor)",
            F_BASE_SCRAM: "R_BASE scrambled (floor)", B_FREQ: "corpus-frequency baseline"},
        "HP_SCOPE": {P_CONTROL: ["d_PCONTROL_minus_RBASE", "wrongpool_control", "floor"],
                     "P_LOCAL_and_all_secondaries": "NO VERDICT WEIGHT"},
        "bands": {"HARD_PASS_delta": HP_DELTA, "floor_max": FLOOR_MAX,
                  "landed_live": LANDED_LIVE, "landed_base": LANDED_BASE, "tol": LANDED_TOL,
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},
        "sigma": {"value": round(float(sigma), 6),
                  "definition": "mean of pool_j = |a_j|+|b_j| over ALL dimensions and ALL items; "
                                "derived from the field, never tuned"},
        "bootstrap_item": bs, "bootstrap_cluster_by_target_word": bs_cluster,
        "verdict_notes": notes,
        "secondary_no_verdict_weight": {
            "sigma_sweep": sigma_sweep, "far_distractor": far, "d_sweep": d_sweep,
            "d_sweep_purpose": "FAIR-TEST diagnostic: a null for the task-local pool would be "
                               "uninterpretable if random-indexing crosstalk at d=256 is the "
                               "dominant limiter. Decides nothing here; informs the next cell."},
        "non_fork_controls": {
            "anchor_matrix_byte_identical_to_hdlab_ConceptSpace": anchor_identical,
            "readout_disagreements_with_canonicalize_fast_on_LIVE": n_disagree},
        "positive_control_self_retrieval": {"values": self_retrieval,
                                            "floor": GP.SELF_RETRIEVAL_FLOOR},
        "arm_diagnostics": diag, "arm_digests": digests,
        "arms_differ_verified": digests[P_CONTROL] != digests[R_BASE],
        "item_construction": item_diag,
        "organs_reused": {
            "items_leak_controls_split_donors": GP.ANCHOR_NAME,
            "encoders_normalisation_readout_bootstrap": P1.ANCHOR_NAME,
            "anchor_accumulator_control": "hdlab.reading_grounding_loop.ConceptSpace",
            "readout_control": "hdlab.reading_grounding_loop.canonicalize_fast"},
        "n_units": len(units), "expected_n_units": len(ARMS), "cardinality_ok": cardinality_ok,
        "crlb": {"crlb_floor_computed": round(float(1.96 * np.sqrt(0.5 / max(n, 1))), 6),
                 "discriminator_reachability": bool(1.96 * np.sqrt(0.5 / max(n, 1)) < HP_DELTA),
                 "discriminator_range_by_construction": "2AFC accuracy, chance 0.50, nothing "
                                                        "hand-scored"},
        "compute_architecture": "sequential-CPU; thread pins before numpy import",
        "selftest": _SELFTEST_RESULT,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for k in SMOKE_ITEM_SCALES:
            out = OUT_SMOKE + "_n%d" % k
            print("=== SMOKE at max_items=%d -> %s ===" % (k, out), flush=True)
            m = run("smoke", out, k)
            a = m["arm_accuracy"]
            if len(sorted(set(round(v, 6) for v in a.values()))) == 1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: all arms identical at %d" % k)
            for arm in (R_LIVE, R_BASE, P_CONTROL):
                if a[arm] in (0.0, 1.0):
                    raise AssertionError("INSTRUMENTATION_SUSPECT: %s pinned at %r" % (arm, a[arm]))
            if not m["non_fork_controls"]["anchor_matrix_byte_identical_to_hdlab_ConceptSpace"]:
                raise AssertionError("BLOCK_DISPATCH: anchor matrix is not hdlab's")
            if m["non_fork_controls"]["readout_disagreements_with_canonicalize_fast_on_LIVE"] != 0:
                raise AssertionError("BLOCK_DISPATCH: read-out disagrees with canonicalize_fast")
            if not m["arms_differ_verified"]:
                raise AssertionError("META_RULE_AF failed at %d" % k)
            print("[smoke] n%d OK: R_BASE=%.4f P_CONTROL=%.4f P_LOCAL=%.4f WRONG=%.4f "
                  "SCRAM=%.4f" % (k, a[R_BASE], a[P_CONTROL], a[P_LOCAL], a[W_WRONGPOOL],
                                  a[F_LOCAL_SCRAM]), flush=True)
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.max_items)


_SELFTEST_RESULT = _instrumentation_selftest()

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
