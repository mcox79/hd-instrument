---
slug: audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins
status: INTEGRATED
review: STRONG
review_text: "Rigorous runtime import+call-trace audit of the grounding-acquisition subsystem (16 LIVE-CALLED / 23 LIVE-INERT / 6 DORMANT, positive control fired), reverified 15/15 first-hand. 4 live stand-ins + 3 corrections; #1 (G1: the meaning read-out is a bag-of-words co-occurrence cosine that LOSES to word-counting on the loop's own metric) is localized as a MIS-SPECIFIED-objective-over-ungrounded-input dissociation. Leakage-guarded prototyped fix takes the read-out 6%->86% of human (multimodal ATL hub + coverage-aware fusion + a MEANING objective), measured on a SimLex PROXY not the live loop. CONVERGES with pri-2 (population-code) + pri-5 (grounding-coverage measurement = its live-loop test) + the C7 line. Integrated 2026-09-09: CATALOG recorded as the authoritative grounding-subsystem reference, §2b folded, corrections adopted; the hdlab wire is a careful measured landing gated on pri-5. NO hdlab writes by the solver (map)."
---

# PROBLEM: the reader-audit (`audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements`, owner-DONE) catalogued only the organs `situation_reader.read()` consumes — but the substrate has a SECOND live entry point it explicitly excluded: the FOUNDATION / GROUNDING-ACQUISITION subsystem (the learn-by-reading / grow-the-knowledge pathway: `hdlab/reading_grounding_loop.py`, `hdlab/substrate.py`, `hdlab/gap_driven_reader.py`, `hdlab/three_tier_loop.py`, `hdlab/grounding_acquisition_loop.py` + what they consume). That pathway is where the owner's 100%-brain-foundational HARD GATE has NOT been swept, and the reader-audit already flagged two live stand-ins there (C7 `cleanup_family`/`iterative_attractor` sign()+attractor-as-RANKER; C8 `hd_fact_store` fact quality — the latter partly solved). PRODUCE the same kind of prioritized, DISK-VERIFIED CATALOG for THIS subsystem: every LIVE non-brain-faithful stand-in / convenient shortcut, five disk-verified fields each, top-K ranked by blast, with a machine-checkable pure-disk witness — reconciled against the actual import closure of the loop's live entry points (NOT stale comments), distinguishing live-defective / live-but-inert / dormant. NOT a re-audit of the reader (done). NOT a full rebuild (this is a MAP + the one deepest fix localized). Glass-box, NO external LLM, NO `hdlab/` writes (Q111 — strategy lands; you deliver the catalog + proposed fixes + a powered localization of the #1 item).

**slug:** `audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins` — **opened:** 2026-09-09 by the strategy session, as the explicit OUT-OF-SCOPE follow-on named by the reader-audit SOLVED.md ("NEW BREADTH FOLLOW-ON: a second breadth pass over the OTHER live entry point"). **status:** OPEN. Strategy lands any hdlab change (Q111); the solver builds the catalog + the localization drills + the witness in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant); a vetted offline FOUNDATION asset IS admissible.

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
The substrate has two ways it runs. One is READING a passage to answer questions — a colleague just went through that whole path and made a ranked list of every place it takes a convenient shortcut instead of working like a brain (the worst: it was peeking at the answer key when grouping people). But there is a SECOND path that never got that treatment: the part that LEARNS — that reads at scale to grow its own store of world knowledge and fill the gaps in what it knows. That learning path has its own shortcuts, and because it is what feeds every future "I learned this by reading" gain, a fake shortcut there quietly caps everything downstream. This problem is: give the learning path the same honest, disk-checked audit — one ranked list of every non-brain-like stand-in in it, each verified against the actual running code (not stale comments), with the single worst one localized precisely and its brain-faithful replacement named.

