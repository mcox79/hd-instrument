"""Continual editing stress test v2 - 100 sequential edits, Kerdock vs correlated.

yc held Kerdock at 30 edits. v2 stress-extends to 100 to find Kerdock's
actual cliff (if any).

Pre-reg: preregs/2026-05-21_wave14yf_continual_editing_v2_stress.md
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


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 4096
M_STORED_SMOKE = 512
N_EDITS_FULL = 100
N_EDITS_SMOKE = 10
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_EDITED = yc.PASS_EDITED
PASS_KEPT = yc.PASS_KEPT
KILL_EDIT_COUNT = 10


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
        return ("CONTINUAL_V2_INCONCLUSIVE", "Missing arms.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    if not kerdock.get("per_edit_trajectory") or not correlated.get("per_edit_trajectory"):
        return ("CONTINUAL_V2_INCONCLUSIVE", "Missing trajectories.")

    k_ok, _ = yc.arm_passes(kerdock)
    c_ok, _ = yc.arm_passes(correlated)
    k_fail_edit = yc.first_fail_edit(kerdock["per_edit_trajectory"], "edited_acc",
                                       PASS_EDITED)
    if k_fail_edit is None:
        k_fail_edit = yc.first_fail_edit(kerdock["per_edit_trajectory"], "kept_acc",
                                           PASS_KEPT)
    c_fail_edit = yc.first_fail_edit(correlated["per_edit_trajectory"], "edited_acc",
                                       PASS_EDITED)
    if c_fail_edit is None:
        c_fail_edit = yc.first_fail_edit(correlated["per_edit_trajectory"], "kept_acc",
                                           PASS_KEPT)

    if (k_fail_edit is not None and k_fail_edit <= KILL_EDIT_COUNT and
        c_fail_edit is not None and c_fail_edit <= KILL_EDIT_COUNT):
        return ("CONTINUAL_V2_BOTH_FAIL_FAST",
                f"Both arms fail by edit {KILL_EDIT_COUNT}. Mechanism issue.")
    if k_ok and not c_ok:
        return ("CONTINUAL_V2_KERDOCK_HOLDS_TO_100",
                f"Kerdock arm holds across all 100 edits: min_edited="
                f"{kerdock['min_edited_acc']:.3f}, min_kept={kerdock['min_kept_acc']:.3f}. "
                f"Correlated fails at edit {c_fail_edit}. Production-scale "
                f"continual editing requires structured keys.")
    if k_ok and c_ok:
        return ("CONTINUAL_V2_CORRELATED_HOLDS",
                f"Both arms hold 100 edits. Unexpected.")
    if not k_ok:
        return (f"CONTINUAL_V2_KERDOCK_DECAYS_AT_{k_fail_edit}",
                f"Kerdock arm fails at edit {k_fail_edit}: min_edited="
                f"{kerdock['min_edited_acc']:.3f}, min_kept={kerdock['min_kept_acc']:.3f}. "
                f"Even Kerdock-keyed substrate degrades under 100 sequential edits.")
    return ("CONTINUAL_V2_INCONCLUSIVE", "Unclassified.")


def self_test_verdict():
    def mk_arm(min_edited, min_kept, fail_edited_step=None, fail_kept_step=None,
                 n_edits=100):
        traj = []
        for i in range(1, n_edits + 1):
            e = 1.0 if (fail_edited_step is None or i < fail_edited_step) else 0.5
            k = 1.0 if (fail_kept_step is None or i < fail_kept_step) else 0.5
            traj.append({"edit_step": i, "edited_acc": e, "kept_acc": k})
        return {"min_edited_acc": min_edited, "min_kept_acc": min_kept,
                "per_edit_trajectory": traj}

    cases = [
        # 1. HOLDS_TO_100
        ({"by_arm": {
            "kerdock": mk_arm(0.98, 0.99),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=2)}},
         "CONTINUAL_V2_KERDOCK_HOLDS_TO_100"),
        # 2. DECAYS at 50
        ({"by_arm": {
            "kerdock": mk_arm(0.50, 0.99, fail_edited_step=50),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=2)}},
         "CONTINUAL_V2_KERDOCK_DECAYS_AT_50"),
        # 3. BOTH_FAIL_FAST
        ({"by_arm": {
            "kerdock": mk_arm(0.50, 0.99, fail_edited_step=5),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=4)}},
         "CONTINUAL_V2_BOTH_FAIL_FAST"),
        # 4. INCONCLUSIVE
        ({}, "CONTINUAL_V2_INCONCLUSIVE"),
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

    # Use v3's Kerdock 4-coset codebook (validated for edit-then-query in yc)
    from importlib.util import spec_from_file_location, module_from_spec
    _v3p = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
    _v3s = spec_from_file_location("v3p", _v3p)
    v3 = module_from_spec(_v3s)
    _v3s.loader.exec_module(v3)

    print(f"[codebook] building 4-coset MM at N={config['N']}...", flush=True)
    codebook, info = v3.make_kerdock_4coset_codebook(config["N"], device)

    print(f"[arm=kerdock] running 100-edit stress...", flush=True)
    arm_k = yc.run_arm("kerdock", codebook, config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = yc.run_arm("correlated", None, config, device)

    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= TRAJECTORIES =========", flush=True)
    for arm_name, arm in summary["by_arm"].items():
        print(f"[{arm_name}]  min_edited={arm['min_edited_acc']:.3f}  "
              f"min_kept={arm['min_kept_acc']:.3f}", flush=True)
        # Print every 10th edit
        for entry in arm["per_edit_trajectory"][::10]:
            print(f"  step={entry['edit_step']:3d}  edited={entry['edited_acc']:.3f}  "
                  f"kept={entry['kept_acc']:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14yf_continual_editing_v2_stress_smoke")
    log_event("experiment_started", name="wave14yf_continual_editing_v2_stress", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    for arm_name in ["kerdock", "correlated"]:
        first_step = summary["by_arm"][arm_name]["per_edit_trajectory"][0]
        oracle.assert_baseline_high(f"{arm_name}_step1_edited",
                                       first_step["edited_acc"], 0.70)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yf_continual_editing_v2_stress",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yf_continual_editing_v2_stress")
    log_event("experiment_started", name="wave14yf_continual_editing_v2_stress", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yf_continual_editing_v2_stress",
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
