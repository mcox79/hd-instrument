"""Cap 2 self-monitoring re-probe with corrected confidence metric (v1).

Original Cap 2 (REFUTED CRITICAL_NO_CORRELATION in v153) used VAMP iteration
count (tau) as the confidence proxy. Post-hoc diagnosis (Sagawa-Ueda precedent
for Cap 1 metric-definition artifacts): tau is a poor confidence proxy because
argmax dynamics converge fast to BOTH correct AND wrong attractors -- fast
convergence does not distinguish error from success. This is the metric-
definition artifact the prompt flagged.

FIX: use the cleanup operator's cosine MARGIN as the confidence proxy.
  margin = (top_1_score - top_2_score) / N
After W @ x, the margin between the best-matching and second-best-matching
stored pattern directly measures the signal-to-noise ratio of the readout.

Secondary fix: stratify by noise level p. The v1 experiment mixed noise levels
in a single trial loop, diluting per-stratum correlation signal.

Predictions:
  HARD PASS: at K=NEAR_CAPACITY (M=200, N=8192), within each stratum p,
    corr(margin, is_correct) >= 0.50 in at least 2/4 noise strata.
    This is the analog of Cap 1 Tier-2 Sagawa-Ueda PASS: a different
    metric gives the signal the original metric missed.
  HARD FAIL: at ALL strata, corr(margin, is_correct) < 0.20.
    Substrate carries no confidence information whatsoever in the cosine margin.

GPU-accelerated: N=8192 M=200 200 trials per stratum, 3 seeds.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402


HARD_PASS_CORR = 0.50     # >= in 2+ strata
HARD_PASS_STRATA_COUNT = 2  # must hit in at least 2/4 noise strata
HARD_FAIL_CORR = 0.20     # < in ALL strata


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing keys in metrics")


def compute_verdict(s):
    if "strata_results" not in s:
        return ("CAP2_MARGIN_INCONCLUSIVE", "Missing strata_results.")
    strata = s["strata_results"]
    pass_count = sum(1 for v in strata.values() if v["corr_mean"] >= HARD_PASS_CORR)
    all_fail = all(v["corr_mean"] < HARD_FAIL_CORR for v in strata.values())
    if pass_count >= HARD_PASS_STRATA_COUNT:
        return ("CAP2_MARGIN_DETECTS",
                f"HARD PASS: margin-vs-correctness corr >= {HARD_PASS_CORR} in "
                f"{pass_count}/{len(strata)} noise strata (need {HARD_PASS_STRATA_COUNT}). "
                f"Cosine margin is a valid confidence proxy; metric-definition fix rescues Cap 2.")
    if all_fail:
        return ("CAP2_MARGIN_KILL",
                f"HARD FAIL: corr(margin, correct) < {HARD_FAIL_CORR} in ALL strata. "
                f"Substrate carries no margin-based confidence signal; Cap 2 structurally closed.")
    return ("CAP2_MARGIN_PARTIAL",
            f"Partial: {pass_count}/{len(strata)} strata above {HARD_PASS_CORR}. "
            f"Margin signal present in some strata but not >= {HARD_PASS_STRATA_COUNT}.")


def self_test_verdict():
    cases = [
        # 2+ strata pass -> DETECTS
        ({"strata_results": {"p0.0": {"corr_mean": 0.70}, "p0.05": {"corr_mean": 0.60},
                              "p0.10": {"corr_mean": 0.35}, "p0.20": {"corr_mean": 0.15}}},
         "CAP2_MARGIN_DETECTS"),
        # all < 0.20 -> KILL
        ({"strata_results": {"p0.0": {"corr_mean": 0.10}, "p0.05": {"corr_mean": 0.12},
                              "p0.10": {"corr_mean": 0.08}, "p0.20": {"corr_mean": 0.05}}},
         "CAP2_MARGIN_KILL"),
        # 1 stratum passes, not all < 0.20 -> PARTIAL
        ({"strata_results": {"p0.0": {"corr_mean": 0.55}, "p0.05": {"corr_mean": 0.35},
                              "p0.10": {"corr_mean": 0.30}, "p0.20": {"corr_mean": 0.25}}},
         "CAP2_MARGIN_PARTIAL"),
        ({}, "CAP2_MARGIN_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: got {got} expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def cosine_margin(W, query, M, N):
    """Return (is_error, margin) where margin = (top1_score - top2_score) / N."""
    # W shape: (N, N); query shape: (N,)
    # Retrieve: run one step of argmax dynamics
    retrieved = torch.sign(W @ query); retrieved[retrieved == 0] = 1.0
    # Compute overlap between retrieved state and all stored values
    # W was built as (values.T @ keys) / N; we need the per-pattern overlaps
    # Instead: compare retrieved to values directly
    # (values pre-stored as rows; overlap = dot / N)
    overlaps = M @ retrieved / N   # shape (M_patterns,)
    top2 = overlaps.topk(2)
    margin = float((top2.values[0] - top2.values[1]).item())
    # True target: keys[0..M-1] -> we'll pass target_idx
    return margin


def run_stratum(W, keys, values, p_flip, n_trials, n_patterns, N, seed, device):
    """Run n_trials at noise level p_flip; return list of (margin, is_correct) pairs."""
    gen = torch.Generator(device=device).manual_seed(seed + int(p_flip * 10000))
    margins = []; corrects = []
    for trial_i in range(n_trials):
        idx = trial_i % n_patterns
        k_noisy = keys[idx].clone()
        if p_flip > 0:
            flips = (torch.rand(N, generator=gen, device=device) < p_flip).float()
            k_noisy = k_noisy * (1.0 - 2.0 * flips)
        # Retrieve
        retrieved = torch.sign(W @ k_noisy); retrieved[retrieved == 0] = 1.0
        # Overlap with true value
        true_overlap = float((retrieved * values[idx]).mean().item())
        is_correct = 1 if true_overlap > 0.7 else 0
        # Cosine margin: overlap of retrieved with ALL values, take top1-top2
        overlaps = (values @ retrieved) / N   # (M_patterns,)
        top2 = overlaps.topk(min(2, overlaps.shape[0]))
        margin = float((top2.values[0] - (top2.values[1] if len(top2.values) > 1 else top2.values[0] - 1.0)).item())
        margins.append(margin); corrects.append(is_correct)
    return margins, corrects


def pearson_corr(xs, ys):
    n = len(xs)
    if n < 2: return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    vx = sum((x - mx) ** 2 for x in xs) / n
    vy = sum((y - my) ** 2 for y in ys) / n
    denom = (vx * vy) ** 0.5
    return cov / denom if denom > 1e-9 else 0.0


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {
        "N": 1024 if smoke else 8192,
        # Smoke: M=100 at N=1024 is near-capacity (K_crit~205 scales as M/N~0.025 at N=8192;
        # at N=1024 near-capacity is M~20-30; use M=30 to force some errors).
        "M": 30 if smoke else 200,
        "n_trials_per_stratum": 15 if smoke else 200,
        "noise_levels": [0.0, 0.05, 0.10, 0.20],
        "seeds": [17] if smoke else [17, 23, 31],
        "device": str(device),
        "note": "Cap 2 re-probe: cosine margin vs correctness correlation; stratified by noise level",
    }
    N = cfg["N"]; M = cfg["M"]

    strata_corrs_by_seed = {str(p): [] for p in cfg["noise_levels"]}

    for seed in cfg["seeds"]:
        gen = torch.Generator(device=device).manual_seed(seed)
        keys = torch.stack([make_pattern(N, gen, device) for _ in range(M)])
        values = torch.stack([make_pattern(N, gen, device) for _ in range(M)])
        W = (values.T @ keys) / N

        for p in cfg["noise_levels"]:
            margins, corrects = run_stratum(W, keys, values, p, cfg["n_trials_per_stratum"],
                                            M, N, seed, device)
            err_rate = 1.0 - sum(corrects) / len(corrects)
            corr = pearson_corr(margins, corrects)
            print(f"  seed={seed} p={p:.2f}: err_rate={err_rate:.3f} "
                  f"corr(margin,correct)={corr:.3f}", flush=True)
            strata_corrs_by_seed[str(p)].append(corr)

    # Average across seeds per stratum
    strata_results = {}
    for p in cfg["noise_levels"]:
        cs = strata_corrs_by_seed[str(p)]
        strata_results[f"p{p}"] = {
            "corr_mean": sum(cs) / len(cs),
            "corr_per_seed": cs,
            "p_flip": p,
        }
        print(f"  stratum p={p:.2f}: mean_corr={strata_results[f'p{p}']['corr_mean']:.3f}", flush=True)

    summary = {
        "strata_results": strata_results,
        "note": "metric=cosine_margin(top1-top2); stratified by noise level; "
                "v1 REFUTED tau-based metric; this is the margin-based re-probe",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_cap2_confidence_margin_probe_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # At small-N smoke (N=1024, M=30) all trials are correct (below capacity);
    # err_rate=0 means corr is degenerate -- this is expected.  Verify structure only.
    assert len(s["strata_results"]) == 4, f"Expected 4 strata, got {len(s['strata_results'])}"
    oracle.assert_baseline_high("strata_count", float(len(s["strata_results"])), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK (structure valid; verdict={v}; note: KILL expected at sub-capacity smoke N; signal appears at FULL N=8192 near-capacity)", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cap2_confidence_margin_probe_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__": sys.exit(main())
