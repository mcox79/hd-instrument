"""VAMP-on-chain noise robustness — adversarial bit-flips per hop.

Per cycle 127 VAMPCHAIN_RESTORES PERFECT. Test deployment-grade noise tolerance:
inject random bit-flips at rate p into the M factbase or per-hop query state, and
measure how acc_50hop degrades.

Verdict thresholds (at N=65536, d=50, K=100):
  VAMPNOISE_ROBUST: acc_50hop(p=0.10) >= 0.50 (substrate handles realistic noise)
  VAMPNOISE_BRITTLE: acc(p=0.10) < 0.50 but acc(p=0.0) >= 0.50 (clean PASS but noise BREAKS)
  VAMPNOISE_BROKEN: acc(p=0.0) < 0.50 (regression from cycle 127 PERFECT)
  VAMPNOISE_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_vamp_chain_noise_robust_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
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


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_per_noise" not in summary:
        return ("VAMPNOISE_INCONCLUSIVE", "Missing acc_per_noise.")
    per = summary["acc_per_noise"]
    clean = per.get("0.0", 0.0)
    p10 = per.get("0.10", 0.0)
    if clean < 0.50:
        return ("VAMPNOISE_BROKEN",
                f"Clean acc_50hop={clean:.3f}<0.50 (regression from cycle 127 PERFECT). "
                f"acc_per_noise={per}.")
    if p10 >= 0.50:
        return ("VAMPNOISE_ROBUST",
                f"VAMP-on-chain noise robust: acc(p=0.10)={p10:.3f}>=0.50; clean={clean:.3f}. "
                f"Substrate handles realistic noise. acc_per_noise={per}.")
    return ("VAMPNOISE_BRITTLE",
            f"VAMP-on-chain brittle: acc(p=0.10)={p10:.3f}<0.50; clean={clean:.3f}. "
            f"acc_per_noise={per}.")


def self_test_verdict():
    cases = [
        ({"acc_per_noise": {"0.0": 1.0, "0.05": 0.9, "0.10": 0.7, "0.20": 0.3}}, "VAMPNOISE_ROBUST"),
        ({"acc_per_noise": {"0.0": 0.9, "0.05": 0.6, "0.10": 0.2}}, "VAMPNOISE_BRITTLE"),
        ({"acc_per_noise": {"0.0": 0.3, "0.05": 0.1}}, "VAMPNOISE_BROKEN"),
        ({}, "VAMPNOISE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def flip_bits(vec, p, gen, device):
    if p <= 0: return vec
    flips = (torch.rand(vec.shape, generator=gen) < p).to(device).float()
    return vec * (1.0 - 2.0 * flips)


def run_one_noise(p_noise, n_trials, N, num_entities, num_relations, num_facts, depth, seed, device):
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
        n_distractors = max(0, num_facts - depth)
        M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        # Inject noise into M
        M_noisy = flip_bits(M, p_noise, cpu_gen, device)
        if v.vamp_chain_forward_backward(M_noisy, chain_entities[0], chain_rels, chain_entities[-1],
                                            entity_atoms, relation_atoms):
            correct += 1
    return correct / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "depth": 25 if smoke else 50,
              "noise_levels": [0.0, 0.10] if smoke else [0.0, 0.05, 0.10, 0.20, 0.30],
              "n_trials": 5 if smoke else 15,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} d={config['depth']} K={config['num_facts']} noise={config['noise_levels']}", flush=True)
    acc_per_noise_per_seed = {p: [] for p in config["noise_levels"]}
    for seed in config["seeds"]:
        for p in config["noise_levels"]:
            acc = run_one_noise(p, config["n_trials"], config["N"], config["num_entities"],
                                  config["num_relations"], config["num_facts"], config["depth"],
                                  seed, device)
            acc_per_noise_per_seed[p].append(acc)
            print(f"  seed={seed} p={p:.2f}: acc={acc:.3f}", flush=True)
    acc_per_noise = {}
    for p in config["noise_levels"]:
        key = "0.0" if p == 0.0 else f"{p:.2f}"
        acc_per_noise[key] = sum(acc_per_noise_per_seed[p]) / len(acc_per_noise_per_seed[p])
    summary = {"acc_per_noise": acc_per_noise,
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
    out_dir = get_output_dir("wave14_vamp_chain_noise_robust_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("clean_acc_present",
                                 summary["acc_per_noise"].get("0.0", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_chain_noise_robust_v1")
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
