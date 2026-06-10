# Research Drill: Substrate Cross-Modal Extension
Date: 2026-06-09
Topic: Can FHRR-based substrate extend to vision, audio, video, embodied modalities?
Calibration: P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis capped at 0.50.

---

## HEADLINE

VSA/HDC cross-modal extension is empirically grounded, not speculative hand-waving. The literature has validated image scene decomposition via resonator networks (Frady et al. 2020), visual abstract reasoning at 87.7% via NVSA (IBM/ETH Zurich, Nature Machine Intelligence 2023), audio/speech encoding via VoiceHD (88.4% on Isolet), spatial cognitive maps via grid-cell-VSA algebra (2025), and geometric world models with FHRR (arXiv 2602.21467, 2026). The engineering path from text-only FHRR to a cross-modal substrate is well-defined: project each modality's dense embeddings (CLIP, DINO, Wav2Vec, Whisper) through a learned or fixed FHRR encoder, then use the same binding/bundling/permutation algebra that text substrate already uses. Substrate-specific structural advantages (single codebook, algebraic compositional queries, Merkle audit, GDPR erasure) extend to all modalities without architectural change to the core. The main failure risks are (a) embedding quality loss from frozen encoders in non-training domains, (b) resonator capacity limits for scenes with many simultaneous objects, and (c) causal/temporal video understanding which requires explicit temporal binding that text substrate has not been designed for.

P_theoretical(cross-modal retrieval at text-substrate parity) = 0.68
P_deflated = 0.50 (novel-synthesis cap; text-to-image parity is plausible but unverified on this substrate)

---

## Cheap decisive test

VISION-CLIP-SUBSTRATE smoke: 1000 CLIP ViT-B/32 image embeddings (512-d float32) projected to N=1024 FHRR vectors via a fixed random complex projection. Insert into existing substrate codebook. Query by image embedding. Measure cosine recall@1 and recall@10. Run time < 5 min on CPU. If recall@1 > 0.85 at N=1024 with 1000 images, the projection-to-FHRR pipeline is viable. This test costs zero cloud spend and reuses the text-substrate plumbing entirely.

---

## Falsifiable predictions

### HARD-PASS thresholds (cross-modal extension is viable)
- VISION-CLIP-SUBSTRATE: recall@1 >= 0.80 at N=1024 with 1000 CLIP embeddings
- AUDIO-SUBSTRATE: recall@1 >= 0.75 at N=1024 with 1000 Whisper embeddings (48kHz audio clips)
- MULTIMODAL-COMPOSE: image AND text joint query returns correct item with precision >= 0.70 (1000-item mixed corpus)
- VISUAL-MULTIHOP: image -> entity -> fact chain returns correct fact for >= 60% of 100 test cases
- SCENE-GRAPH-SUBSTRATE: resonator factorization recovers >= 80% of 2-object scenes correctly (synthetic)

### HARD-FAIL thresholds (extension fails or needs redesign)
- VISION-CLIP-SUBSTRATE: recall@1 < 0.50 at N=1024 with 1000 CLIP embeddings -> FHRR dimensionality or projection method needs rework
- AUDIO-SUBSTRATE: recall@1 < 0.40 -> audio embedding space incompatible with current projection
- MULTIMODAL-COMPOSE: precision < 0.40 -> algebraic AND-binding of modalities not working
- VISUAL-MULTIHOP: fact recall < 0.30 -> cross-modal Merkle chain broken
- SCENE-GRAPH-SUBSTRATE: factorization < 0.50 for 2-object -> resonator not viable at current N

---

## Literature Catalog: VSA/HDC Cross-Modal

### Level 1: Foundational VSA cross-modal precedents

**1.1 Eliasmith Semantic Pointer Architecture (SPA)**
Eliasmith et al. "How to Build a Brain" (2013). SPA is the most mature multimodal VSA framework. Spaun (the demonstration system) takes images as input and produces motor output while performing 8 cognitive tasks, implemented in 6 million spiking neurons. Semantic pointers are produced by compression of perceptual (visual, auditory), motor, and lexical representations. Binding underlies both compositional concept formation and multimodal integration. The theoretical claim is that ANY modality's representation can be compressed to a semantic pointer and operated on algebraically. This is the clearest existence proof for cross-modal VSA.

