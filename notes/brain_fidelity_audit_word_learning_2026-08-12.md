# Brain-fidelity audit -- the WORD-MEANING ACQUISITION path (2026-08-12)

Scope: analysis + design only. No code written. `experiments/exp_context_conditioned_sense_selection*`
untouched (concurrent agent owns it). Written incrementally.

> **SUPERSEDED IN PART -- READ SECTION G FIRST.** Sections B.3, D and E were written before
> (i) the literature drill returned PROPOSE-BUT-VERIFY (not intersection) as the supported
> mechanism, and (ii) the sense-selection v2 re-run (`dd58dcf69`) refuted the topic-controlled
> C3 residual. Section G supersedes the fidelity table, the hypothesis verdict and the build
> order. Sections A and C stand as written.

Trigger: a full session was spent optimizing a hand-written 5-pattern surface parser
(`hdlab/definitional_extraction.py`) and fixing its parse bugs twice, without ever asking which
brain structure performs the operation. This audit applies the project's FORMALIZE discipline:
map the brain (SHAPE / POSITION / METRIC) -> per-component compare against disk -> name the gap.

---

## SECTION A -- MEASURED FACTS OFF DISK (nothing here is an estimate)

### A.1 The reading path's actual import closure

`hdlab/reading_grounding_loop.py` imports, in total:
`grounding_acquisition_loop`, `hd_fact_store`, `gap_detector`, `thematic_role_labeler`,
`closed_class_lexicon`.

`hdlab/definitional_extraction.py` imports, in total:
`closed_class_lexicon`, `thematic_role_labeler`.

`hdlab/low_information_filter.py` imports, in total: `closed_class_lexicon`.

MEASURED CONSEQUENCE -- the word-meaning acquisition path imports **none** of:
`grounded_similarity`, `lexical_similarity`, `learner`, `frame_induction`,
`word_acquisition_loop`, `random_indexing`, `coreference_resolver`, `situation_reader`.

This is the islanding finding, read off the import graph rather than asserted.

### A.2 Registry status (`data/capability_registry.jsonl`, 123 rows, read this pass)

| module | gate_decision | integration_status |
|---|---|---|
| reading_grounding_loop | WIRE | WIRED |
| definitional_extraction | VET_PENDING | WIRED |
| low_information_filter | VET_PENDING | WIRED |
| lexical_similarity (concept_canonicalization) | WIRE | WIRED |
| grounded_similarity (perceptual fallback) | WIRE | WIRED |
| frame_induction (frame_primary_role_assigner_v1) | WIRE | WIRED |
| word_acquisition_loop (increment 1) | SHELVE | -- (HARD_FAIL, shelved) |
| learner (semantic_concept_learning) | SHELVE | ISLAND |
| random_indexing | VET_PENDING | WIRED |
| gap_detector | WIRE | WIRED |
| hd_fact_store | WIRED | WIRED |

`grounding_acquisition_loop` is NOT_IN_REGISTRY despite being the engine the reading loop is
built on. Registry "WIRED" here means wired into *something*, not into this path -- A.1 is the
authority on this path.

### A.3 The argmax landscape -- `best_cos` over the 634 landed v2 facts

Source: `data/foundation/reading_grounding_v2_qualityfix/grounding_provenance.jsonl` (n=634,
every banked `GROUNDED_MEANING` fact carries the `best_cos` that won it).
`SENSE_MATCH_THRESH = 0.45` (`reading_grounding_loop.py:104`).

```
median best_cos 0.4922    mean 0.5137    max 0.7891    min 0.4501
within 0.01 of the 0.45 refusal boundary:  87/634 = 13.7%
within 0.02:                              182/634 = 28.7%
within 0.05:                              352/634 = 55.5%
within 0.10:                              491/634 = 77.4%
```

Also measured on the same rows: exposures median 6.0 (max 78); `schema_score` median 0.4075;
source sentences per fact median 6.0.

READ: the entire banked population is crammed against its own refusal threshold. The median
banked "meaning" beat the "I found nothing" verdict by 0.042 cosine. 55.5% beat it by <0.05.
This is a quantitative statement that the winner is barely separable from no-winner.

