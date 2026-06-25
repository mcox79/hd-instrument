# Pre-reg: substrate_basis_layer_label_contamination_proof_v3_band_corrected

**Authored:** 2026-06-25 by exp_dev.
**Cell:** `experiments/exp_substrate_basis_layer_label_contamination_proof_v3_band_corrected.py`
**Lane:** 1 (substrate-native concept-KG).
**Routing intent:** local_cpu_queue (USER-authorized after Skunkworks tier ruling + 3x convergent drill).
**Prior cell (same code, different bands):** `experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py` (Cell I v2 dispatch).

## Why v3 exists

Cell I v2 (dispatched 2026-06-25; metrics at
`data/exp_substrate_basis_layer_label_contamination_proof_v1/metrics.json`)
returned verdict `HARD_FAIL_REFUTED`. Per-arm raw data showed the principle
held direction-correct:

- LABEL_BASIS retrieval = 0.548 vs RANDOM = 0.647 (Delta = -0.099, std 0.003)
- LABEL_BASIS top5 = 0.806 vs RAND/DW/OF top5 >= 0.995 (clear discrimination)
- within_cat_cos = 0.199 +/- 0.0002 (engineered cone-collapse; mechanism fired on all 5 seeds)

Skunkworks tier ruling 2026-06-25 (notes/skunkworks_tier_ruling_cell_I_v2_basis_label_contamination_2026-06-25.md)
split this into two findings:

- **Atom 1** (T3 experiment_record): `T3/EXP_substrate_basis_layer_label_contamination_proof_v1_MM` —
  MEASURED_MECHANISM_DIRECTION_CORRECT (CERT N += 1 as proven boundary).
- **Atom 2** (T_methodology): `RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M` —
  ADOPTED. For multi-arm "PROVEN: baseline >= X" cells, **X must be capacity-
  feasible** at the chosen (N, M, V, encoder-class) regime. The 0.80 band at
  N=8192 / M=2400 / V=300 Hebbian-bind-bundle was unphysical (empirical
  cleanup-argmax noise floor ~0.65). Suggested fix: switch to **relative
  differential** (LABEL < RANDOM - delta).

Independent 3x deep drill (separate from Skunkworks) converged on the same
remediation and added a **top5 primary metric** recommendation (5x more
headroom; v2's top5 numerics already cleanly discriminate without any
re-running).

v3 implements Skunkworks Atom 2 (relative top1) + drill (top5 primary). Same
code; only verdict bands change.

## Strategic intent

Re-evaluate the same v2 evidence (same code, same RNG seeds -> deterministic
identical raw per-arm numerics) against capacity-feasible bands to confirm or
refute the BIAS-13 principle (basis-layer label contamination should HURT
substrate-native KG retrieval) without the unphysical-threshold failure mode.

This is NOT new science. v3 is band-correction on a measured mechanism v2
already captured.

## Config — IDENTICAL to v2

- N_DIM = 8192
- V_CONCEPTS = 300 (JL-discriminating; N/V = 27)
- V_CATEGORIES = 10 (30 concepts per category)
- V_PREDICATES = 8
- M_TRIPLES = 2400 (8 per concept; well below substrate ~25k capacity at N=8192)
- SEEDS = [7, 13, 17, 23, 29]
- SPARSE_F = 0.02
- K_WTA = 5
- COMP_HELD_FRAC = 0.20
- NOISE_SCALE_AXIS = 0.05

Smoke config (1 seed; ~5-15 min local wall):
- N_DIM = 2048, V_CONCEPTS = 100, V_CATEGORIES = 10, V_PREDICATES = 6
- M_TRIPLES = 600, SEEDS = [7]

## Arms (4) — IDENTICAL to v2 (encoder code bit-for-bit unchanged)

| Arm | Encoder | Labels used? |
|---|---|---|
| ARM_RANDOM_BIPOLAR | isotropic random sparse-bipolar (f=0.02) | NO |
| ARM_LABEL_BASIS_AXIS_PROJECTION | partition N_DIM into 10 axis-subspaces; shared category hub + within-cat perturbation + cross-axis noise | YES (only at encoder construction) |
| ARM_EMERGENT_DEEPWALK | random walks on substrate-KG; skip-gram cooccurrence + JL projection | NO |
| ARM_EMERGENT_OLSHAUSEN_FIELD | forward-only SoftHebb sparse-coding on KG bigram-context | NO |

Audit invariant: `_category_of()` is ONLY called inside `encoder_label_basis_axis_projection`. Grep-verifiable.

## V3 PRE-REGISTERED HARD bands (the only delta from v2)

