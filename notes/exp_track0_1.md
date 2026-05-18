# Pre-registration: Track 0.1 — pure Hebbian-VSA character LM feasibility probe

**Date pre-registered:** 2026-05-17 (before running the experiment)
**Experiment file:** `experiments/exp_pure_hebbian_charlm.py`
**Decision gate this feeds:** Track 0 decision matrix in `NEXT_PHASE.md` — specifically, the row for Bet B viability.

## Question

Can pure Hebbian-trained outer-product VSA do any conditional next-byte prediction on natural English text — better than a frequency-only unigram baseline, ideally competitive with low-order n-grams?

This is the kill-switch test for Bet B (Hebbian-trained VSA-LM from scratch). If the architecture cannot beat unigram baselines at byte-level prediction on a tiny corpus, it almost certainly cannot scale to LLM-class capability. If it can match or beat 3-gram, the architecture is showing signs of learning conditional structure, and Bet B is alive enough to merit further investment.

## Architecture under test

- **Substrate:** FHRR, complex64, N = 4096.
- **Vocabulary:** 256 byte-level atoms (one FHRR atom per byte), drawn IID from the FHRR distribution, fixed for the duration of the run.
- **Position atoms:** K position-role atoms, one per slot in the context window, fixed.
- **Context representation:** for context bytes b_{t-K}, ..., b_{t-1}, form the bundle `c_t = sum_{k=0..K-1} bind(byte_atom[b_{t-k-1}], position_atom[k])`, per-component normalized (standard FHRR bundling).
- **Connection matrix W:** complex64 of shape (N, N). Initialized to zero. This is the only thing that gets updated.
- **Forward (prediction):**
  1. `q_t = (W @ c_t.conj()) / N` (one matrix-vector multiply; conceptually "unbinding W against context").
  2. For each byte b, `score[b] = real(byte_atom[b].conj() @ q_t) / N`.
  3. `P(b | c_t) = softmax(beta * score[b])`, with temperature `beta` swept in {1, 4, 16, 64}.
- **Three-factor Hebbian update:**
  Compute prediction `q_t` as above. Get the true next byte `b_true`.
  Define `surprise = -log(P(b_true | c_t))` (large when wrong; near zero when confident-correct).
  Update: `W += arousal * surprise * outer(byte_atom[b_true], c_t.conj()) / N`.
  This is local (pre = context component, post = target component, modulator = arousal * surprise), no backward pass.
