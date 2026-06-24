# Shotgun Smoke: Compose-Function Discriminator
Date: 2026-06-23
Script: experiments/shotgun_smoke_compose_function_discriminator_v1.py
Data: D:/AI/hd-instrument/data/shotgun_smoke_compose_function_discriminator_v1/metrics.json
Wall: 8.7s (N_DIM=256, N_TRAIN=1000, SEEDS=[42,137,999], VOCAB=256, pure numpy)

## Per-arm results (ranked by BPC -- lower = more informative)

| ARM                       | BPC mean | delta vs control | gate_mean | gate_std | VERDICT   |
|---------------------------|----------|------------------|-----------|----------|-----------|
| ARM_CONTROL_NO_MOD        | 7.0494   | 0.000 (baseline) | 1.000     | 0.000    | BASELINE  |
| ARM_SIGMOID_ADDITIVE      | 7.0540   | +0.005 bits      | 0.805     | 0.077    | LIVE (tie)|
| ARM_MAX_POOL              | 7.0819   | +0.033 bits      | 0.748     | 0.194    | LIVE (tie)|
| ARM_MULTIPLICATIVE_FLOOR10| 7.2420   | +0.193 bits      | 0.163     | 0.121    | DEGRADED  |
| ARM_MULTIPLICATIVE_FLOOR01| 7.4106   | +0.362 bits      | 0.124     | 0.145    | DEGRADED  |
| ARM_LOG_ADDITIVE          | 7.4162   | +0.367 bits      | 0.123     | 0.146    | DEGRADED  |
| ARM_MULTIPLICATIVE        | 7.4162   | +0.367 bits      | 0.123     | 0.146    | DEGRADED  |

Unigram BPC for reference: ~7.795 (delta vs unigram shown in run output; all arms beat unigram).
degenerate-collapse flag (bit-exact unigram): 0/7 arms -- none collapsed completely.

## HARD_INFO interpretation: which compose forms are LIVE vs DEAD

### The core finding: DEGRADED != DEAD, but multiplicative IS harmful

"Dead" was defined as bit-exact unigram collapse. None collapsed by that definition.
The real discriminator is **BPC vs the no-modulator control**. Here the picture is sharp:

**LIVE (within noise of control):**
- ARM_SIGMOID_ADDITIVE: +0.005 bits vs control -- statistically indistinguishable. Brain-canonical form.
- ARM_MAX_POOL: +0.033 bits vs control -- small degradation; still near-parity with pure Hebbian.

**DEGRADED (multiplicative starves the weight matrix):**
- ARM_MULTIPLICATIVE: +0.367 bits vs control -- 3-way product of U[0,1] has E[gate] = 0.5^3 = 0.125.
  The gate is withholding 87.5% of write signal systematically. W accumulates too slowly to dominate
  the readout. This IS the "collapse" pattern from the 3-axis cell -- not bit-exact unigram but
  severe information loss from learning-rate starvation.
- ARM_LOG_ADDITIVE: identical to ARM_MULTIPLICATIVE (BPC=7.4162, gate_mean=0.123). Mathematically
  expected: exp(sum(log(x_i))) = product(x_i). Log transform does NOT fix the near-zero collapse.
  It is algebraically equivalent. Confirmed.
- ARM_MULTIPLICATIVE_FLOOR01: floor=0.01 rescues only 1.4% of the spread (gate_mean rises to 0.124).
  Effectively unchanged.
- ARM_MULTIPLICATIVE_FLOOR10: floor=0.10 gives gate_mean=0.163. Rescues partial signal (+40% vs
  no-floor). Still 0.193 bits WORSE than control -- floor helps but does not eliminate the deficit.

### Mechanistic root cause (now empirically confirmed)

Multiplicative gate with U[0,1] modulators: E[gate] = E[dopa] * E[ACh] * E[sero] = 0.5^3 = 0.125.
The weight matrix W grows 8x slower than pure Hebbian control. At N_TRAIN=1000 steps this is severe.
At production N_TRAIN=100k it MAY self-correct (W eventually accumulates if training is long enough),
BUT the early-phase signal is starved -- startup dynamics are bad.

Sigmoid-additive maps [0,1]^3 inputs to gate in [sigmoid(0), sigmoid(3)] = [0.50, 0.95].
Gate mean = 0.805. W accumulates at ~80% of pure Hebbian -- near-parity explains the near-zero delta.

Max-pool maps [0,1]^3 to [0,1] with E[max of 3 U[0,1]] = 3/4 = 0.75. Gate mean = 0.748. Confirmed.
Both sigmoid-add and max-pool keep gate_mean high by design.

## Floor-rescue finding

Floor=0.10 partially rescues (gate_mean 0.123 -> 0.163, BPC gap 0.367 -> 0.193 bits vs control).
Floor=0.01 is too small (gate_mean barely moves to 0.124). A floor of ~0.50 (half the pure-Hebbian
write rate) would likely close most of the gap. This is the "missing detail" hypothesis: multiplicative
IS viable IF a sufficiently high floor is enforced. UNTESTED at this scale.

## Implication for in-flight 2x2 factorial cell

The in-flight 2x2 factorial cell (ARM_MULTIPLICATIVE x ARM_SIGMOID_ADDITIVE) will correctly show
sigmoid-additive winning at this smoke scale. The result is robust: +0.37 bits BPC gap is large and
consistent across 3 seeds (std in BPC ~0.002 -- very stable).

Key nuance: the 2x2 factorial is testing multiplicative vs sigmoid at PRODUCTION N (larger N_DIM,
larger N_TRAIN). At production scale the multiplicative deficit may DECREASE (W converges more) or
INCREASE (encoder space is richer so gate starvation matters more). Smoke at N=256/N_TRAIN=1000
is NOT production scale. See WHAT_THIS_DOES_NOT_SHOW below.

### Recommendation for the factorial cell

Pre-register: sigmoid_additive expected to WIN (supported by this smoke at d > 5 sigma).
Pre-register: floor investigation as a SECONDARY question (does floor=0.5 close the gap?).
Do NOT pre-reg multiplicative as "viable with floor" without running floor=0.5 arm.

## ARM_LOG_ADDITIVE = ARM_MULTIPLICATIVE (confirmed algebraically + empirically)

exp(log(a)+log(b)+log(c)) = a*b*c. Both give BPC=7.4162 and gate_mean=0.123.
The log transform has zero mechanistic benefit -- it is the same operation.
DEAD as a distinct arm; drop from future cells.

## WHAT_THIS_DOES_NOT_SHOW

- Does NOT measure compose-function at production N (N_DIM=8192, N_TRAIN=100k). Startup-dynamics
  finding at N_TRAIN=1000 may differ at 100x more training. Gate starvation may self-correct.
- Does NOT test compose-ORDER interaction (e.g., sigmoid before vs after nonlinearity in encoder).
- Does NOT test learned modulator weights (ALPHA, BETA, GAMMA fixed to 1.0 here; sigmoid-add
  with learned weights may be substantially better than gate=1.0 control).
- Does NOT test floor values between 0.10 and 1.0 (only 0.01 and 0.10 tested).
- Does NOT test any compose function at multi-step (sequential context, not just bigrams).
- Smoke-only: this is small N, small vocab, random modulators -- not a substrate production run.
- The "equivalence" of sigmoid-add to control (gate=1.0) here means sigmoid-add does NOT HURT,
  not that it provides positive value. In learned-modulator settings it may discriminate strongly.
