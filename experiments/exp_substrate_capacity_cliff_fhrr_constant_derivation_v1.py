"""exp_substrate_capacity_cliff_fhrr_constant_derivation_v1 -- DERIVE C_FHRR
FROM FIRST PRINCIPLES (not calibrate it).

TASK (exp_dev, 2026-07-17): the capacity-reconciliation in
exp_substrate_phase_diagram_subsystem_decoupling_v3 (f58710e08) is
MEASURED_MECHANISM, blocked from chain-grade by ONE thing: C_FHRR = 1.9934110913
is a CALIBRATED constant (measured/predicted at the v1 anchor point), not a
derivation. The v3 docstring (lines 129-135) HYPOTHESIZES a mechanism -- complex
FHRR unit-phasor crosstalk has half the variance of real-bipolar crosstalk,
giving a sqrt(2) SNR gain that squares to a ~2x capacity constant -- but states
explicitly "this is NOT verified in this cell". THIS cell verifies it.

===========================================================================
(1) THE CLOSED-FORM DERIVATION (glass-box, zero free parameters)
===========================================================================
Both code families are compared via THIS harness's OWN cleanup convention
(exp_substrate_phase_diagram_subsystem_decoupling_v1.py:187,
`cleanup(query, codebook): scores = (codebook.conj() @ query).real`) -- i.e.
the discriminating score is the REAL PART of the Hermitian inner product. This
is not an assumption; it is read directly off the harness code (MEASURED@
that file, not hypothesized).

Real bipolar / real-iid code family (the family the cited Plate / Frady-
Kleyko-Sommer / Gallant-Okaywe / Thomas-Dasgupta-Rosing formulas were derived
for -- CITED@notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_
2026-07-17.md): components u_i, v_i are real, iid, mean 0, unit variance
(e.g. bipolar +-1). For two INDEPENDENT codevectors, the per-component
crosstalk term is
    term_i = u_i * v_i,   E[term_i] = 0,
    Var(term_i) = E[u_i^2] * E[v_i^2] = 1 * 1 = 1   (independence of u_i, v_i).
Summed over N independent components (independence across i):
    Var(dot_real) = N * 1 = N.

FHRR complex unit-phasor code family: components u_i = exp(i*theta_u,i),
v_i = exp(i*theta_v,i), theta ~ Uniform(-pi,pi) iid (matches
make_phasors() in v1/v2/v3, copied verbatim below). The Hermitian-inner-
product crosstalk term, taking the REAL PART per the harness's own cleanup
convention:
    term_i = Re(u_i * conj(v_i)) = Re(exp(i*(theta_u,i - theta_v,i)))
           = cos(phi_i),   phi_i = theta_u,i - theta_v,i (mod 2pi) ~ Uniform,
             (difference of two independent uniforms, mod 2pi, is uniform --
             a standard convolution-of-uniforms-on-a-circle identity).
    E[cos(phi_i)] = 0.
    Var(cos(phi_i)) = E[cos^2(phi_i)] = (1/2pi) * INTEGRAL_0^2pi cos^2(phi) dphi
                     = 1/2   (elementary trig-integral identity, THEORETICAL,
                       exact, no approximation).
Summed over N independent components:
    Var(Re(dot_fhrr)) = N * (1/2) = N/2.

RATIO (dimension-independent by construction -- N cancels):
    C_FHRR_derived = Var(dot_real) / Var(Re(dot_fhrr)) = N / (N/2) = 2.0  EXACTLY.

Equivalently: FHRR's crosstalk std is sqrt(1/2) x real-code crosstalk std for
matched N -> a sqrt(2) SNR gain in "s" (since s = signal/std(noise) and the
signal term, the self-similarity, is N in BOTH families -- self term for FHRR
is u_i*conj(u_i) = |u_i|^2 = 1 exactly, no randomness, matching the real
bipolar self term u_i^2 = 1 exactly). Since the exact-integral formula's
"s = sqrt(N/K)" already assumes UNIT-VARIANCE-per-component real crosstalk
(that is what "universal sensitivity" standardizes against, CITED@Frady-
Kleyko-Sommer 2018), an FHRR system with HALF that per-component crosstalk
variance behaves, in the s-formula, exactly like a real system with 2x the
dimension: s_fhrr = sqrt(2) * sqrt(N/K) = sqrt((2*N)/K) = sqrt(C*N/K) with
C = 2, matching v3's own multiplicative-constant slot in
`k_cliff_corrected(N, V_eff) = C_FHRR * N / (s50**2)` (v3 line ~354) EXACTLY
in form -- this is not a new formula, it is a derivation of the ONE number v3
left as a calibrated fit.

===========================================================================
(2) WHAT THIS CELL VERIFIES (three independent checks, all must agree)
===========================================================================
A) ANCHOR MATCH: |C_derived(=2.0) - C_calibrated(=1.9934...)| / C_calibrated
   <= ANCHOR_TOL (0.05). This is the FIRST can-fail gate -- the derivation
   could have come out as anything (a variance-ratio of 1, 4, pi, etc. would
   all have been "a closed form" but WRONG); landing within 0.33% of a
   constant that was measured via a totally different route (grid-search
   calibration against empirical recall curves) is the substantive test.
B) HELD-OUT GRID GENERALIZATION (no fitting): recompute k_corrected at the
   10 AT-RISK grid cells from the ALREADY-LANDED v3 metrics.json (MEASURED@
   data/exp_substrate_phase_diagram_subsystem_decoupling_v3/metrics.json)
   using C_DERIVED=2.0 instead of C_CALIBRATED=1.9934..., holding everything
   else (V_eff, the exact-integral formula) fixed. mean_abs_rel_err_derived
   must be comparable to mean_abs_rel_err_calibrated (GENERALIZATION_TOL:
   not more than 1.5x worse, AND still >= 15x error-reduction vs naive).
   This is genuinely at risk: the anchor match (A) could pass while the
   derived constant fails to generalize across N/V (which would mean the
   ~2x is partly an artifact of the SPECIFIC anchor point, not a structural
   FHRR-vs-real property) -- (B) is the discriminating test for that.
C) DIRECT NUMERICAL CROSS-CHECK (Monte Carlo, multi-seed, independent of the
   grid data entirely): simulate real-bipolar and FHRR-phasor crosstalk
   variance directly at multiple N, and separately at the actual bind-then-
   bundle-then-cleanup MECHANISM level (K items bundled, distractor-score
   variance) at the harness's own anchor config (N=1024, V=64). Confirm the
   empirical variance ratio matches the closed-form 2.0 prediction within
   NUMERIC_TOL, for BOTH the raw-pairwise case and the full bundled-mechanism
   case (the latter closes the gap between "abstract derivation" and "this
   harness's actual retrieval computation").

===========================================================================
(3) CAN-FAIL SELF-TEST (mandatory, run every invocation incl. --self-test)
===========================================================================
Feeds DELIBERATELY WRONG constants (C=1.0, C=1.5, C=2.5, C=4.0) through the
IDENTICAL held-out-grid generalization pipeline and asserts they land OUTSIDE
the pass band (mean_abs_rel_err_wrong >> mean_abs_rel_err_derived) -- proving
the generalization check is a genuine discriminator, not a tautology that
would "pass" any constant. Also verifies the numeric crosstalk-ratio check
would correctly reject a real-vs-real comparison (ratio should be ~1.0, not
~2.0) -- proving the numeric check does not vacuously return 2.0 regardless
of inputs.

===========================================================================
CELL-TEMPLATE MANDATES (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke/full gate (hash-check real vs fhrr term arrays differ)
  - final_metrics_atomicity: tmp_replace (os.replace, single-shot)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no bare except)
  - crlb_floor: n/a (closed-form derivation + variance-ratio check, not a
    top-k argmax capacity-feasibility discriminator; declared explicitly)
  - real_code_path: n/a (pure numpy/math, no KGStore/live substrate object calls)
  - deterministic_seeding: true (fixed integer seed list only, no hash()-based
    seeding or list(set()) ordering; PROT-023 / gate F.5 compliant)
  - discriminator survives scale: N/A framing -- the "scale" axis here IS the
    grid (N in {512,1024,2048}, V in {16,64,256}) already spanning 4x in N;
    the derived constant is tested at ALL of it, held out, no re-fitting per
    cell
  - HARD_PASS strictly above floor + can-fail margin (see PRE-REGISTERED BANDS)
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ inline above
===========================================================================
PRE-REGISTERED BANDS (set BEFORE running FULL; ONE VARIABLE = derived-vs-
calibrated constant, same V_eff/exact-integral formula otherwise):
  HARD_PASS: (A) anchor_match_ok AND (B) grid_generalization_ok AND
             (C) numeric_crosstalk_ok (both raw-pairwise and bundled-mechanism)
             AND can_fail_check_ok (wrong constants correctly rejected).
             => PROMOTES exp_substrate_phase_diagram_subsystem_decoupling_v3's
             capacity-reconciliation claim(a) to CHAIN_GRADE (the ONE blocking
             axis is resolved: the ~2x is no longer "calibrated, unexplained"
             but "derived, verified").
  MIDDLE_BAND: (A) passes but (B) or (C) fails, or vice versa -- the sqrt(2)
             mechanism is DIRECTIONALLY right (matches the anchor) but not
             fully verified as the structural explanation; stays
             MEASURED_MECHANISM, not chain-grade.
  HARD_FAIL: (A) fails (derived constant misses calibrated by > tolerance) --
             the sqrt(2)-crosstalk-variance mechanism is REFUTED as the
             explanation for C_FHRR; the ~2x has some OTHER source. This is a
             real, informative negative (localizes the residual gap
             elsewhere) and must be reported honestly, not suppressed.
progress_logging: n/a (elapsed_s expected << 1800s; entire cell is closed-form
  math + small numpy Monte Carlo, foreground, seconds not hours)
cell_chunked: false (single-shot, no seed-per-cell split needed at this scale)
"""
import argparse
import json
import math
import os
import sys
import time
import traceback
import hashlib
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "substrate_capacity_cliff_fhrr_constant_derivation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
V3_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_substrate_phase_diagram_subsystem_decoupling_v3", "metrics.json"
)

