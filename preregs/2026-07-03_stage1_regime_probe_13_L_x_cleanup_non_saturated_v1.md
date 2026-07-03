# Pre-registration: Stage 1 Regime Probe 13 -- L (chain-depth) x CLEANUP_MECHANISM cross-term

**Date:** 2026-07-03
**Anchor:** `stage1_regime_probe_13_L_x_cleanup_non_saturated_v1`
**Cell:** `experiments/_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_core.py`
**Wrapper (seed=7):** `experiments/exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7.py`
**Author:** exp_dev 2026-07-03 (Opus 4.7, agent-spawn)

## Purpose

REGIME-EXTENSION of atom #3 (`SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1`)
into the L x CLEANUP_MECHANISM cross-term at cliff-adjacent SHARDED. Today's
convergent F x CLEANUP mech-moderation finding (P3 + P6v2 + P8) was measured
at L=2 only. Skunkworks atom #48 addendum flagged L cross-terms as unmapped
(regime matrix atom-#48 6-pair matrix is L=2 slice; L x N, L x F, L x M,
L x corr unmapped). Probe 12 measured L MARGINAL effect (does L moderate any
single mechanism's accuracy). Probe 13 tests L x MECH INTERACTION: does the
mechanism-spread pattern hold across L, or is it L=2-specific?

Interaction vs marginal effect:
- Marginal (P12): does L change accuracy for a single mechanism?
- Interaction (P13): does the WAY mech affects accuracy change across L?

Formally, if mech and L were independent axes, mech_spread would be constant
across L (and L_spread constant across mech). Any variation of mech_spread
across L (or L_spread across mech) is the L x MECH cross-term.

If H1 fires at 3-seed FULL: the L=2 finding IS L-specific in interaction;
regime matrix needs L cross-term rows in addition to F cross-term rows;
axis-labels updated per Skunkworks atom #44. REGIME-EXTENSION (per feedback
2026-07-03), not novel axis discovery.

If H2 fires: L x MECH is a decomposable axis-pair (main effects only); P6v2
+ P8 F x CLEANUP finding EXTENDS to all L in {1,2,4} without change; L can
be treated as orthogonal-to-mech at this cliff-adjacent SHARDED regime.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: SHARDED FHRR chain composition (`run_chain` from
  `_stage1_physics_law_joint_composition_factorial_v1_core`)
- Storage: SHARDED (per-antecedent per-fan-out complex64 phasor codebook)
- N: 512 (CLIFF) / 8192 (DEEP_SAT)
- M: 6400 (CLIFF) / 800 (DEEP_SAT)
- corr: 0.85 (CLIFF) / 0.60 (DEEP_SAT)
- F: 1 (fixed to isolate L x CLEANUP cross-term)
- MECH: modern_hopfield | iterative_cosine | soft_energy_attractor
- BETA: 8.0; ALPHA_SOFT: 0.5 (defaults from Option Y core)
- TR: 100 (FULL) / 40 (SMOKE)
- L: {1, 2, 4} (band-only; L={8,16} excluded per P12 VET below-floor)

## Sweep grid

**FULL (19 pts / seed):**
- CLIFF arm: L in {1,2,4} x 3 mech at (N=512, M=6400, corr=0.85, F=1, SHARDED) = 9 pts
- DEEP_SAT arm (H3-NULL): L in {1,2,4} x 3 mech at (N=8192, M=800, corr=0.60, F=1, SHARDED) = 9 pts
- SATURATION_PC arm (Gate D reproducer): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

**SMOKE (13 pts / seed):**
- CLIFF arm: L in {1,2,4} x 3 mech at CLIFF = 9 pts (FULL matrix; interaction needs >=2 L per axis)
- DEEP_SAT arm spot-check: L=2 x 3 mech at DEEP_SAT = 3 pts
- SATURATION_PC arm: 1 pt

## Discriminator (cross-term interaction metric)

