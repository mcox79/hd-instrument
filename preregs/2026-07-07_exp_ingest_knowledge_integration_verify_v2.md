# Pre-registration: exp_ingest_knowledge_integration_verify_v2 (gate-D hardening)

Date: 2026-07-07. Author: exp_dev. Stage: 0 (ingest arc, INTEGRITY gate). Anchor:
`ingest_knowledge_integration_verify_v2`. Amends: `exp_ingest_knowledge_integration_verify_v1`.
Source spec: `notes/ingest_gate_d_per_seed_regate_anti_lexical_control_spec_2026-07-07.md`;
Test-0 lexical surface: `notes/research_970k_kb_near_duplicate_density_test0_2026-07-07.md`.

## Question

v1 FULL passed gate-D (encoder-only lexical-leak control) only on the MEAN
(D=0.148 < 0.15 ceiling) while 2 of 3 seeds INDIVIDUALLY exceeded 0.15
(per-seed [0.130, 0.157, 0.157] MEASURED@data/exp_ingest_knowledge_integration_verify_v1/metrics.json:per_seed[*].D_encoder_only_nameNN;
max 0.1567). That is a Goodhart signature with zero scale headroom, and the leak grew smoke->full.
This is the ingest-INTEGRITY gate that must clear before any 970K scale. Two independent, cheap
fixes:

- **Fix 1 (per-seed gate):** gate on max-over-seeds of the hardened gate-D, NOT the mean. Removes
  mean-masking.
- **Fix 2 (stronger anti-lexical pool):** v1 drew the encoder-only candidate pool from RANDOM
  nodes, so the name-NN arm only had to beat lexically-UNRELATED names. Harden it: build the
  distractor pool from the answer entity o's NEAREST LEXICAL NEIGHBORS (char-trigram Jaccard on the
  entity name), so the arm must distinguish the true answer from names that LOOK alike. Pool size
  matches the v1 negative count (o + 199 = 200) so the chance rate is unchanged (1/200 = 0.005);
  only the DIFFICULTY changes (base rate controlled per paired-trials + base-rate disciplines). This
  is the ConceptNet entity-name analog of Test-0's near-duplicate lexical-shortcut surface.

Everything else (arms A ingest / B shuffled-hop / C scrambled-KB / C2 no-ingest / R known-item / L
one-hop; completeness; consistency) is UNCHANGED from v1. re-encode HELD (committed ConceptNet,
zero new ingest, zero encoder forward calls). CPU-only.

## Arms (3 D-variants computed in the SAME run; PROOF is the A-D gap on the HARDER pool)

| Arm | What | Expectation |
|---|---|---|
| A `ingest_2hop` | live 2-hop structural composition over REAL committed ConceptNet | ~1.0 |
| B `shuffled_2ndhop` | REAL graph, hop-2 relation randomized | ~0 |
| C `scrambled_kb_2hop` | degree-preserving edge-target permutation | ~0 KEY null |
| C2 `no_ingest_2hop` | empty graph | ~0 sanity |
| **D_hard `D_hard_lexNN`** | **GATED gate-D**: pool = {o} + 199 lexical-NN of o; ranked by name-sim to s | LOW (target) |
| D_random `D_random_pool` | v1 semantics: pool = {o} + 199 RANDOM; same unbiased scoring | continuity ref |
| D_hardscr `D_hard_scrambled_src` | firing control: hard pool, SOURCE name replaced by random node | ~chance 0.005 |
| R `known_item_1hop` | round-trip live-path recall | ~1.0 |
| L `one_hop_direct` | is o a 1-hop neighbor of s? (held-out) | ~0 |

### Construction details (only gate-D changed vs v1)
- Lexical-NN pool: char-trigram inverted index over the FULL 142k node set; per query, top-199 by
  Jaccard to o, excluding s and o; padded with random nodes only if <199 neighbors exist (recorded
  as `mean_lex_neighbors_available`).
- **Unbiased tie-break:** each pool is SHUFFLED before argmax and the answer's shuffled position is
  scored, so lexically-identical lookalikes (common in the hard pool) do NOT bias the answer by its
  list index. (v1 scored `argmax==0` with the answer at index 0, which inflates on ties.)
- Firing control (Fix 2 validity): replace the source name with a random node's name (name->code
  map shuffled on the source side). If D_hard measures a genuine s->o lexical shortcut (not a
  pool-construction artifact), D_hardscr MUST collapse to chance.

## Discriminator (BOTH bands pre-registered BEFORE the FULL run)

Structural gates (unchanged from v1): D1 `A-C >= 0.50`; D2 `A-B >= 0.50 AND B <= 0.15`;
D3 `C2 <= 0.05`; D5 `R >= 0.98`; D6 `L <= 0.05 AND A >= 0.90`; D7 completeness+consistency exact.

