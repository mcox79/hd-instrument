# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 70

## Remote cadence: nothing to add (both queues full + Llama running)
- GPU pending=5, CPU pending=5 -> SKIP new remote ships (per cycle rule). Llama v6 RUNNING (doc ~44k/100k,
  0 failures, ~2.3h to npz). No npz yet -> audit-core-on-real-residuals still pending. No new remote handoffs.

## Productive work this cycle: bio-primitive exploration on LAPTOP CPU (user-directed; requested by bio change-request)
Continued the Stage A bio-primitive sweep + handled Research's consolidated follow-up. All laptop-local, $0.

### Confirmed HARD_PASS (laptop)
- B6 D-ECR audit-eviction (iter2): 0.79 vs LRU 0.39 recall at 2x capacity, 3/3 seeds. FLAGSHIP.
- B2 DG sparse-expansion (fixed recall): >=48x capacity (sparse M_crit 4800 vs dense 100, 3/3 seeds).
- B4 column ensemble: smoke HP (K ensemble matches/beats single large, param-efficient). Full rerun in flight
  (reduced single N 10240->6144; original timed out on laptop).

### Near-HP / characterized
- B3 cf-RPE active gating: 8.3x write reduction at 94% perf (batch1). Ceiling follow-up (full in flight):
  B3a top-5% ~12x@84% (smoke); B3b exp-smoothed-surprise +warmup ~2.6x@112%-perf (gating improves generalization).
- B6c D-ECR CEILING: collapses by M=3x alpha_c (both decr+lru ->0); operational window confirmed ~1.5-2.5x.

### Awaiting Research drills (in flight, ~30min) -- do NOT rebuild yet
- B5 STDP-replay: my replay-decay coupling HURT retention (replay adds decay). Needs offline-replay model +
  the order-vs-random mechanism spec. Research drill `stdp_replay_decay_model_design` in flight.
- B8 residual encoding: r=0.86 with random codebook (projection low-norm). Research drill
  `residual_encoding_representation_question` in flight (PCA/Word2Vec/logit-space bases).

### Pending careful build
- B7 theta-gamma phase binding (scalar-cos degenerate; needs per-position rotation/permutation model).
- B36 composition (B3+B6) -- needs a unified-metric design (gating + eviction under one capacity-pressure task).

## Notes filed
- exp_dev_to_research_bio_smoke_findings_batch1_2_iter2 (my results) -> Research consolidated reply received +
  acted on (B3/B6 ceiling follow-ups built; B5/B8 waiting on drills).

**END.** All laptop scripts use write_metrics. Remote cap_map untouched (no verdict interpretation). Next cycle:
capture full B3/B6-ceiling + B4 results; ingest B5/B8 drill routings when they land; check Llama v6 npz.
