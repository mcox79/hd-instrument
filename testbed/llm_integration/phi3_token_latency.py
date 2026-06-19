"""Week 0 Missing 7 measurement #3: Phi-3-mini-4bit per-token latency.

Per testbed_handoff_substrate_llm_deep_integration_2026-05-31.md sec
WEEK 0 MISSING 7 -- LLM INTEGRATION LATENCY BUDGET CHARACTERIZATION
measurement (3).

Measures:
  Per-token generation latency at seq_len in {128, 512, 2048}
  100 generations per seq_len (after a warm-up).
  Reports mean + p99.

Phi-3-mini-3.8B at 4-bit NF4 quantization with double-quant; bf16 compute.
Loaded with bitsandbytes; fits in ~3.8 GB VRAM (RTX 4060 Ti 8GB target).

Decision criteria (per handoff sec; combined with #1 + #2 + #4):
  PASS  : end-to-end integrated query p99 < 50ms
  MIDDLE: in [50ms, 150ms]
  FAIL  : > 150ms (escalate to research before Week 1)

This script measures Phi-3 alone; the substrate+bridge+Phi-3 integrated
wall is phi3_integrated_latency.py (#4).

Run (REMOTE GPU only; do not run on CPU):
  python -m testbed.llm_integration.phi3_token_latency --device cuda

First run pulls ~3.8 GB Phi-3-mini-4bit from HuggingFace.
Writes data/testbed_missing7/phi3_token_latency_<device>.json.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import torch

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


_MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
_D_MODEL_EXPECTED = 3072


def _load_phi3_4bit(device: torch.device):
    """Load Phi-3-mini-4k-instruct at 4-bit NF4 + double-quant; bf16 compute."""
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)

    if device.type != "cuda":
        raise RuntimeError("Phi-3-mini-4bit requires CUDA (bitsandbytes).")

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    # trust_remote_code=False: use transformers' built-in Phi3 impl, not the
    # model author's modeling_phi3.py. The author's file expects the older
    # rope_scaling schema {"type": ...} which clashes with newer configs and
    # raises KeyError on load. Built-in impl handles current schema cleanly.
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        _MODEL_NAME,
        quantization_config=bnb_cfg,
        device_map={"": 0},
        trust_remote_code=False,
        attn_implementation="eager",
    )
    model.eval()
    return model, tokenizer


def _measure_per_token(model, seq_len: int, n_gen: int, device: torch.device,
                       seed: int) -> tuple[list[float], float]:
    """Measure per-token decode wall (ms) for n_gen tokens after prefill.

    Returns (samples_ms, prefill_ms). Each sample is the wall to produce
    one additional token given the kv-cache from the prior step.
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    vocab = model.config.vocab_size
    prompt_ids = torch.randint(0, vocab, (1, seq_len),
                               generator=g, dtype=torch.long).to(device)

    with torch.inference_mode():
        torch.cuda.synchronize()
        t_pre0 = time.perf_counter_ns()
        out = model(input_ids=prompt_ids, use_cache=True)
        torch.cuda.synchronize()
        t_pre1 = time.perf_counter_ns()
        prefill_ms = (t_pre1 - t_pre0) / 1e6

        past = out.past_key_values
        next_token = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)

        # warm-up 3 tokens (excluded from samples)
        for _ in range(3):
            out = model(input_ids=next_token, past_key_values=past,
                        use_cache=True)
            past = out.past_key_values
            next_token = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
        torch.cuda.synchronize()

        samples_ms: list[float] = []
        for _ in range(n_gen):
            torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            out = model(input_ids=next_token, past_key_values=past,
                        use_cache=True)
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            samples_ms.append((t1 - t0) / 1e6)
            past = out.past_key_values
            next_token = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)

    return samples_ms, prefill_ms


