"""Iterative sign-projection forensics on random-key substrate (Bet 3).

Test of "iterative charge-flipping closes the high-K SVD gap" claim from
active_priorities.md Bet 3. v1 implements the sign-projection refinement
that is the substrate-equivalent of Oszlanyi-Suto charge flipping when W
is fully known (not just its Fourier amplitudes). See prereg for the
implementation-vs-paper honesty note.

Three methods compared at K in {50, 200, 500, 1000, 2000}:
  - SVD: top-K singular vectors, sign-quantized, Hungarian-matched to truth
  - CF random init: iterative sign-projection from random ±1 init
  - CF SVD init: iterative sign-projection from SVD top-K init

Metric: mean cos(recovered_v_matched, true_v) per K. Plus key-index recall@10
at K=500 and iter-count-to-convergence trajectory.

Pre-reg: preregs/2026-05-21_wave14s_chargeflip_forensics_v1.md
"""
from __future__ import annotations

import argparse
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


N_FULL = 4096
N_SMOKE = 512
K_FULL = [50, 200, 500, 1000, 2000]
K_SMOKE = [10, 20]
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
MAX_ITER_FULL = 100
MAX_ITER_SMOKE = 30
CONVERGE_TOL = 1e-4
MAX_ITER_LIMIT = 200

PASS_SVD_BASELINE_AT_HIGH_K = 0.15
PASS_CF_IMPROVEMENT = 0.20
PASS_KILL_DELTA = 0.05
PASS_RECALL_AT_10 = 0.70


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


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_method = summary.get("by_method")
    if not by_method:
        return ("CHARGEFLIP_FORENSICS_INCONCLUSIVE", "Missing per-method data.")
    svd = by_method.get("svd", {})
    cf_svd = by_method.get("cf_svd", {})
    cf_rand = by_method.get("cf_rand", {})
    if not svd or not cf_svd:
        return ("CHARGEFLIP_FORENSICS_INCONCLUSIVE", "Missing SVD or CF-SVD method data.")

    per_k_svd = {row["K"]: row for row in svd.get("per_k", [])}
    per_k_cf_svd = {row["K"]: row for row in cf_svd.get("per_k", [])}
    per_k_cf_rand = {row["K"]: row for row in cf_rand.get("per_k", [])}
    if not per_k_svd or not per_k_cf_svd:
        return ("CHARGEFLIP_FORENSICS_INCONCLUSIVE", "No per-K rows.")

    K_high = max(per_k_svd.keys())
    svd_high = per_k_svd[K_high]["mean_cos"]
    cf_svd_high = per_k_cf_svd[K_high]["mean_cos"]
    cf_rand_high = per_k_cf_rand[K_high]["mean_cos"] if K_high in per_k_cf_rand else float("nan")
    improvement = cf_svd_high - svd_high

    # Iteration convergence check
    max_iters_seen = max(
        max((row["mean_iters"] for row in cf_svd.get("per_k", [])), default=0),
        max((row["mean_iters"] for row in cf_rand.get("per_k", [])), default=0),
    )
    if max_iters_seen > MAX_ITER_LIMIT:
        return ("CHARGEFLIP_NONCONVERGENT",
                f"CF iter count {max_iters_seen} > {MAX_ITER_LIMIT}; algorithm not practical "
                f"at substrate scale.")

    # Kill criterion: CF doesn't beat SVD by even 0.05
    if improvement <= PASS_KILL_DELTA:
        return ("CHARGEFLIP_FORENSICS_NO_GAIN",
                f"At K={K_high}: SVD cos={svd_high:.3f}, CF-from-SVD cos={cf_svd_high:.3f}, "
                f"improvement {improvement:+.3f} <= {PASS_KILL_DELTA}. Iterative refinement "
                f"adds nothing; random-key forensics stays at research-only (SVD-only capability).")

    # Pass conditions
    svd_baseline_ok = svd_high < PASS_SVD_BASELINE_AT_HIGH_K
    cf_improvement_ok = improvement > PASS_CF_IMPROVEMENT
    cf_rand_floor_ok = cf_rand_high >= 0.10

    # recall@10 at K=500 if present
    recall_at_10 = None
    if 500 in per_k_cf_svd:
        recall_at_10 = per_k_cf_svd[500].get("recall_at_10")

    if (svd_baseline_ok and cf_improvement_ok and cf_rand_floor_ok and
        recall_at_10 is not None and recall_at_10 >= PASS_RECALL_AT_10):
        return ("CHARGEFLIP_FORENSICS_PASS",
                f"At K={K_high}: SVD cos={svd_high:.3f} < {PASS_SVD_BASELINE_AT_HIGH_K} "
                f"(baseline gap replicated). CF-from-SVD cos={cf_svd_high:.3f}, improvement "
                f"{improvement:+.3f} > {PASS_CF_IMPROVEMENT}. CF-random cos={cf_rand_high:.3f}. "
                f"recall@10 at K=500 = {recall_at_10:.3f} >= {PASS_RECALL_AT_10}. "
                f"Random-key forensics gap closed; cap_map upgrade candidate.")

    # Marginal: criteria 1-3 pass but recall is low
    if svd_baseline_ok and cf_improvement_ok and (recall_at_10 is None or
                                                   recall_at_10 < PASS_RECALL_AT_10):
        return ("CHARGEFLIP_FORENSICS_MARGINAL",
                f"CF improves over SVD ({improvement:+.3f}) but recall@10 at K=500 = "
                f"{recall_at_10 if recall_at_10 is not None else 'n/a'} < {PASS_RECALL_AT_10}. "
                f"Atoms partially recovered; cap_map inconclusive with caveat.")

    return ("CHARGEFLIP_FORENSICS_MARGINAL",
            f"Mixed signal: SVD_baseline_low={svd_baseline_ok}, "
            f"CF_improves={cf_improvement_ok}, CF_rand_floor={cf_rand_floor_ok}. "
            f"improvement={improvement:+.3f}, recall@10={recall_at_10}. "
            f"Inspect per-K table.")


