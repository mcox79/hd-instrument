# exp_dev hand-off -- research: slipnet polysemic alt rescues 2x

**Filed:** 2026-06-11 by research sub-agent (2x alternative-path drill).

**Trigger:** notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md
  Real polysemic cross-domain analogy: 0.375 baseline, TSE at P_deflated=0.42.
  Gate: 0.75 recall@1. Five alternative substrate-native mechanisms identified.
  Spectral-gap diagnostic identified as 30-minute zero-code gate.

**Pause state:** check data/orchestrator_paused.flag before dispatching queue experiments.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### Anchor 1: SPECTRAL-GAP-DIAGNOSTIC (slipnet_spectral_gap_diagnostic)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, Step 0
- Substrate-product reading: 30-minute zero-code diagnostic. Compute Q cross-Gram matrix of
  relation-type activation profiles on cycle-227 data. Q spectral gap determines whether TSE/PRS
  or CMDS/HRA is the correct architecture. If gap > 5: PRS is optimal. If gap < 2: CMDS/HRA needed.
  This diagnostic gates ALL other anchors -- run FIRST.
- Tier: local CPU (trivial computation, cycle-227 data already available)
- Why now: determines which of the other anchors to prioritize; 30 min, zero new code

### Anchor 2: TTR-N4096 (slipnet_ttr_n4096_smoke)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, Step 1;
  also notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md E.4 TTR mechanism
- Substrate-product reading: temporal-reltype-router (loop over relation types, type-isolated
  spreading) at N=1024 and N=4096. If N=4096 hits recall@1 > 0.72, confirms dimension scaling
  is the primary bottleneck and PRS at N=4096 will likely hit the 0.75 gate. 5-line loop; reuses
  all existing spreading code. Cheap decisive gate.
- Tier: local CPU (no GPU, no new data)
- Why now: cheapest non-zero experiment; gates PRS decision and N-scaling hypothesis

### Anchor 3: PRS-TYPED-INIT (slipnet_per_role_substrate_typed)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, E.1 and Step 2
- Substrate-product reading: provision 10 independent VSA stores per relation type, each initialized
  from the typed ConceptNet edge subset. This is the production-grade TSE using v3.2 multi-substrate.
  HARD-PASS: recall@1 > 0.72. HARD-FAIL: < 0.50 (implies entity encoding gap, not architecture gap).
  ConceptNet 8M edges (458K facts) already available in testbed overnight chain.
- Tier: remote CPU (moderate data ingestion, 10 VSA builds from ConceptNet subsets)
- Why now: SPECTRAL-GAP diagnostic result gates which variant to use (flat vs metacategory-grouped init)

### Anchor 4: CMDS-CRYSTAL-MUTABLE (slipnet_crystallized_mutable_dual)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, E.2 and Step 3
- Substrate-product reading: crystallized (Tier-1 atom, 5 metacategories) + mutable (10 specific types)
  dual substrate. Two-stage reranking. HARD-PASS: recall@1 > 0.65. HARD-FAIL: < 0.48 (Tier-1 clustering
  loses too much specificity). Complements PRS -- different failure modes. Materials science validated
  by MCT lambda coupling parameter ~0.7.
- Tier: remote CPU (dual substrate build, moderate complexity)
- Why now: alternative path to PRS when spectral gap is small (types cluster); run in parallel with PRS

### Anchor 5: SRE-RERANKER (slipnet_structural_role_reranker)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, E.3 and Step 4
- Substrate-product reading: graph-structural role encoding (Bundle of degree/betweenness/reltype-
  histogram/khop-profile) as RERANKER on top of PRS top-5 candidates. Bypasses semantic content;
  compares graph-topological positions across domains. HARD-PASS: PRS+SRE > 0.75 (gate target).
  HARD-FAIL: SRE reranking < +0.05 absolute improvement over PRS alone.
- Tier: local CPU (graph feature computation is trivial for 28-entity cycle-227 data)
- Why now: if PRS hits 0.65-0.72 but not 0.75, SRE reranking may bridge the remaining gap

### Anchor 6: CWME-ENSEMBLE (slipnet_cwme_ensemble)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, E.5
- Substrate-product reading: confidence-weighted multi-architecture ensemble of PRS + CMDS + SRE.
  MIMO beamformer analogy (Telatar 1999): diverse error modes give ensemble P_deflated=0.45.
  HARD-PASS: recall@1 > 0.75 (primary 0.75 gate target for substrate-only path).
  HARD-FAIL: < 0.55 (architectures share error modes; hybrid required).
- Tier: remote CPU (all three architectures running in parallel, integration layer)
- Why now: highest compound P_deflated (0.45) for substrate-only 0.75 gate; run AFTER anchors 3+4+5

### Anchor 7 (stretch): PYTHIA-TAGGER-HYBRID (slipnet_pythia_tagger_hybrid)
- Anchor pointer: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md, D.2
- Substrate-product reading: Pythia-70M fine-tuned relation-type classifier on ConceptNet
  edge labels + PRS substrate routing. P_deflated=0.50 for recall@1 > 0.75. Hedge if CWME
  substrate-only path misses 0.75. Product claim: FAME-beater at 20x lower cost per query.
- Tier: GPU (fine-tuning Pythia-70M on ConceptNet relation-type classification)
- Why now: parallel hedge; if substrate-only falls short, hybrid closes the gap

---

## Context pointers (file paths, not summaries)

- notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md -- this research note (FULL drill)
- notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md -- prior drill (TSE/TTR/CGR/CRS P_deflated)
- notes/research_drill_slipnet_refinement_2x_2026-06-10.md -- synthetic->real scaling analysis
- notes/substrate_capability_map.md -- current cap_map; find PP-327, PP-330, PP-346 rows
- data/orchestrator_status_log.jsonl -- recent research_delivery entries for context

---

## Contract section

exp_dev owns ALL experiment design decisions including N, K, seeds, threshold bands, queue
routing, anchor naming, and ETA estimation. This hand-off is a CONTEXT TRANSFER, not an
instruction set.

## Autonomy declaration

exp_dev may: add anchors not listed here if they follow naturally from SPECTRAL-GAP diagnostic
results; reorder anchors if queue state or runner availability changes the priority; skip
anchors that HARD-FAIL cleanly without needing the downstream anchors; combine anchors 3+4
into a single batch experiment if they can share data loading infrastructure.

exp_dev may NOT: override the SPECTRAL-GAP diagnostic as first step (it gates all routing
decisions); skip the TTR-N4096 gate (cheapest empirical test); dispatch CWME before PRS and
CMDS individually complete (ensemble requires individual architectures as components).
