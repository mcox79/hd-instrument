---
slug: theory_of_mind_is_proven_only_in_a_synthetic_microworld
status: INTEGRATED
review: EXCELLENT
review_text: RESTORED 2026-09-08 (the untracked PROBLEM.md was lost to a git/session op; SOLVED.md intact + committed at 0a65fbb1f). Reconstructed faithfully from the SOLVED. The ToM false-belief organ was de-islanded onto REAL text + the substrate's OWN FHRR organs: per-agent belief partition solves false belief 1.000 CI-sep over the shared-reality floor 0.357 + always-initial 0.643 + twin 0.429; live (text-read observation) 0.821 CI-sep; residual = the observation-cue front-end.
---

> **⚠️ RESTORED 2026-09-08 by the strategy session.** This strategy-owned PROBLEM.md was untracked and lost to a concurrent git/session op; the SOLVED.md survived (committed `0a65fbb1f`, "strategy: integrate theory-of-mind (EXCELLENT)"). Reconstructed faithfully from the SOLVED.md so the folder is complete + tracked. The problem is INTEGRATED (see the review above + SOLVED.md).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate, not the fastest green check.
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure/circuit + the computation and replicate that OPERATION first.
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name structure+computation; PINNED vs OUR-INVENTION; research where unsure.
> 2. **REUSE -- does an existing organ already do it?** Extend rather than re-derive.
> 3. **GENERALIZE -- does it need to, and HOW does the brain?**
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** A located negative counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation; SWEEP (never adopt) parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where along the chain do we lose signal? Itemized mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map their capabilities/limits/brain-status -- seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + FULLY brain-foundational? Else keep pushing.
>
> **(PHASE DIAGRAM)** the operating point (density/dim/binding/capacity/gain/indexed-vs-superposed) is FREE to SWEEP per organ; a wall at one config = MOVE the operating point before calling it a ceiling.
> **(FULL-STACK UPSTREAM)** prototype THIS component AND its upstream to EXCEL+EXCEED; confirm no downstream regress; research the upstream is genuinely brain-foundational.

> ## SOLVER REVIEW -- EXCELLENT (integrated; see SOLVED.md + commit 0a65fbb1f)
> The HARD_PASS-but-SYNTHETIC Sally-Anne false-belief organ was DE-ISLANDED onto REAL English narrative, run on the substrate's OWN FHRR organs (`hdlab.binding.bind/unbind` + `situation_model_accumulate.cleanup_argmax`, codes seeded from TEXT surface forms) -- NOT hand-rolled numpy, NOT a symbolic codebook. Per-agent belief partition solves false belief **1.000 [1.000,1.000]** (false-belief 1.00, true-belief 1.00, reality 1.00), CI-separated over the shared-reality floor (0.357 -- leaks the observer's knowledge to the agent), the trivial always-initial floor (0.643), and an info-free scrambled-observation twin (0.429). With the observation cue READ FROM TEXT it still scores **0.821 [0.679,0.964]**, beating the floor CI-sep; the FULL_TOM(oracle) - LIVE gap localizes the only residual to the observation-cue front-end (filed: `theory_of_mind_residual_is_the_observation_cue_front_end`). Controls are rigorous (true-belief saw/told, divergent two-agent, reality-intact, interference stress). `hdlab/state_of_mind.py` NOTED mislabelled (it is coreference, zero belief logic -- the live reader has no actual belief tracking; the belief timeline is a separate DEBT-1/2 organ).

# PROBLEM: the substrate's Theory-of-Mind (false-belief) organ is HARD_PASS but ONLY in a synthetic symbolic microworld (islanded, hand-rolled numpy, a perfect symbolic codebook) -- de-island it per its own revival criteria: prove the per-agent belief partition recovers FALSE beliefs on a DIVERGENT-belief NARRATIVE task, run on the substrate's OWN FHRR organs (not hand-rolled numpy), with inputs from TEXT (not a codebook), beating the shared-reality floor (which leaks the observer's knowledge to the agent) CI-separated, with an info-free twin LOSING and true-belief controls preventing an always-initial shortcut.

**slug:** `theory_of_mind_is_proven_only_in_a_synthetic_microworld` -- **opened:** 2026-08-26 by the strategy session (self-scoped pickup of the orphaned ToM island, owner-directed). **status:** INTEGRATED (EXCELLENT).

