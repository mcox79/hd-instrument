"""W endpoint injection diagnostic — Strategy 21:32 P6.

For K=100 codewords at N=65536, run L-hop forward chain; record endpoints.
Verify endpoints are distinct (injective) vs collapsed (cluster trapping at endpoint level).
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from collections import Counter
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

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
    if "n_distinct_endpoints" not in summary:
        return ("ENDPOINT_INCONCLUSIVE", "Missing.")
    n = summary["n_distinct_endpoints"]; K = summary["K"]
    if n == K:
        return ("ENDPOINT_INJECTIVE",
                f"Endpoints distinct: {n}/{K}. Substrate forward map injective.")
    if n < K / 2:
        return ("ENDPOINT_COLLAPSED",
                f"Endpoints collapse: {n}/{K} distinct. Cluster trapping at endpoint level.")
    return ("ENDPOINT_PARTIAL",
            f"Partial collapse: {n}/{K} distinct.")


def self_test_verdict():
    for s, exp in [
        ({"n_distinct_endpoints": 100, "K": 100}, "ENDPOINT_INJECTIVE"),
        ({"n_distinct_endpoints": 30, "K": 100}, "ENDPOINT_COLLAPSED"),
        ({"n_distinct_endpoints": 80, "K": 100}, "ENDPOINT_PARTIAL"),
        ({}, "ENDPOINT_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536, "K": 100, "L": 10 if smoke else 25,
              "num_entities": 200, "num_relations": 20, "seed": 17}
    gen = torch.Generator(device=device).manual_seed(config["seed"])
    entity_atoms = mh.make_bsc_codebook(config["num_entities"], config["N"], gen, device)
    relation_atoms = mh.make_bsc_codebook(config["num_relations"], config["N"], gen, device)
    cpu_gen = torch.Generator().manual_seed(config["seed"] + 1009)
    # Construct factbase
    chain_ents = list(range(config["L"] + 1))[:config["L"] + 1]
    chain_rels = [int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                  for _ in range(config["L"])]
    n_distractors = max(0, config["K"] - config["L"])
    M = mh.build_factbase(chain_ents, chain_rels, n_distractors,
                            config["num_entities"], config["num_relations"],
                            entity_atoms, relation_atoms, cpu_gen, device)
    print(f"[setup] N={config['N']} K={config['K']} L={config['L']}", flush=True)
    # Run L-hop chain from each of K=num_entities (capped)
    n_starts = min(config["K"], config["num_entities"])
    endpoints = []
    for start_idx in range(n_starts):
        current = start_idx
        for r_idx in chain_rels:
            current_atom = entity_atoms[current]
            rel = relation_atoms[r_idx]
            probe = M * (current_atom * rel)
            current = int((entity_atoms @ probe).argmax().item())
        endpoints.append(current)
    counter = Counter(endpoints)
    n_distinct = len(counter)
    print(f"  {n_distinct}/{n_starts} distinct endpoints", flush=True)
    print(f"  top10 endpoints: {counter.most_common(10)}", flush=True)
    summary = {"n_distinct_endpoints": n_distinct, "K": n_starts,
                "top10_endpoints": dict(counter.most_common(10))}
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
    out_dir = get_output_dir("wave14_W_endpoint_injection_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("distinct_present", float(summary["n_distinct_endpoints"]) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_W_endpoint_injection_v1")
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
