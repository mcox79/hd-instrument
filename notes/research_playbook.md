# Research playbook

Operational rules for this research program, distilled from the 2026-05-18
literature audit on small-team / fast-iteration / brain-inspired ML research.
This is a standing reference. Update with date when revising.

## The six standing practices

### 1. Pre-register every experiment

Before launching a run, write one file under `preregs/` named
`YYYY-MM-DD_short-slug.md`. Required sections:

- **Hypothesis (H):** one sentence.
- **Cited mechanism / paper:** which paper makes the prediction.
- **Operational definition (Carnap):** the literal code-level operation
  that implements the mechanism. If it does not match the paper, you have
  not yet pre-registered a faithful test.
- **Falsification criterion (Lakens machine-readable):** "If on benchmark B,
  with N≥k seeds, the effect size (delta or BF₁₀) is below threshold T,
  H is rejected."
- **Pre-mortem:** if this fails, the top-3 most likely causes. If "the
  hypothesis was wrong" is not in the top-3, the framing is unfalsifiable —
  rewrite before launching.
- **Parameter-matched non-bio control:** for any brain-inspired claim, name
  the parameter-matched non-biological alternative that this run will also
  measure. ("This is regularization in disguise" is the default null.)

Cited: Lakens & DeBruine 2021 *Making Hypothesis Tests Machine-Readable*;
Hofman et al. 2023 *Pre-registration for Predictive Modeling*; Klein
pre-mortem methodology.

### 2. Five-seed minimum, sequential Bayes factor stopping

Any claim of "X helped" must be replicated. Specifically:
- 3-seed minimum to enter the candidate pool.
- 5-seed minimum before promotion to "result" in the tracker.
- If effect shrinks >50% from 3-seed to 5-seed mean, treat as noise.
- For stopping: continue while 1/6 < BF₁₀ < 6, decide otherwise. BF₁₀ ≥ 6
  → promoted; BF₁₀ ≤ 1/6 → abandoned.

Cited: Schönbrodt et al. 2017; Pineau et al. 2021 NeurIPS reproducibility.

**Honest exception:** for our setup (minutes-to-hours per run, well-instrumented
streaming Hebbian), single-seed exploratory runs are still useful for
direction-setting. The rule applies before a result is *promoted* to the
tracker as "X works", not to all exploration.

### 3. Bandit framing for the two bets

Treat "small bet" (HDC memory for LLM) and "big bet" (Hebbian-VSA-LM) as
two arms of a Thompson-sampled bandit:
- ~80% of compute on the leading arm
- ~20% **permanently reserved** for the trailing arm with high posterior variance
- Quarterly written-rationale review using Hamming's "important problem" test:
  "What changes in the field if this experiment succeeds?"

Cited: Multi-armed bandit literature; Hamming 1986 *You and Your Research*;
Olah 2023 *Research Taste Exercises*.

### 4. Full design-space matrix, not single-axis ablation

Instead of "does X help?" runs, maintain a written full design space in
`notes/design_space.md`:
- Axes: substrate (FHRR/HRR/BSC/sparse), N (1024/4096/8192/16384),
  binding op (HRR/permutation/non-commutative), training rule
  (pure Hebbian/delta/DeltaNet/cleaned-delta), pool gate (none/surprise),
  modReLU on/off, K (2/4/8), pool size, decay schedule, etc.
- Fit a small surrogate (GP or random forest) on accumulated runs.
- Disagreement between surrogate prediction and a spot-check run is where
  new ideas hide.

Cited: Almaatouq et al. 2022 *Integrative Experiment Design*; Newell 1973
*20 Questions with Nature*.

### 5. Verify-against-cited-literature on every new experiment

The standing audit checklist (already in feedback memory):
1. Does the cited paper's mechanism literally match our code?
2. Is the cited paper's prediction quantitative? What value for our setup?
3. Is there a more recent (2022+) paper doing the same thing better?
4. Are we mis-applying a theorem outside its assumptions?
5. If biological, are we capturing the load-bearing property or just the surface analogy?

### 6. Two-week distillation cadence + weekly adjacent-field paper

