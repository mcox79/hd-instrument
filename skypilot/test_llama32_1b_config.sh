#!/usr/bin/env bash
# Test HF license access + config-only load for Llama-3.2-1B.
# Does NOT download model weights (config is ~1KB).
set +e

HF_TOK=$(cat /mnt/d/AI/hd-instrument/.hf_token 2>/dev/null)
if [ -z "${HF_TOK}" ]; then
  echo "ERROR: HF token not found at /mnt/d/AI/hd-instrument/.hf_token"
  exit 1
fi

source /root/skyvenv/bin/activate

echo "=== [1/3] HF Hub access check (model_info) ==="
python3 - <<PY
import os, sys
os.environ["HF_TOKEN"] = "${HF_TOK}"
try:
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    info = api.model_info("meta-llama/Llama-3.2-1B")
    print(f"OK: model_info accessible")
    print(f"  modelId: {info.modelId}")
    print(f"  gated: {getattr(info, 'gated', 'n/a')}")
    print(f"  private: {getattr(info, 'private', 'n/a')}")
    print(f"  last_modified: {getattr(info, 'last_modified', 'n/a')}")
    tags = getattr(info, 'tags', []) or []
    license_tags = [t for t in tags if 'license:' in t]
    print(f"  license tags: {license_tags}")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")
    if "403" in msg or "gated" in msg.lower() or "not authorized" in msg.lower():
        print("  -> License not accepted on this HF account for meta-llama/Llama-3.2-1B")
    sys.exit(2)
PY
rc1=$?

if [ $rc1 -ne 0 ]; then
    echo "License check failed; skipping config load test"
    exit $rc1
fi

echo ""
echo "=== [2/3] Config-only load (no weight download) ==="
python3 - <<PY
import os, json
os.environ["HF_TOKEN"] = "${HF_TOK}"
try:
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(
        "meta-llama/Llama-3.2-1B",
        token=os.environ["HF_TOKEN"],
    )
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
    # Param count estimate (rough)
    H = cfg.hidden_size
    L = cfg.num_hidden_layers
    I = cfg.intermediate_size
    V = cfg.vocab_size
    KV = getattr(cfg, 'num_key_value_heads', cfg.num_attention_heads)
    head_dim = H // cfg.num_attention_heads
    # Per-layer: attn (Q,K,V,O) + MLP (gate, up, down) + norms
    attn = H * H + 2 * KV * head_dim * H + H * H  # Q + K + V + O (GQA-aware)
    mlp = 3 * H * I  # gate, up, down (SwiGLU)
    norms = 2 * H
    per_layer = attn + mlp + norms
    embed = V * H  # tied input/output embeddings
    final_norm = H
    total = L * per_layer + embed + final_norm
    print(f"  estimated_params: {total / 1e9:.3f}B (L*{per_layer/1e6:.1f}M + embed {embed/1e6:.1f}M)")
    # Memory footprints
    bf16_gb = (total * 2) / 1e9
    fp32_gb = (total * 4) / 1e9
    print(f"  BF16 weights: ~{bf16_gb:.2f} GB")
    print(f"  FP32 weights: ~{fp32_gb:.2f} GB")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")
PY

echo ""
echo "=== [3/3] Tokenizer-only load (small download) ==="
python3 - <<PY
import os
os.environ["HF_TOKEN"] = "${HF_TOK}"
try:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.2-1B",
        token=os.environ["HF_TOKEN"],
    )
    print(f"OK: tokenizer loaded")
    print(f"  class: {type(tok).__name__}")
    print(f"  vocab_size: {tok.vocab_size}")
    sample = "The quick brown fox jumps over the lazy dog"
    ids = tok.encode(sample)
    print(f"  sample encode '{sample}' -> {len(ids)} tokens: {ids[:8]}...")
except Exception as e:
    et = type(e).__name__
    msg = str(e)[:300]
    print(f"FAIL: {et}: {msg}")
PY

echo ""
echo "=== done ==="
