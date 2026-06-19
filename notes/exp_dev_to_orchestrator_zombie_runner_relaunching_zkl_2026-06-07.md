# Exp-Dev -> Orchestrator: ZOMBIE RUNNER relaunching zkl_methodology in a ~1s loop -- needs runner cleanup

**From:** Exp-Dev  **Date:** 2026-06-07  **URGENT (GPU waste, not blocking)**

## What happened
zkl_methodology_variance_v1 ran 4.5 HOURS on GPU (my design error: 20 MarianMT+Llama harness runs; ~13.5 min/run). With
user authorization I killed the experiment child (PID 97640, child of runner PID 205260 -- runner NOT touched). The GPU lane
correctly advanced: **pubmedbert_swap is now RUNNING**, iterative_multihop + stella pending. Good.

## The problem (yours -- I cannot kill runners)
A runner keeps **RELAUNCHING exp_zkl_methodology_variance_v1.py every ~1 second** (new PID each check: 97640->115148->230420
->84252->155020->...). I have:
- Set its overnight_queue.json status to **cancelled** (was 'failed') -- UTF-8 no BOM. Runner ignores it.
- taskkill /F /T'd the child tree repeatedly -- respawns in ~1s every time.
So a runner process has zkl as an in-memory job and relaunches on each tick regardless of queue status. **There are 6
processes matching runner_v2_prod** (abnormal -- expect 1-2). One is likely a zombie/duplicate looping on zkl.

## Impact
Not blocking (pubmedbert is progressing), but each respawn reloads MarianMT+Llama on the GPU then dies -- **wasting GPU
cycles + contending** with the real pivotal cells. Should be stopped.

## Request (runner management = your lane; I will not kill runners)
1. Identify + kill the zombie runner looping on zkl (the one whose current job is zkl_methodology_variance), restart a clean
   runner pool (you have the 6-process list; normal is 1 CPU + 1 GPU).
2. After cleanup, a LIGHT zkl (3 seeds, no temp sweep, ~40 min) is ready in repo if you want variance characterization --
   I'll re-queue it once the runner pool is clean (queuing now would just feed the loop).

I stopped the whack-a-mole kills (futile against the loop). Cancelled the queue entry. Pivotal verdicts (pubmedbert/
iterative/stella) are running. Over to you for the runner cleanup.

---
## UPDATE (hours later): STILL respawning + now confirmed POISONING the GPU lane
zkl is STILL relaunching (2 procs, fresh PIDs, ~hours after first report). It's holding ~1.5GB GPU + reloading MarianMT/Llama
every ~1s. **stella400m_encoder_headtohead is now status=failed/dropped** -- almost certainly because the respawning zkl
starved/contended the GPU. The GPU lane is effectively UNUSABLE for new cells until the zombie runner is killed. This is
blocking real GPU work (encoder ceiling resolution). URGENT: please kill the zombie runner + restart a clean pool. I cannot
(runner rule). CPU lane is unaffected (I'm keeping it fed). Once GPU is clean I'll re-queue stella + the light 3-seed zkl.

---
## RETRACTION (important): there was NO zombie runner -- it was a MONITORING-QUERY ARTIFACT
On careful re-check: `Get-CimInstance Win32_Process | Where-Object CommandLine -like '*exp_zkl_methodology*'` matches the
cmd.exe/powershell.exe process RUNNING THAT QUERY (the filter string is in its own command line). So "zkl=2 with fresh PIDs
each check" = my successive monitoring commands matching themselves, NOT a zombie relaunching zkl. Filtering to Name='python.exe'
shows ZERO real zkl processes. GPU memory = 1778 MiB (idle baseline). zkl was killed cleanly hours ago; the GPU has been FREE
the entire time. Apologies for the two false escalations -- no runner action needed. (stella's failure was a real crash, not
contention -- handling separately.) Lesson logged: never match process by CommandLine substring that appears in the query itself.
