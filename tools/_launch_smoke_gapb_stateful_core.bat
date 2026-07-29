@echo off
REM Direct GPU RE-SMOKE launch for the stateful-core cell AFTER audit-gap-B (entity-role-query
REM addressing key). Argparse-gated (--smoke --device cuda): cannot go through the queue runner, so
REM this is a DIRECT detached invocation, fired via Win32_Process.Create (mirrors the full recipe).
REM PRECONDITION: remote synced to the gap-B commit (exp_dev cannot push; orchestrator syncs first).
REM Config == prior re-smoke: seed 7, SMOKE_EPOCHS=25 x SMOKE_BATCH=8 (=200 steps/arm), grad-clip=1.0,
REM 64 train / 32 eval, MES+KD both arms, 1 random-init-core control seed.
REM NEW sentinel/out/err names (_smoke_gapb.*) so this does NOT collide with the prior
REM _smoke_stateful_core.* launch files. Metrics land at data\exp_stateful_core_situation_model_v1_smoke\metrics.json
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe experiments\exp_stateful_core_situation_model_v1.py --smoke --seed 7 --n-random-init-seeds 1 --device cuda 1> data\_smoke_gapb.out 2> data\_smoke_gapb.err
echo DONE exit=%ERRORLEVEL% > data\_smoke_gapb.done
