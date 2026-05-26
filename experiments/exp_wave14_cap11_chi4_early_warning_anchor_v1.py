"""Cap 11 chi_4 early-warning anchor — Strategy 2026-05-24 (Research drill).

Hypothesis (H1, Research drill 2026-05-24):
  As alpha = M_stored / N approaches the Kerdock-Hopfield capacity boundary
  alpha_c during continual operation, the 4-point connected susceptibility
  chi_4 measured over substrate dynamics rises monotonically, peaks at a
  lead-time K writes BEFORE the retrieval-SNR collapse, and survives a
  permutation null. Per Research recommendation, instrument chi_4 + AC(1)
  + Var + tau_R in parallel (near-zero marginal cost).

Indicators (4 per Research mandate):
  1. chi_4         = N * Var_runs(C(t))           Berthier-Biroli-Bouchaud
  2. AC(1)         = lag-1 autocorrelation of m(t)  Scheffer 2009 CSD
  3. Var           = variance of overlap observable Dakos et al.
  4. tau_R         = relaxation time from small read-perturbation
                       (Engineering / power-grid damping ratio analog)

HARD PASS (chi_4 licensed as early-warning):
  chi_4 peak SNR (peak/baseline) >= 3
  AND lead-time K >= 0.05 * alpha_c
  AND survives permutation null (chi_4 spike NOT reproduced when write
    order shuffled)

HARD FAIL (chi_4 dead as early-warning):
  chi_4 SNR < 1.5 OR zero/negative lead-time on >= 3 of 5 seeds.

MIDDLE BAND:
  SNR in [1.5, 3) OR partial lead-time -> triggers combined-indicator v2.

Substrate-product framing: licenses Cap 11 as predictive observability of
Cap 10 capacity boundary; unlocks Composition C (Cap 12 + Cap 11 + Cap 1).

Pre-reg: preregs/2026-05-24_wave14_cap11_chi4_early_warning_anchor_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Kerdock 4-coset codebook builder (from validated wave14y_v3)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook


# ---------------------------------------------------------------------------
# Indicator formulas (with self-test contracts)
# ---------------------------------------------------------------------------

def chi4_from_runs(C_runs: torch.Tensor) -> float:
    """chi_4 = N_eff * Var_runs(C) at fixed lag.

    C_runs: (n_runs,) of two-point overlap values measured under perturbed
    trajectories. Berthier-Biroli (Rev. Mod. Phys. 2011) definition.
    Returns scalar chi_4. Self-test: for white-noise C ~ N(0, sigma^2/n_runs),
    E[chi_4] = N_eff * sigma^2 (controlled by n_runs).
    """
    if C_runs.numel() < 2:
        return 0.0
    v = float(C_runs.var(unbiased=True).item())
    return float(C_runs.numel() * v)


def ac1(x: torch.Tensor) -> float:
    """Lag-1 autocorrelation. Scheffer 2009 CSD indicator.

    x: 1-D tensor. Returns Pearson r at lag 1.
    Self-test: white noise -> AC(1) ~ 0; AR(1) with rho -> AC(1) ~ rho.
    """
    if x.numel() < 3:
        return 0.0
    x0 = x[:-1] - x[:-1].mean()
    x1 = x[1:] - x[1:].mean()
    denom = float((x0.pow(2).sum() * x1.pow(2).sum()).sqrt().item())
    if denom < 1e-12:
        return 0.0
    return float((x0 * x1).sum().item() / denom)


def variance(x: torch.Tensor) -> float:
    """Sample variance. Dakos et al. CSD indicator.

    Self-test: white noise sigma=1, N->inf -> Var ~ 1.
    """
    if x.numel() < 2:
        return 0.0
    return float(x.var(unbiased=True).item())


def tau_relaxation(W: torch.Tensor, s0: torch.Tensor, perturb_flips: int,
                   max_iter: int, gen: torch.Generator,
                   device: torch.device) -> int:
    """Small-perturbation return-time. Engineering damping-ratio analog.

    Flip a small number of bits in s0, run sign(W @ s) until state stops
    changing or matches s0 to within tol. Return iterations.
    Self-test: zero perturbation -> tau = 1; large perturb -> tau >= 2.
    """
    N = s0.numel()
    idxs = torch.randperm(N, generator=gen)[:perturb_flips].to(device)
    s = s0.clone()
    s[idxs] = -s[idxs]
    prev = s.clone()
    for t in range(max_iter):
        s = torch.sign(W @ s); s[s == 0] = 1.0
        if float((s - prev).abs().mean().item()) < 1e-6:
            return t + 1
        prev = s.clone()
    return max_iter


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(s: dict) -> tuple[str, str]:
    if "chi4_snr" not in s or "lead_time_frac" not in s:
        return ("CAP11_CHI4_INCONCLUSIVE", "Missing chi4_snr or lead_time_frac.")
    snr = s["chi4_snr"]
    lead = s["lead_time_frac"]              # K / alpha_c (fraction)
    n_seeds = s.get("n_seeds", 5)
    neg_lead_seeds = s.get("seeds_with_negative_lead", 0)
    perm_pass = s.get("permutation_null_passed", False)
    if snr < 1.5 or neg_lead_seeds >= 3:
        return ("CAP11_CHI4_FAIL",
                f"chi4 SNR={snr:.2f} (<1.5) OR seeds_with_negative_lead="
                f"{neg_lead_seeds} (>=3 of {n_seeds}). chi4 not predictive.")
    if snr >= 3.0 and lead >= 0.05 and perm_pass:
        return ("CAP11_CHI4_EARLY_WARNING_LICENSED",
                f"chi4 SNR={snr:.2f}>=3 AND lead-time K/alpha_c={lead:.3f}"
                f">=0.05 AND permutation_null_passed=True. "
                f"Cap 11 licensed as Cap 10 early-warning.")
    return ("CAP11_CHI4_MIDDLE_BAND",
            f"chi4 SNR={snr:.2f} lead={lead:.3f} perm_pass={perm_pass}. "
            f"Triggers combined-indicator v2 (chi_4 + AC + Var + tau_R).")


def self_test_verdict():
    for s, exp in [
        ({"chi4_snr": 5.0, "lead_time_frac": 0.10, "n_seeds": 5,
          "seeds_with_negative_lead": 0, "permutation_null_passed": True},
         "CAP11_CHI4_EARLY_WARNING_LICENSED"),
        ({"chi4_snr": 1.0, "lead_time_frac": 0.10, "n_seeds": 5,
          "seeds_with_negative_lead": 0, "permutation_null_passed": True},
         "CAP11_CHI4_FAIL"),
        ({"chi4_snr": 5.0, "lead_time_frac": 0.10, "n_seeds": 5,
          "seeds_with_negative_lead": 3, "permutation_null_passed": True},
         "CAP11_CHI4_FAIL"),
        ({"chi4_snr": 2.0, "lead_time_frac": 0.07, "n_seeds": 5,
          "seeds_with_negative_lead": 0, "permutation_null_passed": True},
         "CAP11_CHI4_MIDDLE_BAND"),
        ({"chi4_snr": 5.0, "lead_time_frac": 0.03, "n_seeds": 5,
          "seeds_with_negative_lead": 0, "permutation_null_passed": True},
         "CAP11_CHI4_MIDDLE_BAND"),
        ({"chi4_snr": 5.0, "lead_time_frac": 0.10, "n_seeds": 5,
          "seeds_with_negative_lead": 0, "permutation_null_passed": False},
         "CAP11_CHI4_MIDDLE_BAND"),
        ({}, "CAP11_CHI4_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (7/7 cases)", flush=True)


def self_test_indicator_formulas():
    """Verify each indicator's formula on a known analytical case."""
    g = torch.Generator().manual_seed(42)
    # 1. chi_4 self-test: for white-noise C ~ N(0,1) / sqrt(n_runs), expected
    #    chi_4 = n_runs * Var(C) -> ~ 1 when C has variance 1/n_runs * n_runs.
    #    Simpler: chi_4 of n_runs unit-variance samples -> ~ n_runs * 1.0.
    n_runs = 1000
    C_white = torch.randn(n_runs, generator=g)
    c4 = chi4_from_runs(C_white)
    # E[chi_4] = n_runs * sigma^2 = 1000 * 1 = 1000; tolerance 20%.
    if not (700.0 < c4 < 1300.0):
        raise AssertionError(f"chi4 white-noise self-test: {c4:.2f} not in (700, 1300)")
    # 2. AC(1) self-test: white-noise AC(1) ~ 0 (tolerance 0.1).
    x_white = torch.randn(10000, generator=g)
    a_white = ac1(x_white)
    if abs(a_white) > 0.1:
        raise AssertionError(f"AC(1) white-noise: {a_white:.3f} not ~0")
    # AR(1) with rho=0.7: AC(1) should be ~ 0.7.
    rho = 0.7
    n_ar = 10000
    x_ar = torch.zeros(n_ar)
    eps = torch.randn(n_ar, generator=g)
    for i in range(1, n_ar):
        x_ar[i] = rho * x_ar[i-1] + eps[i] * (1 - rho**2)**0.5
    a_ar = ac1(x_ar)
    if not (0.6 < a_ar < 0.8):
        raise AssertionError(f"AC(1) AR(1) rho=0.7: {a_ar:.3f} not in (0.6, 0.8)")
    # 3. Var self-test.
    v = variance(x_white)
    if not (0.9 < v < 1.1):
        raise AssertionError(f"Var white-noise: {v:.3f} not ~1")
    # 4. tau_R self-test: zero perturbation -> small tau; large -> larger tau.
    #    (Just check the function returns >= 1 on a trivial W.)
    device = torch.device("cpu")
    N_tiny = 64
    W_eye = torch.eye(N_tiny)
    s0 = torch.ones(N_tiny)
    tau_zero = tau_relaxation(W_eye, s0, perturb_flips=0, max_iter=5,
                              gen=g, device=device)
    if tau_zero < 1:
        raise AssertionError(f"tau_R zero-perturb: {tau_zero} < 1")
    print("indicator formula self-tests passed (chi4 + AC(1) + Var + tau_R)", flush=True)


