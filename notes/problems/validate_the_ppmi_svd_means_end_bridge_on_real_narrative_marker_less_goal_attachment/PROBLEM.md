---
review: EXCELLENT
review_text: Reverified first-hand test_contextual_goal_attachment_modern.py 4/4 (+5/5+9/9). The brief's context-free ATOMIC means-end bridge is a LOCATED NEGATIVE (in the info-free twin band); the brain's CONTEXTUAL inverse planning (situation-relatedness) wins CI-sep on modern gold (K1 0.700 vs twin 0.483). LANDED (Q111, DEFAULT-ON, gated goal_purpose_filter): (1) the ADVCL PURPOSE FILTER in hdlab/goal_register.extract_goals (keep bare-purpose iff the infinitive's arc-labeler deprel is advcl, reject xcomp/ccomp/acl -- upstream net-positive on why(), 5.5:1), consuming the reader's own arc labeler over the consolidated arc-eager parse via _frontend_labeler; (2) the CONTEXTUAL _link_open_stack edge in hdlab/goal_hierarchy_graph (attach a marker-less action to the situation-most-related open goal via the associative store, margin-gated, replacing recency), flipped link_open_stack=True in _read_goals with the reader's sentence tokens as the situation. ADDITIVE (fills only previously-parentless action nodes; the flat register + why()/wants() unchanged; self-test PASS). Board: the purpose-filter is the goal-why board lever; the contextual edge enriches the goal graph (marker-less real-narrative attachment) which the current board under-scores (goal_hierarchy arm = explicit-goal battery) -- K1 0.700 needs a mined marker-less gold (instrument gap). NO PARSER WORK (the parser was reused unchanged). §2b folded. INTEGRATED 2026-09-05.
---

# PROBLEM: the goal→subgoal hierarchy graph is landed (default-on), but 10.8% of stated goals on real 19c prose are ISOLATED — marker-less actions with no explicit superordinate link. The solver CRACKED this on a small authored PoC: a graded PPMI+SVD means-end bridge over ATOMIC (xIntent/xWant CSKG — "why PersonX did the event" = the goal), the SAME curated-bridge pattern as the landed 0.700 discourse-fact bridge, reaches 0.9375 on ATOMIC-covered verbs + held-out generalization AUC 0.68, with a reliability GATE that abstains on no-signal items — but it is n=16 authored items with hand distractors. VALIDATE the PPMI+SVD means-end bridge on REAL LitBank marker-less actions with a COVERAGE CURVE, wired as a RELIABILITY-GATED edge type (fire only when a goal is on the open-stack AND the fit clears the margin — the discfact real-text lesson that an ungated bridge HURTS the no-means-end complement), lifting isolated-goal attachment CI-separated over the recency-0.0 floor with an info-free shuffled-index twin LOSING and NO-regress on the explicit-chain goal arm; report the honest ATOMIC verb-coverage bound (softened by the SVD generalization). Glass-box, NO external LLM; ATOMIC is a static offline curated asset (admissible).

**slug:** `validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment` — **opened:** 2026-09-05 by the strategy session, the explicit NEXT-STEPS #2 the goal-hierarchy SOLVED note named (the landed graph leaves 10.8% of goals isolated; the PPMI+SVD means-end bridge cracked it on an authored PoC and now needs real-narrative validation as a reliability-gated edge type). **status:** OPEN. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE. Glass-box, NO external LLM; ATOMIC is an admissible static offline curated asset (owner 2026-08-16).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a character does something to serve a larger aim, a reader connects the small action to the big goal even when the story never spells out the link with a word like "so" or "in order to." The reader's goal-tracking graph is built and working, but on real old prose about one in ten stated goals is left dangling with no such connector. On a small hand-made test set, a method that scores "does this action plausibly serve that goal" — using a curated commonsense resource about why people do things — got it right most of the time and even generalized to unseen verbs, and it knew when to stay silent on cases it couldn't judge. The catch: that test was only 16 hand-authored items. The job is to check whether it holds up on REAL story text, measure how far its knowledge actually reaches, and wire it in as a cautious link that only fires when it is confident and a matching goal is actually open — because an over-eager version was already shown to HURT the cases with no such link.

## 2. WHY THIS ONE — a proven-on-PoC lever that closes a measured 10.8% gap in a landed, default-on organ
The goal-hierarchy graph is live and default-on, and the isolated-goal gap is measured on real prose (10.8%). The bridge is the SAME curated-bridge pattern that already landed at 0.700 for discourse facts, and the PoC numbers are strong (0.9375 covered, AUC 0.68 held-out, with a working abstain gate). This is validating an already-cracked mechanism on real text and wiring it as a gated edge — high-value, low-invention, and it directly extends a landed organ rather than starting cold.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — goal-hierarchy SOLVED §3/§5b/§7):** 10.8% of stated goals on real 19c prose are isolated; the PoC ladder 0.375 binary set-membership → 0.688 counts → 0.9375 PPMI+SVD, held-out generalization AUC 0.68, plus a working reliability gate that abstains on no-signal items — all on n=16 authored items with hand distractors; the discfact real-text lesson that an UNGATED bridge hurts the no-means-end complement.
- **INFERRED (you must measure):** the real-narrative (LitBank marker-less action) coverage curve and whether gated attachment lifts CI-separated over the recency-0.0 floor with the shuffled-index twin losing and no-regress on the explicit-chain goal arm.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension/SOLVED.md` §3, §5b, §7, and NEXT STEPS #2 IN FULL; read `experiments/exp_goal_hierarchy_markerless_bridge_v1.py` (the PoC) IN FULL.
- Check `tools/substrate_map.py` / `hdlab/` FIRST: read `hdlab/goal_hierarchy_graph.py` (the landed graph + the `link_open_stack` Tier-2 hook), `experiments/exp_discfact_store_bridging_graded_v1` (the landed 0.700 curated bridge + its ungated-hurts lesson), `hdlab/graded_competition`, `hdlab/reasoner.py`.
- Reproduce first-hand: the PoC 0.9375 covered + the abstain gate; the 10.8% isolated-goal measurement on real prose (the gap to close + the recency-0.0 can-fail floor).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = the PPMI+SVD means-end bridge validated on REAL LitBank marker-less actions with a COVERAGE CURVE, wired as a RELIABILITY-GATED edge type in `build_goal_graph` (fires only when a goal is on the open-stack AND the fit clears the margin), lifting isolated-goal attachment CI-separated over the recency-0.0 floor, with an info-free shuffled-index twin LOSING and NO-regress on the explicit-chain goal arm; the honest ATOMIC verb-coverage bound reported (softened by the SVD generalization). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the bridge cannot generalize to real marker-less actions beyond ATOMIC coverage (with the named coverage number) — is a FULL PASS. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE.

## ALREADY TRIED / DO NOT REDO
- Binary set-membership scoring — 0.375, ties on real distractors. Do NOT re-attempt binary membership; the graded PPMI+SVD is the mechanism.
- An UNGATED bridge — hurts the no-means-end complement (the discfact real-text lesson). The edge MUST be reliability-gated.
- Do NOT over-tune the n=16 PoC — single-config overfit; hold the replication-gate discipline (validate on real text, do not tune to the authored set).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/goal_hierarchy_graph.py` (the landed graph + `link_open_stack` Tier-2 hook), `experiments/exp_goal_hierarchy_markerless_bridge_v1.py` (the PoC), `experiments/exp_discfact_store_bridging_graded_v1`, `hdlab/graded_competition`, `hdlab/reasoner.py`. ATOMIC ships as a static offline curated asset (`data/frontend_assets/`). Measure on the isolated-goal / explicit-chain goal arms. Strategy lands the Q111 wire (the reliability-gated edge type in `build_goal_graph`); fold a §2b AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`.

## DO NOT QUOTE
- Do NOT quote the 0.9375 as a deployment result — it is the ATOMIC-covered authored PoC number; report the real-narrative coverage-curve + gated attachment lift.
- Do NOT quote a gain without the shuffled-index info-free twin LOSING + explicit-chain no-regress.
- Do NOT use an external LLM (the invariant).
