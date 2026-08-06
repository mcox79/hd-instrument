# research: DID-IT-HAPPEN occurrence-gate — spec for wiring into goal-congruence (FORMALIZE-drill, no build/run)

**Type:** FORMALIZE spec + pre-reg only. Nothing built, nothing run against the detector design itself
(the empirical numbers below are all **existing production code run read-only** to ground the design,
not a new build).
**Consumer organ:** `hdlab/goal_typing.py::congruence_decision` (+ `find_actual_state_candidates`,
`find_desired_state`, `congruence_outcome_valence`, `congruence_with_lexicon_fallback`).
**Trigger:** `notes/research_goal_bearing_eval_driver_decomposition_2026-08-06.md` — did-it-happen is
the single largest primary driver (15/36 OOV items, 42%) on `experiments/data/goal_bearing_modern_eval_v1.jsonl`,
and the highest-leverage build is wiring it as an INPUT SIGNAL into the existing congruence organ, not
a standalone detector.

## HEADLINE

**READING THE CODE CHANGED THE DESIGN.** `find_actual_state_candidates` has **zero negation-awareness**
today (confirmed: no call to `_verb_negated_before` or any negation logic anywhere in it or in
`congruence_decision`) — so the core did-it-happen fix is a small, clean, 2-part ADD: (1) an
**occurrence-gate** that flips `_class_relation`'s same/opposed verdict when the actual candidate's own
verb is negated (reuses `_verb_negated_before` verbatim, unrestricted to goal-governing verbs), and (2) a
**goal-verb-recurrence channel** that lets a class-registry-OOV verb still become a candidate when it is
lemma-identical to the desired verb itself (reuses `lemma_verb`). **But disk-running the harness against
all 15 did-it-happen-primary items surfaced a THIRD, previously-undocumented architectural gap that the
task's 4 mandated subtlety cases only partially cover: `congruence_outcome_valence` hardcodes
`outcome_sentence = sents[-1]` (the literal last split sentence) — when the true resolving clause is not
the passage's final sentence (trailing dialogue/reaction/evaluative sentence follows it), the occurrence-
gate never sees it, no matter how good the negation logic is.** Empirically this GAP-1 (fixed single-
sentence outcome window) blocks **6 of the 9 currently-wrong did-it-happen items** (a comparable
footprint to the negation-detection fix itself), and it double-blocks 2 of the task's 4 mandated
subtlety cases (`race_davey_wiffle`, `onestop_limal_dating`) independent of any negation logic. The other
2 mandated subtlety cases (`agg_anne_avery_scholarship`'s false-negative, `race_german_dog`'s final-state
read) turn out, on inspection, to be **already non-issues for cross-sentence scope** — the existing
`sents[:-1]`/`sents[-1]` split already isolates the true resolving clause from the earlier false-signal,
so those two "subtleties" reduce to a plain single-sentence negation read, which the core occurrence-gate
handles directly. Net: the honest realistic reachable for did-it-happen-alone (occurrence-gate +
recurrence channel, no window widening) is **narrower than the driver-decomposition note's 8/36 estimate**
— roughly 2-4 of the 15 primary items — because half the currently-wrong items need the window-widening
companion too. Window-widening is designed below as a strict-ADD companion (P deflated further for it,
see Honest Scope).

## Brain -> organ map (situation-model goal-status tracking / occurrence-polarity)

