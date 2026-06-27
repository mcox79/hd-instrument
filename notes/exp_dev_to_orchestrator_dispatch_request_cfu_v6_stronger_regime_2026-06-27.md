# Dispatch request: M-CFU v6 stronger regime

From: exp_dev
To: orchestrator
Date: 2026-06-27
Commit: 638d1cd5 (alone; 2 files; 1564 insertions; path-scoped to
        experiments/ + preregs/ only)
Pause flag: NOT present (verified)
Routing: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive;
         harness-DENIED push constraint -> orchestrator dispatches
         via queue_add.sh)

---

## Cell: edge_importance_v6_CFU_stronger_regime

Cell name (HDLAB_EXP_NAME): `edge_importance_v6_CFU_stronger_regime`
Script: `experiments/exp_edge_importance_v6_CFU_stronger_regime.py`
Prereg: `preregs/2026-06-27_edge_importance_v6_CFU_stronger_regime.md`
Queue: `remote_cpu_queue`
Recommended --timeout: `5400` (1.5hr; ~16min nominal full run;
       3 CFU variants per (alpha, seed) + alpha-sweep + 4x probe vs
       v5; 5.6x buffer for queue contention / cold start / continuous-
       downscale variant cost)

Dispatch command:
```bash
bash tools/orchestrator/queue_add.sh remote_cpu_queue \
  edge_importance_v6_CFU_stronger_regime \
  experiments/exp_edge_importance_v6_CFU_stronger_regime.py \
  preregs/2026-06-27_edge_importance_v6_CFU_stronger_regime.md \
  5400
```

## Why this cell

v5 (M-CFU) Skunkworks-tiered MIDDLE_BAND: FIRST mechanism in edge-
importance family to PASS fairness (cor(CFU,|W|)=-0.015 vs +0.83 for
trace-family which sources degree-skewed signal). v5 sel_unretr=+0.037
short of the +0.15 PASS bar. Brain-grounded (Tonegawa optogenetic
engram-silencing analog; chain-grade in neuroscience). Structurally
orthogonal to magnitude.

USER 2026-06-27: "let's try for stronger v6". v6 applies 4
strengthening levers from drill (`notes/research_drill_cortex_
importance_backup_mechanisms_2026-06-27.md` Section M-CFU):

  L1 BIGGER PROBE: M_HELDOUT 100->400, N_PROBE 100->400 (4x; 2x lower
     noise floor)
  L2 LEAVE-K-OUT K=5 variant (multi-atom co-importance)
  L3 ALPHA SWEEP {1.5, 2.0, 2.5, 3.0} (finds loudest signal regime)
  L4 CONTINUOUS DOWNSCALE GRADIENT 5 levels (importance = integral
     of recall-deficit over weight-fraction; more signal per atom
     than v5 binary endpoint)

5 arms (BASELINE_RANDOM + TRACE_ONLY + CFU_LEAVE_ONE_OUT_LARGE_PROBE +
CFU_LEAVE_K_OUT + CFU_CONTINUOUS_DOWNSCALE) x 4 alpha x 3 seeds =
60 arm entries.

META_RULE_U brain-mechanism-vs-caricature: CFU IS the brain mechanism
(Tonegawa). v6 STRENGTHENS measurement (bigger probe, gradient
sampling, multi-atom) without substituting any smooth function of H or
magnitude proxy. Leave-one-out ablation against held-out probe set
preserved load-bearing.

## HARD_PASS bands

All 4 must hold:
1. best v6 CFU sel_unretr asymmetry >= 0.15 (ORIGINAL Path A bar)
2. AND cor(best_CFU, |W|) < 0.30 absolute (META_RULE_F fairness; v5
   win preserved)
3. AND mechanism fires (n_downscaled > 0 AND n_ablations > 0 AND
   cfu_variance > 0 on EACH CFU arm at EACH alpha)
4. AND best_v6_sel >= V5_BASELINE_SEL_CFU + 0.05
   (V5_BASELINE_SEL_CFU = +0.037 measured 2026-06-27; v6 bar = +0.087)

## HARD_FAIL

A. fairness regression (any CFU arm at any alpha |cor| >= 0.30)
B. best_v6_sel <= V5_BASELINE_SEL_CFU (stronger regime did NOT help)
C. mechanism inert (n_downscaled / n_ablations / cfu_variance == 0)
D. saturation (all 5 arms across all alphas within 0.05 on
   rec_RETRIEVED)