## 2. WHY THIS ONE — the second live entry point, never swept against the HARD gate
The owner's standing directive is that EVERY live component must be 100%-brain-foundational (a HARD pass/fail gate, not a rating). The reader-audit swept `situation_reader.read()`'s closure and it paid off immediately — it surfaced the #1 gold-coref-inheritance leak (masking the honest 0.155 experiencer floor as a fake ~0.80), plus 7 more ranked stand-ins. But that audit's DENOMINATOR was the reader only; its SOLVED.md explicitly excludes and hands off the FOUNDATION/grounding-acquisition subsystem, and already found two live stand-ins leaking into it (C7 attractor-as-ranker, C8 fact quality). That subsystem is the learn-by-reading / grow-the-foundation pathway — the north-star knowledge program (curated foundation → online propose-verify growth). A non-brain-faithful stand-in there gates every grounding gain, so it must be swept the same way BEFORE the learner is turned on at scale. The value of a breadth audit here is proven high-yield (the reader-audit's payoff) and it is prerequisite hygiene for the whole knowledge-acquisition line.

## 3. MEASURED vs INFERRED
- **MEASURED (on-disk, the reader-audit's disk-verified catalog, 30/30 pure-disk witness):** C7 `cleanup_family`/`iterative_attractor` is a sign()+attractor-as-RANKER (re-promotes high-degree concept hubs, hurts semantic ranking) — DORMANT wrt the reader but LIVE in the grounding loop (`gap_detector`→`cleanup_family`, witness W7); C8 `hd_fact_store` had ~66% tautology/junk facts (partly remediated by `the_knowledge_store_has_no_correctness_or_consistency_cleanup`, INTEGRATED). These are two KNOWN items; the audit's job is the COMPLETE ranked catalog for this subsystem.
- **INFERRED (what this audit must establish):** that the grounding-acquisition subsystem contains a SMALL number of high-blast non-brain-faithful stand-ins whose removal is prerequisite to a safe learner turn-on, and that the deepest is localizable to one component with a powered can-fail drill. The solver MUST re-verify every claimed defect against CURRENT bytes (the reader-audit found several brief-claimed defects were already fixed — "the disk outranks the brief"), and must distinguish a genuine live defect from dead code / a latent-by-design island (do NOT rank a dormant path as a live defect — grep for a REAL live consumer first).

## 4. ALREADY TRIED / DO NOT REDO
- The READER audit is DONE (`audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements`, owner-DONE) — do NOT re-audit `situation_reader.read()`'s closure; INHERIT its catalog and start where it handed off.
- C8 fact-quality cleanup is INTEGRATED (`the_knowledge_store_has_no_correctness_or_consistency_cleanup`) — do NOT re-file "the fact store has junk facts"; instead CONFIRM its state on disk and audit what remains.
- Do NOT propose turning the learner on / running it at scale here (that is `turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation` / `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite`) — this is the AUDIT that must precede it.
- Do NOT re-audit the consolidation-gate design (`build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`, solved) as a defect; assess only its brain-foundational fidelity as an adjacent component.
- Do NOT reach for spaCy / an off-the-shelf parser / an external LLM to "check" the pipeline — the audit is a glass-box disk trace, and any such tool found AT INFERENCE in the subsystem is itself a defect to CATALOG.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** read IN FULL the reader-audit's deliverables (`notes/problems/audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements/{SOLVED.md,CATALOG.md,PARSER_SIGNAL_TRACE.md,PRI1_INTEGRATION_MAP.md}`) — especially its §C7/C8 and its "NEW BREADTH FOLLOW-ON"; then `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b. Understand ALL relevant organs FIRST via `tools/substrate_map.py`, `tools/reader_capabilities.py`, `tools/wiring_debt.py`, and skim `hdlab/`.
- **ESTABLISH THE DENOMINATOR BY ENUMERATION, NOT SEARCH (owner discipline):** derive the grounding subsystem's live import closure from its real entry points — trace what `reading_grounding_loop.py` / `grounding_acquisition_loop.py` / `three_tier_loop.py` / `gap_driven_reader.py` / `substrate.py` actually import and invoke (a runtime import trace + a call trace, NOT a grep of comments — the reader-audit's key lesson was that comments/docstrings lie about default flags and live-ness). State HOW you enumerated and give a POSITIVE CONTROL.
- Confirm C7's live-consumer chain first-hand (`gap_detector`→`cleanup_family` in the loop) before ranking it, and re-verify C8's current fact-store state post-cleanup.

