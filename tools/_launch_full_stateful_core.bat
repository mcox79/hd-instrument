@echo off
REM Direct GPU FULL launch for the stateful-core cell (argparse-gated: --full --device cuda).
REM This cell CANNOT go through the standard queue runner (runner spawns the script with NO CLI
REM flag -> SystemExit "must specify one of --self-test / --smoke / --full"), so FULL is a DIRECT
REM detached invocation on the GPU host. Fire via Win32_Process.Create (see notes recipe).
REM PRECONDITION: remote must be synced to the commit that honors --device (device-plumbing fix).
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe experimentsxp_stateful_core_situation_model_v1.py --full --seed 7 --n-random-init-seeds 5 --device cuda 1> data\_full_stateful_core.out 2> data\_full_stateful_core.err
echo DONE exit=%ERRORLEVEL% > data\_full_stateful_core.done
