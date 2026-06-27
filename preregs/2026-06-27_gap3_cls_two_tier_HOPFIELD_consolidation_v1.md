# PRE-REG: gap3_cls_two_tier_HOPFIELD_consolidation_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `gap3_cls_two_tier_HOPFIELD_consolidation_v1`
Source: research drill `notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md` STUB 3 (Path C lowest dev cost; substrate-native fallback)
Prior: `exp_gap3_cls_two_tier_BCM_slow_replay_v1` HARD_FAIL at chance (BCM degenerate trap)
Authorization: USER 2026-06-27 NO LOCAL SMOKE; remote_cpu_queue only

## Scientific question

Does the substrate-native chain-grade NREM replay primitive (atom 588; `hdlab.continual.replay_cycle` with proven-bound drift_reduction +0.57) serve as a SLOW-LEARNING consolidation rule that lifts schema generalization above the fast-tier Hebbian baseline?

Specifically: at N=8192, 5 categories x 20 train + 10 heldout, does adding NREM replay over stored episodes (or generated prototype+noise patterns) produce held-out classification accuracy >= 0.65, beating Hebbian-fast-tier-only baseline by >= 0.10, with cor_score >= 0.30 (selectivity emerges)?

## Mechanism class

TWO_TIER + brain-grounded substrate-native slow rule. Drops BCM entirely (BCM's multiplicative-y degeneracy is the v1 failure root cause); uses Hopfield-style attractor consolidation via NREM replay. Brain analog: sharp-wave-ripple replay during NREM sleep consolidates HC traces into NC schemas (McClelland 1995 CLS; Whittington-Behrens 2024 Hopfield-family).

Composes on:
- `hdlab.continual.replay_cycle` (chain-grade atom 588; proven-bound +0.57 drift_reduction at REPLAY_EVERY=100, REPLAY_FRAC=0.2)

NO multiplicative-y plasticity -> NO degenerate fixed point. Even from W=0 with one-hot keys, `replay_cycle` produces non-zero delta (`v_sub.T @ k_sub` is well-defined). Verified in formula T2.

## Config

- N_DIM = 8192 (full); N_DIM (smoke) = 2048
- N_CATEGORIES = 5; N_TRAIN_PER_CAT = 20; N_HELDOUT_PER_CAT = 10
- N_REPLAY_CYCLES = 5000 (full); 500 (smoke)
- ETA_FAST = 1.0 (Hebbian fast-tier write rate)
- ETA_REPLAY = 1.0 (NREM replay re-Hebb lr; matches chain-grade primitive default)
- REPLAY_FRAC = 0.2 (chain-grade default; proven-bound)
- REPLAY_EVERY = 100 (chain-grade default; proven-bound)
- PROTOTYPE_NOISE = 0.30
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds; chain-grade-eligible)

## Arms (4 mandatory)

1. **ARM_BASELINE_HEBBIAN** — mean-of-instances prototype (rail; ~0.37; HP_BASELINE_MAX <= 0.50; methodology-drift gate). Matches v1 ARM_BASELINE_SINGLE_W exactly for cross-cell rail.
2. **ARM_HEBBIAN_SLOW** — fast-tier Hebbian write only, NO replay. Rail vs Hopfield replay arms (tests whether replay specifically contributes).
3. **ARM_HOPFIELD_REPLAY_SLOW** — primary mechanism: fast-tier Hebbian + chain-grade NREM replay over STORED episodes every REPLAY_EVERY=100 cycles.
4. **ARM_HOPFIELD_GENERATIVE_REPLAY** — variant: same as #3 but replay samples are GENERATED prototype+noise patterns (brain DMN consolidation analog; Olafsdottir-McClelland).

## Metric

Per arm:
- `heldout_acc` (cosine to W_schema row; argmax over rows)
- `w_schema_cone_cosine` (mean cosine of W_schema rows to nearest W_episodic row; required in [0.50, 0.95] for HARD_PASS)
- `w_schema_eigenspectrum_entropy_delta` (compression check; informational)
- `cor_score` (per-class accuracy correlated with assigned-row alignment; selectivity proxy)
- `n_replay_cycles_applied` (count of replay events; sanity check that REPLAY_EVERY gate fired)

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (Hopfield consolidation chain-grade-eligible substrate-native slow rule):
- `ARM_HOPFIELD_REPLAY_SLOW.heldout_acc >= 0.65`
- AND `ARM_HOPFIELD_REPLAY_SLOW.heldout_acc - ARM_HEBBIAN_SLOW.heldout_acc >= 0.10` (replay specifically contributes beyond fast-tier alone)
- AND `best_hopfield_arm.cor_score >= 0.30` (selectivity emerges)
- AND `ARM_HOPFIELD_REPLAY_SLOW.cv <= 0.10` across 3 seeds
- AND `w_schema_cone_cosine in [0.50, 0.95]` (cone-preserving)
- AND `cardinality_ok`