The highest-yield idea-mining channels per the literature:
- **Biweekly:** write a 1-page summary of "what I now believe and why",
  including unresolved tensions. Forces compression which exposes gaps.
- **Weekly:** read one paper from an adjacent field (computational
  neuroscience, statistical physics, theoretical linguistics, control
  theory). Historical hit rate at the neuro-AI interface is very high.

Cited: Olah & Carter 2017 *Research Debt*; Sutton 2019 *Bitter Lesson* and
Nielsen/Beren critiques (structure × compute, not compute alone).

## What we explicitly reject

- **"Test set is sacred and untouched."** Reuse is fine if you formally
  update what you think you know. What kills you is reuse plus pretending
  the reuse didn't happen. (Devezer et al. 2021)
- **"Talk to more people."** Wildly oversold for small labs. Fewer, deeper
  conversations with people whose taste you have personally validated.
- **"Don't repeat published work."** Repeating with explicit prior-update
  accounting is fine; the bar is being honest about what we observed.

## Scale-invariant question test

Apply Hamming's "important problem" test in scale-invariant form. Good
questions for us:
- "Does Hebbian-trained VSA produce different representation geometry than backprop?"
- "Does HDC-shaped memory change LM behavior at fixed parameter count?"
- "Are there functional capabilities (continual learning, few-shot ICL) where
  HDC-LM outperforms parameter-matched transformer?"

Bad questions (scale-dependent, unanswerable for us):
- "Does this beat GPT-4 perplexity?"
- "Does this scale to 1B+ params?"

## When to abandon a research thread

Combine items 2 + 5:
- BF₁₀ ≤ 1/6 across 5 seeds → abandon at experiment level
- Three consecutive abandoned experiments in same thread → quarterly review
- If thread fails Hamming's important-problem test → demote to 20% explore bucket

## Rehabilitation pass after rejection (standing practice, added 2026-05-18)

A single-axis rejection rejects the **configuration**, not the **mechanism**.
At the moment of rejection, BEFORE updating the tracker with "X failed":

1. Write 3-5 axis-combination rescue candidates directly in the pre-reg or
   tracker entry. Specifically:
   - Scale axes (N, corpus size, pool size, batch)
   - Hyperparameter neighbors (α, β, decay, threshold)
   - Complementary mechanisms (paired with delta-rule erase, paired with
     a different substrate, paired with surprise gate, etc.)
   - Implementation faithfulness check (did we match the paper's actual
     operating point and signal definition?)

2. Decision rule:
   - If 2+ candidates look non-trivial, queue at least one rehabilitation
     experiment.
   - If rehabilitation is expensive (large compute), defer and tag in
     design space for Wave 2/3.
   - If 0 candidates look promising, abandon and note "no plausible
     rehabilitation paths within current scale" in tracker.

3. Track BOTH layers separately: "configuration X failed" vs. "mechanism Y
   abandoned." Cite the rehabilitation candidates considered. The literature
   nearly always reports gains at specific operating points, not universally —
   our rejections must respect this asymmetry.

## Brain-closer basis as a primary axis (added 2026-05-18)

The substrate itself is a research axis, not a fixed setup. If FHRR keeps
hitting a floor across all the architecture variants we test, the substrate
itself may be the limiting factor — and brain-closer substrates may have
different limits. Specifically:

- **BSC (Binary Spatter Codes)** — XOR-binding, cortical-map-like geometry
- **Sparse Block Codes (Laiho 2015)** — k-WTA structured sparsity, more
  like cortical population activity than dense complex phasors
- **GHRR non-commutative binding (Alam-Raff 2024)** — captures sequence
  order natively without external position codes
- **Grid-cell positional codes (Frady-Kanerva-Sommer 2018)** — entorhinal-like
  (we tested BR5 at K=4, slight hurt; should retry at K=16+)
- **Spiking-network HD codes (Frady-Sommer 2020)** — discrete event substrate

These are **substrate experiments**, not architecture variants on top of
FHRR. They belong in the experimental priority list at the same tier as
architecture-on-FHRR experiments, not below them. Specifically, after each
Wave of FHRR architecture experiments, before doubling down on more FHRR
variants, run at least one substrate-switch experiment to test if the floor
is FHRR-specific.
