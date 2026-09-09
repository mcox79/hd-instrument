---
priority: 5
slug: replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop
status: OPEN
review:
review_text:
---

# PROBLEM: in the FOUNDATION / grounding-acquisition subsystem (live via `hdlab/reading_grounding_loop.py` / `substrate.py` / `gap_driven_reader.py`, consuming `gap_detector`→`cleanup_family`), the concept-cleanup step uses a `sign()`-quantized iterative ATTRACTOR (`hdlab/cleanup_family.py` `classical_hopfield`/`modern_hopfield_continuous`/`iterative_attractor`) as a GRADED SIMILARITY RANKER. That is the wrong brain computation: attractor dynamics are for pattern-COMPLETION / RECOGNITION (Hopfield energy descent to the nearest stored pattern; Marr 1971 CA3 auto-association), NOT for producing a graded ranking of candidates — the `sign()` quantization + energy descent re-promotes high-degree concept HUBS and destroys the graded distances a ranking needs (the reader-audit catalogued this as C7, MEDIUM blast, "active harm in the grounding-acquisition pipeline"). REPLACE the attractor-as-ranker with a brain-foundational GRADED POPULATION READ for the ranking step (a graded similarity / population-vector readout that preserves distances), and RESERVE the attractor for the recognition/recall step where pattern-completion is the right job — measured on the grounding loop's OWN ranking metric, with the info-free twin losing and no regression to the recall path. NOT a change to `situation_reader.read()` (C7 is dormant there). NOT raising a threshold on the same quantized metric. Glass-box, NO external LLM.

**slug:** `replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop` — **opened:** 2026-09-09 by the strategy session, from the reader-audit's disk-verified C7 catalog entry (owner-DONE `audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements`). **status:** OPEN. A single LOCATED live stand-in with a named brain-foundational replacement — buildable in parallel with the broader grounding-subsystem audit (it does not wait on that map). Strategy lands any hdlab change (Q111); the solver builds the graded-read replacement + the ranking-metric evaluation + the witness in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant).

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
When the substrate reads to grow its knowledge, it constantly has to ask "which stored concept is this new thing most like?" and rank the candidates. Right now it answers that by running an ATTRACTOR — a process that snaps to the single nearest stored memory and, along the way, throws away the fine gradations by rounding everything to +1/−1. That is the brain's machine for RECOGNISING ("I've seen this before, it's X") and for RECALLING a full memory from a partial cue — a great tool for the wrong job here. Using it to RANK how similar things are both loses the graded distances a ranking needs and keeps snapping to over-connected "hub" concepts, so the ranking is systematically distorted. The fix is to use the brain's actual ranking machinery — a graded population read that keeps the distances — for ranking, and keep the attractor for recognising/recalling, where it belongs.

## 2. WHY THIS ONE — a located live stand-in that gates the learner, under the HARD gate
Under the owner's 100%-brain-foundational HARD gate, a live component running the WRONG brain computation is a DEFECT that blocks — regardless of whether it currently moves a board dim. This one is disk-located (reader-audit C7, W7): `gap_detector`→`cleanup_family` is live in the grounding-acquisition pipeline, and `cleanup_family`'s ranking primitives (`classical_hopfield`, `modern_hopfield_continuous`, `iterative_attractor`) are `sign()`-quantized attractors used as a similarity ranker. Because this pipeline is the learn-by-reading / grow-the-foundation pathway (the north-star knowledge program), a distorted concept ranking there caps every future grounding gain and would corrupt the learner's propose-verify growth. It is a clean, self-contained fidelity fix with a NAMED brain-foundational replacement — ideal parallel work for an idle solver while the broader subsystem audit runs.

