# PRE-REGISTRATION -- anchor_pool_expansion_v1 (matched ablation, ONE variable: ANCHOR POOL SIZE)

Filed 2026-08-13 BEFORE either arm ran. Cell: `experiments/exp_anchor_pool_expansion_v1.py`.
Outputs: `data/exp_anchor_pool_expansion_v1/` ONLY. **GROWTH IS PAUSED** -- nothing enters a
canonical foundation path.

---

## 1. The finding under test

`notes/downstream_bottleneck_trace_2026-08-13.md`: `canonicalize_fast` argmaxes over
`ConceptSpace` anchors only, and anchors enter at exactly two sites --
`hdlab/reading_grounding_loop.py:1039-1044` (seed vocabulary) and `:1279` (already-grounded
lemmas). Anchor universe = 887 seed + 374 grounded = **1,261**, against ~16,812 corpus content
lemmas: a **6% naming ceiling**. `fruit` and `zone` were never candidates.

`notes/minimum_grounded_basis_derivation_and_refutation_2026-08-13.md`:
`data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv` holds **74,287 rows** and the
loop loads only the top 1,000. The pool problem is not WHICH words, it is HOW words enter.

## 2. The one variable

**ANCHOR POOL SIZE ONLY.** `state.known_seed` stays the shipped top-1,000-row / 887-lemma set in
BOTH arms, so the target set, the gap gate, the reading order, the admission policy, the
comparator (`context_vector_masked`; F1/F3 OFF), `ARM_SEED=4201`, `N_DIM=2048`, `CHUNK_SIZE=150`
and the corpus (`load_corpus_v5(None, lineaware=True)`, 34,169 sentences) are IDENTICAL.

* **SMALL** -- shipped default. Anchors = (seed lemmas that occur) UNION (lemmas grounded by this
  run). `anchor_pool=None`.
* **LARGE** -- `anchor_pool` = lemmas of the FULL 74,287-row ordered base vocabulary (50,461
  distinct lemmas). A pool lemma accumulates a profile in `ConceptSpace` when it occurs, and is
  STILL a gap, STILL flagged, STILL a grounding target: availability as an anchor is not
  knowledge.

Mechanism: `process_sentence(..., anchor_pool=...)`, **ADDITIVE and DEFAULT-OFF**, proven by
`hdlab.reading_grounding_loop._selftest_anchor_pool_is_off_by_default` (default anchor population,
per-anchor bundles, flagged-target count and `known_seed` all unchanged).

### 2.1 Depth chosen by evidence -- measured coverage (`_probe_coverage.json`)

Corpus = 34,169 sentences, 16,812 distinct content lemmas (16,507 `is_eligible_meaning`).

| seed depth (rows) | distinct lemmas | pool lemmas occurring in corpus | TYPE coverage | TOKEN coverage | v5 known-object availability |
|---|---|---|---|---|---|
| 1,000 (shipped) | 887 | 785 | 0.0467 | 0.3644 | 0.167 |
| 5,000 | 4,102 | 3,459 | 0.2057 | 0.6971 | 0.633 |
| 20,000 | 14,962 | 8,561 | 0.5092 | 0.8802 | 0.874 |
| **74,287 (all)** | **50,461** | **12,691** | **0.7549** | **0.9477** | **0.947** |

**CHOSEN DEPTH = 74,287 (the entire ordered base vocabulary).** It is the shallowest depth
reaching a great majority of corpus content lemmas (0.755 of types, 0.948 of tokens); 20,000
reaches only 0.509 of types. The marginal cost is small because the CORPUS vocabulary, not the
base vocabulary, is the binding constraint: 12,691 anchors vs 8,561 at depth 20,000. The residual
24.5% of corpus types are absent from the base vocabulary at ANY depth (proper nouns, technical
biology terms) and are a declared limitation, not a tunable.

## 3. Primary discriminator -- KNOWN-ANSWER RECALL (no hand-scoring, not floor-limited)

Probe subjects must (a) occur in the reading corpus, (b) NOT be in the 887-lemma seed (i.e. be a
real read-out target), (c) be single-token, (d) have >=1 single-token `is_eligible_meaning` known
object != the subject.

* **v62** `data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl`, hand-scored 0.94 ->
  **36 subjects**. **RELATION-MISMATCH, DECLARED IN ADVANCE:** v62's relations are
  `ENABLING_CONDITION` / `ENABLING_CONDITION_AGENT` / `PROCESS_ACTION` / `PROCESS_PATIENT`, NOT
  `GROUNDED_MEANING`. The read-out under test emits `GROUNDED_MEANING`. Recall against this key is
  therefore an answer to a DIFFERENT QUESTION and a low number licenses no conclusion about the
  read-out. Reported because it was requested, and reported with this caveat attached.
* **v5** `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`,
  hand-scored 0.64 -> **1,353 subjects**. Relation IS `GROUNDED_MEANING`: RELATION-MATCHED. About
  a third of these facts are wrong, so recall against this key is bounded above near 0.64 and the
  arm-to-arm DELTA, not the level, is the quantity of interest.

Both key sets are reported separately and never pooled.

### 3.1 The four measures, per arm, per key

1. **AVAILABILITY** -- fraction of probe subjects with >=1 known object present in that arm's
   final `ConceptSpace` anchor set AND eligible. Manipulation check. If it does not move, the
   experiment is broken and no other number is interpreted.
