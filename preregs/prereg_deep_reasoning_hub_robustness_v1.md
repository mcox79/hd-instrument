# Pre-registration: deep_reasoning_hub_robustness_v1

**Date:** 2026-07-05
**Author:** hdi_exp_dev (Opus 4.8 1M, agent-spawn)
**Trigger:** Director task -- BUILD deeper reasoning + fix hub collapse into the substrate (constructive glass-box, NO LLM comparison, NO re-encode). Motivated by `data/exp_cortex_readiness_real_atom_algebra_v1/metrics.json` (GOOD_SHALLOW_MEDIOCRE_HUBS: deg1=1.000 src_uniform=0.920 but deg>=5 single-shot exact top1 ~0.219; reasoning shallow).

## Anchor

`deep_reasoning_hub_robustness_v1` (single self-contained cell; no sibling imports).
Cell: `experiments/exp_deep_reasoning_hub_robustness_v1.py`.

## Routing / Compute architecture

- **Class:** (b) sequential-CPU with justification. Chained retrieval has genuine sequential dependency (hop N cursor = hop N-1 recovered atom); the substrate primitives (HRR FFT bind/unbind + matmul cleanup) are NumPy/BLAS-threaded; no GPU advantage for this diagnostic. Wall time light (smoke ~73s; light-full ~few min).
- **Storage strategy:** the CELL UNDER TEST bundles each source's edges into one trace (the motivating architecture). A key finding is that BUNDLED hub storage is the failure; a declared build recommendation is SHARDED storage (per META_STORAGE_STRATEGY law). No substrate mutation (read-only).
- **Smoke:** local (`.venv` direct invocation). **Full:** Director-authorized light local CPU run OR remote_cpu_queue (idle). No push needed for SCP-based queue_add; harness-DENIED push is not required for local run.

## Why this cell exists (the gap)

The memory algebra reasons over real 2-hop facts for typical low-degree cases but (1) reasoning depth was never measured as a true multi-hop CHAIN over real atoms, and (2) high-degree hubs collapse (deg>=5 single-shot exact top1 ~0.219). Two constructive builds:

- **BUILD 1 (depth envelope):** true chained bind/unbind+cleanup inference over REAL graph paths. Each hop builds the CURRENT atom's source-trace, unbinds by the hop's role, cleans up to a discrete atom, and uses THAT recovered atom as the next cursor (errors propagate). Measures how DEEP the chain stays on the correct path (L=1..Lmax), baseline single-shot cleanup vs iterative cleanup.
- **BUILD 2 (hub robustness):** attack the deg>=5 collapse with (a) mean-centered cleanup (whiten the cos~0.57 cone), (b) roles-known iterative explaining-away resonator, and (c) protected/index binding (distinct permutation power per same-role edge). Diagnostic controls at matched degree: independent-real fillers (ctrlB) and synthetic separable codes (ctrlC) to attribute the collapse to crosstalk-capacity vs neighbor-representation vs same-role-collision.

## Functional Requirements (Gate E)

1. **Multi-hop retrieval over real facts** -> chain of `unbind + cleanup` (existing chain-grade primitive) with per-hop re-materialization (cleanup provides discreteness/error-correction between hops).
2. **Recover all fillers of a high-degree source** -> bundle unbind + cleanup (existing); augmented with iterative explaining-away (new) and protected binding (new mechanism -- flagged).
3. **Attribute the failure** -> matched-degree controls (independent-real, synthetic) + same-role-collision split (new instrumentation).

## Composition edges (Gate C)

- bind (role,filler) -> bundle(sum) : SHAPE_MATCH (both N-vectors).
- bundle -> unbind(role) : SHAPE_MATCH.
- unbind -> cleanup(codebook argmax) : SHAPE_MATCH.
- protected binding: role -> roll(role, k) : SHAPE_MATCH (permutation is dimension-preserving; HRR-compatible).

## Positive control (Gate D) -- reproduce prior at test regime

- arm: `ss_raw` deg>=5 single-shot argmax
- cited_prior_atom: `cortex_readiness_real_atom_algebra_v1` real_graph by_degree deg5
- cited_prior_metric: 0.219  MEASURED@data/exp_cortex_readiness_real_atom_algebra_v1/metrics.json (deg5 top1 seed7=0.2092 seed13=0.2246 seed19=0.2224)
- tolerance: 0.10
- smoke reproduction: 0.222  MEASURED@data/exp_deep_reasoning_hub_robustness_v1_smoke/metrics.json:positive_control_ss_raw_deg_ge5.measured_mean (within tol)

## Sweep axes

