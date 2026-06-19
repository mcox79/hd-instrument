# Research Drill: T-BIND Cross-Modal 2x Refinement
Date: 2026-06-10
Trigger: PP-329 T-BIND-1 HARD_PASS crossmodal_recall=0.944 (25-scene FHRR holographic)
Mandate: Push to real video/audio data, mixed-rate (30Hz/44.1kHz/1kHz), adversarial cross-modal, production-scale 100-scene
Calibration: P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis capped at 0.50.

---

## HEADLINE

PP-329 T-BIND-1 established that FHRR holographic binding achieves crossmodal_recall=0.944 at 25 synthetic scenes. The 2x drill identifies five concrete push paths supported by fresh literature: (1) real-data mixed-rate encoding is feasible via HDC intelligent sensing at the extreme edge (arXiv 2502.10718, IEEE Access 2025) with O(N log N) cleanup now available (arXiv 2506.15793, MLPR 2025); (2) adversarial robustness of cross-modal binding is quantified and fragile in current multimodal encoders but VSA high-dimensionality provides inherent noise tolerance that standard embedding models lack (arXiv 2505.11895, 2509.14383); (3) the temporal binding window constraint from neuroscience (IPS/STG gating, ~60-260ms window, biorXiv 2025) maps directly onto a testable asynchrony tolerance threshold for FHRR permutation-based temporal encoding; (4) inverse effectiveness (superadditive binding when per-modality signal is weak) is empirically established in STS and pulvinar (Nature Comms 2025, Wiley EJN 2025) and predicts FHRR should gain most from binding exactly when per-modality recall is low; (5) production-scale 100-scene tests are now the gating question - the 25-scene HARD_PASS does not extrapolate directly because resonator interference scales as k*log(M), and the Efficient VSA from Histogram Recovery (arXiv 2511.01838, Reed-Solomon + Hadamard) offers a provable path to larger M without heuristics.

P_deflated(T-BIND production-scale 100-scene, crossmodal_recall >= 0.90) = 0.45
P_deflated(adversarial-McGurk robust, recall drop < 10%) = 0.35
P_deflated(mixed-rate 30Hz/44.1kHz temporal binding without resampling artifacts) = 0.40

---

## Cheap decisive test

**TBIND-REAL-25**: Take 25 real YouTube-style clips (1-5 sec each). Extract CLIP ViT-B/32 frame embeddings (30fps -> subsample to 1 frame/sec = 1-5 FHRR vectors per clip) and Whisper encoder states (16kHz, 512-d per 20ms window -> mean-pool per second). Project both to N=2048 FHRR via fixed random complex projection. Bind each clip as: clip_FHRR = MEAN_BUNDLE(SUM_t(PERMUTE^t(frame_FHRR_t) * audio_FHRR_t)). Insert 25 clip vectors. Query by visual-only, audio-only, and cross-modal (visual FHRR * audio_attribute_FHRR). Measure crossmodal_recall@1 and @5. Expected runtime: < 30 min on CPU. Cost: $0. Hard-pass: crossmodal_recall@1 >= 0.80. Hard-fail: < 0.50.

Rationale: This test moves from synthetic scenes (PP-329 T-BIND-1) to real data with real embedding variance, and exercises the PERMUTE-based temporal binding without introducing causal video reasoning.

---

## Falsifiable predictions

### HARD-PASS thresholds

- TBIND-REAL-25: crossmodal_recall@1 >= 0.80 on 25 real AV clips (CPU, N=2048)
- TBIND-100-SCENE: crossmodal_recall@1 >= 0.85 on 100-scene corpus (CPU, N=4096 or 2048+hierarchical)
- TBIND-MIXED-RATE: < 5% recall degradation when audio runs at 44.1kHz vs 16kHz (resampled FHRR temporal index)
- TBIND-ADVERSARIAL-MCGURK: recall drop < 15% when visual stream replaced by semantically incongruent visual (auditory content correct, visual content contradicts) - measures whether binding dominates one modality
- TBIND-LONG-DURATION (10-60 sec clips): crossmodal_recall@1 >= 0.75 with temporal chunking (10-sec segments bundled)
- TBIND-ATTENTION-SELECTIVE (100-scene, query = modality-specific attribute): precision@5 >= 0.70 on modality-specific queries

