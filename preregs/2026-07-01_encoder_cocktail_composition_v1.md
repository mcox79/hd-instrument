# Pre-registration: encoder_cocktail_composition_v1

**Date:** 2026-07-01
**Anchor:** encoder_cocktail_composition_v1
**Queue:** remote_cpu_queue
**N:** 8192, **Seeds:** 7, 13, 19, **M items bound per bundle:** 1024

## Scientific question

Currently 5 encoders (fhrr / hrr_real / binary_bipolar / sparse_bipolar /
sparse_real) are cert-graded individually. What happens when they are
MIXED in the same substrate bundle? Does mixing compose cleanly (mixed
bundle recall stays near single-encoder baseline), or does mixing break
the mechanism (uniform encoding is an architectural constraint)?

Also: can a query encoded in encoder family X retrieve a value stored
under encoder family Y (cross-encoder interop)?

## Cocktail mechanism

Each family produces distinct shape/dtype (FHRR: complex64 dim/2; sparse:
float32 dim; binary: float32 dim). Common bundle domain = real float32
N_DIM via family-specific real-projection at bind-output:

- FHRR complex[N/2] -> concat([Re, Im]) -> real[N]
- sparse_bipolar float32[N] -> identity
- binary_bipolar float32[N] -> identity

Bind is family-native (self-inverse elementwise mul for bipolar; complex
mul for FHRR). Bundle = sum of real-projected bound vectors, L2 normalize.

Query for item i: family_i-native bind(key_i, val_j) for each candidate
j; real-project; cosine against bundle; top-1 argmax = predicted j.
Recall = fraction where argmax_j == i.

## Six arms (pairwise + baseline)

- ARM_FHRR_ONLY: baseline; single-family bundle (reproduces prior CG).
- ARM_FHRR_PLUS_SPARSE: 50/50 FHRR + sparse_bipolar items in same bundle.
- ARM_FHRR_PLUS_BINARY: 50/50 FHRR + binary_bipolar.
- ARM_SPARSE_PLUS_BINARY: 50/50 sparse + binary; no FHRR.
- ARM_ALL_THREE_MIXED: 33/33/33 mix of all three families.
- ARM_FHRR_QUERY_SPARSE_KEYS: keys+values built as sparse_bipolar;
  query bank built as FHRR at the SAME item index; probe uses FHRR bind
  against real-projected bundle. Structural cross-family retrieval probe.

## Pre-registered bands

**HARD-PASS:**
- HP_MIX_COMPOSES: min(mix_arm_recall / baseline_recall) >= 0.85 across
  the 4 mixed arms AND across all 3 seeds (mix loses at most 15%).
- HP_CROSS_ENCODER_QUERY: ARM_FHRR_QUERY_SPARSE_KEYS recall >= 0.50
  across all 3 seeds (partial recall demonstrates structural interop).

**MIDDLE:** mix_ratio_min in [0.30/baseline, 0.85) AND cross_recall in
[0.10, 0.50). Partial signal on either dimension; not decisive.

**HARD-FAIL:**
- HF_MIX_CRUMBLES: any mixed-encoder arm set_recall < 0.30 on any seed
  (mix breaks mechanism).
- HF_CROSS_ENCODER_ZERO: ARM_FHRR_QUERY_SPARSE_KEYS recall < 0.10 on
  any seed (encoders don't interoperate).

**CHAIN_GRADE gate:** HP_MIX_COMPOSES fires cross-seed (3/3 seeds pass);
promotes to CG_ENCODER_COCKTAIL_COMPOSES.

## Calibration rationale

- 0.85 mix-vs-baseline threshold: allows a real 15% compositional cost of
  mixing (interference from cross-family bundle noise floors) while still
  claiming clean composition. Reflects prior ANCHOR 4 v4 finding that
  single-family baselines at N=8192 M=1024 typically recall > 0.90; a
  mixed arm at 0.85 * 0.90 = 0.765 is still well above chance.
- 0.50 cross-encoder query threshold: below single-family baseline (~0.90)
  but well above the chance rate (1/M = 1/1024 ~= 0.001). A 0.50 crossover
  means the FHRR-encoded query actually finds structural signal in the
  sparse-encoded substrate, demonstrating real geometric interop rather
  than perfect same-family retrieval.
- 0.30 mix-crumble floor: any arm below this suggests the mix has
  destroyed the discriminative signal (would be catastrophic).
- 0.10 cross-encoder zero floor: below this the FHRR query is essentially
  guessing against a sparse substrate; encoders live in disjoint
  geometries.

## N-suffix section

No N-suffix in anchor name (N=8192 is default; PROT-018 exemption applies
because N is a scalar constant in core, not swept).

## Cardinality (CARDINALITY_OK; META_RULE_H)

EXPECTED_N_UNITS = 6 arms per seed. cross-seed = 18 units total.
HARD_FAIL if cardinality_observed != cardinality_expected on any seed.

## Discriminator-must-survive-scale check (USER 2026-06-26)

Smoke runs at FULL-N (N=8192) with M=512 items (half of full M=1024) and
N_QUERY=128. This means the baseline arm sees the SAME encoder geometry
at smoke as at full (only bundle load M and query count differ). If
mixing composes at smoke, we have a real prediction for full: mix_ratio
should stay >= 0.85 because the mechanism is bundle-interference-limited
not scale-limited. If baseline saturates at smoke to 1.000 we ALREADY
know the mechanism cannot discriminate at smaller M; we then either
(a) increase M or (b) reduce dim per META_RULE_S regime check.

Expected discriminator behavior at smoke:
- ARM_FHRR_ONLY: recall ~0.90 (M=512 at N=8192 for FHRR is well below
  the 1024-item saturation bound; discriminator active).
- Mix arms: TBD; that's the science.
- ARM_FHRR_QUERY_SPARSE_KEYS: TBD; this is the interop test.

If ARM_FHRR_ONLY saturates at 1.000 at smoke, smoke is inconclusive
regarding compositional cost -- rebalance regime before full dispatch.

## Cross-references

- experiments/_substrate_anchor4_encoder_family_phase_diagram_v4_core.py
  (5 encoders individually verified; encoder registry + preflight pattern)
- experiments/exp_hub_spoke_cross_encoder_alignment_smoke_v1.py
  (SAME-family alignment, not heterogeneous HDC families -- the negative
  space this cell fills)
- experiments/exp_substrate_compose_heterogeneous_routing_v1.py
  (heterogeneous plasticity routing; single encoder family per arm --
  distinct axis from this cell)
- data/exp_*/metrics.json for ANCHOR 4 v4 baseline recall reference.

## Substantive if:

- MIX composes (HP fires): substrate supports heterogeneous encoders in
  same instance -> M3 architectural flexibility for multi-modal / multi-
  algorithm cortex plumbing.
- MIX breaks (HF fires): uniform encoding is an architectural constraint
  and the cortex layer must route items to per-family substrate silos.
