# Research R12 — Sampling rescues for autoregressive repetition collapse (Bet H prerequisite)

**Topic.** Strategy's Bet H (NEW cycle 14, 🟡-rehab-routed):
`wave14yy_autoregressive_generation` showed multi-step generation
collapses to "  e  e  e..." (char_entropy = 0.917, ngram_repetition = 1.000)
under α=1.0, β=8, single seed. The K=16 strict-baseline PASS measured
*single-position* prediction; multi-step autoregressive generation is
the new failure mode. R12 asks: which sampling-time methods prevent
repetition collapse in cosine-similarity-readout retrieval generation,
ranked by predicted char_entropy improvement? Per rehab-routing protocol,
this note GENERATES the ranking independently rather than vetting
Strategy's 5 draft sketches.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 18 tool uses,
18+ verified citations 2018-2026). Sixth consecutive cycle following
the post-audit protocol.

---

## Pass 1 — External literature scan (verified)

Generic-NLP / sampling queries via subagent: "neural language model
sampling repetition collapse," "nucleus sampling top-p Holtzman,"
"mirostat perplexity control," "contrastive decoding," "repetition
penalty," "language model degeneration mode collapse," etc. No
substrate fingerprint.

### 1.1 The repetition-collapse mechanism

**Holtzman et al. 2019** (arXiv:1904.09751, "The Curious Case of Neural
Text Degeneration") is the foundational diagnosis. **Maximization-based
decoding (greedy, beam) produces text stuck in repetitive loops** even
when the model is well-trained. The probability distribution has an
unreliable long tail; maximization concentrates onto attractor tokens.

**Welleck et al. 2020** (arXiv:1908.04319, "Unlikelihood Training")
sharpens at training level: MLE objective assigns too much probability
to sequences containing repeats and frequent tokens.

**"Repetitions are not all alike"** (arXiv:2504.01100, 2025)
distinguishes mechanism types: **degenerate loops** (stable fixed
points the model cannot escape) vs **local echoing** (mode-collapse-like).

**For cosine-similarity-readout substrate**: the **degenerate-loop /
fixed-point framing is load-bearing**. The cosine-similarity argmax IS
a literal fixed point of the dynamics — once context lands near a stored
value, next-step context is barely perturbed, same neighbor wins again,
trajectory blows up the bias. **Worse than softmax LMs structurally**
because softmax has a continuous distribution underneath; pure retrieval
has Dirac-like mixture over codebook entries.

### 1.2 Canonical sampling toolkit

**Top-k** (Fan 2018, arXiv:1805.04833): keep k highest-probability,
renormalize. Standard k=40 word, k=10 char.

**Top-p / Nucleus** (Holtzman 2019): smallest set with cumulative
prob ≥ p. Standard p ∈ [0.9, 0.95]. Beats top-k on diversity/coherence
because **k is too rigid** — at high-entropy steps under-samples
diversity, at low-entropy over-samples noise.

**For substrate** (cosine readout): **top-k is more natural** — "keep
k nearest neighbors, sample weighted by similarity." Top-p harder to
define because cosine doesn't naturally normalize to probability.

### 1.3 Repetition / frequency / presence penalty

**CTRL** (Keskar 2019, arXiv:1909.05858) repetition penalty: divide
logits of previously occurring tokens by θ > 1. Recommended **θ = 1.2**.

**OpenAI GPT-3** frequency penalty: subtract α × count.
**Presence penalty**: subtract β × 1[token appears]. Typical
range 0.5–1.0.

**Quantitative limit**: "frequency and repetition penalty leave 4%+
degenerate-repetition rate on reasoning tasks under greedy" — partial
fix, not complete.

For char-level: **smaller θ (1.05–1.15)** because legitimate character
repetitions ('ee', 'll', 'oo') shouldn't be blocked; **shorter lookback
window** (64–128 chars) instead of full sequence.

### 1.4 Mirostat — adaptive entropy servo

**Basu et al. ICLR 2021** (arXiv:2007.14966, "Mirostat"): feedback-
controlled adaptive top-k that tunes k each step to hit target *surprise*
(cross-entropy) τ. **Directly controls perplexity** of output, avoiding
the loop-vs-incoherence trade-off of fixed-k/p.

Standard τ ∈ [3, 5] bits. For substrate at char_entropy=0.917,
**Mirostat-style control with τ≈4 would force truncation to widen
until entropy recovers**.

### 1.5 Contrastive decoding

**Li et al. 2023** (arXiv:2210.15097, "Contrastive Decoding"): score by
log p_expert − log p_amateur. Subtracts the part of distribution most
responsible for collapse.

**DoLa** (arXiv:2309.03883): layer-contrast; early-layer logits as amateur.

For substrate, **natural amateur is uniform sampling over codebook**
or **identity-readout** (skipping retrieval) — contrast removes "any
entry will do" bias.

### 1.6 Locally typical sampling

**Meister et al. TACL 2023** (arXiv:2202.00666): restricts sampling to
tokens with negative-log-prob within τ-band of local conditional entropy.
Information-theoretic alternative to nucleus.

### 1.7 LZ penalty (2025 SOTA)

**Ginart et al. 2025** (Salesforce, arXiv:2504.20131, "LZ Penalty: An
Information-Theoretic Repetition Penalty"): sliding-window LZ77
codelengths over generation context. **Reports: "frequency and
repetition penalties fail at 4%+ rate on reasoning tasks under greedy,
while LZ penalty enables greedy decoding without degenerate loops."**

This is the strongest published 2024-26 result on degenerate-repetition
prevention. Algorithm: at each step, scale token probability inversely
by LZ77-codelength of (last_k_tokens + candidate_token). Tokens that
would extend an existing pattern get downweighted proportionally to
how much they compress.

### 1.8 Beam search and its failure modes

**Stahlberg-Byrne EMNLP 2019** (arXiv:1908.10090, "On NMT Search Errors
and Model Errors"): the **beam search curse** — with exact search,
**>50% of NMT models prefer the empty translation**, so beam search
helps by failing.

**Diverse Beam Search** (Vijayakumar 2016, arXiv:1610.02424): partitions
beams into groups, penalizes inter-group overlap. Doesn't fix collapse,
adds diversity.

For substrate: **beam search is not useful** in the conventional sense
— beam expansion doesn't escape cosine attractor; every beam path
lands in same basin. Diverse beam search slightly more useful because
diversity penalty acts as explicit anti-collapse force.

### 1.9 Min-p sampling — contested 2024-25 literature

**Nguyen et al. ICLR 2025 Oral** (arXiv:2407.01082, "Min-p Sampling"):
keep tokens with p ≥ p_base × max(p). Claimed to beat top-p at high
temperature.

**arXiv:2506.13681** (2025, "Min-p, Max Exaggeration"): critical
re-analysis. Finds **min-p does NOT improve quality/diversity vs
well-tuned top-p** when hyperparameter parity is enforced.

Honest read: contested literature. Don't bet on min-p without your
own evaluation.

### 1.10 The substrate-specific literature gap

**No published paper studies sampling from a pure-retrieval readout**
without parametric LM interpolation. kNN-LM (Khandelwal 2020) avoids
collapse by interpolating p = λ·p_kNN + (1-λ)·p_LM with λ≈0.25 —
the parametric LM dominates generation entropy.

**Image-retrieval generation** (DALL-E-style) injects ε-noise on the
embedding between steps to prevent same-context-same-retrieval. The
transferable insight: **query-vector dithering** is the cosine-readout
analog of softmax temperature.

**RAG diversity literature**: "Guided Decoding for RAG"
(arXiv:2509.06631) reports **diversity in retrieval (MMR, cluster-then-
sample, Speculative RAG) matters more than diversity in token sampling**.

### 1.11 Materials-science / physics analog (LOAD-BEARING)

The mapping is exact and direct:

- **Repetition collapse = attractor capture** in a discrete dynamical
  system. The cosine-similarity readout defines an energy landscape
  E(s) = −similarity(s, codebook); greedy retrieval is gradient descent
  on E.
- **Sampling = thermal noise**. Temperature T in softmax sampling is
  literally inverse-β of a Boltzmann distribution over logits.
- **Mode collapse = local-minimum trapping**. The Boltzmann/MCMC
  literature has a 50-year solution: simulated annealing (Kirkpatrick
  1983), replica exchange / parallel tempering, basin-hopping.
- **Hopfield/dense-AM analog is direct**: Hopfield at T=0 retrieves
  nearest pattern; at T>0 samples Gibbs distribution and **escapes
  spurious fixed points**. Modern dense associative memories (Ramsauer
  2020, arXiv:2008.02217) make this explicit.
- **2026 paper**: "Thermal Robustness of Retrieval in Dense Associative
  Memories" (arXiv:2603.13350) explicitly studies the retrieval-vs-
  temperature trade-off for LSE vs LSR kernels.

**Substrate-prediction consequence**: the right framing is NOT "what
NLP sampling method do I use" but **"what temperature/noise schedule
keeps the cosine readout from being trapped in spurious fixed
points."** Mirostat, min-p, typical sampling are all special cases of
"control the effective β." The Hopfield literature tells you the
**critical temperature T_c** above which retrieval fails gracefully
(stochastic) and below which it locks. **Substrate should operate
just above T_c.**

This is the load-bearing materials analog: the prediction
(operate just above T_c) is quantitatively derived from the
Hopfield-AM framing, not decorative.

### 1.12 Pass-criterion benchmarks

- Holtzman 2019: nucleus p=0.95 vs greedy → diversity / coherence
  measured by zipf-coefficient and perplexity-vs-human.
- Welleck 2020: repetition reduction from 0.6+ → ~0.1 with unlikelihood
  training.
- LZ penalty (2025): degenerate-repetition rate 4%+ → ~0% with LZ
  penalty + greedy.
- Mirostat: directly hits target perplexity within ±0.5 bits typically.

**Substrate target** (per Bet H multi-probe success criteria):
- char_entropy ≥ 2.5 (over 512 chars; current 0.917)
- ngram_repetition ≤ 0.5 (4-grams; current 1.000)
- self_bpc < 4.0
- 3 seeds minimum

---

## Pass 2 — Substrate-specific drill (independent rescue ranking)

Per rehab-routing protocol, I generate the ranking from first principles
+ lit scan, not from Strategy's draft.

### 2.1 The substrate's specific failure mode

Substrate generation pipeline:
1. Maintain context (last K bytes as bundle representation).
2. Compute cosine to all stored codebook values.
3. Argmax → emit byte.
4. Append to context; truncate to last K; repeat.

**Where collapse happens**: step 3 (argmax). The cosine readout has
NO randomness — same context always produces same byte. Combined with
the bundle representation being slowly-changing across single-byte
extensions, the trajectory locks into a periodic attractor.

**Mathematically**: bundle representation B at step t is
B_t = bundle(byte_{t-K}, ..., byte_t). Replacing byte_t with the just-
emitted byte changes B only slightly (1/K weight on the new byte).
So argmax(cosine(B_{t+1}, codebook)) = argmax(cosine(B_t, codebook))
with high probability. Result: same byte emitted repeatedly.

**This is the textbook fixed-point attractor.**

### 2.2 Independent rescue ranking (9 candidates)

Ranking criteria: (a) **predicted char_entropy lift** (0.917 → ≥ 2.5);
(b) **implementation cost**; (c) **substrate-coherence** (works with
existing infrastructure); (d) **literature anchor** (published validated >
folklore); (e) **mechanism-level vs symptom-level**.

| Rank | Candidate | Mechanism | Predicted char_entropy after | Cost | Substrate-coherent | Literature anchor |
|---|---|---|---|---|---|---|
| **1** | **Query-vector dithering (substrate-novel)** | Mechanism: thermal noise on context vector | **2.5–3.5** | Trivial (Gaussian noise σ=0.01-0.05) | YES (no infra change) | Hopfield T>0 (arXiv:2008.02217); image-retrieval ε-noise folklore |
| **2** | **LZ penalty (Ginart 2025)** | Mechanism: degenerate-loop targeted penalty | **2.8–3.5** | Low (sliding LZ77 over context) | YES (just modify cosine before argmax) | arXiv:2504.20131 (2025 SOTA on greedy degeneracy) |
| **3** | **Mirostat-style entropy servo (Basu 2021)** | Mechanism: adaptive entropy targeting | **2.5–3.5** | Medium (running entropy estimate + adaptive k) | YES | arXiv:2007.14966 (ICLR 2021) |
| **4** | **Top-k + softmax(cosine/T) sampling** | Symptom: add randomness | 2.0–3.0 | Low (k=10, T tuned) | YES | Fan 2018 (top-k); standard recipe |
| **5** | **Repetition penalty θ=1.05–1.15 + sliding window** | Symptom: anti-repetition | 2.0–2.8 | Low (lookback over last 64-128 chars) | YES | Keskar 2019 (CTRL); char-level folklore |
| **6** | **Combined: dithering + LZ + temperature** | Mechanism + Symptom layered | **3.0–4.0** | Medium (compose 1+2+4) | YES | Synthesis; no single published precedent |
| **7** | **Contrastive decoding (uniform amateur)** | Mechanism: subtract collapse mode | 2.0–3.0 | Medium (compute uniform-cosine readout) | YES | Li 2023 (arXiv:2210.15097); unproven at substrate scale |
| **8** | **Nucleus / top-p (requires cosine→prob)** | Symptom: probability truncation | 1.5–2.5 | High (need cosine renormalization) | Low — cosine isn't probability | Holtzman 2019; doesn't port cleanly |
| **9** | **Diverse beam search** | Symptom: structural diversity | 1.5–2.5 | High (multi-trajectory tracking) | Low — doesn't escape attractor | Vijayakumar 2016 |

**Top recommendation: Candidate 6 (combined dithering + LZ + temperature)**
as the production rescue, with **Candidate 1 (query-vector dithering)
alone** as the smoke test to confirm the materials-physics framing.

### 2.3 Reordering vs Strategy's draft

Strategy's 5 sketches:
1. β tuning → already done as part of TS calibration (Bet G resolved);
   relates to my #4 (cosine/T temperature in sampling).
2. top-p → my **#8 (down)** — cosine isn't probability without
   renormalization; doesn't port cleanly.
3. repetition penalty → my **#5** ✓
4. multi-seed → not strictly anti-collapse; gives diversity across
   runs not within a run. Below my #9 in ranking.
5. prefix selection → engineering trick; not in my ranking (initial
   conditions, not sampling-time).

**Strategy missed**:
- **Query-vector dithering (my #1)** — substrate-novel materials-
  physics rescue.
- **LZ penalty (my #2)** — 2025 SOTA on degenerate loops.
- **Mirostat (my #3)** — direct entropy servo, most principled.
- **Contrastive decoding (my #7)** — promising but unproven.

### 2.4 Drill on Candidate 1 — Query-vector dithering (substrate-novel)

**The substrate-specific math**:

Standard substrate generation step:
```text
B_t = bundle(byte_{t-K}, ..., byte_t)  # context bundle
y = W @ B_t  # readout
scores = cosine(y, codebook)  # cosine to all stored values
emit = argmax(scores)
```

With dithering:
```text
B_t = bundle(byte_{t-K}, ..., byte_t)
B_t_noised = B_t + noise(sigma)  # Gaussian noise σ ∈ [0.01, 0.05]
y = W @ B_t_noised
scores = cosine(y, codebook)
emit = argmax(scores)  # or softmax sampling if combined with #4
```

**Why σ ∈ [0.01, 0.05] is the right range**: substrate's cosine
scores typically cluster at 0.3–0.5 (per R11 finding). To meaningfully
perturb argmax, noise must shift cosine by at least the gap between
top-1 and runner-up — typically 0.05–0.10. By linearity of cosine,
noise of σ ≈ 0.02–0.04 on the query vector translates to ~0.02–0.10
cosine perturbation. Choose σ in this range; tune per-corpus.

**Why this is the cleanest first test**: zero new code, zero new
hyperparameters beyond σ, zero changes to storage/binding. If σ=0.02
restores char_entropy to ≥ 2.5, the entire Bet H closes ✅ on the
materials-physics prediction alone.

**Substrate-coherence**: query-vector noise is the literal thermal-
noise analog from Hopfield T>0 retrieval. The substrate operates at
implicit T=0 (deterministic cosine); dithering raises effective T.

**Predicted char_entropy**: 2.5–3.5 (5-seed mean). The wide range
reflects σ-tuning uncertainty.

### 2.5 Drill on Candidate 2 — LZ penalty (2025 SOTA)

**The substrate-specific math**:

LZ77-based penalty against the generation history. At step t:
```text
context_history = bytes_{t-W:t}  # sliding window, W=64-128
for each candidate_byte c:
  candidate_extension = context_history + [c]
  lz_codelength = LZ77_encode_length(candidate_extension) -
                  LZ77_encode_length(context_history)
  # tokens that extend existing patterns have smaller codelength
  penalty[c] = alpha * (1 / lz_codelength)  # smaller codelength = bigger penalty
scores_adjusted = scores - penalty
emit = argmax(scores_adjusted)
```

**Why this targets degenerate loops specifically**: LZ77 codelength is
short exactly when the candidate extends an existing repeating pattern.
"  e  e  " gets a tiny LZ-codelength for the next "  e" — therefore
big penalty — therefore argmax shifts to a different byte.

**Substrate-coherence**: modifies cosine scores before argmax; no
substrate change. Just adds a per-step computation over the last 64-128
bytes.

**Predicted char_entropy**: 2.8–3.5. Per the Ginart 2025 paper, LZ
penalty "enables greedy decoding without degenerate loops" — the
substrate's current failure mode is precisely greedy decoding under
degeneracy.

**Honest caveat from lit scan**: LZ penalty results are from a single
2025 paper on reasoning tasks. Substrate's regime (byte-level retrieval
generation) is different. The reasoning behind the prediction is
mechanism-level (degenerate loops have short LZ codelengths by
definition) and should hold, but specific numerical thresholds need
empirical confirmation.

### 2.6 Drill on Candidate 6 — Combined rescue

```text
combined_generation_step:
  B_t = bundle(byte_{t-K}, ..., byte_t)
  # Layer 1: dithering
  B_t_noised = B_t + gaussian_noise(sigma=0.02)
  # Substrate readout
  y = W @ B_t_noised
  scores = cosine(y, codebook)
  # Layer 2: LZ penalty
  for c in candidates:
    lz_score = compute_lz_penalty(c, history_window)
    scores[c] -= alpha_lz * lz_score
  # Layer 3: temperature + top-k sampling
  top_10 = top_k(scores, k=10)
  probs = softmax(top_10 / temperature)
  emit = sample(probs)  # stochastic, not argmax
```

**Why combine**: each layer addresses a different failure mode:
- Dithering: prevents same-context-same-retrieval (mechanism).
- LZ penalty: prevents extending detected loops (targeted symptom).
- Temperature sampling: ensures even when noise + LZ produce close
  candidates, some randomness chooses.

Per the lit scan: "**for a cosine-similarity readout that's collapsing
under greedy, the LZ penalty + query-vector dithering is the highest-
leverage combination**, because LZ specifically targets degenerate
loops without hurting capability, and dithering is the structural
analog of temperature for retrieval readouts."

**Predicted char_entropy**: 3.0–4.0 (5-seed mean). The combined
approach should clear Bet H's ≥ 2.5 threshold with margin.

---

## Specific experimental design (pseudocode)

**Experiments**: Run THREE parallel rescues at smoke scale, then escalate
top-performer to full multi-seed.

### Experiment A — `wave14_R12_dithering_v1` (primary, simplest test)

```text
config:
  N = 4096
  K = 16  # match Bet H's K
  M_stored = 627  # current substrate operating point
  sigma_sweep = [0, 0.01, 0.02, 0.04, 0.08]  # σ=0 is greedy baseline
  seeds = [7, 17, 23, 31, 41]
  prefix = "the quick brown fox jumps over"  # standard prefix
  gen_length = 512  # bytes

generation_step(B_t, sigma):
  B_t_noised = B_t + np.random.normal(0, sigma, N)
  y = W @ B_t_noised
  scores = cosine(y, codebook)
  return argmax(scores)

evaluate_per_seed(seed, sigma):
  set_random_seed(seed)
  gen = list(prefix.bytes)
  for _ in range(gen_length):
    B = bundle(gen[-K:])
    next_byte = generation_step(B, sigma)
    gen.append(next_byte)

  char_entropy = compute_char_entropy(gen)
  ngram_rep = compute_ngram_repetition(gen, n=4)
  self_bpc = substrate.bpc(gen)
  return char_entropy, ngram_rep, self_bpc

verdict_logic:
  PASS iff:
    char_entropy >= 2.5 across 5 seeds  # Bet H criterion
    ngram_rep <= 0.5 across 5 seeds
    self_bpc < 4.0
    accuracy on stored facts (sanity) >= 0.90

  STRONG PASS iff:
    char_entropy >= 3.0 AND ngram_rep <= 0.3
```

### Experiment B — `wave14_R12_LZ_v1` (2025 SOTA published method)

```text
LZ penalty implementation per Ginart 2025:
  history_window = 64
  alpha_lz = 1.0  # tune in {0.5, 1.0, 2.0}

  At each step:
    lz_baseline = LZ77_encode_length(generated_bytes[-history_window:])
    for each candidate_byte c:
      lz_extended = LZ77_encode_length(generated_bytes[-history_window:] + [c])
      delta = lz_baseline + 8 - lz_extended  # 8 = 1 byte = 8 bits
      # delta is small if c extends existing pattern
      penalty[c] = alpha_lz / max(delta, 0.5)
    scores_adjusted = cosine_scores - penalty
    emit = argmax(scores_adjusted)
```

Same evaluation as Experiment A.

### Experiment C — `wave14_R12_combined_v1` (highest predicted lift)

Layers: dithering + LZ + temperature sampling (per Candidate 6 pseudocode
above). Three hyperparameters: σ=0.02, alpha_lz=1.0, T=0.8, k=10.

### Smoke test (queue_add gate)

K=8, N=512, M_stored=64, gen_length=64, 1 seed. Target ~5s.
Oracle assertions: char_entropy at sigma=0 ≈ baseline (replicates
failure); char_entropy at sigma=0.05 > sigma=0 by ≥ 0.5 (dithering
helps even at smoke scale).

### Self-test (4 synthetic cases)

- Pristine retrieval (no collapse possible, designed test data):
  predict char_entropy = baseline, sigma adds modest noise.
- Designed collapse trap (codebook with 1 dominant cosine attractor):
  predict baseline char_entropy → 0; dithering recovers proportional to σ.
- Pure random codebook (no real text structure): predict char_entropy
  high but garbled output.
- Char-aware codebook (designed for valid bigrams): predict char_entropy
  3.5-4.0 even at baseline; dithering doesn't change much.

### Wall budget

3 experiments × 5 seeds × ~30s per seed = ~8 min at full scale.
Smoke ~5s each. Total ~25 min total compute including overhead.

---

## Materials analog (load-bearing — Hopfield T>0 thermal escape)

**The mapping is direct and quantitatively predictive.**

The substrate's cosine-similarity readout defines an energy landscape:
  **E(B) = −max_i cosine(W·B, v_i)**

Greedy retrieval = gradient descent on E. The substrate's failure mode
(repetition collapse) is **attractor capture**: trajectory falls into
a local minimum of E and stays there.

**The Hopfield/dense-AM literature solves this exact problem.** At T>0,
Hopfield retrieval samples a Gibbs distribution `p(s) ∝ exp(−βE(s))`.
At sufficiently high T, the substrate samples broadly across attractor
basins (failure mode: incoherent output). At sufficiently low T,
substrate locks into one basin (failure mode: repetition collapse,
substrate's current state). **Operating just above T_c (the
ferromagnetic-paramagnetic transition) gives stochastic retrieval that
escapes spurious fixed points while preserving the correct basin
structure.**

**The Hopfield T_c prediction at substrate's α=0.153 operating point**
(per Amit-Gutfreund-Sompolinsky 1987): T_c ≈ 0.5 - 0.7 (in units of
ferromagnetic exchange). Translating to query-vector noise:
σ_optimal ≈ T_c / √(N·α) ≈ 0.5 / √(626) ≈ **0.02**.

**This is the load-bearing prediction**: dithering σ ≈ 0.02 should
work, derived from Hopfield physics, NOT a tuning artifact.

Recent reference: **arXiv:2603.13350** (2026, "Thermal Robustness of
Retrieval in Dense Associative Memories") explicitly studies the
retrieval-vs-temperature trade-off. The substrate's R12 work could be
the first published characterization of LM-generation-from-retrieval
at T just above T_c.

---

## Falsifiable prediction

**Primary prediction (Experiment A, query-vector dithering):**

At N=4096, K=16, M_stored=627, prefix="the quick brown fox jumps over",
gen_length=512, 5 seeds:

- σ=0 (greedy baseline): char_entropy ≈ 0.9 (replicates Bet H failure),
  ngram_rep ≈ 1.0.
- **σ=0.02**: char_entropy **2.5–3.5**, ngram_rep **0.2–0.5**.
- σ=0.04: char_entropy **3.0–4.0**, ngram_rep **0.1–0.3**.
- σ=0.08: char_entropy **3.5–4.5** (approaching baseline-shuffled),
  ngram_rep ≈ 0.1, **but**: self_bpc starts to degrade (noise too
  high disrupts retrieval).
- **Sweet spot at σ=0.02–0.04** based on Hopfield T_c prediction.

**Stress prediction (Experiment B, LZ penalty):**

- char_entropy **2.8–3.5**, ngram_rep **0.05–0.20** (LZ penalty
  specifically targets ngram repetition).
- self_bpc preserved at baseline.

**Combined prediction (Experiment C):**

- char_entropy **3.0–4.0**, ngram_rep **0.1–0.3**, self_bpc < 3.5.
- Closes Bet H ✅ with margin above ≥ 2.5 threshold.

**Kill criterion.**

If Experiment A at σ=0.04 fails to achieve char_entropy > 2.0:
- The Hopfield-T_c materials prediction is wrong direction; dithering
  isn't sufficient.
- Escalate to Experiment B (LZ penalty); if that also fails, Bet H
  closes ❌-with-rehab-discipline. The substrate has structural
  generation limits the sampling-side fixes can't reach.

**Falsifier for Hopfield-T_c prediction**:

If optimal σ is far from 0.02 (e.g., σ=0.001 is enough, or σ > 0.10 is
needed): the substrate's effective T_c is much smaller/larger than
Hopfield theory predicts. Would warrant investigation of why
substrate-specific T_c differs from Amit-Gutfreund-Sompolinsky
prediction.

**Honest probabilities**:
- P(Experiment A passes char_entropy ≥ 2.5 at some σ) ≈ **70–80%** —
  the materials analog is direct.
- P(Experiment B passes) ≈ **65–75%** — Ginart 2025 published precedent.
- P(combined Experiment C passes at ≥ 3.0) ≈ **75–85%**.
- P(any of three rescues passes Bet H criteria) ≈ **85–90%** —
  multi-method redundancy.

---

## Citations

1. **Holtzman et al. (2019). "The Curious Case of Neural Text
   Degeneration."** ICLR 2020. arXiv:1904.09751.
   — Foundational diagnosis; introduces nucleus sampling. Mechanism
   reference for substrate's failure mode.

2. **Welleck et al. (2020). "Neural Text Generation with Unlikelihood
   Training."** arXiv:1908.04319.
   — Training-time fix; not directly applicable to substrate's
   inference-time problem but provides mechanism reference.

3. **Fan, Lewis, Dauphin (2018). "Hierarchical Neural Story Generation."**
   arXiv:1805.04833.
   — Top-k sampling foundational paper.

4. **Keskar, McCann, Varshney, Xiong, Socher (2019). "CTRL: A Conditional
   Transformer Language Model for Controllable Generation."**
   arXiv:1909.05858.
   — Repetition penalty foundational (θ≈1.2).

5. **Basu, Ramachandran, Keskar, Varshney (2021). "Mirostat: A Neural
   Text Decoding Algorithm that Directly Controls Perplexity."**
   ICLR 2021. arXiv:2007.14966.
   — Adaptive entropy servo. Direct anti-collapse mechanism.

6. **Li, Holtzman, Fried, Liang, Eisner, Hashimoto, Zettlemoyer, Lewis
   (2023). "Contrastive Decoding: Open-ended Text Generation as
   Optimization."** ACL 2023. arXiv:2210.15097.
   — Expert-minus-amateur scoring; subtracts collapse mode.

7. **Ginart, et al. (2025). "LZ Penalty: An Information-Theoretic
   Repetition Penalty for Autoregressive Language Models."** Salesforce.
   arXiv:2504.20131.
   — **2025 SOTA on degenerate-repetition prevention.** "Frequency and
   repetition penalties fail at 4%+; LZ enables greedy without
   degenerate loops."

8. **Meister, Pimentel, Wiher, Cotterell (2023). "Locally Typical
   Sampling."** TACL. arXiv:2202.00666.
   — Information-theoretic alternative to nucleus.

9. **Khandelwal, Levy, Jurafsky, Zettlemoyer, Lewis (2020).
   "Generalization through Memorization: Nearest Neighbor Language
   Models."** ICLR 2020. arXiv:1911.00172.
   — kNN-LM; reference for "interpolation prevents collapse" baseline.

10. **Ramsauer et al. (2021). "Hopfield Networks Is All You Need."**
    ICLR 2021. arXiv:2008.02217.
    — Modern dense AM; explicit temperature parameter in attention.
    Materials anchor for query-vector dithering rescue.

11. **(2026). "Thermal Robustness of Retrieval in Dense Associative
    Memories."** arXiv:2603.13350.
    — Recent characterization of retrieval-vs-temperature trade-off.
    Directly substrate-relevant.

12. **Amit, Gutfreund, Sompolinsky (1987). "Statistical Mechanics of
    Neural Networks Near Saturation."** *Ann. Phys.* 173, 30.
    — Classical T_c prediction for Hopfield at finite α; provides
    σ_optimal prediction.

---

## Routing

- **Experiment Dev (E_H)**: this note recommends THREE parallel
  experiments:
  - **`wave14_R12_dithering_v1`** (primary, materials-physics test)
  - **`wave14_R12_LZ_v1`** (2025 SOTA control)
  - **`wave14_R12_combined_v1`** (highest predicted lift)
  Total ~25 min at full scale. Smoke ~5s per variant.

- **Strategy**: this note GENERATES rescue ranking independently per
  rehab-routing protocol. Reordering vs Strategy's draft: my #1
  (dithering) and my #2 (LZ penalty) and my #3 (Mirostat) were ALL
  missing from Strategy's draft. β-tuning is closely related to my
  #4. Repetition penalty matches my #5. top-p, multi-seed, prefix
  selection were downranked or excluded. Proposes cap_map row update:
  "Substrate autoregressive generation rescue via query-vector
  dithering" at 🔬 (experimental design ready). On positive verdict:
  Bet H closes ✅; the materials-physics framing (Hopfield T just
  above T_c) becomes published methodology.

- **Research (this session, future cycles)**: if Experiment A passes
  at σ≈0.02 (Hopfield T_c prediction validated): R12 closes ✅ with
  a publishable materials-physics framing — substrate becomes "the
  first published characterization of LM-generation-from-retrieval
  at T just above T_c." If Experiment A fails but B (LZ) passes:
  pragmatic engineering solution; less materials-physics elegance.
  If all three fail at the ≥ 2.5 threshold: substrate has structural
  generation limits beyond sampling-time fixes — escalate to a
  redesign of the readout layer (R13 candidate).
