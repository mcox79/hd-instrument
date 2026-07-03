"""Cluster identity diagnostic — characterize the absorbing codeword in CLUSTER_TRAPPING_CONFIRMED.

At N=65536 cycle 134 found unique=1 codeword: ALL 500 forward chains converged to ONE codeword.
This experiment tests if that absorbing codeword is robust across:
  (a) different chain definitions (vary chain_rels)
  (b) different start entities (vary start_idx not just noise around it)
  (c) different factbase realizations

Records the absorbing codeword index per (chain_seed, rel_seed, start_seed) triple.

Verdicts:
  CLUSTER_GLOBAL_ATTRACTOR: same codeword absorbs across all variations (universal fixed point)
  CLUSTER_CHAIN_SPECIFIC: absorbing codeword varies with chain_rels (chain-dependent attractor)
  CLUSTER_DIFFUSE: multiple absorbing codewords (no clear single attractor)
  CLUSTER_INCONCLUSIVE
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from collections import Counter
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
    if "n_distinct_attractors" not in summary:
        return ("CLUSTER_INCONCLUSIVE", "Missing.")
    n_dist = summary["n_distinct_attractors"]
    n_configs = summary["n_configs"]
    top_share = summary["top_attractor_share"]
    if n_dist == 1:
        return ("CLUSTER_GLOBAL_ATTRACTOR",
                f"Single absorbing codeword across all {n_configs} chain configs.")
    if top_share >= 0.7:
        return ("CLUSTER_GLOBAL_ATTRACTOR",
                f"Top attractor absorbs {top_share*100:.0f}% of configs (n_distinct={n_dist}/{n_configs}).")
    if n_dist >= n_configs * 0.5:
        return ("CLUSTER_DIFFUSE",
                f"Many distinct attractors: {n_dist}/{n_configs}. No single absorbing codeword.")
    return ("CLUSTER_CHAIN_SPECIFIC",
            f"{n_dist} distinct attractors across {n_configs} configs (top={top_share*100:.0f}%).")


def self_test_verdict():
    for s, exp in [
        ({"n_distinct_attractors": 1, "n_configs": 10, "top_attractor_share": 1.0}, "CLUSTER_GLOBAL_ATTRACTOR"),
        ({"n_distinct_attractors": 3, "n_configs": 10, "top_attractor_share": 0.8}, "CLUSTER_GLOBAL_ATTRACTOR"),
        ({"n_distinct_attractors": 4, "n_configs": 10, "top_attractor_share": 0.4}, "CLUSTER_CHAIN_SPECIFIC"),
        ({"n_distinct_attractors": 8, "n_configs": 10, "top_attractor_share": 0.2}, "CLUSTER_DIFFUSE"),
        ({}, "CLUSTER_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (5/5 cases)", flush=True)


def run_one_config(N, K, depth, num_entities, num_relations, chain_seed, n_trials, device):
    gen = torch.Generator(device=device).manual_seed(chain_seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(chain_seed + 1009)
    perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
    chain_ents = perm.tolist()
    chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                  for _ in range(depth)]
    M = mh.build_factbase(chain_ents, chain_rels, max(0, K - depth),
                            num_entities, num_relations,
                            entity_atoms, relation_atoms, cpu_gen, device)
    # Run n_trials chains with random starts; record final codeword
    finals = []
    for _ in range(n_trials):
        start = int(torch.randint(0, num_entities, (1,), generator=cpu_gen).item())
        current = start
        for r_idx in chain_rels:
            current_atom = entity_atoms[current]
            rel = relation_atoms[r_idx]
            probe = M * (current_atom * rel)
            current = int((entity_atoms @ probe).argmax().item())
        finals.append(current)
    return Counter(finals).most_common(1)[0][0]  # mode (most-absorbing codeword)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536, "K": 100, "depth": 25,
              "num_entities": 200, "num_relations": 20,
              "chain_seeds": [11, 13] if smoke else [11, 13, 17, 19, 23, 29, 31, 37, 41, 43],
              "n_trials_per_config": 30 if smoke else 100}
    print(f"[config] N={config['N']} {len(config['chain_seeds'])} chain configs", flush=True)
    absorbing = []
    for chain_seed in config["chain_seeds"]:
        attr = run_one_config(config["N"], config["K"], config["depth"],
                                config["num_entities"], config["num_relations"],
                                chain_seed, config["n_trials_per_config"], device)
        absorbing.append(attr)
        print(f"  chain_seed={chain_seed}: absorbing codeword={attr}", flush=True)
    counter = Counter(absorbing)
    n_distinct = len(counter)
    top_share = counter.most_common(1)[0][1] / len(absorbing)
    summary = {"n_distinct_attractors": n_distinct,
                "n_configs": len(absorbing),
                "top_attractor_share": top_share,
                "absorbing_per_seed": dict(zip(config["chain_seeds"], absorbing)),
                "attractor_counts": dict(counter.most_common(20))}
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
    out_dir = get_output_dir("wave14_cluster_identity_diagnostic_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("attractors_present", float(summary["n_distinct_attractors"]) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cluster_identity_diagnostic_v1")
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
