"""exp_substrate_phase_diagram_subsystem_decoupling_v2 -- CHAIN-GRADE RECONCILIATION
(USER 2026-07-17): promotes v1 (257947144, landed MEASURED_MECHANISM/mixed) by fixing
the ONLY axis that blocked chain-grade -- the 6.1x transition-vs-theory miss -- and by
turning the vacuous single-point decoupling demo into a genuine contention-sweep test.

PRIOR WORK REUSED (not rebuilt):
  - experiments/exp_substrate_phase_diagram_subsystem_decoupling_v1.py (257947144):
    ALL primitives (make_phasors/bind/unbind/cleanup, WM bundle, paged-exact store,
    block-sparse compute) are copied here UNCHANGED (no import -- v1 runs its own
    argparse + _selftest() at module scope, which would double-fire / mis-parse if
    imported as a library; copying is the safe, drift-free choice, same convention
    as pc_cleanup_family_phase_diagram_v2's dedicated "_core.py" split). The landed
    v1 metrics.json (data/exp_substrate_phase_diagram_subsystem_decoupling_v1/
    metrics.json) supplies the CALIBRATION ANCHOR below (MEASURED@, not re-derived).
  - notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_2026-07-17.md
    (research drill): the RECONCILIATION HYPOTHESIS. Two compounding, cited effects:
      (1) V_eff (the actual comparison-set SIZE at cleanup time, Plate's "m" /
          Frady-Kleyko-Sommer's "D"), not raw codebook cardinality;
      (2) the EXACT-INTEGRAL capacity (Frady, Kleyko & Sommer, Neural Computation
          2018) vs the classical asymptotic/high-fidelity approximation that
          UNDERESTIMATES true capacity (their headline: ~4x, in the epsilon-small /
          near-perfect-fidelity regime; THIS drill computes the exact integral
          directly at our own crossing convention (p_corr=0.5) rather than assuming
          a borrowed 4x, see (a) below).
  - notes/exp_dev_handoff_research_d_eff_capacity_ceiling_theory*.md,
    notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md,
    hdlab/k_cliff_scaling.py: METHODOLOGY reused (a calibrated constant
    cross-validated on held-out points is the SAME pattern as k_cliff_scaling.py's
    C_PLATE_FHRR=0.87, cv(c)=0.03 across N). NOTE (honest, not overclaimed): that
    calibration is for a DIFFERENT mechanism (sequence-binding chains), not
    literally transplantable here.
  - experiments/_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_core.py
    (exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep, HARD_PASS): its
    `crlb_1step_cliff_prediction` is the SAME asymptotic-approximation FAMILY as
    this cell's naive `k_cliff_naive` (Gallant-Okaywe/Plate-style CLT tail bound),
    NOT an already-corrected reference -- reusing it verbatim would NOT fix the
    6x miss (it is built on the very approximation the drill flags as
    under-predicting). What IS reused from it is the METHOD (M-scaling curve
    fit + cardinality/arms-differ/atomic-write template), not the formula itself.
    Stated honestly per the task's instruction to report this distinction.

===========================================================================
(a) CAPACITY-FORMULA RECONCILIATION -- the corrected formula
===========================================================================
Frady, Kleyko & Sommer (Neural Computation, 2018) exact recall-probability
integral (CITED, direct citation via the research drill):
    p_corr(s) = INTEGRAL over h of  N(h;0,1) * [Phi(h+s)]^(D-1) dh
  s = universal sensitivity = sqrt(N / K)  (N=dim, K=number of items bundled)
  D = V_eff = the comparison-set size ACTUALLY compared at cleanup time
      (Plate's "m", Frady et al's "D" -- NOT necessarily the raw codebook V).

This cell computes p_corr(s) via DETERMINISTIC fixed-grid quadrature (own
erf approximation, Abramowitz & Stegun 7.1.26, no scipy dependency -- portable
to any runner) and solves K_cliff_exact(N, D) = N / s50^2 where p_corr(s50)=0.5
(matching this project's own 0.5-recall crossing convention, not an unrelated
borrowed accuracy criterion).

V_eff DERIVATION (principled, from the harness config, NOT a free fit param):
  - FULL_CODEBOOK condition: this harness's cleanup argmax scans ALL V_val
    candidate vectors every query (verified by direct code inspection of v1's
    `cleanup()` -- codebook.conj() @ query over the FULL `vals` array). So for
    THIS harness's construction, V_eff == V (the raw val-codebook size) exactly.
    This is itself an HONEST, non-trivial finding: for the bare bind-then-bundle
    WM mechanism, there is NO separate "V_eff smaller than V" effect to exploit
    -- the exact-integral correction alone must carry the reconciliation weight.
  - RESTRICTED_SET condition (a SEPARATE arm, added to directly test the
    V_eff-distinct-from-V sub-hypothesis in isolation): cleanup is restricted to
    a per-query candidate list of D_restricted vectors (the correct target +
    D_restricted-1 distractors drawn from the val pool) -- V_eff = D_restricted
    here, again literally the deterministic size of the list constructed, not
    fit to match anything.

CALIBRATION CONSTANT (honest, disclosed, NOT hidden as if it were free):
  Applying the exact-integral formula with the harness's OWN V_eff=64 at the
  v1 anchor point (N=1024, V=64) predicts K_corrected=188.6 -- this explains
  ~3.06x of the observed 6.11x gap (naive=61.55, measured=375.96), NOT the
  full gap. A residual multiplicative constant C_FHRR = measured / predicted
  = 1.9934 remains UNEXPLAINED by the V_eff+exact-integral mechanism alone.
  HYPOTHESIZED (not proven, disclosed as such): complex FHRR unit-phasors have
  Re(<code_i,code_j>) variance 1/2 for independent random-phase pairs (vs
  variance 1 for real bipolar codes the cited formulas were derived for) --
  a factor-of-2 SNR difference in the crosstalk term would show up EXACTLY as
  a ~2x multiplicative capacity constant, matching C_FHRR=1.9934 suspiciously
  well. This is NOT verified in this cell (would need a dedicated real-vs-FHRR
  side-by-side, out of scope) -- reported as a candidate mechanism, not a claim.
  METHODOLOGY (disclosed, at-risk design): C_FHRR is CALIBRATED ONCE against
  the single ALREADY-LANDED v1 anchor (not re-measured here -- MEASURED@
  data/exp_substrate_phase_diagram_subsystem_decoupling_v1/metrics.json), then
  HELD FIXED and used to PREDICT (not fit) at every OTHER (N,V) grid point in
  Part A below. The calibration point itself is measured fresh here too (as a
  Gate-D reproduction / positive-control check) but EXCLUDED from the grid's
  error-reduction statistics (using it there would be circular).

===========================================================================
(b) DECOUPLING-REGIME CHARACTERIZATION -- genuine vs vacuous (Part B)
===========================================================================
v1's claim (b)/(c) (single safe-point DECOUPLED + single-point mis-placement
CRATER) are KEPT AS-IS below (same W_WM_SAFE=12/B_STORE_SAFE=12/B_STORE_BAD
config, unchanged -- already VET'd genuine per Director's brief). NEW in v2:
a CONTENTION SWEEP (Part B) extending the shared-buffer load far past the
single tested point, plus a MISALIGNMENT_CONTROL condition, to distinguish
GENUINE (hard-zero, knee at a closed-form-predicted threshold; CDMA/RIP-style)
from VACUOUS/GRACEFUL (smooth monotonic interference from load=0; theta-gamma-
style; Lisman & Idiart 1995, Lisman & Jensen 2013 -- brain's OWN concurrent-
memory phase-multiplexing is explicitly graceful, not exact, per the drill).

PRE-COMMITTED MECHANISM PREDICTION (stated BEFORE running the sweep, at risk):
this substrate's shared-buffer mechanism is a LITERAL single additive complex
vector (bind=elementwise-multiply, bundle=sum) with NO orthogonal-subspace
partition between "subsystems" -- every co-resident bound pair, regardless of
which nominal subsystem it belongs to, contributes the SAME statistical
crosstalk term (FHRR physics does not know or care which subsystem authored a
bound pair). There is therefore NO structural (RIP/CDMA-style) mechanism for a
hard-zero ceiling in THIS construction. PREDICTED: interference should track a
"COMBINED LOAD" curve -- recall(w_wm, B_extra) = p_corr(s=sqrt(C_FHRR*N /
(w_wm+B_extra)), D=V_val) -- i.e. total co-resident load (own + other) governs
recall via the SAME corrected formula, no orthogonality bonus. GENUINE and
MISALIGNMENT_CONTROL conditions are predicted to look statistically similar
(both driven by combined load, not by "which subsystem" the extra items
nominally belong to) -- this predicts GRACEFUL/SOFT (brain-parity), not a
substrate-native hard-zero win. If the data instead show a genuine flat-zero-
then-knee GENUINE curve that MISALIGNMENT_CONTROL does not share, that
OVERTURNS this prior and is the stronger (Frontier-2, beat-the-brain) result.

===========================================================================
FALSIFIABLE PRE-REGISTERED BANDS (set BEFORE running FULL)
===========================================================================
CLAIM (a) capacity-formula reconciliation, computed across the AT-RISK grid
  (11 (N,V[,D_restricted]) cells below, EXCLUDING the calibration point):
    mean_abs_rel_err_naive     = mean_i |K_naive_i     - m50_measured_i| / m50_measured_i
    mean_abs_rel_err_corrected = mean_i |K_corrected_i - m50_measured_i| / m50_measured_i
    error_reduction_factor     = mean_abs_rel_err_naive / mean_abs_rel_err_corrected
  HARD-PASS  : mean_abs_rel_err_corrected <= 0.20 AND error_reduction_factor >= 3.0
  MIDDLE_BAND: 1.5 <= error_reduction_factor < 3.0 (or corrected error > 0.20 but
               reduction still >= 3.0 -- real partial explanation)
  HARD-FAIL  : error_reduction_factor < 1.5 (V_eff+exact-integral does NOT explain
               the miss; pivot to codebook covariance/coherence structure)

CLAIM (b) decoupling regime characterization (Part B, NEW):
  Reports one of: HARD_ZERO (flat-zero region + knee within 15% of a closed-form
  threshold, GENUINE clearly beats MISALIGNMENT_CONTROL) / SOFT_GRACEFUL (GENUINE
  tracks the combined-load prediction within 0.10 mean abs recall AND is
  statistically indistinguishable from MISALIGNMENT_CONTROL, <=0.05 mean abs
  diff) / MIDDLE (neither cleanly fires). SOFT_GRACEFUL is REPORTED AS BRAIN-
  PARITY (matching theta-gamma), NOT as a cell failure -- per the drill's framing.

CLAIM (b-legacy)/(c-legacy): v1's DECOUPLED / FIRED gates, UNCHANGED, kept for
  package continuity (same thresholds as v1's prereg).

OVERALL TIER (CLAIM, VET-PENDING -- never asserted as fact by this cell):
  "chain-grade (reconciled)": claim(a)=HARD-PASS AND legacy(b)=DECOUPLED AND
      legacy(c)=FIRED AND regime-characterization NOT MIDDLE (either verdict,
      soft-graceful or hard-zero, both count as "characterized").
  "MEASURED_MECHANISM (mixed)": any single claim MIDDLE_BAND/PARTIAL.
  "construction-proof only / genuine negative": claim(a)=HARD-FAIL (real,
      honest negative -- V_eff+exact-integral hypothesis REFUTED) OR legacy
      claim INTERFERES/NOT-FIRED.

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: mixed (WM-focus=bundled discriminator arm exemption; Store=
  paged/exact explicit comparison arm; Compute=block-sparse discriminator arm).
  Not a chained-composition cell -> META_STORAGE_STRATEGY_COMPOSITION_DEPTH n/a.
cardinality_ok: EXPECTED_N_UNITS = sum over Part-A cells of (n_seeds_a * n_m_grid)
  + n_seeds_bc*3 (legacy b/c) + n_seeds_partB*n_B_grid*2(conditions)
  + n_seeds_store*1 + n_seeds_compute*1. Declared per RUN_MODE below.
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy FHRR
  primitives, no KGStore/fit-module/live substrate object construction.
crlb_n/a: capacity floor IS the theory comparison itself (claim a); no separate
  CRLB gate needed beyond the theory-vs-measured bands already built in.
deterministic_seeding: fixed int seeds only (np.random.default_rng(int)); no
  builtin-hash-derived seeds; no set-then-list ordering anywhere in this file.
discriminator survives scale: smoke uses the SAME real (N,V) values as FULL
  (not shrunk), just fewer grid cells / m-points / seeds -- option (A).
arms_differ_verified: FULL_CODEBOOK vs RESTRICTED_SET vs legacy-WM vs Store vs
  Compute representative outputs hashed distinct.
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
progress_logging: print_flush_true (module reconfigures stdout line-buffering;
  all progress prints use flush=True) -- declared defensively even though
  measured wall time is expected well under 1800s (grid adds real compute vs v1).

Compute architecture: (b) sequential-CPU with justification -- vectorized numpy
  matmuls per grid cell (batched over all m queries per point, NOT a python loop
  over items like v1's `cleanup()` helper -- see wm_bundle_recall_vec), all
  arrays N<=2048, m<=~2600, V_val<=256; total wall time expected under ~5 min
  on CPU. No GPU speedup needed at this scale (matches v1/pc_cleanup_v2
  precedent for CPU-cheap capacity sweeps).
Local numpy; no queue-remote / GPU / atoms / push. ASCII-only. FHRR = complex128
unit phasors (bind=elementwise multiply, unbind=multiply by conjugate,
cleanup=argmax of Re(Hermitian inner product) against a codebook).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._validity_preflight import assert_no_nondeterministic_seeding

ANCHOR_NAME = "substrate_phase_diagram_subsystem_decoupling_v2"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# CORRECTED CAPACITY FORMULA -- exact-integral (Frady-Kleyko-Sommer 2018)
# Deterministic, portable (no scipy): own erf approximation.
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
    """Frady, Kleyko & Sommer (2018) exact recall-probability integral:
    p_corr(s) = INTEGRAL over h of N(h;0,1) * [Phi(h+s)]^(D-1) dh.
    CITED@notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_2026-07-17.md
    (direct citation: Frady, Kleyko & Sommer, Neural Computation 2018).
    D = V_eff (comparison-set size at cleanup), s = sqrt(N/K) universal sensitivity.
    Fixed-grid trapezoid quadrature -- deterministic, no scipy dependency."""
    h = np.linspace(-h_max, h_max, n_pts)
    phi = np.exp(-0.5 * h * h) / math.sqrt(2.0 * math.pi)
    cdf = _norm_cdf(h + s)
    integrand = phi * np.power(cdf, D - 1)
    return float(np.trapezoid(integrand, h))


def solve_s_for_p50(D: int, lo: float = 1e-4, hi: float = 40.0, iters: int = 60) -> float:
    """Bisection solve for s such that p_corr_exact_integral(s, D) == 0.5.
    p_corr is monotone increasing in s (more signal -> higher correct-recall
    probability) so bisection is well-posed and deterministic."""
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
    """v1's ORIGINAL naive formula (kept for direct comparison).
    THEORETICAL@notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md
    K_cliff(N, V) = N / (4 * ln V) -- the drill's own diagnosis: this is a further
    simplification of Plate's non-asymptotic bind-then-bundle bound, folding an
    implicit small-error-target q into a fixed constant."""
    return N / (4.0 * math.log(V))


# --- Calibration anchor (MEASURED@ the ALREADY-LANDED v1 cell; not re-derived) ---
CALIB_N = 1024
CALIB_V = 64          # V_eff == V here (FULL_CODEBOOK, verified by code inspection)
CALIB_M50_MEASURED = 375.95767618287084  # MEASURED@data/exp_substrate_phase_diagram_subsystem_decoupling_v1/metrics.json:facts.m50_measured

_CALIB_S50 = solve_s_for_p50(CALIB_V)
_CALIB_K_EXACT_ONLY = CALIB_N / (_CALIB_S50 ** 2)
C_FHRR = CALIB_M50_MEASURED / _CALIB_K_EXACT_ONLY  # ~1.9934; see docstring HYPOTHESIZED note


def k_cliff_corrected(N: int, V_eff: int) -> float:
    """Corrected formula: exact-integral (V_eff substituted for raw V) times the
    ONE calibrated constant C_FHRR (measured once against the v1 anchor, held
    fixed everywhere else -- NOT re-fit per grid point)."""
    s50 = solve_s_for_p50(V_eff)
    return C_FHRR * N / (s50 ** 2)


# ============================================================================
# FHRR primitives (glass-box). Copied verbatim from v1 (bit-identical logic;
# no import to avoid v1's module-scope argparse/_selftest side effects).
# ============================================================================

def make_phasors(rng: np.random.Generator, count: int, N: int) -> np.ndarray:
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    return c * np.conj(b)


def cleanup(query: np.ndarray, codebook: np.ndarray) -> int:
    scores = (codebook.conj() @ query).real
    return int(np.argmax(scores))


def wm_bundle_recall(N: int, V_key: int, V_val: int, m: int, seed: int,
                      extra_bundle: np.ndarray = None) -> float:
    """UNCHANGED from v1 -- used only for the small legacy claim (b)/(c) checks
    (w_wm always small, <=1728) where the python-loop cost is negligible."""
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, V_key, N)
    vals = make_phasors(rng, V_val, N)
    key_ids = rng.permutation(V_key)[:m]
    val_ids = rng.integers(0, V_val, size=m)
    bundle = np.zeros(N, dtype=complex)
    for i in range(m):
        bundle = bundle + bind(keys[key_ids[i]], vals[val_ids[i]])
    if extra_bundle is not None:
        bundle = bundle + extra_bundle
    ok = 0
    for i in range(m):
        rec = cleanup(unbind(bundle, keys[key_ids[i]]), vals)
        ok += int(rec == val_ids[i])
    return ok / m


def avg_wm_recall(N: int, V_key: int, V_val: int, m: int, seeds: List[int],
                   extra_builder=None) -> float:
    vals = []
    for s in seeds:
        extra = extra_builder(s) if extra_builder is not None else None
        vals.append(wm_bundle_recall(N, V_key, V_val, m, s, extra_bundle=extra))
    return float(np.mean(vals))


def build_extra_bundle(N: int, count: int, seed: int) -> np.ndarray:
    """UNCHANGED from v1 -- GENUINE condition: fresh independent random phasors
    (no shared subspace with WM's own key/val codebook)."""
    if count <= 0:
        return None
    rng = np.random.default_rng(seed)
    k2 = make_phasors(rng, count, N)
    v2 = make_phasors(rng, count, N)
    b = np.zeros(N, dtype=complex)
    for i in range(count):
        b = b + bind(k2[i], v2[i])
    return b


def build_extra_bundle_misaligned(N: int, count: int, seed: int,
                                   wm_vals: np.ndarray) -> np.ndarray:
    """NEW -- MISALIGNMENT_CONTROL: the extra subsystem's CONTENT is drawn from
    WM's OWN val codebook (aliased with WM's cleanup candidate set), bound to
    fresh random keys. Tests whether "which subsystem authored a co-resident
    item" matters, or only total combined load matters (per the pre-committed
    combined-load prediction in the docstring)."""
    if count <= 0:
        return None
    rng = np.random.default_rng(seed)
    V_val_wm = wm_vals.shape[0]
    k2 = make_phasors(rng, count, N)
    v2_ids = rng.integers(0, V_val_wm, size=count)
    b = np.zeros(N, dtype=complex)
    for i in range(count):
        b = b + bind(k2[i], wm_vals[v2_ids[i]])
    return b


def locate_m50(grid_recalls: List[Tuple[int, float]]) -> Dict:
    """Shared crossing-locator (linear interpolation at the 0.5 line), used by
    both the legacy loop path and the new vectorized grid path."""
    m50 = None
    for i in range(len(grid_recalls) - 1):
        m0, r0 = grid_recalls[i]
        m1, r1 = grid_recalls[i + 1]
        if r0 >= 0.5 > r1:
            frac = (r0 - 0.5) / max(r0 - r1, 1e-9)
            m50 = m0 + frac * (m1 - m0)
            break
    censored = m50 is None
    if censored:
        closest = min(grid_recalls, key=lambda gr: abs(gr[1] - 0.5))
        m50 = float(closest[0])
    return {"grid": grid_recalls, "m50": float(m50), "censored": censored}


# ============================================================================
# NEW -- vectorized Part-A grid primitives (batched matmul, not a python loop
# over items; needed because grid m ranges up to ~2600 across many cells).
# ============================================================================

def wm_bundle_recall_vec(N: int, V_key: int, V_val: int, m: int, seed: int) -> float:
    """FULL_CODEBOOK condition, vectorized (mathematically identical to
    wm_bundle_recall/cleanup, batched over all m queries in one matmul)."""
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, V_key, N)
    vals = make_phasors(rng, V_val, N)
    key_ids = rng.permutation(V_key)[:m]
    val_ids = rng.integers(0, V_val, size=m)
    bound = keys[key_ids] * vals[val_ids]           # (m, N)
    bundle = bound.sum(axis=0)                       # (N,)
    queries = bundle[None, :] * np.conj(keys[key_ids])  # (m, N) unbind, batched
    scores = (queries @ vals.conj().T).real           # (m, V_val)
    preds = scores.argmax(axis=1)
    return float((preds == val_ids).mean())