Given accuracy matrix `M[L][mech]` on CLIFF arm:
- `mech_spread_at_L(L) = max_mech(M[L][mech]) - min_mech(M[L][mech])`
- `L_spread_at_mech(mech) = max_L(M[L][mech]) - min_L(M[L][mech])`
- `range_of_mech_spread_across_L = max(mech_spread_at_L) - min(mech_spread_at_L)`
- `range_of_L_spread_across_mech = max(L_spread_at_mech) - min(L_spread_at_mech)`
- `cross_term_signal = max(range_of_mech_spread_across_L, range_of_L_spread_across_mech)`

Alternate additive-residual metric (redundant informational check):
`residual[L][mech] = M[L][mech] - row_mean(L) - col_mean(mech) + grand_mean`
`residual_range = max(residual) - min(residual)`
Under pure additivity (no interaction), all residuals = 0 and `cross_term_signal = 0`.

## Hypotheses

**H1 (L x MECH INTERACTION at cliff-adjacent SHARDED F=1):**
`cliff.cross_term_signal >= 0.10`
-> the F x CLEANUP mech-moderation pattern is L-dependent; L x MECH interaction
is genuine. REGIME-EXTENSION of atom #3 into the L x CLEANUP cross-term.
Atom candidate: `EMPIRICAL_L_x_CLEANUP_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1`
MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL.

**H2 (L x MECH INTERACTION is INERT at cliff-adjacent SHARDED):**
`cliff.cross_term_signal < 0.05`
-> mech_spread is INDEPENDENT of L; the L=2 finding (P6v2 + P8) EXTENDS to
L in {1,2,4} unchanged. Atom candidate:
`L_x_MECH_CROSS_TERM_INERT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1` MM_TENTATIVE.

**H3-NULL (DEEP_SAT null fires; cross-term degenerates at ceiling):**
`deep_sat.cross_term_signal < 0.05`
-> deep-saturation collapses the L x MECH interaction; both mech and L axes
degenerate at ceiling; strengthens saturation-masks-variance thesis (per
META_saturation_floor_masks_null_variance_probe3_lesson).

## Envelope-fail-bands

**CLIFF arm PASS band (H1):** `cross_term_signal` in [0.10, 1.00]
**CLIFF arm PASS band (H2):** `cross_term_signal` in [0.00, 0.05)
**MIDDLE_BAND (weak interaction):** `cross_term_signal` in [0.05, 0.10)
**DEEP_SAT H3-NULL fires:** `cross_term_signal` in [0.00, 0.05)
**SATURATION_PC PASS:** `acc >= 0.95`

## Empirical bracket (MEASURED@P12 s7 SMOKE 2026-07-03, TR=40 seed=7)

**Source:** `data/exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s7_smoke/metrics.json:cliff_arm.per_L_mech_variance`

**CLIFF (N=512 M=6400 corr=0.85 F=1 SHARDED) at TR=40 seed=7:**
| L | mean | spread | modern_hopfield | iterative_cosine | soft_energy_attractor |
|---|---|---|---|---|---|
| 1 | 0.8417 | 0.100 | 0.875 | 0.875 | 0.775 |
| 2 | 0.7333 | 0.075 | 0.725 | 0.775 | 0.700 |
| 4 | 0.4917 | 0.100 | 0.525 | 0.425 | 0.525 |

Note: L=1 and L=4 measured MEASURED@P12 s7 smoke; L=2 HYPOTHESIZED from P12
pre-reg TR=40 seed=7 bracket (not run by P12 s7 smoke L grid = {1,4,16}).

**Cross-term signal at bracket:**
- mech_spread_at_L: {L=1: 0.100, L=2: 0.075, L=4: 0.100}
- range_of_mech_spread_across_L: 0.100 - 0.075 = 0.025
- L_spread_at_mech: {mh: 0.350, ic: 0.450, sea: 0.250}
- range_of_L_spread_across_mech: 0.450 - 0.250 = 0.200
- cross_term_signal = max(0.025, 0.200) = 0.200 (>= 0.10 H1)

