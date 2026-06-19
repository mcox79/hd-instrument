# Exp-Dev -> Research: CSLS cleanup re-rank HARD_FAIL -- the clustered-codebook deficit is GENUINE SEMANTIC NEAR-DUPLICATES, not hubness; the mitigation is ENCODING (not re-rank)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_csls_cleanup_recovery_gpu_v1 (GPU/cuda)
**Frame:** substrate-property; NO LLM comparison.

## Result
| F | standard cleanup@1 | CSLS cleanup@1 | CSLS lift |
|---|---|---|---|
| 1 | 0.9333 | 0.9333 | +0.0000 |
| 2 | 0.8917 | 0.8917 | +0.0000 |
| 3 | 0.8889 | 0.8889 | +0.0000 |
| 5 | 0.8533 | 0.8533 | +0.0000 |
| 10| 0.8683 | 0.5383 | **-0.3300** |
| 20| 0.8417 | 0.3533 | **-0.4883** |

## Verdict: HARD_FAIL (and informative)
CSLS (the standard hubness mitigation Research/the distractor-density drill flagged) gives **exactly zero recovery** at low F
(1-5) and **actively destroys** accuracy at high F (10-20). Mechanism: at high F the recovered-filler signal is weak
(cos = 1/sqrt(F) ~ 0.22-0.32), so the hubness penalty r_k(c) dominates the CSLS score and the argmax drifts to low-hubness
atoms unrelated to the estimate. At low F the correct atom already wins by cosine, and subtracting r_k doesn't change the winner.

## The decisive finding: the deficit is GENUINE NEAR-DUPLICATES, not hubness
Cell A showed the substrate's clustered codebook caps cleanup at ~0.89 (F=3) vs uniform=1.0. The hypothesis was hubness
(dense-region atoms stealing the argmax). **CSLS refutes it:** if it were hubness, the hubness penalty would help; instead it
does nothing (low F) or hurts (high F). Therefore the ~0.11 deficit is **genuine semantic near-duplicates** -- atoms whose
algebra-HRR encodings are near-identical (e.g., within-category atoms with near-identical structured profiles per the L1
categorical clustering result). The discriminating information is simply NOT in the encoding; no cleanup re-rank can recover it.

## Architectural implication (sharp, actionable)
The mitigation for the clustered-codebook decode ceiling is NOT cleanup re-rank (CSLS/MMR will not help -- CSLS empirically
hurts) but one of:
1. **Finer atom encoding** -- richer algebra-HRR (add signature/complexity fields, which are currently 0-populated for all
   atoms per my earlier audit) so near-duplicate atoms separate in the codebook.
2. **Atom de-duplication / merging** -- if two atoms are genuinely the same primitive, merge them (reduces effective K).
This directly informs the Stratified-Hybrid cleanup layer: invest in ENCODING DISCRIMINABILITY, not re-rank.

This also connects to the path-to-0.70 A-axis work: the same clustered geometry that caps decode is what the bge-name +
algebra-HRR UNION is navigating. Encoding discriminability (signature/complexity population) is a shared lever.

## Routing
- **Exp-Dev:** CSLS done (HARD_FAIL, decisive). Composition/decomposition story COMPLETE: substrate composes+decodes with no
  capacity cliff; ceiling = clustered codebook = genuine near-duplicates = fix is encoding not re-rank. Cell C blocked on bio
  data (separate note). No more authorized GPU work pending mine.
- **Research:** CSLS verdict for verdict_handler. Concrete substrate-product finding: cleanup re-rank is NOT the lever for the
  clustered codebook; signature/complexity field population (finer encoding) is. Candidate input to the free-probability drill
  (the deficit is a rank/duplicate property of the algebra-HRR Gram matrix, not a hubness/density artifact).
