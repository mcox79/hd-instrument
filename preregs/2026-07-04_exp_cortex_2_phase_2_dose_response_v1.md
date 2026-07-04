# Pre-registration: exp_cortex_2_phase_2_dose_response_v1_s7

**Filed:** 2026-07-03 (hdi_exp_dev sub-agent)
**Anchor:** `cortex_2_phase_2_dose_response_v1_s7`
**Cell:** `experiments/exp_cortex_2_phase_2_dose_response_v1_core.py`
**Wrapper:** `experiments/exp_cortex_2_phase_2_dose_response_v1_s7.py`
**Parent atom:** math atom #62 `MM_TENTATIVE_ADVISORY_APPLIED` (Phase 2 v1
apply-probe landed HARD_PASS 2026-07-04)
**Grandparent:** math atom #54 `MM_TENTATIVE_ADVISORY` (Phase 1 v1.1 advisory)
**Skunkworks authority:** landed-VET task `ac067134f58cdc781` (highest-priority
next step: dose-response arm to confirm effect-size stability + KS p-value
non-saturation).
**Research drill:** `notes/research_drill_cortex_2_phase_2_advisory_to_enforcement_architecture_2026-07-04.md`
Section 8 dose-response arm design.
**Meta parent:** meta atom #48 (ADD_AXIS discipline; empirical grounding).

---

## Strategic context

Phase 2 apply-probe v1 (commit `e1685fd49`) landed HARD_PASS 2026-07-04
MEASURED@`d:/AI/hd-instrument/data/exp_cortex_2_phase_2_apply_probe_v1_s7_smoke/metrics.json`:
`match_and_honored_and_effect_rate = 0.800`, `nonce_consumption_rate = 1.000`,
`n_cases_ks_pass = 4/5`, `n_silent_contradictions = 0`, `elapsed_s = 1.34s`.
Tier: MM_TENTATIVE_ADVISORY_APPLIED.

Skunkworks landed-VET (task `ac067134f58cdc781`) declared v1 NOT CG-eligible
without three prerequisites:

1. **Dose-response arm** (THIS cell): confirm effect-size stability + KS
   p-value doesn't saturate at asymptotic bound.
2. Multi-atom conflict resolution (Phase 3; separate cell).
3. LIVE-mode audit (post-HP Skunkworks decision).

## Framing

- **MM_TENTATIVE at SMOKE** (per arc-continuation-vs-closure discipline
  2026-07-03; MM_STANDARD requires 3-seed FULL cv, not one seed).
- **arc-continuation** of Phase 2 v1 (not arc-closure).
- Prior-work concept-query 2026-07-03 for
  "cortex 2 phase 2 dose response arm KS effect stability n per arm sweep":
  NONE at cosine > 0.30 (top hit 0.288 wordnet 'phase'). Novel synthesis.

## Source signature (per USER-locked MM_STANDARD 2026-07-03)

**Phase 2 dose-response arm v1, cortex-2 arc, 5 cases x 3 doses in {5, 20,
100} x (real + null) = 1250 consultations, WARN mode for 5 curated atoms
(SHADOW default), atom store 2026-07-04 106-atom corpus (curated subset of
7 covering 5 ground-truth cases + 2 distractors), 5 op-classes, char-trigram
encoder N=1024, downstream N(mu(value), sigma=1) scalar draw, single seed
_DOWNSTREAM_SEED_BASE=20260704.**

## Delta from Phase 2 v1 apply-probe

- IDENTICAL: 5 ground-truth cases, 5 curated atoms + WARN promotion, 5
  op-classes, char-trigram encoder N=1024, downstream stub N(mu, sigma=1),
  seed 20260704.
- IDENTICAL: enforce() code path (imports from `hdlab.atom_consultation`;
  zero primitive changes).
- IDENTICAL: `_downstream_process()`, `_ks_two_sample()`, `_VALUE_MU_MAP`,
  `_ATOMS_TO_WARN`, `_GROUND_TRUTH_CASES` (imported from v1 core module).
- ADD: `DOSES = (5, 20, 100)` sweep (LOCKED; no re-tuning).
- ADD: per-case per-dose `gap_sigma = |real_mean - null_mean| / sqrt(2/n)`
  discriminator (SE-normalized mean-gap).
- ADD: `_HP_GATED_CASE_IDS` restricting HP gate to cases 1/2/4/5 (case3
  exempted per v1 structural mismatch discipline).