### A.4 Hand-scores (`data/exp_definitional_grounding_v3/metrics.json`, verdict
`STRUCTURAL_PASS_PENDING_B3`)

```
ARM DIST_ASIS    n_facts=634   hand_scored_MEANINGFUL_rate = 0.08  (implied 51)
ARM DIST_LOWINFO n_facts=290   (refusals NEVER_CO_OCCURS 296, LOW_INFORMATION_OBJECT 48)
ARM DEF          n_facts=1751  n_novel_vs_dist=1749
                 pattern_mix COPULA 711 / APPOSITIVE 528 / CALLED 451 / GLOSSARY_COLON 52 / REFERS_TO 9
```

The DEF arm carries **no** `hand_scored_MEANINGFUL_rate` field. The 38% DEF hand-score is
director-reported in conversation and is **NOT ON DISK** -- `notes/STATUS.md` independently flags
this. Treat 38% as unpersisted. The 8% DIST figure IS on disk and is used below.

### A.5 The director's cited numbers -- verification

| claim | status |
|---|---|
| sense selection 0.4296 vs floor 0.4316 | CONFIRMED, `notes/context_conditioned_sense_selection_2026-08-12.md:106-109` |
| median top1-top2 margin = 0.0147 | **UNVERIFIED.** No `margin` field exists in any metrics.json on disk. Every on-disk hit for the literal `0.0147` is an unrelated 2026-06 chunking/spectral result. Replaced by A.3, which measures the same intuition off real data. |

---

## SECTION B -- THE ARGMAX-vs-INVARIANCE HYPOTHESIS (verdict: PARTLY REFUTED)

The director's claim: the brain's cross-situational learning converges on what is INVARIANT
across situations, whereas `canonicalize()` takes a cosine ARGMAX over a single accumulated
context vector -- an intersection-vs-nearest-neighbour SHAPE mismatch.

### B.1 The accumulation half of the claim is WRONG

`canonicalize` (`reading_grounding_loop.py:203`) computes `new_bundle = np.sign(new_raw_sum)`
where `new_raw_sum = np.sum([t.context_vec for t in item.traces], axis=0)`
(`reading_grounding_loop.py:366`), and anchors are `np.sign(self._sums[lemma])`
(`ConceptSpace.bundle`, line 163).

`np.sign(sum of bipolar vectors)` is a **per-dimension majority vote across situations**. It is
not a mean and it is not a nearest-centroid: dimensions on which the situations disagree cancel
toward zero and contribute nothing; dimensions on which they agree survive at full amplitude.
That IS a (soft, frequency-weighted) invariance extractor. The characterization
"accumulate-and-average" does not describe this code. On the accumulation step the
implementation is closer to brain-faithful than the director believes, and saying otherwise
would send a build in the wrong direction.

### B.2 Three mismatches that ARE real, named precisely

**B.2.1 -- NO PER-SITUATION HYPOTHESIS SET (the real "intersection" gap).**
Cross-situational learning intersects a *candidate set per situation*: situation 1 licenses
{ball, dog, grass}, situation 2 licenses {ball, cup, table}, and the learner eliminates what is
inconsistent. `canonicalize` never forms a per-situation candidate set. It runs **once, at gate
time**, over `space.anchors()` -- the entire accumulated vocabulary (`reading_grounding_loop.py:205`).
There is nothing to intersect because no per-situation hypothesis sets are ever constructed.
The gap is in *candidate-set formation*, not in mean-vs-intersect. This distinction matters
because it changes the build: the fix is not a different aggregator, it is emitting a candidate
set at each encounter.

**B.2.2 -- METRIC MISMATCH (the load-bearing one).**
The brain's cross-situational learner converges on REFERENT IDENTITY -- which thing in the world
the word picks out. `canonicalize` converges on DISTRIBUTIONAL CONTEXT SIMILARITY -- which other
word occurs in similar company. These are different quantities, and the second is a
*relatedness* metric, not a *meaning* metric. `definitional_extraction.py`'s own docstring
already states this ("structurally unable to separate 'X means Y' from 'X occurs near Y'").

