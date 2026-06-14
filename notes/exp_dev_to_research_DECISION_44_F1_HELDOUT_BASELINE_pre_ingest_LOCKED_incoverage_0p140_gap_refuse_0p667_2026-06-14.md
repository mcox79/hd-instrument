# Exp-Dev (Prover) -> Research (Director): DECISION 44 DONE -- F1_HELDOUT_BASELINE_pre_ingest LOCKED. IN-COVERAGE macro-F1=0.140 + COVERAGE-GAP refuse-rate=0.667 (FP=31). H_M4 vs H_INGEST reference fixed for post-ingest comparison.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_BASELINE_pre_ingest
**Re:** DECISION 44. Canonical scorer (with 39a type-G bge fallback) on held-out q54-q65. Current pre-ingest substrate. ACTUAL (10th rule).

## LOCKED BASELINE (pre-ingest, post-39a)

### Per-question (13q)
| qid | type | F1 | tp | fp | fn | bucket |
|---|---|---|---|---|---|---|
| Q54-A | A | 0.00 | 0 | 0 | 5 | in-cov |
| Q55-B | B | 0.00 | 0 | 0 | 1 | in-cov |
| Q60-G | G | 0.44 | 2 | 3 | 2 | in-cov |
| Q61-A | A | 0.29 | 1 | 1 | 4 | in-cov |
| Q62-B | B | 0.00 | 0 | 0 | 6 | in-cov |
| Q63-A | A | 0.00 | 0 | 1 | 5 | in-cov |
| Q64-G | G | 0.25 | 1 | 4 | 2 | in-cov |
| Q56-C | C | 0.00 | 0 | 0 | 11 | gap (refuse) |
| Q57-D | D | 0.00 | 0 | 0 | 0 | gap (refuse) |
| Q58-E | E | 0.00 | 0 | 0 | 2 | gap (refuse) |
| Q59-F | F | 0.00 | 0 | 26 | 4 | gap (HALLUCINATE) |
| Q65-E | E | 0.00 | 0 | 0 | 2 | gap (refuse) |
| Q_neg_2 | A | 0.00 | 0 | 5 | 0 | gap (HALLUCINATE) |

### Decomposed (DECISION 32 metric)
- **IN-COVERAGE (7q) macro-F1 = 0.140** (Q60-G 0.44 + Q61-A 0.29 + Q64-G 0.25; other 4 = 0). Concentrated in G-pattern (39a recoveries) + a sliver of A-content.
- **COVERAGE-GAP (6q) refuse-rate = 0.667** (4/6 refuse: Q56,Q57,Q58,Q65; 2/6 hallucinate: Q59 fp=26, Q_neg_2 fp=5). Total coverage-gap FP = 31.

### Per-axis (all 13q)
A_content=0.071 (n4) | B_relation=0.000 (n2) | C_capability=0.000 (n1) | D_composition=0.000 (n1) | E_methodology=0.000 (n2) | F_gap=0.000 (n1) | G_pattern=0.347 (n2). A-E factual avg=0.032 (excludes F/G; HP_v1 0.70 UNMET).

Sanity check: matches prior post-39a numbers (in-coverage 0.14, refuse 0.67). CONFIRMED.

## Pre-registered hypotheses (DECISION 38; reference now LOCKED)
- **H_M4:** IN-COVERAGE macro-F1 stays ~0.140 after ingest -> capability-transfer is the deeper issue; coverage expansion alone doesn't fix it -> M4 (query-side) genuinely needed.
- **H_INGEST:** IN-COVERAGE macro-F1 lifts substantially after ingest -> coverage expansion also helps capability-transfer.
- Decision rule: post-Option-1-ingest re-run; compare IN-COVERAGE macro-F1 vs this locked 0.140. Delta >= +0.15 -> H_INGEST; delta < +0.05 -> H_M4 confirmed.

## State
- This is the LOCKED pre-ingest reference. If USER authorizes Option 1 (wikidata structured), post-ingest re-run decides H_M4 vs H_INGEST. If USER declines, this 0.140 / 0.667 is the FINAL held-out number this session and H_M4 is confirmed by elimination (prose/synthetic have no path to lift in-coverage; architectural 0-edge finding).
- UNAFFECTED (substrate-product positioning): Tier 1+2 production-verified (HMM 0.90 etc), 100pct axiom termination, F2 INDEPENDENT 0.19, cross-domain L6-PROOF, 25 PROVABLY_EQUIVALENT 0 false-merges, BGE cache, pipeline infra validated.

## Awaiting
- USER binary decision: Option 1 (wikidata structured slice) vs Option NONE (this baseline final). The architectural 0-edge finding eliminated half-measures.
- DECISION 44 baseline COMPLETE; reference locked; ready for post-ingest comparison the moment real data lands.

-- EXP-DEV (Prover)
