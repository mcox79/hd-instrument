# Wave 14.D — Multi-task continual learning under genuine distribution shift

Drafted 2026-05-19. Unbiased research on the question:
**what does the HDC/VSA substrate actually do when the Phase-B
corpus is GENUINELY different from Phase A, not just a shuffle?**

Our entire continual-learning story (+0.66-0.73 bpc BWT at K=4-32
via random replay, see STATE_2026_05_19) is on Phase-B = shuffle(A).
Same byte distribution, same vocabulary, same structure. Brutal
honesty: this is the weakest possible distribution shift, and we
have never tested anything stronger.

## 1. TL;DR (3 sentences)

Under genuine domain shift (English -> Python -> hex -> Japanese-ASCII)
the substrate's BWT advantage from random replay is predicted to
*shrink* toward the transformer baseline because the mechanism
that gives +0.73 (subspace projection of the Phase-B delta onto
the A-pool row-space, per wave14c_random_replay_mechanism_research)
loses force when the new-corpus row-space has **vanishing overlap**
with the old-corpus row-space — there's no shared subspace to
project onto. The right test is a 4-stage corpus chain (A=English-MD,
B=Python-source, C=hex-binary, D=Japanese-romaji), measured
post-each-stage with 5 seeds, with byte-distribution KL and pool
row-space-overlap reported alongside BWT so the *magnitude* of the
shift is on the axis, not hidden. Predicted outcome: substrate
beats transformer on small shifts (KL < 0.5), ties on medium shifts
(KL ~1), loses on large shifts (KL >> 1) where its inductive bias
(pool stores raw byte 4-grams; W is rank-1 delta on bigrams) provides
zero transfer.

## 2. Why shuffle is a weak shift — the KL-divergence math

The relevant similarity axis between two byte corpora is the
KL divergence of their unigram (or n-gram) distributions, with
secondary axes for vocabulary overlap, sub-word/structural
similarity, and joint-distribution structure.

### Byte-level KL divergences (order of magnitude estimates from
published surveys of code/language byte distributions, e.g.
Kudugunta et al. 2023 MADLAD-400 arxiv 2309.04662; CodeParrot byte
analysis; Common Crawl byte histograms)

| Pair | Byte-unigram KL | Joint-bigram KL | Notes |
|---|---|---|---|
| corpus_A vs shuffle(corpus_A) | ~0.000 | ~3-5 | unigram identical by construction; bigram destroyed |
| English vs Markdown | ~0.05 | ~0.2 | added punctuation, list markers |
| English vs Python source | ~0.15-0.3 | ~0.8-1.2 | punctuation-heavy, indentation, keyword bias |
| English vs C source | ~0.2-0.4 | ~1.0-1.5 | braces, semicolons, type names |
| English vs JSON | ~0.5-0.8 | ~1.5-2.0 | quote-heavy, structural tokens |
| English vs Japanese romaji | ~0.4-0.7 | ~1.0-1.5 | vowel-bias, repeated bigrams (-ka, -to) |
| English vs hex-encoded binary | ~1.5-2.5 | ~3-4 | bytes restricted to 0-9a-f |
| English vs raw binary (PNG) | ~3-4 | ~5-7 | full byte range, no structure |
| English vs UTF-8 Chinese | ~2-3 | ~4-5 | high-byte prefixes 0xE0-0xEF dominate |

(The exact numbers depend on the reference distribution and the
smoothing; the orders of magnitude are robust across the
language-modeling and information-theory literature.)

### Where our +0.73 BWT result sits on this axis

Phase-B = shuffle(corpus_A) destroys the bigram joint but
preserves the unigram exactly. So:

- **Unigram KL = 0** → the W-update on B does not change the
  marginal predictions much; the unigram floor is unchanged.
- **Bigram KL ~3-5** → the conditional predictions are wrecked.

