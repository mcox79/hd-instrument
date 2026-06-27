# Pre-registration: pfc_controller_orthogonal_role_basis_v1

**Date:** 2026-06-27
**Anchor:** pfc_controller_orthogonal_role_basis_v1
**Queue:** remote_cpu_queue
**N:** 8192, **Seeds:** [7, 17, 23, 31, 41], **Depth:** 4 (decision depth; sweep includes 3,4,6,8)

## Scientific question

Does Gram-Schmidt orthogonalization of role-basis atoms against the filler codebook (entity atoms E) at INIT raise multi-hop heterogeneous routing accuracy compared to a shared-random-basis baseline at depth=4, by removing accidental role/filler alignment? Sister cell exp_pfc_controller_softmax_margin_abstain_v2 (HARD_PASS, same regime) -- this drill is Battery 2 Barrier 1 RANK 3 cheapest single-init change.

## Pre-registered bands

**HARD-PASS:**
- ORTHOGONAL_ROLE_BASIS lift over SHARED_BASIS >= +0.10 at depth=4.
- cv across seeds < 0.10.
- ORTHOGONAL > PARTITIONED by >= +0.03 (orthogonality matters above disjoint-subspace; rules out the lift coming purely from dimension-disjointness).

**MIDDLE:** Lift in [+0.05, +0.10) OR cv in [0.10, 0.20).

**HARD-FAIL:** Lift < +0.05 OR ORTHOGONAL <= SHARED_BASIS + 0.03 (mechanism null).

## Calibration rationale

Sister cell PFC controller v2 HARD_PASSed with +0.10 lift on a related fairness-revival drill; the orthogonal-role-basis intervention is mechanistically tighter (decouples role-contribution from filler-similarity at init by direct Gram-Schmidt projection). At N=8192 random bipolar atoms have expected pairwise cosine ~1/sqrt(N)=0.011 -- so the accidental role-filler alignment is small in absolute magnitude, but accumulates across 4 hops; expected lift on this scale is modest (+0.05 to +0.15). The 0.10 floor reflects that the cell mustn't fire on noise-level effects; the partitioned-control floor (+0.03) ensures that the lift is attributable to orthogonality rather than disjoint-dimensions.

## N-suffix section

No _n<N> in anchor (matches sister cell convention). Production N_DIM = 8192; smoke N_DIM = 4096; selftest N_DIM = 512.

## Timeout estimate

Smoke: N=4096, 3 seeds, depths [3,4] -> ~3-5 min per seed (Hebbian writes + 60-chain routing per depth per arm). Total smoke ~10 min wall.
Full: N=8192, 5 seeds, depths [3,4,6,8]. Dominant cost is the depth-8 chain at N=8192 (each hop is an O(N) inner-product + O(V*N) cleanup). 100 chains x 4 depths x 3 arms ~= 1200 chain-evals per seed; expected ~8-12 min per seed; 5 seeds ~= 50 min plus overhead.
formula: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.0 * (FULL_seeds/smoke_seeds) * (FULL_depths/smoke_depths)) = ceil(1.5 * 600 * 2 * (5/3) * (4/2)) = ~6000 s
timeout_s = 7200 (2h; covers slowest depth-8 case with margin)

# -----------------------------------------------------------------------------
