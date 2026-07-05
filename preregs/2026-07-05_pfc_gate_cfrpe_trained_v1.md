# PRE-REG: pfc_gate_cfrpe_trained_v1

**Date:** 2026-07-05
**Author:** exp_dev (Opus 4.8 1M, agent-spawn)
**Cell:** `experiments/exp_pfc_gate_cfrpe_trained_v1.py`
**Anchor:** `pfc_gate_cfrpe_trained_v1`
**Thrust:** brain-component-driven development (top-ranked build: TRAIN the measured-weak PFC-BG gate with the substrate-native cfrpe RPE signal as a Go/NoGo competitive gate).
**Status:** LOCKED before FULL dispatch. Smoke landed (local CPU); FULL staged for orchestrator (GPU preferred).

## Prior-work check (concept-query mandate)
`bash tools/substrate_query.sh "PFC basal ganglia Go NoGo gate trained reward prediction error temporal credit assignment successor representation"` -> top hits are GENERIC concept atoms only: `Dopamine reward prediction error` (cosine 0.333), `basal_ganglion` (0.327), `basal ganglia action selection` (0.302) from a June multi-drive-arbitration research drill + wordnet. NO prior experiment CELL implementing an RPE-trained gate at cosine>0.30. Composition is genuinely NOVEL (not a rediscovery).

## Hypothesis
The PFC-BG goal-conditioned gate is MEASURED-WEAK. v3 (static additive-bias) HARD_FAILed:
- MEASURED@data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only/metrics.json: V1=0.352, ADD(best a=0.2)=0.420 (add_lift=+0.068), WM=0.396, ORACLE=0.994, headroom=0.642 (depth=6, N=8192, V=2400).
- Static goal-cosine bias is only informative on the LAST hop (goal-sim ~random on early hops of a multi-hop chain), so it closes only ~11% of the 0.642 oracle headroom.

