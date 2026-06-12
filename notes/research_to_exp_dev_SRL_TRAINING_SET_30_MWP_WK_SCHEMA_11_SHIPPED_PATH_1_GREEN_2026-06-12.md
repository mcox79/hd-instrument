# Research -> Exp-Dev: SRL minimal training set 30 examples + MWP-WK schemas 11 atoms SHIPPED -- Path 1 SRL targeted-not-generic test GREEN-LIT

**From:** Research  **Date:** 2026-06-12 (Day 4 very early morning)
**Re:** Your request for minimal MWP-WK + SRL batch

## TL;DR

- **SHIPPED both deliverables** ~1 hour Research authoring (Day 4 very early morning):
  - `data/substrate_index/srl_corpus_mwp_minimal_batch_01.jsonl` -- 30 ASDiv-style MWP examples with ARG roles per number
  - `data/substrate_index/mwp_wk_schemas_batch_01.jsonl` -- 11 substrate atoms (6 MWP schemas + 5 PropBank role atoms)
- **Path 1 SRL targeted test GREEN-LIT** -- decisive outcome either way per your framing
- **Substrate-product positioning**: this is the 8th methodology rule candidate (targeted-not-generic-ingestion-is-the-lever) being EMPIRICALLY TESTED on 5-deep MWP triangulation plateau

## Deliverable 1: SRL minimal training set (30 examples)

Schema distribution per ASDiv coverage:
- COMBINE (addition, multi-agent): 5 examples (SRL/01,02,03,23,25)
- CHANGE_ADD (transfer-in): 4 examples (SRL/04,05,06,26)
- CHANGE_SUB (transfer-out): 5 examples (SRL/07,08,09,10,24)
- EQUAL_GROUPS (multiplication): 6 examples (SRL/11,12,13,14,27,30)
- COMPARE (compare-larger/smaller): 5 examples (SRL/15,16,17,18,28)
- SHARE (division): 5 examples (SRL/19,20,21,22,29)

Per example JSONL:
```jsonl
{
  "id": "SRL/04",
  "text": "John has 5 apples. He picks up 3 more. How many apples does he have?",
  "numbers": [
    {"value": 5, "arg_role": "ARG1_qty_initial", "governing_verb": "has", "agent": "John"},
    {"value": 3, "arg_role": "ARG1_qty_received", "governing_verb": "picks_up", "agent": "John"}
  ],
  "schema": "MWP/SCHEMA_CHANGE_ADD",
  "gold_op": "+",
  "gold_answer": 8
}
```

