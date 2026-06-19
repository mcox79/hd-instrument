# Exp-Dev -> Testbed/Research: BOTH channels of the production two-vector design are now validated on the REAL substrate -- identity (composite_hrr 0.996) AND structural (algebra_hrr Pearson 0.99 vs dict-overlap, identical dicts collide perfectly).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-physics on the PRODUCTION index, REAL atoms. NO LLM.
**Cell:** exp_two_vector_structural_channel_real_substrate_cpu_v1.py (numpy + PartitionedStore, local-safe). Completes the
real-substrate validation begun with the identity-channel cell.

## Structural channel (algebra_hrr) on 242 real covered atoms
The two-vector design intends algebra_hrr to encode STRUCTURAL similarity (collisions DESIRABLE; identical algebra dicts ->
identical vectors). Tested vs algebra-dict (key,value) Jaccard overlap:
- **identical-dict pairs (jac>=1): n=49, mean cosine = 1.0000** -- perfect collisions, exactly as designed.
- **among atoms sharing >=1 dict field (jac>0, n=4881 pairs): Spearman = 0.861, Pearson = 0.987** -- algebra_hrr cosine tracks
  dict overlap near-linearly.
- **zero-overlap pairs (83pct): mean cosine = -0.003** -- orthogonal, as designed (no shared structure -> no similarity).
- within-category_int cosine 0.467 vs between-category 0.001; binned means strictly monotone (jac 0.01->0.19, 0.4->0.67, 0.7->1.0).
- NOTE (honest metric): all-pairs Spearman is 0.449, DEFLATED by the 83pct zero-overlap pairs tied at cos~0 (correct behavior
  but unrankable). The faithful metric conditions on jac>0; that gives 0.86 / Pearson 0.99. (Caught + corrected a tie artifact.)

## Both channels confirmed on real data
| channel | role | real-substrate result |
|---|---|---|
| composite_hrr (IDENTITY) | per-atom-unique, collision-resistant | clean-cue id_prec@1=0.996; robust to cue degradation down to cos~0.32 |
| algebra_hrr (STRUCTURAL) | shared-structure, collisions desirable | dict-overlap->cosine Pearson 0.99; identical dicts cos=1.0; zero-overlap cos~0 |

The production two-vector design (PP-410) does exactly what it claims on the ACTUAL substrate: identity and structure are
cleanly separated channels, each faithful to its purpose. Combined with the trilogy (weight-robust 70x, capacity-robust 18x+),
the index is now characterized and validated end-to-end on real atoms.

## Routing
- **Testbed:** both retrieval channels are production-validated on real atoms; no index changes indicated. Cells re-runnable
  after ingestion (structural-channel coverage tracks the 242->grows as algebra backfill lands; see coverage-gap diagnosis).
- **Research:** clean substrate-product artifact -- the substrate stores identity + structure in one vector, each channel
  empirically faithful on real data (identity 0.996, structural Pearson 0.99). NO LLM.
- **Exp-Dev:** two-vector real-substrate validation COMPLETE (both channels). Holding.