### HARD-FAIL thresholds

- TBIND-REAL-25: crossmodal_recall@1 < 0.50 -> projection method or binding algebra broken for real embeddings; redesign required before any further scale
- TBIND-100-SCENE: crossmodal_recall@1 < 0.65 -> resonator interference exceeds N; must increase N or use hierarchical decomposition
- TBIND-MIXED-RATE: > 20% recall degradation -> temporal quantization of mixed-rate audio-visual is the bottleneck; requires explicit rate-normalization
- TBIND-ADVERSARIAL-MCGURK: recall drop > 40% -> binding is dominated by one modality; cross-modal binding not providing robustness; architectural change needed
- TBIND-LONG-DURATION: crossmodal_recall@1 < 0.40 -> temporal PERMUTE accumulation degrades at long duration; temporal chunking strategy must be redesigned

---

## Level 1: Biology probes

### 1.1 Superior temporal sulcus (STS) and the Stein-Meredith principles

The 2025 sEEG study (Stereoelectroencephalography, PMC12528836) directly recorded from STS in 42 epilepsy patients during AV speech perception. Key quantitative results:
- Auditory response latency: 71 ms post-stimulus
- Visual speech response latency: 109 ms post-stimulus
- Integration in mid-posterior STG and STS: subadditive for intact stimuli, additive for degraded stimuli

The subadditive-for-intact, additive-for-degraded pattern is the Stein-Meredith "inverse effectiveness" principle. For FHRR binding, this maps directly: when per-modality recall is high (intact signal), binding produces no recall improvement over single-modality query. When per-modality recall is low (degraded signal), binding produces additive gain. This means the experimental gain from T-BIND-1 crossmodal_recall=0.944 may be disproportionately from cases where per-modality recall is low.

Prediction: sort T-BIND-1 test cases by per-modality (audio-only, video-only) recall. The cases where crossmodal_recall > per-modality recall should be concentrated at the low per-modality-recall end. If this fails (crossmodal gain is uniform across the recall distribution), the binding is not behaving inverse-effectiveness-like and the mechanism is different from STS integration.

### 1.2 Temporal binding window (TBW) and IPS/STG gating

2025 TMS study (biorXiv 2025.10.01.679698) provides causal evidence: early left IPS and right STG stimulation increases synchrony perception; later bilateral STG stimulation promotes segregation. Natural TBW:
- Simple AV stimuli: ~60-70 ms
- Natural speech: up to ~260 ms

For FHRR temporal binding, the PERMUTE^t operator discretizes time at step t. If the audio and video streams are misaligned by delta_t, the binding produces PERMUTE^(t+delta_t)(audio_FHRR) * PERMUTE^t(video_FHRR) = PERMUTE^t(PERMUTE^(delta_t)(audio_FHRR) * video_FHRR). The cross-modal query at time t will see a mismatch proportional to the phase introduced by PERMUTE^(delta_t). For FHRR this is a rotation in the complex plane by delta_t * 2*pi/N. If N=2048 and delta_t=1 time step = 33ms (30fps), the mismatch phase is 2*pi/2048 ~ 0.003 rad per step. At delta_t=8 steps (264ms, near natural speech TBW), the mismatch is 0.025 rad - still within noise tolerance. This predicts the FHRR temporal binding is tolerant to asynchrony up to roughly the natural speech TBW, which is biologically coherent.

Concrete test: measure crossmodal_recall@1 as a function of audiovisual offset (0, 33, 66, 132, 264ms). HARD-PASS: recall degrades < 10% up to 132ms offset. HARD-FAIL: > 20% degradation at 66ms.

### 1.3 Thalamic gating: pulvinar and superior colliculus

