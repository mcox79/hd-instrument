"""exp_graded_divisive_comparator_v1 -- is the comparator's PER-COMPONENT MAGNITUDE-DESTROYING
NORMALISATION (np.sign) the thing that prevents near-neighbour discrimination?

PRE-REG: preregs/2026-08-13_graded_divisive_comparator.md, COMMITTED (d6c56353c) BEFORE this file
existed and BEFORE any arm was scored. Every arm, band, floor and gate is frozen there.
PARENT AUDIT: notes/comparator_component_fidelity_audit_2026-08-13.md (4e35b5cb7, corrected
eca191ce0).

THE FIDELITY GAP BEING TESTED (audit rows C1 + C2)
CITED@Carandini & Heeger 2012 Nat Rev Neurosci 13:51-62 -- the canonical cortical computation is
divisive normalisation r_i = x_i^n / (sigma^n + SUM_j x_j^n): the denominator is SHARED ACROSS THE
POOL, so every ratio inside the pool is PRESERVED.
Our composition ends in `np.sign(...)`, a PER-COMPONENT SELF denominator, which sets every ratio to
exactly 1. sign(shared + distinctive) = sign(shared) wherever |shared| > |distinctive|, i.e. it is a
PROTOTYPE OPERATOR; CITED@Rogers et al. 2004 Psychol Rev 111:205-235 prototype drift with
WITHIN-CATEGORY COORDINATE CONFUSION is the semantic-dementia signature and our exact failure mode.
MEASURED@experiments/diag_anchor_field_geometry_v1.py (400 concepts, 70 held-out sentences each):
under the live sign() code ||field mean||/||anchor|| = 0.5841 and mean pairwise cosine between two
ARBITRARY concepts = 0.3397; removing sign() gives 0.3545 / 0.1319; adding population divisive
normalisation gives 0.0000 / -0.0020.
MEASURED@a second, independent path (FHRR lexical, diag_percomp_vs_l2_normaliser_v1.py): swapping
ONLY per-component s/|s| for whole-vector s/||s|| moves near-vs-random d' 4.843 -> 6.030.

THIS CELL CHANGES ARITHMETIC ONLY. No new features, no new corpus, no training, no tuned parameter.
The item set, leak controls, held-out split and bootstrap are IMPORTED from the landed parent cell
(exp_context_conditioned_near_neighbour_v1, 367ce167f) so the ONLY difference between this cell and
its parent is the comparator's math.

NOTHING UNDER hdlab/ IS MODIFIED.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified (META_RULE_AF; per-arm choice-vector sha256)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes SEPARATE output dirs
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - discriminator RANGE BY CONSTRUCTION: 2AFC accuracy, chance exactly 0.50, nothing hand-scored
# - MDE_95 ~ 0.021 at n=4000 (parent's measured bootstrap sd) vs a +0.05 band -> reachable
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE: the bands apply to A_GGZ vs A_SSN ONLY; the other 14 factorial arms inherit no gate
# - NON-FORK CONTROLS: (1) sign(my graded encoder) is byte-identical to hdlab.context_vector and
#   context_vector_masked; (2) my A_SS anchor matrix is byte-identical to hdlab's own
#   ConceptSpace.anchor_matrix() over EVERY anchor; (3) my read-out agrees ITEM-FOR-ITEM with
#   hdlab's canonicalize_fast on the LIVE arm
# - deterministic seeding: hashlib + fixed ints only; no builtin hash(), no list(set())
# - per-unit checkpoint via tools/exp_checkpoint.py

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import (numpy sizes its pools at import time).
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

# ---- hdlab organs, imported and never modified -----------------------------------------------
from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, ConceptSpace, canonicalize_fast, content_lemmas, context_vector_masked,
    normalize_lemma,
)
from hdlab.grounding_acquisition_loop import content_words, context_vector    # noqa: E402

# ---- the PARENT CELL, imported wholesale: same corpus assets, same items, same leak controls,
#      same donor derangement. This is what makes "arithmetic is the only difference" true.
import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT        # noqa: E402

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---------------------------------------------------------------------------------------------
# CONFIG -- pre-registered. Nothing here is adjusted after seeing a result.
# ---------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_graded_divisive_comparator_v1"
PREREG_PATH = "preregs/2026-08-13_graded_divisive_comparator.md"
PREREG_COMMIT = "d6c56353c"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260813
BOOTSTRAP_SEED = 20260813
N_BOOTSTRAP = 5000

MAX_ITEMS = PARENT.MAX_ITEMS          # 4000
MIN_ITEMS = PARENT.MIN_ITEMS          # 200
N_PROFILE = PARENT.N_PROFILE          # 70
SMOKE_ITEM_SCALES = (150, 600)
STRICT_MARGIN_FRAC = 0.05
CHANCE = 0.50

ENC_LEVELS = ("S", "G")               # sentence -> vector: Sign (live) / Graded
AGG_LEVELS = ("S", "G")               # encounters -> concept: Sign (live) / Graded
NORM_LEVELS = ("N", "C", "Z", "ZA")   # none (live) / centre / z (divisive) / z-anchors-only

LIVE_ARM = "A_SSN"
PRIMARY_ARM = "A_GGZ"
SCRAM_LIVE = "F_SSN_SCRAM"
SCRAM_PRIMARY = "F_GGZ_SCRAM"
FREQ_ARM = "B_FREQ"

FACTORIAL_ARMS = tuple("A_%s%s%s" % (e, a, n)
                       for e in ENC_LEVELS for a in AGG_LEVELS for n in NORM_LEVELS)
ARMS = FACTORIAL_ARMS + (SCRAM_LIVE, SCRAM_PRIMARY, FREQ_ARM)

HP_DELTA = 0.05                       # HARD_PASS: acc(PRIMARY) - acc(LIVE)
FLOOR_MAX = 0.55                      # HARD_FAIL_FLOOR_BREACH above this
LANDED_LIVE_ACC = 0.6395              # parent's measured ARM 1 at n=4000
LANDED_TOL = 0.02
SELF_RETRIEVAL_FLOOR = PARENT.SELF_RETRIEVAL_FLOOR   # 0.70

_EPS = 1e-9


# ---------------------------------------------------------------------------------------------
# Durability plumbing (same contract as the parent)
# ---------------------------------------------------------------------------------------------
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
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "done": done, "total": total, "elapsed_s": round(elapsed_s, 3)}
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
    os.replace(tmp, final)                                  # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash", "failure_class": type(exc).__name__,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# THE ONE ARITHMETIC CHANGE.
#
# hdlab.grounding_acquisition_loop.context_vector is, verbatim (lines 117-134):
#     acc = sum over content words of a sha256-seeded bipolar draw
#     out = np.sign(acc); out[out == 0] = 1.0
# `_graded` is that function with the LAST TWO LINES REMOVED. `_signed` puts them back. Self-test
# S1 asserts _signed is BYTE-IDENTICAL to hdlab's own function on real sentences, which is what
# makes the graded arm "hdlab's math with one operation removed" rather than a re-implementation.
# ---------------------------------------------------------------------------------------------
_WORD_VEC: Dict[Tuple[str, int], np.ndarray] = {}


def _word_vec(w: str, d: int) -> np.ndarray:
    """The identical per-word bipolar draw hdlab uses. Cached; the draw is deterministic."""
    key = (w, d)
    v = _WORD_VEC.get(key)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        _WORD_VEC[key] = v
    return v


def _kept_words(sentence: str, drop: Optional[frozenset]) -> List[str]:
    ws = content_words(sentence)
    if drop:
        ws = [w for w in ws if normalize_lemma(w) not in drop]
    return ws


def _graded(sentence: str, drop: Optional[frozenset] = None, d: int = CTX_D) -> np.ndarray:
    """GRADED encoder: hdlab.context_vector WITHOUT the terminal per-component sign()."""
    ws = _kept_words(sentence, drop)
    if not ws:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in ws:
        acc += _word_vec(w, d)
    return acc


def _signed(sentence: str, drop: Optional[frozenset] = None, d: int = CTX_D) -> np.ndarray:
    """SIGN encoder: byte-identical to hdlab.context_vector / context_vector_masked (self-test S1)."""
    ws = _kept_words(sentence, drop)
    if not ws:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in ws:
        acc += _word_vec(w, d)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _sign_anchor(acc: np.ndarray) -> np.ndarray:
    """The AGG-step quantiser, matching hdlab.reading_grounding_loop.ConceptSpace.anchor_matrix
    line 446 EXACTLY: a plain `np.sign(...)` with NO zero convention, so the anchor code is
    TERNARY {-1,0,+1}, not bipolar. Note this differs from the ENC-step quantiser in
    `context_vector` (line 132-133), which maps sign-zero to +1. The two live sites use two
    different conventions; the byte-identity controls in the self-test are what surfaced it."""
    return np.sign(acc)


def _normalise(mat: np.ndarray, mu: np.ndarray, sd: np.ndarray, mode: str) -> np.ndarray:
    """Divisive normalisation with the POPULATION as the pool (Carandini & Heeger 2012): the
    denominator is shared across the pool, so ratios inside the pool are preserved. `mode` selects
    which part is applied; "N" is the live no-op."""
    if mode == "N":
        return mat
    out = mat - mu
    if mode == "Z":
        out = out / (sd + _EPS)
    return out


def _cos_rows(q: np.ndarray, M: np.ndarray) -> np.ndarray:
    """cos(q, each row of M). Zero rows score 0.0, matching canonicalize_fast's convention."""
    qn = float(np.linalg.norm(q))
    if qn < _EPS:
        return np.zeros(M.shape[0], dtype=np.float64)
    mn = np.linalg.norm(M, axis=1)
    ok = mn >= _EPS
    out = np.zeros(M.shape[0], dtype=np.float64)
    out[ok] = (M[ok] @ q) / (mn[ok] * qn)
    return out


