"""Bet 2 v8 - 32-coset retry with correlated arm capped to avoid OOM.

zc failed: correlated arm OOM at M=131072 (rank-L weights matrix too large).
Kerdock arm completed. v8 runs Kerdock at full M sweep, correlated capped at
M<=32768 (8N). Contrast still holds for the smaller-M correlated comparison.

Pre-reg: preregs/2026-05-21_wave14zp_kerdock_v8_32coset_retry.md
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

_zc = importlib.util.spec_from_file_location("zc", REPO / "experiments" / "exp_wave14zc_erase_kerdock_v7_32coset.py")
zc = importlib.util.module_from_spec(_zc); _zc.loader.exec_module(zc)
_v4 = importlib.util.spec_from_file_location("v4", REPO / "experiments" / "exp_wave14ya_erase_kerdock_v4.py")
v4 = importlib.util.module_from_spec(_v4); _v4.loader.exec_module(v4)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    v_in, msg = zc.compute_verdict(summary)
    # Rename prefix V7 -> V8
    if v_in.startswith("KERDOCK_V7_"):
        return ("KERDOCK_V8_" + v_in[len("KERDOCK_V7_"):], msg)
    return (v_in, msg)


def self_test_verdict():
    zc.self_test_verdict()
    print(f"v8 inherits zc verdict tree", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored_list": [4096, 8192] if smoke else [16384, 32768, 65536, 98304, 131072],
              "M_stored_list_corr": [4096, 8192] if smoke else [16384, 32768],
              "n_erase": 5 if smoke else 30,
              "n_kept_probe": 10 if smoke else 100,
              "n_paraphrase": 20,
              "hamming_radii": [8] if smoke else [4, 8, 16],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53],
              "alpha": 1.0, "num_cosets": zc.NUM_COSETS}
    print(f"[config] {config}", flush=True)
    codebook, info = zc.make_kerdock_32coset_codebook(config["N"], device)
    print(f"[codebook] size={codebook.shape}, info={info}", flush=True)
    arm_k = v4.run_arm("kerdock", codebook, config["M_stored_list"], config, device)
    arm_c = v4.run_arm("correlated", None, config["M_stored_list_corr"], config, device)
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
    out_dir = get_output_dir("wave14zp_kerdock_v8_32coset_retry_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zp_kerdock_v8_32coset_retry")
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