2025 papers (Wiley EJN 70230; Nature Comms 2025, s41467-025-64600-x) quantify:
- Medial pulvinar: early period dominantly sub-additive; late period shows multisensory integration
- Superior colliculus: nonlinear integration encodes audiovisual delay precisely; >5000 neurons in awake mice

The nonlinear encoding of AV delay in SC is a direct analog of the PERMUTE^delta_t mismatch described above. The biological system encodes AV delay as a nonlinear signal, which then feeds into multisensory cortex for integration. FHRR PERMUTE encoding encodes time-step offset as a rotation in complex space, which is linear. The biological nonlinearity may provide better robustness at larger offsets; FHRR's linear encoding may degrade faster at large offsets. This is a falsifiable difference.

### 1.4 McGurk effect and attentional gating

Alpha oscillations gate cross-modal conflict: when IPS/STG alpha power is elevated, conflicting modality information is suppressed (Scientific Reports 2019). The McGurk effect is attentional: under load, the effect weakens.

For adversarial T-BIND testing: present visual embedding from modality A (e.g., a dog barking) with audio embedding from modality B (e.g., a cat meowing). Query: does the bound composite retrieve the correct audio or does it retrieve the visual label? In FHRR, the binding PERMUTE^t(visual_FHRR) * audio_FHRR produces a composite that, when queried by audio_FHRR alone, returns the visual context. The adversarial test is whether a semantically incongruent visual reduces the recall of the correct audio object. If recall drops more than 20%, the system is more McGurk-like (visual dominates). If recall is unchanged, the binding correctly isolates modalities.

---

## Level 2: Materials science / oscillator mechanics

### 2.1 Kuramoto coupling as a model of FHRR phase synchronization

Kuramoto model: d(theta_i)/dt = omega_i + (K/N) * SUM_j sin(theta_j - theta_i). For N oscillators, synchronization occurs when K > K_c = 2/[pi*g(0)] where g(omega) is the natural frequency distribution.

FHRR complex multiplication corresponds to phase addition: z_1 * z_2 = exp(i*(phi_1 + phi_2)). When binding k modalities, the composite phase is phi_1 + phi_2 + ... + phi_k. If each modality's FHRR vector has phase variance sigma^2, the composite phase variance is k*sigma^2. Query cosine similarity: cos(phi_composite - phi_query) ~ 1 - k*sigma^2 / 2.

For k=2 (audio + video), sigma^2 ~ 1/N (each random FHRR vector has phase variance 1/N for N>>1). So composite variance = 2/N. Cosine degradation from single-modality: ~ 1/N. At N=2048, this is 0.0005 - negligible. At N=256, degradation is 0.004 - still negligible. This confirms binding 2 modalities does not materially degrade recall.

But for k=5 modalities (audio + video + depth + IMU + text) at N=2048: variance = 5/2048 ~ 0.002, cosine degradation ~ 0.001. Still tiny. The resonator capacity (k objects per scene) is the binding limit, not the modality count per item.

Kuramoto analogy: FHRR binding is equivalent to a zero-coupling-constant Kuramoto model (oscillators are independent). The "synchronization" happens not by coupling but by construction (binding). This means FHRR is not susceptible to the Kuramoto desynchronization transition - the modality phases are deterministically added, not stochastically coupled. Adversarial perturbation in FHRR = external noise injection, not natural-frequency drift.

### 2.2 Nonlinear frequency mixing and cross-modal FHRR

Nonlinear optics: sum-frequency generation (SFG) produces output at omega_1 + omega_2 from inputs at omega_1 and omega_2. FHRR binding z_1 * z_2 = exp(i*(phi_1 + phi_2)) is the direct algebraic analog of SFG. The "phase coherence length" in NLO corresponds to the FHRR vector dimension N: larger N = longer coherence = more precise phase discrimination = better recall.

Second harmonic generation (SHG): z^2 = exp(2*i*phi). In FHRR, this is binding a vector with itself. This gives the "self-similarity" operator. For cross-modal binding, this means: if audio_FHRR and video_FHRR are bound, and then queried by another binding of the same pair, the self-similarity is (audio_FHRR)^2 * (video_FHRR)^2 vs query = (audio_FHRR * video_FHRR). This does not produce a clean match. This predicts FHRR queries must use the EXACT binding used for insertion, not a self-convolution. This is a hard constraint on query construction.

