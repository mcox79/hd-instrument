# Research note: brain-faithful OUTCOME-VALENCE DETECTOR (design drill, no cell)

Date: 2026-08-05. Dispatched as a DESIGN DRILL (no cell) to formalize the dominant remaining
lever for real-prose goal-owner attribution. Disk-verified this session against the actual code
(not summarized from memory): `hdlab/goal_owner_select.py`, `hdlab/situation_model_accumulate.py`,
`hdlab/thematic_role_labeler.py`, `hdlab/predictive_coding.py`, `experiments/mine_goal_outcome_
litbank_v1.py`, `experiments/exp_c5_realtext_c3mined_v1.py`, `experiments/exp_c5_realtext_c3mined_
v2_38item_v1.py`, `experiments/exp_grounded_valence_read_from_text_v1.py`.

## HEADLINE

The 14/38 TYPING_MISS bottleneck is not a lexicon-tuning problem, it is a MISSING PIPELINE STAGE:
`directed_goal_outcome_score` (hdlab/goal_owner_select.py) is a SELECTION organ that presupposes
each candidate event is already role-typed (R_GOAL/R_UNMET/R_MET) -- it has no mechanism to look
at raw sentence text and decide "is this the outcome, and what's its valence." Today that
stage IS the ACHIEVE_CUES/BLOCK_CUES lexicon (confirmed by direct import: `exp_c5_realtext_
c3mined_v1.py` line 55 `from mine_goal_outcome_litbank_v1 import ACHIEVE_CUES, BLOCK_CUES`), so
"detection" and "the thing being measured against" are the SAME artifact -- which is exactly why
it under-fires on real prose and why broadening it is whack-a-mole. The fix is a new DETECTION
stage built from goal-OBJECT relevance (via C3's already-EARNED thematic-role frame) + a small
closed-class STRUCTURAL negation/state-change guard, not a bigger open-class word list. This
stage is new construction (no existing organ does it); it FEEDS `directed_goal_outcome_score`
unchanged, so C5's downstream selection math is untouched and still unifies with this arc.

## 1. Biology (SHAPE + POSITION + METRIC)

**Shape.** Zwaan & Radvansky's event-indexing model (situation-model theory, extending van Dijk &
Kintsch propositional textbases) tracks five dimensions readers monitor across a narrative:
space, time, causation, protagonist, and **intentionality**. The intentionality dimension is a
GOAL STACK: when a character's goal is introduced, the reader opens a monitored slot that stays
"active" (elevated activation, faster probe RTs for goal-relevant material -- Suh & Trabasso 1993;
Trabasso & van den Broek 1985 causal-network goal-plan structures) until a later event's STATE
matches or contradicts the goal's desired state, at which point the slot is CLOSED (activation
drops, probe RTs return to baseline). This is a **state-comparison**, not a lexical-trigger
operation: the reader represents the goal as a desired PROPOSITION (agent has/achieves/avoids
object-or-state X), and monitors subsequent clauses for a state-change event whose resulting state
either SATISFIES or NEGATES that proposition. This is computationally the same operation as
prospective-memory intention-completion monitoring (an intended action's target state is compared
against perceived world-state on every relevant update) and functions like a domain-general
prediction-error/expectancy-match computation: match -> goal-satisfied appraisal (positive
valence, "relief/pride" affect literature), mismatch/negation-of-desired-state -> goal-blocked
appraisal (negative valence, "frustration/disappointment"). Multiple readers'-eye-movement and
probe-recognition studies (Zwaan, Magliano & Graesser 1995; Albrecht & O'Brien 1993 on goal
inconsistency slowing reading) converge on: readers do NOT wait for a specific vocabulary word,
they compute goal-relevance + polarity from the clause's propositional content continuously.

**Position.** Prefrontal/hippocampal goal-maintenance circuitry (dlPFC sustained representation of
the goal proposition; hippocampal/parahippocampal situation-model updating on each new clause,
the same relational-binding machinery already mapped for this project's coreference and causal-
link work) -- this is squarely the SAME neural machinery already mapped for `CausalLinkRegister`
and `GoalOutcomeRegister` (situation-model accumulate-register family), not a separate system.

