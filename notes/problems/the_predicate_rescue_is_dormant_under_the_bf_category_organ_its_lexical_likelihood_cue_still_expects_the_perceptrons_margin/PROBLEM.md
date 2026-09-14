---
priority: 107
slug: the_predicate_rescue_is_dormant_under_the_bf_category_organ_its_lexical_likelihood_cue_still_expects_the_perceptrons_margin
status: OPEN
review:
review_text:
---

# PROBLEM: the reader's predicate RESCUE (the organ that recovers a real verb the tagger mis-called a noun) is DORMANT under the brain-foundational category organ -- its lexical-likelihood cue was the supervised perceptron's emission margin, and the stand-in that replaced it reads a bare posterior threshold that never fires.

**slug:** `the_predicate_rescue_is_dormant_under_the_bf_category_organ_its_lexical_likelihood_cue_still_expects_the_perceptrons_margin` -- **opened:** 2026-09-14 00:50 by strategy, found while repairing `verification/test_predicate_recall_landing_organ.py` under the one-default reader fix.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy / nltk taggers / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only. Offline foundation assets (WordNet as the verb-reading gate) are admissible at build time; ship a dict.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** predicate-hood is a CATEGORY decision under context -- it belongs to the category organ (`hdlab/lexical_categories.py`) as an ARM, or to the detector that already exists (`hdlab/predicate_detector.py`) reading the category organ's own quantities. Do NOT build a third organ.
> **PLASTIC, NEVER FROZEN:** knowledge = counts; strengths = one pure function of counts; an online `observe_*` path for anything you add.
> **WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Predicate-hood in the brain is a noisy-channel decision: a LEXICAL LIKELIHOOD (how verb-like is this word form, given what it usually does) combined with a STRUCTURAL PRIOR (a clause wants one predicate; arguments flank it; finite morphology marks it) -- Gibson 2013 noisy-channel comprehension; one-predicate-per-clause competition (Spivey-Knowlton 1993); frequent frames (Mintz 2003); morphology (Monaghan 2005). The existing detector IS this combination (7 cues, glass-box logistic) -- and its lexical-likelihood cue is the ONE thing that was never brain-foundational: `verb_margin` = the supervised perceptron's emission score(VERB) minus its best non-verb score, a quantity that no longer exists on the live path.
> 2. **REUSE.** `hdlab/predicate_detector.py` (`feats_parsefree`, `verb_margin`, `PredicateDetector.rescue_indices`; asset `data/frontend_assets/predicate_detector_ud_qasrl.json`: coef / mu / sd / threshold -- the verb_margin feature's mu is -20.6 and sd 14.5, the perceptron's raw weight scale); the builder `experiments/exp_register_predicate_detector_v1.py` (self-supervised auto-labels = the tagger's natural errors on gold held out from its own training; recovery at a fixed false-verbs-per-sentence budget; modern to 19c transfer; twin); the live hook in `hdlab/situation_reader.py`, the `_rescue` branch near line 1944 (`if hasattr(ft, "_perc")` takes the perceptron path; otherwise the 2026-09-13 stand-in: `post[i]["VERB"] >= PREDICATE_RESCUE_MIN_P` (0.3) for tokens with a WordNet verb reading -- NO other cue); the category organ `hdlab/lexical_categories.py` (`tag_with_posterior`; the count model's EMISSION counts word-given-category and its forward-backward posterior; `observe`).
> 3. **GENERALIZE.** The cue must serve every register the detector was built for (modern UD-EWT + QA-SRL; the 19c transfer population is INFORMATIONAL only under the 19c ban) and every consumer of `sm.events` (roles, coref salience, causal, timeline all read the event set).
> 4. **WALL -> DEEPER.** If the refit detector still misses the witness sentence ("the lake presents an unbroken sheet of ice": the category organ reads DET ADJ NOUN DET ADJ NOUN ADP NOUN, P(VERB given presents) = 0.022, the whole sentence verbless), ask whether the category organ's OWN decode should already have preferred a verb somewhere (a clause-level one-predicate expectation inside the forward-backward = an arm of the category organ) -- measure that form too; the loss may be upstream of the detector.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the cue's form (emission log-ratio vs posterior log-odds), the operating threshold, the argument window k; never adopt a number.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Measure on the LIVE chain (the category organ's tags, not the perceptron's): recovery of mis-tagged real verbs at the fixed false-verb budget on UD-EWT test (modern) and QA-SRL; end-to-end event recall through `SituationReader.read()` with the flag ON vs OFF (`predicate_recall=False`); the 7-dimension modern board no-regress (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set, about 25 min).
> 7. **ADJACENT.** The category organ's unseen-word cues (pri 99) and the entity-to-category prior (pri 104, running) change P(VERB) for exactly these tokens; report the interaction, do not duplicate them.
> 8. **COMPLETION BAR.** The rescue FIRES on the live chain: recovery of mis-tagged real verbs CI-separated above (a) the dormant stand-in (threshold read) and (b) an information-free twin (random promotion at the matched rate), at a false-verbs-per-sentence budget no worse than the perceptron-era detector's; end-to-end event recall through the reader up with the flag ON vs OFF on modern gold; board not down; knowledge as counts with an observe path; `verification/test_predicate_recall_landing_organ.py` green under the live tagger -- OR a numbered located negative naming which upstream quantity (the category organ's emission, its decode) blocks it.

