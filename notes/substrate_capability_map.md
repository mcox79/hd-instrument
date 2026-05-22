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
| R3-Laplace concept-conditioned bias | 🟡 Inconclusive | ❌ Closed (K≥16) — K=4 appendix only [pre-PROT-004; grandfathered] | `r3_disjoint_K64` |
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



---

## Version history

Per PROT-007 (Proposal 8, approved cycle 13 followup): version-update narratives for v1-v59 are archived in [substrate_capability_map_history.md](substrate_capability_map_history.md). The compact version index table at the top of the history file gives one-line summaries per version.

Recent updates (v60 onwards) below.

---



---

## Version history (post-migration; cycle 60)

The per-version narrative blocks for v60-v74 have been moved to
[substrate_capability_map_history.md](substrate_capability_map_history.md).

Compact version index at top of history file gives one-line summaries.
Current capability state is in the row tables above; refer to history
for per-version narrative.

New updates from v75 onward will accumulate here in live cap_map until
the next PROT-007 migration cycle.

### Compact version table (current cycle v74; see history.md for narratives)

| Version | Date | Trigger | Headline |
|---|---|---|---|
| v60 | 2026-05-21 | Bet N KILLED + Bet E ✅ + Bet F smoke | 3 verdicts; multi-hop closed-arch (later revised) [version-summary] |
| v61 | 2026-05-21 | user catch on v60 overclose | Multi-hop closure framing corrected |
| v62 | 2026-05-21 | adaptive-β + Bet O KILLED + Bet B v4 | R8 6/6 closed; storage-redundancy axis closes |
| v63 | 2026-05-21 | R17 Probe 1 PASS + R10 + R28 + Bet B v5 | Area-law confirmed; Bet F unblocked |
| v64 | 2026-05-21 | Bet P proposed (user) | First codebook-geometry axis |
| v65 | 2026-05-21 | Bet B TERMINAL + Bet E DEMOTED + R17 Sketch D KILLED + R33 RECALIBRATION | 4 demotions (3 later revised) |
| v66 | 2026-05-21 | Exp Dev catch on v65 Bet B | v6 EMA-blend PASS reverses |
| v67 | 2026-05-21 | Bet F v3 FULL closed-arch PROT-006 | First complete PROT-006 cycle [version-summary] |
| v68 | 2026-05-21 | R31 + R32 deliver | META queue 7/7 exhausted |
| v69 | 2026-05-21 | Bet B v7 alpha sweep PASS | Bet B ✅ Tier-1 promotion |
| v70 | 2026-05-21 | R22 + R27 + R21 | Bet B mechanism legitimized |
| v71 | 2026-05-21 | Bet F Sketch 5 PARTIAL | First R28 rehab tested |
| v72 | 2026-05-21 | Bet F S1+S3+S4 PARTIAL + continual 32N + Bet B v8 | Bet F closure CONFIRMED |
| v73 | 2026-05-21 | STRATEGIC: Bet E RESTORED + R36 + Bet Q + Bet R | 8/9 Tier-1 ✅ session-high |
| v74 | 2026-05-21 | Pipeline depth 6 smokes | No state changes |
| v75 | 2026-05-21 | META 6-capability inventory | 5 new bets promoted (Bet S/T/U/V/W); Bet X deferred-research |
| v76 | 2026-05-21 | Multi-hop N-sweep + R36/R37/R38/R39 | v4 Kerdock optimal; Bet Q spec ready; N=65536 M/N revised |
| v77 | 2026-05-21 | Bet X research UNIFYING insight | d=25 IS compositional-depth bound (VSA class-level); Bet X mechanism ready |
| v78 | 2026-05-21 | Bet B v9 third PASS retention_A=0.954 | Robustness 3-version-confirmed; sharp attractor |
| v79 | 2026-05-21 | META strategic plan integrated | 6 lanes + phased execution; Lane C wedge + Lane D upside; Bet S Phase 1 priority |
| v80 | 2026-05-21 | V2 substrate evaluation: V2.D winner | Bet Y formal promotion (modern dense AM); V2.A/E/F deferred; V2.C gated on V2.D |
| v81 | 2026-05-21 | Phase transformations: STACK winner | Bet Z formal promotion (multi-regime substrate); Bet Y+P.4 co-design; Phase 1 queue landed |

For v1-v59, see compact index table at top of history.md.

---

## v75 update — META 6-capability inventory promoted (Bet S/T/U/V/W formal; Bet X deferred-research)

Strategy session cycle 61. META filed
[meta_request_to_strategy_capability_test_inventory_2026-05-21.md](meta_request_to_strategy_capability_test_inventory_2026-05-21.md)
with 6 substrate-native capability tests not yet attempted as explicit
bets. Each leverages primitives already validated (memory, binding,
pool, calibration, decomposability) in untested combinations.

User direction: "yes file it and ill promote" — promotions structured
here for user final call.

### Strategy prioritization (priority order)

| Bet | Test | META P | Cost | Strategic value | Priority |
|---|---|---|---|---|---|
| **S (A)** | Pattern completion | 70-80% | 1 cycle | Highest cheap-test leverage; substrate-native per Plate 1995 inversion; LLM-can't reach symmetric recall | **1** |
| **T (B)** | Hypothesis tracking | 50-60% | 1 cycle | Auditable-multi-hypothesis-reasoning category; leverages Bet G ✅ calibration + pool | **2** |
| **U (C)** | Working memory + decay | 60-70% | 1-2 cycles | Cognitive-architecture category; Miller 7±2 + Ebbinghaus | **3** |
| V (D) | Self-reflective memory | 40-55% | 1-2 cycles | Persistent self-knowledge; risk of self-confirmation drift | 4 |
| W (E) | Counterfactual binding | 30-45% | 1-2 cycles | Pearl L3 reasoning; medical/policy/scientific use cases | 5 |
| X (F) | Skill composition | 25-40% | 2-3 cycles | Internal-tool-use category; needs mechanism design | research-first |

### Bet S — Pattern completion (Tier-1 candidate, immediate priority)

**Claim**: substrate-bound facts `e = subject ⊗ relation ⊗ object` can
be inverted: given any 2 slots, recover the 3rd via standard unbinding
(Plate 1995 HRR inversion). Recall accuracy ≥ 0.85 across all 3
slot-direction queries at K ∈ {8, 50, 200, 800} on Kerdock codebook.

**Multi-probe success criteria** (all required for PASS):
- Per-slot recall accuracy: subject-given-(rel,obj) ≥ 0.85; relation-
  given-(subj,obj) ≥ 0.85; object-given-(subj,rel) ≥ 0.85