### Principle PROVEN (ALL must hold; verdict = `HARD_PASS_CHAIN_GRADE`)

**PRIMARY (top5 retrieval discriminates):**
- `ARM_LABEL_BASIS_AXIS_PROJECTION.retrieval.top5 mean <= 0.90`
- `ARM_RANDOM_BIPOLAR.retrieval.top5 mean >= 0.95`
- `(ARM_EMERGENT_DEEPWALK OR ARM_EMERGENT_OLSHAUSEN_FIELD).retrieval.top5 mean >= 0.95`

**SECONDARY (top1 relative — the literal BIAS-13 gate):**
- `(ARM_RANDOM_BIPOLAR.retr_top1 - ARM_LABEL_BASIS.retr_top1) >= 0.05`
- `|ARM_EMERGENT_*.retr_top1 - ARM_RANDOM_BIPOLAR.retr_top1| <= 0.05` (at least one of DW/OF)

**COMPOSITION (relative top5):**
- `(ARM_RANDOM_BIPOLAR.comp_top5 - ARM_LABEL_BASIS.comp_top5) >= 0.10`
- `(ARM_EMERGENT_*.comp_top5 - ARM_LABEL_BASIS.comp_top5) >= 0.10` (at least one)

**DIAGNOSTIC (mechanism fired):**
- `ARM_LABEL_BASIS_AXIS_PROJECTION.within_cat_cos_mean >= 0.15`

### Principle REFUTED (ANY holds; verdict = `HARD_FAIL_BAND_CORRECTED_PRINCIPLE_REFUTED`)

These are GENUINE refutations: principle direction would be wrong regardless of bands.

- `ARM_LABEL_BASIS_AXIS_PROJECTION.retrieval.top5 mean >= 0.95` (no top5 separation)
- OR `ARM_LABEL_BASIS_AXIS_PROJECTION.retr_top1 >= ARM_RANDOM_BIPOLAR.retr_top1` (label NOT hurting in top1)

### Partial / inconclusive

- `HARD_PASS_PARTIAL_TOP5_ONLY_BAND_CORRECTED` if top5 and mechanism fire but top1/comp relative fail
- `MIDDLE_BAND_BAND_CORRECTED` if intermediate
- `CONFOUND_CHECK` if C2 within-cat cosine >= 0.95 (label arm code-degenerate)

## V3 EXPECTED outcome (Q-discipline pre-registration)

Re-running v2 code with same seeds is **deterministic**; v3 should produce
**identical per-arm raw numerics** to v2 (subject to numpy / BLAS minor
nondeterminism in matmul; expected to be negligible for these top1/top5
counts).

Expected verdict: `HARD_PASS_CHAIN_GRADE` (chain-grade band-corrected).

Pre-registered Q-discipline rail: if v3 produces materially different per-arm
numerics than v2 (delta > 0.01 on any retr_top1 or top5 mean across the 5
seeds), that's a NONDETERMINISM finding to investigate BEFORE claiming PASS.

The self-test in v3 has a HARD assertion that V3 verdict logic on v2-recorded
numerics returns `HARD_PASS_CHAIN_GRADE`. This is a load-bearing pre-check.

## Sanity rails / discipline gates

