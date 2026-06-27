# PRE-REG: stage3_typed_routing_falsification_bijective_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `stage3_typed_routing_falsification_bijective_v1`
Source: research drill `notes/research_drill_typed_multibank_actively_hurts_3x_2026-06-27.md` STUB E
Authorization: USER 2026-06-27 NO LOCAL (cell-author smoke + dispatch on remote only)
Wave: closes typed-routing branch cleanly after Wave 2 Anchor 2 HARD_FAIL

## Scientific question

Falsification probe: with N_TYPES = N_BANKS = 64 (BIJECTIVE one-to-one type-to-bank
assignment, ZERO collision possible by construction), does typed-routing
recover untyped chain-grade multibank performance, OR does the
type-routing path introduce ANY measurable degradation? AND does the
prior K=128 (collision regime) replicate to its mathematically predicted
~0.44 recall as documented in the drill?

This is a sanity probe with P_deflated = 0.80 — should HARD_PASS unless
substrate has a non-collision bug we haven't seen.

## Mechanism class

Bijective type-to-bank routing (drill fix M1). Composes on:
- chain-grade multibank K=8192 / k_per_bank=64 / n_banks=64 with content-cosine
  routing (BASELINE arm; sanity rail)
- typed routing where each bank has a UNIQUE type (BIJECTIVE_TYPED arm)
- collision-regime control replicating v1 FALLBACK_FIRST_MATCH (validates
  drill math; META_RULE_K discriminator-fires)

No magnitude-coupling (META_RULE_F): type labels are external integer
routing tokens, NOT per-atom |W| signals.

## Config

- N_DIM = 8192 (full); N_DIM (smoke) = 2048
- K_TOTAL = 4096 (full); K_TOTAL (smoke) = 1024
- N_BANKS = 64 (full); N_BANKS (smoke) = 16
- K_PER_BANK = 64 (full); K_PER_BANK (smoke) = 64
- N_TYPES_BIJECTIVE = N_BANKS = 64 (full) / 16 (smoke)  [bijective arm]
- N_TYPES_FALLBACK = N_BANKS / 2 = 32 (full) / 8 (smoke)  [collision control arm]
- FEATURE_OVERLAP_FRAC = 0.40 (adversarial; matches v1 regime for clean compare)
- CUE_COS = 0.70
- SIGMA = 1.0
- N_ITEMS_PER_K = 100
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds chain-grade)

## Arms (3 mandatory; per-arm metrics in metrics.json)

1. **ARM_BASELINE** — chain-grade content-cosine multibank routing (no typing).
   Sanity rail: must land >= 0.90 (untyped chain-grade at this regime).
2. **ARM_BIJECTIVE_TYPED** — N_TYPES = N_BANKS = 64. Each bank assigned unique
   type. Typed routing by type-label-lookup. Routing accuracy = 1.000 by
   construction (no collisions possible).
3. **ARM_FALLBACK_FIRST_MATCH** — N_TYPES = N_BANKS / 2 = 32. Replicates v1
   first-match-deterministic collision regime as control. Expected
   recall ~ E[1/k] x cleanup ~= 0.44 per drill A1.2 math.

## Metric

Primary endpoints per arm (per-arm in metrics.json):
- `recall_mean` across 3 seeds
- `recall_cv` across 3 seeds
- `route_acc_mean` per arm
- `typed_lift_vs_baseline` = ARM_BIJECTIVE_TYPED.recall - ARM_BASELINE.recall
- `collision_ratio_check` = ARM_FALLBACK_FIRST_MATCH.recall / 0.44
  (drill-math validation; should be in [0.85, 1.15])

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (drill recommendation: KEEP typed-routing as concept; collision
geometry was sole cause of v1 failure):
- `ARM_BIJECTIVE_TYPED.recall_mean >= ARM_BASELINE.recall_mean + 0.10`
- AND `ARM_BASELINE.recall_mean >= 0.90` (sanity rail intact)
- AND `ARM_FALLBACK_FIRST_MATCH.recall_mean in [0.38, 0.50]` (validates
  drill math at E[1/k] x cleanup ~= 0.44)
- AND `recall_cv <= 0.05` across 3 seeds for ALL arms
- AND `cardinality_ok`

**MIDDLE_BAND** (drill recommendation: KILL typed-routing — adds no value
when collision-free, redundant with content-cosine):
- ARM_BIJECTIVE_TYPED within 0.05 of ARM_BASELINE (typed adds no value)
- AND ARM_FALLBACK_FIRST_MATCH in [0.38, 0.50] (drill math holds)
- AND cardinality_ok

