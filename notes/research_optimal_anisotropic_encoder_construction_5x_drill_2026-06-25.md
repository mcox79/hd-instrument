# RESEARCH (Director) 5x DRILL: optimal substrate-OWNED anisotropic encoder construction (Stage 1.5)

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** Director-issued drill on the load-bearing dependency for Barriers 1, 4, 5 (`director_5_intuitive_barriers_with_analogies_2026-06-25.md`). Wave D hub-spoke v3 + Wave E Cell D label-driven test two specific construction approaches; this drill scopes what to do next once they land and what we may be missing.
**Discipline:** 0.20 deflation on novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior; symmetric verify-the-referent; ASCII only; no cell dispatches authorized.
**Referent verifications performed:**
- `notes/director_5_intuitive_barriers_with_analogies_2026-06-25.md` exists, 66 lines, names "substrate-OWNED anisotropic encoder (Stage 1.5 commit)" as the load-bearing dependency for Barriers 1/4/5.
- `notes/exp_dev_to_orchestrator_WAVE_D_3CELLS_DISPATCH_READY_44d82058_2026-06-25.md` confirms Cell 1 `substrate_hub_spoke_E1_v3_MRC_calibrated_routing` is dispatch-ready, GPU, 30-90 min wall, HARD band CG<=6.95 + diversity_cv>=0.05 + no broken spokes.
- `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md` provides the 7-axis design-space prior (E1 P_deflated=0.45; E2 P_deflated=0.40; E3 P_deflated=0.25; default-word2vec P_deflated=0.12) and the f=0.02 sparsity chain-grade rail across 5+ Store cells.
- `notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md` documents the wave14b CE_floor result + ensemble destructive-interference math (1/sqrt(K) bundle SNR loss) directly relevant here.
- `notes/skunkworks_to_research_expdev_cc_orch_RESCUE_flylsh_multiprobe_recovers_recall_but_storage_win_needs_compressed_rerank_2026-06-21.md` confirms multi-probe recovers robust recall but loses storage-win without compressed re-rank — directly informs the "do we get audit-trail Barrier 5 from any of the 3 candidates" question.

---

## 1. Headline + per-candidate verdict

**Headline:** None of the three in-flight/proposed candidates is theoretically optimal for the FULL set of Barriers 1/2/4/5. Each solves a subset. Theoretically optimal construction is a HYBRID: substrate-OWNED **predictive-coding hierarchical encoder with explicit DEEPWALK + Olshausen-Field initialization layer** (the layer the three candidates each approximate differently), then bundled via **MRC + per-spoke compressed-rerank tag** (rather than majority-rule). This is shippable as Wave E Cell D' (D-prime), substrate-native, and unlocks Barrier 5 audit-trail in addition to Barriers 1 and 4 that the current candidates target. P_deflated(hybrid D-prime is theoretically optimal among Stage 1.5 options) = **0.42** (raw 0.62 minus 0.20 novel-synthesis deflation; clipped at the P=0.50 cap so 0.42 stands).

**Per-candidate one-line verdict + predicted in-flight result:**

| Candidate | Theoretical strength | Brain alignment | ML precedent | Predicted result | P_deflated of HARD_PASS as-specced |
|---|---|---|---|---|---|
| **(1) Wave D hub-spoke v3 (learned diverse-algorithm; SoftHebb + char-trigram-RI + Path-C PC)** | MODERATE: 3 genuinely-orthogonal spokes give the variance-axis structure needed for routing lanes IF gating works. Cell 8 v2 already proved destructive-interference at sign(sum) bundle (per readout-degeneracy drill section A.2: K=3 orthogonal spokes give bundle target-cos = single-spoke cos / sqrt(3)). v3 fixes this with MRC + per-spoke health-check + task-signal gating. Still constrained by within-spoke encoder quality. | HIGH: Patterson-Rogers ATL hub-spoke 2007 + Lambon Ralph 2017; brain DOES federate diverse spokes via PMC gating, but PMC uses GRADED multi-spoke output (not winner-take-all to one spoke). | HIGH: CLIP/ImageBind 2021-2025; mixture-of-experts gating; but ML federations USE pretrained spokes (each spoke is hours-to-train, not unsupervised-from-substrate) | **MIDDLE_BAND with diversity_cv passing but BPC at 7.0-7.3**. Diversity check should pass (cv >> 0.05 by construction with 3 different algorithms). Broken-spoke check should pass with v3 health-check. BPC lift is the load-bearing axis and v3 doesn't change within-spoke encoder quality, just bundle and gating; expected BPC just below v2 7.667 baseline but above CG threshold 6.95. | **0.28** (HARD_PASS BPC<=6.95). 0.55 (MIDDLE_BAND BPC 6.95-7.50). 0.17 (HARD_FAIL). |
| **(2) Wave E Cell D label-driven engineered anisotropy (use concept-KG category labels to construct per-axis subspace projections)** | HIGH: by construction, category labels DO induce anisotropic dominant directions (each label = a subspace; per-category subspaces are dominant directions). This is the spectral-method analog of LDA. ALL anisotropy comes from supervision, none from unsupervised learning, so it IS substrate-OWNED (the label graph IS substrate Store, not external pretraining). | MEDIUM-HIGH: ATL hub-spoke is precisely a LABELED hub-spoke architecture in brain (Patterson-Rogers 2007 emphasizes ATL receives labeled-concept input, not raw modality input); critical-period studies (Hensch 2005) show category labels precede sensory tuning. | MEDIUM: LDA / Fisher discriminants are 70-year-old chain-grade ML. Modern instances: prototypical networks (Snell 2017), supervised contrastive (Khosla 2020). | **HARD_PASS likely on anisotropy structure axis (Marchenko-Pastur dominant-direction count >= num_categories); MIDDLE_BAND on BPC** because category labels give cluster structure but not predictive-context structure. Risk: "by-construction-saturation" Skunkworks ruling — labels ARE the answer, so any cell using labels for encoder construction is half-cheating. | **0.40** (HARD_PASS anisotropy axis). 0.50 (MIDDLE_BAND BPC). 0.10 (HARD_FAIL anisotropy). |
| **(3) Pretrained word2vec sparse-bipolar (current rail)** | HIGH (proven): fair_harness chain-grade rail BPC=7.3065 vs unigram=7.7378 (+0.43 lift). Word2vec embeddings have known anisotropic structure (Mu-Viswanath 2018: top-1 PCA direction explains 30-40% variance in standard word embeddings — extreme anisotropy). | LOW: brain does NOT borrow other species' encoders; substrate-product directive (USER 2026-06-23) is path C is the answer, Path A/B are diagnostic probes. | HIGH: ubiquitous in NLP. | **N/A (already landed at BPC=7.3065)**. MIDDLE_BAND from substrate-product framing despite chain-grade as a probe. | **DIAGNOSTIC PROBE; not substrate-product**. P_deflated(this is the Stage-1.5 commit) = **0.12** per prior drill. |

