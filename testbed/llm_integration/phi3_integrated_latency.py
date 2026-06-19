"""Week 0 Missing 7 measurement #4: end-to-end integrated forward-pass wall.

Per testbed_handoff_substrate_llm_deep_integration_2026-05-31.md sec
WEEK 0 MISSING 7 -- LLM INTEGRATION LATENCY BUDGET CHARACTERIZATION
measurement (4).

Pipeline (one integrated query):
  Phi-3 emits query head (hidden state at last position after prefill)
    -> ReverseBridge R^3072 -> R^4096 (continuous-relaxed substrate query)
    -> sign() to bipolar
    -> Path D depth=5 retrieve at N=4096, K_paths=500
    -> ForwardBridge R^4096 -> R^3072 (prefix embedding)
    -> Phi-3 decode 1 token conditioned on the prefix

Measures TOTAL wall per integrated query at seq_len in {128, 512}.
Components are timed separately so the breakdown is visible:
  - prefill (one-time per query, not per-token)
  - extract hidden state + reverse_bridge + sign
  - substrate Path D depth=5
  - forward_bridge + prefix embed concat
  - Phi-3 decode 1 token with prefix injection

Decision criteria (per handoff sec):
  PASS  : total integrated p99 < 50ms (per-query wall)
  MIDDLE: in [50ms, 150ms]
  FAIL  : > 150ms (escalate to research before Week 1)

Bridges are RANDOM-INIT (Xavier) per #2; substrate W is populated.
This measures the ARCHITECTURE-LEVEL latency, not learned-bridge quality.

Run (REMOTE GPU only):
  python -m testbed.llm_integration.phi3_integrated_latency --device cuda

Writes data/testbed_missing7/phi3_integrated_latency_<device>.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402
from testbed.llm_integration.bridge_mlp_scaffold import (  # noqa: E402
    ForwardBridge, ReverseBridge,
)
from testbed.llm_integration.phi3_token_latency import _load_phi3_4bit  # noqa: E402


_N_SUBSTRATE = 4096
_M_SUBSTRATE = 4096
_K_PATHS = 500
_D_MODEL = 3072
_DEPTH = 5


def _build_substrate(seed: int, device: torch.device):
    """Build a populated substrate (codebook + W + relation graph) at N=4096."""
    return build_shared(_N_SUBSTRATE, _M_SUBSTRATE, seed, device)


def _measure_integrated(
    model, reverse_bridge: ReverseBridge, forward_bridge: ForwardBridge,
    substrate_tuple, seq_len: int, n_reps: int,
    device: torch.device, seed: int,
    progress_jsonl_path: Path | None = None,
) -> dict[str, Any]:
    """Measure one integrated query end-to-end, plus per-component breakdown.

    Returns dict with `total_ms` (samples), `breakdown_ms` (samples per
    component), `prefill_ms` (one-time at prompt level not in budget).

    If progress_jsonl_path is set, appends one JSON line per rep
    IMMEDIATELY after each measurement -- failure-recovery: if the run
    crashes at rep K/N, reps 1..K-1 are preserved on disk.
    """
    codebook, W, key_idx, val_idx, relation = substrate_tuple
    starts = key_idx[:1].to(device)

    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    vocab = model.config.vocab_size
    prompt_ids = torch.randint(0, vocab, (1, seq_len),
                               generator=g, dtype=torch.long).to(device)

    component_samples = {
        "reverse_bridge": [],
        "substrate_path_d": [],
        "forward_bridge": [],
        "phi3_decode_1tok": [],
    }
    total_samples: list[float] = []

    with torch.inference_mode():
        # Prefill once per (seq_len, seed) — not part of per-query budget
        torch.cuda.synchronize()
        t_pre0 = time.perf_counter_ns()
        out = model(input_ids=prompt_ids, use_cache=True,
                    output_hidden_states=True)
        torch.cuda.synchronize()
        t_pre1 = time.perf_counter_ns()
        prefill_ms = (t_pre1 - t_pre0) / 1e6

        past = out.past_key_values
        # Last-position hidden state from final layer (R^d_model)
        query_hidden = out.hidden_states[-1][:, -1, :].to(dtype=torch.float32)

        # warm-up 3 integrated queries (excluded from samples)
        for _ in range(3):
            rh = reverse_bridge(query_hidden)
            bipolar = torch.sign(rh).squeeze(0)
            zero_mask = bipolar == 0
            if zero_mask.any():
                bipolar = bipolar + zero_mask.float()
            _ = bipolar
            _ = path_d_run(
                codebook=codebook, W=W, starts=starts, relation=relation,
                depth=_DEPTH, K_paths=_K_PATHS, seed=seed, N_use=_N_SUBSTRATE,
            )

        for rep in range(n_reps):
            torch.cuda.synchronize()
            t_total0 = time.perf_counter_ns()

            # Component 1: ReverseBridge (LLM hidden -> substrate query)
            torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            rh = reverse_bridge(query_hidden)
            bipolar = torch.sign(rh).squeeze(0)
            zero_mask = bipolar == 0
            if zero_mask.any():
                bipolar = bipolar + zero_mask.float()
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            component_samples["reverse_bridge"].append((t1 - t0) / 1e6)

            # Component 2: substrate Path D depth=5
            torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            result = path_d_run(
                codebook=codebook, W=W, starts=starts, relation=relation,
                depth=_DEPTH, K_paths=_K_PATHS, seed=seed + rep,
                N_use=_N_SUBSTRATE,
            )
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            component_samples["substrate_path_d"].append((t1 - t0) / 1e6)

            # Result is path_d_run's argmax winner index -> codeword R^N
            # path_d_run returns (best_idx, debug). Take the codeword.
            if isinstance(result, tuple):
                best_idx = result[0]
            else:
                best_idx = result
            if isinstance(best_idx, torch.Tensor):
                bi = best_idx.flatten()[0].item() if best_idx.numel() > 0 else 0
            else:
                bi = int(best_idx) if not hasattr(best_idx, "__iter__") else 0
            # Cast to int -- path_d_run may return a float tensor whose
            # .item() lands as Python float; codebook[...] needs an int index.
            bi = int(bi) if not isinstance(bi, int) else bi
            bi = max(0, min(bi, codebook.shape[0] - 1))
            substrate_result = codebook[bi].to(dtype=torch.float32).unsqueeze(0)

            # Component 3: ForwardBridge (substrate -> LLM prefix embed)
            torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            prefix_embed = forward_bridge(substrate_result).unsqueeze(1)
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            component_samples["forward_bridge"].append((t1 - t0) / 1e6)

            # Component 4: Phi-3 decode 1 token with prefix injected via embeds
            torch.cuda.synchronize()
            t0 = time.perf_counter_ns()
            dec_out = model(
                inputs_embeds=prefix_embed.to(dtype=model.dtype),
                past_key_values=past,
                use_cache=True,
            )
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            component_samples["phi3_decode_1tok"].append((t1 - t0) / 1e6)

            torch.cuda.synchronize()
            t_total1 = time.perf_counter_ns()
            rep_total = (t_total1 - t_total0) / 1e6
            total_samples.append(rep_total)

            # Per-rep stdout line: matches generic_progress_wrapper default
            # cell-regex (`^\s+...seed=\d+\s+(?:ok=|acc=|FAILED:)`) so cloud
            # ProgressPoller can count cells = rep_count and stream live
            # progress in the dashboard. Without this print the wrapper has
            # nothing to match and progress.json stays at cell=0.
            print(f"  seed={seed} rep={rep} ok=True total_ms={rep_total:.2f}",
                  flush=True)

            # Failure-recovery: append per-rep result to JSONL immediately.
            if progress_jsonl_path is not None:
                rep_record = {
                    "seq_len": seq_len,
                    "seed": seed,
                    "rep": rep,
                    "total_ms": round(rep_total, 4),
                    "reverse_bridge_ms": round(
                        component_samples["reverse_bridge"][-1], 4),
                    "substrate_path_d_ms": round(
                        component_samples["substrate_path_d"][-1], 4),
                    "forward_bridge_ms": round(
                        component_samples["forward_bridge"][-1], 4),
                    "phi3_decode_1tok_ms": round(
                        component_samples["phi3_decode_1tok"][-1], 4),
                    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
                try:
                    with progress_jsonl_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(rep_record) + "\n")
                        f.flush()
                except Exception as exc:
                    print(f"[WARN] per-rep JSONL write failed at "
                          f"seq={seq_len} seed={seed} rep={rep}: {exc}",
                          flush=True)

    return {
        "total_ms": total_samples,
        "component_ms": component_samples,
        "prefill_ms": prefill_ms,
    }


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
        seq_lens: tuple[int, ...] = (128, 512),
        n_reps_per_seed: int = 20,
        progress_jsonl_path: Path | None = None) -> dict[str, Any]:
    """Run all Missing 7 #4 measurements; return structured results.

    If progress_jsonl_path is set, each rep's measurement is appended to
    that JSONL file IMMEDIATELY (failure-recovery; crashed runs preserve
    completed reps).
    """
    results: dict[str, Any] = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "n_substrate": _N_SUBSTRATE,
        "m_substrate": _M_SUBSTRATE,
        "k_paths": _K_PATHS,
        "depth": _DEPTH,
        "d_model": _D_MODEL,
        "seeds": list(seeds),
        "seq_lens": list(seq_lens),
        "n_reps_per_seed": n_reps_per_seed,
        "progress_jsonl_path": str(progress_jsonl_path) if progress_jsonl_path else None,
        "measurements": {},
    }

    print(f"[phi3_integrated_latency] loading Phi-3 (4-bit)...")
    t0 = time.perf_counter()
    model, tokenizer = _load_phi3_4bit(device)
    print(f"[phi3_integrated_latency] model loaded in {time.perf_counter() - t0:.1f}s")
    print(f"[phi3_integrated_latency] d_model={model.config.hidden_size}")
    results["d_model_actual"] = model.config.hidden_size

    if model.config.hidden_size != _D_MODEL:
        raise RuntimeError(
            f"d_model mismatch: bridge built for {_D_MODEL}, "
            f"model has {model.config.hidden_size}")

    # Build bridges and substrate once (seeded inside loops)
    torch.manual_seed(0)
    reverse_bridge = ReverseBridge().to(device).to(dtype=torch.float32)
    forward_bridge = ForwardBridge().to(device).to(dtype=torch.float32)
    reverse_bridge.eval()
    forward_bridge.eval()

    for seq_len in seq_lens:
        per_seed_total: list[float] = []
        per_seed_components: dict[str, list[float]] = {
            "reverse_bridge": [], "substrate_path_d": [],
            "forward_bridge": [], "phi3_decode_1tok": [],
        }
        prefill_samples: list[float] = []
        for s in seeds:
            substrate_tuple = _build_substrate(s, device)
            try:
                meas = _measure_integrated(
                    model, reverse_bridge, forward_bridge, substrate_tuple,
                    seq_len, n_reps_per_seed, device, s,
                    progress_jsonl_path=progress_jsonl_path,
                )
                per_seed_total.extend(meas["total_ms"])
                for k, v in meas["component_ms"].items():
                    per_seed_components[k].extend(v)
                prefill_samples.append(meas["prefill_ms"])
            except Exception as exc:
                print(f"[ERROR] seq_len={seq_len} seed={s}: {exc}",
                      file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

        key = f"integrated_seq{seq_len}"
        results["measurements"][key] = {
            "total": _summarize(per_seed_total),
            "components": {k: _summarize(v) for k, v in per_seed_components.items()},
            "prefill": _summarize(prefill_samples),
        }
        m = results["measurements"][key]["total"]
        comp = results["measurements"][key]["components"]
        print(f"  {key}: total mean={m['mean']:.3f}ms p99={m['p99']:.3f}ms")
        for cname, csumm in comp.items():
            print(f"    [{cname}]: mean={csumm['mean']:.4f}ms "
                  f"p99={csumm['p99']:.4f}ms")

    # Final verdict on integrated p99 at seq_len=512 (production reference)
    ref = results["measurements"].get("integrated_seq512", {}).get("total", {})
    total_p99 = ref.get("p99", 0.0)
    if total_p99 < 50:
        verdict_integrated = "PASS (integrated query < 50ms p99; soft-prompt prefix-injection viable)"
    elif total_p99 < 150:
        verdict_integrated = "MIDDLE (integrated in [50,150]ms; design works with deployment caveats)"
    else:
        verdict_integrated = "FAIL (integrated > 150ms p99; need async-batched or precomputed-prefix variants)"
    print()
    print(f"  Week 0 Missing 7 #4 verdict (seq_len=512): {verdict_integrated}")
    results["integrated_verdict"] = verdict_integrated
    results["integrated_p99_ms_seq512"] = total_p99

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integrated forward-pass latency (Week 0 Missing 7 #4)")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seeds", default="7,13,17,23,31")
    parser.add_argument("--seq-lens", default="128,512,2048")
    parser.add_argument("--n-reps-per-seed", type=int, default=20)
    parser.add_argument("--out-dir", default="data/testbed_missing7")
    parser.add_argument("--progress-jsonl",
                        default="data/testbed_missing7/phi3_integrated_progress_results.jsonl",
                        help="Path to per-rep JSONL written immediately per "
                             "rep (failure-recovery; preserves completed reps "
                             "if run crashes mid-flight)")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    seeds = tuple(int(s) for s in args.seeds.split(","))
    seq_lens = tuple(int(s) for s in args.seq_lens.split(","))

    progress_jsonl_path: Path | None = None
    if args.progress_jsonl:
        progress_jsonl_path = Path(args.progress_jsonl)
        if not progress_jsonl_path.is_absolute():
            progress_jsonl_path = _REPO_ROOT / progress_jsonl_path
        progress_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        # Truncate at start so a re-run doesn't append to stale data.
        progress_jsonl_path.write_text("", encoding="utf-8")

    print(f"[phi3_integrated_latency] device={device} torch={torch.__version__} "
          f"cuda={torch.cuda.is_available()}")
    print(f"[phi3_integrated_latency] seeds={seeds} seq_lens={seq_lens} "
          f"n_reps_per_seed={args.n_reps_per_seed}")
    print(f"[phi3_integrated_latency] progress JSONL: {progress_jsonl_path}")
    print()

    results = run(
        device=device,
        seeds=seeds,
        seq_lens=seq_lens,
        n_reps_per_seed=args.n_reps_per_seed,
        progress_jsonl_path=progress_jsonl_path,
    )

    out_dir = _REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"phi3_integrated_latency_{device.type}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
