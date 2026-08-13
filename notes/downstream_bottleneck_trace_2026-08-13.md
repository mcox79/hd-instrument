# Downstream bottleneck trace: where the correct candidate dies (2026-08-13)

**Scope.** DIAGNOSIS ONLY. No quality claim, no proposed fix, nothing wired, nothing written to any
canonical foundation path. Read-mostly: one probe script under
`data/exp_structured_comparator_v1/probes/`, no edit to `hdlab/` or `tools/`.

**The lead being chased** (`notes/director_handscore_structured_comparator_2026-08-13.md`, the
"tension" paragraph): on `banana` the STRUCTURED encoder isolates `(^nsubj, fruit)` and on
`aphotic` it isolates `(^amod, zone)` -- demonstrably the right feature -- and the arm still scored
0/50 MEANINGFUL. Question: which stage downstream of feature selection discards the correct
candidate?

**Answer, both lemmas, same stage: STAGE 2, the candidate set.** `fruit` and `zone` are never
anchors in the `ConceptSpace` at any point in either arm's run, so no comparator, threshold,
verifier or store could have selected them. This is a MISSING-CANDIDATE defect, not a
wrong-comparison defect, and it is ARM-INDEPENDENT (it holds identically in CONTROL).

---

## The candidate set, off the code

`canonicalize_fast` takes its argmax over `space.anchor_matrix()` and nothing else
(`hdlab/reading_grounding_loop.py:656-703`). A lemma enters `ConceptSpace` at exactly two sites in
the live path (grep-verified, whole repo, `*.py`):

| site | who enters |
|---|---|
| `hdlab/reading_grounding_loop.py:1039-1044` | `if lemma in state.known_seed: state.space.observe(...)` -- SEED vocabulary only |
| `hdlab/reading_grounding_loop.py:1279` | `state.space.seed_from_bundle(lemma, raw_sum)` for each lemma that just GROUNDED |

So: **anchors = (seed lemmas seen in the corpus) UNION (lemmas already grounded by this same
loop)**. Nothing else can ever be the object of a `GROUNDED_MEANING` fact.

Measured off disk (`data/exp_structured_comparator_v1/units.jsonl`,
`data/corpora/.../base_vocabulary` via `load_base_vocab_seed()`):

| quantity | value |
|---|---|
| seed vocabulary | 1000 words -> **887 distinct lemmas** |
| STRUCTURED grounded lemmas (become anchors) | 374 |
| anchor universe, superset (seed UNION grounded) | **1261** (CONTROL 1271) |
| distinct content lemmas in the 34,169-sentence corpus | **16,812** (16,507 `is_eligible_meaning`) |
| anchor universe as a share of eligible corpus vocabulary | **0.0599** STRUCTURED / 0.0605 CONTROL |
| banked objects that are SEED lemmas | **347/384 = 0.9036** CONTROL, **301/374 = 0.8048** STRUCTURED |

`1261` is a SUPERSET of the true anchor set at any decision time (anchors accumulate during the
run, and a seed lemma only enters when it actually occurs with a non-zero context vector), so a
"not in this set" verdict is exact.

**`fruit`: corpus frequency 95, in seed vocab NO, grounded in STRUCTURED NO, grounded in CONTROL
NO.**
**`zone`: corpus frequency 71, in seed vocab NO, grounded in STRUCTURED NO, grounded in CONTROL
NO.**

Neither is ever an anchor. In CONTROL, `banana -> people` (best_cos 0.4219, 4 exposures, fid in
`arm_CONTROL_provenance.json`) was banked; `fruit` was not a candidate there either. In STRUCTURED
neither `banana` nor `aphotic` was banked at all.

---

## Stage-by-stage aliveness

Legend: ALIVE = the correct answer was still reachable at the exit of that stage.

### banana (correct answer `fruit`), STRUCTURED arm

| # | stage | code | verdict |
|---|---|---|---|
| 1 | feature extraction | `StructuralEncoder.features`, `reading_grounding_loop.py:331-367` | **ALIVE.** `(^nsubj, fruit)` present in 2 of the 7 corpus sentences (`_probe_witness.json`), and `sym("fruit")` is bound into the encounter vector at `:380-381`. |
| 2 | ConceptSpace candidate set | `:1039-1044` + `:1279`; argmax pool at `:656` | **DEAD HERE.** `fruit` is in neither the 887-lemma seed nor the 374 grounded lemmas, so it has no row in `anchor_matrix()`. |
| 3 | similarity / argmax | `canonicalize_fast`, `:641-703` | not reachable -- no score exists for `fruit`; the winner is drawn from the other 1200-odd anchors. |
| 4 | admission gate (`SENSE_MATCH_THRESH` 0.45 / `PBV_INFORMATIVE_MIN` 0.30) | `:839`, `:701` | not reachable. |
| 5 | PBV propose/verify | `make_pbv_fns`, `:877-887`; `Library.flag`, `grounding_acquisition_loop.py:286-321` | not reachable. |
| 6 | store write / displacement | `checkpoint`, `:1277-1279` | not reachable, and no displacement occurred anywhere (below). |

### aphotic (correct answer `zone`), STRUCTURED arm

Identical table: `(^amod, zone)` is present (in 2 of 7 sentences, one of them the single feature of
that encounter), and `zone` has no row in the anchor matrix. **DEAD AT STAGE 2, the same stage as
`banana`.** The two lemmas do NOT die at different stages -- this is one defect, not two.

---

## Stage 6 checked independently: no displacement

