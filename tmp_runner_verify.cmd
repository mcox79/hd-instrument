@echo off
cd /d C:\dev\hd-instrument
echo === [%TIME%] git pull on runner ===
git fetch origin 2>&1 | findstr /v "^$"
git pull origin main 2>&1 | findstr /v "^$"
echo.

echo === [%TIME%] all substrate module self-tests via .venv-demo ===
set PY=C:\dev\hd-instrument\.venv-demo\Scripts\python.exe
for %%m in (core audit persistence khop confidence cascade gdpr bitemporal) do (
    echo --- substrate.%%m ---
    "%PY%" -m substrate.%%m 2>&1
)
echo.
echo === [%TIME%] backend imports ===
"%PY%" -c "from backend.main import app; print('backend.main app routes:', len(app.routes))" 2>&1
echo.

echo === [%TIME%] Pythia-1.4B smoke (~30s; check VRAM fit) ===
"%PY%" -c "import torch; from transformers import AutoModel, AutoTokenizer; print('VRAM before:', torch.cuda.memory_allocated()//(1024**2), 'MiB used'); tok = AutoTokenizer.from_pretrained('EleutherAI/pythia-1.4b'); mdl = AutoModel.from_pretrained('EleutherAI/pythia-1.4b', torch_dtype=torch.bfloat16).to('cuda').eval(); print('VRAM after load:', torch.cuda.memory_allocated()//(1024**2), 'MiB used / 8188 MiB total'); t = tok('Substrate v1 demo smoke test', return_tensors='pt').to('cuda'); h = mdl(**t).last_hidden_state; print('forward pass OK; last hidden:', h.shape, h.dtype); print('VRAM after forward:', torch.cuda.memory_allocated()//(1024**2), 'MiB used')" 2>&1
echo.
echo === [%TIME%] DONE ===