## 3. MEASURED vs INFERRED
- **MEASURED (on-disk):** `cleanup_family.py` `classical_hopfield` does `s_next = np.sign(W @ s)` (L130), `modern_hopfield_continuous` does `np.sign(s_mix)` (L179), `iterative_attractor` wraps `iterative_cleanup` (L201) — sign-quantized energy-descent attractors; the reader-audit (owner-DONE, 30/30 pure-disk witness) classified C7 as a LIVE attractor-as-RANKER in the grounding loop, MEDIUM blast, "re-promotes high-degree concept hubs and hurts semantic ranking" (CONT-28 #3 corroborated). The sign-quantiser's averaging-machine failure is a separately-recorded finding (`the_sign_quantiser_makes_the_substrate_an_averaging_machine`).
- **INFERRED (the bet to test):** that a graded population read (distance-preserving similarity readout — e.g. a normalized graded cosine / population-vector decode, no sign-quantization, hub-corrected) beats the sign()+attractor ranker on the grounding loop's OWN ranking metric CI-separated, WITHOUT regressing the recall/recognition path (where the attractor stays). The solver must MEASURE the ranking metric on the live loop (not a synthetic proxy) and show the info-free twin (shuffled codebook / random ranker of equal size) losing, and hub-degree is no longer over-promoted.

## 4. ALREADY TRIED / DO NOT REDO
- Do NOT "fix" this by raising a threshold or changing `temp`/`beta` on the SAME sign-quantized attractor output — the located defect is that an attractor is the wrong COMPUTATION for ranking, not a mis-tuned parameter (PHASE-DIAGRAM note: sweep parameters of the RIGHT computation, do not tune the wrong one).
- Do NOT remove the attractor entirely — pattern-completion / recognition / recall IS its correct brain job (Hopfield; Marr CA3); this problem only re-routes the RANKING step off it. Preserve the recall path byte-identical-or-better.
- Do NOT touch `situation_reader.read()` — C7 is DORMANT there (reader-audit W7); the live consumer is the grounding loop. Confirm that before editing.
- Do NOT re-open the sign-quantiser averaging finding (`the_sign_quantiser_makes_the_substrate_an_averaging_machine`, solved) as new — cite it; this is its concrete grounding-loop realization for the ranking step.
- Do NOT reach for an off-the-shelf nearest-neighbour / embedding library as the "graded read" — the readout must be the brain's graded population mechanism, glass-box, in-substrate.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** read the reader-audit's `CATALOG.md` §C7 IN FULL (`notes/problems/audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements/CATALOG.md`) + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b; read `hdlab/cleanup_family.py` + `hdlab/iterative_attractor.py` + `hdlab/gap_detector.py` end-to-end; trace the live consumer chain in `hdlab/reading_grounding_loop.py` / `hdlab/substrate.py` / `hdlab/gap_driven_reader.py`. Understand ALL relevant organs FIRST via `tools/substrate_map.py` / `tools/reader_capabilities.py`.
- CONFIRM FIRST-HAND that the ranking step (not just a recall step) consumes the attractor output in the LIVE loop, and identify the loop's existing ranking/growth-quality metric to grade on — if the ranking is actually served by a graded readout already and the attractor is only doing recall, this is a located NEGATIVE (say so, with the trace).
- CHECK for an existing graded-read organ to REUSE (`hdlab/modern_hopfield_readout.py`, the `no_cleanup`/`k_NN_lookup`/`flat_topk_readout` paths in `cleanup_family.py`, `hdlab/convergent_cue_reader.py`) before building a new one.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
PASS = a brain-foundational GRADED POPULATION READ replacing the sign()+attractor as the RANKING step in the grounding-acquisition loop, that beats the incumbent attractor-as-ranker CI-separated on the loop's OWN ranking / growth-quality metric (its real live measure, not a synthetic proxy), with (a) the info-free twin (shuffled codebook / random ranker of equal size) LOSING, (b) high-degree-hub over-promotion MEASURABLY reduced (the named failure mode), and (c) the recall / recognition path (the attractor's correct job) byte-identical-or-better — NO regression. A rigorous LOCATED NEGATIVE is a full pass IF it names, with a number, exactly why the graded read cannot beat the attractor here (e.g. the loop's ranking is already graded and the attractor only does recall, or the metric is saturated) — quantify it. Strategy lands the hdlab change (Q111) on your witnessed diff.

## 7. FILES AND ENTRY POINTS
- The defect: `hdlab/cleanup_family.py` (`classical_hopfield` L107-153 `np.sign(W@s)` L130; `modern_hopfield_continuous` L155-199 `np.sign(s_mix)` L179; `iterative_attractor` L201-226) + `hdlab/iterative_attractor.py` (`iterative_cleanup`).
- The live consumers: `hdlab/gap_detector.py` → `cleanup_family`; driven by `hdlab/reading_grounding_loop.py`, `hdlab/substrate.py`, `hdlab/gap_driven_reader.py`.
- Graded-read organs to REUSE / extend: the `no_cleanup` / `k_NN_lookup` / `flat_topk_readout` paths in `cleanup_family.py`; `hdlab/modern_hopfield_readout.py`; `hdlab/convergent_cue_reader.py`.
- Recall/recognition organs (the attractor's correct home — do not disturb): `hdlab/ca3_completer.py`, `hdlab/dg_pattern_separation.py`, `hdlab/hippocampal_encoder.py`.
- Reference: `notes/problems/audit_the_live_substrate_.../CATALOG.md` §C7; `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.
- New work: `experiments/exp_graded_read_vs_attractor_ranker_v1.py`, `verification/test_graded_read_ranker.py`.

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT quote the reader-audit's "MEDIUM blast" as a board-dim claim — C7's blast is the grounding loop's ranking, NOT a `situation_reader` board dimension; grade on the loop's own metric (a board-invisible fidelity win is still a PASS under the HARD gate).
- Do NOT quote attractor recall accuracy as evidence the ranker is fine — recall and ranking are different jobs; the defect is specifically the ranking use.
- Do NOT report a graded-read win that was actually measured on a synthetic codebook detached from the live loop — the bar is the LIVE loop's ranking metric.
- Do NOT use an external LLM / off-the-shelf ANN library at inference (THE invariant); the graded read must be the brain's in-substrate population mechanism.