Hardened gate-D (D4), evaluated on the per-seed `D_hard_lexNN` with the firing control as a validity
precondition:

| Outcome | Condition |
|---|---|
| **HARD-PASS** | `max_over_seeds(D_hard) < 0.15` (EVERY seed) AND firing `mean(D_hardscr) <= 0.02` AND all structural gates hold |
| **MIDDLE_BAND** | firing OK AND `0.15 <= max(D_hard) < 0.17` AND `max(D_hard) <= 0.1567` (did not grow vs current FULL) -- honest bounded ~0.85 non-vacuousness |
| **HARD-FAIL (`HARD_FAIL_LEXICAL_LEAK`)** | firing OK AND (`any seed D_hard >= 0.17` OR `max(D_hard) > 0.1567` i.e. leak grew vs current FULL). Core integration still CG; the honest leak bound has no scale headroom |
| **VACUOUS_NON_DISCRIMINATING** | firing control did NOT collapse (`mean(D_hardscr) > 0.02`) -> hard pool carries a non-lexical artifact, D_hard untrustworthy; OR a structural control failed |
| **HARD_FAIL** (plumbing) | `A < 0.50` OR `R < 0.80` OR completeness breach |

Strategic read: if A holds while D_hard DROPS on the harder pool, the A-D gap WIDENS (stronger
non-vacuousness proof than v1's 0.85). If D_hard stays high, the ~15% name-shortcuttable fraction is
genuinely real and we report the honest bounded number. Either way we learn the TRUE value.

## SMOKE RESULT (multi-seed gate; all 3 FULL seeds at reduced chains) -- HARD_PASS

MEASURED@data/exp_ingest_knowledge_integration_verify_v2_smoke/metrics.json (seeds {7,13,23} x 100 chains):
- A=1.000 B=0.000 C=0.000 C2=0.000 L=0.000 R=1.000 (all seeds); completeness+consistency True.
- `D_hard_lexNN` per-seed = [0.0200, 0.0300, 0.0300]; max=0.0300 (<< 0.15; clears by 80% of band).
- `D_random_pool` per-seed max=0.2800 mean=0.1633 (reproduces the v1 random-pool leak; noisier at n=100).
- firing `D_hard_scrambled_src` mean=0.0033 max=0.0100 (<= 0.02; collapses to chance -> D_hard valid).
- worst-seed A-D gap = 0.970 (WIDENED vs v1's ~0.85). `mean_lex_neighbors_available` = 199.0 (full hard pool).
- Verdict: HARD_PASS. GOOD case realized: the harder pool DROPS the leak, gap widens.

Multi-seed smoke satisfies the leak/contamination-cell discipline (per-seed spread observed before
FULL): all three seeds land at 0.02-0.03, far below ceiling; regression-to-mean risk is toward
LOWER, not higher, so full dispatch is safe.

## SCHEMA-VET mandatory fields

- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds (full=3 {7,13,23}; smoke=3). Seed axis only.
- `arms_differ_verified`: true (hash-test: A/B/C distinct; **Dhard distinct from Drand** -- else Fix
  2 did nothing -> the cell raises AssertionError). B/C legitimately share the all-floor hash
  (exempted pair, both designed floor arms); AF gate fires only if A==B==C.
- `final_metrics_atomicity`: `tmp_replace` (metrics.json + all partials via .tmp + os.replace).
- `crlb_n/a`: "exact graph reachability + argmax over a bounded name-similarity pool; deterministic
  set membership + Jaccard ranking, not a continuous estimate against a noise floor. No Cramer-Rao
  bound applies."
- `discriminator_reachability`: true. HARD-PASS target `max D_hard < 0.15` is attainable (smoke
  max=0.030 MEASURED). The could-fail quantity is genuinely uncertain (D_hard could rise at n=300,
  or the firing control could fail to collapse).
- `baseline_in_band` (META_RULE_AG): **EXEMPTED** -- null/D arms are DESIGNED to sit at floor and A
  at ceiling; that separation IS the claim. The genuinely-uncertain discriminator is the per-seed
  max D_hard + the firing-control collapse.
- `calibration_check`: `default_ok_for_this_regime`. Bands are structural / rate thresholds on
  exact-graph + name-Jaccard, not inherited from vector-Hebbian benchmark cells.
- `HP_SCOPE`: {A: [D1,D2,D6], B: [D2], C: [D1], C2: [D3], D_hard: [D4], D_hardscr: [D4-firing],
  R: [D5], completeness: [D7]}. Null/continuity arms not held to the ingest-arm ceiling.
- `cell_chunked`: false. Fast deterministic CPU cell (smoke 3 seeds incl. store load ~12s total);
  per-seed atomic checkpoint/resume; a mid-run death loses at most the in-progress seed.
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED +
  traceback, atomic). `heartbeat_present`: n/a (per-seed wall < 15s; full total << 15-min threshold;
  per-seed progress lines flushed).
- `defensive_error_checking`: "start_marker + crash_diagnostic + per-seed atomic checkpoint;
  heartbeat exempted (sub-15-min cell)".
- `progress_logging`: `print_flush_true` (all progress lines flush=True; timeout_s 1200 < 1800 so
  not mandatory, declared anyway).

## Compute architecture

- Class: **(b) sequential-CPU with justification**. Graph adjacency set-membership + a char-trigram
  inverted-index NN (Counter over postings, argpartition top-k); no matmul, no dense linear algebra,
  no substrate-primitive batching opportunity; full wall << 15 min. GPU not applicable (numpy/no
  torch -> overnight_queue would be routing-REJECTED by queue_add.sh's no-torch gate; correct route
  is remote_cpu_queue).
- Storage strategy: **graph-native / no vector storage** (sharded typed adjacency; composition is a
  graph walk, not a bundle unbind).

## Numbers (tagged per META_RULE_AC)

- v1 FULL max-over-seeds random-pool leak = 0.1567 MEASURED@data/exp_ingest_knowledge_integration_verify_v1/metrics.json:per_seed[*].D_encoder_only_nameNN (the "current FULL" HARD-FAIL reference)
- v2 smoke D_hard per-seed = [0.0200, 0.0300, 0.0300] max=0.0300 MEASURED@data/exp_ingest_knowledge_integration_verify_v2_smoke/metrics.json:per_seed[*].D_hard_lexNN
- v2 smoke firing mean=0.0033 MEASURED@same:per_seed[*].D_hard_scrambled_src
- v2 smoke A=1.000 R=1.000 MEASURED@same
- chance floor for the leak (pool=200) = 0.005 THEORETICAL@1/N_POOL
- firing-control chance = 1/200 = 0.005; FIRING_CEIL 0.02 = ~4x chance (margin) THEORETICAL

## Dispatch plan

- Smoke: OFF-QUEUE local (`--smoke`, full committed graph, 3 seeds x 100 chains). DONE, HARD_PASS.
- Full: `remote_cpu_queue`, 3 seeds {7,13,23} x 300 chains x 2000 known-item probes.
  Referent required on remote: `data/substrate_index/concept/{atoms,relations}.jsonl` (present; v1
  FULL ran there). `--timeout 1200` (smoke ~12s total incl. ~3s store load; full ~3x chains + ~5x
  known-item ~ <90s; 1200s is >13x margin). No GPU (numpy graph walk; CPU-only). SCP-based
  dispatch via `tools/orchestrator/queue_add.sh` (no origin push needed); post-ship verify (exit 5
  = ship FAIL). On landing -> XHIGH skunkworks VET.

## v2.1 FIX AMENDMENT (deterministic FULL crash + SMOKE!=FULL coverage gap; 2026-07-07)

Prior v2 FULL (commit c39dd3ba7) crashed deterministically ~0.0s into seed 7 on remote_cpu_queue:
`KeyError: 'math::T3/hungarian_algorithm'` at run_seed `si = node_index[s]`.

- ROOT CAUSE (MEASURED@live concept graph): the concept relations file references 93 cross-corpus
  edge endpoints (e.g. `math::T3/hungarian_algorithm`) whose atoms live in another partition and are
  absent from the concept store's `all_atom_ids()`; every USES edge auto-derives a HAS_USERS reverse
  edge (store._load_from_disk), making 31 of those dangling nodes appear as chain SOURCES in real_out.
  `node_index` was built from `all_atom_ids()` alone -> `node_index[s]` KeyError. SMOKE (100 chains)
  never sampled a dangling-rooted chain; FULL (300 chains, seed 7) did -> SMOKE!=FULL slip.
- FIX 1 (crash): node universe = atoms UNION every edge endpoint (build_adjacency, sorted for
  determinism). Guarantees every edge source AND target is indexable; drops NO edge/content -> gate-D
  and structural arms UNCHANGED. MEASURED@ post-fix smoke: D_hard per-seed=[0.020,0.000,0.030]
  max=0.030, A-D worst=0.970, firing max=0.000 (identical good-case behavior to pre-crash smoke).
- FIX 2 (smoke-gap closure): a GRAPH-CONSISTENCY GATE runs IDENTICALLY in smoke and full BEFORE any
  chain sampling, asserting every edge endpoint is in node_index. Converts the sample-lottery latent
  crash into a deterministic construction-time gate. PROVEN load-bearing: pre-fix (atoms-only) index
  -> gate finds 93 missing -> smoke RAISES; post-fix (union) -> 0 missing -> smoke passes.
  disk_completeness now logs `n_dangling_edge_only_nodes` (=93) for visibility.
- Self-test extended with the union/dangling-coverage case; grep-gate (no bare/BaseException) PASS.
