"""R17 Probe 2 - Substrate codebook Delta_eff scaling dimension.

Sequenced AFTER Probe 1 R17_AREA_LAW_LIKE positive. Tests whether substrate
codebooks (random ±1, Hadamard, Kerdock 4-coset) carry power-law two-point
correlation with Delta_eff > 0.5 — Sang-Hsieh-Zou AQEC enabling condition.

C(r) = mean of |<col_i, col_j>| / M over (i, j) with |i-j| = r
Fit log|C(r)| vs log(r+1); slope = -Delta_eff.

Pre-reg: preregs/2026-05-21_wave14_r17_delta_eff_probe2b.md
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

DELTA_AQEC_THRESHOLD = 0.5
R2_FIT_THRESHOLD = 0.7


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
        return ("DELTA_EFF_INCONCLUSIVE", "Missing by_codebook.")
    well_fit = {ck: data for ck, data in by_ck.items()
                  if data.get("r_squared", 0.0) >= R2_FIT_THRESHOLD}
    aqec_codebooks = [ck for ck, d in well_fit.items() if d["delta_eff"] > DELTA_AQEC_THRESHOLD]
    if len(aqec_codebooks) >= 2:
        deltas = ", ".join(f"{ck}={well_fit[ck]['delta_eff']:.3f}"
                              for ck in aqec_codebooks)
        return ("DELTA_EFF_AQEC_ENABLE",
                f"{len(aqec_codebooks)}/{len(by_ck)} codebooks give "
                f"Delta_eff > {DELTA_AQEC_THRESHOLD} with R^2 > {R2_FIT_THRESHOLD}. "
                f"AQEC noise-tolerance derivation applicable. Codebooks: {deltas}.")
    if well_fit:
        deltas = ", ".join(f"{ck}={d['delta_eff']:.3f}"
                              for ck, d in well_fit.items())
        return ("DELTA_EFF_PRESENT",
                f"Power-law decay present in {len(well_fit)}/{len(by_ck)} codebooks "
                f"but Delta_eff < {DELTA_AQEC_THRESHOLD} (AQEC threshold). "
                f"Codebooks: {deltas}.")
    return ("DELTA_EFF_NO_POWERLAW",
            f"No codebook gives R^2 > {R2_FIT_THRESHOLD}. No power-law two-point "
            f"correlation; substrate has no AQEC analog. by_codebook: " +
            ", ".join(f"{ck}:R^2={d.get('r_squared', 0):.3f}"
                          for ck, d in by_ck.items()))


def self_test_verdict():
    cases = [
        ({"by_codebook": {"random_bsc": {"delta_eff": 0.6, "r_squared": 0.8},
                              "hadamard": {"delta_eff": 0.7, "r_squared": 0.85},
                              "kerdock": {"delta_eff": 0.4, "r_squared": 0.75}}},
         "DELTA_EFF_AQEC_ENABLE"),
        ({"by_codebook": {"random_bsc": {"delta_eff": 0.3, "r_squared": 0.8},
                              "hadamard": {"delta_eff": 0.4, "r_squared": 0.85}}},
         "DELTA_EFF_PRESENT"),
        ({"by_codebook": {"random_bsc": {"delta_eff": 0.6, "r_squared": 0.3},
                              "hadamard": {"delta_eff": 0.5, "r_squared": 0.4}}},
         "DELTA_EFF_NO_POWERLAW"),
        ({}, "DELTA_EFF_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def compute_two_point_correlation(codebook, max_r):
    """C[r] = mean(|sum_mu codebook[mu, i] codebook[mu, j]|) / M over (i, j) with |i-j|=r.
    Equivalent to mean(|G[i, j]|) over (i, j) with |i-j|=r, where G = codebook.T @ codebook.
    """
    M, N = codebook.shape
    G = (codebook.T @ codebook) / M  # (N, N), |G[i,j]| = correlation
    abs_G = G.abs()
    # Diagonal r=0: |G[i,i]| = 1 always; skip.
    rs = list(range(1, min(max_r, N) + 1))
    c_by_r = []
    for r in rs:
        diag = abs_G.diagonal(offset=r)  # all (i, i+r) pairs
        c_by_r.append(float(diag.mean()))
    return rs, c_by_r


def loglog_fit(xs, ys):
    """Linear regression log(y) = -delta * log(x) + b. Return (delta, r_squared)."""
    log_x = [math.log(x) for x in xs]
    log_y = [math.log(max(y, 1e-30)) for y in ys]
    n = len(log_x)
    mx = sum(log_x) / n
    my = sum(log_y) / n
    num = sum((log_x[i] - mx) * (log_y[i] - my) for i in range(n))
    den_x = sum((log_x[i] - mx) ** 2 for i in range(n))
    den_y = sum((log_y[i] - my) ** 2 for i in range(n))
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0, 0.0
    slope = num / den_x
    r_squared = (num * num) / (den_x * den_y)
    delta = -slope  # power-law decay: |C(r)| ~ r^(-delta)
    return delta, r_squared


def run_codebook(codebook_type, N, M_for_codebook, device):
    """Compute Delta_eff for one codebook type."""
    # Use a codebook with at least M = max(N, 2N) rows so correlations are well-defined
    codebook = pv1.make_pool(codebook_type, N, M_for_codebook, seed=17, device=device)
    max_r = N // 2
    rs, c_by_r = compute_two_point_correlation(codebook, max_r)
    # Use r in [1, max_r] for fit
    delta, r2 = loglog_fit(rs, [max(c, 1e-30) for c in c_by_r])
    return {"codebook_type": codebook_type,
             "delta_eff": delta, "r_squared": r2,
             "c_at_r1": c_by_r[0], "c_at_r_max": c_by_r[-1],
             "max_r": max_r}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "M_for_codebook_mult": 2,  # M = 2N for codebook
              "codebook_types": ["random_bsc", "hadamard"] if smoke else
                                  ["random_bsc", "hadamard", "kerdock"]}
    print(f"[config] {config}", flush=True)
    M_for_codebook = config["M_for_codebook_mult"] * config["N"]
    by_ck = {}
    for ck in config["codebook_types"]:
        print(f"[codebook {ck}] N={config['N']} M={M_for_codebook} ...", flush=True)
        r = run_codebook(ck, config["N"], M_for_codebook, device)
        by_ck[ck] = r
        print(f"  delta_eff={r['delta_eff']:.4f} R^2={r['r_squared']:.4f} "
              f"C(r=1)={r['c_at_r1']:.4f} C(r=max)={r['c_at_r_max']:.4f}",
              flush=True)
    summary = {"by_codebook": by_ck}
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
    out_dir = get_output_dir("wave14_r17_delta_eff_probe2b_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["by_codebook"].values())[0]
    oracle.assert_baseline_high("c_at_r1_present", first["c_at_r1"], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_r17_delta_eff_probe2b")
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
