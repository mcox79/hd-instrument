# M3 Cortex Layer Design — substrate operating off Stage 1 findings

**Filed:** 2026-07-03 (Director; USER-directed after Director-KB char-trigram bottleneck discovery + tandem architecture reframe)
**Purpose:** Design spec for the cortex layer that consumes atom-store retrieval and applies Stage 1 laws + prior findings as ACTIVE CONSTRAINTS on substrate operations
**Composes with:**
- Stage 1 CG_META atoms (storage-strategy, scale-free, topology-free, algebra-composition) — locked earlier this arc
- Director-KB pipeline (`hdlab/director_kb.py`) — currently char-trigram encoded (bottleneck)
- VSA Cells 1-4 (analogy / composition / multi-hop / episodic) — CG_MB'd tonight
- USER-clarified tandem architecture (dense retrieval frontend + substrate reasoning backend)
- USER 2026-06-28 project note "M3 architecture needs cortex layer above substrate"

## Problem statement

Stage 1 CG_META atoms (substrate physics laws) are DOCUMENTED in the atom store but not YET ACTIVE — the substrate performs new operations without automatically consulting the atoms that govern those operations. Example: when substrate is about to compose 5 primitives, it should automatically apply the storage-strategy law (SHARDED > BUNDLED at scale) — but currently it doesn't query for that law; it just uses whatever storage policy the cell-author hardcoded.

**The M3 cortex layer** is the substrate-native component that:
1. Detects when a substrate operation is about to happen
2. Queries the atom store for atoms relevant to that operation class
3. Applies retrieved constraints to modify the operation's execution
4. Atomizes any new findings back to the atom store (closed loop)

## REVISION 2026-07-03 EARLY AFTERNOON (post-drill informed)

Original design assumed rerank-tandem was the retrieval-fix. Composite ruling 2026-07-03 + optimal-arch drill invalidated that assumption:
- ORACLE=0.783 proved composition is NOT the bottleneck (unchanged)
- Rerank-tandem HARD_FAILed (retrieval bottleneck stayed at 0.083 vs 0.783)
- Root cause: hop-1 dense retrieval structurally cannot reach bridge chunks that share no lexical/semantic overlap with query — an encoder-quality question maps onto this only partially
- Drill recommendation: extend `KGStore` (which `hdlab/director_kb.py` already runs on) with iterative graph-walk retrieval

**Revised architecture inserts a NEW Layer 0.5 (KG-walk retrieval) between Layer 0 (dense frontend) and Layer 1 (VSA compositional).** Layer 0.5 outcome-gated on Wikipedia semantic-KB detour (in flight):
- HARD_PASS → Layer 0.5 is graph-walk-primary as described below
- **HARD_FAIL → NO AUTO-PIVOT (USER-locked 2026-07-03 [[feedback_architecture_decision_HF_deep_dive_before_pivot_USER_2026-07-03]]).** Sequence: (1) deep-dive mechanism-attribution — structural vs implementation vs infrastructure vs scope; (2) Skunkworks-verify diagnosis; (3) THEN decide pivot vs iterate vs halt. Do not treat all HFs as equivalent. Encoder-swap is candidate fallback only if STRUCTURAL diagnosis confirmed; implementation/scope failures get iteration, not abandonment.
- MIDDLE → hybrid: graph-walk for detected-bridge-query subclass, dense-only for lexical-overlap subclass

## Architecture (staged)

### Layer 0: Sensory input (retrieval frontend)

**Current:** Director-KB uses `CharTrigramEncoder` for atom-name indexing. Limited retrieval quality for atom-body content queries.

**Target (per USER tandem architecture clarification):** dual-index atom store:
- **char-trigram index** for exact entity-name lookup (cheap, deterministic, works for known-atom-name queries — e.g., "get the storage-strategy CG_META atom by anchor")
- **Dense encoder index (bge, or stella_en_1.5B_v5 per prior 2026-07-03 encoder drill)** for content-similarity queries (e.g., "find all atoms about capacity limits" — semantic query over atom bodies). Encoder swap is orthogonal to Layer 0.5 fix per drill: bge is near-ceiling on single-hop; upgrade for license/context-length reasons, not for bridge-chunk recovery.
- Hybrid ranking (RRF or weighted sum) for queries that could be either

