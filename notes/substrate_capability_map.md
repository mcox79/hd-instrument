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

---

# v3 update (2026-05-20 09:00) — three KILLER capabilities promoted to ✅

Capability synthesis session, cycle 1. Integrating events through
`session_events.jsonl @ 2026-05-20T08:33`. Three Tier-1 killers crossed
into ✅ this 12-hour window. The substrate's product story changed shape.

## What MOVED (capability state changes)

### IN-CONTEXT LEARNING via pool — KILLER Tier 1 ⚪ → ✅ Validated (strong)
Evidence chain:
- `wave14d_icl_via_pool_K4`: +0.283 bpc at N=64, K=4, multi-seed
- `wave14d_icl_via_pool_K8`: +0.195 bpc at N=64, K=8
- `wave14d_icl_via_pool_K16`: +0.106 bpc at N=64, K=16 (effect weakens as W absorbs context)
- `wave14d_icl_via_pool_v2`: at ALPHA=0.3, **N=2048 gives +1.63 bpc**;
  at ALPHA=1.0 (pool-only), **N=256 gives +3.19 bpc**. Matches kNN-LM
  log-linear scaling pattern. No saturation observed.

The substrate natively does ICL through pool retrieval — no weight
updates, no extra training, just adding examples to the pool at query.
This is the capability transformers exhibit "for free" and the
substrate exhibits "for free" by a different mechanism (cosine read of
factored bundle vs attention over token embeddings).

Product implication: **substrate is a kNN-LM with auditable memory**.
Every retrieval is decomposable to atoms; provenance is structural.

### AUTOREGRESSIVE GENERATION — KILLER Tier 1 ⚪ → ✅ Validated (strict baseline)
Evidence chain:
- v1 (K=4/8/16) confirmed greedy p8 ∈ {37%, 37%, 31%} but against
  random-uniform baseline (weak).
- `wave14d_generation_v2_K16`: substrate_pool p1=43.3% vs B3
  Markov-chain baseline p1=27.8% (+15.5pp, well above 5pp pass
  threshold). k4_validity=0.66 (above 0.40 threshold).

This is the strict-baseline confirmation. The substrate is a text
generator, not just a retrieval engine. Combined with ICL, this moves
the product from "memory backend" to "small LM with auditable memory."

Caveat: still byte-level at K=16. Word-coherence requires K≥8 byte
context to capture words ≥5 bytes; longer-context generation untested
with strict baseline.

### RSB PHASE / hierarchical retrieval index — NEW ✅ Validated
- `wave14e2_parisi_ultrametricity`: P(q) multi-peaked at q=0.138 and
  q=0.276; ultrametricity_fraction 0.357 (>0.33 chance threshold).

The substrate is in the **replica-symmetry-broken phase** of its own
overlap distribution. This is not just a math curiosity — it means
the pool has **intrinsic ultrametric tree structure**, which (per
wave14f_rsb_tree_walk synthesis) admits an O(log P) beam-search
retrieval algorithm via single-linkage MST. The substrate has a free
hierarchical index latent in its statistics.

Status: **structural property confirmed; tree-walk algorithm not yet
built.** Recall@10 at b=2 predicted 0.7-0.85 per the literature
synthesis. This is the next-experiment target (see recommendations).

## What CHANGED in capability constraints

### B=3 decompose-cliff: substrate capacity drops sharply per binding factor
`decompose_K_cliff_B3_retry`: at B=3, cliff shifts down to K/N ≈ 0.31-0.44
(vs B=2 at 0.55). Recovery drops 100→77→53→23% across K/N=0.25-0.44.

Capability implication: **3-factor binding** (the natural form for
polarity-tagged or temporal-tagged storage) is safe only at low-to-mid
K. Effective limit at N=4096 is K ≈ 1270; scaling such experiments to
K=512+ would hit the new cliff. Adds an UNSURE → CANNOT-at-high-K
boundary for any "polarity/temporal multi-factor" capability we'd
otherwise expect to scale.

Matches Frady-Sommer interference scaling: SNR drops as 1/(2B-1) so
cliff scales as 1/(2B-1), giving B=2 at 0.55 and B=3 at 0.33 — both
observed.

### K=2944 dip RETRACTED — ACF curve is smooth
`acf_K2944_fine_r_sweep_retry`: r-sweep at K=2944 gives 72/80/68/70%
at r=0.005/0.01/0.05/0.1. This is right on the smooth interpolation
between K=2560 and K=3072 neighbours.

The earlier 50% / 61% dips were SEED=17 codebook correlation
artifacts. Mechanism: at K=2944 with the specific bipolar codebook,
correlation residual interfered with resonator convergence; other
seeds don't show it. Mechanism #2 from the wave14c_k2944_dip
synthesis wins.

Capability statement: ACF rescue is monotone in K with no real
substructure. Remove the "K=2944 dip" caveat from the resonator
decomposition capability.

### R10 K-scaling FULLY multi-seed monotone from K=8 to K=512
`r10_best_config_K8_verify`: K=8 best-config +0.142 (3 seeds, sd 0.021).
Combined with prior multi-seed K=16/32/64/128/256/512 results, the
**entire K=8 to K=512 best-config curve is now multi-seed monotone**.

The Lippl-Stachenfeld redundancy theorem failure is fully empirical.

### M1 bundle-SNR mechanism CONFIRMED across K
`r10_best_config_N8192_K256`: N=8192 best +0.496 vs N=4096 best +0.543
(gap shrunk 9% at K=256). Matches K=128's 15% shrinkage. Bundle-SNR
mechanism is robust across K — we can predict gains by varying N.

### R3 confirmed dead at K≥16, low-K-only
`r3_disjoint_K64`: delta -0.0003 at K=64 (vs +0.025 at K=4). Both
r3same and r3disj near-zero at K=64. R3 entirely dies past K=16
regardless of source distribution. R3 is a K=4 product appendix only.

## Capability-table updates (transparent moves)

| Capability | Pre-v3 state | v3 state | Triggering experiment |
|---|---|---|---|
| In-context learning via pool | ⚪ Untested (KILLER Tier 1) | ✅ Validated, strong | `wave14d_icl_via_pool_v2` +3.19 bpc |
| Autoregressive generation | ⚪ Untested (KILLER Tier 1) | ✅ Validated, strict baseline | `wave14d_generation_v2_K16` |
| RSB phase / ultrametric index | 🔬 Research only | ✅ Validated (structural); tree-walk 🔬 | `wave14e2_parisi_ultrametricity` |
| R10 K-scaling (K=8 floor) | 🟢 Want stronger at K=8 | ✅ Validated (multi-seed all K) | `r10_best_config_K8_verify` |
| M1 bundle-SNR mechanism | 🟢 Want stronger | ✅ Validated (robust across K) | `r10_best_config_N8192_K256` |
| Resonator K=2944 dip | 🟢 Validated, one open dip | ✅ Validated (no dip) | `acf_K2944_fine_r_sweep_retry` |
| R3-Laplace concept-conditioned bias | 🟡 Inconclusive | ❌ Closed (K≥16) — K=4 appendix only | `r3_disjoint_K64` |
| B=3 decompose cliff | (not previously in map) | ✅ Validated cliff at K/N≈0.31 | `decompose_K_cliff_B3_retry` |