2. **RECALL@1** -- the read-out's top-1 object is a known object.
3. **RECALL@5** -- a known object is in the read-out's top 5.
4. **AVAILABILITY-CONDITIONED RECALL@1** -- (2) restricted to rows where (1) holds. **This is the
   number that separates the two hypotheses.**

Read-out procedure, identical in both arms: for each probe subject that the arm actually flagged,
`raw_sum = sum(t.context_vec for t in library.items[subject].traces)`, scored by
`canonicalize_fast`'s own math (cosine of `sign(raw_sum)` against the final anchor matrix, masked
by `is_eligible_meaning`, self excluded), top-5 taken in the same sorted-anchor tie-break order.
This is a POST-HOC read-out over the arm's own final field, run over the SAME subject list in both
arms, because the live loop banks only ~380 of ~16,000 targets and a live-banked-only intersection
would be underpowered by construction. The LIVE banked recall over the same probe subjects is
recorded too, and is explicitly secondary.

## 4. BANDS -- fixed before running

Delta = `recall@1(LARGE) - recall@1(SMALL)` on the **v5 relation-matched** key (the v62 key is
relation-mismatched and cannot carry the verdict).

* **POOL_WAS_BINDING** -- availability rises sharply (>= +0.30) AND delta >= **+0.10**.
* **PARTIAL** -- delta in **[+0.03, +0.10)**.
* **COMPARATOR_IS_BINDING** -- availability rises sharply AND delta < **+0.03**. The correct answer
  is now on the menu and is still not chosen. **PRE-DECLARED FULLY EXPECTED AND ACCEPTABLE**; on
  the evidence to date (the comparator is bag-of-co-occurrence cosine, hand-scored 3/100
  MEANINGFUL) this is the modal outcome and it is a real result, not a failure of the cell.
* **HURTS** -- delta <= **-0.03**. A 10x larger pool adds a competitor to every decision; this is a
  live possibility, not a formality.
* **BROKEN** -- availability does not rise. Nothing else is interpreted.

Power: at n=1,353 subjects, SE of a proportion near 0.05 is 0.006 and SE(delta) <= 0.019, so the
+0.03 boundary is resolvable at >1.5 SE and +0.10 at >5 SE. (Contrast: the two 2026-08-12 cells
were floor-limited by a random 50-row hand-score at 1-3% MEANINGFUL and could not resolve
anything.)

## 5. Secondary, pre-registered

* **Per-arm co-occurrence agreement** (`cooc_agreement_top1` / `top5`) against the plain
  sentence-level co-occurrence baseline over the same corpus -- the mechanistic, hand-score-free
  measure that worked twice on 2026-08-12. Prediction recorded, not a gate: if the comparator is
  the binding constraint, LARGE's agreement stays high or RISES (a bigger pool gives the
  frequency backbone more room), whereas a pool-limited read-out would show agreement FALL as
  better-fitting rare anchors become reachable.
* **Per-arm fact counts** (`n_meaning_facts`, `n_grounded`), refusal-reason histogram, PBV
  trajectory, admission/confirm rates.
* **Anchor-matrix dimensions and peak process RSS per arm.**

## 6. Structural gates

* **S1 cardinality** -- 2 arms x 5 segments + 2 arm-done units present in `units.jsonl`.
* **S2 integrity** -- 0 tautology facts, 0 closed-class objects, 0 no-leak violations per arm.
* **S3 arms differ** -- distinct `pairs_digest`.
* **S4 SMALL REPRODUCES THE SHIPPED REFERENCE** -- `n_meaning_facts == 384` and
  `pairs_digest[:16] == 836571fa99d5765d` against
  `data/exp_grounding_quality_readout_v1/metrics.json`. If this fails the cell reports the exact
  divergence and the LARGE result is quarantined.
* **S5 yield floor** -- >= 50 facts per arm.
* **S6 default-off witness** -- `_selftest_anchor_pool_is_off_by_default` in the module's
  self-test suite.

## 7. Secondary hand-score deliverable

A blind pooled sample, n=100 (50/arm, `random.Random(42).sample` over fid order, shuffled with
seed 42, key sealed in `arm_key.json`, `SCORING_SHEET.txt` in the exact format of
`data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt`, no-leak: no scores, no counters, no
fid, no segment, one context sentence per row). **THE CELL MAKES NO QUALITY CLAIM.** Given the
1-3% MEANINGFUL floor measured on 2026-08-12, n=50/arm cannot resolve a delta below ~+0.11; this
sample is SECONDARY evidence and the known-answer recall above is primary.

## 8. Declared limitations (written before the result)

* A pool lemma's anchor profile is a bag-of-co-occurrence sum, exactly like a seed anchor's. This
  cell tests AVAILABILITY, not a better representation.
* 24.5% of corpus content types are in no depth of the base vocabulary; the ceiling on LARGE's
  availability is set by that, not by the loop.
* The post-hoc read-out scores against each arm's FINAL anchor field, not the field as it stood at
  the live decision. It is a fair between-arm comparison (same procedure both sides) but it is not
  the live decision, and is labelled as such.
* v5's key is 64% correct; v62's key is 94% correct but relation-mismatched. Neither is a clean
  gold standard and no absolute quality tier is claimed from either.