| Axis | Smoke | Full |
|------|-------|------|
| seeds | [7] | [7,13,19] |
| deg_bins (source out-degree) | [2,3,5,8plus] | [2,3,4,5,6,7,8plus] |
| hub_per_bin | 50 | 80 |
| codebook_M | 8000 | 10000 |
| iter_n_iters | 6 | 4 |
| chain_n_paths | 100 | 200 |
| chain_Lmax | 5 | 6 |

**cardinality_ok:** EXPECTED_N_UNITS = seeds * (len(deg_bins) + 2*Lmax). Verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if n_units_counted < expected.

**effective_vs_nominal_parameter_audit (Gate A):** degree bins map directly to bundle size the cleanup experiences (effective = nominal). sweep_alignment_verdict: ALIGNED.

**bracket_includes_discriminating_band (Gate B):** single-shot by-degree spans deg2=0.79 (near-sat), deg3=0.67, deg5=0.50, 8plus=0.14 (floor) -- deg3/deg5 land in [0.30,0.70]. discriminating_fraction >= 0.30. The BUILD arms move them.

## Pre-registered bands (envelope-fail-bands)

**BUILD 2 -- hub rescue (primary discriminator; HP_SCOPE = idx_bind + iter_mc arms):**
- discriminator-fires gate: baseline `ss_raw` deg>=5 < 0.40 (collapse present). If >=0.40, DISCRIMINATOR_DID_NOT_FIRE.
- HARD_PASS (rescue): a build arm lifts deg>=5 top1 by >= +0.10 over ss_raw AND strictly above floor+5%.
  - `HUBS_RESCUED_BY_PROTECTED_BINDING`: idx_bind lift >= 0.10 AND idx_bind_lift > iter_lift+0.03.
  - `HUBS_RESCUED_BY_ITERATION`: iter_mc lift >= 0.20 AND iter_mc >= 0.50.
- FAIL band (no algebra rescue): `HUB_COLLAPSE_CAPACITY_AND_COLLISION_LIMITED` -- neither build lifts; controls show synth/indep-real also collapse => capacity + same-role collision, not representation. (This is still an informative build: identifies the true fix = sharded storage + protected binding.)

**BUILD 1 -- depth envelope (HP_SCOPE = chain arms):**
- depth@0.5 = largest L where cumulative on-path >= 0.50. Report baseline vs iterative envelope. No hard PASS/FAIL threshold (characterization); iterative depth >= baseline depth is the expected build direction.

## SCHEMA-VET mandatory fields

- `arms_differ_verified`: true (hub ss_raw / ss_mc / iter_mc recovery-index arrays hash-distinct; smoke verified).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp -> os.replace).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; grep-gated clean).
- `crlb_n/a`: "recovery-vs-chance; chance floor = 1/M reported; the operative floor is the MEASURED single-shot 0.219 positive control, not a Cramer-Rao noise floor."
- `discriminator_reachability`: true (idx_bind smoke = 0.622 >> ss_raw 0.222; reachable and demonstrated).
- `baseline_in_band`: true (ss_raw deg>=5 ~0.22; 0.05 < x < 0.95).
- `discriminator_survives_scale`: smoke codebook_M=8000 near full (10000); baseline collapses in smoke; idx_bind rescues in smoke; effect size +0.40 robust to M (collision-removal is M-independent).
- `calibration_check`: default_ok (substrate primitives used directly; mean-centering + permutation are fixed label-free transforms, no data leakage).
- `cell_chunked`: false (single-seed-loop cell; light; start-marker + crash-diagnostic + heartbeat present).
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED + traceback). `heartbeat_present`: true.
- `defensive_error_checking`: passed_all_4_patterns.
- `run_mode verification`: post-write assert written.run_mode == run_mode.
- `progress_logging`: print_flush_true (line-buffered stdout + per-arm flush prints). timeout_s < 1800 (light), so field is defensive not required.

## Numbers (tagged)

- ss_raw deg>=5 smoke: 0.222  MEASURED@data/exp_deep_reasoning_hub_robustness_v1_smoke/metrics.json
- idx_bind deg>=5 smoke: 0.622 (+0.400)  MEASURED@ same
- iter_mc deg>=5 smoke: 0.244 (+0.022)  MEASURED@ same
- collision_frac deg>=5 smoke: 0.88  MEASURED@ same
- chain depth@0.5 smoke: baseline=2 iter=3  MEASURED@ same
- THEORETICAL: near-orthogonal white roles decouple the joint bundle-recovery into per-slot cleanup, so roles-known explaining-away has ~zero leverage -> iteration cannot rescue (confirmed empirically +0.02).
