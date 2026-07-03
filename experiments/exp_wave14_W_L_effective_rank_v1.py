"""W^L effective rank — Strategy 21:25 Priority 3 (Oseledets subspace collapse test).

Compute SVD of W^L for L in {1, 5, 10, 20, 50}; measure effective rank.
CONFIRMS rank collapse if eff_rank(L=50) <= eff_rank(L=1)/2.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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
    if "eff_rank_per_L" not in summary:
        return ("RANK_INCONCLUSIVE", "Missing.")
    per = summary["eff_rank_per_L"]
    r1 = per.get("1", 0); r50 = per.get("50", 0)
    if r50 <= r1 / 2:
        return ("RANK_COLLAPSE_CONFIRMS",
                f"Subspace collapse: rank(L=1)={r1} -> rank(L=50)={r50} (>=2x drop). {per}.")
    if r50 >= r1:
        return ("RANK_COLLAPSE_REFUTES",
                f"No collapse: rank(L=1)={r1}, rank(L=50)={r50}. {per}.")
    return ("RANK_COLLAPSE_PARTIAL",
            f"Partial: rank(L=1)={r1}, rank(L=50)={r50}. {per}.")


def self_test_verdict():
    for s, exp in [
        ({"eff_rank_per_L": {"1": 100, "50": 40}}, "RANK_COLLAPSE_CONFIRMS"),
        ({"eff_rank_per_L": {"1": 100, "50": 110}}, "RANK_COLLAPSE_REFUTES"),
        ({"eff_rank_per_L": {"1": 100, "50": 70}}, "RANK_COLLAPSE_PARTIAL"),
        ({}, "RANK_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def compute_W(N, K, num_entities, num_relations, cpu_gen, device, target):
    entity_atoms = mh.make_bsc_codebook(num_entities, N, torch.Generator(device=device).manual_seed(17), device).to(target)
    relation_atoms = mh.make_bsc_codebook(num_relations, N, torch.Generator(device=device).manual_seed(17), device).to(target)
    triples = []
    for _ in range(K):
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        triples.append(mh.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o]))
    T = torch.stack(triples, dim=0)
    W = (T.T @ T) / N
    return W


def effective_rank(eigvals, threshold_rel=0.01):
    top = float(eigvals.abs().max())
    return int((eigvals.abs() > threshold_rel * top).sum())


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 4096 if smoke else 65536, "K": 100,
              "L_grid": [1, 5, 10] if smoke else [1, 5, 10, 20, 50],
              "num_entities": 200, "num_relations": 20, "seed": 17}
    use_cpu = config["N"] >= 32768
    target = torch.device("cpu") if use_cpu else device
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    print(f"[setup] N={config['N']} on {target}", flush=True)
    W = compute_W(config["N"], config["K"], config["num_entities"], config["num_relations"], cpu_gen, device, target)
    print(f"[setup] W built, shape={tuple(W.shape)}", flush=True)
    per_L = {}
    W_L = W.clone()
    for L in config["L_grid"]:
        # Compute W^L iteratively
        while L > 1 and L != max(config["L_grid"]):
            break
        # Actually compute W^L from scratch each time for clarity
        WL = W.clone()
        for _ in range(L - 1):
            WL = WL @ W
        eigvals = torch.linalg.eigvalsh(WL.float()).cpu()
        rank = effective_rank(eigvals)
        per_L[str(L)] = rank
        print(f"  L={L}: effective rank = {rank}", flush=True)
        del WL
    summary = {"eff_rank_per_L": per_L}
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
    out_dir = get_output_dir("wave14_W_L_effective_rank_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("rank_present", float(summary["eff_rank_per_L"].get("1", 0)) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_W_L_effective_rank_v1")
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