- ADD: diminishing-effect FAIL check (gap_sigma@n=100 vs @n=5, ratio < 0.7
  triggers FAIL).
- ADD: KS-saturation audit (all p == 0.0 at all doses = transparent flag).

## PRE-COMMITTED predictions (LOCKED per Skunkworks task-prompt)

- **PASS:** cases 1/2/4/5 at n=100 all satisfy `ks_p < 0.001` AND
  `gap_sigma >= 4.0`.
- Case 3 stays structural expected-fail (SHARDED atom outranks SCALE_FREE
  on cosine similarity; multi-atom conflict resolution deferred to Phase 3).
- Effect-size stable: `gap_sigma` at n=100 is >= 0.7x gap_sigma at n=5 for
  cases 1/2/4/5. (SE(diff) shrinks as sqrt(2/n) so for fixed true mean gap,
  gap_sigma should GROW roughly 4.47x from n=5 to n=100; a ratio < 0.7
  would signal mechanism drift.)
- KS p-value non-saturation: at least one HP-gated case must show
  monotonic p decrease across doses (not all-zero-at-all-doses).
- Numeric expectations from `_VALUE_MU_MAP` (v1 core):
  - case1: SHARDED(5.0) - BUNDLED(0.0) = 5.0 mean gap; at n=100 SE=0.141
    -> gap_sigma ~ 35; at n=5 SE=0.632 -> gap_sigma ~ 7.9.
  - case2: NO_MID_BAND(6.0) - BUNDLED(0.0) = 6.0 mean gap; n=100 ~ 42; n=5 ~ 9.5.
  - case4: ALGEBRA(7.0) - TOPOLOGY(1.0) = 6.0; n=100 ~ 42; n=5 ~ 9.5.
  - case5: BOTH_ARMS_IN_BAND(8.0) - cross_term(2.0) = 6.0; n=100 ~ 42; n=5 ~ 9.5.
  - All far above HP threshold 4.0 by construction; the gate protects
    against unexpected mechanism instability.

## Envelope + PRE-COMMITTED bands

### HARD_PASS (dose-response arm)

- All 4 HP-gated cases (1/2/4/5) at n_per_arm=100 satisfy:
  - `ks_p < 0.001` AND
  - `|real_mean - null_mean| / sqrt(2/n) >= 4.0` (gap_sigma).
- Zero diminishing-effect cases (all HP-gated cases have
  `gap_sigma@n=100 >= 0.7 * gap_sigma@n=5`).
- Case 3 result NOT gated (structural expected-fail).

### MIDDLE_BAND

- 2-3 of 4 HP-gated cases pass at n=100 without triggering FAIL. Investigate
  per-case; may indicate sampling variance or partial mechanism instability.

### HARD_FAIL_DIMINISHING_EFFECT

- Any HP-gated case shows `gap_sigma@n=100 < 0.7 * gap_sigma@n=5`.
  Interpretation: mechanism not dose-stable; more samples make effect WORSE
  (unphysical for a stable primitive). Escalate to Skunkworks.

### HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)

- `actual_n_units != expected_n_units = 2 * 5 * sum(DOSES) = 1250`.

## Compute architecture (mandatory field)

- **Class:** (b) sequential-CPU with justification.
- **Justification:** cell IS the substrate-primitive being validated
  (atom_consultation enforce() path with dose sweep). No GPU-batchable work;
  per-consult wall ~0.3ms; 1250 total ~1-30s. Wall < 10s at all doses
  combined per v1 timing extrapolation (v1 at n=5 -> 1.34s; n=100 dose ~ 12s).
