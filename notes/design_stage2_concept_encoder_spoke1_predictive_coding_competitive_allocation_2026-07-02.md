# Stage 2 Spoke 1 — Substrate concept encoder design

**Filed:** 2026-07-02 evening (post-brain-best-in-class strategic pivot)
**Anchor:** `substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1`
**USER anchor 2026-07-02:** brain function is best-in-class reference standard
**Motivation:** substrate's current "concepts" are random-codebook HDs — satisfy only 1 of 6 brain-property criteria. Spoke 1 builds the base of a substrate-owned concept encoder that produces sparse-distributed HDs which EMERGE from data via purely local learning rules (no backprop, no borrowed embeddings).

## What Spoke 1 does (intuitive)

Take raw text → produce sparse-bipolar concept HD via:
1. **Char + positional encoder** (V1 analog): each character bound to its position via HRR bind; bundle for word. Preserves order. Substrate's "sensory front-end" for text.
2. **Predictive coding layer** (cortex analog, Rao-Ballard/Friston): learns to predict its own input from higher-level activity. Residual error updates local weights via Hebbian outer-product. Emergent representation compresses common patterns.
3. **Competitive allocation layer** (winner-take-all, Tonegawa excitability trace): sparse readout — only ~1-3% of dimensions activate per concept. Enforces pattern separation.
4. **Output:** substrate-owned concept HD (bipolar ±1, N=8192, sparse activation).

## Six brain properties — what Spoke 1 targets

| Property | Spoke 1 coverage |
|---|---|
| (1) Emerged from data | ✅ predictive coding learns from stream |
| (2) Sparse-distributed | ✅ competitive allocation enforces sparsity |
| (3) Predictive | ✅ representation directly minimizes prediction error |
| (4) Compositional | ✅ HRR bind primitive baked in (M1.9 K=5 proven) |
| (5) Grounded | ❌ Spoke 4 deferred |
| (6) Continually updateable | ⚠️ partial — online learning yes, but robustness to forgetting is Spoke 3 |

Spoke 1 targets 4 of 6. Spokes 2-4 add the rest.

## Existing pieces to compose

- `hdlab/predictive_coding.py` — Rao-Ballard predict + Hebbian outer-product update; local rules only ✅
- `hdlab/excitability.py` — Tonegawa excitability trace for winner-take-all allocation ✅
- `hdlab/binding.py` — HRR bind/unbind CG-proven ✅

Missing (new for Spoke 1):
- `hdlab/char_positional_encoder.py` — char + position bind for text-to-HD (~100-200 lines new)
- `hdlab/concept_encoder.py` — orchestration composing the above (~500-800 lines new)

## Cell design

**Anchor:** `exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1`

### Arms (5 arms × 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_RANDOM_BASELINE | Random-codebook HDs (no learning) | Control: proves learning is needed |
| ARM_CHAR_TRIGRAM_BASELINE | Existing char_trigram_encoder.py (no learning) | Baseline: bag-word encoder currently in use |
| ARM_PREDICTIVE_ONLY | Char+positional + predictive coding (no competitive allocation) | Ablation: proves competitive allocation matters |
| ARM_COMPETITIVE_ONLY | Char+positional + winner-take-all + Hebbian (no predictive coding) | Ablation: proves predictive coding matters |
| **ARM_FULL_HYBRID** | Char+positional + predictive coding + competitive allocation | LOAD-BEARING (brain-analog) |

### Corpus

**Smoke:** synthetic controlled corpus (2000 sentences over 50 concepts with known semantic structure). E.g., generate sentences like "the cat sat on the mat", "the kitten drank milk", "the airplane flew over the mountain" with known concept-cluster ground truth. Advantages: controlled semantics + fast + reproducible. Disadvantages: synthetic (not real).

**FULL:** 10K Wikipedia first-sentences (real corpus).

### Metrics per arm × seed

- `sparse_rate`: mean fraction of dimensions active in output HDs (target: 0.01-0.03 for FULL_HYBRID)
- `cat_kitten_cos`: cosine of concept HDs for "cat" vs "kitten" across their occurrences (target: ≥ 0.4 for FULL_HYBRID; ≈ 0 for RANDOM_BASELINE)
- `cat_airplane_cos`: cosine of concept HDs for "cat" vs "airplane" (target: ≤ 0.1 for FULL_HYBRID)
- `intra_concept_cv`: cv of concept-HD cosine within same concept across contexts (invariance measure; lower = better; target for FULL_HYBRID: < 0.2)
- `n_concepts_stable`: count of concepts where within-concept mean cosine > 0.6 (stable-representation count)
- `arm_digest`: hash of concept-HD table

