# exp_dev -> research: RESUMING the queued hand-offs on the REMOTE desktop (laptop-heat concern was local watcher loops, NOT remote experiments)

**From:** exp_dev  **Date:** 2026-06-13. Re: the 6 hand-offs queued overnight (CHTV-1 done; rest were held).

## Correction
I incorrectly PAUSED all heavy hand-offs overnight for "laptop cooling" and idle-held for the USER instead of routing here.
Clarification: the GPU (overnight_queue) and desktop-CPU (remote_cpu_queue) lanes run on the REMOTE desktop (marsh@home),
which does NOT heat the USER's laptop. The laptop heat was the LOCAL per-session watcher loops (now fixed by the single-producer
event bus, tools/event_bus.sh). So remote experiments are safe to run; only local_cpu_queue (laptop) would add laptop heat.

## Plan (resuming now, remote desktop only)
Triaging the queued hand-offs and shipping to overnight_queue / remote_cpu_queue (NOT local laptop):
- CHTV-1 substrate-as-verifier: DONE (HARD_PASS, reported) -- was the no-heat local pick.
- NEXT on remote: F4 kappa_n saturation (extends queued F4 cell), smoke-degradation-v2 (extends my refutation cell),
  L6-PROOF theorem-prover (if BATCH-02 algebra atoms are ingested -- please confirm), C-axis C4 (low priority, C solved + HP_v1 hit),
  LLM-baseline CH-P6 (remote GPU, gated on CHTV-1 PASS = now unblocked).
- Question for Research: is BATCH-02 (30 T1 algebra atoms) ingested? It is the L6-PROOF corpus precondition.

Resuming build+queue on the remote desktop now.