**(PHASE DIAGRAM.)** The cue form, the threshold, the window and any prior weight are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (count organ, in order, graded posterior; BF) -> THIS decision -> events -> every downstream organ. Trace exactly what the category organ hands down for the 'presents' class of tokens (emission vs transition share) and write it in the signal-loss trace.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the word-kind organ calls a real verb a noun ("the lake PRESENTS an unbroken sheet of ice"), the whole clause disappears -- no event, no who-did-what, nothing for the later organs to read. A small rescue organ was built to catch these (it looked at how verb-like the word is, whether the sentence has any verb at all, whether things stand before and after it like arguments, and its ending), and it paid about 6.7 points on the old event board. Since the word-kind organ became the brain-style one (12 Sep), the rescue has been silent: its "how verb-like" clue was read straight off the OLD statistical tagger's internal numbers, and the quick replacement reads a single probability that is far too small on exactly these words. Nothing downstream knows the rescue stopped working, because the test that guarded it was written against the old tagger.

## 2. WHY THIS ONE
A landed, measured organ is DORMANT on the live path (landed is not live), board-invisible, at the top of the chain (every downstream read depends on the event set), and the fix is bounded: one cue re-derived from the brain-foundational organ that replaced its source, then the combiner re-learned from the organ's own errors.

## 3. MEASURED vs INFERRED
MEASURED (2026-09-14 00:40, strategy): live tags for the witness sentence = DET ADJ NOUN DET ADJ NOUN ADP NOUN; P(VERB given presents) = 0.022, P(VERB given lake) = 0.021 (threshold 0.3, nothing rescued); "the old man fishes the river at dawn": fishes NOUN with P(VERB) = 0.316 (rescued by luck of the threshold), dawn 0.103. The perceptron-era detector rescued 'presents' at p at or above its threshold (witness check 1). INFERRED: the size of the live loss on modern prose -- the builder's populations will give it; measure first.

## 4. ALREADY TRIED / DO NOT REDO
The bare posterior threshold (the 2026-09-13 stand-in) -- it is what is dormant. A hard heuristic override (3.72 false verbs per sentence) and the single-cue noisy-channel rule (0.16 recovery at 0.46 FP on modern) were refuted in the parent problem -- the COMBINATION of cues is the mechanism.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `hdlab/predicate_detector.py`; `hdlab/situation_reader.py` lines 1925-1970 (the `_rescue` branch); `experiments/exp_register_predicate_detector_v1.py`; `hdlab/lexical_categories.py` (`tag_with_posterior`, the emission model, `observe`); `verification/test_predicate_recall_landing_organ.py`; `notes/problems/register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb/SOLVED.md` (the parent). Run the witness once to see the current state.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the dormant stand-in (live, as is) and predicate_recall OFF. Controls: the information-free twin (random promotion at the matched rate), paired bootstrap over sentences; the false-verb budget reported at the operating point, not tuned per population.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_predicate_rescue_bf_cue_v1.py` (your cell; use `get_output_dir`), `notes/problems/<slug>/{SOLVED.md, predicate_detector_bf_patch.diff}` (a unified diff against `hdlab/predicate_detector.py` and/or the `_rescue` branch of `hdlab/situation_reader.py`), and a NEW asset under `data/hook_state/` (strategy swaps it into `data/frontend_assets/` on integration). Never edit hdlab/ or tools/ directly.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. The 19c (LitBank) transfer number is informational only (owner ban on 19c as a requirement).
