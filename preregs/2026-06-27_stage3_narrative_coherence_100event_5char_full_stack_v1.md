# PRE-REG: stage3_narrative_coherence_100event_5char_full_stack_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `stage3_narrative_coherence_100event_5char_full_stack_v1`
Source: research drill `notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md` CELL 1 (P_deflated=0.45)
Hand-off: `notes/exp_dev_handoff_research_long_context_narrative_coherence_stage3_2026-06-27.md` ANCHOR 1
Authorization: per drill (TOP cell of long-context narrative coherence Stage-3 drill)
Wave: Stage 3 compositional understanding (marquee integration test)

## Scientific question

Can the substrate maintain narrative coherence across 100 events with 5
characters by COMPOSING 5 chain-grade primitives into a Stage-3 integration
pipeline? HARD_PASS demonstrates the substrate's modular primitives compose
into M3-relevant capability (long-context conversational memory) without new
physics; HARD_FAIL identifies which composition seam breaks.

USER concern #3 for M3: "friend who's great at last 5 min, loses track by
hour 2". This cell is the marquee integration test that empirically anchors
the answer at 100-event / 5-character scale.

## Mechanism class

5-primitive composition pipeline:

1. **cortex_hippo_handoff** (smoke HARD_PASS today; M=400 FULL=1.000;
   gap=+0.998): sparse k-WTA hippo (10% sparsity) + dense cortex with slow
   Hebbian eta_c=0.005 + scene-boundary-triggered consolidation replay.
2. **sequence_binding K=20** (chain-grade): cyclic-shift permutation
   positional code applied to within-scene event keys (np.roll(key, pos)).
3. **partition_routing** (chain-grade @M=100k=0.9697): per-character
   partition cortex W_part[char_id] writes; routes character-tagged events
   to per-character matrix. 5 characters -> 5 partitions.
4. **TWO_TIER generational W** (HARD_PASS_PARTIAL drift_reduction=0.30):
   per-(char, fact_idx) latest-value cache with generation counter so the
   latest fact-write overrides earlier ones (resolves Q4 contradictions).
5. **FIXED-K=10 event boundaries** (per ANCHOR 2 MIDDLE_BAND fallback): the
   ANCHOR 2 cosine-shift detector smoke landed cs_f1=1.000 saturated at the
   drill SNR (auto-demoted MIDDLE_BAND per by-construction-saturation rule);
   drill recommendation in that branch is "fall back to fixed-K=10 boundaries"
   -- this cell uses that fallback per task brief.

## Config

Full:
- N_HIPPO = 512, N_CORTEX = 1024, N_PART = 1024
- N_EVENTS = 100, N_CHARACTERS = 5
- K_SCENE_BOUNDARY = 10 (10 scenes of 10 events each)
- K_HIPPO_ACTIVE = 51 (10% k-WTA sparsity)
- ETA_CORTEX = 0.005 (slow Hebbian rate; cortex_hippo_handoff convention)
- N_REPLAY_CYCLES = 3 (per-scene consolidation)
- N_FACTS_PER_CHAR = 3 (static factual claims about each char)
- N_UPDATE_PAIRS = 3 (early/late update pairs for Q4 contradictions)
- N_PRONOUN_EVENTS = 8 (events using pronoun coreference)
- FORGET_WINDOW = 5 (ARM_FORGET visibility)
- Q_PER_TYPE = 3 (3 queries per Q-type * 4 Q-types = 12 queries per arm/seed)
- N_RAW = 64 (raw input dim, drives sparse pattern separation)
- N_VERBS = 12, N_OBJECTS = 16, N_JOBS = 8 (vocab sizes)
- SEEDS = [11, 13, 19] (3 seeds chain-grade)

