# Pre-registration: substrate_cl_crispr_append_only_v1

**Date:** 2026-06-24
**Anchor:** substrate_cl_crispr_append_only_v1
**Queue:** local_cpu_queue (pure numpy at N_BASE=4096; per-slab matmul small; ~25-45min wall)
**N_BASE:** 4096, **D_slab:** 819 (= floor(4096/5)), **J_phases:** 5, **M_per_phase:** 400, **Seeds:** [7, 17, 23]
**Primary arm:** ARM_APPEND_ONLY_PLUS_CFRPE

## Scientific question

Does CRISPR-style append-only memory growth (MOVE C structural commitment from cross-biology CL 3rd-angle drill) rescue the substrate from the spectrum CL HARD_FAIL? Spectrum HARD_FAIL diagnosis is 3-part: (i) fused-W antagonism, (ii) IID-pessimal curriculum, (iii) transfer-metric cancellation. CRISPR architecture addresses (i) by construction: each new domain gets NEW orthogonal subspace dims; OLD subspace is frozen and CANNOT be overwritten. This directly tests whether the shared-W architecture is the load-bearing failure point or whether there is a deeper substrate-CL issue.

## Strategic stakes

Substrate has 11 brain-CL primitives but uses NONE of the 3 biology-convergent CL design moves (substrate-offload, clonal-selection, structural-commitment). Brain has neurogenesis (dentate gyrus) for new-task assimilation; current substrate has FIXED shared W. CRISPR bacterial immune memory APPENDS new phage signatures to a tandem-spacer array sequentially without overwriting. Substrate-native analog: per-phase NEW orthogonal subspace; W grows monotonically; OLD subspace preserved by construction.

- **If HARD_PASS:** substrate's CL moat becomes architecturally real (not just primitive-level). Structural-commitment is by-construction-no-forgetting; the substrate-as-CL-product story has a real architectural foundation.
- **If HARD_FAIL:** the issue is deeper than shared-W antagonism. IID-pessimal curriculum or transfer-metric framing must be the next drill (per L4 audit of CL spectrum cell).

## Arm specification (4 arms x 3 seeds)

1. **ARM_BASELINE_STATIC** — Phase 1 train + freeze on full-N fused-W. Sanity rail: Phase 1 recall stays at 1.0.
2. **ARM_FUSED_W_CFRPE_HEBBIAN** — Reproduces spectrum FULL_CL minimal repro: single fused-W with Hebbian-fast write -> CLS-replay (recency-weighted, ALPHA_SLOW=0.1) -> cf-RPE nudge (ALPHA_CFRPE=0.05). Sanity rail: forgetting_p1 in [0.55, 0.75] (spectrum reported 0.65).
3. **ARM_APPEND_ONLY_NEW_DIMS** — Each phase appends a NEW D_slab=819 subspace; Hebbian write only into new slab; old slabs HARD-FROZEN; no cf-RPE.
4. **ARM_APPEND_ONLY_PLUS_CFRPE (PRIMARY)** — Append-only + cf-RPE delta-rule on NEWLY-added slab only. Old slabs HARD-FROZEN.

## Architecture (CRISPR slab partition)

- W starts empty. At phase j, allocate a NEW W_slab_j of shape (D_slab, D_slab); D_slab = floor(N_BASE / J_PHASES) = 819.
- Total W after J phases = block-diagonal direct-sum of J slabs.
- Per-slab alpha = M / D_slab = 400 / 819 ~= 0.488 (matches fused-W alpha; alpha-fair).
- Retrieve via max-cosine slab routing: probe scored against each slab's one-step Hopfield retrieval; argmax slab does the full retrieval.
- Routing accuracy reported per phase per arm.

## Pre-registered HARD bands

**Sanity rails (required):**
- ARM_BASELINE_STATIC Phase 1 initial recall in [0.85, 1.00]. Smoke: 1.000 (pass).
- ARM_FUSED_W_CFRPE_HEBBIAN forgetting_p1 in [0.55, 0.75] (FULL mode only; smoke alpha sub-cliff so rail skipped).

**HARD_PASS_CRISPR_MOAT:**
- ARM_APPEND_ONLY_NEW_DIMS forgetting_p1 < 0.10
- AND mean_total_slabs >= J_PHASES (5 slabs allocated, one per phase).

