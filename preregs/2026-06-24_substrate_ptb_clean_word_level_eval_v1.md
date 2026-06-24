# Pre-registration: substrate_ptb_clean_word_level_eval_v1

**Date:** 2026-06-24
**Anchor:** substrate_ptb_clean_word_level_eval_v1
**Routing:** overnight_queue (GPU; torch.cuda; N_DIM=8192 matmul; Fix #24)
**Motivation:** USER directive 2026-06-24 -- "isn't text8 and pythia biased in that we aren't using a standard encoding or looking at just words?" ALL current substrate-as-LM cells use text8 (stripped lowercase character corpus) -- subject to corpus bias. Penn Treebank (Mikolov 2010 split) word-level is the canonical NLP word-level LM benchmark. This cell is the FIRST proper apples-to-apples PTB substrate-as-LM evaluation.

## Reference Cells (heritage)

- `experiments/exp_fair_harness_substrate_as_lm_v1.py` -- the torch+cuda fair_harness; this cell forks its GPU pipeline (word2vec encoder -> sparse-bipolar f=0.05 -> N_DIM=8192 -> rank-1 / K=2 / adaptive cf-RPE plasticity).
- `experiments/exp_substrate_sequence_modeling_production_v2.py` -- the alpha=0.001 word-bigram fix (v1 used alpha=0.1; smoothing-mass V*alpha=400 dominated real bigram counts).
- `experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py` -- K=2 banks gate-weighted cf-RPE primitive (`build_W_k2_cfrpe_gpu`).
- `experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py` -- per-token adaptive cf-RPE (median-normalized LR per sample; clamped to [0.25, 4.0]).
- `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md` -- the methodology drill establishing Lane 2 (intra-corpus substrate-vs-substrate + tagged cross-paradigm baseline) + CONFOUND_AUDIT + INTRA_LANE_DELTA standing discipline.
- Mikolov 2010 PTB split: `https://raw.githubusercontent.com/wojzaremba/lstm/master/data/ptb.{train,valid,test}.txt` -- canonical word-level NLP benchmark; 887k train tokens, 70k valid, 79k test (raw); + `<eos>` injection at line boundaries -> 929k train / 73k val / 82k test; V=10000 incl `<unk>` and `<eos>`.

## Design

### Five arms (apples-to-apples)

ALL arms operate on the IDENTICAL PTB corpus + IDENTICAL word vocabulary + IDENTICAL held-out split. Substrate arms share encoder (word2vec -> sparse-bipolar f=0.05 -> N_DIM=8192).

1. **ARM_B1_UNIGRAM** -- analytic word-unigram floor (alpha=0.1). Sanity floor.
2. **ARM_B2_WORD_BIGRAM** -- add-alpha smoothed word-bigram LM (alpha=0.001 per v2 fix). The REAL LM threshold; tagged two-paradigm baseline.
3. **ARM_S_CFRPE_BASE** -- substrate K=1 with iterative cf-RPE delta-rule plasticity. Rank-1 W. The substrate base reference.
4. **ARM_S_K2_CFRPE** -- substrate K=2 banks (4096 per bank) with gate-weighted cf-RPE per bank. INTRA_LANE_DELTA arm vs ARM_S_CFRPE_BASE (only K_BANKS changes; everything else identical).
5. **ARM_S_ADAPTIVE_CFRPE** -- substrate K=1 with per-token adaptive cf-RPE (median-normalized LR; clamped [0.25, 4.0]). INTRA_LANE_DELTA arm vs ARM_S_CFRPE_BASE (only the cf-RPE rule changes; everything else identical).

### Encoder + corpus

- word2vec-google-news-300 projected to N_DIM=8192, sparse-bipolar f=0.05 (production config; matches fair_harness baseline encoder).
- PTB Mikolov split; train=929k tokens (incl `<eos>`); held=73k tokens (valid set; canonical eval).
- VOCAB = PTB native V=10000 (incl `<unk>` and `<eos>`).
- LAMBDA_GRID = [0.05, 0.1, 0.3, 0.5, 0.7, 1.0] (C7: excludes 0.0).
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0].
- SEEDS = [7, 17, 23] (3 seeds).
- CFRPE: N_STEPS=5000, BATCH=64, LR=0.5 (anchored to v1 chain-grade configs).
- K2 gate temperature = 1.0.

