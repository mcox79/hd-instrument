"""R8 B3 - Adaptive beta cleanup multi-hop. Closes R8 rescue list.

Per cycle 42 followup: cleanup sharpness anneals per hop:
  beta(h) = BETA_INIT / (1 + h * decay_rate)
Sweep (BETA_INIT, decay) pairs. Builds on B1 (modern Hopfield, killed) but
with hop-dependent beta to avoid over-commitment as noise accumulates.

Pre-reg: preregs/2026-05-21_wave14r_multihop_adaptive_beta_v1.md
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
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
BETA_DECAY_PAIRS_FULL = [(8.0, 0.1), (16.0, 0.2), (32.0, 0.5)]
BETA_DECAY_PAIRS_SMOKE = [(8.0, 0.1)]

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
    per_pair = summary.get("per_pair_depth")
    if not per_pair:
        return ("ADAPTIVE_BETA_INCONCLUSIVE", "Missing per_pair_depth.")
    acc50_per_pair = {}
    for k, by_d in per_pair.items():
        d50 = by_d.get("50") or by_d.get(50) or 0.0
        acc50_per_pair[k] = float(d50)
    best_k = max(acc50_per_pair.keys(), key=lambda kk: acc50_per_pair[kk])
    best_acc50 = acc50_per_pair[best_k]

    if best_acc50 < PARTIAL_FLOOR:
        return ("ADAPTIVE_BETA_KILLED",
                f"Adaptive-beta fails: best acc_50hop={best_acc50:.3f} < "
                f"{PARTIAL_FLOOR}. R8 rescue list formally closed (A1, B1, C1, B3 all "
                f"KILLED). d=25 architectural-closure stance secure. per-pair: " +
                ", ".join(f"{k}:{acc50_per_pair[k]:.3f}"
                              for k in sorted(acc50_per_pair)))
    if best_acc50 >= PASS_ACC_50:
        return ("ADAPTIVE_BETA_50HOP_VALIDATED",
                f"Adaptive-beta rescues 50-hop: best acc_50={best_acc50:.3f} >= "
                f"{PASS_ACC_50} at config {best_k}. Symptom mitigation surprisingly "
                f"works. per-pair: " + ", ".join(f"{k}:{acc50_per_pair[k]:.3f}"
                                                       for k in sorted(acc50_per_pair)))
    return (f"ADAPTIVE_BETA_PARTIAL_AT_{best_k}",
            f"Adaptive-beta partial: best acc_50={best_acc50:.3f} at config "
            f"{best_k} in [{PARTIAL_FLOOR}, {PASS_ACC_50}). per-pair: " +
            ", ".join(f"{k}:{acc50_per_pair[k]:.3f}" for k in sorted(acc50_per_pair)))


def self_test_verdict():
    def mk(acc50_by_k):
        return {"per_pair_depth": {k: {"50": v} for k, v in acc50_by_k.items()}}
    cases = [
        (mk({"a": 0.60, "b": 0.55}), "ADAPTIVE_BETA_50HOP_VALIDATED"),
        (mk({"a": 0.30, "b": 0.35}), "ADAPTIVE_BETA_PARTIAL_AT_b"),
        (mk({"a": 0.18, "b": 0.20}), "ADAPTIVE_BETA_KILLED"),
        ({}, "ADAPTIVE_BETA_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def adaptive_beta_cleanup(probe, codebook, beta_h, N):
    """Modern-Hopfield-style retrieval at beta_h. Returns argmax index."""
    state = probe.clone().float()
    for _ in range(3):  # 3 Ramsauer iterations
        sims = codebook @ state / math.sqrt(N)
        scaled = beta_h * sims
        scaled = scaled - scaled.max()
        weights = torch.softmax(scaled, dim=0)
        state = weights @ codebook
    final_sims = codebook @ state
    return int(final_sims.argmax().item())


def run_adaptive_chain(M, start_idx, rel_idxs, target_idx, entity_atoms,
                         relation_atoms, beta_init, decay_rate, N):
    current_idx = start_idx
    for h, r_idx in enumerate(rel_idxs):
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        beta_h = beta_init / (1.0 + h * decay_rate)
        current_idx = adaptive_beta_cleanup(probe, entity_atoms, beta_h, N)
    return current_idx == target_idx


def run_one_seed(seed, hop_depths, n_trials, beta_init, decay_rate, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
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
            ok = run_adaptive_chain(M, chain_entities[0], chain_rels,
                                      chain_entities[-1], entity_atoms,
                                      relation_atoms, beta_init, decay_rate, N)
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
              "beta_decay_pairs": BETA_DECAY_PAIRS_SMOKE if smoke else BETA_DECAY_PAIRS_FULL}
    print(f"[config] {config}", flush=True)
    per_pair_depth = {}
    for (beta_init, decay_rate) in config["beta_decay_pairs"]:
        key = f"beta{beta_init}_dec{decay_rate}"
        per_seed = {}
        for seed in config["seeds"]:
            by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"],
                                  beta_init, decay_rate, config, device)
            per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
            print(f"  {key} seed={seed}: " +
                  " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]),
                  flush=True)
        depth_mean = {}
        for d in config["hop_depths"]:
            depth_mean[str(d)] = sum(per_seed[str(s)][str(d)] for s in config["seeds"]) / len(config["seeds"])
        per_pair_depth[key] = depth_mean
    summary = {"per_pair_depth": per_pair_depth}
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
    out_dir = get_output_dir("wave14r_multihop_adaptive_beta_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_key = list(summary["per_pair_depth"].keys())[0]
    first_d = str(config["hop_depths"][0])
    acc_1 = summary["per_pair_depth"][first_key][first_d]
    oracle.assert_baseline_high("adaptive_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_adaptive_beta_v1")
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
