---
slug: audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins
status: INTEGRATED
review: STRONG
review_text: "Reverified first-hand: test_audit_reward_cluster_standins 31/31 PASS, test_grounded_successor_features_landing 5/5 PASS. A rigorous, in-depth AUDIT (the deliverable; NO hdlab writes by the solver, Q111): a pure-disk AST import trace over 249 hdlab modules enumerated the 7-organ reward cluster's 40-organ closure, liveness reconciled vs the REAL import graph. FINDING: the cluster's PINNED decision core (action_selection TD/RPE+SR-transport+Go/NoGo, successor_representation M=(I-gamma*P)^-1, self_manager DIAL#1 ACC/EVC halting) is FAITHFUL but DORMANT (0 hdlab importers); comprehension organs (goal_typing/goal_achievement/result_type_induction) are honestly-labelled OUR-INVENTIONs; state_of_mind is a correctly-labelled coref tracker. NO live unflagged decision stand-in of the reader-audit-C1 kind. #1 LOCATED (powered): the tonic-DA VIGOR channel is MISSING (cluster named 'vigor control' but no vigor computation) -- the Niv-2007 dial tau*=sqrt(C_v/rho) recovers +579 net reward CI-sep, composes byte-separably with the shipped halting dial. Also: R2 consequence teacher = symbolic MET/UNMET lexicon (inert); R3 self_manager 6-dial bank, 5 unbuilt; R4 action_selection reads value by COSINE not the linear SR read-out V=M*R (Dayan 1993 beats cosine Spearman 0.80 vs 0.39). OWNER-DIRECTED PROTOTYPES (BF, can-fail, NOT landed): the missing dial bank (vigor+NE gain+ACh encode/retrieve+5HT horizon+homeostasis, joint-EVC separable), R4 linear SR value, R2 graded OFC value teacher, + 4 perf-vs-brain gaps (state abstraction/successor features, MF<SR<MB revaluation, recursive 2nd-order ToM ORDER2 1.00 vs 0.00). INTEGRATION: audit folded to notes/BRAIN_FOUNDATIONAL_AUDIT.md + the reward-cluster BF-status confirmed (dormant-faithful, not defects); the highest-value prototypes captured as follow-on problems (the vigor dial + linear SR value are the leading BF-upchain reward wins). Reverified STRONG 2026-09-10."
---

# PROBLEM: two brain-fidelity audits exist (the reader's `situation_reader.read()` closure → the C1-C11 CATALOG; the grounding-acquisition subsystem → pri-4, in flight) — but the REWARD / ACTION-SELECTION / VIGOR control cluster (`hdlab/action_selection.py`, `successor_representation.py`, `self_manager.py`, `goal_achievement.py`, `consequence_learning_loop.py`, `goal_typing.py`, `state_of_mind.py`) has NEVER been fidelity-scored — the audit doc itself says "the fidelity audit stops at the reading/memory pipeline" and TIER 6 is "BUILT, BUT LARGELY OUTSIDE THE FIDELITY AUDIT … never been scored." Each prior audit surfaced a live OUR-INVENTION stand-in (the reader audit's #1 became the crown-jewel de-leak). This cluster can still harbor an unflagged non-brain-foundational placeholder — find it before it is wired. Produce the same disk-verified CATALOG deliverable. Glass-box, NO external LLM.