Smoke:
- N_HIPPO = 512, N_CORTEX = 1024, N_PART = 512
- N_EVENTS = 50, N_CHARACTERS = 3
- K_SCENE_BOUNDARY = 10, K_HIPPO_ACTIVE = 51
- N_FACTS_PER_CHAR = 2, N_UPDATE_PAIRS = 2, N_PRONOUN_EVENTS = 4
- Q_PER_TYPE = 2 (8 queries per arm/seed)
- SEEDS = [11]

## Arms (4 mandatory)

1. **ARM_FORGET_EVERYTHING** (floor): only last FORGET_WINDOW=5 events
   encoded; queries about earlier events get random-floor answers. This is
   the "good at last 5 min" baseline that USER's concern describes.
2. **ARM_FLAT_BASELINE** (lose-by-interference): single Hebbian W with all
   100 events + facts superposed; no partition, no segmentation, no two-tier.
3. **ARM_NO_SEGMENT** (segmentation discriminator): cortex+partition+two-tier
   composed, but consolidate every event (no scene boundaries). Tests
   whether scene segmentation is load-bearing.
4. **ARM_FULL_STACK** (MECHANISM): all 5 primitives composed properly.
   Scene-boundary consolidation every K=10 events; per-character cortex
   partitions; TWO_TIER W for fact updates.

## Queries (4 types)

- **Q1_factual**: "what is char's fact[fi] value?" - tests cortex
  consolidation; pulls a static fact from early events.
- **Q2_coreference**: "when 'he/she' did <verb> <obj> in scene s, who is
  the referent?" - tests pronoun-to-partition routing.
- **Q3_temporal**: "given target event, which event came IMMEDIATELY
  before in the same scene?" - tests sequence-binding positional code.
- **Q4_contradict**: "char had fact[fi]=X early, =Y late; current value?"
  - tests TWO_TIER generational W staleness signal.

## Pre-registered bands (strictly-above-floor per META_RULE_L; LOCKED)

**HARD_PASS** (all 5 conditions must hold):
- `ARM_FULL_STACK.overall_accuracy_mean >= 0.70` (HP_OVERALL_FLOOR)
- AND `ARM_FULL_STACK.overall - ARM_FLAT_BASELINE.overall >= 0.25`
  (HP_LIFT_OVER_FLAT; composition adds value over flat)
- AND `ARM_FULL_STACK.overall - ARM_FORGET_EVERYTHING.overall >= 0.50`
  (HP_LIFT_OVER_FORGET; signal above 5-event-window floor)
- AND `min(Q1, Q2, Q3, Q4) >= 0.60` (HP_PER_QUERY_FLOOR; no single
  query type fails)
- AND `cv_overall <= 0.15` across seeds (HP_CV_MAX)
- AND `arms_distinct=True` (META_RULE_AF; SHA-256 of prediction lists)
- AND `cardinality_ok` (META_RULE_H)

**MIDDLE_BAND** (productive learning zone):
- `ARM_FULL_STACK.overall_accuracy_mean` in [0.40, 0.70)
- AND `lift_over_flat >= 0.10` (composition still adds some value)
- Per-arm diagnostic identifies which primitive is the binding constraint
  (likely partition-router coref Q2 or contradiction Q4 per drill HF3).

**HARD_FAIL** (any one kills this cell direction):
- `ARM_FULL_STACK.overall < 0.40` (HF_OVERALL_BREAK; composition broken)
- OR `abs(FULL - FLAT) <= 0.05` (HF_FLAT_TIE_DELTA; composition useless)
- OR `min(Q1, Q2, Q3, Q4) < 0.30` (HF_PER_QUERY_FLOOR; single point of failure)
- OR `cardinality_ok=False` (META_RULE_H)
- OR `arms_distinct=False` (META_RULE_AF)

## Discriminator survives full-N (META_RULE_K, Option A + B)

