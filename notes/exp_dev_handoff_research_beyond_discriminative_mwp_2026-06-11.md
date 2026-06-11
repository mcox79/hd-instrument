# exp_dev hand-off -- research: beyond discriminative MWP mechanism classes

filed-by: research (opus, 2x DEEP drill)
date: 2026-06-11
trigger: research drill 2x DEEP found 5+ mechanism classes BEYOND substrate-discriminative for MWP role-assignment / comprehension plateau at 0.37; substrate-ceiling claim premature per drill-defeatism rule
source-note: d:/AI/hd-instrument/notes/research_drill_beyond_discriminative_mwp_mechanism_classes_2x_2026-06-11.md

## Pause state

honor data/orchestrator_paused.flag. If paused, hold all queue-refill; this hand-off becomes pickup on resume.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor candidates + substrate-product reading + tier hints + pointer files. exp_dev OWNS detailed experiment design, smoke-gates, pre-regs, ship.

## Anchor candidates (rank-ordered)

### Rank 1 -- WORLD-MODEL SIMULATION (substrate Tier-2 schema state-machines)

- anchor pointer: 7 schemas (PURCHASE, DISTRIBUTE, EQUAL_GROUPS, COMPARE, CHANGE, COMBINE, PART-WHOLE) as state-machines; parse MWP entities to slots; SIMULATE transitions; readout answer
- substrate-product reading: AUDITABLE STATE-SIMULATION for MWPs -- "show me the situational model + state-transitions" -- LLM-black-box differentiator
- tier hint: smoke ~30 min CPU; if smoke passes, Tier-A full eval on ASDiv-1op + SVAMP held-out
- why-now: highest P_deflated (0.45) HARD-PASS in drill; strongest mechanistic story (state-delta carries asymmetry MWPs need)
- pre-reg HARD-PASS: held-out >= 0.48 on ASDiv-1op (LIFT >= 0.11 over discriminative 0.37); MIDDLE 0.40-0.48; HARD-FAIL < 0.40
- existing substrate %: ~80% (schemas, FHRR bind, cleanup, temporal-policy); ~150 lines new for transition operators
- substrate primitives wired: FHRR-bind (entity-state pairs); substrate-temporal-policy (state-transitions per PP-225 family); substrate-cleanup (state-readout)

### Rank 2 -- BAYESIAN MODEL-AVERAGING over existing 7 discriminative mechanisms

- anchor pointer: aggregate p(role | mechanism_i) for i in {single-pair selector, program-ranker, cascade+WK, heuristic role-binding, learned role-tagger, FHRR vector binding, discriminative perceptron} via product-of-experts or BMA
- substrate-product reading: CALIBRATED MULTI-MECHANISM UNCERTAINTY (confidence-by-mechanism for each role)
- tier hint: cheapest (~20 min CPU); aggregator script only, 100% existing primitives
- why-now: HARD-FAIL is HIGH-INFORMATION (proves correlated-blindspot in discriminative class); cheapest decisive test
- pre-reg HARD-PASS: held-out >= 0.45; MIDDLE 0.39-0.45; HARD-FAIL < 0.39 (correlated-error case)
- existing substrate %: 100%
- substrate primitives wired: count-NB posterior; 7 existing mechanisms; substrate aggregator

### Rank 3 -- FRAME-SEMANTIC SCHEMA RETRIEVAL (Fillmore frames as substrate frame-vectors)

- anchor pointer: FRAME-VECTOR = bind(FRAME, ROLE, FILLER) tuples; MWP -> cosine-similarity to frame-bank -> winning frame INSTANTIATES role-slots
- substrate-product reading: schema-as-vector with explicit role assignment (auditable)
- tier hint: smoke ~30 min CPU; 95% existing primitives
- why-now: high reuse, mechanistically cleaner than BMA, strong mid-tier P_deflated (0.40)
- pre-reg HARD-PASS: held-out >= 0.45; MIDDLE 0.40-0.45; HARD-FAIL < 0.40
- existing substrate %: ~95%
- substrate primitives wired: FHRR bind/unbind, cosine, cleanup -- all existing

### Rank 4 -- RL-POLICY PORT (Path 8 PP-375 from MultiArith to ASDiv role-assignment)