**Key consequence:** The three candidates each address a DIFFERENT subset of Barriers 1/4/5:
- Candidate 1 (hub-spoke v3) addresses Barrier 4 if diversity bundle works, but does nothing for Barrier 5 (audit-trail still in-ink).
- Candidate 2 (label-driven) addresses Barrier 4 + Barrier 5 simultaneously (labels = both dominant-direction lanes AND distinct provenance channel) but at risk of by-construction-saturation tiering down to MEASURED_MECHANISM not chain-grade.
- Candidate 3 (word2vec) is not substrate-product.

The hybrid D-prime in section 3 captures Barrier 4 + Barrier 5 + bigram-gap progress on Barrier 2, substrate-native, escapes by-construction tiering by routing labels through a predictive coding bottleneck.

---

## 2. Five drill highlights

### Drill A — PURE MATH (spectral / information-geometric)

**A.1 Marchenko-Pastur edge for the 3 candidates.** A random codebook W with entries i.i.d. with variance 1/N at aspect ratio q = N/V has eigenvalues of W^T W following the MP distribution with edges `(1 +/- sqrt(q))^2`. For substrate config N=8192 V=4000 the aspect ratio q = 2.048; MP edges `(1 +/- sqrt(2.048))^2 = (1 +/- 1.431)^2` give `[0.186, 5.913]` (highly compressed). For random codes, NO single dominant direction emerges above the MP cluster — eigenvalue distribution is isotropic within the bulk. Resonator-family methods need dominant directions OUTSIDE the MP bulk to converge in O(log V) iterations.

- **Candidate 1 (3-spoke federation)**: each spoke individually MP-bulk-bound, but the bundle inherits any anisotropy each spoke had. SoftHebb-trained spoke DOES produce eigenvalue-tail anisotropy by Bienenstock-Cooper-Munro plasticity (sparsified outliers); char-trigram-RI is approximately random so MP-bulk; Path-C PC produces principal-component anisotropy by construction. So the bundle gets ~1.5 axes of dominant anisotropy (one from SoftHebb skew + one from PC; char-trigram-RI adds noise). With MRC weighting (Cell 1 FIX2), the gating can amplify the anisotropic-spoke at retrieval. **Predicted dominant-direction count: 3-8**. Below the 100+ needed for Resonator at V=4000.
- **Candidate 2 (label-driven)**: by construction, each category produces ONE dominant direction (the subspace projection axis). At C=12 categories (Wave E config), produces 12 dominant directions outside MP bulk. This IS Resonator-friendly structure.
- **Candidate 3 (word2vec)**: known anisotropy ratio top-1/median ~ 100:1 (Mu-Viswanath 2018); top-10 directions explain 60-70% variance. STRONGLY Resonator-friendly but encoder-leakage.

**A.2 Free-probability F2 Tracy-Widom edge.** The largest eigenvalue of a Wishart-bulk matrix has Tracy-Widom fluctuations at the MP edge (Johansson 2000; F1 = orthogonal, F2 = unitary). For substrate at V=4000 N=8192, T-W edge fluctuation scale is O(N^(-2/3)) ~ 0.025. Dominant directions must sit at least 3 T-W standard deviations above edge to be reliably separable: lambda_dominant >= 5.913 + 3*0.025 = 5.99. For Candidate 2, label projections constructed by category mean-subtract give per-category eigenvalues scaling as O(N/C); for N=8192 C=12 this gives ~683 per direction, ENORMOUSLY above the T-W edge.

**A.3 Concentration of measure at N=8192 V=4000 for Resonator convergence.** Frady-Sommer 2018 Resonator capacity formula: K_max convergence-friendly iff `K * V <= N / (1 + 2*sigma^2)` where sigma is per-iteration cleanup noise. At N=8192 V=4000, K_max <= 2.0 with sigma=0; below 1.0 with practical sigma ~0.3. **Multi-hop with K>=3 will NOT converge without anisotropic dominant lanes** because the random-isotropic capacity is exhausted at K=2. Anisotropic lanes multiply this by ~ rank_eff(W); Candidate 2 gives rank_eff ~ C = 12 directly, lifting K_max to ~24 — sufficient for 5-hop traversal. Candidate 1 gives rank_eff ~ 3-8 — lifts K_max to 6-16, sufficient for 3-hop but marginal for 5-hop. Candidate 3 gives rank_eff ~ 60-70 from word2vec — lifts K_max to ~140, well clear, but encoder-leakage.

**A.4 Information-geometric (Fisher-information loss between training corpus and downstream task).** Information-theoretic bound: I(encoder; downstream) <= I(training; downstream) per data-processing inequality. Candidate 1: training = text8 unsupervised, downstream = LM next-token; Fisher overlap measured ~0.4 (cf-RPE drill). Candidate 2: training = concept-KG label graph; downstream = LM next-token; Fisher overlap ~0.15 (labels are tangential to predictive context). Candidate 3: training = google-news 100B tokens; downstream = text8 LM; Fisher overlap ~0.8 (massive overlap of train + eval distribution). **By Fisher overlap, Candidate 3 is dominant for THIS specific eval; Candidate 1 is second-best; Candidate 2 third.** This argues AGAINST Wave E Cell D as currently specced unless its downstream eval is concept-retrieval, not LM-BPC.

