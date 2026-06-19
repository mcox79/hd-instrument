# exp_dev hand-off -- research: multimodal substrate primitives (VSA non-linguistic modalities)

**Filed:** 2026-06-04 by research sub-agent.

**Trigger:** Research drill `notes/research_drill_multimodal_substrate_primitives_2x_2026-06-04.md` found that vision (K=196), audio (K=62), and motor (K=100) modalities all sit within the substrate's clean-retrieval envelope at N=4096. Concrete experiments are proposed. Cheap decisive test defined.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. Vision Hebbian write -- CIFAR-10 patch-level encode + classify

- **Anchor pointer:** Research note sub-question 1 + cheap decisive test section (vision patch encoding, K=196 at N=4096, hierarchical bundle then Hebbian class write)
- **Substrate-product reading:** This is the first non-linguistic modality smoke test. If vision encoding is within the clean-retrieval envelope (P_clean > 0.95 at K=196, N=4096) as derived algebraically, a Hebbian-write classifier on CIFAR-10 (or MNIST) should achieve >50% accuracy with no gradient. Validates that substrate's bipolar outer-product write generalises to images. Tier hint: LOCAL CPU (K-nearest-neighbor in VSA space; no training loop; < 60s wall).
- **Why now:** This is the cheapest possible non-linguistic product demo. If it passes, product narrative expands immediately. If hard-fail (accuracy < 20%), encoding distribution is degenerate and the SNR formula's iid assumption is violated -- important falsification.

### 2. Audio spectral chunk encode + classify (environmental sounds)

- **Anchor pointer:** Research note sub-question 1 audio row (K=62 frames, 1s window, SNR=8.13, P_clean=1.000) + sub-question 2 audio encoding schemes (MFCC + sign-quantize approach)
- **Substrate-product reading:** Audio is the most forgiving modality (K=62, SNR=8.13 >> K_crit). Single-step MFCC binarization + Hebbian write should yield clean recognition on a small audio classification dataset (ESC-10 or similar, 10 classes). Tier hint: LOCAL CPU or REMOTE CPU.
- **Why now:** Pairs with the vision anchor to demonstrate modality breadth in a single exp_dev cycle. If both pass, multi-modal product story is fully grounded at the cheap level.

### 3. Cross-modal text+image binding retrieval smoke

- **Anchor pointer:** Research note sub-question 4 (cross-modal K=3 modalities, SNR=36.9 at N=4096; cross-modal binding algebra: V = bind(V_text, key_text) + bind(V_img, key_img)); recommended N=8192 for product use.
- **Substrate-product reading:** Tests whether VSA cross-modal binding (3 modalities, K=3 bound terms) allows accurate retrieval of the image component given a text query. At K=3, SNR is enormous and retrieval should be near-perfect. The bottleneck is whether the random-projected text and image vectors are distinguishable in the same N-dimensional space. Tier hint: LOCAL CPU smoke first; escalate to REMOTE CPU if multi-scale sweep needed.
- **Why now:** Cross-modal binding is the highest-leverage product capability (enables text-to-image retrieval, audio-to-text, etc.) and the algebra predicts it is trivially within capacity. A clean pass here would be the most compelling product demonstration possible.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_multimodal_substrate_primitives_2x_2026-06-04.md`
- Prior position-binding language note: `d:/AI/hd-instrument/notes/research_drill_position_binding_translation_language_2x_2026-06-04.md`
- SNR formula derivation: see language note lines 28-60 (carries over unchanged to all modalities)
- Capacity table (all modalities, N=4096): research note Sub-Question 1 table

---

## Contract

exp_dev owns: anchor naming, sweep grid, threshold bands (HARD-PASS / MID / HARD-FAIL), queue routing, ETA, smoke vs FULL profile, pre-registration format.

Research provides: algebraic predictions (SNR and P_clean values), encoding scheme options per modality, and HARD-FAIL conditions (encoding degenerate test: pairwise cosine > 0.1 -> encoding not near-orthogonal).

## Autonomy declaration

exp_dev should not wait for orchestrator confirmation to begin smoke design on these anchors if queue depth < 1 and pause flag is absent. The research justification is complete.
