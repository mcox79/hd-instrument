# Pre-registration: substrate_activity_energy_confidence_signal_v1

**Filed:** 2026-07-02 (post-4-signal-empirical-downgrade session, Option C bounded probe)
**Anchor:** `substrate_activity_energy_confidence_signal_v1`
**Cell:** `experiments/exp_substrate_activity_energy_confidence_signal_v1.py`
**Author role:** hdi_exp_dev (bounded single-cell exploration; USER 2026-07-02 auth "we could drill on C though")

## Framing

USER's primary decision on the 4-signal confidence-architecture proposal was **Option D (move on)**. USER also authorized **Option C (substrate ACTIVITY / ENERGY signals)** as parallel bounded exploration.

Three of four confidence-signal mechanism classes already CG'd as HFs this session:
- Density (h4, h4-harness) — HARD_FAIL CG
- Spatial (h4b) — HARD_FAIL CG in both h4-harness and reframed regime
- Stochastic (lane_x_prime) — HARD_FAIL CG
- Post-hoc (lap3_12) — MIDDLE_BAND (Cramer-Rao ceiling; structural, not tunable)

All observations above were of substrate STATE (geometry / margin / consistency). This cell probes substrate **ACTIVITY** — dynamical observables during retrieval cleanup:
- **First-step ΔE** = ‖cleaned - q‖² (energy change of first cleanup iteration)
- **σ_max(J)** = largest singular value of Jacobian of cleanup around retrieved point (retrieval sensitivity to input perturbation)

**Brain analog:** prefrontal cortex tracks metabolic effort as an uncertainty proxy (Kool et al 2018 J Neurosci; Shenhav et al 2013 EVC theory). "How hard did I have to work" correlates with "how uncertain I should be." Different observable class than density/margin/entropy — those measure geometry; this measures work.

**Prior-work check (substrate-KB concept-query 2026-07-02):** `bash tools/substrate_query.sh "substrate activity energy Jacobian singular value cleanup delta effort confidence prefrontal"` — top hit cosine=0.263 (Physarum direct-retrieval; unrelated concept). NO prior arc at cosine>0.30. Novel observable class.

## Regime

**Reframed** per abe94cac drill Phase 3 skeleton (h4-harness empirically dead across 3 mechanism classes):

- `N = 8192` (substrate dim)
- `n_items = 3600` (60 clusters x 60 items)
- `INTRA_COS = 0.35` (relaxed from 0.60 — reduces ridge saturation)
- `p_target = 0.40` (contamination fraction — much higher than 4.6% h4-harness; measurable Bayes-signal room per drill)
- `TOPK = 10` (matches h4/h4b contamination-in-top-K definition)
- `n_queries_per_arm_per_seed = 400` (200 pos + 200 neg; 200 train + 200 test split)
- `seeds = [7, 17, 23]` (3-seed variance probe)
- `beta = 8.0` (softmax inverse temperature for Hopfield-style cleanup; standard for our substrate)

## Arms (4)

- **ARM_DELTA_E** — risk = ΔE = ‖cleaned - q‖², where cleaned = K^T softmax(β K q). Higher ΔE = more work moved the state = less confident.
- **ARM_SIGMA_J** — risk = σ_max(J) via power-iteration Jacobian of the same cleanup. J = β (K^T diag(p) K - cc^T) where c = cleaned. Symmetric; 5 power-iter steps suffice.
- **ARM_ABLATED_RANDOM** — risk = uniform random per query. Negative control; must produce AUC = 0.50 ± 0.05.
- **ARM_COMBINED** — logistic regression on [ΔE, σ_J] fit on train half of queries; predict on test half. Joint AUC vs individuals tests whether signals are orthogonal.

## Discriminator

For each arm, per query compute risk; contaminated label = 1 iff any injected-false-fact index in top-K. AUC over test-half queries (rank-based; matches h4/h4b implementation for cross-comparability).

## Bands

Primary discriminator = per-arm AUC on test half.