**MIDDLE_BAND**:
- `best_hopfield_arm.heldout_acc in [0.50, 0.65]` AND lift over baseline >= 0.10
- OR HARD_PASS arithmetic holds BUT cone-cosine outside band

**HARD_FAIL**:
- all consolidation arms (HEBBIAN_SLOW + 2 HOPFIELD arms) within 0.05 of baseline (mechanism null)
- OR `ARM_BASELINE_HEBBIAN >= 0.50` (methodology drift; rail violated)
- OR `w_schema_cone_cosine < 0.30` (schema rotated off cone)
- OR `cardinality_ok=False` (silent unit drop)

## Discriminator survives full-N (META_RULE_K)

NREM replay primitive is chain-grade at N=4096; well-characterized at N=8192. Smoke at N=2048 with 500 replay cycles produces (500 / REPLAY_EVERY=100) = 5 replay applications; full at N=8192 with 5000 cycles produces 50 applications — 10x more updates at 4x N. Discriminator (lift over Hebbian by >=0.10) is at-scale-defensible: brain-grounded replay consolidation effect grows with replay count.

No multiplicative-y trap to detect; the cell's risk is "replay doesn't add anything beyond fast-tier Hebbian" which is a band-rejection HARD_FAIL via mechanism_null path, NOT a numerical degeneracy.

## By-construction-saturation check (Q-discipline)

If `ARM_HEBBIAN_SLOW` and `ARM_HOPFIELD_REPLAY_SLOW` give identical heldout_acc, replay added nothing — HP_LIFT_OVER_HEBBIAN gate (>=0.10) catches this. Demotes to MIDDLE_BAND or HARD_FAIL depending on absolute level.

If both Hopfield arms saturate at the same value as ARM_BASELINE_HEBBIAN, mechanism_null HARD_FAIL fires.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` AND halt the loop (`raise`).

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Replay rule uses `v_sub.T @ k_sub` (outer-sum), not |W|. cor_score selectivity gate exposes magnitude-coupling indirectly (per-class acc tracks alignment not magnitude).

## Formula self-tests (run at module import)

1. **Chain-grade replay_cycle composes correctly** — `replay_cycle(W=0, eye-keys, eye-values, replay_frac=1.0)` produces expected outer-sum on diagonal.
2. **One-hot keys escape W=0** — demonstrates NO BCM-style degeneracy; verifies the substrate-native rule sidesteps v1's trap.
3. **Verdict-machinery HARD_PASS synthetic path** (12-unit synthetic perfect input).
4. **Methodology drift** (baseline >= 0.50 -> HARD_FAIL).
5. **Cardinality breach** (<EXPECTED_N -> HARD_FAIL).
6. **Mechanism null** (all arms at baseline -> HARD_FAIL).
7. **Cone violation** (cone < 0.30 -> HARD_FAIL).
8. **MIDDLE_BAND** (partial consolidation path).
9. **Cone-preserving cosine math sanity** (identity W -> ~1.0).
10. **Eigenspectrum entropy direction** (low-rank < random).
11. **Envelope constants LOCKED** (assert each band value).

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-bound; matrix ops at N=8192 modest; ~50 replay events vs 5000 BCM steps = much lighter than v1)
- Smoke wall budget: ~200s (1 seed * 4 arms * 500 cycles at N_DIM=2048; 5 replay events per Hopfield arm)
- Full wall estimate: 2-4 hr (5000 cycles * 4 arms * 3 seeds at N_DIM=8192; 50 replay events per Hopfield arm)
- Per-experiment `--timeout`: 21600s (6 hr; 1.5x slack on 4-hr upper estimate; > 14400 triggers PROT-021)
- Must import `_seed_checkpoint` (done) per PROT-021

## USER NO LOCAL SMOKE (2026-06-27)

Smoke runs on `remote_cpu_queue`. Smoke variant name: `<anchor>_smoke`.

## Brain-grounding

STRONG.
- McClelland 1995 CLS — HC fast-tier + NC slow-tier with replay-mediated consolidation
- Kumaran-McClelland 2016 review — generative replay as cortical schema extraction mechanism
- Whittington-Behrens 2024 family — modern Hopfield as substrate for memory consolidation
- Olafsdottir-McClelland — generative replay (synthesized patterns) drives generalization

Composes on PROVEN-BOUND substrate primitive (atom 588; +0.57 drift_reduction at chain-grade bar). Lowest implementation risk per drill.

## P_deflated (lit-scan calibration)

P = 0.60 (per drill; substrate-native primitive already cert-graded; main uncertainty is "does it lift CATEGORICAL GENERALIZATION not just trace drift").

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=8192, 5 categories x 20 train + 10 heldout, ETA_FAST=1.0, ETA_REPLAY=1.0, REPLAY_FRAC=0.2, REPLAY_EVERY=100, N_REPLAY_CYCLES=5000, 3 seeds, PROTOTYPE_NOISE=0.30.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