E. D3 any caught exception
F. D4 cardinality breach (observed_arm_entries != 60)

## MIDDLE_BAND HONEST_BOUND

best_v6_sel in [0.08, 0.15] + fairness held + mechanism fired + lift
>= +0.02 over v5 -> ship as new band annotation; lifts ceiling
estimate for M-CFU family.

## D1/D2/D3/D4 disciplines all wired

- D1 discriminator-must-survive-scale: smoke uses FULL-N + FULL probe
  (only J / seeds / alphas reduced). Gate: smoke best_v6_sel > v5 +
  0.02 OR halt-and-route.
- D2 smoke-must-FIRE-discriminator: 3 CFU arms each must show
  n_ablations > 0 + cfu_variance > 0 per (alpha, seed).
- D3 no-silent-except: setup + each CFU variant + each arm wrapped;
  per-(alpha, seed) and per-arm exceptions recorded + verdict halts.
- D4 cardinality_ok: 60 arm entries TOTAL (4 alphas x 3 seeds x 5
  arms); HARD_FAIL on breach.
- SCHEMA-VET 5b per-arm HP scope: each arm's metrics fully reported
  per (alpha, seed) in per_alpha_seed[].arms[]; verdict reads per-arm
  fields not summary text (Fix #28).

## Pre-flight verification (exp_dev side)

- ASCII-only verified (53388 bytes cell; 10237 bytes prereg; both
  pass decode('ascii') roundtrip; no unicode, no em-dashes, no
  emojis).
- --self-test PASS at module-import time (8 axioms: argmax determinism,
  cohort ablation hurts atom recall, downscale monotone in fraction,
  continuous integral non-zero when binary positive, continuous fires
  non-flat variance, fairness orthogonality synthetic, alpha-grid
  feasible at all 4 targets, CFU schedule load-bearing constraints
  honored).
- D3 no-silent-except wrapped: setup + CFU_LARGE_PROBE + CFU_LEAVE_K +
  CFU_CONTINUOUS + each of 5 arms (per-(alpha, seed) granularity).
- D4 cardinality_ok pre-reg fields explicit (EXPECTED_N_UNITS=60;
  per-(alpha, seed) sub-count=5; verdict halts on either breach).
- D1 discriminator-must-survive-scale: smoke @ N=512 (FULL) +
  N_PROBE_BATCH=400 (FULL) + M_HELDOUT=400 (FULL); ALPHA_GRID=[2.5]
  representative.
- D2 smoke-fires-discriminator built into self-tests
  (_selftest_continuous_uses_full_gradient confirms non-flat variance
  at smoke scale).
- Routing-sanity gate-friendly: numpy-only (0 torch/cuda imports;
  verified `grep -c 'import torch\|from torch' = 0`); no large-N
  literal (N=512); remote_cpu_queue correct route.
- Substrate-only-decode gate: n_llm_calls per (alpha, seed) = 0
  (_LLM_CALL_COUNTER hardcoded to never increment; verdict halts on
  any_llm violation).
- numpy>=2.0 compat: np.trapz aliased to np.trapezoid if absent;
  remote .venv either-numpy compatible.

## Post-dispatch verification expected (orchestrator + remote)

- queue_add.sh POST-SHIP-VERIFY: cell present in remote queue.json
  (script validates this automatically; exits non-zero on miss).
- Remote --self-test invocation by runner before full run (queue_add.py
  default behavior); --self-test must PASS on remote .venv before full
  dispatch proceeds.
- On landing: metrics.json in `data/edge_importance_v6_CFU_stronger_
  regime/metrics.json` with fields: verdict, verdict_msg, per_alpha_
  seed[].arms[] with full HP-scope schema, cardinality_ok bool,
  v5_baseline_sel_cfu (cross-cell anchor=+0.037).
- 12 partial files: `partial_metrics_alpha{1.5,2.0,2.5,3.0}_seed{7,
  17,23}.json` (write_partial_key compound key).
- Notify Skunkworks for landed-VET via SendMessage / TaskCompleted
  hook on cell completion.

## Standing / waiting-on

exp_dev waiting on: orchestrator to invoke queue_add.sh (harness-
DENIED push from exp_dev). Cell + prereg filed + committed (638d1cd5;
path-scoped: experiments/ + preregs/ only; no incidental drift); ball
in orchestrator's court.
