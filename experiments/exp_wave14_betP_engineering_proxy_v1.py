"""Bet P-Engineering proxy — semantic-structured codebook via Hadamard mixing.

Strategy filed cycle 45 + 20:35 EDT. Tests whether codebook-geometry rescue
extends multi-hop d=25 cliff. Proxy: use Hadamard rows projected with class
labels (semantic similarity preserved) instead of pretrained KGE embeddings.

Pre-reg: preregs/2026-05-21_wave14_betP_engineering_proxy_v1.md
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
_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)

PASS_ACC_50 = 0.50
PARTIAL_FLOOR = 0.22


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    pdm = summary.get("per_depth_mean_acc")
    if not pdm:
        return ("BET_P_PROXY_INCONCLUSIVE", "Missing.")
    pdm = {int(k): float(v) for k, v in pdm.items()}
    acc_50 = pdm.get(50, 0.0)
    if acc_50 >= PASS_ACC_50:
        return ("BET_P_PROXY_PASS",
                f"Semantic codebook achieves acc_50={acc_50:.3f}>=0.50; codebook-geometry "
                f"rescue validated. Multi-hop extends past argmax baseline 0.22 floor.")
    if acc_50 <= PARTIAL_FLOOR:
        return ("BET_P_PROXY_KILLED",
                f"Semantic codebook acc_50={acc_50:.3f}<={PARTIAL_FLOOR}. Codebook geometry "
                f"axis closes on this proxy.")
    return ("BET_P_PROXY_PARTIAL",
            f"acc_50={acc_50:.3f} in ({PARTIAL_FLOOR},{PASS_ACC_50}); marginal codebook gain.")


def self_test_verdict():
    cases = [
        ({"per_depth_mean_acc": {1: 0.95, 50: 0.65}}, "BET_P_PROXY_PASS"),
        ({"per_depth_mean_acc": {1: 0.95, 50: 0.35}}, "BET_P_PROXY_PARTIAL"),
        ({"per_depth_mean_acc": {1: 0.95, 50: 0.15}}, "BET_P_PROXY_KILLED"),
        ({}, "BET_P_PROXY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_semantic_codebook(num_entities, N, n_classes, device):
    """Proxy KGE: each entity belongs to one of n_classes; codeword = class_signature + noise.
    This creates semantic structure where same-class entities are closer than different-class."""
    n_log2 = int(round(math.log2(N)))
    H = v1.sylvester_hadamard(n_log2, device)  # (N, N)
    # Class signatures: pick n_classes random Hadamard rows
    cpu_gen = torch.Generator().manual_seed(7)
    class_idx = torch.randperm(N, generator=cpu_gen)[:n_classes]
    class_atoms = H[class_idx]  # (n_classes, N)
    # Entity codewords: class_atom + random perturbation, then sign-quantize
    ent_class = torch.randint(0, n_classes, (num_entities,), generator=cpu_gen).to(device)
    dev_gen = torch.Generator(device=device).manual_seed(13)
    noise = 2.0 * (torch.rand((num_entities, N), generator=dev_gen, device=device) > 0.5).float() - 1.0
    noisy = class_atoms[ent_class] * 0.6 + noise * 0.4
    return torch.sign(noisy).clamp(-1, 1) + (torch.sign(noisy) == 0).float()


def run_one_seed(seed, hop_depths, n_trials, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = make_semantic_codebook(num_entities, N, config["n_classes"], device)
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
            if t.run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                              entity_atoms, relation_atoms):
                successes += 1
        by_depth[depth] = successes / n_trials
    return by_depth


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 4096,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "num_facts": 20 if smoke else 100,
              "n_classes": 10 if smoke else 25,
              "hop_depths": [1, 5] if smoke else [1, 5, 10, 25, 50],
              "n_trials": 5 if smoke else 30,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = {}
    for seed in config["seeds"]:
        by_d = run_one_seed(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed[str(seed)] = {str(k): v for k, v in by_d.items()}
        print(f"  seed={seed}: " + " ".join(f"d{d}={by_d[d]:.3f}" for d in config["hop_depths"]), flush=True)
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
    out_dir = get_output_dir("wave14_betP_engineering_proxy_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    acc_1 = summary["per_depth_mean_acc"][1]
    oracle.assert_baseline_high("semantic_1hop", acc_1, 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betP_engineering_proxy_v1")
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