This mismatch makes a falsifiable prediction about the ERROR PROFILE, not just the error rate:
a topical metric should fail predominantly into RELATED, not into random NOISE, for the pairs it
does get wrong in a recoverable way. MEASURED (v2 corrected run, 50-pair hand-score,
`notes/STATUS.md` / `notes/definitional_grounding_v3_2026-08-12.md` sec 1):
**8% MEANINGFUL / 26% RELATED / 66% NOISE**. The RELATED bucket is 3.25x the MEANINGFUL bucket.
That is the metric mismatch's fingerprint: the mechanism is successfully computing the quantity
it actually optimizes (topical relatedness) and that quantity is not meaning.
A.3 supplies the second half -- the argmax that selects among those topical neighbours is
operating on a landscape where 55.5% of winners clear "nothing matched" by <0.05.

**B.2.3 -- PROPOSE-BUT-VERIFY IS IMPLEMENTED AT INTAKE AND DISCARDED AT DECISION.**
`grounding_acquisition_loop`'s docstring explicitly cites Trueswell propose-verify as the reason
traces are "kept SEPARATE per trace, never folded/averaged at intake". True at intake. But at the
decision point the traces are collapsed with a single `np.sum` (`reading_grounding_loop.py:366`).
The trace-separation is preserved right up to the moment it would have done work, then thrown
away. Half-faithful, and the unfaithful half is the deciding half.

### B.3 The director's EVIDENCE is misattributed (independent of B.1/B.2)

The director offers the 0.4296 sense-selection null as the failure `canonicalize`'s shape
predicts. It is not. That experiment
(`notes/context_conditioned_sense_selection_2026-08-12.md`) tests a *downstream* operation --
given a context, pick among senses already stored -- and it runs on the **v3 DEFINITIONAL**
facts, which `canonicalize` did not produce. More decisively, that same experiment's C3 arm
shows the retrieval mechanism WORKS:

```
sense = the bare object word the store holds     -> 0.4296  (floor 0.4316) DEAD
sense = the source sentences that sense came from -> 0.6914  (query-swap control 0.4272, lift 0.264)
```

So the sense-selection null is evidence for a **storage/representation** gap -- the fact banks a
bare object word and discards the source context, leaving nothing for a context key to match --
not for a `canonicalize` shape gap. Note also the honest cap the source note attaches to C3:
segment-free residual n=45, CI lower bound 0.4330 sits essentially on the floor; 0.6914 must not
be quoted as a clean sense-selection number.

### B.4 Verdict

PARTLY CONFIRMED, PARTLY REFUTED. There IS a genuine SHAPE+METRIC infidelity, and it is worth a
build. But (a) the accumulation step is majority-vote invariance, not averaging, so the specific
mechanism named is wrong; (b) the real shape gap is absent per-situation candidate sets, not
mean-vs-intersect; (c) the dominant defect is the METRIC (relatedness where the brain uses
reference), evidenced by the 26%-RELATED-vs-8%-MEANINGFUL error profile; and (d) the cited
evidence tests a different component, whose C3 arm exonerates the retrieval path.

---

## SECTION C -- THE CHARTER QUESTION: is the bolt-on-parser concern real or overstated?

Asked not to simply agree with the director. I do not.

**The concern as stated is OVERSTATED.** Three reasons, each checkable:

1. Learning word meaning from explicit definitional statements is a **real human mechanism**, not
   a workaround. It is the dominant route for post-childhood and technical vocabulary, and it is
   exactly the input a textbook is designed to supply -- which is the current mission's premise.
   Ruling it out would rule out the mission.
2. It occupies the **right position in the CLS architecture**, and the module already says so:
   its docstring identifies the definitional path as the one-shot hippocampal/relational bind and
   the distributional path as the slow neocortical accumulator, "the CLS pair, not competitors".
   That is brain-faithful reasoning, correctly applied, before the code was written.
3. It supplies **knowledge**, not the comprehension mechanism. The charter's line
   (supplying knowledge allowed, supplying the mechanism not) is not crossed by a module that
   reads assertions out of the text the substrate is reading. No external model is consulted at
   inference; it is glass-box and deterministic.

