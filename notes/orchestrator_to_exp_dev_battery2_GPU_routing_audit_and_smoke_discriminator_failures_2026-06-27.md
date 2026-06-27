# exp_dev hand-off -- battery 2 GPU routing audit + smoke-discriminator failures

**Filed-by:** Orchestrator (Opus 4.7-1M)
**Date:** 2026-06-27 ~14:55 PDT
**Trigger:** USER 2026-06-27 ~14:55 PDT: "send things to gpu that deserve to go to gpu."
**Pause flag:** absent (verified)
**Coordination:** This handoff is for the hdi_exp_dev agent (a8a419a3) that authored the v1 cells. NOT a re-routing; a request for follow-up authoring.

---

## CURRENT STATE (audit)

**Queues (authoritative; SSH-pulled):**
- `overnight_queue` (GPU): 0 pending, 0 running. GPU runner (PID 17308) ALIVE + IDLE. (The 1 stale "running" + 1 "pending" entry visible in the local laptop snapshot are residual; remote queue is empty.)
- `remote_cpu_queue`: 0 pending, 0 running. CPU runner (PID 13164) ALIVE + IDLE.
- `local_cpu_queue`: 0 pending, 0 running.

**Existing v1 cells (smoke-VET this turn by orchestrator):**
1. `multi_readout_fisher_importance_v1` -- self-test PASS; smoke HARD_FAIL `Fisher=+0.039 Single=-0.049 Two=-0.108 lift=+0.089 cv=1.230 cor=0.085 n=2`. **MATCHES the research drill `research_drill_2x_multi_readout_fisher_revival_2026-06-27.md`** -- this v1 cell is NOT for full dispatch per drill recommendation. Drill TOP-1 revival = `lock_in_amp_pca_readout_fisher_v1` (composes B2 lock-in + A2 Gram-Schmidt-orthogonal bases + A3 held-out Fisher variance estimation).
2. `sub_atom_token_stream_encoder_v1` -- self-test PASS; smoke MIDDLE_BAND with **1.000 SATURATION on ALL discriminator metrics including baseline** (`RF_d3=1.000 Trig_d3=1.000 alpha_cos=1.000 codebook_disambig=1.000 cv=0.000`). Per Discipline #2 (`feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive`): **smoke MUST FIRE the discriminator**; here baseline saturates equally with mechanism arms = discriminator not firing. Per META_RULE bias-Q: "suspect 1.000 results." Cannot dispatch full at this smoke regime; need harder smoke that escapes by-construction saturation BEFORE full ship per `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`.

---

## GPU vs CPU routing analysis (Fix #24 audit)

USER's directive is to route GPU-deserving work to GPU. The 7 cells called out as "GPU-eligible" by research are:

| Cell | Authored? | torch.cuda? | Fix #24 verdict | Routing |
|---|---|---|---|---|
| `multi_readout_fisher_importance_v1` | YES (v1 numpy) | NO | Numpy-on-GPU = 1% util waste | **DO NOT route to GPU as-is.** Author `lock_in_amp_pca_readout_fisher_v1` revival per drill (torch.cuda fp16 matmul; k=8 PCA readouts x M=4096 x 8 seeds = matrix-heavy). |
| `sub_atom_token_stream_encoder_v1` | YES (v1 numpy) | NO | Numpy-on-GPU = waste | **DO NOT route to GPU as-is.** Revise smoke regime to escape saturation FIRST (harden smoke discriminator); THEN consider GPU variant if codebook x corpus matmul justifies (drill says ~1 GPU-day full for 3 corpora x 2k codebook). |
| `lean_mathlib_ingest_v1` | NO | n/a | DEPENDS on sub_atom encoder | Blocked until encoder lands HARD_PASS. |
| `materials_project_ingest_v1` | NO | n/a | DEPENDS on sub_atom encoder | Blocked until encoder lands HARD_PASS. |
| `oeis_ingest_v1` | NO | n/a | DEPENDS on sub_atom encoder | Blocked until encoder lands HARD_PASS. |
| `tensor_network_contraction_ordering_v1` | NO | n/a | TBD on authoring | Author with torch.cuda batched-tensor-contraction over 5 topologies x depth-4; **PRIORITY for GPU** -- matrix contraction sequences ARE the workload GPUs were built for. |
| `cortex_schema_integration_from_ultrametric_v1` | NO | n/a | DEPENDS on cortex 2x drill TOP picks | Schema-bind ops on large W; GPU plausible if N_DIM=8192 + M=50 clusters x 30 members; could go either queue. Defer routing decision to author. |

