# hd-instrument substrate — capability map v1

Drafted 2026-05-19 21:00. Product-framed (not paper-framed). Goal: map every
capability the substrate has, lacks, might have, or would be game-changing if
we had it.

**Each capability links to dashboard-tab experiments with verdict state:**
- ✅ **Validated** — `positive` verdict, multi-seed where applicable
- 🟢 **Validated, want stronger** — `positive` but only single-seed or single-K, more validation desired
- 🟡 **Inconclusive** — `inconclusive` in dashboard, follow-up queued or needed
- 🔬 **Research only** — synthesis exists, no experiment yet
- ⚪ **Not yet tested** — capability proposed but no experiment + no research
- ❌ **Closed** — `negative` or `retracted` verdict

Cross-reference experiment names against the dashboard's `Tests` tab.

---

## 1. CAN — capabilities with empirical evidence

### Memory primitives (the substrate's core)

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **Auditable decomposition** — given any bundle, recover the constituent (byte, position) atoms | ✅ Validated | `decompose_K_cliff`, `decompose_K_cliff_extended` (both positive, cross-validated independently) | "Look inside any memory and read off what's stored." Unique vs transformers (KV cache is not decomposable). |
| **Edit individual bindings** — swap one (byte, position) for another by residual + rebind | 🟢 Validated, want stronger | `memory_editing`, `memory_recomposition` (positive but no multi-seed, no query-integration test) | Surgical correction: "fix this stored fact without retraining." |
| **Recompose novel bundles** — construct new memory bundles from extracted atoms | 🟢 Validated, want stronger | `memory_recomposition`, `interpretability_demo` (demo-only, not stress-tested) | Build new memories programmatically. |
| **CPU-only retrieval** — sub-100ms at K=4 on consumer hardware | 🟡 Inconclusive | `cpu_platform_timing` positive, `cpu_platform_timing_redo` **timed out** at 3600s (likely hung). Need a clean re-run. | Ship on edge / on-device. No GPU dependency at inference. |
| **Pool retrieval (factored + classical)** — pool of past contexts with weighted-vote readout | ✅ Validated | `phase_b2_pool_size_sweep`, `phase_b2_pool_size_annealed`, full Phase B suite | "Show me predictions backed by specific past examples" — provenance built-in. |
| **Resonator decomposition with ACF rescue** — recover atoms past capacity cliff (K/N=1.5 at 97%) | ✅ Validated, one open dip | `acf_K_dependent_retry`, `acf_resonator_redo`, `acf_sparsity_sweep_redo` (all positive). `acf_K_dependent_extended` revealed K=2944 dip (50% vs 75% neighbors); follow-up `acf_K2944_100trials` queued. | Can store more concepts than naive capacity bound. |

### Concept-level structure

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **R10 concept fusion at K≥8** — gap **+0.628 bpc at K=512 best-config**, monotone in K | ✅ Validated (strong) | `r10_best_config_multiseed` K=128 (+0.412)/K=256 (+0.543), `r10_best_config_K512` (+0.628), `r10_best_config_K64_verify` (+0.321 3-seed), `r10_ksweep_multiseed` (default-config baseline). All positive. | Substrate gets dramatically better as context window grows — opposite of transformer KV-cache scaling cost. |
| **PPMI bigram concept extraction** | 🟢 Validated, want stronger | `m2_ppmi`, `m2_concept_extraction` (older runs, mostly used as infrastructure inside R3/R10) | "Discover semantic units from data without supervision." |
| **R3-Laplace concept-conditioned readout bias** | 🟡 Inconclusive (mechanism unclear) | `r3_alone_laplace` positive (+0.032, 3 seeds, sd 0.005); `r3_unigram_diagnostic` inconclusive (GAMMA mis-calibrated); `r3_sparse_unigram_diagnostic` **queued — settles it**. Per research: most likely class-prior gated by sparsity, not substrate-unique. | If sparse-unigram matches R3: reframe as methodology. If R3 has residual: keep as capability. |

