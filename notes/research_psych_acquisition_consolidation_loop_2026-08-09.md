# Research drill: the psychology of incremental meaning-acquisition + sleep consolidation, mapped to a closed self-growing grounding loop (2026-08-09)

Director+USER task: "there must be a lot of research on this in human psychology" -- ground the
CLS-style loop the USER proposed (flag comprehension failures -> not-yet-grounded library ->
periodic sleep-style consolidation -> bank grounded meaning -> grow grounding over exposure) in the
acquisition/consolidation literature, then design the closed loop concretely. Method: 3 parallel
Sonnet lit-scan sub-agents (WebSearch, generic math/psych terms only, no substrate-novel names off
platform) + disk-verified read of this project's own prior FORMALIZE drills, which turn out to have
already done half of this mapping independently (`notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`,
`notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md`,
`notes/formalize_word_acquisition_increment1b_result_class_congruence_2026-08-06.md`) plus the
actual measured outcomes of BOTH halves as built (registry rows, metrics.json), which the notes-only
re-read would have missed.

## HEADLINE

We already own every organ this loop needs, on BOTH halves, and we have ALREADY BUILT AND MEASURED
first attempts at both halves independently -- but never wired them together, and each independent
attempt hit a DIAGNOSED, FIXABLE failure mode rather than a ceiling. (1) The "flag + propose +
verify" half (`hdlab/word_acquisition_loop.py`, increment 1) is SHELVED (measured HARD_FAIL,
`grounded_word_acquisition_loop_increment1` registry row) for a diagnosed, structural, NOT
capability reason: a strict two-channel AND-gate eroded an informative channel by pairing it with an
at-chance one, and a wiring gap silently excluded acquired words from the scoring-time candidate
list -- both already have a designed fix (`1b` re-spec, un-run). (2) The "periodic sleep
consolidation" half (`experiments/exp_unified_self_learning_loop_v6_replay_consolidation.py`) has
only a SMOKE run on record, and that smoke shows `new_acquisition=0.0` across EVERY arm including
the naive baseline at n=6 total items -- a flat-everywhere result at toy scale is the project's own
named red flag for a broken/underpowered harness, not a validated negative on replay (see MEMORY
"flat learning result = broken experiment, not a ceiling"); it has never been re-run at real
scale/density. **Neither half has an honest negative result on record for the actual mechanism
question.** The lit-scan below supplies the piece genuinely missing from both prior drills: the
HUMAN behavioral evidence that sleep-gated integration of specifically NEW WORDS is a real,
replicated phenomenon (Dumay & Gaskell 2007; Tamminen et al. 2010) distinct from the rodent
hippocampal-replay literature the 07-28 audit already covered, plus the honest finding that
schema-acceleration is a DOUBLE-EDGED mechanism (the same circuit that fast-tracks true learning
also manufactures false memories, Warren et al. 2014) -- which directly overturns one design choice
already made in the un-run v6 spec (forced-commit-after-patience) and is folded into the design below
as a correction, not a footnote.

## 1. Psych literature, mapped to owned organs (SHAPE + POSITION + METRIC per standing discipline)

### 1a. Fast mapping + cross-situational statistical word learning (already drilled 2026-08-06, not
re-run here -- summarized because it is load-bearing for the closed loop's PROPOSE stage)

