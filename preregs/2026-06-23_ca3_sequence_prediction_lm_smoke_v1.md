# PRE-REG: ca3_sequence_prediction_lm_smoke_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_ca3_sequence_prediction_lm_smoke_v1.py`
**Anchor:** `ca3_sequence_prediction_lm_smoke_v1`
**Queue routing:** local_cpu_queue (smoke; numpy-only; <2min end-to-end)
**Source brief:** `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` Section L1.4
**Parent / context:** Gap 1 LM mechanism mining; brain-grounded composition; Tsodyks-Sejnowski 1995, Hasselmo 2002, Salvatori 2024 (CA3-as-RNN, Salk, Cell:Neuron).

## Motivation (intuitive first)

CA3 in the hippocampus is the canonical biological autoassociative-memory + sequence-completion structure: recurrent autoassociation for pattern-completion cleanup, heteroassociation for binding to the next pattern, and (per Salvatori 2024) trained as a self-supervised next-input predictor with spike-coupling between DG, CA3, CA1 confirming the predictive structure.

The substrate already has every primitive needed for the CA3 composition:
- `hdlab/sequence_memory.py` `SequenceMatrix` (the bind primitive; ordered-pair outer-product write)
- `hdlab/iterative_attractor.py` `iterative_cleanup` (the autoassociative cleanup; iterative, not single-shot; basin attraction with sqrt(D)-scaled softmax)
- `hdlab/char_trigram_encoder.py` `CharTrigramEncoder` (the substrate-native text->HD encoder; bipolar)

But we have never composed them as:

  `bind(prev_token, position) -> recurrent autoassoc cleanup -> heteroassoc completion -> next_token distribution`

This is structurally distinct from Path A v2 (rank-1 outer-product Hebbian over token-pairs only). Adding the position-binding step gives the source-side a per-position identity (so the same token in different positions writes to different rows of W), and adding the iterative-cleanup step pulls the noisy bound cue toward the nearest stored attractor in the substrate codebook before heteroassoc readout.

Per `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` Section L2 ranking, this is candidate #2 (CA3 hetero+autoassoc) of the top-2 surviving forward-only Hebbian-compatible mechanisms. Substrate-native; no backprop; composes naturally with existing primitives.

## Cell design

**Numpy-only CPU dispatch.** No torch; smoke at N_TRAIN=10k is matmul-light enough that local CPU is the right home (PROT-020 NumPy + local_cpu_queue is the routed combination).

**Config (smoke):**
- N_DIM = 4096
- N_TRAIN = 10,000 tokens (smoke; full at 100k queued only if smoke not-HARD_FAIL)
- N_HELD = 2,000
- VOCAB_CAP = 4,000
- K_POS = 16 (positional carrier pool; cyclic)
- INGEST_CHUNK = 4096
- CLEANUP_TEMP = 4.0, CLEANUP_MAX_STEPS = 4, CLEANUP_TOL = 1e-3 (iterative_attractor parameters; sqrt(D)-scaled so effective beta ~ 256 at D=4096, sharp enough for clean basin)
- Seeds = [7, 17, 23]
- Vocab: text8 (data/text8_cache/text8.txt); first N_TRAIN+N_HELD whitespace-split tokens

**4 arms:**

1. **ARM_UNIGRAM.** Baseline; Dirichlet-smoothed unigram with alpha=0.1. Floor for the substrate to beat.
2. **ARM_PATH_A_RAW.** Current substrate rank-1 Hebbian: `W = sum_t (E[t+1] outer E[t])`. Prediction = `W @ E[ctx]`, then L2-normalize, then `softmax(<pred, E.T>)`. Reproduces the Path A regime as a within-cell control.
3. **ARM_CA3_HETERO_ONLY.** CA3 heteroassoc step only: `W += bind(E[prev], P[pos]) outer E[next]` where `bind = element-wise product` (standard VSA bipolar binding) and `P` is a fixed pool of K_POS=16 bipolar HD position carriers, cycled over the training corpus. Eval cue = `bind(E[ctx], P[ctx_position % K_POS])` then `W @ cue` then `softmax(<pred, E.T>)`.
4. **ARM_CA3_FULL.** CA3_HETERO_ONLY + iterative_attractor cleanup of the bound cue BEFORE heteroassoc readout. Codebook for cleanup is the encoder matrix E itself (V rows; stored attractors). The cleanup pulls the noisy bound cue toward the nearest stored vocab attractor; THEN we re-read via W.

