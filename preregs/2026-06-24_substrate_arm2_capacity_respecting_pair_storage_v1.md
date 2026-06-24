# Prereg: substrate_arm2_capacity_respecting_pair_storage_v1

Date: 2026-06-24
Author: exp_dev (compositional drill handoff ANCHOR 1)
Routing: local_cpu_queue (wall <= 5min per handoff)

## Strategic rationale

Shotgun ARM 2 (compositional generalization) at M=200 train pairs / D=8192 with
sparse-bipolar f=0.05 produced **in_distribution top-1 = 0.10 (chance)** and bank
L2 grew unbounded -- a SATURATION failure, not an HRR primitive failure.

The canonical regime for HRR pair storage is M ~= vocab_size (1-to-1 binding),
NOT M >> vocab_size (super-saturated bank). This cell establishes the BASELINE
for HRR primitive aliveness at the capacity-respecting regime.

Per compositional drill handoff 2026-06-24 [ANCHOR 1 highest priority].

## Configuration

- N_DIM = 8192 (substrate canonical dim)
- SPARSE_F = 0.05 (sparse-bipolar fraction)
- n_subj = 20, n_obj = 20 (vocab sizes)
- M = 20 train pairs, **1-to-1 mapping** via random permutation pi:
    train_pairs = [(i, pi(i)) for i in range(20)]
- Bank = sum_{(i,j) in train} bind(A_i, B_j)
- 3 seeds for CV
- Metric: in_distribution top-1 recovery (for each train (i, pi(i)),
  unbind(bank, A_i) -> argmax cosine over B_book; check == pi(i))

## Pre-reg HARD bands (sacrosanct, both directions)

- **HARD_PASS**: in_dist top-1 >= 0.95
  -- HRR primitive ALIVE at canonical capacity. Confirms shotgun ARM 2 failure
     was super-saturation (M=200 > capacity at D=8192), not primitive collapse.

- **HARD_FAIL**: in_dist top-1 < 0.80
  -- HRR primitive BROKEN even at canonical capacity-respecting regime.
     Substrate-product implication: HRR cannot serve as pair-store primitive;
     need alternative composition mechanism (Lock-in chain, sparse-bipolar
     direct outer-product, etc.).

- **MIDDLE_BAND**: 0.80 <= in_dist top-1 < 0.95
  -- Partial aliveness; HRR works but with measurable crosstalk at M=vocab.
     Characterize ratio + escalate to capacity sweep.

## By-construction-saturation rule (per handoff)

If in_dist == 1.000 (exact) AND CV < 0.001 across seeds:
- Tier as **DIAGNOSTIC_PASS** (not chain-grade)
- Reason: M=20 << HRR capacity at D=8192 with sparse-bipolar f=0.05; perfect
  recovery is BY CONSTRUCTION (~M*f^2/D crosstalk ~= 20*0.0025/8192 ~= 6e-6,
  far below 1/n_obj = 0.05 discrimination floor).
- Per Skunkworks tiering discipline (Fix #28 + by-construction-saturation atom):
  let cert-classification come from cert-owner not from cell-author framing.

## Selftest gate (formula-selftests)

At D=512, M=5, 1-to-1 mapping:
- Expect in_dist == 1.000 (M=5 deeply below crosstalk floor at D=512)
- Crosstalk estimate: 5 * 0.05^2 / 512 = 2.4e-5 << 1/5 = 0.20

Cell must `--self-test` exit 0 with selftest measurement matching expected.

## Cell-level verdict mapping

- in_dist >= 0.95 AND CV >= 0.001 -> HARD_PASS (in band, measurable variance)
- in_dist == 1.000 AND CV < 0.001 -> DIAGNOSTIC_PASS (by-construction)
- 0.80 <= in_dist < 0.95 -> MIDDLE_BAND
- in_dist < 0.80 -> HARD_FAIL

## What this does NOT show

- Holdout / compositional generalization (THIS cell only tests in-distribution
  storage; holdout to follow if HARD_PASS / DIAGNOSTIC_PASS)
- Learning, plasticity, gradient updates (pure substrate primitives)
- Chain-grade integration with substrate KG
- Capacity ceiling (M=20 is the canonical lower bound; capacity sweep is
  follow-up cell)

## Cites

- compositional_drill_handoff_ANCHOR_1_USER_2026-06-24
- exp_substrate_brain_aligned_aliveness_shotgun_v1 (ARM 2 super-saturation failure)
- by-construction-saturation tiering atom (Skunkworks 2026-06-22)
- HRR involutive intuition (operational findings 2026-06-23)
- sparse-bipolar 20-300x bundle lift (operational findings 2026-06-23)
