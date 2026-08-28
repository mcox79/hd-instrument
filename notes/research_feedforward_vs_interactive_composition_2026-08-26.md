# Research: is a strictly-feedforward reading pipeline brain-faithful, or a modelling artifact? (adjudicating p1's composition design)

Filed by: research sub-agent, 2026-08-26. Directly targets the open, priority-1 problem
`notes/problems/wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end/PROBLEM.md` (p1,
"wire the validated organs into the live reader and measure end-to-end"). That brief's own §3 currently states
as **PINNED**: *"the brain reads as a PIPELINE of these operations composed, not in isolation... The COMPOSITION
(each stage feeds the next) is the brain's architecture."* This note is the adversarial check on that exact claim,
requested before p1 is run, because the brief's own §7 bar treats a front-end swamping result (event-extraction
recall ~0.32) as possibly "the single most valuable finding available right now" — and that verdict is only
trustworthy if the composition that produced it was itself brain-faithful.

Method: 4 parallel Sonnet lit-scan sub-agents (public psycholinguistics/cognitive-neuroscience literature, standard
academic search terms, no substrate-internal detail exposed off-platform), synthesized here. ~30 distinct
citations surfaced across the four scans (count below); none independently re-verified against primary sources by
me — standard lit-scan calibration, penalty applied per [[feedback-lit-scan-calibration-penalty]].

## HEADLINE

**Neither extreme is right, and three independent lit-scans now converge on the same fix.** The brain is not a
one-shot feedforward cascade (successful garden-path reanalysis requires literally re-visiting earlier
representations — a single forward pass cannot do that) — but it is also not full continuous backward-editing
recurrence either: Norris, McQueen & Cutler's Merge model (2000, *BBS*) proved that the classic "top-down lexical
knowledge changes perception" effects can be produced without any backward connections at all, by **late algebraic
combination of independently-forward-computed streams** (prior × likelihood, argmax at a decision point). That is
the SAME architectural conclusion reached independently by two prior threads on this substrate:
`notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` found word-sense selection is a two-term
argmax (frequency-prior + context-coherence), explicitly NOT a recurrent attractor settle, because ORGAN_MAP C4
already found attractor settling actively **hurts** this substrate's near-neighbor discrimination; and
`the_meaning_win_is_offline_context_free_and_unwired` (p6, integrated 2026-08-26) found context-conditioning does
NOT beat the frequency prior — a negative that is exactly what you'd predict if top-down correction is a narrow,
local rescue mechanism rather than a general-purpose override. **The brain-faithful fix for p1 is a bounded,
late-merge decision layer + occasional single-pass revision, not a recurrent loop** — and the substrate already
has the two organs (`n400_coherence_monitor`'s coherence score, `dg_ca3_recollection_gate`'s confidence-combining
pattern) needed to build it cheaply, without inventing new architecture.

**The single highest-leverage, lowest-cost move: before running p1's oracle-vs-live comparison, split the existing
~0.32 front-end errors into MISSES (nothing extracted) vs MISASSIGNMENTS (something extracted, but the wrong
role/entity among plausible alternatives).** This is a re-labelling pass on data already on disk — no new
experiment. It determines whether interactive correction is even mechanistically in scope, per Q3 below.

## Q1 — Feedforward or interactive/recurrent, with top-down feedback to lower stages?

**PINNED, word recognition:** apparent top-down/lexical effects on perception (Ganong 1980) are real and robust,
but Norris, McQueen & Cutler (2000, *Behavioral and Brain Sciences*) "Merge" model shows the SAME effects are
producible by two parallel *feedforward* streams (prelexical + lexical) combined only at a late decision stage —
**no literal backward connections required.** This is the single most important fact for p1: observed top-down
correction behavior does not, by itself, prove backward-editing architecture is needed.

