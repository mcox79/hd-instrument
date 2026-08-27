---
priority:
review: EXCELLENT
review_text: "Integrated PARTIAL/EXCELLENT 2026-08-27 (owner-DONE). Re-verified scaffold-free first-hand (test_frontend_role_who_did_what.py, 6/6 PASS). The front-end wall is REAL and RECOVERED: the fair brain-faithful assigner (core-mention selection + QUOTE EXCLUSION + a learnable SPEECH-VERB/quotative class + the organ's graded perceptron over selected mentions) = 0.747 [0.680,0.809] end-to-end on McGuffey, BEATS the live positional baseline 0.483 CI-separated; role-balanced macro 0.191 > majority-macro 0.125. On modern QA-SRL two-animate (n=564, animacy structurally chance 0.500): learned WORD-ORDER(+voice) = 0.918, and adding THEMATIC-FIT is net-negative everywhere. REFUTES two brief premises on disk: (1) naively wiring the learned organ is WORSE (0.385 -- over-generation 9.96 cand/clause + no quotative cue); (2) fixing animacy-dominance via thematic-fit does NOT help -- WORD ORDER dominates English role assignment (PINNED, MacWhinney/Bates cue-validity; the two-animate 0.918 is its modern echo). Deepening (4 lit-VET'd passes, multiple self-corrections): thematic-fit is a REAL but LOW-VALIDITY backup cue (pure/order-removed 0.585 CI-sep above chance + its shuffled twin, correctly dominated by order -- Dowty 1991 indeterminacy + Cai 2022 human analog of additive-fit-hurts); the speech-verb class is genuinely SEMANTIC + brain-faithfully LEARNABLE from quote co-occurrence (verba dicendi; beats a proper NULL DISTRIBUTION on the role-balanced metric, not a lucky single-draw twin); normalized-recurrence dynamics (Spivey-Knowlton) is a more brain-faithful integrator than the perceptron at EQUAL accuracy (its difficulty-signal payoff unproven on this word-order-dominant corpus). VERDICT PARTIAL: the rigorous-negative branch -- it TIES (does not clear) the agent-saturated 78% majority floor on McGuffey plain accuracy; the clean floor-clearing win is on the role-balanced metric + modern QA-SRL (0.93 vs 0.50), pending a role-balanced reading gold. Judged CONVERGED for natural-corpus role labeling (mechanism identified+replicated+tested; further gains need DATA, not mechanisms). Grade EXCELLENT (rigorous, lit-VET'd, self-corrected, refutes the brief on disk). hdlab landing EARNED (the quote-exclusion + speech-verb + core-mention wiring beats the live baseline CI-sep) -> QUEUED proven-ready (default-off; NO thematic-fit). Proximity audit named the biggest remaining front-end gap (the batch UD parser vs incremental/predictive structure) -> packaged as the successor."
---

# PROBLEM: the live reader's FIRST step -- working out who did what to whom -- is the measured wall; it MISLABELS roles (mostly agent-vs-patient between two people), and a LEARNED organ that could fix it already exists, ISLANDED

**slug:** `the_live_front_end_mislabels_who_did_what_to_whom` - **opened:** 2026-08-26 by the strategy session
(the re-pointed successor the DECISIVE `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end` named:
the front-end/event-role extraction is the binding constraint, measured -- every downstream organ is swamped by it).
**status:** OPEN - **THE TOP PRIORITY: the measured binding constraint for end-to-end comprehension (Branch B of `notes/NEXT_STAGE_after_wire_and_measure.md`).**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. The wire-and-measure proved the composed reader
> scores BELOW a trivial "always say agent" floor end-to-end (0.483 < 0.781) while the SAME memory organs hit 1.000 on
> CLEAN inputs -- so the front-end is the single lever that moves comprehension, and a brain-faithful verb-argument
> assigner already recovered most of it (0.48→0.74 CI-sep) in a construction proof. This is the highest-leverage
> BUILDABLE work in the substrate right now. Everything downstream (entity-tracking p2, meaning-context p8) is gated on
> a front-end that emits clean events.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just plugged all our proven memory organs into the live reader and measured it on real passages. The verdict was
decisive: on clean, hand-checked inputs the organs work perfectly, but run through the reader's OWN first step --
figuring out who did what to whom from raw text -- the whole system scores WORSE than a dumb "always guess the most
common answer." The bottleneck is that first step, and we know exactly how it is wrong: not "found nothing" but "found
something and MISLABELLED it" -- mostly getting the doer vs the done-to backwards between two people (e.g. treating the
speaker in `"..." said the boatman` as the one spoken to). A better memory does nothing until this is fixed.

