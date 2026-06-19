# Pre-registration: a2_oneshot_addition_recall_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: a2_oneshot_addition_recall_v1

## Scientific question
Can new (key,value) patterns be added one-shot to a pre-existing Hopfield substrate
with immediate recall and no degradation of previously stored patterns?

## Hard-pass (pre-registered)
HP1: new pattern cosine >= 0.90
HP2: existing acc after addition >= 0.95
HP3: write time < 1.0s

## Hard-fail (pre-registered)
HF1: new pattern cosine < 0.70
HF2: existing acc drops > 10pp

## Middle band
2/3 HP conditions met

## Smoke result
HARD_PASS: all 3 HP conditions met (N=256 smoke, 2 seeds).
new_cos=1.000, acc_after=1.000, write_t=0.001s. Perfect one-shot addition.

## Production config
N=1024, M_INIT=100, K_NEW=10, SEEDS=[7,17,23,31,41]

## Timeout estimate
~3s
