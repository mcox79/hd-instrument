"""Continual editing at 200 edits - find Kerdock's cliff if any.

Trivial extension of yf with N_EDITS=200.

Pre-reg: preregs/2026-05-21_wave14yj_continual_editing_v3_200.md
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


_yc_path = REPO / "experiments" / "exp_wave14yc_continual_editing_kerdock.py"
spec_yc = importlib.util.spec_from_file_location("yc", _yc_path)
yc = importlib.util.module_from_spec(spec_yc)
spec_yc.loader.exec_module(yc)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec_v3 = importlib.util.spec_from_file_location("v3", _v3_path)
v3 = importlib.util.module_from_spec(spec_v3)
spec_v3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 4096
M_STORED_SMOKE = 512
N_EDITS_FULL = 200
N_EDITS_SMOKE = 10
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_EDITED = yc.PASS_EDITED
PASS_KEPT = yc.PASS_KEPT
KILL_EDIT_COUNT = 20


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
        return ("CONTINUAL_V3_INCONCLUSIVE", "Missing arms.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    if not kerdock.get("per_edit_trajectory"):
        return ("CONTINUAL_V3_INCONCLUSIVE", "Missing trajectories.")

    k_ok, _ = yc.arm_passes(kerdock)
    c_ok, _ = yc.arm_passes(correlated)
    k_fail = yc.first_fail_edit(kerdock["per_edit_trajectory"], "edited_acc", PASS_EDITED) or \
             yc.first_fail_edit(kerdock["per_edit_trajectory"], "kept_acc", PASS_KEPT)
    c_fail = yc.first_fail_edit(correlated["per_edit_trajectory"], "edited_acc", PASS_EDITED) or \
             yc.first_fail_edit(correlated["per_edit_trajectory"], "kept_acc", PASS_KEPT)

    if (k_fail is not None and k_fail <= KILL_EDIT_COUNT and
        c_fail is not None and c_fail <= KILL_EDIT_COUNT):
        return ("CONTINUAL_V3_BOTH_FAIL",
                f"Both arms fail early. Mechanism issue.")
    if k_ok:
        return ("CONTINUAL_V3_HOLDS_TO_200",
                f"Kerdock holds 200 edits: min_edited={kerdock['min_edited_acc']:.3f}, "
                f"min_kept={kerdock['min_kept_acc']:.3f}. Correlated fails at edit "
                f"{c_fail}. Substrate continual editing is unbounded with structured keys.")
    return (f"CONTINUAL_V3_DECAYS_AT_{k_fail}",
            f"Kerdock arm decays at edit {k_fail}: min_edited="
            f"{kerdock['min_edited_acc']:.3f}, min_kept={kerdock['min_kept_acc']:.3f}.")


def self_test_verdict():
    def mk_arm(min_e, min_k, fail_e=None, fail_k=None, n=200):
        traj = []
        for i in range(1, n + 1):
            e = 1.0 if (fail_e is None or i < fail_e) else 0.5
            k = 1.0 if (fail_k is None or i < fail_k) else 0.5
            traj.append({"edit_step": i, "edited_acc": e, "kept_acc": k})
        return {"min_edited_acc": min_e, "min_kept_acc": min_k, "per_edit_trajectory": traj}

    cases = [
        ({"by_arm": {"kerdock": mk_arm(0.98, 0.99),
                       "correlated": mk_arm(0.5, 0.99, fail_e=2)}},
         "CONTINUAL_V3_HOLDS_TO_200"),
        ({"by_arm": {"kerdock": mk_arm(0.5, 0.99, fail_e=150),
                       "correlated": mk_arm(0.5, 0.99, fail_e=2)}},
         "CONTINUAL_V3_DECAYS_AT_150"),
        ({"by_arm": {"kerdock": mk_arm(0.5, 0.99, fail_e=10),
                       "correlated": mk_arm(0.5, 0.99, fail_e=10)}},
         "CONTINUAL_V3_BOTH_FAIL"),
        ({}, "CONTINUAL_V3_INCONCLUSIVE"),
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
        "n_edits": N_EDITS_SMOKE if smoke else N_EDITS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alpha": ALPHA,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building 4-coset MM at N={config['N']}...", flush=True)
    codebook, info = v3.make_kerdock_4coset_codebook(config["N"], device)

    print(f"[arm=kerdock] running 200-edit stress...", flush=True)
    arm_k = yc.run_arm("kerdock", codebook, config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = yc.run_arm("correlated", None, config, device)

    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
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
    out_dir = get_output_dir("wave14yj_continual_editing_v3_200_smoke")
    log_event("experiment_started", name="wave14yj_continual_editing_v3_200", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    for arm_name in ["kerdock", "correlated"]:
        first_step = summary["by_arm"][arm_name]["per_edit_trajectory"][0]
        oracle.assert_baseline_high(f"{arm_name}_step1_edited",
                                       first_step["edited_acc"], 0.70)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yj_continual_editing_v3_200",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yj_continual_editing_v3_200")
    log_event("experiment_started", name="wave14yj_continual_editing_v3_200", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yj_continual_editing_v3_200",
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
