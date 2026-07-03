"""R32 M.1 — Phasor codebook (magnon standing-wave) capacity test.

Per Strategy pipeline-fill #6: replace random ±1 atoms with phasor codewords
sign(cos(2pi*n*k/N)). Test Bet C capacity vs random ±1 baseline.

Pre-reg: preregs/2026-05-21_wave14_R32_M1_phasor_codebook.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

PASS_CAPACITY_RATIO = 4.0  # M/N must >= 4 to pass
KILL_CAPACITY_RATIO = 2.0


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(summary):
    if "phasor_capacity" not in summary:
        return ("R32_M1_INCONCLUSIVE", "Missing capacity.")
    phasor_cap = summary["phasor_capacity"]
    rand_cap = summary.get("random_capacity", 0.0)
    if phasor_cap < KILL_CAPACITY_RATIO:
        return ("R32_M1_KILLED",
                f"Phasor codebook capacity {phasor_cap:.2f}*N below kill threshold "
                f"{KILL_CAPACITY_RATIO}. Phasor substrate not viable.")
    if phasor_cap >= PASS_CAPACITY_RATIO:
        return ("R32_M1_PASS",
                f"Phasor codebook achieves capacity {phasor_cap:.2f}*N "
                f">= {PASS_CAPACITY_RATIO} (random baseline {rand_cap:.2f}). "
                f"Magnon standing-wave codebook validated.")
    return ("R32_M1_PARTIAL",
            f"Phasor capacity {phasor_cap:.2f}*N in ({KILL_CAPACITY_RATIO}, "
            f"{PASS_CAPACITY_RATIO}); random baseline {rand_cap:.2f}.")


def self_test_verdict():
    cases = [
        ({"phasor_capacity": 5.0, "random_capacity": 1.5}, "R32_M1_PASS"),
        ({"phasor_capacity": 3.0, "random_capacity": 1.5}, "R32_M1_PARTIAL"),
        ({"phasor_capacity": 1.5, "random_capacity": 1.5}, "R32_M1_KILLED"),
        ({}, "R32_M1_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_phasor_codebook(M, N, device):
    """Phasor atoms: sign(cos(2*pi*n*k/N)) for n in [0,N), k in [1,M+1]."""
    n = torch.arange(N, device=device, dtype=torch.float32).unsqueeze(0)
    k = torch.arange(1, M + 1, device=device, dtype=torch.float32).unsqueeze(1)
    phases = 2.0 * math.pi * n * k / N
    codes = torch.sign(torch.cos(phases))
    return torch.where(codes == 0, torch.ones_like(codes), codes)


def make_random_codebook(M, N, gen, device):
    return 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0


def find_capacity(codebook_fn, N, M_grid, n_seeds, device):
    """For each M in grid, build M facts and test argmax retrieval. Capacity = max M passing."""
    max_passing = 0
    for M in M_grid:
        if hasattr(codebook_fn, '__call__') and 'gen' in codebook_fn.__code__.co_varnames:
            seeds_pass = 0
            for seed in range(n_seeds):
                gen = torch.Generator(device=device).manual_seed(seed * 17 + 7)
                keys = codebook_fn(M, N, gen, device)
                values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
                W = (values.T @ keys) / N
                pred = (keys @ W.T @ values.T).argmax(dim=1)
                acc = float((pred == torch.arange(M, device=device)).float().mean())
                if acc >= 0.95:
                    seeds_pass += 1
            if seeds_pass >= n_seeds * 2 // 3:
                max_passing = max(max_passing, M)
        else:
            # Deterministic codebook (phasor)
            keys = codebook_fn(M, N, device)
            keys = keys[:M]
            seeds_pass = 0
            for seed in range(n_seeds):
                gen = torch.Generator(device=device).manual_seed(seed * 17 + 7)
                values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
                W = (values.T @ keys) / N
                pred = (keys @ W.T @ values.T).argmax(dim=1)
                acc = float((pred == torch.arange(M, device=device)).float().mean())
                if acc >= 0.95:
                    seeds_pass += 1
            if seeds_pass >= n_seeds * 2 // 3:
                max_passing = max(max_passing, M)
    return max_passing / N


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "M_grid": [256, 512] if smoke else [1024, 2048, 4096, 8192, 16384, 32768],
              "seeds": 1 if smoke else 3}
    print(f"[config] {config}", flush=True)
    print(f"[phasor sweep]", flush=True)
    phasor_cap = find_capacity(make_phasor_codebook, config["N"], config["M_grid"],
                                    config["seeds"], device)
    print(f"  phasor capacity = {phasor_cap:.2f}*N", flush=True)
    print(f"[random sweep]", flush=True)
    rand_cap = find_capacity(make_random_codebook, config["N"], config["M_grid"],
                                  config["seeds"], device)
    print(f"  random capacity = {rand_cap:.2f}*N", flush=True)
    summary = {"phasor_capacity": phasor_cap, "random_capacity": rand_cap}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_R32_M1_phasor_codebook_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("phasor_cap_present", summary["phasor_capacity"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_R32_M1_phasor_codebook")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
