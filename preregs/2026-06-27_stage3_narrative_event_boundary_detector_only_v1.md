# PRE-REG: stage3_narrative_event_boundary_detector_only_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `stage3_narrative_event_boundary_detector_only_v1`
Source: research drill `notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md` CELL 2
Hand-off: `notes/exp_dev_handoff_research_long_context_narrative_coherence_stage3_2026-06-27.md` ANCHOR 2
Authorization: per drill (recommended dispatch FIRST; de-risks ANCHOR 1)
Wave: Stage 3 compositional understanding (long-context narrative coherence drill)

## Scientific question

Can a substrate-native cosine-shift detector identify event boundaries in
a synthetic narrative stream at precision >= 0.75 AND recall >= 0.75 vs
ground-truth boundaries? Brain analog: hippocampal / DMN event-segmentation
(Zacks 2007 Event Segmentation Theory; Speer-Zacks-Reynolds 2007 brain
activity time-locked to narrative event boundaries; Baldassano 2017
cortical event boundaries; DuBrow-Davachi 2014/16 hippocampal SWR-locked
consolidation).

This cell is an ISOLATED probe of the cosine-shift detector primitive
that ANCHOR 1 (full Stage-3 integration test) depends on. If boundary
detection fails at substrate-native cosine geometry, ANCHOR 1 needs to
fall back to fixed-K=10 evenly-spaced boundaries; this cell determines
which path to take BEFORE the more expensive integration test runs.

## Mechanism class

Within-stream cosine-shift event detection on substrate-encoded events.
Each event is a bipolar hyperdimensional vector built from per-event
component bindings (character / verb / scene-bag). Detector compares
adjacent events: if cosine(event_t, event_{t-1}) drops below theta -> fire
boundary candidate.

Composes on:
- chain-grade bipolar substrate encoding
- chain-grade cosine similarity infrastructure
- substrate-native vector arithmetic (no FFT bind required for THIS cell;
  this cell is event-VECTOR-only, no role-filler bind)

No magnitude-coupling (META_RULE_F): cosine is unit-normalized.

## Config

- N_DIM = 1024 (full); N_DIM (smoke) = 512
- N_EVENTS = 100 (full); 20 (smoke)
- N_CHARACTERS = 5 (full); 3 (smoke)
- N_TRUE_BOUNDARIES = 10 (full; ~one every 10 events on average, jittered);
  3 (smoke)
- WITHIN_EPISODE_DRIFT_RATE = 0.10 (fraction of bits that flip event-to-event
  WITHIN the same episode -- gives within-episode cosine drift signal)
- BOUNDARY_FLIP_RATE = 0.45 (fraction of bits that flip ACROSS a true
  boundary -- significant cosine drop; chosen so cosine drops from ~0.80
  within-episode to ~0.10 across-boundary at N_DIM=1024 SNR)
- THETA_TUNING_SPLIT = 0.30 (first 30% of events used for theta calibration;
  remainder for evaluation -- no test-set tuning per drill spec)
- K_FIXED_BUDGET = 10 (ARM_FIXED_BUDGET fires every K=10 cycles regardless;
  matches full N_TRUE_BOUNDARIES so cardinality is identical)
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds chain-grade)

## Arms (4 mandatory)

1. **ARM_RANDOM_BOUNDARIES** -- chance baseline: pick N_TRUE_BOUNDARIES
   uniformly-random positions. Tests floor (no signal).
2. **ARM_FIXED_BUDGET** -- evenly-spaced: pick every K=N_EVENTS/N_TRUE_BOUNDARIES
   positions. Tests structural-prior baseline (no event-content signal but
   correct count).
3. **ARM_COSINE_SHIFT** (MECHANISM) -- substrate cosine-shift detector. For
   each adjacent pair (event_t, event_{t-1}) compute cosine; fire boundary
   if cosine < theta_calibrated. Theta calibrated on first 30% of events
   (held-out-only-from-eval); fire-budget is the count of values below theta
   (NOT capped at N_TRUE_BOUNDARIES -- detector must self-calibrate).
4. **ARM_ORACLE_CEILING** -- hand-coded boundary detector with ground-truth
   awareness (knows where the BOUNDARY_FLIP_RATE bit-flips happened by
   construction); upper bound. Must be ~1.00 by construction.

## Metric

Primary endpoints per arm (per-arm in metrics.json):
- `boundary_precision` = TP / (TP + FP) -- predicted boundary positions
  matching ground-truth within +/-2 events tolerance window (per drill
  HYPOTHESIZED@ +/-2 window).
- `boundary_recall` = TP / (TP + FN) -- ground-truth boundaries matched
  within tolerance window.
- `boundary_f1` = 2 * P * R / (P + R)
- `precision_recall_balance` = abs(precision - recall) -- HARD_FAIL gate at
  > 0.30 imbalance per drill HF.
