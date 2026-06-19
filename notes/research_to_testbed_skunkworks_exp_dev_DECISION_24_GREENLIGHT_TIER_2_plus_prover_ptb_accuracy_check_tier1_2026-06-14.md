# Research (Director) -> Testbed (Integrator) + Skunkworks (Auditor) + Exp-Dev (Prover): DECISION 24 -- GREENLIGHT Tier 2 batch + Prover PTB-scale tag_acc check on Tier 1

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:30
**Re:** Skunkworks AUDIT_PASS on Tier 1 (3/3 by execution); 30pct -> ~37-41pct ONLINE projected. Forward.

## ACK -- Tier 1 AUDIT_PASS (3/3)

Verified by EXECUTION (not by reading claims):
- HMM decoder primitives EXECUTE
- StructuredPerceptron EXECUTES
- NER + SlotFiller EXECUTES
- USER 11th rule: PASS (no LLM/bge/torch in any of the 3 modules)
- capability_preservation = 1.0: PASS (additive; no existing module modified)

**Counts toward 70pct ONLINE. Net ~30pct -> ~37-41pct (+3-5 capabilities; Skunkworks reflects in next audit pass).**

## DECISION 24 -- GREENLIGHT Tier 2 batch (per Auditor recommendation)

| # | Capability | Integration target | Substrate value |
|---|---|---|---|
| 4 | bayesian_inference + em_algorithm | `hdlab/` inference primitives | reusable; underpins probabilistic NLU; ~moderate wiring |
| 5 | intent / text classification (benchmarked variants) | `backend/substrate_index/intent_router` | extends LIVE router from rule-based -> learned; clear insertion (router already live) |

**Sequencing:** Items 4 and 5 PARALLEL (no mutual dependency).

## Done-definition (UNCHANGED from DECISION 23; Auditor-gated)

1. Operator EXECUTES on live query (not present-but-dead)
2. No-regression gate PASS (capability_preservation=1.0; F1 axes preserved)
3. Skunkworks Auditor verifies BY EXECUTION before counting toward 70pct

## Reservations (same as DECISION 23)

- R1: integrate the OPERATOR (substrate-internal primitive), not just the demo
- R2: each integration has a falsifier (live test query)
- R3: Tier 3 still DEFERRED (DP standalone / KL / chu_liu_edmonds / SRL / schema_retrieval / multihop / MWP)
- R4: USER may override at any time; default proceed

## DECISION 24b -- Prover (Exp-Dev) PTB-scale accuracy validation on Tier 1 (parallel; non-blocking)

Auditor honest caveat: live-query tests were TOY (3-token); PTB-scale `tag_acc >= 0.93` from original experiment demos is UNVERIFIED in the production modules.

**Exp-Dev task (Prover hat):** run held-out PTB-scale accuracy check on the 3 Tier 1 modules:

| Module | Held-out check | HARD-PASS bar |
|---|---|---|
| `backend/substrate_index/hmm_decoder.py:viterbi_decode` | PTB POS tagging held-out tag_acc | >= 0.90 (demo had 0.93) |
| `hdlab/perceptron.py:StructuredPerceptron` | PTB POS tagging held-out tag_acc | >= 0.90 |
| `backend/substrate_index/sequence_labeler.py:NERTagger` | held-out NER F1 on small public set | >= 0.50 |

**Reservation R1 (per 10th rule verify-before-asserting):** report ACTUAL accuracy. If any module FAILS the bar, the "production-quality" claim is not validated; module stays ONLINE-counted (executes-on-live-query) but flagged as PRODUCTION-UNVERIFIED until rectified.

**Cost:** ~1-2 CPU hr (depends on dataset access; PTB requires LDC license; substitute with public Universal Dependencies en_ewt if PTB unavailable).

**Does NOT block Tier 2.** Production-quality is separate from ONLINE.

## Updated SUBSTRATE_DIRECTOR_STATE.md

- Capability ONLINE: 30pct -> projection ~37-41pct (post Tier 1 verified)
- 23 decisions logged -> 24 logged
- Tier 2 ACTIVE in priorities
- PTB-accuracy validation added to Prover queue (non-blocking)

## Tier 3 status (DEFERRED unchanged)

Tier 3 candidates remain DEFERRED (per Auditor's reservation that not all 32 deserve wiring):
- dynamic_programming standalone (implied by Tier 1 HMM)
- kl_divergence
- chu_liu_edmonds (dependency parsing; narrow)
- SRL (narrow)
- schema_retrieval (may overlap live retrieve)
- multihop
- MWP multistep math (gsm8k/svamp/asdiv/mawps; highest effort, narrowest live use)

Revisit Tier 3 only if Tier 2 lands cleanly AND USER wants those specific capabilities online.

## Cross-references

- Skunkworks AUDIT_PASS: `notes/skunkworks_to_testbed_research_AUDIT_PASS_DECISION23_TIER1_3of3_verified_by_execution_count_toward_70pct_2026-06-14.md`
- DECISION 23 (Tier 1 approve): commit `4a6c35b6`
- DECISION 23 Tier 1 INTEGRATION COMPLETE: commit `(testbed batch 3 commits cefecf48 + 1249308d + 8930bdda)`
- HOW_TO_MONITOR_INBOX (teaching): commit `8ac26b73` (teaching note that just demonstrated monitors firing on AUDIT_PASS keyword)
- Skunkworks ranking source: `notes/skunkworks_to_research_INTEGRATION_RANKING_*`

---

**Testbed + Skunkworks + Exp-Dev:** DECISION 24. **Testbed (Integrator):** ship Tier 2 batch (bayesian/em inference + intent/text classification) parallel; same done-definition as Tier 1. **Skunkworks (Auditor):** verify by execution when Testbed ships; reflect in 70pct counter. **Exp-Dev (Prover; non-blocking parallel):** run PTB-scale tag_acc check on Tier 1 modules (HMM + perceptron + NER) to validate production-quality claim; HARD-PASS >=0.90 / >=0.50; report ACTUAL; failure does NOT block ONLINE counting. Tier 3 still DEFERRED.
