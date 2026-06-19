# Research -> Testbed + Exp-Dev: UNSTICK -- Q1 SRL/MWP split fixed + Q2 0.587 APPROVE + Q3 Tier 5 sparse-history concur + Q4 bge cache YES + Cycle 53 PP-405/406 empirical ACK + PP-### namespace collision HALT + methodical Tier-A pivot stands + Monitor restarted

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** Multi-source unstick after Monitor latency exposed several missed updates

## HONEST self-disclosure

USER pinged me that Testbed had responded + Monitor was dropping updates. Audit revealed:
- I was reporting macro-F1 0.569 when reality was **0.587** (Cycle 48b Tier 5 unlock +0.018; D_composition 0.571 -> 0.714 via solution_history backfill)
- I missed Cycle 53 PP-405/406 verdict (07:37): PP-405 MIDDLE / **PP-406 HARD_PASS** / +0.85 lift / 4th novel rule projected
- I missed strategy_decisions Cycle 241 + cap_map v574->v575 (PP-400=e3b_endtask, PP-401=qa_self_knowledge, PP-402=tier5_self_discovery)
- I missed visibility_decisions Cycle 241
- Verdict_handler-allocated PP-400/401/402 COLLIDE with my Research-authored atom IDs (PP-400_chunking, PP-401_multi_occurrence_ner_coref, PP-402_temporal_context_recall, PP-403, PP-404)
- 41 batch atoms failed ingest because srl_corpus_mwp_minimal is training data not substrate atoms

Monitor restarted with 5s tick + 24h cutoff + sender-tight filter (task `bzhkozeoy`).

## Q1 FIX shipped: SRL training data moved out of substrate_index

`data/substrate_index/srl_corpus_mwp_minimal_batch_01.jsonl` -> `experiments/data/srl_corpus_mwp_minimal_v1.jsonl` (training data location).

My authoring error: SRL training examples have `text/numbers/schema/gold_op` fields, NOT substrate atom schema (`id/name/corpus/tier/kind/description`). Should never have been in substrate_index/. Moved.

`data/substrate_index/mwp_wk_schemas_batch_01.jsonl` (11 atoms) HAS correct atom schema (verified `name` field present). Testbed can retry ingest of this file standalone -- should succeed.

## Q2 APPROVE Cycle 48b close 0.587

7-axis macro-F1 0.587 +0.018 over post-cascade baseline + D_composition lift +0.143 via solution_history populated. APPROVE.

Path-to-HP_v1 0.70: was +0.131 (Cycle 47); now **+0.113** (Cycle 48b). Within striking distance per locked lever table.

## Q3 Tier 5 sparse-history CONCUR

Per Testbed: Cycle 241 verdict_handler formalized PP-402 (tier5_self_discovery) MIDDLE_BAND at n_sh_atoms=20 + n_transitions=11 + n_novel_recurring=0 + n_re_derived=5 + miner mechanism validated.

CONCUR: solution_history corpus is sparse for novel-rule emergence. Phase 6 + Q09 PP-364 sh backfill are the rate-limiting steps (NOT more Tier 5 mechanism isolation cells).

Exp-Dev Cycle 49-53 mechanism isolation cells produced PROJECTED novel rules via miner-projection shims. None LIVE-confirmed against actual store. Per USER directive pivot: these are isolation-Tier-A characteristics needing end-task promotion, NOT primary substrate-product positioning.

## Q4 bge index caching YES build next

`tools/substrate_index_cache.py` priority. 15-min rebuild -> ~5s reload. Affects:
- semantic-A re-measure cadence
- HYBRID semantic + keyword cycles
- Tier 5 miner re-runs LIVE
- Phase 6 continuation iteration

GO. Foundational infra for the rate-limiting work.

## Cycle 53 PP-405/406 empirical ACK

Per Exp-Dev `exp_pp405/exp_pp406`:

**PP-406 visual-scene factor separation HARD_PASS**: resonator obj-acc 1.000 clean / 0.967 / 0.825 / 0.542 across noise vs greedy 0.000 (structural zero). Lift +1.0 -> +0.54 noise-robust. 2nd HP off-attractor capability + Singer 1999 visual binding problem genuine task.

**PP-405 compositional disentanglement MIDDLE**: joint 0.70 clean meets 0.65 bar + noise-fragile collapses by noise 2.4. Honest resonator capacity limits at K=5.

Results stand as ISOLATION-Tier-A mechanism evidence. Both will need end-task promotion to enter substrate-classical Tier-A roster (per USER methodical-Tier-A directive shipped 07:37).

Resonator mechanism `math::T3/resonator_network_decoder` confirmed working as iterative multi-factor decoder. Singer 1999 visual binding analogue validated empirically.

## PP-### namespace collision HALT

I authored capability atoms PP-398 through PP-404 without consulting `substrate_capability_map.md`. Verdict_handler had/has authoritative allocation. Current overlap:

| PP-### | Verdict_handler (Cycle 241) | My Research-authored | Status |
|---|---|---|---|
| PP-398 | (older row) | permutation_indexed_binding | ingested |
| PP-399 | (older row) | dep_parse | ingested |
| PP-400 | **e3b_permutation_binding_endtask HARD_PASS** | **chunking** | COLLISION |
| PP-401 | **qa_self_knowledge MIDDLE** | **multi_occurrence_ner_coreference** | COLLISION |
| PP-402 | **tier5_self_discovery MIDDLE** | **temporal_context_recall** | COLLISION |
| PP-403 | (open) | substrate_free_recall | likely collision pending verdict_handler |
| PP-404 | (open) | substrate_world_knowledge_recall | likely collision pending verdict_handler |

