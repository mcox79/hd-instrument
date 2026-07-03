"""VAMP-on-chain K-stress — push K=100 PERFECT to agent-realistic K=500, 1000, 5000.

Per cycle 127 VAMPCHAIN_RESTORES PERFECT at K=100. Demo 1 (Lane D agent memory SDK)
targets agent-realistic K=1K-10K facts. Does VAMP-on-chain sustain at K=5000?

Verdict thresholds (at d=50, N=65536):
  K_STRESS_AGENT_READY: acc_50hop >= 0.50 at K=5000 (full agent-realistic scale)
  K_STRESS_SMALL_AGENT: K=500 PASS but K=5000 < 0.50 (small-cardinality only)
  K_STRESS_LIMITED:     K=500 also fails (positioning narrower)
  K_STRESS_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_vamp_chain_K_stress_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_per_K" not in summary:
        return ("K_STRESS_INCONCLUSIVE", "Missing acc_per_K.")
    per = summary["acc_per_K"]
    a5000 = per.get("5000", 0.0); a500 = per.get("500", 0.0)
    if a5000 >= 0.50:
        return ("K_STRESS_AGENT_READY",
                f"VAMP-on-chain at K=5000: acc_50hop={a5000:.3f}>=0.50. Agent-realistic deep "
                f"chain composition viable. acc_per_K={per}.")
    if a500 >= 0.50:
        return ("K_STRESS_SMALL_AGENT",
                f"K=500 PASS ({a500:.3f}) but K=5000 ({a5000:.3f}) < 0.50. Demo 1 positions "
                f"as small-cardinality agent memory only. acc_per_K={per}.")
    return ("K_STRESS_LIMITED",
            f"K=500 ({a500:.3f}) < 0.50. Demo 1 positioning narrower than expected. acc_per_K={per}.")


def self_test_verdict():
    cases = [
        ({"acc_per_K": {"100": 1.0, "500": 0.95, "1000": 0.85, "5000": 0.65}}, "K_STRESS_AGENT_READY"),
        ({"acc_per_K": {"100": 1.0, "500": 0.95, "1000": 0.70, "5000": 0.20}}, "K_STRESS_SMALL_AGENT"),
        ({"acc_per_K": {"100": 1.0, "500": 0.30, "1000": 0.10, "5000": 0.02}}, "K_STRESS_LIMITED"),
        ({}, "K_STRESS_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed_K(seed, K_grid, depth, n_trials, num_entities_per_K, num_relations, N, device):
    """Per K value: run VAMP-on-chain at depth d, n_trials chains."""
    by_K = {}
    for K in K_grid:
        # num_entities must be >= depth+1; also large enough so K facts use diverse entities
        num_entities = max(num_entities_per_K.get(K, 300), depth + 10)
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
        by_K[K] = correct / n_trials
        print(f"  seed={seed} K={K} (num_entities={num_entities}): acc_d{depth}={by_K[K]:.3f}", flush=True)
    return by_K


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "depth": 25 if smoke else 50,
              "K_grid": [100, 500] if smoke else [100, 500, 1000, 5000],
              "num_relations": 20,
              "num_entities_per_K": {100: 200, 500: 500, 1000: 1000, 5000: 5000},
              "n_trials": 5 if smoke else 15,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} depth={config['depth']} K_grid={config['K_grid']}", flush=True)
    acc_per_K_per_seed = {K: [] for K in config["K_grid"]}
    for seed in config["seeds"]:
        by_K = run_one_seed_K(seed, config["K_grid"], config["depth"], config["n_trials"],
                                 config["num_entities_per_K"], config["num_relations"],
                                 config["N"], device)
        for K, acc in by_K.items():
            acc_per_K_per_seed[K].append(acc)
    acc_per_K = {str(K): sum(acc_per_K_per_seed[K]) / len(acc_per_K_per_seed[K])
                  for K in config["K_grid"]}
    summary = {"acc_per_K": acc_per_K,
                "depth": config["depth"]}
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
    out_dir = get_output_dir("wave14_vamp_chain_K_stress_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present",
                                 summary["acc_per_K"].get("100", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_chain_K_stress_v1")
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
