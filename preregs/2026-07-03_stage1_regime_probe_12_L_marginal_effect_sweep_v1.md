# Pre-registration: Stage 1 Regime Probe 12 -- L (chain-depth) marginal-effect sweep

**Date:** 2026-07-03
**Anchor:** `stage1_regime_probe_12_L_marginal_effect_sweep_v1`
**Cell:** `experiments/_stage1_regime_probe_12_L_marginal_effect_sweep_v1_core.py`
**Wrapper (seed=7):** `experiments/exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s7.py`
**Author:** exp_dev 2026-07-03 (Opus 4.7, agent-spawn)

## Purpose

Skunkworks structural VET (task afadd5dbd43055cf1, atom #48 filed 2026-07-03
21:35Z) surfaced that L (chain length in `run_chain`) is a GENUINELY DISTINCT
5th potential algebra-depth axis but is FIXED at L=2 across all recent probes
(Probes 1/2/4/5/6v2/7v2/8/9v2/10/11). The "algebra" concept in Probes 8/10
aliases to F (sharded-DAG fan-out); it is NOT the same abstraction as
SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3), which
refers to M1.9/M1.10 roundtrip K=5 (chain-depth). This probe tests whether L
has a genuine marginal effect on retrieval capacity at cliff-adjacent SHARDED
regime, or whether the L=2 convention has been masking a real 5th axis.

If H1 fires: L IS a real 5th sweep axis; today's "regime matrix complete at 6
pairs" needs revision to include L cross-terms; CG_META axis set expands.

If H2 fires: L is NOT a real axis at this signature; L=2 convention was not
masking a real axis; can atomize as inert negative finding.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: SHARDED FHRR chain composition (`run_chain` from
  `_stage1_physics_law_joint_composition_factorial_v1_core`)
- Storage: SHARDED (per-antecedent per-fan-out complex64 phasor codebook)
- N: 512 (CLIFF) / 8192 (DEEP_SAT)
- M: 6400 (CLIFF) / 800 (DEEP_SAT)
- corr: 0.85 (CLIFF) / 0.60 (DEEP_SAT)
- F: 1 (fixed to isolate L marginal effect)
- MECH: modern_hopfield | iterative_cosine | soft_energy_attractor
- BETA: 8.0; ALPHA_SOFT: 0.5 (defaults from Option Y core)
- TR: 100 (FULL) / 40 (SMOKE)
- L primitive: `run_chain(storage, mechanism, L, F, TR, ...)` L in {1,2,4,8,16}
- L semantics: number of consecutive bind-shard-unbind-cleanup iterations;
  gold = perms[f_L-1](..perms[f_0](start)..) built per-trial per-step

## Sweep grid

**FULL (25 pts / seed):**
- CLIFF arm: L in {1,2,4,8,16} x 3 mech at (N=512, M=6400, corr=0.85, F=1, SHARDED) = 15 pts
- DEEP_SAT arm (H3-NULL): L in {1,4,16} x 3 mech at (N=8192, M=800, corr=0.60, F=1, SHARDED) = 9 pts
- SATURATION_PC arm (Gate D reproducer): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

**SMOKE (13 pts / seed):**
- CLIFF arm: L in {1,4,16} (endpoints + mid) x 3 mech at CLIFF = 9 pts
- DEEP_SAT arm spot-check: L=2 x 3 mech at DEEP_SAT = 3 pts
- SATURATION_PC arm: 1 pt

## Hypotheses

**H1 (L has genuine marginal effect on retrieval capacity):**
`cliff.max_per_mech_L_spread >= 0.10`
-> L IS a real 5th CG_META axis at cliff-adjacent SHARDED; today's regime
matrix (6 pairs) needs revision. Atom candidate:
`EMPIRICAL_L_MARGINAL_EFFECT_SHARDED_CLIFF_ADJACENT_v1` MM_TENTATIVE at SMOKE,
MM_STANDARD at 3-seed FULL.

**H2 (L is INERT at cliff-adjacent SHARDED):**
`cliff.max_per_mech_L_spread < 0.05`
-> L does NOT moderate retrieval at this regime. L=2 convention was not
masking a real axis. Atom candidate:
`L_INERT_AT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1` MM_TENTATIVE.

