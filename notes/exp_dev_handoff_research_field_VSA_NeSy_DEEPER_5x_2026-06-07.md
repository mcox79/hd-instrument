# exp_dev hand-off -- research: VSA NeSy Rule Engine DEEPER 5x

**Filed by:** research sub-agent, 2026-06-07
**Trigger:** DEEPER 5x drill on VSA as NeSy execution layer + rule encoding + differentiable VSA + resonator multi-hop
**Research note path:** notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching any GPU anchors. CPU/local anchors may run regardless.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Anchor Candidates (rank-ordered by cost-to-insight ratio)

### 1. Rule storage + auditable unbind chain (LOCAL, ~1-2 hrs)
- **Anchor pointer:** Research note Probe 1 -- rule storage as bind(predicate_HV, condition_HV) bundles; apply via unbind chain; measure top-1 cosine discrimination
- **Substrate-product reading:** Demonstrates substrate as rule engine in existing production architecture. Zero new code beyond labeling existing bundle-write + retrieve as rule_store + rule_apply. If top-1 cosine > 0.80 at M=100 rules, the "substrate as auditable rule engine" customer pitch is empirically grounded.
- **Tier hint:** Local (laptop CPU). Analyzer-style run on existing substrate. No cloud needed.
- **Why now:** Cheapest decisive test that directly grounds the NeSy / rule engine product framing. All required substrate primitives already exist. HARD-PASS in 1-2 hours.

### 2. Compositional retrieval algebraic guarantee test (LOCAL, ~1-2 hrs)
- **Anchor pointer:** Research note Probe 10 -- compositional generalization via VSA. Store individual entities A, B; query with bind(A, B) for novel pairs; measure recall.
- **Substrate-product reading:** The algebraic guarantee (compositional by construction) must hold empirically at production scale M=1M. If recall > 90% for novel compositional pairs at N=4096, the claim is auditable. If recall < 70%, the interference from M=1M scale degrades the guarantee and the compositional pitch needs qualification.
- **Tier hint:** Local (laptop CPU). Uses existing codebook. Analyzer pass.
- **Why now:** Directly addresses the Lake-Baroni framing (neural models fail compositional generalization; substrate succeeds by construction). Auditable in 1-2 hours.

### 3. Resonator network bridge entity extraction (LOCAL/Remote CPU, ~2-4 hrs)
- **Anchor pointer:** Research note Probe 4 -- resonator networks for multi-hop QA bridge entity factorization. Frady 2020/2022. Synthetic 2-hop query test.
- **Substrate-product reading:** The multi-hop revival mandate (MEMORY.md: "multi-hop extremely important") requires a bridge-entity extractor. The resonator network is the candidate mechanism. If resonator factorizes synthetic bind(role_A, bind(role_B, entity_C)) composites with > 70% accuracy at M=1000 codebook size, the mechanism is validated for the production pipeline.
- **Tier hint:** Remote CPU (numpy resonator implementation, ~100 lines). No GPU required. Frady 2020 appendix provides reference code.
- **Why now:** Multi-hop revival is user-declared priority. Resonator is the cheapest falsifiable test of the bridge-entity extraction hypothesis. Pre-test before any cloud multi-hop encoding.

### 4. LLM-proposes / substrate-verifies rule verification latency (Remote CPU or LOCAL, ~3-4 hrs)
- **Anchor pointer:** Research note Probe 2 -- NeSy execution layer pipeline. LLM generates hypothesis; substrate applies rule verification via unbind chain; measure accuracy + latency.
- **Substrate-product reading:** The 98% vs 37% clinical QA benchmark (lit validated) was achieved with external knowledge graph + LLM. If substrate can match or exceed this with internal rule bundles at < 1ms latency per rule application, the product differentiator (no external graph store) is validated.
- **Tier hint:** Remote CPU or local (depends on LLM API access; substrate-side is CPU). Anthropic API key available (MEMORY.md).
- **Why now:** Directly validates the regulated industry commercial pitch. Can use a small number of medical/legal test cases from public benchmarks.

### 5. Differentiable bipolar VSA gradient smoke (LOCAL, ~2-3 hrs)
- **Anchor pointer:** Research note Probe 3 -- STE gradient through bipolar {-1,+1} sign() operation. Verify gradient is non-degenerate in production encoder architecture.
- **Substrate-product reading:** If STE gradient is non-degenerate, joint encoder + rule optimization is tractable. This is the gate for the larger differentiable VSA capability. Expected cheap smoke: synthetic rule loss function, measure gradient magnitude vs zero.
- **Tier hint:** Local (laptop CPU/GPU). Smoke only -- verify gradient flows, not full training run.
- **Why now:** Pre-test for differentiable VSA joint training (the larger capability). Failure here closes Probe 3 without expensive training run.

---

## Context Pointers

- `notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md` -- this research note; all technical depth, P_deflated, HARD-PASS/HARD-FAIL thresholds
- `notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md` -- prior VSA foundation drill (substrate = mature deployed VSA; MAP Permute HP'd; arXiv 2512.14709 identity)
- `notes/research_drill_field_modern_hopfield_5x_2026-06-07.md` -- modern Hopfield drill (substrate < 1% capacity; retrieval = transformer attention algebraically)
- `notes/substrate_capability_map.md` -- current cap_map; K-hop PP-11 K=12 recovery=0.987 empirically validated
- MEMORY.md entry: "multi-hop extremely important, must REVIVE despite 3 HF; treat closure as working hypothesis NOT settled conclusion"
- MEMORY.md entry: "NORTH STAR: deployed system that EMPIRICALLY exceeds LLMs of relative size in clear measurable ways"
- Frady 2020 (Neural Computation): https://arxiv.org/pdf/1906.11684 -- resonator network reference implementation
- LARS-VSA (arXiv 2405.14436): https://arxiv.org/html/2405.14436v1 -- bipolar binding + HD attention

---

## Contract

- Pre-reg per envelope-fail-bands: HARD-PASS + HARD-FAIL bands BEFORE smoke per research note Section "Falsifiable Predictions"
- Self-test per [[feedback-formula-selftests]] and [[feedback-function-signature-mismatch-self-test-blind]]
- Multi-seed FULL on smoke clearance (where applicable; analyzer-style runs may be deterministic)
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0
- Ship via bash tools/orchestrator/queue_add.sh
- POST-SHIP REMOTE VERIFY
- status_log entry per anchor with plain_language + importance

## Autonomy Declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. Research passes anchor POINTERS only. If exp_dev determines a different sequence or substitutes a cheaper pre-test, that is exp_dev's call.

**Priority note:** Anchors 1-3 are all LOCAL/Remote CPU and can run without pause-flag check. Anchor 4 requires LLM API. Anchor 5 is LOCAL. All five can be dispatched while GPU queue is paused.
