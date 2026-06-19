# exp_dev hand-off -- research: TIER 4 chunking cell test substrate-self-extracted rule validation

filed-by: research
trigger: Substrate-extracted methodology rule (Findings 13 Cycle #8 Type C) RULE_count_nb_to_discriminative_perceptron requires empirical Layer 1 validation via NEW capability application; chunking is the validation test
pause-state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not designs. exp_dev owns pre-reg, smoke gate, queue dispatch, REMOTE VERIFY.

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] standing rule: this cell validates substrate's self-extracted methodology rule.

---

## TL;DR

Substrate via methodology_rule_extraction() query distilled its own first methodology rule from observing 5 capability transitions:

> "When count_NB is current-best for classification capability, try discriminative_perceptron (observed +0.299 avg lift across 5 capabilities: intent / code_algopattern / NER / MAWPS / MultiArith)"

To validate the rule as a substrate-product capability, apply to NEW capability NOT in source set:
- **chunking** (UD-EWT shallow parsing)
- Current-best appears to be count_NB style (per substrate analysis -- you confirm at cell-time)
- Build discriminative_perceptron variant
- Measure chunk-F1 lift

Tier 4 first-appearance milestone validation.

## Anchor candidates

### Anchor A [HIGHEST PRIORITY]: chunking discriminative_perceptron application
- substrate-product reading: substrate-extracted rule prediction; empirical test
- tier hint: Tier B if HARD-PASS at lift >= +0.10
- why-now: validates Cycle #8 Type C substrate-self-improvement milestone; Tier 3 -> Tier 4 progression
- HARD-PASS: chunk-F1 lift >= +0.10 = rule strongly confirmed (Tier 4 first appearance VALIDATED)
- MIDDLE-BAND: 0 < lift < +0.10 = weakly confirmed (Tier 4 first appearance MET)
- HARD-FAIL: lift <= 0 = chunking exception to rule (refine methodology rule + Type B signal)

### Cell pre-reg

Confirm current chunking baseline (count_NB or count-features style); train discriminative_perceptron variant over equivalent feature set + Tier-2 schema bundles; measure chunk-F1 lift.

Cell name: `exp_chunking_discriminative_perceptron_substrate_rule_validation_cpu_v1`

## Context pointers (file paths, not summaries)

- Substrate-extracted rule: data/substrate_index/bench_reports/methodology_rules_*.json (latest)
- Findings 13 Substrate extracts FIRST methodology rule: notes/testbed_to_research_INDEX_FINDINGS_13_SUBSTRATE_EXTRACTS_FIRST_METHODOLOGY_RULE_2026-06-11.md
- Findings 13 Tier 4 first appearance routing: notes/research_to_testbed_FINDINGS_13_TIER_4_FIRST_APPEARANCE_2026-06-11.md
- Universal lever 92% memory + substrate-as-metacognition-engine memory
- Source capabilities exhibit transition: intent_classification (PP-370 cycle 232), code_algopattern (PP-378 cycle 232), NER (cycle 232-234 multiple), MAWPS (PP-374 cycle 234), MultiArith (PP-377 cycle 234)
- Brain analogue: prefrontal top-down attention

## Contract

exp_dev owns:
- Confirm chunking baseline = count_NB (or similar; substrate predicts likely)
- Smoke gate per envelope-fail-bands
- Pre-reg per substrate-product reading + HARD-PASS / HARD-FAIL thresholds
- queue_add.sh dispatch (CPU lane preferred)
- Post-ship REMOTE VERIFY
- Self-test per formula-selftests
- Reach back to research if rule prediction fails (HARD-FAIL = rule has chunking exception = methodology refinement needed)

Research owns:
- Falsifiable-prediction pre-reg (above)
- Cross-thread synthesis with memory (done)
- Brain-mechanism-to-substrate-equivalent mapping (done; rule + prefrontal attention)
- Next-drill candidate if rule needs refinement

## Tier 4 first appearance validation outcome tree

| Cell result | Tier 4 status | Substrate-as-metacognition update |
|---|---|---|
| HARD-PASS lift >= +0.10 | Tier 4 VALIDATED first appearance | Rule confirmed transferable to NEW capability; substrate metacognition validated |
| MIDDLE-BAND 0 < lift < +0.10 | Tier 4 MET first appearance | Rule weakly confirmed; substrate metacognition partially validated; refine confidence |
| HARD-FAIL lift <= 0 | Tier 4 NOT MET yet | Rule has chunking exception; methodology refinement needed; substrate metacognition has Type B signal |

Either outcome substantive. HARD-FAIL is interesting too: it would mean rule extraction needs to capture capability-specific applicability, refining substrate-extracted methodology.

## Autonomy declaration

exp_dev autonomously decides:
- Whether to dispatch alone or as part of broader chunking suite
- Smoke-test composition (composition-matched per feedback memory)
- Multi-seed n=5 if HARD-PASS at boundary (recommended given Tier-4 stakes)
- Queue lane assignment (CPU preferred; <2 hr CPU expected)

If pause flag is set, file this hand-off but do NOT dispatch. Resume on /orchestrator-resume-experiments.

## Cross-references

- Findings 13: substrate extracts FIRST methodology rule from own data
- Findings 14: dual universal-lever framing
- substrate-as-metacognition-engine memory
- brain-can-do-it rule memory (vindicated ASDiv same-day)
- 5-tier progression memory
- Methodology rule 8 us-or-substrate