**H3 (mechanism ranking crossover across L, MM_TENTATIVE informational):**
Mech ranking changes across L within CLIFF band.

**H3-NULL (DEEP_SAT null fires):**
`deep_sat.max_per_mech_L_spread < 0.05`
-> confirms L-axis degeneracy at deep-saturation; strengthens saturation-masks-variance thesis.

## Envelope-fail-bands

**CLIFF arm PASS band (H1):** `max_per_mech_L_spread` in [0.10, 1.00]
**CLIFF arm PASS band (H2):** `max_per_mech_L_spread` in [0.00, 0.05)
**MIDDLE_BAND (weak L moderation):** `max_per_mech_L_spread` in [0.05, 0.10)
**DEEP_SAT H3-NULL fires:** `max_per_mech_L_spread` in [0.00, 0.05)
**SATURATION_PC PASS:** `acc >= 0.95`

## Empirical bracket (MEASURED@scratchpad probe12_L_bracket 2026-07-03, TR=40 seed=7)

**CLIFF (N=512 M=6400 corr=0.85 F=1 SHARDED):**
| L | mean | spread | modern_hopfield | iterative_cosine | soft_energy_attractor |
|---|---|---|---|---|---|
| 1 | 0.825 | 0.200 | 0.950 | 0.750 | 0.775 |
| 2 | 0.733 | 0.075 | 0.725 | 0.775 | 0.700 |
| 4 | 0.442 | 0.100 | 0.375 | 0.475 | 0.475 |
| 8 | 0.200 | 0.175 | 0.175 | 0.300 | 0.125 |
| 16 | 0.067 | 0.125 | 0.125 | 0.000 | 0.075 |

Per-mech L-spread (max-min across all L in {1,2,4,8,16}):
- modern_hopfield = 0.825
- iterative_cosine = 0.775
- soft_energy_attractor = 0.700

At TR=40 single-seed, all three well above H1 threshold 0.10; H1 strongly
predicted to fire. Noise floor at TR=40 approximately sqrt(0.5/40) = 0.11
suggests 3-seed TR=100 will preserve signal.

in_band [0.30, 0.95] verdict: L in {1, 2, 4} True; L in {8, 16} False (below
floor by construction; captures cliff transition and validates the L axis is
not band-limited artifact).

**DEEP_SAT (N=8192 M=800 corr=0.60 F=1 SHARDED):**
All L in {1,2,4,8,16} across all mechs = 1.000 exact; spread = 0.000.
H3-NULL strongly predicted to fire.

## Discipline gates satisfied

- CARDINALITY_OK: EXPECTED_N_UNITS_FULL=25, EXPECTED_N_UNITS_SMOKE=13; verdict
  counts phase_map length + emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
  on mismatch.
- META_RULE_AF (ARMS-MUST-DIFFER): mechanism-output-hash aggregation across
  CLIFF arm; if 3 mechs share a hash, HARD_FAIL fires. `arms_differ_verified`
  emitted in metrics.
- META_RULE_J (per-unit failure-class): no bare except; failure-class
  propagates as RuntimeError with specific class name.
- META_RULE_K (discriminator-fires): pre-reg declares `max_per_mech_L_spread`
  as discriminator; smoke gates informationally on it (null-hypothesis
  discipline per feedback_smoke_gates_null_hypothesis).
- META_RULE_L (strictly-above-floor): H1 uses `>= 0.10` (not just above 0);
  MIDDLE_BAND for [0.05, 0.10).
- META_RULE_M (calibration): `default_ok_for_this_regime` -- BETA=8.0
  ALPHA=0.5 inherited from Option Y core; empirical bracket at TR=40 confirms
  discriminator present in this regime.
- META_RULE_AF (arms differ): CLIFF-arm mechanism hashes aggregated; verified
  distinct at smoke gate + FULL.
- META_RULE_AH (atomic final metrics): `tmp_replace` via `os.replace()`
  everywhere.
- META_RULE_AG (baseline_in_band): empirically confirmed L={1,2,4} lands in
  [0.30, 0.95]; L={8,16} intentionally below floor to span cliff.
