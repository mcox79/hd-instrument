# Pre-registration: exp_ingest_knowledge_integration_verify_v1

Date: 2026-07-07. Author: exp_dev. Stage: 0 (ingest arc). Anchor: `ingest_knowledge_integration_verify_v1`.
Source spec: `notes/research_ingest_arc_scoping_staged_plan_2026-07-07.md` (Item 4 + Item 5 Stage 0),
extended per Director/USER non-vacuousness directive (2026-07-07).

## Question

Can the substrate INTEGRATE + QUERY already-committed ConceptNet knowledge through the LIVE
structural query path (`backend.substrate_index.store.Store.out_neighbors`), such that a genuine
2-hop composition returns the correct integrated answer -- AND is that result NON-VACUOUS (the
real ingested edge structure is doing the work, not graph density, name similarity, or prior
substrate state)?

This is a PLUMBING / ADDRESSABILITY verification (the single largest untested item in the ingest
arc per the scoping drill: "Live-path addressability of the already-ingested ConceptNet content:
NEVER TESTED"). It is explicitly NOT a full-quality retrieval claim (retrieval quality is a later
gate). CPU-only. NO BGE re-encode (re-encode HELD, USER-locked): `Store` loads atoms + relations
only; `Retriever.rebuild_index()` (the BGE re-encode path) is NEVER called.

## Refinement of the drill spec (declared per contract)

The drill's Item 4 point 3 asked for semantic `recall@10` against the live BGE index. That path
requires either (a) a BGE re-encode over 133k+ atoms (VIOLATES re-encode-HELD, USER-locked), or
(b) wiring the content-hash BGE cache whose live-loader wiring the drill itself flags as
UNVERIFIED. Since the drill also explicitly DEFERS retrieval quality to a later gate, Stage 0 as
built tests the load-bearing integration+composition+addressability claim via the STRUCTURAL live
path (graph adjacency, zero vectors). The semantic-recall bar is deferred to a later stage. The
known-item round-trip recall (arm R) substitutes a re-encode-HELD-compliant addressability check.

## Arms (all persisted per-seed to metrics.json; PROOF is the GAP, not any absolute score)

| Arm | What | Expectation |
|---|---|---|
| A `ingest_2hop` | live 2-hop structural composition over REAL committed ConceptNet | HIGH (~1.0) |
| B `shuffled_2ndhop` | REAL graph, hop-2 relation randomized | COLLAPSE (~0) |
| C `scrambled_kb_2hop` | degree-preserving edge-target permutation, same probes | FAIL (~0) KEY null |
| C2 `no_ingest_2hop` | empty graph, same probes | ~0 sanity |
| D `encoder_only_nameNN` | char-trigram name-NN over {o}+199 distractors, NO graph | LOW (leak-check) |
| R `known_item_1hop` | round-trip live-path recall of ingested edges (`store.out_neighbors`) | ~1.0 addressability |
| L `one_hop_direct` | is o a 1-hop neighbor of s? (held-out chains) | ~0 not-lookup |

### Construction details
- 2-hop chains `(s,p1,x,p2,o)` sampled from real edges; HELD-OUT enforced: `o not in
  out_neighbors(s, any)` so the answer requires composing >=2 ingested edges (integration, not
  single-hop lookup). o != s, o != x, x != s.
- Scrambled-KB null (C): per relation type, permute the target column of that relation's edge
  list. Preserves per-(src,rel) out-degree and per-rel edge count EXACTLY; destroys the real
  (s,p,o) structure. If the 2-hop walk still reaches o under scramble, the "integration" was a
  density artifact -> VACUOUS.
- Encoder-only leak (D): predict o via char-trigram Jaccard name similarity to s among a pool of
  {o} + 199 random distractors (chance ~= 1/200 = 0.005). NOT BGE (no re-encode); a
  substrate-knows-nothing name proxy. If names alone recover o, that is a leak.
- Consistency assert: on a 20-chain sample the cached adjacency is checked against the LIVE
  `store.out_neighbors(s, RelationType(p1))` -- ties arms A/B/C to the live query path.

## Discriminator (pre-registered explicitly; USER directive)

| Gate | Definition | Band |
|---|---|---|
| D1 real-vs-scrambled | A - C | >= 0.50 |
| D2 firing-control | A - B >= 0.50 AND B | <= 0.15 |
| D3 no-ingest sanity | C2 | <= 0.05 |
| D4 encoder leak | D | <= 0.15 |
| D5 addressability | R | >= 0.98 |
| D6 not-lookup | L <= 0.05 AND A | >= 0.90 |
| D7 completeness | loaded_atoms == disk_atoms AND loaded_edges == disk_distinct + derived AND consistency | exact |

### Verdict
- **HARD_PASS**: all D1..D7 hold.
- **VACUOUS_NON_DISCRIMINATING** (NOT a pass): a control failed to fire -- C did not collapse, OR
  C2 not ~0, OR D leak, OR shuffled-hop did not collapse. Reported honestly as non-discriminating.
- **HARD_FAIL**: A < 0.50 OR R < 0.80 OR completeness breach (silent truncation).
- **MIDDLE_BAND**: addressability holds but a gate is partial.

## SCHEMA-VET mandatory fields

- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds (full = 3: {7,13,23}; smoke = 1: {7}).
  Seed axis only; no sweep axis. Verdict aggregates over seeds with n_chains>0.
- `arms_differ_verified`: true (hash-test on A/B/C hit-vectors; A distinct from nulls). B and C
  legitimately share the all-floor hash -- exempted pair (both are designed floor arms); the AF
  gate fires only if A==B==C.
