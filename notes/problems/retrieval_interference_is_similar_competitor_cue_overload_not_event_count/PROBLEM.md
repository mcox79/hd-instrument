---
priority:
review: STRONG
review_text: A rigorous mostly-NEGATIVE that CONFIRMS the reframe and closes the route. Reverified 18/18 FIRST-HAND on held-out LitBank pronoun coref (n=3,378 ambiguous >=2-candidate queries): (1) REFRAME CONFIRMED — the who-did-what event-count proxy content floor 0.398 and naive recency TIES it (0.402), so interference is NOT event-count; it is similar-competitor cue-overload (content x context). (2) The right-axis organ ALREADY EXISTS — the landed graded_antecedent_pick scores 0.676 vs content-only 0.521 (+0.155 CI-sep), beats naive recency + hard-tier, shuffled-context twin LOSES (0.436). (3) BOTH candidate NEW cues are RIGOROUS NEGATIVES: the brief's multi-timescale TCM context adds -0.001 NOT_SEP over the landed organ; gender's marginal over the already-landed PERSON cleanup is +0.003 NOT_SEP (number +0.004) — vindicating the landed organ's own "gender is a non-lever" note. (4) The residual is measurably STRUCTURAL not a memory feature: reachable ceiling 0.921 (only 7.9% cataphora unreachable), 72% of errors are gold-present-but-not-most-accessible, and two combination rules (additive 0.650, Boltzmann 0.659) converge ~0.10 below the oracle-of-cues 0.763 (the combination rule is not the bottleneck — the information isn't there). Exemplary controls: the PERSON-vs-GENDER decomposition caught + corrected a v7 conflation (gender's apparent +0.040 was +0.038 person + 0.003 gender); shuffled twins for both context and phi; no-fit weighting; 6-split robustness (person 6/6, gender +0.001±0.001). NO hdlab landing earned (both new cues negative; the right organ already landed). Grade STRONG (a high-quality rigorous negative that closes the new-cue route and reframes the residual as structural; not EXCELLENT only because it yields no new capability — the honest outcome, not a flaw).
---

> ## ✅ SOLVER REVIEW -- STRONG (integrated by strategy 2026-08-31)
> **Why STRONG (a rigorous negative done right):** it confirmed the reframe on the substrate's OWN task (real
> held-out LitBank pronoun coref, n=3,378), showed the right-axis organ already exists (`graded_antecedent_pick`
> +0.155 CI-sep over content), and then RIGOROUSLY REFUTED both candidate new memory-axis cues — the brief's own
> multi-timescale TCM context (-0.001 NOT_SEP) and gender/number agreement (+0.003 NOT_SEP over the person cleanup).
> The decisive move was the PERSON-vs-GENDER decomposition: it isolated gender's marginal from the already-landed
> person cleanup and CAUGHT + CORRECTED its own v7 conflation (the apparent +0.040 was +0.038 person + 0.003 gender)
> — exactly the "adversarial control that reproduces the win from the wrong source" discipline, applied to itself.
> And it proved the residual is STRUCTURAL, not a missing memory feature: reachable ceiling 0.921, 72% of errors are
> gold-present-but-not-most-accessible, and two combination rules converge ~0.10 below the oracle-of-cues (so the
> combiner is not the bottleneck — the information is not in these cues).
> **Reproduced under my check:** I re-ran `verification/test_similar_competitor_retrieval.py` — 18/18 PASS,
> scaffold-free; the event-count tie (0.398/0.402), oracle headroom (0.763 vs 0.620), combiner 0.650 > floors,
> shuffled twins lose (0.438/0.436), TCM -0.001, gender marginal +0.003, and the structural-residual ceiling (0.921,
> 72% structural) all reproduce from source.
> **NO hdlab landing (correct no-landing):** both candidate new cues are CI-separated negatives, and the right organ
> (`graded_antecedent_pick`) is already landed — there is nothing new to wire. The route "add a memory-axis cue to
> beat retrieval interference" is CLOSED; the residual is a STRUCTURAL/accessibility problem (Centering-style
> most-accessible-antecedent selection), not a cue-overload one. Recorded in WIRING_MAP non-debt so it is never
> re-packaged. A rigorous negative is a full PASS.

# PROBLEM: our memory-interference organ is aimed at the wrong axis — it models interference as EVENT-COUNT per entity, but real retrieval interference is SIMILAR-COMPETITOR CUE-OVERLOAD. The generalization stress-test (`stress_test_which_organ_wins_actually_generalize_on_held_out_text`, integrated) reran the separated store on real LitBank (n=28,569) and found its synthetic +0.94 win collapses 15–60× to +0.06, concentrated in the ~13% of "busy" entities (≥4 events) — because on real text the median entity carries ~1 event, so event-count is almost never the interference driver. The brain-foundational drill (PINNED) reframed it: interference is not "one entity is busy," it is "several OTHER active entities feature-MATCH the retrieval cue" — cue-overload among SIMILAR competitors (Van Dyke & McElree 2006; the partial-cue retrieval the original task deliberately removed). The reframe is GATE-CLEARED on the right axis: on real similar-competitor queries a content-only feature matcher scores only 0.398 (content genuinely UNDER-determines the choice), so there is real headroom for a context-reinstatement mechanism. Build the reframed similar-competitor / partial-cue retrieval — a TCM temporal-discourse CONTEXT-reinstatement cue that disambiguates among feature-matching competitors — and validate it beats the content-only floor on real ambiguous queries.

