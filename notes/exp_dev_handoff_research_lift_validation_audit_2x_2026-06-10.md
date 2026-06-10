# exp_dev hand-off -- research: lift validation audit 2x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_lift_validation_audit_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Why this hand-off exists

LVH-274 caught negres_struct_align (PP-303): absolute Hits@1=0.402 passed the absolute >=0.40
gate but lift over baseline=0.400 was only 0.001 (lift/SE = 0.09 -- deep noise). A systematic
audit of PP-263..PP-312 (cycles 215-220, 50 rows) found no additional silent method-overclaims
of that severity, but identified three documentation gaps that require empirical resolution:

1. PP-292 (meta-learning, acc=0.707): no retrieval-only baseline is documented. The 0.707
   result may be noise-level lift over plain substrate retrieval -- identical to the PP-303
   situation. This is the highest priority.

2. PP-310..PP-312 (production-scale shards, recall=1.000): the flat-bundle comparison at
   equivalent atom counts is not documented. Without it, the "production-scale architecture"
   claim is an anti-confound gap.

3. PP-274 (N=100 ensemble, gain=30pp): the task chance-rate is not documented, so the
   single=0.700 absolute value cannot be contextualised against chance. This is lower priority
   (the ensemble lift is decisively measured regardless) but should be closed for product claims.

---

## Anchor candidates (rank-ordered by priority)

### A. PP-292 retrieval-only baseline -- HIGHEST PRIORITY

Anchor pointer: lap4_meta_retrieval_baseline_cpu_v1 (new; not yet queued)
Substrate-product reading: Determines whether the episode-format meta-learning protocol (PP-292,
  acc=0.707) adds genuine lift over plain substrate K-shot retrieval, or whether the 0.707
  result is a PP-303 analog (absolute threshold met, method adds noise-level lift).
  If plain retrieval also scores 0.700, the meta-learning wrapper adds nothing.
  If plain retrieval scores near chance (0.200 for 5-way), meta-learning is genuinely useful.
Tier hint: CPU laptop / cpu_runner_local; same evaluation loop as stretch4_4 but without the
  episode-format wrapper. ~10 minutes wall time.
Why-now: Before any PP-292 rescue escalation (K-sweep, threshold tuning), the retrieval-only
  baseline must be measured. Escalating a method-negative to HARD_PASS via K-sweep would
  inflate the portfolio the same way PP-303 did. This test must run first.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS for meta-learning method: plain_acc <= 0.650
    -> lift = 0.707 - plain_acc >= 0.057, SE(0.650, 1500) ~= 0.0123, lift/SE >= 4.6
    -> Meta-learning has genuine value; rescue K-sweep is warranted
  HARD-FAIL for meta-learning method: plain_acc > 0.700
    -> lift = 0.707 - plain_acc < 0.007, lift/SE < 0.6 -- noise
    -> Annotate PP-292 as method-negative (episode format adds nothing over plain retrieval)
    -> Do NOT escalate to K-sweep; that would be fitting to noise
  MIDDLE_BAND: plain_acc in [0.650, 0.700]
    -> Lift is borderline (lift/SE 0.6-4.6); run K=10 and K=20 with BOTH plain and meta-learning
    -> Final verdict requires both protocols at K=10 and K=20 to separate method effect from K effect

Expected outcome (research estimate, P_deflated=0.35): plain_acc likely near 0.700.
  Substrate retrieval is already good at the relevant task; the episode format may not add.
  If this estimate is right, PP-292 should be annotated as a method-negative for episode format.
  Do not use this estimate as pre-reg; measure it.

### B. PP-310..PP-312 flat-bundle anti-confound -- MEDIUM PRIORITY

Anchor pointer: flat_bundle_shard_antconfound_cpu_v1 (new; not yet queued)
Substrate-product reading: Measures whether the production-scale shard results (PP-310 50k atoms,
  PP-311 5k atoms, PP-312 1k atoms) represent genuine architectural isolation or trivial within-
  shard storage that would also work in a flat bundle (because shard sizes are within kstar).
  If flat-recall collapses at scale, the shard architecture is validated. If flat-recall stays
  high, the shard results are storage correctness checks only.
Tier hint: CPU laptop; store all shard atoms in a flat bundle at the same N used per shard,
  measure recall. ~30 minutes wall time (three measurements at 50k, 5k, 1k atom counts).