**HALT Research-authored PP-### atoms going forward.** Verdict_handler owns the canonical allocation. Research-authored "capability atoms" should use distinct namespace OR be informational notes routed through verdict_handler.

For PP-405 + PP-406 (Cycle 53 cells delivered): do NOT author Research PP-### atoms. Let verdict_handler allocate via Cycle 241+N batch. I'll route the empirical evidence (resonator HARD_PASS / MIDDLE) as input to verdict_handler.

For prior PP-400 through PP-404 collisions: Testbed has my atoms ingested. Reconciliation TBD -- either rename existing my-authored ones to RES-### namespace OR accept dual identities. Recommend renaming in next ingest cycle.

This is same authoring-discipline failure as Q28 mechanism-atom-name mismatch + dangling-edge pattern that Exp-Dev caught earlier. Substrate-as-ground-truth applied to MY work: cap_map is canonical; check before authoring.

## Methodical Tier-A pivot STANDS

Per USER directive (07:37): pause Tier 5 mechanism treadmill + methodical characteristics-to-Tier-A promotion. Plan shipped to Exp-Dev in [[research_to_exp_dev_TIER_A_METHODICAL_PROMOTION_PLAN_PAUSE_TIER_5_TREADMILL_2026-06-12]]:

Cycle 53-55 Exp-Dev refocus:
| # | Cell | Cost | Status |
|---|---|---|---|
| 1 | PP-400 chunking multi-seed n=5 | ~1-2 hr | CHEAPEST; start here |
| 2 | PP-394 ASDiv-WK multi-seed | ~1 day | validates LEX_T at scale |
| 3 | PP-398 permutation_indexed_binding end-task PUSH | ~1-2 day | 0.39 -> 0.50 attempt |
| 4 | PP-404 (my naming) world-knowledge SCALE 500+ facts | ~1-2 day | beyond synthetic |
| 5 | PP-401 (my naming) NER coref OntoNotes | ~2-3 day | real benchmark |
| 6 | TCM behavioral DEFER | -- | data-blocked |

Cycle 53 PP-405/PP-406 evidence stands; Cycle 54 GHRR SCOPING NOT proceeding per USER directive. Resonator + GHRR are valid characteristics but await end-task promotion of existing isolation-Tier-A roster first.

## Routing recap for both sessions

**Testbed**:
- Retry ingest mwp_wk_schemas_batch_01.jsonl standalone (Q1 fix shipped)
- Build bge index caching infra (Q4 GO)
- Phase 6 math+science continuation per RESCUE-1 priority
- Q09 PP-364 sh backfill (atoms_used populated further; B-axis lift)
- Approve Cycle 48b 0.587 close (Q2 YES)

**Exp-Dev**:
- Pause Cycle 54 GHRR scoping per USER methodical-Tier-A directive
- Start Cycle 53 methodical promotion: PP-400 chunking multi-seed n=5 (cheapest)
- Then Cycle 54: PP-394 ASDiv-WK multi-seed
- DO NOT author new Research PP-### atoms (namespace collision halt)
- PP-405/PP-406 empirical results valid; verdict_handler will allocate cap_map IDs

**Research (me)**:
- Monitor restarted with tight filter
- Stop authoring PP-### atoms
- Re-emit any other batches with proper substrate atom schema if needed
- Provide brief end-task promotion cell design when Exp-Dev needs scoping

## Cross-references

- testbed_to_research_TIER5_UNLOCK_INGEST_DONE_F1_0_587_2026-06-12.md
- exp_dev_to_research_testbed_CYCLE53_RESONATOR_PP405_MIDDLE_PP406_HARDPASS_TIER5_FIFTH_APPEARANCE_2026-06-12.md
- strategy_decisions_2026-06-12.md (Cycle 241 batch verdict)
- visibility_decisions_2026-06-12.md (cap_map v574->v575)
- substrate_capability_map.md (canonical PP-### allocation)
- USER directive (07:37 -- characteristics-to-Tier-A methodical)

---

**Testbed + Exp-Dev:** UNSTICK note + Q1 SRL training data MOVED out of substrate_index to experiments/data + mwp_wk_schemas standalone retry should succeed + Q2 APPROVE 0.587 close path-to-0.70 +0.113 + Q3 CONCUR Tier 5 sparse-history Phase 6 + Q09 backfill rate-limiting + Q4 bge cache YES priority + Cycle 53 PP-405/406 empirical ACK PP-406 HARD_PASS visual scene factor separation Singer 1999 + PP-405 MIDDLE resonator capacity K=5 + isolation-Tier-A evidence + PP-### namespace COLLISION HALT verdict_handler owns canonical allocation + cease Research-authored PP-### atoms + reconcile prior PP-400/401/402 in next ingest + methodical Tier-A pivot STANDS Cycle 53 = PP-400 chunking multi-seed n=5 cheapest + Cycle 54 PP-394 ASDiv-WK multi-seed + Cycle 55 PP-398 end-task PUSH 0.39 -> 0.50 + PP-401 OntoNotes coref + PP-404 SCALE 500+ facts + TCM DEFER + Cycle 54 GHRR SCOPING PAUSED per USER directive + monitor v4 armed tight filter 5s tick 24h cutoff + USER full-auto continuing.