# ---------------------------------------------------------------------------------------------
# Arm scoring
# ---------------------------------------------------------------------------------------------
def score_arm(items: List[dict], anchors_pos: Dict[str, int], A: np.ndarray,
              Q: np.ndarray) -> Tuple[np.ndarray, dict]:
    """2AFC: for each item, cos(query, anchor[target]) vs cos(query, anchor[distractor]).
    Tie-break replicates canonicalize_fast: np.argmax over an anchor list in SORTED order picks the
    FIRST maximum, i.e. the alphabetically earlier candidate wins a tie."""
    correct = np.zeros(len(items), dtype=bool)
    n_tie, n_zero_q = 0, 0
    margins = np.zeros(len(items), dtype=np.float64)
    for i, it in enumerate(items):
        q = Q[i]
        if float(np.linalg.norm(q)) < _EPS:
            n_zero_q += 1
        t, dsr = it["target"], it["distractor"]
        pair = np.array([anchors_pos[t], anchors_pos[dsr]], dtype=np.int64)
        s = _cos_rows(q, A[pair])
        st, sd = float(s[0]), float(s[1])
        margins[i] = st - sd
        if st == sd:
            n_tie += 1
            correct[i] = (t < dsr)            # alphabetically-first wins, as argmax would
        else:
            correct[i] = st > sd
    return correct, {"n_ties": n_tie, "n_zero_query": n_zero_q,
                     "mean_abs_margin": round(float(np.mean(np.abs(margins))), 6),
                     "mean_signed_margin": round(float(np.mean(margins)), 6)}


def arm_frequency(items: List[dict], counts: Dict[str, int],
                  rng: np.random.Generator) -> Tuple[np.ndarray, dict]:
    correct = np.zeros(len(items), dtype=bool)
    n_tie = 0
    for i, it in enumerate(items):
        ct, cd = counts.get(it["target"], 0), counts.get(it["distractor"], 0)
        if ct == cd:
            n_tie += 1
            correct[i] = bool(rng.integers(2) == 0)
        else:
            correct[i] = ct > cd
    return correct, {"n_ties_fell_back_to_coin": n_tie}


