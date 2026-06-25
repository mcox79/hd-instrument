# Pre-reg: substrate_basis_layer_label_contamination_proof_v1

**Authored:** 2026-06-25 by exp_dev. USER-revised spec (4 arms, no classifier).
**Cell:** `experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py`
**Lane:** 1 (substrate-native concept-KG)
**Routing intent:** LOCAL SMOKE FIRST (USER re-enabled local smoke gate); then route to remote_cpu_queue for FULL run via Orchestrator (USER decides remote dispatch).

## Strategic intent

Prove BIAS-13 (basis-layer label contamination) and Principle O (basis layer should be unsupervised; use-case can have labels separately) via a clean 4-arm retrieval+composition test where:

- a label-driven basis is predicted to LOSE retrieval (cone-collapse)
- random and biology-native emergent bases are predicted to WIN
- composition shows the same pattern (basis carries / fails-to-carry compositional structure)

**USER pushback honored:** Director's original spec had 6 arms with classifier readout. USER removed classifier readout entirely. This cell uses labels in only ONE arm (`ARM_LABEL_BASIS_AXIS_PROJECTION`); 3 of 4 arms have ZERO labels anywhere. The labels-at-use-case claim is SEPARATE and not tested here.

## Config (FULL)

- N_DIM = 8192
- V_CONCEPTS = 300 (JL-discriminating: N/V = 27)
- V_CATEGORIES = 10 (30 concepts per category)
- V_PREDICATES = 8
- M_TRIPLES = 2400 (8 per concept; well below substrate capacity ~25k at N=8192)
- SEEDS = [7, 13, 17, 23, 29] (5 seeds for statistical power)
- SPARSE_F = 0.02
- K_WTA = 5
- Retrieval = recall@1 on all M stored triples (substrate-native; per USER spec "cosine+cleanup on stored triples")
- Composition = held-out 2-hop chains assembled from train edges (independent split inside task; 20% chain-held)

## Config (SMOKE)

- N_DIM = 2048
- V_CONCEPTS = 100
- V_CATEGORIES = 10 (10 concepts per category)
- V_PREDICATES = 6
- M_TRIPLES = 600 (6 per concept)
- SEEDS = [7] (1 seed)
- Expected wall: 5-15 minutes on local CPU

## Arms (4) — all retrieval+composition, NO classifier readout

| Arm | Encoder mechanism | Labels used? | Prediction |
|---|---|---|---|
| ARM_RANDOM_BIPOLAR | isotropic random sparse-bipolar (f=0.02) | NO | retrieval ≥ 0.80 (substrate-native baseline) |
| ARM_LABEL_BASIS_AXIS_PROJECTION | partition N_DIM into 10 axis-subspaces (one per category); concept in cat c lives in subspace c + cross-axis noise | YES (only at encoder construction) | retrieval ≤ 0.65 (cone-collapse HURTS) |
| ARM_EMERGENT_DEEPWALK | random walks on substrate-KG graph edges; skip-gram cooccurrence + JL projection | NO | retrieval ≥ ARM_RANDOM - 0.05 (matches or beats) |
| ARM_EMERGENT_OLSHAUSEN_FIELD | forward-only SoftHebb sparse-coding on KG bigram-context (numerical stability per commit 3e3a7421) | NO | retrieval ≥ ARM_RANDOM - 0.05 |

**Audit:** the function `_category_of()` is ONLY called inside `encoder_label_basis_axis_projection`. Greppable. ARMS 1, 3, 4 receive `triples_train` but never invoke `_category_of()`.

## Two measurements per arm (substrate-native; no classifier needed)

1. **M1 RETRIEVAL**: substrate's native task. For each STORED (s, p, o) triple (all M ingested), key (s, p) should score o top-1 (cosine+cleanup on ingest matrix W). Primary discriminator per USER spec. Cone-collapse in LABEL_BASIS blocks argmax separation among same-category o's even on stored facts.
2. **M2 COMPOSITION**: substrate-product task. 2-hop chains (s, R1, mid) + (mid, R2, o) where each hop is in train but the chain composition is held out (20%). Tests whether the basis carries compositional structure beyond direct lookups.

NO CLASSIFIER ARM. NO LABEL-USE AT USE-CASE LAYER.

## Pre-registered HARD bands

### Principle PROVEN (ALL must hold)
- `ARM_LABEL_BASIS_AXIS_PROJECTION.retrieval.top1 mean <= 0.65`
- `ARM_RANDOM_BIPOLAR.retrieval.top1 mean >= 0.80`
- `(ARM_EMERGENT_DEEPWALK OR ARM_EMERGENT_OLSHAUSEN_FIELD).retrieval.top1 mean >= ARM_RANDOM_BIPOLAR.retrieval.top1 - 0.05`
- `ARM_LABEL_BASIS_AXIS_PROJECTION.composition.top1 mean <= 0.55`
- `ARM_RANDOM_BIPOLAR.composition.top1 mean >= 0.70`

