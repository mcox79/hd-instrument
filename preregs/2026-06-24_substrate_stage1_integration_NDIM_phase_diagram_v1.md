# Pre-registration: substrate_stage1_integration_NDIM_phase_diagram_v1

**Date:** 2026-06-24
**Anchor:** substrate_stage1_integration_NDIM_phase_diagram_v1
**Queue:** overnight_queue
**N:** sweep {4096, 8192, 16384, 32768}, **Seeds:** 3 (7, 17, 23), **Param:** N_DIM_GRID

## Scientific question
Do seven individually-chain-grade-validated substrate ingredients (substrate-OWNED encoder, rank-1 Hebbian outer-product W, role-tagged HRR binding, CRISPR append-only growth, Wave14R K50 multi-hop, tau-gate refuse, 1/sqrt(f) amplitude) compose into a single substrate stack that reproduces each capability at production scale, and how does the integrated stack scale with N_DIM (phase-diagram navigation per USER 2026-06-22 latent-capability framing)?

## Pre-registered bands

**HARD-PASS (STAGE_1_INTEGRATED_CHAIN_GRADE):**
- At canonical N_DIM=8192: >= 5 of 6 tasks chain-grade
- AND phase-diagram-mapped: all 24 measurements (6 tasks x 4 N_DIM) classified into {chain-grade | partial | off-regime} and reported

**HARD-PASS auxiliary (N_DIM_SCALING_CHAIN_GRADE):**
- Each task chain-grade at >= 2 distinct N_DIM values (capabilities not single-N artifacts)

**MIDDLE:** 3 or 4 tasks chain-grade at canonical N_DIM=8192.

