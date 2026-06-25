# RESEARCH (Director): biology-native unsupervised anisotropy mechanisms — substrate-native replication recipes, NO LABELS

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** USER course-correction mid-2x-drill: "on cell 7 - we need more drills. I'm most concerned about these labels locking us into particular directions. Are there other ways to do this we haven't thought about? How exactly does biology do it and can we replicate and how?" Per USER ask: deep-dive biology's mechanisms with substrate-native replication recipes; expand graph-edges-vs-label-taxonomy dimension; replace Cell 7 v2 proposal with biology-native shotgun cell.
**Discipline:** 0.20 deflation novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior; Fix #28 default UNDER-claim; ASCII only; no cell dispatches authorized.
**Referent verifications performed:**
- USER course-correction text quoted verbatim above (from system-reminder mid-conversation).
- Substrate Store coverage check: SoftHebb (exp_encoder_dual_gain_softhebb_v1 present), Predictive Coding (exp_pc1 + exp_substrate_owned_predictive_coding_encoder_v1), BCM (research_drill_bcm_snr_vs_polynomial_p_2x 2026-06-04), sparse coding (research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x 2026-06-04). Foldiak anti-Hebbian, Kohonen SOM, Slow Feature Analysis, Linsker InfoMax, DeepWalk-on-substrate-KG: NOT in Store as substrate-native chain-grade tests (search did not surface specific cells under those names).
- f=0.02 sparse k-WTA chain-grade rail confirmed across 5+ Store cells per prior drill (`notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`).
- Cell 4 multihop_consolidation HARD_PASS confirms substrate has consolidation primitive — relevant to CLS architecture proposal in section 9.

---

## 0. The core distinction (per USER's worry, stated up front)

| Aspect | LABEL-DRIVEN (Cell 7 v1 approach) | GRAPH-EDGES (DeepWalk family) | UNSUPERVISED-SPARSE-CODING (V1 family) |
|---|---|---|---|
| What it uses | Hand-engineered category names (animal / color / royal) | Observed relations (cat is_a animal) | Raw input statistics (bigram context windows) |
| Source of structure | EXTERNAL taxonomy imposition | EMERGENT from connectivity | EMERGENT from input statistics |
| Brain analog | Weak; ATL labels develop AFTER unsupervised sensory tuning | Place-cell development via path traversals | V1 oriented edges via Olshausen-Field |
| Taxonomy commitment risk | HIGH | LOW (taxonomy emerges from data) | NONE (no taxonomy) |
| Substrate-product alignment | RED FLAG per USER course-correction | GOOD | EXCELLENT |
| Failure mode | Prior commits to wrong cuts | Inherits whatever bias the graph has | Slow to converge; needs natural-image-equivalent input |

**Key claim:** brain's anisotropic representations come from MECHANISMS 1, 2, 3, 4, 5, 6, 7, 8 below (all unsupervised). NONE of them are label-driven. USER's worry is biologically correct.

---

## 1. Olshausen-Field sparse coding — V1 oriented receptive fields

**How biology does it:** V1 (primary visual cortex) develops oriented Gabor-like receptive fields in critical period via sparse-reconstruction unsupervised learning on natural-image statistics (Olshausen-Field 1996, Nature 381:607-609). Mechanism: each neuron tries to reconstruct its input from a small number of active basis functions; sparseness penalty drives the dictionary toward independent components. Result: a basis where each element corresponds to a localized oriented edge — NO category labels involved.

**Can substrate replicate it?** YES. Substrate already has bipolar f=0.02 sparse codes (chain-grade rail). Missing piece: explicit RECONSTRUCTION LOSS training.

**Substrate-native recipe:**
```
For each text8 bigram-context window of length 10:
  x = sum-aggregate of token embeddings in window  (300-dim from char-trigram or random init)
Train 1-layer encoder W (300 -> 8192) with loss:
  L = lambda * ||x - W^T sigma(W x)||^2          # reconstruction
      + (1-lambda) * ||sigma(W x)||_1            # sparseness
  where sigma is hard k-WTA at f=0.02 (~164 active per 8192)
Update via SGD or forward-only Hebbian approximation (SoftHebb-style for substrate-native)
```

