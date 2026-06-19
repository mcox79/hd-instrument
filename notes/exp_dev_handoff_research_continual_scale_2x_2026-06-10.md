# exp_dev hand-off -- research: continual learning scale 2x (production push)

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_continual_scale_2x_2026-06-10.md.
Current D2 battery (D2.2 + D2.4 + D2.7 HARD_PASS, D2.1 MIDDLE_BAND) validated at
1000-item synthetic scale. Research drill identifies 5 decisive tests and 8 push
paths to extend to 10K+ production scale with real concept drift.

**Pause state:** Check data/orchestrator_paused.flag before any queue dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS
and POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands,
queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile.
Orchestrator does NOT specify numerical parameters.

---

## Anchor Candidates (rank-ordered)

### 1. D2.1-HARD_PASS-RESCUE -- dual-CLS with N_buffer=10

- Anchor pointer: D2.1 MIDDLE_BAND verdict (dual=0.962, slow=0.922, lift=+4pp vs
  +10pp HARD_PASS threshold). Research note Synthesis 4 predicts that N_buffer=10
  (replay every 10 new writes instead of 100) will increase lift to >= 0.10 recall@1
  above slow-only. This is the MCT alpha-process timescale argument: replay rate
  must exceed the drift rate of new writes.
- Substrate-product reading: D2.1 HARD_PASS would confirm the full 4/4 D2 battery
  at production scale, establishing the dual-CLS architecture as validated for the
  slow-generalizer capability (currently the only missing CLS component).
- Tier hint: CPU (pure outer-product algebra, no GPU needed).
- Why now: cheapest fix; one parameter change; directly converts MIDDLE_BAND to
  potential HARD_PASS. No new mechanism required.

### 2. LONG-STREAM-10K -- D2.2 + D2.4 at M=10K Wikipedia stream

- Anchor pointer: research note TEST-1. D2.2 (PP-319 HARD_PASS) + D2.4 (PP-322
  HARD_PASS) combined on a 10K-item Wikipedia sentence embedding stream. Check
  recall@1 on oldest 500 items at M=1K, 2K, 5K, 10K checkpoints.
- Substrate-product reading: validates whether the production-scale capacity formula
  (neurogenesis + per-shard K/N < 0.40) survives real LLM embedding distributions.
  This is the gate for the enterprise-KB product claim (10K+ items with stable recall).
- Tier hint: CPU. Pythia-160m embedding generation is the primary cost (validated
  setup per feedback-causal-lm-last-token-pool).
- Why now: the 30-day realistic stream (v425, PP = retention=0.999 over 1-day windows)
  showed promising results but only at 1-day scale. The 10K test is the production gate.

### 3. CONCEPT-DRIFT-TEST -- Misra-Gries + D2.3 reconsolidation integration

- Anchor pointer: research note TEST-2 + Synthesis 1. PP-4b Misra-Gries drift
  detection (HARD_PASS, ratio=6.59x) is currently passive monitoring only. This
  anchor connects it to D2.3 reconsolidation-edit: when drift is detected, trigger
  targeted edits on recently-written items. Measure: drifted item new-value recall,
  undrifted item degradation.
- Substrate-product reading: GDPR Art 16 (right to correction) + continuous fact-
  updating use case. First substrate-native automated drift-detect-and-correct loop.
- Tier hint: CPU. Small M (5K items), short experiment.
- Why now: PP-4b HARD_PASS already confirmed detection; the integration with D2.3
  is a single architectural connection that completes the drift-correction capability.

### 4. WIKIPEDIA-STREAM-CONTINUAL -- full D2 stack real-data validation (TEST-3)

- Anchor pointer: research note TEST-3. N=8192 (or N=4096), 10K Wikipedia sentences,
  real Pythia-160m last-token embeddings. D2.1 + D2.2 + D2.4 combined. Sleep-defrag
  every 1K writes. 3 seeds. Checkpoints at 1K, 3K, 5K, 10K.
- Substrate-product reading: this is the definitive synthetic-to-real audit for the
  D2 continual learning battery. If this HARD_PASSES, the production-scale continual
  learning claim is grounded in real LLM embedding space.
- Tier hint: CPU (3-6 hours wall, 3 seeds, Pythia embedding generation + D2 mechanics).
  Sequenced AFTER TEST-1 (which validates the D2.2+D2.4 stack alone first).
- Why now: required before any product-facing claim about continual learning at scale.

### 5. MIXED-TASK-INTERFERENCE -- task-subspace partition validation (TEST-4)

- Anchor pointer: research note TEST-4 + Push Path 3. 3 task types (factual,
  compositional, multi-hop), 1K items per task, interleaved. Task-type HD projection
  matrices P_task provide structural separation. Validates whether cross-task
  interference at M=3K is controlled.
- Substrate-product reading: gate for multi-tenant enterprise deployments where the
  KB serves multiple task types simultaneously. Also validates the MoE-CL mapping:
  substrate's content-based routing already is a sparse MoE system by construction.
- Tier hint: CPU. Can run alongside TEST-1 (independent workload).
- Why now: the MIDDLE_BAND result on D2.5 empowerment (emp-policy lift=6.8%) suggests
  that multi-task coordination benefits are currently weak. TEST-4 is a cleaner test
  of the structural separation hypothesis.

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_continual_scale_2x_2026-06-10.md
- Prior 3x drill: d:/AI/hd-instrument/notes/research_drill_continual_learning_revival_3x_2026-06-10.md
- Prior 5x drill: d:/AI/hd-instrument/notes/research_drill_continual_full_cls_5x_2026-06-10.md
- D2.1 metrics: data/exp_d2_1_dual_cls_cpu_v1/metrics.json (MIDDLE_BAND, dual=0.962)
- D2.2 metrics: data/exp_d2_2_frequency_decay_cpu_v1/metrics.json (HARD_PASS, AUC=0.886)
- D2.4 metrics: data/exp_d2_4_neurogenesis_cpu_v1/metrics.json (HARD_PASS, recall=1.000)
- D2.7 metrics: data/exp_d2_7_intentional_forgetting_cpu_v1/metrics.json (HARD_PASS, retained=1.000)
- PP-4b Misra-Gries (drift detection): notes/substrate_capability_map.md PP-4b annotation
- 30-day realistic stream result: v425 annotation in notes/substrate_capability_map.md
- Pythia embedding setup: feedback memory (last-token pooling for causal LMs)

---

## Contract Section

exp_dev should:
1. Design smoke tests first for anchors 1-3 (quick validation before FULL runs).
2. For anchor 2 (LONG-STREAM-10K), generate Pythia-160m embeddings for 10K Wikipedia
   sentences first (separate step), then run D2.2+D2.4 mechanics on the embedding vectors.
3. Pre-register HARD-PASS / MID / HARD-FAIL bands per envelope-fail-bands policy
   BEFORE running any experiment.
4. Route all experiments to CPU queue (data/local_cpu_queue or data/remote_cpu_queue)
   unless a specific experiment requires GPU (none of the 5 tests listed above do).
5. Anchor 4 (WIKIPEDIA-STREAM-CONTINUAL) is a multi-seed FULL run; sequence AFTER
   anchor 2 smoke confirms the D2.2+D2.4 mechanism is working on real embeddings.

## Autonomy Declaration

exp_dev decides ALL of: specific N values, M values per checkpoint, exact decay
parameters, neurogenesis threshold values, number of seeds per tier (smoke vs full),
anchor names, queue routing, ETA, and whether to batch multiple anchors per cluster.
This hand-off is a task specification, not a design specification.
