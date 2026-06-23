# Pre-registration: lock_in_position_encoding_smoke_v1

**Date:** 2026-06-23
**Anchor:** lock_in_position_encoding_smoke_v1
**Queue:** local_cpu_queue (smoke; CPU; numpy-only; ~10min wall)
**N:** N_DIM=4096; **Seeds:** [7, 17, 23]; **L:** 5 (sequence length); **V:** 200 (vocab); **n_sequences:** 100
**k_signal:** 31 (inherited from validated lock-in amplifier parent)

## Scientific question

Can the lock-in amplifier's permutation-as-frequency operator serve as the substrate's
native position encoding for sequence modeling? USER intuition 2026-06-23: "vectors have
concepts attached, the combination of words will have their own combined vector meaning,
particularly if each word has a weight, and the order of the words carries another
weight" — recognized by USER as the HRR/Plate-1995 structure where bundle = vector add,
bind = element-wise product, permute = cyclic shift. Lock-in amp's roll(v, k*2pi/P) is
structurally identical to a position encoding operator with k as position index. THIS
cell tests whether phase-locked position encoding beats traditional position-tag binding
(the encoding used in CA3 smoke that failed).

## Key reframe (substrate-native sequence encoding)

Traditional sequence encoding (CA3 smoke `exp_ca3_sequence_prediction_lm_smoke_v1.py`
build_position_carriers + `bind(prev_token, position_carrier)`) used a SEPARATE random
position hypervector P_i bound multiplicatively to each token. This scrambles signal:
each position-tag is a fresh random vector adding M*N independent error terms before the
demodulation step. CA3 smoke landed HARD_FAIL on this mechanism.

THIS cell encodes position as PHASE in the lock-in amplifier framework:

    sequence_vec = sum_i roll(v_token_i, i * k_signal)

then decodes via demodulation at the matching phase:

    candidate_at_p = roll(sequence_vec, -p * k_signal); argmax over codebook

The position operator is structured (cyclic permutation) rather than random; decoding is
a phase-coherent demodulation, not a binding-inverse over a random tag.

## Arms (4)

1. **ARM_BUNDLE_NO_ORDER** — `sum_i v_token_i` (no position info; control floor).
2. **ARM_BIND_POSITION_TAG** — `sum_i v_token_i * P_i` where P_i is a random bipolar
   tag (element-wise bind); the CA3-smoke encoding; expected to fail at L=5 due to
   interference cross-terms.
3. **ARM_PHASE_ROLL** — `sum_i roll(v_token_i, i * k_signal)`; substrate-native lock-in
   position encoding with phase=i*k_signal for position i.
