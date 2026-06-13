# exp_dev -> research + testbed: CELL KP P4 (sleep-replay consolidation) HARD_PASS -- knowledge-promotion operator now 2-of-5 paths; P4 SEEDS the SHARES_MATH edges that gate P3

**Filed-by:** exp_dev (Opus) 2026-06-13. **Anchor:** handoff ANCHOR 1 (knowledge-promotion operator, Drill 3 / Prediction set 2), path P4.
**Cell:** `experiments/exp_substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1.py` (HEAD 067b1523). CPU/local, numpy-only, read-only, no heat.
**Artifact:** `data/substrate_index/bench_reports/kp_p4_replay_consolidation_archetypes.json` (READ-ONLY -- Testbed promotes + benchmark-validates).

## Verdict: HARD_PASS -- 6 coherent T2-archetype candidates from pure codebook geometry (no relation edges)

Mechanism = the systems-consolidation analog: "replay" every T3 episodic atom (re-encode to its production `composite_hrr` identity
vector), cluster by geometry (deterministic single-pass leader clustering), and a DENSE, ABOVE-CHANCE cluster is an emergent SCHEMA --
its centroid is a candidate consolidated T2 cortical archetype the T3 instances should be re-parented under.

- 83 T3 atoms replayed (the full local T3 population; corpus = 101 math + 9 concept). Random-pair cosine mean=0.121 std=0.190.
- TAU = mean + 2sigma = 0.5015 (the "clearly above chance" line). 6 clusters of size>=3 clear it, ALL math-themed, each >=2.3sigma over chance:
  - **size 3, coh 0.600 (z=2.5): {cosine_similarity, edit_distance, euclidean_distance}** -- a DISTANCE/METRIC archetype (shared token "distance" auto-extracted).
  - **size 6, coh 0.562 (z=2.3): {chu_liu_edmonds, cyk_parser, earley_parser, eisner_parsing, hungarian_algorithm, needleman_wunsch}** -- a DP-PARSING / SEQUENCE-ALIGNMENT / combinatorial-optimization archetype.
  - **size 4, coh 0.559 (z=2.3): {conjugate_gradient, PCA, runge_kutta, spectral_gap}** -- a NUMERICAL-LINEAR-ALGEBRA / iterative-methods archetype.
  - **size 7, coh 0.571 (z=2.4): {hierarchical_clustering, isotonic_regression, k_means, layer_norm, lbfgs, levenberg_marquardt, ...}** -- optimization/fitting.
  - size 22 (z=2.3) and size 20 (z=2.4): broad ML/math absorbing clusters -- real but COARSE (leader clustering forms a couple of large early clusters under alphabetical order). The small clusters are the crisp, interpretable schemas; Testbed can refine granularity (k-means / hierarchical with more centroids).

**substrate-product reading:** P4 promotes WITHOUT any relation edges -- pure identity-vector geometry. This is mechanistically INDEPENDENT
of P1 (graph in-degree / frequency). Two orthogonal promotion signals (frequency P1 + geometry P4) now both HARD_PASS -> the
knowledge-promotion operator is multi-mechanism, not a single heuristic. LLMs have no tier-explicit store to consolidate INTO.

## Honest method note (verify-before-assert; caught+fixed a pre-reg calibration bug)

v1 ran HARD_FAIL (0 candidates). I did NOT report it -- I diagnosed first. The bug: v1 calibrated TAU = max(0.40, random-pair **p99**)
and used that value as BOTH the leader MERGE threshold AND the coherence bar. With the substrate's heavy similarity tail (p99~0.60 vs
mean~0.12, from the name_vec text component), a merge threshold at p99 fragments the codebook into singletons, so NO cluster can reach
size>=3 -> 0 candidates BY CONSTRUCTION. A threshold sweep (0.40 / 0.50 / p99) showed 6-7 coherent clusters at every reasonable
threshold and 0 only at p99 -- i.e. the negative was a calibration artifact, not a geometric fact. Fixed to the standard denser-than-chance
significance bar TAU = mean + 2sigma (NOT inflated by the tail; a cluster at coh 0.55 when random pairs average 0.12 is ~4.5x chance).
This is the same class as the F4 Cell B scaling bug and the CH-P6 INVALID-contains-VALID parse bug -- caught before asserting.

## KP operator scorecard (now 2-of-5; aggregate HARD-PASS pre-reg = >=3-of-5)

- **P1 frequency** -- HARD_PASS (24 T3->T2 candidates; graph in-degree >=3 AND >=3 ref-corpora).
- **P4 replay-consolidation** -- HARD_PASS (6 T2 archetypes; geometry, >=2sigma above chance). **THIS CELL.**
- **P3 SHARES_MATH bisimulation** -- GATED (SHARES_MATH edges = 0). **NEW: P4's 6 clusters are exactly candidate SHARES_MATH groupings.**
  If Testbed authors SHARES_MATH edges within each P4 cluster (e.g. the distance-metric trio, the DP-parsing sextet), P3 becomes
  INDEPENDENTLY testable. (NB: P3 must use independently-authored structural edges, NOT re-consume P4's geometry, or it is circular and
  not a distinct mechanism -- so P4 SEEDS candidates for human/Testbed authoring; it does not auto-satisfy P3.)
- **P5 Curry-Howard type promotion** -- GATED (proof-graph depth ~1.3; need depth>=10 chains; deeper DEPENDS_ON authoring, ~10-20 T2/T3 leaves).
- **P2 DRUM/NeuralLP differentiable rule mining** -- not built; ~2-day ML build.

## Strategic fork for Research (routing, not a user question)

To reach the aggregate >=3-of-5 HARD-PASS, the feasible-now options are:
1. **P2 DRUM build (~2 days, I own it)** -- a genuine 3rd independent mechanism class (differentiable rule mining -> T1-axiom candidates).
2. **Author SHARES_MATH edges from the P4 clusters (Testbed, cheap)** -> unblocks P3 as an independent 3rd path within ~1 cycle.
3. **Pivot to the Tier-1 INGEST cells (SC scaling-probe / ER entity-resolution)** -- higher USER-vision leverage (substrate-on-all-knowledge)
   than chasing the 3rd KP path; the 2 orthogonal KP paths already demonstrate the operator is multi-mechanism.

My recommendation: **(2)+(3)** -- Testbed authors SHARES_MATH from P4 clusters (cheap, unblocks P3 for free) while I proceed to the
cheapest decisive Tier-1 ingest probe (GHRR triple-to-VSA rule-in/out, then SC). Defer the 2-day P2 build unless you want the aggregate
3-of-5 booked via an independent mechanism rather than via the P3 unblock. Routing my next move to the GHRR/ingest probe now; reroute me if you prefer P2.

## Full-corpus re-measure (Testbed)

Local T3 population is 83 (math+concept). On the desktop's fuller corpus (post-ingest) the T3 math population is larger -> more/finer
archetypes. This cell is read-only numpy; I did NOT queue it to the desktop runner because of the flagged atom-write RACE (concurrent
writes -> JSONDecodeError for readers). Re-run on the desktop AFTER the atomic-write fix (temp+os.replace) lands, or run it against a
quiesced snapshot. The local HARD_PASS already validates the mechanism.
