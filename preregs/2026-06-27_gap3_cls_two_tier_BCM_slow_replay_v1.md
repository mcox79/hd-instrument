# PRE-REG: gap3_cls_two_tier_BCM_slow_replay_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `gap3_cls_two_tier_BCM_slow_replay_v1`
Source: research drill `notes/research_drill_stage3_compositional_cell_design_2026-06-27.md` CELL 1 (highest-priority Wave A)
Authorization: USER 2026-06-27 "overcome all of these" greenlight covering Wave A; 6-10 CPU-hr explicitly authorized
Wave: Wave A (parallel with `typed_multibank_K128_adversarial_v1`)

## Scientific question

Does adding a SLOW-LEARNING SECOND-TIER schema matrix `W_schema` with a
NON-LINEAR write rule (BCM sliding-threshold) on top of the substrate's
existing chain-grade NREM replay primitive produce category prototypes that
generalize to HELDOUT instances >= 0.65 accuracy at N=8192, with 5 categories
x 20 train + 10 heldout instances per category?

This is the brain-grounded CLS mechanism per McClelland 1995 / Kumaran-McClelland
2016 + Bienenstock-Cooper-Munro 1982 BCM rule. Composes on chain-grade NREM
replay (drift_reduction +0.57 proven-bound) + new W_schema + new BCM write.

## Mechanism class

TWO_TIER + non-linear slow-rate write. Mechanistically distinct from:
- cortex E-tensor (HARD_FAIL 3x; per-atom importance has magnitude coupling)
- Modern Hopfield prototype attractor v1 (MIDDLE_BAND 0.26; single-W
  non-linearity failed)
- chain-grade TWO_TIER generational W (HARD_PASS_PARTIAL on drift, NOT on
  compositional generalization — this cell adds BCM + replay to extract
  generalizable schema)

No magnitude-coupling (META_RULE_F): BCM rule is `dW = eta_slow * x * y * (y - theta_M)`
using output activity, NOT |W| signal.

## Config

- N_DIM = 8192 (full); N_DIM (smoke) = 2048
- N_CATEGORIES = 5; N_TRAIN_PER_CAT = 20; N_HELDOUT_PER_CAT = 10
- N_EPISODES = N_CATEGORIES * N_TRAIN_PER_CAT = 100 (full)
- N_REPLAY_CYCLES = 5000 (full); 500 (smoke)
- ETA_SLOW = 1e-3 (BCM slow-tier learning rate; brain-aligned)
- THETA_M_WINDOW = 200 (BCM sliding-threshold EWMA window)
- REPLAY_FRAC = 0.2 (chain-grade NREM replay default)
- REPLAY_EVERY = 100 (chain-grade NREM replay default)
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds; chain-grade-eligible)

## Arms (4 mandatory)

1. **ARM_BASELINE_SINGLE_W** — substrate's existing single-W with iterative
   cleanup; no second tier. Cross-cell rail: must replicate the Wave 1
   cortical_schema ARM_NO_SCHEMA ~0.37 within 0.05. Methodology-drift gate.
2. **ARM_TWO_TIER_HEBBIAN_SLOW** — vanilla Hebbian outer-product write into
   W_schema at eta_slow=1e-3 (NO BCM non-linearity). Tests: does the
   slow-rate ALONE (without BCM) do anything? RAIL — if this matches BCM, the
   lift is from eta_slow not from BCM; mechanism not as claimed.
3. **ARM_TWO_TIER_BCM_SLOW** — BCM sliding-threshold rule:
   `dW = eta_slow * x * y * (y - theta_M)`, `theta_M = EWMA(y^2, window=200)`.
   Full brain-aligned mechanism.
4. **ARM_TWO_TIER_BCM_GENERATIVE_REPLAY** — same BCM but replay samples
   GENERATIVE-RECONSTRUCTION from W_episodic (not literal episode IDs); tests
   Olafsdottir-McClelland generative-replay-helps-generalization claim.

## Metric

Primary endpoint per arm:
- `heldout_acc_mean` across 3 seeds (held-out instances classified by
  nearest-prototype in respective W)
- `heldout_acc_cv` across 3 seeds
- `w_schema_cone_cosine` (cone-preserving rail per Gap 2): mean cosine of
  W_schema rows to nearest W_episodic row direction; required in [0.5, 0.95]
  for HARD_PASS (cone-preserving means W_schema rotates within the substrate's
  cone, not into noise direction)
