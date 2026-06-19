"""Week 0 Missing 7 measurement #2: bridge MLP latency.

Per testbed_handoff_substrate_llm_deep_integration_2026-05-31.md sec
WEEK 0 MISSING 7 -- LLM INTEGRATION LATENCY BUDGET CHARACTERIZATION
measurement (2).

Measures:
  Forward direction (substrate codeword -> LLM prefix):
    R^4096 -> R^2048 -> R^d_model=3072
  Reverse direction (LLM query head -> substrate query):
    R^d_model=3072 -> R^2048 -> R^4096
  Batch sizes: 1 and 8
  5 seeds; mean + p99 per measurement.

The bridge is a 2-layer MLP with GELU activation per the research design
doc Pattern 3 (Flamingo / LLaMA-Adapter style projection). Total params
~30M bidirectional (handoff target ~27M; within tolerance of the round
hidden-dim choice).

Bridge is RANDOM-INIT (Xavier). No training. This isolates compute cost
from learned-weight effects so the latency budget characterization is
architecture-level not training-state-dependent.

Decision criteria (combined with substrate_latency.py per handoff sec):
  PASS  : Path D depth=5 + bridge round-trip p99 < 50ms
  MIDDLE: in [50ms, 150ms]
  FAIL  : > 150ms p99

Run:
  python -m testbed.llm_integration.bridge_mlp_scaffold
  python -m testbed.llm_integration.bridge_mlp_scaffold --device cuda

Writes results to data/testbed_missing7/bridge_mlp_latency_<device>.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import torch
from torch import nn

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


_N_SUBSTRATE = 4096
_D_MODEL = 3072       # Phi-3-mini-3.8B hidden dim
_D_HIDDEN = 2048      # bridge hidden layer per research note


class ForwardBridge(nn.Module):
    """substrate codeword R^N -> R^d_model LLM prefix token."""

    def __init__(self, n_sub: int = _N_SUBSTRATE,
                 d_hidden: int = _D_HIDDEN, d_model: int = _D_MODEL) -> None:
        super().__init__()
        self.fc1 = nn.Linear(n_sub, d_hidden)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(d_hidden, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.act(self.fc1(x)))


class ReverseBridge(nn.Module):
    """LLM query head R^d_model -> R^N substrate query (continuous-relaxed)."""

    def __init__(self, d_model: int = _D_MODEL,
                 d_hidden: int = _D_HIDDEN, n_sub: int = _N_SUBSTRATE) -> None:
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_hidden)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(d_hidden, n_sub)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.act(self.fc1(x)))


def _measure_module(module: nn.Module, inp: torch.Tensor,
                    device: torch.device, n_reps: int) -> list[float]:
    """Measure forward-pass wall (ms) over n_reps. Returns per-rep samples."""
    module.eval()
    samples_ms: list[float] = []
    with torch.inference_mode():
        # warm-up (excluded from samples)
        for _ in range(3):
            _ = module(inp)
        if device.type == "cuda":
            torch.cuda.synchronize()

        for _ in range(n_reps):
            if device.type == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            _ = module(inp)
            if device.type == "cuda":
                torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            samples_ms.append((t1 - t0) / 1e6)
    return samples_ms


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


def _count_params(module: nn.Module) -> int:
    return sum(p.numel() for p in module.parameters())


def run(
    device: torch.device,
    n_reps: int = 100,
    seeds: tuple[int, ...] = (7, 13, 17, 23, 31),
    batch_sizes: tuple[int, ...] = (1, 8),
) -> dict[str, Any]:
    """Run all Missing 7 #2 measurements; return structured results."""
    results: dict[str, Any] = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "n_substrate": _N_SUBSTRATE,
        "d_model": _D_MODEL,
        "d_hidden": _D_HIDDEN,
        "seeds": list(seeds),
        "n_reps_per_seed": n_reps,
        "batch_sizes": list(batch_sizes),
        "measurements": {},
        "param_counts": {},
    }

    # Build bridges once per seed; only weights vary across seeds
    for direction_name, BridgeCls, d_in, d_out in [
        ("forward_R4096_to_R3072", ForwardBridge, _N_SUBSTRATE, _D_MODEL),
        ("reverse_R3072_to_R4096", ReverseBridge, _D_MODEL, _N_SUBSTRATE),
    ]:
        for B in batch_sizes:
            all_samples: list[float] = []
            for seed in seeds:
                torch.manual_seed(seed)
                bridge = BridgeCls().to(device)
                if "param_counts" not in results or direction_name not in results["param_counts"]:
                    results["param_counts"][direction_name] = _count_params(bridge)

                g = torch.Generator(device="cpu")
                g.manual_seed(seed + 42)
                # continuous-relaxed inputs: tanh-bounded, matches bridge training assumption
                inp = torch.tanh(torch.randn(B, d_in, generator=g)).to(device)

                try:
                    all_samples.extend(_measure_module(bridge, inp, device, n_reps))
                except Exception as exc:
                    print(f"[ERROR] {direction_name} B={B} seed={seed}: {exc}",
                          file=sys.stderr)

            key = f"{direction_name}_B{B}"
            results["measurements"][key] = _summarize(all_samples)
            m = results["measurements"][key]
            print(f"  {key}: mean={m['mean']:.4f}ms p99={m['p99']:.4f}ms")

    # Round-trip estimate: forward(B=1) + reverse(B=1)
    fwd_p99 = results["measurements"]["forward_R4096_to_R3072_B1"]["p99"]
    rev_p99 = results["measurements"]["reverse_R3072_to_R4096_B1"]["p99"]
    bridge_round_trip_p99 = fwd_p99 + rev_p99
    results["bridge_round_trip_p99_ms_B1"] = round(bridge_round_trip_p99, 4)

    total_params = sum(results["param_counts"].values())
    results["bidirectional_param_count"] = total_params

    print()
    print(f"  Bidirectional bridge params: {total_params/1e6:.2f}M "
          f"(handoff target ~27M)")
    print(f"  Round-trip p99 (B=1): {bridge_round_trip_p99:.4f}ms")

    # Bridge-only verdict against 50ms PASS target leaves substrate budget
    if bridge_round_trip_p99 < 5:
        verdict_bridge = "PASS (bridge well under budget; ample substrate headroom)"
    elif bridge_round_trip_p99 < 20:
        verdict_bridge = "MIDDLE (bridge fits but cuts into substrate budget)"
    else:
        verdict_bridge = "FAIL (bridge alone burns most of 50ms budget; needs redesign)"
    print(f"  Bridge-only verdict: {verdict_bridge}")
    results["bridge_only_verdict"] = verdict_bridge

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bridge MLP latency probe (Week 0 Missing 7 #2)")
    parser.add_argument("--device", default="auto",
                        help="cpu / cuda / auto (default auto)")
    parser.add_argument("--seeds", default="7,13,17,23,31",
                        help="Comma-separated seeds (default 5 seeds)")
    parser.add_argument("--out-dir", default="data/testbed_missing7",
                        help="Directory to write JSON results")
    parser.add_argument("--n-reps", type=int, default=100,
                        help="Reps per seed per measurement (default 100)")
    parser.add_argument("--batch-sizes", default="1,8",
                        help="Comma-separated batch sizes (default 1,8)")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    seeds = tuple(int(s) for s in args.seeds.split(","))
    batch_sizes = tuple(int(b) for b in args.batch_sizes.split(","))

    print(f"[bridge_mlp_scaffold] device={device} torch={torch.__version__} "
          f"cuda={torch.cuda.is_available()}")
    print(f"[bridge_mlp_scaffold] seeds={seeds} batch_sizes={batch_sizes}")
    print()

    results = run(
        device=device,
        n_reps=args.n_reps,
        seeds=seeds,
        batch_sizes=batch_sizes,
    )

    out_dir = _REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"bridge_mlp_latency_{device.type}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
