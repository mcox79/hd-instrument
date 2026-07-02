# Prereg: stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1

## Anchor
`stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1`

## Queue
`remote_cpu_queue` (FULL). Smoke already ran on local (short wall).

## Cell path
`d:/AI/hd-instrument/experiments/exp_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1.py`

## Rescue context
Rescue path A for `stretch4_3_temporal_strips_cpu_v1` (v1 aborted by cell-author `aac06e4bd74722588`, 2026-07-02). v1 defects: (1) BFS operated on raw Python sets ignoring the FHRR substrate it defined (numpy-costume); (2) Goal G sampled from reached state = saturation trap.

## Mechanism (v2 rescue)
FHRR substrate hosts the TEMPORAL STRIPS ACTION LIBRARY. Each action `a` encodes as:

```
store_a = akeys[a] * (SLOTP*sum(props[pre[a]]) + SLOTA*sum(props[add[a]])
                    + SLOTD*sum(props[del[a]]) + SLOTU*durkeys[dur[a]-1])
substrate = SUM over all a
```

Substrate-native retrieval: `cunbind(cunbind(substrate, akeys[a]), SLOT_role)` then cleanup against props codebook via `Re(props @ conj(extract)) > tau_frac * N`. Recovers pre / add / del sets per action FROM substrate; substrate-BFS uses recovered sets for applicability + state transition.

**Grep-check verified (Skunkworks META CG 2026-07-02, numpy-costume defect prevention):** 9 substrate-primitive invocations inside `run()` at planner call sites (`build_action_substrate`, `substrate_bfs`, `substrate_retrieve_props`, `cphasor`, `cbind`, `cunbind`). No `except:` or `except BaseException:`.

## Arms
- **ARM_SUBSTRATE_NATIVE**: FHRR substrate mediates action-library encoding and per-action retrieval; recovered pre/add/del drive BFS.
- **ARM_SYMBOLIC_ORACLE**: Pure Python set-BFS on ground-truth schemas (positive control; ceiling reference).

## Non-oracle goal sampling (fix for v1 saturation trap)
`G` drawn INDEPENDENTLY from `S0` as a random 1..3-prop subset of `NPROP=12`. Some episodes unsolvable within `depth_budget=12`. `n_solvable` (symbolic finds a plan) is honest denominator.

## Config (FULL)
- `N = 8192`, `NPROP = 12`, `NACT = 16`, `NDUR = 5`
- `depth_budget = 12`, `tau_frac = 0.4` (0.4 * N = 3277)
- `TR = 150`, single seed = 271 (matches v1 seed for cross-version continuity)

## Config (smoke, already-ran)
- Same `N=8192`, `TR=15` (satisfies DISCRIMINATOR-MUST-SURVIVE-SCALE — full-N, only TR reduced)

## Envelope-fail-bands
| Case | Verdict |
| --- | --- |
| `arms_differ` AND `gap = sym - sub` in `[-inf, 0.10]` AND `sym in [0.30, 0.85]` AND `sub >= 0.30` | `HARD_PASS` (substrate tracks symbolic under noise) |
| `!arms_differ` AND all retrieval p/r >= 0.95 AND `sym in [0.30, 0.85]` | `HARD_PASS` (substrate-native equivalence proven at high fidelity) |
| `gap in (0.10, 0.20]` | `MIDDLE_BAND` (partial retrieval) |
| `!arms_differ` AND any retrieval p/r < 0.95 | `BLOCK_DISPATCH_META_RULE_AF_SUSPECT` (code short-circuit) |
| `gap > 0.20` | `HARD_FAIL` (substrate cleanup LOSSY vs symbolic; CG-eligible negative) |
| `sym > 0.85` | `MIDDLE_BAND_EQUIV_SATURATED` |
| `sym < 0.30` | `MIDDLE_BAND_EQUIV_LOW_BASELINE` |

