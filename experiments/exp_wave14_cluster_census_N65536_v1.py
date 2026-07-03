"""Cluster census at N=65536 — Strategy 21:25 Priority 1.

Per Research 4th-attempt FINAL spurious-attractor cluster-trapping framework.
Run 500 forward chains from same true codeword; count how few unique codewords
the chains terminate on. CONFIRMED if unique<10 AND top5_share>0.9.
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
    if "unique_codewords_hit" not in summary:
        return ("CLUSTER_INCONCLUSIVE", "Missing.")
    u = summary["unique_codewords_hit"]; t5 = summary["top5_share"]
    if u < 10 and t5 > 0.9:
        return ("CLUSTER_TRAPPING_CONFIRMED",
                f"Cluster trapping confirmed: unique={u}<10 AND top5_share={t5:.3f}>0.9.")
    if u > 50 or t5 < 0.5:
        return ("CLUSTER_TRAPPING_REFUTED",
                f"Cluster trapping refuted: unique={u}, top5_share={t5:.3f}.")
    return ("CLUSTER_TRAPPING_PARTIAL",
            f"Partial: unique={u}, top5_share={t5:.3f}.")


def self_test_verdict():
    for s, exp in [
        ({"unique_codewords_hit": 5, "top5_share": 0.95}, "CLUSTER_TRAPPING_CONFIRMED"),
        ({"unique_codewords_hit": 80, "top5_share": 0.30}, "CLUSTER_TRAPPING_REFUTED"),
        ({"unique_codewords_hit": 20, "top5_share": 0.7}, "CLUSTER_TRAPPING_PARTIAL"),
        ({}, "CLUSTER_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_cluster_census(N, K, depth, n_trials, num_relations, noise_p, seed, device):
    num_entities = max(K, depth + 10)
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    # Use one true chain, run from same start with noise variations
    perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
    chain_entities = perm.tolist()
    chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                  for _ in range(depth)]
    M = mh.build_factbase(chain_entities, chain_rels, max(0, K - depth),
                            num_entities, num_relations,
                            entity_atoms, relation_atoms, cpu_gen, device)
    final_outputs = []
    for trial in range(n_trials):
        # Noisy start
        start = entity_atoms[chain_entities[0]].clone()
        if noise_p > 0:
            flips = (torch.rand(N, generator=cpu_gen) < noise_p).to(device).float()
            start = start * (1.0 - 2.0 * flips)
        current_idx = int((entity_atoms @ start).argmax().item())
        # Forward chain with argmax cleanup
        for r_idx in chain_rels:
            current = entity_atoms[current_idx]
            rel = relation_atoms[r_idx]
            probe = M * (current * rel)
            current_idx = int((entity_atoms @ probe).argmax().item())
        final_outputs.append(current_idx)
    counts = Counter(final_outputs)
    unique = len(counts)
    top5_share = sum(sorted(counts.values(), reverse=True)[:5]) / n_trials
    return unique, top5_share, dict(counts.most_common(10))


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536, "K": 100, "depth": 25,
              "n_trials": 100 if smoke else 500,
              "num_relations": 20, "noise_p": 0.05, "seed": 17}
    print(f"[config] N={config['N']} K={config['K']} d={config['depth']} n={config['n_trials']}", flush=True)
    unique, top5, top10 = run_cluster_census(
        config["N"], config["K"], config["depth"], config["n_trials"],
        config["num_relations"], config["noise_p"], config["seed"], device)
    print(f"  unique={unique}, top5_share={top5:.3f}", flush=True)
    print(f"  top10 codewords by frequency: {top10}", flush=True)
    summary = {"unique_codewords_hit": unique,
                "top5_share": top5,
                "top10_distribution": top10,
                "n_trials": config["n_trials"]}
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
    out_dir = get_output_dir("wave14_cluster_census_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("unique_present", float(summary["unique_codewords_hit"]) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cluster_census_N65536_v1")
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