Corroborating measurement: the DEF arm produced 1751 facts of which **1749 were not producible by
the distributional path** (A.4). Whatever its precision, it is supplying an orthogonal signal, not
duplicating one.

**BUT there is a real fidelity violation, and it is a different one than the director named.**
The five constructions are **hand-written regexes, hand-tuned twice against a hand-score**. The
brain does not ship with five definitional patterns; it *induces* constructions from
distribution. This is the project's own `glass-box != hand-rules` line, and the second tuning
pass against the eval is fitting the evaluator.

The sharpest fact in this audit: **the repo already owns the learned-construction organ, and the
definitional extractor does not import it.** `hdlab/frame_induction.py` is registered
`WIRE`/`WIRED`, is explicitly Gleitman (1990) syntactic bootstrapping, is a *config-only* expand
of `hdlab/learner` (zero edits to learner core), and carries exactly the invariant this problem
needs: **the lemma is never a feature**, so induced constructions transfer to unseen items.
`definitional_extraction.py` imports `closed_class_lexicon` and `thematic_role_labeler` and
nothing else (A.1).

So the correct ruling is neither "the parser is fine" nor "delete the parser". It is: the
definitional path is the **right mechanism in the right position**; its **shape is wrong** because
the constructions are specified instead of induced; and the fix is to induce them through the
organ already built for inducing constructions.

---

## SECTION D -- PER-COMPONENT FIDELITY TABLE

Brain-side SHAPE/POSITION/METRIC per mechanism is pending the literature drill; the
owned/wired/matches columns below are MEASURED off disk this pass and do not depend on it.

