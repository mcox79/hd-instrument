"""Bet T Hypothesis Tracking — substrate tracks K competing hypotheses in parallel.

Per cap_map v78 Bet T: store K hypothesis bundles, each containing different
sets of facts. Query disambiguation: a fact-query should retrieve from the
correct hypothesis without cross-talk above noise floor.

Substrate analog: K hypothesis-tag atoms; each fact stored as
  (subj * rel * obj) tagged with hypothesis atom h_k
Bundle: M_k = sign(sum_i s_i * r_i * o_i)  per hypothesis
Joint: M_joint = sign(sum_k h_k * M_k)

Pre-reg: preregs/2026-05-22_wave14_betT_hypothesis_tracking_v1.md
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

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)

PASS_PER_HYP = 0.80
KILL_PER_HYP = 0.40


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "per_hypothesis_acc" not in summary:
        return ("BET_T_INCONCLUSIVE", "Missing per_hypothesis_acc.")
    accs = list(summary["per_hypothesis_acc"].values())
    if not accs:
        return ("BET_T_INCONCLUSIVE", "Empty accs.")
    min_acc = min(accs)
    mean_acc = sum(accs) / len(accs)
    if min_acc >= PASS_PER_HYP:
        return ("BET_T_PASS",
                f"All K hypotheses recovered above {PASS_PER_HYP}: min={min_acc:.3f}, "
                f"mean={mean_acc:.3f}. Substrate maintains parallel hypothesis tracking.")
    if min_acc < KILL_PER_HYP:
        return ("BET_T_KILLED",
                f"Some hypothesis falls below {KILL_PER_HYP}: min={min_acc:.3f}, mean={mean_acc:.3f}. "
                f"Cross-talk between hypotheses dominates.")
    return ("BET_T_PARTIAL",
            f"min_acc={min_acc:.3f} in [{KILL_PER_HYP},{PASS_PER_HYP}); mean={mean_acc:.3f}.")


def self_test_verdict():
    cases = [
        ({"per_hypothesis_acc": {"0": 0.92, "1": 0.88, "2": 0.85}}, "BET_T_PASS"),
        ({"per_hypothesis_acc": {"0": 0.92, "1": 0.60, "2": 0.85}}, "BET_T_PARTIAL"),
        ({"per_hypothesis_acc": {"0": 0.92, "1": 0.30, "2": 0.85}}, "BET_T_KILLED"),
        ({}, "BET_T_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    N = config["N"]
    K_hyp = config["n_hypotheses"]
    n_facts_per_hyp = config["n_facts_per_hyp"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)
    hyp_atoms = t.make_bsc_codebook(K_hyp, N, gen, device)

    # Build per-hypothesis fact lists
    hyp_facts = []
    for k in range(K_hyp):
        facts = []
        for _ in range(n_facts_per_hyp):
            s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
            o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            facts.append((s, r, o))
        hyp_facts.append(facts)

    # Joint bundle: M = sign(sum_k h_k * sign(sum_i s*r*o))
    triples_per_hyp = []
    for k, facts in enumerate(hyp_facts):
        triples = []
        for s, r, o in facts:
            triples.append(t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o]))
        bundle_k = t.sign_quantize(torch.stack(triples, dim=0).sum(dim=0))
        triples_per_hyp.append(hyp_atoms[k] * bundle_k)
    M_joint = t.sign_quantize(torch.stack(triples_per_hyp, dim=0).sum(dim=0))

    # For each hypothesis k, decode obj given (s, r): probe = M_joint * h_k * s * r
    per_hyp_acc = {}
    for k, facts in enumerate(hyp_facts):
        correct = 0
        for s, r, o in facts:
            probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            pred = int((entity_atoms @ probe).argmax().item())
            if pred == o:
                correct += 1
        per_hyp_acc[str(k)] = correct / n_facts_per_hyp
    return per_hyp_acc


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "n_hypotheses": 3 if smoke else 5,
              "n_facts_per_hyp": 10 if smoke else 30,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = {}
    for s in config["seeds"]:
        accs = run_one_seed(s, config, device)
        per_seed[str(s)] = accs
        print(f"  seed={s}: " + " ".join(f"h{k}={accs[k]:.3f}" for k in accs), flush=True)
    # Mean across seeds, per hypothesis
    K = config["n_hypotheses"]
    per_hyp_mean = {str(k): sum(per_seed[str(s)][str(k)] for s in config["seeds"]) / len(config["seeds"])
                       for k in range(K)}
    summary = {"per_hypothesis_acc": per_hyp_mean, "per_seed": per_seed}
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
    out_dir = get_output_dir("wave14_betT_hypothesis_tracking_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["per_hypothesis_acc"].values())[0]
    oracle.assert_baseline_high("hyp0_acc", first, 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betT_hypothesis_tracking_v1")
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
