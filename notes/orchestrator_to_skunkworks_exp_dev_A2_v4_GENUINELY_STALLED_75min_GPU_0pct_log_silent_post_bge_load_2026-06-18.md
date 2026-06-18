# Orchestrator -> Skunkworks + Exp-Dev: A2 v4 GENUINELY STALLED (Exp-Dev's flag confirmed). Runner-log-first diagnosis:

Runner heartbeat: status=running, current=a2_decisive_test_untuned_auroc_v4
GPU utilization: 0% (nvidia-smi)
GPU memory: 2805 MiB (residual)
Runner log mtime: 2026-06-18 16:15:26 UTC (~75 min ago)
Runner log content (verbatim, last 6 lines):
  Warning: You are sending unauthenticated requests to the HF Hub...
  Loading weights:   0%|          | 0/391 [00:00<?, ?it/s]
  Loading weights: 100%|...| 391/391 [00:00<00:00, 7786.66it/s]
  C:\dev\hd-instrument\backend\llm\bge_encoder.py:65: FutureWarning: get_sentence_embedding_dimension renamed
    self.hidden_size = self.model.get_sentence_embedding_dimension()

The cell hung POST-bge-load. After "FutureWarning + get_sentence_embedding_dimension", NOTHING. GPU went idle but the runner still claims it's the current job.

Possible causes:
- HF Hub request hung (unauthenticated -> rate-limit wait?)
- rebuild_index_cached over 41k atoms hung silently
- Some other indeterminate wait

Composes with Skunkworks's verify-running-not-just-dispatched lesson: "running" status is necessary, not sufficient -- GPU utilization + log freshness are the secondary check. My broadcast bd1b38fa confirmed RUNNING at 16:15:22 (just after bge load). I should have re-checked after ~10 min to verify the cell wasn't stuck post-load.

Actions need auth:
- Kill the hung process on remote (destructive remote-side; need explicit authorization)
- Re-dispatch v5 with HF_TOKEN env OR fix the rebuild_index hang root-cause

NOT killing without authorization. Standing for Skunkworks/USER ratify on next step.

-- Orchestrator (Custodian)
