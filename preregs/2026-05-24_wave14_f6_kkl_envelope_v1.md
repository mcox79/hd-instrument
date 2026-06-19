# Prereg: wave14_f6_kkl_envelope_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: F-6 KKL Boolean envelope expansion (broader density + N stress)
**Trigger**: v195 KKL_HARD_PASS_LOW_INFLUENCE at density=0.10, N=256; F-6 row 🔬 -> 🟡 candidate; envelope expansion is the validation gate per [[feedback-envelope-expansion-fail-bands]].

## Hypothesis

Substrate boundaries are low-influence/well-distributed (KKL-class) not just at
the tested operating point (density=0.10, N=256) but across a BROADER envelope
(densities {0.10, 0.30, 0.50, 0.70} x N {64, 256, 1024} = 12 cells).

## Design (exp_dev autonomy)

- N values: {64, 256, 1024}
- Density (M_stored/N): {0.10, 0.30, 0.50, 0.70}
- n_samples per coordinate: 500
- Seeds: {7, 17, 23, 31, 41}
- Queue: local_cpu_queue (pure numpy, N<=1024, <60s)
- ETA: ~45 sec local CPU

## Pre-registered falsifier bands (broader claim, envelope-expansion drill)

The BROADER claim is: substrate boundaries are low-influence/well-distributed
ACROSS the operating envelope (density in {0.10..0.70}, N in {64..1024}).

- **HARD-PASS**: max_inf_share <= 0.30 AND kkl_ratio >= 1.0 at ALL 12 operating points.
  -> F-6 row promoted 🟡 -> 🟢.
- **HARD-FAIL**: max_inf_share >= 0.60 at >=2 cells (substrate behaves junta-like under stress).
  -> F-6 row reverts 🟡 -> 🔬 (envelope-dependent only).
- **MIDDLE-BAND**: any intermediate (1 cell fails PASS but <2 fail HARD-FAIL).
  -> F-6 🟡 STAYS; annotate density envelope narrowing.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

- (max_inf_share=0.05 all cells, kkl_ratio=1.1 all) -> F6_ENVELOPE_HARD_PASS
- (max_inf_share=0.65 at 2 cells) -> F6_ENVELOPE_HARD_FAIL
- (max_inf_share=0.65 at 1 cell, 0.05 elsewhere) -> F6_ENVELOPE_MIDDLE_BAND
- (cells=[]) -> F6_ENVELOPE_INCONCLUSIVE
All 4/4 self-test cases pass.

## Smoke outcome (N in {64, 256}, densities {0.10, 0.30}, 1 seed)

F6_ENVELOPE_HARD_PASS: all 4 cells pass (share={0.048, 0.086, 0.018, 0.041}, kkl={1.29, 1.10, 2.24, 1.78}). Smoke clears; ship FULL.

## Queue entry

`queue=local_cpu_queue name=wave14_f6_kkl_envelope_v1 script=experiments/exp_wave14_f6_kkl_envelope_v1.py prereg=preregs/2026-05-24_wave14_f6_kkl_envelope_v1.md timeout=300`
