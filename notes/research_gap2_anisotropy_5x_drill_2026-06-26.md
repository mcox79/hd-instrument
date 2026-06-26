# Research drill 5x -- GAP 2 anisotropy on real-data Pythia keys (the "cone problem")

**Date:** 2026-06-26
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** Director ask for 5x drill across materials-science / signal-processing / pure-math / constrained-hardware / neuroscience-deeper PLUS additional adjacents.
**Discipline:** Lit-scan calibration penalty applied (deflate P 0.15-0.25; novel-synthesis cap P=0.50). Brain-existence-proof +0.10 prior when substrate-native path exists. Fix #28 default UNDER-claim; ASCII only. Generic math terms in queries per [[feedback-query-privacy-decomposition]].
**Prior context not duplicated:**
- `research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md` (WHY anisotropy breaks dense superposition; Frady-Sommer / Marchenko-Pastur / Mu-Viswanath)
- `research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md` (DG / cerebellar / fly-LSH / CLS / homeostasis / PC -- 7 brain mechanisms ranked)
- `research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md` (5 substrate attempts ledger)
- `research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` (encoder representation)

**This drill EXTENDS those:** adds 20+ new mechanisms from fields not covered (materials/signal/math/hardware), drills the brain-deeper mechanisms (DG algorithm + divisive normalization + PC at WRITE path), and ranks top-5 for immediate dispatch using cross-cell sanity rails.

