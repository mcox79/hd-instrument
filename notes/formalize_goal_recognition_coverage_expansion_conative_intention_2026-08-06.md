# FORMALIZE: goal-recognition coverage expansion (conative ATTEMPT + intention DECISION + bouletic extension)

Date: 2026-08-06. Status: **SPEC + PRE-REG ONLY, NOT BUILT/RUN.** Companion: `preregs/2026-08-06_goal_recognition_coverage_expansion_v1.md`
(can-fail bands + precision-guard controls). This note is the owned-coverage map + brain-mechanism map +
fix design a cell-author (exp_dev) implements from directly; no further research pass should be required
to start the build.

Trigger: increment-1b's own HARD_FAIL-adjacent finding that `find_desired_state` only reaches "18/36"
of the eval's OOV goal items (`notes/formalize_word_acquisition_increment1b_result_class_congruence_
2026-08-06.md`), and the Director's follow-up measurement that the `goal_verb_lemma` distribution in
`experiments/data/goal_bearing_modern_eval_v1.jsonl` shows roughly half the eval's goal-bearing sentences
use a governing verb (`try`, `decide`, `determine`, ...) the `DESIDERATIVE_PASS` gate does not recognize
at all. This drill verifies that measurement against the actual code and actual text, on disk, and finds
it is **directionally right but numerically off** -- see "Corrected baseline" below.

## HEADLINE

`find_desired_state`'s literal `DESIDERATIVE_PASS` membership gate (`hdlab/goal_typing.py` L295-300) is
the single choke point for goal-content extraction; it recognizes only bouletic-DESIRE verbs
(want/wish/hope/mean/plan/intend/aim/long/yearn/desire) and misses two entire classes of intentional-state
construction that are lexically and syntactically just as regular: CONATIVE/ATTEMPT (`try`) and
INTENTION/DECISION (`decide`, `determine`). Both classes take the identical "SUBJECT V (NP) to VP"
infinitival-CONTROL/ECM shape the gate already parses for `want`/`hope` -- they were misfiled into
`ASPECTUAL_STOP` (a genuinely-different class: aspect verbs like `began`/`managed` that do NOT introduce a
goal) rather than given their own pass-class. A disk-verified simulation (production `find_desired_state`,
only the governing-verb set patched, nothing else touched) shows this reclassification alone recovers
**13 genuinely-new fires**, moving true coverage from **19/44 (0.432) to 32/44 (0.727)**, with **zero**
false-fires introduced on an 11-item bare-transitive/aspectual control set. A cheap, separately-bundled
gerund-form fix (`yearning`, `wanting`, etc. -- currently absent from every desiderative verb's inflection
set) adds one more measured item, for a combined ceiling of **33/44 (0.750)**.

## Corrected baseline (read the code, don't trust the label -- per Director's own caution, confirmed again)

The Director's tally (`want=10, wish=4, hope=4, mean=3, yearn=1` -> "~22/44 recognized") is a **proxy**
built from the `goal_verb_lemma` column, which assumes 1:1 correspondence between "the label says this
lemma" and "the mechanism actually fires on this text." Running the real `find_desired_state` against
all 44 `goal_text` fields (unmodified `DESIDERATIVE_PASS`) shows this correspondence **breaks in both
directions**:

- **True baseline = 19/44 (0.432), not 22/44.** Five of the nominally-recognized 22 do NOT actually fire:
  - `lw_beth_piano_invite` (yearn): the sentence uses the GERUND `"yearning"`, which is absent from
    `DESIDERATIVE_PASS` (only `yearn/yearns/yearned` are listed -- **none of the 10 desiderative verbs
    has a gerund form in the set**, a systematic, cheap-to-fix enumeration gap, not specific to `yearn`).
  - `lw_jo_story_prize`, `agg_anne_avery_scholarship_gilbert_medal_ch36` (both `hope`): `hope` appears as
    a bare NOUN governing a PP (`"all hope of ever seeing..."`, `"I have not hope of the Avery"`), not a
    verb governing a `to VP` infinitival. No `to` token follows `hope` in either sentence at all --
    `find_desired_state`'s forward scan correctly finds nothing (this is a different complement type,
    noun+PP, not a coverage gap in the sense this drill addresses).
  - `ts_tom_wish_free_potter` (`wish`): `"I wish we could get him out of there"` -- `wish` governs a
    FINITE, modal-marked clause (`wish [that] we COULD VP`), not an infinitival. This is the SAME
    finite-complement gap that blocks several of the "missed" items below (see "Genuinely out of scope"
    section) -- and it shows the gap is not specific to the new verb classes; it already limits the
    EXISTING recognized set.
  - `agg_anne_hair_dye_green_ch27` (`mean`): no literal `mean` token anywhere in the quoted `goal_text` --
    a label/paraphrase mismatch (see below), not a construction-coverage issue.
- **Two extra, unlabeled fires** happen already, incidentally, via the pre-existing `mean` verb (present
  literally in their text even though their `goal_verb_lemma` label is something else):
  - `lw_aunt_march_opposition` (labeled `persuade`): fires on `"do you mean to marry"` -- but this is
    grammatically Meg's own `mean`-clause, not a lexicalization of Aunt March's implicit
    persuasion/prevention goal at all (the eval's own `notes` field flags this item as a goal-relative,
    multi-owner-valence case). The mechanism fires, but on the wrong content for what the label implies.
  - `agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17` (labeled `forgive`): fires on `"I did not mean
    to--to--intoxicate Diana"` -- this is a **genuine false-positive class**: the sentence NEGATES the
    desiderative (`did NOT mean to`), and `find_desired_state` has no negation check at all, so it reads
    a disclaimed intention as an affirmed goal. Confirmed reproducible (see Precision section below) and
    **pre-existing** (affects `mean` today, independent of anything this drill proposes to change).

