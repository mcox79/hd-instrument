"""Proper calibration test for soft trace - per research agent recipe.

Replaces wave14soft_trace's INCONCLUSIVE ECE result. The agent's prescription:
1. Use un-clipped soft trace (sign-clip destroys Gaussian crosstalk model)
2. Posterior = softmax(N * cosine_k / sigma_sq) with sigma_sq = M-1 (analytic)
3. Adaptive (quantile) binning, NOT equal-width
4. >= 2000 probes
5. Report panel: Brier (primary), adaptive ECE, AURC, AUROC of p_top for OOD

Source: Plate 1995 HRR cleanup; Frady-Sommer 2020 resonator; Guo 2017 temp scaling;
Nixon 2019 adaptive binning; Blasiok-Nakkiran 2024 SmoothECE.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_M", [])
    if not rows:
        return ("CAL_INCONCLUSIVE", "No data.")
    # Compare soft vs clipped Brier scores
    soft_briers = [r["brier_soft"] for r in rows]
    clip_briers = [r["brier_clip"] for r in rows]
    soft_mean = sum(soft_briers) / len(soft_briers)
    clip_mean = sum(clip_briers) / len(clip_briers)
    soft_ece = sum(r["adaptive_ece_soft"] for r in rows) / len(rows)
    clip_ece = sum(r["adaptive_ece_clip"] for r in rows) / len(rows)
    if soft_brier_advantage := (clip_mean - soft_mean) > 0.02:
        soft_brier_advantage = True
    if soft_ece_advantage := (clip_ece - soft_ece) > 0.02:
        soft_ece_advantage = True
    if soft_brier_advantage and soft_ece_advantage:
        return ("CAL_SOFT_WINS_CLEAR",
                f"Brier soft={soft_mean:.3f} < clip={clip_mean:.3f}. "
                f"ECE soft={soft_ece:.3f} < clip={clip_ece:.3f}. "
                f"Un-clipped trace gives calibrated Bayesian uncertainty from the algebra.")
    if soft_brier_advantage or soft_ece_advantage:
        return ("CAL_SOFT_PARTIAL",
                f"Soft wins one axis. Brier: soft={soft_mean:.3f} vs clip={clip_mean:.3f}. "
                f"ECE: soft={soft_ece:.3f} vs clip={clip_ece:.3f}.")
    return ("CAL_NO_GAIN",
            f"Soft and clip indistinguishable. Brier soft={soft_mean:.3f} clip={clip_mean:.3f}.")


def self_test_verdict() -> None:
    cases = [
        ({"per_M": [{"brier_soft": 0.10, "brier_clip": 0.25, "adaptive_ece_soft": 0.02,
                     "adaptive_ece_clip": 0.15}]}, "CAL_SOFT_WINS_CLEAR"),
        ({"per_M": [{"brier_soft": 0.10, "brier_clip": 0.25, "adaptive_ece_soft": 0.05,
                     "adaptive_ece_clip": 0.05}]}, "CAL_SOFT_PARTIAL"),
        ({"per_M": [{"brier_soft": 0.10, "brier_clip": 0.10, "adaptive_ece_soft": 0.05,
                     "adaptive_ece_clip": 0.05}]}, "CAL_NO_GAIN"),
        ({"per_M": []}, "CAL_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen):
    return 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0


def adaptive_ece(probs, correct, n_bins=15):
    """Quantile-binning ECE per Nixon 2019."""
    n = len(probs)
    if n == 0:
        return 0.0
    # Quantile bin edges
    sorted_idx = torch.argsort(probs)
    bin_size = n // n_bins
    ece = 0.0
    for b in range(n_bins):
        lo = b * bin_size
        hi = (b + 1) * bin_size if b < n_bins - 1 else n
        if hi - lo == 0:
            continue
        bin_idx = sorted_idx[lo:hi]
        bin_p = probs[bin_idx].mean().item()
        bin_acc = correct[bin_idx].float().mean().item()
        weight = (hi - lo) / n
        ece += weight * abs(bin_acc - bin_p)
    return ece


def brier_score(probs, correct):
    return ((probs - correct.float()) ** 2).mean().item()


def run_one_M(N, M_load, n_probes, codebook_size, seed, device):
    """For bundle load M, generate n_probes (item, cue) pairs, build bundle,
    measure calibration of soft vs clipped retrieval.
    """
    gen = torch.Generator().manual_seed(seed)
    codebook = make_bipolar((codebook_size, N), gen).to(device)
    # Sample M items from codebook
    item_idxs = torch.randperm(codebook_size, generator=gen)[:M_load].tolist()
    items = codebook[item_idxs]  # (M, N) - the stored values
    cues = make_bipolar((M_load, N), gen).to(device)
    bound = items * cues
    bundle_soft = bound.sum(dim=0)  # soft trace (Z-valued)
    bundle_clip = torch.sign(bundle_soft + 1e-9)

    # For n_probes random items from stored, predict via soft and clip
    probe_gen = torch.Generator().manual_seed(seed * 11 + M_load)
    sigma_sq = max(1.0, M_load - 1)  # per-coordinate noise variance
    probe_results = {"soft": [], "clip": [], "true_idx": []}
    for _ in range(n_probes):
        i = int(torch.randint(0, M_load, (1,), generator=probe_gen).item())
        c_i = cues[i]
        # Soft retrieval
        r_soft = bundle_soft * c_i
        # Cosine to all codebook items
        sims_soft = (codebook @ r_soft) / (codebook.norm(dim=1) * r_soft.norm() + 1e-9)
        # Posterior = softmax(N * sims / sigma_sq)
        logits_soft = N * sims_soft / sigma_sq
        posterior_soft = torch.softmax(logits_soft, dim=0)
        # Clipped retrieval
        r_clip = bundle_clip * c_i
        sims_clip = (codebook @ r_clip) / (codebook.norm(dim=1) * r_clip.norm() + 1e-9)
        logits_clip = N * sims_clip / sigma_sq
        posterior_clip = torch.softmax(logits_clip, dim=0)
        true_idx = item_idxs[i]
        probe_results["soft"].append((posterior_soft.argmax().item(),
                                       posterior_soft.max().item(),
                                       true_idx == posterior_soft.argmax().item()))
        probe_results["clip"].append((posterior_clip.argmax().item(),
                                       posterior_clip.max().item(),
                                       true_idx == posterior_clip.argmax().item()))
        probe_results["true_idx"].append(true_idx)

    # Compute metrics
    def metrics_for(method):
        confidences = torch.tensor([r[1] for r in probe_results[method]])
        correctness = torch.tensor([r[2] for r in probe_results[method]], dtype=torch.float)
        ece = adaptive_ece(confidences, correctness, n_bins=10)
        brier = brier_score(confidences, correctness)
        accuracy = correctness.mean().item()
        mean_conf = confidences.mean().item()
        return ece, brier, accuracy, mean_conf

    ece_s, brier_s, acc_s, conf_s = metrics_for("soft")
    ece_c, brier_c, acc_c, conf_c = metrics_for("clip")
    return {"M": M_load, "n_probes": n_probes,
            "adaptive_ece_soft": ece_s, "brier_soft": brier_s,
            "acc_soft": acc_s, "mean_conf_soft": conf_s,
            "adaptive_ece_clip": ece_c, "brier_clip": brier_c,
            "acc_clip": acc_c, "mean_conf_clip": conf_c,
            "sigma_sq_used": sigma_sq}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "codebook_size": 1024,
                  "M_list": [50, 200], "n_probes": 200, "seeds": [17]}
    else:
        # Substantial: sweep M, many probes per cell
        config = {"mode": "full", "N": 4096, "codebook_size": 4096,
                  "M_list": [100, 300, 627, 1000, 2000, 3000],
                  "n_probes": 2000, "seeds": [17, 23, 31]}
    print(f"wave14calibration_v2. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    per_M = []
    for M_load in config["M_list"]:
        rows = []
        for seed in config["seeds"]:
            r = run_one_M(config["N"], M_load, config["n_probes"],
                          config["codebook_size"], seed, device)
            rows.append(r)
        agg = {k: sum(r[k] for r in rows) / len(rows)
               for k in ["adaptive_ece_soft", "brier_soft", "acc_soft", "mean_conf_soft",
                          "adaptive_ece_clip", "brier_clip", "acc_clip", "mean_conf_clip"]}
        agg["M"] = M_load
        agg["n_probes_total"] = config["n_probes"] * len(config["seeds"])
        per_M.append(agg)
        print(f"  M={M_load:5d}  soft: ECE={agg['adaptive_ece_soft']:.3f} "
              f"Brier={agg['brier_soft']:.3f} acc={agg['acc_soft']:.2%}  "
              f"clip: ECE={agg['adaptive_ece_clip']:.3f} Brier={agg['brier_clip']:.3f} "
              f"acc={agg['acc_clip']:.2%}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_M": per_M}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_M": per_M, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14calibration_v2")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
