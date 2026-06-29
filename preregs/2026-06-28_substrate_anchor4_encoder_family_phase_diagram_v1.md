# Pre-registration: substrate_anchor4_encoder_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive (Research 2026-06-28) — systematic phase-diagram
coverage across COMPONENTS. Encoder family is the most load-bearing lever;
prior encoder-family sweeps shipped 2026-06-28 for PC (pattern completion),
seqbind (sequence binding), and WM (multi-bank working memory K-cliff).
ANCHOR 4 (time-decay eviction) is the first 2x-research-drill chain-grade
win (Pareto-AUC v2 ratified per cert ledger).

## Anchor

`substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling
files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_anchor4_encoder_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct
  invocation, completed in ~0.2s per seed)
- **Full queue:** **remote_cpu_queue** (NumPy-only cell; no torch needed;
  total compute ~1s/seed × 3 seeds = 3s; well under any timeout)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes
  through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap)

ANCHOR 4 (time-decay eviction) v2 Pareto-AUC chain-grade evidence at the
HRR-default (no encoder layer; eviction reads atom attributes directly).
We don't know if the chain-grade result is encoder-family-invariant or
specific to the default. Per USER's systematic phase-diagram directive, the
encoder family is swept as the OUTER axis over the same Pareto-dominance
discriminator.

This is the FOURTH COMPONENT-SUBSTITUTION phase diagram (after PC + seqbind
+ WM). The pattern across the four:
1. PC encoder family v1 (2026-06-28): 4 encoders x inner grid
2. seqbind encoder family v1 (2026-06-28): 4 encoders x K-cliff grid
3. WM encoder family v1 (2026-06-28): 4 encoders x (K_per_bank x num_banks)
4. **ANCHOR 4 encoder family v1 (THIS CELL)**: 4 encoders x (decay x load x N_dim)

## Encoder families (OUTER axis)

Four families, each with same (`n_items`, `N_dim`) codebook footprint but
distinct representation:

| Family | Codebook elements | Bind op | Score | Unbind op |
|--------|-------------------|---------|-------|-----------|
| `binary_bipolar` | `{-1,+1}^N` dense | elementwise mul | real cosine | mul (self-inv) |
| `hrr_real` | `N(0,1/N)^N` L2-normalized | FFT circular convolution | real cosine | circular correlation |
| `fhrr` | unit-mod `exp(i*phi)` in `C^(N/2)` | elementwise complex mul | Re(Q.conj(X))/n | mul by conjugate |
| `sparse_bipolar` | `{-1,0,+1}^N` density 0.05 | elementwise mul | real cosine | mul (masked) |

**The encoder mediates eviction (the COMPONENT-SUBSTITUTION mechanism):**

The substrate stores each atom as a bound vector:
```
atom_vec[i] = encode(atom_id[i]) (*) encode_recency_bucket(last_query_day[i])
```

To decide eviction, the substrate DECODES each atom's recency:
```
decoded_recency[i] = decode(atom_vec[i], encode(atom_id[i]))
                   = argmax_b ( score(decoded_recency[i], recency_basis[b]) )
