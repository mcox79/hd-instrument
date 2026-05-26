"""Iterative re-edit on the SAME fact - does it converge to latest v_new?

Different stress mode than continual editing (which edits N distinct facts).
Here: edit ONE fact N times in sequence, checking each edit produces the
intended retrieval.

Pre-reg: preregs/2026-05-21_wave14yv_iterative_reedit.md
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("REEDIT_INCONCLUSIVE", "Missing.")
    kerdock = arms["kerdock"]
    correlated = arms.get("correlated", {})
    k_min = kerdock.get("min_acc_along_trajectory", 0.0)
    c_min = correlated.get("min_acc_along_trajectory", 0.0)
    PASS = 0.95

    if k_min >= PASS and c_min >= PASS:
        return ("REEDIT_BOTH_HOLD",
                f"Both arms maintain >= {PASS} accuracy across all re-edits. "
                f"Kerdock min={k_min:.3f}, correlated min={c_min:.3f}.")
    if k_min >= PASS and c_min < PASS:
        return ("REEDIT_KERDOCK_HOLDS",
                f"Kerdock maintains accuracy across all re-edits (min={k_min:.3f}); "
                f"correlated drops to {c_min:.3f}. Iterative edits converge under "
                f"structured keys but drift under correlated.")
    if k_min < PASS:
        return ("REEDIT_KERDOCK_DRIFTS",
                f"Kerdock drifts under iterative re-edit: min_acc={k_min:.3f} < {PASS}. "
                f"Iterative re-edit accumulates numerical drift even with structure.")
    return ("REEDIT_INCONCLUSIVE", "Unclassified.")


def self_test_verdict():
    cases = [
        ({"by_arm": {"kerdock": {"min_acc_along_trajectory": 1.0},
                       "correlated": {"min_acc_along_trajectory": 0.30}}},
         "REEDIT_KERDOCK_HOLDS"),
        ({"by_arm": {"kerdock": {"min_acc_along_trajectory": 1.0},
                       "correlated": {"min_acc_along_trajectory": 1.0}}},
         "REEDIT_BOTH_HOLD"),
        ({"by_arm": {"kerdock": {"min_acc_along_trajectory": 0.50},
                       "correlated": {"min_acc_along_trajectory": 0.30}}},
         "REEDIT_KERDOCK_DRIFTS"),
        ({}, "REEDIT_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_arm(codebook, config, device):
    """Iterative re-edit: edit ONE fact N times, check accuracy after each."""
    N = config["N"]
    M = config["M_stored"]
    n_iters = config["n_iterations"]
    seeds = config["seeds"]

    per_seed_min = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        if codebook is not None:
            keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
        else:
            rank_L = max(2, int(M * 0.25))
            keys = v1.make_correlated_keys(M, N, rank_L, gen, device)
        v_orig = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N

        # Pick one fact to edit repeatedly
        target_idx = int(torch.randint(0, M, (1,), generator=cpu_gen).item())
        k_target = keys[target_idx]

        v_after_target = v_orig[target_idx].clone()  # current value for this fact
        v_after = v_orig.clone()
        accs_along = []
        for iter_idx in range(n_iters):
            # New v_new for this iteration
            v_new = 2.0 * (torch.rand((N,), generator=gen, device=device) > 0.5).float() - 1.0
            W = yb.edit_fact(W, k_target, v_new, 1.0, N)
            v_after[target_idx] = v_new
            v_after_target = v_new

            # Query the edited fact
            retrieved = (k_target @ W.T)
            sims = retrieved @ v_after.T
            pred = int(sims.argmax().item())
            ok = (pred == target_idx)
            accs_along.append(1.0 if ok else 0.0)

        per_seed_min.append(min(accs_along))

    return {"min_acc_along_trajectory": sum(per_seed_min) / len(per_seed_min),
            "per_seed_min": per_seed_min}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 512 if smoke else 2048,
              "n_iterations": 20 if smoke else 100,
              "seeds": [17] if smoke else [17, 23, 31, 41, 53]}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = run_arm(codebook, config, device)
    arm_c = run_arm(None, config, device)
    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
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
    out_dir = get_output_dir("wave14yv_iterative_reedit_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    k_min = summary["by_arm"]["kerdock"]["min_acc_along_trajectory"]
    oracle.assert_baseline_high("kerdock_min_smoke", k_min, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yv_iterative_reedit")
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
