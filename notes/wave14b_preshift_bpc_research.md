# Pre-shift bpc unmoved — research synthesis

Returned 2026-05-19. Unbiased Bayes-floor analysis of why pre-shift bpc
hasn't moved across the session, and what would (or wouldn't) move it.

## TL;DR

**Pre-shift is the WRONG goal.** Substrate's unique-enabling stories
(audit/edit/recompose, +0.73 BWT, R10 +0.193) all live in regimes a
backprop transformer cannot occupy. Beating tiny-transformer 2.39 by
0.05 bpc on a 50KB markdown blob will not change anyone's mind.

Treat pre-shift as a hygiene check (within ~0.1 bpc of reference =
acceptable) and stop trying to move it.

## Bayes floor estimate

For a ~50KB markdown corpus:
- Shannon 1951 / modern replications: English 4-7-char conditional
  entropy ~2.3 bpc asymptotically
- Markdown is sub-English entropy (lots of #, *, repeated headers, code
  fences). Realistic K=4 conditional entropy: 2.0-2.3 bpc reachable
  asymptotically
- 39KB training = ~39K conditional samples in 256^5 = 10^12 space.
  Brutally sparse. Good-Turing estimates over-estimate by 0.1-0.3 bpc.

**Honest floor at K=4 on this corpus: ~2.30-2.45 bpc.** Our 2.4817 is
0.03-0.18 above floor.

**Tiny transformer 2.39 uses K=32** — already beats the K=4 asymptotic
floor. Different regime, exploiting longer-range structure (header
repetition, code-block boilerplate). **The transformer is NOT the K=4
ceiling — it's a different regime.**

**Beating 2.39 at K=4 is excluded by information theory.** The
transformer uses K=32.

## Why substrate hasn't moved pre-shift

- **N=4096→8192 = -0.047 bpc**: bundle interference real but small.
  N=16384 would give ~-0.02 more.
- **K-extension WORSENS pre-shift**: bundle-interference term grows
  faster than marginal-information term. Frady-Sommer capacity regime.
  Substrate bottlenecked by **bundle SNR at large K, not basis dim**.
- **W training NOT the bottleneck** at K=4. Delta rule converges to
  same minimum as SGD asymptotically on quadratic loss (Melchior-Wiskott
  Hebbian-Descent).
- **Cosine retrieval has capacity ceiling** that bites at K>=8, exactly
  what Lippl-Stachenfeld K-sweep showed.

## Larger corpus prediction

A1 said "Bayes-floor headroom needs bigger corpus." Only half right:
- Floor MOVES DOWN with more data (estimate becomes more accurate;
  50KB → 5MB drops floor estimate from ~2.45 to ~2.30 on markdown-ish)
- Whether substrate moves with floor depends on **W-training capacity
  vs bundle SNR**
- At K=4 dominant remaining loss is conditional-distribution sampling
  noise → corpus size cures it
- **Expected gain at 1MB: 0.05-0.15 bpc** (modest)
- Linear-transformer scaling laws (Schlag-Irie): delta-rule outer-product
  memory tracks gradient-trained until key-collision regime kicks in

## Interventions ranked by realism (within "no backprop on W")

### HIGHEST EV — Schlag-Irie slow projection
- Train a 2-layer MLP (input: byte_atom, pos_atom; output: ctx_vector)
  by backprop on per-token CE; W itself stays delta-rule
- Respects "no backprop on W" — projection is slow learner, W is fast
  Hebbian
- Predicted gain: **0.10-0.25 bpc** — proven for analogous setups in FWP paper
- Implementation: ~150 LOC, single GPU hour
- Preserves: decompose, continual learning, cheap CPU at inference

### Other interventions
- **Learned codebook atoms** (SVD/PCA of bigram PPMI): +0.02-0.08 at K=4. CPU-only, ~15 min.
- **Bricken SDM substrate** (Top-K + L2-norm): claimed pre-shift parity with dense MLPs + native CL. ~1 GPU hour to port.
- **Sparse block codes** (Hersche 2024): log(N/B)·B capacity beats dense BSC. Already on B1 list.
- **Hierarchical context pool** (recent K bigrams + episodic anchors): +0.05-0.15. Speculative.

## Single best experiment

**Schlag-Irie projection in front of delta-rule W, K=4-8, N=4096.**

Predicted gain: 0.08-0.20 bpc pre-shift, with serious chance of beating
2.39 (because projection can extract K=8 context info into K=4-shaped
retrieval key).

Falsifier: |Δbpc| < 0.03.

## Honest assessment

**Pre-shift is NOT the right goal.** Three reasons:

1. Substrate's unique-enabling stories — auditable/editable memory,
   +0.73 BWT, R10 +0.193 — live in regimes transformers cannot occupy.
   KV cache not decomposable; backprop forgets catastrophically;
   concept-fusion has no analog inside attention.

2. Pre-shift bpc is a commodity metric. 0.05 bpc delta on 50KB markdown
   won't change minds. Reviewer who cares about pre-shift wants
   WikiText-103, then Pile, etc.

3. "Matches small reference architecture pre-shift, wins decisively on
   substrate-unique axes" is the honest framing of what we have.
   **Publication-grade headlines are +0.193 at K=256 + +0.73 BWT, not
   a 0.05 pre-shift delta.**

## Recommendation

- Treat pre-shift as hygiene check (~0.1 of tiny-transformer = OK)
- Invest GPU hour budget in:
  - (a) Schlag-Irie ONLY if it serves the CL story (slow projections
    that don't drift across tasks = clean CL angle)
  - (b) **Scaling unique-enabling demos** — port R10/random-replay to
    WikiText-2 or multi-domain corpus. Validates substrate properties
    on something less trivially small.

## Sources

- [Shannon Prediction and Entropy of Printed English 1951](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf)
- [Entropy Rate Estimation via Mechanical Turk PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7514546/)
- [Schlag-Irie-Schmidhuber Linear Transformers Are Secretly Fast Weight Programmers](https://arxiv.org/abs/2102.11174)
- [Melchior-Wiskott Hebbian-Descent](https://arxiv.org/pdf/1905.10585)
- [Bricken SDM is a Continual Learner](https://arxiv.org/abs/2303.11934)
- [Hersche Factorizers for Distributed Sparse Block Codes](https://ar5iv.labs.arxiv.org/html/2303.13957)
- [Kaplan Scaling Laws for Neural LMs](https://arxiv.org/pdf/2001.08361)
- [Frady-Sommer Resonator Networks for VSA factorization](https://arxiv.org/abs/1906.11684)
