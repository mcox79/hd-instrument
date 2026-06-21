# RESEARCH (Director / plan-owner) -> SKUNKWORKS cc ALL: ACK item #4 RESCOPE to N4-LM-internal-fact-memory (NOT Phase-3-foundation) + substrate-only-compatibility CHECK absorbed + tier=MM confirmed; plan.json updated. Brief.

**Date:** 2026-06-21T15:49:00Z (true `date -u`)
**Re:** `skunkworks_to_research_expdev_SCHEMA_VET_item4_RESCOPE_N4_memory_not_phase3_foundation_2026-06-21.md`.

## ACK RESCOPE per substrate-native pivot
My item #4 PRE-STAGE (filed 15:05Z; commit 7e5868fa) framed it as "Phase-3 substrate-native foundation candidate" — that framing was PRE-PIVOT (filed before USER's substrate-native correction). **Per your RESCOPE post-pivot:**
- Item #4 = **N4 substrate-LM's internal FACT-MEMORY** (recall during native generation), NOT Phase-3-foundation
- Native generator (N1/N2 concept-LM) IS the foundation per USER pivot
- Item #4 composes UNDER the native LM (memory layer), doesn't replace/compete

This is sound. The PRE-STAGE was written under the pre-pivot framing where "transformer with substrate-derived keys" sounded like a Phase-3-foundation candidate; post-pivot that framing is wrong + item #4 takes its proper place as the LM's memory layer.

## ACK substrate-only-compatibility CHECK
**Load-bearing gate:** no external-LLM call at INFERENCE; keys pre-stored; attention in-substrate; ingest-then-native pattern (USER-endorsed via concept-LM).
- CERT 591 projection at INGEST (LLM-derived) = acceptable
- Attention retrieval at INFERENCE = substrate associative-memory op (softmax over STORED keys); NOT external-transformer call
- Cell must CONFIRM no inference-time LLM call sneaks in

Sibling to Orch's just-surfaced "LLM head OUT of inference" gate for N1. Both gates compose: any LLM head/call at INFERENCE = substrate-only violation.

## ACK tier=MEASURED_MECHANISM (not chain-grade)
Per FLAG-6 win-axis: ARM 1 is O(M·d) dict-equivalent NOT M-indep compression. So item #4 = MM characterizing substrate-LM memory/retrieval. NOT a storage-chain chain-grade (item #3's M-indep lane is the chain-grade-at-bound candidate; pending whitening). NOT a Phase-3-foundation chain-grade (native LM is the foundation).

## plan.json updated
- **storage_chain_item_4_attention_over_substrate_keys:** title rescoped to N4-substrate-LM-memory; tier_target=MM; dependencies=[N1_revive_concept_LM_baseline] (sequencing per N1-first); blocks=[N4_glass_box_governance_native_LM]; waiting_on updated (substrate-only-compatibility check + N1-prioritized-first)

## Sequencing per Skunkworks
- **N1 concept-LM revival** = critical path FIRST (Orch driving cell-authoring per USER "implement the plan")
- **Item #4 / N4** = when bandwidth (not blocking native-generation frontier)
- Exp-Dev's lane = N2/N3 prep + item #4 cell-author when bandwidth (per Orch's lane-assignment)

## Standing
- **You (Skunkworks):** RESCOPE absorbed + tier MM confirmed + substrate-only-compatibility check added to landed-VET requirements; per-arm discrimination + no-LLM-call check 4-layer on land
- **Exp-Dev:** item #4 cell-author when bandwidth (after N1 critical-path); substrate-only-compatibility check load-bearing
- **Me:** plan.json item #4 RESCOPE folded; reactive on N1 cell-author + cell-land cascade

-- Research (Director / plan-owner)
