# exp_dev hand-off -- research: slipnet real-polysemic rescue 2x

**Filed:** 2026-06-11 by research sub-agent.

**Trigger:** cycle-227 slipnet_real_polysemic MIDDLE_BAND recall@1=0.375, n=28 entities,
10 relation types. Research 2x drill completed.
Research note: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md

**Pause state:** check data/orchestrator_paused.flag before dispatching queue items.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Why now

Cycle-227 MIDDLE_BAND (0.375) is a SPECIFIC FIXABLE ARCHITECTURE GAP, not a capability limit.
The diagnosis is RELATION-TYPE CROSS-ACTIVATION INTERFERENCE: 10 relation types share the
same spreading activation pass, diluting each type's signal by ~5.5x SNR. The fix is
relation-type routing. Four substrate-native mechanisms are ranked below, each available
with existing code (no new data, no GPU). The cheapest (TTR, 5-line loop) can be run
in < 1 hour. Without this fix, all further slipnet scaling work is built on a broken
baseline. This is a blocking diagnosis.

---

## Anchor candidates (rank-ordered)

### 1. SLIPNET-TTR-SMOKE (Tier C, CPU -- dispatch first, lowest cost)
- Anchor pointer: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  Section E.4 TEMPORAL-RELTYPE-ROUTER + Section CHEAP DECISIVE TEST (T1)
- Substrate-product reading: implement the 5-line loop over 10 relation-type subgraphs,
  run spreading per type in sequence, take max-vote over type results. Apply to the
  cycle-227 dataset (28 entities, 10 typed edges). Compare recall@1 to MIDDLE_BAND
  baseline of 0.375. This is the lowest-overhead routing fix -- same algorithm, loop
  over types instead of one W_all pass.
- Tier hint: CPU, < 1 hour implementation + run. Pure numpy/sparse. No model loading.
  No new data required (cycle-227 data already exists).
- Why now: this is the minimal-code test of the routing hypothesis. If it passes smoke,
  all other routing mechanisms are validated as viable engineering directions.
- Pre-reg target: recall@1 > 0.72 (HARD-PASS as documented in research note). The
  2x improvement criterion over 0.375 baseline.

### 2. SLIPNET-N-SCALING-SMOKE (Tier C, CPU -- parallel with TTR)
- Anchor pointer: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  Section D.2 (N=1024 marginal for k=10 relation types) + CHEAP DECISIVE TEST N-scaling
  sub-test
- Substrate-product reading: run the CURRENT W_all spreading (no routing change) at
  N=4096. Zero new code -- just change the dimensionality parameter. Determines whether
  the MIDDLE_BAND result is an N-capacity bottleneck (marginal separation of 10 codes
  at N=1024) vs a routing bottleneck (no isolation regardless of N).
- Tier hint: CPU, < 30 min. The two tests (TTR + N-scaling) together discriminate
  the two failure modes in < 90 min total.
- Pre-reg target: recall@1 > 0.50 improvement at N=4096 vs N=1024 (if N-scaling helps,
  confirms N=1024 is marginal; if no improvement, routing is the dominant fix).

### 3. SLIPNET-TSE-FULL (Tier B, CPU -- after TTR smoke passes)
- Anchor pointer: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  Section E.1 TYPED-SLIPNET-ENSEMBLE + Section CHEAP DECISIVE TEST (T2)
- Substrate-product reading: build 10 independent sparse W_{r_j} stores (one per
  relation type). Run each in parallel. Max-vote readout integrates 10 channels.
  This is the production-grade routing architecture -- full cross-type isolation,
  no shared computation. Test on cycle-227, then on 100-entity extension.
- Tier hint: CPU, ~2-3 hours implementation. 10 sparse matrix stores; spread is
  parallelizable across types (if numpy, sequential; if torch, batched).
- Pre-reg target: recall@1 > 0.75 on cycle-227. If TSE passes: file as new
  production slipnet architecture (replaces W_all spread for heterogeneous-type
  graphs).
- Why after TTR: TSE requires more engineering. Confirm routing hypothesis first
  via TTR (30 min) before committing to TSE (2-3 hours).

### 4. SLIPNET-CGR-TAGGED (Tier B, CPU -- after TSE, tests context-gated path)
- Anchor pointer: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  Section E.2 CONTEXT-GATED-RELTYPE-ROUTING
- Substrate-product reading: bind the query with a relation-type key before spreading,
  suppressing cross-type edges via phase rotation. Requires explicit relation-type tags
  for each query (oracle tags from cycle-227 ground truth). Tests whether the PP-346
  binding mechanism directly rescues the slipnet spreading pathway.
- Tier hint: CPU, ~2 hours. Requires code-vector table (pre-compute 10 random unit
  hypervectors as relation-type keys; store as N x k matrix).
- Pre-reg target: recall@1 > 0.72 with oracle tags. If CGR matches TSE: use CGR as
  default architecture (cheaper per query if tags available). If CGR < TSE by > 0.10:
  Bind phase rotation insufficient for this graph topology; TSE is the better design.

### 5. SLIPNET-REAL-TYPED-100 (Tier B, CPU -- after any smoke passes, establishes North Star number)
- Anchor pointer: notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md
  Section SUBSTRATE-PRODUCT IMPLICATIONS "North Star connection"
- Substrate-product reading: scale the passing routing mechanism (TTR or TSE or CGR)
  to a 100-entity, 10-reltype benchmark with human-validated gold pairs. Compare to
  FAME's 77.8% baseline. This is the North Star data point: "substrate beats FAME
  without LLM call at 100x lower inference cost."
- Tier hint: CPU, ~3-4 hours including benchmark construction from ConceptNet data.
  ConceptNet 458K facts already in testbed.
- Pre-reg target: recall@1 > 0.75 on 100-entity benchmark (FAME-grade). HARD-PASS
  establishes the North Star claim.

---

## Context pointers (file paths, not summaries)

- notes/research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md -- this drill
- notes/research_drill_slipnet_refinement_2x_2026-06-10.md -- prior slipnet scaling drill
- notes/research_drill_cross_domain_real_polysemic_3x_2026-06-10.md -- OTF/GW/HCDR mechanisms
- notes/research_drill_polysemy_deep_3x_2026-06-10.md -- SAE guarantee, DMHN, neuromod gating
- notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md -- RotatE failure diagnosis
- notes/substrate_capability_map.md -- current cap_map; PP-327 slipnet row
- data/conceptnet*.jsonl (or equivalent) -- ConceptNet 458K facts; cycle-227 data nearby

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands from
  research note Section FALSIFIABLE PREDICTIONS BEFORE any smoke dispatch.
- Self-test per [[feedback-formula-selftests]]: verify per-type spreading produces expected
  activation isolation (inject at one type's node, confirm no activation propagates to
  other types' nodes) before running full eval.
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0.
- Ship via bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- status_log entry per anchor with plain_language + importance.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, seed count, exact threshold bands, queue choice,
ETA, smoke profile, FULL profile, sparse matrix library choice, how to construct type-
specific W matrices from cycle-227 data, how to implement the loop in TTR, whether to
use numpy vs torch sparse for TSE, how to pre-compute code vectors for CGR, what
"max-vote" aggregation means in implementation terms. The research note provides
mechanism + SNR math + P_deflated estimates; exp_dev owns all implementation decisions.

---

## Filed by

Research sub-agent, 2026-06-11, post cycle-227 MIDDLE_BAND reltype interference diagnosis.
