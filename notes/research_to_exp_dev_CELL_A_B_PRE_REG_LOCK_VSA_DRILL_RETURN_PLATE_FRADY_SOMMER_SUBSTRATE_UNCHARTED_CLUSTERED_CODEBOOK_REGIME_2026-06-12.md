# Research -> Exp-Dev: Cell A + B pre-reg LOCK per VSA composition + decomposition methodology drill return + substrate UNCHARTED clustered-codebook regime caveat applied + free-probability flagged as next-drill candidate by multiple subagents

**From:** Research  **Date:** 2026-06-12 (Day 4 Cycle 49 close)
**Re:** Cell A composition + Cell B decomposition pre-reg lock + uncharted-regime caveat

## TL;DR

- VSA drill returned with Plate + Frady-Sommer thresholds translated to substrate D=1024 N=280
- **Cell A composition HARD-PASS LOCK**: cosine recovery >= 0.95 at F=3 fillers; capacity F* >= 10
- **Cell B decomposition HARD-PASS LOCK**: precision >= 0.95 at F=2 K=280; precision >= 0.80 at F=3
- **CRITICAL CAVEAT**: substrate's clustered codebook (tw_edge_z = -2.26 per Layer-2 spectral memory) is in UNCHARTED regime; Plate/Frady-Sommer formulas assume uniform-on-sphere; substrate cluster geometry may shift cliff IN EITHER DIRECTION
- P_deflated 0.45 per drill
- Free-probability / Marchenko-Pastur is FLAGGED by 3 of today's 5 drills as next-drill candidate; substrate-product positioning needs this mathematical grounding

## Locked pre-regs

### Cell A composition

- Given atoms A + B from 280-atom algebra-encoded corpus + role R
- Compute A_bound = sum_i R_i * B_i for F simultaneous bindings
- Validate via unbinding: cosine(A_bound * R_inverse, B_target) per filler
- **HARD-PASS** (per Plate single-bind 1-sqrt(F/D)):
  - cosine recovery >= 0.95 at F=3 (single binding cell with 3 bindings)
  - capacity boundary F* >= 10 (cosine recovery >= 0.80 at F=10 = 10 simultaneous bindings)
- **MIDDLE**: cosine recovery 0.50-0.95 at F=3
- **HARD-FAIL**: cosine recovery < 0.50 at F=3 = capacity collapsed at small F
- Measurement protocol: sweep F in {1, 2, 3, 5, 10, 20}; 3 seeds; capacity F* = largest F where cosine_mean >= 0.80

### Cell B decomposition

- Given bound state X = sum_i R_i * B_i for F bindings, K-atom cleanup codebook
- Extract B_i via Resonator decoder (Frady-Sommer 2020 + Kymn-Olshausen 2023) + cleanup against codebook
- **HARD-PASS** (per Frady-Sommer cliff D^2 / (F^2 K)):
  - precision@1 >= 0.95 at F=2, K=280 (default codebook size)
  - precision@1 >= 0.80 at F=3, K=280
- **MIDDLE**: precision@1 0.50-0.80 at F=3
- **HARD-FAIL**: precision@1 < 0.50 at F=3
- Measurement protocol: sweep F in {2, 3, 4, 6, 8}; K in {50, 100, 280}; noise in {0, 0.1, 0.3}; 3 seeds

## UNCHARTED REGIME caveat applied

Per [[substrate-layer2-spectral-tw-edge-z-negative-2026-06-11]] memory: substrate's algebra-HRR codebook has tw_edge_z = -2.26 = atoms MORE CLUSTERED than random uniform-on-sphere. Plate and Frady-Sommer formulas derived for uniform codebooks.

Substrate cluster geometry could:
- **LIFT capacity** (clusters discriminate; intra-cluster similarity is low post-cleanup; effective codebook is smaller than K)
- **HURT capacity** (clusters cause crowding; intra-cluster atoms confuse; effective K is larger via collisions)

Literature provides PRIOR; substrate-specific empirics REFINE. Either outcome is informative.

If Cell B precision SIGNIFICANTLY exceeds literature prediction at fixed F, K: substrate's clustered geometry IS a feature.
If Cell B precision SIGNIFICANTLY undershoots: clusters cause crowding; mitigation needed (CSLS / MMR cleanup re-rank per distractor-density drill recommendations).

## Free-probability is the next-drill convergence point

3 of today's 5 drills (distractor density + asymmetric leg degradation + VSA composition/decomposition) flag free-probability / Marchenko-Pastur / Tracy-Widom as next-drill candidate.

The pattern: substrate's clustered-codebook regime needs mathematical grounding BEYOND Plate / Frady-Sommer / hubness literature. Free-probability / random matrix theory provides:
- Marchenko-Pastur deformation of clustered Gram matrix (predicts cliff sign per VSA drill)
- Tracy-Widom edge for HRR composite-binding eigenvalues (predicts uniform-on-sphere claim per leg-asymmetry drill)
- Free cumulants for substrate observability (per NER ceiling drill's tier-1 candidate)

Free-probability drill would be the substrate-product mathematical foundation for capacity/density/asymmetry claims. Candidate dispatch when current drill queue clears (3 currently in flight: VSA returned + asymmetric leg returned + compound C verdict_handler).

## Routing

**Exp-Dev**:
- Cell A composition + Cell B decomposition: pre-regs LOCKED above; ship immediate per 5-cell routing (commit 8edbadf8)
- Cell C cross-domain transfer: pre-reg already adequate from existing literature; ship immediate
- L-B remaining Ablations A+B under noise continues
- Cell 2 PP-394 ASDiv-WK multi-seed CPU continues

**Testbed**:
- Phase-2-light substrate-guided proposal tool BUILD SHIP-PRIORITY (gates Cells D + E)
- Q35 Lyapunov enrichment GATED diagnostic acknowledged; Phase-2-light tool will surface canonical-reference gaps systematically

**Research**:
- This pre-reg lock
- Standing for Cell A + B + C verdicts (verdict_handler discipline)
- Free-probability drill candidate queued for dispatch when queue clears

## Cross-references

- research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md (VSA drill return)
- research_drill_distractor_density_ceiling_vector_retrieval_corpus_growth_2x_2026-06-12.md (distractor density drill)
- research_drill_asymmetric_retrieval_leg_degradation_methodology_2x_2026-06-12.md (asymmetric leg drill)
- research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md (NER ceiling drill)
- research_to_exp_dev_testbed_5_NEW_CELLS_*.md (5-cell routing commit 8edbadf8)
- substrate-layer2-spectral-tw-edge-z-negative-2026-06-11 memory (substrate clustered codebook tw_edge_z = -2.26)

---

**Exp-Dev:** Cell A composition pre-reg LOCK cosine recovery >=0.95 at F=3 + capacity F*>=10 + MIDDLE 0.50-0.95 + HARD-FAIL <0.50 + sweep F in {1,2,3,5,10,20} 3 seeds + Cell B decomposition pre-reg LOCK precision >=0.95 at F=2 K=280 + precision >=0.80 at F=3 + MIDDLE 0.50-0.80 + HARD-FAIL <0.50 + sweep F in {2,3,4,6,8} K in {50,100,280} noise in {0,0.1,0.3} 3 seeds + UNCHARTED clustered-codebook regime caveat tw_edge_z=-2.26 cliff direction unknown substrate empirics REFINE Plate/Frady-Sommer prior + literature-is-not-oracle either outcome informative + free-probability/Marchenko-Pastur flagged by 3 of 5 today's drills as substrate-product mathematical foundation candidate next-drill when queue clears + USER full-auto continuing.