**slug:** `retrieval_interference_is_similar_competitor_cue_overload_not_event_count` — **opened:** 2026-08-30 by the strategy
session (the generalization stress-test's gate-cleared retrieval reframe). **status:** OPEN — a MECHANISM + BUILD problem. You
build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` — the gate is cleared (content under-determines on real
> similar-competitor queries, 0.398) but the UNBUILT step (cue COMBINATION — how context + content combine to break the tie) is
> the uncertain one, so the stress-test flags this at **P≈0.50**: real headroom, honest uncertainty. Ranked below the extraction
> front-end (p1, the ceiling on everything) + the causation successor (p5, gate-cleared + course-corrects a live problem).
> **Re-rank per the owner.** ⚠️ HONEST GUARD: naive recency ALONE ties the content-only floor — the VALUE is in the COMBINATION,
> which is the part not yet built.

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
When a reader has to figure out which earlier thing a "she"/"it" refers to, memory gets confused not because one character
was mentioned a lot, but because SEVERAL earlier things all half-match the clue — two women, two similar objects. Our current
"interference" part watches the wrong thing (how busy one entity is) and on real text that almost never matters. The brain's
actual driver is how many OTHER things compete for the same partial clue, and it breaks the tie by reinstating WHEN/WHERE in
the discourse that thing was active. Build that tie-breaker and show it helps on real ambiguous references — honestly, since
the tricky part (how to combine the "what" clue with the "when" clue) is the piece we haven't built.

## 2. WHY THIS ONE
The stress-test proved the event-count interference axis is a near-dead lever on real text (+0.06, busy-entities only) AND
identified the right axis with a gate: content genuinely under-determines similar-competitor queries (0.398), so a
context-reinstatement cue has real room to help. It targets the measured #1 comprehension bottleneck (coref among similar
competitors) from a brain-faithful angle the other coref work has not tried.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** retrieval interference is CUE-OVERLOAD — a cue's diagnosticity falls as more items in memory match it
  (Van Dyke & McElree 2006; Watkins & Watkins fan; the Competition Model cue-validity the substrate already pins). Disambiguation
  among feature-matching competitors uses CONTEXT REINSTATEMENT — reactivating the temporal-discourse context in which the
  target was last active (Temporal Context Model, Howard & Kahana 2002; the substrate's `graded_temporal_context` already exists).
- **OUR-INVENTION (flag + sweep):** the exact combination rule for content-match × context-reinstatement (THE uncertain, unbuilt
  step — a reliability-weighted product? a gated race?); the similarity threshold defining a "competitor"; thresholds. Glass-box,
  no external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (the gate is CLEARED on the axis):** on a real similar-competitor ambiguous subset the content-only feature matcher
  scores 0.398 (≤ ~0.75 → content genuinely under-determines → build licensed). The event-count axis is falsified as the
  interference primitive on real text (Radvansky & Zacks). ⚠️ Naive recency ALONE ties the content-only floor — so the value is
  NOT recency and NOT content alone; it is their COMBINATION.
- **INFERRED (you build + measure):** whether a TCM context-reinstatement cue, COMBINED with content, beats the content-only
  floor on real ambiguous similar-competitor queries — the combination is the unbuilt step.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The event-COUNT interference axis (`resolve_retrieval_interference` synthetic win) — falsified on real text (+0.06 busy-only);
  do NOT re-model interference as event-count.
- Naive recency alone (ties content — a documented non-lever by itself); content alone (0.398 floor). The build MUST be the
  content × context COMBINATION, not either alone.
- `graded_temporal_context` (built) is the TCM context vector — CONSUME it, do not rebuild it.
- The coref phi-agreement pre-filter + the discourse-participant exclusion (integrated) are the syntactic residual — this is the
  COMPLEMENTARY memory axis, not that; compose, don't collide.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the stress-test's retrieval research note (`research_retrieval_interference_load_and_dg_boundary_2026-08-30.md`) + the
  similar-competitor gate cell — the cue-overload reframe, the 0.398 content-only floor, the pre-registered +0.10 HARD-PASS, and
  the recency-ties-content guard.
- Confirm on disk that the ambiguous similar-competitor subset + the content-only floor reproduce (0.398) before building.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On real similar-competitor / partial-cue queries (LitBank / OntoNotes coref, a pre-existing gold):
- **PASS =** the content × TCM-context-reinstatement cue beats the content-only floor by ≥ +0.10 hit@1, CI-separated (bootstrap;
  CI half-width + null p95), with the info-free twin (shuffled/permuted context) LOSING, AND it beats naive-recency-alone (the
  documented tie) — i.e. the COMBINATION is load-bearing, not either cue alone.
- **A rigorous NEGATIVE is a full PASS:** if content × context cannot beat content-alone on real ambiguous queries (the
  combination adds nothing), name why, enumerated — it closes the memory route and returns the residual to the syntactic axis.

## 8. FILES AND ENTRY POINTS
- Consumes: the stress-test's retrieval research note + gate cell; `hdlab/graded_temporal_context.py` (the TCM context);
  LitBank/OntoNotes coref (`data/corpora/`). Build + validate in `experiments/`; witness recomputes from source.
- Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (retrieval interference = similar-competitor cue-overload, not
  event-count; TCM context reinstatement is the disambiguator; the combination rule is the invention).


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