# ---------------------------------------------------------------------------------------------
# Paired bootstrap (all arms score the SAME items)
# ---------------------------------------------------------------------------------------------
def paired_bootstrap(correct: Dict[str, np.ndarray], keys: Sequence[str], n_boot: int, seed: int,
                     contrasts: Sequence[Tuple[str, str, str]],
                     clusters: Optional[np.ndarray] = None) -> dict:
    keys = list(keys)
    mat = np.stack([correct[k].astype(np.float64) for k in keys], axis=0)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    acc_boot = np.empty((n_boot, len(keys)), dtype=np.float64)
    if clusters is None:
        chunk, done = 400, 0
        while done < n_boot:
            m = min(chunk, n_boot - done)
            idx = rng.integers(0, n, size=(m, n))
            acc_boot[done:done + m] = mat[:, idx].mean(axis=2).T
            done += m
    else:
        uniq = sorted(set(int(c) for c in clusters))
        members = [np.flatnonzero(clusters == c) for c in uniq]
        for r in range(n_boot):
            pick = rng.integers(0, len(members), size=len(members))
            idx = np.concatenate([members[p] for p in pick])
            acc_boot[r] = mat[:, idx].mean(axis=1)
    out = {"n_boot": n_boot, "seed": seed, "clustered": clusters is not None,
           "arm_acc_ci": {}, "deltas": {}}
    ki = {k: j for j, k in enumerate(keys)}
    for k in keys:
        j = ki[k]
        lo, hi = np.percentile(acc_boot[:, j], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": round(float(mat[j].mean()), 6),
                                "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
                                "sd": round(float(acc_boot[:, j].std()), 6)}
    for name, a, b in contrasts:
        if b == "__CHANCE__":
            d = acc_boot[:, ki[a]] - CHANCE
            point = float(mat[ki[a]].mean() - CHANCE)
        else:
            d = acc_boot[:, ki[a]] - acc_boot[:, ki[b]]
            point = float(mat[ki[a]].mean() - mat[ki[b]].mean())
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"][name] = {"delta": round(point, 6), "ci_lo": round(float(lo), 6),
                               "ci_hi": round(float(hi), 6), "sd": round(float(d.std()), 6),
                               "mde_95": round(float(1.96 * d.std()), 6),
                               "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
                               "frac_boot_above_zero": round(float((d > 0).mean()), 6)}
    return out


def decide_verdict(bs: dict, accs: Dict[str, float], readout_disagreements: int,
                   self_retrieval: Dict[str, float]) -> Tuple[str, List[str]]:
    """Bands frozen in preregs/2026-08-13_graded_divisive_comparator.md sec 4."""
    notes: List[str] = []
    d = bs["deltas"]["d_PRIMARY_minus_LIVE"]
    dch = bs["deltas"]["d_PRIMARY_minus_CHANCE"]

    # INSTRUMENTATION verdicts dominate everything.
    if readout_disagreements > 0:
        return "INSTRUMENTATION_SUSPECT_READOUT_FORK", [
            "the direct read-out disagreed with hdlab.canonicalize_fast on %d LIVE-arm items; the "
            "harness is a fork of the substrate's read-out and no read is licensed"
            % readout_disagreements]
    if abs(accs[LIVE_ARM] - LANDED_LIVE_ACC) > LANDED_TOL:
        return "INSTRUMENTATION_SUSPECT_LIVE_ARM_DRIFT", [
            "LIVE arm %.4f is not the landed %.4f +/- %.2f: the harness changed, not the hypothesis"
            % (accs[LIVE_ARM], LANDED_LIVE_ACC, LANDED_TOL)]
    for k, v in sorted(self_retrieval.items()):
        if v < SELF_RETRIEVAL_FLOOR:
            return "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR", [
                "SELF_RETRIEVAL(%s)=%.4f < floor %.2f" % (k, v, SELF_RETRIEVAL_FLOOR)]

    # HARD_FAIL branches, evaluated before any pass.
    if accs[SCRAM_PRIMARY] > FLOOR_MAX:
        return "HARD_FAIL_FLOOR_BREACH", [
            "scrambled-context floor for the PRIMARY arm = %.4f > %.2f: any gain is not specific "
            "to THIS context" % (accs[SCRAM_PRIMARY], FLOOR_MAX)]
    if d["delta"] < 0.0 and d["ci_excludes_zero"]:
        return "HARD_FAIL_BINARISATION_WAS_LOAD_BEARING", [
            "d(PRIMARY-LIVE)=%.4f CI=[%.4f,%.4f] EXCLUDES 0 and is NEGATIVE: sign() is doing real "
            "work, and the brain-faithful direction is gain-BEFORE-quantisation, not no "
            "quantisation" % (d["delta"], d["ci_lo"], d["ci_hi"])]
    if not d["ci_excludes_zero"]:
        return "HARD_FAIL_BINARISATION_NOT_THE_LEVER", [
            "d(PRIMARY-LIVE)=%.4f CI=[%.4f,%.4f] INCLUDES 0: the audit's rank-1/rank-2 fidelity "
            "gaps are refuted as the binding constraint on this task; the measured field-geometry "
            "change is real but DECOUPLED from task performance"
            % (d["delta"], d["ci_lo"], d["ci_hi"])]

    hp = (d["delta"] >= HP_DELTA and d["ci_excludes_zero"]
          and accs[SCRAM_PRIMARY] <= FLOOR_MAX
          and dch["delta"] > 0 and dch["ci_excludes_zero"])
    if hp:
        if d["delta"] < HP_DELTA * (1.0 + STRICT_MARGIN_FRAC):
            notes.append("META_RULE_L: the HARD_PASS delta is cleared by < 5%% of its floor "
                         "(%.4f / %.4f) -> MIDDLE_BAND"
                         % (d["delta"], HP_DELTA * (1.0 + STRICT_MARGIN_FRAC)))
            return "MIDDLE_BAND_FLOOR_HUGGING", notes
        return "HARD_PASS", [
            "d(PRIMARY-LIVE)=%.4f CI=[%.4f,%.4f] clears +%.2f strictly above floor; scrambled "
            "floor %.4f <= %.2f; PRIMARY above chance"
            % (d["delta"], d["ci_lo"], d["ci_hi"], HP_DELTA, accs[SCRAM_PRIMARY], FLOOR_MAX)]
    return "MIDDLE_BAND_REAL_BUT_SMALL", [
        "d(PRIMARY-LIVE)=%.4f CI=[%.4f,%.4f] excludes 0 but is below the +%.2f band: a real but "
        "sub-threshold effect; does NOT license a build"
        % (d["delta"], d["ci_lo"], d["ci_hi"], HP_DELTA)]


