# Wave E (retry) -- 4 cell dispatch handoff

From: exp_dev
To: orchestrator (cc: research, skunkworks)
Date: 2026-06-24
Commit: d38c3d68

## Summary

4 cells authored + committed; all self-tests PASS. ALL remote routing (USER smoke
embargo: self-test PASS is the dispatch gate). Orchestrator dispatches via
queue_add.py with `--skip-smoke`.

Estimated total wall: 100-130 min (3 remote_cpu + 1 GPU; can interleave).

## Pre-dispatch verify-referent results (per Skunkworks N1 discipline)

Each cell's prereg + DESIGN_NOTE documents the inline verify-referent reads.
Notable flags (adapted IN-CELL, not refused):
- concept_kg_storage_retrieval_v1 actual verdict=MIDDLE_BAND (USER cited A3=1.0
  comes from SEMANTIC battery v2 FULL, not concept_kg itself). Flagged in Cells
  A, B-redirect, D preregs.
- substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL actual verdict=
  HARD_PASS (6/6 PASS, A3 heldout_top1=1.000, cv=0.000). Citation EXACT for
  Cell B redirect.
- fair_harness_substrate_as_lm_v1 actual verdict=HARD_PASS, sparse_bipolar
  bpc_best_mean=7.3065 cv=0.0018 (was the rail for original Cell B; Cell B has
  been REDIRECTED per USER course-correction; no longer used).
- lock_in_amplifier_hd_frequency_smoke_v1 actual verdict=HARD_PASS; citation
  for Cell C primitive is sound.
- USER citation of "7.54 SHARED_W" for Cell C NOT directly observed in audited
  referents (closest collapse referent = compose FULL_JOINT=7.8919). Flagged
  in Cell C prereg; sanity-band widened to [7.20, 7.95] and we measure in-cell.
- USER citation of "7.17 cross-layer" matches CFRPE_STDP_HETEROGENEOUS=7.1654
  within +/- 0.05; SAFE.

## Cell A: substrate_multihop_consolidation_memory_v1 (Barrier 1)

- Script: experiments/exp_substrate_multihop_consolidation_memory_v1.py
- Prereg: preregs/2026-06-24_substrate_multihop_consolidation_memory_v1.md
- Routing: remote_cpu_queue
- Timeout: 1800s
- Self-test PASS: naive_top1=0.800 hop2_oracle=0.850 cons_top1=1.000 hyb_top1=0.900
- Queue command:
```
python tools/queue_add.py remote_cpu_queue \
    substrate_multihop_consolidation_memory_v1 \
    experiments/exp_substrate_multihop_consolidation_memory_v1.py \
    --prereg preregs/2026-06-24_substrate_multihop_consolidation_memory_v1.md \
    --timeout 1800 \
    --skip-smoke \
    --purpose "Barrier 1: substrate-native compound-atom consolidation; Squire-Wixted analogy"
```

## Cell B (REDIRECTED per USER): substrate_role_tagged_compositional_generalization_on_concept_KG_v1

- Original Cell B (substrate_LM_role_tagged_plate_context_v1 on text8) DELETED.
  Reason: text8 has no labels/grammatical structure -> role-tagging primitive
  on unlabeled corpus is strategically misaligned. USER ack required for any
  later substrate-as-LM lane (would need PTB-WSJ POS-tagged or SRL corpora).
- Script: experiments/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.py
- Prereg: preregs/2026-06-24_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.md
- Routing: remote_cpu_queue (substrate-native concept-KG; CPU feasible at N=8192 / V=32)
- Timeout: 3600s
- Self-test PASS: role_codebook clustering within_A=0.843 within_B=0.845 cross=0.000
  (clean orthogonal-vs-clustered discriminator)
- Queue command:
```
python tools/queue_add.py remote_cpu_queue \
    substrate_role_tagged_compositional_generalization_on_concept_KG_v1 \
    experiments/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.py \
    --prereg preregs/2026-06-24_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.md \
    --timeout 3600 \
    --skip-smoke \
    --purpose "Barrier 2 redirect: compositional generalization to heldout (subject, role); extends SEMANTIC v2 A3=1.0"
```

## Cell C: substrate_compose_lock_in_frequency_stacking_v1 (Barrier 3 alt)

- Script: experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py
- Prereg: preregs/2026-06-24_substrate_compose_lock_in_frequency_stacking_v1.md
- Routing: GPU overnight_queue (torch.cuda batched matmul per Fix #24; 4 W
  matrices x ingest_chunk over text8 100k tokens)
- Timeout: 7200s
- Self-test PASS: shared!=lockin (diff=3.053e+03) Ws=3 logits_ok bpc_uniform_ok
- Queue command:
```
python tools/queue_add.py overnight_queue \
    substrate_compose_lock_in_frequency_stacking_v1 \
    experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py \
    --prereg preregs/2026-06-24_substrate_compose_lock_in_frequency_stacking_v1.md \
    --timeout 7200 \
    --skip-smoke \
    --purpose "Barrier 3 alt: temporal frequency-division separation across plasticity rules"
```

## Cell D: substrate_label_driven_anisotropic_encoder_v1 (Barrier 4 alt)

- Script: experiments/exp_substrate_label_driven_anisotropic_encoder_v1.py
- Prereg: preregs/2026-06-24_substrate_label_driven_anisotropic_encoder_v1.md
- Routing: remote_cpu_queue (pure-numpy; small V_C=12)
- Timeout: 3600s
- Self-test PASS: encoders=4 a1=0.560 a3_top5_in_cat=0.583
- Queue command:
```
python tools/queue_add.py remote_cpu_queue \
    substrate_label_driven_anisotropic_encoder_v1 \
    experiments/exp_substrate_label_driven_anisotropic_encoder_v1.py \
    --prereg preregs/2026-06-24_substrate_label_driven_anisotropic_encoder_v1.md \
    --timeout 3600 \
    --skip-smoke \
    --purpose "Barrier 4 alt: construct encoder anisotropy from concept-KG labels (not learn unsupervised)"
```

## Push to origin/main (REQUIRED before GPU/remote_cpu_queue dispatch)

Cells routing to remote_cpu_queue (A, B-redirect, D) and overnight_queue (C)
require origin/main to contain commit d38c3d68. Push is harness-DENIED to
exp_dev; orchestrator routes via hd_metrics_sync. Dispatch commands above
will GATE_FAIL with "prereg-not-found" until push lands.

## Wave E summary

- 4 cells authored (1 redirected per USER course-correction)
- All self-tests PASS (mechanism + sanity rails)
- All preregs document both directions of NEGATIVITY-BIAS check
- Per-arm Fix #28 metrics in all 4 verdict functions
- Per-seed checkpoint via _seed_checkpoint helper (PROT-021 N/run_mode guard)
- atexit synthesizer per cell (catches crash partials before metrics.json)
- ASCII only
- No _n<N> anchor suffix (PROT-019 timeout floor not triggered)

Ready for orchestrator dispatch.