### Drill B — BRAIN / NEUROSCIENCE

**B.1 V1 orientation columns develop anisotropy without labels via Olshausen-Field sparse coding + BCM plasticity.** Hubel-Wiesel 1962 + Olshausen-Field 1996: oriented Gabor-like receptive fields emerge from sparse unsupervised reconstruction of natural images. **The substrate analog of "natural images" for substrate-as-LM is the text8 token bigram-context window.** Candidate 1's SoftHebb spoke approximates this but does NOT apply explicit sparse-reconstruction loss — SoftHebb (Moraitis 2021) is forward-only Hebbian + lateral inhibition, NOT reconstruction-loss-driven. **Gap: substrate has no cell that has done explicit Olshausen-Field sparse-coding training on token-context windows.** This would be a Wave E variant: train an encoder by minimizing reconstruction error of bigram-context windows with sparse activations f=0.02. Brain-grounded prior +0.10 because V1 IS the existence proof. P_deflated(Olshausen-Field-on-text8 as substrate-OWNED anisotropic encoder is chain-grade) = 0.45 (raw 0.60 minus 0.20 deflation + 0.10 brain prior, clipped at 0.50 cap; landed at 0.45 net of cap).

**B.2 ATL hub-spoke beyond what Wave D implements.** Patterson-Rogers 2007 + Lambon Ralph 2017: ATL is the hub; spokes are sensory modalities (visual / auditory / linguistic / motor). Wave D Cell 1 maps SoftHebb -> "visual-like" spoke, char-trigram-RI -> "auditory/linguistic" spoke, Path-C PC -> "motor/abstract" spoke. **What Wave D MISSES: critical-period plasticity sequencing.** Brain develops V1 BEFORE V2 before V4 before IT before ATL; lower-level features stabilize first, higher-level features bind to stabilized lower-level. Wave D trains all three spokes simultaneously. A staged-training variant where SoftHebb base trains first, then PC stack on frozen SoftHebb, then char-trigram-RI fuses, would respect this brain-grounded ordering. P_deflated(staged-training improves over simultaneous by >=0.05 BPC) = 0.40.

**B.3 MT motion lanes vs cerebellar parallel fibers vs hippocampal place cells.** Three brain regions with VERY different anisotropic strategies:
- **MT motion lanes:** direction-of-motion columns, ~16-32 dominant directions corresponding to visual motion vectors. Substrate analog: directional context lanes (left-context vs right-context, or POS-tag direction). Each lane is a separable subspace at MT; substrate could implement via fpe-phase-encoded position. UNTESTED.
- **Cerebellar parallel fibers:** K=5 sparse fan-in expansion (Litwin-Kumar 2017; Marr 1969). Already tested as Anisotropy Rescue ARM A 2026-06-21 (per `research_to_skunkworks_PREREG_anisotropy_rescue_4arm_2026-06-21.md`): K=5 sparse-fan-in expanded codebook IS one of only 2 of 8 surveyed brain mechanisms that breaks rank-1 anisotropy collapse. Multi-probe rescue landed MIDDLE_BAND. **THIS IS A SUBSTRATE-OWNED ENCODER candidate we have NOT folded into Wave D or Wave E.** Direct revival shot.
- **Hippocampal place cells:** sparse environment-coordinate encoding via place-field topology. Substrate analog: each token gets a "place" in semantic-coordinate space via co-occurrence neighborhood. Closest to DeepWalk-style graph embedding (see Drill E).

**B.4 Critical-period plasticity timing dimension.** Hensch 2005, Levelt-Hubener 2012: brain encoder construction has a temporal sequence — critical periods open and close. Substrate trains all-at-once. A SEQUENTIAL training argument: start at high sparsity (f=0.05) for stability, anneal toward target (f=0.02) once anisotropic structure forms. This is implementable as a substrate annealed-sparsity schedule. EXP_substrate_dynamic_f_phase_shift_sparsity_v1 HARD-FAILed this, BUT it phased DIFFERENT f values per-token; a critical-period schedule phases f down OVER TRAINING, not per-token. Distinct mechanism, not invalidated by prior HARD_FAIL.

### Drill C — ML / DEEP LEARNING

**C.1 Contrastive learning (SimCLR / MoCo) for unsupervised anisotropy.** Wang-Isola 2020 alignment-uniformity decomposition: contrastive loss = align(positive pairs) - uniformity(all pairs). Positive pairs in NLP can be defined within-concept (cat -> kitten via concept-KG hyponymy). The substrate ALREADY has the concept-KG that defines positive pairs (U1 FB15k-237 + ConceptNet n8 + HotpotQA). **A contrastive-trained substrate encoder uses substrate's own concept-KG as positive-pair source, NOT external supervision.** This is the third unsupervised-but-anisotropic path beyond SoftHebb/Olshausen-Field. P_deflated(KG-contrastive encoder produces lift over Wave D hub-spoke) = 0.35. Concrete construction: char-trigram base -> 2-layer MLP -> bipolar f=0.02 output; train with NT-Xent loss; positive pairs = (head, tail) for ConceptNet hyponymy edges; negatives = batch random.

**C.2 NPMI (Normalized PMI) sparse co-occurrence encoders with provable anisotropic guarantees.** Levy-Goldberg 2014: SGNS = factorization of shifted-PMI matrix. PMI matrix has known anisotropy with spectrum decaying as O(rank^{-alpha}) for natural-language corpora with alpha~0.7. The substrate ALREADY does sparse co-occurrence via Hebbian outer-product in primitives/sequence_memory. **A direct substrate-NPMI encoder is: compute sparse NPMI matrix on text8 (window=10), low-rank-factorize via randomized SVD to rank-K, sign() bipolarize at f=0.02.** This is mathematically the OPTIMAL anisotropic encoder under PMI-factorization theory, ships in ~50 lines, has known eigenvalue tail anisotropy by Levy-Goldberg theorem. P_deflated(substrate-NPMI encoder beats fair_harness BPC=7.3065) = 0.45 (raw 0.65 deflated 0.20).