| # | brain mechanism | owned organ | wired into word-meaning acquisition? | matches on SHAPE / POSITION / METRIC? |
|---|---|---|---|---|
| 1 | Cross-situational statistical learning | `grounding_acquisition_loop` Library/Trace + `canonicalize` | YES (this IS the path) | SHAPE partial (majority-vote invariance OK; no per-situation candidate set; traces summed at decision). POSITION OK. **METRIC WRONG** -- relatedness, not reference. Evidence B.2.2 |
| 2 | Syntactic bootstrapping (Gleitman) | `frame_induction` (+`learner`) | **NO** -- not imported by any module in the path (A.1) | organ matches on shape+metric for its own axis; simply absent here |
| 3 | Fast-mapping / one-shot relational bind | `definitional_extraction` | YES | POSITION correct (CLS one-shot arm). SHAPE WRONG -- constructions hand-specified, not induced (Section C) |
| 4 | Perceptual / sensorimotor grounding | `grounded_similarity` (Lancaster + Brysbaert, 36,810 words x 12 dims) | **NO** -- not imported by the path (A.1). Used only by the *evaluation* cell | present, idle w.r.t. acquisition |
| 5 | ATL amodal hub | `lexical_similarity.concept_similarity`, `verb_lexical_similarity` | **NO** -- not imported by the path (A.1); registered only 2026-08-12 | present, idle w.r.t. acquisition. Known cap: 16.4% of scored pairs saturate at `GROUNDED_CAP=0.45` |
| 6 | Hippocampal->neocortical consolidation | Library PENDING/ESCALATED tier + `consolidation_pass` intervening-pass rule | YES | best-matched component in the path: SHAPE (schema gate + patience + escalate-don't-force-commit), POSITION, METRIC all defensible |

Two structural notes that fall out of the table:
- The one component with a genuinely faithful implementation (#6) is gating a decision whose
  METRIC is wrong (#1). A correct consolidation gate over an incorrect quantity still banks
  incorrect facts -- which is what 8% MEANINGFUL means. Fixing the gate cannot fix this.
- #2, #4 and #5 are all present, all registered, and all absent from the import closure. This is
  the documented islanding failure mode, measured rather than suspected.

## SECTION E -- BUILD ORDER

Ranked by brain-foundational correctness. Difficulty is not an input to the ranking, per the
project's selection rule. Nothing here is a promotion recommendation; all four are proposals.

**E1. Bank the source context INTO the fact, not just the object word.**
Brain mechanism: episodic/hippocampal encoding retains the encoding context; the ATL hub
abstracts across retained episodes rather than replacing them.
Reuses: `hd_fact_store`, the `grounding_provenance` rows that already carry the sentences
(median 6 per fact, A.3), `random_indexing` as the context encoder.
Can-fail test: rerun the context-conditioned sense selection with the sense side built from the
banked context. PASS if it reproduces C3's separation from its own query-swap control.
Falsified if: accuracy stays at the 0.4316 floor, which would mean the C3 lift lived in the
held-out sentences rather than in anything storable.
Why first: it is the only step whose payoff is already measured (0.4296 -> 0.6914 dissociation,
B.3), and every later step needs a fact that carries context.

**E2. Replace the hand-written 5 patterns with INDUCED constructions.**
Brain mechanism: construction learning / syntactic bootstrapping (Gleitman 1990).
Reuses: `frame_induction`'s config-only pattern over `hdlab/learner` -- new code should be a
cue-encoder only, zero edits to learner core, and the definiendum lemma must never be a feature.
Can-fail test: hold out one of the five construction types entirely from the induction set; the
induced hypothesis must still recover it above the hand-written pattern's own precision on that
type. Held-out only -- the 38% must be persisted first (A.4).
Falsified if: induced precision falls below the hand-written baseline on held-out constructions,
which would be honest evidence that at this corpus size the constructions are not inducible and
the hand-list is the defensible interim.
Why second: it is the actual fidelity violation identified in Section C, and unlike E1 it has no
measured payoff yet.

**E3. Give cross-situational learning a per-situation CANDIDATE SET.**
Brain mechanism: hypothesis elimination across situations (B.2.1).
Reuses: `gap_detector` for novelty, `low_information_filter`'s corpus-measured PMI floor to bound
each situation's candidate set, the existing Trace structure (already per-situation, already
separate at intake).
Can-fail test: intersection-scored selection vs the current summed-argmax on the SAME traces and
the SAME hand-score rubric. PASS if MEANINGFUL rises above the on-disk 8% with the RELATED
fraction falling.
Falsified if: MEANINGFUL is flat and only NOISE moves -- that would say the defect is the metric
alone (B.2.2) and candidate-set formation is not carrying weight.
Why third: it is a real shape gap, but B.2.2 argues the metric dominates it, so it should be
measured after E1 gives it a referent-bearing target.

**E4. Wire the perceptual + ATL organs in as an acquisition-time signal.**
Brain mechanism: hub-and-spoke -- the amodal hub is constituted by convergence from modal
spokes, not consulted after the fact.
Reuses: `grounded_similarity` (coverage measured at 84.2% of the multi-sense objects),
`lexical_similarity.concept_similarity`.
Can-fail test: same hand-score rubric, grounded-profile agreement as an additional gate.
Falsified if: no MEANINGFUL lift, or if the `GROUNDED_CAP=0.45` saturation (16.4% of pairs)
destroys ranking at acquisition time the way it already does at evaluation time.
Why last of the four: it is the clearest islanding fix, but it is a re-ranking signal over
candidates the earlier steps produce, so its ceiling is set by them.

**Explicitly NOT proposed:** promoting `FHRRProcessStore`. The sense-selection cell already
adjudicated this (its Step 1) and the C3 dissociation confirms the collapse operation is not what
is broken. Its source cell carries `HARD_FAIL_PARTIAL` and its 0.9556 is a closed 3-way codebook
number that must not cross into this regime.

---

## SECTION F -- OPEN / UNVERIFIED

- Brain-side SHAPE/POSITION/METRIC rows and citations: literature drill in flight; Section D's
  brain column is deliberately unfilled rather than filled from recollection.
- DEF-arm 38% hand-score: not on disk. E2's can-fail test depends on it being persisted first.
- `median top1-top2 margin 0.0147`: no such field on disk (A.5). A.3 is the substitute measure.
- C3's segment-free residual (n=45, CI lower bound 0.4330): suggestive, not established. E1's
  band must be set against the swap control, not against 0.6914.

---

# SECTION G -- SUPERSEDES B.3, D AND E

Written after (i) the literature drill returned PROPOSE-THEN-VERIFY (PBV) as the supported
cross-situational mechanism and INTERSECTION (Siskind 1996) as having essentially no human
behavioural support, and (ii) the sense-selection v2 re-run
(`notes/context_conditioned_sense_selection_v2_2026-08-12.md`) refuted the topic-controlled C3
residual. Brain side is SUPPLIED, not re-derived here: Medina 2011 PNAS / Trueswell 2013 Cog
Psych / Woodard 2016 (commit to ONE hypothesis, carry it, confirm or abandon at the next
informative encounter, no partial credit to alternatives, abrupt switching not smooth
convergence); Medina's exposure census (~90% of natural exposures uninformative, ~7% highly
informative); Stevens 2017 Hybrid Pursuit (one hypothesis with a PERSISTING strength);
Gillette/Gleitman 1999 (verbs 15% from scene alone, 51.7% from syntax alone); Horst & Samuelson
2008 (fast mapping yields a fragile hypothesis needing re-exposure); grounding matters mainly
for CONCRETE vocabulary, ATL hub graded and category-general.

## G.1 -- PER-COMPONENT FIDELITY TABLE (supersedes Section D)

| # | brain mechanism (SHAPE / POSITION / METRIC) | owned organ | wired into the reading path? | match |
|---|---|---|---|---|
| 1 | **Single-hypothesis PBV.** SHAPE: exactly ONE carried referent hypothesis per word, no alternatives scored. POSITION: at each encounter, online. METRIC: binary confirm/disconfirm against the present encounter | `grounding_acquisition_loop.Library`/`Trace` (`:152-190`); decision made in `reading_grounding_loop._make_grounding_gate.gate` (`:358-383`) | YES -- this IS the path | **SHAPE partial, POSITION WRONG, METRIC WRONG.** Traces are kept separate at intake exactly as the docstring's Trueswell citation claims (`grounding_acquisition_loop.py:52-57`, `:152-160`), then all of them are collapsed at once by `np.sum([t.context_vec for t in item.traces], axis=0)` (`reading_grounding_loop.py:366`). Nothing is carried BETWEEN encounters; the decision is offline (consolidation pass), not at the encounter; the metric is context cosine, not confirm/disconfirm |
| 2 | **Persisting hypothesis strength** (Stevens 2017 Hybrid Pursuit). SHAPE: a scalar attached to the held hypothesis that rises on confirmation, falls on disconfirmation | none. Nearest is `LibraryItem.patience` (`grounding_acquisition_loop.py:169`, `:399-402`) | n/a | **NAME ONLY.** `patience` counts consolidation-guard FAILURES toward a give-up bound (`PATIENCE_MAX = 3`, `:86`). It never rises on evidence and is not attached to a hypothesis, because no hypothesis object exists -- `LibraryItem` (`:162-169`) has fields `lemma / traces / status / first_min_confirm_pass / patience` and no hypothesis field |
| 3 | **Abandon-on-disconfirmation, then RE-PROPOSE.** POSITION: at the disconfirming encounter. METRIC: the encounter contradicts the held hypothesis | `ESCALATED` terminal status + `Library.flag`'s terminal no-op (`:186-190`, `:399-402`); `REFUSAL_TAUTOLOGY` refusal ledger (`reading_grounding_loop.py:369-374`) | YES | **SHAPE partial, POSITION WRONG.** Escalate-don't-force-commit is genuinely faithful as a *refusal*, and refusals are ledgered rather than dropped. But it fires on repeated offline coherence-guard failure, not on a disconfirming encounter, and it is TERMINAL -- an escalated item accepts no further traces (`:186-190`) and no new hypothesis is ever proposed. PBV abandons and re-proposes in the same act |
| 4 | **Informative-encounter selection** (Medina: ~7% highly informative). SHAPE: a filter over encounters. POSITION: upstream of the mapping decision. METRIC: referential clarity of the encounter | `definitional_extraction` (5 patterns), `low_information_filter` (PMI floor) | YES | **POSITION CORRECT, SHAPE WRONG.** See G.3: the function is brain-supported; the constructions are hand-specified and hand-tuned twice against the eval, and their output is banked directly rather than proposed to a verify step |
| 5 | **Syntactic bootstrapping.** METRIC: the frame, not the scene -- 51.7% syntax-only vs 15% scene-only (Gillette/Gleitman 1999) | `frame_induction` (+`learner`), registered WIRE/WIRED | **NO** -- not in the import closure (A.1) | absent. The measured 51.7-vs-15 asymmetry says the ABSENT organ carries the stronger signal and the wired one the weaker |
| 6 | **Cross-situational intersection** (Siskind 1996) | none | n/a | **correctly absent.** No human behavioural support; see G.2 -- this retracts B.2.1 and E3 |
| 7 | **Fast mapping is fragile, needs re-exposure** (Horst & Samuelson 2008). SHAPE: bind now, require later re-encounters before it is durable | `MIN_CONFIRM = 4` (`:81`), Dumay-Gaskell intervening-pass rule (`:357-358`), `PROMOTE_MIN_EXPOSURE = 8` (`:87`) | YES | **best-matched component in the path** -- SHAPE, POSITION and METRIC all defensible. Unchanged from D#6 |
| 8 | **ATL hub: graded, category-general, amodal; grounding load-bearing mainly for CONCRETE vocabulary** | `lexical_similarity.concept_similarity`, `grounded_similarity` (Lancaster + Brysbaert) | **NO** -- not in the import closure (A.1) | present, idle. NEW CAVEAT vs D#4/D#5: because grounding is concrete-biased, the expected payoff of wiring these is bounded to the concrete subset, not to the vocabulary at large |

Two consequences that change the read from Section D:
- The infidelity is not "argmax where the brain intersects" (D#1's METRIC row). It is that the
  path has **no hypothesis object at all** -- rows 1, 2 and 3 are three faces of one absence.
- Row 7 remains the one faithful component, and it now looks worse, not better: a well-shaped
  re-exposure requirement is accumulating exposures for a decision procedure that never holds a
  hypothesis to re-expose.

## G.2 -- THE ARGMAX VERDICT (supersedes B.2.1 and B.3)

**Yes. `canonicalize()`'s argmax is CLOSER to PBV than the director's proposed intersection.**
Argmax returns exactly one winner and gives zero credit to the runner-up
(`reading_grounding_loop.py:204-218`: a single `best_anchor`, no candidate set, no score
retained for any alternative). "Commit to one, no partial credit to alternatives" is PBV's
defining shape. An intersection scorer maintains a SET of surviving candidates across
situations -- which is precisely the mechanism Siskind 1996 formalized and which has essentially
no human behavioural support. **B.2.1 was therefore backwards, and E3 is retracted:** building
per-situation candidate sets would move the substrate AWAY from the supported mechanism. The
absence of candidate sets is fidelity, not a gap.

What the argmax still lacks -- three named absences, each verified on disk:

1. **No persistent hypothesis across encounters.** `canonicalize` runs ONCE, at gate time, over
   the whole of `space.anchors()` (`:205`), called from a single site in the consolidation gate
   (`:367`). Between encounters nothing holds a chosen referent: `LibraryItem`
   (`grounding_acquisition_loop.py:162-169`) stores traces, status, a pass index and a patience
   counter -- no hypothesis field. Stevens' persisting strength has no carrier.
2. **No explicit verification event.** There is no operation of the form "does THIS encounter
   confirm the standing hypothesis?". The nearest thing, `schema_consistency_split_half`
   (`:193-241`), tests whether an item's own traces cohere with EACH OTHER -- an internal
   reliability statistic, not a confirmation of a hypothesis by an encounter. Coherence among
   traces is exactly what a wrong-but-topically-consistent hypothesis also produces.
3. **No abandon-and-re-propose.** `ESCALATED` (`:400-402`) is terminal and `Library.flag`
   refuses further traces on a terminal item (`:186-190`). PBV's abandonment is not an exit; it
   is immediately followed by a new proposal at the same encounter. Nothing in the path
   re-proposes.

**Does that gap PREDICT the measured sense-selection failure? No.** I am using the v2 primary
arm: `subject` index, S2_PERC **0.4809** against floor **0.4634**, and decisively the **C1 swap
drop of 0.0100** against the pre-registered 0.05 requirement (C2 lesion 0.4564). The C1 number
is the one that adjudicates this. A missing-PBV gap predicts that the substrate commits to the
WRONG referent -- but a wrong-yet-real referent would still make the stored fact respond
differently to a right context than to a swapped one. C1 says it does not: right context and
wrong context yield near-identical accuracy. That is context-INSENSITIVITY, and the mechanism
that predicts context-insensitivity is the storage shape (the fact banks a bare object word;
`gate` at `:380-382` carries `canonical_obj` forward and the source sentences are not part of
the stored fact), not the hypothesis machinery.

So the PBV gap is real (G.1 rows 1-3) but the sense-selection cell is not its evidence. Its
evidence is the on-disk 8% MEANINGFUL / 26% RELATED hand-score (A.4, B.2.2), which is a
measurement of the mapping decision itself.

**And B.3's counter-claim is withdrawn with the same stroke.** B.3 argued the sense-selection
null exonerated the retrieval path because C3 worked. Under topic control it does not: C3-SEG
on the primary index is **0.5714, n=49, CI [0.4327, 0.6998]**, whose lower bound is BELOW the
0.4634 floor. Raw C3 remains swap-separated but is topic-confounded, which is the confound v2
was built to remove and did. Net: the sense-selection experiment now supports neither the
director's claim nor my B.3 rebuttal; it establishes only that the stored bare object word
carries no context-matchable signal. The practical cost is in G.4 -- E1's "payoff already
measured" justification is gone.

## G.3 -- CHARTER RULING ON THE HAND-WRITTEN 5-PATTERN PARSER

**Ruling, plainly: NOT a charter violation in FUNCTION. It IS a violation in WIRING, and
separately in FORM.** I disagree with the director's framing, and I also correct my own
Section C on one point.

**Function: legitimate, and now positively brain-supported.** Medina's census -- ~90% of natural
exposures uninformative, ~7% highly informative -- means PBV cannot work at all unless the
learner has a way of telling which encounters are worth committing on. Informative-encounter
selection is not a workaround bolted beside the mechanism; it is a REQUIRED upstream component
of the mechanism. Selecting explicit definitional sentences is one concrete realization of it.
The charter line "no bolt-on reader/parser AS the comprehension organ" is not crossed by a
selector, and Section C's positional argument (right arm of the CLS pair) stands.

**Wiring: violating, and this is the part Section C got wrong.** Section C ruled the parser
"supplies knowledge, not the comprehension mechanism". That is true only if its output is a
PROPOSAL that some verify step then confirms or rejects. It is not. The DEF arm banks 1751
facts (A.4) straight out of the pattern match; nothing downstream can disconfirm a pattern hit.
A selector whose output IS the banked meaning, unverified, is being used as the comprehension
organ -- which is exactly the charter's line, reached by a route neither the director nor
Section C named. The fix is not deletion: it is demoting the parser's output from FACT to
HYPOTHESIS and routing it into the verify step G.4.1 builds.

**Form: violating, unchanged from Section C.** Five hand-written constructions, hand-tuned
twice against a hand-score, is `glass-box != hand-rules` and is fitting the evaluator. The
Gillette/Gleitman asymmetry sharpens this rather than excusing it: 51.7% from syntax alone
versus 15% from scene alone says the syntactic/constructional route carries the DOMINANT signal
for verbs, so the component doing that work is the last one that should be a frozen hand-list,
and the owned induction organ (`frame_induction`, lemma-never-a-feature, config-only over
`learner`) is the right place to earn it. Credit where due -- that organ exists and is
registered; the extractor simply does not import it (A.1).

Summary of the ruling: KEEP the definitional path, DEMOTE its output to a proposal, INDUCE its
constructions. Neither "the parser is fine" nor "delete the parser".
