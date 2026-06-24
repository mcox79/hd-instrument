# Pre-reg: substrate_dynamic_f_phase_shift_sparsity_v1

Date filed: 2026-06-24
Filed-by: exp_dev
Trigger: Meta-skepticism drill Anchor 4 / USER directly raised A11 question:
  "is f one of the things we can phase-shift around? It would be pretty amazing
  to be able to switch to a fast high-power mode and to a slower low-power mode."
Cell: experiments/exp_substrate_dynamic_f_phase_shift_sparsity_v1.py

## Purpose

f sparsity has been FIXED at 0.05 across all substrate cells to date. Brain
DYNAMICALLY modulates cortical sparsity via ACh/NE neuromodulation (Goard-Dan
2009; Pinto-Goard 2013; Polack-Friedman-Golshani 2013): awake/attending =
denser, sleep/default = sparser. The computational hypothesis: storage can be
sparse (capacity-efficient, low-power), recall can be dense (fast, high-power).

This cell tests whether substrate gains a BPC lift when STORAGE phase uses one
sparsity f and QUERY phase uses a different sparsity f. Simplest 2-phase
formulation; no continuous modulation; no query-difficulty gating (future).

Substrate-novel: no prior cell varies f BETWEEN store and query phases. Existing
cells fix one f (typically 0.05) for both. If HARD_PASS, substrate gains a
brain-canonical mode-switching capability.

## Mechanism

For each arm, given base encoder E_base (word2vec -> Gaussian-project(N_DIM) ->
L2 normalize):

  E_store_f = L2(sparsify_bipolar(E_base, f_store))
  E_query_f = L2(sparsify_bipolar(E_base, f_query))

  Storage:  W = sum_t E_store_f[idx[t+1]]^T @ E_store_f[idx[t]]
  Recall:   query[ctx] = L2(E_store_f[ctx] @ W^T)       (in store-sparsity space)
            logits[ctx] = query[ctx] @ E_query_f^T      (decode in query-sparsity space)

When f_store == f_query the mechanism is identical to the static-f baseline
(fair_harness pipeline). When f_store != f_query, the query phase reads bound
traces through a different sparsity prior than was used at write time.

## Arms (6 arms, 3 seeds in full run)

| Arm | f_store | f_query | Notes |
|-----|---------|---------|-------|
| ARM_STATIC_F_0p02              | 0.02 | 0.02 | A5 finding: f=0.02 capacity-optimal |
| ARM_STATIC_F_0p05              | 0.05 | 0.05 | SANITY RAIL vs fair_harness 7.3065 |
| ARM_STATIC_F_0p50              | 0.50 | 0.50 | Dense baseline |
| ARM_DYNAMIC_STORE002_QUERY005  | 0.02 | 0.05 | Store sparse, query slightly denser |
| ARM_DYNAMIC_STORE002_QUERY050  | 0.02 | 0.50 | Store sparse, query dense (brain analog) |
| ARM_DYNAMIC_STORE005_QUERY050  | 0.05 | 0.50 | Store middle, query dense |

## Pre-registered HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust post-smoke)

Sanity rail (gate; must hold else HARD_FAIL_PROVENANCE in full mode):
  ARM_STATIC_F_0p05 BPC within +/- 0.05 of fair_harness 7.3065

HARD_PASS:
  Any dynamic arm BPC <= (best static arm BPC) - 0.10 bits
  AND that dynamic arm cv <= 0.05 across 3 seeds.
  Action: substrate gains genuine dynamic-f mode-switching at fair_harness scale.

CHAIN_GRADE_BONUS:
  Any dynamic arm BPC <= (best static arm BPC) - 0.30 bits
  AND cv <= 0.05.
  Action: substrate-novel feature unlocked; report energy efficiency + mode-switch
  story; promote to chain-grade with atom + hdlab/ primitive update.

MIDDLE_BAND:
  Best dynamic arm lift in [+0.05, +0.10) bits over best static
  (insufficient for HARD_PASS but non-trivial signal).
  Also MIDDLE_BAND_HIGH_CV: lift >= +0.10 but cv > 0.05.

HARD_FAIL:
  ALL dynamic arms lift <= +0.05 over best static (no phase-shift benefit).
  Action: this 2-phase formulation doesn't help; consider continuous-f or
  query-difficulty-gated modulation (3+ phase mode).

HARD_FAIL_PROVENANCE:
  Sanity rail ARM_STATIC_F_0p05 drifts > 0.05 from fair_harness 7.3065.
  Action: encoder pipeline mismatch; cannot conclude; investigate.

## Config (FULL run)

- N_DIM = 8192
- N_TRAIN = 100_000 tokens, N_HELD = 20_000 tokens
- VOCAB_CAP = 4000
- text8 corpus (data/text8_cache/text8.txt)
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  (excludes 0.0 per Skunkworks META C7)
- MRR_K = 10
- seeds = [7, 17, 23] (3 seeds for cv check)
- Encoder: word2vec-google-news-300 -> Gaussian-project -> L2 (OOV: char-trigram)
- Rank-1 Hebbian W; joint (T, lambda) sweep on dev half; report on test half
- Routing: overnight_queue (GPU; torch.cuda for storage and recall matmuls)

## Why 3 seeds is sufficient

- Substrate encoder is deterministic per seed (word2vec lookup cached;
  Gaussian-project seeded; sparsify is deterministic top-k)
- 3-seed cv across distinct random Gaussian projections measures variance from
  projection geometry only (not data variance)
- cv <= 0.05 is the discipline-standard threshold for HARD_PASS claims at this
  config

## What this cell does NOT show

- Does NOT test continuous-f modulation (only 2 fixed phases)
- Does NOT test query-difficulty gated f-switching (no adaptive f)
- Does NOT test 3+ phase modes (only store / query)
- Does NOT vary f_store across the train trajectory (storage f fixed per arm)
- Does NOT test combination with cf-RPE / heterogeneous plasticity / K-banks
- Result at N_TRAIN=100k text8 V=4000 may not generalize to other corpora

## Brain prior

P_inherited = 0.50 (brain DOES modulate cortical sparsity; mechanism documented)
Deflated to P_substrate_native = 0.35 (implementation uncertainty; substrate's
bipolar top-k sparsification has discrete semantics quite different from
biological pyramidal-neuron firing-rate modulation; lift magnitude may be small
or null at this scale; brain modulates dynamically per attention state, not as
a fixed two-phase store/query split)

## Routing rationale

overnight_queue (GPU). Fix #24 compliance: uses torch.cuda for storage W matmul
and recall logits matmul. N_DIM=8192 W=8192x8192 matmul over 100k pairs
benefits from GPU throughput. Encoder build on CPU (gensim lookup) is fixed
overhead.

## Disciplines applied

- ASCII-only
- Fix #14: ONE cell (this anchor)
- Fix #24: torch.cuda for heavy matmuls
- Fix #28: per-arm metrics ONLY in verdict_msg; no cross-arm framing in claim
- A5: path-scoped commit (caller)
- Pre-reg filed BEFORE smoke run
- PROT-018: no _nN suffix in anchor (N_DIM stated above)
- WHAT_THIS_DOES_NOT_SHOW clause in detail and this prereg
- LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
- Per-seed checkpointing + atexit synthesizer

## Cites

- experiments/exp_fair_harness_substrate_as_lm_v1.py (sanity rail 7.3065)
- experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (torch.cuda + word2vec template)
- experiments/exp_substrate_ACh_query_conditional_read_gain_LM_v1.py (related: per-query gain, DIFFERENT mechanism)
- USER A11 question (meta-skepticism drill Anchor 4)