Net: `19 = 22 (nominal) - 5 (non-firers) + 2 (incidental/mislabeled firers)`. **The pre-reg below gates
on the verified 19/44, not the Director's 22/44 estimate.**

## Owned-detector coverage map (from code, `hdlab/goal_typing.py`)

Two SEPARATE mechanisms both key off governing-verb-set membership, and they diverge in what they check:

1. **`find_desired_state(sentence)`** (L711-743) -- goal-CONTENT extraction (referent + verb-class of the
   desired end-state), consumed by `congruence_decision`/outcome-valence. Gate: `dv_idx = next(i for i, t
   in enumerate(toks) if t in DESIDERATIVE_PASS)` (L718) -- **literal, case-folded, un-lemmatized token
   membership** in `DESIDERATIVE_PASS` only. If found, scans FORWARD from `dv_idx+1` to the end of the
   sentence for the first `to X` where `X not in DET_STOP` (L721-722) -- this scan is GREEDY and
   POSITION-INSENSITIVE past the governing verb (it will cross intervening clause material, which is why
   `race_tim_rescue`'s `"decided it would be safer... for him to pull..."` is reachable once `decide` is
   added, via the embedded for-to infinitival -- verified below, not assumed).
2. **`action_frame_feats(sentence)`** (L347-367) via `_control_verb_is_aspectual_like` (L328-344) -- goal-
   OWNER-ELIGIBILITY typing (feeds `has_goal`/owner-selection through the MDL-induced classifier). Gate:
   the SINGLE token immediately preceding `to` (`preceding = toks[i-1]`). Tier-1: literal
   `PARTITIONED_STOP` (=`ASPECTUAL_STOP | OTHER_STOP_UNCHANGED`, L316) membership suppresses (returns
   `True` = aspectual-like); literal `DESIDERATIVE_PASS` membership passes (`False`); OOV of both falls to
   a Tier-2 open-vocab classifier (`_verblex.classify_2way(lemma, _GOAL_ASPECT_SEED_LEMMAS,
   _GOAL_DESID_SEED_LEMMAS, "goal", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)`, L342-343).

