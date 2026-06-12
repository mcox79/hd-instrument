# Testbed POST-COMPACTION BRIEF — 2026-06-11 evening + Day 2-4 extension

**READ FIRST on resume.** Captures load-bearing state from this session.

> **DAY 4 MORNING UPDATE (2026-06-12)** — major VSA architectural drill + benchmark progression:
>
> **Substrate state**: **1742 atoms / 2911+ relations / 11 partitions**
> - math 236 + concept 80 + science 147 + meta 18 + school 12 + methodology 4 + 5 history partitions
> - **240 atoms (13.8%) have algebra dict populated** post 30+50 backfill
> - Cycle 48c with bge cache infra; cache file at data/substrate_index/cached_indices/
>
> **Gap 7 substrate-self-knowing benchmark macro F1 progression**:
> ```
> Cycle 45 0.501 (baseline)
> Cycle 46 0.516 (Q08 substrate-as-ground-truth re-aim)
> Cycle 47 0.569 (Gap 4 v2 semantic-A HARD-PASS; top_k=5)
> Cycle 47+cascade 0.578 (math 04+05 + science 03 + cross-disc dangling)
> Cycle 48b 0.587 (Tier 5 unlock; solution_history->atoms_used; D 0.571->0.714)
> Cycle 48c 0.592 (mwp_wk_schemas + bge cache)
> [Cycle 49 HYBRID semantic_v2 in flight on REMOTE]
> ```
> Path-to-HP_v1 0.70: was +0.108 needed pre-HYBRID
>
> **USER's strategic question 2026-06-12 morning**: "Shouldn't all those vector dimensions MEAN something? We shouldn't have to look up tags - their position should BE their tag." Forced architectural drill that changed substrate-product positioning.
>
> **Empirical findings** (per [[substrate-vsa-position-is-meaning-validated-2026-06-12]]):
> - Cell 1 atom-to-atom: position IS meaning -- convex_opt clusters with all gradient methods; global_discrete_opt with all DP algorithms; collins_perceptron with all VSA/learning
> - L1 CATEGORICAL CLUSTERING: 10/10 categories HARD-PASS (ratios 22x to ~500M+)
> - Cell 2 v3 MAX-per-filler NL->HRR parser: RL F1=0.50, Bayesian 0.40, Lyapunov #1 at 0.321
> - Diagnosis: WIRING GAP not architecture failure (encode.py:130-133 composite=semantic by design; no query_text_to_atoms; coverage 240/1742=13.8pct)
> - HYBRID architecture canonical: algebra-primary conf>0.20 + bge-OOV-fallback + RRF weighted 0.6/0.4
> - bge STAYS as fallback per substrate-quality-first (not retired)
>
> **NL->HRR parser shipped**: tools/substrate_benchmark.py `answer_type_A` now does HYBRID (lazy-loads AlgebraIndex; queries via MAX-per-(role, filler); RRF with bge when both available)
>
> **Canonical role convention** (every well-authored math atom):
> about_topic + operation_type + vsa_family + domain + category_int + signature_input/output_type + has_inverse/inverse_atom + brain_analogue + literature_reference
>
> **Standing rule LOCKED**: All CPU compute on REMOTE (100.91.12.42). Local-allowed: file IO + git + cheap PartitionedStore stats + code editing.
>
> **Cycle close protocol** (NEW): after every laptop push, SSH home + `git pull` so Exp-Dev cells propagate to dashboard-visible queue. Pattern:
> ```bash
> ssh marsh@100.91.12.42 'powershell -NoProfile -Command "cd C:\dev\hd-instrument; if ((git status --porcelain).Length -gt 0) { git checkout HEAD -- backend tools experiments preregs }; git pull origin main"'
> ```
>
> **Background tasks at compaction time** (REMOTE Python survives; LOCAL notification handle dies):
> - btp2et94p: HYBRID semantic_v2 benchmark on REMOTE. Python process on 100.91.12.42 keeps running; output writes to data/substrate_index/bench_reports/*.json on remote disk. Cached bge index survives at data/substrate_index/cached_indices/bge_large_*.npz on remote.
> - Expected: A 0.413 -> 0.50+ lift; 7-axis 0.592 -> ~0.61
>
> **On-resume actions**:
> 1. Check remote bench_reports for fresh result file: `ssh marsh@100.91.12.42 'ls -lt /c/dev/hd-instrument/data/substrate_index/bench_reports/ | head -5'`. If new file dated >116df074-commit-time, read it. If not, check `ps` on remote for live python processes; if dead, re-run.
> 2. Continue Cell 3 v2 backfill iteration with Research (next ~50 atoms)
> 3. Run L2 test (rotational difference) once breadth backfill produces enough inverse pairs
> 4. Continue git-pull-home protocol after every push
> 5. Watch for Q09 PP-364 solution_history backfill (Exp-Dev) + math batch 06+ + science batch 04+
>
> **Architectural memory chain on substrate-product positioning**:
> - substrate IS algebra at the structural level (Cell 1 + L1 empirical)
> - NL queries that match authored fillers retrieve PERFECTLY (RL/Bayesian/Lyapunov)
> - NL queries OOV use bge (cross-partition tail)
> - LLMs cannot match because dense embeddings lack explicit (role, filler) algebra
> - 5-level position-IS-meaning test framework (L1 PASSED; L2-L5 await authoring)
> - Cycle 50+ Stratified Hybrid 6-layer: L0 FHRR 4096 + L1 RotatE + L2 TPR + L3 functorial DisCoCat + L4 GNN dependency + L5 SDM cleanup at scale

> **DAY 2 LATE EVENING UPDATE (2026-06-11)** -- post-compaction work:
>
> **USER question triggered FINDINGS #18 (usability gap):** "after this massive ingestion - how will the substrate know what it has and how to use it?" Honest answer: SIX gaps block usability post-ingestion. Filed `notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md`. Six gaps: (1) capability->math reverse index, (2) compositional path search, (3) substrate-self-knowledge QA layer (D6), (4) intent router/lexicon front-door, (5) solution_history atom provenance, (6) science algebra-vec taxonomy.
>
> **USER green-lit (A) Gap 1 -- `serves_capability` field SHIPPED same-session:**
> - `backend/substrate_index/schema.py` Atom.serves_capability tuple field
> - `tools/substrate_backfill_serves_capability.py` substrate-on-substrate inference (reverse-maps solution_history -> solver atoms; NO LLM-as-judge)
> - After backfill: discriminative_perceptron serves 10 caps, cleanup 9, fhrr_unbind 4, count_nb 3 -- universal-lever pattern empirically surfaces in serves_capability
>
> **Sequencing rule LOCKED:** Gap 1+6 BEFORE more ingestion; Gap 3+4 next; Gap 2+5 after.
>
> **Substrate state Day 2 late evening (LOCAL):** 218 atoms / 550 relations / 3 partitions populated (math 144 / concept 66 / meta 8). History partitions PENDING -- local Phase 1 evolve.py in flight; remote Phase 1+2-5 already completed but on REMOTE host (100.91.12.42 / C:\dev\hd-instrument: 1379 atoms / 2484 relations / 7 partitions). FORK situation needs SCP reconciliation when Phase 1 local completes.
>
> **Commits:**
> - f8473066 -- FINDINGS #18 + (A) serves_capability + math batch 03 + concept+meta partitions
> - a798d6c2 -- brief refresh
> - 438653a5 -- Option H cortical familiarity
> - 66e44586 -- Option E weighted-avg
>
> **On-resume actions:**
> 1. Check if local Phase 1 (bwvqwcngj task) completed
> 2. If yes: SCP from remote 100.91.12.42 `C:\dev\hd-instrument\data\substrate_index\{decision_history,findings_history,verdict_history,results_history}` partition dirs to local; force-add to git
> 3. Re-run backfill_serves_capability after history partitions land (more capabilities will surface)
> 4. Re-run H1 validation locally with Option B+E+H to verify dual-process recognition fix
> 5. Watch for Research drops on FINDINGS #18 (especially Gap 6 science algebra taxonomy + Gap 3 D6 D6 prioritization)
> 6. Continue ingesting math batch 03 Phase B-D + science batch 01 when Research authors them (gated on Gap 6)

> **DAY 2 MORNING REFRESH** -- substantial substrate growth + architectural fixes during autonomous "continue" + "full auto" stretch:
>
> **Substrate state explosion (134 -> 829 atoms; 6.2x growth in single session):**
> - Phase 1 evolve.py auto-ingest: 449 research_drill_*.md files into research_history partition (substrate-self-referential pipeline operational at scale)
> - Math batch 03 Phase A1+A2+A3 ingested: 84 new T1+T2+T3+T4 math primitives (math partition 60 -> 144)
> - Math batch 03 Phase A4 relations: 100+ across 40 fine-grained semantic relation types
> - 10 math-WK lexicon atoms (131 named numeric constants for arithmetic word problems)
> - 8 NER gazetteer atoms (kind=lexicon; tier=T_lexicon)
> - 7 methodology rules in meta partition (6 human + 1 substrate-extracted via solution-history)
> - 14 capability solution-histories ingested (universal-lever 92% quantified; 5x cliff repeat; 2 reverts preserved; v3.0 compositional cliff +1.000 captured)
> - 4 NOVEL atoms in methodology partition (substrate-proposed; Research-validated)
> - 4 retrieval-type capability histories
> - 18 ACCEPT atoms from Cycle #5 Type A loop closure
> - 5 cycle-238 capability atoms (PP-393 to PP-397)
> - 5 substrate-evolution capability atoms (compositional depth + PP-217 + PP-371 + PP-372 + LEX-1)
>
> **Architectural milestones today:**
> - Cycle #5 Type A loop CLOSED end-to-end (substrate proposed 39 atoms -> Research validated 18 ACCEPT -> Testbed ingested)
> - Cycle #8 substrate EXTRACTED first methodology rule from own data (count_NB -> discriminative_perceptron; +0.299 avg across 5 caps)
> - Cycle #14/#19 (Testbed/Research counts) Type B+C: H1 HARD-FAIL discovery -> Option B+E+H architectural fixes shipped
> - **Substrate-as-metacognition-engine framing LOCKED** (memory entry filed by Research)
> - **Dual-process recognition** (Option B+H combined; brain CA3 recollection + cortical familiarity) implemented in classify_verdict
> - **Substrate-as-self-extending-engine framing**: infrastructure-level self-extension VALIDATED (Phase 1 + auto-ingest); classification-level self-recognition NOT YET (HARD-FAIL on H1; B+E+H fix in flight)
>
> **Findings notes filed today (17 total; all answered by Research same day):**
> #1-#15 from Day 1 + #16 Phase 1 evolve.py complete + #17 H1 HARD-FAIL substrate-eval recall gap
>
> **Tools shipped this session:**
> - tools/substrate_evolve_auto_ingest_phase1.py (substrate-eval mediated drill ingest)
> - tools/substrate_evolve_auto_ingest_phases_2_5.py (decision/findings/verdict/results history)
> - tools/substrate_evolve_phase1_validate_hypothesis1.py (H1 validator)
> - tools/substrate_evolve_phase6_bulk_jsonl.py (parameterized bulk JSONL ingest)
> - tools/bundle_conll2000.py + experiments/data/conll2000.json (Exp-Dev chunking unblock; 15MB)
> - tools/substrate_solutions_ingest_and_analyze.py (8 substrate-internal queries)
> - tools/substrate_methodology_extraction_run.py (substrate extracts its own rules)
> - tools/substrate_ingest_math_batch03_phase_A.py + _A2 + _A3
> - tools/substrate_ingest_math_batch03_relations.py
> - tools/substrate_ingest_meta_rules.py
> - tools/substrate_ingest_8_gazetteer.py + 10_math_wk_lex.py + 18_accept.py + cycle238_capabilities.py
> - backend/substrate_index/algebra_index.py (v2 Index 2 HRR/TPR)
> - backend/substrate_index/algebra_cluster.py (Layer 3 archaeology + EQUIVALENT_UNDER discovery)
> - backend/substrate_index/atom_candidates.py (Tier 3 generation; 5 sources)
> - backend/substrate_index/dialectic.py (Layer 4)
> - backend/substrate_index/spectral.py (Layer 2 v2.1; M=100+ ready)
> - backend/substrate_index/solutions.py (8 queries; universal-lever / cliff / revert / rule-extraction)
>
> **Schema additions:**
> - RelationType: SUPERSEDES + SUPERSEDED_BY + CURRENT_BEST_FOR + RELATES + GENERALIZES + INSTANCE_OF + DEFINED_BY + DEFINED_OVER + EQUIVALENT_UNDER + CONTRIBUTES_TO + TRACES_TO + INFLUENCED_BY
> - AtomKind: METHODOLOGY + LEXICON + METHODOLOGY_RULE + CAPABILITY + SCHOOL
> - Tier: TIER_LEXICON + TIER_METHODOLOGY
> - Atom: current_best_solution + solution_history fields
> - Corpus: METHODOLOGY (validated; populated 4 atoms) + 6 history partitions (RESEARCH_HISTORY populated 449; others queued)
>
> **Architectural lever framing (3 candidates substrate sees on its own):**
> 1. Discriminative attention (universal lever; 5+ capabilities; +0.299 avg; brain analogue: prefrontal top-down attention) -- 92% of capabilities current-best
> 2. Structural binding (cosine_cleanup -> fhrr_unbind; 2 capabilities so far; +0.346 / +0.200; brain analogue: hippocampal/cortical binding) -- second lever
> 3. WK augmentation (discriminative_perceptron + WK lexicon; +0.114; emergent pattern from cycle 238 ingest) -- third pattern
>
> **Research's Drill 1 5-option ranking for substrate-eval recall gap:**
> 1. B + H combined (dual-process recognition; brain analogue) -- SHIPPED
> 2. G (algebra_novelty in BUNDLE space; ~150 LOC) -- sequenced after B+H
> 3. E (weighted-avg composite; 5 LOC bridge) -- SHIPPED
> 4. J (hierarchical 4-channel) -- pending
> 5. F (parallel supervised) -- off-thesis
>
> **User direction LOCKED (latest):** "substrate might still need far, far more knowledge before it can really do this self improvement job... ingest as much of existing mathematics first... and science if possible"; root cause = sparse corpus; Day 2-7 priority = massive math + science ingestion (~400-600 math atoms + 200-400 science Phase B-D coming from Research)
>
> **Background tasks at compaction time (will NOT survive):**
> - b460qy2rc: H1 re-validation with Option B (in flight; ~30-50 min total runtime)
> - bykug3l1u: Phase 2-5 evolve.py auto-ingest (research_to / testbed_to / exp_dev_to / strategy_decisions; in flight)
>
> **On-resume actions:**
> 1. Check if background tasks completed via TaskList; if results landed, analyze
> 2. Pull latest commits; check for new Research notes (math batch 03 B-D / science batch 01 likely)
> 3. With Option B+E+H shipped, re-run H1 validator to validate dual-process recognition
> 4. If background tasks DIDN'T survive: re-run Phase 2-5 + H1 with fixed code
> 5. Re-engage with Research's continuing math+science ingestion deliveries via Phase 6
>
> **5-tier progression state:**
> - Tier 1 (>=3 surprise cycles): MET (14+ cycles)
> - Tier 2 (substrate-proposed architecture Layer 1 validated): MET (v2 composite C, Option B+H)
> - Tier 3 (substrate-proposed atom candidates VALIDATED): MET (18 ACCEPT + ongoing)
> - Tier 4 (substrate-proposed architecture validated via Layer 1 + meta-eval methodology improved): ON DECK pending CoNLL-2000 chunking cell-test + H1 re-validation with B+E+H
> - Tier 5 (substrate proposes structural unification not in catalog): pending Tier 4 + massive corpus expansion
>
> ----- (original Day 1 close state below for reference) -----

> **REFRESHED late evening 2026-06-11** -- Day 1 closing state added below:
> - Layer 1 attribution Day 1 OPERATIONAL; caught algebra-vec as NET NEGATIVE; closed loop ran ~10 min (surprise -> drill -> v2 architecture -> Fix A -> ranking recovery)
> - V2 hybrid two-index + RRF + intent router IMPLEMENTED tonight (algebra_index.py); atom-to-atom shared-basis DEMO works empirically (fhrr_bind -> unbind+circular_conv 0.871/0.533; Hungarian -> beam_search+Viterbi+A* 0.819/0.811/0.810; HMM_emission -> forward_algorithm)
> - Atom.from_dict native multi-format (improvement A); EQUIVALENT_UNDER + CAPABILITY added to enums; concept early-subset (10 atoms; 8-field schema) ingested -> 70 atoms / 237 relations / 10 cross-store
> - Layer 1 audit on tier_tag/corpus_tag (findings #5): corpus_tag PURE NOISE drop; tier_tag marginal-Q5-coincidence
> - Day 2 v2 experiments pre-registered (preregs/2026-06-12_v2_*)
> - Deep-eval dashboard shipped (notes/substrate_deep_self_evaluation_dashboard.md)
> - User direction LOCKED: "literature is not oracle" -- substrate may discover better solutions; flag divergences as discovery not bug; memory file feedback_literature_is_not_oracle_2026-06-11.md
> - Strategic Research notes: 5-tier progression + full-research-ledger vision + Research-direct-CLI-workflow + scientific-corpus-ingest priorities
> - Findings 01-05 all filed + answered same day; 1 closed loop validated (algebra-vec NET NEG -> drill -> v2 in 4 min)
> - Stage A confirmed HEALTHY: F: drive mounted on runner; 2.09M facts; ~23 facts/sec; python procs alive
>
> **DAY 1 FULL CLOSE (post-refresh additions):**
> - Layer 3 archaeology + EQUIVALENT_UNDER discovery shipped (substrate proposed 6 cross-domain equivalence candidates; 5 point at probabilistic-DP <-> graph_traversal unification not in drill 13's 42-pair catalog)
> - Multi-seed tier_tag validation: 2/5 seeds = coincidence -> drop tier_tag; composite simplified to pure semantic
> - Substrate-evaluation ingest path BUILT (NOT regex parser per user critique "substrate can't do its own evaluation?")
> - User-locked rule: literature is not oracle; flag divergences as discovery; memory `feedback_literature_is_not_oracle_2026-06-11.md`
> - Findings #4-#8 all filed and answered same day
> - User reframe: substrate handles NOVELTY correctly via 5-class verdict (TIER-A/B/C/NOVEL/REJECT); shipped v1; surfaced jargon-overlap floor at 19/20 TIER-B
> - Composite C (semantic + algebra HRR) shipped v2; works empirically (16 TIER-C + 4 NOVEL)
> - 4 NOVEL atoms form TIGHT cluster (pairwise 0.65-0.86): substrate proposes new `methodology_corpus` partition for multi-operation methodological content
> - Research VALIDATED methodology_corpus partition + OUT_OF_DOMAIN as 6th verdict class
> - Corpus.METHODOLOGY enum + PartitionedStore.methodology partition added (Phase A)
> - Architectural insight saved as memory: substrate atoms have TWO orthogonal axes (semantic-vec vs content-references); v3 = 3 indexes + RRF
>
> **Day 1 closed-loop cycles toward Tier 1+2 gates (BOTH MET):**
> - Cycle #1: Type B (algebra-vec NET NEGATIVE) -> v2 architecture
> - Cycle #2: Type E (Layer 3 cross-domain unifications)
> - Cycle #3: Type B (corpus_tag PURE NOISE)
> - Cycle #4: Type B + D simultaneously (jargon-floor -> composite C -> methodology_corpus partition)
> - 4 cycles in 1 day; Tier 1 (>=3) + Tier 2 (substrate-proposed architectural improvement validated via Layer 1) BOTH MET
> - Day 2 moves to Tier 3 work per Research
>
> **15-min heartbeat operational (ScheduleWakeup at 17:18)** per user direction.
>
> **AUTONOMOUS-MODE EXTENSIONS (user AFK; "continue on substrate"):**
> - Substrate atom count 92 -> 100 via 8 NER gazetteer ingest (kind=lexicon; tier=T_lexicon NEW)
> - **M=100 spectral observability threshold MET** (insufficient_M_warning=false on semantic codebook)
> - Cycle #6 Type B source #5 noise overshoot CLOSED via Research's 4 Q1 fixes (1678 -> 77 cands; 20x reduction)
> - Layer 2 v2.1 numerics corrected (rescale eigenvalues by aspect M/N; algebra-HRR 12x more structured than semantic via mp_bulk_kl)
> - Tier 3 Type A signal SUSTAINED: 18 ingested (cycle #5) + 11 more validated by Research (cycle #7 pending ingest) + 8 gazetteer = 37 substrate-proposed-Research-validated atoms in <24h
> - Layer 4 dialectic operational; 17 findings classified all SECOND_ORDER (substrate proposals extend without contradicting)
> - Path A foreground SSH running (~13 min in on 150 notes; ETA imminent)
> - Stage A still dead (silent crash after RESUME mode post desktop-restart; user "yes back up" attempt failed twice with detached SSH children dying)
> - Day 1 closing summary: notes/testbed_DAY1_SUBSTRATE_INDEX_CLOSING_SUMMARY_2026-06-11.md
> - 11 findings filed; 11 answered same day (Research closed-loop healthy)

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
