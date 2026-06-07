# exp_dev hand-off -- research: parametric knowledge synthesis

Filed-by: research sub-agent
Trigger: notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md
Pause state: respect data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and context pointers only. Exp_dev designs the experiments from these pointers.

---

## Anchor candidates (rank-ordered)

### 1. Wikipedia-substrate recall pre-test on NQ + TriviaQA (HIGHEST PRIORITY)
- Anchor pointer: CELL-2 v3 Wikipedia cache (5.84M articles already extracted at production encoder)
- Substrate-product reading: If substrate+Qwen-1.5B achieves NQ exact match >= bare Qwen + 10 points, this is the v1 demo benchmark for the NORTH STAR LLM comparison.
- Tier hint: Tier 1 -- direct path to shipped v1 demo benchmark
- Why now: CELL-2 v3 cache exists, encoder is production-ready, the pre-test is 1-2 hours. This is the cheapest decisive test for the biggest open question (does Wikipedia-substrate match frontier LLM on encyclopedic queries?).
- Pre-reg bands pre-registered in research note Section 5 and Section 8.

### 2. Substrate recall scaling: 500K -> 1M -> 5M facts
- Anchor pointer: Pattern B at 16 bytes/fact (cycle 162 result); CELL-4 at 100K perfect recall
- Substrate-product reading: Determines whether 100M-fact substrate requires hierarchical chunking (known engineering path) or whether a single-instance substrate can hold 1M+ facts at high recall.
- Tier hint: Tier 2 -- must pass before any 100M-fact product claim is made
- Why now: The gap between 100K (confirmed) and 5.84M (unconfirmed recall) is the biggest empirical unknown in the scaling thesis.

### 3. Small-LLM reader quality: Qwen-1.5B vs Llama-1B vs Pythia on retrieved context
- Anchor pointer: Cycle 158 (+0.35 F1 on HotpotQA); feedback on causal LM last-token pool
- Substrate-product reading: The NORTH STAR comparison is substrate+small LLM vs frontier LLM. Reader quality determines the ceiling for the substrate+small LLM system.
- Tier hint: Tier 2 -- needed to interpret pre-test results and bound v1 demo performance
- Why now: If Qwen-1.5B is a weak reader (does not use retrieved context effectively), the pre-test will show MIDDLE-BAND results for the wrong reason.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md
- CELL-2 v3 Wikipedia cache: data/cell2_results/ (check rsync status)
- Cycle 158 HotpotQA result: check cap_map for substrate+LLM retrieval row
- Cycle 162 Pattern B 16 bytes/fact: cap_map storage row
- CELL-4 100K perfect recall: cap_map capacity row
- NORTH STAR memo: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md (v1 plan section)

---

## Contract

Exp_dev: read the research note for pre-registered HARD-PASS / HARD-FAIL / MIDDLE-BAND bands before dispatching any anchor. Smoke gate required for pre-test (1000 questions before full eval). Production encoder Pythia sanity check required before any cloud dispatch per feedback_pythia_sanity_check_before_cloud.md.

## Autonomy declaration

Exp_dev decides: exact script design, which queues (local GPU vs remote GPU vs CPU), whether to batch anchors 1+2 together, smoke gate parameters. Orchestrator does not specify these.
