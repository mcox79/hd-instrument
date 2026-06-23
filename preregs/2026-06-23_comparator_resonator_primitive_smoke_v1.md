# PREREG: comparator_resonator_primitive_smoke_v1

**Date:** 2026-06-23
**Anchor:** comparator_resonator_primitive_smoke_v1
**Routing:** local_cpu_queue (smoke-only; numpy-only; ~5min wall)
**Source:** notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md L1 Stream C+D / L3 Mechanism B
**Author:** exp_dev (under Director/Research routing)

---

## SCIENTIFIC QUESTION

The substrate has NO 2-argument relational-comparator primitive. HotpotQA comparison questions sit at em=0.07 (floor) in the v2 cell because the substrate's W chains entity-to-entity but cannot evaluate "X attribute1 vs Y attribute1 -> which-is-greater?" Brain analogue: hippocampus stores pair-wise associations; RLPFC integrates them at choice time via a comparator. Substrate has the hippocampal analogue (W); no RLPFC analogue.

**Hypothesis:** a substrate-native RESONATOR comparator built from `bind`, scalar-value fractional-power-encoding, and a sign-test on hypervector projection CAN evaluate two-argument relational predicates over retrieved attribute values, at chain-grade accuracy (>=0.75 on synthetic templated questions where the ground truth is known by construction).

**Falsification target:** if the comparator fails to clear 0.75 across 3 seeds OR fails to beat both trivial baselines (raw W-lookup argmax AND majority-class frequency-bias) by >= 0.20, the comparator primitive is dead at this substrate regime and the substrate-QA composition gap for comparison questions is structurally closed (route to L2 glass-box-LLM closure).

---

## CELL CONFIG

- **N_DIM:** 4096 (FHRR-like real numpy with circular-convolution bind)
- **M:** 50 entities
- **A:** 5 attributes per entity (born_year, height_cm, founded_year, salary_usd, population)
- **Seeds:** [7, 17, 23]
- **Question pool:** 60 templated comparison questions per seed
  - 30 "Is X attr1 greater than Y attr1?" (single-attribute binary comparison; sampled across the 5 attrs)
  - 30 "Is X-or-Y attr1 closer to Z attr1?" (3-way comparison)
- **Attribute values:** integers drawn from per-attribute ranges (born_year in [1900, 2000], height_cm in [150, 200], founded_year in [1800, 2020], salary_usd in [30000, 200000], population in [1000, 1000000]); each entity's value vector is fixed per-seed.
- **Scalar value encoder:** fractional-power-encoding via real-valued analog: `scalar_value_vec(v) = circular_convolution_power(base_vec, v_normalized)`, where v_normalized = (v - v_min) / (v_max - v_min) in [0, 1]; concretely implemented via FFT-based fractional convolution power so that the encoded vector is continuous in v.

### Arms (3)

1. **ARM_RAW_W_LOOKUP**: ingest entity-attribute as `W += outer(bind(E[X], R[attr]), value_scalar_vec(v))`; at query, retrieve `v_X_hat = W @ bind(E[X], R[attr])` and `v_Y_hat = W @ bind(E[Y], R[attr])`; argmax over scalar-value-codebook to recover the integer value; sign-test on (val_X - val_Y).
2. **ARM_COMPARATOR**: ingest via the same outer-product but compute the sign directly via projection: `score = dot(W @ bind(E[X], R[attr]) - W @ bind(E[Y], R[attr]), basis_direction_vec)`; sign-test on score (no scalar reconstruction).
3. **ARM_FREQ_BIAS**: majority-class prediction per question type (always-X or always-Y for binary; always-X or always-Y or always-Z for 3-way). Computed per-seed.

### Sanity self-test (endpoint check)

5-pair holdout with KNOWN integer ordering 1..50 mapped 1:1 to a synthetic attribute. ARM_COMPARATOR must give 100% correct sign on the 5 pairs. If not, comparator math is broken and the whole cell aborts with HARD_FAIL before the main sweep.

---

## PRE-REG HARD-PASS BANDS

**HARD_PASS (chain-grade-candidate comparator primitive):**
- ARM_COMPARATOR accuracy >= 0.75 across all 3 seeds (min across seeds >= 0.75)
- AND ARM_COMPARATOR mean >= ARM_FREQ_BIAS mean + 0.20 (comparator beats majority-class by 20 EM points)
- AND sanity-self-test passes 5/5 on the holdout (mechanism is sound)