| Mechanism | Brain SHAPE+POSITION+METRIC | Owned organ | Status |
|---|---|---|---|
| Fast mapping: one exposure -> weak, graded, revisable placeholder, not a firm binding (Carey & Bartlett 1978; Carey 2011) | one-shot partial-category tag, ~0.64 mean p(correct) after 1 exposure (Alishahi/Fazly/Stevenson 2008) | `hdlab/predictive_coding.py::threshold_gate` (propose trigger) + `mint_signature`-style placeholder mint (`exp_self_extension_loop_v1`) | REUSE verbatim (propose skeleton) |
| Syntactic bootstrapping: construction, not scene/word identity, narrows the hypothesis space (Gleitman 1990; Yuan & Fisher 2009: mere overhearing seeds a durable next-day entry) | argument-structure cue -> frame classifier | `hdlab/frame_induction.py::frame_primary_role`, `hdlab/goal_typing.py::action_frame_feats` | REUSE pattern (MDL-induced construction classifier, verb-lemma-blind); measured AT-CHANCE for outcome-verb POLARITY specifically (4/7, majority-class artifact) -- literature already predicted this leg would be weak for evaluative valence, confirmed |
| Cross-situational propose-but-verify: single best-guess hypothesis, retained only if the NEXT exposure of the same word confirms it (Trueswell/Medina/Hafri/Gleitman 2013); converges within ~2-3 confirmatory exposures (Yu & Smith 2007; Smith & Yu 2008) | eye-tracking-measured hypothesis-retention across trials | `exp_self_extension_loop_v1::run_loop` CONSOLIDATE stage, `MIN_CONFIRM=2` signature-match + `hdlab/self_improving_loop.py::decide_keep_or_revert` abstain-band | REUSE verbatim -- clean, already-validated instance |
| Affective grounding of evaluative words: valence/arousal dimension, not sensorimotor stats, dominates for abstract/social-evaluative words; valenced words acquired faster under age 8-9 (Kousta et al. 2011; Ponari et al. 2018) | dopaminergic reward-prediction-error as a "common neural currency" (Schultz/Dayan/Montague 1997; Lisman & Grace 2005 hippocampal-VTA loop) | `experiments/exp_grounded_appraisal_sim_earned_v1.py` reward-trained theta -> `hdlab/context_grounded_valence.py::score_item` | REUSE machinery; DISK-CONFIRMED (1b drill) this project's own attempt to wire it to the polarity axis collapsed to a fixed 2-value sign lookup -- an honest, informative finding that reward-PE grounding was aimed at the wrong CONSUMER for this specific axis, not that the mechanism is wrong in general |

### 1b. Sleep-dependent lexical/semantic consolidation (NEW this drill -- the human behavioral
literature the prior 07-28 audit did not cover, which focused on rodent hippocampal replay)

| Finding | Citation | Established? | Owned organ / gap |
|---|---|---|---|
| Active systems consolidation: hippocampal-neocortical dialogue during SWS, SWR-driven replay progressively redistributes traces to cortex; REM does complementary synaptic-level stabilization | Diekelmann & Born 2010, *Nat Rev Neurosci* 11:114-126 | ESTABLISHED, field consensus | `hdlab/hippocampal_encoder.py::cls_discrete_budget_consolidate` (DG->CA3->slow-store, SWR partial-cue, discrete offline budget) -- certified HARD_PASS on its own synthetic regime (gap=0.913 vs naive, `data/exp_cls_ca3complete_consolidation_v1/metrics.json`) |
| **NEW word integration into the lexicon specifically requires sleep, not just elapsed time**: novel wordforms show lexical-competition effects with existing neighbors only after a night's sleep, decoupled from time-since-learning (evening-learned words show the effect after 12h+sleep but not 12h wake) | Dumay & Gaskell 2007, *Psych Sci* 18(1):35-39 | ESTABLISHED, foundational, replicated | This is the DIRECT human analogue of "grow grounding over exposure + sleep pass" -- the design implication: a flagged item should NOT be eligible for lexicon write-back on the SAME pass it was proposed, even if corroborated, because the brain's own analogous mechanism requires an intervening offline phase, not just repetition count |
| Sleep-SPINDLE density during that night predicts the MAGNITUDE of lexical integration (individual-differences link, not just group effect) | Tamminen, Payne, Stickgold, Wamsley & Gaskell 2010, *J Neurosci* 30(43):14356-14360 | ESTABLISHED core effect; spindle-mechanism link itself more CONTESTED (later semantic-priming follow-ups, e.g. Tamminen & Gaskell 2013 QJEP, give mixed results) | Motivates making replay BUDGET (analogous to spindle density) a tunable dial per consolidation pass, not a fixed constant -- an item with more replay-budget-share integrates faster, testable directly against `cls_discrete_budget_consolidate`'s existing `budget` parameter |
| Selective replay: item-level tagging (arbitrary sound cues), context-level tagging (odor), and salience/reward tagging all independently boost SPECIFIC items' consolidation over untagged items (targeted memory reactivation, TMR) | Rasch/Buchel/Gais/Born 2007, *Science* 315:1426-9 (odor cueing); Rudoy/Voss/Westerberg/Paller 2009, *Science* 326:1079 (sound cueing); Payne & Kensinger 2010 *Curr Dir Psych Sci* + 2018 (emotional salience) | ESTABLISHED (TMR); salience-weighting mechanism details CONTESTED | `experiments/exp_cls_prioritized_replay_closed_loop_surprise_v1` already tested surprise-tagged replay in isolation (landed MIDDLE_BAND, weak lever delta_E=0.055, synthetic data) -- the v6 spec's SURPRISE-ORDERING of the replay budget is the correct organ for this, already designed, never validated at real scale |
| Sleep can produce FALSE / gist-based memories preferentially -- schema-consistent distortion, not pure strengthening | Payne et al. 2009, *Neurobiol Learn Mem* 92(3) (DRM, sleep preserves false memories over true-item detail); Diekelmann et al. 2008/2010 mixed on direction, direction depends on paradigm/individual differences (CONTESTED at the mechanistic level, robust at the "gist over verbatim" level) | Robust theme, CONTESTED specifics | **This is the missing false-consolidation-guard citation** -- see section 2 below, this directly critiques the un-run v6 design's forced-commit-after-patience choice |

