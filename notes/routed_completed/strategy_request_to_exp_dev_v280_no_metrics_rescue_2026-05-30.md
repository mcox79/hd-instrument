# Strategy request → exp_dev — v280 NO_METRICS consolidated rescue (2026-05-30)

**Status.** Filed by verdict_handler during batched 41-verdict processing (v279 → v280). **NOT auto-dispatched per user explicit no-refill directive.** Surfaced for orchestrator main-thread decision when user resumes refill mode.

**Context.** Of the 41 verdicts processed in the v279 → v280 batch, 5 returned NO_METRICS (runner failures / OOM / timeout). One consolidated rescue routing rather than 5 individual notes per [[feedback-no-padding-experiments]].

## Rescue 1 (CHEAPEST, RECOMMENDED-FIRST) — TCFT erase_robustness N=8192 4 missing cell-seeds via laptop CPU

**Anchor.** `tcft_erase_robustness_n8192_v1_cpu` TIMEOUT 21600s on remote_cpu_queue; 41/45 partial cell-seeds salvaged via PROT-019 seed-checkpoint helper at `C:\dev\hd-instrument\data\exp_tcft_erase_robustness_n8192_v1_cpu\partial_metrics_*.json`.

**Gap.** 4 cell-seeds missing from 5 alphas × 3 splits × 3 seeds = 45 total grid.

**Recommendation.** Run a small completion script on laptop CPU (per [[feedback-laptop-cpu-quick-probes]]) that:
1. Reads existing `partial_metrics_*.json` to identify which (alpha, split, seed) cells are missing.
2. Runs ONLY those 4 missing cell-seeds with the same config (N=8192, smoke=False, same alphas/splits).
3. Aggregates with the 41 existing partials and emits a final composed verdict (HARD_PASS / MIDDLE_BAND from 45/45 cell coverage).

**Cost.** 21600s wall / 45 cell-seeds × 4 missing ≈ 30 minutes wall on laptop CPU.

**Benefit.** Salvages the 21600s remote_cpu_queue compute that was already spent; converts a NO_METRICS into a clean TCFT erase-robustness anchor for cap_map.

**Alternative (not recommended).** Re-ship full 45-cell at N=8192 on remote_cpu_queue (~21600s wasted again risk of same timeout).

## Rescue 2 (MEDIUM) — Bet B smoke-debug for 4 crashed N=2048 anchors

**Anchors.**
- `bet_b_tp_hdc_subspace_v1_n2048` — crashed early (25s wall)
- `bet_b_genreplay_phaseD_v1_n2048` — crashed early (19s wall)
- `bet_b_moe_per_task_dg_gating_v1_n2048` — crashed early (24s wall)
- `bet_b_4stage_n16384_v1` — failed 538s (likely OOM at N=16384 or runner-side crash)

**Gap.** Crashes too fast for substantive metrics; indicates either config error, import failure, or schema mismatch.

**Recommendation.** Single diagnostic dispatch reading the queue.json `error` field for each of the 4 anchors (cheapest 0-cost subsumption per v276 V6 R1 pattern); if `error` field empty or generic, run the 4 scripts locally at smoke=True N=128 to catch the failure mode without ship overhead.

**Cost.** 5 minutes wall (4 quick smokes on laptop or local cpu).

**Benefit.** Disambiguates "config-error / import-error / OOM-N-scaling / runtime-bug" before re-shipping at production scale; prevents repeat-crash compute waste.

**Notes on bet_b_4stage_n16384_v1.** 538s wall + N=16384 = consistent with CUDA OOM mid-experiment (N=16384 doubles memory vs N=8192); recommend N/2 bisect (N=16384 → N=12288 first) to disambiguate hard-OOM-N-ceiling vs script bug.

## Sequencing per [[feedback-rescue-sketch-first-sequencing]]

R1 (TCFT 4 cell-seeds) FIRST — cheapest, salvages largest prior compute investment.
R2 (Bet B smoke-debug 4 anchors) SECOND — diagnostic before re-ship; prevents repeat crash.

## NOT-auto-dispatched per user no-refill directive

Pause flag absent BUT user explicit no-refill directive HONORED. This rescue routing is filed for orchestrator main-thread decision when user resumes refill mode. NO exp_dev dispatched from this v280 entry.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
