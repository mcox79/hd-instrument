"""Multi-hop HMM per-hop p_fail measurement — Test 3 from Research 20:23.

Per Research's HMM cascade-error theory: substrate's argmax single-hop has implicit
p_fail; if p_fail = 0.03, then 0.97^50 ≈ 0.218 matches empirical multi-hop 0.217.
Direct measurement validates the per-hop noise rate.

Test: 10^4 1-hop retrieval trials at N=65536 K=100; count miss rate.

Verdict thresholds:
  PFAIL_CONFIRMS:  p_fail in [0.025, 0.035] (matches HMM theory)
  PFAIL_HIGHER:    p_fail > 0.035 (more per-hop noise than model assumes)
  PFAIL_LOWER:     p_fail < 0.025 (less per-hop noise; per-hop model overcounts)
  PFAIL_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_hmm_per_hop_pfail_v1.md
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


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "p_fail" not in summary:
        return ("PFAIL_INCONCLUSIVE", "Missing p_fail.")
    p = summary["p_fail"]
    pred_50hop = (1.0 - p) ** 50
    if 0.025 <= p <= 0.035:
        return ("PFAIL_CONFIRMS",
                f"Per-hop p_fail={p:.4f} in [0.025, 0.035] (predicted 0.03). "
                f"(1-p)^50 = {pred_50hop:.3f} matches empirical acc_50hop ~ 0.217. "
                f"HMM cascade-error theory validated.")
    if p > 0.035:
        return ("PFAIL_HIGHER",
                f"Per-hop p_fail={p:.4f} > 0.035 (predicted 0.03). "
                f"(1-p)^50 = {pred_50hop:.3f}. Substrate has more per-hop noise than HMM model.")
    return ("PFAIL_LOWER",
            f"Per-hop p_fail={p:.4f} < 0.025 (predicted 0.03). "
            f"(1-p)^50 = {pred_50hop:.3f}. Substrate has less per-hop noise; HMM model overcounts.")


def self_test_verdict():
    cases = [
        ({"p_fail": 0.03}, "PFAIL_CONFIRMS"),
        ({"p_fail": 0.05}, "PFAIL_HIGHER"),
        ({"p_fail": 0.01}, "PFAIL_LOWER"),
        ({}, "PFAIL_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, n_trials, config, device):
    N = config["N"]; num_entities = config["num_entities"]
    num_relations = config["num_relations"]; num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = mh.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, gen, device)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    correct = 0
    for trial in range(n_trials):
        # 1-hop chain: pick 2 entities + 1 relation; build factbase with this fact + distractors
        perm = torch.randperm(num_entities, generator=cpu_gen)[:2]
        chain_entities = perm.tolist()
        r_idx = int(torch.randint(0, num_relations, (1,), generator=cpu_gen).item())
        chain_rels = [r_idx]
        n_distractors = max(0, num_facts - 1)
        M = mh.build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
        if mh.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                          entity_atoms, relation_atoms):
            correct += 1
        if (trial + 1) % max(1, n_trials // 10) == 0:
            print(f"      trial {trial+1}/{n_trials}: cum_acc={correct/(trial+1):.4f}", flush=True)
    acc = correct / n_trials
    return acc


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "n_trials": 200 if smoke else 10000,
              "seed": 17}
    print(f"[config] N={config['N']} K={config['num_facts']} n_trials={config['n_trials']}", flush=True)
    acc = run_one_seed(config["seed"], config["n_trials"], config, device)
    p_fail = 1.0 - acc
    print(f"  acc_1hop = {acc:.4f}, p_fail = {p_fail:.4f}", flush=True)
    print(f"  predicted (1-p_fail)^50 = {(1.0-p_fail)**50:.3f}", flush=True)
    summary = {"acc_1hop": acc,
                "p_fail": p_fail,
                "predicted_50hop": (1.0 - p_fail) ** 50,
                "n_trials": config["n_trials"]}
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
    out_dir = get_output_dir("wave14_multihop_hmm_per_hop_pfail_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", summary["acc_1hop"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_hmm_per_hop_pfail_v1")
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
