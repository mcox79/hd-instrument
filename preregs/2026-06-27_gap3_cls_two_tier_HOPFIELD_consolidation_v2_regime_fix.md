# PRE-REG: gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix`
Source: research drill `notes/research_drill_hopfield_consolidation_by_construction_3x_2026-06-27.md`
Prior: `exp_gap3_cls_two_tier_HOPFIELD_consolidation_v1` HARD_FAIL methodology_drift (all 4 arms at 1.000; alpha=6e-4 sub-critical; regime trivially separable)
Authorization: USER 2026-06-27 NO LOCAL; remote_cpu_queue only; full-auto-authorized

## Scientific question

In the discriminating regime (alpha = P/N ~ 0.05, structured within-cat correlation via PROTOTYPE_NOISE=0.60, schema-formation instance count 100/cat), does `hdlab.continual.replay_cycle` (atom 588) as NREM-replay consolidation lift heldout categorization accuracy above fast-tier-Hebbian baseline by >= 0.10, IN A REGIME WHERE THE BASELINE IS PROVABLY BELOW CEILING (baseline in [0.20, 0.70])?

## Diagnosis of v1 failure (regime, not mechanism)

v1 cell shipped at N_DIM=8192, N_CAT=5, N_TRAIN=20 -> alpha = 5/8192 ~ 6e-4 = 230x sub-critical (AGS bound 0.138). At this load:
- crosstalk SNR ~ 40 (every associative rule trivially saturates by Amit-Gutfreund-Sompolinsky)
- within-cat overlap ~ 0.22, cross-cat overlap ~ 0.011 (random codebook in 8192-dim)
- Z-score ~ 19 -> ceiling territory for ANY classifier
- ALL 4 arms hit 1.000 -> ceiling-effect destroys discriminator -> rail HF_BASELINE_MAX=0.5 violated
- This is the textbook "Goodhart ceiling-effect" caught by the methodology_drift gate (correct trip)

The cell-author discipline that should have caught it pre-dispatch: alpha-in-[0.03, 0.20] regime check. v2 ADDS this as formula self-test #12 (META_RULE_W candidate).

## Mechanism class

IDENTICAL to v1. NO mechanism redesign. ONLY regime change:
- TWO_TIER + brain-grounded substrate-native slow rule
- Hopfield-style attractor consolidation via NREM replay
- Brain analog: sharp-wave-ripple replay during NREM consolidates HC traces into NC schemas (McClelland 1995 CLS; Whittington-Behrens 2024 Hopfield-family)

Composes on:
- `hdlab.continual.replay_cycle` (chain-grade atom 588; proven-bound +0.57 drift_reduction at REPLAY_EVERY=100, REPLAY_FRAC=0.2)

## Config (regime-fix per drill Section 2)

**Full (production):**
- N_DIM = 2048 (down from 8192)
- N_CATEGORIES = 100 (up from 5)
- N_TRAIN_PER_CAT = 100 (up from 20; schema-formation regime matches McClelland 1995)
- N_HELDOUT_PER_CAT = 30 (up from 10)
- N_REPLAY_CYCLES = 5000 (unchanged)
- PROTOTYPE_NOISE = 0.60 (up from 0.30; queries genuinely noisy, exercising attractor completion)
- ETA_FAST = 1.0; ETA_REPLAY = 1.0; REPLAY_FRAC = 0.2; REPLAY_EVERY = 100 (chain-grade defaults; unchanged)
- seeds: [11, 13, 19]
- **alpha = N_CAT/N_DIM = 100/2048 ~ 0.049** (in [0.03, 0.20] discriminating; PASS)
- **predicted SNR_Hebbian = 1/sqrt(alpha) ~ 4.52** (in [2.5, 6.0] discriminating SNR band; PASS)

**Smoke:**
- N_DIM = 1024, N_CATEGORIES = 50, N_TRAIN_PER_CAT = 30, N_HELDOUT_PER_CAT = 10
- N_REPLAY_CYCLES = 500, PROTOTYPE_NOISE = 0.60, seeds = [11]
- alpha = 50/1024 ~ 0.0488 (in discriminating band; PASS)
- predicted SNR ~ 4.53 (PASS)

## Arms (4 mandatory; IDENTICAL to v1)

