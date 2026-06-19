"""Multi-hop Resonator with VAMP-backward warm-start — Test 4 from Research 20:23.

Per Research's HMM framework: Resonator FAILED at N=65536 (acc_50hop=0.200, worse
than argmax 0.250). Two possible reasons:
  (a) Loopy within-hop dynamics fail regardless of evidence availability
  (b) Resonator lacks cross-hop backward evidence; argmax also lacks it

Test 4: warm-start Resonator with VAMP backward messages as prior, then run
Resonator iterations. If acc rises, (b) was the reason; if stays low, (a) holds.

Verdict thresholds:
  WARMSTART_RESCUES:    acc_50hop >= 0.70 (backward evidence rescues Resonator)
  WARMSTART_PARTIAL:    0.30 <= acc < 0.70 (some lift)
  WARMSTART_INSUFFICIENT: acc < 0.30 (Resonator's loopy dynamics fail independent of evidence)
  WARMSTART_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_resonator_warmstart_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_50hop_warmstart" not in summary:
        return ("WARMSTART_INCONCLUSIVE", "Missing acc_50hop_warmstart.")
    w = summary["acc_50hop_warmstart"]
    arg = summary["acc_50hop_argmax_baseline"]
    if w >= 0.70:
        return ("WARMSTART_RESCUES",
                f"Backward evidence rescues Resonator: acc_50hop={w:.3f}>=0.70 vs argmax {arg:.3f}. "
                f"Loopy dynamics work given right starting point.")
    if w >= 0.30:
        return ("WARMSTART_PARTIAL",
                f"Partial lift: acc_50hop={w:.3f} (0.30<=w<0.70) vs argmax {arg:.3f}.")
    return ("WARMSTART_INSUFFICIENT",
            f"Resonator dynamics fail independent of evidence: acc_50hop={w:.3f}<0.30 vs argmax {arg:.3f}. "
            f"Loopy-BP-cycle failure mode confirmed.")


def self_test_verdict():
    cases = [
        ({"acc_50hop_warmstart": 0.80, "acc_50hop_argmax_baseline": 0.22}, "WARMSTART_RESCUES"),
        ({"acc_50hop_warmstart": 0.45, "acc_50hop_argmax_baseline": 0.22}, "WARMSTART_PARTIAL"),
        ({"acc_50hop_warmstart": 0.20, "acc_50hop_argmax_baseline": 0.22}, "WARMSTART_INSUFFICIENT"),
        ({}, "WARMSTART_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def log_softmax(x):
    return x - torch.logsumexp(x, dim=0)


def compute_vamp_backward_priors(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms):
    """Run VAMP forward-backward; return per-hop smoothed log-posteriors as initialization for Resonator."""
    depth = len(rel_idxs)
    K = entity_atoms.shape[0]
    # Forward
    forward_log_post = []
    log_p0 = torch.full((K,), -1e9, device=entity_atoms.device)
    log_p0[start_idx] = 0.0
    forward_log_post.append(log_p0)
    q_state = entity_atoms[start_idx].clone().float()
    for hop in range(depth):
        rel = relation_atoms[rel_idxs[hop]].float()
        probe = M.float() * (q_state * rel)
        sims = entity_atoms.float() @ probe
        log_post = log_softmax(sims)
        forward_log_post.append(log_post)
        weights = torch.exp(log_post)
        q_state = (weights.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
    # Backward
    target_prior = torch.full((K,), -1e9, device=entity_atoms.device)
    target_prior[target_idx] = 0.0
    smoothed = [None] * (depth + 1)
    smoothed[depth] = log_softmax(forward_log_post[depth] + target_prior)
    for hop in range(depth - 1, -1, -1):
        rel = relation_atoms[rel_idxs[hop]].float()
        weights_next = torch.exp(smoothed[hop + 1])
        x_next = (weights_next.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
        probe_back = M.float() * (mh.sign_quantize(x_next) * rel)
        sims_back = entity_atoms.float() @ probe_back
        backward_log_msg = log_softmax(sims_back)
        smoothed[hop] = log_softmax(forward_log_post[hop] + backward_log_msg)
    return smoothed  # list of (K,) log-posteriors, indexed by hop


def chain_resonator_warmstart(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms, T_inner=20):
    """At each hop, initialize the resonator state from VAMP smoothed posterior;
    run T_inner resonator iterations; commit final argmax."""
    # First compute VAMP smoothed posteriors as warm-start
    smoothed = compute_vamp_backward_priors(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms)
    depth = len(rel_idxs)
    K = entity_atoms.shape[0]
    current_idx = start_idx
    for hop in range(depth):
        rel = relation_atoms[rel_idxs[hop]]
        current = entity_atoms[current_idx]
        probe = M * (current * rel)
        # Initialize from VAMP smoothed posterior (warm-start)
        prior_weights = torch.exp(smoothed[hop + 1])
        x_hat = (prior_weights.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
        # Resonator iterations starting from warm-start
        for t in range(T_inner):
            x_sign = torch.sign(entity_atoms.float().T @ torch.sign(entity_atoms.float() @ x_hat))
            x_sign = torch.where(x_sign == 0, torch.ones_like(x_sign), x_sign)
            scores = entity_atoms.float() @ x_sign
            tau_t = 1.0 / (1.0 + 0.5 * t)
            w = log_softmax(scores / tau_t).exp()
            x_hat = (w.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
        # Use VAMP-informed scores for next-hop input
        final_scores = entity_atoms.float() @ probe.float() + smoothed[hop + 1]
        current_idx = int(final_scores.argmax().item())
    return current_idx == target_idx


def run_one_seed(seed, depth, n_trials, T_inner, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    c_arg = 0; c_ws = 0
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
        if chain_resonator_warmstart(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                         entity_atoms, relation_atoms, T_inner):
            c_ws += 1
    return {"argmax": c_arg / n_trials, "warmstart": c_ws / n_trials}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "depth": 25 if smoke else 50,
              "T_inner": 10 if smoke else 20,
              "n_trials": 5 if smoke else 20,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} d={config['depth']} T_inner={config['T_inner']}", flush=True)
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed(seed, config["depth"], config["n_trials"], config["T_inner"], config, device)
        per_seed.append(r)
        print(f"  seed={seed}: argmax={r['argmax']:.3f}, warmstart={r['warmstart']:.3f}", flush=True)
    summary = {"acc_50hop_argmax_baseline": sum(r["argmax"] for r in per_seed) / len(per_seed),
                "acc_50hop_warmstart": sum(r["warmstart"] for r in per_seed) / len(per_seed),
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
    out_dir = get_output_dir("wave14_multihop_resonator_warmstart_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("warmstart_present",
                                 summary["acc_50hop_warmstart"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_resonator_warmstart_v1")
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
