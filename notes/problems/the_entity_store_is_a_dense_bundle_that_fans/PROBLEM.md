---
priority:
review: EXCELLENT
review_text: "Corrected the brief's premise then solved the real problem brain-faithfully. Re-verified FIRST-HAND: core 21/21 + frontier 26/26. The measured fan is an ADDRESSING COLLISION (unique-address decode 1.0 at every load; top-m recovers the set at ~1.0 -- the dense bundle never loses info), NOT superposition blur. Fix = finer conjunctive temporal key (TCM) + SET-RETURN read (CA3 reactivation): slope 0.288->0.000 CI-sep, info-free order twin loses. Built the maximally faithful FACTORIZED two-system store (sparse DG exact-recall + graded context, read separately) -> BOTH fan-flat 0.001 AND contiguity 0.585 on real LitBank, where a single key trades them; matches Bausch 2026 single-unit data + TEM. Sparse DG relocated to its true home (high-load exact-recall capacity, holds 1.0 to N=800 where the organ falls to 0.78), residual similarity-gated not count-gated. Honest deflations self-flagged. LANDED the cheap core fix (decode_set set-return on both register backends, witness PASS, registered); QUEUED the factorized two-system store as a proven-ready follow-on."
---

# PROBLEM: the situation-model entity store is a DENSE FHRR bundle whose decode DEGRADES as a character accumulates events (a measured fan effect) -- the faithful fix is a SPARSE, pattern-separated per-entity trace store (DG k-WTA + CA3 completion), NOT a pointer

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-27 (strategy session; grade EXCELLENT)
> **Re-verified FIRST-HAND** — `test_entity_store_fan.py` **21/21** + `test_entity_store_frontier.py` **26/26** (both run
> myself; suspected my own checker). One of the strongest submissions: it **corrected the brief's premise**, then solved
> the real problem the brain's way, then built the maximally faithful store and validated it on real data.
> **Diagnosis (decisive, honest):** the measured LitBank fan (decode 0.945@few → 0.657@many, slope 0.288) is an
> **ADDRESSING COLLISION + argmax readout, NOT superposition blur** — unique-(entity,slot) addresses decode at **1.0000 at
> every load level**, a top-m read recovers the co-slot set at ~1.0, and 22.7% of (entity,sentence) keys hold >1 verb (a
> busy character acts several times per context). "Ask whether the experiment could have SUCCEEDED first" falsified the
> superposition premise in one check — exactly the discipline we prize.
> **Fix (brain-faithful, CI-sep):** a FINER conjunctive temporal key (TCM continuous drift) OR a SET-RETURN read (CA3
> context-cued reactivation) flattens the slope **0.288 → ~0.000**; the info-free shuffled-order twin LOSES (1.000 vs
> 0.502, null p95 0.520); the finer index carries the specific-action info. Sparse coding is NEUTRAL for the measured fan
> (FINER_CTX === FINER_CTX_SPARSE) — the lever is the KEY + the READ.
> **Frontier (built + measured):** the maximally faithful store is FACTORIZED — sparse DG k-WTA exact-recall × graded
> multi-timescale temporal context × within-moment order, bound only at storage, read separately, with schema/gist routing
> and a race-to-stop set-return. On real LitBank it gets **BOTH** a flat fan (0.001) AND temporal contiguity (0.585) where
> a single graded key is stuck trading them (0.194 / 0.585). Independently confirmed by **Bausch et al. 2026 (Nature,
> human single-unit: content & context are SEPARATE populations bound by timing)** + TEM. Sparse DG relocated to its true
> home — high-unique-load exact-recall capacity (holds 1.0 to N=800 where the multibank organ falls to 0.78; residual
> **similarity-gated 3.5× not count-gated**) — so the brief's sparse mechanism was right, for a different regime than the
> measured fan. Reconstructive DRM intrusions (5.5×), event-boundary contiguity cut, path-integration transfer, and a
> local-rule SR predictor all measured, each with an info-free twin losing.
> **Honest deflations (self-flagged, preserved):** the fan fix is retrievability, not a downstream comprehension win;
> set-return ≈ a pointer on THIS data (the distinction is the mechanism + graceful degradation in the high-load/partial-cue
> regime, not the LitBank number); Part-3 sparse superiority partly a dimension effect; kWTA partial-cue robustness a real
> UNFIXED deficit (needs the iterative CA3 completer); spaCy verbs + oracle linking stand-ins (the diagnosis is robust to them).
> **hdlab LANDED (Q111, the cheap proven core):** `cleanup_set` + `decode_set` (SET-return) on BOTH register backends
> (`situation_model_accumulate` + `situation_model_multibank`); additive, `decode()` byte-unchanged. Witness
> `verification/test_situation_setreturn_organ.py` PASS on both backends; registered `situation_register_setreturn_v1`.
> **QUEUED proven-ready (larger follow-on hdlab landings, NOT in this commit, per owner "land the cheap fix first"):** the
> finer conjunctive temporal key; the FACTORIZED two-system store (sparse DG exact-recall + graded context); schema/gist
> interception; the CMR race-to-stop; the path-integration + local-rule-SR scaffolds. AUDIT UPDATE folded (§2b). Heavy
> LitBank-scale validations of the factorized store route to the REMOTE GPU box.

**slug:** `the_entity_store_is_a_dense_bundle_that_fans` - **opened:** 2026-08-27 by the strategy session
(the fan effect the entity-tracking integration MEASURED and flagged: oracle decode falls 0.695 -> 0.608 as an entity's
event-count grows 1-3 -> 17+; the dense bundle IS the shortcut).
**status:** OPEN - **a NEW-MECHANISM build (parallel-solver-appropriate): design the sparse pattern-separated per-entity
store the brain uses so a busy character's history stays retrievable.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2`. The fan effect is measured on running narrative;
> the sparse store is an evidence-backed BUILD, not a hunch. Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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

