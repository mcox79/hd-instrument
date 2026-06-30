# Pre-registration: substrate_anchor4_encoder_family_phase_diagram_v4

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Skunkworks atomized v3 as MM_PARTIAL_DISCRIMINATION 2026-06-30
(6th phantom-FULL recurrence partial). v3 promoted 0/5 -> 2/5 distinct
(sparse_bipolar + sparse_real wired); dense triplet (binary_bipolar /
hrr_real / fhrr) remained BIT-IDENTICAL at full capacity. Cell-author
self-reported `encoder_pair_distinctness=False` for 3 pairs yet verdict
still emitted HARD_PASS. META_RULE_AY atomized 2026-06-30: verdict-emitter
MUST auto-demote HARD_PASS -> MM/HARD_FAIL on self-reported distinctness
False rate.

## Anchor

`substrate_anchor4_encoder_family_phase_diagram_v4_seed_{7,13,19}` (3 sibling
files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_anchor4_encoder_family_phase_diagram_v4_core.py`.

## Routing

- **Smoke queue:** local CPU (laptop `.venv/Scripts/python.exe`; ~5-20s
  per seed at smoke regime)
- **Full queue:** `overnight_queue` (GPU runner; PROT-020 `import torch`;
  CUDA torch backend at FULL N_DIM up to 8192; ~15-30 min/seed)
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch
  routes through Orchestrator via SendMessage post-smoke.

## v4 fix per design spec (notes/director_anchor4_encoder_v4_design_spec_2026-06-30.md)

### 1. Encoder-specific binding code paths (v3 routed all through same path)

Each encoder invokes its OWN binding op (verified via SHA-256 mechanism_hash):

| Family | bind_op_name | Mathematical op |
|--------|--------------|-----------------|
| binary_bipolar | elementwise_mul_bipolar | a (*) b on {-1,+1}^N |
| hrr_real | fft_circular_convolution | F(c) = F(a) * F(b) |
| fhrr | complex_elementwise_mul | a * b in C^(N/2) |
| sparse_bipolar | elementwise_mul_sparse_bipolar | a (*) b on {-1,0,+1} |
| sparse_real | elementwise_mul_sparse_real | a (*) b on sparse Gaussian |

### 2. Pre-flight distinctness gate (HARD_FAIL pre-dispatch)

At `run_one_seed_phase_diagram` entry, bind a FIXED test pair (n=4) under
each encoder; SHA-256 hash on bytes of bind output. ANY 2 collisions ->
HARD_FAIL_PREFLIGHT (verdict emitted, no phase points run). Implemented in
`verify_encoder_distinctness_preflight()`.

### 3. META_RULE_AY verdict-emitter (NEW)

```python
def emit_verdict_with_AY(base_verdict, base_vmsg, encoder_pair_distinctness):
    n_false = sum(1 for v in encoder_pair_distinctness.values() if not v)
    n_total = len(encoder_pair_distinctness)
    false_frac = n_false / n_total
    if false_frac >= 0.50:
        return "HARD_FAIL", "HARD_FAIL_ENCODER_AXIS_BROKEN"
    elif false_frac >= 0.10 and base_verdict == "HARD_PASS":
        return "MIDDLE_BAND", "MIDDLE_BAND_AY_DEMOTE"
    return base_verdict, base_vmsg
```

Both smoke and FULL verdicts pass through this gate before emission.

### 4. v4 regime (escape saturation)

| Axis | FULL values | SMOKE values | Count |
|------|-------------|--------------|-------|
| encoder_family | 5 | 5 | 5 |
| decay_rate_days | {30, 60, 180} | {30, 180} | 3 / 2 |
| capacity_load_ratio | {8.0, 12.0, 16.0, 24.0} | {8.0, 16.0, 24.0} | 4 / 3 |
| N_DIM | {2048, 4096, 8192} | {2048, 4096, 8192} | 3 / 3 |
| NOISE_SIGMA | 0.1 | 0.1 | const |

**Cardinality:**
- FULL: 5 * 3 * 4 * 3 = **180 phase points per seed**
- SMOKE: 5 * 2 * 3 * 3 = **90 phase points per seed**

EXPECTED_N_UNITS_FULL=180, EXPECTED_N_UNITS_SMOKE=90 LOCKED.

v3 had N_DIMS=[1024,4096,8192] LOADS=[1.0,5.0]; v4 drops N=1024 (too small)
and pushes LOAD to {8.0, 12.0, 16.0, 24.0}. v4 also introduces BUNDLED memory:
each cell's M atoms (M = load * dim_eff / n_buckets) share a single memory vector.
This is the canonical HD capacity stressor; without bundling load was inert
(only modulated timeline). NOISE_SIGMA=0.1 adds Gaussian noise on bundled memory
for additional stress. Goal: NO cell saturates to 1.000. LOAD axis empirically
calibrated against smoke: dropped {2.0, 4.0} (FHRR saturates at load=4 across N).

### 5. Discriminator-survives-scale (smoke at FULL-N range)

Smoke uses identical N_DIMS as full ({2048, 4096, 8192}). Smoke verifies:
- (a) preflight all 5 hashes distinct
- (b) per-encoder metrics differ by `|delta recency_decode| >= 0.05`
  on >=7/10 cross-encoder pairs averaged across grid
- (c) NO cell saturates at recall=1.000 at smoke regime

## Pre-reg discriminator bands (LOCKED)

### Per-encoder chain-grade gate (v3 Pareto-AUC + META_RULE_AP)
- `dominance_rate >= 0.85`
- `net_dominance >= 0.70`
- `rd_loss_rate <= 0.05`
- `recency_decode_acc_mean >= 0.30`

### Cell-level HARD gates
- **HARD_FAIL_PREFLIGHT**: encoder bind hash collision pre-dispatch (META_RULE_AY)
- **HARD_FAIL_CARDINALITY_BREACH**: observed != expected
- **HARD_FAIL_ARMS_IDENTICAL**: TD and RD per-encoder hashes match
- **HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX):**
  `n_pairs_differ < 5 of 10`
- **HARD_FAIL_SATURATION (META_RULE_Q):** `saturation_frac >= 0.50` at FULL
- **HARD_FAIL_METRIC_COLLAPSE:** `n_pairs_metric_distinct < 7/10` at smoke
- **HARD_FAIL_CONTROL_FAIL**: positive control fails
- **HARD_FAIL_ENCODER_AXIS_BROKEN (META_RULE_AY):**
  `false_frac(pairs_differ) >= 0.50`
- **HARD_FAIL_LLM_LEAK**: `n_llm_calls > 0`

### Verdict bands

| Verdict | Condition |
|---------|-----------|
| HARD_PASS | `n_chain_grade >= 4/5` AND `overall_dom >= 0.85` AND `n_pairs_metric_distinct >= 7/10` AND pre-flight pass AND no saturation |
| MIDDLE_BAND | encoders distinguish (pairs_differ >= 5) but n_chain_grade < 4, OR HARD_PASS auto-demoted by META_RULE_AY (10-50% False) |
| HARD_FAIL | any HARD gate trips OR META_RULE_AY >= 50% False |

v3 had HARD_PASS at n_chain_grade >= 2; v4 raises to >=4 to require near-
universal encoder discrimination (only 1 dominated encoder allowed).

## Positive control (v4 op-point)

`binary_bipolar @ (decay=180, load=8.0, N_DIM=4096, seed=13, noise_sigma=0.1, bundle)` MUST:
- `pareto_outcome == TD_DOMINATES`
- `0.60 <= recency_decode_acc <= 0.999` (NOT saturated; META_RULE_Q)

Higher load + noise (vs v3's load=1.0, no-noise op-point at decode=1.000)
forces non-saturated working regime where mechanism resolution is observable.

## Smoke gate predicate (8 conditions; ALL must pass)

1. preflight_ok (all 5 encoder bind hashes distinct)
2. cardinality_ok (90 / 90)
3. arms_differ per encoder (TD != RD hashes for all 5 encoders)
4. **n_pairs_differ >= 5 of 10** (META_RULE_AX)
5. **n_pairs_metric_distinct >= 7 of 10** (NEW v4; `|delta rec_decode| >= 0.05`)
6. **saturation_frac == 0.0** at smoke (META_RULE_Q strict; no cell at 1.000)
7. positive control PASS (TD_DOMINATES + non-saturated decode)
8. per-encoder recency_decode_acc_mean >= 0.30 (META_RULE_AP)
9. >= 2 encoders show dominance_rate >= 0.50 (mechanism fires)

## SCHEMA-VET checklist (load-bearing pre-dispatch)

- [x] CARDINALITY_OK: EXPECTED_N_UNITS_FULL=180, EXPECTED_N_UNITS_SMOKE=90 declared
- [x] META_RULE_AF arms-must-differ: SHA-256 hash gate per encoder (TD vs RD)
- [x] META_RULE_AX arms-distinct-across-family-axis: 5/10 pairs distinct floor
- [x] **META_RULE_AY (NEW): pre-flight bind hash gate + verdict-emitter auto-demote**
- [x] META_RULE_AW seed-config-identical: SEED is only variable across siblings
- [x] META_RULE_AH atomic metrics: `tmp + os.replace` for all writes
- [x] META_RULE_AC numbers tagged: all pre-reg numbers TAGGED below
- [x] META_RULE_AP readout-floor: recency_decode_acc >= 0.30 per encoder
- [x] **META_RULE_Q (NEW v4): saturation_frac strict floor at smoke (==0.0);
  hard_fail at FULL (>= 0.50)**
- [x] `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- [x] `import torch` present (PROT-020 GPU routing)
- [x] CRLB / capacity feasibility: 1500 atoms at 128 buckets = ~12 atoms/bucket;
  per-atom-decode-feasible because atom IDs are codebook-distinct. Noise injection
  at sigma=0.1 lowers SNR; decode is now ~0.60-0.95 expected (non-saturated).
  Top-k argmax over 128 buckets remains identifiable. crlb_n/a declared: ANCHOR 4
  is not a quantitative-noise-floor cell; eviction decision is binary per atom.
- [x] HP_SCOPE: HARD_PASS chain-grade gates apply ONLY to encoder arms;
  RANDOM arm exempt (by construction)
- [x] discriminator-survives-scale: smoke at FULL-N range {2048, 4096, 8192};
  smoke discriminator checks (a)+(b)+(c) per v4 spec

## Numbers TAGGED (META_RULE_AC)

- v4 cardinality FULL=180, SMOKE=90: HYPOTHESIZED@this prereg derived from
  5 enc * 3 decay * 4 load * 3 N_DIM (FULL) and 5 * 2 * 3 * 3 (SMOKE).
- NOISE_SIGMA=0.1: HYPOTHESIZED@design spec; rationale = inject SNR floor
  below saturation regime. MEASURED@smoke: 0/90 saturated cells per seed; OK.
- N_DIM lower bound 2048: HYPOTHESIZED@design spec; v3 had N=1024 too small.
- LOAD upper bound 24.0: empirically calibrated against smoke after design-spec
  {2.0, 4.0, 8.0, 12.0} produced FHRR saturation at load<=4; raised to {8, 12, 16, 24}.
- BUNDLED memory (M atoms / chunk): NEW v4 mechanism; previous versions stored each
  atom's bound vector separately so load was inert (only modulated timeline).
  Bundling makes load = bundle_capacity_ratio drive interference; M = round(load *
  dim_eff / n_buckets). MEASURED@smoke: rec drops from ~0.99 at low load to ~0.30
  at load=24 (genuine capacity gradient).
- DECAY 60 (replaces v3's 90): HYPOTHESIZED@design spec; mid-decay axis
  retained.
- META_AY_HARD_FAIL_FRAC=0.50, META_AY_MM_DEMOTE_FRAC=0.10: HYPOTHESIZED
  @design spec verbatim. >=50% False = encoder axis broken; >=10% False =
  cell tier-demoted from HP to MB.
- v3 distinctness verdict-emission breach (cell-author self-reported
  encoder_pair_distinctness False for 3 pairs but verdict emitted HARD_PASS):
  CITED@Skunkworks landed-VET atomization 2026-06-30 a4bfdc71.
- HP_MIN_PAIRS_DIFFER=5: ported from v3 ratify (Skunkworks recommended >=5).
- HP_RECENCY_DECODE_FLOOR=0.30: ported from v3 ratify (META_RULE_AP base).
- HARD_PASS threshold n_chain_grade >= 4 (raised from v3 >=2):
  HYPOTHESIZED@this prereg. Rationale = if 4/5 encoders all chain-grade
  AND 7/10 metric pairs distinct AND no saturation, framing as encoder-
  family-invariant is justified. v3's >=2 allowed partial framing.

## Open questions for landed-VET (Skunkworks)

- Is `NOISE_SIGMA=0.1` sufficient to escape saturation across all 5 encoders?
  Smoke discriminator check (c) verifies; if smoke fails saturation strict
  floor, will re-author at sigma=0.2.
- Is `n_chain_grade >= 4` the right HARD_PASS bar? Design spec says >=4
  for HARD_PASS, >=3 for MM. Cell-author chose v3's >=2 ratchet to >=4.
- Is the v4 LOAD axis {2.0, 4.0, 8.0, 12.0} regime-defensible? Skunkworks
  landed-VET call; concern is whether 12.0 is so over-capacity that all
  encoders collapse to chance (mechanism doesn't differentiate).
- v4 verdict-emitter HARD_FAIL on `>= 50%` False: is this the right
  threshold? Design spec verbatim; could argue >= 30% is stricter.

## Cardinality_ok (META_RULE_H)

```
EXPECTED_N_UNITS_FULL  = 5 enc * 3 decay * 4 load * 3 N_DIM = 180
EXPECTED_N_UNITS_SMOKE = 5 enc * 2 decay * 3 load * 3 N_DIM = 90
cardinality_ok: bool field in metrics.json
HARD_FAIL_CARDINALITY_BREACH on mismatch
```

## Dispatch info

- Per-seed timeout estimate: smoke ~13s CPU MEASURED; FULL on GPU ~5-15 min
  (180 phase points; each ~0.1-0.3s GPU at smoke wall, ~3x for full vs smoke)
- Smoke MEASURED@laptop CPU: seed_7=13.0s, seed_13=13.1s, seed_19=14.2s
- All 3 seeds smoke HARD_PASS: 90/90 td_wins, 10/10 pairs_differ, 8-9/10 metric_distinct,
  0/90 saturation, 5/5 encoders chain-grade.
- Timeout per cell: **1800s** (30min/seed per spec; smoke at full-N range
  may take longer than v3 due to larger per-cell N)
- 3 seeds dispatched separately (chunked per USER 2026-06-28; runner-death
  loses 1/3 seeds at most)
- Routing: `overnight_queue` (PROT-020 `import torch` confirmed)
- Helper modules SCP'd: `experiments/_seed_checkpoint.py` and
  `experiments/_substrate_anchor4_encoder_family_phase_diagram_v4_core.py`
- run_mode=full verification post-dispatch (§16): mandatory; sentinel file
  size > 5KB at full
