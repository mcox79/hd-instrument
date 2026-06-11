# exp_dev hand-off -- research: slipnet-substrate refinement 2x

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** PP-327 SLIPNET-SUBSTRATE HARD_PASS (hits1=0.985, lift=+0.158 on synthetic 30-50 node slipnet, 2 domain pairs). Research 2x drill completed. Research note at: notes/research_drill_slipnet_refinement_2x_2026-06-10.md

**Pause state:** check data/orchestrator_paused.flag before dispatching queue items.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Why now

PP-327 validated a slipnet-spreading mechanism at small (30-50 node) synthetic scale. The research drill identifies a staged ladder of 6 push paths, each with a cheap CPU test as gate. The SLIPNET-SCALE-SMOKE-100 is the gate experiment for all further slipnet work. ConceptNet 458K facts are already loaded in the testbed. This is a pure CPU experiment (no GPU required for SMOKE).

---

## Anchor candidates (rank-ordered)

### 1. SLIPNET-SCALE-SMOKE-100 (Tier B, CPU)
- Anchor pointer: notes/research_drill_slipnet_refinement_2x_2026-06-10.md Section "CHEAP DECISIVE TEST"
- Substrate-product reading: validates that the PP-327 mechanism is not confined to the 30-node synthetic setting. A 500-node ConceptNet-derived slipnet with derived conceptual depth (betweenness centrality) and sparse matrix-vector spreading. Five evaluation groups: Scale-500, Cross-domain Pair B (finance <-> neuro), Cross-language (Eng-Spa), Depth-3 chain, Temporal.
- Tier hint: CPU, 3-4 hours. ConceptNet data already available in testbed at data/conceptnet*.
- Why now: all further slipnet engineering gates on this result. Cheap. No GPU. Fast.
- Pre-reg target: delta per group as per note Section "CHEAP DECISIVE TEST" acceptance criteria.

### 2. SLIPNET-CROSS-DOMAIN-PAIR-A (Tier B, CPU)
- Anchor pointer: notes/research_drill_slipnet_refinement_2x_2026-06-10.md Section 4.1 Pair A
- Substrate-product reading: justice/freedom/rights (political) <-> biological ecosystem (ecology) domain pair. High difficulty, high ceiling. Tests structural isomorphism on semantically distant domains with no surface co-occurrence.
- Tier hint: CPU, ~2 hours. Requires ConceptNet subgraph construction per domain (~200-500 nodes).
- Why now: this is the highest-value domain pair for enterprise positioning (legal + biology are two distinct high-value verticals).
- Pre-reg target: hits1 >= 0.75 on 20-triple test with slipnet vs baseline.

### 3. SLIPNET-CROSS-LANGUAGE-ENG-SPA (Tier B, CPU)
- Anchor pointer: notes/research_drill_slipnet_refinement_2x_2026-06-10.md Section 4.4
- Substrate-product reading: align English and Spanish slipnets at NSM-prime nodes (65 universal semantic primitives per Wierzbicka). Procrustes rotation in VSA embedding space. Cross-language analogy without LLM. GDPR-relevant capability (no external API call).
- Tier hint: CPU, ~3 hours. Multilingual ConceptNet required (check if data/conceptnet* contains multilingual edges; if not, this requires data download step first).
- Why now: highest-ceiling path for the North Star goal (distinct from LLM analogy capability; cost advantage ~1000x at inference time).
- Pre-reg target: hits1 >= 0.65 on 20-triple cross-language test.

### 4. SLIPNET-DEPTH-3-CHAIN (Tier B, CPU)
- Anchor pointer: notes/research_drill_slipnet_refinement_2x_2026-06-10.md Section 4.3
- Substrate-product reading: 3-hop chain analogy (A -r1-> B -r2-> C) <-> (A' -r1'-> B' -r2'-> C') using FHRR binding for chain encoding. Validates that VSA chain noise at K=3 is below the detection threshold at N=4096. Prerequisite for causal-chain analogy product capability.
- Tier hint: CPU, ~1-2 hours. Pure numpy/VSA computation. No model loading.
- Why now: structurally prerequisite to the 5000-node slipnet (which uses 3-hop chains as the primary cross-domain test). Cheap to run before committing to 5000-node engineering.

### 5. SLIPNET-5000-NODE (Tier A, GPU -- deferred until SMOKE-100 passes)
- Anchor pointer: notes/research_drill_slipnet_refinement_2x_2026-06-10.md Section 4.2
- Substrate-product reading: 5000-node ConceptNet slipnet with fractional graph Laplacian (alpha=0.7). Requires eigen-decomposition of the Laplacian (GPU for tractability at 5000 nodes). Cross-domain Pair A or B as the primary test.
- Tier hint: GPU. DO NOT DISPATCH until SLIPNET-SCALE-SMOKE-100 passes (otherwise risks engineering work on a failing mechanism).
- Why now (deferred): this is the target scale for product deployment; the path is clear but gated on SMOKE.

---

## Context pointers (file paths, not summaries)

- notes/research_drill_slipnet_refinement_2x_2026-06-10.md -- full research note with mechanism analysis, math, P estimates
- notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md -- prior cross-domain analogy research; structural-alignment-mapping mechanism composes with slipnet
- notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md -- compositional cliff crossing; per-level cleanup = slipnet depth mechanism
- notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md -- hierarchical cleanup = slipnet abstract-node operation
- notes/substrate_capability_map.md -- current cap_map; PP-327 row
- data/conceptnet*.jsonl (or equivalent) -- ConceptNet 458K facts loaded in testbed

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands from research note Sections "CHEAP DECISIVE TEST" and "FALSIFIABLE PREDICTIONS" BEFORE any smoke dispatch.
- Self-test per [[feedback-formula-selftests]]: verify sparse matrix-vector multiply produces expected activation decay before running full eval.
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0.
- Ship via bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code (5 = post-ship verification failed).
- status_log entry per anchor with plain_language + importance.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, ConceptNet subgraph construction details, depth-derivation method (betweenness vs PageRank vs hyperbolic), Procrustes alignment implementation details. The research note provides the mechanism and direction; exp_dev owns the experiment design.

---

## Filed by

Research sub-agent, 2026-06-10, post PP-327 HARD_PASS 2x drill.
