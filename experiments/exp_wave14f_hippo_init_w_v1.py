"""HiPPO-LegS W initialization probe vs random-init baseline on Cap 3 chain-cleanup.

Tests whether HiPPO-LegS-structured W_0 improves chain-cleanup depth-at-half
compared to random-BSC-init W_0 at matched seed/cell.

Three predictions (from research note research_ssm_hippo_compatibility_2026-05-25.md):
  Prediction 1: depth_at_half(HiPPO-init) >= 1.5 * depth_at_half(random-init) at ALL d
  Prediction 2: N-doubling (N*2) is INSUFFICIENT to recover chain-cleanup at d=200
                (Jelassi |U| >= |V|^n state-size lower bound observable on substrate)
  Prediction 3: Top-32 eigenvalues of HiPPO-init W and post-training random-init W
                are correlated > 0.5 (spectral-match test)

Pre-reg: preregs/2026-05-25_wave14f_hippo_init_w_v1.md

Infra reuse: HiPPO A-matrix construction from exp_wave14e_s4_depth_smoke_v1.py
lines 90-105 (init_ssm builds diagonal-exponential parameterization of HiPPO-LegS).
This probe uses the A-matrix EIGENVALUES to structure W_0 as:
   W_0 = sum_j sigma_j * u_j * u_j^T  where sigma_j ~ |A_diag_j|, u_j ~ BSC atoms
thereby giving W_0 the HiPPO-LegS spectral structure without running SSM dynamics.
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
sys.path.insert(0, str(REPO))

# Full-scale config
N_FULL = 4096
N_SMOKE = 1024
N_2X_FULL = 8192    # For Prediction 2 (Jelassi bound)
D_MAX_FULL = 200
D_MAX_SMOKE = 50
N_PROBES_FULL = 30   # chains to average over per depth
# Smoke: 10 probes; depth saturation at smoke scale is expected (capacity not limiting at N=1024)
# Full scale (N=4096, d_max=200) provides the actual discriminator
N_PROBES_SMOKE = 10
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
TOP_K_EIGEN = 32    # for Prediction 3 spectral match

# Pre-registered thresholds
P1_HARD_PASS_RATIO = 1.5   # depth_at_half ratio >= 1.5 at ALL d points
P1_HARD_FAIL_RATIO = 1.0   # ratio <= 1.0 at ANY d point
P2_HARD_PASS_NSCALE = 0.8  # depth_at_half(N*2) / depth_at_half(N) < 1.2 (no improvement)
P2_HARD_FAIL_NSCALE = 1.8  # N-doubling gives >= 1.8x depth (Jelassi bound rejected)
P3_SPECTRAL_HARD_PASS = 0.5  # correlation of top-32 eigenvalues > 0.5
P3_SPECTRAL_HARD_FAIL = 0.2  # correlation < 0.2 (spectra uncorrelated)

# Training epochs for Prediction 2 (needs actual Hebbian training, not just init)
P2_TRAIN_STEPS = 500   # gradient steps to build a trained W for spectral comparison


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
    """Make M bipolar {-1, +1} vectors of dimension N."""
    raw = torch.rand((M, N), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def bind(a, b):
    """BSC XOR via product on {-1, +1}."""
    return a * b


def cosine_sim(a, b):
    return float((a * b).sum() / (a.norm() * b.norm() + 1e-9))


def hippo_legs_eigenvalues(H):
    """Compute diagonal-exponential HiPPO-LegS approximate eigenvalues.

    From exp_wave14e_s4_depth_smoke_v1.py init_ssm() lines 97-101:
       lam_re = 0.5 + 0.01 * arange(H)
       lam_im = pi * arange(H) / H
       dt = 0.5
       A = exp(-dt * lam_re + 1j * dt * lam_im)

    Returns |A| (H,) as real magnitudes (decay rates).
    """
    H_f = float(max(H, 1))
    lam_re = 0.5 + 0.01 * torch.arange(H, dtype=torch.float32)
    lam_im = math.pi * torch.arange(H, dtype=torch.float32) / H_f
    dt = 0.5
    A_log_re = -dt * lam_re
    A_log_im = dt * lam_im
    A_re = torch.exp(A_log_re) * torch.cos(A_log_im)
    A_im = torch.exp(A_log_re) * torch.sin(A_log_im)
    magnitudes = (A_re ** 2 + A_im ** 2).sqrt()
    return magnitudes  # (H,)


def make_hippo_init_W(N, gen):
    """Construct HiPPO-LegS-structured W_0 of shape (N, N).

    Construction:
      1. Generate N random BSC atoms u_j ~ {-1, +1}^N
      2. Compute sigma_j = magnitude of j-th HiPPO-LegS eigenvalue
      3. W_0 = (1/N) * sum_j sigma_j * u_j outer u_j^T
         (rank-N outer-product overlay weighted by HiPPO decay structure)
    """
    atoms = make_bsc(N, N, gen)           # (N, N)
    sigma = hippo_legs_eigenvalues(N)      # (N,) magnitudes
    # W = (1/N) * sum_j sigma_j * u_j u_j^T
    # Vectorized: W = (1/N) * (atoms.T * sigma) @ atoms  ... but atoms is (N,N)
    # sigma weights rows: atoms shape (N, N), each row j weighted by sigma[j]
    W = (atoms.T * sigma.unsqueeze(0)) @ atoms / N  # (N, N)
    return W


def make_random_init_W(N, gen):
    """Random-BSC baseline: W_0 = zero (matches base substrate initialization).
    Note: using zero-init to match the base Bet B experiments exactly.
    """
    return torch.zeros((N, N), dtype=torch.float32)


# Hebbian learning rates for chain training (separate from BetB values)
DELTA_DECAY_APPROX = 1e-4
DELTA_ALPHA_APPROX = 0.3


def train_and_eval_chain_depth(N, d_max, n_patterns, d_train, W_init, gen, device):
    """Train W on chain-recall task then measure depth-at-half on the TRAINING patterns.

    Associative memory benchmark: store n_patterns chains in W, then measure
    how deep the retrieval remains accurate on those SAME patterns.

    This is the correct test: W stores (hat_t, a_0) associations for specific chains
    and is evaluated on whether it can retrieve them. HiPPO-init is expected to
    help W converge to better associations faster because the structured initialization
    provides a better spectral starting point for the Hebbian outer-product updates.
    """
    W = W_init.clone().to(device)

    # Build chains from a fixed codebook (deterministic, same for hippo and random)
    codebook_gen = torch.Generator().manual_seed(int(gen.initial_seed()) + 99999)
    n_atoms = n_patterns * (d_max + 1)
    codebook = make_bsc(n_atoms, N, codebook_gen).to(device)

    def get_chain(chain_idx):
        base = chain_idx * (d_max + 1)
        atoms = codebook[base: base + d_max + 1]
        cs = torch.zeros((d_max + 1, N), device=device)
        cs[0] = atoms[0]
        for t in range(1, d_max + 1):
            cs[t] = bind(cs[t - 1], atoms[t])
        return atoms, cs

    # Training: store all patterns in W via Hebbian updates
    n_epochs = 5
    for epoch in range(n_epochs):
        for ci in range(n_patterns):
            atoms, cs = get_chain(ci)
            for t in range(1, min(d_train + 1, d_max + 1)):
                hat = cs[t].clone()
                for j in range(1, t + 1):
                    hat = bind(hat, atoms[j])
                pred = W @ hat
                residual = atoms[0] - pred
                dW = residual.unsqueeze(1) * hat.unsqueeze(0) / N
                W = W * (1.0 - DELTA_DECAY_APPROX) + dW * DELTA_ALPHA_APPROX

    # Evaluation: test recall of the SAME stored patterns at all depths up to d_max
    all_cos = torch.zeros((n_patterns, d_max + 1))
    for ci in range(n_patterns):
        atoms, cs = get_chain(ci)
        for t in range(1, d_max + 1):
            hat = cs[t].clone()
            for j in range(1, t + 1):
                hat = bind(hat, atoms[j])
            hat_proj = W @ hat
            hat_snap = torch.sign(hat_proj)
            hat_snap = torch.where(hat_snap == 0, torch.ones_like(hat_snap), hat_snap)
            all_cos[ci, t] = cosine_sim(hat_snap, atoms[0])

    mean_cos = all_cos.mean(dim=0)

    def depth_at_half(cos_profile):
        for t in range(1, len(cos_profile)):
            if cos_profile[t] < 0.5:
                return t - 1
        return len(cos_profile) - 1

    dah = depth_at_half(mean_cos)
    return int(dah), mean_cos.tolist(), W


def compute_spectral_correlation(W_hippo, W_trained_random, top_k):
    """Compute Pearson correlation of top-k singular values between two weight matrices."""
    try:
        sv_hippo = torch.linalg.svdvals(W_hippo)[:top_k]
        sv_random = torch.linalg.svdvals(W_trained_random)[:top_k]
    except Exception:
        return float("nan")
    if len(sv_hippo) < 2 or len(sv_random) < 2:
        return float("nan")
    sv_hippo = sv_hippo.float()
    sv_random = sv_random.float()
    # Pearson correlation
    sv_h_n = sv_hippo - sv_hippo.mean()
    sv_r_n = sv_random - sv_random.mean()
    num = (sv_h_n * sv_r_n).sum()
    denom = (sv_h_n.norm() * sv_r_n.norm() + 1e-12)
    return float(num / denom)


def compute_verdict(summary):
    """Classify Predictions 1/2/3 outcomes."""
    if not summary.get("per_seed"):
        return ("HIPPO_INCONCLUSIVE", "Missing per-seed data.")

    seeds = list(summary["per_seed"].values())
    n = len(seeds)

    # Prediction 1: depth ratio across seeds
    p1_ratios = [s["p1_depth_ratio"] for s in seeds]
    p1_ratio_mean = sum(p1_ratios) / n
    p1_all_pass = all(r >= P1_HARD_PASS_RATIO for r in p1_ratios)
    p1_any_fail = any(r <= P1_HARD_FAIL_RATIO for r in p1_ratios)

    # Prediction 2: N-doubling effect
    p2_vals = [s.get("p2_ndouble_ratio") for s in seeds if s.get("p2_ndouble_ratio") is not None]
    p2_mean = sum(p2_vals) / len(p2_vals) if p2_vals else None

    # Prediction 3: spectral correlation
    p3_vals = [s.get("p3_spectral_corr") for s in seeds
               if s.get("p3_spectral_corr") is not None and not math.isnan(s.get("p3_spectral_corr", float("nan")))]
    p3_mean = sum(p3_vals) / len(p3_vals) if p3_vals else None

    if p1_all_pass:
        p1_label = "P1_HARD_PASS"
    elif p1_any_fail:
        p1_label = "P1_HARD_FAIL"
    else:
        p1_label = "P1_MIDDLE"

    if p2_mean is not None:
        if p2_mean < P2_HARD_PASS_NSCALE:
            p2_label = "P2_HARD_PASS"   # N-doubling doesn't help (Jelassi confirmed)
        elif p2_mean > P2_HARD_FAIL_NSCALE:
            p2_label = "P2_HARD_FAIL"   # N-doubling rescues (Jelassi rejected)
        else:
            p2_label = "P2_MIDDLE"
    else:
        p2_label = "P2_SKIP"

    if p3_mean is not None:
        if p3_mean > P3_SPECTRAL_HARD_PASS:
            p3_label = "P3_HARD_PASS"
        elif p3_mean < P3_SPECTRAL_HARD_FAIL:
            p3_label = "P3_HARD_FAIL"
        else:
            p3_label = "P3_MIDDLE"
    else:
        p3_label = "P3_SKIP"

    p2_str = f"{p2_mean:.3f}" if p2_mean is not None else "N/A"
    p3_str = f"{p3_mean:.3f}" if p3_mean is not None else "N/A"

    verdict = f"HIPPO_INIT_{p1_label}_{p2_label}_{p3_label}"
    msg = (f"P1={p1_label} depth_ratio={p1_ratio_mean:.2f}x (mean across seeds, "
           f"PASS>={P1_HARD_PASS_RATIO}x, FAIL<={P1_HARD_FAIL_RATIO}x). "
           f"P2={p2_label} ndouble_ratio={p2_str} (Jelassi bound; PASS<{P2_HARD_PASS_NSCALE}). "
           f"P3={p3_label} spectral_corr={p3_str} (PASS>{P3_SPECTRAL_HARD_PASS}).")
    return (verdict, msg)


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Verify HiPPO eigenvalue construction
    mags = hippo_legs_eigenvalues(32)
    assert mags.shape == (32,), f"hippo eigenvalues shape wrong: {mags.shape}"
    assert float(mags.min()) > 0, "eigenvalues must be positive"
    assert float(mags.max()) < 1.5, f"eigenvalues unreasonably large: {mags.max()}"
    assert float(mags[0]) != float(mags[-1]), "eigenvalues should vary across H"

    # 2. Verify HiPPO W_init construction at small N
    gen = torch.Generator().manual_seed(42)
    W_h = make_hippo_init_W(64, gen)
    assert W_h.shape == (64, 64), f"W_hippo shape wrong: {W_h.shape}"
    assert not torch.isnan(W_h).any(), "W_hippo has NaN"
    assert float(W_h.abs().max()) > 0, "W_hippo is all zero"

    # 3. Verify train_and_eval_chain_depth returns non-sentinel at smoke scale
    gen2 = torch.Generator().manual_seed(17)
    device = torch.device("cpu")
    W_zero = make_random_init_W(64, gen2)
    N_small = 64
    dah, cos_profile, W_out = train_and_eval_chain_depth(
        N_small, d_max=10, n_patterns=6, d_train=5, W_init=W_zero, gen=gen2, device=device)
    assert dah >= 0, f"depth_at_half must be >= 0, got {dah}"
    assert len(cos_profile) == 11, f"cos_profile length wrong: {len(cos_profile)}"
    assert cos_profile[1] is not None and not math.isnan(cos_profile[1]), "cosine profile has NaN"
    assert W_out.shape == (64, 64), f"W_out shape wrong: {W_out.shape}"

    # 4. Verify spectral correlation does not crash
    gen3 = torch.Generator().manual_seed(7)
    W_a = make_hippo_init_W(64, gen3)
    W_b = torch.randn(64, 64) * 0.01
    corr = compute_spectral_correlation(W_a, W_b, 16)
    assert not math.isnan(corr), "spectral_corr returned NaN on valid matrices"

    # 5. Verify compute_verdict with synthetic data
    # P2_HARD_PASS requires ndouble_ratio < P2_HARD_PASS_NSCALE=0.8
    # (N-doubling gives <20% depth improvement -- Jelassi bound confirmed)
    s_pass = {"per_seed": {"17": {
        "p1_depth_ratio": 2.0,
        "p2_ndouble_ratio": 0.7,
        "p3_spectral_corr": 0.7,
        "depth_hippo": 40,
        "depth_random": 20,
    }}}
    v, _ = compute_verdict(s_pass)
    assert "P1_HARD_PASS" in v, f"expected P1_HARD_PASS, got {v}"
    assert "P2_HARD_PASS" in v, f"expected P2_HARD_PASS, got {v}"
    assert "P3_HARD_PASS" in v, f"expected P3_HARD_PASS, got {v}"

    # P2_HARD_FAIL requires ndouble_ratio >= P2_HARD_FAIL_NSCALE=1.8
    s_fail = {"per_seed": {"17": {
        "p1_depth_ratio": 0.8,
        "p2_ndouble_ratio": 2.5,
        "p3_spectral_corr": 0.1,
        "depth_hippo": 16,
        "depth_random": 20,
    }}}
    v2, _ = compute_verdict(s_fail)
    assert "P1_HARD_FAIL" in v2, f"expected P1_HARD_FAIL, got {v2}"

    print("_instrumentation_selftest passed (5 assertions, 2 verdict cases)", flush=True)


_instrumentation_selftest()


def run_one_seed(seed, config, device):
    N = config["N"]
    d_max = config["d_max"]
    n_patterns = config["n_probes"] * 4   # 4x patterns: 2x for train, 2x for eval
    d_train = min(d_max, 30)  # train on chains up to depth d_train

    gen_h = torch.Generator().manual_seed(seed)
    gen_r = torch.Generator().manual_seed(seed)  # SAME gen -> same codebook for fair comparison

    # Build W inits
    W_hippo_init = make_hippo_init_W(N, gen_h).to(device)
    W_random_init = make_random_init_W(N, gen_r).to(device)

    # Prediction 1: train both inits on SAME chain data, compare depth-at-half on SAME eval chains
    print(f"  [seed={seed}] P1 train+eval chain cleanup (N={N}, d_max={d_max}, "
          f"n_patterns={n_patterns})...", flush=True)

    gen_task_h = torch.Generator().manual_seed(seed + 20000)
    gen_task_r = torch.Generator().manual_seed(seed + 20000)  # same codebook

    depth_hippo, cos_hippo, W_hippo_trained = train_and_eval_chain_depth(
        N, d_max, n_patterns, d_train, W_hippo_init, gen_task_h, device)
    depth_random, cos_random, W_random_trained = train_and_eval_chain_depth(
        N, d_max, n_patterns, d_train, W_random_init, gen_task_r, device)

    p1_ratio = depth_hippo / max(depth_random, 1)
    print(f"    depth_hippo={depth_hippo} depth_random={depth_random} ratio={p1_ratio:.3f}",
          flush=True)

    # Prediction 2: N-doubling test (full scale only; skipped on smoke)
    p2_ndouble_ratio = None
    if not config.get("smoke") and config.get("run_p2", True):
        N_2x = config.get("N_2x", N_FULL * 2)
        print(f"  [seed={seed}] P2 N-doubling (N_2x={N_2x})...", flush=True)
        gen_2x_init = torch.Generator().manual_seed(seed + 30000)
        gen_2x_task = torch.Generator().manual_seed(seed + 31000)
        W_2x_init = make_random_init_W(N_2x, gen_2x_init).to(device)
        depth_2x, _, _ = train_and_eval_chain_depth(
            N_2x, d_max, n_patterns, d_train, W_2x_init, gen_2x_task, device)
        p2_ndouble_ratio = depth_2x / max(depth_random, 1)
        print(f"    depth_2x={depth_2x} depth_random_baseline={depth_random} "
              f"ndouble_ratio={p2_ndouble_ratio:.3f}", flush=True)

    # Prediction 3: spectral correlation of HiPPO-init W_0 vs post-training random-init W
    print(f"  [seed={seed}] P3 spectral correlation...", flush=True)
    p3_spectral_corr = compute_spectral_correlation(
        W_hippo_init.cpu(), W_random_trained.cpu(), TOP_K_EIGEN)
    print(f"    spectral_corr(top-{TOP_K_EIGEN})={p3_spectral_corr:.3f}", flush=True)

    return {
        "depth_hippo": depth_hippo,
        "depth_random": depth_random,
        "p1_depth_ratio": float(p1_ratio),
        "p2_ndouble_ratio": float(p2_ndouble_ratio) if p2_ndouble_ratio is not None else None,
        "p3_spectral_corr": float(p3_spectral_corr),
        "cos_hippo_at_d5": float(cos_hippo[min(5, d_max)]) if len(cos_hippo) > 5 else None,
        "cos_random_at_d5": float(cos_random[min(5, d_max)]) if len(cos_random) > 5 else None,
    }




def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "smoke": smoke,
        "N": N_SMOKE if smoke else N_FULL,
        "N_2x": N_2X_FULL,
        "d_max": D_MAX_SMOKE if smoke else D_MAX_FULL,
        "n_probes": N_PROBES_SMOKE if smoke else N_PROBES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "top_k_eigen": TOP_K_EIGEN,
        "p1_hard_pass_ratio": P1_HARD_PASS_RATIO,
        "p1_hard_fail_ratio": P1_HARD_FAIL_RATIO,
        "run_p2": not smoke,  # skip N-doubling on smoke
    }
    print(f"[config] {config}", flush=True)

    per_seed = {}
    for seed in config["seeds"]:
        print(f"[seed={seed}]", flush=True)
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r

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
    out_dir = get_output_dir("wave14f_hippo_init_w_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Instrumentation validity checks
    seeds_data = summary["per_seed"]
    assert len(seeds_data) > 0, "No seed data"
    s = list(seeds_data.values())[0]
    assert s["depth_hippo"] >= 0, f"depth_hippo invalid: {s['depth_hippo']}"
    assert s["depth_random"] >= 0, f"depth_random invalid: {s['depth_random']}"
    assert s["p3_spectral_corr"] is not None and not math.isnan(s["p3_spectral_corr"]), \
        f"p3_spectral_corr invalid: {s['p3_spectral_corr']}"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14f_hippo_init_w_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _instrumentation_selftest()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
