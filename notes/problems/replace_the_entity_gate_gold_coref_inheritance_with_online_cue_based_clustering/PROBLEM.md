---
priority:
review:
review_text: "INTEGRATED 2026-09-09 (CONT-29): PART 1 (online_cluster) + PART 2 (crosstype_live_adapter, gold-free) landed + wired + FLIPPED DEFAULT-ON; verified (test_deleak_crosstype_live_adapter.py PASS: no crash, gold-free, pronoun byte-identical, +0.0838 CI-sep gain reproduced); board no-regress (coref flat, core aggregate stable). See SOLVED.md INTEGRATED_BY_STRATEGY."
---

# PROBLEM: the live reader's entity/common-noun layer secretly reuses the GOLD coreference answer key ("gold-coref inheritance" in `_apply_commonnoun_gate`) to cluster mentions — a non-brain-foundational oracle peek that inflates the live coref/experiencer numbers (~0.80–0.86) and MASKS every real coref, name-bridge and experiencer gain (strip the peek and the honest floor is ~0.13–0.49); build the brain's ONLINE, cue-based entity clustering (no answer key) so the reader works coreference out for itself, and prove it beats the HONEST (de-leaked) floor CI-separated and lets at least one downstream consumer's proven gain become live — or a rigorous located negative naming the honest ceiling.

**slug:** `replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering` — **opened:** 2026-09-08 by the strategy session, from TWO in-flight live-wire submissions (`wire_the_crosstype_definite_name_bridge...` and `report_the_typed_coref_organ_onto_the_live_reader...`) that INDEPENDENTLY hit this exact wall and both handed it off; the owner RULED 2026-09-08 that the gold-coref reuse is a LEAK to remove (not a legitimate "given" like gold mention spans). **status:** OPEN. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, NO external LLM at inference (an offline-built static clustering asset is admissible).

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
When the reader decides which mentions in a text refer to the same character or thing, it is quietly cheating: it copies the human-made answer key (the "gold" coreference labels) instead of working the grouping out from the words. With the answer key it looks like it gets ~80 in 100 right; take the key away — which the brain never has — and it drops to ~15–49 in 100. Two separate solvers just discovered this the hard way: each built a genuinely good tool (one links "the doctor" to "Elizabeth"; one re-groups common nouns by meaning), plugged it into the real reader, and saw NO improvement — because the answer key had already done the job. The peek is hiding the value of their work and of every future coreference improvement. The job here is to build the way the brain actually does this: form and update discourse referents ONLINE, mention by mention, from real cues (recency, grammatical role, gender/number, meaning/type match), with no answer key — and show it beats the honest score and lets those blocked tools finally pay off.

## 2. WHY THIS ONE — it is the precondition that unblocks a whole line of proven work
This is the highest-leverage UNASSIGNED problem right now: it is the single upstream component that two in-flight submissions independently identified as the reason their brain-faithful mechanisms show no live gain. Fix it and the crosstype definite→name bridge (+0.0528 experiencer, proven on the honest floor), the typed common-noun coref win, the entity-KB resolver, and every cross-type consumer become REAL live gains instead of "redundant." It also removes a standing non-brain-foundational leak from the live reader — a fidelity debt the audit already flags. Leaving it means every coref/entity result the fleet produces is measured against a peeking baseline and looks worthless.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: coreference is resolved ONLINE and incrementally, with no external key — the reader maintains a discourse model (a set of entity "files"; Heim 1982 file-change semantics) and, at each referring expression, retrieves the antecedent by CUE-BASED content-addressable retrieval (Lewis & Vasishth 2005: match gender/number/animacy/role/semantic-type cues against the active entity files, weighted by activation) biased by CENTERING salience (Grosz-Joshi-Weinstein; the backward-looking center / Cf ranking by grammatical role) and ACT-R base-level activation/recency (Anderson). Type/semantic-fit is one more retrieval cue, supplied by the landed typed-spokes (Lambon-Ralph ATL typed spokes: sense-resolved is-a AND part-whole). OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the cue weights, the activation decay, the write/merge policy (Nieuwland hold-under-uncertainty: resolve without destructively merging when confidence is low — a lesson already proven in the typed-coref win), the clustering granularity. NONE of it may consult gold coreference.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the two in-flight SOLVEDs; recompute on the HONEST floor):** the current live gate gold-inherits coref cluster ids, so its reported live numbers are peeking. Crosstype, GUM V12.1.0, all 275 docs, n=549 person-common experiencers, doc-level paired bootstrap: HONEST floor (raw `commonnoun_binder.situation_predict`, no peek) — C3 experiencer **0.1548**, C1 entity-layer CoNLL **0.6947**, C2 hard-link **0.0239**; the crosstype bridge lifts C3 **+0.0528 CI-sep** on that honest floor (twin loses), and de-leaking is downstream-safe (C1 up-or-flat, C2 up). Typed-coref, GUM modern TEST n=2855 anaphoric common-noun mentions: the DEPLOYED binder's per-mention resolution accuracy **0.4904** vs same-head string-identity **0.5412** (the deficit is the binder's BINDING, not the candidate set); the committed `hdlab/typed_coref.py` organ is the identified fix; its type comparator is HALF-WIRED (taxonomic is-a route only — the C6 part-whole route is available and unused).
- **INFERRED (you must measure):** whether a brain-faithful ONLINE cue-based clustering (no gold) beats the honest floor CI-separated on live common-noun/entity resolution AND raises at least one downstream consumer (crosstype experiencer C3, or the entity-KB resolver) to a live CI-separated gain over its honest floor, with the info-free twin LOSING and pronoun/named-antecedent consumers not regressing; the honest ceiling and its named cause (the world-knowledge residual is a SEPARATE, filed problem — see `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual`).

