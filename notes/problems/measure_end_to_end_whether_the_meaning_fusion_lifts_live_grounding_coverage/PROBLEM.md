---
priority: 5
slug: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage
status: OPEN
review:
review_text:
---

# PROBLEM: the C7 solver PROVED that reading the grounding-loop's sense-assignment RANKING over a reliability-weighted convergent FUSION (grounded + distributional + is-a/taxonomic identity) beats the distributional incumbent CI-separated — but ONLY on the sense-assignment RANKING PROXY (vs the independent SimLex gold). It was NEVER measured on the live loop's actual OUTCOME: does the fusion, wired into `reading_grounding_loop.canonicalize_fast`, actually raise the loop's downstream GROUNDING-COVERAGE GROWTH on a real read? The solver flagged this as "the one measurement not yet done" and, per measure-impact-first / no-more-default-off, the fusion-wire must NOT be flipped live until this transfer is proven. Build the end-to-end grounding-coverage measurement (info-free twin losing) and PROVE or REFUTE the transfer, WITH A NUMBER. Glass-box, NO external LLM at inference.

**slug:** `measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage` — **opened:** 2026-09-09 by the strategy session, from the integrated C7 solver (`replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop`, STRONG) — its NEXT STEP #3, "the one measurement NOT yet done," and the explicit gate on its biggest live lever (the fusion-wire, which strategy is holding until this measurement exists). **status:** OPEN. The solver builds the end-to-end grounding-coverage measurement + the fusion prototype + the witness in `experiments/`, `verification/`, and this folder (a faithful harness of `canonicalize_fast`'s read; NO hdlab write — strategy lands the live wire IFF this proves net-positive, Q111). Glass-box, NO external LLM at inference (the invariant).

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
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model
> are NOT brain-foundational -- never reach for a convenient/easy tool without careful consideration (a vetted static
> offline FOUNDATION asset is admissible; an external tool AT INFERENCE or a fitted/convenient stand-in is a DEFECT
> that BLOCKS).**
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
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The system grows its grounded vocabulary by READING: for each new word it decides which known concept the word means (sense assignment) and grows its knowledge from there. A prior result showed that if it makes that "which concept" decision using a richer, brain-like BLEND of meaning evidence (perceptual grounding + word-context + "is-a / same-kind" identity) instead of just word-context, it picks the right concept far more often — measured on a stand-in ranking test against independent human similarity ratings. But that is a STAND-IN. The thing we actually care about is whether, over a real reading pass, that better decision makes the system LEARN MORE — grow more, correct, grounded concepts (coverage) — and not just score better on a side test. Nobody has measured that yet, and until we do we will not flip the change on. Build the real end-to-end measurement: wire the blended decision into the live reading-grounding loop, read a real corpus, and measure whether grounding coverage actually GROWS, with a shuffled/info-free version losing. If it does NOT transfer, say so with a number — that is just as valuable (it stops us flipping a change that only helps a proxy).

## 2. WHY THIS ONE — the gate on the biggest live meaning lever, under the HARD 100%-BF gate
The C7 solver's fusion win is the single biggest identified lever on the grounding loop's meaning decision (MRR 0.024 → 0.081 CI-sep on the ranking proxy; knowledge moves the bar ~214×). Strategy is deliberately HOLDING the live fusion-wire into `canonicalize_fast` because the win is proven only on the sense-assignment RANKING, not the live loop's OUTCOME — and the project rule is measure-impact-first / no-more-default-off (a proxy win is not a live win; do not flip on faith). This problem IS that measurement. It is the difference between "proven on a side test" and "proven on the job," and it unblocks a landing that touches the whole grow-by-reading north-star. It is also a clean can-fail: a rigorous REFUTE (the ranking win does not transfer to coverage) is a full pass and saves the substrate from a bad flip.

## 3. MEASURED vs INFERRED
- **MEASURED (integrated C7 solver, reverified 23/23 — disk facts):** on the loop's OWN sense-assignment RANKING vs the independent SimLex-999 gold, the reliability-weighted convergent fusion (grounded + distributional [+ is-a/taxonomic identity]) beats the distributional incumbent CI-sep (MRR 0.0241 → 0.0812, +0.0571 CI[+0.0335,+0.0834]; grounded-alone +0.0396; info-free twins lose 0.0013/0.0009); the all-BF equal-weight composition (no fitted params) beats the mixed chain +0.028 CI-sep. Recall/recognition path byte-identical (only the ranking's input representation changed).
- **INFERRED (what THIS problem must MEASURE, not assume):** that the ranking improvement TRANSFERS to the live loop's downstream GROUNDING-COVERAGE GROWTH on a real read. The C7 solver states plainly: "NOT an end-to-end grounding-coverage run … the first thing I would withdraw is any implied coverage-growth number." So the transfer is UNMEASURED — prove or refute it.

