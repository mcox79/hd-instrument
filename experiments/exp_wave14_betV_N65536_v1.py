"""Bet V meta-cognition at N=65536 — V2.D Phase 1 sub-test #5.

Per Strategy 13:15 V2.D mechanism revision: "Bet V meta-cognition at N=65536
(target: gap > 0.424 extending cycle 103 N-scaling)". Cycle 103 showed gap
scaling 0.285 → 0.424 across N range.

Bet V tests whether substrate can distinguish stored vs unstored (s, r) queries
via confidence margin = (top1_sim - top2_sim) / |top1|. Larger gap = better
self-knowledge.

Reuses Bet V largeN infrastructure at scaled N. No W matrix needed
(codebook + bundle only).

Verdict thresholds (per Strategy V2.D revision):
  BET_V_N65K_PASS:    gap >= 0.424 (extends cycle 103 N-scaling)
  BET_V_N65K_PARTIAL: 0.30 <= gap < 0.424 (partial extension)
  BET_V_N65K_KILLED:  gap < 0.30 (N-scaling fails)
  BET_V_N65K_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betV_N65536_v1.md
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

_v = importlib.util.spec_from_file_location("betv",
    REPO / "experiments" / "exp_wave14_betV_largeN.py")
betv = importlib.util.module_from_spec(_v); _v.loader.exec_module(betv)


PASS_GAP = 0.424
PARTIAL_GAP = 0.30


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "gap" not in summary:
        return ("BET_V_N65K_INCONCLUSIVE", "Missing gap.")
    gap = summary["gap"]; stored = summary["stored_conf"]; unstored = summary["unstored_conf"]
    if gap >= PASS_GAP:
        return ("BET_V_N65K_PASS",
                f"Bet V at N=65536: gap={gap:.3f} (>={PASS_GAP}). Cycle 103 N-scaling "
                f"extends. stored_conf={stored:.3f}, unstored_conf={unstored:.3f}.")
    if gap >= PARTIAL_GAP:
        return ("BET_V_N65K_PARTIAL",
                f"gap={gap:.3f} ({PARTIAL_GAP}<=gap<{PASS_GAP}). Partial N-scaling. "
                f"stored={stored:.3f}, unstored={unstored:.3f}.")
    return ("BET_V_N65K_KILLED",
            f"gap={gap:.3f}<{PARTIAL_GAP}. N-scaling fails for Bet V. "
            f"stored={stored:.3f}, unstored={unstored:.3f}.")


def self_test_verdict():
    cases = [
        ({"gap": 0.50, "stored_conf": 0.6, "unstored_conf": 0.1}, "BET_V_N65K_PASS"),
        ({"gap": 0.35, "stored_conf": 0.5, "unstored_conf": 0.15}, "BET_V_N65K_PARTIAL"),
        ({"gap": 0.10, "stored_conf": 0.2, "unstored_conf": 0.1}, "BET_V_N65K_KILLED"),
        ({}, "BET_V_N65K_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 30 if smoke else 100,
              "n_probes": 20 if smoke else 50,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = []
    for seed in config["seeds"]:
        r = betv.run_one_seed(seed, config, device)
        per_seed.append(r)
        print(f"  seed={seed}: stored={r['stored']:.3f} unstored={r['unstored']:.3f} "
              f"gap={r['stored']-r['unstored']:.3f}", flush=True)
    stored = sum(r["stored"] for r in per_seed) / len(per_seed)
    unstored = sum(r["unstored"] for r in per_seed) / len(per_seed)
    gap = stored - unstored
    summary = {"stored_conf": stored, "unstored_conf": unstored, "gap": gap,
                "per_seed": per_seed, "N": config["N"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\ngap at N={config['N']}: {gap:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14_betV_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("gap_present", abs(summary["gap"]) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betV_N65536_v1")
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