Human readers maintain a **situation model** of the unfolding narrative with goal/intentionality as one
of its core tracked dimensions, distinct from the surface text form (Zwaan & Radvansky 1998,
*Psychological Bulletin* 123(2):162-185). Comprehension research shows readers build a **causal network**
linking goal -> attempt -> outcome events, and the goal-outcome causal link specifically predicts recall
and perceived importance of a clause (Trabasso & van den Broek 1985, *J. Memory & Language* 24:612-630;
Trabasso & Sperry 1985, same volume, 595-611). Readers actively **monitor whether a protagonist's stated
goal-plan succeeds or fails** as a distinct inferential act during reading, evidenced by talk-aloud
protocols and recognition priming (Suh & Trabasso 1993, *J. Memory & Language* 32(3):279-300) — this is
the closest direct precedent for "did-it-happen" as a dedicated situation-model READOUT, not a byproduct
of verb valence. At the event-perception level, comprehension effort spikes at event boundaries generally
(Zacks, Speer, Swallow, Braver & Reynolds 2007, *Psychological Bulletin* 133(2):273-293) — goal-resolution
is one of the strongest such boundary triggers. Negation processing is a well-studied, DISTINCT two-step
phenomenon (simulate the negated proposition's content first, then integrate the "not" — Kaup, Lüdtke &
Zwaan 2006, *J. Pragmatics* 38(7):1033-1050; Kaup, Yaxley, Madden, Zwaan & Lüdtke 2007, *QJEP* 60(7):976-990),
distinguishable from the separate activation-suppression account of negation (MacDonald & Just 1989,
*JEP:LMC* 15(4):633-642). Citations independently verified this cycle by a Sonnet lit-scan sub-agent
(generic cognitive-science search terms, no substrate framing) — see Citations section.

**Organ mapping (brain structure -> our organ, per [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]):**
- Situation-model goal/intentionality dimension tracking -> `hdlab/goal_typing.py`'s
  `find_desired_state`/`congruence_decision` pair (already built; this is the organ that HOLDS the
  goal-status readout).
- Did-it-happen occurrence-polarity readout on the causal goal-outcome link (Suh & Trabasso's monitoring
  act) -> **NOT YET BUILT as a distinct signal** — currently conflated with (and structurally dependent
  on) verb-pole/class lookup, which is the wrong shape (a lexical fact, not a discourse-occurrence fact).
  This spec builds the missing distinct readout.
- Negation two-step simulation -> `_verb_negated_before` (already built, commit c2f88ea91, on the GOAL
  side only). This spec's core move is applying the SAME general-purpose negation-scope scanner to the
  OUTCOME side, where it has never been called.

## Code-verified findings (all numbers are LIVE production code, run read-only this cycle)

Ran `hdlab.goal_typing.congruence_with_lexicon_fallback` + `_sentences` against all 15 did-it-happen-
primary items from the driver-decomposition table (`experiments/data/goal_bearing_modern_eval_v1.jsonl`):

