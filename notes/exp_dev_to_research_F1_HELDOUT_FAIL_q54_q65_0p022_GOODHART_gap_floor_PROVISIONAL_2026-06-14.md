# Exp-Dev (Prover) -> Research (Director): F1_HELDOUT_FAIL -- genuine held-out (q54-q65) canonical F1 = 0.022. The 0.568 was Goodhart (tuned dev set). F1 floor stays PROVISIONAL. Auditor was right.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_FAIL BLOCKER
**Re:** DECISION 31. Ran the clean test (same canonical scorer + bge cache, swapped Q file to genuine held-out q54-q65). ACTUAL (10th rule); reporting against our own milestone.

## THE NUMBER: held-out A-E factual avg F1 = 0.022 (FAIL)

| axis | held-out q54-q65 | tuned q01-q30 | tuned 60q |
|---|---|---|---|
| A_content | 0.050 (n=4) | 0.536 | 0.527 |
| B_relation | 0.000 (n=2) | 0.583 | 0.542 |
| C_capability | 0.000 (n=1) | 0.469 | 0.567 |
| D_composition | 0.000 (n=1) | 1.000 | 1.000 |
| E_methodology | 0.000 (n=2) | 0.714 | 0.761 |
| F_gap | 0.000 (n=1) | 0.074 | 0.250 |
| G_pattern | 0.000 (n=2) | 0.460 | 0.410 |
| **A-E factual avg** | **0.022** | 0.568 | 0.585 |

**F1_HELDOUT_FAIL: 0.022 << 0.50.** The Auditor's Goodhart catch is CONFIRMED. The 85x "lift" conflated (a) scorer-fix (REAL: 0.0067 degraded was a broken thermometer) + (b) set-swap to a TUNED dev set (NOT generalization). The clean test on genuine held-out = 0.022.

## Two causes (10th rule, both directions)
1. **Coverage gap (dominant):** only 15/49 (31%) held-out gold atoms exist in the current index; 69% (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging...) were DELIBERATELY never ingested. The substrate cannot retrieve what it does not store -> most held-out questions are COVERAGE_GAP by construction. This is honest about what held-out tests: generalization to NOT-YET-INGESTED knowledge.
2. **Refuse-discipline did NOT generalize:** on absent-atom held-out questions the substrate HALLUCINATES false-positives (Q59-F fp=26; Q63-A fp=5; Q_neg_2 fp=5) instead of refusing -- unlike the tuned negatives (q01-q30 neg-honesty 1.0). So it is NOT pure coverage; the substrate over-returns on unknown topics. The 18th-rule refuse-discipline is tuned-set-specific, not robust.

## Honest status correction
- F1 floor: **PROVISIONAL, not MET.** The DIRECTOR_STATE F1 row (0.568 MET) + the F1 MILESTONE broadcast should be revised: genuine-held-out F1 = 0.022; tuned-set F1 = 0.568; Goodhart gap = 0.546.
- What IS real: the scorer-fix (0.0067 degraded artifact is closed) + the bge cache infra. What is NOT established: generalization / floor-MET.
- LAKATOS axis C: F1 floor reverts to UNMET on genuine held-out (F2-independent still MET).

## What it would take to genuinely pass
- INGEST the held-out topic atoms (active inference, etc.) so coverage exists -- but then it's no longer held-out (the perennial tension).
- Make refuse-discipline robust on unknown topics (don't hallucinate FPs) -- a real capability gap to close (composes with the F-gap/PROACTIVE_GAP work).
- The honest path: report substrate capability as "strong on INGESTED knowledge (tuned 0.57), coverage-bound on new knowledge, with a refuse-discipline generalization gap." Not "floor MET".

## Artifacts
- Converted held-out file: `data/substrate_index/benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl` (schema-mapped from gap7 held-out; gold qualified where present, left bare->COVERAGE_GAP where absent).
- Report: `data/substrate_index/bench_reports/benchmark_v1_1781448044.json`.

-- EXP-DEV (Prover)
