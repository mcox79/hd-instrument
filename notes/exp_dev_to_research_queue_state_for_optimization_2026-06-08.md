# Exp-Dev -> Research/Orchestrator: queue + running state (for scheduling optimization)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** requested queue snapshot for optimization

## Current state (demo-mode pause ACTIVE; runner draining existing queue, no new auto-dispatch)
### CPU (remote_cpu_queue)
- RUNNING: e3_cyclic_khop_1m_cpu_v1
- PENDING (1): nary_relation_roles_cpu_v1
- Note: lane near-idle; cron refills. soft_weighted_and_cpu_v1 (N=16384) bounced off the PROT-019 timeout-floor gate and is NOT
  queued (needs --timeout>=21600); pp155_hp_rescue_n32768 + verify_span_factcheck staged locally, not yet queued (pause).

### GPU (overnight_queue)
- RUNNING: wikipedia_ingest_1m_gpu_v1  <-- ~2 HR JOB, HEAD-OF-LINE
- PENDING (10, FIFO order): legal_citation_snowball, f1_substrate_kv_m50000, t5a_s2_substrate_kv_m100000,
  t5b_1_attention_substitution_scaffold, t5b_2_attention_perplexity, t5b_3_attention_fact_use,
  substrate_vs_knnlm_falsifiable, t5b_flamingo_entropy_pretest, substrate_vs_iterative_knnlm, llm_routing_t1_3b

## Optimization analysis
1. **GPU head-of-line block:** the 1M-Wikipedia ingest (~2hr) is running and blocks all 10 pending. The single-job GPU runner is
   FIFO, so nothing behind it starts for ~2hr.
2. **~6 of the 10 pending are FULL-MODE RE-RUNS of cells already SMOKED + reported** (results known, filed to Research today):
   - substrate_vs_knnlm_falsifiable (HARD_PASS +0.983 multi-hop), llm_routing_t1_3b (HARD_PASS 0.833),
     t5b_1 (scaffold PASS), t5b_2 (perplexity PASS), t5b_3 (additive FAIL -- known negative), t5b_flamingo_entropy_pretest (PASS, adapter req).
   These are confirmation runs; their verdicts are NOT blocking any decision.
3. **~4 are genuinely NEW results worth prioritizing:** f1_substrate_kv_m50000 (capacity ceiling), t5a_s2_substrate_kv_m100000
   (production scale), substrate_vs_iterative_knnlm (moat hardening vs multi-step RAG), legal_citation_snowball (sharded full run).
   All are FAST (~1-5 min each) except none are long.

## Recommendations
- **Option A (minimal):** let the 1M ingest finish (it is the demo data layer Testbed needs); the 10 pending then clear in ~15-20
  min total (all fast except they're all fast). No action needed if the ingest is wanted now.
- **Option B (if new results urgent):** deprioritize/requeue the 1M ingest to LAST so the 4 new + 6 confirmation jobs (~15 min total)
  finish first, then the 2hr ingest runs unattended. Recommended if f1/t5a_s2/iterative-knnlm numbers are needed for demo decisions.
- **Queue hygiene:** drop the 6 known-result re-runs from the GPU queue to save ~compute (smoke verdicts already filed); requeue
  soft_weighted_and with timeout>=21600.
- **CPU:** healthy but near-idle; safe to lift pause for the cheap CPU product-gates (pp155 N=32768 rescue, verify_span_factcheck)
  when ready -- both ~1-2hr, critical-path for probabilistic + verification product claims.

Exp-Dev recommends Option B + dropping the 6 confirmation re-runs, if the f1/t5a_s2/iterative-knnlm numbers are wanted soon.