---

## Level 3: LLM multimodal theory

### 3.1 LLM2CLIP and the modality gap problem

LLM2CLIP (AAAI 2026 Outstanding Paper Award; microsoft.github.io/LLM2CLIP) uses a large language model as a textual teacher to improve CLIP text representation quality. Key finding: the "modality gap" in CLIP (image and text embeddings occupy different parts of the joint space) is reducible by parameter sharing + intra-modality separation. SigLIP2 updated with LLM2CLIP in March 2025 shows improved short and long-text image retrieval.

For FHRR cross-modal binding: the modality gap is problematic. If CLIP image embeddings and CLIP text embeddings have different means and variances in 512-d space, a shared random projection to N=2048 FHRR will produce modality-specific clusters. Cross-modal binding of an image FHRR and a text FHRR will then have a systematic phase offset proportional to the modality gap. LLM2CLIP-style alignment (reducing the modality gap before projection) directly improves FHRR cross-modal binding quality. This is an actionable recommendation: use LLM2CLIP-aligned CLIP rather than vanilla CLIP for the FHRR projection step.

Quantitative prediction: FHRR crossmodal_recall@1 with LLM2CLIP-aligned embeddings vs vanilla CLIP: expect 5-15% recall improvement, concentrated in text-queried-image retrieval cases where the modality gap is largest.

### 3.2 Improving CLIP cross-modal alignment (ICLR 2025)

"Improving Cross-Modal Alignment in CLIP" (ICLR 2025, iclr.cc): proposes parameter sharing + explicit alignment loss to reduce modality gap while maintaining intra-modality separation. Directly applicable: use this aligned CLIP as the encoder for FHRR projection to reduce modality-gap-induced phase offset.

### 3.3 PaLM-E / GPT-4V / Gemini: what they do that FHRR does not

- PaLM-E, GPT-4V, Gemini: end-to-end learned cross-modal alignment; reasoning over bound representations via attention.
- FHRR substrate: algebraic binding; no learned alignment; no attention-based reasoning.

The gap: learned alignment in LLMs corrects for embedding quality issues automatically through training. FHRR relies on pre-aligned embeddings. The advantage: FHRR is O(N) at query time vs O(N^2) for attention; FHRR provides algebraic composition (AND, NOT, PERMUTE) that LLMs cannot do algebraically; FHRR Merkle audit is exact.

The actionable synthesis: use an LLM (or CLIP-style contrastive training) for the encoder step, then project to FHRR for the retrieval/composition layer. This is the NVSA pattern (Hersche et al. 2023) applied to production cross-modal retrieval.

---

## Level 4: Push paths - detailed drill

### 4.1 REAL-VIDEO-AUDIO (YouTube-style clips)

Engineering path:
1. Download 100 clips using yt-dlp (non-commercial test clips, Creative Commons).
2. Extract frames at 1fps with CLIP ViT-B/32 -> 512-d float32 per frame.
3. Extract Whisper base encoder states at 20ms hop -> mean-pool per second -> 512-d float32 per second.
4. Random complex projection: W ~ CN(0, 1/N) sized (512, N). Apply to both modalities (same W works only if CLIP + Whisper are in compatible spaces; independent W matrices per modality is safer).
5. Temporal binding: for clip of length T seconds, clip_FHRR = SUM_t(PERMUTE^t(visual_FHRR_t) * audio_FHRR_t) / T.
6. Insert into substrate codebook.
7. Query by (a) visual FHRR of a held-out frame, (b) audio FHRR of a held-out second, (c) cross-modal: visual * audio attribute.
8. Measure recall@1, @5, cross-modal precision@5.

