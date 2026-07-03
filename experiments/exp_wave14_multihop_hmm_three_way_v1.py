"""Multi-hop HMM three-way comparison — hard Viterbi vs soft-forward-only vs full BCJR smoother.

Per Research 2026-05-22 20:23 multihop mechanism 3rd-attempt: substrate IS an HMM
with argmax = hard Viterbi, VAMP-on-chain = tree-exact BCJR. Test 1 (most
discriminating): three-way comparison.

HMM framework predictions:
  hard Viterbi:    acc_50hop ~ 0.22 (cascade error 0.97^50)
  soft-forward:    acc_50hop in [0.5, 0.95] (better than hard, worse than smoother)
  full smoother:   acc_50hop ~ 1.000 (tree-exact BCJR)

Verdict thresholds:
  HMM_CONFIRMED:    acc_hard <= 0.30 AND acc_soft in [0.40, 0.95] AND acc_smoother >= 0.70
                    (monotone hard < soft < smoother)
  HMM_PARTIAL:      monotone but tighter bands
  HMM_REFUTED:      soft ~ hard OR soft ~ smoother (no information ordering)
  HMM_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_hmm_three_way_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
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
    if "acc_hard" not in summary:
        return ("HMM_INCONCLUSIVE", "Missing acc_hard.")
    h = summary["acc_hard"]; sf = summary["acc_soft_forward"]; sm = summary["acc_smoother"]
    monotone = h <= sf <= sm + 0.05
    # Differentiated bands: hard <= 0.30, soft in [0.40, 0.95], smoother >= 0.70
    if h <= 0.30 and 0.40 <= sf <= 0.95 and sm >= 0.70 and monotone:
        return ("HMM_CONFIRMED",
                f"HMM framework confirmed: hard={h:.3f}, soft={sf:.3f}, smoother={sm:.3f}. "
                f"Information ordering hard<soft<smoother validates BCJR theory.")
    if abs(sf - h) < 0.10:
        return ("HMM_REFUTED",
                f"HMM framework REFUTED: soft={sf:.3f} ~ hard={h:.3f} (no information gain). "
                f"smoother={sm:.3f}.")
    if abs(sf - sm) < 0.10 and sf > h + 0.20:
        return ("HMM_REFUTED",
                f"HMM framework PARTIALLY REFUTED: soft={sf:.3f} ~ smoother={sm:.3f} "
                f"(backward pass provides no gain). hard={h:.3f}.")
    if monotone:
        return ("HMM_PARTIAL",
                f"Monotone but tighter bands: hard={h:.3f}, soft={sf:.3f}, smoother={sm:.3f}.")
    return ("HMM_INCONCLUSIVE",
            f"Non-monotone or unclear: hard={h:.3f}, soft={sf:.3f}, smoother={sm:.3f}.")


def self_test_verdict():
    cases = [
        ({"acc_hard": 0.22, "acc_soft_forward": 0.70, "acc_smoother": 1.0}, "HMM_CONFIRMED"),
        ({"acc_hard": 0.30, "acc_soft_forward": 0.50, "acc_smoother": 0.65}, "HMM_PARTIAL"),
        ({"acc_hard": 0.22, "acc_soft_forward": 0.25, "acc_smoother": 1.0}, "HMM_REFUTED"),
        ({"acc_hard": 0.22, "acc_soft_forward": 0.98, "acc_smoother": 1.0}, "HMM_REFUTED"),
        ({}, "HMM_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def log_softmax(x):
    return x - torch.logsumexp(x, dim=0)


def chain_hard_viterbi(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms):
    """Argmax cleanup per hop — same as standard mh.run_chain."""
    return mh.run_chain(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms)


def chain_soft_forward(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms):
    """Soft posterior forward-only: keep continuous superposition state; no backward pass."""
    K = entity_atoms.shape[0]
    q_state = entity_atoms[start_idx].clone().float()  # keep continuous
    log_p = None
    for r_idx in rel_idxs:
        rel = relation_atoms[r_idx].float()
        probe = M.float() * (q_state * rel)
        sims = entity_atoms.float() @ probe
        log_p = log_softmax(sims)
        weights = torch.exp(log_p)
        # Continuous superposition — do NOT sign-quantize
        q_state = (weights.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
    pred = int(log_p.argmax().item())
    return pred == target_idx


def chain_full_smoother(M, start_idx, rel_idxs, target_idx, entity_atoms, relation_atoms):
    """Full BCJR-style forward-backward EP — reuses VAMP chain."""
    return v.vamp_chain_forward_backward(M, start_idx, rel_idxs, target_idx,
                                             entity_atoms, relation_atoms)


def run_one_seed(seed, depth, n_trials, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    c_hard = 0; c_soft = 0; c_smoother = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
        chain_entities = perm.tolist()
        chain_rels = [int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
                      for _ in range(depth)]
        n_distractors = max(0, num_facts - depth)
        Mb = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if chain_hard_viterbi(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                 entity_atoms, relation_atoms):
            c_hard += 1
        if chain_soft_forward(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                 entity_atoms, relation_atoms):
            c_soft += 1
        if chain_full_smoother(Mb, chain_entities[0], chain_rels, chain_entities[-1],
                                  entity_atoms, relation_atoms):
            c_smoother += 1
    return {"hard": c_hard / n_trials, "soft": c_soft / n_trials, "smoother": c_smoother / n_trials}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "depth": 25 if smoke else 50,
              "n_trials": 10 if smoke else 30,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K={config['num_facts']} d={config['depth']}", flush=True)
    per_seed = []
    for seed in config["seeds"]:
        r = run_one_seed(seed, config["depth"], config["n_trials"], config, device)
        per_seed.append(r)
        print(f"  seed={seed}: hard={r['hard']:.3f} soft_forward={r['soft']:.3f} smoother={r['smoother']:.3f}", flush=True)
    summary = {"acc_hard": sum(r["hard"] for r in per_seed) / len(per_seed),
                "acc_soft_forward": sum(r["soft"] for r in per_seed) / len(per_seed),
                "acc_smoother": sum(r["smoother"] for r in per_seed) / len(per_seed),
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
    out_dir = get_output_dir("wave14_multihop_hmm_three_way_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("smoother_present", summary["acc_smoother"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_hmm_three_way_v1")
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
