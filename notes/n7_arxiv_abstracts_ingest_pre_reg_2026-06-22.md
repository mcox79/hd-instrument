# N7 arxiv-abstracts ingest-cert pre-reg

**Filed:** 2026-06-22T05:27Z by exp_dev. Tier-2 ingest-breadth expansion per USER do-it-all directive.

## Cell
- `experiments/exp_n7_arxiv_abstracts_ingest_cert_v1.py` (anchor `n7_arxiv_abstracts_ingest_cert_v1`)
- Plugin: SubstrateCharLM (substrate-only; zero transformers/torch import).
- Corpus: arxiv abstracts (HF multi-fallback; loader tries `ccdv/arxiv-classification` -> `armanc/scientific_papers` config=arxiv -> `arxiv_dataset` in that order; cache at `data/arxiv_abstracts_cache/`).
- Char-level scientific-text small-vocab technical English.

## Config (full run)
- N_DIM=4096 / N_LAYERS=4 / ALPHA_MAX=0.10 / N_STEPS_PER_LAYER=3
- MAX_CHARS_TRAIN=2_000_000 / MAX_CHARS_TEST=100_000
- SEEDS=[7,17,23]
- ALLOW_SYNTHETIC=False (fail-loud; vocab>=40 also asserted)

## Pre-registered bands (absolute-floor; baselines: bigram ~3.8-4.2, 5gKN ~2.4-2.8, LSTM ~1.6-2.0)
- HARD_PASS (chain-grade): substrate_bpc <= 2.80 AND cv <= 0.05 AND gain_vs_ceiling >= 0.05 AND zero LLM calls AND corpus_provenance_real AND run_mode=full
- MIDDLE_BAND: 2.80 < substrate_bpc <= 4.20 (or pass-bpc + cv>0.05 demote, or near-ceiling saturated demote)
- HARD_FAIL: substrate_bpc > 4.20, OR LLM violation, OR synthetic fallback, OR primitive collapse, OR run_mode=smoke

## Instrumentation (Skunkworks 4 chain-grade blockers; all baked)
1. per_unit row per seed
2. cv across seeds in verdict
3. zero_llm_calls_at_inference LOGGED + asserted
4. VQ-floor analog: bigram_ceiling_bpc + gain_above_bigram_ceiling

## Provenance gates
- ALLOW_SYNTHETIC=False
- vocab>=40 fingerprint (scientific text typically has vocab >= 60-80 in practice)
- corpus_provenance_real LOGGED per seed

## Selftest results (`--self-test`; .venv python)
- 9/9 PASS (T1-T9 same coverage as n6)

## Dispatch
- Queue: remote_cpu_queue (HF dataset cached on remote)
- Smoke gate first; full only if smoke is clean.

## Honest scope + risks
- HF arxiv-abstracts dataset availability is NOT guaranteed. Loader tries 3 candidates in order; if all fail (private/withdrawn/network), allow_synthetic=False raises RuntimeError -- the cert run refuses to silently fall back. SMOKE WILL SURFACE THE AVAILABILITY PICTURE on the remote runner.
- Corpus size depends on which HF dataset wins. Could be ~1M (small classification subset) to ~50M+ chars (full scientific_papers). MAX_CHARS_TRAIN caps the cell's budget independently.
- First-pass cell; substrate-LM plugin may shift if Tier-1 closes the gap.

## Wall estimate (per-seed; full)
- Same harness as n6/n3 text8; per-seed bigram ~10-20s + substrate fit ~5-15 min + score ~1-3 min
- 3 seeds: ~20-60 min full
- Smoke: ~15-60s (mostly dataset download on first run)

## What this measures
Whether the substrate-native char-LM, trained on arxiv abstracts (scientific-text technical English, smaller domain-specific corpus), beats the 5-gram-KN bar (2.80 BPC absolute floor). Probes whether the substrate generalizes ingest beyond cleaned Wikipedia / natural language to a domain-specific scientific register. Complements n6 (WikiText-103) on the language-breadth axis.
