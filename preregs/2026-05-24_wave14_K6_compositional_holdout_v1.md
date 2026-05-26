# Prereg: wave14_K6_compositional_holdout_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: K6 compositional generalization — hierarchical pre-binding axis 2
**Source**: cap_map v190 K6 4-axis rehab list; v193 hand-off optional anchor 9

## Per [[feedback-rehabilitation-after-rejection]]

K6 dim-scaling axis 1 exhausted; axes 2/3/4 elevated. Axis 2 = hierarchical pre-binding (this anchor).

## Hypothesis

If substrate stores hierarchically pre-bound compositions c_k = a_i ⊗ a_j (Hadamard product), then held-out UNSEEN compositions should retrieve via the compositional structure of seen atoms. Without pre-binding (random independent codes per composition), held-out should fail.

## Design

- N=4096 substrate width
- p=40 atomic concepts
- 200 seen compositions stored; 100 held-out tested
- Compositional structure: c_k = a_i ⊗ a_j (Hadamard product of atoms — canonical BSC binding op)
- Treatment: Hebbian outer-product W from seen (key, val=composition) pairs
- Control: same with random independent vals (no structure)
- 5 seeds: [7, 17, 23, 31, 41]

## Falsifier bands (pre-registered)

- **HARD-PASS — K6 🔬 -> 🟢 compositional generalization supported**: held-out cosine >= 0.50 AND (seen - held) gap <= 0.15.
- **HARD-FAIL — K6 axis 2 REJECTED**: held-out cosine <= 0.10 (chance) OR gap >= 0.40.
- **MIDDLE**: any intermediate; report bands.

## Smoke result (N=512, p=10, M_seen=30, M_held=20, 1 seed)

`K6_HARD_FAIL_NO_GENERALIZATION` at smoke (cos_held=-0.001, gap=0.555). Smoke result is consistent with no compositional generalization at small N — but FULL N=4096 with p=40 atoms gives the substrate room for atom-overlap-driven recall; this is the actual hypothesis test.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=overnight_queue name=wave14_K6_compositional_holdout_v1 script=experiments/exp_wave14_K6_compositional_holdout_v1.py prereg=preregs/2026-05-24_wave14_K6_compositional_holdout_v1.md timeout=3600`