1. **ARM_BASELINE_HEBBIAN** — mean-of-instances prototype rail
2. **ARM_HEBBIAN_SLOW** — fast-tier Hebbian only, NO replay (rail vs Hopfield arms)
3. **ARM_HOPFIELD_REPLAY_SLOW** — primary mechanism: fast-tier Hebbian + chain-grade NREM replay over STORED episodes
4. **ARM_HOPFIELD_GENERATIVE_REPLAY** — variant: replay samples are GENERATED prototype+noise patterns (brain DMN consolidation analog)

## Metric (per arm)

- `heldout_acc` (cosine to W_schema row; argmax over N_CAT rows)
- `w_schema_cone_cosine` (mean nearest-row cosine to W_episodic; required in [0.50, 0.95] for HARD_PASS)
- `w_schema_eigenspectrum_entropy_delta` (compression check)
- `cor_score` (per-class selectivity proxy)
- `n_replay_cycles_applied`
- `alpha_load` (recorded per unit for runtime sanity check vs pre-dispatch prediction)
- `snr_hebbian_predicted`
- `cardinality_ok`
- `baseline_in_discriminating_band` (NEW v2; baseline in [0.20, 0.70])

## Pre-registered bands (re-anchored to discriminating regime)

**HARD_PASS** (Hopfield consolidation chain-grade-eligible IN DISCRIMINATING REGIME):
- `ARM_HOPFIELD_REPLAY_SLOW.heldout_acc >= 0.65`
- AND `ARM_HOPFIELD_REPLAY_SLOW.heldout_acc - ARM_HEBBIAN_SLOW.heldout_acc >= 0.10`
- AND `ARM_BASELINE_HEBBIAN in [0.20, 0.70]` (discriminating-regime gate; NEW v2)
- AND `best_hopfield_arm.cor_score >= 0.30`
- AND `ARM_HOPFIELD_REPLAY_SLOW.cv <= 0.10` across 3 seeds
- AND `w_schema_cone_cosine in [0.50, 0.95]`
- AND `cardinality_ok`

**MIDDLE_BAND**:
- `best_hopfield_arm.heldout_acc >= 0.50` AND `lift_over_baseline >= 0.05`
- OR HARD_PASS arithmetic holds but baseline outside [0.20, 0.70]

**HARD_FAIL**:
- `ARM_BASELINE_HEBBIAN >= 0.75` (ceiling-effect; SAME trip class as v1 but raised threshold from 0.50; v1 hit 1.000)
- OR `ARM_BASELINE_HEBBIAN < 0.20` (floor-effect; NEW v2; regime too hard)
- OR all consolidation arms within 0.03 of baseline (mechanism null; tightened from 0.05)
- OR `w_schema_cone_cosine < 0.30`
- OR `cardinality_ok=False`
- OR `alpha_actual not in [0.03, 0.20]` at runtime (META_RULE_W check)

## Discriminator survives full-N (META_RULE_K)

- Smoke at N_DIM=1024, N_CAT=50, N_TRAIN=30, single seed: predicted baseline ~ 0.45-0.55, Hopfield_replay ~ 0.55-0.70 if mechanism works. Both well clear of saturation.
- Full at N_DIM=2048, N_CAT=100: same alpha ~ 0.049; baseline predicted in same band (alpha is the load-axis; baseline depends on alpha not raw N).
- If smoke baseline outside [0.20, 0.70] -> reject; raise N_CAT to 200 or lower N_DIM to 512 and re-smoke. NO dispatch until smoke baseline in band.

## NEW META_RULE_W (alpha-in-[0.03, 0.20] regime gate; drill synthesis)

