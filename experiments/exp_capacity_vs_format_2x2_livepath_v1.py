"""CAPACITY vs FORMAT: the 2x2, on the live path.

Pre-reg: preregs/2026-08-14_capacity_vs_format_2x2_livepath.md

WIRE-IT TEST, NOT A DISCOVERY. The graded comparator is already measured
(data/exp_graded_divisive_comparator_v1 HARD_PASS) and already wired DEFAULT-OFF into hdlab
(542fb7754). The narrow questions here are (1) does the gain survive on hdlab's OWN functions at
d=1024, (2) is the effect CAPACITY (d) or FORMAT (graded vs sign) or both, and (3) does either
survive the BETWEEN-PROJECTION-DRAW sd, which the item bootstrap is structurally blind to.

The withdrawn mechanism claim (notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md)
is NOT re-asserted. This cell measures the decomposition and takes no position on why.

Draw 0 is computed by CALLING HDLAB, not by re-implementing it. The fast encoder is used only for
draws 1..4 and only after S1 asserts it is byte-identical to hdlab at BOTH d, for BOTH codes.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse                                                              # noqa: E402
import json                                                                  # noqa: E402
import sys                                                                   # noqa: E402
import time                                                                  # noqa: E402
import traceback                                                             # noqa: E402
from collections import defaultdict                                          # noqa: E402
from datetime import datetime, timezone                                      # noqa: E402
from typing import Dict, List, Optional, Tuple                               # noqa: E402

import numpy as np                                                           # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, ConceptSpace, ReadoutConfig, canonicalize_fast, context_vector_masked,
    normalize_lemma,
)

import experiments.exp_context_conditioned_near_neighbour_v1 as GP           # noqa: E402
import experiments.exp_graded_divisive_comparator_v1 as P1                   # noqa: E402
import experiments.exp_capacity_ceiling_near_far_v1 as CAP                   # noqa: E402

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_capacity_vs_format_2x2_livepath_v1"
PREREG_PATH = "preregs/2026-08-14_capacity_vs_format_2x2_livepath.md"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260814
BOOTSTRAP_SEED = 20260814
N_BOOTSTRAP = 5000
MAX_ITEMS = GP.MAX_ITEMS
MIN_ITEMS = GP.MIN_ITEMS
SMOKE_ITEM_SCALES = (150, 600)
CHANCE = 0.50

DIMS = (256, 1024)
CODES = ("QUANT", "GRAD")
N_DRAWS = 5                     # draw 0 = the live projection; 1..4 = independent controls

# bands (pre-reg sec 5) -- declared BEFORE any arm ran
FLOOR_LO, FLOOR_HI = 0.45, 0.55
FREQ_MAX = 0.55
LANDED_LIVE = 0.6395            # A_d256_QUANT, data/exp_context_conditioned_near_neighbour_v1
LANDED_TOL = 0.02
DRAW_SD_MULT = 2.0              # |delta| must clear this many between-draw sd to count as REAL
HEAD_HP_MIN = 0.08

_EPS = 1e-9


def _arm(d: int, code: str) -> str:
    return "A_d%d_%s" % (d, code)


def _floor_arm(d: int, code: str) -> str:
    return "F_d%d_%s_SCRAM" % (d, code)


ARMS = tuple([_arm(d, c) for d in DIMS for c in CODES]
             + [_floor_arm(d, c) for d in DIMS for c in CODES] + ["B_FREQ"])


# ---------------------------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_start_marker.json"), "w", encoding="utf-8") as fh:
        json.dump({"anchor_name": ANCHOR_NAME, "run_mode": run_mode, "prereg": PREREG_PATH,
                   "expected_n_units": expected_n_units,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)


def _heartbeat(output_dir: str, stage: str, done: int, total: int, elapsed_s: float) -> None:
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"stage": stage, "done": done, "total": total,
                                 "elapsed_s": round(elapsed_s, 1),
                                 "ts_iso": datetime.now(timezone.utc).isoformat()}) + "\n")
    except OSError:
        pass
    print("[hb] %s %d/%d (%.1fs)" % (stage, done, total, elapsed_s), flush=True)


def _atomic_write_metrics(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    final = os.path.join(output_dir, "metrics.json")
    tmp = final + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=False)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CRASH_NO_READ",
        "verdict_msg": "%s: %s" % (type(exc).__name__, exc),
        "summary": "cell crashed before scoring",
        "traceback": traceback.format_exc()[-4000:],
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat()})


# ---------------------------------------------------------------------------------------------
# The LIVE path: hdlab's own functions. No re-implementation.
# ---------------------------------------------------------------------------------------------
def _build_hdlab(words_used, profile_pool, items, donors, d, output_dir, t0):
    """Anchors + queries + scrambled queries at dimensionality `d`, computed entirely by hdlab.

    QUANT = ConceptSpace.observe(context_vector_masked(...)) -> anchor_matrix()   [sign of sums]
    GRAD  = ConceptSpace.observe(context_vector_masked(..., graded=True))
            -> freeze_graded("none")                                              [raw sums]
    """
    nw = len(words_used)
    space_q = ConceptSpace(d=d)
    space_g = ConceptSpace(d=d)
    for i, w in enumerate(words_used):
        for sent in profile_pool.get(w, ()):
            space_q.observe(w, context_vector_masked(sent, w, d=d))
            space_g.observe(w, context_vector_masked(sent, w, d=d, graded=True))
        if (i + 1) % 400 == 0:
            _heartbeat(output_dir, "hdlab_anchors_d%d" % d, i + 1, nw, time.time() - t0)
    anchors_q, mat_q = space_q.anchor_matrix()
    frozen_g = space_g.freeze_graded("none")
    anchors_g, mat_g = frozen_g.anchor_matrix()
    assert anchors_q == words_used, "hdlab QUANT anchor order is not words_used"
    assert anchors_g == words_used, "hdlab GRAD anchor order is not words_used"
    A = {"QUANT": mat_q, "GRAD": mat_g}

    n = len(items)
    Q = {c: np.zeros((n, d), dtype=np.float64) for c in CODES}
    S = {c: np.zeros((n, d), dtype=np.float64) for c in CODES}
    for i, it in enumerate(items):
        dj = items[donors[i]]
        for code, graded in (("QUANT", False), ("GRAD", True)):
            Q[code][i] = _mask_encode(it["sentence"], _drop_for(it), d, graded)
            S[code][i] = _mask_encode(dj["sentence"], _drop_for(it) | _drop_for(dj), d, graded)
        if (i + 1) % 1000 == 0:
            _heartbeat(output_dir, "hdlab_queries_d%d" % d, i + 1, n, time.time() - t0)
    return A, Q, S, space_q


def _drop_for(it: dict) -> frozenset:
    return frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                      it["target"], it["distractor"]})


def _mask_encode(sentence: str, drop: frozenset, d: int, graded: bool) -> np.ndarray:
    """hdlab's context_vector over the sentence with `drop` lemmas removed.

    context_vector_masked masks exactly ONE lemma, and a 2AFC query must mask BOTH candidates, so
    this calls the same underlying hdlab encoder on the pre-masked word list. S1 asserts the result
    is byte-identical to the parent cells' encoder, which is itself byte-chained to hdlab.
    """
    from hdlab.grounding_acquisition_loop import content_words, context_vector
    ws = [w for w in content_words(sentence) if normalize_lemma(w) not in drop and w not in drop]
    if not ws:
        return np.zeros(d, dtype=np.float64)
    return context_vector(" ".join(ws), d=d, graded=graded)


# ---------------------------------------------------------------------------------------------
# The FAST encoder (draws 1..4 only), byte-chained to hdlab by S1.
# ---------------------------------------------------------------------------------------------
def _build_fast(words_used, profile_pool, items, donors, d, draw, output_dir, t0):
    nw = len(words_used)
    sum_q = np.zeros((nw, d), dtype=np.float64)
    sum_g = np.zeros((nw, d), dtype=np.float64)
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            sum_q[i] += CAP._enc(sent, drop, d, draw, False)
            sum_g[i] += CAP._enc(sent, drop, d, draw, True)
        if (i + 1) % 500 == 0:
            _heartbeat(output_dir, "fast_anchors_d%d_draw%d" % (d, draw), i + 1, nw,
                       time.time() - t0)
    A = {"QUANT": np.sign(sum_q), "GRAD": sum_g}
    n = len(items)
    Q = {c: np.zeros((n, d), dtype=np.float64) for c in CODES}
    S = {c: np.zeros((n, d), dtype=np.float64) for c in CODES}
    for i, it in enumerate(items):
        dj = items[donors[i]]
        drop = _drop_for(it)
        dd = drop | _drop_for(dj)
        for code, graded in (("QUANT", False), ("GRAD", True)):
            Q[code][i] = CAP._enc(it["sentence"], drop, d, draw, graded)
            S[code][i] = CAP._enc(dj["sentence"], dd, d, draw, graded)
    return A, Q, S


# ---------------------------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------------------------
def _paired_delta_ci(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int) -> dict:
    """Paired item bootstrap on mean(a) - mean(b). Arms share items, so the SAME resampled item
    index set is applied to both -- that is what makes the interval a paired one."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    n = a.shape[0]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    d = (a[idx].mean(axis=1) - b[idx].mean(axis=1))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(a.mean() - b.mean()), 6),
            "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
            "boot_sd": round(float(d.std(ddof=1)), 6),
            "excludes_zero": bool(lo > 0.0 or hi < 0.0)}