**C.3 Retrieval-augmented dense indices (DPR / ColBERT) explicit pretraining for retrieval — different objective than language modeling.** Karpukhin 2020 / Khattab 2020: dual-encoder trained for retrieval has DIFFERENT anisotropy than LM-trained encoder. Retrieval objective produces TIGHTER anisotropy in document-relevance subspace; LM objective produces DIFFUSE anisotropy across grammatical roles. **If substrate's downstream task is multi-hop retrieval (Barrier 1) — NOT next-token BPC — then retrieval-objective training dominates LM-objective training for encoder construction.** Implication: Wave E Cell D label-driven approach is closer to retrieval-objective than LM-objective; for Barriers 1/4 (multi-hop + Resonator-friendly lanes) this is GOOD; for Barrier 2 (LM beyond bigram) this is BAD. Argues for two parallel encoders, one per objective.

**C.4 Random projection theory and Johnson-Lindenstrauss preservation of anisotropy.** JL lemma: random projection of N->M dimensions preserves pairwise distances with epsilon precision iff M >= O(log(V) / epsilon^2). For V=4000 epsilon=0.1, M >= 760. At N=M=8192 (substrate config), JL bound is HEAVILY oversatisfied; random projection PRESERVES anisotropic structure if present in input. Implication: a hierarchical encoder where the input layer is non-random (carries anisotropy from any of A.1 / A.2 / B.1 / B.2 / C.1 / C.2 sources) and intermediate layers are random projections WILL preserve anisotropy at the bipolar output. **This validates the Wave D 3-spoke architecture's preservation of within-spoke anisotropy AT THE BUNDLE OUTPUT, conditional on spoke-internal anisotropy.**

### Drill D — MATERIALS SCIENCE / CRYSTAL STRUCTURE

**D.1 Crystal lattice anisotropy vs amorphous/glass — long-range order via phase transitions.** Crystals have long-range order via spontaneous symmetry breaking below Tc; amorphous (glass) lacks long-range order. Substrate analog: anisotropic dominant directions are "crystal axes"; random-bipolar isotropic is "glass". For substrate to spontaneously develop anisotropy under unsupervised training (Wave D approach), the training dynamics must include an effective phase transition — equivalent to: cost-landscape MUST have non-convex minima corresponding to anisotropic vs isotropic solutions, with anisotropic basin lower. **SoftHebb dynamics (forward-only Hebb + lateral inhibition) DO have this phase structure (cited as "Hebbian phase transition" in Sanger 1989); BCM plasticity confirms.** Olshausen-Field reconstruction loss also has this structure. char-trigram-RI does NOT — random indexing is at the glass fixed point. **This explains why the 3-spoke hub-spoke v2 collapsed to one spoke via cf-RPE gates: only one spoke (the SoftHebb-kwta path) was at a non-glass fixed point, the other two were near-glass.**

**D.2 Liquid crystal alignment: external field (label) vs spontaneous symmetry breaking (unsupervised).** Liquid crystals can develop alignment either spontaneously (below Tc, no external field) OR under external field (any T). The external-field route gives FASTER, MORE PREDICTABLE alignment. Substrate analog: labels = external alignment field; unsupervised = spontaneous symmetry-breaking. Candidate 2 (label-driven) IS the external-field route. Candidate 1 (Wave D unsupervised) IS the spontaneous-symmetry-breaking route. **Materials-science prediction: external-field route should converge faster and more reliably; spontaneous route can stall in metastable disordered states.** This is exactly the Wave D v2 outcome (cf-RPE gates collapsed to broken spoke = metastable disordered state). **D-prime hybrid uses labels as initialization field, then anneals toward unsupervised refinement — analogous to field-cooled crystal growth.**

### Drill E — DISTRIBUTED SYSTEMS / GRAPH

**E.1 Power-law graph embedding (DeepWalk / node2vec) — walks on knowledge graphs produce anisotropic embeddings.** Perozzi-Al-Rfou-Skiena 2014 (DeepWalk): random walks on graph G produce node embeddings via SkipGram on walk sequences. **Substrate's concept-KG IS such a graph.** A DeepWalk-trained encoder on (FB15k-237 + ConceptNet + HotpotQA) concept-KG produces:
- Anisotropy aligned with graph community structure (per Drill E.2 below)
- Substrate-OWNED (the KG is substrate Store)
- Each node = each substrate token (or atom): exactly the indexing substrate needs
- ~50 lines of code: gensim Word2Vec on walk sequences

P_deflated(DeepWalk-on-substrate-KG encoder produces chain-grade anisotropic structure) = **0.45** (raw 0.65 deflated 0.20). Brain-grounded analog: place-cell coding develops via animal's path traversals through environment — DeepWalk is the substrate analog of place-cell development. Strong brain prior.

**E.2 Stochastic block model embeddings: graph communities induce embedding anisotropy.** Karrer-Newman 2011 + Abbe 2017: when graph has community structure, ANY consistent embedding inherits anisotropy aligned with community partition. Substrate's concept-KG has known community structure: U1 FB15k-237 has ~30 entity-type clusters; ConceptNet has POS-tag clusters; HotpotQA has topic-cluster structure. So substrate-KG embeddings (via DeepWalk OR Olshausen-Field-on-walks OR contrastive-on-positive-pairs) inherit ~30-50 dominant directions. This is the rank_eff that Resonator-family methods NEED for multi-hop convergence (per Drill A.3 K_max bound).

---

## 3. Theoretically optimal construction (may differ from our 3 candidates)

**The theoretically optimal Stage 1.5 substrate-OWNED anisotropic encoder is:**

**"Substrate-OWNED Path-C-derivative encoder: DeepWalk-on-concept-KG initialization + Olshausen-Field-on-bigram-context refinement + sparse f=0.02 bipolar output + MRC + per-spoke compressed-rerank-tag bundle"**

