@echo off
set PY=C:\dev\hd-instrument\.venv-demo\Scripts\python.exe

echo === [%TIME%] downgrade transformers to 4.x for torch 2.5.1 compat ===
"%PY%" -m pip install "transformers<5.0" "tokenizers<0.21" "huggingface-hub<0.30" 2>&1 | findstr /I "Successfully Uninstalling Installing"
echo.

echo === [%TIME%] verify substrate + backend dirs exist (scp delivered) ===
dir /b C:\dev\hd-instrument\substrate 2>nul
echo ---
dir /b C:\dev\hd-instrument\backend 2>nul
echo.

echo === [%TIME%] all 8 substrate self-tests via .venv-demo ===
cd /d C:\dev\hd-instrument
for %%m in (core audit persistence khop confidence cascade gdpr bitemporal) do (
    echo --- substrate.%%m ---
    "%PY%" -m substrate.%%m 2>&1
)
echo.

echo === [%TIME%] backend import ===
"%PY%" -c "from backend.main import app; print('backend.main app routes:', len(app.routes))" 2>&1
echo.

echo === [%TIME%] Pythia-1.4B smoke ===
"%PY%" -c "import torch; from transformers import AutoModel, AutoTokenizer; print('VRAM start:', torch.cuda.memory_allocated()//(1024**2), 'MiB used / 8188 MiB total'); tok = AutoTokenizer.from_pretrained('EleutherAI/pythia-1.4b'); mdl = AutoModel.from_pretrained('EleutherAI/pythia-1.4b', torch_dtype=torch.bfloat16).to('cuda').eval(); print('VRAM after load:', torch.cuda.memory_allocated()//(1024**2), 'MiB'); t = tok('Substrate v1 demo smoke', return_tensors='pt').to('cuda'); h = mdl(**t).last_hidden_state; print('forward OK:', h.shape, h.dtype); print('VRAM after fwd:', torch.cuda.memory_allocated()//(1024**2), 'MiB')" 2>&1
echo.

echo === [%TIME%] Node + Cloudflared check (new shell session for PATH) ===
where node 2>&1
node --version 2>&1
where cloudflared 2>&1
cloudflared --version 2>&1
echo.

echo === [%TIME%] DONE ===
