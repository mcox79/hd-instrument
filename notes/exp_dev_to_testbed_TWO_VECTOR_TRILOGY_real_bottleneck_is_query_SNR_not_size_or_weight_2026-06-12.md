# Exp-Dev -> Testbed/Research: two-vector index TRILOGY -- the production index's real bottleneck is QUERY SNR (cue quality), NOT atom count or the mixing weight. Invest in query encoding; wide margin everywhere.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-physics of the PRODUCTION two-vector index
(composite_hrr = normalize(algebra_hrr + 0.5*name_vec), PP-410, backend/substrate_index/algebra_index.py). NO LLM. GPU, N=1024.
Three cells, each pre-registered; honest look-harder arc (saturated -> diagnose -> boundary-map -> locate real bottleneck).

## The trilogy
**1. alpha PLATEAU (exp_two_vector_alpha_plateau_gpu_v3)** -- robust band alpha in [0.15, 10] (~70x), shipped 0.5 CENTRAL.
   NO delicate knee: in high-D, name_vec and algebra_hrr are near-orthogonal so they superpose without interference. Lower edge
   ~0.15 (identity onset), upper edge ~10-20 (structure swamped by name).
**2. SCALING (exp_two_vector_scaling_law_gpu_v1)** -- at shipped alpha=0.5/N=1024, identity_prec@1 AND struct_recall@5 both
   stay 1.0000 from 500 to 32000 atoms (>=18x the current ~1742). Atom count is NOT the limit; ceiling not even reached.
**3. QUERY SNR -- the REAL bottleneck (exp_two_vector_query_snr_bottleneck_gpu_v1)** -- fix n=8000, sweep cue degradation:
   | cos(cue,name) | 1.00 | 0.96 | 0.86 | 0.71 | 0.55 | 0.45 | 0.32 | 0.20 | 0.12 |
   | identity_prec@1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.998 | 0.853 | 0.259 | 0.049 |
   Identity holds (>=0.90) down to **cos(cue,name) ~ 0.45**; half-fails ~0.32; collapses below 0.20.

## Conclusion (actionable)
- The two-vector index is robust in TWO dimensions that intuition flags as risky -- the mixing weight (robust over ~70x) and
  atom count (robust over >=18x, ceiling not reached). Neither needs attention for any realistic near-term substrate.
- The SOLE real operating constraint is QUERY SNR: how well the retrieval cue matches the stored name_vec. And even that is
  generous -- a query encoder need only produce a cue ~45% aligned to the true name for near-perfect identity retrieval.
- **Where to invest:** query/cue encoding quality, NOT a larger N and NOT re-tuning the 0.5 weight.

## CORRECTION / scope (verified against algebra_index.py after first draft -- two distinct retrieval paths)
- The trilogy measures **composite_hrr IDENTITY retrieval, which is ATOM-KEYED**: retrieve_by_composite(atom_id, top_k) ->
  identity-similar atoms (used for compose/decode/cleanup). name_vec = HRR bundle of the atom's hashed name + id-path TOKENS
  (_name_vec). So the cos~0.45 threshold is the tolerance of the ATOM-KEYED identity channel to a degraded atom-cue.
- **Free-text A-axis queries do NOT hit composite_hrr** -- per the module design they route through the semantic-bge Index 1
  (algebra-vec was net-negative in the free-text composite, FINDINGS_04). So my first-draft line tying the cos~0.45 number to
  the A-axis conflated two paths; retracted.
- What DOES generalize is the PRINCIPLE, not the number: every retrieval path is ultimately query-SNR-bound (cue-to-target
  alignment), and the index/weight/capacity are not the limit. For the ATOM-KEYED composite path the margin is generous
  (cos~0.45). For the FREE-TEXT A-axis path the relevant cue is the BGE semantic embedding, a SEPARATE measurement (its own
  threshold), and the right lever there is bge query encoding -- consistent with the prior A-axis finding (Testbed-tuned UNION,
  bge-bound), not the two-vector name_vec.

## Routing
- **Testbed:** no index change needed for substrate growth (>=18x headroom) or weight (70x robust) on the ATOM-KEYED composite
  identity channel. That channel tolerates a cue down to cos~0.45. Free-text A-axis is a SEPARATE (bge) path -- its lever is bge
  query encoding, not the two-vector index. Cells importable for re-measurement.
- **Research:** clean substrate-product positioning -- the two-vector index stores identity+structure in one vector with the
  mixing weight and capacity both non-critical (structural properties of high-D superposition); the only tunable that matters
  is cue quality, with a wide (cos~0.45) margin. NO LLM.
- **Exp-Dev:** trilogy complete via honest arc (v1/v2 saturated, NOT reported as a knee; diagnosed; mapped; located the real
  bottleneck). Holding.
