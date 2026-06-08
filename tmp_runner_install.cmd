@echo off
echo === [%TIME%] install Node.js LTS via winget ===
winget install --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements 2>&1 | findstr /v "^$"

echo === [%TIME%] install Cloudflared via winget ===
winget install --id Cloudflare.cloudflared --silent --accept-source-agreements --accept-package-agreements 2>&1 | findstr /v "^$"

echo === [%TIME%] create .venv-demo for the v1 demo backend ===
set PY=C:\Users\marsh\AppData\Local\Programs\Python\Python311\python.exe
"%PY%" -m venv C:\dev\hd-instrument\.venv-demo 2>&1

echo === [%TIME%] upgrade pip in .venv-demo ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install --upgrade pip 2>&1 | findstr /I "Successfully Requirement"

echo === [%TIME%] install torch (cu121 wheel for RTX 4060 Ti) ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 2>&1 | findstr /I "Successfully Requirement Downloading"

echo === [%TIME%] install transformers + fastapi + uvicorn + numpy + pydantic + python-dotenv ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m pip install transformers accelerate fastapi "uvicorn[standard]" pydantic python-dotenv httpx openai anthropic 2>&1 | findstr /I "Successfully Requirement"

echo === [%TIME%] verify torch + CUDA + transformers ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'cap', torch.cuda.get_device_capability(0))"
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -c "import transformers, fastapi, uvicorn; print('transformers', transformers.__version__); print('fastapi', fastapi.__version__); print('uvicorn', uvicorn.__version__)"

echo === [%TIME%] verify Node + Cloudflared (may require new shell session) ===
where node 2>nul
where cloudflared 2>nul

echo === [%TIME%] DONE ===
