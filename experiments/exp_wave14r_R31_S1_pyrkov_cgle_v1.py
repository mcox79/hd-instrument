"""R31 S.1 Pyrkov CGLE — iterative basin-attractor cleanup multi-hop.

Per Strategy push 20:35 EDT: replace argmax cleanup with iterative basin-
attractor dynamics from Pyrkov-Byrnes-Cherny 2020 (arXiv:1909.05082).
Bet N rehab axis #6.

Pre-reg: preregs/2026-05-21_wave14r_R31_S1_pyrkov_cgle_v1.md
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

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)

PASS_ACC_50 = 0.50
PARTIAL_FLOOR = 0.22


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def compute_verdict(summary):
    per_config = summary.get("per_config")
    if not per_config:
        return ("BET_N_R31_S1_INCONCLUSIVE", "Missing per_config.")
    acc50_per_cfg = {}
    for cfg_key, depths in per_config.items():
        d50 = depths.get("50") or depths.get(50) or 0.0
        acc50_per_cfg[cfg_key] = float(d50)
    best_cfg = max(acc50_per_cfg.keys(), key=lambda k: acc50_per_cfg[k])
    best_acc50 = acc50_per_cfg[best_cfg]
    if best_acc50 < PARTIAL_FLOOR:
        return ("BET_N_R31_S1_KILLED",
                f"Pyrkov CGLE fails: best acc_50hop={best_acc50:.3f} < "
                f"{PARTIAL_FLOOR} at all configs. Bet N rehab axis #6 closes. "
                f"per_config: " + ", ".join(f"{k}:{acc50_per_cfg[k]:.3f}"
                                                  for k in sorted(acc50_per_cfg)))
    if best_acc50 >= PASS_ACC_50:
        return ("BET_N_R31_S1_PASS",
                f"Pyrkov CGLE rescues 50-hop: best acc_50={best_acc50:.3f} at "
                f"config {best_cfg}. Dissipative-attractor cleanup extends d=50.")
    return ("BET_N_R31_S1_PARTIAL",
            f"Partial: best acc_50={best_acc50:.3f} at config {best_cfg} in "
            f"[{PARTIAL_FLOOR}, {PASS_ACC_50}). per_config: " +
            ", ".join(f"{k}:{acc50_per_cfg[k]:.3f}" for k in sorted(acc50_per_cfg)))


def self_test_verdict():
    def mk(by_k_acc50):
        return {"per_config": {k: {"50": v} for k, v in by_k_acc50.items()}}
    cases = [
        (mk({"k1_l1.0": 0.55, "k5_l1.0": 0.62}), "BET_N_R31_S1_PASS"),
        (mk({"k1_l1.0": 0.30, "k5_l1.0": 0.35}), "BET_N_R31_S1_PARTIAL"),
        (mk({"k1_l1.0": 0.18, "k5_l1.0": 0.20}), "BET_N_R31_S1_KILLED"),
        ({}, "BET_N_R31_S1_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def pyrkov_basin_cleanup(probe, codebook, k_iter, lam, eps, N, gen):
    """Iterative basin-attractor: state_t+1 = sign(soft_blend(codebook, state_t) + noise)."""
    state = probe.float()
    for _ in range(k_iter):
        sims = codebook @ state / math.sqrt(N)
        scaled = sims / lam
        scaled = scaled - scaled.max()
        weights = torch.softmax(scaled, dim=0)
        state_blend = weights @ codebook
        if eps > 0:
            state_blend = state_blend + eps * torch.randn(state_blend.shape, generator=gen, device=state_blend.device)
        out = torch.sign(state_blend)
        state = torch.where(out == 0, torch.ones_like(out), out)
    final_sims = codebook @ state
    return int(final_sims.argmax().item())


def run_pyrkov_chain(M, start_idx, rel_idxs, target_idx, entity_atoms,
                       relation_atoms, k_iter, lam, eps, N, gen):
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        current_idx = pyrkov_basin_cleanup(probe, entity_atoms, k_iter, lam, eps, N, gen)
    return current_idx == target_idx


def run_one_seed(seed, hop_depths, n_trials, k_iter, lam, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)
    noise_gen = torch.Generator(device=device).manual_seed(seed + 5003)
    by_depth = {}
    for depth in hop_depths:
        if depth > num_entities - 1:
            by_depth[depth] = 0.0
            continue
        n_distractors = max(0, num_facts - depth)
        successes = 0
        for trial in range(n_trials):
            chain_entities = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1].tolist()
            chain_rels = torch.randint(0, num_relations, (depth,), generator=cpu_gen).tolist()
            M = t.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, num_relations, entity_atoms,
                                    relation_atoms, cpu_gen, device)
            ok = run_pyrkov_chain(M, chain_entities[0], chain_rels,
                                    chain_entities[-1], entity_atoms,
                                    relation_atoms, k_iter, lam, 0.02, N, noise_gen)
            if ok:
                successes += 1
        by_depth[depth] = successes / n_trials
    return by_depth


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "num_facts": 20 if smoke else 100,
              "hop_depths": [1, 5] if smoke else [1, 5, 10, 25, 50],
              "n_trials": 5 if smoke else 30,
              "seeds": [17] if smoke else [17, 23, 31],
              "k_iter_sweep": [5] if smoke else [1, 5, 10, 20],
              "lambda_sweep": [1.0] if smoke else [0.5, 1.0, 2.0]}
    per_config = {}
    for k_iter in config["k_iter_sweep"]:
        for lam in config["lambda_sweep"]:
            cfg_key = f"k{k_iter}_l{lam}"
            per_seed = {}
            for seed in config["seeds"]:
                by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"],
                                       k_iter, lam, config, device)
                per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
                print(f"  {cfg_key} seed={seed}: " +
                      " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]),
                      flush=True)
            depth_mean = {}
            for d in config["hop_depths"]:
                depth_mean[str(d)] = sum(per_seed[str(s)][str(d)] for s in config["seeds"]) / len(config["seeds"])
            per_config[cfg_key] = depth_mean
    summary = {"per_config": per_config}
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
    out_dir = get_output_dir("wave14r_R31_S1_pyrkov_cgle_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_cfg = list(summary["per_config"].keys())[0]
    acc_1 = summary["per_config"][first_cfg]["1"]
    oracle.assert_baseline_high("pyrkov_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_R31_S1_pyrkov_cgle_v1")
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