| id | gold | current pred | correct today? | true-resolution verb in `sents[-1]`? |
|---|---|---|---|---|
| lw_meg_currant_jelly | UNMET | NONE | NO | yes, but blocked by a SEPARATE bug (GAP-2, below) |
| lw_laurie_flower_table_amy | MET | NONE | NO | **NO** (GAP-1) |
| agg_gilbert_pond_rescue_friendship_plea | UNMET | UNMET | yes (lexicon-luck) | no, but already right |
| agg_anne_pudding_sauce_mouse | UNMET | UNMET | yes (lexicon-luck) | no, but already right |
| agg_anne_mrs_barry_forgiveness | UNMET | NONE | NO | **NO** (GAP-1) |
| woz_dorothy_kansas_wish | MET | NONE | NO | **NO** (GAP-1) |
| woz_scarecrow_brains | MET | MET | yes (lexicon-luck, fragile) | no (GAP-1 present but currently masked by luck) |
| woz_tin_woodman_heart | MET | NONE | NO | NO — needs synonym bridging, not recurrence (see below) |
| woz_lion_courage_denied | UNMET | UNMET | **yes, correctly** | yes — clean in-window negation |
| alice_beautiful_garden | MET | MET | **yes, correctly** | yes — clean in-window recurrence |
| race_german_dog | UNMET | UNMET | yes (lexicon-luck, fragile) | yes — clean in-window negation (occurrence-gate would get this right for the RIGHT reason, replacing luck) |
| race_davey_wiffle | MET | NONE | NO | **NO** (GAP-1, task's mandated exception-scope case) |
| onestop_malala | MET | NONE | NO | ambiguous substring match, needs care |
| onestop_hunt_crowdfunding | MET | NONE | NO | yes — clean in-window, needs recurrence channel (task's mandated multi-attempt case, half) |
| onestop_limal_dating | MET | NONE | NO | **NO** (GAP-1, task's mandated multi-attempt case, other half) |

**6/15 already correct today** (2 genuinely via structure that will remain correct, 1 via the occurrence-
gate replacing luck with the right mechanism, 3 via **lexicon-fallback coincidence** — `lexicon_predict`'s
Tier-2 open-vocab similarity scan has NO negation-scope logic either, so `race_german_dog`'s and
`woz_scarecrow_brains`'s correctness today is fragile word-similarity luck, not comprehension; flagged as
a non-regression risk below, not counted as "solved").

### GAP-1 (newly found, not in the task's framing): fixed single-last-sentence outcome window

`congruence_outcome_valence` (`hdlab/goal_typing.py:935-942`) is purely positional:
```python
def congruence_outcome_valence(passage_text: str):
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    return congruence_decision(sents[:-1], sents[-1])
```
`sents[-1]` is treated as THE outcome sentence unconditionally. When a passage's true resolving clause is
followed by a trailing sentence of dialogue, reaction, or evaluative content (extremely common in real
narrative prose — 3 of the 4 concretely-checked failing items above have this shape), the resolving
clause is **never scanned by `find_actual_state_candidates` at all**, independent of how good any
did-it-happen negation logic is. This blocks `lw_laurie_flower_table_amy`, `agg_anne_mrs_barry_forgiveness`,
`woz_dorothy_kansas_wish`, `race_davey_wiffle` (the task's mandated exception-scope case), and
`onestop_limal_dating` (half of the task's mandated multi-attempt case) — **5 of the 9 currently-wrong
items**, a footprint comparable in size to the negation-detection gap itself.

### GAP-2 (newly found): `find_desired_state`'s first-match-wins can pick the wrong goal clause

`lw_meg_currant_jelly`'s goal region is: *"Fired with a housewifely wish to **see** her storeroom stocked
[...] Meg resolved to **fill** them all [...]"* — two desiderative clauses. `find_desired_state` iterates
`goal_sentences` and returns on the FIRST `GOAL_GOVERNING_PASS` match found (`goal_typing.py:824-827`,
`next((...), None)`), landing on `"see"` (an `ARG0`-referent-less verb with **no CLASS_REGISTRY class at
all**) instead of the more goal-relevant `"fill"`. Disk-confirmed: `desired["classes"] == set()` and
`desired["referent"] is None` for this item — `_class_relation` returns `None` unconditionally whenever
`desired_classes` is empty (`same = bool(set() & actual) == False` always; `opposed` likewise), so **no
occurrence-gate design, however good, can fix this item** — it needs the same "not just first match, all
class-related candidates" upgrade `find_actual_state_candidates` already got on the OUTCOME side
(`find_actual_state_candidates`'s own docstring documents this exact class of fix having been made there)
applied symmetrically to the GOAL side. This is genuinely out of did-it-happen's charter but is flagged
here because it silently caps the did-it-happen-solve rate on at least this 1 item, and is a cheap,
directly-analogous follow-up (candidate-list + best-class-match instead of first-desiderative-match).

### GAP-3 (the core, correctly-scoped mechanism): zero negation-awareness on the outcome side

Confirmed by reading `find_actual_state_candidates` (`goal_typing.py:853-867`) end to end: it lemmatizes
every token, classifies via `_verb_classes`, and appends a candidate if `classes` is non-empty — no
negation check anywhere. This is the direct, correctly-scoped did-it-happen gap the task asked for, and
is design below.

### GAP-4 (lexical, small but concrete): `lemma_verb`'s irregular table has no past-participle rule

`_IRREGULAR_LEMMA` (`hdlab/thematic_role_labeler.py:160-175`) maps simple-past forms (`gave->give`,
`came->come`, `found->find`, `made->make`) but has **no entry for past participles** (`given`, `spoken`,
`written`, `broken`, `known`, `shown`, `grown`, `worn`, `chosen`, `beaten`, ...) and `lemma_verb`'s suffix
rules (`-ing`, `-ied`, `-ed`, `-es`, `-s`) don't cover the `-en` participle pattern either. Concretely:
`lemma_verb("given")` returns `"given"` unchanged, NOT `"give"`. This directly weakens the goal-verb-
recurrence channel on exactly the construction it's meant to catch (`"I have **given** you [...] brains"`,
`woz_scarecrow_brains` — though that item is separately GAP-1-blocked too, so this doesn't change its
outcome, but WILL matter for other items once GAP-1 is fixed). Flagged as a small, bounded, closed-list
addition (11-15 more irregular-participle entries), not a new mechanism.

## Design — the occurrence-gate (core, GAP-3)

**1. Negation flag on every candidate (strict ADD to `find_actual_state_candidates`):**
```python
def find_actual_state_candidates(sentence: str):
    toks = _tokens(sentence)
    out = []
    for idx, t in enumerate(toks):
        lemma = lemma_verb(t)
        classes = _verb_classes(lemma)
        if classes:
            referent = _np_last_content(toks[:idx])
            out.append({"referent": referent, "classes": classes, "verb_lemma": lemma,
                        "verb_idx": idx, "negated": _verb_negated_before(toks, idx)})   # <-- NEW
    return out
```
`_verb_negated_before` is reused **verbatim, unmodified** — it is already lexeme-independent (takes
`toks`/`v_idx`, not a fixed verb set) and already carries the precision guards proven on the goal side
(litotes/complement-negation false-positive avoidance, do-support/modal/"never" adjacency, transparent-
adverb skip window). Calling it on an arbitrary outcome-side verb index is the SAME operation it already
performs on goal-side verb indices — zero new taxonomy, zero new parsing.

**2. The occurrence-gate itself (strict ADD to `congruence_decision`, ~3 lines at the relation-computation
site, `goal_typing.py:918`):**
```python
relation = _class_relation(desired["classes"], actual["classes"])
if relation is not None and actual.get("negated"):
    relation = "opposed" if relation == "same" else "same"     # <-- NEW: occurrence-gate polarity flip
```
This is a pure XOR: a negated actual verb whose raw class-relation would be "same" (the wanted THING
happened lexically) becomes "opposed" (it did NOT actually happen -> UNMET) — `lw_meg_currant_jelly`'s
`"wouldn't jell"` class. A negated actual verb whose raw class-relation is "opposed" (e.g., desired=`win`,
actual=`lose`, i.e. FAIL_LOSE) becomes "same" under negation (`"didn't lose"` reads as an achieved goal)
— the general double-negative-is-positive case, included for completeness though no eval item currently
exercises it. **Precision-critical property, verified by design not yet by run:** this only fires when
`relation is not None`, i.e. only on candidates that ALREADY passed class-relatedness — it can never
create a MET/UNMET verdict out of a class-unrelated candidate, so it cannot regress the `NA` abstain path.

**3. Goal-verb-recurrence channel (independent path, for class-registry-OOV verbs — covers
`onestop_hunt_crowdfunding`'s `"make"`):**
```python
# inside find_actual_state_candidates, per-token loop, AFTER the existing classes = _verb_classes(lemma):
if not classes and desired_verb_lemma is not None and lemma == desired_verb_lemma:
    classes = {"RECURRENCE_MATCH"}
```
`RECURRENCE_MATCH` is a new one-element sentinel, structurally identical in kind to the existing
`ACQUIRED_REALIZED`/`ACQUIRED_BLOCKED` Tier-3 pole sentinels (`goal_typing.py:601-656` — same pattern,
same precedent, same "never fires unless the specific condition holds" safety property). `_class_relation`
needs one new branch: `RECURRENCE_MATCH` vs `desired["classes"]` containing the SAME verb_lemma trivially
counts as `"same"` (then the occurrence-gate in step 2 flips it if `negated`). This requires threading
`desired["verb_lemma"]` into `find_actual_state_candidates` as a new parameter (today it takes only
`sentence`) — a real signature change, but a small, mechanical, strictly-additive one (existing callers
that don't pass it get `desired_verb_lemma=None`, and the new branch never fires, byte-identical).
**Precision guard needed (not yet built):** must NOT fire on light/function verbs that happen to recur
coincidentally (e.g. "said", "was") — restrict the recurrence channel to verb lemmas already excluded
from `_NEG_TRANSPARENT_ADVERBS`-style function-word noise, or simplest: only accept recurrence when
`desired_verb_lemma` is itself a content verb of length > 3 and not in a small closed stop-list of copulas/
light verbs (`be`, `do`, `have`, `say`, `get`) reused from `GOAL_ASPECT_SEED_LEMMAS`'s neighborhood. This
guard is a MANDATORY can-fail check in the pre-reg (see below) — the risk is concrete: the anti-drift-leak
finding already logged this same day (`{answered, carried}` self-locking POS under a different mechanism)
is the exact failure class recurrence-without-a-stoplist would reproduce.

## Design — outcome-window widening (companion, GAP-1, required for ~5-6/15 items)

```python
def congruence_outcome_valence_windowed(passage_text: str, max_window: int = 4):
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    goal_sentences = sents[:-1]
    for k in range(1, min(max_window, len(sents) - 1) + 1):
        outcome_sentence = sents[-k]
        if find_actual_state_candidates(outcome_sentence):     # candidate-nonempty gate
            return congruence_decision(goal_sentences, outcome_sentence)
    return congruence_decision(goal_sentences, sents[-1])       # byte-identical fallback
```
**Strict-widen property:** when `sents[-1]` already yields >=1 candidate (today's common, majority case),
`k=1` wins immediately -> byte-identical to `congruence_outcome_valence` for every currently-typed item.
Only steps backward when the closest-to-end sentence is candidate-EMPTY, which directly encodes "read to
the true final state, nearest-to-end wins" (the task's subtlety #4 framing) rather than a naive whole-
passage scan. **Named risk (must be pre-registered, not assumed safe):** stepping backward could pick up
an EARLIER, WRONG resolution when the true final resolution is expressed ONLY via bridging/affect language
with no class-related or recurrence verb at all (`woz_scarecrow_brains`'s `sents[-1]` — "pleased and
proud" — has zero candidates under this design too, so widening would step to sentence 4, "given [...]
brains" — that IS the correct clause here, a lucky alignment, but a passage where a class-related INTERIM-
FAILURE clause sits between the true resolution and the end would make widening pick the wrong one). This
requires an explicit non-regression ablation over the full 44 items, not just the 15 did-it-happen items,
before this companion can ship (Pre-reg Check 4).

## The 4 mandated subtlety cases, re-analyzed against the empirical run

1. **EXCEPTION-SCOPE (`race_davey_wiffle`):** confirmed **NOT a negation-scope-parsing problem** — the
   true resolving clause ("except the one with eight oblong holes...") is `sents[3]`, not `sents[-1]`
   (`sents[-1]` is "Davey was now striking out so many batters..."). Blocked by GAP-1 alone; once window-
   widening reaches `sents[3]`, no special EXCEPT-clause parser is needed because `find_actual_state_
   candidates` already returns ALL class-related verb occurrences and `congruence_decision`'s Pass-1
   already prefers a referent-LINKED candidate over an unlinked one — "the balls failed" (referent="balls",
   collective) most likely does not referent-link to Davey at all, so "curved"/the specific-ball referent
   should win by construction. **Flagged as needing verification once window-widening is built** — stated
   as a can-fail check, not assumed.
2. **FALSE-NEGATIVE OVERRIDE (`agg_anne_avery_scholarship`):** confirmed **NOT an issue at all** for
   cross-sentence scope — `"So she had failed"` is `sents[3]`, safely inside `goal_sentences` (never
   scanned by `find_actual_state_candidates`); `sents[-1]` is `"...winner of the Avery"` alone, containing
   no false signal. This item is an in-lexicon control (`outcome_in_lexicon=True` per the JSONL, matching
   the task's own framing of it as a control-trap, not an OOV item) whose CURRENT wrong answer
   (`AMBIGUOUS`) traces to a lexicon-ambiguity issue unrelated to did-it-happen — out of this spec's scope,
   noted for completeness.
3. **MULTI-ATTEMPT PERSISTENCE:** the two examples split cleanly. `onestop_hunt_crowdfunding`'s
   interim failure (`"tried [...] but it's slow and difficult"`) is `sents[1]`, safely outside `sents[-1]`
   — a non-issue for cross-sentence scope; this item is solved by the recurrence channel alone (its
   `sents[-1]` literally contains `"made 400,000 pounds"`, OOV of `CLASS_REGISTRY`). `onestop_limal_dating`
   is the harder half: `"without success"` (`sents[1]`) is also safely outside scope, but the TRUE
   resolution `"Limal has finally found love"` is `sents[3]`, NOT `sents[-1]` (`sents[-1]` is unrelated
   dialogue) — GAP-1-blocked, needs window-widening.
4. **FINAL-STATE READING (`race_german_dog`):** confirmed a clean, single-sentence case — `sents[-1]` IS
   `"He never came back"` alone; the repeated prior pattern (`"German was back again"` x N) lives entirely
   in `goal_sentences` and is never scanned. Already correct today, but via **lexicon-fallback coincidence**
   (`lexicon_predict`'s Tier-2 similarity scan has no negation logic either — it is guessing from word
   similarity, not detecting "never"). The occurrence-gate design gives the RIGHT mechanism for the same
   right answer — this is a **replace-luck-with-reasoning** case, not a new win, and must be pre-registered
   as a non-regression check (still UNMET after the change) rather than counted as new lift.

## Owner-attribution companion (7/15 need it — design-level, per task's lighter-detail ask)

`congruence_decision`'s own referent-linking (`_referent_links`, tiers literal/pronoun_coref/shared_feature)
is a NOUN-PHRASE-to-NOUN-PHRASE matcher; it cannot bridge "his dad ... decided to find a better solution"
(surface actor = Dad) to "Davey's goal" (true beneficiary = Davey) — that is a DELEGATE-ACTOR-TO-BENEFICIARY
relation, structurally different from coreference. The right reuse target is `hdlab/goal_owner_select.py`'s
`select_outcome_owner` — the DIRECTED, non-symmetric coherence-score engine purpose-built for exactly this
class of problem (Component-5, `directed_goal_outcome_score` + `GoalOutcomeRegister`, already disk-VET'd on
recency-trap items). Two integration shapes, presented for a build-time decision (not decided here):

- **(a) SHALLOW (cheap, lower ceiling):** run `select_outcome_owner` once per item to get the resolved
  owner entity, then bias `_referent_links` to accept a referent that COREF-chains to that owner (reusing
  `hdlab/event_centrality_coref.py` / `coreference_resolver.py`'s antecedent-chain, e.g. "his son" ->
  possessive-pronoun-chain -> "Davey") as an ADDITIONAL link tier. Bounded, additive, no signature change
  to `congruence_decision` itself (the owner lookup happens in the caller, one level up).
- **(b) DEEP (brain-faithful, higher ceiling, more invasive):** thread a `roster` argument through
  `congruence_decision`/`find_actual_state_candidates` and replace the plain tier-based `_referent_links`
  check with a call into the SAME directed coherence-score organ `select_outcome_owner` already uses —
  i.e., does binding the actual-candidate's outcome slot to the desired referent score higher than binding
  it to any other roster entity, under `directed_goal_outcome_score`. This is the RIGHT answer per
  [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]
  (reuse the purpose-built directed-binding organ rather than a shallower coref hack), but requires a real
  signature change (roster threading) through 3 functions — flagged explicitly as the "harder than it
  looks" item for this companion; NOT scoped as part of this cycle's build, left for a follow-up FORMALIZE
  pass once did-it-happen + window-widening are landed and measured standalone (so the owner-companion's
  OWN lift can be isolated per the driver-decomposition note's Prediction 2, not confounded).

## Pre-reg — can-fail bands (see `preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md` for the formal doc)

Baselines on `experiments/data/goal_bearing_modern_eval_v1.jsonl` (36 OOV items), all disk-measured this
cycle or cited from same-day BACKUP-doc-logged runs:
- empty-overlay floor: 0.1667 (6/36)
- majority-class floor: 0.6389 (23/36, all-MET)
- current production (`congruence_with_lexicon_fallback`, no did-it-happen): **measured this cycle,
  full 36-item run not yet re-executed by this spec pass** — spot-checked 15/15 did-it-happen-primary items
  above (6/15 correct = 0.40 on that subset); cell-author must re-run the full 36 before landing to get the
  true current whole-eval number (distinct from the 16/36=0.4444 increment-1b number and the 0.1944
  combined-dict+consequence number cited in the BACKUP doc, which used a DIFFERENT acquisition mechanism
  layered on top — this spec's baseline is the BARE congruence organ, acquisition-mechanism-independent).

**Bands (Occurrence-gate + recurrence channel only, GAP-3 scope, no window-widening):**
- HARD-PASS: net new-correct on the 15-item did-it-happen-primary subset >= 2 (realistic reachable per the
  empirical table: `lw_meg_currant_jelly` blocked by GAP-2 so excluded; `onestop_hunt_crowdfunding` and
  `onestop_malala` are the only in-window, non-GAP-1-blocked wrong items — expect 1-2 of these to flip),
  AND zero regressions on the 6 currently-correct items (2 of which are lexicon-luck and must be verified
  to stay right for the SAME reason or a better one, not silently broken), AND the 2 in-lexicon numeric-
  threshold traps (`race_chen_situps`, `onestop_carle_madeinfrance`) remain correctly UNMET (not flipped
  by an over-eager recurrence or negation match).
- HARD-FAIL: any regression on a currently-correct item, OR the recurrence channel produces a false MET/
  UNMET on any of the 8 `NOISE` light-verb items already tracked in
  `verification/verify_grounded_word_acquisition_increment1b.py` (`answered`, `carried`, etc. — the same
  anti-drift-leak class already caught once this day), OR net new-correct is 0.

**Bands (Window-widening companion, GAP-1 scope):**
- HARD-PASS: recovers >= 3 of the 5 GAP-1-identified items (`lw_laurie_flower_table_amy`,
  `agg_anne_mrs_barry_forgiveness`, `woz_dorothy_kansas_wish`, `race_davey_wiffle`, `onestop_limal_dating`)
  once combined with the occurrence-gate, with ZERO regressions across the FULL 44-item eval (not just the
  36 OOV — window-widening touches the outcome-sentence-selection step used by every item, in-lexicon
  controls included, so the non-regression check must be eval-wide).
- HARD-FAIL: any item that was correct under `sents[-1]`-only selection becomes wrong once widening can
  step backward (would mean an earlier, coincidentally-class-related clause is being preferred over the
  true final one on some item not yet sampled), OR fewer than 2 of the 5 targeted items are recovered.

**4-subtlety cases (explicit, from the task):** report each of the 4 with its ACTUAL cause per this spec's
empirical re-analysis (2 are cross-sentence non-issues needing only in-window negation/recurrence; 2 are
GAP-1-blocked and need window-widening) — a naive first-negation-wins scanner is pre-registered to FAIL
`race_davey_wiffle` and `onestop_limal_dating` even with the occurrence-gate alone (both need window-
widening as a hard prerequisite, not an optional nice-to-have) and to PASS `agg_anne_avery_scholarship`/
`race_german_dog` for the trivial reason that the current sentence-split already isolates the right clause
(so their being "solved" is not evidence the naive-scanner risk was real for THIS eval's phrasing — a
genuinely adjacent-sentence false-negative-then-override case is NOT tested by the current 44 items and
should be flagged as an eval-coverage gap for a future item-writing pass, not claimed as solved).

## Honest scope

Do NOT overclaim: the realistic reachable from occurrence-gate + recurrence channel ALONE, without window-
widening, is **2-4 of the 15 did-it-happen-primary items on top of the 6 already correct today** (several
of which are lexicon-luck, not yet earned) — well short of the driver-decomposition note's 8/36 "clean
subset" estimate, because that estimate implicitly assumed access to whichever sentence a human reader
judged as "the resolving clause," not the production code's literal `sents[-1]`. Window-widening is a
REQUIRED companion, comparably sized to the core mechanism (not a minor polish), to reach anywhere near
that 8-item mark. Owner-attribution is a THIRD, separately-scoped companion (7/15) with real overlap against
the window-widening set (3 of the window-gap items also need owner-attribution), so the three levers are
NOT simply additive — a full build must sequence occurrence-gate -> window-widening -> owner-attribution
and re-measure the marginal lift of each, not assume the driver-decomposition table's per-item single-cause
tags hold once multiple fixes compound. P_deflated=0.35 for the occurrence-gate + recurrence channel alone
(concrete, code-verified, small-diff, high confidence in the MECHANISM being right; deflated per lit-scan
calibration discipline because the REALISTIC eval-wide lift is unmeasured and the 15-item sample above is
hand-traced, not yet a full harness run). P_deflated=0.25 for window-widening (real risk of an earlier-
clause false-pick not yet ruled out by any run). P_deflated=0.20 for the owner-attribution DEEP integration
(b) (real signature-change cost, unbuilt, unmeasured or even smoke-tested).

## Cross-thread synthesis

Directly implements the highest-leverage build named in `notes/research_goal_bearing_eval_driver_
decomposition_2026-08-06.md` ("wire did-it-happen as an input signal into the existing goal-congruence
organ, not a standalone detector") and sharpens it: the "goal-congruence organ" the driver-decomposition
note pointed at is not one function but a small pipeline (`congruence_outcome_valence` -> `congruence_
decision` -> `find_actual_state_candidates`/`find_desired_state`), and did-it-happen's own effectiveness is
gated by a structural property of that pipeline (single-sentence outcome window) the prior analysis did not
have visibility into (it worked from the eval's TEXT, not from tracing the production code's exact
sentence-selection behavior). This is a direct instance of [[feedback_every_negative_check_missing_
component_especially_learning_USER_2026-08-04]]'s sibling discipline — here the missing component is not a
new organ OR a new signal, but a structural WIDENING of an existing organ's input scope, discovered only by
reading the code end to end as this FORMALIZE drill requires. Also directly continues the negation-scope
work landed this session (commit c2f88ea91, `_verb_negated_before`) by identifying its natural second call
site (outcome side, never yet used) rather than building a parallel negation mechanism.

## Substrate-product implications

A "did this character get what they wanted" reader that only wires negation-detection into the EXISTING
single-sentence outcome window will plateau quickly on real prose, because real narrative resolution
clauses are frequently followed by a reaction/dialogue sentence (a very common narrative pattern — 5/15 of
this small sample). Shipping occurrence-gate detection without window-widening would look like a real win
in a narrow eval and then silently fail to generalize to any passage with a trailing reaction sentence —
precisely the kind of construction-determined false win the standing discipline (CONSTRUCTION-PROOF !=
capability-win) warns against. The product-correct build order is occurrence-gate first (small, safe,
clearly-scoped), window-widening second (comparable size, needs its own non-regression pass across the
FULL 44-item eval since it changes sentence-selection for every item), owner-attribution third (largest,
most invasive, has real interaction effects with window-widening that must be measured, not assumed).

## Citations (verified count: 6, all confirmed real this cycle by a dedicated Sonnet lit-scan sub-agent
using generic cognitive-science search terms per query-privacy discipline)

1. Zwaan, R.A. & Radvansky, G.A. (1998). Situation models in language comprehension and memory.
   *Psychological Bulletin* 123(2):162-185.
2. Trabasso, T. & van den Broek, P. (1985). Causal thinking and the representation of narrative events.
   *Journal of Memory and Language* 24:612-630.
3. Trabasso, T. & Sperry, L.L. (1985). Causal relatedness and importance of story events. *Journal of
   Memory and Language* 24:595-611.
4. Suh, S. & Trabasso, T. (1993). Inferences during reading: converging evidence from discourse analysis,
   talk-aloud protocols, and recognition priming. *Journal of Memory and Language* 32(3):279-300.
5. Zacks, J.M., Speer, N.K., Swallow, K.M., Braver, T.S. & Reynolds, J.R. (2007). Event perception: a
   mind/brain perspective. *Psychological Bulletin* 133(2):273-293.
6. Kaup, B., Lüdtke, J. & Zwaan, R.A. (2006). Processing negated sentences with contradictory predicates:
   is a door that is not open mentally closed? *Journal of Pragmatics* 38(7):1033-1050. (Companion: Kaup,
   Yaxley, Madden, Zwaan & Lüdtke 2007, *QJEP* 60(7):976-990.)

No lit-scan calibration penalty on the citation-verification pass itself (these are confirmed, well-
established findings, not novel synthesis). Calibration penalty applied instead to the P estimates in
Honest Scope, per [[feedback-lit-scan-calibration-penalty]] (deflated 0.15-0.25 off a naive read, capped
below 0.50 for the novel window-widening/owner-integration synthesis pieces).