Key knobs: lambda=0.5 default; window size 10 (text8 bigram-LM context); 100k windows for training; 3 seeds.

**P_deflated working at substrate scale:** 0.45 (raw 0.55, deflated 0.20, +0.10 brain prior STRONG; cap not invoked at 0.45). Risk: Olshausen-Field has never been tested on TOKEN-context windows in Store; only image-patch evidence exists in literature. Discriminating regime: BPC <= 7.30 AND A3 lift_vs_random >= +0.10 at V=4000.

**Cell spec contribution:** ARM_OLSHAUSEN_FIELD in Cell H (section 9).

---

## 2. BCM rule (Bienenstock-Cooper-Munro) — sliding-threshold Hebbian

**How biology does it:** Bienenstock-Cooper-Munro 1982: a Hebbian-like plasticity rule where the sign of synaptic change FLIPS based on whether postsynaptic activity is above or below a time-averaged threshold. Below threshold = LTD (long-term depression); above threshold = LTP. The sliding threshold produces BISTABILITY in synaptic strengths, driving the synapse population toward INDEPENDENT components rather than redundant copies. This is what makes orientation columns DIFFERENTIATE in V1 — without it, all neurons would tune to the same dominant input direction.

**Can substrate replicate it?** YES. Substrate has BCM-flavored Hebbian primitives per `research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md` (polynomial-p factorial cell exp_substrate_polynomial_p4_bcm_factorial_rung1_v1_n512 already in Store).

**Substrate-native recipe:**
```
For each input-output pair (x, y) where y = sigma(W x) at f=0.02 sparsity:
  threshold_i = exponential moving average of y_i^p, time constant tau (e.g. p=2, tau=1000)
  delta W_ij = eta * y_i * (y_i - threshold_i) * x_j   # sign FLIPS at threshold_i
Repeated over corpus; encoder weights converge to independent components.
```

**P_deflated working at substrate scale:** 0.35 (raw 0.45, deflated 0.20, +0.10 brain prior; cap not invoked). Substrate already has cells testing this; the gap is INTEGRATION with anisotropic-encoder construction at V=4000 scale.

**Cell spec contribution:** could be folded into ARM_OLSHAUSEN_FIELD as an UPDATE RULE choice (replace SGD with BCM); not a separate arm.

---

## 3. Predictive coding hierarchy (Rao-Ballard)

**How biology does it:** Rao-Ballard 1999, Nature Neuroscience 2:79-87: cortical hierarchy uses top-down predictions and bottom-up residuals (prediction errors). Each layer predicts the activity of the layer below; layer below sends only the RESIDUAL (the unexplained part) up. Hierarchical anisotropy emerges from PREDICTION ERROR DYNAMICS — features in upper layers are exactly those that capture the unexplained variance in lower layers, by construction.

NO category labels involved. Top-down predictions emerge from data statistics.

**Can substrate replicate it?** Substrate has PARTIAL coverage: exp_pc1_predictive_coding_residual_gate_v1 + exp_substrate_owned_predictive_coding_encoder_v1 in Store. Status: smoke-only; not yet chain-grade at V=4000.

**Substrate-native recipe (extending existing Path-C predictive coding work):**
```
Layer 1: encoder W_1: token -> N=8192 sparse-bipolar
Layer 2: encoder W_2: residual of layer 1 -> M=4096 sparse-bipolar
Layer 3: encoder W_3: residual of layer 2 -> K=2048 sparse-bipolar

Training (forward-only, no backprop):
For each token x in sequence:
  prediction_1 = W_top_down_1 . hidden_2
  residual_1 = x - prediction_1
  hidden_1 = sparse_kWTA(W_1 . residual_1)
  ... (recurse to layer 3)
Hebbian update: delta W_l = eta * residual_l * hidden_l^T
```

This is a substrate-native implementation of Rao-Ballard with forward-only Hebbian updates (no backprop), preserving substrate's local-rule discipline.

**P_deflated working at substrate scale:** 0.40 (raw 0.50, deflated 0.20, +0.10 brain prior; cap not invoked at 0.40). Risk: existing PC cells are smoke-only; chain-grade evidence at V=4000 missing.

