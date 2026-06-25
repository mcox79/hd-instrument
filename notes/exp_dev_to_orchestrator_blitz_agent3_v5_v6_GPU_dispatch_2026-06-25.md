# exp_dev -> orchestrator: v5 DEFINITIVE + v6 SEGREGATED ready for GPU dispatch

**From:** exp_dev (coordinated blitz Agent 3 of 3)
**To:** orchestrator (handles GPU push lane)
**Date:** 2026-06-25
**Status:** Cells + preregs filed + self-tests PASS + commit landed; ready for `overnight_queue` dispatch.

---

## Two cells to dispatch (both GPU `overnight_queue`)

### Cell 1: substrate_compose_freq_routing_v5_DEFINITIVE
- **Anchor:** `substrate_compose_freq_routing_v5_DEFINITIVE`
- **Cell:** `experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py`
- **Prereg:** `preregs/2026-06-25_substrate_compose_freq_routing_v5_DEFINITIVE.md`
- **Queue:** `overnight_queue` (GPU)
- **Timeout:** **7200s**
- **Self-test:** PASS (16 STs; ST16 budget headroom 12.95x)
- **Goal:** Convert v4 ARM_FREQ_DEEPER_TRAIN CHAIN_GRADE_PARTIAL (7.159, n=3) to DEFINITIVE via 5 seeds + cross-N (4096 + 8192) + n_steps upper-bound (2000 vs 3000)
- **5 arms:** ARM_BASELINE_N8192, ARM_FREQ_DEEPER_N8192, ARM_BASELINE_N4096, ARM_FREQ_DEEPER_N4096, ARM_FREQ_DEEPER_NSTEPS_3000
- **5 seeds:** [7, 13, 17, 23, 29]
- **Bands (PROSPECTIVE):** HARD_PASS_CHAIN_GRADE_DEFINITIVE if cross-N both pass + cv<=0.03; HARD_PASS_SINGLE_CONFIG if just N8192 replicates v4; HARD_FAIL_NULL if N8192 >= 7.30

### Cell 2: substrate_compose_segregated_dual_W_context_gated_v1
- **Anchor:** `substrate_compose_segregated_dual_W_context_gated_v1`
- **Cell:** `experiments/exp_substrate_compose_segregated_dual_W_context_gated_v1.py`
- **Prereg:** `preregs/2026-06-25_substrate_compose_segregated_dual_W_context_gated_v1.md`
- **Queue:** `overnight_queue` (GPU)
- **Timeout:** **7200s**
- **Self-test:** PASS (19 STs; ST17 cost-model in band; ST18 budget headroom 6.42x)
- **Goal:** Per drill recommendation -- v4 COMBINE_W_THETA HURT (7.365) due to cf-RPE+STDP FDM intermod on shared W. v6 segregates by FUNCTION: W_when (STDP-only) + W_what (cf-RPE-only) + context-magnitude gate. Tests whether brain-canonical theta=WHEN/gamma=WHAT separation avoids intermod.
- **5 arms:** ARM_BASELINE_SHARED_W, ARM_FREQ_DEEPER, ARM_THETA_PHASE_TWO_W, ARM_SEGREGATED_DUAL_W, ARM_SEGREGATED_PLUS_CONTEXT_GATE
- **5 seeds:** [7, 13, 17, 23, 29]
- **Bands (PROSPECTIVE):** HARD_PASS_CHAIN_GRADE if SEGREGATED+GATE beats both FREQ_DEEPER (7.159) AND THETA (7.235); HARD_FAIL_INTERMOD_NOT_AVOIDED if SEGREGATED arms cluster near 7.365

---

## Commit hash

`70bef627` -- 4 files added, 4110 insertions, all path-scoped.

Files staged:
- experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py
- experiments/exp_substrate_compose_segregated_dual_W_context_gated_v1.py
- preregs/2026-06-25_substrate_compose_freq_routing_v5_DEFINITIVE.md
- preregs/2026-06-25_substrate_compose_segregated_dual_W_context_gated_v1.md

---

## Action items for orchestrator

1. **Push origin/main** (via hd_metrics_sync; harness-DENIED to me)
2. **queue_add overnight_queue** for both cells with `--timeout 7200`:
   ```bash
   bash tools/orchestrator/queue_add.sh overnight_queue \
       experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py \
       --timeout 7200 --skip-smoke
   bash tools/orchestrator/queue_add.sh overnight_queue \
       experiments/exp_substrate_compose_segregated_dual_W_context_gated_v1.py \
       --timeout 7200 --skip-smoke
   ```
   (Use `--skip-smoke` per USER embargo this arc.)
3. **REMOTE VERIFY post-dispatch**: confirm both `data/<anchor>/metrics.json` paths populate post-completion and that cell-spec arrived intact on `marsh@home`.

---

## Disciplines verified

- [x] D1 roofline probe wired in both cells (probes 3 N scales pre-FULL, extrapolates wall, gates dispatch if extrapolated > 0.8 * timeout)
- [x] D2 atexit + per-seed checkpoint via `experiments/_seed_checkpoint.py` in both cells
- [x] Self-test PASS gate: v5 16 STs, v6 19 STs; all PASS local CPU at venv python 3.11
- [x] Per Fix #24 GPU: torch.cuda + batched ops in all kernels
- [x] Per Fix #28: per-arm BPC + cv in `detail.by_arm_agg.<arm>` + `detail.arm_bpc.<arm>`; verdict_msg cites per-arm numerics
- [x] PROSPECTIVE bands per Skunkworks META_RULE_retrospective_band_correction (both cells are genuine new architectures + measurement upgrades; not retroactive band adjustment)
- [x] ASCII only
- [x] Pre-reg committed BEFORE dispatch (now in repo)
- [x] Path-scoped commits

---

## Routing rationale (per fleet doctrine)

Both cells are matmul-heavy at N=8192 (v5 has FREQ@N=8192/n_steps=3000 = 255s/seed; v6 has 4-arm chain @n_steps=2000 = ~1100s/seed). GPU mandatory.

Per recent USER directive (Fix #24 / `feedback_gpu_underutilization_route_heavy_cells_via_orchestrator_USER_2026-06-22.md`): heavy cells route via `overnight_queue` (GPU). Per `feedback_cell_author_smoke_and_dispatch_route_via_orchestrator_for_heavy_cells_USER_2026-06-22.md`: smoke + Fix #17 measurement on remote (not laptop). USER --smoke embargo this arc means we ship straight to overnight_queue.

Per `reference_hd_dispatch_queue_architecture_cpu_local_vs_gpu_remote_push_2026-06-19.md`: overnight_queue reads origin/main; push is harness-DENIED to exp_dev. Hence this handoff to Orchestrator.

---

## What this hand-off explicitly does NOT do

- Does NOT push to origin/main (Orchestrator's hd_metrics_sync handles)
- Does NOT queue_add on overnight_queue (Orchestrator dispatches)
- Does NOT register scheduled tasks (already in place)
- Does NOT modify other in-flight cells (per Fix #17/Fix #26 -- author scope only)
- Does NOT author Cell 2 v7+ (USER scope cap: v5 + v6 only)

---

## Expected verdict landing

Per cost models in self-tests:
- v5: ~2780s wall (5 seeds * ~556s); D1 will refine. Lands well within 7200s.
- v6: ~5610s wall (5 seeds * ~1122s); tighter at 78% of 7200s. D1 will gate; if extrapolated > 5760s, cell refuses dispatch + writes minimal metrics with HARD_FAIL_D1_ROOFLINE_REFUSE.

Skunkworks should expect both cells to land within one overnight cycle.
