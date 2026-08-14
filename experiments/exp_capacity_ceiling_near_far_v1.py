"""exp_capacity_ceiling_near_far_v1 -- at the capacity ceiling, does NEAR-NEIGHBOUR discrimination
still lag FAR-DISTRACTOR discrimination, or does the gap close?

PRE-REG: preregs/2026-08-14_capacity_ceiling_and_the_near_far_gap.md, COMMITTED (f1511ee8f) BEFORE
this file existed and BEFORE any arm was scored. Every arm, band and floor is frozen there.
HEAD ITEM set by notes/landed_vet_graded_comparator_mechanism_refuted_2026-08-14.md (f05b8a88a),
which promoted audit row C7 (representation format / capacity) from last place to first.

WHY THIS CELL EXISTS
MEASURED@data/exp_graded_divisive_comparator_v1/metrics.json: removing the comparator's quantisers
is worth +0.0602 at the live CTX_D=256.
MEASURED@the landed-VET: the UNMODIFIED quantised comparator at d=1024 scores 0.7030, BEATING the
graded one at d=256 (0.69975); the graded advantage shrinks 0.0602 -> 0.047 -> 0.041 across
d = 256 / 1024 / 4096.
MEASURED@data/exp_task_local_normalisation_pool_v1/metrics.json: every per-dimension REWEIGHTING
tried is null or harmful (log-IDF null, field z-scoring +0.0018, pool-inverse -0.011, contrast gain
-0.0220), while removing a per-dimension DESTRUCTION helped -- an estimation-noise/capacity story.
So the substrate is operating where random-projection crosstalk binds: unrelated codes sit at an
expected |cos| ~ 1/sqrt(256) = 0.0625, with 2377 concepts in that space.

THE UNMEASURED QUESTION: no FAR-distractor measurement exists above d=256. If 16x the capacity
closes the NEAR/FAR gap, the near-neighbour wall was substantially a d=256 artifact. If the gap
persists, a genuine semantic residual is isolated on a task with a working floor.

NOTHING UNDER hdlab/ IS MODIFIED BY THIS CELL.

ASCII-only.
"""
from __future__ import annotations

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
from hdlab.grounding_acquisition_loop import content_words                    # noqa: E402

import experiments.exp_context_conditioned_near_neighbour_v1 as GP           # noqa: E402
import experiments.exp_graded_divisive_comparator_v1 as P1                   # noqa: E402

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_capacity_ceiling_near_far_v1"
PREREG_PATH = "preregs/2026-08-14_capacity_ceiling_and_the_near_far_gap.md"
PREREG_COMMIT = "f1511ee8f"

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

DIMS = (256, 1024, 4096)
CODES = ("QUANT", "GRAD")
DISTRACTORS = ("NEAR", "FAR")
D_PRIMARY = 4096
N_DRAWS = 3                       # projection-draw control (pre-reg sec 6.6)

# bands (pre-reg sec 4)
HP_NEAR_MIN, HP_GAP_MAX = 0.80, 0.02
HF_NEAR_MAX, HF_GAP_MIN = 0.75, 0.04
DIM_MIN_GAIN = 0.02
FLOOR_MAX = 0.55
LANDED = {("256", "QUANT", "NEAR"): 0.6395, ("256", "GRAD", "NEAR"): 0.69975}
LANDED_TOL = 0.02
_EPS = 1e-9


def _arm(d, code, dist):
    return "A_d%d_%s_%s" % (d, code, dist)


def _floor_arm(d, code):
    return "F_d%d_%s_SCRAM" % (d, code)


ARMS = tuple([_arm(d, c, x) for d in DIMS for c in CODES for x in DISTRACTORS]
             + [_floor_arm(d, c) for d in DIMS for c in CODES] + ["B_FREQ"])


# ---------------------------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
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


