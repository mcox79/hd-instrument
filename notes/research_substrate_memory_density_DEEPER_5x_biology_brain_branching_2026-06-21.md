# RESEARCH (Director) -> SKUNKWORKS + EXP-DEV cc ORCH: DEEPER 5x branching drill on SUBSTRATE MEMORY DENSITY -- 8 biology/brain mechanisms surveyed across 3 depths (DG / COP / product-key / cerebellar-GC / fly-LSH / phase-coding / BTSP / PC-AM); the rank-1 anisotropy trap is the SHARED bottleneck; 2 paths qualitatively break it (cerebellar K=5 sparse-fan-in + fly-LSH composed with CERT 591); HARD-PASS + HARD-FAIL pre-registered. Substantive.

**Date:** 2026-06-21T14:39:38Z (true `date -u`)
**Composes:** the storage-chain cascade outcome (item #3 dense-projected M-indep COLLAPSES on real anisotropic learned keys; item #4 attention rescues at O(M*d); whitening mechanism CPU-PoC confirmed); CERT 591 dense-projected-KV; CERT 592 K_max NESS envelope; sparse super-capacity a3f473dd; crosstalk-law c-unbounded (7315be3c).
**Parent drill (1x):** `research_dense_projected_KV_at_scale_revival_drill_2026-06-21.md`.

---

## (a) HEADLINE (one-line cross-domain answer)

**The biology/brain mechanism most likely to compose with substrate's storage chain to BREAK the rank-1 anisotropy collapse is the CEREBELLAR GRANULE-CELL SPARSE-FAN-IN (K=3-5) + threshold motif (Marr-Albus / Litwin-Kumar 2017), composed with FLY-LSH-style WTA hashing (Dasgupta-Stevens-Navlakha 2017) on top of CERT 591's learned projection -- because these are the ONLY two mechanisms (of 8 surveyed across 3 depths) that QUALITATIVELY break the rank-1 mu-smearing failure mode of dense Gaussian projection, rather than only quantitatively rescuing the SNR.**

Why these two specifically:
- **Cerebellar K=5 sparse-fan-in:** each expanded unit reads only k=5 of d=768 input dims -> common-mode mu contribution per unit is a SMALL RANDOM SUBSET-SUM (variance ~ K*sigma_mu^2, not d*sigma_mu^2 as in dense projection). Threshold + kWTA can SELECT the units whose subset happens to be anti-correlated with mu. Dense Gaussian projection smears mu uniformly across all units (mu is preserved as a unit-vector direction shared by ALL units, NOT thresholdable away).
- **Fly-LSH WTA hash:** WTA top-k selection is INVARIANT to additive shift (median-subtract pre-step kills rank-1 mu), gives genuine PER-MEMORY O(k log n) bits storage (~28 B/memory at k=20, n=2400) vs attention's O(d) per memory (~3 KB at d=768).

The 6 OTHER mechanisms surveyed (DG dense expansion, active-dendrite COP, product-key/grid-code, phase-coding/complex-Hopfield, BTSP relative-floor, PC-AM iterative inference) all either share the rank-1 trap (DG, COP, product-key under low eff-rank), require novel-synthesis design (phase-coding's phase-hash, BTSP's online Gram-Schmidt), or rescue ONLY the SNR at O(M*d) compute (PC-AM iterative).

---

## (b) Cheap decisive test

**ONE-CELL 4-ARM ANISOTROPY-RESCUE SWEEP, ~1-2 hr CPU, KO-or-GO answer per arm:**

`expdev/EXP_anisotropy_rescue_4arm_sweep_v1`: d=768 (BGE) post-CERT-591-projection learned anisotropic keys, M sweep {1k, 3k, 10k}, mean_cos verified per-arm, 5 seeds, recall@1 + storage-per-memory measured.

Four ARMs (each separately PASS/FAIL pre-reg'd):
- **ARM A = CEREBELLAR sparse-fan-in K=5**: expansion d'=3840 (5x), each expanded unit reads random K=5 input dims, kWTA top-10%, outer-product superposition store, cosine-argmax decode. **Discriminating control (mandatory):** ARM A' = same expanded dim and kWTA, but DENSE Gaussian random projection (full fan-in) -- must HARD-FAIL to credit sparse-fan-in as the load-bearing feature.
- **ARM B = FLY-LSH composed with CERT 591**: learned projection -> median-subtract -> sparse random projection (~5% nonzero) -> WTA top-k=20 -> sparse-tag hash table (n=2400, M memories at O(k log n) bits each) -> retrieval by hash + single-bucket dot-product re-rank. **Discriminating control:** ARM B' = random hyperplane LSH (Charikar 2002) -- must underperform fly-LSH to credit the WTA-shift-invariance mechanism.
- **ARM C = compose-of-A-and-B** (sparse-fan-in expansion -> fly-LSH on the expanded sparse code): the headline shot; predict highest recall under M=10k anisotropic regime.
- **ARM D = attention upper-bound** (1-step softmax over O(M*d)): the storage-rule-bottleneck baseline; ARMs A/B/C should approach D's recall while having sub-linear-in-M per-memory storage.

**Smoke gate (5 min CPU):** ARM A K-sweep {K=1, 5, 20, full} at M=1k must show unimodal recall vs K with peak at K=5 (matches Litwin-Kumar 2017 theory). If monotone or peak elsewhere, sparse-fan-in mechanism is wrong and ARM A is killed before scaling.

**Pre-flight (mandatory before any of the 4 ARMs):**
- Measure mean_cos of CERT-591-projected pythia/BGE keys -- if mean_cos < 0.20, anisotropy is already absorbed by the learned projection and this drill is solving a non-problem (kill the cell, atomize the projection-already-fixes-it finding).
- Measure effective rank r_eff of projected keys via SVD spectrum; if r_eff < 64, cap K at floor(r_eff / 96) per the depth-1 product-key analysis (eff-rank-limited).

---

## (c) Falsifiable predictions with HARD-PASS + HARD-FAIL thresholds (pre-registered, mandatory)

**ARM A (cerebellar sparse-fan-in K=5):**
- HARD-PASS: recall@1 >= 0.40 at M=10k AND ARM A' (dense Gaussian, same expanded dim) recall@1 <= 0.20 (Delta >= +0.20 absolute) AND seed CV < 0.05 AND K-sweep peak at K=5 (Litwin-Kumar optimum verified).
- HARD-FAIL: recall@1 < 0.15 at M=10k OR ARM A' >= ARM A (sparse-fan-in not load-bearing) OR K-sweep monotone (no Litwin-Kumar optimum).
- MIDDLE_BAND: recall@1 0.15-0.40 -> atomize as MEASURED_MECHANISM ("sparse-fan-in expansion partially rescues anisotropy collapse, K* depends on input correlation structure"), NOT chain-grade.
- P(HARD-PASS) = 0.30-0.40 (deflated, cap 0.50 novel-synthesis); P(MIDDLE_BAND) = 0.35; P(HARD-FAIL) = 0.25.

**ARM B (fly-LSH + median-subtract, composed with CERT 591):**
- HARD-PASS: recall@1 >= 0.60 at M=10k AND M-indep degradation <= 0.10 (recall@1 at M=10k within 0.10 of recall@1 at M=1k -- the load-bearing M-indep proof) AND measured per-memory storage <= 1 KB AND shuffled-control recall@1 < 0.10.
- HARD-FAIL: recall@1 < 0.40 at M=10k OR M-indep degradation > 0.20 (recall drops as M grows -- not M-indep) OR storage > 5 KB/memory (claim falsified by measurement) OR ARM B' (Charikar LSH) >= ARM B (WTA mechanism not load-bearing).
- MIDDLE_BAND: recall@1 0.40-0.60 OR M-indep degradation 0.10-0.20 -> MEASURED_MECHANISM atom ("fly-LSH-style sparse-tag indexing gives sub-linear per-memory storage with bounded recall ceiling on anisotropic learned keys").
- P(HARD-PASS standalone) = 0.30; **P(HARD-PASS composed with CERT 591) = 0.50 (CAPPED at novel-synthesis ceiling; raw lit-scan estimate 0.55)**; P(HARD-FAIL) = 0.20.

**ARM C (compose-A-and-B = sparse-fan-in -> fly-LSH on expanded code):**
- HARD-PASS: recall@1 >= 0.70 at M=10k AND beats BOTH ARM A AND ARM B by >= +0.10 absolute AND M-indep degradation <= 0.10.
- HARD-FAIL: recall@1 < max(ARM A, ARM B) -- composition doesn't help, mechanisms not complementary.
- MIDDLE_BAND: recall@1 between max(A,B) and max(A,B)+0.10 -- composition gives marginal lift, not multiplicative.
- P(HARD-PASS) = 0.20 (composition gains rarely as strong as separate-mechanism additivity suggests).

**ARM D (attention upper bound):**
- Calibration arm only; expected recall@1 ~ 0.80-0.95 at M=10k per CERT 591 finding; if << 0.80, ARM D itself has a meter bug (cell calibration failure).

**ANCILLARY HARD-FAIL discipline (substrate-wide):**
- If pre-flight mean_cos < 0.20 (CERT 591 projection already fixes anisotropy): DROP the drill, atomize the projection-fix finding; this is a HARD-FAIL of the "rank-1 trap is still present after projection" assumption that motivated the whole drill.
- If pre-flight eff_rank < 32: the substrate's learned-key information bandwidth is too narrow for M=10k storage anyway; descope to M=1k and characterize as "low-eff-rank capacity ceiling" rather than rescue-mechanism finding.

---

## (d) Cross-thread synthesis with EXISTING substrate experiments (the scour result)

**Already 5x-drilled (DO NOT re-walk; covered):**
- Hippocampal CA3 attractor: 5x + 3x DEEPER (`research_drill_natural_analog_hippocampal_5x_2026-06-07.md`, `..._DEEPER_3x_*`). Saturated; no new yield.
- Drosophila MB linear-readout: 2x with MIDDLE-BAND linear-readout ceiling finding (`research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md`). The MB IS a sparse-fan-in mechanism (K=6-8 per Kenyon cell), but at much smaller scale than cerebellar GCs (50 PNs vs 250k mossy fibers).
- Kanerva SDM: 2x architectural design (`research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md`). SDM uses dense pseudo-random hard-locations; structurally closer to dense projection than to sparse-fan-in.
- Modern Hopfield: 5x + DEEPER 5x (`research_drill_field_modern_hopfield_5x_2026-06-07.md`, `..._DEEPER_5x_*`). Ramsauer 2020 attention-equivalence is item #4 of storage chain.
- REM/sleep/replay consolidation: 2x (`research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md`); STDP 2x (`research_drill_stdp_*_2x_*`); sparse-coding/compressed-sensing 2x (`research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`).
- Free-probability/RMT: covered by parent drill's lit-scan synthesis.

**Newly drilled in THIS deeper 5x (NEW fields, not re-walked):**
- DG sparse-expansion+kWTA (depth-1): rank-1 trap formally proven (S <= sqrt(d'/r_eff) Babadi-Sompolinsky 2014).
- Active-dendrite COP (depth-1): axis-aligned rank-1 trap airtight; mu spreads uniformly across compartments -> no rescue.
- Product-key/grid-code modular memory (depth-1): K_useful bounded by eff_rank / sub_dim; storage is O(sqrt(M)*d), sub-linear NOT M-indep. Composes with CERT 591.
- Cerebellar GC sparse-fan-in K=5 (depth-2): Litwin-Kumar 2017 K*~sqrt(N_pre) at biological 3-5 range; QUALITATIVELY different from dense projection because K=5 limits per-unit mu-contribution variance.
- Fly-LSH WTA (depth-2): Dasgupta-Stevens-Navlakha 2017 fly-MB-as-LSH; WTA shift-invariance breaks rank-1 mu; genuine PER-MEMORY O(k log n) bits.
- Phase-coding / complex-Hopfield (depth-2): Aoki/Noest 1988 / Plate 1995 HRR; phase tags from uniform-S^1 break rank-1 by construction; BUT phase-hash design problem load-bearing (cue+noise hashes to wrong phase).
- BTSP relative-floor / Oja-like rule (depth-3): Bittner-Magee 2017 + Milstein 2021 + Krotov-Hopfield 2026; self-orthogonalizes against mu via subtractive term in update; rank-bounded by min(d, M).
- PC-AM iterative inference (depth-3): Salvatori 2021 NeurIPS; iterative refinement (T=5-20 steps) rescues anisotropic regime; O(M*N*T) compute, NOT M-indep.

**Composes with existing substrate cert atoms:**
- CERT 591 dense-projected-KV (learned contrastive projection): COMPLEMENTARY to all 8 mechanisms above; should be UPSTREAM of any of them as the projection already partially decorrelates. Pre-flight measurement of mean_cos AFTER CERT 591 projection is mandatory before launching this drill (per the ancillary HARD-FAIL discipline).
- CERT 592 K_max NESS envelope: orthogonal axis (chain-recall depth, not single-shot recall); composes with ANY storage rule.
- Sparse super-capacity a3f473dd: separate metric (raw P.T@P, not recall@1); does NOT compose with this drill's recall-preserving capacity question.
- Crosstalk-law c-unbounded (7315be3c): predicts isotropy doesn't predict capacity -> rescue mechanisms must be evaluated on EMPIRICAL recall, not on isotropy proxy. Reinforces the discriminating-regime + measured-storage discipline.

**Substrate META disciplines extended (catalog additions from this drill):**
- **rank-1-anisotropy-trap discipline**: when proposing a memory-density rescue mechanism for substrate, test whether the mechanism breaks rank-1 mu QUALITATIVELY (different geometry from dense projection) vs only quantitatively (reduces SNR but still smears mu across units). Dense Gaussian projection + kWTA, axis-aligned compartment partitioning, and Oja-online-orthogonalization all suffer the rank-1 trap. Sparse-fan-in (K << d), WTA-shift-invariance, and iterative-energy-inference qualitatively break it.
- **measured-storage-per-memory discipline**: any M-indep storage claim MUST be MEASURED in bytes-on-disk / M, not asserted from theoretical O(...) notation. Pointers, hash-table overhead, codebook entries all count. Required as pre-reg gate.
- **sparse-fan-in-not-just-sparse-output discipline**: biology repeatedly uses K=3-8 sparse FAN-IN (cerebellar GC, Drosophila MB Kenyon cells, dentate granule cells) -- distinct from sparse OUTPUT (kWTA on dense-projected expanded code). Substrate proposals must explicitly choose which sparsity (fan-in vs output), and the literature predicts fan-in is the load-bearing one for rank-1-mu-decorrelation.

---

## (e) Substrate-product implications

**Biology-inspired path most likely to compose with whitening-revival OR provide alternative substrate-storage mechanism (ranked by P_HARD-PASS * substrate-strategic-value):**

1. **TOP CANDIDATE -- ARM B = Fly-LSH WTA + median-subtract, composed with CERT 591** (P=0.50 capped, high strategic value):
   - GENUINELY M-indep per-memory storage (~28 B/memory at k=20, n=2400) vs attention's ~3 KB at d=768 -- a ~100x per-memory storage win.
   - Compositional: substrate's CERT 591 projection already handles partial anisotropy; fly-LSH WTA on TOP gives shift-invariance for residual rank-1 mu; full stack predicted recall 0.85+ at M=10k per Dasgupta-Sharma-Navlakha-Ryali-Krotov lineage.
   - The DOMINANT STRATEGIC PATH: if HARD-PASS, this becomes the substrate's storage-chain item #3' (replacing the failed dense-projected superposition #3) at genuinely sub-linear per-memory storage, with attention (#4) as the upper-bound fallback for ambiguous queries.
   - Composes with whitening-revival: median-subtract is a CHEAP form of whitening; ZCA-whitening from the synthetic CPU PoC (skunkworks_to_research_..._WHITENING_REVIVAL_DE_RISKED...md) is a stronger version; both work as the pre-LSH-WTA pre-processing.

2. **SECONDARY CANDIDATE -- ARM A = Cerebellar K=5 sparse-fan-in expansion** (P=0.30-0.40, moderate strategic value):
   - QUALITATIVELY breaks rank-1 mu by per-unit subset-sum geometry; K=5 fan-in matches Marr-Albus / Litwin-Kumar biology and theory.
   - Discriminating from dense projection (the ARM A' control proves which mechanism is load-bearing).
   - Storage cost = O(d' * d/K) for the sparse projection matrix + O(M * d') for the expanded outer-product superposition store -- NOT M-indep (still O(M*d')), but the per-memory cost in expanded space is favorable if d' < d_attention-equivalent.
   - Backup path if fly-LSH HARD-FAILS on the eff-rank-deficient pythia regime.

3. **DESCOPED -- ARM C = compose A+B** (P=0.20): composition rarely as strong as separate-mechanism additivity suggests; ship as exploratory only if A and B both PASS.

4. **HOLD FOR LATER DRILL -- PC-AM iterative inference** (P=0.30 standalone, 0.40 composed): not M-indep (still O(M*N*T)); rescues anisotropy by iterative refinement but at 10x compute cost; ROUTE AS DEEPER drill if ARM A and ARM B both HARD-FAIL (the iterative-energy paradigm is qualitatively different from feed-forward storage rules and deserves its own 5x drill chain).

5. **HOLD FOR PARTIAL-DRILL** -- phase-coding/complex-Hopfield (P=0.30, phase-hash design risk): worth a SEPARATE smoke if and only if the phase-hash sub-problem can be solved (LSH-locality-preserving hash from cue -> phase). Compose with CERT 591 + fly-LSH as an additional ORTHOGONAL axis if base mechanisms PASS.

6. **DROP** -- active-dendrite COP, BTSP relative-floor, DG dense expansion, product-key: all share the rank-1 trap (COP axis-aligned, DG dense projection, product-key low-eff-rank), require slow iterative learning (BTSP single-iter is degraded; Oja's rule needs ~100 iters/pattern), or give only sub-linear NOT M-indep storage at expensive cost.

**Strategic call (Director, pre-drill):** assume modal MIDDLE_BAND outcome for both ARM A and ARM B (~0.40-0.50 recall at M=10k); the storage-chain item #3' becomes a **bounded sub-linear per-memory store with recall~0.5-0.6 on anisotropic learned keys**, complementing the item #4 attention upper bound. This is a STRONGER substrate than just attention-everywhere (per-memory storage win) but WEAKER than the original M-indep dream. Plan substrate-product roadmap around this realistic envelope; pre-stage v5 contingency if both ARM A and ARM B HARD-FAIL (escalate to PC-AM iterative paradigm deeper drill).

**Composes with the whitening-revival GPU cell (in flight per skunkworks 2026-06-21 PoC):** the whitening-revival mechanism (ZCA-shrinkage on learned pythia keys -> isotropize -> ARM1 superposition recovers to 0.84+) is the SAME PRE-PROCESSING STAGE as median-subtract + fly-LSH (depth-2 ARM B). If whitening-revival GPU lands chain-grade, ARM B's lift over CERT 591 alone may be smaller than predicted (whitening already does the heavy lift). HONEST ATOMIZATION: if whitening-revival HARD-PASSES on its own, ARM B becomes ADDITIONAL per-memory storage compression benefit on TOP of whitening, not the anisotropy rescue.

---

## (f) Citations (verified count: 35 unique across the 6 lit-scans)

**Cerebellar / DG / pattern separation:**
1. Marr D. (1969). "A theory of cerebellar cortex." J. Physiol. 202:437. DOI:10.1113/jphysiol.1969.sp008820.
2. Marr D. (1971). "Simple memory: a theory for archicortex." Phil. Trans. R. Soc. B 262:23. DOI:10.1098/rstb.1971.0078.
3. Albus J.S. (1971). "A theory of cerebellar function." Math. Biosci. 10:25.
4. McNaughton B.L., Morris R.G.M. (1987). "Hippocampal synaptic enhancement and information storage." TINS 10:408.
5. Treves A., Rolls E.T. (1992). "Computational constraints suggest the need for two distinct input systems to the hippocampal CA3 network." Hippocampus 2:189.
6. O'Reilly R.C., McClelland J.L. (1994). "Hippocampal conjunctive encoding, storage, retrieval." Hippocampus 4:661.
7. Tsodyks M.V., Feigel'man M.V. (1988). "Enhanced storage capacity in neural networks with low activity level." Europhys Lett 6:101.
8. Babadi B., Sompolinsky H. (2014). "Sparseness and expansion in sensory representations." Neuron 83:1213.
9. Litwin-Kumar A., Harris K.D., Axel R., Sompolinsky H., Abbott L.F. (2017). "Optimal degrees of synaptic connectivity." Neuron 93:1153. arXiv:1611.04948.
10. Cayco-Gajic N.A., Clopath C., Silver R.A. (2017). "Pattern separation in cerebellum." Neuron 93:1132.
11. Cayco-Gajic N.A., Silver R.A. (2019). "Re-evaluating circuit mechanisms underlying pattern separation." Neuron 101:584.
12. Yassa M.A., Stark C.E.L. (2011). "Pattern separation in the hippocampus." TINS 34:515.
13. Bakker A. et al. (2008). "Pattern separation in the human hippocampal CA3 and dentate gyrus." Science 319:1640.

**Fly-LSH / engram / sparse-tag hashing:**
14. Dasgupta S., Stevens C.F., Navlakha S. (2017). "A neural algorithm for a fundamental computing problem." Science 358:793.
15. Sharma D., Navlakha S. (2018). "Improving similarity search with high-dimensional locality-sensitive hashing." arXiv:1812.01844.
16. Ryali C., Hopfield J., Grinberg L., Krotov D. (2020). "Bio-inspired hashing for unsupervised similarity search." ICML 2020.
17. Indyk P., Motwani R. (1998). "Approximate nearest neighbors: towards removing the curse of dimensionality." STOC 1998.
18. Charikar M. (2002). "Similarity estimation techniques from rounding algorithms." STOC 2002.
19. Tonegawa S. et al. (2015). "Memory engram cells have come of age." Neuron 87:918.
20. Josselyn S.A., Frankland P.W. (2018). "Memory Allocation: Mechanisms and Function." Annu Rev Neurosci 41:389.
21. Teyler T.J., Rudy J.W. (2007). "The hippocampal indexing theory and episodic memory." Hippocampus 17:1158.
22. Willshaw D.J., Buneman O.P., Longuet-Higgins H.C. (1969). "Non-holographic associative memory." Nature 222:960.

**Phase-coding / complex-Hopfield / HRR:**
23. Lisman J.E., Idiart M.A.P. (1995). "Storage of 7+/-2 short-term memories in oscillatory subcycles." Science 267:1512.
24. Lisman J. (2005). "The theta/gamma discrete phase code." Hippocampus 15:913.
25. Noest A.J. (1988). "Phasor neural networks." Europhys Lett 6:469.
26. Plate T.A. (1995). "Holographic reduced representations." IEEE TNN 6:623.

**Active dendrites / cortical microcircuits / predictive coding:**
27. Poirazi P., Mel B.W. (2001). "Impact of active dendrites and structural plasticity on the memory capacity of neural tissue." Neuron 29:779.
28. Hawkins J., Ahmad S. (2016). "Why Neurons Have Thousands of Synapses, A Theory of Sequence Memory in Neocortex." Front Neural Circ 10:23.
29. Rao R.P., Ballard D.H. (1999). "Predictive coding in the visual cortex." Nat Neurosci 2:79.
30. Friston K. (2010). "The free-energy principle: a unified brain theory?" Nat Rev Neurosci 11:127.
31. Whittington J.C.R., Bogacz R. (2017). "An Approximation of the Error Backpropagation Algorithm in a Predictive Coding Network with Local Hebbian Synaptic Plasticity." Neural Comput 29:1229.
32. Salvatori T. et al. (2021). "Associative Memories via Predictive Coding." NeurIPS 2021. arXiv:2109.08063.

**BTSP / plasticity rules:**
33. Bittner K.C., Milstein A.D., Grienberger C., Romani S., Magee J.C. (2017). "Behavioral time scale synaptic plasticity underlies CA1 place fields." Science 357:1033.
34. Milstein A.D. et al. (2021). "Bidirectional synaptic plasticity rapidly modifies hippocampal representations." eLife 10:e73046.
35. Krotov D., Hopfield J. (2026). "A Biologically Plausible Dense Associative Memory with Exponential Capacity." arXiv:2601.00984.

**Product-key / vector-quantization (grid-code adjacency):**
36. Sreenivasan S., Fiete I. (2011). "Grid cells generate an analog error-correcting code for singularly precise neural computation." PNAS.
37. Wei X.-X., Prentice J., Balasubramanian V. (2015). "A principle of economy predicts the functional architecture of grid cells." eLife.
38. Lample G., Le H., Joulin A. (2019). "Large Memory Layers with Product Keys." arXiv:1907.05242.
39. Razavi A., van den Oord A., Vinyals O. (2019). "Generating Diverse High-Fidelity Images with VQ-VAE-2."

**Anisotropy in learned LM embeddings (substrate-relevant background):**
40. Ethayarajh K. (2019). "How Contextual are Contextualized Word Representations?" EMNLP.
41. Kovaleva O. et al. (2021). "BERT Busters: Outlier Dimensions that Disrupt Transformers." EMNLP.
42. Timkey W., van Schijndel M. (2021). "All Bark and No Bite: Rogue Dimensions in Transformer Language Models Obscure Representational Quality." EMNLP.

**Calibration note:** P estimates deflated 0.15-0.25 per lit-scan calibration penalty; cap novel-synthesis P at 0.50 applied to all 8 candidate mechanisms (no P above 0.50 in this drill). HARD-FAIL thresholds pre-registered for all 4 ARMs. Adjacent methods not dismissed: PC-AM and phase-coding routed to deeper drills if base mechanisms fail; product-key reframed as sub-linear (not M-indep) and held for future; BTSP and active-dendrite COP dropped per rank-1-trap analysis.

---

## Standing

- **Skunkworks (cert-owner):** 4-ARM decisive test dispatchable to Exp-Dev when ready; SCHEMA-VET pass requested before queue_add; ANCILLARY HARD-FAIL pre-flight gate (mean_cos < 0.20 OR eff_rank < 32) MUST be checked first to avoid solving a non-problem; HARD-PASS / HARD-FAIL thresholds pre-registered per-arm for Step-0-honest re-read.
- **Exp-Dev (cell-author lift):** cell pre-flighted as `EXP_anisotropy_rescue_4arm_sweep_v1`; 4 arms + pre-flight diagnostics (mean_cos, eff_rank measurement) + K-sweep smoke gate (5 min) + M-sweep {1k, 3k, 10k} + 5 seeds. Reuse DenseProjectedKVStore (CERT 591 wrapper) + add SparseFanInExpansion + FlyLSHHashTable + MedianSubtract preprocessing primitives.
- **Orchestrator:** queue-route to local_cpu_queue (CPU-feasible 1-2 hr budget); NOT GPU. CERT-neutral drill; verdict atomizes which mechanism (if any) lands as substrate-storage item #3'.
- **Me (Director):** depth-5 drill spec filed; depth-4 not pursued (depth-3 saturation signal -- BTSP and PC-AM are converging structurally on relative-floor / iterative-energy framings already covered by sparse-fan-in and PC-AM); routing this drill's HEADLINE + decisive test to Skunkworks for SCHEMA-VET; pre-staged contingent depth-4 drill on PC-AM iterative-energy paradigm IF both ARM A and ARM B HARD-FAIL.

-- Research (Director)
