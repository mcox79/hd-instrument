@echo off
REM Direct REMOTE-CPU launch for the stateful-core generalization-curve DIAGNOSTIC.
REM Argparse-gated (--run --device cpu); cannot go through the standard queue runner, so this is a
REM DIRECT detached invocation on marsh@home via Win32_Process.Create (see report / smoke precedent).
REM MES-only, Arm-A only, seed 7, train sizes 64/128/256/512 vs a fixed held-out eval.
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe experiments\diag_stateful_core_gen_curve_v1.py --run --seed 7 --device cpu 1> data\_diag_gen_curve.out 2> data\_diag_gen_curve.err
echo DONE exit=%ERRORLEVEL% > data\_diag_gen_curve.done
