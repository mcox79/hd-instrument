---
priority:
review: EXCELLENT
review_text: "A rigorous, two-sided, brain-grounded VALIDATION on real LitBank (100 novels, self-extracted facts, no oracle; reverified 11/11 FIRST-HAND, scaffold-free, recomputes every headline). NEGATIVE (a full pass): fired blind on competitive coref the self-extracted discourse-fact bridge does NOT beat the salience floor (DEV weight 0; forced-on HURTS 0.68-0.78 vs floor 0.805 CI-sep below; the constructed 0.998 was idealized-extraction + exact-KG artifact). Built ACROSS the wall (a rich-entity action-history model, 93% coverage) -- ALSO collapses, and the reason generalizes to a law (for the hard cases the gold antecedent is the LEAST-mentioned entity, so ANY discourse-content bridge is anti-correlated -> the brain uses the syntactic binder, not memory). POSITIVE (honest, gated): on the ~15% fact-present sliver fusing the fact into the REAL resolver LIFTS 0.837->0.961 CI-sep (DEV weight 2, twin crashes to 0.16); on the 85% complement the cue HURTS blind (0.80->0.52) -> unconditional weight 0. GATE drilled to ground: NO observable gate beats the floor (best +0.001; oracle ceiling +0.021 unreachable); research drill (5 literatures) -> INTRINSIC BOUND (the brain has no reliability gate; world knowledge is a graded Bayesian prior, correctly low-weighted). CONVERGES with + triangulates the assembly's own coref-residual drill (a KB is dead ~2-3% on the residual). Correct hdlab call: do NOT wire any discourse-content bridge into competitive coref (measured net-zero, brain-faithfully) and do NOT build a fact-reliability gate (intrinsic dead end) -> NO coref landing earned; the organ's real home is fact-GIVEN downstream tasks (QA/bridging) where the 0.84->0.96 lives. Exemplary honesty (withdrew an inflated construction-proof positive; flagged the PARTIAL/SOLVED labelling churn). Grade EXCELLENT. One VET-pending: the strongest 'net-zero = correct calibration' equivalence claim runs one notch ahead of a direct proof."
---

