"""Verify that the runner's .hf_token can authorize Llama-3.2-1B config download."""
import os
import sys

REPO = "C:/dev/hd-instrument"  # runner path
tok_path = os.path.join(REPO, ".hf_token")
if not os.path.exists(tok_path):
    print(f"FAIL: token missing at {tok_path}")
    sys.exit(2)

tok = open(tok_path, "r", encoding="utf-8").read().strip()
print(f"  token: len={len(tok)} prefix={tok[:5]}...")

os.environ["HF_TOKEN"] = tok

try:
    from transformers import AutoConfig, AutoTokenizer
except Exception as e:
    print(f"FAIL: transformers import error: {e}")
    sys.exit(3)

try:
    cfg = AutoConfig.from_pretrained("meta-llama/Llama-3.2-1B", token=tok)
    print(f"  CONFIG_OK hidden={cfg.hidden_size} "
          f"layers={cfg.num_hidden_layers} vocab={cfg.vocab_size}")
except Exception as e:
    print(f"FAIL: AutoConfig: {type(e).__name__}: {str(e)[:200]}")
    sys.exit(4)

try:
    tok_obj = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B", token=tok)
    sample_ids = tok_obj.encode("hello world")
    print(f"  TOKENIZER_OK class={type(tok_obj).__name__} "
          f"sample_ids_len={len(sample_ids)}")
except Exception as e:
    print(f"FAIL: AutoTokenizer: {type(e).__name__}: {str(e)[:200]}")
    sys.exit(5)

print("PASS: runner has valid Llama-3.2-1B access")
