# hd-instrument: next-phase research plan

Forward plan agreed 2026-05-17. Structured as **two parallel bets** with a **shared decision gate (Track 0)** that determines how aggressively to pursue each. Replaces the post-Week-8 placeholder content in `PLAN.md`.

## Strategic position

The build phase is done. Six VSA substrates measured under a common protocol (FHRR, HRR, BSC, VTB, permutation, tangent-space hyperbolic); all converge on β ≈ 0.7–1.2 depth scaling — the substrate axis is exhausted. Three independent architecture experiments (pointer-chain HDC, recurrent VSA, multi-relation Hebbian graph) crack the depth ceiling on synthetic structured tasks. Observability layer with ablation traceability is shipped (commit `2da311f`). Lit search confirms ablation-traceable per-relation external memory + frozen LLM is unpublished territory; per-relation orthogonal operators (OrthogonalE, EMNLP 2024) and HRR-inside-attention (GHRR Transformer, 2024) bracket the space but don't occupy it.

Two coherent research bets, both worth pursuing because they share infrastructure and de-risk each other:

| | Bet A (small) | Bet B (big) |
|---|---|---|
| **Claim** | HDC retrieval/memory layer beats RAG SOTA on multi-hop QA with full ablation traceability | Hebbian-trained connections over VSA substrate train a language model from scratch with no backprop |
| **Architecture** | Frozen 1–8B LLM + HDC memory (pointer-chain + multi-relation graph) | No transformer. VSA substrate + Hebbian-plastic connection layer + 6 neuromodulators + reward-modulated learning |
| **Differentiator** | Auditable reasoning + lower retrieval compute vs Titans/ATLAS/HippoRAG 2 | Energy-bounded LLM-class capability on hardware transformers can't run on; continual learning without forgetting |
| **Timeline** | ~3 months | 12–24 months |
| **P(ships useful artifact)** | ~80% | ~40% |
| **P(category-defining)** | ~10% | ~15% |
| **P(beats SOTA on chosen benchmark)** | ~30% | ~5–15% |

Both bets are durable independently of each other. Bet A's observability + retrieval infrastructure is exactly what Bet B needs to debug training. Bet B's architecture, if it works at any scale, makes a natural deployment pattern alongside Bet A's augmentation approach (small Hebbian-VSA-LM as the model, HDC memory layer as the context).

## Track 0 — shared decision gate (1–2 weeks)

Three parallel sub-tracks. Decision criteria stated up front. No proceeding to full Bet A or B until Track 0 reports.

### Track 0.1 — Algorithmic feasibility probe (3–4 days, *highest stakes*)

The kill-switch test for Bet B. Build a tiny pure-Hebbian-VSA character-level language model on a small corpus (Penn Treebank or WikiText-2 first 100K chars). Architecture spec:

- **Substrate:** N=4096 FHRR atoms, one per character in vocab (~256 atoms for byte-level).
- **Context representation:** depth-k bundle (k ∈ {4, 8, 16}) of recent character atoms, with positional binding.
- **Connection layer:** Hebbian association matrix between context-bundle states and next-character atoms, updated online via three-factor rule: `ΔW = arousal · reward · pre · post` where reward = log-probability of the true next character under current cleanup distribution.
- **Generation:** at each position, bind current context, cleanup against character codebook softmax-weighted by similarity, output a distribution.
- **Training:** stream the corpus once; emit semantic events at every prediction; capture snapshots at each 10K-token boundary; observable end-to-end.

**Baselines on identical corpus:**
- 5-gram language model (clear floor)
- 1M-param transformer (~200K steps; the realistic ceiling for this scale)

**Decision criteria (perplexity on held-out 10% of corpus):**
- Within 2× of tiny transformer → **Bet B alive**; commit to full architecture exploration.
- Between n-gram and tiny transformer → **hybrid scope**; Bet A becomes higher-priority but with bigger ambition.
- At or below n-gram → **Bet B dead at this architecture**; consider one architectural pivot before falling back fully to Bet A.

### Track 0.2 — Hardware characterization (2–3 days, parallel)

Profile the operations the project uses and project onto hardware. This pays off independently of either bet because it produces the energy/efficiency story that's load-bearing for the user's "uniquely enabling" framing.

- **Ops to profile:** FHRR bind, BSC bind, HRR bind (FFT-based), cleanup over codebook (linear and ANN), Hebbian update with modulator gating, multi-relation matrix spread.
- **Metrics per op:** FLOPs, bytes moved, ops-per-token-equivalent, dependency chain depth.
- **Hardware classes to project onto:**
  - Commodity CPU (AVX-512): real benchmarks via `pytest-benchmark` already wired.
  - GPU (consumer + H100-class): batched timings via PyTorch CUDA.
  - In-memory analog compute (IBM Zurich phase-change memory): use published per-op energy from Sebastian/Rahimi 2023–2024.
  - Bit-parallel ASIC / FPGA for BSC: cite Imani et al. work, project from CMOS scaling.
