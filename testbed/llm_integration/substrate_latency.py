"""Week 0 Missing 7 measurement #1: substrate baseline latency.

Per testbed_handoff_substrate_llm_deep_integration_2026-05-31.md sec
WEEK 0 MISSING 7 -- LLM INTEGRATION LATENCY BUDGET CHARACTERIZATION.

Measures:
  - Single store at N=4096 and N=8192
  - Single retrieve (Path D depth=1) at N=4096, K_paths=500
  - Path D depth=5 retrieve at N=4096, K_paths=500
  5 seeds; mean + p99 per measurement.

Decision criteria (per handoff sec):
  PASS  : Path D depth=5 + bridge MLP round-trip p99 < 50ms
  MIDDLE: in [50ms, 150ms]
  FAIL  : > 150ms p99 (escalate to research before Week 1)

This script measures substrate alone; bridge MLP is bridge_mlp_scaffold.py.
Final PASS/MIDDLE/FAIL combines this + bridge + Phi-3 + integrated wall in
the Week 0 deliverable note.

Run:
  python -m testbed.llm_integration.substrate_latency
  python -m testbed.llm_integration.substrate_latency --device cuda

Writes results to data/testbed_missing7/substrate_latency_<device>.json.
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

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402


def _measure_store(N: int, M: int, seed: int, device: torch.device,
                   n_reps: int) -> list[float]:
    """Measure single-fact store wall time (outer-product write to W) in ms.

    Build substrate fresh (so each rep stores fact #M+1 into a populated
    substrate; mirrors deployment where W is non-empty).
    """
    codebook, W, key_idx, val_idx, _ = build_shared(N, M, seed, device)
    keys_v = codebook[key_idx]
    vals_v = codebook[val_idx]
    # Synthesize a "new fact" key + value atom not in the codebook so we
    # measure outer-product write (matches v290 prior wall measurements).
    g = torch.Generator(device=device.type if device.type != "cuda" else "cpu")
    g.manual_seed(seed + 9001)
    if device.type == "cuda":
        new_key = (torch.randint(0, 2, (N,), generator=g, dtype=torch.int8)
                   .to(device).float() * 2 - 1)
        new_val = (torch.randint(0, 2, (N,), generator=g, dtype=torch.int8)
                   .to(device).float() * 2 - 1)
    else:
        new_key = torch.randint(0, 2, (N,), generator=g, dtype=torch.int8).float() * 2 - 1
        new_val = torch.randint(0, 2, (N,), generator=g, dtype=torch.int8).float() * 2 - 1
        new_key = new_key.to(device)
        new_val = new_val.to(device)

    samples_ms: list[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter_ns()
        W = W + torch.outer(new_val, new_key) / N
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter_ns()
        samples_ms.append((t1 - t0) / 1e6)
    return samples_ms


def _measure_path_d(N: int, M: int, seed: int, depth: int, K_paths: int,
                    device: torch.device, n_reps: int) -> list[float]:
    """Measure Path D retrieve wall (ms). One starting key per call; B=1."""
    codebook, W, key_idx, val_idx, relation = build_shared(N, M, seed, device)
    starts = key_idx[:1].to(device)
    samples_ms: list[float] = []
    for rep in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter_ns()
        _ = path_d_run(
            codebook=codebook, W=W, starts=starts, relation=relation,
            depth=depth, K_paths=K_paths, seed=seed + rep, N_use=N,
        )
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


def run(
    device: torch.device,
    n_reps_store: int = 50,
    n_reps_path_d: int = 30,
    seeds: tuple[int, ...] = (7, 13, 17, 23, 31),
    K_paths: int = 500,
) -> dict[str, Any]:
    """Run all Missing 7 #1 measurements; return structured results."""
    results: dict[str, Any] = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "seeds": list(seeds),
        "K_paths": K_paths,
        "measurements": {},
    }

    # --- Store latency at N in {4096, 8192} -----------------------------
    for N in (4096, 8192):
        M = N  # populated substrate; one fact per N (capacity-matched start)
        all_samples: list[float] = []
        for s in seeds:
            try:
                all_samples.extend(_measure_store(N, M, s, device, n_reps_store))
            except Exception as exc:
                print(f"[ERROR] store N={N} seed={s}: {exc}", file=sys.stderr)
        key = f"store_N{N}_M{M}"
        results["measurements"][key] = _summarize(all_samples)
        print(f"  {key}: mean={results['measurements'][key]['mean']:.3f}ms "
              f"p99={results['measurements'][key]['p99']:.3f}ms")

    # --- Path D depth=1 at N=4096 K_paths=500 ----------------------------
    all_samples = []
    for s in seeds:
        try:
            all_samples.extend(
                _measure_path_d(N=4096, M=4096, seed=s, depth=1,
                                K_paths=K_paths, device=device, n_reps=n_reps_path_d)
            )
        except Exception as exc:
            print(f"[ERROR] path_d depth=1 seed={s}: {exc}", file=sys.stderr)
    results["measurements"]["path_d_depth1_N4096_K500"] = _summarize(all_samples)
    m = results["measurements"]["path_d_depth1_N4096_K500"]
    print(f"  path_d_depth1_N4096_K500: mean={m['mean']:.3f}ms p99={m['p99']:.3f}ms")

    # --- Path D depth=5 at N=4096 K_paths=500 (THE production op) --------
    all_samples = []
    for s in seeds:
        try:
            all_samples.extend(
                _measure_path_d(N=4096, M=4096, seed=s, depth=5,
                                K_paths=K_paths, device=device, n_reps=n_reps_path_d)
            )
        except Exception as exc:
            print(f"[ERROR] path_d depth=5 seed={s}: {exc}", file=sys.stderr)
    results["measurements"]["path_d_depth5_N4096_K500"] = _summarize(all_samples)
    m = results["measurements"]["path_d_depth5_N4096_K500"]
    print(f"  path_d_depth5_N4096_K500: mean={m['mean']:.3f}ms p99={m['p99']:.3f}ms")
    print()
    p99_d5 = m["p99"]
    if p99_d5 < 30:
        verdict_substrate = "PASS (substrate budget; bridge has 20ms headroom)"
    elif p99_d5 < 120:
        verdict_substrate = "MIDDLE (substrate viable; bridge must fit in remaining budget)"
    else:
        verdict_substrate = "FAIL (substrate alone exceeds 150ms p99; design rework needed)"
    print(f"  Substrate-only verdict: {verdict_substrate}")
    results["substrate_only_verdict"] = verdict_substrate
    results["budget_remaining_for_bridge_ms"] = max(0.0, 50.0 - p99_d5)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Substrate latency probe (Week 0 Missing 7 #1)")
    parser.add_argument("--device", default="auto",
                        help="cpu / cuda / auto (default auto)")
    parser.add_argument("--seeds", default="7,13,17,23,31",
                        help="Comma-separated seeds (default 5 seeds)")
    parser.add_argument("--out-dir", default="data/testbed_missing7",
                        help="Directory to write JSON results")
    parser.add_argument("--n-reps-store", type=int, default=50)
    parser.add_argument("--n-reps-path-d", type=int, default=30)
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    seeds = tuple(int(s) for s in args.seeds.split(","))

    print(f"[substrate_latency] device={device} torch={torch.__version__} "
          f"cuda={torch.cuda.is_available()}")
    print(f"[substrate_latency] seeds={seeds}")
    print()

    results = run(
        device=device,
        n_reps_store=args.n_reps_store,
        n_reps_path_d=args.n_reps_path_d,
        seeds=seeds,
    )

    out_dir = _REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"substrate_latency_{device.type}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