**Cell spec contribution:** ARM_HIERARCHICAL_PC in Cell H (section 9, as an OPTIONAL 6th arm — sequence behind 5-arm shotgun if compute permits).

---

## 4. Foldiak anti-Hebbian lateral inhibition — decorrelation

**How biology does it:** Foldiak 1990, Biological Cybernetics 64:165-170: lateral inhibition between neurons in the same layer produces DECORRELATED outputs. Anti-Hebbian update on the lateral weights drives outputs to be independent of each other. Result: sparse independent components emerge from a Hebbian-trained encoder + anti-Hebbian lateral connections, WITHOUT any reconstruction loss.

This is an ALTERNATIVE to Olshausen-Field for producing the same sparse-independent-components result.

**Can substrate replicate it?** YES. Substrate has lateral-inhibition primitives via k-WTA (k-Winners-Take-All implements hard lateral inhibition). Foldiak adds SOFT anti-Hebbian update on lateral weights, which is implementable as sign-flip Hebbian on bipolar outputs.

**Substrate-native recipe:**
```
Forward weights W (token -> N=8192), trained with standard Hebbian:
  delta W_ij = eta_f * y_i * x_j
Lateral weights U (N x N, but only between sparse-active pairs ~ N * f^2 connections),
  trained with anti-Hebbian:
  delta U_ij = -eta_l * y_i * y_j  (for i != j)
Forward pass:
  y = sparse_kWTA(W x - U y)  (Hopfield-like recurrent dynamics until convergence)
```

**P_deflated working at substrate scale:** 0.40 (raw 0.50, deflated 0.20, +0.10 brain prior; cap not invoked at 0.40). Risk: recurrent dynamics add compute cost; convergence at substrate scale (N=8192) not yet validated in Store.

**Cell spec contribution:** ARM_FOLDIAK_ANTI_HEBBIAN in Cell H (section 9).

---

## 5. Drosophila MB k-WTA sparse fan-in — Litwin-Kumar 2017

**How biology does it:** Drosophila mushroom body Kenyon cells receive ~5% activation via sparse fan-in projections from olfactory projection neurons (Caron 2013, Litwin-Kumar 2017). The sparse fan-in is RANDOM (not learned) — but the SPARSITY itself creates anisotropic structure by EXPANSION RECODING: ~50 inputs project to ~2000 KCs with sparse random connectivity, producing a representation that is decorrelated and dimensional-expanded.

This is a SUBSTRATE-NATIVE PRECEDENT for "structure WITHOUT labels via sparse projection." Substrate already has f=0.02 sparsity chain-grade.

**Can substrate replicate it?** ALREADY DONE. The Anisotropy Rescue ARM A from 2026-06-21 implemented K=5 sparse fan-in expansion (per `research_to_skunkworks_PREREG_anisotropy_rescue_4arm_2026-06-21.md`). Landed MIDDLE_BAND — broke rank-1 anisotropy collapse but didn't reach chain-grade.

**Substrate-native recipe (extending existing K=5 work):**
```
Per token: project to N=8192 via sparse random matrix R with exactly K=5 non-zero entries per output
Output: sparse-bipolar at f=0.02 via k-WTA on |R . x|
```

This is RANDOM projection with structural sparsity constraint — preserves JL guarantees while adding biological-grounded fan-in pattern.

**P_deflated working at substrate scale:** ALREADY MIDDLE_BAND at 2026-06-21. Direct revival shot: combine K=5 sparse fan-in WITH Olshausen-Field reconstruction loss to get BOTH the brain-grounded sparsity pattern AND the structured-anisotropy training signal.

**Cell spec contribution:** can be folded into ARM_OLSHAUSEN_FIELD as a CONNECTIVITY CONSTRAINT (replace dense W with K=5 sparse W); not a separate arm.

---

## 6. Self-organizing maps (Kohonen SOM)

**How biology does it:** Kohonen 1982; biological analog is topographic maps in cortex (tonotopy in A1, retinotopy in V1, somatotopy in S1). Competitive learning + neighborhood preservation produces TOPOGRAPHIC representations where nearby neurons code for nearby input features. NO labels involved — topography emerges from input statistics + competition.

