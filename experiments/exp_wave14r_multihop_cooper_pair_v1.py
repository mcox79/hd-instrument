"""Bet O - Cooper-pair gap-protected encoding for multi-hop rescue.

Each fact stored twice with independent global twists; cleanup requires both
to agree. Storage-side rescue (vs all prior cleanup/binding rescues which
KILLED). BCS-analog: single-twist corruption doesn't break the pair.

Pre-reg: preregs/2026-05-21_wave14r_multihop_cooper_pair_v1.md
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
    pdm = summary.get("per_depth_mean_acc")
    if not pdm:
        return ("BET_O_INCONCLUSIVE", "Missing per-depth.")
    pdm = {int(k): float(v) for k, v in pdm.items()}
    acc_1 = pdm.get(1, 0.0)
    acc_50 = pdm.get(50, 0.0)
    if acc_50 >= PASS_ACC_50:
        return ("BET_O_50HOP_VALIDATED",
                f"Cooper-pair encoding rescues multi-hop: acc_1={acc_1:.3f}, "
                f"acc_50={acc_50:.3f} >= {PASS_ACC_50}. Storage-side redundancy "
                f"beats single-encoding cliff. BCS analog substrate-validated.")
    if acc_50 < PARTIAL_FLOOR:
        return ("BET_O_KILLED",
                f"Cooper-pair encoding fails: acc_50={acc_50:.3f} < {PARTIAL_FLOOR}. "
                f"Storage-side redundancy axis closes; ALL multi-hop rescue axes "
                f"now exhausted (cleanup A1/B1/B3/N + encoding O). d=25 architectural "
                f"closure final.")
    depths = sorted(pdm.keys())
    decay_at = next((d for d in depths if pdm[d] < 0.50), depths[-1])
    return (f"BET_O_PARTIAL_AT_{decay_at}",
            f"Cooper-pair partial: acc_50={acc_50:.3f} in [{PARTIAL_FLOOR}, {PASS_ACC_50}). "
            f"acc_1={acc_1:.3f}. Beats single-encoding but not 2x. decay@d{decay_at}.")


def self_test_verdict():
    cases = [
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.95, 10: 0.85, 25: 0.70, 50: 0.55}},
         "BET_O_50HOP_VALIDATED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.50, 10: 0.30, 25: 0.20, 50: 0.10}},
         "BET_O_KILLED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.85, 10: 0.65, 25: 0.40, 50: 0.30}},
         "BET_O_PARTIAL_AT_25"),
        ({}, "BET_O_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_paired_factbase(chain_entities, chain_rels, n_distractors, num_entities,
                            num_relations, entity_atoms, relation_atoms,
                            twist_1, twist_2, cpu_gen, device):
    """M = sign(sum of paired triples). Each fact contributes TWO triples
    (one per twist)."""
    triples = []
    def emit(subj, rel, obj):
        for tw in (twist_1, twist_2):
            triples.append(t.sign_quantize((subj * tw) * (rel * tw) * (obj * tw)))
    for i in range(len(chain_rels)):
        subj = entity_atoms[chain_entities[i]]
        rel = relation_atoms[chain_rels[i]]
        obj = entity_atoms[chain_entities[i + 1]]
        emit(subj, rel, obj)
    if n_distractors > 0:
        ds = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        dr = torch.randint(0, num_relations, (n_distractors,), generator=cpu_gen)
        do = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        for j in range(n_distractors):
            emit(entity_atoms[int(ds[j])], relation_atoms[int(dr[j])],
                  entity_atoms[int(do[j])])
    stacked = torch.stack(triples, dim=0)
    return t.sign_quantize(stacked.sum(dim=0))


def run_cooper_chain(M, start_idx, rel_idxs, target_idx, entity_atoms,
                       relation_atoms, twist_1, twist_2):
    current_idx = start_idx
    # Pre-compute twisted entity codebooks
    ea_t1 = entity_atoms * twist_1.unsqueeze(0)
    ea_t2 = entity_atoms * twist_2.unsqueeze(0)
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe_1 = M * (current * twist_1) * (rel * twist_1)
        probe_2 = M * (current * twist_2) * (rel * twist_2)
        sims_1 = ea_t1 @ probe_1
        sims_2 = ea_t2 @ probe_2
        combined = sims_1 + sims_2  # require both to agree
        current_idx = int(combined.argmax().item())
    return current_idx == target_idx


def run_one_seed(seed, hop_depths, n_trials, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)
    # Two independent global twists
    twist_gen = torch.Generator(device=device).manual_seed(seed + 5003)
    twist_1 = 2.0 * (torch.rand(N, generator=twist_gen, device=device) > 0.5).float() - 1.0
    twist_2 = 2.0 * (torch.rand(N, generator=twist_gen, device=device) > 0.5).float() - 1.0
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
            M = build_paired_factbase(chain_entities, chain_rels, n_distractors,
                                          num_entities, num_relations, entity_atoms,
                                          relation_atoms, twist_1, twist_2, cpu_gen, device)
            ok = run_cooper_chain(M, chain_entities[0], chain_rels,
                                    chain_entities[-1], entity_atoms,
                                    relation_atoms, twist_1, twist_2)
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
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"],
                              config, device)
        per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
        print(f"  seed={seed}: " +
              " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]),
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
    out_dir = get_output_dir("wave14r_multihop_cooper_pair_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    acc_1 = summary["per_depth_mean_acc"][1]
    oracle.assert_baseline_high("cooper_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_cooper_pair_v1")
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