### Continual learning

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **Random replay BWT recovery: +0.66 to +0.73 at K=4** | ✅ Validated (3-seed) | `r7_concept_replay`, `replay_mechanism_sweep`, `r7_multiseed` (all positive) | Add new training data without catastrophic forgetting. Production-relevant. |
| **Pre-shift neutral replay** — replay during Phase A at 0.9 fraction has zero measurable cost | ✅ Validated | `replay_preshift_K4` (negative for Stein-prediction, but the substrate-capability finding is that replay is COST-FREE — that's a positive for us) | Replay is a "free" mechanism — no Phase A degradation budget to spend. |
| **Hebbian-only training (no backprop)** | ✅ Validated | All 86 experiments use delta rule on W. No autograd anywhere in the substrate. | Compatible with neuromorphic / specialized hardware. No autograd graph. |

### Robustness / scaling

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **Lippl-Stachenfeld redundancy theorem fails at K≥8** — substrate scales monotone where theory said it shouldn't | ✅ Validated | `r10_ksweep_multiseed` (default config K=16→256 monotone), `r10_best_config_K16_K32_K64` through `r10_best_config_K512` (best config K=8→512 monotone). 8 separate experiments, all positive. | Empirically falsifies a published limit. Defensible capability claim. |
| **M1 bundle-SNR mechanism confirmed** — doubling N shrinks gap 15% at K=128 | 🟢 Validated, want stronger | `r10_best_config_N8192_K128` positive. `r10_best_config_N8192_K256` **currently running** (will confirm at higher K). `r10_N8192` (default-config N-scaling, earlier positive). | We understand WHY it works → can predict / engineer further wins. |
| **K-cliff at K/N≈0.56** — sharp, cross-validated 2× independently | ✅ Validated | `decompose_K_cliff` + `decompose_K_cliff_extended` (positive, identical cliff). `decompose_K_cliff_dense8` queued for finer mapping. | Hard operating boundary; product can be sized confidently. |

---

## 2. CANNOT — empirically closed limits

### Compound mechanisms don't stack
- ❌ **R3 × R10 × random-replay**: closed. `triple_compound` + `triple_compound_v2` + `r10_r3_combined` all negative. Mechanism: shared evidence base (4 arguments converging). Research: `wave14b_compound_falsification_research.md`.
- ❌ **R3 same-source + replay**: `r3_disjoint_concepts` showed zero compound at K=4 (delta −0.001).
- ❌ **R3-disjoint compound at K≥16**: `r3_disjoint_K16` + `r3_disjoint_K32` both negative. Mechanism: concept-coverage saturation collapse. Research: `wave14c_r3_disjoint_K_flatness_research.md`. **`r3_disjoint_K64` queued** to confirm K-flatness extends.

### Specific mechanisms that don't work
- ❌ **MIR-style priority replay**: `mir_canonical` + `mir_replay` + `mir_rescues` all negative. Rank-equivalence math closes 3 rescue variants. Research: `wave14b_mir_failure_diagnosis.md`.
- ❌ **Iterative Hopfield as label readout**: `r1_modern_hopfield` negative. Protocol mismatch (Ramsauer iterates to nearest pattern, not label).
- ❌ **R10 best-config at K<8**: `r10_best_config_K2_K4_K8` negative. Best is WORSE than default at K=2 (−0.135) and K=4 (−0.174). 🟡 **Research agent in flight** on rescue; could move to 🔬 if a K-adaptive lambda recovers low K. `r10_best_config_K8_verify` currently running multi-seed to pin down the boundary precisely.
- ❌ **C3 factored compositional retrieval beats C1 classical**: `c3_factored` + 3 `c3_minimal*` runs — original +0.098 was a lambda artifact, true effect ~0.
- ❌ **Basis modifications**: `basis_modification` (exit 1) + `basis_modification_v2` + `basis_modification_indep` — no meaningful beat. Closed.

### Information-theoretic ceilings
- ❌ **Beat tiny-transformer pre-shift bpc (2.39) at K=4**: closed by information theory, not implementation. Transformer uses K=32 (different regime).
- ❌ **Pre-shift bpc as a "win" metric on this corpus**: wrong goal. Research: `wave14b_preshift_bpc_research.md`. Substrate is hygiene-pass at pre-shift; unique-enabling stories live in BWT / decomposition / K-scaling.

---

## 3. UNSURE — known unknowns (might be possible)

### Architectural extensions we haven't tested

| Direction | What it might give | Test path | Estimate |
|---|---|---|---|
| **Wave 9 MPS (Matrix Product States)** — u-MPS + DMRG | Compositional advantage over BSC binding | Literature-rec test untested | New build |
| **Wave 8 Clifford algebras** — grade-aware readout | Better concept structure than bipolar | Untested | New build |
| **Wave 10A RG-flow** — Krotov-WTA + linear Layer 1 | Lit-rec fix; might give a better basis | Untested | New build |
| **Wave 4.5 gradient W** — preconditioned delta rule | Faster/better convergence than plain delta | Untested | ~50 LOC |
| **Schlag-Irie slow projection** | Pre-shift mover (but pre-shift is wrong goal) | ~150 LOC, 1h GPU | Probably skip per CANNOT |
| **Learned codebook atoms** (SVD/PCA of bigram PPMI) | Better atoms than random bipolar | Estimated +0.02–0.08 at K=4 | ~15 min CPU |
| **Bricken SDM substrate** (Top-K + L2-norm) | Claimed pre-shift parity + native CL | Port + run | ~1 GPU hour |
| **Sparse block codes (Hersche 2024)** | log(N/B)·B capacity vs dense BSC | On the list, not built | Medium build |
| **Hierarchical context pool** (recent K bigrams + episodic anchors) | Speculative +0.05–0.15 | Untested | Medium build |

### Capability questions we haven't asked

| Question | Why it matters for a product | Test |
|---|---|---|
| **Can the substrate autoregressively GENERATE?** Not just predict next byte — generate sequences | If yes, substrate becomes a text generator with auditable memory. If no, it's a retrieval engine. | Sample-feedback-repeat loop; never run |
| **Multi-task transfer (corpus A → corpus C, not just shuffled A)** | Whether continual learning generalizes beyond same-distribution shifts | Test on genuinely different domain |
| **Compositional generalization** — novel combinations of learned concepts | Whether substrate has structural generalization vs just memorization | Hold-out compositional eval |
| **In-context learning** — adapt to examples at retrieval time without weight updates | Differentiator vs transformers (substrate's pool retrieval might natively do this) | Add examples to pool at query, measure adaptation |
| **Few-shot learning** | Tied to in-context | Pool-as-context-window eval |
| **Multi-step reasoning chains** | Whether substrate can chain inferences | No current mechanism; would need episodic-replay + chained retrieval |
| **Self-supervised concept discovery (no PPMI prior)** | PPMI is hand-crafted; can substrate learn its own concepts? | New mechanism needed |
| **Hierarchical concepts** (concepts-of-concepts) | Deep semantic structure | Could R3 recurse on its own pool? |
| **Sleep-style memory consolidation** | Offline strengthening of important memories | Replay-during-quiescence experiment |
| **Principled forgetting** — forget specific items on demand (e.g., GDPR-erase) | Editing yes, but full forgetting? | Untested |
| **Calibration / uncertainty** — does the substrate know when it doesn't know? | Critical for any product that takes actions | Softmax temp ≠ Bayesian uncertainty |
| **Online adaptation during inference** — every query updates W | Real-time learning vs batch retraining | Would need to break train/inference separation |

---

## 4. KILLER — game-changing capabilities we either lack or don't know about

These are the capabilities that, if confirmed, would define what the product IS.
Each is currently in CANNOT or UNSURE — but if we could move any into CAN, the product changes shape.

### Tier 1: would define the product

| Capability | Current status | Why killer |
|---|---|---|
| **GPT-quality generation with auditable memory** | CANNOT (we're byte K-gram, not transformer-quality) | Combine transformer output quality + decompose/edit. The actual product moat. |
| **True continual learning at production scale** — learn A, then B, then C, then D, retain all | UNSURE (only tested A→B single shift) | "LLM that genuinely learns from interactions" vs "LLM that hallucinates corrections away." |
| **Edit-then-query for fact correction** — user uploads correction, substrate updates relevant bundle, future queries reflect it | UNSURE — can edit, but full pipeline integration untested | Solves a fundamental LLM problem: factual updates without retraining. |
| **Provenance for every prediction** — "this output came from these N stored examples" | CAN (pool retrieval indices) but not exposed | Trust / debug / compliance. |

### Tier 2: would unlock product directions

| Capability | Current status | Why killer |
|---|---|---|
| **On-device personalization with continual addition** — train on user data locally (CPU-only) | UNSURE — substrate is compatible (Hebbian only) but full pipeline not built | Privacy + personalization that doesn't go to cloud. |
| **Cross-modal binding** — text concepts bound with image embeddings | UNSURE — multimodal research synthesis exists | Vision-language model with audit capability. |
| **Real-time learning during inference** — every prediction updates W | UNSURE — currently train/inference separate | "Agent that gets smarter as it works" without retrain cycles. |
| **In-context learning via pool** — adapt at query time without weight updates | UNSURE — pool retrieval might natively do this | The transformer feature substrate may already have for free. |
| **Compositional generalization** — novel combinations of learned concepts | UNSURE — not tested | Generalization quality is what makes LMs useful. |
| **Multi-step reasoning** — chain inferences | UNSURE — no current mechanism | Reasoning chains are the current frontier. |

### Tier 3: bonus capabilities (nice if cheap)

| Capability | Current status | Why nice |
|---|---|---|
| **Self-supervised concept discovery (no PPMI)** | UNSURE | Removes a hand-crafted prior. |
| **Hierarchical concepts** | UNSURE | Deeper semantic structure. |
| **Principled forgetting / GDPR-erase** | UNSURE | Compliance feature. |
| **Calibration / uncertainty** | UNSURE | Trustworthy outputs. |

---

## Open questions for next step

1. **Of the Tier-1 killer capabilities, which is the product hypothesis?** "GPT-quality generation with auditable memory" is the most ambitious. "Edit-then-query for fact correction" is the most tractable.
2. **Which UNSURE items are cheap-to-test now?** In-context-learning-via-pool and on-device-personalization are both ~1-week builds. Generation-via-sample-feedback is a ~1-day build (no new training, just inference loop change).
3. **Are there capabilities I've missed?** This v1 map is what I can derive from 86 experiments + the wave14b/c research syntheses. Capabilities I've never thought about would be additions.

---

## Summary tally (against dashboard verdicts)

| Section | ✅ Validated | 🟢 Want stronger | 🟡 Inconclusive | 🔬 Research only | ⚪ Untested | ❌ Closed |
|---|---|---|---|---|---|---|
| Memory primitives | 3 | 2 | 1 | — | — | — |
| Concept structure | 1 | 1 | 1 | — | — | — |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 2 | 1 | — | — | — | — |
| CANNOT section | — | — | — | — | — | 12 |
| UNSURE section | — | — | — | 9 | 12 | — |
| KILLER section | — | — | — | — | 14 | 1 |

**Most-validated areas**: continual learning, R10 K-scaling, K-cliff/decomposition primitives.
**Highest-uncertainty / highest-leverage areas**: anything in KILLER Tier 1, plus the four reopened directions (Wave 9/8/10A/4.5) in UNSURE.
**Decisive followups queued or running**: `r3_sparse_unigram_diagnostic`, `acf_K2944_100trials`, `r10_best_config_K8_verify`, `r10_best_config_N8192_K256`, `r3_disjoint_K64`, `r10_best_config_K1024_retry`.

---

# v2 update (2026-05-20 00:30) — research-driven revisions

Twelve research agents have landed since v1 of this map. Major framework shifts:

## What CHANGED

### Substrate is POOL-BOUNDED, not capacity-bounded
Per wave14e2 spin glass deep dive: AGS α_c=0.138 is the WRONG yardstick. Right
framing is Frady-Sommer sparse-vector capacity, which gives **~350K bundle
headroom against our current ~4K pool** — we're operating at <1.2% of capacity.
The substrate has 50-100x more room than we thought.

**New 🔬 capability**: pool scaling to 100K+ entries. Untested but theoretically
free. Decisive test: `wave14e2_parisi_ultrametricity` (RS vs RSB phase localization).

### R3 should DROP entirely from substrate-unique tier
Per wave14c K=64 collapse research: R3 effect dies as 1/K² × sigmoid(-log K)
via dual-floor mechanism (PPMI sparsity + W info saturation). At K=64 BOTH same
and disjoint variants give ~0. R3 is a K=4-specific small-effect at literature
floor for additive-prior-bias.

**Update**: R3-Laplace concept-conditioned readout bias → ❌ Closed at K≥16 for substrate-unique. Keep as K=4-product appendix only.

### R10 low-K inversion has a mechanism + rescue
Per wave14c2 R10 low-K research: PPMI rank-deficiency at K<8 (only K(K-1)/2
position pairs exist). Best-config concept space collapses to bigram lookup
with beta=16 sharpening wrong labels.

**K-adaptive rescue (NEW 🔬 capability)**:
- `lam(K) = 0.7 + (0.3-0.7)·σ((K-8)/3)`
- `beta(K) = 8 + 8·σ((K-12)/4)`
- `nc(K) = round(min(K(K-1)/2, 200))`

Predicted: matches default at K=2 (±0.02), preserves best at K≥32.

## What's NEW in KILLER Tier 1

### Integer winding-protected memories (SSH-BSC topological)
Per wave14e2 topological research: bind atoms with sublattice structure
`key = sign(a_A + h_q · a_B)` where `h_q` has q domain walls. Topological charge
is the winding number — an INTEGER. Chiral class AIII (Hasan-Kane 10-fold way)
gives CATEGORICAL noise immunity.

**Why killer**: substrate-stored facts get integer-quantized noise protection.
Local bit-flips can shift count by ±1 only at wall-adjacent sites; larger
shifts need coordinated multi-bit flips with probability ~p². Predicted SHARP
KINK at p_c ≈ 1/(2·ν_density).

**Status**: 🔬 — `wave14e2_ssh_bsc_topological` queued (30-min test).

## Mechanism corrections (v1 framings updated)

### LSH for BSC: BinaryIVF not SimHash
Per wave14e LSH research: at our similarity regime (s ∈ [0.1, 0.3], Hamming
radius 0.35-0.45) classical LSH degrades. BinaryIVF (k-means partition) is the
right algorithm. GPU brute-force at N=4096 packed is already ~3ms/query at
P=10M — within target without indexing for current scales. v2: `wave14e_lsh_v2_binaryivf` queued.

### Multi-hop reasoning: bound triples + per-hop cleanup
Per wave14e multi-hop research: encode each fact as `e = subj * rel * obj`,
superpose to fact-base M, then probe with cleanup at each hop. BSC self-inverse
algebra (x·x=1) makes chains clean. **50+ hops viable** with cleanup; ~1 hop
without. v2: `wave14e_multi_hop_v2` queued.

### Hierarchical composition: cleanup between levels
Per wave14e hierarchical research: Plate 1995 chunking requires cleanup at
each level. Without cleanup, noise multiplies; depth 4-5 collapses. With
cleanup, depth 5-6. With sparse block codes, depth 6-8. v2: `wave14e_hierarchical_v2` queued.

### Continuous edits: Bernoulli mixing, not deterministic blend
Per wave14e continuous-edits research: `sign(α·A + (1-α)·B)` is a STEP
function at α=0.5 (FAILS continuity). Correct primitive: per-coordinate
Bernoulli mix (in expectation = soft-bipolar latent). v2: `wave14e_continuous_edits_v2` queued.

## NEW Tier B longshots from materials science

### FFT-as-reciprocal-substrate
Per wave14e materials science: Bloch's theorem + convolution theorem identify
FHRR as the reciprocal substrate where binding becomes pointwise multiplication
in Fourier space. O(N log N) binding instead of O(N²). Half-day build.

### Free hierarchical retrieval index via RSB
If Parisi P(q) shows multi-peaking + ultrametricity > 0.3, substrate is in
RSB phase with FREE O(log P) tree-walk retrieval. 10-min CPU test queued.

### Substrate-as-spin-glass framing
The bundle IS a spin glass. 50 years of statistical mechanics literature
inherited. Sherrington-Kirkpatrick, Parisi, Hopfield all directly apply.

## Updated tally

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 3 | 2 | 1 | — | — | — |
| Concept structure | 1 | 1 | — | — | — | 1 (R3 dropped) |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 2 | 1 | — | — | — | — |
| Topological / spin glass (NEW) | — | — | — | 3 | — | — |
| CANNOT | — | — | — | — | — | 13 (R3 added) |
| UNSURE | — | — | — | 13 | 12 | — |
| KILLER Tier 1 | — | — | — | 5 (added winding) | — | — |