**HARD_PASS_CRISPR_PLUS_PLASTICITY (PRIMARY):**
- ARM_APPEND_ONLY_PLUS_CFRPE forgetting_p1 < 0.10
- AND ARM_APPEND_ONLY_PLUS_CFRPE transfer_final >= 0.30 (cf-RPE on new dims gives real plasticity).
- AND cv_forgetting_p1 < 0.05 across seeds.

**MIDDLE_BAND:** forgetting in [0.10, 0.30] on either CRISPR arm; CRISPR partly characterized but not chain-grade.

**HARD_FAIL_DECISIVE:**
- ARM_APPEND_ONLY_NEW_DIMS forgetting_p1 >= 0.30 (structural-commitment doesn't fix CL; deeper substrate-level issue).
- OR sanity rails violated.

## Apples-to-apples (per master bias checklist)

- **Lane 1 declared:** substrate-native CL architecture comparison (fused-W vs CRISPR append-only).
- **CONFOUND_AUDIT:**
  - D_slab constant across CRISPR arms; D_slab * J <= N_BASE.
  - Frozen-old-slab policy: HARD-freeze (strict structural-commitment test).
  - Subspace orthogonality: by construction (disjoint dims).
  - Parameter-budget asymmetry DOCUMENTED: fused-W has N_BASE^2 params; CRISPR has J*D_slab^2 ~ N_BASE^2 / J params. CRISPR uses LESS total compute per write -- this is a feature, not a confound.
- **INTRA_LANE_DELTA:** ARM_APPEND_ONLY -> ARM_APPEND_ONLY_PLUS_CFRPE varies ONE thing = cf-RPE delta-rule passes on the new slab. Both freeze old slabs.
- **Single primary metric:** forgetting_p1 (top1 recall on Phase 1 atoms after Phase J training).
- **Pre-registered primary arm:** ARM_APPEND_ONLY_PLUS_CFRPE.

## Calibration rationale

- Smoke (J=3, M=200, N_BASE=4096, 2 seeds) measured wall = 49.4s.
- Smoke verdict: HARD_PASS. CRISPR mechanism works as designed (forget=0, slabs=3, routing=1.0).
- Smoke alpha_fused = 0.1465 < Hopfield cliff 0.138; smoke doesn't stress FUSED_W. Full alpha_fused = 0.488 should reproduce spectrum forgetting=0.65.
- HP_FORGETTING_MAX = 0.10 inherited from CL spectrum prereg.
- HP_TRANSFER_MIN = 0.30 calibrated to task-spec: cf-RPE on the new slab should give measurable plasticity above bare-Hebbian retention.

## N-suffix section

Anchor has NO _n<N> suffix (PROT-018 family-level naming). Production N_BASE = 4096; script asserts at config load. No mismatch possible.

## Timeout estimate

- Smoke wall: 49.4s (J=3, M=200, 2 seeds).
- FUSED_W arm is dominant cost (4096x4096 matmuls); CRISPR arms are 25x cheaper per write (819x819 per slab).
- Full vs smoke scaling: J 3->5 (1.67x), M 200->400 (4x via Hebbian M^2 in Xi^T Xi), seeds 2->3 (1.5x).
- Formula: ceil(1.5 * 49.4 * 1.67 * 4 * 1.5) ~= 745s.
- PROT-019 floor: anchor has no _n<N> suffix, so floor does NOT bind.
- Use timeout_s = 5400 (matches reference spectrum cell; safety x7 over formula estimate).

## What this does NOT show

- NOT a fix for IID-pessimal curriculum (Issue 1 of L4 audit). HARD_PASS here is robust to ANY curriculum because old slabs are protected.
- NOT cross-CORPUS continual learning (synthetic bipolar atoms only).
- NOT a comparison to transformer fine-tuning baseline (out-of-scope).
- NOT a soft-freeze ablation (only hard-freeze tested).
- NOT a learned-gating variant (max-cosine routing only).
- Slab routing is max-cosine-on-one-step-retrieval; not energy-functional; not learned.

## Citation

- Barrangou R, Fremaux C, Deveau H, Richards M, Boyaval P, Moineau S, Romero DA, Horvath P. CRISPR provides acquired resistance against viruses in prokaryotes. Science 315:1709 (2007).
- Research drill: `notes/research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md` (L5 Cell 1 design).
- exp_dev_handoff: `notes/exp_dev_handoff_research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md`.
- Reference cell: `experiments/exp_substrate_continual_learning_spectrum_v1.py` (provenance + 5-arm fused-W spectrum).
- Reference prereg: `preregs/2026-06-24_substrate_continual_learning_spectrum_v1.md`.
