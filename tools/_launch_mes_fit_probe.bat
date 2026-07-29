@echo off
REM Direct GPU launch for the stateful-core MES fit probe (argparse-gated: --sweep --device cuda).
REM This cell CANNOT go through the standard queue runner (runner spawns the script with NO CLI flag
REM -> SystemExit), so the sweep is a DIRECT detached invocation on the GPU host. Fire via
REM Win32_Process.Create. PUSH-FREE: the changed files are scp'd directly to the remote repo (no
REM origin push); this .bat is one of them.
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe experiments\exp_stateful_core_mes_fit_probe_v1.py --sweep --seeds 7 13 --device cuda 1> data\_mes_fit_probe.out 2> data\_mes_fit_probe.err
echo DONE exit=%ERRORLEVEL% > data\_mes_fit_probe_launch.done
