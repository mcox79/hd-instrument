# Pre-reg: exp_ingest_knowledge_livepath_verify_v1 (LIVE-PATH INGESTION VERIFY PILOT)

Date: 2026-07-05. Author: hdi_exp_dev. Origin: USER 5x-drill angle-4
(`notes/research_ingestion_readiness_scoped_pilot_5x_angle4_2026-07-05.md`).
Cell: `experiments/exp_ingest_knowledge_livepath_verify_v1.py`.
Prior-work check (substrate_query.sh, concept keywords): top hit cosine=0.2676 (< 0.30 threshold)
= NONE at cosine>0.30. Genuinely novel cell (live-path verify of already-held ConceptNet;
no prior arc cell exercises Retriever.semantic/structural over the committed ConceptNet content).

## Question
Can the substrate live-reason over REAL KNOWLEDGE IT ALREADY HOLDS (ConceptNet, ~133k
CONCEPT_NODE atoms committed 2026-06-19) through the LIVE operational retriever path
(`Retriever.semantic()` + `Retriever.structural()`), NOT an isolated numpy harness?
NO new ingest, NO re-encode. READ-ONLY on the canonical store.

## Honest framing (USER-LOCKED)
Verifies LIVE-PATH USABILITY of already-held knowledge. NOT new ingest; NOT a language-capability
claim. The live 2-hop mechanism = BGE semantic-addressing + structural edge-composition. This is a
DIFFERENT mechanism/regime than U1 (`exp_u1_fb15k237_ingest_eval_v1`, CHAIN_GRADE, isolated
HD-algebra Hebbian store over FB15k-237). We reproduce U1's QUALITATIVE bar (real signal >> random
floor + fabrication-refusal) through the live path, NOT U1's exact numbers.

## Two phases
- **Phase A** (full-store addressability/collision/cache-wiring audit, read-only, ~6s): id_order =
  `[a.id for a in PartitionedStore.all_atoms()]` (exactly what `Retriever.rebuild_index` /
  `retrieve_cache` use); cross-partition bare-id collision count (the 1500->1497 concern at 177k
  scale); collisions restricted to CN_ namespace; which live cache `retrieve_cache._cache_path`
  resolves + whether it EXISTS (settles "is the qualified-id fix wired into the live path?").
- **Phase B** (live retriever round-trip + 2-hop over a real ConceptNet subgraph): deterministic
  seed-anchored subgraph (2-hop IS_A seeds + neighborhoods + random concept distractors) built into
  the CELL's own dir (cache isolated; no canonical pollution). Round-trip known-item recall@1/@10 by
  exact name + correct-id rate; refuse-gate cosine separation (known vs fabricated queries); 2-hop
  semantic-address + structural-compose vs 1-hop baseline vs random-target floor + fabrication-refusal.

## Bands (locked)
- **HARD-PASS**: `collision_safe_cn` (0 collisions in CN namespace) AND `round_trip_recall@10 >= 0.80`
  on `>= 0.90` of probes AND `correct_id_rate >= 0.95` AND `twohop_true_recall > onehop_baseline + 0.02`
  AND `twohop_true_recall >= 20x random_floor`.
- **HARD-FAIL**: `round_trip_recall@10 < 0.40`, OR `correct_id_rate < 0.60` (wrong concepts / collision),
  OR `twohop_true_recall <= random_floor` (compose collapses), OR `twohop_fabrication_accept > 0.30`.
- **MIDDLE-BAND**: otherwise.
- **Cache-wiring (Phase A) is a first-class REPORTED finding, NOT a gate** on the Phase-B mechanism
  PASS/FAIL: Phase B builds its own subgraph index so it measures the retrieval mechanism independent
  of whether the canonical full-store cache is wired.

## Discriminator honesty (load-bearing; no-smoke)
- **Non-vacuous discriminators** (carry the verdict): (1) `round_trip_correct_id_rate` over a real
  BGE index (collision-sensitive; drops if collisions return wrong atoms); (2) Phase-A full-scale
  collision audit (real measurement); (3) `refuse_separation` (BGE accept-vs-fabricated, stochastic);
  (4) Phase-A cache-wiring (decisive operational finding).
- **Near-by-construction / plumbing-correctness** (VERIFY, not chain-grade reasoning): `twohop=1.0` /
  `onehop=0.0` (chain selection excludes 1-hop-reachable targets; structural-compose is deterministic
  graph-walk); `twohop_fabrication_accept=0.0` (structural-compose returns only stored-edge
  reachables, cannot fabricate). Reported honestly as "live path composes 2 stored hops correctly +
  does not fabricate edges", NOT as a noisy-reasoning discriminator.

## SMOKE result (MEASURED@data/exp_ingest_knowledge_livepath_verify_v1_smoke/metrics.json 2026-07-05)
- verdict=HARD_PASS, elapsed=92.2s (BGE model load ~44s dominated), run_mode=smoke.
- Phase A (real canonical store, same branch as full): n_atoms=177872, n_collisions=1, n_cn_dup=0,
  collision_safe_cn=True; live_cache_hit=**False** (resolves `bge_large_v2_name_177872_c1f5fc5d.npz`
  = MISS; on-disk full cache is `..._177899_54f7cf6a` = 27-atom stale; `qualified_*` collision-safe
  caches present but NOT selected by retrieve_cache glob).
