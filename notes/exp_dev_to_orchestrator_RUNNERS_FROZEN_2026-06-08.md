# Exp-Dev -> Orchestrator: URGENT -- both runners + healer FROZEN (needs restart; runners are your domain)

**From:** Exp-Dev  **Date:** 2026-06-08  **Priority:** HIGH (both lanes dead)

## Diagnosis (definitive)
Both runner daemons are HUNG (zero CPU movement over a 4s sample; heartbeats over an hour stale). They will not self-recover.
- **gpu_runner_0:** heartbeat 103 min stale, dCPU=0s -> FROZEN
- **cpu_runner_0:** heartbeat 79 min stale, dCPU=0s -> FROZEN
- **healer (auto-restart watchdog):** healer_heartbeat 53 min stale -> ALSO DEAD, so self-healing did NOT fire
- nvidia-smi: GPU utilization 0%, 4.5GB resident (idle model)

## Timeline / root cause
The GPU runner froze ~103 min ago. Symptom that surfaced it: wikipedia_ingest_1m_gpu_v1 showed "running" for 177 min at 0% GPU
-- it was NOT a slow job, the runner had frozen and stopped monitoring it. CPU runner froze ~79 min ago (e3_cyclic_khop_1m "running"
70 min). The freeze PRE-DATES my intervention.

## What I did (with user authorization, before realizing runners were frozen)
- Killed the two wasteful worker tasks ONLY (wikipedia_ingest_1m_gpu, e3_cyclic_khop_1m_cpu) -- matched script name, excluded
  runner_v2_prod; verified runner_daemon_alive=True + workers_remaining=0. (These jobs were genuinely wasteful: wiki was a
  no-incremental-save benchmark at 0% GPU; e3 pathologically slow.)
- Marked their stuck queue entries status=killed via tools/reconcile_killed.py (runner was blocking on metrics.json that a killed
  job never writes). Both queues now have NO running job.
- I did NOT touch the runner daemons or runner_v2_prod supervisor (your domain).

## Current state
- CPU: 0 running, 1 pending (nary_relation_roles_cpu_v1)
- GPU: 0 running, 10 pending (legal_citation_snowball, f1_substrate_kv_m50000, t5a_s2_substrate_kv_m100000, t5b_1/2/3,
  substrate_vs_knnlm_falsifiable, t5b_flamingo_entropy_pretest, substrate_vs_iterative_knnlm, llm_routing_t1_3b)
- demo-mode pause flag: NOT present (cleared)

## Requested action (runners are orchestration's domain)
1. Restart gpu_runner_0 + cpu_runner_0 (they are frozen; pending jobs will not start until they are revived).
2. Restart / investigate the healer -- it failed to auto-restart the frozen runners (root-cause its 53-min staleness so this
   self-heals next time).
3. After restart: confirm fresh heartbeats + that the runners claim the 10 GPU + 1 CPU pending.
4. Optional (my earlier queue-optimization note): 6 of the 10 GPU pending are full-mode re-runs of cells already smoked+reported
   today (kNN-LM, routing, t5b-1/2/3, flamingo) -- safe to drop to save compute; 4 are genuinely new (f1, t5a_s2, iterative-knnlm,
   legal-snowball). See notes/exp_dev_to_research_queue_state_for_optimization_2026-06-08.md.

I will hold all new dispatch until you confirm the runners are back.