**Can substrate replicate it?** YES. Substrate-native SOM on bipolar HD vectors:

**Substrate-native recipe:**
```
Initialize: N=8192 nodes, each with random bipolar codebook entry W_i (N-dim)
For each input x:
  winner = argmax_i (W_i . x)   # nearest-neighbor competition
  neighborhood_radius = r(t)    # shrinks over training
  for i in neighborhood(winner, r(t)):
    W_i = sign(W_i + eta(t) * (x - W_i))  # bipolar update
```

Output for token x: the WINNER index becomes a 1-hot code; OR the top-k=164 winners (f=0.02) becomes a sparse-bipolar code that PRESERVES TOPOLOGY of the input space.

**P_deflated working at substrate scale:** 0.30 (raw 0.40, deflated 0.20, +0.10 brain prior; cap not invoked). Risk: SOM at N=8192 nodes has SLOW training; substrate has no prior SOM cell in Store.

**Cell spec contribution:** ARM_KOHONEN_SOM in Cell H (section 9).

---

## 7. Slow Feature Analysis (Wiskott-Sejnowski)

**How biology does it:** Wiskott-Sejnowski 2002: features that change SLOWLY over time are more informative than features that change rapidly (slow features = invariances; rapid features = noise). Place cells, head-direction cells, grid cells all emerge from this principle — they encode features that change SLOWLY as the animal navigates.

NO labels involved. Slowness IS the prior.

**Can substrate replicate it?** YES. Substrate has SEQUENTIAL data (text8 token stream) — slow features are exactly the right prior for substrate-as-LM.

**Substrate-native recipe:**
```
For each token sequence x_1, x_2, ..., x_T:
  Encode each token: y_t = sigma(W x_t) at f=0.02
  Loss = lambda * mean_t ||y_t - y_{t-1}||^2     # SLOWNESS
       + (1-lambda) * (per-feature variance constraint - 1)^2   # avoid trivial solutions
Update via forward-only Hebbian approximation or SGD.
```

**P_deflated working at substrate scale:** 0.35 (raw 0.45, deflated 0.20, +0.10 brain prior; cap not invoked at 0.35). Risk: SFA on text8 token sequence has ZERO Store evidence; slowness prior may not be strong enough for text (text changes character-by-character; slow features may be just unigram statistics).

**Cell spec contribution:** ARM_SFA in Cell H (section 9, optional 5th arm).

---

## 8. Linsker InfoMax — maximize mutual information

**How biology does it:** Linsker 1988, IEEE Computer 21:105-117: maximize mutual information I(input; output) under local processing constraints. Produces feature maps that capture maximally informative input statistics. This is the ROOT principle underlying many of the above (Olshausen-Field, Foldiak all approximate InfoMax under different constraints).

**Can substrate replicate it?** YES via local Hebbian + adaptation. The trick: InfoMax at the output is achieved by MATCHING OUTPUT VARIANCE to maximum-entropy distribution (uniform on bipolar = exactly the f=0.02 sparse-bipolar codes substrate uses).

**Substrate-native recipe:**
```
Encoder W trained with:
  delta W_ij = eta * (y_i - <y_i>) * (x_j - <x_j>)   # Hebbian on mean-centered
  Plus adaptation: rescale each y_i so its time-averaged activation = f=0.02
```

**P_deflated working at substrate scale:** 0.40 (raw 0.50, deflated 0.20, +0.10 brain prior; cap not invoked at 0.40). This is essentially a substrate-native unification of items 1, 2, 4 above under the InfoMax umbrella.

**Cell spec contribution:** subsumed by ARMs 1, 4 in Cell H.

---

## 9. Cell H proposal: substrate_unsupervised_anisotropic_encoder_v1 (5-arm shotgun)

**Cell:** `substrate_unsupervised_anisotropic_encoder_biology_native_v1`

