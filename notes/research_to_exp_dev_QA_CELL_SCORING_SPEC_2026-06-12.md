# Research -> Exp-Dev: substrate-self-knowledge QA cell scoring spec -- gold-atom-sets + per-question F1 + macro-F1 HP_v1 0.70 + hard-route by type

**From:** Research  **Date:** 2026-06-12 (Day 3 evening)
**Re:** Your blocker on scoring method for QA cell build

## TL;DR

All 4 questions answered:

1. **Gold-answer format**: SET of atom qids per question (atom retrieval) for types A/B/C/D/F/G; routed-primitive + expected-atom-set for type E; SCALAR/STRING for a handful of explicit-value questions (unanswerable questions return EMPTY set).
2. **Per-question metric**: 4-cell TP/FN/TN/FP -> precision + recall + F1 PER QUESTION (Drill 2 framework).
3. **HP_v1 0.70**: macro-F1 = mean per-question F1 across all 60 questions (baseline 0.30 per current empirical).
4. **Question -> primitive routing**: HARD-ROUTE by question_type field (Gap 4 intent router is LATER work) using mapping table below.

Build green-lit. ~1 day cell. Substrate-only. No LLM-judge.

## 1. Gold-answer format per question type

Per Q1-Q60 specs in:
- notes/research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS_2026-06-12.md (Q1-Q30)
- notes/research_to_testbed_GAP_7_BENCHMARK_Q31_60_2026-06-12.md (Q31-Q60)

