# Pre-reg: substrate_n1v3_corpus_transfer_discriminator_v1

**Anchor:** `substrate_n1v3_corpus_transfer_discriminator_v1`
**Author:** exp_dev (hd-instrument Agent Teams)
**Date:** 2026-06-24T16:32:39Z
**Trigger:** Research drill `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md`
  recommended a 4-arm corpus-transfer discriminator to resolve whether n1_v3
  chain-grade (+61.6% top1, cert row 699) is corpus-specific or substrate-general.
**Queue:** overnight_queue (GPU; torch.cuda; ARM_PYTHIA arms require remote NPZ at
  `data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz`).

## Strategic context

- n1_v3 cert anchor (`exp_n1_concept_lm_substrate_native_token_decode_v3.py`,
  cert row 699) reports substrate top1=0.4455 (+61.6% over unigram 0.2757) under
  METRIC_SCOPE=top1 on Pythia-160m-residual VQ of Wikipedia. Skunkworks-VET-
  verified off per-seed data; cv=0.020; chain-grade ratified.
- v2 BUGFIX of `substrate_n1v3_readout_x_cfrpe_plasticity_compose` produced
  ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY top1=0.2128 on text8 + word2vec at
  N_DIM=8192 (PROVENANCE_FAIL). Research diagnosed this as **corpus-transfer
  failure**, not readout fragility -- the v2 cell changed corpus + encoder +
  vocab + token count + N_DIM simultaneously, so the failure mode was
  ambiguous.
- This discriminator isolates the corpus + encoder + V_TOK variables by
  running four matched arms.

## Falsifiable predictions (load-bearing)

| Hypothesis | HARD-PASS evidence | HARD-FAIL evidence |
|---|---|---|
| n1_v3 lift is corpus-general | ARM_TEXT8_WORD2VEC_N1V3_READOUT top1 >= 0.40 | top1 in [0.20, 0.27] |
| n1_v3 lift is corpus-specific | ARM_PYTHIA_RESIDUALS_N1V3_READOUT top1 >= 0.40 AND ARM_TEXT8_WORD2VEC_N1V3_READOUT top1 < 0.30 | both arms <= 0.30 or both >= 0.40 |
| Cert row 699 is reproducible | ARM_PYTHIA_RESIDUALS_N1V3_READOUT within +/- 0.05 of 0.4455 | top1 outside [0.40, 0.50] |
| Logit-mixer readout floors at +12% top1 (structural cap) | both LOGIT_MIXER arms in [0.20, 0.30] | EITHER LOGIT_MIXER arm > 0.32 |

## Four arms (each builds FRESH state)

1. **ARM_TEXT8_WORD2VEC_LOGIT_MIXER** -- reference baseline. text8 + word2vec
   sparse-bipolar @ f=0.05 + standard logit-mixer readout (matches v2 BUGFIX
   ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY's setup MINUS the cf-RPE plasticity
   replaced with Hebbian-style outer-product for a direct readout comparison;
   the same encoder + corpus stream + V=4000 as the other text8 arm). Expect
   top1 ~ 0.20 - 0.25 per v2_BUGFIX evidence and fair_harness.
2. **ARM_TEXT8_WORD2VEC_N1V3_READOUT** -- PRIMARY DISCRIMINATOR for corpus-
   general claim. text8 + word2vec + n1_v3 readout (VQ of word2vec embeddings
   into 256 concepts; k=25 sparse codebook; W_C=P_src.T@P_dst on word-pair
   transitions; decode-D word-distribution; raw scores into temp-softmax +
   unigram back-off). The "matched k=25 sweet spot" readout from the v2 BUGFIX
   that gave 0.2128 -- so this arm IS the v2 BUGFIX ARM 2 reproduced inside a
   matched-config cell.