4. **ARM_PHASE_ROLL_WEIGHTED** — `sum_i w_i * roll(v_token_i, i * k_signal) * cos(2*pi*i/L)`
   (USER intuition: weighted + cosine-phase per position; tests if the "weight per word +
   weight per order" framing improves recovery via transmit-side carrier; w_i=1 in smoke).

## Per-arm measurements

For each test sequence (100 total per seed), decode token at each position p in [0..L-1]
via the arm-appropriate decode rule; report **recall@1 per position** and **mean
sequence accuracy** (mean over positions, mean over sequences, mean over seeds).

## Pre-registered bands

**HARD-PASS** (substrate-native position encoding is a new sequence-modeling primitive;
chain-grade-eligible per parent lock-in amplifier atom):

  - ARM_PHASE_ROLL position-recall@1 mean over 5 positions **>= 0.80** across 3 seeds
  - AND ARM_PHASE_ROLL **>= ARM_BIND_POSITION_TAG + 0.20** (must beat traditional
    sequence binding by 20 percentage points absolute).

**HARD-FAIL** (no advantage; mechanism dead):

  - ARM_PHASE_ROLL **<= ARM_BIND_POSITION_TAG + 0.05** (no advantage over traditional
    binding within noise).

**MIDDLE_BAND**: lift in (0.05, 0.20).

## Sanity self-tests (run at module import)

1. **L=1 endpoint**: at sequence length 1, ALL arms recover the single token with
   recall=1.0 (single-token codebook nearest-neighbor is trivial; no encoding can
   degrade this).
2. **L=N_DIM degenerate**: at L=N_DIM (extreme overload), all arms degrade toward
   chance 1/V. (Not part of main sweep — sanity that bands are not saturated.)
3. **Roll involution**: roll(roll(v, k), -k) == v exactly.
4. **Bind self-test**: random bipolar v * v == ones_like(v); unbind by multiplication
   with the same tag is exact.

## Implementation notes

- numpy-only; ASCII-only. PROT-018 N/A (no _n suffix; N_DIM=4096 is configured but the
  anchor name carries no _n binding).
- Bipolar codebook (substrate convention {-1, +1}^N) for the vocabulary (V=200
  codewords).
- Position-tag P_i for ARM_BIND_POSITION_TAG drawn fresh-per-seed from same bipolar
  distribution; stored once per seed (consistent across all sequences in that seed).
- Decoding: for each arm, the position-p decode rule is the arm's modulation inverse
  applied to sequence_vec, followed by argmax over the V-row codebook. Concretely:
  - ARM_BUNDLE_NO_ORDER: decode_p = sequence_vec (same for all p; cannot disambiguate
    position; expected near 1/L for any position other than the bag-of-words majority).
  - ARM_BIND_POSITION_TAG: decode_p = sequence_vec * P_p (unbind by multiplication
    with the tag for position p).
  - ARM_PHASE_ROLL: decode_p = roll(sequence_vec, -p * k_signal).
  - ARM_PHASE_ROLL_WEIGHTED: decode_p = roll(sequence_vec, -p * k_signal) * cos(2*pi*p/L)
    (the cosine carrier inversion).

## Timeout estimate

Smoke wall budget: at N_DIM=4096, V=200, L=5, 100 sequences x 5 positions x 4 arms x 3
seeds = 6000 decodes; each decode is one np.roll + one (V, N) matmul. Estimated wall
~5-10 min. timeout_s = 900 (15 min safety; smoke gate enforces 180s --smoke and 3600s
HDLAB_SMOKE_TIMEOUT ceiling so the FULL run gets a 900s entry budget on
local_cpu_queue).

## N-suffix section

No _n suffix in anchor name (PROT-018 N/A). N_DIM=4096 hard-coded.

## Compose-with

Parent atom: lock_in_amplifier_hd_frequency_smoke_v1 (chain-grade candidate). Sister
falsifier: ca3_sequence_prediction_lm_smoke_v1 (HARD_FAIL on bind-position-tag at smoke
scale). Substrate primitives consumed: roll (cyclic permutation), bundle (vector sum),
bind (element-wise product) - Plate-1995 HRR triad.

## Pre-dispatch probe finding (2026-06-23 exp_dev)

A pre-dispatch noise-sweep probe (N_DIM=512, V=200, L=5, sigma in [0..32]) showed
ARM_PHASE_ROLL and ARM_BIND_POSITION_TAG recover within +-0.02pp at every sigma
in the range tested. Both mechanisms are linear-orthogonal (cyclic permutation +
random bipolar tag both produce ~zero-correlated reference frames with identical
SNR characteristics).

The probe PREDICTS HARD_FAIL on the original pre-reg HP ("phase-roll beats
bind-position-tag by 20pp"). The cell is shipped UNCHANGED to honor pre-reg
sacredness (NEGATIVITY-BIAS rule: bands sacrosanct both ways; no retroactive
edits after seeing data). The probe finding is surfaced here for the
landed-VET to consider when ratifying the falsification.

USER intuition reframe (anticipated): the "vectors-with-weights" framing is
mathematically equivalent to HRR composition; both phase-roll and tag-bind are
valid HRR position encodings. The substrate-distinctive claim (phase-roll
exploits cyclic-shift structure that random tags can't) may require a
DIFFERENT discriminator regime than this cell's clean+noisy single-substrate
setup. Candidates: cross-cell transfer (phase-roll structure surviving binding
to NEW context vectors), compositional position arithmetic (P_3 + P_2 = P_5
via shift composition), or capacity-at-fixed-N. None of those are this cell's
question, which is why the answer is structural-equivalence-within-noise.
