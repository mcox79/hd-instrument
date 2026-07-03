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

## Architecture (staged)

### Layer 0: Sensory input (retrieval frontend)

**Current:** Director-KB uses `CharTrigramEncoder` for atom-name indexing. Limited retrieval quality for atom-body content queries.

**Target (per USER tandem architecture clarification):** dual-index atom store:
- **char-trigram index** for exact entity-name lookup (cheap, deterministic, works for known-atom-name queries — e.g., "get the storage-strategy CG_META atom by anchor")
- **Dense encoder index (bge or stella_en_1.5B_v5)** for content-similarity queries (e.g., "find all atoms about capacity limits" — semantic query over atom bodies)
- Hybrid ranking (RRF or weighted sum) for queries that could be either

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

1. **Does substrate compositional rerank on structured queries beat dense-encoder alone?** — v2 explicit-compositional cell (ae88f4634610572bc)
2. **Does substrate multi-hop composition over retrieved chunks beat naive concat?** — RAG-composition cell (aee9ea879e4ce6698)
3. **Is stella_en_1.5B_v5 meaningfully better than bge for dense retrieval frontend?** — encoder bake-off (proposed; gated on chunking question)
4. **Do Foldiak-corrected DG preprocessing + hippocampus recover positive delta at cluster_cos ~0.9?** — Foldiak cell (a00691ec67e4e7c73; expected HF given implementation collapse)

Each of these has direct implications for Layer 0-2 design.

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

**Pre-M3 blockers:**
1. Encoder decision for Director-KB (dense frontend + char-trigram hybrid) — gated on tandem cell results
2. Re-index atom store with locked encoder — operational (few hours)
3. Cortex middleware skeleton — code-only, no cell dispatch needed

**Post-blocker Cell dispatches:**
1. Cortex layer skeleton cell — apply storage-strategy law to a test operation
2. End-to-end integration cell — substrate does new composition, cortex queries + applies storage-strategy law + operation succeeds
3. Stage 1 findings active-verification cell — measure that cortex actually retrieves and applies the law

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

## Next steps (post-cell-landings)

1. Wait for RAG-with-substrate-composition cell (aee9ea879e4ce6698) — informs Layer 1/2 design
2. Answer chunking question for Wikipedia ingest (already answered: not the bottleneck)
3. Decide dense retrieval frontend encoder (bge, chunking-fixed, or stella_en_1.5B_v5)
4. Re-index atom store with locked encoder
5. Author cortex middleware skeleton (`hdlab/cortex_middleware.py`)
6. Author cortex integration test cell
7. Verify Stage 1 laws actively applied via measurement