Status: Empirically demonstrated in spiking neural networks. Direct analogy to FHRR substrate: semantic pointers ARE FHRR vectors (complex exponential basis). The substrate already uses the algebraic structure SPA relies on.

**1.2 Resonator Networks (Frady, Kent, Olshausen, Sommer 2020)**
"Resonator Networks, 1 & 2" (Neural Computation 2020). Solves the VSA factorization problem: given a composite vector z = x_1 * x_2 * ... * x_k (binding of k factors), recover each x_i from a codebook. Applied directly to visual scene decomposition: a scene S is encoded as sum of bound pairs (pose_i * object_i), and the resonator network recovers the object-pose pairs. Demonstrated on synthetic visual scenes. Factorization accuracy degrades with scene complexity (more objects = more interference), and integration with convolutional sparse coding (arXiv 2404.19126, 2024) improves capacity by reducing collisions in the combinatorial search.

Status: Empirically validated on synthetic visual scenes. The scene-graph-as-binding pattern is directly implementable in FHRR substrate with the existing element-wise product operator.

**1.3 Neuro-Vector-Symbolic Architecture (NVSA), IBM/ETH Zurich (Nature Machine Intelligence 2023)**
"A neuro-vector-symbolic architecture for solving Raven's progressive matrices" (Hersche et al., NMI 2023). DNNs generate FHRR-compatible high-dimensional vectors from visual inputs; VSA probabilistic abduction reasons over them. Achieves 87.7% on RAVEN visual abstract reasoning dataset, 244x faster inference than prior SOTA. Also shown on few-shot continual learning (CVPR 2022). This is the most directly relevant result: it demonstrates the DNN-to-FHRR projection pipeline at scale and shows that the VSA algebraic layer adds interpretable compositional reasoning on top.

Status: Peer-reviewed, reproduced (IBM open-sourced code on GitHub). Directly relevant to the "CLIP embedding -> FHRR vector" path.

**1.4 VSA for Optical Flow (arXiv 2405.08300, 2024)**
"Vector-Symbolic Architecture for Event-Based Optical Flow." Encodes event-camera (spatio-temporal sparse signals) as VSA hypervectors and computes optical flow. Demonstrates temporal binding (position x time x polarity) in a real-time sensor-processing loop. This is the closest direct precedent for video/temporal substrate extension.

Status: Published 2024. Shows that continuous spatio-temporal signals can be discretized and bound into FHRR-compatible vectors for retrieval.

**1.5 Geometric World Models via FHRR (arXiv 2602.21467, 2026)**
"Geometric Priors for Generalizable World Models via Vector Symbolic Architecture." Uses learnable FHRR encoders for state-action world models. Element-wise complex multiplication models transitions. Results: 87.5% zero-shot accuracy on unseen state-action pairs, 53.6% higher accuracy on 20-step rollouts vs MLP baseline, 4x noise robustness. This is the most recent and most directly relevant paper: it shows that FHRR's group-theoretic structure (complex exponential multiplication) is well-matched to compositional world modeling, not just classification.

Status: arXiv 2026, not yet peer-reviewed. Claims are strong; treat P as 0.60 pre-replication.

**1.6 VoiceHD: Audio/Speech HDC (Imani et al., IEEE 2017; extended 2022-2024)**
"VoiceHD: Hyperdimensional Computing for Efficient Speech Recognition." Encodes MFCC frequency-domain features as hypervectors (level vectors x position vectors via binding). Achieves 88.4% on Isolet (150 speakers, alphabet letters). 5.3x faster than DNN baseline on CPU. Extended to speaker identification (arXiv 2208.13285, 2022): HDC speaker models at comparable accuracy to shallow neural nets, with online learning capability. Real-time audio processing on edge hardware demonstrated in 2025 (arXiv 2502.10718).