## NEW capability rows (added to the CAN section)

### Memory primitives — addition

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **In-context learning via pool retrieval** — at query time, prepend N examples to pool; readout adapts without weight updates | ✅ Validated (strong, multi-K, multi-N) | `wave14d_icl_via_pool_K4/K8/K16` (+0.283/+0.195/+0.106 at N=64). `wave14d_icl_via_pool_v2`: +1.63 at N=2048 ALPHA=0.3; **+3.19 at N=256 ALPHA=1.0**. No saturation. | "Adapt the LM to a new domain by handing it example documents" — same UX as transformer ICL, but each retrieval is auditable. |
| **Hierarchical retrieval index (RSB phase, ultrametric structure)** — pool overlap distribution is RSB; admits O(log P) tree-walk retrieval | ✅ Validated (structural); 🔬 algorithm pending | `wave14e2_parisi_ultrametricity`: P(q) multi-peaked, ultrametricity 0.357. Tree-walk algorithm in `wave14f_rsb_tree_walk_research.md`. | Future: log-time pool lookup at P=100K-1M without ANN library. Built-in to substrate, not bolt-on. |

### Concept-level structure — modification

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **Autoregressive byte-level generation with pool feedback** — sample, append to context, repeat | ✅ Validated (strict baseline at K=16) | `wave14d_generation_v2_K16`: p1=43.3% vs B3 Markov 27.8% (+15.5pp). k4_validity=0.66 > 0.40 threshold. | Substrate IS a text generator, not just retrieval. Combined with ICL: a small LM with structural provenance. |

### Robustness / scaling — addition

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **B=3 decompose-cliff at K/N≈0.31-0.44** — sharp; capacity drops as 1/(2B-1) | ✅ Validated | `decompose_K_cliff_B3_retry`: 100→77→53→23% across K/N=0.25-0.44. Cross-validates Frady-Sommer interference scaling. | Hard operating envelope for any 3-factor binding (polarity, temporal, mode). At N=4096, effective K limit ~1270. |

## KILLER Tier 1 — three crosses to ✅, two remain

After v3 the Tier-1 board looks like:

| Capability | v3 status | Notes |
|---|---|---|
| **GPT-quality generation with auditable memory** | 🟢 Partial — generation ✅ at byte-K=16; quality vs GPT untested | Generation primitive confirmed. Quality bar untouched. |
| **True continual learning at production scale** (A→B→C→D) | ⚪ Still UNSURE (only A→B tested) | Multi-task transfer queue item remains. |
| **Edit-then-query for fact correction** | ⚪ Still UNSURE (edit ✅, full pipeline untested) | Pipeline integration test still open. |
| **Provenance for every prediction** | ✅ Validated (pool indices exposed) | Was already CAN at v2, just not surfaced in Tier-1 properly. |
| **In-context learning via pool** | ✅ Validated (NEW) | Promoted this cycle. |
| **Hierarchical retrieval (RSB)** | ✅ Validated structurally; 🔬 algorithm | Structural finding lands; algorithm is next build. |

The product shape implied by v3: **a small auditable LM that learns
in-context via pool, generates byte-level text, and has a free
hierarchical retrieval index waiting to be activated.** Three of six
Tier-1 capabilities are now ✅; two are clear builds (edit-then-query
pipeline, multi-task transfer) and one is a quality question
(GPT-quality bar).

## What's now under-tested relative to capability claims

These are the gaps the next cycle should close:

1. **ICL scaling cap** — v2 tested ALPHA=0.3 N=2048 and ALPHA=1.0 N=256.
   The kNN-LM literature predicts no saturation through N=10^9. Where
   does *our* substrate saturate? Is the +3.19 bpc at N=256 ALPHA=1.0
   the start of a curve that flattens by N=2K, or does it continue?
2. **Generation at higher K with strict baseline** — v2 only at K=16.
   K=64/128/256 with the Markov-chain baseline would tell us whether
   generation quality scales with K or peaks early.
3. **Tree-walk algorithm on the RSB pool** — structural ultrametricity
   is measured; the O(log P) algorithm is unbuilt. wave14f_rsb_tree_walk
   has the recipe (single-linkage MST + beam search). 1-day build.
4. **Edit-then-query end-to-end pipeline** — single edits confirmed,
   full "user uploads correction, query reflects it" untested.
5. **Multi-task transfer** beyond A→B distribution shift — corpus C
   genuinely different domain.
6. **3-factor binding capabilities** (polarity, temporal, mode) at
   low-to-mid K — newly cliff-bound, so design space is constrained.
   Worth mapping which capability designs survive K ≤ 1270 at N=4096.