- **HARD_PASS**: at least one activity signal (ΔE or σ_J) AUC_mean ≥ 0.65 AND ARM_COMBINED AUC_mean ≥ 0.70 AND ARM_ABLATED_RANDOM in [0.45, 0.55] AND 3-seed cv ≤ 0.06 for the passing arm(s).
- **MIDDLE_BAND**: at least one activity signal AUC_mean in [0.55, 0.65] OR combined in [0.60, 0.70] (partial evidence of substrate-activity uncertainty proxy).
- **HARD_FAIL**: all activity signals AUC_mean < 0.55 AND combined AUC_mean < 0.60. Joins the confidence-signal graveyard as 4th mechanism class HF.

## Prognosis (HYPOTHESIZED@substrate-KB drill abe94cac Phase 3)

- P_CG (HARD_PASS) = 0.30-0.40 (dynamical observables have different SNR from static-geometric; Bayes-floor argument was for STATIC observables so lower P_HF than lane_x_prime)
- P_MB = 0.35
- P_HF = 0.25-0.35

## Prior-art check + prior-arc position

- Kool et al 2018 J Neurosci — PFC metabolic effort tracks uncertainty (CITED@doi.org/10.1523/JNEUROSCI.1521-17.2018)
- Shenhav et al 2013 Neuron — Expected Value of Control theory (CITED@doi.org/10.1016/j.neuron.2013.07.007)
- Ramsauer et al 2020 dense-Hopfield energy landscape (CITED — cleanup ΔE formulation)
- Substrate-KB prior arc: NONE at cosine>0.30 for this observable class (query 2026-07-02)

## Compute architecture

**(a) batched-GPU** — matmul-heavy per-query cleanup + power-iteration Jacobian. Loads:
- Batched sims: Q (400, 8192) @ K^T (8192, 3600) = (400, 3600) — matmul
- Batched cleaned: softmax x K = (400, 8192)
- Batched ΔE: elementwise ‖·‖² over 400 rows
- Batched power-iteration: 5 steps, each ~3 matmuls of size (400, 3600) or (400, 8192)

Per-arm-per-seed wall on GPU: ~2-5s; 12 units total ~30-60s. On CPU-torch: per-arm ~30-60s; 12 units ~5-10 min (feasible but slow).

**FULL routing:** overnight_queue (GPU) preferred. FULL on remote_cpu_queue is acceptable fallback (~10 min).
**SMOKE routing:** local_cpu_queue (per USER-locked 2026-07-01 smoke-only-local); reduced regime N=4096 items=1200 N_Q=50 completes in <30s on CPU-torch.

## Multi-seed smoke gate (Skunkworks META_RULE_smoke_single_seed_inflates_AUC 2026-07-02)

**Mandatory 3-seed variance probe at reduced regime BEFORE FULL:**
- SMOKE seeds = [1, 2, 3] at N=4096, items=1200, N_Q=25 per side (50 total)
- Reject FULL if 3-seed cross-arm max AUC is within 0.05 of chance (0.55) — i.e. best arm < 0.60 on smoke
- Reject FULL if ARM_ABLATED_RANDOM AUC not in [0.42, 0.58] over 3 seeds (control-arm sanity)

## SCHEMA-VET pre-dispatch fields

