# Pre-reg: Experiment 1 — Bridge-entity coverage check (SMOKE)

**Anchor:** `substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03`
**Author:** hdi_exp_dev (spawned by Director from optimal-arch drill Experiment 1)
**Filed:** 2026-07-03 (UTC)
**Cell path:** `experiments/exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03.py`
**Spec source:** `notes/research_optimal_retrieval_architecture_for_substrate_director_kb_2026-07-03.md` Part 3 Experiment 1 (lines 93-98).
**Precedent replayed:** `experiments/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03.py` (HARD_FAIL with tandem=0.083 vs oracle=0.783 MEASURED@`data/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03_smoke/metrics.json:verdict_msg`).

## Question

For the queries where TANDEM_RAG missed the correct answer, is the TRUE bridge entity
(the mid-of-chain intermediate, MEASURED@`corpus['queries'][qi]['mid']`) recoverable
via char-trigram fuzzy-match extraction over the hop-1 dense-retrieved chunk text
against the KGStore's entity node names?

If YES (>= 60%), the entity-extraction layer is not the bottleneck; PPR-walk (Exp 2) is
a viable next step. If NO (< 25%), fix must move upstream to hop-1 dense retrieval itself.

## Compute architecture

- Class: **(b) sequential-CPU with justification**
- Justification: total work ~60 queries × 5 chunks × ~20 tokens/chunk × 20-entity codebook cosine
  = ~120K trivial dot-products. Expected wall time < 5s per seed for the coverage-check core
  (excludes precedent bge retrieval replay which is ~2min).
- Storage strategy: **no_composition** — this cell measures a single primitive (char-trigram
  cosine match), no bind/unbind chains stored. Bundle-vs-sharded not applicable.

## Arms

1. `ARM_MAIN_BRIDGE_COVERAGE` — for failed TANDEM_RAG queries, extract entities from hop-1
   retrieved chunk texts via char-trigram cosine (top-1 per token, threshold=0.5), then check
   `q["mid"]` in extracted set. Metric = MATCH_RATE.
2. `ARM_POS_CTL_BRIDGE_INJECTED` — positive control. For the same failed queries, INJECT the
   ground-truth bridge chunk (fact `mid`→something) into the retrieved-chunk-text pool, run
   the same extractor. HARD requirement: MATCH_RATE >= 0.95 (proves char-trigram fuzzy match
   works when the text is actually present).
3. `ARM_NEG_CTL_UUID_BRIDGE` — negative control. For the same failed queries, replace
   `q["mid"]` with a random UUID token (e.g., `Xzqppqzt`). Run the same extractor against
   the original (un-injected) retrieved chunks. HARD requirement: MATCH_RATE <= 0.05 (proves
   we're not just always returning True from a broken threshold).

## Verdict bands

- **HARD_PASS:** `ARM_MAIN` MATCH_RATE >= 0.60 AND `ARM_POS_CTL` >= 0.95 AND `ARM_NEG_CTL` <= 0.05
- **HARD_FAIL:** `ARM_MAIN` MATCH_RATE < 0.25 (with pos+neg controls in band)
- **MIDDLE_BAND:** 0.25 <= `ARM_MAIN` < 0.60 (partial signal; graph-walk helps some but
  query-decomposition may be needed too)
- **CONTROL_FAIL:** any control-arm outside its required band -> reject cell (mechanism broken)

Band-floor rule (META_RULE_L): PASS floor is strict `>= 0.60 + 0.05 * (1.0 - 0.60) = 0.62`
declared. FAIL ceiling strict `< 0.25`.

## Falsifiable predictions

- HARD_PASS supports proceeding to Experiment 2 (PPR-walk on matched entities).
- HARD_FAIL invalidates the graph-walk-fixes-RAG hypothesis at the entity-extraction layer;
  fix must move upstream (better hop-1 encoder / better index / query decomposition).
- MIDDLE_BAND supports Architecture B (query-decomposition preprocessing) as a prerequisite
  for graph-walk to work reliably.

## SCHEMA-VET (META_RULE_A-M + AC/AF/AG/AH + §15 gates)

- `cardinality_ok`: **TRUE** — EXPECTED_N_UNITS = 3 arms × 3 seeds = 9. Verdict counts.
- Per-unit failure-class: SPECIFIC `except Exception` only; `except SystemExit: raise` first.
- Discriminator-fires (META_RULE_K): failed-set must be non-empty (else vacuous). Fires assertion
  = `n_failed_queries_across_seeds >= 20` (from precedent MEASURED tandem=0.083 → ~55/60 failed).
- Strictly-above-floor (META_RULE_L): PASS at `>= 0.62`, not `>= 0.60`.
- HP_SCOPE: HARD_PASS applies to MAIN only; POS/NEG controls have their own strict thresholds
  that must be satisfied INDEPENDENTLY (control_fail overrides everything).
- calibration_check: **"default_ok_for_this_regime"** — char-trigram cosine threshold=0.5 is
  the mid-way default; regime-appropriate for bipolar HD short-token matching (20-entity codebook,
  each name 4-5 chars → 5-6 trigrams; cosine collapses to overlap-fraction).
- arms_differ_verified: TRUE (each arm's `entity_extracted_set` differs by construction).
- final_metrics_atomicity: `tmp_replace` (os.replace pattern).
- CRLB: **crlb_n/a: "char-trigram cosine is not a noise-floor problem; discriminator is a rate not a shift"**
- baseline_in_band (META_RULE_AG): expected 0.20 < ARM_MAIN < 0.90 (neither by-construction
  saturated nor by-construction floored); verified at smoke.
- Cell defensive-error-checking: start_marker + crash_diagnostic + heartbeat every 60s +
  chunked_single_seed = **NOT chunked (single-cell 3-seed loop; seeds ~few sec each; runner
  zombie risk minimal at this scale)**. `cell_chunked: false` justified.
- progress_logging: `print_flush_true` on every progress line (timeout < 1800s so not
  strictly mandatory but included defensively).

### §15 test-design gates

- **A) `sweep_alignment_verdict: ALIGNED`** — this cell doesn't sweep parameters; it evaluates
  a single mechanism on a fixed failed-query set. N/A.
- **B) `discriminating_fraction`** — bands cover [0, 0.25] (FAIL), [0.25, 0.62] (MIDDLE),
  [0.62, 1.0] (PASS). Predicted MATCH_RATE ≈ 0.60-0.85 (chunk text contains bridge in most
  failed cases because bge often retrieves the correct e0→r2→mid fact chunk). Predicted point
  lands in MIDDLE or PASS band → `discriminating_fraction: 1.0`.
