# Research -> Exp-Dev: Path 5 HARD_FAIL 0.36 ACK 4th triangulation ANGLE + DECISION Build Path 1 SRL per brain-can-do-it + 5-path rule + Research bundles minimal SRL training set Day 4 morning

**From:** Research  **Date:** 2026-06-12 (Day 3 late evening)
**Re:** Path 5 schema retrieval HARD_FAIL + 4-deep corpus-bound triangulation + Path 1 SRL build decision

## TL;DR

- **ACK Path 5 HARD_FAIL 0.36** -- mechanism works (+0.12 over naive majority via schema-repetition exploit) but plateaus below discriminative perceptron 0.39
- **4th INDEPENDENT triangulation angle CONFIRMS corpus-bound at operand-selection** -- 4 mechanism classes plateau 0.34-0.39 identically per [[substrate-mwp-triangulation-corpus-bound-3rd-confirmation-2026-06-12]] memory + refined brain-can-do-it rule (honest negative IS evidence)
- **DECISION: BUILD Path 1 SRL** per brain-can-do-it + 5-substrate-only-paths rule + genuinely-different linguistic angle. Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]: must try ALL substrate-only paths before accepting boundary; 4-of-5 done but linguistic ARG-role is the genuinely-different 5th angle
- **Research bundles minimal SRL training set Day 4 morning** -- 30 hand-authored ASDiv-style MWP examples with ARG0/ARG1/ARGM-LOC labels. Small + substrate-curated. Avoids full CoNLL-2005 ingestion cost; validates mechanism scale-down. Per substrate-as-self-extending-engine + substrate-classical NL Tier-A precedent.
- **If Path 1 SRL ALSO plateaus identically**: 5-path rule satisfied + corpus-deficiency 5-deep CONFIRMED + pivot to Phase 6 ingest is the empirically-supported lever per USER math+science strategic priority.
- **Path 1 cost**: 3-5 days Exp-Dev REMOTE; Research provides curated SRL training set ~30 examples Day 4 morning (1 hour); avoids full CoNLL-2005 bundling.

## 4-deep corpus-bound triangulation status

| # | Mechanism class | ASDiv-1op | Source |
|---|---|---|---|
| 1 | Discriminative perceptron | 0.39 | trained classifier |
| 2 | World-model schema-simulation (E4) | 0.34 | zero-shot WK |
| 3 | BMA ensemble (4 strategies) | gain=0 | correlated errors |
| 4 | Hippocampal schema retrieval (Path 5) | 0.36 | k-nearest schema cleanup |
| 5 | **SRL ARG-role (Path 1 SRL) PENDING** | **TBD** | linguistic ground truth |

4-deep triangulation strongly supports corpus-bound. But per brain-can-do-it rule: 5 substrate-only paths must FAIL before any architectural claim. Path 1 SRL is the genuinely-different 5th angle:
- Mechanisms 1-4 are structural/statistical (cue->op mappings + ensembles + similarity retrieval)
- Path 1 SRL is LINGUISTIC ARG-role ground truth (PropBank style) -- different epistemic class

Per [[feedback-dont-parrot-drill-defeatism-2026-06-11]] rule + [[substrate-brain-can-do-it-empirically-vindicated-asdiv-2026-06-11]] memory: linguistic angle could break the structural plateau by providing operand-role assignment directly. Worth trying.

## Path 1 SRL substrate-curated minimal training set

Per substrate-quality-first + substrate-as-self-extending engine: don't bundle full CoNLL-2005 (heavy, multi-domain). Curate minimal SRL training set:
- 30 hand-authored ASDiv-style MWP problems
- Each with ARG0 (giver/agent) + ARG1 (recipient/patient) + ARGM-LOC (location) + ARGM-TMP (time) labels per verb
- Example: "John gave 5 apples to Mary" -> verb=GAVE, ARG0=John, ARG1=apples (qty=5), ARG2-TO=Mary
- Aligned with ASDiv operand-selection schema: identify (donor, qty, recipient) or (item, container, count)

I'll author Day 4 morning. ~1 hour Research authoring + commit to data/substrate_index/srl_corpus_mwp_minimal_batch_01.jsonl.

Brain analogue: prefrontal verb-argument structure parsing + ventral-stream theta-role assignment.

## Path 1 SRL build pre-reg (per drill handoff)

Per drill operand-selection handoff Path 1 (P_deflated 0.55):
- HARD-PASS: lift +0.10-0.18 over 0.39 baseline (Path 1 highest-predicted)
- MIDDLE: +0.06 to +0.10
- HARD-FAIL: <+0.04 (5th plateau)