- `final_metrics_atomicity`: `tmp_replace` (metrics.json + all partials written via .tmp +
  os.replace).
- `crlb_n/a`: "exact graph reachability; the discriminator is deterministic set membership over a
  loaded adjacency, not a continuous estimate against a noise floor. No Cramer-Rao bound applies."
- `discriminator_reachability`: true. A=1.0 is attainable by construction IF the live loader
  addresses every committed edge; the could-fail quantities (R<1.0 truncation, C>0 density
  artifact, D>0.15 name leak, completeness breach) are all genuinely uncertain until measured.
- `baseline_in_band` (META_RULE_AG): **EXEMPTED with rationale**. The null arms (B/C/C2/D) are
  DESIGNED to sit at floor and the ingest arm A at ceiling -- that separation IS the addressability
  claim. The genuinely-uncertain, could-fail discriminator is the GAP (A - C, A - B) plus the null
  floors themselves (a dense graph could lift C; lexical structure could lift D). So the standard
  "0.05 < baseline < 0.95" band does not apply; the non-vacuousness controls are what can fail.
- `calibration_check`: `default_ok_for_this_regime`. Bands are structural (exact-graph) thresholds,
  not inherited from vector-Hebbian benchmark cells; the noisy-vector 2hop>1hop+0.02 band from N8/U1
  is deliberately NOT reused (wrong regime: structural walk is exact).
- `HP_SCOPE`: {A: [D1,D2,D6], B: [D2], C: [D1], C2: [D3], D: [D4], R: [D5], completeness: [D7]}.
  Null arms are NOT held to the ingest-arm ceiling.
- `cell_chunked`: false. Justification: fast deterministic CPU cell (smoke 30.9s incl. 13.9s
  one-time store load); per-seed checkpoint/resume via atomic partial_seed files (sibling-cell N8
  precedent); a mid-run death loses at most the in-progress seed and resumes.
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED +
  traceback, atomic). `heartbeat_present`: n/a (per-seed wall < 20s; full total < ~3 min <<
  15-min heartbeat threshold; per-seed progress lines flushed).
- `defensive_error_checking`: "start_marker + crash_diagnostic + per-seed atomic checkpoint;
  heartbeat exempted (sub-15-min cell)".
- `progress_logging`: `print_flush_true` (all progress lines flush=True; not mandatory below
  timeout_s 1800 but declared).

## Compute architecture

- Class: **(b) sequential-CPU with justification**. The op is graph adjacency set-membership over
  a loaded dict; there is no matmul, no substrate-primitive batching opportunity, wall < ~3 min
  total. GPU batching is not applicable (no dense linear algebra).
- Storage strategy: **graph-native / no vector storage**. ConceptNet edges are stored as typed
  adjacency (sharded per (src, rel) key), the sharded-not-bundled default; composition is a
  graph walk, not a bundle unbind.

## §15 test-design gates

- `sweep_alignment_verdict`: ALIGNED (no parameter sweep; seed axis only).
- `discriminating_fraction`: n/a (no sweep axis). The single discriminator (gap A-C, A-B) is
  predicted >= 0.50 and MEASURED@smoke = 1.000.
- `composition_edges`: hop1 (out_neighbors s,p1) -> hop2 (out_neighbors x,p2). SHAPE_MATCH (both
  are `set[atom_id]` over the same id namespace).
- `positive_control_arms`: arm R (known-item 1-hop recall) reproduces the live `out_neighbors`
  round-trip AT THE TEST REGIME (the committed concept partition). MEASURED@smoke R=1.000.
- `functional_requirements`: (1) load committed ConceptNet into the live store without truncation
  -> completeness assert; (2) address an ingested edge via the live path -> arm R; (3) compose two
  ingested edges into an integrated answer -> arm A; (4) prove composition is genuine, not
  artifact -> arms B/C/C2/D.

## Numbers (tagged per META_RULE_AC)

- A_ingest_2hop = 1.000 MEASURED@d:/AI/hd-instrument/data/exp_ingest_knowledge_integration_verify_v1_smoke/metrics.json:per_seed[0].A_ingest_2hop
- B_shuffled = 0.000; C_scrambled = 0.000; C2_no_ingest = 0.000 MEASURED@same:per_seed[0]
- D_encoder_only_nameNN = 0.117 MEASURED@same:per_seed[0].D_encoder_only_nameNN (below 0.15 ceiling;
  ~23x chance -> honest lexical-shortcut signal; the closest gate; full run tightens the estimate)
- R_known_item_1hop_recall = 1.000; L_one_hop_direct = 0.000 MEASURED@same:per_seed[0]
- completeness: loaded_atoms 142219 == disk 142219; loaded_relations 189763 == 189654 + 109 derived
  MEASURED@same:disk_completeness
- chance floor for D (pool=200) = 0.005 THEORETICAL@1/N_POOL

## Dispatch plan

- Smoke: OFF-QUEUE local (`--smoke`, full committed graph, 1 seed x 60 chains). DONE, HARD_PASS.
  (local_cpu_queue is paused; smoke run directly per convention.)
- Full: `remote_cpu_queue`, 3 seeds {7,13,23} x 300 chains x 2000 known-item probes.
  Referent required on remote: `data/substrate_index/concept/{atoms,relations}.jsonl`.
  `--timeout 1200` (smoke 30.9s; store-load fixed ~14s + 3 seeds x ~10s + probe scaling; 1200s is
  ~4x-margin). Full has no GPU component (numpy-free graph walk; CPU-only). exp_dev cannot push;
  Orchestrator (hd_metrics_sync) commits + queues + REMOTE VERIFY.