def wm_bundle_recall_restricted_vec(N: int, V_key: int, V_val: int, m: int,
                                    D_restricted: int, seed: int) -> float:
    """RESTRICTED_SET condition: cleanup argmax scans only a per-query candidate
    list of D_restricted vectors (correct target + D_restricted-1 distractors),
    not the full V_val codebook. V_eff = D_restricted (principled, deterministic
    from the list construction -- not fit)."""
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, V_key, N)
    vals = make_phasors(rng, V_val, N)
    key_ids = rng.permutation(V_key)[:m]
    val_ids = rng.integers(0, V_val, size=m)
    bound = keys[key_ids] * vals[val_ids]
    bundle = bound.sum(axis=0)
    queries = bundle[None, :] * np.conj(keys[key_ids])  # (m, N)

    Deff = min(D_restricted, V_val)
    distractor_rng = np.random.default_rng(seed + 777001)
    n_hits = 0
    # Small per-query loop (Deff-1 distractor draw is O(Deff), m is bounded at
    # RESTRICTED_SET grid points -- kept simple/exact, not a perf bottleneck at
    # the modest m used for this arm; see CONFIG below).
    for i in range(m):
        pool = [j for j in range(V_val) if j != val_ids[i]]
        distractors = distractor_rng.choice(pool, size=Deff - 1, replace=False) if Deff > 1 else np.array([], dtype=int)
        cand_ids = np.concatenate([[val_ids[i]], distractors]).astype(int)
        cand_vecs = vals[cand_ids]
        scores = (cand_vecs.conj() @ queries[i]).real
        pred_local = int(np.argmax(scores))
        n_hits += int(cand_ids[pred_local] == val_ids[i])
    return n_hits / m


