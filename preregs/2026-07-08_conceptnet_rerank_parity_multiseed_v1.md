# Pre-registration: conceptnet_rerank_parity_multiseed_v1

- ANCHOR: `conceptnet_rerank_parity_multiseed_v1`
- Script: `experiments/exp_conceptnet_rerank_parity_multiseed_v1.py`
- Date: 2026-07-08
- Author: exp_dev
- Device: cpu | Queue target: `remote_cpu_queue` (FULL); local smoke only
- Referents: `exp_substrate_conceptnet_kg_inference_transfer_cpu_v1` (j19) +
  `exp_conceptnet_semantic_seeded_beam_composition_v1` (comp) reused as pure-function libraries
  (byte-identical split / metrics / beam decode / cf-RPE store).

## Prior-work check (substrate-KB concept-query, MANDATORY)

`bash tools/substrate_query.sh "semantic rerank beam composition multi-hop conceptnet associative
store decorrelated"` -> top hit cosine=0.330 (`an associative relation`, wordnet), then
`ANCHOR-3 CONCEPTNET-RELATION-DECOMPOSITION` (0.314) and `Multiplicative composition` (0.314) -- all
GENERIC. No prior arc cell for POST-HOC BGE-rerank over a DECORRELATED substrate beam. GENUINELY
NOVEL vs the v1 SEM_BEAM cell (which injected semantics INTO the store and HARD_FAILed 0.227). This
cell keeps the store decorrelated and applies semantics ONLY at post-hoc rerank -- the design the
correlation-hurts-capacity reference prescribes.

## Two deliverables (one cell; shared decorrelated store + firewalled split)

