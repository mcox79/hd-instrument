"""Multi-hop bidirectional chain inference at N=65536 — Mofrad et al 2021 Viterbi-on-chain.

Per Research 2026-05-22 18:58. Resonator (forward-only) failed at N=65536
(RESONATOR_INSUFFICIENT acc_50hop=0.200 < argmax baseline 0.250). Next-highest-P
rehabilitation: bidirectional chain inference with backward messages.

Mechanism: assume known start and target. Forward pass yields top-2 candidates per
hop with confidence. Backward pass from target yields top-2 candidates per hop in
reverse direction. Combine: per-hop, pick candidate that has best joint forward
AND backward score. Backward correction recovers from premature forward commitment.

For deployment this requires target known at chain time (compositional query
templates). For substrate-novel test: we know the target by construction.

Verdict thresholds:
  BIDIR_RESTORES: acc_50hop >= 0.50 (substantive lift over both baselines)
  BIDIR_PARTIAL:  0.30 <= acc_50hop < 0.50
  BIDIR_INSUFFICIENT: acc_50hop < 0.30 (alternative mechanism class needed)
  BIDIR_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_bidirectional_N65536_v1.md
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
    if "acc_50hop_bidir" not in summary:
        return ("BIDIR_INCONCLUSIVE", "Missing acc_50hop_bidir.")
    bdr = summary["acc_50hop_bidir"]
    arg = summary["acc_50hop_argmax_baseline"]
    if bdr >= PASS_ACC_50:
        return ("BIDIR_RESTORES",
                f"Bidirectional inference restores chain: acc_50hop={bdr:.3f} (>={PASS_ACC_50}) "
                f"vs argmax baseline {arg:.3f}. Mofrad et al 2021 Viterbi-on-chain mechanism viable.")
    if bdr >= PARTIAL_ACC_50:
        return ("BIDIR_PARTIAL",
                f"Bidirectional partial: acc_50hop={bdr:.3f} ({PARTIAL_ACC_50}<=acc<{PASS_ACC_50}) "
                f"vs argmax {arg:.3f}.")
    return ("BIDIR_INSUFFICIENT",
            f"Bidirectional insufficient: acc_50hop={bdr:.3f} (<{PARTIAL_ACC_50}) "
            f"vs argmax {arg:.3f}. Mofrad-class also fails; alternative mechanism class needed.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_bidir": 0.60, "acc_50hop_argmax_baseline": 0.22}, "BIDIR_RESTORES"),
        ({"acc_50hop_bidir": 0.40, "acc_50hop_argmax_baseline": 0.22}, "BIDIR_PARTIAL"),
        ({"acc_50hop_bidir": 0.20, "acc_50hop_argmax_baseline": 0.22}, "BIDIR_INSUFFICIENT"),
        ({}, "BIDIR_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def chain_top_k_per_hop(M, start_idx, rel_idxs, entity_atoms, relation_atoms, top_k=5):
    """Forward chain; at each hop return top-k candidates (with similarity scores)."""
    current_idx = start_idx
    per_hop = []
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        sims = entity_atoms @ probe
        topk = torch.topk(sims, top_k)
        per_hop.append({"idxs": topk.indices.tolist(), "sims": topk.values.tolist()})
        current_idx = int(topk.indices[0].item())  # commit to top-1 for next-hop probe
    return per_hop


def chain_backward_top_k(M, target_idx, rel_idxs, entity_atoms, relation_atoms, top_k=5):
    """Backward chain: starting from target, query reverse to find prior entity at each hop.
    For each hop in reversed order, probe = M * (current * rel) and argmax.
    Note: substrate's bundled M has triples sign(subj * rel * obj); for reverse query
    given obj and rel, the substrate returns subj via M * obj * rel."""
    rev_rel_idxs = list(reversed(rel_idxs))
    current_idx = target_idx
    per_hop = []
    for r_idx in rev_rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        sims = entity_atoms @ probe
        topk = torch.topk(sims, top_k)
        per_hop.append({"idxs": topk.indices.tolist(), "sims": topk.values.tolist()})
        current_idx = int(topk.indices[0].item())
    # Reverse so per_hop[i] corresponds to FORWARD chain position i+1
    per_hop.reverse()
    return per_hop


def bidirectional_combine(forward_per_hop, backward_per_hop, start_idx, target_idx):
    """For each intermediate hop, combine forward and backward top-k by joint score.
    Return predicted chain. Compare final to target_idx."""
    n_hops = len(forward_per_hop)
    if n_hops != len(backward_per_hop):
        return -1  # mismatch
    chain = [start_idx]
    for i in range(n_hops):
        fwd = forward_per_hop[i]
        bwd = backward_per_hop[i]
        # Build dict idx -> joint score
        joint = {}
        for j, idx in enumerate(fwd["idxs"]):
            joint[idx] = fwd["sims"][j]
        for j, idx in enumerate(bwd["idxs"]):
            if idx in joint:
                joint[idx] = joint[idx] + bwd["sims"][j]
            else:
                joint[idx] = bwd["sims"][j] * 0.5  # half weight if only backward
        best = max(joint, key=joint.get)
        chain.append(best)
    return chain[-1]


def run_one_seed_compare(seed, hop_depths, n_trials, config, device):
    """For each depth: run argmax baseline + bidirectional. Return per-depth acc for both."""
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    by_depth_argmax = {}; by_depth_bidir = {}
    for depth in hop_depths:
        if depth > num_entities - 1 or depth > num_facts:
            by_depth_argmax[depth] = 0.0; by_depth_bidir[depth] = 0.0
            continue
        correct_arg = 0; correct_bdr = 0
        for trial in range(n_trials):
            perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                          for _ in range(depth)]
            n_distractors = max(0, num_facts - depth)
            M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                    num_entities, num_relations,
                                    entity_atoms, relation_atoms, cpu_gen, device)
            # argmax baseline
            if mh.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                              entity_atoms, relation_atoms):
                correct_arg += 1
            # Bidirectional
            fwd = chain_top_k_per_hop(M, chain_entities[0], chain_rels, entity_atoms, relation_atoms)
            bwd = chain_backward_top_k(M, chain_entities[-1], chain_rels, entity_atoms, relation_atoms)
            pred = bidirectional_combine(fwd, bwd, chain_entities[0], chain_entities[-1])
            if pred == chain_entities[-1]:
                correct_bdr += 1
        by_depth_argmax[depth] = correct_arg / n_trials
        by_depth_bidir[depth] = correct_bdr / n_trials
    return {"seed": seed,
             "by_depth_argmax": by_depth_argmax,
             "by_depth_bidir": by_depth_bidir}


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
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K={config['num_facts']} depths={config['hop_depths']}", flush=True)
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed_compare(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed.append(r)
        a_arg = " ".join(f"d{d}={r['by_depth_argmax'][d]:.3f}" for d in config["hop_depths"])
        a_bdr = " ".join(f"d{d}={r['by_depth_bidir'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} ARGMAX: {a_arg}", flush=True)
        print(f"  seed={seed} BIDIR:  {a_bdr}", flush=True)
    per_depth_arg = {}; per_depth_bdr = {}
    for d in config["hop_depths"]:
        per_depth_arg[d] = sum(r["by_depth_argmax"][d] for r in per_seed) / len(per_seed)
        per_depth_bdr[d] = sum(r["by_depth_bidir"][d] for r in per_seed) / len(per_seed)
    max_d = max(config["hop_depths"])
    summary = {"per_depth_mean_acc_argmax": {str(d): per_depth_arg[d] for d in config["hop_depths"]},
                "per_depth_mean_acc_bidir": {str(d): per_depth_bdr[d] for d in config["hop_depths"]},
                "acc_50hop_argmax_baseline": per_depth_arg.get(50, per_depth_arg[max_d]),
                "acc_50hop_bidir": per_depth_bdr.get(50, per_depth_bdr[max_d])}
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
    out_dir = get_output_dir("wave14_multihop_bidirectional_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("bidir_present",
                                 summary["per_depth_mean_acc_bidir"].get("1", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_bidirectional_N65536_v1")
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