- META_RULE_AC (numbers tagged): all empirical numbers in this pre-reg tagged
  MEASURED@scratchpad probe12_L_bracket.py 2026-07-03.
- `except SystemExit: raise` before `except Exception` in wrapper.
- CRLB: `crlb_n/a: "categorical accuracy; discriminator is per-mech L-spread"`
- HP_SCOPE per-arm:
  - CLIFF arm: `[H1_marginal_effect | H2_inert | MIDDLE_BAND_weak]`
  - DEEP_SAT arm: `[H3_NULL_fires]` (informational; MUST saturate; regime
    drift = HARD_FAIL)
  - SATURATION_PC arm: `[Gate_D_reproducer]` (>= 0.95 required or HARD_FAIL)
- `progress_logging: "print_flush_true"` -- per-phase-point flush prints in
  `run_one_seed`; timeout_s < 1800 for smoke so not strictly required but
  applied anyway.

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point (build_rules
+ run_chain use `torch.matmul` internally); Python for-loop across (L, mech)
sweep is unavoidable (each phase point requires independent state build).
Wall-time smoke on CPU estimated ~30-60s total (13 phase points at 1-3s each).
FULL on CPU estimated ~2-5 min (25 phase points at 3-10s each; TR=100 vs 40).
GPU available but modest sizes (N<=8192, M<=6400) -- CPU adequate for smoke;
FULL routes remote when Tailscale restored.

## Progress logging

`progress_logging: "print_flush_true"` -- every per-phase-point line uses
`flush=True`.
`progress_cadence_expected_s: 15` (per-phase-point cadence ~1-10s).

## SCHEMA-VET §15 gates

- **A) effective_vs_nominal_parameter_audit:** L is directly settable in
  run_chain; no partition/routing intermediary changes effective L. Sweep
  aligned. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** predicted per-L mean-acc from
  bracket: {L=1: 0.825, L=2: 0.733, L=4: 0.442, L=8: 0.200, L=16: 0.067}.
  Points in discriminating band [0.30, 0.70]: L=4 (0.442). Points in extended
  band [0.30, 0.95]: L=1, L=2, L=4. `discriminating_fraction: 3/5 = 0.60`
  (against extended band); `>= 0.30` satisfied.
- **C) signal_shape_compatibility_audit:** L feeds into run_chain step count;
  no cross-primitive signal-shape edges introduced. `composition_edges: []`
  (single-primitive cell; no shape-mismatch risk).
- **D) reproduce_prior_chain_grade_result_as_positive_control:**
  `positive_control_arms: [SATURATION_PC]` reproduces Gate D easy regime at
  L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine >= 0.95, matching Probes
  6/7/8 baseline SATURATION_PC threshold. `regime_extension_audit: SHAPE_MATCH`
  (same primitive as Probe 8; only sweep axis differs).
- **E) functional_requirement_decomposition_present:** functional requirement
  = "test whether L axis has marginal effect on chain retrieval accuracy at
  cliff-adjacent regime"; primitive = `run_chain` with L parameter (existing
  chain-grade primitive from Option Y core).

## Additional cell-template mandates satisfied

- `arms_differ_verified`: bool (smoke asserts 3 mech-output-hashes distinct)
- `final_metrics_atomicity: "tmp_replace"`
- `crlb_n/a: "categorical accuracy; discriminator per-mech L-spread"`
- `baseline_in_band`: empirically verified L in {1,2,4} mid-band; L in {8,16}
  below floor by intent (cliff-spanning)
- `cell_chunked: true` (one seed per sibling file)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: false` (per-phase-point flush prints suffice at this
  scale; short cell)
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
- Do NOT overclaim CG_META axis expansion at SMOKE.
- If H1 fires at 3-seed FULL: atom `EMPIRICAL_L_MARGINAL_EFFECT_SHARDED_CLIFF_ADJACENT_v1`.
- If H2 fires at 3-seed FULL: atom `L_INERT_AT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1`.

## Independence

Independent of Skunkworks BUNDLED bimodal VET (task a15d50b89be3f7b5f) and
P9 v2 N x L cross-term (task a65fbcfda40db8b24) -- different files, different
anchor. This probe alone tests L marginal-effect at cliff-adjacent SHARDED F=1.