Brain claim (PBWM/Frank-O'Reilly 2004/2006; Schultz 1997): the BG Go/NoGo gate is TRAINED by a dopaminergic reward-prediction-error signal that performs TEMPORAL CREDIT ASSIGNMENT (propagates goal-value backward through the chain). We test whether adding that missing training signal closes materially more headroom.

## Mechanism (composes two already-proven substrate primitives; no new representational machinery)
- **cfrpe RPE signal** = the substrate's error-driven delta-rule outer-product update (borrowed EXACTLY from `exp_substrate_adaptive_cfrpe_x_k2_compose_v1`, incl. the adaptive per-sample LR clamp error/median in [0.25, 4.0]).
- **Successor-feature transport M** (Dayan-1993 SR / Stachenfeld-2017 hippocampal-striatal SR) trained by TD(0): `E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M)`. The TD-error IS the canonical reward-prediction-error. M is trained on EXPLORATION rollouts only (random walks over the operator graph); it NEVER sees the goal or op_seq. gamma=0.85.
- **reach(cand;goal) = cos(E[cand]@M, E[goal])** -- high iff goal is a discounted successor of cand (the early-hop signal the static gate lacks).
- **Go/NoGo competition:** `Go_i = w_manifold*manifold_i + w_goal*goal_sim_i + w_reach*reach_i`; gate = argmax_i Go_i (winner-take-all; non-winners = NoGo). w_reach tuned on TRAIN rollouts only (w_reach==0 reduces GONOGO exactly to ADDITIVE_BASELINE -> any lift is attributable to the RPE-trained reach; a null result is a clean reduction).

## ANTI-TAUTOLOGY (VET steer 2026-07-05, load-bearing)
v3's HARD_FAIL was PARTLY TAUTOLOGICAL (WM and additive arms were the same target-cosine signal; combined was byte-identical to WM). To be decisive, the RPE-trained reach MUST carry information INDEPENDENT of raw target-cosine. Structural guarantee: M is trained on transition DYNAMICS, never on the goal. Made FALSIFIABLE by:
- **ARM_CFRPE_CONTROL_IDENTITY**: gonogo with reach:=target-cosine (M:=identity). If real-M gonogo does NOT beat this control (`dynamics_lift <= 0.05`), the win is target-cosine in disguise -> NOT chain-grade (demoted).
- **reach-vs-targetcosine correlation guard**: Pearson corr over candidate reach vs target-cosine on the held-out trajectory; `corr >= 0.85` => reach is target-cosine in disguise -> demote.
- **ST7 self-test**: on a two-live-branch toy, trained-M separates on-path from off-path by 0.63 while target-cosine separates by 0.03 (MEASURED@self-test). The control is uninformative exactly where M is informative.

## Arms (paired -- all share E, W_ops, and the SAME test chains per seed)
| Arm | Description | Role / rail |
|---|---|---|
| ARM_V1_NO_GOAL | goal-blind manifold reference | rail ~0.35 (v3) |
| ARM_ADDITIVE_BASELINE | static additive goal-bias, alpha tuned on train | positive control: additive_lift in [0.03,0.10] (reproduces v3 +0.068) |
| ARM_CFRPE_CONTROL_IDENTITY | gonogo with reach:=target-cosine (M=identity) | anti-tautology foil |
| ARM_CFRPE_TRAINED_GONOGO | SR/TD-transport Go/NoGo trained by cfrpe | THE TEST |
| ARM_ORACLE | applies true op_seq | rail >= 0.90; ceiling ~0.99 |

## PRE-REG BANDS (LOCKED; decision_depth=6 at FULL)
Primary: `gonogo_lift = GONOGO - ADDITIVE`; `dynamics_lift = GONOGO - CONTROL`.
- **HARD_PASS** (chain-grade eligible): `gonogo_lift >= 0.155` (META_RULE_L strict floor = 0.15 + 0.05*(0.15-0.05)) AND `dynamics_lift > 0.05` AND `reach_tcos_corr < 0.85` AND `cv(gonogo) < 0.10` AND paired sign-test `p < 0.05` AND mechanism-fires `reach_rank_acc_test > 0.30` AND rails OK (oracle>=0.90, 0.05<additive<0.95, additive_lift>0) AND arms differ.
- **HARD_FAIL**: `gonogo_lift <= 0.05` (RPE training adds nothing beyond the static rule; thrust wrong -- gate weakness is architectural).
- **MIDDLE_BAND**: `gonogo_lift in (0.05, 0.155)`, OR `gonogo_lift >= 0.155` but NOT dynamics-attributable/corr-ok (`MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE`).
- **HP_SCOPE**: HARD_PASS gates apply ONLY to `cfrpe_trained_gonogo` (vs additive + control). Rails apply to v1/additive/oracle. v1/control are NOT held to the chain-grade lift gate.

**discriminator_reachability = TRUE**: additive~0.42, oracle~0.99 => 0.57 headroom reachable; +0.155 lands at ~0.575, well inside feasibility. Fireable BOTH ways (see anti-tautology + generalization-failure paths).

## SCHEMA-VET mandatory fields
- `cardinality_ok`: True. `EXPECTED_N_UNITS = n_arms(5) * n_seeds * n_depths`. FULL = 5*5*2 = 50. SMOKE = 5*3*2 = 30. Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if completed < expected.
- `arms_differ_verified`: True (per-chain op-trace SHA256; gonogo vs additive must differ at decision depth UNLESS w_reach==0 -> `arms_differ_exempted`).
- `final_metrics_atomicity`: `tmp_replace` (os.replace on metrics.json + per-seed partials via write_partial_key).
- `crlb_n/a`: "accuracy-lift discriminator has no single closed-form noise floor; reachability declared via additive->oracle headroom feasibility (0.57 >> 0.155)".
- `baseline_in_band`: True at smoke (additive=0.115 in (0.05,0.95)); enforced at FULL (HARD_FAIL_ADDITIVE_RAIL otherwise).
- `calibration_check`: `adaptive_with_discriminator_gate` (adaptive cf-RPE per-sample LR clamp; reach_rank + dynamics_lift + corr guards logged; discriminator still fires verified at smoke).
- `cell_chunked`: False (EXEMPT). Multi-seed but uses `_seed_checkpoint` per-seed partials (resumable; runner death loses only the in-flight seed). Per-seed runtime short (~8s smoke; minutes on GPU FULL). Matches v3 single-file-multi-seed heritage.
- `start_marker_written`: True. `crash_diagnostic_present`: True (Exception -> CELL_CRASHED + traceback, atomic). `heartbeat_present`: True (_heartbeat.jsonl per seed). `defensive_error_checking`: passed (start marker + crash diag + heartbeat + per-seed failure-class + no silent continue; seed crash -> partial with failure_class + demote-from-HP).
- `progress_logging`: `print_flush_true` (line_buffering + flush=True on all progress lines; SR training prints per-seed err/M_norm).
- `run_mode default`: `full` (explicit `--smoke`/`--self-test` for the other modes) -> RUN_MODE_MISMATCH guard.

### Gate A -- effective vs nominal parameter audit
No V_C/M/alpha capacity sweep. Depth is a genuine axis (each depth = separate exact-length chain set); all arms see the same chains. `sweep_alignment_verdict: ALIGNED`.

### Gate B -- bracket includes discriminating band
Predicted decision-depth accuracies: additive ~0.42 (v3), gonogo target ~0.50-0.60, oracle ~0.99. Non-oracle arms land in [0.30,0.70]. `discriminating_fraction ~ 1.0` (>> 0.30). Smoke MEASURED additive=0.115, gonogo=0.479 (both non-saturated, non-floor).

### Gate C -- signal-shape compatibility
Composition edges (all SHAPE_MATCH):
- cfrpe delta-rule (error [b,N]) -> M [N,N] update: outer product `E[cur]^T @ (error*lr)`; shapes match.
- M [N,N] -> reach: `E[cand]@M` [b,N] cos `E[goal]` [b,N]; match.
- reach [b] -> Go-score [b] linear combine with manifold/goal_sim [b]; match.
No SHAPE_MISMATCH_no_adapter.

### Gate D -- reproduce prior chain-grade result as positive control
`ARM_ADDITIVE_BASELINE` reproduces v3's additive gate AT MATCHED FULL REGIME (N=8192, V=2400, 4 ops, 500 triples/op, depth 6): cited prior `additive_lift = +0.068` (MEASURED@v3 metrics). Tolerance 0.04 -> `additive_lift in [0.03, 0.10]`; outside band => `HARD_FAIL_ADDITIVE_RAIL` (invocation/regime mismatch, downstream suspect). Regime-extension audit: SAME synthetic-bipolar-chain regime as v3 (no synthetic->narrative drift). Smoke MEASURED additive_lift=0.073 (in band -> rail reproduces).

### Gate E -- functional requirement decomposition
1. "Same content, different goal -> different op-selection" -> goal-conditioned Go-value (goal_sim + reach).
2. "Early-hop credit assignment (is candidate on a path to goal)" -> SR transport M reach-value (the NEW piece; no prior primitive addressed this -> the build).
3. "Winner-take-all action selection" -> argmax Go/NoGo competition (existing router-style primitive).
4. "Do not leak the answer" -> M trained on exploration only; held-out test chains; no op_seq access (only ORACLE sees op_seq).

## Compute architecture
Class **(a) batched-GPU**. SR-TD training, operator application, cleanup, reach are all batched torch matmuls; per-hop op-selection is batched ACROSS chains (chains independent; only within-chain hops sequential). FULL strongly prefers overnight_queue (GPU) -- SR training is matmul-heavy (per GPU-batching-mandatory rule). Remote CPU feasible but slow. Device = cuda-if-available else cpu.
Storage strategy: **sharded** (each operator is its own W matrix; no bundled item store). M is a learned value operator, not an item store.

## Discriminator-survives-scale
Option **B (analytical) + C (smoke preview)**. The reach signal is INFORMATIONAL (early-hop reachability via learned dynamics), not capacity-limited: `reach_rank_acc` > chance is scale-robust in DIRECTION even as absolute accuracy shifts with N/V and depth. Smoke (easier N/V=10, depth 4) MEASURED reach_rank_test=0.576 (>> 0.25 chance), dynamics_lift=0.438, gonogo_lift=0.365 -- mechanism fires strongly. FULL (v3-matched N/V=3.4, depth 6/8) will give the canonical effect size; depth 8 tests whether the gap WIDENS with depth (temporal-credit-assignment prediction). Note: smoke effect size is at an easier regime and is NOT the FULL claim; FULL is canonical.

## SMOKE RESULT (local CPU, N=2048, V=200, 3 seeds, depths {3,4}, dd=4) -- MEASURED
`MEASURED@data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json`:
- V1=0.042, ADD(a=0.37)=0.115, CTRL=0.042, GONOGO=0.479, ORACLE=0.969
- gonogo_lift=+0.365, dynamics_lift=+0.438, additive_lift=+0.073 (in rail band)
- reach_tcos_corr=-0.086 (corr_ok), reach_rank_test=0.576, sign_p=0.0000 (go_only=40 add_only=5)
- cv=0.187, mech_fires=True, rails_ok=True, add_rail_in_band=True, arms_differ=True, cardinality_ok=True (30/30)
- Verdict = MIDDLE_BAND (label driven ONLY by cv=0.187 > 0.10 at 32-chain smoke scale; effect size massively clears HP floor). SMOKE GATE PASSED: cell runs, rails hold, discriminator fires decisively in PASS direction, anti-tautology controls green. cv expected to tighten at FULL (120 chains, 5 seeds).

## Self-test (formula correctness) -- MEASURED, ALL PASS
ST1 cfrpe TD shrinks RPE 0.088->0.001; ST2 adaptive LR ordering; ST3 Go/NoGo argmax; ST4 mechanism-fires reach on-path 0.66 >> off-path 0.03; ST5 pipeline (5 arms, oracle 0.875 toy); ST6 binomial symmetric; ST7 anti-tautology trained-sep 0.63 >> control(targetcos)-sep 0.03.

## Falsifiable predictions (FULL)
- HARD_PASS (thrust confirmed): gonogo_lift >= 0.155, dynamics-attributable, cross-seed cv<0.10.
- HARD_FAIL (thrust wrong -- weakness is architectural not training-signal): gonogo_lift <= 0.05.
- MIDDLE_BAND: 0.05 < gonogo_lift < 0.155, or a lift not attributable to learned dynamics.

## Cites
- data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only/metrics.json (v3 rails)
- experiments/exp_pfc_goal_conditioned_gate_v3_wm_additive_only.py (harness heritage)
- experiments/exp_substrate_adaptive_cfrpe_x_k2_compose_v1.py (cfrpe adaptive delta-rule)
- notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md (Section 4 build spec)