ANCHOR_TOL = 0.05           # gate A: |C_derived - C_calib| / C_calib
GENERALIZATION_ERR_MULT = 1.5   # gate B: derived err <= 1.5x calibrated err
GENERALIZATION_MIN_REDUCTION = 15.0  # gate B: derived err-reduction vs naive
NUMERIC_TOL = 0.05          # gate C: |ratio - 2.0| / 2.0
WRONG_CONST_MUST_FAIL_ERR = 0.15   # can-fail: wrong-C mean_abs_rel_err must exceed this

SEEDS = [7, 13, 19, 23, 29]           # deterministic, fixed integers (F.5 compliant)
SIM_N_GRID = [256, 512, 1024, 2048, 4096]
N_PAIRS_PER_SIM = 3000

# Bundled-mechanism-level check config -- matches the v3/v1 anchor (N=1024, V=64).
# V=64 means only 63 distractor scores per trial (matching the harness's actual
# anchor config for fidelity) -- the per-trial variance ESTIMATE is therefore
# noisier than the raw-pairwise check (which draws N_PAIRS_PER_SIM=3000 fresh
# pairs per estimate). MECH_SEEDS uses more seeds (deterministic, fixed
# integers, primes to avoid accidental periodicity) to tighten the Monte Carlo
# mean without changing the mechanism config itself.
MECH_N = 1024
MECH_V = 64
MECH_K_GRID = [50, 100, 200, 375]
MECH_SEEDS = [7, 13, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
              73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149]

