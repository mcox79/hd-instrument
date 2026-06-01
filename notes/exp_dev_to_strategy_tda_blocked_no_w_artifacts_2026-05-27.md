# exp_dev upstream push: TDA reanalysis blocked -- no W tensor artifacts found

**Date:** 2026-05-27
**Source handoff:** notes/exp_dev_handoff_tda_reanalysis_substrate_W_2026-05-27.md
**Blocking condition:** dependency not satisfied

## What was requested

TDA re-analysis on existing W artifacts from v200-era MoE experiments + battery v1 fixtures.
The handoff explicitly states: "No new W generation. No GPU. CPU-only. Existing artifacts only."

## What was found

Searched all data/ directories for saved W tensor files:
- Searched for *.pt, W_*.npy, weight_matrix* across all data/ subdirectories.
- Found: ZERO saved W artifacts.

All experiment data directories (exp_wave14_moe_shift_K_perarm_v1/, exp_wave14_moe_cosine_router_v1/, etc.) contain ONLY metrics.json files. No W matrices were saved during any prior MoE or battery run.

The battery v1 fixtures (exp_anchor_novel_phase_battery_v1/, v2/, v3_n8192/) also contain only metrics.json.

## Decision

Cannot ship TDA anchor. The "No new W generation" constraint in the handoff means this probe
requires W artifacts that do not exist in the local data store.

## Suggested resolution

Strategy options (not exp_dev's call):
(a) Modify a prior MoE or battery script to ALSO save W matrices, then re-run; TDA reanalysis follows.
(b) Relax the "no new W generation" constraint to allow a minimal CPU W-generation pass.
(c) Deprioritize TDA given that BID (bid_substrate_probe_v1) is a cheaper framework-free discriminator that was also shipped this cycle.
