# Pre-reg: arc_retrieval_multicue_ppr_discriminative_v1

date: 2026-07-24
anchor_name: arc_retrieval_multicue_ppr_discriminative_v1
author: exp_dev (cell author)
design source: notes/research_arc_retrieval_biology_and_design_2026-07-24.md (anchor arc_retrieval_multicue_ppr_discriminative_v1)
prior-work check (substrate_query): top hits `research_drill_iterative_multihop_where_it_works_5x` (cosine 0.373, PPR-native-in-substrate) + prior `ppr_spreading_activation_cpu_v1` HARD_FAIL (0.364). This cell is the FAIR real-graph re-test the note credits, NOT a rediscovery of either.

## Question (can-fail)
RETRIEVAL is the VET-confirmed wall (29537 MM, af29a98ef): given GOLD facts the bind+settle combiner reaches Challenge 0.696, but end-to-end stays ~chance because ~50% of misses = the right fact was never retrieved. Our retriever is flat single-shot cosine NN. Does brain-faithful SPREADING ACTIVATION (Collins&Loftus / ACT-R fan-effect / HippoRAG PPR) over the REAL WorldTree fact-graph -- multi-cue seeded, hub-downweighted, discriminatively re-ranked -- surface the RIGHT (gold central) facts better than cosine, and does that lift end-to-end ARC?

## Graph (REAL WorldTree, sharded; NOT synthetic, NOT superposed)
Bipartite fact-term graph over the ingested tablestore (9720 typed facts across 82 relation tables KINDOF/CAUSE/SYNONYMY/PARTOF/USEDFOR/REQUIRES/IFTHEN/COUPLEDRELATIONSHIP/AFFECT/...):
- FACT nodes = tablestore rows (UID), each an independent node (SHARDED, no bundle superposition -- fixes the prior PPR confound c).
- TERM nodes = content lemmas (arc._content_words, min_len>=4, stopword-filtered) appearing in facts.
- Edges = fact-contains-term incidence. A fact of type KINDOF linking term "dog" and term "animal" realizes the typed KINDOF bridge via both terms attaching to that fact node -- co-occurrence THROUGH a typed fact IS the relational link.
- Node-specificity (hub-dilution fix, HippoRAG precondition b): term vertex weight v[t]=idf[t]=log(nFacts/df[t]); fact->term walk + fact-scoring weighted by idf so KINDOF/hub terms ("animal","water","characteristic") do not swamp activation.

## Pipeline (design note steps 1-5; combiner UNCHANGED = the ONE variable)
1. SEED (semantic, not lexical): content words of question stem + ALL choices linked to term nodes -- exact-vocab match, plus SemanticHDEncoder meaning-match (cosine to term vectors >= SEED_COS for out-of-vocab words). Multi-cue: seeds from stem AND every choice enter one personalization vector (ACT-R fan-effect: a fact bridging a stem-term and a choice-term sums activation from both).
2. PPR / spreading activation: term->fact->term random-walk-with-restart, batched across questions. a = (1-alpha)*seed + alpha*(a @ M), M = row_norm(A^T) @ row_norm(A*idf). alpha=DAMP.
3. DEPTH CAP: HOPS=2 fact-hops (WorldTree central-support median 2, p90 5) -- no open-ended chaining.
4. Fact activation Fscore = (a*idf) @ A^T; rank facts. Arm C re-ranks B's top-M pool by discriminative_score(f)=max_choice cos(f,choice) - 2nd-max_choice cos(f,choice) (Tulving/Badre-Wagner: facts that SEPARATE choices, answer-agnostic -- uses all choices symmetrically).
5. Feed each arm's top-K pool through the UNCHANGED agg.aggregate combiner (imported from exp_arc_aggregation_retriever_bindsettle_v1; modes single + bundle).

## Arms (one variable = retrieval mechanism)
- A baseline_single_shot : existing cosine top-K (QQ @ SV_store.T), unchanged.
- B ppr_spreading_only   : multi-cue PPR, rank by activation, top-K.
- C ppr_plus_discriminative : B's top-M pool re-ranked by discriminative_score, top-K. [MECHANISM]
- D shuffled_graph_control : B/C on degree-preserving edge-permuted incidence (config-model term-endpoint shuffle) -- same seeds, randomized graph. MUST collapse toward A.
- E hub_dilution_ablation : C with idf down-weighting OFF (v=1). Must be worse than C.

