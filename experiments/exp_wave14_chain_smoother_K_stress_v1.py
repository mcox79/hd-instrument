"""Smoother-only K-stress — does backward-msg-alone method scale to agent-realistic K?

Per cycle 132 SMOOTHER_ONLY_WORKS (PERFECT at K=100). Test K in {500, 1000, 5000, 10000}.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
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
    if "acc_per_K" not in summary:
        return ("SMOOTHER_K_INCONCLUSIVE", "Missing.")
    per = summary["acc_per_K"]
    a10k = per.get("10000", 0.0); a1k = per.get("1000", 0.0); a500 = per.get("500", 0.0)
    if a10k >= 0.5:
        return ("SMOOTHER_K_AGENT_READY", f"Backward-only scales to K=10000: {per}.")
    if a1k >= 0.5:
        return ("SMOOTHER_K_MID", f"Holds at K=1000: {per}.")
    if a500 >= 0.5:
        return ("SMOOTHER_K_LIMITED", f"Only at K=500: {per}.")
    return ("SMOOTHER_K_KILLED", f"Fails: {per}.")


def self_test_verdict():
    cases = [
        ({"acc_per_K": {"500": 1.0, "1000": 1.0, "5000": 1.0, "10000": 0.7}}, "SMOOTHER_K_AGENT_READY"),
        ({"acc_per_K": {"500": 1.0, "1000": 0.8, "5000": 0.3, "10000": 0.0}}, "SMOOTHER_K_MID"),
        ({"acc_per_K": {"500": 0.7, "1000": 0.2, "5000": 0.0, "10000": 0.0}}, "SMOOTHER_K_LIMITED"),
        ({"acc_per_K": {"500": 0.1}}, "SMOOTHER_K_KILLED"),
        ({}, "SMOOTHER_K_INCONCLUSIVE"),
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
              "depth": 25 if smoke else 50,
              "K_grid": [500, 1000] if smoke else [500, 1000, 5000, 10000],
              "num_relations": 20,
              "n_trials": 5 if smoke else 15,
              "seed": 17}
    per_K = {}
    for K in config["K_grid"]:
        num_entities = max(K, config["depth"] + 10)
        gen = torch.Generator(device=device).manual_seed(config["seed"] + K)
        entity_atoms = mh.make_bsc_codebook(num_entities, config["N"], gen, device)
        relation_atoms = mh.make_bsc_codebook(config["num_relations"], config["N"], gen, device)
        cpu_gen = torch.Generator().manual_seed(config["seed"] + K + 1009)
        correct = 0
        for trial in range(config["n_trials"]):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:config["depth"] + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                          for _ in range(config["depth"])]
            n_distractors = max(0, K - config["depth"])
            M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, config["num_relations"],
                                    entity_atoms, relation_atoms, cpu_gen, device)
            if so.chain_smoother_only(M, chain_entities[0], chain_rels, chain_entities[-1],
                                          entity_atoms, relation_atoms):
                correct += 1
        per_K[str(K)] = correct / config["n_trials"]
        print(f"  K={K}: acc={per_K[str(K)]:.3f}", flush=True)
    summary = {"acc_per_K": per_K, "depth": config["depth"]}
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
    out_dir = get_output_dir("wave14_chain_smoother_K_stress_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", max(summary["acc_per_K"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_chain_smoother_K_stress_v1")
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