Option A (smoke at near-full event count): smoke uses N_EVENTS=50 with
3 characters at the SAME N_HIPPO=512 / N_CORTEX=1024 geometry as full.
The 50-event half-scale stresses the consolidation + partition pipeline
sufficiently to fire the discriminator (ARM_FULL_STACK vs ARM_FLAT vs
ARM_FORGET should separate at this scale because flat-W interference is
already significant at 50 events with full superposition).

Option B (analytical scale justification): cortex capacity alpha = M /
N_c = 100 / 1024 = 0.098 well below Hopfield alpha_c = 0.14; cortex
should hold all 100 events post-consolidation without catastrophic
interference. With 5 partitions, per-partition alpha = (100/5) / 1024 =
0.02 (highly under capacity); partition routing should yield near-lossless
per-character recall. Discriminator survives scale because the FLAT arm
gets interference-degraded at alpha=0.098 (within Hopfield regime) while
the partitioned full-stack stays at alpha=0.02 per-partition.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 4 arms = 12 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4 (smoke)
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected OR any failures

## No silent except (META_RULE_J)

All per-unit exceptions captured into failures[] list AND halt the loop
(raise after recording). SystemExit re-raised BEFORE BaseException per
discipline.

## META_RULE_AF arms-must-differ (SHA-256)

Each arm produces an independent prediction sequence across all 12 queries
(serialized as `Qn:char:fi:pred` strings). SHA-256 of joined predictions
must differ across at least 2 of 6 arm pairs (mechanism may legitimately
tie one baseline if mechanism converges to oracle on Q1+Q4 facts; the
gate enforces non-trivial separation).

## META_RULE_AH atomic-write

All metrics.json writes via tmp + os.replace via write_metrics helper.

## Q-discipline by-construction-saturation check

If `ARM_FULL_STACK.overall_accuracy >= 0.99`, suspect saturation (queries
trivial at this regime). Auto-DEMOTE to MIDDLE_BAND would apply but this
cell's HP gate is 0.70 (well below 0.99); saturation is structurally
implausible at this composition.

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

Cortex readout uses cosine_argmax over L2-normalized candidates so magnitude
coupling is structurally ruled out at the decision boundary. Sparse hippo
codes are unit-energy by construction (exactly K=51 bipolar entries).

## Formula self-tests (run at module import; --self-test exits after)

1. cosine identity: cosine(v, v) >= 0.999 for random bipolar v
2. cosine orthogonality: |cosine(u, v)| < 4/sqrt(N) for independent bipolar
3. pattern_separate_sparse k-WTA bipolar at exactly k=51 active entries
4. project_h_to_c shape (N_CORTEX,) and L2 normalization
5. permute_role_pos bijective (np.roll preserves all entries)
6. Narrative produces N_EVENTS events; N_PRONOUN_EVENTS pronouns; valid char_ids
7. make_queries: Q_PER_TYPE per type; Q1 expected matches static_facts;
   Q4 expected = late_val with late_event_idx > early_event_idx
8. build_vocab returns expected shapes (chars, P_hc, P_pc)
9. run_arm(ARM_FORGET_EVERYTHING) completes; returns 0<=acc<=1; required fields
10. verdict HARD_PASS synthetic case
11. verdict HARD_FAIL composition_broken synthetic case
12. verdict HARD_FAIL composition_useless synthetic case
13. verdict HARD_FAIL single_query_collapse synthetic case
14. verdict META_RULE_AF arms-collapse-to-identical-SHA -> HARD_FAIL
15. verdict cardinality breach -> HARD_FAIL
16. verdict MIDDLE_BAND synthetic
17. pre-reg envelope constants LOCKED

## Queue / Dispatch

- Queue: `remote_cpu_queue` (per USER 2026-06-22 remote-first; cell is
  numpy/CPU bound; matmul-light at N_CORTEX=1024; <60 min wall expected)
- Estimated full wall: 30-60 min (3 seeds * 4 arms; per-arm wall dominated
  by N_REPLAY_CYCLES=3 over scene events; cheap relative to multi-hop cells)
