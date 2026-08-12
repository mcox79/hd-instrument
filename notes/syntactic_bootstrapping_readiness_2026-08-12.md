# Syntactic bootstrapping: readiness assessment (2026-08-12)

READ-ONLY audit. No code changed. All numbers read off disk this session; every claim carries a
path. Registry rows were NOT trusted as evidence (three WIRE rows were demoted on inspection
earlier this session); metrics.json is the referent throughout.

WHY ASKED: `notes/brain_fidelity_audit_word_learning_2026-08-12.md` Section G ranks wiring
syntactic bootstrapping a top build step on literature payoff (Gillette/Gleitman 1999 human
simulation: verb ID ~15% from scene/co-occurrence vs 51.7% from syntax alone, 3.4x, largest for
mental + perception verbs). Our reading path is co-occurrence-driven and noun-biased, so verbs
should be exactly where we are weakest. The question is whether the organ we already have can
close that, on OUR data.

---

## 1. FIND IT -- where the capability actually lives

MODULE: `D:/AI/hd-instrument/hdlab/frame_induction.py` (570 lines, dated 2026-08-04).
Self-described as "OOV VERB THEMATIC-FRAME INDUCTION -- FEATURE ENCODER ONLY (config-only EXPAND
of hdlab/learner)", explicitly citing Gleitman (1990) syntactic bootstrapping. The
config-only-reuse claim checks out on inspection: it imports `hdlab.learner.registry` and
`hdlab.thematic_role_labeler` and adds no learner-core edits; the real-data cell records
`hdlab_learner_core_registry_plugins_edited = false`.

TWO CELLS produced the claim, and they disagree. Both were read in full.

(a) TEMPLATED / mechanism demo --
`D:/AI/hd-instrument/data/exp_frame_induction_oov_psych_v1/metrics.json`
  run_mode=full, verdict=**HARD_PASS**
  verdict_msg (verbatim): "HARD_PASS: held-out-novel experiencer-axis acc=0.667 (>=0.55), beats
  default-AGENT (0.000) + position-majority (0.000), scramble collapses (delta=0.333).
  Induced=ruleind. Construction signal, not position."
  Scale: 609 train episodes, 4 held-out verbs (cherish/loathe/crave/covet), **12 held-out
  episodes**. The cell's own `supplied_vs_earned` field says: "corpus is templated (mechanism
  test, not a real-corpus capability claim)."

(b) REAL TEXT --
`D:/AI/hd-instrument/data/exp_frame_induction_oov_psych_real_v1/metrics.json`
  run_mode=full, verdict=**MIDDLE_BAND**
  verdict_msg (verbatim): "overall=MIDDLE_BAND (worse-of-axes). SUBJ-axis: acc=0.8333333333333334
  N=12 tier=MIDDLE_BAND beats_default=True beats_position=False (pos_acc=1.0). OBJ-axis (hard
  case): acc=0.45454545454545453 N=11 tier=MIDDLE_BAND beats_default=True beats_position=False
  (pos_acc=0.5454545454545454). scramble_delta=0.30434782608695654 scramble_collapses=True.
  Induced=ruleind. Real litbank-mined data, NOT templated."
  Data: `experiments/data/experiencer_narrative_roles_v1.jsonl` (litbank-mined + supplements),
  176 train episodes, 12 + 11 held-out sentences.

So the honest one-line status: **HARD_PASS on a templated corpus, MIDDLE_BAND on real text.** The
"PROVED" framing is true only of (a).

### The real-data result is worse than MIDDLE_BAND sounds

On real text the organ **loses to a trivial position baseline on BOTH axes**:
  subj axis: induced 0.833 vs position-majority **1.000**
  obj axis:  induced 0.455 vs position-majority **0.545**
It beats only `default-AGENT` (0.000 on both), which is a floor, not a baseline.

And the induced hypothesis itself explains why. Read off
`induced_hypothesis` in the real-data metrics, the top-coverage rules are:
  `["arg_animate","passive"] -> EXPERIENCER` (cov 6, prec 1.0)
  `["order_pre","arg_animate"] -> EXPERIENCER` (cov 47, prec 0.894)
  `["order_pre","degree_mod"] -> OTHER` (cov 6, prec 0.833)
Every high-coverage conjunct is built from `order_pre` (position) and `arg_animate` (animacy).
The genuinely syntactic cues -- `has_scomp`, `degree_mod`, `progressive` -- are near-inert.
Compression ratio collapses from 8.69 (templated) to **1.45** (real), i.e. the learner found
almost no structure to compress.

