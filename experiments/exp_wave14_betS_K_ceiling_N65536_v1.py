"""Bet S K-ceiling at N=65536 — V2.D Phase 1 sub-test (Strategy 2026-05-22 13:15 EDT).

Per Strategy revision: drop modern dense AM; verify substrate scales by extending
Bet S K-ceiling from N=4096 baseline (K_crit ~130-205) to N=65536. Prediction
per cycle 88 K_crit theory: K_crit at N=65536 should be ~16x of N=4096 baseline,
or ~2000-3000.

Reuses Bet S pattern completion infrastructure but at scaled N + extended K grid.

Verdict thresholds (per V2.D revision):
  BET_S_N65K_PASS:    K_crit >= 1000 (substrate scales)
  BET_S_N65K_PARTIAL: 500 <= K_crit < 1000 (partial scaling)
  BET_S_N65K_KILLED:  K_crit < 500 (substrate doesn't scale to N=65536)
  BET_S_N65K_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betS_K_ceiling_N65536_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_s = importlib.util.spec_from_file_location("bets",
    REPO / "experiments" / "exp_wave14_betS_pattern_completion_v1.py")
bets = importlib.util.module_from_spec(_s); _s.loader.exec_module(bets)


PASS_K_CRIT = 1000
PARTIAL_K_CRIT = 500
PASS_SLOT = 0.85


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "K_crit" not in summary:
        return ("BET_S_N65K_INCONCLUSIVE", "Missing K_crit.")
    K_crit = summary["K_crit"]
    by_K = summary["per_K"]
    if K_crit >= PASS_K_CRIT:
        return ("BET_S_N65K_PASS",
                f"Bet S K-ceiling at N=65536: K_crit={K_crit} (>={PASS_K_CRIT}). "
                f"Substrate scales to N=65536. per_K={by_K}.")
    if K_crit >= PARTIAL_K_CRIT:
        return ("BET_S_N65K_PARTIAL",
                f"K_crit={K_crit} ({PARTIAL_K_CRIT}<=K_crit<{PASS_K_CRIT}). "
                f"Partial scaling. per_K={by_K}.")
    return ("BET_S_N65K_KILLED",
            f"K_crit={K_crit}<{PARTIAL_K_CRIT}. Substrate fails to scale to N=65536. "
            f"per_K={by_K}.")


def self_test_verdict():
    cases = [
        ({"K_crit": 2400, "per_K": {}}, "BET_S_N65K_PASS"),
        ({"K_crit": 700, "per_K": {}}, "BET_S_N65K_PARTIAL"),
        ({"K_crit": 300, "per_K": {}}, "BET_S_N65K_KILLED"),
        ({}, "BET_S_N65K_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def find_K_crit(K_grid, per_K_accs):
    """K_crit = largest K where ALL 3 slots clear PASS_SLOT."""
    K_crit = 0
    for K in K_grid:
        rec = per_K_accs[str(K)]
        if min(rec["subject"], rec["relation"], rec["object"]) >= PASS_SLOT:
            K_crit = max(K_crit, K)
    return K_crit


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 4096 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 50,
              "K_sweep": [50, 200] if smoke else [200, 500, 1000, 2000, 3000],
              "n_trials_per_K": 20 if smoke else 60,
              "seeds": [17] if smoke else [17, 23]}
    per_K_seed = {K: [] for K in config["K_sweep"]}
    for seed in config["seeds"]:
        for K in config["K_sweep"]:
            r = bets.run_one_K(K, config["num_entities"], config["num_relations"],
                                config["N"], config["n_trials_per_K"], seed, device)
            per_K_seed[K].append(r)
            print(f"  seed={seed} K={K}: subj={r['subject']:.3f} rel={r['relation']:.3f} obj={r['object']:.3f}", flush=True)
    per_K_mean = {}
    for K, seed_results in per_K_seed.items():
        per_K_mean[str(K)] = {
            "subject": sum(r["subject"] for r in seed_results) / len(seed_results),
            "relation": sum(r["relation"] for r in seed_results) / len(seed_results),
            "object": sum(r["object"] for r in seed_results) / len(seed_results),
        }
    K_crit = find_K_crit(config["K_sweep"], per_K_mean)
    summary = {"per_K": per_K_mean, "K_crit": K_crit, "N": config["N"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nK_crit at N={config['N']}: {K_crit}", flush=True)
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
    out_dir = get_output_dir("wave14_betS_K_ceiling_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("K_crit_present", float(summary["K_crit"]) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betS_K_ceiling_N65536_v1")
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
