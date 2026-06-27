# PRE-REG: gap3_cls_two_tier_BCM_v2_init_fix

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `gap3_cls_two_tier_BCM_v2_init_fix`
Source: research drill `notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md` STUB 1 (Path A primary rescue)
Prior: `exp_gap3_cls_two_tier_BCM_slow_replay_v1` HARD_FAIL at chance (0.20 = 1/N_CAT); zero-init W + zero-init theta = degenerate fixed point dW=0 forever (every cycle, every seed; verified algebraically by Research code-read forensics)
Authorization: USER 2026-06-27 NO LOCAL SMOKE; remote_cpu_queue only

## Scientific question

Does BCM (Bienenstock-Cooper-Munro 1982) actually operate as a slow-learning rule in the substrate WHEN PROPERLY INITIALIZED (non-zero W variance + warm theta + Hebbian pre-tuning warmup), as the brain operates BCM on pre-tuned cortical substrate (not from scratch)?

Specifically: at N=8192, 5 categories x 20 train + 10 heldout, does the v2 fix produce held-out classification accuracy >= 0.65 AND emergent selectivity (cor_score >= 0.30), beating the v1 degenerate-fixed-point trap?

## Mechanism class

TWO_TIER + non-linear slow-rate write + brain-grounded initialization. Three load-bearing fixes vs v1:

1. **W_schema init: `torch.empty(...).normal_(mean=0, std=0.01)`** — non-zero VARIANCE (Bio-protocol Scholarpedia BCM: "weights init randomly between 0.10 and 0.12"; Yger-Harris 2022 "BCM has multiple fixed points; init must break symmetry").
2. **theta_M init: `torch.full(..., 0.5)`** — warm threshold; BN-analog symmetry breaking. (y - theta) factor has non-trivial sign on first cycle even if W has tiny perturbation.
3. **500-cycle Hebbian warmup phase BEFORE BCM phase begins** — cortical-pre-tuning analog; brain runs BCM on pre-existing connectivity from thalamic input + spontaneous activity, NOT on tabula rasa. eta_warm=1e-2 (10x eta_slow) for faster coarse tuning, then 4500 cycles of BCM with eta_slow=1e-3 for selectivity refinement.

No magnitude-coupling (META_RULE_F): BCM rule is `dW = eta_slow * x * y * (y - theta_M)` using output activity, NOT |W|.

## Config

- N_DIM = 8192 (full); N_DIM (smoke) = 2048
- N_CATEGORIES = 5; N_TRAIN_PER_CAT = 20; N_HELDOUT_PER_CAT = 10
- N_REPLAY_CYCLES = 5000 (full; 500 warmup + 4500 BCM for FULL arm); 500 (smoke; 100 warmup + 400 BCM)
- ETA_SLOW = 1e-3 (BCM); ETA_WARM = 1e-2 (Hebbian warmup)
- THETA_M_WINDOW = 200 (EWMA)
- W_INIT_STD = 0.01 (v2 fix; non-zero variance)
- THETA_INIT = 0.5 (v2 fix; warm threshold)
- N_WARMUP_CYCLES = 500 (v2 fix; cortical pre-tuning analog)
- REPLAY_FRAC = 0.2
- PROTOTYPE_NOISE = 0.30
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds; chain-grade-eligible)

## Arms (4 mandatory)

1. **ARM_BASELINE_SINGLE_W** — mean-of-instances prototype (rail; ~0.37; methodology-drift gate at <0.50).
2. **ARM_BCM_V2_INIT_ONLY** — random non-zero init only (theta=0, no Hebbian warmup). Ablation: tests whether init alone breaks the degenerate trap.
3. **ARM_BCM_V2_WARMUP_ONLY** — zero init + Hebbian warmup (no theta init). Ablation: tests whether warmup alone suffices.
4. **ARM_BCM_V2_FULL** — all three fixes combined. Primary mechanism.

## Metric

