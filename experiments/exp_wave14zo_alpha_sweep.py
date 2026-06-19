"""Anti-Hebbian alpha sweep - does partial or over-erase beat alpha=1.0?

All edit-then-query tests fixed alpha=1.0. Sweep {0.5, 0.8, 1.0, 1.2, 1.5}.
Measure edit_argmax_acc, kept_acc, side_effect. Find operating point that
maximizes min(edit, kept).

Pre-reg: preregs/2026-05-21_wave14zo_alpha_sweep.md
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

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)

PASS = 0.95
FLAT_TOL = 0.02


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    per_alpha = summary.get("per_alpha")
    if not per_alpha:
        return ("ALPHA_INCONCLUSIVE", "Missing per_alpha.")
    # Score: min(edit, kept) at each alpha
    scores = {a: min(r["edit_acc"], r["kept_acc"]) for a, r in per_alpha.items()}
    best_a = max(scores.keys(), key=lambda a: scores[a])
    best_s = scores[best_a]
    s_vals = list(scores.values())
    is_flat = max(s_vals) - min(s_vals) < FLAT_TOL
    if is_flat:
        return ("ALPHA_FLAT",
                f"All alpha values produce min(edit, kept) within {FLAT_TOL}: "
                f"range [{min(s_vals):.4f}, {max(s_vals):.4f}]. Substrate insensitive "
                f"to erase strength in tested range.")
    default = per_alpha.get(1.0)
    if default and abs(scores[1.0] - best_s) < 1e-6:
        return ("ALPHA_DEFAULT_BEST",
                f"alpha=1.0 wins with min(edit, kept)={best_s:.4f}. "
                f"Per-alpha: " + ", ".join(f"a={a}:e={r['edit_acc']:.3f},k={r['kept_acc']:.3f}"
                                                 for a, r in sorted(per_alpha.items())))
    return (f"ALPHA_OPT_AT_{best_a}",
            f"alpha={best_a} maximizes min(edit, kept)={best_s:.4f}. "
            f"At alpha=1.0, min={scores.get(1.0, 0):.4f}. Per-alpha: " +
            ", ".join(f"a={a}:e={r['edit_acc']:.3f},k={r['kept_acc']:.3f}"
                          for a, r in sorted(per_alpha.items())))


def self_test_verdict():
    def mk(scores):
        return {a: {"edit_acc": e, "kept_acc": k} for a, (e, k) in scores.items()}
    cases = [
        ({"per_alpha": mk({0.5: (0.7, 1.0), 0.8: (0.9, 1.0),
                           1.0: (0.99, 0.99), 1.2: (0.99, 0.96), 1.5: (0.99, 0.92)})},
         "ALPHA_DEFAULT_BEST"),
        ({"per_alpha": mk({0.5: (0.99, 0.99), 0.8: (0.99, 0.99),
                           1.0: (0.99, 0.99), 1.2: (0.99, 0.99), 1.5: (0.99, 0.99)})},
         "ALPHA_FLAT"),
        ({"per_alpha": mk({0.5: (0.7, 1.0), 0.8: (1.0, 0.99),
                           1.0: (0.99, 0.92), 1.2: (0.95, 0.85), 1.5: (0.90, 0.80)})},
         "ALPHA_OPT_AT_0.8"),
        ({}, "ALPHA_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "n_edit": 5 if smoke else 30,
              "n_kept": 20 if smoke else 100,
              "alphas": [0.8, 1.0] if smoke else [0.5, 0.8, 1.0, 1.2, 1.5],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53]}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)

    per_alpha = {}
    for alpha in config["alphas"]:
        per_seed_e, per_seed_k = [], []
        for seed in config["seeds"]:
            gen = torch.Generator(device=device).manual_seed(seed)
            cpu_gen = torch.Generator().manual_seed(seed + 1009)
            keys = v3.sample_kerdock_keys(codebook, config["M_stored"], cpu_gen, device)
            v_orig = 2.0 * (torch.rand((config["M_stored"], config["N"]),
                                          generator=gen, device=device) > 0.5).float() - 1.0
            v_new = 2.0 * (torch.rand((config["M_stored"], config["N"]),
                                         generator=gen, device=device) > 0.5).float() - 1.0
            W = (v_orig.T @ keys) / config["N"]
            edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
            kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
            edit_idx = sorted(torch.randperm(config["M_stored"],
                                                generator=edit_gen)[:config["n_edit"]].tolist())
            edit_set = set(edit_idx)
            cands = [i for i in range(config["M_stored"]) if i not in edit_set]
            kept_idx = sorted(torch.tensor(cands)[torch.randperm(
                len(cands), generator=kept_gen)[:min(config["n_kept"], len(cands))]].tolist())

            W_edit = W.clone()
            for i in edit_idx:
                W_edit = yb.edit_fact(W_edit, keys[i], v_new[i], alpha, config["N"])
            v_after = v_orig.clone()
            for i in edit_idx:
                v_after[i] = v_new[i]
            edit_target = torch.tensor(edit_idx, device=device)
            kept_target = torch.tensor(kept_idx, device=device)
            ret_e = keys[edit_idx] @ W_edit.T
            edit_acc = float(((ret_e @ v_after.T).argmax(dim=1) == edit_target).float().mean())
            ret_k = keys[kept_idx] @ W_edit.T
            kept_acc = float(((ret_k @ v_after.T).argmax(dim=1) == kept_target).float().mean())
            per_seed_e.append(edit_acc)
            per_seed_k.append(kept_acc)
        per_alpha[alpha] = {"edit_acc": sum(per_seed_e) / len(per_seed_e),
                              "kept_acc": sum(per_seed_k) / len(per_seed_k)}

    summary = {"per_alpha": per_alpha}
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
    out_dir = get_output_dir("wave14zo_alpha_sweep_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    a = config["alphas"][-1]
    e = summary["per_alpha"][a]["edit_acc"]
    oracle.assert_baseline_high("edit_acc_at_top_alpha", e, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zo_alpha_sweep")
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