- **Path:** `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py` (to author)
- **Prereg:** `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_v1.md` (to author)
- **Queue:** `overnight_queue` (GPU; 5 arms x 3 seeds at V=4000 text8 scale)
- **Timeout:** 10800s (3 hr)
- **Config:** N=8192, V_concepts=4000 (real text8 vocab), 3 seeds, eval on text8 LM-BPC + SEMANTIC battery (A3 generalization)
- **5 arms (ALL UNSUPERVISED, NO category labels):**
  - ARM_RANDOM_BIPOLAR_BASELINE (control)
  - ARM_OLSHAUSEN_FIELD_SPARSE_CODING (V1 analog; sparse-reconstruction loss on bigram context; section 1)
  - ARM_DEEPWALK_ON_CONCEPT_KG (graph-edges WITHOUT labels; section "E" of companion drill)
  - ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_INHIBITION (decorrelation via anti-Hebbian; section 4)
  - ARM_KOHONEN_SOM_TOPOGRAPHIC (input-statistics-driven topology; section 6)
- **HARD bands:**
  - HARD_PASS_FULL_STAGE15: at least one of ARMs 2-5 achieves BPC <= 6.95 AND A3 lift_vs_random >= +0.10 AND CV <= 0.05
  - HARD_PASS_PARTIAL: at least one of ARMs 2-5 achieves BPC <= 7.30 (clears fair_harness rail) AND A3 lift_vs_random >= +0.05
  - MIDDLE_BAND: best ARM in BPC (7.30, 7.50) OR A3 lift_vs_random in (0.00, +0.10)
  - HARD_FAIL: NO ARM 2-5 beats ARM_RANDOM_BIPOLAR_BASELINE by >= +0.05 on A3
  - BY_CONSTRUCTION_SATURATION_GUARD: if ALL arms achieve A3 >= 0.95 (saturation), tier as MEASURED_MECHANISM not chain-grade and require larger V (V=16000) follow-up
- **Discriminator (load-bearing):**
  - At least ONE biology-native arm MUST beat random by >= +0.05 at V=4000 for the unsupervised-biology-grounded path to be validated. Otherwise the conclusion is "anisotropy is genuinely encoder-leakage at this scale" and substrate falls back to either Path C predictive coding OR pretrained word2vec rail.
- **Pre-flight gates:** sigma=0 sanity recall=1.000 across all arms (mandatory). HDLAB_EXP_NAME without smoke suffix. Self-test PASS on .venv Python 3.11. Commit-first per pre-dispatch checklist.
- **Expected wall:**
  - ARM_DEEPWALK: ~10 min CPU (gensim Word2Vec on KG walks)
  - ARM_OLSHAUSEN_FIELD: ~30 min GPU (100k bigram-context windows, 1-layer encoder)
  - ARM_FOLDIAK: ~30 min GPU (recurrent dynamics convergence per token)
  - ARM_KOHONEN_SOM: ~45 min GPU (slow convergence; 200 epochs)
  - ARM_RANDOM_BIPOLAR: ~1 min (control)
  - Total: ~ 90-120 min per seed x 3 seeds = 4.5-6 hr GPU wall.
- **Honest scope caveat:** ARMs 2-5 individually have ZERO Store chain-grade evidence at V=4000 substrate scale. SoftHebb has prior cell but not chain-grade on text8 LM-BPC. PC has smoke-only cells. SFA has zero substrate cells. Olshausen-Field on text-context is novel substrate construction. Foldiak anti-Hebbian on bipolar HD is novel. SOM on bipolar HD is novel. Probability ALL FOUR fail simultaneously is non-negligible.

**P_deflated rollup:**
| Arm | HARD_PASS at V=4000 (BPC AND A3 both) | At-least-MIDDLE_BAND on A3 |
|---|---|---|
| ARM_OLSHAUSEN_FIELD | 0.30 | 0.55 |
| ARM_DEEPWALK_ON_CONCEPT_KG | 0.35 | 0.65 |
| ARM_FOLDIAK_ANTI_HEBBIAN | 0.25 | 0.50 |
| ARM_KOHONEN_SOM | 0.20 | 0.45 |
| **Cell H any-arm HARD_PASS** | **0.45** | **0.75** |
| Cell H all-arms HARD_FAIL | 0.15 |  |

