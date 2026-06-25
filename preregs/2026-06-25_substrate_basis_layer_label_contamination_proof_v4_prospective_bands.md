# Pre-reg: substrate_basis_layer_label_contamination_proof_v4_prospective_bands

**Authored:** 2026-06-25 by exp_dev (coordinated blitz Agent 1 of 3).
**Cell:** `experiments/exp_substrate_basis_layer_label_contamination_proof_v4_prospective_bands.py`
**Lane:** 1 (substrate-native concept-KG; pure numpy; substrate-only).
**Routing intent:** local_cpu_queue (CPU-feasible; ~10min wall estimated).
**Prior cells (same code, evolving bands/seeds):**
- `experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py` (Cell I v2; absolute bands; HARD_FAIL_REFUTED)
- `experiments/exp_substrate_basis_layer_label_contamination_proof_v3_band_corrected.py` (v3 capacity-feasible bands; HARD_PASS_CHAIN_GRADE_BAND_CORRECTED; Skunkworks ruled CHAIN_GRADE_PARTIAL)

## Why v4 exists

v3 returned `HARD_PASS_CHAIN_GRADE_BAND_CORRECTED` on seeds [7, 13, 17, 23, 29] using
v3 bands. Skunkworks ruled `CHAIN_GRADE_PARTIAL` because bands had been tuned
post-hoc on v2 data (even though tuning logic was disciplined: top5 discriminator
visible BEFORE band tuning; relative top1 from BIAS-13 principle; cone-collapse
mechanism pre-confirmed by Cell 7).

**v4 is the DEFINITIVE upgrade test:** same code, **same bands locked at cell init
via assertion**, FRESH seeds [42, 47, 51] that have NEVER seen the bands. If v4
PROVEN bands pass on fresh seeds + phase-scan consistency, the bands are
GENUINELY PROSPECTIVE not retrospective-fit.

## Strategic intent

Convert the substrate's BIAS-13 cone-collapse evidence from MM_DIRECTION_CORRECT
(v2) → CHAIN_GRADE_PARTIAL (v3) → CHAIN_GRADE_DEFINITIVE (v4) by closing the
retrospective-band-tuning audit gap.

This is a methodology proof, not new science. v4 holds the mechanism constant and
adds the prospective-band discipline.

## Config — PRIMARY OPERATING POINT IDENTICAL to v3

| Param | Value | Reason |
|---|---|---|
| N_DIM | 8192 | v3 invariant |
| V_CONCEPTS | 300 | v3 invariant |
| V_CATEGORIES | 10 | v3 invariant |
| V_CONCEPTS_PER_CAT | 30 | derived |
| V_PREDICATES | 8 | v3 invariant |
| M_TRIPLES | 2400 | v3 invariant (well below ~25k capacity) |
| SPARSE_F | 0.02 | v3 invariant |
| K_WTA | 5 | v3 invariant |
| **SEEDS** | **[42, 47, 51]** | **V4 DELTA: fresh; never used in v1/v2/v3** |
| **PHASE_SCAN_VC_VALUES** | **[200, 500]** | **V4 DELTA: phase-diagram envelope** |
| PHASE_SCAN_SEED | 42 | one of fresh seeds |

## V4 PROSPECTIVE BANDS — IDENTICAL to v3 (asserted at cell init)

The cell module includes `ASSERT_PROSPECTIVE_BANDS_MATCH_V3()` invoked at import
time. If ANY band differs from v3, the cell aborts with `PROSPECTIVE_BAND_VIOLATION`.

### PROVEN top5 retrieval (primary discriminator)
- `LABEL_BASIS top5 ≤ 0.90`
- `RANDOM top5 ≥ 0.95`
- `EMERGENT (DW OR OF) top5 ≥ 0.95`

### PROVEN relative top1 (the principle gate)
- `LABEL_top1 < RANDOM_top1 - 0.05` (LABEL hurts retrieval)
- `EMERGENT within RANDOM ± 0.05` (no-label encoders match no-label baseline)

### PROVEN composition (relative top5)
- `LABEL comp_top5 < RANDOM comp_top5 - 0.10`
- `EMERGENT comp_top5 ≥ LABEL comp_top5 + 0.10`

### DIAGNOSTIC (mechanism fired)
- `LABEL within_cat_cos ≥ 0.15` (cone-collapse engaged; v2 measured 0.199±0.0002)

