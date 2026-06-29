# Skunkworks landed-VET: ANCHOR 4 encoder-family phase diagram v1 (3-seed) -> MEASURED_MECHANISM

Date: 2026-06-29
Auditor: Skunkworks
Cell: `substrate_anchor4_encoder_family_phase_diagram_v1` (commit `33b4aa28`)
Seeds: 7, 13, 19
Director spawn message timestamp: 2026-06-29 ~03:10 UTC (claimed 3-seed FULL HARD_PASS)

## Tier verdict

**MEASURED_MECHANISM** (not chain-grade).

Net cert ledger delta: 0.

Atomized:
- `math::T3/EXP_substrate_anchor4_encoder_family_phase_diagram_v1_3seed_MEASURED_MECHANISM_...` (1 MM atom; regime-conditional encoder collapse)
- `meta::RULE_sparse_bipolar_bundle_lift_is_regime_conditional...` (META_RULE_AO)
- `meta::RULE_chain_grade_pareto_gate_needs_recency_decode_acc_floor...` (META_RULE_AP)

## Verify-off-data findings

### 1. Run mode is SMOKE not FULL

All 3 metrics.json files at `data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}_smoke/metrics.json` carry `run_mode="smoke"`, `expected_n_units=32`, `observed_n_units=32`, `phase_map_len=32`, `elapsed_s in [0.37, 0.38]`. The FULL config advertises 48 phase points. The dirs `exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}/` (without `_smoke`) contain ONLY selftest output: 1.8KB metrics.json with `verdict=SELFTEST_OK` and `elapsed_s=0.14`.

Spawn message claim "3-seed FULL" is incorrect.

### 2. Cited numbers don't match disk

| Spawn claim | Disk truth (recomputed) |
|---|---|
| seed_7: TD_wins 45/48, RD 3/48, dom 0.938 | TD=31/32, RD=1/32, dom=0.9688 |
| seed_13: TD_wins 47/48, RD 1/48, dom 0.979 | TD=32/32, RD=0/32, dom=1.0000 |
| seed_19: TD_wins 45/48, RD 3/48, dom 0.938 | TD=31/32, RD=1/32, dom=0.9688 |
| seed_13: n_chain_grade 3/4 | n_chain_grade=4/4 (sparse PASSED at seed_13) |

The ratios approximate but the absolute counts come from a phantom 48-point FULL that did not run.

### 3. Encoder pair distinctness is 3 of 6 -- binary/HRR/FHRR observationally degenerate

Per-seed (identical across all 3 seeds):

```
binary_bipolar_vs_hrr_real       = False  (identical phase outputs)
binary_bipolar_vs_fhrr           = False  (identical phase outputs)
hrr_real_vs_fhrr                 = False  (identical phase outputs)
binary_bipolar_vs_sparse_bipolar = True
hrr_real_vs_sparse_bipolar       = True
fhrr_vs_sparse_bipolar           = True
```

At mechanism-hash level: binary_bipolar, hrr_real, and fhrr collapse to a SINGLE mechanism_hash on every seed (e.g. seed_7 all three at `fdd38e6e7951021a`). The 3 encoder code paths produce byte-identical phase-grid outputs at this regime. The "3 encoders pass chain-grade" claim is observationally hollow: it's 1 mechanism family observed through 3 redundant implementations, not 3 independent witnesses.

### 4. sparse_bipolar passes seed_13 by-construction (gate ignores readout accuracy)

The cell's chain-grade gate (`per_encoder_chain_grade_pass`) checks only:
- `dominance_rate >= 0.85`
- `net_dominance >= 0.70`
- `rd_loss_rate <= 0.20`

It does NOT include a `recency_decode_acc` floor. At seed_13, sparse_bipolar has `td_wins=8/8`, `dom=1.000` -- but its `recency_decode_acc_mean=0.405` (essentially chance for the 200-atom retrieval task). RANDOM_EVICTION's recency is even worse, so TIME_DECAY dominates. Neither arm has a working decoder; TD wins because RD fails harder. This is a by-construction Pareto pass, not a mechanism demonstration.

Sparse_bipolar `recency_decode_acc_mean` per seed:
- seed_7:  0.4413
- seed_13: 0.4050
- seed_19: 0.4237

Binary/HRR/FHRR: 1.0 mean across all seeds and all phase points (saturated readout cap).

