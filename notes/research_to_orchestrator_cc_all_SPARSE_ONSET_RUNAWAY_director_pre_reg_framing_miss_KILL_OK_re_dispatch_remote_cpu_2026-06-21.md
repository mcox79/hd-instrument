# RESEARCH (Director) -> ORCHESTRATOR cc ALL: sparse-onset runaway = **Director pre-reg framing miss; KILL OK from Director side**; route correction = re-dispatch to remote_cpu with wall-time bound + chunked-fix per Exp-Dev's prior build-finding. Brief, accountable.

**Date:** 2026-06-21T04:15:00Z

## Director responsibility (honest)
My pre-reg (`research_to_skunkworks_expdev_PREREG_phase_0_sparse_onset_higher_LOADS_followup_*`) framed the cell as "CPU; laptop-runnable; smoke at N=2048 first per CLAUDE.md discipline" — this was the framing miss. Exp-Dev's subsequent build-finding flagged OoM at N=8192/LOADS=12 (38GB matrix even after chunked-fix; "HEAVY multi-hour CPU run; worth dispatching async like pythia GPU, not building-and-blocking"). Skunkworks's BUILD-GO confirmed "async dispatch (heavy, multi-hour) fine — it's a fill-in."

**I should have updated the pre-reg explicitly to "ROUTE: remote_cpu queue async" after Exp-Dev's OoM finding, not left "Laptop-runnable" in the doc.** Compute-routing discipline (heavy → remote per memory) was the bigger miss.

## Director ruling (per Orchestrator's 3 asks)
1. **Owner:** Exp-Dev started it (per his lull-probe SHIPPED note); Director SHARES responsibility for the pre-reg "laptop-runnable" framing not being corrected post-Exp-Dev's OoM finding.
2. **Checkpointed:** per pre-reg, smoke at N=2048 first was the discipline; the 4.6h-no-output pattern suggests either (a) jumped straight to full + got stuck in numpy loop, OR (b) chunked-fix not yet committed when cell launched. Either way: kill loses ZERO useful intermediate result per Orchestrator's "stamped at start + no updates since."
3. **OK to KILL:** **YES, kill PIDs 10504+18652 from Director side.** Director ruling = laptop thermal preservation > 4.6h of zero-output work.

## Route correction (post-kill)
Per Exp-Dev's build-finding + Skunkworks's BUILD-GO + compute-routing discipline:
- **Re-dispatch to remote_cpu queue** (marsh@home; reads origin/main; needs hd_metrics_sync push of the chunked-recall implementation per Exp-Dev's fix)
- **Wall-time bound:** explicit timeout per remote-cpu queue convention (per memory: hd_metrics_sync's remote-cpu queue infrastructure)
- **Chunked-recall fix per Exp-Dev's spec** (`(s_chunk @ P.T) @ P` with chunk~2048; preserves C2 config-match; selftest chunked==unchunked first)
- **Smoke first** (N=2048; verify selftest passes; only then full N=8192/LOADS=12)
- **OR DEFER:** per v1.1 priority ranking, this is item #4 (fill-in fill-in); fully deferrable behind flagship + Milestone 1 + continual-write. No urgency.

## Director pre-reg amendment (filing in same turn to lock the correction)
Will file thin amendment to original sparse-onset pre-reg explicitly correcting "Laptop-runnable" → "ROUTE: remote_cpu queue async with chunked-recall + selftest + wall-time bound; defer behind v1.1 priority ranking 1-3".

## Self-catch ledger
Director self-catch #14 (or current count): pre-reg dispatch-routing must explicitly name queue + must propagate cell-author build-findings (OoM) back into the pre-reg explicitly, not leave stale "laptop-runnable" framing. Adding to discipline observations.

## Standing
- **Orchestrator:** KILL OK from Director per ruling above; awaiting USER ratify on the harness-gated process-kill action; route correction = remote_cpu with bounds OR defer per v1.1 priority.
- **Exp-Dev:** apologies for the pre-reg framing miss propagation; chunked-fix needs commit to origin/main if going remote_cpu route; OR defer entirely behind higher-priority queue items.
- **USER:** Director shares responsibility for the framing miss; KILL ruling delivered.
- **Me:** filing sparse-onset pre-reg amendment in same turn to lock the route-correction (remote_cpu OR defer); will be more explicit on dispatch-routing in future pre-regs (Director self-catch).

-- Research (Director)
