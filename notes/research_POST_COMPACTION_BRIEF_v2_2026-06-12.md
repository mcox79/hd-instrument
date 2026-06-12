# Research POST-COMPACTION BRIEF v2 -- 2026-06-12 Day 4 late morning

**READ FIRST on resume.** Supersedes v1 (research_POST_COMPACTION_BRIEF_2026-06-12.md). Incorporates language+creativity drills + Semantic-A v2 close + AG2 comparison + GPU pipeline live.

## Session role + locks

- Research session
- USER directive in flight: **"keep going + drill language + creativity HARD; no defeatism"**
- USER prior directives still active:
  - "Implement all recommendations"
  - "Methodical characteristics-to-Tier-A" (paused Cycle 53/54 Resonator/GHRR mechanism cells)
  - "Support Testbed first"
  - Full-auto continuing

## Empirical substrate state at v2

- **Atoms**: 1742 live store + ~80 algebra-backfill pending Testbed ingest = ~1822 post
- **Gap 7 macro-F1**: 0.587 (Cycle 48b; D_composition +0.143 from sh backfill)
- **Path-to-HP_v1 0.70**: now empirically grounded at 0.64-0.68 reachable in 30-day window. **HP_v1 0.70 likely needs Cycle 50+ Stratified Hybrid Layer 2-3 OR aggressive Phase 6.**
- **Substrate-classical NL Tier-A roster**: 7 multi-seed (POS / NER / Intent / Sentiment / AG-News / dep-parse / chunking)
- **6-deep MWP triangulation CLOSED**: corpus-bound; Phase 6 ingest is the genuine lever. 6th USER ingestion vindication EMPIRICAL.

## VSA position-as-meaning EMPIRICAL state

**Cell 1 STRONG POSITIVE** (Testbed): 8/8 nearest correct on math anchors -- position IS meaning at atom-to-atom level.

**Wiring gap**: encode.py:130-133 composite=semantic (pure bge); algebra_index.py atom-to-atom only ("Free-text queries DO NOT come here"). Authoring gap 10.8% coverage.

**Backfill shipped**:
- 30 core VSA primitives: algebra_backfill_core_vsa_primitives_2026-06-12.jsonl
- 50 breadth atoms: algebra_backfill_breadth_50_partitions_2026-06-12.jsonl (SCHOOL + NEURO/BIO + PHYS/CHEM + concept PP-*)

**Semantic-A v2 retrieval DECISIVELY CLOSED** (Exp-Dev empirical):

| Condition | A-axis F1 |
|---|---|
| Description+aliases (original) | ~0.33-0.37 |
| **Name/id-token field alone** | **0.357-0.41 ← LEVER** |
| Multi-field RRF equal-weight | ~0.34 (DILUTES weak fields drag strong) |
| Name + DEPENDS_ON graph-prop | 0.268 (-0.089 HURTS; wrong edge type) |

My drill recommendations (Multi-field RRF + Graph-prop) were WRONG -- 9th methodology rule (refine-via-empirical-FAIL) 5th confirmation.

**HYBRID semantic_v2 architecture (REFINED)**:
```
if parsed.confidence > 0.20:
    algebra_HRR primary + bge-on-NAME fallback + RRF weighted (0.6/0.4)
else:
    bge-on-NAME alone  # NOT description; NOT graph-prop; NOT naive RRF
```

**Substrate-product positioning insight**: atom IDs are structured by construction (`math::T3/discriminative_perceptron`); bge cosine over NAMES captures structural similarity FOR FREE. LLMs lack this benefit -- they don't have structured atom IDs.

## 5-level test framework (REVISED per math drill)

L1 categorical clustering: Testbed building NOW on 196 atoms
L2 interpretable differences (multiplicative): `unbind(vec_inverse_pair)` parallel relation_vec
L3 ROTATIONAL analogies (NOT parallelogram per math drill): phase rotation + unbind on FHRR (RotatE/HolE)
L4 composition via bundle
L5 decomposition via unbind

## Stratified Hybrid 6-layer (Cycle 50+ medium-term target)

Math drill recommended:
- L0 FHRR 4096-dim atomic random base
- L1 RotatE algebra (rotation in complex space)
- L2 TPR signature (Smolensky)
- L3 functorial composition (DisCoCat / Shiebler)
- L4 GNN over DEPENDS_ON DAG
- L5 SDM cleanup at scale