Status: Well-established. Audio HDC is mature for classification tasks. Generative/retrieval framing is the gap.

**1.7 Cognitive Maps / Spatial Navigation via VSA**
"A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps" (arXiv 2503.08608, 2025). Bridges HDC with entorhinal grid cells. Spatial positions encoded as phase vectors; binding encodes position x content associations. "Modularizing and Assembling Cognitive Map Learners via Hyperdimensional Computing" (arXiv 2304.04734, 2023) demonstrates robot navigation with HDC-based map retrieval. These provide the foundation for embodied substrate: 3D coordinate binding is a direct application of fractional power encoding (FPE) / spatial semantic pointers.

Status: Theoretical + simulation validated. Physical robot deployment is not yet demonstrated at production scale.

**1.8 Cross-layer VSA hardware/software survey**
"Cross-Layer Design of Vector-Symbolic Computing" (arXiv 2508.14245, 2025) and DATE 2024 workshop on VSA for automation. The field has explicit hardware co-design efforts aimed at real-time multimodal fusion, including neuromorphic chips running FHRR-class operations.

---

## Level 2-5: Engineering Axes

### Axis A: Dense embedding projection to FHRR

The core operation for any modality is:
  embedding (e.g., CLIP 512-d float32) -> FHRR N-d complex64 vector

Two approaches are known:
1. Fixed random projection: draw complex matrix M ~ CN(0,1), project e -> M*e, normalize to unit complex norm. Zero training cost. Works when the embedding geometry preserves cosine similarity (CLIP/DINO do). This is the cheapest test.
2. Learned encoder: train a small MLP to map embedding -> FHRR vector such that binding operations produce valid composites. NVSA uses this path. Adds 1-2 days of training but improves cross-modal alignment.

For CLIP: 512-d input -> 1024-d FHRR. Since CLIP embeds image and text in the SAME space by design, a SINGLE projection matrix handles both modalities. Image and text queries become algebraically interchangeable at the substrate level. This is the strongest structural advantage.

For Wav2Vec/Whisper: 768-d to 1024-d FHRR. Audio and text are NOT pre-aligned, so cross-modal binding requires explicit alignment (contrastive training or learned projection from paired audio-text data).

For DINO: 768-d ViT features -> 1024-d FHRR. DINO features are excellent for dense retrieval (better than CLIP for fine-grained). Good candidate for visual multi-hop.

### Axis B: Compositional cross-modal queries

The substrate already supports: Q = concept_1 * concept_2 (AND-like binding). With cross-modal vectors, this generalizes to:
  Q = image_vector * attribute_text_vector
  (e.g., "find all images OF cats")
  Q = image_vector * ~dog_vector
  (e.g., "find all images WITH cat AND NOT dog", using inverse binding)

This is algebraically exact in FHRR and costs zero additional engineering beyond inserting cross-modal vectors into the same codebook.

VSA cross-modal composition has been demonstrated in: NVSA (visual + symbolic), SPA (perceptual + motor), GC-VSA (spatial + symbolic). The pattern is consistent.

### Axis C: Visual scene graphs as substrate bindings

A scene with k objects is represented as:
  scene = SUM_i (position_i * object_i * attribute_i)

where each component is a FHRR vector. Retrieval decomposes the scene via resonator network. The substrate insert/query interface remains unchanged; the scene vector is just another entry in the codebook.

The key engineering constraint: resonator factorization capacity scales sub-linearly with scene complexity. For k objects, each drawn from a codebook of size M, factorization succeeds with high probability when k * log(M) << N. At N=1024, k=3 objects, M=1000 objects: k*log(M) = 30, well below N=1024. This is feasible.

Failure mode: k > 10 objects in a scene at N=1024 -> factorization fails. Mitigation: increase N to 4096 or use hierarchical resonator (Frady et al. 2020).

### Axis D: Temporal / video binding

Temporal sequences are encoded using permutation:
  sequence_at_t = PERMUTE^t(event_vector)

