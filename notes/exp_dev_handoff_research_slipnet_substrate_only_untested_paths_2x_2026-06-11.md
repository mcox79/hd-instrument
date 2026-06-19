# exp_dev hand-off -- research: slipnet substrate-only untested paths 2x

**Filed:** 2026-06-11 by research sub-agent (Sonnet, 2x operational drill).

**Trigger:** Research note at:
  d:/AI/hd-instrument/notes/research_drill_slipnet_substrate_only_untested_paths_2x_2026-06-11.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching any queued cells.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA,
smoke profile, full profile. Research does NOT specify numerical parameters or implementation
details. Exp_dev reads the research note for mechanism rationale; designs all experiments
autonomously.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Phase 0 -- Diagnostics (run first, no new code required)

**Anchor 1: ORACLE-RELTYPE-TAG-GATE**
- Anchor pointer: Path 14 in research note (oracle relation-type tag upper-bound diagnostic)
- Substrate-product reading: Provides the critical discriminating test: if oracle-tagged TSE
  recall@1 < 0.55 on ALL benchmarks, entity encoding is the bottleneck and all disambiguation
  paths (3, 4, 5, 10, 11) have low utility. If oracle-tagged recall@1 > 0.70, disambiguation
  is the bottleneck and paths 3, 4, 10 have high expected value. Must run before Phase 1.
- Tier hint: local_cpu_queue or remote_cpu_queue (zero new code; modify existing TSE to accept
  explicit relation-type key at query time)
- Why now: 30-minute experiment that determines the entire Phase 1-3 strategy. Delaying this
  burns engineering time on mechanisms that may have < 0.05 expected lift.

**Anchor 2: BENCHMARK-COMPARISON-WN18RR**
- Anchor pointer: Path 6 in research note (WN18RR + OGBL-WikiKG2 + ConceptNet hand-curated)
- Substrate-product reading: The P9 Control 3.1/3.2 degree-bias confound for FB15K-237 was
  confirmed. WN18RR is a structurally cleaner benchmark where structural methods consistently
  show 0.10-0.20 MRR higher than FB15K-237 in the link-prediction literature. If TSE recall@1
  > 0.58 on WN18RR, the "0.42 architectural ceiling" is a benchmark artifact, not an
  architectural ceiling. This reframes the entire capability claim.