**PINNED, garden-path parsing:** the field has moved from Frazier's serial syntax-first model (1987) toward
multiple-constraint / probabilistic accounts (MacDonald, Pearlmutter & Seidenberg 1994, *Psych Review*; Levy 2008,
*Cognition*, surprisal), but whether this reflects true architectural interactivity or a race among
independently-forward-computed candidates (Van Gompel, Pickering & Traxler's "unrestricted race" model) is
unresolved. **CONTESTED.**

**PINNED, garden-path reanalysis:** successful reanalysis (P600, Osterhout & Holcomb 1992) requires literally
re-visiting earlier input — documented via regressive eye movements (Frazier & Rayner) — which a bare one-shot
cascade structurally cannot do. But reanalysis frequently **fails** (see Q2/Q3) — "semantic P600" findings (Kim &
Osterhout 2005) show competition between a heuristic-semantic route and the syntactic route rather than a clean
autonomous-then-repair sequence. **CONTESTED** whether P600 is repair, continued monitoring, or both.

**PINNED, predictive coding:** Kuperberg & Jaeger (2016, *Language, Cognition & Neuroscience*) — N400 = lexical
prediction error, P600 = higher structural/integration error. Formally, predictive coding (Rao & Ballard 1999;
Friston) requires reciprocal message-passing by construction — but a feedforward architecture with **enough
forward context at each stage** can produce locally prediction-error-shaped output without literal backward
connections (the same Merge-model point, generalized). **CONTESTED**, and this is exactly the crux for p1.

**RECOMMENDATION:** p1 does not need to build biological recurrence. It needs (a) a late-merge decision layer that
combines forward-computed streams (front-end confidence × situation-model coherence), and (b) a *bounded* single
re-pass of the front-end when a large coherence violation is detected (mirrors reanalysis / regressive re-reading)
— not unbounded iteration. Both are cheap relative to true recurrence and are what the evidence actually supports.

## Q2 — Mechanism: does top-down context quantitatively RESCUE a noisy/degraded bottom-up signal?

**PINNED — yes, but the effect is LOCAL and bounded, not a blanket correction.** Gibson, Bergen & Piantadosi (2013,
*PNAS*) noisy-channel: implausible role-reversal sentences ("the mother gave the candle the daughter") are
answered as their plausible neighbor on **35-65% of trials** vs <5% for plausible controls — genuine
misperception, not just slower RTs. Levy, Bicknell, Slattery & Rayner (2009, *PNAS*) show regressions consistent
with revising earlier lexical commitments. Degraded-speech literature (Kalikow SPIN test) shows a real
**accuracy interaction, not just a main effect**: 76% correct for high-predictability vs 37% for low-predictability
sentence-final words at matched SNR; Van Os, Kray & Demberg (2022, *Frontiers in Psychology*) report an explicit
Predictability × Noise interaction (β=-2.02, p<.001).

**The scope-limiting fact (CONTESTED only in the sense that it is under-discussed, not disputed):** in every one of
these paradigms, the noisy/ambiguous element is **one word or one slot inside an otherwise fully-formed,
grammatical, mostly-correctly-perceived sentence** — Gibson et al.'s correction space is edit-distance-1-2
alternatives, trusting ~95% of the sentence as accurately perceived. Cloze-probability pre-activation (DeLong,
Urbach & Kutas 2005) is itself PARTIALLY non-replicated at the article level (Nieuwland et al. 2018, *eLife*,
9-lab collaboration) — flagged here as an internal calibration correction the original scan surfaced against its
own first citation, preserved rather than smoothed over.

**RECOMMENDATION:** treat top-down rescue as real but narrow-scope. It is evidenced for near-miss,
plausible-neighbor confusions against an otherwise-intact structure — NOT for a front end that fails to extract
structure at all. This directly motivates the Q3 diagnostic below.

## Q3 — THE KEY IMPLICATION: is the ~0.32 front-end-swamps-everything result faithful or an artifact?

**Adjudicated, calibrated answer: it is genuinely undetermined without one specific diagnostic, and that
diagnostic is cheap.** Two facts pull in opposite directions and BOTH must be held:

1. **Pulling toward "faithful, not an artifact":** Ferreira's good-enough processing (Ferreira, Bailey & Ferraro
   2002, *Current Directions*; Christianson, Hollingworth, Halliwell & Ferreira 2001, *Cognitive Psychology*) is
   direct evidence the brain does NOT reliably self-correct even when it has the machinery — and the flagship
   demonstration is specifically **thematic-role assignment lingering wrong** ("Did the mother dress the baby?"
   answered "yes" after "While Anna dressed the baby played," even after forced reanalysis). This is the SAME
   class of extraction the substrate's front end performs (event/role assignment). So a persistently-wrong,
   uncorrected role-extraction front end is not obviously unfaithful — it may be the brain-accurate expectation
   for exactly this task, under Ferreira's documented boundary conditions (implausible-but-not-impossible parse,
   expensive reanalysis, low task demand → error lingers; cheap/plausible reanalysis, explicit cue → corrected).

