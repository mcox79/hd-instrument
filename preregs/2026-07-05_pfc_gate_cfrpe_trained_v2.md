# PRE-REG: pfc_gate_cfrpe_trained_v2

**Date:** 2026-07-05
**Author:** exp_dev (Opus 4.8 1M, agent-spawn)
**Cell:** `experiments/exp_pfc_gate_cfrpe_trained_v2.py`
**Anchor:** `pfc_gate_cfrpe_trained_v2`
**Thrust:** brain-component-driven development (give the RPE-trained PFC-BG Go/NoGo gate a FAIR test after v1's broken-rail HARD_FAIL).
**Status:** LOCKED before FULL dispatch. Smoke landed HARD_PASS (local CPU, direct). FULL staged for orchestrator (GPU preferred; remote_cpu_queue feasible).

## Prior-work check (concept-query mandate)
`bash tools/substrate_query.sh "cfrpe RPE-trained Go/NoGo gate successor-feature transport additive baseline in-band rail-trip fair regime"` -> top hit cosine=0.2607 (a ConceptNet-eval SCHEMA-VET note; unrelated). NO prior experiment CELL at cosine>0.30. This is a direct continuation of my own v1 arc (fair-regime + better-SR redo), genuinely NOT a rediscovery.

## Why v2 (VET diagnosis, atom commit f144563ee)
v1 FULL landed `HARD_FAIL_ADDITIVE_RAIL`, but the landed-VET proved it was a BROKEN-RAIL TEST-DESIGN FAILURE, not a structural collapse:
- MEASURED@`data/exp_pfc_gate_cfrpe_trained_v1/metrics.json` (N=8192, V=2400 => N/V=3.41, decision_depth=6): V1=0.013, ADD(a=0.14)=0.015, CTRL=0.018, GONOGO=0.100, ORACLE=0.958. The additive BASELINE (0.015) fell BELOW its 0.05 measurability floor -> the rail-priority branch fired HARD_FAIL before the gonogo comparison was reached.
- The RPE mechanism is ALIVE + scale-robust: gonogo/additive ratio ~6.7x@d6; paired sign_p=1.2e-14 (go_only=52, add_only=1); reach_rank_test=0.495 (>0.25 chance); reach_tcos_corr=-0.045 (target-cosine independent).
- MEASURED@`data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json` (a FAIR regime N=2048, V=200 => N/V=10.24, dd=4): ADD=0.115 (IN BAND), GONOGO=0.479, ORACLE=0.969 -> closure = (0.479-0.115)/(0.969-0.115) = 0.426. Only blocked from HP by cv=0.187 (n_test=32 sampling-noise dominated).

**Diagnosis:** the fair regime is SHALLOWER decision depth + HIGHER N/V. At depth 6 the compounding (chain acc = per_hop^depth) both floors the baseline AND starves the absolute gonogo-additive gap; at depth 4-5 with N/V ~ 7-10 the baseline lands in band and the mechanism advantage survives.

## Two fixes (the whole point of v2)
1. **FAIR REGIME** -- sweep V (the lever that reliably moves the baseline back into band) at decision_depth in {4,5}, holding density constant. Each regime carries an EXPLICIT `baseline_in_band` gate (0.05 < additive < 0.95). A regime whose baseline floors/saturates is declared NOT-FAIR and cannot be read as a structural verdict (this is the META_RULE the VET atomized). The `V2400_d6` regime is an in-cell GATE-D POSITIVE CONTROL reproducing v1's exact floored condition.
2. **BETTER-TRAINED SR** -- boost rollout coverage (~50*V transitions vs v1's ~16.7*V), SR steps (3000->8000), batch (128->256), and add a linear LR decay schedule (1.0 -> 0.2*base). Target per-hop `reach_rank_test > ~0.50` at fair regimes.

## Mechanism (unchanged from v1; composes two already-proven substrate primitives)
- **cfrpe RPE signal** = substrate error-driven delta-rule outer-product update (adaptive per-sample LR clamp error/median in [0.25, 4.0]) with FIX-2 global linear LR decay.
- **Successor-feature transport M** (Dayan-1993 SR / Stachenfeld-2017) trained by TD(0): `E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M)`, gamma=0.85. TD-error IS the RPE. M trained on EXPLORATION rollouts only (never sees goal/op_seq).
- **reach(cand;goal) = cos(E[cand]@M, E[goal])** -- early-hop reachability signal.
- **Go/NoGo:** `Go_i = w_manifold*manifold_i + w_goal*goal_sim_i + w_reach*reach_i`; argmax_i (WTA). alpha + w_reach tuned on TRAIN only; w_reach==0 reduces GONOGO exactly to ADDITIVE_BASELINE.

## Anti-tautology (VET steer; load-bearing)
- **ARM_CFRPE_CONTROL_IDENTITY** (reach:=target-cosine, M=identity): if real-M gonogo does not beat it (`dynamics_lift <= 0.05`), the win is target-cosine in disguise -> demote to MIDDLE_BAND.
- **reach-vs-targetcosine corr guard**: `reach_tcos_corr >= 0.85` => demote.
- **ST7 self-test**: trained-M separates on/off-path by 0.63 vs target-cosine 0.03 (MEASURED@self-test).

## Arms (paired -- all share E, W_ops, and the SAME test chains per regime+seed)
| Arm | Description | Role / rail |
|---|---|---|
| ARM_V1_NO_GOAL | goal-blind manifold reference | reference |
| ARM_ADDITIVE_BASELINE | static additive goal-bias, alpha tuned on train | in-band gate subject; the number to beat |
| ARM_CFRPE_CONTROL_IDENTITY | gonogo with reach:=target-cosine (M=identity) | anti-tautology foil |
| ARM_CFRPE_TRAINED_GONOGO | SR/TD-transport Go/NoGo trained by cfrpe | THE TEST |
| ARM_ORACLE | applies true op_seq | rail >= 0.90 |

## Regimes (V, decision_depth) -- N fixed per mode; V swept so N/V brackets the fairness band
- **FULL** (N=8192): `V800_d4` (N/V=10.24), `V1200_d4` (6.83), `V2400_d4` (3.41), `V800_d5`, `V1200_d5`, `V2400_d5`, `V2400_d6` (Gate-D floored positive control). density=0.21 constant; n_train_triples_per_op = round(0.21*V).
- **SMOKE** (N=2048): `V200_d4` (N/V=10.24), `V600_d4` (3.41). N/V ratios EQUAL the FULL bracket ends -> matched per-hop cleanup difficulty (discriminator-preview at matched N/V, option C).

## PRE-REG BANDS (LOCKED) -- per-regime, at that regime's decision_depth
Primary per fair regime: `closure = (GONOGO - ADDITIVE) / (ORACLE - ADDITIVE)`; `gonogo_lift = GONOGO - ADDITIVE`; `dynamics_lift = GONOGO - CONTROL`.
- **HARD_PASS**: EXISTS a FAIR regime (0.05 < additive < 0.95) where `closure >= 0.25` (contract: closes >=25% of headroom) AND `cv(gonogo) < 0.10` AND `reach_tcos_corr < 0.85` AND `dynamics_lift > 0.05` AND paired sign-test `p < 0.05` AND mechanism-fires `reach_rank_test > 0.30` AND `oracle >= 0.90` AND arms differ.
- **HARD_FAIL** (`HARD_FAIL_RPE_NO_HELP`): fair regime(s) exist AND at ALL of them `gonogo_lift <= 0.05` (mechanism genuinely does not help when the test IS fair).
- **MIDDLE_BAND**: fair regime helps (`gonogo_lift > 0.05`) but no fair regime clears the full HP bar -- sub-classified `MIDDLE_BAND_HELPS_BELOW_25` / `MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE` / `MIDDLE_BAND_CV_TOO_HIGH`.
- **INCONCLUSIVE_NO_FAIR_REGIME**: NO regime lands the baseline in band (all floored/saturated) -- a REGIME-MISS reported explicitly, NOT a structural verdict. This is the META_RULE guard: a rail-trip cannot masquerade as a mechanism verdict.
- **HP_SCOPE**: HP gates apply ONLY to `cfrpe_trained_gonogo` vs `additive_baseline` at a FAIR regime; oracle rail applies to `oracle`. v1/control not held to the closure gate.
- **cv gate**: cv<0.10 is a FULL-scale cross-seed stability gate (n_test=240, sampling std ~0.032). It is NOT fairly evaluable at smoke n_test (sampling-noise dominated) -> `cv_gate_enforced = (RUN_MODE=='full')`; reported-but-non-blocking in smoke (`focus_cv_meets_full_gate` logged).

**discriminator_reachability = TRUE**: v1-smoke already MEASURED closure=0.426 at a fair regime, well above the 0.25 HP floor. Fireable BOTH ways (HARD_FAIL if SR does not generalize -> w_reach->0 -> gonogo~additive; MIDDLE_BAND if a closure win is not dynamics-attributable).

## SCHEMA-VET mandatory fields
- `cardinality_ok`: EXPECTED_N_UNITS = n_arms * n_seeds * n_regimes = 5 * 5 * 7 = 175 (FULL); smoke 5*3*2=30. Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if completed < expected.
- `baseline_in_band` (META_RULE_AG): explicit per-regime 0.05 < additive < 0.95; verdict keys on fair regimes only.
- `arms_differ_verified` (META_RULE_AF): per-regime per-seed gonogo vs additive op-trace SHA256 must differ when w_reach>0; `arms_differ_exempted` when w_reach==0 (legitimate reduction). Smoke MEASURED: no collisions, all wr>0.
- `final_metrics_atomicity`: tmp_replace (os.replace on metrics.json).
- `except SystemExit: raise` before `except Exception` (no BaseException); grep gates pass.
- `crlb_n/a`: accuracy-closure discriminator has no single closed-form noise floor; reachability declared via v1-smoke MEASURED closure=0.426 feasibility.
- `discriminator_reachability`: TRUE (see above).
- `calibration_check`: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank>0.30 mechanism-fires gate logged per regime).
- `cell_chunked`: false (single-cell multi-seed with per-seed resumable checkpoints via `_seed_checkpoint`; runner-death loses at most in-flight seed, partials preserved).
- `start_marker_written`: true. `crash_diagnostic_present`: true (CELL_CRASHED + traceback). `heartbeat_present`: true (per-seed _heartbeat.jsonl). `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: print_flush_true (line-buffered stdout + flush=True on all progress lines + per-seed heartbeat; FULL timeout_s >= 1800).
- Gate A `sweep_alignment_verdict`: ALIGNED -- swept axis is (V, decision_depth); every primitive (cleanup, additive, gonogo, oracle, SR) experiences the same V/depth the discriminator measures (no partition indirection).
- Gate B `discriminating_fraction`: smoke MEASURED 2/2 regimes in the discriminating/fair band (additive 0.185, 0.269; closure 0.36 each). FULL predicts >=4/7 fair (V800/V1200 at dd4,5 fair; V2400_d6 intentionally floored control). >= 0.30. PASS.
- Gate C `composition_edges`: SR-transport M output -> reach cosine -> Go/NoGo score is SHAPE_MATCH (all [B,n] tensors; scalar scores). No SHAPE_MISMATCH.
- Gate D `positive_control_arms`: `V2400_d6` reproduces v1 FULL's floored-baseline condition at the matched regime (N=8192, V=2400, dd=6). Expected additive floored ~0.015 -> baseline_in_band=False -> EXCLUDED from verdict (demonstrates meta-rule, no rail-trip). ARM_ADDITIVE also reproduces the static-bias baseline as the number-to-beat.
- Gate E `functional_requirements`: (1) early-hop reachability signal -> cfrpe-trained SR transport M; (2) competitive gate -> Go/NoGo argmax WTA; (3) fair measurability -> per-regime baseline_in_band gate; (4) anti-tautology -> identity-reach control + corr guard.

## Compute architecture
(a) batched-GPU. SR-TD training, operator application, cleanup, reach are batched matmuls on cuda-if-available. Chains batched; within-chain hops sequential (genuine dependency). Storage strategy: SHARDED (each operator its own W matrix; M is a learned value operator, not an item store; no bundled store). FULL strongly prefers overnight_queue (GPU); remote_cpu_queue feasible but slower for SR.

## SMOKE RESULT (MEASURED, local CPU direct, 58s wall, 3 seeds)
MEASURED@`data/exp_pfc_gate_cfrpe_trained_v2_smoke/metrics.json`: `HARD_PASS` | n_fair=2/2 | focus V200_d4: ADD=0.185(IN BAND) GONOGO=0.472 CTRL=0.185 ORACLE=0.981 closure=0.360 dynamics_lift=0.287 reach_rank_test=0.509 reach_tcos_corr=-0.079 sign_p<0.0001 (go_only=36 add_only=5) oracle_rail=True; V600_d4: closure=0.359 dynamics_lift=0.250 reach_rank=0.544 in_band=True. cv=0.127 reported non-blocking (smoke n_test=36 sampling-noise dominated; FULL n_test=240 -> sampling std 0.032). Cardinality 30/30. AF: no hash collisions. arms_differ_verified=True.

## FULL dispatch parameters
- Queue: overnight_queue (GPU) preferred; remote_cpu_queue acceptable.
- Timeout: 3600s (est. 10-15 min GPU; 15 SR trainings at 8000 steps + 7-regime x 5-seed arm eval).
- Requires push to origin/main (harness-denied to exp_dev) -> route via orchestrator.
