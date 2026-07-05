# Pre-reg: schema_relation_hardneg_mined_scorer_v1 (MARGIN-augmented trained scorer loss)

**Filed:** 2026-07-05 by exp_dev. **Cell:** `experiments/exp_schema_relation_hardneg_mined_scorer_v1.py`
**Design source:** `notes/research_hardneg_mined_scorer_v1_spec_2026-07-05.md` (spec only; exp_dev owns parameterization).
**Reuses (verbatim import `ref`):** `experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py`.

## Question
The training-free post-hoc rescore (`exp_schema_relation_hubness_debias_rescore_v1`) landed MIDDLE_BAND and
is a FROZEN-slot PHANTOM (rms win = SHUFFLED-collapse; REAL-abs Hits@1 degraded). The scorer already
trains EXACT FULL SOFTMAX, so DPR/ANCE exposure-mining gives no benefit. The matched fix is a
MARGIN-augmented loss (additive-margin softmax + a z-margin-calibrated hard-neg HINGE, mining repurposed
as curriculum/target-selection) applied to BOTH the FROZEN and JOINT slots. Decisive question: does a
TRAINED fix lift REAL-absolute Hits@1 where the training-free fix could not, on the SAME diagnosed bias?

## Mechanism (3 training methods per slot)
- `CE_BASELINE` = `ref.fit_scorer_paired` / `ref.joint_train_score` VERBATIM (positive control = parent; Gate D).
- `MARGIN_HARDNEG` = additive margin `-m_add` on the true-class logit (CosFace/L-Softmax family) + hinge
  `max(0, m_hinge - (s_true - s_h))` with `h = argmax_{j!=y} score` re-mined every K steps (no ANN; V<=1000).
- `LOGIT_ADJUST_LOSS` = Menon 2021 TRAIN-TIME logit adjustment (add `tau_adj*log(pi_train)` to the softmax
  input during training; score with plain logits at test).
Applied to FROZEN (analytic gradient, torch bmm B=2) and JOINT (autograd B=2). Both arms mine independently
from their OWN checkpoint (paired-trials discipline).

## Fixed loss hyperparameters (LOCKED; calibrated to the MEASURED z-margin, NOT tuned-for-pass)
- `m_add = 1.0 * tau_slot` (one softmax-input unit); `m_hinge = 2.5 * tau_slot` (== MEASURED miss-row
  z-margin 2.2-2.7 std; `THEORETICAL@` dimensional-coherence self-test asserts 2.2 <= mult <= 2.7).
- `lambda_hinge = 1.0`; `tau_adj = 1.0` (Menon default); `mine_K = 25 (smoke) / 50 (full)`.
- `SLOT_TAU = {FROZEN: 0.05, JOINT: 0.1}` (inherited from parent).

## Bands (LOCKED; from CONTRACT + spec Section 3)
- **HARD_PASS**: best-of-{FROZEN,JOINT} x {MARGIN_HARDNEG, LOGIT_ADJUST_LOSS} with, in a SINGLE slot+method,
  REAL-absolute filtered Hits@1 lift over CE_BASELINE `>= 0.05` **AND** filtered MRR real_minus_shuf(inductive)
  `>= 0.15` **AND** SHUFFLED-abs Hits@1 lift over CE_BASELINE `<= +0.03` (SHUF_OVERFIT_GUARD), holding on
  `>=2 semantic relations x >=2 encoders at V>=300`.
- **HARD_FAIL**: max over semantic (rel x enc) at V>=300 of best guard-clean REAL Hits@1 lift `<= +0.02`
  (trained fix no better than CE_BASELINE everywhere) -> both post-hoc AND trained-margin have now failed on
  the same bias; residual is a fanout ceiling or a content-decorrelation problem.
- **MIDDLE_BAND**: partial (clears on one relation, or lift in (+0.02,+0.05)); or discriminator-vacuous.

`HP_HITS1_LIFT_MIN=0.05` is 2.5x the `HF=0.02` ceiling -> strictly-above-floor (META_RULE_L). Bands ordered
and below saturation (assert at import).

## SHUF_OVERFIT_GUARD (load-bearing anti-phantom, TRAINING-specific)
A TRAINED mechanism can overfit-game the SHUFFLED control (unlike a post-hoc rescore that never touches
params). Required: SHUFFLED-abs Hits@1 under the new loss must NOT rise `> +0.03` over CE_BASELINE SHUFFLED
at the same V/seed; a violation zeroes that unit's HP eligibility (`shuf_overfit_guard_violated` flag).
The REAL lift is credited only when guard-clean. (SMOKE evidence this fires: 1-seed V300 JOINT LOGIT SHUFFLED
lifted +0.05 -> flagged; averaged out under multi-seed.)

