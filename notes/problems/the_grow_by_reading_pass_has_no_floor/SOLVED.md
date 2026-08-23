---
problem: the_grow_by_reading_pass_has_no_floor
status: SOLVED
bar: "THE TRIVIAL ARM AND THE REAL ARM SCORED ON THE SAME SURVIVING SENTENCES, PRECISION REPORTED SIDE BY SIDE, WITH A CI ON THE DIFFERENCE."
result: "Real extractor 0.90 (90/100 hand-adjudicated survivors) vs strongest genuinely-trivial floor first_noun_after_verb 0.7053 (67/95 emitted) on the SAME 100 survivor items; paired real-minus-floor +0.23, 95% CI [+0.13, +0.33], McNemar exact p=2e-5. The 0.90 is NOT a pure selection artifact -- but a 2-line voice-aware rule already reaches 0.83, so most of it is filter-selection plus a trivial rule, not the sophisticated reading."
floor: "Strongest genuinely-trivial floor = first_noun_after_verb = syntactic_object_no_filter = 0.7053 precision-over-emitted (0.67 acc over 100). Also: nearest_noun_to_verb 0.70; information-free constant twin most_frequent_entity 0.09. Filter-contribution DIAGNOSTIC voice_aware_adjacency (the real arm's candidate step minus all 6 filters) = 0.83, real-minus-it CI [0.00, 0.14] -> NOT CI-separated."
controls: "(a) info-free constant twin (most_frequent_entity='water') scores 0.09, CI-separated below real [+0.73,+0.88] -- the mandated info-free-loses control; EXCLUDES all sentence content. (b) A0 reproducibility: extract_facts_strict reproduces 99/100 recorded facts on the isolated survivor sentences, so the saved 100-item sample IS the scorable survivor population; EXCLUDES corpus-context effects and the need for a full re-run. (c) exact-match inheritance: 292 trivial facts identical to the real arm's own fact inherit the ORIGINAL human C/W label (witness-verified, no relabel); EXCLUDES annotator drift on identical facts. (d) voice_aware_adjacency diagnostic decomposes the 0.90 into filter-selection vs reading; EXCLUDES the 6 filters/role-labeling/concreteness."
files_changed: "experiments/exp_grow_by_reading_trivial_floor_v1.py, experiments/exp_grow_by_reading_trivial_floor_score_v1.py, verification/test_grow_by_reading_trivial_floor.py, data/exp_grow_by_reading_trivial_floor_v1/ (metrics.json, metrics_scored.json, _per_item.json, _adjudication_worklist.json, _adjudicated_population.json), notes/problems/the_grow_by_reading_pass_has_no_floor/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_grow_by_reading_trivial_floor.py"
---

# SOLVED: a floor now sits under the grow-by-reading pass, and the pass clears it -- but barely more than a two-line rule does

## HEADLINE

The 0.90 hand-adjudicated precision on the goal-bearing "grow by reading" cell now has a floor
under it, run on the **same 100 survivor sentences** the 0.90 was measured on:

| arm (same 100 survivors) | precision | vs real: paired 95% CI |
|---|---|---|
| **real extractor** (the pass) | **0.90** (90/100) | -- |
| voice_aware_adjacency *(diagnostic, see below)* | 0.83 | real-it **[0.00, +0.14]  NOT separated** |
| **first_noun_after_verb** *(strongest trivial floor)* | **0.7053** (67/95) | real-floor **[+0.13, +0.33]  separated** |
| syntactic_object_no_filter | 0.7053 (67/95) | [+0.13, +0.33]  separated |
| nearest_noun_to_verb | 0.70 (70/100) | [+0.11, +0.29]  separated |
| most_frequent_entity *(info-free twin, constant "water")* | 0.09 (9/100) | [+0.73, +0.88]  separated |

