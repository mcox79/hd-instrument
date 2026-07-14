# Pre-registration: Fixed-support N-scaling of the AdditiveKGMap held-out-entity inductive margin

- **Cell**: `experiments/exp_additive_map_fixed_support_scaling_cskg_v1.py`
- **Anchor**: `additive_map_fixed_support_scaling_cskg_v1`
- **Date**: 2026-07-13
- **Author**: exp_dev
- **Capability under test**: `hdlab/additive_map.py::AdditiveKGMap` (live, acceptance-gate PASSED, reproduces 0.12821)
- **Queue**: overnight_queue (GPU). device=auto (cuda on GPU host).

## Prior-work check
`bash tools/substrate_query.sh` unavailable in-thread; prior-work established by the task's own provenance chain
(scaling-ladder VET, acceptance gate). This cell is NOT a rediscovery: it is the direct measurement of the ONE open
validation the scaling-ladder VET flagged -- N grown ~10x HOLDING per-entity support-degree FIXED (the 1.5x rung
confounded N-growth with a sparser core; N-invariance beyond 1.5x was mechanism-INFERRED, never measured).

## Question
Does the held-out-ENTITY ANCHOR_COMPOSE margin RETAIN as global N grows ~10x while per-entity support-degree is held
FIXED? Theory (capacity tracks LOCAL support-degree, not global N) predicts RETENTION.

## Design
- **N-ladder (MEASURED, k-core probe 2026-07-14)**: k_core=12 -> N=25752 (1.0x, base) ; k_core=3 -> 70697 (2.7x) ;
  k_core=1 -> 498540 (**19.4x, EXCEEDS the 10x target**). Bands are retention RATIOS -> robust to the exact realized N.
- **Support-degree control = FIXED-SUPPORT-CAP**: at every rung, scored held-out entities restricted to those with
  >= K_SUP support edges (+>=1 query), each subsampled to EXACTLY K_SUP support edges (deterministic). Per-entity
  support-degree input is EXACTLY K_SUP at every N -> the sparser-core confound cannot recur. Eligible counts MEASURED
  comparable across the span (K3: 1389/2464/2662 ; K6: 1134/1348/1443 at k12/k3/k1).
- **Candidate-growth fairness**: filtered MRR is rank-vs-ALL-N -> mechanically harder at 19.4x N even for a perfect
  code. FIX = a SEEN transductive reference arm (both-seen held-out edges, LEARNED codes) that suffers the SAME
  candidate-growth. PRIMARY metric = candidate-growth-NORMALIZED retention
  `R_norm(top) = [ANCHOR_K3/SEEN](top) / [ANCHOR_K3/SEEN](base)`. Raw retention R_raw also reported.
