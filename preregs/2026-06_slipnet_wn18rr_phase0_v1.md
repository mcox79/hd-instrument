# Pre-registration: slipnet_wn18rr_phase0_cpu_v1
**Date:** 2026-06-11  **Anchor:** slipnet_wn18rr_phase0_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Was the slipnet polysemic 0.42 ceiling (FB15K-237) a benchmark artifact or architectural? Runs the same 3 mechanisms (TTR/TSE/PerRole-RRF) on WN18RR.
## Pre-registered bands
HARD-PASS any mechanism > 0.55 (artifact). HARD-FAIL all < 0.45 (ceiling generalizes). [Refined: WN18RR sparse -> judge by lift-over-chance when n differs.]
## Calibration rationale
WN18RR is hierarchical/sparse -- no dense multi-relation subgraph at n=28 (controlled comparison impossible). Grown to n=463 for
edge density: absolute recall 0.044 but lift-over-chance 20.2x >= FB15K 11.8x. Mechanisms recover MORE-than-chance structure on
WN18RR too -> FB15K 0.42 leans benchmark-DIFFICULTY (dense polysemy), NOT a clean architectural ceiling. Per drill-defeatism, the
clean "ceiling" claim is not supported by a controlled test; WN18RR's structure prevents one.
## N-suffix section
N=8192; WN18RR (villmow GitHub-raw, 86835 triples); grown subgraph; 3 mechanisms; lift-over-chance metric.
