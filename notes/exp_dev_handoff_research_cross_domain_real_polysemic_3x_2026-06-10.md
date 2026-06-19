# exp_dev hand-off -- research: cross-domain real-polysemic analogy 3x

**Filed:** 2026-06-10 by research sub-agent (3x depth drill, 5-stream parallel scan)

**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_cross_domain_real_polysemic_3x_2026-06-10.md

**Pause state:** Check `data/orchestrator_paused.flag` before queueing any anchor.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding in one line

Substrate can perform cross-domain relational analogy on real polysemic concepts (justice/ecology)
using OVERLAY-THEN-FILTER (OTF) as the highest-probability mechanism (P_empirical=0.28 pre-test);
the barrier is the DISAMBIGUATION COMMITMENT PROBLEM, not representational capacity.

---

## Anchor candidates (rank-ordered, highest to lowest confidence)

### Anchor 1 -- OTF cross-domain relational recall (OVERLAY-THEN-FILTER)
- **Anchor pointer:** Research note Section E.1 + Cheap decisive test (20-pair justice/ecology benchmark)
- **Substrate-product reading:** If OTF recall@1 > 0.50 on the held-out 20-pair set, substrate has a new
  capability claim: "analogical memory -- cross-domain relational reasoning with algebraic audit trail."
  This does NOT require any new substrate operations, only multi-sense encoding + cross-store inner product.
- **Tier hint:** LOCAL CPU (pure numpy/torch, no GPU needed, N=8192, ConceptNet data, 2-4 hr runtime)
- **Why now:** R10 K=512 HARD-PASS already validates that representational capacity is sufficient.
  OTF is the minimal experiment -- 1-2 days engineering, verifies whether the disambiguation mechanism
  works before investing in the more expensive GW or SML variants.
- **Pre-registration:** HARD-PASS = recall@1 > 0.50 on 20-pair set. HARD-FAIL = recall@1 < 0.25 all mechanisms.

### Anchor 2 -- HCDR cross-domain replay schema extraction
- **Anchor pointer:** Research note Section E.10 (HEBBIAN-CROSS-DOMAIN-REPLAY)
- **Substrate-product reading:** Cross-domain replay is algebraically identical to within-domain replay
  (already validated, PP-82 HP). Extending to two separate source stores tests whether the biological
  REM-sleep cross-domain schema-induction mechanism translates to substrate. Low engineering risk.
- **Tier hint:** LOCAL CPU (pure substrate operations, no external data needed, smoke in <1 hr)
- **Why now:** HCDR requires only existing substrate operations -- bundle, store, cleanup -- on two
  separate domain stores. Can be smoked immediately without ConceptNet data pipeline.
- **Pre-registration:** HARD-PASS = extracted skeleton inner product with gold relational pattern > 0.65.
  HARD-FAIL = skeleton inner product with any valid analogy pair < 0.5 (noise level).

### Anchor 3 -- GW-OPTIMAL-TRANSPORT cross-domain alignment (GWOTA)
- **Anchor pointer:** Research note Section E.3 + Stream D (GW-OPTIMAL-TRANSPORT-DOMAIN-ALIGN)
- **Substrate-product reading:** Gromov-Wasserstein transport plan finds optimal relational matching
  between two metric spaces. If GWOTA top-1 transport matches > 12/20 human-validated analogies,
  this provides a polysemy-robust cross-domain similarity score independent of surface features.
  Applicable to cross-silo enterprise KB insight generation.
- **Tier hint:** REMOTE CPU (requires Python Optimal Transport (POT) library, O(n^3) on n=100 concepts,
  ~5 min per domain pair, but needs setup)
- **Why now:** GWOTA is the theoretically cleanest mechanism (GW distance has known convergence
  guarantees). Worth running in parallel with OTF after OTF smoke completes.
- **Pre-registration:** HARD-PASS = top-1 GW transport matches >12/20. HARD-FAIL = matches <6/20.

### Anchor 4 -- SML iterative slippage improvement probe
- **Anchor pointer:** Research note Section E.2 (SLIPNET-MULTI-LAYER)
- **Substrate-product reading:** Tests whether iterative cleanup with directed perturbation (Hofstadter
  slippage) improves recall over single-shot query. If yes, this opens a search mechanism over
  polysemy space that can generalize beyond the specific analogy benchmark.
- **Tier hint:** LOCAL CPU (requires ConceptNet concept proximity graph, iterative cleanup loop)
- **Why now:** Run AFTER OTF result is in hand. If OTF already achieves recall@1 > 0.50, SML is an
  enhancement. If OTF fails, SML is the first rescue path.
- **Pre-registration:** HARD-PASS = SML improves recall@1 by >0.10 absolute over OTF single-shot.
  HARD-FAIL = SML degrades recall (polysemy space not structured enough for directed search).

### Anchor 5 -- UCD universality class detector (free-probability + Laplacian RG)
- **Anchor pointer:** Research note Section E.5 (UNIVERSALITY-CLASS-DETECTOR) + adjacency to
  Tier-1 free-probability drill (F4 in field advisor)
- **Substrate-product reading:** Apply Laplacian RG coarse-graining to ConceptNet subgraphs for
  biology/ecology and justice/freedom. If coarse-grained eigenspectra converge to similar profiles,
  the domains are structurally analogous at scale -- a quantitative, polysemy-robust measure.
  This ALSO closes F4 (free cumulants / Voiculescu kappa_n) as a field drill, addressing the
  Tier-1 underdrill flagged by the field advisor.
- **Tier hint:** REMOTE CPU (networkx + scipy eigendecomposition, ~1 day setup + 1 hr run)
- **Why now:** Kills two birds: tests UCD cross-domain mechanism AND addresses Tier-1 field-advisor gap.

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_real_polysemic_3x_2026-06-10.md
- Substrate capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- R10 K=512 HARD-PASS evidence: see cap_map row "R10 concept fusion at K>=8"
- PP-82 counterfactual replay HARD-PASS: see cap_map row reference
- Field advisor output: run `python d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py`
- Testbed data pipeline (ConceptNet extraction): d:/AI/hd-instrument/notes/testbed_post_compaction_brief_2026-06-09_overnight_chain.md (ConceptNet 8M = 458K facts already extracted)

---

## Contract

exp_dev owns ALL experimental design decisions: N, K, seed count, threshold bands,
queue routing, anchor naming, timing. This hand-off provides WHAT to test and WHY,
not HOW to test it numerically.

If the LOCAL CPU queue is at capacity, sequence: HCDR smoke first (pure substrate,
no external data), then OTF (requires ConceptNet data), then GWOTA (requires POT setup).

If any anchor achieves HARD-PASS, escalate to research for: (a) capability claim
wording, (b) production-scale parameter design (larger N, larger concept vocabularies),
(c) integration with existing PP rows in cap_map.

If all anchors achieve HARD-FAIL (recall@1 < 0.25): the failure is in the ConceptNet
encoding sparsity. Escalate to research with finding: "ConceptNet relational triples
are too sparse for VSA encoding; need LLM-derived relational embeddings as source."

---

## Autonomy declaration

exp_dev has full autonomy to:
- Choose which anchors to queue in which order
- Determine smoke vs full profile per Tier A/B/C policy
- Skip any anchor if capacity or time constraints require prioritization
- Redesign the 20-pair benchmark if the ConceptNet extraction reveals data quality issues
- Add intermediate diagnostic anchors not listed here if OTF fails for non-obvious reasons
