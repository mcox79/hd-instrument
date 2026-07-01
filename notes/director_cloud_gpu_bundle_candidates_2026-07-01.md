# Cloud-GPU Bundle Candidates

**Filed:** 2026-07-01
**Trigger:** USER offered cloud GPU capacity for special-needs experiments; wants bundle collected first before dispatch.
**Local GPU ceiling:** RTX 4060 Ti / Windows / 8 GB VRAM / no `expandable_segments` support (see `feedback_pytorch_windows_expandable_segments_unavailable_2026-07-01.md`)

**🚨 USER DIRECTIVE 2026-07-01 (dispatch cadence):** Cloud GPU runs are **ONCE per STAGE as the last, single run of that stage** — NOT an ongoing overflow queue. Accumulate candidates per stage; when Stage N is otherwise complete, do ONE bundled cloud-GPU run that pushes to the frontier. Then move to Stage N+1.

**Implication:** don't add cells to a cloud-GPU queue mid-arc. Only trigger cloud dispatch when signaling "Stage N is done + this final run is the culmination test."

---

## Ready-to-run candidates (hit hardware ceiling on local GPU today)

### 1. Cell D N-sweep v1 (CUDA OOM at N=32768)
- **Commit:** `b239d531`
- **Local result:** 3-seed FULL failed CUDA OOM at N=32768; runs at N∈{4096, 8192, 16384} would need to be captured too
- **What cloud GPU adds:** verifies M3 architecture (dense-Hopfield READ-REPLACE) scales past 8GB local ceiling
- **Cell files:** `experiments/exp_cortex_hippo_dense_layer_N_sweep_v1_seed_{7,13,19}.py`
- **Prereg:** `preregs/2026-07-01_cortex_hippo_dense_layer_N_sweep_v1.md`
- **Memory need:** ≥ 16 GB VRAM (N=32768, replacement-mode attention on M=8192)
- **Wall estimate:** ~5-15 min per seed on cloud GPU
- **CG payoff:** if HP at N=32768 → M3 scaling win; validates cortex layer for larger substrates

### 2. Cell D M-ultra-extend v4 (a53b061a; likely also OOM)
- **Status:** cell-author was authoring; result unclear post-restart
- **Target:** M ∈ {8192, 32768, 65536} at N=8192
- **Memory need:** ≥ 24 GB VRAM (M=65536 attention is heavy)
- **CG payoff:** validates replacement-mode at 8x capacity crack

### 3. Batch B seqbind_N_dim_scaling v1.6 (Windows-capped at N=16384)
- **Commit:** `f6157dca`
- **Local result:** N=32768 dropped due to Windows-lacking-expandable_segments; landed HF at cardinality (56 not 70)
- **Cloud GPU adds:** re-enables N=32768 point for full scaling curve
- **Memory need:** ≥ 16 GB VRAM
- **Wall estimate:** ~15-30 min per seed
- **CG payoff:** N-scaling law CG-lift; validates hdlab K_cliff formula at N=32768

### 4. Compositional generation depth-15+ (extends today's smoke +0.700 lift)
- Compositional generation depth-8 landed today at HP smoke
- Cloud GPU could push depth ∈ {15, 20, 30} which may exceed local capacity
- Load-bearing for M3 language substrate (Stage 4 prerequisites)

### 5. Cortex_hippo replace+refuse-gate composition v2 (regime revival)
- Cell v1 honest-abort at M/N_c=0.049 (baseline saturated)
- Revival needs M ≥ 400 at N_c ≥ 8192 = M/N_c ≥ 0.05
- Larger M/N ratios may fit local; but cloud GPU comfortable at N_c=16384 M=800+

## Upcoming candidates (in flight; may qualify)

- Cell D M-ultra-extend (a53b061a) — pending return
- Multihop d20-40 (a49646eaf) — likely fits local but could benefit from cloud parallelism
- Cell D + refuse-gate composition v2 (need author to iterate) — cloud-comfortable at M≥400

## Not candidates (fit local GPU comfortably)

- ANCHOR4 encoder N=16384 (2.6s per seed on RTX 4060 Ti) — CG landed
- Capacity multi-bank HIGH (35s per seed) — HP landed
- Theta-gamma v3 N=16384 (fits local)
- Any numpy-only cell (routes to remote_cpu_queue anyway)

## Bundle-and-dispatch protocol (proposed)

1. Continue accumulating candidates until USER signals bundle full
2. Package all cell files + preregs + prior evidence + expected GPU footprint per cell
3. Prepare cloud-GPU dispatch batch with:
   - Cloud provider (AWS EC2 p3.2xlarge V100 16GB or p4d.24xlarge A100 40GB depending on need)
   - Docker/venv image with hd-instrument environment
   - Batch queue script that runs all cells sequentially or in parallel across multiple GPUs
   - Result-collection mechanism (SCP back to marsh@home for local integration)
4. Skunkworks VET on landing (same STANDARD_LANDED_VET as remote)

## Priority ranking (highest CG payoff per compute-hour)

1. **Cell D N-sweep v1** (already failed local; direct swap-in) — HIGH
2. **Batch B seqbind v1.6 re-enabled N=32768** (formula-adjacent to today's CG) — HIGH
3. **Cell D M-ultra-extend** (validates M-scaling of M3 architecture) — HIGH
4. **Cortex_hippo replace+refuse-gate v2** (regime revival) — MEDIUM
5. **Compositional generation depth-15+** (Stage 4 prerequisite) — MEDIUM

## Estimated total compute

- 5 cells × ~15-30 min each × 3 seeds = ~4-8 GPU-hours (single-GPU sequential)
- Parallel across 4 GPUs = ~1-2 hours wall
- Cost estimate: ~$5-15 on cloud provider spot pricing
