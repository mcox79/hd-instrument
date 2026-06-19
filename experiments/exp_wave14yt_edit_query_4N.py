"""Edit-then-query at M=4N (full 4-coset codebook). Tests edit pipeline at 4x over-capacity.

Pre-reg: preregs/2026-05-21_wave14yt_edit_query_4N.md
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

_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)
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
    if "kerdock" not in arms or "correlated" not in arms:
        return ("EDIT_QUERY_4N_INCONCLUSIVE", "Missing arms.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    k_ok, k_fails = yb.cell_passes_per_seed(kerdock)
    c_ok, c_fails = yb.cell_passes_per_seed(correlated)
    if k_ok and c_ok:
        return ("EDIT_QUERY_4N_BOTH_PASS", f"Both pass at M=4N.")
    if k_ok and not c_ok:
        return ("EDIT_QUERY_4N_KERDOCK_PASS",
                f"Kerdock passes at M=4N (4x over-capacity). edit={kerdock['edit_argmax_acc']:.3f}. "
                f"Correlated fails: {'; '.join(c_fails)}. Edit pipeline scales to 4x over-capacity "
                f"with structured keys.")
    if not k_ok:
        return ("EDIT_QUERY_4N_KERDOCK_FAILS",
                f"Kerdock fails at M=4N: {'; '.join(k_fails)}.")
    return ("EDIT_QUERY_4N_INCONCLUSIVE", "Unclassified.")


def self_test_verdict():
    def mk(args):
        return {"edit_argmax_acc": args.get("edit_argmax", 0.99),
                "kept_argmax_acc": args.get("kept_argmax", 0.99),
                "edit_paraphrase_acc_h8": args.get("edit_para", 0.96),
                "kept_paraphrase_acc_h8": args.get("kept_para", 0.98),
                "side_effect_rate": args.get("side", 0.01)}
    cases = [
        ({"by_arm": {"kerdock": mk({}), "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_4N_KERDOCK_PASS"),
        ({"by_arm": {"kerdock": mk({}), "correlated": mk({})}},
         "EDIT_QUERY_4N_BOTH_PASS"),
        ({"by_arm": {"kerdock": mk({"edit_argmax": 0.40}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_4N_KERDOCK_FAILS"),
        ({}, "EDIT_QUERY_4N_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 4096 if smoke else 16384,  # M = 4N
              "n_edit": 5 if smoke else 30,
              "n_kept": 20 if smoke else 100,
              "hamming_radii": [8] if smoke else [4, 8, 16],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53],
              "alpha": 1.0}
    print(f"[config] {config}", flush=True)
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = yb.run_arm("kerdock", codebook, config, device)
    arm_c = yb.run_arm("correlated", None, config, device)
    summary = {"N": config["N"], "by_arm": {"kerdock": arm_k, "correlated": arm_c}}
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
    out_dir = get_output_dir("wave14yt_edit_query_4N_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    k_kept = summary["by_arm"]["kerdock"]["kept_argmax_acc"]
    oracle.assert_baseline_high("kerdock_kept_smoke_4N", k_kept, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yt_edit_query_4N")
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