---

## ASKS (in priority order)

### A. **STOP** any work to "send" the v1 numpy cells to GPU.

Numpy-on-GPU = Fix #24 anti-pattern. Confirmed by the 2-call orchestrator audit:
- both v1 cells have `import numpy as np`; no `import torch`.
- both have `RUN_MODE`-gated scaling; FULL mode is N_DIM=8192, M=500/4096.
- ARM math is `np.einsum`/`@`/`np.linalg.svd` family. Would execute on GPU host's CPU via the runner_v2_prod harness; gpu_util will sit at 1%.

### B. **AUTHOR `lock_in_amp_pca_readout_fisher_v1`** (drill TOP-1 revival; supersedes multi_readout v1)

Per `research_drill_2x_multi_readout_fisher_revival_2026-06-27.md` Section TOP-1:
- ARMS: ARM_SINGLE_DC / ARM_K4_PCA_DC / ARM_K4_PCA_LOCKIN_F4 / ARM_K8_PCA_LOCKIN_F4 / ARM_K8_PCA_LOCKIN_FISHER_HELDOUT
- HARD_PASS: K8 LOCKIN FISHER HELDOUT mean sel_unretr >= +0.15 cv <= 0.25 across n=8 seeds at N=8192 M=4096; cor(imp, |W|) < 0.30 (Fix BIAS-Q fairness)
- Honest bound: if K8 LOCKIN FISHER within +/-0.02 of K4 PCA DC, ceiling confirmed
- **GPU mandate (Fix #24):** torch.cuda + fp16 readout matmul + gpu_util_p50 >= 50% in smoke (nvidia-smi sampling per arm). Hoist readout construction outside seed loop.
- Cost: ~3 GPU-hr per drill; route via orchestrator to `overnight_queue`.
- Smoke discipline: smoke must FIRE the K8 LOCKIN FISHER vs K4 PCA DC discriminator at smoke N (use N=4096 M=1024 2 seeds smoke; require K8 LOCKIN FISHER > K4 PCA DC by >= +0.03 in smoke or HARD_FAIL the smoke and revise the regime BEFORE full).

### C. **REVISE `sub_atom_token_stream_encoder_v1` smoke discriminator**

Current smoke regime saturates everything at 1.000. Per Discipline #2 + USER 2026-06-26 (`feedback_discriminator_must_survive_scale_before_full_dispatch`), one of:
- Option A: smoke at full N_DIM (N=8192 codebook=2000) for 1 seed to verify CHAR_TRIGRAM_BASELINE lands in [0.10, 0.30] (drill expectation) NOT 1.000. The current smoke at N=2048/codebook=200 collapses both arms.
- Option B: analytical justification of scale (show via NESS or capacity-bound math why TRIGRAM baseline must drop at full N).
- Option C: include a full-N preview arm in smoke (1 config x 100 test theorems at N=8192 codebook=2000) within smoke wall budget; reject full dispatch if baseline saturates >= 0.90 of mechanism.

Then GPU authoring: codebook x corpus matmul (200 corpora atoms x 2000 codebook x N_DIM=8192) IS legitimately GPU-grade. Once smoke discriminator fires, author torch.cuda variant; route to overnight_queue.

### D. **AUTHOR `tensor_network_contraction_ordering_v1`** GPU-aware

Per `preregs/2026-06-27_tensor_network_contraction_ordering_v1.md`:
- ARMS: ARM_LTR_BASELINE / ARM_MIN_DEGREE / ARM_OPTIMAL_BRUTE_FORCE / ARM_DIAG_INTERMEDIATE_DIM / ARM_DIAG_NOISE_COMPOUNDING
- 5 topologies x 5 seeds x 3 mandatory arms = 75 units; cardinality_ok HARD lock
- HARD_PASS: MIN_DEGREE depth-4 hetero >= LTR + 0.10; cv < 0.10; within +/-0.03 of OPTIMAL_BRUTE_FORCE
- **GPU mandate:** torch.cuda tensor contractions are NATIVE GPU workload (this is what tensor cores were designed for); fp16 contractions; batched across topologies; nvidia-smi p50 >= 50%
- Smoke discriminator at full N_DIM=8192 over depth-3 chain+star 2 seeds; HARD_FAIL if MIN_DEGREE < LTR + 0.05
- Route to `overnight_queue` once smoke fires discriminator

### E. **DEFER** the 3 ingest cells (`lean_mathlib`, `materials_project`, `oeis`) until sub_atom encoder is chain-grade

These DEPEND_ON sub_atom_token_stream_encoder_v1 HARD_PASS per their preregs. Until encoder revised smoke + full HARD_PASS lands, ingest authoring is premature work.

### F. **`cortex_schema_integration_from_ultrametric_v1`** -- defer routing decision to author

Per its prereg DEPENDS_ON `cortex_ultrametric_clustering_coarse_grain_v1` HARD_PASS (CERT 623 chain-grade per the prereg) AND `kb_partition_by_source_class_v4_calibrated` HARD_PASS. If those land, cell-author can decide GPU-vs-CPU based on N_DIM=8192 x 50 clusters x 10-50 members per cluster. If GPU-authored (torch.cuda HD ops), route to overnight_queue; if numpy, route to remote_cpu_queue. Either is defensible.

---

## What orchestrator did this turn (the audit-trail facts)

1. Verified gpu_runner_0 (PID 17308) + cpu_runner_0 (PID 13164) alive on remote.
2. Pulled authoritative remote queue state -- both empty (GPU idle, remote CPU idle).
3. Verified `multi_readout_fisher_importance_v1` --self-test PASS.
4. Ran ACTUAL --smoke for `multi_readout_fisher_importance_v1` -- HARD_FAIL Fisher=+0.039 cv=1.230 -- matches drill.
5. Verified `sub_atom_token_stream_encoder_v1` --self-test PASS.
6. Ran ACTUAL --smoke for `sub_atom_token_stream_encoder_v1` -- MIDDLE_BAND with 1.000 saturation; discriminator did not fire at smoke regime.
7. Did NOT dispatch either cell to FULL. The drill TOP-1 revival path supersedes v1 multi_readout; sub_atom encoder needs smoke-regime revision.
8. Did NOT route any numpy cell to GPU (Fix #24 mandate).
9. Filed this coordination handoff.

---

## Standing / waiting-on

Orchestrator waiting on: hdi_exp_dev to (1) author `lock_in_amp_pca_readout_fisher_v1` GPU-aware per Section B, (2) revise sub_atom smoke per Section C, (3) author `tensor_network_contraction_ordering_v1` GPU-aware per Section D. On commit + dispatch-request file, orchestrator ships via queue_add.sh.

Orchestrator can also accept dispatch-requests for the CPU-eligible Battery 2 cells (BTSP / STC / engram-dropout / cyclic-eta / memristive / 3-tier W / PFC schema replay / orthogonal role basis / LBP damped / multi-channel importance / lock-in amplifier importance / sparse-comp K-WTA / 5 Barrier 3 cells / parietal cortex spatial reasoning) for remote_cpu_queue routing while GPU authoring happens in parallel.

---

-- Orchestrator (Opus 4.7-1M)
