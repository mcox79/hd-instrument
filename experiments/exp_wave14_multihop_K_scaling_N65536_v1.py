"""Multi-hop K-scaling at N=65536 — Research falsifiability test of near-degeneracy hypothesis.

Per Research 2026-05-22 18:58. The eigenvalue-near-degeneracy mechanism predicts
smaller K (less crowding in signal subspace) → less per-hop drift → higher
acc_50hop.

Quantitative predictions at N=65536 with argmax cleanup:
  K=100: acc_50hop = 0.22 (cycle 121 baseline)
  K=50:  acc_50hop ~ 0.65-0.80
  K=25:  acc_50hop ~ 0.80-0.90

Falsification: if K=50 doesn't improve significantly over K=100 (e.g., acc_50hop
< 0.35 at K=50), the eigenvalue-degeneracy hypothesis is WRONG.

Verdict thresholds:
  KSCALE_CONFIRMS:  K=25 acc_50hop >= 0.70 AND K=50 acc_50hop >= 0.50 (monotone K)
  KSCALE_PARTIAL:   K=50 acc_50hop in [0.35, 0.50] (partial confirmation)
  KSCALE_FALSIFIES: K=50 acc_50hop < 0.35 (mechanism diagnosis falsified)
  KSCALE_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_K_scaling_N65536_v1.md
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
    if "acc_50hop_per_K" not in summary:
        return ("KSCALE_INCONCLUSIVE", "Missing acc_50hop_per_K.")
    per_K = summary["acc_50hop_per_K"]
    a25 = per_K.get("25", 0.0); a50 = per_K.get("50", 0.0); a100 = per_K.get("100", 0.0)
    if a25 >= 0.70 and a50 >= 0.50:
        return ("KSCALE_CONFIRMS",
                f"K-scaling confirms near-degeneracy mechanism: K=25 acc_50hop={a25:.3f}>=0.70, "
                f"K=50={a50:.3f}>=0.50, K=100={a100:.3f}. acc_50hop_per_K={per_K}.")
    if a50 < 0.35:
        return ("KSCALE_FALSIFIES",
                f"K-scaling FALSIFIES near-degeneracy mechanism: K=50 acc_50hop={a50:.3f}<0.35. "
                f"acc_50hop_per_K={per_K}. Smaller K doesn't help; mechanism diagnosis wrong.")
    return ("KSCALE_PARTIAL",
            f"Partial confirmation: K=50 acc_50hop={a50:.3f} in [0.35, 0.50]. "
            f"acc_50hop_per_K={per_K}.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_per_K": {"25": 0.85, "50": 0.65, "100": 0.22}}, "KSCALE_CONFIRMS"),
        ({"acc_50hop_per_K": {"25": 0.55, "50": 0.40, "100": 0.22}}, "KSCALE_PARTIAL"),
        ({"acc_50hop_per_K": {"25": 0.30, "50": 0.25, "100": 0.22}}, "KSCALE_FALSIFIES"),
        ({}, "KSCALE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_K(K, N, num_entities, num_relations, depth, n_trials, seed, device):
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    if depth > num_entities - 1 or depth > K:
        return 0.0
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
        if mh.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                          entity_atoms, relation_atoms):
            correct += 1
    return correct / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "K_grid": [25, 50] if smoke else [25, 50, 100],
              "num_entities": 200,
              "num_relations": 20,
              "depth": 25 if smoke else 50,
              "n_trials": 10 if smoke else 30,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} depth={config['depth']} K_grid={config['K_grid']}", flush=True)
    acc_per_K_per_seed = {K: [] for K in config["K_grid"]}
    for seed in config["seeds"]:
        for K in config["K_grid"]:
            acc = run_one_K(K, config["N"], config["num_entities"], config["num_relations"],
                              config["depth"], config["n_trials"], seed, device)
            acc_per_K_per_seed[K].append(acc)
            print(f"  seed={seed} K={K}: acc_{config['depth']}hop={acc:.3f}", flush=True)
    acc_per_K = {}
    for K in config["K_grid"]:
        acc_per_K[str(K)] = sum(acc_per_K_per_seed[K]) / len(acc_per_K_per_seed[K])
    summary = {"acc_50hop_per_K": acc_per_K,
                "depth_tested": config["depth"]}
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
    out_dir = get_output_dir("wave14_multihop_K_scaling_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_K_acc_present", max(summary["acc_50hop_per_K"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_K_scaling_N65536_v1")
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
