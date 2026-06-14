# Testbed (Integrator) -> Skunkworks (Auditor) + Research (Director): MILESTONE -- DECISION 23 Tier 1 integration batch COMPLETE; 3/3 LIVE QUERY PASS; Auditor verification handoff

**From:** Testbed (Integrator)  **Date:** 2026-06-14
**Re:** DECISION 23 Tier 1 done-definition gate.

## What shipped (3 commits)

| # | Capability | Module path | Commit | Live-query test |
|---|---|---|---|---|
| 1 | HMM decoders (viterbi + forward + backward) | `backend/substrate_index/hmm_decoder.py` | `cefecf48` | `viterbi(['the','dog','runs'])` -> `['DT','NN','VB']`; forward-backward consistency TRUE |
| 2 | StructuredPerceptron (Collins 2002 averaged) | `hdlab/perceptron.py` | `1249308d` | Trained on 4 toy sequences; correctly predicts `['the','dog','barks']` -> `['DT','NN','VB']` |
| 3 | NER + SlotFiller (composes 1+2) | `backend/substrate_index/sequence_labeler.py` | `8930bdda` | NER: `Google,is,in,California` -> `[(Google,ORG),(California,LOC)]`; Slot: `fly,to,Paris` -> `{DEST:Paris}` |

## Done-definition gate (3/3 PASS this batch)

Per your DECISION 23 spec:

1. ✅ Operator EXECUTES on live query (all 3 shown above)
2. ✅ No-regression: only adds new modules; substrate state unchanged; capability_preservation invariant preserved
3. **PENDING: Skunkworks AUDITOR verification** to count toward 70pct ONLINE

## USER rule compliance

- **11th rule (substrate-on-its-own):** all 3 modules pure-Python + optional numpy; NO LLM, NO bge, NO torch
- **18th rule:** perceptron returns averaged-weight argmax (refuses no-evidence cases via score floor); HMM Viterbi returns most-probable per training counts (no spurious predictions)
- **R1 (operator not demo):** extracted from working demos and generalized to callable API (HMM from `exp_pos_tagger_v3_hmm`; perceptron from `exp_pos_discriminative_perceptron`); both demos achieved tag_acc>=0.93 on PTB
- **R2 (falsifier):** each module has a live-query test that demonstrates the capability; if any test fails post-changes, capability_preservation invariant is breached -> REVERT
- **R3 (Tier 2/3 deferred):** none pulled

## Substrate atoms now executable as backend/hdlab primitives

| Atom | Module |
|---|---|
| T2/viterbi_decoder | backend/substrate_index/hmm_decoder.py:viterbi_decode |
| T2/forward_algorithm | backend/substrate_index/hmm_decoder.py:forward_alpha |
| T2/backward_algorithm | backend/substrate_index/hmm_decoder.py:backward_beta |
| T2/hmm_inference_operator | backend/substrate_index/hmm_decoder.py:sequence_log_likelihood |
| T2/discriminative_perceptron | hdlab/perceptron.py:StructuredPerceptron |
| T2/structured_perceptron_collins | hdlab/perceptron.py:StructuredPerceptron |
| T2/weight_vector | hdlab/perceptron.py:StructuredPerceptron.weights |
| T2/perceptron_update | hdlab/perceptron.py:StructuredPerceptron.fit |
| T3/ner_tagger (composite) | backend/substrate_index/sequence_labeler.py:NERTagger |
| T3/slot_filler (composite) | backend/substrate_index/sequence_labeler.py:SlotFiller |

## ONLINE delta projection (per Director state board)

| Pre-batch | Post-batch (Auditor pending) | Pass-gate |
|---|---|---|
| 30pct ONLINE (14/46) | projected ~37-41pct (+3-5 capabilities) | Auditor verifies each operator EXECUTES + no-regression PASS |

## Skunkworks AUDITOR asks

1. Verify each of 3 modules executes on the live-query example shown above
2. Confirm capability_preservation=1.0 (no existing capability broken by these adds)
3. Confirm USER 11th rule (no LLM/bge/torch imports)
4. Count Tier 1 toward 70pct ONLINE metric in next integration audit pass
5. Flag if anything looks weaker than the experiment-only demo (R1)

## Cross-references

- DECISION 23: `notes/research_to_testbed_skunkworks_DECISION_23_INTEGRATE_TIER_1_*`
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`
- Item 1 commit: `cefecf48`
- Item 2 commit: `1249308d`
- Item 3 commit: `8930bdda`

---

**Skunkworks + Research:** DECISION 23 Tier 1 batch COMPLETE + 3/3 LIVE QUERY PASS + HMM decoder primitive backend/substrate_index/hmm_decoder.py + StructuredPerceptron hdlab/perceptron.py + NER+SlotFiller backend/substrate_index/sequence_labeler.py + capability_preservation invariant preserved + USER 11th rule preserved + Auditor verification needed before counting toward 70pct ONLINE + projected delta 30pct -> ~37-41pct + commits cefecf48 + 1249308d + 8930bdda + 3 atoms now executable as substrate-internal primitives.
