"""R8 B1 - BSC multi-hop with Ramsauer 2020 modern Hopfield cleanup.

A1 (FHRR) killed, C1 (hybrid) killed. B1 is the cleanup-side rescue.
Storage identical to wave14t BSC. Per-hop cleanup swapped from argmax to
iterated Ramsauer softmax retrieval - exponential-energy attention may
denoise closure-induced collisions that argmax can't resolve.

Update rule per hop:
  state = probe = M * (current * rel)
  for _ in range(n_iters):
    weights = softmax(beta * codebook @ state)
    state = codebook.T @ weights
  current_idx = argmax(codebook @ state)

Pre-reg: preregs/2026-05-21_wave14r_multihop_modernhopfield_v1.md
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

N_FULL = 4096
N_SMOKE = 512
NUM_ENTITIES_FULL = 200
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 20
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = 100
NUM_FACTS_SMOKE = 20
HOP_DEPTHS_FULL = [1, 5, 10, 25, 50]
HOP_DEPTHS_SMOKE = [1, 5]
N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 5
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

BETA_DEFAULT = 8.0
HOPFIELD_ITERS = 5
PASS_ACC_50HOP = 0.80
PARTIAL_ACC_50HOP = 0.40


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
    pdm = summary.get("per_depth_mean_acc")
    if not pdm:
        return ("MULTIHOP_HOPFIELD_INCONCLUSIVE", "Missing per-depth accuracy.")
    pdm = {int(k): float(v) for k, v in pdm.items()}
    acc_1 = pdm.get(1, 0.0)
    acc_50 = pdm.get(50, 0.0)
    depths = sorted(pdm.keys())
    monotone = all(pdm[depths[i]] >= pdm[depths[i + 1]] - 0.02
                       for i in range(len(depths) - 1))

    if acc_50 >= PASS_ACC_50HOP and monotone:
        return ("MULTIHOP_HOPFIELD_50HOP_VALIDATED",
                f"Modern Hopfield cleanup validates 50-hop: acc_1={acc_1:.3f}, "
                f"acc_50={acc_50:.3f}. R8 B1 cleanup-side rescue works where A1/C1 failed.")
    if acc_50 < PARTIAL_ACC_50HOP:
        return ("MULTIHOP_HOPFIELD_KILLED",
                f"Modern Hopfield fails: acc_50={acc_50:.3f}<{PARTIAL_ACC_50HOP}, "
                f"acc_1={acc_1:.3f}. All three R8 rescues (A1, C1, B1) killed; "
                f"d=25 cliff is architectural, not cleanup-or-binding-algebra.")
    decay_at = None
    for d in depths:
        if pdm[d] < 0.50:
            decay_at = d
            break
    if decay_at is None:
        decay_at = depths[-1]
    return (f"MULTIHOP_HOPFIELD_PARTIAL_AT_{decay_at}",
            f"Modern Hopfield partial: acc_50={acc_50:.3f}, acc_1={acc_1:.3f}, "
            f"first decay below 0.50 at depth={decay_at}.")


def self_test_verdict():
    cases = [
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.96, 10: 0.92, 25: 0.86, 50: 0.82}},
         "MULTIHOP_HOPFIELD_50HOP_VALIDATED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.80, 10: 0.40, 25: 0.15, 50: 0.10}},
         "MULTIHOP_HOPFIELD_KILLED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.90, 10: 0.80, 25: 0.65, 50: 0.55}},
         "MULTIHOP_HOPFIELD_PARTIAL_AT_50"),
        ({}, "MULTIHOP_HOPFIELD_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def hopfield_cleanup(probe, codebook, beta=BETA_DEFAULT, n_iters=HOPFIELD_ITERS):
    """Iterated Ramsauer 2020 modern Hopfield retrieval.
    probe: (n,) bipolar state. codebook: (k, n)."""
    state = probe.clone().float()
    for _ in range(n_iters):
        sims = codebook @ state  # (k,)
        # numerically stable softmax
        sims = sims - sims.max()
        weights = torch.softmax(beta * sims, dim=0)
        state = codebook.T @ weights  # (n,)
    final_sims = codebook @ state
    return int(final_sims.argmax().item())


def run_hopfield_chain(M, start_idx, rel_idxs, target_idx, entity_atoms,
                         relation_atoms, beta, n_iters):
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        current_idx = hopfield_cleanup(probe, entity_atoms, beta, n_iters)
    return current_idx == target_idx


def run_one_seed(seed, hop_depths, n_trials, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    beta = config["beta"]
    n_iters = config["hopfield_iters"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)

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
            ok = run_hopfield_chain(M, chain_entities[0], chain_rels,
                                       chain_entities[-1], entity_atoms,
                                       relation_atoms, beta, n_iters)
            if ok:
                successes += 1
        by_depth[depth] = successes / n_trials
    return by_depth


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
              "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
              "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
              "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
              "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "beta": BETA_DEFAULT, "hopfield_iters": HOPFIELD_ITERS}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"],
                              config, device)
        per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
        print(f"  seed={seed}: " + " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]),
              flush=True)
    per_depth_mean = {}
    for d in config["hop_depths"]:
        per_depth_mean[d] = sum(per_seed[str(s)][str(d)] for s in config["seeds"]) / len(config["seeds"])
    summary = {"per_depth_mean_acc": per_depth_mean, "per_seed_acc": per_seed}
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
    out_dir = get_output_dir("wave14r_multihop_modernhopfield_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    acc_1 = summary["per_depth_mean_acc"][1]
    oracle.assert_baseline_high("hopfield_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_modernhopfield_v1")
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
