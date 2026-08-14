"""exp_rank1_common_mode_removal_v1 -- does removing the anchor field's rank-1 COMMON MODE buy
near-neighbour discrimination, and is any gain the COMMON MODE rather than perturbation?

PRE-REG: preregs/2026-08-14_rank1_common_mode_removal_near_neighbour.md, COMMITTED (32ca72e9c)
BEFORE this file existed and BEFORE any arm was scored. Every band, arm and floor is frozen there.

STEP 3 of notes/SUBSTRATE_STRATEGY.md (5f850770b).

WHY THIS IS NOT A FIFTH REPEAT OF A DEAD ROUTE
CITED@notes/ORGAN_MAP.md organ G3 (decorrelation drill, 2026-08-14): whitening is per-dimension
gain IN THE RIGHT BASIS. Four failed reweightings (log-IDF distinctiveness, differentia supply,
genus supply, near/far diagnostic) all applied gain per RAW dimension -- the wrong basis -- so they
are NOT evidence that gain-based decorrelation fails.
MEASURED@notes/ORGAN_MAP.md B3 (experiments/diag_anchor_field_geometry_v1.py, 400 concepts x 70
held-out sentences): ||field mean||/||anchor|| = 0.5841 under sign(), 0.3545 under GRADED; mean
pairwise cosine 0.3397 vs 0.1319. Sec 5 of the pre-reg pre-declares that under the graded default
this cell should measure NEARER 0.35 than 0.58, and this cell reports what it actually finds.
ESTIMABILITY is the separator: covariance is estimated ACROSS concepts (2000+ anchors), not
per-dimension within a concept (~70 encounters). Rank-1 needs O(d) samples and IS estimable.
FULL covariance at d=4096 needs O(d^2) = 65k-16M samples and is PARKED-BY-SAMPLE-SIZE -- NOT
attempted here and NOT to be queued off this cell's result either way.

BRAIN-FIDELITY SCOPE, CARRIED HONESTLY (pre-reg sec 0)
Decorrelation is UNPINNED for cortex and NOT-LICENSED as "the semantic hub does this". Real
decorrelating organs exist (olfactory-bulb whitening via structured inhibition; V1 adaptation
equalising across neurons; cortex cancelling shared input to near-zero correlation) but NONE is in
the semantic hub. This is an operation-class-compatible ENGINEERING fix, not a brain claim.
It is NOT the Carandini-Heeger error (ORGAN_MAP sec 3.1): a shared ADDITIVE component is not a
pool-shared SCALAR denominator, and it DOES change a two-candidate cosine argmax whenever the two
anchors' norms or their projections onto the shared direction differ.
HARD CAUTION: cortex's top PCs are MEANINGFUL (Huth 2012 Neuron 76:1210 -- PC1 mobility/animacy,
PC2 social). TOP-PC REMOVAL IS NOT BRAIN-LICENSED. Arm P4_TOP_PC is reported separately and
carries NO verdict weight.
ENGINEERING PRECEDENT, CREDITED: Mu & Viswanath, All-but-the-Top, ICLR 2018; Timkey & van
Schijndel, All Bark and No Bite, EMNLP 2021; Kovaleva et al., BERT Busters, ACL Findings 2021.

BASELINE. Live path at d=256 under the graded default (38f7a0d5c). 0.7495 is the d=1024 arm and
was NOT shipped; it is quoted NOWHERE in this cell as the live path.

NOTHING UNDER hdlab/ IS MODIFIED. The anchor accumulator, the context encoder and the read-out are
hdlab's own code, imported and called. The C1 testbed's item construction, leak controls, splits
and bootstrap are imported from experiments/exp_context_conditioned_near_neighbour_v1.py, not
re-implemented.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - IDENTITY-PROJECTION EQUIVALENCE positive control: P0's per-item boolean vector must be
#   BIT-IDENTICAL (sha256) to canonicalize_fast's over the same items, or INSTRUMENTATION_SUSPECT
# - arms_differ_verified at smoke gate (META_RULE_AF; per-arm choice-vector sha256)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes SEPARATE output dirs
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_floor_computed: paired-binomial se(delta)=sqrt(p_disc/n); mde_95 at n=4000, p_disc=0.10 is
#   0.0098 < the +0.03 HARD_PASS delta -> discriminator_reachability True (pre-reg 4)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < P0 < 0.95)
# - discriminator survives scale: multi-scale smoke (150 / 600 items) + FULL at MAX_ITEMS=4000
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; STRICT_MARGIN)
# - HP_SCOPE: the HARD_PASS gates apply to P1_COMMON_MODE ONLY; no other arm inherits a gate
# - cardinality_ok: EXPECTED_N_UNITS = named arms + K random draws x 2 control families
# - deterministic seeding: hashlib + fixed ints only; no builtin hash(), no list(set())
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

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
import importlib.util
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
    CTX_D, GRADED_COMPARATOR, canonicalize_fast,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402


# ---------------------------------------------------------------------------------------------
# THE TESTBED, IMPORTED WHOLE (pre-reg 2). Its module-scope self-test runs on import, which is a
# free positive control: if the C1 harness is broken, this cell cannot start.
# ---------------------------------------------------------------------------------------------
_BASE_PATH = os.path.join(REPO_ROOT, "experiments", "exp_context_conditioned_near_neighbour_v1.py")
_spec = importlib.util.spec_from_file_location("_c1_testbed", _BASE_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the C1 testbed at %s" % _BASE_PATH)
BASE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BASE)                              # runs BASE's self-test


ANCHOR_NAME = "exp_rank1_common_mode_removal_v1"
PREREG_PATH = "preregs/2026-08-14_rank1_common_mode_removal_near_neighbour.md"
PREREG_COMMIT = "32ca72e9c"
TESTBED_REPAIR_COMMIT = "df149251f"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260814
BOOTSTRAP_SEED = 20260814
N_BOOTSTRAP = 5000
K_RANDOM_DRAWS = 20                 # between-projection-draw sd is computed over these
MAX_ITEMS = 4000
MIN_ITEMS = 200
SMOKE_ITEM_SCALES = (150, 600)

# ---- BANDS, FROZEN IN THE PRE-REG (sec 4). Nothing here is adjusted after seeing a result. -----
HP_DELTA = 0.03                     # HARD_PASS floor on d_P1
SMALL_DELTA = 0.01                  # MIDDLE_BAND_REAL_BUT_SMALL floor
RAND_SD_MULTIPLE = 2.0              # must beat mu_rand + 2*sd_rand
SCRAMBLE_CEIL = 0.55                # P1's own scramble floor must stay at or below this
STRICT_MARGIN_FRAC = 0.05           # META_RULE_L
SELF_RETRIEVAL_FLOOR = 0.70
CHANCE = 0.50

NAMED_ARMS = ("P0_BASELINE", "P1_COMMON_MODE", "P4_TOP_PC_NOT_BRAIN_LICENSED", "P5_MEAN_SUBTRACT")
OPEN_VOCAB_ARMS = ("P0_BASELINE", "P1_COMMON_MODE", "P4_TOP_PC_NOT_BRAIN_LICENSED",
                   "P5_MEAN_SUBTRACT", "P2_RANDOM_DIR_d00", "P3_RANDOM_MATCHED_d00")


# ---------------------------------------------------------------------------------------------
# Durability plumbing (same contract as the testbed)
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


def _heartbeat(output_dir: str, stage: str, elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
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


def _seed_for(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


# ---------------------------------------------------------------------------------------------
# THE MECHANISM. One rank-1 linear map, applied to BOTH the anchor rows and the query.
#
# Everything operates on L2-NORMALISED vectors. Cosine is invariant to normalising its inputs, so
# for the PROJECTION arms this changes nothing at all -- but it makes the SUBTRACTION arms
# (P3/P5) well-defined: an anchor is a graded sum over ~70 encounters and a query is a single
# sentence's bundle, so their raw norms differ by an order of magnitude and subtracting one fixed
# anchor-scale offset from a query would simply obliterate the query. Normalising first is also
# exactly the regime Mu & Viswanath 2018 operate in.
# ---------------------------------------------------------------------------------------------
def _unit_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n = np.where(n < 1e-12, 1.0, n)
    return x / n


def _remove_direction(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """x - (x . u)u for unit u. Scale-free: identical whether or not x was normalised first."""
    return x - np.outer(x @ u, u)


def _subtract_offset(x: np.ndarray, r: np.ndarray) -> np.ndarray:
    """x - r, applied to already-unit-normalised rows (see the note above)."""
    return x - r[None, :]


def common_mode_stats(mat: np.ndarray) -> dict:
    """Every definition of 'the common mode' this cell reports, so the 58% figure can be checked
    against a like-for-like number rather than a differently-defined one.

    CITED@notes/ORGAN_MAP.md B3: ||field mean||/||anchor|| = 0.5841 (SIGN) / 0.3545 (GRADED),
    mean pairwise cosine 0.3397 / 0.1319, from diag_anchor_field_geometry_v1 over 400 concepts."""
    unit = _unit_rows(mat)
    u_raw = mat.mean(axis=0)
    u_unit = unit.mean(axis=0)
    mean_norm = float(np.linalg.norm(u_raw))
    mean_anchor_norm = float(np.mean(np.linalg.norm(mat, axis=1)))
    nu = float(np.linalg.norm(u_unit))
    uhat = u_unit / nu if nu > 1e-12 else u_unit
    proj = unit @ uhat
    # mean pairwise cosine over the whole field, computed without materialising n^2:
    # mean_{i!=j} u_i.u_j = (||sum u||^2 - n) / (n(n-1))
    n = unit.shape[0]
    s = unit.sum(axis=0)
    mean_pair_cos = float((float(s @ s) - n) / max(1, n * (n - 1)))
    return {
        "n_anchors": int(n), "d": int(mat.shape[1]),
        "organ_map_definition_mean_norm_over_anchor_norm":
            round(mean_norm / mean_anchor_norm, 6) if mean_anchor_norm > 0 else None,
        "norm_of_mean_of_unit_vectors": round(nu, 6),
        "shared_direction_energy_fraction": round(float(np.mean(proj ** 2)), 6),
        "mean_projection_on_shared_direction": round(float(np.mean(proj)), 6),
        "mean_pairwise_cosine": round(mean_pair_cos, 6),
        "definitions": {
            "organ_map_definition_mean_norm_over_anchor_norm":
                "||mean_i a_i|| / mean_i ||a_i|| -- the ORGAN_MAP B3 definition (0.5841 SIGN / "
                "0.3545 GRADED). Like-for-like with the 58% figure.",
            "norm_of_mean_of_unit_vectors":
                "||mean_i (a_i/||a_i||)|| -- the quantity P1 actually removes the direction of, "
                "and the norm P3/P5 subtract.",
            "shared_direction_energy_fraction":
                "mean_i (a_i_hat . u_hat)^2 -- fraction of unit-vector energy in the ONE shared "
                "direction. This is the 'more than half the variance is one direction' claim.",
            "mean_pairwise_cosine":
                "mean_{i!=j} cos(a_i,a_j) over the whole field, computed as "
                "(||sum a_hat||^2 - n)/(n(n-1))"}}


def build_projections(mat: np.ndarray, k_draws: int, seed: int) -> Tuple[Dict[str, dict], dict]:
    """Every arm's rank-1 map, built ONCE from the anchor population.

    ESTIMATION SET, disclosed (pre-reg 3): u, PC1 and the mean come from the FULL anchor
    population, which is built from HELD-OUT profile sentences and carries NO item labels. The
    estimate is UNSUPERVISED, so it cannot leak the 2AFC answer; it is in-sample with respect to
    the anchor set and that is stated rather than hidden."""
    unit = _unit_rows(mat)
    u_unit = unit.mean(axis=0)
    nu = float(np.linalg.norm(u_unit))
    if nu < 1e-12:
        raise AssertionError("the anchor field has NO mean direction (||mean|| = %.3e): the "
                             "premise of this cell is absent, no read is licensed" % nu)
    uhat = u_unit / nu

    # PC1 of the MEAN-CENTRED field (Mu & Viswanath's second step). Explicitly NOT brain-licensed.
    centred = unit - u_unit[None, :]
    # d=256 rows: full SVD of the (n x d) centred matrix via its d x d gram is exact and cheap.
    gram = centred.T @ centred
    evals, evecs = np.linalg.eigh(gram)
    pc1 = np.asarray(evecs[:, -1], dtype=np.float64)
    pc1 = pc1 / max(float(np.linalg.norm(pc1)), 1e-12)
    if float(pc1 @ uhat) < 0:
        pc1 = -pc1                                          # sign-canonicalise for reproducibility
    tot = float(np.sum(evals))
    pc1_var_frac = float(evals[-1] / tot) if tot > 0 else 0.0

    projs: Dict[str, dict] = {
        "P0_BASELINE": {"kind": "identity", "family": "baseline", "verdict_weight": True},
        "P1_COMMON_MODE": {"kind": "remove_dir", "vec": uhat, "family": "primary",
                           "verdict_weight": True},
        "P4_TOP_PC_NOT_BRAIN_LICENSED": {"kind": "remove_dir", "vec": pc1, "family": "non_brain",
                                         "verdict_weight": False},
        "P5_MEAN_SUBTRACT": {"kind": "subtract", "vec": u_unit, "family": "centering",
                             "verdict_weight": False},
    }

    rng = np.random.default_rng(seed)
    for k in range(k_draws):
        v = rng.standard_normal(mat.shape[1])
        v = v / float(np.linalg.norm(v))
        projs["P2_RANDOM_DIR_d%02d" % k] = {"kind": "remove_dir", "vec": v,
                                            "family": "random_dir_control", "verdict_weight": False}
    for k in range(k_draws):
        v = rng.standard_normal(mat.shape[1])
        v = v / float(np.linalg.norm(v))
        # MATCHED MAGNITUDE: same norm as the mean vector P5 subtracts, i.e. the size of the
        # shared offset actually present in the field.
        projs["P3_RANDOM_MATCHED_d%02d" % k] = {"kind": "subtract", "vec": v * nu,
                                                "family": "random_matched_control",
                                                "verdict_weight": False}
    meta = {"common_mode_direction_norm": round(nu, 6),
            "pc1_variance_fraction_of_centred_field": round(pc1_var_frac, 6),
            "pc1_dot_common_mode": round(float(pc1 @ uhat), 6),
            "k_random_draws": k_draws, "random_seed": seed,
            "estimation_set": "FULL anchor population (held-out profile sentences, no item "
                              "labels); unsupervised, so no answer leak; in-sample wrt the anchor "
                              "set, disclosed"}
    return projs, meta


def apply_projection(x: np.ndarray, spec: dict) -> np.ndarray:
    """Applied identically to the anchor rows and to the queries -- a change of basis applies to
    everything in the space, not to one side of the comparison."""
    kind = spec["kind"]
    if kind == "identity":
        return x
    if kind == "remove_dir":
        return _remove_direction(x, spec["vec"])
    if kind == "subtract":
        return _subtract_offset(_unit_rows(x), spec["vec"])
    raise AssertionError("unknown projection kind %r" % kind)


def score_2afc(rows: np.ndarray, queries: np.ndarray, t_idx: np.ndarray, d_idx: np.ndarray,
               ) -> Tuple[np.ndarray, dict]:
    """Two-candidate cosine argmax, vectorised. Tie-break = FIRST anchor in sorted order, which is
    exactly what canonicalize_fast's np.argmax over its sims array does; the identity-projection
    equivalence control asserts this reproduces canonicalize_fast bit for bit."""
    rn = _unit_rows(rows)
    qn = _unit_rows(queries)
    st = np.einsum("ij,ij->i", rn[t_idx], qn)
    sd = np.einsum("ij,ij->i", rn[d_idx], qn)
    tie = st == sd
    correct = np.where(tie, t_idx < d_idx, st > sd)
    return correct.astype(bool), {"n_ties": int(tie.sum()),
                                  "mean_margin": round(float(np.mean(np.abs(st - sd))), 6),
                                  "mean_target_cos": round(float(np.mean(st)), 6)}


# ---------------------------------------------------------------------------------------------
# Paired bootstrap on the deltas (every arm scores the SAME items)
# ---------------------------------------------------------------------------------------------
def paired_bootstrap(correct: Dict[str, np.ndarray], keys: Sequence[str], n_boot: int,
                     seed: int) -> dict:
    keys = list(keys)
    mat = np.stack([correct[k].astype(np.float64) for k in keys], axis=0)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    acc_boot = np.empty((n_boot, len(keys)), dtype=np.float64)
    chunk, done = 500, 0
    while done < n_boot:
        m = min(chunk, n_boot - done)
        idx = rng.integers(0, n, size=(m, n))
        acc_boot[done:done + m] = mat[:, idx].mean(axis=2).T
        done += m
    out = {"n_boot": n_boot, "seed": seed, "arm_acc_ci": {}, "deltas": {}}
    for j, k in enumerate(keys):
        lo, hi = np.percentile(acc_boot[:, j], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": round(float(mat[j].mean()), 6),
                                "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
                                "sd": round(float(acc_boot[:, j].std()), 6)}
    b = keys.index("P0_BASELINE")
    for j, k in enumerate(keys):
        if k == "P0_BASELINE":
            continue
        dd = acc_boot[:, j] - acc_boot[:, b]
        point = float(mat[j].mean() - mat[b].mean())
        lo, hi = np.percentile(dd, [2.5, 97.5])
        out["deltas"]["d_%s_minus_P0" % k] = {
            "delta": round(point, 6), "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
            "sd": round(float(dd.std()), 6), "mde_95": round(float(1.96 * dd.std()), 6),
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
            "frac_boot_above_zero": round(float((dd > 0).mean()), 6)}
    return out


def decide_verdict(d_p1: dict, mu_rand: float, sd_rand: float, p1_scramble: float) -> Tuple[
        str, List[str]]:
    """Bands frozen at preregs/2026-08-14_rank1_common_mode_removal_near_neighbour.md sec 4.
    HARD_FAIL_PERTURBATION_ARTIFACT is evaluated FIRST and dominates."""
    notes: List[str] = []
    delta = d_p1["delta"]
    beat_rand = mu_rand + RAND_SD_MULTIPLE * sd_rand
    if mu_rand >= delta:
        return "HARD_FAIL_PERTURBATION_ARTIFACT", [
            "mean random-direction delta %.4f >= common-mode delta %.4f -- removing a RANDOM "
            "rank-1 direction helps as much, so the effect is perturbation, not decorrelation"
            % (mu_rand, delta)]
    if not d_p1["ci_excludes_zero"]:
        return "HARD_FAIL_NO_EFFECT", [
            "d_P1=%.4f CI=[%.4f,%.4f] INCLUDES 0" % (delta, d_p1["ci_lo"], d_p1["ci_hi"])]
    clears_rand = delta > beat_rand
    if delta >= HP_DELTA and clears_rand and p1_scramble <= SCRAMBLE_CEIL:
        if delta < HP_DELTA * (1.0 + STRICT_MARGIN_FRAC):
            notes.append("META_RULE_L: d_P1=%.4f clears the %.2f floor by < 5%% (%.4f) "
                         "-> MIDDLE_BAND" % (delta, HP_DELTA, HP_DELTA * 1.05))
            return "MIDDLE_BAND_FLOOR_HUGGING", notes
        return "HARD_PASS", [
            "d_P1=%.4f CI=[%.4f,%.4f] >= %.2f, beats the random-direction control "
            "(mu_rand=%.4f sd_rand=%.4f -> threshold %.4f), P1 scramble floor %.4f <= %.2f"
            % (delta, d_p1["ci_lo"], d_p1["ci_hi"], HP_DELTA, mu_rand, sd_rand, beat_rand,
               p1_scramble, SCRAMBLE_CEIL)]
    if SMALL_DELTA <= delta < HP_DELTA and clears_rand:
        return "MIDDLE_BAND_REAL_BUT_SMALL", [
            "d_P1=%.4f CI=[%.4f,%.4f] excludes 0 and beats mu_rand+2sd (%.4f), but is below the "
            "%.2f HARD_PASS floor" % (delta, d_p1["ci_lo"], d_p1["ci_hi"], beat_rand, HP_DELTA)]
    return "MIDDLE_BAND", [
        "d_P1=%.4f CI=[%.4f,%.4f]; mu_rand=%.4f sd_rand=%.4f (threshold %.4f); P1 scramble %.4f "
        "-- neither the HARD_PASS conjunction nor the small-but-real band is met, and no HARD_FAIL "
        "trigger fired" % (delta, d_p1["ci_lo"], d_p1["ci_hi"], mu_rand, sd_rand, beat_rand,
                           p1_scramble)]


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- module scope, before any measurement; must not touch the 251 MB corpus)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {"c1_testbed_selftest_ran_on_import": bool(BASE._SELFTEST_RESULT),
                 "graded_comparator_switch": bool(GRADED_COMPARATOR)}

    # T1 -- the projection ALGEBRA is right: removal is idempotent, kills the direction, and is
    #       scale-free (so pre-normalising cannot change a projection arm).
    rng = np.random.default_rng(11)
    x = rng.standard_normal((40, 32))
    u = rng.standard_normal(32)
    u = u / float(np.linalg.norm(u))
    y = _remove_direction(x, u)
    assert float(np.max(np.abs(y @ u))) < 1e-10, "removal left a component on the removed direction"
    assert np.allclose(y, _remove_direction(y, u), atol=1e-12), "removal is not idempotent"
    y_scaled = _remove_direction(x * 7.0, u)
    assert np.allclose(y_scaled / 7.0, y, atol=1e-10), "removal is not scale-free"
    res["projection_algebra"] = {"orthogonal_after_removal": True, "idempotent": True,
                                 "scale_free": True}

    # T2 -- CAN-FAIL SANITY on the mechanism's premise: a synthetic field with a PLANTED common
    #       mode must (a) be measured as having one, and (b) have it removed. A field WITHOUT one
    #       must measure near zero. If common_mode_stats cannot tell these apart it is not a meter.
    d = 64
    base = rng.standard_normal((300, d))
    shared = rng.standard_normal(d)
    shared = shared / float(np.linalg.norm(shared))
    planted = base / np.linalg.norm(base, axis=1, keepdims=True) + 1.5 * shared[None, :]
    s_planted = common_mode_stats(planted)
    s_plain = common_mode_stats(base)
    assert s_planted["shared_direction_energy_fraction"] > 0.5, (
        "meter missed a PLANTED common mode: %r" % s_planted)
    assert s_plain["shared_direction_energy_fraction"] < 0.15, (
        "meter reports a common mode in an isotropic field: %r" % s_plain)
    pj, _m = build_projections(planted, 2, 5)
    after = common_mode_stats(apply_projection(planted, pj["P1_COMMON_MODE"]))
    assert after["shared_direction_energy_fraction"] < 0.15, (
        "P1 did NOT remove a planted common mode: %.4f -> %.4f"
        % (s_planted["shared_direction_energy_fraction"],
           after["shared_direction_energy_fraction"]))
    res["common_mode_meter"] = {
        "planted_energy_frac": s_planted["shared_direction_energy_fraction"],
        "isotropic_energy_frac": s_plain["shared_direction_energy_fraction"],
        "planted_after_P1": after["shared_direction_energy_fraction"]}

    # T3 -- score_2afc reproduces the SAME decisions as an explicit cosine loop, INCLUDING the
    #       first-in-sorted-order tie-break. A scorer that silently disagrees on ties is a fork.
    rows = rng.standard_normal((12, 16))
    rows[3] = rows[7]                                       # force exact ties
    q = rng.standard_normal((25, 16))
    ti = rng.integers(0, 12, 25)
    di = (ti + 1 + rng.integers(0, 11, 25)) % 12
    got, _ = score_2afc(rows, q, ti, di)
    ref = []
    for i in range(25):
        def _c(r):
            nr, nq = np.linalg.norm(rows[r]), np.linalg.norm(q[i])
            return 0.0 if nr < 1e-12 or nq < 1e-12 else float(rows[r] @ q[i] / (nr * nq))
        ct, cd = _c(int(ti[i])), _c(int(di[i]))
        ref.append(ct > cd or (ct == cd and int(ti[i]) < int(di[i])))
    assert list(got) == ref, "score_2afc disagrees with the explicit cosine loop"
    res["scorer_matches_reference_loop"] = True

    # T4 -- a RANDOM direction in high d removes almost nothing, and the MATCHED subtraction
    #       removes a comparable amount to the true mean. This is what makes the two controls
    #       different controls rather than the same one twice.
    unit_p = _unit_rows(planted)
    up = unit_p.mean(axis=0)
    nu = float(np.linalg.norm(up))
    vr = rng.standard_normal(d)
    vr = vr / float(np.linalg.norm(vr))
    frac_true = float(np.mean((unit_p @ (up / nu)) ** 2))
    frac_rand = float(np.mean((unit_p @ vr) ** 2))
    assert frac_true > 10 * frac_rand, (
        "the random control removes a comparable share of energy to the common mode "
        "(%.5f vs %.5f) -- the two controls are not distinguishable at this d" % (frac_true,
                                                                                  frac_rand))
    res["control_separation"] = {"energy_on_true_common_mode": round(frac_true, 6),
                                 "energy_on_a_random_direction": round(frac_rand, 6)}

    # T5 -- the bootstrap MOVES on a real delta and its NULL false-positive rate is calibrated.
    #       (Rate, not a single draw: two fair coins differ by chance ~5% of the time.)
    n = 400
    b0 = rng.random(n) < 0.50
    b1 = b0 | (rng.random(n) < 0.25)
    bs = paired_bootstrap({"P0_BASELINE": b0, "P1_COMMON_MODE": b1},
                          ["P0_BASELINE", "P1_COMMON_MODE"], 400, 7)
    assert bs["deltas"]["d_P1_COMMON_MODE_minus_P0"]["ci_excludes_zero"], "bootstrap missed a delta"
    n_fp, n_rep, nn = 0, 6, 800
    for s in range(n_rep):
        r2 = np.random.default_rng(2000 + s)
        null = {k: (r2.random(nn) < 0.50) for k in ("P0_BASELINE", "P1_COMMON_MODE")}
        if paired_bootstrap(null, ["P0_BASELINE", "P1_COMMON_MODE"], 400,
                            7)["deltas"]["d_P1_COMMON_MODE_minus_P0"]["ci_excludes_zero"]:
            n_fp += 1
    assert n_fp <= 1, "bootstrap false-positive rate too high: %d/%d" % (n_fp, n_rep)
    res["bootstrap_selftest"] = {"real_delta": bs["deltas"]["d_P1_COMMON_MODE_minus_P0"]["delta"],
                                 "null_false_positives": n_fp, "null_replicates": n_rep}

    # T6 -- every verdict branch is REACHABLE, and the PERTURBATION-ARTIFACT branch dominates.
    def _d(delta, ex=True):
        return {"delta": delta, "ci_lo": delta - 0.005 if ex else -abs(delta) - 0.005,
                "ci_hi": delta + 0.005, "ci_excludes_zero": ex}
    seen = sorted({
        decide_verdict(_d(0.060), 0.001, 0.002, 0.50)[0],            # HARD_PASS
        decide_verdict(_d(0.0305), 0.001, 0.002, 0.50)[0],           # FLOOR_HUGGING
        decide_verdict(_d(0.018), 0.001, 0.002, 0.50)[0],            # REAL_BUT_SMALL
        decide_verdict(_d(0.002, ex=False), 0.000, 0.002, 0.50)[0],  # NO_EFFECT
        decide_verdict(_d(0.010), 0.030, 0.002, 0.50)[0],            # PERTURBATION_ARTIFACT
        decide_verdict(_d(0.060), 0.001, 0.002, 0.80)[0]})           # MIDDLE_BAND (scramble ceil)
    want = sorted(["HARD_PASS", "MIDDLE_BAND_FLOOR_HUGGING", "MIDDLE_BAND_REAL_BUT_SMALL",
                   "HARD_FAIL_NO_EFFECT", "HARD_FAIL_PERTURBATION_ARTIFACT", "MIDDLE_BAND"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    # dominance: a big, tight, clean delta STILL fails if the random control matches it
    assert decide_verdict(_d(0.20), 0.25, 0.001, 0.50)[0] == "HARD_FAIL_PERTURBATION_ARTIFACT"
    res["verdict_branches_reachable"] = seen
    res["perturbation_branch_dominates"] = True

    # T7 -- the read-out we are about to project is the LIVE one (signature binding, gate F.2).
    import inspect
    inspect.signature(canonicalize_fast).bind_partial(
        new_lemma="x", new_raw_sum=None, space=None, thresh=0.0, eligible_mask=None)
    res["substrate_signature_checked"] = ["canonicalize_fast"]
    res["testbed_functions_bound"] = sorted([
        f for f in ("build_corpus_assets", "split_pools", "build_items", "build_space",
                    "assign_donors", "_ctx_masked_multi", "_is_variant")
        if hasattr(BASE, f)])
    assert len(res["testbed_functions_bound"]) == 7, (
        "C1 testbed API drift: only %r resolved" % res["testbed_functions_bound"])

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_items: int) -> dict:
    t0 = time.time()
    n_arms = len(NAMED_ARMS) + 2 * K_RANDOM_DRAWS
    _write_start_marker(output_dir, run_mode, n_arms)
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000

    # ---- items + anchor space: the C1 testbed's own construction, unmodified -------------------
    assets = BASE.build_corpus_assets()
    profile_pool, eval_pool = BASE.split_pools(assets["buckets"])
    items, item_diag = BASE.build_items(assets["pairs_strict"], eval_pool, max_items)
    n = len(items)
    print("[items] n=%d %s" % (n, json.dumps(item_diag["removals"])), flush=True)
    _heartbeat(output_dir, "items_built", time.time() - t0, {"n_items": n})

    if run_mode == "full" and n < MIN_ITEMS:
        metrics = {"verdict": "INSUFFICIENT_ITEMS_NO_READ",
                   "verdict_msg": "only %d clean items (floor %d); STOPPED rather than running "
                                  "underpowered" % (n, MIN_ITEMS),
                   "summary": "rank-1 common-mode removal -- item gate stopped the run",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "n_items": n,
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "cardinality_ok": False}
        _atomic_write_metrics(output_dir, metrics)
        return metrics
    if n < 2:
        raise AssertionError("VACUOUS RUN: %d items" % n)

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    space = BASE.build_space(words_used, profile_pool)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    print("[space] anchors=%d d=%d graded=%s" % (len(anchors), mat.shape[1], GRADED_COMPARATOR),
          flush=True)
    _heartbeat(output_dir, "space_built", time.time() - t0, {"n_anchors": len(anchors)})

    t_idx = np.array([pos[it["target"]] for it in items], dtype=np.int64)
    d_idx = np.array([pos[it["distractor"]] for it in items], dtype=np.int64)

    # ---- queries: real, and the deranged-donor SCRAMBLE (the testbed's own construction) -------
    q_real = np.stack([BASE._ctx_masked_multi(
        it["sentence"], [BASE.normalize_lemma(it["target"]), BASE.normalize_lemma(it["distractor"]),
                         it["target"], it["distractor"]]) for it in items]).astype(np.float64)
    donors = BASE.assign_donors(items)
    q_scram = np.stack([BASE._ctx_masked_multi(
        items[donors[i]]["sentence"],
        [BASE.normalize_lemma(it["target"]), BASE.normalize_lemma(it["distractor"]),
         it["target"], it["distractor"],
         BASE.normalize_lemma(items[donors[i]]["target"]),
         BASE.normalize_lemma(items[donors[i]]["distractor"]),
         items[donors[i]]["target"], items[donors[i]]["distractor"]])
        for i, it in enumerate(items)]).astype(np.float64)
    _heartbeat(output_dir, "queries_built", time.time() - t0)

    # ---- COMMON-MODE MEASUREMENT (pre-reg sec 5) -----------------------------------------------
    cm_graded = common_mode_stats(mat)
    cm_sign = common_mode_stats(np.sign(mat))
    cm_query = common_mode_stats(q_real)
    print("[common-mode] GRADED organ_map_def=%.4f energy_frac=%.4f pair_cos=%.4f | SIGN "
          "organ_map_def=%.4f energy_frac=%.4f pair_cos=%.4f"
          % (cm_graded["organ_map_definition_mean_norm_over_anchor_norm"],
             cm_graded["shared_direction_energy_fraction"], cm_graded["mean_pairwise_cosine"],
             cm_sign["organ_map_definition_mean_norm_over_anchor_norm"],
             cm_sign["shared_direction_energy_fraction"], cm_sign["mean_pairwise_cosine"]),
          flush=True)

    projs, proj_meta = build_projections(mat, K_RANDOM_DRAWS, MASTER_SEED)

    # ---- POSITIVE CONTROL: IDENTITY-PROJECTION EQUIVALENCE (pre-reg sec 6) ---------------------
    # P0 must be BIT-IDENTICAL to hdlab's own read-out. This is the licence for the vectorised
    # scorer; without it every arm below is an unverified fork.
    p0_vec, p0_diag = score_2afc(mat, q_real, t_idx, d_idx)
    ref = np.zeros(n, dtype=bool)
    for i, it in enumerate(items):
        m = np.zeros(len(anchors), dtype=bool)
        m[t_idx[i]] = True
        m[d_idx[i]] = True
        pick, _c = canonicalize_fast("__slot__", q_real[i], space, thresh=-1.0, eligible_mask=m)
        ref[i] = (pick == it["target"])
        if (i + 1) % 1000 == 0:
            _heartbeat(output_dir, "equivalence_control", time.time() - t0, {"i": i + 1})
    n_mismatch = int(np.sum(p0_vec != ref))
    equivalence_ok = (n_mismatch == 0)
    equivalence = {
        "n_mismatch": n_mismatch, "n_items": n, "bit_identical": equivalence_ok,
        "sha256_vectorised": hashlib.sha256(p0_vec.tobytes()).hexdigest(),
        "sha256_canonicalize_fast": hashlib.sha256(ref.tobytes()).hexdigest(),
        "acc_vectorised": round(float(p0_vec.mean()), 6),
        "acc_canonicalize_fast": round(float(ref.mean()), 6),
        "definition": "P0's per-item boolean vector vs hdlab.canonicalize_fast over the SAME "
                      "items and the SAME 2-anchor eligible_mask; anything but bit-identity means "
                      "the vectorised scorer has FORKED the live read-out"}
    print("[positive-control] IDENTITY-PROJECTION EQUIVALENCE: mismatches=%d acc_vec=%.4f "
          "acc_hdlab=%.4f" % (n_mismatch, p0_vec.mean(), ref.mean()), flush=True)

    # ---- SELF_RETRIEVAL positive control -------------------------------------------------------
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    n_sr = min(300, len(words_used))
    sr_words = [words_used[i] for i in
                np.sort(rng_sr.choice(len(words_used), size=n_sr, replace=False))]
    sr_hits, sr_n = 0, 0
    for w in sr_words:
        sents = profile_pool.get(w, [])
        if not sents:
            continue
        other = words_used[int(rng_sr.integers(len(words_used)))]
        while other == w:
            other = words_used[int(rng_sr.integers(len(words_used)))]
        q = BASE._ctx_masked_multi(sents[0], [w, other, BASE.normalize_lemma(w),
                                              BASE.normalize_lemma(other)])
        m = np.zeros(len(anchors), dtype=bool)
        m[pos[w]] = True
        m[pos[other]] = True
        pick, _ = canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=m)
        sr_hits += int(pick == w)
        sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 4)
    print("[positive-control] SELF_RETRIEVAL = %.4f (floor %.2f, n=%d)"
          % (self_retrieval, SELF_RETRIEVAL_FLOOR, sr_n), flush=True)

    # ---- FREQUENCY floor (arm-invariant) -------------------------------------------------------
    counts = assets["counts"]
    rng_f = np.random.default_rng(MASTER_SEED + 4)
    freq = np.zeros(n, dtype=bool)
    for i, it in enumerate(items):
        ct, cd = counts.get(it["target"], 0), counts.get(it["distractor"], 0)
        freq[i] = bool(rng_f.integers(2) == 0) if ct == cd else ct > cd
    freq_floor = round(float(freq.mean()), 6)

    # ---- ALL ARMS: real query + per-arm SCRAMBLE floor ------------------------------------------
    done = completed_units(output_dir)
    correct: Dict[str, np.ndarray] = {}
    scramble: Dict[str, float] = {}
    arm_diag: Dict[str, dict] = {}
    proj_anchor_cache: Dict[str, np.ndarray] = {}
    for name in sorted(projs):
        spec = projs[name]
        rows = apply_projection(mat, spec)
        qr = apply_projection(q_real, spec)
        qs = apply_projection(q_scram, spec)
        cv, dg = score_2afc(rows, qr, t_idx, d_idx)
        sv, _sg = score_2afc(rows, qs, t_idx, d_idx)
        correct[name] = cv
        scramble[name] = round(float(sv.mean()), 6)
        cmr = common_mode_stats(rows)
        arm_diag[name] = {
            "family": spec["family"], "verdict_weight": spec["verdict_weight"], **dg,
            "acc": round(float(cv.mean()), 6), "scramble_floor": scramble[name],
            "residual_common_mode_energy_fraction": cmr["shared_direction_energy_fraction"],
            "residual_mean_pairwise_cosine": cmr["mean_pairwise_cosine"]}
        if name in OPEN_VOCAB_ARMS:
            proj_anchor_cache[name] = rows
        key = unit_key(ANCHOR_NAME, run_mode, str(n), name)
        if key not in done:
            record_unit(output_dir, key, {"arm": name, "acc": float(cv.mean()),
                                          "scramble": scramble[name], "n": n,
                                          "digest": hashlib.sha256(cv.tobytes()).hexdigest()})
        _heartbeat(output_dir, "arm_scored", time.time() - t0,
                   {"arm": name, "acc": arm_diag[name]["acc"]})
    print("[arms] %s" % json.dumps({k: arm_diag[k]["acc"] for k in NAMED_ARMS}), flush=True)

    # ---- META_RULE_AF: the NAMED arms must not be bit-identical ---------------------------------
    digests = {k: hashlib.sha256(correct[k].tobytes()).hexdigest() for k in sorted(correct)}
    seen_d: Dict[str, str] = {}
    for k in NAMED_ARMS:
        if digests[k] in seen_d:
            raise AssertionError("META_RULE_AF VIOLATION: named arms %r and %r bit-identical -- "
                                 "the projection did nothing" % (seen_d[digests[k]], k))
        seen_d[digests[k]] = k

    # ---- BETWEEN-PROJECTION-DRAW SD (pre-reg sec 2 floor 4) -------------------------------------
    p0_acc = float(correct["P0_BASELINE"].mean())
    rand_dir = sorted(k for k in correct if k.startswith("P2_RANDOM_DIR_"))
    rand_mat = sorted(k for k in correct if k.startswith("P3_RANDOM_MATCHED_"))
    rd_acc = np.array([float(correct[k].mean()) for k in rand_dir])
    rm_acc = np.array([float(correct[k].mean()) for k in rand_mat])
    mu_rand = float(rd_acc.mean() - p0_acc)
    sd_rand = float(rd_acc.std(ddof=1)) if len(rd_acc) > 1 else 0.0
    mu_matched = float(rm_acc.mean() - p0_acc)
    sd_matched = float(rm_acc.std(ddof=1)) if len(rm_acc) > 1 else 0.0
    print("[control] RANDOM-DIRECTION delta mu=%.4f sd=%.4f (K=%d) | MATCHED-SUBTRACT delta "
          "mu=%.4f sd=%.4f" % (mu_rand, sd_rand, len(rd_acc), mu_matched, sd_matched), flush=True)

    # ---- bootstrap on the named arms ------------------------------------------------------------
    boot_keys = list(NAMED_ARMS) + [rand_dir[0], rand_mat[0]]
    bs = paired_bootstrap(correct, boot_keys, n_boot, BOOTSTRAP_SEED)
    d_p1 = bs["deltas"]["d_P1_COMMON_MODE_minus_P0"]

    # ---- SECONDARY: SISTER-TERM SEPARATION (pre-reg sec 7; NO verdict weight) -------------------
    sib = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    anchor_arr = np.array(anchors)
    sister: Dict[str, dict] = {}
    top1_by_arm: Dict[str, np.ndarray] = {}
    for name in OPEN_VOCAB_ARMS:
        rows = proj_anchor_cache[name]
        qn = _unit_rows(apply_projection(q_real, projs[name]))
        rn = _unit_rows(rows)
        top1 = np.empty(n, dtype=np.int64)
        step = 500
        for s in range(0, n, step):
            top1[s:s + step] = np.argmax(qn[s:s + step] @ rn.T, axis=1)
        top1_by_arm[name] = top1
        picks = anchor_arr[top1]
        exact = np.array([picks[i] == items[i]["target"] for i in range(n)])
        is_sib = np.array([(picks[i] != items[i]["target"]
                            and picks[i] in sib[items[i]["target"]]) for i in range(n)])
        sister[name] = {
            "top1_exact": round(float(exact.mean()), 6),
            "top1_sibling_not_target": round(float(is_sib.mean()), 6),
            "neighbourhood_hit_at_1": round(float((exact | is_sib).mean()), 6),
            "top1_unrelated": round(float((~(exact | is_sib)).mean()), 6)}
        _heartbeat(output_dir, "open_vocab", time.time() - t0, {"arm": name})
    p0_top1 = top1_by_arm["P0_BASELINE"]
    p0_picks = anchor_arr[p0_top1]
    p0_was_sibling = np.array([(p0_picks[i] != items[i]["target"]
                                and p0_picks[i] in sib[items[i]["target"]]) for i in range(n)])
    for name in OPEN_VOCAB_ARMS:
        picks = anchor_arr[top1_by_arm[name]]
        exact = np.array([picks[i] == items[i]["target"] for i in range(n)])
        conv = (float(exact[p0_was_sibling].mean())
                if int(p0_was_sibling.sum()) > 0 else None)
        sister[name]["sister_conversion_from_P0_sibling_errors"] = (
            None if conv is None else round(conv, 6))
        sister[name]["n_P0_sibling_errors"] = int(p0_was_sibling.sum())
    print("[secondary] SISTER-TERM %s" % json.dumps(
        {k: {"exact": v["top1_exact"], "sib": v["top1_sibling_not_target"],
             "conv": v["sister_conversion_from_P0_sibling_errors"]}
         for k, v in sister.items()}), flush=True)

    # ---- ANCHORS-ONLY diagnostic (labelled; NO verdict weight) ----------------------------------
    anchors_only = {}
    for name in NAMED_ARMS:
        cv, _ = score_2afc(apply_projection(mat, projs[name]), q_real, t_idx, d_idx)
        anchors_only[name] = round(float(cv.mean()), 6)

    # ---- verdict --------------------------------------------------------------------------------
    units = load_units(output_dir)
    cardinality_ok = len(units) >= n_arms
    baseline_in_band = bool(0.05 < p0_acc < 0.95)
    verdict, notes = decide_verdict(d_p1, mu_rand, sd_rand, scramble["P1_COMMON_MODE"])
    if not equivalence_ok:
        verdict = "INSTRUMENTATION_SUSPECT_IDENTITY_PROJECTION_NOT_BIT_IDENTICAL"
        notes = ["P0 differs from canonicalize_fast on %d/%d items: the vectorised scorer is a "
                 "FORK of the live read-out, so NO read on the hypothesis is licensed"
                 % (n_mismatch, n)] + notes
    elif self_retrieval < SELF_RETRIEVAL_FLOOR:
        verdict = "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR"
        notes = ["SELF_RETRIEVAL=%.4f < %.2f" % (self_retrieval, SELF_RETRIEVAL_FLOOR)] + notes
    elif not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not baseline_in_band:
        verdict = "MIDDLE_BAND_BASELINE_OUT_OF_BAND_META_RULE_AG"

    msg = ("n=%d d=%d | COMMON MODE graded organ_map_def=%.4f energy=%.4f pair_cos=%.4f (sign "
           "field %.4f/%.4f) | P0=%.4f P1=%.4f d_P1=%.4f CI=[%.4f,%.4f] | RANDOM-DIR CONTROL "
           "mu=%.4f sd=%.4f (K=%d) MATCHED mu=%.4f sd=%.4f | P4_topPC=%.4f P5_mean=%.4f | FLOORS "
           "scramble P0=%.4f P1=%.4f freq=%.4f chance=0.50 | self_retrieval=%.4f | SISTER exact "
           "P0=%.4f P1=%.4f sib-err P0=%.4f P1=%.4f conv=%s | %s"
           % (n, mat.shape[1],
              cm_graded["organ_map_definition_mean_norm_over_anchor_norm"],
              cm_graded["shared_direction_energy_fraction"], cm_graded["mean_pairwise_cosine"],
              cm_sign["organ_map_definition_mean_norm_over_anchor_norm"],
              cm_sign["shared_direction_energy_fraction"],
              p0_acc, float(correct["P1_COMMON_MODE"].mean()),
              d_p1["delta"], d_p1["ci_lo"], d_p1["ci_hi"],
              mu_rand, sd_rand, len(rd_acc), mu_matched, sd_matched,
              float(correct["P4_TOP_PC_NOT_BRAIN_LICENSED"].mean()),
              float(correct["P5_MEAN_SUBTRACT"].mean()),
              scramble["P0_BASELINE"], scramble["P1_COMMON_MODE"], freq_floor, self_retrieval,
              sister["P0_BASELINE"]["top1_exact"], sister["P1_COMMON_MODE"]["top1_exact"],
              sister["P0_BASELINE"]["top1_sibling_not_target"],
              sister["P1_COMMON_MODE"]["top1_sibling_not_target"],
              sister["P1_COMMON_MODE"]["sister_conversion_from_P0_sibling_errors"],
              "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "rank-1 COMMON-MODE removal on the near-neighbour 2AFC read-out, against a "
                   "random-rank-1-direction control and a matched-magnitude subtraction control",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "testbed_repair_commit": TESTBED_REPAIR_COMMIT,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "hdlab_modified": False,
        "graded_comparator_switch": bool(GRADED_COMPARATOR),
        "n_items": n, "d": int(mat.shape[1]), "n_anchors": len(anchors), "chance": CHANCE,

        "brain_fidelity_scope": {
            "claim_class": "operation-class-compatible ENGINEERING fix",
            "NOT_claimed": "that the anterior temporal semantic hub performs decorrelation",
            "decorrelation_in_cortex": "UNPINNED; NOT-LICENSED for the semantic hub",
            "real_decorrelating_organs_cited_as_operation_class_only": [
                "olfactory-bulb whitening via structured granule-cell inhibition",
                "V1 adaptation equalising response across neurons",
                "cortex cancelling shared input to near-zero correlation"],
            "not_the_carandini_heeger_error":
                "a shared ADDITIVE component is not a pool-shared SCALAR denominator; cosine is "
                "invariant to the latter but NOT to the former whenever the two candidate "
                "anchors' norms or their projections on the shared direction differ",
            "top_pc_caution":
                "cortex's top PCs are MEANINGFUL (Huth 2012 Neuron 76:1210 -- PC1 "
                "mobility/animacy, PC2 social). TOP-PC REMOVAL IS NOT BRAIN-LICENSED; arm "
                "P4_TOP_PC_NOT_BRAIN_LICENSED carries NO verdict weight.",
            "engineering_precedent_credited": [
                "Mu & Viswanath 2018, All-but-the-Top, ICLR",
                "Timkey & van Schijndel 2021, All Bark and No Bite, EMNLP",
                "Kovaleva et al. 2021, BERT Busters, ACL Findings"],
            "full_covariance_whitening":
                "PARKED-BY-SAMPLE-SIZE at O(d^2) = 65k-16M samples. NOT attempted here and NOT to "
                "be queued off this cell's result in either direction."},

        "common_mode_measured": {
            "graded_field_LIVE": cm_graded, "sign_field": cm_sign, "query_field": cm_query,
            "organ_map_reference": {"sign": 0.5841, "graded": 0.3545,
                                    "mean_pairwise_cosine_sign": 0.3397,
                                    "mean_pairwise_cosine_graded": 0.1319,
                                    "source": "notes/ORGAN_MAP.md B3 / "
                                              "experiments/diag_anchor_field_geometry_v1.py, "
                                              "400 concepts x 70 held-out sentences"},
            "prereg_prediction": "under the graded default this should be NEARER 0.35 than 0.58",
            "projection_meta": proj_meta},

        "arm_accuracy": {k: round(float(correct[k].mean()), 6) for k in sorted(correct)},
        "arm_diagnostics": arm_diag,
        "arm_labels": {
            "P0_BASELINE": "identity -- the unchanged live read-out",
            "P1_COMMON_MODE": "remove (x.u)u, u = unit-normalised mean of the L2-normalised "
                              "anchors; applied to BOTH anchors and query -- PRIMARY",
            "P2_RANDOM_DIR_dNN": "remove (x.v)v for a RANDOM unit v -- THE CONTROL THAT MATTERS: "
                                 "if this helps as much, the gain is perturbation not "
                                 "decorrelation",
            "P3_RANDOM_MATCHED_dNN": "subtract a FIXED random vector of the SAME NORM as the mean "
                                     "P5 subtracts -- matched-magnitude control",
            "P4_TOP_PC_NOT_BRAIN_LICENSED": "remove PC1 of the mean-centred field -- NOT "
                                            "brain-licensed, NO verdict weight",
            "P5_MEAN_SUBTRACT": "x - mean(unit anchors) (Mu & Viswanath step 1)"},
        "HP_SCOPE": {"P1_COMMON_MODE": ["d_P1", "beats_random_control", "scramble_ceiling"],
                     "P0_BASELINE": [], "P2_RANDOM_DIR_dNN": [], "P3_RANDOM_MATCHED_dNN": [],
                     "P4_TOP_PC_NOT_BRAIN_LICENSED": [], "P5_MEAN_SUBTRACT": []},

        "random_direction_control": {
            "k_draws": len(rd_acc), "per_draw_acc": [round(float(v), 6) for v in rd_acc],
            "mean_delta_vs_P0": round(mu_rand, 6),
            "between_projection_draw_sd": round(sd_rand, 6),
            "threshold_P1_must_beat": round(mu_rand + RAND_SD_MULTIPLE * sd_rand, 6),
            "P1_beats_it": bool(d_p1["delta"] > mu_rand + RAND_SD_MULTIPLE * sd_rand),
            "definition": "removal of a RANDOM rank-1 direction, K independent draws. A gain "
                          "smaller than the variation BETWEEN random draws is not a gain."},
        "matched_magnitude_control": {
            "k_draws": len(rm_acc), "per_draw_acc": [round(float(v), 6) for v in rm_acc],
            "mean_delta_vs_P0": round(mu_matched, 6),
            "between_projection_draw_sd": round(sd_matched, 6),
            "definition": "subtract a FIXED random vector whose norm equals the true mean's; "
                          "tests whether ANY shared offset of that size helps"},

        "floors": {
            "chance": CHANCE, "frequency_baseline": freq_floor,
            "scramble_per_arm": scramble,
            "between_projection_draw_sd_random_dir": round(sd_rand, 6),
            "note": "all floors are SAME-corpus, SAME-metric, SAME-run as the arms above"},

        "bootstrap": bs, "primary_delta": d_p1, "verdict_notes": notes,
        "bands": {"HARD_PASS_delta": HP_DELTA, "REAL_BUT_SMALL_delta": SMALL_DELTA,
                  "random_sd_multiple": RAND_SD_MULTIPLE, "scramble_ceiling": SCRAMBLE_CEIL,
                  "strict_margin_frac": STRICT_MARGIN_FRAC,
                  "HARD_FAIL_PERTURBATION_ARTIFACT": "mu_rand >= d_P1 (evaluated FIRST)",
                  "HARD_FAIL_NO_EFFECT": "CI of d_P1 includes 0",
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},

        "positive_control_identity_projection_equivalence": equivalence,
        "positive_control_self_retrieval": {"value": self_retrieval, "floor": SELF_RETRIEVAL_FLOOR,
                                            "n": sr_n},
        "sister_term_diagnostic": {
            "prereg_status": "PRE-DECLARED SECONDARY (pre-reg sec 7), NO VERDICT WEIGHT",
            "by_arm": sister,
            "definition": "open-vocabulary argmax over ALL anchors on the same held-out eval "
                          "sentences. sister_conversion = among items where P0's top-1 was a "
                          "WordNet loose-criterion sibling of the target but not the target, the "
                          "fraction this arm gets exactly right -- the operational form of "
                          "'separates members within a neighbourhood'"},
        "anchors_only_diagnostic": {
            "prereg_status": "LABELLED SECONDARY, NO VERDICT WEIGHT",
            "acc": anchors_only,
            "definition": "projection applied to the anchor rows ONLY, query left alone"},

        "arms_differ_verified": True, "arm_digests": digests,
        "baseline_in_band": baseline_in_band, "baseline_arm": "P0_BASELINE",
        "item_construction": item_diag,
        "held_out": {"k_sentences_per_word": BASE.K_SENT, "n_profile": BASE.N_PROFILE,
                     "disjoint": "profile and eval pools disjoint by construction (C1 testbed); "
                                 "no sentence that builds an anchor is ever scored"},
        "corpus": {"path": "data/corpora/simplewiki/simplewiki_clean_v1.txt",
                   "n_lines": assets["n_lines"], "vocab_size": assets["vocab_size"],
                   "n_pairs_strict": len(assets["pairs_strict"])},
        "wordnet_version": assets["wordnet_version"],
        "organs_reused": {
            "context_encoder": "hdlab.reading_grounding_loop.context_vector_masked (via the C1 "
                               "testbed's _ctx_masked_multi)",
            "anchor_accumulator": "hdlab.reading_grounding_loop.ConceptSpace(.observe)",
            "read_out": "hdlab.reading_grounding_loop.canonicalize_fast (equivalence-controlled)",
            "testbed": "experiments/exp_context_conditioned_near_neighbour_v1.py imported whole; "
                       "items, leak controls, splits and derangement REUSED, not re-implemented",
            "only_new_mechanism": "the rank-1 linear maps in build_projections/apply_projection"},
        "n_units": len(units), "expected_n_units": n_arms, "cardinality_ok": cardinality_ok,
        "crlb": {"crlb_formula_reference": "paired-binomial se(delta) = sqrt(p_disc/n)",
                 "crlb_floor_computed": round(float(1.96 * np.sqrt(0.10 / max(n, 1))), 6),
                 "discriminator_reachability": bool(1.96 * np.sqrt(0.10 / max(n, 1)) < HP_DELTA),
                 "note": "p_disc=0.10 conservative; reported mde_95 per delta is 1.96*bootstrap sd"},
        "compute_architecture": "sequential-CPU; thread pins set before numpy import",
        "storage_strategy": "sharded (one anchor vector per word); no_composition (single-hop)",
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
        for k in SMOKE_ITEM_SCALES:                 # DISCRIMINATOR-MUST-SURVIVE-SCALE
            out = OUT_SMOKE + "_n%d" % k
            print("=== SMOKE at max_items=%d -> %s ===" % (k, out), flush=True)
            m = run("smoke", out, k)
            if m["n_items"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d: %d items" % (k, m["n_items"]))
            if not m["positive_control_identity_projection_equivalence"]["bit_identical"]:
                raise AssertionError(
                    "BLOCK_DISPATCH: identity projection is NOT bit-identical to canonicalize_fast "
                    "at n=%d (%d mismatches)" % (k, m["positive_control_identity_projection_"
                                                      "equivalence"]["n_mismatch"]))
            if m["positive_control_self_retrieval"]["value"] < SELF_RETRIEVAL_FLOOR:
                raise AssertionError("BLOCK_DISPATCH: SELF_RETRIEVAL %.4f < %.2f"
                                     % (m["positive_control_self_retrieval"]["value"],
                                        SELF_RETRIEVAL_FLOOR))
            if not m["baseline_in_band"]:
                raise AssertionError("META_RULE_AG: baseline out of band at %d" % k)
            accs = {a: m["arm_accuracy"][a] for a in NAMED_ARMS}
            if len(sorted(set(round(v, 6) for v in accs.values()))) == 1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: all named arms identical at %d: %r"
                                     % (k, accs))
            for a, v in accs.items():
                if v in (0.0, 1.0):
                    raise AssertionError("INSTRUMENTATION_SUSPECT: arm %s pinned at %r" % (a, v))
            # the discriminator must be able to FIRE at this scale, not merely be computable
            if not m["crlb"]["discriminator_reachability"] and k == SMOKE_ITEM_SCALES[-1]:
                print("[smoke] NOTE: at n=%d the %.2f discriminator is below the CRLB floor "
                      "(%.4f); FULL at n=%d is where it is reachable"
                      % (k, HP_DELTA, m["crlb"]["crlb_floor_computed"], MAX_ITEMS), flush=True)
            if m["elapsed_s"] < 0.1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: <100ms exit at %d" % k)
            print("[smoke] n%d OK: named=%s d_P1=%.4f mu_rand=%.4f sd_rand=%.4f"
                  % (k, json.dumps(accs), m["primary_delta"]["delta"],
                     m["random_direction_control"]["mean_delta_vs_P0"],
                     m["random_direction_control"]["between_projection_draw_sd"]), flush=True)
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