## 4. ALREADY TRIED / DO NOT REDO
- The RANKING proxy is DONE (`exp_sense_assignment_grounded_vs_distributional_v1.py`): the fusion beats the incumbent on the sense-assignment ranking. Do NOT re-run the ranking proxy as the deliverable — the OPEN question is coverage TRANSFER on the live loop.
- The attractor-as-RANKER swap is a measured NO-OP (C7 located negative) — the ranking is already a graded population read; do NOT reintroduce an attractor as the ranker.
- Coarse discourse typing over-licenses (measured negative in adjacent work) — if you add an is-a/identity channel, use the FINE grain, not a coarse PLACE/PERSON flag.
- Do NOT wire anything into live `hdlab/` (Q111) — build a faithful harness of `canonicalize_fast`'s read and measure; strategy lands the live wire IFF you prove net-positive.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reverify the C7 result first-hand: `.venv/Scripts/python.exe verification/test_graded_read_ranker.py` (23/23). Read `notes/problems/replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop/SOLVED.md` IN FULL (esp. §"The hdlab proposal" + §"What I did NOT establish" + NEXT STEP #3) + `BF_AUDIT.md`.
- Read the live loop: `hdlab/reading_grounding_loop.py` (`canonicalize_fast` = the graded cosine population read; `identify_missing_prerequisites` = candidate ranking; the FLAG→LIBRARY→CONSOLIDATE→GATE→BANK→PROMOTE growth architecture) + its measurement harness `experiments/exp_reading_grounding_loop_cycle1_v1.py` (corpus loading, curriculum ordering, controls, the COVERAGE metric it already scores — reuse it). Read `hdlab/grounded_similarity.py`, `hdlab/conceptual_meaning.py`, `hdlab/convergent_cue_reader.py` (the landed Bayes fusion).
- Prior-work check: `python tools/experiment_index.py query "grounding coverage"` / `"reading grounding loop"`; `tools/substrate_map.py`. NOTE the adjacent OPEN pri-4 `audit_the_grounding_acquisition_subsystem` (the same subsystem) + the INTEGRATED located-negative `the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation` (growing meaning-from-reading did NOT lift WSD — a DIFFERENT metric; do not conflate, but understand why it failed there before claiming coverage transfer here).
- Threads: cap OMP/OpenBLAS/MKL/NumExpr=2 for reproducibility.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
PASS = an END-TO-END measurement on the LIVE reading-grounding loop (a faithful harness of `canonicalize_fast`'s read over the real reading corpus, curriculum-ordered as the loop does it) showing whether reading the sense-assignment ranking over the reliability-weighted convergent fusion (grounded + distributional [+ is-a/taxonomic identity], the landed `convergent_cue_reader` Bayes rule, weights/taus calibrated OFFLINE + held-out) changes the loop's OWN downstream GROUNDING-COVERAGE GROWTH metric — with (a) the INFO-FREE TWIN (shuffled representation rows) LOSING, (b) the recall/recognition path byte-identical, (c) the number reported with a CI on the loop's own metric/population (no cross-population/scorer number). A CI-SEPARATED lift is a landable win (hand strategy the wire spec). A rigorous LOCATED NEGATIVE — the ranking win does NOT transfer to coverage — is a FULL PASS if it names, WITH A NUMBER, exactly why (e.g. coverage is gated by candidate GENERATION not sense SELECTION; or the loop's coverage is exposure-bound not decision-bound), and, per the protocol, then builds the stronger brain version and tests THAT before concluding. Leave room to solve the coverage lever a DIFFERENT, more brain-faithful way if the fusion is not it.

## 7. FILES AND ENTRY POINTS
- **The C7 evidence + proxy harness:** `notes/problems/replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop/{SOLVED.md,BF_AUDIT.md,KNOWLEDGE_LEVER.md}`; `experiments/exp_sense_assignment_grounded_vs_distributional_v1.py` (the fusion + held-out calibration + twins), `experiments/exp_all_bf_chain_v1.py` (equal-weight all-BF fusion), `experiments/exp_richer_meaning_channel_v1.py` (the +is-a/taxonomic identity channel).
- **The live loop (the thing to measure):** `hdlab/reading_grounding_loop.py` (`canonicalize_fast`, `identify_missing_prerequisites`, the grow architecture + its COVERAGE metric); `experiments/exp_reading_grounding_loop_cycle1_v1.py` (the loop's measurement harness — corpus, curriculum, controls, coverage). Meaning organs: `hdlab/grounded_similarity.py`, `hdlab/conceptual_meaning.py`, `hdlab/meaning_foundation.py`, `hdlab/convergent_cue_reader.py`.
- **Build in `experiments/` + `verification/` + THIS folder only. NO `hdlab/` writes (Q111).** Tag mechanism cells with `__bf_status__` (keep `verification/test_bf_status_tags.py` green). `SOLVED.md` with bar/result/floor/controls/reverify + TLDR / QUESTIONS / NEXT STEPS.

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT quote the C7 sense-assignment RANKING MRR as if it were a coverage number — they are different populations/metrics; the whole point is to measure coverage transfer freshly.
- Do NOT flip / write the live `canonicalize_fast` wire yourself (Q111) — MEASURE with a faithful harness; strategy lands the wire iff you prove net-positive.
- Do NOT reintroduce an attractor as the ranker (C7 located negative), and do NOT use a coarse PLACE/PERSON discourse-type flag for the is-a channel (measured over-licenses); use the fine grain.
- Do NOT use an external LLM / transformer / off-the-shelf model at inference; a vetted static offline FOUNDATION asset (the curated grounded norms / sense signatures / is-a taxonomy) is admissible.
