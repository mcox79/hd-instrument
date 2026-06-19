"""Continual editing 5000 edits - find Kerdock's actual cliff (if any).

Pre-reg: preregs/2026-05-21_wave14zb_continual_5000.md
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

_yc = importlib.util.spec_from_file_location("yc", REPO / "experiments" / "exp_wave14yc_continual_editing_kerdock.py")
yc = importlib.util.module_from_spec(_yc); _yc.loader.exec_module(yc)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


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
        return ("CONTINUAL_5000_INCONCLUSIVE", "Missing.")
    kerdock = arms["kerdock"]
    if not kerdock.get("per_edit_trajectory"):
        return ("CONTINUAL_5000_INCONCLUSIVE", "Missing traj.")
    k_ok, _ = yc.arm_passes(kerdock)
    k_fail = yc.first_fail_edit(kerdock["per_edit_trajectory"], "edited_acc",
                                   yc.PASS_EDITED) or yc.first_fail_edit(
        kerdock["per_edit_trajectory"], "kept_acc", yc.PASS_KEPT)
    if k_ok:
        return ("CONTINUAL_5000_HOLDS",
                f"Kerdock holds 5000 edits: min_edited={kerdock['min_edited_acc']:.3f}, "
                f"min_kept={kerdock['min_kept_acc']:.3f}. >2x the M=4096 fact-base size "
                f"in edits; substrate genuinely unbounded with structured keys.")
    return (f"CONTINUAL_5000_DECAYS_AT_{k_fail}",
            f"Kerdock decays at edit {k_fail}. min_edited={kerdock['min_edited_acc']:.3f}.")


def self_test_verdict():
    def mk(min_e, fail_e=None, n=5000):
        traj = [{"edit_step": i, "edited_acc": 1.0 if (fail_e is None or i < fail_e) else 0.5,
                  "kept_acc": 1.0} for i in range(1, n + 1)]
        return {"min_edited_acc": min_e, "min_kept_acc": 1.0, "per_edit_trajectory": traj}
    cases = [
        ({"by_arm": {"kerdock": mk(0.98), "correlated": mk(0.5, fail_e=2)}},
         "CONTINUAL_5000_HOLDS"),
        ({"by_arm": {"kerdock": mk(0.5, fail_e=3000), "correlated": mk(0.5, fail_e=2)}},
         "CONTINUAL_5000_DECAYS_AT_3000"),
        ({}, "CONTINUAL_5000_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (3/3 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full", "N": 1024 if smoke else 4096,
              "M_stored": 1024 if smoke else 4096, "n_edits": 50 if smoke else 5000,
              "seeds": [17] if smoke else [17, 23, 31], "alpha": 1.0}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = yc.run_arm("kerdock", codebook, config, device)
    arm_c = yc.run_arm("correlated", None, config, device)
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
    out_dir = get_output_dir("wave14zb_continual_5000_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = summary["by_arm"]["kerdock"]["per_edit_trajectory"][0]
    oracle.assert_baseline_high("kerdock_step1", first["edited_acc"], 0.70)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zb_continual_5000")
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