**Per-arm rationale (highest-confidence first):**
- **ARM_DEEPWALK (P=0.35):** highest P because the substrate-KG already EXISTS as a chain-grade artifact (3-domain KG portfolio per MEMORY.md); DeepWalk reuses it. Brain-prior STRONG (place-cell development analog). ML literature CHAIN-GRADE (DeepWalk widely-cited).
- **ARM_OLSHAUSEN_FIELD (P=0.30):** brain-prior STRONGEST (V1 IS the existence proof), but substrate construction is novel (no prior text-context Olshausen-Field cell in Store). Convergence on text8 token-context is the load-bearing risk.
- **ARM_FOLDIAK_ANTI_HEBBIAN (P=0.25):** brain-prior MODERATE (Foldiak less-cited than Olshausen-Field but biologically grounded); substrate construction novel; recurrent dynamics add convergence risk.
- **ARM_KOHONEN_SOM (P=0.20):** brain-prior STRONG (topographic maps everywhere in cortex), but SOM has SLOW convergence and substrate has no prior SOM cell — significant implementation risk at substrate scale.

---

## 10. Cross-thread implications + Director recommendation

**Cell 7 v2 retest at V=4000 (Option 5a in companion drill, label-driven retest):** DROP per USER course-correction. Label-driven path commits substrate to taxonomy chosen from outside; brain doesn't do this; even a positive V=4000 result would be substrate-product RED FLAG.

**Cell H 5-arm biology-native shotgun (this proposal):** RECOMMENDED as Wave E Cell H' replacement for the label-driven Cell 7 v2. P_deflated(at least one arm HARD_PASS) = 0.45. Authorship cost: ~5 days exp_dev work (4 novel arms, each ~150-300 lines). Compute cost: ~5 hr GPU wall.

**Sequencing:**
1. Wave D Cell 1 v3 lands (already in flight) -> identifies whether MRC + diversity-gating + within-spoke quality is the load-bearing issue.
2. If Wave D v3 MIDDLE_BAND or HARD_FAIL, Cell H' becomes the natural follow-up: the within-spoke encoder quality bottleneck likely needs Olshausen-Field-style unsupervised refinement, not federation.
3. If Wave D v3 HARD_PASS, Cell H' becomes optional (federated approach validated); but the encoder question for Barriers 4/5 remains and Cell H' still provides decisive comparison.

**Cross-thread anchor to materials science:** USER's concern about label-driven taxonomy commitment maps cleanly to the materials-science "field-cooled vs spontaneous symmetry breaking" distinction in companion 5x drill. External-field (label) route is FASTER and MORE PREDICTABLE; spontaneous-symmetry-breaking (unsupervised) is SLOWER but produces structure that ACTUALLY MATCHES INPUT STATISTICS. Brain chose the spontaneous route. Substrate-product alignment argues we should too.

**Final standing for Director:**
- Cell H' (this proposal) is the recommended Wave E follow-up to Cell 7 v1 negative landing.
- DO NOT dispatch Cell 7 v2 label-driven retest at V=4000 unless Cell H' HARD_FAILs across all arms.
- Author Cell H' AFTER Wave D Cell 1 v3 lands so ARMs in Cell H' can be informed by Wave D outcome.
- D-prime hybrid (from companion 5x drill Section 3) remains the longer-term Stage 1.5 commit; Cell H' is a DISCRIMINATOR that narrows down which D-prime STEP-2 mechanism (Olshausen-Field vs alternatives) is load-bearing.

**Brain-prior summary:** the brain is the only system that has SOLVED unsupervised anisotropic representation learning at scale. Eight known mechanisms (Olshausen-Field, BCM, Predictive Coding, Foldiak anti-Hebbian, Drosophila MB sparse fan-in, Kohonen SOM, Slow Feature Analysis, Linsker InfoMax) all share the property of NEVER USING EXTERNAL CATEGORY LABELS. Substrate-product alignment with biology argues every Stage 1.5 anisotropy cell from now on should be drawn from these mechanisms or their substrate-native variants. USER's worry about taxonomy commitment is biologically correct and the substrate's architectural commitment to brain-grounded mechanisms should reflect that.

-- Research (Director), biology-native unsupervised anisotropy 3x drill complete