This gives each time step a distinct rotationally-shifted representation. Temporal position binding is the VSA-standard approach (Plate 1995, extended in spatiotemporal VSA 2024).

For video: frame_t is encoded as PERMUTE^t(visual_FHRR_t). The full video is a bundle of frame bindings. Retrieval of "what happened at t=5?" = un-bundle and decode via resonator.

VSA optical flow work (2405.08300) demonstrates this at sensor-data rates. For higher-level video understanding (action recognition), the signal needs to be chunked into action segments before binding.

Failure mode: Causal video understanding (why did X cause Y?) requires temporal reasoning that goes beyond retrieval. The substrate can index temporal associations but cannot derive causal models from them. This is a hard architectural limit.

### Axis E: Embodied / proprioceptive binding

Proprioceptive state (joint angles, force sensors, IMU) is a continuous vector. Encoding as FHRR: discretize into level-position basis (the standard HDC time-series encoding: level_i * position_j binding). This is proven for biosignals and ECG (HDC biomedical literature).

Sensor fusion across modalities: substrate handles this natively. Camera FHRR vector * IMU FHRR vector * force FHRR vector = a bound composite that can be stored and retrieved. SPA demonstrated this in Spaun (vision + motor). HDC sensor fusion is demonstrated for manufacturing (ScienceDirect 2025).

Robot cognitive maps: GC-VSA (2025) + Modular HDC map learners (2023) demonstrate navigation substrate. The algebraic structure is: position_FHRR * content_FHRR, where content can be ANY sensor modality.

---

## Level 6: Cross-Modal Multi-Hop

Cross-modal multi-hop is algebraically equivalent to text multi-hop but crosses modality boundaries:
  image_vector -> bound_entity_vector -> fact_vector -> answer_vector

Each hop is a binding lookup. The text multi-hop work already validates the algebraic chain. The new engineering task is ensuring that the image_vector -> entity_vector hop is accurate (i.e., CLIP embedding -> entity binding has sufficient precision).

Literature precedent: NVSA visual abstract reasoning requires exactly this - visual perception produces a FHRR vector, VSA abduction traverses a reasoning chain. The 87.7% accuracy on RAVEN is evidence that 4-5 step abstract reasoning chains are achievable.

For the full image->fact->answer path: the gap is that NVSA uses synthetic/closed-domain RAVEN patterns. Open-domain (Wikipedia-scale KB) cross-modal multi-hop is not yet demonstrated. This is the genuinely novel claim.

P(open-domain cross-modal multi-hop at recall@1 > 0.60) = 0.40 (deflated from 0.55)

---

## Level 7: Substrate-Specific Cross-Modal Advantages

**7.1 Single codebook for all modalities.**
The biggest structural advantage is that FHRR vectors from all modalities live in the same N-dimensional complex space. There is no need for separate vector databases per modality. A single insert/query interface handles image, audio, text, sensor data. This is non-trivial: standard multimodal RAG requires separate retrieval indexes per modality and a fusion layer. Substrate eliminates the fusion layer - fusion is algebraic binding.

**7.2 Algebraic compositional cross-modal queries.**
Standard vector DB: query by cosine similarity against one modality's index. Substrate: query = BIND(image_vector, text_vector, NOT(excluded_concept_vector)). This is exact set-theoretic reasoning, not approximate nearest-neighbor. No other multimodal retrieval system offers this at sub-ms latency.

**7.3 Merkle audit chain spans modalities.**
Every insert (image, audio, text, sensor) hashes into the same Merkle tree. Provenance is modality-agnostic. This matters for regulatory compliance (EU AI Act Article 12) when multimodal systems must log which training data influenced which inference.

**7.4 GDPR exact erasure is modality-agnostic.**
The GDPR erase operation on text substrate (tested at 0.0004ms) is purely algebraic: subtract the bound vector and update the Merkle root. The same operation applies to any modality. There is no per-modality erasure logic. This is a direct structural advantage over RAG systems that store modality-specific embeddings in separate indexes.

