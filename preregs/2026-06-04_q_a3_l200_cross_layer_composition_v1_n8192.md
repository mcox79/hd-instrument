# Prereg: q_a3_l200_cross_layer_composition_v1_n8192

## Anchor
q_a3_l200_cross_layer_composition_v1_n8192

## Priority
A (cycle 55 EXTREME-DEPTH sweep: L=200/L=300 N=16384 both HARD_PASS -> map where composition breaks)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at extreme depth L=200 N=8192?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/8192 = 0.0122 << alpha_c=0.138.
This probes whether floating-point accumulation over 200 sequential Hadamard+Hopfield ops degrades
fidelity, locating the practical depth bound (if any).

## Pre-registered bands
HARD-PASS: all 200 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l200_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern (locates practical bound).
HARD-FAIL: any L_fid < 0.85 OR l200_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=8192 -> alpha=0.0122 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 198. [INPUT: L_DEPTH=200] [EXPECTED: len(M_MID)=198]
3. L=200 chain: 199-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: exact]

## Extreme-depth note (cycle 55)
L=200 is far past the validated frontier (N=16384 L=200/L=300 HARD_PASS; prior incremental frontier
L=156). One-shot probe of the extreme regime. Smoke-at-low-N satisfied by remote --self-test (199-ctx
chain decode + capacity asserts). Full run N=8192 5-seed. Memory: on-demand W 8192x8192x4 bytes, one at
a time. A MIDDLE_BAND result here is informative (finds the practical depth bound), not a failure of theory.

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192. Script constant N = 8192.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600 (L=200 est. wall few min; floor dominates).

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates chain decode + capacity. gen_qa3_scripts.py template (same as L=137 HARD_PASS).

## Queue
overnight_queue (GPU required).
