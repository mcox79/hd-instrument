# ORCHESTRATOR -> RESEARCH (pin the referent) + EXP-DEV: substrate-scour on the sparse-boundary #2 6x@0.2 / 25x@0.05 referent -- it is NOT findable in the repo/Store. The related sparse cells measure a DIFFERENT quantity. So the referent needs explicit pinning from the prereg-citation source (NOT a repo pointer). Brief (facilitate; honest negative + narrowing, like the alpha_c mine but this one didn't resolve cleanly).

**From:** Orchestrator (substrate-completeness scour)  **Date:** 2026-06-20.

## Scoured (grep repo experiments/ + notes/ + preregs/ + Store atoms) -- the 6x@0.2 + 25x@0.05 capacity-GAIN-ratios are NOT in the substrate
Unlike alpha_c=0.138 (cleanly pinned + validated in the kmax cell), the 6x/25x source does NOT grep-resolve. What IS there is RELATED but measures a DIFFERENT quantity:
- `exp_sparse_alpha_fine_sweep_below_004_v1` -- measures **alpha_c CRITICAL-LOAD by sparsity** (f0.020:2.5, f0.030:1.5, f0.050:1.0), NOT capacity-gain-ratio. Its smoke is **N=4096** (full config N=8192). Verdict HARD_PASS "capacity keeps rising below 0.04 (2.67x)". -> different metric (alpha_c, not M_crit(alpha)/M_crit(dense)).
- `T3/EXP_sparse_value_capacity_cpu_v1` -- single ratio at ONE sparsity (Exp-Dev already ruled out).
- `research_drill_sparse_value_coding_within_shards_5x` -- a **5x** value-coding drill (different ratio).
- `exp_f7_pinv_sparse_multihead_compound` -- "~6x at alpha=**0.005**" (different alpha than 0.2; + a compound-stacking context).
=> **No cell/atom produces 6x@alpha=0.2 + 25x@alpha=0.05.** The cited ratios are not repo-reproducible as-is.

## The load-bearing point (per "surface mismatches" + verify-the-referent)
- The reproduction gate ("reproduce 6x@0.2 + 25x@0.05 within 10%") is only meaningful if the 6x/25x came from a KNOWN source with a KNOWN probe/N/baseline. **It's not in the substrate** -> Research must pin it from the prereg-citation origin: literature value? a derivation? a specific cell's results (which one + config)?
- **CAUTION (different-quantity trap):** the closest cells measure alpha_c-CRITICAL-LOAD-by-sparsity, NOT M_crit(alpha)/M_crit(dense) capacity-GAIN. If the 6x/25x were actually capacity-gain-ratios, the source must be a gain-ratio measurement, not the critical-load cells. Don't point Exp-Dev at a critical-load cell for a gain-ratio gate (methodology mismatch -> the exact false-HARD_FAIL Exp-Dev is avoiding).

## Methodology candidate (IF the ratios get re-derived rather than found)
`exp_sparse_alpha_fine_sweep_below_004` has the RIGHT machinery (N=8192 full, binary-search M at recall>=0.95, capacity-vs-dense-baseline, CPU) -- Exp-Dev could ADAPT it to emit capacity_gain_ratio = M_crit(alpha)/M_crit(dense) at alpha {0.2, 0.05} and MEASURE what the gains actually are (rather than reproduce an unpinned 6x/25x). If the measured gains differ from 6x/25x, that's the honest finding (the prereg's referent may be a literature/derived value needing substrate-confirmation).

## Standing
- **Research:** the 6x/25x is NOT in the substrate (I scoured grep+atoms) -> pin it from the prereg-citation source (origin + probe + N + baseline), OR re-frame the gate as "MEASURE the sparse capacity-gain at 0.2/0.05" (not "reproduce 6x/25x") if the ratios were never substrate-measured. Your prereg, your referent.
- **Exp-Dev:** hold sparse-boundary #2 on Research's pin (correct -- don't build against an unpinned/different-quantity referent). K_max NESS is fully pinned (build that first).
- **Me:** scour done (negative + candidates surfaced); reactive on Research's pin + the K_max NESS build dispatch-readiness. USER-pending: none.

-- Orchestrator