**Why `try`/`decide`/`determine` fall through today, precisely:** they are literal members of
`ASPECTUAL_STOP` (`try/tries/tried`) or `OTHER_STOP_UNCHANGED` (`decide/decides/decided`) (L303-315).
`determine`/`determines`/`determined` is in **neither** set -- not `DESIDERATIVE_PASS`, not
`ASPECTUAL_STOP`, not `OTHER_STOP_UNCHANGED` -- a genuine unclassified gap, currently falling to the
Tier-2 similarity classifier in `action_frame_feats` (untested, unverified outcome) and to a flat `None`
in `find_desired_state` (which has no Tier-2 fallback at all -- it is Tier-1-literal-only). This is a
**category-conflation bug**, not a threshold-tuning gap: `ASPECTUAL_STOP`'s own module comment (L301-302)
says its members are excluded because "X began/tried/failed to VP is not a goal ownership signal" --
correct for `began`/`failed`/`managed`/`happened`/`ceased`/`stopped`/`continued` (pure aspect: they mark
the START/END/SUCCESS of an already-established action, contributing no new goal), but **wrong for
`try`**: an attempt is not aspectual marking of a prior action, it is itself the ATTEMPT toward the goal
(Talmy 1988 force-dynamics AGONIST-exertion, already this module's own cited framework for
`goal_congruence_appraisal_type`, L881-883). `decide`/`determine` were separately parked in
`OTHER_STOP_UNCHANGED`, whose own comment (L310-311) states plainly they are "Unclassified by the source
cell's task brief -- conservatively LEFT in the stop set" -- i.e. an acknowledged placeholder, not a
considered exclusion.

## Brain mechanism map

Three intentional-state classes, cited, mapped to owned detectors:

- **Bouletic DESIRE** (want/wish/hope/mean/plan/intend/aim/long/yearn/desire; extend with `like`/`love`,
  see below) -- a "world-to-mind" propositional attitude (Searle 1983, *Intentionality*; Farkas 1992 on
  desiderative mood selection). Neurally, desire/wanting implicates mesolimbic dopaminergic
  incentive-salience signaling (VTA -> nucleus accumbens), separable from hedonic "liking"
  (opioid/endocannabinoid hotspots, NAcc shell/ventral pallidum) per Berridge & Robinson's
  incentive-sensitization account (Berridge 2007; Berridge & Kringelbach 2015). Caveat, not overclaimed:
  this wanting/liking neural dissociation does not mean the English words "want" and "like" cleanly track
  incentive-salience vs. hedonic-impact in every use -- it is cited as evidence that DESIRE is a real,
  independently-motivated psychological natural class, which is the claim actually needed here.
  Already-owned detector: `DESIDERATIVE_PASS` -> `find_desired_state`.
- **Conative ATTEMPT** (`try`, and its OOV siblings `attempt`/`endeavor`/`strive`) -- Talmy's (1988) force
  dynamics: an AGONIST exerts force toward a goal-state; `try` lexicalizes the EFFORT component
  independent of whether an ANTAGONIST force blocks it -- which is exactly why the goal must be recognized
  **even when the attempt fails** (`ts_tom_sugar_theft`: "He tried to steal sugar... " -- unmet; the goal
  is still "steal sugar"). Neurally: SMA/pre-SMA and anterior cingulate cortex support effort-based action
  initiation and monitoring (Shenhav, Botvinick & Cohen 2013, "The expected value of control"). No owned
  detector currently; this drill adds one (`CONATIVE_PASS`).
