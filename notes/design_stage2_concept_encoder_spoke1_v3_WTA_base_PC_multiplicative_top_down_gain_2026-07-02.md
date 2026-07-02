# Stage 2 Spoke 1 v3 — WTA base + PC multiplicative top-down gain

**Filed:** 2026-07-02 late evening (post-5x-drill convergence: neuroscience + physics/spin-glass + non-equilibrium thermo all point same way)
**Anchor:** `substrate_concept_encoder_spoke1_v3_WTA_base_PC_multiplicative_top_down_gain`
**Motivation:** v1 + v2 empirical results show HYBRID ≈ COMPETITIVE_ONLY (gap delta 0.010 within cv 0.377). Three independent domain drills converge on diagnosis: our composition order is inverted. Brain-analog + rigorous stat-mech + non-equilibrium thermo all agree: PC is NOT a concept-forming mechanism at the sensory-to-semantic layer; competitive-Hebbian is. PC is a top-down modulator applied ON TOP.

## Intuitive summary (no jargon)

**What the empirical evidence + literature says.** In real brains, when neurons form CONCEPT representations (like a "cat" cell in temporal cortex), the mechanism doing the work is competitive Hebbian learning — neurons compete for the input, winners strengthen their connections, losers get suppressed, and gradually sparse specific representations emerge. This is Kohonen self-organizing maps, cerebellum granule cells, Quiroga concept cells, barrel cortex organization — ALL competitive-Hebbian, none PC-driven.

Predictive coding IS a real brain mechanism — but it operates at a DIFFERENT layer. PC modulates what already-formed concept representations do based on expectation and context. Like: "given I expect to see a cat given the surrounding context, MODULATE the strength of cat-neuron activation." It doesn't CREATE the cat concept; it BIASES it.

Our v1 + v2 asked PC to do work it's not evolved (or theoretically justified) to do — form concept representations from scratch. Empirically that failed cleanly: PC + WTA composition ≈ WTA alone.