This problem builds the brain-faithful first-read step: assign the right thematic role (who is the agent, patient,
experiencer, recipient...) to each participant, using verbs and plausibility the way the brain does. **Crucially, a
LEARNED organ that does much of this ALREADY EXISTS in the substrate and is switched off** -- so the core of the work is
to WIRE it into the live reader and MEASURE it, improving where it falls short, NOT to build a new one from scratch.

## 2. WHY THIS ONE

- **It is the measured binding constraint.** The wire-and-measure showed every downstream organ is swamped by this
  step; a brain-faithful verb-argument assigner recovered most of the wall in a construction proof (front-end 0.36→0.82,
  end-to-end 0.48→0.74 CI-separated). It is the one lever that moves comprehension.
- **WIRE-DON'T-ISLAND: the organ exists, islanded.** `hdlab/thematic_role_labeler.py` is a LEARNED (averaged-perceptron)
  Competition-Model role labeler with a RICHER inventory (AGENT/PATIENT/EXPERIENCER/RECIPIENT/GOAL -- covering much of
  the 104 out-of-scope roles the current agent/patient front-end structurally cannot emit), a real animacy lexicon, 228
  verb frames, scramble/ablate controls -- registered `validated_hard_pass_realderived_islanded_2026-08-10`, with ZERO
  wirings into the live reader. The wire-and-measure's own Stage-4 hand-cascade re-derived a WORSE subset of it.
- **Everything else is gated on it.** Entity-tracking (p2), meaning wiring, QA -- all need a front-end that emits clean,
  correctly-labelled events.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** thematic role assignment is INCREMENTAL, GRADED, WEIGHTED-CUE CONSTRAINT SATISFACTION -- best formalised as
Bayesian log-linear / noisy-channel: score each (NP, role) by `exp(Σ_i w_i · log P_i)` over cues -- word order / voice,
VERB ARGUMENT STRUCTURE (PropBank/VerbNet selectional frames), ANIMACY, case, THEMATIC FIT (McRae selectional
preference), and discourse -- graded and REVISABLE, not a fixed rule cascade (MacDonald, Pearlmutter & Seidenberg 1994;
McRae, Spivey-Knowlton & Tanenhaus 1998; Levy 2008 noisy-channel; Gibson, Bergen & Piantadosi 2013 good-enough; eADM,
Bornkessel-Schlesewsky). It localises to pMTG/IFG (verb-argument structure) + angular gyrus (event combination). The
composition is a late algebraic MERGE of these forward-computed cue streams (Norris/McQueen/Cutler 2000), not backward
editing.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** the exact cue set + weights; the lexicon SOURCE (the
existing organ's learned perceptron + `hdlab/learner/` for selectional preference vs a hand frame list -- prefer
LEARNED); how the graded constraint-satisfaction is implemented over our reps; the special handling of quotative
inversion (the biggest single error class -- speech verbs put the speaker POSTVERBAL); and the compose points with the
already-integrated organs (below). COPY the OPERATION (graded weighted-cue role assignment, revisable); SWEEP the params.

**Compose, don't duplicate (already integrated this session):** the PREDICTIVE READER supplies verb→argument
SELECTIONAL PREFERENCE (thematic fit) -- exactly the cue for the ~26 two-animate "who-did-what" cases animacy cannot
break; the RELCL FILLER-GAP resolver handles reversible relative/cleft constructions; the N400 monitor marks event
boundaries. This problem INTEGRATES these into one graded role assigner, it does not re-derive them.

**Corpus-age note (MIND IT):** the reading corpus (McGuffey) is ~200 years old AND dialogue-heavy (quotative inversion
is common there). The existing learned labeler HARD_FAILED its own MODERN-prose (QA-SRL) revalidation as animacy-
dominant -- so measure on BOTH, and hold era fixed across arms; a fix that only helps archaic quotative prose is not the
same as a fix that generalises.

## 4. MEASURED vs INFERRED