- **Local-degree demonstration** (theory's causal claim + weak-point localization): on the MATCHED >=6-support set,
  compose with 3 vs 6 support edges (ANCHOR_K3m vs ANCHOR_K6, same entities/queries). Capacity tracks local degree
  iff ANCHOR_K6 > ANCHOR_K3m at every rung, invariant to N.
- **Arms** (one shared additive fit per rung/seed; k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, reciprocal,
  lr=A1_LR -- pinned to VET/acceptance gate): ANCHOR_K3 (mechanism), SCRAMBLE_K3 (must-fail relation control),
  RANDOM (null floor), ANCHOR_K6 + ANCHOR_K3m (local-degree demo), SEEN (candidate-growth reference).
- **Seeds**: [7, 13, 17]. **Multi-seed**. Rungs x seeds = 9 units. Cardinality-gated (EXPECTED_N_UNITS).

## Bands (envelope-fail-bands; registered BEFORE run)
- **SCALES_AT_10X (HARD_PASS)**: R_norm(top) >= 0.70 AND top fires (ANCHOR_K3 >= 3x RANDOM AND -RANDOM >= 0.003) AND
  relation signal (ANCHOR_K3 - SCRAMBLE_K3 >= 0.003) AND local-degree (ANCHOR_K6 > ANCHOR_K3m) at top AND every rung
  eligible (>= 300) AND base fires AND SEEN above RANDOM floor at every rung AND top_N >= 10x base_N.
- **DEGRADES_WITH_N (HARD_FAIL)**: base fires AND SEEN valid AND R_norm(top) < 0.40 (composition degrades beyond the
  shared candidate-growth cost).
- **MIDDLE_BAND**: 0.40 <= R_norm(top) < 0.70, or a fire/relation/local-degree control marginal.
- **INCONCLUSIVE (gated)**: base not firing, any rung < 300 eligible, or SEEN at the RANDOM floor (normalizer degenerate).
- 0.70 clears 0.40 by 30% of the ratio range (strictly-above-floor, META_RULE_L).

## Discriminator survives scale
Option (B) analytical: R_norm is a ratio of two independently-MEASURED MRRs at 19.4x-different N/candidate counts;
free to land in [0, >1]; SEEN + RANDOM measured per-rung subtract candidate-growth. Self-test (2-rung planted
mini-ladder) exercises the SAME split->cap->fit->compose->score->retention->verdict pipeline and fires every
within-rung discriminator + produces a non-INCONCLUSIVE verdict. **MEASURED@ selftest: ok=True, verdict=MIDDLE_BAND,
preflight_ok=True, 11/11 checks true (VALIDITY_PREFLIGHT_MODE=enforce), SELFTEST_PASS, run_mode=self_test verified.**

## OOM safety
The FULL run is self-guarding: an internal folded MEMSMOKE runs the biggest-N rung (k_core=1, N=498540) at 15 epochs
for seed 7 FIRST (peak memory is set by N not epochs), failing fast on OOM before the multi-hour ladder. No separate
memsmoke dispatch / remote env needed.

## Compute architecture
class (a/c) MIXED. Batched-GPU fits (neg-chunked, fit-checkpointed for outage-resume). SHARDED storage (per-entity
coords; per-TYPE relation displacements; only bundle = per-entity anchor mean). N_EVAL=1500 caps the top-rung CPU
score tensor ~3GB. Read-only w.r.t. KGStore (zero regression).

## Validity-preflight declarations (F.1-F.4 ENFORCE)
- real_code_path: AdditiveKGMap(.fit/.compose_into_table/.score_edges) + fit_kge_anchor1 + additive_direct_scores all
  exercised in the self-test on the planted arena.
- substrate_signature: fit_kge_anchor1 + additive_direct_scores bound vs live signature; BASE/portable kwargs (the
  SAME kwargs the accepted acceptance gate ran on the remote GPU -> remote parity proven; optional-kwarg advisory
  expected + benign).
- guard_baseline_valid: SEEN (the R_norm normalizer) validated above the RANDOM floor.

## Template mandates
arms_differ (>=3 sigs/rung); tmp_replace atomic metrics; SystemExit before Exception (no BaseException/bare except);
start-marker + crash-diagnostic + heartbeat; progress_logging print_flush_true (line-buffered + per-unit flush);
cardinality HARD_FAIL_CARDINALITY_BREACH_META_RULE_H; per-unit failure_class; run_mode verified.

## Fields
```yaml
cell_chunked: false          # seeds x rungs sequential in-process (matches accepted acceptance-gate pattern) + fit-ckpt resume
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
final_metrics_atomicity: tmp_replace
progress_logging: print_flush_true
cardinality_ok: true         # EXPECTED_N_UNITS = n_seeds * n_rungs = 9
calibration_check: adaptive_with_discriminator_gate
crlb_n/a: "MRR rank-vs-all-N candidate-growth ceiling made explicit + normalized via the SEEN reference; bands are retention ratios"
discriminator_reachability: true
baseline_in_band: true       # base rung fires; RANDOM near 1/N floor
real_code_path_exercised: [AdditiveKGMap, fit_kge_anchor1, additive_direct_scores]
substrate_signature_checked: [fit_kge_anchor1, additive_direct_scores]
guard_baseline_validated: [R_NORM_SEEN_NORMALIZER_VALID]
```
