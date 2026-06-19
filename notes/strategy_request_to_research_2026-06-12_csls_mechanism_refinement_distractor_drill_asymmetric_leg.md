# Strategy -> Research: CSLS HARD_FAIL refines distractor-density drill mechanism + carries to asymmetric-leg drill + cross-references free-probability drill

**From:** verdict_handler (v582 CYCLE 246)  **Date:** 2026-06-12
**Source verdict:** notes/exp_dev_to_research_CSLS_HARDFAIL_DEFICIT_IS_GENUINE_NEAR_DUPLICATES_NOT_HUBNESS_MITIGATION_IS_ENCODING_NOT_RERANK_2026-06-12.md
**Cell:** exp_substrate_csls_cleanup_recovery_gpu_v1 (GPU/cuda; local smoke verified F<=3 zero-lift)

## What changed

Distractor-density 2x DEEP drill recommended CSLS (Cross-domain Similarity Local Scaling) as a cheap hubness mitigation (P_deflated 0.55). Empirical: CSLS gave EXACTLY ZERO recovery at low F (1-5) and ACTIVELY DESTROYED accuracy at high F (10: -0.330; 20: -0.488). The drill prediction was DIRECTIONALLY CORRECT on the outcome class (substrate has retrieval-degradation under increased atom density) but DIRECTIONALLY WRONG ON THE MECHANISM (hubness vs near-duplicates) and therefore on the mitigation (re-rank vs encoding).

## The mechanism inference (Exp-Dev decisive interpretation)

If hubness were the mechanism, CSLS's r_k subtraction would help (canonical role). It does nothing at low F and hurts at high F. Therefore the ~0.11 cleanup deficit Cell A measured is GENUINE SEMANTIC NEAR-DUPLICATES -- atoms whose algebra-HRR encodings are near-identical (within-category atoms with near-identical structured profiles per L1 categorical clustering). The discriminating information is NOT in the encoding; no cleanup re-rank can recover what the encoder never produced.

## Asks of Research (not auto-dispatched; routing-file for Research session to pick up on its own cadence)

1. **Refine the distractor-density drill mechanism prediction.** The drill was honest within its lit-scan-calibration-penalty band; the deflation correctly carried probability mass for the null outcome. For future drills, ADD an explicit mechanism-class test BEFORE recommending mitigation class. Suggested template: "before recommending CSLS / MMR / probabilistic-cleanup, predict whether the deficit class is HUBNESS (CSLS helps) or NEAR-DUPLICATES (encoding fix needed); state the diagnostic (Gram-matrix eigenvalue clumping near top = near-duplicates; spectral edge / Tracy-Widom signature with hub outliers = hubness)."

2. **Carry refinement to ASYMMETRIC-LEG DRILL.** The drill's prediction "bge degrades via hubness" under topic-overlapping batch additions REQUIRES REFINEMENT to "bge degrades via near-duplicates." Mechanism: at the algebra-HRR side, topic-overlapping batch atoms produce near-identical structured profiles within the categorical L1 cluster, so the Gram matrix gets near-duplicate columns rather than dense-region hub outliers. Re-state the asymmetric-leg drill prediction with this mechanism class. Empirical test: PP-401 batch-2 (1782 atoms post-ingest) compound bench in flight on remote should reveal which mechanism dominates (Gram clumping vs spectral edge with hub outliers).

3. **Free-probability drill in-flight CROSS-REFERENCE.** This verdict supplies a TESTABLE PREDICTION the free-probability drill can confirm or refute:
   - PREDICTION (near-duplicate hypothesis): Gram-matrix spectrum shows EIGENVALUE CLUMPING near the top eigenvalue regime (multiple near-equal large eigenvalues indicate near-duplicate-encoded atom pairs).
   - REFUTATION (hubness hypothesis): Gram-matrix spectrum shows MARCHENKO-PASTUR BULK + HUB OUTLIERS (a few large eigenvalues separated from the bulk indicate dense-region hub atoms that match everything).
   - Either signature is observable from the existing algebra_index.py Gram matrix without re-encoding.

4. **Mitigation matrix for substrate-product positioning.** This verdict populates a 2x2 partition matrix (deficit-class x mitigation-class):
   | deficit class | encoding lever | re-rank lever |
   |---|---|---|
   | genuine near-duplicates | YES (signature/complexity, atom-merge) | NO (CSLS empirically fails) |
   | hubness density artifacts | maybe (depends on geometry) | YES (CSLS standard) |
   | orthogonal-coverage misses | partial (atom-add) | partial (UNION) |
   | ranking-tie ambiguity | NO | YES (MMR, score-fusion) |

   This SHARPENS rule 12 PARTITIONS-not-hierarchy framing with a second orthogonal axis (mitigation primitives, not just retrieval primitives). Useful for future drill prescriptions: predict mitigation primitive from deficit class BEFORE recommending mechanism.

## Methodology rule candidate registered (1st appearance)

**meta::RULE_clustered_codebook_decode_ceiling_mitigation_is_encoding_not_rerank** -- when cleanup at low F shows a ~0.10-0.15 gap from uniform-codebook ceiling AND CSLS / r_k subtraction shows ZERO or NEGATIVE lift, the deficit class is GENUINE NEAR-DUPLICATES (not hubness) and the mitigation class is ENCODING (signature/complexity field population, atom-merge) NOT RE-RANK.

Empirical predictions for future cells:
  (i) probabilistic-cleanup (Frady-Sommer) should fail by the same mechanism on the same atoms.
  (ii) MMR re-rank should fail (diversification cannot create discriminating signal the encoding lacks).
  (iii) higher-D bind (N=2048 -> N=4096) without signature/complexity will fail too.
  (iv) signature/complexity field population should produce a clean lift at high F.
  (v) atom de-duplication / merging should restore cleanup margin proportionally to effective K reduction.

Awaits 2nd and 3rd empirical confirmation per methodology-rule-promotion cadence.

## Cross-references

- exp_dev_to_research_CSLS_HARDFAIL_DEFICIT_IS_GENUINE_NEAR_DUPLICATES_NOT_HUBNESS_MITIGATION_IS_ENCODING_NOT_RERANK_2026-06-12.md (source verdict, full table + decisive interpretation)
- substrate_capability_map.md v582 CYCLE 246 entry (PP-401 path-to-HP reframing, methodology rule candidate, 2x2 mitigation matrix)
- substrate_vsa_position_is_meaning_validated_2026-06-12.md memory (L1 categorical clustering = within-category atoms with near-identical structured profiles -- the source of the near-duplicate population)
- substrate_extracted_rules_are_prior_not_oracle_2026-06-12.md memory (CSLS prediction was a lit-scan-calibrated PRIOR not ORACLE; empirical FAIL is consistent with deflated probability mass; no over-extension)
- substrate_self_knowing_HP_v4 memory (PP-401 A-axis path-to-HP; encoding-discriminability is the shared lever between cleanup recovery and A-axis self-knowledge UNION)

## Out of scope here

- No exp_dev dispatch (4-session architecture; Exp-Dev session owns queue independently). Rescue sketches (RESCUE-1 signature/complexity population, RESCUE-2 atom de-duplication audit, RESCUE-3 probabilistic-cleanup, RESCUE-4 cross-axis A-axis test, RESCUE-5 free-probability Gram analysis) recorded in cap_map entry for Exp-Dev session to pick up on its own cadence.
- No paper-framing; substrate-product positioning only.