### Lane declaration + CONFOUND_AUDIT

- **Lane 2** (intra-corpus substrate-vs-substrate ablation + tagged cross-paradigm word-bigram baseline).
- **CONFOUND_AUDIT tuple** (stamped in CONFIG_VERSION):
  `(corpus=PTB-word-level-Mikolov, encoder_paradigm=word2vec_sparse_bipolar_f0.05, N_DIM=8192, vocab=PTB-V10000, metric_primary=BPW, baseline_paradigm=word-bigram-add-alpha=0.001, lane=2_intra_corpus_substrate_vs_substrate_plus_tagged_bigram)`
- **INTRA_LANE_DELTA arms**:
  - `ARM_S_K2_CFRPE vs ARM_S_CFRPE_BASE` -- knob = K_BANKS (1 -> 2); else identical.
  - `ARM_S_ADAPTIVE_CFRPE vs ARM_S_CFRPE_BASE` -- knob = cf-RPE rule (fixed-global LR -> per-token adaptive); else identical.
- **Corpus provenance tag** on cert atom (if landed): `corpus_provenance="PTB-word-level (Mikolov split; wojzaremba/lstm)"`.

## Pre-registered HARD Bands (locked before dispatch)

| Band | Condition | Verdict |
|------|-----------|---------|
| Sanity rail: unigram | ARM_B1_UNIGRAM BPW in [9.0, 11.0] (canonical PTB) | gate |
| Sanity rail: bigram | ARM_B2_WORD_BIGRAM BPW in [5.20, 6.80] (canonical PTB) | gate |
| HARD_PASS_CLEAN_SUBSTRATE_VIABLE | ANY substrate arm BPW <= ARM_B2_WORD_BIGRAM BPW - 0.30 AND cv <= 0.05 AND zero_llm_calls_at_inference | HARD_PASS |
| CHAIN_GRADE_BONUS | ANY substrate arm BPW <= 4.5 (approaches LSTM territory) AND HP conditions | HARD_PASS (bonus flag) |
| MIDDLE_BAND | ANY substrate arm BPW in (ARM_B2_WORD_BIGRAM BPW - 0.30, ARM_B2_WORD_BIGRAM BPW] | MIDDLE_BAND |
| HARD_FAIL_DECISIVE | ALL substrate arm BPW means strictly > ARM_B2_WORD_BIGRAM BPW | HARD_FAIL |
| HARD_FAIL (other) | substrate-only-decode gate violated (n_llm_calls > 0) OR sanity rails violated | HARD_FAIL |

### Discriminator probe (NOT a band; diagnostic)

- 3-arm substrate spread = max(substrate_BPW_means) - min(substrate_BPW_means).
- If spread <= 0.05 -> arm-level mechanisms (K_BANKS, adaptive cf-RPE) are NULL on PTB (no discriminating lift over base K=1 cf-RPE).
- If one arm clearly leads -> that knob is the load-bearing factor on PTB.

## Smoke Results

To be filled by exp_dev cell-author after `--smoke` run (PROT-018/019 gates rely on this).

Pre-run expectation (smoke; N_DIM=512, V=200, N_TRAIN=3000, N_HELD=~750, 1 seed):
- ARM_B1_UNIGRAM BPW ~7-9 (smaller V -> lower entropy floor).
- ARM_B2_WORD_BIGRAM BPW lower than unigram (smoothing-mass V*alpha=0.2 at V=200; ample real-signal weight).
- Substrate arms: smoke is not a verdict -- only confirms instrumentation runs end-to-end.

## Routing Decision

