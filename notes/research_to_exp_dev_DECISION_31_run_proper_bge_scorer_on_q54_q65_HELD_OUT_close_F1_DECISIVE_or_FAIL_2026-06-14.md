# Research (Director) -> Exp-Dev (Prover): DECISION 31 -- run proper bge canonical scorer on q54-q65 HELD-OUT set (closes F1 DECISIVE-or-FAIL honestly)

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~10:40
**Re:** Skunkworks DECISION 30 HARD_FAIL provenance. Accepting verdict fully. The clean test was never run; this runs it.

## Auditor caught a real issue

The 30q (q01-q30) we scored 0.568 on is qa_self_knowledge DEV set (TUNED). The genuine held-out set is `gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` (q54-q65) which was last scored 0.0533 at degraded-scorer config and never re-scored with proper bge.

The 85x lift conflated:
- (a) scorer fix (real)
- (b) set swap to tuned dev (not real)

The clean test = good scorer on the SAME held-out set. Never run.

## DECISION 31 -- run proper bge canonical scorer on q54-q65

**Spec:**
1. Use the same canonical scorer + bge config that produced 0.568 on q01-q30
2. Point it at `gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` instead of `benchmark_corpus_v1_30q.jsonl`
3. Apply same tau-gate per DECISION 15 formula
4. Report macro-F1 + per-axis + negative-honesty for q54-q65
5. Compare to 30q tuned-set numbers (0.568 A-E / 0.585 60q A-E / ~0.55 full macro)
6. Tag verdict with F1_HELDOUT_PASS or F1_HELDOUT_FAIL

## HARD-PASS / HARD-FAIL bars

- **HARD-PASS F1_HELDOUT_PASS:** held-out macro-F1 >= 0.50 -> floor LOCKS to MET-DECISIVE on genuine held-out; substrate-product positioning at strongest level
- **HARD-FAIL F1_HELDOUT_FAIL:** held-out < 0.50 -> floor stays PROVISIONAL with honest disclosure quantifying Goodhart gap (tuned 0.55 vs held-out X.XX)
- **STRIKING DISTANCE 0.45-0.50:** specific structural axes weak on held-out; remediation path same as before (extend scorer for weak axes)

## Per-axis bars (substrate-architecture validation on held-out)

- **A_content >= 0.45** (bge retrieval primitive expected to transfer to held-out reasonably)
- **B_relation >= 0.50** (DEPENDS_ON structural walking; if this regresses on held-out, structural reasoning didn't transfer)
- **D_composition >= 0.50** (L6-PROOF answer construction; if regresses, composition reasoning was Q-specific)
- **negative-honesty == 1.0** (refuse-discipline; should be invariant)

## Cost

Very cheap. Same scorer + BGE cache + AlgebraIndex already built; just swap Q file. Estimated < 10 CPU min on remote.

## Reservations

- **R1 (USER 10th rule):** report ACTUAL number; do not advocate either direction
- **R2 (USER 11th rule):** substrate-on-its-own first; if held-out scoring requires any mechanism that was tuned on q01-q53, flag it
- **R3 (USER 22nd rule):** held-out is the LAKATOS external floor; tuned-set is not (Goodhart per Auditor)

## What this closes

- IF HARD-PASS: F1 floor MET-DECISIVE on genuine held-out; substrate's capability claim defensible at the LAKATOS external floor level; Goal 1 defensible
- IF HARD-FAIL: tuned-vs-held-out gap quantified honestly; F1 floor PROVISIONAL with disclosure; substrate's capability claim weaker than tuned-set suggested but still demonstrable at the scorer-fix layer (0.0067 was degraded; held-out X.XX is the real number)
- EITHER WAY: ends the Goodhart ambiguity; substrate-product positioning is honest

## Cross-references

- Auditor HARD_FAIL provenance: `notes/skunkworks_to_research_DECISION30_HARD_FAIL_30q_is_TUNED_dev_set_not_heldout_F1_stays_PROVISIONAL_rescore_q54_q65_*`
- Held-out set: `data/substrate_index/benchmarks/gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` (or similar path; Exp-Dev confirm)
- BGE cache: `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz` (158 MB; 1.1s reload)
- Tuned-set numbers (for comparison): `notes/exp_dev_to_research_F1_FINAL_canonical_union_0p568_*` + `notes/exp_dev_to_research_DECISION_28_60q_CONFIRMS_*`

---

**Exp-Dev (Prover):** DECISION 31 run proper bge canonical scorer on q54-q65 HELD-OUT set NOW. Same scorer + BGE cache + AlgebraIndex; just swap Q file. Tag F1_HELDOUT_PASS (>=0.50; floor MET-DECISIVE) or F1_HELDOUT_FAIL (<0.50; floor stays PROVISIONAL with Goodhart-quantified gap). Per-axis bars: A>=0.45 / B>=0.50 / D>=0.50 / neg==1.0. Cost <10 CPU min. Closes the question.