**MEASURED (`wire_the_validated_organs...`, integrated PARTIAL/EXCELLENT, re-verified scaffold-free):** through the live
front-end the composed reader answers entity-role queries at 0.483 [0.410,0.556] -- BELOW the trivial majority floor
0.781; the same organs on CLEAN inputs hit 1.000 (front-end localised as the wall by the oracle-vs-live contrast). Errors
are MISASSIGNMENT-dominant (role-label 86 > entity 50 > miss 30; 104 gold roles OUT-OF-SCOPE for agent/patient). A
brain-faithful verb-argument assigner (verb-class + quotative inversion + animacy) lifted front-end in-scope 0.36→0.82
and end-to-end 0.48→0.74 CI-separated over a position baseline AND an info-free twin -- but TIED the 0.908 in-scope
majority floor (residual = out-of-scope roles + two-animate). The existing learned `thematic_role_labeler.py` EXISTS +
is islanded; its own revalidation HARD_FAILED on modern prose (cue-integration collapses to animacy alone; strong
canonical 0.90 / experiencer 0.89, weak agent_by_phrase 0.35 / ditrans_recipient 0.16 / passive 0.73).

**INFERRED / OPEN (this problem, decisive either way):**
- Whether WIRING the existing learned Competition-Model role labeler (with richer roles + graded cue integration + verb
  selectional preference for two-animate) into the live reader beats the live position-baseline front-end AND clears (not
  just ties) the majority floor, end-to-end on real passages.
- Whether fixing its animacy-dominance (graded constraint-satisfaction that actually integrates cues, per McRae/S-K/T)
  generalises to modern prose, not just archaic quotative McGuffey.

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT build a new role extractor from scratch -- WIRE + MEASURE `hdlab/thematic_role_labeler.py` (+ `hdlab/learner/`
  for selectional preference). The wire-and-measure's Stage-4 hand-cascade is a CONSTRUCTION PROOF that the lever works;
  do not re-derive it -- improve on the existing LEARNED organ.
- Do NOT use a rule-PRIORITY cascade -- it is the known divergence; the faithful form is GRADED parallel constraint-
  satisfaction (log-linear / normalised-recurrence).
- Do NOT re-run the downstream memory organs as a comprehension lift -- the wire-and-measure proved they are swamped by
  this front-end (they ARE validated on clean inputs; their live payoff is gated on THIS).
- Query `experiment_index.py query "thematic"`, `query "role"`, `query "vargs"`, and read
  `exp_thematic_role_labeler_qasrl_modern_revalidation_v1` (its HARD_FAIL diagnosis) + the wire-and-measure Stage 4
  (`exp_wire_organs_endtoend_v1.py`) BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `hdlab/thematic_role_labeler.py`, `hdlab/animacy_lexicon*`, `hdlab/learner/`, and the live read path
  (`hdlab/situation_reader.py` / `reading_grounding_loop.py`) -- confirm where role assignment happens live and how to
  swap the assigner behind a flag (identical downstream, only the assigner changes -- the attributable design).
- Reproduce the wire-and-measure's live-front-end number + its error taxonomy once, so you trust the wall you are moving.
- Pick a real reading population where roles matter (the McGuffey entity-role gold the wire-and-measure used, AND a modern
  QA-SRL slice) and recompute EVERY floor (majority, position baseline, info-free twin) on each.

## 7. THE BAR

Wire a graded, brain-faithful thematic-role assigner (the existing learned Competition-Model labeler, improved) into the
live reader behind a flag, identical inputs. On a real reading population, floors recomputed on it:

- **The improved front-end must beat (a) the current live position-baseline front-end AND (b) the trivial majority floor,
  CI-separated over its UPPER bound, end-to-end, with an info-free twin (roles assigned by coin-flip / scrambled cues)
  LOSING CI-separated.** Report CI half-width + null p95 beside every margin. Attribute PER CUE (ablate verb-argument /
  animacy / thematic-fit / quotative). Test on BOTH archaic (McGuffey) and modern (QA-SRL) populations.
- **DECISIVE EITHER WAY:**
  - It clears the majority floor CI-separated end-to-end -> wire it live (propose the hdlab diff; strategy lands it) --
    the first real comprehension lift of the substrate.
  - A faithfully-built graded assigner beats the position baseline + twin but still TIES the majority floor -> a
    rigorous negative that localises the residual precisely (out-of-scope role inventory + verb selectional preference +
    the two-animate cases), naming the next lever -- as valuable as the win. State what you built and why it is the
    brain's, and whether the animacy-dominance is fixed.

## 8. FILES AND ENTRY POINTS

- `hdlab/thematic_role_labeler.py` (the LEARNED organ to wire), `hdlab/animacy_lexicon*`, `hdlab/learner/` (selectional
  preference), `hdlab/situation_reader.py` / `hdlab/reading_grounding_loop.py` (the live role-assignment site).