Our reader stores everything a character does by adding it all into ONE combined memory vector for that character. That
works when a character has done a few things, but as they pile up events the memory BLURS -- pulling back "what did this
character do at that moment" gets less accurate the busier the character is (we measured it: accuracy drops from ~0.70 to
~0.61 as a character goes from a few events to many). The brain does NOT do this: the hippocampus keeps memories SEPARATE
(pattern separation, so similar memories do not overwrite each other) and RECOVERS a full memory from a partial cue
(pattern completion). The task: build that sparse, separated per-character store so a busy character's history stays
sharp.

## 2. WHY THIS ONE

- **The fan effect is MEASURED on running narrative** (not synthetic) -- a real, quantified fidelity gap.
- **It aligns with the standing substrate-wide dense->sparse deviation** (the audit's biggest un-built store-design gap).
- **It is a clean brain-mechanism build** (DG pattern separation + CA3 completion), parallel to the strategy session's
  wiring/measurement work.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** the hippocampus stores episodic traces with DENTATE GYRUS pattern separation (sparse conjunctive expansion
recoding, ~1-5% active, k-WTA) and CA3 attractor pattern-COMPLETION (recover a full trace from a partial cue) --
Marr 1971; O'Reilly & McClelland 1994; Norman & O'Reilly 2003 (which EXPLICITLY names fan effects and states pattern
separation reduces the SLOPE of interference, not to zero). A dense superposition bundle is the WRONG store: it fans.

**OUR-INVENTION-UNDER-TEST (mark each; sweep, don't adopt):** the sparsity level (k-WTA %), the expansion dimension, the
completion dynamics (1-step vs iterative). COPY the operation (sparse conjunctive encode per event + attractor completion
retrieval); SWEEP the params. **CRITICAL (from the integration's finest-resolution drill): a pointer/index alone fixes
only CROSS-entity lookup, NOT within-register superposition crosstalk -- a "dense bundle + pointer" would STILL fan. The
faithful redesign is sparse encoding at EACH event.** Keep the dense bundle as a GIST (do not delete it -- augment).

## 4. MEASURED vs INFERRED

**MEASURED (from `wire_entity_tracking_end_to_end_on_running_narrative`, integrated 2026-08-27):** on LitBank, oracle
decode of "what did entity X do at event e" falls **0.6954 -> 0.6079** as X's event-count grows (1-3 -> 4-8 -> 9-16 ->
17+) -- the dense FHRR bundle degrades with N. The real `hdlab/situation_model_accumulate` register is the dense store.

**INFERRED / OPEN (this problem):**
- Does a sparse (DG-style k-WTA) conjunctive per-event encode + CA3-style attractor completion REDUCE the fan-effect
  SLOPE (decode accuracy vs event-count) CI-separated vs the dense bundle, with an info-free twin (random sparse code)
  LOSING?
- After sparsification, does the RESIDUAL degradation track item-SIMILARITY (brain-faithful) rather than item-COUNT?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT propose an index/pointer as the fix -- the integration's drill showed it does NOT remove within-register
  crosstalk (it still fans). The fix is sparse encoding at each event.
- Do NOT delete the gist bundle -- AUGMENT (the brain keeps a global gist AND separated traces).
- The prior `dg_separate` organ at ENCODING on the content code was NEUTRAL in an earlier test -- read that result;
  the faithful separator here is per-EVENT conjunctive sparse encode + completion, not content-sparsification alone.
- Query `experiment_index.py query "fan"`, `query "sparse"`, `query "pattern separation"`; read the entity-tracking
  SOLVED + `hdlab/situation_model_accumulate.py` + `hdlab/dg_separate.py` / `hdlab/dg_ca3_recollection_gate.py` BEFORE
  building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the fan effect on the REAL register (`hdlab/situation_model_accumulate`): decode-accuracy stratified by
  entity event-count on LitBank -- confirm the 0.695 -> 0.608 slope.
- Read `hdlab/situation_model_accumulate.py` (the dense bundle) + the existing DG/CA3 organs; confirm what is already
  built vs what the sparse per-event store needs.

## 7. THE BAR

A sparse pattern-separated per-entity trace store (DG k-WTA conjunctive encode + CA3 attractor completion) must, on the
REAL register + LitBank (or a construction proof on the real grounded/FHRR codes):

- **Reduce the FAN-EFFECT SLOPE (decode accuracy vs entity event-count) CI-separated vs the dense-bundle baseline over
  its UPPER bound, with an info-free twin (a RANDOM sparse code of matched sparsity) LOSING CI-separated.** Report CI
  half-width + null p95. Show the residual degradation tracks item-SIMILARITY, not item-COUNT.
- **DECISIVE EITHER WAY:** it flattens the fan CI-separated -> propose the hdlab store redesign (strategy lands it). It
  does NOT -> a rigorous negative localising whether the fan is irreducible at this representation (a real property to
  EXHIBIT, per the fan-effect-is-real-behaviour discipline) or needs a different separator.

## 8. FILES AND ENTRY POINTS

- `hdlab/situation_model_accumulate.py` (the dense register) + `hdlab/dg_separate.py` + `hdlab/dg_ca3_recollection_gate.py`
  + `hdlab/binding.py` (FHRR). `data/litbank/` (running narrative). The entity-tracking SOLVED's fan-effect cell.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT
  write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- A pointer/index is NOT the fix (still fans) -- sparse per-event encode + completion is.
- The fan effect is REAL human behaviour to EXHIBIT gracefully, not to zero out -- reduce the SLOPE, do not claim
  elimination.
- No number crosses populations -- recompute the fan slope on the LitBank register.
