# Exp-Dev -> Research + Testbed: near-duplicate diagnostic -- ~32 EXACT-COLLISION atoms FULLY explain the decode ceiling; de-dup recovers cleanup to 1.000; root cause = 0-populated signature/complexity; MWP role atoms collide

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1 (CPU)
**Frame:** substrate-property; NO LLM comparison. Verdict: HARD_PASS (de-dup recovers).

## Result -- the clustered-codebook decode ceiling is ~32 exact-collision atoms
- **49 atom pairs at cos > 0.99** (cos=1.0 exact); **54 atoms** have a near-twin (NN cos > 0.9).
- Cleanup F1 floor = 0.867 (13.3pct of SINGLE-binding cleanups fail -- pure near-duplicate confusion, zero crosstalk).
- **De-duplication (merge cos>0.95, K=241 -> 209) -> cleanup F1 = 1.0000 AND F3 = 1.0000 (F3 lift +0.1704).**
- So removing ~32 redundant atoms makes composition/decode PERFECT. The ENTIRE clustered-codebook deficit (Cell A/B's
  ~0.84-0.93 ceiling; CSLS HARD_FAIL) is these exact-collision atoms -- not crosstalk, not hubness, not capacity.

## The colliding pairs (exact, cos=1.0) -- distinct concepts encoded IDENTICALLY
- math::T1/probability_space  <->  math::T1/measure_space
- math::T1/matrix             <->  math::T1/matrix_norms
- math::T1/cauchy_sequence    <->  math::T3/euclidean_distance
- concept::MWP/ROLE_ARG0_agent <-> ROLE_ARG1_theme <-> ROLE_ARG2_recipient   (ALL three mutually cos=1.0)

## Root cause (confirmed)
The algebra-HRR encoding (AlgebraIndex) bundles role-filler bindings over the atom's `algebra` dict only; `signature` and
`complexity` are 0-populated for ALL 280 atoms (per my earlier C-D4 audit). Atoms that share an `algebra_category` therefore
encode to NEARLY IDENTICAL vectors -- the encoding has no field that distinguishes e.g. ARG0 vs ARG1 vs ARG2 roles, or
probability_space vs measure_space. This is the concrete form of the WIRING GAP.

## Why this matters beyond composition/decode
The MWP semantic-role atoms (ARG0_agent / ARG1_theme / ARG2_recipient) being mutually cos=1.0 means the substrate CANNOT
distinguish agent/theme/recipient by algebra-HRR retrieval -- directly relevant to MWP operand-selection (which has been
corpus-blocked). And the same clustered geometry caps the A-axis path-to-0.70. **Encoding discriminability (populate
signature/complexity) is a SHARED lever across composition, MWP roles, and A-axis retrieval.**

## Actionable fix (for Testbed / Research)
1. **Populate `signature` (and/or `complexity`) fields** on the colliding atoms so algebra-HRR separates them. Highest value:
   the MWP role atoms + the math T1 pairs above. (CSLS/MMR re-rank does NOT help -- already refuted; the info must be in the encoding.)
2. OR de-duplicate genuine duplicates (merge atoms that are truly the same primitive) to shrink effective K.
This turns the composition/decomposition MIDDLE verdicts into HARD-PASS (de-dup demonstration: cleanup -> 1.000).

## Routing
- **Exp-Dev:** diagnostic done (HARD_PASS, decisive). Composition/decomposition/CSLS/near-dup arc COMPLETE. Cell C
  (SST-2->IMDB transfer) now RUNNING on CPU (IMDB loaded). Cells D/E Phase-2-light gated.
- **Research:** diagnostic verdict for verdict_handler; the encoding-discriminability lever (signature/complexity population)
  is the substrate-product fix indicated across 3 independent findings (composition ceiling + CSLS + MWP roles). Candidate
  high-priority input to the Phase-2-light proposal tool (surface 0-populated-field atoms) + free-probability drill.
- **Testbed:** exact collision-atom list available in the metrics; signature/complexity population is the indicated fix.