- Positive control: injected CN dup detected -> detector fires (collision_safe_cn=False when injected).
- Phase B (N_INDEX=400): index_complete_no_collision_loss=True; recall@1=1.0, recall@10=1.0,
  correct_id_rate=1.0; refuse_separation=0.1276 (accept 0.8394 vs fab 0.7118); twohop=1.0 vs
  onehop=0.0 (400x floor 0.0025); fab_accept=0.0.

## Compute architecture
- Class: **(b) sequential-CPU with justification.** The live retriever path uses the production
  BGE-large encoder which is CPU-pinned by design (`backend/llm/bge_encoder.py` DEFAULT_DEVICE=cpu,
  "keeps GPU clear for experiments"). Retrieval is a single `matrix @ q` (numpy BLAS, not a batchable
  GPU sweep). Wall time dominated by one-time BGE encode of the subgraph (N_INDEX atoms) + model load.
  No GPU batching applies (no independent-phase-point sweep; the cell IS the live operational path).
- **Storage strategy: sharded (read-only).** The store is per-atom sharded (each atom + its edges is
  its own record); 2-hop is structural edge-walk over stored per-atom edges, NOT bundled superposition
  (correct per META_STORAGE_STRATEGY_COMPOSITION_DEPTH). The cell stores no new/composed items.

## SCHEMA-VET fields
- `cardinality_ok: true` — EXPECTED_N_UNITS = fixed (Phase A: 1 full-store audit; Phase B: N_PROBE
  round-trip + N_2HOP chains + N_REFUSE fab). Not a sweep-axis cell; verdict counts probes/chains and
  divides by actual N (no phantom-completion path).
- `arms_differ_verified: true` — onehop vs twohop reachable sets differ by construction (asserted:
  target excluded from onehop); round-trip / refuse / 2-hop are distinct measurement functions.
- `final_metrics_atomicity: "tmp_replace"` — metrics.json written via tmp + os.replace (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` (NO BaseException, NO bare except) — grep-gate clean.
- `crlb_n/a: "no quantitative noise-floor mechanism; retrieval recall + graph-walk are not
  Cramer-Rao-bounded estimators"`. Capacity-feasibility: recall@10 HP=0.80 is achievable (exact-name
  BGE retrieval; smoke measured 1.0); random-floor for 2-hop = mean_closure/N_index (tiny).
- `baseline_in_band`: n/a — this is a VERIFY pilot, not a mechanism-vs-baseline discriminator sweep;
  the "baseline" (1-hop) is 0.0 by construction (composition necessity), which is the intended signal.
- `calibration_check: "default_ok_for_this_regime"` — uses the production BGE encoder + real store
  state unchanged; no adaptive thresholds (refuse tau reported, not tuned-for-PASS).
- `discriminating_fraction: n/a` (not a sweep); discriminator-fires verified in smoke (Phase-A
  positive control + Phase-B round-trip/2-hop/refuse all fired).
- `positive_control_arms`: {arm: LIVE_2HOP_QUALITATIVE_BAR; cited_prior_atom: U1
  exp_u1_fb15k237_ingest_eval_v1 (CHAIN_GRADE); cited_prior_metric: 2hop 0.381 vs 1hop 0.0075 (5000x),
  refuse OOD/accept 0.974/0.958; test_regime: ConceptNet live structural-compose;
  **regime_extension_audit: SHAPE_DRIFT** (different mechanism AND regime — live BGE-address +
  structural-compose vs isolated HD-algebra Hebbian; NO numeric reproduction claimed, only the
  QUALITATIVE bar: real signal >> random floor + fabrication-refusal separation)}.
- `sweep_alignment_verdict: ALIGNED` (no sweep). `composition_edges`: semantic-address ->
  structural-compose (SHAPE_MATCH: both operate on the same bare CN_ id space via the same Store).
- Defensive error-checking: `start_marker_written: true`, `crash_diagnostic_present: true`,
  `heartbeat_present: true` (_heartbeat.jsonl per stage), `cell_chunked: false` (single-unit).
- `progress_logging: "print_flush_true"` (all progress via print(..., flush=True) + per-stage
  heartbeat; MANDATORY since full timeout_s >= 1800).
- RUN_MODE verification (META_RULE §16): cell defaults to `full` (no flag); `--smoke` / `--self-test`
  explicit; metrics.json records `run_mode`. FULL dispatch must land `run_mode=full`.

## FULL config + dispatch
- FULL: N_INDEX=6000, N_PROBE=250, N_2HOP=120, N_REFUSE=120, SEED=12345. Estimated wall ~7 min
  (BGE model load ~44s + store load ~6s + subgraph mine ~25s + encode 6000 ~300s + queries ~40s).
  `--timeout 2400` (40 min, generous for slow remote CPU).
- Route: `remote_cpu_queue` (CPU-bound; SMOKE-only on local_cpu_queue per USER lock). Needs push to
  origin/main (harness-denied to exp_dev) -> hdi_orchestrator dispatches.
- **Remote precondition (SCRIPT_PRECONDITION_VIOLATION guard):** marsh@home must have
  `sentence-transformers` + `BAAI/bge-large-en-v1.5` model cached (ConceptNet live-path has never run
  remote). Cell fails loud with CELL_CRASHED + traceback if BGE import/model-load fails.
- Canonical run = the remote FULL (per USER canon!=preview lock); local smoke is the pre-flight gate.