Rationale for one cell not two: A and B share the identical RANDOM_BEAM (decorrelated cf-RPE store)
spine and the firewalled held-out split. Co-running makes the rerank-vs-random-beam comparison
PAIRED on the exact same candidate sets and builds the expensive cf-RPE store once per seed instead
of twice. B's numbers (RANDOM_BEAM, BGE_ALONE) are IDENTICAL whether or not A's rerank arms are
present (rerank is a separate scoring pass over the same pools) -> no contamination. Top-level
`verdict` reflects deliverable A (the new-science mechanism question); deliverable B's `parity_tier`
is a SEPARATE metrics block, read INDEPENDENTLY by the VET (NOT gated by A's verdict).

### (A) SEM_RERANK -- semantic 2x-revival of the SEM_BEAM HARD_FAIL
Store codes stay DECORRELATED (near-orthogonal random -- the config that hit PARITY). Semantics
enters ONLY as a POST-HOC re-rank over the substrate-native RANDOM_BEAM candidate set: BGE-large
cosine re-scores the top-`RERANK_K=25` beam shortlist. Respects
`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08` (store
wants decorrelated; retrieval wants correlated; DECOUPLE -- never semantic-seed the store codes).
Q: does semantic rerank of the glass-box beam BEAT plain RANDOM_BEAM Hits@10 WITHOUT collapsing the
way SEM_BEAM did (0.502 -> 0.227)?

Two rerank strategies bracket the question: `SEM_RERANK_HARD` (BGE fully replaces substrate order
within the shortlist -- aggressive) and `SEM_RERANK_RRF` (reciprocal-rank fusion of substrate rank +
BGE rank -- robust). Primary arm = best-mean of the two.

### (B) Multi-seed CG-parity firm-up
RANDOM_BEAM-vs-BGE PARITY (0.502 vs 0.494, MM-TENTATIVE) made multi-seed + determinism-pinned so the
claim can move MM -> CHAIN_GRADE.

## Compute architecture (MANDATORY)

Class: **(b) sequential-CPU with justification.** The cf-RPE store build is a Widrow-Hoff online
delta rule `W += (LR/n)*outer(val - W@key, key)` -- W_t depends on W_{t-1}, inherently sequential
(cannot batch edges). This IS the CG referent mechanism being validated (June-19). BLAS `sger`
in-place rank-1 updates are used (memory-bound). The beam-eval matmuls are minor relative to the
store build. CPU matches June-19 runtime. Store build is O(n_edges * N_DIM^2) memory traffic per
seed; ~5 seeds + 2 determinism-check rebuilds. Route to `remote_cpu_queue` (CPU is the right
resource; GPU batching does not help the sequential delta-rule).

Storage strategy: `cfrpe_heteroassociative_matrix` -- inherited from the June-19 CG referent; this
is a heteroassociative cleanup matrix W, NOT the bundle-superposition that collapses at chain depth.
It is the exact store whose parity is being validated (not a design choice; the referent).

## Determinism (deliverable B core; PYTHONHASHSEED root-cause + fix)

Root cause: June-19 iterated `store_edges` (a set of (u,rel,v) string-tuples) and the ORDER-DEPENDENT
cf-RPE delta rule built W in Python set-iteration order, which is PYTHONHASHSEED-dependent -> Hits@10
wandered ~sigma 0.02 run-to-run. Candidate-pool composition (iterating `tails_by_rel[r]` then capping)
had the same dependence.

Fix (portable; NO os.execv re-exec -- unsafe on Windows/runner PID tracking): every set that feeds an
order-dependent computation is `sorted()` to a fixed canonical order BEFORE use:
- store edges: `canonical_edges(store_edges) = sorted(...)` -> fixed store-build order.
- rel-subgraph BFS: `det_rel_subgraph_edges` iterates neighbours in sorted order -> cap-truncation
  (which edges survive when capped) is hash-independent.
- candidate base pool: `sorted(...)` before the deterministic-rng prune-shuffle.
- entity/relation id maps: already `sorted()`.
Result: input-order-independent -> PYTHONHASHSEED-independent BY CONSTRUCTION. Verified in
`--self-test` (build W from a scrambled-order edge list; assert byte-identical digest to the
sorted-order build) AND in the eval (`determinism_check`: rebuild seed[0] store W twice; assert
identical W digest -> `determinism_ok`).

Multi-seed variance source: SPLIT + pools + BGE + closure are built ONCE (seed-invariant, driven by
`SPLIT_SEED=20260619` -- the exact June-19 firewalled split). Only the RANDOM codebook (E_rand, R)
varies per code-seed -- that is the legitimate substrate run-to-run variance (which random codes were
drawn). Answers "was 0.502 a lucky code draw, or does parity hold across draws?"

## Arms

| arm | codes | scoring | deliverable | seed-varying |
|-----|-------|---------|-------------|--------------|
| RANDOM_BEAM | random (decorrelated) | width-BEAM_K=6 beam, KHOP=4 | A spine + B | yes (E_rand) |
| BGE_ALONE | -- (frozen BGE teacher) | BGE-large cosine (June-19 convention) | B comparator + A rerank source | no (invariant) |
| SEM_RERANK_HARD | random store; BGE post-hoc | top-25 reordered purely by BGE cosine | A | yes (via RB) |
| SEM_RERANK_RRF | random store; BGE post-hoc | top-25 fused via RRF (k0=60) of RB rank + BGE rank | A | yes (via RB) |
| closure | -- | BFS transitive-closure oracle | baseline (control) | no |
| random_floor | -- | uniform random score | baseline (floor) | no |

## Bands (honest, pre-committed; NO SMOKE inflation)

### Deliverable A (primary = best-mean of {SEM_RERANK_HARD, SEM_RERANK_RRF}; lift vs RANDOM_BEAM), S=5 seeds
- **WIN (HARD_PASS):** best-rerank mean Hits@10 >= RANDOM_BEAM + 0.03 AND best arm positive in
  >= ceil(0.8*S)=4 seeds (paired same-seed). Strictly above floor (lift band 0.03 > 0). P~0.15-0.20.
- **TIE (MIDDLE_BAND):** |best-rerank lift| < 0.03 AND best arm >= RANDOM_BEAM - 0.02 (no collapse).
  Glass-box beam already captures what BGE-rerank would add. EXPECTED / pre-committed. P~0.45.
- **COLLAPSE (HARD_FAIL):** best-rerank mean <= RANDOM_BEAM - 0.05 (post-hoc semantics HURTS even at
  rerank -> extends correlation-hurts to reranking). P~0.20.

### Deliverable B (RANDOM_BEAM vs BGE_ALONE; parity_tier -- read INDEPENDENTLY of A)
- **CG_PARITY:** |mean(RB)-BGE| <= 0.02 AND std(RB) <= 0.03 AND pooled McNemar p > 0.05 AND
  determinism_ok -> parity FIRM, promote MM -> CHAIN_GRADE.
- **MM_PARITY:** |mean(RB)-BGE| in (0.02, 0.05] OR std(RB) > 0.03 OR McNemar p in (0.01, 0.05].
- **SUBSTRATE_WINS:** mean(RB)-BGE > 0.05 AND McNemar p <= 0.05 (substrate BEATS the encoder).
- **SUBSTRATE_LOSES:** mean(RB)-BGE < -0.05 AND McNemar p <= 0.05.

## SCHEMA-VET checklist

- `cardinality_ok`: EXPECTED_N_UNITS = len(CODE_SEEDS) = 5 (FULL) / 2 (smoke). Verdict counts seed
  partials; S != EXPECTED emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`. Set in metrics.
- Per-unit failure-class: `except Exception` (NOT BaseException/bare) writes `CELL_CRASHED` +
  traceback; per-seed checkpoint isolates a runner death to one seed.
- `arms_differ_verified`: RANDOM_BEAM vs BGE_ALONE rank digests MUST differ (different mechanisms);
  asserted + reported (`arms_differ_rb_vs_bge`). Rerank-vs-RB pair EXEMPTED-if-identity (rerank is an
  identity when true items never fall in the shortlist beyond top-10) -- covered by the
  `rerank_headroom > 0.03` discriminator-fires gate + `rerank_identity` report field.
- `final_metrics_atomicity`: `tmp_replace` (per-seed partials atomic via `_seed_checkpoint.write_partial`;
  final aggregate via `write_metrics`).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException) -- grep-gate PASSES.
- `crlb_n/a`: "ranking metric Hits@10 in [0,1]; parity bar 0.494 reachable (June-19 MEASURED) and
  rerank lift bounded by rerank_headroom feasibility, not a Cramer-Rao noise floor."
- `discriminator_reachability`: parity bar 0.494 MEASURED-reachable; rerank WIN threshold +0.03 is
  reachable iff rerank_headroom (frac true in top-25 minus frac in top-10) >= 0.03 -- checked at smoke.
- `baseline_in_band`: RANDOM_BEAM ~0.50 in (0.05, 0.95). Smoke band [0.42, 0.58].
- `discriminator survives scale`: SMOKE at FULL N_DIM=8192 (option A) so RANDOM_BEAM reproduces
  ~0.50; `rerank_headroom` fires the rerank discriminator.
- `calibration_check`: `default_ok_for_this_regime` -- BEAM_K=6/KHOP=4/N_DIM=8192 inherited verbatim
  from the June-19 referent that produced the 0.502/0.494 numbers (same regime, not synthetic).
- `cell_chunked`: true (within-cell per-seed checkpoint/resume via `_seed_checkpoint`).
- `start_marker_written`: true. `crash_diagnostic_present`: true. `heartbeat_present`: true.
- `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (line-buffered stdout + per-seed/per-100-row heartbeat).
  timeout_s >= 1800 -> field required, satisfied.
- `run_mode` verification: cell defaults `run_mode=full` (no --smoke) so a FULL dispatch cannot
  silently land as self_test; `--smoke` isolates to `_smoke` output dir.

## §15 composition/sweep gates

- `sweep_alignment_verdict`: ALIGNED. Seed axis varies E_rand realization only; RANDOM_BEAM
  experiences the seed as intended (different random codes). No nominal-vs-effective mismatch.
- `discriminating_fraction`: N/A as a sweep-band metric (no accuracy-sweep axis); the analogous
  discriminator-reachability is `rerank_headroom >= 0.03`, checked at smoke.
- `composition_edges`: beam(RANDOM_BEAM) -> rerank(BGE cosine): SHAPE_MATCH -- rerank consumes the
  per-candidate substrate score vector + the per-candidate BGE cosine vector (both length n_cands),
  emits a reordered candidate list. No adapter needed (post-hoc reorder, not a primitive chain).
- `positive_control_arms`: RANDOM_BEAM reproduces the June-19 RANDOM_BEAM referent AT THE TEST
  REGIME (N_DIM=8192, BEAM_K=6, KHOP=4, same split). Cited prior metric 0.502; tolerance absorbed by
  the [0.42, 0.58] smoke band (the determinism fix changes the store-build order from the June-19
  hash-order to canonical-sorted -> a different specific draw within the ~0.02 sigma cloud, by design).
- `functional_requirements`: (1) decorrelated multi-hop retrieval -> RANDOM_BEAM cf-RPE beam (CG
  referent); (2) post-hoc semantic reorder without touching store codes -> BGE-cosine rerank of the
  shortlist (new, respects correlation-hurts-capacity); (3) bit-reproducibility -> canonical sorted
  set ordering (new determinism helper); (4) parity significance -> paired McNemar (existing stat).

## Expected units / timeout

FULL: 5 code-seeds + 2 determinism-check store rebuilds = 7 store builds + 5 beam evals over the full
held_t pool. HYPOTHESIZED runtime ~30-45 min (store build memory-bound at N_DIM=8192). Recommend
`timeout_s = 5400` (90 min) headroom. Smoke: 2 seeds + 2 rebuilds at CLASSIFY_POOL=700; HYPOTHESIZED
~10-20 min.