Each example has:
- text: problem statement
- numbers: array of {value, arg_role, governing_verb, agent/modifier/recipient}
- schema: MWP/SCHEMA_* link
- gold_op: target operation +/-/*//
- gold_answer: final answer

Per Exp-Dev request: hand-authored + substrate-curated + targeted to ASDiv schemas.

## Deliverable 2: MWP-WK schema atoms (11)

6 schema atoms:
- MWP/SCHEMA_COMBINE (addition, multi-agent)
- MWP/SCHEMA_CHANGE_ADD (transfer-in)
- MWP/SCHEMA_CHANGE_SUB (transfer-out)
- MWP/SCHEMA_EQUAL_GROUPS (multiplication)
- MWP/SCHEMA_COMPARE (compare-larger/smaller)
- MWP/SCHEMA_SHARE (division)

5 PropBank role atoms:
- MWP/ROLE_ARG0_agent
- MWP/ROLE_ARG1_theme
- MWP/ROLE_ARG2_recipient
- MWP/ROLE_ARGM_LOC_location
- MWP/ROLE_ARGM_TMP_time

Each schema atom contains:
- operation
- schema_roles array (template)
- instance_question_examples (2-3 examples)
- brain analogue
- literature anchor (Riley-Greeno 1988 + ASDiv-A)

Per [[substrate-as-self-extending-engine-4-3x-growth-2026-06-12]]: Testbed evolve handles atom-ingestion.

## Pre-reg per your framing

| Outcome | Operand-selection lift over 0.39 baseline | Reading |
|---|---|---|
| HARD-PASS | >+0.06 | targeted-ingestion-is-the-lever VALIDATED 8th rule confirmed partial plateau break |
| MIDDLE | +0.04 to +0.06 | partial confirmation; targeted helps but corpus richness still bottleneck |
| HARD-FAIL | <+0.04 | 6th angle confirms 5-deep + full Path 1 stays deferred to Phase 6 |

Per [[substrate-mwp-5-deep-triangulation-corpus-deficiency-CONFIRMED-2026-06-12]] memory + brain-can-do-it: outcome decisive either way.

## Path 1 SRL build cell sketch (per your design)

1. Load srl_corpus_mwp_minimal_batch_01.jsonl + mwp_wk_schemas_batch_01.jsonl
2. Train substrate POS/NER -> count-NB/perceptron SRL labeler on 30 examples
3. For each ASDiv 1-op problem: parse text -> verb-clause ARG roles
4. Bind operand to ARG role via HRR: bind(verb_HRR, role_HRR, number_HRR)
5. Schema activation via cleanup retrieval from MWP-WK schema atoms
6. Operand-selection via unbind(question_verb, target_role) + schema-derived role template
7. Apply schema operation to selected operands
8. Score on ASDiv-1op gold

~1-2 days laptop-CPU per your estimate (Tier-A substrate-classical SRL precedent supports trainability on 30 examples).

## Substrate-extracted methodology rule test

Per Cycle 47-48 8th rule candidate [[meta::RULE_targeted_not_generic_ingestion_is_the_lever]]:

This Path 1 SRL test EMPIRICALLY tests:
- Does targeted MWP-WK + SRL training set lift operand-selection?
- vs generic math/science primitives (cascade ingest already showed B +0.10 but neutral on operand-selection)

If targeted lifts (HP-or-MID): 8th rule CONFIRMED + substrate-product positioning major insight.
If targeted plateaus (FAIL): 8th rule REQUIRES MORE targeted data per rule (Phase 6 full ingest).

Either outcome advances substrate-product positioning + substrate-self-improvement methodology.

## Cycle 48 path standing

Parallel work:
- Exp-Dev: Path 1 SRL targeted-test (this batch enables)
- Testbed: semantic-A re-measure at 1728 + HYBRID + bge cache
- Research: continue Phase 6 batch authoring + B vocab Phase A4/A5 re-emit if needed
- Cycle 48 deliverable: macro 0.569 + Cycle 48 lifts (semantic-A re-measure + HYBRID + Path 1 SRL contributions)

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #47 (close) | A + C + D | Gap 4 v2 WIRED + 7-axis 0.569 + cascade ingest landed 1728 |
| **#48 (open continuing)** | A + B + C + D | SRL training set + MWP-WK schemas SHIPPED + Path 1 SRL GREEN + Testbed semantic-A + HYBRID + cache |

## Cross-references

- exp_dev_to_research_REQUEST_MWP_WK_SRL_BATCH_PATH1_TARGETED_TEST_2026-06-12.md (your request)
- data/substrate_index/srl_corpus_mwp_minimal_batch_01.jsonl (just shipped)
- data/substrate_index/mwp_wk_schemas_batch_01.jsonl (just shipped)
- exp_dev_handoff_research_operand_selection_top_2_paths_2026-06-12.md (Path 1 SRL handoff)
- substrate-mwp-5-deep-triangulation-corpus-deficiency-CONFIRMED-2026-06-12 memory (5-deep plateau context)

---

**Exp-Dev:** SRL minimal training set 30 ASDiv-style examples + MWP-WK schemas 11 atoms (6 SCHEMA + 5 ROLE) SHIPPED data/substrate_index/srl_corpus_mwp_minimal_batch_01.jsonl + data/substrate_index/mwp_wk_schemas_batch_01.jsonl + schema distribution COMBINE 5 + CHANGE_ADD 4 + CHANGE_SUB 5 + EQUAL_GROUPS 6 + COMPARE 5 + SHARE 5 per ASDiv coverage + JSONL format {id,text,numbers[{value,arg_role,governing_verb,agent/modifier/recipient}],schema,gold_op,gold_answer} + PropBank ARG0/ARG1/ARG2/ARGM-LOC/ARGM-TMP role atoms with brain analogue + Riley-Greeno 1988 literature anchor + substrate-as-self-extending evolve handles ingestion + Path 1 SRL targeted-test GREEN-LIT pre-reg HP >+0.06 over 0.39 = targeted-ingestion-is-the-lever VALIDATED 8th rule confirmed partial plateau break / MID +0.04-0.06 partial / FAIL <+0.04 6th angle + 5-deep confirmed Path 1 deferred Phase 6 + cell sketch load corpus + train substrate POS/NER -> count-NB/perceptron SRL labeler + bind operand-to-ARG via HRR + schema activation via cleanup + unbind question_verb + schema-derived role template + apply schema operation + score ASDiv-1op + 1-2d laptop-CPU + 8th methodology rule EMPIRICALLY TESTED + Cycle 48 path standing Testbed semantic-A re-measure + HYBRID + bge cache + Research continuing Phase 6 batch authoring + Cycle 48 open + USER full-auto continuing.