def _heartbeat(output_dir, stage, done, total, elapsed_s):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage, "done": done,
           "total": total, "elapsed_s": round(elapsed_s, 3)}
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(output_dir, exc):
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0, "run_mode": "crash",
        "failure_class": type(exc).__name__, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# Encoders: identical math to P1, with a float32 code cache so d=4096 fits in memory.
# Bipolar +/-1 sums are EXACT in float32 up to 2^24, so this is lossless -- asserted, not assumed.
# ---------------------------------------------------------------------------------------------
_CODE: Dict[Tuple[str, int, int], np.ndarray] = {}


def _code(w: str, d: int, draw: int) -> np.ndarray:
    """The identical per-word bipolar draw hdlab uses, at draw 0. `draw` > 0 salts the seed to give
    an INDEPENDENT random-indexing projection (the projection-draw control)."""
    key = (w, d, draw)
    v = _CODE.get(key)
    if v is None:
        tag = w if draw == 0 else ("%s|draw%d" % (w, draw))
        seed = int.from_bytes(hashlib.sha256(tag.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d).astype(np.float32)
        _CODE[key] = v
    return v


def _enc(sentence: str, drop: Optional[frozenset], d: int, draw: int, graded: bool) -> np.ndarray:
    ws = content_words(sentence)
    if drop:
        ws = [w for w in ws if normalize_lemma(w) not in drop]
    if not ws:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in ws:
        acc += _code(w, d, draw)
    if graded:
        return acc
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def score(items, wpos, A, Q, distractor_key="distractor"):
    """2AFC; tie-break replicates canonicalize_fast (alphabetically earlier candidate wins)."""
    correct = np.zeros(len(items), dtype=bool)
    n_tie = 0
    for i, it in enumerate(items):
        t, dsr = it["target"], it[distractor_key]
        s = P1._cos_rows(Q[i], A[np.array([wpos[t], wpos[dsr]], dtype=np.int64)])
        st, sd = float(s[0]), float(s[1])
        if st == sd:
            n_tie += 1
            correct[i] = (t < dsr)
        else:
            correct[i] = st > sd
    return correct, {"n_ties": n_tie}


def decide_verdict(accs, gap_ci, dim_ci, self_checks) -> Tuple[str, List[str]]:
    """Bands frozen in preregs/2026-08-14_capacity_ceiling_and_the_near_far_gap.md sec 4."""
    for key, want in sorted(LANDED.items()):
        got = accs.get(_arm(int(key[0]), key[1], key[2]))
        if got is None or abs(got - want) > LANDED_TOL:
            return "INSTRUMENTATION_SUSPECT_BASELINE_DRIFT", [
                "%s = %s, want %.4f +/- %.2f: the harness changed, not the hypothesis"
                % (_arm(int(key[0]), key[1], key[2]), got, want, LANDED_TOL)]
    if not self_checks.get("float32_lossless", False):
        return "INSTRUMENTATION_SUSPECT_PRECISION", [
            "float32 and float64 accumulation did not agree byte-for-byte at the largest d"]
    for a in ARMS:
        if a.startswith("F_") and accs[a] > FLOOR_MAX:
            return "HARD_FAIL_FLOOR_BREACH", ["%s = %.4f > %.2f" % (a, accs[a], FLOOR_MAX)]

    near = accs[_arm(D_PRIMARY, "GRAD", "NEAR")]
    gap = accs[_arm(D_PRIMARY, "GRAD", "FAR")] - near

    # does dimensionality do anything at all? (this cell must be able to refute its own premise)
    dim_ok = False
    for c in CODES:
        dd = dim_ci[c]
        if dd["delta"] >= DIM_MIN_GAIN and dd["ci_excludes_zero"]:
            dim_ok = True
    if not dim_ok:
        return "HARD_FAIL_DIMENSION_DOES_NOTHING", [
            "neither code gains >= %.2f going d=256 -> d=%d with CI excluding 0: the capacity "
            "reading of the landed-VET is refuted by its own follow-up"
            % (DIM_MIN_GAIN, D_PRIMARY)]

    if near >= HP_NEAR_MIN and gap <= HP_GAP_MAX and not gap_ci["ci_excludes_zero"]:
        return "HARD_PASS_CAPACITY_EXPLAINS_THE_WALL", [
            "at d=%d GRAD: NEAR=%.4f >= %.2f and gap=%.4f <= %.2f with CI [%.4f,%.4f] including 0 "
            "-- the near-neighbour deficit was capacity"
            % (D_PRIMARY, near, HP_NEAR_MIN, gap, HP_GAP_MAX, gap_ci["ci_lo"], gap_ci["ci_hi"])]
    if near < HF_NEAR_MAX and gap >= HF_GAP_MIN and gap_ci["ci_excludes_zero"]:
        return "HARD_FAIL_WALL_IS_NOT_CAPACITY", [
            "at d=%d GRAD: NEAR=%.4f < %.2f and gap=%.4f >= %.2f with CI [%.4f,%.4f] EXCLUDING 0 "
            "-- 16x the capacity does not close the gap; a genuine semantic residual is isolated"
            % (D_PRIMARY, near, HF_NEAR_MAX, gap, HF_GAP_MIN, gap_ci["ci_lo"], gap_ci["ci_hi"])]
    return "MIDDLE_BAND_CAPACITY_PARTIAL", [
        "at d=%d GRAD: NEAR=%.4f gap=%.4f CI=[%.4f,%.4f] -- neither band met"
        % (D_PRIMARY, near, gap, gap_ci["ci_lo"], gap_ci["ci_hi"])]


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}
    sents = ["The poet wrote a long book about rivers and mountains in winter.",
             "A cathedral stands beside the river near the old market square."]

    # S1 -- at draw 0 and d=CTX_D the encoders are BYTE-IDENTICAL to the parent cell's, which are
    #       themselves byte-identical to hdlab's. Chains this cell to the substrate.
    for s in sents:
        assert np.array_equal(_enc(s, None, CTX_D, 0, False), P1._signed(s, None, CTX_D)), \
            "QUANT encoder FORKED the parent"
        assert np.array_equal(_enc(s, None, CTX_D, 0, True), P1._graded(s, None, CTX_D)), \
            "GRAD encoder FORKED the parent"
        for lem in ("poet", "river"):
            assert np.array_equal(_enc(s, frozenset({lem}), CTX_D, 0, False),
                                  context_vector_masked(s, lem)), "masked encoder FORKED hdlab"
    res["encoders_byte_identical_to_parent_and_hdlab"] = True

    # S2 -- PRECISION CONTROL (pre-reg 6.5): float32 codes accumulated in float64 must be
    #       BYTE-IDENTICAL to float64 codes at the largest d. Bipolar sums are exact below 2^24.
    d = DIMS[-1]
    acc32 = np.zeros(d, dtype=np.float64)
    acc64 = np.zeros(d, dtype=np.float64)
    for w in content_words(sents[0]) * 40:              # ~440 terms, still far below 2**24
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        acc64 += v
        acc32 += v.astype(np.float32)
    lossless = bool(np.array_equal(acc32, acc64))
    assert lossless, "float32 code cache is NOT lossless at d=%d -- the cell must abort" % d
    res["float32_lossless"] = lossless

    # S3 -- an independent projection DRAW really is independent.
    a0 = _code("river", 256, 0)
    a1 = _code("river", 256, 1)
    assert not np.array_equal(a0, a1), "draw 1 reproduced draw 0"
    c = float(a0 @ a1 / (np.linalg.norm(a0) * np.linalg.norm(a1)))
    assert abs(c) < 0.25, "two draws of the same word are not near-orthogonal (cos=%.3f)" % c
    res["draws_independent"] = {"cos_draw0_draw1": round(c, 4)}

    # S4 -- crosstalk falls with d as 1/sqrt(d). This is the premise of the whole cell, measured.
    ct = {}
    rng = np.random.default_rng(5)
    vocab = ["w%d" % i for i in range(200)]
    for dd in DIMS:
        M = np.stack([_code(w, dd, 0) for w in vocab]).astype(np.float64)
        M = M / np.linalg.norm(M, axis=1, keepdims=True)
        C = M @ M.T
        iu = np.triu_indices(len(vocab), 1)
        ct["d%d" % dd] = round(float(np.abs(C[iu]).mean()), 5)
    assert ct["d%d" % DIMS[-1]] < ct["d%d" % DIMS[0]] / 2.0, \
        "crosstalk did not fall with d: %r" % ct
    res["mean_abs_crosstalk_by_d"] = ct

    # S5 -- every verdict branch reachable.
    def _ci(v, ex):
        return {"delta": v, "ci_lo": v - 0.01 if ex else -abs(v) - 0.01, "ci_hi": v + 0.01,
                "ci_excludes_zero": ex}
    base = {a: 0.5 for a in ARMS}
    base[_arm(256, "QUANT", "NEAR")] = 0.6395
    base[_arm(256, "GRAD", "NEAR")] = 0.69975
    dim_ok = {"QUANT": _ci(0.06, True), "GRAD": _ci(0.06, True)}
    dim_no = {"QUANT": _ci(0.00, False), "GRAD": _ci(0.00, False)}
    ok = {"float32_lossless": True}
    hp = dict(base)
    hp[_arm(D_PRIMARY, "GRAD", "NEAR")] = 0.85
    hp[_arm(D_PRIMARY, "GRAD", "FAR")] = 0.86
    hf = dict(base)
    hf[_arm(D_PRIMARY, "GRAD", "NEAR")] = 0.72
    hf[_arm(D_PRIMARY, "GRAD", "FAR")] = 0.79
    mb = dict(base)
    mb[_arm(D_PRIMARY, "GRAD", "NEAR")] = 0.78
    mb[_arm(D_PRIMARY, "GRAD", "FAR")] = 0.80
    fl = dict(hp)
    fl[_floor_arm(256, "QUANT")] = 0.80
    drift = dict(hp)
    drift[_arm(256, "GRAD", "NEAR")] = 0.40
    seen = sorted({
        decide_verdict(hp, _ci(0.01, False), dim_ok, ok)[0],
        decide_verdict(hf, _ci(0.07, True), dim_ok, ok)[0],
        decide_verdict(mb, _ci(0.02, True), dim_ok, ok)[0],
        decide_verdict(hp, _ci(0.01, False), dim_no, ok)[0],
        decide_verdict(fl, _ci(0.01, False), dim_ok, ok)[0],
        decide_verdict(drift, _ci(0.01, False), dim_ok, ok)[0],
        decide_verdict(hp, _ci(0.01, False), dim_ok, {"float32_lossless": False})[0]})
    want = sorted(["HARD_PASS_CAPACITY_EXPLAINS_THE_WALL", "HARD_FAIL_WALL_IS_NOT_CAPACITY",
                   "MIDDLE_BAND_CAPACITY_PARTIAL", "HARD_FAIL_DIMENSION_DOES_NOTHING",
                   "HARD_FAIL_FLOOR_BREACH", "INSTRUMENTATION_SUSPECT_BASELINE_DRIFT",
                   "INSTRUMENTATION_SUSPECT_PRECISION"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["verdict_branches_reachable"] = seen

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def _build(words_used, profile_pool, items, donors, d, draw, output_dir, t0):
    """Anchors + queries at (d, draw) for BOTH codes, one pass over the profile sentences."""
    nw = len(words_used)
    sum_q = np.zeros((nw, d), dtype=np.float64)
    sum_g = np.zeros((nw, d), dtype=np.float64)
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            sum_q[i] += _enc(sent, drop, d, draw, False)
            sum_g[i] += _enc(sent, drop, d, draw, True)
        if (i + 1) % 500 == 0:
            _heartbeat(output_dir, "anchors_d%d_draw%d" % (d, draw), i + 1, nw, time.time() - t0)
    A = {"QUANT": np.sign(sum_q), "GRAD": sum_g}
    n = len(items)
    Q = {"QUANT": np.zeros((n, d)), "GRAD": np.zeros((n, d))}
    S = {"QUANT": np.zeros((n, d)), "GRAD": np.zeros((n, d))}
    for i, it in enumerate(items):
        drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                          it["target"], it["distractor"],
                          normalize_lemma(it["far"]), it["far"]})
        dj = items[donors[i]]
        dd = drop | frozenset({normalize_lemma(dj["target"]), normalize_lemma(dj["distractor"]),
                               dj["target"], dj["distractor"], normalize_lemma(dj["far"]),
                               dj["far"]})
        for code, graded in (("QUANT", False), ("GRAD", True)):
            Q[code][i] = _enc(it["sentence"], drop, d, draw, graded)
            S[code][i] = _enc(dj["sentence"], dd, d, draw, graded)
    return A, Q, S