The charter's recorded verdict -- "on sparse real data collapses to a position+animacy proxy =
data-starved, MIDDLE" -- is **ACCURATE**. Confirmed independently here off metrics.json.

**Honest statement, per the brief: the mechanism exists, and it has never beaten a trivial
baseline on real text.**

### A second, independent negative on the same idea

`data/capability_registry.jsonl` row `grounded_word_acquisition_loop_increment1`
(`hdlab/word_acquisition_loop.py`, which is explicitly built on "the EXACT
hdlab.frame_induction.py pattern") is `built_measured_HARD_FAIL_shelved_2026-08-06`, and its
standing finding is directly on point: Channel A (structural syntactic-bootstrapping) carries NO
genuine polarity signal -- MEASURED, every construction-cue signature ~50/50 POS/NEG across 249
real seed-corpus episodes (129 POS / 120 NEG). Different axis (verb valence, not thematic frame),
but the same mechanism failing on real data for the same reason.

Two independent real-data measurements, both null-to-weak. This is not a one-off.

---

## 2. WHAT IS THE ACTUAL CAPABILITY?

INPUT (from the module's public API docstring): `episode_feats(tokens, v_idx, subj_idx, pos=None)`
-- a tokenized sentence PLUS the integer index of the verb PLUS the integer index of the subject
argument. It therefore presupposes an upstream parse that has already located the predicate and
its argument.

FEATURES: four declared boolean construction atoms,
`CONSTRUCTION_ATOMS = ["has_scomp","degree_mod","progressive","order_pre"]` (the real-data adapter
adds `passive`, `arg_animate`). The verb lemma is deliberately never a feature -- that is what
makes the induced rule transfer to an unseen verb, and it is a genuinely good design choice.

OUTPUT: `predict_subj_role(...) -> str`, a **single thematic role label for one argument**,
drawn from {AGENT, EXPERIENCER} (templated) or {EXPERIENCER, OTHER} (real). That is the entire
output. It is a 2-way role tag on an argument slot.

VALIDATED ON: 12 templated held-out episodes over 4 psych verbs (HARD_PASS); 12 + 11 real
litbank-mined sentences over 5 + 5 held-out psych verbs (MIDDLE_BAND, loses to position). N is
tiny in both. The real cell sets `small_n_cap_threshold = 8`, i.e. the cell itself flags the
small-N regime.

Note the scope gap against the literature that motivated this. Gleitman's 51.7% is verb
IDENTIFICATION -- narrowing *which verb meaning* a novel form has from its frame. This organ does
not identify a verb; it labels one argument of an already-located verb as EXPERIENCER or not.
That is a downstream consumer of syntactic bootstrapping, not the bootstrapping result itself.

---

## 3. IS IT WIRED?

`tools/integration_health.py` re-run fresh this session (the tool was fixed today -- bare
cell-to-cell import detection, per `notes/island_harvest_assessment_2026-08-12.md`; old counts
not cited). Header: `5735 exp cells, 140 hdlab modules`. Section [3] DEAD hdlab MODULES lists 8
modules with ~0 consumers: `_scratch_orig_goal_owner_select, compose_freq_routing, excitability,
harness, k_cliff_scaling, lock_in_amp, profiling, self_manager`. **`frame_induction` is NOT among
them.**

Direct consumer count (grep, source files only, `__pycache__` excluded):
  hdlab consumers (5): `situation_reader.py`, `word_acquisition_loop.py`, `goal_typing.py`,
  `result_type_induction.py`, `goal_outcome_relation.py`
  experiments/ consumers: 20 cells

**So "it is now islanded" is FALSE and should be corrected wherever it is recorded.** The organ
is wired -- into the Component-3 / Component-5 situation-reading stack. Registry row
`frame_primary_role_assigner_v1` says `integration_status=WIRED`,
`pipeline_status=WIRED_BUT_NOT_PIPELINE_REACHABLE`, and on this point the registry agrees with
disk.

The accurate statement is narrower and more useful: **it is wired to the situation-reader stack
and DISCONNECTED FROM THE READING PATH.** `hdlab/reading_grounding_loop.py`,
`hdlab/gap_driven_reader.py` contain zero references to `frame_induction` (grep, no hits). That
is the gap -- a wiring gap between two live subsystems, not an island.

---

## 4. CAN IT SERVE THE READING PATH?

The reading path proposes a meaning per encounter through
`hdlab/reading_grounding_loop.py::canonicalize` (L222):

```python
def canonicalize(new_lemma: str, new_raw_sum: np.ndarray, space: ConceptSpace,
                 thresh: float = SENSE_MATCH_THRESH,
                 eligible: Optional[Callable[[str], bool]] = None) -> Tuple[str, float]:
```

**NAMED INTEGRATION POINT: the `eligible` predicate of
`hdlab/reading_grounding_loop.py::canonicalize` (L222-224), with its fast-path mask
`_eligible_mask` (L303) and the caller `process_sentence` (L469).**

This is genuinely the right seam and it already exists -- it was added today for closed-class
filtering (`hdlab.closed_class_lexicon.is_eligible_meaning`), and it does exactly the shape of
thing wanted: it restricts WHICH anchors are eligible to be the proposed meaning. So the seam is
real. Three concrete obstacles sit on it, and none is cosmetic.

**(i) The predicate signature carries no frame.** `eligible` is `Callable[[str], bool]` over an
ANCHOR LEMMA. A frame constraint is a property of the current ENCOUNTER, not of the candidate
anchor. It could be supplied as a per-encounter closure without changing the signature -- but see
(ii).

**(ii) `_eligible_mask` caches on anchor COUNT and would silently serve a stale mask.** From its
own docstring (L303-306): "Recomputed only when the anchor COUNT changes (anchors are only ever
added, and the predicate is a pure function of the lemma)". A frame-conditioned predicate is NOT
a pure function of the lemma. Passing one through the fast path yields the FIRST encounter's
frame mask applied to every later encounter -- a correctness bug that would not throw and would
not obviously show in aggregate metrics. Any wiring must address this cache invariant explicitly.

**(iii) The organ's output type does not fit the slot -- this is the blocking one.** `eligible`
needs a predicate over candidate MEANINGS. `frame_induction` returns a thematic ROLE for an
argument, from a 2-element vocabulary. There is no function from {EXPERIENCER, OTHER} to a
restriction over anchor lemmas. To supply the constraint Gleitman's result is about ("this frame
means the novel verb is a mental-state predicate, so restrict its meaning to psych anchors") the
organ would have to output a semantic CLASS over verb meanings, which it does not compute.
Separately, its input contract needs `tokens, v_idx, subj_idx` -- a located predicate and
argument -- and the reading path operates on `content_lemmas` / masked context vectors (L140,
L146) with no dependency parse in the loop, so the indices are not available either.

Assessment: **the seam is right, the organ does not fit it.** This is real work -- a new
frame-to-meaning-class mapping plus a parse hop into the reading loop plus a cache-invariant fix
-- not a config-only reuse.

---

## 5. IS OUR DATA ADEQUATE? (the decisive measurement)

Gleitman's effect is about VERBS. Measured directly, two stores, this session.

**(a) Current definitional reading path** --
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`, 2092 facts, all
`relation=GROUNDED_MEANING`. Each fact's `definiendum_surface` was located in its own
`source_sentences[0]` and POS-tagged in context with spaCy `en_core_web_sm` (2068 of 2092 located;
24 unmatched):

| POS of definiendum | count | share |
|---|---|---|
| NOUN | 1380 | 66.7% |
| PROPN | 580 | 28.0% |
| **VERB** | **48** | **2.3%** |
| ADJ | 29 | 1.4% |
| ADV | 28 | 1.4% |
| other | 3 | 0.1% |

**2.3% is an upper bound, and hand-inspection collapses it to approximately zero.** All 48
VERB-tagged facts were pulled and 20 read. Not one is a verb definition. They split into
(1) sentence-initial glossary terms mis-tagged as verbs -- `amniote`, `capsid`, `cellulose`,
`hornwort`, `diploblast`, `budding`, `annealing`, `cnidocytes` (all nouns), and (2) reporting-verb
and misparse artifacts -- `adds` -> `boss`, `He added` -> `moment`, `cuts we have witnessed` ->
`economy`, `Millennium Falcon could make the Kessel Run` -> `spaceship`. **Genuine verb
definitions in the current foundation: ~0 / 2092.**

**This is structural, not a sampling accident.** The extractor's entire pattern inventory is
NP-headed and cannot express a verb definition:
`COPULA 648, GLOSSARY_COLON 519, APPOSITIVE 495, CALLED 422, REFERS_TO 8`. Each defines a term by
a nominal genus ("X is a Y", "X: a Y", "X, a Y", "a Y called X"). There is no construction in the
pipeline that defines a verb, so no corpus fed through it can produce verb definienda in
quantity. Per-segment VERB share is uniformly ~1-5% (bio_new 2.3%, bootstrap 1.1%, adv_new 1.9%,
int_cont 2.8%, ele_cont 5.3%) -- all artifact-dominated.

**(b) Earlier co-occurrence store** -- `data/foundation/reading_grounding_v1/store/store_facts.json`,
7966 facts (4422 KNOWN_WORD, 3544 GROUNDED_MEANING). Independently reconfirms this session's
earlier audit: 2328/3544 = **65.7% are self-referential tautologies** (`subject == obj`), leaving
1216 substantive. Of those 1216 subjects, out-of-context tagging gives NOUN 42.9%, PROPN 27.1%,
**VERB 12.3% (150)**, ADJ 11.9%. But the verb-subject groundings are the noise tail, not a
resource -- verbatim samples: `chew -> under`, `dissolve -> say`, `survive -> also`,
`settle -> austria`, plus mis-tagged nouns (`artwork`, `igneou`, `staphylococcu`). Consistent
with the standing finding that top grounded objects are function words.

**Finding, stated plainly: our corpus defines almost only nouns. Syntactic bootstrapping has
essentially nothing to bite on in the current foundation.** Wiring it would improve a verb
population that is approximately empty.

---

## 6. VERDICT

**NOT APPLICABLE TO OUR DATA AS IT STANDS -- and, separately, NEEDS REAL WORK even if the data
existed. It is not the next best step.**

Three independent reasons, in order of decisiveness:

1. **Data (decisive).** ~0 / 2092 genuine verb definienda in the current foundation, and the
   extractor's five patterns are all NP-headed so no corpus can change that without extractor
   work. The intervention targets a population we do not have.
2. **Evidence.** The proof is templated (12 held-out episodes, 4 verbs). On real text the organ
   is MIDDLE_BAND and LOSES to position-majority on both axes (0.833 vs 1.000; 0.455 vs 0.545),
   with an induced rule made of `order_pre` + `arg_animate` -- position and animacy. A second,
   independent real-data measurement (`word_acquisition_loop` increment1, HARD_FAIL, shelved)
   found the same cue family carries no signal across 249 real episodes.
3. **Interface.** The organ outputs a 2-way argument role; the `canonicalize.eligible` seam needs
   a constraint over candidate meanings. Plus a parse hop for `v_idx/subj_idx` and a
   `_eligible_mask` cache-invariant fix. Config-only reuse is not available here.

The director ranked this on literature payoff. The literature payoff is real -- Gillette/Gleitman
is a strong result and the 3.4x is worth wanting. It just does not transfer to this substrate at
this moment, because the measured precondition (verbs in the data) is absent and the organ that
would exploit it has never cleared a trivial baseline on real text.

### Can-fail test for THIS verdict

The verdict is "not applicable"; the test must be able to overturn it. Pre-registered, cheap:

**Test.** Take a deliberately verb-dense definitional source (a dictionary/glossary section with
verb entries, or a procedural corpus). Run the existing v5 definitional extractor over it
unmodified. Hand-adjudicate a random 50 of the extracted `definiendum_surface` values for whether
the definiendum is a genuine verb sense being defined.

**Thresholds (fixed in advance).**
- If **>= 15%** genuine verb definienda AND the reading path grounds those verb entries at
  above-scramble rate: **this verdict is OVERTURNED**, syntactic bootstrapping has a population
  to act on, and the frame-to-meaning-class work in section 4 becomes justified.
- If **< 5%**: verdict CONFIRMED and the blocker is located in the EXTRACTOR (NP-headed pattern
  inventory), not in the bootstrapping organ -- so no amount of work on `frame_induction` helps
  until the extractor can express a verb definition at all.
- 5-15%: inconclusive, re-run at larger N.

Current measurement on our actual corpus already sits at approximately 0%, i.e. deep in the
CONFIRMED band. The test's value is that it is the specific, bounded thing that could prove me
wrong.

### Correction to propagate

Wherever syntactic bootstrapping is recorded as "PROVED ... now islanded", both halves are wrong:
the proof is **templated-only (real text = MIDDLE_BAND, loses to position)**, and the organ is
**wired (5 hdlab + 20 exp consumers), just not reachable from the reading path**.

---

UNVERIFIED / not checked in this pass:
- Whether the 20 experiments/ consumers of `frame_induction` are live or archival cells.
- The upstream real-data mining quality of `experiments/data/experiencer_narrative_roles_v1.jsonl`
  (litbank-mined); the cell reports 3 `arg_not_located` failures but the file itself was not
  audited here.
- spaCy `en_core_web_sm` POS accuracy on sentence-initial glossary terms is visibly poor (it is
  the source of most of the 48 false VERB tags). The direction of that error INFLATES the verb
  count, so it does not threaten the conclusion, but the 2.3% figure should be read as a ceiling.
- No promotion is proposed and no code was modified.