- `n_predicted` = boundaries fired by arm
- `theta_calibrated` (ARM_COSINE_SHIFT only)

## Pre-registered bands (strictly-above-floor per META_RULE_L; per drill recommendation)

**HARD_PASS** (cosine-shift detector chain-grade-eligible; gates ANCHOR 1):
- `ARM_COSINE_SHIFT.boundary_precision_mean >= 0.75`
- AND `ARM_COSINE_SHIFT.boundary_recall_mean >= 0.75`
- AND `ARM_COSINE_SHIFT.boundary_f1_mean >= 0.75`
- AND `abs(precision_mean - recall_mean) <= 0.30` (balance check)
- AND `ARM_COSINE_SHIFT.f1_mean - ARM_FIXED_BUDGET.f1_mean >= 0.30`
  (mechanism beats budget-matched random by clear margin -- per drill HP)
- AND `ARM_RANDOM_BOUNDARIES.f1_mean < 0.45` (floor: random expected
  0.30-0.40 mean given +/-2 tolerance over N_EVAL~70 / 7-8 true bdys
  per CRLB pre-validation revision; 0.45 ceiling is realistic random-detection
  floor at this regime, NOT chance-of-exact-hit)
- AND `cv_f1 <= 0.15` across 3 seeds for ARM_COSINE_SHIFT
- AND `cardinality_ok`

**MIDDLE_BAND** (productive learning zone; ANCHOR 1 needs fixed-K=10 fallback):
- `ARM_COSINE_SHIFT.f1_mean` in [0.50, 0.75]
- OR `ARM_COSINE_SHIFT.f1 - ARM_FIXED_BUDGET.f1` in [0.10, 0.30]
  (mechanism above budget but not by drill margin)

**HARD_FAIL** (cell direction killed for ANCHOR 1 cosine-shift path):
- `ARM_COSINE_SHIFT.boundary_f1_mean < 0.50` (mechanism null)
- OR `abs(precision_mean - recall_mean) > 0.30` (severe imbalance per drill HF)
- OR `ARM_ORACLE_CEILING.f1_mean < 0.90` (sanity rail: oracle should be ~1.00
  by construction; if < 0.90 the synthetic generator is mis-built and the
  whole cell is invalid -- structural bug)
- OR `ARM_COSINE_SHIFT.f1_mean <= ARM_RANDOM_BOUNDARIES.f1_mean + 0.05`
  (no lift over chance)
- OR `cardinality_ok=False`

## Discriminator survives full-N (META_RULE_K -- Options A + B)

Option A (smoke at regime-equivalent geometry): smoke at N_DIM=512 with
SAME BOUNDARY_FLIP_RATE=0.45 / WITHIN_EPISODE_DRIFT_RATE=0.10 ratios. The
cosine separation across a boundary at N_DIM=512 vs N_DIM=1024 differs
only in SNR by sqrt(2); the discriminator (mechanism vs fixed-budget vs
random) is regime-invariant at this scale because the cosine drop signal
(0.80 -> 0.10) is far above N_DIM=512 noise floor (~0.045).

Option B (analytical scale justification): cosine on bipolar at N_DIM has
noise std ~ 1/sqrt(N). N=512 -> 0.044; N=1024 -> 0.031. The drift signal
0.80 - 0.10 = 0.70 is >= 15x noise floor at both scales; detector signal
strength does NOT degrade smoke -> full. If smoke ARM_COSINE_SHIFT HP, full
should land tighter (lower noise = sharper boundaries = higher F1).