- The integrated composers: the predictive reader's verb→argument selectional preference (see
  `the_reader_is_feed_forward_where_the_brain_is_predictive` SOLVED), the relcl filler-gap resolver
  (`the_relcl_parser...` SOLVED), the N400 monitor (`hdlab/n400_coherence_monitor.py`).
- `experiments/exp_wire_organs_endtoend_v1.py` (the live front-end + error taxonomy + Stage-4 construction proof),
  `exp_thematic_role_labeler_qasrl_modern_revalidation_v1` (the HARD_FAIL diagnosis).
- Prove in `experiments/` + `verification/`; propose the hdlab WIRING diff in `SOLVED.md` (strategy lands it, board Q111).
  **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the memory organs' clean-input 1.000 as a live capability -- it is oracle-input; the live number is
  front-end-bound (this problem).
- Do NOT build a rule-priority cascade or a new hand extractor -- wire + improve the existing LEARNED organ, graded.
- Do NOT score only on McGuffey -- the existing organ HARD_FAILED on modern prose; test both, hold era fixed across arms.
- No number crosses populations/scorers -- recompute every floor on the live population.

---

## SOLVER REVIEW (strategy session, 2026-08-27 — INTEGRATED, owner-DONE)

**Grade EXCELLENT. Verdict PARTIAL** (the brief's rigorous-negative branch, with the residual precisely localized).
Re-verified scaffold-free first-hand — `test_frontend_role_who_did_what.py` 6/6 PASS.

**Why EXCELLENT — a model of disk-outranks-brief rigor.** It refuted BOTH of the brief's premises by *measuring* them:
naively wiring the learned organ is WORSE (0.385 — it labels words inside quotes and gets "said Fred" backwards), and
"fix animacy-dominance with thematic-fit" does not help because **word order dominates English role assignment** — the
actual brain-faithful cue hierarchy (MacWhinney/Bates cue-validity, PINNED; the two-animate 0.918-where-animacy-is-chance
is its modern echo). The fix that works is truer to the brain and simpler: ignore quoted spans, know speech verbs put
the speaker postverbal, lean on word order — recovering the wall 0.48→0.75 CI-separated. Four literature-VET'd deepening
passes, each with a self-correction: it caught its own info-free-twin overclaim (a permuted-role twin preserves the 78%
agent marginal, so it isn't a clean control on a saturated set), a bug leaking word-order into the thematic-fit arm
(fixed → pure thematic-fit is a real 0.585 low-validity cue, not noise — Dowty indeterminacy + Cai 2022), and a
lucky-single-draw verb-class artifact (→ a proper 40-draw null distribution, against which the *learned* speech class
still wins on the role-balanced metric). It showed the speech-verb cue is brain-faithfully LEARNABLE from quote
co-occurrence (not a hand patch), and that normalized-recurrence dynamics is a more faithful integrator than the
perceptron at equal accuracy. It judged the mechanism CONVERGED honestly — further gains need DATA (a role-balanced
gold, human difficulty measures), not new mechanisms.

**What it establishes for the substrate:** the front-end IS improvable brain-faithfully, and the lever is word order +
quote exclusion + a learnable speech-verb class — NOT thematic-fit or animacy. The clean floor-clearing win is blocked
only by an agent-saturated McGuffey query gold (78% agent); on the role-balanced metric and modern QA-SRL the fix beats
the trivial prior. This is decision-shaping: it confirms the wire-and-measure's Branch-B diagnosis AND delivers the fix.

**hdlab landing EARNED, QUEUED proven-ready** (Q111): wire the specific improved assigner into `situation_reader` /
`thematic_role_labeler` default-OFF — QUOTE EXCLUSION in `_pick_role_mentions`, a SPEECH-VERB class (from WordNet
`verb.communication` / distributionally-learned, NOT a hand list) as a graded `role_feats` cue, and the learned
perceptron over SELECTED core mentions only; do NOT add thematic-fit. It beats the live baseline CI-separated, so the
landing is a real recovery (a multi-part live wiring — a focused deliberate landing, not a batch-cram). AUDIT UPDATEs
folded (thematic-role entry: word-order dominant PINNED; thematic-fit real-but-low-validity TESTED; normalized-recurrence
faithful; the organ's training-distribution confound). **The successor packaged** = the biggest remaining front-end
fidelity gap the proximity audit named: the batch UD dependency parser vs the brain's incremental/predictive
structure-building.
