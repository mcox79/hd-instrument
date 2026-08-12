@echo off
REM Direct GPU FULL launch for the encoder latent-PC (JEPA) cell (lever #1).
REM PUSH-FREE: cell + prereg + temporal_trace.py scp'd directly to the remote repo (no origin push).
REM Default run_mode = FULL (no --self-test / --smoke flag). --device cuda. 2 seeds [7,13], 4 arms, d512.
REM The built-in _cuda_safety_audit() runs 2 end-to-end LPC+TC steps on cuda BEFORE data prep (fail-fast).
REM -u = unbuffered stdout (defense-in-depth for live progress per section-17); cell also uses flush=True.
cd /d C:\dev\hd-instrument
.venv\Scripts\python.exe -u experiments\exp_encoder_latent_pc_arc_v1.py --device cuda 1> data\_full_encoder_latent_pc.out 2> data\_full_encoder_latent_pc.err
echo DONE exit=%ERRORLEVEL% > data\_full_encoder_latent_pc.done
