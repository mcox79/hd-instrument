# Brain Reading Architecture Emulation — v2 Concept-Encoder Prescription

**Author:** Research (Director)
**Date:** 2026-07-02 (late evening)
**Trigger:** USER directive — "remember to do drills on how the brain handles this too - we may find we need to emulate."
**Task the brain solves that we fail at:** Given a text query (single word / short phrase), retrieve the correct concept from N candidates on held-out synonym retrieval. Our sparse-competitive-Hebbian concept encoder loses to a trivial char-trigram bag.
**Framing:** Content-level HF (High-Fidelity) research drill. Prescribes concrete substrate architecture (not descriptive neuroscience).

---

## 1. Prior-work check via substrate-KB

Ran four `substrate_query.sh` queries (v2 schema, chunk-content, tau=0.15, k=5).

| Query | Top prior atom | Cosine | Verdict |
|---|---|---|---|
| "VWFA visual word form area Dehaene letterbox reading" | `visual_area` (WordNet) | 0.31 | No prior design work; lexicon only |
| "hub and spoke anterior temporal lobe semantic Patterson Rogers" | `BIO/anterior_temporal_lobe` (T1 primitive) | 0.41 | ATL exists as science-atom primitive; NO substrate emulation attempt |
| "morphological decomposition angular gyrus reading network" | `chemical_decomposition_reaction` (WordNet) | 0.32 | No prior work; misfires to chemistry |
| "cortical layer L4 dense L2/3 sparse multi mechanism" | `defense_mechanism` (WordNet) | 0.37 | No prior layer-specialization design |

**Prior arc work on this concept: NONE (novel synthesis).**
Lit-scan calibration penalty applies — P estimates capped at 0.50 for novel-synthesis addition.

---

## 2. What the brain's reading network actually computes

### 2.1 VWFA (Visual Word Form Area, left mid-fusiform)

**Anatomy:** Left mid-fusiform gyrus (~ Talairach -45, -57, -12). Category-selective for orthographic strings across cultures/scripts (Dehaene & Cohen 2011 *TICS* "Reading in the Brain"; McCandliss/Cohen/Dehaene 2003 *TICS* "The visual word form area").

