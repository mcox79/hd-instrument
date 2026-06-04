# Prereg: q_a3_l10000_cross_layer_composition_v1_n16384

## Anchor
q_a3_l10000_cross_layer_composition_v1_n16384

## Priority
A (single authorized deep marketing/demo anchor per capacity-stress redirect: "ONE single run at
L=10000 would suffice rather than continuing the ladder"). Depth-ladder otherwise STOPPED.

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0000 at the striking depth L=10000 N=16384?
Per algebra: sign-rounded bipolar composition has no precision-drift mechanism (noise/signal ~1e-5 <<
sign threshold), so EXACT is expected at M~0 storage pressure. One headline anchor.

## Pre-registered bands
HARD-PASS: all 10000 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l10000_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
HARD-FAIL: any L_fid < 0.85 OR l10000_acc < 0.5.

## Formula self-tests (PROT-022)
1. M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. 2. M_MID length == 9998.
3. L=10000 chain: 9999-ctx Hadamard roundtrip recovers xi_L1. [in script _selftest]

## N-suffix binding (PROT-018)
anchor _n16384; production N=16384. 5 seeds.

## Timeout
L=10000 ~5x L=2000 wall; est few-to-10 min. PROT-019 floor: 21600s. Memory: on-demand W one at a time;
Xi_layers ~1.3GB; peak ~2.5GB < 8GB.

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates the 9999-ctx chain decode + capacity asserts.
gen_qa3_scripts.py template (same as L=2000 HARD_PASS).

## Queue
overnight_queue (GPU required).