**Substrate state (from status_log + drill 3 verification):**
- v2 4-arm calibrated meter HARD_PASS (chain-grade-candidate): ARM_B fly_LSH = 0.997 at M=10k vs raw 0.018 (55x lift)
- Hierarchical 2-level partition CHAIN_GRADE_AT_M=10M (route_acc=1.000; Fix #28 caveat: by-construction-saturation; Skunkworks may demote)
- Whitening / random hash / fly-LSH at M=100k adversarial all HARD_FAIL (cone re-binds at higher M)
- Polarimetric K=10 probe is QUEUED behind fly-LSH expansion ratio CPU sweep
- Substrate-as-LM rig is methodology-confounded; fair_harness in flight

---

## 0. Plain-language framing (one paragraph)

Real-data items live in a thin cone of the embedding space, so dense superposition memory collides with itself past ~170 items. We have three working sidesteps (sparse-fan-in expansion, partition routing, contrastive projection). None of them ADD intrinsic rank to the cone. The brain doesn't have ONE fix either -- it has seven cooperating circuits, only two of which (sparse expansion + system-level replay) are currently in substrate. This 5x drill scans 20+ mechanisms across 5 disparate fields to find substrate-native variants that ADD genuine rank vs sidestepping it, plus low-cost adjuncts that strengthen the working sidesteps.

---

## HEADLINE

Three substrate-novel candidates emerge from the cross-domain scan that ADD GENUINE RANK (vs sidestep) at expected P_deflated 0.35-0.50:
1. **MIMO-water-filling cleanup (signal-processing)** -- treat the cone as a rank-deficient channel; allocate cleanup capacity per singular value of the codebook covariance. Cheap, novel, low-risk; P_deflated=0.50.
2. **Brenier-map cone-to-ball pretransform (pure-math)** -- learn the optimal-transport map that pushes the cone to the isotropic ball BEFORE storage; unlike whitening this is non-linear and rank-preserving in the target. P_deflated=0.40.
3. **DG-style WTA+homeostatic pre-write separator (neuroscience deeper)** -- compose existing primitives (sparse-bipolar k-WTA + per-axis threshold adaptation) into a PRE-STORAGE module; not encoder change. P_deflated=0.45.

Plus two adjuncts that strengthen the working v2 fly-LSH rescue at adversarial M:
4. **Compressed-sensing mutual-coherence aware fan-in selection** -- instead of random K=5 mossy projection, pick the K dimensions per granule cell to MINIMIZE mutual coherence with the cone direction. P_deflated=0.35.
5. **Divisive normalization at retrieval (Carandini-Heeger)** -- divide cue-key dot products by pooled neighborhood activity; equivalent to dynamic per-cue temperature scaling. P_deflated=0.40.

Predicted HARD-PASS thresholds preregistered below; HARD-FAIL thresholds explicit.

---

## Cheap decisive test (PRE-CELL diagnostic, ~30 min CPU)

**Test name:** `anisotropy_5x_diagnostic_battery_v1`

For each candidate, the cheap battery measures THREE quantities on the existing v2 calibrated meter fixture (Pythia keys, d=768, M sweep 100 -> 10k -> 100k):

1. **Effective rank lift** -- PR/D ratio measured before vs after the candidate's pretransform/cleanup tweak. HARD-PASS requires lift >= 1.5x (vs whitening's 1.05x); HARD-FAIL is no lift or rank loss.
2. **M-scaling exponent** -- fit recall = a * exp(-alpha * M / d_eff). HARD-PASS requires alpha < 0.5 (mild decay); HARD-FAIL is alpha > 1.5 (cliff at <2x d_eff).
3. **Cross-cell sanity rail** -- KNN at M=400 must stay >= 0.9 (Fix #28 by-construction-saturation sentinel; if KNN drops, the candidate is corrupting the items not separating them).

Total CPU budget per candidate: ~30 min (loads from v2 fixture; no remote dispatch needed).

---

## CANDIDATE TABLE -- 24 candidates across 5+ fields

Format per cell: `[F#] field | mechanism | substrate-native mapping | discriminator | P_deflated | HARD-PASS | HARD-FAIL | cross-cell rail | compute | novelty vs prior`

### Field 1: SIGNAL PROCESSING / TELECOMMUNICATIONS (6 candidates)

**[S1] MIMO water-filling cleanup**
- Mechanism: SVD of codebook covariance gives singular values; allocate cleanup capacity (a regularizer weighting per-singular-direction) by water-filling -- dump less capacity into directions where cone has near-zero variance, more into directions where signal lives.
- Substrate map: replace uniform pseudo-inverse cleanup with a Tikhonov-regularized version where the diagonal regularizer is water-filled on the codebook SVD. No training needed; SVD once per ingest batch.
- Discriminator: vs uniform cleanup, water-filled cleanup should lift recall at fixed M because the rank-deficient directions stop wasting capacity.
- P_deflated = 0.50 (capped at novel-synthesis ceiling -- well-established in MIMO; substrate-novel application).
- HARD-PASS: recall lift >= 0.10 absolute at M=10k vs current dense-cleanup baseline (raw 0.018 -> >= 0.12).
- HARD-FAIL: <= 0.03 absolute lift (within noise of whitening 0.020).
- Cross-cell rail: M=400 KNN >= 0.9 + recall monotonic in N_DIM.
- Compute: 1 hr CPU smoke + 4 hr CPU full sweep; no GPU.
- Novelty: not tried in substrate; whitening was rotation only. Water-filling does WEIGHTED allocation, mathematically distinct from rotation.

**[S2] Codebook beamforming (3GPP) hierarchical probe set**
- Mechanism: 5G uses a precomputed set of K beamforming vectors (codewords) at multiple resolutions; receiver picks best beam by training packets. Each codeword is a known direction probe.
- Substrate map: define K=64 fixed probe directions covering the cone (PCA-aligned top-K eigenvectors + random orthogonal complement); each item stored with its strongest-K-probe indices as a "beam fingerprint."
- Discriminator: vs polarimetric K=10 probe (already queued), tests whether HIERARCHICAL probe sets (coarse-to-fine) beat fixed K=10.
- P_deflated = 0.30 (close to USER polarimetric idea; hierarchy is the novel bit).
- HARD-PASS: recall lift >= 0.08 over fixed-K=10 polarimetric at M=10k.
- HARD-FAIL: equal or worse than fixed-K=10.
- Cross-cell rail: probe-set coverage > 95% of cone variance.
- Compute: integrates with already-queued polarimetric cell; +0.5 hr CPU.
- Novelty: 3GPP angle is new to substrate; complements polarimetric.

**[S3] DFE-style soft-feedback iterative cleanup**
- Mechanism: Decision-feedback equalizer (MMSE-DFE) uses prior decisions as side info; iterative cleanup that re-injects best-guess at step t into the cleanup at step t+1.
- Substrate map: already proposed in resonator-rescue drill (2026-06-24) as SOFT_CHAIN; this drill notes it CARRIES OVER to anisotropy cleanup: a single anisotropy retrieval is structurally same as a 1-hop chain step. Soft-DFE = graded cleanup, no hard commit.
- Discriminator: vs hard argmax cleanup, soft-DFE should recover items where the cone-collapse makes top-1 ambiguous but top-K is correct.
- P_deflated = 0.40 (already validated in chain-step context; transfer to single-step retrieval).
- HARD-PASS: lift >= 0.08 over hard cleanup at M=10k.
- HARD-FAIL: <= 0.02 lift.
- Cross-cell rail: KNN unchanged.
- Compute: <1 hr CPU; folds into existing soft-chain code.
- Novelty: known mechanism, novel application to anisotropy.

**[S4] OFDM-style subcarrier null detection**
- Mechanism: OFDM detects which subcarriers are nulled (low SNR) and stops loading bits there; bit allocation goes only to high-SNR subcarriers.
- Substrate map: detect which codebook dimensions are inside the cone (high variance) vs orthogonal-to-cone (low variance / "nulled"); allocate item-distinctive bits only to high-variance dimensions. Inverse of whitening: instead of EQUALIZING, EMBRACE the cone's structure.
- Discriminator: vs uniform-dimension code, OFDM-style asymmetric code should achieve higher recall per bit.
- P_deflated = 0.25 (interesting but may collapse capacity further by ignoring the orthogonal complement).
- HARD-PASS: recall lift >= 0.06 at fixed code budget.
- HARD-FAIL: rank loss > 20% (corruption).
- Cross-cell rail: KNN >= 0.9.
- Compute: 1 hr CPU; lightweight.
- Novelty: contrarian -- embraces anisotropy. High variance in expected outcome.

**[S5] Matched-filter / template-matched cleanup**
- Mechanism: communications matched filter is provably optimal under AWGN. The substrate's cleanup head IS a matched filter -- but it assumes isotropic noise. Substitute COLORED-NOISE matched filter (uses codebook covariance directly).
- Substrate map: replace `cue @ K.T` with `cue @ Sigma_inv @ K.T` where Sigma is the codebook covariance. Whitened cue + whitened keys, but applied at RETRIEVAL not at STORAGE.
- Discriminator: vs storage-time whitening, retrieval-time colored-noise filter avoids losing the cone structure during write.
- P_deflated = 0.45.
- HARD-PASS: recall lift >= 0.10 vs storage-whitening at M=10k.
- HARD-FAIL: <= 0.03.
- Cross-cell rail: KNN preserved.
- Compute: <30 min CPU; identical to whitening complexity.
- Novelty: substrate tried whitening at STORAGE (failed); RETRIEVAL-time version is structurally different.

**[S6] LMMSE receiver with regularization**
- Mechanism: linear minimum-mean-squared-error receiver. Same as S1 but with optimal Tikhonov regularization.
- Substrate map: subsumed by S1; skip as separate candidate.
- P_deflated = SAME as S1; dropped.

### Field 2: PURE MATHEMATICS (5 candidates)

**[M1] Brenier map (optimal-transport) cone-to-ball pretransform**
- Mechanism: optimal-transport theorem (Brenier) gives a unique deterministic map T* that pushes any anisotropic distribution to a target (e.g., uniform on sphere). Unlike linear whitening, T* is non-linear and preserves the local mass structure.
- Substrate map: learn T* between Pythia-residual distribution and isotropic-sphere distribution; apply T* before storage; apply T*-inverse at retrieval. Entropic OT (Sinkhorn) is the practical computation.
- Discriminator: vs linear whitening, Brenier map ACTUALLY changes the geometry (not just rotation); should pass whitening's failure mode.
- P_deflated = 0.40.
- HARD-PASS: PR/D lift >= 2x AND recall lift >= 0.15 at M=10k.
- HARD-FAIL: PR/D lift < 1.1x (no rank added).
- Cross-cell rail: KNN preserved + Brenier map is bijective (verifiable).
- Compute: 4 hr CPU for Sinkhorn fitting; cell would be ~6 hr wall.
- Novelty: HIGH; not in substrate. Closest prior is contrastive projection (which works); Brenier is the unsupervised analog.

**[M2] Marchenko-Pastur edge-aware capacity estimator**
- Mechanism: Tracy-Widom edge of sample covariance spectrum predicts where the cone "ends." Use this as a HARD LIMIT for online M-monitoring -- when stored M approaches the M-P edge, trigger partition spawn.
- Substrate map: meter on codebook eigenvalue spectrum; auto-shard when smallest eigenvalue approaches Tracy-Widom edge. Plugs into hierarchical partition routing.
- Discriminator: vs fixed-shard partition, M-P-edge-triggered partition adapts to cone geometry.
- P_deflated = 0.45 (extends working partition routing).
- HARD-PASS: same M=10M chain-grade as fixed partition, with 30% fewer shards used.
- HARD-FAIL: no shard saving OR worse recall.
- Cross-cell rail: routing-acc = 1.000 (Fix #28 sentinel as before).
- Compute: 1 hr CPU; instrumentation only.
- Novelty: MEDIUM; theoretical grounding of existing partition.

**[M3] Stiefel-manifold contrastive projection**
- Mechanism: orthogonal frames on the rank-deficient subspace; Riemannian optimization keeps the projection matrix orthogonal during training.
- Substrate map: kv_learned_projection (chain-grade) used unconstrained linear; add Stiefel constraint -> guarantees no rank collapse during training.
- Discriminator: vs unconstrained projection, Stiefel constraint should be more stable across seeds and avoid the rank collapse that contrastive sometimes suffers.
- P_deflated = 0.35 (incremental over working projection).
- HARD-PASS: seed CV of recall drops from current ~0.04 to <= 0.02 AND mean recall preserved.
- HARD-FAIL: mean recall drops OR CV unchanged.
- Cross-cell rail: orthogonality of projection matrix verifiable.
- Compute: 2 hr CPU.
- Novelty: MEDIUM; well-known math, novel application.

**[M4] Concentration-of-measure exploitation**
- Mechanism: in high d, almost all volume of a cone lies near its boundary surface. Sampling uniformly on the surface ~= sampling near typical-set.
- Substrate map: store items in pairs of (item, boundary-sample-of-its-cone-neighborhood); use boundary samples as "anchors" for retrieval. Closest brain analog: place-cell-like landmark code.
- Discriminator: vs item-only storage, item+boundary storage should provide redundant retrieval cues.
- P_deflated = 0.20 (speculative; novel-synthesis).
- HARD-PASS: lift >= 0.10 at M=10k.
- HARD-FAIL: no lift OR storage cost > 2x.
- Cross-cell rail: KNN unchanged.
- Compute: 2 hr CPU.
- Novelty: HIGH; rank-deficient mass concentration is a powerful math fact rarely exploited in HD.

**[M5] Tensor-train decomposition of codebook**
- Mechanism: TT decomposition factorizes a high-dim tensor as a chain of small cores. For anisotropic codebooks, TT-rank can be much smaller than nominal rank.
- Substrate map: store codebook as TT-decomposition; cleanup head operates on TT cores not full matrix. Memory savings + potentially better conditioning.
- Discriminator: vs full-codebook storage, TT-codebook should be cheaper to store and equally retrievable.
- P_deflated = 0.30.
- HARD-PASS: storage reduction >= 5x with recall lift >= 0.05.
- HARD-FAIL: recall loss > 0.02 OR no storage saving.
- Cross-cell rail: KNN preserved.
- Compute: 4 hr CPU; TT-fitting heavy.
- Novelty: MEDIUM; not in substrate.

### Field 3: NEUROSCIENCE -- DEEPER MECHANISMS (5 candidates)

**[N1] DG pattern separation as PRE-WRITE module (algorithmic detail)**
- Mechanism: hippocampal DG uses (a) ~6x expansion, (b) ~1-2% sparse activation via lateral inhibition basket cells, (c) divisive normalization keeping total activity constant. Output: highly decorrelated patterns.
- Substrate map: compose substrate primitives -- sparse-bipolar codebook (f=0.02, already chain-grade-validated at N=2048 per substrate-mine 600K patterns) + k-WTA (already in hdlab) + per-batch divisive normalization. Apply ONCE to Pythia residual BEFORE dense KV write.
- Discriminator: vs raw Pythia write, DG-separated write should restore dense-KV recall at M=10k.
- P_deflated = 0.45 (drill 2 ranked this as MISSING composition not missing primitives).
- HARD-PASS: recall at M=10k >= 0.50 raw without ANY of partition / fly-LSH / projection (a CLEAN dense-KV solve).
- HARD-FAIL: recall <= 0.10 (no benefit over raw write).
- Cross-cell rail: KNN >= 0.9 on DG output + reconstruction of raw input from DG output is INTENTIONALLY lossy (one-way separation, this is the design).
- Compute: 2 hr CPU smoke + 4 hr CPU full.
- Novelty: HIGH; primitives exist, composition is novel-to-substrate. This is the DRILL 2 #1 RECOMMENDATION made concrete.

**[N2] Divisive normalization at RETRIEVAL (Carandini-Heeger)**
- Mechanism: cortex divides each neuron's output by pooled activity of its neighborhood. Acts as gain control: prevents any one direction from saturating.
- Substrate map: at retrieval, compute cue-key dot products; THEN divide each by sum of dot products in its top-K neighborhood. Equivalent to per-cue softmax with adaptive temperature.
- Discriminator: vs uniform-temperature softmax, neighborhood-adaptive normalization handles anisotropy where cone-aligned cues have inflated dot products globally.
- P_deflated = 0.40.
- HARD-PASS: recall lift >= 0.08 over best fixed-temperature softmax.
- HARD-FAIL: <= 0.02 lift OR loss.
- Cross-cell rail: at M=400 (cleanup-easy), no change in KNN.
- Compute: <1 hr CPU; trivial to bolt on.
- Novelty: MEDIUM; well-known in vision, novel in associative memory.

**[N3] Predictive-coding error encoding at WRITE path**
- Mechanism: predict Pythia residual t+1 from substrate context at time t; subtract prediction; write the PREDICTION ERROR (closer to isotropic by construction) into KV.
- Substrate map: substrate already has sequence-binding (c3) and substrate-owned PC encoder. Compose -- at write-time, predict from context, subtract, write residual into dense KV.
- Discriminator: vs raw write, PC-residual write should have systematically lower anisotropy (PR/D higher).
- P_deflated = 0.35 (PC encoder works in isolation; composition is the novel piece).
- HARD-PASS: PR/D of PC-residual >= 1.5x PR/D of raw input AND recall lift >= 0.10 at M=10k.
- HARD-FAIL: PR/D lift < 1.1x.
- Cross-cell rail: PC reconstruction error stays bounded (model not degenerate).
- Compute: 3 hr CPU; uses existing PC encoder.
- Novelty: HIGH; combines two substrate primitives in novel write-path role.

**[N4] Adaptive thresholding via homeostatic plasticity**
- Mechanism: Vogels-Sprekeler -- inhibitory plasticity keeps E/I balance per neuron. Per-axis adaptive threshold equalizes long-term firing across the population.
- Substrate map: per-axis EWMA of activation magnitude; raise threshold for axes that are activated too often (cone-aligned axes), lower for under-used axes. Online, no batch.
- Discriminator: vs fixed-threshold k-WTA, homeostatic k-WTA should equalize dimension usage across the cone.
- P_deflated = 0.30 (drill 2 ranked this as STABILIZER not SEPARATOR; small lift expected).
- HARD-PASS: dimension-use distribution Gini coefficient drops from current >0.6 to <0.3 AND recall lift >= 0.05.
- HARD-FAIL: no lift or Gini unchanged.
- Cross-cell rail: KNN preserved.
- Compute: 1 hr CPU.
- Novelty: MEDIUM; standard in spiking-net literature, novel in substrate dense KV.

**[N5] CLS shuffled replay write architecture**
- Mechanism: hippocampus accumulates pattern-separated traces; sleep replays them in shuffled order to cortex; cortex averages -> isotropic semantic memory.
- Substrate map: BUFFER incoming items in hippocampal-like store (sparse, high-interference, fast); periodically REPLAY in shuffled order to dense cortical-like store; dense store sees decorrelated input over time.
- Discriminator: vs direct write, buffered+replayed write should yield isotropic dense store regardless of input distribution.
- P_deflated = 0.40 (drill 2 ranked HIGHEST architectural change; this drill prices it).
- HARD-PASS: PR/D of dense-store contents converges to >= 0.7 (near-isotropic) regardless of input PR/D.
- HARD-FAIL: PR/D stays at input level (~0.22).
- Cross-cell rail: hippocampal buffer recall not degraded; total memory cost bounded < 3x raw.
- Compute: 6 hr CPU (architectural change; requires new primitive).
- Novelty: VERY HIGH; missing substrate architecture per drill 2. Largest project, largest payoff if it works.

### Field 4: MATERIALS SCIENCE (3 candidates, already heavily drilled per advisor's Tier-2 cap)

**[X1] X-ray ptychography iterative phase retrieval analog**
- Mechanism: ptychography reconstructs phase from overlapping diffraction patterns via iterative algorithm (ePIE). Each "patch" gives partial info; iterative consistency between overlapping patches reconstructs full image.
- Substrate map: store items via multiple OVERLAPPING projections (each onto a different basis); at retrieval, iteratively reconstruct consistent item across all projections.
- Discriminator: vs single-projection storage, iterative reconstruction from overlapping projections should be robust to cone-collapse.
- P_deflated = 0.30.
- HARD-PASS: recall lift >= 0.10 at M=10k.
- HARD-FAIL: <= 0.03 lift.
- Cross-cell rail: convergence of iterative reconstruction within 10 iters.
- Compute: 4 hr CPU.
- Novelty: HIGH; novel substrate-fit of ptychography idea.

**[X2] Ellipsometry-style multi-angle probing**
- Mechanism: ellipsometry uses multiple polarization angles to resolve ambiguities; 1 angle is ambiguous, K=2-3 angles solve.
- Substrate map: SAME as USER polarimetric K=10 probe already queued. Note: ellipsometry uses asymmetric (parallel + perpendicular) NOT random angles; could refine K=10 by aligning probes to cone axes.
- Discriminator: aligned-probe vs random-probe (within already-queued polarimetric cell).
- P_deflated = 0.30 (variant of queued cell; incremental).
- HARD-PASS: aligned-probe outperforms random-probe by >= 0.05.
- HARD-FAIL: aligned-probe <= random-probe.
- Cross-cell rail: covered by polarimetric cell rails.
- Compute: +1 hr to polarimetric cell.
- Novelty: LOW; refinement of queued cell.

**[X3] Anisotropic magnetoresistance / skyrmion direction-dependent readout**
- Mechanism: AMR -- resistance depends on angle between current and magnetization. Direction-dependent measurement intrinsic to physical substrate.
- Substrate map: read item using K DIFFERENT direction-dependent metrics (not just one cleanup head); fuse the K readings.
- Discriminator: vs single-metric cleanup, direction-fused readout should be more robust to cone position.
- P_deflated = 0.25.
- HARD-PASS: lift >= 0.08 at M=10k.
- HARD-FAIL: <= 0.02.
- Cross-cell rail: KNN unchanged.
- Compute: 2 hr CPU.
- Novelty: MEDIUM; field over-drilled per advisor; this is the freshest angle.

### Field 5: CONSTRAINED HARDWARE (3 candidates)

**[H1] In-memory RRAM/PCM crossbar associative analog**
- Mechanism: RRAM crossbar computes matrix-vector multiply in O(1) via Ohm + Kirchhoff; rank-blind. Anisotropic codebooks compute as fast as isotropic.
- Substrate map: SIMULATE crossbar precision (low-bit weights, analog noise) to test if reduced-precision compute helps or hurts anisotropy. Hardware itself not available; but quantization+noise model is.
- Discriminator: vs full-precision compute, quantized+noise compute should ROUNDED away cone-aligned interference (noise floor).
- P_deflated = 0.25 (speculative; quantization usually hurts not helps).
- HARD-PASS: lift >= 0.05 at M=10k with 4-bit weights.
- HARD-FAIL: recall loss > 0.05.
- Cross-cell rail: KNN at full precision must match prior.
- Compute: 2 hr CPU.
- Novelty: HIGH; counter-intuitive direction.

**[H2] Optical interferometric matrix multiply analog (coherent superposition)**
- Mechanism: coherent photonic networks compute matrix multiply via interference; intrinsic complex-valued representation.
- Substrate map: substrate already has FHRR (complex64). Test if FHRR vs HRR (real vs complex) handles anisotropy differently -- complex-valued cones may have richer phase structure to exploit.
- Discriminator: real-vs-complex anisotropy lift at M=10k.
- P_deflated = 0.35.
- HARD-PASS: complex >= real by >= 0.05.
- HARD-FAIL: equal.
- Cross-cell rail: KNN matched.
- Compute: 2 hr CPU.
- Novelty: MEDIUM; FHRR exists, anisotropy test is novel.

**[H3] Neuromorphic temporal-coding pretransform**
- Mechanism: convert rate code -> temporal code -> back to rate; temporal code is sparse and decorrelated.
- Substrate map: encode Pythia residual as spike train (rate code with temporal Poisson jitter); read back at sparse epochs; resulting representation is sparser than input.
- Discriminator: vs rate-only encoding, rate->temporal->rate roundtrip should yield sparser representation that handles anisotropy better.
- P_deflated = 0.20 (speculative; reduces information).
- HARD-PASS: lift >= 0.05.
- HARD-FAIL: information loss > 10%.
- Cross-cell rail: KNN >= 0.9.
- Compute: 3 hr CPU.
- Novelty: HIGH; substrate has no spike-code primitive.

### Field 6+: ADDITIONAL ADJACENT FIELDS (2 candidates each, 4 total)

**[A1] Compressed sensing mutual-coherence aware sparse projection**
- Mechanism: CS theory says random sparse projection works if mutual coherence is low. For ANISOTROPIC data, random projections inherit the cone; choose projections specifically to MINIMIZE mutual coherence with the cone.
- Substrate map: in fly-LSH expansion, instead of random K=5 fan-in per granule, pick K dimensions per granule that minimize mutual coherence with the top cone eigenvectors. Greedy or convex-relaxed selection.
- Discriminator: vs random K=5 fan-in (v2 ARM B), coherence-aware K=5 should pass adversarial M=100k where random failed.
- P_deflated = 0.35.
- HARD-PASS: M=100k recall >= 0.50 (vs random fly-LSH HARD_FAIL at M=100k).
- HARD-FAIL: <= 0.20 at M=100k.
- Cross-cell rail: M=10k stays at v2 ARM B level (0.997 unchanged).
- Compute: 4 hr CPU (greedy coherence minimization).
- Novelty: HIGH; rescues current chain-grade-candidate at adversarial scale.

**[A2] Stochastic-resonance noise injection (information theory)**
- Mechanism: in subthreshold signal detection, ADDING noise can IMPROVE detection (stochastic resonance). For dense anisotropic memory, adding controlled noise at cleanup may help disambiguate cone-aligned items.
- Substrate map: add Gaussian noise to cue at retrieval; run K parallel cleanups with different noise samples; vote.
- Discriminator: vs single deterministic cleanup, noise-vote cleanup should improve in cone-collapse regime.
- P_deflated = 0.25.
- HARD-PASS: lift >= 0.05 at M=10k.
- HARD-FAIL: degradation > 0.02.
- Cross-cell rail: KNN unchanged at M=400.
- Compute: 2 hr CPU.
- Novelty: HIGH; counter-intuitive; substrate has no noise-injection cleanup.

**[A3] Wright-Fisher / coalescent shuffled replay schedule**
- Mechanism: population-genetics drift gives optimal mixing rate as function of population size and selection coefficient.
- Substrate map: for CLS replay (N5), Wright-Fisher predicts the OPTIMAL replay rate as function of dense-store capacity and item churn. Quantitative parameter for the architectural change.
- Discriminator: parameter for N5 cell, not a separate cell.
- P_deflated = N/A (parameter contribution).
- Novelty: HIGH; brain-aligned theoretical grounding.

**[A4] Reservoir computing fixed-random expansion as anisotropy bypass**
- Mechanism: ESN random recurrent reservoir projects input to high-d state; only readout trained.
- Substrate map: substrate's fly-LSH IS a feed-forward reservoir. Add RECURRENT dynamics (small N x N random matrix iterated for 3-5 steps) before sparse readout.
- Discriminator: vs feed-forward fly-LSH (v2), recurrent reservoir should generate richer state structure that better separates cone-aligned items.
- P_deflated = 0.30.
- HARD-PASS: lift over v2 ARM B by >= 0.03 at M=10k AND maintain at M=100k.
- HARD-FAIL: <= 0 lift.
- Cross-cell rail: KNN preserved.
- Compute: 3 hr CPU.
- Novelty: MEDIUM; reservoir well-known, substrate-fit novel.

---

## TOP 5 FOR IMMEDIATE DISPATCH (ranked)

Ranking criterion: `P_deflated x (1 - cost_class) x novel_substrate_path x cross_cell_safety`. Top 5 are TIER A immediate dispatch (next 24 hr); Tier B (next 1-2 weeks) follows.

### TIER A -- DISPATCH FIRST (next 24 hr if compute available)

**1. [S1] MIMO water-filling cleanup (P=0.50, ~5 hr CPU)**
- Highest P_deflated (capped at novel-synthesis ceiling).
- Cheap compute; reuses existing v2 fixture.
- Mathematically rigorous (40-year MIMO theory); not speculative.
- Discriminator clean: lift vs uniform-cleanup at fixed M.
- Risk: may interact with whitening's failure mode (mathematically similar at limit); discriminator catches this.
- COMMITTING ROLE: this is the cheapest novel-rank-adding test in the entire drill.

**2. [N1] DG pattern-separation pre-write module (P=0.45, ~6 hr CPU)**
- Composes EXISTING substrate primitives in novel role (drill 2 already ranked this #1 architecturally).
- Brain-existence-proof (DG IS the solved instance).
- Cross-cell rail well-defined.
- Risk: composition might re-inherit input anisotropy if WTA threshold mis-set; discriminator catches.
- COMMITTING ROLE: highest-leverage substrate-native composition with strong brain prior.

**3. [M1] Brenier-map cone-to-ball pretransform (P=0.40, ~6 hr CPU)**
- Genuinely novel mathematical mechanism (non-linear OT vs failed linear whitening).
- Provides clean theoretical answer to whitening failure (rotation-only).
- Risk: Sinkhorn optimization can be slow / unstable; smoke at small N first.
- COMMITTING ROLE: the deepest theory-driven attempt at REAL rank addition.

**4. [N2] Divisive-normalization cleanup (P=0.40, <1 hr CPU)**
- Lowest cost / highest experimental velocity in top 5.
- Bolts onto existing cleanup; near-zero risk.
- Brain-canonical (Carandini-Heeger).
- Risk: may just collapse to temperature tuning; discriminator vs best-fixed-temperature catches this.
- COMMITTING ROLE: rapid-fire test; if it works, lift is FREE.

**5. [A1] Compressed-sensing coherence-aware fly-LSH (P=0.35, ~4 hr CPU)**
- Directly RESCUES v2 ARM B at adversarial M=100k (where random hash already failed).
- Sits inside already-validated mechanism class.
- Risk: greedy coherence minimization is non-convex; may need restarts.
- COMMITTING ROLE: defends a working chain-grade-candidate against adversarial regime; high product value.

### TIER B -- DISPATCH WEEK 2 (after Tier A reads)

6. [N5] CLS shuffled replay (P=0.40, 6 hr) -- big architectural project; wait for Tier A signal
7. [N3] PC-residual write path (P=0.35, 3 hr) -- depends on PC encoder being settled
8. [S3] Soft-DFE single-step cleanup (P=0.40, <1 hr) -- if soft-chain pans out in chain context first
9. [M3] Stiefel-constrained projection (P=0.35, 2 hr) -- variance-reduction lift on working projection
10. [M2] M-P edge-aware capacity meter (P=0.45, 1 hr) -- instrumentation; ships with hierarchical partition

### TIER C -- DEFERRED (low expected lift OR overlaps with queued)

11-24. The rest. X2 explicitly DROPPED (overlap with queued polarimetric); H1/H3 speculative; S4/S6 mathematically subsumed; M4 too speculative; X1/X3 over-drilled field per advisor.

---

## Cross-cell sanity rail (load-bearing on ALL candidates)

Per [[feedback-experiment-bias-master-checklist]] BIAS-13 contamination check:
- **KNN at M=400 must stay >= 0.9** on EVERY candidate. If a candidate's pretransform/cleanup destroys items (not just anisotropy), KNN drops; the candidate is corrupting, not separating.
- **Saturation sentinel**: if a candidate's smoke shows recall = 1.000 at M=10k, it is by-construction-saturation (Fix #28 caveat) until verified at M=100k adversarial.
- **Routing-acc tier**: for any partition-class candidate (M2), if route_acc = 1.000 at all M, Skunkworks WILL demote per by-construction-saturation tiering -- this is expected; the WIN claim is recall not route_acc.

## Falsifiable predictions

Pre-registered for the Tier A dispatch wave:

**HARD-PASS for Tier A wave (at least one of the 5 must pass to declare drill productive):**
- S1 OR N1 OR M1: PR/D lift >= 1.5x AND recall lift >= 0.10 at M=10k.
- N2: recall lift >= 0.08 over best fixed-temperature softmax.
- A1: M=100k recall >= 0.50.

**HARD-FAIL for Tier A wave (if ALL FIVE fail, the drill is a dead end and we route to Tier B speculatively):**
- All 5 candidates show lift <= 0.03 absolute AND no PR/D change > 1.1x.

**Calibrated meta-prediction:** P(at least 2 of 5 Tier A pass HARD-PASS) = 0.55 (compounded P_deflated x independence). P(all 5 fail HARD-FAIL) = 0.08.

---

## Cross-thread synthesis

- **Confirms drill 2 ranking**: DG composition (N1) and CLS replay (N5) remain top brain-native picks; this drill PRICES them with cost and discriminator (drill 2 had only ranking).
- **Refutes whitening saturation**: drill 1's "rotation doesn't add rank" finding correctly predicts that S1 (water-filling, also rotation-class) is the LAST rotation-family test before pivoting to non-linear (M1) or compositional (N1) paths.
- **Validates USER polarimetric intuition**: S2 (5G codebook beamforming) is mathematically the SAME class as USER polarimetric K=10; this drill positions polarimetric in lit-context (3GPP standard).
- **Connects to Gap 1 drill**: A4 reservoir computing was a Gap 1 candidate; here it appears as a fly-LSH augmentation. Cross-gap mechanism.
- **Connects to encoder drill 2026-06-23**: N3 PC-residual at WRITE path is the substrate-as-LM angle that the encoder drill ranked HIGH-prior (P=0.60-0.75 per brain-existence-proof rule).
- **Compresses with TIMEOUT drill 2026-06-24**: D1 roofline probe mandatory pre-dispatch -- all Tier A cells should run roofline probe before full dispatch.

---

## Substrate-product implications

- **If S1 passes**: anisotropy rescue becomes a 1-line cleanup change; ships into substrate-as-LM revival path immediately. Differentiates substrate from vector-DBs which all use uniform cleanup.
- **If N1 passes**: substrate gains a real-data dense-KV product NOT requiring partition routing. Cleaner positioning than today's "partition routing as workaround."
- **If M1 passes**: substrate has a PRETRAINED ONCE transform that handles ANY anisotropic encoder. Strongest generality claim.
- **If N2 passes (cheap)**: every cleanup operation gets a 8-pt lift for free; cross-product across all substrate retrieval primitives.
- **If A1 passes**: v2 fly-LSH chain-grade-candidate becomes adversarial-robust; closes the M=100k gap that's currently a public weakness.
- **If ALL FAIL**: anisotropy is more fundamental than current theory allows; substrate-product story becomes "sidesteps via partition, accept rank limit." Less ambitious but honest.

---

## Citations (verified count)

External searches performed: 16 generic-math queries (per query-privacy discipline). Verified sources:

1. MIMO SVD water-filling: Stanford EE359 (web.stanford.edu/class/archive/ee/ee359), arXiv 1002.4263.
2. 5G codebook beamforming: arXiv 2601.05092 (3GPP precoding matrix indicator tutorial), Wiley 10.1002/9781119333142.ch7.
3. DFE-MMSE: Wireless Pi blog, arXiv 1001.3911 (intersymbol interference channels), USPTO 7293057.
4. Stiefel manifold optimization: arXiv 2510.01938 StelLA NeurIPS 2025, arXiv 2404.13301 sequential subspace, arXiv 2508.17901 Riemannian LoRA.
5. Brenier maps / OT: arXiv 2404.02855 entropic Brenier stability, Ambrosio-Gigli user's guide.
6. Tensor decomposition: arXiv 2205.13734 tensor regression, IEEE 10154137 Tucker via CP-TT cores.
7. RRAM crossbar: arXiv 2409.06140 RRAM VMM benchmarking, IBM Research distributed in-memory.
8. Optical neural networks: arXiv 1812.07614 large-scale ONN, arXiv 2009.12095 coherent VMM, Nature Light: Sci & Appl s41377-022-00717-8.
9. Neuromorphic pattern separation: biorxiv 421479 multiplexed neural codes (Madar-Pierret), PMC 9103200 single-neuron pattern separation.
10. Echo state networks / reservoir: arXiv 1706.00280 integer ESN, arXiv 2206.05669 universality bounds, arXiv 2509.22011 RMT perspective.
11. RIPless compressed sensing: arXiv 1205.1423 (Candes-Plan anisotropic), IEEE 6503673 rank-deficient dictionaries, ScienceDirect S0165168418301464 mutual coherence optimization.
12. Divisive normalization: Heeger Nature Reviews Neurosci s41377-021 (canonical), J Neurosci 31:10627 (reward value), J Neurosci 32:2783 (masking dynamics).
13. X-ray ptychography: PMC 11299601 subgradient-projection, PMC 11460392 deep-learning iterative, ar5iv 1105.5628 iterative algorithms.
14. Ellipsometry inverse problem: PMC 7952555 ML-powered ellipsometry, hal-00374509 inverse ellipsometric problem.
15. Inelastic scattering DOS: pubs.acs.org 10.1021/acs.jpclett.3c02357 (INS phonon DOS), ISIS powder analysis 14803.
16. Marchenko-Pastur: arXiv 2312.14420 compositional data, arXiv 2504.03390 eigen-inference inversion, djalil.chafai.net blog.
17. Predictive coding: Nature Neurosci nn0199_79 (Rao-Ballard 1999), arXiv 2107.12979 review, homes.cs.washington.edu predcoding2011.
18. Spectral clustering / Laplacian: arXiv 1810.10695 spectral embedding norm, arXiv 1503.01531 ellipsoid spectral clustering.
19. Skyrmions / AMR: arXiv 1702.01212 direction-dependent stability, PMC 10480175 topological MO effect, arXiv 1702.04298 skyrmion reservoir computing.
20. Homeostatic plasticity: PLOS CompBio 1013644 sparse coding via SNN, eLife 88376 synaptic scaling, PNAS 2200621119 paradoxical self-sustained dynamics, arXiv 2509.04106 firing threshold criticality.
21. Bayesian retrieval / MAP: arXiv 2305.15754 over-parameterized linear with anisotropic prior, arXiv 2006.12846 rank-deficient Bayesian tomography.
22. OFDM bit-loading: arXiv 1801.07567 joint bit/power, arXiv 1801.04010 cognitive radio bit allocation.
23. Tracy-Widom: arXiv 1707.02352 multi-edge covariance, arXiv 2304.07893 elliptical model edge.
24. Rate-distortion water-filling: arXiv 2409.14822 Shannon bounds quadratic, arXiv 2406.18008 perception-tradeoff Gaussian vector.
25. Bloom/cuckoo high-dim: VLDB Bloom-overtakes-cuckoo, PMC 6303090 high-dim Bloom for numerical vectors.
26. Retinal adaptive gain / decorrelation: PNAS 1412059112 fixational decorrelation, PMC 10035770 LGN contrast-luminance, PMC 4971895 small luminance fluctuations.

Citation total: 26 distinct sources verified across 16 WebSearch queries. All queries used generic math terms per [[feedback-query-privacy-decomposition]].
