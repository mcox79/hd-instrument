"""Multi-hop chain with Resonator Network per-hop iteration at N=65536.

Per Research 2026-05-22 18:58 multihop_chain_rehabilitation_N65536. MULTIHOP_N65K_KILLED
verdict (this cycle) showed acc_50hop=0.217 at N=65536 (3.5x worse than N=4096 cycle 96
0.767). Mechanism diagnosis: signal-eigenvalue near-degeneracy at large N causes
within-K-dim signal-subspace drift; argmax commits prematurely.

Rehabilitation (Frady-Kent-Olshausen-Sommer 2020 Neural Computation 32:12): replace
per-hop argmax with T iterations of resonator dynamics that maintain superposition
estimate and iteratively resolve K-dim signal-subspace mixture before committing.

Predicted acc_50hop with resonator (Research): 0.45 - 0.65; falsification at <0.30.

Verdict thresholds:
  RESONATOR_RESTORES: acc_50hop >= 0.50 (substantial improvement over 0.217 baseline)
  RESONATOR_PARTIAL:  0.30 <= acc_50hop < 0.50 (modest improvement)
  RESONATOR_INSUFFICIENT: acc_50hop < 0.30 (falsifies rehabilitation hypothesis)
  RESONATOR_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_resonator_N65536_v1.md
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

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


PASS_ACC_50 = 0.50
PARTIAL_ACC_50 = 0.30


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_50hop_resonator" not in summary:
        return ("RESONATOR_INCONCLUSIVE", "Missing acc_50hop_resonator.")
    a_res = summary["acc_50hop_resonator"]
    a_arg = summary["acc_50hop_argmax_baseline"]
    if a_res >= PASS_ACC_50:
        return ("RESONATOR_RESTORES",
                f"Resonator restores chain composition: acc_50hop={a_res:.3f} (>={PASS_ACC_50}) "
                f"vs argmax baseline {a_arg:.3f}. Frady et al. 2020 mechanism viable at N=65536.")
    if a_res >= PARTIAL_ACC_50:
        return ("RESONATOR_PARTIAL",
                f"Resonator partial: acc_50hop={a_res:.3f} ({PARTIAL_ACC_50}<=acc<{PASS_ACC_50}) "
                f"vs argmax baseline {a_arg:.3f}. Some lift but below substantive threshold.")
    return ("RESONATOR_INSUFFICIENT",
            f"Resonator insufficient: acc_50hop={a_res:.3f} (<{PARTIAL_ACC_50}) "
            f"vs argmax baseline {a_arg:.3f}. Research's rehabilitation hypothesis falsified; "
            f"substrate-level restructuring needed.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_resonator": 0.55, "acc_50hop_argmax_baseline": 0.22}, "RESONATOR_RESTORES"),
        ({"acc_50hop_resonator": 0.40, "acc_50hop_argmax_baseline": 0.22}, "RESONATOR_PARTIAL"),
        ({"acc_50hop_resonator": 0.20, "acc_50hop_argmax_baseline": 0.22}, "RESONATOR_INSUFFICIENT"),
        ({}, "RESONATOR_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def softmax(scores, tau):
    s = scores / tau
    s = s - s.max()
    e = torch.exp(s)
    return e / e.sum()


def run_chain_resonator(M, start_idx, rel_idxs, target_idx,
                          entity_atoms, relation_atoms, T_inner=20, tau_anneal=True):
    """Resonator chain: per-hop T-step iteration before committing.
    Returns True iff final committed idx == target_idx."""
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)  # noisy estimate of next entity
        # Warm-start: softmax-weighted superposition
        scores = entity_atoms @ probe
        tau = 1.0
        w = softmax(scores, tau)
        x_hat = (w.unsqueeze(1) * entity_atoms).sum(dim=0)
        # Resonator iterations
        for t in range(T_inner):
            tau_t = 1.0 / (1.0 + 0.5 * t) if tau_anneal else 0.5
            # Sign-based resonator (Frady et al. 2020): x = sign(C^T sign(C x))
            x_sign = torch.sign(entity_atoms.T @ torch.sign(entity_atoms @ x_hat))
            x_sign = torch.where(x_sign == 0, torch.ones_like(x_sign), x_sign)
            scores = entity_atoms @ x_sign
            w = softmax(scores, tau_t)
            x_hat = (w.unsqueeze(1) * entity_atoms).sum(dim=0)
        # Commit
        current_idx = int(scores.argmax().item())
    return current_idx == target_idx


def run_one_seed_compare(seed, hop_depths, n_trials, T_inner, config, device):
    """Per seed: run BOTH argmax baseline and resonator at same chain instances."""
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    by_depth_argmax = {}; by_depth_resonator = {}
    for depth in hop_depths:
        if depth > num_entities - 1 or depth > num_facts:
            by_depth_argmax[depth] = 0.0; by_depth_resonator[depth] = 0.0
            continue
        correct_arg = 0; correct_res = 0
        for trial in range(n_trials):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                          for _ in range(depth)]
            n_distractors = max(0, num_facts - depth)
            M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, num_relations,
                                    entity_atoms, relation_atoms, cpu_gen, device)
            if mh.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                              entity_atoms, relation_atoms):
                correct_arg += 1
            if run_chain_resonator(M, chain_entities[0], chain_rels, chain_entities[-1],
                                      entity_atoms, relation_atoms, T_inner):
                correct_res += 1
        by_depth_argmax[depth] = correct_arg / n_trials
        by_depth_resonator[depth] = correct_res / n_trials
    return {"seed": seed,
             "by_depth_argmax": by_depth_argmax,
             "by_depth_resonator": by_depth_resonator}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "hop_depths": [1, 25] if smoke else [1, 5, 10, 25, 50],
              "n_trials": 5 if smoke else 20,
              "T_inner": 10 if smoke else 20,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K={config['num_facts']} T_inner={config['T_inner']}", flush=True)
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed_compare(seed, config["hop_depths"], config["n_trials"],
                                    config["T_inner"], config, device)
        per_seed.append(r)
        a_arg = " ".join(f"d{d}={r['by_depth_argmax'][d]:.3f}" for d in config["hop_depths"])
        a_res = " ".join(f"d{d}={r['by_depth_resonator'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} ARGMAX:  {a_arg}", flush=True)
        print(f"  seed={seed} RESONATOR: {a_res}", flush=True)
    per_depth_arg = {}; per_depth_res = {}
    for d in config["hop_depths"]:
        per_depth_arg[d] = sum(r["by_depth_argmax"][d] for r in per_seed) / len(per_seed)
        per_depth_res[d] = sum(r["by_depth_resonator"][d] for r in per_seed) / len(per_seed)
    max_d = max(config["hop_depths"])
    summary = {"per_depth_mean_acc_argmax": {str(d): per_depth_arg[d] for d in config["hop_depths"]},
                "per_depth_mean_acc_resonator": {str(d): per_depth_res[d] for d in config["hop_depths"]},
                "acc_50hop_argmax_baseline": per_depth_arg.get(50, per_depth_arg[max_d]),
                "acc_50hop_resonator": per_depth_res.get(50, per_depth_res[max_d]),
                "T_inner": config["T_inner"]}
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
    out_dir = get_output_dir("wave14_multihop_resonator_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_depth_present",
                                 summary["per_depth_mean_acc_resonator"].get("1", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_resonator_N65536_v1")
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
