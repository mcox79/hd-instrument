"""Substrate observability suite v1 — C_ij eigvals + P(h) moments (Family I + II).

Per Strategy 2026-05-22 14:25 EDT request. Top 3 probes for spin-glass diagnostics:
  Priority 1: C_ij time-average correlation eigvalsh (Sinova-Houdayer-Martin)
  Priority 3: P(h) local-field histogram moments (Mezard 0711.3934)
  (Priority 2: P(q) replica overlap requires PT MC; deferred to v2)

Setup: load M = alpha*N random bipolar patterns into W (Hebbian); run Glauber
MC at low temperature; sample configurations every 100 steps.

Verdict (cross-family agreement = certification):
  OBS_SUITE_RSB_CERTIFIED: C_ij RSB AND P(h) FROZEN/BIMODAL agree
  OBS_SUITE_RS_CERTIFIED:  C_ij RS  AND P(h) PARAMAGNETIC agree
  OBS_SUITE_AMBIGUOUS:     disagreement OR marginal counts

Pre-reg: preregs/2026-05-22_wave14_observability_suite_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "cij_verdict" not in summary or "ph_verdict" not in summary:
        return ("OBS_SUITE_INCONCLUSIVE", "Missing probe verdict.")
    c = summary["cij_verdict"]; p = summary["ph_verdict"]
    cij_excess = summary["cij_excess_eigvals"]
    bimodal = summary["ph_bimodal"]
    wipeout = summary["ph_wipeout_fraction"]
    if c == "OBS_CIJ_RSB" and p == "OBS_PH_FROZEN":
        return ("OBS_SUITE_RSB_CERTIFIED",
                f"Cross-family RSB certification: C_ij excess eigvals={cij_excess} "
                f"(>1=RSB), P(h) bimodal={bimodal} wipeout={wipeout:.3f}. "
                f"Substrate confirmed in RSB phase.")
    if c == "OBS_CIJ_RS" and p == "OBS_PH_PARAMAGNETIC":
        return ("OBS_SUITE_RS_CERTIFIED",
                f"Cross-family RS certification: C_ij excess eigvals={cij_excess} (<=1), "
                f"P(h) unimodal narrow wipeout={wipeout:.3f}. "
                f"Substrate confirmed in RS / paramagnet phase.")
    return ("OBS_SUITE_AMBIGUOUS",
            f"Probe disagreement or marginal: cij={c} (excess={cij_excess}), "
            f"ph={p} (bimodal={bimodal} wipeout={wipeout:.3f}). "
            f"Need more probes or longer MC chain.")


def self_test_verdict():
    cases = [
        ({"cij_verdict": "OBS_CIJ_RSB", "ph_verdict": "OBS_PH_FROZEN",
          "cij_excess_eigvals": 5, "ph_bimodal": True, "ph_wipeout_fraction": 0.45},
         "OBS_SUITE_RSB_CERTIFIED"),
        ({"cij_verdict": "OBS_CIJ_RS", "ph_verdict": "OBS_PH_PARAMAGNETIC",
          "cij_excess_eigvals": 1, "ph_bimodal": False, "ph_wipeout_fraction": 0.05},
         "OBS_SUITE_RS_CERTIFIED"),
        ({"cij_verdict": "OBS_CIJ_RSB", "ph_verdict": "OBS_PH_PARAMAGNETIC",
          "cij_excess_eigvals": 3, "ph_bimodal": False, "ph_wipeout_fraction": 0.10},
         "OBS_SUITE_AMBIGUOUS"),
        ({}, "OBS_SUITE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_hopfield_W(M, N, cpu_gen, device):
    bits = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device)
    patterns = 2.0 * bits.float() - 1.0
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    return W, patterns


def glauber_step(s, W, beta, cpu_gen, device):
    """One full sweep: each spin updated in turn via Glauber rule."""
    N = s.shape[0]
    order = torch.randperm(N, generator=cpu_gen).to(device)
    us = torch.rand(N, generator=cpu_gen).to(device)
    for k, idx in enumerate(order):
        h_i = float(W[idx] @ s)
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[idx] = 1.0 if float(us[k]) < p_plus else -1.0
    return s


def run_mc_chain(W, N, beta, n_burn, n_sample, sample_interval, cpu_gen, device):
    init_bits = (torch.rand(N, generator=cpu_gen) > 0.5).to(device)
    s = (2.0 * init_bits.float() - 1.0)
    for _ in range(n_burn):
        s = glauber_step(s, W, beta, cpu_gen, device)
    samples = []
    for k in range(n_sample * sample_interval):
        s = glauber_step(s, W, beta, cpu_gen, device)
        if (k + 1) % sample_interval == 0:
            samples.append(s.clone())
    return torch.stack(samples, dim=0)  # (n_sample, N)


def probe_cij(samples, W, threshold_rel=0.1):
    """Compute C_ij = <s_i s_j> - <s_i><s_j>; count eigvals with lam/N > threshold."""
    N = samples.shape[1]
    mean_s = samples.mean(dim=0)
    C = (samples.T @ samples) / samples.shape[0] - torch.outer(mean_s, mean_s)
    eigvals_C = torch.linalg.eigvalsh(C.float()).cpu().numpy()
    eigvals_W = torch.linalg.eigvalsh(W.float()).cpu().numpy()
    n_extensive_C = int(((eigvals_C / N) > threshold_rel).sum())
    n_extensive_W = int(((eigvals_W / N) > threshold_rel).sum())
    excess = n_extensive_C - n_extensive_W
    verdict = "OBS_CIJ_RSB" if excess > 1 else ("OBS_CIJ_RS" if excess == 1 else "OBS_CIJ_AMBIGUOUS")
    if excess == 0:
        verdict = "OBS_CIJ_RS"
    elif excess == 1:
        verdict = "OBS_CIJ_RS"
    return verdict, excess, n_extensive_C, n_extensive_W


def probe_ph(samples, W):
    """Compute h_i = W s; aggregate; fit unimodal vs bimodal; wipeout fraction."""
    h_flat = []
    for s in samples:
        h = W @ s
        h_flat.append(h)
    h_all = torch.cat(h_flat, dim=0).float()
    sigma = float(h_all.std())
    mean = float(h_all.mean())
    skew = float(((h_all - mean) ** 3).mean() / max(sigma ** 3, 1e-9))
    kurt = float(((h_all - mean) ** 4).mean() / max(sigma ** 4, 1e-9))
    # Bimodality coefficient (SAS): b = (skew^2 + 1) / (kurt + 3*(n-1)^2 / ((n-2)*(n-3)))
    # For large n simplifies to b = (skew^2 + 1) / kurt; b > 5/9 ~= 0.555 = bimodal
    b = (skew * skew + 1.0) / max(kurt, 1e-9)
    bimodal = bool(b > 0.555)
    wipeout = float((h_all.abs() > 2.0 * sigma).float().mean())
    if bimodal:
        verdict = "OBS_PH_FROZEN"
    elif wipeout < 0.10:
        verdict = "OBS_PH_PARAMAGNETIC"
    else:
        verdict = "OBS_PH_INTERMEDIATE"
    return verdict, bimodal, wipeout, sigma, mean, skew, kurt, b


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 4096,
              "alpha": 0.15,
              "beta": 2.0,
              "n_burn": 20 if smoke else 200,
              "n_sample": 50 if smoke else 500,
              "sample_interval": 5 if smoke else 50,
              "seed": 17,
              "cij_threshold_rel": 0.1}
    N = config["N"]
    M = int(config["alpha"] * N)
    print(f"[config] N={N} M={M} alpha={config['alpha']} beta={config['beta']}", flush=True)
    cpu_gen = torch.Generator().manual_seed(config["seed"] + 1009)
    W, patterns = build_hopfield_W(M, N, cpu_gen, device)
    print(f"[MC] burn={config['n_burn']} sweeps; sampling {config['n_sample']} configs every {config['sample_interval']} sweeps", flush=True)
    samples = run_mc_chain(W, N, config["beta"], config["n_burn"],
                              config["n_sample"], config["sample_interval"],
                              cpu_gen, device)
    print(f"[MC] collected {samples.shape[0]} samples", flush=True)
    print("[probe C_ij]", flush=True)
    cij_verdict, excess, n_cij, n_W = probe_cij(samples, W, config["cij_threshold_rel"])
    print(f"  C_ij eigvals (lam/N > 0.1): {n_cij}, W eigvals: {n_W}, excess: {excess} -> {cij_verdict}", flush=True)
    print("[probe P(h)]", flush=True)
    ph_verdict, bimodal, wipeout, sigma, mean_h, skew, kurt, b_coef = probe_ph(samples, W)
    print(f"  P(h): sigma={sigma:.3f} skew={skew:.3f} kurt={kurt:.3f} b={b_coef:.3f} "
          f"bimodal={bimodal} wipeout={wipeout:.3f} -> {ph_verdict}", flush=True)
    summary = {"cij_verdict": cij_verdict,
                "cij_excess_eigvals": excess,
                "cij_n_extensive": n_cij,
                "cij_W_n_extensive": n_W,
                "ph_verdict": ph_verdict,
                "ph_bimodal": bimodal,
                "ph_wipeout_fraction": wipeout,
                "ph_sigma": sigma,
                "ph_skew": skew,
                "ph_kurtosis": kurt,
                "ph_bimodality_coef": b_coef,
                "n_samples": samples.shape[0]}
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
    out_dir = get_output_dir("wave14_observability_suite_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("samples_collected", float(summary["n_samples"]), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_observability_suite_v1")
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