**HARD-FAIL (HARD_FAIL_INTEGRATION_BREAKS):** < 3 of 6 tasks chain-grade at canonical N_DIM=8192 (individually-proven capabilities don't compose in single cell).

### Per-task chain-grade thresholds
- T1 STORAGE (rank-1 Hebbian, M=2000, sparse-bipolar f=0.02): top1 >= 0.95
- T2 CAPACITY_CEILING (M sweep [500, 1000, 2000, 4000, 8000]): M_critical >= 4000 * (N/8192) (linear scale in N)
- T3 MULTIHOP_K20_K50 (Wave14R, beta=6.0, K_set=50): K20_acc >= 0.85 AND K50_acc >= 0.40
- T4 COMPOSITIONAL (HRR role-filler, 4 roles x 16 fillers): lift_over_chance >= 5.0
- T5 CL_CRISPR_3DOMAIN (append-only block-diagonal slabs, J=3): forgetting_d1 < 0.05
- T6 REFUSE_TAU (calibrate on half, eval on half): refuse_acc (balanced) >= 0.80

### Per-task partial thresholds
- T1 top1 in [0.70, 0.95): partial
- T2 M_critical in [0.5 * scaled, scaled): partial
- T3 K20 >= 0.6 OR K50 >= 0.2 (but not chain-grade): partial
- T4 lift in [2.0, 5.0): partial
- T5 forgetting in [0.05, 0.20): partial
- T6 refuse_acc in [0.65, 0.80): partial

## Calibration rationale
- T1 0.95: matches sparse-bipolar Hebbian recall reference from CERT 590 CSP first-ship + Wave14R cell family at f=0.02.
- T2 4000 at N=8192: rank-1 Hebbian bound is alpha=M/N <= 0.5 for clean recall; 4000/8192=0.49. Scales linearly with N because Hebbian capacity is rank-bounded.
- T3 K20>=0.85 AND K50>=0.40: matches Wave14R K50 reference from r1 multi-hop K=2 chain-grade (CERT 588 family) where naive-2hop accuracy ranges 0.487 at K=50 to 0.987 at K=20 on the validated KG family. Synthetic-random graphs here are STRICTER than ConceptNet (no relational regularity to exploit) so thresholds pre-reg the LOWER end of the validated range.
- T4 5x chance: matches HRR role-filler binding literature + n8 KG primitive r=1 lift. Chance = 1/(R*F) = 1/64 = 0.0156; 5x = 0.078; HRR primitive routinely achieves this at any N >= 1024.
- T5 forgetting < 0.05: CRISPR append-only is by-construction zero-forgetting on the OLD slab (frozen at recall). Slack of 0.05 absorbs measurement noise.
- T6 0.80 refuse_acc: matches r1b multi-hop refuse calibration v1 standard (balanced accuracy on calibration+eval split). Below 0.80 indicates degenerate discriminator.

## N-suffix section
NO _n<N> suffix per PROT-018: this anchor is a PHASE-DIAGRAM SWEEP across {4096, 8192, 16384, 32768}; production N is the GRID itself, not a single value. The variable `N_DIM_GRID` carries the production values.

## Timeout estimate
Smoke laptop-CPU at N=512 single seed all 6 tasks: ~30-60s (measured at gate time; will be confirmed below).
Per-cell scaling: T1+T2+T5+T6 are O(M^2) + O(N*M); T3 is O(N^2) for Wave14R matmul (W accumulate + per-hop W@key); T4 is O(N log N) per binding * (R*F)*queries.

D1 ROOFLINE PROBE (estimate; will be verified by smoke):
- N=512 (smoke) all 6 tasks: ~30s
- N=4096 = 8x linear, but T3 N^2 = 64x => ~5 min on GPU
- N=8192 = 16x linear, T3 N^2 = 256x => ~10 min on GPU
- N=16384 = ~25 min on GPU
- N=32768 = ~80 min on GPU
- Per seed total: ~120 min
- 3 seeds = 360 min = 6 hours

formula: ceil(1.5 * 60s * (32768/512)^1.5 * (3/1)) -- but T3 dominates and scales N^2, so use scaling_exp=1.5 across the GRID dominant cost
ceil(1.5 * 60 * 64^1.5 * 3) = ceil(1.5 * 60 * 512 * 3) = 138240s = 38h -- TOO LOOSE

Use empirical roofline: smoke + linear extrapolation per cell:
T_per_cell(N) ~ T_smoke_per_cell * (N/512)^1.5 (matmul on GPU + per-cell setup)
Sum across N_DIM_GRID = T_smoke * [(8)^1.5 + (16)^1.5 + (32)^1.5 + (64)^1.5]
                     = T_smoke * [22.6 + 64 + 181 + 512] = T_smoke * 780
Per seed total = 780 * T_smoke_per_cell
3 seeds = 2340 * T_smoke_per_cell

If T_smoke_per_cell ~= 30s (laptop CPU) -> GPU is ~10x faster -> 3s effective
=> 3 seeds total ~ 7020s = 117 min
1.5x safety => 175 min = 10500s

CONSERVATIVE PRE-RUN ESTIMATE: timeout_s = 18000 (5 hours) -- gives headroom for N=32768 matmul on GPU + GPU contention + cold-start.

If smoke wall comes back larger than ~60s, scale timeout proportionally.

timeout_s = 18000

## Disciplines applied
- ASCII-only per feedback_ascii_only_in_scripts
- Fix #14: spawn-budget; cell-author + smoke + dispatch in main thread (this cycle)
- Fix #17: smoke runtime measured (BLOCKING_BEFORE_DISPATCH)
- Fix #24: GPU dispatch (torch.cuda); MUST use GPU not just route to remote
- Fix #26: predispatch_check.py PROCEED (no prior landings)
- Fix #28: per-arm metrics not verdict_msg summary
- D1 roofline probe before timeout
- D2 atexit + per-(N,seed) checkpoint via _seed_checkpoint.write_partial_key
- PROT-021: run_mode stamped on every partial; smoke partials rejected by FULL runs
- A5: cert-owner final tier (this cell pre-reg sets bands; landed-VET decides)

## Cites
- experiments/exp_substrate_stage1_integration_NDIM_phase_diagram_v1.py (this cell)
- experiments/exp_substrate_cl_crispr_append_only_v1.py (CRISPR primitive reference)
- experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py (substrate-owned encoder pattern)
- experiments/exp_wave14_1rsb_hysteresis_v6_n4096.py (Wave14R primitive)
- hdlab/kg_traversal.py (KGStore composes-with)
- hdlab/multi_hop.py (Wave14R K_set softmax cleanup)
- hdlab/refuse_gate.py (tau calibration)
- USER 2026-06-22 phase-diagram-action + data-survives-phase-transformations latent-capability framing
- USER 2026-06-24 GPU idle + integration + phase-diagram-navigation directive