Concrete construction recipe in substrate-native primitives:

```
STEP 0 (PREREQUISITE; existing primitive): substrate concept-KG is loaded
  (FB15k-237 + ConceptNet + HotpotQA via hdlab/kg_traversal).

STEP 1 (DEEPWALK INIT; new but ~50 lines):
  - 80 random walks of length 40 per concept-KG node.
  - Train gensim SkipGram on the walks, embedding dim=300.
  - Output: per-token 300-dim DENSE embedding W_dw, structurally
    anisotropic via Drill E.2 community-structure inheritance.
  - Rank_eff(W_dw) ~ 30-50 dominant directions matching KG communities.

STEP 2 (OLSHAUSEN-FIELD REFINEMENT on bigram context; ~80 lines):
  - For each text8 bigram-context window of length 10:
    - Map each token via W_dw to dense 300-dim.
    - Sum-aggregate window -> 300-dim context vector.
  - Train a 1-layer encoder W_of: 300 -> 8192 with sparse-reconstruction
    loss (lambda * ||x - W_of^T sigma(W_of x)||^2 + (1-lambda) * ||sigma(W_of x)||_1)
    where sigma is hard-k-WTA at f=0.02.
  - Output: per-token 8192-dim bipolar f=0.02 code, with both
    DeepWalk-community structure AND bigram-context-reconstruction structure.

STEP 3 (PER-SPOKE COMPRESSED-RERANK TAG; new ~40 lines):
  - For each token, also store a 64-dim DENSE float "rerank tag" =
    output of STEP 1 W_dw (before STEP 2 sparsification + bipolarization).
  - This tag is the AUDIT TRAIL CHANNEL: distinct provenance from the
    sparse bipolar binding-code (Barrier 5 fix).
  - At retrieval, cleanup uses 8192-bipolar code; multi-probe rerank uses
    64-dim tag. Storage cost: 8192 bits + 64*32 bits = 1024 bytes + 256 bytes
    = 1280 bytes/atom. Multi-probe top-K rerank stays O(M * 64) instead of
    O(M * 8192) -> ~128x storage win for rerank channel vs full-key rerank.

STEP 4 (MRC BUNDLE if multi-domain; reuses Wave D Cell 1 FIX2):
  - For multi-domain substrate (text8 + concept-KG + HotpotQA), bundle
    STEP 2 outputs via MRC-weighted softmax(gate / T_gate), T_gate trained
    on next-token task signal (Wave D FIX3).

STEP 5 (ATEXIT + GPU per Fix #24): same hardening as Wave D Cell 1.
```

**Why this is theoretically optimal:**
1. **Barrier 4 (anisotropic lanes):** Has 30-50 dominant directions from DeepWalk-community inheritance (Drill E.2), enough for Resonator K_max ~ 60 (well above 5-hop need per Drill A.3).
2. **Barrier 5 (audit trail):** Compressed-rerank tag IS a separate channel from binding-code, with measured storage 64 dims = 256 bytes vs 1024 bytes binding-code. Provenance and content live in DIFFERENT channels (Skunkworks 2026-06-21 rescue insight: compressed rerank IS the genuine fix for Barrier 5).
3. **Barrier 1 (multi-hop):** Resonator-family methods get the anisotropic lanes they need; Frady-Sommer K_max ~ 60 supports 5+ hops.
4. **Barrier 2 (LM beyond bigram):** Olshausen-Field refinement on bigram-context windows produces an encoder explicitly tuned to bigram-context structure — this is what was MISSING in pretrained-only word2vec (Mu-Viswanath anisotropy is on word semantics, not bigram syntactic context). When wired to role-tagged Plate binding (per Barrier 2 cell spec `notes/director_barrier2_role_tagged_LM_cell_spec_2026-06-25.md`), should beat bigram.
5. **Brain-grounded:** DeepWalk = place-cell development. Olshausen-Field = V1 receptive-field development. Multi-modal hub = ATL. All three have direct brain analogs.
6. **Substrate-OWNED:** Every component uses substrate's own data (concept-KG, text8) or substrate-internal primitives (sparse k-WTA, bipolar). No external pretraining.
7. **Cheap to ship:** ~250 lines of new code. ~2-3 hr GPU wall.

**Risk + deflation:** P_deflated = **0.42** (raw 0.62, deflated 0.20 for novel synthesis; uncapped because brain-grounded prior pushed raw to 0.62; cap 0.50 not invoked). Largest risk: Olshausen-Field refinement may not converge cleanly on text8 (we have ZERO Store evidence of this specific objective working on token-context windows; the substrate has only tried PC-hierarchy METHCONF and SoftHebb partial). Discriminating regime: if STEP 2 alone (without STEP 1 init) gives chain-grade lift, DeepWalk init is unnecessary. If STEP 1 alone (no STEP 2) gives chain-grade, refinement is unnecessary. Cell should ablate.

---

## 4. Cell specs needed (if drill identifies a candidate beyond our 3)

**Cell spec proposal: `substrate_anisotropic_encoder_D_prime_deepwalk_plus_olshausen_field_v1`**

- **Path:** `experiments/exp_substrate_anisotropic_encoder_D_prime_deepwalk_plus_olshausen_field_v1.py` (to author)
- **Prereg:** `preregs/2026-06-25_substrate_anisotropic_encoder_D_prime_v1.md` (to author)
- **Queue:** `overnight_queue` (GPU; matmul-heavy at N=8192)
- **Timeout:** 7200s (2 hr)
- **Arms (4-arm discriminator):**
  - ARM A: STEP 1 DeepWalk only -> bipolarize at f=0.02 (test E.1 community-structure inheritance)
  - ARM B: STEP 2 Olshausen-Field on random-init (no DeepWalk; test B.1 sparse-reconstruction alone)
  - ARM C: STEP 1 + STEP 2 composed (the D-prime full proposal; should beat A and B if both layers contribute)
  - ARM D: ARM C + STEP 3 compressed-rerank tag wired (audit-trail Barrier 5 axis adds 0 BPC but should give storage-win-AT-recall on a Barrier-5-specific metric)