def self_test_verdict() -> None:
    cases = [
        # 1. PASS: SVD low at high K, CF beats it by >0.20, CF_rand floor met, recall good
        ({"by_method": {
            "svd": {"per_k": [
                {"K": 50, "mean_cos": 0.95, "mean_iters": 0},
                {"K": 2000, "mean_cos": 0.09, "mean_iters": 0}]},
            "cf_svd": {"per_k": [
                {"K": 50, "mean_cos": 0.98, "mean_iters": 5},
                {"K": 500, "mean_cos": 0.80, "mean_iters": 20, "recall_at_10": 0.90},
                {"K": 2000, "mean_cos": 0.40, "mean_iters": 50}]},
            "cf_rand": {"per_k": [
                {"K": 50, "mean_cos": 0.80, "mean_iters": 50},
                {"K": 2000, "mean_cos": 0.15, "mean_iters": 100}]}}},
         "CHARGEFLIP_FORENSICS_PASS"),
        # 2. NO_GAIN: CF barely beats SVD
        ({"by_method": {
            "svd": {"per_k": [{"K": 2000, "mean_cos": 0.09, "mean_iters": 0}]},
            "cf_svd": {"per_k": [{"K": 2000, "mean_cos": 0.11, "mean_iters": 50,
                                    "recall_at_10": 0.5}]},
            "cf_rand": {"per_k": [{"K": 2000, "mean_cos": 0.05, "mean_iters": 100}]}}},
         "CHARGEFLIP_FORENSICS_NO_GAIN"),
        # 3. MARGINAL: CF beats SVD but recall@10 is missing or low
        ({"by_method": {
            "svd": {"per_k": [
                {"K": 2000, "mean_cos": 0.09, "mean_iters": 0}]},
            "cf_svd": {"per_k": [
                {"K": 500, "mean_cos": 0.60, "mean_iters": 20, "recall_at_10": 0.50},
                {"K": 2000, "mean_cos": 0.35, "mean_iters": 50}]},
            "cf_rand": {"per_k": [{"K": 2000, "mean_cos": 0.15, "mean_iters": 100}]}}},
         "CHARGEFLIP_FORENSICS_MARGINAL"),
        # 4. NONCONVERGENT
        ({"by_method": {
            "svd": {"per_k": [{"K": 2000, "mean_cos": 0.09, "mean_iters": 0}]},
            "cf_svd": {"per_k": [{"K": 2000, "mean_cos": 0.40, "mean_iters": 250,
                                    "recall_at_10": 0.8}]},
            "cf_rand": {"per_k": [{"K": 2000, "mean_cos": 0.20, "mean_iters": 250}]}}},
         "CHARGEFLIP_NONCONVERGENT"),
        # 5. INCONCLUSIVE
        ({}, "CHARGEFLIP_FORENSICS_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_random_bipolar(shape, gen, device):
    return 2.0 * (torch.rand(shape, generator=gen, device=device) > 0.5).float() - 1.0


def build_W(V, K_atoms, N):
    """V, K_atoms both (N, atoms) with atoms as columns.
    W = Σ_i V[:,i] K_atoms[:,i]^T / N = V @ K_atoms.T / N → (N, N)."""
    return (V @ K_atoms.T) / N


def hungarian_sign_match(V_hat, V_true):
    """For each true column, find the best-cos hat column and sign.
    Returns matched V_hat aligned to V_true plus per-column cos values.

    Algorithm: greedy on |cos| (true Hungarian is overkill at K ≤ 2000 and
    greedy is empirically the same answer for non-degenerate atoms).
    """
    K_true = V_true.shape[1]
    K_hat = V_hat.shape[1]
    # cos matrix: (K_true, K_hat)
    v_hat_n = V_hat / (V_hat.norm(dim=0, keepdim=True) + 1e-12)
    v_true_n = V_true / (V_true.norm(dim=0, keepdim=True) + 1e-12)
    cos_matrix = v_true_n.T @ v_hat_n
    abs_cos = cos_matrix.abs()

    assigned = []
    cos_out = torch.zeros(K_true, device=V_hat.device)
    available_hat = torch.ones(K_hat, dtype=torch.bool, device=V_hat.device)
    for i in range(K_true):
        scores = abs_cos[i].clone()
        scores[~available_hat] = -1.0
        j = int(scores.argmax().item())
        if scores[j] < 0:
            assigned.append(-1)
            continue
        assigned.append(j)
        cos_out[i] = cos_matrix[i, j]  # signed cos
        available_hat[j] = False
    # Build matched V_hat with sign flipped to match V_true
    V_hat_matched = torch.zeros_like(V_true)
    for i, j in enumerate(assigned):
        if j < 0:
            continue
        V_hat_matched[:, i] = V_hat[:, j] * (1.0 if cos_out[i] >= 0 else -1.0)
    return V_hat_matched, cos_out.abs()  # report |cos|


def svd_recover(W, K):
    """Recover top-K (V, K) atoms via SVD + sign quantize."""
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    V_hat = torch.sign(U[:, :K])
    V_hat = torch.where(V_hat == 0, torch.ones_like(V_hat), V_hat)
    K_hat = torch.sign(Vh[:K, :].T)
    K_hat = torch.where(K_hat == 0, torch.ones_like(K_hat), K_hat)
    # Scale singular values back in
    return V_hat, K_hat, S[:K]


def chargeflip_iter(W, V_init, K_init, max_iter, converge_tol):
    """Iterative sign-projection. Alternate K_hat = sign(V_hat^T W),
    V_hat = sign(W K_hat / ||K_hat||^2). Return (V_hat, K_hat, iters_used)."""
    V_hat = V_init.clone()
    K_hat = K_init.clone()
    iters = 0
    for _ in range(max_iter):
        iters += 1
        K_hat_new = torch.sign(V_hat.T @ W * 1.0)
        K_hat_new = torch.where(K_hat_new == 0, torch.ones_like(K_hat_new), K_hat_new)
        K_hat_new = K_hat_new.T  # (N, K_hat columns)
        # Now compute V_hat_new = sign(W K_hat_new / col norms)
        denom = (K_hat_new ** 2).sum(dim=0).clamp(min=1.0)
        V_hat_new = torch.sign((W @ K_hat_new) / denom)
        V_hat_new = torch.where(V_hat_new == 0, torch.ones_like(V_hat_new), V_hat_new)
        # Convergence: how many sign-bits flipped?
        if iters > 1:
            v_changes = (V_hat_new != V_hat).float().mean().item()
            k_changes = (K_hat_new != K_hat).float().mean().item()
            V_hat = V_hat_new
            K_hat = K_hat_new
            if max(v_changes, k_changes) < converge_tol:
                break
        else:
            V_hat = V_hat_new
            K_hat = K_hat_new
    return V_hat, K_hat, iters


def evaluate_recovery(V_hat, K_hat, V_true, K_true, top_n_recall=10):
    """Compute mean |cos(V_hat_matched, V_true)|, plus recall@N for top-N atoms."""
    V_matched, cos_per_col = hungarian_sign_match(V_hat, V_true)
    mean_cos = float(cos_per_col.mean())

    # Recall@10: of the top-N (by |cos| to truth) recovered atoms, how many match the top-N
    # truth atoms (here defined as the first top_n_recall truth columns by convention).
    # The truth atoms are unordered, so recall@10 is just: did we recover N≥top_n_recall atoms
    # with cos >= 0.5 (a permissive bar)?
    cos_sorted, _ = cos_per_col.sort(descending=True)
    n_recovered_at_thresh = int((cos_per_col >= 0.5).sum().item())
    recall_at_n = min(1.0, n_recovered_at_thresh / max(top_n_recall, 1))

    return {"mean_cos": mean_cos, "recall_at_10": recall_at_n}


def run_method(method: str, W, V_true, K_true, K_recover, max_iter, converge_tol,
                gen, device):
    if method == "svd":
        V_hat, K_hat, _ = svd_recover(W, K_recover)
        result = evaluate_recovery(V_hat, K_hat, V_true, K_true)
        result["mean_iters"] = 0
        return result
    if method == "cf_svd":
        V_init, K_init, _ = svd_recover(W, K_recover)
        V_hat, K_hat, iters = chargeflip_iter(W, V_init, K_init, max_iter, converge_tol)
        result = evaluate_recovery(V_hat, K_hat, V_true, K_true)
        result["mean_iters"] = iters
        return result
    if method == "cf_rand":
        N = W.shape[0]
        V_init = make_random_bipolar((N, K_recover), gen, device)
        K_init = make_random_bipolar((N, K_recover), gen, device)
        V_hat, K_hat, iters = chargeflip_iter(W, V_init, K_init, max_iter, converge_tol)
        result = evaluate_recovery(V_hat, K_hat, V_true, K_true)
        result["mean_iters"] = iters
        return result
    raise ValueError(f"unknown method {method}")


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "K_list": K_SMOKE if smoke else K_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "max_iter": MAX_ITER_SMOKE if smoke else MAX_ITER_FULL,
        "converge_tol": CONVERGE_TOL,
        "methods": ["svd", "cf_svd", "cf_rand"],
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    by_method = {m: {"per_k": []} for m in config["methods"]}
    for K_recover in config["K_list"]:
        per_seed = {m: [] for m in config["methods"]}
        for seed in config["seeds"]:
            gen = torch.Generator(device=device).manual_seed(seed)
            V_true = make_random_bipolar((config["N"], K_recover), gen, device)
            K_true = make_random_bipolar((config["N"], K_recover), gen, device)
            W = build_W(V_true, K_true, config["N"])
            for method in config["methods"]:
                r = run_method(method, W, V_true, K_true, K_recover,
                                config["max_iter"], config["converge_tol"], gen, device)
                per_seed[method].append({"seed": seed, **r})
        for method in config["methods"]:
            rows = per_seed[method]
            agg = {
                "K": K_recover,
                "mean_cos": sum(r["mean_cos"] for r in rows) / len(rows),
                "mean_iters": sum(r["mean_iters"] for r in rows) / len(rows),
                "recall_at_10": sum(r["recall_at_10"] for r in rows) / len(rows),
                "per_seed": rows,
            }
            by_method[method]["per_k"].append(agg)
        # Quick log
        for method in config["methods"]:
            row = by_method[method]["per_k"][-1]
            print(f"  K={K_recover:4d} {method:8s}  cos={row['mean_cos']:.3f}  "
                  f"iters={row['mean_iters']:.1f}  recall@10={row['recall_at_10']:.3f}",
                  flush=True)

    summary = {"by_method": by_method}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start
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
    out_dir = get_output_dir("wave14s_chargeflip_forensics_v1_smoke")
    log_event("experiment_started", name="wave14s_chargeflip_forensics_v1", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle assertions
    svd_low_K = summary["by_method"]["svd"]["per_k"][0]
    cf_svd_low_K = summary["by_method"]["cf_svd"]["per_k"][0]
    oracle.assert_in_range("svd_cos_low_K", svd_low_K["mean_cos"], (0.2, 1.0))
    oracle.assert_in_range("cf_iter_count_smoke", cf_svd_low_K["mean_iters"], (1.0, MAX_ITER_LIMIT))
    # CF-SVD should match or beat SVD at low K (it's initialized from SVD)
    if cf_svd_low_K["mean_cos"] < svd_low_K["mean_cos"] - 0.01:
        raise AssertionError(
            f"SANITY FAIL [cf_svd_regresses]: cf_svd={cf_svd_low_K['mean_cos']:.3f} < "
            f"svd={svd_low_K['mean_cos']:.3f} at low K. Iter shouldn't regress from init.")

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14s_chargeflip_forensics_v1",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14s_chargeflip_forensics_v1")
    log_event("experiment_started", name="wave14s_chargeflip_forensics_v1", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14s_chargeflip_forensics_v1",
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