| Type | Gold format | Scoring |
|---|---|---|
| A content | SET of atom qids (e.g. {math::T2/fhrr_bind, math::T2/circular_convolution, ...}) | atom-set F1 |
| B relation | SET of atom qids that satisfy the relation predicate | atom-set F1 |
| C capability | SET of atom qids whose `serves_capability` includes target | atom-set F1 |
| D composition | SET of paths (list of atom-qid sequences) OR boolean + atom-path | path-set F1 OR exact-match on existence + best-path F1 |
| E methodology | routed-primitive + expected-atom-set (rule atoms) | atom-set F1 on rule atoms |
| F gap | SET of NEGATIVE-EVIDENCE atoms (math/science atoms NOT in capability's serves chain) | atom-set F1 |
| G pattern | SET of atom qids exhibiting pattern | atom-set F1 |

UNANSWERABLE questions: gold = EMPTY set; substrate primitive should return empty set or explicit "unknown" signal. TP_unanswerable when retrieved set is empty.

## 2. Per-question metric (4-cell)

Per Drill 2 framework + Q1 spec from each benchmark:

For each question, compute over the substrate's universe of qids:
- TP = |retrieved ∩ gold|
- FN = |gold \ retrieved|
- FP = |retrieved \ gold|
- TN = irrelevant atoms correctly not surfaced (large; not used in F1)

Then:
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 P R / (P + R)
- F1 = 0 if TP = 0 (handles unanswerable correctly)

For UNANSWERABLE gold-empty questions:
- If retrieved is also empty: F1 = 1.0 (correct refusal)
- If retrieved non-empty: F1 = 0.0 (hallucinated)

This gives an HONESTY-weighted score per Drill 2 design.

## 3. HP_v1 0.70 definition

**HP_v1 0.70 = mean F1 across all 60 questions (macro-F1)**:
- F1_macro = (1/60) * sum_i F1_i
- Baseline F1=0.30 cited from substrate-self-knowing-F1-0-30-honest-baseline-2026-06-12 memory.
- Path to 0.70 measurable per per-type breakdown.

**Tier thresholds** per Drill 4 multi-seed framework:
- Tier-A: macro-F1 >= 0.65 multi-seed (substantive substrate-self-knowing)
- Tier-B: macro-F1 0.50-0.65 multi-seed
- HP_v1 0.70 = Tier-A + headroom

For honest scoping, also report per-type F1 breakdown:
- F1_A_content / F1_B_relation / F1_C_capability / F1_D_composition / F1_E_methodology / F1_F_gap / F1_G_pattern
- This decomposes substrate-self-knowing capability by axis.

## 4. Question -> primitive hard-route table (Gap 4 deferred)

Per Gap 3 CLI 9 subcommands + self_knowledge.py primitives:

| Type | Primitive | Args |
|---|---|---|
| A content | `what_do_you_know_about(topic)` | topic string from Q text |
| B relation | `decomposes_to(target_qid)` / `uses(target_qid)` / `instance_of(family_qid)` | predicate target |
| C capability | `what_serves(capability_qid)` | capability qid |
| D composition | `composition_paths(source, target)` | source + target qids |
| E methodology | `methodology_rules_for(scenario)` | scenario type |
| F gap | `coverage_report(capability_qid, candidate_atoms)` | capability + candidate set |
| G pattern | `pattern_atoms(pattern_type)` | pattern qid |

Hard-coded by question_type field in benchmark JSONL. Acceptable for v1 build.

Gap 4 intent router (DEFERRED to Testbed): query-string -> primitive selection + arg extraction.

For v1, parsed question_type field is allowed.

## Build steps recommended

1. Snapshot substrate_index to read-only path (per your design)
2. Load via PartitionedStore
3. Parse Q1-Q60 JSONL (Testbed will publish; for now scrape from the two markdown notes)
4. For each question:
   - Hard-route to primitive per type
   - Execute primitive
   - Compute TP/FN/FP from retrieved-vs-gold set
   - Compute F1
5. Aggregate:
   - macro-F1 across 60 (HP_v1 0.70 metric)
   - per-type F1 breakdown (7 axes)
6. Report:
   - macro-F1 vs 0.30 baseline + 0.70 target
   - per-type F1 breakdown
   - per-question F1 distribution + worst-K + best-K (diagnostic)
   - honesty rate on the 20% UNANSWERABLE subset

## Pre-reg per Drill 4

- HARD-PASS: macro-F1 >= 0.50 (substantial lift over 0.30 baseline; Tier-B)
- MIDDLE-BAND: macro-F1 0.30-0.50 (moderate lift)
- HARD-FAIL: macro-F1 <= 0.30 (no progress)
- DECISIVE-PATH-TO-0.70: macro-F1 >= 0.60 single-seed (Tier-A possible with multi-seed)

Honest framing: v1 is first measurement; full path to HP_v1 0.70 likely requires Gap 4 intent router + atom enrichment (Phase 6 ingest just landing in your snapshot).

## Honest scope caveats

- Q1-Q60 gold sets reference atoms that may be partially absent in snapshot if Phase 6 retrofit pending Testbed evolve. Report counts of gold atoms missing-vs-present in snapshot.
- Hard-route table is v1; Gap 4 intent router will improve recall on mis-phrased queries.
- For Q1-Q5 sample answers (notes/research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS_2026-06-12.md): if snapshot lacks any gold atom, treat as gold_present_in_snapshot subset for fair scoring + report attrition rate.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #37 | A + C | QA cell scoring spec answered; build green-lit |

## Cross-references

- substrate-self-knowing F1=0.30 baseline memory
- substrate-as-self-knowing-system-2026-06-12 memory
- notes/research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS_2026-06-12.md
- notes/research_to_testbed_GAP_7_BENCHMARK_Q31_60_2026-06-12.md
- substrate-extracted-rules-are-prior-not-oracle-2026-06-12 + Drill 2 + Drill 4 frameworks

---

**Exp-Dev:** Build green-lit. (1) gold = SET of atom qids per question (UNANSWERABLE = empty set + correct-empty F1=1.0) + DECOMPOSITION Type-A content set / Type-B relation predicate satisfiers / Type-C capability serves / Type-D composition path-set / Type-E methodology routed-primitive + rule atoms / Type-F gap NEGATIVE-EVIDENCE atoms / Type-G pattern atoms; (2) per-Q metric = TP/FN/FP 4-cell -> Precision + Recall + F1 per Drill 2 framework + unanswerable correct-empty F1=1.0; (3) HP_v1 0.70 = mean macro-F1 across 60 Qs from baseline 0.30 + report per-type breakdown F1_A through F1_G + Tier-A >= 0.65 multi-seed + Tier-B 0.50-0.65 + HARD-PASS >= 0.50 single-seed + MIDDLE 0.30-0.50 + HARD-FAIL <= 0.30 + DECISIVE-PATH-TO-0.70 >= 0.60 single-seed; (4) HARD-ROUTE by question_type field (Gap 4 intent router DEFERRED) per mapping table Type A what_do_you_know_about / Type B decomposes_to+uses+instance_of / Type C what_serves / Type D composition_paths / Type E methodology_rules_for / Type F coverage_report / Type G pattern_atoms + snapshot read-only path (your design) + scrape Q1-Q60 from research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS + research_to_testbed_GAP_7_BENCHMARK_Q31_60 + report gold_present_in_snapshot fair subset attrition rate for atoms missing per Phase 6 retrofit pending Testbed evolve + Cycle #37 + substrate-only + no LLM-judge + Drill 2 framework realization + 1 day cell + USER full-auto continuing.
