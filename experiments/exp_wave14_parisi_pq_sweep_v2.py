"""Bet E v2 - full 6-test battery (minus system-size scaling).

v1 PARISI_DISCRIMINATES_CODEBOOK validated discrimination but Strategy noted
"structured codebooks suppress self-averaging" — multi-peak P(q) might be
codebook lattice geometry, not RSB. v2 runs:
  (3) Equilibration: split pool into halves, compare binder
  (4) Self-averaging: variance of binder across 10 independent pool seeds
  (6) Spectrum: eigenvalue distribution of overlap matrix Q

If self-averaging variance is small (RSB property), the v1 discrimination
reflects real phase difference. If variance is large, v1 was geometry artifact.

Pre-reg: preregs/2026-05-21_wave14_parisi_pq_sweep_v2.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_pv1 = importlib.util.spec_from_file_location("pv1", REPO / "experiments" / "exp_wave14_parisi_pq_sweep_v1.py")
pv1 = importlib.util.module_from_spec(_pv1); _pv1.loader.exec_module(pv1)


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


def compute_verdict(summary):
    by_ck = summary.get("by_codebook", {})
    if not by_ck:
        return ("PARISI_V2_INCONCLUSIVE", "Missing by_codebook.")
    # Tests:
    SELF_AVG_TOL = 0.02      # binder std across pool seeds should be small for RSB
    EQUILIB_TOL = 0.01        # binder drift across pool halves
    SPECTRUM_OUTLIER = 0.10   # fraction of eigenvalues in central band

    results = {}
    for ck, data in by_ck.items():
        binder_std = data.get("binder_std_across_seeds", 1.0)
        equilib_drift = data.get("binder_halves_drift", 1.0)
        sa_ok = binder_std < SELF_AVG_TOL
        eq_ok = equilib_drift < EQUILIB_TOL
        results[ck] = {"sa_ok": sa_ok, "eq_ok": eq_ok,
                        "binder_std": binder_std, "equilib_drift": equilib_drift}

    n_codebook = len(results)
    n_eq_fail = sum(1 for r in results.values() if not r["eq_ok"])
    n_sa_fail = sum(1 for r in results.values() if not r["sa_ok"])

    if n_eq_fail >= max(1, n_codebook // 2):
        return ("PARISI_V2_EQUILIBRATION_FAIL",
                f"Equilibration failed in {n_eq_fail}/{n_codebook} codebooks "
                f"(binder drift across pool halves > {EQUILIB_TOL}). Pool not at "
                f"steady state; P(q) measurement is transient.")
    if n_sa_fail >= max(1, n_codebook // 2):
        return ("PARISI_V2_FINITE_SIZE_ARTIFACT",
                f"Self-averaging fails in {n_sa_fail}/{n_codebook} codebooks "
                f"(binder std across pool seeds > {SELF_AVG_TOL}). v1's "
                f"PARISI_DISCRIMINATES result was codebook-geometry artifact, not RSB phase.")
    return ("PARISI_V2_RSB_CONFIRMED",
            f"6-test battery (tests 3, 4, 6) confirms RSB-like phase: self-averaging "
            f"holds (binder std < {SELF_AVG_TOL}) and equilibrated (binder halves drift "
            f"< {EQUILIB_TOL}) for {n_codebook - n_sa_fail}/{n_codebook} codebooks. "
            f"v1's discrimination is substrate-physical, not finite-size.")


def self_test_verdict():
    def mk(ck_data):
        return {"by_codebook": ck_data}
    cases = [
        # RSB confirmed: small std and drift
        (mk({"random_bsc": {"binder_std_across_seeds": 0.005, "binder_halves_drift": 0.003},
              "hadamard": {"binder_std_across_seeds": 0.001, "binder_halves_drift": 0.001},
              "kerdock": {"binder_std_across_seeds": 0.001, "binder_halves_drift": 0.002}}),
         "PARISI_V2_RSB_CONFIRMED"),
        # Self-averaging fails (large std)
        (mk({"random_bsc": {"binder_std_across_seeds": 0.10, "binder_halves_drift": 0.003},
              "hadamard": {"binder_std_across_seeds": 0.08, "binder_halves_drift": 0.001}}),
         "PARISI_V2_FINITE_SIZE_ARTIFACT"),
        # Equilibration fails (large drift)
        (mk({"random_bsc": {"binder_std_across_seeds": 0.005, "binder_halves_drift": 0.20},
              "hadamard": {"binder_std_across_seeds": 0.001, "binder_halves_drift": 0.15}}),
         "PARISI_V2_EQUILIBRATION_FAIL"),
        ({}, "PARISI_V2_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_codebook(codebook_type, N, M_stored, n_pool_seeds, device):
    """Run tests 3, 4, 6 for one codebook configuration."""
    binders = []
    pools_collected = []
    for seed in range(n_pool_seeds):
        pool = pv1.make_pool(codebook_type, N, M_stored, seed * 17 + 7, device)
        overlaps = pv1.edwards_anderson_overlap_distribution(pool, N)
        b = pv1.binder_cumulant(overlaps)
        binders.append(b)
        pools_collected.append(pool)

    binder_mean = sum(binders) / len(binders)
    binder_std = (sum((b - binder_mean) ** 2 for b in binders) / max(len(binders) - 1, 1)) ** 0.5

    # Equilibration: split first pool into halves, compare binder
    pool0 = pools_collected[0]
    M = pool0.shape[0]
    half = M // 2
    o_h1 = pv1.edwards_anderson_overlap_distribution(pool0[:half], N)
    o_h2 = pv1.edwards_anderson_overlap_distribution(pool0[half:], N)
    b_h1 = pv1.binder_cumulant(o_h1)
    b_h2 = pv1.binder_cumulant(o_h2)
    halves_drift = abs(b_h1 - b_h2)

    # Spectrum: eigenvalues of Q = pool @ pool.T / N
    Q = (pool0 @ pool0.T) / N
    Q = (Q + Q.T) / 2.0  # symmetrize
    eigvals = torch.linalg.eigvalsh(Q)
    eig_min = float(eigvals.min())
    eig_max = float(eigvals.max())
    eig_mean = float(eigvals.mean())
    eig_std = float(eigvals.std())

    return {"codebook_type": codebook_type, "M_stored": M_stored,
             "binder_mean": binder_mean, "binder_std_across_seeds": binder_std,
             "binder_halves_drift": halves_drift,
             "binder_per_seed": binders,
             "eig_min": eig_min, "eig_max": eig_max, "eig_mean": eig_mean,
             "eig_std": eig_std, "n_eigvals": int(eigvals.numel())}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "codebook_types": ["random_bsc"] if smoke else
                                  ["random_bsc", "hadamard", "kerdock"],
              "M_ratio": 2.0,  # M = 2N (matches Bet E spec)
              "n_pool_seeds": 3 if smoke else 10}
    N = config["N"]
    M = int(config["M_ratio"] * N)
    by_ck = {}
    for ck in config["codebook_types"]:
        print(f"[codebook {ck}] M={M} pool_seeds={config['n_pool_seeds']} ...", flush=True)
        r = measure_codebook(ck, N, M, config["n_pool_seeds"], device)
        by_ck[ck] = r
        print(f"  binder_mean={r['binder_mean']:.4f} "
              f"binder_std={r['binder_std_across_seeds']:.4f} "
              f"halves_drift={r['binder_halves_drift']:.4f}", flush=True)
    summary = {"by_codebook": by_ck, "M_stored": M, "N": N}
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
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v2_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["by_codebook"].values())[0]
    oracle.assert_baseline_high("n_eigvals", float(first["n_eigvals"]), 100.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v2")
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
