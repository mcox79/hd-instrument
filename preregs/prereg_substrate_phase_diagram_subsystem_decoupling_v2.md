# Pre-registration: substrate_phase_diagram_subsystem_decoupling_v2

Chain-grade RECONCILIATION cell (USER 2026-07-17), promoting v1 (257947144,
landed MEASURED_MECHANISM/mixed). Full pre-reg embedded in the cell docstring:
`experiments/exp_substrate_phase_diagram_subsystem_decoupling_v2.py` (top).
This file is the pointer + condensed summary for queue_add.sh provenance.

## Question

v1's ONLY blocking axis was a 6.1x transition-vs-theory miss (naive K_cliff =
N/(4 ln V) predicted 61.55, measured 375.96 at N=1024, V=64). Research drill
`notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_2026-07-17.md`
diagnosed two compounding, cited effects: (1) V_eff (the comparison-set size
ACTUALLY compared at cleanup, Plate's "m" / Frady-Kleyko-Sommer's "D"), not
raw codebook V; (2) the EXACT-INTEGRAL capacity (Frady, Kleyko & Sommer 2018)
vs the classical asymptotic approximation that underestimates true capacity.
(1) Does a formula built from these two effects (V_eff + exact-integral, one
calibration constant fit ONCE against the v1 anchor and held fixed) predict
the measured 0.5-recall crossing across a GRID of (N,V) cells, genuinely at
risk (not back-fit per point)? (2) Is the shared-buffer decoupling GENUINE
(hard-zero, RIP/CDMA-style) or VACUOUS/GRACEFUL (theta-gamma-style, brain
parity) under a contention sweep that extends past the single previously-
tested operating point, with a misalignment control?

## Reconciliation formula (at-risk, predict-then-verify)

`K_corrected(N, V_eff) = C_FHRR * N / s50(V_eff)^2`, where `s50` solves the
Frady-Kleyko-Sommer exact integral `p_corr(s50, V_eff) = 0.5` (own portable
erf-approximation quadrature, no scipy dependency), and `C_FHRR = 1.9934` is
calibrated ONCE against the ALREADY-LANDED v1 anchor (N=1024, V=64,
m50_measured=375.958, MEASURED@data/exp_substrate_phase_diagram_subsystem_
decoupling_v1/metrics.json) then HELD FIXED for every other grid prediction.

V_eff derivation (principled, NOT fit): FULL_CODEBOOK condition -> V_eff = V
(the harness's cleanup argmax scans the entire val codebook every query,
verified by code inspection -- no restriction exists in this construction).
RESTRICTED_SET condition (separate arm, tests the V_eff-distinct-from-V
sub-hypothesis in isolation) -> V_eff = D_restricted = 16 (the deterministic
size of the per-query candidate list actually constructed).

## Grid (11 cells; 1 excluded from error stats as the calibration source)

FULL_CODEBOOK: N in {512, 1024, 2048} x V in {16, 64, 256} = 9 cells (incl.
the (1024, 64) calibration point, measured fresh here as a reproduction/
positive-control check but excluded from the at-risk error statistics).
RESTRICTED_SET (D_restricted=16): (N, V) in {(1024, 256), (2048, 256)} = 2
cells. 10 at-risk cells total.

## Falsifiable bands (set BEFORE running FULL)

CLAIM (a): mean_abs_rel_err_corrected <= 0.20 AND error_reduction_factor
(mean_abs_rel_err_naive / mean_abs_rel_err_corrected) >= 3.0 -> HARD-PASS;
1.5 <= reduction < 3.0 -> MIDDLE_BAND; reduction < 1.5 -> HARD-FAIL (genuine
refutation of the V_eff+exact-integral hypothesis).

