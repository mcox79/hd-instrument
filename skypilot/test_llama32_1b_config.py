"""Test HF license + config load for Llama-3.2-1B. No weight download."""
import os
import sys
from pathlib import Path

TOK_PATH = Path(__file__).resolve().parents[1] / ".hf_token"
tok = TOK_PATH.read_text(encoding="utf-8").strip()
if not tok:
    print("ERROR: empty .hf_token")
    sys.exit(1)
os.environ["HF_TOKEN"] = tok

MODEL = "meta-llama/Llama-3.2-1B"

print(f"=== [1/3] HF Hub access check (model_info) for {MODEL} ===")
try:
    from huggingface_hub import HfApi
    api = HfApi(token=tok)
    info = api.model_info(MODEL)
    print(f"OK: model_info accessible")
    print(f"  modelId: {info.modelId}")
    print(f"  gated: {getattr(info, 'gated', 'n/a')}")
    print(f"  private: {getattr(info, 'private', 'n/a')}")
    print(f"  last_modified: {getattr(info, 'last_modified', 'n/a')}")
    tags = getattr(info, "tags", []) or []
    license_tags = [t for t in tags if "license" in t.lower()]
    print(f"  license tags: {license_tags}")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")
    if "403" in msg or "gated" in msg.lower() or "not authorized" in msg.lower():
        print("  -> License not accepted on this HF account for " + MODEL)
    sys.exit(2)

print()
print(f"=== [2/3] Config-only load (no weight download) ===")
try:
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(MODEL, token=tok)
    print(f"OK: config loaded")
    print(f"  model_type: {cfg.model_type}")
    print(f"  hidden_size: {cfg.hidden_size}")
    print(f"  num_hidden_layers: {cfg.num_hidden_layers}")
    print(f"  num_attention_heads: {cfg.num_attention_heads}")
    print(f"  num_key_value_heads: {getattr(cfg, 'num_key_value_heads', 'n/a')}")
    print(f"  intermediate_size: {cfg.intermediate_size}")
    print(f"  vocab_size: {cfg.vocab_size}")
    print(f"  max_position_embeddings: {cfg.max_position_embeddings}")
    print(f"  torch_dtype: {getattr(cfg, 'torch_dtype', 'n/a')}")
    H = cfg.hidden_size
    L = cfg.num_hidden_layers
    I = cfg.intermediate_size
    V = cfg.vocab_size
    KV = getattr(cfg, "num_key_value_heads", cfg.num_attention_heads)
    head_dim = H // cfg.num_attention_heads
    attn = H * H + 2 * KV * head_dim * H + H * H
    mlp = 3 * H * I
    norms = 2 * H
    per_layer = attn + mlp + norms
    embed = V * H
    final_norm = H
    total = L * per_layer + embed + final_norm
    print(f"  estimated_params: {total/1e9:.3f}B "
          f"(L*{per_layer/1e6:.1f}M + embed {embed/1e6:.1f}M)")
    print(f"  BF16 weights: ~{(total*2)/1e9:.2f} GB")
    print(f"  FP32 weights: ~{(total*4)/1e9:.2f} GB")
    # Map paper Algorithm 1 layer range (latter half: L/2 .. L)
    median_layer = L // 2
    band = L - median_layer + 1
    print(f"  Algorithm 1 layer band: [{median_layer}..{L-1}] = {band} layers "
          f"(0-indexed; size for Llama-3.1-8B comparison: 32-layer model has band of 17)")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")

print()
print(f"=== [3/3] Tokenizer-only load ===")
try:
    from transformers import AutoTokenizer
    tk = AutoTokenizer.from_pretrained(MODEL, token=tok)
    print(f"OK: tokenizer loaded")
    print(f"  class: {type(tk).__name__}")
    print(f"  vocab_size: {tk.vocab_size}")
    sample = "The quick brown fox jumps over the lazy dog"
    ids = tk.encode(sample)
    print(f"  sample encode '{sample}' -> {len(ids)} tokens: {ids[:8]}...")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")

print()
print("=== done ===")
