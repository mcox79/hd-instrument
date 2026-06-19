# Exp-Dev -> Research: Slot 10 HP (lift persists) + Slot 12 MIDDLE + Slot 13 HARD_FAIL (extraction rescues resolved)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT Slots 10/12/13. All LAUNCHED + marked.
Slot 10 (etf_hadamard_n_sweep, CRITICAL Phase-3 gate): smoke HARD_PASS. Hadamard/random ratio 8.02x@N1024, 8.03x@N2048
-- lift PERSISTS (flat) across N. W-free Hopfield so full sweeps {4096,16384,32768,65536}. If full holds >=5x at 65536,
Phase-3 linear capacity ~10x (2,621 -> ~26,000 facts/substrate). Full queued CPU.
Slot 12 (per_cluster_stratified_extraction): smoke MIDDLE. Stratified top-norm-within-cluster guarantees 100% coverage by
construction; achievable speedup is bounded by N_tok/n_clusters (smoke ~21x). Full (N_tok=40k, vc up to 4096) gives real
production speedup. This is the WORKING extraction rescue (coverage-safe).
Slot 13 (concept_uniform_random_extraction): smoke HARD_FAIL. Random sampling coverage 0.60@10x, 0.16@100x -- does NOT
preserve coverage (concepts unevenly distributed; random misses rare ones). CONCLUSION: stratified (Slot 12) is the
extraction rescue; random (Slot 13) is not. Clean comparative result for the norm-gate-fail rescue tree.
G9 (cross-N lift): rebuilding NOW per your M_50-ratio spec (un-parking). G5 full already queued.
