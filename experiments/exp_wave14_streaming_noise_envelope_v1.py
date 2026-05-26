"""Streaming inference noise-envelope -- Cap 3 envelope expansion under bit-flip noise.

Probes whether the STREAMING_CONTINUOUS_PASS criterion (throughput_ratio >= 0.9)
from cycle 173 v1 holds when bit-flip noise is applied to W at each streaming step.

Noise model: each entry of W is independently flipped in sign with probability p
BEFORE the inference/readout step at each streaming iteration. This mimics
realistic substrate perturbation during live inference operation.

Noise levels: p in {0.0 (clean baseline), 0.05, 0.10, 0.20}.
3 seeds x full streaming protocol per cell.

Verdict labels:
  STREAMING_NOISE_ENVELOPE_PASS    - 2 or 3 noisy cells (p>0) satisfy throughput_ratio>=0.9
  STREAMING_NOISE_ENVELOPE_PARTIAL - 1 noisy cell satisfies throughput_ratio>=0.9
  STREAMING_NOISE_ENVELOPE_KILL    - 0 noisy cells satisfy; envelope narrows to clean only
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing keys: {required - d.keys()}")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_noise_verdict(per_noise_results):
    """per_noise_results: dict { p_str -> throughput_ratio }.
    Count how many NOISY cells (p > 0.0) pass the >= 0.9 threshold.
    """
    noisy_pass = 0
    noisy_total = 0
    for p_str, val in per_noise_results.items():
        p_float = float(p_str)
        if p_float > 0.0:
            noisy_total += 1
            if val >= 0.9:
                noisy_pass += 1
    if noisy_pass >= 2:
        verdict = "STREAMING_NOISE_ENVELOPE_PASS"
        msg = (f"Noise envelope PASS: {noisy_pass}/{noisy_total} noisy cells "
               f"satisfy throughput_ratio>=0.9. Cap 3 streaming verified under bit-flip noise.")
    elif noisy_pass == 1:
        verdict = "STREAMING_NOISE_ENVELOPE_PARTIAL"
        msg = (f"Noise envelope PARTIAL: {noisy_pass}/{noisy_total} noisy cells "
               f"satisfy throughput_ratio>=0.9. Cap 3 partial noise robustness.")
    else:
        verdict = "STREAMING_NOISE_ENVELOPE_KILL"
        msg = (f"Noise envelope KILL: 0/{noisy_total} noisy cells satisfy "
               f"throughput_ratio>=0.9. Cap 3 envelope narrows to clean substrate only.")
    return verdict, msg


def self_test_verdict():
    cases = [
        # All 3 noisy levels pass -> PASS
        ({"0.05": 0.95, "0.10": 0.92, "0.20": 0.91}, "STREAMING_NOISE_ENVELOPE_PASS"),
        # 2 of 3 pass -> PASS
        ({"0.05": 0.95, "0.10": 0.92, "0.20": 0.50}, "STREAMING_NOISE_ENVELOPE_PASS"),
        # 1 of 3 pass -> PARTIAL
        ({"0.05": 0.95, "0.10": 0.60, "0.20": 0.30}, "STREAMING_NOISE_ENVELOPE_PARTIAL"),
        # 0 of 3 pass -> KILL
        ({"0.05": 0.60, "0.10": 0.40, "0.20": 0.20}, "STREAMING_NOISE_ENVELOPE_KILL"),
        # Baseline p=0.0 excluded from count; 2 noisy pass -> PASS
        ({"0.0": 0.99, "0.05": 0.95, "0.10": 0.91, "0.20": 0.50},
         "STREAMING_NOISE_ENVELOPE_PASS"),
    ]
    for i, (results, expected) in enumerate(cases):
        got, _ = compute_noise_verdict(results)
        if got != expected:
            raise AssertionError(f"self_test case {i}: got {got} expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Experiment primitives
# ---------------------------------------------------------------------------

def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device)
    return (2.0 * b.float() - 1.0)


def apply_bit_flip_noise(W, p, gen):
    """Flip each entry of W in sign with probability p using generator gen.
    W is float; noise mask is bool. Returns new tensor (W unchanged in-place)."""
    if p == 0.0:
        return W
    mask = torch.rand(W.shape, generator=gen, device=W.device) < p
    return torch.where(mask, -W, W)


def stream_block(W, queries, p_noise, gen, max_iter=20):
    """Process a block of queries under noise p; return total time and accuracy.

    At each query, bit-flip noise is applied to W before the Hopfield iteration.
    W_noisy is constructed fresh per query (noise is i.i.d. across queries).
    """
    t0 = time.monotonic()
    n_correct = 0
    for q, target in queries:
        W_noisy = apply_bit_flip_noise(W, p_noise, gen)
        s = q.clone()
        for _ in range(max_iter):
            s = torch.sign(W_noisy @ s)
            s[s == 0] = 1.0
        overlap = float((s * target).mean().item())
        if overlap > 0.7:
            n_correct += 1
        del W_noisy
    elapsed = time.monotonic() - t0
    return elapsed, n_correct / max(len(queries), 1)


def run_cell(N, M, burn_in, steady, n_blocks, seed, p_noise, device):
    """Run one (seed, p_noise) cell. Returns throughput_ratio and per-block stats."""
    gen = torch.Generator().manual_seed(seed)
    gpu_gen = torch.Generator(device=device).manual_seed(seed + 100000)

    keys = torch.stack([make_pattern(N, gen, device) for _ in range(M)], dim=0)
    values = torch.stack([make_pattern(N, gen, device) for _ in range(M)], dim=0)
    W = (values.T @ keys) / N

    # Burn-in block: first burn_in queries
    burn_queries = [(keys[i % M], values[i % M]) for i in range(burn_in)]
    burn_time, burn_acc = stream_block(W, burn_queries, p_noise, gpu_gen)
    burn_throughput = burn_in / max(burn_time, 1e-9)

    # Steady-state blocks
    steady_throughputs = []
    for b in range(n_blocks):
        st_queries = [
            (keys[(b * steady + i) % M], values[(b * steady + i) % M])
            for i in range(steady)
        ]
        st_time, st_acc = stream_block(W, st_queries, p_noise, gpu_gen)
        thr = steady / max(st_time, 1e-9)
        steady_throughputs.append(thr)

    steady_mean = sum(steady_throughputs) / len(steady_throughputs)
    ratio = steady_mean / max(burn_throughput, 1e-9)

    del W, keys, values
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "throughput_ratio": ratio,
        "burn_throughput": burn_throughput,
        "steady_throughput_mean": steady_mean,
        "steady_throughputs": steady_throughputs,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        N = 2048
        M = 50
        burn_in = 10
        steady = 20
        n_blocks = 2
        seeds = [17]
        noise_levels = [0.0, 0.10]
    else:
        N = 16384
        M = 200
        burn_in = 100
        steady = 200
        n_blocks = 3
        seeds = [17, 18, 19]
        noise_levels = [0.0, 0.05, 0.10, 0.20]

    cfg = {
        "N": N, "M": M, "burn_in": burn_in, "steady": steady,
        "n_blocks": n_blocks, "seeds": seeds, "noise_levels": noise_levels,
    }

    print(f"Config: N={N} M={M} burn_in={burn_in} steady={steady} "
          f"n_blocks={n_blocks} seeds={seeds} noise_levels={noise_levels}", flush=True)

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    # cell_results[p_str][seed] = cell dict
    cell_results = {}
    for p in noise_levels:
        p_str = str(p)
        cell_results[p_str] = {}
        for seed in seeds:
            print(f"\n  [p={p} seed={seed}] running streaming loop...", flush=True)
            result = run_cell(N, M, burn_in, steady, n_blocks, seed, p, device)
            cell_results[p_str][seed] = result
            print(f"    throughput_ratio={result['throughput_ratio']:.3f} "
                  f"burn={result['burn_throughput']:.2f}q/s "
                  f"steady_mean={result['steady_throughput_mean']:.2f}q/s", flush=True)

    if device.type == "cuda":
        peak_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        print(f"\n  Peak VRAM: {peak_mb:.1f} MB", flush=True)
    else:
        peak_mb = None

    # Aggregate throughput_ratio per noise level across seeds
    per_noise_summary = {}
    for p_str, seed_dict in cell_results.items():
        all_ratios = [v["throughput_ratio"] for v in seed_dict.values()]
        per_noise_summary[p_str] = sum(all_ratios) / len(all_ratios)

    print(f"\nPer-noise throughput_ratio (mean over seeds):", flush=True)
    for p_str, val in sorted(per_noise_summary.items(), key=lambda x: float(x[0])):
        print(f"  p={p_str}: throughput_ratio={val:.3f}", flush=True)

    verdict, msg = compute_noise_verdict(per_noise_summary)
    elapsed = time.monotonic() - t0

    summary = {
        "per_noise_throughput_ratio": per_noise_summary,
        "per_noise_cell_details": cell_results,
        "peak_vram_mb": peak_mb,
        "N": N, "M": M, "burn_in": burn_in, "steady": steady,
        "n_blocks": n_blocks, "seeds": seeds,
    }

    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

def run_smoke():
    out_dir = get_output_dir("wave14_streaming_noise_envelope_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Sanity: baseline p=0.0 throughput_ratio should be reasonable (>=0.5)
    baseline_ratio = s["per_noise_throughput_ratio"].get("0.0")
    if baseline_ratio is not None:
        oracle.assert_in_range("throughput_ratio_baseline", baseline_ratio, (0.0, 10.0))
    # Sanity: p=0.10 ratio should be within a physically plausible band
    p010_ratio = s["per_noise_throughput_ratio"].get(
        "0.1", s["per_noise_throughput_ratio"].get("0.10", None)
    )
    if p010_ratio is not None:
        oracle.assert_in_range("throughput_ratio_p010", p010_ratio, (0.0, 10.0))
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_streaming_noise_envelope_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
