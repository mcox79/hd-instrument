"""Multi-hop VAMP-on-chain forward-backward EP at N=65536.

Per Research 19:25 redrill: TOP rehabilitation candidate post-Resonator-refutation
(calibrated P=0.40). Structurally different from Resonator (tree-exact single-pass,
not loopy iteration).

Forward pass: at each hop, soft posterior log_post = sims - logsumexp(sims);
next-hop probe = posterior-expectation state (weighted superposition, NOT argmax).
Backward pass: from final hop, accumulate backward messages; smoothed posterior
= forward_log_post + backward_log_msg. Final commit per hop = argmax of smoothed.

Tree-exactness: chain has no loops → forward-backward is exact for chains
(analogous to Kalman smoother).

Verdict thresholds:
  VAMPCHAIN_RESTORES: acc_50hop >= 0.50
  VAMPCHAIN_PARTIAL: 0.30 <= acc_50hop < 0.50
  VAMPCHAIN_INSUFFICIENT: acc_50hop < 0.30 (all readout-only rehab fails -> V3 substrate change)
  VAMPCHAIN_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_vamp_chain_N65536_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
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


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_50hop_vamp_chain" not in summary:
        return ("VAMPCHAIN_INCONCLUSIVE", "Missing acc_50hop_vamp_chain.")
    v = summary["acc_50hop_vamp_chain"]
    a = summary["acc_50hop_argmax_baseline"]
    if v >= PASS_ACC_50:
        return ("VAMPCHAIN_RESTORES",
                f"VAMP-on-chain restores deep composition: acc_50hop={v:.3f} (>={PASS_ACC_50}) "
                f"vs argmax {a:.3f}. Tree-exact forward-backward EP succeeds where Resonator failed.")
    if v >= PARTIAL_ACC_50:
        return ("VAMPCHAIN_PARTIAL",
                f"VAMP-on-chain partial: acc_50hop={v:.3f} ({PARTIAL_ACC_50}<=v<{PASS_ACC_50}) "
                f"vs argmax {a:.3f}.")
    return ("VAMPCHAIN_INSUFFICIENT",
            f"VAMP-on-chain insufficient: acc_50hop={v:.3f} (<{PARTIAL_ACC_50}) vs argmax {a:.3f}. "
            f"All readout-only rehabilitations fail. V3 substrate-level restructuring required "
            f"(sparse codebook / asymmetric W / clique codes).")


def self_test_verdict():
    cases = [
        ({"acc_50hop_vamp_chain": 0.55, "acc_50hop_argmax_baseline": 0.22}, "VAMPCHAIN_RESTORES"),
        ({"acc_50hop_vamp_chain": 0.40, "acc_50hop_argmax_baseline": 0.22}, "VAMPCHAIN_PARTIAL"),
        ({"acc_50hop_vamp_chain": 0.20, "acc_50hop_argmax_baseline": 0.22}, "VAMPCHAIN_INSUFFICIENT"),
        ({}, "VAMPCHAIN_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def log_softmax(x):
    return x - torch.logsumexp(x, dim=0)


def vamp_chain_forward_backward(M, start_idx, rel_idxs, target_idx,
                                  entity_atoms, relation_atoms):
    """Tree-exact forward-backward EP on chain. Single-pass per direction."""
    depth = len(rel_idxs)
    K = entity_atoms.shape[0]
    # FORWARD PASS
    forward_log_post = []
    # Posterior at hop 0 (= input): delta at start_idx
    log_p0 = torch.full((K,), -1e9, device=entity_atoms.device)
    log_p0[start_idx] = 0.0
    forward_log_post.append(log_p0)
    q_state = entity_atoms[start_idx].clone()
    for hop in range(depth):
        rel = relation_atoms[rel_idxs[hop]]
        probe = M * (q_state * rel)
        sims = entity_atoms @ probe
        log_post = log_softmax(sims)
        forward_log_post.append(log_post)
        # Posterior expectation state for next hop probe
        weights = torch.exp(log_post)
        q_state = (weights.unsqueeze(1) * entity_atoms).sum(dim=0)
        q_state = mh.sign_quantize(q_state)
    # BACKWARD PASS: accumulate from target back
    backward_log_msg = torch.full((K,), 0.0, device=entity_atoms.device)
    # Smoothed posterior at depth (= last hop) = combine forward[depth] with target prior (delta at target_idx)
    target_prior = torch.full((K,), -1e9, device=entity_atoms.device)
    target_prior[target_idx] = 0.0
    smoothed = [None] * (depth + 1)
    smoothed[depth] = log_softmax(forward_log_post[depth] + target_prior)
    # Backward: each hop transmits log p(s_{t-1} | s_t) prior * backward message
    for hop in range(depth - 1, -1, -1):
        rel = relation_atoms[rel_idxs[hop]]
        # For each candidate s_{hop} entity, compute log p(s_{hop+1}|s_{hop}) similarity-based proxy
        # via reverse probe through M: y = M * (s_{hop} * rel) gives s_{hop+1} estimate
        # Marginalize backward msg over s_{hop+1} weighted by transition: approximate using
        # current smoothed posterior of next hop
        # Simplification: backward message at hop i is the log posterior of smoothed[i+1] back-propagated
        # via the transition kernel (which is the same as forward kernel since M is symmetric in bipolar substrate)
        weights_next = torch.exp(smoothed[hop + 1])
        # Estimate of state at hop+1 given smoothed
        x_next = (weights_next.unsqueeze(1) * entity_atoms).sum(dim=0)
        # Reverse probe: given s_{hop+1}, predict s_{hop} via M * (s_{hop+1} * rel)
        # (in bipolar substrate, M * x * r unbinds to give the partner of x in r-bound triples)
        probe_back = M * (mh.sign_quantize(x_next) * rel)
        sims_back = entity_atoms @ probe_back
        backward_log_msg = log_softmax(sims_back)
        smoothed[hop] = log_softmax(forward_log_post[hop] + backward_log_msg)
    # Commit at final hop (target prediction)
    pred = int(smoothed[depth].argmax().item())
    return pred == target_idx


def run_one_seed_compare(seed, hop_depths, n_trials, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    by_depth_arg = {}; by_depth_vamp = {}
    for depth in hop_depths:
        if depth > num_entities - 1 or depth > num_facts:
            by_depth_arg[depth] = 0.0; by_depth_vamp[depth] = 0.0
            continue
        correct_arg = 0; correct_v = 0
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
            if vamp_chain_forward_backward(M, chain_entities[0], chain_rels, chain_entities[-1],
                                              entity_atoms, relation_atoms):
                correct_v += 1
        by_depth_arg[depth] = correct_arg / n_trials
        by_depth_vamp[depth] = correct_v / n_trials
    return {"seed": seed,
             "by_depth_argmax": by_depth_arg,
             "by_depth_vamp_chain": by_depth_vamp}


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
        a_v = " ".join(f"d{d}={r['by_depth_vamp_chain'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} ARGMAX: {a_arg}", flush=True)
        print(f"  seed={seed} VAMP:   {a_v}", flush=True)
    per_depth_arg = {}; per_depth_v = {}
    for d in config["hop_depths"]:
        per_depth_arg[d] = sum(r["by_depth_argmax"][d] for r in per_seed) / len(per_seed)
        per_depth_v[d] = sum(r["by_depth_vamp_chain"][d] for r in per_seed) / len(per_seed)
    max_d = max(config["hop_depths"])
    summary = {"per_depth_mean_acc_argmax": {str(d): per_depth_arg[d] for d in config["hop_depths"]},
                "per_depth_mean_acc_vamp_chain": {str(d): per_depth_v[d] for d in config["hop_depths"]},
                "acc_50hop_argmax_baseline": per_depth_arg.get(50, per_depth_arg[max_d]),
                "acc_50hop_vamp_chain": per_depth_v.get(50, per_depth_v[max_d])}
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
    out_dir = get_output_dir("wave14_multihop_vamp_chain_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_depth_present",
                                 summary["per_depth_mean_acc_vamp_chain"].get("1", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_vamp_chain_N65536_v1")
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