**Pre-dispatch HARD gate at module import (formula self-test #12 + #13):**
1. Compute `alpha = N_CAT / N_DIM` for current run mode; assert in [0.03, 0.20]
2. Compute predicted `SNR_Hebbian = 1/sqrt(alpha)`; assert in [2.5, 6.0]
3. ANY failure -> module import HARD_FAIL (no compute spent)

**Drill recommendation:** META_RULE_W should apply to ALL associative-memory cells going forward (Hebbian, Hopfield, modern-Hopfield, BCM, attractor, replay, schema-extraction). Cells in sub-critical regime (alpha < 0.03) trivially saturate; cells in super-critical (alpha > 0.20) collapse below Hebbian. Discrimination only happens in the middle band.

## By-construction-saturation check (Q-discipline)

If `ARM_HEBBIAN_SLOW` and `ARM_HOPFIELD_REPLAY_SLOW` give identical heldout_acc, replay added nothing -> HP_LIFT_OVER_HEBBIAN gate (>=0.10) catches this -> demote to MIDDLE_BAND or HARD_FAIL.

If both Hopfield arms saturate at baseline, mechanism_null HARD_FAIL fires.

NEW v2: baseline saturation at >= 0.75 explicitly named ceiling-effect; baseline collapse < 0.20 explicitly named floor-effect.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full); 1 * 4 = 4 (smoke)
- `cardinality_ok` MANDATORY in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` AND halt the loop (`raise`).

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Replay rule uses `v_sub.T @ k_sub` (outer-sum). cor_score selectivity gate exposes magnitude-coupling indirectly.

## Formula self-tests (run at module import; 11 from v1 + 2 NEW v2 + 1 sub-test)

1. Chain-grade replay_cycle composes correctly
2. One-hot keys escape W=0
3. Verdict HARD_PASS synthetic path (regime-fix bands)
4. Methodology drift CEILING (baseline >= 0.75 -> HARD_FAIL)
4b. Methodology drift FLOOR (baseline < 0.20 -> HARD_FAIL) — NEW v2
5. Cardinality breach
6. Mechanism null
7. Cone violation
8. MIDDLE_BAND partial
9. Cone-preserving cosine sanity
10. Eigenspectrum entropy direction
11. Envelope constants LOCKED
12. **META_RULE_W alpha-in-[0.03, 0.20] regime gate — NEW v2**
13. **Predicted SNR_Hebbian in [2.5, 6.0] — NEW v2**

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-bound; matrix ops at N=2048 with N_CAT=100 modest)
- Smoke wall budget: ~300s (1 seed * 4 arms * 500 cycles at N=1024, N_CAT=50, N_TRAIN=30)
- Full wall estimate: 3-6 hr (5000 cycles * 4 arms * 3 seeds at N=2048, N_CAT=100, N_TRAIN=100; N_EPISODES=10000 per arm; 50 replay events at M=10000 each)
- Per-experiment `--timeout`: **21600s** (6 hr; > 14400 triggers PROT-021 -> _seed_checkpoint required, already imported)

## USER NO LOCAL (2026-06-27)

Smoke + full both on `remote_cpu_queue`. Smoke variant name: `<anchor>_smoke`.

## Brain-grounding

STRONG. v2 enters the brain's actual operating regime (v1 was 1000x below):
- CA3 attractor at alpha ~ 0.02-0.10 (Treves-Rolls); v2 cell at alpha ~ 0.049 (IN-REGIME)
- McClelland 1995 CLS: cortical schema requires 50-200 instances per category; v2 at 100 (IN-REGIME)
- Tse-Morris 2007: schema formation regime; v2 N_TRAIN sufficient
- Whittington-Behrens 2024: modern Hopfield consolidation in attractor regime, not sub-critical regime

## P_deflated (lit-scan calibration)

P = **0.45** (deflated from P_raw=0.65 by 0.20 for lit-scan calibration penalty + substrate-specific composition risk; under novel-synthesis cap of 0.50).

Main residual risk: even in discriminating regime, replay-over-stored-episodes may add no NEW information vs single-pass Hebbian outer product (Hebbian prototype = mean of instances = what replay re-applies). This would land MIDDLE_BAND not HARD_FAIL.

DIRECTIONALITY (alpha is the right axis; v2 in correct regime) HIGH confidence — 4+ literature anchors converge (AGS 1987, Treves-Rolls, Hu 2024, Brenndoerfer 2025).

MAGNITUDE (substrate-specific lift >= 0.10 at alpha ~ 0.05) is the deflation locus.

## Honest scope

HARD_PASS claim bounded to: N_DIM=2048, N_CAT=100, N_TRAIN=100, N_HELDOUT=30, WITHIN_CAT_CORR via PROTOTYPE_NOISE=0.60, alpha ~ 0.049, 3 seeds. Does NOT claim mechanism scales to arbitrary alpha or to adversarial within-category structure; those are separate cells.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