**HARD_FAIL** (drill recommendation: KILL typed-routing definitively;
typed actively HURTS even bijective):
- `ARM_BIJECTIVE_TYPED.recall_mean < ARM_BASELINE.recall_mean - 0.02`
  (typed hurts even with zero collisions)
- OR `ARM_BASELINE.recall_mean < 0.85` (baseline broken; methodology drift)
- OR `ARM_FALLBACK_FIRST_MATCH.recall_mean` outside [0.30, 0.60]
  (drill math wrong; substrate behaves differently than predicted)
- OR `cardinality_ok=False` (silent unit drop per META_RULE_H)

## Discriminator survives full-N (META_RULE_K — Option A)

Smoke at N_DIM=2048, K_TOTAL=1024, N_BANKS=16: same OVERLAP=0.40 regime as
full. The COLLISION arm at smoke (N_TYPES=8, N_BANKS=16) should land near 0.44
(2-banks-per-type avg, same as v1). If smoke COLLISION arm lands at 0.90,
the discriminator is by-construction-saturated at this regime and full
dispatch is aborted. Discriminator FIRES at smoke-N because the math is N-invariant
(routing collision rate is purely a function of N_TYPES/N_BANKS ratio).

Per USER 2026-06-27 NO LOCAL: smoke runs on remote_cpu_queue same as full;
no laptop runs.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 3 arms = 3
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` list AND halt the loop.
No silent pass-through.

## Q-discipline by-construction-saturation check

ARM_BASELINE at this regime can be expected at ~0.90-0.95 (chain-grade
content-cosine at K=4096 / n_banks=64 / k_per_bank=64 / OVERLAP=0.40);
NOT 1.000 saturated because OVERLAP=0.40 is adversarial. If ARM_BASELINE
>= 0.98, auto-demote regardless of HP arithmetic (saturation makes the
+0.10 lift requirement structurally unachievable).

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Type labels are external integer tokens; no per-atom |W| coupling possible.
META_RULE_F NA for this cell (asserted at module init in selftest).

## Formula self-tests (run at module import)

1. `assert N_TYPES_BIJECTIVE == N_BANKS` (bijective constraint)
2. `assert N_TYPES_FALLBACK * 2 == N_BANKS` (collision regime: 2 banks per type)
3. Type-tag construction yields N_TYPES distinct integer labels (asserted unique)
4. Routing-by-type-lookup matches identity for bijective case (synthetic check)
5. Drill-math prediction: E[1/k] for k = 1 + Binomial(N_BANKS-1, 1/N_TYPES) ~= 0.44
   for N_TYPES=32, N_BANKS=64; assert via Monte Carlo at module init
6. Verdict-machinery selftest: HP / HF / MB / cardinality breach synthetic cases
7. Pre-reg envelope locks (assert HP_LIFT_MIN, HF_BASELINE_FLOOR constants frozen)

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-only; no GPU benefit at this scale)
- Estimated full wall: ~1 hr (3 seeds * 3 arms * N_DIM=8192 simple matmuls)
- Per-experiment `--timeout`: 5400s (1.5 hr; 1.5x slack on 1-hr estimate)
- Smoke wall budget: ~30s (1 seed * 3 arms at N_DIM=2048)
- USER 2026-06-27 NO LOCAL: smoke gate runs on remote, not laptop

## Brain-grounding

N/A — this is a falsification probe, not a brain-grounded mechanism cell.
Per drill: "if STUB E HARD_PASSes, I close the typed-routing investigation
cleanly."

## P_deflated (lit-scan calibration)

P_deflated = 0.80 (raw 0.95 because mechanism is essentially relabeling
chain-grade; calibration -0.15 for cell-author-error risk). This is HIGH P
because it's basically a sanity check; should HARD_PASS if substrate is
working correctly.

## Honest scope

The HARD_PASS / HARD_FAIL / MIDDLE_BAND verdict is bounded to:
N_DIM=8192, K_TOTAL=4096, N_BANKS=64, K_PER_BANK=64, FEATURE_OVERLAP_FRAC=0.40,
N_TYPES_BIJECTIVE=64, N_TYPES_FALLBACK=32, 3 seeds.

Outcome decisions (per drill SYNTHESIS):
- HARD_PASS -> KEEP typed-routing concept; v1 failure was pure collision geometry
- MIDDLE_BAND -> KILL typed-routing branch; redundant with content-cosine
- HARD_FAIL -> KILL typed-routing definitively; actively hurts mechanism

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
