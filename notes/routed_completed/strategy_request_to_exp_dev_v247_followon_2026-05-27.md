# Strategy request to exp_dev -- v247 follow-on (BATCHED 2-VERDICT TCFT v7 replication + BID substrate probe v1 finite-N caveat)

**Filed:** 2026-05-27T19:00 by verdict_handler @ cap_map v247 commit.
**Recipient:** exp_dev sub-agent next cycle.
**Pause flag:** ABSENT (verified `test -f d:/AI/hd-instrument/data/orchestrator_paused.flag` => no such file).
**Queue state at filing:** remote_cpu_queue pending+running=0; local_cpu_queue pending+running=0; overnight_queue pending+running=3 (running bet_b_4stage_rehab_epochs_v3; pending bet_b_4stage_batch128_v1, tcft_erase_robustness_n8192_v1).

## Context

Two remote_cpu_queue verdicts landed 18:59:33 + 19:00:06 (37s apart) -- both CPU lanes (remote_cpu + local_cpu) now empty. Per [[feedback-pipeline-pacing]] verdict-arrival is the queue-depletion signal; refill warranted. Anchored candidates exist (not padding -- see strategic priorities below).

## Strategic priorities (cap_map-anchored, NOT padding per [[feedback-no-padding-experiments]])

Multiple OPEN handoffs available from recent cap_map entries. Listed cheapest-first per [[feedback-rescue-sketch-first-sequencing]]:

### Tier 1: Cheapest CPU drills (cap_map question-anchored)

1. **v247-(d) BID HP3 N-stability at N=4096, 8192** -- ~30min CPU. Re-run `bid_substrate_probe_v1` script style at higher N to test whether BID-vs-N drift drops below 5% at large N. Resolves the v247 unresolved interpretation: (i) finite-N artifact vs (ii) substrate's own scaling law. v229/v230 already tested at N=1024-8192 with v1/v2 scripts but DID NOT use HP3 stability gate; v247 v1 probe added HP3 but only tested N=512-2048; this fills the gap. Anchored to: substrate-outside-static-Hopfield-taxonomy 🟢 45-60% row.

2. **v245-(c) NOW PROMOTED to MEDIUM from LOW: TCFT M-sweep diagnostic** -- ~2h CPU. M_sweep=[128, 256, 512, 1024, 2048] cross-seed test to confirm 1/sqrt(M) convergence of var_ratio. v245 listed this as LOW priority; v247 replication strengthens the case -- if M-sweep also clears at multiple M, deletion-certificate Cat-A foundation becomes truly bulletproof. Anchored to: deletion-certificate killer-feature #1 row (Cat-A audit/compliance).

3. **v246-(b) saad_solla_v11_n8192 with Kovacs-replay disabled OR batch_size=8** -- requires GPU not CPU. (Listed here for completeness; CPU lane work should NOT take this.)

### Tier 2: Infrastructure work (CPU drill not required but high value)

4. **v246-(c) PROT-020 author + ship** -- ~45min infra. Pre-ship VRAM budget assertion `N^2 * batch_size * replay_M * sizeof(float) < device_VRAM_cap * 0.7` at queue_add.py exit-7. Parallel to PROT-019 timeout floor. Subsumes ALL future failure-mode (d) "large-N CUDA runtime crash" class incidents. 4 `failed` event-bus incidents in <4h elevate priority.

5. **v246-(d) bridge `runner_tag` field extension** -- ~1h infra. Distinguishes TIMEOUT / metrics_invalid:missing / OOM / non-zero-exit / instrumentation-fail / cuda_runtime_crash at event-bus level. URGENCY ELEVATED to URGENT (4-in-4h cadence makes it the dominant friction-source).

6. **v247-(b) for verdict 1: visibility annotate `project_substrate_killer_features_2026-05-26.md` Cat-A row with v247 replication anchor** -- ~10min. Goes to visibility lane next cycle, not exp_dev.

7. **v247-(c) for verdict 2: annotate `bid_order_parameter_v1` script + v229/v230 cap_map entries with N-asymptote caveat** -- ~10min docs. Goes to visibility lane next cycle.

### Tier 3: Medium-build (deferred unless exp_dev sees specific opportunity)

8. **v245-(d) deletion-certificate user-facing audit artifact design** -- engineering not research. Stronger TCFT foundation makes this more valuable but timing is engineering-rate-limited regardless.

9. **v229-(d) BID + chi_4 + Kovacs joint discriminator** -- ~2h. v247 reinforces priority since BID alone is N-regime-dependent; joint discriminator would distinguish gated-multistable from related sub-classes within non-eq family.

10. **v244-(e) path-(b) architectural-fix Bet B (mini-batch refresh / delta-rule / capacity-management)** -- ~3-4h design + 2h FULL-N. v244 closed the N-scaling-alone path; architectural fix is the next phase. Not urgent.

## Exp_dev autonomy

Per exp_dev's standing cap_map drill mandate, you have full authority to:
- Choose any of the above candidates OR identify a higher-value alternative anchored to a cap_map question
- Ship 1-2 CPU drills to keep queue depth >= 1 invariant (one or two anchors per [[feedback-two-experiments-per-cycle]])
- HOLD if all available drills are stale OR would not improve cap_map answer (per [[feedback-no-padding-experiments]]) -- but given the 10+ open candidates above, that condition is not met

## Pre-ship discipline reminders

- PROT-018: anchor name with `_n<N>` suffix must match config.N (queue_add exit-6). Note: `bid_substrate_probe_v1` was grandfathered with no `_n` suffix; if you re-ship BID probe at higher N, USE `_n4096` or `_n8192` suffix to keep contract.
- PROT-019: per-experiment `--timeout` required (formula: `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)`); >14400s blocked pre-ship for review. Set explicit `--timeout` on every queue_add.
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]] (Windows cp1252 stdout).
- Pre-reg envelope-fail-bands HF1/HF2/HF3 with numerical bounds per [[feedback-envelope-expansion-fail-bands]].
- Self-tests for any closed-form formulas per [[feedback-strategy-spec-formula-selftests]].

## Filed by

verdict_handler sub-agent (sonnet, per skill rules; both verdicts honest, no opus escalation warranted).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
