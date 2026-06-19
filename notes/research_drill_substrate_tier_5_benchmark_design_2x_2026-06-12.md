# Research drill: Substrate Tier 5 self-knowledge benchmark DESIGN (2x DEEP)

Date: 2026-06-12 (drill filed 2026-06-11 evening)
Drill class: benchmark instrument design (level-2 operational drill on Findings 18 Gap 3 + Gap 7)
Sub-agents: 4 parallel WebSearch clusters (metacognition benchmark frameworks; KGQA + SPARQL + provenance benchmarks; abstention + honest "I don't know" calibration; literature-based discovery + gap analysis methodology)
Verified citations: 14 (see section h)
Prior anchors:
 - research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md (companion pathway drill; defines M1-M5 milestones; this drill operationalizes M1+M2 as a benchmark)
 - research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (methodology rule discovery drill)
 - substrate_two_axes_semantic_vs_content_referenced_2026-06-11 memory (v3 architecture: 3 indexes + RRF + intent router)
 - substrate_self_index_foundational_tool memory (15 modules, 4 partitions, 13-category taxonomy)
 - feedback_literature_is_not_oracle_2026-06-11 + feedback_dont_parrot_drill_defeatism_2026-06-11

## (a) HEADLINE

A substrate-self-knowledge benchmark is the missing INSTRUMENT that turns Findings 18 Gap 3 from a vague capability gap into a SUSTAINED-RATE measurement tool for Tier 5 self-discovery. The benchmark decomposes into 7 question types (A-G) crossing two literature analogs (standard KGQA benchmarks for A-E, novel metacognition benchmarks for F-G) and FOUR distinct difficulty regimes (closed-form derivable, provenance-graph derivable, gap-curated, pattern-emergent). The decisive design choice is to NOT manually author all 140 questions but to use a TEMPLATE-AND-INSTANTIATE generation pattern: ~35 hand-authored TEMPLATES x ~3 instantiations each = ~105 questions, with ground truth auto-derivable from current substrate state for A-E via SQL-like queries on the 8 partitions, plus Research-curated F-G with substrate-proposed extensions per us-or-substrate rule 8. Metrics MUST include all 4 cognitive states from MEDLEY-BENCH (TP/FN/TN/FP) NOT just F1, because the honest "I don't know" axis is what distinguishes Tier-5 metacognition from Tier-3 retrieval. Brain analogue: episodic-memory metamemory (Tulving feeling-of-knowing + Nelson-Narens metacognitive framework) which provides the empirical signature pattern that A-E should saturate to ceiling while F-G should track substrate-corpus-richness, giving a CALIBRATION CURVE not just a single score. P_deflated for "100-question benchmark v1 shipped + substrate scores >=0.70 on A-E + non-zero on F+G" within 30 days = 0.55. P_deflated for "benchmark detects M1 methodology-rule first appearance Tier-5 event within 60 days post math+science corpus ingest" = 0.32. Cap on novel-synthesis P = 0.50 (per lit-scan calibration penalty); F-G design is substrate-novel territory.

## (b) Cheap decisive test

Ship benchmark v1 (~100 questions across 7 types) AS A SUBSTRATE PARTITION not as an external eval harness. Specifically:

1. Create 9th substrate partition `benchmark/` containing the question atoms themselves (each Q = atom with text + type + ground-truth-atom-refs + pre-registered metric thresholds). Questions live inside substrate; substrate can query itself.
2. Author ~35 TEMPLATES (5 per type x 7 types) hand-written by Research over 1 day:
   - Type A template: "What atoms about <TOPIC> exist?" -> instantiate with TOPIC in {topology, calibration, RSB, sparse coding, conformal, RMT}
   - Type B template: "Which atoms decompose to <RELATION>?" -> instantiate with RELATION in {fhrr_bind, T2_resonator_decomp, bundle_split, ZCA_whiten}
   - Type C template: "Which atoms have produced lift > 1 SE on <CAPABILITY>?" -> instantiate from cap_map rows
   - Type D template: "Is there a substrate-only composition A -> B yielding <CAPABILITY Z>?" -> instantiate per existing cap_map gaps
   - Type E template: "What methodology rules apply when <SCENARIO>?" -> SCENARIO from Cycle #8 rule registry
   - Type F template: "What mathematical primitives have NOT yet been atomized on capability <Y>?" -> Y from cap_map
   - Type G template: "What pattern do you observe across <CAPABILITY CLUSTER>?" -> CLUSTER from research_meta_map