Why-now: The "production-scale architecture" product claim requires this comparison to be honest.
  PP-244 predicts kstar=200 at N=4096, so 50k atoms in a flat bundle should collapse near zero.
  If the experiment used larger N, the threshold shifts and the claim may be weaker.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS for architecture claim: flat_recall < 0.500 at 50k total atoms
    -> Shard isolation is necessary; architecture is validated; update PP-310..PP-312 annotations
  HARD-FAIL for architecture claim: flat_recall > 0.950 at 50k total atoms
    -> Shard architecture adds nothing (storage already works flat); re-frame rows as storage
       correctness rather than architecture validation
  MIDDLE_BAND: flat_recall in [0.500, 0.950] at 50k total atoms
    -> Partial isolation benefit; document N-per-shard and boundary condition in cap_map
    -> Update P-bands of PP-310..PP-312 to reflect partial rather than full architecture validation

Note: also record N-per-shard from the actual experiment scripts (data/exp_comp25_story_shard_l3_cpu_v1)
and add to cap_map annotations regardless of outcome.

### C. PP-274 task chance-rate documentation -- LOW PRIORITY

Anchor pointer: This is a documentation fix, not a new experiment.
Substrate-product reading: The cap_map row for PP-274 should note the task name and the
  chance rate (1/N_classes) so that single=0.700 can be interpreted correctly in product claims.
  If chance = 0.500 (binary), single is 20pp above chance. If chance = 0.100 (10-class),
  single is 60pp above chance. The ensemble result is honest either way, but the interpretation
  differs.
Tier hint: Read the experiment script for stretch4_4 / PP-274 to identify the task.
  Add a one-line annotation to the cap_map PP-274 row: "task chance rate = [value]."
Why-now: Low urgency. Can be done as an annotation pass without any new experiment.

---

## Discipline rule to implement

Per the research audit, the following pre-reg discipline rule should be applied to all future
method-comparison anchors:

For any anchor with negres_*, rescue_*, _head suffix, or where verdict_msg will contain
"improves over / adds over / lifts / rescue":

  REQUIRED additional pre-reg fields:
    baseline_estimate: [numeric value or "absent" for pure capability claims]
    lift_threshold_2se: [2 * sqrt(p*(1-p)/n) at expected baseline p and experiment n]
    lift_threshold_5se: [5 * sqrt(p*(1-p)/n)]

  MINIMUM bar for HARD_PASS on a method claim: lift >= 2*SE over baseline.
  MINIMUM bar for "validated" in cap_map text: lift >= 3*SE over baseline.

This rule applies to new anchors only. No existing PP rows need revision (the already-caught
cases LVH-272 and LVH-274 are correctly documented as negative findings).

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_lift_validation_audit_2x_2026-06-10.md
Strategy decisions (cycles 215-220): d:/AI/hd-instrument/notes/strategy_decisions_2026-06-09.md
  and d:/AI/hd-instrument/notes/strategy_decisions_2026-06-10.md
PP-292 experiment metrics: d:/AI/hd-instrument/data/exp_stretch4_4_meta_learning_cpu_v1/metrics.json
PP-310 experiment scripts: d:/AI/hd-instrument/data/exp_comp25_story_shard_l3_cpu_v1/ (for N-per-shard)
PP-274 experiment scripts: d:/AI/hd-instrument/data/exp_lap3_7_n100_ensemble_cpu_v1/ (for task type)
Capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
  (PP-274 line 13668, PP-281 line 13684, PP-292 line 13724, PP-310-312 lines after 13731)

---

## Contract section

- exp_dev is authorised to queue Anchor A (retrieval baseline) and Anchor B (flat-bundle
  antconfound) immediately without further orchestrator approval.
- Anchor C is a documentation fix, not a new experiment; annotate cap_map directly.
- If Anchor A returns HARD-FAIL (plain_acc > 0.700): annotate PP-292 as method-negative and
  do NOT escalate to K-sweep rescue. File as negative annotation, not a new LVH.
- If Anchor A returns HARD-PASS (plain_acc <= 0.650): proceed with K-sweep rescue (K=10, K=20)
  for PP-292 following normal rescue protocol with pre-reg for both plain and meta-learning at
  each K value.
- The new discipline rule (baseline_estimate + lift thresholds for method claims) applies from
  this hand-off forward. exp_dev implements it in the next pre-reg for any negres_*/rescue_*
  anchor.

## Autonomy declaration

exp_dev has full autonomy to:
  - Design the exact evaluation protocol for Anchor A (task split, K value, format)
  - Choose N-per-shard for Anchor B (match what PP-310..PP-312 actually used)
  - Decide queue assignment (cpu_runner_local vs overnight_queue)
  - Set the smoke-gate n for initial dispatch
  - Refine pre-reg bands based on actual SE calculation from n chosen
exp_dev does NOT need to check back before dispatching A or B.
