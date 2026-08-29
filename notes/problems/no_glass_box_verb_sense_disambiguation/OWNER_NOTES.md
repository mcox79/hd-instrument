---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — no_glass_box_verb_sense_disambiguation                          (STATUS: SOLVED)
hdlab/ UNTOUCHED (proposed diff only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_frame_sense_disambiguator.py            -> 11/11
          experiments/exp_frame_sense_serves_motion_cue_v2.py   -> BAR 3 HARD_PASS (5-fold CV n=961)
          experiments/exp_frame_sense_context_broad_v1.py       -> BAR 2 (gated context beats MFS)
          python tools/problem_ledger.py --check                -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════════════

BAR (§7): ALL of — (1) glass-box sense/frame disambiguator over the parse for the two dominant confusions
(motion-vs-deposit; perception-vs-speech); (2) beats a most-frequent-sense floor CI-separated on a real WSD
gold, info-free twin LOSES, null p95, a context-flipped positive control; (3) lifts a downstream front-end
(ToM motion cue OR mined-event precision) CI-separated vs the un-disambiguated path; (4) one-screen summary.

VERDICT: ALL FOUR BARS CLEAR.
 - BAR 1 MET: experiments/frame_sense_disambiguator.py — reordered-access PRIOR + argument-structure
   CONSTRUCTION (Goldberg/Levin) incl. the Barwise&Perry/Gisborne COMPLEMENT-TYPE rule ("saw him leave"=
   perception vs "saw that S"=cognition vs "saw the point"=cognition), stored-unit IDIOM lexicon (1852
   phrasal + 566 object MWEs), thematic FIT, reliability-gated CONTEXT cue, combined by graded_competition,
   with Frazier&Rayner UNDERSPECIFICATION as the default. Witness 11/11; minimal pairs 6/6.
 - BAR 2 MET: on the broad frame-alternating multiclass WSD gold (SemCor human tags), the reliability-gated
   context cue BEATS MFS — 5-fold pooled paired-Δaccuracy +0.007, 95% CI [+0.002,+0.012] (excludes 0),
   McNemar p=0.003, override precision 0.558; the INFO-FREE (shuffled-label context) TWIN loses BELOW the
   null p95 (real +0.007 vs null p95 −0.010); positive control = the context-flipped minimal pairs.
 - BAR 3 MET: mined MOTION-event decision (the exact call the ToM ledger / an event-miner makes), 5-fold CV
   pooled n=961: DISAMBIG+context 0.685 [0.655,0.713] BEATS the un-disambiguated verb-string front-end
   0.611 [0.580,0.642] CI-SEPARATED (non-overlapping), McNemar p=8e-06 (160 fixed / 89 broken), motion
   precision 0.611->0.677, info-free twin loses -> HARD_PASS.
 - BAR 4 MET: one-screen summary (this).

THE STORY (a corrected wall — the owner's catch): I first filed PARTIAL concluding "MFS is a wall." That was
WRONG. The owner pushed back — the brain does this, so a brain-faithful mechanism must — and the discipline
agrees ("brain-faithful losing = presumed impl-bug"). The fix was the brain's actual lever I had OMITTED:
CONTEXT (reordered access). Two confounds/bugs were hiding it, each drilled and fixed: (a) a WordNet-vs-corpus
PRIOR MISMATCH inflated fake "gains"/"breaks" — fixed with a matched-prior one-variable test; (b) the
conservative gate silently REVERTED context-driven moves — fixed to honor a decisive discourse vote; (c) a
coarse "proposition" type conflated comm/cog objects ("see the point"->communication) — split into comm_obj/
cog_obj. Un-gated, context HURTS the broad task (over-fires on taxonomy/idiom/world-knowledge senses); a
PER-VERB RELIABILITY GATE (Friston precision-weighting — trust context only for the 163/1379 verbs where it
beats MFS on train) flips it to a robust broad win.

OPTIMIZATIONS SWEPT (all MEASURED, brain-foundational, fair): grounded-context = NEGATIVE (representation
isn't the issue); large-corpus BOOTSTRAP scale-up = NEGATIVE (out-of-domain data REGRESSES 0.761->0.700 — the
bottleneck is IN-DOMAIN sense-tagged data, not volume; the in-domain oracle proves +0.045 headroom);
cross-sentence context = NEGATIVE (local suffices); coref for anaphoric objects = NEGLIGIBLE (few pronoun-
object confusion cases); diagnostic-word weighting = MARGINAL. CUE CALIBRATION (conditional-logit MLE +
temperature): the hand-set weights are near-accuracy-optimal (validates the sweep), but the softmax is
OVERCONFIDENT (ECE 0.245->0.209) because the cues aren't conditionally independent -> the additive->softmax=
Bayesian-posterior claim is STRUCTURALLY ISOMORPHIC with an accuracy-optimal argmax but the CONFIDENCE is
approximately, NOT exactly, calibrated. Kept as an honest caveat.

RESEARCH (validated the whole stack): a 4-lane brain-foundational drill on the "I see" perceive-vs-cognize wall
confirmed every cue — Sweetser mind-as-body regular polysemy; Barwise&Perry/Gisborne/Dik&Hengeveld/Noonan
complement-type discriminator; Frazier&Rayner/Frisson&Pickering underspecification; Apresjan/Copestake&Briscoe
class-scoped-rule + frequency-weighted default = exactly this mechanism. (research_see_perceive_vs_cognize + the
earlier research note on disk.)

HONEST CAVEATS (withdraw first if wrong): the BAR-3 lift is over the UN-DISAMBIGUATED FRONT-END (what the ledger
actually does — fire motion on the verb string); DISAMBIG TIES the stronger per-lemma-MFS-binary floor (0.685) —
the win is removing false motion events, not beating an oracle prior. BAR-2's broad effect is small (+0.007)
though CI-separated on the paired delta. The context model is IN-DOMAIN (SemCor); out-of-domain transfer is
unproven (measured to regress). The residual CEILING is precisely characterized, not hand-waved: bare "I see"/
discourse backchannels (need cross-sentence pragmatics) + WordNet lexname-taxonomy quirks ("discover an avocado"
= gold cognition) — the world-knowledge piece the no-LLM invariant precludes.

KEY REALIZATIONS: (1) "MFS is a wall" was MINE, not the brain's — I'd omitted CONTEXT; the brain beats MFS with
context, so a faithful mechanism can too. (2) A cue applied INDISCRIMINATELY hurts; the brain applies it WHERE
RELIABLE (precision-weighting) — the same fix turned both the construction cue (verb-sensitivity) and the
context cue (per-verb reliability gate) from wash/harm into a win. (3) The bottleneck is IN-DOMAIN DATA, not
model cleverness (measured: bootstrap out-of-domain regresses; oracle in-domain gains). (4) Standard WSD golds'
sense grain (WordNet lexname, WiC) mismatches the event-frame grain the front-ends need — the disambiguator
should be scored on the DOWNSTREAM task, which is where it wins.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md, verb-polysemy wall): now BUILT + validated. Reordered-access +
construction + complement-type + idiom-storage + thematic-fit + reliability-gated context + graded-competition,
all PINNED/research-validated; parameters swept. Deviation: additive->softmax combiner has an accuracy-optimal
argmax but approximately-calibrated confidence (ECE ~0.21).

PROPOSED hdlab LANDING (strategy lands; I did not write hdlab/): promote experiments/frame_sense_disambiguator.py
+ experiments/context_prior.py + data/{idiom_foundation_v1, context_prior_v1} -> hdlab (gated context ON,
min-context guard). Optional default-OFF gate: perceptual_access_ledger._motion_signal consults it to suppress
non-motion departures. Do NOT adopt a fixed verb->sense lookup, out-of-domain context data, or claim an exact
Bayesian posterior. TWO FOLLOW-ON BRIEFS FILED (FOLLOW_ON_BRIEFS.md): (A) coreference_for_anaphoric_arguments —
the #1 real-narrative cap; (B) wire_the_event_frame_as_a_shared_primitive — banks the bar-3 win into the live
reader.

FILES: experiments/{frame_sense_disambiguator, context_prior, idiom_gate, idiom_gate_expand_v1, sense_selprefs}.py;
experiments/exp_frame_sense_{semcor_v1, wic_v1, serves_motion_cue_v1, serves_motion_cue_v2, confusion_pairs_v1,
serves_tom_ledger_v1, bakeoff_v1, subordinate_recovery_v1, context_v1, context2_v1, context_scaleup_v1,
context_broad_v1, calibration_v1}.py; verification/test_frame_sense_disambiguator.py (11/11);
data/{idiom_foundation_v1/idioms.json, sense_selprefs_v1/table.json, context_prior_v1/model.pkl};
notes/problems/no_glass_box_verb_sense_disambiguation/{SOLVED.md, BRAIN_MECHANISM_SPEC.md, FOLLOW_ON_BRIEFS.md,
research_brain_foundational_verb_sense_2026-08-28.md, research_see_perceive_vs_cognize_2026-08-28.md}. hdlab/ UNTOUCHED.

TLDR (plain language): the reader now tells "left the room" (walked out) from "left a note" (put down), and
"went to the store" from "went bad" — not by a lookup, but by copying how the brain does it: grammar + stored
idioms + CONTEXT, each trusted only where it's a reliable clue. It beats the "always guess the commonest
meaning" baseline with clean statistics, and it makes a real event-miner measurably more precise (fewer false
"someone moved" events, 0.61->0.68). I first wrongly said the baseline was unbeatable; the owner corrected me,
and the fix was the brain's own tool (context) that I'd left out. QUESTIONS: none. NEXT: land it; the two
highest-value follow-ons are coreference and wiring this event-reader into the rest of the pipeline.
═══════════════════════════════════════════════════════════════════════════════════════════════════