- `w_schema_eigenspectrum_entropy_delta`: change in eigenspectrum entropy
  from start to end of training; HARD_PASS requires DECREASE (compression
  happened)

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (chain-grade-eligible TWO_TIER BCM compositional schema):
- best `ARM_TWO_TIER_BCM_*.heldout_acc_mean >= 0.70` (floor 0.65 + 0.05 META_RULE_L band-width)
- AND best BCM arm >= `ARM_BASELINE_SINGLE_W.heldout_acc_mean + 0.18`
- AND best BCM arm >= `ARM_TWO_TIER_HEBBIAN_SLOW.heldout_acc_mean + 0.10`
  (BCM non-linearity actually contributes — distinct from vanilla Hebbian)
- AND `heldout_acc_cv <= 0.08` across 3 seeds
- AND `w_schema_cone_cosine in [0.5, 0.95]` (cone-preserving rail)
- AND `w_schema_eigenspectrum_entropy_delta < 0` (compression actually happened)
- AND `cardinality_ok`

**MIDDLE_BAND**:
- best BCM arm in [0.50, 0.70] AND > baseline by >= 0.10
- OR HARD_PASS arithmetic holds BUT cone-cosine outside [0.5, 0.95] or
  entropy-delta >= 0 (mechanism shows lift but in non-cone direction)

**HARD_FAIL**:
- all TWO_TIER arms within 0.05 of single-W baseline (mechanism null)
- OR `ARM_BASELINE_SINGLE_W.heldout_acc_mean >= 0.50` (methodology drift;
  cross-cell rail violated; abort and re-audit)
- OR `w_schema_cone_cosine < 0.3` (schema rotated off cone into noise direction)
- OR `cardinality_ok=False` (silent unit drop)

## Discriminator survives full-N (META_RULE_K — Option A + C)

Option A: smoke at N=8192 with 500 replay cycles (vs full 5000):
verify ARM_BASELINE replicates ~0.37 (cross-cell rail) AND BCM arm rises
MONOTONICALLY over training. If BCM arm doesn't move in 500 cycles at N=8192,
kill before full dispatch.

Option C (smoke includes full-N rail): smoke runs N_DIM=2048 with N=8192 baseline
single-unit cross-check (load `data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json` to verify the
~0.37 single-W baseline; abort if cross-cell rail not satisfied).

## By-construction-saturation check (Q-discipline)

If `w_schema` converges to identical-to-mean of class instances (reduces to
ARM_FEATURE_BASED_SCHEMA from Cell 1 cortical_schema), BCM is not doing
anything non-linear. Pre-reg requires log W_schema-eigenspectrum entropy at
end of training to be LOWER than at start (compression actually happened); if
entropy unchanged, MM auto-demote per META_RULE_K.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` AND halt the loop.

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Compute `cor(per_episode_heldout_score, |W_schema|_row_for_episode)`; if
`|cor| >= 0.5`, demote regardless of arithmetic.

## Formula self-tests (run at module import)

1. BCM rule arithmetic: small synthetic `(x, y, theta_M)` -> expected `dW` sign
2. NREM replay primitive composes correctly (chain-grade
   `replay_cycle(W, replay_indices, keys, values)` import works; calls match)
3. Verdict-machinery selftest: synthetic HP / HF / MB / cardinality breach cases
4. Cone-preserving cosine math sanity (orthonormal W_episodic -> cone-cosine ~1.0)
5. Eigenspectrum entropy delta sign on synthetic identity vs random matrices

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-bound BCM iteration; no GPU benefit at
  N_DIM=8192 with 5000 cycles)
- Estimated full wall: 6-10 hr (5000 replay cycles * 4 arms * 3 seeds)
- Per-experiment `--timeout`: 43200s (12 hr; 1.5x slack on 8-hr midpoint
  estimate; > 14400 = 4hr triggers PROT-021 checkpoint requirement)
- Must import `_seed_checkpoint` per PROT-021 (>= 14400s timeout)
- Smoke wall budget: ~300s (1 seed * 4 arms * 500 cycles at N_DIM=2048)

## Brain-grounding

STRONG. McClelland 1995, Kumaran-McClelland 2016 EXPLICITLY identify TWO_TIER
as the cortical-schema mechanism. BCM (Bienenstock-Cooper-Munro 1982) is
established experimentally in mouse visual cortex. NREM replay drift-reduction
is PROVEN-BOUND in our substrate. Composition of brain-existence-proof
primitives.

## P_deflated (lit-scan calibration)

P_deflated = 0.45 (raw lit P=0.65 minus 0.20 calibration penalty; highest
individual P of any Stage 3 candidate).

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=8192, 5 categories x 20 train + 10
heldout, ETA_SLOW=1e-3, BCM sliding-threshold with THETA_M_WINDOW=200,
N_REPLAY_CYCLES=5000, REPLAY_FRAC=0.2, REPLAY_EVERY=100, 3 seeds.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