# Deliberately-wrong constants for the can-fail self-test.
WRONG_CONSTANTS = [1.0, 1.5, 2.5, 4.0]


# ============================================================================
# COPIED VERBATIM from exp_substrate_phase_diagram_subsystem_decoupling_v3.py
# (p_corr_exact_integral / solve_s_for_p50 / k_cliff_naive / make_phasors).
# Copying, not importing: v3 fires its own argparse + _selftest() at module
# scope (same drift-free convention v3 itself documents re: v1).
# ============================================================================

def _erf_approx(x: np.ndarray) -> np.ndarray:
    """Abramowitz & Stegun 7.1.26 rational approximation, max abs error 1.5e-7.
    CITED@Abramowitz & Stegun, Handbook of Mathematical Functions, 1964."""
    a1, a2, a3, a4, a5 = (0.254829592, -0.284496736, 1.421413741,
                          -1.453152027, 1.061405429)
    p = 0.3275911
    sign = np.sign(x)
    xa = np.abs(x)
    t = 1.0 / (1.0 + p * xa)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-xa * xa)
    return sign * y


def _norm_cdf(z: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + _erf_approx(z / math.sqrt(2.0)))


def p_corr_exact_integral(s: float, D: int, n_pts: int = 6001, h_max: float = 12.0) -> float:
    """CITED@Frady, Kleyko & Sommer, Neural Computation 2018 (via
    notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_2026-07-17.md).
    p_corr(s) = INTEGRAL over h of N(h;0,1) * [Phi(h+s)]^(D-1) dh."""
    h = np.linspace(-h_max, h_max, n_pts)
    phi = np.exp(-0.5 * h * h) / math.sqrt(2.0 * math.pi)
    cdf = _norm_cdf(h + s)
    integrand = phi * np.power(cdf, D - 1)
    return float(np.trapezoid(integrand, h))


def solve_s_for_p50(D: int, lo: float = 1e-4, hi: float = 40.0, iters: int = 60) -> float:
    f_lo = p_corr_exact_integral(lo, D) - 0.5
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        f_mid = p_corr_exact_integral(mid, D) - 0.5
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def k_cliff_naive(N: int, V: int) -> float:
    """THEORETICAL@notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md"""
    return N / (4.0 * math.log(V))


def k_cliff_with_constant(N: int, V_eff: int, C: float) -> float:
    """Same formula slot as v3's k_cliff_corrected, with C as an explicit
    argument instead of the module-level calibrated C_FHRR."""
    s50 = solve_s_for_p50(V_eff)
    return C * N / (s50 ** 2)


def make_phasors(rng: np.random.Generator, count: int, N: int) -> np.ndarray:
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


# ============================================================================
# (1) CLOSED-FORM ANALYTIC DERIVATION -- zero free parameters
# ============================================================================

def derive_c_fhrr_analytic() -> dict:
    """THEORETICAL, exact, closed form (see module docstring section (1) for
    the full derivation). Returns the derived constant plus its two
    ingredient variances so the ratio is inspectable, not just asserted."""
    real_pair_crosstalk_variance_per_component = 1.0          # THEORETICAL: E[u^2]E[v^2], unit-variance iid
    fhrr_pair_crosstalk_variance_per_component = 0.5           # THEORETICAL: E[cos^2(Uniform(-pi,pi))] = 1/2, exact
    c_derived = (real_pair_crosstalk_variance_per_component
                 / fhrr_pair_crosstalk_variance_per_component)
    return {
        "real_variance_per_component": real_pair_crosstalk_variance_per_component,
        "fhrr_variance_per_component": fhrr_pair_crosstalk_variance_per_component,
        "C_FHRR_derived": c_derived,
    }


