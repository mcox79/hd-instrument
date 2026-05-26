"""Bet N - Soft cleanup multi-hop. Strategy IMMEDIATE per cycle 42 followup.

R16 identified cleanup amplification as mechanism extending substrate d from
RMT-naive 7 to empirical 25. Bet N tests if AMPLIFYING that further pushes
d past 25.

Mechanism (per cap_map v57):
  probe = M * (current * rel)            # BSC unbind
  sims = codebook @ probe / sqrt(N)
  weights = softmax(N * sims / tau)      # broad weighting at temperature tau
  next_soft = weights @ codebook         # blended entity (soft state)
  current = sign(next_soft)              # quantize once to keep BSC ops

Sweep tau in {0.5, 1.0, 2.0, 4.0}. Different from B1 Modern Hopfield
(Ramsauer exponential capacity with multi-iteration retrieval).

Pre-reg: preregs/2026-05-21_wave14r_multihop_soft_cleanup_v1.md
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
TAUS_FULL = [0.5, 1.0, 2.0, 4.0]
TAUS_SMOKE = [1.0]

PASS_ACC_50 = 0.50  # per Strategy cap_map v57 Bet N pass criterion
PARTIAL_FLOOR = 0.22  # FHRR's acc_50; Bet N must beat by 2x for PASS


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
    by_tau = summary.get("per_tau_depth")
    if not by_tau:
        return ("BET_N_INCONCLUSIVE", "Missing per-tau-depth.")
    # Find acc_50 per tau
    acc50_per_tau = {}
    for tau, by_depth in by_tau.items():
        d50 = by_depth.get("50") or by_depth.get(50) or 0.0
        acc50_per_tau[float(tau)] = float(d50)
    best_tau = max(acc50_per_tau.keys(), key=lambda t: acc50_per_tau[t])
    best_acc50 = acc50_per_tau[best_tau]

    if best_acc50 <= PARTIAL_FLOOR:
        return ("BET_N_KILLED",
                f"Soft cleanup fails: best acc_50hop={best_acc50:.3f} <= {PARTIAL_FLOOR} "
                f"(FHRR floor) at all tau. Cleanup amplification axis CLOSED. "
                f"d=25 architectural-closure stance becomes secure. per-tau: " +
                ", ".join(f"tau={t}:{acc50_per_tau[t]:.3f}" for t in sorted(acc50_per_tau)))
    if best_acc50 >= PASS_ACC_50:
        return ("BET_N_PASS",
                f"Soft cleanup pushes acc_50hop={best_acc50:.3f} >= {PASS_ACC_50} at "
                f"tau={best_tau}. Cleanup amplification rescues multi-hop d=50. "
                f"per-tau: " + ", ".join(f"tau={t}:{acc50_per_tau[t]:.3f}"
                                            for t in sorted(acc50_per_tau)))
    return ("BET_N_PARTIAL",
            f"Soft cleanup partial: best acc_50hop={best_acc50:.3f} at tau={best_tau} "
            f"in ({PARTIAL_FLOOR}, {PASS_ACC_50}). Beats FHRR but doesn't clear 2x bar. "
            f"per-tau: " + ", ".join(f"tau={t}:{acc50_per_tau[t]:.3f}"
                                       for t in sorted(acc50_per_tau)))


def self_test_verdict():
    def mk(acc50_by_tau):
        return {"per_tau_depth": {str(t): {"50": v} for t, v in acc50_by_tau.items()}}
    cases = [
        (mk({0.5: 0.55, 1.0: 0.60, 2.0: 0.65, 4.0: 0.50}), "BET_N_PASS"),
        (mk({0.5: 0.30, 1.0: 0.35, 2.0: 0.40, 4.0: 0.25}), "BET_N_PARTIAL"),
        (mk({0.5: 0.15, 1.0: 0.18, 2.0: 0.22, 4.0: 0.15}), "BET_N_KILLED"),
        ({}, "BET_N_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def soft_cleanup(probe, codebook, tau, N):
    """Soft cleanup: weighted blend over codebook by softmax(N*cos/tau).
    Returns the SIGN-quantized blended state (keeps BSC algebra for next hop)."""
    sims = (codebook @ probe) / math.sqrt(N)
    # numerically stable softmax
    scaled = N * sims / tau
    scaled = scaled - scaled.max()
    weights = torch.softmax(scaled, dim=0)
    blend = weights @ codebook
    # Quantize back to BSC for next hop's multiplicative ops
    out = torch.sign(blend)
    return torch.where(out == 0, torch.ones_like(out), out)


def run_soft_chain(M, start_idx, rel_idxs, target_idx, entity_atoms,
                     relation_atoms, tau, N):
    """Multi-hop with soft cleanup."""
    current = entity_atoms[start_idx].clone()
    for r_idx in rel_idxs:
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        current = soft_cleanup(probe, entity_atoms, tau, N)
    # Final argmax over codebook to pick the predicted entity
    final_sims = entity_atoms @ current
    return int(final_sims.argmax().item()) == target_idx


def run_one_seed(seed, hop_depths, n_trials, tau, config, device):
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
            ok = run_soft_chain(M, chain_entities[0], chain_rels,
                                  chain_entities[-1], entity_atoms,
                                  relation_atoms, tau, N)
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
              "taus": TAUS_SMOKE if smoke else TAUS_FULL}
    print(f"[config] {config}", flush=True)
    per_tau_depth = {}
    per_tau_seed = {}
    for tau in config["taus"]:
        per_seed = {}
        for seed in config["seeds"]:
            by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"],
                                  tau, config, device)
            per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
            print(f"  tau={tau} seed={seed}: " +
                  " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]),
                  flush=True)
        # Mean across seeds
        depth_mean = {}
        for d in config["hop_depths"]:
            depth_mean[str(d)] = sum(per_seed[str(s)][str(d)] for s in config["seeds"]) / len(config["seeds"])
        per_tau_depth[str(tau)] = depth_mean
        per_tau_seed[str(tau)] = per_seed
    summary = {"per_tau_depth": per_tau_depth, "per_tau_seed": per_tau_seed}
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
    out_dir = get_output_dir("wave14r_multihop_soft_cleanup_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_tau = str(config["taus"][0])
    first_d = str(config["hop_depths"][0])
    acc_1 = summary["per_tau_depth"][first_tau][first_d]
    oracle.assert_baseline_high("soft_1hop", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_soft_cleanup_v1")
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
