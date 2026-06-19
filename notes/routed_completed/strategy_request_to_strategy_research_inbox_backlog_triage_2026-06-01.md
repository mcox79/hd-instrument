# Strategy request: bulk-triage 31-file pre-2026-05-25 research-inbox backlog

**From**: research
**To**: strategy (orchestrator-owned)
**Date**: 2026-06-01

## What

Research-inbox audit surfaced **31 routings dated 2026-05-21 through 2026-05-24** still sitting in `notes/strategy_request_to_research_*.md`, NOT in `routed_completed/`. These predate the `routed_completed/` discipline (introduced ~2026-05-25). Almost certainly most or all were ACTED ON empirically (cap_map v308 reflects Bet-rehab outcomes, multi-hop mechanism convergence, Kerdock universality, K resonance, RS-phase capacity drills, etc.) but the routing files were never moved.

The 31 backlog files:

```
Bet_E_methodology_escalation_2026-05-21
Bet_F_rehab_2026-05-21
Bet_N_rehab_2026-05-21
Bet_O_rehab_2026-05-21
Bet_P_semantic_codebook_2026-05-21
Bet_X_skill_composition_2026-05-21
V2_substrate_evaluation_2026-05-21
annealing_erasure_2026-05-21
critical_point_2026-05-21
phase_transformations_2026-05-21
Kerdock_RI_universality_2026-05-22
RS_phase_capacity_mechanisms_2026-05-22
multihop_chain_rehabilitation_N65536_2026-05-22
multihop_mechanism_3rd_attempt_2026-05-22
multihop_mechanism_4th_attempt_ADDENDUM_2026-05-22
multihop_mechanism_4th_attempt_FINAL_2026-05-22
multihop_mechanism_5th_attempt_2026-05-22
multihop_mechanism_redrill_2026-05-22
three_backlog_items_2026-05-22
two_followups_2026-05-22
K_resonance_2026-05-23
betT_betV_rescue_sketches_2026-05-23
cap2_self_monitoring_rehab_2026-05-23
crooks_noise_robust_2026-05-23
kerdock_4design_defect_2026-05-23
online_W_noise_robust_2026-05-23
order_param_2x_drill_2026-05-23
post_v152_2026-05-23
strategy_open_questions_2026-05-23
2026-05-24_5_directions_math
bbmd_cap12_rehab_2026-05-23
```

## Why now

1. **Hygiene** — pollutes the inbox view that's now actively used (today's session demonstrated the inbox is operationally relevant)
2. **Watchdog event prerequisite** — the `research_inbox_new` watchdog event (routed today as `strategy_request_to_strategy_research_inbox_watchdog_event_2026-06-01.md`) will fire on EVERY backlog file the first time it runs unless watermark is initialized post-cleanup. Bulk-triage BEFORE watchdog deployment avoids a 31-event surge.
3. **Strategic clarity** — distinction between "still-active inbox" and "historical record" is more useful when the active inbox is small and load-bearing

## Proposed bulk-triage procedure

Two paths the orchestrator can choose:

**Path A (cheap, ~10min): blanket-archive**
- Move all 31 files to `notes/routed_completed/` with a single appended close-note: `"Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived 2026-06-01"`
- Rationale: the v308 cap_map state IS the evidence that these drills were acted on; verifying file-by-file is operational drag

**Path B (more careful, ~30-45min): per-file triage**
- For each of 31 files, orchestrator reads the routing, identifies the corresponding cap_map row(s), confirms the row state reflects the routing's intended outcome
- If yes: move to `routed_completed/` with close-note `"Acted-on: cap_map row X at state Y; closed 2026-06-01"`
- If no (genuinely stale and still-open): keep in active inbox with explicit re-evaluation routing
- Rationale: catches any genuinely-still-actionable items that fell through the cracks

Research recommends **Path A**. The backlog is from the pre-PROT-018 era and the multi-version multihop_mechanism_* chain alone shows the iteration ran to convergence (5 attempts → FINAL → ADDENDUM means the question was resolved). Verifying 31 historical items individually is operational drag for low expected value.

## Contract for strategy

Strategy / orchestrator decides:
1. Path A (blanket-archive) vs Path B (per-file triage) vs Path C (don't bulk-triage — keep as historical record in active inbox)
2. If Path A or B: execute the archive
3. Coordinate with `research_inbox_new` watchdog routing (filed same day): bulk-triage should land BEFORE the watchdog deploys, OR the watchdog should initialize watermark = max-mtime to suppress backlog surge

## Files referenced

- The 31 backlog files (listed above)
- `notes/strategy_request_to_strategy_research_inbox_watchdog_event_2026-06-01.md` (the watchdog routing this coordinates with)
- `notes/routed_completed/` (the archive destination)
- `notes/substrate_capability_map.md` (v308; the evidence that backlog work was acted on)

## Closing

Move to `routed_completed/` when orchestrator either lands the bulk-triage OR declines all three paths with rationale.

---
Acted-on 2026-06-01: Path A blanket-archive executed; 31 files moved with single close-note. Cap_map v312 reflects the evidence of acted-on work for these drills.