2. **Pulling toward "the rescue mechanism is out of scope, so a 0.32 front end tells you nothing about
   interactivity either way":** every rescue/correction mechanism reviewed (noisy-channel, cloze, SPIN,
   anticipatory pre-activation) operates on an otherwise-mostly-intact signal with one ambiguous or corrupted
   slot. None was ever demonstrated to operate when the majority of structured output is simply wrong or missing.
   A Bayesian noisy-channel posterior needs an *informative* likelihood to combine with the prior; at ~30%
   accuracy the likelihood is barely more informative than noise, so the posterior should degenerate toward the
   prior alone (confident, fluent, and frequently wrong) — not toward truth recovery. **A front end this broken is
   not obviously in the regime where the top-down mechanisms in this literature are expected to help much, so its
   badness cannot be blamed on "we omitted top-down feedback" without checking the failure mode first.**

**These two facts resolve into one concrete, testable split:** classify the front end's errors as **MISSES**
(nothing extracted — a role/event slot simply absent) vs **MISASSIGNMENTS** (something extracted, but the wrong
filler among plausible alternatives — the Gibson/Christianson pattern). Only misassignments are in scope for any
top-down/interactive correction mechanism in this literature. Misses are a detection-capability gap that no amount
of "add a feedback loop" would be expected to fix, per every source reviewed.

**RECOMMENDATION (the cheap decisive test, do FIRST, before building anything):** relabel a sample (n≈100-150) of
the existing front-end errors on data already on disk into MISS vs MISASSIGNMENT.
- If MISS-dominant (my calibrated prior: this is likely, given "~0.32 recall" is the framing already used in
  STATUS.md/PROBLEM.md, and recall failures are usually detection gaps) → the front end is a real, brain-independent
  capability ceiling; p1's planned pure-feedforward composition is *already* the right test, no interactive arm is
  motivated by this literature, and a swamped result should be reported as a genuine capability finding, not an
  artifact.
