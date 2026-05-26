"""Calibration of substrate fact-retrieval: does max softmax track accuracy?

Test of cap_map Tier-3 KILLER 'Calibration / uncertainty'. wave14calibration_v2
tested bundle-side soft-vs-clip (different question, got CAL_NO_GAIN). This
tests fact-retrieval cleanup confidence vs correctness.

Build M facts with Kerdock keys. For each fact, probe with exact key and
multiple Hamming paraphrases. Compute (max_softmax, correct) pairs across
all probes. Report ECE (10-bin), Brier score, top-bin accuracy.

Pre-reg: preregs/2026-05-21_wave14yd_calibration_fact_retrieval.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec1 = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(v1)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 4096
M_STORED_SMOKE = 256
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
HAMMING_RADII_FULL = [0, 4, 8, 16]  # 0 = exact key
HAMMING_RADII_SMOKE = [0, 8]
BETA = 8.0  # matches substrate's operating value (wave14d_icl_via_pool, etc.)
N_BINS = 10

ECE_THRESHOLD_WELL = 0.05
ECE_THRESHOLD_MARGINAL = 0.15
TOP_BIN_ACC_THRESHOLD = 0.95


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_ece(confidences: list[float], correct: list[bool],
                  n_bins: int = N_BINS) -> tuple[float, list[dict]]:
    """Compute Expected Calibration Error with equal-width bins on [0, 1].
    Returns (ECE, per_bin_details).
    """
    total = len(confidences)
    bin_edges = [i / n_bins for i in range(n_bins + 1)]
    bins = []
    ece = 0.0
    for b in range(n_bins):
        lo, hi = bin_edges[b], bin_edges[b + 1]
        if b == n_bins - 1:
            in_bin = [i for i, c in enumerate(confidences) if lo <= c <= hi]
        else:
            in_bin = [i for i, c in enumerate(confidences) if lo <= c < hi]
        n_in = len(in_bin)
        if n_in == 0:
            bins.append({"lo": lo, "hi": hi, "n": 0, "mean_conf": None, "accuracy": None})
            continue
        mean_conf = sum(confidences[i] for i in in_bin) / n_in
        accuracy = sum(1 for i in in_bin if correct[i]) / n_in
        bins.append({"lo": lo, "hi": hi, "n": n_in,
                       "mean_conf": mean_conf, "accuracy": accuracy})
        ece += abs(mean_conf - accuracy) * (n_in / total)
    return ece, bins


def compute_verdict(summary: dict) -> tuple[str, str]:
    metrics = summary.get("metrics")
    if not metrics:
        return ("CALIBRATION_INCONCLUSIVE", "Missing calibration metrics.")
    ece = metrics.get("ece")
    top_bin_acc = metrics.get("top_bin_accuracy")
    brier = metrics.get("brier")
    bins = summary.get("bins", [])
    overall_acc = metrics.get("overall_accuracy", 0.0)

    if ece is None:
        return ("CALIBRATION_INCONCLUSIVE", "ECE not computed.")

    # Inversion check: is high-confidence less accurate than low-confidence?
    valid_bins = [b for b in bins if b["n"] > 0 and b["mean_conf"] is not None]
    if len(valid_bins) >= 4:
        # Check slope of accuracy vs mean_conf across bins
        confs = [b["mean_conf"] for b in valid_bins]
        accs = [b["accuracy"] for b in valid_bins]
        n = len(confs)
        mean_c = sum(confs) / n
        mean_a = sum(accs) / n
        num = sum((confs[i] - mean_c) * (accs[i] - mean_a) for i in range(n))
        den = sum((confs[i] - mean_c) ** 2 for i in range(n))
        slope = num / den if abs(den) > 1e-12 else 0.0
        if slope < -0.1:
            return ("CALIBRATION_INVERTED",
                    f"Accuracy slope vs confidence = {slope:+.3f} < -0.1. "
                    f"High-confidence predictions are LESS accurate than low-confidence. "
                    f"ECE={ece:.4f}, Brier={brier:.4f}. Audit substrate behavior.")

    if ece < ECE_THRESHOLD_WELL and top_bin_acc is not None and top_bin_acc >= TOP_BIN_ACC_THRESHOLD:
        return ("CALIBRATION_WELL",
                f"ECE={ece:.4f} < {ECE_THRESHOLD_WELL}; top-bin accuracy="
                f"{top_bin_acc:.3f} >= {TOP_BIN_ACC_THRESHOLD}. Substrate confidence "
                f"reliably tracks accuracy. Brier={brier:.4f}, overall_acc={overall_acc:.3f}.")

    if ece < ECE_THRESHOLD_MARGINAL:
        return ("CALIBRATION_MARGINAL",
                f"ECE={ece:.4f} in [{ECE_THRESHOLD_WELL}, {ECE_THRESHOLD_MARGINAL}). "
                f"Confidence somewhat tracks accuracy but with measurable miscalibration. "
                f"top_bin_acc={top_bin_acc}, Brier={brier:.4f}.")

    return ("CALIBRATION_POOR",
            f"ECE={ece:.4f} >= {ECE_THRESHOLD_MARGINAL}. Substrate confidence does not "
            f"reliably indicate accuracy. Post-hoc calibration needed before shipping. "
            f"top_bin_acc={top_bin_acc}, Brier={brier:.4f}.")


def self_test_verdict() -> None:
    def mk(ece, top_bin_acc, brier=0.1, overall_acc=0.8, bins=None):
        return {"metrics": {"ece": ece, "top_bin_accuracy": top_bin_acc,
                              "brier": brier, "overall_accuracy": overall_acc},
                "bins": bins or [{"n": 10, "mean_conf": 0.5, "accuracy": 0.5, "lo": 0.4, "hi": 0.6}] * 5}

    cases = [
        # 1. WELL: ECE 0.02, top_bin 0.98
        (mk(0.02, 0.98), "CALIBRATION_WELL"),
        # 2. MARGINAL: ECE 0.08
        (mk(0.08, 0.90), "CALIBRATION_MARGINAL"),
        # 3. POOR: ECE 0.25
        (mk(0.25, 0.70), "CALIBRATION_POOR"),
        # 4. INVERTED: slope test fires. Mock bins with decreasing accuracy
        (mk(0.20, 0.30, bins=[
            {"n": 100, "mean_conf": 0.2, "accuracy": 0.8, "lo": 0.1, "hi": 0.3},
            {"n": 100, "mean_conf": 0.4, "accuracy": 0.6, "lo": 0.3, "hi": 0.5},
            {"n": 100, "mean_conf": 0.6, "accuracy": 0.4, "lo": 0.5, "hi": 0.7},
            {"n": 100, "mean_conf": 0.8, "accuracy": 0.2, "lo": 0.7, "hi": 0.9},
        ]), "CALIBRATION_INVERTED"),
        # 5. INCONCLUSIVE: empty
        ({}, "CALIBRATION_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_calibration(N: int, M: int, codebook: torch.Tensor, hamming_radii: list,
                       seeds: list, device: torch.device) -> tuple[list[float], list[bool], dict]:
    """Run the calibration experiment. Returns (confidences, correct, summary_dict)."""
    all_confs = []
    all_correct = []
    all_probs_per_pred = []  # probability assigned to true label (for Brier)

    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)

        keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
        values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (values.T @ keys) / N

        for h in hamming_radii:
            if h == 0:
                probe_keys = keys
            else:
                probe_keys = v1.hamming_perturb(keys, 1, h, cpu_gen, device)

            retrieved = probe_keys @ W.T  # (M, N)
            sims = retrieved @ values.T / N  # (M, M) similarities
            # softmax over value dimension
            scaled_sims = sims * BETA
            # Normalize for numerical stability
            scaled_sims = scaled_sims - scaled_sims.max(dim=1, keepdim=True).values
            exp_sims = torch.exp(scaled_sims)
            probs = exp_sims / exp_sims.sum(dim=1, keepdim=True)  # (M, M)

            max_probs = probs.max(dim=1).values  # (M,)
            argmax_idx = probs.argmax(dim=1)  # (M,)
            target = torch.arange(M, device=device)
            correct = (argmax_idx == target)
            # Probability assigned to true index
            true_probs = probs.gather(1, target.unsqueeze(1)).squeeze(1)

            all_confs.extend(max_probs.tolist())
            all_correct.extend(correct.tolist())
            all_probs_per_pred.extend(true_probs.tolist())

    # Compute metrics
    overall_acc = sum(1 for c in all_correct if c) / len(all_correct)
    ece, bins = compute_ece(all_confs, all_correct, n_bins=N_BINS)

    # Top-bin accuracy: predictions with confidence > 0.9
    top_bin = [(c, k) for c, k in zip(all_confs, all_correct) if c > 0.9]
    top_bin_acc = (sum(1 for c, k in top_bin if k) / len(top_bin)) if top_bin else None

    # Brier score: mean (prob_at_true - 1)^2 + sum over others of prob_other^2 -- but
    # simpler: 1-prob_at_true is the "loss" for one-hot label
    brier = sum((1.0 - p) ** 2 for p in all_probs_per_pred) / len(all_probs_per_pred)

    metrics = {
        "ece": ece,
        "brier": brier,
        "top_bin_accuracy": top_bin_acc,
        "overall_accuracy": overall_acc,
        "n_probes": len(all_confs),
    }
    return all_confs, all_correct, {"metrics": metrics, "bins": bins}


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
        "beta": BETA,
        "n_bins": N_BINS,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building 4-coset Kerdock at N={config['N']}...", flush=True)
    codebook, info = v3.make_kerdock_4coset_codebook(config["N"], device)
    print(f"[codebook] {info}", flush=True)

    confs, correct, summary = run_calibration(
        config["N"], config["M_stored"], codebook, config["hamming_radii"],
        config["seeds"], device)
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= CALIBRATION =========", flush=True)
    m = summary["metrics"]
    print(f"  n_probes={m['n_probes']}  overall_acc={m['overall_accuracy']:.3f}",
          flush=True)
    print(f"  ECE={m['ece']:.4f}  Brier={m['brier']:.4f}  "
          f"top_bin_acc={m['top_bin_accuracy']}", flush=True)
    print(f"  Per-bin details:", flush=True)
    for b in summary["bins"]:
        if b["n"] == 0:
            continue
        print(f"    [{b['lo']:.2f}, {b['hi']:.2f}]  n={b['n']:5d}  "
              f"mean_conf={b['mean_conf']:.4f}  acc={b['accuracy']:.4f}",
              flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14yd_calibration_fact_retrieval_smoke")
    log_event("experiment_started", name="wave14yd_calibration_fact_retrieval", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle 1: substrate actually stores facts (mean accuracy > 0.50 at smoke)
    overall_acc = float(summary["metrics"]["overall_accuracy"])
    oracle.assert_baseline_high("calibration_smoke_accuracy", overall_acc, 0.50)

    # Oracle 2: confidence distribution spans meaningful range
    valid_bins = [b for b in summary["bins"] if b["n"] > 0]
    if len(valid_bins) < 2:
        raise AssertionError(
            f"SANITY FAIL [conf_range]: only {len(valid_bins)} nonempty bins. "
            f"Confidence distribution too narrow for meaningful calibration.")

    # Oracle 3: ECE in [0, 1]
    ece = float(summary["metrics"]["ece"])
    oracle.assert_in_range("calibration_smoke_ece", ece, (0.0, 1.0))

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yd_calibration_fact_retrieval",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yd_calibration_fact_retrieval")
    log_event("experiment_started", name="wave14yd_calibration_fact_retrieval", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yd_calibration_fact_retrieval",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
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
