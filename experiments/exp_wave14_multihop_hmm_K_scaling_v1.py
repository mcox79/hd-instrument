"""Multi-hop HMM K-scaling — does substrate's plateau-at-~0.22 phenomenon hold at K=50,100,200,500?

Per cycle 132 GEOMETRIC_FALSIFIED + cycle 121 plateau-at-0.22 at K=100. Test if
plateau is K-invariant (suggesting fundamental dynamics) or K-dependent.

Verdict thresholds:
  HMMK_INVARIANT: plateau acc within +/-0.10 across all K (substrate-dynamic fundamental)
  HMMK_DECREASING: acc drops monotonically with K (capacity-mediated)
  HMMK_INCONCLUSIVE

Pre-reg: minimal — diagnostic follow-up to GEOMETRIC_FALSIFIED.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

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
    if "acc_d50_per_K" not in summary:
        return ("HMMK_INCONCLUSIVE", "Missing acc_d50_per_K.")
    per = summary["acc_d50_per_K"]
    vals = list(per.values())
    spread = max(vals) - min(vals)
    if spread < 0.10:
        return ("HMMK_INVARIANT",
                f"Plateau K-invariant: acc_d50_per_K={per}, spread={spread:.3f}<0.10.")
    Ks = sorted(int(k) for k in per.keys())
    monotone = all(per[str(Ks[i])] >= per[str(Ks[i+1])] for i in range(len(Ks)-1))
    if monotone:
        return ("HMMK_DECREASING",
                f"Monotone decrease with K: acc_d50_per_K={per}, spread={spread:.3f}.")
    return ("HMMK_INCONCLUSIVE", f"Non-monotone: acc_d50_per_K={per}.")


def self_test_verdict():
    cases = [
        ({"acc_d50_per_K": {"50": 0.22, "100": 0.20, "200": 0.18}}, "HMMK_INVARIANT"),
        ({"acc_d50_per_K": {"50": 0.50, "100": 0.22, "200": 0.05}}, "HMMK_DECREASING"),
        ({"acc_d50_per_K": {"50": 0.10, "100": 0.50, "200": 0.20}}, "HMMK_INCONCLUSIVE"),
        ({}, "HMMK_INCONCLUSIVE"),
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
              "K_grid": [50, 100] if smoke else [50, 100, 200, 500],
              "depth": 25 if smoke else 50,
              "num_entities": 600,
              "num_relations": 20,
              "n_trials": 10 if smoke else 30,
              "seed": 17}
    print(f"[config] N={config['N']} depth={config['depth']} K_grid={config['K_grid']}", flush=True)
    per_K = {}
    for K in config["K_grid"]:
        acc = run_one_K(K, config["N"], config["num_entities"], config["num_relations"],
                          config["depth"], config["n_trials"], config["seed"], device)
        per_K[str(K)] = acc
        print(f"  K={K}: acc_d{config['depth']}={acc:.3f}", flush=True)
    summary = {"acc_d50_per_K": per_K, "depth": config["depth"]}
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
    out_dir = get_output_dir("wave14_multihop_hmm_K_scaling_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", max(summary["acc_d50_per_K"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_hmm_K_scaling_v1")
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