## Discriminator-fires controls (SCHEMA-VET; META_RULE_K)
- `synth_label_prior_hub` (POSITIVE, MUST FIRE): a severe train-only label-prior nuisance over a recoverable
  clean map (relabel 60% of TRAIN to head objects; test clean+balanced). best-of{MARGIN,LOGIT} REAL Hits@1
  lift `>= 0.05` while SHUFFLED lift `<= 0.03`. MEASURED off-disk: seed0 = **+0.068 via LOGIT_ADJUST**
  (max_shuf -0.003); mean(7,13,19) ~ +0.061. Fires via LOGIT_ADJUST (Menon's exact mechanism).
  **MARGIN is near-inert on the bilinear at convergence (~0)** -- a GENUINE measured property (full-batch GD
  reaches the max-likelihood W regardless of an additive margin), NOT a bug: MARGIN's gradient is proven by
  three finite-difference checks + a descent-direction check. MARGIN's real lever is the JOINT nonlinear slot.
- `synth_ambiguous_null` (NULL, MUST STAY CLEAN): labels independent of content; NEITHER fix may manufacture
  a test win. MEASURED off-disk: |lift| <= +0.013 both methods both arms (< 0.03 tol).

## SCHEMA-VET checklist
- `cardinality_ok`: EXPECTED_N_UNITS = sum_cfg (rels x encs) x (slots=2 x arms=2 x evals=2). smoke=32, full grid
  V{100,300,1000} x {AtLocation,CausesDesire,DerivedFrom} x {bge,gsbc}. Verdict emits CARDINALITY_BREACH if short
  (gsbc-cache-missing exempted). `cardinality_ok=True` smoke.
- `arms_differ_verified`: {CE,MARGIN,LOGIT} x {REAL,SHUF} 6 score matrices all differ (sha256). PASS.
- `final_metrics_atomicity`: tmp_replace.
- `except SystemExit: raise` before `except Exception` (no BaseException); start-marker + crash-diag + heartbeat.
- `crlb_n/a`: rank-lift transfer has no closed-form noise floor. Reachability: JOINT undertrained-rescore already
  MEASURED +0.467 REAL Hits@1 lift achievable (`data/exp_schema_relation_hubness_debias_rescore_v1_smoke`), so
  0.05 is reachable; 2.5x the HF ceiling.
- `baseline_in_band`: SHUFFLED filtered Hits@10 not saturated (< 0.95); CE_BASELINE reproduces parent (Gate D).
- `discriminator_survives_scale`: option B/C -- synth positive proves the instrument detects a >=0.05 removable
  bias; null proves no false win; the V>=300 real lift IS the map question (partial IS a finding).
- `calibration_check`: adaptive_with_discriminator_gate (m_add/m_hinge FIXED to the measured z-margin; synth
  fires + null clean are the proofs; NOT tuned on real data).
- `progress_logging`: print_flush_true (all progress flush=True; line-buffered stdout). timeout_s(full) ~1800-2400.
- `positive_control_arms` (Gate D): CE_BASELINE = parent scorer VERBATIM at test regime (tolerance 0 -- same code
  object); `ce_reproduces_parent` self-test asserts the function module.
- `composition_edges`: none (single scorer per slot; no primitive->primitive composition). `functional_requirements`:
  (1) lift rank-1 without degrading real signal -> margin/hinge + logit-adjust loss; (2) not game the popularity
  control -> SHUF_OVERFIT_GUARD.
- `HP_SCOPE`: HP gates apply to best-of-{FROZEN,JOINT} x {MARGIN,LOGIT} REAL/inductive/FILTERED SEMANTIC rel x enc
  at V>=300. CE_BASELINE=baseline(parent); SHUFFLED=guard; DerivedFrom=watchdog; raw=reported-not-gating.

## Compute architecture
Class (a) batched-GPU. FROZEN = analytic gradient torch bmm B=2 per (method x paired-arm); numpy fallback.
JOINT = autograd B=2. Storage: no_storage. No generative-LLM calls (deterministic bge/gsbc caches). Wall:
smoke ~18s/seed (measured); FULL ~15-25 min (3 seeds x full grid + synth controls). Discriminator = per-query
Hits@1 lift (continuous over judgments) -> MULTI-SEED SMOKE GATE applied (3 seeds smoke).

## SMOKE result (local, 3 seeds [7,13,19]; canonical smoke path)
See completion report / `data/exp_schema_relation_hardneg_mined_scorer_v1_smoke/metrics.json`.

## Dispatch
FULL routes to `remote_cpu_queue` (CPU cell; torch autograd small; ~15-25 min) via Orchestrator (exp_dev cannot
push). SMOKE local only (USER-LOCKED). Per-formula timeout: self-test < 180s; smoke ~60s; full timeout_s ~2400.