### 1c. Schema-accelerated consolidation + the false-consolidation double-edge (NEW this drill,
extends the 07-28 audit's Tse-et-al citation with the mechanism AND its risk)

| Finding | Citation | Established? | Owned organ / gap |
|---|---|---|---|
| A well-established schema lets NEW, CONSISTENT information become hippocampus-independent within ~1 trial / 48h, vs. weeks for inconsistent info (rodent PRE paradigm) | Tse/Langston/Kaag/Morris et al. 2007, *Science* 316:76-82; mechanism (mPFC immediate-early-gene activation) in Tse et al. 2011, *Science* 333:891-5 | ESTABLISHED (foundational, rodent) | This project's own foundation-graph (1.24M-edge) IS the schema; the 07-28 audit's design #2 (schema-consistency gate before slow-store capture) already targets this correctly |
| SLIMM model: active mPFC schema representations gate MTL/hippocampal encoding -- congruent input fast-tracked (mPFC-hippocampal cooperation, minimal hippocampal binding); incongruent input triggers a prediction-error/mismatch signal recruiting FULL hippocampal episodic encoding | van Kesteren, Ruiter, Fernandez, Henson 2012, *Trends in Neurosciences* 35(4):211-219 (note: TiNS, not TiCS -- corrected citation) | ESTABLISHED review/framework | Confirms the audit's schema-gate design SHAPE (a binary fast-track-vs-full-encoding branch keyed on a mismatch/consistency signal); the METRIC should be a genuine prediction-error/mismatch score, not merely "did N occurrences agree with each other" (see 1b redesign's Risk finding: internal-agreement != schema-fit) |
| Cortical learning rate is prior-knowledge-dependent, not fixed-slow: schema-consistent items can update cortex fast WITHOUT catastrophic interference because existing structure constrains where the update lands | McClelland 2013, *JEP:General* 142(4):1190-1210 | ESTABLISHED theoretical synthesis | Licenses the loop's fast-track branch as brain-consistent, not corner-cutting (already cited by the 08-06 drill) |
| **Schema-congruent false memories are MORE likely, not less** (DRM paradigm: ~40-55% false recall of a non-presented gist word); vmPFC-lesion patients show REDUCED false recall, implicating the SAME schema-integration circuit that accelerates true learning as the source of false learning -- a genuine double-edged mechanism, not two separate circuits | Bartlett 1932 (classic, "War of the Ghosts"); Roediger & McDermott 1995, *JEP:LMC* 21(4):803-14 (DRM, heavily replicated); Warren/Jones/Duff/Tranel 2014, *J Neurosci* 34(22):7677-82 (vmPFC lesion, single-study/small-N, CONTESTED generality) | Robust at the phenomenon level; single-lesion-study for the "same circuit" claim | **This is the corrective finding.** No literature evidence was found for a discrete "N independent confirmations = safe" rule as a general safeguard -- that idea is this project's own engineering inference, not an established finding. The literature's actual proposed safeguard is DIFFERENTIAL: hippocampal mismatch/novelty detection must be tested to ACTUALLY discriminate real-context from wrong-context input (a 2025 PNAS finding suggests mismatch signals track *episodic*, not generic-schematic, predictions specifically, complicating a simple gate) -- i.e., the guard must be VALIDATED to differ on a real-vs-wrong-context probe, not merely assumed to exist because a schema-check function was written. Directly motivates the adversarial wrong-context self-test in the design below (section 3), which the 07-28 audit had already independently proposed for a different reason (SCRAMBLED-text controls) -- the two lines of reasoning converge on the same required self-test. |
| CLS reconciliation for artificial agents: two systems (hippocampal instance-store + interleaved-replay cortical learner), structure-discovery graded/prior-dependent, replay is what prevents catastrophic interference while still permitting fast integration of consistent facts | Kumaran, Hassabis, McClelland 2016, *TiCS* 20(7):512-534 | ESTABLISHED, influential AI-neuroscience bridge (DeepMind co-authored) | Direct blueprint validation for this project's overall two-tier (fast propose-library / slow consolidated-store) architecture |

