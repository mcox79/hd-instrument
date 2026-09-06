---
priority: 1
slug: close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the reader now builds a LIVE forward prediction (`sm.predict_next_event`, Elman-GEK, default-on) but its coherence/boundary monitor (`n400_coherence_monitor`) still takes its prediction error against a BACKWARD gist, so the predictive-coding loop is OPEN -- close it by taking the N400 / event-segmentation error against the FORWARD prediction (and updating the situation model by mild REINSTATEMENT, not a hard reset), and prove the closed loop beats the current backward-gist monitor CI-separated on a MODERN coherence / event-segmentation gold, with a shuffled-forward info-free twin LOSING and no live-consumer regress.

**slug:** `close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction` -- **opened:** 2026-09-06
by the strategy session. This is the FIRST measured, buildable step of the wall-map's #1 north-star: the dominant
non-brain-foundational decision across three biology-led drills is that we built a FEED-FORWARD PIPELINE OF
HARD-COMMITTING SILOS instead of the brain's SINGLE RECURRENT, TOP-DOWN-PREDICTIVE loop -- and the loop's organs are
already BUILT but LATENT. The just-integrated forward projector (`sm.predict_next_event`) gave the reader a live FORWARD
expectation; this problem closes the loop by redirecting the coherence monitor's error onto that forward prediction. It
is INTEGRATION of landed organs into a loop, not new research -- but the end-to-end comprehension payoff must be PROVEN.
**status:** CANDIDATE -- a WIRING + VALIDATION problem. You build + validate in `experiments/`; strategy lands any hdlab
change (Q111). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `1` because it
> is the wall-map's named highest-leverage brain-foundational build (`WALL_MAP...` FORWARD PLAN step 2, "close the
> recurrent top-down loop"), it is overwhelmingly REUSE of landed organs (low build risk), and the loop-closure
> DIRECTION is ALREADY MEASURED (~3x better event-boundary detection: forward-error F1 0.766-0.806 vs backward-gist
> 0.272 in the SOLVED loop cell). It stays CANDIDATE only because that payoff was measured in a CONSTRUCTION setting
> (concatenated ROCStories + Story Cloze), so the modern-gold end-to-end proof is still owed. Set the real priority when
> promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
A good reader is always a step ahead of the story: they guess what is coming next, and when what actually arrives does
NOT match the guess, that surprise tells them something changed -- a new scene has started, or the last sentence does not
fit. That guess-then-check loop is the core of how the brain reads. Our reader now HAS the "guess what comes next" step
(it was just built and turned on). But the part that measures surprise -- the thing that decides "this is a new event" or
"this ending does not fit" -- is still comparing each new sentence against a summary of what it has ALREADY read
(looking backward), instead of against the forward guess (looking ahead). So the loop is only half-connected. Connect it:
make the surprise signal measure the gap between the FORWARD guess and what actually arrives, and when a boundary fires,
gently carry the recent context forward instead of wiping the slate clean. We have already measured, in a rough test,
that this makes the reader about three times better at spotting where one event ends and the next begins. The job here is
to wire that loop properly and prove, on modern test text, that the forward-guess version really does beat the current
backward-summary version -- and that a scrambled-guess version falls apart, so we know it is the real guess doing the work.