### REFUTED (principle direction wrong; band-correction wouldn't save)
- `LABEL top5 ≥ 0.95` (no top5 separation)
- `LABEL top1 ≥ RANDOM top1` (relative inversion)

### V4 EXTENSION: phase-scan consistency
- At V_C=200 AND V_C=500: `LABEL_top1 < RANDOM_top1 AND LABEL_top5 < RANDOM_top5`

### Sanity rails
- `Q_SUSPECT_RETR_TOP1_MAX = 0.995` (saturation flag)
- `CONFOUND_LABEL_WITHIN_CAT_COSINE_MAX = 0.95` (degenerate-codes flag)

## Verdict bands

- **HARD_PASS_CHAIN_GRADE_DEFINITIVE**: all PROVEN gates PASS on fresh seeds AND phase-scan consistent → CERT-promotable as definitive
- **HARD_PASS_CHAIN_GRADE**: all PROVEN gates PASS but phase-scan inconsistent (principle holds at primary V_C only)
- **HARD_PASS_PARTIAL**: only top5 + mechanism fired (no top1-relative)
- **MIDDLE_BAND**: some PROVEN pass; partial replication
- **HARD_FAIL_PROSPECTIVE**: REFUTED on fresh seeds (band-correction wouldn't save it)

## Q discipline

- All bands are physically achievable at chosen M/N/V (cf. Skunkworks RULE_4arm_principle_band_must_be_capacity_feasible). M=2400, V=300, N=8192 keeps capacity headroom; top1 cleanup-argmax noise floor ~0.65 makes 0.95 top5 reachable across no-label arms.
- Fresh seeds [42, 47, 51] are deterministically independent of v1/v2/v3 seeds; no info-leak.
- V_C scan tests whether the principle generalizes (defines operating envelope around primary point).

## Fix #28 discipline

- Per-arm metrics reported (4 arms × 6 metrics each); verdict_msg cites per-arm numerics.
- No verdict summary text used as ground-truth for downstream classification.

## Pre-registered expectation (Q-discipline)

Cone-collapse mechanism is corpus-substrate-dependent (already validated 3x: v2 raw,
v3 re-run, Cell 7 drill). Fresh seeds [42, 47, 51] should reproduce direction-correct
discrimination because the mechanism is deterministic given the encoder construction,
not seed-fit. **Expected v4 verdict:** `HARD_PASS_CHAIN_GRADE_DEFINITIVE` (P ~ 0.65;
slight deflation vs v3 because fresh seeds CAN produce within-band noise variance).

If v4 returns MIDDLE_BAND on fresh seeds, that is the genuine prospective ruling
(bands tighter on noise variance than v3 estimated); not a refutation, just a band
recalibration toward more seeds.

If v4 returns HARD_FAIL on fresh seeds, the mechanism is unstable to seed init and
the prior chain-grade evidence was seed-fortunate; that IS a serious finding.

## Operational disciplines (Q-checklist)

- D1 roofline (CPU primary): pure numpy on N=8192/M=2400 should be ~3-5min/seed; 3 seeds + V_C-scan ~10-15min total
- D2 atexit + per-seed checkpoint mandatory (via `_seed_checkpoint`)
- Self-test PASS gate (verified before commit)
- LOCAL SMOKE PASS gate (USER re-enabled local smoke)
- ASCII only
- Substrate-only (`_LLM_CALL_COUNTER = [0]`; pure numpy; no torch)
- Per-arm metrics (Fix #28)

## Disposition

- If HARD_PASS_CHAIN_GRADE_DEFINITIVE: route to Skunkworks for CERT upgrade-DEFINITIVE VET
- If HARD_PASS_CHAIN_GRADE: route to Skunkworks; flag phase-scan inconsistency for follow-up
- If MIDDLE_BAND / HARD_FAIL: route NEGATIVE to Research for 2x revival drill

## Cites

- `experiments/exp_substrate_basis_layer_label_contamination_proof_v3_band_corrected.py`
- `preregs/2026-06-25_substrate_basis_layer_label_contamination_proof_v3_band_corrected.md`
- Skunkworks v3 tier ruling (CHAIN_GRADE_PARTIAL pending definitive upgrade)
- BIAS-13 director_encoder_basis_vs_use_case_labels_2026-06-25
- Cell 7 cone-collapse drill (4-of-4 mechanism confirmation, independent corpus)