# ---------------------------------------------------------------------------------------------
# Self-test (module scope, before any measurement)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}

    # S1 -- THE LOAD-BEARING NON-FORK CONTROL. _signed must be BYTE-IDENTICAL to hdlab's own
    #       context_vector and context_vector_masked. If this fails, the graded arm is not
    #       "hdlab's math with one operation removed" and nothing downstream is licensed.
    sents = ["The poet wrote a long book about rivers and mountains in winter.",
             "A cathedral stands beside the river near the old market square.",
             "Boats travel along the river between the town and the sea every summer.",
             "the the of and a"]
    for s in sents:
        assert np.array_equal(_signed(s), context_vector(s, d=CTX_D)), \
            "_signed FORKED hdlab.context_vector on %r" % s
        for lem in ("poet", "cathedral", "river", "zzzz"):
            assert np.array_equal(_signed(s, frozenset({lem})),
                                  context_vector_masked(s, lem)), \
                "_signed FORKED hdlab.context_vector_masked on (%r,%r)" % (s, lem)
    res["signed_encoder_byte_identical_to_hdlab"] = True

    # S2 -- the graded encoder actually differs from the signed one and carries magnitude.
    g = _graded(sents[0])
    sgn = _signed(sents[0])
    assert not np.array_equal(g, sgn), "graded encoder is bit-identical to the signed one"
    # the two live quantisers differ ONLY in the zero convention (context_vector maps sign-zero to
    # +1; ConceptSpace.anchor_matrix leaves it 0). Assert exactly that relationship.
    assert np.array_equal(np.where(g == 0.0, sgn, _sign_anchor(g)), sgn), \
        "the ENC and AGG quantisers differ by more than the zero convention"
    assert len(sorted(set(np.abs(g).tolist()))) > 1, "graded encoder has no magnitude variation"
    res["graded_encoder"] = {"n_distinct_abs_values": len(sorted(set(np.abs(g).tolist()))),
                             "max_abs": float(np.abs(g).max())}

    # S3 -- normalisation is a real transform and NORM='N' is exactly the live no-op.
    M = np.array([[3.0, 1.0, -2.0], [1.0, 1.0, 4.0], [-1.0, 5.0, 0.0]])
    mu, sd = M.mean(axis=0), M.std(axis=0)
    assert np.array_equal(_normalise(M, mu, sd, "N"), M), "NORM='N' is not the identity"
    assert np.allclose(_normalise(M, mu, sd, "C").mean(axis=0), 0.0), "NORM='C' did not centre"
    Z = _normalise(M, mu, sd, "Z")
    assert np.allclose(Z.std(axis=0), 1.0, atol=1e-6), "NORM='Z' did not scale to unit sd"
    # and the pool-shared property that motivates it: ratios WITHIN a row survive Z, but a
    # per-component self-denominator (sign) destroys them.
    row = np.array([8.0, 1.0])
    assert abs(row[0] / row[1] - 8.0) < 1e-9
    assert np.array_equal(_sign_anchor(row), np.array([1.0, 1.0])), "sign() did not flatten the ratio"
    res["normalisation_selftest"] = {"N_is_identity": True, "C_centres": True, "Z_unit_sd": True,
                                     "sign_flattens_ratio_8_to_1": True}

    # S4 -- the read-out MOVES, and it agrees with hdlab's canonicalize_fast on a real space.
    sp = ConceptSpace(d=CTX_D)
    prof = {"poet": ["The poet wrote verses and published a book of poems every winter.",
                     "A famous poet read verses aloud at the library and the school."],
            "river": ["The river flows through the valley and past the bridge each spring.",
                      "Boats travel along the river between the town and the sea."]}
    for w, ss in prof.items():
        for s in ss:
            sp.observe(w, context_vector_masked(s, w))
    anch, mat = sp.anchor_matrix()
    pos = {a: i for i, a in enumerate(anch)}
    # my A_SS must be byte-identical to hdlab's own anchor matrix
    mine = np.stack([_sign_anchor(sum(_signed(s, frozenset({w})) for s in prof[w])) for w in anch])
    assert np.array_equal(mine, mat), "A_SS anchor matrix FORKED hdlab's ConceptSpace"
    q_poet = _signed("She read verses from a book of poems at the library.",
                     frozenset({"poet", "river"}))
    q_river = _signed("Boats travel through the valley past the bridge to the sea.",
                      frozenset({"poet", "river"}))
    picks = []
    for q in (q_poet, q_river):
        m = np.ones(len(anch), dtype=bool)
        ref, _ = canonicalize_fast("__slot__", q, sp, thresh=-1.0, eligible_mask=m)
        s = _cos_rows(q, mat)
        mineb = anch[int(np.argmax(s))]
        assert mineb == ref, "read-out disagrees with canonicalize_fast: %r vs %r" % (mineb, ref)
        picks.append(ref)
    assert picks[0] != picks[1], ("READ-OUT CANNOT MOVE: two maximally different queries picked "
                                  "the same anchor (%r)" % picks[0])
    res["readout_matches_canonicalize_fast_and_moves"] = {"poetlike": picks[0],
                                                          "riverlike": picks[1]}

    # S5 -- the bootstrap MOVES on a real delta and its null false-positive rate is calibrated.
    rng = np.random.default_rng(3)
    n = 300
    base = rng.random(n) < 0.50
    better = base | (rng.random(n) < 0.30)
    keys = [LIVE_ARM, PRIMARY_ARM]
    fake = {LIVE_ARM: base, PRIMARY_ARM: better}
    con = [("d_PRIMARY_minus_LIVE", PRIMARY_ARM, LIVE_ARM),
           ("d_PRIMARY_minus_CHANCE", PRIMARY_ARM, "__CHANCE__")]
    bs = paired_bootstrap(fake, keys, 400, 7, con)
    assert bs["deltas"]["d_PRIMARY_minus_LIVE"]["ci_excludes_zero"], "bootstrap missed a real delta"
    n_fp, n_rep, nn = 0, 6, 800
    for s in range(n_rep):
        r2 = np.random.default_rng(2000 + s)
        null = {k: (r2.random(nn) < 0.50) for k in keys}
        if paired_bootstrap(null, keys, 400, 7, con)["deltas"]["d_PRIMARY_minus_LIVE"][
                "ci_excludes_zero"]:
            n_fp += 1
    assert n_fp <= 1, "bootstrap false-positive rate too high: %d/%d" % (n_fp, n_rep)
    res["bootstrap_selftest"] = {"real_ci_excludes_zero": True, "null_false_positives": n_fp,
                                 "null_replicates": n_rep}

    # S6 -- EVERY verdict branch is reachable (no unreachable band).
    def _mk(d, dch, ex=True, exch=True):
        def c(v, e):
            return {"delta": v, "ci_lo": v - 0.02 if e else -abs(v) - 0.02, "ci_hi": v + 0.02,
                    "ci_excludes_zero": e}
        return {"deltas": {"d_PRIMARY_minus_LIVE": c(d, ex),
                           "d_PRIMARY_minus_CHANCE": c(dch, exch)}}
    ok_acc = {LIVE_ARM: LANDED_LIVE_ACC, SCRAM_PRIMARY: 0.50}
    ok_sr = {LIVE_ARM: 0.85}
    seen = sorted({
        decide_verdict(_mk(0.12, 0.20), ok_acc, 0, ok_sr)[0],
        decide_verdict(_mk(0.051, 0.20), ok_acc, 0, ok_sr)[0],
        decide_verdict(_mk(0.03, 0.15), ok_acc, 0, ok_sr)[0],
        decide_verdict(_mk(0.00, 0.02, ex=False), ok_acc, 0, ok_sr)[0],
        decide_verdict(_mk(-0.08, 0.02), ok_acc, 0, ok_sr)[0],
        decide_verdict(_mk(0.12, 0.20), {LIVE_ARM: LANDED_LIVE_ACC, SCRAM_PRIMARY: 0.80}, 0,
                       ok_sr)[0],
        decide_verdict(_mk(0.12, 0.20), {LIVE_ARM: 0.40, SCRAM_PRIMARY: 0.50}, 0, ok_sr)[0],
        decide_verdict(_mk(0.12, 0.20), ok_acc, 7, ok_sr)[0],
        decide_verdict(_mk(0.12, 0.20), ok_acc, 0, {LIVE_ARM: 0.10})[0]})
    want = sorted(["HARD_PASS", "MIDDLE_BAND_FLOOR_HUGGING", "MIDDLE_BAND_REAL_BUT_SMALL",
                   "HARD_FAIL_BINARISATION_NOT_THE_LEVER", "HARD_FAIL_BINARISATION_WAS_LOAD_BEARING",
                   "HARD_FAIL_FLOOR_BREACH", "INSTRUMENTATION_SUSPECT_LIVE_ARM_DRIFT",
                   "INSTRUMENTATION_SUSPECT_READOUT_FORK",
                   "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["verdict_branches_reachable"] = seen

    # S7 -- the parent cell is the REAL parent (its constants are the ones we inherit).
    assert PARENT.MAX_ITEMS == 4000 and PARENT.N_PROFILE == 70 and PARENT.CHANCE == 0.50
    assert PARENT.PREREG_COMMIT == "42792834c"
    res["parent"] = {"anchor": PARENT.ANCHOR_NAME, "prereg_commit": PARENT.PREREG_COMMIT,
                     "max_items": PARENT.MAX_ITEMS, "n_profile": PARENT.N_PROFILE}

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_items: int) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode, len(ARMS))
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000

    # ---- items: the PARENT's, byte-for-byte -----------------------------------------------------
    assets = PARENT.build_corpus_assets()
    counts = assets["counts"]
    profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
    items, item_diag = PARENT.build_items(assets["pairs_strict"], eval_pool, max_items)
    n = len(items)
    print("[items] n=%d %s" % (n, json.dumps(item_diag["removals"])), flush=True)

    if run_mode == "full" and n < MIN_ITEMS:
        metrics = {"verdict": "INSUFFICIENT_ITEMS_NO_READ",
                   "verdict_msg": "only %d clean items (floor %d); STOPPED rather than running "
                                  "underpowered" % (n, MIN_ITEMS),
                   "summary": "graded/divisive comparator -- item gate stopped the run",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "n_items": n, "min_items": MIN_ITEMS, "cardinality_ok": False}
        _atomic_write_metrics(output_dir, metrics)
        return metrics
    if n < 2:
        raise AssertionError("VACUOUS RUN: %d items" % n)

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    nw = len(words_used)

    # ---- ANCHORS: four accumulators from ONE pass, plus hdlab's OWN space as the control --------
    sum_S = np.zeros((nw, CTX_D), dtype=np.float64)     # sum of SIGNED sentence vectors
    sum_G = np.zeros((nw, CTX_D), dtype=np.float64)     # sum of GRADED sentence vectors
    # query-pool statistics come from the PROFILE sentences (held out from scoring)
    qs_S = np.zeros(CTX_D)
    qs_S2 = np.zeros(CTX_D)
    qs_G = np.zeros(CTX_D)
    qs_G2 = np.zeros(CTX_D)
    n_prof_sent = 0
    space = ConceptSpace(d=CTX_D)                        # hdlab's own, for the byte-identity control
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            vs = _signed(sent, drop)
            vg = _graded(sent, drop)
            sum_S[i] += vs
            sum_G[i] += vg
            qs_S += vs
            qs_S2 += vs * vs
            qs_G += vg
            qs_G2 += vg * vg
            n_prof_sent += 1
            space.observe(w, context_vector_masked(sent, w))   # hdlab's own call, unmodified
        if (i + 1) % 250 == 0:
            _heartbeat(output_dir, "anchors", i + 1, nw, time.time() - t0)
    print("[space] anchors=%d profile_sentences=%d (%.1fs)"
          % (nw, n_prof_sent, time.time() - t0), flush=True)

    # NON-FORK CONTROL 2: my A_SS must be hdlab's own anchor matrix, byte for byte, over EVERY
    # anchor. If this fails the whole cell is void.
    hd_anchors, hd_mat = space.anchor_matrix()
    assert hd_anchors == words_used, "anchor order drifted from hdlab's sorted order"
    A_SS_live = np.stack([_sign_anchor(sum_S[i]) for i in range(nw)])
    anchor_matrix_identical = bool(np.array_equal(A_SS_live, hd_mat))
    assert anchor_matrix_identical, ("A_SS anchor matrix is NOT byte-identical to hdlab's "
                                     "ConceptSpace.anchor_matrix(); the cell is a fork")

    ANCH = {("S", "S"): A_SS_live, ("S", "G"): sum_S,
            ("G", "S"): np.stack([_sign_anchor(sum_G[i]) for i in range(nw)]), ("G", "G"): sum_G}

    # ---- QUERIES --------------------------------------------------------------------------------
    donors = PARENT.assign_donors(items)
    Q: Dict[str, np.ndarray] = {}
    QS: Dict[str, np.ndarray] = {}
    for enc, fn in (("S", _signed), ("G", _graded)):
        real = np.zeros((n, CTX_D))
        scram = np.zeros((n, CTX_D))
        for i, it in enumerate(items):
            drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                              it["target"], it["distractor"]})
            real[i] = fn(it["sentence"], drop)
            d = items[donors[i]]
            dd = drop | frozenset({normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                                   d["target"], d["distractor"]})
            scram[i] = fn(d["sentence"], dd)
        Q[enc] = real
        QS[enc] = scram
    # NON-FORK CONTROL 2b: the SIGN queries must be the parent's own _ctx_masked_multi output.
    n_q_check = min(200, n)
    for i in range(n_q_check):
        it = items[i]
        ref = PARENT._ctx_masked_multi(it["sentence"], [normalize_lemma(it["target"]),
                                                        normalize_lemma(it["distractor"]),
                                                        it["target"], it["distractor"]])
        assert np.array_equal(Q["S"][i], ref), "query encoder FORKED the parent's at item %d" % i

    # query-pool normalisation statistics (profile population, held out from scoring)
    m = max(1, n_prof_sent)
    QMU = {"S": qs_S / m, "G": qs_G / m}
    QSD = {"S": np.sqrt(np.maximum(qs_S2 / m - QMU["S"] ** 2, 0.0)),
           "G": np.sqrt(np.maximum(qs_G2 / m - QMU["G"] ** 2, 0.0))}

    # ---- SCORE ALL ARMS ---------------------------------------------------------------------------
    correct: Dict[str, np.ndarray] = {}
    arm_diag: Dict[str, dict] = {}
    for enc in ENC_LEVELS:
        for agg in AGG_LEVELS:
            A0 = ANCH[(enc, agg)]
            amu, asd = A0.mean(axis=0), A0.std(axis=0)
            for nm in NORM_LEVELS:
                arm = "A_%s%s%s" % (enc, agg, nm)
                A = _normalise(A0, amu, asd, "Z" if nm == "ZA" else nm)
                qmode = "N" if nm == "ZA" else nm
                Qa = _normalise(Q[enc], QMU[enc], QSD[enc], qmode)
                correct[arm], arm_diag[arm] = score_arm(items, wpos, A, Qa)
                _heartbeat(output_dir, "arm:" + arm, 1, 1, time.time() - t0)
    # floors: same arithmetic, scrambled query
    for arm, enc, agg, nm in ((SCRAM_LIVE, "S", "S", "N"), (SCRAM_PRIMARY, "G", "G", "Z")):
        A0 = ANCH[(enc, agg)]
        A = _normalise(A0, A0.mean(axis=0), A0.std(axis=0), nm)
        Qa = _normalise(QS[enc], QMU[enc], QSD[enc], nm)
        correct[arm], arm_diag[arm] = score_arm(items, wpos, A, Qa)
    correct[FREQ_ARM], arm_diag[FREQ_ARM] = arm_frequency(
        items, counts, np.random.default_rng(MASTER_SEED + 4))

    accs = {k: round(float(correct[k].mean()), 6) for k in ARMS}
    print("[arms] %s" % json.dumps(accs), flush=True)

    # ---- NON-FORK CONTROL 3: item-for-item agreement with hdlab's canonicalize_fast (LIVE) ------
    n_disagree = 0
    for i, it in enumerate(items):
        msk = np.zeros(nw, dtype=bool)
        msk[wpos[it["target"]]] = True
        msk[wpos[it["distractor"]]] = True
        pick, _c = canonicalize_fast("__slot__", Q["S"][i], space, thresh=-1.0, eligible_mask=msk)
        if bool(pick == it["target"]) != bool(correct[LIVE_ARM][i]):
            n_disagree += 1
    print("[control] read-out disagreements with canonicalize_fast on the LIVE arm: %d/%d"
          % (n_disagree, n), flush=True)

    # ---- META_RULE_AF: arms must not be bit-identical --------------------------------------------
    digests = {k: hashlib.sha256(correct[k].tobytes()).hexdigest() for k in ARMS}
    seen_d: Dict[str, str] = {}
    dup: List[str] = []
    for k in sorted(digests):
        if digests[k] in seen_d:
            dup.append("%s==%s" % (seen_d[digests[k]], k))
        else:
            seen_d[digests[k]] = k
    # the two arms whose bands are read MUST differ; duplicates elsewhere in the factorial are
    # reported, not fatal (e.g. C and Z can coincide if a pool sd is uniform).
    if digests[LIVE_ARM] == digests[PRIMARY_ARM]:
        raise AssertionError("META_RULE_AF VIOLATION: LIVE and PRIMARY arms are bit-identical")

    # ---- positive control: SELF_RETRIEVAL, for LIVE and PRIMARY ---------------------------------
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    n_sr = min(300, nw)
    sr_idx = np.sort(rng_sr.choice(nw, size=n_sr, replace=False))
    sr_words = [words_used[int(i)] for i in sr_idx]
    self_retrieval: Dict[str, float] = {}
    for arm, enc, agg, nm in ((LIVE_ARM, "S", "S", "N"), (PRIMARY_ARM, "G", "G", "Z")):
        A0 = ANCH[(enc, agg)]
        A = _normalise(A0, A0.mean(axis=0), A0.std(axis=0), nm)
        fn = _signed if enc == "S" else _graded
        hits, tot = 0, 0
        for w in sr_words:
            sents = profile_pool.get(w, [])
            if not sents:
                continue
            other = words_used[int(rng_sr.integers(nw))]
            while other == w:
                other = words_used[int(rng_sr.integers(nw))]
            q = fn(sents[0], frozenset({w, other, normalize_lemma(w), normalize_lemma(other)}))
            q = _normalise(q[None, :], QMU[enc], QSD[enc], nm)[0]
            pair = np.array([wpos[w], wpos[other]], dtype=np.int64)
            s = _cos_rows(q, A[pair])
            hits += int(s[0] > s[1] or (s[0] == s[1] and w < other))
            tot += 1
        self_retrieval[arm] = round(hits / max(1, tot), 4)
    print("[positive-control] self_retrieval %s (floor %.2f)"
          % (json.dumps(self_retrieval), SELF_RETRIEVAL_FLOOR), flush=True)

    # ---- SECONDARY (no verdict weight): FAR distractor for LIVE and PRIMARY ----------------------
    sib = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    rng_far = np.random.default_rng(MASTER_SEED + 11)
    far_cand: List[Optional[int]] = []
    for it in items:
        c = words_used[int(rng_far.integers(nw))]
        tries = 0
        while tries < 20 and (c == it["target"] or c in sib[it["target"]]
                              or PARENT._is_variant(c, it["target"])):
            c = words_used[int(rng_far.integers(nw))]
            tries += 1
        far_cand.append(None if (c == it["target"] or c in sib[it["target"]]) else wpos[c])
    far: Dict[str, dict] = {}
    for arm, enc, agg, nm in ((LIVE_ARM, "S", "S", "N"), (PRIMARY_ARM, "G", "G", "Z")):
        A0 = ANCH[(enc, agg)]
        A = _normalise(A0, A0.mean(axis=0), A0.std(axis=0), nm)
        Qa = _normalise(Q[enc], QMU[enc], QSD[enc], nm)
        hits, tot = 0, 0
        for i, it in enumerate(items):
            j = far_cand[i]
            if j is None:
                continue
            s = _cos_rows(Qa[i], A[np.array([wpos[it["target"]], j], dtype=np.int64)])
            hits += int(s[0] > s[1])
            tot += 1
        far[arm] = {"acc": round(hits / max(1, tot), 4), "n": tot}
    print("[secondary] far-distractor %s" % json.dumps(far), flush=True)

    # ---- bootstrap --------------------------------------------------------------------------------
    contrasts = [("d_PRIMARY_minus_LIVE", PRIMARY_ARM, LIVE_ARM),
                 ("d_PRIMARY_minus_CHANCE", PRIMARY_ARM, "__CHANCE__"),
                 ("d_PRIMARY_minus_SCRAM", PRIMARY_ARM, SCRAM_PRIMARY),
                 ("d_LIVE_minus_CHANCE", LIVE_ARM, "__CHANCE__"),
                 ("d_PRIMARY_minus_FREQ", PRIMARY_ARM, FREQ_ARM)]
    # secondary factor contrasts -- NO VERDICT WEIGHT, attribution only
    for nm in NORM_LEVELS:
        contrasts.append(("sec_ENC_G_minus_S_at_agg%s_norm%s" % ("G", nm),
                          "A_GG%s" % nm, "A_SG%s" % nm))
        contrasts.append(("sec_AGG_G_minus_S_at_encG_norm%s" % nm, "A_GG%s" % nm, "A_GS%s" % nm))
    for nm in ("C", "Z", "ZA"):
        contrasts.append(("sec_NORM_%s_minus_N_at_GG" % nm, "A_GG%s" % nm, "A_GGN"))
        contrasts.append(("sec_NORM_%s_minus_N_at_SS" % nm, "A_SS%s" % nm, "A_SSN"))
    bs = paired_bootstrap(correct, ARMS, n_boot, BOOTSTRAP_SEED, contrasts)
    tw = sorted({it["target"] for it in items})
    twi = {w: i for i, w in enumerate(tw)}
    clusters = np.array([twi[it["target"]] for it in items], dtype=np.int64)
    bs_cluster = paired_bootstrap(correct, ARMS, min(n_boot, 2000), BOOTSTRAP_SEED + 1,
                                  contrasts[:5], clusters)

    # ---- per-unit checkpoint ----------------------------------------------------------------------
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
    d = bs["deltas"]["d_PRIMARY_minus_LIVE"]
    msg = ("n=%d | LIVE(A_SSN)=%.4f PRIMARY(A_GGZ)=%.4f | d=%.4f CI=[%.4f,%.4f] | "
           "floors: SCRAM_PRIMARY=%.4f SCRAM_LIVE=%.4f FREQ=%.4f CHANCE=0.50 | "
           "readout_disagreements=%d | self_retrieval=%s | %s"
           % (n, accs[LIVE_ARM], accs[PRIMARY_ARM], d["delta"], d["ci_lo"], d["ci_hi"],
              accs[SCRAM_PRIMARY], accs[SCRAM_LIVE], accs[FREQ_ARM], n_disagree,
              json.dumps(self_retrieval), "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "does replacing the comparator's per-component magnitude-destroying "
                   "normalisation (np.sign) with a graded code + population divisive "
                   "normalisation improve near-neighbour discrimination in context?",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "parent_cell": PARENT.ANCHOR_NAME, "parent_prereg_commit": PARENT.PREREG_COMMIT,
        "audit_note": "notes/comparator_component_fidelity_audit_2026-08-13.md",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "hdlab_modified": False,
        "n_items": n, "min_items": MIN_ITEMS, "chance": CHANCE, "n_anchors": nw,
        "arm_accuracy": accs,
        "arm_labels": {
            "A_<ENC><AGG><NORM>": "ENC = sentence->vector: S=np.sign (live) / G=graded sum; "
                                  "AGG = encounters->concept: S=np.sign (live) / G=graded sum; "
                                  "NORM = pool: N=none (live) / C=centre / Z=centre+scale "
                                  "(divisive normalisation) / ZA=Z on anchors only",
            LIVE_ARM: "THE LIVE COMPARATOR -- positive control, must reproduce the landed 0.6395",
            PRIMARY_ARM: "THE PRE-DESIGNATED BRAIN-FAITHFUL ARM -- the only treatment arm",
            SCRAM_LIVE: "LIVE arithmetic, another item's real sentence as the query",
            SCRAM_PRIMARY: "PRIMARY arithmetic, another item's real sentence as the query",
            FREQ_ARM: "pick the corpus-more-frequent candidate"},
        "HP_SCOPE": {PRIMARY_ARM: ["d_PRIMARY_minus_LIVE", "floor", "above_chance"],
                     "all_other_factorial_arms": "NO VERDICT WEIGHT -- attribution only"},
        "bands": {"HARD_PASS_delta": HP_DELTA, "floor_max": FLOOR_MAX,
                  "landed_live_acc": LANDED_LIVE_ACC, "landed_tol": LANDED_TOL,
                  "strict_margin_frac": STRICT_MARGIN_FRAC,
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},
        "bootstrap_item": bs, "bootstrap_cluster_by_target_word": bs_cluster,
        "verdict_notes": notes,
        "non_fork_controls": {
            "signed_encoder_byte_identical_to_hdlab_context_vector": True,
            "anchor_matrix_byte_identical_to_hdlab_ConceptSpace": anchor_matrix_identical,
            "query_encoder_matches_parent_ctx_masked_multi_on_first_n": n_q_check,
            "readout_disagreements_with_canonicalize_fast_on_LIVE": n_disagree,
            "note": "all four are the controls that stop this cell from being a silent fork of "
                    "the substrate's own comparator; the anchor-matrix check covers EVERY anchor"},
        "positive_control_self_retrieval": {"values": self_retrieval,
                                            "floor": SELF_RETRIEVAL_FLOOR, "n": len(sr_words)},
        "secondary_far_distractor": {"prereg_status": "SECONDARY, NO VERDICT WEIGHT", **far},
        "arm_diagnostics": arm_diag,
        "arms_differ_verified": digests[LIVE_ARM] != digests[PRIMARY_ARM],
        "arm_digests": digests, "duplicate_arm_digests": sorted(dup),
        "item_construction": item_diag,
        "normalisation_pools": {
            "anchors": "per-dimension mean/sd over the ANCHOR MATRIX rows for that (ENC,AGG)",
            "queries": "per-dimension mean/sd over the PROFILE-SENTENCE population under the same "
                       "ENC (profile sentences are held out from scoring, so no eval item "
                       "contributes to its own normaliser)",
            "n_profile_sentences": n_prof_sent},
        "held_out": {"n_profile": N_PROFILE, "split": "inherited from the parent cell verbatim"},
        "corpus": {"path": "data/corpora/simplewiki/simplewiki_clean_v1.txt",
                   "n_lines": assets["n_lines"], "vocab_size": assets["vocab_size"],
                   "n_pairs_strict": len(assets["pairs_strict"])},
        "wordnet_version": assets["wordnet_version"],
        "organs_reused": {
            "items_leak_controls_split_donors": "experiments.exp_context_conditioned_near_neighbour_v1",
            "anchor_accumulator_control": "hdlab.reading_grounding_loop.ConceptSpace",
            "readout_control": "hdlab.reading_grounding_loop.canonicalize_fast",
            "encoder": "hdlab.grounding_acquisition_loop.context_vector, with the terminal "
                       "per-component sign() removed for the GRADED levels"},
        "n_units": len(units), "expected_n_units": len(ARMS), "cardinality_ok": cardinality_ok,
        "crlb": {"crlb_formula_reference": "paired-binomial se(delta) = sqrt(p_disc/n)",
                 "crlb_floor_computed": round(float(1.96 * np.sqrt(0.5 / max(n, 1))), 6),
                 "discriminator_reachability": bool(1.96 * np.sqrt(0.5 / max(n, 1)) < HP_DELTA),
                 "discriminator_range_by_construction": "2AFC accuracy in [0,1], chance exactly "
                                                        "0.50, nothing hand-scored"},
        "compute_architecture": "sequential-CPU; thread pins set before numpy import",
        "storage_strategy": "sharded (one anchor vector per candidate word); no_composition",
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
            if m["n_items"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d: %d items" % (k, m["n_items"]))
            a = m["arm_accuracy"]
            if len(sorted(set(round(v, 6) for v in a.values()))) == 1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: all arms identical at %d" % k)
            for arm in (LIVE_ARM, PRIMARY_ARM):
                if a[arm] in (0.0, 1.0):
                    raise AssertionError("INSTRUMENTATION_SUSPECT: %s pinned at %r" % (arm, a[arm]))
            if not m["non_fork_controls"]["anchor_matrix_byte_identical_to_hdlab_ConceptSpace"]:
                raise AssertionError("BLOCK_DISPATCH: anchor matrix is not hdlab's")
            if m["non_fork_controls"]["readout_disagreements_with_canonicalize_fast_on_LIVE"] != 0:
                raise AssertionError("BLOCK_DISPATCH: read-out disagrees with canonicalize_fast")
            if not m["arms_differ_verified"]:
                raise AssertionError("META_RULE_AF failed at %d" % k)
            if m["elapsed_s"] < 0.1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: <100ms exit at %d" % k)
            print("[smoke] n%d OK: LIVE=%.4f PRIMARY=%.4f SCRAM_P=%.4f"
                  % (k, a[LIVE_ARM], a[PRIMARY_ARM], a[SCRAM_PRIMARY]), flush=True)
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.max_items)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any measurement

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