Verdict: `HARD_PASS_CHAIN_GRADE`

### Principle REFUTED (ANY holds)
- `ARM_LABEL_BASIS_AXIS_PROJECTION.retrieval.top1 mean >= 0.80` (labels DON'T hurt)
- OR `ARM_RANDOM_BIPOLAR.retrieval.top1 mean <= 0.65` (random doesn't work; breaks emergent claim)

Verdict: `HARD_FAIL_REFUTED`

### Inconclusive / partial
- `HARD_PASS_PARTIAL` if retrieval shows the pattern but composition doesn't
- `MIDDLE_BAND` if bands in between
- `CONFOUND_CHECK` if C2 within-cat cosine ≥ 0.95 (label arm code-degenerate)

## Sanity rails / discipline gates

- **Q-discipline rail** (Fix #28-recurring): any arm with `retr_top1 >= 0.995` flagged `Q_SATURATE`; investigated before declaring victory. Predicted spread is 0.55–0.85; no 1.000 arms expected.
- **C2 confound guard**: `ARM_LABEL_BASIS_AXIS_PROJECTION.within_cat_cos_mean >= 0.95` flags `CONFOUND_CHECK` — code-degeneracy could fake the "labels hurt" signal.
- **Substrate-only assertion**: `_LLM_CALL_COUNTER == 0` asserted before metrics.json write.

## CONFOUND_AUDIT (mandatory per Fix #26)

**C1 axis-projection implementation bug**: cone-collapse could be due to bad noise scale or wrong subspace partition.
- **Mitigation:** `NOISE_SCALE_AXIS = 0.05` matches the working reference cell `exp_substrate_label_driven_anisotropic_encoder_v1.py`. Subspace partition uses contiguous bands identical to the reference. Sparse-bipolarization at f=SPARSE_F matches the other arms.

**C2 degenerate codes in label arm**: if axis-projection produces near-duplicate embeddings within a category, retrieval could fail by code degeneracy (not by "labels hurt").
- **Mitigation:** the cell measures `within_cat_cos_mean` per arm; the verdict flags `CONFOUND_CHECK` if LABEL_BASIS has within-cat cosine >= 0.95. Symmetric noise on every dimension breaks degeneracy.

**C3 capacity-respecting tier issue**: if M_TRIPLES is too close to substrate capacity, all arms saturate.
- **Mitigation:** M = 2400 = 8 per concept; substrate capacity at N=8192 is ~25000 (per CERT-graded measurements). We are at ~10% of capacity. Random-bipolar at this scale should NOT saturate retrieval at 1.000.

## Bias-checklist application

- **BIAS-13** (basis-layer label contamination): the LABEL_BASIS arm tests this DIRECTLY.
- **BIAS-14** (JL-oversatisfaction): V=300 N=8192 → N/V=27, in productive JL regime; NOT saturated like Cell 7's V=12 (N/V=683).
- **BIAS-15** (prior-data mismatch): 10 categories / 300 concepts → 30 per category, balanced (not Zipfian-mismatch).
- **BIAS-Q** (suspect 1.000): predicted spread 0.55–0.85; Q rail guards saturation.

## Routing flow

1. ✅ Author cell + prereg locally
2. ✅ Run `--self-test` (must PASS) — PASSED
3. [pending] Run `--smoke` at local CPU (must PASS per smoke criteria below)
4. [pending] Commit cell + prereg + smoke metrics
5. [pending] Author orchestrator handoff for full dispatch
6. [pending] USER decides remote dispatch

## Smoke PASS criteria

- All 4 arms produce finite metrics (no NaN)
- `ARM_RANDOM_BIPOLAR.retrieval.top1 >= 0.60` (baseline works at smoke scale)
- `ARM_LABEL_BASIS_AXIS_PROJECTION.retrieval.top1 < ARM_RANDOM_BIPOLAR.retrieval.top1` (preview of full-scale prediction)
- `ARM_EMERGENT_*.retrieval.top1 >= ARM_RANDOM_BIPOLAR.retrieval.top1 - 0.10` (emergent works at least near random at smoke scale)

Smoke is NOT a pass for chain-grade; it's a check that the cell-author code runs correctly + predictions directionally hold at small scale.

## Honest assessment plan

After smoke runs:
1. Report all 4 per-arm retrieval + composition numbers (no summary string framing per Fix #28)
2. Report within_cat_cos and cross_cat_cos diagnostics
3. State whether smoke shows directional signal toward principle confirmation OR ambiguity/confound
4. If AMBIGUOUS at smoke → FLAG IT; do not proceed to remote dispatch on inconclusive smoke
5. If C2 confound triggered (label-arm within-cat-cos ≥ 0.95) → investigate code degeneracy before any FULL dispatch