3. **ARM_PYTHIA_RESIDUALS_LOGIT_MIXER** -- new baseline. Pythia-160m residuals
   from `residuals_per_token.npz` + logit-mixer readout. Asks "does the
   logit-mixer readout cap at ~+12% lift even on the Pythia corpus?" If YES
   (top1 ~ 0.30 floor), the +60% lift requires the n1_v3 readout. If NO
   (top1 > 0.35), the corpus alone carries most of the lift.
4. **ARM_PYTHIA_RESIDUALS_N1V3_READOUT** -- SANITY/PROVENANCE arm. Pythia-160m
   residuals + n1_v3 readout. Should reproduce cert row 699 within +/- 0.05 at
   N_DIM=8192 (versus cert anchor's N_DIM=4096). If it doesn't, the entire
   discriminator is on the wrong reference and re-examination is needed.

## Production config

- N_DIM = 8192 (matches v2 BUGFIX scale; doubled from cert anchor's 4096; the
  "lift survives N_DIM=8192 on home corpus" cheapest-discriminator
  prediction from the drill is folded into ARM 4)
- V_C = 256 (matches cert anchor)
- CONCEPT_SPARSE_F = 0.003 (yields k = round(0.003 * 8192) = 25 active -- matches
  cert anchor's k=25 at the doubled N_DIM)
- SEEDS = [7, 17, 23] (matches cert anchor)
- text8 arms: VOCAB_CAP = 4000, N_TRAIN = 100_000, N_HELD = 20_000 (matches
  v2 BUGFIX; the regime where v2 saw 0.2128)
- Pythia arms: MAX_DOCS = 6000 (matches cert anchor's 4800-train+1200-test
  scale at TRAIN_FRAC=0.8); V_TOK = 50257 cap (Pythia/GPT-2 full vocab)
- LAM_BACKOFF = 0.1, LAPLACE_A = 0.5 (matches cert anchor)
- Joint (T, lambda) sweep: TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
  LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (matches v2 BUGFIX)

## HARD bands (pre-registered; verdict_lint surfaces)

**Sanity rail (Fix #28 verify-the-referent on cert row 699):**
- ARM_PYTHIA_RESIDUALS_N1V3_READOUT top1 within +/- 0.05 of N1_V3_REF_TOP1 (0.4455).
  If FAILS: verdict = HARD_FAIL_PROVENANCE; cert row 699 needs re-examination.

**Primary verdict:**
- **HARD_PASS_SUBSTRATE_GENERAL:** ARM_TEXT8_WORD2VEC_N1V3_READOUT top1 >= 0.40
  AND ARM_PYTHIA_RESIDUALS_N1V3_READOUT within sanity rail AND cv < 0.05 on the
  text8-n1v3 arm.
  Implication: substrate has +60%+ top1 path on text8 too; opens composition
  space; the readout is corpus-general.

- **HARD_PASS_CORPUS_SPECIFIC:** ARM_PYTHIA_RESIDUALS_N1V3_READOUT >= 0.40 AND
  ARM_TEXT8_WORD2VEC_N1V3_READOUT < 0.30 (i.e. text8 caps at unigram + ~12%).
  Implication: chain-grade is Pythia-corpus-specific; production substrate-as-LM
  must port to Pythia OR use Path C substrate-OWNED encoder (USER 2026-06-23
  directive).

- **HARD_FAIL_PROVENANCE:** ARM_PYTHIA_RESIDUALS_N1V3_READOUT < 0.40. Cert
  row 699 fails to reproduce on this harness; the original ruling needs re-
  examination. Does NOT impeach the cert ruling itself (different N_DIM,
  different corpus loader) but flags a SECOND replication gap.

- **MIDDLE_BAND:** anything else (e.g. ARM_PYTHIA passes sanity but
  ARM_TEXT8_WORD2VEC top1 in [0.30, 0.40] -- partial transfer with attenuation).

- **cv > 0.05 on any HARD_PASS arm: demote to MIDDLE_BAND** (seed-unstable;
  Skunkworks's standing discipline).

## By-construction guards

1. **Substrate-only-decode (zero LLM forward calls at inference)** -- inherited
   from cert anchor. Pythia-160m is called ONCE at ingest (loading
   residuals_per_token.npz); never at inference. word2vec-google-news-300 is a
   static embedding lookup (no model forward). LLM_CALL_COUNTER assert = 0
   before metrics write.

2. **No test leakage in VQ** -- MiniBatchKMeans fit on train tokens only; test
   tokens are PREDICT'd post-fit. Inherited from cert anchor and v2 BUGFIX.

3. **Raw scores into temp-softmax** -- BUGFIX-1 from v2 BUGFIX preserved (NO
   L2 normalization on activated or D). Verified by T10 selftest from v2 BUGFIX.

4. **Sparse Willshaw sweet spot** -- k = round(0.003 * 8192) = 25 active per
   concept code; matches cert anchor's k=25 at N_DIM=4096 (BUGFIX-2 from v2).

5. **Per-arm fresh state** -- each arm builds its own VQ + codebook + W + D
   from scratch in `compute_arm_logits`. No cross-arm leakage.

## Risks + mitigations

- **R1: Pythia NPZ missing on remote** -- already verified existing as of
  2026-06-24T16:30Z (ssh marsh@home; 80k-row file at
  C:/dev/hd-instrument/data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/).
- **R2: text8 corpus missing on remote** -- text8.txt is in the repo
  (`data/text8_cache/text8.txt`); will arrive via SCP with the script.
- **R3: word2vec cache (~1.7GB)** -- already at
  `C:/dev/hd-instrument/data/gensim_cache_v2/word2vec-google-news-300/`
  on remote (verified 2026-06-24T16:30Z).
- **R4: Pythia residual extraction takes >30min if missing** -- guarded by
  hard FileNotFoundError; cell exits cleanly if NPZ absent.
- **R5: VQ collapse on Pythia residuals at V_C=256** -- inherited from cert
  anchor; codebook utilization logged + warned at <50%; will not block.
- **R6: Memory** -- N_DIM=8192 + V_TOK=50257 ~ 1.6GB D matrix in float32;
  fits comfortably in 6.8GB GPU. text8 arms with V=4000 are an order smaller.

## Cites

- `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md` (Research drill;
  drives the 4-arm design + bands)
- `experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py` (cert
  anchor source; readout helpers reused verbatim)
- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json`
  (cert row 699 per-seed verified evidence: 0.4506 / 0.4506 / 0.4353 top1)
- `experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.py`
  (text8/word2vec scaffolding + readout helpers reused)
- `data/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX/metrics.json`
  (PROVENANCE_FAIL evidence: ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY top1=0.2128)
- `cert_ledger.jsonl` rows 588, 627, 698, 699 (chain-of-rulings for n1_v3)
- USER 2026-06-23 directive: Path C substrate-owned encoder is the answer if
  this comes back HARD_PASS_CORPUS_SPECIFIC.

## Estimated cost

- ~30-40min on remote_cpu (encoder load + 4 arms x 3 seeds + Pythia residual
  load). On GPU, likely 15-25min (matmul + W_C build are GPU-accelerated;
  encoder load is the bottleneck on a fresh process). Timeout requested:
  7200s = 2 hours (3-4x safety margin per the BLOCKING pre-dispatch checklist
  formula). Below PROT-019 4h floor because anchor has no `_n4096+` suffix.

## REQUIRED_FIELDS

- verdict, verdict_msg, elapsed_s, summary (queue_add.py REQUIRED_FIELDS)
- by_arm_agg (per-arm aggregates with top1_acc_mean / cv)
- per_seed[i].by_arm[arm].top1_acc (per-arm per-seed top1 -- Fix #28 anchor)
- detail.provenance_arm_pythia_n1v3_top1 + .provenance_arm_pythia_n1v3_ok
- detail.honest_scope + .v1_design_notes