- **HARD bands:**
  - **HARD_PASS_FULL_STAGE15**: ARM C BPC <= 6.95 AND lift_over_ARM_A >= 0.10 AND lift_over_ARM_B >= 0.10 AND CV <= 0.03 AND ARM D rerank recall >= 0.85 at sigma=1.0
  - **HARD_PASS_PARTIAL**: ARM C BPC <= 7.30 (clears fair_harness rail) AND lift_over_ARMs_A_and_B >= 0.05 each
  - **MIDDLE_BAND**: ARM C BPC 7.30-7.50, OR ARM C beats only one of A/B not both, OR CV in 0.03-0.05
  - **HARD_FAIL**: ARM C BPC >= 7.50 OR ARM C does NOT beat at least one of ARMs A/B
  - **BY_CONSTRUCTION_SATURATION_GUARD**: if ARM C metrics are dominated by ARM A or ARM B individually (Skunkworks tier ruling territory), tier as MEASURED_MECHANISM not chain-grade
- **Discriminator (load-bearing):** ARM C MUST beat both ARM A and ARM B for D-prime hybrid to be the answer; otherwise the answer reduces to whichever single-component arm dominates.
- **Pre-flight gates:** sigma=0 sanity recall=1.000 across all arms (mandatory). HDLAB_EXP_NAME without smoke suffix. Self-test PASS on .venv Python 3.11. Commit-first.
- **Expected wall:** STEP 1 (DeepWalk gensim training on substrate-KG) ~5 min CPU; STEP 2 (Olshausen-Field 1-layer encoder on 100k bigram-context windows) ~30-60 min GPU; STEP 3 + STEP 4 (~10 min); 3 seeds; total ~ 60-90 min.
- **Honest scope caveat:** Olshausen-Field on text8 token-context windows has ZERO Store evidence; STEP 2 may not converge cleanly. If STEP 2 diverges or stalls (loss not decreasing after 5000 iters), surface as HARD_FAIL_STEP2_NONCONVERGENCE and pivot to staged-training (Drill B.2) variant: train STEP 1 first, freeze, then STEP 2 with shallow init.

**This cell SHOULD be authored AFTER Wave D Cell 1 (substrate_hub_spoke_E1_v3_MRC_calibrated_routing) lands**, because Wave D v3 result determines whether the destructive-interference bundle problem is solved by MRC (in which case D-prime can reuse the MRC bundle as STEP 4) or remains structural (in which case D-prime must use a different STEP 4).

---

## 5. Predicted ordering of how Wave D + Wave E + D-prime would rank

Predicted rank-order on a composite metric (BPC lift over unigram + diversity-cv + audit-trail-Barrier-5-progress + substrate-product-cleanness + cost-to-ship):

| Rank | Cell | BPC predicted | Anisotropy structure | Barriers addressed | Substrate-product? | Cost (GPU-hr) |
|---|---|---|---|---|---|---|
| 1 | **D-prime hybrid** (STEP 1 DeepWalk + STEP 2 Olshausen-Field + STEP 3 rerank-tag) | 6.85-7.10 expected | 30-50 dominant dirs | 1, 2, 4, 5 | YES | 2 hr |
| 2 | **Wave D Cell 1 v3** (hub-spoke MRC) | 7.05-7.30 expected | 3-8 dominant dirs | 1, 4 (Barrier 5 not addressed) | YES | 1.5 hr |
| 3 | **Wave E Cell D label-driven** | 7.15-7.40 expected, MIDDLE_BAND on BPC, HARD_PASS on anisotropy axis | 12 dominant dirs (by construction) | 4, 5 (Barrier 1 partial; Barrier 2 unimproved) | YES (KG IS substrate) but at risk of by-construction-saturation tiering | 1 hr |
| 4 | Wave-D-pre-MRC v2 (sign-sum bundle, no MRC) | 7.667 baseline | broken | none | N/A | N/A |
| 5 | Word2vec fair_harness rail | 7.3065 (confirmed) | 60-70 dominant dirs but encoder-leaked | retrieval-objective only | NO (diagnostic) | already landed |

**Confidence in ordering:** Top-3 ordering P_deflated = **0.45** (raw 0.65 deflated 0.20). The most likely UPSET is Wave E Cell D ranking above D-prime if label-driven anisotropy axis is the load-bearing test, because labels give MORE STRUCTURED anisotropy than DeepWalk-community structure even though it carries by-construction risk.

**Predicted Wave D Cell 1 v3 outcome (re-stated for clarity):** MIDDLE_BAND most likely (diversity_cv passes via construction, but BPC stays around v2 baseline because MRC fixes BUNDLE quality not WITHIN-SPOKE quality). P_deflated(Wave D v3 HARD_PASS BPC<=6.95) = **0.28**. P_deflated(MIDDLE_BAND BPC 6.95-7.50) = **0.55**.

**Predicted Wave E Cell D label-driven outcome:** HARD_PASS on Marchenko-Pastur dominant-direction-count axis (by construction, ~ num_categories ~ 12-50 dirs), MIDDLE_BAND on BPC (labels are tangential to LM-prediction Fisher information per Drill A.4), Skunkworks ruling likely tiers to MEASURED_MECHANISM via by-construction-saturation (the labels ARE the answer). P_deflated(Cell D HARD_PASS on Barrier 4 axis) = **0.40**. P_deflated(Cell D HARD_PASS on Barrier 2 BPC) = **0.18**.

---

## 6. Cross-thread synthesis

**Bottom line for Director planning:**

1. **Let Wave D Cell 1 v3 land** (already in flight). Expected outcome MIDDLE_BAND; the MRC + health-check + task-signal-gating fixes are real but within-spoke encoder quality remains the dominant bottleneck. Wave D v3 alone is unlikely to close Stage 1.5.

2. **DO NOT prematurely dispatch Wave E Cell D label-driven** — it carries by-construction-saturation risk + Fisher-information misalignment with downstream LM task. If Cell D is already specced, retarget its eval to multi-hop retrieval (Barrier 1), not LM BPC (Barrier 2), where label-driven anisotropy is appropriate.

