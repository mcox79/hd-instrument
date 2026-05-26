"""Smoother-only mega characterization — single long-running multi-axis sweep.

Sweeps (N, K, depth) jointly to characterize the substrate's smoother-only readout envelope.
Replaces multiple small smokes with one comprehensive run.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_so = importlib.util.spec_from_file_location("so",
    REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
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
    if "results" not in summary:
        return ("MEGA_INCONCLUSIVE", "Missing results.")
    results = summary["results"]
    n_cells = len(results)
    n_pass = sum(1 for v in results.values() if v >= 0.5)
    frac_pass = n_pass / max(n_cells, 1)
    if frac_pass >= 0.80:
        return ("MEGA_BROAD_ENVELOPE", f"{n_pass}/{n_cells} cells pass (>={frac_pass*100:.0f}% envelope).")
    if frac_pass >= 0.50:
        return ("MEGA_MID_ENVELOPE", f"{n_pass}/{n_cells} cells pass.")
    return ("MEGA_NARROW_ENVELOPE", f"Only {n_pass}/{n_cells} cells pass.")


def self_test_verdict():
    for s, exp in [
        ({"results": {"a": 1.0, "b": 0.9, "c": 0.8, "d": 0.6}}, "MEGA_BROAD_ENVELOPE"),
        ({"results": {"a": 1.0, "b": 0.6, "c": 0.3, "d": 0.2}}, "MEGA_MID_ENVELOPE"),
        ({"results": {"a": 0.3, "b": 0.2}}, "MEGA_NARROW_ENVELOPE"),
        ({}, "MEGA_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_cell(N, K, depth, n_trials, num_relations, seed, device):
    num_entities = max(K, depth + 10)
    gen = torch.Generator(device=device).manual_seed(seed + N + K + depth)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + N + K + depth + 1009)
    correct = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain = perm.tolist()
        rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item()) for _ in range(depth)]
        M = mh.build_factbase(chain, rels, max(0, K - depth),
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if so.chain_smoother_only(M, chain[0], rels, chain[-1], entity_atoms, relation_atoms):
            correct += 1
    return correct / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        cells = [(4096, 100, 25), (8192, 100, 25), (8192, 500, 25)]
        n_trials = 3
    else:
        cells = [(N, K, D)
                  for N in [8192, 32768, 65536]
                  for K in [100, 500, 1000, 5000]
                  for D in [25, 50, 100]]
        n_trials = 10
    config = {"cells": cells, "n_trials": n_trials, "num_relations": 20, "seed": 17}
    print(f"[config] {len(cells)} cells, {n_trials} trials each", flush=True)
    results = {}
    for i, (N, K, D) in enumerate(cells):
        acc = run_cell(N, K, D, n_trials, config["num_relations"], config["seed"], device)
        key = f"N{N}_K{K}_d{D}"
        results[key] = acc
        print(f"  [{i+1}/{len(cells)}] {key}: acc={acc:.3f}", flush=True)
    summary = {"results": results, "n_cells": len(cells)}
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
    out_dir = get_output_dir("wave14_chain_smoother_mega_characterization_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_pass", max(summary["results"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_chain_smoother_mega_characterization_v1")
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