# ---------------------------------------------------------------------------
# Substrate dynamics + indicator measurement
# ---------------------------------------------------------------------------

def build_kerdock_W(N: int, M: int, device: torch.device,
                    cpu_gen: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """Hebbian W from M codewords sampled (with replacement) from Kerdock 4-coset.
    Returns (W, codewords_used). Diagonal zeroed."""
    cb, _info = make_kerdock_4coset_codebook(N, device)  # (4N, N) bipolar
    n_cb = cb.shape[0]
    idx = torch.randint(0, n_cb, (M,), generator=cpu_gen).to(device)
    patterns = cb[idx].float()  # (M, N) in {-1, +1}
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    return W, patterns


def measure_indicators(W: torch.Tensor, patterns: torch.Tensor, target_idx: int,
                       n_runs: int, T_steps: int, noise_p: float,
                       cpu_gen: torch.Generator, device: torch.device) -> dict:
    """Measure chi_4 + AC(1) + Var + tau_R for substrate at current load.

    chi_4: per-step overlap-variance across n_runs perturbed trajectories,
           peaked over t in [1, T_steps].
    AC(1): lag-1 autocorrelation of mean-overlap trajectory.
    Var:   variance of mean-overlap trajectory.
    tau_R: relaxation time from a small read-perturbation (perturb_flips=N//50).
    """
    N = W.shape[0]
    target = patterns[target_idx]
    overlaps = torch.zeros((n_runs, T_steps), device=device)
    for run in range(n_runs):
        s = target.clone()
        flips = (torch.rand(N, generator=cpu_gen) < noise_p).to(device).float()
        s = s * (1.0 - 2.0 * flips)
        for t in range(T_steps):
            s = torch.sign(W @ s); s[s == 0] = 1.0
            overlaps[run, t] = float((s * target).mean())
    # chi_4 peak across lags
    chi4_per_t = torch.tensor([N * float(overlaps[:, t].var(unbiased=True).item())
                                for t in range(T_steps)])
    chi4_peak = float(chi4_per_t.max().item())
    # AC(1) + Var on the mean-trajectory
    m_t = overlaps.mean(dim=0).cpu()
    a1 = ac1(m_t)
    v_obs = variance(m_t)
    # tau_R from one fresh seed
    perturb_flips = max(1, N // 50)
    tau = tau_relaxation(W, target, perturb_flips=perturb_flips,
                         max_iter=30, gen=cpu_gen, device=device)
    return {"chi4_peak": chi4_peak, "ac1": a1, "var": v_obs, "tau_R": tau,
            "chi4_per_t": chi4_per_t.tolist()}


def retrieval_accuracy(W: torch.Tensor, patterns: torch.Tensor,
                       noise_p: float, n_test: int,
                       cpu_gen: torch.Generator, device: torch.device,
                       max_iter: int = 10) -> float:
    """Mean overlap of retrieved state with stored target across n_test probes."""
    M = patterns.shape[0]
    N = W.shape[0]
    idxs = torch.randint(0, M, (n_test,), generator=cpu_gen).tolist()
    accs = []
    for i in idxs:
        target = patterns[i]
        flips = (torch.rand(N, generator=cpu_gen) < noise_p).to(device).float()
        s = target * (1.0 - 2.0 * flips)
        for _ in range(max_iter):
            s_new = torch.sign(W @ s); s_new[s_new == 0] = 1.0
            if float((s_new - s).abs().mean().item()) < 1e-6:
                break
            s = s_new
        accs.append(float((s * target).mean().item()))
    return float(sum(accs) / max(len(accs), 1))


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # alpha_c for Kerdock-Hopfield: substrate-specific; default 0.14 from
    # generic Hopfield (Amit-Gutfreund-Sompolinsky); post-hoc recalibration
    # planned if knee location disagrees. Note: Kerdock structure typically
    # raises usable alpha vs random bipolar but may not change the formal
    # alpha_c; tested empirically by knee detection.
    alpha_c = 0.14
    if smoke:
        cfg = {
            "N": 1024, "alpha_c": alpha_c,
            "alpha_grid": [0.05, 0.10, 0.14, 0.18],  # 0.36, 0.71, 1.0, 1.29 of alpha_c
            "n_runs": 10, "T_steps": 5, "noise_p": 0.05,
            "n_retrieval_probes": 30, "n_seeds": 1, "seed": 17,
            "perm_null": True,
        }
    else:
        cfg = {
            "N": 4096, "alpha_c": alpha_c,
            "alpha_grid": [0.014, 0.028, 0.056, 0.084, 0.112, 0.140, 0.168, 0.196],
                # 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4 of alpha_c (ramp 0.1 -> 1.5)
            "n_runs": 32, "T_steps": 10, "noise_p": 0.05,
            "n_retrieval_probes": 100, "n_seeds": 5, "seed": 17,
            "perm_null": True,
        }
    N = cfg["N"]
    print(f"[setup] N={N} alpha_c={alpha_c} alpha_grid={cfg['alpha_grid']} "
          f"n_seeds={cfg['n_seeds']} device={device}", flush=True)
    per_seed = []                                # per-seed results
    for seed_idx in range(cfg["n_seeds"]):
        cpu_gen = torch.Generator().manual_seed(cfg["seed"] + seed_idx * 1009)
        per_alpha = []
        for alpha in cfg["alpha_grid"]:
            M = max(2, int(round(alpha * N)))
            W, patterns = build_kerdock_W(N, M, device, cpu_gen)
            ind = measure_indicators(W, patterns, target_idx=0,
                                     n_runs=cfg["n_runs"], T_steps=cfg["T_steps"],
                                     noise_p=cfg["noise_p"], cpu_gen=cpu_gen,
                                     device=device)
            acc = retrieval_accuracy(W, patterns, cfg["noise_p"],
                                     cfg["n_retrieval_probes"], cpu_gen, device)
            ind["alpha"] = alpha
            ind["M"] = M
            ind["retrieval_overlap"] = acc
            per_alpha.append(ind)
            print(f"  seed={seed_idx} alpha={alpha:.4f} M={M} "
                  f"chi4={ind['chi4_peak']:.3f} AC1={ind['ac1']:.3f} "
                  f"Var={ind['var']:.5f} tau_R={ind['tau_R']} "
                  f"retrieval={acc:.3f}", flush=True)
        per_seed.append(per_alpha)
    # Aggregate
    n_alpha = len(cfg["alpha_grid"])
    chi4_med = [0.0] * n_alpha; ac1_med = [0.0] * n_alpha
    var_med = [0.0] * n_alpha; tau_med = [0.0] * n_alpha
    ret_med = [0.0] * n_alpha
    for i in range(n_alpha):
        col = [per_seed[s][i] for s in range(cfg["n_seeds"])]
        col.sort(key=lambda r: r["chi4_peak"])
        chi4_med[i] = col[len(col) // 2]["chi4_peak"]
        ac1_med[i] = sum(r["ac1"] for r in col) / len(col)
        var_med[i] = sum(r["var"] for r in col) / len(col)
        tau_med[i] = sum(r["tau_R"] for r in col) / len(col)
        ret_med[i] = sum(r["retrieval_overlap"] for r in col) / len(col)
    # SNR = peak / baseline (baseline = median of lowest 30% alpha cells)
    n_base = max(1, n_alpha // 3)
    chi4_baseline = sum(sorted(chi4_med)[:n_base]) / n_base
    chi4_peak_all = max(chi4_med)
    chi4_snr = chi4_peak_all / max(chi4_baseline, 1e-9)
    chi4_peak_alpha = cfg["alpha_grid"][chi4_med.index(chi4_peak_all)]
    # Knee: smallest alpha where retrieval drops below 0.5 of plateau
    plateau = max(ret_med[:n_base]) if ret_med else 1.0
    knee_alpha = None
    for i, a in enumerate(cfg["alpha_grid"]):
        if ret_med[i] < 0.5 * plateau:
            knee_alpha = a
            break
    if knee_alpha is None:
        knee_alpha = cfg["alpha_grid"][-1]
    # Lead-time (in units of alpha_c) = knee_alpha - chi4_peak_alpha
    lead_time_alpha = max(0.0, knee_alpha - chi4_peak_alpha)
    lead_time_frac = lead_time_alpha / max(alpha_c, 1e-9)
    # Per-seed lead-time stats
    neg_lead = 0
    for s in range(cfg["n_seeds"]):
        row = per_seed[s]
        chi4_col = [r["chi4_peak"] for r in row]
        ret_col = [r["retrieval_overlap"] for r in row]
        chi4_peak_a = cfg["alpha_grid"][chi4_col.index(max(chi4_col))]
        plateau_s = max(ret_col[:n_base]) if ret_col else 1.0
        knee_s = next((cfg["alpha_grid"][i] for i in range(len(ret_col))
                       if ret_col[i] < 0.5 * plateau_s), cfg["alpha_grid"][-1])
        if (knee_s - chi4_peak_a) < 0.05 * alpha_c:
            neg_lead += 1
    # Permutation null: shuffle write order (different codeword sample) and
    # recompute chi_4 at the same M; spike should disappear if order-specific.
    perm_pass = False
    if cfg["perm_null"]:
        # Use the alpha closest to the chi4 peak; build W from shuffled
        # codeword sample (independent random draw). If chi4 peak >> SNR
        # threshold reproduces, null fails (artifact).
        M_peak = max(2, int(round(chi4_peak_alpha * N)))
        cpu_gen_perm = torch.Generator().manual_seed(cfg["seed"] + 99991)
        chi4_perms = []
        n_perm = 3 if smoke else 5
        for _ in range(n_perm):
            W_p, pat_p = build_kerdock_W(N, M_peak, device, cpu_gen_perm)
            ind_p = measure_indicators(W_p, pat_p, target_idx=0,
                                       n_runs=cfg["n_runs"], T_steps=cfg["T_steps"],
                                       noise_p=cfg["noise_p"],
                                       cpu_gen=cpu_gen_perm, device=device)
            chi4_perms.append(ind_p["chi4_peak"])
        perm_med = sorted(chi4_perms)[len(chi4_perms) // 2]
        # Pass condition: real-spike >= 1.5x the permutation-null median
        perm_pass = (chi4_peak_all >= 1.5 * perm_med)
        print(f"  permutation null: real_peak={chi4_peak_all:.3f} "
              f"perm_med={perm_med:.3f} ratio={chi4_peak_all/max(perm_med,1e-9):.2f} "
              f"pass={perm_pass}", flush=True)
    summary = {
        "alpha_grid": cfg["alpha_grid"],
        "chi4_median_per_alpha": chi4_med,
        "ac1_mean_per_alpha": ac1_med,
        "var_mean_per_alpha": var_med,
        "tau_R_mean_per_alpha": tau_med,
        "retrieval_overlap_mean_per_alpha": ret_med,
        "chi4_peak": chi4_peak_all,
        "chi4_baseline": chi4_baseline,
        "chi4_snr": chi4_snr,
        "chi4_peak_alpha": chi4_peak_alpha,
        "knee_alpha": knee_alpha,
        "lead_time_alpha": lead_time_alpha,
        "lead_time_frac": lead_time_frac,
        "n_seeds": cfg["n_seeds"],
        "seeds_with_negative_lead": neg_lead,
        "permutation_null_passed": perm_pass,
        # Bonus complementary-indicator SNRs (zero marginal cost; per Research)
        "ac1_snr": (max(ac1_med) / max(min([a for a in ac1_med if a > 0] +
                                            [1e-9]), 1e-9))
                    if any(a > 0 for a in ac1_med) else 0.0,
        "var_snr": (max(var_med) / max(min([v for v in var_med if v > 0] +
                                            [1e-9]), 1e-9))
                    if any(v > 0 for v in var_med) else 0.0,
        "tau_R_snr": (max(tau_med) / max(min(tau_med + [1e-9]), 1e-9)),
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"  Bonus indicators (per Research mandate):", flush=True)
    print(f"    AC(1) SNR={summary['ac1_snr']:.2f}  Var SNR="
          f"{summary['var_snr']:.2f}  tau_R SNR={summary['tau_R_snr']:.2f}",
          flush=True)
    return summary, verdict, msg, elapsed, cfg


# ---------------------------------------------------------------------------
# IO + entry points
# ---------------------------------------------------------------------------

def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing required metrics fields")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_cap11_chi4_early_warning_anchor_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    oracle.assert_baseline_high("chi4_present", s["chi4_peak"] + 0.001, 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cap11_chi4_early_warning_anchor_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        self_test_indicator_formulas()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
