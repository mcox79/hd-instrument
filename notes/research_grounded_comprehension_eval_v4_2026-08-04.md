# Grounded-comprehension eval v4 (DRAFT) — the category-labeled ruler

**Date:** 2026-08-04
**Deliverable:** `data/eval_gold_mention_role_mcguffey_v1/gold_grounded_comprehension_v4_DRAFT.jsonl` (14 items)
**Builder/validator (deterministic, glass-box):** `data/eval_gold_mention_role_mcguffey_v1/build_grounded_comprehension_v4.py`
**Status:** every item `gold_verified=false`, `needs_director_review=true`. DIRECTOR VERIFICATION REQUIRED before any use as gold.

## Purpose
Ruler for the breadth-building phase (supply grounded ~6yo knowledge → measure per-category
coverage). Bigger than the n=7 probe set and CATEGORIZED by the grounded-knowledge type each
item requires, so coverage can be tracked per category as knowledge is supplied. Each item is a
causal-attribution / grounded-comprehension probe tagged with `grounded_knowledge_category`.

## Total valid items
- **14 items authored**, all substring-guarded VERBATIM against the on-disk corpora (100% guard pass), **no span reuse** (every `true_blocker_span` / `distractor_span` / `query_span` / `action_span` / `surface_span` unique across items — verified programmatically).
- **11 FULL baseline-defeat** (defeat BOTH recency and surface). **3 flagged PARTIAL/HOLD** (recorded, not silently counted — see below).

## Per-category counts (all 14 authored — 2 per category, balanced)
| category | authored | full baseline-defeat |
|---|---|---|
| physical_harm | 2 | 2 |
| multi_candidate_attribution | 2 | 1 |
| counterfactual_cause | 2 | 1 |
| out_of_span_cause | 2 | 2 |
| beneficiary_vs_patient | 2 | 2 |
| irony | 2 | 2 |
| goal_blocking | 2 | 1 |
| **total** | **14** | **11** |

## Measured baseline-defeat (computed, not eyeballed)
- **RECENCY-wrong: 11/12 applicable** (recency = candidate whose span is nearest the query by absolute line distance; item passes if it predicts the DISTRACTOR). Irony items (2) are recency-n/a. The 1 non-defeat = `grapp_v4_010` (see partials).
- **SURFACE-nonseparating: 12/14** (harm/valence word-boundary lexicon on true vs distractor span; item passes if surface does NOT strictly favour the true cause). The 2 that separate = `grapp_v4_002`, `grapp_v4_004` (see partials).

## Partial / HOLD items (flagged for Director, not counted as full)
- **grapp_v4_002 (torn book, mca):** defeats recency (Tom's post-query false confession is the nearest salient claim) but the true-cause span literally contains the query word "tear" → a lexical-overlap/surface reader could separate it. HOLD.
- **grapp_v4_004 (liniment, counterfactual):** defeats recency but Marilla's true-cause span contains "broke" (broke the bottle) → surface harm-lexicon favours the true span. HOLD.
- **grapp_v4_010 (left-behind child, goal_blocking):** defeats the STATED-PRETEXT (surface) baseline — the official reason is "Mother's wish / weak eyes" while the real cause is Jo's selfish crossness — but Jo's forceful refusal is proximate to the outcome, so a pure recency baseline coincidentally lands on the true blocker. HOLD.

## True-cause POSITION distribution (deliberately varied — defeats the detective-v3 "true-cause-always-last" confound)
Of the 10 attribution-structured items: **6 true-cause-BEFORE-query** (backward-causal: true cause precedes the query while a nearer distractor sits between), **4 true-cause-AFTER-query** (the true cause is revealed after the question — greenhair peddler, Potter/Joe frame, Europe self-fault, +1). Beneficiary (2) and irony (2) are position-n/a by structure. True cause is NOT always the most-recent nor always-last.

## Sources (all public-domain, Project Gutenberg)
- Anne of Green Gables (Montgomery) — 7 items
- The Adventures of Tom Sawyer (Twain) — 3 items
- The Wonderful Wizard of Oz (Baum) — 2 items
- Little Women (Alcott) — 2 items

## Honest yield — which categories were HARD to source
- **physical_harm and goal_blocking are the hardest to make BASELINE-DEFEATING.** Direct physical-harm scenes (Tom's cat + Pain-killer, Dorothy melting the Witch) and goal-blocking scenes (Amy burns Jo's book; the play refusal) STRUCTURALLY let recency/surface win, because the harm act (or the blocker) is normally the proximate/recent, surface-loaded event. Those were rejected. The baseline-defeating instances required **displaced causation**: the Tin Woodman's enchanted axe (proximate = axe/self, true = the Witch bribed by the old woman), and Jo passed over for Europe (proximate = Amy the replacement, true = Jo's own past blunt manners). This is itself a finding: recency-defeating physical_harm/goal_blocking items are exactly the ones where the harm/block is NOT the recent event.
- **counterfactual_cause and mca surface-leak** when the true-cause span narrates the act with a harm/lexical-overlap verb (torn 'tear', liniment 'broke') → 2 of these fell to PARTIAL.
- **out_of_span_cause, beneficiary_vs_patient, irony** sourced cleanly (2 full each). out_of_span leaned on deception/false-attribution scenes (peddler's dye claim; Joe framing Potter).

## Merge reference — this EXTENDS, does not duplicate, the Director-verified set
Existing Director-verified items (spot-verified 2026-08-03; DISTINCT spans from all v4 items):
- `gold_grounded_appraisal_richer_v1.jsonl`: grapp_mcca_001/003/004/005, grapp_irony_001/002/003, grapp_sincere_001/002/003, grapp_benpat_001–005 (15 items).
- `gold_grounded_causal_crossspan_v2_DRAFT.jsonl`: grapp_mcca_007/008/009 (Director-verified). **EXCLUDE grapp_mcca_006.**
v4 uses fresh, non-overlapping spans (guarded), so the combined ruler = 15 verified + 14 v4-draft (11 full / 3 hold), pending Director verification of the v4 set.

## Schema notes
- `grounded_knowledge_category` per item; leak-safe `goal_description_leaksafe` (never names the goal_owner — avoids the item-007 leak class).
- Solver-facing fields = the spans; gold-label fields are prefixed `_forbidden_*` (true_blocker_agent / true_beneficiary / true_intent_valence) and separated from discriminating text.
- Per item: measured `recency_baseline_prediction` + `recency_baseline_correct`, `surface_harm_score_*` + `surface_separates_true`, `true_cause_position_vs_query`, `passes_baseline_defeat` (+ `baseline_defeat_note` when partial), `verify_flag`, `coherence_justification`.

## Guards honored
Deterministic; contamination-guarded (verbatim substring reconstruction from disk); glass-box; local commit only (NO push, no remote queue). Nothing marked `gold_verified=true` — Director verifies.
