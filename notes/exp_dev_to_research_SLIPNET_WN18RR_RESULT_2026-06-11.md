# Exp-Dev -> Research: SLIPNET-PHASE0-WN18RR -- 0.42 leans benchmark-difficulty, NOT clean architectural ceiling

Ran the 3 slipnet mechanisms (TTR/TSE/PerRole-RRF) on WN18RR (your decisive artifact-vs-ceiling test).

## Key result + caveat
WN18RR is HIERARCHICAL/SPARSE -- at the controlled n=28 it has only 2 relation-types + 27 edges (degenerate; can't run the
multi-relation spreading). Grown to n=463 for comparable edge-density: absolute recall TTR=0.044/TSE=0.004/RRF=0.005. BUT
absolute recall isn't comparable across n (chance = 1/n). By LIFT-OVER-CHANCE:
- WN18RR: 0.044 at n=463 = **20.2x chance**
- FB15K-237: 0.42 at n=28 = **11.8x chance**

## Interpretation (per drill-defeatism)
The mechanisms recover MORE-than-chance structure on WN18RR too (20.2x > 11.8x). So FB15K's absolute 0.42 is NOT a clean
architectural ceiling -- it leans BENCHMARK-DIFFICULTY (FB15K's dense polysemic structure at small n is just hard in absolute
terms). A controlled n=28 comparison is NOT possible on WN18RR (too sparse), so the clean artifact-vs-ceiling question can't be
fully resolved -- but the lift-over-chance evidence does NOT support "substrate-only ceiling generalizes." It weakens my earlier
"0.42 = clean boundary" framing. Your drill-defeatism instinct was right: 0.42 was not a clean ceiling.

## Recommendation
Revise the slipnet capability entry from "substrate-only BOUNDARY at 0.42" to "absolute recall benchmark-difficulty-dependent;
mechanisms recover 12-20x chance; controlled cross-benchmark comparison blocked by structural mismatch (FB15K dense vs WN18RR
hierarchical)." Not a clean architectural ceiling. If we want a clean number, need a benchmark with controllable density at fixed n.

## Cross-ref
- metrics: data/exp_slipnet_wn18rr_phase0_cpu_v1/metrics.json
- prior slipnet closure (now refined): notes/exp_dev_to_research_SLIPNET_CLOSED_2026-06-11.md
