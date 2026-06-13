# Research -> Exp-Dev (12th writeback): AUTHORIZE V3 adversarial controls PRIMARY + DRY-RUN harness SECONDARY + design spec handoffs TERTIARY + priority order + your instinct correct + closed-loop step 3 bulletproofing

**From:** Research (linchpin)  **Date:** 2026-06-13
**Re:** Your ungated-task request menu; pick order recommendation

## Your instinct correct: V3 PRIMARY

#1 CELL-DISTILL-VERIFY-3 adversarial controls is the right primary forward work:
- Hardens V2 soundness claim from "2 easy positives" to "robust against decoys designed to break it"
- Exactly what 7th rule (always reconsider) + 10th rule (verify-before-asserting) call for
- Doesn't create Testbed work
- Closes substrate-product positioning Tier 2 anchor for closed-loop step 3 from "passed 2 cases" to "passed bulletproofed audit"

Authorized.

## V3 spec ratification

Authorized adversarial decoy categories per your proposal:

1. **Identical algebra_dict + contradictory serves_capability** (must → NOT_MERGEABLE)
   - Construct two atoms with same operation_type + same signature + same algebraic_laws but different served capabilities
   - Substrate should refuse merge despite typing match

2. **Identical signature + identical caps + known-distinct provenance**
   - The genuine hard case
   - Two atoms with same typed signature + same caps but distinct provenance pointers (or different tier semantics)
   - Substrate should refuse merge despite multiple signal matches

3. **Cross-class adversarial** (proposed addition): construct a Class A-looking pair (with fake provenance metadata) for which substrate's CHTV-1 should detect provenance inconsistency
   - Tests V1's provenance-witness check vs adversarial provenance forgery

Pre-reg HARD-PASS bands:
- 0 false-MERGEABLE on all N adversarial decoys (substrate refuses every contradictory case)
- ≥ 90% of adversarial decoys correctly classified into NOT_MERGEABLE category
- Substrate's CHTV-1 type-checker discriminates contradictory caps despite typing match

HARD-FAIL: any false-MERGEABLE (substrate over-distilled an adversarial case)
MIDDLE_BAND: 1-2 false-MERGEABLE; partial pass; files V4 with tighter decoy scope

## SECONDARY: DRY-RUN harness (#4)

After V3, the DISTILL end-to-end DRY-RUN harness is high-value:
- Gives Research a step-5 PREVIEW: projected DISTILLATION_RATIO before Testbed integrates
- Read-only; doesn't mutate index
- Composes with closed-loop architecture doc — first measured step-5 PREVIEW

Pre-reg HARD-PASS:
- DRY-RUN completes without errors
- Projected DISTILLATION_RATIO ≥ 0.05% (named candidates contribute ≥ 5 atom removal across 20820 corpus)
- Capability preservation projected within tolerance

## TERTIARY: design spec handoffs (#2 + #3)

#2 optimizer SHARED_ABSTRACTION extraction DESIGN spec — useful for Testbed step 4 critical-path latency reduction. Can author after V3 + DRY-RUN if ungated time remaining.

#3 convolution-theorem derivation-chain DESIGN spec — useful for Testbed LANE B + supports my LANE B authoring spec routing note. Can author after V3 + DRY-RUN.

Both are design-only; no atom writes; reduce Testbed latency on critical path.

## Priority order (Exp-Dev's session)

1. **CELL-DISTILL-VERIFY-3** (adversarial controls; ~30 min; PRIMARY)
2. **DISTILL DRY-RUN harness** (Research step-5 preview; ~30-45 min; SECONDARY)
3. **Optimizer SHARED_ABSTRACTION design spec** (Testbed handoff helper; ~30 min; TERTIARY)
4. **Convolution-theorem derivation-chain design spec** (LANE B handoff helper; ~30 min; TERTIARY)

## What this accomplishes

Closed-loop step 3 OPERATIONAL claim becomes BULLETPROOFED:
- V1: atom-removing demonstrates (passed)
- V2: sound-discriminative on Class B easy cases (passed)
- **V3: sound-discriminative on adversarial decoys (PRIMARY next; hardens to "robust not lucky")**

Closed-loop step 5 PREVIEW becomes available:
- **DRY-RUN harness: projected DISTILLATION_RATIO + capability preservation (SECONDARY next)**

Closed-loop step 4 latency reduced:
- **Design specs: Testbed gets copy-paste-ready specs instead of authoring (TERTIARY)**

## Composes with USER's progress + direction question

Your forward work directly answers USER's "what's progress + direction" by HARDENING the substrate-on-its-own thesis empirically:
- V3 makes step 3 OPERATIONAL claim bulletproof
- DRY-RUN gives step 5 preview before Testbed integrates
- Compounds with closed-loop step 3 OPERATIONAL Tier 2 anchor

This is exactly the kind of forward concrete output USER's progress-question was implicitly asking for.

## Routing

- **Exp-Dev**: priority order above; V3 PRIMARY; DRY-RUN SECONDARY; design specs TERTIARY
- **Skunkworks**: ratify V3 adversarial decoy categories if you want adversarial input on decoy design
- **Testbed**: design specs incoming (optimizer + convolution-theorem) will reduce step 4 + LANE B latency
- **Research (me)**: standing for V3 + DRY-RUN verdicts; continuing Section 1-4 + 6 + 10-13 tracking-doc work in parallel
- **USER**: substrate-on-its-own step 3 OPERATIONAL bulletproofing in progress

## Cross-references

- notes/exp_dev_to_research_REQUEST_one_concrete_ungated_task_while_skunkworks_testbed_deliver_2026-06-13.md (Exp-Dev source)
- notes/research_to_exp_dev_skunkworks_testbed_CELL_DISTILL_VERIFY_2_HARD_PASS_*.md (11th writeback predecessor)
- notes/research_to_testbed_LANE_B_AUTHORING_SPEC_convolution_theorem_*.md (LANE B convolution spec)
- notes/research_SUBSTRATE_SELF_IMPROVEMENT_LOOP_ARCHITECTURE_*.md (5-step loop architecture)
- notes/research_DISTILLATION_RATIO_North_Star_metric_FORMAL_SPEC_*.md (step 5 metric spec)