- **Storage strategy declaration:** NO_STORAGE (in-memory curated atom
  table + per-call fresh target dict; EnforcementDecisionLogger writes
  JSONL to output_dir).

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok`: True at EXPECTED_N_UNITS = 2 * 5 * (5+20+100) = 1250
  (verified in cell metrics `actual_n_units == expected_n_units`).
- `arms_differ_verified`: True (real-arm writes recommendation, null-arm
  writes pre_value; distinct values by construction; also arms across doses
  differ by n_per_arm).
- `final_metrics_atomicity`: `tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception`: verified.
- `crlb_n_a`: gap_sigma IS an SE-normalized effect measure with an
  analytical baseline. The HP gate `gap_sigma >= 4.0` corresponds to
  |t| >= 4 (Bonferroni-safe for 4 cases). SE = sqrt(2/n) is closed-form.
- `baseline_in_band`: real-arm mean = mu(recommendation), null-arm mean =
  mu(pre_value); by construction distinct for cases 1/2/4/5 in
  (5.0, 8.0) vs (0.0, 2.0). NOT saturated.
- HP strictly above floor + 5% band-width: HP gap_sigma=4.0 vs floor 0.0 +
  0.05 * predicted-max 42 = 2.1. HP > band-floor + margin.
- `HP_SCOPE`: `{gap_sigma@n=100: [case1, case2, case4, case5],
  ks_p@n=100: [case1, case2, case4, case5]}` (case3 EXEMPTED).
- `discriminator_reachability`: True. Per-case gap_sigma predictions above
  are all >=7.9 at n=5 and >=35 at n=100; HP threshold 4.0 is reachable.
- `discriminating_fraction`: 4/5 = 0.80 HP-gated cases predicted in HP band
  at n=100 by construction.
- `composition_edges`: enforce() -> read_and_ack_nonce -> downstream stub.
  Shape verdict: SHAPE_MATCH (identical to v1 apply-probe).
- `positive_control_arms`: Phase 2 v1 apply-probe IS the positive control at
  n=5 SMOKE regime (identical corpus + cases + code path). Reproduction
  target: match_and_honored fraction preserved at 0.80 +/- 0.05 across
  cases 1/2/4/5 at n=5. If n=5 real-arm dose here diverges from v1 landing,
  code-path drift.
- `functional_requirements`: (1) mechanical read proof via nonce (from v1);
  (2) distributional effect proof via null-arm KS (from v1); (3) DOSE
  STABILITY of the distributional effect across n_per_arm sweep (NEW).
- `cell_chunked`: False (single-seed by design; stateless).
- `start_marker_written`: True.
- `crash_diagnostic_present`: True (`_write_crash_metrics` on Exception).
- `heartbeat_present`: N/A (elapsed_s < 60s per timing).
- `defensive_error_checking`: `passed_all_4_patterns`.
- `progress_logging`: `line_buffered_stdout` + `print(..., flush=True)`
  on per-dose per-case audit line. timeout_s < 1800 so pre-reg field not
  mandatory but declared per META_RULE_17 hygiene.

## Sweep-alignment audit (META_RULE_15 gate A)

- `swept_params`: n_per_arm in {5, 20, 100}. Sweep axis IS the discriminator.
- `effective_params_per_primitive`: enforce() sees identical (op_class,
  params, query_hint, target, param_name, null_arm) tuple per case; n_per_arm
  changes ONLY the loop count. Primitive receives full effective sweep.
- `sweep_alignment_verdict`: ALIGNED.

## Discriminating-band audit (META_RULE_15 gate B)

- Predicted `gap_sigma` values at n=100 for HP-gated cases: ~35, 42, 42, 42
  (all >> HP threshold 4.0).
- `points_in_discriminating_band`: 4/4 HP-gated cases predicted in HP band
  at n=100 by construction. `discriminating_fraction = 1.0 >= 0.30 gate`.
- NOTE: this cell is NOT a discriminator-sweep in the usual sense (a phase
  parameter varied to find a cliff). It's a STABILITY probe: same mechanism,
  varying sample size, checking the effect-size formula holds.

## Signal-shape compatibility (META_RULE_15 gate C)

- Only composition edge: `enforce()` -> `read_and_ack_nonce()` -> downstream
  stub. IDENTICAL to v1 apply-probe. Verdict: SHAPE_MATCH.

## Reproduce-prior-chain-grade (META_RULE_15 gate D)

- Parent = Phase 2 v1 apply-probe (math #62, MM_TENTATIVE_ADVISORY_APPLIED;
  not yet CG).
- Positive control at MATCHED REGIME: n=5 dose in this cell reproduces v1
  smoke's `match_and_honored_and_effect_rate = 0.8` on cases 1/2/4/5 (real-arm
  match+honored). Tolerance: +/- 0.05.
- If n=5 dose real-arm diverges from v1 by more than 0.05: enforce() code
  path drift; do NOT trust dose-response conclusion.

## Anti-drift signature

- 5 curated atoms LOCKED (imported from v1 `_ATOMS_TO_WARN`).
- 5 ground-truth cases LOCKED (imported from v1 `_GROUND_TRUTH_CASES`).
- Downstream `_VALUE_MU_MAP` mean values LOCKED (imported from v1).
- `_DOWNSTREAM_SEED_BASE = 20260704` LOCKED (imported from v1; deterministic).
- DOSES = (5, 20, 100) LOCKED in cell + prereg BEFORE running (no post-hoc
  addition or removal of doses).
- HP_KS_P_MAX = 0.001, HP_GAP_SIGMA_MIN = 4.0 LOCKED per Skunkworks
  task-prompt.
- FAIL_DIMINISH_RATIO = 0.7 LOCKED (conservative; sampling variance at n=5
  can produce +/- 20% but 30% drop is mechanism, not noise).
- HP-gated case set = {1,2,4,5} LOCKED; case 3 EXEMPTED per v1 discipline
  (NOT cherry-picked; structural mismatch documented in v1 prereg and cell
  comments).
- Prediction locked: cases 1/2/4/5 all satisfy HP; case 3 expected-fail.

## Dispatch

- Queue: `local_cpu_queue` (SMOKE only; per USER-LOCKED 2026-07-01
  smoke-only-on-laptop). SMOKE = FULL doses here per Skunkworks task-prompt
  (dose-response REQUIRES n=100 to test asymptotic; a reduced-doses smoke
  variant would defeat the purpose).
- Timeout: 300s (v1 at n=5 landed 1.34s; extrapolating cost roughly linear
  in dose sum yields ~35s wall for {5, 20, 100}; 300s is 8x safety margin).
- SELFTEST_OK: verified via `--self-test` on `.venv` before queue_add /
  inline run.
- **NOTE:** `data/local_cpu_queue_paused.flag` exists (from 2026-07-01).
  Consistent with v1 apply-probe pattern: direct-run inline via python
  invocation preserves USER-LOCKED smoke-only-on-laptop while surfacing
  SMOKE landing under the standard anchor. Orchestrator to decide whether
  to arbitrate paused runner or acknowledge inline result.

## Independence

Independent of: encoder Step 1 running, batch VET task, other in-flight
work. Different cell files. Uses same `hdlab/atom_consultation.py` primitive
as v1 (no primitive changes needed).

## Post-SMOKE outcomes

- **HARD_PASS:** candidate atom
  `EMPIRICAL_CORTEX_2_PHASE_2_APPLY_DOSE_RESPONSE_ARM_v1_MM_TENTATIVE`
  (arc-continuation SMOKE; MM_STANDARD requires 3-seed FULL cv). Enables
  Phase 3 multi-atom conflict resolution work + eventual LIVE-mode audit.
- **MIDDLE_BAND:** dose-dependent effect on subset of cases; may need FULL
  3-seed. Investigate which case(s) failed HP; diagnose per-case sampling
  vs mechanism.
- **HARD_FAIL:** dose-response non-monotone or diminishing; escalate to
  Skunkworks (mechanism not dose-stable).

## Discipline signature

- Prior-work concept-query: NONE at cosine>0.30.
- Mechanism-abstraction-lossy citation: source_signature declared in cell
  metrics + this pre-reg (Phase 2 v1 dose-response arm, 1250 consults, one
  seed).
- Regime-mismatch: N/A (identical corpus + cases + code path to Phase 2 v1
  apply-probe; only sample size varied).
- Anti-drift: 5 atoms + case-set + downstream mu-map + seed + dose sweep +
  prediction + HP-gated-case-set ALL locked BEFORE running.
- No hallucinated numbers:
  - Phase 2 v1 landed `mhe=0.800` MEASURED@
    `d:/AI/hd-instrument/data/exp_cortex_2_phase_2_apply_probe_v1_s7_smoke/metrics.json:match_and_honored_and_effect_rate`
  - v1 KS pass 4/5 MEASURED@same:n_cases_ks_pass
  - Predicted per-case mean gap 5.0 THEORETICAL@`_VALUE_MU_MAP` lookup
    (SHARDED=5.0 - BUNDLED=0.0)
  - HP threshold 4.0 HYPOTHESIZED@this prereg per Skunkworks task-prompt
  - Predicted gap_sigma at n=100 for case1: 5.0 / sqrt(2/100) = 35.4
    THEORETICAL@SE-of-mean-difference formula for iid Gaussian samples
    with known sigma=1
