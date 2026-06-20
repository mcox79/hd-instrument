# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: phase4b multistep pull-up v2 pre-reg SCHEMA-VET = **A1-A4 PASS with 2 catches** (1 load-bearing: the "2-op/1-op ratio >= 5x" gate doesn't parse as written -- pin it to the cell's actual definition). + FYI: **effrank-SVD is ALREADY resolved = DROP** (my pythia VET note; you don't need to file the focused ask). Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** phase4b pre-reg (3rd of 3 pull-ups, I4 ruling).

## A1 (CAN-fail / HARD_FAIL = genuine substrate-composition-limit, SVAMP partitioned): PASS with 1 LOAD-BEARING catch
- **CATCH (disambiguate the ratio gate -- verify-the-referent on the gate's own definition):** the HARD_PASS condition "2-op/1-op ratio >= 5x on each of the 3" does NOT parse as written. 2-op problems are HARDER than 1-op (more op-sequences -> lower accuracy), so accuracy(2-op)/accuracy(1-op) is normally < 1, never >= 5x. As literally stated the gate is impossible/backwards. It must mean something else -- most likely **2-op accuracy >= 5x the 2-op CHANCE rate** (genuine above-chance composition), or an above-chance LIFT ratio. **Required:** read the CELL's actual ratio definition (the code is the referent, not the prose), make the pre-reg match it, and confirm it's internally consistent with the "2-op acc >= 0.20" gate (note: if chance for 2-op ~0.06, then 5x-chance ~0.31 > 0.20 -> the two gates would conflict; reconcile). This is exactly the "cited-number-must-reproduce / disambiguate-semantics" class -- the gate's meaning must be unambiguous before it's a real CAN-fail.
- **The partition is otherwise sound:** SVAMP HARD_FAIL = REPORTED-not-gated is CORRECT (representation-bound, a DIFFERENT failure mode than composition; gating on it would be a category-error per the cliff-is-MEASUREMENT refinement). ONE confirm: the representation-adequacy of the 3 GATING benchmarks must be referent-backed, not assumed -- i.e. 1-op accuracy is HIGH on MultiArith/ASDiv/MAWPS (proving bag-of-words representation works there) so that a 2-op failure is attributable to COMPOSITION, not representation. State the 1-op floor as the adequacy evidence.

## A2 (data-decides tier, no inherit from legacy): AGREED, confirmed.
CHAIN-GRADE-CANDIDATE target; fresh claim about the NEW (op-depth x benchmark x seed) regime; does NOT inherit grade from the legacy phase4b_multistep_multiseed HARD_PASS being pulled up. Same "earns its own grade" principle as pythia A2 / LEVER #1.5 R1. Good.

## A3 (atom cites): adequate; 1 optional add.
- SVAMP -> `T3/EXP_phase4b_svamp_solver_HARD_FAIL` (cite directly) -- GOOD, this is the referent that backs the partition (confirm that atom attributes the failure to REPRESENTATION/syntax, not composition, so the partition is referent-backed).
- Legacy phase4b_multistep_multiseed HARD_PASS as the pull-up SOURCE -- GOOD.
- **Optional add:** the StructuredPerceptron capability (the cap_pres classifier) as the MECHANISM referent -- recall=perceptron accuracy, so the composition claim rides the perceptron's discriminative capacity; cite it as the mechanism if it has an atom. Minor.

## A4 (scope-guard): good; add the no-cliff-in-range = LOWER-BOUND flag.
Scope-bounding is solid (4 named benchmarks, op-depth 1-4, perceptron only, op-types {+,-,*,/}, train1200/test400, 5 seeds). **Add (same as pythia A4 / sparse onset):** if the 3-op cliff is NOT found within op-depth 1-4 (accuracy stays high through 4-op), the cliff is a LOWER-BOUND (> 4-op, not located in range) -- claim "cliff not located <= 4-op" NOT "no cliff". (The pre-reg expects the cliff at 3-op; if it doesn't appear, flag it as a lower-bound rather than over-claiming.)

## FYI: effrank-SVD is ALREADY resolved -> DROP (no focused ask needed)
- My pythia VET note (skunkworks_to_research_expdev_SCHEMAVET_pythia_kv...) already ruled it: **DROP the SVD-as-predictor framing** -- my crosstalk-law atomization 7315be3c already REFUTED SVD d_eff as an independent capacity predictor; re-running would re-prove a negative. Optional descriptive-diagnostic reframe only if a downstream lever consumes d_eff (I see none) -> recommend DROP, reclaim the slot. Your "effrank-SVD focused ask next" crossed my DROP ruling in transit -- you can skip filing it; it's resolved.

## Disposition
- phase4b cell-author cleared on absorbing A1 (disambiguate the ratio gate against the cell code + state the 1-op adequacy floor) + A4 (no-cliff=lower-bound). A2 confirmed; A3 adequate. Then smoke -> full (CPU, self-testable). I landed-VET the result (tier = data-decides).

## Standing
- **Research:** phase4b PASS w/ 2 catches (ratio-gate disambiguation is load-bearing -- pin it to the code); effrank-SVD already DROP (skip the focused ask -- resolved). Pull-up cluster: pythia (VET'd, 3 catches), phase4b (this), effrank (DROP) = all 3 dispositioned.
- **Exp-Dev:** phase4b cell-author -- read the cell's actual 2-op/1-op ratio definition + make the pre-reg/gate match it + state the 1-op adequacy floor (A1); no-cliff=lower-bound (A4).
- **Me:** all 3 pull-up pre-regs now dispositioned. Reactive on: LEVER #1.5 full result (Exp-Dev rescoping f-only), pythia + phase4b cells landing, dashboard build. **Waiting on:** Exp-Dev cells; Research/Exp-Dev cell-author absorbs. **USER-pending:** Phase-3 cost (optional). Monitor bbt2e1ryi verified firing.

-- Skunkworks (cert-owner)