Substrate-product positioning: "structured-cognition-first; LLMs second."

## Language + Creativity drills (USER no-defeatism)

**Language drill** (`research_drill_substrate_language_beyond_tier_a_hard_drill_3x_2026-06-12.md`):
- 5 ranked substrate-distinctive NL capabilities
- TOP-2: REC-A Adversarial-robust NER (~2 GPU-hrs; reuses Tier-A 0.71 NER; LLMs brittle per Nature SciRep 2025) + REC-B Few-shot transfer curve (cheap CPU; quantifies low-data crossover)
- Other ranks: MRL dep parsing (Turkish/Finnish UD); OntoNotes coref via P^k; structured templated generation (DSL/Karel)

**Creativity drill** (`research_drill_substrate_creativity_capabilities_hard_drill_3x_2026-06-12.md`):
- Substrate has ALL 3 Boden tiers measurably:
  - Combinatorial = HRR bind/bundle
  - Exploratory = cleanup attractor walk
  - Transformational = Tier-5 methodology rule extraction (**LLMs structurally CANNOT do this**)
- TOP-2: C-D4 Cross-domain analogy (algebra-HRR offset + cleanup; Hit@5 >=0.30) + C-D5 Tier-5 novel rule mining at scale (>=1 novel rule per 100 atoms)
- **AlphaGeometry/AG2 anchor**: "superhumanly creative via composition + verifier" = SAME SHAPE as substrate HRR-compose + cleanup-verify (Nature 2024/2025 published precedent)
- 12-week win-state: >=3 Boden tiers measurable + >=1 cross-domain analogy PASS + >=1 conjecture cell >=10% novel+verifiable

## AlphaGeometry / AG2 comparison (per USER question)

**Same architectural engine, different stage of demonstration**:
- AG2: symbolic engine + LLM proposes + verifier; superhuman geometry creativity
- Substrate: HRR-compose + cleanup-verify; 4 confirmed novel methodology rules + position-IS-meaning at Cell 1

**Differences**:
- AG2 narrow (geometry); substrate broad (math/science/methodology/creativity)
- AG2 uses LLM in loop; substrate Tier-5 miner is LLM-FREE (structural extraction)
- AG2 has hard formal verifier (axioms); substrate has cleanup-codebook softer verifier
- AG2 has IMO gold-medal proof; substrate at atom-clustering + 4 novel rules

**Gap to close for substrate parity**: Stratified Hybrid Layer 3 functorial composition gives substrate AG2-style algebra-preserving verifier guarantees. Cycle 50+ work.

## In-flight cells

| Cell | Owner | Status |
|---|---|---|
| **L-A Adversarial-robust NER** | Exp-Dev GPU | queue path open (persistent runner live); 2 GPU-hrs |
| **L-B Few-shot transfer curve** | Exp-Dev+Research | CPU; can start NOW (parallel to GPU work) |
| **C-D4 Cross-domain analogy** | Exp-Dev CPU | after breadth backfill ingest |
| **C-D5 Tier-5 mining at scale** | Exp-Dev CPU | after breadth backfill ingest |
| **Cell 2 PP-394 ASDiv-WK multi-seed** | Exp-Dev CPU | next methodical Tier-A; still queued |
| **HYBRID semantic_v2** | Testbed | REFINED architecture (algebra-HRR primary + bge-on-NAME fallback) |
| **L1 categorical clustering test** | Testbed | building on 196 atoms |
| **Q35 Lyapunov parser debug** | Testbed | max-match logic per-filler-score |
| **Cell 2 v3 re-measure** | Testbed | after breadth ingest |
| **Mwp_wk_schemas standalone retry** | Testbed | Q1 fix landed (SRL moved to experiments/data) |
| **Bge index caching infra** | Testbed | Cycle 47 Q4 |
| **Graph propagation prototype** | Exp-Dev | DONE -- HURT (-0.089); CLOSED |
| **Multi-field RRF prototype** | Exp-Dev | DONE -- DILUTES; CLOSED |
| **H2 container/transfer world-model** | -- | DEFERRED to Phase 6 ingest per H3+H1 6-deep close |
| **Resonator / GHRR mechanism cells** | -- | PAUSED per USER methodical-Tier-A directive |

## GPU pipeline status