## 1. THE PROBLEM IN PLAIN LANGUAGE
Understanding that another person can believe something FALSE (they think the ball is in the basket because they didn't see it moved) is Theory of Mind — a core part of reading. Our system could do this, but only in a toy, made-up world with hand-written math and perfect labels. The job: prove it works on REAL English stories, using the system's own memory machinery, reading the clues from the text — and show it genuinely tracks each character's separate belief, not just the true state of the world.

## 2. WHY THIS ONE
Theory of Mind was the substrate's most-cited "we can't do this on real text" gap; the organ existed but was islanded + synthetic. De-islanding it proves the per-agent belief mechanism is REAL and portable (runs on the shared FHRR organs), and localizes the true remaining gap (reading "did the agent see it?" from text) for a focused follow-on.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: Theory of Mind maintains a SEPARATE mental model per agent (the TPJ/mPFC ToM network; Sally-Anne false-belief; Baron-Cohen; Leslie). A false belief is an agent's STALE representation of the world — the agent who did not observe a change keeps their old binding while reality updates. The computational analog: a per-agent belief bank in the SAME vector-symbolic store the reader uses (bind agent×location; an unobserved change leaves the agent's binding stale). OUR-INVENTION-UNDER-TEST: the observation-cue extractor (did the agent see/get told of the move?), the code seeding from text surface forms.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the synthetic Sally-Anne organ is HARD_PASS (Q2 0.806 vs 0.138, oracle 1.0, 5 seeds) but SYNTHETIC (perfect codebook), ISLANDED, hand-rolls bind/unbind in numpy.
- **INFERRED (measured by this problem):** whether the per-agent partition holds on REAL narrative, on the substrate's OWN organs, with TEXT inputs, beating the shared-reality + always-initial floors CI-sep with the twin losing. RESULT: yes — 1.000 (oracle observation) / 0.821 (text-read observation), CI-sep; residual = the observation-cue front-end.

## ALREADY TRIED / DO NOT REDO
- The synthetic symbolic microworld (`theory_of_mind_sally_anne_nested_hrr`) — HARD_PASS but islanded/hand-rolled; the thing this de-islands. Do not re-run it as a real-text claim.
- The higher-order recursive ToM line (`exp_substrate_higher_order_tom_recursive_v1..v4`) — a DIFFERENT, synthetic, MIDDLE_BAND effort; not a duplicate of this first-order real-text result.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Reproduce first-hand: `.venv/Scripts/python.exe verification/test_theory_of_mind_realtext.py` (witness 2/2).
- Read the SOLVED.md in this folder in full; inspect `experiments/exp_theory_of_mind_realtext_v1.py` + `experiments/data/gold_false_belief_realtext_v1{,b}.jsonl` (26 real-text false-belief passages) + `hdlab.binding` / `hdlab.situation_model_accumulate` (the organs it runs on).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = the per-agent belief partition, run on the substrate's OWN FHRR organs with TEXT inputs, recovers false beliefs on a divergent-belief narrative task and beats the shared-reality floor (leaks observer knowledge) CI-separated, info-free (scrambled-observation) twin LOSING, true-belief controls (saw/told) preventing an always-initial shortcut, reality questions intact. MET: 1.000 (oracle observation) CI-sep over floors 0.357/0.643/0.429; 0.821 live (text-read observation) CI-sep; the residual localizes to the observation-cue front-end.

## FILES AND ENTRY POINTS
`experiments/exp_theory_of_mind_realtext_v1.py`, `experiments/data/gold_false_belief_realtext_v1{,b}.jsonl`, `verification/test_theory_of_mind_realtext.py`, `data/exp_theory_of_mind_realtext_v1/metrics.json`. Runs on `hdlab.binding` + `hdlab.situation_model_accumulate` (the substrate's own organs). hdlab/ UNTOUCHED at solve time (Q111 proposed diff in the SOLVED). Follow-on: `theory_of_mind_residual_is_the_observation_cue_front_end`.

## DO NOT QUOTE
- Do NOT quote the synthetic microworld's 0.806 as a REAL-TEXT number — real-text is 1.000 (oracle) / 0.821 (text-read).
- Do NOT quote the ORACLE 1.000 as the LIVE number — live (observation read from text) is 0.821; the gap is the observation front-end.
- Do NOT treat `hdlab/state_of_mind.py` as belief tracking — it is coreference (mislabelled); the live reader has no belief tracking here.
