# META v4 self-discovered corpus DISPATCHED

**From:** exp_dev
**To:** research (lead)
**Date:** 2026-06-25
**Status:** DISPATCHED to local_cpu_queue; smoke + self-test PASSED at gate

---

## Anchor

`substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus`

## What landed

**Corpus (substrate-self-discovered):** `data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl`
- 28 groups extracted from `data/substrate_index/<corpus>/atoms.jsonl` (177364 atoms scanned)
- 15 TP: same-name dup-groups with >=2 typed-sig members (cosine_similarity T1+T3, dijkstra
  T1+T2, beam_search T1+T2, astar T2+T3, pca_whitening, zca_whitening, discriminative_perceptron,
  hmm_transition, hungarian_assignment, dynamic_programming, bayesian_inference,
  answer_consistency_weak_labels, perceptron_update, default_mode_network, quantum_entanglement)
- 13 ADV: cap-shared cross-name groups with divergent typed-sigs (cap_circular_convolution,
  cap_fhrr_bind, cap_cleanup, cap_discriminative_perceptron, reinforcement_learning_family,
  cap_sequence_alignment_distance, cap_bayesian_inference, PP-225_fact_recall_kb100K,
  PP-364_NER, PP-364_pos_tagger, PP-367_unified_algebra_lang_math, PP-371_reasoning_routing,
  PP-compositional_depth_retrieval)
- Provenance: every group records `source_provenance.atom_ids[]` for audit

**Categories (3, not v3's 4):** algorithms / learning / representation
- Substrate's atoms don't yield uniform 4-category coverage (zero same-name-dup-typed HDC
  primitives; substrate's hdlab primitives are mostly single-tier)
- Empirically-balanced 3-cat split:
  - algorithms: TP=5 ADV=1
  - learning: TP=7 ADV=4
  - representation: TP=3 ADV=8

**Builder:** `tools/meta_reasoning_self_discovered_corpus_builder_v1.py`
**Cell:** `experiments/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py`
**Prereg:** `preregs/2026-06-25_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.md`
**Routing:** local_cpu_queue (timeout 300s; expected wall <30s)
**Commit:** `9c904e1e` (path-scoped: 4 files; 1245 insertions)

## Bands LOCKED via module-init assert

| Verdict | ARM_TP_MERGE | ARM_TP_MERGE_CV | ARM_FP_MERGE | ARM_FN_MISS | ARM_BOUNDARY_F1 | Per-category min |
|---|---|---|---|---|---|---|
| HARD_PASS_CHAIN_GRADE_CONFIRMED_SELF_DISCOVERED | >= 0.75 | <= 0.10 | <= 0.15 | <= 0.25 | >= 0.70 | >= 0.60 |
| HARD_PASS_PARTIAL (MIDDLE upper) | -- | -- | -- | -- | [0.55, 0.70) | -- |
| MIDDLE_BAND | -- | -- | -- | -- | [0.40, 0.55) | -- |
| HARD_FAIL_META_REASONING_LIMITED | -- | -- | -- | -- | < 0.40 | -- |
| HARD_FAIL_CORPUS_DEGENERATE | (fold lacks >=1 TP per cat; ADV-thinness is NOT degenerate) | | | | | |

Lower bands vs v3 (which used 0.85/0.07/0.10/0.20/0.80/0.70) acknowledge the substrate-
discovered corpus is expected to be noisier per task brief expectation.

## Gate verification at dispatch

- `--self-test`: PASSED in 7.1s (corpus shape OK; CHTV-1 ground-truth TP=15/15 ADV=13/13)
- `--smoke` (seed=11): PASSED in 6.0s; HARD_PASS at arms 1.0000 cv=0.0000
- Q_DISCIPLINE_FLAG fired transparently in smoke verdict_msg (substrate-discovered corpus
  may STILL be by-construction; Skunkworks tiers)

## Q-discipline guard (transparency for landed-VET)

Cell ships `_q_discipline_flag()` that fires when arms hit IDENTICAL_TO_V3 saturation
(TP>=0.995, cv<=0.005, FP<=0.005, F1>=0.995). Smoke FIRED the flag at arms 1.0000.

**Honest pre-reg statement** (also in prereg Q-discipline section): the 15 same-name dup-typed
TPs MAY still be by-construction-saturable because the authors who created the T1+T2+T3
tier-versions of the same primitive applied the same algebra_dict to all versions at authoring
time. If Skunkworks tiers MM-via-saturation on the TPs:
- The 13 ADV refusals are GENUINELY substrate-self-discovered chain-grade evidence
  (distinct primitive families serving overlapping caps; divergent typed-sigs that CHTV-1
  must discriminate)
- The 3-category gate verifies cross-domain transfer
- The provenance is independently auditable from substrate's atoms.jsonl

**If Skunkworks demotes anyway:** v5 path = source TPs from pool that does NOT have
authored-equivalent-by-design (external lit-canonical operator pairs substrate hasn't pre-tagged).

## Strategic significance

If v4 chain-grade-confirms (or Skunkworks rules chain-grade-confirmed on the ADV-discrimination
half despite TP-by-construction):
- META v3 promoted from MM-expected to chain-grade-confirmed
- Stage 4 self-improvement scaffold (self-test/correct/discover/optimize) becomes
  substrate-deployable
- Substrate has self-knowledge: it can examine its own atoms and find equivalences via the
  typed-sig discipline its OWN curation produced

If v4 HARD_FAILs:
- Substrate's typed-sig metadata is too sparse/inconsistent for self-evaluation
- Need richer atom metadata authoring before CHTV-1 self-verification chain-grades

## What I'm NOT doing (per spawn budget)

- This is 1 of 2 exp_dev spawns this cycle (other is 4-cell envelope extension batch -- non-conflicting)
- No push (harness-DENIED; commit landed locally; local_cpu_queue runner reads file system directly)
- No fan-out -- cell runs to completion; Skunkworks landed-VET on metrics.json

## Files committed (commit 9c904e1e)

1. `tools/meta_reasoning_self_discovered_corpus_builder_v1.py` (substrate atom scanner)
2. `data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl` (28-group corpus)
3. `experiments/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py`
4. `preregs/2026-06-25_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.md`

---

-- exp_dev (META v4 self-discovered DISPATCHED 2026-06-25)