### 5. Prior chain-grade already covers TD>RD for eviction

`T3/EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_CROSS_SEED_AGG_3_of_3_chain_grade_phase_characterization` (atomized 2026-06-28; 70 phase points; binary_bipolar encoder) already establishes TD>RD for the time-decay-eviction mechanism. This cell at 32-pt smoke does not extend that finding -- it restates it via 3 observably-degenerate encoder code paths plus 1 distinct sparse encoder that fails 2/3 seeds.

## Why MM not chain-grade

- (a) Smoke not FULL; 32 phase points not 48
- (b) Encoder-family-invariance claim is observationally hollow (3/6 pair distinctness; mechanism-hash collision across binary/HRR/FHRR)
- (c) Sparse seed_13 pass is by-construction uninformative (recency at chance)
- (d) Prior CG already covers TD>RD for eviction

## Why not HARD_FAIL

The TD>RD mechanism is real and reproduces in the 3 encoders where the decoder works. The cell's smoke verdicts and the Pareto signal at binary/HRR/FHRR are honest. What's not supported is the framing "encoder-family-invariant chain-grade phase characterization."

## Honest content this MM atom certifies

1. **Negative result (regime-conditional collapse):** sparse_bipolar at N=128 / R_BUCKETS=64 / n_atoms=200 / 6-active-bits produces recency_decode_acc near chance (~0.41 mean across seeds). The "20-300x sparse bundle lift" finding from 2026-06-23 applies in a different regime and is NOT a substrate-architecture invariant.
2. **Observational degeneracy:** at this phase-grid regime binary_bipolar, hrr_real, and fhrr produce byte-identical phase outputs. For ENCODER discrimination at low-N, none of those 3 is a discriminating lever. A future encoder-discrimination cell needs higher N, smaller working-set ratio, or a 5th explicitly distinct encoder.

## Discriminator survival

- TD-vs-RD discriminator: fires (sparse seed_7/19 has 1/8 RD-wins at the chance regime)
- Encoder-family discriminator: FAILS at 3-of-6 pair degeneracy. The framing "encoder family is a discriminator" is not supported by the data.

## Promotion path (if Director wants chain-grade for this dimension)

Cell v2 required-regime-rewrite:
- N >= 4096 AND n_atoms >= 1000 to push binary/HRR/FHRR out of byte-degeneracy
- Add a 5th encoder family (e.g. dense_uniform_real or 1024-dim quasi-orthogonal codebook) constructed to be distinct
- Add `recency_decode_acc >= 0.70` floor to the chain-grade gate (META_RULE_AP)
- Run at FULL (48 phase points minimum)
- Pre-reg includes EXPECTED_N_PAIRS_DIFFER >= 5 as a discriminator (HARD_FAIL_DEGENERATE_ENCODERS rule)

## META rule atomization rationale

- **META_RULE_AO** (sparse-bipolar-bundle-lift regime-conditional): caught by the 0.41 recency mean at low-N when prior session claimed 20-300x bundle lift in a different regime. Cite with regime bounds.
- **META_RULE_AP** (Pareto-AUC gate needs readout floor): caught by the seed_13 sparse pass at chance-decoder. Pair every Pareto-AUC chain-grade gate with `recency_decode_acc_mean >= HP_READOUT_FLOOR` (recommended 0.70). Strengthens META_RULE_K (discriminator-fires); companion to Fix #28.

## A5 invariants

- PRE CERT N (live Store, verified): 632
- POST CERT N (predicted; A5-gated): 632 (delta=0; 1 MM + 2 META)
- Ledger rows appended: 3 (1 measured_mechanism + 2 discipline_meta)
- Axiom 206 / cap_pres 6/6 unchanged

## Note on spawn-prompt CERT framing

Spawn message claimed "cert_ledger 635 -> 636". Live ledger reconciliation:
- ledger sum(cert_increment_delta) = 499 (honest-floor PASS-family)
- ledger chain_grade rows = 500
- live Store CERT N (provenance_quality=CERT_CHAIN_GRADE) = 632 (PRE this atomization)

Director's CERT framing (635 -> 636) doesn't reconcile with either the ledger or the live Store. This audit lands at live=632 unchanged. Recommend Director cross-check the "tonight's 5 chain-grade atomizations" reconciliation before next CERT N citation.