- **Modulators in use:** `arousal` (fixed learning rate), `surprise` (per-step, computed from current model's log-probability of the true target). `reward` and `attention` not used in this minimal version.

## Constraints — what makes this a Hebbian-VSA run, not gradient descent

The update rule mathematically coincides with the gradient of a linear softmax classifier over hypervector similarity. The constraints that distinguish this from gradient descent on a learned model are:

1. Substrate atoms (byte atoms, position atoms) are **random IID, fixed**. They are not optimized.
2. Updates are **local per weight**: `dW[i, j]` depends only on `post[i]`, `pre[j]`, and a global modulator. No backward pass, no information flow between weights.
3. Single forward pass per training example; weight update from that example only. No replay buffer, no batched gradient, no momentum.

If these three constraints hold and the model still learns conditional structure, that's evidence three-factor Hebbian learning at this scale produces useful behavior on language data.

## Corpus

- **Training corpus:** concatenation of the project's own English markdown files (`PLAN.md`, `NEXT_PHASE.md`, `README.md`, `PROGRESS.md`, `RESULTS.md`, `CLAUDE.md`). UTF-8 encoded, treated as raw bytes. Estimated 50–100 KB.
- **Train/test split:** first 80% train, last 20% test, contiguous (no shuffling — held-out is genuinely unseen suffix).
- **Why this corpus:** self-contained, reproducible on the user's machine without downloads, natural English with technical vocabulary, deterministic.
- **Note:** corpus size is intentionally small. We're testing whether the architecture can learn conditional structure at all, not whether it competes with frontier models. If Track 0.1 lands "alive," phase 2 of Bet B scales to a real corpus (WikiText-2 or a 1B-token dataset).

## Baselines

All evaluated on the same test split.

1. **Uniform random:** `log2(256) = 8.0 bits/char` (worst case, chance).
2. **Unigram with Laplace smoothing:** byte-frequency-only conditional model. Expected ~4.5–5.0 bits/char on natural English.
3. **3-gram with Kneser-Ney smoothing:** uses the immediately preceding two bytes. Expected ~2.5–3.5 bits/char.
4. **5-gram with Kneser-Ney smoothing:** uses the preceding four bytes. Expected ~2.2–3.0 bits/char.
5. **Pure-Hebbian-VSA (this experiment).**

No tiny-transformer baseline in this probe. That comes in Track 0.1 phase 2 if the result is "alive."

## Hyperparameters and sweeps

- Context window K ∈ {4, 8, 16}.
- Learning rate (arousal) ∈ {0.1, 0.3, 1.0}.
- Temperature beta ∈ {1, 4, 16, 64}.
- Seeds: 3 per configuration.

This is 36 configurations × 3 seeds = 108 runs. Each run is a single training pass over 50–100 KB of bytes, which on CPU should complete in seconds-to-minutes. Total wall time estimate: under 30 minutes.

Report the best K, arousal, beta configuration on the validation set; also report variance across seeds.

## Primary metric

**Test-set bits-per-character (cross-entropy in bits).** Lower is better.

## Pre-registered decision criteria

Stated up front, before seeing any results. These map onto the Track 0 decision matrix in `NEXT_PHASE.md`.

| Outcome on test bits/char | Bet B status | Action |
|---|---|---|
| ≥ unigram (no improvement over frequency-only) | **Dead at this architecture.** One architectural pivot allowed before falling back to Bet A entirely. | Try Sparse Distributed Memory variant (prototype-based, not direct outer-product). If that also fails, ship Bet A only. |
| Between unigram and 3-gram, closer to unigram (improvement < 1 bit/char over unigram) | **Hybrid tier.** Architecture learns *something*, but loses to trivial n-gram baselines. | Bet A becomes higher-priority; Bet B held in reserve as a long-term research thread, not the main investment. |
| Within 0.5 bits/char of 3-gram | **Alive tier.** Architecture is competitive with classical methods at small scale. | Commit Bet B phase 2: scale to 1B-token corpus and word-level vocab; introduce tiny-transformer baseline. |
| At or below 3-gram | **Strong alive.** Architecture is doing genuine conditional modeling. | Commit Bet B phase 2 with high priority; allocate compute for scaling experiments. |

## Risks and what they would mean

- **Memorization.** If train bits/char is dramatically lower than test bits/char (e.g., < 1 bit/char train, > 6 bits/char test), the model has memorized the training corpus rather than learned generalizable conditional structure. Train/test gap > 2 bits/char is suspicious; investigate before claiming a win.
- **Capacity saturation.** With N = 4096 and ~50K training examples, W is over-saturated relative to FHRR bundling capacity. We may see the model improving for the first few thousand updates and then degrading as crosstalk takes over. Plot bits/char over training steps; if it U-shapes, the architecture is capacity-limited, not learning-limited.
- **Trivial wins.** A model that just outputs the most common byte (space) achieves substantially better than chance but doesn't tell us anything. The bar to clear is *unigram with Laplace smoothing*, not chance.

## What we will not claim from this experiment regardless of outcome

- Anything about whether Hebbian-VSA scales to billions of weights or trillions of tokens.
- Anything about whether the architecture works on non-language data.
- Anything about hardware efficiency (that's Track 0.2's job).
- Anything beyond byte-level next-character prediction on a single small corpus.

A positive result here means "the architecture isn't broken at small scale" — not "we have an LLM replacement." The next phase of Bet B would actually test scaling.

## What gets logged

- Train and test bits/char per epoch (single epoch here, so per fraction-of-training-done).
- Distribution of `surprise` over training.
- Final connection-matrix norm and effective rank.
- Per-byte recall (does the model do better on common bytes than rare ones, or is the gap uniform?).
- Standard semantic-trace events from the observability layer so we can inspect any single prediction afterward.
