# Research Post-Compaction Brief — 2026-06-09 substrate-AROUND-LLM

Read this FIRST on context recovery. Strategic direction LOCKED.

## STRATEGIC DIRECTION (LOCKED)

**Substrate IS the AI system. LLM is vendor-swappable language-generation tool.**

NOT substrate-inside-LLM (Path B KBLaM-style integration was shoehorn). YES substrate-around-LLM (substrate orchestrates; calls LLM only when language generation needed).

**Reframe note:** notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md

## SESSION DAY 2 (June 9) WINS

- **Path A SHIPPED** 3-seed multi-seed VALIDATED both families:
  - C1 (Pythia-160M 2-layer): 0.836x ± 0.001
  - D1 (Qwen-1.5B L12+13): 0.852x ± 0.001
  - ~15-17% perplexity improvement; publication-grade reproducibility
- **Path B de-risk** DATA-LIMITED (synthetic non-discriminative subjects); Exp-Dev diagnosed; re-de-risk authorized with DBpedia entities
- **5 drills landed today (June 9):**
  - Path A mechanism: extended effective context via past-hidden-state injection into semantic band; H1 P=0.45; Memorizing Transformer analog
  - Path B variations: 5 backup anchors; PP-107 algebraic gate substrate-unique 2-3 eng-days
  - Programmable per-layer attention routing: NOVEL synthesis (no published direct implementation); 2-source PoC <1 week CPU
  - Generalizable retrieval training: KBLaM-pattern requires 50K-100K facts + 50/50 + frozen Sentence-BERT encoder + every-layer rectangular + answer-token CE alone
  - Substrate-stateful tool orchestration (in flight)

## DEMO BUILD STATUS

- **Panel A LIVE** (Qwen-1.5B + bge-large encoder swap landed; 14/30 → 24/30 benchmark)
- **Q2 Wikipedia 100K ingest RUNNING** (~8 hours; spaCy NER + bge-large CPU encode; detached PID 124696)
- **/converse endpoint build routed to Testbed** (substrate-first conversation; 3-5 days prototype)
- **backend/converse/templates.py + routes/converse.py** STARTED by Testbed (visible in commits)
- **backend/llm/bge_encoder.py** Testbed bge-large encoder swap shipped

## ENGINEERING ANCHORS ROUTED TODAY

- BATCH 4 CRITICAL (25+ anchors; vertical proofs + augmented benchmarks + production hardening + categorical demos)
- BATCH 3 FRESH (30+ anchors; Q-series + TALKS + LM + CAP-DOMAIN + VERIFY + BIO)
- TIER 5C FULL ROADMAP (15 anchors)
- 8 DRILLS CONSOLIDATED BATCH (25 anchors; CHEAP-1/3/4 already HP cycle 195)
- FRESH CHEAP BATCH + T5C-B1 (20 anchors)
- NEGATIVE RESCUES (10 anchors)
- TALKS addendum (5 anchors)
- CYCLE 200 FOLLOWUPS (10 anchors)
- **CONV substrate conversational capabilities (15 anchors; CONV-1/2/3/4/5 Tier 1 highest)**
- **BATCH 5 OVERNIGHT GPU (32 anchors; Path A deepening + Path B alternatives + substrate-augmented benchmarks + scaling + compression + v2.0 exploration)**

## EMPIRICAL STATE END OF DAY 2

- **HONEST 1297 → ~1500+** (cycles 175-201; through day 1; day 2 cycles 202+ pending)
- **Portfolio +127 PP rows** through cycle 201
- 16+ research drills landed (16 day 1 + 5 day 2 today = 21+)
- Compliance stack COMPLETE empirically (3 algebraic pillars + 4 vertical demos + HIPAA + EU AI Act)
- Tier 5c architecture story COMPLETE (PP-203 codebook + PP-204 single-layer + PP-205 differentiability + PP-216 projection + PP-217/218 multi-layer Pythia+Qwen)
- Categorical multi-hop empirically grounded vs BOTH naive AND iterative kNN-LM (+0.983 / 1.0 vs 0.927→0.780)
- 540+ anchors verdicted

## QUADRUPLE GROUNDING (locked end day 1; reaffirmed day 2)

- **Formal/complexity:** Stratified Datalog engine (PTIME P-complete)
- **Empirical:** 218+ PP rows; 4 public KG-QA benchmarks + 4 vertical demos
- **Biological:** Clark-Chalmers extended mind; isomorphic to ACC + hippocampal successor + concept cells
- **Linguistic:** FHRR Wirtinger-differentiable; LARS-VSA + GHRR-Transformer existence proofs; GPT-2 weights explain as VSA (NeurIPS 2024)

## STANDING POST-COMPACTION

1. Read this brief FIRST
2. Check overnight Exp-Dev results (BATCH 5: 32 GPU anchors queued)
3. Check Testbed /converse build progress
4. Synthesize cycles 202+ as they land
5. Standing for substrate-stateful-tool-orchestration drill return
6. v3.0 vision = programmable per-layer attention routing (drill validated novel synthesis)

## DISCIPLINE RULES (active)

- NO time estimates (user feedback; team executes faster than predicted)
- Substrate-around-LLM is product; Path A is research evidence; Path B is OPTIONAL R&D not product gate
- Always research negative findings 2x
- Plain language no hype
- Don't oversell to cryptographic
- Demo discipline: substrate-direct ratio ≥85-90% (per honest re-examination of capability range)

## CRITICAL CROSS-REFERENCES

- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- BATCH 5 OVERNIGHT GPU: notes/research_to_exp_dev_BATCH_5_OVERNIGHT_GPU_2026-06-09.md
- /converse build: notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md
- CONV capabilities: notes/research_to_exp_dev_SUBSTRATE_CONVERSE_CAPABILITIES_2026-06-09.md
- Path A SHIPPED: notes/exp_dev_to_research_PATH_A_SHIPPED_2026-06-09.md
- Path A mechanism: notes/research_drill_path_a_mechanism_5x_2026-06-09.md
- Path B variations: notes/research_drill_path_b_variations_5x_2026-06-09.md
- Programmable routing: notes/research_drill_programmable_attention_routing_5x_2026-06-09.md
- Generalizable retrieval: notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md
- Day 1 brief: notes/research_POST_COMPACTION_BRIEF_2026-06-08_TIER5_SPRINT.md

End of brief. Substrate-around-LLM locked. 32 overnight GPU experiments queued. Standing.