- If MISASSIGNMENT-dominant → the literature directly motivates adding ONE late-merge arm (Q1's recommendation) and
  testing it specifically on the misassignment subset, where a real, moderate (not blanket) gain is predicted.

## Q4 — Event segmentation: bottom-up prediction error only, or also top-down schema/goal knowledge?

**PINNED, unambiguously top-down-laden — and this is a live, actionable fidelity gap in the substrate's own
landed organ.** Zacks, Speer, Swallow, Braver & Reynolds (2007, *Psychological Bulletin*) state directly that
"event schemata affect event models in a top-down fashion" and that the predicting event model is "determined by a
combination of bottom-up and top-down processing," integrating sensory input with stored script/schema knowledge.
Speer, Zacks & Reynolds (2007, *Psych Science*) show boundaries track situation-model content (goals, causes), not
surface features. Newtson (1973) and Hard, Recchia & Tversky (2011) show observer instructions/goals change
segmentation grain even for the SAME stimulus. Zacks, Tversky & Iyer (2001, *JEP:General*): coarse (goal-level) and
fine (subgoal-level) boundaries are **coupled, not independent** — coarse structure constrains where fine
boundaries can fall. In text specifically (Zwaan, Magliano & Graesser 1995's event-indexing model), segmentation
tracks discourse-level discontinuities (protagonist, causality, time/goals) — i.e. schema/world-knowledge content
dominates even more in reading than in video, since there's no raw sensory stream to fall back on.

**Direct hit on an existing landed organ:** `hdlab/n400_coherence_monitor.py` (BRAIN_FOUNDATIONAL_AUDIT.md §2b,
F5) computes boundary prediction error as `1 - cos(content, running_event_gist)` against a **running-mean,
reset-per-event content gist** — no schema, script, or goal term. Per Zacks et al.'s own core papers, this is a
stripped special case the theory's own authors explicitly reject as incomplete: the running-gist-only version would
miss the LOAD-BEARING top-down channel that determines not just *whether* a boundary fires but *where* it lands
(script violations, goal changes shift boundary position independent of low-level content statistics).

**RECOMMENDATION — AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT.md §2b (F5):** this is a genuine fidelity gap, not
disqualifying for p1's immediate decisive test (the isolated 0.988-vs-floors result was measured on synthetic
items that likely never tested schema violations, so it isn't refuted — it's untested on the dimension that
matters). It is NOT required to unblock p1's core question (does composition beat baseline / is the front end the
wall) but should be logged and queued as a follow-on: seed or periodically update the "expected content" prior from
a coarse discourse-topic/genre signal, then re-test whether boundary PLACEMENT (not just within-event recovery on
schema-free items) improves.

## Q5 — Situation-model retrieval: hippocampal, cortical/LT-WM, or resonance — and does the substrate's landed organ match?

**PINNED, and this is good news for what's already landed.** Myers & O'Brien (1998, *Discourse Processes*) and
McKoon & Ratcliff's minimalist hypothesis (1992, *Psych Review*) independently establish that moment-to-moment
retrieval during reading is an **automatic, passive, parallel resonance process**: the current sentence acts as a
content-addressable cue against the WHOLE prior discourse representation (not just a single top situation-model
node), closer to "everything stored so far" than a directed search. This is the PINNED default mechanism — it maps
directly onto the substrate's landed `hdlab/content_addressable_retrieval.py::AdditiveCueRetrieval` (additive
Lewis-Vasishth partial-cue activation, argmax), which is therefore NOT an invented convenience but the
literature-correct choice.

**But resonance alone is not sufficient, per three qualifications:** (1) Ericsson & Kintsch's Long-Term Working
Memory (1995, *Psych Review*) retrieval STRUCTURES are themselves an expertise/practice-built, top-down scaffold
that determines what resonance can even find — retrieval quality is coupled to how well-organized the store is at
write time. (2) Kintsch's own Construction-Integration model (1988, *Psych Review*) is, within one cycle, an
iterative constraint-satisfaction settle (multi-cycle relaxation) that actively SUPPRESSES resonance-activated but
context-inappropriate content — not a single feedforward step even locally. (3) Graesser, Singer & Trabasso's
constructionist theory (1994, *Psych Review*) shows goal-driven "search after meaning" inference generation is a
real, more strategic mechanism operating alongside passive resonance, not a replacement for it. Neurobiologically,
Baldassano, Chen, Zadbood, Pillow, Hasson & Norman (2017, *Neuron*) show hippocampal activity spikes at
cortically-defined event boundaries during naturalistic narrative listening and predicts later reinstatement — the
honest answer is genuinely **both**: hippocampus indexes/binds at event boundaries (maps to the substrate's DG/CA3
gate), cortex/WM holds the ongoing situation-model content (LT-WM), consistent with the two-organ split already on
the shelf.

