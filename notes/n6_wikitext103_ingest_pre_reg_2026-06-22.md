# N6 WikiText-103 ingest-cert pre-reg

**Filed:** 2026-06-22T05:27Z by exp_dev. Tier-2 ingest-breadth expansion per USER do-it-all directive.

## Cell
- `experiments/exp_n6_wikitext103_ingest_cert_v1.py` (anchor `n6_wikitext103_ingest_cert_v1`)
- Plugin: SubstrateCharLM (4-primitive bipolar-bind streaming Hebbian + anti-Hebbian contrastive). Substrate-only at inference; zero transformers/torch import.
- Corpus: HF `wikitext` config `wikitext-103-raw-v1` (loader added to `testbed/substrate_lm/data.py`; cache at `data/wikitext103_cache/`).
- Char-level (matches text8/n3 cert pattern; absolute-floor BPC bands map directly).

## Config (full run; ALL BPC-affecting params in CONFIG_VERSION)
- N_DIM=4096 / N_LAYERS=4 / ALPHA_MAX=0.10 / N_STEPS_PER_LAYER=3
- MAX_CHARS_TRAIN=2_000_000 / MAX_CHARS_TEST=100_000
- SEEDS=[7,17,23] / TRAIN_FRAC implied via HF train/validation splits
- ALLOW_SYNTHETIC=False (fail-loud; vocab>=50 also asserted)

## Pre-registered bands (absolute-floor; baselines: bigram ~3.5-4.0, 5gKN ~2.2-2.5, LSTM ~1.5-1.8)
- HARD_PASS (chain-grade): substrate_bpc <= 2.50 AND cv <= 0.05 AND gain_vs_ceiling >= 0.05 AND zero LLM calls AND corpus_provenance_real AND run_mode=full
- MIDDLE_BAND: 2.50 < substrate_bpc <= 4.00 (or pass-bpc + cv>0.05 demote, or near-ceiling saturated demote)
- HARD_FAIL: substrate_bpc > 4.00, OR LLM violation, OR synthetic fallback, OR primitive collapse, OR run_mode=smoke

## Instrumentation (Skunkworks 4 chain-grade blockers; all baked)
1. per_unit row per seed (recompute-ready)
2. cv across seeds in verdict
3. zero_llm_calls_at_inference LOGGED + asserted in verdict
4. VQ-floor analog: bigram_ceiling_bpc (bigram-MLE fit on TEST) + gain_above_bigram_ceiling

## Provenance gates
- ALLOW_SYNTHETIC=False (RuntimeError on no real data)
- vocab>=50 fingerprint (synthetic uses fixed 78-char ASCII; WT-103 typically has unicode/diacritics pushing vocab >= 80 in practice)
- corpus_provenance_real LOGGED per seed; HARD_FAIL if any seed synthetic

## Selftest results (`--self-test`; .venv python; local)
- 9/9 PASS (T1-T9: bigram baseline / SubstrateCharLM mini-pipeline / zero-D fallback / LLM=0 / CONFIG_VERSION / per_unit shape / verdict direction / ceiling==baseline identity / Fix #4 smoke-refuse)

## Dispatch
- Queue: remote_cpu_queue (HF dataset cached on remote; ~100MB on first download)
- Smoke gate first; full only if smoke is clean.

## Honest scope
- First-pass ingest cell. If Tier-1 cells (n4 / Path A / Path B) close the bigram gap on text8/N1, the substrate-LM plugin may shift; this cell would re-run on the better plugin.
- ConceptNet handled by separate spawn (don't duplicate).
- math/code corpora scoped by separate research drill.

## Wall estimate (per-seed; full)
- Bigram count+score over 2M train chars: ~10-20s
- SubstrateCharLM fit over 2M chars N=4096 L=4 steps=3: extrapolate from n3_text8 (same harness; same N/L/steps): ~5-15 min train + ~1-3 min score = ~6-18 min per seed
- 3 seeds total: ~20-60 min full run
- Smoke (10k train / 1k test / N=512 L=2): ~15-60s

## What this measures
Whether the substrate-native char-LM, when trained on real WikiText-103 (cleaned Wikipedia, ~100M tokens standard LM benchmark), beats the 5-gram-KN bar (2.50 BPC absolute floor) on char-level prediction. Probes generalization beyond text8 (the cleaner subset) and the Pythia-residual token-level path (no LM at inference).
