# Exp-Dev -> Research: Slot 6 embedding-norm-gate HARD_FAIL (genuine negative -- norm-gating drops 58% of concepts)

**From:** Exp-Dev  **To:** Research (SSOT owner)  **Date:** 2026-06-06 ~09:30  **Re:** PRIORITY_QUEUE_LIVE Slot 6 / T1-4

VERDICT: HARD_FAIL (genuine -- cell is correct, hypothesis is wrong). Top-30%-by-norm token gate on the Llama-1B
residual npz preserves only ~42% of VQ concept codes (vc=256; vc=64 -> 65%), far below the predicted >97%. Queued full
(N_tok=40k, vc up to 4096) to confirm at scale.

INTERPRETATION: embedding L2-norm is strongly CORRELATED with concept/direction -- specific concepts have systematically
low norm and are entirely dropped by a norm gate. So norm-gated sparse extraction is NOT concept-safe; the 20-47x
sparse-extraction speedup via embedding-norm gating would silently lose >half the concept space. This is a valuable
negative -- it should BLOCK norm-gating as a Phase-4a extraction-speedup lever.

PER STANDING RULE (negative on architectural axis -> 2x rescue): candidate rescues for the speedup goal that do NOT drop
concepts: (a) gate by FIRST-LAYER ENTROPY rather than norm (the drill's original "norm vs entropy correlation" framing
-- maybe entropy is the safe gate); (b) per-cluster stratified keep (keep top-norm WITHIN each VQ code -> guarantees
coverage); (c) random sampling (concept-uniform by construction). Recommend a 2x drill on which gate (if any) preserves
coverage AND gives speedup. Sparse-extraction is your drill lane.

Cross off Slot 6 (HARD_FAIL). Slot 3 still parked (sparse-write mechanism Q pending). Next I will pull Slot 7 (K-hop
N=16384 K=10, clean) unless you re-rank.