**RECOMMENDATION:** keep `AdditiveCueRetrieval` as-is for p1 (it is the pinned mechanism, not a compromise). But
retrieval-quality results from p1 should be interpreted jointly with Q4: if retrieval underperforms, check whether
the STORE was mis-organized by schema-blind segmentation before concluding retrieval itself is the deficient stage
— a Q4 defect can masquerade as a Q5 defect.

## Cheap decisive test (formal)

**Test 1 (do first, ~zero cost):** Error-taxonomy audit. Sample n≈100-150 of the existing front-end
event/role-extraction errors (already on disk, no new run). Classify MISS (nothing extracted) vs MISASSIGNMENT
(wrong filler among plausible alternatives, Gibson/Christianson-pattern). Report the split with a CI.

**Test 2 (only if Test 1 finds MISASSIGNMENT-dominant, ≥30% of errors):** Extend p1's planned oracle-vs-live
comparison from 2 points to a 3-point noise sweep: {oracle-clean, moderately-degraded (synthetically corrupt the
oracle at a rate/kind matching the observed misassignment pattern — swap in a plausible-neighbor filler, don't
delete), current live (~0.32)}. Add ONE late-merge arm: combine the front end's raw confidence with the existing
`n400_coherence_monitor` coherence score at the retrieval/write-acceptance decision (reuse
`dg_ca3_recollection_gate`'s confidence-combination pattern) — a forward-computed Merge-style combination, not a
recurrent loop.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**H1 (routing hypothesis):** the ~0.32 front-end errors are MISS-dominant (>=70% of the audited sample).
P_deflated=0.55 (raw prior ~0.70-0.75 based on how "recall ~0.32" is already framed in STATUS.md/PROBLEM.md;
deflated 0.15-0.20 for no direct measurement yet). HARD-PASS: >=70% MISS in the n=100-150 sample, CI excludes 50%.
HARD-FAIL: <50% MISS (i.e., misassignment-dominant) — in which case route directly to Test 2, do not conclude "pure
capability ceiling" yet.

**H2 (late-merge rescue, ONLY tested if H1 hard-fails):** the late-merge arm beats pure-feedforward CI-separated,
specifically on the misassignment subset, at the MODERATE-noise point — and this margin SHRINKS toward zero (not
grows) as noise approaches the current catastrophic ~0.32 level, because the likelihood term becomes uninformative.
P_deflated=0.40 (raw ~0.55-0.65 from strong SPIN/noisy-channel effect sizes reviewed above; deflated 0.15-0.25 for
untested substrate-specific implementation of the merge; capped at 0.50 per novel-synthesis cap regardless).
HARD-PASS: CI-separated gain over pure-feedforward on the misassignment subset AND over an info-free twin
(shuffled coherence score) AND the predicted non-monotonic (peaks at moderate, collapses at catastrophic noise)
pattern. HARD-FAIL: any of — no CI-separated gain over the info-free twin; gain is flat or grows monotonically with
noise (inconsistent with an uninformative-likelihood account); gain is uniform across misassignment/miss items
(not concentrated in misassignment, which the mechanism predicts).

**H3 (composition-general):** if H1 hard-passes (MISS-dominant), p1's already-planned pure-feedforward composition
run will show the front end swamping downstream organs, and this IS a faithful capability finding, not an
architecture artifact — no interactive/late-merge arm is needed to trust that verdict. P_deflated=0.50 (capped;
this follows near-definitionally from H1 hard-passing plus the literature's scope limits in Q3, but is still
substrate-specific synthesis).

## Cross-thread synthesis

Converges directly with `notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` (frequency-prior +
context-coherence as an argmax two-term score, not recurrent settling — same Merge-model logic found independently
here) and with p6 `the_meaning_win_is_offline_context_free_and_unwired` (context-conditioning did NOT beat the
frequency prior — consistent with top-down correction being narrow-scope, not a blanket override). Extends
`BRAIN_FOUNDATIONAL_AUDIT.md` §2b's F5 (N400 coherence monitor) entry with a concrete, actionable gap (missing
schema/goal term) that was previously unflagged. Directly answers the open question the p1 PROBLEM.md brief itself
raises in its §7 bar ("is the front-end the binding constraint that swamps the organs... a well-attributed... is
the single most valuable finding available right now") by giving the specific control (error taxonomy first, then
a noise sweep, not a binary oracle-vs-live check) that makes that attribution trustworthy rather than assumed.