> ## ✅ SOLVER REVIEW — EXCELLENT (integrated 2026-08-30 by the strategy session; owner_verdict: DONE)
> **A rigorous, two-sided NEGATIVE-leaning validation** — the good kind: it measures the integrated discourse-fact
> reasoner on real narrative (LitBank, 100 novels, SELF-extracted facts, no oracle) and honestly bounds it, then
> correctly PREVENTS a wrong wiring. Reverified **11/11 FIRST-HAND** (scaffold-free; recomputes every headline from
> source — the trustworthy kind, unlike a witness that reads cached metrics).
>
> **The result (two-sided):** (NEG, a full pass) fired blind on competitive coref the self-extracted discourse-fact
> bridge does NOT beat the salience floor — DEV sets its weight to 0; forced-on it HURTS (0.68–0.78 vs the real
> fact-blind floor 0.805, CI-sep below). The constructed 0.998 was an idealized-extraction + exact-KG artifact (a
> degradation curve connects 0.998 → floor). The solver then BUILT ACROSS the wall (a rich-entity action-history model,
> 93% coverage vs 43% for stated types) — it ALSO collapses, and the reason generalizes to a **law**: for the hard
> cases (salience fails) the gold antecedent is the LEAST-mentioned entity, so ANY discourse-content bridge is
> anti-correlated with it → the brain uses the syntactic binder there, not memory. (POS, honest + gated) on the ~15%
> fact-present sliver, fusing the fact into the REAL resolver LIFTS **0.837 → 0.961 CI-sep** (DEV weight 2, info-free
> twin crashes to 0.16); on the 85% complement the same cue HURTS blind (0.80 → 0.52) — which is exactly why the
> unconditional weight is 0.
>
> **The gate question drilled to ground:** it's a gated capability, so can an observable fact-reliability gate deploy
> it? Every gate built (clean-type, low-margin, salient-bridger, combinations, a learned logistic gate) — NONE beats
> the floor (best +0.001); the oracle ceiling is only +0.021 and unreachable. A research drill (5 converging
> literatures: McRae 1998; Metusalem 2012; Kehler & Rohde 2013; Competition Model; Ferreira & Patson) gives the verdict:
> **INTRINSIC BOUND, not a missing mechanism** — the brain has no reliability gate; it integrates world knowledge as a
> continuous graded Bayesian PRIOR, so a low-validity cue correctly gets low weight. The net-zero gate is the CORRECT
> brain-faithful behavior; a gate is the wrong lever.
>
> **Why EXCELLENT:** two-sided, controlled, brain-grounded, and it correctly does NOT deploy a measured-net-zero cue —
> plus exemplary honesty (it WITHDREW an inflated constructed-2way positive it caught as a construction proof, and
> flagged its own PARTIAL→SOLVED labelling churn). It also **triangulates** the assembly's independent coref-residual
> drill (both measured a commonsense KB dead ~2-3% on the anti-typical residual) — two drills this session converge that
> the residual is discourse-focus / syntactic-binder bound, NOT world-knowledge bound. One VET-pending caveat (does not
> cap the grade): the strongest "net-zero = correct calibration" equivalence claim runs one notch ahead of a direct
> proof — do not let a future brief lean on it un-VET'd.
>
> **hdlab landing (Q111):** NONE earned into competitive coref (measured net-zero, brain-faithfully so) and NO
> fact-reliability gate (intrinsic dead end) — the result IS "do not wire it there." The organ's proper home is
> fact-GIVEN downstream tasks (the parent's QA / next-event / bridging), where the 0.84→0.96 lift lives — a FUTURE
> landing when such a consumer exists, not now. Audit §2b folded (REFINE: real-text accuracy measured two-sided;
> intrinsic bound; organ value is fact-given tasks).


# PROBLEM: the reading-built discourse-fact store + graded 2-hop bridging RESOLUTION (integrated `situation_model_has_no_discourse_fact_reasoning`) scored 0.998 vs a fact-blind 0.504 (chance) on an INTER-SENTENTIAL fact-decisive population — but that population is CONSTRUCTED (state-a-role-then-refer-by-action), and the near-1.0 reflects IDEALIZED extraction (facts handed in clean) + EXACT KG edges. Its own #1 withdraw-first caveat: real-text accuracy is UNMEASURED. So we do NOT know whether the capability survives when the reader must EXTRACT the facts itself from noisy real prose and the KG coverage is patchy — the difference between "a mechanism that works on a jig we built for it" and "a reading skill." MEASURE it on real narrative: build an inter-sentential fact-decisive population from LitBank/real narrative (a reference resolved by a fact stated earlier about a character, NOT resolvable by grammar/salience alone), have the reader SELF-EXTRACT the per-entity facts (no oracle), and show the fact-store reader beats the fact-BLIND reader CI-separated with the info-free twin losing — PLUS the graceful coverage-degradation curve (accuracy vs the fraction of the deciding fact actually extracted). A rigorous NEGATIVE (real-text extraction/KG coverage caps it at or below the fact-blind floor — quantified) is a FULL PASS that honestly bounds the capability.

**slug:** `the_discourse_fact_reasoner_is_unvalidated_on_natural_text` — **opened:** 2026-08-29 by the strategy session
(the SOLVER-FLAGGED #1 follow-on of the integrated `situation_model_has_no_discourse_fact_reasoning`, owner-DONE/EXCELLENT:
its L1 win is on a constructed population with idealized extraction + exact KG edges, and it explicitly names real-text
measurement as the #1 thing to establish). **status:** OPEN — a MEASUREMENT + (if it degrades) BUILD problem. You build +
validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — HIGH value: this confronts a capability graded
> EXCELLENT-but-on-constructed-data with reality, before anything downstream is built on it. If it holds, we have a
> validated reasoning-frontier skill; if it degrades (likely — extraction noise + KG sparsity on archaic prose are real),
> the QUANTIFIED bound reshapes the reasoning program and is itself the deliverable. Either outcome is load-bearing. Ranked
> below the assembly (p3) and causation (p4) because it VALIDATES an existing capability rather than adding a new one, but
> above lower facets. **Dependency web:** the fact store is a landed/queued organ; a better parser (p8) + richer semantics
> (p1) both lift extraction. **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
We built a "reading memory" that stores facts about characters as it reads and uses them to work out later references
("...she poured the tea. Moments later the hostess sat down" → the tea-pourer is the hostess). It scored almost perfectly —
but on sentences we HAND-BUILT to have exactly the right shape, with the facts handed to it clean and the background
knowledge guaranteed present. That is a lab jig, not a book. The honest question is whether the skill survives on REAL
prose, where the reader has to dig the facts out of messy sentences itself and the background knowledge is patchy. This
problem measures exactly that on real narrative, and — crucially — maps HOW the accuracy falls as the reader's own
fact-extraction gets worse, so we get an honest picture instead of a lab number.

## 2. WHY THIS ONE
Because right now a capability is graded EXCELLENT in the substrate on the strength of a constructed test, and its own
author flagged real-text as unmeasured. Building anything downstream on an unvalidated near-1.0 is how a substrate fools
itself. Confronting it with real narrative either promotes it to a genuine reading skill or hands us a quantified bound
that redirects the reasoning program — both are decisive, and neither exists yet.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** the situation-model RESOLUTION stage (Garrod-Sanford BONDING/RESOLUTION; Kintsch CI) runs
  on facts the reader EXTRACTED incrementally WHILE READING — noisy, partial, good-enough (Ferreira & Patson) — not on a
  clean oracle store. Bridging resolves the reference by retrieving the accumulated fact that makes the clause coherent
  (Haviland-Clark +181ms cost). The DECIDING signal is discourse-specific and self-built.
- **OUR-INVENTION-UNDER-TEST (the real-world variables to MEASURE, not sweep-and-adopt):** the FACT-EXTRACTION pipeline
  (how per-entity `(entity, relation, value)` facts are pulled from real prose — the noisy step the constructed test
  bypassed) and the KG coverage for the bridge. **Copy the RESOLUTION computation** (the landed discourse-fact organ);
  MEASURE how its accuracy tracks the quality/coverage of the self-extracted facts (the degradation curve IS the result).
- **NOT brain-faithful:** an oracle fact store (hand-fed clean facts — the constructed L1 setup, inadmissible as a real-text
  claim); a gold-leak from the reference answer into the extracted facts; an external LLM extractor (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the L1 constructed result (`situation_model_has_no_discourse_fact_reasoning`,
  `exp_discfact_store_bridging_capability_v1`): fact_store 0.998 vs fact-blind 0.504 (chance), +0.494 CI-sep, ALL controls
  at chance (info-free twin, KG-only-null, ablation) — on IDEALIZED extraction + exact KG edges. The graded distributional
  bridge generalizes to held-out edges 0.700 (L1b). The organ's own #1 caveat: real-text accuracy unmeasured.
- **INFERRED (to prove):** the REAL-TEXT accuracy on an inter-sentential fact-decisive population from LitBank/narrative,
  with SELF-EXTRACTED facts (no oracle) + real KG coverage — CI-separated over the fact-BLIND graded resolver recomputed on
  the same population, info-free twin (shuffled facts) losing, PLUS the accuracy-vs-fact-coverage degradation curve — OR a
  rigorous, quantified NEGATIVE (real extraction/KG coverage caps it at/below the fact-blind floor; name the coverage % and
  the dominant failure — extraction miss vs KG gap vs no-fact-exists).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-run the constructed L1 (done — it is the MOTIVATION, not the deliverable). Do NOT rebuild the fact store or the
  graded bridge (landed/validated — compose them). Do NOT test on the anti-typical LitBank COREF residual (already REFUTED
  as fact-decisive in the parent — the fact store is DEAD there; this is INTER-sentential fact-decisive reference, a
  DIFFERENT population). Do NOT hand-feed clean facts (that is the oracle the constructed test already used). REUSE the
  discourse-fact organ + a real narrative corpus + the substrate's own extraction.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `situation_model_has_no_discourse_fact_reasoning/SOLVED.md` (the L1 result, the two levels, the #1 real-text caveat,
  the graceful-degradation framing) + its `research_discourse_fact_resolution_brain_mechanism_2026-08-29.md` +
  `exp_discfact_store_bridging_capability_v1.py` (the constructed harness to adapt to real text). Read the discourse-fact
  organ (proposed/landed) + the substrate's fact-extraction path. Run `tools/experiment_index.py query "discfact"` /
  `"bridging"` / `"situationmodel"`. Audit: the newest §2b discourse-fact-store entry. **Mind the CORPUS-AGE confound** —
  archaic-prose extraction noise is a REAL contributor to the degradation you are measuring (attribute it, don't hide it).

## 7. THE BAR
PASSES only with ALL of:
1. **A REAL-TEXT inter-sentential fact-decisive population** (built in `experiments/` from LitBank/real narrative): a
   reference (pronoun or definite description) resolvable ONLY by a fact stated earlier about a candidate (NOT by
   grammar/salience — filter those out, as the parent did), with self-EXTRACTED per-entity facts (no oracle, no gold leak).
2. **The fact-store reader beats the fact-BLIND reader CI-separated on real text** (the fact-blind graded resolver
   recomputed on the same population = the floor); the **info-free twin** (shuffled facts) LOSES CI-separated; report CI
   half-width + null p95; no number crosses populations.
3. **The graceful-degradation curve:** accuracy vs the fraction of the deciding fact actually self-extracted (and/or KG
   coverage) — the honest real-world bound, with the dominant failure mode named (extraction miss / KG gap / no-fact-exists).
4. **One-screen summary:** population → floor → twin → real-text lift → degradation curve → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "on real narrative the fact store lifts fact-decisive reference +X CI-sep where
the fact IS self-extracted [Y% of cases], but real coverage is Y% so the population-level lift is Z — the constructed 1.0
was an idealized-extraction artifact; the mechanism is real, the bound is extraction/coverage").

## 8. FILES AND ENTRY POINTS
- **Motivation + harness (REUSE, adapt):** `situation_model_has_no_discourse_fact_reasoning/{SOLVED.md,
  research_discourse_fact_resolution_brain_mechanism_2026-08-29.md}`; `experiments/exp_discfact_store_bridging_capability_v1.py`
  (the constructed harness — swap its idealized extraction for real self-extraction on LitBank).
- **Compose:** the discourse-fact store + graded 2-hop bridging organ (proposed/landed); the substrate's fact-extraction
  path; a real narrative corpus (LitBank). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The constructed 0.998 is the MOTIVATION, not your result — the deliverable is the REAL-TEXT number with self-extracted
facts + the degradation curve. Do NOT re-run the constructed L1, hand-feed clean facts, or test on the anti-typical coref
residual (wrong population — measured dead there). Strategy owns any hdlab landing.