Key open question: should visual and audio use the SAME projection matrix W, or separate W_v and W_a? Same W assumes pre-alignment (CLIP + Whisper are pre-aligned). Separate W_v, W_a makes each modality independently retrievable but cross-modal queries require knowing which W was used. Recommendation: use separate W_v, W_a, and construct cross-modal composite as clip_FHRR = W_v(visual) * W_a(audio); query by W_a(audio_query) to retrieve clip.

### 4.2 MIXED-RATE-30HZ-44.1KHZ-1KHZ

Three temporal rates: 30Hz video, 44.1kHz audio, 1kHz sensor (IMU/depth).

The PERMUTE^t operator uses integer step t. For 30Hz video, t is in video frames. For 44.1kHz audio, there are 44100/30 = 1470 audio samples per video frame. For 1kHz IMU, there are 1000/30 = 33 IMU samples per video frame.

Two strategies:
A. Common-clock: resample all to 30Hz (1 vector per frame for all modalities). Simple, lossless for video and IMU, lossy for audio (1470->1 audio sample per frame via mean-pool Whisper state).
B. Multi-resolution: audio uses t_audio = floor(t_sample * 30 / 44100), so each audio frame maps to a 30fps-equivalent index. PERMUTE^t_audio quantizes audio to video frame boundaries. This avoids resampling but introduces temporal quantization error of up to 1/30 sec = 33ms.

The Temporal Binding Window analysis (Section 1.2) shows 33ms offset corresponds to 1 time step at 30fps, which introduces phase mismatch of 2*pi/N. At N=2048, this is 0.003 rad, well within noise tolerance. Strategy B is therefore viable without recall degradation.

Engineering test (TBIND-MIXED-RATE): compare recall@1 for strategy A vs B on 25 real clips. If degradation < 5%, strategy B is preferred (no resampling overhead). If degradation > 20%, strategy A is required.

### 4.3 ADVERSARIAL-MCGURK

Setup: 25 real clips. For each clip, swap the visual stream with a semantically incongruent visual (different category, same temporal structure). E.g., audio of a speech segment paired with visual frames of a bird.

Three query types:
1. Audio-only query: recall of correct clip (audio content unchanged).
2. Visual-only query: recall of adversarial clip (video content changed).
3. Cross-modal bound query: does the adversarial visual contaminate the audio-retrievable composite?

Expected behavior (HARD-PASS): audio-only query unchanged; cross-modal query degraded by < 20% (binding with adversarial visual introduces noise proportional to the visual FHRR variance, which is 1/N per dimension).

Expected behavior (HARD-FAIL): cross-modal query degraded > 40% -> binding weight is too visual-heavy; binding formula needs modality-reliability weighting (IPS-like gating).

Modality-reliability weighting: weight_v = recall_v / (recall_v + recall_a); w_a = 1 - w_v. Composite: clip_FHRR = w_v * visual_FHRR * PERMUTE^t + w_a * audio_FHRR. If recall_v = 0 (fully adversarial visual), w_v -> 0 and composite reduces to audio-only FHRR. This is the FHRR analog of the inverse effectiveness / reliability-weighted Bayesian multisensory integration.

This is the "attentional selective" push path: modality reliability gating via scalar weights, computed from per-modality recall, applied before binding.

### 4.4 SYNESTHESIA analogy: learned arbitrary cross-modal associations

Synesthesia research: arbitrary learned associations between modalities are encoded in cross-modal binding regions (STS, parietal cortex). Synesthetes show stronger long-term memory for arbitrary pairings. For FHRR: arbitrary cross-modal associations are bindable with no constraint on semantic relatedness (audio of jazz can bind to visual of mountain). This is the production use case: cross-modal index where modality pairs are domain-defined, not perceptually natural.

Test: compare recall@1 for (a) semantically congruent AV pairs (speech + face video), (b) arbitrary AV pairs (speech + unrelated visual). Hypothesis: recall@1 is the same for both, since FHRR binding quality depends on vector quasi-orthogonality, not semantic relatedness. HARD-PASS: < 5% recall difference between congruent and arbitrary pairs. HARD-FAIL: > 15% difference -> the embedding model (CLIP/Whisper) has pre-aligned modalities such that incongruent pairs have lower cosine similarity in FHRR space, degrading recall.