**The 0.90 is not a pure selection artifact** -- the real extractor beats the strongest genuinely-
trivial extractor by +0.23, CI-separated, McNemar p=2e-5. **But the number that actually matters for
the project is 0.83:** a two-line voice heuristic (grab the noun before the verb on a passive, after
it on an active -- no filters, no role-labeling, no concreteness) already reaches 0.83 on the
survivors, and the real arm's entire sophisticated machinery adds only +0.07 beyond it, an increment
that is **NOT CI-separated** at n=100. So the honest reading is: **the filters do the heavy lifting
by selecting easy sentences, a trivial rule does most of the rest, and the fancy reading adds a
sliver that this sample cannot distinguish from zero.**

## DISK OUTRANKS THE BRIEF: no re-run was needed

The brief (§6) and the source write-up say the survivors "were not persisted, so this needs a RE-RUN
of the extractor" and to "price the re-run before starting." **That is only partly true and the
cheaper path was available.** The full 1,414 survivors were not saved, but the **exact 100-item
hand-check sample WAS** -- with full sentence text -- in
`data/exp_stated_entity_fate_reading_extractor_v2_highprecision/_survivors_for_handcheck.json`, and
the labels in `_survivors_handcheck_adjudicated.json`. Running `extract_facts_strict` on those
isolated sentences reproduces **99/100** of the recorded facts (the 1 miss is the already-Wrong
`noun_misparsed_as_verb` item). So the trivial arm could be scored on **the same items the real arm
was scored on** -- the bar's own "ideally the same items" -- with no corpus re-run. Priced: ~13s to
load the cached frontend, seconds to score.

## WHAT I BUILT

1. `experiments/exp_grow_by_reading_trivial_floor_v1.py` -- loads the 100 saved survivors + their
   original C/W labels, runs pre-named trivial arms on each, and emits a fresh-adjudication worklist.
   Every arm is **anchored to the same verb + fate the real arm used** and varies *only the entity-
   selection rule* -- because the "fact" is `(entity_head, fate)`, `fate` is a deterministic verb-
   lexicon lookup, and **all 10 of the real arm's hand-check errors are wrong-patient (entity)
   errors, never fate errors.** So the trivial floor probes exactly the axis the errors live on.
   - `first_noun_after_verb`, `syntactic_object_no_filter`, `nearest_noun_to_verb` -- the brief's
     three named baselines (POS/parse only, no filters).
   - `most_frequent_entity` -- the brief's "most frequent patient type"; the information-free twin.
   - `voice_aware_adjacency` -- a DIAGNOSTIC, not a trivial floor: it is the real arm's candidate-
     selection step with all six filters, role-labeling and concreteness stripped, to decompose the
     0.90 into "filters selecting clean sentences" vs "genuine reading".
