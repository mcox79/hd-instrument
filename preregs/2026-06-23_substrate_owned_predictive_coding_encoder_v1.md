# Pre-reg: substrate_owned_predictive_coding_encoder_v1

**Date:** 2026-06-23
**Author:** exp_dev (subagent spawn under Research/Director)
**Anchor:** `substrate_owned_predictive_coding_encoder_v1`
**Script:** `experiments/exp_substrate_owned_predictive_coding_encoder_v1.py`
**Queue:** `overnight_queue` (GPU; Fix #24 routing — matmul-bound PC training over text8 100k tokens at N_DIM=8192)
**Cell class:** Production FULL run (not smoke-only). Smoke runs at small config inside the same script via `--smoke` for the dispatch gate.

## Scientific question

USER strategic principle 2026-06-23: substrate-owned encoder is THE answer to the
LM gap; Path A (word2vec) and Path B (char_trigram) are diagnostic probes only.
Brain didn't borrow other species' encoders. Path C tests whether a fully
substrate-native, brain-analog predictive-coding hierarchy — trained without
backpropagation, using only local Hebbian updates on prediction error per
Rao-Ballard 1999 / Friston 2005 / Bastos 2012 — can produce an encoder that
beats the borrowed word2vec encoder on the SAME fresh-W BPC harness used by
`fresh_W_bpc_per_encoder_v2`.

If a substrate-owned PC encoder beats word2vec on this fair-comparison
harness, Path C is chain-grade-eligible as THE substrate-product encoder and
the L2 glass-box LM has a viable substrate-native front end. If it loses,
substrate W matrix is the bottleneck (not encoder choice) and the LM gap
closure pivots to architectural rewrite.

## Hypotheses tested

1. (H_PASS) A 3-layer substrate-native PC encoder, composed with sparse-bipolar
   readout and Tonegawa competitive-allocation lock-in, learns word
   representations whose downstream fresh-W BPC is meaningfully better than
   word2vec at identical N_DIM, vocab, train/held splits, and seeds.
2. (H_FAIL) Substrate-owned PC encoders perform no better than word2vec
   (substrate W is encoder-invariant cap).

## Design — 5 arms, fair-comparison harness

Same `fresh_W_bpc_per_encoder_v2` BPC pipeline:
- N_DIM = 8192
- Vocab cap = 4000 most-frequent text8 tokens (plus `<unk>`)
- N_TRAIN = 100_000 tokens (text8)
- N_HELD = 20_000 tokens (text8 held-out; split 50/50 dev/test as in v2)
- Seeds = [7, 17, 23]
- Lambda grid (log-linear interp with unigram): [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- Per-arm: build fresh Hebbian W from scratch via outer-product on encoded
  vocab pairs; report BPC at best dev-selected lambda
- ARM_UNIGRAM = analytic floor (matches v2 reference 7.738)

### Arms

1. **ARM_UNIGRAM** (analytic floor; bpc=7.738 reference baseline)
2. **ARM_CHAR_TRIGRAM_FRESH_W** (lexical-encoder substrate baseline; matches v2)
3. **ARM_WORD2VEC_FRESH_W** (Path A reference; matches v2 setup exactly)
4. **ARM_SUBSTRATE_PC_BASIC** (substrate-owned PC encoder; L3 output without
   sparse-bipolar readout — tests pure brain-analog PC)
5. **ARM_SUBSTRATE_PC_PLUS_SPARSE_BIPOLAR_PLUS_LOCK_IN** (full substrate-owned:
   PC + sparse-bipolar f=0.05 readout + Tonegawa lock-in at readout — tests
   composed substrate primitives)

### Substrate-owned PC encoder training (no backprop)

- 3-layer hierarchy at N_DIM=8192 (L1 -> L2 -> L3 all N_DIM-wide)
- Forward pass: `L1_out = sign(W_L1 @ input)`; same for L2, L3
- Input: token excitation = a fixed random bipolar seed vector per vocab id
  (planted identity per word; PC must learn to organise these into a
  semantically meaningful representation via co-occurrence statistics)
- Per-layer reconstruction error (Rao-Ballard):
  `error_Li = layer_input - W_Li.T @ Li_out`
- Local Hebbian update per layer:
  `W_Li += alpha * outer(error_Li, layer_input) / N_DIM`
- **Tonegawa competitive allocation at L3** (write-time): maintain excitability
  trace `E[i]` per L3 position; route sparse activations via
  `softmax(beta * E[i])`. Tonegawa-style winner-take-most allocation prevents
  L3-position degeneracy. (Per Tonegawa engram allocation lit.)
- **Sparse-bipolar L3 output** (full arm only): keep top-`f` (default 0.05)
  L3 activations by magnitude; set those to sign, rest to zero. Tests whether
  sparse readout helps Hebbian outer-product fresh-W cap.
- Trained on text8 N_TRAIN=100k tokens for 1 or 3 passes (sweep)
- Per-word encoded representation = L3 output of forward-pass on the word's
  fixed-bipolar input (deterministic conditional on trained W matrices)

### Hyperparameter sweep (small grid; best-config per arm)

- `alpha` (PC learning rate): [0.01, 0.05, 0.10]
- `beta` (Tonegawa softmax temperature): [1.0, 2.0, 5.0]  (full arm only)
- `f_sparse` (output sparsity): [0.03, 0.05, 0.10]  (full arm only)
- `training_passes`: [1, 3] (full pass through 100k tokens)

For PC_BASIC: sweep alpha + training_passes only (3 * 2 = 6 configs).
For PC_FULL: alpha + beta + f_sparse + training_passes (3*3*3*2 = 54 configs).
To keep cost bounded, we run a 2-stage sweep:
  - Stage 1 per seed=7: full grid; pick best config by WordSim353-25 + training
    convergence
  - Stage 2: re-run best config under seeds=[7,17,23] for variance estimation

## Pre-registered bands

### HARD_PASS (substrate-owned encoder WINS; Path C is THE answer)
ALL of:
- `ARM_SUBSTRATE_PC_PLUS_SPARSE_BIPOLAR_PLUS_LOCK_IN bpc_best_mean < ARM_WORD2VEC_FRESH_W bpc_best_mean - 0.3` (clear lift over word2vec)
- AND `ARM_SUBSTRATE_PC_PLUS_SPARSE_BIPOLAR_PLUS_LOCK_IN bpc_best_mean < 7.738` (beats unigram floor)
- AND `cleanup recall at sigma=1.5 >= 0.20` (lifts Shannon floor)
- AND `cv across seeds <= 0.05` (stability)

### HARD_FAIL (substrate-owned does NOT beat borrowed OR substrate W capped)
EITHER of:
- `ARM_SUBSTRATE_PC_* bpc_best_mean >= ARM_WORD2VEC_FRESH_W bpc_best_mean` (no
  substrate-owned arm beats Path A; encoder-borrowing remains the better strategy)
- OR `ALL arms bpc >= 7.738` (substrate W matrix is the bottleneck regardless
  of encoder choice; pivots V2 LM gap closure to architectural rewrite)

### MIDDLE_BAND (partial; characterize)
- substrate-PC beats char-trigram but not word2vec; characterize what
  primitive is missing

## Mandatory sanity self-tests (before training counts)

1. **PC mechanism mechanically valid**: at zero-noise input, L3 reconstructs
   the input via downward projection (`recon_cos > 0.85`)
2. **Excitability trace evolves**: E[i] across L3 positions becomes
   non-uniform during training (`std(E) > 0.1 * mean(E)` after first pass)
3. **Reconstruction error decreases**: per-layer `||error||` monotonically
   decreases over training passes (within noise)
4. **Encoder learned SOMETHING semantic**: at training convergence,
   WordSim353-25 subset Spearman correlation > 0.15 (planted-bipolar baseline
   alone gives ~0 ; this discriminates "PC did nothing" from "PC organised
   inputs")
5. **Sparse-bipolar f=0.05 output verified**: per encoded word, sum(|out|>0)
   is within [0.03 * N_DIM, 0.07 * N_DIM]
6. **Fresh W per arm**: each arm's W trace built from scratch; no cross-arm
   contamination

If any sanity test fails for an arm, that arm's BPC is recorded but flagged
`sanity_failed` and excluded from HARD_PASS classification (audit-only).

## Estimated compute budget

- PC training matmul-bound: 100k tokens * 3 layers * (N_DIM^2 = 67M) ~ 20G ops
  per pass; 3 passes = 60G ops; per seed * 3 seeds = 180G ops
- Plus fresh W Hebbian build per arm at 100k pairs * N_DIM^2 = same scale
- Plus BPC eval (2 substrate logit batches per arm * 5 arms)
- GPU 3090-class: ~30-60 min per seed full sweep; 3 seeds = 90-180 min
- Stage-1 grid (60 configs): ~30 min on one seed
- TOTAL FULL estimate: 120-180 min wall on GPU

**Timeout**: 10800s (3 hr) — 1.5x safety margin

## PROT discipline

- PROT-018: no `_nN` suffix in anchor name; production N_DIM=8192 stated in
  script body (anchor is mechanism-named).
- PROT-019: no `_n8192` suffix in anchor, so tier rule not auto-triggered;
  10800s well below any tier floor anyway.
- PROT-020: queue=overnight_queue (GPU) and script uses torch + cuda — OK.
- PROT-021: timeout 10800s < 14400s threshold; _seed_checkpoint helper
  imported and used per discipline anyway.

## Risk

- Modal expected outcome: MIDDLE_BAND (PC-FULL beats char-trigram but not
  word2vec). Lit-scan calibration: PC on discrete bipolar substrates has
  multiple negative results; but per USER 2026-06-22, lit-scan
  dismissed-as-impossible is INFORMATION, not STOP. Substrate-native variant
  (sign-quantised + Tonegawa lock-in + sparse-bipolar) differs from prior
  failed work and is cost-bounded.
- HARD_PASS would route to atomization + hdlab/ primitive update SAME CYCLE
  per USER 2026-06-22 results-to-application cadence; substrate-product
  encoder becomes the canonical Path C answer.
- HARD_FAIL routes to Research as a 2x revival drill per USER STANDING rule
  (try N_DIM=16384, longer training, alternative competitive-allocation
  policy, different sparsity schedule).

## P estimates (lit-scan calibration penalty applied)

- P(HARD_PASS) = 0.20  (substrate-native PC encoder beats word2vec by 0.3 bits
  is ambitious; PC discrete-vector lit-scan negatives discount)
- P(MIDDLE_BAND) = 0.55  (beats char-trigram but not word2vec; modal expected)
- P(HARD_FAIL) = 0.25  (all arms cap at unigram; substrate W bottleneck)

## Cites

- `preregs/2026-06-23_fresh_W_bpc_per_encoder_v2.md` (sister Path A harness)
- `preregs/2026-06-22_predictive_coding_hierarchy_smoke_v1.md` (substrate PC mechanism baseline)
- `experiments/exp_fresh_W_bpc_per_encoder_v2.py` (BPC harness reused verbatim)
- `experiments/exp_predictive_coding_hierarchy_smoke_v1.py` (PC mechanism prior art)
- USER 2026-06-23 Path C strategic principle (substrate-owned encoder is the answer)
- USER 2026-06-22 GPU dispatch must use GPU (Fix #24)
- USER 2026-06-22 empowered to experiment where lit says dismissed
- Rao + Ballard 1999 (predictive coding canonical formulation)
- Friston 2005 / Bastos 2012 (cortical PC microcircuits)
- Tonegawa engram allocation lit (competitive write-time routing)