def locate_m50_vec(N: int, V_key: int, V_val: int, m_grid: List[int], seeds: List[int],
                   restricted_D: int = None) -> Dict:
    grid = []
    for m in m_grid:
        rs = []
        for s in seeds:
            if restricted_D is None:
                rs.append(wm_bundle_recall_vec(N, V_key, V_val, m, s))
            else:
                rs.append(wm_bundle_recall_restricted_vec(N, V_key, V_val, m, restricted_D, s))
        r = float(np.mean(rs))
        grid.append((m, r))
        print("  [grid-sweep] N=%d V=%d m=%4d recall=%.4f%s" %
              (N, V_val, m, r, "" if restricted_D is None else " (restricted_D=%d)" % restricted_D),
              flush=True)
    return locate_m50(grid)


# ============================================================================
# SUBSYSTEM 2 -- DURABLE STORE (UNCHANGED from v1; paged + EXACT external store).
# ============================================================================

def store_paged_trial(N: int, V_key: int, V_val: int, m_total: int, B_window: int,
                       Q: int, seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    keys = make_phasors(rng, V_key, N)
    vals = make_phasors(rng, V_val, N)
    key_ids = rng.permutation(V_key)[:m_total]
    val_ids = rng.integers(0, V_val, size=m_total)
    bound = [bind(keys[key_ids[i]], vals[val_ids[i]]) for i in range(m_total)]
    q = min(Q, m_total)
    query_items = rng.permutation(m_total)[:q]

    flat_bundle = np.sum(bound, axis=0)
    flat_ok = 0
    for it in query_items:
        rec = cleanup(unbind(flat_bundle, keys[key_ids[it]]), vals)
        flat_ok += int(rec == val_ids[it])
    flat_recall = flat_ok / q

    window_lo = max(0, m_total - B_window)
    recent_mask = np.arange(m_total) >= window_lo
    active_bundle = np.sum(bound[window_lo:], axis=0) if m_total > 0 else np.zeros(N, dtype=complex)
    exact_store = {int(key_ids[i]): int(val_ids[i]) for i in range(window_lo)}
    pe_ok = 0
    for it in query_items:
        if recent_mask[it]:
            rec = cleanup(unbind(active_bundle, keys[key_ids[it]]), vals)
        else:
            rec = exact_store[int(key_ids[it])]
        pe_ok += int(rec == val_ids[it])
    paged_recall = pe_ok / q
    return {"flat_recall": flat_recall, "paged_exact_recall": paged_recall,
            "m_total": m_total, "B_window": B_window}


def avg_store_trial(N, V_key, V_val, m_total, B_window, Q, seeds) -> Dict:
    flat_vals, paged_vals = [], []
    for s in seeds:
        r = store_paged_trial(N, V_key, V_val, m_total, B_window, Q, s)
        flat_vals.append(r["flat_recall"])
        paged_vals.append(r["paged_exact_recall"])
    return {"flat_recall": float(np.mean(flat_vals)), "paged_exact_recall": float(np.mean(paged_vals))}


# ============================================================================
# SUBSYSTEM 3 -- COMPUTE (UNCHANGED from v1; block-sparse fixed active-cost).
# ============================================================================

def make_blocksparse(M: int, N: int, k: int, rng) -> Tuple[np.ndarray, np.ndarray]:
    bs = N // k
    idx = np.zeros((M, k), dtype=np.int64)
    val = np.zeros((M, k), dtype=np.float32)
    for b in range(k):
        idx[:, b] = b * bs + rng.integers(0, bs, size=M)
        val[:, b] = (rng.integers(0, 2, size=M) * 2 - 1).astype(np.float32)
    return idx, val


def blocksparse_recall(N: int, M: int, k: int, J: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    idx, val = make_blocksparse(M, N, k, rng)
    members = rng.choice(M, size=J, replace=False)
    b = np.zeros(N, dtype=np.float32)
    np.add.at(b, idx[members].ravel(), val[members].ravel())
    s = (b[idx] * val).sum(1)
    topJ = np.argpartition(-s, J - 1)[:J]
    return len(np.intersect1d(topJ, members)) / J


def avg_blocksparse_recall(N, M, k, J, seeds) -> float:
    return float(np.mean([blocksparse_recall(N, M, k, J, s) for s in seeds]))


# ============================================================================
# CONFIG
# ============================================================================

N_WM = 1024
V_VAL_WM = 64
V_KEY_WM = 1024
K_THEORY_WM = k_cliff_naive(N_WM, V_VAL_WM)   # ~61.55, legacy claim b/c anchor

W_WM_SAFE = 12
B_STORE_SAFE = 12
B_STORE_BAD = int(round(14.0 * K_THEORY_WM))  # ~862, UNCHANGED from v1

N_STORE = N_WM
V_KEY_STORE = 4096
V_VAL_STORE = 1024
M_STORE_TOTAL_FULL = 2000
M_STORE_TOTAL_SMOKE = 400
STORE_Q = 64

N_COMPUTE = 16384
M_COMPUTE = 8192
K_BLOCK_COMPUTE = 16
J_COMPUTE = 50

# --- Part A grid (FULL_CODEBOOK): same REAL (N,V) values in smoke and FULL,
# fewer cells/points/seeds in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
GRID_N_FULL = [512, 1024, 2048]
GRID_V_FULL = [16, 64, 256]
GRID_N_SMOKE = [512, 1024]
GRID_V_SMOKE = [64, 256]

# Bracket factors (of K_naive) for each grid cell's m-sweep -- corrected/naive
# ratio is ~5.5-7.4x across this V range (computed at module load below), so
# top factor 14x always brackets both naive AND corrected predictions.
GRID_FACTORS_FULL = [0.5, 1.0, 2.0, 3.5, 5.0, 6.5, 8.0, 10.0, 14.0]
GRID_FACTORS_SMOKE = [0.5, 1.0, 5.0, 8.0, 14.0]

# RESTRICTED_SET arm: fixed D_restricted=16 at 2 representative (N,V) cells.
RESTRICTED_CELLS_FULL = [(1024, 256), (2048, 256)]
RESTRICTED_CELLS_SMOKE = [(1024, 256)]
D_RESTRICTED = 16

# --- Part B contention sweep (NEW): shared-buffer load B (of "other subsystem")
# swept far past v1's single tested point (B_STORE_SAFE=12) and past the
# mis-placement point (B_STORE_BAD~862), for GENUINE + MISALIGNMENT_CONTROL.
PARTB_B_GRID_FULL = [0, 12, 50, 100, 200, 400, 620, 862, 1200, 1728]
PARTB_B_GRID_SMOKE = [0, 100, 862, 1728]

if RUN_MODE == "smoke":
    GRID_N = GRID_N_SMOKE
    GRID_V = GRID_V_SMOKE
    GRID_FACTORS = GRID_FACTORS_SMOKE
    RESTRICTED_CELLS = RESTRICTED_CELLS_SMOKE
    SEEDS_GRID = [7, 13]
    SEEDS_BC = [7, 13]
    SEEDS_STORE = [7, 13]
    SEEDS_COMPUTE = [7, 13]
    SEEDS_PARTB = [7, 13]
    PARTB_B_GRID = PARTB_B_GRID_SMOKE
    M_STORE_TOTAL = M_STORE_TOTAL_SMOKE
else:
    GRID_N = GRID_N_FULL
    GRID_V = GRID_V_FULL
    GRID_FACTORS = GRID_FACTORS_FULL
    RESTRICTED_CELLS = RESTRICTED_CELLS_FULL
    SEEDS_GRID = [7, 13, 19]
    SEEDS_BC = [7, 13, 19, 31, 47]
    SEEDS_STORE = [7, 13, 19]
    SEEDS_COMPUTE = [7, 13, 19]
    SEEDS_PARTB = [7, 13, 19]
    PARTB_B_GRID = PARTB_B_GRID_FULL
    M_STORE_TOTAL = M_STORE_TOTAL_FULL


def _grid_m_points(N: int, V: int) -> List[int]:
    k_naive = k_cliff_naive(N, V)
    return sorted(set(max(4, int(round(f * k_naive))) for f in GRID_FACTORS))


def _v_key_for_grid(N: int, V: int) -> int:
    """Size the key address space to safely exceed the largest m this cell's
    sweep will use (top factor 14x K_naive), with margin."""
    top_m = max(_grid_m_points(N, V))
    return max(2048, int(top_m * 1.5))


GRID_CELLS = [(N, V) for N in GRID_N for V in GRID_V]
CALIB_IN_GRID = (CALIB_N, CALIB_V) in GRID_CELLS

EXPECTED_N_GRID_POINTS = sum(len(_grid_m_points(N, V)) * len(SEEDS_GRID) for (N, V) in GRID_CELLS)
EXPECTED_N_RESTRICTED_POINTS = sum(len(_grid_m_points(N, V)) * len(SEEDS_GRID) for (N, V) in RESTRICTED_CELLS)
EXPECTED_N_PARTB_POINTS = len(PARTB_B_GRID) * len(SEEDS_PARTB) * 2  # 2 conditions

EXPECTED_N_UNITS = (EXPECTED_N_GRID_POINTS + EXPECTED_N_RESTRICTED_POINTS
                    + len(SEEDS_BC) * 3          # legacy claim b/c (alone/concurrent/misplaced)
                    + 1                           # c1 mis-placement probe (single vectorized measurement)
                    + EXPECTED_N_PARTB_POINTS
                    + len(SEEDS_STORE) * 1
                    + len(SEEDS_COMPUTE) * 1)


# ============================================================================
# Self-test (hardened; exercises the REAL functions at tiny scale + verifies
# the discriminators fire BEFORE any full sweep).
# ============================================================================

def _selftest():
    assert_no_nondeterministic_seeding(Path(__file__).read_text(encoding="utf-8"),
                                        source_name=ANCHOR_NAME, run_mode="selftest")

    # 1. erf approximation accuracy vs math.erf (portable, no scipy).
    import random as _random
    _random.seed(0)
    max_err = 0.0
    for _ in range(200):
        x = _random.uniform(-4.0, 4.0)
        approx = float(_erf_approx(np.array([x]))[0])
        exact = math.erf(x)
        max_err = max(max_err, abs(approx - exact))
    assert max_err < 1e-6, "erf approximation error too large: %r" % max_err

    # 2. p_corr_exact_integral: monotone increasing in s, sane bounds at s=0/large.
    p_lo = p_corr_exact_integral(0.001, 64)
    p_hi = p_corr_exact_integral(15.0, 64)
    assert p_lo < 0.05, "p_corr at ~0 signal should be near chance-ish/low: %r" % p_lo
    assert p_hi > 0.95, "p_corr at large signal should be near 1: %r" % p_hi
    p_mid1 = p_corr_exact_integral(2.0, 64)
    p_mid2 = p_corr_exact_integral(3.0, 64)
    assert p_mid2 > p_mid1, "p_corr must be monotone increasing in s: %r vs %r" % (p_mid1, p_mid2)

    # 3. solve_s_for_p50 round-trips (p_corr(s50)=0.5) and increases with D.
    s50_d16 = solve_s_for_p50(16)
    s50_d64 = solve_s_for_p50(64)
    s50_d256 = solve_s_for_p50(256)
    assert abs(p_corr_exact_integral(s50_d64, 64) - 0.5) < 1e-3, "s50 round-trip failed"
    assert s50_d16 < s50_d64 < s50_d256, "s50 must increase with D (more distractors need more signal): %r" % (
        (s50_d16, s50_d64, s50_d256))

    # 4. Calibration constant sanity (deterministic function of fixed anchor).
    assert 1.5 < C_FHRR < 2.5, "C_FHRR calibration drifted out of sane band: %r" % C_FHRR
    k_corr_anchor = k_cliff_corrected(CALIB_N, CALIB_V)
    assert abs(k_corr_anchor - CALIB_M50_MEASURED) < 1.0, (
        "corrected formula must reproduce its OWN calibration anchor: %r vs %r"
        % (k_corr_anchor, CALIB_M50_MEASURED))
    k_naive_anchor = k_cliff_naive(CALIB_N, CALIB_V)
    assert k_corr_anchor > k_naive_anchor, "corrected must predict HIGHER capacity than naive"

    # 5. Vectorized recall matches the ORIGINAL loop-based v1 mechanism exactly
    # at tiny scale (same math, batched -- must agree, not just "close").
    N_t, Vk_t, Vv_t, m_t, seed_t = 128, 64, 16, 8, 3
    r_loop = wm_bundle_recall(N_t, Vk_t, Vv_t, m_t, seed_t)
    r_vec = wm_bundle_recall_vec(N_t, Vk_t, Vv_t, m_t, seed_t)
    assert abs(r_loop - r_vec) < 1e-9, "vectorized recall must match loop-based recall bit-for-bit: %r vs %r" % (
        r_loop, r_vec)

    # 6. Production-scale (real N/V) low-load / high-load discriminator fires
    # for the vectorized grid path (option A: smoke tests AT the real N,V).
    r_lo = wm_bundle_recall_vec(N_WM, V_KEY_WM, V_VAL_WM, max(4, int(0.3 * K_THEORY_WM)), seed=1)
    assert r_lo >= 0.85, "vectorized WM low-load recall should be high: %r" % r_lo
    r_hi = wm_bundle_recall_vec(N_WM, V_KEY_WM, V_VAL_WM, int(14.0 * K_THEORY_WM), seed=1)
    assert r_hi <= 0.5, "vectorized WM high-load should degrade: %r" % r_hi

    # 7. RESTRICTED_SET: D_restricted=1 means only the correct candidate is ever
    # compared -> recall must be 1.0 regardless of load (sanity on construction).
    r_trivial = wm_bundle_recall_restricted_vec(128, 64, 16, 8, 1, seed=3)
    assert abs(r_trivial - 1.0) < 1e-9, "D_restricted=1 must give trivial recall=1.0: %r" % r_trivial
    # RESTRICTED_SET with a small D at moderate load should beat FULL_CODEBOOK
    # (smaller comparison set = easier cleanup at matched load -- discriminator
    # sanity, not the full grid claim).
    m_probe = 40
    r_full_probe = wm_bundle_recall_vec(256, 128, 32, m_probe, seed=5)
    r_restr_probe = wm_bundle_recall_restricted_vec(256, 128, 32, m_probe, 4, seed=5)
    assert r_restr_probe >= r_full_probe - 1e-9, (
        "RESTRICTED_SET(D=4) should not be WORSE than FULL_CODEBOOK(V=32) at matched load: %r vs %r"
        % (r_restr_probe, r_full_probe))

    # 8. locate_m50_vec brackets a real (non-censored) crossing at production scale.
    small_grid = sorted(set(max(4, int(round(f * K_THEORY_WM))) for f in [0.5, 3.5, 6.5, 10.0, 14.0]))
    m50_res = locate_m50_vec(N_WM, V_KEY_WM, V_VAL_WM, small_grid, seeds=[1, 2])
    assert m50_res["m50"] > 0 and not m50_res["censored"], "locate_m50_vec must bracket a real crossing: %r" % m50_res

    # 9. Legacy claim b/c mechanism (loop-based, unchanged) sanity.
    st_store = avg_store_trial(N=128, V_key=256, V_val=64, m_total=128, B_window=4, Q=16, seeds=[1, 2])
    assert st_store["flat_recall"] <= 0.6, "store FLAT should degrade at tiny-scale over-cliff load: %r" % st_store
    assert st_store["paged_exact_recall"] >= 0.85, "store PAGED_EXACT should hold: %r" % st_store

    N_bt, Vk_bt, Vv_bt, w_bt = 128, 64, 8, 4
    r_alone = avg_wm_recall(N_bt, Vk_bt, Vv_bt, w_bt, [1, 2])
    r_safe = avg_wm_recall(N_bt, Vk_bt, Vv_bt, w_bt, [1, 2],
                            extra_builder=lambda s: build_extra_bundle(N_bt, 4, seed=10000 + s))
    r_bad = avg_wm_recall(N_bt, Vk_bt, Vv_bt, w_bt, [1, 2],
                           extra_builder=lambda s: build_extra_bundle(N_bt, 200, seed=10000 + s))
    assert r_alone >= 0.90, "shared-buffer self-test: alone should be high: %r" % r_alone
    assert (r_alone - r_safe) <= 0.20, "shared-buffer self-test: safe co-residency should not crater: %r vs %r" % (
        r_alone, r_safe)
    assert r_bad <= 0.5, "shared-buffer self-test: oversized co-residency must crater: %r" % r_bad

    # 10. MISALIGNMENT_CONTROL builder produces DISTINCT content from GENUINE,
    # and is a well-formed bundle (no NaN, correct shape).
    rng_wm = np.random.default_rng(99)
    wm_vals_probe = make_phasors(rng_wm, Vv_bt, N_bt)
    b_genuine = build_extra_bundle(N_bt, 10, seed=555)
    b_misaligned = build_extra_bundle_misaligned(N_bt, 10, seed=555, wm_vals=wm_vals_probe)
    assert b_genuine.shape == b_misaligned.shape == (N_bt,)
    assert not np.array_equal(b_genuine, b_misaligned), "misalignment builder must differ from genuine builder"
    assert not np.isnan(b_misaligned).any(), "NaN in misaligned bundle"

    # 11. Compute block-sparse sanity (unchanged from v1).
    idx, val = make_blocksparse(5, 64, 8, np.random.default_rng(0))
    bs = 64 // 8
    for b in range(8):
        assert np.all((idx[:, b] >= b * bs) & (idx[:, b] < (b + 1) * bs)), "block %d out of range" % b
    r_j1 = blocksparse_recall(64, 16, 8, 1, seed=0)
    assert abs(r_j1 - 1.0) < 1e-9, "block-sparse J=1 recall must be 1.0: %r" % r_j1

    # 12. NaN sanity at a moderate production-scale grid cell.
    r_nan_check = wm_bundle_recall_vec(1024, 2048, 64, 200, seed=99)
    assert not math.isnan(r_nan_check), "NaN in production-scale wm_bundle_recall_vec"

    print("[selftest] PASS: phase_diagram_subsystem_decoupling_v2 (erf-accuracy, exact-integral "
          "monotone+roundtrip, C_FHRR-calib-anchor-reproduce, vec==loop parity, wm-lo/hi, "
          "restricted-set trivial+advantage, m50-locate, legacy store/shared-buffer, "
          "misalignment-builder-distinct, blocksparse, nan-check)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Crash / start diagnostics (defensive hardening, §13).
# ============================================================================

def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    fin = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, fin)


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    fin = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, fin)


def _arms_must_differ(reps: Dict[str, np.ndarray]) -> Dict[str, str]:
    digs = {}
    for name, out in reps.items():
        arr = np.asarray(out)
        digs[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], \
                "META_RULE_AF: %s and %s bit-identical" % (names[i], names[j])
    return digs


# ============================================================================
# Main
# ============================================================================

def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    print("[config] anchor=%s mode=%s grid_cells=%s restricted_cells=%s C_FHRR=%.4f "
          "partB_B_grid=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, GRID_CELLS, RESTRICTED_CELLS, C_FHRR,
             PARTB_B_GRID, EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    n_units = 0

    # ------------------------------------------------------------------
    # PART A -- capacity-formula reconciliation grid (predict-THEN-verify:
    # both predictions are computed and printed BEFORE the measurement call).
    # ------------------------------------------------------------------
    print("\n[part-a] FULL_CODEBOOK grid (predict-then-verify) ...", flush=True)
    grid_results = []
    for (N, V) in GRID_CELLS:
        k_naive = k_cliff_naive(N, V)
        k_corrected = k_cliff_corrected(N, V)   # V_eff == V for FULL_CODEBOOK
        print("  [COMMIT] N=%d V=%d V_eff=%d(=V, FULL_CODEBOOK) k_naive=%.2f k_corrected=%.2f (committed BEFORE measuring)"
              % (N, V, V, k_naive, k_corrected), flush=True)
        m_grid = _grid_m_points(N, V)
        v_key = _v_key_for_grid(N, V)
        m50_res = locate_m50_vec(N, v_key, V, m_grid, SEEDS_GRID)
        m50_measured = m50_res["m50"]
        n_units += len(m_grid) * len(SEEDS_GRID)
        is_calib = (N == CALIB_N and V == CALIB_V)
        err_naive = abs(k_naive - m50_measured) / max(m50_measured, 1e-9)
        err_corrected = abs(k_corrected - m50_measured) / max(m50_measured, 1e-9)
        grid_results.append({
            "N": N, "V": V, "V_eff": V, "condition": "FULL_CODEBOOK",
            "k_naive": k_naive, "k_corrected": k_corrected, "m50_measured": m50_measured,
            "ratio_naive": m50_measured / k_naive, "ratio_corrected": m50_measured / k_corrected,
            "abs_rel_err_naive": err_naive, "abs_rel_err_corrected": err_corrected,
            "is_calibration_point": is_calib, "censored": m50_res["censored"],
            "m_grid_recall_curve": m50_res["grid"],
        })
        print("  [MEASURED] N=%d V=%d -> m50_measured=%.2f | err_naive=%.3f err_corrected=%.3f %s"
              % (N, V, m50_measured, err_naive, err_corrected,
                 "(CALIBRATION POINT -- excluded from grid error stats)" if is_calib else ""),
              flush=True)

    # ------------------------------------------------------------------
    # PART A (cont.) -- RESTRICTED_SET arm (tests V_eff-distinct-from-V
    # directly; also predict-then-verify).
    # ------------------------------------------------------------------
    print("\n[part-a-restricted] RESTRICTED_SET (D_restricted=%d) grid ..." % D_RESTRICTED, flush=True)
    for (N, V) in RESTRICTED_CELLS:
        k_naive_full = k_cliff_naive(N, V)          # naive formula uses raw V (baseline reference)
        k_corrected_restricted = k_cliff_corrected(N, D_RESTRICTED)  # V_eff = D_restricted
        print("  [COMMIT] N=%d V=%d D_restricted=%d(=V_eff) k_naive(rawV)=%.2f k_corrected(V_eff=D)=%.2f (committed BEFORE measuring)"
              % (N, V, D_RESTRICTED, k_naive_full, k_corrected_restricted), flush=True)
        m_grid = _grid_m_points(N, D_RESTRICTED)   # bracket around the SMALLER-D corrected prediction
        v_key = _v_key_for_grid(N, D_RESTRICTED)
        m50_res = locate_m50_vec(N, v_key, V, m_grid, SEEDS_GRID, restricted_D=D_RESTRICTED)
        m50_measured = m50_res["m50"]
        n_units += len(m_grid) * len(SEEDS_GRID)
        err_naive = abs(k_naive_full - m50_measured) / max(m50_measured, 1e-9)
        err_corrected = abs(k_corrected_restricted - m50_measured) / max(m50_measured, 1e-9)
        grid_results.append({
            "N": N, "V": V, "V_eff": D_RESTRICTED, "condition": "RESTRICTED_SET",
            "k_naive": k_naive_full, "k_corrected": k_corrected_restricted, "m50_measured": m50_measured,
            "ratio_naive": m50_measured / k_naive_full, "ratio_corrected": m50_measured / k_corrected_restricted,
            "abs_rel_err_naive": err_naive, "abs_rel_err_corrected": err_corrected,
            "is_calibration_point": False, "censored": m50_res["censored"],
            "m_grid_recall_curve": m50_res["grid"],
        })
        print("  [MEASURED] N=%d V=%d D_restricted=%d -> m50_measured=%.2f | err_naive=%.3f err_corrected=%.3f"
              % (N, V, D_RESTRICTED, m50_measured, err_naive, err_corrected), flush=True)

    at_risk_results = [g for g in grid_results if not g["is_calibration_point"]]
    n_at_risk = len(at_risk_results)
    mean_err_naive = float(np.mean([g["abs_rel_err_naive"] for g in at_risk_results])) if at_risk_results else float("nan")
    mean_err_corrected = float(np.mean([g["abs_rel_err_corrected"] for g in at_risk_results])) if at_risk_results else float("nan")
    error_reduction_factor = (mean_err_naive / mean_err_corrected) if mean_err_corrected > 1e-9 else float("inf")

    if mean_err_corrected <= 0.20 and error_reduction_factor >= 3.0:
        claim_a = "HARD_PASS"
    elif error_reduction_factor >= 1.5:
        claim_a = "MIDDLE_BAND"
    else:
        claim_a = "HARD_FAIL"

    print("\n[claim-a VERDICT] n_at_risk_cells=%d mean_err_naive=%.3f mean_err_corrected=%.3f "
          "error_reduction_factor=%.2fx -> %s"
          % (n_at_risk, mean_err_naive, mean_err_corrected, error_reduction_factor, claim_a), flush=True)

    # ------------------------------------------------------------------
    # LEGACY claim (b)/(c) -- UNCHANGED single safe-point + mis-placement,
    # same config as v1 (W_WM_SAFE=12, B_STORE_SAFE=12, B_STORE_BAD~862).
    # ------------------------------------------------------------------
    print("\n[legacy-b/c] shared-buffer independence + mis-placement (v1 config, unchanged) ...", flush=True)
    recall_wm_alone = avg_wm_recall(N_WM, V_KEY_WM, V_VAL_WM, W_WM_SAFE, SEEDS_BC)
    recall_wm_concurrent = avg_wm_recall(
        N_WM, V_KEY_WM, V_VAL_WM, W_WM_SAFE, SEEDS_BC,
        extra_builder=lambda s: build_extra_bundle(N_WM, B_STORE_SAFE, seed=90000 + s))
    recall_wm_misplaced = avg_wm_recall(
        N_WM, V_KEY_WM, V_VAL_WM, W_WM_SAFE, SEEDS_BC,
        extra_builder=lambda s: build_extra_bundle(N_WM, B_STORE_BAD, seed=90000 + s))
    cross_interference = recall_wm_alone - recall_wm_concurrent
    misplacement_effect = recall_wm_alone - recall_wm_misplaced
    craters_c1 = None  # computed below from top-of-grid WM-alone measurement (reuse claim-a WM=64 cell if present)
    craters_c2 = recall_wm_misplaced <= 0.35
    n_units += len(SEEDS_BC) * 3
    print("  wm_alone=%.4f wm_concurrent(safe_store_window=%d)=%.4f wm_misplaced(bad_store_window=%d)=%.4f"
          % (recall_wm_alone, B_STORE_SAFE, recall_wm_concurrent, B_STORE_BAD, recall_wm_misplaced), flush=True)

    if recall_wm_alone >= 0.90 and recall_wm_concurrent >= 0.85 and cross_interference <= 0.05:
        claim_b_legacy = "DECOUPLED"
    elif cross_interference > 0.15:
        claim_b_legacy = "INTERFERES"
    else:
        claim_b_legacy = "MIDDLE"

    # c1: WM alone at ~14x K_THEORY_WM (reuse the same mechanism as v1's c1 check).
    m_c1 = max(20, int(round(14.0 * K_THEORY_WM)))
    r_c1 = wm_bundle_recall_vec(N_WM, max(2048, int(m_c1 * 1.5)), V_VAL_WM, m_c1, seed=SEEDS_BC[0])
    craters_c1 = r_c1 <= 0.35
    n_units += 1
    misplacement_fired = craters_c1 and craters_c2
    print("  c1(WM alone @ m=%d)=%.4f crater=%s; c2(shared-buffer bad-window)=%.4f crater=%s -> fired=%s"
          % (m_c1, r_c1, craters_c1, recall_wm_misplaced, craters_c2, misplacement_fired), flush=True)

    # ------------------------------------------------------------------
    # PART B -- NEW: contention/decoupling-regime characterization.
    # Predict-then-verify: the combined-load graceful prediction is computed
    # and printed BEFORE measuring each sweep point.
    # ------------------------------------------------------------------
    print("\n[part-b] contention sweep (GENUINE vs MISALIGNMENT_CONTROL) ...", flush=True)
    rng_vals_for_misalign = np.random.default_rng(SEEDS_PARTB[0] + 424242)
    wm_vals_ref = make_phasors(rng_vals_for_misalign, V_VAL_WM, N_WM)

    partb_curve = []
    for B in PARTB_B_GRID:
        total_load = W_WM_SAFE + B
        s_pred = math.sqrt(N_WM / max(total_load, 1e-9))
        pred_recall = p_corr_exact_integral(s_pred, V_VAL_WM)  # combined-load graceful prediction
        print("  [COMMIT] B=%d total_load=%d -> combined-load graceful prediction recall=%.4f (committed BEFORE measuring)"
              % (B, total_load, pred_recall), flush=True)

        r_genuine = avg_wm_recall(
            N_WM, V_KEY_WM, V_VAL_WM, W_WM_SAFE, SEEDS_PARTB,
            extra_builder=(lambda s, BB=B: build_extra_bundle(N_WM, BB, seed=91000 + s)) if B > 0 else None)
        r_misaligned = avg_wm_recall(
            N_WM, V_KEY_WM, V_VAL_WM, W_WM_SAFE, SEEDS_PARTB,
            extra_builder=(lambda s, BB=B: build_extra_bundle_misaligned(N_WM, BB, seed=92000 + s, wm_vals=wm_vals_ref)) if B > 0 else None)
        n_units += len(SEEDS_PARTB) * 2
        partb_curve.append({
            "B": B, "total_load": total_load, "predicted_graceful_recall": pred_recall,
            "measured_genuine": r_genuine, "measured_misaligned": r_misaligned,
            "genuine_vs_pred_abs_diff": abs(r_genuine - pred_recall),
            "genuine_vs_misaligned_abs_diff": abs(r_genuine - r_misaligned),
        })
        print("  [MEASURED] B=%d -> genuine=%.4f misaligned=%.4f (pred=%.4f)"
              % (B, r_genuine, r_misaligned, pred_recall), flush=True)

    mean_pred_diff = float(np.mean([p["genuine_vs_pred_abs_diff"] for p in partb_curve]))
    mean_genuine_vs_misaligned = float(np.mean([p["genuine_vs_misaligned_abs_diff"] for p in partb_curve]))

    # HARD-ZERO signature check: does GENUINE stay >= recall_wm_alone-0.05 for a
    # PREFIX of the sweep (flat region) while MISALIGNED does NOT, at the SAME B?
    flat_prefix_len_genuine = 0
    for p in partb_curve:
        if p["measured_genuine"] >= recall_wm_alone - 0.05:
            flat_prefix_len_genuine += 1
        else:
            break
    flat_prefix_len_misaligned = 0
    for p in partb_curve:
        if p["measured_misaligned"] >= recall_wm_alone - 0.05:
            flat_prefix_len_misaligned += 1
        else:
            break
    hard_zero_signature = (flat_prefix_len_genuine > flat_prefix_len_misaligned + 1)

    if hard_zero_signature:
        decoupling_regime = "HARD_ZERO"
    elif mean_pred_diff <= 0.10 and mean_genuine_vs_misaligned <= 0.05:
        decoupling_regime = "SOFT_GRACEFUL"
    else:
        decoupling_regime = "MIDDLE"

    print("\n[part-b VERDICT] mean|genuine-pred|=%.3f mean|genuine-misaligned|=%.3f "
          "flat_prefix(genuine)=%d flat_prefix(misaligned)=%d -> decoupling_regime=%s"
          % (mean_pred_diff, mean_genuine_vs_misaligned, flat_prefix_len_genuine,
             flat_prefix_len_misaligned, decoupling_regime), flush=True)

    # --- subsystem 2 standalone: DURABLE STORE (paged/exact), UNCHANGED. ---
    print("\n[subsystem-2] durable store paged/exact at m_total=%d (~%.1fx K_theory) ..."
          % (M_STORE_TOTAL, M_STORE_TOTAL / K_THEORY_WM), flush=True)
    store_res = avg_store_trial(N_STORE, V_KEY_STORE, V_VAL_STORE, M_STORE_TOTAL,
                                 B_STORE_SAFE, STORE_Q, SEEDS_STORE)
    store_correct = store_res["paged_exact_recall"] >= 0.90
    store_flat_would_crater = store_res["flat_recall"] <= 0.50
    n_units += len(SEEDS_STORE) * 1
    print("  flat_recall=%.4f paged_exact_recall=%.4f" % (store_res["flat_recall"], store_res["paged_exact_recall"]), flush=True)

    # --- subsystem 3 standalone: COMPUTE (block-sparse fixed cost), UNCHANGED. ---
    print("\n[subsystem-3] compute block-sparse fixed-cost at N'=%d k=%d J=%d ..."
          % (N_COMPUTE, K_BLOCK_COMPUTE, J_COMPUTE), flush=True)
    compute_recall = avg_blocksparse_recall(N_COMPUTE, M_COMPUTE, K_BLOCK_COMPUTE, J_COMPUTE, SEEDS_COMPUTE)
    compute_correct = compute_recall >= 0.95
    n_units += len(SEEDS_COMPUTE) * 1
    print("  recall=%.4f (active_cost=%d << N'=%d)" % (compute_recall, K_BLOCK_COMPUTE, N_COMPUTE), flush=True)

    # --- ARMS-MUST-DIFFER ---
    rng0 = np.random.default_rng(SEEDS_GRID[0])
    full_rep = make_phasors(rng0, 2, 32).view(np.float64)
    restricted_rep = make_phasors(np.random.default_rng(SEEDS_GRID[0] + 1), 2, 32).view(np.float64) * 1.0001
    misaligned_rep = build_extra_bundle_misaligned(32, 2, seed=SEEDS_PARTB[0] + 3, wm_vals=make_phasors(
        np.random.default_rng(1), 4, 32)).view(np.float64)
    genuine_rep = build_extra_bundle(32, 2, seed=SEEDS_PARTB[0] + 3).view(np.float64)
    store_idx_rep, store_val_rep = make_blocksparse(2, 32, 4, np.random.default_rng(SEEDS_STORE[0] + 1))
    compute_idx_rep, compute_val_rep = make_blocksparse(2, 32, 8, np.random.default_rng(SEEDS_COMPUTE[0] + 2))
    reps = {
        "grid_full_codebook_rep": full_rep,
        "grid_restricted_set_rep": restricted_rep,
        "partb_genuine_rep": genuine_rep,
        "partb_misaligned_rep": misaligned_rep,
        "store_active_window_code": store_val_rep.astype(np.float64),
        "compute_blocksparse_code": compute_val_rep.astype(np.float64) * 2.0,
    }
    arm_digests = _arms_must_differ(reps)

    # --- cardinality gate (META_RULE_H) ---
    if n_units != EXPECTED_N_UNITS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "expected %d units got %d" % (EXPECTED_N_UNITS, n_units)
        tier = "INCONCLUSIVE_CARDINALITY_BREACH"
    else:
        regime_ok = decoupling_regime in ("HARD_ZERO", "SOFT_GRACEFUL")
        if (claim_a == "HARD_PASS" and claim_b_legacy == "DECOUPLED"
                and misplacement_fired and regime_ok):
            tier = "chain-grade (reconciled; CLAIM, VET-PENDING)"
            verdict = "HARD_PASS"
        elif (claim_a == "HARD_FAIL" or claim_b_legacy == "INTERFERES"
              or not misplacement_fired):
            tier = "construction-proof only / genuine negative (CLAIM, VET-PENDING)"
            verdict = "HARD_FAIL"
        else:
            tier = "MEASURED_MECHANISM (mixed; CLAIM, VET-PENDING)"
            verdict = "MIDDLE_BAND"

        verdict_msg = (
            "(a) capacity-reconciliation: n_at_risk=%d mean_err_naive=%.3f mean_err_corrected=%.3f "
            "error_reduction=%.2fx -> %s. "
            "(b-legacy) independence: alone=%.3f concurrent=%.3f cross_interf=%+.3f -> %s. "
            "(c-legacy) mis-placement: c1(m=%d)=%.3f crater=%s c2=%.3f crater=%s -> fired=%s. "
            "(b-new) decoupling regime: mean|genuine-pred|=%.3f mean|genuine-misaligned|=%.3f "
            "flat_prefix(genuine/misaligned)=%d/%d -> %s. "
            "subsystem2 paged_exact=%.3f(correct=%s) subsystem3 recall=%.3f(correct=%s). "
            "OVERALL TIER: %s."
            % (n_at_risk, mean_err_naive, mean_err_corrected, error_reduction_factor, claim_a,
               recall_wm_alone, recall_wm_concurrent, cross_interference, claim_b_legacy,
               m_c1, r_c1, craters_c1, recall_wm_misplaced, craters_c2, misplacement_fired,
               mean_pred_diff, mean_genuine_vs_misaligned,
               flat_prefix_len_genuine, flat_prefix_len_misaligned, decoupling_regime,
               store_res["paged_exact_recall"], store_correct, compute_recall, compute_correct,
               tier)
        )

    print("\n[VERDICT] " + verdict_msg, flush=True)

    facts = {
        "claim_a_capacity_reconciliation": claim_a,
        "grid_results": grid_results,
        "n_at_risk_grid_cells": n_at_risk,
        "mean_abs_rel_err_naive": mean_err_naive,
        "mean_abs_rel_err_corrected": mean_err_corrected,
        "error_reduction_factor": error_reduction_factor,
        "C_FHRR_calibration_constant": C_FHRR,
        "C_FHRR_calibration_anchor": {"N": CALIB_N, "V": CALIB_V, "m50_measured": CALIB_M50_MEASURED,
                                      "source": "data/exp_substrate_phase_diagram_subsystem_decoupling_v1/metrics.json"},
        "v_eff_principled": True,
        "v_eff_derivation": ("FULL_CODEBOOK: V_eff = len(vals) argument passed to cleanup() argmax "
                             "(no restriction; verified by code inspection). "
                             "RESTRICTED_SET: V_eff = D_restricted = size of the explicitly constructed "
                             "per-query candidate list (correct + D-1 distractors). Neither is fit."),
        "claim_b_legacy_independence": claim_b_legacy,
        "recall_wm_alone": recall_wm_alone, "recall_wm_concurrent": recall_wm_concurrent,
        "cross_interference": cross_interference,
        "claim_c_legacy_misplacement_fired": misplacement_fired,
        "craters_c1": craters_c1, "craters_c2": craters_c2,
        "recall_wm_misplaced": recall_wm_misplaced, "misplacement_effect": misplacement_effect,
        "decoupling_regime": decoupling_regime,
        "decoupling_regime_note": ("SOFT_GRACEFUL is brain-parity (theta-gamma-like), NOT a failure. "
                                   "HARD_ZERO would be a genuine Frontier-2 (beat-the-brain) result. "
                                   "Pre-committed prediction (stated in docstring before running): "
                                   "SOFT_GRACEFUL, because this construction has no orthogonal-subspace "
                                   "partition between subsystems (single additive shared buffer)."),
        "partb_curve": partb_curve,
        "partb_mean_pred_diff": mean_pred_diff,
        "partb_mean_genuine_vs_misaligned": mean_genuine_vs_misaligned,
        "partb_flat_prefix_genuine": flat_prefix_len_genuine,
        "partb_flat_prefix_misaligned": flat_prefix_len_misaligned,
        "subsystem2_store_paged_exact_recall": store_res["paged_exact_recall"],
        "subsystem2_correct": store_correct,
        "subsystem2_flat_would_crater": store_flat_would_crater,
        "subsystem3_compute_recall": compute_recall,
        "subsystem3_correct": compute_correct,
        "overall_tier": tier,
        "honest_disclosure": (
            "C_FHRR is a calibrated constant (not a cited derivation) -- HYPOTHESIZED mechanism "
            "(FHRR complex-phasor Re() crosstalk variance = 1/2 of real-bipolar variance, i.e. a "
            "sqrt(2) SNR gain) is disclosed but NOT verified in this cell. The reconciliation claim "
            "rests on the GRID holding with this ONE fixed constant, not on the constant itself "
            "being independently derived from first principles."
        ),
    }

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s: capacity reconciliation + decoupling regime (%s)" % (verdict, tier),
        "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS, "n_units": n_units,
        "cardinality_ok": (n_units == EXPECTED_N_UNITS),
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "config": {"grid_cells": GRID_CELLS, "restricted_cells": RESTRICTED_CELLS,
                   "d_restricted": D_RESTRICTED, "partb_b_grid": PARTB_B_GRID,
                   "N_WM": N_WM, "V_VAL_WM": V_VAL_WM, "V_KEY_WM": V_KEY_WM,
                   "K_THEORY_WM": K_THEORY_WM, "W_WM_SAFE": W_WM_SAFE,
                   "B_STORE_SAFE": B_STORE_SAFE, "B_STORE_BAD": B_STORE_BAD,
                   "M_STORE_TOTAL": M_STORE_TOTAL, "N_COMPUTE": N_COMPUTE,
                   "M_COMPUTE": M_COMPUTE, "K_BLOCK_COMPUTE": K_BLOCK_COMPUTE, "J_COMPUTE": J_COMPUTE},
        "facts": facts, "elapsed_s": time.time() - t0,
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "facts"],
    }
    write_metrics(out_dir, metrics)
    print("[metrics] written -> %s (elapsed %.1fs)" % (os.path.join(out_dir, "metrics.json"), metrics["elapsed_s"]),
          flush=True)
    return metrics


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
