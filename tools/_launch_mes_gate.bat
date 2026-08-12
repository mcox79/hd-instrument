@echo off
REM Direct detached launch for the data-sufficient MES gate (argparse-gated: --gate).
REM Push-free: this .bat + the cell files are scp-delivered to the remote working copy.
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe experiments\exp_stateful_core_mes_data_sufficient_gate_v1.py --gate --device cuda 1> data\_mes_gate_launch.out 2> data\_mes_gate_launch.err
echo DONE exit=%ERRORLEVEL% > data\_mes_gate_launch.procdone