- Tier hint: remote_cpu_queue (data loading + evaluation; WN18RR publicly available at
  https://github.com/villmow/datasets_knowledge_embedding)
- Why now: WN18RR evaluation directly tests whether the 0.42 FB15K-237 ceiling is
  benchmark-specific. If YES: all other experiments move to WN18RR as primary evaluation.

---

### Phase 1 -- Cheapest mechanism tests (after Phase 0 diagnostics)

**Anchor 3: MODERN-HOPFIELD-SLIPNET**
- Anchor pointer: Path 9 in research note (Ramsauer 2020 MHN softmax update rule)
- Substrate-product reading: MHN is field-advisor Tier-1 fruit-bearing, explicitly recommended
  for drilling. MHN spreading is one code change (replace W*activation with softmax(beta*W*a)).
  Exponential capacity theorem provides the strongest mathematical guarantee of any mechanism
  in this batch. Sweep beta in {0.1, 0.5, 1.0, 2.0, 5.0} to find optimal softmax sharpness.
  If recall@1 > 0.58 at any beta: confirms MHN brings transformer-equivalent dynamics to
  the substrate spreading computation.
- Tier hint: remote_cpu_queue (2-4 hours; one code modification + beta sweep)
- Why now: Tier-1 field advisor recommendation + 2-4 hour cost + highest P_deflated (0.40)
  among Phase 1 mechanisms.

**Anchor 4: PP346-CONTEXT-BINDING-TRANSPORT**
- Anchor pointer: Path 4 in research note (PP-346 context binding transported to slipnet query)
- Substrate-product reading: PP-346 achieved 1.000 on context-bound polysemy -- the substrate
  already has this validated primitive. The slipnet query pathway does NOT currently apply
  context binding before injection. Transporting PP-346's binding call to the slipnet injection
  step is a direct product of existing validated code. If recall@1 > 0.58: PP-346 context
  binding generalizes to the spreading activation setting.
- Tier hint: local_cpu_queue (2-3 hours; adapt existing PP-346 binding call to slipnet; no
  new algorithm)
- Why now: lowest-cost test of a validated existing primitive. Should precede more engineering-
  intensive paths.

**Anchor 5: N-SCALE-SWEEP-8192-TO-65536**
- Anchor pointer: Path 1 in research note (N scaling: VSA capacity theorem, JL interference)
- Substrate-product reading: Zero new code. One config constant change. Tests the VSA capacity
  hypothesis directly: does recall@1 improve monotonically with N from 8192 to 65536?
  JL guarantee: interference ~ 1/sqrt(N); 8x reduction from N=1024 to N=65536. If monotonic
  improvement > 0.08 absolute: N scaling is a practical rescue path.
- Tier hint: local_cpu_queue (1-2 hours; trivial config change)
- Why now: truly zero-code test. If it works, immediate actionable path.

**Anchor 6: ITERATIVE-WTA-REFINEMENT-SPREADING**
- Anchor pointer: Path 5 in research note (TOP-K iterative gating, T=5 iterations)
- Substrate-product reading: Implements cortical WTA competition dynamics (Lim & Goldman 2013).
  5-iteration loop with TOP-K gate is a minor extension of existing spreading code. Tests
  whether iterative accumulation of dominant activations converges to better precision than
  single-pass spreading. Pre-check: compute eigenvalue gap of W_all before running -- if gap
  < 2x, MHN (anchor 3) is preferred over iterative (near-degenerate case).
- Tier hint: local_cpu_queue (2-3 hours; loop extension + eigenvalue gap diagnostic)
- Why now: cheap test of a genuinely distinct mechanism (iterative vs single-pass).

---

### Phase 2 -- Medium cost, after Phase 1 results (run if Phase 1 < 0.55)

**Anchor 7: VSA-FCG-HOLISTIC-CONSTRUCTION**
- Anchor pointer: Path 7 in research note (VSA-FCG construction schema approach)
- Substrate-product reading: VSA-FCG achieved 0.906 on POS tagging -- the most direct
  empirical precedent for this mechanism class. Path 7 encodes relational patterns as holistic
  VSA construction bundles (form+function+context triples) rather than graph spreading.
  This is architecturally orthogonal to all tested spreading mechanisms. If recall@1 > 0.58:
  holistic bundle completion is a viable alternative to spreading for the analogy task.
- Tier hint: remote_cpu_queue (4-6 hours; new construction encoding architecture; moderate
  implementation effort)
- Why now: Highest P_deflated in Phase 2 (0.40) and orthogonal mechanism to all prior tests.
  Field advisor indirectly endorses via free-probability link to FHRR fractional binding.

**Anchor 8: CLASSIFIER-THEN-RETRIEVAL-CENTROID**
- Anchor pointer: Path 10 in research note (substrate-as-classifier for relation type first)
- Substrate-product reading: Self-labeling using pre-computed relation-type centroid vectors.
  If centroid accuracy > 72%: the substrate can self-route without an LLM tagger, keeping
  the system substrate-only. Product implication: substrate performs end-to-end cross-domain
  analogy with built-in relation-type disambiguation, no external model required. Most
  product-relevant substrate-only path.
- Tier hint: local_cpu_queue (2-3 hours; centroid pre-computation offline + lookup at query time)
- Why now: product-critical test; substrate self-labeling is the strongest "beats LLMs at
  relevant cost" product narrative.

**Anchor 9: HIERARCHICAL-TIER1-TIER3-PIPELINE**
- Anchor pointer: Path 11 in research note (Tier-1 abstract atoms then Tier-3 entity specificity)
- Substrate-product reading: Implements the Badre frontoparietal hierarchy in the substrate.
  Stage 1 uses metacategory-level abstract relation atoms (5-6 types from ConceptNet clustering,
  Speer 2017) to get top-20 candidates; Stage 2 refines with instance-level typed spreading.
  This is the most biologically faithful approach. Requires building Tier-1 atom W_crystal
  from ConceptNet metacategory merging -- ConceptNet 8M edges are already loaded in testbed.
- Tier hint: remote_cpu_queue (4-6 hours; Tier-1 atom clustering from ConceptNet + 2-stage eval)
- Why now: ConceptNet data already available from testbed overnight chain. Tier-1 clustering
  can use the metacategory labels that Speer 2017 provides explicitly.

**Anchor 10: CASCADE-DISAMBIGUATION-3STAGE**
- Anchor pointer: Path 3 in research note (3-stage sequential context-binding refinement)
- Substrate-product reading: Implements the full neural analogy pipeline: Stage 1 (automatic
  spreading), Stage 2 (context-binding gating), Stage 3 (structural role reranking). This is
  the most comprehensive substrate-only disambiguation approach and addresses all three
  bottleneck sources identified in the prior drills. Highest engineering cost in Phase 2.
- Tier hint: remote_cpu_queue (4-8 hours; 3 sequential passes over existing code)
- Why now: after cheaper Phase 1 + Phase 2 anchors clarify which single stage provides the
  most lift. If anchor 4 (PP-346 Stage 2 transport) + anchor 8 (classifier Stage 1) both
  pass independently, the cascade (anchor 10) should combine both lifts.

---

### Phase 3 -- Higher cost (run only if Phase 1+2 < 0.60 or oracle > 0.70)

**Anchor 11: HIERARCHICAL-N-3TIER-ENCODING**
- Anchor pointer: Path 2 in research note (Tier-1/2/3 with N_1=256, N_2=1024, N_3=4096)
- Substrate-product reading: Multiplicative capacity argument: K_total ~ 3.2 million vs
  K_flat ~ 148. New encoding architecture, not just a spreading modification. Requires
  defining 3-tier binding hierarchy for all FB15K-237 or WN18RR entities. Most
  implementation-intensive Phase 3 path but has the strongest theoretical capacity
  argument.
- Tier hint: remote_cpu_queue (4-6 hours implementation + 1 hour eval)
- Why now: after simpler capacity path (anchor 5, N scaling) establishes whether
  dimension alone helps or whether encoding STRUCTURE is needed.

**Anchor 12: SDM-SPARSE-CODING-SUBBAND**
- Anchor pointer: Path 8 in research note (Kanerva SDM with adaptive density)
- Substrate-product reading: Sub-band sparse coding for relation-type isolation. SDM capacity
  200x over dense VSA. Directly implements the compressed-sensing / sparse-coding field
  (Tier-1b per field advisor). Tests whether sparse encoding preserves the semantic
  similarity structure needed for analogy.
- Tier hint: remote_cpu_queue (4-6 hours; new SDM encoding code)
- Why now: test AFTER simpler N-scaling (anchor 5) establishes whether dimension-based
  capacity is useful at all.

**Anchor 13: CONTRASTIVE-W-MATRIX-UPDATE**
- Anchor pointer: Path 13 in research note (outer-product InfoNCE-style contrastive update)
- Substrate-product reading: Lowest-priority Phase 3 path. Engineering-intensive (training
  pass over FB15K-237 training split ~272K triples). Novel synthesis -- no VSA convergence
  theorem for outer-product contrastive updates. Ship only if all Phase 1+2+3 architectures
  achieve < 0.55 recall@1. Most likely to reveal fundamental W-update limitations.
- Tier hint: remote_cpu_queue (4-8 hours training + 1 hour eval)
- Why now: last resort mechanism. Ship only after exhausting anchors 1-12.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_slipnet_substrate_only_untested_paths_2x_2026-06-11.md
- Prior drill (rescue mechanisms): d:/AI/hd-instrument/notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
- Prior drill (alt rescues): d:/AI/hd-instrument/notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md
- Prior drill (refinement): d:/AI/hd-instrument/notes/research_drill_slipnet_refinement_2x_2026-06-10.md
- ConceptNet data: already loaded at testbed (8M edges, 458K facts -- testbed overnight chain)
- WN18RR: publicly available, https://github.com/villmow/datasets_knowledge_embedding
- FB15K-237: standard benchmark, Toutanova & Chen 2015 (use existing loading code)
- PP-346 context binding code: existing substrate code (achieves 1.000 on polysemy benchmark)
- Existing slipnet code: search notes for cycle-227 implementation anchor
- VSA capacity map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev commits to:
1. Running Phase 0 diagnostics (anchors 1+2) before ANY Phase 1-3 experiments.
2. Using Phase 0 results to prune the Phase 1-3 queue per the decision tree in the research note.
3. Pre-registering HARD-PASS / HARD-FAIL bands per the research note thresholds BEFORE each run.
4. Reporting the oracle-tag upper bound result as a cap on all subsequent P_deflated estimates.
5. NOT running all 13 paths in parallel without Phase 0 context -- that would waste queue cycles
   on mechanisms that Phase 0 rules out.

## Autonomy declaration

exp_dev AUTONOMOUSLY decides:
- Specific N, seed count, K, threshold bands for each cell
- Queue routing (local_cpu_queue vs remote_cpu_queue vs overnight_queue)
- Implementation details for each mechanism
- Whether to combine Phase 1 mechanisms into a single cell or run separately
- Anchor naming convention
- Whether Phase 2/3 anchors are worth dispatching given Phase 0+1 results
- How to implement the oracle-tag diagnostic (which relation-type key format to use)
- How to construct WN18RR loading code (adapter for existing slipnet infrastructure)
