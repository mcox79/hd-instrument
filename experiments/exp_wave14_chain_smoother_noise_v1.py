"""Smoother-only noise robustness — backward-msg-alone with bit-flipped factbase."""
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
    if "acc_per_noise" not in summary:
        return ("NOISE_INCONCLUSIVE", "Missing.")
    per = summary["acc_per_noise"]
    p10 = per.get("0.10", 0.0); clean = per.get("0.0", 0.0)
    if clean < 0.5: return ("NOISE_BROKEN", f"Clean fails: {per}.")
    if p10 >= 0.5: return ("NOISE_ROBUST", f"Survives 10% noise: {per}.")
    return ("NOISE_BRITTLE", f"Breaks under noise: {per}.")


def self_test_verdict():
    for s, exp in [
        ({"acc_per_noise": {"0.0": 1.0, "0.10": 0.8}}, "NOISE_ROBUST"),
        ({"acc_per_noise": {"0.0": 1.0, "0.10": 0.2}}, "NOISE_BRITTLE"),
        ({"acc_per_noise": {"0.0": 0.3}}, "NOISE_BROKEN"),
        ({}, "NOISE_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536, "num_entities": 200, "num_relations": 20,
              "num_facts": 100, "depth": 25 if smoke else 50,
              "noise_levels": [0.0, 0.10] if smoke else [0.0, 0.05, 0.10, 0.20, 0.30],
              "n_trials": 5 if smoke else 15, "seed": 17}
    gen = torch.Generator(device=device).manual_seed(config["seed"])
    entity_atoms = mh.make_bsc_codebook(config["num_entities"], config["N"], gen, device)
    relation_atoms = mh.make_bsc_codebook(config["num_relations"], config["N"], gen, device)
    per = {}
    for p in config["noise_levels"]:
        cpu_gen = torch.Generator().manual_seed(config["seed"] + int(p * 1000) + 1009)
        correct = 0
        for trial in range(config["n_trials"]):
            perm = torch.randperm(config["num_entities"], generator=cpu_gen)[:config["depth"] + 1]
            chain = perm.tolist()
            rels = [int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                    for _ in range(config["depth"])]
            M = mh.build_factbase(chain, rels, max(0, config["num_facts"] - config["depth"]),
                                    config["num_entities"], config["num_relations"],
                                    entity_atoms, relation_atoms, cpu_gen, device)
            if p > 0:
                flips = (torch.rand(M.shape, generator=cpu_gen) < p).to(device).float()
                M = M * (1.0 - 2.0 * flips)
            if so.chain_smoother_only(M, chain[0], rels, chain[-1], entity_atoms, relation_atoms):
                correct += 1
        per[f"{p:.2f}" if p > 0 else "0.0"] = correct / config["n_trials"]
        print(f"  p={p:.2f}: acc={per[list(per)[-1]]:.3f}", flush=True)
    summary = {"acc_per_noise": per}
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
    out_dir = get_output_dir("wave14_chain_smoother_noise_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", summary["acc_per_noise"].get("0.0", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_chain_smoother_noise_v1")
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
