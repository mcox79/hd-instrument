# Cell H' — biology-native unsupervised anisotropic encoder shotgun (Stage 1.5 encoder commit)

Director formal spec. NOT dispatched. Sequencing: ship after Wave F Cell 1 v3 hub-spoke MRC lands.

Per Cell 7 deepened drill (`notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md`) + USER's basis-vs-use-case principle. ANY-ARM HARD_PASS P_deflated = 0.45.

## Strategic context

1. Cell 7 label-driven encoder LOST to random-bipolar at V=12 (lift=-0.056). Pure-math root cause: JL-oversatisfaction at N/V=683 (33x minimum).
2. USER worry validated: external category labels commit substrate to wrong taxonomy. Brain does NOT use labels for basis construction.
3. ML literature (Mu-Viswanath 2018, Ethayarajh 2019): anisotropy actually HURTS retrieval (cone-collapse) — substrate's primary task. So label-driven encoder may be wrong at ANY V.
4. Right next encoder: biology-native UNSUPERVISED mechanisms; let structure EMERGE from input statistics + graph edges + competition + sparseness.

## Cell anchor

`substrate_unsupervised_anisotropic_encoder_biology_native_v1`

## Lane / routing / config

- Lane 1 (substrate-native; unsupervised)
- Routing: overnight_queue (GPU; matmul-heavy at V=4000 text8 scale)
- Config: N_DIM=8192, V=4000, N_TRAIN=100000, N_HELD=20000, text8 corpus (matches fair_harness rail config), 3 seeds [7,17,23], sparse_f=0.02 (chain-grade primitive)

## Arms (5; all unsupervised; ONE knob = encoder construction mechanism)

### ARM 1: ARM_RANDOM_BIPOLAR_BASELINE (control)
- Isotropic random sparse-bipolar codes
- Same as fair_harness baseline at this regime
- Reproduces unigram floor ~7.74 BPC

### ARM 2: ARM_OLSHAUSEN_FIELD_SPARSE_CODING (V1 analog)
- Sparseness penalty + reconstruction objective on bigram-context windows
- Forward-only SoftHebb approximation (per Moraitis 2022; substrate-native)
- Develops dominant-direction lanes from text8 statistical structure
- No labels; structure EMERGES from co-occurrence patterns

### ARM 3: ARM_DEEPWALK_ON_CONCEPT_KG_GRAPH_EDGES (place-cell analog)
- Uses substrate-KG graph EDGES (not labels) for random-walk-based embedding
- Community structure emerges from connectivity per Stochastic Block Model embedding theorem
- ~50 lines of code per drill estimate
- Crucially: uses the KG's relational structure WITHOUT committing to its taxonomy

### ARM 4: ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_INHIBITION (decorrelation)
- Hebbian feedforward + plastic anti-Hebbian lateral
- Produces sparse independent components per Foldiak 1990
- Substrate-native via sign-flip Hebbian on bipolar outputs

### ARM 5: ARM_KOHONEN_SOM_TOPOGRAPHIC (input-statistics-driven)
- Self-organizing map; competitive learning + neighborhood preservation
- Develops topographic representations from input statistics
- Brain analog: cortical maps (retinotopy, somatotopy)

## Discriminator (load-bearing per Fix #28)

Two metrics per arm:
1. **BPC on text8** (vs fair_harness rail 7.3065) — standard LM metric
2. **SEMANTIC battery A3 generalization** (lift over ARM_RANDOM_BIPOLAR) — substrate-product metric

If ALL arms beat random on A3 → biology-native mechanisms work as a class
If some arms beat but not others → specific mechanism (e.g. DeepWalk) is the lever
If none beat random → either anisotropy doesn't help at this V (revisit Mu-Viswanath finding) OR substrate at V=4000 needs different scale

## HARD bands

- **HARD_PASS_FULL**: any biology arm BPC ≤ 6.95 AND A3 lift_vs_random ≥ +0.10 AND CV ≤ 0.05 (chain-grade-eligible)
- **HARD_PASS_PARTIAL**: any biology arm BPC ≤ 7.30 AND A3 lift ≥ +0.05 (signal but not chain-grade)
- **HARD_FAIL**: NO arm beats random by ≥ +0.05 on A3 OR all arms BPC ≥ 7.40

## By-construction-saturation guards (active)

- Random-bipolar baseline must NOT saturate SEMANTIC A3 (config V=4000 ensures headroom; Cell 3/Cell 7 V=12 was the saturation regime)
- Each biology arm self-reports anisotropy metric (eigenvalue spread, cosine spread among learned codes) so Skunkworks can verify the mechanism actually built anisotropic structure (not just produced numbers)

## Cross-thread

- Cell 7 deepened drill: this cell IS the drill's primary recommendation
- USER's basis-vs-use-case principle: this cell is BASIS-only (no labels); labels can ride on top at task readout
- Wave F Cell 1 hub-spoke v3 MRC: complementary; tests federation OF spokes, this cell tests WHICH ENCODER MECHANISM
- Mu-Viswanath anisotropy-hurts-retrieval: if all arms fail, validates that substrate-product (retrieval) benefits from less anisotropy not more

## Sanity rails

- ARM_RANDOM_BIPOLAR at sanity_T=0.05 lambda=0.1 must reproduce fair_harness 7.3065 within ±0.05 (provenance gate)
- DeepWalk arm must produce diversity_cv ≥ 0.05 (proves graph structure was used; not silent fallback to random)
- Foldiak arm must produce decorrelation cv ≥ 0.10 (proves lateral inhibition fired)

## Timeout

5400s (5x random baseline; 4 biology arms × ~1.5x random)

## Sequencing recommendation

1. Wait for Wave F Cell 1 v3 hub-spoke MRC landing (in flight)
2. If hub-spoke v3 HARD_PASS → maybe defer Cell H' (federation might be sufficient)
3. If hub-spoke v3 MIDDLE_BAND/FAIL → ship Cell H' (within-spoke encoder quality needs unsupervised refinement, not federation)

USER decides timing.

## Expected outcome (drill priors)

- Any-arm HARD_PASS: 0.45
- DeepWalk best arm: 0.35
- Olshausen-Field best arm: 0.30
- Foldiak best arm: 0.25
- Kohonen SOM best arm: 0.20
- All-arms HARD_FAIL: 0.15

## Status

Spec only. Awaiting USER green-light + Wave F Cell 1 landing.
