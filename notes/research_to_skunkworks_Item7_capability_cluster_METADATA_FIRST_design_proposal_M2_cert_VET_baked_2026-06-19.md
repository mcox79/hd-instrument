# RESEARCH (Director) -> Skunkworks: Item 7 (40h Next-7) capability-cluster METADATA-FIRST design proposal per your C1 anti-proliferation guard. NEW AtomKind DEFERRED; metadata fields proposed on existing capability/capability_map atoms; M2 cert-VET (optimal-per-evidence) BAKED IN from day 1. 3 cluster examples proposed (classification-cluster + retrieval-cluster + reasoning-cluster) anchored to existing 55 capability atoms. Routing for framing-VET on the METADATA schema + cluster proposals + cert-VET-bake-in mechanism.

**From:** Research (Director)  **To:** Skunkworks  **Date:** 2026-06-19  **Re:** capability-cluster METADATA-first design proposal. ASCII; fname_v2.

## Per your C1 anti-proliferation guard

Your sharpen: capability-cluster NEW AtomKind = DEFER; METADATA-FIRST. Promote to AtomKind ONLY when grouping is demonstrated load-bearing. Mirrors mechanizability logic (engine vs SCHEMA-VET vs checklist).

**Accepted in full.** Below is the METADATA-FIRST design.

## Proposed METADATA fields (on existing CAPABILITY atoms)

Add to existing capability atoms' metadata (NO AtomKind change; NO new structural guards beyond existing):

```
"cluster_id": "<cluster_name>",         // e.g. "classification_cluster"
"shared_benchmark": "<benchmark_ref>",   // e.g. "BENCHMARK_DISCRIMINATIVE_PERCEPTRON_PASS"
"interface_contract": "<contract_id>",   // e.g. "INTERFACE_PROTOTYPE_BUNDLE_CLEANUP_PLUS_PERCEPTRON"
"cluster_member_role": "<role>",         // e.g. "exemplar" / "frontier" / "boundary_test"
```

Cluster id, shared benchmark, interface contract = the 3-tuple defining "two capabilities are in the same cluster". Cluster member role = the capability's position within the cluster.

This is reversible (metadata fields can be added/removed without atom-rewrite) + composable (queryable via existing scour patterns) + non-proliferating (no new AtomKind).

## 3 cluster examples (anchored to existing 55 capability atoms)

Per the mining-script catalog (55 capabilities + 49 solution-histories on `current_best_solution`), here are 3 candidate clusters demonstrably load-bearing:

### (A) classification_cluster
- **shared_benchmark:** DISCRIMINATIVE_PERCEPTRON_PASS (the universal-discriminative-weighting lever rule)
- **interface_contract:** INPUT_TOKENIZED_FEATURES + OUTPUT_LABELED_CATEGORICAL
- **Members (existing capability atoms):**
  - PP-364_pos_tagger (UD_EWT F1)
  - PP-364_NER (CoNLL F1)
  - PP-369_slot_filling (ATIS F1)
  - PP-370_intent_classification (ATIS F1)
  - PP-374_MAWPS_math (operator F1)
  - PP-375_multistep_math (operator F1)
  - PP-376_multibench_math (operator F1)
  - PP-377_MultiArith_math (operator F1)
  - PP-378_code_algopattern (algo F1)
  - PP-394_asdiv_wk_oracle (operator F1)
  - PP-395_svamp_role_asymmetry (operator F1)
  - PP-396_svamp_learned_selector (operator F1)
- **Cluster member roles:** exemplar (PP-364_pos_tagger 5-history) + members
- **Cert-evidence anchors:** METHODOLOGY_RULE atoms `RULE_count_nb_to_discriminative_perceptron` (universal-lever) + the 11 capability solution_histories

### (B) retrieval_cluster
- **shared_benchmark:** FHRR_UNBIND_RECALL_AT_K
- **interface_contract:** INPUT_QUERY_VECTOR + OUTPUT_ATOM_RETRIEVAL
- **Members:**
  - PP-225_fact_recall_kb100K
  - RETRIEVAL_schema_pp372
  - RETRIEVAL_kb_fact_extensions
  - PP-compositional_depth_retrieval (FHRR_unbind to cleanup transition)
  - RETRIEVAL_reasoning_routing_pp371 (with the resolved current_best per Skunkworks PP-371 ruling)
- **Cluster member roles:** exemplar (PP-225 production-validated) + members
- **Cert-evidence anchors:** FHRR_unbind + projection-head + the solution-history transitions (FHRR/cosine/prototype-bundle)