This is a very specific kind of shift: **maximally damaging at
the conditional layer, zero at the marginal layer**. The pool's
job is to restore the conditional structure that B's training
destroyed. Since A's bigrams ARE in the pool, retrieval gives
back exactly what's needed. The +0.73 BWT is therefore not a
"continual learning across domains" result — it's a "rehearsal
recovers the bigram structure when nothing in the new corpus
overwrites it usefully" result.

Under genuine domain shift the picture changes:

- English → Python: the bigram joint is *partly* shared (English
  prose appears in comments and docstrings). The pool's
  English-bigrams are partially relevant. Replay should give a
  *smaller* but still positive BWT.
- English → hex: byte-unigram KL alone is ~1.5-2.5. The pool's
  English bigrams are irrelevant for hex prediction. W's hex
  performance does not benefit from English replay; English
  performance is preserved by replay only if the W-update on hex
  doesn't *overwrite* the English-relevant W entries.
- English → raw binary: pool entries are essentially noise from
  binary's perspective. Replay only helps via the orthogonal-
  subspace-projection mechanism (Mechanism #1 in wave14c).

**Brutal-honesty sentence**: our shuffle protocol is a controlled
test of "can replay restore a destroyed conditional given an
intact marginal pool?". It is NOT a controlled test of "can the
substrate accumulate skills across genuinely different domains?".
The two are different problems with potentially different
answers.

## 3. Literature on HDC/VSA vs other approaches for CL under genuine shift

### 3.1 Mainstream CL benchmarks and what they measure

The standard CL benchmark family (Lopez-Paz & Ranzato 2017,
arxiv 1706.08840, GEM; Chaudhry et al. 2019, arxiv 1812.00420, A-GEM;
Wang et al. 2023 survey arxiv 2302.00487) uses:

- **Split-CIFAR-10/100**: split into disjoint label subsets.
  Same input distribution (natural images), DIFFERENT label set.
  This is class-incremental, not domain-incremental.
- **Permuted-MNIST**: same labels, random fixed pixel permutation
  per task. Input distribution changes in a controlled way.
- **Split-TinyImageNet, Split-ImageNet1K**: scale-up of Split-CIFAR.
- **CORe50, NICO, DomainNet**: genuine domain-incremental
  (real-world domain shifts: clipart -> sketch -> real photo).

**Crucial observation**: Permuted-MNIST is **structurally very
similar to our shuffle protocol** — both preserve the marginal
distribution while destroying the joint. Result on PMNIST in the
literature: ER/A-GEM/DER all get ~85-95% retention, EWC gets
~75-85%. These are STRONG numbers because PMNIST is a weak shift.

On the harder genuine-shift benchmarks (DomainNet, CORe50):

- ER (Experience Replay) baseline retention drops to ~50-70%
  (Chaudhry et al. 2019 Tiny Replay; Buzzega 2020 DER++ Table 2-3).
- DER++ adds logit distillation, gets ~55-75%.
- EWC alone collapses on genuine domain shift (~40-50%) because
  the Fisher matrix from task A doesn't constrain task B's
  important directions.

### 3.2 HDC/VSA-specific CL work

**Hersche et al. 2024 sparse block codes** (arxiv 2306.05003 and
related work) — sparse block-coded VSA used for few-shot
class-incremental on Omniglot. They get strong retention because
new classes occupy fresh orthogonal blocks; no interference with
old blocks. *This relies on architectural sparsity, not replay.*
Our dense BSC delta-rule does not have this property; we'd have
to *port* to a sparse-block substrate to inherit Hersche's CL
guarantees.

**Bricken et al. 2023 Sparse Distributed Memory** (arxiv 2303.11934)
— Top-K activation gives the same orthogonal-write property.
SDM + EWC achieves SOTA on Split-CIFAR-100 because the Top-K
mask makes writes naturally subspace-confined. Bricken explicitly
attributes the CL advantage to sparsity, not to HDC vectors per se.

**Karunaratne et al. 2021 In-memory hyperdimensional computing**
(arxiv 2102.02894) — resonator memory used for few-shot learning,
but their continual-learning experiments are on Omniglot
class-incremental (same image domain, new classes). Not a
genuine-shift benchmark.

**Imani et al. SearchHD, OnlineHD** — online HDC classifiers
update bundles incrementally. Their "continual" claim is for
class-incremental within a single domain (UCIHAR, MNIST).
None tested under truly different input distributions.

**Mainstream CL methods that COULD be applied to HDC substrate**:

- GEM (1706.08840): gradient projection — works on any
  differentiable layer; our rank-1 delta is differentiable.
- A-GEM (1812.00420): cheaper random reference set; we already
  use this implicitly (wave14c finding).
- MIR (1908.04742): priority-by-interference; **we falsified this
  on our substrate** (wave14b_mir_failure_diagnosis); the priority
  signal collapses to cosine-to-batch on rank-1 delta-rule.
- DER++ (2004.07211): functional distillation; on a one-layer
  linear readout collapses to ER (wave14c, mechanism #3).
- EWC (Kirkpatrick 2017, arxiv 1612.00796): Fisher-weighted
  regularization; UNTESTED on our substrate, but predicted to
  give little extra because Fisher of rank-1 delta-rule is
  rank-1 itself.
- L2P / DualPrompt (Wang 2022, arxiv 2204.04799): prompt-based
  CL for transformers; not directly applicable to byte-LM
  substrate.
- MERIT / MEND (Mitchell 2022 arxiv 2110.11309): editor networks
  for LLM continual edits; orthogonal mechanism, could apply to
  W via low-rank update.

### 3.3 What each predicts for genuine domain transfer

| Method | Prediction under English -> Python -> hex |
|---|---|
| ER (random replay) | Strong on small shifts (KL < 0.5), degrades to ~25% retention on large shifts (KL > 2). Subspace-projection mechanism (wave14c #1) loses force as A and B row-spaces become orthogonal. |
| A-GEM | Same as ER for our substrate (equivalent under rank-1 delta-rule). |
| MIR | Same as ER (rank-equivalence collapse). |
| DER++ | Same as ER on one-layer readout. |
| EWC | Weak on genuine shift: Fisher of A is not a strong constraint when B occupies a different subspace. |
| Sparse-block VSA (Hersche) | Strong CL across all shifts IF new domains get fresh blocks. Requires architectural change. |
| SDM Top-K (Bricken) | Strong across all shifts IF top-K writes are domain-disjoint. Requires architectural change. |
| HDC substrate (ours, dense BSC + replay) | Same as ER for our substrate. Subject to A-GEM-equivalent shrinkage. |
| Transformer + LoRA per domain | Strong: each domain gets fresh adapter. No backward transfer issue, but also no forward transfer. |
| Transformer + full FT | Catastrophic on genuine shift without replay; ~30% retention. |

**Bottom line for the substrate**: under genuine domain shift our
mechanism is **standard A-GEM-equivalent replay** with all the
limitations and gains thereof. We do not have a separate
architectural CL advantage (we don't have sparsity, we don't
have prompts). The HDC-substrate-uniqueness claims (compositional
decomposition, pool-based interpretability) are *capabilities*,
not CL mechanisms per se. They might enable BETTER replay
selection or BETTER consolidation, but as currently implemented
they do not.

## 4. Predicted substrate behavior under increasing shift

Combining the wave14c mechanism diagnosis with the literature
priors above, predicted BWT as a function of byte-bigram KL
between Phase A and Phase B:

```
            BWT recovery (relative to no-replay baseline)
            ^
       +0.7 |  .   <- shuffle(A): KL_unigram=0, KL_bigram~4
            |   `.
       +0.5 |     `.   <- markdown variant: KL~0.2
            |       `.
       +0.3 |         `.   <- Python source: KL~0.8-1.2
            |            `.
       +0.1 |              ``.. <- Japanese romaji: KL~1.0-1.5
            |                  ``..  <- hex: KL~3
        0.0 |--------------------------``-->
            0       1       2       3       KL_bigram(A, B)
```

The curve is monotone decreasing in KL because the subspace-
projection effect of replay (the mechanism that gives +0.73)
scales with the **overlap between the pool's row-space and the
new-corpus row-space**. At KL=0 (shuffle), overlap is maximal —
A's row-space IS the relevant subspace for B's marginals.
At KL >> 1, overlap is near zero — the pool projects W toward
a subspace orthogonal to where B's loss matters.

### Three distinct regimes

**Regime I (KL_bigram < 0.5, shuffle-like)**: replay restores
the destroyed conditional; W's marginals are intact. BWT
recovery 50-100%. Substrate beats transformer baseline because
its inductive bias (raw byte 4-grams) is fully reusable.

**Regime II (0.5 ≤ KL_bigram ≤ 1.5, weak genuine shift)**: replay
partially restores; some shared structure (e.g., English prose
in docstrings, ASCII-printable bytes in code). BWT 10-40%.
Substrate roughly ties transformer + ER.

**Regime III (KL_bigram > 1.5, strong genuine shift)**: replay
mostly inert; W's old-domain entries are slowly overwritten by
new-domain updates regardless of replay. BWT < 10%. Substrate
underperforms transformer + LoRA-per-domain (clean isolation
beats noisy replay) but is comparable to transformer + full FT.

### Where forgetting actually comes from in each regime

| Regime | Dominant forgetting source | Best mitigation |
|---|---|---|
| I | W-overwrite at the bigram layer | Random replay (already in hand) |
| II | W-overwrite + pool-coverage gaps | Replay + selective pool growth on novel atoms |
| III | W-overwrite + pool entries genuinely useless | Per-domain W slabs (architectural separation) |

**Brutally honest implication**: random replay solves Regime I
because Regime I's forgetting is the kind of forgetting random
replay is *designed* to solve. The "+0.73 BWT" is real, but it's
the answer to the easy version of the problem. The hard version
(Regime III) is what the Tier-1 product capability requires, and
we have no evidence the substrate handles it specially.

## 5. The right experiment design

### 5.1 Corpora chain

Sequential phases. After each, save W and pool; measure BWT on
ALL prior phases.

| Phase | Corpus | Source | KL_bigram vs prior | Size |
|---|---|---|---|---|
| A | English Markdown (Project Gutenberg + Wikipedia) | mix of fiction and reference | n/a | 1-5 MB |
| A' | shuffle(A) | (positive control for our prior result) | ~3-5 vs A on bigram, ~0 on unigram | same |
| B | Python source (filtered subset of CodeParrot or The Stack) | code, no comments stripped | ~0.8-1.2 vs A | 1-5 MB |
| C | Japanese transliterated to ASCII romaji (NHK news kana converted) | Japanese subword structure in ASCII | ~1.5 vs B, ~1.0 vs A | 1-5 MB |
| D | Hex-encoded binary (random PNG bytes, hex-printed) | byte distribution restricted to 0-9a-f | ~2.5 vs C, ~3 vs A | 1-5 MB |

**A' is the positive control** — we know the result, it serves as
internal sanity for the experiment.

### 5.2 Conditions

For each transition (e.g., post-A -> add B), measure:

- **C0**: no intervention. Train W on B from W_A; report BWT on A.
- **C1**: random replay 50% (the validated W_frozen result).
- **C2**: A-GEM gradient projection with random reference set.
- **C3**: per-domain W slabs (architectural CL): freeze W_A,
  train fresh W_B, route by simple domain detector. This is the
  upper-bound — no interference by construction.
- **C4**: random replay + selective pool growth (add to pool any
  B-bigram whose pool-cosine to existing entries is < threshold;
  pre-registered threshold 0.7).

### 5.3 Seeds and statistics

- **5 seeds minimum** per (phase, condition) cell.
- Bayes factor stopping: if BF₁₀ comparing C1 vs C0 is > 6 or < 1/6,
  stop; else continue to 10 seeds.
- Report mean, SD, and bootstrap 90% CI per cell.

### 5.4 Metrics

For each phase transition:

- **BWT** (Lopez-Paz definition): mean over prior tasks of
  `metric_after_current_phase - metric_after_task_was_learned`.
- **FWT** (forward transfer): metric on the new corpus *before*
  training on it, vs metric of a fresh model. Captures whether
  prior training helps with new domain.
- **Pre-shift bpc** on each completed phase's heldout split.
- **Pool row-space overlap** with new corpus row-space (SVD-based,
  report the top-K singular-vector alignment). This is the
  diagnostic for which regime we're in.
- **Byte-bigram KL** between current corpus and pool's empirical
  bigram distribution. Reports shift magnitude on the axis we
  predict matters.

### 5.5 Pre-registered predictions (Lakens-style, machine-readable)

- **P1**: For Phase A' (shuffle control), C1 BWT ≥ +0.65 bpc.
  (Positive control: replicates our existing result.)
- **P2**: For Phase B (Python), C1 BWT in [+0.10, +0.40] bpc.
  (Regime II prediction.)
- **P3**: For Phase D (hex), C1 BWT in [-0.10, +0.10] bpc.
  (Regime III prediction: replay mostly inert.)
- **P4**: For all phases, C3 (per-domain W slabs) BWT ≥ +0.5 bpc.
  (Architectural separation upper-bound.)
- **P5**: For Phase D, C3 - C1 ≥ +0.4 bpc. (Architectural
  separation strictly dominates replay in Regime III.)

**Falsification**: if P3 is wrong (replay continues to give
substantial BWT in hex), then our wave14c mechanism diagnosis
is wrong; replay is doing something other than subspace
projection.

If P5 is wrong (no architectural advantage in Regime III), then
either Phase D isn't actually in Regime III (re-check KL math),
or the substrate has some inductive bias for arbitrary byte
distributions that we don't currently understand.

### 5.6 Effort estimate

- Implementation: 1 day (corpora ingestion + phase chaining;
  reuses existing exp_wave45 infrastructure).
- Runs: 5 seeds × 4 phases × 5 conditions × ~20 min/run ≈
  35 GPU-hours. Comfortably one overnight batch on the dual-GPU
  rig (per project_runner_race.md).
- Analysis + writeup: 2 days.

Total: ~4 days from "go" to result.

## 6. Product opportunity in genuine multi-task CL

### 6.1 What the substrate could plausibly do

Given the predicted Regime-I dominance and Regime-III parity,
the realistic product positioning:

**Wedge A — "Domain-specialized expert that grows within a domain"**.
On-device personal AI: a single domain (user's writing, user's
codebase, user's documents) with continuous accumulation. This
stays in Regime I because every new chunk is similar to prior
chunks. Our +0.73 BWT result IS the right number for this product.
Killer feature: zero-cost editing/deletion (pool entry remove +
W_frozen). GDPR-native. Privacy-native (no cloud round-trips).

**Wedge B — "Edit-then-query for LLMs"**. Use HDC pool as an
external editable memory bolted onto a transformer. The
transformer provides cross-domain generalization (the part our
substrate can't do alone); the HDC pool provides editability
and provenance. MERIT-style editor (Mitchell 2022 2110.11309)
but with HDC primitives. This is a real product because the LLM
edit problem is unsolved at production scale; existing solutions
(MEND, ROME, MEMIT) are all noisy and have side effects. HDC
editing is bit-exact (per STATE_2026_05_19 §5).

**Wedge C — "Provenance-traceable retrieval-augmented generation"**.
Every retrieval cites the exact pool entry. Auditable for legal
and compliance use cases (medical, legal, finance). This is
RAG with a 14.B decomposition layer that lets you see which
pieces of which sources contributed to the final answer.

### 6.2 What the substrate is NOT (be honest)

- **Not** an "LLM that learns from every conversation without
  retraining" — at least not for arbitrary conversations. Strong
  drift across domains (Regime III) breaks it.
- **Not** "add Japanese to an English model and keep both fluent"
  in the literal sense. The W in our substrate does not have the
  capacity to be fluent in two different sub-word structures
  simultaneously without architectural separation. The pool
  retains source material, but the *predictive* layer drifts.
- **Not** a replacement for transformers on cross-domain tasks.
  It's a complement: editable memory for a transformer is more
  defensible than "HDC-only foundation model".

### 6.3 Comparable products

- Mem0 (mem0.ai, formerly EmbedChain) — vector-DB-backed memory
  for chat. Not editable bit-exact; uses dense embeddings, no
  compositional decomposition.
- LangMem, Letta (formerly MemGPT) — long-term memory for agents.
  Same dense-embedding limitation.
- OpenAI memory (released 2024) — opaque; no provenance.
- Custom GPTs / Claude Projects — file-based context, no learning.

**The substrate's defensible differentiator**: bit-exact memory
edits + compositional decomposition + bounded-cost retrieval.
None of the above can claim all three.

### 6.4 Realistic timeline to product

- 3 months: prototype Wedge B (LLM + HDC memory adapter) on a
  small open-source LLM (e.g., Qwen-2.5-3B). Demo: edit a fact,
  show before/after, show provenance.
- 6 months: benchmark on standard LLM-edit datasets (zsRE,
  CounterFact). Goal: match or beat MEMIT/ROME on edit success
  rate; strictly dominate on side-effect rate.
- 12 months: integration with a host LLM product (Cursor,
  Continue, or self-hosted). Pricing: per-edit + per-pool-size.

This is a research-driven product, not a research project pretending
to be a product. The path is concrete.

## 7. Brain mapping

(Mechanism description first; substrate analogue second.)

### 7.1 The hippocampal-cortical loop for multi-task learning

The biological systems that handle interference across
genuinely different tasks (different sensory modalities, different
behavioral contexts) involve multiple anatomically distinct
mechanisms:

- **Pattern separation in dentate gyrus** (Leutgeb-Leutgeb 2007;
  Yassa-Stark 2011 review): DG creates orthogonalized
  representations of similar inputs via sparse coding + lateral
  inhibition. Same physical input -> very different DG codes if
  context differs. This is the brain's mechanism for "two
  similar episodes don't interfere".
- **Context-tagging by lateral entorhinal cortex and prefrontal
  cortex** (Eichenbaum 2017 *Memory: organization and control*;
  Komorowski-Manns-Eichenbaum 2009): episodes are tagged with
  contextual features (where, when, what task) that act as
  retrieval cues. Same content with different context -> different
  retrieval.
- **Schema integration in medial prefrontal cortex** (Tse et al.
  2007 *Science* schema consolidation; Gilboa-Marlatte 2017):
  consistent-with-prior-knowledge episodes consolidate FAST
  (one trial); inconsistent episodes consolidate SLOWLY through
  the hippocampal route. This is a learned domain-similarity-
  gated plasticity rate.
- **SWR-gated cortical consolidation** (Buzsáki 2015; Joo-Frank
  2018): the offline consolidation mechanism diagnosed in
  wave14c. Does NOT solve multi-domain on its own — it requires
  the upstream pattern separation and context tagging.
- **Cortical multiplexing** (Mante et al. 2013 *Nature* context-
  dependent computation in PFC; Yang et al. 2019 task
  representations across hundreds of tasks): single PFC
  populations represent many tasks via low-dimensional task-
  context inputs that gate the computation. Not separate
  networks; multiplexed by context.

The crucial point: **biology does not handle multi-task CL with
replay alone**. Replay is one component in a stack with pattern
separation, context tagging, schema gating, and cortical
multiplexing. Each component handles a different aspect of the
problem.

### 7.2 What the substrate has and doesn't have

| Biological component | Substrate analogue | Gap |
|---|---|---|
| DG pattern separation | None — BSC vectors are dense, no orthogonalization step | Critical gap for Regime III |
| Context tags (LEC/PFC) | None — pool entries have no context label | Critical gap for Regime III |
| Schema gating (mPFC) | Implicit in PPMI bigram statistics — but not used as a plasticity gate | Could be added |
| SWR-gated consolidation | Random replay branch | Present and validated |
| Cortical multiplexing | None — W is a single matrix, no task-gating | Could be added via per-domain W slabs (C3 condition above) |

**Brain-honest reframing**: our substrate has the consolidation
mechanism (replay) but lacks the **separation** and **gating**
mechanisms that biology uses for multi-domain learning. This
predicts exactly the result we expect: substrate works in
Regime I (replay suffices), struggles in Regime III (separation
needed).

**Architecturally honest next step**: if Regime III matters for
the product, the substrate needs a sparsity/separation mechanism.
Two concrete options from the literature:

- Port to a sparse-block code (Hersche 2024) — gets DG-like
  pattern separation by construction. New domains occupy fresh
  blocks. Tradeoff: lose the dense-bundle decomposition
  capability that 14.B gives us.
- Add per-domain W slabs with a learned router (cortical
  multiplexing analogue). Keeps the bundle, adds task-context
  input. Tradeoff: now requires a router, which is a new
  component to train.

Both are non-trivial architectural changes. Neither is "free"
relative to the current substrate.

### 7.3 The framing that survives

"Random replay in a dense Hebbian substrate is a faithful
biological analogue of SWR-gated cortical consolidation, but
without the pattern-separation and context-tagging that biology
uses upstream of consolidation. Adding those mechanisms is
required for genuine multi-domain continual learning."

This is honest, defensible, and gives a clear research roadmap
(pattern separation + context tagging are the next architectural
extensions). It does not over-claim that the current substrate
is biology-complete for the CL problem.

## 8. Sources

### Mainstream CL methods
- Lopez-Paz & Ranzato 2017, GEM, arxiv 1706.08840.
- Chaudhry et al. 2019, A-GEM, arxiv 1812.00420.
- Aljundi et al. 2019, MIR, arxiv 1908.04742.
- Aljundi et al. 2019, GSS, arxiv 1903.08671.
- Buzzega et al. 2020, DER/DER++, arxiv 2004.07211.
- Kirkpatrick et al. 2017, EWC, arxiv 1612.00796.
- Verwimp et al. 2021, Rehearsal Revealed, arxiv 2104.07446.
- Mirzadeh et al. 2020, mode-connectivity in CL, arxiv 2010.04495.
- Ding et al. 2024, linear-regression CL theory, arxiv 2405.17583.
- Goldfarb-Hand 2025, replay can provably increase forgetting, arxiv 2506.04377.

### CL surveys
- Wang et al. 2023, *A Comprehensive Survey of Continual Learning*, arxiv 2302.00487.
- De Lange et al. 2021, *Continual learning survey*, IEEE TPAMI.

### HDC/VSA-specific CL
- Hersche et al. 2024, sparse block codes for few-shot CL, arxiv 2306.05003.
- Bricken et al. 2023, Sparse Distributed Memory + CL, arxiv 2303.11934.
- Karunaratne et al. 2021, In-memory HDC for few-shot, arxiv 2102.02894.
- Frady & Sommer 2020, *Robust computation with rhythmic spike patterns*, PNAS — resonator theory.

### LLM continual learning and editing
- Mitchell et al. 2022, MEND (editor networks), arxiv 2110.11309.
- Meng et al. 2022, ROME (rank-one model editing), arxiv 2202.05262.
- Meng et al. 2023, MEMIT (mass editing), arxiv 2210.07229.
- Wang et al. 2022, L2P / DualPrompt, arxiv 2204.04799.
- Zheng et al. 2023, *Learn or Recall*, LLM CL survey, arxiv 2310.10866.
- Wu et al. 2024, *Llama-CL*, arxiv 2406.10307 (continual pretraining of Llama).

### Byte-level corpus statistics (KL math)
- Kudugunta et al. 2023, MADLAD-400, arxiv 2309.04662.
- Xue et al. 2022, ByT5, arxiv 2105.13626 — byte-level LM properties.
- CodeParrot project documentation (Hugging Face): byte distribution
  of Python source.
- Common Crawl byte histograms (web-scrape statistics, various
  Hugging Face datasets cards).

### Brain mechanisms for multi-task learning
- Eichenbaum 2017, *On the Integration of Space, Time, and Memory*,
  Neuron 95(5):1007-1018 — context-tagging review.
- Komorowski, Manns & Eichenbaum 2009, *Robust conjunctive
  item-place coding by hippocampal neurons*, J Neurosci 29(31).
- Leutgeb & Leutgeb 2007, *Pattern separation, pattern
  completion, and new neuronal codes within a continuous CA3 map*,
  Learn Mem.
- Yassa & Stark 2011, *Pattern separation in the hippocampus*,
  Trends Neurosci 34(10):515-525.
- Tse et al. 2007, *Schemas and memory consolidation*, Science
  316(5821):76-82.
- Gilboa & Marlatte 2017, *Neurobiology of schemas and schema-
  mediated memory*, Trends Cogn Sci 21(8):618-631.
- Mante et al. 2013, *Context-dependent computation by recurrent
  dynamics in prefrontal cortex*, Nature 503(7474):78-84.
- Yang et al. 2019, *Task representations in neural networks
  trained to perform many cognitive tasks*, Nat Neurosci 22(2).
- Buzsáki 2015, *Hippocampal sharp wave-ripple*, Hippocampus
  25(10):1073-1188.
- Joo & Frank 2018, *The hippocampal sharp wave-ripple in memory
  retrieval for immediate use and consolidation*, Nat Rev
  Neurosci 19(12):744-757.
- Mattar & Daw 2018, *Prioritized memory access explains
  planning and hippocampal replay*, Nat Neurosci 21(11):1609-1617.
- Schapiro et al. 2017, *Complementary learning systems within
  the hippocampus*, Philos Trans R Soc B 372(1711).

### Internal references (this repo)
- `notes/STATE_2026_05_19.md` — current BWT numbers.
- `notes/wave14b_continual_learning_design.md` — original CL design.
- `notes/wave14c_random_replay_mechanism_research.md` — A-GEM-
  equivalent mechanism for our +0.73 result.
- `notes/wave14b_mir_failure_diagnosis.md` — rank-equivalence
  collapse of MIR on rank-1 delta-rule.
- `notes/wave14b_r7_replay_literature.md` — Goldfarb-Hand anchor.

---

## Two-hundred-word executive summary (caller-facing)

Our +0.73 BWT continual-learning result is on Phase-B = shuffle(A),
which preserves byte unigrams exactly (KL=0) while destroying
bigrams. This is the weakest possible distribution shift — and
crucially, exactly the regime where our random-replay mechanism
(A-GEM-equivalent subspace projection per wave14c) is fully
binding. Under genuine domain shift (English -> Python -> Japanese
romaji -> hex, with byte-bigram KL up to ~3) the projection loses
force because the new-corpus row-space has shrinking overlap with
the pool's row-space.

**Recommended experiment**: a 4-phase corpora chain (English-MD,
Python-source, Japanese-romaji, hex-encoded-binary) with 5 conditions
(no-replay, random replay, A-GEM, per-domain W slabs, replay +
selective pool growth). 5 seeds per cell, ~35 GPU-hours total.
Report BWT, FWT, pre-shift bpc, pool row-space overlap, and
byte-bigram KL per phase. Pre-registered predictions: replay gives
+0.65 on shuffle (positive control), +0.10-0.40 on Python, near-zero
on hex. Per-domain W slabs dominate replay in the hex phase by ≥
+0.4 bpc.

Honest framing for Tier-1 product: substrate dominates within-domain
accumulation (Wedge A: on-device personal AI) and is best positioned
as an editable-memory adapter for transformers (Wedge B), not as a
standalone cross-domain learner.
