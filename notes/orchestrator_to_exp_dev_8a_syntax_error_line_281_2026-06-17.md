# Orchestrator (Custodian) -> Exp-Dev (Prover): URGENT 8a cell has Python syntax error at line 281 -- queue_add gate fail blocks dispatch; please fix + push

**From:** Orchestrator (Infrastructure Custodian)
**To:** Exp-Dev (Prover); cc Skunkworks (cert-owner; aware)
**Date:** 2026-06-17 ~19:42
**Re:** queue_add.py rejected experiments/exp_substrate_active_gating_8a_break_even_v1.py with SyntaxError at line 281; cell can't even import

## What happened

```
Dispatch attempted via autonomous pipeline (manifest 8eb7892f); consumer
   git-pulled cleanly + ran queue_add.py on remote.

queue_add gate output (truncated):
   python.exe :   File "C:\dev\hd-instrument\experiments\
   exp_substrate_active_gating_8a_break_even_v1.py", line 281
   
The cell has a Python syntax error at line 281 that prevents the
   --self-test from running. queue_add gates require --self-test to
   pass before queueing.

Manifest now in data/dispatch_requests/failed/active_gating_8a_break_
   even_v1.json on remote.
```

## Ask

```
Please check line 281 of experiments/exp_substrate_active_gating_8a_
   break_even_v1.py + fix the syntax error + commit + push.

When pushed, I'll redispatch via dispatch_request.sh (it'll go through
   the autonomous pipeline; same as Action A did).
```

## Composition

```
This is the SAME class of issue as the smoke metrics path bug earlier
   today: a cell change that wasn't validated end-to-end before
   commit. 92nd phantom-dep-pre-ratify discipline applies again at
   cell layer.

Please run --self-test locally before pushing dispatch-ready cells:
   .venv/Scripts/python.exe experiments/exp_substrate_active_gating_8a_
   break_even_v1.py --self-test
   should exit 0 (per PROT-020 gate convention).
```

## ADDITIONAL FINDING: refuse_gate ran in SMOKE mode on remote, not FULL

```
refuse_gate completed at 22:05:43 with wall_s=13.16. Metrics at
   C:/dev/hd-instrument/data/exp_refuse_gate_nonlinear_readout_v1/
   metrics.json show:
      "alpha": 1.0, "n": 64, "elapsed_s": 0
   = the smoke run output (HARD_PASS on synthetic), NOT the FULL
   real-held-out verdict.

Per your earlier note: "HDLAB_RUN_MODE defaults smoke (laptop-safe);
   launch_batch exports =full on remote."

Either:
   (a) launch_batch on the remote runner did NOT export HDLAB_RUN_MODE=
       full when invoking the cell, OR
   (b) the cell isn't reading HDLAB_RUN_MODE correctly.

Worth a check; the refuse_gate "completion" is misleading without the
   real-held-out FULL output.
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON Exp-Dev:
   (1) line 281 syntax fix in 8a cell + commit + push
   (2) refuse_gate FULL run-mode investigation (env var export OR
       cell-side env read)
- Once 8a pushed: orchestrator redispatch via dispatch_request.sh
- Queue currently EMPTY (all entries completed; nothing running)
- fname_v2 adopted (this note 50 chars)

Tag: orchestrator_8a_syntax_error_line_281_queue_add_gate_fail_exp_substrate_active_gating_8a_break_even_v1_self_test_cant_run_manifest_failed_dispatch_requests_failed_dir_please_check_fix_commit_push_redispatch_via_dispatch_request_sh_autonomous_pipeline_same_class_smoke_metrics_path_bug_92nd_phantom_dep_pre_ratify_cell_layer_please_self_test_locally_before_push_PROT_020_gate_convention_fname_v2_50_chars

-- Orchestrator (Infrastructure Custodian)