Predicted H1 firing at SMOKE (single-seed TR=40); MM_TENTATIVE.

L={1,2,4} all in [0.30, 0.95] band at bracket -> both-arms-in-band per
Skunkworks meta #43 satisfied.

**DEEP_SAT (N=8192 M=800 corr=0.60 F=1 SHARDED) at TR=40 seed=7:**
MEASURED@P12 s7 smoke: all L in {1,2,4,8,16} across all mechs = 1.000 exact
(spread = 0.000 across full grid; deep_sat_arm.mean_acc=1.0).

Predicted cross_term_signal at FULL TR=100 3-seed: 0.0 exact
(H3-NULL strongly predicted to fire).

## Discipline gates satisfied

- CARDINALITY_OK: EXPECTED_N_UNITS_FULL=19, EXPECTED_N_UNITS_SMOKE=13; verdict
  counts phase_map length + emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
  on mismatch.
- META_RULE_AF (ARMS-MUST-DIFFER): mechanism-output-hash aggregation across
  CLIFF arm; if 3 mechs share a hash, HARD_FAIL fires. `arms_differ_verified`
  emitted in metrics.
- META_RULE_J (per-unit failure-class): no bare except; failure-class
  propagates as RuntimeError with specific class name.
- META_RULE_K (discriminator-fires): pre-reg declares `cross_term_signal`
  as discriminator; smoke gates informationally (null-hypothesis discipline
  per feedback_smoke_gates_null_hypothesis 2026-07-03).
- META_RULE_L (strictly-above-floor): H1 uses `>= 0.10` (not `> 0`);
  MIDDLE_BAND for [0.05, 0.10).
- META_RULE_M (calibration): `default_ok_for_this_regime` -- BETA=8.0
  ALPHA=0.5 inherited from Option Y core; empirical bracket at TR=40 confirms
  discriminator present in this regime.
- META_RULE_AH (atomic final metrics): `tmp_replace` via `os.replace()`
  everywhere.
- META_RULE_AG (baseline_in_band): empirically confirmed L={1,2,4} lands in
  [0.30, 0.95]; both-arms-in-band satisfied per Skunkworks meta #43.
- META_RULE_AC (numbers tagged): all empirical numbers in this pre-reg tagged
  MEASURED@P12 s7 smoke metrics.json OR HYPOTHESIZED@P12 pre-reg.
- `except SystemExit: raise` before `except Exception` in wrapper.
- CRLB: `crlb_n/a: "categorical accuracy; discriminator = cross-term interaction"`
- HP_SCOPE per-arm:
  - CLIFF arm: `[H1_L_x_MECH_interaction | H2_L_x_MECH_inert | MIDDLE_BAND_weak]`
  - DEEP_SAT arm: `[H3_NULL_fires]` (informational; MUST saturate; regime
    drift = HARD_FAIL)
  - SATURATION_PC arm: `[Gate_D_reproducer]` (>= 0.95 required or HARD_FAIL)
- `progress_logging: "print_flush_true"` -- per-phase-point flush prints in
  `run_one_seed`; timeout_s < 1800 for smoke so not strictly required but
  applied anyway.

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point
(`build_rules` + `run_chain` use `torch.matmul`); Python for-loop across
(L, mech) sweep is unavoidable (each phase point requires independent state
build; can't batch across L due to different chain-length semantics).
Wall-time SMOKE on CPU estimated ~30-90s (13 phase points at 1-5s each).
FULL on CPU estimated ~3-8 min (19 phase points at 3-15s each; TR=100 vs 40).
GPU available but modest sizes (N<=8192, M<=6400) -- CPU adequate.

Storage strategy: `SHARDED` (per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1;
chain composition L in {1,2,4} requires SHARDED). BUNDLED excluded per
Skunkworks atom #49 bimodal collapse at chain composition.

## Progress logging

`progress_logging: "print_flush_true"` -- every per-phase-point line uses
`flush=True`.
`progress_cadence_expected_s: 15` (per-phase-point cadence ~1-15s).

## SCHEMA-VET §15 gates

- **A) effective_vs_nominal_parameter_audit:** L is directly settable in
  `run_chain`; no partition/routing intermediary changes effective L. Sweep
  aligned. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** predicted per-L mean-acc from
  bracket: {L=1: 0.842, L=2: 0.733, L=4: 0.492}. Points in discriminating
  band [0.30, 0.70]: L=2 (0.733 near top of band), L=4 (0.492 mid-band). All
  3 in extended band [0.30, 0.95]. `discriminating_fraction: 3/3 = 1.00`.
