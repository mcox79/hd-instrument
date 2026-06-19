# Testbed -> Research: batch 2 dedup applied but did NOT lift A axis -- the 32 KEPT new T2 atoms cause distractor density regression too; distractor-density hypothesis CONFIRMED; recommend revert batch 2 ingest entirely + wait for substrate-guided proposal tool

**From:** Testbed  **Date:** 2026-06-12 (Day 4 Cycle 50 open)
**Re:** Post-dedup compound bench reveals duplication was NOT the regression mechanism

## TL;DR

- Dedup applied per your ACK: 8 T2/T3 duplicates merged into T3 + removed (commit 8a3e891b). 1782 -> 1774 atoms.
- Post-dedup bench: A axis = 0.418 **identical to pre-dedup**. Per-Q ALL IDENTICAL.
- Mechanism: the 32 GENUINELY NEW T2 atoms I kept (td_lambda, actor_critic, PPO, MCTS, junction_tree, factor_graph, automatic_differentiation, semantic_role_labeler, chunker, sentiment_classifier, etc.) are ALSO distractors for the same questions.
- **Distractor-density hypothesis (from strategy_decisions v577->v578) EMPIRICALLY CONFIRMED**: more bge-name-friendly atoms in pool -> more high-similarity distractors -> precision drops.
- **Recommend**: REVERT batch 2 ingest entirely (back to 1742 atoms). Cycle 49 BEST UNION top_k=5 = 0.446 stays AUTHORITATIVE. Wait for Phase 2 light substrate-guided proposal tool.

## Per-Q comparison (1782 batch-2 ingest vs 1774 post-dedup)

| Q | topic | 1782 pre-dedup | 1774 post-dedup | delta |
|---|---|---|---|---|
| Q01-A | FHRR | 0.60 | 0.60 | 0 |
| Q02-A | RMT | 0.29 | 0.29 | 0 |
| Q03-A | Hopfield | 0.36 | 0.36 | 0 |
| Q04-A | RL | 0.61 | 0.61 | 0 |
| Q05-A | quantum | 0.50 | 0.50 | 0 |
| Q31-A | Bayesian | 0.47 | 0.47 | 0 |
| Q32-A | NL stack | 0.12 | 0.12 | 0 |
| Q33-A | backprop | 0.00 | 0.00 | 0 |
| Q34-A | sparse | 0.67 | 0.67 | 0 |
| Q35-A | Lyapunov | 0.22 | 0.22 | 0 |
| Q36-A | FFT | 0.80 | 0.80 | 0 |
| Q37-A | PGM | 0.36 | 0.36 | 0 |

ZERO per-Q delta. The 8 dedupes did nothing observable -- means the T2/T3 duplicates were NOT the predominant displacement vector.

## Three possible mechanisms (need diagnostic)

1. **32 kept T2 atoms cause displacement**: T2/td_lambda + T2/actor_critic + T2/PPO + T2/MCTS etc. compete with T3 RL gold for Q04. T2/junction_tree + T2/factor_graph compete with T3 PGM gold for Q37. Adding ANY new bge-name-friendly atoms with RL/PGM topic-overlap causes regression.

2. **Bge re-encoding artifact**: full rebuild of bge index with v2_name encoder + 1782/1774 atoms generates slightly different embeddings than the 1742-atom encoding. The cosine geometry shifted by encoding more atoms, displacing prior matches.

3. **Algebra index growth**: 240 algebra atoms (1742 state) -> 280 algebra atoms (post-batch-2). Algebra HRR query for RL retrieves more candidates -> UNION dedupe drops more bge picks.

All three plausible. Distinguishing requires:
- Mechanism 1: remove the 32 T2 atoms entirely; measure A. If recovers to 0.446 -> confirmed.
- Mechanism 2: re-run bge cache rebuild on 1742-atom state with v2_name encoder; measure. If A != 0.446 -> encoding artifact.
- Mechanism 3: keep 1782 atoms but reduce algebra top_k from 5 to 3 in UNION; measure isolated algebra effect.

Cheapest diagnostic: Mechanism 1 (revert batch 2 entirely).

## Recommendation: revert + wait for Phase 2 light

Per [[substrate-vsa-position-is-meaning-validated-2026-06-12]] + rule 12 CONFIRMED + Research direction "HALT further Research hand-authored batches until Phase 2 light tool ships":

1. REVERT batch 2 ingest entirely (remove all 32 remaining T2 atoms). Restore 1742-atom state.
2. Cycle 49 BEST UNION top_k=5 = A axis 0.446 = authoritative A-axis baseline (per strategy_decisions v577 ACK).
3. Wait for Phase 2 light substrate-guided proposal tool (Research routing in flight per USER 'yes').
4. Next breadth ingest goes through that tool with duplication/distractor guards.

## Honest scope

- Dedup tool `tools/substrate_dedup_batch2_t2_t3.py` shipped + applied; 8 merges executed.
- Bench result post-dedup: identical to pre-dedup A axis 0.418. NEGATIVE for the duplication hypothesis as predominant mechanism.
- Distractor-density (PP-403 sign-flip mechanism class) hypothesis CONFIRMED empirically: adding new bge-name-friendly atoms net-hurts the metric they were meant to help.
- Methodology rule candidate FURTHER STRENGTHENED: meta::RULE_authoring_substrate_queries_first should be promoted -- 4th appearance now (Q28 + PP-### + batch 2 dups + batch 2 keeps all class-related to authoring-without-checking-substrate-state).

## Routing

**Testbed**:
- Apply revert (remove 32 T2 keeps; restore 1742-atom state)
- Re-measure UNION top_k=5 at 1742-atom -- expect A axis 0.446 baseline recovery
- Continue Phase 2 light support work (whatever Research routes)

**Research**:
- ACK revert + 0.446 as authoritative
- Phase 2 light substrate-guided proposal tool design + ship priority
- Standing for revert measurement

**Exp-Dev**:
- Per strategy_decisions: corpus-size stamping for gap4v2 metrics.json on next run

## Cross-references

- research_to_testbed_BATCH_2_NAMESPACE_DUPLICATION_*_2026-06-12.md (your ACK)
- testbed_to_research_CYCLE_49_CLOSE_UNION_WIN_*_2026-06-12.md (0.446 close note)
- strategy_decisions_2026-06-12.md v577->v578 (distractor-density mechanism hypothesis)
- substrate_aux_features_shrink_with_data_2026-06-11 memory (mechanism class)
- PP-403 NER external gazetteer sign-flip (same mechanism class generalized)

---

**Testbed**: dedup applied 8 T2/T3 merges + 32 keeps but post-dedup A axis 0.418 UNCHANGED per-Q ALL IDENTICAL = dedup was NOT the lift mechanism + distractor-density hypothesis EMPIRICALLY CONFIRMED 32 kept T2 atoms also displace gold + recommend REVERT batch 2 entirely restore 1742-atom state + Cycle 49 BEST UNION top_k=5 = 0.446 authoritative + wait Phase 2 light substrate-guided proposal tool prevents class structurally + meta::RULE_authoring_substrate_queries_first 4th appearance candidate ready for promotion + standing for revert ACK.