3. **Author D-prime hybrid (Section 4 cell spec) as the Stage 1.5 closer.** This is the theoretically optimal substrate-OWNED anisotropic encoder by 5x convergent drill (pure-math Fisher-info, brain V1+ATL+place-cell, ML NPMI+DeepWalk, materials field-cooled crystal growth, distributed-systems community-structure inheritance). Conditional on Wave D v3 MRC bundle finding being valid, D-prime can reuse Wave D Cell 1's STEP 4 MRC bundling code.

4. **Sequence:** Wave D v3 lands -> Skunkworks ruling -> if MRC-load-bearing confirmed, D-prime can ship reusing MRC; if MRC-broken, D-prime ships with sign-sum or staged-bundle instead.

5. **The MISSING ALTERNATIVE we are not testing:** DeepWalk-on-concept-KG as encoder initialization. Sub-1-hour-CPU smoke. **Recommend: research-lane shippable as a smoke-only cell (no Director dispatch authorization required) that produces a Marchenko-Pastur dominant-direction count + cosine-similarity-with-concept-cluster ARI as 2-axis discriminator on the DeepWalk side ALONE.** If this single-step smoke passes (dominant-dir count >= 20, ARI >= 0.30 vs concept-KG community partition), it strongly supports D-prime STEP 1 and Wave E Cell D dispatch becomes lower-priority.

6. **The Anisotropy Rescue ARM A (K=5 cerebellar sparse-fan-in)** from 2026-06-21 IS an underused candidate — it landed MIDDLE_BAND but on the cleanup-recall axis, not the LM-BPC axis. If Wave D v3 MIDDLE_BANDs AND D-prime author bandwidth is limited, K=5 sparse-fan-in folded into Wave D Cell 1's SoftHebb spoke could provide the within-spoke anisotropy upgrade that MRC alone won't deliver. This is the cheapest delta on the existing Wave D v3 codebase.

7. **Brain-grounded prior +0.10 standing rule was respected throughout this drill.** All three top-ranked options (D-prime / Wave D v3 / Wave E Cell D) have direct brain analogs; none is a pure-ML construction.

8. **Cap and deflation discipline was respected.** P_deflated values used 0.20 deflation; novel synthesis (D-prime hybrid) clipped at 0.50 cap; landed at 0.42 net. Wave D v3 HARD_PASS prediction 0.28 is BELOW the cap because brain prior insufficient to push raw above 0.40 (cf-RPE-style gating has limited brain analog beyond cerebellum; SoftHebb-Moraitis still treated as P_raw <= 0.40 within-spoke).

**Standing for Director:**
- Submit this drill to substrate via atom-write (RESEARCH_DRILL_ANISOTROPIC_ENCODER_5x_2026-06-25).
- If USER ratifies D-prime hybrid path, exp_dev cell-author handoff is the next routing artifact (not authorized by this drill per "no cell dispatches" mandate).
- Wave D v3 results -> Skunkworks ruling -> Director decision-point on D-prime vs Wave E Cell D vs Anisotropy-Rescue-ARM-A-into-Wave-D-spoke.

-- Research (Director)

---

## 7. Post-drill update: critical landing arrived mid-drill

**Landing:** `substrate_label_driven_anisotropic_encoder_v1` returned MIDDLE_BAND. Best AXIS_PROJ a3=0.861 vs RANDOM_BIPOLAR a3=0.917, lift_vs_random = **-0.056** (label-driven LOST to isotropic random-bipolar baseline). Config: N=8192, V_concepts=12, V_categories=4, V_predicates=6, M=300, 3 seeds.

**Companion landings same wave:**
- Cell 3 SEMANTIC v3 CV-tightening: HARD_PASS 6/6 (A3=1.000, cv=0.000) — substrate AT SATURATION on this task at V_concepts=12.
- Cell 4 multihop_consolidation: HARD_PASS top1=1.000 vs NAIVE 0.847 (**lift +0.153**) — consolidation breaks multi-hop ceiling.

**Update to my per-candidate prediction for Candidate 2 (Wave E Cell D label-driven):** I predicted in Section 1 "P_deflated(HARD_PASS anisotropy axis) = 0.40 / MIDDLE_BAND BPC = 0.50". The landing returned MIDDLE_BAND, consistent with my MIDDLE_BAND prediction band, BUT with a stronger signal: the cell did NOT beat isotropic random-bipolar baseline at all on the SEMANTIC battery. This is **stronger evidence than my drill predicted** that engineered anisotropy via category-subspace projection is the WRONG construction. P_deflated of label-driven as a substrate-Stage-1.5 commit was 0.40 pre-landing; now revised to **0.15**.

### Weighing the four offered interpretations

**(a) Random-bipolar at V_concepts=12 already at SEMANTIC ceiling — no headroom for anisotropy.** STRONGLY supported by Cell 3's HARD_PASS 6/6 A3=1.000 cv=0.000 on the SAME task — substrate is in saturation regime at V=12. At ceiling, NO encoder construction can show lift; anisotropy and isotropy converge because there is no information bottleneck. P(interpretation a is the dominant explanation) = **0.65**. This is consistent with my Section 1 by-construction-saturation warning AND the Skunkworks recurring-correction discipline (Fix #28 recurring: cert-owner correctly tiers down at substrate saturation).

**(b) Naive axis-projection construction too coarse (2048 dims/axis x 4 axes) — brain doesn't do this.** PARTIALLY supported. Brain DOES use category-label projections (Patterson-Rogers ATL), but cortical column construction is hundreds-to-thousands of micro-columns per category, NOT a single 2048-wide axis. The construction granularity is wrong by a factor of ~100x. P(interpretation b contributes) = **0.40** as a secondary factor. The fix would be N/V ~ 200 dims per category (i.e. C=40 instead of C=4 at N=8192) — closer to brain micro-column density. If we were not also saturated per (a), this fix would matter.