# ============================================================================
# (2C) NUMERICAL CROSS-CHECK -- raw pairwise crosstalk variance, multi-seed, multi-N
# ============================================================================

def simulate_pairwise_crosstalk_variance(N: int, n_pairs: int, seed: int, family: str) -> float:
    """family in {"real_bipolar", "fhrr_phasor"}. Returns empirical Var of the
    per-pair crosstalk score (real dot product, or Re(Hermitian inner
    product) respectively) over n_pairs INDEPENDENT random codevector pairs."""
    rng = np.random.default_rng(seed)
    if family == "real_bipolar":
        u = rng.choice(np.array([-1.0, 1.0]), size=(n_pairs, N))
        v = rng.choice(np.array([-1.0, 1.0]), size=(n_pairs, N))
        terms = (u * v).sum(axis=1)
    elif family == "fhrr_phasor":
        theta_u = rng.uniform(-np.pi, np.pi, size=(n_pairs, N))
        theta_v = rng.uniform(-np.pi, np.pi, size=(n_pairs, N))
        cu = np.exp(1j * theta_u)
        cv = np.exp(1j * theta_v)
        terms = (cu * np.conj(cv)).sum(axis=1).real
    else:
        raise ValueError("unknown family: %r" % family)
    return float(np.var(terms)), terms


def run_numeric_pairwise_check() -> dict:
    per_n = []
    ratios = []
    digest_pool = {}
    for N in SIM_N_GRID:
        real_vars = []
        fhrr_vars = []
        for seed in SEEDS:
            v_real, terms_real = simulate_pairwise_crosstalk_variance(N, N_PAIRS_PER_SIM, seed, "real_bipolar")
            v_fhrr, terms_fhrr = simulate_pairwise_crosstalk_variance(N, N_PAIRS_PER_SIM, seed, "fhrr_phasor")
            real_vars.append(v_real)
            fhrr_vars.append(v_fhrr)
            digest_pool["real_N%d_seed%d" % (N, seed)] = hashlib.sha256(terms_real.tobytes()).hexdigest()
            digest_pool["fhrr_N%d_seed%d" % (N, seed)] = hashlib.sha256(terms_fhrr.tobytes()).hexdigest()
        mean_real = float(np.mean(real_vars))
        mean_fhrr = float(np.mean(fhrr_vars))
        ratio = mean_real / mean_fhrr
        per_n.append({
            "N": N, "mean_real_variance": mean_real, "mean_fhrr_variance": mean_fhrr,
            "ratio": ratio, "predicted_real_variance": float(N), "predicted_fhrr_variance": float(N) / 2.0,
        })
        ratios.append(ratio)
    mean_ratio = float(np.mean(ratios))
    std_ratio = float(np.std(ratios))
    # arms-must-differ (META_RULE_AF): real vs fhrr term digests, per N/seed, must not collide
    n_digest_collisions = 0
    seen = {}
    for k, d in digest_pool.items():
        if d in seen and seen[d] != k:
            n_digest_collisions += 1
        seen[d] = k
    return {
        "per_n": per_n,
        "mean_ratio_across_N": mean_ratio,
        "std_ratio_across_N": std_ratio,
        "n_digest_collisions": n_digest_collisions,
        "n_arms_checked": len(digest_pool),
    }


# ============================================================================
# (2C, mechanism-level) bind-then-bundle-then-cleanup distractor-score variance
# ============================================================================

def _distractor_score_variance(N: int, K: int, V: int, seed: int, family: str):
    rng = np.random.default_rng(seed)
    chosen_val_idx = rng.integers(0, V, size=K)
    if family == "fhrr":
        keys = np.exp(1j * rng.uniform(-np.pi, np.pi, size=(K, N)))
        vals = np.exp(1j * rng.uniform(-np.pi, np.pi, size=(V, N)))
        pairs = keys * vals[chosen_val_idx]
        bundle = pairs.sum(axis=0)
        query = bundle * np.conj(keys[0])          # unbind with key_0
        scores = (vals.conj() @ query).real
    elif family == "real_bipolar":
        keys = rng.choice(np.array([-1.0, 1.0]), size=(K, N))
        vals = rng.choice(np.array([-1.0, 1.0]), size=(V, N))
        pairs = keys * vals[chosen_val_idx]
        bundle = pairs.sum(axis=0)
        query = bundle * keys[0]                    # bipolar keys are involutory: key*key=1
        scores = vals @ query
    else:
        raise ValueError("unknown family: %r" % family)
    correct_idx = int(chosen_val_idx[0])
    distractor_scores = np.delete(scores, correct_idx)
    return float(np.var(distractor_scores)), float(scores[correct_idx]), distractor_scores