### 4.5 PRODUCTION-100-SCENES

Scaling from 25 to 100 scenes. Resonator capacity: k objects per scene from codebook of M objects. At N=2048, k=2 objects, M=1000: k*log2(M) = 20, well below N/2 = 1024. Capacity is ample.

For clip binding (not resonator factorization): 100 distinct clips in codebook. Query precision depends on inter-clip quasi-orthogonality. Expected near-orthogonality: cosine similarity between random N-dimensional complex vectors ~ 1/sqrt(N). At N=2048, pairwise cosine ~ 0.022 per pair. With 100 clips, the interference term per query ~ 99 * 0.022 = 2.2. This is below the signal (self-cosine = 1.0) by a factor of 2.2, so interference dominates at 100 clips without cleanup.

This is the key scaling failure mode. Mitigation options:
1. Increase N to 4096: interference term drops by sqrt(2) to ~1.56. Still dominant.
2. Use Kronecker rotation cleanup (arXiv 2506.15793, O(N log N)): cheaply re-orthogonalize after insertion.
3. Use histogram recovery VSA (arXiv 2511.01838, Reed-Solomon + Hadamard): provably quasi-orthogonal codes at larger M.

Recommendation: test at N=4096 first (2x computational cost, -3dB interference). If not sufficient, implement linearithmic cleanup (arXiv 2506.15793).

Quantitative prediction (N=4096, 100 clips): interference term = 99 * (1/sqrt(4096)) = 99 * 0.0156 = 1.55. Signal = 1.0. Signal-to-interference ratio (SIR) = 0.65. This predicts recall@1 ~ 50-60% without cleanup, not 90%+. The 100-scene HARD-PASS target requires cleanup or higher N.

At N=16384, interference = 99/128 = 0.77. SIR = 1.30. Recall@1 should exceed 80%.

Cheapest test: TBIND-100-SCENE at N=4096 with and without linearithmic cleanup (Kronecker rotation, O(N log N)). This decides the practical path for production-scale.

---

## Level 5: Empirical tests - ranked priority

All tests CPU-local, zero cloud spend, 30 min - 4 hr runtime.

| Priority | Anchor name | N | Clips | Key metric | HARD-PASS | HARD-FAIL | Runtime |
|---|---|---|---|---|---|---|---|
| 1 | TBIND-REAL-25 | 2048 | 25 real AV | crossmodal_recall@1 | >= 0.80 | < 0.50 | 30 min |
| 2 | TBIND-ASYNCHRONY | 2048 | 25 real AV | recall vs offset (0-264ms) | < 10% drop at 132ms | > 20% drop at 66ms | 1 hr |
| 3 | TBIND-ADVERSARIAL-MCGURK | 2048 | 25 adversarial | recall of audio under swapped visual | < 20% drop | > 40% drop | 1 hr |
| 4 | TBIND-INVERSE-EFF | 2048 | 25 real AV, stratified by per-modal recall | crossmodal gain vs per-modal recall bucket | gain concentrated at low-recall end | flat gain across recall buckets | 1 hr |
| 5 | TBIND-MIXED-RATE | 2048 | 25 clips, two rate strategies | strategy A vs B recall difference | < 5% difference | > 20% difference | 1 hr |
| 6 | TBIND-100-SCENE | 4096 + cleanup | 100 real AV | crossmodal_recall@1 | >= 0.85 | < 0.65 | 2 hr |
| 7 | TBIND-LONG-DURATION | 2048 | 10 clips, 10-60 sec each | recall with temporal chunking | >= 0.75 | < 0.40 | 2 hr |
| 8 | TBIND-LLMC2LIP | 2048 | 25 clips, LLM2CLIP vs vanilla CLIP | recall improvement | 5-15% better | worse than vanilla CLIP | 4 hr |

---

## Cross-thread synthesis

### With PP-329 T-BIND-1 result