## ALREADY TRIED / DO NOT REDO
- Wiring the crosstype bridge / re-porting the typed-coref organ onto the CURRENT (peeking) gate — both yield NO live board gain, because the gold-coref peek already did the clustering. That is the whole reason this problem exists; do not re-run "wire it onto the current gate and measure the board."
- Treating gold-coref as a legitimate "given": the owner RULED it a leak (2026-09-08). Do not reintroduce it under any flag as a live-scored path.
- Destructive different-head merging: the typed-coref win PROVED the write regresses the same-head chain (always-hold is required). Reuse that lesson; do not re-derive it.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; then read IN FULL both in-flight SOLVEDs that handed this off — `notes/problems/wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift/SOLVED.md` (its "FULL-STACK-UPSTREAM" section pinpoints the leak as upstream #1 and confirms de-leaking is downstream-safe) and `notes/problems/report_the_typed_coref_organ_onto_the_live_reader_common_noun_path_and_measure/SOLVED.md` (the binder-binding diagnosis + the half-wired type comparator). Also read `notes/problems/improve_the_common_noun_coref_candidate_quality...` SOLVED (the typed-card-identity + non-writing-bridge levers, already proven) and the memory-flagged leak note.
- Locate the leak first-hand: the gold-coref inheritance is in `hdlab/situation_reader.py`'s `_apply_commonnoun_gate` entity-layer clustering; the deployed binder is `hdlab/commonnoun_binder.py` `situation_predict` (line ~203). Reproduce the honest floor by running the crosstype cell's honest-floor sweep (`verification/test_crosstype_live_wire.py`, W4 is the gold-coref leak diagnostic).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a brain-faithful ONLINE cue-based entity/common-noun clustering (glass-box, NO external LLM, NO gold-coref; an offline-built static asset is admissible) that, measured ONLY on the HONEST de-leaked floor, beats the current honest floor CI-separated on live common-noun/entity RESOLUTION accuracy (GUM modern TEST) AND lifts at least one downstream consumer (crosstype experiencer C3 over honest 0.1548, or the entity-KB resolver) to a live CI-separated gain, with the info-free twin (random type-compatible clustering of the same size) LOSING and pronoun + named-antecedent consumers byte-identical-or-up (no regress). Report CI half-width + null p95; recompute every floor on the item's own population; quote NO number computed with the gold-coref peek. A rigorous located NEGATIVE is a FULL PASS if it names the honest ceiling WITH a number and its cause (e.g. "online cue-based clustering reaches R on the honest floor and the residual is the ~81% world-knowledge slice, filed separately"). Strategy lands the Q111 wire (replacing the peek), witnessed.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE (do not rebuild): `hdlab/commonnoun_binder.py` (`situation_predict`, the deployed binder to replace), `hdlab/typed_coref.py` (the committed organ the typed-coref solver identified as the fix — the natural home for the honest clustering), `hdlab/typed_spokes.py` (`coref_type_license` — WIRE BOTH the is-a AND the currently-unused C6 part-whole route into the type cue), the salience/Centering binder + ACT-R recency already in the coref stack, and `hdlab/situation_reader.py` `_apply_commonnoun_gate` + `_build_entities` (where the leak lives and where the honest clustering wires in). Downstream consumers to re-check for regress AND to revisit so they consume the honest clustering: `hdlab/crosstype_bridge.py`, the entity-KB resolver, `goal_register.make_canonicalizer`, `affect_register.bind_experiencers`. Heavy runs → REMOTE. Strategy lands the hdlab change (Q111, witnessed) + folds an AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote ANY live coref/experiencer/entity number computed WITH the gold-coref inheritance (~0.80–0.86) as a real result — it is the peek. Every headline is on the HONEST de-leaked floor.
- Do NOT quote the typed-coref board win (0.5671 on the URG instrument) as a LIVE-reader number — it was a board-instrument proxy; the live binder is the thing being fixed here.
- Do NOT use an external LLM, and do NOT use any 19c gold (LitBank/McGuffey) as a load-bearing measurement — grade on modern GUM (native LitBank is a robustness check only).