**HARD_FAIL (comparator mechanism dead; substrate-QA structurally closed for comparison):**
- ARM_COMPARATOR mean <= ARM_RAW_W_LOOKUP mean + 0.05 (adds nothing over raw lookup)
- OR ARM_COMPARATOR mean <= ARM_FREQ_BIAS mean (loses to majority-class)
- OR sanity-self-test fails (math wrong)

**MIDDLE_BAND (partial primitive characterization):**
- ARM_COMPARATOR mean in (ARM_RAW_W_LOOKUP + 0.05, ARM_FREQ_BIAS + 0.20)
- Onboard as MEASURED_MECHANISM (comparator-partial); queue a parameter sweep cycle (N_DIM ladder, attribute-cardinality sweep) to characterize the regime where comparator clears chain-grade.

---

## SCALING / RUNTIME

- **Smoke (this cell):** N_DIM=4096, M=50, 60 Q, 3 seeds, ~5 min CPU wall (numpy matmuls of 4096x4096 are ~0.5s each; 3 seeds * 60 Q * 3 arms * ~0.05s = ~30s; plus 3 ingest builds ~3s each).
- **No FULL run queued here.** This is a primitive-validation smoke. If HARD_PASS, follow-on cells extend to:
  - integration with substrate KG storage at h_hotpotqa scale
  - synthetic-attribute -> real-HotpotQA-attribute transfer test
  - composition with bridge-chain composition for K>=3 multi-hop comparison

---

## FORMULA SELF-TESTS (run unconditionally at startup)

1. **Bind/unbind round-trip:** `unbind(bind(a, b), b) ~= a` within cosine 0.95 at N_DIM=4096.
2. **Scalar-value-vec monotonicity:** `cos(scalar_vec(v1), scalar_vec(v2))` strictly decreases as |v1 - v2| grows for v1, v2 in [0, 1].
3. **Ordering preservation under projection:** for known integer pairs (i, j) with i < j, the projection `dot(scalar_vec(i) - scalar_vec(j), basis_direction)` has consistent sign across multiple random basis_direction draws (signal is in the direction; noise washes out at N_DIM=4096).

Self-test failure -> exit non-zero before main sweep.

---

## SUBSTRATE / META ALIGNMENT

- **By-construction-saturation:** ARM_FREQ_BIAS is the trivial-prior baseline (by-construction predictable from question-type alone). HARD_PASS requires beating it by 0.20 -- substrate adds real work above the trivial bound.
- **Negativity-bias symmetric verify:** HARD_FAIL bands are STRICTER than HARD_PASS bands (must lose to BOTH raw-lookup AND freq-bias to fail). MIDDLE_BAND is the honest in-between.
- **Verify-the-referent:** sanity self-test on KNOWN ordering ensures the comparator math actually does what it claims before any QA-band measurement.
- **No Hebbian-window:** comparator does NOT modify W at query time. Forward-only. Compatible with substrate continual-learning lane.

---

## SOURCE & CONTEXT

- Research drill: `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` -> Stream C (transitive inference brain mechanisms) + Stream D (HDC Resonator Networks).
- Lit anchor: Frady-Kent-Olshausen-Sommer 2020 "Resonator Networks" (bind/unbind/cleanup iteration for compound HD structure decomposition).
- Substrate-internal precedent: existing `hdlab/binding.py` (bind/unbind via FFT circular convolution); existing `hdlab/char_trigram_encoder.py` (entity-name encoder); CERT 587 g1b autoregressive generation; CERT 588 h_hotpotqa KG primitive.
- Brain anchor: DeVito-Lykken-Kanter-Eichenbaum 2010 -- RLPFC performs the comparator/integrator function at choice time over hippocampal relational stores; substrate has the hippocampal analogue (W) but no RLPFC analogue.

---

## CONTRACT OUTPUT

`exp_dev: queued comparator_resonator_primitive_smoke_v1 -> local_cpu_queue ; smoke-only ~5min ; HARD_PASS = ARM_COMPARATOR >=0.75 across 3 seeds AND >= ARM_FREQ_BIAS + 0.20 ; HARD_FAIL = comparator <= max(raw_lookup+0.05, freq_bias) OR sanity-selftest fails ; substrate primitive Gap 3 QA composition build`