Per arm:
- `heldout_acc` (cosine to W_schema row; argmax over rows)
- `w_schema_cone_cosine` (mean cosine of W_schema rows to nearest W_episodic row; required in [0.50, 0.95] for HARD_PASS)
- `w_schema_eigenspectrum_entropy_delta` (compression check; informational)
- `cor_score` (per-class accuracy correlated with assigned-row alignment; selectivity emergence proxy)
- `max_abs_y_first_200` (BCM trace; v2 must escape v1's y=0 trap)

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (BCM v2 init-fix rescue works):
- `ARM_BCM_V2_FULL.heldout_acc >= 0.65` (above HP_BASELINE_MAX=0.50)
- AND `ARM_BCM_V2_FULL` lift over `ARM_BASELINE_SINGLE_W` >= 0.15
- AND `ARM_BCM_V2_FULL.cor_score >= 0.30` (selectivity emerges)
- AND `ARM_BCM_V2_FULL.cv <= 0.10` across 3 seeds
- AND `w_schema_cone_cosine in [0.50, 0.95]`
- AND `max_abs_y_first_200 >= 0.01` (y-degeneracy escaped)
- AND `cardinality_ok`

**MIDDLE_BAND**:
- `ARM_BCM_V2_FULL.heldout_acc in [0.50, 0.65]` AND lift over baseline >= 0.10
- OR HARD_PASS arithmetic holds BUT cone-cosine outside band

**HARD_FAIL**:
- `max_abs_y_first_200 < 0.01` (v2 init+theta+warmup did NOT escape v1's degenerate trap; verdict surfaces "BCM_DEGENERATE_FIXED_POINT")
- OR all BCM v2 arms within 0.05 of baseline (mechanism null)
- OR `ARM_BASELINE_SINGLE_W >= 0.50` (methodology drift; rail violated)
- OR `w_schema_cone_cosine < 0.30` (schema rotated off cone)
- OR `cardinality_ok=False` (silent unit drop)

## Discriminator survives full-N (META_RULE_K — Option A)

**Smoke must FIRE the discriminator, not just verify cell runs.** Cell raises `RuntimeError(SMOKE_DISCRIMINATOR_FAILED)` if smoke `ARM_BCM_V2_FULL.max_abs_y_first_200 < 0.01` — halts before full dispatch. This is the v1-trap detector: if v2 init+theta+warmup STILL leaves y=0 throughout the first 200 BCM cycles, the rescue did not work and full dispatch is futile.

Smoke at N_DIM=2048 with 500 cycles total (100 warmup + 400 BCM) preserves the same algebraic dynamics as N=8192 (W_INIT_STD=0.01 → y ~ 0.01 * sqrt(2048) ~ 0.45 expected magnitude; well above 0.01 threshold).

## By-construction-saturation check (Q-discipline)

ARM_BCM_V2_FULL must show NON-TRIVIAL contribution beyond ARM_BCM_V2_INIT_ONLY (HP requires combined fix >= init-only ablation by some margin; current bands tolerate this implicitly via overall floor + selectivity gate).

If FULL == INIT_ONLY exactly, the warmup phase contributed nothing — interesting partial result but does not invalidate HP.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` AND halt the loop (`raise`).

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

BCM rule uses post-synaptic activity y, not |W|, so the rule itself is structurally clean. We additionally surface `cor_score` (selectivity) which would expose magnitude-coupling indirectly (if per-class acc correlates with row magnitude not with row direction, cone_cosine + cor_score both decline).

## Formula self-tests (run at module import; assert measured == expected BEFORE dispatch)

1. **v1 zero-init reproduces W=0, theta=0, y=0 trap** (regression sanity that the degenerate path still exists)
2. **v2 non-zero init breaks the trap** (y != 0 after one BCM step with W~N(0, 0.01))
3. **BCM rule arithmetic correctness** (W_new = W + eta * x * y * (y - theta_M); same formula as v1)
4. **Hebbian warmup step** (W_after = W + eta_warm * x; pure additive)
5. **Verdict-machinery HARD_PASS synthetic path** (12-unit synthetic perfect input)
6. **Verdict catches degenerate fixed point** (max_abs_y_first_200=0 + acc=0.20 -> HARD_FAIL with BCM_DEGENERATE_FIXED_POINT msg)
7. **Methodology drift** (baseline >= 0.50 -> HARD_FAIL)
8. **Cardinality breach** (<EXPECTED_N -> HARD_FAIL)
9. **MIDDLE_BAND** (partial rescue path)
10. **Envelope constants LOCKED** (assert each band value)

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-bound BCM iteration; same as v1)
- Smoke wall budget: ~300s (1 seed * 4 arms * 500 cycles at N_DIM=2048)
- Full wall estimate: 6-10 hr (5000 cycles * 4 arms * 3 seeds at N_DIM=8192)
- Per-experiment `--timeout`: 43200s (12 hr; 1.5x slack on 8-hr midpoint; > 14400 triggers PROT-021)
- Must import `_seed_checkpoint` (done) per PROT-021

## USER NO LOCAL SMOKE (2026-06-27)

Smoke runs on `remote_cpu_queue` (NOT laptop). Smoke variant name: `<anchor>_smoke`. Same anchor file invoked with `--smoke` flag OR via `HDLAB_EXP_NAME=<anchor>_smoke` env var (cell honors both per harness convention).

## Brain-grounding

STRONG.
- Scholarpedia BCM: "weights init randomly (normal distribution with zero MEAN but non-zero VARIANCE)"
- Yger-Harris 2022 J Comput Neurosci: "BCM has multiple fixed points; init must break symmetry"
- Cooper-Bear 2010 review: BCM successful in cat V1 receptive field formation (in vivo)
- Brain runs BCM on PRE-TUNED substrate (thalamic input + spontaneous activity establishes coarse tuning before BCM-style refinement). v2's Hebbian warmup phase is the substrate analog of cortical pre-tuning.

## P_deflated (lit-scan calibration)

P = 0.50 (raw lit P=0.65 minus 0.15 novel-synthesis calibration penalty; per drill).

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=8192, 5 categories x 20 train + 10 heldout, ETA_SLOW=1e-3, ETA_WARM=1e-2, BCM sliding-threshold with THETA_M_WINDOW=200, W_INIT_STD=0.01, THETA_INIT=0.5, N_WARMUP_CYCLES=500, N_REPLAY_CYCLES=5000, 3 seeds, REPLAY_FRAC=0.2.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
