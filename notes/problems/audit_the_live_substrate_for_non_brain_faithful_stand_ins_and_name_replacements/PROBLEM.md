---
priority: 2
review:
review_text:
---

# PROBLEM: systematically IDENTIFY every LIVE non-brain-foundational component in the reader (a cheap stand-in / surface-feature proxy / external tool AT INFERENCE / fitted-or-test-tuned heuristic / hand-lexicon standing in for a computation) and produce ONE prioritized CATALOG, each entry naming (a) the brain's actual structure+computation, (b) why the current thing is not it, (c) the brain-faithful replacement, (d) the blast radius (which live board dim), (e) LOCAL-FIX vs RE-ARCHITECTURE — a breadth pass whose re-architectures become their own follow-on problems.

**slug:** `audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements` — **opened:** 2026-09-08 by the strategy session, owner-requested (2026-09-08, under the emphatic 100%-brain-foundational GATE). **status:** OPEN. This is the BREADTH pass — find them ALL and map each fix — distinct from the DEPTH fixes (the pri-1 generative world-model, the pri-6 de-leak). Strategy lands any hdlab change (Q111); the solver writes the catalog + evidence in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant).

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
The system that reads text and builds meaning has been assembled from many parts. Some parts do their job the way a brain does it. Others are shortcuts we reached for because they were convenient: a part that guesses from surface word-patterns instead of understanding; a part that phones an outside, off-the-shelf language tool at the very moment of reading; a part whose settings were hand-tuned to pass one small test; or a hand-written word list standing in where a real computation belongs. The owner's rule is simple and firm: every part must work the way the brain works, and a convenient shortcut is a defect that blocks — not a preference. This job is to hunt down ALL of those shortcuts across the LIVE reading system and, for each one, write down five things: how the brain actually does that job, why the current part is not that, what the brain-faithful replacement would be, what fixing it would affect, and whether it is a small local fix or a bigger rebuild. The deliverable is ONE prioritized list. This job is not fixing them — it is finding them all and mapping each fix, so the big rebuilds can each become their own separate job. One caveat so the hunt does not over-fire: using a fixed, pre-built reference (a dictionary, a word-frequency table, an offline knowledge store) is FINE — the brain has that knowledge too. The defects are the convenient shortcuts done at reading time, the outside tools called mid-read, and the settings hand-fitted to a test.

## 2. WHY THIS ONE — the enabling INVENTORY under the 100%-brain-foundational gate
The owner made the 100%-brain-foundational gate the SPINE (2026-09-08): a non-brain-foundational component is a defect that BLOCKS, and board movement is now downstream of the gate. But the current map of what violates the gate is a strategy FIRST-PASS (`BRAIN_FOUNDATIONAL_AUDIT.md` §2b, entry CONT-28) that is admittedly LENIENT exactly where a bottom-up proxy stands in for a top-down / constraint-satisfaction computation — the blind spot a live solver already caught (the surface-feature parse scorer was rated "unpinned-OK"). A dedicated BREADTH pass finds every live stand-in in one place, verifies each on disk, and prioritizes them, so each re-architecture becomes a properly-scoped follow-on instead of being discovered piecemeal, one integration at a time. It is worth: a complete, ranked work-list for the gate — the thing that says WHICH defect to build across next and whether it is a ten-minute swap or a north-star rebuild. It is distinct from the DEEP fixes (this does not build the pri-1 generative world-model or land the pri-6 de-leak; it MAPS them and everything alongside them).

