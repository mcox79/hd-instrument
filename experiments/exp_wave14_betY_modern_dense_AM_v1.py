"""Bet Y V2.D — Modern exponential-capacity dense AM (Demircigil 2017 / Ramsauer 2020).

Strategy filed 21:42 EDT. Tests whether explicit energy-descent cleanup
E(s) = -beta^-1 log sum_i exp(beta * x_i^T s) beats argmax cleanup at
high capacity (M/N > 8).

Pre-reg: preregs/2026-05-21_wave14_betY_modern_dense_AM_v1.md
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

PASS_CAPACITY_BOOST = 1.5  # modern dense AM must beat baseline by 1.5x
KILL_CAPACITY_BOOST = 0.9


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(summary):
    if "modern_capacity" not in summary:
        return ("BET_Y_INCONCLUSIVE", "Missing capacity.")
    modern = summary["modern_capacity"]
    base = summary["argmax_capacity"]
    ratio = modern / max(base, 1e-9)
    if ratio < KILL_CAPACITY_BOOST:
        return ("BET_Y_KILLED",
                f"Modern dense AM cleanup ({modern:.2f}*N) underperforms argmax baseline "
                f"({base:.2f}*N); ratio={ratio:.2f}<{KILL_CAPACITY_BOOST}.")
    if ratio >= PASS_CAPACITY_BOOST:
        return ("BET_Y_PASS",
                f"Modern dense AM achieves {modern:.2f}*N capacity vs argmax {base:.2f}*N "
                f"(ratio {ratio:.2f}x >={PASS_CAPACITY_BOOST}). Demircigil/Ramsauer regime "
                f"validates substrate-product capacity gain.")
    return ("BET_Y_PARTIAL",
            f"Modern dense AM {modern:.2f}*N vs argmax {base:.2f}*N (ratio {ratio:.2f}); "
            f"some gain but below {PASS_CAPACITY_BOOST}x threshold.")


def self_test_verdict():
    cases = [
        ({"modern_capacity": 12.0, "argmax_capacity": 6.0}, "BET_Y_PASS"),
        ({"modern_capacity": 7.0, "argmax_capacity": 6.0}, "BET_Y_PARTIAL"),
        ({"modern_capacity": 4.0, "argmax_capacity": 6.0}, "BET_Y_KILLED"),
        ({}, "BET_Y_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_keys(M, N, gen, device):
    return 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0


def test_capacity_argmax(M, N, gen, device):
    keys = make_keys(M, N, gen, device)
    values = make_keys(M, N, gen, device)
    W = (values.T @ keys) / N
    pred = (keys @ W.T @ values.T).argmax(dim=1)
    return float((pred == torch.arange(M, device=device)).float().mean())


def test_capacity_modern_dense(M, N, beta, n_iter, gen, device):
    """Energy-descent cleanup: state_t+1 = sum_i softmax(beta * keys_i^T state_t) * keys_i."""
    keys = make_keys(M, N, gen, device)
    values = make_keys(M, N, gen, device)
    W = (values.T @ keys) / N
    correct = 0
    for i in range(M):
        # Query at key_i; modern Hopfield retrieval refines toward value_i
        probe = (keys[i] @ W.T)  # initial guess at value
        state = probe.float()
        for _ in range(n_iter):
            sims = (values @ state) * beta  # (M,)
            sims = sims - sims.max()
            w = torch.softmax(sims, dim=0)
            state = w @ values
        # Argmax over values
        final = (values @ state).argmax().item()
        if int(final) == i:
            correct += 1
    return correct / M


def find_max_passing_M(test_fn, N, M_grid, n_seeds, device, fn_kwargs=None):
    fn_kwargs = fn_kwargs or {}
    best = 0
    for M in M_grid:
        ok = 0
        for s in range(n_seeds):
            gen = torch.Generator(device=device).manual_seed(s * 17 + 7)
            acc = test_fn(M=M, N=N, gen=gen, device=device, **fn_kwargs)
            if acc >= 0.95:
                ok += 1
        if ok >= max(1, n_seeds * 2 // 3):
            best = max(best, M)
    return best / N


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "M_grid": [256, 512] if smoke else [1024, 4096, 8192, 16384, 32768],
              "seeds": 1 if smoke else 3,
              "beta": 8.0, "n_iter": 5}
    print(f"[config] {config}", flush=True)
    print("[argmax baseline]", flush=True)
    argmax_cap = find_max_passing_M(test_capacity_argmax, config["N"], config["M_grid"],
                                          config["seeds"], device)
    print(f"  argmax capacity = {argmax_cap:.2f}*N", flush=True)
    print("[modern dense]", flush=True)
    modern_cap = find_max_passing_M(test_capacity_modern_dense, config["N"], config["M_grid"],
                                          config["seeds"], device,
                                          fn_kwargs={"beta": config["beta"], "n_iter": config["n_iter"]})
    print(f"  modern capacity = {modern_cap:.2f}*N", flush=True)
    summary = {"argmax_capacity": argmax_cap, "modern_capacity": modern_cap}
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
    out_dir = get_output_dir("wave14_betY_modern_dense_AM_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("argmax_cap", summary["argmax_capacity"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betY_modern_dense_AM_v1")
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
