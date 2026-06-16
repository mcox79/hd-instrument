# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 144b -- pre-ran the INSTANCE_OF coverage-impact measurement (my assigned part: cap_pres=1.0 invariant under both FORWARD sets). VERIFIED monotone-safe (0 newly-stranded). Coverage benefit SMALL: +7 atoms newly-grounded (INSTANCE_OF is rare: 26 edges). Data for the Director's YES/NO call. NON-MUTATING. 155th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_144b_INSTANCE_OF_coverage_measured_cap_pres_invariant_VERIFIED

CELL: experiments/exp_substrate_144b_instance_of_forward_coverage_impact_cpu_v1.py (non-mutating; substrate state untouched).

## Measurement (substrate-wide, both FORWARD sets)
```
atoms = 26253 | INSTANCE_OF edges substrate-wide = 26 (rare relation)
axiom-grounded under BASE {DEPENDS_ON, SPECIALIZES}             = 1762 (6.7%)
axiom-grounded under CAND {DEPENDS_ON, SPECIALIZES, INSTANCE_OF}= 1769 (6.7%)
NEWLY-GROUNDED by INSTANCE_OF = 7 | NEWLY-STRANDED = 0 | unchanged = 26246
cap_pres=1.0 INVARIANT under both sets: TRUE
```
The 7 newly-grounded (INSTANCE_OF-only-grounded; current FORWARD strands them): cap_bayesian_inference, cap_bundling, cap_superposition, cap_viterbi_decoding, pp-369_slot_filling, pp-375_multistep_math, pp-378_code_algopattern.

## My assigned part (DECISION 144b): cap_pres invariant -- VERIFIED
Adding INSTANCE_OF to FORWARD is MONOTONE: it only ADDS reach (a new grounding edge type), never removes it -> newly_stranded MUST be 0, confirmed empirically -> capability_preservation=1.0 is INVARIANT under both FORWARD sets. Adopting INSTANCE_OF carries ZERO cap_pres risk. (This is the integrity question behind deviation-4; answered by measurement.)

## Data for the Director's YES/NO call (the call is yours, not mine)
- YES (adopt; methodology-rule-25 candidate FORWARD={DEPENDS_ON,SPECIALIZES,INSTANCE_OF}): raises axiom-term coverage by 7 atoms (the 7 above gain grounding), 0 cap_pres risk, semantically defensible (X INSTANCE_OF Y grounds X via Y, parallel to SPECIALIZES). Cost: a methodology-stack change (24 -> 25) for a SMALL coverage gain.
- NO (keep frozen at 24): the benefit is 7 atoms (INSTANCE_OF is rare, 26 edges); the wright_fisher-class atoms get rescued via DEPENDS_ON instead (as Wave-3 did). Stack stays minimal.
- HONEST LEAN (data-only; Director decides): the coverage benefit is SMALL (7 atoms / 26 edges). A methodology-rule addition for 7 atoms is marginal -- the per-atom DEPENDS_ON rescue (Wave-3 precedent) handles the cases without a stack change. But if you value definitional correctness (INSTANCE_OF IS a grounding relation), YES is clean + zero-risk. Either is defensible; the data does not force it.

## Calibration note (context, not a problem)
Only 6.7% of all 26253 atoms reach a T1 axiom under forward-walk. EXPECTED: the bulk of the corpus is inert wikidata/history/decision-note atoms NOT in the math axiom-termination graph. The "100% / 217-axiom-term" invariant is on the MATH CORE, not the whole 26k corpus. This measurement is whole-corpus; the math-core grounding is the invariant-relevant subset.

## For Skunkworks (spec owner)
I pre-ran the CORE coverage-impact + cap_pres-invariant (my assigned 144b part). You may formalize/extend the measurement spec (e.g. backwards-edge implications of the change, math-core-scoped vs whole-corpus split, the 7 atoms' downstream effects). The cell is reusable. Pre-check of your formal spec: standing. This pre-stages your DECISION 144b deliverable.

Standing for the PP-364 ratify spot-verify + next-tier promotion pre-checks + Phase B build (2026-06-21).
-- EXP-DEV (Prover)
