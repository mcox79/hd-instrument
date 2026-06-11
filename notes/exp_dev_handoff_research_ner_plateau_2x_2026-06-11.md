# exp_dev hand-off -- research: NER 3-datapoint plateau (~0.58 F1) substrate paths 2x

filed-by: research
trigger: 2x DEEP drill on NER plateau (cycles 235-236 LVH-287/288/289 all clustered F1 0.575-0.58)
research-note: d:/AI/hd-instrument/notes/research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md
pause-state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not designs. exp_dev owns pre-reg, smoke gate, queue dispatch, REMOTE VERIFY.

---

## Anchor candidates (rank-ordered by P_deflated x cost-efficiency)

### Anchor A [HIGHEST PRIORITY]: BIO-Viterbi on existing emission scores
- substrate-product reading: cheap decisive test; discriminates 3 hypotheses (structured-decoder dominant / necessary-not-sufficient / emission-bottleneck) in one cell
- tier hint: Tier B if HARD-PASS at F1 >= 0.63; Tier C if MIDDLE-BAND
- why-now: zero new training, reuses cycle 235 LVH-287 trained model emission scores, <1 hour CPU, decisive for the next 4 anchor decisions
- pointer: research-note section (d) Path 1 + section (e) pre-reg
- HARD-PASS: F1 >= 0.63 / HARD-FAIL: F1 < 0.59

### Anchor B: Cascade substrate POS (PP-379 at 0.9499) as upstream feature into NER discriminative
- substrate-product reading: simplest cascade; substrate POS exists and is high-quality
- tier hint: Tier C (incremental, modest expected lift)
- why-now: cycle 235 ranked it RESCUE-3 but skipped to gazetteer; trivially cheap (<30 min CPU)
- pointer: research-note section (d) Path 3
- run together with Anchor A if Anchor A PASSES; gate behind Anchor A result

### Anchor C: Substrate Brown-cluster-equivalent via Layer-3 archaeology + co-occurrence binding
- substrate-product reading: substrate-novel angle for distributional word clusters as discrete cluster-ID features
- tier hint: Tier B (substrate-novel mechanism, published Brown-cluster precedent on classical NER)
- why-now: aligns with substrate-classical-NLP-outperforms-phasor memory pattern; reusable for chunking + shallow parse later
- pointer: research-note section (d) Path 2
- gate behind Anchor A result (if A FAILs at <0.59, run C BEFORE B)

### Anchor D: Class-balanced bipolar emission with rare-tag upweighting
- substrate-product reading: trivial perceptron extension; addresses fine-grained 36-tag class imbalance
- tier hint: Tier C (incremental, low-risk)
- why-now: <1 hour CPU; stacks with all other anchors
- pointer: research-note section (d) Path 5

### Anchor E [HIGHEST VARIANCE -- DEFER]: Resonator phrase-decomposition for multi-token entities
- substrate-product reading: substrate-novel span decoder; reusable for chunking + shallow parse
- tier hint: Tier B if HARD-PASS at +0.10 lift; Tier D if HARD-FAIL
- why-now: HOLD until Anchor A result. If A FAILS (<0.59), promote E as the alternative emission-bottleneck path
- pointer: research-note section (d) Path 4

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md (this drill, authoritative)
- d:/AI/hd-instrument/notes/substrate_only_NL_pos_tagger_validated_2026-06-11.md (POS 0.9064 mechanism, basis for Anchor B cascade)
- d:/AI/hd-instrument/notes/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (validated substrate-classical NL primitive pattern)
- d:/AI/hd-instrument/notes/drill_pattern_temporal_contextual_not_structural_2026-06-11.md (temporal+contextual works; fixed-architecture caps Anchor E lower)
- d:/AI/hd-instrument/notes/feedback_dont_parrot_drill_defeatism_2026-06-11.md (rule applied: 5 untested paths inventoried before any ceiling claim)
- prior LVH cells: LVH-287 (discriminative seed 1 F1 0.5817), LVH-288 (gazetteer F1 0.5747), LVH-289 (discriminative seed 2 F1 0.5752)

---

## Contract

exp_dev owns:
- Smoke gate per envelope-fail-bands
- Pre-reg per substrate-product reading + HARD-PASS / HARD-FAIL thresholds in research-note section (e)
- queue_add.sh dispatch (CPU lane preferred; all 5 anchors are CPU-fit)
- Post-ship REMOTE VERIFY (file presence + queue index)
- Self-test per formula-selftests
- Reach back to research if Anchor A delivers a result that contradicts pre-reg or surfaces new substrate-novel angle

Research owns:
- Falsifiable-prediction pre-reg (done; section e)
- Cross-thread synthesis with memory (done; section f)
- P_deflated estimates with calibration penalty (done; section a)
- Next-drill candidate fields (done; section i)

---

## Autonomy declaration

Anchor A is the cheap decisive test. exp_dev autonomously decides:
- Whether to dispatch A alone first, OR A+B+D as a stack (Anchor A result still decisive within the stack via ablation)
- Smoke-test composition (composition-matched per feedback memory)
- Whether to run multi-seed (recommended given 3-datapoint pattern -- if A passes, multi-seed at the boundary)
- Queue lane assignment (CPU preferred; home GPU not needed for any of A-D-E in pure-substrate setup)

If pause flag is set, file this hand-off but do NOT dispatch. Resume on /orchestrator-resume-experiments.
