@echo off
set PY=C:\Users\marsh\AppData\Local\Programs\Python\Python311\python.exe
echo === python311 ===
"%PY%" --version 2>&1
echo === torch ===
"%PY%" -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())" 2>&1
"%PY%" -c "import torch; print('VRAM total', torch.cuda.get_device_properties(0).total_memory // (1024**3), 'GB')" 2>&1
echo === transformers ===
"%PY%" -c "import transformers; print('transformers', transformers.__version__)" 2>&1
echo === fastapi ===
"%PY%" -c "import fastapi; print('fastapi', fastapi.__version__)" 2>&1
echo === pip list relevant ===
"%PY%" -m pip list 2>nul | findstr /I "torch transformers fastapi uvicorn numpy sentence-transformers"
echo === hd-instrument repo ===
cd /d C:\dev\hd-instrument 2>nul
git rev-parse HEAD 2>&1
git status -s 2>&1 | findstr /v "^$"
echo === orchestrator_paused.flag ===
if exist "C:\dev\hd-instrument\data\orchestrator_paused.flag" (echo PRESENT) else (echo ABSENT)
echo === HF cache ===
dir C:\Users\marsh\.cache\huggingface\hub 2>nul | findstr "models--"
echo === schtasks ===
schtasks /query /tn "\hd_cpu_runner_0" 2>nul | findstr "\\"
schtasks /query /tn "\hd_gpu_runner_0" 2>nul | findstr "\\"
echo === GPU ===
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv 2>nul
echo === ports already in use ===
netstat -an | findstr "LISTEN" | findstr ":3000 :8000 :8001 :5173"
echo === DONE ===
