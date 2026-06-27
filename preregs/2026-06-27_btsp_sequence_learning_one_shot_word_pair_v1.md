# PRE-REG: btsp_sequence_learning_one_shot_word_pair_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** Stage 3 -> Stage 4 bridge (language-sequence-learning unlock)
**Queue:** overnight_queue (GPU mandate per Fix #24)
**Research drill:** notes/research_drill_2x_btsp_binary_signal_collapse_revival_2026-06-27.md (Angle B)
**USER directive 2026-06-27 ~17:55 PDT:** "btsp sounds important in the context of language and, in particular, scoring word weight based on order. tall stand vs stand tall." + "GPU is idle now"

## CONTEXT + WHY THIS CELL

BTSP HARD_FAILed earlier today (`exp_btsp_binary_synapse_v3_baseline_fixed_v3p1` and predecessors) at **prototype-classification** -- but per drill Angle B finding, BTSP was DESIGNED for **sequence / episodic** learning (hippocampal place-cell sequences during behavior; Bittner-Milstein 2017, Wu-Maass 2025). USER recognized this maps to language word-order binding: same atoms, different sequence = different meaning ("tall stand" vs "stand tall"). This is the RIGHT testbed for BTSP. If it works here, unlocks language-sequence-learning capability for the substrate.

## HYPOTHESIS

BTSP with sparse input (fp=0.005) + sparse tagging (fq=0.0025) + one-shot binary flip on context-arrival produces **order-sensitive sequence binding** -- where additive Hebbian collapses (linear sum of bind(POS,a) + bind(POS,b) loses position-context information through naive aggregation), BTSP's selective tagging preserves the sequence-to-context association via tagged-synapse one-shot consolidation.

## TASK -- one-shot order-sensitive sequence binding

Per-trial:
1. Pick 2 random atoms a, b from vocabulary V (size 1000 distinct HD words at full).
2. Form sequence-vector `S_AB = bind(POS_1, a) + bind(POS_2, b)` (= "a b").
3. Form sequence-vector `S_BA = bind(POS_1, b) + bind(POS_2, a)` (= "b a").
4. Generate context-tag-vector C_X (random HD vector, the "meaning" of "a b").
5. Generate context-tag-vector C_Y (random HD vector, different meaning for "b a").
6. EACH ARM uses its specific storage rule to bind S_AB -> C_X and S_BA -> C_Y AFTER ONE SHOT.

Recall:
- Query with S_AB -> should retrieve C_X (NOT C_Y).
- Query with S_BA -> should retrieve C_Y (NOT C_X).
- Cross-confusion = retrieve C_Y when querying S_AB = order-information lost.

Metric: `order_discrimination = recall_correct - recall_wrong` in [-1, +1]. Higher = more order-sensitive.

Bind is HRR-style circular shift: `bind(POS_j, atom) = roll(atom, j)`.

## ARMS (4 mandatory + 1 diagnostic)

1. **ARM_ADDITIVE_HEBBIAN** (baseline): `W += outer(C, S)`. Tests if naive Hebbian sum preserves order.
2. **ARM_RANDOM_TAG_50PCT** (control): random 50% of synapses tagged; only tagged positions receive the update. Tests if random selectivity matters (negative control for "any sparsity wins").
3. **ARM_BTSP_SPARSE_TAG_5PCT** (Wu-Maass spec, MECHANISM ARM): fp=0.005 input sparsity (top-k WTA), fq=0.0025 tag gating (top fq fraction of |outer(C, S_sparse)|), one-shot binary flip of tagged synapses.
4. **ARM_BTSP_SPARSE_TAG_PAIRED_REWARD** (refinement): tag fires only when "context-arrival" pulse passes a threshold (max-eligibility > 1.5x median nonzero eligibility), pairing the sequence with context-tag activation.
5. **ARM_DIAG_ATOM_ORTHOGONALITY** (diagnostic): vary atom-similarity in {0.0 ortho, 0.5 partial, 1.0 identical}. Calibrates discriminator difficulty; identical atoms should yield order_disc ~ 0 (no signal); ortho atoms should be easiest. Run with BTSP_5PCT mechanism.

## REGIME

- **Full:** N_DIM=16384 (GPU-eligible matmul-heavy scale), V=1000, N_PAIRS=200, seeds=[11,17,23,29,37].
- **Smoke:** N_DIM=2048, V=200, N_PAIRS=20, seeds=[1].
- **Self-test:** N_DIM=512, V=50, N_PAIRS=10, seed=[1].
- Single-shot binding (M=1 update per pair; that is the BTSP point).
- Fresh W per pair (clean ONE-SHOT test; no cross-pair contamination).

## PRE-REG BANDS

**HARD_PASS:**
- ARM_BTSP_SPARSE_TAG_5PCT `order_discrimination >= 0.50`
- AND BTSP - ADDITIVE_HEBBIAN `>= +0.20`
- AND BTSP - RANDOM_TAG_50PCT `>= +0.10` (sparse selectivity > random selectivity)
- AND `cv across seeds < 0.10`
- AND NO arm at >= 0.995 saturation (META_RULE_Q)
- AND GPU_UTIL_P50 >= 30% in smoke (Fix #24 enforcement)

**MIDDLE_BAND:**
- BTSP order_discrimination in [0.20, 0.50] OR
- positive lift smaller than HP threshold OR
- cv > 0.10 but means qualify

**HARD_FAIL:**
- BTSP <= ADDITIVE_HEBBIAN (no mechanism win)
- OR BTSP order_discrimination < 0.10 (substrate can't bind order-sensitively even with BTSP)
- OR GPU_UTIL_P50 < 30% in smoke (numpy-on-GPU anti-pattern, Fix #24)
- OR fairness violation (different encoding / readout per arm)
- OR any arm at >= 0.995 saturation (regime too easy)

## FAIRNESS GATES (META_RULE_AA)

- All arms use SAME sequence-vector encoding (same `bind = roll` operation; same atom samples per pair).
- All arms READ the same way: `W @ S_query`, cosine to {C_X, C_Y}, pick max.
- RANDOM_TAG_50PCT controls for "any sparsity helps" (cv discipline: BTSP-5PCT must beat random-50PCT by >= 0.10 to claim sparse-selectivity matters, not just "sparsity").
- Per-pair fresh W; no cross-pair confound.
- 1.000-saturation guard (META_RULE_Q): if any arm hits >= 0.995, regime is too easy -> redesign.

## GPU MANDATE (Fix #24)

- `assert torch.cuda.is_available()` else HARD_FAIL.
- All bind / outer / matmul on `torch.cuda`.
- `nvidia-smi` background sampler every 2s; `gpu_util_p50` must be >= 30% in smoke (anti numpy-on-GPU).
- Cell routes to `overnight_queue`, NOT `remote_cpu_queue`.

## CARDINALITY_OK

`EXPECTED_N_UNITS = n_seeds * (4 mandatory arms * N_PAIRS * 2 queries + 3 diag levels * N_PAIRS * 2 queries)`
- Full: 5 * (4*200*2 + 3*200*2) = 5 * (1600 + 1200) = 14000 datapoints.
- Smoke: 1 * (4*20*2 + 3*20*2) = 280.
HARD_FAIL on cardinality breach (observed < expected).

## HARDENING (META_RULE_X + L1-L4)

- L1 STARTED metrics written immediately at module init.
- L2 per-seed and per-arm progress metrics.
- L3 outer try/except with import-crash sentinel.
- L4 import-crash sentinel writes metrics.json on `BaseException` at module top.
- GPU util sampler runs in daemon thread; stopped in finally block.

## DISPATCH

- **Queue:** overnight_queue (GPU runner; marsh@home).
- **Smoke timeout:** 900s (15 min on smoke regime).
- **Full timeout:** 7200s (2 hr; 5 seeds * 200 pairs * 5 arms at N=16384 GPU matmul).

## EXPECTED OUTCOMES

- **HARD_PASS**: BTSP demonstrates order-sensitive one-shot binding at full N=16384; Stage 3 -> Stage 4 language-sequence-learning bridge UNLOCKED. Substrate has the mechanism for "tall stand" vs "stand tall" distinction.
- **HARD_FAIL with BTSP <= ADDITIVE**: even on the right task class, BTSP doesn't help; substrate's order-sensitivity must come from elsewhere (positional encoding alone, or another mechanism). Atomize as HONEST_NEG; close BTSP arc.
- **HARD_FAIL with order_disc < 0.10 across arms**: NO mechanism in our suite can bind order-sensitively at this regime; possibly task design issue OR substrate-N too small for the bind/unbind to discriminate. Drill back to encoding / N-scaling.
- **MIDDLE_BAND with lift > 0 but < +0.20**: partial mechanism win; needs regime probe (sweep fp, fq, N_PAIRS) to find PASS-band.

## REFERENCES

- Wu & Maass 2025, Nature Comms (binary synapses, one-shot, sparsity fp=0.005 fq=0.0025).
- Bittner & Milstein 2017, Science (BTSP CA1 place fields, one-shot place-cell formation).
- Drill: Angle B framing reorientation (right task class for BTSP).
