# Pre-reg: RELATION-TYPE-RICHNESS LADDER (degree-sequence-matched) v1

**Anchor:** `relation_type_richness_ladder_v1`
**Cell:** `experiments/exp_relation_type_richness_ladder_v1.py`
**Filed:** 2026-07-09 by exp_dev. **Trigger:** research hand-off
`notes/exp_dev_handoff_research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`
(drill note `notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`).

## Question
The #4-VET result: substrate reasons OVER known knowledge but cannot infer BEYOND the ingested graph; held-out edges are
unpredictable from structure by ANY method (codes, classic LP, GNN). A density fix (k-core subsetting) was refuted as a
BRANCHINESS confound (denser subset = higher out-degree = harder routing). The drill argues the missing richness axis is
RELATION-TYPE / COMPOSITION-PATTERN diversity, not raw density/entity-count. This is the confound-fixed first test: does
raising the number of distinct relation TYPES (at MATCHED out-degree) raise the best-method inductive held-out score,
WHILE the known-degree oracle ceiling stays FLAT (proving the degree control held, unlike the k-core test)?

## Design
Reuses the #4 graph-inductive-ceiling harness VERBATIM (`experiments/exp_graph_inductive_ceiling_v1.py`, commit 84f46d6:
`run_regime` split + far-negatives + AUC + CN/AA/RA/JC/PA/GCN/CODE_COSINE). Ladder = nested relation-type sets ranked by
edge mass, rungs **k in {2, 5, 10, 16}** on the SAME common node set. Degree control: D* = per-node degree sequence of the
LOWEST rung (top-2 types); every rung uses configuration-model-style degree-preserving greedy resampling to approximate
D* per node from that rung's allowed-type pool (nested supersets => feasibility guaranteed; higher rungs fill the SAME
quota with a MORE DIVERSE type mix => richness varies, out-degree held).

- **PRIMARY metric** `best_inductive[rung]` = max over {CN,AA,RA,JC,GCN,CODE_COSINE} of held-out far-AUC.
  PA EXCLUDED (PA = deg(u)*deg(v) = the known-degree config-model oracle, not an inductive signal).
- **ORACLE / degree control** `ORACLE[rung]` = PA far-AUC = known-degree transition ceiling = branchiness/difficulty
  control (the same degree-artifact diagnostic that exposed the k-core density confound).

## Discriminator (pre-registered bands; from the research note, NOT loosened)
- **P1 richness axis:** `slope = best_inductive[k=16] - best_inductive[k=2]`.
- **P3 degree-control validity (MANDATORY GATE, checked FIRST):** `oracle_range_rel = (max-min ORACLE)/mean ORACLE`;
  `degree_range_rel = (max-min mean_degree)/mean mean_degree`.

| Verdict | Condition |
|---|---|
| `HARD_FAIL_DEGREE_CONTROL_FAILED_CONFOUNDED` | `oracle_range_rel > 0.15` OR `degree_range_rel > 0.10` (checked FIRST; confounded — repeats the k-core mistake; uninterpretable) |
| `HARD_PASS_RICHNESS_IS_LEVER` | `slope >= +0.05` AND `oracle_range_rel <= 0.10` AND `degree_range_rel <= 0.10` |
| `HARD_FAIL_RICHNESS_NOT_LEVER` | `|slope| < 0.05` (flat/non-monotonic) AND `degree_range_rel <= 0.05` (tight match) -> redirect to ULTRA-style cross-domain composition-pattern transfer |
| `MIDDLE_BAND_RICHNESS_LADDER` | otherwise |
| `INCONCLUSIVE_TOO_FEW_HELDOUT_OR_RUNG` | any rung has < 60 held-out edges or fails to build |

## Self-test (planted; MANDATORY assert_discriminator_fires; blocks dispatch if any fails)
- **POS** (composition genuinely enables inference at matched degree): two random base types (the k=2 floor, ~0.5) + one
  DENSE typed clique per added type => best_inductive MUST rise (`slope >= +0.05`).
- **NULL** (fake richness = more type LABELS, random edges, no composition) => best_inductive MUST NOT rise (`|slope| < 0.05`).
- **DEGREE** (oracle-detects-degree): fixed richness, varying preferential-attachment degree => ORACLE (PA) MUST MOVE
  (`range > 0.10`) — proves a flat oracle on real data genuinely certifies matched degree.
- `assert_discriminator_fires = POS_rises AND NULL_flat AND DEGREE_oracle_moves`.
- **MEASURED** (selftest, small n=260): `pos_slope=0.112`, `null_slope=-0.012`, `degree_probe_range=0.470`, ok=True
  MEASURED@`data/exp_relation_type_richness_ladder_v1_selftest/metrics.json:mechanism_selftest`.

## Anchor 0 audit (relation-type pool; embedded, no separate dispatch)
Ingested typed ConceptNet subgraph has **16 distinct relation types**. At N=5000: 14,767 edges; ~10 types with >=100
edges (IS_A 5001, CN_SYNONYM 2311, CN_RELATED_TO 2299, CN_MANNER_OF 1944, CN_AT_LOCATION 1364, PART_OF 551, CN_USED_FOR
518, CN_CAPABLE_OF 282, CN_HAS_PROPERTY 122, CN_HAS_A 115; tail: CAUSES 85, MOTIVATED 58, ANTONYM 46, DERIVED 45,
RECEIVES_ACTION 17, MADE_OF 9). MEASURED@Anchor-0-audit-2026-07-09. **Pool is workable** (not too thin to block the
ladder); honest caveat: k=10->16 adds mostly small-mass types (marginal richness gain vs k=2->10). Rung boundaries
{2,5,10,16} chosen by fixed rank-by-mass rule (not tuned for verdict).