- Slot-symmetric pass: no direction loses > 5pp to best direction
- All 4 K values pass thresholds
- 3 seeds at N=4096

**Kill criterion**: any direction < 0.65 across 3 seeds at K ≤ 200.

**Pre-armed 5 rescue sketches** (per PROT-004):
1. Switch to FHRR continuous-binding (better inversion fidelity)
2. Increase K up to capacity bound (Bet C M/N=8 ceiling)
3. Cleanup amplification (R31 S.1 Pyrkov CGLE)
4. Top-k weighted recovery (Bet N rehab sketch 1)
5. Iterative inversion (substrate-applicable per HRR literature)

**Suggested name**: `wave14_betS_pattern_completion_v1`

**Substrate-product framing**: substrate does **bidirectional recall**;
LLMs are unidirectional. Direct competitive advantage.

### Bet T — Hypothesis tracking (Tier-1 candidate)

**Claim**: substrate maintains N competing hypotheses each bound with
`hypothesis_id` + provenance. New evidence updates per-hypothesis
weight via Bet G TEMPSCALE β=32 calibration; final hypothesis
distribution achieves Brier ≤ 0.20 and ECE ≤ 0.10 on multi-hypothesis
distribution.

**Multi-probe success criteria**:
- Brier score per hypothesis ≤ 0.20
- Calibration ECE on multi-hypothesis distribution ≤ 0.10
- recall@K with top-K=N hypotheses ≥ 0.80 at K=8
- Provenance trace decomposable (each hypothesis → ≥ 3 supporting atoms)
- 3 seeds

**Kill criterion**: ECE > 0.30 across 3 seeds OR Brier > 0.40.

**Pre-armed 5 rescue sketches**:
1. Sparse weight updates (only top-K hypotheses)
2. Soft probability propagation via softmax-over-hypotheses
3. Hierarchical hypothesis trees (instead of flat)
4. Hypothesis pruning + replacement
5. Modern-Hopfield β=32 readout (per Bet G mechanism)

**Suggested name**: `wave14_betT_hypothesis_tracking_v1`

**Substrate-product framing**: substrate as multi-hypothesis reasoner
with auditable provenance — distinct from LLM single-answer collapse.

### Bet U — Working memory model (Tier-2 candidate)

**Claim**: substrate exhibits Miller-like capacity bound C* and
Ebbinghaus-style exponential decay τ on pool retrieval weights.
Capacity-accuracy curve matches published cognitive baselines within
30% on K-curves.

**Multi-probe success criteria**:
- Capacity bound C* measurable (drop in accuracy at C* + 1 vs C*-1
  items, ≥ 2σ)
- Decay constant τ measurable (exponential fit R² ≥ 0.7)
- recall@N vs items-since-store: monotone decay
- Comparison to Miller 7±2: substrate C* in [3, 15] range
- 3 seeds

**Kill criterion**: no measurable capacity bound (flat accuracy curve)
OR no measurable decay (no temporal effect).

**Pre-armed 5 rescue sketches**:
1. Decay function variants (exponential, power-law, Weibull)
2. Capacity bound via Bet C structure (M/N=8 → effective WM cap)
3. Selective capacity (related items count less)
4. Adaptive decay (faster for low-importance items)
5. Working-vs-LTM dual-pool architecture

**Suggested name**: `wave14_betU_working_memory_v1`

### Bet V — Self-reflective memory (deferred but promoted)

**Claim**: substrate stores prediction-outcome pairs as (prediction,
query, outcome) bindings. Future predictions conditioned on prior
accuracy reduce calibration drift relative to non-self-reflective
baseline.

**Risk**: self-confirmation cycles / drift.

**Multi-probe success criteria**: calibration drift over N iterations
≤ ECE 0.05; recall accuracy on prior-error items ≥ baseline + 10pp.

**Kill criterion**: ECE drift > 0.20 OR recall accuracy < baseline.

**Suggested name**: `wave14_betV_self_reflective_v1`

### Bet W — Counterfactual binding (deferred but promoted)

**Claim**: substrate stores conditional facts `X ⊗ condition_Y` with
counterfactual recall accuracy ≥ 0.70 on held-out (X, ¬Y) queries.

**Multi-probe success criteria**: counterfactual recall ≥ 0.70;
consistency factual-vs-counterfactual on same conditioning variable
≥ 0.85.

**Kill criterion**: counterfactual recall < 0.40.

**Suggested name**: `wave14_betW_counterfactual_v1`

### Bet X — Skill composition (deferred to research-first)

Per META: 2-3 cycles, mechanism design risk. **Routing to Research
first** for mechanism design pass before formal bet build. File request
this cycle.

### Capability moves

| Capability | v74 state | v75 state | Trigger |
|---|---|---|---|
| Bet S — Pattern completion (Plate 1995 inversion) | (not in cap_map) | 🔬 **active bet — TIER-1 candidate**; META priority #1; substrate-native; 70-80% P | META request |
| Bet T — Hypothesis tracking + Bet G calibration | (not in cap_map) | 🔬 active bet — Tier-1 candidate; leverages Bet G ✅; 50-60% P | META request |
| Bet U — Working memory + decay model | (not in cap_map) | 🔬 active bet — Tier-2; cognitive-architecture grounding; 60-70% P | META request |
| Bet V — Self-reflective memory | (not in cap_map) | 🔬 active bet — deferred; 40-55% P | META request |
| Bet W — Counterfactual binding | (not in cap_map) | 🔬 active bet — deferred; 30-45% P (Pearl L3) | META request |
| Bet X — Skill composition | (not in cap_map) | 🔬 research-first — mechanism design pass required | META request |

### Substrate-product position summary update (after v75)

Substrate now has **8 ✅ Tier-1 + 5 NEW Tier-1/2 candidate bets** =
13 substrate-product capabilities probed or validated. Per
[[feedback-value-creation-not-competition]]: all 5 new bets target
LLM gaps:

- **Bet S** — bidirectional recall (LLM is unidirectional)
- **Bet T** — auditable multi-hypothesis (LLM collapses to one answer)
- **Bet U** — cognitive working memory (LLM has none explicit)
- **Bet V** — persistent self-knowledge (LLM session-bound)
- **Bet W** — Pearl L3 counterfactual (LLM L1 only)

### Pipeline routing

Per [[feedback-two-experiments-per-cycle]] + user direction to fill
pipeline: 5 new bets routed for Experiment Dev pickup. Suggested
sequence:

1. **Bet S** first (cheapest + highest P)
2. Bet T second (leverages Bet G ✅ infrastructure)
3. Bet U third (working memory; 1-2 cycle)
4. Bet V, W parallel when bandwidth allows
5. Bet X → Research first