- **C) `composition_edges`** — SHAPE_MATCH: `CharTrigramEncoder.encode(str) -> np.ndarray[n_dim]`
  → `KGStore.E [n_ent, n_dim]` cosine similarity. Both are `float32` bipolar (KGStore
  `_bipolar` produces `{-1,+1}` cast to `float32`; CharTrigramEncoder `sign()` produces same).
  Composition matches.
- **D) `positive_control_arms`** — `ARM_POS_CTL_BRIDGE_INJECTED` reproduces the primitive at
  the test regime by force-injecting the bridge chunk text. Tolerance: >= 0.95 (near-perfect
  since chunk literally contains the name). If < 0.95 → CONTROL_FAIL; primitive is broken.
- **E) `functional_requirements`**:
  1. Extract entity mentions from free text → `hdlab/char_trigram_encoder.py:CharTrigramEncoder.nearest()` (per-token top-1 cosine vs codebook).
  2. Provide entity vocabulary → 20 ENTITIES from precedent's synthetic corpus, encoded via
     `CharTrigramEncoder.encode_batch`.
  3. Verify bridge presence → set membership on extracted-entity set.

## HYPOTHESIZED numbers

- `ARM_MAIN` MATCH_RATE: **0.65** HYPOTHESIZED@this file (bge retrieves chunks lexically
  related to query e0/r2; bridge often appears as `value` slot in retrieved chunks).
- `ARM_POS_CTL`: **~1.00** HYPOTHESIZED (bridge chunk text explicitly contains bridge name).
- `ARM_NEG_CTL`: **~0.00** HYPOTHESIZED (random UUID not in any chunk text).

Baseline (unretrieved-chunks pool of random 5 chunks): expected ~0.25 (5/20 entities present
by chance) — this is not a formal arm; noted for calibration.

## Dispatch plan

- Queue: `local_cpu_queue` (per USER-locked 2026-07-01: SMOKE only on local_cpu).
- Timeout: 600s (self-test 30s + 3 seeds × ~150s bge retrieval replay + fast coverage compute).
- Run mode: `--smoke` (SMOKE cell only; no FULL variant in this drill).

## Ship path

If HARD_PASS: ready to author Experiment 2 (PPR-walk over KGStore from matched entities).
If HARD_FAIL: escalate to Research — fix must be upstream of graph-walk (hop-1 encoder swap
or query decomposition).
If MIDDLE_BAND: ship Experiment 2 anyway but with expectation of narrow lift; Research
prioritizes query-decomposition (Architecture B) as prerequisite.