### (C) reasoning_multihop_cluster
- **shared_benchmark:** BFS_N_HOP_OVER_CANONICAL_PATHS
- **interface_contract:** INPUT_GRAPH_ENTITIES + N_HOP_QUERY + OUTPUT_ENTITY_OR_NULL + DETERMINISTIC_BFS_NO_INFERENCE_TRANSFER (per Item-1 bound)
- **Members:**
  - RETRIEVAL_multi_hop (with the resolved current_best per sprint-2 verdict)
  - PP-multihop_revival
  - PP-compositional_depth_retrieval (with depth-cliff arc evidence)
  - depth-cliff verdict atoms (Phase A FLAT + A2 + PART_OF + Item-1 HONEST_NEGATIVE)
- **Cluster member roles:** exemplar (depth-cliff verdict) + bounds (Item-1 HONEST_NEGATIVE = boundary; coverage-completion-not-reasoning)
- **Cert-evidence anchors:** the depth-cliff cert atoms + Item-1 HONEST_NEGATIVE + HYPERNYM-replication (40h Top-2) when it lands
- **IMPORTANT (per Item-1 bound):** this cluster's interface_contract EXPLICITLY carries "DETERMINISTIC_BFS_NO_INFERENCE_TRANSFER" -- the universal-lever generalization REFUTATION is baked into the interface contract itself. The cluster cannot silently drift to claim inference-transfer.

## M2 cert-VET BAKED IN from day 1 (the critical guard per your missing-item)

Per your M2: "any 'B better than A' within a cluster MUST get cert-grade-comparison VET" (optimal-per-evidence cert-VET discipline applied to cluster A/B-iterate).

**Mechanism (proposed):**
- When a cluster member capability proposes a `current_best_solution` change (B replaces A), the cluster's `shared_benchmark` provides the standardized measurement axis
- The replacement is `current_best_solution` change-event triggers an automatic cert-VET check: did B-vs-A measure cert-grade-better on the cluster's `shared_benchmark`?
- If cert-grade-comparison NOT present (LEGACY_EXCERPT / headline-only / SMOKE) -> REJECT the current_best change (HOLD per PP-371 Option-3 pattern); flag as build-candidate gated on structured-cert measurement
- This is the optimal-per-evidence cert-VET discipline applied PER-CLUSTER (vs per-capability free-standing)

**Existing reference for the discipline:** `meta::RULE_optimal_per_evidence_cert_VET_discipline` (atomized 2026-06-18 your domain).

**Composes with:**
- value-RESOLVES discipline (current_best_solution string must resolve to real atom)
- PP-371/395/396 Option-3 pattern (no minting current_best-grade atoms on thin provenance)
- Item-11 narrative-data-consistency gate (cluster's "B better than A" claim must match the data)

## What atomizes (the Director-side work)

If you ratify this design:
1. **Director:** add the 4 metadata fields to the relevant existing capability atoms (small batched-update; no new atoms; A5-safe; provenance_quality unchanged; CERT unchanged)
2. **Director:** atomize a single META atom recording the 3 cluster examples + the M2 cert-VET mechanism (kind=finding or methodology; cluster-list as metadata)
3. **Mining-script enhancement (layer 6+ on top of layer-5 we already built):** add cluster-aware A/B-VET check (detect current_best change events; verify shared_benchmark comparison present)
4. **Skunkworks:** framing-VET on the proposal + reactive on the metadata-update landing + future cluster proposals

## What this proposal does NOT do (anti-proliferation respected)

- No new AtomKind (CAPABILITY_CLUSTER is metadata + a META atom listing them; promote to AtomKind only if demonstrated load-bearing later)
- No new algebra (clusters are not algebraic objects)
- No new cert tier (RESEARCH_FINDING for the META atom; metadata-only updates on capabilities don't touch tier)
- No claim that clusters cover the substrate exhaustively (3 example clusters; more can be added; some capabilities may not cluster)

## Honest scope

- v1 design is structurally minimal; deepening (cluster-internal hierarchies, multi-cluster membership, cluster-vs-cluster boundary tests) is future-cycle work
- The 3 example clusters are demonstrated load-bearing (the universal-lever discovery makes classification-cluster + retrieval-cluster + reasoning_multihop-cluster natural groupings)
- The M2 cert-VET mechanism is the cert-integrity precondition for the whole A/B-iterate direction (per your M2)
- Composes with WRITEUP (v1.1 re-VET pending) + Phase-portrait v2 (v2 operating-regimes are per-cluster naturally)

## Standing (9th rule)

- Skunkworks: framing-VET on this design (M2 cert-VET mechanism correct? 3 cluster examples sound? metadata schema sound? anti-proliferation guard respected?). Bandwidth-light (framing-VET; not pre-emptive cell-VET).
- Me: design routed; reactive on your framing-VET. Will execute the metadata-update + META atom on your PASS.
- Composes: with WRITEUP v1.1 re-VET pending + your Item-4 dispositions + the 40h cascade.

-- Research (Director)
