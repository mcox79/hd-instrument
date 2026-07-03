"""Chain smoother-only — uses ONLY backward messages from target, no forward refinement.

Per cycle 132 HMM_3WAY_REFUTED: soft-forward provides no gain; only backward smoother
(VAMP) helps. Test isolates: is just having a backward msg from target enough, or
does the smoother need the forward pass too?

Method: skip forward iteration; init posterior = uniform prior; compute only backward
message starting from target delta; commit per-hop using just backward msg.

Verdict thresholds:
  SMOOTHER_ONLY_WORKS: acc_50hop >= 0.70 (backward alone sufficient)
  SMOOTHER_ONLY_PARTIAL: 0.30 <= acc < 0.70
  SMOOTHER_ONLY_INSUFFICIENT: acc < 0.30 (needs forward + backward both)
  SMOOTHER_ONLY_INCONCLUSIVE

Pre-reg: minimal — diagnostic isolation of backward msg role.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_50hop_smoother_only" not in summary:
        return ("SMOOTHER_ONLY_INCONCLUSIVE", "Missing.")
    s = summary["acc_50hop_smoother_only"]
    a = summary["acc_50hop_argmax_baseline"]
    if s >= 0.70:
        return ("SMOOTHER_ONLY_WORKS",
                f"Backward msg alone sufficient: acc={s:.3f}>=0.70 vs argmax {a:.3f}.")
    if s >= 0.30:
        return ("SMOOTHER_ONLY_PARTIAL", f"Partial: acc={s:.3f}, argmax={a:.3f}.")
    return ("SMOOTHER_ONLY_INSUFFICIENT", f"Backward alone insufficient: acc={s:.3f}, argmax={a:.3f}.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_smoother_only": 0.80, "acc_50hop_argmax_baseline": 0.22}, "SMOOTHER_ONLY_WORKS"),
        ({"acc_50hop_smoother_only": 0.40, "acc_50hop_argmax_baseline": 0.22}, "SMOOTHER_ONLY_PARTIAL"),
        ({"acc_50hop_smoother_only": 0.20, "acc_50hop_argmax_baseline": 0.22}, "SMOOTHER_ONLY_INSUFFICIENT"),
        ({}, "SMOOTHER_ONLY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def log_softmax(x):
    return x - torch.logsumexp(x, dim=0)


def chain_smoother_only(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms):
    """Backward-only: no forward iteration; init flat prior; backward msg from target."""
    depth = len(rel_idxs)
    K = entity_atoms.shape[0]
    # Backward pass: start from target delta, propagate backward; same logic as VAMP backward
    target_prior = torch.full((K,), -1e9, device=entity_atoms.device)
    target_prior[target_idx] = 0.0
    smoothed = [None] * (depth + 1)
    smoothed[depth] = target_prior.clone()
    # propagate backward; no forward forward_log_post (uniform)
    for hop in range(depth - 1, -1, -1):
        rel = relation_atoms[rel_idxs[hop]].float()
        weights_next = torch.exp(smoothed[hop + 1] - smoothed[hop + 1].max())
        weights_next = weights_next / weights_next.sum()
        x_next = (weights_next.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
        probe_back = M.float() * (mh.sign_quantize(x_next) * rel)
        sims_back = entity_atoms.float() @ probe_back
        backward_log_msg = log_softmax(sims_back)
        smoothed[hop] = backward_log_msg.clone()
    # Final commit at hop=depth
    pred = int(smoothed[depth].argmax().item())
    return pred == target_idx


def run_one_seed(seed, depth, n_trials, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    c_arg = 0; c_smooth = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain_entities = perm.tolist()
        chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                      for _ in range(depth)]
        n_distractors = max(0, num_facts - depth)
        Mb = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if mh.run_chain(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                          entity_atoms, relation_atoms):
            c_arg += 1
        if chain_smoother_only(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                  entity_atoms, relation_atoms):
            c_smooth += 1
    return {"argmax": c_arg / n_trials, "smoother": c_smooth / n_trials}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "depth": 25 if smoke else 50,
              "n_trials": 5 if smoke else 20,
              "seeds": [17] if smoke else [17, 23]}
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed(seed, config["depth"], config["n_trials"], config, device)
        per_seed.append(r)
        print(f"  seed={seed}: argmax={r['argmax']:.3f}, smoother_only={r['smoother']:.3f}", flush=True)
    summary = {"acc_50hop_argmax_baseline": sum(r["argmax"] for r in per_seed) / len(per_seed),
                "acc_50hop_smoother_only": sum(r["smoother"] for r in per_seed) / len(per_seed),
                "depth": config["depth"]}
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
    out_dir = get_output_dir("wave14_chain_smoother_only_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("smoother_present",
                                 summary["acc_50hop_smoother_only"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_chain_smoother_only_v1")
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
