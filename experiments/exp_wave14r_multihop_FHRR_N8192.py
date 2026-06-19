"""R8 A1 - Multi-hop FHRR (continuous-group binding) vs BSC closure cliff.

R8 identified BSC's Walsh-XOR closure as the v17/v23 d=25 cliff mechanism.
FHRR's continuous phase torus has no finite closure subgroup; chained binds
should avoid collision cross-talk. A1 is R8's top rescue.

Mechanism per R8:
  entities: z_i in (C, |z|=1)^N, theta ~ Uniform[0, 2*pi)
  relations: same construction (complex unit-magnitude phasors)
  bind: z1 * z2 (element-wise complex multiply)
  inverse: conj(z)  (since |z|=1 implies z^-1 = conj(z))
  fact bundle: M = sum(subj * rel * obj) over all stored triples (NO quantization)
  unbind for hop: M * conj(current * rel) ~= obj when (current, rel, obj) in M
  cleanup: argmax over codebook by complex inner product magnitude

Pre-reg: preregs/2026-05-21_wave14r_multihop_FHRR_N8192.md
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

# Inherit verdict thresholds + helpers from wave14t (the BSC multihop reference)
_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)

N_FULL = 8192
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
        return ("MULTIHOP_FHRR_INCONCLUSIVE", "Missing per-depth accuracy.")
    pdm = {int(k): float(v) for k, v in pdm.items()}
    acc_1 = pdm.get(1, 0.0)
    acc_50 = pdm.get(50, 0.0)
    depths = sorted(pdm.keys())
    monotone = all(pdm[depths[i]] >= pdm[depths[i + 1]] - 0.02
                       for i in range(len(depths) - 1))

    if acc_50 >= PASS_ACC_50HOP and monotone:
        return ("MULTIHOP_FHRR_50HOP_VALIDATED",
                f"FHRR 50-hop reasoning validated: acc_1={acc_1:.3f}, "
                f"acc_50={acc_50:.3f}, monotone-decreasing. R8 A1 rescue confirmed; "
                f"continuous group avoids BSC closure cliff at d=25.")
    if acc_50 < PARTIAL_ACC_50HOP:
        return ("MULTIHOP_FHRR_KILLED",
                f"FHRR 50-hop fails: acc_50={acc_50:.3f} < {PARTIAL_ACC_50HOP}. "
                f"acc_1={acc_1:.3f}. R8 A1 rescue does not rehabilitate multi-hop "
                f"depth cliff. See prereg pre-armed rescue sketches.")
    # Find decay point — first depth crossing 0.50, else the deepest tested depth
    decay_at = None
    for d in depths:
        if pdm[d] < 0.50:
            decay_at = d
            break
    if decay_at is None:
        decay_at = depths[-1]
    return (f"MULTIHOP_FHRR_PARTIAL_AT_{decay_at}",
            f"FHRR partial: acc_50={acc_50:.3f} in [{PARTIAL_ACC_50HOP}, {PASS_ACC_50HOP}). "
            f"acc_1={acc_1:.3f}. First decay below 0.50 at depth={decay_at}.")


def self_test_verdict():
    cases = [
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.95, 10: 0.92, 25: 0.88, 50: 0.85}},
         "MULTIHOP_FHRR_50HOP_VALIDATED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.85, 10: 0.50, 25: 0.20, 50: 0.10}},
         "MULTIHOP_FHRR_KILLED"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.90, 10: 0.80, 25: 0.65, 50: 0.55}},
         "MULTIHOP_FHRR_PARTIAL_AT_50"),
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.90, 10: 0.30, 25: 0.55, 50: 0.50}},
         "MULTIHOP_FHRR_PARTIAL_AT_10"),
        ({}, "MULTIHOP_FHRR_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_fhrr_phasors(k, n, gen, device):
    """Return (k, n) complex64 tensor of unit-magnitude phasors with random phases."""
    theta = torch.rand((k, n), generator=gen, device=device) * (2.0 * math.pi)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def fhrr_bind(a, b):
    return a * b  # element-wise complex multiply


def fhrr_unbind(a, b):
    return a * b.conj()


def cleanup_complex_argmax(noisy, codebook):
    """Return index in codebook of phasor with max |<codebook_i, noisy>|.
    noisy: (n,) complex; codebook: (k, n) complex."""
    sims = (codebook.conj() * noisy.unsqueeze(0)).sum(dim=-1)
    return int(sims.abs().argmax().item())


def build_fhrr_factbase(chain_entities, chain_rels, n_distractors, num_entities,
                          num_relations, entity_phasors, relation_phasors, cpu_gen, device):
    """M = sum of (subj * rel * obj) across all triples. No quantization."""
    triples = []
    for i in range(len(chain_rels)):
        subj = entity_phasors[chain_entities[i]]
        rel = relation_phasors[chain_rels[i]]
        obj = entity_phasors[chain_entities[i + 1]]
        triples.append(fhrr_bind(fhrr_bind(subj, rel), obj))
    if n_distractors > 0:
        dist_subj_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        dist_rel_idx = torch.randint(0, num_relations, (n_distractors,), generator=cpu_gen)
        dist_obj_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        for j in range(n_distractors):
            subj = entity_phasors[int(dist_subj_idx[j])]
            rel = relation_phasors[int(dist_rel_idx[j])]
            obj = entity_phasors[int(dist_obj_idx[j])]
            triples.append(fhrr_bind(fhrr_bind(subj, rel), obj))
    return torch.stack(triples, dim=0).sum(dim=0)


def run_fhrr_chain(M, start_idx, rel_idxs, target_idx, entity_phasors, relation_phasors):
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_phasors[current_idx]
        rel = relation_phasors[r_idx]
        # Unbind (current, rel) from M to extract noisy obj phasor
        probe = fhrr_unbind(M, fhrr_bind(current, rel))
        current_idx = cleanup_complex_argmax(probe, entity_phasors)
    return current_idx == target_idx


def run_one_seed(seed, hop_depths, n_trials, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_phasors = make_fhrr_phasors(num_entities, N, gen, device)
    relation_phasors = make_fhrr_phasors(num_relations, N, gen, device)

    by_depth = {}
    for depth in hop_depths:
        if depth > num_entities - 1:
            by_depth[depth] = 0.0
            continue
        # n_distractors = NUM_FACTS - depth so M holds depth chain triples + distractors
        n_distractors = max(0, num_facts - depth)
        successes = 0
        for trial in range(n_trials):
            chain_entities = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1].tolist()
            chain_rels = torch.randint(0, num_relations, (depth,), generator=cpu_gen).tolist()
            M = build_fhrr_factbase(chain_entities, chain_rels, n_distractors,
                                       num_entities, num_relations, entity_phasors,
                                       relation_phasors, cpu_gen, device)
            ok = run_fhrr_chain(M, chain_entities[0], chain_rels,
                                  chain_entities[-1], entity_phasors, relation_phasors)
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
    out_dir = get_output_dir("wave14r_multihop_FHRR_N8192_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    acc_1 = summary["per_depth_mean_acc"][1]
    oracle.assert_baseline_high("FHRR_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_FHRR_N8192")
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
