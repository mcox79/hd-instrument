# exp_dev hand-off — research: dopamine-modulated LR alternatives (2x post-HARD_FAIL)

**Filed:** 2026-06-23 by research sub-agent (after 2x revival drill on `substrate_meta_lr_dopamine_analog_v1` HARD_FAIL).

**Trigger:** `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` HEADLINE recommends DURATION-extension rescue as highest-yield discriminator (P_deflated=0.50 HARD_PASS; novel-synthesis ceiling) against the BETA=1.0 multiplicative-positive failure.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS + PRE-REG BANDS only. exp_dev designs ALL of: N_TRAIN, V, exact seed count, encoder pipeline (must mirror chain-grade fair_harness sparse-bipolar at f=0.05), smoke profile, FULL profile parameters, queue choice, atexit synthesizer detail. Research provides FAILURE-MODE analysis + CANDIDATE RANK ORDER + PRE-REG BANDS.

---

## Failure mode diagnosis (from research note)

v1 cell used `alpha_t = base_lr * (1 + beta * clamp(rpe_t / ema_rpe, 0, 5))` with BETA=1.0. Four distinguishable errors vs brain canonical:

1. **MAGNITUDE not DURATION.** Brain (Gong/Coddington 2026 *Science*; our own Store 2026-05-24) modulates LR-effect via eligibility-trace DURATION, not per-token alpha scaling.
2. **POSITIVE-multiplicative.** Brain canonically SATURATES (Schultz sigmoid) or INVERSE-modulates (Yu-Dayan caution) — does NOT amplify proportionally.
3. **EMA timescale too short (~20 steps).** Brain timescales correspond to ~200+ token windows for stable noise floor.
4. **Wrong neuromodulator analog.** Per Doya 2002, LR is controlled by ACh (environmental stability), not dopamine (RPE); v1 conflated them.

---

## Anchor candidates (rank-ordered)

### Rank 1 (HIGHEST yield, dispatch FIRST)

**Anchor:** `substrate_meta_lr_duration_extension_v1`

- **Anchor pointer:** `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` FORMULA 1 section.
- **Substrate-product reading:** Brain-canonical eligibility-trace-DURATION extension (Gong/Coddington 2026 magnitude-via-duration; Brzosko-Paulsen 2017 dopamine broadens STDP window). Substrate test: each high-RPE token's update PROPAGATES forward to next K tokens where K = K_base * (1 + gamma * normalized_rpe), with exponential decay. Preserves base_lr; extends WINDOW not MAGNITUDE. If HARD_PASS, opens substrate-product capability "context-extension learning rule" (genuine differentiator vs GPT/Llama timestep-local credit).
- **Tier hint:** Likely Remote CPU at N=8192. ~30-45 min wall at production N_TRAIN=100k 3 seeds (slightly slower than v1 due to K-step propagation; mitigate via batched outer-product cache).
- **Why now:** USER duration-vs-magnitude intuition + our own 2026-05-24 research note explicitly predicted this; v1 cell IGNORED that prior finding. Cheap, brain-unambiguous, composes with TAU_NEG=10 STDP in flight (Brzosko shows dopamine broadens STDP window — same mechanism).
- **Pre-reg bands (research-provided; exp_dev must include):**
  - HARD_PASS: ARM_DURATION_LR lift >= +0.10 BPC vs ARM_FIXED_LR AND >= +0.10 vs v1's per-token magnitude formula (must replicate v1's ARM_PER_TOKEN_RPE_LR as a sanity arm); cv <= 0.05.
  - CHAIN_GRADE_BONUS: lift >= +0.20 vs ARM_FIXED_LR AND beats fair_harness sparse-bipolar 7.3065 by >= +0.30.
  - MIDDLE_BAND: lift in [+0.03, +0.10] vs ARM_FIXED_LR.
  - HARD_FAIL: within +/-0.02 of ARM_FIXED_LR (duration mechanism not load-bearing for substrate-LM).
  - **C7 INSTR_SUSPECT guard:** if best_lambda=0.0 across all arms, tag INSTRUMENTATION_SUSPECT not HARD_FAIL (per Skunkworks batch VET C7); expand LAMBDA_GRID to include {0.02, 0.05, 0.07}.
  - **Fix #28 per-arm reporting mandatory:** raw_bpc_at_T1_L1, best_T, best_lambda, top1, mrr per arm; per-arm metrics in metrics.json, NOT only verdict_msg.