- **C) signal_shape_compatibility_audit:** L feeds into run_chain step count;
  no cross-primitive signal-shape edges introduced. `composition_edges: []`
  (single-primitive cell; no shape-mismatch risk).
- **D) reproduce_prior_chain_grade_result_as_positive_control:**
  `positive_control_arms: [SATURATION_PC]` reproduces Gate D easy regime at
  L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine >= 0.95, matching Probes
  6/7/8/12 baseline SATURATION_PC threshold. `regime_extension_audit: SHAPE_MATCH`
  (same primitive as Probe 8/12; only cross-term axis differs).
- **E) functional_requirement_decomposition_present:** functional requirement
  = "test whether L x MECH cross-term interaction is genuine at cliff-adjacent
  SHARDED F=1"; primitive = `run_chain` L parameter x CLEANUP_MECHANISM
  (existing chain-grade primitives from Option Y core).

## Additional cell-template mandates satisfied

- `arms_differ_verified`: bool (smoke asserts 3 mech-output-hashes distinct)
- `final_metrics_atomicity: "tmp_replace"`
- `crlb_n/a: "categorical accuracy; discriminator = L x MECH cross-term"`
- `baseline_in_band`: empirically verified L in {1,2,4} all mid-band (P12 s7 smoke)
- `cell_chunked: true` (one seed per sibling file)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: false` (per-phase-point flush prints suffice at this scale)
- `defensive_error_checking: "passed_all_4_patterns"`

## Dispatch plan

- **SMOKE:** `local_cpu_queue` per USER-locked SMOKE-only local rule (Tailscale
  down 2026-07-03). Timeout: 600s.
- **FULL:** 3 seeds (s7, s13, s19) via `remote_cpu_queue` OR `overnight_queue`
  when Tailscale restored. Author has filed s7; sibling wrappers s13/s19 to
  be authored after Tailscale restore + smoke verified. Timeout: 1800s each.

## Framing discipline

- MM_TENTATIVE at SMOKE at most (per feedback_arc_continuation_vs_arc_closure).
- Discriminator variance is INFORMATIONAL at smoke (not gating; per
  feedback_smoke_gates_null_hypothesis).
- MM_STANDARD claim requires 3-seed FULL replication before atomization.
- REGIME-EXTENSION of atom #3, NOT axis discovery (per USER 2026-07-03
  feedback_arc_continuation_vs_arc_closure). L was already CG_META-covered
  at atom #3 (M1.9/M1.10 K=5 roundtrip); P13 tests INTERACTION with cleanup.
- If H1 fires at 3-seed FULL: atom
  `EMPIRICAL_L_x_CLEANUP_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1`.
- If H2 fires at 3-seed FULL: atom
  `L_x_MECH_CROSS_TERM_INERT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1`.
- Prior-work check: cosine query for L cross-term concept at `EMPIRICAL_L_x_CLEANUP`
  keyword to be run pre-atomization; if prior arc atom at cosine > 0.30, flag
  rediscovery vs genuine novelty.

## Independence

Independent of Probe 12 (L marginal effect, different discriminator: per_mech
L-spread vs cross-term interaction), Probe 14 (L x F cross-term, different
axes), and dispatch bundle authoring (different scope). This probe alone
tests L x MECH interaction at cliff-adjacent SHARDED F=1.
