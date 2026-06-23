# Pre-registration: substrate_pc_hierarchy_text8_lm_v1

**Date:** 2026-06-23
**Anchor:** substrate_pc_hierarchy_text8_lm_v1
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** [7, 17, 23], **PC layer depth grid:** {rank1-baseline, 2, 5}

## Scientific question

Does a multi-layer Predictive Coding hierarchy (Friston/Rao-Ballard 1999, forward-only
local Hebbian on prediction error per layer) break substrate's rank-1 Hebbian cap
(Schlag-Schmidhuber linear-attention ceiling ~7.6 BPC) on text8 word-level next-token
prediction? Brain typically runs 6-8 cortical PC layers deep; brain is existence proof
that multi-layer PC works at scale. This cell isolates ONE mechanism (PC layer depth)
with a clean char_trigram encoder baseline (no encoder confound), complementary to
brain_full_compose cells that combine all brain primitives simultaneously.

## Pre-registered bands

**HARD-PASS:**
- ARM_PC_5_LAYER bpc_best < ARM_RANK1_HEBBIAN_NO_HIERARCHY bpc_best - 1.0 bits
  (clearly beats rank-1 ceiling by 1+ bit)
- AND ARM_PC_5_LAYER bpc_best < 7.5 (beats unigram floor 7.738 by 0.24+ bits)
- AND ARM_PC_5_LAYER bpc_best CV across 3 seeds <= 0.10

**MIDDLE:** ARM_PC_5_LAYER beats rank-1 baseline (lift > 0) but does not meet HP
criteria — either lift < 1.0 bits OR pc5_bpc >= 7.5.

**HARD-FAIL:** ARM_PC_2_LAYER bpc_best >= ARM_RANK1_HEBBIAN_NO_HIERARCHY bpc_best
AND ARM_PC_5_LAYER bpc_best >= ARM_RANK1_HEBBIAN_NO_HIERARCHY bpc_best (no lift from
multi-layer hierarchy at either depth; rank-1 is the structural cap regardless of
PC depth; brain-existence-proof does NOT transfer to substrate-style sign() PC).

## Calibration rationale

- Rank-1 ceiling reference: substrate-as-LM with char_trigram + dense bipolar + single
  outer-product W has consistently landed at ~7.7-7.9 BPC (e.g. fresh_W_bpc_per_encoder
  arms). This is the linear-attention rank-1 cap; the analytic floor.
- Unigram analytic floor: ~7.738 (from text8 word-level VOCAB_CAP=4000 frequency dist).
- 1.0 bit lift threshold: a chain-grade hierarchy-helps result must produce decisive
  separation, not noise. 1 bit is roughly halving the per-token NLL — large enough to
  rule out finite-sample variance at 100k train + 20k held tokens.
- CV <= 0.10: standard cert-grade tolerance for cross-seed stability.
- Symmetric trip-wires (NEGATIVITY-BIAS rule per USER 2026-06-17): HF condition
  triggers only when BOTH PC arms fail, not just one — gives the mechanism the most
  honest chance to land HP.

## N-suffix section

Anchor does NOT use _n8192 suffix (PROT-018 binding); production N_DIM = 8192 is
documented here and enforced in the script (`N_DIM = 8192`). Anchor name reflects the
mechanism (pc_hierarchy_text8_lm) not the dim. Per PROT-019 the script's N_DIM=8192
combined with timeout >=21600s satisfies the large-N floor.

## Timeout estimate

Smoke: at SMOKE config (N_DIM=8192, N_TRAIN=1500, 1 seed, all 3 alphas swept per PC
arm) measured smoke wall ~95s for the algorithm portion (selftest + load + 4 arms).
Per Fix #17 strict measurement: smoke_wall_s_algo measured.

FULL: N_DIM=8192, N_TRAIN=100000, 3 seeds, 3 alphas swept x (2 PC arms) + 1 rank-1
arm + 1 unigram arm. Dominant cost = PC arm ingest: N_TRAIN matmul chunks * n_layers
matmuls per chunk per alpha. Scaling vs smoke:
  - N_TRAIN factor: 100k / 1.5k ~ 66.7x
  - 3 seeds factor: 3x
  - Per-seed wall ~ 95s * 66.7 * (5 alphas/3 alphas) at smoke ratio. Smoke had
    3 alphas; full also 3 alphas, so no alpha factor.
  formula: ceil(1.5 * 95 * 66.7 * 3) = 28507s
  But: GPU >> CPU smoke (~10-30x speedup on matmul-bound), so realistic 1-3hr wall.
  Conservatively budget 21600s (6h) per PROT-019 N=8192 floor; well above realistic.
timeout_s = 21600

## Self-test discipline

11 self-tests:
1. char_trigram encoder bipolar shape
2. _safe_sign_t (zero -> +1; nonzero sign preserved)
3. Hebbian sign correct (W magnitude grows under repeated outer)
4. PC error decomposition (error + recon == input within tolerance)
5. rank1_hebbian_W shape + nonzero
6. PC layer stack shape (n_layers + W_pred)
7. forward_pc_layers produces correct shape + finite logits
8. zero-logits BPC near log2(V) (random init sanity)
9. unigram analytic max-class
10. verdict bands trip HP/HF/MID correctly
11. LLM call counter clean (substrate-only-decode)

Plus runtime sanity: ARM_RANK1_HEBBIAN BPC should reproduce prior ~7.7-7.9 (validates
encoder + W baseline); PC reconstruction error should decrease across training.

## Cites

- exp_predictive_coding_hierarchy_smoke_v1.py (CPU/numpy PC smoke; same Rao-Ballard
  local Hebbian rule, applied to associative recall not LM)
- exp_substrate_as_lm_composed_primitives_GPU_v1.py (text8 word-LM GPU template;
  char_trigram encoder + rank-1 W baseline)
- USER 2026-06-23: substrate's rank-1 cap may break with multi-layer hierarchy;
  brain is existence proof
- USER 2026-06-22: GPU dispatch must use GPU (Fix #24)
- USER 2026-06-22: empowered to experiment where lit says dismissed (PC negative
  results in literature are information not stop signal)
