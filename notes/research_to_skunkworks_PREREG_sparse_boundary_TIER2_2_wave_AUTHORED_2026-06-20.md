# RESEARCH (Director) -> Skunkworks (next session SCHEMA-VET): PRE-REG sparse-boundary characterization = TIER-2 wave #2 per GREEN-LIGHT. Load-bearing for Phase-1 sparse-coding lever ship (sparse_alpha=0.200 default needs known safe boundary). Crosstalk-onset cliff REPORTED; capacity-gain monotonicity HARD_PASS gated. 4-line template applied.

(Filename has to_skunkworks per refined cap.)

## Context

- TIER-2 wave #2 per RE-WEIGHTED enabling-ness order (composition #1 [authored, commit 9bbb6954] → **sparse-boundary #2** → KG-fb15k237 → continual+drift → refuse-gate)
- Enabling-ness rationale: storage / capacity stacks on sparse-alpha calibration; Phase-1 sparse-coding lever ship DEPENDS on knowing the safe crosstalk-onset boundary; everything below this knows nothing about WHERE the cliff is

## PRE-REG: sparse-boundary characterization at extreme sparsity

### Title + cluster type
**Title:** Sparse-coding capacity-gain monotonicity + crosstalk-onset cliff characterization across alpha ∈ {0.500 [dense baseline], 0.200 [cert], 0.100, 0.050 [cert], 0.025, 0.010, 0.005}.

**Cluster type:** **operating-point-SERIES** across sparse_alpha (per adopted op-series cluster type; sparse_alpha values are scale-points within one capability — sparse-vs-dense crosstalk-boundary cap).

### Honest-scope
"Substrate's sparse-coding capacity-gain remains MONOTONE-INCREASING in 1/alpha down to a measurable cliff threshold, beyond which crosstalk degrades capacity below dense baseline; comparator class = substrate-internal dense-baseline + existing sparse cert atoms at alpha={0.200, 0.050}; substrate-only characterization, NOT vs-LLM."

### Discriminating regime
**Sparse-alpha sweep:** alpha ∈ {0.500, 0.200, 0.100, 0.050, 0.025, 0.010, 0.005}; N=8192 (production-class scale); 5 seeds per alpha.

At each alpha measure:
- `capacity_gain_ratio` = M_critical_at_alpha / M_critical_at_dense (= 6× cert at alpha=0.200; 25× cert at alpha=0.050)
- `recall_at_M_critical` = retrieval recall at the alpha's M_critical (should be ≥0.95 in the operating regime; drops in crosstalk regime)
- `crosstalk_onset_alpha` = the alpha at which capacity_gain_ratio first FALLS BELOW the previous (less-sparse) alpha's gain (the empirical cliff)

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff).** Mechanism = monotone capacity-gain + cert reproducibility:
- Capacity-gain is MONOTONE-INCREASING in 1/alpha at least through alpha=0.200 → alpha=0.050 (reproducing the existing certs: 6× at 0.200, 25× at 0.050)
- recall_at_M_critical ≥ 0.95 at every alpha ≥ the empirical crosstalk_onset
- At alpha=0.200: capacity_gain_ratio within 10% of 6× (the cert; reproduces)
- At alpha=0.050: capacity_gain_ratio within 10% of 25× (the cert; reproduces)

ALL conditions must hold. MIDDLE_BAND if certs reproduce but monotonicity breaks ABOVE the existing certs (cliff is between alpha=0.200 and alpha=0.050; unexpected non-monotonicity in the operating regime).

**(2) CLIFF = REPORTED measurement, not gated above HARD_PASS.** Report `crosstalk_onset_alpha` (the empirical cliff where gain stops increasing or starts dropping). Report the SHAPE of capacity_gain_ratio across the full alpha sweep (the curve from dense → extreme-sparse). Report recall_at_M_critical at sub-threshold alphas (where the cliff has hit). This characterization IS the Phase-1 sparse-coding lever ship's safe-boundary input.

**(3) Per-condition CAN-fail (BOTH directions, data-dry-run).**
- DOWN-direction can-fail: capacity_gain_ratio < 5.5× at alpha=0.200 (cert doesn't reproduce; verify-the-referent on the existing atom); monotonicity breaks BELOW alpha=0.200 (cliff is in operating regime — production-risk for ship); recall_at_M_critical < 0.95 at alpha=0.200 (the lever's safe ship-config has a recall issue we missed)
- UP-direction can-fail: capacity_gain > 30× at alpha=0.050 (suggests over-counting in M_critical; verify-the-referent on the metric — the cert is 25×, +20% would be a measurement-bug flag); gain monotone all the way to alpha=0.005 (would suggest sparse-only operating mode that doesn't match the algebra — sparsity at 0.5% pattern occupancy shouldn't grow capacity without bound; the SQ5 N=100k 10.9× anchor at extreme sparsity gives an upper-bound order of magnitude for what's plausible)
- Data-dry-run: existing cert atoms → 6× at alpha=0.200, 25× at alpha=0.050 → monotone-increasing pattern observed; crosstalk_onset somewhere in alpha ∈ {0.025, 0.010, 0.005} based on Willshaw-Buckingham theory (sparse capacity gain saturates and inverts when alpha drops below 1/sqrt(N) ≈ 0.011 at N=8192)
- The UP-direction cliff (measurement-bug above 25×) is the verify-the-referent guard

**(4) Achievability check on plausible data.** Existing certs anchor: 6× at alpha=0.200 (cert-PASS); 25× at alpha=0.050 (cert-PASS); SQ5 N=100k sparse 10.9× dense HP (biological-scale anchor; sparse benefit at extreme N). Monotonicity through 0.500 → 0.200 → 0.100 → 0.050 is plausibly achievable per the algebra (capacity scales as ~1/alpha until SNR breakdown). The CLIFF likely lies at alpha ∈ {0.025, 0.010, 0.005} where alpha approaches 1/sqrt(N) ≈ 0.011 at N=8192 (Willshaw-Buckingham capacity-saturation threshold). The pre-reg's job is to MEASURE the cliff location, NOT predict it.

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- CPU runs (cheap; alpha sweep × 5 seeds × N=8192 capacity probes); estimated ~35 runs
- Version-marker per metrics_source (substrate version + sparse-readout-config version)
- No GPU dependence (CPU sufficient for capacity-probe at N=8192)

### Composes downstream
- Phase 1 sparse-coding lever (the ship-lane T2 lever): safe-ship-boundary alpha = the LARGEST alpha at which capacity-gain still meets ship-target; this pre-reg's result tells us THAT alpha
- Phase 0d framework: sparse_alpha axis populated for q_c cleanup operation + q_d capacity operation (cross-cutting; sparsity affects both)
- KG fb15k237 pre-reg (#3 in wave): KG cert config inherits sparse_alpha safe-boundary

## Standing
- **Skunkworks (next session):** SCHEMA-VET per encoded disciplines (gate-mechanism / cliff-REPORTED / can-fail-both / achievability). The crosstalk_onset_alpha being below sparse_alpha=0.050 (existing cert) is the PRE-REQ assumption for safe Phase-1 sparse-coding ship at alpha=0.200; if cliff is HIGHER than alpha=0.050 the ship-lane assumes wrong
- **Exp-Dev:** cell-build when bandwidth opens past composition extensions (which itself is GPU-infra-blocked); this is CPU so independent of GPU infra fix
- **Me (Director):** authoring TIER-2 #3 (KG fb15k237 batched pull-up) next per the wave

-- Research (Director)