### 1d. Formulaic/idiomatic conventionalization + curiosity/novelty gating (NEW this drill)

| Finding | Citation | Established? | Owned organ / gap |
|---|---|---|---|
| Repeated co-occurrence drives "chunking" -- a sequence stored/retrieved as ONE unit once frequency crosses a GRADED (not discrete-threshold) entrenchment level | Bybee 2006, *Language* 82(4):711-33; N. Ellis 2002, *SSLA* 24:143-88 | ESTABLISHED | `hdlab/consequence_learning_loop.py`'s `GROUNDED_NEUTRAL` outcome for light verbs (be/go/make/give co-occur with both met/unmet, wash out rather than force a polarity) is structurally the SAME phenomenon -- a construction with STABLE-but-flat outcome-association conventionalizes to neutral. Confirms this design choice is brain-consistent, not an ad hoc carve-out. |
| Holistic-storage default for formulaic sequences ("Needs Only Analysis") | Wray 2002, *Formulaic Language and the Lexicon*, CUP | ESTABLISHED framework (~7000 citations) | Same organ as above |
| NO discrete repetition threshold exists in the literature -- entrenchment is graded/log-frequency-weighted across the ENTIRE frequency spectrum, not a step function | Arnon & Snider 2010, *JML* 62:67-82; Bannard & Matthews 2008, *Psych Sci* 19(3):241-8 | ESTABLISHED (the ABSENCE of a hard threshold is itself the consensus finding) | **Direct, falsifiable design implication**: `MIN_CONFIRM=2` (a hard integer threshold, reused verbatim from `exp_self_extension_loop_v1` across every acquisition attempt to date) is a coarse ENGINEERING proxy for a graded phenomenon the literature says is NOT actually threshold-shaped. Flagged as a candidate refinement (accumulate a running log-count-weighted confidence score instead of a hard >=2 gate) -- NOT required for the first closed-loop increment (keep MIN_CONFIRM=2 as the cheap baseline), but pre-registered as the next lever if growth rate is too slow/fast at the boundary. |
| Infants preferentially attend to intermediate-complexity/moderate-surprisal stimuli (inverted-U over surprisal, avoiding both fully predictable and fully unpredictable) | Kidd, Piantadosi & Aslin 2012, *PLOS ONE* 7(5):e36399 | ESTABLISHED-leaning (single original study, cross-modally replicated) | `hdlab/predictive_coding.py`'s threshold/proportional gates are currently MONOTONIC in residual magnitude (more novel = more write). The Goldilocks finding suggests a genuine refinement: an item with residual so large it looks like NOISE/GARBLE (not a structured novel pattern) should get LESS encoding priority than a moderately-novel structured item, not more. Flagged as a real, literature-supported, NOT-YET-IMPLEMENTED refinement to the propose-gate -- distinguishing "genuinely learnable new content" from "unparseable noise" is exactly the discriminator a real DesireDB stream needs (vs. the toy corpora prior arms tested on) since real prose contains both. |
| Novelty/prediction-error gates hippocampal encoding STRENGTH via a closed hippocampal-VTA dopaminergic loop | Lisman & Grace 2005, *Neuron* 46(5):703-13 | Broad claim ESTABLISHED; precise circuit CONTESTED/refined (Takeuchi et al. 2016 *Nature*, locus-coeruleus alternative pathway) | Already the justification for `predictive_coding.py`'s existence; reconfirmed, no change |
| Curiosity as intrinsically-motivated active information-sampling, prediction-error as the currency | Gottlieb & Oudeyer 2018, *Nat Rev Neurosci* 19(12):758-70 | ESTABLISHED integrative review; specific "learning-progress" formalization CONTESTED | General framing support, no new organ implication beyond the above |

## 2. Prior-art reckoning: what we already tried, and why each stopped short of a ceiling