**slug:** `audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins` — **opened:** 2026-09-09 by the strategy session, from a whole-substrate gap scan (the meaning/coref/parser/learner lines are saturated; this motivational-control cluster is the one genuinely-unaudited region — verified: none of `action_selection`/`consequence_learning`/`goal_achievement`/`successor_representation`/`self_manager` appear in `situation_reader.py` or the grounding-loop import closure). **status:** OPEN. This is a MAP (a CATALOG + witness), NO hdlab writes — strategy lands any fix a later problem scopes. Honest scope note: this cluster is largely DORMANT (off the reader's live walls), so this is MEDIUM-blast fidelity-map-closing work, not an immediate board mover — its value is catching a placeholder before it is wired + completing the 100%-BF map. Glass-box, NO external LLM at inference (the invariant).

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
We have been checking, organ by organ, whether each part of the system computes things the way the brain actually does — and fixing or removing the parts that don't (that discipline already caught a component that was secretly cheating by peeking at answer keys, which became a major fix). But we only ever ran that check over the parts involved in READING and MEMORY. The parts that handle MOTIVATION and CHOICE — reward learning, deciding what action/goal to pursue, how hard to try (vigor), tracking consequences — have never been checked. They're built and sitting there, mostly not yet switched on. The job here is to go through that motivational-control cluster the same careful way: for each organ, say exactly what brain structure it's supposed to be, whether the code actually computes that or is a convenient placeholder, whether it's live or dormant, and how you'd fix it — and prove every claim against the code on disk. The point is to catch any fake/placeholder computation BEFORE it gets wired in, and to finish the map of "is every component brain-foundational?"

## 2. WHY THIS ONE — the last unaudited region, under the HARD 100%-BF gate
The owner's #1 standing directive is that EVERY component must be 100% brain-foundational — a non-brain-foundational component is a DEFECT that blocks. Two audits enforced that over the reading + grounding pipelines and each found a real live stand-in (one became the de-leak crown jewel). The reward/action-selection/vigor cluster is the region those two audits provably do NOT cover (verified by grep — see below), and the living audit doc explicitly flags it as never fidelity-scored. Auditing it closes the 100%-BF map and de-risks the moment any of these organs gets wired into a live control loop (e.g. an autonomous reading agent that chooses what to read/do next). It is a can-fail MAP with a proven deliverable shape (two accepted precedents).

## 3. MEASURED vs INFERRED
- **MEASURED (disk-verifiable now):** none of `action_selection` / `consequence_learning_loop` / `goal_achievement` / `successor_representation` / `self_manager` is imported by `hdlab/situation_reader.py` (the reader audit's closure) or by `hdlab/reading_grounding_loop.py` (the pri-4 audit's closure) — so this cluster is genuinely uncovered. The living audit records `successor_representation` as PINNED (M=(I−γP)⁻¹) but MEASURED-AND-LOST / degrading with scale, and names `state_of_mind` as "not ToM despite the name" — concrete starting threads.
- **INFERRED (what the audit must establish, not assume):** whether any organ in the cluster is an OUR-INVENTION placeholder vs the brain's actual computation; whether each is LIVE / DORMANT / measured-and-lost; and whether any is reachable from a THIRD control loop (autonomous-reading-agent) that neither prior audit swept — if so its blast rises from MEDIUM.

## 4. ALREADY TRIED / DO NOT REDO
- The two prior audits are DONE and are the DELIVERABLE TEMPLATE, not to be redone: `audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements` (reader closure, CATALOG C1-C11) and `audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins` (pri-4, grounding-loop closure). Do NOT re-audit organs already dispositioned there (the reader-side affect/goal SUPPLY organs — affect_lexicon / occ_appraisal / goal_register verb classes — were ruled ADMISSIBLE; C6 `context_grounded_valence` is already flagged). Audit only the reward/action-selection/vigor DECISION organs those closures do not reach.
- `dimensional_phase_diagram_audit_of_the_current_organs` audits dimensionality/orthogonality/store-family — a different axis; do not overlap it.
- Do NOT write `hdlab/` (Q111) — this is a map; a fix is a later problem strategy scopes.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the two precedent CATALOGs + witnesses (the exact deliverable shape): `notes/problems/audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements/CATALOG.md` + `verification/test_audit_live_standins.py`; `notes/problems/audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins/PROBLEM.md`.
- Read the cluster organs IN FULL: `hdlab/action_selection.py`, `hdlab/successor_representation.py`, `hdlab/self_manager.py`, `hdlab/goal_achievement.py`, `hdlab/consequence_learning_loop.py`, `hdlab/goal_typing.py`, `hdlab/state_of_mind.py` (+ any organ in their import closure). Establish the ENUMERATED DENOMINATOR: the full import closure of the cluster, reconciled against ACTUAL flag defaults (NOT the docstring comments — several "default OFF" comments are stale).
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the TIER 1-6 organ map + §2b) and inherit its verdicts (successor_representation, state_of_mind).
- Determine LIVE vs DORMANT with a PROVING GREP for each organ (who imports it; is it called under default flags in any live loop — reader, grounding, OR an autonomous-agent control loop). `python tools/experiment_index.py query "action selection"` / `"successor representation"` / `"vigor"`; `tools/substrate_map.py`.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
PASS = a `CATALOG.md` in this folder of the reward/action-selection/vigor cluster, with (a) an ENUMERATED DENOMINATOR (every organ in the cluster's import closure, reconciled against actual flag defaults, not comments — state HOW you enumerated); (b) for EACH organ the five disk-verified fields — brain structure+computation (PINNED cite or OUR-INVENTION), why-the-code-is/isn't-it at file:line, the BF replacement, LIVE-vs-DORMANT with the proving grep, LOCAL-FIX-vs-RE-ARCHITECTURE; (c) a TOP-K ranked by blast × severity; (d) ONE powered localization of the #1 stand-in (a can-fail measurement on its own metric with the strongest floor + an info-free twin LOSING, on the organ's own population — no cross-population number); and (e) a machine-checkable PURE-DISK witness `verification/test_*.py` that reproduces every LIVE/DORMANT/stand-in claim on the current bytes (a positive control that the guard fires). It FAILS if the witness cannot reproduce the claims on disk, or if the entries reduce to items already dispositioned in the two prior CATALOGs, or if an absence claim rests on a keyword search rather than an enumeration. A rigorous result of "this cluster is fully brain-foundational / all dormant, here is the enumerated proof" is a FULL PASS.

## 7. FILES AND ENTRY POINTS
- **The deliverable template:** `notes/problems/audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements/{CATALOG.md,PROBLEM.md}` + `verification/test_audit_live_standins.py`.
- **The cluster to audit:** `hdlab/action_selection.py`, `hdlab/successor_representation.py`, `hdlab/self_manager.py`, `hdlab/goal_achievement.py`, `hdlab/consequence_learning_loop.py`, `hdlab/goal_typing.py`, `hdlab/state_of_mind.py` + their import closure. Cross-check reachability from `hdlab/substrate.py` / `hdlab/glass_box_loop.py` / any autonomous-agent control loop.
- **Brain grounding to research:** basal-ganglia Go/NoGo + dopaminergic TD/RPE (Frank 2005; Schultz 1997); successor representation (Dayan 1993; Stachenfeld 2017); DA-vigor / ACC expected-value-of-control halting (Niv 2007; Shenhav 2013).
- **Build in THIS folder + `verification/` only. NO `hdlab/` writes (Q111).** Tag any mechanism cell with `__bf_status__` (keep `verification/test_bf_status_tags.py` green). Propose per-organ `__bf_status__` values in the CATALOG for strategy to land. `SOLVED.md` with bar/result/floor/controls/reverify + TLDR / QUESTIONS / NEXT STEPS.

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT re-audit organs already dispositioned in the two prior CATALOGs (name them + cite the prior verdict instead).
- Do NOT quote a liveness claim from a docstring comment — reconcile against the ACTUAL flag default at file:line (the stale-comment trap the reader audit catalogued as C-STALE).
- Do NOT make an absence claim ("organ X is dormant / has no live consumer") from a keyword search — it requires an ENUMERATION (state how you enumerated + a positive control).
- Do NOT use an external LLM / off-the-shelf model at inference; a vetted static offline FOUNDATION asset is admissible.