### HP bands (HP_SCOPE: LOAD-BEARING on ARM_FULL_HYBRID)

**HARD_PASS (target CG):**
- ARM_FULL_HYBRID cat_kitten_cos ≥ 0.4 (semantically-related concepts cluster)
- ARM_FULL_HYBRID cat_airplane_cos ≤ 0.1 (unrelated concepts separate)
- ARM_FULL_HYBRID sparse_rate ∈ [0.01, 0.03] (sparse-distributed constraint satisfied)
- ARM_FULL_HYBRID intra_concept_cv < 0.2 (stable representation)
- ARM_FULL_HYBRID cat_kitten_cos beats BOTH ARM_PREDICTIVE_ONLY AND ARM_COMPETITIVE_ONLY by ≥ 0.15 (composition-lift proven)
- ARM_RANDOM_BASELINE cat_kitten_cos ∈ [-0.05, 0.05] (random doesn't cluster — sanity)
- 3-seed HP; cv across seeds < 0.15

**HARD_FAIL:**
- ARM_FULL_HYBRID cat_kitten_cos < 0.25 (concepts don't cluster at all)
- OR ARM_FULL_HYBRID sparse_rate outside [0.005, 0.10] (sparsity architecture broken)
- OR ARM_FULL_HYBRID does NOT beat both single-mechanism ablations by ≥ 0.05 (hybrid mechanism not composing)

**MIDDLE_BAND:**
- Any target in intermediate range — leads to v2 with tuning (learning rate, sparsity target, hierarchy depth)

### Sanity + integration gates

- ARM_RANDOM_BASELINE cat_kitten and cat_airplane both ∈ [-0.05, 0.05] — pins baseline at chance
- ARM_CHAR_TRIGRAM_BASELINE cat_kitten typically 0.15-0.25 (surface morphological similarity — should be POSITIVE but small)
- Sparse rate ARM_FULL_HYBRID monotonically related to competitive-allocation strength parameter (verify parameter is doing work)

### Substrate primitives called

- `hd_bind` (char × position; word-composition)
- `hdlab.predictive_coding.predict + hebbian_update` (Rao-Ballard local rule)
- `hdlab.excitability.excitability_trace_allocation` (winner-take-all)
- No backprop, no gradient, no global error signal

### CELL-TEMPLATE MANDATORY compliance

Standard: arms_differ_verified (15 unique), except SystemExit before except Exception, tmp_replace metrics, cardinality_ok, HP_SCOPE=LOAD_BEARING on FULL_HYBRID, sparse-rate architectural constraint verified, ASCII-only.

### Compute architecture

- (a) batched-CPU-torch or NumPy; corpus fits in memory; predictive-coding-per-token is the bottleneck
- Per-seed smoke wall estimate: ~2-5 min (2000 sentences × learning-rule ops)
- FULL wall: ~10-20 min (10K sentences)
- Route: local_cpu smoke (USER SMOKE_ONLY_LOCAL); remote_cpu_queue for FULL

### Dispatch prereqs

1. char_positional_encoder + concept_encoder authored + selftests passing (cell author's first task)
2. Prereg SCHEMA-VET (Skunkworks — cell-author files prereg draft, Skunkworks validates)
3. Smoke gate on local_cpu

## Post-verdict routing

**HARD_PASS:** Spoke 1 CG. Extract composed concept_encoder to hdlab (following M1.9 extraction pattern). Fire Spoke 2 (temporal contiguity).

**HARD_FAIL:** file CG_HONEST_NEGATIVE closing this specific composition. Options: (i) different learning-rate schedule, (ii) different sparsity target, (iii) deeper predictive-coding hierarchy (currently flat), (iv) alternative competitive-allocation mechanism.

**MIDDLE_BAND:** file MM_TENTATIVE; v2 with parameter tuning.

## What CG at Spoke 1 unlocks

Even Spoke 1 alone (predictive coding + competitive allocation on char+positional) is a real deliverable:
- Substrate has learned concept HDs from data (emerged, not designed)
- Sparse-distributed representation (architectural constraint satisfied)
- Semantically similar concepts cluster (structure emerges)
- Compositionally usable via HRR bind (M1.9 mechanism becomes REAL, not random-codebook proof)

USER's Stage 2 substrate-load ritual becomes semantically-grounded — "storage strategy" query hits SHARDED atom via concept similarity, not word overlap.

Spokes 2-4 add invariance, one-shot learning, and grounding — but Spoke 1 alone is the load-bearing foundation.