- **Routing: overnight_queue** (GPU; torch.cuda; Fix #24 — N_DIM=8192 matmul-bound; idle GPU host gets matmul work).
- **Timeout: 14400s (4h)** — per-seed timeout estimate based on similar fair_harness/K2 cells at full-N_DIM=8192 (smoke wall ~30-90s; full estimated 30-60min per seed across 5 arms). PROT-021 applies (>= 14400 timeout requires `_seed_checkpoint`; this cell imports it via `experiments._seed_checkpoint`).
- **Per-seed checkpoint** via `experiments/_seed_checkpoint.py`. atexit synthesizer recovers metrics from partials on SIGTERM / timeout.
- PROT-018/019 not triggered (no `_n<NUM>` suffix in anchor name).
- PROT-020 satisfied (cell imports torch).

## C7 META Compliance

LAMBDA_GRID excludes 0.0 (per fair_harness convention; lambda=0 is the pure-unigram bypass).

## Discriminator Honesty

- 3-way substrate discriminator (K=1 cf-RPE / K=2 cf-RPE / K=1 adaptive cf-RPE) is INTRA_LANE: each variant changes ONE knob from the base; mechanism-causal claims are valid for the differentiated arm.
- Word-bigram baseline is explicitly TAGGED as cross-paradigm (Lane 2 framing).
- HARD_PASS requires substrate to beat word-bigram by >= 0.30 BPW with cv <= 0.05 -- a real margin, not noise-grade.
- HARD_FAIL_DECISIVE retains its meaning: if ALL substrate arms miss on canonical PTB even with intra-lane variation, the substrate-as-LM ceiling is REAL (not text8-bias artifact).

## What This Does NOT Show

- Does NOT test substrate vs LSTM/transformer at PTB (Lane 4 substrate-product axes are separate; out of scope).
- Does NOT atomize as "substrate-general LM" -- this is PTB-word-level only. Cross-corpus generalization requires separate landing.
- Does NOT test cf-RPE STDP heterogeneous compose, modern_hopfield cleanup, brain_compose stack (each requires its own intra-lane cell on PTB if pursued).
- Does NOT establish whether substrate can match transformer-LM perplexity on PTB (transformer is not an INTRA_LANE arm; the only TAGGED two-paradigm comparison here is to word-bigram).

## CONFOUND_AUDIT (apples-to-apples 2x drill standing discipline)

Per `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`:

| Field | Value |
|-------|-------|
| corpus | PTB-word-level (Mikolov split; wojzaremba/lstm) |
| encoder_paradigm | word2vec_sparse_bipolar_f0.05 |
| N_DIM | 8192 |
| vocab | PTB-V10000 (incl `<unk>` + `<eos>`) |
| metric_primary | BPW (bits-per-word) |
| baseline_paradigm | word-bigram-add-alpha=0.001 (tagged cross-paradigm) |
| lane | Lane 2 (intra-corpus substrate-vs-substrate + tagged bigram) |

mechanism_paradigm (substrate variants) != baseline_paradigm (word-bigram). Therefore the substrate-vs-bigram comparison is TAGGED as two-paradigm; substrate-vs-substrate ablations (K=1 vs K=2; fixed vs adaptive cf-RPE) are intra-lane.

## Honest Scope Statement (atomization guide)

Substrate clearing word-bigram on PTB by >= 0.30 BPW = "PTB-word-level substrate-as-LM viable; clears canonical NLP real-LM baseline on canonical NLP benchmark."

Substrate failing to clear word-bigram on PTB = "PTB-word-level substrate-as-LM bounded below word-bigram; the previous text8 substrate-as-LM landings (fair_harness 7.31, K2 etc.) are characterizing text8-encoding-specific behavior, NOT general LM capability." (Note: this is the load-bearing negative-result framing; the text8 fair_harness landings are not REVOKED by a PTB HARD_FAIL_DECISIVE -- they remain measurements on text8 with their text8 provenance tags -- but their generalization to canonical NLP is constrained.)