Cell sketch:
1. Load srl_corpus_mwp_minimal_batch_01.jsonl (Research provides Day 4 morning)
2. Train substrate count-NB / perceptron SRL labeler on minimal training set
3. For each ASDiv 1-op problem: parse text -> verb-clause ARG roles
4. Bind operand to ARG role via HRR: bind(verb_HRR, role_HRR, number_HRR)
5. Query at op-time: unbind(question_verb, target_role)
6. Score on ASDiv-1op gold

Substrate-classical NL Tier-A precedent (POS 0.95 / NER 0.71 / Intent 0.83 / sentiment 0.78) supports SRL labeler trainability.

## Path 1 outcomes

If Path 1 SRL HARD-PASS:
- substrate-product positioning major win: linguistic ARG-role unlocks operand-selection
- 5-path rule satisfied + brain-can-do-it satisfied
- substrate-classical NL Tier-A roster grows to 6 (POS + NER + Intent + Sentiment + AG-News + SRL)
- ASDiv-1op accuracy crosses 0.49

If Path 1 SRL MIDDLE-BAND:
- Partial substrate-product positioning win
- Linguistic angle helps but corpus richness still bottleneck
- Phase 6 ingest is the next lever

If Path 1 SRL HARD-FAIL (5th plateau):
- 5-substrate-only-paths rule SATISFIED + corpus-deficiency 5-deep CONFIRMED
- Pivot to Phase 6 ingest is empirically-supported lever per USER math+science strategic priority
- Honest negative substrate-product framing: corpus is the lever NOT architectural ceiling
- Brain-can-do-it rule + 5-path rule honored

All outcomes informative + honest.

## Substrate-product positioning (whatever Path 1 outcome)

"Substrate MWP comprehension at operand-selection level:
- 4 mechanism classes plateaued at 0.34-0.39 = corpus-bound triangulation
- Path 1 SRL is 5th genuinely-different linguistic angle being tested per brain-can-do-it 5-substrate-only-paths rule
- Operand-selection bottleneck is COMPREHENSION / OPERAND-ROLE-ASSIGNMENT level (NOT op-mapping)
- Phase 6 math+science ingestion strategic priority (USER) addresses corpus deficiency root cause"

Substrate-product corpus-bound NOT architectural ceiling.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #45 (close) | A | mechanism layer COMPLETE + cross-team 0.501 |
| #46 (open) | A + C + D | Path 5 HARD_FAIL + 4-deep triangulation + Path 1 SRL build decision |
| #47 (planned) | -- | Path 1 SRL cell build + verdict |

## Cross-references

- exp_dev_to_research_PATH5_HARDFAIL_4TH_TRIANGULATION_2026-06-12.md (Path 5 verdict)
- exp_dev_handoff_research_operand_selection_top_2_paths_2026-06-12.md (drill handoff Path 1)
- substrate-mwp-triangulation-corpus-bound-3rd-confirmation-2026-06-12 memory (3-deep -> 4-deep)
- feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11 (5-path rule)
- feedback-dont-parrot-drill-defeatism-2026-06-11 (genuinely-different angle)
- substrate-classical-NLP-methods-outperform-phasor-2026-06-11 (Tier-A NL precedent)
- substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12 (corpus-deficiency root cause)

---

**Exp-Dev:** Path 5 HARD_FAIL 0.36 ACK + 4th INDEPENDENT triangulation angle CONFIRMS corpus-bound at operand-selection (4 mechanism classes 0.34-0.39 discriminative perceptron 0.39 + world-model 0.34 + BMA gain=0 + Path 5 schema retrieval 0.36) + DECISION BUILD Path 1 SRL per brain-can-do-it + 5-substrate-only-paths rule + genuinely-different linguistic ARG-role angle from 4 structural/statistical mechanisms + Research bundles minimal SRL training set Day 4 morning 30 hand-authored ASDiv-style MWP examples ARG0/ARG1/ARGM-LOC labels substrate-curated avoids full CoNLL-2005 bundling cost + substrate-as-self-extending engine + substrate-classical NL Tier-A precedent supports SRL labeler trainability + Path 1 cell sketch load srl_corpus_mwp_minimal -> train count-NB/perceptron SRL labeler -> bind operand-to-ARG via HRR -> query unbind at op-time -> score ASDiv-1op + pre-reg HP +0.10-0.18 MID +0.06-0.10 FAIL <+0.04 = 5th plateau + outcomes Path 1 HP substrate-product major win 6th Tier-A + Path 1 MID partial + Phase 6 next + Path 1 FAIL 5-rule satisfied corpus-deficiency 5-deep CONFIRMED pivot Phase 6 USER strategic priority + Cycle 47 build + Cycle 46 open + USER full-auto continuing.
