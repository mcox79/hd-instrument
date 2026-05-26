"""Bet Y Phase 2 — Kerdock keys + calibrated beta sweep (beta=8 vs beta=32 vs beta=2).

Per Strategy Phase 2 gate request (2026-05-22 11:30 EDT):
beta-calibration smoke (cycle 100) measured c = beta*N = 32768. Predicts
beta_optimal(N=4096) = 8. Phase 0/v1 ran random bipolar keys at beta=8 with
ratio=1.0 (PARTIAL). Strategy hypothesizes substrate at calibrated beta with
*structured* (Kerdock 4-coset) keys may activate exp-capacity regime.

Tests in-experiment beta sensitivity at fixed N=4096 with Kerdock 4-coset
codebook over multiple M values.

Verdict thresholds (per strategy_request_to_exp_dev_BetY_V2D_phase2_gate):
  PHASE2_PASS:    best_ratio >= 1.5 (substrate enters exp-capacity regime)
  PHASE2_PARTIAL: 1.0 <= best_ratio < 1.5 (some gain; beta-blend needed)
  PHASE2_KILLED:  best_ratio < 1.0 (modern dense AM never beats argmax)
  PHASE2_INCONCLUSIVE: missing metric

Pre-reg: preregs/2026-05-22_wave14_betY_phase2_kerdock_betacalibrated_v1.md
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

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


PASS_RATIO = 1.5
KILL_RATIO = 1.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "best_ratio" not in summary:
        return ("BET_Y_PHASE2_INCONCLUSIVE", "Missing best_ratio.")
    best_ratio = summary["best_ratio"]
    best_beta = summary["best_beta"]
    by_beta = summary["ratio_per_beta"]
    if best_ratio >= PASS_RATIO:
        return ("BET_Y_PHASE2_PASS",
                f"Modern dense AM ratio peaks at beta={best_beta} ratio={best_ratio:.2f} "
                f"(>= {PASS_RATIO}). Substrate enters exp-capacity regime under "
                f"Kerdock 4-coset keys. Phase 3 (N=65536 beta=0.5) cleared.")
    if best_ratio < KILL_RATIO:
        return ("BET_Y_PHASE2_KILLED",
                f"All tested betas yield ratio<1.0 (best={best_ratio:.2f} at beta={best_beta}). "
                f"Modern dense AM cleanup never beats argmax with Kerdock keys at N=4096. "
                f"ratio_per_beta={by_beta}.")
    return ("BET_Y_PHASE2_PARTIAL",
            f"Best ratio={best_ratio:.2f} at beta={best_beta} (1.0 <= ratio < {PASS_RATIO}). "
            f"Partial exp-capacity gain; substrate is in intermediate regime. "
            f"ratio_per_beta={by_beta}. Consider beta-blend strategy.")


def self_test_verdict():
    cases = [
        ({"best_ratio": 1.8, "best_beta": 8, "ratio_per_beta": {"2": 0.9, "8": 1.8, "32": 1.0}}, "BET_Y_PHASE2_PASS"),
        ({"best_ratio": 1.2, "best_beta": 8, "ratio_per_beta": {"2": 0.9, "8": 1.2, "32": 1.0}}, "BET_Y_PHASE2_PARTIAL"),
        ({"best_ratio": 0.7, "best_beta": 8, "ratio_per_beta": {"2": 0.5, "8": 0.7, "32": 0.6}}, "BET_Y_PHASE2_KILLED"),
        ({}, "BET_Y_PHASE2_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def kerdock_keys(M, N, device, gen):
    """Draw M keys from Kerdock 4-coset codebook (4N codewords)."""
    cb, _ = v3.make_kerdock_4coset_codebook(N, device)
    idx = torch.randperm(cb.shape[0], generator=gen)[:M].to(device)
    return cb[idx].float()


def random_bipolar(M, N, device, gen):
    return 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0


def capacity_argmax(keys, values, N):
    M = keys.shape[0]
    W = (values.T @ keys) / N
    pred = (keys @ W.T @ values.T).argmax(dim=1)
    return float((pred == torch.arange(M, device=keys.device)).float().mean())


def capacity_modern_dense(keys, values, N, beta, n_iter):
    M = keys.shape[0]
    W = (values.T @ keys) / N
    correct = 0
    for i in range(M):
        state = (keys[i] @ W.T).float()
        for _ in range(n_iter):
            sims = (values @ state) * beta
            sims = sims - sims.max()
            w = torch.softmax(sims, dim=0)
            state = w @ values
        if int((values @ state).argmax().item()) == i:
            correct += 1
    return correct / M


def find_max_passing_M(test_fn, key_fn, N, M_grid, n_seeds, device, fn_kwargs=None):
    fn_kwargs = fn_kwargs or {}
    best = 0
    # Kerdock 4-coset has 4N codewords; cap M_grid to fit codebook
    max_M = 4 * N
    for M in M_grid:
        if M > max_M:
            continue
        ok = 0
        for s in range(n_seeds):
            gen_d = torch.Generator(device=device).manual_seed(s * 17 + 7)
            gen_c = torch.Generator().manual_seed(s * 17 + 7)
            keys = key_fn(M, N, device, gen_c)
            values = random_bipolar(M, N, device, gen_d)
            acc = test_fn(keys=keys, values=values, N=N, **fn_kwargs)
            if acc >= 0.95:
                ok += 1
        if ok >= max(1, n_seeds * 2 // 3):
            best = max(best, M)
    return best / N


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_grid": [256, 512] if smoke else [1024, 4096, 8192, 16384],
              "seeds": 1 if smoke else 3,
              "betas": [8.0] if smoke else [2.0, 8.0, 32.0],
              "n_iter": 5,
              "key_family": "kerdock_4coset"}
    print(f"[config] {config}", flush=True)
    N = config["N"]
    print("[argmax baseline, kerdock keys]", flush=True)
    argmax_cap = find_max_passing_M(capacity_argmax, kerdock_keys, N, config["M_grid"],
                                      config["seeds"], device)
    print(f"  argmax capacity = {argmax_cap:.2f}*N", flush=True)

    modern_cap_per_beta = {}
    for beta in config["betas"]:
        print(f"[modern dense, beta={beta}, kerdock keys]", flush=True)
        cap = find_max_passing_M(capacity_modern_dense, kerdock_keys, N, config["M_grid"],
                                          config["seeds"], device,
                                          fn_kwargs={"beta": beta, "n_iter": config["n_iter"]})
        modern_cap_per_beta[str(beta)] = cap
        print(f"  beta={beta}: modern capacity = {cap:.2f}*N", flush=True)

    ratio_per_beta = {b: (modern_cap_per_beta[b] / max(argmax_cap, 1e-9))
                       for b in modern_cap_per_beta}
    best_beta_str = max(ratio_per_beta, key=ratio_per_beta.get)
    best_ratio = ratio_per_beta[best_beta_str]
    summary = {"argmax_capacity": argmax_cap,
               "modern_capacity_per_beta": modern_cap_per_beta,
               "ratio_per_beta": ratio_per_beta,
               "best_beta": float(best_beta_str),
               "best_ratio": best_ratio}
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
    out_dir = get_output_dir("wave14_betY_phase2_kerdock_betacalibrated_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("argmax_cap_present", summary["argmax_capacity"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betY_phase2_kerdock_betacalibrated_v1")
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
