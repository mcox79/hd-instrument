# HALT_ATOMIZE: distributional_shape_zipfian_v2 — HF_PREDICTION_FAILS (dense-Hopfield Dim-H closure)

**Date:** 2026-07-01
**Author:** hdi_exp_dev
**Type:** Halt-atomize hand-off (Skunkworks decides tier)
**Commit hash:** `70aa3b9c` (main; not pushed)
**Session:** Director-decision Option A approved (2026-07-01)
**Compute saved:** ~64,800s remote-CPU (3 × 21,600s FULL dispatches) by DISCRIMINATOR-MUST-SURVIVE-SCALE + Director's explicit falsification rule at smoke preview

---

## Anchors

- `distributional_shape_zipfian_v2_seed_7` (smoke landed HF_PREDICTION_FAILS at preview)
- `distributional_shape_zipfian_v2_seed_13` (authored; NOT dispatched)
- `distributional_shape_zipfian_v2_seed_19` (authored; NOT dispatched)

**Files:**
- `d:/AI/hd-instrument/experiments/exp_distributional_shape_zipfian_v2_seed_7.py`
- `d:/AI/hd-instrument/experiments/exp_distributional_shape_zipfian_v2_seed_13.py`
- `d:/AI/hd-instrument/experiments/exp_distributional_shape_zipfian_v2_seed_19.py`
- `d:/AI/hd-instrument/preregs/2026-07-01_distributional_shape_zipfian_v2.md`
- Smoke metrics (seed_7): `d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v2_seed_7_smoke/metrics.json`

---

## Verdict

**HF_PREDICTION_FAILS at smoke DISCRIMINATOR PREVIEW at full-N=8192.**

Per Director's explicit rule (2026-07-01): "if BOTH Q1 AND Q4 >= 0.95 at preview, sparse-coding two-tier prediction FALSIFIED at these params; halt + report as HARD-FAIL for prediction (valid substrate physics finding)."

Preview point met exactly this condition.

---

## Full-N=8192 preview arm — LOAD-BEARING NUMBERS

MEASURED@`d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v2_seed_7_smoke/metrics.json` (arm `PREVIEW_a1.0_s0.30_L0.30_fullN`):

| Field | Value |
|---|---|
| alpha_shape | 1.0 (natural Zipf) |
| sigma (BSC bit-flip) | 0.30 (30% coord flip) |
| load M/N | 0.30 |
| M items | 2458 |
| N_DIM | 8192 |
| N_QUERIES | 400 |
| beta (adaptive) | 11.36 |
| cosine_margin | 0.975 |
| **recall_all** | **1.000** |
| **recall_Q1_head** | **1.000** |
| **recall_Q4_tail** | **1.000** |
| Q1-Q4 gap | 0.000 (predicted >= 0.15) |
| wall_s | 13.8s |

**BOTH Q1 AND Q4 = 1.000 >> 0.95** → sparse-coding two-tier prediction falsified at these params.

Full smoke sweep (all 54 arms at N_smoke=1024): recall_all=1.000 uniformly across all (alpha, sigma, load). No arm dropped below 1.000.

---

## Physics finding (why prediction failed for dense-Hopfield mechanism-class)

At N=8192 dimensions with iid bipolar keys, cosine_margin = 0.975 (near-orthogonal). BSC bit-flip at sigma=0.30 leaves the query cosine-similar to its target-key by approximately:
  cos(q_noisy, k_target) ~ sqrt(1 - 2*sigma) = sqrt(0.4) ~ 0.63

Softmax attention at beta=11.36 concentrates mass exponentially:
  exp(beta * 0.63) / exp(beta * off_diag_cos) = exp(11.36 * (0.63 - 0.025)) = exp(6.87) ~ 962x

Argmax over M=2458 finds target with overwhelming margin. Zipfian rank-selection changes WHICH items are queried, not HOW retrievable they are. Head items don't get sharpened by frequency because dense-Hopfield tape stores each item ONCE — no reinforcement mechanism.

**Sparse-coding drill's two-tier prediction assumes either:**
1. Storage strength scales with frequency (Willshaw synaptic saturation — multiple writes for head items), OR
2. Keys have shared substructure so head items compete for shared coordinates (Palm-Willshaw sparse-CAM collision regime).

Cell D v2 template has NEITHER. Single-write attention on iid bipolar keys is architecturally the wrong mechanism-class to exhibit the drill's predicted signature.

---

## What this CLOSES