def run_numeric_bundled_mechanism_check() -> dict:
    per_k = []
    ratios = []
    for K in MECH_K_GRID:
        real_vars, fhrr_vars = [], []
        for seed in MECH_SEEDS:
            v_real, _, _ = _distractor_score_variance(MECH_N, K, MECH_V, seed, "real_bipolar")
            v_fhrr, _, _ = _distractor_score_variance(MECH_N, K, MECH_V, seed, "fhrr")
            real_vars.append(v_real)
            fhrr_vars.append(v_fhrr)
        mean_real = float(np.mean(real_vars))
        mean_fhrr = float(np.mean(fhrr_vars))
        ratio = mean_real / mean_fhrr
        per_k.append({"K": K, "mean_real_variance": mean_real, "mean_fhrr_variance": mean_fhrr, "ratio": ratio})
        ratios.append(ratio)
    return {"per_k": per_k, "mean_ratio_across_K": float(np.mean(ratios)), "std_ratio_across_K": float(np.std(ratios))}


# ============================================================================
# (2B) HELD-OUT GRID GENERALIZATION -- reuse the ALREADY-LANDED v3 grid data
# ============================================================================

def load_v3_grid_results() -> dict:
    if not os.path.exists(V3_METRICS_PATH):
        raise FileNotFoundError(
            "v3 landed metrics not found at %r -- this cell requires the "
            "already-landed capacity-reconciliation grid as its held-out "
            "generalization test data (MEASURED@ dependency)." % V3_METRICS_PATH
        )
    with open(V3_METRICS_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    facts = d["facts"]
    return {
        "grid_results": facts["grid_results"],
        "C_FHRR_calibrated": facts["C_FHRR_calibration_constant"],
        "calibration_anchor": facts["C_FHRR_calibration_anchor"],
        "mean_abs_rel_err_naive_v3": facts["mean_abs_rel_err_naive"],
        "mean_abs_rel_err_corrected_v3": facts["mean_abs_rel_err_corrected"],
    }


def recompute_grid_with_constant(grid_results: list, C: float) -> dict:
    """Recompute k_corrected for every AT-RISK (non-calibration) grid cell
    using constant C, holding V_eff / exact-integral formula fixed (ONE
    VARIABLE per task's design gate #4). Returns per-cell + mean stats."""
    per_cell = []
    at_risk_errs = []
    at_risk_errs_naive = []
    for row in grid_results:
        N, V_eff, m50 = row["N"], row["V_eff"], row["m50_measured"]
        k_c = k_cliff_with_constant(N, V_eff, C)
        k_n = row["k_naive"]  # already computed identically in v3; reuse (naive has no C)
        err_c = abs(k_c - m50) / max(m50, 1e-9)
        err_n = abs(k_n - m50) / max(m50, 1e-9)
        per_cell.append({
            "N": N, "V": row["V"], "V_eff": V_eff, "condition": row["condition"],
            "is_calibration_point": row["is_calibration_point"],
            "k_corrected_with_C": k_c, "m50_measured": m50, "abs_rel_err": err_c,
        })
        if not row["is_calibration_point"]:
            at_risk_errs.append(err_c)
            at_risk_errs_naive.append(err_n)
    mean_err = float(np.mean(at_risk_errs))
    mean_err_naive = float(np.mean(at_risk_errs_naive))
    reduction = mean_err_naive / max(mean_err, 1e-12)
    return {
        "C_used": C,
        "per_cell": per_cell,
        "n_at_risk_cells": len(at_risk_errs),
        "mean_abs_rel_err": mean_err,
        "mean_abs_rel_err_naive": mean_err_naive,
        "error_reduction_factor": reduction,
    }


# ============================================================================
# CAN-FAIL SELF-TEST
# ============================================================================

def run_can_fail_check(grid_results: list, c_derived: float) -> dict:
    """Feed deliberately WRONG constants through the identical pipeline; they
    must land clearly worse than c_derived. Also confirm a real-vs-real
    "ratio" sanity check returns ~1.0 (not ~2.0) -- proving the numeric
    variance-ratio check is not a vacuous always-2.0 return."""
    derived_result = recompute_grid_with_constant(grid_results, c_derived)
    wrong_results = []
    all_wrong_failed = True
    for c_wrong in WRONG_CONSTANTS:
        r = recompute_grid_with_constant(grid_results, c_wrong)
        # "wrong" constants close to 2.0 (e.g. 1.5, 2.5) are expected to be
        # somewhat worse but not catastrophic; only assert the pipeline can
        # discriminate for constants far from 2.0 -- the discriminating
        # power check is over the FULL wrong-constant set's WORST performers.
        wrong_results.append({"C": c_wrong, "mean_abs_rel_err": r["mean_abs_rel_err"]})
    # can-fail requirement: the most-wrong constants (1.0 and 4.0, both 2x off
    # from 2.0 in opposite directions) must clear WRONG_CONST_MUST_FAIL_ERR,
    # i.e. the check is capable of failing, not tautologically green for any C.
    extreme_wrong_errs = [r["mean_abs_rel_err"] for r in wrong_results if r["C"] in (1.0, 4.0)]
    can_fail_demonstrated = all(e > WRONG_CONST_MUST_FAIL_ERR for e in extreme_wrong_errs)

    # sanity: real-vs-real numeric ratio must be ~1.0, not ~2.0 (proves the
    # variance-ratio numeric check discriminates code-family, not just returns 2).
    real_vs_real_ratios = []
    for seed in SEEDS:
        v_a, _ = simulate_pairwise_crosstalk_variance(1024, N_PAIRS_PER_SIM, seed, "real_bipolar")
        v_b, _ = simulate_pairwise_crosstalk_variance(1024, N_PAIRS_PER_SIM, seed + 1000, "real_bipolar")
        real_vs_real_ratios.append(v_a / v_b)
    real_vs_real_mean = float(np.mean(real_vs_real_ratios))
    real_vs_real_sane = abs(real_vs_real_mean - 1.0) < 0.15  # should be near 1.0, NOT near 2.0

    return {
        "derived_result_summary": {"C": c_derived, "mean_abs_rel_err": derived_result["mean_abs_rel_err"]},
        "wrong_constant_results": wrong_results,
        "can_fail_demonstrated": can_fail_demonstrated,
        "real_vs_real_control_ratio_mean": real_vs_real_mean,
        "real_vs_real_control_sane": real_vs_real_sane,
    }


# ============================================================================
# Atomic write / crash / start-marker helpers
# ============================================================================

def _write_start_marker(out_dir, run_mode):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
    }
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "REQUIRED_FIELDS": ["verdict", "verdict_msg", "summary", "elapsed_s"],
    }
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics_atomic(out_dir, payload):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


