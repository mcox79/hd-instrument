# Wave F handoff -- 4 cells FIXED + ready for dispatch
Date: 2026-06-25
From: exp_dev
To: hdi_orchestrator
Type: dispatch handoff (REMOTE routing -- USER smoke embargo active)

## Summary
Four cells that HARD_FAILed in Wave E dispatch are now bug-fixed, self-test
PASS, and ready for re-dispatch. All 4 routes are REMOTE (smoke embargo).
Total wall budget for fixes: ~25 min (within 30-45 min ceiling).

## Cells (4)

### Cell 1: substrate_hub_spoke_E1_v3_MRC_calibrated_routing
- Bug: device-mismatch in `hub_aggregate_mrc` -- gate_logits passed CPU,
  spoke_outputs on cuda; `(stacked * w).sum(dim=0)` failed.
- Fix: defensive `.to(target_device)` of gate_logits inside `hub_aggregate_mrc`
  AND `hub_aggregate_cfrpe_weighted` (same root-cause class). Also explicit
  `device=DEVICE` on T12/T14 self-test tensors (`gl_test`, `gates_uni`,
  `gates_peak`) so the test path exercises real device behavior.
- File: experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py
- Self-test PASS evidence:
    `[T8] diverse-algo spoke diversity_cv = 1.0886 (v1 was 0.0008)`
    `[selftest v3] PASS: T1..T16 (incl T12 FIX2 MRC bundle, T14 gate_entropy, T16 llm=0)`
- Route: overnight_queue (GPU), 7200s
- Anchor: substrate_hub_spoke_E1_v3_MRC_calibrated_routing
- Prereg: preregs/2026-06-25_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.md

### Cell 2: substrate_compose_heterogeneous_routing_v3_full_config_rerun
- Bug: stale v2_RESCUE assertion in ST16 (`N_DIM == 4096`, `N_TRAIN == 50_000`,
  `len(SEEDS) == 2`) -- v3 sets N_DIM=8192, N_TRAIN=100k, 3 seeds, so the
  full-mode self-test hit a hard assertion at startup.
- Fix: updated ST16 to assert v3 contract (N_DIM=8192, N_TRAIN=100k, 3 seeds).
  Kept the "N_DIM even (orthog split safe)" invariant since orthogonal
  subspace split mechanism is unchanged.
- File: experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py
- Self-test PASS evidence (smoke mode skips the full-mode ST16 path):
    `[selftest] ST16 config-coherence sanity OK (N_DIM=1024 N_TRAIN=2000 seeds=1)`
    `[selftest] ALL PASS`
  Full-mode ST16 will validate N_DIM=8192/N_TRAIN=100k/3-seeds at dispatch.
- Route: overnight_queue (GPU), 7200s
- Anchor: substrate_compose_heterogeneous_routing_v3_full_config_rerun
- Prereg: preregs/2026-06-25_substrate_compose_heterogeneous_routing_v3_full_config_rerun.md

### Cell 5: substrate_role_tagged_compositional_generalization_on_concept_KG_v1
- Bug: `ingest_no_roles` function-signature parameter name was `R_action` but
  function body referenced `E_action[a]` -- NameError at runtime. The CALLER
  passes `E_action` positionally (line ~392), so the body is correct; the
  parameter name was wrong.
- Fix: renamed parameter `R_action` -> `E_action` to match body usage and
  caller intent. (Other arms `ingest_role_orthogonal` and `ingest_grammatical`
  already use `E_action` in their signatures consistently.)
- File: experiments/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.py
- Self-test PASS evidence:
    `[selftest] PASS role_codebook_ok clustering={A=0.843 B=0.845 X=0.000} encoder_ok ingest_ok query_ok`
- Route: remote_cpu_queue, 3600s
- Anchor: substrate_role_tagged_compositional_generalization_on_concept_KG_v1
- Prereg: preregs/2026-06-24_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.md

### Cell 6: substrate_compose_lock_in_frequency_stacking_v1
- Bug: CUDA OOM on 8GiB GPU at full config. Tried to allocate 3.05GiB on top
  of 4.22GiB already pinned. Root cause: ARM_LOCK_IN_PLUS_CROSS_LAYER holds
  3 separate W matrices simultaneously (3 * 8192^2 * 4 bytes = 768MB) plus
  encoder state plus per-batch matmul intermediates. At v1 full config
  exceeds 8GiB ceiling.
- Fix: ROUTE TO CPU (no code change). DEVICE auto-falls-back to cpu when
  cuda unavailable; on remote_cpu_queue runner the cell runs CPU correctly.
  Float32 already enforced (TORCH_DTYPE). 64GB RAM gives 8x headroom over
  the worst-case 4-5GiB working set. Prereg updated with reroute justification.
- File: experiments/exp_substrate_compose_lock_in_frequency_stacking_v1.py
  (NO code change to this file; only prereg metadata updated)
- Self-test PASS evidence:
    `[selftest] PASS shared!=lockin (diff=3.053e+03) Ws=3 logits_ok bpc_uniform_ok`
- Route: remote_cpu_queue, 10800s (was 7200s GPU; CPU ~3-5x slower; 1.5x safety)
- Anchor: substrate_compose_lock_in_frequency_stacking_v1
- Prereg: preregs/2026-06-24_substrate_compose_lock_in_frequency_stacking_v1.md
  (Wave F reroute justification appended)

## Routing summary

| Cell | Queue          | Timeout |
|------|----------------|---------|
| 1    | overnight_queue| 7200s   |
| 2    | overnight_queue| 7200s   |
| 5    | remote_cpu_queue | 3600s |
| 6    | remote_cpu_queue | 10800s |

GPU lane: 2 cells (7200s each = 4h sequential or parallel if free)
CPU lane: 2 cells (3600 + 10800 = 14400s sequential)

## Disciplines preserved (USER smoke embargo)
- Self-test PASS gate used (no smoke runs).
- Verify-the-referent on cited Store cells preserved per each prereg.
- D1 roofline + D2 atexit + per-seed checkpoint preserved (cells 1, 2 have
  the prereg-spec D1 probe).
- ASCII-only.
- Path-scoped commits (one per cell + this handoff).

## Commits (path-scoped)
Cells were committed individually per path; see git log on origin/main after
push. Final commit hashes will be appended once `hd_metrics_sync` push lane
completes (laptop is harness-DENIED for push; relies on sync task).

## Action for hdi_orchestrator
Dispatch the 4 cells via `tools/queue_add.py` in a follow-up turn. The
Anchor/Queue/Timeout triples above are the dispatch spec. All 4 cells pass
`--self-test` on .venv locally; remote runner picks up after origin/main push.

Wave G cells (E/F/G from director_gap_cell_specs_E_F_G_2026-06-25.md) are
SPEC-ONLY -- do NOT dispatch in this turn (USER has not authorized).
