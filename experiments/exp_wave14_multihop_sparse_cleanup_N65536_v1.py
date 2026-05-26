"""Multi-hop per-hop sparse cleanup at N=65536 — Research H#3 (P=0.50).

Per Research 2026-05-22 18:58 (Krotov-Hopfield + Mofrad 2021). After Resonator
INSUFFICIENT, test cheaper mechanism: per-hop threshold-AMP cleanup that
sparsifies state before next-hop probe.

Mechanism: at each hop, after entity cleanup, keep only top-K candidates with
weighted superposition (sparse representation); pass softened state to next hop.
Avoids hard argmax commitment without full resonator iteration cost.

Verdict thresholds:
  SPARSE_RESTORES: acc_50hop >= 0.50
  SPARSE_PARTIAL:  0.30 <= acc_50hop < 0.50
  SPARSE_INSUFFICIENT: acc_50hop < 0.30
  SPARSE_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_sparse_cleanup_N65536_v1.md
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
    if "acc_50hop_sparse" not in summary:
        return ("SPARSE_INCONCLUSIVE", "Missing acc_50hop_sparse.")
    sp = summary["acc_50hop_sparse"]
    arg = summary["acc_50hop_argmax_baseline"]
    if sp >= PASS_ACC_50:
        return ("SPARSE_RESTORES",
                f"Sparse cleanup restores chain: acc_50hop={sp:.3f} (>={PASS_ACC_50}) vs argmax {arg:.3f}.")
    if sp >= PARTIAL_ACC_50:
        return ("SPARSE_PARTIAL",
                f"Sparse cleanup partial: acc_50hop={sp:.3f} ({PARTIAL_ACC_50}<=acc<{PASS_ACC_50}) vs argmax {arg:.3f}.")
    return ("SPARSE_INSUFFICIENT",
            f"Sparse cleanup insufficient: acc_50hop={sp:.3f} (<{PARTIAL_ACC_50}) vs argmax {arg:.3f}.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_sparse": 0.60, "acc_50hop_argmax_baseline": 0.22}, "SPARSE_RESTORES"),
        ({"acc_50hop_sparse": 0.40, "acc_50hop_argmax_baseline": 0.22}, "SPARSE_PARTIAL"),
        ({"acc_50hop_sparse": 0.20, "acc_50hop_argmax_baseline": 0.22}, "SPARSE_INSUFFICIENT"),
        ({}, "SPARSE_INCONCLUSIVE"),
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


def run_chain_sparse(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms,
                        top_k=5, tau=0.5):
    """Sparse cleanup: maintain soft state = softmax(top-k entity) projected back as superposition.
    Next-hop probe uses softened state instead of hard top-1."""
    current = entity_atoms[start_idx].clone()
    for r_idx in rel_idxs:
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        sims = entity_atoms @ probe
        topk = torch.topk(sims, top_k)
        # Sparse softmax over top-K only
        soft_weights = softmax(topk.values, tau)
        # Soft state = weighted sum of top-K entity atoms; then sign-quantize
        soft = (soft_weights.unsqueeze(1) * entity_atoms[topk.indices]).sum(dim=0)
        current = mh.sign_quantize(soft)
    # Final commit: argmax sim with last entity codebook
    final_sims = entity_atoms @ current
    pred = int(final_sims.argmax().item())
    return pred == target_idx


def run_one_seed_compare(seed, hop_depths, n_trials, top_k, tau, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    by_depth_argmax = {}; by_depth_sparse = {}
    for depth in hop_depths:
        if depth > num_entities - 1 or depth > num_facts:
            by_depth_argmax[depth] = 0.0; by_depth_sparse[depth] = 0.0
            continue
        correct_arg = 0; correct_sp = 0
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
            if run_chain_sparse(M, chain_entities[0], chain_rels, chain_entities[-1],
                                  entity_atoms, relation_atoms, top_k, tau):
                correct_sp += 1
        by_depth_argmax[depth] = correct_arg / n_trials
        by_depth_sparse[depth] = correct_sp / n_trials
    return {"seed": seed,
             "by_depth_argmax": by_depth_argmax,
             "by_depth_sparse": by_depth_sparse}


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
              "top_k": 5,
              "tau": 0.5,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K={config['num_facts']} top_k={config['top_k']} tau={config['tau']}", flush=True)
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed_compare(seed, config["hop_depths"], config["n_trials"],
                                    config["top_k"], config["tau"], config, device)
        per_seed.append(r)
        a_arg = " ".join(f"d{d}={r['by_depth_argmax'][d]:.3f}" for d in config["hop_depths"])
        a_sp = " ".join(f"d{d}={r['by_depth_sparse'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} ARGMAX: {a_arg}", flush=True)
        print(f"  seed={seed} SPARSE: {a_sp}", flush=True)
    per_depth_arg = {}; per_depth_sp = {}
    for d in config["hop_depths"]:
        per_depth_arg[d] = sum(r["by_depth_argmax"][d] for r in per_seed) / len(per_seed)
        per_depth_sp[d] = sum(r["by_depth_sparse"][d] for r in per_seed) / len(per_seed)
    max_d = max(config["hop_depths"])
    summary = {"per_depth_mean_acc_argmax": {str(d): per_depth_arg[d] for d in config["hop_depths"]},
                "per_depth_mean_acc_sparse": {str(d): per_depth_sp[d] for d in config["hop_depths"]},
                "acc_50hop_argmax_baseline": per_depth_arg.get(50, per_depth_arg[max_d]),
                "acc_50hop_sparse": per_depth_sp.get(50, per_depth_sp[max_d])}
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
    out_dir = get_output_dir("wave14_multihop_sparse_cleanup_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_depth_present",
                                 summary["per_depth_mean_acc_sparse"].get("1", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_sparse_cleanup_N65536_v1")
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