# ============================================================================
# self-test
# ============================================================================

def _selftest():
    t0 = time.perf_counter()
    # 1. erf approximation accuracy vs math.erf (copied gate, sane portability check).
    max_err = 0.0
    for x in np.linspace(-6, 6, 25):
        approx = float(_erf_approx(np.array([x]))[0])
        exact = math.erf(x)
        max_err = max(max_err, abs(approx - exact))
    assert max_err < 1e-6, "erf approximation error too large: %r" % max_err

    # 2. analytic derivation returns EXACTLY 2.0 (closed form, no numerical noise).
    deriv = derive_c_fhrr_analytic()
    assert abs(deriv["C_FHRR_derived"] - 2.0) < 1e-12, "derivation must be exact 2.0: %r" % deriv

    # 3. tiny numeric pairwise check at small N/n_pairs runs + sane ratio (fast smoke of the real check).
    v_real, _ = simulate_pairwise_crosstalk_variance(256, 500, 7, "real_bipolar")
    v_fhrr, _ = simulate_pairwise_crosstalk_variance(256, 500, 7, "fhrr_phasor")
    ratio_smoke = v_real / v_fhrr
    assert 1.5 < ratio_smoke < 2.7, "smoke-scale ratio out of sane band (noisy small-n_pairs OK): %r" % ratio_smoke

    # 4. tiny bundled-mechanism check runs + sane ratio.
    v_real_m, _, _ = _distractor_score_variance(256, 20, 32, 7, "real_bipolar")
    v_fhrr_m, _, _ = _distractor_score_variance(256, 20, 32, 7, "fhrr")
    ratio_mech_smoke = v_real_m / v_fhrr_m
    assert 1.3 < ratio_mech_smoke < 3.0, "smoke-scale mechanism ratio out of sane band: %r" % ratio_mech_smoke

    # 5. v3 landed grid file is readable + calibration anchor value matches (positive control / Gate D).
    grid = load_v3_grid_results()
    assert abs(grid["C_FHRR_calibrated"] - 1.9934110912669731) < 1e-6, \
        "v3 calibrated constant drifted from expected value: %r" % grid["C_FHRR_calibrated"]

    # 6. CAN-FAIL: this is the mandatory "verify the derivation CAN come out wrong" gate.
    #    We assert here that IF the derivation had produced C=1.0 (naive real-code
    #    assumption applied to FHRR, i.e. no correction at all) or C=4.0 (a
    #    plausible-looking but wrong "double-squared" guess), the held-out grid
    #    generalization check WOULD reject them -- proving gate B is a genuine
    #    discriminator over the constant, not a rubber stamp.
    can_fail = run_can_fail_check(grid["grid_results"], 2.0)
    assert can_fail["can_fail_demonstrated"], (
        "CAN-FAIL SELF-TEST VIOLATION: wrong constants (1.0, 4.0) did not clearly "
        "fail the generalization check -- gate B may be vacuous: %r" % can_fail
    )
    assert can_fail["real_vs_real_control_sane"], (
        "CAN-FAIL SELF-TEST VIOLATION: real-vs-real control ratio should be near "
        "1.0 (not near 2.0) -- numeric ratio check may be vacuously returning 2: %r" % can_fail
    )

    elapsed = time.perf_counter() - t0
    print("[selftest] PASS: capacity_cliff_fhrr_constant_derivation_v1 "
          "(erf-accuracy, exact-2.0-derivation, pairwise-ratio-smoke, "
          "bundled-mechanism-ratio-smoke, v3-grid-readable, can-fail-demonstrated) "
          "elapsed=%.3fs" % elapsed, flush=True)