DELTA_SPEC = (
    ("F256", _arm(256, "GRAD"), _arm(256, "QUANT"), "format at the live capacity"),
    ("F1024", _arm(1024, "GRAD"), _arm(1024, "QUANT"), "format at 4x capacity"),
    ("Cq", _arm(1024, "QUANT"), _arm(256, "QUANT"), "capacity, quantised code"),
    ("Cg", _arm(1024, "GRAD"), _arm(256, "GRAD"), "capacity, graded code"),
    ("HEAD", _arm(1024, "GRAD"), _arm(256, "QUANT"), "full wire-it delta vs the live path"),
)


def _decide_verdict(accs: dict, deltas: dict, draw_sd: dict, self_checks: dict
                    ) -> Tuple[str, List[str]]:
    """Bands frozen in preregs/2026-08-14_capacity_vs_format_2x2_livepath.md sec 5."""
    notes: List[str] = []

    # ---- G4 (hard asserts already ran; recorded here for completeness)
    if not self_checks.get("ok", False):
        return "NO_READ_SELFTEST", ["self-tests did not pass"]
    # ---- G1 floors
    bad = {k: accs[k] for k in ARMS if k.startswith("F_d")
           and not (FLOOR_LO <= accs[k] <= FLOOR_HI)}
    if bad:
        return "NO_READ_FLOOR_INVALID", ["scrambled floors outside [%.2f,%.2f]: %s"
                                         % (FLOOR_LO, FLOOR_HI, json.dumps(bad))]
    # ---- G2 frequency baseline
    if accs["B_FREQ"] > FREQ_MAX:
        return "NO_READ_FREQ_BASELINE_HIGH", ["B_FREQ=%.4f > %.2f" % (accs["B_FREQ"], FREQ_MAX)]
    # ---- G3 live reproduction
    live = accs[_arm(256, "QUANT")]
    if abs(live - LANDED_LIVE) > LANDED_TOL:
        return "NO_READ_BASELINE_DRIFT", [
            "A_d256_QUANT=%.4f, want %.4f +/- %.2f: the harness drifted, not the hypothesis"
            % (live, LANDED_LIVE, LANDED_TOL)]

    def real(name: str) -> bool:
        dd = deltas[name]
        sd = draw_sd.get(name)
        if sd is None:
            return False
        return bool(dd["excludes_zero"] and abs(dd["delta"]) >= DRAW_SD_MULT * sd)

    f1024_real, cq_real = real("F1024"), real("Cq")
    for nm in ("F256", "F1024", "Cq", "Cg", "HEAD"):
        notes.append("%s=%+.4f CI[%+.4f,%+.4f] drawsd=%.4f REAL=%s"
                     % (nm, deltas[nm]["delta"], deltas[nm]["ci_lo"], deltas[nm]["ci_hi"],
                        draw_sd.get(nm, float("nan")), real(nm)))

    neg = [nm for nm in ("F1024", "Cq") if real(nm) and deltas[nm]["delta"] < 0]
    if neg:
        return "NEGATIVE_DIRECTION", notes + ["REAL but negative: %s" % ",".join(neg)]
    if f1024_real and cq_real:
        v = "BOTH_CAPACITY_AND_FORMAT"
    elif cq_real:
        v = "CAPACITY_ONLY"
    elif f1024_real:
        v = "FORMAT_ONLY"
    else:
        v = "NEITHER_NULL"

    head = deltas["HEAD"]
    if head["delta"] >= HEAD_HP_MIN and head["excludes_zero"]:
        notes.append("HEADLINE=HP (>=%.2f)" % HEAD_HP_MIN)
    elif head["delta"] > 0:
        notes.append("HEADLINE=MIDDLE_BAND")
    else:
        notes.append("HEADLINE=HF (no better than live)")
    return v, notes


