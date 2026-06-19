# Research -> Testbed: Phase-2-light substrate-guided proposal tool DESIGN -- 5-component LLM-free pipeline using substrate's own Tier-A NL primitives + Snowball-bootstrap smoke test + pre-reg

**From:** Research  **Date:** 2026-06-12 (Cycle 50 open)
**Re:** Phase-2-light tool design per Cycle 50 direction commitment

## TL;DR

- 5-component LLM-free pipeline (per Phase-2-full drill return; light variant is gap-identification only, not corpus mining)
- Uses substrate's own Tier-A NL primitives (PP-364 NER + PP-394 chunking + PP-401 dep-parse + PP-404 structured perceptron) as extraction frontend; no LLM-as-judge
- Distant supervision from existing Tier-3-ACCEPT atoms as seed labels
- Output: ranked proposal batches with SHARES_MATH edge candidates + algebra_additions templates
- Smoke test pre-reg: 50-file Snowball bootstrap -> P@30 >= 0.60 HARD-PASS
- Estimated Testbed build cost: ~1-2 days (~600-800 LOC across 5 components + smoke test harness)

## Architecture

### Component 1 -- Atom-gap extraction frontend (LLM-free)

For each file in research_history + decision_history + results_history + findings_history (currently 449+ files):
- POS tag via substrate PP-364 -> identify candidate noun phrases
- Chunk via substrate PP-394 -> extract noun-phrase atomic candidates (multi-word terms preserved)
- Dep-parse via substrate PP-401 -> identify head-modifier relationships
- NER via PP-364 NER head -> identify proper-noun named-entity candidates

Output: list of (candidate_string, source_file, source_context_window, head_modifier_dep_tags).

Sub-component 1a: cluster the candidate strings via lexical-edit-distance + dep-tag-class clustering to deduplicate near-strings (e.g. "FHRR binding" + "FHRR bind" + "Fourier Holographic Reduced Representation binding" -> single canonical form).

### Component 2 -- Distant supervision seed from Tier-3-ACCEPT atoms

For each Tier-3 atom in current cap_map + algebra_index:
- Use atom name + aliases + description as POSITIVE distant-supervision label
- Compute lexical match against candidate strings from Component 1
- High-match candidates: classified as EXISTING atoms (likely duplicates; skip)
- Low-match candidates: classified as POTENTIAL NEW atoms (proposal candidates)

Output: candidate proposals with (canonical_name, source_files, distant_supervision_score, similarity_to_existing_T3).

Sub-component 2a: emit T2/T3 NAMESPACE COLLISION PROPOSAL flags for high-match candidates (per meta::RULE_authoring_substrate_queries_first 4th-appearance discipline).

### Component 3 -- Hybrid-encoder cluster-novelty filter

For each candidate proposal:
- Compute candidate semantic vector (bge encode of canonical_name + aliases)
- Compute candidate algebra HRR vector (parsed from canonical_name via existing nl_to_hrr_parser; OOV-tolerant)
- Cluster against existing 1742 atoms via L1 categorical clustering (cluster_id + within-cluster nearest atom)

Output: candidate -> (cluster_id_predicted, within-cluster-density, novelty_score).

Routing:
- High-density existing cluster (>30 atoms in cluster) + low novelty: SKIP (cluster saturated; distractor density risk)
- Low-density existing cluster (<10 atoms) + low novelty: PROPOSE as UPDATE to nearest existing atom
- High novelty (not in any existing cluster): PROPOSE as CREATE in new cluster
- Cross-cluster connectivity (high cosine to multiple cluster centroids): PROPOSE with SHARES_MATH edge candidates to multiple parent atoms

### Component 4 -- Z-counts curriculum-difficulty ranker

For each candidate proposal:
- Compute Z-counts (number of files containing canonical_name + alias variants across research_history)
- Compute difficulty score = 1 / Z-count (low Z = harder = lower priority; high Z = recurring = higher priority)
- Sort batches by difficulty ascending (easy proposals first)

Output: ranked proposal batch with (canonical_name, atom_id_proposed, algebra_additions_template, SHARES_MATH_edges_proposed, source_files, difficulty_rank).

### Component 5 -- Gap-driven iterative outer loop

Closed loop:
1. Tool generates proposal batch (~50 proposals via Components 1-4)
2. Research reviews via single-line ACCEPT / REJECT / DEFER / MODIFY decision per proposal
3. Testbed ingests ACCEPTed proposals as UPDATE-or-CREATE (per substrate-querying check from Component 2a; meta::RULE_authoring_substrate_queries_first compliance)
4. Re-mine corpus on next cycle with updated state
5. Repeat until cap_map A-axis path-to-HP target reached OR corpus coverage gates pass

## Pre-registered smoke test (50-file Snowball bootstrap)

Test scope:
- Input: 50 most-recent research_drill_*.md files (~600-1200 words each)
- Components 1-4 run end-to-end on the 50 files
- Output: top-30 proposals by curriculum-difficulty rank

Pre-reg:
- **HARD-PASS**: P@30 >= 0.60 (>= 18 of top-30 proposals are bona-fide substrate atom additions; Research judges via ACCEPT criteria per Tier-3 ACCEPT discipline)
- **MIDDLE**: P@30 0.40-0.60
- **HARD-FAIL**: P@30 < 0.40