### Layer 0.5: KG-walk retrieval (NEW; drill-informed 2026-07-03)

**Purpose:** surface bridge chunks that Layer 0 dense retrieval structurally cannot reach (validated regime per Exp 1 MM_SCALE_BOUNDED bridge-entity coverage 0.982 on synthetic + Exp 2 MB_STRUCTURAL_LIMIT PPR recovery 0.170 on random-KG floor + Exp 2C MEASURED_MECHANISM PPR recovery 0.993 on real semantic KG within hub-concept-bridge scope).

**Composition of existing primitives (per drill KEY REFRAME: Director-KB is already a knowledge graph):**
- `hdlab/kg_traversal.py::KGStore` — already the graph; Wikidata triples (5,510 relations from 2026-06-14 ingest at `data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl`) directly usable as production-scale semantic KG
- `hdlab/char_trigram_encoder.py::CharTrigramEncoder` — bridge-entity extraction from hop-1 candidates via fuzzy match against KGStore node names (Exp 1 confirmed mechanism at synthetic-scale; real-scale re-test required)
- New ~50-line addition: Personalized PageRank (sparse matrix power iteration, α=0.15, 3-5 fixed iterations, ppr[s]-only scoring per Exp 2 mid-smoke correction to HippoRAG authorship-mass pattern)

**Trigger condition (cortex-computable, no LLM):** route query to Layer 0.5 iff entity-coverage-gap detected in Layer 0's top-K — hop-1 candidates fail to jointly cover the query's detected entity set. Otherwise Layer 0 alone is sufficient (per drill Prediction 3: graph-walk lift is regime-selective, ~zero on already-dense-solvable queries).

**Fallback (MDR-style, only if PPR mass degenerate/empty):** re-encode query ⊕ hop-1-passage-text with the dense frontend and re-query the flat index directly. This is the incomplete-KB fallback (PullNet rationale) since the substrate's KG is not Freebase-complete.

**Output:** UNION of {hop-1 dense candidates, hop-2 PPR candidates, MDR-fallback candidates} → **FEEDS INTO NEW LAYER 0.75, not directly into Layer 1** (per Exp 3 MB_INTERFACE_BOUND finding 2026-07-03).

### Layer 0.75: Query-aware candidate-set refinement (NEW REQUIREMENT; Exp 3 discovered 2026-07-03)

**Purpose:** reduce ~30 candidates from Layer 0.5 union down to ~2-5 clean candidates that composition (Layer 1) can consume without argmax noise cascade failure.

**Discovered because:** Exp 3 SMOKE 2026-07-03 measured:
- ORACLE (correct 2 chunks → composition): 0.822 F1
- MAIN (PPR union ~30 chunks → composition): 0.411 F1
- Composition primitive INTACT (ORACLE reproduces); PPR mechanism INTACT (Exp 2C 0.993 recovery replicates); INTERFACE between them fails.