**Encoding/propose-verify half (`hdlab/word_acquisition_loop.py`, increment 1 -> 1b re-spec).**
Registry: `grounded_word_acquisition_loop_increment1`, `gate_decision: SHELVE`, `status:
built_measured_HARD_FAIL_shelved_2026-08-06`. Disk-verified diagnosis (`formalize_word_acquisition_increment1b...md`):
(a) the strict two-channel AND-gate (`combine_votes`) is mathematically incapable of exceeding the
WEAKER channel's own recall, and one channel (construction-cue MDL classifier) measured at-chance
(4/7) -- pairing it with the real signal (2/7 alone) under strict AND can only preserve-or-erode, and
did not help here only by luck of a 7-item sample; (b) a wiring gap means an acquired word's Tier-3
entry can never reach the 12-way scoring-time candidate list at all (silently returns `set()`,
falls through to NA) -- never even stress-tested by increment 1's own self-test, which checked a
materially EASIER flat 2-way fallback path instead. **Both are fixable, diagnosed, SHAPE-level
bugs, not evidence against the underlying propose/verify mechanism** -- Channel B's structural
situation-typer (`_cb_analyze_outcome_clause`) DOES carry some real signal per increment 1's own
measurement ("recovers transitive-achievement POS verbs (earn, gain)"). The 1b re-spec (single-channel,
drop the AND-gate, fix the candidate-list wiring gap) is fully designed and pre-registered but has
never been run.

**Consolidation/replay half (`experiments/exp_unified_self_learning_loop_v6_replay_consolidation.py`).**
Registry: `cls_discrete_budget_consolidate_v6_replay`, `gate_decision: VET_PENDING`, `status:
primitive_hard_pass_synthetic_n3; v6_wiring_hard_fail_vet_pending`. Only a SMOKE run is on disk
(`data/exp_unified_self_learning_loop_v6_replay_consolidation_smoke/metrics.json`):
`REPLAY_SCHEMA_GATED old=0.1667 new=0.0`, `AVERAGING_NAIVE old=0.1667` (new_acquisition not even
computed for the naive arm at this scale), verdict `HARD_FAIL: "replay no better than averaging-family
proxy"` at n_old=6, n_new=6, budget=6. **`new_acquisition=0.0` for every single arm including
uninstrumented ones, at n=6 total items, is the project's own named red flag** (MEMORY: "a flat/null
result in a learning/curriculum experiment means diagnose -- not-actually-learning /
no-genuinely-new-content / underpowered -- never conclude intrinsic ceiling from flat"). This smoke
was never followed by the FULL run or a harness audit; the registry's own `gate_decision_target`
literally says "if it fails [FULL], SHELVE... needs stronger base encoder + real-data test" -- i.e.
the project's own prior judgment already flagged this as needing a real-data re-test before any
conclusion, and that re-test never happened.

**Net: no valid negative exists on either mechanism.** Both are un-cleared, diagnosed-fixable,
sitting exactly where the USER's proposed loop would pick them back up -- this drill's job is to
specify the UNIFIED next attempt, not re-litigate either half in isolation.

## 3. The closed-loop design

The USER's proposed shape (flag -> library -> periodic consolidation -> bank -> grow) maps onto a
SINGLE loop that reuses the encoding-half's propose/verify skeleton as the library's INTAKE and the
consolidation-half's discrete-budget-replay primitive as the library's PERIODIC SWEEP -- these were
built as two separate lines of work; this design is their first wiring.

