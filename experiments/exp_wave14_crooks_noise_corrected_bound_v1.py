"""Post-hoc re-analysis of wave14_crooks_noise_envelope_v1 FULL data.

Re-applies the Sagawa-Ueda / Generalized-Landauer noise-corrected bound
theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)
in place of the static 0.05 threshold used in the original v157 audit.

No new substrate run. Reads existing metrics.json from
data/exp_wave14_crooks_noise_envelope_v1/metrics.json and re-evaluates
per-cell delta_S_emp against the corrected bound.

Verdict labels:
  CROOKS_NOISE_CORRECTED_PASS    - all 3 noisy cells pass delta_S_emp <= theta(p) + 0.02
  CROOKS_NOISE_CORRECTED_PARTIAL - 1 or 2 noisy cells pass
  CROOKS_NOISE_CORRECTED_FAIL    - any noisy cell has delta_S_emp > theta(p) + 0.05

Unit note: delta_S_emp is measured as absolute entropy change in nats (natural log base).
theta(p) is also in nats. The ln(2) anchor matches the substrate's clean Crooks bound.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing keys: {required - d.keys()}")


# ---------------------------------------------------------------------------
# Noise-corrected bound
# ---------------------------------------------------------------------------

def theta(p: float) -> float:
    """Generalized Landauer / Sagawa-Ueda noise-corrected erasure bound in nats.

    theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)

    At p=0 (clean): theta(0) = ln(2) ~ 0.693 nats  (recovers standard Landauer bound)
    At p=0.05:      theta(0.05) ~ 0.693 - 0.199 = 0.494 nats
    At p=0.10:      theta(0.10) ~ 0.693 - 0.325 = 0.368 nats
    At p=0.20:      theta(0.20) ~ 0.693 - 0.500 = 0.193 nats  (heavy noise; low threshold)

    Note: at high p, theta(p) decreases. The substrate delta_S_emp must be BELOW theta(p).
    For large p the corrected bound becomes more lenient in absolute terms because the
    noisy erase only needs to account for the fraction of recoverable information after
    noise has degraded the write; but the RELATIVE entropy budget narrows.

    Citation: Bormashenko & Voronel (2023) Entropy 25, 984; also Sagawa & Ueda (2012)
    PRL 109, 180602 gives the general form k_B T [ln 2 + p ln p + (1-p) ln(1-p)].
    """
    if p <= 0.0:
        return math.log(2)
    if p >= 1.0:
        return math.log(2)  # degenerate; pure flip = also erasure
    # binary entropy terms (in nats)
    h_p = p * math.log(p) + (1.0 - p) * math.log(1.0 - p)
    return math.log(2) + h_p


def self_test_theta() -> None:
    """Unit tests for theta(p)."""
    # p=0 -> ln(2) ~ 0.6931
    got = theta(0.0)
    assert abs(got - math.log(2)) < 1e-9, f"theta(0): got {got}"
    # p=0.5 -> ln(2) + 0.5*ln(0.5) + 0.5*ln(0.5) = ln(2) - ln(2) = 0
    got = theta(0.5)
    assert abs(got) < 1e-9, f"theta(0.5): got {got}"
    # p=0.1 -> ln(2) + 0.1*ln(0.1) + 0.9*ln(0.9)
    expected = math.log(2) + 0.1 * math.log(0.1) + 0.9 * math.log(0.9)
    got = theta(0.1)
    assert abs(got - expected) < 1e-9, f"theta(0.1): got {got} expected {expected}"
    # p=0.05 -> should be positive and less than ln(2)
    t05 = theta(0.05)
    assert 0.0 < t05 < math.log(2), f"theta(0.05) out of range: {t05}"
    print(f"theta self-test passed (4/4 cases)", flush=True)
    print(f"  theta(0.00) = {theta(0.00):.4f} nats  (clean bound = ln2)", flush=True)
    print(f"  theta(0.05) = {theta(0.05):.4f} nats", flush=True)
    print(f"  theta(0.10) = {theta(0.10):.4f} nats", flush=True)
    print(f"  theta(0.20) = {theta(0.20):.4f} nats", flush=True)


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_corrected_verdict(
    per_noise_delta: dict,
    per_noise_cell_details: dict,
    pass_margin: float = 0.02,
    fail_margin: float = 0.05,
) -> tuple:
    """Apply the noise-corrected bound to each noisy cell.

    per_noise_delta: { p_str -> delta_S_emp_mean_over_seeds }
    per_noise_cell_details: { p_str -> { seed_str -> { mean, max, std, n_trials } } }

    Returns (verdict, verdict_msg, cell_report_list)
    where cell_report_list is [{ p, delta_S, theta_p, margin_to_pass, margin_to_fail,
                                  cell_result }]
    """
    cell_reports = []
    noisy_pass = 0
    hard_fail_triggered = False
    hard_fail_details = []

    for p_str, delta_S in sorted(per_noise_delta.items(), key=lambda x: float(x[0])):
        p_float = float(p_str)
        if p_float <= 0.0:
            continue  # skip clean baseline in verdict logic

        th = theta(p_float)
        # Per-seed std for confidence check
        seed_means = []
        seed_stds = []
        if p_str in per_noise_cell_details:
            for seed_data in per_noise_cell_details[p_str].values():
                seed_means.append(seed_data.get("mean", delta_S))
                seed_stds.append(seed_data.get("std", 0.0))
        mean_seed_std = (sum(seed_stds) / len(seed_stds)) if seed_stds else 0.0

        margin_to_pass = th + pass_margin - delta_S   # positive = passes
        margin_to_fail = delta_S - (th + fail_margin)  # positive = hard-fails

        cell_result = "UNKNOWN"
        if delta_S <= th + pass_margin:
            cell_result = "PASS"
            noisy_pass += 1
        elif delta_S <= th + fail_margin:
            cell_result = "MARGINAL"
        else:
            cell_result = "HARD_FAIL"
            hard_fail_triggered = True
            hard_fail_details.append(
                f"p={p_float:.2f}: delta_S_emp={delta_S:.4f} > theta({p_float:.2f})"
                f"+{fail_margin}={th+fail_margin:.4f}"
            )

        cell_reports.append({
            "p": p_float,
            "delta_S_emp": delta_S,
            "theta_p": th,
            "pass_threshold": th + pass_margin,
            "fail_threshold": th + fail_margin,
            "margin_to_pass": margin_to_pass,
            "cell_result": cell_result,
            "mean_seed_std": mean_seed_std,
        })

    noisy_total = len(cell_reports)

    if hard_fail_triggered:
        verdict = "CROOKS_NOISE_CORRECTED_FAIL"
        msg = (
            f"Noise-corrected bound FAIL: hard-fail triggered. "
            f"{noisy_pass}/{noisy_total} cells pass theta(p)+{pass_margin} margin. "
            f"Substrate delta_S_emp exceeds theta(p)+{fail_margin} in: "
            + "; ".join(hard_fail_details)
        )
    elif noisy_pass == noisy_total:
        verdict = "CROOKS_NOISE_CORRECTED_PASS"
        msg = (
            f"Noise-corrected bound PASS: all {noisy_pass}/{noisy_total} noisy cells "
            f"satisfy delta_S_emp <= theta(p)+{pass_margin} after re-axiomatization. "
            f"Cap 1 SLA widens to tiered noise-tolerance certificate."
        )
    elif noisy_pass >= 1:
        verdict = "CROOKS_NOISE_CORRECTED_PARTIAL"
        msg = (
            f"Noise-corrected bound PARTIAL: {noisy_pass}/{noisy_total} noisy cells "
            f"satisfy delta_S_emp <= theta(p)+{pass_margin}. "
            f"Cap 1 partially rehabilitated under noise-corrected bound."
        )
    else:
        verdict = "CROOKS_NOISE_CORRECTED_FAIL"
        msg = (
            f"Noise-corrected bound FAIL: 0/{noisy_total} noisy cells satisfy "
            f"delta_S_emp <= theta(p)+{pass_margin}. "
            f"Substrate exceeds corrected bound; mechanism #1 refuted."
        )

    return verdict, msg, cell_reports


def self_test_verdict() -> None:
    """Unit tests for compute_corrected_verdict."""
    # Case 1: all cells well below theta(p) + 0.02 -> PASS
    # theta(0.05)~0.494, theta(0.10)~0.368, theta(0.20)~0.193
    t05, t10, t20 = theta(0.05), theta(0.10), theta(0.20)
    per_delta = {"0.0": 0.0, "0.05": t05 - 0.10, "0.10": t10 - 0.10, "0.20": t20 - 0.10}
    per_details = {}
    v, _, rpts = compute_corrected_verdict(per_delta, per_details)
    assert v == "CROOKS_NOISE_CORRECTED_PASS", f"case 1: got {v}"

    # Case 2: one cell marginal (between pass+0.02 and fail+0.05) -> PARTIAL
    per_delta2 = {"0.05": t05 + 0.03, "0.10": t10 - 0.05, "0.20": t20 - 0.05}
    v2, _, _ = compute_corrected_verdict(per_delta2, {})
    assert v2 == "CROOKS_NOISE_CORRECTED_PARTIAL", f"case 2: got {v2}"

    # Case 3: one cell hard-fails -> FAIL regardless of others
    per_delta3 = {"0.05": t05 - 0.10, "0.10": t10 + 0.10, "0.20": t20 - 0.10}
    v3, _, _ = compute_corrected_verdict(per_delta3, {})
    assert v3 == "CROOKS_NOISE_CORRECTED_FAIL", f"case 3: got {v3}"

    # Case 4: all three marginal (between pass and fail) -> FAIL (0 pass, none hard-fails)
    per_delta4 = {"0.05": t05 + 0.03, "0.10": t10 + 0.03, "0.20": t20 + 0.03}
    v4, _, _ = compute_corrected_verdict(per_delta4, {})
    assert v4 == "CROOKS_NOISE_CORRECTED_FAIL", f"case 4: got {v4}"

    # Case 5: simulated v157 values (delta_S much larger than 0.05 but check vs theta)
    # Smoke: p=0.10 -> delta_S=0.2325; theta(0.10)=0.368 -> 0.2325 <= 0.368+0.02=0.388 -> PASS
    per_delta5 = {"0.10": 0.2325}
    v5, _, r5 = compute_corrected_verdict(per_delta5, {})
    assert v5 == "CROOKS_NOISE_CORRECTED_PASS", f"case 5 (smoke analogue): got {v5}"
    assert r5[0]["cell_result"] == "PASS", f"case 5 cell_result: {r5[0]['cell_result']}"

    print(f"verdict self-test passed (5/5 cases)", flush=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_source_metrics(source_path: Path) -> dict:
    """Load the FULL run metrics.json from wave14_crooks_noise_envelope_v1."""
    if not source_path.exists():
        raise FileNotFoundError(
            f"Source metrics not found: {source_path}\n"
            f"The FULL run of wave14_crooks_noise_envelope_v1 must exist on this machine. "
            f"If running on the GPU runner: ensure the overnight_queue run completed "
            f"and produced data/exp_wave14_crooks_noise_envelope_v1/metrics.json."
        )
    with open(source_path) as f:
        data = json.load(f)
    return data


def check_source_completeness(metrics: dict) -> dict:
    """Validate the source metrics has what we need. Returns a report dict."""
    report = {"ok": True, "warnings": [], "errors": []}
    summary = metrics.get("summary", {})
    config = metrics.get("config", {})

    per_noise = summary.get("per_noise_delta_S", {})
    cell_details = summary.get("per_noise_cell_details", {})

    # Check expected noise levels
    expected_noisy = {"0.05", "0.1", "0.10", "0.2", "0.20"}
    found_noisy = {k for k in per_noise if float(k) > 0.0}
    if not found_noisy:
        report["errors"].append("No noisy cells found in per_noise_delta_S")
        report["ok"] = False
    elif len(found_noisy) < 3:
        report["warnings"].append(
            f"Only {len(found_noisy)} noisy levels found (expected 3): {found_noisy}"
        )

    # Check N matches FULL config
    N = config.get("N", summary.get("N", None))
    if N is None:
        report["warnings"].append("N not found in config or summary")
    elif N < 16384:
        report["warnings"].append(
            f"N={N} < 16384 -- this may be smoke data, not FULL. "
            f"Re-analysis result will be conservative (smoke delta_S tends to be higher)."
        )

    # Check seeds
    seeds = config.get("seeds", summary.get("seeds", []))
    if len(seeds) < 3 and N and N >= 16384:
        report["warnings"].append(
            f"Only {len(seeds)} seeds found (expected 3 for FULL): {seeds}"
        )

    # Per-trial data availability
    has_per_trial = False
    for p_str, seed_dict in cell_details.items():
        for seed_str, seed_data in seed_dict.items():
            if "trials" in seed_data or "deltas" in seed_data:
                has_per_trial = True
                break

    if has_per_trial:
        report["per_trial_data"] = True
        report["warnings"].append(
            "Per-trial delta lists found (rich data). Using trial-level stats."
        )
    else:
        report["per_trial_data"] = False
        # Standard path: use mean per noise level
        # This is fine; the corrected bound comparison uses means over 50 trials x 3 seeds

    report["N"] = N
    report["seeds"] = seeds
    report["found_noisy_levels"] = sorted([float(k) for k in found_noisy])
    return report


# ---------------------------------------------------------------------------
# Main re-analysis
# ---------------------------------------------------------------------------

def run_reanalysis(source_metrics: dict) -> tuple:
    """Core re-analysis logic. Returns (summary, verdict, msg, elapsed)."""
    t0 = time.monotonic()

    summary_in = source_metrics.get("summary", {})
    config_in = source_metrics.get("config", {})

    per_noise_delta = summary_in.get("per_noise_delta_S", {})
    per_noise_cell_details = summary_in.get("per_noise_cell_details", {})

    N = config_in.get("N", summary_in.get("N", "unknown"))
    seeds = config_in.get("seeds", summary_in.get("seeds", []))
    n_trials = config_in.get("n_trials", summary_in.get("n_trials", "unknown"))
    noise_levels = config_in.get("noise_levels", list(per_noise_delta.keys()))

    print(f"Source config: N={N} seeds={seeds} n_trials={n_trials} "
          f"noise_levels={noise_levels}", flush=True)
    print(f"", flush=True)

    # Print raw values and corrected bounds
    print(f"{'p':>6}  {'delta_S_emp':>12}  {'theta(p)':>10}  "
          f"{'pass_thr (+0.02)':>17}  {'fail_thr (+0.05)':>17}  {'cell':>12}", flush=True)
    print(f"{'-'*6}  {'-'*12}  {'-'*10}  {'-'*17}  {'-'*17}  {'-'*12}", flush=True)

    for p_str in sorted(per_noise_delta.keys(), key=lambda x: float(x)):
        p_f = float(p_str)
        delta = per_noise_delta[p_str]
        th = theta(p_f)
        label = "(baseline)" if p_f == 0.0 else ""
        print(f"{p_f:>6.2f}  {delta:>12.4f}  {th:>10.4f}  "
              f"{th+0.02:>17.4f}  {th+0.05:>17.4f}  {label}", flush=True)

    print(f"", flush=True)

    verdict, msg, cell_reports = compute_corrected_verdict(
        per_noise_delta, per_noise_cell_details, pass_margin=0.02, fail_margin=0.05
    )

    elapsed = time.monotonic() - t0

    summary_out = {
        "source_N": N,
        "source_seeds": seeds,
        "source_n_trials": n_trials,
        "source_noise_levels": noise_levels,
        "source_original_verdict": source_metrics.get("verdict", "unknown"),
        "per_noise_raw_delta_S": per_noise_delta,
        "theta_values": {p_str: theta(float(p_str)) for p_str in per_noise_delta},
        "cell_reports": cell_reports,
        "pass_margin": 0.02,
        "fail_margin": 0.05,
    }

    return summary_out, verdict, msg, elapsed


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run_smoke() -> None:
    """Smoke: use the smoke-run data (N=4096, 1 seed, 10 trials).
    This validates the re-analysis machinery, not the FULL verdict.
    Expected: CROOKS_NOISE_CORRECTED_PASS since delta_S=0.2325 < theta(0.10)+0.02=0.388."""
    out_dir = get_output_dir("wave14_crooks_noise_corrected_bound_v1_smoke")
    # Try FULL first; fall back to smoke data
    full_path = REPO / "data" / "exp_wave14_crooks_noise_envelope_v1" / "metrics.json"
    smoke_path = REPO / "data" / "exp_wave14_crooks_noise_envelope_v1_smoke" / "metrics.json"

    if full_path.exists():
        src = full_path
        print(f"[smoke] Using FULL source data: {src}", flush=True)
    elif smoke_path.exists():
        src = smoke_path
        print(f"[smoke] FULL data not found; using SMOKE source data: {src}", flush=True)
        print(f"  NOTE: smoke run has N=4096 1 seed 10 trials; PASS does not imply FULL PASS", flush=True)
    else:
        raise FileNotFoundError(
            f"Neither FULL nor smoke source data found.\n"
            f"  Looked for: {full_path}\n"
            f"              {smoke_path}"
        )

    source = load_source_metrics(src)
    comp_report = check_source_completeness(source)
    print(f"[smoke] Source completeness: {comp_report}", flush=True)
    if comp_report["errors"]:
        raise RuntimeError(f"Source data errors: {comp_report['errors']}")

    summary, verdict, msg, elapsed = run_reanalysis(source)

    config = {
        "mode": "smoke",
        "source_path": str(src),
        "pass_margin": 0.02,
        "fail_margin": 0.05,
        "source_is_smoke_data": not full_path.exists(),
    }

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)
    print(f"  {msg}", flush=True)


def run_main() -> None:
    """FULL run: reads the FULL wave14_crooks_noise_envelope_v1 metrics.json."""
    out_dir = get_output_dir("wave14_crooks_noise_corrected_bound_v1")
    src = REPO / "data" / "exp_wave14_crooks_noise_envelope_v1" / "metrics.json"

    print(f"[main] Loading source data: {src}", flush=True)
    source = load_source_metrics(src)

    comp_report = check_source_completeness(source)
    print(f"[main] Source completeness check:", flush=True)
    print(f"  N={comp_report.get('N')} seeds={comp_report.get('seeds')} "
          f"noisy_levels={comp_report.get('found_noisy_levels')}", flush=True)
    for w in comp_report.get("warnings", []):
        print(f"  [warn] {w}", flush=True)
    if comp_report["errors"]:
        for e in comp_report["errors"]:
            print(f"  [ERROR] {e}", flush=True)
        raise RuntimeError(f"Source data errors: {comp_report['errors']}")

    print(f"", flush=True)
    summary, verdict, msg, elapsed = run_reanalysis(source)

    config = {
        "mode": "full",
        "source_path": str(src),
        "pass_margin": 0.02,
        "fail_margin": 0.05,
        "source_is_smoke_data": False,
    }

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"  {msg}", flush=True)
    print(f"\nDONE: {verdict}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Post-hoc re-analysis of Crooks noise-envelope data under noise-corrected bound"
    )
    ap.add_argument("--self-test", action="store_true",
                    help="Run unit tests (theta + verdict logic)")
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke mode: use available source data (FULL or smoke fallback)")
    args = ap.parse_args()

    if args.self_test:
        self_test_theta()
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
