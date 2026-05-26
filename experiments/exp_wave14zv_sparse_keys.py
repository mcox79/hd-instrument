"""Sparse ternary keys substrate - {-1, 0, +1}^N with sparsity p.

All prior tests used dense bipolar keys. zv tests sparse ternary keys
(Hopfield-style sparse coding, Treves-Rolls limit). Sweep sparsity p in
{0.1, 0.3, 0.5, 1.0=dense} and measure argmax + edit-then-query accuracy.

Pre-reg: preregs/2026-05-21_wave14zv_sparse_keys.md
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)

PASS = 0.95
EQUIV_TOL = 0.03


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def make_sparse_keys(M, N, p, gen, device):
    """Sparse ternary keys: each entry in {-1, 0, +1} with sparsity p (prob nonzero).
    p=1.0 -> dense bipolar."""
    if p >= 1.0:
        return 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    mask = (torch.rand((M, N), generator=gen, device=device) < p).float()
    signs = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    return mask * signs


def compute_verdict(summary):
    per_p = summary.get("per_p", {})
    if not per_p:
        return ("SPARSE_INCONCLUSIVE", "Missing.")
    dense = per_p.get(1.0)
    if dense is None:
        return ("SPARSE_INCONCLUSIVE", "Missing dense baseline.")
    dense_score = min(dense["edit_acc"], dense["kept_acc"])
    # Find best non-dense sparsity
    sparse_ps = [p for p in per_p if p < 1.0]
    scores = {p: min(per_p[p]["edit_acc"], per_p[p]["kept_acc"]) for p in sparse_ps}
    # Any sparse p fails outright?
    failing = [p for p in sparse_ps if scores[p] < 0.5]
    if failing:
        return (f"SPARSE_FAILS_AT_{min(failing)}",
                f"At sparsity p={min(failing)}, score={scores[min(failing)]:.3f}<0.5. "
                f"Dense baseline={dense_score:.3f}. Substrate broken at this sparsity.")
    best_p = max(sparse_ps, key=lambda p: scores[p])
    best_s = scores[best_p]
    if abs(best_s - dense_score) < EQUIV_TOL:
        return ("SPARSE_EQUIVALENT_TO_DENSE",
                f"Best sparse p={best_p} score={best_s:.3f}, dense={dense_score:.3f}. "
                f"Within tolerance. Substrate sparsity-invariant in tested range.")
    if best_s > dense_score:
        return (f"SPARSE_BETTER_THAN_DENSE_AT_{best_p}",
                f"Sparse p={best_p} beats dense: {best_s:.3f}>{dense_score:.3f}. "
                f"Per-p: " + ", ".join(f"p={p}:{scores[p]:.3f}" for p in sorted(scores)))
    return ("SPARSE_WORSE_THAN_DENSE",
            f"All sparse p worse than dense ({dense_score:.3f}). Best={best_s:.3f} at p={best_p}.")


def self_test_verdict():
    def mk(scores):
        return {p: {"edit_acc": e, "kept_acc": k} for p, (e, k) in scores.items()}
    cases = [
        ({"per_p": mk({0.1: (0.99, 0.99), 0.3: (0.99, 0.99),
                        0.5: (0.99, 0.99), 1.0: (0.99, 0.99)})},
         "SPARSE_EQUIVALENT_TO_DENSE"),
        ({"per_p": mk({0.1: (0.99, 1.0), 0.3: (0.99, 0.99),
                        0.5: (0.95, 0.95), 1.0: (0.95, 0.90)})},
         "SPARSE_BETTER_THAN_DENSE_AT_0.1"),
        ({"per_p": mk({0.1: (0.80, 0.80), 0.3: (0.85, 0.85),
                        0.5: (0.90, 0.90), 1.0: (0.99, 0.99)})},
         "SPARSE_WORSE_THAN_DENSE"),
        ({"per_p": mk({0.1: (0.20, 0.20), 0.3: (0.99, 0.99),
                        0.5: (0.99, 0.99), 1.0: (0.99, 0.99)})},
         "SPARSE_FAILS_AT_0.1"),
        ({}, "SPARSE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def run_at_sparsity(p, config, device):
    N = config["N"]
    M = config["M_stored"]
    n_edit = config["n_edit"]
    n_kept = config["n_kept"]
    seeds = config["seeds"]
    alpha = config["alpha"]
    per_seed_e, per_seed_k = [], []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        keys = make_sparse_keys(M, N, p, gen, device)
        v_orig = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        v_new = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N
        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        edit_idx = sorted(torch.randperm(M, generator=edit_gen)[:n_edit].tolist())
        edit_set = set(edit_idx)
        cands = [i for i in range(M) if i not in edit_set]
        kept_idx = sorted(torch.tensor(cands)[torch.randperm(
            len(cands), generator=kept_gen)[:min(n_kept, len(cands))]].tolist())
        W_edit = W.clone()
        for i in edit_idx:
            W_edit = yb.edit_fact(W_edit, keys[i], v_new[i], alpha, N)
        v_after = v_orig.clone()
        for i in edit_idx:
            v_after[i] = v_new[i]
        et = torch.tensor(edit_idx, device=device)
        kt = torch.tensor(kept_idx, device=device)
        e_acc = float(((keys[edit_idx] @ W_edit.T) @ v_after.T).argmax(dim=1).eq(et).float().mean())
        k_acc = float(((keys[kept_idx] @ W_edit.T) @ v_after.T).argmax(dim=1).eq(kt).float().mean())
        per_seed_e.append(e_acc)
        per_seed_k.append(k_acc)
    return {"edit_acc": sum(per_seed_e) / len(per_seed_e),
             "kept_acc": sum(per_seed_k) / len(per_seed_k)}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "n_edit": 5 if smoke else 30,
              "n_kept": 20 if smoke else 100,
              "sparsities": [0.5, 1.0] if smoke else [0.05, 0.1, 0.3, 0.5, 1.0],
              "seeds": [17] if smoke else [17, 23, 31],
              "alpha": 1.0}
    per_p = {}
    for p in config["sparsities"]:
        per_p[p] = run_at_sparsity(p, config, device)
        print(f"  p={p}: edit={per_p[p]['edit_acc']:.3f}, kept={per_p[p]['kept_acc']:.3f}",
              flush=True)
    summary = {"per_p": per_p}
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
    out_dir = get_output_dir("wave14zv_sparse_keys_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    dense_e = summary["per_p"][1.0]["edit_acc"]
    oracle.assert_baseline_high("dense_edit", dense_e, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zv_sparse_keys")
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