- **Required arms (4):**
  - ARM_UNIGRAM (sanity)
  - ARM_FIXED_LR (control — exact ARM_FIXED_LR from v1)
  - ARM_PER_TOKEN_MAGNITUDE (replicate v1's failed formula — confirms reproducibility before adding new arms)
  - ARM_DURATION_LR (the new mechanism)

### Rank 2 (dispatch in parallel with Rank-1 — orthogonal mechanism, cheap)

**Anchor:** `substrate_meta_lr_pearce_hall_associability_v1`

- **Anchor pointer:** `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` FORMULA 3 section.
- **Substrate-product reading:** Pearce-Hall associability rule `a_t = b*|rpe_t|/norm + (1-b)*a_{t-1}`, then `alpha_t = a_t * base_lr_scale`. Classic associability (Mathys 2020 PLOS-CB shows this is equivalent to Behrens 2007 hierarchical-Bayesian volatility LR). Variance-TRACKING not magnitude-RATIO (which is v1's error). If HARD_PASS, opens substrate primitive "variance-tracked LR" — more robust than DURATION for noisy/multi-domain.
- **Tier hint:** Cheap; ~15-25 min CPU at production N=8192 (very similar compute to v1; just different alpha computation).
- **Why now:** Pearce-Hall is the longest-validated brain LR-modulation rule (~50 years); Mathys 2020 mapped it to modern Bayesian volatility models. Orthogonal failure-mode test: if Rank-1 fails and Rank-2 passes, mechanism is variance-tracking not duration-extension.
- **Pre-reg bands:**
  - HARD_PASS: ARM_PEARCE_HALL lift >= +0.07 BPC vs ARM_FIXED_LR (matches Mathys 2020 PLOS-CB simple-volatility-model gain over fixed-LR); cv <= 0.05.
  - MIDDLE_BAND: lift in [+0.03, +0.07].
  - HARD_FAIL: within +/-0.02 of ARM_FIXED_LR.
- **Required arms (3):** ARM_UNIGRAM, ARM_FIXED_LR, ARM_PEARCE_HALL.

### Rank 3 (dispatch IF Rank-1 + Rank-2 BOTH HARD_FAIL — third-line test)

**Anchor:** `substrate_meta_lr_inverse_caution_v1`

- **Anchor pointer:** `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` FORMULA 2 section.
- **Substrate-product reading:** Multiplicative-INVERSE (Yu-Dayan unexpected-uncertainty SUPPRESSES learning): `alpha_t = base_lr / (1 + beta * clamp(rpe_t / ema_rpe, 0, 5))`. Mathematical opposite of v1. Tests whether substrate's LM regime benefits from CAUTION-on-high-RPE (focus updates on confident tokens, damp updates on uncertain ones).
- **Tier hint:** Cheap; ~15 min CPU. Cell shares 95% of v1 source code — just flip the formula.
- **Why now:** If DURATION (Rank-1) AND variance-tracking (Rank-2) both fail, the brain LR-via-RPE story is BROKEN for substrate, OR the direction is REVERSED. Inverse-LR is the "direction-flip" test.
- **Pre-reg bands:**
  - HARD_PASS: ARM_INVERSE_LR lift >= +0.05 BPC vs ARM_FIXED_LR; cv <= 0.05. (Lower bar than Rank-1/2 because brain precedent is weaker for inverse-on-dopamine specifically; mechanism is sound but cross-domain support thinner.)
  - HARD_FAIL: within +/-0.02 of ARM_FIXED_LR.
- **Required arms (3):** ARM_UNIGRAM, ARM_FIXED_LR, ARM_INVERSE_LR.

### Rank 4 (3-way composition; ONLY dispatch IF Rank-1 HARD_PASSES AND TAU_NEG=10 STDP cell also lands HARD_PASS)

**Anchor:** `substrate_cfrpe_x_stdp_x_duration_3way_composition_v1`

- **Anchor pointer:** `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` Cross-thread synthesis section.
- **Substrate-product reading:** 3-way superadditive composition of cf-RPE delta-rule + STDP timing-window + duration-extension. Brzosko-Paulsen 2017 shows dopamine BROADENS STDP window = SAME brain mechanism as Gong/Coddington duration-extension. If both substrate mechanisms capture the same brain mechanism via different routes, they should COMPOSE multiplicatively (like prior validated cfrpe x stdp superadditive cell).
- **Tier hint:** Likely Remote GPU; ~60-90 min wall. Compute-heavier (4 arms x 3 mechanisms = 12 effective configs).
- **Why now:** Only dispatch AFTER both upstream cells (Rank-1 here + the in-flight TAU_NEG=10 STDP) land HARD_PASS. Premature composition wastes compute.
- **Pre-reg bands:**
  - HARD_PASS: 3-way composition lift >= sum-of-pairs lift (superadditive) AND beats fair_harness 7.3065 by >= +0.50 BPC; cv <= 0.05.
  - MIDDLE_BAND: 3-way at-or-below sum-of-pairs (additive only; still useful but not superadditive).
  - HARD_FAIL: 3-way <= best-of-pairs (negative interaction; mechanisms interfere).
- **Required arms (5):** ARM_FIXED_LR, ARM_FIXED_LR + STDP, ARM_DURATION_LR, ARM_DURATION_LR + STDP, ARM_UNIGRAM sanity.

---

## Context pointers (file paths, not summaries)

- `notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` — full research note (THIS hand-off's source)
- `notes/research_dopamine_article_drill_2026-05-24.md` — prior Store note that ALREADY identified DURATION as load-bearing (v1 ignored this)
- `data/exp_substrate_meta_lr_dopamine_analog_v1/metrics.json` — v1 failed metrics (ARM_PER_TOKEN_RPE_LR=7.0602 vs ARM_FIXED_LR=7.0642)
- `experiments/exp_substrate_meta_lr_dopamine_analog_v1.py` — v1 cell source (reuse encoder pipeline, atexit synthesizer, _seed_checkpoint)
- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` — chain-grade ARM_CFRPE_ONLY=7.1052 reference
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` — sparse-bipolar f=0.05 encoder pipeline (REQUIRED match for all rescue arms)
- `notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md` — C7 INSTR_SUSPECT guard (lambda=0.0 collapse detection)

---

## Contract section

- exp_dev MUST replicate v1's ARM_FIXED_LR exactly (encoder pipeline + base_lr=0.5 + INGEST_BATCH=64) for control-arm validity.
- exp_dev MUST include `raw_bpc_at_T1_L1` per-arm AND best_T best_lambda per-arm per Fix #28 / batch VET C7 guard.
- exp_dev MUST register pre-reg note at `preregs/2026-06-23_<anchor_name>.md` before queue_add.
- exp_dev MUST run smoke at v1's smoke regime (N=512/V=300/N_TRAIN=2k) and verify ARM_FIXED_LR smoke BPC ~ v1's 4.8934 within 0.05 before promoting to FULL. If smoke baseline drift > 0.05, halt and diagnose.
- exp_dev decides: smoke wall-time budget; per-seed runtime measurement (Fix #17); queue selection (Remote CPU recommended for Rank 1-3; Remote GPU for Rank 4).
- exp_dev SHIPS Rank-1 + Rank-2 in PARALLEL (orthogonal failure-modes; both cheap; spawn budget allows per Fix #14).
- Rank-3 and Rank-4 are CONDITIONAL — dispatch only on the trigger specified in the rank section.

---

## Autonomy declaration

Research provides: failure-mode diagnosis (4 specific errors), 4 ranked rescue candidates with pre-reg bands, brain-literature citations, substrate-product implications per HARD_PASS / HARD_FAIL path.

exp_dev decides: ALL implementation parameters (N_TRAIN exact, encoder seed strategy, atexit detail), smoke profile, FULL profile, queue assignment, spawn timing, conditional-rank dispatch decisions based on upstream verdicts.

Research does NOT decide: how to implement the duration-extension propagation algorithm (exp_dev's choice: explicit per-token K-step decay loop vs accumulated eligibility-trace vector; both are valid); EMA timescales for Pearce-Hall variance estimator (exp_dev's choice; suggest b in [0.05, 0.15] range per Mathys 2020 fits).
