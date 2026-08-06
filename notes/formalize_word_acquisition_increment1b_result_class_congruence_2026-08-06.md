# FORMALIZE-drill: re-spec grounded-word-acquisition INCREMENT 1b (RESULT-CLASS, not polarity)

Date: 2026-08-06. Task: apply the project's FORMALIZE discipline to re-spec increment 1 of the
grounded-word-acquisition loop, correcting the SHAPE the increment-1 HARD_FAIL diagnosed (commit
7c314c840; drilled in `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`'s "ACQUISITION
INCREMENT 1 = HARD_FAIL" entry). This is a SPEC + pre-reg revision, not an experiment run. Companion
pre-reg: `preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`. Supersedes (does not
delete) `notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md` +
`preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md`, which stay as the source-of-truth
for increment 1's own (HARD_FAIL) numbers and honest-scope record.

**Correction made mid-drill, reported honestly:** increment 1 was not only spec'd, it was actually
BUILT and measured HARD_FAIL -- `hdlab/word_acquisition_loop.py` (372 lines), the Channel B adapter
in `hdlab/goal_typing.py` (`goal_congruence_appraisal_type`/`_cb_analyze_outcome_clause`/
`_cb_antecedent_goal_type`, L834-952), `experiments/exp_grounded_word_acquisition_increment1_v1.py`,
and `verification/verify_grounded_word_acquisition_increment1.py` all exist on disk (confirmed via
`ls`, not just the registry label) and are registered in `data/capability_registry.jsonl` as
`grounded_word_acquisition_loop_increment1` (`gate_decision: SHELVE`). Reading THAT code (not the
drill note's description of the ORIGINAL plan) surfaced a materially different, more actionable
picture than the notes-only re-spec would have produced -- Sections 2-3 below are the payoff of that
correction.

## HEADLINE

Two confirmed findings, both from reading the ACTUAL built code (not labels or docstrings):

1. **`congruence_decision` (the organ that computes production MET/UNMET) never calls into
   `context_grounded_valence` or `grounded_appraisal_sim_earned` anywhere in its call graph** --
   MET/UNMET is entirely a structural/relational judgment over `CLASS_REGISTRY` class-set membership,
   `OPPOSED_PAIRS` opposition, and discourse-entity referent-linking. This confirms the task's core
   architectural claim.
2. **"Channel B," as actually built, is ALSO already 90% structural.** `goal_congruence_appraisal_
   type` (`hdlab/goal_typing.py` L928-952) derives its RECIPROCITY/BLOCK_HIGH situation-type from pure
   clause structure (`_cb_analyze_outcome_clause`'s animacy/direct-object/passive/result-particle
   read, or an explicit antecedent-goal referent-link check via `_cb_antecedent_goal_type`) -- **the
   reward-earned theta (`channel_b_valence_table`) is consulted exactly ONCE, globally, to resolve a
   FIXED 2-value lookup (RECIPROCITY -> POS, BLOCK_HIGH -> NEG) that never varies per word or per
   sentence.** This is a real, disk-verified, previously-unstated finding: the reward-grounding step
   contributes exactly one constant bit of information (which of two structurally-already-decided
   labels maps to which polarity direction) -- a sign CONVENTION, not per-instance grounding. It could
   be replaced by a hand-stated constant (RECIPROCITY=completing=REALIZED, BLOCK_HIGH=thwarting=
   BLOCKED) with **zero loss of information**, because that is definitionally what those two label
   names already mean. This is a stronger, more precise version of the task's architectural
   clarification than "reward-grounding is a separate downstream layer" -- it turns out increment 1's
   own Channel B had ALREADY, functionally, collapsed to a structural mechanism; the reward-theta
   indirection was inert scaffolding around it.

Combined, these findings mean 1b's redesign is smaller and more surgical than "build a new Channel A
and drop Channel B": **keep the existing structural situation-typer (currently named "Channel B"),
drop the reward-theta sign-lookup indirection (proven redundant, not a capability loss), drop the
STRICT two-channel AND-gate `combine_votes` (Section 3 below shows this is net-harmful, not merely
unhelpful, when paired with a channel that carries no signal), and fix the ONE genuine, previously
undiagnosed gap that prevents this structural typer's output from ever reaching the congruence organ
at SCORING time (Section 2).**

## 1. THE CONFIRMED CONGRUENCE-ORGAN INPUT CONTRACT (disk-read, `hdlab/goal_typing.py`)

Call graph for the production entry point:

```
congruence_with_lexicon_fallback(passage_text)          [L789-799]
  -> congruence_outcome_valence(passage_text)            [L760-767]
       -> congruence_decision(goal_sentences, outcome_sentence)   [L704-757]
            -> find_desired_state(goal_sentence)          [L644-676]  -- desired = {referent, classes, verb_lemma, pattern}
                 classes = _verb_classes(embedded_lemma)   [L513-519] -- CLASS_REGISTRY (Tier-1 exact) or _verb_classes_similarity (Tier-2)
            -> find_actual_state_candidates(outcome_sentence)  [L679-693] -- SAME _verb_classes() call per candidate verb;
                 candidates whose classes come back EMPTY are SILENTLY EXCLUDED (`if classes: out.append(...)`, L690-692)
            -> _referent_links(desired_ref, actual_ref)    [L564-595]  -- literal / pronoun-coref / shared-feature-cosine
            -> same = desired["classes"] & actual["classes"]         -> MET
               opposed = _opposed_of(desired["classes"]) & actual["classes"]  -> UNMET
               neither  -> NA ("verb_class_unrelated")
               related but referent doesn't link -> UNMET ("referent_mismatch", the over-link guard)
  -> falls back to lexicon_predict(outcome_sentence) ONLY if congruence returns NA  [L795-799]
```

**Confirmed, precisely:** MET/UNMET is a **STRUCTURAL/RELATIONAL congruence judgment** -- does the
outcome clause's result-state verb belong to the SAME `CLASS_REGISTRY` class as the goal's
desired-state verb (-> MET), or a class in that class's `OPPOSED_OF` set (-> UNMET), PROVIDED the
outcome clause's affected referent resolves (literal / pronoun-coref / shared-feature-similarity) to
the goal's desired referent. **Zero reward-prediction-error term anywhere in this path** -- grep-
confirmed (`grounded_appraisal_sim`, `context_grounded_valence` do not appear in `goal_typing.py`
outside the Channel B adapter section, which this organ never calls).

`_verb_classes(lemma)`'s job is to place a verb into one of 12 **structural result-state classes**
(`REPAIR_PRESERVE`, `DAMAGE_LOSE`, `ARRIVE_SUCCEED`, `FAIL_LOSE`, `OPEN_CLASS`, `CLOSE_CLASS`,
`FILL_CLASS`, `EMPTY_CLASS`, `GATHER_CLASS`, `SCATTER_CLASS`, `HEAL_CLASS`, `HARM_CLASS`) -- a
result-state/telicity typology (Levin & Rappaport Hovav 1998's "result verbs," each lexically
entailing a scalar change along one specific dimension), not an affective-valence lexicon.

**Scoping correction to the audit (as instructed, checked against code, refined further by Section 3's
finding):** the audit's framing ("ground emotion/goal via reward-prediction-error") is right for a
SEPARATE, downstream AFFECTIVE-VALUE layer (`context_grounded_valence`'s actual consumer, the
ANIMACY/HARM-FORCE governor domain, wired 2026-08-05) but is not what MET/UNMET needs, and -- more
precisely than the task brief itself anticipated -- **increment 1's own attempt to USE reward-
grounding for this axis already reduced, in the code that was actually built, to a fixed constant**,
which is itself informative: it suggests the project's earlier intuition ("ground affect/goal via
reward-PE") was reaching for grounding in the wrong place for THIS specific axis, not merely applying
a real mechanism to the wrong consumer.

## 2. NEWLY-SURFACED RISK #1: a Tier-3-acquired word can never become a scoring-time candidate
   (confirmed by reading `find_actual_state_candidates` + `_verb_classes_similarity` together)

`find_actual_state_candidates` (L679-693) only includes a verb token as a candidate `if classes:`
(L690) -- i.e. only if `_verb_classes(lemma)` returns a NON-EMPTY set. For a Tier-3-acquired lemma,
`_verb_classes` (L513-519) tries Tier-1 (exact, fails by definition -- it's OOV) then Tier-2
(`_verb_classes_similarity`, L522-545): a **12-way argmax with a floor (0.35) and margin (0.15) gate**
over ALL of `CLASS_REGISTRY`, each class keyed by a feature vector whose dominant discriminating
component is its EVENT_DOMAIN tag (`verb_lexical_similarity.py` L96-101). Increment 1's Tier-3
write-back schema (`ACQUIRED_OUTCOME_VERB_FEATURES`, `_ACQUIRED_POS_TAGS`/`_ACQUIRED_NEG_TAGS`,
L269-283) **deliberately carries no EVENT_DOMAIN tag** (by design, to avoid an unearned domain claim
-- module comment L264-266). Worked through by hand: an acquired word's bundle vector shares its
polarity-pole tags with every SAME-POLE class's seed exemplars roughly equally (none of the 6
same-pole classes differ from each other in their polarity tags, only in domain, which the acquired
word never has) -- the 12-way argmax is expected to be **near-tied across all same-pole classes**,
very likely failing the 0.15 margin gate -> returns `set()` -> the word is **silently excluded from
`find_actual_state_candidates` entirely**, a more severe failure than "abstain": if the target verb is
the ONLY result-bearing verb in its outcome sentence (the common case for a short acquisition/eval
sentence), `find_actual_state_candidates` returns `[]` and `congruence_decision` reports NA
(`"actual_verb_class_unknown"`).

**This exact risk was never stress-tested by increment 1's own measured HARD_FAIL.** Increment 1's
self-test (`hdlab/word_acquisition_loop.py::self_test`, L339-365) verifies its acquired-word write-back
via `lexicon_predict` (the FLAT 2-way Tier-1/2/3 `_outcome_polarity_tier2` path, L207-235 of
`goal_typing.py`) -- confirmed directly in the self-test's own assertion (`lexicon_predict("The rat
stole out, and she jumped at it and caught it.") == "MET"`), NOT via `congruence_decision`/
`congruence_outcome_valence`/`find_actual_state_candidates`. The flat 2-way path is a materially
EASIER comparison (2 seed pools, not 12 classes) where the domain-less pole tags DO differentiate
somewhat (consistent with increment 1's own measured 2/7, weak-but-nonzero). **1b is the first
increment that will actually exercise the 12-way congruence path for an acquired word** -- unless
fixed, the predicted failure mode is the acquired word silently vanishing from candidacy, landing back
at NA -> the same flat fallback increment 1 already measured weak.

**Fix (small, strict-ADD, part of this spec, not deferred):** give `_verb_classes` a Tier-3 branch
that, for a lemma resolvable ONLY through `ACQUIRED_OUTCOME_VERB_FEATURES`, returns a **pole
SENTINEL** (`{"ACQUIRED_REALIZED"}` or `{"ACQUIRED_BLOCKED"}`, one-element, not a literal
`CLASS_REGISTRY` name) instead of `set()`. This makes `find_actual_state_candidates`'s existing
`if classes:` gate include it (zero change to that function). Then extend `congruence_decision`'s
`same`/`opposed` computation with ONE new branch, gated strictly on this sentinel shape: derive the
desired class's own pole via `POS_POLE_CLASSES = {c for c, _ in OPPOSED_PAIRS}` /
`NEG_POLE_CLASSES = {c for _, c in OPPOSED_PAIRS}` (both a re-derivation of the ALREADY-EXISTING
`OPPOSED_PAIRS` structure, zero new taxonomy) and compare pole-to-pole rather than requiring literal
class-name-set intersection. Tier-1/Tier-2 candidate resolution is completely untouched -- zero
regression risk, same discipline as every existing Tier extension in this module.

## 3. NEWLY-SURFACED RISK #2: the STRICT two-channel AND-gate is net-harmful when one channel is
   chance-level (confirmed by reading `combine_votes` + increment 1's own measured numbers together)

`combine_votes(a, b)` (`word_acquisition_loop.py` L255-263): production write-back requires BOTH
channels to produce the SAME non-abstain vote; either channel alone or disagreeing votes -> `None`.
Increment 1's own measured ablation (registry `provenance` field, `data/exp_grounded_word_acquisition_
increment1_v1/metrics.json`): `channel_A_only=4/7` (disk-diagnosed as a majority-class-default
artifact of an AT-CHANCE channel -- "every construction-cue signature is ~50/50 POS/NEG across 249
seed-corpus episodes, 129 POS/120 NEG"), `channel_B_only=2/7`, `combined=2/7`. **Because `combine_
votes` is a strict AND-gate, `combined` can never exceed `min` of what each channel alone would
correctly confirm at the SAME occurrences -- pairing an informative channel with a chance-level one
under strict AND can only preserve or REDUCE the informative channel's effective recall, never add
real confirmatory value** (a chance-level channel's agreement with a good channel on any given item is
itself chance, so requiring it adds variance, not evidence). In this specific run `combined ==
channel_B_only` (no net loss this time), but that is a property of this one 7-word sample, not a
property of the gate -- at larger N the AND-gate would be expected to net-erode Channel B's own
(already weak) signal by roughly Channel A's disagreement rate. **This is a genuine design flaw in
increment 1's anti-drift architecture, distinct from either channel's own individual weakness, worth
reporting even though 1b's revised design (Section 4) removes the two-channel structure that exposed
it.**

## 4. THE REVISED (SINGLE-CHANNEL) ARCHITECTURE

Given Sections 1-3, 1b's design is a targeted repair, not a rebuild:

1. **Keep the existing structural situation-typer, reframed as the sole channel.** Reuse
   `_cb_analyze_outcome_clause` (clause-local animacy/direct-object/passive/result-particle read,
   already built, verb-lemma-blind) + `_cb_antecedent_goal_type` (explicit antecedent-goal referent-
   link check, already built, reuses `find_desired_state`/`find_actual_state_candidates`/
   `_referent_links` verbatim) + `goal_congruence_appraisal_type`'s combination logic (L928-952) AS
   THE PROPOSAL MECHANISM, but **drop the `channel_b_valence_table`/reward-theta indirection** (Section
   1's finding: it is a fixed 2-value constant, replaceable with a direct label map with zero
   information loss) -- map RECIPROCITY -> `AGONIST_REALIZED` (write "POS"/REALIZED), BLOCK_HIGH ->
   `AGONIST_BLOCKED` (write "NEG"/BLOCKED) directly. This removes a real-but-inert dependency
   (`experiments.exp_bridge1_governor_grounding_v1`, `hdlab.context_grounded_valence`) from the
   acquisition loop's hot path -- a simplification, not a capability loss (proven by Section 1's
   constant-mapping argument, not merely asserted).
2. **Drop the STRICT two-channel AND-gate** (`combine_votes`, Section 3) -- there is only one channel
   now, so this is moot for votes, but the DESIGN LESSON (don't AND-gate an informative signal against
   a chance-level one, expecting free anti-drift) is recorded so it isn't repeated if a genuine second
   channel is added in a future increment.
3. **NEW, optional enrichment atoms (secondary, separately-ablated, not required for the core fix):**
   extend `_cb_analyze_outcome_clause`'s clause read with (a) a TELICITY gate (Vendler 1957; Beavers
   2008/2011: is the direct object a definite/quantized NP, or is a bounded directional PP present --
   sharpens the existing bare `has_direct_object` signal) and (b) a discourse-connective POLE cue
   (Kehler 2002 *Coherence, Reference, and the Theory of Grammar*, CSLI; Hobbs 1979 *Cognitive
   Science* 3(1): a CONTRAST connective -- `but`/`however`/`yet` -- immediately preceding the outcome
   clause votes REVERSAL-relative-to-trajectory; a RESULT/continuation connective -- `and`/`so`/`then`
   -- votes continuation). These are proposed as an ABLATED addition (Section 5's ablation prediction
   below) precisely because Section 1's finding shows the EXISTING implicit force-dynamics read
   (`agonist_realized`/`agonist_blocked`, L943-951) already recovers SOME real signal (the registry's
   own provenance note: "recovers transitive-achievement POS verbs (earn, gain)") -- the honest
   question for 1b is whether these 2 new atoms add real marginal signal or are redundant with what
   `_cb_analyze_outcome_clause` already captures, not whether a signal exists at all (it partially
   does, per increment 1's own measurement).
4. **Fix Risk #1 (Section 2), REQUIRED, not optional** -- without it, an acquired word can never
   reach the congruence organ's scoring-time candidate list at all, and 1b would silently degrade to
   re-testing increment 1's already-measured-weak flat 2-way fallback.
5. **Propose/gate/consolidate skeleton: REUSED VERBATIM, unchanged** -- `predictive_coding.
   threshold_gate` (`word_is_novel`, L65-75) as the propose trigger; `MIN_CONFIRM=2` +
   `decide_keep_or_revert` abstain-band (`consolidate`, L266-289) as the single remaining anti-drift
   gate (now carrying the FULL anti-drift weight, since the two-channel AND-gate is gone -- this is
   the correct, brain-consistent locus for anti-drift per Trueswell 2013 / Alishahi-Fazly-Stevenson
   2008's propose-but-verify account: repeated CONFIRMATION across independent occurrences, not
   redundant simultaneous channels).
6. **Write-back: REUSED VERBATIM, unchanged schema** -- `register_acquired_outcome(word, polarity)`
   into `ACQUIRED_OUTCOME_VERB_FEATURES`. Only the label's SOURCE changes (direct structural mapping,
   not a reward-theta lookup); the consumer-facing representation and every downstream Tier-3
   integration point are byte-identical to increment 1's.

## 5. AN ABLATION 1b OWES INCREMENT 1's OWN FINDING (informational, pre-registered)

Increment 1's registry provenance states Channel A (separate MDL-induced construction classifier, atop
`CHANNEL_A_ATOMS = [has_direct_object, patient_np_present, result_particle_present,
subject_is_animate_agent]`) measured at-chance (4/7, "majority-class-default artifact... every
construction-cue signature ~50/50 POS/NEG"). Section 4's redesign **drops this separate MDL-induced
classifier entirely**, reusing only the DETERMINISTIC rule-based read inside `_cb_analyze_outcome_
clause`/`goal_congruence_appraisal_type` (`agonist_realized`/`agonist_blocked`, a hand-specified
boolean combination, not learned) -- because the LEARNED version of essentially the same atom set
already measured no signal, redoing MDL-induction over the same base atoms would be expected to
reproduce the same chance-level result (no reason to expect a different MDL fit on the same features
to discover signal the features don't carry). **1b's design choice to keep the hand-specified boolean
combination rather than re-inducing it is therefore itself a falsifiable, pre-registered bet**: if the
hand-specified rule ALSO turns out to carry no real signal once tested via the FIXED congruence organ
(Risk #1's fix) instead of the flat fallback, that is a genuine, informative finding about whether
`_cb_analyze_outcome_clause`'s atoms (animacy, direct-object, passive, result-particle) predict
telicity/force-dynamics AT ALL for OOV result verbs -- not merely an artifact of MDL-induction's
sample size on 249 episodes.

## 6. HONEST SCOPE -- what 1b does NOT solve

Same items increment 1 already carried forward (negation-scope, PP-only reward-allocation
constructions, third-party-unnamed-helper outcomes, taxonomic-generality; see `notes/drill_online_
grounded_word_acquisition_loop_2026-08-06.md`'s own "Honest scope," not repeated). ADDED for 1b:

- **Coverage ceiling from `find_desired_state`'s narrow goal-construction gate.** `find_desired_state`
  (L644-676, ALSO the function `_cb_antecedent_goal_type` calls at acquisition time) only recognizes a
  goal clause governed by a literal `DESIDERATIVE_PASS` verb (`{hope, want, wish, mean, plan, intend,
  aim, long, yearn, desire}`). Cross-checking `goal_verb_lemma` against this set for all 44 items of
  `experiments/data/goal_bearing_modern_eval_v1.jsonl` (counted directly off the file, this session):
  **22/44 items use a recognized goal verb; 22/44 do not** (`try`/`decide`/`determine`/`resolve`/
  `make`/`persuade`/`avoid`/`like`/`love`/`get`/`beg`/`forgive` -- several deliberately excluded
  elsewhere in this module, e.g. `try`/`decide` are in `ASPECTUAL_STOP`/`OTHER_STOP_UNCHANGED`, a
  conservative pre-existing choice, not a new bug). Restricted to the 36 OOV-outcome items 1b's primary
  metric scores: **18/36 (50%) have a `find_desired_state`-parseable goal clause; the other 18/36 will
  return NA from `congruence_outcome_valence` regardless of 1b's mechanism quality**, falling to the
  flat 2-way `lexicon_predict` path. This is a real, pre-registered coverage ceiling, reported not
  swept -- a goal-construction-diversity gap, a separate competency from outcome-verb acquisition, not
  attempted here. Flagged as the highest-leverage next increment after 1b (broadening
  `find_desired_state` to match `action_frame_feats`'s already-broader purpose-infinitival net).
- **Does not attempt to recover an acquired word's DOMAIN** (which of the 12 `CLASS_REGISTRY` classes,
  in the abstract) -- only its POLE relative to whatever domain the current passage's goal already
  established (Section 2's sentinel fix). A narrower, more defensible claim than "this word IS an
  ARRIVE_SUCCEED verb" in general.
- **Does not persist across process restarts** (same as increment 1, in-memory-only).
- **Does not claim the 2 new enrichment atoms (Section 4.3) are load-bearing** -- pre-registered as an
  ablated addition specifically so a null result there is informative, not swept.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

P(1b clears its pre-registered HARD-PASS band) is capped at 0.50 and further deflated to **~0.30-0.35**
(similar range to, not lower than, my first-pass estimate before this correction, for a different
reason than originally stated): Section 1-2's findings are net-POSITIVE for 1b's odds (the SHAPE fix
is real, Risk #1 is a genuinely fixable wiring gap, not a fundamental one, and the existing implicit
force-dynamics read already shows SOME real signal per increment 1's own provenance note, unlike a
from-scratch channel) -- but Section 6's coverage ceiling (only 18/36 items reach the fully-fixed
path) and Section 5's honest bet (the hand-specified atoms may simply not carry enough signal once
tested where it counts) keep this from clearing higher. A clean HARD-FAIL here -- the 18-item
`find_desired_state`-reachable subset does NOT outperform the 18-item flat-fallback subset -- would be
a genuinely informative falsification of this respec's central claim, not an implementation miss.

## Citations

Carried forward unchanged from increment 1 (mechanisms 1/3/4/6, fast-mapping/cross-situational-
learning list): see `notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md`. New for 1b's
enrichment atoms (Section 4.3): Vendler 1957 *Philosophical Review* 66(2); Beavers 2008 PhD diss UT
Austin; Beavers 2011 *Natural Language & Linguistic Theory* 29(2); Kehler 2002 *Coherence, Reference,
and the Theory of Grammar*, CSLI; Hobbs 1979 *Cognitive Science* 3(1). Structural verb typology
(unchanged, carried from increment 1's own drill): Jackendoff 1990; Talmy 1988; Rappaport Hovav &
Levin 1998/2010.

Cross-thread synthesis: extends `notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md` +
`preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md` (increment 1's own spec + measured
HARD_FAIL, `data/exp_grounded_word_acquisition_increment1_v1/metrics.json`); diagnosis sourced from
`notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`'s "ACQUISITION INCREMENT 1 = HARD_FAIL" +
"FAIR MODERN GOAL-BEARING EVAL" entries; test bed = `experiments/data/goal_bearing_modern_eval_v1.
jsonl` + `notes/research_goal_bearing_modern_eval_2026-08-06.md`; direct prior-art row =
`data/capability_registry.jsonl`'s `grounded_word_acquisition_loop_increment1` (gate: SHELVE, revival
criteria explicitly names "the telicity/result-state discriminator... test on goal+outcome PASSAGE
structure" -- exactly what this re-spec delivers, confirmed word-for-word against the registry, not
paraphrased from memory).

## Substrate-product implications

Unchanged in kind from increment 1's own framing: if 1b clears its bands, outcome-typing coverage on
real narrative prose stops depending on hand-curated lexicon entries, with the SAME inspectable
provenance trail. This drill sharpens the PRODUCT claim's honesty in two ways: (1) Section 6's coverage
ceiling means a HARD-PASS licenses "generalizes for goal-bearing passages with an explicit desiderative
construction" specifically, not narrative prose broadly; (2) Section 3's AND-gate finding is a reusable
design lesson for any future multi-channel acquisition increment in this codebase -- don't require
simultaneous cross-channel agreement as an anti-drift substitute for genuine repeated-confirmation,
when one channel's signal quality is unverified going in.
