---
priority: 4
review:
review_text:
---

> **⚠️ RESTORED 2026-09-08 by the strategy session.** This strategy-owned PROBLEM.md was lost from disk when the folder was removed during concurrent git/session activity (the solver's SOLVED.md survived + was recreated from context; see its RECOVERY NOTE). Recreated faithfully from the original brief spec + the solver's SOLVED — the mechanism, bar, and DO-NOT list are the original; numbers below reflect what the solver measured.

# PROBLEM: narrative causation is mostly UNMARKED (~65.6% of gold causal edges carry no connective), so every connective/parse-bound typer dead-ends (~0.5% recall) and retrieval from a causal KB/CSKG recovers only ~2% (an EDGE gap, not a vocabulary gap) — the brain does NOT match surface cues, it GENERATES the causal antecedent by simulating forward from candidate prior events (force dynamics for physical causation + inverse-planning/mentalizing for social causation, over the RESOLVED participants) and checking which produces the observed event; build that generate-don't-retrieve causal reader to break the ~5% coverage bound on the unmarked majority while HOLDING binding precision CI-separated over the contiguity floor with participant coref ON, or a rigorous located negative naming the no-LLM causal-recall ceiling with a number.

**slug:** `generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation` — **opened:** 2026-09-08 by the strategy session (the causal channel's blessed located-negative deepening from the owner-DONE `extract_spatial_and_causal_relations...`). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM at inference (an offline static world-model / force-dynamics asset is admissible).

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
Readers constantly work out WHY something happened even when the text never says "because" — "she saw the letter, then wept" tells you the seeing caused the weeping, though nothing marks it. Our reader can only catch the ~1-in-200 causal links that ARE marked by a connective; the unmarked majority it misses. Looking them up in a causal database barely helps (it finds ~2%). The brain doesn't look causation up — it GENERATES a candidate: it simulates a likely earlier event forward (using physical force-dynamics for physical causes, and "what would this person be trying to do" reasoning for mental/social causes) over the actual characters, and keeps the one whose predicted outcome matches what happened. The job: build that generate-don't-retrieve causal reader so it recovers unmarked causal links a competent reader would, without over-linking — or prove exactly where a no-LLM version hits its ceiling.

## 2. WHY THIS ONE
Causal understanding is one of the reasoning board's core dimensions and the blessed located-negative from the shared-extraction work: the connective path is a 0.5%-recall dead-end and a bigger KB is refuted (the gap is EDGE generation, not vocabulary). This is the mechanism that could actually recover the unmarked majority, and it is the shared engine behind the generative world-model — so it compounds.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: readers build a CAUSAL NETWORK by inferring connections between events online (Trabasso & van den Broek 1985; Graesser-Singer-Trabasso constructionist inferences — necessary bridging causal inferences ARE drawn during reading); physical causation is understood via FORCE DYNAMICS (Talmy 1988; Wolff force theory), social/mental causation via a DISTINCT mentalizing system (Jack et al. 2013 opposing-domain / inverse planning, Baker-Saxe-Tenenbaum); antecedent selection is a generative check (does simulating prior event E forward produce the observed event?) with an ACT-R recency/activation prior. OUR-INVENTION-UNDER-TEST (sweep): the forward simulator, the physical-vs-mental routing, the candidate-antecedent window, the coverage/precision operating point.

## MEASURED vs INFERRED
- **MEASURED (from the parent extract_spatial_and_causal SOLVED + this solver's SOLVED — do NOT re-derive):** causal type is UNMARKED for 65.6% of MAVEN edges; connective-matching ~0.5% recall; retrieval/CSKG refuted at ~2% (EDGE gap). The generative causal-antecedent search WINS binding precision (MAVEN balanced-precision reader 0.4565 vs contiguity 0.1395, +0.317 CI-sep) and on TellMeWhy cause-ID non-adjacent (n=299) beats topical 0.254 (+0.067 CI-sep) + info-free twin 0.238 (+0.084 CI-sep); participant COREF lifts the simulator ~3.29×. Most narrative causation is MENTAL (a distinct system from physical force-dynamics).
- **INFERRED (measure):** how far the generative reader breaks the ~5% coverage bound on the UNMARKED majority while holding binding precision CI-sep over contiguity; the physical-vs-mental routing's fidelity; the exact no-LLM causal-recall ceiling + its cause (the twin matching on the unmarked residual = the honest coverage wall).

## ALREADY TRIED / DO NOT REDO
- CSKG / bigger-KB retrieval — refuted at ~2% (EDGE gap, not vocabulary).
- Connective-matching / connective-scoping typer — 0.5% recall; the scoping workaround is the connective-path CEILING (do not retire or re-open it).
- Parse-marginal attachment (parse ~99.9% confident) + object-affordance (register-bound) — located negatives.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read IN FULL the parent `notes/problems/extract_spatial_and_causal_relations.../SOLVED.md` (the causal located-negative) + this folder's own SOLVED.md (the built reader). Reproduce: `.venv/Scripts/python.exe verification/test_causal_antecedent_reader.py`.
- Inspect what you REUSE: `hdlab/force_dynamics_typer.py`, the coref stack (`hdlab/entity_binder.py` / `commonnoun_binder.py`), the goal/affect registers, `hdlab/causal_reasoner.py`, and this folder's cells (`experiments/exp_causal_antecedent_reader_*.py`).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a brain-faithful GENERATIVE causal-antecedent reader (glass-box, NO external LLM at inference; an offline static world-model/force-dynamics asset is admissible) that, on a MODERN causal gold, materially breaks the ~5% coverage bound for the UNMARKED majority while HOLDING binding precision CI-separated over the contiguity floor (MAVEN 0.1395) with participant coref ON, info-free twin LOSING, no live reasoner regressing. A rigorous located NEGATIVE is a FULL PASS if it names the no-LLM causal-recall ceiling WITH a number + mechanism (e.g. the twin matches on the unmarked residual → the coverage wall is instance-specific context no aggregate can supply). Report CI half-width + null p95; recompute floors per population. **19c is NOT load-bearing.**

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/force_dynamics_typer.py`, the coref stack, goal/affect registers, `hdlab/causal_reasoner.py`, and this folder's `exp_causal_antecedent_reader_*.py` + `verification/test_causal_antecedent_reader.py`. Heavy runs → REMOTE. Strategy lands any hdlab wire (Q111, witnessed) + folds an AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b. **GOLD (owner 2026-09-08): GLUCOSE is the better narrative-causal gold — MAVEN newswire is the "easy reach" but GLUCOSE (implicit cause/effect over ROCStories) is the more representative narrative instrument; prefer it (with TellMeWhy) over MAVEN as the load-bearing gold.**

## DO NOT QUOTE
- Do NOT quote a CSKG/bigger-KB causal reader as viable (refuted ~2% — the gap is EDGE generation).
- Do NOT quote the connective path's numbers as the reader's (0.5% recall; a located-negative ceiling).
- Do NOT use an external LLM as the causal reasoner at inference (the invariant); do NOT use 19c gold as load-bearing.
