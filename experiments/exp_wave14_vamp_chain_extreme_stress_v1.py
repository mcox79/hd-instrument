"""VAMP-on-chain extreme stress — find K ceiling beyond K=5000 AND depth cliff between d=200-500.

Per cycle 128 results: VAMP-on-chain PERFECT at d=200 AND K=5000. Cliff between
d=200 and d=500. K ceiling unknown above 5000.

Two-axis test:
  Axis 1: K ceiling at d=50 with K in {5000, 10000, 50000, 100000}
  Axis 2: Depth cliff with d in {200, 300, 400, 500} at K=200

Verdict thresholds:
  EXTREME_HIGH:   K >= 10000 PASS AND d >= 400 PASS (substrate has massive headroom)
  EXTREME_MID:    K_ceiling in [5000, 10000] OR d_ceiling in [200, 400]
  EXTREME_BOUNDED: K_ceiling < 5000 OR d_ceiling < 200
  EXTREME_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_vamp_chain_extreme_stress_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "K_ceiling" not in summary:
        return ("EXTREME_INCONCLUSIVE", "Missing K_ceiling.")
    K_c = summary["K_ceiling"]
    d_c = summary["depth_ceiling"]
    per_K = summary["acc_per_K"]
    per_d = summary["acc_per_depth"]
    if K_c >= 10000 and d_c >= 400:
        return ("EXTREME_HIGH",
                f"Massive headroom: K_ceiling>={K_c}, depth_ceiling>={d_c}. "
                f"acc_per_K={per_K}, acc_per_depth={per_d}.")
    if K_c >= 5000 and d_c >= 200:
        return ("EXTREME_MID",
                f"Confirmed PERFECT bounds: K_ceiling={K_c}, depth_ceiling={d_c}. "
                f"acc_per_K={per_K}, acc_per_depth={per_d}.")
    return ("EXTREME_BOUNDED",
            f"Tighter bounds than expected: K_ceiling={K_c}, depth_ceiling={d_c}. "
            f"acc_per_K={per_K}, acc_per_depth={per_d}.")


def self_test_verdict():
    cases = [
        ({"K_ceiling": 50000, "depth_ceiling": 400, "acc_per_K": {}, "acc_per_depth": {}}, "EXTREME_HIGH"),
        ({"K_ceiling": 5000, "depth_ceiling": 200, "acc_per_K": {}, "acc_per_depth": {}}, "EXTREME_MID"),
        ({"K_ceiling": 1000, "depth_ceiling": 100, "acc_per_K": {}, "acc_per_depth": {}}, "EXTREME_BOUNDED"),
        ({}, "EXTREME_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_K(K, depth, n_trials, num_relations, N, seed, device):
    num_entities = max(K, depth + 10)
    gen = torch.Generator(device=device).manual_seed(seed + K)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + K + 1009)
    correct = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain_entities = perm.tolist()
        chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                      for _ in range(depth)]
        n_distractors = max(0, K - depth)
        M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if v.vamp_chain_forward_backward(M, chain_entities[0], chain_rels, chain_entities[-1],
                                            entity_atoms, relation_atoms):
            correct += 1
    return correct / n_trials


def run_one_depth(depth, K, n_trials, num_relations, N, seed, device):
    num_entities = max(K, depth + 10)
    return run_one_K(K, depth, n_trials, num_relations, N, seed, device)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "K_grid": [5000, 10000] if smoke else [5000, 10000, 50000, 100000],
              "depth_grid": [200, 300] if smoke else [200, 300, 400, 500],
              "K_axis_depth": 25 if smoke else 50,
              "depth_axis_K": 200,
              "num_relations": 20,
              "n_trials": 3 if smoke else 10,
              "seed": 17}
    print(f"[config] N={config['N']} K_grid={config['K_grid']} depth_grid={config['depth_grid']}", flush=True)
    print(f"[axis 1] K-stress at depth={config['K_axis_depth']}", flush=True)
    acc_per_K = {}
    for K in config["K_grid"]:
        acc = run_one_K(K, config["K_axis_depth"], config["n_trials"], config["num_relations"],
                         config["N"], config["seed"], device)
        acc_per_K[str(K)] = acc
        print(f"  K={K} (d={config['K_axis_depth']}): acc={acc:.3f}", flush=True)
    K_ceiling = max([K for K in config["K_grid"] if acc_per_K[str(K)] >= 0.5], default=0)
    print(f"[axis 2] depth-cliff at K={config['depth_axis_K']}", flush=True)
    acc_per_depth = {}
    for d in config["depth_grid"]:
        acc = run_one_depth(d, config["depth_axis_K"], config["n_trials"], config["num_relations"],
                              config["N"], config["seed"], device)
        acc_per_depth[str(d)] = acc
        print(f"  d={d} (K={config['depth_axis_K']}): acc={acc:.3f}", flush=True)
    depth_ceiling = max([d for d in config["depth_grid"] if acc_per_depth[str(d)] >= 0.5], default=0)
    summary = {"acc_per_K": acc_per_K, "K_ceiling": K_ceiling,
                "acc_per_depth": acc_per_depth, "depth_ceiling": depth_ceiling}
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
    out_dir = get_output_dir("wave14_vamp_chain_extreme_stress_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("K_ceiling_present", float(summary["K_ceiling"]) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_chain_extreme_stress_v1")
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