**Computation — Dehaene 2005 letterbox model (hierarchical local combination detectors, LCD):**
- L1: retinotopic pixel bank (V1/V2)
- L2: **case-invariant letter detectors** (100–300 units per letter identity across positions)
- L3: **open-bigram / bigram detectors** (order-preserving pairs: `ab`, `ac`, `ad`, ... not necessarily adjacent)
- L4: **quadrigram / morpheme-scale detectors** (longer sub-word units, ~4 chars, language-specific)
- L5: **whole-word units** (only for high-frequency words; rare/novel words don't have L5)

**Key computational properties:**
1. **Multi-scale.** Simultaneously encodes at char, bigram, trigram, quadrigram, whole-word grain.
2. **Position-relative, NOT position-absolute.** Encoded position is relative to word onset/offset, not retinal coordinates. Robust to string shifts.
3. **Statistics are BAKED IN**, not learned per query. ~7 years of reading exposure fixes the feature bank; it's a PRE-COMPUTED read-only encoder at retrieval time.
4. **Order-approximation, not strict adjacency.** Open-bigrams (e.g., `ca` in `cart` AND `cast`) support morphological/analogical retrieval when strict adjacency fails.

**Prescription for substrate:** A **read-only multi-scale character-with-position encoder** that produces a single query HD by HRR-binding (char, position) pairs and bundling across characters and scales. **This is what the substrate is missing.** The char-trigram bag that beat us captures ONE scale of ONE grain; VWFA does the full multi-scale bank with position encoding.

### 2.2 Morphological decomposition (angular gyrus + posterior STS / left fusiform anterior to VWFA)

**Anatomy:** Angular gyrus, posterior superior temporal sulcus, mid-fusiform anterior to VWFA (Devlin et al. 2004; Bozic et al. 2010).

**Computation:**
- Rastle-Davis-New 2004 *Lang Cog Proc*: morphological priming for pseudo-affixed words ("corner" primes "corn" as if `corn-er` decomposed). Decomposition is **obligatory, fast (~200 ms), and morpheme-based**, not semantically pre-filtered.
- Split: `unhappiness` → `un` (prefix) + `happy` (root) + `ness` (suffix); parallel activation of all three.
- Role encoding: `root` vs `prefix` vs `suffix` is a **structural role** bound to the morph.

**Key computational property:** Decomposition happens BEFORE full-word lookup, in PARALLEL with VWFA whole-word activation. Both streams contribute to the composite query representation.

**Prescription for substrate:** A **role-bound morpheme encoder** — decompose word to `[(morph, role)]` list, encode each morph as HD, bind with role HD via HRR, bundle. Handles cases where surface char-trigram misses (e.g., `unhappiness` → `happy` root activates via morph stream even if surface trigrams don't match `happy`).

### 2.3 Semantic hub-and-spoke (bilateral anterior temporal lobe)

**Anatomy:** Bilateral ATL with mild left dominance for language (Patterson/Nestor/Rogers 2007 *Nat Rev Neuro*; Ralph/Jefferies/Patterson/Rogers 2017 *Nat Rev Neuro*).

**Computation — hub-and-spoke:**
- **Amodal semantic hub** in ATL binds modality-specific spokes: visual, auditory, motor, olfactory, orthographic, phonological.
- Spokes carry MODALITY-SPECIFIC representations; hub is MODALITY-INDEPENDENT and encodes **abstract identity + associative structure**.
- **Semantic dementia (SD)** = focal ATL atrophy → progressive loss of specific semantic distinctions ("this is an animal, but I forget which one") while phonological + orthographic + syntactic capacities remain intact. **Behavioral proof that the ATL hub is what carries fine-grained semantic identity.**
- Mechanism: **convergence-zone binding** (Damasio 1989 revised by Meyer/Damasio 2009). Sparse population code in ATL binds co-occurring spoke activations into a unified representation.

**Key computational property:** Semantic identity is **DISTINCT from surface identity.** Two words with identical surface (heteronyms — e.g., "bass" the fish vs. "bass" the instrument) route to different ATL patterns via context; two words with disparate surface (synonyms — "entombment" vs. "burial") route to overlapping ATL patterns via shared semantic-associative structure.

**Prescription for substrate:** The current sparse-competitive-Hebbian concept encoder IS the ATL-analog. Its function is correct in principle. Its failure on held-out synonym is a **spoke-integration** failure, not a hub-competency failure — the hub has no useful surface-orthographic spoke to bind, so query representations lack surface-similarity gradients that would activate synonym neighborhoods.

### 2.4 Multi-stream parallel-independent LATE-COMBINE

**Evidence (MEG / ECoG timing studies — Marinkovic et al. 2003; Solomyak & Marantz 2010):**
- **~100–150 ms post-stimulus:** VWFA orthographic activation (letters, bigrams).
- **~150–250 ms:** Morphological decomposition (angular gyrus, mid-fusiform).
- **~200–350 ms:** ATL semantic hub retrieval.
- **~300–500 ms (N400 window):** LATE integration across all streams.
- **The streams DO NOT gate each other**; they run in parallel and combine at the N400 window.

**N400 amplitude** reflects the **DIFFICULTY of late integration**, not any single stream — supporting evidence that lexical retrieval is fundamentally a **parallel-streams-late-combine** architecture, not a sequential-cascade architecture.

**Prescription for substrate:** Streams should be **INDEPENDENT** at encoding, **COMBINED** at retrieval via weighted sum. **NOT sequential** (don't run morph → VWFA → semantic). Weights (α, β, γ) fit by held-out validation.

### 2.5 Held-out synonym retrieval SPECIFICALLY

**Query:** "entombment" → retrieve "burial" from N candidates.

**How the brain does it (parallel streams):**
1. **VWFA stream:** activates orthographic pattern for "entombment"; open-bigrams `en`, `nt`, `to`, `om`, `mb`, `me`, `en`, `nt` weakly overlap with `burial` (basically none — surface OVERLAP with target synonym is TINY).
2. **Morphological stream:** decomposes to `en-tomb-ment`; root morpheme `tomb` activates.
3. **Phonological stream (superior temporal):** `/ɛn.ˈtuːm.mənt/` — activates rhyming/similar-sounding words (not synonyms).
4. **ATL semantic-hub stream:** "entombment" full-word (+ `tomb` root spike from morph stream) activates the **semantic-neighborhood pattern** encoding death-ritual-container-earth. This pattern OVERLAPS with the pattern for "burial" (both encode the death-ritual-container-earth structure).
5. **Late combine (N400 window):** candidate scores summed; "burial" wins because ATL semantic-neighborhood pathway CROSSES the surface gap.

**Key insight for our failure:** The brain's semantic-hub stream is doing the heavy lift on SYNONYMY specifically — because surface overlap between synonyms is near-zero. But the hub is FED by decomposed morphological + orthographic spokes; without a decent morphology + orthography spoke feed, the hub has nothing to associate against.

**Our current failure mode:** The sparse-competitive-Hebbian encoder has NO orthographic spoke feeding it. It receives whatever the current encoder passes in, which appears to have lost the surface signal (evidence: trivial char-trigram bag beats us on the same task — that signal exists and is discriminative, but our current architecture throws it away or fails to weight it).

### 2.6 Cortical layer specialization (Douglas-Martin canonical microcircuit)

**Anatomy (universal across neocortex):**
- **L1:** sparse tangential axons, top-down feedback landing zone.
- **L2/3:** superficial pyramidal + fast-spiking PV interneurons. **Sparse, competitive, associative.** ← Our current sparse-competitive-Hebbian encoder.
- **L4:** dense granular layer, receives thalamic input. **Dense, feature-rich, high-dimensional.** ← **WE ARE MISSING THIS.**
- **L5:** deep pyramidal, output/motor projection. ← Our HRR-bind output interface (partially present).
- **L6:** corticothalamic, top-down feedback + prediction. ← Absent from our substrate.

**Key computational asymmetry:** Brain has **DENSE (L4) feeding SPARSE (L2/3)**. Our substrate has ONLY sparse. The dense-feeding-sparse pipeline is what makes L2/3 discriminative — L4 does the surface feature extraction, L2/3 does the competitive concept binding. Without L4, L2/3 receives impoverished input.

**Prescription for substrate:** Add an **L4-analog dense feature layer** — VWFA-analog + morphological-analog as the DENSE FEATURE BANKS — feeding into the sparse-competitive-Hebbian L2/3-analog.

---

## 3. Concrete substrate emulation architecture — Concept Encoder v2

### 3.1 Current failing architecture

```
query_text
  → [sparse_competitive_hebbian] (L2/3-analog only, no L4 feed)
    → concept_HD
      → retrieve
```

Result: LOSES to char-trigram bag on held-out synonym retrieval.

### 3.2 v2 brain-emulating architecture

```
query_text
  │
  ├─── VWFA-analog (L4-dense, orthographic spoke)
  │     • Multi-scale bank: char, bigram, trigram, quadrigram
  │     • HRR bind: (char_HD ⊗ position_HD) per scale
  │     • Bundle across positions and scales
  │     → v_ortho (HD)
  │
  ├─── Morphological-analog (angular-gyrus / L4-dense, morph spoke)
  │     • Decompose: [(morph, role)] via longest-common-substring against morpheme dict
  │       OR unsupervised morfessor-style split
  │     • HRR bind: (morph_HD ⊗ role_HD) where role ∈ {root, prefix, suffix}
  │     • Bundle
  │     → v_morph (HD)
  │
  ├─── Semantic-hub-analog (ATL / L2/3-sparse — EXISTING)
  │     • Current sparse-competitive-Hebbian concept encoder
  │     → v_sem (HD)
  │
  └─── LATE COMBINE (N400-analog integration)
        v_query = α · v_ortho + β · v_morph + γ · v_sem
        (α, β, γ fit by held-out validation)
        → retrieve top-1 concept
```

### 3.3 Compose-with-existing — how the brain-analog additions PLUG INTO current substrate

**Backward compatibility:** With `α=0, β=0, γ=1`, v2 REDUCES to current architecture. No breaking change to existing infrastructure.

**Decoupling:** Streams are independent — VWFA-analog can be built and tested before morphological-analog exists. Each spoke can be validated as a standalone concept encoder against the same held-out synonym task; standalone accuracy gives a per-spoke discriminative lower bound.

**No re-training required for the ATL-analog** (the sparse-competitive-Hebbian encoder) — it stays as-is. New spokes are ADDED, not substituting.

**Weight fitting is CHEAP:** α, β, γ are three scalars fit via grid-search or simple gradient descent on held-out validation accuracy. Not a full model retrain.

### 3.4 New HDlab modules required

| Module | Function | LOC est. | Priority |
|---|---|---|---|
| `hdlab/vwfa.py` | Multi-scale (char, bigram, trigram, quadrigram) position-bound encoder. `encode_multiscale_ortho(text: str) → HD` | ~150 | **P1 — HIGHEST** |
| `hdlab/late_combine.py` | Weighted-sum stream combiner. `combine(streams: dict[str, HD], weights: dict[str, float]) → HD`; `fit_weights_on_heldout(streams, targets, candidates) → weights` | ~80 | **P1 — ENABLING** |
| `hdlab/morph_decomp.py` | Role-bound morphological decomposer. `decompose(word) → [(morph, role)]`; `encode_morph(word) → HD` | ~200 | **P2** |
| `hdlab/concept_encoder_v2.py` | Assembly: dispatches to vwfa + morph_decomp + existing sparse-CH; late-combines. `encode(text) → HD` | ~100 | **P2 (post-VWFA)** |

Total new code: ~530 LOC across 4 modules. Existing sparse-competitive-Hebbian encoder UNTOUCHED (only imported).

---

## 4. Build order and priority

### P1 — Build FIRST (highest lift for held-out synonym task):

1. **`hdlab/vwfa.py` (VWFA-analog multi-scale char+position encoder)** — THIS IS THE SINGLE MOST LOAD-BEARING ADDITION.
   - Rationale: char-trigram bag beat us on the same task. VWFA-analog SUBSUMES char-trigram bag as ONE special case (trigram-scale, no position encoding) and ADDS multi-scale + position binding. Strong prior that this recovers OR exceeds trigram-bag performance while remaining composable.
2. **`hdlab/late_combine.py` (LATE COMBINE weighted-sum harness)** — enabling.
   - Rationale: even with VWFA-analog built, without a late-combine we can't compose spokes. Cheap to build; unblocks all downstream composition.

### P1 EXPERIMENT — after building both:

3. **Cell:** `encoder_v2_vwfa_plus_sparseCH_late_combine_2026-07-XX` — compose (α · VWFA-analog) + (γ · current sparse-CH), fit α, γ on held-out validation split, evaluate on same failed synonym-retrieval task.
   - Discriminator: top-1 accuracy on held-out synonym retrieval.
   - PASS band: top-1 ≥ char-trigram-bag baseline (specifically match or beat it — beating is P-heavy per below).
   - Reference: match current sparse-CH failure as anti-baseline (should exceed).

### P2 — Only if P1 experiment falls short:

4. **`hdlab/morph_decomp.py`** — adds morphological role-bound stream. Marginal lift on cases where surface overlap is near-zero (`unhappiness` → `happy`).
5. **`hdlab/concept_encoder_v2.py`** — full 3-spoke assembly with late-combine.
6. **Cell:** `encoder_v2_full_3spoke_2026-07-XX` — full v2 (VWFA + morph + sparse-CH + late-combine).

### P3 — Deferred:

7. **L6 top-down feedback:** cortical L6 corticothalamic feedback would gate L4 features via prediction error. Substantial architectural addition. Defer until P1/P2 measured.
8. **L4 dense feature layer for the sparse-CH itself:** upgrading the current L2/3-analog to receive a dense L4 feed (rather than raw text) would require re-training. High cost; deferred.
9. **Phonological stream (superior temporal analog):** low predicted lift for synonym retrieval per the entombment→burial worked example above. Deferred.

---

## 5. P estimates (calibration-penalty-applied)

**Applied discipline:** Lit-scan calibration penalty (deflate 0.15–0.25 for novel-synthesis, cap at 0.50).

| Addition | Task | Raw P | Deflated P | Notes |
|---|---|---|---|---|
| VWFA-analog alone | Beats current sparse-CH on held-out synonym | 0.75 | **0.55** | Direct extension of the mechanism that already beat us (trigram bag) with position + multi-scale. High prior. |
| VWFA-analog alone | Beats char-trigram bag on held-out synonym | 0.50 | **0.30** | Novel synthesis; position encoding may help OR may add noise. Trigram bag is a competitive baseline. Cap-adjusted. |
| VWFA + late-combine + current sparse-CH | Beats char-trigram bag on held-out synonym | 0.60 | **0.45** | Late-combine adds semantic-hub spoke on top of orthographic spoke. Novel-synthesis cap. |
| Full v2 (VWFA + morph + sparse-CH + late-combine) | Beats char-trigram bag on held-out synonym | 0.60 | **0.50** | Novel-synthesis cap binds. Morph adds marginal lift on prefixed/suffixed queries only. |
| Full v2 | MATCHES char-trigram bag on held-out synonym | 0.80 | **0.65** | Matching a baseline is easier than beating; higher raw prior; still calibration-penalized. |
| Full v2 | Beats current sparse-CH on held-out synonym | 0.85 | **0.70** | Current sparse-CH is our failure baseline; strong prior we improve on it. |

**Interpretation:**
- P(v2 rescues from current failure) ≈ **0.70** — reasonable bet.
- P(v2 beats the trigram bag baseline) ≈ **0.45–0.50** — coin-flip at novel-synthesis cap; the honest answer.
- The primary risk is that trigram bag is HARDER to beat than to match, because it already captures the discriminative surface signal densely; VWFA-analog's marginal advantage over trigram bag depends on whether position encoding + multi-scale bundling ADD independent discriminative signal beyond bag-of-trigrams, or merely redistribute the same signal.

---

## 6. What we still DON'T know (research questions surviving the drill)

1. **Are open-bigrams strictly better than adjacent-bigrams for HD encoding?** Reading-neuroscience evidence for open-bigrams is behavioral (priming); the substrate-computational case for open vs. adjacent bigrams in HD binding is untested. If HRR position-binding is used with adjacent bigrams, we get most of the position sensitivity. Open-bigrams may or may not add.
2. **Optimal number of scales in the multi-scale bank?** Brain does char, bigram, trigram, quadrigram, whole-word. Substrate may saturate earlier (e.g., trigram + whole-word may be sufficient). Empirical.
3. **Best morphological decomposer for held-out generalization?** Options: (a) hand-curated affix list, (b) MorfessorBaseline / unsupervised MDL, (c) BPE from a large text corpus. Each has different generalization properties. Empirical.
4. **Does the current sparse-competitive-Hebbian actually behave like an ATL-analog under load?** Semantic dementia would predict specific-distinction loss under lesion; our encoder has never been probed with SD-like ablation. Post-P1 research probe.
5. **Do we need L6 top-down feedback for CONTEXT-DEPENDENT retrieval?** For pure synonym retrieval (context-free), probably not. For agentic use (M4/M5), likely yes. Deferred.

---

## 7. Top-line prescription

**Single most load-bearing addition:** **`hdlab/vwfa.py` — multi-scale char-with-position orthographic encoder.**

**Why:** The mechanism that beat us (char-trigram bag) is a degenerate 1-scale, no-position case of the VWFA-analog. Building the VWFA-analog gives us that mechanism AS A SPECIAL CASE and adds proper composition into the substrate as a spoke that late-combines with the existing sparse-competitive-Hebbian. No breaking change, backward compatible, cheap (~150 LOC).

**P(v2 rescues from current failure):** 0.70.
**P(v2 beats trigram-bag baseline):** 0.45–0.50 (novel-synthesis cap binds).
**P(v2 matches trigram-bag baseline):** 0.65.

**Build order:**
1. `hdlab/vwfa.py` + `hdlab/late_combine.py` (P1, cheap).
2. Compose experiment: `α · VWFA + γ · sparse-CH` on failed held-out synonym task.
3. If insufficient, add `hdlab/morph_decomp.py` and 3-spoke assembly.
4. Deferred: L6 top-down feedback (M4/M5 concern), L4 upgrade of sparse-CH (retraining cost too high).

**Governance:** each module authored as a standalone HDlab primitive with self-test; each cell pre-registered with envelope-fail-bands and CARDINALITY_OK before dispatch. Cell v2 dispatch should follow SMOKE-on-local-CPU discipline (local_cpu smoke first; only promote to remote GPU after smoke passes discriminator).

---

*End of design note. ~350 lines. Ready for cell-author hand-off.*