## 2. WHY THIS ONE
This closes the single dominant non-brain-foundational decision in the whole substrate. `notes/WALL_MAP_non_brain_
foundational_decisions_2026-09-06.md` drilled the three biggest below-peak walls (parser, meaning, world-knowledge) and
ALL THREE land on the same place: we built N parallel FEED-FORWARD SILOS, each hard-committing one best hypothesis, where
the brain runs ONE RECURRENT loop in which a top-down forward prediction constrains every lower stage as it reads. The
wall-map names the fix as its highest-leverage build (FORWARD PLAN step 2: "close the recurrent top-down loop -- wire
`predictive_reader` (+ `n400`) into the parse attachment and the meaning re-resolution"). This problem is the FIRST,
measured, buildable step of that closure: the just-landed forward projector (`sm.predict_next_event`, owner-DONE) gave the
reader a live forward expectation, and the SOLVED loop cell ALREADY MEASURED that taking the coherence / segmentation
error against that forward prediction is ~3x better at event-boundary detection than the current backward gist. It is
almost entirely REUSE of landed organs -- so it is high-value and low-risk. It also seeds the deeper prize (the STRETCH):
feeding that top-down expectation into the parse and meaning competitions, which the wall-map argues lifts who-did-what
and WSD at once.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Predictive coding: the cortex continuously predicts its next input TOP-DOWN and computes
  the ERROR between the prediction and what arrives; only the error propagates and updates the model (Rao & Ballard 1999;
  Friston 2010). At the language level the N400 IS that prediction error -- a graded lexical/semantic pre-activation-vs-
  input mismatch (Kutas & Federmeier 2011; Kuperberg & Jaeger 2016; Rabovsky, Hansen & McClelland 2018 model the N400 as
  a forward belief-update / semantic-prediction-error signal). At the discourse level the reader indexes events on a
  situation model (Zwaan event-indexing; Zwaan & Radvansky 1998), and Event Segmentation Theory (Zacks, Speer, Swallow,
  Braver & Reynolds 2007; Reynolds, Zacks & Braver 2007) makes the boundary rule explicit: the event model is a FORWARD
  predictor of the next input, and a boundary is posted when FORWARD prediction error SPIKES against its own running
  baseline. At a boundary the model is REINSTATED / updated, not wiped (Baldassano et al. 2017; Pu, Kong, Ranganath &
  Melloni 2022 fit a gated blend C_t = (1 - lambda)[...] + lambda*C_1, lambda ~ 0.2; Franklin/Gershman SEM gating). So the
  loop is: forward expectation -> arriving content -> error against the FORWARD prediction -> the error updates (reinstates
  / resets) the situation model.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The reinstatement decay lambda (SWEEP ~0.2-0.3; the SOLVED cell found
  0.3 beats hard reset and 0.7 hurts -- do NOT adopt 0.3 blindly); the EST relative threshold tau + baseline decay
  (already present in `n400_coherence_monitor`, SWEEP per deployment); the mapping of "distribution-concentration ->
  confidence" onto the same error currency (fusing error magnitude for the boundary with GEK precision for confidence is
  OUR-INVENTION -- a defensible Friston/EST synthesis, EST's formal model uses magnitude only; flag it, do not overclaim);
  and, for the STRETCH, the precision-weighting that turns the forward expectation into a cue for the parse / meaning
  competitions.
- **NOT brain-faithful (do NOT do).** Taking the coherence/boundary error against a BACKWARD running gist (the current
  monitor -- that is the incumbent this must beat); a hard RESET that wipes the context at a boundary (reinstate instead);
  a learned end-to-end segmentation / coherence model; an external LLM at inference; treating the SOLVED loop cell's
  CONSTRUCTION-gold F1 (concatenated ROCStories) as the modern annotated result the bar requires.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The FORWARD prediction is LIVE and default-on. `hdlab/situation_reader.py` binds `sm.predict_next_event(candidates=
    None, t=None)` at read time (`track_prediction=True` by default, `_read_prediction`, runs LAST in `read()`), a
    glass-box generalized-event-knowledge readout (`hdlab/generalized_event_knowledge.GEKProjector`, Elman 2009 GEK)
    composing a GEK content cue + the agent's-goal cue via `graded_competition`, precision = 1 - normalized entropy. It
    DEGRADES GRACEFULLY (abstains -> None if the gitignored store asset is absent), is a NEW ISLAND (no downstream
    consumer today), and its validated discrimination headline is Story Cloze val 0.5922 CI-separated over the majority
    floor, cross-context twin collapses (owner-DONE `predictive_inference_forward_project...`).
  - The coherence monitor takes its error BACKWARD. `hdlab/n400_coherence_monitor.py` computes e = 1 - cos(content_i,
    running gist of the CURRENT event) and HARD-RESETS that gist at every boundary (EST relative threshold e >= tau *
    running-baseline). Its docstring marks it OFF-PATH / WIRE_CANDIDATE -- it is an ISLAND (verify: no live consumer).
  - The loop-closure DIRECTION is already measured, in a CONSTRUCTION setting (`experiments/exp_forward_event_predictive_
    loop_v1.py`, the SOLVED loop cell -- read its `forward_error_segment` / `backward_error_segment`):
    - (A) COHERENCE (Story Cloze val, pick the coherent 5th sentence): forward-prediction-error acc 0.5922 [0.570,0.615]
      vs backward-gist acc 0.5377 [0.515,0.561] -- same discrimination, only the prediction the error is taken against
      differs.
    - (B) SEGMENTATION (400 ROCStories concatenated; true boundaries = story starts; matched EST z-score threshold):
      forward-error F1 0.766 (reset) / 0.806 (reinstate lambda=0.3) vs backward-gist 0.272 (matched) / 0.043 (landed
      organ); random-boundary floor 0.230; shuffled-stream twin collapses to 0.166. Reset-vs-reinstate: mild reinstate
      (0.3) 0.806 > hard reset 0.766 > heavy reinstate (0.7) 0.707.
  - The SOLVED's AUDIT UPDATE (Tier 5) already recommends: `n400_coherence_monitor` should take its error against the
    FORWARD prediction, and add a swept lambda ~0.2-0.3 reinstatement. This problem is the measured, modern-gold proof of
    that recommendation.
- **INFERRED (you must prove):** that REDIRECTING the coherence / segmentation error onto the LIVE forward prediction
  (`sm.predict_next_event` / `GEKProjector`) and REINSTATING (not hard-resetting) the situation model at a boundary beats
  the current BACKWARD-gist monitor CI-separated on a MODERN gold -- for BOTH coherence discrimination AND event
  segmentation -- with a shuffled-FORWARD info-free twin LOSING and NO live-consumer regress; OR a rigorous LOCATED
  NEGATIVE with the cause named and counted (e.g. the live forward projection abstains / undercovers on real modern prose,
  so on N of M items the forward error cannot be set and the loop falls back to the backward gist -- enumerated). The
  STRETCH -- that the top-down forward expectation, fed as a precision-weighted cue into the parse attachment and meaning
  re-resolution competitions, lifts who-did-what / WSD -- is INFERRED and NAMED, not required.

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the FORWARD projector or `sm.predict_next_event` -- they are LANDED (owner-DONE `predictive_inference_
  forward_project_the_next_event_and_state_from_the_situation_model`). Read that SOLVED.md IN FULL: it built + wired the
  projector, measured the loop-closure direction (the F1 payoff above), and drilled the forward-coherence wall. REUSE it;
  this problem CONSUMES it and closes the loop.
- Do NOT re-derive `n400_coherence_monitor` -- it is landed (`the_substrate_does_not_learn_or_update_by_prediction_error`,
  integrated EXCELLENT). You are REDIRECTING which prediction its error is taken against + adding reinstatement, not
  rebuilding the EST machinery.
- Do NOT re-litigate the SOLVED's located negative -- "the forward projection ties a 1-step co-occurrence COUNTER" is a
  DIFFERENT question (the projector's ABSOLUTE discrimination vs a counter). This problem is about the LOOP: forward-error
  vs backward-gist error, same discrimination. Beating the counter is NOT the bar here.
- Do NOT re-measure the construction-setting F1 (0.766-0.806 vs 0.272) and call it done -- that was concatenated
  ROCStories with story-start boundaries + Story Cloze val, in an experiment cell. It NAMES the direction; the bar is a
  MODERN annotated gold with the twin + no-regress, floor recomputed on the item's own population.
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold, and do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "segmentation"`
  / `"n400"` / `"coherence"` / `"boundary"` / `"prediction"` / `"reinstate"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` -- confirm `track_prediction`
  is default-ON and that a built `SituationReader` binds a callable `sm.predict_next_event`; skim `hdlab/` so you build ON
  the existing organs, not beside them.
- READ IN FULL (build ON it, credit it): `notes/problems/predictive_inference_forward_project_the_next_event_and_state_
  from_the_situation_model/{PROBLEM.md, SOLVED.md, OWNER_NOTES.md, research_drill_forward_coherence_wall_2026-09-06.md}`
  and `notes/WALL_MAP_non_brain_foundational_decisions_2026-09-06.md` (the dominant-finding section + FORWARD PLAN step 2).
- INSPECT what you REUSE: `hdlab/n400_coherence_monitor.py` (`N400CoherenceMonitor`, `segment`, the backward-gist error +
  hard reset); `hdlab/generalized_event_knowledge.py` (`GEKProjector.score` / `.project` / `.expected`); `hdlab/situation_
  reader.py` `_read_prediction` + the `predict_next_event` closure + `sm.forward_prediction`; `hdlab/predictive_reader.py`
  (the word/feature-level forward predictor, Altmann-Kamide -- the STRETCH's parse-side cue); `hdlab/graded_competition.py`
  (the keep-alternatives competition the STRETCH feeds); `experiments/exp_forward_event_predictive_loop_v1.py`
  (`forward_error_segment`, `backward_error_segment` -- the EXACT measured forward-vs-backward comparison) +
  `data/exp_forward_event_predictive_loop_v1/metrics.json`.
- READ the audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` Tier 5 (prediction / event-segmentation) -- the SOLVED's AUDIT
  UPDATE recommending the error be taken against the forward prediction + a swept lambda reinstatement, and the
  `predictive_reader` / `n400_coherence_monitor` "four levels of prediction error, three are islands" entries.
- ENUMERATE the wiring reality (an absence claim requires an enumeration, not a search): grep for every LIVE consumer of
  `n400_coherence_monitor` (`grep -rin "n400_coherence_monitor\|N400CoherenceMonitor\|from hdlab.n400" hdlab/ experiments/
  verification/`) to confirm it is an ISLAND (so the redirect regresses nothing live), and confirm `predict_next_event` is
  bound only as the additive default-on closure. State how you enumerated in your submission.
- GOLD: you are PRE-AUTHORIZED to acquire an open MODERN gold under `data/corpora/<name>/` with a REPRODUCIBLE pinned
  fetch script in `experiments/` + a provenance note. For COHERENCE discrimination, Story Cloze (2016; already on disk at
  `data/corpora/story_cloze`) is a modern gold -- but heed the SOLVED's caution: it carries a Schwartz-2017 STYLE artifact,
  so the CROSS-CONTEXT twin (not a mere order-shuffle) is the load-bearing control. For EVENT SEGMENTATION, prefer a
  HUMAN-annotated modern narrative event-boundary gold (e.g. published cognitive-neuroscience boundary annotations over
  modern narrative -- Baldassano/Sherlock-style human boundaries, or a modern annotated discourse/scene-segmentation set);
  if none is obtainable, the concatenated-modern-story construction gold (as the SOLVED loop cell used) is admissible ONLY
  as a construction control, LABELLED as such, with the shuffled-stream twin -- it is NOT the load-bearing modern annotated
  benchmark. State provenance + license + n; note any genre confound. Do NOT lean on 19c because it is better-powered.

## 7. THE BAR
PASSES only with ALL of:
1. **The loop CLOSED as a glass-box wire (built + validated in `experiments/`; strategy lands the hdlab change, Q111).**
   Redirect the coherence / segmentation ERROR to be taken against the FORWARD prediction (`sm.predict_next_event` /
   `GEKProjector` forward expectedness) instead of the backward running gist, and UPDATE the situation model at a boundary
   by REINSTATEMENT (carry a decayed context forward, lambda ~ 0.2-0.3, SWEEP) rather than a hard reset. Copy the
   predictive-coding / EST COMPUTATION (forward prediction -> error -> reinstate/reset); SWEEP lambda, tau, the baseline
   decay. NO external LLM.
2. **The forward-error loop beats the current BACKWARD-gist monitor CI-separated on a MODERN gold, on BOTH slices,
   reported separately AND aggregated:** (a) COHERENCE discrimination and (b) EVENT SEGMENTATION. The FLOOR is the
   incumbent BACKWARD-gist monitor recomputed on the SAME population (the strongest floor actually run -- it is the live
   path this must beat), plus a random-boundary floor for segmentation; gate on the floor's UPPER CI bound. Report CI
   half-width + null p95; recompute each floor on the item's OWN population; NO number crosses populations.
3. **The info-free twin LOSES CI-separated:** shuffle the FORWARD prediction (score the arriving content against a RANDOM
   other context's forward prediction, and/or temporally-shuffle the stream), keeping shapes / balance -- this proves the
   loop uses THIS story's forward expectation, not a shape artifact. (For the Story Cloze coherence slice, the
   CROSS-CONTEXT twin is the load-bearing one that defeats the style artifact, per the SOLVED.)
4. **NO-regress on the existing coherence path.** The redirect must not degrade any LIVE consumer of `n400_coherence_
   monitor` (enumerate them -- it is currently an island, so confirm), and the reader stays byte-identical where the loop
   is off. A POSITIVE control the backward gist CANNOT get: a mid-stream event boundary where the forward prediction
   spikes but the backward gist has not yet drifted.
5. **Reset-vs-reinstate isolated.** Show mild REINSTATEMENT (lambda ~ 0.2-0.3) beats a hard RESET on the boundary gold and
   that HEAVY reinstatement (e.g. 0.7) HURTS (a can-fail control), reconfirmed on the modern gold's own population -- so
   the reinstatement is load-bearing, not free.
6. **One-screen summary:** forward predictor source -> modern gold + provenance -> backward-gist floor -> twin -> coherence
   + segmentation margins (with CI half-width + null p95) -> reset-vs-reinstate -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the forward-error loop beats the backward gist on the CONSTRUCTION segmentation
gold as measured, but on the MODERN annotated gold the LIVE `sm.predict_next_event` abstains / undercovers on N of M items
because the frozen GEK store covers too little modern narrative content, so the forward error cannot be set and the loop
falls back to the backward gist -- the bottleneck is FORWARD-projection COVERAGE on real prose, enumerated with counts, a
distinct upstream organ"; OR "the coherence slice clears the backward gist CI-separated but the segmentation slice does
not, because the reader's event boundaries on real prose are driven by SPATIAL/character shifts the content-only GEK
forward prediction is blind to -- located and counted").
**STRETCH (name it, do NOT require it):** feed the top-down forward expectation as a PRECISION-WEIGHTED cue into (a) the
parse attachment competition (`graded_competition` -- the PATIENT arc the wall-map shows loses to a hard-commit) and (b)
the meaning re-resolution competition, and show it lifts who-did-what and/or WSD on a modern gold. This is the wall-map's
FULL recurrent-loop closure -- the deeper prize; report it as an additional arm if you reach it.

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated / landed -- do NOT rebuild):** `hdlab/n400_coherence_monitor.py` (the backward-gist monitor to
  redirect); `hdlab/generalized_event_knowledge.py` (`GEKProjector` -- the forward projector); `hdlab/situation_reader.py`
  (`_read_prediction`, the `predict_next_event` closure, `sm.forward_prediction`); `hdlab/predictive_reader.py` (word-level
  forward predictor -- STRETCH parse-side cue); `hdlab/graded_competition.py` (the competition the STRETCH feeds).
- **CONSUME (the measured payoff -- do NOT re-derive):** `experiments/exp_forward_event_predictive_loop_v1.py`
  (`forward_error_segment` / `backward_error_segment`) + `data/exp_forward_event_predictive_loop_v1/metrics.json`.
- **Gold:** Story Cloze on disk (`data/corpora/story_cloze`) for the coherence slice (use the cross-context twin); acquire
  a MODERN human-annotated event-boundary gold under `data/corpora/<name>/` with a pinned fetch script in `experiments/`
  for the segmentation slice (a concatenated-modern-story construction gold is a construction control only, labelled).
- **Motivation + fence:** `notes/WALL_MAP_non_brain_foundational_decisions_2026-09-06.md`; the SOLVED loop cell + its
  research drill; the audit Tier 5 AUDIT UPDATE. Build in `experiments/` + `verification/`; strategy lands any hdlab change
  (Q111). Heavy -> REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` Tier 5 (the predictive-coding loop is now CLOSED and measured on a modern gold, or a
  located negative naming the coverage bottleneck).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the loop cell's segmentation F1 0.766-0.806 vs backward-gist 0.272 (or coherence 0.5922 vs 0.5377) as a
  MODERN annotated-benchmark result -- it was measured on CONCATENATED ROCStories (story-start boundaries) + Story Cloze
  val, in an experiment cell. It is the MOTIVATING measurement that names the loop-closure direction; the bar requires a
  MODERN gold with the twin + no-regress, backward-gist floor recomputed on the item's own population. No number crosses
  scorers / populations.
- Do NOT re-derive the forward projector, `sm.predict_next_event`, or the `n400_coherence_monitor` EST machinery -- all
  are landed. The ingredients are the forward prediction + the backward monitor; the deliverable is CLOSING the loop
  (redirect the error + reinstate) and proving it on a modern gold.
- Do NOT re-open "does the forward projection beat a 1-step co-occurrence counter" -- that is the SOLVED's located
  negative (the projector's absolute discrimination), a DIFFERENT question from forward-error-vs-backward-gist. This
  problem is about which prediction the error is taken against, not beating a counter.
- Do NOT hard-RESET if reinstatement wins (but SWEEP lambda; do NOT adopt 0.3 blindly). Do NOT lean on a 19c corpus as
  load-bearing gold (BANNED 2026-09-06 -- a 19c number is informational only); do NOT use an external LLM at inference (the
  invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** Our reader just learned to guess what comes next in a story, but the part that measures surprise
still checks each new sentence against a summary of what it already read, not against that forward guess -- so the
guess-then-check loop the brain runs is only half-connected. Finish connecting it: make the surprise signal measure the
gap between the forward guess and what actually arrives, and when it decides a new scene has started, carry the recent
context gently forward instead of wiping it. A rough test already showed this makes the reader about three times better at
spotting where one event ends and the next begins. The job is to wire that loop properly and prove on MODERN test text
that the forward-guess version beats the current backward-summary version -- with a scrambled-guess version falling apart,
so we know the real guess is doing the work.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm `sm.predict_next_event` is live and that
`n400_coherence_monitor` is an unwired island taking its error backward), reads the forward-projection SOLVED and the
wall-map in full, acquires a modern coherence + event-segmentation gold (Story Cloze on disk for coherence; a pinned fetch
for a modern boundary gold) with an info-free shuffled-forward twin, builds the closed loop in `experiments/` (redirect the
error onto the forward prediction + reinstatement lambda ~0.2-0.3), and reports the margin over the backward-gist monitor
on both slices with CI half-width + null p95 and the reset-vs-reinstate control -- or a located negative naming the exact
cause (most likely forward-projection coverage on real prose). The STRETCH (forward expectation into the parse + meaning
competitions) is named as the deeper follow-on.
