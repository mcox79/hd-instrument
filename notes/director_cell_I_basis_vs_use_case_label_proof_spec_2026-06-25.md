# Cell I — substrate_basis_vs_use_case_label_layer_discriminator_v1

The PROOF experiment for USER's basis-vs-use-case principle (Principle O) + engineered-vs-emergent pattern (drill 5x). Director spec; NOT dispatched. Wait for prerequisites.

## Why this cell

The drill found 5-field convergence supporting the principle. But our 5 supporting data points each have confounds (BIAS-13/14/15). A clean 2×3 design with same labels at both layers + matched data + JL-discriminating regime would prove or refute the principle definitively.

## Cell anchor

`substrate_basis_vs_use_case_label_layer_discriminator_v1`

## Lane / routing / config

- Lane 1 (substrate-native concept-KG)
- Routing: remote_cpu_queue (CPU-feasible at V=300)
- Config: N=8192, **V=300** (JL-discriminating regime: N/V=27, NOT in Cell 7's saturated N/V=683 nor under JL margin), V_categories=10 (30 instances per category), V_predicates=8, M=2400 triples (8/concept), 5 seeds (statistical power)
- text8-derived OR substrate-OWNED concept-KG with explicit category labels

## Arms (6) — 2×3 design

| Arm | BASIS encoder | USE-CASE readout | Hypothesis |
|---|---|---|---|
| ARM_RANDOM_NO_READOUT | random sparse-bipolar | retrieval only | baseline; OK retrieval, chance class |
| ARM_RANDOM_CLASS | random sparse-bipolar | trained W_class on labels | OK retrieval, OK classification |
| ARM_LABEL_BASIS_NO_READOUT | label-driven axis-projection at encoder | retrieval only | HURT retrieval (cone-collapse), chance class |
| ARM_LABEL_BASIS_CLASS | label-driven encoder | trained W_class on labels | HURT retrieval, OK classification (control: "labels work but at wrong layer") |
| ARM_EMERGENT_NO_READOUT | data-driven (DeepWalk OR SoftHebb) | retrieval only | OK+ retrieval, chance class |
| ARM_EMERGENT_CLASS | data-driven | trained W_class on labels | OK+ retrieval, OK classification |

Where "data-driven" = pick the WINNING biology-native arm from Cell H' (DeepWalk or Olshausen-Field or SOM or Foldiak). If Cell H' all-arms HARD_FAIL, this cell is deferred until different biology-native is identified.

## Three measurements per arm (all required for proof)

1. **RETRIEVAL accuracy**: substrate's native task; cosine + cleanup on stored triples; should differentiate BASIS-imposed cone-collapse from random/emergent
2. **CLASSIFICATION accuracy**: use-case readout success; classifier W_class trained on labels; should differentiate "labels-help-at-readout" from "labels-hurt-at-basis"
3. **COMPOSITION accuracy**: substrate-product task; compose-bind-unbind-retrieve through 2-hop; integrated measure

## Pre-registered predictions (HARD bands)

**Principle PROVEN (5 of 6 predictions hold):**
- ARM_RANDOM_NO: retrieval ≥ 0.80, classification ≈ chance
- ARM_RANDOM_CLASS: retrieval ≥ 0.80, classification ≥ 0.70
- ARM_LABEL_BASIS_NO: retrieval ≤ 0.65 (cone-collapse hurts), classification ≈ chance
- ARM_LABEL_BASIS_CLASS: retrieval ≤ 0.65 (same cone-collapse), classification ≥ 0.70 (readout works on broken basis)
- ARM_EMERGENT_NO: retrieval ≥ 0.80
- ARM_EMERGENT_CLASS: retrieval ≥ 0.80 AND classification ≥ 0.70 (best joint score; principle's prediction)

**Principle REFUTED:**
- ARM_LABEL_BASIS_NO retrieval ≥ 0.80 (basis-imposed labels DON'T hurt retrieval)
- OR ARM_LABEL_BASIS_CLASS shows BETTER retrieval than ARM_RANDOM_CLASS (basis-imposed labels HELP)
- OR ARM_RANDOM_CLASS retrieval drops below 0.80 (readout layer somehow hurts basis)

## Discriminators (load-bearing per Fix #28)

- ARM_LABEL_BASIS_NO vs ARM_RANDOM_NO: isolates basis-imposed labels harmful?
- ARM_LABEL_BASIS_CLASS vs ARM_LABEL_BASIS_NO: isolates classifier-readout-can-compensate?
- ARM_EMERGENT_CLASS vs ARM_LABEL_BASIS_CLASS: isolates BASIS choice when USE-CASE is constant
- ARM_RANDOM_CLASS vs ARM_LABEL_BASIS_CLASS: isolates "labels at basis vs readout when both have classifier"
- ARM_EMERGENT_CLASS vs ARM_RANDOM_CLASS: isolates "emergent basis > random basis when both have readout"

## Sanity rails

- ARM_RANDOM_NO retrieval must reproduce Cell 7's ARM_RANDOM_BIPOLAR_BASELINE within ±0.05 at same scale (regime match)
- Classifier per ARM_RANDOM_CLASS must achieve classification ≥ 0.70 (otherwise readout itself is broken)
- All arms use same data, same number of seeds (5), same retrieval/classifier architectures

## Bias-checklist application

- BIAS-13 basis-layer label contamination: the LABEL_BASIS arms test this directly; prediction is they HURT retrieval
- BIAS-14 JL-oversatisfaction: V=300 N=8192 → N/V=27 → in JL-discriminating regime (not saturated)
- BIAS-15 prior-data mismatch: 10 categories vs 300 concepts → roughly aligned (not Zipfian-mismatch)
- BIAS-Q (suspect 1.000): no arm should hit 1.000 at this V; the predicted spread is 0.65 to 0.85

## By-construction-saturation guard

- V=300 chosen to ensure random-bipolar is NOT saturating retrieval (Cell 7's V=12 saturated)
- M=2400 triples = 8/concept; well below substrate's ~25000 capacity at N=8192
- Classifier W_class has explicit train/test split; train on 70%, test on 30%

## Timeout

3600s

## Cross-thread

- Cell H' result determines the EMERGENT arm choice (which biology-native mechanism)
- Cell 7 finding (label-driven lost to random) → predicts ARM_LABEL_BASIS_NO will hurt
- Cell 5 HYBRID 1.000 = MM → predicts ARM_LABEL_BASIS_CLASS will inherit label-driven basis collapse
- Drill 5x: theoretical framing for the principle

## Strategic implication

If HARD_PASS (principle proven):
- Stage 1.5 encoder commit DECIDED: biology-native unsupervised + use-case labels at readout
- All five barriers' encoder requirements unify
- Substrate-product architecture has its first definitive principle

If HARD_FAIL (principle refuted):
- Revisit basis-vs-use-case framing
- Examine specific failure mode (which prediction broke) for new principle
- Worst case: refine the principle to be more nuanced

## Status

NOT dispatched. Awaiting:
1. Cell H' landing → tells us which biology-native arm for EMERGENT slot
2. Cell 2 v4 FREQ_ROUTED landing → optional cross-validation
3. USER green-light + spawn budget

Ready for one-orchestrator-turn dispatch when prereqs land favorably.