CLAIM (b, new): decoupling-regime characterization via a contention sweep
(B in {0,12,50,100,200,400,620,862,1200,1728}, shared buffer load) for GENUINE
(independent random co-resident content, v1's mechanism unchanged) vs
MISALIGNMENT_CONTROL (co-resident content drawn from WM's own val codebook).
Pre-committed prediction (stated before running, at risk): SOFT_GRACEFUL,
because this construction has no orthogonal-subspace partition between
subsystems (single additive shared complex buffer) -- predicts GENUINE tracks
a combined-load formula `p_corr(sqrt(N/(w_wm+B)), V_val)` and is statistically
similar to MISALIGNMENT_CONTROL. HARD_ZERO (a stronger, prior-overturning
result) requires a flat-zero-then-knee GENUINE curve that MISALIGNMENT_CONTROL
does not share. MIDDLE = neither cleanly fires (an anticipated, honest outcome
per the drill's own falsifiable bands, not a design failure).

CLAIM (b-legacy)/(c-legacy): v1's DECOUPLED / FIRED gates, config UNCHANGED
(W_WM_SAFE=12, B_STORE_SAFE=12, B_STORE_BAD~862) -- kept for package continuity.

## Overall tier (CLAIM, VET-PENDING -- never asserted as fact by this cell)

"chain-grade (reconciled)": (a)=HARD_PASS AND legacy(b)=DECOUPLED AND
  legacy(c)=FIRED AND regime in {HARD_ZERO, SOFT_GRACEFUL} (not MIDDLE).
"MEASURED_MECHANISM (mixed)": any single claim MIDDLE_BAND/PARTIAL.
"construction-proof only / genuine negative": (a)=HARD-FAIL OR legacy claim
  INTERFERES/NOT-FIRED.

## Schema-vet gates (see docstring for full detail)

storage_strategy=mixed (explicit exemption, comparison arms); cardinality_ok
EXPECTED_N_UNITS declared per RUN_MODE (grid points + restricted points +
legacy b/c + c1-probe + Part-B sweep + store + compute); real_code_path/
substrate_signature N/A (self-contained numpy FHRR, no KGStore);
deterministic_seeding=fixed ints only; discriminator survives scale (smoke =
SAME real N/V values as FULL, fewer cells/points/seeds -- option A);
arms_differ_verified=True (hashes actual generated codes across 6 distinct
arms); final_metrics_atomicity=tmp_replace; progress_logging=print_flush_true.

## Compute architecture

(b) sequential-CPU with justification: vectorized numpy matmuls per grid cell
(batched over all m queries, not a python loop over items); all arrays
N<=2048, m<=~2600, V_val<=256; measured wall time smoke=20.4s, FULL=128.8s.
No GPU speedup needed at this scale. Local numpy only; no remote queue-push /
GPU / atoms / origin push.

## Measured (landed locally; both smoke and FULL)

SMOKE (2 seeds grid, 5-cell grid, elapsed 20.4s): cardinality_ok=True (76/76).
claim(a): n_at_risk=4, mean_err_naive=0.857, mean_err_corrected=0.050,
error_reduction=17.27x -> HARD_PASS. legacy(b)=DECOUPLED. legacy(c): c1
crater=True, c2 crater=False (0.375 vs 0.35 threshold, 2-seed noise around
the v1-established 0.333 boundary) -> fired=False at smoke scale only.
Part-B regime = MIDDLE at smoke resolution.

FULL (3 seeds grid, 11-cell grid + 2 restricted, elapsed 128.8s):
cardinality_ok=True (379/379).
  claim(a): n_at_risk=10, mean_err_naive=0.861, mean_err_corrected=0.029,
    error_reduction=30.00x -> HARD_PASS (well beyond the >=3x/<=20% bar;
    holds across ALL 3 N values, ALL 3 V values, AND the RESTRICTED_SET arm).
  legacy(b): alone=1.000 concurrent=1.000 cross_interference=+0.000
    -> DECOUPLED (identical to v1).
  legacy(c): c1(m=862)=0.254 crater=True; c2(store_window=862)=0.3330
    crater=True -> fired=True (c2 EXACTLY reproduces v1's landed 0.3330,
    same unchanged mechanism+config+seeds).
  Part-B (new): mean|genuine-pred|=0.133, mean|genuine-misaligned|=0.050,
    flat_prefix(genuine)=3 vs flat_prefix(misaligned)=4 -> decoupling_regime
    = MIDDLE (neither SOFT_GRACEFUL nor HARD_ZERO cleanly fires; an honest,
    anticipated outcome per the drill's own bands, not a manufactured result).
  OVERALL TIER: MEASURED_MECHANISM (mixed; CLAIM, VET-PENDING) -- the 6x
    capacity-formula miss is CLOSED (claim a HARD_PASS), but the NEW
    regime-characterization sub-question (added scope beyond v1) remains
    open; full "chain-grade (reconciled)" promotion is gated on that
    characterization resolving, per this cell's own pre-registered bands.