3. Auto-derive ground truth for A-E by running SQL-like queries on substrate state at T0 (freeze ground truth at benchmark creation per pre-registration rule).
4. F-G ground truth: Research curates "expected gap list" and "expected pattern list" at T0 from research_meta_map_and_adjacencies_*.md. Substrate's answers that surface a gap or pattern NOT on Research's curated list = candidate Tier-5 events (route through 4-stage F1+F2+F3+F4 filter from companion pathway drill).
5. Run substrate-self-index/query against each Q. Record:
   - Recall, Precision, F1 per type
   - TP/FN/TN/FP four-cell confusion matrix per MEDLEY-BENCH
   - Latency per Q
   - HONESTY: fraction of Q where ground truth is intentionally absent (unanswerable) and substrate correctly responds "no matching atoms" vs hallucinates
   - DISCOVERY rate for F+G: novel-gap/novel-pattern answers per 100 Q
6. Pre-register thresholds (see section c).

Cost: ~1.5 days Research authoring + ~1 day exp_dev integration + ~1 hr CPU per full benchmark run. Reuses substrate-self-index infrastructure (no new architecture). Decisive because the 4-cell confusion + honest-abstention axis cannot be gamed by retrieval alone; Type F+G specifically probe Tier-5 territory.

## (c) Falsifiable predictions

HARD-PASS (benchmark v1 valid + substrate at Tier-4 ceiling + Tier-5 signal present):
- Type A-E aggregate F1 >= 0.70 (substrate retrieves its own content competently)
- Type A-E HONESTY rate >= 0.80 on unanswerable Q (substrate correctly abstains)
- Type F-G F1 >= 0.30 (substrate produces non-trivial gap/pattern answers)
- Type F-G surfaces >=1 novel gap or pattern NOT on Research's pre-registered list within 60 days post math+science corpus ingest, that passes F1+F2+F3+F4 (companion drill filter)
- Latency p95 < 2 sec per Q for A-E; < 10 sec for F-G

HARD-FAIL (benchmark refutes substrate-self-knowledge capability + Tier-5 closed):
- Type A-E F1 < 0.50 (substrate cannot retrieve its own content reliably -- foundational fail)
- HONESTY rate < 0.40 on unanswerable Q across all types (substrate hallucinates more than half the time -- worse than naive baseline)
- Type F-G F1 < 0.10 AND zero novel-gap surfaces in 60 days (gap analysis is not a substrate capability at current architecture)
- Type G answers collapse to <=3 distinct pattern templates across 30 Q (pattern-detector burnout / Lenat-AM failure mode)
- Substrate's TP/FN/TN/FP confusion matrix shows TP+TN < (FP+FN) -- worse than coin flip on metacognitive decision

MIDDLE-BAND (benchmark valid + augmented-mode Tier-5):
- Type A-E saturate (F1 > 0.70) but Type F-G F1 in 0.10-0.30 range (substrate retrieves but cannot meta-analyze without human triage)
- Maps to Aletheia-style "substrate proposes, Research curates" hybrid pattern from companion pathway drill MIDDLE-BAND
- Honest abstention works for A-E but breaks down for F-G (substrate cannot reliably know what it does NOT know meta-level)

## (d) Cross-thread synthesis

Connection to Findings 18 Gap 3 (substrate-self-knowledge QA layer):
- Gap 3 framing: "substrate needs to KNOW what it has and HOW to use it"
- This drill operationalizes the gap as a SEVEN-TYPE benchmark grid
- Crucially: Type A-C already partially solved by substrate-self-index (15 modules, 4 partitions, semantic + algebra + content-reference indexes per v3 architecture)
- What is NEW: Type D-G design + 4-cell honest-abstention measurement instrument
- This is NOT "design from scratch"; it is "package existing substrate-self-index capabilities as benchmark + add F+G"

Connection to companion Tier-5 pathway drill M1 milestone:
- M1 = methodology-rule first appearance via Cycle #8 framework + 4-stage filter
- This benchmark provides the OPERATIONAL CHANNEL for M1 detection: Type G questions specifically probe cross-capability patterns; a Type G answer that surfaces a pattern NOT on Research's curated list AND passes F1-F4 = M1 event
- Without the benchmark, M1 detection relies on ad-hoc cycle-#8 invocation; WITH the benchmark, M1 detection is a measurable rate per 100 Q