## Metrics
- PRIMARY: recall@K (K=10) of GOLD CENTRAL support facts vs WorldTree gold, per arm (objective, external gold; store = FULL tablestore incl. gold, since retrieving a general curriculum fact IS the task -- gold facts are plain sentences, NOT answer labels; this is closed-book-over-curriculum, not answer-leak). Also recall@20 reported.
- SECONDARY: end-to-end ARC (Easy + Challenge separately) through the unchanged combiner (bundle + single), per arm. Binomial 95% CI on Challenge under C.
- SEED-QUALITY SUB-CHECK (make-or-break, HippoRAG): seed_recall = |seed_terms ∩ gold_fact_terms| / |gold_fact_terms|; seed_precision likewise. Measured FIRST (smoke). If seed_recall < 0.5 -> a downstream mechanism fail is attributed to SEEDING, not spreading.

## Pre-registered bands (per the note; HYPOTHESIZED until MEASURED@this cell's metrics.json)
- HARD-PASS (mechanism): C(or B) recall@10 >= A recall +0.15 abs, AND D recall <= A +0.03 (lift collapses when structure destroyed), AND E recall < C recall (hub-downweight load-bearing).
- HARD-PASS (end-to-end): Challenge accuracy under C's pool statistically above chance (binomial 95% CI excludes 0.25; ~+0.08 at n=487).
- MIDDLE-BAND: recall lift positive 0.05-0.15 but D does not fully collapse (partial confound), OR recall rises clearly but end-to-end Challenge stays flat (retrieval necessary-not-sufficient -> redirect: K too high diluting settle).
- HARD-FAIL (mechanism): C/B recall does not exceed A beyond noise (<0.05), OR D ~= C/B (lift not structure-driven -> refutes spreading for this task; redirect to discriminative-rerank-alone isolating step 2 vs 4).
- HARD-FAIL (seeding, diagnostic): seed_recall < 0.5 -> prior-stage failure explains B/C fail WITHOUT indicting spreading. Attributed independently.

## SCHEMA-VET fields
```yaml
cell_chunked: false                       # single cell, no per-seed axis (batched deterministic)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
arms_differ_verified: true                # A/B/C/D/E top-K digests differ (smoke asserts)
deterministic_seeding: true               # fixed int seeds, numpy default_rng, sorted iteration, no hash()
progress_logging: print_flush_true        # + line_buffered stdout + heartbeats
baseline_in_band: true                    # baseline A recall in (0.05,0.95) verified at smoke (AG-guard)
calibration_check: adaptive_with_discriminator_gate  # SEED_COS/DAMP fixed a priori; discriminator-fires (B pool != A pool, PPR moved mass, seeds non-empty) verified at smoke
crlb_n/a: "recall@K over a real gold set has no closed-form argmax-noise floor; feasibility set by graph reachability, measured not bounded"
discriminator_reachability: true          # recall lift is reachable (planted bridge-fact case in self-test proves B>A is achievable)
compute_architecture: "mixed CPU: batched GloVe encode + scipy.sparse batched PPR matmuls across all questions + per-question discriminative re-rank; wall < 10 min foreground (INLINE-LOCAL)"
storage_strategy: sharded                 # each fact = own embedding + own graph node; no superposition (fixes prior PPR confound)
positive_control_arms:                    # gate D: the combiner is reused UNCHANGED; baseline A reproduces the prior cosine retrieval at matched regime
  - arm: A_baseline_reproduces_cosine_retrieval
    primitive: single_shot_cosine_topk (agg.retrieval_pool logic)
    tolerance: n/a (identical code path)
functional_requirements:
  - req: surface gold central facts -> recall@K metric (arms A-E)
  - req: reach bridge facts with no query lexical overlap -> multi-cue PPR (arm B, step 2)
  - req: pick facts that separate choices -> discriminative re-rank (arm C, step 4)
  - req: combine retrieved facts -> UNCHANGED agg.aggregate (bundle/single)
composition_edges:
  - from: retrieval_pool (A-E)
    to: agg.aggregate
    verdict: SHAPE_MATCH   # pool -> (fact_hd[K,N], q_rel[K]) exactly the shape agg.aggregate consumes
```

## Contract
INLINE-LOCAL foreground-to-completion (GloVe cache + WorldTree git-ignored/large -> NOT remote-portable); NO push/remote-persist; ASCII-only; deterministic; runs in repo .venv; agent-reported VET-PENDING. Glass-box: every retrieved fact traces to seed terms + activation path (glassbox_sample.json).