- anchor pointer: port 2-op composition + answer-consistency weak-label policy from PP-375; reward = reachability-oracle confirmation OR answer-correctness on ASDiv
- substrate-product reading: CROSS-TASK POLICY TRANSFER demo (trained once, generalizes to comprehension-heavy MWPs)
- tier hint: smoke ~1 hr CPU; 70% existing PP-375 architecture
- why-now: prior MultiArith 0.7530 Tier-A; tests transferability into comprehension-bound task
- pre-reg HARD-PASS: held-out >= 0.48; MIDDLE 0.40-0.48; HARD-FAIL < 0.40
- existing substrate %: ~70%
- substrate primitives wired: PP-375 policy architecture; reachability-oracle as reward signal

### Rank 5 -- ANALOGY-RETRIEVAL + STRUCTURE-MAPPING

- anchor pointer: store ~50 solved MWP exemplars with FHRR-bound schema annotation; test-MWP -> top-k via substrate composite-similarity -> slot-isomorphism (Gentner SME-style)
- substrate-product reading: case-based retrieval + structure-transfer for MWPs (explainable analogue)
- tier hint: smoke ~30 min CPU; 85% existing
- why-now: lit precedent +6.7% (Liu et al. NeurIPS 2024); substrate slipnet ceiling REFUTED already
- pre-reg HARD-PASS: held-out >= 0.44; MIDDLE 0.39-0.44; HARD-FAIL < 0.39
- existing substrate %: ~85%
- substrate primitives wired: substrate retrieval, cleanup, Tier-2 schema slot-isomorphism

## Context pointers (file paths -- not summaries)

- d:/AI/hd-instrument/notes/research_drill_beyond_discriminative_mwp_mechanism_classes_2x_2026-06-11.md (this drill -- full mechanistic analysis + 8 classes inventoried + cross-thread synthesis)
- d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-11_north_star.md (current exp_dev state)
- d:/AI/MEMORY.md ref entries: substrate-unified-compositional-generation-engine-2026-06-11; substrate-discriminative-beats-generative-asymmetric-NL-2026-06-11; substrate-LLM-boundary-decomposition-2026-06-10; substrate-static-robust-dynamic-fragile-2026-06-10; methodology-benchmark-must-break-symmetry-2026-06-11; feedback-dont-parrot-drill-defeatism-2026-06-11; feedback-literature-is-not-oracle-2026-06-11; substrate-deep-self-evaluation-program-2026-06-11
- ASDiv-1op + SVAMP dataset locations: per current exp_dev brief (held-out 200-item slice with reachability-oracle annotation)

## Drill-defeatism enforcement (binding)

All 5 ranks MUST fail (HARD-FAIL thresholds) before the "0.37 is substrate ceiling on MWP role-assignment" claim survives. Per [[feedback-dont-parrot-drill-defeatism-2026-06-11]]: I (research) am explicitly NOT accepting the ceiling. 5 paths uninstantiated; instantiate them.

Recommended order: Rank 2 (BMA, cheapest, 100% existing) FIRST as a 20-min decisive screen. If BMA HARD-PASSes, that alone refutes the ceiling. If BMA HARD-FAILs, proceeds to Rank 1 (world-model) which is the strongest mechanistic candidate. Rank 3/4/5 can run parallel.

## Contract

exp_dev owns: experiment design (smoke layout, data slicing, seed budget), pre-reg per envelope-fail-bands, smoke gate, queue_add via queue_add.sh, REMOTE VERIFY post-ship, self-test per formula-selftests, verdict-emit on HARD-PASS / MIDDLE / HARD-FAIL.

research owns: mechanism class inventory + brain analogue + substrate primitive map + P_deflated estimates + HARD-FAIL thresholds + cross-thread synthesis.

## Autonomy declaration

exp_dev has FULL autonomy over: smoke gate design; how many seeds per class; whether to ship 1 anchor at a time or batch-of-5; CPU vs GPU lane routing; whether to use reachability-confirmed subset only vs full ASDiv-1op; verdict-emit timing; when to escalate back to research for Rank-K deep drill if a class lifts to MIDDLE (research will then own next-level mechanism breakdown).

end of hand-off.
