"""Multi-hop 1-hop ceiling test: does Hadamard entity codebook fix it?

Follow-up to wave14x_multihop_N_scaling. The 1-hop ceiling at ~0.95-0.97
isn't moved by N-scaling (slope +0.01 per log2(N)). Hypothesis: dense
random-BSC entity codebook creates cross-talk in cleanup. Hadamard
entities (exactly orthogonal) would eliminate that cross-talk.

Two arms, same script:
  Arm A: entity_atoms = NUM_ENTITIES random Sylvester Hadamard rows
  Arm B: entity_atoms = NUM_ENTITIES random ±1 vectors (v3 baseline)

Relation codebook is random ±1 in both arms (relation algebra unchanged).
Multi-hop chain test at depths {1, 10, 50}, NUM_FACTS=100, 3 seeds.

Pre-reg: preregs/2026-05-21_wave14z_multihop_hadamard_entities.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


# Import v3 (multihop) and v1 (orthkeys, has sylvester_hadamard) functions.
_v3_path = REPO / "experiments" / "exp_wave14t_multihop_v3.py"
spec = importlib.util.spec_from_file_location("multihop_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)

_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec2 = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v1)


N_FULL = 4096
N_SMOKE = 512
NUM_ENTITIES_FULL = 200
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 20
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = 100
NUM_FACTS_SMOKE = 20
HOP_DEPTHS_FULL = [1, 10, 50]
HOP_DEPTHS_SMOKE = [1, 10]
N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 5
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]

PASS_ACC_1HOP_HIGH = 0.99
PASS_HELP_THRESHOLD = 0.02
PASS_PARTIAL_THRESHOLD = 0.005
HURT_THRESHOLD = -0.05  # Hadamard significantly worse than random


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_verdict(summary: dict) -> tuple[str, str]:
    arms = summary.get("by_arm")
    if not arms or "hadamard" not in arms or "random_bsc" not in arms:
        return ("HADAMARD_ENTITIES_INCONCLUSIVE", "Missing arm data.")

    h_row = arms["hadamard"]
    r_row = arms["random_bsc"]
    if "acc_by_depth" not in h_row or "acc_by_depth" not in r_row:
        return ("HADAMARD_ENTITIES_INCONCLUSIVE", "Missing acc_by_depth.")

    acc_h_1 = float(h_row["acc_by_depth"]["1"])
    acc_r_1 = float(r_row["acc_by_depth"]["1"])
    delta_1 = acc_h_1 - acc_r_1

    # Decision tree (note: HURT check first because it's the most diagnostic)
    if delta_1 <= HURT_THRESHOLD:
        return ("HADAMARD_HURTS",
                f"Hadamard arm acc_1hop={acc_h_1:.3f}; random_bsc acc_1hop={acc_r_1:.3f}; "
                f"delta = {delta_1:+.3f} <= {HURT_THRESHOLD}. Hadamard codebook BREAKS "
                f"multi-hop storage. Likely cause: BSC bind algebra (Hadamard_a*Hadamard_b="
                f"Hadamard_{{a XOR b}}) makes distractor binds collide with stored entities. "
                f"The orthogonal-codebook intuition from key-erase doesn't transfer to "
                f"multi-hop because bind itself isn't permutation-preserving on a sampled "
                f"Hadamard subset.")

    if acc_h_1 >= PASS_ACC_1HOP_HIGH and delta_1 >= PASS_HELP_THRESHOLD:
        return ("HADAMARD_LIFTS_1HOP_CEILING",
                f"Hadamard arm acc_1hop={acc_h_1:.3f} >= {PASS_ACC_1HOP_HIGH}; "
                f"random_bsc acc_1hop={acc_r_1:.3f}; delta = {delta_1:+.3f} >= "
                f"{PASS_HELP_THRESHOLD}. The 1-hop ceiling is moved by the entity "
                f"codebook structure; cleanup cross-talk was the bottleneck.")

    if abs(delta_1) <= PASS_PARTIAL_THRESHOLD:
        return ("HADAMARD_NO_HELP",
                f"Hadamard arm acc_1hop={acc_h_1:.3f}; random_bsc acc_1hop={acc_r_1:.3f}; "
                f"|delta| = {abs(delta_1):.3f} <= {PASS_PARTIAL_THRESHOLD}. Entity-codebook "
                f"choice is not the bottleneck; mechanism limit is elsewhere "
                f"(binding, superposition, or substrate-intrinsic).")

    if delta_1 >= PASS_HELP_THRESHOLD:
        return ("HADAMARD_MEANINGFUL_HELP",
                f"Hadamard arm acc_1hop={acc_h_1:.3f}; random_bsc acc_1hop={acc_r_1:.3f}; "
                f"delta = {delta_1:+.3f} >= {PASS_HELP_THRESHOLD} but < ceiling. "
                f"Orthogonal entity codebook is a meaningful improvement but more is "
                f"needed for high-fidelity 1-hop.")

    return ("HADAMARD_PARTIAL_HELP",
            f"Hadamard arm acc_1hop={acc_h_1:.3f}; random_bsc acc_1hop={acc_r_1:.3f}; "
            f"delta = {delta_1:+.3f} in ({PASS_PARTIAL_THRESHOLD}, "
            f"{PASS_HELP_THRESHOLD}). Cleanup is part of the bottleneck but not all of it.")


def self_test_verdict() -> None:
    def mk(by_depth, max_pairwise=0.0):
        return {"acc_by_depth": {str(k): v for k, v in by_depth.items()},
                "max_pairwise_ip": max_pairwise}

    cases = [
        # 1. LIFTS_CEILING: hadamard 0.995 vs random 0.95
        ({"by_arm": {
            "hadamard": mk({1: 0.995, 10: 0.85, 50: 0.40}),
            "random_bsc": mk({1: 0.95, 10: 0.70, 50: 0.25})}},
         "HADAMARD_LIFTS_1HOP_CEILING"),
        # 2. MEANINGFUL_HELP: hadamard 0.97 vs random 0.94 (delta=0.03)
        ({"by_arm": {
            "hadamard": mk({1: 0.97, 10: 0.80, 50: 0.30}),
            "random_bsc": mk({1: 0.94, 10: 0.72, 50: 0.25})}},
         "HADAMARD_MEANINGFUL_HELP"),
        # 3. NO_HELP: hadamard 0.95 vs random 0.948 (|delta|=0.002)
        ({"by_arm": {
            "hadamard": mk({1: 0.95, 10: 0.75, 50: 0.25}),
            "random_bsc": mk({1: 0.948, 10: 0.745, 50: 0.245})}},
         "HADAMARD_NO_HELP"),
        # 4. PARTIAL_HELP: delta 0.01
        ({"by_arm": {
            "hadamard": mk({1: 0.96, 10: 0.78, 50: 0.27}),
            "random_bsc": mk({1: 0.95, 10: 0.75, 50: 0.25})}},
         "HADAMARD_PARTIAL_HELP"),
        # 5. HURTS: hadamard 0.6 vs random 1.0 (delta=-0.4) — the smoke result
        ({"by_arm": {
            "hadamard": mk({1: 0.60, 10: 0.20, 50: 0.0}),
            "random_bsc": mk({1: 1.00, 10: 0.50, 50: 0.15})}},
         "HADAMARD_HURTS"),
        # 6. INCONCLUSIVE
        ({}, "HADAMARD_ENTITIES_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_hadamard_entity_codebook(num_entities: int, N: int,
                                    cpu_gen: torch.Generator,
                                    device: torch.device) -> torch.Tensor:
    """Sample num_entities distinct rows of N×N Sylvester Hadamard."""
    if num_entities > N:
        raise ValueError(f"num_entities ({num_entities}) > N ({N})")
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N:
        raise ValueError(f"N={N} must be power of 2 for Hadamard codebook")
    H = v1.sylvester_hadamard(n_log2, device)
    perm = torch.randperm(N, generator=cpu_gen)[:num_entities].to(device)
    return H[perm]


def run_one_seed(seed: int, codebook_type: str, config: dict,
                   device: torch.device) -> dict:
    """Variant of v3.run_one_seed: entity codebook depends on codebook_type."""
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    hop_depths = config["hop_depths"]
    n_trials = config["n_trials"]

    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    if codebook_type == "hadamard":
        entity_atoms = make_hadamard_entity_codebook(num_entities, N, cpu_gen, device)
    elif codebook_type == "random_bsc":
        entity_atoms = v3.make_bsc_codebook(num_entities, N, gen, device)
    else:
        raise ValueError(f"unknown codebook_type {codebook_type}")
    relation_atoms = v3.make_bsc_codebook(num_relations, N, gen, device)

    # Codebook pairwise stats
    ent_ips = (entity_atoms @ entity_atoms.T) / N
    mask = ~torch.eye(num_entities, dtype=torch.bool, device=device)
    max_pairwise = float(ent_ips[mask].abs().max())

    by_depth = {}
    for depth in hop_depths:
        if depth > num_entities - 1 or depth > num_facts:
            by_depth[depth] = 0.0
            continue
        correct = 0
        for trial in range(n_trials):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, num_relations, (1,),
                                              generator=cpu_gen).item())
                          for _ in range(depth)]
            n_distractors = max(0, num_facts - depth)
            M = v3.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, num_relations,
                                    entity_atoms, relation_atoms, cpu_gen, device)
            ok = v3.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                                entity_atoms, relation_atoms)
            if ok:
                correct += 1
        by_depth[depth] = correct / n_trials
    return {"seed": seed, "by_depth": by_depth, "max_pairwise_ip": max_pairwise}


def run_arm(codebook_type: str, config: dict, device: torch.device) -> dict:
    """Run all seeds for one arm, aggregate."""
    per_seed_runs = []
    for seed in config["seeds"]:
        r = run_one_seed(seed, codebook_type, config, device)
        per_seed_runs.append(r)
        accs_str = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
        print(f"  arm={codebook_type} seed={seed}  {accs_str}  "
              f"max_ip={r['max_pairwise_ip']:.4f}", flush=True)

    acc_by_depth = {}
    for d in config["hop_depths"]:
        vals = [r["by_depth"][d] for r in per_seed_runs]
        acc_by_depth[str(d)] = sum(vals) / len(vals)
    per_depth_mean = {d: acc_by_depth[str(d)] for d in config["hop_depths"]}
    retention = v3.per_hop_retention_rate(per_depth_mean)
    return {"acc_by_depth": acc_by_depth,
            "retention_rate": retention,
            "max_pairwise_ip": max(r["max_pairwise_ip"] for r in per_seed_runs),
            "per_seed": per_seed_runs}


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
        "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
        "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[arm=hadamard] running...", flush=True)
    arm_h = run_arm("hadamard", config, device)
    print(f"[arm=random_bsc] running...", flush=True)
    arm_r = run_arm("random_bsc", config, device)

    summary = {"by_arm": {"hadamard": arm_h, "random_bsc": arm_r}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm_data in summary["by_arm"].items():
        accs_str = " ".join(f"d{d}={arm_data['acc_by_depth'][str(d)]:.4f}"
                              for d in config["hop_depths"])
        print(f"  {arm_name:12s}  {accs_str}  retention={arm_data['retention_rate']:.4f}  "
              f"max_ip={arm_data['max_pairwise_ip']:.6f}", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14z_multihop_hadamard_entities_smoke")
    log_event("experiment_started", name="wave14z_multihop_hadamard_entities",
              mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle 1: Hadamard codebook strictly orthogonal
    had_max = float(summary["by_arm"]["hadamard"]["max_pairwise_ip"])
    oracle.assert_in_range("hadamard_entity_max_ip", had_max, (0.0, 1e-6))
    # Oracle 2: random BSC codebook IPs bounded
    rnd_max = float(summary["by_arm"]["random_bsc"]["max_pairwise_ip"])
    oracle.assert_in_range("random_entity_max_ip", rnd_max, (0.0, 0.40))
    # Oracle 3: random BSC arm (the established baseline) must hit a decent floor
    # at smoke scale. The Hadamard arm is the experimental variable — its value
    # can be anywhere from 0 to 1, that's what the verdict measures.
    r_acc_1 = float(summary["by_arm"]["random_bsc"]["acc_by_depth"]["1"])
    oracle.assert_baseline_high("random_acc_1hop_smoke", r_acc_1, 0.70)

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14z_multihop_hadamard_entities",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14z_multihop_hadamard_entities")
    log_event("experiment_started", name="wave14z_multihop_hadamard_entities",
              mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14z_multihop_hadamard_entities",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