**Hidden phase-diagram Dim-H (distributional shape) for dense-Hopfield mechanism-class.** At operating regimes N=8192, M/N in [0.10, 1.20], sigma in [0, 0.30], alpha in [0, 2.0]:
- Distributional shape does NOT bite dense-Hopfield READ-REPLACE recall.
- Ramsauer 2021 exponential capacity + attention margin dominates.
- Commercial-workload deployment on dense-Hopfield backbone is architecturally robust to Zipfian item selection at these regimes.

Note scope-limits (per META_RULE_M honest calibration):
- Untested regime: sigma near 0.5 (BSC channel capacity limit) — recall floor is unavoidable but shape-invariant claim still likely holds.
- Untested regime: N << 8192 (thin redundancy dimensions where BSC bit-flip drives cos_margin near collision threshold).
- Untested regime: multi-write / consolidated tape (M3 cortex layer). Different mechanism-class per §Follow-up.

---

## Cross-references

- **Sparse-coding drill (source of prediction):** `d:/AI/hd-instrument/notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`
  - D-RIP unified framework (Krahmer-Needell-Ward 2015; Cai-Zhang-Zhang 2014; Baraniuk 2008)
  - Willshaw sparse associative memory (1969); Palm 2010; Gripon-Berrou 2011
  - Predicted mechanism-class: sparse-CAM head-tail asymmetry under noise
- **Hidden phase-diagram taxonomy:** `d:/AI/hd-instrument/notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` (Dim H ranked highest-probability overlooked failure mode, P_deflated=0.38)
- **v1 (superseded):** commit `6b1c994e` — 15-arm sweep at load {0.05, 0.10, 0.15}; underloaded regime; discriminator did not survive scale
- **Parent CG cell:** Cell D v2 dense-Hopfield READ-REPLACE (`data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json`)
- **Ramsauer 2021 capacity:** CITED@eq.14 exponential storable patterns for orthogonal bipolar keys
- **Zipf 1949; Donoho-Tanner CS phase transitions:** CITED

---

## Recommended follow-up (queue as NEW cell; NOT this session)

### Option B — v3 with Hebbian frequency-reinforcement (RECOMMENDED)

**Slug (suggested):** `distributional_shape_zipfian_v3_hebbian_frequency_reinforce`

**Rationale:** tests whether frequency reinforcement produces two-tier under noise — the Willshaw synaptic saturation mechanism-class the D-RIP drill actually describes. This is a DIFFERENT MECHANISM-CLASS from Cell D v2 dense-Hopfield READ-REPLACE, so falsification of dense-Hopfield does NOT close this angle.

**Design sketch:**

Two design variants (Skunkworks / cell-author chooses per follow-up spawn):

**Variant B.1 (tape write-scale reinforcement):**
Modify Cell D v2 tape write:
```python
freq = zipf_probs(M, alpha)         # per-item selection probability
eta = np.sqrt(freq / freq.max())     # per-item write-scale in [0, 1]
K_tape = eta[:, None] * L2norm(keys_raw)
V_tape = eta[:, None] * L2norm(vals_raw)
```
Head items have larger tape magnitude → wider softmax margin → recover better under noise. Tail items have thin magnitude → collide + lose under BSC.

**Variant B.2 (proper Hebbian W-matrix, no attention):**
```python
W = np.zeros((N, N))
for i in range(M):
    W += eta_i * np.outer(vals[i], keys[i])   # eta_i = sqrt(freq_i / freq_max)
# Readout: sign(W @ q_noisy) — classical Hopfield, Amit-Gutfreund 0.138N wall
```
This is the closest analog to Willshaw synaptic saturation. Amit-Gutfreund wall becomes head-tail asymmetric under Zipfian.

**Predicted signature (per drill):**
- HP_TWO_TIER_HEBBIAN: at (alpha=1.0, sigma=0.30, load near Amit-Gutfreund wall M/N ~ 0.10-0.14):
  - Q1_head recall >= 0.85 (frequency reinforcement rescues head from noise)
  - Q4_tail recall <= 0.50 (thin storage magnitude + collision + noise = collapse)
  - Q1-Q4 gap >= 0.30 (much stronger than v2 target 0.15)

**Cardinality:** same 3 alpha × 3 sigma × 6 load = 54 arms per seed cell; Variant B.1 = one extra line in write phase; Variant B.2 = whole different runner (classical Hebbian W-matrix). Variant B.1 is cheaper first probe; B.2 is the Willshaw-canonical mechanism.

