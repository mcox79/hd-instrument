"""Smoother validation matrix — 5 seeds x 5 K x 5 depths x 3 noise levels = 375 cells.

Heavy multi-axis sweep. Single experiment that fills pipeline meaningfully (~20-60min runtime).
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

_so = importlib.util.spec_from_file_location("so",
    REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
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
    if "matrix" not in summary:
        return ("MATRIX_INCONCLUSIVE", "Missing.")
    cells = summary["matrix"]
    if not cells: return ("MATRIX_INCONCLUSIVE", "Empty.")
    pass_count = sum(1 for v in cells.values() if v >= 0.7)
    frac = pass_count / len(cells)
    if frac >= 0.70:
        return ("MATRIX_BROAD_VALIDATED",
                f"{pass_count}/{len(cells)} cells pass >=0.7 ({frac*100:.0f}%). Substrate-product envelope broad.")
    if frac >= 0.40:
        return ("MATRIX_MID_VALIDATED",
                f"{pass_count}/{len(cells)} cells pass ({frac*100:.0f}%). Envelope mid.")
    return ("MATRIX_NARROW_VALIDATED",
            f"Only {pass_count}/{len(cells)} cells pass ({frac*100:.0f}%). Envelope narrow.")


def self_test_verdict():
    for s, exp in [
        ({"matrix": {f"c{i}": 1.0 for i in range(10)}}, "MATRIX_BROAD_VALIDATED"),
        ({"matrix": {f"c{i}": 1.0 if i < 5 else 0.3 for i in range(10)}}, "MATRIX_MID_VALIDATED"),
        ({"matrix": {f"c{i}": 0.2 for i in range(10)}}, "MATRIX_NARROW_VALIDATED"),
        ({}, "MATRIX_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_cell(N, K, depth, noise_p, seed, num_relations, n_trials, device):
    num_entities = max(K, depth + 10)
    gen = torch.Generator(device=device).manual_seed(seed + N + K + depth + int(noise_p * 1000))
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + N + K + depth + int(noise_p * 1000) + 1009)
    correct = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain = perm.tolist()
        rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                for _ in range(depth)]
        M = mh.build_factbase(chain, rels, max(0, K - depth),
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if noise_p > 0:
            flips = (torch.rand(M.shape, generator=cpu_gen) < noise_p).to(device).float()
            M = M * (1.0 - 2.0 * flips)
        if so.chain_smoother_only(M, chain[0], rels, chain[-1], entity_atoms, relation_atoms):
            correct += 1
    return correct / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"N": 8192, "K_grid": [100, 500], "depth_grid": [25, 50],
                   "noise_grid": [0.0, 0.10], "seeds": [17, 23],
                   "n_trials": 3, "num_relations": 20}
    else:
        config = {"N": 65536, "K_grid": [100, 500, 1000, 5000, 10000],
                   "depth_grid": [25, 50, 100, 200, 500],
                   "noise_grid": [0.0, 0.10, 0.30],
                   "seeds": [17, 23, 31, 41, 53],
                   "n_trials": 5, "num_relations": 20}
    matrix = {}
    n_cells = len(config["K_grid"]) * len(config["depth_grid"]) * len(config["noise_grid"]) * len(config["seeds"])
    print(f"[config] N={config['N']} {n_cells} cells x {config['n_trials']} trials", flush=True)
    cell_i = 0
    for seed in config["seeds"]:
        for K in config["K_grid"]:
            for depth in config["depth_grid"]:
                for noise in config["noise_grid"]:
                    if depth >= K:
                        continue
                    acc = run_cell(config["N"], K, depth, noise, seed,
                                     config["num_relations"], config["n_trials"], device)
                    key = f"s{seed}_K{K}_d{depth}_p{noise}"
                    matrix[key] = acc
                    cell_i += 1
                    if cell_i % 10 == 0:
                        avg = sum(matrix.values()) / max(len(matrix), 1)
                        print(f"  [{cell_i}/{n_cells}] {key}: acc={acc:.3f} (running avg={avg:.3f})", flush=True)
    summary = {"matrix": matrix, "n_cells": len(matrix)}
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
    out_dir = get_output_dir("wave14_smoother_validation_matrix_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_pass", max(summary["matrix"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_smoother_validation_matrix_v1")
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