Option C (full-N preview arm in smoke): NOT needed -- analytical+regime
justification above is sufficient since the mechanism is geometry-driven
not learning-driven (no capacity issue).

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` list AND halt the loop
(raise after recording). SystemExit re-raised BEFORE BaseException per
discipline.

## META_RULE_AF arms-must-differ (SHA-256)

Each arm produces an independent prediction vector (list of fired
boundary positions). At smoke verify SHA-256 of sorted prediction lists
differ across arms (defensive against silent shared-state bug).

## META_RULE_AH atomic-write

All metrics.json writes via tmp + os.replace. Inherited from write_metrics
helper.

## Q-discipline by-construction-saturation check

If `ARM_COSINE_SHIFT.f1_mean >= 0.99`, suspect saturation (the synthetic
generator's BOUNDARY_FLIP_RATE=0.45 may make the task trivially easy at
this N_DIM regime). Auto-demote MM regardless of arithmetic if saturated
AND mechanism F1 within 0.02 of oracle ceiling.

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Cosine is unit-normalized so magnitude coupling is structurally ruled out.
Sanity check: `cor(per_event_cosine, ||event||_per_event)` < 0.5
(should be near 0 by normalization).

## Formula self-tests (run at module import; --self-test exits after)

1. cosine identity: cosine(v, v) ~= 1.0 for random bipolar v
2. cosine orthogonality: |cosine(u, v)| < 4/sqrt(N) for two independent
   random bipolar at N_DIM=1024 (expected ~0.03 noise floor)
3. bit-flip cosine relation: flip-fraction p in [0, 0.5] gives
   cosine = 1 - 2*p ; verify at p=0.10, 0.45 (synthetic small-N)
4. ground-truth boundary injection: assert generator places exactly
   N_TRUE_BOUNDARIES boundaries (no off-by-one)
5. precision/recall/F1 arithmetic on synthetic (TP=8, FP=2, FN=2 ->
   P=0.80, R=0.80, F1=0.80)
6. tolerance-window matching: predicted=[5, 25, 50] vs gt=[6, 27, 51]
   with tol=2 -> all 3 TP
7. theta calibration on first 30% only: assert evaluation set excludes
   first 30% events
8. verdict machinery HP/HF/MB/cardinality synthetic cases
9. pre-reg envelope locks (HP_F1_FLOOR, HP_BAL_MAX frozen)

## Queue / Dispatch

- Queue: `remote_cpu_queue` (per USER 2026-06-28 remote-first; cell is
  numpy/torch eligible; very lightweight; CPU-bound; <30 min wall)
- Estimated full wall: 5-15 min (3 seeds * 4 arms * 100 events * O(N_DIM)
  cosine; cheap)
- Per-experiment `--timeout`: 1800s (30 min; 1.5x slack on 20-min
  conservative midpoint -- much smaller than typical)
- Smoke wall budget: ~30s (1 seed * 4 arms * 20 events at N_DIM=512)

Timeout formula (per CLAUDE.md / queue_add.sh discipline):
- smoke_wall_estimate = 30s
- scaling: events 20->100 = 5x linear; seeds 1->3 = 3x linear; N_DIM 512->1024 = 2x linear cosine
- full_wall_estimate = 30 * 5 * 3 * 2 * 1.5 = 1350s
- Round up to 1800s for slack against jitter / SSH overhead

## Brain-grounding

STRONG. Zacks 2007 Event Segmentation Theory canonical for event-boundary
perception in narrative. Speer-Zacks-Reynolds 2007 brain activity
time-locked to narrative boundaries. Baldassano 2017 cortical event
boundaries shared across individuals. DuBrow-Davachi 2014/16 hippocampal
SWR-locked consolidation at boundaries. Michelmann-Hasson-Norman 2023
LLM-segmented narrative events match human boundaries. The cosine-shift
detector is the substrate-native analog of these mechanisms; this cell
tests whether it works at substrate-native (random-projection) cosine
geometry rather than trained-encoder geometry the lit assumes.

## P_deflated (lit-scan calibration)

P_deflated = 0.40 (raw 0.55, calibration -0.15) per drill CELL 2:
lit-anchored mechanism (cosine-shift segmentation is well-validated in
trained-encoder NLP); substrate-side calibration uncertainty is the only
unknown (random-projection geometry vs trained-encoder geometry).

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=1024, N_EVENTS=100,
N_CHARACTERS=5, N_TRUE_BOUNDARIES=10, BOUNDARY_FLIP_RATE=0.45,
WITHIN_EPISODE_DRIFT_RATE=0.10, +/-2 event tolerance window, 3 seeds.

This cell does NOT claim the cosine-shift detector works on real
trained-encoder text; it claims it works on substrate-native bipolar
event vectors at the parametric drift regime above. ANCHOR 1 (the full
integration test) is what extends this to integration-with-other-primitives;
this cell is the ISOLATED de-risking probe.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).

## CRLB pre-validation (per drill §9)

Cosine on bipolar at N_DIM=1024: noise std ~ 1/sqrt(1024) = 0.031.
BOUNDARY_FLIP_RATE=0.45 -> cosine drop = 1 - 2*0.45 = 0.10 across
boundary; WITHIN_EPISODE_DRIFT_RATE=0.10 -> within-episode cosine = 0.80.
SNR for boundary detection = (0.80 - 0.10) / 0.031 ~= 22.6 -- far above
the SNR=3 conservative detection threshold. F1=0.75 HARD_PASS gate is
CRLB-feasible with substantial margin.

For ARM_FIXED_BUDGET at N=100 events / K=10 budget vs N_TRUE_BOUNDARIES=10:
chance of hitting a true boundary at +/-2 tolerance window is ~5/100 = 0.05;
expected F1 ~ 0.05. The drill HP gate of mechanism-minus-fixed-budget >= 0.30
gives F1 separation 0.30+ above this baseline floor, which is realized at
F1>=0.35 for mechanism (well below HP at F1=0.75).

For ARM_RANDOM_BOUNDARIES: expected F1 ~= 5/100 = 0.05 (random hits within
tolerance ~5% of the time given +/-2 window). HP gate at < 0.30 is well
above this 0.05 noise.

All HARD_PASS gates are CRLB-feasible.