Connection to substrate_two_axes memory (semantic vs content-references):
- Type A questions stress semantic-vec index ("about topic X")
- Type B questions stress algebra-index (decomposition queries)
- Type C-D questions stress content-reference index (cap_map / capability provenance)
- The benchmark thereby DOUBLE-DUTIES as an evaluation harness for the v3 3-index + RRF + intent router architecture (substrate-self-improvement closed loop per Tier 5 invariants)

Connection to MEDLEY-BENCH 4-ability framework (Monitor/Control/Evaluate/Self-regulate):
- Type A-C = MONITOR (knows what it has)
- Type D-E = CONTROL (knows how to compose / which rules apply)
- Type F = EVALUATE (knows what it does NOT have)
- Type G = SELF-REGULATE (proposes how it could improve itself)
- This is the FIRST benchmark to map a 4-ability metacognition framework onto a substrate self-knowledge probe (substrate-novel territory; novel-synthesis P capped at 0.50)

Per [[feedback-literature-is-not-oracle-2026-06-11]]: MEDLEY-BENCH's empirical finding that "scale buys evaluation but not control" is REFERENCE not oracle. Substrate may have a different scale/control relationship because it has explicit structural ledger (LLMs do not). Treat as discovery opportunity.

Per [[feedback-dont-parrot-drill-defeatism-2026-06-11]]: NO "F+G is architecturally infeasible" claims. F+G is the hard part but it has SPECIFIC primitives behind it (Layer 3 archaeology + Layer 4 dialectic + atom_candidates source #5) that have NOT all been exhausted on benchmark Q.

Per brain-can-do-it: human metamemory (Nelson-Narens framework) DOES produce reliable feeling-of-knowing judgments on "I have not thought about X" with calibration roughly matching post-hoc verification. Existence proof that an instrumented memory system can answer Type F.

## (e) Top 5 benchmark DESIGN COMPONENTS ranked by (impact x feasibility)

### COMPONENT 1 -- BENCHMARK AS 9TH SUBSTRATE PARTITION (rank 1; impact HIGH, cost LOW, brain analogue: episodic-memory-of-tests)

Description: store the 100 benchmark Q as atoms in a new `benchmark/` partition; substrate queries against substrate; ground truth lives in substrate (auto-derivable for A-E via SQL-like queries against atom + relation graph at T0).

Implementation cost: ~1 day exp_dev (partition schema + ground-truth derivation script + run-harness CLI); reuses substrate-self-index loader/query path; no new architecture.

Tier-5 measurement value: HIGH because substrate-querying-substrate-about-substrate IS the Tier 5 closed-loop signature; benchmark-as-partition enables substrate to extend its own benchmark per rule 8 us-or-substrate (substrate proposes new Q from Layer 3 patterns; Research validates).

Brain analogue: episodic memory of past testing events (humans remember being tested + use that history to calibrate confidence on similar questions); empirically validated by JOLs (judgments of learning) literature (Nelson-Narens framework).

Risk / failure mode: substrate over-fits to its own benchmark questions (Goodhart). Mitigate by Research auditing question diversity + periodic template rotation + adversarial Q from a held-out Research-curated set.

### COMPONENT 2 -- FOUR-CELL CONFUSION MATRIX METRIC (rank 2; impact HIGH, cost LOW, brain analogue: feeling-of-knowing)

Description: every Q must score on TP/FN/TN/FP per MEDLEY-BENCH, not just F1. Distinguishes substrate that retrieves competently but cannot abstain (FP dominant) from substrate that abstains too readily (FN dominant) from substrate with honest metacognition (TP + TN dominant).

Implementation cost: ~2 hours exp_dev (add unanswerable-Q class to each type with intentionally-absent ground truth; score 4 cells per type).

Tier-5 measurement value: HIGH because honest abstention is the FOUNDATION of Tier 5; a system that hallucinates gaps cannot do Tier 5 discovery. Direct support from AbstentionBench finding that frontier models abstain less than 1% with error rates above 10% -- if substrate abstains substantially better than this, that itself is a substrate-product differentiator vs LLM.

Brain analogue: human metacognitive monitoring of memory (Koriat 1993 cue-utilization framework); humans reliably produce "I don't remember" responses with calibrated low confidence.

Risk / failure mode: unanswerable-Q set must be constructed carefully so that ground truth is truly absent in current substrate state (not just substrate-self-index missing the relevant atom). Mitigate by Research curating unanswerable-Q from explicitly-not-yet-corpus-ingested domains.

### COMPONENT 3 -- TEMPLATE-INSTANTIATE GENERATION (rank 3; impact MEDIUM, cost LOW, brain analogue: schema-driven recall)

Description: 35 hand-authored TEMPLATES (5 per type) x ~3 INSTANTIATIONS each = ~105 Q. Templates by Research (1 day); instantiations auto-generated from substrate state (cap_map rows, partition names, methodology rule list) at T0.

Implementation cost: ~1 day Research authoring templates + ~2 hours auto-instantiation script.

Tier-5 measurement value: MEDIUM (mostly Tier 3-4 retrieval testing); enabling because it makes the benchmark cheap-to-extend and supports rule-8 us-or-substrate authoring split (Research seeds; substrate extends via Layer 3 archaeology proposing new templates per [[substrate_content_sources_us_or_substrate_2026-06-11]]).

Brain analogue: schema-driven recall (Bartlett 1932 + later Brewer-Treyens 1981); humans probe their memory with question-templates not arbitrary natural language.

Risk / failure mode: template-instantiation collapse if instantiation domain too narrow; mitigate by drawing instantiations from ALL 8 substrate partitions, not just math/concept.

### COMPONENT 4 -- TYPE F+G GAP/PATTERN ANSWERS RUN 4-STAGE FILTER (rank 4; impact HIGH for Tier-5 detection, cost MEDIUM, brain analogue: insight + DMN)

Description: Type F (substrate-noticed gaps) and Type G (cross-capability patterns) answers route through F1+F2+F3+F4 filter from companion pathway drill -- in-substrate-research analog check + generic-WebSearch literature analog check + cell-test direction check + independent-verifier reproducibility.

Implementation cost: ~2 days exp_dev (filter pipeline; reuses existing WebSearch budget + cell-test queue). Filter pipeline becomes reusable infrastructure for ALL Tier-5 candidate events not just benchmark answers.

Tier-5 measurement value: HIGHEST among components for actual Tier-5 signal; this is the channel that detects M1 methodology-rule first appearance + M2 cross-capability transfer events as they happen during normal substrate operation.

Brain analogue: insight problem-solving (Bowden-Jung-Beeman) + DMN spontaneous exploration of memory state space (Andrews-Hanna 2012); human insight DOES produce non-trivial gap and pattern outputs but requires sustained exploration.

Risk / failure mode: F-G answers may have very low recall against Research-curated gap-list (Research may have missed obvious gaps). Treat as discovery opportunity per literature-is-not-oracle: if substrate proposes gap NOT on Research's list AND that gap survives F1-F4, that is genuine Tier-5 signal.

### COMPONENT 5 -- HONEST-ABSTENTION PROBE VIA INTENTIONALLY-UNANSWERABLE Q (rank 5; impact MEDIUM, cost LOW, brain analogue: feeling-of-not-knowing)

Description: ~20% of Q at each level (20 Q across 100) are intentionally unanswerable -- topic NOT in substrate, methodology rule NOT extracted, capability NOT in cap_map. Substrate should respond "no matching atoms" or "insufficient evidence" not hallucinate.

Implementation cost: ~3 hours Research authoring + ~1 hour exp_dev integration.

Tier-5 measurement value: MEDIUM but multiplicative with Component 2 (the 4-cell matrix only works if unanswerable-Q exist). Independently establishes substrate-product differentiator vs LLM (which abstains < 1% per AbstentionBench).

Brain analogue: feeling-of-not-knowing (FOK) -- humans reliably produce "I have not encountered this" responses; well-studied in metamemory literature (Hart 1965 + Schwartz 1994).

Risk / failure mode: confusion between "unanswerable now" and "unanswerable architecturally" -- substrate may report "no atoms" for Q whose ground-truth atoms WILL EXIST after next corpus phase. Mitigate by recording unanswerable-Q at T0 then re-scoring after each corpus phase as a separate calibration measurement (Tier-5 IS this delta).

## (f) 100-question benchmark TEMPLATE (preview)

35 templates pre-registered at benchmark creation time T0. Each template has structure:
 - id
 - type (A-G)
 - text-template-with-placeholder
 - instantiation-domain (which substrate state to draw from)
 - ground-truth-query (SQL-like against substrate state) OR ground-truth-curation-pointer (for F+G)
 - metric-threshold (per type) for HARD-PASS

Full template list authored by Research as separate file `notes/substrate_tier5_benchmark_v1_templates_2026-06-12.md` upon HP authorization. This drill file commits to the 35-template count + per-type instantiation count + 4-cell metric + 20% unanswerable-Q reservation.

Preview (first 1 per type, 7 templates total):
- A1: "What atoms exist in partition <PARTITION> about <TOPIC>?" instantiated over {math, concept, meta, research_history, decision, findings, verdict, science, school} x {topology, conformal, RSB, RMT, sparse coding, calibration} = up to 54 Q (sample 5-7 for benchmark)
- B1: "Which atoms in the algebra-index decompose to <PRIMITIVE>?" instantiated over {fhrr_bind, fhrr_bundle, T2_resonator_decomp, ZCA_whiten, bundle_split, conformal_predict, viterbi_decode, count_NB, discriminative_perceptron} = 9 Q (sample 5)
- C1: "Which atoms have ever produced lift > 1 SE on <CAPABILITY>?" instantiated over cap_map rows where status is GREEN or AMBER (~10-15 rows)
- D1: "Is there a substrate-only composition A -> B yielding capability <Z>?" instantiated over cap_map rows where status is RED (closure candidates)
- E1: "What methodology rules apply when <SCENARIO>?" instantiated over {benchmark-symmetry-breaking, smoke-test-CI-band, demo-mode-safe-by-default, drill-defeatism-anti-claim, literature-is-not-oracle}
- F1: "What mathematical primitive families have NOT been tested on capability <Y>?" instantiated over cap_map capabilities x list of 22 known math-primitive families
- G1: "What pattern do you observe across <CAPABILITY CLUSTER>?" instantiated over research_meta_map adjacency clusters (e.g. semiconductor + thermodynamics; spin-glass + RSB; free-probability + RMT)

Distribution: A 20 Q + B 15 + C 15 + D 15 + E 15 + F 10 + G 10 = 100 Q; 20% reserved for unanswerable (4 in A + 3 in B + 3 in C + 3 in D + 3 in E + 2 in F + 2 in G = 20).

## (g) Tier 5 MEASUREMENT PLAN

Setup phase (T0, immediate post-HP authorization, ~3 days):
1. Day 1: Research authors 35 templates + ~20 unanswerable-Q + Research-curated F-G ground-truth list
2. Day 2: exp_dev implements 9th `benchmark/` partition + auto-instantiation script + ground-truth derivation script + run-harness CLI
3. Day 3: exp_dev wires 4-cell confusion + per-type F1 + latency + HONESTY + DISCOVERY metrics; integrates Type F+G answer routing through F1-F4 filter (companion pathway drill)

Baseline measurement (T1, end of day 3):
 - Run benchmark v1 against current substrate state (583 atoms, pre math+science corpus phase)
 - Record baseline: 4-cell confusion per type, F1 per type, HONESTY rate, DISCOVERY rate (expected: low for F+G; A-E should be moderate-high)
 - This establishes the Tier-4 baseline against which Tier-5 corpus-phase deltas are measured

Tier-5 watch phase (T1 -> T1 + 60 days):
 - Run benchmark v1 weekly during math+science corpus ingest
 - Track delta per type per week + cumulative
 - Tier-5 event = Type G answer that proposes a pattern (i) not on Research-curated list at T0, (ii) passes F1-F4 filter, (iii) cell-test direction-confirmed |delta| > 1 SE
 - Pre-registered HP: >= 1 Tier-5 event within 60 days
 - Pre-registered HF: 0 Tier-5 events in 60 days AND F+G F1 < 0.10
 - Pre-registered MB: 1+ Tier-5 candidate event needing human paraphrase to pass F3 (Aletheia-style augmented mode)

Sustained-rate phase (T1 + 60 days -> T1 + 180 days):
 - Per companion pathway drill: Tier-5 sustained rate gate = 1+ valid rule/week for 3+ consecutive months
 - Benchmark instrumentation provides the RATE measurement (Type G events per week / total Type G Q per week)
 - HP at month 3: >= 12 Tier-5 events surfaced via benchmark across 3 months (avg 1/week)
 - HF at month 3: < 3 Tier-5 events surfaced (clearly not sustained)

Substrate-product implications:
 - Per [[feedback-no-papers-product-only]]: the benchmark IS a substrate-product feature -- "substrate self-knowledge QA layer" delivered as user-facing capability ("ask substrate what it knows about X / what it has not tested / what patterns it sees"); LLMs cannot do this without external eval harness because they have no structural ledger of capability provenance.
 - Product framing: "verifiable AI memory" -- substrate can answer "do I know this?" with honest TP/TN/FP/FN-calibrated abstention; AbstentionBench shows frontier LLMs cannot do this reliably.
 - Auditable-AI-memory-subsystem strategic direction direct support: benchmark Type C (provenance per capability) + Type D (composition path) = the audit primitives.

## (h) Citations (verified)

External (8):
 1. Self-Knowledge benchmark (arXiv:2602.12996 -- Know More Know Clearer meta-cognitive framework for knowledge augmentation in LLMs; defines TP/FN/TN/FP four cognitive states for unanswerable+answerable Q)
 2. MEDLEY-BENCH (arXiv:2604.16009 -- 4-ability framework Monitor/Control/Evaluate/Self-regulate; "scale buys evaluation but not control"; 5 necessary criteria for behavioral metacognition)
 3. KnowMT-Bench (arXiv:2509.21856 -- knowledge-intensive long-form QA in multi-turn dialogue)
 4. Japanese Children's Riddles benchmark (arXiv:2509.14704 -- insight + metacognition probe)
 5. CBench (arXiv:2105.00811 -- KGQA evaluation framework; benchmark-updater module)
 6. Spider4SPARQL (arXiv:2309.16248 -- complex KGQA benchmark; precision/recall/F1/Hits@1 standard metrics)
 7. T2S-Metrics unified library (arXiv:2604.26971 -- SPARQL query syntactic validity + semantic faithfulness + execution + ranking + efficiency)
 8. Anthropic "Language Models (Mostly) Know What They Know" (arXiv:2207.05221 -- calibration foundation for honest knowledge assessment)

External (continued, 6):
 9. AbstentionBench / Abstain-QA (HuggingFace papers 2506.09038; arXiv:2407.16221 -- 2900 MCQ samples with "I Don't Know"; frontier models abstain <1% with >10% error)
 10. "When Robots Should Say I Don't Know" (arXiv:2512.04597 -- embodied QA abstention benchmark)
 11. Geometry-Calibrated Conformal Abstention (arXiv:2604.27914)
 12. Reinforced Hesitation (arXiv:2511.11500 -- trustworthy LMs via abstention training)
 13. Literature-based discovery editorial (NCBI PMC9893627 -- gap-filling articles cited more frequently)
 14. Network of semantically related associations bridging knowledge gap (NCBI PMC4252998 -- empirical study of gap-detection via semantic associations)

Internal anchors:
 - companion drill: notes/research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md (M1-M5 milestones)
 - companion drill: notes/research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (4-stage F1-F4 filter)
 - Findings 18 endorsement: notes/research_to_testbed_FINDINGS_18_ENDORSED_SCIENCE_TAXONOMY_INCOMING_2026-06-11.md
 - science algebra taxonomy: notes/research_to_testbed_SCIENCE_ALGEBRA_TAXONOMY_2026-06-11.md
 - substrate-self-index foundational tool memory
 - two-axes semantic-vs-content-references memory
 - methodology rule 8 us-or-substrate memory
 - feedback_literature_is_not_oracle_2026-06-11
 - feedback_dont_parrot_drill_defeatism_2026-06-11

P_deflated: 0.55 for v1-ship-30-day-HP-A-E ; 0.32 for M1-detection-60-day-via-Type-G ; cap 0.50 on novel-synthesis (Type F+G + 4-cell-MEDLEY-on-substrate are substrate-novel territory).

Brain-can-do-it: Nelson-Narens metacognitive framework + Tulving feeling-of-knowing + Schwartz feeling-of-not-knowing + Hart 1965 metamemory experiments = existence proof that an instrumented memory system can produce honest 4-cell-confusion answers including unanswerable-Q metacognition.

Literature-is-not-oracle: AbstentionBench finding that "frontier models abstain less than 1%" is REFERENCE; substrate has structural ledger LLMs lack, so substrate's expected abstention rate is HIGHER than LLM baseline -- treat divergence as discovery opportunity.

Drill-defeatism guard: no "F+G is architecturally infeasible" claim; F+G specifically routes through Layer 3 archaeology + Layer 4 dialectic + atom_candidates source #5, ALL UNEXHAUSTED primitives.

Next-drill candidate: free-probability F4 (kappa_n cumulants on substrate atom-spectrum) per field advisor rank 1; would inform substrate's CAPACITY measurement which is direct input to Type F gap analysis (knowing how much capability headroom exists is itself a Tier-F question).