## Substrate-product implications

In plain terms: the reading system's early "who did what to whom" extraction step is currently wrong about two out
of every three times. Before assuming that's simply the memory and retrieval steps' fault for not double-checking
it, we need to know WHAT KIND of wrong it is. If it's mostly "found nothing" (a detection gap), no amount of
adding a second-guessing step downstream will fix it — that is a real, separate engineering problem worth its own
attention, not a wiring problem. If it's mostly "found something, but picked the wrong-but-plausible answer," then
the science says a cheap, one-more-signal check at the decision point (does this candidate answer fit the story so
far?) should recover some — not all — of the accuracy, and that check is buildable from two things we already have
on the shelf, at low cost. Either way, the finding is decision-shaping and worth having before building anything
new: it tells us whether to invest in a better first-read step or a smarter double-check step, and the check to
find out costs nothing beyond re-reading errors we already recorded.

## Citations (verified count)

~30 distinct citations surfaced across 4 parallel Sonnet lit-scans (public literature, standard academic search,
not independently re-verified against primary sources by this synthesis — standard lit-scan calibration). Notable
self-correction preserved: one scan flagged that DeLong, Urbach & Kutas (2005) pre-activation claim is only
partially replicated (Nieuwland et al. 2018, *eLife*, 9-lab collaboration) — kept in rather than smoothed over.
Key sources: Norris, McQueen & Cutler 2000 (*BBS*, Merge model); Zacks, Speer, Swallow, Braver & Reynolds 2007
(*Psych Bulletin*, EST); Kintsch 1988/1998 (Construction-Integration); Ericsson & Kintsch 1995 (*Psych Review*,
LT-WM); Myers & O'Brien 1998 (*Discourse Processes*, resonance); Ferreira, Bailey & Ferraro 2002 / Christianson et
al. 2001 (good-enough processing); Gibson, Bergen & Piantadosi 2013 (*PNAS*, noisy-channel); Levy 2008 (*Cognition*,
surprisal); Baldassano et al. 2017 (*Neuron*, hippocampal narrative indexing); Kuperberg & Jaeger 2016 (*LCN*,
predictive coding in language); Altmann & Kamide 1999 (*Cognition*, anticipatory eye movements); Speer, Zacks &
Reynolds 2007 (*Psych Science*); Zwaan, Magliano & Graesser 1995 (event-indexing model).

## TLDR

We asked whether the brain reads in one straight pass (see word, get meaning, find event, done) or double-checks
itself as it goes. Answer: a bit of both, and science tells us exactly which kind of double-checking is real and
which isn't. The brain does NOT have a full "go back and rewrite everything" loop — but it does have a cheap,
late "does this fit the story so far?" check, and it only fixes near-miss wrong answers, not total blanks. Before
building anything, the free next step is to sort our system's current mistakes into "found nothing" vs "found the
wrong plausible thing" — that alone tells us whether adding a double-check would help at all.

## Questions

None.

## Next steps

1. Run the error-taxonomy audit (Test 1) on the existing ~0.32 front-end output — cheapest, most decisive next
   action, zero new experiment.
2. Route based on Test 1's result: MISS-dominant -> p1's existing plan is already correct, proceed as designed.
   Misassignment-dominant -> add the late-merge arm + 3-point noise sweep (Test 2) to p1 before drawing the
   front-end-is-the-wall conclusion.
3. Log the F5 (N400 coherence monitor) missing-schema-term gap as an AUDIT UPDATE in
   `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b at next integration touching that organ — not blocking for p1.