```

Eviction decision: evict if `decoded_age > decay_rate_days`.

**Key insight (why the encoder matters):** with a perfect encoder, recency
decodes exactly. With a noisy encoder (low N_dim; high capacity load; sparse
density), decode acc drops, eviction misclassifies, and the Pareto-AUC
discriminator can flip from `TD_DOMINATES` to `RD_DOMINATES`. The cell
measures whether the chain-grade ANCHOR 4 result survives encoder
substitution across the four families.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| encoder_family (OUTER) | {binary_bipolar, hrr_real, fhrr, sparse_bipolar} | 4 |
| decay_rate_days (inner) | {30, 90, 180} | 3 |
| capacity_load_ratio (inner) | {1.0, 5.0} | 2 |
| N_dim (inner; fidelity-vs-crosstalk axis) | {128, 1024} | 2 |

**Cardinality FULL per seed:** `4 * 3 * 2 * 2 = 48` phase points.
**Cardinality SMOKE per seed:** `4 * 2 * 2 * 2 = 32` phase points (drop
decay=180).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

Other fixed substrate parameters (matched to v2 cell for control fidelity):
- `n_atoms = 200`
- `n_days = 365`
- `query_decay_tau = 60.0`
- `recent_query_days = 30`
- `R_BUCKETS = 64` (quantized recency basis)
- `sparse_density = 0.05`

## Hypothesis

**H1 (PRIMARY): Encoders DIFFER in eviction quality when N_dim is small enough
to force crosstalk.** Prediction per encoder (HYPOTHESIZED@):
- `binary_bipolar`: full recency_decode_acc at both N=128 and N=1024 (200
  atoms x 64 buckets fits comfortably; 1024-dim bipolar has 2048 storage
  bits which is well above the (200 atoms x log2(64) buckets = 1200 bits)
  Shannon load).
- `hrr_real`: same as binary at N=1024; at N=128 FFT circular conv may
  introduce small fidelity loss but predicted dominant Pareto outcomes.
- `fhrr`: at N=128 has 64 complex bins = 128 real DoF; predicted equivalent
  to binary at high N, may exhibit phase-coherence loss at low N.
- `sparse_bipolar`: density 0.05 → at N=128 only 6 active bits per
  codeword. Predicted SEVERE fidelity loss at N=128 (DOMINATED_ENCODER);
  remains COMPETITIVE at N=1024 (51 active bits).

**H2 (PARETO INVARIANCE): At HIGH N_dim, ALL 4 encoders pass v2 chain-grade
Pareto-AUC thresholds (dominance_rate >= 0.85, net_dominance >= 0.70,
rd_loss_rate <= 0.05).** Smoke evidence on seed_13 confirms 4/4 encoders
chain-grade at smoke regime including N=128 (where 200/64 isn't a stress).

**H3 (CLIFF DISCRIMINATION): At LOW N_dim (128), sparse_bipolar exhibits
RD_DOMINATES at >= 1 phase point** (mechanism breaks; random eviction
outperforms broken time-decay decisions). Smoke evidence: seed_7 and
seed_19 show 1 RD_DOMINATES point each at sparse @ N=128, dr=90, ld=1.0;
seed_13 shows 0 (random seed luck on this specific atom distribution).

**H4 (POSITIVE CONTROL): binary_bipolar at (decay=90, load=1.0, N_dim=1024)
reproduces v2 cell op-point TD_DOMINATES with recency_decode_acc >= 0.80.**
Smoke evidence: all three seeds reproduce TD_DOMINATES with acc=1.000.

**H5 (NULL): If ALL pair-hashes IDENTICAL after FULL run, encoder is NOT a
discriminating lever for ANCHOR 4 time-decay eviction in tested regime.**
This is a load-bearing NEGATIVE (downstream cells free to pick any encoder
for ANCHOR 4 eviction; substrate inherits HRR default).

## Discriminator: per-encoder v2 Pareto-AUC

For each (encoder, decay, load, N_dim) phase point:
- ARM_TIME_DECAY: encoder's decoded-recency eviction
- ARM_RANDOM_FLOOR: random eviction, count-matched to TIME_DECAY

Pareto outcome per point: TD_DOMINATES / RD_DOMINATES / TIE on
`(ws_retention, 1 - clutter_fraction)` plane.

Per-encoder Pareto-AUC stats:
- `dominance_rate = (td_wins + 0.5*ties) / n_points`
- `net_dominance = (td_wins - rd_wins) / n_points`
- `rd_loss_rate  = rd_wins / n_points`

**Per-encoder v2 chain-grade gate (LOCKED at module init):**
- `dominance_rate >= 0.85` AND
- `net_dominance  >= 0.70` AND
- `rd_loss_rate   <= 0.05`

## Pre-reg bands (LOCKED at module init)

**Cell-level verdict (FULL):**
- **HARD_PASS_ENCODER_DISCRIMINATION**: cardinality_ok + arms_differ all 4 +
  positive_control_pass + n_pairs_differ >= 1 + `n_chain_grade >= 1` AND
  `overall_dominance_rate >= 0.85`
- **MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_CHAIN_GRADE**: encoders distinguish
  (n_pairs_differ >= 2) but `n_chain_grade < 1` AND
  `overall_dominance_rate >= 0.60`
- **MIDDLE_BAND_NULL_ENCODER_INVARIANCE**: all 4 encoders produce identical
  Pareto outcome vectors (H5 confirmed; encoder NOT discriminating lever)
- **MIDDLE_BAND_LOW_DISCRIMINATION**: `overall_dominance_rate < 0.60`
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 48
- **HARD_FAIL_ARMS_IDENTICAL**: any encoder's TD hash == its RD hash
- **HARD_FAIL_CONTROL_FAIL**: positive_control doesn't reproduce TD_DOMINATES
  OR recency_decode_acc < 0.80

**Cell-level verdict (SMOKE):**
- **HARD_PASS_SMOKE**: cardinality_ok (32 pts) + arms_differ all 4 encoders +
  >= 2 encoder pair hashes differ + positive_control_pass + >= 2 encoders
  show `dominance_rate >= 0.50`
- **HARD_FAIL_SMOKE_*** mirrors FULL HARD_FAIL conditions

## Selftest (encoder calibration + positive control)

For each of the 4 encoders at N_dim=1024, M=100, n_buckets=16, seed=8:
- Build store; assert `recency_decode_acc >= 0.50` (each encoder achieves
  better than 50% recall on quantized recency; else encoder adapter broken)
- Confirm 4 encoders produce DISTINCT bound stores (hash-distinctness;
  META_RULE_AF)

Additionally, v2 op-point reproduction (LOAD-BEARING):
- `binary_bipolar @ (decay=90, load=1.0, seed=13, N_dim=1024)` must produce
  `pareto_outcome == TD_DOMINATES` AND `recency_decode_acc >= 0.80`
- This is the positive control: if it fails, the encoder adapter has broken
  the v2 mechanism — cell aborts with CONTROL_FAIL before any phase points.

## Smoke gate (MUST pass before FULL dispatch)

1. 32 corner points all ran (no silent except per META_RULE_J)
2. `cardinality_ok`: observed_n_units == 32
3. `arms_differ` per encoder (TD hash != RD hash) for ALL 4 encoders
4. `>= 2` of the 6 encoder pair hashes differ (mechanism substitution
   produces measurable change for at least 2 pairs)
5. positive_control: binary_bipolar @ (dr=90, ld=1.0, N_dim=1024) shows
   `pareto_outcome == TD_DOMINATES` AND `recency_decode_acc >= 0.80`
6. `>= 2` encoders show `dominance_rate >= 0.50` (mechanism observably works
   for at least two encoders; else cell is at floor everywhere)

## SMOKE EVIDENCE (recorded 2026-06-28; ALL THREE SEEDS HARD_PASS)

Smoke run on laptop CPU at `.venv/Scripts/python.exe`; ~0.2s wall per seed.

| Seed | Verdict | TD_wins | RD_wins | Ties | Overall dom_rate | n_chain_grade | Encoder tiers |
|------|---------|---------|---------|------|------------------|---------------|---------------|
| 7    | HARD_PASS_SMOKE | 31/32 | 1/32 | 0 | 0.969 | 3/4 | binary/hrr/fhrr: COMPETITIVE; sparse: DOMINATED |
| 13   | HARD_PASS_SMOKE | 32/32 | 0/32 | 0 | 1.000 | 4/4 | all 4: COMPETITIVE |
| 19   | HARD_PASS_SMOKE | 31/32 | 1/32 | 0 | 0.969 | 3/4 | binary/hrr/fhrr: COMPETITIVE; sparse: DOMINATED |

**Positive control (verbatim per seed):**
- binary_bipolar @ (dr=90, ld=1.0, N_dim=1024): all 3 seeds reproduce
  `TD_DOMINATES` with `recency_decode_acc = 1.000` (matches v2 cell's
  op-point semantics; encoder adapter does NOT break the v2 mechanism)

**Cliff observable:**
- sparse_bipolar @ N_dim=128: recency_decode_acc drops to 0.090-0.100
  (vs 0.770-0.805 at N_dim=1024); TD eviction misclassifies; on seed_7
  and seed_19 this produces 1 RD_DOMINATES point each at the cliff regime
  (dr=90, ld=1.0, N_dim=128). On seed_13 the same point happens to remain
  TD_DOMINATES by random luck of the atom-day distribution.

## ETA

Smoke (laptop CPU): ~0.2s per seed; ~0.6s total (already executed)
FULL (remote_cpu_queue): ~1-2s per seed; ~3-6s total. Effectively no-cost
on remote_cpu_queue.

Timeout per seed: 600s (10 min margin — well above expected 2s wall).

## Per-experiment timeout calculation (REQUIRED per queue_add.py contract)

Formula: `timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)**scaling_exp * (FULL_seeds/smoke_seeds))`

For ANCHOR 4 encoder family v1:
- `smoke_wall_s` = 0.2s (measured)
- `FULL_N / smoke_N` = `48 / 32 = 1.5` (point count ratio)
- `scaling_exp` = 1.0 (NumPy-light; linear in point count)
- `FULL_seeds / smoke_seeds` = 1 (one seed per sibling file in both modes)
- `timeout_s = ceil(1.5 * 0.2 * 1.5^1.0 * 1)` = `ceil(0.45)` = **1s minimum**

For safety floor (slow remote disks, momentary scheduler pause), pick
`timeout_s = 600` (10 min — well above any plausible variation; per
PROT-019 no large-N tier triggers since no `_n>=4096` suffix in anchor).

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (TD vs RD; per-encoder)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 encoder hashes distinct (else encoder substitution didn't
  happen — mechanism bug). NB: pair-hashes MAY converge in
  high-fidelity regime; cell tolerates this gracefully (>= 2 distinct pairs
  required for chain-grade, not all 6)
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (48 FULL, 32 SMOKE)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24): production-scale calibration; verify-
  referent; basis-vs-use-case; anisotropy guards; suspect 1.000 results
- Functional-requirement decomposition: time-decay eviction = decide which
  atoms to evict given access-pattern recency (single primitive; encoder is
  the substituted COMPONENT that mediates recency decode)
- Substrate-as-canonical query-first: v1 + v2 Pareto-AUC chain (cert ledger
  per Pareto-AUC chain-grade promotion) reviewed; this cell extends by
  SUBSTITUTING the encoder layer between atom-attribute and eviction-decision
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at low N_dim shows
  the cliff (sparse @ N=128 has 6 active bits → severe crosstalk); FULL
  adds dr=180 axis (more decay-rate granularity) without changing
  fidelity regime
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): HARD_PASS only if at least
  one encoder clears chain-grade v2 thresholds AND overall_dominance_rate
  >= 0.85; otherwise MIDDLE_BAND
- NO_HALLUCINATED_NUMBERS (USER 2026-06-27): all smoke numbers above are
  verbatim from `data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}_smoke/metrics.json`
- TEST_RATIONALITY_ENCODING_BEFORE_READOUT (USER 2026-06-27): the recency
  decode is the explicit "encoding mechanism first"; without it, "can
  substrate evict stale items" would be a readout test against an
  un-encoded property; here last_query_day is explicitly encoded via
  bound(atom_id, recency_basis[bucket]) before any eviction-decision

## Positive control

`binary_bipolar` at (decay=90, load=1.0, N_dim=1024, seed=13) must reproduce
v2 cell's TD_DOMINATES outcome. v2 measured at this op-point: TD.ws=1.000,
RD.ws=0.894, pareto=TD_DOMINATES (per metrics.json
`data/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_13`).

Smoke confirms: across all 3 seeds, binary_bipolar at this point produces
`TD_DOMINATES` with `recency_decode_acc = 1.000` and `TD.ws = 1.000`,
matching v2 numerically.

## Composition edges (substrate atomization context)

- This cell uses the v2 Pareto-AUC discriminator (LOCKED): TIME_DECAY vs
  RANDOM eviction with Pareto-dominance on `(ws_retention, 1-clutter_fraction)`
- Encoder is the COMPONENT being swept; eviction-decision pipeline
  (decode_recency -> threshold-on-age) is the COMPOSED-WITH primitive
- Downstream atomization: HARD_PASS promotes the strongest encoder for the
  `time_decay_eviction` ROLE; informs downstream cells' default-encoder
  choice for ANCHOR 4 work

## Outputs

`data/exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_{7,13,19}/metrics.json`
with:
- `phase_map` (list; one entry per phase point — 48 entries FULL, 32 SMOKE)
- `per_encoder_summary` (4 entries; dominance_rate / net_dominance / rd_loss_rate
  / recency_decode_acc_mean per encoder)
- `encoder_pair_distinctness` (6 pair-comparisons; differ flag)
- `arms_differ_per_encoder` (4 entries; TD vs RD hash differ flag per encoder)
- `positive_control_result` (verbose record of the b_b @ v2-op-point check)
- `per_encoder_chain_grade_pass` (4 entries; bool per encoder)
- `n_encoders_chain_grade` (int 0-4)
- `overall_dominance_rate`, `overall_net_dominance`, `overall_rd_loss_rate`
- `encoder_tiers` (DOMINANT / COMPETITIVE / DOMINATED per encoder)

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_ENCODER_DISCRIMINATION: SUBSTRATE_ENCODER_FAMILY_LEVER_FOR_ANCHOR4
  + (per-encoder chain-grade results: which encoders pass; which dominate)
- if MIDDLE_BAND_NULL_ENCODER_INVARIANCE: ENCODER_NOT_DISCRIMINATING_LEVER_FOR_ANCHOR4
  (downstream cells free to pick any)
- if HARD_PASS with cliff-flip pattern (sparse @ N=128 RD_DOMINATES): atom
  ENCODER_DOMINANCE_REQUIRES_MINIMUM_FIDELITY_FOR_ANCHOR4 (load-bearing for
  any downstream "sparse-encoder is the high-M storage path" framing —
  must verify decode fidelity before assuming the eviction mechanism survives)

## Cell-author smoke verdict per seed (RECORDED)

- seed_7: HARD_PASS_SMOKE — 31/32 TD, 1 RD; 3/4 encoders chain-grade; sparse DOMINATED
- seed_13: HARD_PASS_SMOKE — 32/32 TD, 0 RD; 4/4 encoders chain-grade
- seed_19: HARD_PASS_SMOKE — 31/32 TD, 1 RD; 3/4 encoders chain-grade; sparse DOMINATED

All three SMOKE positive controls reproduce v2 op-point TD_DOMINATES with
recency_decode_acc=1.000 (test rig calibrated; encoder adapter does not
break the v2 mechanism).

## Cell file layout (chunked-per-seed)

```
experiments/
  _substrate_anchor4_encoder_family_phase_diagram_v1_core.py
  exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_7.py
  exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_13.py
  exp_substrate_anchor4_encoder_family_phase_diagram_v1_seed_19.py
```

Per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021
config-mismatch guard ON via `run_config={N: N_DIM_DEFAULT, run_mode: ...}`).