## Bands / feasibility (tagged)
- HARD_PASS slope `+0.05` reachable: planted POS clears it (`+0.112` MEASURED). AUC chance floor 0.50 (THEORETICAL).
- HELDOUT_FRAC=0.30 + far-negative construction inherited VERBATIM from phase-0 M5 / #4 (`calibration_check:
  default_ok_for_this_regime`).

## SMOKE result (single seed, n=1800; REPORTED vs bands only, mechanism-story HELD)
MEASURED@`data/exp_relation_type_richness_ladder_v1_smoke/metrics.json`:
- **VERDICT: MIDDLE_BAND_RICHNESS_LADDER** (run_mode=smoke, 10.3KB, 24.7s).
- `best_inductive` k=[2,5,10,16] = [0.656, 0.640, 0.650, 0.666]; **slope = +0.010** (non-monotonic dip at k=5).
- **DEGREE CONTROL HELD**: `oracle_range_rel=0.057` (flat<=0.10), `degree_range_rel=0.085` (flat<=0.10),
  `degree_control_failed=False`. Richness genuinely varied: type_entropy [0.65,1.14,1.34,1.40], n_types_used [2,5,10,16].
- best inductive method = CODE_COSINE (~0.65-0.67, consistent with #4 codes ~0.70); classic LP CN/AA ~0.57, oracle PA ~0.62-0.65.
- Interpretation (SMOKE ONLY, held pending multi-seed FULL VET): the degree control WORKS cleanly; richness does not
  visibly move the inductive floor at smoke scale. MIDDLE (not HARD_FAIL) only because slope is marginally positive and
  degree_range 8.5% exceeds the 5% tight-match a clean HARD_FAIL_RICHNESS_NOT_LEVER requires.

## Compute architecture
class: **(b) sequential-CPU with justification** (inherits #4 VERBATIM: parameter-free neighbor-set predictors + one tiny
dense 2-layer GCN over n<=4500 + the phase-0 binding encoder). 4 rungs x 3 seeds sequential; no
loop-over-independent-points matmul; total wall < 2h FULL. Storage: `no_storage / no_composition`. Device-aware torch;
CPU adequate -> **remote_cpu_queue**. No GPU-batching speedup available (graph-analysis, not batched substrate primitive).

## SCHEMA-VET fields
- `cardinality_ok: true` — EXPECTED_N_UNITS = n_seeds (3); each seed must produce ALL 4 rungs (rung-cardinality gate) + arms-differ per rung.
- `arms_differ_verified: true` (>=4 distinct structural score sigs per rung, inherited #4 path).
- `final_metrics_atomicity: tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no BaseException / no bare except) — grep-gate PASSED.
- `crlb_floor_computed: 0.50` (AUC chance); `discriminator_reachability: true` (planted POS clears +0.05).
- `baseline_in_band: true` — planted NULL (must-not-rise) + POS (must-rise) + DEGREE (oracle-must-move) controls.
- `sweep_alignment_verdict: ALIGNED` (Gate A: swept param = n_distinct_relation_types; degree held => richness is the only varied axis; oracle-flat check certifies alignment empirically).
- `discriminating_fraction`: planted POS demonstrates the discriminating band (Gate B); real-data bands are deltas.
- `positive_control_arms`: CODE_COSINE reproduces the #4 code-cosine regime per rung (reported); #4 SBM-vs-ER separation inherited via run_regime primitives (Gate D).
- `functional_requirements`: (1) vary relation-type diversity -> nested mass-ranked rung sets; (2) hold branchiness -> degree-preserving greedy resampling to D*; (3) certify (2) -> PA oracle-flatness + mean-degree-flatness gate.
- `cell_chunked: false` (3 seeds in one cell; per-seed write_partial + rung-cardinality gate; single-cell acceptable — CPU, <2h, seeds independent within loop with per-seed failure-class capture).
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true` (per-rung emit_heartbeat), `defensive_error_checking: passed_all_4_patterns`.
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed/per-rung flush prints).
- `run_mode default: full` (explicit `--self-test`/`--smoke` flags); RUN_MODE post-dispatch verification required (§16).

## Honest risks (drill-flagged)
1. Relation-type pool (16, ~10 with mass) makes k=10->16 a marginal richness step — dynamic range is really k=2->10.
2. Degree-matching a labeled multi-relational graph is approximate; the oracle-ceiling-flat gate is the guard (fired
   clean in smoke: oracle_range 5.7%, degree_range 8.5%).
3. A HARD_PASS would be correlation, not causal composition — rule-mining (AMIE-style) follow-up noted (hand-off Anchor 2).

## Dispatch
- SMOKE: `local_cpu_queue` equivalent (ran locally, PASS — cell runs, selftest fires, degree control holds, all rungs valid).
- FULL: **remote_cpu_queue**, 3 seeds n=5000, timeout 7200s. exp_dev cannot push -> orchestrator ships the queue_add line.
