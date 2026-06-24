# Prereg: substrate_meta_lr_dopamine_analog_v1

Date: 2026-06-23
Filed-by: exp_dev
Script: experiments/exp_substrate_meta_lr_dopamine_analog_v1.py

## Hypothesis

Per-token RPE-modulated learning rate (phasic dopamine analog) produces measurable BPC
lift over fixed-LR cf-RPE baseline on text8 LM next-token prediction. This tests whether
the meta-learning gap (CLAIM 8 from brain-to-LM relevance audit) is closed by RPE-modulated
learning rate alone, without full MAML overhead.

Context: ARM_CFRPE_ONLY in heterogeneous_plasticity_v1 achieved BPC=7.1052 (vs Hebbian 7.3065;
+0.201 bits) using a FIXED learning rate (alpha=0.5). This cell extends to three arms:

- ARM_FIXED_LR: reproduces heterogeneous_plasticity ARM_CFRPE_ONLY baseline
- ARM_GLOBAL_RPE_LR: tonic dopamine analog (alpha modulated by EMA of RPE)
- ARM_PER_TOKEN_RPE_LR: phasic dopamine analog (alpha_t = base * (1 + beta * rpe_t_norm))

## Pre-registered HARD bands

(Pre-registered before smoke run per [[feedback-envelope-expansion-fail-bands]].)

HARD_PASS:
  ARM_PER_TOKEN_RPE_LR BPC lift >= +0.15 bits vs ARM_FIXED_LR
  AND ARM_PER_TOKEN_RPE_LR lift >= +0.05 bits vs ARM_GLOBAL_RPE_LR
  (phasic granularity matters AND outperforms tonic baseline)

MIDDLE_BAND:
  ARM_PER_TOKEN_RPE_LR lift vs ARM_FIXED_LR in [+0.05, +0.15) bits

HARD_FAIL:
  ARM_PER_TOKEN_RPE_LR lift within +/-0.05 bits of ARM_FIXED_LR
  (RPE-modulated LR not load-bearing at this scale)

CHAIN_GRADE_BONUS:
  lift >= +0.20 bits over ARM_FIXED_LR
  AND per_token_bpc <= (7.3065 - 0.30) = 6.7065
  (closes meta-learning gap decisively; beats fair_harness Hebbian by >=0.30)

cv < 0.05 across seeds mandatory for all verdict tiers.

## Middle-band outcome plan

MIDDLE_BAND result: meta-LR modulation helps but not decisively. Next step:
  - Check if per_token lift > global lift (phasic vs tonic discriminator).
  - If phasic > tonic: modulation granularity matters; try higher beta or
    per-arm T-grid tuning in a follow-up cell.
  - If phasic <= tonic: slow modulation is sufficient; global RPE tracking
    is the mechanistic lever, not per-token.
  Route finding to Strategy for CLAIM 8 re-assessment.

## N-suffix

No _nN suffix in anchor name. Production N_DIM = 8192. N_TRAIN = 100k.
Rationale: anchor name conveys mechanism (meta_lr_dopamine_analog) not scale;
scale matches prior chain-grade cell (heterogeneous_plasticity_v1 N_DIM=8192).

## Config

- N_DIM: 8192
- N_TRAIN: 100000
- N_HELD: 20000
- VOCAB_CAP: 4000
- SEEDS: [7, 17, 23]
- N_STEPS: 1000
- BASE_CFRPE_LR: 0.5
- META_LR_BETA: 1.0 (phasic scale; alpha_t = 0.5 * (1 + 1.0 * rpe_norm))
- META_LR_BETA_GLOBAL: 1.0 (tonic scale)
- SPARSE_BIPOLAR_F: 0.05
- Encoder: word2vec-google-news-300 -> Gaussian project to N_DIM -> sparse-bipolar

## Routing

Queue: overnight_queue (GPU required per Fix #22 rule 1: N_DIM=8192 matmul-bound)
Fix #24: torch.cuda + batched matmul; encoder hoisted outside arm loop; smoke verifies GPU

## Timeout estimate

Reference: heterogeneous_plasticity_v1 elapsed_s=496.86 (3 seeds, 4 arms, N_STEPS=1000).
This cell: 3 plasticity arms (vs 3 in prior cell for iterative arms; FIXED replaces Hebbian).
Estimated: similar profile to prior cell (~500s at production scale).

smoke_wall_s (smoke, N_DIM=512, N_TRAIN=2k, 1 seed): to be measured
FULL config: same N_DIM/N_TRAIN as prior chain-grade cell.
Formula: timeout_s = ceil(1.5 * 500 * 1.0 * 1.0) = 750s for single-seed baseline.
Scale to 3 seeds + 10% margin: 750 * 3 * 1.1 = 2475s.
Round up: timeout_s = 3600

Note: Prior cell ran 496s for 3 seeds. This cell has slightly different arm structure
(no STDP arm; one extra arm = ARM_GLOBAL_RPE_LR). Expected to be similar or slightly
faster. Setting timeout_s = 3600 (1h) as conservative estimate for overnight_queue.

PROT-019 check: anchor has no _n4096+ suffix; PROT-019 floor does NOT apply.
Setting timeout=3600 which is a reasonable conservative estimate.

## Dependency verification

- text8 corpus: data/text8_cache/text8.txt (required; same as prior cell which ran successfully)
- gensim word2vec: data/gensim_cache_v2/ (required; loaded by prior cell successfully)
- _seed_checkpoint.py: experiments/_seed_checkpoint.py (exists)
- tools/gensim_load_helper.py: required for encoder (used in prior cell; exists remotely)

All dependencies verified present on remote (marsh@home C:/dev/hd-instrument) via
prior cell successful run at same N_DIM/N_TRAIN/encoder config.

## Sources

- notes/exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md (Anchor 1)
- notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md (CLAIM 8)
- data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json
  (ARM_CFRPE_ONLY bpc=7.1052; ARM_HEBBIAN_ONLY bpc=7.3065; chain-grade prior)
- Lit: AWD-LSTM + meta-learner WikiText-2: 46.9 vs 64.8 perplexity (~28% reduction)