def _summarize(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"n": 0, "mean": 0.0, "min": 0.0, "p50": 0.0, "p95": 0.0,
                "p99": 0.0, "max": 0.0}
    s = sorted(samples)
    n = len(s)
    return {
        "n": n,
        "mean": round(statistics.fmean(s), 4),
        "min": round(s[0], 4),
        "p50": round(s[n // 2], 4),
        "p95": round(s[min(n - 1, int(n * 0.95))], 4),
        "p99": round(s[min(n - 1, int(n * 0.99))], 4),
        "max": round(s[-1], 4),
        "stdev": round(statistics.pstdev(s), 4) if n > 1 else 0.0,
    }


def run(device: torch.device, seeds: tuple[int, ...] = (7, 13, 17, 23, 31),
        seq_lens: tuple[int, ...] = (128, 512, 2048),
        n_gen_per_seed: int = 20) -> dict[str, Any]:
    """Run all Missing 7 #3 measurements; return structured results.

    n_gen_per_seed * len(seeds) = ~100 generations per seq_len (5*20=100).
    """
    results: dict[str, Any] = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "model_name": _MODEL_NAME,
        "quantization": "nf4_4bit_double_quant_bf16_compute",
        "seeds": list(seeds),
        "seq_lens": list(seq_lens),
        "n_gen_per_seed": n_gen_per_seed,
        "measurements": {},
        "prefill_latencies": {},
    }

    print(f"[phi3_token_latency] loading {_MODEL_NAME} (4-bit)...")
    t_load0 = time.perf_counter()
    model, tokenizer = _load_phi3_4bit(device)
    t_load1 = time.perf_counter()
    print(f"[phi3_token_latency] model loaded in {t_load1 - t_load0:.1f}s")
    print(f"[phi3_token_latency] d_model={model.config.hidden_size}")
    if model.config.hidden_size != _D_MODEL_EXPECTED:
        print(f"  WARN: d_model={model.config.hidden_size} != {_D_MODEL_EXPECTED} "
              f"(bridge_mlp_scaffold assumes 3072)")
    results["d_model"] = model.config.hidden_size

    for seq_len in seq_lens:
        all_samples: list[float] = []
        prefill_samples: list[float] = []
        for s in seeds:
            try:
                samps, prefill_ms = _measure_per_token(
                    model, seq_len, n_gen_per_seed, device, s)
                all_samples.extend(samps)
                prefill_samples.append(prefill_ms)
            except Exception as exc:
                print(f"[ERROR] seq_len={seq_len} seed={s}: {exc}",
                      file=sys.stderr)
        key = f"per_token_seq{seq_len}"
        results["measurements"][key] = _summarize(all_samples)
        results["prefill_latencies"][key] = _summarize(prefill_samples)
        m = results["measurements"][key]
        p = results["prefill_latencies"][key]
        print(f"  {key}: tok mean={m['mean']:.3f}ms p99={m['p99']:.3f}ms "
              f"| prefill mean={p['mean']:.1f}ms")

    # Phi-3 alone vs budget: per-token must fit in remaining budget
    # after substrate (20ms) + bridge (1ms) = 29ms remaining of 50ms
    seq512 = results["measurements"].get("per_token_seq512", {})
    tok_p99 = seq512.get("p99", 0.0)
    if tok_p99 < 29:
        verdict_phi = "PASS (per-token fits in remaining 29ms after substrate+bridge)"
    elif tok_p99 < 130:
        verdict_phi = "MIDDLE (per-token in [29,130]ms; integrated budget tight)"
    else:
        verdict_phi = "FAIL (per-token > 130ms; LLM is the bottleneck not substrate)"
    print()
    print(f"  Phi-3-alone verdict (per seq_len=512 p99 vs 29ms remaining "
          f"after substrate+bridge): {verdict_phi}")
    results["phi3_alone_verdict"] = verdict_phi
    results["budget_remaining_for_substrate_bridge_ms"] = max(
        0.0, 50.0 - tok_p99)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phi-3-mini-4bit per-token latency (Week 0 Missing 7 #3)")
    parser.add_argument("--device", default="auto",
                        help="cpu / cuda / auto (default auto)")
    parser.add_argument("--seeds", default="7,13,17,23,31",
                        help="Comma-separated seeds (default 5 seeds)")
    parser.add_argument("--seq-lens", default="128,512,2048",
                        help="Comma-separated seq lengths (default 128,512,2048)")
    parser.add_argument("--n-gen-per-seed", type=int, default=20,
                        help="Tokens generated per seed (default 20 -> 100/seq_len)")
    parser.add_argument("--out-dir", default="data/testbed_missing7",
                        help="Directory to write JSON results")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    seeds = tuple(int(s) for s in args.seeds.split(","))
    seq_lens = tuple(int(s) for s in args.seq_lens.split(","))

    print(f"[phi3_token_latency] device={device} torch={torch.__version__} "
          f"cuda={torch.cuda.is_available()}")
    print(f"[phi3_token_latency] seeds={seeds} seq_lens={seq_lens} "
          f"n_gen_per_seed={args.n_gen_per_seed}")
    print()

    results = run(
        device=device,
        seeds=seeds,
        seq_lens=seq_lens,
        n_gen_per_seed=args.n_gen_per_seed,
    )

    out_dir = _REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"phi3_token_latency_{device.type}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
