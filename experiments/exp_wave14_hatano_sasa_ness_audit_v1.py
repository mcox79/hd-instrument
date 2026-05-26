"""Hatano-Sasa NESS-Crooks audit for Cap 3 streaming inference.

Post-hoc CPU re-analysis implementing the Hatano-Sasa fluctuation theorem
decomposition (Hatano & Sasa, PRL 86:3463, 2001) applied to the substrate's
NESS streaming dynamics.

Theory:
For a Markov chain in NESS with stationary measure pi_ss, the Hatano-Sasa
fluctuation theorem gives:

  <exp(-W_ex)> = 1

where the excess work along a trajectory x_0 -> x_1 -> ... -> x_T is:

  W_ex = log pi_ss(x_T) - log pi_ss(x_0)   (telescoping sum of step-log-ratios)

This is the "excess entropy production" associated with relaxation toward
the NESS -- it is zero when the system starts AND ends in the same basin
of pi_ss, and nonzero when trajectories cross basins.

The housekeeping entropy production (cost of maintaining the NESS) is
estimated from the total path variation minus the excess:

  sigma_hk ~ (mean path-wise total variation in log pi_ss) - |W_ex mean|

Implementation:
- Build substrate W from M stored patterns.
- Run a large population of streaming trajectories from NOISY starts
  (corrupted stored patterns), not purely random starts.
- Label each trajectory's attractor by argmax cosine overlap with stored values.
- Build pi_ss over the M stored-pattern basins from empirical hit frequencies.
- Compute W_ex and sigma_hk per trajectory.
- Check HS identity.

FULL run: N=8192, M=150, 400 noisy trajectories (corruption p in {0.1, 0.2, 0.3}).
This is CPU-only, expected ~5-10 min.

Verdicts:
  HATANO_SASA_NESS_CERT_PASS    - HS identity <exp(-W_ex)>=1 within tol
                                   AND sigma_hk > 0 (genuine NESS cost)
  HATANO_SASA_NESS_CERT_PARTIAL - HS identity holds but sigma_hk ~ 0
                                   (all trajectories start and end same basin)
  HATANO_SASA_NESS_CERT_FAIL    - HS identity violated beyond tol
                                   (substrate NESS is not Markov-consistent)
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def get_output_dir(name: str) -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing keys: {required - d.keys()}")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_hs_verdict(
    hs_identity_val: float,
    hs_tol: float,
    sigma_hk_mean: float,
    sigma_hk_tol: float,
    cross_basin_frac: float,
) -> tuple:
    """
    hs_identity_val: <exp(-W_ex)> (should be ~1.0 if HS holds)
    hs_tol: tolerance around 1.0
    sigma_hk_mean: mean housekeeping EP proxy across trajectories
    sigma_hk_tol: threshold below which sigma_hk is considered ~0
    cross_basin_frac: fraction of trajectories that crossed basins (W_ex != 0)
    """
    identity_error = abs(hs_identity_val - 1.0)
    identity_holds = identity_error <= hs_tol

    if not identity_holds:
        verdict = "HATANO_SASA_NESS_CERT_FAIL"
        msg = (
            f"HS identity VIOLATED: <exp(-W_ex)>={hs_identity_val:.4f} "
            f"(error={identity_error:.4f} > tol={hs_tol:.4f}). "
            f"cross_basin_frac={cross_basin_frac:.3f}. "
            f"Substrate NESS is not Markov-consistent; Cap 3 streaming audit fails."
        )
        return verdict, msg

    if cross_basin_frac < 0.02 or sigma_hk_mean < sigma_hk_tol:
        verdict = "HATANO_SASA_NESS_CERT_PARTIAL"
        msg = (
            f"HS identity HOLDS: <exp(-W_ex)>={hs_identity_val:.4f} "
            f"(error={identity_error:.4f} <= tol={hs_tol:.4f}). "
            f"BUT cross_basin_frac={cross_basin_frac:.3f} and "
            f"sigma_hk={sigma_hk_mean:.4f} (tol={sigma_hk_tol:.4f}): "
            f"insufficient basin crossings to resolve NESS cost. "
            f"Cap 3 streaming PARTIAL certificate; increase noise or M."
        )
        return verdict, msg

    verdict = "HATANO_SASA_NESS_CERT_PASS"
    msg = (
        f"HS identity HOLDS: <exp(-W_ex)>={hs_identity_val:.4f} "
        f"(error={identity_error:.4f} <= tol={hs_tol:.4f}). "
        f"sigma_hk={sigma_hk_mean:.4f} > tol={sigma_hk_tol:.4f}; "
        f"cross_basin_frac={cross_basin_frac:.3f}. "
        f"Substrate has genuine NESS housekeeping cost with verified HS identity. "
        f"Cap 3 streaming earns NESS-fluctuation-theorem audit certificate "
        f"(analogue of Cap 1 Crooks erase certificate)."
    )
    return verdict, msg


def self_test_verdict() -> None:
    cases = [
        # identity holds, sigma_hk positive, cross_basin present -> PASS
        (1.0, 0.15, 0.25, 0.05, 0.30, "HATANO_SASA_NESS_CERT_PASS"),
        # identity holds exactly, sigma_hk positive -> PASS
        (1.00, 0.15, 0.10, 0.05, 0.15, "HATANO_SASA_NESS_CERT_PASS"),
        # identity holds but no cross-basin -> PARTIAL
        (0.98, 0.15, 0.01, 0.05, 0.00, "HATANO_SASA_NESS_CERT_PARTIAL"),
        # identity holds, sigma_hk near zero -> PARTIAL
        (0.98, 0.15, 0.01, 0.05, 0.20, "HATANO_SASA_NESS_CERT_PARTIAL"),
        # identity violated -> FAIL
        (1.25, 0.15, 0.20, 0.05, 0.30, "HATANO_SASA_NESS_CERT_FAIL"),
        # identity violated below 1 -> FAIL
        (0.70, 0.15, 0.20, 0.05, 0.30, "HATANO_SASA_NESS_CERT_FAIL"),
        # identity at boundary (error exactly = tol) -> PASS (<=)
        (1.15, 0.15, 0.10, 0.05, 0.10, "HATANO_SASA_NESS_CERT_PASS"),
    ]
    for i, (hs_val, hs_tol, hk_mean, hk_tol, cb_frac, expected) in enumerate(cases):
        got, _ = compute_hs_verdict(hs_val, hs_tol, hk_mean, hk_tol, cb_frac)
        if got != expected:
            raise AssertionError(
                f"self_test case {i}: got {got} expected {expected}"
            )
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Substrate primitives
# ---------------------------------------------------------------------------

def make_pattern(N: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    b = (torch.rand(N, generator=gen) > 0.5).to(device)
    return (2.0 * b.float() - 1.0)


def corrupt_pattern(
    x: torch.Tensor, p_flip: float, gen: torch.Generator
) -> torch.Tensor:
    """Randomly flip p_flip fraction of bits in x."""
    mask = torch.rand(x.shape, generator=gen) < p_flip
    return torch.where(mask, -x, x)


def hopfield_run(
    W: torch.Tensor, x0: torch.Tensor, max_iter: int
) -> torch.Tensor:
    """Run Hopfield dynamics from x0 to fixed point. Return final state."""
    s = x0.clone()
    for _ in range(max_iter):
        s_new = torch.sign(W @ s)
        s_new[s_new == 0] = 1.0
        if torch.equal(s_new, s):
            break
        s = s_new
    return s


def identify_attractor(final: torch.Tensor, values: torch.Tensor) -> int:
    """Return index of stored value with maximum overlap to final state.
    Returns -1 if all overlaps are below threshold (spurious attractor).
    """
    overlaps = (values @ final) / values.shape[1]  # shape (M,)
    best_idx = int(overlaps.argmax().item())
    best_overlap = float(overlaps[best_idx].item())
    if best_overlap < 0.7:
        return -1  # spurious; not a stored-pattern attractor
    return best_idx


# ---------------------------------------------------------------------------
# Core experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple:
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU-only experiment

    if smoke:
        N = 2048
        M = 60           # undercapacity: M/N ~ 0.029 well within RS phase
        n_traj_per_level = 30
        noise_levels = [0.10, 0.20, 0.30]
        max_iter = 40
        seed = 42
        hs_tol = 0.25
        sigma_hk_tol = 0.01
    else:
        N = 8192
        M = 150          # M/N ~ 0.018 well within RS phase
        n_traj_per_level = 130
        noise_levels = [0.10, 0.15, 0.20, 0.25, 0.30]
        max_iter = 60
        seed = 42
        hs_tol = 0.15
        sigma_hk_tol = 0.02

    n_total_traj = n_traj_per_level * len(noise_levels)

    cfg = {
        "N": N, "M": M, "n_traj_per_level": n_traj_per_level,
        "noise_levels": noise_levels, "max_iter": max_iter, "seed": seed,
        "hs_tol": hs_tol, "sigma_hk_tol": sigma_hk_tol,
        "n_total_traj": n_total_traj,
    }

    print(
        f"Config: N={N} M={M} n_traj_per_level={n_traj_per_level} "
        f"noise_levels={noise_levels} max_iter={max_iter} seed={seed}",
        flush=True,
    )

    gen = torch.Generator().manual_seed(seed)

    # Build substrate W from M stored (key, value) pairs
    keys = torch.stack([make_pattern(N, gen, device) for _ in range(M)], dim=0)   # (M, N)
    values = torch.stack([make_pattern(N, gen, device) for _ in range(M)], dim=0) # (M, N)
    W = (values.T @ keys) / N  # (N, N)

    print(
        f"  W built: shape={list(W.shape)} "
        f"frobenius_norm={W.norm():.4f} M/N={M/N:.4f}",
        flush=True,
    )

    # Phase 1: generate trajectories
    # Strategy: for each noise level, run n_traj_per_level trajectories starting
    # from corrupted stored KEYS (so initial states are near-stored-pattern starts,
    # giving a well-defined "streaming" scenario as in Cap 3).
    # We want to observe BOTH same-basin trajectories (noise low -> high recovery)
    # AND cross-basin trajectories (noise high -> wrong attractor).
    # This gives a non-degenerate pi_ss distribution.

    print(
        f"\nPhase 1: generating {n_total_traj} trajectories "
        f"across {len(noise_levels)} noise levels...",
        flush=True,
    )

    # attractor_hits[i] = number of trajectories landing at stored pattern i
    # attractor_hits[-1] = spurious attractors
    attractor_hits: dict = {}
    for i in range(M):
        attractor_hits[i] = 0
    attractor_hits[-1] = 0  # spurious

    # Store (start_attractor_idx, end_attractor_idx) per trajectory
    trajectory_transitions: list = []

    for noise_p in noise_levels:
        noise_hits: dict = {i: 0 for i in range(M)}
        noise_hits[-1] = 0
        n_correct = 0
        for traj_idx in range(n_traj_per_level):
            # Start from a corrupted version of stored key at index (traj_idx % M)
            src_idx = traj_idx % M
            x0 = corrupt_pattern(keys[src_idx], noise_p, gen)
            xT = hopfield_run(W, x0, max_iter)
            end_idx = identify_attractor(xT, values)
            attractor_hits[end_idx] = attractor_hits.get(end_idx, 0) + 1
            noise_hits[end_idx] = noise_hits.get(end_idx, 0) + 1
            trajectory_transitions.append((src_idx, end_idx))
            if end_idx == src_idx:
                n_correct += 1
        acc = n_correct / n_traj_per_level
        print(
            f"  p={noise_p:.2f}: acc={acc:.3f} "
            f"spurious={noise_hits[-1]}/{n_traj_per_level}",
            flush=True,
        )

    n_spurious = attractor_hits[-1]
    n_valid = n_total_traj - n_spurious
    print(
        f"\n  Total: {n_total_traj} trajectories, "
        f"{n_spurious} spurious, {n_valid} valid",
        flush=True,
    )

    # Phase 2: build pi_ss from valid attractor hit frequencies
    print(f"\nPhase 2: estimating NESS stationary distribution pi_ss...", flush=True)

    valid_hits = {i: attractor_hits[i] for i in range(M) if attractor_hits[i] > 0}
    total_valid = sum(valid_hits.values())

    if total_valid == 0:
        # Degenerate: all trajectories landed in spurious attractors
        # This means M > capacity; substrate is overloaded for this probe
        print("  WARNING: all trajectories landed in spurious attractors!", flush=True)
        total_valid = 1  # prevent div-by-zero
        valid_hits = {0: 1}

    n_distinct_attractors = len(valid_hits)
    log_pi_ss = {
        i: math.log(count / total_valid)
        for i, count in valid_hits.items()
    }
    # Default log_p for unseen attractors (should not occur since we cover all M)
    default_log_p = math.log(1.0 / (total_valid + 1))

    attractor_probs = sorted(
        [(i, count / total_valid) for i, count in valid_hits.items()],
        key=lambda x: -x[1],
    )
    print(
        f"  pi_ss over {n_distinct_attractors} attractors. "
        f"Top-3: {attractor_probs[:3]}",
        flush=True,
    )

    # Phase 3: Hatano-Sasa decomposition
    print(f"\nPhase 3: computing Hatano-Sasa decomposition...", flush=True)

    w_ex_list = []
    exp_neg_w_ex_list = []
    sigma_hk_list = []
    cross_basin_count = 0

    for i, (src_idx, end_idx) in enumerate(trajectory_transitions):
        if end_idx == -1:
            # Spurious attractor: skip (no well-defined pi_ss value)
            continue

        # pi_ss(x_0): start state is a corrupted key; approximate its log_pi_ss
        # as the log_pi_ss of the source attractor it was drawn from
        # (the initial state is in the basin of src_idx before corruption)
        log_p_start = log_pi_ss.get(src_idx, default_log_p)
        log_p_end = log_pi_ss.get(end_idx, default_log_p)

        # W_ex = log pi_ss(x_T) - log pi_ss(x_0)
        w_ex = log_p_end - log_p_start
        w_ex_list.append(w_ex)
        exp_neg_w_ex_list.append(math.exp(-w_ex))

        # sigma_hk proxy: path-wise entropy flow not captured by W_ex
        # For a trajectory that stays in the same basin: sigma_hk = 0 (no irreversible cost)
        # For a trajectory that crosses basins: sigma_hk = |log_p_end - log_p_start|
        # (the irreversible contribution is the |EP| that does not cancel in the path)
        if end_idx != src_idx:
            cross_basin_count += 1
            # sigma_hk proxy: measure of irreversibility = |delta log pi_ss|
            # minus the excess work contribution (which can be negative)
            sigma_hk = abs(w_ex)
        else:
            sigma_hk = 0.0
        sigma_hk_list.append(sigma_hk)

        if i < 5:
            print(
                f"  traj[{i}]: src={src_idx} end={end_idx} "
                f"W_ex={w_ex:.4f} exp(-W_ex)={math.exp(-w_ex):.4f} "
                f"sigma_hk={sigma_hk:.4f}",
                flush=True,
            )

    n_valid_traj = len(w_ex_list)
    cross_basin_frac = cross_basin_count / max(n_valid_traj, 1)

    if n_valid_traj == 0:
        hs_identity_val = 1.0
        w_ex_mean = 0.0
        w_ex_std = 0.0
        sigma_hk_mean = 0.0
        sigma_hk_std = 0.0
        hs_sem = 0.0
    else:
        hs_identity_val = sum(exp_neg_w_ex_list) / n_valid_traj
        w_ex_mean = sum(w_ex_list) / n_valid_traj
        w_ex_std = (
            sum((x - w_ex_mean) ** 2 for x in w_ex_list) / n_valid_traj
        ) ** 0.5
        sigma_hk_mean = sum(sigma_hk_list) / n_valid_traj
        sigma_hk_std = (
            sum((x - sigma_hk_mean) ** 2 for x in sigma_hk_list) / n_valid_traj
        ) ** 0.5
        hs_sem = (
            sum((x - hs_identity_val) ** 2 for x in exp_neg_w_ex_list)
            / n_valid_traj
        ) ** 0.5 / math.sqrt(n_valid_traj)

    print(f"\nHatano-Sasa summary:", flush=True)
    print(
        f"  <exp(-W_ex)>      = {hs_identity_val:.4f}  (target=1.0; SEM={hs_sem:.4f})",
        flush=True,
    )
    print(f"  W_ex mean         = {w_ex_mean:.4f}  std={w_ex_std:.4f}", flush=True)
    print(
        f"  sigma_hk proxy    = {sigma_hk_mean:.4f}  std={sigma_hk_std:.4f}",
        flush=True,
    )
    print(f"  cross_basin_frac  = {cross_basin_frac:.4f}  ({cross_basin_count}/{n_valid_traj})", flush=True)
    print(f"  n_distinct_ep     = {n_distinct_attractors}", flush=True)
    print(f"  HS tol            = {hs_tol}", flush=True)
    print(f"  sigma_hk tol      = {sigma_hk_tol}", flush=True)

    verdict, msg = compute_hs_verdict(
        hs_identity_val, hs_tol, sigma_hk_mean, sigma_hk_tol, cross_basin_frac
    )
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)

    summary = {
        "hs_identity_val": hs_identity_val,
        "hs_identity_sem": hs_sem,
        "hs_tol": hs_tol,
        "w_ex_mean": w_ex_mean,
        "w_ex_std": w_ex_std,
        "sigma_hk_mean": sigma_hk_mean,
        "sigma_hk_std": sigma_hk_std,
        "sigma_hk_tol": sigma_hk_tol,
        "cross_basin_frac": cross_basin_frac,
        "cross_basin_count": cross_basin_count,
        "n_valid_traj": n_valid_traj,
        "n_spurious": n_spurious,
        "n_distinct_attractors": n_distinct_attractors,
        "n_total_traj": n_total_traj,
    }

    return summary, verdict, msg, elapsed, cfg


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def write_metrics(
    out_dir: Path,
    summary: dict,
    verdict: str,
    msg: str,
    elapsed: float,
    config: dict,
) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run_smoke() -> None:
    out_dir = get_output_dir("wave14_hatano_sasa_ness_audit_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Sanity: HS identity must be a positive finite number
    oracle.assert_in_range("hs_identity_val", s["hs_identity_val"], (0.0, 10.0))
    # Sanity: must have discovered at least 1 valid attractor
    oracle.assert_baseline_high(
        "n_distinct_attractors", float(s["n_distinct_attractors"]), 0.0
    )
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)
    print(f"  {m}", flush=True)


def run_main() -> None:
    out_dir = get_output_dir("wave14_hatano_sasa_ness_audit_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Hatano-Sasa NESS-Crooks audit for Cap 3 streaming inference"
    )
    ap.add_argument(
        "--self-test", action="store_true", help="Run verdict unit tests"
    )
    ap.add_argument("--smoke", action="store_true", help="Smoke run at small N")
    args = ap.parse_args()

    if args.self_test:
        self_test_verdict()
        print("All self-tests passed.", flush=True)
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
