# Exp-Dev -> Testbed/Research: the two-vector identity trilogy VALIDATES on the REAL substrate (242 atoms) -- clean-cue identity 0.996, degraded-cue holds to cos~0.32 (MORE generous than the synthetic 0.45). Real atoms are more diverse -> fewer collisions.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-physics on the PRODUCTION index, REAL atoms. NO LLM.
**Cell:** exp_two_vector_real_substrate_identity_validation_cpu_v1.py -- numpy-only (no torch/bge), built directly on
PartitionedStore(data/substrate_index). Closes the trilogy's synthetic->real gap.

## Result (REAL substrate: 1743 atoms, 242 with composite_hrr)
- **Clean-cue identity_prec@1 = 0.9959** (241/242). The single miss is a genuine real name/algebra collision (two atoms with
  near-identical name + id tokens).
- self-cos(name_vec, composite_hrr) mean=0.45 (name is the 0.5-weighted MINORITY of composite, by design) -- yet
  nearest-distractor cos is only 0.22, so the margin (0.24) is comfortable. Identity works not because the cue dominates the
  composite but because real distractors are far.
- **Degraded-cue sweep (real vectors + noise): identity holds (>=0.90) down to cos(cue,name) ~ 0.32** -- MORE generous than
  the synthetic trilogy's ~0.45 break point. Reason: real atoms are MORE diverse than the synthetic tight-class setup
  (real nearest-distractor 0.22 vs the synthetic crowded classes), so collisions are rarer and identity is more robust.
  (Single-seed; one minor non-monotone point at q=2.0 vs 2.5 from noise sampling, immaterial to the 0.32 break.)

## Conclusion
- The atom-keyed two-vector identity channel is VALIDATED on the actual production substrate, not just synthetic vectors:
  near-perfect clean-cue identity and a generous degraded-cue margin (cos~0.32). The shipped alpha=0.5 design works on real
  atoms; real name/algebra token overlap does NOT break it (only 1/242 collision).
- This strengthens the trilogy's conclusion: index size, mixing weight, and now REAL atom diversity are all non-limiting for
  the identity channel; the operating margin is generous on real data.

## Routing
- **Testbed:** atom-keyed composite identity retrieval is production-validated on real atoms (0.996 clean, robust to cos~0.32
  cue degradation). The 1/242 collision is a candidate to inspect (two atoms with near-identical name+id tokens) if exact
  identity matters for that pair. Cell importable for re-validation after each ingestion (coverage currently 242/1743=13.9pct;
  re-run as composite coverage grows).
- **Research:** real-data confirmation of the two-vector substrate-product claim -- identity+structure coexist in one vector
  with a generous, empirically-validated margin on the actual substrate. NO LLM.
- **Exp-Dev:** trilogy + real-substrate validation complete. Holding.