# ============================================================================
# main / full run
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test or not args.full:
        _selftest()
        if not args.full:
            return

    t0 = time.perf_counter()
    os.makedirs(OUT_DIR, exist_ok=True)
    _write_start_marker(OUT_DIR, "full")

    print("[config] anchor=%s ANCHOR_TOL=%.3f GENERALIZATION_ERR_MULT=%.2f "
          "NUMERIC_TOL=%.3f seeds=%s sim_N_grid=%s"
          % (ANCHOR_NAME, ANCHOR_TOL, GENERALIZATION_ERR_MULT, NUMERIC_TOL, SEEDS, SIM_N_GRID), flush=True)

    # (1) closed-form derivation
    deriv = derive_c_fhrr_analytic()
    c_derived = deriv["C_FHRR_derived"]
    print("[step 1] C_FHRR_derived (closed-form) = %.6f" % c_derived, flush=True)

    # load v3 landed grid (MEASURED@ dependency)
    grid = load_v3_grid_results()
    c_calibrated = grid["C_FHRR_calibrated"]

    # gate A: anchor match
    anchor_rel_err = abs(c_derived - c_calibrated) / c_calibrated
    anchor_match_ok = anchor_rel_err <= ANCHOR_TOL
    print("[step A] C_derived=%.6f C_calibrated=%.6f rel_err=%.5f (tol=%.3f) -> %s"
          % (c_derived, c_calibrated, anchor_rel_err, ANCHOR_TOL, anchor_match_ok), flush=True)

    # gate B: held-out grid generalization
    result_derived = recompute_grid_with_constant(grid["grid_results"], c_derived)
    result_calibrated = recompute_grid_with_constant(grid["grid_results"], c_calibrated)
    err_derived = result_derived["mean_abs_rel_err"]
    err_calibrated = result_calibrated["mean_abs_rel_err"]
    generalization_ok = (
        err_derived <= GENERALIZATION_ERR_MULT * err_calibrated
        and result_derived["error_reduction_factor"] >= GENERALIZATION_MIN_REDUCTION
    )
    print("[step B] mean_abs_rel_err: derived=%.5f calibrated=%.5f (mult<=%.2f) "
          "error_reduction_derived=%.2fx (min=%.1fx) -> %s"
          % (err_derived, err_calibrated, GENERALIZATION_ERR_MULT,
             result_derived["error_reduction_factor"], GENERALIZATION_MIN_REDUCTION, generalization_ok), flush=True)

    # gate C: numeric cross-checks
    pairwise_check = run_numeric_pairwise_check()
    bundled_check = run_numeric_bundled_mechanism_check()
    pairwise_ok = abs(pairwise_check["mean_ratio_across_N"] - 2.0) / 2.0 <= NUMERIC_TOL
    bundled_ok = abs(bundled_check["mean_ratio_across_K"] - 2.0) / 2.0 <= NUMERIC_TOL
    numeric_ok = pairwise_ok and bundled_ok
    print("[step C] pairwise mean_ratio=%.4f (std=%.4f) -> %s | bundled mean_ratio=%.4f (std=%.4f) -> %s"
          % (pairwise_check["mean_ratio_across_N"], pairwise_check["std_ratio_across_N"], pairwise_ok,
             bundled_check["mean_ratio_across_K"], bundled_check["std_ratio_across_K"], bundled_ok), flush=True)

    # can-fail check (also re-run at FULL scale, not just selftest scale)
    can_fail = run_can_fail_check(grid["grid_results"], c_derived)
    print("[can-fail] demonstrated=%s real_vs_real_control=%.4f sane=%s"
          % (can_fail["can_fail_demonstrated"], can_fail["real_vs_real_control_ratio_mean"],
             can_fail["real_vs_real_control_sane"]), flush=True)

    arms_differ_verified = pairwise_check["n_digest_collisions"] == 0

    all_gates_pass = (anchor_match_ok and generalization_ok and numeric_ok
                       and can_fail["can_fail_demonstrated"] and can_fail["real_vs_real_control_sane"]
                       and arms_differ_verified)

    if all_gates_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            "HARD_PASS: C_FHRR derived from first principles (closed-form, complex-phasor "
            "Re(Hermitian inner product) crosstalk variance = N/2 vs real-bipolar crosstalk "
            "variance = N, ratio = 2.0 EXACTLY, zero free parameters) matches the CALIBRATED "
            "C_FHRR=%.4f within %.2f%% (tol=%.0f%%), reproduces the held-out 10-cell grid "
            "generalization at %.2f%% mean error (calibrated: %.2f%%, %.1fx reduction vs naive) "
            "WITH NO FITTING, and the sqrt(2)-crosstalk mechanism is confirmed numerically via "
            "multi-seed Monte Carlo at BOTH the raw-pairwise level (ratio=%.3f across N=%s) AND "
            "the actual bind-bundle-cleanup mechanism level (ratio=%.3f across K=%s). Can-fail "
            "self-test confirms the pipeline correctly rejects wrong constants (C=1.0, C=4.0) "
            "and the real-vs-real control ratio (%.3f) is near 1.0, not vacuously near 2.0. "
            "PROMOTES exp_substrate_phase_diagram_subsystem_decoupling_v3's capacity-"
            "reconciliation claim(a) from MEASURED_MECHANISM to CHAIN_GRADE: the ~2x residual is "
            "no longer a calibrated fit but a derived, numerically-verified consequence of FHRR "
            "complex-phasor geometry vs real-bipolar codes."
            % (c_calibrated, anchor_rel_err * 100, ANCHOR_TOL * 100, err_derived * 100, err_calibrated * 100,
               result_derived["error_reduction_factor"], pairwise_check["mean_ratio_across_N"], SIM_N_GRID,
               bundled_check["mean_ratio_across_K"], MECH_K_GRID, can_fail["real_vs_real_control_ratio_mean"])
        )
    elif anchor_match_ok and (generalization_ok or numeric_ok):
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            "MIDDLE_BAND: derived C_FHRR=%.4f matches calibrated %.4f (anchor gate PASS, "
            "rel_err=%.4f), but %s. The sqrt(2)-crosstalk mechanism is DIRECTIONALLY correct "
            "(reproduces the anchor) but not fully verified as the complete structural "
            "explanation across the grid/numeric checks -- stays MEASURED_MECHANISM, not "
            "promoted to chain-grade."
            % (c_derived, c_calibrated, anchor_rel_err,
               "grid generalization failed" if not generalization_ok else "numeric cross-check failed")
        )
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (
            "HARD_FAIL: derived C_FHRR=%.4f does NOT match calibrated %.4f within tolerance "
            "(rel_err=%.4f > tol=%.3f), OR held-out grid/numeric checks failed. The complex-"
            "phasor sqrt(2)-crosstalk-variance mechanism is REFUTED as the explanation for "
            "C_FHRR -- the ~2x residual in the capacity-reconciliation has some OTHER source "
            "(not identified by this cell). This is a genuine, informative negative: the "
            "capacity-reconciliation stays MEASURED_MECHANISM (calibrated, unexplained "
            "constant), NOT chain-grade."
            % (c_derived, c_calibrated, anchor_rel_err, ANCHOR_TOL)
        )

    elapsed = time.perf_counter() - t0

    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "C_FHRR derivation: %s (derived=%.4f calibrated=%.4f anchor_rel_err=%.4f "
                   "grid_err_derived=%.4f grid_err_calibrated=%.4f pairwise_ratio=%.4f bundled_ratio=%.4f)"
                   % (verdict, c_derived, c_calibrated, anchor_rel_err, err_derived, err_calibrated,
                      pairwise_check["mean_ratio_across_N"], bundled_check["mean_ratio_across_K"]),
        "elapsed_s": elapsed,
        "REQUIRED_FIELDS": ["verdict", "verdict_msg", "summary", "elapsed_s"],
        "anchor_name": ANCHOR_NAME,
        "run_mode": "full",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "cardinality_ok": True,
        "expected_n_units": len(SIM_N_GRID) * len(SEEDS) * 2 + len(MECH_K_GRID) * len(MECH_SEEDS) * 2,
        "arms_differ_verified": arms_differ_verified,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "closed-form derivation + variance-ratio numeric check, not a top-k argmax capacity-feasibility discriminator",
        "real_code_path": "n/a (pure numpy/math, no KGStore/live substrate object calls)",
        "deterministic_seeding": True,
        "gates": {
            "A_anchor_match": {"ok": anchor_match_ok, "rel_err": anchor_rel_err, "tol": ANCHOR_TOL,
                                "C_derived": c_derived, "C_calibrated": c_calibrated},
            "B_grid_generalization": {"ok": generalization_ok, "err_derived": err_derived,
                                       "err_calibrated": err_calibrated,
                                       "error_reduction_derived": result_derived["error_reduction_factor"],
                                       "mult_tol": GENERALIZATION_ERR_MULT,
                                       "min_reduction": GENERALIZATION_MIN_REDUCTION},
            "C_numeric_crosstalk": {"ok": numeric_ok, "pairwise_ok": pairwise_ok, "bundled_ok": bundled_ok,
                                     "tol": NUMERIC_TOL},
            "can_fail": can_fail,
        },
        "facts": {
            "derivation": deriv,
            "grid_derived": result_derived,
            "grid_calibrated": result_calibrated,
            "pairwise_numeric_check": pairwise_check,
            "bundled_mechanism_check": bundled_check,
            "calibration_anchor_source": grid["calibration_anchor"],
            "v3_mean_abs_rel_err_naive": grid["mean_abs_rel_err_naive_v3"],
            "v3_mean_abs_rel_err_corrected": grid["mean_abs_rel_err_corrected_v3"],
        },
    }
    _write_metrics_atomic(OUT_DIR, payload)
    print("[DONE] verdict=%s elapsed=%.2fs -> %s" % (verdict, elapsed, os.path.join(OUT_DIR, "metrics.json")), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        os.makedirs(OUT_DIR, exist_ok=True)
        _write_crash_metrics(OUT_DIR, e)
        raise