- **Deliverable:** `notes/hardware_characterization.md` with a comparison table: per-op energy across substrates and hardware classes, plus a one-paragraph "if this works, here's what it would run on" verdict.

### Track 0.3 — HippoRAG 2 baseline on MuSiQue (2 days, lowest priority, parallel)

Only kicks off if Track 0.1 falls into "hybrid" or "dead" tiers. Reproduce HippoRAG 2 on MuSiQue-Ans dev set using their published checkpoint or re-implementation. Confirm MuSiQue F1 ≈ 75.4 to within reasonable tolerance. This grounds Bet A's baseline numbers.

### Track 0 decision matrix

| Track 0.1 outcome | Track 0.2 outcome | Action |
|---|---|---|
| Within 2× transformer | Compelling hardware story | Full commit Bet B; Bet A continues as parallel methods paper |
| Within 2× transformer | Weak hardware story | Commit Bet B but flag the strategic risk; lit-search alternative hardware angles |
| Hybrid tier | Compelling hardware story | Bet A scope-expanded to "Hebbian-VSA reasoning module + frozen LLM"; Bet B held in reserve |
| Hybrid tier | Weak hardware story | Standard Bet A; write Track 0.1 results as a workshop paper |
| At/below n-gram | Compelling hardware story | One architectural pivot on Bet B (different binding scheme, different update rule); if also fails, ship methods paper |
| At/below n-gram | Weak hardware story | Methods paper on substrate + connectivity + observability findings; close out research arc |

## Bet A — HDC memory layer for frozen LLM (full plan if Track 0 lands hybrid or dead)

### Architecture

- **Memory store:** multi-relation Hebbian graph (one connection matrix per relation type) + pointer-chain HDC for episodic context. Both already prototyped at small scale.
- **LLM:** frozen Llama-3-8B-Instruct or Qwen-2.5-7B-Instruct (open-weights, fits on a single H100, established baselines).
- **Interface:** standard RAG-style — HDC retrieval returns top-k passages or structured facts, formatted as text, prepended to LLM prompt.
- **Differentiator vs HippoRAG 2:** typed-relation operators (not text-only retrieval), ablation-traceable trace of which relation/edge drove the answer.

### Phases

1. **Reproduce baselines** (week 1–2). HippoRAG 2 on MuSiQue/CofCA/2Wiki dev sets. Vanilla RAG (BM25 + dense retrieval) as floor. Confirm published numbers.
2. **Wire HDC retrieval** (week 3–4). Replace HippoRAG 2's retrieval with our multi-relation graph. Same interface to the LLM. Measure accuracy, compute, ablation traceability.
3. **Compositional generalization test** (week 5). Construct held-out relation compositions on MuSiQue or CofCA. Measure whether HDC retrieval generalizes to unseen compositions vs HippoRAG 2.
4. **Ablation studies** (week 6). For each multi-hop answer, ablate the relation / edge / modulator the trace says drove it. Show the answer changes. This is the falsifiable observability claim.
5. **Write up** (week 7–10). Methods paper, target NeurIPS workshop or ICLR proceedings. Ship `hd-instrument` v0.1.0 to PyPI alongside.

### Kill criteria for Bet A