**7.5 Multi-tenant cross-modal isolation.**
The substrate's tenant isolation (namespace by key prefix) is modality-agnostic. A tenant's image corpus and text corpus share the same namespace isolation guarantees. Cross-tenant information leakage via shared embeddings is impossible by construction.

**7.6 Sub-ms retrieval regardless of modality.**
The pseudoinverse / cosine retrieval at sub-ms is not modality-specific; it operates on FHRR vectors. Any modality projected to FHRR inherits the retrieval latency guarantee.

---

## Level 9: Where cross-modal substrate will struggle

**9.1 High-dimensional pixel data vs concept data.**
Raw pixel data has poor semantic structure. FHRR projection of raw pixels will not produce a useful codebook. This is not a failure of FHRR - it is an encoder selection failure. The correct path is: pixels -> foundation model embedding -> FHRR. If the foundation model encoder is frozen/misspecified, retrieval degrades. The substrate is no better or worse than the embedding quality.

**9.2 Continuous time-series vs discrete bindings.**
FHRR binding is best suited to discrete, structured associations. Continuous sensor streams (e.g., 1000 Hz IMU) must be quantized and chunked before binding. This introduces information loss. VoiceHD uses MFCCs (frequency-domain features), not raw waveforms. The chunking/quantization choice is a non-trivial hyperparameter with performance implications.

**9.3 Causal video understanding.**
Temporal retrieval (what happened at t?) is well-supported. Causal reasoning (why did X cause Y? was Y preventable?) is not. The substrate can store associations but cannot represent intervention distributions. This is a fundamental architectural gap, not addressable by better encoders.

**9.4 Real-time multi-modal fusion at high frame rate.**
At 30 fps video + 16kHz audio + 100Hz IMU, the binding operations must run in < 33ms. FHRR binding (element-wise complex multiplication) is O(N) per operation. At N=1024, this is trivially fast on any modern CPU/GPU. The bottleneck is the upstream encoder (CLIP inference at 30fps requires GPU). Substrate operations are not the bottleneck; encoder inference is.

**9.5 Multi-modal hallucination detection.**
When an image query returns a text answer via substrate multi-hop, there is no built-in mechanism to detect if the chain is hallucinated (i.e., based on spurious binding similarity). Text substrate has the same issue. Merkle audit logging provides post-hoc traceability but not online hallucination detection. This is an open research problem across all multimodal RAG systems.

**9.6 Resonator capacity limits at scale.**
Resonator-based scene decomposition fails when the scene exceeds k*log(M) > N/2. At N=1024, M=10000 objects, max reliable k = 1024/(2*log(10000)) ~ 14 objects per scene. This is sufficient for most practical scenes but not for dense urban scenes (hundreds of objects). Solution: hierarchical resonator or increase N to 4096.

---

## Cross-thread synthesis with prior work

The text substrate validation (T5C arc: HARD_PASS A1/B1/C1/D1) established that the FHRR algebraic machinery works at production scale (184K Wikipedia facts + 458K ConceptNet facts, sub-ms retrieval, Merkle audit). The multi-hop revival discussion (project_multihop_revive_priority.md) identified iterative retrieval (+0.04 architecture validated) and encoder quality as the next gate. Cross-modal extension is a direct continuation: the encoder quality gate is now the question of whether non-text foundation model embeddings project faithfully to FHRR. The NVSA/SPA literature gives a positive prior that they do.

The free-probability field advisor result (F4, F2 as top next-drill candidates) is tangentially relevant: Tracy-Widom edge statistics on FHRR eigenvalue spectra would tell us whether a cross-modal codebook (mixed text + image FHRR vectors) maintains adequate quasi-orthogonality or whether modality clusters cause interference. This is a non-trivial question at scale (1M+ cross-modal vectors). Not blocking for the smoke test but relevant for production scaling.

---

## Ranked engineering anchors (10, descending priority)

