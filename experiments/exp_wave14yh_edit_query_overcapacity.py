"""Edit-then-query at over-capacity M=2N with Kerdock vs correlated.

yb tested at M=N=4096 (within v1 envelope) and got BOTH_PASS. yh extends
to M=2N=8192 to test if the edit pipeline holds in the over-capacity
regime where Bet 2 v2 validated Kerdock multi-probe protection.

Pre-reg: preregs/2026-05-21_wave14yh_edit_query_overcapacity.md
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
M_STORED_FULL = 8192  # = 2N
M_STORED_SMOKE = 2048  # = 2N at smoke
N_EDIT_FULL = 30
N_EDIT_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 20
HAMMING_RADII_FULL = [4, 8, 16]
HAMMING_RADII_SMOKE = [8]
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_EDIT_ARGMAX = yb.PASS_EDIT_ARGMAX
PASS_KEPT_ARGMAX = yb.PASS_KEPT_ARGMAX
PASS_EDIT_PARAPHRASE = yb.PASS_EDIT_PARAPHRASE
PASS_KEPT_PARAPHRASE = yb.PASS_KEPT_PARAPHRASE
PASS_SIDE_EFFECT_MAX = yb.PASS_SIDE_EFFECT_MAX


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
        return ("EDIT_QUERY_OC_INCONCLUSIVE", "Missing arms.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    if not kerdock or not correlated:
        return ("EDIT_QUERY_OC_INCONCLUSIVE", "Empty arms.")

    k_ok, k_fails = yb.cell_passes_per_seed(kerdock)
    c_ok, c_fails = yb.cell_passes_per_seed(correlated)

    edits_ok = kerdock["edit_argmax_acc"] >= PASS_EDIT_ARGMAX
    kept_ok = kerdock["kept_argmax_acc"] >= PASS_KEPT_ARGMAX
    para_ok = (kerdock.get("edit_paraphrase_acc_h8", 0.0) >= PASS_EDIT_PARAPHRASE
                and kerdock.get("kept_paraphrase_acc_h8", 0.0) >= PASS_KEPT_PARAPHRASE)

    if k_ok and c_ok:
        return ("EDIT_QUERY_OC_BOTH_PASS",
                f"Both arms pass at M=2N. Kerdock edit={kerdock['edit_argmax_acc']:.3f}, "
                f"correlated edit={correlated['edit_argmax_acc']:.3f}.")
    if k_ok and not c_ok:
        return ("EDIT_QUERY_OC_KERDOCK_PASS",
                f"Kerdock arm passes all 5 criteria at M=2N. edit_argmax="
                f"{kerdock['edit_argmax_acc']:.3f}, kept_argmax={kerdock['kept_argmax_acc']:.3f}, "
                f"edit_para_h8={kerdock.get('edit_paraphrase_acc_h8', 0.0):.3f}, "
                f"kept_para_h8={kerdock.get('kept_paraphrase_acc_h8', 0.0):.3f}, "
                f"side_effect={kerdock.get('side_effect_rate', 0.0):.3f}. "
                f"Correlated arm fails: {'; '.join(c_fails)}. "
                f"Edit pipeline extends to over-capacity with structured keys.")
    if not k_ok:
        if edits_ok and kept_ok and not para_ok:
            return ("EDIT_QUERY_OC_KERDOCK_PARAPHRASE_FAIL",
                    f"Kerdock passes edit/kept argmax but paraphrase fails: "
                    f"edit_para_h8={kerdock.get('edit_paraphrase_acc_h8', 0.0):.3f}, "
                    f"kept_para_h8={kerdock.get('kept_paraphrase_acc_h8', 0.0):.3f}.")
        return ("EDIT_QUERY_OC_KERDOCK_FAILS",
                f"Kerdock arm fails at M=2N: {'; '.join(k_fails)}. "
                f"Edit pipeline doesn't extend to over-capacity even with structure.")
    return ("EDIT_QUERY_OC_INCONCLUSIVE", "Unclassified.")


def self_test_verdict():
    def mk(args):
        return {"edit_argmax_acc": args.get("edit_argmax", 0.99),
                "kept_argmax_acc": args.get("kept_argmax", 0.99),
                "edit_paraphrase_acc_h8": args.get("edit_para", 0.96),
                "kept_paraphrase_acc_h8": args.get("kept_para", 0.98),
                "side_effect_rate": args.get("side", 0.01)}

    cases = [
        ({"by_arm": {"kerdock": mk({}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_OC_KERDOCK_PASS"),
        ({"by_arm": {"kerdock": mk({}), "correlated": mk({})}},
         "EDIT_QUERY_OC_BOTH_PASS"),
        ({"by_arm": {"kerdock": mk({"edit_argmax": 0.40}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_OC_KERDOCK_FAILS"),
        ({"by_arm": {"kerdock": mk({"edit_para": 0.50}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_OC_KERDOCK_PARAPHRASE_FAIL"),
        ({}, "EDIT_QUERY_OC_INCONCLUSIVE"),
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

    print(f"[codebook] building 4-coset MM at N={config['N']}...", flush=True)
    codebook, info = v3.make_kerdock_4coset_codebook(config["N"], device)

    print(f"[arm=kerdock] running edit-then-query at M=2N...", flush=True)
    arm_k = yb.run_arm("kerdock", codebook, config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = yb.run_arm("correlated", None, config, device)

    summary = {"N": config["N"], "by_arm": {"kerdock": arm_k, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm in summary["by_arm"].items():
        paras = " ".join(f"e_h{h}={arm[f'edit_paraphrase_acc_h{h}']:.3f}"
                          f" k_h{h}={arm[f'kept_paraphrase_acc_h{h}']:.3f}"
                          for h in config["hamming_radii"])
        print(f"  [{arm_name}]  edit_argmax={arm['edit_argmax_acc']:.3f}  "
              f"kept_argmax={arm['kept_argmax_acc']:.3f}  "
              f"side_effect={arm['side_effect_rate']:.3f}  {paras}", flush=True)
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
    out_dir = get_output_dir("wave14yh_edit_query_overcapacity_smoke")
    log_event("experiment_started", name="wave14yh_edit_query_overcapacity", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    k_kept = summary["by_arm"]["kerdock"]["kept_argmax_acc"]
    oracle.assert_baseline_high("kerdock_kept_smoke_oc", k_kept, 0.60)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yh_edit_query_overcapacity",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yh_edit_query_overcapacity")
    log_event("experiment_started", name="wave14yh_edit_query_overcapacity", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yh_edit_query_overcapacity",
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
