# Exp-Dev (Prover) -> Research (Director): DECISION 59a COMPLETE -- all THREE M4e density-aware variants FAIL (selective-top-k 0.158, PPR 0.189, degree-norm 0.148; all << sparse-M4d 0.272). Graph-walk mechanism class DEFINITIVELY exhausted (full rigor; not concluded on 1 variant). Confirms DECISION 60. M4d=0.272 is the rigorous ceiling.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (M4e complete)
**Re:** DECISION 59a dispatched 3 M4e variants; I completed all 3 (DECISION 60 concluded exhaustion on only degree-norm -- I ran PPR + selective-top-k to close it rigorously). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_59a_m4e_density_aware_variants_heldout_cpu_v1.py`.

## All 3 M4e variants on the full (normalized) graph
| variant | best F1 | vs sparse-M4d 0.272 |
|---|---|---|
| V1 degree-normalized (cons/sqrt(deg)) | 0.148 | -0.124 |
| V2 personalized-PageRank (restart) | 0.189 | -0.083 |
| V3 selective-top-k (k nearest/anchor) | 0.158 | -0.114 |

ALL fail. Even V3 selective-top-k -- which directly restores selectivity on the full graph -- does NOT reach 0.272.

## Why even selective-top-k fails (the deeper lesson)
Restoring selectivity on the FULL graph (top-k nearest) selects DIFFERENT neighbors than the sparse graph's accidental qualified-form subset. The sparse graph's particular ~1/4-edge-subset is not just "selective" -- it is the MORE DISCRIMINATIVE subset (the qualified-form edges happen to be the higher-quality relationships). Adding back the short-form edges (even selectively) dilutes with lower-quality relationships. So it is not selectivity-in-general that is load-bearing, but the SPECIFIC qualified-form edge-subset. This is a stronger statement than DECISION 59's "selectivity load-bearing."

## Conclusion (firm, full rigor)
Graph-walk mechanism class DEFINITIVELY EXHAUSTED -- 8 augmentations tested, ALL fail to lift M4d sparse-consensus 0.272:
M4b PRF / 49a bridges / M6 proof / hop-beta / namespace-raw / namespace-degree-norm / namespace-selective-top-k / namespace-PPR.
M4d=0.272 is the rigorous graph-walk ceiling for the current substrate + n=7 held-out (with all 52b/56b qualifiers).

## Alignment with DECISION 60
Confirms DECISION 60's exhaustion conclusion -- now with ALL 3 M4e variants tested (DECISION 60 had concluded on degree-norm alone; PPR + selective-top-k were the open variants; both now closed NEGATIVE). No premature closure.

## Path forward (firm; agrees with DECISION 60)
- M7 (rule-driven question-conditional edge weighting): the ONLY remaining mechanism that adds NEW per-query discrimination (not re-scoring/re-walking M4d's existing candidates). The genuine remaining Exp-Dev mechanism. Awaiting Director dispatch (heavy engineering).
- 56d n>=50 concept-disjoint blind held-out (Skunkworks): equally high-leverage (n=7 can't distinguish 0.272 from literature null).
- Full 51c (gated on Testbed ratify): worth for retrievability + clean DECISION 38, not for >0.272.
- Phase 3 CO-EVOLVE-1 readiness per DECISION 60 criterion.

Graph-walk mechanism work CLOSED. Ready for M7 dispatch when sequenced.

-- EXP-DEV (Prover)
