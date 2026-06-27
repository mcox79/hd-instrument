# PRE-REG: btsp_sequence_learning_one_shot_word_pair_v2

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Predecessor:** btsp_sequence_learning_one_shot_word_pair_v1 (smoke saturation HARD_FAIL)
**Queue:** overnight_queue (GPU mandate per Fix #24)

## v1 -> v2 SMOKE-DISCRIMINATOR REDESIGN

**v1 smoke verdict: HARD_FAIL (saturation guard fired).**
- All 3 mandatory storage arms hit recall = 1.000 (order_disc = 1.0).
- Diagnostic arm showed mechanism IS well-formed (ortho=0.95, partial=0.45, identical=0.0).
- Root cause: v1 used FRESH W per pair -> trivial because outer(C, S) on empty W with random C is a near-orthogonal-projector; recall just picks higher cosine. No crosstalk = no information bottleneck = all arms trivially solve.
- Also: btsp_paired_reward at -1.0 because median-threshold gate skipped all updates -> empty W -> systematic wrong (broken).

**v2 fixes (per META_RULE_K + Discipline #2 smoke-must-fire-discriminator):**
1. **SHARED W across ALL bindings**: store 2*N_PAIRS bindings (both orderings of every atom-pair) into ONE W. Now substrate is at capacity-load = real crosstalk pressure = additive naive accumulation should interfere with itself; sparse-selective storage should preserve more order-info.
2. **Recall against ALL stored contexts (2*N_PAIRS candidates)**: argmax over the full bank, not just C_X/C_Y two-way pick. Much harder fairness gate.
3. **Cross-order confusion metric**: order_discrimination = correct - cross_order_confusion (where cross_order = SWAPPED-order tag for SAME atom pair). This is the diagnostic that targets "order info preserved or lost."
4. **Fixed paired-reward gate**: replace broken median-threshold with biologically-motivated "max_elig > 2*mean_elig" context-arrival pulse. The Wu-Maass paired-reward is a neuromodulator-pulse-gated tagging; this captures it.
5. **BTSP W initialized as random bipolar** (Wu-Maass spec: binary synapses start at random sign before consolidation), not zero. Other arms still start at zero (additive/random_tag are continuous-W rules).

## HYPOTHESIS

At shared-W capacity load (400 bindings into one 16384x16384 W at full), additive Hebbian's order_discrimination collapses due to crosstalk (linear superposition loses position context as load grows). BTSP's sparse-tagging preserves order info because each binding only flips ~0.25% of synapses to a SIGNED value tied to the (C, S_sparse) outer product, leaving the rest of W carrying other bindings without interference.

## TASK -- shared-W one-shot order-sensitive sequence binding

- Vocab V (1000 bipolar atoms, dim N_DIM=16384 at full).
- Generate N_PAIRS distinct atom-pairs (a_i, b_i).
- For each pair, build TWO orderings: `S_AB_i = roll(a_i, 1) + roll(b_i, 2)` and `S_BA_i = roll(b_i, 1) + roll(a_i, 2)`.
- Each ordering gets a unique random HD context tag: `C_AB_i`, `C_BA_i`. Total 2*N_PAIRS bindings.
- ONE shared W per arm; store all 2*N_PAIRS bindings via the arm's storage rule (single-shot per binding).
- Recall: query each S, compute `W @ S`, cosine to ALL 2*N_PAIRS candidate contexts; argmax.
- Correct: argmax == paired_context. Cross-order confusion: argmax == SWAPPED-order tag for the SAME pair.

Metric: `order_discrimination = recall_correct - cross_order_confusion` in [-1, +1].

## ARMS (4 + 1 diag)

1. **ARM_ADDITIVE_HEBBIAN**: `W += outer(C, S) / N`. Tests if naive Hebbian preserves order under crosstalk.
2. **ARM_RANDOM_TAG_50PCT**: random 50% of synapses tagged per binding -- only tagged positions update. Controls for "any sparsity wins."
3. **ARM_BTSP_SPARSE_TAG_5PCT**: fp=0.005 input k-WTA, fq=0.0025 top-eligibility tag, binary flip. Mechanism arm.
4. **ARM_BTSP_SPARSE_TAG_PAIRED_REWARD**: BTSP + context-arrival gate (only fire if max_elig > 2*mean_elig).
5. **ARM_DIAG_ATOM_ORTHOGONALITY**: vary atom-similarity in {0.0 ortho, 0.5 partial, 1.0 identical} on BTSP_5PCT. Calibrates difficulty.

## REGIME

- **Full**:  N_DIM=16384, V=1000, N_PAIRS=200, seeds=[11,17,23,29,37]  (400 bindings into one W)
- **Smoke**: N_DIM=2048,  V=200,  N_PAIRS=50,  seeds=[1]               (100 bindings into one W)
- **Self**:  N_DIM=512,   V=50,   N_PAIRS=20,  seeds=[1]               (40 bindings; minimal)

## PRE-REG BANDS

**HARD_PASS:**
- ARM_BTSP_SPARSE_TAG_5PCT `order_discrimination >= 0.30` (lowered from v1 because shared-W is harder)
- AND BTSP - ADDITIVE `>= +0.15`
- AND BTSP - RANDOM_TAG_50PCT `>= +0.10` (sparse selectivity beats random)
- AND `cv across seeds < 0.10`
- AND NO arm at `recall_correct >= 0.995` saturation (META_RULE_Q)
- AND GPU_UTIL_P50 >= 30% in smoke (when n_samples >= 3)

**MIDDLE_BAND:**
- BTSP order_disc in [0.10, 0.30] OR positive lift < HP threshold

**HARD_FAIL:**
- BTSP <= ADDITIVE (no mechanism win even under crosstalk)
- OR BTSP order_disc < 0.05 (substrate fails order-binding even at the right task class)
- OR ANY arm at recall_correct >= 0.995 (regime still too easy -- redesign needed)
- OR GPU_UTIL_P50 < 30% in smoke (with n_samples >= 3)

## FAIRNESS GATES (META_RULE_AA)

- All arms see SAME vocab, SAME pair indices, SAME context tags. Different storage rules ONLY.
- All arms READ same way: `W @ S` -> cosine to all 2*N_PAIRS context candidates -> argmax.
- RANDOM_TAG_50PCT controls for "any sparsity wins" -- BTSP must beat random-50 by >= +0.10.
- BTSP W-init is RANDOM BIPOLAR (Wu-Maass spec); other arms W-init is zero (their natural state).
- Per-arm RNG derived from seed + arm-hash so storage stochasticity is reproducible but independent of data RNG.

## GPU MANDATE (Fix #24)

- `assert torch.cuda.is_available()` else HARD_FAIL.
- All bind / outer / matmul on `torch.cuda`.
- `nvidia-smi` background sampler every 2s; in smoke, `gpu_util_p50 >= 30%` REQUIRED (when n_samples >= 3 to avoid false-FAIL on fast cells).
- Routes to `overnight_queue`.

## CARDINALITY_OK

`EXPECTED_N_UNITS = n_seeds * (4 arms * 2*N_PAIRS queries + 3 diag levels * 2*N_PAIRS queries)`
- Full: 5 * (4*400 + 3*400) = 5 * 2800 = 14000 datapoints.
- Smoke: 1 * (4*100 + 3*100) = 700 datapoints.
HARD_FAIL on cardinality breach.

## HARDENING (META_RULE_X + L1-L4)

- L1 STARTED metrics written immediately.
- L2 per-seed progress.
- L3 outer try/except in main + finally on GPU sampler stop.
- L4 import-crash sentinel.

## DISPATCH

- **Queue:** overnight_queue.
- **Smoke timeout:** 1200s (20 min; shared-W is heavier than v1 per-pair but still small at smoke regime).
- **Full timeout:** 10800s (3 hr; 5 seeds * 400 bindings into a 16384^2 W is matmul-heavy).

## EXPECTED OUTCOMES

- **HARD_PASS**: BTSP wins under shared-W crosstalk. Stage 3->Stage 4 language bridge UNLOCKED. Substrate can bind "tall stand" vs "stand tall" robustly even at capacity.
- **HARD_FAIL with BTSP <= Additive**: BTSP is genuinely the wrong mechanism for substrate's sequence-binding task class (closes the arc). Atomize HONEST_NEG; consider STC tag-and-capture instead.
- **HARD_FAIL with all arms saturated**: regime STILL too easy at smoke; need more N_PAIRS (more load) OR add noise OR raise V/N_PAIRS ratio. Redesign before full.
- **MIDDLE_BAND**: partial mechanism win; ship sparsity-regime sweep next.

## REFERENCES

- Wu & Maass 2025, Nature Comms.
- Bittner & Milstein 2017, Science.
- v1 smoke metrics: `data/exp_btsp_sequence_learning_one_shot_word_pair_v1_smoke/metrics.json` (saturation HARD_FAIL).
- Research drill Angle B: `notes/research_drill_2x_btsp_binary_signal_collapse_revival_2026-06-27.md`.
