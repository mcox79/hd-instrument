# PRE-REG: typed_multibank_K128_adversarial_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `typed_multibank_K128_adversarial_v1`
Source: research drill `notes/research_drill_stage3_compositional_cell_design_2026-06-27.md` CELL 4
Authorization: USER 2026-06-27 "overcome all of these" greenlight covering Wave A
Wave: Wave A (parallel with `gap3_cls_two_tier_BCM_slow_replay_v1`; FIRST to dispatch — cheapest; produces ARM_PRESCRIBED_SLOTS rail for Wave B CELL 2)

## Scientific question

Does adding an explicit per-bank TYPE LABEL on top of the chain-grade multibank
WM K=4096 / k_per_bank=64 primitive (1) LIFT recall above the typeless baseline
at NON-SATURATED operating point AND (2) drive REFUSE rate on type-mismatched
queries to >= 0.85? Critical RESPEC from Wave 2 Anchor 2 audit: must operate
OUTSIDE the by-construction-saturation regime documented in
`hdlab/working_memory.py` (k_per_bank >= 64 at adversarial OVERLAP=0.40, not
the baseline 0.20).

## Mechanism class

Type-routed multibank WM. Composes on chain-grade primitives:
- chain-grade multibank K=4096 / MULTI_64x / k_per_bank=64 (cell-land 2026-06-26
  commit 6e2ff698; HARD_PASS chain-grade per Skunkworks landed-VET; ledger row
  62ce9e7dca071828)
- chain-grade intent classifier n=100 (`exp_a1_substrate_intent_classifier_v1`)
- chain-grade refuse-gate V_REL=256

No magnitude-coupling (META_RULE_F): type labels are EXTERNAL routing tokens,
not per-atom |W| signals.

## Config

- N_DIM = 8192
- N_DIM (smoke) = 2048
- K_TOTAL = 8192, n_banks = 128, k_per_bank = 64 (RESPEC: above
  K_TOTAL_CHAIN_GRADE_ENVELOPE = 4096 so the cell-author smoke gate is the
  load-bearing regime check; assert_k_per_bank_in_discriminating_regime passes
  because k_per_bank = 64 and OVERLAP = 0.40 > 0.20 threshold)
- FEATURE_OVERLAP_FRAC = 0.40 (ADVERSARIAL; raised from chain-grade 0.20 to push
  baseline OUT OF saturation regime; verified at smoke that ARM_UNTYPED_BASELINE
  lands in [0.60, 0.85])
- CUE_COS = 0.70
- SIGMA = 1.0
- N_TYPES = 64 (matches n_banks; one type per bank slot)
- N_ITEMS_PER_K = 200
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds; chain-grade-eligible)
- REGIME_LABEL = "ADVERSARIAL_OVERLAP_040"

## Arms (3 mandatory)

1. **ARM_UNTYPED_BASELINE_ADVERSARIAL** — chain-grade multibank at K=8192,
   n_banks=128, OVERLAP=0.40 with NO type labels (vanilla
   `eval_multi_bank_arm` from chain-grade primitive). Sanity rail: must land in
   [0.60, 0.85] (NOT saturated). If <= 0.60, baseline broken; if >= 0.85,
   regime by-construction-saturated and cell vacuous.
2. **ARM_TYPED_ROUTING_MATCHED** — per-bank type label assigned matching the
   ground-truth content bank; query carries type label; routing-by-type
   (compare cue.type to each bank.type tag); cleanup within the routed bank
   only. Tests typed-routing LIFT over untyped at the non-saturated regime.
3. **ARM_TYPED_ROUTING_ADVERSARIAL_PROBE** — deliberately ill-typed queries
   (type label mismatches content bank by uniform-random shuffle); tests
   refuse-rate when the refuse-gate (V_REL=256) detects type-mismatch via
   bank-cosine-below-threshold + type-tag-conflict.

## Metric

- `recall_mean`, `recall_cv` per arm across 3 seeds
- `route_acc_mean` per arm
- `refuse_rate` (ARM_TYPED_ROUTING_ADVERSARIAL_PROBE only): fraction of
  ill-typed queries the system declines vs answers wrongly