**Skunkworks-verified mechanism attribution:** IMPLEMENTATION primary (missing primitive), STRUCTURAL secondary (FHRR CRLB rises 2.5× from K=5 to K=30 but doesn't explain full gap alone). Load-bearing gap = missing query-aware candidate-scoring primitive.

**Design candidates (external drills A/B/C in flight informing choice):**
- Reranker layer (cross-encoder, cosine-only for substrate-native)
- Hierarchical FHRR cleanup (per substrate's own 2026-06-10 research drill; never operationalized)
- Query-conditioned PPR-mass rescoring
- Diversity-aware MMR-style selection
- Learned candidate scoring (small primitive, no external LLM)

**Prereg gate for the primitive:** must lift Layer 0.5+0.75 composed pipeline MAIN to ≥0.90×ORACLE (~0.74) at same N_DIM=4096 regime. Deliverable = single primitive (Principle 11 compositional discipline) not full retrieval-pipeline rewrite.

**Related atoms filed 2026-07-03:**
- `substrate_exp3_composition_recovery_hub_bridge_INTERFACE_BOUND_MB_2026_07_03` (math)
- `META_RULE_composition_primitive_input_shape_contract_2026_07_03` MM_TENTATIVE_SYNTHESIS (meta) — FHRR composition input-shape contract

### Layer 1: Substrate VSA compositional query layer

**Purpose:** for STRUCTURED queries that dense retrieval alone can't handle. When the substrate operation has explicit role-filler structure (e.g., "atoms about storage-strategy under sharded composition"), substrate VSA compositional operations bind the query structure and match against atom-body content indexed with the same operations.

**Depends on VSA cells firing tonight:**
- Cell 3 multi-hop reasoning (validated compositional generalization at r@1=1.000 saturated)
- Tandem v2 explicit-compositional rerank (in flight; will tell us if substrate rerank on structured queries beats dense-alone at Wikipedia scale)
- RAG-with-substrate-composition (in flight; will tell us if substrate can compose answers from retrieved atoms)

### Layer 2: Cortex control (retrieval trigger + application)

**Purpose:** the substrate-native code that runs alongside every substrate operation and decides:
1. What atoms to query for (based on operation class)
2. How to interpret retrieved atoms (parse into constraint objects)
3. How to apply retrieved constraints (modify operation execution)

**Triggers (initial candidates):**
- **Storage-strategy trigger:** any operation involving bind/compose of ≥3 primitives → query storage-strategy law
- **Scale trigger:** operations at N ≥ 8192 → query scale-free law
- **Composition-depth trigger:** operations at chain depth ≥ 3 → query algebra-composition law
- **Topology trigger:** operations involving DAG composition → query topology-free law
- **Task-class trigger:** ambiguous operations → query task-class-fit META (VSA-native vs retrieval)
- **NEW: Entity-coverage-gap trigger (per drill):** query has detected entities not jointly covered by Layer 0's top-K candidates → route to Layer 0.5 (KG-walk retrieval) before Layer 1 composition. Gates on Wikipedia semantic-KB detour outcome for promotion beyond synthetic-scale mechanism proof.

**Constraint objects (deterministic):**
- Storage: SHARDED vs BUNDLED vs COMPOSED
- Sparsity: rate (0.02 default per current mechanism; may override per atom)
- Composition ordering: sequential vs parallel
- Readout: cosine vs modern-Hopfield (default cosine per Component C HF)
- Regime scoping: cluster_cos, corruption, K_DIST bounds

### Layer 3: Constraint application (operation modification)

**Purpose:** actually modifies the substrate operation execution per retrieved constraints.

**Implementation options:**
- **Decorator pattern:** wrap substrate primitives (`hdlab/binding.py::bind`, etc.) with a cortex-aware decorator that queries + applies constraints before execution
- **Middleware layer:** a `hdlab/cortex_middleware.py` module that intercepts operation calls and consults the atom store
- **Explicit invocation:** every substrate primitive call becomes `cortex.execute(op, args)` instead of `op(args)`

**Recommend decorator pattern** — least invasive to existing cells + backwards-compatible.

### Layer 4: Feedback (atomize back to KB)

**Purpose:** closed loop. When substrate discovers a new law or empirical bound, cortex atomizes it back to the KB via A5-gated write (same discipline Skunkworks used tonight).

**Trigger:** cell landing with CG_MEASURED_BOUND or CG_META-eligible finding → cortex fires atomization.

**NEW: Layer 0.5 feedback (per drill closed-loop discipline).** Every successful PPR-walk resolution (bridge chunk recovered + composition F1 hit) is itself atomizable as a MEASURED bridge-path fact. This directly compounds the KG's completeness over time — mitigates the incomplete-KB weakness flagged in PullNet precedent, which was the reason MDR-fallback was needed in Layer 0.5. Long-term: enough atomized bridge-paths reduce MDR-fallback rate, converging on graph-walk-only for the covered subgraph.

**Note:** this is what Skunkworks does now manually via VET. The cortex layer would automate this for straightforward atomizations (with Skunkworks retained as human-in-loop audit for CG_META promotions).

## Integration with tonight's cells + roadmap

**VSA-suite Cells 1-4** provide the primitive VSA operations for Layer 1:
- Analogy operations (Cell 1) → bind/unbind cascade for query-atom matching
- Compositional generalization (Cell 2) → novel role-filler binding for structured queries
- Multi-hop reasoning (Cell 3) → chain query for multi-hop atom retrieval
- Episodic binding (Spoke 3) → one-shot storage of new findings

**Tandem architecture cells (in flight):**
- v2 explicit-compositional rerank tests whether Layer 1 compositional query on top of bge-retrieved atoms beats bge-alone
- RAG-with-substrate-composition tests whether Layer 2 cortex control can compose answers from bge-retrieved chunks

## Empirical decision points (require cell data)

**Original (2026-07-02):**
1. ~~Does substrate compositional rerank on structured queries beat dense-encoder alone?~~ **RESOLVED 2026-07-03: tandem v2 MB_MECHANISM_RUNS_SMOKE_TIER (Skunkworks-demoted from cell-author HARD_PASS); hash-bag proxy + ground-truth structure pipe both ends invalidated the compositional claim.**
2. ~~Does substrate multi-hop composition over retrieved chunks beat naive concat?~~ **RESOLVED 2026-07-03: RAG-composition HARD_FAIL (0.083 tandem-RAG vs 0.783 ORACLE); composition works with correct chunks, retrieval is the bottleneck.**
3. ~~Is stella_en_1.5B_v5 meaningfully better than bge for dense retrieval frontend?~~ **DEFERRED per optimal-arch drill: encoder swap orthogonal to bridge-chunk recovery; upgrade for license/context-length only.**
4. **Foldiak-corrected DG preprocessing + hippocampus recover positive delta at cluster_cos ~0.9?** — RESOLVED 2026-07-03: HF_IMPLEMENTATION_COLLAPSE (representation collapse; not a mechanism-defect ruling — revival criterion in atom).

**NEW (2026-07-03 drill-informed):**
5. **Does PPR-walk over KGStore recover bridge chunks at semantic-KB scale?** — Wikipedia semantic-KB detour cell (dispatched 2026-07-03 afternoon; USES 5,510 Wikidata triples already at `data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl`; gates whole Layer 0.5 promotion path). HP≥0.50, HF<0.15, MIDDLE 0.15-0.50.
6. **Does composition recover to near-ORACLE=0.783 when fed PPR-recovered candidates?** — Exp 3, gated on #5 HARD_PASS; ≥90% of ORACLE = HP, <60% = HF, 60-90% = MIDDLE.
7. **Does Layer 0.5 lift replicate at 170K-atom Director-KB scale?** — scale re-test after #5 + #6 satisfy; revival criterion in Exp 1 + Exp 2 atoms.

Each of these has direct implications for Layer 0.5 design and downstream cortex trigger conditions.

## Non-negotiables

- Cortex layer MUST be substrate-native — no external LLM in the cortex control loop (USER-locked substrate-native language directive)
- Dense retrieval frontend (Layer 0) CAN use bge/stella per USER clarification (2026-07-03: bge NEVER in substrate ITSELF, but non-brain-analog encoder at sensory-input layer is OK)
- All cortex-driven operations MUST be atomizable back to the KB — closed-loop discipline
- CG_META atoms cannot be silently overwritten — Skunkworks A5-gate discipline preserved
- Cortex layer failures must be honest — if cortex can't find a relevant constraint, operation proceeds with default (recorded as a MEASURED bound for future cortex training)

## Stage 1 findings that become ACTIVE via cortex

Currently documented in atom store; would become ACTIVE constraints:
1. **Storage-strategy law:** cortex forces SHARDED when detecting composition-depth ≥ 3 + N ≥ 8192
2. **Scale-free law:** cortex allows N ≥ 16384 operations without secondary sanity checks (law says they scale)
3. **Topology-free law:** cortex allows arbitrary DAG topology without regime-specific overrides
4. **Algebra-composition law:** cortex allows 5-step primitive chains without capacity anxiety (law says algebra scales)
5. **Task-class-fit META:** cortex routes retrieval-task queries to dense-frontend; VSA-native queries to substrate direct

## What's left before this is buildable

**Pre-M3 blockers (REVISED 2026-07-03):**
1. ~~Encoder decision for Director-KB~~ **DEFERRED per drill: encoder is not the bottleneck; upgrade orthogonal to Layer 0.5.**
2. **NEW: Wikipedia semantic-KB detour outcome (in flight)** — gates Layer 0.5 promotion path. If HP → proceed to #3; if HF → revive encoder path as primary.
3. **NEW: Exp 3 composition-recovery vs ORACLE=0.783** — gated on #2 HP; confirms retrieval-completeness (not composition) was sole bottleneck.
4. **NEW: 170K-atom scale re-test** — Exp 1 + Exp 2 revival criteria; before production wiring.
5. Cortex middleware skeleton — code-only, no cell dispatch needed (can start in parallel with #2)

**Post-blocker Cell dispatches:**
1. Layer 0.5 KG-walk implementation cell — PPR + entity-extraction wired to KGStore + CharTrigramEncoder, tested against Wikidata triples at production scale
2. Cortex layer skeleton cell — apply storage-strategy law to a test operation (unchanged from original)
3. End-to-end integration cell — substrate does new composition, cortex queries + applies storage-strategy law + operation succeeds (unchanged)
4. Stage 1 findings active-verification cell — measure that cortex actually retrieves and applies the law (unchanged)
5. **NEW: Layer 0.5 closed-loop atomization cell** — verify successful bridge-path resolutions atomize back to KB (compounding KG completeness)

## Priority order per USER strategic vision

1. Substrate operates off Stage 1 findings (this design)
2. Self-improvement portal (USER strategic vision; cortex layer enables closed-loop substrate improvement)
3. Core mathematics work (USER strategic vision; cortex-driven math operations)
4. M3 conversational agent (uses cortex layer to reason over retrieved KB)
5. M4/M5 agentic loops (cortex-mediated action + memory)

## Open design questions

1. **Cortex query language:** structured (explicit role-filler bindings) or NL-parsed? Recommend structured for interpretability + efficiency.
2. **Constraint conflict resolution:** what happens when 2 retrieved atoms contradict? Recommend Skunkworks-audit for CG_META atoms; latest-wins for MM atoms.
3. **Caching:** should cortex cache retrieved constraints for repeat operations? Recommend yes with cache-invalidation on KB write.
4. **Failure mode:** cortex retrieval fails to find any atom — should operation proceed with defaults or block? Recommend proceed + record MEASURED bound for training future retrieval.
5. **Cross-session state:** does cortex learn across sessions or is it stateless? Recommend stateless per-session but atomization-driven cumulative KB improvement.

## Next steps (post-cell-landings) — REVISED 2026-07-03

1. **Wikipedia semantic-KB PPR detour** (in flight) — decision-point experiment for whole Layer 0.5 path
2. **If detour HP:** dispatch Exp 3 composition-recovery vs ORACLE — confirms composition wasn't the bottleneck
3. **If detour + Exp 3 both HP:** 170K-atom scale re-test (revival criterion) before production wiring
4. **If detour HF:** **NO AUTO-PIVOT.** Deep-dive mechanism-attribution FIRST — was HF structural (PPR mechanism dead at real-KB scale), implementation (α, iteration count, seeding wrong), infrastructure (Wikidata triples too sparse / typed relations wrong shape for target query class), or scope (test set didn't cover intended regime). Skunkworks-verify diagnosis. Only if STRUCTURAL is confirmed → consider encoder-swap fallback. Implementation/scope failures → iterate PPR with fix, do NOT abandon.
5. **Regardless of detour outcome:** author cortex middleware skeleton (`hdlab/cortex_middleware.py`) — decision-independent; enables Layers 2-4 in parallel with retrieval-layer decision
6. **Post-Layer-0.5 lock:** author cortex integration test cell exercising all 5 (or 6 including 0.5) layers end-to-end
7. **Stage 1 findings active-verification cell** — measure cortex actually retrieves and applies the law; final gate before this design is buildable

## Materially updated preconditions (filesystem-verified 2026-07-03)

- **Wikidata triples on disk (2026-06-14 ingest):** 5,510 relations at `data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl` — semantic KG ready for Layer 0.5 PPR without new ingest
- **Wikidata atoms already in substrate_index/math/atoms.jsonl:** 5,376 atoms mapped from wikidata via `mapper_v2_adapter` — production-scale semantic-KG lane exists
- **Wikipedia atoms in substrate_index/math:** 17 (my earlier assumption "Wikipedia FULL 10K subgraph we already have" in Wikipedia-KG-build dispatches was NOT filesystem-verified — Fix#28 pattern; corrected mid-flight to detour agent via SendMessage)
- **KGStore + CharTrigramEncoder composition** already lives in `hdlab/director_kb.py::737` — the substrate's OWN Director-KB is already a knowledge graph, not just an atom index (drill KEY REFRAME)