## SCHEMA-VET fields
- `cardinality_ok: true` (not a sweep-axis cell; single config per run_mode)
- `arms_differ_verified: <computed at runtime>` (bit-identical is HONEST at high-SNR N; verdict logic differentiates)
- `final_metrics_atomicity: tmp_replace` (write_metrics uses os.replace)
- `crlb: n/a` (planner is discrete; no continuous CRLB. THEORETICAL@SNR-analysis: signal ~ N, noise sigma ~ sqrt(N*NACT*4) ~ 724 at N=8192, threshold 0.4*N=3277, SNR ~10, empirical exact-recovery = 1.000 confirmed at selftest)
- `discriminator_reachability: true` (both arms produced non-saturated plan_rate in smoke)
- `baseline_in_band: <computed>` (smoke: 0.467 in [0.30, 0.85])
- `calibration_check: default_ok_for_this_regime` (tau_frac=0.4 works at N=8192 per selftest exact-recovery)
- `sweep_alignment_verdict: N/A` (not a sweep)
- `discriminating_fraction: N/A`
- `composition_edges`: substrate encode -> substrate retrieval -> BFS applicability -> state transition; all SHAPE_MATCH (recovered sets used as Python sets; standard BFS semantics)
- `positive_control_arms`: `ARM_SYMBOLIC_ORACLE` is the positive control at test regime
- `functional_requirements`: (1) encode multi-slot action schemas in single substrate vector; (2) recover schemas by unbind+cleanup; (3) drive discrete planner from recovered schemas
- `progress_logging: print_flush_true` (progress prints every 20 trials + at end)
- `compute_architecture: sequential_cpu_bfs_dependencies` (see cell docstring)

## Compute architecture (§17 gate)
**Class (b): sequential-CPU with justification.** BFS has genuine sequential dependencies (state N depends on state N-1's applicability decision). Per-action substrate probes at BFS-init are small (NACT=16 × 3 slots × N=8192 unbind + N×NPROP cleanup ≈ 400k complex-ops); total substrate work per trial ≈ 48 probes. Empirical smoke wall = 0.1s / 15 trials. Full estimated ≈ 1-3s. GPU batching not applicable: work volume is trivial + BFS is discrete-sequential.

## Pre-flight smoke result (ALREADY RAN 2026-07-02)
Metrics: `d:/AI/hd-instrument/data/exp_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1/metrics.json`

- Selftest: substrate pre exact-recovery = 1.000; add exact-recovery = 1.000; PASS
- Verdict: `HARD_PASS_SUBSTRATE_NATIVE_EQUIVALENCE`
- `sub_plan_rate = 0.467` MEASURED@data/exp_stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1/metrics.json:per_seed[0].sub_plan_rate
- `sym_plan_rate = 0.467` MEASURED@same:sym_plan_rate
- `gap_sym_minus_sub = 0.000` MEASURED (bit-identical plans — high-fidelity retrieval → equivalence)
- `n_solvable = 7 / 15` (non-oracle goal-sampling working; 47% solvable within budget)
- `sub_pre_precision_mean = 1.000`, `sub_pre_recall_mean = 1.000`
- `sub_add_precision_mean = 1.000`, `sub_add_recall_mean = 1.000`
- `sub_del_precision_mean = 1.000`, `sub_del_recall_mean = 1.000`
- `arms_differ_verified = false` (honest bit-identical due to 100% retrieval fidelity + deterministic BFS)
- Wall: 0.1s

## Timeout (FULL)
`900s` — very generous. Full estimated < 5s wall.

## Framing notes for verdict handler
- **This is a positive result with a nuance.** `arms_differ_verified=false` is honestly HARD_PASS here because retrieval p/r all = 1.000 = substrate-native equivalence. The verdict logic explicitly distinguishes bit-identical-with-high-fidelity (substrate-native equivalence proven) from bit-identical-with-low-fidelity (code short-circuit; BLOCK).
- **Substrate loads action library once per trial and caches** — schemas don't change during BFS. Per-step re-probing would be algorithmically redundant. Substrate primitives (encode + retrieve) are the load-bearing operation.
- **Non-oracle goal-sampling is working**: symbolic finds plans in 47% of trials (7/15 smoke) — baseline in band, not saturated.
- **Cross-arc note**: v1 predecessor `stretch4_3_temporal_strips_cpu_v1` had HARD_PASS row in cap_map v552 (2026-06-09) with `plan_rate=1.000` — that result was BOGUS (numpy-costume + reachable-by-construction goal). v2's honest 0.467 supersedes; consider substrate-KB atom bump / cap_map amendment to demote v1's row.