## 3. MEASURED vs INFERRED
**MEASURED (the confirmed live stand-ins / flags already on the map — VERIFY + DEEPEN, do not restart; §2b CONT-28 + the 2026-09-08 solver session):**
- **The SURFACE-FEATURE arc scorer** (`hdlab/arceager_parser.py`) — a bottom-up surface-feature attachment scorer; the brain parses by constraint-satisfaction with TOP-DOWN feedback. Solver-flagged 2026-09-08; SHARPENS the audit's lenient "arceager = UNPINNED-OK" verdict.
- **The cue PROXIES** — ConceptNet-count / Lancaster-norm / gold-coref-count cues, and **PURE-DEFER** (solver-flagged 2026-09-08).
- **`context_grounded_valence`** — harm/help event-valence from a self-admitted TEST-FITTED force-verb hand list `FORCE_CLASS_HARM_REAL` + a governor perceptron fitted on a tiny cert set (`hdlab/context_grounded_valence.py`). LIVE FAIL (board affect/valence); the named fix is in-substrate Wolff force arithmetic + animacy, retiring the fitted list+perceptron.
- **`perceptual_access_ledger`** — reaches for spaCy AT INFERENCE (`hdlab/perceptual_access_ledger.py:196-197`, `:529`, `:624`, `:681-682`). LIVE invariant violation; swap for the in-substrate parser.
- **`causation_typing`** — reaches for spaCy AT INFERENCE (`hdlab/causation_typing.py:566-567`, `:618`). LIVE.
- **`commonnoun_binder.situation_predict`** — a live string-identity head-match heuristic that TRAILS plain string identity (`hdlab/commonnoun_binder.py:203`); the named fix is the pinned `typed_coref` type-license resolver + a grown type KB.
- **`_apply_commonnoun_gate` gold-coref-inheritance LEAK** (`hdlab/situation_reader.py:3834`) — honest ~0.13 vs leaked ~0.83; masks every coref/name-bridge/experiencer gain (#1 blast; already filed as pri-6).
- **`cleanup_family` / `iterative_attractor`** — sign()+attractor-as-ranker re-promotes concept-hubs and HURTS semantic ranking, LIVE via `gap_detector`.
- **`hd_fact_store`** — 66% tautology/junk facts (FLEET).
- **Admissible, do NOT flag:** the many DORMANT brain-faithful PASSES (meaning channel not consumed at read()); vetted static offline FOUNDATION assets (WordNet/FrameNet/valence norms/open modern gold). The `state_register` closure→WordNet antonymy fix is ALREADY LANDED.

**INFERRED (you must establish):** whether the list above is COMPLETE — enumerate every organ the LIVE reader (`situation_reader`) consumes at read() time and check each, do not keyword-search; the LIVE-vs-DORMANT status of each (grep `situation_reader` for a real read()-time consumer — landed ≠ live); the LOCAL-FIX vs RE-ARCHITECTURE verdict per item; whether any flagged item is actually brain-faithful on deeper reading (a located-negative catalog entry is valid, if the deeper reading is shown); the priority ranking (blast × severity); and a concrete brain-faithful replacement DESIGN for the parser-scorer cluster (surface-feature scorer + cue proxies + pure-defer), referencing the recurrent predictive-coding loop / pri-1 generative world-model.

## 4. ALREADY TRIED / DO NOT REDO
- **The strategy first-pass audit (§2b CONT-28) exists — VERIFY + DEEPEN it, do not restart from scratch.** Its explicit blind spot is "unpinned-OK" verdicts where a bottom-up proxy stands in for a top-down computation (the arceager scorer is the worked example the solver already corrected). Re-check exactly those.
- **`state_register` closure → WordNet antonymy: ALREADY LANDED.** Do NOT re-flag it as a live defect.
- **The distinctive-feature IDF/whitening for `lexical_similarity`/`grounded_similarity`:** measured DORMANT (ZERO live consumer — an in-place swap is a NO-OP; it is a narrow follow-on, the whitening already an island). Do NOT re-derive that or call it a live gate-fail.
- **`crf_tagger`:** disposition is do-NOT-wire (an offline CRF is a cheap ML supplement for the pinned calibrated-belief property, which must come from the constraint-satisfaction / incremental parser). Don't propose wiring it as a fix.
- **The pri-1 generative world-model / recurrent predictive-coding loop is POSTED (`build_the_generative_result_state_world_model`, pri 1).** REFERENCE it as the convergent deep fix for the parser-scorer cluster; do NOT duplicate or rebuild it here.
- **Do NOT re-flag admissible static offline FOUNDATION assets** (WordNet/FrameNet/norms/open modern gold) — supplying knowledge the brain already has is not a violation.
- Run `python tools/before_you_start.py "audit live substrate for non-brain-faithful stand-ins"` anyway.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** `python tools/substrate_map.py`; `python tools/reader_capabilities.py`; skim `hdlab/`. Then read IN FULL `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the CONT-28 defect list is lines 68-77) and, IN FULL, the two deep-fix briefs this catalog feeds: `notes/problems/build_the_generative_result_state_world_model/PROBLEM.md` (pri 1) and `notes/problems/replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering/PROBLEM.md` (pri 6).
- **Establish live-vs-dormant per component (landed ≠ live).** The enumeration DENOMINATOR is the live reader: `grep -n "situation_predict\|_apply_commonnoun_gate\|perceptual_access\|causation_typing\|context_grounded_valence\|cleanup_family\|hd_fact_store" hdlab/situation_reader.py`. An organ with no read()-time consumer is DORMANT, not a live gate-fail — say so with the grep that proves it.
- **Confirm the spaCy-at-inference sites first-hand:** `grep -n "import spacy\|spacy.load\|nlp(" hdlab/perceptual_access_ledger.py hdlab/causation_typing.py`.
- **Confirm the fitted list + perceptron:** read `hdlab/context_grounded_valence.py` around `FORCE_CLASS_HARM_REAL` and its governor.
- `python tools/problem_ledger.py` — see what is already filed, so a re-architecture follow-on you name is not a duplicate of an open brief.

## 6. THE BAR (can-fail; a RIGOROUS MAP is the pass — not an open-ended survey)
**PASS = a prioritized CATALOG of >= 8 LIVE non-brain-faithful stand-ins, EACH with all five fields VERIFIED ON DISK:** (a) the brain's actual structure + computation, marked PINNED vs OUR-INVENTION, with a citation where PINNED; (b) why the current thing is NOT it (file:line); (c) the brain-faithful REPLACEMENT (named mechanism/organ); (d) blast radius = which LIVE board dim(s) it moves, OR "dormant / no live consumer" backed by the grep that proves it; (e) a LOCAL-FIX vs RE-ARCHITECTURE verdict. **PLUS** the top-K (K >= 5) prioritized by blast × severity, **AND** the parser-scorer cluster (surface-feature arc scorer + ConceptNet/Lancaster/gold-coref cue proxies + pure-defer) resolved to a concrete brain-faithful replacement DESIGN that references the recurrent predictive-coding loop / pri-1 generative world-model (does not rebuild it). A component flagged and then found brain-faithful on deeper reading is a VALID catalog entry (a located negative), provided the deeper reading is shown.

**HOW WE'D KNOW IT FAILED:** the catalog is a keyword-grep list with no on-disk verification of live-status (landed ≠ live); OR it re-flags an admissible static foundation asset (WordNet/FrameNet/norms/gold) as a violation; OR it stops at "survey" without the LOCAL-vs-RE-ARCHITECTURE verdict and the parser-cluster replacement design; OR it re-derives the pri-1 world-model instead of referencing it; OR it MISSES a component already named in §2b CONT-28 (an absence claim requires an ENUMERATION, not a search — state HOW you enumerated: every organ `situation_reader` consumes at read() time is the denominator, and a positive control that your enumeration recovers the already-named items). The deliverable is a bounded, disk-verified, prioritized catalog + one resolved replacement design; each re-architecture in it seeds its own follow-on PROBLEM, which the strategy session files from the catalog.

## 7. FILES AND ENTRY POINTS
**Read (do NOT edit `hdlab/` — Q111, the strategy session lands any change):** `hdlab/situation_reader.py` (the LIVE reader — the enumeration denominator: every organ it consumes at read() time), `hdlab/arceager_parser.py` (the surface-feature scorer), `hdlab/context_grounded_valence.py` (the fitted list + perceptron), `hdlab/perceptual_access_ledger.py` + `hdlab/causation_typing.py` (spaCy at inference), `hdlab/commonnoun_binder.py` (`situation_predict`), `hdlab/cleanup_family.py` (sign()+attractor ranker), `hdlab/hd_fact_store.py`, `hdlab/lexical_similarity.py`, `hdlab/grounded_similarity.py`. **Reference:** `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b, `tools/substrate_map.py`, `tools/reader_capabilities.py`. **Write only in** `experiments/`, `verification/`, and this folder — put the catalog itself in this folder (e.g. `CATALOG.md` alongside `SOLVED.md`). Do NOT touch other problems' folders, the plan, `STATUS.md`, or `BOARD.md`. Fold an AUDIT UPDATE into the audit at integration (strategy does that).

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT quote the leaked `_apply_commonnoun_gate` numbers (~0.83) as a live capability — they are gold-coref-inherited; the honest floor is ~0.13.
- Do NOT quote a "landed" organ as "live" without a grep of `situation_reader` proving a read()-time consumer (landed ≠ live).
- Do NOT re-flag the `state_register` closure (WordNet antonymy — already landed) or the distinctive-feature whitening (dormant, no-op swap) as live defects.
- Do NOT re-flag admissible static offline foundation assets (WordNet/FrameNet/valence norms/open modern gold). The violation is a tool AT INFERENCE, a convenient dataset/model-as-crutch, or a fitted/test-tuned heuristic doing a computation — never a static supply asset.
- Do NOT rebuild the pri-1 generative world-model / predictive-coding loop — reference it as the convergent deep fix for the parser-scorer cluster.
- Do NOT use an external LLM at inference anywhere in a proposed replacement (the invariant).