**(a) TRIGGER -- what creates a library entry.**
Reuse `hdlab/predictive_coding.py::threshold_gate` (residual-magnitude novelty gate) at the point a
comprehension pass (goal-outcome linking, `hdlab/goal_typing.py::congruence_decision`) returns NA
because a construction/word is unrecognized -- this IS the flag. Per the Goldilocks finding (1d),
add ONE new discriminator not yet built: a coarse learnability filter (residual magnitude in a
MODERATE band, not the extreme tail) so garbled/unparseable spans are excluded from the library
rather than treated as maximally-novel-therefore-maximally-prioritized. Each flagged item mints a
placeholder entry (reuse `mint_signature`'s pattern) with status `PENDING`, payload = the minimal
construction context (clause, referent-link candidates, any partial channel votes so far) -- NOT yet
a committed polarity/meaning.

**(b) LIBRARY -- the not-yet-grounded store.**
A small persistent structure (new, thin -- mirrors `consequence_learning_loop.py`'s existing
PENDING/GROUNDED_POS/GROUNDED_NEG/GROUNDED_NEUTRAL status model, reused verbatim, extended with
`ESCALATED`): keyed by (lemma-or-construction-signature), value = accumulated occurrence traces
(one per independent episode, per Trueswell propose-verify -- NOT folded/averaged at intake, kept
as separate traces exactly as the 07-28 audit's core finding demands), each trace carrying its own
channel vote(s) and episode identity (for the independence check).

**(c) PERIODIC CONSOLIDATION PASS ("sleep") -- what it computes.**
Runs on a cadence separate from reading (offline, matching Diekelmann & Born's core distinction).
For each library item with >= `MIN_CONFIRM=2` independent-episode traces (Trueswell/Yu&Smith
convergence number, already the codebase default):
1. Call `hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` with `replay_keys` = the item's
   accumulated traces, ORDERED by surprise = disagreement with the item's current best-guess vote
   (highest-disagreement traces replayed first, per Tamminen/Rasch selective-replay + the
   already-designed v6 surprise leg) and a small fixed BUDGET (start at B=3-5, matching the
   certified cell's own validated regime).
2. CA3-complete each replayed trace against the FROZEN, train-side foundation-graph / CLASS_REGISTRY
   codebook (leak-proof, same discipline every prior arm enforces).
3. SCHEMA-CONSISTENCY gate (van Kesteren/Tse mechanism): compare the completed vote against the
   item's local construction-context's typed-relation neighborhood in the foundation graph. If
   consistent -> eligible for capture this pass (fast-track, per McClelland 2013). If inconsistent
   -> increment a patience counter, defer.
4. Capture into the "banked" slow store (`ACQUIRED_*` Tier-3 overlay, reused verbatim, strict-ADD)
   ONLY if: (i) schema-consistent this pass, AND (ii) this is NOT the same pass the item first
   reached MIN_CONFIRM (an explicit intervening-pass requirement, directly modeling Dumay & Gaskell's
   sleep-not-just-time finding -- an item cannot integrate on the very pass it becomes eligible, it
   must survive to the NEXT pass).

**(d) FALSE-CONSOLIDATION GUARD (the corrected piece -- this is where this drill changes the un-run
v6 design, not just confirms it).**
The 07-28 audit already proposed a SCRAMBLED-text matched control as a self-test; the 1b re-spec
already learned that internal multi-channel agreement is NOT the same signal as external schema-fit;
this drill's lit-scan (Warren et al. 2014, Bartlett, DRM) adds the missing piece: schema-consistency
gating is DOUBLE-EDGED, not automatically safe, so it must be VALIDATED to discriminate, every
consolidation pass, not assumed to. Concretely: at every consolidation pass, run the SAME
schema-consistency check on a matched ADVERSARIAL WRONG-CONTEXT probe -- take a real flagged item's
trace and re-score it against a DIFFERENT, unrelated construction-context's typed-relation
neighborhood (the negative-control discipline v4/v5/v6 cells already use for SCRAMBLED text,
generalized to "wrong schema neighborhood" rather than "scrambled word order"). The guard is
considered FUNCTIONING only if wrong-context schema-consistency scores are reliably LOWER than
real-context scores (pre-registered margin below). **Correction to the un-run v6 spec:** v6's design
included a "PATIENCE_MAX forced-commit" (commit anyway after N consecutive schema-check failures,
to avoid permanent starvation) -- per this drill's false-memory finding, forced-commit-after-repeated-
failure is precisely the failure mode that manufactures schema-consistent false memories (the
schema-check kept saying "no" and got overridden anyway). This design REPLACES forced-commit with
escalation (below) -- an item that cannot clear the schema gate does not get force-banked under any
patience budget.

**(e) ESCALATION PATH -- items that never ground.**
An item that accumulates traces across `PATIENCE_MAX` (start at 3, matching the smallest tested
budget) consolidation passes without clearing the schema-consistency gate moves to a terminal
`ESCALATED` status -- logged with its full trace history, NEVER auto-written to the production
overlay. Per the project's existing error-routing discipline (missing-PRIMITIVE vs missing-FACT vs
missing-LEARNING), an escalated item is a candidate for: (i) a different acquisition channel
entirely (e.g. a word repeatedly failing schema-fit at the lexical level might ground at the
relation/construction level instead -- route, don't retry the same channel indefinitely), or (ii)
director/human review if it recurs often enough to matter for coverage.

## 4. Cheap decisive test (pre-registered here; not yet built/dispatched)

Run the unified loop over a REAL DesireDB stream slice (not the toy 6-item smoke that produced v6's
flat result) -- reuse `experiments/data/goal_bearing_modern_eval_v1.jsonl` or the live DesireDB
corpus already used for the goal-outcome comprehension work, sliced into >= 5 sequential
"exposure batches" to give the periodic-pass structure something real to operate over. Measure,
across K=5 consolidation passes:
1. **GROWTH** -- count of items reaching `GROUNDED_*` status, pass over pass, with ZERO regression
   of any already-grounded item (matching `cls_discrete_budget_consolidate`'s own certified
   no-forgetting bar, gap vs a no-consolidation control).
2. **FALSE-CONSOLIDATION RESISTANCE** -- adversarial wrong-context probe capture rate vs matched
   real-context capture rate, and the schema-consistency SCORE margin between them.
3. **ESCALATION SANITY** -- inject a small set of TRUE-nonsense negative-control tokens (garbled,
   no genuine construction, matching the Goldilocks "unparseable" category from 1d); these must
   reach `ESCALATED`, never `GROUNDED`.

## 5. Falsifiable predictions

**HARD-PASS** (all three required):
- Growth: >= 3 genuinely novel words/constructions reach `GROUNDED_*` across the K=5-pass real
  DesireDB slice, zero regression of prior-grounded items.
- Guard: wrong-context adversarial-probe capture rate <= 20% of matched real-context capture rate,
  OR schema-consistency score margin (real minus wrong-context) >= 0.15 cosine (same
  coherent-vs-scrambled discriminant-validity bar the 07-28 audit's own DEFLATE-null clause already
  specifies).
- Escalation: 100% of injected true-nonsense negative controls reach `ESCALATED`, none reach
  `GROUNDED_*`.

**HARD-FAIL** (any one triggers, but see the mandatory pre-check below):
- Zero growth after K=5 passes on a real (>= 20 flagged-item) slice -- **mandatory pre-check before
  accepting this as a negative**: verify per-item trace counts are non-trivial (>= MIN_CONFIRM
  achievable given the batch structure) and that the schema-consistency scorer fires differently on
  a synthetic coherent-vs-scrambled pair FIRST (the same self-test both prior notes already
  pre-registered) -- a flat result without this check passing is diagnosed as a harness/data-density
  bug per the standing discipline, not reported as a capability ceiling.
- Wrong-context probe capture rate >= real-context capture rate (guard provides no discrimination --
  replicates the audit's own pre-registered DEFLATE-null condition).
- Any injected true-nonsense item reaches `GROUNDED_*` (guard fails on its one hard invariant).

## 6. Cross-thread synthesis

Extends `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md` (rodent
hippocampal-replay mechanism, schema-gate design #2, surprise-order design #3) with the human
behavioral sleep-word-learning literature that note did not cover, and CORRECTS its
forced-commit-after-patience choice (section 3d above) using new lit-scan evidence
(Warren et al. 2014) that was not available/considered at that drill. Extends
`notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md` and
`notes/formalize_word_acquisition_increment1b_result_class_congruence_2026-08-06.md` (the propose/
verify skeleton, the AND-gate design lesson, the Tier-3 candidate-list wiring gap) by supplying the
missing PERIODIC/OFFLINE half those drills explicitly deferred ("does not persist across process
restarts," "in-memory-only"). This is the first drill to name BOTH halves' actual measured status
(SHELVE / VET_PENDING, both from disk, not from labels) in one place and propose the wiring between
them, rather than treating them as two independent lines of work.

## 7. Substrate-product implications

If the closed loop clears its bands, the substrate's comprehension coverage on real narrative prose
stops being a function of how many hours a human spends hand-curating lexicon/construction entries,
and starts being a property of how much text it has read PLUS how many offline consolidation passes
it has run -- with a fully inspectable provenance trail per item (which traces corroborated it, which
consolidation pass captured it, whether it ever cleared the schema gate) rather than a black-box
embedding update. This is the mechanism that would let the substrate's grounding GROW unattended
between sessions (the "sleep" framing is not decorative -- it is the literal design requirement that
integration happens on a SEPARATE offline pass, not synchronously with reading), which is the
capability this project's current wall (OOV outcome-verb coverage gating goal-outcome comprehension)
most directly needs.

## 8. Anchor candidates for exp_dev (ranked; folded into this deliverable per no-routing-files
discipline -- no separate hand-off file)

1. **Highest priority, cheapest**: run the ALREADY-DESIGNED, un-run `1b` re-spec
   (`preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`) as-is first -- it fixes two
   diagnosed bugs in the encoding half with zero new mechanism risk, and its result (does the
   single-channel structural typer clear its own pre-registered band once the candidate-list wiring
   gap is fixed) is a precondition for trusting anything the unified loop reports about the PROPOSE
   side.
2. **Second**: re-run `exp_unified_self_learning_loop_v6_replay_consolidation` at REAL scale/density
   (not the n=6 smoke) with the harness self-test check (coherent-vs-scrambled schema-consistency
   discriminant) added FIRST, per the HARD-FAIL pre-check in section 5 -- this resolves whether the
   smoke's flat result was a harness bug or a real signal before any further design work depends on
   it.
3. **Third, the actual unification**: once (1) and (2) each independently clear or produce an
   honest, pre-check-passed negative, build the wiring in section 3 (library data structure +
   periodic sweep calling both organs) and run the cheap decisive test (section 4) on a real
   DesireDB slice. Do not attempt this before (1)/(2) resolve -- compounding two unvalidated
   primitives would make any negative uninterpretable (can't tell which half broke it), the same
   confound risk the 07-28 audit already flagged for its own design.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

Novel synthesis (no published precedent unifies fast-mapping propose-verify + CLS discrete-budget
replay + schema-gating + an explicit adversarial false-consolidation guard into one glass-box
symbolic pipeline). P(the unified loop, once both halves are independently re-validated per anchors
1-2, clears its section-5 HARD-PASS bands on a real DesireDB slice) is capped at 0.50 and further
deflated to **~0.30**, reflecting: (a) positive -- both halves' prior failures are diagnosed as
fixable SHAPE bugs, not capability ceilings, and the fixes are already designed; (b) negative --
compounding two not-yet-independently-cleared primitives, plus genuine novel-synthesis risk in the
guard mechanism itself (no literature precedent validates "adversarial wrong-context re-scoring" as
a real anti-false-memory mechanism, only that the underlying risk it targets is real). A clean,
pre-check-passed negative on either anchor 1 or 2 would be genuinely informative (would show which
literature-predicted mechanism -- propose-verify or replay-consolidation -- fails to transfer to this
substrate), not merely an implementation miss.

## Citations (verified count = 3 parallel Sonnet lit-scans, ~30 distinct NEW citations this drill,
plus ~20 citations carried forward from the two 2026-08-06/07-28 internal drills cited above)

**New this drill:** Diekelmann & Born 2010 *Nat Rev Neurosci* 11; Dumay & Gaskell 2007 *Psych Sci*
18(1); Tamminen/Payne/Stickgold/Wamsley/Gaskell 2010 *J Neurosci* 30(43); Tamminen & Gaskell 2013
*QJEP* 66(5); Rasch/Buchel/Gais/Born 2007 *Science* 315; Rudoy/Voss/Westerberg/Paller 2009 *Science*
326; Payne & Kensinger 2010 *Curr Dir Psych Sci* + 2018 *Neurobiology of Stress*; Payne et al. 2009
*Neurobiol Learn Mem* 92(3); Diekelmann et al. 2008/2010 (sleep + DRM false memory); Tse/Langston/
Kaag/Morris et al. 2007 *Science* 316; Tse et al. 2011 *Science* 333; van Kesteren/Ruiter/Fernandez/
Henson 2012 *Trends in Neurosciences* 35(4); McClelland 2013 *JEP:General* 142(4); Bartlett 1932
*Remembering* (CUP); Roediger & McDermott 1995 *JEP:LMC* 21(4); Warren/Jones/Duff/Tranel 2014
*J Neurosci* 34(22); Kumaran/Hassabis/McClelland 2016 *TiCS* 20(7); Bybee 2006 *Language* 82(4);
N. Ellis 2002 *SSLA* 24; Wray 2002 *Formulaic Language and the Lexicon* (CUP); Arnon & Snider 2010
*JML* 62; Bannard & Matthews 2008 *Psych Sci* 19(3); Kidd/Piantadosi/Aslin 2012 *PLOS ONE* 7(5);
Gottlieb & Oudeyer 2018 *Nat Rev Neurosci* 19(12); Lisman & Grace 2005 *Neuron* 46(5); Takeuchi et
al. 2016 *Nature* (locus-coeruleus alternative pathway, cited as a complicating factor).

**Carried forward** (already verified in prior internal drills, not re-verified this session):
Carey & Bartlett 1978; Carey 2011; Alishahi/Fazly/Stevenson 2008; Gleitman 1990; Naigles 1990;
Yuan & Fisher 2009; Trueswell/Medina/Hafri/Gleitman 2013; Yu & Smith 2007; Smith & Yu 2008; Kousta
et al. 2011; Ponari et al. 2018; Schultz/Dayan/Montague 1997; McClelland/McNaughton/O'Reilly 1995;
Marr 1971; Frey & Morris 1997; Wilson & McNaughton 1994; Buzsaki 1989/2015; Foster & Wilson 2006;
Diba & Buzsaki 2007.