The 25-scene HARD_PASS at crossmodal_recall=0.944 used synthetic scenes. The 2x drill reveals the critical gap: synthetic scenes do not test (a) real encoder variance, (b) temporal asynchrony, (c) adversarial incongruence, or (d) scale beyond 25 clips. The TBIND-REAL-25 anchor is the first gating test before any production claim.

### With existing cross-modal research notes

Prior drill (research_drill_substrate_cross_modal_2x_2026-06-09.md) established the 10-anchor roadmap from VISION-CLIP-SUBSTRATE through CROSS-MODAL-SCALE. T-BIND-1 HARD_PASS on PP-329 means VISION-CLIP-SUBSTRATE-equivalent (recall at small scale) is now confirmed. The next gates are: real data, adversarial, scale. This drill provides the mechanistic justification for why scale fails (SIR argument at N=4096) and the mitigation (linearithmic cleanup).

### With linearithmic VSA cleanup (arXiv 2506.15793)

The Kronecker rotation cleanup paper (MLPR 2025, Liu et al.) provides O(N log N) cleanup with O(log N) codebook storage. This is immediately implementable in the substrate and would directly address the 100-scene SIR problem. Importantly, the FHRR substrate already uses complex multiplication (consistent with Kronecker rotation product structure). This is the highest-leverage algorithmic improvement for scale-up.

### With free-probability / Tracy-Widom adjacency

The field advisor identifies Tracy-Widom edge statistics (F2) and free cumulants (F4) as top-next-drill candidates. The SIR calculation above is a finite-N random matrix question: the interference term is the spectral edge of the Gram matrix of 100 random complex FHRR vectors. Tracy-Widom gives the precise edge fluctuation for the largest eigenvalue of this Gram matrix, which determines the worst-case interference. A follow-up drill connecting T-BIND scale failure to Tracy-Widom edge statistics would provide the exact N required for a given number of clips.

### With efficient VSA from histogram recovery (arXiv 2511.01838)

Reed-Solomon + Hadamard codes provide provably quasi-orthogonal vectors with formal noise recovery guarantees. The key advantage over random FHRR: mutual coherence is bounded by a code-theoretic constant rather than a 1/sqrt(N) probabilistic bound. For M=100 clips at N=2048, the RS+Hadamard code gives guaranteed quasi-orthogonality, not just expected quasi-orthogonality. This is relevant for TBIND-100-SCENE: using RS+Hadamard codebook vectors instead of random FHRR vectors may achieve HARD-PASS at N=2048 without increasing N.

---

## Substrate-product implications

1. **Single-codebook cross-modal at scale**: the SIR argument predicts the production bottleneck is codebook size (M), not binding algebra. The solution (linearithmic cleanup, RS+Hadamard) is implementable now, before any customer deployment.

2. **Adversarial robustness clause**: the RL-Bind paper (arXiv 2509.14383) shows standard multimodal encoders are highly fragile (up to 100% accuracy drop under epsilon=2/255 perturbation). FHRR's high-dimensionality provides inherent noise resistance. This is a concrete product differentiator: "adversarially robust cross-modal retrieval without adversarial training."

3. **Temporal asynchrony tolerance**: the TBW analysis predicts FHRR tolerates AV offsets up to ~130ms without cleanup. This means real-world video (where audio/video sync may drift) does not require tight synchronization before ingestion. Practical implication: ingest pipeline does not need frame-accurate AV alignment.

4. **Modality reliability weighting**: the inverse-effectiveness / IPS-like gating (weighted binding) is a simple scalar operation. It would make the substrate robust to one modality being unavailable or corrupted without architectural change. Product angle: "graceful degradation when one modality fails."

5. **LLM2CLIP encoder integration**: using LLM2CLIP-aligned CLIP vs vanilla CLIP is a drop-in encoder swap (same API, different weights). This 5-15% estimated recall improvement is low-risk, low-cost. Recommend swapping before any production demo.

6. **EU AI Act Article 12 cross-modal audit**: every cross-modal insert (AV clip) hashes into the same Merkle tree as text inserts. Multimodal provenance audit is structural, not bolted-on. Enforcement begins August 2026.

---

## Citations (verified, 24 total)