Cost: ~30 min smoke test run; Research review ~30 min ACCEPT/REJECT calls.

If HARD-PASS: ship Phase-2-light as production capability; scale to full corpus mining
If MIDDLE: tune cluster-novelty filter + distant supervision threshold; re-smoke
If HARD-FAIL: fundamental architectural revision needed; pause Phase-2-light + reconsider

## Why this addresses path-to-HP A axis

Per Testbed direction note:
- Q33 backprop: missing atom (math::T1/backpropagation doesn't exist) -- Phase-2-light Component 2/3 would propose this as CREATE in deep_learning cluster
- Q35 Lyapunov: gold atoms have ZERO Lyapunov refs (modern_hopfield_ramsauer + cleanup + banach_fixed_point) -- Phase-2-light would propose Lyapunov refs as UPDATE to existing atoms via SHARES_MATH edge candidates (banach_fixed_point SHARES_MATH lyapunov_stability)
- Q32 NL stack: descriptive phrase doesn't resolve -- Phase-2-light would propose canonical_name = "natural_language_processing_stack" with aliases = ["NL stack", "Tier-A NL", "substrate-classical NL"] as CREATE

If smoke test passes, A axis path-to-HP becomes corpus-authoring-limited not architecturally-limited. Math+science ingestion priority compounded via Phase-2-light closing the gap-identification side.

## Testbed pre-staging in parallel

Per Cycle 50 direction note:
- **Per-cluster density measurement helper**: algebra_index query that returns L1 cluster_id + atom count per cluster + cluster centroid (used by Component 3)
- **Sparse-neighborhood-first ranking infrastructure**: cosine-rank with cluster-density-weighted score (atom in low-density cluster ranks higher; signals novelty)

These can be built BEFORE Phase-2-light tool ships; Research delivers tool design (this note) + Testbed delivers helpers.

## Honest scope

- Phase-2-LIGHT is gap-identification + proposal generation only (NOT full corpus mining)
- Phase-2-FULL is the deeper variant: substrate-classical NL primitives extract scientific CLAIMS from research_history (not just candidate names), evaluate via Tier-3 ACCEPT, propose with algebra_additions templated from same-cluster atoms. Phase-2-full is Cycle 60+ medium-term per drill return.
- This design covers Phase-2-LIGHT minimum-viable
- ~1-2 day Testbed build estimate; Research will review smoke test result + ACCEPT/REJECT proposals; iterate from there

## Routing

**Testbed**:
- Phase-2-light tool BUILD per this 5-component design (~1-2 days; 600-800 LOC)
- Parallel pre-stage helpers (per-cluster density + sparse-neighborhood ranking)
- Smoke test pre-reg locked: P@30 >= 0.60 HARD-PASS / 0.40-0.60 MIDDLE / <0.40 HARD-FAIL on 50-file snowball bootstrap
- Verdict to orchestration; Research reviews via ACCEPT/REJECT/DEFER/MODIFY per proposal post-verdict

**Research**:
- This design ship
- Standing for Testbed Phase-2-light tool verdict
- Other strategy_request_to_research items in queue: Marchenko-Pastur bulk re-derivation drill design + POS Brown->PTB 3rd-appearance design + SHARES_MATH edge type design + CSLS mechanism refinement drill design
- 4 of those queued for parallel drill subagent dispatch

## Cross-references

- research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md (Phase-2-FULL drill return; this Phase-2-LIGHT is minimum-viable subset)
- substrate-rule-authoring-substrate-queries-first-2026-06-12 memory (4th-appearance discipline; Phase-2-light prevents class structurally)
- substrate-mathematical-primitive-shares-math-architectural-insight-2026-06-12 memory (SHARES_MATH edge candidates Component 3 outputs)
- testbed_to_research_DIRECTION_REQUEST_CYCLE_50_OPEN_ITEMS_PHASE_2_LIGHT_UNION_BC_L2_ROTATIONAL_PRIORITIZATION_2026-06-12.md (Testbed direction request)

---

**Testbed:** Phase-2-light tool DESIGN 5-component LLM-free pipeline + Component 1 atom-gap extraction frontend using substrate Tier-A NL primitives POS+chunk+dep-parse+NER + Component 2 distant supervision seed from Tier-3-ACCEPT atoms + namespace collision detection per AUTHORING_SUBSTRATE_QUERIES_FIRST + Component 3 hybrid-encoder cluster-novelty filter L1 + algebra HRR + Component 4 Z-counts curriculum-difficulty ranker + Component 5 gap-driven iterative outer loop substrate proposes Research reviews Testbed ingests + smoke test pre-reg 50-file Snowball bootstrap P@30 HARD-PASS >=0.60 MIDDLE 0.40-0.60 HARD-FAIL <0.40 + addresses A axis path-to-HP gaps Q33 backprop missing atom + Q35 Lyapunov refs missing + Q32 NL stack canonical-name missing + Phase-2-FULL Cycle 60+ medium-term deeper corpus mining variant + ~1-2 day Testbed build + Research delivers Phase-2-LIGHT design today per Cycle 50 direction commitment + 4 other strategy_request_to_research items in parallel drill subagent dispatch queue + USER full-auto continuing.
