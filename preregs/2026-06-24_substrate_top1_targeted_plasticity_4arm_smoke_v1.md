# Pre-reg: substrate_top1_targeted_plasticity_4arm_smoke_v1

**Date:** 2026-06-24
**Author:** exp_dev (per Research top1-targeted plasticity 2x drill 2026-06-24)
**Anchor:** `substrate_top1_targeted_plasticity_4arm_smoke_v1`
**Cell type:** CPU smoke / decisive discriminator (Research drill recommendation)
**Routing:** local_cpu_queue OR remote_cpu_queue (~30min wall expected)
**Reference drill:** `notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md`
**Reference empirical anchor (cf-RPE +12% top1 ceiling):**
  `notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md`

---

## HYPOTHESIS

The cf-RPE family's empirical +12% top1 lift ceiling vs unigram is RULE-TARGETING-LIMITED,
not substrate-W-limited. cf-RPE optimizes the MSE residual (BPC-targeted by construction);
top1 is dominated by the winner-runner-up logit gap, which MSE rules do not directly widen.
Four argmax-targeted plasticity rule families are lit-precedented as candidates to break
this ceiling: BCPNN (Ravichandran 2024), ARGMAX-DELTA (perceptron-class gated update),
LATERAL-INHIBIT (Foldiak anti-Hebbian; brain-canonical WTA), CHL (Movellan / O'Reilly).

## DESIGN — 5 arms, SAME readout

All arms use the SAME cosine-NN readout (logits[V] = cosine(W @ src_hd, codebook C)) and
the SAME word2vec-projected-to-sparse-bipolar encoder (matches fair_harness CERT591
chain-grade baseline). ONLY the plasticity rule on W differs.

| Arm | Plasticity rule | Targets |
|-----|-----------------|---------|
| ARM_CFRPE_REFERENCE | delta-rule MSE: dW = lr * (Nxt - Ctx @ W^T)^T @ Ctx / B | residual MSE |
| ARM_BCPNN | log-odds: W = log((W_co + eps) / (M_marg + eps)) via online EMA traces | conditional log-odds |
| ARM_ARGMAX_DELTA | gated margin: dW = lr * outer(C[tgt] - C[pred_argmax], src) when pred != tgt | top1 directly |
| ARM_LATERAL_INHIBIT | cf-RPE + anti-Hebbian runner-up: dW = cfrpe_dW - gamma*lr*outer(C[runner_up], src) | runner-up suppression |
| ARM_CHL | contrastive: dW = lr * (outer(C[tgt], src) - outer(W@src, src)) | free vs clamped phase diff |

## CONFIG (smoke-scale CPU-tractable per Research drill recommendation)

- `N_DIM = 2048`
- `VOCAB_CAP = 2000` (text8 V=2000 most-frequent words; "<unk>" reserved)
- `N_TRAIN = 20_000`, `N_HELD = 4_000` (drill recommendation)
- `SEEDS = [7, 17, 23]` (3 seeds; drill recommendation)
- `N_STEPS_PLASTIC = 5000` (matches cf-RPE adaptive baseline COARSE_N_STEPS for fair-by-construction
  comparison; gated rules run same step budget so total update budget is equalized)
- `INGEST_BATCH = 64`
- `SPARSE_BIPOLAR_F = 0.05` (matches fair_harness CERT591)
- `CFRPE_LR = 0.5` (matches cf-RPE COARSE reference)
- `BCPNN_EMA_ALPHA = 0.01` (matches Ravichandran 2024 trace half-life ~100 steps)
- `BCPNN_EPS = 1e-6` (numerical floor for log)
- `ARGMAX_MARGIN_THRESHOLD = 0.0` (pure argmax gate; rule fires only when pred != tgt)
- `LATERAL_INHIBIT_GAMMA = 0.5` (Foldiak-class anti-Hebbian; centered between drill PRED-3
  recommendation range [0.3, 1.0])
- `CHL_FREE_PHASE_SCALE = 1.0` (free-phase prediction direct from W@src, no nonlinearity)
- Corpus: text8 word stream
- Encoder: word2vec-google-news-300 projected via gaussian to N_DIM=2048, sparse-bipolar (f=0.05).
  Char-trigram fallback if gensim unavailable.

## PRE-REG HARD BANDS (locked BEFORE dispatch; per Research drill)

**PRIMARY METRIC: per-arm top1_acc absolute, computed identically across all arms.**

### Sanity gate (smoke + full)
- ARM_CFRPE_REFERENCE top1 within +/-0.03 of expected +12% lift over unigram baseline at smoke scale.
  (At V=2000 text8 / N=20k: unigram top1 expected ~0.21-0.23 from word2vec/sparse-bipolar fair_harness
  precedent; cf-RPE reference top1 expected ~0.23-0.25. Sanity gate: cfrpe_top1 - unigram_top1
  in [+0.03, +0.18] absolute.)
- If sanity FAILS -> verdict = SANITY_FAIL + diagnosis (provenance check broken; do NOT
  classify the rule-targeting question).

### HARD_PASS (rule-targeting cap BROKEN; escalate to N=8192 full dispatch)
- ANY non-cf-RPE arm: `top1_acc_mean(arm) - top1_acc_mean(ARM_CFRPE_REFERENCE) >= +0.05` absolute
- AND that arm's top1_acc cv across seeds <= 0.10
- AND Hebbian-baseline sanity computed correctly (not all-NaN)

### MIDDLE_BAND (weak signal; gated escalation)
- Best non-cf-RPE arm: lift in `[+0.02, +0.05)` absolute over cf-RPE reference
- OR HARD_PASS conditions met but cv in (0.10, 0.15]

### HARD_FAIL_DECISIVE (close plasticity-as-top1-lever hypothesis)
- ALL non-cf-RPE arms: `|top1_acc(arm) - top1_acc(ARM_CFRPE_REFERENCE)| <= 0.02`
- This is the substrate-product DECISIVE outcome per drill: top1 chain-grade lever IS readout,
  not plasticity. Route all top1 effort to readout axis (n1_v3 V_C sweep).

### HARD_FAIL_INSTABILITY
- Any arm crashes (all-seeds compute_failed) -> HARD_FAIL with diagnosis (not a science fail)
- Hebbian-baseline cv > 0.15 (sanity rail seed-unstable; methodology issue)

## SECONDARY METRICS REPORTED

- Per-arm BPC mean / cv / lift vs cf-RPE
- Per-arm MRR@10 mean / cv / lift vs cf-RPE
- Per-arm `effective_update_fraction` (load-bearing for ARM_ARGMAX_DELTA: must be in [0.10, 0.95])
- Per-arm wall time (compute budget audit)
- ARM_LATERAL_INHIBIT W-norm stability flag (anti-Hebbian destabilizes if gamma too high; report
  W.norm() final / W.norm() coarse-cfrpe-reference; flag if > 5x or < 0.2x)

## C7 / methodology hygiene

- LAMBDA_GRID excludes 0.0 (anti-calibration-collapse).
- ALL ARMS use SAME (T_grid, LAMBDA_grid) joint sweep -> dev/test split.
- ALL ARMS use SAME readout function (cosine-NN), SAME encoder build, SAME held set.
- Per-seed _seed_checkpoint resume.
- Fix #28: per-arm top1 PRIMARY (NOT BPC); per-arm metrics recomputable from per_seed
  partials; no cross-arm aggregation in verdict_msg without per-arm number visible.

## WHAT THIS DOES NOT SHOW

- Smoke scale (N=2048, N=20k); HARD_PASS triggers a FULL dispatch at N=8192 / N=100k,
  it does NOT itself produce a chain-grade-eligible substrate-product claim.
- Does not test composition with n1_v3 readout (PRED-4 of drill is a separate cell, fired
  only AFTER smoke HARD_PASS identifies the best plasticity arm).
- Does not exhaust the plasticity-rule-family space; 4 lit-precedented argmax-targeted
  families chosen per drill mechanism analysis. CHL/BCPNN variants (e.g., Krotov MHC) NOT tested.
- HARD_FAIL_DECISIVE is honest closure of the drill question at smoke; FULL-scale HARD_PASS
  remains theoretically possible if smoke-scale crosstalk hides a small lift, but the
  drill explicitly accepts smoke as decisive per drill section "Cheap decisive test".

## ROUTING DECISION

- local_cpu_queue: ~30min wall expected; numpy+torch CPU; SAME envs as cf-RPE adaptive
  reference (which ran 13min at production scale 8192-D).
- Authorized via Fix #14 (ONE cell), Fix #26 (predispatch_check PROCEED), Fix #28 (per-arm).

## TIMEOUT ESTIMATE

- smoke runtime extrapolation: 5 arms x 3 seeds x ~30s per arm-seed = ~7.5 min lower bound.
- Plasticity rules with extra per-step compute (BCPNN trace ops, ARGMAX_DELTA per-step argmax,
  LATERAL_INHIBIT per-step runner-up, CHL phase-diff) ~2-3x cf-RPE per step.
- Encoder build (word2vec V=2000) one-time per seed ~30-60s.
- Conservative timeout: 2400s (40 min). Drill says ~30 min; buffer 30%.

## TRIGGER ON LAND

- HARD_PASS -> route to Research for FULL-dispatch authorization (N=8192/N=100k) on the
  winning arm + design n1_v3 composition follow-up
- HARD_FAIL_DECISIVE -> route negative to Research (USER STANDING revival drill) +
  route to cap_map as "plasticity-as-top1-lever closed at smoke; readout dominates"
- MIDDLE_BAND -> route to Research for design-of-discriminator follow-up (drill says don't
  USER-arbitrate between MIDDLE_BANDs; build harder discriminator cell)

---

ASCII-only. Pre-reg trail committed BEFORE dispatch. No padding. Honest scope.
