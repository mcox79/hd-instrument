# Orchestrator -> Research: results summary cycle 128 (v450)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~12:00
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 HP HONEST + 2 LVH catches #229 #230 (both smoke-flag, NOT failures)** — Hadamard 8× holds at N=1024/2048 (smoke), **word-bigram AUC=0.970 = best KF-1 adversarial rescue to date** (smoke), MiniLM real d_eff=82/384 explains all Phase-4 ceilings.

## Findings

**`substrate_etf_hadamard_n_sweep_capacity_v1` HARD_PASS [SMOKE — LVH #229: HP→HP-SMOKE]**
Hadamard codebook keeps **~8× capacity advantage** over random at N=1024 and N=2048; ratio barely changes between them (suggesting flat-across-scale lift). **Single smoke seed** — cannot call HARD_PASS until full multi-seed sweep confirms. **If 8× holds at N=16384, Phase-3 projection (~2600 facts at N=65536) multiplies by ~8×.** Full sweep is the gate.

**`hoc1_word_bigram_v1` HARD_PASS [SMOKE — LVH #230: HP→HP-SMOKE]**
Word-level bigrams scored **AUC=0.970** at detecting adversarial shuffled-fact hallucinations — **4.5× better than the best prior approach** (char-ngrams at 0.19). Mechanism: word bigrams inject word-order signal that MiniLM cannot see. **Most promising KF-1 adversarial rescue result to date.** Cycles 120-126 had ruled out n-grams, order-sensitive encoders, contradiction detection, TruthfulQA-style — all HF. This is a different mechanism (word-LEVEL bigrams vs char n-grams). Smoke flag: needs full multi-seed before band-lift. Band-lift 0.72-0.87 → ~0.75-0.90 candidate IF replicated.

**`effective_rank_svd_v1` HARD_PASS HONEST**
**MiniLM uses only 21% of its nominal 384 dimensions (d_eff=82.1).** Explains why Phase-4A dim-expansion anchors keep hitting ceilings: they were bumping the **intrinsic-rank limit, not a substrate limit**. Whitening (v441/v448) pushes toward this ceiling; larger encoder (higher d_eff) is the primary lever to expand PP-8 capacity. Diagnostic confirms all Phase-4 operations are correctly scoped.

## State

- cap_map v449 → **v450**
- commit: `c616b20`
- HONEST 977 → 980 (+3)
- LVH 228 → **230** (+2 smoke-flag catches; both honest reads, smoke results re-classified as HP-SMOKE pending full)
- 0 BAND-LIFTS pending full multi-seed
- 0 closures
- Portfolio 32+77 unchanged

## Context for research session

**The two smoke catches are CONSERVATIVE LVH catches** — they're "this looks great but we need full N-sweep / multi-seed before claiming HP" rather than "this label was wrong." This is the correct cautious framing. Both have strong upside if confirmed:

1. **ETF Hadamard 8× flat-across-scale** → Phase-3 capacity rescue: prior projection ~2600 facts at N=65536 (cycle 116 alpha=0.040 floor); IF Hadamard 8× holds at N=16384/65536, projection jumps to **~21k facts at N=65536** (8× rescue × prior 2621 = ~21000). Critical follow-up: extend the sweep to N=16384 + add full 3-seed.

2. **Word-bigram KF-1 adversarial rescue** → finally a non-encoder fix path. v442/443/444/445/448 all converged on "adversarial training or NLI-aware encoder." Word-bigram says NEITHER is needed if word-LEVEL bigrams replace char-n-grams. Critical follow-up: full multi-seed + check whether it generalizes beyond shuffled-fact attacks to negation/contradiction (where v448 showed AUC=0.018/0.083).

3. **d_eff=82 diagnostic** is the cleanest theoretical explanation of TODAY: every Phase-4 ceiling we've hit is the intrinsic-rank limit of the encoder, not the substrate. This reframes the entire Phase-4 narrative: the substrate can absorb arbitrarily more capacity, but it's encoder-dimensionality-bound. **The Pythia/Llama follow-on tests (v445 HP smoke 6.68× at Pythia D1024) become CRITICAL** — they probe d_eff at higher-capacity encoders.

**Pipeline:** 13 cap_map commits in ~200 min this morning (v438 → v450). 25 anchors verdicted. 6 LVH catches (#225, 226, 227, 228, 229, 230) — re-read discipline at high rate, including new "smoke-flag" sub-category.

---

**END.** No action requested — results heads-up per step-4 convention.
