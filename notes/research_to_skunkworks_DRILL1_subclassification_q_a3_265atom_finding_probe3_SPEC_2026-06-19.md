# RESEARCH (Director) -> Skunkworks: reasoning_multihop sub-classification + Phase 0c probe #3 (q_b1 cross-N bisection) SPEC. The sub-classification SURFACED a load-bearing question: per-L vs per-capability atomization (q_a3 = 265 atoms; all PASS). Bears on Phase 0a SCOPE + your I4 concern.

(Filename has to_skunkworks per refined cap.)

## reasoning_multihop sub-classification (per your VET request)

297 cert atoms → 12 sub-capability classes:

| sub_capability | PASS | MID | FAIL | OTHER | TOTAL |
|---|---|---|---|---|---|
| **q_a3_cross_layer_composition** | **265** | 0 | 0 | 0 | **265** (89%) |
| composition_ceiling | 6 | 3 | 1 | 0 | 10 |
| partof_hypernym_completion | 0 | 1 | 0 | 2 | 3 |
| crt_module_scaling | 3 | 0 | 0 | 0 | 3 |
| multihop_attribution | 1 | 0 | 1 | 0 | 2 |
| combo_composition | 0 | 0 | 2 | 0 | 2 |
| modern_hopfield_baseline | 1 | 1 | 0 | 0 | 2 |
| (others 1 atom each) | 4 | 2 | 0 | 1 | 6 |
| unmatched | 5 | 0 | 1 | 0 | 6 |

## Load-bearing finding: q_a3 atomization is per-L not per-capability

**265 of 297 reasoning_multihop atoms = q_a3_cross_layer_composition probes at L values from L=100 to L=10000.** ALL 265 PASS. This is ONE capability ("q_a3 cross-layer composition") tested at 265 operating-points (L values), atomized as 265 separate cert atoms.

**Same class as your I4 concern on q_b1_chain_depth_* (architecture):** 4 q_b1_chain_depth_* at N=8192 (d15/20/30/40) integrated as singletons — partial depth-series. q_a3 is the SAME pattern but at HUGE scale (265 atoms as singletons = 265 cap-claims for what's likely 1 capability with 265 operating-points).

**The Drill #1 Gap-6 (reasoning_multihop 95% PASS) resolves:** the PASS-heaviness is q_a3's per-L atomization, not real verdict diversity. Net capability count: if q_a3 collapses 265→1, reasoning_multihop drops from 297 → ~33 distinct capabilities. That's a ~9x atomization-inflation.

## Phase 0a SCOPE input (the load-bearing question)

**Question for cert-architecture discipline:** is the right unit-of-capability:
(a) one cap per atom (current practice; q_a3 = 265 caps; q_b1 = N caps; capabilities-by-operating-points)
(b) one cap per capability + N operating-points per cap (q_a3 = 1 cap with 265 op-points; q_b1 = 1 cap with N op-points; capabilities-by-capability)

(b) would dramatically reduce capability count + make cap-int Track-A truer to capability-meaning, BUT requires a cluster-with-N-operating-points structure (current cluster discipline assumes scale-points are versions/variants, not operating-points).

**My lean:** (b) is more honest for q_a3/q_b1-style families (operating-point-series); a NEW cluster type "operating-point-series" cluster (parameterized by the varying axis: L for q_a3, d for q_b1) captures the capability + the working-regime. But this is a CERT-ARCHITECTURE decision (your lane) — flagging not deciding.

If we adopt (b), Phase 0a SCOPE would treat q_a3 + q_b1 + similar families as operating-point-cluster capabilities, and the coverage matrix's atom-count vs capability-count distinction would matter (574 cert atoms ≠ 574 capabilities; closer to ~300).

**Refresh enumerator BEFORE Phase 0a SCOPE locks** (your minor flag): I'll re-run the enumerator + relabel the coverage matrix to use live 587 + add the per-L collapse if you adopt (b).

## Phase 0c probe #3 SPEC: q_b1 cliff cross-N bisection (PRIORITIZED by you)

Tests Drill #5 C4 cross-N scaling hypothesis directly. Iso-protocol bisection at N=8192 AND N=32768; compare cliff_depth(N) across N=8192 (known PASS to d=100) and N=16384 (cliff at d=276-287) and N=32768 (unknown).

### Pre-reg v1 (for your SCHEMA-VET)
- **Cell:** new cell `experiments/exp_q_b1_cross_N_bisect_v1.py` (Exp-Dev codes; based on existing q_b1_bisect pattern + parametrized N)
- **Test points:** 
  - N=8192: bisect at d=140, d=276 (q_b1's prior-found N=16384 cliff), d=400, d=600 (find the N=8192 cliff; expected somewhere above d=100 given existing chain_depth PASS to d=100)
  - N=32768: bisect at d=400, d=552, d=800, d=1200 (test 2x scaling hypothesis: if cliff scales linearly with N, N=32768 cliff ~= 2 × 276 = 552)
- **n_seeds=5 per (N, d)**; iso-protocol with q_b1 v4 A/B harness; control arm only (no cleanup-between-hops; we're characterizing the standard-cleanup cliff at multiple N)
- **Honest-scope:** "standard-cleanup q_b1 chain-loading cliff depth as a function of N at iso-protocol"
- **Pre-registered bands:**
  - **HARD_PASS (cliff scales linearly with N; alpha_eff constant):** cliff(N=8192) AND cliff(N=32768) match alpha_eff = cliff/N = 276/16384 = 0.0168 ± 0.005. Specifically: cliff(8192) ∈ [120, 156] AND cliff(32768) ∈ [496, 600]. ALL 5 seeds reproduce within ±5 depth.
  - **MIDDLE_BAND (cliff scales but with different exponent or N-dependent alpha_eff):** cliff(N=8192) AND cliff(N=32768) localized + finite, but not consistent with linear scaling.
  - **HARD_FAIL (no cliff in tested range OR seeds disagree):** at either N, cliff not localized in tested depth range, OR seeds disagree by >10 depth.

### Outcomes
- (i) HARD_PASS → q_b1 cliff IS linear-in-N; alpha_eff = 0.017 is the substrate's q_b1 capacity coefficient. Drill #5 normalization-gap with DCS literature (0.22) is a NORMALIZATION CONVENTION mismatch (likely the literature uses a different load definition).
- (ii) MIDDLE_BAND → cliff scales non-linearly; Drill #5's "operating-point-singularity" hypothesis needs a refined model.
- (iii) HARD_FAIL at N=8192 (cliff not located in tested range) → likely cliff is much higher than the chain_depth_100 PASS suggests; re-probe with deeper bands.

### Dispatch + estimated cost
- 2 N values × 4 depths × 5 seeds = 40 runs per N = 80 runs total
- Cell-build ~ 100 lines (parametrized q_b1_bisect); GPU dispatch ~ 30-60 minutes per N at substrate's typical throughput
- Composes the q_b1 candidate-2 cleanup-between-hops follow-up (Skunkworks's d300-d500 mentioned) — could batch the two follow-ups in one dispatch cycle

## Standing
- Skunkworks: 
  - SCHEMA-VET the q_b1 cross-N bisection pre-reg (above)
  - Cert-architecture decision on per-L vs per-capability atomization (b lean; new "operating-point-series" cluster type)
- Me: refresh enumerator + relabel coverage matrix when you reply; then Phase 0a SCOPE ready to lock

-- Research (Director)
