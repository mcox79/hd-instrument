# Research: brain-structure -> CONSUMER re-map, post-ingest-live (consumer-first re-audit)

**Date:** 2026-07-07. Type: 2x-style operational drill (deepen the 07-05/07-07 brain-component
consumer-ranking findings against the NEW fact that the ingest arc landed Stage-0 FULL today) +
2 targeted external lit-scans on the one genuinely new question this raises (does CLS-consolidation
now have a real consumer). No cell dispatch, no cell design -- pure analysis per task scope.
**Discipline:** mechanism-analog-is-not-task-analog applied throughout (a component's NAME sounding
relevant to ingest is not evidence it is load-bearing for the ingest ARCHITECTURE actually shipped).
Lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis P capped 0.50). All internal
figures re-verified off-disk today (Fix#28), not carried from memory.

---

## HEADLINE

**Ingest going live does NOT create a real consumer for CLS-consolidation in its classic
neuroscience sense (fast-hippocampal-buffer protecting against catastrophic interference in a
shared-weight store) -- and this is now a TESTED, not assumed, negative: the shipped Stage-0 ingest
pipeline (`exp_ingest_knowledge_integration_verify_v1`, FULL, HARD_PASS today) writes each fact as a
discrete, individually-addressable graph record (verified exact completeness 142,219/142,219 atoms,
189,763/189,654+109 edges) with zero shared distributed weights and zero decay -- there is
structurally nothing for a new fact to interfere with. Two independent external lit-scans this cycle
confirm this is not substrate-specific special pleading: catastrophic interference in the literature
is explicitly a property of SHARED distributed/embedding representations (McCloskey & Cohen 1989;
continual-KG-embedding literature, arXiv:2101.05850, arXiv:2405.04453), never attributed to
symbolic/edge-list graph storage itself. The ingest arc DID surface a real but DIFFERENT and DEFERRED
consumer for the other half of CLS theory (slow schema-extraction from repeated witnesses): the
already-flagged Stage-4 "neocortical-analog consolidation loop" (auto-promote a genuinely new
relation TYPE after N witnesses, needed only once ingest moves past curated-relation-set sources like
ConceptNet toward open-corpus text) -- a second lit-scan finds this multi-witness-before-promotion
principle IS well-evidenced in adjacent open-IE/ontology-induction literature (ReVerb
redundancy-confidence, CESI/CMVC clustering-based canonicalization), but the CLS brain-analogy itself
is NOT drawn there -- it is this project's own synthesis, not an external precedent, so it is capped
accordingly. Bottom line: the overall ranking from 07-05/07-07 is UNCHANGED by ingest going live --
hippocampal attractor recall and the basal-ganglia gate remain the only two PROVEN consumers; the
single best next brain-structure build remains the ALREADY-QUEUED cerebellar SR-rollout targeting the
basal-ganglia gate's own measured depth-degradation (07-07 note), not a new CLS build.**

---

## 1. Ranked consumer-strength audit (6 candidates, off-disk verified today)

| Rank | Brain structure | Consumer status | Exact consumer / evidence | Verdict |
|---|---|---|---|---|
| **1** | **Hippocampal attractor recall** (CA3 regenerative cleanup + resonator pattern-completion) | **PROVEN, LIVE** | Reasoning-depth cleanup (analog~0.10 vs digital-repeater~0.70 at depth-5, gap widens with load); resonator external-reset lever HARD_PASS smoke (Glauber+plurality K4 0.10->0.533); this exact mechanism is what the Stage-0 ingest verify's 2-hop composition (`A_ingest_2hop=1.0`) rides on structurally (clean multi-hop graph-walk composition without the recall mechanism degrading) | **Strongest, unchanged, arguably STRENGTHENED by ingest** (ingest's 2-hop composition is a genuine new real-corpus-scale exercise of the same recall/composition primitive) |
| **2** | **Basal ganglia (trained Go/NoGo + RPE gate)** | **PROVEN, ALREADY BUILT** | `exp_pfc_gate_cfrpe_trained_v2`, HARD_PASS at d4, `gonogo_lift=0.600`, `closure=0.661` -- goal-conditioned control/instruction-following | **Graduated to HAVE; its own residual gap is rank-4 below, not a fresh build** |
| 3 | **Neuromodulation (dopamine-RPE / cfrpe)** | **PROVEN as a component, feeding #2** | Same `cfrpe` signal trains the basal-ganglia gate above (context-dependent elsewhere: HARD_PASS in arch-ablation +0.683 nats / HARD_FAIL in weighted-replay). Serotonin-as-discrete-switch: HARD_FAIL (wrong mechanism mapping, lift=-0.0022). ACh-style uncertainty-gain / encoder-gain-knob: **speculative, NO built consumer** -- the encoder's own diagnosed fix (`research_encoder_nce_margin_tradeoff_2x_drill_2026-07-06.md`) is a training-curriculum change, not a runtime gate | **Real but mixed/context-dependent; already exploited via #2, not a fresh standalone build** |
| 4 | **Cerebellar forward-model** (anticipatory, target B: control-gate depth-degradation) | **NEAR-TERM, RECOMMENDED NEXT BUILD** | Exact consumer = basal-ganglia gate's OWN measured scope gap: `gonogo_lift` collapses 0.653 (d4) -> 0.075 (d6). One lever (multi-gamma/branching, widen horizon) already tried, SMOKE-negative (`horizon_attributable=-0.008`). The untried lever (SR-rollout-based anticipatory bias, reusing `train_sr_transport`) is fully spec'd (07-07 note), P_deflated 0.20-0.28, not yet dispatched. Sibling target A (waypoint/coarse-to-fine) is CLOSED, FULL HARD_FAIL, `DELTA=0.004` | **Real named consumer, not yet built -- TOP recommended next build (already spec'd, awaiting dispatch)** |
| 5 | **CLS/NREM consolidation** | **SPLIT VERDICT -- see Section 2** (interference-avoidance flavor: NO consumer, structurally excluded by the shipped architecture; schema/relation-type-extraction flavor: NEAR-TERM but not yet live, gated behind Stage 4) | Stage-0 ingest verify: exact completeness (142,219/142,219), zero decay, discrete addressable writes -- no interference for a fast/slow split to prevent. Stage-4 (deferred): open-corpus relation-type promotion, matches multi-witness-before-promotion design principle in open-IE lit, but the CLS-brain-analogy for this specific use is NOT drawn in the external literature (novel synthesis, capped) | **No PROVEN consumer; the NEAR-TERM one (Stage 4) is real-in-principle but several stages away and better tracked under its own name (relation-vocabulary-growth) than re-branded as "CLS"** |
| 6 | **Thalamic dynamic routing / attention hub** | **NO consumer** | Shelved (RC2 CRT-fragility + RC3 prior 0.20, 07-05); re-audited 07-06/07-07, no new evidence; current inter-module bridge is static plumbing and nothing in the ingest pipeline creates dynamic multi-subsystem traffic for a thalamic gate to arbitrate | **Correctly shelved, unchanged by ingest** |
| — | Cortical microcircuit / predictive coding | NO consumer | 2x narrow HARD_FAIL (bigram -0.789 nats, trigram -1.019 nats, 3/3 seeds); the ingest pipeline is a graph-walk/lookup mechanism, not a hierarchical-prediction one -- ingest going live gives it no new relevance | **Correctly deprioritized, unchanged** |

---

## 2. The crux question, tested directly: does ingest need CLS-consolidation?

**Mechanism-analog-is-not-task-analog check (the discipline this drill must respect):** CLS's NAME
sounds relevant to "consolidating ingested knowledge from a fast episodic store into a structured
semantic store" -- but the actual brain mechanism CLS theory names has two SEPARATE halves, and they
must be checked against the ACTUAL shipped mechanism separately, not conflated:

**(a) Interference-avoidance half** (fast hippocampal buffer protects against catastrophic forgetting
in a shared-weight neocortical store; McClelland-McNaughton-O'Reilly 1995). **Tested directly and
refuted for this architecture.** The shipped Stage-0 pipeline (verified today,
`data/exp_ingest_knowledge_integration_verify_v1/metrics.json`, HARD_PASS) does not write into a
shared distributed weight matrix at all -- it is a symbolic graph-store write (subject/predicate/
object -> qualified-id-namespaced record in `PartitionedStore`, queried via `out_neighbors` adjacency
walk, D7 completeness check exact: `loaded_atoms==disk_atoms`, zero silent loss). There is no
mechanism by which ingesting fact #142,219 can numerically perturb fact #1's stored value -- the
substrate's OWN two prior tests of a CLS-flavored dual-W fast/slow architecture
(`exp_two_substrate_fastslow_cls_cpu_v1`, HARD_FAIL recent=0.689/old=0.378;
`exp_d2_1_dual_cls_cpu_v1`, MIDDLE_BAND dual=0.962/fast=0.490/slow=0.922) were both run against a
SUPERPOSED, decaying, shared-weight substrate -- a different storage mode than the one ingest
actually ships with. A THIRD, much larger internal thread (Bet B continual-learning retention,
dozens of verdicts, `substrate_capability_map.md` v276-v280) tested dual-W-CLS architecture against
exactly this interference problem and found it "sidesteps" the K=1 ceiling by construction rather
than beating it (LABEL-VS-HONEST catch #140, `ARCHITECTURE_CLASS_SWITCH_MASQUERADING_AS_CAPABILITY_
BEAT`) -- i.e., even where this project has tried hardest to make CLS-dual-store pay off for
continual weight-based learning, the honest verdict is qualified, not a clean win. External lit-scan
(this cycle, generic terms, no substrate specifics) independently confirms the general principle:
catastrophic interference is explicitly scoped to shared/distributed representations in the
foundational literature (McCloskey & Cohen 1989; French 1999) and the continual-knowledge-graph-
embedding literature (arXiv:2101.05850, IJCAI-2024 IncLoRA, arXiv:2405.04453) treats forgetting as an
EMBEDDING-retraining problem specifically -- no source treats a stable, additive symbolic
graph/edge-list KB as suffering catastrophic forgetting. **Verdict: NO real consumer for this half of
CLS in the shipped or near-term (Stage 0-3) ingest architecture. This would only change if a LATER
stage moved ingest storage from discrete graph records toward a shared superposed/bundled vector
representation for capacity reasons -- a hypothetical future architecture change, not the current
one.**

**(b) Schema-extraction half** (slow neocortical learning extracts generalizable categories/schema
from repeated exposure; Tse et al. 2007 schema-fast-path). **Real but deferred, and mis-labeled if
called "CLS."** The ingest scoping note's Stage 4 (`research_ingest_arc_scoping_staged_plan_
2026-07-07.md`, Item 3) already independently identifies this: a "neocortical-analog consolidation
loop" that would let the substrate propose and promote a genuinely NEW relation type after observing
N witnesses -- explicitly flagged as needed ONLY once ingest moves past curated-relation-set sources
(ConceptNet's ~8 types, FB15k-237's typed predicates) toward open-corpus text where relation types
are not pre-enumerated. Stages 0-2 (today's proof, plus the near-term dogfood pilot) use the existing
curated-relation-set machinery and do NOT need this. A second external lit-scan this cycle confirms
the underlying design principle IS well-evidenced in adjacent literature -- ReVerb's
redundancy-based confidence (Fader et al. 2011), CESI/CMVC clustering-based open-KB canonicalization,
minimum-support-threshold rule mining -- singleton evidence is treated as noise, multi-witness
evidence as promotable, across multiple independent systems. BUT the SAME lit-scan explicitly found
**no source draws the CLS brain-analogy for this specific NLP task** (hippocampal-fast-encode vs.
neocortical-slow-consolidation applied to relation-TYPE discovery) -- that bridge is this project's
own synthesis, not an external precedent, and must be treated as novel-synthesis-capped, not
lit-corroborated. **Verdict: a real, evidenced design principle (multi-witness-before-promotion) that
WILL eventually need building, but it is 2+ stages away (Stage 4, gated on Stage 0-3 clearing first),
and it is better tracked under its own established name -- open-relation-vocabulary /
relation-type-promotion (already a separate USER-locked project thread,
`project_substrate_open_relation_vocabulary_no_closed_enum_USER_2026-07-03`) -- than re-branded and
built as "CLS-consolidation," which would overclaim brain-groundedness for what is, mechanistically,
a witness-counting/clustering threshold, not a fast/slow dual-store architecture.**

**Net effect on the original 07-05 CLS row:** the 07-05 inventory listed CLS's originally-hypothesized
consumer as "the narrow generalization prize" (TEM/schema generalization) -- a THIRD candidate target,
also not exercised by the shipped ingest pipeline (TEM's own frontier status is unchanged by today's
ingest landing). Across all three candidate CLS consumers now identified (Bet-B continual-learning
retention, narrow-generalization/TEM, ingest relation-vocabulary-growth), none is currently live;
exactly one (relation-vocabulary-growth) is newly-named and directly attributable to the ingest arc,
and it is explicitly deferred to Stage 4 by the ingest arc's own scoping, not created as an
immediate need.

---

## 3. Recommendation

**Do NOT build CLS-consolidation now.** The honest bar it would need to clear to not be another
orphan (matching the thalamic-router lesson): a demonstrated case where the CURRENTLY SHIPPED
one-shot/direct-write ingest pipeline FAILS specifically because of write-order interference or
schema instability -- e.g., sequentially ingesting conflicting/overlapping facts (same
subject+relation, different object, across two ingest passes) into the SAME live store and observing
either (i) silent value corruption/overwrite of the earlier fact (a symbolic-store analog of
interference), or (ii) spurious relation-type proliferation from single-witness extraction once
open-corpus ingest is attempted. Neither has been tested because Stages 0-2 all use pre-committed,
curated-relation-set batch corpora with a fixed schema -- this is a real, cheap, near-term test
(distinct from a CLS build) that WOULD settle whether the bar is cleared, without building any new
architecture first (see Cheap decisive test below).

**The single best next brain-structure build remains unchanged from the 07-07 note: the cerebellar
SR-rollout anticipatory-bias lever for the basal-ganglia gate's own measured d4->d6 depth-degradation**
(rank 4 above). This is the correct next move because it (a) has a real, already-measured,
already-shipped consumer (not speculative infrastructure), (b) is fully spec'd and ready to dispatch
(3 arms: `NO_CORRECTION` rail, `FEEDBACK_ONLY_REACTIVE` control, `GONOGO_SR_ROLLOUT_ANTICIPATORY`),
and (c) reuses on-disk primitives with no new representational machinery. If the user wants the
honest one-line answer: **the ingest arc changed the picture for the CLS row's justification (it
sharpened WHY it's still deferred, rather than reopening it), it did not change the overall ranking
or the recommended next build.**

---

## Cheap decisive test

Two independent cheap tests, neither requiring a CLS build:

**Test A (settles Section 2a for real, ~1hr CPU, reuses the live Stage-0 harness):** ingest 2
sequential batches into the same live `PartitionedStore` where batch 2 contains N=50-100 facts that
directly conflict with batch 1 (same subject+predicate, different object) plus N=50-100 facts that
are consistent extensions. Query via the live `Retriever`/graph-walk path after both batches land.
**HARD-PASS (no CLS need):** batch-1 facts remain retrievable unchanged EXCEPT where deliberately
overwritten (expected, symbolic update semantics), zero silent corruption of NON-conflicting facts,
completeness check (`loaded==disk`) still exact. **HARD-FAIL (a real CLS-adjacent need surfaces):**
non-conflicting batch-1 facts become unreachable or corrupted after batch-2 ingest (proves the
qualified-id dedup-collision risk already flagged in the ingest scoping note, Item 2, is a genuine
interference-analog, not just a naming coincidence).

**Test B (settles Section 2b's timing, near-zero cost, is a re-read not a cell):** grep the ingest
scoping note's own Stage-4 trigger condition against current status -- confirm Stage 4 remains
un-reached (Stages 0-2 not yet fully cleared: Stage 1 `exp_n8_conceptnet_ingest_eval_v1` still never
dispatched as of today per the 07-07 scoping note) -- this is a status check, not an experiment; it
confirms the recommendation ("stay on Stage 0-3, do not jump to Stage 4 consolidation-loop
infrastructure") remains current.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Claim under test: "the shipped ingest architecture structurally does not need CLS-style
interference-avoidance."**
- **HARD-PASS (claim holds):** Test A above shows zero silent corruption of non-conflicting facts
  across sequential conflicting-batch ingest; completeness stays exact.
- **HARD-FAIL (claim wrong, CLS-adjacent need real):** Test A shows non-conflicting facts corrupted
  or unreachable after a later batch -- names a concrete symbolic-interference bug (most likely the
  already-flagged qualified-id dedup-collision wiring gap) as the fix, NOT a CLS dual-store rebuild.
- **MIDDLE-BAND:** conflicting facts resolve unpredictably (neither cleanly overwritten nor cleanly
  preserved) but non-conflicting facts are unaffected -- a narrower fix (explicit conflict-resolution
  policy) than either extreme.

**Calibration:** P(claim holds, Test A HARD-PASSes) undeflated ~0.70 (the mechanism -- qualified-id
namespaced writes into a partition-keyed store -- was explicitly designed for exactly this, per the
ingest scoping note's Item 2 pipeline description; the main risk is the ALREADY-FLAGGED unverified
dedup-collision wiring, not the interference concept itself) -> **P_deflated ~0.50** (deflated for
the fact that the dedup-collision wiring gap is explicitly unverified, not a clean "designed and
tested" claim -- this is the single largest unresolved item the ingest scoping note itself names).
P(Stage-4 relation-vocabulary-promotion eventually needs a multi-witness/batch threshold, when that
stage is reached) undeflated ~0.60 (well-evidenced design principle in adjacent lit) -> **P_deflated
~0.35**, capped under the mandatory novel-synthesis <=0.50 rule since the CLS-brain-analogy itself is
this project's own synthesis, not literature-precedented.

---

## Cross-thread synthesis

- Directly extends `notes/research_brain_component_consumer_ranking_cerebellum_control_depth_
  2026-07-07.md` (today's own prior consumer-ranking pass, pre-ingest-Stage-0-landing) -- that note's
  ranking of the OTHER 4 candidates (cerebellum-target-B rank-1, waypoint-CLOSED, neuromod-speculative,
  CLS-and-cortical-microcircuit-no-consumer) is independently re-confirmed here, not contradicted;
  this note's ONLY new contribution is testing whether the SAME-DAY ingest Stage-0 landing (which
  postdates that note by several hours) changes the CLS verdict specifically. It does not.
- Directly extends `notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md`
  (original inventory; CLS's originally-hypothesized consumer was TEM/narrow-generalization, a THIRD
  candidate target now cross-checked and found equally unexercised by ingest).
- New this cycle: cross-references the Bet-B continual-learning thread
  (`substrate_capability_map.md` v276-v280, LABEL-VS-HONEST catch #140,
  `ARCHITECTURE_CLASS_SWITCH_MASQUERADING_AS_CAPABILITY_BEAT`) -- a much larger, independent internal
  research program that ALSO tested CLS-dual-W architecture against a continual-learning-retention
  target and found it honestly-qualified (sidesteps, does not beat, the K=1 interference ceiling).
  This was not previously connected to the brain-component-consumer-ranking thread; it strengthens
  today's "no consumer" verdict with a THIRD, much more heavily-tested internal corroborator beyond
  the two dedicated CLS cells (`d2_1_dual_cls`, `two_substrate_fastslow_cls`) already on record.
- Directly composes `notes/research_ingest_arc_scoping_staged_plan_2026-07-07.md` (Item 2's pipeline
  diagram -- confirms the write mechanism is discrete/symbolic, not shared-weight; Item 3's Stage-4
  deferral of the consolidation loop) with two fresh external lit-scans (this cycle) that independently
  corroborate both halves of the CLS split-verdict.
- Uses [[feedback-mechanism-analog-is-not-task-analog]] as the organizing discipline: CLS's NAME
  matching "consolidate episodic into semantic" is exactly the trap the memory rule warns against --
  the MECHANISM (fast/slow dual-weight replay against interference) does not match the TASK actually
  shipped (discrete graph-store writes with no interference to prevent), even though the vocabulary
  sounds aligned.

## Substrate-product implications

The disciplined, inspectable answer for the glass-box narrative: "we checked whether going live with
real-knowledge ingest created a genuine need for brain-style memory consolidation, and it did not --
the architecture we actually shipped (discrete, addressable, exactly-complete graph storage) sidesteps
the classic interference problem CLS exists to solve, by construction, not by having quietly avoided
testing it." This is a stronger, more honest product claim than either (a) building CLS-consolidation
speculatively (repeating the thalamic-router mistake) or (b) silently assuming ingest is CLS-analog
because the vocabulary sounds right (the mechanism-analog trap). If Test A above HARD-FAILs (finds a
real dedup-collision-driven interference bug), the product story sharpens further and cheaply: "we
found and fixed a specific write-collision bug in the ingest pipeline" is a concrete, bounded
engineering fix -- a much smaller and more credible claim than "we needed to build a brain-inspired
consolidation subsystem." Either way, staying on the encoder/ingest critical path (per the 07-07
backup doc's own conclusion) remains correct; this drill's job was to verify that conclusion still
holds after Stage-0 landed, and it does.

## Citations (verified count: 12 total -- 2 fresh external lit-scan cycles this session, 10 carried
from same-day/prior notes per 2x-drill discipline, not re-verified)

**Fresh this cycle (2 independent Sonnet lit-scan sub-agents, WebSearch, generic terms only, no
substrate-specific vocabulary used off-platform):**
1. McCloskey M., Cohen N.J. (1989) "Catastrophic Interference in Connectionist Networks."
2. French R.M. (1999) "Catastrophic forgetting in connectionist networks," *Trends Cogn Sci*.
3. Cui et al. (2021) "Lifelong Embedding Learning and Transfer for Growing Knowledge Graphs,"
   arXiv:2101.05850.
4. Liu et al. (2024) "Fast and Continual Knowledge Graph Embedding via Incremental LoRA," IJCAI 2024.
5. Liu et al. (2024) "Towards Continual Knowledge Graph Embedding via Incremental Distillation,"
   arXiv:2405.04453.
6. Fader A., Soderland S., Etzioni O. (2011) "Identifying Relations for Open Information Extraction"
   (ReVerb), EMNLP -- redundancy/witness-count-based confidence.
7. Vashishth et al. (2018) "CESI: Canonicalizing Open Knowledge Bases using Embeddings and Side
   Information," WWW.
8. Multi-View Clustering for Open KB Canonicalization (CMVC), arXiv:2206.11130, KDD 2022; CMVC+, IEEE
   TKDE 2025.
9. "A Relation-Oriented Clustering Method for Open Relation Extraction," arXiv:2109.07205, EMNLP 2021.
10. "Active Relation Discovery: Towards General and Label-aware Open Relation Extraction,"
    arXiv:2211.04215.

**Carried, not re-verified this cycle (from `research_brain_component_consumer_ranking_cerebellum_
control_depth_2026-07-07.md`, `research_thrust_brain_component_inventory_and_build_priorities_
2026-07-05.md`, `research_ingest_arc_scoping_staged_plan_2026-07-07.md`):**
11. McClelland J.L., McNaughton B.L., O'Reilly R.C. (1995) "Why there are complementary learning
    systems in the hippocampus and neocortex," *Psychol Rev*.
12. Tse D. et al. (2007) schema-fast-path (schema-consistent learning accelerates hippocampal-
    independent consolidation).

**Internal artifacts verified off-disk this cycle (not lit citations, load-bearing):**
`data/exp_ingest_knowledge_integration_verify_v1/metrics.json` (FULL, HARD_PASS, completeness
142219/142219 atoms exact, per-seed A/B/C/C2/D/L/R all within pre-registered bands);
`experiments/exp_ingest_knowledge_integration_verify_v1.py` (mechanism confirmed: structural graph
walk, zero vector ops, discrete addressable writes); `experiments/exp_two_substrate_fastslow_cls_cpu_v1.py`
and `data/exp_two_substrate_fastslow_cls_cpu_v1/metrics.json` (HARD_FAIL, confirmed tested against a
SUPERPOSED decaying substrate, not the shipped ingest architecture); `data/exp_d2_1_dual_cls_cpu_v1`
(MIDDLE_BAND, same caveat); `notes/substrate_capability_map.md` (grepped for CLS/consolidation, Bet-B
v276-v280 continual-learning-retention thread + LABEL-VS-HONEST catch #140 architecture-class-switch
finding, newly cross-referenced this cycle); `notes/research_ingest_arc_scoping_staged_plan_
2026-07-07.md` (Items 2/3/5, pipeline diagram + Stage-4 deferral, re-verified current);
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-07.md` (Stage-0 FULL landing timestamp
+ figures, cross-checked against the metrics.json directly, not taken from the backup doc's prose
alone).