- **INTENTION/COMMITMENT** (`decide`, `determine`, and the OOV sibling `resolve`) -- Bratman's (1987)
  distinction between INTENTION (a conduct-controlling, commitment-bearing pro-attitude) and mere DESIRE:
  deciding is the act of FORMING an intention, and the decided-upon action becomes the goal regardless of
  whether the decision is later acted out. Neurally, intention-formation/volitional decision implicates
  dorsolateral prefrontal cortex and pre-SMA (Haggard 2008, "Human volition: towards a neuroscience of
  will," *Nat Rev Neurosci*). No owned detector currently; this drill adds one (`INTENTION_PASS`).
- **DIRECTIVE REQUEST** (`persuade`/`beg`/`ask`) -- Speech Act Theory illocutionary force (Austin 1962;
  Searle 1969, 1976 taxonomy): a directive is the speaker's attempt to get the ADDRESSEE to bring about P;
  the goal is doubly indexed (speaker's desire that addressee do P), structurally an Equi/ECM control
  configuration (Rosenbaum 1967; Postal 1970) the code's existing ECM branch (`between`-span referent
  extraction, `pattern="ECM"`, L727-729) already handles WHEN a literal infinitival complement is present.
  **Explicitly deferred this increment** -- see "Genuinely out of scope" below: zero eval items currently
  supply the exploitable form (`persuade`/`ask` SOMEONE `to VP`).

## Fix design (strict-ADD to the class taxonomy; NOT strict-ADD to observed behavior on this eval -- see honest framing below)

1. **New set `CONATIVE_PASS = {"try","tries","tried","trying"}`.**
2. **New set `INTENTION_PASS = {"decide","decides","decided","deciding","determine","determines",
   "determined","determining"}`.**
3. **Extend `DESIDERATIVE_PASS` itself** with the bouletic-preference verbs `like`/`love` (same semantic
   class as want/wish/hope, not a new category) plus the GERUND form for every existing member (none of
   the 10 current bases has an `-ing` form today): `liking, loving, wanting, wishing, hoping, meaning,
   planning, intending, aiming, longing, yearning, desiring`, plus `like, likes, liked, love, loves,
   loved`.
4. **Remove `try/tries/tried/trying` from `ASPECTUAL_STOP`; remove `decide/decides/decided` from
   `OTHER_STOP_UNCHANGED`** (the mis-partition fix -- `determine*` was never in either set, no removal
   needed there). **Load-bearing implementation detail:** the module's own `assert
   DESIDERATIVE_PASS.isdisjoint(PARTITIONED_STOP)` (L317) will hard-crash at import if this removal is
   skipped while the additions land -- the removal and the addition are one atomic edit, not two.
5. **Both consumers must reference the UNION.** Define `GOAL_GOVERNING_PASS = DESIDERATIVE_PASS |
   CONATIVE_PASS | INTENTION_PASS` at module scope; `find_desired_state`'s `dv_idx` check (L718) and
   `_control_verb_is_aspectual_like`'s Tier-1 checks (L337-340) both switch from testing
   `DESIDERATIVE_PASS` alone to testing `GOAL_GOVERNING_PASS` (or equivalent -- implementer's call on
   exact refactor shape, but the union must cover all three sets at both call sites, not just one).
6. **Tier-2 seed-pool consistency (recommended, not eval-scored this increment):** `_GOAL_ASPECT_SEED_
   LEMMAS` (L322-323) currently includes `"try"` as an aspectual exemplar -- leaving it there after `try`
   moves to `CONATIVE_PASS` would bias OOV siblings (`attempt`, `endeavor`, `strive`) toward the WRONG
   pool via similarity. Remove `"try"` from `_GOAL_ASPECT_SEED_LEMMAS`; optionally add `decide`/`try`-
   family exemplars to `_GOAL_DESID_SEED_LEMMAS` (or rename it to reflect "PASS pool" rather than
   "desiderative pool," since it is really a suppress-vs-pass distinction, not strictly
   desiderative-vs-aspectual) so future OOV conative/intention verbs fall the right way. This does not
   move any of this eval's 44 items (none of them hit the Tier-2 path for a `CONATIVE_PASS`/
   `INTENTION_PASS` member) and is not gated in the pre-reg; flagged as a correctness improvement to land
   in the same edit for coherence, at the implementer's discretion.

**Honest framing of "strict-ADD":** items 1-3 above (new verbs previously OOV of every set) are strict-ADD
in the conventional sense -- they can only take a caller from `None`/abstain to a value, never change an
existing non-None result. Item 4 (removing `try`/`decide` from `ASPECTUAL_STOP`/`OTHER_STOP_UNCHANGED`) is
**not** strict-ADD in that sense: it changes `action_frame_feats`' output for any sentence containing
`try`/`decide` + infinitival, from suppressed to firing. This is the intended, correct fix (those verbs
were miscategorized), but report it as a **behavior change to a previously-deterministic, tested code
path**, not as a zero-regression addition. No existing `self_test` assertion (L1069-1192) references
`try`/`decide`/`determine` specifically, so no CURRENT cert assertion conflicts -- confirmed by reading
`self_test`, not assumed.

## Genuinely out of scope this increment (named so exp_dev doesn't have to re-derive)

Each maps to one or more of the missed-22 items, confirmed by reading the actual `text`/`goal_text`
fields, not the `goal_verb_lemma` label alone (multiple labels turned out to be paraphrase glosses of an
implicit goal with no literal governing-verb token in the passage at all -- the same failure mode the
Director's brief warned about, ""9+ mislabels caught this session""):

- **Finite that-clause / modal complementation** (`decide THAT S`, `beg THAT S`, `wish [that] S COULD VP`):
  `agg_matthew_puffed_sleeves_dress_ch25` ("Matthew decided that he would give her one"),
  `woz_lion_courage_denied` ("I came to you to beg THAT you give me courage"), and even the ALREADY-
  recognized `ts_tom_wish_free_potter` ("I wish we could get him out"). `find_desired_state`'s scan is
  infinitival-only (`toks[i] != "to"`); no verb-set change reaches these. Needs a separate finite-clause
  complement detector -- cross-cutting, affects existing verbs too, likely the single highest-value NEXT
  increment after this one given it already limits the recognized-19 baseline.
- **Bare-infinitive causatives** (`make NP VP`, no "to"): `lw_laurie_flower_table_amy` ("make them buy
  every flower"). Structurally incompatible with the `to`-token-anchored scanner regardless of verb-set
  membership -- needs a distinct no-"to" complement pattern.
- **Modal/future-intention constructions** (`be going to VP`, deontic `must VP`):
  `lw_beth_slippers_piano_gift` ("I'm going to work... I must thank him") -- no governing lexical verb in
  either of these frames at all; a different construction class entirely.
- **Predicate-nominal goal announcement** (`X be [next thing] to VP`): `alice_beautiful_garden` ("the next
  thing is, to get into that beautiful garden") -- no governing control verb before `to get`; the
  preceding token is the copula `is`. A promising, likely-high-yield, narrow future pattern (do not add
  `is` itself to any pass set -- would massively over-fire on ordinary copular sentences).
- **Implicit/pragmatic goal inference (no literal governing verb in the text at all):**
  `lw_aunt_march_opposition` (persuade), `ts_becky_anatomy_book_confession` (avoid),
  `agg_gilbert_pond_rescue_friendship_plea_ch28` (try -- the quoted `goal_text` is pure dialogue, "Can't we
  be good friends?", no "try" token anywhere), `lw_beth_slippers_piano_gift` and
  `agg_anne_hair_dye_green_ch27` (both labels don't correspond to any literal token in the quoted text).
  These need bridging inference / implicit-goal attribution (the mechanism class already named in this
  session's other research deliveries, `notes/audit_brain_composition_situationmodel_2026-08-06.md`), not
  construction typing.
- **Directive-request** (`persuade`/`beg`/`ask` SOMEONE to VP): mapped in the brain-mechanism section
  above, but zero eval items supply the exploitable ECM-infinitival form today (`persuade` here is a
  paraphrase with no literal token; `beg` governs a finite that-clause) -- adding a `DIRECTIVE_PASS` set
  now would move **zero** items on this eval, failing the cheap-decisive-test bar. Worth a 1-line mention
  for a future eval expansion that includes real "asked/urged/ordered SOMEONE to VP" sentences.
- **Negation-scope** (pre-existing, NOT introduced by this drill, but INHERITED and WIDENED by it since
  more verbs now sit behind the same unguarded gate): `find_desired_state` has no negation check.
  `"did not mean to intoxicate Diana"` already false-fires today; empirically confirmed this also false-
  fires for `try`/`decide`/`like` once added (see pre-reg precision section). This is the Director's own
  already-named next roadmap item ("negation-scope") -- tracked, measured, reported, **not** fixed here.

## Cheap decisive test (already run this cycle, disk-verified, reproducible)

The "cheap decisive test" for this drill IS the simulation below -- production `find_desired_state`,
imported unmodified, with only the module-level `DESIDERATIVE_PASS` name monkeypatched (no file edits) --
run against all 44 eval `goal_text` fields plus an 11-item control set. This becomes exp_dev's smoke gate
before landing the real edit (same numbers should reproduce byte-for-byte once the sets are actually
edited on disk, since the simulation calls the real function, not a re-implementation):

| Configuration | Coverage | Delta |
|---|---|---|
| TRUE baseline (unmodified) | 19/44 = 0.432 | -- |
| + gerund forms only (bonus, cheap) | 20/44 = 0.455 | +1 |
| + `CONATIVE_PASS` + `INTENTION_PASS` + like/love (no gerunds) | 32/44 = 0.727 | +13 |
| + combined (gerunds + new classes) | **33/44 = 0.750** | **+14** |
| Control false-fires (6 bare-transitive + 3 aspectual + 2 gerund-noun-phrase) | 0/11 | -- |

## Falsifiable predictions (summary -- full bands + controls in the companion pre-reg)

**HARD-PASS:** `find_desired_state` coverage on the 44-item eval `>= 30/44` (0.682, a +0.25 absolute lift
over the verified 19/44 baseline) AND zero false-fires on the bare-transitive/aspectual precision-guard
control set (measured ceiling this cycle: 33/44 coverage, 0/11 false-fires -- HARD-PASS band is set with
slack below the measured ceiling, not pinned to it).

**HARD-FAIL:** coverage `<= 22/44` (0.5, i.e. does not clear the Director's own original, since-corrected
estimate) OR any bare-transitive/aspectual control produces a false GOAL fire OR the `DESIDERATIVE_PASS.
isdisjoint(PARTITIONED_STOP)` assertion breaks (import-time crash) OR `python verification/run_
certification.py` regresses below 220 passed / 3 skipped.

Full bands, MIDDLE-BAND definition, and the exact 11-item control-sentence list are in the companion
pre-reg.

## Substrate-product implications

This closes the single largest measured share (13-14 of ~22-25 missed items, roughly 60%) of the
upstream goal-recognition ceiling that caps EVERY downstream comprehension organ gated on `has_goal`/
`find_desired_state` -- outcome-valence congruence, goal-owner selection, the word-acquisition Channel-B
adapter's antecedent-goal linking. It does so with a taxonomically well-motivated (not ad-hoc) three-way
split of intentional-state verbs (desire/attempt/intention) that mirrors an established philosophy-of-
action distinction (Bratman 1987), reusing 100% of the existing infinitival-scan machinery -- no new
parser, no new binding operation, consistent with the standing no-bolt-on-reader discipline. The honest
remainder (finite-clause complementation, bare-infinitive causatives, modal/future-intention frames,
predicate-nominal announcements, implicit/pragmatic goals) is now a named, prioritized backlog rather than
an undifferentiated "half the eval is missed" number -- the single highest-value next item is finite-
clause complementation (`decide/wish/beg THAT S`), since it already limits the CURRENTLY-recognized
desiderative baseline, not just the new classes this increment adds.

## Citations (verified count: 7)

1. Bratman, M. (1987). *Intention, Plans, and Practical Reason.* Harvard University Press. --
   desire-vs-intention distinction (INTENTION_PASS mapping).
2. Talmy, L. (1988). "Force Dynamics in Language and Cognition." *Cognitive Science* 12(1). --
   AGONIST/ANTAGONIST force-dynamics (CONATIVE_PASS mapping; already cited elsewhere in this module).
3. Haggard, P. (2008). "Human volition: towards a neuroscience of will." *Nature Reviews Neuroscience*
   9(12). -- dlPFC/pre-SMA decision/intention-formation.
4. Shenhav, A., Botvinick, M. M., & Cohen, J. D. (2013). "The expected value of control: an integrative
   theory of anterior cingulate cortex function." *Neuron* 79(2). -- ACC effort/attempt monitoring.
5. Berridge, K. C., & Robinson, T. E. / Berridge, K. C., & Kringelbach, M. L. (2015). "Pleasure systems in
   the brain." *Neuron* 86(3). -- wanting/liking dissociation (bouletic DESIRE class support, calibrated
   caveat given).
6. Searle, J. R. (1969, 1976). *Speech Acts*; "A classification of illocutionary acts." *Language in
   Society* 5(1). -- directive speech acts (deferred DIRECTIVE_PASS mapping).
7. Rosenbaum, P. S. (1967). *The Grammar of English Predicate Complement Constructions.* MIT Press. --
   Equi/ECM control syntax (already partially implemented via the code's own ECM referent-extraction
   branch).

Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: this is primarily a
**code-verification + construction-typology** drill, not a novel-synthesis claim, so P-deflation is
modest -- P_deflated=0.72 reflects high confidence in the disk-verified numbers (simulation ran against
the real production function) and moderate-only confidence in the brain-mechanism citations' precise
applicability (calibrated, not novel-synthesis-capped at 0.50, since the citations support an
independently-motivated linguistic/psychological taxonomy rather than a claim about the substrate's own
novel physics).