- `arm_baseline_in_band` (ARM_UNTYPED_BASELINE_ADVERSARIAL): bool, baseline in
  [0.60, 0.85]

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (chain-grade-eligible typed multibank routing):
- `ARM_TYPED_ROUTING_MATCHED.recall_mean >= ARM_UNTYPED_BASELINE_ADVERSARIAL.recall_mean + 0.10`
- AND `ARM_TYPED_ROUTING_ADVERSARIAL_PROBE.refuse_rate >= 0.85`
- AND `ARM_UNTYPED_BASELINE_ADVERSARIAL.recall_mean in [0.60, 0.85]` (NOT saturated;
  load-bearing gate per Wave 2 audit)
- AND `recall_cv <= 0.05` across 3 seeds
- AND `cardinality_ok` (all expected units present)

**MIDDLE_BAND**:
- typed-recall lift in [0.03, 0.10] OR refuse-rate in [0.50, 0.85]
- OR baseline in [0.85, 0.95] (mild saturation but still discriminating)

**HARD_FAIL**:
- typed-recall lift <= 0.02 (type signal not actionable; mechanism null)
- OR refuse-rate <= 0.40
- OR `ARM_UNTYPED_BASELINE_ADVERSARIAL.recall_mean >= 0.95`
  (by-construction-saturation auto-demote per META_RULE_K; Q-discipline)
- OR `ARM_UNTYPED_BASELINE_ADVERSARIAL.recall_mean < 0.40` (baseline broken;
  adversarial regime construction is wrong)
- OR `cardinality_ok=False` (silent unit drop per META_RULE_H)

## Discriminator survives full-N (META_RULE_K — Option C)

Smoke at N_DIM=2048, K_TOTAL=2048, n_banks=32, k_per_bank=64, OVERLAP=0.40
(same regime as full at smaller substrate). Smoke ARM_UNTYPED_BASELINE must
land in [0.55, 0.90] (smoke envelope is wider; full envelope tightens to
[0.60, 0.85]). If smoke baseline saturates (>= 0.95) AT SMOKE-N, abort full
dispatch: the OVERLAP=0.40 isn't pushing baseline far enough below ceiling.

Full-N preview arm (per discriminator-must-survive-scale USER 2026-06-26):
smoke runs the adversarial baseline at the SAME OVERLAP=0.40 the full will
use; that IS the regime check.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 3 arms = 3
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` list AND halt the loop
(no silent pass-through; honest failure mode).

## Q-discipline by-construction-saturation check

If `ARM_UNTYPED_BASELINE_ADVERSARIAL.recall_mean >= Q_SUSPECT_SATURATION = 0.95`,
auto-demote any verdict to MEASURED_MECHANISM regardless of HP arithmetic.
This is the load-bearing fix from the Wave 2 audit.

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Compute `cor(refuse_rate_per_query, |W_bank_routed|_per_query)` over the
adversarial-probe arm; if `|cor| >= 0.5`, demote regardless of pass/fail
arithmetic (refuse mechanism is coupled to weight magnitude, not type signal).

## Formula self-tests (run at module import)

1. `assert_k_per_bank_in_discriminating_regime(K_TOTAL=8192, n_banks=128, overlap=0.40, n_dim=8192)` PASSES
2. type-tag construction yields N_TYPES distinct vectors at cosine < 0.10
3. Refuse-gate fires on synthetic ill-typed query (bank cosine << threshold)
4. Verdict-machinery selftest: synthetic HP / HF / MB / cardinality breach cases

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-only; multibank does not need GPU at K=8192)
- Estimated full wall: 1-1.5 hr (3 seeds * 3 arms * N_DIM=8192 matmuls)
- Per-experiment `--timeout`: 7200s (2 hr; 1.5x slack)
- Smoke wall budget: ~60s (1 seed * 3 arms at N_DIM=2048)

## Brain-grounding

MEDIUM. Multi-bank routing analog of basal-ganglia thalamic loops
(Houk-Adams-Barto 1995) + IT cortex feature-grouping.

## P_deflated (lit-scan calibration)

P_deflated = 0.45 (raw lit P=0.65 minus 0.20 calibration penalty; HIGH P
because composes on 3 chain-grade primitives; respec'd to escape saturation).

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=8192, K_TOTAL=8192, n_banks=128,
k_per_bank=64, FEATURE_OVERLAP_FRAC=0.40 ADVERSARIAL, N_TYPES=64, 3 seeds.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
