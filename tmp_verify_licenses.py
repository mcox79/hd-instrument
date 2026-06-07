import os, sys
from pathlib import Path
TOK = Path(r"C:\dev\hd-instrument\.hf_token").read_text(encoding="utf-8").strip()
os.environ["HF_TOKEN"] = TOK
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from huggingface_hub import HfApi
api = HfApi()
for repo in ["meta-llama/Llama-3.1-8B", "meta-llama/Llama-3.1-70B"]:
    try:
        info = api.model_info(repo, token=TOK)
        print(f"OK: {repo} (last_modified={info.lastModified})")
    except Exception as e:
        print(f"FAIL: {repo} -> {type(e).__name__}: {str(e)[:200]}")