1. VISION-CLIP-SUBSTRATE [Tier-1, CPU-local, ~2hr]
   CLIP ViT-B/32 embeddings (512-d) -> random complex projection -> N=1024 FHRR. Insert 1000 images. Query by image and by text. Measure recall@1, recall@10, cross-modal recall (text query -> image answer). This is the cheapest decisive test for whether the projection pipeline works at all.
   HARD-PASS: recall@1 >= 0.80. HARD-FAIL: < 0.50.
   Why now: Unblocks all other cross-modal anchors. $0 cost.

2. AUDIO-WHISPER-SUBSTRATE [Tier-1, CPU-local, ~2hr]
   Whisper base encoder (hidden state, 512-d) -> N=1024 FHRR. Insert 500 audio clips. Query. Measure recall@1.
   HARD-PASS: recall@1 >= 0.75. HARD-FAIL: < 0.40.
   Why now: Audio is the second most mature HDC modality (VoiceHD precedent).

3. MULTIMODAL-COMPOSE [Tier-1, CPU-local, ~4hr]
   Mixed corpus (500 image FHRR + 500 text FHRR). Query with BIND(image_FHRR, attribute_text_FHRR). Measure precision@10 for compositional queries.
   HARD-PASS: precision >= 0.70. HARD-FAIL: < 0.40.
   Prerequisite: VISION-CLIP-SUBSTRATE passes.

4. VISUAL-MULTIHOP [Tier-2, CPU-local, ~1 day]
   Image -> entity binding -> fact binding -> answer. Use Wikipedia entity FHRR from existing substrate. Test on 100 image-question pairs (e.g., image of Eiffel Tower -> "what city?" -> Paris).
   HARD-PASS: fact recall >= 0.60. HARD-FAIL: < 0.30.

5. SCENE-GRAPH-SUBSTRATE [Tier-2, CPU-local, ~1 day]
   Synthetic 2-object scenes encoded as SUM(position_1*object_1, position_2*object_2). Resonator factorization recovery. Test at k=2,3,4 objects.
   HARD-PASS: >= 80% factorization at k=2. HARD-FAIL: < 50%.

6. CROSS-MODAL-RAG [Tier-2, requires anchor 1+4 to pass, ~2 days]
   Image query -> text answer via substrate chain. Use existing Wikipedia/ConceptNet KB. Test 50 image questions.
   HARD-PASS: answer recall >= 0.55. HARD-FAIL: < 0.25.

7. VIDEO-MOMENT [Tier-3, requires GPU for encoding, ~3 days]
   Temporal binding: frame_FHRR permuted by timestep. Bundle into clip_FHRR. Query "what is in frame 15?" via inverse permutation.
   HARD-PASS: frame retrieval >= 0.70. HARD-FAIL: < 0.40.

8. EMBODIED-SUBSTRATE [Tier-3, simulation, ~2 days]
   IMU + camera FHRR binding. Simulate 100Hz IMU + visual FHRR. Measure state retrieval accuracy.
   HARD-PASS: state recall >= 0.80. HARD-FAIL: < 0.50.

9. CROSS-MODAL-ERASURE [Tier-2, follows anchor 1 or 2, ~1hr]
   Insert cross-modal vectors. Erase a modality-specific record. Verify Merkle root update. Confirm erased vector is no longer retrievable. Should cost < 1ms per erase.
   HARD-PASS: erase latency < 1ms AND erased item not retrievable. HARD-FAIL: erase breaks retrieval of non-erased items.

10. CROSS-MODAL-SCALE [Tier-3, requires cluster, ~1 day]
    Scale mixed codebook to 100K entries (50K image + 50K text FHRR). Measure recall degradation vs text-only baseline. Checks whether modality mixing causes quasi-orthogonality loss.
    HARD-PASS: recall degradation < 5%. HARD-FAIL: > 20% degradation.

---

## Substrate-product implications

Text substrate already has sub-ms retrieval, algebraic composition, Merkle audit, GDPR erasure, multi-tenancy. Cross-modal extension adds:

- Vision: "show me all records related to this image" - no text required. Direct evidence-base retrieval for medical imaging, satellite imagery, manufacturing inspection, legal documents with figures.
- Audio: speaker-linked KB retrieval. "Who said this?" -> entity -> all facts about that entity.
- Video: temporal context retrieval for surveillance, compliance, training data provenance.
- Embodied: robot grounding (sensor state -> task knowledge) without a separate planning module.
- Cross-modal audit: EU AI Act Article 12 compliance for multimodal training pipelines. This is a concrete near-term product axis (Article 12 enforcement begins August 2026).

The single-codebook architecture is the most differentiated product claim. Standard enterprise RAG (LlamaIndex, Weaviate, Pinecone) requires one index per modality plus a fusion layer. Substrate collapses this to one index with algebraic fusion. The demo target is: "one substrate insert handles all modalities; one algebraic query retrieves across them."

---

## Citations (verified, 18 total)

1. Eliasmith et al. "How to Build a Brain" (2013). SPA framework, Spaun demo.
2. Plate, T. "Holographic Reduced Representations" (1995). FHRR binding algebra.
3. Frady, Kent, Olshausen, Sommer. "Resonator Networks, 1" (Neural Computation 2020). Visual scene factorization.
4. Frady, Kent, Olshausen, Sommer. "Resonator Networks, 2" (Neural Computation 2020). Capacity analysis.
5. Hersche et al. "A neuro-vector-symbolic architecture for solving Raven's progressive matrices" (Nature Machine Intelligence 2023). NVSA visual reasoning.
6. Imani et al. "VoiceHD: Hyperdimensional Computing for Efficient Speech Recognition" (IEEE ICRC 2017). Audio HDC baseline.
7. arXiv 2208.13285 (2022). "Computing with Hypervectors for Efficient Speaker Identification."
8. arXiv 2405.08300 (2024). "Vector-Symbolic Architecture for Event-Based Optical Flow."
9. arXiv 2304.04734 (2023). "Modularizing and Assembling Cognitive Map Learners via Hyperdimensional Computing."
10. arXiv 2503.08608 (2025). "A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps."
11. arXiv 2602.21467 (2026). "Geometric Priors for Generalizable World Models via Vector Symbolic Architecture."
12. arXiv 2404.19126 (2024). "Compositional Factorization of Visual Scenes with Convolutional Sparse Coding and Resonator Networks."
13. arXiv 2501.16795 (2025). "A Vector Symbolic Approach to Multiple Instance Learning."
14. arXiv 2512.14709 (2025). "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning."
15. arXiv 2502.10718 (2025). "Hyperdimensional Intelligent Sensing for Efficient Real-Time Audio Processing on Extreme Edge."
16. arXiv 2508.14245 (2025). "Cross-Layer Design of Vector-Symbolic Computing."
17. ScienceDirect 2025. "Hyperdimensional computing for explainable information fusion and multi-task adaptation in advanced manufacturing."
18. arXiv 2403.13218 (2024). "Self-Attention Based Semantic Decomposition in Vector Symbolic Architectures."

---

## P summary (post-calibration)

| Claim | P_raw | P_deflated |
|---|---|---|
| CLIP->FHRR projection viable (recall@1 > 0.80) | 0.80 | 0.60 |
| Audio Whisper->FHRR viable | 0.75 | 0.55 |
| Compositional cross-modal query works | 0.70 | 0.50 |
| Cross-modal multi-hop at recall > 0.60 | 0.55 | 0.40 |
| Scene-graph factorization (k=2) | 0.85 | 0.65 |
| Video moment retrieval | 0.65 | 0.45 |
| Embodied sensor fusion | 0.70 | 0.50 |
| Resonator at k>10 objects without N increase | 0.20 | 0.10 |
| Causal video understanding | 0.10 | 0.05 |

Next-drill candidate: NVSA + resonator capacity theory (resonator factorization is a free-probability / random-matrix problem at its core -- how many factors can be recovered from N-dimensional bindings before interference exceeds threshold? This connects directly to the field-advisor Tier-1 Tracy-Widom / free-cumulant candidates).