```yaml
arms_differ_verified: true  # per-arm risk-vector hash differs across ARM_DELTA_E, ARM_SIGMA_J, ARM_ABLATED_RANDOM
final_metrics_atomicity: "tmp_replace"  # write_metrics helper uses os.replace
cardinality_ok: true  # EXPECTED_N_UNITS = 4 arms * 3 seeds = 12
per_unit_failure_class_instrumentation: true  # except Exception with failure_class field
discriminator_fires_gate: true  # ARM_ABLATED_RANDOM baseline in [0.42, 0.58] (control fires)
baseline_in_band: true  # ARM_ABLATED_RANDOM = 0.50 by construction (chance)
strictly_above_floor: true  # HP band 0.65 vs floor 0.55 (10-pt margin > 5% band-width)
hp_scope: {ARM_DELTA_E: [activity_signal], ARM_SIGMA_J: [activity_signal], ARM_COMBINED: [combined_gate], ARM_ABLATED_RANDOM: [control_sanity_only]}
calibration_check: "default_ok_for_this_regime"  # no adaptive tuning; parameter-free ΔE/σ_max
crlb_n_a: "AUC discriminator; Bayes-floor argument in drill abe94cac was for STATIC geometric class (density/margin); dynamical observables have different SNR structure not yet characterized in closed form"
discriminator_reachability: true  # test-half N=200 queries -> AUC 0.65 achievable per lit
discriminator_survives_scale: true  # smoke uses reduced regime; FULL preview if smoke passes
cell_chunked: false  # single-seed-per-arm loop within cell; multi-seed within cell OK for 4-arm x 3-seed 12-unit
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false  # cell wall <10min; heartbeat not required per §13
defensive_error_checking: "passed_start_marker+crash_diagnostic; heartbeat_exempted_short_wall"
progress_logging: "print_flush_true"
composition_edges: []  # not composing prior CG; new observable class probe
positive_control_arms: [{arm: ARM_ABLATED_RANDOM, primitive: uniform_random, tolerance: 0.08, if_outside: HARD_FAIL_CONTROL_BROKEN}]
sweep_alignment_verdict: N/A  # not a parameter sweep
discriminating_fraction: 1.0  # all 4 arms in discriminating band by design (single-regime cell)
functional_requirements:
  - "detect contamination in top-K via substrate activity (not state) observable"
  - "verify ΔE is monotone-noisy with respect to contamination presence"
  - "verify σ_max(J) is monotone-noisy with respect to contamination presence"
  - "verify combined signal beats individual by ≥ 0.05 AUC (orthogonality test)"
```

## Grep-check discipline (Skunkworks META)

Cell must invoke substrate primitives ≥ 3 times in run():
1. `softmax(β * kb @ q)` — dense-Hopfield cleanup primitive
2. `K^T @ p` (attractor recall) — bundle-project primitive
3. `K^T @ (p * (K @ v))` — power-iteration Jacobian primitive (matmul chain)
Grep pattern: `matmul|@ kb|softmax` — expect ≥ 6 hits in run_arm_seed.

## Stage-progression compliance

Stage 3 (higher-function cortex; compositional understanding). NOT Stage 4. NOT a language benchmark. Cell tests M3 cortex confidence-signal at reframed contamination-detection regime — substrate-native observable class.

## Substrate-doesn't-know-anything rule

N/A. Cell tests contamination-detection at reframed regime with synthetic vector KB; not testing substrate against language.

## Non-blockers (per spawn prompt)

- Do NOT reuse h4-harness (empirically dead)
- Do NOT fire follow-up sub-agents
- Do NOT block on stretch4_3 / cortex integration / analogy #6 parallel spawns
- If HF: ship the atom as closure (no follow-up cells)
- If HP: reopens confidence architecture with working corner (USER decision on how to fold in)

## Dispatch plan

1. Cell-author files pre-reg (this doc) + cell + selftest
2. `python -u experiments/exp_substrate_activity_energy_confidence_signal_v1.py --self-test` — formula selftest
3. `bash tools/queue_add.sh local_cpu_queue exp_substrate_activity_energy_confidence_signal_v1 <cell_path> --smoke <timeout>` — multi-seed smoke gate on local
4. Verify smoke passes multi-seed gate (§ Multi-seed smoke)
5. Report dispatch of FULL to Orchestrator (overnight_queue GPU preferred; harness-denied to exp_dev to push)
6. REMOTE VERIFY post-FULL landing

## References

- notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md — Option C rationale
- notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md — abe94cac Phase 3 reframed regime skeleton
- Skunkworks META CG 2026-07-02 — `META_RULE_smoke_single_seed_inflates_AUC` (multi-seed smoke gate)
- experiments/exp_h4b_regime_redesign_probe_v1.py — reused harness KB/injection functions
- USER 2026-07-02 spawn auth: "we could drill on C though"