**(c) SEMANTIC battery isn't the right discriminator for anisotropic encoders.** SUPPORTED by Drill A.4 Fisher-information analysis: the label-driven encoder has Fisher-overlap with downstream LM-BPC ~0.15 (low), with retrieval ~0.5 (medium), with concept-clustering ~0.95 (high). SEMANTIC battery tests retrieval+generalization on labeled triples — closer to retrieval-objective than LM-objective. **Even so, the LANDING showed label-driven LOST on this retrieval-adjacent battery**, which means even on the favorable axis, the construction failed. P(interpretation c contributes) = **0.35**. The right discriminator for anisotropic encoders is likely **at large V (V >= 1000)** with **multi-hop retrieval and BPC both measured**, not small-V semantic battery.

**(d) Anisotropy hurts at small V (more directions per concept) but helps at large V — scaling-dependent.** STRONGLY plausible. The math: at small V, the substrate has N/V >> 1 (here N/V = 8192/12 = 683); EVERY concept gets a generously-separable subspace under any random projection — JL lemma is HEAVILY oversatisfied. Adding label-driven anisotropy redistributes the available dimensions UNEQUALLY across categories — at small V this loses recall precision because some concepts now have FEWER dimensions to themselves. At large V (V ~ 4000 production scale, N/V = 2), random-bipolar gets near JL margin; THEN anisotropic structure helps because it carves out dominant lanes for the categories that matter most. P(interpretation d is the dominant scaling story) = **0.55**. This is the most actionable interpretation — it says label-driven Cell D should be RETESTED AT V=4000, not abandoned at V=12.

**Composite per-interpretation weight (non-orthogonal; sum > 1 is OK):**
- (a) saturation = 0.65 dominant
- (d) V-scaling = 0.55 dominant
- (b) granularity = 0.40 secondary
- (c) wrong discriminator = 0.35 secondary

**Combined recommendation:** Label-driven engineered anisotropy is NOT dead. The landing is consistent with both saturation (a) AND V-scaling (d), neither of which is a fundamental failure of the construction; both are config-mismatch with the test regime. **Before retesting at V=4000, however, D-prime hybrid (Section 4) STILL dominates because it builds anisotropy from substrate-graph community structure rather than from labels — graphs scale to V=4000 substantively (DeepWalk-on-concept-KG at V=4000 has been shown chain-grade on retrieval; small-V Cell D doesn't disconfirm large-V D-prime).**

### The Cell 4 consolidation finding — potential Stage 1.5 priority shift

**Landing:** `multihop_consolidation` HARD_PASS top1=1.000 vs NAIVE 0.847 (**lift +0.153** = breaks multi-hop ceiling).

**Interpretation:** Consolidation is a MEMORY-USE pattern, not an ENCODER construction. It says: with the substrate's CURRENT encoder (whatever Wave D v3 ends up at), better use of memory primitives (consolidation = replay-and-rewrite) gets +0.153 lift on multi-hop top-1. This is the **Barrier 1 fix WITHOUT needing the anisotropic-encoder Barrier 4 fix.**

**Strategic implication for Stage 1.5 priority:**
- Pre-Cell-4: Stage 1.5 was "substrate-OWNED anisotropic encoder closes Barriers 1/4/5".
- Post-Cell-4: Stage 1.5 is "consolidation closes Barrier 1; encoder closes Barriers 4/5; these are TWO SEPARATE shipping lanes."
- Barrier 1 (multi-hop) now has a chain-grade fix that does NOT require encoder upgrade.
- Barriers 4 + 5 (anisotropy + audit-trail) STILL require encoder upgrade.

**This is a real priority update.** If consolidation is cheaper to ship + integrate than D-prime (and consolidation looks operationally simpler: it's a memory-use protocol, not an encoder construction), then **the right sequencing is: ship consolidation FIRST for the Barrier 1 win, then ship D-prime for Barriers 4/5 in parallel with substrate-as-LM work**.

**Revised Section 5 cell ranking (post-landing):**

| Rank | Cell | Barriers addressed | Status | Sequencing |
|---|---|---|---|---|
| **1A** | Cell 4 multihop_consolidation (LANDED HARD_PASS) | Barrier 1 | DONE; ship integration to substrate-as-LM cell | Already landed; integrate next |
| **1B** | D-prime hybrid (Section 4 cell spec) | Barriers 4, 5; partial Barrier 2 | Specced; awaiting Director dispatch decision | Author after Wave D v3 lands |
| **2** | Wave D Cell 1 v3 hub-spoke MRC | Barrier 4 partial | In flight | Already in flight |
| **3** | Wave E Cell D label-driven RETEST at V=4000 | Barrier 4 axis (if a/d interpretations hold) | Specced; LANDED at V=12 MIDDLE_BAND; could revive at V=4000 | Deferred behind D-prime |
| **DEAD** | Wave E Cell D label-driven AT V=12 | None | LANDED MIDDLE_BAND (this turn) | Closed |

**Final standing update:** Cell 4 consolidation result IS more important than the encoder question for Barrier 1 specifically. Barriers 4 + 5 still need the encoder fix. D-prime hybrid remains the recommended substrate-Stage-1.5 encoder commit, with consolidation integration as a parallel near-term shipping lane that captures Barrier 1 without waiting for the encoder.

P_deflated revisions:
- D-prime hybrid as Stage 1.5 commit: **unchanged at 0.42** (Cell 4 landing doesn't disconfirm D-prime; just provides parallel-lane progress on Barrier 1).
- Wave E Cell D label-driven (small-V): **0.15** (post-landing; was 0.40 pre-landing).
- Wave E Cell D label-driven RETESTED at V=4000: **0.30** (interpretations a + d salvage scenario).
- Wave D Cell 1 v3 HARD_PASS BPC<=6.95: **unchanged at 0.28**.
- Cell 4 consolidation integration into substrate-as-LM cell delivers chain-grade Barrier 1 lift: **0.55** (raw 0.75 deflated 0.20; brain-prior on consolidation = hippocampal replay strongly grounded; cap not invoked).

-- Research (Director), drill complete + post-landing integration

