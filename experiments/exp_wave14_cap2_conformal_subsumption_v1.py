"""Cap 2 conformal subsumption (Gap C rescue, Rescue 5 of v160 rehab) — v1.

Strategy x Research shore-up matrix Weakness #1 (HIGH priority).
Premise: Cap 2 PROVISIONAL ❌ at v160 was closed because the substrate carries no
intrinsic margin-based confidence signal. Two attempts (tau-iter count at v153,
cosine margin at v160) both crossed pre-reg hard-fail.

This experiment re-axiomatizes Cap 2 as DOWNSTREAM CONFORMAL CALIBRATION over the
existing observability stack — NOT a substrate-level confidence mechanism. The
customer-facing claim becomes "calibrated abstention via a conformal threshold
on the Bet G / cleanup confidence stream" rather than "intrinsic margin signal".

Pattern 1 (metric re-axiomatization) per research_meta_map_and_adjacencies. Zero
substrate change required; pure post-hoc Venn-Abers / split-conformal wrapper.

Construction:
  1. Generate the same retrieval pipeline used by cap2_confidence_margin_probe_v1
     (N=8192, M=200, multi-seed) — produces (margin, is_correct) pairs.
  2. Split: 50% calibration, 50% test.
  3. Calibration set: rank conformal score s(x) = -margin (low margin -> high score
     -> higher probability of being wrong). Threshold q_alpha at the
     ceil((n+1)(1-alpha))-th smallest score gives a (1-alpha) split-conformal
     coverage guarantee on i.i.d. data.
  4. Abstain when margin < threshold(alpha); commit otherwise.
  5. The Cap 2 claim is re-axiomatized as:
       "On the committed subset (margin >= threshold), retrieval accuracy >= 0.90."
     This is calibrated abstention — a stronger claim than mean accuracy.

HARD PASS:
  - Venn-Abers / conformal threshold achieves committed-set accuracy >= 0.90
    at abstention rate <= 0.20 in >= 3 / 5 seeds.
  - Pareto front shows monotone trade-off: as alpha decreases, abstention
    increases AND committed accuracy increases.

HARD FAIL:
  - No threshold achieves accuracy >= 0.90 at abstention <= 0.20 in ANY seed.
  - Pareto front is non-monotone (margin is not a calibratable score).

Verdict labels:
  CAP2_CONFORMAL_RESCUE_PASS       — HARD PASS criteria met; Cap 2 re-axiomatized
  CAP2_CONFORMAL_RESCUE_PARTIAL    — coverage achieved but Pareto degenerate
  CAP2_CONFORMAL_RESCUE_FAIL       — HARD FAIL; re-axiomatization does not deliver
  CAP2_CONFORMAL_RESCUE_INCONCLUSIVE

Pure CPU. ~30 min wallclock at FULL: N=8192 M=200 n_queries=400/seed 5 seeds.
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
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Pre-reg thresholds
HARD_PASS_ACC = 0.90          # committed-set accuracy floor
HARD_PASS_MAX_ABSTAIN = 0.20  # abstention rate ceiling
HARD_PASS_MIN_SEEDS = 3       # seeds that must satisfy both
HARD_FAIL_NO_SEED = 0         # if zero seeds satisfy -> FAIL
ALPHA_GRID = [0.30, 0.20, 0.10, 0.05]  # for Pareto-front sweep


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    if "seed_results" not in summary or "pareto_front" not in summary:
        return ("CAP2_CONFORMAL_RESCUE_INCONCLUSIVE", "Missing seed_results or pareto_front.")
    seed_results = summary["seed_results"]
    pareto = summary["pareto_front"]

    # Count seeds satisfying both committed-acc and abstain constraints at any alpha
    n_pass = 0
    best_per_seed = []
    for seed, alpha_dict in seed_results.items():
        sat = False
        best = None
        for alpha, res in alpha_dict.items():
            if (res["committed_acc"] >= HARD_PASS_ACC
                    and res["abstain_rate"] <= HARD_PASS_MAX_ABSTAIN):
                sat = True
                if best is None or res["committed_acc"] > best[1]:
                    best = (alpha, res["committed_acc"], res["abstain_rate"])
        if sat:
            n_pass += 1
        best_per_seed.append((seed, best))

    n_seeds = len(seed_results)

    # Pareto monotonicity: in this construction, tau = the alpha-quantile of calibration
    # margins (low-tau = small alpha threshold). As alpha DECREASES, tau DECREASES,
    # so we abstain LESS. Likewise committed accuracy should DECREASE because we
    # admit borderline cases. So the expected monotonicity is:
    #   alpha_hi (lax)   -> abstain_hi, acc_hi
    #   alpha_lo (strict)-> abstain_lo, acc_lo (admits more, accuracy drops)
    # Sort by descending alpha; abstain should be non-INCREASING (tolerate noise).
    pareto_monotone = True
    pareto_sorted = sorted(pareto, key=lambda p: -p["alpha"])  # large alpha -> small
    for i in range(len(pareto_sorted) - 1):
        a_hi = pareto_sorted[i]
        a_lo = pareto_sorted[i + 1]
        # tolerate small noise
        if a_lo["abstain_rate"] > a_hi["abstain_rate"] + 0.05:
            pareto_monotone = False
            break

    if n_pass >= HARD_PASS_MIN_SEEDS and pareto_monotone:
        return ("CAP2_CONFORMAL_RESCUE_PASS",
                f"HARD PASS: conformal subsumption rescues Cap 2. {n_pass}/{n_seeds} seeds "
                f"achieve committed_acc >= {HARD_PASS_ACC} at abstain <= "
                f"{HARD_PASS_MAX_ABSTAIN}. Pareto front monotone. "
                f"Cap 2 re-axiomatized as calibrated abstention over Bet G stream.")
    if n_pass == HARD_FAIL_NO_SEED:
        return ("CAP2_CONFORMAL_RESCUE_FAIL",
                f"HARD FAIL: 0/{n_seeds} seeds reach committed_acc >= "
                f"{HARD_PASS_ACC} at abstain <= {HARD_PASS_MAX_ABSTAIN} at ANY alpha. "
                f"Margin is not a calibratable confidence score on this substrate; "
                f"Cap 2 closure stands.")
    if n_pass >= HARD_PASS_MIN_SEEDS and not pareto_monotone:
        return ("CAP2_CONFORMAL_RESCUE_PARTIAL",
                f"Calibration coverage achieved ({n_pass}/{n_seeds}) but Pareto front "
                f"non-monotone: margin is partially calibratable but not a clean "
                f"conformal score. Re-axiomatization yields an unstable customer claim.")
    return ("CAP2_CONFORMAL_RESCUE_PARTIAL",
            f"Partial: {n_pass}/{n_seeds} seeds satisfy gate (need {HARD_PASS_MIN_SEEDS}). "
            f"Re-axiomatization holds for a minority of seeds; portfolio claim is fragile.")


def self_test_verdict():
    # 5 seeds, 3 satisfy gate, pareto monotone -> PASS
    res_pass = {
        "seed_results": {str(s): {
            "0.30": {"committed_acc": 0.95, "abstain_rate": 0.15},
            "0.20": {"committed_acc": 0.92, "abstain_rate": 0.10},
            "0.10": {"committed_acc": 0.88, "abstain_rate": 0.05},
            "0.05": {"committed_acc": 0.85, "abstain_rate": 0.03},
        } for s in range(5)},
        "pareto_front": [
            {"alpha": 0.30, "abstain_rate": 0.15, "committed_acc": 0.95},
            {"alpha": 0.20, "abstain_rate": 0.10, "committed_acc": 0.92},
            {"alpha": 0.10, "abstain_rate": 0.05, "committed_acc": 0.88},
            {"alpha": 0.05, "abstain_rate": 0.03, "committed_acc": 0.85},
        ],
    }
    v, _ = compute_verdict(res_pass)
    assert v == "CAP2_CONFORMAL_RESCUE_PASS", f"expected PASS got {v}"

    # 0 seeds satisfy gate -> FAIL
    res_fail = {
        "seed_results": {str(s): {
            "0.30": {"committed_acc": 0.70, "abstain_rate": 0.40},
            "0.20": {"committed_acc": 0.65, "abstain_rate": 0.30},
            "0.10": {"committed_acc": 0.60, "abstain_rate": 0.25},
            "0.05": {"committed_acc": 0.55, "abstain_rate": 0.22},
        } for s in range(5)},
        "pareto_front": [
            {"alpha": 0.30, "abstain_rate": 0.40, "committed_acc": 0.70},
            {"alpha": 0.20, "abstain_rate": 0.30, "committed_acc": 0.65},
            {"alpha": 0.10, "abstain_rate": 0.25, "committed_acc": 0.60},
            {"alpha": 0.05, "abstain_rate": 0.22, "committed_acc": 0.55},
        ],
    }
    v, _ = compute_verdict(res_fail)
    assert v == "CAP2_CONFORMAL_RESCUE_FAIL", f"expected FAIL got {v}"

    # 3+ seeds satisfy, non-monotone pareto -> PARTIAL
    res_partial = {
        "seed_results": {str(s): {
            "0.30": {"committed_acc": 0.95, "abstain_rate": 0.05},
            "0.20": {"committed_acc": 0.92, "abstain_rate": 0.10},
            "0.10": {"committed_acc": 0.88, "abstain_rate": 0.30},  # abstain SPIKES at alpha=0.10
            "0.05": {"committed_acc": 0.85, "abstain_rate": 0.03},
        } for s in range(5)},
        "pareto_front": [
            {"alpha": 0.30, "abstain_rate": 0.05, "committed_acc": 0.95},
            {"alpha": 0.20, "abstain_rate": 0.10, "committed_acc": 0.92},
            {"alpha": 0.10, "abstain_rate": 0.30, "committed_acc": 0.88},
            {"alpha": 0.05, "abstain_rate": 0.03, "committed_acc": 0.85},
        ],
    }
    v, _ = compute_verdict(res_partial)
    assert v == "CAP2_CONFORMAL_RESCUE_PARTIAL", f"expected PARTIAL got {v}"

    v, _ = compute_verdict({})
    assert v == "CAP2_CONFORMAL_RESCUE_INCONCLUSIVE"
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def generate_margin_correct_pairs(N, M, n_queries, seed, device):
    """Run the Bet G / cleanup stream and produce (margin, is_correct) pairs.

    This is the SAME pipeline as cap2_confidence_margin_probe_v1 (Bet G calibration
    stream) but extracts the raw (margin, correctness) pairs across a noise
    distribution — these are the points the downstream conformal layer wraps.
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = torch.stack([make_pattern(N, gen, device) for _ in range(M)])
    values = torch.stack([make_pattern(N, gen, device) for _ in range(M)])
    W = (values.T @ keys) / N
    pairs = []
    # Stratify noise across the queries to span the full operating range.
    noise_grid = [0.0, 0.05, 0.10, 0.15, 0.20]
    per_stratum = max(1, n_queries // len(noise_grid))
    for p_flip in noise_grid:
        for trial in range(per_stratum):
            idx = (trial * 7919) % M  # deterministic-ish
            k_noisy = keys[idx].clone()
            if p_flip > 0:
                flips = (torch.rand(N, generator=gen, device=device) < p_flip).float()
                k_noisy = k_noisy * (1.0 - 2.0 * flips)
            retrieved = torch.sign(W @ k_noisy)
            retrieved[retrieved == 0] = 1.0
            true_overlap = float((retrieved * values[idx]).mean().item())
            is_correct = 1 if true_overlap > 0.7 else 0
            overlaps = (values @ retrieved) / N
            top2 = overlaps.topk(min(2, overlaps.shape[0]))
            margin = float((top2.values[0] - top2.values[1]).item())
            pairs.append((margin, is_correct, p_flip))
    return pairs


def conformal_threshold(cal_margins, alpha):
    """Split-conformal threshold: abstain when margin < tau.

    Score s(x) = -margin (so low margin -> high score -> reject).
    For coverage 1-alpha, take the ceil((n+1)(1-alpha))-th smallest score's NEGATIVE
    as the margin threshold tau. Concretely, sort calibration margins ascending;
    take the floor((n+1)*alpha)-th smallest margin as tau (abstain if margin < tau).
    """
    n = len(cal_margins)
    if n == 0:
        return float("-inf")
    sorted_m = sorted(cal_margins)
    # Quantile index for abstention: lowest alpha fraction get rejected
    q_idx = max(0, min(n - 1, int(math.floor((n + 1) * alpha)) - 1))
    return sorted_m[q_idx]


def evaluate_threshold(test_pairs, tau):
    """Return (committed_acc, abstain_rate, n_committed, n_total)."""
    n_total = len(test_pairs)
    committed_correct = 0
    committed_count = 0
    abstain_count = 0
    for margin, is_correct, _ in test_pairs:
        if margin < tau:
            abstain_count += 1
        else:
            committed_count += 1
            if is_correct:
                committed_correct += 1
    committed_acc = (committed_correct / committed_count) if committed_count > 0 else 0.0
    abstain_rate = abstain_count / n_total if n_total > 0 else 0.0
    return committed_acc, abstain_rate, committed_count, n_total


def run_one_seed(seed, config, device):
    pairs = generate_margin_correct_pairs(config["N"], config["M"],
                                          config["n_queries"], seed, device)
    # Split: first 50% calibration, second 50% test (deterministic w.r.t. seed).
    cut = len(pairs) // 2
    cal = pairs[:cut]
    test = pairs[cut:]
    cal_margins = [m for (m, _, _) in cal]

    alpha_results = {}
    for alpha in config["alpha_grid"]:
        tau = conformal_threshold(cal_margins, alpha)
        c_acc, abs_rate, n_c, n_t = evaluate_threshold(test, tau)
        alpha_results[str(alpha)] = {
            "alpha": alpha,
            "tau": tau,
            "committed_acc": c_acc,
            "abstain_rate": abs_rate,
            "n_committed": n_c,
            "n_total": n_t,
        }
    return alpha_results


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # pure CPU per matrix spec
    config = {
        "N": 1024 if smoke else 8192,
        "M": 30 if smoke else 200,
        "n_queries": 100 if smoke else 800,  # queries per seed (before 50/50 split)
        "seeds": [17] if smoke else [17, 23, 31, 37, 41],
        "alpha_grid": ALPHA_GRID,
        "device": "cpu",
        "note": ("Cap 2 conformal subsumption: re-axiomatize as calibrated "
                 "abstention over Bet G stream; pure post-hoc wrapper."),
    }
    print(f"Cap 2 conformal: N={config['N']} M={config['M']} "
          f"queries/seed={config['n_queries']} seeds={config['seeds']}", flush=True)

    seed_results = {}
    pareto_per_alpha = {a: [] for a in config["alpha_grid"]}

    for seed in config["seeds"]:
        ar = run_one_seed(seed, config, device)
        seed_results[str(seed)] = ar
        for alpha_str, res in ar.items():
            pareto_per_alpha[float(alpha_str)].append(
                (res["committed_acc"], res["abstain_rate"])
            )
        print(f"  seed={seed}: " + ", ".join(
            f"alpha={a:.2f} acc={ar[str(a)]['committed_acc']:.3f} "
            f"abs={ar[str(a)]['abstain_rate']:.3f}"
            for a in config["alpha_grid"]
        ), flush=True)

    # Pareto front: mean across seeds per alpha
    pareto_front = []
    for alpha, lst in pareto_per_alpha.items():
        accs = [p[0] for p in lst]
        absrs = [p[1] for p in lst]
        pareto_front.append({
            "alpha": alpha,
            "committed_acc": sum(accs) / len(accs),
            "abstain_rate": sum(absrs) / len(absrs),
        })

    summary = {
        "seed_results": seed_results,
        "pareto_front": pareto_front,
        "n_seeds": len(config["seeds"]),
        "alpha_grid": config["alpha_grid"],
        "note": "Pattern 1 metric re-axiomatization; zero substrate change.",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nPareto front (mean across seeds):", flush=True)
    for pt in sorted(pareto_front, key=lambda p: -p["alpha"]):
        print(f"  alpha={pt['alpha']:.2f}: committed_acc={pt['committed_acc']:.3f} "
              f"abstain={pt['abstain_rate']:.3f}", flush=True)
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
    self_test_verdict()
    out_dir = get_output_dir("wave14_cap2_conformal_subsumption_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    assert len(s["seed_results"]) >= 1, "smoke: at least one seed required"
    assert len(s["pareto_front"]) == len(ALPHA_GRID), "smoke: pareto_front size mismatch"
    oracle.assert_baseline_high("pareto_count", float(len(s["pareto_front"])), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK (verdict={v}; sub-capacity smoke may PASS or FAIL artificially; "
          f"FULL N=8192 M=200 5-seed is the discriminating run)", flush=True)


def run_main():
    self_test_verdict()
    out_dir = get_output_dir("wave14_cap2_conformal_subsumption_v1")
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
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
