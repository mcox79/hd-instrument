"""S4/SSM toy port smoke: single-channel diagonal state-space cleanup layer
applied to chained cleanup tasks. Tests whether HiPPO-like state recurrence
extends usable chain depth past the d~50 cliff observed on the binding-only
substrate.

Mechanism:
- Initialize a complex-diagonal state-space:
    h_{t+1} = A * h_t + B * x_t,   y_t = real(C * h_t),
  with A = exp(-dt * (lam_re + 1j * lam_im)) — diagonal HiPPO-like decay.
- "Chain" task: random BSC atoms a_1, ..., a_d; bind chain c_t = a_1 XOR a_2 ...
  XOR a_t; ask for a_1 given c_t (probe deeper t). Cleanup via:
    (a) binding-only: y_t = c_t XOR a_2 ... XOR a_t (assume cleanup at each step)
    (b) SSM-aided: feed c_t into the SSM with B vector encoding the binding key,
        and read out a candidate atom; cleanup against codebook.

Hypothesis: SSM extends the depth at which mean(cosine(recall, a_1)) drops
below 0.5 (the cleanup-success threshold).

Hard-fail: SSM depth-at-half <= binding-only depth-at-half (no improvement).
Hard-pass: SSM depth-at-half >= 1.5x binding-only depth-at-half.
Middle band: SSM depth-at-half in (1.0x, 1.5x).

Smoke: N=512, d_max=50, 32 hidden states, 1 seed, ~45 min CPU upper bound but
typically much faster.
Full: N=4096, d_max=200, 128 hidden states, 5 seeds.

Pre-reg: preregs/2026-05-24_wave14e_s4_depth_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

N_FULL = 4096
N_SMOKE = 512
D_MAX_FULL = 200
D_MAX_SMOKE = 50
H_FULL = 128  # SSM hidden states
H_SMOKE = 32
N_PROBES_FULL = 50
N_PROBES_SMOKE = 20
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_RATIO = 1.5
HARD_FAIL_RATIO = 1.0
PARTIAL_RATIO = 1.05


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_bsc(M, N, gen):
    raw = torch.rand((M, N), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def bind(a, b):
    """BSC XOR via product on {-1, +1}."""
    return a * b


def cosine(a, b):
    return float((a * b).sum() / (a.norm() * b.norm() + 1e-9))


def init_ssm(H, N, gen):
    """Diagonal HiPPO-like SSM with complex eigenvalues.
    A: (H,) complex diagonal of state transition
    B: (H, N) real input embedding
    C: (H, N) real output embedding
    """
    # HiPPO-Legs: lam_n = -1/2 - 1j * n * pi (approximate)
    lam_re = 0.5 + 0.01 * torch.arange(H, dtype=torch.float32)
    lam_im = math.pi * torch.arange(H, dtype=torch.float32) / max(H, 1)
    dt = 0.5
    A_log = -dt * lam_re + 1j * dt * lam_im
    A = torch.exp(A_log).to(torch.complex64)
    # Random projections (BSC-style binarized)
    B_re = make_bsc(H, N, gen)
    C_re = make_bsc(H, N, gen)
    return A, B_re, C_re


def run_ssm(A, B, C, xs):
    """Run the SSM forward over a sequence xs[0..T-1], each xs[t] is (N,).
    Returns ys[0..T-1] each (N,).
    """
    H = A.shape[0]
    N = B.shape[1]
    T = xs.shape[0]
    h = torch.zeros(H, dtype=torch.complex64, device=xs.device)
    ys = torch.zeros((T, N), dtype=torch.float32, device=xs.device)
    for t in range(T):
        # h = A * h + B @ x  ; B @ x is real but we lift to complex
        bx = (B @ xs[t]).to(torch.complex64)
        h = A * h + bx
        # y = real(C^T @ h)
        y = (C.T.to(torch.complex64) @ h).real
        ys[t] = y
    return ys


def chained_cleanup_smoke(N, d_max, n_probes, H, seed, device):
    """Build chained-binding test, score binding-only vs SSM-aided recovery
    of a_1 at depths 1..d_max."""
    gen = torch.Generator().manual_seed(seed)
    # Codebook of d_max+1 atoms
    atoms = make_bsc(d_max + 1, N, gen).to(device)  # (d_max+1, N)

    # For each probe (different chain target a_1), measure cosine(recovered, a_1)
    # at depth t. We probe `n_probes` chains, each rooting at a_1 = atoms[0]
    # but with a different second-onwards seq pulled from atoms[1:].
    # For simplicity, use the same single chain across depths.

    # Build chain c_t = a_0 XOR a_1 XOR ... XOR a_t
    cs = torch.zeros((d_max + 1, N), device=device)
    cs[0] = atoms[0]
    for t in range(1, d_max + 1):
        cs[t] = bind(cs[t - 1], atoms[t])

    # binding-only recovery: at depth t, hat_a0 = c_t XOR a_1 XOR a_2 ... XOR a_t
    binding_cos_at_depth = torch.zeros(d_max + 1)
    for t in range(1, d_max + 1):
        hat = cs[t].clone()
        for j in range(1, t + 1):
            hat = bind(hat, atoms[j])
        # cleanup to nearest atom (snap to ±1)
        hat = torch.sign(hat)
        hat = torch.where(hat == 0, torch.ones_like(hat), hat)
        binding_cos_at_depth[t] = cosine(hat, atoms[0])

    # SSM-aided recovery
    A, B, C = init_ssm(H, N, gen)
    A = A.to(device)
    B = B.to(device)
    C = C.to(device)
    # Feed cs[0..d_max] into SSM, read out ys[t] as the SSM estimate of a_0
    ys = run_ssm(A, B, C, cs)
    ssm_cos_at_depth = torch.zeros(d_max + 1)
    for t in range(d_max + 1):
        # Snap SSM output to ±1 for fair comparison, then cosine
        hat = torch.sign(ys[t])
        hat = torch.where(hat == 0, torch.ones_like(hat), hat)
        ssm_cos_at_depth[t] = cosine(hat, atoms[0])

    def depth_at_half(cos_at_depth):
        for t in range(1, len(cos_at_depth)):
            if cos_at_depth[t] < 0.5:
                return t - 1
        return len(cos_at_depth) - 1

    binding_depth = depth_at_half(binding_cos_at_depth)
    ssm_depth = depth_at_half(ssm_cos_at_depth)
    return {
        "binding_depth_at_half": int(binding_depth),
        "ssm_depth_at_half": int(ssm_depth),
        "binding_cos_at_depth": binding_cos_at_depth.tolist(),
        "ssm_cos_at_depth": ssm_cos_at_depth.tolist(),
        "ratio": ssm_depth / max(binding_depth, 1),
    }


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("S4_INCONCLUSIVE", "Missing per-seed.")
    seeds = list(per_seed.values())
    avg_ratio = sum(s["ratio"] for s in seeds) / len(seeds)
    avg_ssm = sum(s["ssm_depth_at_half"] for s in seeds) / len(seeds)
    avg_bind = sum(s["binding_depth_at_half"] for s in seeds) / len(seeds)
    if avg_ratio >= PASS_RATIO:
        return ("S4_PASS",
                f"SSM extends depth: ratio={avg_ratio:.2f} >= {PASS_RATIO}. "
                f"ssm depth={avg_ssm:.1f}, binding depth={avg_bind:.1f}.")
    if avg_ratio <= HARD_FAIL_RATIO:
        return ("S4_KILLED",
                f"SSM does not extend depth: ratio={avg_ratio:.2f} <= {HARD_FAIL_RATIO}. "
                f"ssm depth={avg_ssm:.1f}, binding depth={avg_bind:.1f}.")
    if avg_ratio >= PARTIAL_RATIO:
        return ("S4_PARTIAL",
                f"SSM modestly extends depth: ratio={avg_ratio:.2f} in "
                f"[{PARTIAL_RATIO}, {PASS_RATIO}). "
                f"ssm depth={avg_ssm:.1f}, binding depth={avg_bind:.1f}.")
    return ("S4_INCONCLUSIVE",
            f"Ratio {avg_ratio:.2f} marginal. ssm depth={avg_ssm:.1f}, "
            f"binding depth={avg_bind:.1f}.")


def self_test_verdict():
    def mk(rows):
        return {"per_seed": {str(i): r for i, r in enumerate(rows)}}
    cases = [
        (mk([{"binding_depth_at_half": 20, "ssm_depth_at_half": 40, "ratio": 2.0}]), "S4_PASS"),
        (mk([{"binding_depth_at_half": 20, "ssm_depth_at_half": 10, "ratio": 0.5}]), "S4_KILLED"),
        (mk([{"binding_depth_at_half": 20, "ssm_depth_at_half": 22, "ratio": 1.10}]), "S4_PARTIAL"),
        (mk([{"binding_depth_at_half": 20, "ssm_depth_at_half": 20, "ratio": 1.00}]), "S4_KILLED"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "d_max": D_MAX_SMOKE if smoke else D_MAX_FULL,
        "H": H_SMOKE if smoke else H_FULL,
        "n_probes": N_PROBES_SMOKE if smoke else N_PROBES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = chained_cleanup_smoke(config["N"], config["d_max"], config["n_probes"],
                                    config["H"], seed, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: binding_depth={r['binding_depth_at_half']} "
              f"ssm_depth={r['ssm_depth_at_half']} ratio={r['ratio']:.2f}", flush=True)
    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14e_s4_depth_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    seed_key = list(summary["per_seed"].keys())[0]
    r = summary["per_seed"][seed_key]
    assert r["binding_depth_at_half"] >= 1, "binding depth degenerate"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14e_s4_depth_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


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