- HippoRAG 2 reproduction fails (likely an implementation bug; debug, don't pivot).
- HDC retrieval at matched compute is worse than HippoRAG 2 by >5 absolute F1 on MuSiQue. → Fall back to writing the methods paper on observability + substrate findings without the SOTA claim.
- Compositional generalization gap is < 3 points. → The "typed-relation" differentiator isn't worth the engineering; drop to standard RAG comparison.

## Bet B — Hebbian-trained VSA language model (full plan if Track 0.1 lands "alive")

### Architecture

This is the brain-inspired version of training. **No transformer. No backprop.**

- **Substrate:** VSA atoms, fixed, drawn from FHRR or BSC distribution (pick by Track 0.2 hardware projection). Vocabulary atoms + role atoms (position, syntactic role, semantic role).
- **Connection layer:** sparse Hebbian association matrices linking context-state hypervectors to candidate next-token hypervectors. *This is what gets trained.* These matrices ARE the model parameters.
- **Modulator suite (6 factors, see "Neuromodulator architecture" below):** reward, surprise, attention, arousal, recency, gating.
- **Learning rule:** three-factor rule `ΔW = arousal · M(reward, surprise) · pre · post`, where `M` mixes reward prediction error and novelty signal. Local updates only. No global backward pass.
- **Inference:** input → context-bundle → cleanup against connection matrix → softmax-weighted output distribution.
- **Architecture depth:** multi-layer composition via stacked Hebbian matrices, but each layer learns locally. Compatible with predictive coding formulations (Whittington & Bogacz 2017) for the credit-assignment-at-depth question.

### Phases

1. **Validate at small scale** (Track 0.1, already in plan). Character-level. Establish that the architecture trains at all and produces sub-n-gram perplexity.
2. **Scale corpus** (month 2). 1B tokens. Word-level vocab. Measure perplexity vs n-param transformers at matched compute.
3. **Scale connections** (month 3–4). 10M–100M connection weights. Test where Hebbian capacity caps out.
4. **Continual learning study** (month 5). Stream new corpora; measure whether Hebbian updates produce catastrophic forgetting (predicted: no) and whether they continue to improve perplexity on the original corpus.
5. **Compositional generalization** (month 6). Tests Bet B's claim that the connection layer learns structure rather than memorizing statistics.
6. **Hardware co-design** (month 7+). With Track 0.2 in hand, target one specific in-memory analog or bit-parallel deployment. Demonstrate measured energy advantage on a fixed task.
7. **Decision: scale further or write up** (month 9). Based on perplexity-vs-compute curves, decide whether to push to 1B+ parameter-equivalent or write the result as-is.

### Kill criteria for Bet B (per phase)

- Phase 2: perplexity at matched compute is more than 5× worse than transformer. → One pivot allowed (different connection topology, different update rule, predictive-coding wrapper). If still fails, write up the small-scale result and stop.
- Phase 3: perplexity plateaus before transformer matches. → That's the architectural ceiling. Write it up; consider whether the ceiling is useful for any deployment regime.
- Phase 4: catastrophic forgetting appears at scale. → Surprising but real; investigate before continuing.
- Phase 6: measured energy advantage is less than 10× over GPU inference. → The hardware differentiator is weaker than claimed; reconsider strategic positioning.

## Neuromodulator architecture

The user asked: why three factors? Why not four? How many does the brain have?

### Why "three-factor"

The term "three-factor learning" (Frémaux & Gerstner 2016 review) refers to the minimum theoretical structure to make Hebbian learning solve credit-assignment problems pure Hebbian cannot:

1. **Pre-synaptic activity** (was the input active?)
2. **Post-synaptic activity** (was the output active?)
3. **Modulator signal** (was something globally informative happening?)

The first two are Hebbian (correlation). The third is what turns pure Hebbian into something that can solve XOR, do reinforcement learning, or perform credit assignment. Without the third factor, you only get unsupervised correlation. The "three" is theoretical minimum, not biological constant.

### What the brain actually uses

There are roughly five major classical neuromodulator systems with whole-brain reach, plus dozens of more localized peptide modulators:

| System | Source | Functional role |
|---|---|---|
| Dopamine (DA) | VTA, substantia nigra | Reward prediction error, motivation, novelty, action selection |
| Norepinephrine (NE) | Locus coeruleus | Arousal, attention to relevance, global learning rate, stress response |
| Serotonin (5-HT) | Raphe nuclei | Mood, value/cost signals, satiety, behavioral inhibition, time perception |
| Acetylcholine (ACh) | Basal forebrain, brainstem | Attention, encoding-vs-retrieval mode switching, signal-to-noise gating |
| Histamine | Tuberomammillary nucleus | Wakefulness, alertness |

Beyond these, peptide modulators with demonstrated learning-relevant effects: oxytocin, vasopressin, opioids/endorphins, endocannabinoids, orexin, substance P, CRH, NPY, CCK, and many more. Counting strictly: 5 major; including peptides: ~20; including all signaling molecules with modulatory effects: 50+.

Crucially, **the brain uses a combinatorial code** — modulators are released in patterns, not in isolation. A surprise event releases NE + DA in a specific ratio; a routine reward releases DA alone; consolidation involves ACh and NE coordination during sleep. Single-factor descriptions are simplifications.

### What our codebase has and what Bet B will likely need

Current `hdlab/modulators.py`:

| Modulator | Mapped to | Role in code |
|---|---|---|
| `attention` | ACh | Cleanup threshold |
| `reward` | DA | Hebbian update sign/gain |
| `arousal` | NE | Global plasticity rate |
| `recency` | 5-HT (loose) | Bundling weight on new items |
| `gating` | GABA | Per-module activation mask |

For Bet B's Hebbian-trained VSA-LM, we likely need to add at least one more:

- **`surprise`** (novelty / prediction-error, distinct from reward): brain releases NE on surprise and DA on reward, and they signal different things. Reward says "this was good"; surprise says "this was unexpected — encode it more strongly." For language modeling, prediction error on the next token *is* the relevant signal, but it's not quite the same as reward — large negative predictions should drive encoding regardless of whether the outcome is "good."

That brings the architecture to **six factors**: attention, reward, surprise, arousal, recency, gating. This is well within biological precedent (matches the major classical systems plus a separate error channel) and is the conventional count in modern computational-neuroscience implementations of three-factor learning.

We may add more later as research demands — eligibility-trace decay parameter (could be modulator or hyperparameter), curiosity / exploration drive (distinct from external reward), confidence/uncertainty (modulates update magnitude). Each addition needs justification by what learning behavior it enables. Don't chase biological completeness for its own sake.

### Concrete change to the codebase (small, deferred)

When Bet B activates, add `surprise` to `ModulatorState` in `hdlab/modulators.py`, wire it into `learning.HebbianAssociations.update()` as a separate signal that interacts with `reward` multiplicatively, and add a `test_modulator_effect.py` witness that surprise alone drives encoding without reward. Three-line change in the dataclass, plus the wiring and verification test. Not urgent — track this for when Bet B kicks off.

## Strategic posture (durable, independent of which bet works)

Three durable advantages survive regardless of how the bets resolve:

1. **Energy-constrained / edge deployment.** HDC's hardware story is real and well-established for primitives (XOR, complex unit-modulus mul, in-memory similarity). Even if pure-HDC doesn't match transformers on perplexity, it has uncontested ground on devices where transformers can't physically run.
2. **Auditable / ablation-traceable reasoning.** The observability layer that shipped already gives us a differentiator vs Titans / ATLAS / HippoRAG 2 that doesn't depend on accuracy numbers. This matters in regulated domains independent of any other claim.
3. **Continual learning without forgetting.** Hebbian updates are local and online. Transformers require retraining or fine-tuning regimes with rehearsal. Even if Hebbian-VSA caps out at smaller models, the deployment regime of "agent with continuously updating memory" is durable.

These are the things to emphasize in any external communication regardless of bet outcome. They give us something to ship even in the worst case.

## Open research questions (the exciting threads, recorded so we don't lose them)

Tracked here so each is referenceable and so we don't quietly drop them. Each is a candidate for a future experiment or pivot.

1. **Credit assignment at depth with three-factor learning.** Pure three-factor works at shallow networks. At depth-50, does it match or fail predictive-coding alternatives? Scellier-Bengio equilibrium propagation is a relevant reference.
2. **Whether the multi-relation orthogonality result extends to learned relations.** Our experiment used hand-defined relations. Can the system *discover* useful relations from data, or does that require gradient descent?
3. **Whether pointer-chain HDC composes hierarchically.** Pointers-to-pointer-chains, or pointers-to-graphs. This would extend the depth-β=0 result to more complex memory structures.
4. **Whether Hebbian updates can implement in-context learning.** Transformers do meta-learning in their attention. Can a Hebbian-VSA do it in its connection matrix at inference time without explicit training?
5. **The role of sleep-replay analogues.** Brains consolidate via sleep. Should the system have offline replay phases that strengthen specific Hebbian patterns? Tied to continual-learning claim.
6. **Hardware co-design with specific silicon targets.** Track 0.2 found that fabricated HDC silicon today favors BSC (binary XOR-and-count). FHRR-friendly silicon doesn't exist because nobody has built it — but the substrate is real: phase-based photonic computing (Lightmatter, Lightelligence, Luminous) and multi-state memristor / PCM cells (IBM has demonstrated multi-bit) both natively represent the complex unit-modulus that FHRR uses. If our algorithm proves out, the right play is co-design — fabricate (or commission) chips that match the substrate we want, rather than constraining the algorithm to the simpler substrate that current chips happen to favor. We could potentially be the customer that justifies an FHRR-targeted fabrication run. Revisit after Track 0 decides whether the algorithm is alive.
7. **The "what is structure" question.** Multi-relation graph encodes structure explicitly. Pointer-chain encodes it via addressing. Transformers learn it implicitly. Is there a principled way to compare which form of structure-encoding wins for which data?
8. **Hyperbolic VSA on real hierarchical data.** Tangent-space failed; native hyperbolic operations untested. Worth one more experiment if any of the bets stalls.
9. **Information-theoretic lower bounds on Hebbian-VSA capacity.** Plate's analysis gives bundling capacity bounds. Are there analogous bounds for connection-matrix capacity that would predict where Bet B caps out?
10. **Whether observability scales.** At 100M connections, naive trace-everything will be infeasible. Sampling strategies, hierarchical traces, ablation-summary statistics — research question in its own right.

## Operating discipline

Inherited from `CLAUDE.md` and the build-phase discipline:

- Every new framework feature ships with at least one scaffold-free witness in `verification/`.
- Pre-register every experiment in `notes/expNN.md` before running. Re-read after; mark confirmed, surprised, or falsified.
- `python verification/run_certification.py` stays green on `main`.
- Decision gates have written kill criteria stated up front. Re-state probabilities at each gate.
- Honest reporting: if a bet stalls, write it up as a negative result rather than quietly pivoting.
