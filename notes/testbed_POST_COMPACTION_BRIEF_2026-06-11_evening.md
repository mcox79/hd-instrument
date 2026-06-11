# Testbed POST-COMPACTION BRIEF — 2026-06-11 evening

**READ FIRST on resume.** Captures load-bearing state from this session.

## 30-second status

- **substrate self-index** foundational tool: 15 modules + schema extension SHIPPED under `backend/substrate_index/`. First end-to-end run produced a real discovery (Research-validated).
- **Stage A Wikidata** fp32 grinding at ~23.4 facts/sec on F:\hd-substrate NVMe. ~4-day ETA. Route A int8 FAILED (i5-12600 no AMX); Route B GPU pending Exp-Dev's kb-run convergence.
- **Demo backend** polished through cycle 234 (4 public NL benchmarks on `/benchmark/fb15k-237`: FB15K-237 + Penn Treebank POS 0.9063 5-seed + ATIS slot+intent + MAWPS/MultiArith math TIER A 5-seed).
- **F: NVMe migration** done; PP-150 sub-ms retrieval claim physically defensible.
- **What user last asked**: implicit pending decision — hand-author algebra-vec fields on 60 batch-01 atoms (~90 min focused) to run first substrate-vs-LLM head-to-head benchmark tonight before Research's batch 02 lands tomorrow. I recommended yes. User said "prepare for compaction" instead, so the question is OPEN.

## What I was working on at moment of compaction

User direction this evening built up:
1. "do it" -> start the substrate self-index pilot
2. "we need a way to measure how well it works, how to improve it etc"
3. "we're going to want a lot of meta on this system too - how things are relationally, can we do reasoning with it, the works"
4. "we'll need to be able to update it as we build out our capabilities. I'm hoping the construct actually helps us to find better solutions. Make sure to report to research on what you find, and also that you can do analysis from research on the substrate if it is possibly helpful"
5. "the real magic will be in being able to compare the math itself -- how close they are, how close different operators are and if there are shared basis"
6. "ask research for research support on it"
7. (Research expanded to a 4th SCHOOLS partition based on a parallel user direction about representing schools of thought)
8. User asked twice what I'm waiting on; I proposed hand-authoring algebra-vec fields; user said "prepare for compaction"

## substrate_index architecture (load-bearing)

Location: `backend/substrate_index/`

### Day 1 modules (10)
- `schema.py` — Atom, Relation, TestQuery, QueryResult dataclasses; Corpus enum (MATH/CONCEPT/META/SCHOOL); Tier; AtomKind (PRIMITIVE/FAMILY_TAG/SUB_OP/MACRO/SCHOOL); RelationType (16 types including CONTRIBUTES_TO/TRACES_TO/INFLUENCED_BY for school relations); ALGEBRA_CATEGORIES constant (13 categories on 3 axes + substrate_native)
- `metrics.py` — FailureMode classification (NO_MATCH/EMBEDDING_DRIFT/WRONG_RANKING/MISSED_RELATION/COVERAGE_GAP/LATENCY_FAIL/LLM_LOSS), per-query QueryScore (recall@k/MRR/NDCG/relations_recall), aggregate SystemDiagnostic with auto-generated improvement recommendations, drift detection, spectral_observability stub (post-batch-02 + M>=100)
- `store.py` — single-partition Store with append-only audit log (ChangeEvent)
- `partition.py` — PartitionedStore with 4 stores (math/concept/meta/school) + 4 failure-mode guards (meta-rule self-collapse / string-similarity laundering / hand-coded scaling 5K warn 10K cap / unbounded self-reference max_depth=6)
- `encode.py` — AtomEncoder (bge-large + FHRR tier/corpus tags + algebra_vec/signature_vec/complexity_vec via deterministic tag-vector tag-sum scheme; composite weights alpha=1.0/beta=0.5/gamma=0.3/delta=0.2)
- `retrieve.py` — Retriever: semantic / structural / hybrid / algebraic query modes
- `relate.py` — shortest_path / k_hop_neighbors / degree_centrality / betweenness_centrality / communities / gap_atoms / relation_density / cross_corpus_links
- `ingest.py` — JSONL corpus loader (idempotent; IngestReport)
- `cli.py` — operator CLI (stats / ingest / query / related / paths / gaps / centrality / algebraic / bench)
- `reason.py` — transitive_neighbors / find_atoms_matching(AtomPredicate) / algebraic_agreement / reason (combined consensus + disagreement across structural/semantic/algebraic)