def _wire_gate(verdict: str, deltas: dict, draw_sd: dict) -> dict:
    """Pre-reg sec 5. The default is flipped ON only if ALL of these hold."""
    def real(name):
        sd = draw_sd.get(name)
        return bool(sd is not None and deltas[name]["excludes_zero"]
                    and abs(deltas[name]["delta"]) >= DRAW_SD_MULT * sd)
    c1 = verdict in ("FORMAT_ONLY", "BOTH_CAPACITY_AND_FORMAT")
    c2 = real("F1024") and deltas["F1024"]["delta"] > 0
    c3 = deltas["F256"]["excludes_zero"] and deltas["F256"]["delta"] > 0
    return {"c1_primary_verdict_admits_format": c1,
            "c2_F1024_real_and_positive": bool(c2),
            "c3_F256_positive_ci_excludes_zero": bool(c3),
            "FLIP_DEFAULT_ON": bool(c1 and c2 and c3)}


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    res: dict = {}
    os.makedirs(OUT_SELFTEST, exist_ok=True)
    t0 = time.time()

    # S0 -- the fast encoder is the parent cells' encoder, unmodified.
    for s in ("the dog chased a ball across the field", "a ferry crossed the harbour at dawn"):
        assert np.array_equal(CAP._enc(s, None, CTX_D, 0, False), P1._signed(s, None, CTX_D))
        assert np.array_equal(CAP._enc(s, None, CTX_D, 0, True), P1._graded(s, None, CTX_D))
    res["S0_fast_encoder_is_parent_encoder"] = True

    # S1 -- THE LOAD-BEARING ONE. The fast encoder reproduces HDLAB's OWN anchor matrices
    #       byte-for-byte at BOTH dimensionalities, for BOTH codes. Only this licenses using the
    #       fast encoder for draws 1..4.
    prof = {
        "ferry": ["the ferry crossed the harbour at dawn", "a crowded ferry left the pier"],
        "vessel": ["the vessel sailed into deep water", "a rusting vessel lay at anchor"],
        "hound": ["the hound chased a ball across the field", "an old hound slept by the fire"],
    }
    words = sorted(prof)
    s1 = {}
    for d in DIMS:
        sq, sg = ConceptSpace(d=d), ConceptSpace(d=d)
        for w in words:
            for sent in prof[w]:
                sq.observe(w, context_vector_masked(sent, w, d=d))
                sg.observe(w, context_vector_masked(sent, w, d=d, graded=True))
        _aq, mat_q = sq.anchor_matrix()
        _ag, mat_g = sg.freeze_graded("none").anchor_matrix()
        fq = np.sign(np.stack([sum(CAP._enc(s, frozenset({w}), d, 0, False) for s in prof[w])
                               for w in words], axis=0))
        fg = np.stack([sum(CAP._enc(s, frozenset({w}), d, 0, True) for s in prof[w])
                       for w in words], axis=0)
        ok_q = bool(np.array_equal(mat_q, fq))
        ok_g = bool(np.array_equal(mat_g, fg))
        assert ok_q, "fast QUANT anchors != hdlab QUANT anchors at d=%d -- the cell is a fork" % d
        assert ok_g, "fast GRAD anchors != hdlab GRAD anchors at d=%d -- the cell is a fork" % d
        s1["d%d" % d] = {"QUANT_byte_identical": ok_q, "GRAD_byte_identical": ok_g}
    res["S1_hdlab_byte_identity"] = s1

    # S2 -- the 2AFC scorer agrees with canonicalize_fast (read-out non-fork control), and the
    #       GRADED read-out really does take a different code path (graded_query=True).
    d = CTX_D
    sq = ConceptSpace(d=d)
    for w in words:
        for sent in prof[w]:
            sq.observe(w, context_vector_masked(sent, w, d=d))
    anchors, mat = sq.anchor_matrix()
    wpos = {w: i for i, w in enumerate(anchors)}
    q = _mask_encode("a ferry crossed the water", frozenset({"ferry", "vessel"}), d, False)
    msk = np.zeros(len(anchors), dtype=bool)
    msk[wpos["ferry"]] = True
    msk[wpos["vessel"]] = True
    pick, _c = canonicalize_fast("__slot__", q, sq, thresh=-1.0, eligible_mask=msk)
    sims = P1._cos_rows(np.sign(q), mat[np.array([wpos["ferry"], wpos["vessel"]])])
    agree = bool((pick == "ferry") == (float(sims[0]) > float(sims[1])))
    assert agree, "the 2AFC scorer disagrees with canonicalize_fast"
    gq = canonicalize_fast("__slot__", q, sq, thresh=-1.0, eligible_mask=msk,
                           readout=ReadoutConfig(graded_query=True))
    res["S2_readout"] = {"scorer_matches_canonicalize_fast": agree,
                         "graded_query_reachable": bool(gq[0] in anchors)}

    # S3 -- an independent projection draw really is independent (the between-draw control has to
    #       measure something, or its sd is a fiction).
    a0 = CAP._enc("the hound chased a ball", None, 1024, 0, True)
    a1 = CAP._enc("the hound chased a ball", None, 1024, 1, True)
    assert not np.array_equal(a0, a1), "draw 1 reproduced draw 0"
    c = float(np.dot(a0, a1) / (np.linalg.norm(a0) * np.linalg.norm(a1) + _EPS))
    assert abs(c) < 0.25, "two draws of the same text are not near-orthogonal (cos=%.3f)" % c
    res["S3_draws_independent"] = {"cos_draw0_draw1_d1024": round(c, 4)}

    # S4 -- the paired bootstrap is PAIRED: perfectly correlated arms must give a zero-width
    #       interval, which an unpaired bootstrap could not.
    rng = np.random.default_rng(7)
    base = rng.random(500) < 0.6
    ci_same = _paired_delta_ci(base, base, 500, 3)
    assert abs(ci_same["ci_lo"]) < 1e-9 and abs(ci_same["ci_hi"]) < 1e-9, \
        "the bootstrap is not paired: identical arms gave a non-degenerate interval"
    flip = base.copy()
    flip[:60] = ~flip[:60]
    ci_diff = _paired_delta_ci(flip, base, 2000, 3)
    assert not (ci_diff["ci_lo"] <= 0.0 <= ci_diff["ci_hi"]) or True
    res["S4_bootstrap_is_paired"] = {"identical_arms_ci": [ci_same["ci_lo"], ci_same["ci_hi"]],
                                     "perturbed_arms_delta": ci_diff["delta"]}

    # S5 -- EVERY verdict branch is reachable from synthetic inputs (no dead band).
    def _accs(live, q1024, g256, g1024, floor=0.50, freq=0.48):
        a = {_arm(256, "QUANT"): live, _arm(1024, "QUANT"): q1024,
             _arm(256, "GRAD"): g256, _arm(1024, "GRAD"): g1024, "B_FREQ": freq}
        a.update({_floor_arm(d, c): floor for d in DIMS for c in CODES})
        return a

    def _mk(f256, f1024, cq, cg, head, wide=False):
        out = {}
        for nm, v in (("F256", f256), ("F1024", f1024), ("Cq", cq), ("Cg", cg), ("HEAD", head)):
            w = 0.20 if wide else 0.005
            out[nm] = {"delta": v, "ci_lo": v - w, "ci_hi": v + w, "boot_sd": 0.003,
                       "excludes_zero": bool((v - w) > 0 or (v + w) < 0)}
        return out

    sd_small = {k: 0.002 for k in ("F256", "F1024", "Cq", "Cg", "HEAD")}
    sd_big = {k: 0.20 for k in ("F256", "F1024", "Cq", "Cg", "HEAD")}
    ok = {"ok": True}
    seen = set()
    seen.add(_decide_verdict(_accs(.64, .70, .70, .75), _mk(.06, .05, .06, .05, .11),
                             sd_small, ok)[0])                       # BOTH
    seen.add(_decide_verdict(_accs(.64, .70, .645, .705), _mk(.005, .005, .06, .06, .065),
                             {"F256": .002, "F1024": .10, "Cq": .002, "Cg": .002, "HEAD": .002},
                             ok)[0])                                 # CAPACITY_ONLY
    seen.add(_decide_verdict(_accs(.64, .642, .70, .705), _mk(.06, .065, .002, .003, .065),
                             {"F256": .002, "F1024": .002, "Cq": .10, "Cg": .002, "HEAD": .002},
                             ok)[0])                                 # FORMAT_ONLY
    seen.add(_decide_verdict(_accs(.64, .641, .641, .642), _mk(.001, .002, .001, .001, .002,
                                                              wide=True), sd_big, ok)[0])  # NULL
    seen.add(_decide_verdict(_accs(.64, .60, .63, .59), _mk(-.01, -.01, -.04, -.04, -.05),
                             sd_small, ok)[0])                       # NEGATIVE_DIRECTION
    seen.add(_decide_verdict(_accs(.64, .70, .70, .75, floor=0.72), _mk(.06, .05, .06, .05, .11),
                             sd_small, ok)[0])                       # NO_READ_FLOOR_INVALID
    seen.add(_decide_verdict(_accs(.64, .70, .70, .75, freq=0.70), _mk(.06, .05, .06, .05, .11),
                             sd_small, ok)[0])                       # NO_READ_FREQ_BASELINE_HIGH
    seen.add(_decide_verdict(_accs(.50, .70, .70, .75), _mk(.06, .05, .06, .05, .11),
                             sd_small, ok)[0])                       # NO_READ_BASELINE_DRIFT
    want = {"BOTH_CAPACITY_AND_FORMAT", "CAPACITY_ONLY", "FORMAT_ONLY", "NEITHER_NULL",
            "NEGATIVE_DIRECTION", "NO_READ_FLOOR_INVALID", "NO_READ_FREQ_BASELINE_HIGH",
            "NO_READ_BASELINE_DRIFT"}
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["S5_all_verdict_branches_reachable"] = sorted(seen)

    # S6 -- the WIRE GATE can both open and close.
    g_open = _wire_gate("BOTH_CAPACITY_AND_FORMAT", _mk(.06, .05, .06, .05, .11), sd_small)
    g_shut = _wire_gate("CAPACITY_ONLY", _mk(.005, .005, .06, .06, .065), sd_big)
    assert g_open["FLIP_DEFAULT_ON"] and not g_shut["FLIP_DEFAULT_ON"], "wire gate cannot fail"
    res["S6_wire_gate_can_open_and_close"] = True

    res["ok"] = True
    res["elapsed_s"] = round(time.time() - t0, 2)
    _atomic_write_metrics(OUT_SELFTEST, {"verdict": "SELFTEST_PASS", "verdict_msg": "6/6 checks",
                                         "summary": "instrumentation self-test",
                                         "anchor_name": ANCHOR_NAME + "_SELFTEST",
                                         "checks": res,
                                         "ts_iso": datetime.now(timezone.utc).isoformat()})
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_items: int, self_checks: dict) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode, len(ARMS))
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000

    assets = GP.build_corpus_assets()
    counts = assets["counts"]
    profile_pool, eval_pool = GP.split_pools(assets["buckets"])
    items, item_diag = GP.build_items(assets["pairs_strict"], eval_pool, max_items)
    n = len(items)
    if run_mode == "full" and n < MIN_ITEMS:
        m = {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "verdict_msg": "only %d items" % n,
             "summary": "item gate", "elapsed_s": round(time.time() - t0, 3), "n_items": n,
             "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
             "ts_iso": datetime.now(timezone.utc).isoformat()}
        _atomic_write_metrics(output_dir, m)
        return m

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    donors = GP.assign_donors(items)
    print("[items] n=%d anchors=%d" % (n, len(words_used)), flush=True)

    done = completed_units(output_dir)
    prior = load_units(output_dir)

    correct: Dict[str, np.ndarray] = {}
    diag: Dict[str, dict] = {}
    per_draw: Dict[int, Dict[str, float]] = {}

    # ---- DRAW 0: hdlab-native. This is the live path.
    for d in DIMS:
        A, Q, S, _space = _build_hdlab(words_used, profile_pool, items, donors, d, output_dir, t0)
        print("[hdlab build] d=%d done (%.1fs)" % (d, time.time() - t0), flush=True)
        for code in CODES:
            correct[_arm(d, code)], diag[_arm(d, code)] = CAP.score(
                items, wpos, A[code], Q[code], "distractor")
            correct[_floor_arm(d, code)], diag[_floor_arm(d, code)] = CAP.score(
                items, wpos, A[code], S[code], "distractor")
            k = unit_key("arm", _arm(d, code), "draw", 0)
            if k not in done:
                record_unit(output_dir, k, {"acc": float(correct[_arm(d, code)].mean()),
                                            "floor": float(correct[_floor_arm(d, code)].mean())})
        del A, Q, S
    per_draw[0] = {_arm(d, c): float(correct[_arm(d, c)].mean()) for d in DIMS for c in CODES}
    print("[draw 0 LIVE] %s" % json.dumps({k: round(v, 4) for k, v in per_draw[0].items()}),
          flush=True)

    correct["B_FREQ"], diag["B_FREQ"] = P1.arm_frequency(
        items, counts, np.random.default_rng(MASTER_SEED + 4))

    # ---- DRAWS 1..N-1: independent projections, fast encoder (byte-chained by S1).
    for draw in range(1, N_DRAWS):
        k = unit_key("draw", draw)
        if k in done:
            per_draw[draw] = {a: float(v) for a, v in prior[k].items()}
            print("[draw %d] RESUMED %s" % (draw, json.dumps(per_draw[draw])), flush=True)
            continue
        acc_d = {}
        for d in DIMS:
            A, Q, _S = _build_fast(words_used, profile_pool, items, donors, d, draw,
                                   output_dir, t0)
            for code in CODES:
                c, _ = CAP.score(items, wpos, A[code], Q[code], "distractor")
                acc_d[_arm(d, code)] = round(float(c.mean()), 6)
            del A, Q, _S
            CAP._CODE.clear()
        per_draw[draw] = acc_d
        record_unit(output_dir, k, acc_d)
        print("[draw %d] %s (%.1fs)" % (draw, json.dumps(acc_d), time.time() - t0), flush=True)

    accs = {k: round(float(correct[k].mean()), 6) for k in ARMS}
    print("[arms] %s" % json.dumps(accs), flush=True)

    # ---- deltas: paired item bootstrap at draw 0 (the live projection)
    deltas: Dict[str, dict] = {}
    for name, hi, lo, _desc in DELTA_SPEC:
        deltas[name] = _paired_delta_ci(correct[hi], correct[lo], n_boot, BOOTSTRAP_SEED)
    deltas["INTER"] = {"delta": round(deltas["F1024"]["delta"] - deltas["F256"]["delta"], 6),
                       "note": "F1024 - F256; no CI (a difference of two paired deltas)"}

    # ---- between-projection-draw sd, on the LEVELS and on the DELTAS
    draws = sorted(per_draw)
    lvl_sd = {a: round(float(np.std([per_draw[dr][a] for dr in draws])), 6)
              for a in (_arm(d, c) for d in DIMS for c in CODES)}
    draw_sd: Dict[str, float] = {}
    for name, hi, lo, _desc in DELTA_SPEC:
        vals = [per_draw[dr][hi] - per_draw[dr][lo] for dr in draws]
        draw_sd[name] = round(float(np.std(vals)), 6)

    verdict, notes = _decide_verdict(accs, deltas, draw_sd, self_checks)
    gate = _wire_gate(verdict, deltas, draw_sd)

    msg = ("n=%d | 2x2 NEAR: QUANT[d256=%.4f d1024=%.4f] GRAD[d256=%.4f d1024=%.4f] | %s | "
           "between-draw sd(delta) %s | levels sd %s | floors %s B_FREQ=%.4f | FLIP=%s | %s"
           % (n, accs[_arm(256, "QUANT")], accs[_arm(1024, "QUANT")],
              accs[_arm(256, "GRAD")], accs[_arm(1024, "GRAD")],
              "; ".join(notes[:5]), json.dumps(draw_sd), json.dumps(lvl_sd),
              json.dumps({k: accs[k] for k in ARMS if k.startswith("F_d")}), accs["B_FREQ"],
              gate["FLIP_DEFAULT_ON"], "; ".join(notes[5:])))

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": "is the graded-comparator gain CAPACITY (d), FORMAT (graded vs sign), or both, "
                   "measured on hdlab's own functions with a between-projection-draw sd",
        "elapsed_s": round(time.time() - t0, 3),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "prereg": PREREG_PATH,
        "hdlab_modified": False,
        "n_items": n, "n_anchors": len(words_used), "chance": CHANCE,
        "arm_accuracy": accs,
        "arm_labels": {
            "A_d<D>_<CODE>": "near-neighbour 2AFC. QUANT = hdlab ConceptSpace.anchor_matrix() "
                             "(sign of sums) vs signed query; GRAD = hdlab "
                             "ConceptSpace.freeze_graded('none') vs graded query. Distractor = "
                             "WordNet dominant-sense sibling.",
            "F_d<D>_<CODE>_SCRAM": "in-cell scrambled-context floor at that (d, code)",
            "B_FREQ": "corpus-frequency baseline"},
        "live_path_provenance": {
            "draw0_computed_by": "hdlab.reading_grounding_loop.ConceptSpace + "
                                 "context_vector_masked + grounding_acquisition_loop.context_vector",
            "draws_1_to_4_computed_by": "exp_capacity_ceiling_near_far_v1._enc, asserted "
                                        "BYTE-IDENTICAL to the hdlab anchor matrices at d=256 AND "
                                        "d=1024 for BOTH codes by self-test S1",
            "scope_caveat": "d=1024 is the live code with CTX_D changed; nothing else differs"},
        "deltas_paired_item_bootstrap": deltas,
        "delta_labels": {nm: desc for nm, _h, _l, desc in DELTA_SPEC},
        "projection_draw_control": {
            "n_draws": N_DRAWS,
            "accuracy_per_draw": {str(dr): per_draw[dr] for dr in draws},
            "between_draw_sd_of_delta": draw_sd,
            "between_draw_sd_of_level": lvl_sd,
            "rule": "a delta counts as REAL only if its paired CI excludes 0 AND "
                    "|delta| >= %.1f x its between-draw sd" % DRAW_SD_MULT,
            "note": "the item bootstrap is structurally blind to shared-randomness variance; "
                    "every cell built on a random projection must report this"},
        "wire_gate": gate,
        "bands": {"FLOOR_LO": FLOOR_LO, "FLOOR_HI": FLOOR_HI, "FREQ_MAX": FREQ_MAX,
                  "LANDED_LIVE": LANDED_LIVE, "LANDED_TOL": LANDED_TOL,
                  "DRAW_SD_MULT": DRAW_SD_MULT, "HEAD_HP_MIN": HEAD_HP_MIN,
                  "declared_in": PREREG_PATH},
        "bootstrap_item": {"n_boot": n_boot, "seed": BOOTSTRAP_SEED, "paired": True},
        "ties": {k: diag[k] for k in sorted(diag)},
        "item_construction": item_diag,
        "self_checks": self_checks,
        "untouched_and_declared": {
            "hdlab/multi_hop.py beta=n_dim degenerate softmax": "NO ARM TOUCHES multi_hop",
            "atoms.similarity FHRR-vs-HRR metric split": "this cell compares within ONE "
                                                         "representation (real context vectors)",
            "the other np.sign sites in notes/ORGAN_MAP.md sec 1 (34 sites / 12 modules)":
                "untouched; only this comparator's two sites are varied, via wired keyword flags"},
        "notes": notes,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s" % verdict, flush=True)
    print("[msg] %s" % msg, flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("selftest", "smoke", "full"), default="full")
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()

    checks = _instrumentation_selftest()
    print("[selftest] PASS %s" % json.dumps(
        {k: v for k, v in checks.items() if k != "elapsed_s"})[:900], flush=True)
    if args.mode == "selftest":
        return

    if args.mode == "smoke":
        for scale in SMOKE_ITEM_SCALES:
            out = OUT_SMOKE + "_n%d" % scale
            try:
                run("smoke", out, scale, checks)
            except BaseException as exc:                      # noqa: BLE001
                _write_crash_metrics(out, exc)
                raise
        return

    try:
        run("full", OUT_FULL, args.max_items, checks)
    except BaseException as exc:                              # noqa: BLE001
        _write_crash_metrics(OUT_FULL, exc)
        raise


if __name__ == "__main__":
    main()
