# Exp Dev — v188 queue-refill pickup-ready hand-off (GPU drained to 0; CPU 8 pending)

**From**: Orchestrator inline cycle (2026-05-24 14:45 local; verdict_handler role inline)
**To**: Exp Dev (next cycle)
**Triggering verdict**: v188 LONGER_PHASEA_MIDDLE_BAND (compound + longer Phase-A adds +0.2pp; intrinsic compound ceiling at 91-92% CONFIRMED; user pre-cycle structural-axis-question framing empirically established across 4 converging-PARTIAL probes)
**Cap_map**: v188 (commit d905aa3 local; push pending main-thread authorization)
**Pause state**: ACTIVE (no `orchestrator_paused.flag`)

## Why this hand-off exists (and is NOT a script-ship)

Per [[feedback-no-experiment-design-in-prompts]]: orchestrator main thread MUST NOT design experimental parameters (N, M, seeds, thresholds, queue, formula details) for exp_dev. The items below are pickup-ready -- design intent + pointer-to-prior-hand-offs only -- exp_dev decides parameters.

Per [[feedback-pipeline-pacing]]: GPU queue drained to 0 at v188 verdict-event preamble (user-stated; state_check confirmed `gpu_q:0 cpu_q:8`). Pipeline-pacing reflex FIRES this cycle. Refill target: **2 GPU + 1-2 CPU** from the remaining 10 pickup-ready anchors in the existing two hand-offs:

- `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` (v183 post-batch anchors; Ablation A + B CONSUMED at v185 + v186; remaining: F-6 Boolean re-ship + SSM/S4 re-queue + Sellke re-queue + MS_1ST_ORDER script-fix)
- `notes/strategy_untested_rows_triage_2026-05-24.md` (v184 KILLER/UNSURE triage; 6 anchors; consumption status uncertain post-14:37 batch ship -- see status_log entry at 14:37:58)

## Action by next exp_dev cycle

1. Read this file + both prior hand-offs.
2. Cross-reference the 14:37:58 status_log entry (`{"event_kind":"exp_dev_ship","summary":"5-anchor parallel ship for v187 follow-up + triage-A KILLERs/UNSUREs..."}`) to determine which anchors are ALREADY shipped this turn vs which remain.
3. Design + ship the highest-leverage REMAINING 2 GPU + 1-2 CPU anchors. Exp_dev's call which.

## Priority pointers (locked by Strategy v183 + v184 + v188 rankings)

| Priority order | Source hand-off | Highest-leverage GPU candidates (exp_dev confirms unshipped) |
|---|---|---|
| **1 GPU** | v187 LIVE-TOP-PRIORITY routing | **compound + THIRD axis** (compound per-task + replay + MoE stacked OR compound + Lane D 4-stage OR compound + eligibility-trace consolidation). This is the cheapest remaining HARD-PASS path per v187 + v188 cap_map; exp_dev picks which of three third-axis options. Base script reuse: `experiments/exp_wave14d_betB_kovacs_v1.py` with third-axis extension. |
| **2 GPU** | v185/v188 Lane D 4-stage Priority A KILLER T1 routing | **Lane D 4-stage continual learning (A->B->C->D)** -- K2 KILLER Tier-1 per triage; extension of v103 Lane D 3-stage ✅. May overlap with "1 GPU" if exp_dev picks Lane D as the third axis; in that case ship a different second-GPU anchor (e.g., compound + MoE stacked, OR compound + eligibility-trace, OR K4 cross-modal binding if image-embedding source decided). |

| Priority order | Source hand-off | Highest-leverage CPU candidates (exp_dev confirms unshipped) |
|---|---|---|
| **1 CPU** | v184 triage Priority A #1 | **K6/U8 Compositional generalization hold-out probe** -- if shipped at 14:37, pick next-highest remaining. Otherwise ship per triage. |
| **2 CPU (optional)** | v184 triage Priority A #6 | **A6 Learned codebook atoms A/B** (SVD/PCA of bigram PPMI vs random-bipolar) -- ~15 min CPU per v1 estimate; cheapest item; A/B against random bipolar. |

## Falsifier discipline citations

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev decides N, M, seeds, thresholds, formula details, exact anchor names.
Per [[feedback-no-smoke]]: both HARD-PASS and HARD-FAIL bands MUST be falsifiable BEFORE running.
Per [[feedback-envelope-expansion-fail-bands]]: each prereg carries pre-registered HARD-PASS + HARD-FAIL bands.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print() / verdict_msg (Windows cp1252 stdout crashes on emoji/em-dash).
Per [[feedback-rehabilitation-after-rejection]]: v188 confirms longer-Phase-A axis adds essentially nothing on top of compound; further variants of "more consolidation time" or "more replay fraction" are OFF-LIMITS (5th converging-PARTIAL probe on the same axis would be diminishing-returns).

## Queue state at hand-off (verified 2026-05-24 14:45 local via state_check.py)

- **overnight_queue (GPU)**: 0 pending (drained per v188 verdict-event preamble; pipeline-pacing FIRES).
- **remote_cpu_queue**: 8 pending (state_check output `cpu_q:8`; no emergency-refill).
- **local_cpu_queue**: idle (state_check `local:DEAD`; revival per `project_cpu_resource_underutilized` still pending separately).

Pipeline-pacing invariant per [[feedback-pipeline-pacing]]: target depth >= 1 on both GPU and CPU. GPU drained = refill priority; CPU healthy = optional refill only.

## Strategic context (v188 informs design)

The compound (per-task + replay) ceiling at 91-92% is CONFIRMED INTRINSIC. The third-axis tests (compound + MoE / Lane D 4-stage / eligibility-trace) are the most strategically important next probes because they either:
- (a) CLEAR HARD-PASS 0.95 -> Bet B retention 🟡 -> ✅ promotion (highest portfolio-impact outcome possible this week), OR
- (b) ALSO PARTIAL -> empirically establish that the entire "rehab via mechanism stacking on existing axes" path is bounded, forcing the v188-NEW scope-rescoping option (accept 91-92% ceiling at current envelope; reserve 0.95 for specific M_crit(K) cells). Either outcome is high-information.

Parallel: the v188 Research drill on the Bet B retention ceiling FIFTH-MECHANISM candidate (filed at `notes/research_request_betB_fifth_mechanism_2026-05-24.md`) is dispatched in parallel. Research designs the question; if Research surfaces a high-P substrate-novel candidate from a DIFFERENT framework, that's a new exp_dev anchor for the cycle after next.

## No blockers

Routing notes already exist. Exp_dev reads `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` + `notes/strategy_untested_rows_triage_2026-05-24.md` + this file. Designs preregs per [[feedback-no-experiment-design-in-prompts]]. Ships.

## PROT discipline

- Per [[feedback-no-experiment-design-in-prompts]]: no N / M / seed / threshold / formula specification in this note; only WHAT + WHY + pointer-to-base-script.
- Per [[feedback-structural-agent-usage-mandate]]: this filing routes to next exp_dev cycle (does NOT design experiments in main thread).
- Per [[feedback-dispatch-wrappers-default]]: orchestrator main-thread role is routing + permission + quick mechanical; this hand-off is the routing mechanism.
- Per [[feedback-pipeline-pacing]]: queue-refill reflex fires on GPU=0 + ACTIVE pause-flag state; both met.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
