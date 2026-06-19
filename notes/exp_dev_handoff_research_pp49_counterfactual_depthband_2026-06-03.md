# exp_dev hand-off -- research: PP-49 counterfactual depth-band capability deep dive

**Filed-by:** research sub-agent (Sonnet 4.6)
**Date:** 2026-06-03
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_pp49_counterfactual_depthband_capability_deep_dive_2026-06-03.md

**Per [[feedback-no-experiment-design-in-prompts]]:** This file passes TASK + WHY + CONTRACT + AUTONOMY only. exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA.

---

## Pause state

Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching. This handoff is allowed while paused (research delivery); exp_dev queue actions are gated on pause flag.

---

## Anchor candidates (rank-ordered)

### Rank 1: Protocol-fix anchor -- depth-5 root-start

**Anchor pointer:** pp49 counterfactual abduction at depth-5 with ROOT-START retrieval protocol (start from chain root, traverse to substitution depth, THEN measure cf_cos). Compare against predecessor-start (current broken protocol).

**Substrate-product reading:** If root-start depth-5 yields cf_cos >= 0.90, the depth-5 HARD_FAIL is confirmed as a measurement protocol artifact. PP-49 cap_map row (0.70-0.85) is defended; no downgrade. Phase 0.5b distillation MVP can proceed with PP-49 using root-start in the audit API.

**Tier hint:** CPU (pure numpy, N=4096, ~5 min wall). Should pass easily per algebraic prediction (cf_cos > 0.99 predicted at alpha=0.026).

**Why-now:** I-16 and I-15 in the compaction brief are unresolved. The research drill closes I-16 algebraically; the anchor closes it empirically. Strategy_request_to_exp_dev_pp49cf_r2_redesign_2026-06-03.md is awaiting a spec response -- root-start protocol IS the spec response.

---

### Rank 2: Depth envelope sweep -- root-start protocol

**Anchor pointer:** CF abduction sweep at depths d in {2, 5, 8, 10, 12} using root-start protocol at N=4096 and M_bg ~ 80-100. Maps the empirical d_max boundary; tests whether cf_cos(d) degrades monotonically per the formula erf(sqrt(N/(d + M_bg))).

**Substrate-product reading:** Confirms (or refutes) the formula cf_cos = erf(sqrt(N/M_total)) and establishes the N-dependent depth envelope for the product SLA: "counterfactual abduction supported to depth d_max(N, M_stored, theta)."

**Tier hint:** CPU (~30 min at N=4096, 5 seeds, 5 depths).

**Why-now:** The revised PP-49 product claim requires empirical d_max validation before the Phase 0.5b MVP demo.

---

### Rank 3: Rank-2 substitution primitive

**Anchor pointer:** Implement bidirectional counterfactual: replace both the inbound hop (d-1->d) and outbound hop (d->d+1) simultaneously. Starting from xi_B (retrieved by rank-1 step), verify the next-step counterfactual xi_C is retrievable. Tests whether rank-2 substitution bypasses the rank-1 0.50-ceiling for predecessor-start measurements.

**Substrate-product reading:** If rank-2 substitution achieves cf_cos >= 0.80 with predecessor-start protocol, it enables the "edit-and-continue" counterfactual product API pattern without requiring root traversal. More flexible than root-start for real-time audit queries.

**Tier hint:** CPU (~15 min at N=4096).

**Why-now:** Opens a new product API design option if root-start is inconvenient for streaming queries.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_pp49_counterfactual_depthband_capability_deep_dive_2026-06-03.md
- Existing depth-5 anchor script: d:/AI/hd-instrument/experiments/exp_pp49_hrc_counterfactual_depth_5_v1_n4096.py (predecessor-start, HARD_FAIL reference)
- Existing depth-8 anchor script: d:/AI/hd-instrument/experiments/exp_pp49_hrc_counterfactual_depth_8_v1_n4096.py (root-start, HARD_PASS reference)
- CF depth sweep script: d:/AI/hd-instrument/experiments/exp_pp49_hrc_cf_depth_band_sweep_v1_n4096.py (predecessor-start sweep, all-HARD_FAIL reference)
- exp_dev routing file: d:/AI/hd-instrument/notes/strategy_request_to_exp_dev_pp49cf_r2_redesign_2026-06-03.md (R2 redesign request)
- Compaction brief (I-15, I-16 open issues): d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md
- Blocked items: d:/AI/hd-instrument/data/blocked_items.json

---

## Contract

- Return format: one-line per [[research]] role contract.
- Pre-reg bands MUST be registered before queue_add per [[feedback-envelope-expansion-fail-bands]].
- Formula self-tests required per PROT-022: cf_cos formula inputs -> expected outputs.
- PROT-018: anchor name _nN suffix must match production N.
- No experiment design in dispatch prompt per [[feedback-no-experiment-design-in-prompts]].

## Autonomy declaration

exp_dev decides: specific anchor names, sweep grid values, threshold formulas, HP/MID/HF band numerical values, queue assignment (CPU vs GPU), wall-time estimates, timeout formula application, and which rank-1/rank-2 candidates to bundle into one dispatch vs separate anchors.