`GROUNDED_MEANING` is FUNCTIONAL, so a second write for the same subject would silently replace the
first. It did not happen: in `arm_CONTROL_provenance.json` 384 rows carry 384 distinct subjects, and
in `arm_STRUCTURED_provenance.json` 374 rows carry 374 distinct subjects -- **zero subjects written
more than once in either arm**. The "correct answer was banked then displaced" failure mode is
excluded for this run. (Mechanism: a GROUNDED item is terminal and is short-circuited on every later
encounter, `reading_grounding_loop.py:1046-1049`.)

---

## Extension beyond n=2 (40 lemmas, deterministic sample)

n=2 is a lead. The candidate-set test extends mechanically because it needs no correctness
judgement -- only "is the syntactically isolated head available as an anchor at all".

Selection rule (deterministic, `sorted(...)` then `random.Random(42).sample`): content lemmas with
>= 4 corpus occurrences, not in the seed vocabulary, and NOT banked by the STRUCTURED arm (7,201
qualify); 40 sampled. For each, its structural features were computed with the same
`StructuralEncoder` over up to 8 of its corpus sentences, and the most frequent head filler under a
`^`-relation (`^amod / ^nsubj / ^nmod / ^appos / ^conj` -- the governor, the slot that held `fruit`
and `zone`) was tested for membership in the anchor universe.

| measure | value |
|---|---|
| lemmas for which structure isolates a head filler | **32 / 40** |
| of those, head filler present in the anchor universe at all | **11 / 32 = 0.3438** |
| all distinct structural fillers seen, across the 40 lemmas | 588 |
| of those, present in the anchor universe | **249 / 588 = 0.4235** |

So for roughly two thirds of the sampled lemmas the syntactically isolated head could not have been
output no matter what the comparator scored -- consistent with `banana` and `aphotic`, and measured
against a SUPERSET of the true anchor set (the true rate is at most this). Cases where the head IS
available (`winter -> autumn`, `destroy -> create`) are exactly the cases where the head is itself a
common seed word.

This is a candidate-AVAILABILITY rate, NOT an accuracy rate: "head filler in the anchor universe"
does not mean the head filler is the correct meaning, and "available" does not mean "selected".

---

## Two structural observations (diagnosis, not fixes)

**1. The anchor space can only grow through the loop that is failing.** A non-seed lemma becomes an
anchor only by being GROUNDED first (`:1279`), and grounding requires a standing hypothesis at
strength >= `PBV_COMMIT_STRENGTH` 0.6 (`:1176-1181`); 25,643 of 27,402 STRUCTURED refusals are
`HYPOTHESIS_BELOW_COMMIT_STRENGTH` (`metrics.json`). `fruit` (95 occurrences) and `zone` (71) are
both in that population. The set of expressible meanings is therefore pinned near the seed
vocabulary: 80-90% of all banked objects ARE seed lemmas, and the read-out's whole expressive range
is 6% of the corpus's content vocabulary.

**2. The decision variable has no first-order term for the isolated feature.** A target's own lemma
is never admitted as a filler in its own contexts -- `usable()` at `:350-352` for STRUCTURED, and
the pre-filter at `:209` for CONTROL -- so the anchor vector for `fruit` never contains
`sym("fruit")`. `banana`'s encounter vector contains `bind(REL:^nsubj, sym("fruit"))`. Those two
share no term. The score for anchor `fruit` would be a SECOND-ORDER quantity (do `banana`'s
role-bound contexts resemble `fruit`'s role-bound contexts), and the isolated feature `(^nsubj,
fruit)` contributes to it only incidentally. Isolating the right feature is therefore not, by
construction, a route to naming it -- even in the counterfactual where `fruit` were an anchor.

**Concentration, reported as an observation:** 78 of 374 STRUCTURED facts (**0.2086**) have the
object `people`, against 13 of 384 (0.0339) in CONTROL.

---

## Score gap at the argmax

**No gap is reportable for these two lemmas, and that is the finding.** The correct anchor has no
row in the anchor matrix, so there is no "correct candidate score" to subtract from the winner's.
The question "is the gap small (tuning) or large (representation)" does not apply: the failure is
not a comparison that came out wrong, it is a comparison that was never offered. Any single-lemma
gap number would be over-read; none is given.

---

## What I could NOT verify

* **The live anchor set at the exact encounter.** I verified membership against the SUPERSET (seed
  UNION all-lemmas-ever-grounded). That is exact for the NEGATIVE verdicts used here, but I did not
  reconstruct the anchor set as it stood at each individual encounter for the 40-lemma extension.
* **The per-encounter propose/verify trail for `banana` and `aphotic`** -- see the section below,
  which is filled in from a re-run.
* **Refusal reasons per lemma from the ORIGINAL run.** The cell persists refusal COUNTS
  (`metrics.json:refusal_reasons`) but not the per-lemma refusal ledger, and `state.refusals` is not
  written to disk; per-lemma reasons here come from an instrumented re-run, not from the original
  run's artifacts. The re-run reproduces the arm's construction exactly (same corpus and order, same
  `ARM_SEED` 4201, same PBV wiring, `encoder=StructuralEncoder`) but was NOT digest-checked against
  `1ce97a59c1b613d2`.
* **Whether `fruit`/`zone` were ever flagged as Library items at all** in the original run -- their
  fate (PENDING vs ESCALATED, and which refusal fired) is taken from the re-run.
* **Anything about correctness.** "The head filler is available as an anchor" is not "the head
  filler is the right meaning". No hand-scoring was done here and no quality tier is claimed.
* **Generality beyond this corpus and this seed vocabulary.** Every number above is specific to the
  34,169-sentence v5 line-aware corpus and the 1000-word base-vocabulary seed.

---

## Instrumented re-run: actual fate of the watched lemmas

FILLED IN BELOW FROM `data/exp_structured_comparator_v1/probes/downstream_trace_STRUCTURED*.json`.