## 6. THE BAR (can-fail; a rigorous catalog with a pure-disk witness IS the deliverable)
PASS = a prioritized, DISK-VERIFIED CATALOG (`CATALOG.md`) of every LIVE non-brain-faithful stand-in in the grounding-acquisition subsystem, each with FIVE disk-verified fields (the brain structure+computation it should implement / why the current thing is not it / the brain-foundational replacement / blast + live-vs-dormant with the consuming file:line / fix class), top-K ranked by blast, denominator = the subsystem's actual live import+call closure (reconciled against flag defaults, not comments), explicitly distinguishing live-defective vs live-but-inert vs dormant — PLUS a powered can-fail LOCALIZATION of the #1 item on the subsystem's OWN metric (the grounding loop's ranking / growth-quality measure), with a machine-checkable pure-disk witness (`verification/test_audit_grounding_subsystem.py`) that reproduces every LIVE/DORMANT classification from disk. NO `hdlab/` writes (Q111). A rigorous located result is a full pass IF it names the ranking with numbers and localizes the deepest fix (or shows, with a positive control, that the subsystem is ALREADY clean — that too is a valid, valuable located result). Do NOT over-fire: a knowledge-supply lexicon or a vetted offline asset is NOT a defect; only an at-inference external tool / a fitted-convenient stand-in / a non-brain computation counts.

## 7. FILES AND ENTRY POINTS
- Subsystem entry points to trace: `hdlab/reading_grounding_loop.py`, `hdlab/grounding_acquisition_loop.py`, `hdlab/three_tier_loop.py`, `hdlab/gap_driven_reader.py`, `hdlab/substrate.py`.
- Known stand-ins to confirm/rank: `hdlab/cleanup_family.py` + `hdlab/iterative_attractor.py` (C7 attractor-as-ranker) via `hdlab/gap_detector.py`; `hdlab/hd_fact_store.py` (C8 fact quality, partly remediated).
- Adjacent (assess fidelity, don't re-solve): `hdlab/prelim_tier.py`, `hdlab/convergent_cue_reader.py`, the consolidation-gate + `hdlab/meaning_foundation.py`, `hdlab/dg_pattern_separation.py` / `hdlab/ca3_completer.py` (recognition/recall organs — the correct home for attractor dynamics).
- Reference: `notes/problems/audit_the_live_substrate_.../{CATALOG.md,SOLVED.md}` (the sibling audit's method + handoff); `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.
- New work: `experiments/exp_audit_grounding_subsystem_v1.py` (the import/call trace + the #1-item localization drill), `verification/test_audit_grounding_subsystem.py`, and `CATALOG.md` in this folder.

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT quote the reader-audit's C7/C8 "LIVE (other path)" line as if it were a full ranking of THIS subsystem — it was a two-item flag from a reader-scoped denominator; the whole catalog is yours to build.
- Do NOT quote any organ's "live" or "default-on" status from a docstring or a comment — the reader-audit found multiple stale defaults ("default-off" docstrings on default-ON flags). Derive live-ness from the actual import+call closure only.
- Do NOT report a dormant / dead-code path as a live defect — that mis-ranks the work (the reader-audit's explicit lesson: "LIVE" has three failure modes; conflating them mis-ranks). Grep for a REAL live consumer first.
- Do NOT use an external LLM at inference (THE invariant); do NOT reach for spaCy / an off-the-shelf parser or dataset as a convenient stand-in. A vetted OFFLINE foundation asset built once is admissible; an external tool AT INFERENCE is a DEFECT that BLOCKS (and belongs IN the catalog).