**What v3 does.** Invert the composition:
1. Competitive-Hebbian forms the concept representation base (unchanged from v2's COMPETITIVE_ONLY arm, which lands stably)
2. Predictive coding runs on TOP as a multiplicative gain: for each concept, PC predicts expected activation from context; if prediction is high, GAIN the WTA output; if low, DOWNSCALE
3. PC contributes context-sensitivity and expectation-modulation without needing to form representations itself

Brain-analog: L5 cortex feedback → L2/3 competitive activation (Bastos 2015 canonical microcircuit; roughly).

## Convergent evidence from 5x drill (3 angles reported, 2 pending)

| Drill | Finding | Convergence |
|---|---|---|
| Neuroscience + biology | For concept-encoding domain specifically, competitive-Hebbian forms base; PC is top-down modulation. P=0.85 across two hypotheses that composition is inverted. | ✅ recommend WTA base + PC gain |
| Physics + stat-mech (spin-glass) | Rigorous capacity gains come from energy-function/interaction-order axis (Krotov-Hopfield polynomial, Ramsauer modern). No paper takes PC term added to spin-glass Hamiltonian and derives α_c increase. Salvatori 2021 hierarchical PC gain is empirical retrieval, not capacity theorem. | ✅ PC-in-flat-composition unsupported by capacity theory |
| Physics + non-equilibrium thermo | No evidence iterative PC accesses thermodynamic resources single-shot WTA can't. Landauer/Sagawa-Ueda error correction adds dissipation cost, not extracts advantage. | ✅ cuts against PC-as-activation-driver |
| Math + info theory | Sub-drills firing; results pending | (pending) |
| ML/AI literature | Sub-drills firing; results pending | (pending) |
| Empirical ablation (a51e4c) | Sub-drills firing; results pending | (pending) |

Three of five drills already converge. If any pending drill has counter-evidence (e.g., empirical ablation finds a specific PC-config where HYBRID beats COMPETITIVE by ≥0.10), we should weigh it. Otherwise v3 direction is well-supported.

## v3 mechanism design

### Architecture (composed from existing hdlab modules)

```
Raw text → char_positional_encoder → surface_hd
    ↓
Competitive-Hebbian layer (WTA base — same as v2 COMPETITIVE_ONLY arm):
    - k_largest-then-sign sparsification (k=~2%)  
    - Hebbian outer-product update on winners
    - Result: sparse-bipolar concept HD (base representation)
    ↓
PC top-down gain (new for v3):
    - PC layer predicts expected WTA output given surrounding context HD
    - Prediction error residual computed
    - Gate: multiplicatively SCALE each dim of WTA output by (1 + gain * (predicted_activation - baseline))
    - Result: WTA representation MODULATED by PC context prediction
    ↓
Concept HD (sparse-bipolar, PC-modulated, N=8192)
```

Key architectural difference from v1/v2: PC does NOT drive WTA activation. WTA operates on surface features alone (competitive-Hebbian). PC operates on WTA output as a multiplicative gain based on context-prediction.

### Existing pieces to compose

- `hdlab/char_positional_encoder.py` — surface HD encoding (from v1)
- `hdlab/binding.py` — HRR bind (proven)  
- `hdlab/predictive_coding.py` — PC primitives (repositioned: now applied at output layer, not input)
- Winner-take-all sparsification (from v1 cell; k-largest-then-sign — proven mechanism vs 2026-06-23 naive-sampling)

New for v3:
- Multiplicative-gain composition function (small, ~50 lines): `apply_pc_gain(wta_output_hd, pc_prediction_hd, gain_scale)` — scales WTA active dims up/down based on PC prediction match/mismatch

### Arms (6 arms × 5 seeds = 30 units expected)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_RANDOM_BASELINE | Random codebook | Control: proves learning is needed |
| ARM_CHAR_TRIGRAM_BASELINE | Existing char_trigram encoder | Baseline: bag-word ceiling |
| ARM_WTA_ONLY_TUNED | Competitive-Hebbian only, sparsity=2% (matches v3 target exactly) | Same-mechanism collapse hypothesis test |
| ARM_PC_UNDER_WTA_V2_REPRO | Reproduces v2 HYBRID (PC drives activation → WTA sparsifies) | Comparator: shows the v2 architecture |
| **ARM_WTA_BASE_PC_GAIN** | LOAD-BEARING: WTA forms base + PC as multiplicative top-down gain | Brain-analog composition |
| ARM_NAIVE_WTA_SAMPLING | 2026-06-23 falsified mechanism (retained from v2) | Falsified-baseline comparator |

### HP bands

**HARD_PASS (target CG):**
- ARM_WTA_BASE_PC_GAIN cat/kitten gap ≥ ARM_WTA_ONLY_TUNED gap + 0.10 (PC gain earns complexity)
- OR ARM_WTA_BASE_PC_GAIN context-dependent-cosine variance (measured across contexts) is LOWER than ARM_WTA_ONLY_TUNED by ≥ 0.10 (PC adds context-invariance without breaking discrimination)
- ARM_WTA_BASE_PC_GAIN sparse_rate ∈ [0.01, 0.03]
- ARM_WTA_BASE_PC_GAIN beats ARM_NAIVE_WTA_SAMPLING by ≥ 0.15 (progress vs 2026-06-23)
- All 5 seeds independently pass; cv across seeds < 0.20

**HARD_FAIL:**
- ARM_WTA_BASE_PC_GAIN gap < ARM_WTA_ONLY_TUNED gap (PC gain HURTS)
- OR sparsity architectural break
- OR intra-context-variance identical to WTA_ONLY (PC gain does nothing)

**MIDDLE_BAND (partial):**
- ARM_WTA_BASE_PC_GAIN gap ∈ [WTA_ONLY_gap, WTA_ONLY_gap + 0.10) (PC gain neutral to weak)
- Would file as: "PC gain doesn't meaningfully earn complexity at Spoke 1 layer; defer PC to Spoke 2 temporal contiguity per drill recommendation"

### The critical honesty

**Under brain-best-in-class, MIDDLE_BAND on v3 is a defensible outcome.** If WTA_BASE_PC_GAIN doesn't meaningfully beat WTA_ONLY, that itself is a real finding: PC's earn-complexity role at the concept-encoding LAYER is not present in HD substrate. That's consistent with brain evidence for concept encoding specifically. In that case, ship WTA_ONLY as Spoke 1 v3 primitive and reposition PC for Spoke 2 (temporal contiguity — MMN-analog domain where brain evidence predicts PC clearly wins).

**Under brain-best-in-class, HARD_PASS on v3 would also be a real finding** — it would mean PC-as-gain is a real substrate-owned mechanism that lifts concept encoding beyond competitive-Hebbian alone. Both outcomes are honest.

## Position in program

- If v3 HARD_PASS: WTA + PC-gain composed encoder is Spoke 1 primitive. Extract to `hdlab/concept_encoder.py`. Fire Spoke 2 temporal contiguity (Foldiak trace) which composes on top.
- If v3 MIDDLE_BAND: Spoke 1 primitive is competitive-Hebbian alone (WTA_ONLY_TUNED). Extract to `hdlab/concept_encoder.py`. Fire Spoke 2 which reintroduces PC in the correct temporal-contiguity role.
- If v3 HARD_FAIL: PC gain HURTS at concept-encoding layer — actively worse than WTA_ONLY. Ship WTA_ONLY as Spoke 1 primitive; defer PC. Same downstream as MIDDLE_BAND but with stronger evidence PC belongs at a different layer.

**All three outcomes advance Stage 2** — none are stuck. The point of the drill was to know which outcome is expected, not to shortcut to one.

## Dispatch prerequisites

1. Confirm convergence: at least 3 of 5 drills point WTA-base + PC-gain (or PC-deferred) direction (currently 3 of 5 already)
2. Empirical drill (a51e4c) result — if it shows a specific PC-config where HYBRID beats WTA meaningfully, weigh vs. literature convergence
3. USER approval of the v3 direction
4. Skunkworks SCHEMA-VET on the prereg

## Estimated timeline (once dispatch fires)

- Cell authoring: ~30-45 min (hdi_exp_dev; substantial changes from v2 in composition function)
- Smoke on local_cpu: ~5-15 min
- SCHEMA-VET: ~5 min (Skunkworks)
- If HP: extract hdlab/concept_encoder.py (~30-60 min following M1.9 pattern)
- FULL dispatch: not required for Spoke 1 v1 verdict (smoke HP is sufficient to advance); FULL for scale verification could be parallel to Spoke 2 launch

Total: ~1-2 hours from USER approval to Spoke 1 v3 verdict.
