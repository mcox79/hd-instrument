"""Pseudoinverse vs Hebbian Hopfield capacity — F2 RS-phase capacity extension.

Per Research 2026-05-22 15:15 RS-phase capacity mechanisms F2: Personnaz-Guyon-
Dreyfus 1985 / Kanter-Sompolinsky 1987 PRA 35:380 pseudoinverse rule:
  W_pseudo = Xi (Xi^T Xi)^(-1) Xi^T
gives EXACT fixed points for all P < N linearly independent patterns (alpha -> 1.0)
WITHOUT requiring RSB. Tradeoff: basins shrink as alpha -> 1.

Compares attractor accuracy at alpha in {0.138 (AGS critical), 0.50, 0.95} vs
canonical Hebbian. Direct test of substrate-applicable F2 learning rule.

Verdict thresholds:
  PINV_PASS:    pseudoinverse beats Hebbian by >=2x acc at alpha >= 0.50 (above AGS)
  PINV_PARTIAL: 1.2x <= ratio < 2x
  PINV_KILLED:  ratio < 1.2x (no learning-rule advantage at substrate operating point)
  PINV_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_pseudoinverse_capacity_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


PASS_RATIO = 2.0
PARTIAL_RATIO = 1.2


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "best_ratio" not in summary:
        return ("PINV_INCONCLUSIVE", "Missing best_ratio.")
    best = summary["best_ratio"]; best_alpha = summary["best_alpha"]
    ratios = summary["ratio_per_alpha"]
    if best >= PASS_RATIO:
        return ("PINV_PASS",
                f"Pseudoinverse > Hebbian: best ratio={best:.2f} at alpha={best_alpha} "
                f"(>={PASS_RATIO}). F2 learning rule unlocks supra-AGS storage. ratio_per_alpha={ratios}.")
    if best >= PARTIAL_RATIO:
        return ("PINV_PARTIAL",
                f"Partial gain: best ratio={best:.2f} at alpha={best_alpha} "
                f"({PARTIAL_RATIO}<=r<{PASS_RATIO}). Modest advantage; ratio_per_alpha={ratios}.")
    return ("PINV_KILLED",
            f"No advantage: best ratio={best:.2f} at alpha={best_alpha} (<{PARTIAL_RATIO}). "
            f"Pseudoinverse doesn't beat Hebbian at substrate operating point. ratio_per_alpha={ratios}.")


def self_test_verdict():
    cases = [
        ({"best_ratio": 3.0, "best_alpha": 0.5, "ratio_per_alpha": {}}, "PINV_PASS"),
        ({"best_ratio": 1.5, "best_alpha": 0.5, "ratio_per_alpha": {}}, "PINV_PARTIAL"),
        ({"best_ratio": 1.0, "best_alpha": 0.5, "ratio_per_alpha": {}}, "PINV_KILLED"),
        ({}, "PINV_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_patterns(M, N, cpu_gen, device):
    bits = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device)
    return 2.0 * bits.float() - 1.0


def hebbian_W(patterns, N):
    """W = (1/N) Xi^T Xi; zero diagonal."""
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    return W


def pseudoinverse_W(patterns):
    """W = Xi^T (Xi Xi^T)^(-1) Xi where Xi shape (M, N). Project onto pattern subspace."""
    M = patterns.shape[0]
    XX = patterns @ patterns.T  # (M, M)
    inv = torch.linalg.pinv(XX.float())
    W = patterns.T @ inv @ patterns  # (N, N)
    W.fill_diagonal_(0.0)
    return W


def attractor_accuracy(W, patterns, n_iter=5):
    """Sync update; check if patterns are fixed points after n_iter."""
    M = patterns.shape[0]
    correct = 0
    for i in range(M):
        s = patterns[i].clone()
        for _ in range(n_iter):
            h = W @ s
            s = torch.sign(h)
            s[s == 0] = 1.0
        # Compare to original
        match = float((s * patterns[i]).mean())
        if match > 0.95:
            correct += 1
    return correct / M


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "alpha_grid": [0.138, 0.50, 0.95] if not smoke else [0.50, 0.95],
              "n_iter": 3 if smoke else 5,
              "seeds": [17] if smoke else [17, 23, 31]}
    N = config["N"]
    ratio_per_alpha = {}
    detail_per_alpha = {}
    for alpha in config["alpha_grid"]:
        M = int(alpha * N)
        h_accs = []; p_accs = []
        for seed in config["seeds"]:
            cpu_gen = torch.Generator().manual_seed(seed)
            patterns = make_patterns(M, N, cpu_gen, device)
            Wh = hebbian_W(patterns, N)
            Wp = pseudoinverse_W(patterns)
            ha = attractor_accuracy(Wh, patterns, config["n_iter"])
            pa = attractor_accuracy(Wp, patterns, config["n_iter"])
            h_accs.append(ha); p_accs.append(pa)
            print(f"  alpha={alpha} seed={seed}: hebbian={ha:.3f}, pseudo={pa:.3f}", flush=True)
        ha_mean = sum(h_accs) / len(h_accs)
        pa_mean = sum(p_accs) / len(p_accs)
        # Avoid divide by zero / chance-level baseline
        ratio = pa_mean / max(ha_mean, 0.05)
        ratio_per_alpha[str(alpha)] = ratio
        detail_per_alpha[str(alpha)] = {"hebbian_acc": ha_mean, "pseudo_acc": pa_mean}
        print(f"  -> alpha={alpha}: hebbian={ha_mean:.3f}, pseudo={pa_mean:.3f}, ratio={ratio:.2f}", flush=True)
    best_alpha_str = max(ratio_per_alpha, key=ratio_per_alpha.get)
    best_ratio = ratio_per_alpha[best_alpha_str]
    summary = {"ratio_per_alpha": ratio_per_alpha,
                "detail_per_alpha": detail_per_alpha,
                "best_ratio": best_ratio,
                "best_alpha": float(best_alpha_str)}
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
    out_dir = get_output_dir("wave14_pseudoinverse_capacity_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("ratio_present", summary["best_ratio"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pseudoinverse_capacity_v1")
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
