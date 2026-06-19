"""Lane C compliance-audit FULL multi-seed — upgrade smoke PERFECT to FULL per Strategy 15:55.

Per `strategy_request_to_exp_dev_lane_C_compliance_FULL_2026-05-22.md`: cycle 86
smoke ran LANE_C_PRIMITIVES_COMPOSE PERFECT (delete_leak=0, edit_acc=1.0,
kept_acc=1.0, side_effect=0, ECE=0). Strategy oversight: no FULL queued.
META Phase 1 wedge + Product Demo 2 dependency.

Per cycle 102 smoke-not-predictive 7-anchor precedent: smoke perfect is NOT
predictive of FULL. Need 5-seed multi-seed verification.

Verdict (per Strategy request):
  LANE_C_FULL_PASS:    all 5 probes pass across all 5 seeds (smoke PERFECT reproduces)
  LANE_C_FULL_PARTIAL: >= 3 of 5 probes pass on aggregate; some regress
  LANE_C_FULL_KILLED:  <= 2 of 5 probes pass on aggregate
  LANE_C_FULL_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_lane_C_compliance_audit_FULL_v1.md
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

_lc = importlib.util.spec_from_file_location("lc",
    REPO / "experiments" / "exp_wave14_lane_C_compliance_audit_smoke_v1.py")
lc = importlib.util.module_from_spec(_lc); _lc.loader.exec_module(lc)


PASS_MIRAGE_LEAK = 0.05
PASS_KEPT = 0.90
PASS_ECE = 0.10
PASS_SIDE_EFFECT = 0.05


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def per_seed_probes_pass(s):
    """Returns dict of {probe: bool_pass}."""
    return {
        "delete_leak": s["delete_leak_max"] <= PASS_MIRAGE_LEAK,
        "edit_acc": s["edit_acc"] >= PASS_KEPT,
        "kept_acc": s["kept_acc"] >= PASS_KEPT,
        "side_effect": s["side_effect_rate"] <= PASS_SIDE_EFFECT,
        "ece": s["ece_post"] <= PASS_ECE,
    }


def compute_verdict(summary):
    if "per_seed" not in summary:
        return ("LANE_C_FULL_INCONCLUSIVE", "Missing per_seed.")
    per_seed = summary["per_seed"]
    n_seeds = len(per_seed)
    if n_seeds < 3:
        return ("LANE_C_FULL_INCONCLUSIVE", f"Only {n_seeds} seeds; need >=3.")
    # Count probes that pass across ALL seeds
    probe_names = ["delete_leak", "edit_acc", "kept_acc", "side_effect", "ece"]
    all_seed_pass_per_probe = {p: True for p in probe_names}
    any_seed_pass_per_probe = {p: 0 for p in probe_names}
    for seed_data in per_seed:
        passes = per_seed_probes_pass(seed_data)
        for p in probe_names:
            if not passes[p]:
                all_seed_pass_per_probe[p] = False
            else:
                any_seed_pass_per_probe[p] += 1
    n_robust = sum(1 for p in probe_names if all_seed_pass_per_probe[p])
    if n_robust == 5:
        return ("LANE_C_FULL_PASS",
                f"All 5 probes pass across all {n_seeds} seeds. Smoke PERFECT reproduces "
                f"at FULL. Lane C is FULL-grounded for substrate-product Demo 2. "
                f"all_seed_pass={all_seed_pass_per_probe}.")
    if n_robust >= 3:
        return ("LANE_C_FULL_PARTIAL",
                f"{n_robust}/5 probes robust across all seeds. "
                f"all_seed_pass={all_seed_pass_per_probe}. any_seed_pass={any_seed_pass_per_probe}. "
                f"Smoke PERFECT partially reproduces.")
    return ("LANE_C_FULL_KILLED",
            f"{n_robust}/5 probes robust across all seeds. "
            f"all_seed_pass={all_seed_pass_per_probe}. Smoke PERFECT does NOT reproduce — "
            f"8th smoke-not-predictive anchor.")


def self_test_verdict():
    perfect_seed = {"delete_leak_max": 0.0, "edit_acc": 1.0, "kept_acc": 1.0,
                     "side_effect_rate": 0.0, "ece_post": 0.0}
    bad_seed = {"delete_leak_max": 0.5, "edit_acc": 0.3, "kept_acc": 0.4,
                 "side_effect_rate": 0.5, "ece_post": 0.5}
    mid_seed = {"delete_leak_max": 0.0, "edit_acc": 1.0, "kept_acc": 1.0,
                 "side_effect_rate": 0.5, "ece_post": 0.5}
    cases = [
        ({"per_seed": [perfect_seed, perfect_seed, perfect_seed, perfect_seed, perfect_seed]}, "LANE_C_FULL_PASS"),
        ({"per_seed": [perfect_seed, perfect_seed, mid_seed, mid_seed, mid_seed]}, "LANE_C_FULL_PARTIAL"),
        ({"per_seed": [bad_seed, bad_seed, bad_seed, bad_seed, bad_seed]}, "LANE_C_FULL_KILLED"),
        ({}, "LANE_C_FULL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_facts": 30 if smoke else 100,
              "n_edits": 10 if smoke else 50,
              "n_deletes": 8 if smoke else 30,
              "seeds": [17, 23] if smoke else [17, 23, 31, 41, 53]}
    per_seed = []
    for seed in config["seeds"]:
        r = lc.run_one_seed(seed, config, device)
        per_seed.append(r)
        print(f"  seed={seed}: leak={r['delete_leak_max']:.4f} edit={r['edit_acc']:.3f} "
              f"kept={r['kept_acc']:.3f} side={r['side_effect_rate']:.4f} ECE={r['ece_post']:.4f}",
              flush=True)
    summary = {"per_seed": per_seed,
                "n_seeds": len(per_seed),
                "agg_delete_leak_max": max(r["delete_leak_max"] for r in per_seed),
                "agg_edit_acc_min": min(r["edit_acc"] for r in per_seed),
                "agg_kept_acc_min": min(r["kept_acc"] for r in per_seed),
                "agg_side_effect_max": max(r["side_effect_rate"] for r in per_seed),
                "agg_ece_max": max(r["ece_post"] for r in per_seed)}
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
    out_dir = get_output_dir("wave14_lane_C_compliance_audit_FULL_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("seeds_collected", float(summary["n_seeds"]), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_C_compliance_audit_FULL_v1")
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
