"""Smoother-only extreme K — does backward-msg scale to K=20k, 50k, 100k?"""
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
    if "acc_per_K" not in summary:
        return ("EXTREME_K_INCONCLUSIVE", "Missing.")
    per = summary["acc_per_K"]
    if per.get("100000", 0.0) >= 0.5: return ("EXTREME_K_100K", f"Scales to 100K: {per}.")
    if per.get("50000", 0.0) >= 0.5: return ("EXTREME_K_50K", f"Scales to 50K: {per}.")
    if per.get("20000", 0.0) >= 0.5: return ("EXTREME_K_20K", f"Scales to 20K: {per}.")
    return ("EXTREME_K_LIMITED", f"Caps below 20K: {per}.")


def self_test_verdict():
    for s, exp in [
        ({"acc_per_K": {"20000": 1.0, "50000": 1.0, "100000": 1.0}}, "EXTREME_K_100K"),
        ({"acc_per_K": {"20000": 1.0, "50000": 1.0, "100000": 0.0}}, "EXTREME_K_50K"),
        ({"acc_per_K": {"20000": 1.0, "50000": 0.0}}, "EXTREME_K_20K"),
        ({"acc_per_K": {"20000": 0.0}}, "EXTREME_K_LIMITED"),
        ({}, "EXTREME_K_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (5/5 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536,
              "depth": 25 if smoke else 50,
              "K_grid": [10000, 20000] if smoke else [20000, 50000, 100000],
              "num_relations": 20, "n_trials": 3 if smoke else 8, "seed": 17}
    per = {}
    for K in config["K_grid"]:
        num_entities = max(K, config["depth"] + 10)
        gen = torch.Generator(device=device).manual_seed(config["seed"] + K)
        entity_atoms = mh.make_bsc_codebook(num_entities, config["N"], gen, device)
        relation_atoms = mh.make_bsc_codebook(config["num_relations"], config["N"], gen, device)
        cpu_gen = torch.Generator().manual_seed(config["seed"] + K + 1009)
        correct = 0
        for trial in range(config["n_trials"]):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:config["depth"] + 1]
            chain = perm.tolist()
            rels = [int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                    for _ in range(config["depth"])]
            M = mh.build_factbase(chain, rels, max(0, K - config["depth"]),
                                    num_entities, config["num_relations"],
                                    entity_atoms, relation_atoms, cpu_gen, device)
            if so.chain_smoother_only(M, chain[0], rels, chain[-1], entity_atoms, relation_atoms):
                correct += 1
        per[str(K)] = correct / config["n_trials"]
        print(f"  K={K}: acc={per[str(K)]:.3f}", flush=True)
    summary = {"acc_per_K": per}
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
    out_dir = get_output_dir("wave14_chain_smoother_extreme_K_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", max(summary["acc_per_K"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_chain_smoother_extreme_K_v1")
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