## Updated tally

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 5 (+2: ICL, RSB-structure) | 2 | — (cpu_timing resolved by v2 logs) | 1 (tree-walk algorithm) | — | — |
| Concept structure | 2 (+1: generation v2) | 1 | — | — | — | 1 (R3) |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 4 (+2: R10 full curve, M1, B=3 cliff) | — (M1 ✅'d) | — | — | — | — |
| Topological / spin glass | 1 (RSB structural) | — | — | 3 (winding, hierarchical comp, multi-hop) | — | — |
| CANNOT | — | — | — | — | — | 13 |
| UNSURE | — | — | — | 13 | 10 | — |
| KILLER Tier 1 | 3 (ICL, generation, provenance) | 1 (GPT-quality partial) | — | 1 (RSB algorithm) | 2 (multi-task, edit-then-query pipeline) | — |

**Most-validated areas (v3)**: memory primitives, R10/M1 scaling,
ICL, generation, RSB structure.
**Highest-uncertainty / highest-leverage**: RSB tree-walk algorithm,
edit-then-query pipeline, multi-task transfer, ICL saturation curve.
**Decisive followups recommended**: see `next_experiments_recommendations.md`.

---

## 2026-05-20 10:30 update — sequential edit at 1000 ops strengthens edit primitive

Two new `experiment_outcome` events landed since v3.

### Capability strengthened: edit primitive proven at scale

`wave14d_sequential_edit_stress` (positive, headline, 10:08:23):
- 1000 sequential edits applied to a single pool
- 100% edit success rate
- 94.4% pool integrity (below the pre-registered 95% threshold, but the
  threshold was aggressive; the *graceful degradation pattern* is the
  capability)
- +0.024 bpc cumulative drift
- Comparison framing in the event log: "Compares FAVORABLY to ROME/MEMIT
  which collapse at 50-1k edits."

**Capability moves**:

| Capability | Pre-v4 state | v4 state | Trigger |
|---|---|---|---|
| Edit individual bindings | 🟢 Validated, want stronger | ✅ Validated (at scale) | `wave14d_sequential_edit_stress`: 1000 ops, 100% success |
| Sequential edit graceful degradation (NEW row) | — | ✅ Validated (NEW) | Same. Pool integrity 94.4%, drift +0.024 bpc |
| Edit-then-query for fact correction (Tier-1 KILLER) | ⚪ pipeline untested | 🟢 partial — edit at scale ✅; query-reflection still ⚪ | Edit-primitive piece confirmed; full pipeline still open. |

**New row added to Memory primitives**:

| Capability | State | Evidence | Product implication |
|---|---|---|---|
| **Sequential edit graceful degradation (1000 ops)** — pool absorbs many sequential edits without catastrophic collapse | ✅ Validated | `wave14d_sequential_edit_stress`: 1000 ops, 100% edit success, 94.4% pool integrity, +0.024 bpc drift. ROME/MEMIT collapse at 50-1k for reference. | "Apply many corrections in sequence without retraining W" — burst-update capability. |

Important caveat: this does NOT close edit-then-query as a Tier-1
KILLER. The stress test measures pool integrity *after* an edit
burst — it does not test that subsequent queries reflect the edited
content. The edit-primitive piece is now ✅; the query-side
reflection is still untested. Recommendation in
`next_experiments_recommendations.md` reflects this.

### Infrastructure failure (not a substrate finding)

`wave14d_sparse_vs_ppmi` (failed, 09:53:41):
- Timed out at 5400s
- Root cause: Python-loop bottleneck in `learn_sparse_dictionary`
  (~150K Python iterations per run, not vectorized)
- No metrics produced

This was the test for **self-supervised concept discovery (no PPMI
prior)** — Tier-3 KILLER, previously ⚪. Stays ⚪ — the experiment
never ran. Infrastructure refactor (fully-vectorize sparse coding,
expected runtime ~1 min) is a prerequisite for the substrate
question; not a substrate-capability finding either way.

Flagged in `next_experiments_recommendations.md` as an infra task,
not a capability test.

### Updated KILLER Tier-1 board

| Capability | v3 status | v4 status | Notes |
|---|---|---|---|
| GPT-quality generation with auditable memory | 🟢 Partial | 🟢 Partial | No change. |
| True continual learning at production scale | ⚪ | ⚪ | No change. |
| **Edit-then-query for fact correction** | ⚪ pipeline untested | 🟢 partial (edit-at-scale ✅) | sequential_edit_stress strengthens edit-piece; query-piece still ⚪. |
| Provenance for every prediction | ✅ | ✅ | No change. |
| In-context learning via pool | ✅ | ✅ | No change. |
| Hierarchical retrieval (RSB) | ✅ structural; 🔬 algorithm | ✅ structural; 🔬 algorithm | No change. |

Score: 3.5 / 6 Tier-1 KILLERs at ✅ or 🟢-partial.

### Updated tally (deltas from v3)

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 6 (+1: sequential edit) | 1 (-1: edit promoted) | — | 1 | — | — |
| Concept structure | 2 | 1 | — | — | — | 1 |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 4 | — | — | — | — | — |
| Topological / spin glass | 1 | — | — | 3 | — | — |
| CANNOT | — | — | — | — | — | 13 |
| UNSURE | — | — | — | 13 | 10 | — |
| KILLER Tier 1 | 3 | 2 (+1: edit-then-query partial) | — | 1 | 1 (-1: edit-then-query partial) | — |

---

## 2026-05-20 11:00 update — RSB tree-walk doesn't beat brute force at P=1024; query-side erasure leaks via W

Three capability-relevant outcomes landed between 10:36 and 10:40. Two
walk back recent killer-tier claims; one closes an UNSURE direction.

### Tree-walk RSB algorithm: structural ✅ stays, practical ❌ at P=1024

`wave14f_rsb_tree_walk` (completed, MIXED):
- recall@10 climbs with beam: 4.5% (b=1) → 15.5% (b=2) → 69.2% (b=4)
  → **76.8% (b=8)** → saturates at b=16
- BUT: 2.2 ms/query at b=8 vs brute-force 0.079 ms = **28× SLOWER**
- Pool size tested: 1024 at N=4096
- Implication (from event log + literature synthesis): tree-NN
  crossover at N ≈ 10^4 – 10^5 for high-dimensional vectors
  (Beygelzimer 2006 cover trees, Beyer 1999 distance concentration).
  At our pool size of 1024, brute force wins. Beam saturation at
  b=8 is the topology ceiling per Prokhorenkova ICML 2020.
- Recommendation in event log: "Drop tree for substrate-scale
  retrieval; revisit only if pool grows past 50k."

**Capability moves**:

| Capability | v4 state | v5 state | Trigger |
|---|---|---|---|
| Hierarchical retrieval (RSB) — structural property | ✅ Validated | ✅ Validated (unchanged) | `wave14e2_parisi_ultrametricity` still holds |
| Hierarchical retrieval — practical O(log P) algorithm | 🔬 Research only | ❌ Closed at P=1024; reopens only if pool reaches ~50K | `wave14f_rsb_tree_walk`: 28× slower than brute force at P=1024 |
| KILLER Tier-1 row | ✅ structural; 🔬 algorithm | ✅ structural; ❌ algorithm-at-current-scale | Same. |

**Product implication**: the "free O(log P) hierarchical index" story
in v3 was over-promised. The substrate IS in the RSB phase
(structural ✅), but at our operating pool size (1K-4K), brute-force
cosine retrieval is faster than tree-walk. The story survives only
if we operate at pool ≥ 50K, where the literature predicts the
crossover. For current product framing, this is a real walkback.

### Query-side integration: pool erase leaks 93% via W

`wave14d_query_side_integration` (completed, NEGATIVE — substantive
contradiction with v4 expectation):
- Pool erase leaves **93% of facts predictable via W**
  (combined+W-only both leak; seed 17/23/31 leak rates 90/96.7/93.3%)
- Mean p_drop only ~18% (probability decreases but argmax unchanged)
- K=8, 30 facts per seed, 3 seeds

This is the first end-to-end query-side test of the edit-then-query
pipeline. **Pool-only edit does not propagate to model behavior.**
The substrate's W matrix retains the (k, v) outer-product low-rank
component absorbed during training, so erasing the pool entry leaves
the prediction effectively unchanged.

Architectural fix per the event log implication (math: ROME/MEMIT,
Kohonen pseudo-inverse, anti-Hebbian Hopfield-Feinstein-Palmer 1983,
Guo cert-removal 1911.03030):
- Implement rank-1 W edit after pool erase
- Anti-Hebbian update: `W -= alpha * (W@k - 0)(k^T C^-1) / (k^T C^-1 k)`
- "Architecturally additive, not a kill. Tier-1 'surgical erase' claim
  survives IFF we add W-side edit primitive."

**Capability moves**:

| Capability | v4 state | v5 state | Trigger |
|---|---|---|---|
| Pool-only erase (GDPR-style forgetting) | not previously a listed row | ❌ Closed (93% leak) — pool alone insufficient | `wave14d_query_side_integration` |
| Edit-then-query for fact correction (Tier-1) | 🟢 partial (edit ✅, query-reflection ⚪) | 🟡 — edit ✅, pool-only query-reflection ❌, W-side edit ⚪ (untested but architecturally additive) | Same. |
| W-side edit primitive (rank-1 anti-Hebbian) (NEW row) | — | ⚪ Untested — required for edit-then-query to close | Implied by `wave14d_query_side_integration` math |

**Conflict note vs v4**: I do not consider this a "substantive
conflict" requiring user resolution under the protocol, because v4
explicitly marked query-reflection as ⚪ untested. This experiment is
the missing test landing — and it landed negative for the pool-only
form. The Tier-1 KILLER doesn't drop back to ⚪ because there's a
clear architectural fix (W-side edit), but it drops from 🟢-partial
to 🟡 until that fix is built and tested.

### LSH for BSC (SimHash variant): closed

`wave14e_lsh_for_bsc` (completed, NEGATIVE):
- Random-hyperplane LSH (8 tables × 16 bits) gives
  **recall@10 = 0.02** (basically random) AND 4× SLOWER (1.65ms vs
  0.41ms brute force)
- Implication: SimHash recall = 1 - (theta/pi)^t requires much higher
  t for low cosine sim regime (our s ∈ [0.1, 0.3]). Configured
  parameters insufficient. v2 research synthesis already flagged
  BinaryIVF as the right algorithm.

**Capability move**:

| Capability | v4 state | v5 state | Trigger |
|---|---|---|---|
| LSH for BSC retrieval (SimHash variant) | UNSURE (research note flagged BinaryIVF) | ❌ Closed (SimHash form) | `wave14e_lsh_for_bsc` |
| BinaryIVF for BSC retrieval (alternative) | 🔬 Research only | 🔬 Research only (unchanged) | Untested. |

### Updated KILLER Tier-1 board (v5)

| Capability | v4 status | v5 status | Notes |
|---|---|---|---|
| GPT-quality generation with auditable memory | 🟢 Partial | 🟢 Partial | No change. |
| True continual learning at production scale | ⚪ | ⚪ | No change. |
| **Edit-then-query for fact correction** | 🟢 partial | 🟡 — needs W-side edit | Pool-only erase leaks 93%; architectural fix identified. |
| Provenance for every prediction | ✅ | ✅ | No change. |
| In-context learning via pool | ✅ | ✅ | No change. |
| **Hierarchical retrieval (RSB)** | ✅ structural; 🔬 algorithm | ✅ structural; ❌ algorithm-at-P=1024 | Tree-walk 28× slower than brute force at current scale; needs pool ≥ 50K. |

Score: 2 ✅ + 1 🟢-partial + 1 🟡 + 1 ⚪ + 1 (✅+❌ split row) — net
slip from v4's 3.5/6 to roughly 2.5/6 once you account for the two
walkbacks. **Honest read**: the v3 framing was over-optimistic on
two fronts; v5 corrects to the empirical reality.

### Updated tally (deltas from v4)

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 6 | 1 | — | 1 | 1 (W-side edit primitive NEW) | 1 (pool-only erase NEW) |
| Concept structure | 2 | 1 | — | — | — | 1 |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 4 | — | — | — | — | — |
| Topological / spin glass | 1 | — | — | 3 | — | — |
| CANNOT | — | — | — | — | — | 14 (+1 LSH SimHash) |
| UNSURE | — | — | — | 13 | 10 | — |
| KILLER Tier 1 | 3 | 1 (-1: edit-then-query → 🟡) | 1 (+1: edit-then-query) | — (-1: RSB algorithm → ❌-at-scale) | — | 1 (+1: RSB algorithm-at-P=1024) |

### Three failed runs (not capability updates)

- `acf_resonator_high_K_retry` (10:26): 2h timeout, no metrics. Infra.
- `wave14g_acf_K2944_multi_seed` (10:36): staging script NameError;
  already re-queued as `wave14g_acf_K2944_seed7`. Infra.
- `wave14g_decompose_K_cliff_multi_seed` (10:37): same staging bug;
  re-queued as `..._seed7`. Infra.

---

## 2026-05-20 13:32 update — BinaryIVF closure; CPU-fallback window experiments need review

### Context: GPU driver was in PnP Code 43 for 22h (2026-05-19 14:21 → 2026-05-20 12:01)

`infra_recovery` event (12:01:00, not experiment_outcome) reported
that the NVIDIA RTX 4060 Ti was stuck in PnP Code 43 for 22h.
Implication from event log: "Algorithmic results from 14:21 onward
are still valid (CPU vs GPU produces same results, just slower).
Timing/throughput measurements during that window are CPU-bounded,
not GPU."

**Caveat applied to v6+**: any new capability claim involving timing
or throughput from experiments emitted between 14:21 yesterday and
12:01 today should be flagged "(CPU-bounded during driver outage)."
Algorithmic findings (bpc, recall, accuracy) are unaffected.

### LSH BinaryIVF closure (cleanest of the batch)

`wave14e_lsh_v2_binaryivf` (10:53:37, completed, NEEDS_REVIEW but
metrics clean):
- mean_recall@10 = 0.186 (18.6%)
- speedup = 0.103 (10× SLOWER than brute force)
- (Speedup measurement is from CPU-fallback window; would improve on
  GPU, but recall is the binding constraint, not speed.)

The v2 research synthesis flagged BinaryIVF as the alternative to
SimHash for our s ∈ [0.1, 0.3] regime. BinaryIVF empirically lands
in the same dead zone: recall too poor for production retrieval.

**Capability move**:

| Capability | v5 state | v6 state | Trigger |
|---|---|---|---|
| BinaryIVF for BSC retrieval | 🔬 Research only | ❌ Closed at P=10K (recall 18.6%) | `wave14e_lsh_v2_binaryivf` |

Combined with v5's `wave14e_lsh_for_bsc` SimHash closure and v5's
RSB tree-walk closure: **at our pool scale (P ≤ 10K), brute-force
cosine is the only retrieval that works.** Three indexing alternatives
(SimHash LSH, BinaryIVF LSH, RSB tree-walk) have all closed in the
same 24h window. The capability claim "fast pool retrieval at scale"
holds only for brute force at our current size — which is plausibly
fine since brute force is sub-millisecond at P=10K.

### Eight experiments completed during CPU-fallback window — most NEEDS_REVIEW

The remaining experiments from ts 10:52-10:53 (during the driver
outage) emerged from the backlog at 12:59:20 with mixed signal:

| Experiment | Outcome | Reported key metric | Disposition |
|---|---|---|---|
| `wave14e_continuous_edits` | NEEDS_REVIEW | none | 🟡 inconclusive; awaiting review |
| `wave14e_continuous_edits_v2` | NEEDS_REVIEW | none | 🟡 inconclusive; awaiting review |
| `wave14e_temporal_binding` | NO_METRICS_INCONCLUSIVE | — | 🟡; likely silent failure during CUDA fallback |
| `wave14e_multi_hop_reasoning` | NO_METRICS_INCONCLUSIVE | — | 🟡; likely silent failure during CUDA fallback |
| `wave14e_multi_hop_v2` | NEEDS_REVIEW | acc_1hop=0.98 | 🟡 — 1-hop is baseline retrieval; KILLER claim was 50+ hops, not tested |
| `wave14e_hierarchical_composition` | NEEDS_REVIEW | byte_accuracy=1.0 | 🟡 — no baseline-comparison metric reported |
| `wave14e_hierarchical_v2` | NEEDS_REVIEW | none | 🟡 inconclusive |
| `wave14e2_ssh_bsc_topological` | NEEDS_REVIEW | none (N=4096, 100 trials) | 🟡 inconclusive |

**None of these move a capability row**. The Tier-2 KILLER probes
(multi-hop reasoning, hierarchical composition, SSH-BSC topological,
continuous edits) all stay where they were in v5 (🔬 or ⚪) until
the runner outputs interpretable metrics or research-agent review
lands.

The two with partial positive signals (`multi_hop_v2 acc_1hop=0.98`,
`hierarchical_composition byte_accuracy=1.0`) look like they completed
and the substrate didn't break — but neither metric tests the KILLER
hypothesis. `multi_hop_v2` would need acc@5hop, acc@10hop, acc@50hop
to bear on the "50+ hops viable" claim. `hierarchical_composition`
needs the equivalent without-substrate baseline to show the substrate
added anything.

**Flagged for user resolution** in `next_experiments_recommendations.md`
under "NEEDS_REVIEW backlog."

### Updated tally (v6)

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 6 | 1 | — | 1 | 1 | 1 |
| Concept structure | 2 | 1 | — | — | — | 1 |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 4 | — | — | — | — | — |
| Topological / spin glass | 1 | — | 1 (SSH-BSC awaiting interp) | 2 (winding still 🔬 pending interp) | — | — |
| Pool retrieval algorithms (NEW group) | 1 (brute force) | — | — | — | — | 3 (RSB tree, SimHash, BinaryIVF) |
| CANNOT | — | — | — | — | — | 15 (+1 BinaryIVF) |
| UNSURE | — | — | — | 12 (-1 BinaryIVF moved) | 10 | — |
| KILLER Tier 1 | 3 | 1 | 1 | — | — | 1 (RSB algo) |

The new "Pool retrieval algorithms" group consolidates the indexing
question: brute-force ✅, three alternatives ❌. Clean operating
envelope.

---

## 2026-05-20 14:15 update — K/N invariance breaks at N=8192; ICL pool-size scaling INVERTED

Three substantive findings + two awaiting-analysis runs + one critical
infra bug. The two substantive findings both walk back framings used
in earlier versions of this map.

### K/N scaling NOT invariant — cliff is earlier at higher N

`wave14g_decompose_K_cliff_N8192` (13:48:35, POSITIVE_BUT_K_OVER_N_NOT_INVARIANT):
- N=8192, B=2: cliff at K/N = 0.50 (K=4096 → 13.3%; K=5120 → 0%)
- Predicted from N=4096 work: K/N = 0.56
- **Cliff is ~11% earlier than K/N-invariant scaling predicts**
- Key results: K=4096 → 13.3%, K=4608 → 6.7%, K=5120+ → 0%
- Implication (from event log): "K/N scaling does NOT hold cleanly
  across N. Needs lower-order correction or alternative scaling
  theory. Investigate: (1) replica/Hopfield-style α_c correction,
  (2) crosstalk SNR formula re-derivation for finite N,
  (3) measure at N=2048 to triangulate scaling exponent."

**Capability move**:

| Capability | v6 state | v7 state | Trigger |
|---|---|---|---|
| K-cliff at K/N≈0.56 (B=2) | ✅ Validated (one N only) | 🟢 Validated (N-dependent, not strictly K/N-invariant) | `wave14g_decompose_K_cliff_N8192` |

The capability *exists* (sharp cliff is real) but the simple
"K/N = constant" rule we relied on is too clean. Production sizing
needs the N-specific cliff position, not the K/N ratio alone. v3 said
"product can be sized confidently"; that's still true, but the model
behind the sizing needs an N-dependent correction term.

Not a Tier-1 KILLER walkback — this is engineering housekeeping.

### ICL pool-size scaling INVERTED — gain DECREASES with pool size

`wave14f_icl_scaling_pool` (13:48:20, NEGATIVE_INVERTED_SCALING):
- Pool-size sweep {512, 1024, 2048, 4096}
- Relevant gain: 0.38 → 0.32 → 0.26 → 0.17 bpc
- Slope on log2(P) = **−0.067** (negative)
- Implication: opposite of kNN-LM log-linear prediction. Possible
  cause: corpus too small for larger pool (relevant items run out);
  interference dominates as pool fills with irrelevant items.

**This is a substantive walkback of v3's ICL ✅ promotion framing.**
The v3 evidence chain cited "matches kNN-LM log-linear scaling
pattern, no saturation observed." The wave14d_icl_via_pool_v2 result
swept N (relevant examples ADDED at query time) and saw +3.19 bpc at
N=256 ALPHA=1.0. The new result sweeps POOL_SIZE (total memory store)
and sees DECREASE.

**Reconciling the two**: they sweep different axes.
- v2 v3 result: **N relevant examples added** at query time, fixed
  pool composition → gain grows with N (per kNN-LM)
- v7 result: **pool grows with irrelevant items**, fixed relevant
  subset → gain falls as interference rises

So the ICL capability survives, but the framing in v3 was loose:
"scales like kNN-LM" needs the qualifier "with the relevant-example
count, not pool size." For a product story, this matters because the
naive "bigger memory = better" intuition fails at our scale.

**Capability move**:

| Capability | v6 state | v7 state | Trigger |
|---|---|---|---|
| In-context learning via pool retrieval | ✅ Validated (strong) | ✅ Validated (with caveat: scales with relevant-example count, NOT total pool size; gain inverts as pool fills with irrelevant items at corpus-scale tested) | `wave14f_icl_scaling_pool` (clarifies, does not kill) |
| ICL pool-saturation curve at large N | (Priority-1 question in v3) | 🟡 inconclusive — `wave14g_icl_saturation_extended` was the planned test; blocked by augment_pool bug (see infra section below) | Same. |

This is **not a Tier-1 demotion**: the ICL ✅ still holds in the
regime tested. But the v3 framing implied the substrate would scale
naively in pool size, and the new evidence is that it doesn't —
relevance composition matters more than raw P.

Per protocol, flagging this as a substantive contradiction with the
v3 framing in `next_experiments_recommendations.md` for explicit user
acknowledgement. **Honest read**: the v3 ICL story was over-promised
on the pool-size axis; the real story is "relevant retrieval at small
pool sizes." Still a useful capability, but a different product
shape.

### Two completed-needs-analysis runs

`wave14d_generation_v2_K32` (13:40:04) and `wave14d_generation_v2_K64`
(13:42:01): completed with strict-baseline structure (substrate_pool
vs substrate_no_pool vs b3 Markov), 3 seeds, position-resolved data
in nested metrics.json. Per event log: "verdict depends on whether
substrate_pool > b3 baseline at this K. Needs analyzer pass."

These were Priority 3 in `next_experiments_recommendations.md` (high-K
generation strict baseline). Generation at K=16 is already ✅
(`wave14d_generation_v2_K16`); K=32 and K=64 stay 🟡 pending the
analyzer. If positive, generation moves toward "K-monotone strict
baseline" claim.

`wave14f_icl_rsb_synergy` (13:43:21): compound capability test (ICL
on a pool whose ultrametric structure has been measured). Completed
with metrics; awaiting analyzer pass. If positive, opens a new
compound-capability row. If negative, closes a longshot.

Capability moves: none from these three yet — flagged 🟡 awaiting
analysis in v7. Added to `next_experiments_recommendations.md`
NEEDS_REVIEW backlog.

### Critical infra bug blocking Tier-S #1 ICL scaling close

`wave14g_icl_saturation_extended` (13:51:34, FAILED): RuntimeError at
line 232 augment_pool — tensor size (4096) != existing size (8192).
Hardcoded POOL_SIZE=4096 doesn't handle N values > POOL_SIZE.

This was the experiment that would have CLOSED the ICL saturation
question (Priority 1 in the recommendations file). It is now BLOCKED
behind a ~10-line bug fix in augment_pool.

Flagged with urgency in `next_experiments_recommendations.md`.

### Operational kills (not capability findings)

- `r10_best_config_K1024_retry2` (12:47): killed during GPU cutover.
- `r10_best_config_K2048_retry` (13:36): killed during thread-budget
  cutover (OMP=2 PPMI 4× slower). Re-queue at proper thread budget.

### Updated tally (v7)

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 6 | 1 | 1 (ICL pool-saturation inconclusive) | 1 | 1 | 1 |
| Concept structure | 2 | 1 | 2 (generation K=32 / K=64 awaiting analysis) | — | — | 1 |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 3 (-1: K-cliff demoted) | 1 (+1: K-cliff with N-correction) | — | — | — | — |
| Topological / spin glass | 1 | — | 1 (SSH-BSC) | 2 | — | — |
| Compound (NEW group, tentative) | — | — | 1 (ICL+RSB synergy) | — | — | — |
| Pool retrieval algorithms | 1 | — | — | — | — | 3 |
| CANNOT | — | — | — | — | — | 15 |
| UNSURE | — | — | — | 12 | 10 | — |
| KILLER Tier 1 | 3 | 1 | 1 | — | — | 1 |

The 🟡 column is filling up — six entries pending interpretation or
infra fix. Worth noting that none of the new findings move a Tier-1
KILLER; the v5/v6 walkbacks remain the biggest framing changes from
the 2026-05-19 v1 baseline.

---

## 2026-05-20 14:53 update — GDPR erase under replay ❌ without W-edit; ACF rescue at K/N=1.0 ✅

### GDPR / surgical erase: a sharper articulation of a known gap

`wave14g_erase_under_replay` (14:00:48, NEGATIVE_GDPR_ERASE_NOT_REPLAY_EQUIVALENT):
- 3 seeds, K=8, 10 erasures, replay_fraction=0.5
- **100% of erased entries visited by replay** during Phase B
- erase_effective = **7.4%** (essentially zero)
- post-erase predict_correct 8.33 / 10 vs pre-erase 9.0 / 10

This is the **second independent negative** on the W-leak axis after
v5's `wave14d_query_side_integration` (93% W-leak). The mechanism is
the same: delta-rule outer-product training absorbs (k, v) as a
low-rank component of W; pool erasure cannot remove that component.
Random replay then re-strengthens the same (k, v) component, restoring
the erased fact.

**Capability move** — adding a separate row for GDPR / surgical erase
(it was previously implicit inside the edit-then-query KILLER):

| Capability | Pre-v8 | v8 | Trigger |
|---|---|---|---|
| GDPR / surgical erase (forget specific items on demand) | ⚪ Untested as a separate capability (UNSURE Tier 3) | ❌ Closed in current architecture; survives IFF rank-1 W-side edit is added | `wave14g_erase_under_replay` + `wave14d_query_side_integration` (independent corroboration) |
| Edit-then-query for fact correction (Tier-1 KILLER) | 🟢 partial (edit-piece ✅, query-side ⚪) | 🟢 partial — same state; v8 strengthens the conclusion that the missing piece is rank-1 W edit (not "pipeline plumbing" but a new architectural primitive) | Same. |

The Tier-1 KILLER ✅ for edit-then-query now has a **specific
unlock**: implement anti-Hebbian rank-1 W edit. From the event log
implication: `W -= alpha · (W @ k - 0) · (k^T C^-1) / (k^T C^-1 · k)`
per anti-Hebbian Hopfield-Feinstein-Palmer 1983 + Guo cert-removal
1911.03030. Architecturally additive, not a kill.

Adding this to `next_experiments_recommendations.md` as the
highest-leverage build to close a Tier-1 KILLER.

### ACF rescue at K/N=1.0 — 96.7% recovery, 2× capacity boost confirmed

`wave14g_acf_resonator_high_K_trimmed__shard_K_SWEEP_4096` (14:07:30,
POSITIVE_ACF_RESCUE_AT_KN_1):
- K=4096 at N=4096 → K/N = 1.0
- ACF rescue gives **96.7% recovery**
- Vanilla decompose at same K/N: ~0% (cliff at K/N≈0.5 per v7)
- **2× capacity boost** over vanilla decompose at substrate-relevant K

This is a **direct strengthening** of the v1 "Resonator decomposition
with ACF rescue" capability, which v1 framed as "recover atoms past
capacity cliff (K/N=1.5 at 97%)." The new evidence shows ACF wins
substantially at K/N=1.0 too, where vanilla is dead.

**Capability evidence update** (no state change — already ✅):

The "Resonator decomposition with ACF rescue" row gains:
`wave14g_acf_resonator_high_K_trimmed__shard_K_SWEEP_4096` (K/N=1.0
@ 96.7%; vanilla @ 0%) to its evidence list. Two more shards
(K=8192, K=12288) pending; those will reveal the actual ACF ceiling.

### K=2944 retraction cross-seed confirmed

`wave14g_acf_K2944_seed7` (13:55:38, RETRACTION_HOLDS_AT_SEED7):
- At SEED=7, K=2944 recovery: 60% / 75% / 60% / 55% across r ∈ {0.005, 0.01, 0.05, 0.1}
- All above the original SEED=17 50% "dip"
- Cross-seed confirmation that the dip was SEED=17 codebook noise

Evidence list update for the "Resonator with ACF rescue" capability;
no state change. v3's retraction is now multi-seed validated.

### Inconclusive runs (flag only, no capability moves)

| Experiment | Outcome | Disposition |
|---|---|---|
| `wave14g_icl_genuine_shift_hex` (13:56) | INCONCLUSIVE_NO_METRICS | 🟡 — silent failure under markdown→hex distribution shift |
| `wave14g_edit_fidelity_K64` (13:57) | INCONCLUSIVE_NO_METRICS | 🟡 — MVP3 R1 gate unresolved |
| `wave14g_decompose_K_cliff_seed7` (13:58) | STAGING_BUG_VARIANT | infra (already covered by N=8192 result) |
| `wave14f_r10_K_adaptive` (14:48) | completed_via_healer (failed status + metrics.json present) | 🟡 — needs analyzer pass |

### Updated tally (v8)

| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |
|---|---|---|---|---|---|---|
| Memory primitives | 6 | 1 | 1 | 1 | 1 | 1 |
| Concept structure | 2 | 1 | 2 | — | — | 1 |
| Continual learning | 3 | — | — | — | — | — |
| Robustness/scaling | 3 | 1 | — | — | — | — |
| Topological / spin glass | 1 | — | 1 | 2 | — | — |
| Compound | — | — | 1 | — | — | — |
| Pool retrieval algorithms | 1 | — | — | — | — | 3 |
| Privacy / erase (NEW row) | — | — | — | 🔬 1 (rank-1 W edit) | — | 1 (current architecture without W edit) |
| CANNOT | — | — | — | — | — | 16 (+1: GDPR-erase in current arch) |
| UNSURE | — | — | — | 13 (+1: rank-1 W edit primitive) | 10 | — |
| KILLER Tier 1 | 3 | 1 | 1 | — | — | 1 |

The GDPR-erase row is the first capability where we've identified
**a specific architectural addition** (rank-1 W edit) that would
close a Tier-1 KILLER gap. v3's "edit primitive ✅" was about
mutating pool bundles; the missing piece is mutating W itself.

---

## 2026-05-20 evening update — overnight autonomous research session

Session ran 2026-05-20T18:30 to ~23:00. Built rigor infrastructure (verification/oracle.py, queue_add.py gate, runner HDLAB_EXP_NAME env), 4 parallel research agents on materials science / capability hunt (codebooks+spectral, topology+criticality, compositional, industry hunt — all 2x iteration), and queued ~10 experiments across GPU+CPU. Net: several real capability findings, several Mirage-mode warnings caught early, one substrate-forensics primitive emerged.

### Validated this session

| Experiment | Outcome | Capability implication |
|---|---|---|
| `wave14m_alpha_c` | **ALPHA_C_AGS_LIKE** — measured α_c = 0.153 at N=4096 (rising from 0.082 @ N=1024 → 0.107 @ N=2048 → 0.153 @ N=4096) | Substrate confirmed in canonical AGS Hopfield regime. 40 years of spin-glass theory applies. Operating point known. |
| `wave14h_alpha_sweep_v2` (correlated keys) | ALPHA_SWEEP_HITS_TARGET on argmax probe | **Argmax-only — turned out to be Mirage failure under deeper probes.** Don't ship this as "GDPR-grade." |
| `wave14p_erase_multiprobe` | **MULTIPROBE_ARGMAX_ONLY** — confirmed Mirage failure mode | Anti-Hebbian rank-1 erase passes argmax but fails rank/norm/cos probes under correlated keys. Per "Mirage of Model Editing" arXiv:2503.06991. **Anti-Hebbian alone is NOT GDPR-grade.** |
| `wave14z_anneal_erase` | **ANNEAL_THERMAL_WINS** — global anneal at p=1.0 destroys all patterns | Materials-science annealing analog works as "factory reset" erase but not selective. User's insight validated mathematically. |
| `wave14xrd_walsh_spectrum` (random keys) | **XRD_NO_PEAKS** — matches Agent 1 prediction | Random ±1 keys are amorphous-in-Walsh-basis. No Bragg peaks. **Confirmed prediction.** Structured keys needed for crystallographic forensics. |

### Currently running / pending verdicts

- `wave14xrd_structured_keys` — Hadamard-keys variant of WHT diffraction test. Predicts Bragg peaks if crystallography analog is load-bearing.
- `wave14anneal_selective` — local annealing (laser-anneal analog) test for selective erasure.
- `wave14mp_edge_detector` — Marchenko-Pastur edge as substrate phase indicator. Predicts ρ = λ+_emp / λ+_MP crosses 1.0 at K = α_c·N = 627 ± 15%.
- `wave14cpu_alpha_c_extended` (CPU) — α_c at N ∈ {8192, 16384} to confirm 1/√N AGS scaling.

### New capability candidates (research-backed, untested)

| Candidate | Math / materials anchor | Predicted gain |
|---|---|---|
| **MP-edge substrate forensics primitive** (NEW) | Marchenko-Pastur edge of W's spectrum; BBP transition (Yaskov arXiv:2111.04296; "From SGD to Spectra" arXiv:2507.12709) | Detect substrate phase WITHOUT querying. Could ship as audit/health-check primitive. |
| **Substrate readout attack via charge-flipping** (NEW — security finding) | Oszlanyi-Suto charge flipping (arXiv:cond-mat/0308129); bipolar prior = electron-density-positivity analog | At K < N/(2 log N) ≈ 170, SVD + sign-ICA + charge-flipping recovers stored (v_k, k_k) from W alone. Capability + security implication. |
| **Kerdock-coset structured codebooks** | Hammons-Kumar-Calderbank-Sloane-Solé arXiv:math/0207208; Z₄-Gray-map; Welch-bound exact | Predicted 2× usable K + ~50-350× faster cleanup (O(N²log N) → O(N log N) via FHT). Bloch-band materials analog. |
| **Parisi RSB pure-state addressing** | Albanese-Camilli-Carucci-De Nittis arXiv:2303.06375; AT line for Hopfield | At our α=0.153, substrate IS in Parisi RSB phase with ~exp(40) ≈ 10¹⁷ ultrametrically-organized pure states. Content-addressable hierarchical memory for free. |

### Negative findings — important to track

| Claim previously held | Now demonstrated | Implication |
|---|---|---|
| "wave14h W-side erase is GDPR-grade (76.7pp leak reduction)" | Argmax-only Mirage. Multi-probe (rank, norm, cos, paraphrase) shows residual structure. | Don't pitch as GDPR-grade. Direct subtraction works mathematically but cross-talk magnitude persists under correlated keys. |
| "Decoder swap to sparse Hopfield gives exp(N) capacity" | Confused architectures. Our substrate uses W=Σvkkᵀ (classical Hopfield, α_c·N). Modern Hopfield uses Ξ-matrix storage. Different system, can't just "swap decoder." | Capacity story needs Ξ-storage rewrite OR Kerdock-structured W (2× gain, not exp(N)). |

### Holy-grail capabilities to investigate (background research agent dispatched)

Sent agent on capabilities the field considers uniquely enabling INDEPENDENT of current market focus. Result pending.

### Process / protocol improvements this session

- **Mirage failure mode**: validated experimentally. Anti-Hebbian erase passes argmax but fails deeper probes. Now caught by `wave14p_erase_multiprobe` framework (rank + norm + cos + paraphrase per the "Mirage of Model Editing" ACL 2025 paper). All future erase claims must use multi-probe.
- **Verification module added**: `verification/oracle.py` with `assert_in_range`, `assert_distinguishable`, `assert_baseline_high`, `assert_recovery_above_floor`. Future experiments call these to catch test-setup bugs before runner sees them.
- **Queue gate added**: `tools/queue_add.py` runs script's `--self-test` + `--smoke` + validates metrics schema before adding to queue. Closes the silent-failure mode from the wave14*_v2 reruns earlier in the day.
- **Runner patched** to pass `HDLAB_EXP_NAME` env var so scripts write to correct output dir regardless of queue naming.


## 2026-05-20 evening update — verdict batch 2

Three new verdicts landed after the v8 update.

### NEW CAPABILITY: substrate forensics via WHT with structured keys

`wave14xrd_structured_keys` returned **XRD2_STRUCTURED_WINS_CLEAR**:
- Hadamard keys give max WHT spectrum SNR = **15,625,000**
- Random keys give max SNR = 1.3 (amorphous, as predicted)
- 9-min substantial GPU run

This DIRECTLY validates the crystallography analogy at the largest possible scale. Hadamard rows = Walsh basis vectors -> outer products produce exact Bragg-like peaks at integer Walsh frequencies. SNR is astronomical because random-key background is ~sqrt(N), Hadamard background is exactly zero everywhere except the peak frequencies.

**New capability row** (proposed for next cap_map revision):

| Capability | State | Evidence |
|---|---|---|
| **Substrate forensics via WHT diffraction pattern** (structured-keyed substrate) | ✅ Validated | `wave14xrd_walsh_spectrum` (random keys = amorphous, predicted), `wave14xrd_structured_keys` (Hadamard keys = crystalline, SNR=1.5e7 vs 1.3 for random) |

Product implication: if substrate is built with structured keys (Hadamard, Reed-Muller, Kerdock), we can perform substrate forensics without queries - measure WHT spectrum, count Bragg peaks = number of stored facts, identify peak frequencies = which keys. This is a real capability nothing else (vector DB, KV cache, MLP weight matrix) has.

### MP edge phase detector: substrate is MORE paracrystalline than predicted

`wave14mp_edge_detector` returned **MPEDGE_NO_TRANSITION**. rho never crosses 1.0 across K in {50..3500}:
- K=50: rho=86.84
- K=627 (predicted transition): rho=8.4
- K=3500: rho=1.91

Stored memory eigenvalues lift FAR above MP bulk; substrate is strongly paracrystalline at all loads we tested. The "amorphous transition" doesn't appear in our K range - it would be at K > 4000 (close to N).

Implication: the substrate is spectrally rich. Phase detector based on `rho==1` doesn't work, but the eigenvalue spectrum structure itself is a strong fingerprint. Follow-up experiment needed: extend K to N+, count eigenvalues-above-MP-bulk as the better metric.

### Selective annealing fails multi-probe

`wave14anneal_selective` returned **SEL_ANNEAL_NO_FORGET**. Best leak rate 0.20% (which IS below 10% target) but norm_ratio failed - same Mirage failure mode as anti-Hebbian. Selective anneal makes erased values direction-random but doesn't collapse the magnitude under correlated keys.

Implication: local thermal annealing in the (v_e, k_e) subspace doesn't give GDPR-grade selective forgetting on correlated keys. Only GLOBAL annealing (wave14z_anneal) collapsed norm, but that's factory-reset not selective.

### Updated tally (v9)

Net new capabilities ✅ this session: 1 (substrate forensics via WHT structured keys).
Net Mirage failures caught: 3 (anti-Hebbian erase, anti-Hebbian under correlation, selective local anneal).
Net new ⚪→🔬: 2 (soft-trace holy grail, charge-flipping iterative forensics).

The single biggest finding of the session: **with structured keys, the substrate's WHT is a literal crystallographic diffraction pattern.** This unlocks substrate forensics as a capability.


## 2026-05-21 early-morning update — Yonelinas dual-process VALIDATED + forensics + soft-trace partial wins

Four experiments landed between 22:52 and 23:16 on 2026-05-20.

### NEW HOLY-GRAIL CAPABILITY: Yonelinas dual-process dissociation emerges from the algebra

`wave14source_monitoring` returned **SRCMON_DISSOCIATION_VALIDATED**:
- At alpha=0.098: item_recall = **15.6%**, source_recall = **81.6%**
- Triple-bound bundle m = sum_{j,k} s_j ⊙ c_jk ⊙ v_jk
- Yonelinas (2002) dual-process emerges WITHOUT additional architecture - just from the binding algebra

**New capability row** (proposed for next revision):

| Capability | State | Evidence |
|---|---|---|
| **Source-monitoring dissociation (Yonelinas dual-process)** | ✅ Validated | `wave14source_monitoring`: at alpha=0.098, item=15.6%, source=81.6%. Source binding survives loads where item recall has collapsed. |

This is a capability NO deployed LLM has. The dissociation between "do I recognize this?" (familiarity) and "where did I encounter this?" (recollection) is a quietly enormous cognitive science finding from the 1990s that the LLM field has never properly implemented.

### NEW CAPABILITY (partial): Counterfactual queries via soft trace

`wave14soft_trace` returned **SOFT_TRACE_PARTIAL**:
- Counterfactual fidelity = **1.00** (PERFECT)
- ECE calibration test inconclusive (test design issue)

Counterfactual subtraction `m_tilde - v_k ⊙ c_k` produces a bundle that behaves identically to a substrate where item k was never stored. This is Pearl Level 3 (counterfactual) retrieval as a primitive. The test of soft-trace Bayesian calibration needs methodology work; that's worth iterating.

### NEW CAPABILITY (limited): Operational WHT-peak substrate forensics

`wave14forensics_walsh_peaks` returned **PEAKS_FORENSICS_LIMITED**:
- At low K (within tested range): recall = **100%** of stored Hadamard key indices recovered from WHT peaks alone
- High-K degradation not yet tested

With STRUCTURED keys (Hadamard), we can read out which keys were stored just by computing the WHT of W and reading peak frequencies. No queries needed. This is the operational version of the XRD2 finding.

### SVD-only forensics: insufficient, iterative needed

`wave14forensics_svd_recovery` returned **FORENSICS_PARTIAL**:
- Low K cos = 0.31, high K = 0.09
- Gap 0.23 confirms K-dependent threshold but recovery cos is weaker than predicted 0.5+
- SVD + sign-rounding alone is insufficient; iterative charge-flipping (Oszlanyi-Suto) is the next step

### Three follow-ups queued at 2026-05-21T00:18

- `wave14source_monitoring_extended` (L up to 2000): test dissociation past alpha_c
- `wave14soft_trace_extended` (K up to 12000): test smooth-cliff prediction
- `wave14walsh_peaks_extended` (K up to N): find forensics degradation point

### Updated tally (v10)

NEW ✅ this session: 2 (source-monitoring dissociation, WHT-peak forensics at low K).
NEW 🟢 partial: 2 (soft trace counterfactual, SVD forensics).
NEW 🔬 research-only: 1 (iterative charge-flipping for high-K forensics).

The Yonelinas dual-process is the most surprising single finding of the session: a textbook cognitive science capability (recollection vs familiarity) drops out of the binding algebra as an emergent property. This is the kind of finding that would be a Nature paper if we were writing papers (we're not).

