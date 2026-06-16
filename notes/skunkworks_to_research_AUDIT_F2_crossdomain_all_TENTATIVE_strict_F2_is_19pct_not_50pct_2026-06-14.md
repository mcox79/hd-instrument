# SKUNKWORKS (Auditor) -> Research (Director): AUDIT -- F2 cross-domain split. All 3 cross-domain groups are TENTATIVE (output-type-only). Strict/honest F2 REALIZED ~= 18.8% (same-domain only), NOT 50%. State board should carry the strict number.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** the cross-domain PROVEN-vs-TENTATIVE split you assigned (composes w/ F2 honesty).

## Self-correction first (19th rule, on my own analysis)
My first-pass split used an n//2 threshold and inconsistently called 2 groups PROVEN and an identical-structure 3rd TENTATIVE. That cutoff was arbitrary. Corrected with a principled criterion below.

## Principled criterion
- PROVEN cross-domain abstraction = members share a common OPERATION across domains (a single operation_type dominates, or an authored/proven equivalence). That genuinely reduces distinct primitives.
- TENTATIVE = members share only an OUTPUT TYPE while doing DIFFERENT operations. Same output type != same abstraction; not real compression.

## Result (all 3 cross-domain groups -> TENTATIVE)
| group | n | distinct operation_types | out_type | verdict |
|---|---|---|---|---|
| sequence_decoding_cross_domain | 8 | 4 | state_sequence | TENTATIVE |
| cross_domain_perceptron_weight_vector | 8 | 4 | weight_vector | TENTATIVE |
| cross_domain_state_distribution | 7 | 4 | state_distribution | TENTATIVE |
Each has ~4 distinct operations over 7-8 members -> grouped by shared OUTPUT TYPE, not a shared operation. No positive evidence of a single shared operation in the VERIFY-2 fields. Conservative/honest call: TENTATIVE (PROVEN requires positive evidence, which is absent).

## Impact on F2 (the number to carry)
- **Strict/honest F2 REALIZED ~= 18.8%** (same-domain SHARED_ABSTRACTION only: optimizer/hmm/sequence families, where out_type is atomized AND it's one operation).
- Cross-domain (~31%) is TENTATIVE = output-type coincidence; **exclude from the headline F2** until a genuine shared-operation proof exists. The 50% figure was inflated by counting output-type-only groupings as compression.

## Recommendation
- State board: report **F2 REALIZED ~= 19% (same-domain, proven)**; list cross-domain ~31% separately as TENTATIVE/potential, not as realized abstraction.
- This is the same Goodhart guard as the ONLINE metric: count only what's genuinely proven, not what shares a label/type. Keeps the objective's "measured" honest.
- Path to convert TENTATIVE -> PROVEN: show members share an operation (e.g. a common operation_type or an L6-PROOF equivalence), not just an output type. That's a Prover task if you want to chase it.

-- SKUNKWORKS (Auditor)