def run(run_mode: str, output_dir: str, max_items: int) -> dict:
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
             "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
             "ts_iso": datetime.now(timezone.utc).isoformat()}
        _atomic_write_metrics(output_dir, m)
        return m

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    # FAR distractor: a random NON-SIBLING for the same target, drawn ONCE and attached to the
    # item, so NEAR and FAR are PAIRED on the same target and the same held-out sentence.
    sib = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    rng_far = np.random.default_rng(MASTER_SEED + 11)
    kept = []
    for it in items:
        c = words_used[int(rng_far.integers(len(words_used)))]
        tries = 0
        while tries < 40 and (c == it["target"] or c in sib[it["target"]]
                              or c == it["distractor"] or GP._is_variant(c, it["target"])):
            c = words_used[int(rng_far.integers(len(words_used)))]
            tries += 1
        if c == it["target"] or c in sib[it["target"]]:
            continue
        it["far"] = c
        kept.append(it)
    items = kept
    n = len(items)
    words_used = sorted({w for it in items for w in (it["target"], it["distractor"], it["far"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    nw = len(words_used)
    donors = GP.assign_donors(items)
    print("[items] n=%d anchors=%d" % (n, nw), flush=True)

    correct: Dict[str, np.ndarray] = {}
    diag: Dict[str, dict] = {}
    draw_deltas: Dict[str, List[float]] = {"QUANT": [], "GRAD": []}
    anchor_identical = None
    n_disagree = None

    for d in DIMS:
        A, Q, S = _build(words_used, profile_pool, items, donors, d, 0, output_dir, t0)
        print("[build] d=%d done (%.1fs)" % (d, time.time() - t0), flush=True)
        if d == CTX_D:
            # NON-FORK CONTROLS at the live dimensionality (pre-reg 6.4)
            space = ConceptSpace(d=CTX_D)
            for w in words_used:
                for sent in profile_pool.get(w, ()):
                    space.observe(w, context_vector_masked(sent, w))
            hd_anchors, hd_mat = space.anchor_matrix()
            anchor_identical = bool(hd_anchors == words_used
                                    and np.array_equal(A["QUANT"], hd_mat))
            assert anchor_identical, "anchor matrix is not hdlab's -- the cell is a fork"
            n_disagree = 0
            for i, it in enumerate(items):
                msk = np.zeros(nw, dtype=bool)
                msk[wpos[it["target"]]] = True
                msk[wpos[it["distractor"]]] = True
                pick, _c = canonicalize_fast("__slot__", Q["QUANT"][i], space, thresh=-1.0,
                                             eligible_mask=msk)
                cq, _ = score([it], wpos, A["QUANT"], Q["QUANT"][i][None, :])
                if bool(pick == it["target"]) != bool(cq[0]):
                    n_disagree += 1
            print("[control] read-out disagreements: %d/%d" % (n_disagree, n), flush=True)
        for code in CODES:
            correct[_arm(d, code, "NEAR")], diag[_arm(d, code, "NEAR")] = score(
                items, wpos, A[code], Q[code], "distractor")
            correct[_arm(d, code, "FAR")], diag[_arm(d, code, "FAR")] = score(
                items, wpos, A[code], Q[code], "far")
            correct[_floor_arm(d, code)], diag[_floor_arm(d, code)] = score(
                items, wpos, A[code], S[code], "distractor")
        _CODE.clear()

    # PROJECTION-DRAW CONTROL at d=256 (pre-reg 6.6): repeat the whole d=256 measurement over
    # N_DRAWS independent projections and report the between-draw sd next to every CI.
    for draw in range(1, N_DRAWS):
        A, Q, _S = _build(words_used, profile_pool, items, donors, CTX_D, draw, output_dir, t0)
        for code in CODES:
            cn, _ = score(items, wpos, A[code], Q[code], "distractor")
            cf, _ = score(items, wpos, A[code], Q[code], "far")
            draw_deltas[code].append(round(float(cf.mean() - cn.mean()), 6))
        _CODE.clear()
        print("[draw %d] gap QUANT=%.4f GRAD=%.4f"
              % (draw, draw_deltas["QUANT"][-1], draw_deltas["GRAD"][-1]), flush=True)

    correct["B_FREQ"], diag["B_FREQ"] = P1.arm_frequency(
        items, counts, np.random.default_rng(MASTER_SEED + 4))
    accs = {k: round(float(correct[k].mean()), 6) for k in ARMS}
    print("[arms] %s" % json.dumps(accs), flush=True)

    contrasts = []
    for d in DIMS:
        for c in CODES:
            contrasts.append(("gap_d%d_%s" % (d, c), _arm(d, c, "FAR"), _arm(d, c, "NEAR")))
    for c in CODES:
        contrasts.append(("dim_%s_near_d%d_minus_d256" % (c, D_PRIMARY),
                          _arm(D_PRIMARY, c, "NEAR"), _arm(256, c, "NEAR")))
        contrasts.append(("code_GRAD_minus_QUANT_near_d%d" % d, _arm(d, "GRAD", "NEAR"),
                          _arm(d, "QUANT", "NEAR")))
    bs = P1.paired_bootstrap(correct, ARMS, n_boot, BOOTSTRAP_SEED, contrasts)

    for draw in range(N_DRAWS - 1):
        pass
    gap0 = {c: round(accs[_arm(256, c, "FAR")] - accs[_arm(256, c, "NEAR")], 6) for c in CODES}
    draw_sd = {c: round(float(np.std([gap0[c]] + draw_deltas[c])), 6) for c in CODES}

    digests = {k: hashlib.sha256(correct[k].tobytes()).hexdigest() for k in ARMS}
    done = completed_units(output_dir)
    for k in ARMS:
        key = unit_key(ANCHOR_NAME, run_mode, str(n), k)
        if key not in done:
            record_unit(output_dir, key, {"arm": k, "acc": accs[k], "n": n, "digest": digests[k]})
    units = load_units(output_dir)

    gap_ci = bs["deltas"]["gap_d%d_GRAD" % D_PRIMARY]
    dim_ci = {c: bs["deltas"]["dim_%s_near_d%d_minus_d256" % (c, D_PRIMARY)] for c in CODES}
    verdict, notes = decide_verdict(accs, gap_ci, dim_ci, {"float32_lossless": True})

    curve = {"d%d" % d: {c: {"NEAR": accs[_arm(d, c, "NEAR")], "FAR": accs[_arm(d, c, "FAR")],
                             "gap": round(accs[_arm(d, c, "FAR")] - accs[_arm(d, c, "NEAR")], 6),
                             "floor": accs[_floor_arm(d, c)]} for c in CODES} for d in DIMS}
    msg = ("n=%d | NEAR by d: QUANT %s GRAD %s | GAP(FAR-NEAR) by d: QUANT %s GRAD %s | "
           "gap@d%d_GRAD CI=[%.4f,%.4f] | between-draw gap sd @d256 %s | floors %s | %s"
           % (n,
              [accs[_arm(d, "QUANT", "NEAR")] for d in DIMS],
              [accs[_arm(d, "GRAD", "NEAR")] for d in DIMS],
              [curve["d%d" % d]["QUANT"]["gap"] for d in DIMS],
              [curve["d%d" % d]["GRAD"]["gap"] for d in DIMS],
              D_PRIMARY, gap_ci["ci_lo"], gap_ci["ci_hi"], json.dumps(draw_sd),
              [accs[_floor_arm(d, c)] for d in DIMS for c in CODES], "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "at the capacity ceiling, does near-neighbour discrimination still lag "
                   "far-distractor discrimination, or does the gap close?",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "hdlab_modified": False,
        "n_items": n, "n_anchors": nw, "chance": CHANCE,
        "arm_accuracy": accs, "curve_by_dimension": curve,
        "arm_labels": {
            "A_d<D>_<CODE>_<DISTRACTOR>": "CODE QUANT = the live sign/sign comparator; GRAD = the "
                                          "wired graded path. DISTRACTOR NEAR = WordNet "
                                          "dominant-sense sibling; FAR = random non-sibling for "
                                          "the SAME target and the SAME held-out sentence",
            "F_d<D>_<CODE>_SCRAM": "scrambled-context floor at that (d, code)",
            "B_FREQ": "corpus-frequency baseline"},
        "HP_SCOPE": {"d%d_GRAD" % D_PRIMARY: ["NEAR level", "FAR-NEAR gap"],
                     "all_other_cells": "reported, no verdict weight"},
        "bands": {"HP_NEAR_MIN": HP_NEAR_MIN, "HP_GAP_MAX": HP_GAP_MAX,
                  "HF_NEAR_MAX": HF_NEAR_MAX, "HF_GAP_MIN": HF_GAP_MIN,
                  "DIM_MIN_GAIN": DIM_MIN_GAIN, "FLOOR_MAX": FLOOR_MAX,
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},
        "bootstrap_item": bs, "verdict_notes": notes,
        "projection_draw_control": {
            "n_draws": N_DRAWS, "gap_per_draw_d256": {c: [gap0[c]] + draw_deltas[c] for c in CODES},
            "between_draw_sd": draw_sd,
            "note": "the landed-VET showed the item bootstrap is blind to projection-draw "
                    "variance; no claim in this cell may rest on a difference smaller than this sd"},
        "non_fork_controls": {
            "anchor_matrix_byte_identical_to_hdlab_ConceptSpace": anchor_identical,
            "readout_disagreements_with_canonicalize_fast_at_d256": n_disagree,
            "encoders_byte_identical_to_parent": True,
            "float32_code_cache_lossless": True},
        "arm_diagnostics": diag, "arm_digests": digests,
        "item_construction": item_diag,
        "n_units": len(units), "expected_n_units": len(ARMS),
        "cardinality_ok": len(units) >= len(ARMS),
        "crlb": {"crlb_floor_computed": round(float(1.96 * np.sqrt(0.5 / max(n, 1))), 6),
                 "discriminator_range_by_construction": "2AFC accuracy, chance 0.50, nothing "
                                                        "hand-scored; the gap is a WITHIN-ITEM "
                                                        "paired contrast"},
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
            if not m["non_fork_controls"]["anchor_matrix_byte_identical_to_hdlab_ConceptSpace"]:
                raise AssertionError("BLOCK_DISPATCH: anchor matrix is not hdlab's")
            if m["non_fork_controls"]["readout_disagreements_with_canonicalize_fast_at_d256"] != 0:
                raise AssertionError("BLOCK_DISPATCH: read-out disagrees with canonicalize_fast")
            print("[smoke] n%d OK curve=%s" % (k, json.dumps(m["curve_by_dimension"])), flush=True)
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