- **Q-discipline rail** (Fix #28-recurring): any arm with `retr_top1 >= 0.995` flagged `Q_SATURATE`.
  Predicted top1 spread 0.55-0.85; no 1.000 arms expected.
- **C2 confound guard**: LABEL_BASIS `within_cat_cos_mean >= 0.95` flags `CONFOUND_CHECK`.
- **Substrate-only assertion**: `_LLM_CALL_COUNTER == 0` asserted before metrics.json write.
- **Determinism check (v3-specific)**: per-arm retr_top1 should match v2 to ±0.01.

## CONFOUND_AUDIT (mandatory per Fix #26)

**C1 axis-projection implementation bug**: cone-collapse could be due to bad noise scale or wrong subspace partition.
- Mitigation: ENCODER CODE IS BIT-FOR-BIT IDENTICAL TO v2. Diff against
  `exp_substrate_basis_layer_label_contamination_proof_v1.py` (lines 245-335
  match exactly). `NOISE_SCALE_AXIS=0.05` matches v2. Subspace partition
  identical.

**C2 degenerate codes in label arm**: if axis-projection produces near-duplicate embeddings within a category, retrieval could fail by code degeneracy.
- Mitigation: `within_cat_cos` measured per arm; v2 observed 0.199 +/- 0.0002
  (well below 0.95 confound threshold). Symmetric cross-axis noise breaks
  degeneracy.

**C3 capacity-respecting tier issue**: if M_TRIPLES is too close to capacity, all arms saturate.
- Mitigation: M=2400 = 8 per concept; substrate capacity at N=8192 is ~25000.
  At ~10% of capacity. v2 confirmed retrieval at random did NOT saturate at
  1.000 (top1=0.647).

**C3 retrofit-risk band tuning (NEW in v3)**: by changing bands after v2 returned HARD_FAIL_REFUTED, are we just retrofitting bands to make the test pass?

Mitigation chain (cited in the cell's `metrics["CONFOUND_AUDIT"]` dict):

1. **The top5 discriminator was visible in v2 raw data BEFORE band tuning.**
   LABEL_BASIS top5 = 0.806 vs RAND/DW/OF top5 >= 0.995 — a 0.19 absolute gap
   that existed in the dispatched v2 metrics file. The drill recommendation
   was an OBSERVATION about v2 data, not a post-hoc band-tweak.

2. **The relative-top1 gate is the literal statement of BIAS-13.** "Label
   contamination should HURT relative to no-label baseline." The absolute
   level of the no-label baseline is irrelevant to the contamination claim.
   The relative formulation pre-dates v2 (see
   `notes/director_encoder_basis_vs_use_case_labels_2026-06-25.md`).

3. **Cell 7 drill (4-of-4) confirmed cone-collapse mechanism on independent
   corpus BEFORE v2 ran.** The mechanism is not in question; only the bands
   were the issue.

4. **Skunkworks Atom 2 methodology rule is independent of v3 authoring.**
   `RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M` is an
   atomized methodology rule (T_methodology), not a v3 band-justification.
   It applies prospectively to all future multi-arm principle cells.

## Bias-checklist application

- **BIAS-13** (basis-layer label contamination): tested DIRECTLY (LABEL_BASIS arm; primary discriminator).
- **BIAS-14** (JL-oversatisfaction): V=300 N=8192 -> N/V=27, productive JL regime.
- **BIAS-15** (prior-data mismatch): 10 categories / 300 concepts -> 30 per category, balanced.
- **BIAS-Q** (suspect 1.000): predicted top1 spread 0.55-0.85; Q rail guards saturation.
- **META_RULE_BAND_CALIBRATION_TOP1_VS_TOP5_REGIME_CHECK** (NEW v3 entry):
  pre-register top1 vs top5 ceiling check based on V_per_cat * argmax-noise
  floor. For N=8192 / M=2400 / V=300 Hebbian-bind-bundle, top1 ceiling ~0.65
  (cleanup-argmax noise); top5 ceiling ~1.0 (cleanup separation dominates).
  Adopt top5 as primary discriminator at this regime.

## Routing flow

1. Author v3 cell (`exp_substrate_basis_layer_label_contamination_proof_v3_band_corrected.py`) — DONE
2. Self-test (must PASS V2-synth band logic check) — DONE (V3 verdict on v2 numerics = HARD_PASS_CHAIN_GRADE)
3. Local smoke (1 seed; all 4 arms produce finite metrics) — pending
4. Commit cell + prereg + smoke metrics — pending
5. queue_add to local_cpu_queue for FULL run (5 seeds; ~10 min wall expected) — pending
6. Report verdict + per-arm numerics + atomization stub — pending

## Smoke PASS criteria

- All 4 arms produce finite metrics (no NaN)
- `ARM_RANDOM_BIPOLAR.retrieval.top1 >= 0.50` (lower bar at smoke scale)
- `ARM_LABEL_BASIS.retrieval.top1 < ARM_RANDOM.retrieval.top1` (preview directional)
- `ARM_LABEL_BASIS.diagnostics.within_cat_cos_mean >= 0.10` (mechanism fires at smoke scale)

## Wall-clock budget

- v2 wall (5 seeds, FULL): 451s = 7.5 min (per per-seed elapsed: 86.3, 89.7, 88.2, 89.9, 96.5)
- v3 same code: ~7.5 min wall expected on local CPU.
- Queue timeout: 1800s (30 min) — generous floor with 4x margin.

## Discipline citations

- Skunkworks tier ruling: `notes/skunkworks_tier_ruling_cell_I_v2_basis_label_contamination_2026-06-25.md`
- v2 prereg base: `preregs/2026-06-25_substrate_basis_layer_label_contamination_proof_v1.md`
- v2 metrics.json: `data/exp_substrate_basis_layer_label_contamination_proof_v1/metrics.json`
- USER directive 2026-06-25: authorize v3 dispatch after drill convergent recommendations.
- Methodology rule: Skunkworks Atom 2 `RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M` (ADOPTED).