1. Stereoelectroencephalography STS sEEG study (PMC12528836, 2025). sEEG direct recording STS AV speech.
2. McGurk and MacDonald "Hearing lips and seeing voices" (Nature 1976). McGurk effect original.
3. Alpha oscillations IPS/STG attentional gating (Scientific Reports 2019, s41598-019-41636-w).
4. TMS IPS/STG TBW study (biorXiv 2025.10.01.679698). Causal evidence temporal binding.
5. Medial pulvinar frequency coding LFP (Wiley EJN 70230, 2025). Subadditive AV pulvinar.
6. Superior colliculus multisensory temporal specialization (Nature Communications 2025, s41467-025-64600-x). 5000+ neurons AV delay encoding.
7. Inverse effectiveness cellular mechanism (PMC5375642). Dopamine reinforcement cross-modal learning Drosophila.
8. Incorporating brain-inspired mechanisms multimodal AI (Science Advances 2025, sciadv.ady8751).
9. Inverted encoding superadditive multisensory (eLife 2024/PMC 2025, PMC12928699).
10. Kuramoto stability synchronization (arXiv 2411.17925, 2024). Stability analysis.
11. Higher-dimensional Kuramoto matrix-weighted couplings (arXiv 2603.08352, 2026).
12. LLM2CLIP AAAI 2026 Outstanding Paper (microsoft.github.io/LLM2CLIP). LLM as textual teacher for CLIP.
13. Improving Cross-Modal Alignment in CLIP (ICLR 2025, iclr.cc cc1de06a58ba1db43538a37e076e466d).
14. Mitigate the Gap CLIP alignment (arXiv 2406.17639, 2024).
15. Adversarial robustness unified multimodal encoders (arXiv 2505.11895, 2025).
16. RLBind adversarial-invariant cross-modal alignment (arXiv 2509.14383, 2025).
17. Robustness VLMs under noise (arXiv 2509.12492, 2025).
18. Linearithmic cleanup Kronecker rotation VSA (arXiv 2506.15793, MLPR 2025).
19. Efficient VSA from histogram recovery RS+Hadamard (arXiv 2511.01838, 2025).
20. Efficient modular composite HDC representations (arXiv 2511.09708, 2025).
21. Hyperdimensional intelligent sensing real-time audio edge (arXiv 2502.10718, IEEE Access 2025).
22. Geometric world models VSA (arXiv 2602.21467, 2026). Temporal binding PERMUTE structure.
23. Cross-layer VSA hardware (arXiv 2508.14245, 2025).
24. Frady et al. resonator networks (Neural Computation 2020). Factorization capacity formula.

---

## P summary (post-calibration)

| Claim | P_raw | P_deflated |
|---|---|---|
| TBIND-REAL-25 recall@1 >= 0.80 | 0.70 | 0.50 |
| TBIND-100-SCENE recall@1 >= 0.85 (N=4096+cleanup) | 0.60 | 0.40 |
| TBIND-ADVERSARIAL-MCGURK recall drop < 15% | 0.55 | 0.35 |
| TBIND-ASYNCHRONY < 10% degradation at 132ms offset | 0.75 | 0.55 |
| TBIND-MIXED-RATE strategy B viable (< 5% degradation) | 0.65 | 0.45 |
| LLM2CLIP swap gives 5-15% recall improvement | 0.60 | 0.40 |
| RS+Hadamard codebook replaces random FHRR at N=2048 for 100 clips | 0.55 | 0.35 |
| Inverse effectiveness pattern verified in T-BIND-1 case distribution | 0.65 | 0.45 |

---

## Next-drill candidate

**Tracy-Widom / free-cumulant drill on FHRR codebook Gram matrix spectral statistics**: the SIR scaling argument above is a random matrix problem. The exact N required for M clips at target recall can be derived from Tracy-Widom edge statistics for complex random matrices. This connects the field-advisor top-2 candidates (F2, F4) directly to the T-BIND production scaling question. A 1-day theory drill would give the closed-form N(M, recall_target) formula.