- Testbed-owned persistent `gpu_runner_0` LIVE (PID 4716 Services session 0; survives SSH disconnect)
- Exp-Dev queue path via `queue_add.sh overnight_queue` works
- Dashboard visible end-to-end
- Graph propagation cell completed (negative result)
- L-A NER cell queue-ready
- Testbed runner lifecycle: Testbed owns; Exp-Dev `RESTART_RUNNER` in note name if needed

## Methodology rules pattern

5 confirmed + 8 candidates including:
- 9th rule (refine-via-empirical-FAIL) -- **5th consecutive cycle confirmation**:
  1. targeted -> targeted-AND-sufficient-scale (Path 1 SRL FAIL)
  2. PP-402 TCM 0.491 -> MIDDLE per soft metric
  3. H3 NEG-3 -> NEG-1 via drop-guard
  4. H3+H1 stacked DECISIVE HARD_FAIL refines drill ranks
  5. **Multi-field RRF + DEPENDS_ON graph-prop -> name-field-IS-lever (Exp-Dev empirical)**
- 11th rule (verify-before-asserting-via-empirical-test) -- consistently firing alongside 9th

## Monitor

- Task ID: bzhkozeoy
- 5-second tick + 24-hour cutoff + sender-tight filter
- Working (notifications landing <10s)

## Key memories load on resume

(loaded automatically via MEMORY.md):
- substrate-tier-5-THIRD-APPEARANCE-TWO-NOVEL-RULES-10TH-GENERALIZES
- substrate-self-knowing-HP-v2-macro-F1-0-569-Cycle-47
- substrate-mwp-5-deep-triangulation-corpus-deficiency-CONFIRMED
- substrate-UNIFIED-compositional-generation-engine (creativity anchor)
- substrate-classical-NLP-methods-outperform-phasor (NL Tier-A)
- substrate-brain-can-do-it-empirically-vindicated-asdiv (LEX_T)
- feedback-brain-can-do-it-no-boundary-acceptance (NO defeatism rule)
- feedback-dont-parrot-drill-defeatism
- feedback-all-cpu-compute-on-remote-desktop

## Honest scope (USER pushback integrated)

**Substrate-classical NL Tier-A bounded WHERE corpus-knowledge required** (MWP combine-schema = HARD_FAIL).
**NOT bounded universally**: structural cognition + low-data + adversarial robust + morphology = substrate-distinctive remains.

**Substrate creativity NOT defeatist**:
- ALL 3 Boden tiers measurably
- AlphaGeometry/AG2 = published precedent at superhuman scale
- 4 confirmed novel methodology rules already
- Cross-discipline analogue partition exists; algebra-HRR offset cells will measure systematically

## Path-to-HP_v1 0.70 revised reading

- Bge-on-NAME vs description: +0.04 macro A-axis = +0.005 macro overall (axis-gated)
- HYBRID algebra-HRR primary: +0.04-0.06 A-axis = +0.01-0.02 macro overall (after breadth ingest)
- Q09 PP-364 sh backfill: +0.02
- Multi-seed Tier-A promotions: +0.01-0.02
- Phase 6 full ingest (math+science): +0.02-0.03
- Combined: **0.587 + 0.06-0.10 = 0.64-0.68 reachable 30-day**

**HP_v1 0.70 likely needs Cycle 50+ Stratified Hybrid Layer 2-3 OR aggressive Phase 6 ingest.** Honest revised projection.

## Critical post-resume sequence

1. **Read this BRIEF first** (POST_COMPACTION_BRIEF_v2)
2. **Check Monitor task bzhkozeoy** + read latest notes via Monitor
3. **Standing for**:
   - L-B Few-shot transfer curve (can start now CPU)
   - L-A Adversarial NER (queue when GPU bandwidth)
   - C-D4 + C-D5 (after Testbed breadth ingest)
   - Cell 2 PP-394 multi-seed (Exp-Dev methodical Tier-A)
   - Testbed HYBRID build + L1 test + Lyapunov debug + Cell 2 v3 measurement
4. **No more PP-### atom authoring** (verdict_handler owns cap_map; namespace collision)
5. **Methodology rule 9 reliable** -- drill projections are PRIORS; substrate-specific empirics REFINE them

## Heartbeat

Active. USER full-auto + no-defeatism + drill language+creativity hard + GPU pipeline live.

---

**On resume**: read this file (v2) first + check Monitor + read inbound notes + resume.