**Metric.** The brain's discriminator is: (goal-relevant-content overlap between the goal
proposition and the candidate clause) x (polarity match: does the clause assert or negate the
goal's desired state). NOT: does the clause contain a word from a fixed achieve/fail vocabulary.
A brain-faithful detector must therefore be built from (a) an OBJECT/STATE relevance gate and (b)
a STRUCTURAL (negation-scope) polarity computation -- both closed-class, compositional signals --
rather than an open-class lexicon lookup.

## 2. Reuse check (WIRE-DON'T-ISLAND, read the code)

- **`directed_goal_outcome_score` / `GoalOutcomeRegister` (hdlab/goal_owner_select.py) -- NOT
  reusable for detection, IS reusable as the downstream consumer.** Read line-by-line: it takes
  `role_seq` (a list of ALREADY-ASSIGNED role labels, R_GOAL/R_UNMET/R_MET/R_ACTION) and
  `cluster_ids` (already-resolved entity ids) and asks only "does the entity bound to the outcome
  slot ALSO carry an earlier GOAL role, under this candidate's own assignment." It has zero
  access to raw sentence text or lexical content -- it cannot decide which sentence IS the outcome
  or what its valence is; that decision must already have been made before this function is
  called. This is the exact stage that's currently the lexicon. **Verdict: reuse as-is for
  selection/binding (unchanged); it is the wrong tool for detection.**
- **`GoalOutcomeRegister.appraise()`** -- also presupposes typed roles already written; same verdict.
- **`hdlab/predictive_coding.py`** -- Friston/Rao-Ballard residual-gated write on the substrate's
  W matrix (pattern-level novelty of a bipolar vector against `sign(W@key)`). This is a
  general novelty/surprise detector over the substrate's OWN associative-memory predictions, not a
  lexical-semantic goal-state comparator -- there is no existing encoding that would make "goal
  proposition" and "candidate clause" bipolar keys whose W-residual meaningfully tracks
  goal-resolution semantics without first building the exact relevance+polarity machinery this
  drill is designing. Checked, not dismissed pre-judgementally: it is architecture for a
  DIFFERENT signal (associative surprise) and would require the detector's output as its INPUT,
  not the other way around. Not the mechanism; noted as a possible LATER layer (residual-gate the
  substrate's uptake of a newly-typed outcome event) but out of scope for the detection stage
  itself.
- **`hdlab/thematic_role_labeler.py` (C3, WIRED, EARNED perceptron) -- REUSABLE, is the load-
  bearing input.** `PSYCH_VERBS` + `_PSYCH_FRAME = {"subj": "EXPERIENCER", "obj": "PATIENT"}`
  already gives, for the GOAL sentence, exactly the goal's OBJECT/THEME slot (what is
  wanted/feared) via the SAME earned role-frame machinery already used to find these sentences.
  This IS the "goal object" the detector needs, at zero new mechanism cost (call the frame slot
  extraction on the goal sentence's `obj` argument).
- **`hdlab/coreference_resolver.py` (WIRED, canonical resolver, atom 29613/29614/29618) --
  REUSABLE** for the object-relevance gate: if the goal object is itself an entity mention (e.g.
  "wanted the necklace" ... later "the necklace was found"), coref-chain identity between the goal
  object mention and a candidate event's PATIENT mention is a non-lexical relevance signal, not a
  word-list.
- **`experiments/exp_grounded_valence_read_from_text_v1.py`'s `grounded_valence_evidence`** --
  read (not promoted to hdlab yet, still experiment-local): a HARM/HELP verb-class read gated by
  a hypothetical/conditional-modality guard (does NOT count a purely hypothetical/threatened event
  as an enacted valence event) and patient/instrument-presence checks. This establishes the
  PATTERN this drill borrows structurally: small closed-class verb-CLASS lexicon (allowed,
  supplied knowledge) + a STRUCTURAL guard (modality/negation), not a large open achieve/block
  word list, and not a bag-of-words match. This is the closest existing precedent for "how to be
  non-brittle without a bigger lexicon" and is the template this drill's mechanism follows.
- **`CausalLinkRegister` (situation_model_accumulate.py)** -- checked (connective-dependent
  CAUSE/EFFECT binding, 'X because Y'). Confirmed (per the session's prior ruling, re-verified by
  reading the class) it requires an explicit causal connective to link events; narrative
  goal->outcome resolution is usually connective-free ("She wanted the necklace. ... Months later,
  it was returned to her."). Correctly ruled out for THIS stage; not reusable for detection.
- **Capability registry / invisible-island HIGH tier**: grepped for valence/sentiment/outcome-
  detection entries -- none exist. This is genuinely new construction, not a rediscovery.

**Named: reusable = C3 thematic-role frame (goal-object extraction) + coreference_resolver
(object-identity relevance) + GoalOutcomeRegister/directed_goal_outcome_score (unchanged
downstream consumer) + the grounded_valence_read closed-class-verb-plus-structural-guard PATTERN.
Genuinely new = the relevance-scoring + negation-scope polarity computation that turns a raw
candidate sentence into a (typed_role, valence) pair.**

## 3. The mechanism (glass-box, deterministic)

Given: a GOAL item = (goal_owner, goal_object_or_predicate, polarity in {desiderative, aversive})
extracted from the C3 frame on the goal sentence (subj=EXPERIENCER already resolved to
goal_owner via the roster/coref resolver; obj=PATIENT slot text = goal_object; for embedded-clause
goals ("hoped to escape" / "feared that X would happen") recursively apply the SAME frame
extraction to the embedded verb phrase's own subj/obj, giving an embedded PREDICATE instead of an
object -- both cases reduce to "the desired PROPOSITION").

For each candidate sentence in the forward window:

**(a) Relevance gate** (does this sentence talk about the goal-relevant content at all?):
  - noun-goal case: candidate sentence's own PATIENT/THEME slot (via the SAME C3 role-labeler
    frame call on the candidate sentence) either (i) head-noun-identical to goal_object, or
    (ii) coref-chain-identical to goal_object (reuse `coreference_resolver` mention linking), or
  - predicate-goal case: candidate sentence's MAIN VERB lemma (via `thematic_role_labeler.
    lemma_verb`, already reused elsewhere in this arc) is identical to the goal's embedded verb
    lemma, or is in a small SUPPLIED near-synonym set for that one verb (e.g. escape ~
    {flee, get_away, break_free} -- knowledge, not a general achieve/block list; scoped per-goal-
    verb, not corpus-wide).
  Relevance score = 1.0 if either test fires, else 0.0. Sentences scoring 0.0 are dropped from
  consideration (this replaces the mining lexicon's "any ACHIEVE/BLOCK word anywhere in the
  window" scan with an object/predicate-anchored scan -- the brain-faithful difference: relevance
  is anchored to THE GOAL'S CONTENT, not to a fixed vocabulary).

**(b) Polarity (structural negation/state-change check)**, applied only to relevance-passing
  sentences: scan the sentence for a CLOSED-CLASS negation/failure-modal marker
  (not/never/couldn't/could not/failed to/unable to/refused to/no/without -- ~12 items, a
  structural closed class, not an open achieve/block vocabulary) in the SAME clause as (adjacent
  to, within the clause boundary) the matched predicate/object token from (a). If a negation
  marker scopes over the matched content -> the goal's desired state did NOT come about.
  If desiderative + negation-present -> UNMET (R_UNMET). If desiderative + no negation -> MET
  (R_MET). If aversive + negation-present -> MET (the feared thing was averted, R_MET). If
  aversive + no negation -> UNMET (the feared thing happened, R_UNMET). This is the direct
  computational analogue of Zwaan's state-match/state-mismatch check: match desired-polarity to
  observed-polarity, not "is there a happy word here."
  **Fallback (honest abstain, mirrors `ContentMatchResolver`'s pattern):** if (a) fires but no
  negation marker is present AND the matched predicate is not itself a resultative state predicate
  (small closed class: found/lost/gone/returned/dead/free/safe -- reused from the existing
  ACHIEVE/BLOCK cue set's HIGHEST-precision members only, not the full list), do not force a
  valence call -- ABSTAIN on that sentence and continue scanning the window. This bounds the
  "knowledge supplied" surface to two small closed classes (negation markers, resultative-state
  predicates) instead of the current ~100-item open list.

**Outcome pick**: among relevance-passing, polarity-resolved candidates in the forward window,
pick the FIRST one (Zwaan: readers resolve a goal at first disconfirming/confirming evidence, not
at the most recent one -- recency-within-relevance is a candidate ablation, see eval). Emit
(entity=goal_owner, role=R_MET|R_UNMET) exactly as `type_sentence_events_c3` does today, so
`directed_goal_outcome_score` / `GoalOutcomeRegister` consume it completely unchanged.

**Supplied vs earned, stated honestly:** SUPPLIED = the ~12-item negation/failure-modal closed
class + the ~7-item resultative-state closed class + per-goal-verb near-synonym sets (small,
scoped, not a general sentiment lexicon) + C3's VERB_FRAMES table (already-declared supplied
knowledge in that module's own docstring). EARNED = the relevance-anchoring computation itself
(which content counts as "about this goal" is computed from the goal's own extracted
object/predicate, not looked up), the negation-scope structural check, and the composition of
these with C3's EARNED perceptron role assignment and the coref resolver's EARNED mention-linking.
This is a smaller and more principled supplied-knowledge surface than the current ~100-word
open-class achieve/block lexicon, and it is structurally guarded (scope/modality) rather than
bag-of-words.

## 4. Pre-registered eval

**Data**: `experiments/data/goal_outcome_c3mined_v1.jsonl` (38 items, each carries a mined
`outcome_span` sentence + `outcome_polarity` in {achieved, blocked, mixed}).

**KNOWN CIRCULARITY CAVEAT (must be reported, not buried):** this item bank was ITSELF mined by
scanning for an ACHIEVE_CUES/BLOCK_CUES hit within the forward window (see
`mine_goal_outcome_litbank_v1.py` lines 209-225) -- so the population is, by construction, biased
toward outcomes the lexicon CAN detect. A genuinely different mechanism can only be shown to (i)
match the mined outcome_span position/polarity as well or better on THIS lexicon-selected
population, and (ii) survive an ablation that proves it is not just re-deriving the same lexicon
hit. It CANNOT, on this item bank alone, prove it generalizes to outcomes the lexicon misses
entirely (that would require a fresh mining pass using the new detector itself, out of scope for
this eval -- named here as the natural next drill).

**Metrics** (typed items only, denominator = n_relevance_fires):
  - `outcome_detection_accuracy` = fraction where the picked sentence index == mined outcome_idx
    (index of `outcome_span` in the item's sentence list).
  - `outcome_valence_accuracy` = fraction where picked polarity == mined `outcome_polarity`
    (collapsing "mixed" to whichever the detector is allowed to abstain on, reported separately).
  - `detector_fire_rate` = n_relevance_fires / 38, reported against the lexicon's own
    `typing_fire_rate` (measured 0.55 on the same-shaped 38-item full-pipeline bucket per commit
    dfabbde26) as the number to beat.
  - **Non-vacuousness ablation (mandatory, mirrors the role-scramble control already used
    elsewhere in this arc):** re-score every item with the goal_object/predicate STRING SCRAMBLED
    across items (goal i's object paired with item i+1's candidate sentences). A detector that is
    secretly just re-deriving the ACHIEVE/BLOCK lexicon hit (ignoring the goal-object match) will
    show little to no accuracy drop under this scramble; a genuinely directed detector should
    collapse toward the base rate of the resultative-state fallback alone.

**HARD-PASS bands** (pre-registered before running, per lit-scan calibration discipline):
  - `outcome_detection_accuracy` >= 0.55 (matches or beats the lexicon's own fire rate as a floor)
    AND `outcome_valence_accuracy` >= 0.65 on relevance-firing items, AND the scramble ablation
    drops detection accuracy by >= 0.20 absolute (proves the object-relevance anchor is doing real
    work, not disguised lexicon-matching).
**HARD-FAIL bands:**
  - `outcome_detection_accuracy` < 0.35 (worse than a plausible base rate for "first
    relevance-passing sentence in a 7-sentence window"), OR the scramble ablation drops accuracy
    by < 0.05 absolute (mechanism is a disguised lexicon lookup, the exact risk flagged by the
    dispatcher), OR `detector_fire_rate` < 0.30 (the relevance gate is too narrow, same brittle-
    coverage failure mode as the original narrow ACHIEVE/BLOCK-adjacent typing attempt this arc
    already diagnosed and fixed once).
  - MIDDLE_BAND (neither): report as directional, same discipline as the existing 38-item
    measurement cell (`exp_c5_realtext_c3mined_v2_38item_v1.py` sets the precedent: this is a
    MEASUREMENT cell, not a forced pass/fail, given N=38).

## 5. Cross-thread synthesis

This detector is the missing UPSTREAM stage for the entire C5 goal-owner arc measured this session
(commit dfabbde26, 0.32 end-to-end = 12/38, TYPING_MISS=14/38 the dominant term). It does not
touch `directed_goal_outcome_score`, `GoalOutcomeRegister`, `GeneralRecencyEntityResolver`, or
`ContentMatchResolver` -- those are reused byte-identical, unchanged. It replaces exactly the
`type_sentence_events_c3` function's OUTCOME half (the GOAL half, via C3 PSYCH_VERBS, already
works and is untouched). It also borrows the closed-class-verb-plus-structural-guard PATTERN
already established (independently, same session's broader arc) in
`exp_grounded_valence_read_from_text_v1.py`'s harm/help valence read -- two different sub-problems
(action-valence for causal attribution vs goal-outcome valence) converging on the same design
principle (small supplied verb-class + structural modality/negation guard, not an open lexicon),
which is itself a useful cross-thread finding: this project's THREE separate valence-adjacent
problems (harm/help action valence, goal-outcome valence here, and the earlier-diagnosed causal
connective-dependence gap) all resolve to "ground the read in a small closed-class-plus-structural-
guard computation over an already-extracted argument structure," not in a bigger word list. That
is a reusable DESIGN PRINCIPLE worth naming for future valence-adjacent gaps, not just this one.

## Substrate-product implications

A detector that resolves goal outcomes from OBJECT/PREDICATE relevance rather than a fixed
vocabulary is the difference between a demo that only works on the training template's sentences
and a component that generalizes across arbitrary real prose -- which is the stated blocker
(TYPING_MISS=14/38) for shipping honest real-text goal-owner attribution numbers at all. If the
HARD-PASS bands hold, this closes the dominant failure term in the current end-to-end measurement
without touching (and therefore without risking regression to) the already-VET'd C5 selection
math, which is the cheapest possible fix shape (new upstream stage, zero changes to a validated
downstream consumer).

## Citations (verified count)

This drill is a design/synthesis drill over the project's OWN code (disk-verified, 7 files read
directly, listed at top) plus established psycholinguistics theory cited from memory (Zwaan &
Radvansky 1998 event-indexing model; Trabasso & van den Broek 1985 causal-network goal-plan
structures; Suh & Trabasso 1993 goal-activation probe studies; Albrecht & O'Brien 1993 goal-
inconsistency reading-time effects) -- **0 external web/lit-scan queries were dispatched** (no
sub-agent lit-scan run; the biology citations are canonical situation-model-theory results already
part of this project's standing knowledge base, not a fresh literature search). Per lit-scan
calibration discipline this means the STANDARD external-verification penalty does not apply in the
usual sense (nothing was scanned to inflate), but the NOVEL-SYNTHESIS cap still applies fully
(this is untested original mechanism design) and P below reflects that.

**P_deflated = 0.35** (novel-synthesis cap 0.50 applied, further deflated for: (1) the relevance-
matching step's untested generalization past exact head-noun/verb-lemma identity onto genuine
paraphrase -- the single most likely failure mode named explicitly below; (2) N=38 with a
population-selection circularity caveat that limits what a pass even proves; (3) the negation-
scope check is a simple adjacency heuristic, not real dependency-scope parsing, and could mis-scope
on multi-clause sentences).

**Biggest risk:** goal-object/predicate relevance-matching fails on PARAPHRASE -- a goal stated as
"wanted freedom" and an outcome narrated as "she slipped past the guards at midnight" share no
head noun, no coref chain, and no verb-lemma overlap, so the relevance gate scores 0.0 and the
detector abstains exactly where the lexicon (which would catch "escaped") might have fired. This
is the real-prose-diversity failure mode the C3-mined item bank's `structure_type` diversity axes
were built to probe, and it is the most likely source of a HARD-FAIL or MIDDLE_BAND result on
first measurement.

---

**research: delivered outcome_valence_detector_design -> notes/research_outcome_valence_detector_
design_2026-08-05.md ; HEADLINE: TYPING_MISS is a missing upstream detection STAGE, not a lexicon-
size problem -- reuse C3 frame + coref for goal-object relevance, add a small closed-class
negation-scope polarity check, feed directed_goal_outcome_score unchanged; P_deflated=0.35; next-
drill candidate: same-arc fresh-mining pass using the new detector itself (to escape the current
item bank's lexicon-selection circularity) OR the paraphrase-relevance gap (embedding-based
head-noun/predicate similarity instead of exact-match, if this first spec HARD-FAILs on
paraphrase-heavy structure_type buckets).**