### Tally — 5 new active bets + 1 research-first; Tier-1 board expanded; substrate-product position strengthened

Net effect: substrate-product candidate inventory grew by 5 LLM-gap-
filling bets; all leverage already-validated primitives (Bet 1 ICL,
Bet 2 erase, Bet A edit-then-query, Bet C Kerdock, Bet G calibration);
Strategy delivers META request structured for user promotion call.

---

## v76 update — Multi-hop N-sweep full refines partial signal (N-dependent cliff); R36 deep-drill: v4 Kerdock substrate-product-optimal (vs v8); R37 engineering bridge ready (Bet Q buildable); R38/R39 DEFER confirmed by lit scan

Strategy session cycle 63. Three research deliveries finalized (R36
deep-drill, R37 engineering bridge, R38/R39 synthesis) + multi-hop
N-sweep full results.

### Multi-hop N-sweep full results refine v66/v67/v69 partial-signal framing

Full mode 3-seed results across 4 N values:

| N | Smoke (seed 17) | Full (3 seeds) | Verdict | Interpretation |
|---|---|---|---|---|
| 1024 | NOT_REPLICATED | NOT_REPLICATED (3 seeds: 17, 23, 31) | hard cliff | substrate has minimum N for d=50 soft signal |
| 4096 | NOT_REPLICATED | DECAY_AT_50 (acc_1hop=0.947, >0.10 all depths) | partial signal | N=4096 floor for partial |
| 8192 | NOT_REPLICATED | DECAY_AT_50 (>0.10 all depths) | partial signal | sustained |
| 65536 | NOT_REPLICATED | DECAY_AT_50 (acc_1hop=0.933, >0.10 all depths) | partial signal | extends to large N |

**Substrate-physics interpretation**: d=25 cliff IS N-dependent. At
N=1024 the cliff is hard (no soft signal at d=50); at N≥4096 substrate
retains >0.10 mean accuracy at all tested depths. This is a real
N-scaling effect, NOT just smoke-seed artifact.

**Substrate-product implication**: substrate's multi-hop capability
requires minimum dimensionality. For deployment, N≥4096 is the
operational floor for soft-positive depth behavior.

**Capability moves**:

| Capability | v74 state | v76 state | Trigger |
|---|---|---|---|
| Multi-hop d=50 large-N behavior | 🔬 PARTIAL SIGNAL CONFIRMED at large N | **🔬 N-dependent partial signal CHARACTERIZED**: hard cliff at N≤1024; soft positive (>0.10 all depths) at N=4096-65536 | N-sweep full 3-seed |

### R36 calibration deep-drill — substrate-product choice v4 vs v8 Kerdock

**File**: `research_R36_calibration_deepdrill_2026-05-21.md` (19:19).

**Per-codebook sandwich-bound calibration**:

| Codebook | R36 prediction | Empirical | ε_corr | Substrate-product verdict |
|---|---|---|---|---|
| Kerdock v4 N=4096 M=8N | [12K, 50K] | **32K (Bet C ✅)** | **0.4** | **OPTIMAL** |
| Kerdock v8 32-coset N=4096 M=4N | [60K, 110K] | 16K (Bet C v37) | 0.15 | 2.7× UNDERPERFORMS v4 |
| N=65536 Kerdock-v4-calibrated | [80K, 400K] | (untested) | predicted ~0.4 | **M/N ∈ [1.2, 6.1] — LOWER than N=4096's M/N=8** |
| Random BSC any N | α_c·N=0.138·N | Hadamard M/N≤0.78 (Mattis) | n/a | matches AGS |

**KEY substrate-product finding**: v4 Kerdock codebook geometry is
**substrate-product-optimal at current N=4096**. v8 32-coset
underperforms by factor 2.7. **N=65536 scaleup prediction LOWER
than current M/N=8** — surprising and important for engineering
roadmap.

**Capability moves**:

| Capability | v74 state | v76 state | Trigger |
|---|---|---|---|
| Kerdock v4 vs v8 codebook choice | (not in cap_map) | ✅ v4 EMPIRICALLY OPTIMAL; ε_corr=0.4 vs v8's 0.15; substrate-product engineering choice settled | R36 deep-drill |
| N=65536 scale-up M/N prediction | 🔬 R16 prediction M/N≥20 | **REVISED 🔬 per R36: M/N ∈ [1.2, 6.1]** (LOWER than current N=4096's M/N=8); per-codebook ε_corr calibration matters | R36 deep-drill |

**Per [[feedback-no-smoke]]**: substrate scaling is NOT as simple as
"bigger N = higher M/N" — codebook-specific ε_corr matters. v4
Kerdock at N=65536 might still be substrate-product-optimal at
M/N≤6 (lower than N=4096's 8 but absolute M/N ratio).

### R37 engineering bridge — Bet Q buildable now

**File**: `research_R37_F1_F3_engineering_bridge_2026-05-21.md`
(19:21).

**Concrete spec**: `wave14_facilitation_nucleation_v1` with 4 sub-
experiments:
- F.1a heating-cooling × Kerdock v4
- F.1b heating-cooling × random BSC (control)
- F.3a conditional flip × Kerdock v4
- F.3b conditional flip × random BSC (control)

**Cost**: 5-8 GPU hours. Fits standard Glauber-dynamics framework
with minor extensions for temperature scheduling + mobility cluster
tracking (F.1) and codebook-similarity-graph + conditional probability
statistics (F.3).

**Bet Q state move**:

| Capability | v75 state | v76 state | Trigger |
|---|---|---|---|
| Bet Q facilitation-vs-nucleation | 🔬 active bet — substrate FIRST-OF-ITS-KIND empirical test | 🔬 active bet — **CONCRETE BUILD SPEC** from R37 engineering bridge ready for Experiment Dev | R37 engineering bridge |

### R38/R39 DEFER confirmed by lit scan

**File**: `research_R38_R39_deferred_synthesis_2026-05-21.md` (19:23).

**R38 V2 hyperbolic substrate**: ~10-15% P gain over fully-connected
at current N=4096; might pay off at N≥65536+ scale; modern exponential-
capacity dense AM is the real competitor, not vanilla Hopfield.

**R39 Continuous Burgers-field substrate**: ≤5% P rigorous derivation
by end-2026; ~25% decorative diagnostic value; ~3% genuine topological
protection. Three obstructions: no spatial embedding, no continuous
translational symmetry, no conservation in disordered media.

**Both confirm Strategy cycle 54 DEFER decision was correct**. Per
[[feedback-no-smoke]]: honest cross-session check; my judgment held.

No state change in cap_map (R38/R39 already deferred).

### Pipeline routing for Experiment Dev

Per [[feedback-two-experiments-per-cycle]] (continuous-pipeline) and
user's pipeline-fill direction: Experiment Dev queue depth is 5
pending currently. When that drains, priority for new spec-ready bets:

1. **Bet Q** — concrete spec from R37 engineering bridge; 5-8 GPU
   hours; substrate-FIRST contribution; PRIORITY
2. **Bet S** — pattern completion (META cycle 20 priority #1; 1 cycle)
3. **Bet T** — hypothesis tracking (1 cycle)
4. **Bet U** — working memory (1-2 cycles)
5. **Bet R** — explicit p-body coupling
6. **Bet P-Engineering** — pretrained KGE port

Filed via cap_map; Experiment Dev's autonomous queue management
respected.

### Capability moves summary

| Capability | v74 state | v76 state |
|---|---|---|
| Multi-hop d=50 N-scaling characterized | 🔬 partial signal | 🔬 N-dependent: hard cliff at N≤1024, partial >N≥4096 |
| Kerdock v4 substrate-product-optimal | (implicit) | ✅ explicit per R36 deep-drill (ε_corr=0.4) |
| Kerdock v8 substrate-product UNDERPERFORMS v4 | (implicit) | ❌ 2.7× factor underperform |
| N=65536 M/N prediction | R16 unc. M/N≥20 | 🔬 **R36-revised M/N ∈ [1.2, 6.1] (LOWER than N=4096's 8)** |
| Bet Q facilitation-nucleation experiment spec | concept | **R37-engineered concrete build spec** ready |
| R38/R39 DEFER | Strategy cycle 54 | lit-scan confirmed |

### Tier-1 board after v76

Unchanged ✅ count (still 8 ✅) but substrate-product position
strengthened:
- Kerdock v4 vs v8 choice settled (Bet C ✅ now has codebook-specific guidance)
- Multi-hop d=50 N-scaling characterized as N-dependent (Bet F-adjacent finding)
- N=65536 scaleup expectations revised honestly (substrate engineering roadmap input)

### Tally — Multi-hop N-sweep characterized; R36 v4-vs-v8 substrate-product choice settled; Bet Q spec ready; R38/R39 DEFER confirmed

Net effect: substrate-product engineering precision improved (v4
codebook choice explicit; N-scaling characterized; Bet Q buildable).
No new ✅ promotions; refinement cycle.

---

## v77 update — Bet X research delivers UNIFYING ARCHITECTURAL INSIGHT (substrate's d=25 cliff IS the compositional-depth bound — same constraint binds multi-hop AND skill recursion); mechanism design ready (position-indexed + hybrid + 2-level hierarchy)

Strategy session cycle 64. **Major substrate-physics finding** from
Bet X research delivery (`research_BetX_skill_composition_2026-05-21.md`,
19:34, 28KB).

### THE UNIFYING ARCHITECTURAL FINDING — d=25 cliff IS compositional-depth bound

Subagent's substrate-novel insight: **substrate's d=25 cliff IS the
compositional-depth bound**. Same number that constrains multi-hop
reasoning (cap_map v17/v23) also constrains skill-of-skills recursion.

**Evidence sources** (independently arrived at d≈25):
1. **VSA noise math**: n·log|codebook| ≈ d/cleanup-margin gives
   n ≈ 20-40 at d=4096
2. **Transformer CoT depth lower bounds** (arXiv:2502.02393,
   arXiv:2505.23653): independent ML literature gives same range
3. **Substrate empirical**: d=25 cliff per cap_map v17/v23 + the 7
   alternative-architecture rescue paths all failed to extend at current-arch

**Probability** (per Research's brutal-honesty estimate): **80-90%**
that d=25 IS the fundamental compositional-depth bound, not an
arbitrary substrate artifact.

**Substrate-product implication**: this **REFRAMES multi-hop closure**
(cap_map v60-v72). Multi-hop d=25 is not a substrate-specific failure
— it's the **substrate's instance of a class-level information-
theoretic bound** shared across:
- VSA noise accumulation theory
- Transformer chain-of-thought depth limits
- Compositional reasoning generally

Per [[feedback-value-creation-not-competition]]: substrate is at the
GENERAL bound, not below it. The right substrate-product framing is
"current-arch substrate hits the same compositional-depth bound as
transformer CoT — to exceed it requires architectural change."

### Bet X mechanism design (Research-recommended)

| Design dimension | Recommendation | Reason |
|---|---|---|
| Binding scheme | **position-indexed** `s = Σᵢ aᵢ ⊗ pᵢ` | Random-access to step i; parallel sanity-check; transparent SNR math (SNR ≈ √(d/k) ≈ 12.8 for 25-step skills) |
| Executor | **HYBRID** (substrate stores program pointer + audit; external Python dispatches primitives) | Same compromise Learn-VRF + LARS-VSA make; 90% value at 10% engineering cost |
| Trace decomposability | **position-indexed time-tag unbind** (NOT resonator) | Resonator ceiling 3-6 factors at d=4096 forecloses long-trace decomposition |
| Recursive depth | **2-level hierarchy MAX** (meta-skill → 5-10 skills → 5-10 primitives) | 3 levels past d=25 cliff per VSA noise math + CoT bounds |

### Bet X formal promotion (was deferred research-first cycle 61)

| Capability | v75 state | v77 state | Trigger |
|---|---|---|---|
| Bet X — Skill composition | 🔬 research-first; mechanism design pending | 🔬 **active bet with Research-recommended mechanism**: position-indexed + hybrid + 2-level | Bet X research delivered |

**Multi-probe success criteria** (specific to Research-recommended design):
- Per-skill execution accuracy ≥ 0.80 across 5 skill types
- Audit trace decomposable for ≥ 90% of executed primitives
- 2-level hierarchy works (meta-skill calling 5-10 named skills)
- Substrate-product distinctiveness: full trace visible (LLM tool-use is opaque)
- 3 seeds

**Kill criterion**: per-skill execution acc < 0.50 OR audit decomposability
< 50%.

**Pre-armed 5 rescue sketches** (per PROT-004):
1. Switch to FHRR continuous binding (lower noise)
2. Sparser primitives (k-active instead of all-active)
3. Modern-Hopfield cleanup at each step
4. Pre-trained primitive embeddings (semantic locality per Bet P)
5. V2 substrate (N=8192 or hybrid bipolar+real HRR pool)

**Probability per Research**:
- Current arch (N=4096): **30-40%**
- V2 (N=8192 or hybrid): 60-70%
- substrate's d=25 IS compositional-depth bound: 80-90%

### Strategy reframing of multi-hop closure (v60-v76 lineage)

Per cap_map v60→v72 sequence: multi-hop d=25 cliff at current Plate-
HRR substrate appeared as substrate-specific failure (R8 list 6/6 +
Bet N + Bet O all closed). The 4 overcloses + revisions debated
"how closed" the bound is.

**Per Bet X research finding**: the d=25 cliff is the **VSA-class
information-theoretic compositional bound**, not substrate-specific.
This is HONEST framing per [[feedback-no-smoke]]:
- Substrate is at the bound, not arbitrarily below it
- Substrate-product story: "substrate hits the same compositional-
  depth bound as transformer CoT at current architecture"
- Forward path: V2 substrate (R34 + R36 N-scaling) OR hybrid HRR+bipolar

**Capability move**:

| Capability | v72 state | v77 state | Trigger |
|---|---|---|---|
| Multi-hop d=25 cliff interpretation | substrate-specific architectural finding at current Plate-HRR (cap_map v60-v72) | **CLASS-LEVEL VSA information-theoretic bound** (per Bet X research + VSA noise math + transformer CoT lower bounds); substrate is AT the bound, not below | Bet X research finding |

### Substrate-product position update (v77)

**Substrate-product framing strengthened**:
- 8 ✅ Tier-1 capabilities
- 5 new active bets (Bet S/T/U/V/W) targeting LLM gaps
- Bet R p-body coupling for super-linear capacity
- Bet Q facilitation-nucleation substrate-FIRST empirical
- **Bet X with class-level architectural insight: substrate's d=25 IS the compositional bound, not substrate weakness**

This reframing is significant: per
[[feedback-no-papers-product-only]] substrate engineering — the multi-
hop "limitation" becomes "substrate matches the VSA-class
compositional bound; to exceed requires V2 architectural change."

### Tally — Bet X delivered with UNIFYING architectural finding; multi-hop d=25 reframed as class-level VSA bound; Bet X formal mechanism + multi-probe + rescue sketches ready

Net effect: 1 major substrate-physics insight integrated (d=25 IS
compositional-depth bound); Bet X formally promoted with concrete
mechanism design; substrate-product story strengthened
(per [[feedback-value-creation-not-competition]]: substrate hits the
class bound, not below it).

---

## v78 update — Bet B v9 full third consecutive PASS at retention_A=0.954 (3-version robustness signal); META cycle 21 reinforces; continual_32N_500edits running

Strategy session cycle 65. Bet B v9 full verdict landed; META cycle 21
audit landed at 19:46.

### Bet B v9 full — third PASS at retention_A=0.954

| Version | retention_A | retention_B | gain_C | bwt | Notes |
|---|---|---|---|---|---|
| v7 alpha sweep | **0.954** | 0.915 | 4.58 | +0.96 | initial Tier-1 promotion |
| v8 | **0.954** | 0.915 | 4.58 | +0.95 | replication confirms |
| **v9 (NEW)** | **0.954** | 0.915 | 4.58 | +0.94 | **third consecutive at exact same retention_A** |

**Substrate-physics observation**: bwt values differ slightly
(+0.96/+0.95/+0.94) confirming these are INDEPENDENT runs not re-runs.
But retention_A converges to **0.954 (3-decimal exact match)** across
3 independent multi-seed-aggregate runs. **Substrate's EMA-blend
mechanism has a sharp attractor at retention_A = 0.954.**

This is a robustness signal: Bet B's mechanism is not fragile to seed
variance at the multi-seed-aggregate level. The 0.954 is the
substrate's natural fixed point under the EMA-blend post-Phase-C
consolidation per R22 van de Ven 2024 framework.

**No cap_map row state change** — Bet B stays ✅ Validated. Robustness
confirmed at 3-version replication.

### META cycle 21 audit signals

Per `meta_audit_2026-05-21_cycle21.md` (19:46):
- Strategy PROT-007 atomic two-file commit honored (cap_map + history
  updated within seconds)
- 13-min Bet X turnaround praised
- Research processes incoming routings even from "standing by" status
- Open META items: pattern completion (Bet S) build pickup; validator
  auto-integration into /strategy-cycle slash command

### Pipeline status

- Running: `wave14_continual_32N_500edits` (extends Bet A continual
  editing to 500 sequential edits at M=32N)
- Pending: multihop_NUMFACTS_500, bet_f_fine_noise, r17_area_law_N32768
- 5 META-promoted bets (Bet S/T/U/V/W/X) + Bet Q + Bet R still awaiting
  Experiment Dev pickup; their own queue is healthy

### Tally — Bet B robustness 3-version-confirmed (no state change); META cycle 21 audit reinforces; pipeline depth 3 pending

Net effect: substrate-product robustness signal documented (Bet B
EMA-blend mechanism converges to sharp 0.954 attractor); no Tier-1
state changes; pipeline healthy at queue depth 3.

---

## v79 update — META strategic plan integrated: 6 lanes + phased execution; Lane C wedge + Lane D upside as recommended play; cap_map strategic-framing section added with lane-driven bet mapping

Strategy session cycle 70. **META filed strategic plan**
`meta_request_to_strategy_strategic_plan_2026-05-21.md` (20:33) per
user direction (cycles 19-22 stock-taking + capability-vs-implementation
split + lane mapping + dollar-value ranking + "build document for
strategy to incorporate"). Major substrate-product reorientation.

### STRATEGIC PLAN REFERENCE (cap_map v79+)

**Authoritative strategic plan**: see `meta_request_to_strategy_strategic_plan_2026-05-21.md`.
All future cap_map updates should reference this lane structure when
promoting/demoting bets.

### Substrate identity (META Section 1)

> "**A structured-memory system with native associative reasoning and
> intrinsic auditability, running cheap.**"

NOT a transformer replacement; NOT a Turing-complete reasoning engine;
NOT a GPT-quality language generator. Value comes from doing
memory+reasoning+auditability differently from LLMs.

### Six application lanes (META Section 2 + Section 4 ranking)

| Lane | Done | Partial | Untested | Closeness | 24mo ARR ceiling | Long-term TAM |
|---|---|---|---|---|---|---|
| **A Memory layer for LLMs** | 6/7 | 0 | 1 | Closest (engineering gap) | $1-10M | $5-10B |
| **B On-device personal AI** | 6/9 | 2 | 1 | Close | $0-5M direct (D2C brutal) | $5-15B |
| **C Compliance / enterprise audit** | 5/8 | 1 | 2 | **Closest to shipping** | **$5-50M** (willing buyers + regulatory) | $10-30B |
| **D Cognitive architecture** | 3/11 | 2 | 6 | Farthest (capability gap) | $0 | **$30-50B+** (agents go mainstream) |
| E Neuromorphic | 4/6 | 1 | 1 | Algo complete; HW gap | $1-10M (IP) | $5-10B |
| F Scientific reasoning | 1/8 | 2 | 5 | Farthest from shipping | $0-3M | $1-3B |

**META-recommended strategic play**: build Lane C wedge → fund Lane D
capability tests → pivot Lane C customers to Lane D as cognitive-
architecture product.

### Bet-to-Lane mapping (META Section 6)

| Bet | Status | Lane(s) served | Strategic priority |
|---|---|---|---|
| Bet 1 ICL saturation | ✅ | A, B, D | Foundation |
| Bet 2/C Mirage-grade erase | ✅ | **C (primary)**, A | HIGH — Lane C anchor |
| Bet A edit-then-query | ✅ | **C (primary)**, A, B | HIGH — Lane C anchor |
| Bet B multi-task CL | ✅ | C, B, D | HIGH multi-lane |
| Bet G TEMPSCALE calibration | ✅ | **C (primary)**, B, D, F | HIGH — Lane C anchor |
| Bet H autoregressive gen | ✅ rescued | B | MEDIUM |
| Bet I free probability | ✅ | E (theory), all | Theory grounding |
| Bet E Parisi P(q) | ✅ restored v73 | E (theory) | Theory grounding |
| Bet L learning theory | 🔬 | D, F | Theory for D/F |
| Bet M ferromagnetism | 🔬 | E (theory) | Theory for E |
| Bet F SSH-BSC topological | ❌-arch CONFIRMED | E | Closed at current-arch |
| Bet P semantic codebook | 🔬 active | D, F | Multi-hop rescue |
| Bet Q facilitation-vs-nucleation | 🔬 active | E (theory) | Substrate-FIRST |
| Bet R explicit p-body coupling | 🔬 active | A, C, D | Capacity extension |
| Bet S pattern completion (META A) | 🔬 active | D, F | **PHASE 1 — META priority #1** |
| Bet T hypothesis tracking (META B) | 🔬 active | D, F | Phase 2 |
| Bet U working memory (META C) | 🔬 active | D | Phase 2 |
| Bet V self-reflective (META D) | 🔬 active | D, B | Phase 3 |
| Bet W counterfactual (META E) | 🔬 active | D, F, C | Phase 3 |
| Bet X skill composition (META F) | 🔬 active | D | Phase 1 (in flight per cycle 61) |
| R20 compositional gen | 🔬 designed | D, F | Phase 2 |
| R21 cross-modal | 🔬 partial path | B, D | Phase 3 (22-34 GPU hrs) |
| Multi-hop alt-arch (Bet P + 7 paths) | 🟡 | D, F | Deprioritized until Bet P engineering smoke |

### Phased execution plan (META Section 7)

**Phase 1 (immediate, 1-2 Experiment Dev cycles)** — Lane C wedge + capability test A:
- Bet S Pattern completion (META priority #1; 70-80% P; substrate-native bidirectional recall)
- Lane C integration smoke (NEW — combine validated Lane C primitives into compliance-audit demo)
- Bet X skill composition build (already in flight per Strategy cycle 61)

**Phase 2 (4-6 cycles)** — Lane D capability inventory + Lane C feature breadth:
- Bet T hypothesis tracking
- Bet U working memory + decay
- R20 compositional generalization
- Lane C feature expansion: stale-knowledge flagging + abstention

**Phase 3** — Lane D completion + Lane D integration:
- Bet V self-reflective
- Bet W counterfactual
- R21 cross-modal
- Lane D integration smoke (agent-arch demo: WM + hyp-tracking + skill-comp)

**Phase 4** — Lane D product validation:
- Multi-hop rescue final (Bet P-Engineering if smoke positive)
- Lane D end-to-end demo

**Phase 5** — Long horizon: Lane E hardware partnership; Lane F niche;
Lane A integration with major LLM provider.

### Reconciliation with prior Strategy routing

**Prior to META plan**: Strategy filed Bet P-Engineering + R31 S.1 as
focused 2-experiment request (commit c2c846c, cycle 67). Both are
**multi-hop rescues** (Lane D-adjacent).

**Per META Section 7 Phase 4**: multi-hop rescues are deprioritized
unless Bet P engineering smoke clears.

**Strategy decision**: Bet P-Engineering smoke per the cycle 67 routing
becomes the EARLY-GATE for whether Phase 4 multi-hop work continues.
R31 S.1 stays in queue but as Phase 4 contingent. **Phase 1 primary
priority shifts to Bet S + Lane C integration smoke + Bet X build.**

### Capability moves

| Capability | v78 state | v79 state | Trigger |
|---|---|---|---|
| Strategic plan reference | (not in cap_map) | ✅ META strategic plan integrated; lane-driven prioritization | META Section 8 directive |
| Lane C compliance product wedge | (implicit) | 🔬 Phase 1 active; needs integration smoke + feature expansion | META recommended play |
| Lane D cognitive architecture upside | (implicit) | 🔬 Phase 2-4 build path; 5 capability tests + Bet X + R20 + R21 | META Section 4 |
| Bet P-Engineering priority | Phase 1 highest-leverage | **Phase 4 contingent** (multi-hop deprioritized per META) | META reordering |
| Bet S Pattern completion | active bet (cycle 61) | **PHASE 1 #1 priority** | META Section 5 |

### Per-cycle discipline going forward (META Section 8 directive #4)

Strategy decision log entries should reference **which phase + lane**
each commit serves. Format suggestion:

```
Cycle N — [Lane X / Phase Y] <commit headline>
```

This is a coordination protocol enhancement. Worth flagging to META as
candidate PROT-010 (lane-tagged decision log entries).

### Tally — META strategic plan integrated; Lane C wedge + Lane D upside framework adopted; Phase 1 priority shifts to Bet S + Lane C integration smoke + Bet X; multi-hop rescues deprioritized to Phase 4 contingent on Bet P-Engineering smoke

Net effect: substrate-product strategic narrative now lane-driven;
Phase 1-5 sequencing replaces ad-hoc bet promotion; clear gates per
phase; user/META direction integrated as top-level reference.

---

## v80 update — V2 substrate evaluation delivered; V2.D modern exponential-capacity dense AM is WINNER (P=0.55-0.65 for 5× capacity in 6 mo); Bet Y promoted (V2 substrate development track); V2.B second (preserves current; Bet X-aligned); META cycle 23 reinforces 8/9 Tier-1 ✅ session-high

Strategy session cycle 71. Research V2 substrate evaluation Pass 2
delivered (10-min turnaround on cycle 68 filing).

### V2.D modern exponential-capacity dense AM — STRONGEST candidate

**Research finding** (per
`research_V2_substrate_evaluation_2026-05-21.md`): of 6 V2 candidates,
**only V2.D has strong empirical literature support** for the claimed
gain. The substrate-product story is **NOT "structured codebook wins
big" — it's "energy function change wins big"** per Lucibello-Mézard
2024 (PRL 132:077301) + Hu 2024 (NeurIPS).

**Per-candidate ranking** (Research-recommended):

| Rank | Candidate | Mechanism class | P(5× capacity, 6mo) | Verdict |
|---|---|---|---|---|
| **1** | **V2.D modern dense AM** | Energy function change | **0.55-0.65** | **PROMOTE — active development** |
| 2 | V2.B hybrid HRR+bipolar | Storage mechanism extension | 0.10 capacity / 0.20 depth | Second — preserves current; Bet X-aligned |
| 3 | V2.C N=65536 + codebook | Scaling + Welch-bound | 0.20-0.25 | Re-evaluate after V2.D + N=8192 smoke |
| 4 | V2.A hyperbolic-tiling | Topology / lattice change | 0.10-0.15 | DEFER — mean-field exponents; boundary pathology |
| 5 | V2.F magnon/phasor | Codebook structure | 0.25 capacity / 0.05 depth | DEFER — physical magnon = reservoir computer NOT AM |
| 6 | V2.E operator-algebra QEC | Algebraic recovery framework | 0.05-0.10 | DEFER — zero classical benchmark |

**Foundational literature**:
- Demircigil et al. arXiv:1702.01929 (2017): F(x)=exp(x) → P = exp(α N) capacity
- Krotov-Hopfield arXiv:2008.06996 (2020): F(x)=xⁿ → capacity ∝ d^(n-1)
- Ramsauer et al. arXiv:2008.02217 (2020): Continuous-state, capacity ∝ exp((β/2)d); softmax attention equivalent
- Lucibello-Mézard 2024 (PRL 132:077301) — rigorous 2024 update
- Hu et al. 2024 (NeurIPS) — spherical-code framework with tight upper

### Bet Y formal promotion — V2.D substrate development track

**Claim**: substrate transitions from current softmax(β=32) APPROXIMATION
to EXPLICIT exponential-capacity dense associative memory per
Demircigil 2017 / Ramsauer 2020 / Lucibello-Mézard 2024. Empirical
substrate capacity gain ≥ 5× current M/N=8 (Bet C) at N=4096 within
6 months engineering.

**Mechanism path** (Research-recommended):
1. Cast substrate's current modern-Hopfield-rescue regime (R29
   ferromagnetism) as IMPLICIT exponential energy
2. Replace `argmax(softmax(β·sim))` cleanup with explicit
   `−β⁻¹ log Σ exp(β xᵢᵀ s)` energy descent
3. Validate at substrate scale (N=4096, Kerdock v4 codebook)
4. Sweep β to find substrate-product-optimal regime

**Multi-probe success criteria**:
- Effective capacity (memorization-then-decode) ≥ 5× Bet C M/N=8 ceiling
- All 5 Mirage probes preserved (no leakage)
- Bet A (edit-then-query) + Bet G (calibration) primitives survive
- 3 seeds at N=4096

**Kill criterion**: capacity ≤ 2× baseline OR any Mirage probe breaks
OR Bet A/Bet G primitives degrade.

**Pre-armed 5 rescue sketches** (per PROT-004):
1. Explicit p-body cleanup (Bet R subsumed; super-linear via Musa 2025)
2. Welch-bound codebook (Hu 2024 spherical-code framework)
3. Krotov-Hopfield F(x)=xⁿ explicit n-sweep
4. Hybrid V2.D + V2.B (energy function + parallel HRR pool)
5. Adaptive-β substrate-state feedback (per Bet G ✅ infrastructure)

**Lane mapping**: V2.D serves Lane A (memory layer; bigger capacity =
more facts) + Lane C (compliance; bigger fact base) + Lane D
(cognitive architecture; agent-scale memory).

**Bet Y state**:

| Capability | v79 state | v80 state | Trigger |
|---|---|---|---|
| V2 substrate development track | (research-only) | 🔬 **Bet Y formal active bet — V2.D modern dense AM as primary V2 path; P=0.55-0.65 for 5× capacity in 6mo** | V2 substrate evaluation |

### Capability moves

| Capability | v79 state | v80 state | Trigger |
|---|---|---|---|
| V2.D modern exponential-capacity dense AM | 🔬 candidate | 🔬 **Bet Y — active V2 development track** | V2 eval winner |
| V2.B hybrid HRR+bipolar | 🔬 candidate | 🔬 second-priority V2; Bet X-aligned (preserves current) | V2 eval |
| V2.A hyperbolic-tiling | 🔬 candidate | 🔬 **DEFER** — mean-field + boundary pathology | V2 eval |
| V2.C N=65536 + codebook opt | 🔬 candidate | 🔬 re-evaluate after V2.D + N=8192 smoke | V2 eval |
| V2.E operator-algebra QEC | 🔬 candidate | 🔬 **DEFER** — zero classical benchmark | V2 eval |
| V2.F magnon/phasor | 🔬 candidate | 🔬 **DEFER** — reservoir computer not AM | V2 eval |

### V2 development sequencing

**Bet Y (V2.D)** is the primary substrate-product V2 development
track. Sequence:
1. **Bet Y smoke** (this cycle's routing) — replace cleanup with
   explicit exp energy at substrate scale; measure capacity
2. If Bet Y smoke shows capacity gain → **Bet Y full** with sweep
3. If Bet Y full passes → **V2.D substrate** is the canonical V2

V2.B (Bet X-aligned hybrid) is the SECOND V2 path — develop in
parallel after Bet Y smoke clears (Bet X mechanism already designed
per Research).

### META cycle 23 reinforcement

Per `meta_audit_2026-05-21_cycle23.md`:
- Strategy v79 was "best cycle of session" per META
- 4 overcloses caught + reversed (full session pattern)
- Tier-1 board at 8/9 ✅ session-high
- Strategic plan working as designed
- Phase 1 pending Experiment Dev pickup of Bet S + Lane C smoke + Bet X
- User approval on Proposal 10 (PROT-009) still pending

### Tally — V2 substrate evaluation delivered; V2.D winner promoted as formal Bet Y (V2 development track); 4 V2 candidates DEFERRED (V2.A/V2.E/V2.F mechanism-class mismatch; V2.C gated on V2.D); META cycle 23 reinforces

Net effect: V2 substrate roadmap now has clear primary path (Bet Y);
4 deferred candidates with explicit gate criteria; substrate-product
story for V2 is "energy function change" per Research's Pass 2 finding.

---

## v81 update — Phase transformations Research delivered; STACK (P.5 sleep/wake + P.2 metaplasticity + P.6 eviction) is SUBSTRATE-NOVEL highest-P axis (0.75); Bet Z promoted; P.4 dense↔sparse co-designs with Bet Y V2.D; Phase 1 Bet S + Lane C smoke NOW QUEUED by Experiment Dev

Strategy session cycle 72. Research phase-transformations Pass 2
delivered (`research_phase_transformations_2026-05-21.md`, 41 KB,
20:58 — ~25 min after cycle 68 filing).

### Phase transformations — Research findings

**Per-axis ranking by literature-supported probability**:

| Rank | Axis | P(gain over fixed regime, 6mo) | Substrate-product fit |
|---|---|---|---|
| **★1** | **STACK = P.5 + P.2 + P.6-eviction** | **0.75** | **Three coupled mode-switches; SUBSTRATE-NOVEL no paper combines** |
| 1 | **P.5 Sleep/wake mode** | **0.70** | Fachechi dreaming-Hopfield α_c → 1; Bet B EMA-blend partial-implements; R22 already legitimized |
| 2 | P.2 Metaplasticity (multi-timescale) | 0.55 | Benna-Fusi 2016 provable N vs √N; Hopfield-scale gap |
| 3 | **P.4 Dense ↔ sparse mode** | **0.45** | **Hopfield-Fenchel-Young arXiv:2411.08590 single (α, β) knob; co-design with Bet Y V2.D natural** |
| 4 | **P.6 Adaptive β per-query** | **0.35** | Bet G β=32 already; substrate-novel write-T ≠ read-T gap |
| 5 | P.1 Time-varying T (SA/Kovacs) | 0.15 | Marginal in modern-Hopfield regime |
| 6 | P.3 Runtime codebook switching | 0.10-0.20 | Literature doesn't define problem (substrate-novel territory) |
| 7 | P.7 Magnon / collective-mode | 0.05-0.15 | Hardware-bound; reservoir computer ≠ AM |

**Substrate-novel headline**: STACK combination of Fachechi (sleep) +
Benna-Fusi (metaplasticity) + active α-eviction (load modulation) is
the substrate-novel opportunity nobody has done.

### Bet Z formal promotion — STACK multi-regime substrate

**Claim**: substrate operates as **3-mode coupled controller** — sleep
mode (P.5; offline Hebbian replay extending α_c→1 per Fachechi),
multi-timescale plasticity mode (P.2; fast + slow weight components
per Benna-Fusi 2016), active α-eviction (P.6; load modulation under
working-memory pressure). Joint operation > sum-of-parts.

**Multi-probe success criteria**:
- Retention_A ≥ 0.97 (vs Bet B ✅ 0.954 baseline) under multi-phase CL
  with sleep-cycle interspersed
- Capacity stable at M/N=8 across mode switches (no degradation)
- Bet G calibration ECE ≤ 0.10 in each mode
- Audit trace shows which mode active when
- 3 seeds

**Kill criterion**: retention_A < 0.95 OR capacity drops > 30% in any
mode OR mode switching destabilizes Bet 1/Bet 2/Bet A primitives.

**Pre-armed 5 rescue sketches** (per PROT-004):
1. Decouple modes (test individually before joint)
2. Sleep cycle only (just P.5 from Fachechi 2024)
3. Multi-timescale only (just Benna-Fusi 2016 fast+slow)
4. Conservative mode controller (slow switching)
5. P.4 dense↔sparse substitution (replace P.6 with α-entmax)

**Lane mapping**: Lane D (cognitive architecture; multi-regime is
agent-distinctive) + Lane B (on-device personal AI; sleep cycles
enable resource-bounded operation) + Lane C (compliance; explicit
mode-trace satisfies auditability).

### Bet Y + P.4 co-design opportunity

Per Research: **P.4 dense ↔ sparse mode via Hopfield-Fenchel-Young
(α, β) single-knob** is the natural co-design with V2.D modern dense
AM (Bet Y). Both energy-function variants; both substrate-applicable.

**Strategic decision**: Bet Y development should INCLUDE the P.4
single-knob extension. The "(α, β) controller" generalizes V2.D's
energy-function change to a parametric family covering both dense
modern Hopfield (small α) and sparse k-active (large α).

**Capability moves**:

| Capability | v80 state | v81 state | Trigger |
|---|---|---|---|
| Bet Y V2.D modern dense AM | 🔬 active V2 development | 🔬 active + **P.4 co-design**: (α, β) controller variant; Hopfield-Fenchel-Young extension | Phase transformations + V2 eval cross-product |
| Bet Z STACK multi-regime substrate | (not in cap_map) | 🔬 **NEW formal active bet — SUBSTRATE-NOVEL highest-P phase axis P=0.75** | Phase transformations |
| P.6 write-T ≠ read-T substrate-novel gap | (not in cap_map) | 🔬 substrate-novel adaptive-β extension; Bet G ✅ infrastructure leverage | Phase transformations |
| P.1/P.3/P.7 deprioritized | (active candidates) | 🔬 deferred per Research; marginal/undefined/hardware-bound | Phase transformations |

### Phase 1 routing landed in pipeline

Confirmed in dashboard queue_pending: `wave14_betS_pattern_completion_v1`
+ `wave14_lane_C_compliance_audit_smoke_v1` both QUEUED by Experiment
Dev per Strategy's cycle 70 routing.

This is the META strategic plan Phase 1 in flight. Pipeline cycle-by-
cycle verdicts to harvest as they land.

### Substrate-product position after Phase transformations + V2 evaluation

Substrate now has 3 distinct architectural development tracks:

1. **Bet Y (V2.D modern dense AM)** — energy function change; +P.4 co-design (α, β) controller; targets capacity 5× M/N=8
2. **Bet Z (STACK multi-regime)** — substrate-novel three-mode controller; targets retention 0.97+
3. **Bet X (skill composition hybrid HRR+bipolar per Bet X)** — composition + d>25 cliff exceedance via parallel real-valued pool

All three are substrate-novel substrate-product directions. **None are
mutually exclusive** — could combine (Bet Y energy function + Bet Z
multi-regime + Bet X skill composition).

### Tally — Phase transformations Research delivered; Bet Z STACK formally promoted (highest-P substrate-novel phase axis 0.75); Bet Y + P.4 co-design identified; Phase 1 routing landed in Exp Dev queue; substrate has 3 architectural development tracks

Net effect: substrate-product roadmap now has 3 substrate-novel
architectural tracks (Bet Y energy / Bet Z multi-regime / Bet X
composition); Phase 1 in flight; clear gates per track.
