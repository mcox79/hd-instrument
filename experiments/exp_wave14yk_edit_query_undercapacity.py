"""Edit-then-query at M=N/2 (under-capacity baseline).

Pre-reg: preregs/2026-05-21_wave14yk_edit_query_undercapacity.md
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


_yb_path = REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py"
spec_yb = importlib.util.spec_from_file_location("yb", _yb_path)
yb = importlib.util.module_from_spec(spec_yb)
spec_yb.loader.exec_module(yb)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec_v3 = importlib.util.spec_from_file_location("v3", _v3_path)
v3 = importlib.util.module_from_spec(spec_v3)
spec_v3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 2048  # = N/2
M_STORED_SMOKE = 512  # = N/2 at smoke
N_EDIT_FULL = 30
N_EDIT_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 20
HAMMING_RADII_FULL = [4, 8, 16]
HAMMING_RADII_SMOKE = [8]
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing: {required - set(d.keys())}")


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("EDIT_QUERY_UC_INCONCLUSIVE", "Missing arms.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    k_ok, k_fails = yb.cell_passes_per_seed(kerdock)
    c_ok, c_fails = yb.cell_passes_per_seed(correlated)

    if k_ok and c_ok:
        return ("EDIT_QUERY_UC_BOTH_PASS",
                f"Both arms pass at M=N/2. Kerdock edit={kerdock['edit_argmax_acc']:.3f}, "
                f"correlated edit={correlated['edit_argmax_acc']:.3f}.")
    if not k_ok:
        return ("EDIT_QUERY_UC_KERDOCK_FAILS",
                f"Kerdock fails at M=N/2 (regression): {'; '.join(k_fails)}.")
    return ("EDIT_QUERY_UC_CORRELATED_FAILS",
            f"Correlated fails at M=N/2 (under-capacity). Failure mode "
            f"kicks in below M=N: {'; '.join(c_fails)}.")


def self_test_verdict():
    def mk(args):
        return {"edit_argmax_acc": args.get("edit_argmax", 0.99),
                "kept_argmax_acc": args.get("kept_argmax", 0.99),
                "edit_paraphrase_acc_h8": args.get("edit_para", 0.96),
                "kept_paraphrase_acc_h8": args.get("kept_para", 0.98),
                "side_effect_rate": args.get("side", 0.01)}

    cases = [
        ({"by_arm": {"kerdock": mk({}), "correlated": mk({})}},
         "EDIT_QUERY_UC_BOTH_PASS"),
        ({"by_arm": {"kerdock": mk({"edit_argmax": 0.40}),
                       "correlated": mk({})}},
         "EDIT_QUERY_UC_KERDOCK_FAILS"),
        ({"by_arm": {"kerdock": mk({}),
                       "correlated": mk({"edit_argmax": 0.40})}},
         "EDIT_QUERY_UC_CORRELATED_FAILS"),
        ({}, "EDIT_QUERY_UC_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_edit": N_EDIT_SMOKE if smoke else N_EDIT_FULL,
        "n_kept": N_KEPT_PROBE_SMOKE if smoke else N_KEPT_PROBE_FULL,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alpha": ALPHA,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = yb.run_arm("kerdock", codebook, config, device)
    arm_c = yb.run_arm("correlated", None, config, device)
    summary = {"N": config["N"], "by_arm": {"kerdock": arm_k, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start
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
    out_dir = get_output_dir("wave14yk_edit_query_undercapacity_smoke")
    log_event("experiment_started", name="wave14yk_edit_query_undercapacity", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    k_kept = summary["by_arm"]["kerdock"]["kept_argmax_acc"]
    oracle.assert_baseline_high("kerdock_kept_smoke_uc", k_kept, 0.70)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yk_edit_query_undercapacity",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yk_edit_query_undercapacity")
    log_event("experiment_started", name="wave14yk_edit_query_undercapacity", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yk_edit_query_undercapacity",
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