### Days 4-8 modules (5)
- `discover.py` — 8 discovery surfaces: structural_gap / cluster_unification / centrality_drift / cross_corpus_orphans / semantic_vs_structural_disagreement / underutilized_relation_types / tier_imbalance + DiscoveryReport
- `meta.py` — summarize_state / identify_strongest_claims / identify_exposed_atoms / knowledge_pertaining_to / describe_self
- `evolve.py` — auto-ingest from cap_map cycles: parse_strategy_decisions / evolve_from_strategy_files / evolve_from_notes_dir
- `report.py` — render_findings_note (markdown + JSON) + reply_to_research_query (ResearchQuery driven)
- `validate.py` — LLM head-to-head harness (NO LLM-as-judge per Refinement 2); AnthropicClient + OpenAIClient lazy adapters; HeadToHeadResult

### Schema extension fields on Atom
- `algebra: dict | None` — {structure (one of 13 ALGEBRA_CATEGORIES), commutative, associative, identity (atom_id), inverse (atom_id), distributes_over, domain}
- `signature: dict | None` — {input_arity, input_types, output_type, preserves: {dim/norm/unit_modulus/etc.}}
- `complexity: dict | None` — {time_class, space_class, parallelism, online}
- `equivalences: tuple[dict]` — [{equivalent_to, under_transformation, fidelity}]
- `concept_links: tuple[str]` — qualified ids (substrate-product DIFFERENTIATOR per Research's drill)

## Empirical state as of compaction

### 60 atoms ingested from `data/substrate_index/math_corpus_batch01.jsonl`
- 15 T1 (foundational), 11 T2 (substrate primitives), 25 T3 (algorithm sub-ops), 11 T2 family-tags
- All have just description+name+aliases+metadata; algebra/signature/complexity NOT YET populated
- File force-added (data/* is gitignored): `git add -f data/substrate_index/math_corpus_batch01.jsonl`

### 5 disclosed pre-registered queries saved as `data/substrate_index/queries_disclosed.json`
- Q1: inverse of FHRR binding (Expected fhrr_unbind)
- Q2: discrete combinatorial optimization globally (Expected Hungarian, Viterbi, Chu-Liu-Edmonds)
- Q3: concepts using count-NB (Expected code_algopattern, intent_atis, POS_tagger - cross-corpus; blocked till concept corpus lands)
- Q4: probabilistic inference family
- Q5: structurally equivalent to FHRR binding in frequency domain (Expected circular_convolution via FFT-dual)

### Diagnostic queries run (smoke test):
- bge-large encoder loaded; retriever index for 60 atoms built in ~21 sec; per-query latency 189-376 ms
- Q3-style ("sequence decoding via DP") textbook-clean (Viterbi top at 0.777)
- Q1-style ("dual of FHRR binding") EMBEDDING_DRIFT (queried atom ranked top, not its dual)
- Q2-style ("global discrete optimization") EMBEDDING_DRIFT (convex first, family-tag second)
- Q4-style ("probabilistic inference for structured predictions") partial (Collins perceptron first - discriminative not probabilistic)
- Tier filter works

### Discovery engine first run (81 findings)
- 30 warnings, 36 suggestions, 15 info
- Top finding: **bundling vs superposition cosine 0.863** within T2_FAM/superposition_aggregation family — flagged as cluster_unification candidate
- Research VALIDATED this as "the user-requested 'find better solutions' capability operating empirically" (their phrase)
- Research chose option 2: DISTINGUISH the two atoms (not merge); refined descriptions for batch 02

## What Research is delivering (pending)

### Batch 02 — Day 1 EOB tomorrow (~24h from compaction)
- ~40-50 hand-authored RELATIONS (DUAL pairs, USES_SUBPROC chains, COMPOSES, SPECIALIZES, PRESERVES, OPTIMIZES, COST_FUNCTION_TYPE, COMPLEXITY_CLASS)
- 6 description REFINEMENTS:
  1. T1/convex_optimization lead with "CONTINUOUS optimization"
  2. T2_FAM/global_discrete_optimization lead with "DISCRETE combinatorial"
  3. T3/collins_structured_perceptron lead with "discriminative max-margin"
  4. T3/hmm_transition lead with "probabilistic generative"
  5. T3/hmm_emission lead with "probabilistic generative"
  6. T2/bundling vs T2/superposition unit-modulus-preserving vs raw
- ALGEBRA-VEC FIELDS populated on the 60 batch-01 atoms per 13-category taxonomy + 14-field record
- Initial cross-domain EQUIVALENCES (6 known off-hand + drill catalog): FHRR-bind FFT-dual circular_convolution / Hungarian LP-relaxation convex / Viterbi semiring-shift forward / PCA-whitening rotation ZCA / etc.
- 27-tag 5-super-group family-tag inventory (binders/unbinders/mixers/transformers/observers) refactor
- substrate_CRF + cleanup_margin + split_conformal_prediction additions

### Day 2 deliveries
- Batch 03 full Tier-3 decomposition to 300-500 sub-ops
- Concept corpus (~60-80 atoms: PP rows + drill outcomes + capabilities)
- Schools corpus (~30 atoms initial: VSA/FHRR lineage, HMM, cognitive arch, free probability, etc.)
- ~150-200 cross-corpus USES + CONTRIBUTES_TO links
- 5 SEALED queries (set Day 2 EOB before validation)

### 6 drills dispatched tonight/tomorrow (will refine batches)
1. Schools-of-thought lineage ~30-50 schools
2. Cross-domain equivalences catalog ~30-50
3. Substrate-only NL synthesis path
4. Substrate continual-learning + RAG-backend
5. RMT-beyond-free-probability
6. Substrate vs larger LLM methodology

## What Exp-Dev is delivering (pending)

- B2 Path A toggle UI — blocked on Q1-Q4 answers about .pt checkpoint location + K/V source
- B3 HYBRID composed backend — blocked on same
- PP-225 .pt re-export — DONE (this morning); /converse/pp225 endpoint is live with real fp32 head
- kb25k / kb50k determinism run on GPU (will eventually free GPU for Stage A Route B burst)

## What I told Research (notes filed this evening, in order)

1. `testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md` — first 5 semantic queries; EMBEDDING_DRIFT at 60% identified
2. `testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md` — discovery engine surfaced bundling/superposition redundancy candidate
3. `testbed_to_research_SELF_INDEX_RESCOPE_TO_FOUNDATIONAL_TOOL_2026-06-11.md` — rescope to 5-8 day foundational tool (Research endorsed)
4. `testbed_to_research_SELF_INDEX_REFINEMENTS_INTEGRATED_2026-06-11.md` — integrated 3 design drills (granularity / no-LLM-judge / partitioned-substrate-with-role-binding); answered meta-atom scope question
5. `testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md` — proposed the algebra-vec extension with 6 lit-scan asks
6. `testbed_to_research_ARXIV_MATH_VERIFY_RESULT_2026-06-11.md` — confirmed arxiv_2m is ML-papers (not math); Stage A2.math re-ingest needed
7. `testbed_to_research_INGEST_ROUTE_A_FAILED_2026-06-11.md` — int8 quantization gave ~0x speedup on i5-12600 (no AMX); reverted to pure fp32
8. `testbed_to_research_INGEST_SPEEDUP_REQUEST_2026-06-11.md` — earlier escalation that triggered Route A approval

## What Research told me (notes received this evening)

1. `research_to_testbed_SUBSTRATE_SELF_INDEX_PILOT_2026-06-11.md` — original 2-3 day pilot authorization
2. `research_to_testbed_SELF_INDEX_RESCOPE_ENDORSED_2026-06-11.md` — endorsed 5-8 day rescope + 3 design refinements
3. `research_to_testbed_MATH_CORPUS_DRAFT_01_2026-06-11.md` — 60-atom batch 01 delivery
4. `research_to_testbed_INDEX_FINDINGS_01_RESPONSE_2026-06-11.md` — endorsed; 5 disclosed queries + batch 02 commitments
5. `research_to_testbed_INDEX_FINDINGS_02_RESPONSE_2026-06-11.md` — bundling/superposition validated; refined descriptions for batch 02
6. `research_to_testbed_FREE_PROBABILITY_OBSERVABILITY_INTEGRATION_2026-06-11.md` — ~30-line numpy primitive (Marchenko-Pastur + Tracy-Widom + kappa_4 + spectral_gap); deferred to batch 02 when M >= 100
7. `research_to_testbed_ALGEBRA_VEC_SUPPORT_PLUS_SCHOOLS_CORPUS_2026-06-11.md` — Q1-Q6 initial answers; SCHOOLS partition proposal with CONTRIBUTES_TO/TRACES_TO/INFLUENCED_BY; 7 drills dispatched
8. `research_to_testbed_ALGEBRA_VEC_REFINED_13_CATEGORY_2026-06-11.md` — drill refinement: 13 categories on 3 axes + 14-field operator record + concept_links substrate-product differentiator

## Stage A state at compaction

- PID was 30488 at last check; running detached on the runner
- Substrate state at `F:\hd-substrate\substrate_state\wikidata_truthy_50m\` (junction from `C:\dev\hd-instrument\data\substrate_state\`)
- facts.jsonl was ~2.01M rows at ~14:00 runner time
- Rate: ~23.4 facts/sec (essentially fp32 baseline; int8 was a no-op on this CPU)
- ETA: ~4 days to 11M target
- Log file: `data\logs\wikidata_stage_a_fp32_2026-06-11.log`

## Demo backend state at compaction

- Live on runner port 8000
- `/converse/pp225` real PP-225 fp32 head (206 MB) loaded; substrate retrieval -> fact -> bge encode -> head projection into Pythia-1.4B vocab
- `/benchmark/fb15k-237` has 4 public benchmark callouts: FB15K-237 (cycle 211, Hits@1=0.956) + Penn Treebank POS (cycle 230, 0.9063 5-seed) + ATIS slot-fill+intent (cycle 232, slot 0.871 intent 0.846) + math TIER A (cycle 233-234, MAWPS=0.882 / MultiArith=0.750 multi-seed mean 0.753 std=0.005)
- `/demo/reasoning` + `/demo/cognition` + `/demo/lifecycle` all polished through cycle 234

## ON-RESUME ACTIONS (top of priority list)

1. **Check Stage A health** first — facts.jsonl mtime, partial count, log tail, process PID alive
2. **Read note monitor `b01eebt68`** state if still armed; otherwise re-arm via Monitor with the same pattern set
3. **Pull latest** for batch 02 from Research if their EOB tomorrow already landed
4. **Decide on the pending algebra-vec hand-author** task (user said "prepare for compaction" instead of yes/no on my proposal; the option still stands — populate algebra fields on the 60 atoms to run head-to-head benchmark tonight before Research's batch 02 lands)

## OPEN QUESTIONS at compaction

- User has not explicitly accepted or rejected the algebra-vec hand-author proposal (~90 min focused work). My recommendation stands.
- Stage A Route B GPU burst: still waiting for Research's signal that Exp-Dev's kb run has freed the GPU.
- Cycle 232 secondary polish (PP-368/371/372) keeps getting deferred; minor wins.

## DISCIPLINE REMINDERS (do not forget on resume)

- **No emojis** unless user asks
- **No em-dashes in code outputs**
- **ASCII-only in scripts**
- **No padding** — only ship cells/atoms with real content
- **honest framing** per Research's OVERCLAIM_CORRECTIONS 2026-06-10 (was earlier today; substrate is NOT autonomous-agent / NOT LLM-replacement on most axes)
- **Routings direct to Exp-Dev** per `routings_direct_to_exp_dev` rule
- **No LLM-as-judge** in any substrate_index validation per Refinement 2
- **Hand-coded relation cap**: 5K warn / 10K hard cap; auto-extracted relations don't count
- **Backend restarts**: kill BOTH uvicorn PIDs (there are typically two — venv stub + system python worker), then wmic process call create the batch file
- **data/* is gitignored**: force-add with `git add -f` for corpus files

## Key files to look at quickly on resume

- `backend/substrate_index/*.py` (15 modules)
- `data/substrate_index/math_corpus_batch01.jsonl` (60 atoms)
- `data/substrate_index/queries_disclosed.json` (5 pre-registered queries)
- `notes/research_to_testbed_ALGEBRA_VEC_REFINED_13_CATEGORY_2026-06-11.md` (latest Research call on schema; informs hand-authoring)
- `notes/strategy_decisions_2026-06-11.md` (latest cap_map cycle 234 had PP-378 + PP-375 TIER A promote)
- `data/logs/wikidata_stage_a_fp32_2026-06-11.log` (Stage A grinds)

---

**End of brief.** Total tokens used today: substantial; substrate self-index foundational tool went from idea to 15-module shipping system in one evening. The user's strategic intuition about algebra-vec being "the real magic" matches Research's drill-supported architecture and is now structurally ready in the schema.