**Discriminator preview design:** smoke should include full-N=8192 preview at (alpha=1.0, sigma=0.30, load=0.12) — near classical Amit-Gutfreund wall — for both variants to fire meaningfully.

### Option C — v3 with correlated keys (SKIP — redundant with in-flight cell)

Per Director: **redundant with the in-flight correlated-key rho cell**. Not authoring.

---

## Tier candidacy for Skunkworks

Per Director's substantive-impact note:

> HF_PREDICTION_FAILS with clean mechanism reasoning + preview arm evidence + full-N smoke verification is stronger than a lot of MMs. Skunkworks will decide the tier.

**Evidence pillars for CG eligibility:**

1. **Full-N preview at N=8192** (not just smoke-N=1024) — DISCRIMINATOR-MUST-SURVIVE-SCALE explicitly satisfied
2. **Explicit prediction from external drill** (D-RIP unified framework, 2x depth, 6 citations) — falsification is against a pre-registered theoretical claim, not a null hypothesis
3. **Full sweep breadth** — 54 arms cover alpha × sigma × load lattice, all saturate at 1.000 uniformly (not a lucky-point saturation)
4. **Clean mechanism attribution** — cosine_margin=0.975 + beta=11.36 + BSC-noise-margin sqrt(0.4)=0.63 arithmetic explains WHY the mechanism dominates (not just measures that it does)
5. **Scope-honest claim** — closure is for dense-Hopfield mechanism-class specifically at N>=8192 regime; explicit escape hatches noted (sigma→0.5, N<<8192, multi-write mechanism-class)

**Evidence pillars for MEASURED_MECHANISM (partial demotion):**

1. **Single-seed evidence** — preview + smoke on seed_7 only; seed_13/19 authored but NOT dispatched
2. **Preview arm N_Q=400 only** — CRLB stratified sigma at N_Q/4 ~ 100 is ~0.05; Q4 recall=1.000 is 20 sigma above the 0.95 floor but with N_Q=400 total, per-quartile support could be sharper

**Bias check (per BIAS-13/14/15 regime-suspect):**
- Result "1.000" is suspect per Principle Q (USER 2026-06-24). Cross-check: v1 smoke also saturated at 1.000 uniformly across independent sweep grid; smoke sweep AT N_smoke=1024 also 1.000 across 54 arms independently seeded. Convergence of independent runs at 1.000 is not measurement error — it's the mechanism.

**Skunkworks A5 landed-VET recommendation:** either CG-single-seed with strong physics or MM pending seed_13/19 dispatch. Author defers to A5 role.

---

## Discipline gates satisfied

- Substrate-KB concept check: top hit cosine=0.3477 sub-threshold; novel
- CARDINALITY_OK: EXPECTED_N_UNITS=54; verdict counts arms
- DISCRIMINATOR-MUST-SURVIVE-SCALE: pattern C (full-N=8192 preview arm in smoke) — fired correctly, caught falsification
- META_RULE_AG baseline_in_band: baseline (alpha=0, sigma=0, load=0.10) at 1.000 (over-ceiling; sanity)
- META_RULE_AF arms differ: verified via hash-signature check across 54 arms
- META_RULE_AH atomicity: metrics.json.tmp + os.replace
- META_RULE_L strict-band: HP gates strict `>=` with 5% band-width margin
- META_RULE_M calibration: adaptive_with_discriminator_gate (beta = log2(M) / margin)
- META_RULE_AC provenance: all numbers tagged MEASURED@ / THEORETICAL@ / CITED@
- Chunked one-seed-per-cell architecture (§13)
- Start-marker + crash-diagnostic + heartbeat inline
- ASCII-only

## What Skunkworks needs to do

1. **Tier decision** — CG single-seed vs MM pending seed_13/19 dispatch. Author leans MM given single-seed but defers to A5.
2. **Atom entity name** — suggest: "Dense-Hopfield READ-REPLACE noise+shape invariance at N=8192" (positive-framing) OR "Sparse-coding two-tier prediction falsified for dense-Hopfield mechanism-class" (negative-framing). Author's suggestion is positive-framing since the substantive finding is architectural robustness.
3. **Edge attribution** — should link to Cell D v2 CG (parent), sparse-coding drill (source of prediction), hidden-phase-diagram (Dim H taxonomy).
4. **Follow-up spawn** — recommend Director spawn hdi_exp_dev with `distributional_shape_zipfian_v3_hebbian_frequency_reinforce` slug per Option B above; NOT this session.
