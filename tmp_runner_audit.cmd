@echo off
echo === python ===
where python 2>nul
python --version 2>&1
echo === node ===
where node 2>nul
node --version 2>&1
echo === npm ===
where npm 2>nul
npm --version 2>&1
echo === git ===
git --version 2>&1
echo === cloudflared ===
where cloudflared 2>nul
cloudflared --version 2>&1
echo === uv ===
where uv 2>nul
uv --version 2>&1
echo === conda ===
where conda 2>nul
conda --version 2>&1
echo === torch on default python ===
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'cap', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None)" 2>&1
echo === transformers ===
python -c "import transformers; print('transformers', transformers.__version__)" 2>&1
echo === fastapi ===
python -c "import fastapi; print('fastapi', fastapi.__version__)" 2>&1
echo === free disk ===
wmic logicaldisk where DriveType=3 get DeviceID,FreeSpace,Size /format:list 2>nul | findstr "="
echo === Existing schtasks dispatch queues ===
schtasks /query /tn "\hd_cpu_runner_0" /fo LIST 2>nul | findstr "TaskName Status"
schtasks /query /tn "\hd_gpu_runner_0" /fo LIST 2>nul | findstr "TaskName Status"
echo === orchestrator_paused.flag check ===
if exist "C:\dev\hd-instrument\data\orchestrator_paused.flag" (echo FLAG_PRESENT) else (echo FLAG_ABSENT)
echo === hd-instrument repo state ===
cd /d C:\dev\hd-instrument 2>nul && git rev-parse HEAD 2>&1 && git status -s 2>&1 | findstr /v "^$"