The KEY hypothesis being tested: the autoassociative-cleanup step BEFORE the heteroassoc readout is the load-bearing CA3 composition (per Salvatori 2024 + Tsodyks-Sejnowski 1995 + Hasselmo 2002). If the cleanup adds nothing over CA3_HETERO_ONLY, the composition is degenerate at this scale. If CA3_FULL beats Path A but CA3_HETERO_ONLY doesn't, the cleanup is the load-bearing element.

## Pre-registered bands (chain-grade-eligible mechanism)

**HARD_PASS:** mean ARM_CA3_FULL BPC < mean ARM_UNIGRAM BPC AND zero LLM calls at inference. The CA3 composition mechanism survives smoke and beats the trivial floor; substrate-only-decode invariant intact. Chain-grade-eligible follow-on at FULL scale.

**HARD_FAIL:** mean ARM_CA3_FULL BPC >= mean ARM_PATH_A_RAW BPC. The CA3 composition does NOT lift over the existing raw rank-1 Hebbian; the mechanism is rejected at smoke scale and we do NOT bundle a FULL run. Honest negative result; routes to Research for 2x/3x revival drill per USER STANDING rule.

**MIDDLE_BAND:** mean ARM_CA3_FULL BPC in (ARM_UNIGRAM, ARM_PATH_A_RAW]. Partial mechanism characterization -- composition lifts over raw rank-1 Hebbian but not over the unigram floor. NOT chain-grade-eligible; tier as MEASURED_MECHANISM per by-construction-saturation tiering.

**Sanity self-test (in-cell, --self-test gate):** at the trivial 10-token cycle vocabulary, Path A and CA3_HETERO each must recover the memorized sequence at acc >= 0.7 (mirrors `text8_substrate_pseudoLM_v2`'s convention). iterative_cleanup zero-noise codebook-recovery invariant exercised in selftest 7.

**Methodology nuance (smoke specifically):**
- Single corpus prefix means the seed differences ONLY affect the encoder seed (and CA3's P carriers). Across-seed CV is expected to be tiny (corpus is identical) -- this is not a discriminator on noise robustness, only on encoder-seed sensitivity. Genuine across-corpus-prefix noise requires N_TRAIN > VOCAB_CAP*log scaling and a per-seed corpus offset, deferred to FULL.
- BPC at smoke N_TRAIN=10k is intrinsically high (sparse pair coverage); a HARD_FAIL here does NOT prove the mechanism is dead at FULL N_TRAIN=100k. But a HARD_FAIL at smoke is sufficient to NOT bundle FULL until the smoke gap is closed at the same scale.

## Substrate-only-decode invariant

Zero LLM calls at inference. Counter asserted at exit; verdict enforces it. Per CLAUDE.md standing requirement.

## Composes with

- `hdlab.char_trigram_encoder.CharTrigramEncoder` (vocab encoder; substrate-native text->HD)
- `hdlab.sequence_memory.SequenceMatrix` (the bind primitive; we use element-wise-product variant for compositional dim-preserving binding rather than full matrix outer product, but architecturally the same ordered-pair role)
- `hdlab.iterative_attractor.iterative_cleanup` (the autoassociative cleanup; mech 5 broad-exploration drill 2026-06-22)

## Out-of-scope (FULL-cycle work)

- N_TRAIN sweep to 100k / 1M (only if smoke not-HARD_FAIL)
- Multiple K_POS values (8, 32, 64) -- this smoke locks K_POS=16
- Different binding ops (circular convolution vs element-wise product)
- Per-position dedicated W matrices instead of shared W
- Cross-seed corpus-prefix variation (genuine sampling noise)

## Honest-scope statement (in metrics.json)

Embedded in `detail.honest_scope`: scale + arms + bands + smoke-only framing as above.
