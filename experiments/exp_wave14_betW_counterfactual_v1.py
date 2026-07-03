"""Bet W Counterfactual Binding — substrate answers 'if X' substituted queries.

Per cap_map v78 Bet W: store fact (s, r, o); query 'if subject were s', what
would o be?' — substitute s' (different from any stored subject) and ask if
substrate produces a coherent answer based on relation r's structure.

Substrate analog: stored fact (s, r, o). Counterfactual probe = M * s' * r,
where s' is a NEW entity. Expected behavior: substrate returns whatever entity
is closest in r's row of W; this should be consistent (not random) across
similar s' inputs.

Pre-reg: preregs/2026-05-22_wave14_betW_counterfactual_v1.md
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


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "consistency" not in summary:
        return ("BET_W_INCONCLUSIVE", "Missing consistency.")
    cons = summary["consistency"]
    factual = summary.get("factual_acc", 0.0)
    if cons >= 0.50 and factual >= 0.80:
        return ("BET_W_PASS",
                f"Counterfactual consistency {cons:.3f}>=0.50 with factual_acc {factual:.3f}>=0.80. "
                f"Substrate produces stable counterfactual responses without losing factual fidelity.")
    if cons < 0.15:
        return ("BET_W_KILLED",
                f"Counterfactual consistency {cons:.3f}<0.15. Random-like response to perturbed s.")
    return ("BET_W_PARTIAL",
            f"cons={cons:.3f}, factual={factual:.3f}. Partial counterfactual behavior.")


def self_test_verdict():
    cases = [
        ({"consistency": 0.65, "factual_acc": 0.90}, "BET_W_PASS"),
        ({"consistency": 0.05, "factual_acc": 0.85}, "BET_W_KILLED"),
        ({"consistency": 0.30, "factual_acc": 0.85}, "BET_W_PARTIAL"),
        ({}, "BET_W_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    n_perturb = config["n_perturb"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(num_entities + 50, N, gen, device)
    relation_atoms = t.make_bsc_codebook(num_relations, N, gen, device)
    # First num_entities are "stored" entities; last 50 are "new" for counterfactual
    new_ent_start = num_entities

    facts = []
    triples = []
    for _ in range(num_facts):
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        facts.append((s, r, o))
        triples.append(t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o]))
    M = t.sign_quantize(torch.stack(triples, dim=0).sum(dim=0))

    # Factual accuracy
    factual_correct = 0
    for s, r, o in facts[:30]:
        probe = M * entity_atoms[s] * relation_atoms[r]
        if int((entity_atoms @ probe).argmax().item()) == o:
            factual_correct += 1
    factual_acc = factual_correct / min(30, len(facts))

    # Counterfactual: pick relation r, substitute new entity s'; query r-many times
    # to check consistency (do similar s' all give same/similar o' for fixed r?)
    n_test_relations = min(10, num_relations)
    consistency_scores = []
    for r_test in range(n_test_relations):
        new_subjs = list(range(new_ent_start, new_ent_start + n_perturb))
        preds = []
        for sp in new_subjs:
            probe = M * entity_atoms[sp] * relation_atoms[r_test]
            pred = int((entity_atoms @ probe).argmax().item())
            preds.append(pred)
        # Consistency = fraction agreeing with the modal prediction
        if not preds:
            continue
        mode = max(set(preds), key=preds.count)
        consistency_scores.append(preds.count(mode) / len(preds))
    avg_consistency = sum(consistency_scores) / max(len(consistency_scores), 1)
    return {"consistency": avg_consistency, "factual_acc": factual_acc}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "num_entities": 50 if smoke else 200,
              "num_relations": 5 if smoke else 20,
              "num_facts": 30 if smoke else 100,
              "n_perturb": 5 if smoke else 10,
              "seeds": [17] if smoke else [17, 23, 31]}
    seed_results = []
    for s in config["seeds"]:
        r = run_one_seed(s, config, device)
        seed_results.append(r)
        print(f"  seed={s}: consistency={r['consistency']:.3f} factual={r['factual_acc']:.3f}", flush=True)
    summary = {"consistency": sum(x["consistency"] for x in seed_results) / len(seed_results),
                "factual_acc": sum(x["factual_acc"] for x in seed_results) / len(seed_results),
                "per_seed": seed_results}
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
    out_dir = get_output_dir("wave14_betW_counterfactual_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("factual_acc", summary["factual_acc"], 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betW_counterfactual_v1")
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