2. `experiments/exp_grow_by_reading_trivial_floor_score_v1.py` -- folds in the adjudication and
   scores. Adjudication provenance: **292 tuples inherited the ORIGINAL human label** (the trivial
   fact was byte-identical to the real arm's fact), **198 tuples I hand-labelled** by the same
   protocol, each with a one-line reason embedded in code, 10 no-emits.
3. `verification/test_grow_by_reading_trivial_floor.py` -- scaffold-free witness that recomputes the
   headline independently from the saved JSON (pure-python bootstrap, different RNG) and checks the
   inheritance did not relabel the real arm's own judgements. All checks pass.

## WHAT I MEASURED, AND THE DECOMPOSITION

Reading the numbers as a chain lifts the fog off the 0.90:

- **Raw prose, real extractor: 0.394** (from the source cell -- pre-filter).
- **Survivors, genuinely-trivial extractor (first noun after the verb): 0.70.** The six filters lift
  even a stupid extractor from ~0.39 on raw prose to 0.70 on survivors. **That gap is the filters
  selecting easy sentences** -- exactly the worry the brief was built around, now measured.
- **Survivors, trivial voice+adjacency rule: 0.83.**
- **Survivors, real extractor: 0.90.**

The real arm clears the strongest *genuinely-trivial* floor CI-separated (+0.23), so the pass is not
an artifact. But the increment of the real arm's full apparatus over a two-line voice rule is +0.07
and not CI-separated -- the sophisticated patient-role labeling, PP/by-agent rejection, causative
guard and concreteness gate buy little **on the already-filtered population** beyond "know the voice,
grab the adjacent noun."

Where the trivial arms failed is diagnostic and consistent: `first_noun_after_verb` misses on
**passives** (grabs a location/agent after the verb instead of the subject patient -- e.g.
"Mineralocorticoids are produced in the adrenal cortex" -> grabs "cortex"), and `voice_aware_adjacency`
misfires on **copula+infinitive** ("their job is to pump blood" -> grabs "job"), which the real arm's
infinitival-purpose guard handles. Where the trivial arms *beat* the real arm: they picked a
different-but-also-true fact on 4 items the real arm got wrong or where two entities share a fate
(e.g. "make a neutral salt solution" -> `solution` CREATE is correct; the real arm emitted the
reactant `base`). I gave the floor credit for those, which makes the floor *higher* and the real
arm's margin *more conservative*.

## BRAIN-FOUNDATIONAL READING (added on review): the error structure maps onto the brain's parsing boundary

The brief (§10) pins the TASK as brain-relevant (building a situation model / event structure from
language -- thematic-role assignment, which the brain does during comprehension) and flags the
MECHANISM (six hand-written syntactic filters) as OURS-UNDER-TEST. This floor experiment is
measurement hygiene, not brain science -- but the *result* has a clean brain-foundational signature,
so I stratified by voice to test it.

**Good-enough / heuristic parsing** (Bever 1970; Ferreira 2003; Townsend & Bever) says the brain
comprehends *canonical* (active, word-order-transparent) sentences with a fast agent-verb-patient
heuristic, and only recruits effortful syntactic analysis (left inferior frontal / Broca's) for
*non-canonical* sentences -- passives, object-relatives, semantically reversible sentences -- where
agent and patient cannot be read off word order. Prediction: a positional heuristic should ~tie the
real extractor on actives and collapse on passives, and the real arm's value should live entirely in
the non-canonical stratum.

| stratum (n=100) | n | real | first_noun_after_verb (heuristic) | real - heuristic, paired 95% CI |
|---|---|---|---|---|
| **active** (canonical) | 68 | 0.956 | 0.941 | +0.015, [0.00, +0.04] **not separated**, p=1.0 |
| **passive** (non-canonical) | 32 | 0.781 | 0.094 | **+0.688, [+0.44, +0.88] separated**, p=3e-5 |

**Confirmed, sharply.** On canonical actives, "grab the noun after the verb" is statistically
indistinguishable from the full apparatus (both ~0.95). On passives the heuristic collapses to 0.094
(it grabs the location/agent after the verb instead of the subject patient), and the real arm's
voice-handling wins by +0.69. **The entire +0.23 aggregate margin is carried by the passive stratum**
-- exactly the canonical/non-canonical boundary at which the brain switches from heuristic to
effortful parsing. So the mechanism, however un-brain-like its *implementation* (hand-written
filters), has an *error profile that tracks the brain's own division of labour*: it earns its keep
precisely where word order stops being sufficient. That is the most brain-foundational thing this
number can say, and it was invisible before the floor was run.

## WHAT I DID NOT ESTABLISH

- **Not the full 1,414.** This is n=100 -- the same fresh random sample the 0.90 was measured on
  (representative of the survivors), not the whole surviving set. The CIs are n=100 CIs. Extending to
  1,414 would need the re-run the brief priced; the bar did not require it and "the same items" is
  the stronger comparison.
- **Single-annotator on the 198 fresh calls.** The 292 exact-match tuples carry the ORIGINAL
  adjudicator's labels; the 198 novel (entity,fate) tuples are my judgement under the same protocol.
  A second annotator could move a handful. The +0.23 margin over the trivial floor is wide enough to
  survive plausible disagreement; the +0.07 over the voice diagnostic is not, and I do not claim it.
- **Not a claim that grow-by-reading is viable.** Per the brief's DO NOT QUOTE, that verdict is not
  established by this cell, and this floor does not establish it either. What is established: the
  0.90 beats a trivial floor, and most of it is selection + a trivial rule.

## WHAT I WOULD WITHDRAW FIRST IF WRONG

The **+0.23 real-minus-trivial margin**, if my 198 fresh adjudications are biased against the trivial
arms. Mitigation already in place: I inherited the original labels wherever the fact was identical
(292 of 490 arm-facts), and I resolved every genuinely-ambiguous "different-but-true" call *in the
floor's favour*, so the bias runs the other way. The claim I would defend last, because a witness
recomputes it from disk, is the arithmetic and the info-free-twin loss.

## PROPOSED hdlab CHANGE (a result, not a landed diff -- Q111)

Nothing in `hdlab/` needs to change to *fix* a defect; the extractor works as documented. The change
this result argues for is **interpretive and belongs in how the cell's verdict is recorded**: the
`final_verdict_msg` string `HARD_PASS_CLEAN_GROW_BY_READING_VIABLE` should be qualified to note that
(1) on the surviving population a trivial extractor scores 0.70 and a two-line voice rule 0.83, and
(2) the real arm's margin over the strongest trivial floor is +0.23 CI-separated but its margin over
the voice rule (+0.07) is not. Concretely, the strategy session may wish to add a floor field to that
cell's `metrics.json` (`trivial_floor_first_noun_after_verb: 0.7053`, `voice_aware_adjacency: 0.83`)
so the number never again travels without its floor. That is a metadata annotation on a landed
`metrics.json`, which is the strategy session's to land, not mine.

## TLDR

We had an experiment that reads plain sentences and pulls out what happened to things, and it got 90
out of 100 right -- but only on sentences it had already filtered down to one third of the original,
and nobody had checked what a dumb method scores on those same easy sentences. I checked, on the exact
same 100 sentences. A dumb method (just grab the noun next to the action word) gets about 70; a
slightly-less-dumb method that also notices whether the sentence is "X did Y" or "Y was done" gets
about 83; the real system gets 90. So the real system is genuinely better than the dumbest baseline
(and that difference is statistically solid), but the filtering step is doing most of the work by
throwing away the hard sentences, and a two-line rule closes almost all of the remaining gap. The
"90%" is real, not a mirage -- but it is much less impressive than it sounds, and it is now on record
with a floor beneath it so it can't be quoted bare again.

## QUESTIONS

None.

## NEXT STEPS

1. **The brain-framed lever is recall on NON-CANONICAL sentences.** The filters buy precision by
   discarding two thirds of the output, and the discarded set is disproportionately the hard,
   non-canonical sentences -- which is exactly where the deep-reading machinery (and the brain's
   effortful parser) earns its place. On the surviving population the mechanism is only tested on 32%
   passives; a positional heuristic handles the rest. The real question for grow-by-reading is whether
   the syntactic machinery holds precision as the filters admit MORE non-canonical sentences (object-
   relatives, reversible SVO, coordination) -- a recall-vs-precision curve stratified by canonicity,
   not another aggregate precision point.
2. If the +0.07 real-over-voice-rule increment matters to a downstream decision, it needs the full
   1,414 (or a larger fresh sample) and a second adjudicator to become CI-separable or be declared a
   tie -- cheap now that the harness exists.
3. A **semantic-reversibility** stratum (irreversible "acid dissolves metal" vs reversible "X produces
   Y") would be the cleaner brain test than voice, since reversibility is what forces the brain onto
   syntax; it needs per-item reversibility judgements (annotator load) and more n than 100 to resolve.