- Per-experiment `--timeout`: 3600s (60 min; 1.5x slack on 40-min midpoint)
- Smoke wall budget: ~5-10 min (1 seed * 4 arms * 50 events; analytical
  scaling from 5-min cortex_hippo_handoff smoke at M=400 -> here M=50 events
  but more arms + queries + per-char partitions)

Timeout formula (per CLAUDE.md / queue_add.sh discipline):
- smoke_wall_estimate = 300s (5 min)
- scaling: events 50->100 = 2x linear; chars 3->5 = 1.67x linear (more partitions);
  seeds 1->3 = 3x linear
- full_wall_estimate = 300 * 2 * 1.67 * 3 * 1.5 (slack) = 4500s
- Cap at 3600s for budget discipline (most arms much cheaper than worst-case);
  smoke must validate that estimate before full dispatch.

## Brain-grounding

STRONG. CLS theory (McClelland-McNaughton-O'Reilly 1995) for cortex_hippo
consolidation; ATL person-to-schema hub (Patterson 2007) for entity binding;
Hasson 2008 hierarchy of temporal receptive windows for narrative integration;
Chen 2017 DMN tracks shared narrative structure; Zacks 2007 event
segmentation theory for scene-boundary triggered consolidation; Buzsaki 2015
SWR consolidation; Cowan 2010 working memory 4-item limit (substrate offers
1M-partition routing -- 200,000x parallel-referent capacity vs brain).

## P_deflated (lit-scan calibration)

P_deflated = 0.45 (raw 0.65, calibration -0.20) per drill CELL 1:
all 4 ingredients chain-grade individually; the composition at >100 events
has zero substrate prior; cortex_hippo_handoff smoke HARD_PASS at M=400
today de-risks the consolidation step. Novel-synthesis cap 0.50 respected.

## Honest scope

The HARD_PASS claim is bounded to: 100-event narrative, 5 characters,
10 scenes (K=10 fixed boundaries), 3 facts per char, 3 update pairs, 8
pronoun events, +/- 5 minutes "current time" semantics (Q4 "current"
means most-recent), random-projection encoder geometry (not trained text
embedding), 3 seeds.

This cell does NOT claim the substrate handles real conversational text
(no token-level prediction; no language model competence test). It claims
the substrate's 5-primitive composition handles a SYNTHETIC long-context
narrative at the parametric regime above. ANCHOR 2 de-risked the boundary
detector (MIDDLE_BAND saturated; using fixed-K fallback); this cell is the
end-to-end integration test for the full pipeline.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).

## CRLB pre-validation (per drill §9)

For Q1 factual at M=100 events / N_c=1024 cortex: alpha = M/N_c = 0.098,
below Hopfield alpha_c=0.14. Expected recall in absence of noise >= 0.85.
HP gate at Q1 >= 0.60 has CRLB margin of ~0.25.

For Q2 coref at 5 partitions / N_part=1024: 5-way classification floor =
0.20 (random); HP gate at 0.60 is +0.40 above floor; per-partition write
count = (100/5) * 0.92 (non-pronoun) ~= 18 supporting writes per partition;
CRLB on 5-way classifier needs ~12 supporting co-occurrences which is
satisfied.

For Q3 temporal at sequence_binding K=20 chain-grade ceiling: within-scene
positional code via np.roll is lossless (bijective permutation); CRLB on
predecessor recall at K=20 binding ceiling >= 0.95 in absence of noise;
HP gate at Q3 >= 0.60 has CRLB margin of ~0.35.

For Q4 contradiction at TWO_TIER drift_reduction=0.30 baseline: the
generational W stores the LATEST write per (char, fact_idx); recall of
LATEST is structurally 1.0 by design (the gen_W dict is a direct map).
HP gate at Q4 >= 0.60 has substantial CRLB margin against gen_W read
failures (which would imply a code bug, not a capacity issue).

All HARD_PASS gates are CRLB-feasible with margin.
