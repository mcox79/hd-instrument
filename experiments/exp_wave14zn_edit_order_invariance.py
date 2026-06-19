"""Edit-order invariance - does anti-Hebbian erase commute across keys?

Anti-Hebbian erase exactly commutes for orthogonal keys, not for correlated.
Test: apply edits in order P1 then P2=reverse(P1), measure Frobenius drift
||W_p1 - W_p2||_F / ||W||_F and argmax accuracy after each ordering.

Pre-reg: preregs/2026-05-21_wave14zn_edit_order_invariance.md
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

FROB_COMMUTE_TOL = 0.05
ARGMAX_TOL = 0.95


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("ORDER_INVARIANT_INCONCLUSIVE", "Missing.")
    k = arms["kerdock"]
    c = arms.get("correlated", {})
    if "frob_drift_rel" not in k:
        return ("ORDER_INVARIANT_INCONCLUSIVE", "Missing frob.")
    k_frob_commutes = k["frob_drift_rel"] < FROB_COMMUTE_TOL
    c_frob_commutes = c.get("frob_drift_rel", 1.0) < FROB_COMMUTE_TOL
    k_argmax_stable = (k["argmax_p1"] >= ARGMAX_TOL and k["argmax_p2"] >= ARGMAX_TOL)
    if k_frob_commutes and not c_frob_commutes:
        return ("ORDER_INVARIANT_KERDOCK_COMMUTES",
                f"Kerdock anti-Hebbian erase near-commutes: frob_drift_rel="
                f"{k['frob_drift_rel']:.4f} < {FROB_COMMUTE_TOL}. "
                f"Correlated drifts {c['frob_drift_rel']:.4f}. Argmax stable: "
                f"p1={k['argmax_p1']:.3f}, p2={k['argmax_p2']:.3f}.")
    if k_frob_commutes and c_frob_commutes:
        return ("ORDER_INVARIANT_BOTH_COMMUTE",
                f"Both arms commute. Kerdock frob={k['frob_drift_rel']:.4f}, "
                f"correlated frob={c['frob_drift_rel']:.4f}.")
    if not k_frob_commutes and k_argmax_stable:
        return ("ORDER_INVARIANT_ARGMAX_STABLE_FROBENIUS_DRIFTS",
                f"Frobenius drift {k['frob_drift_rel']:.4f} > {FROB_COMMUTE_TOL} but "
                f"argmax stable (p1={k['argmax_p1']:.3f}, p2={k['argmax_p2']:.3f}). "
                f"Substrate is order-robust at the retrieval level.")
    return ("ORDER_INVARIANT_FAILS",
            f"Kerdock fails ordering invariance: frob_drift_rel="
            f"{k['frob_drift_rel']:.4f}, argmax_p1={k['argmax_p1']:.3f}, "
            f"argmax_p2={k['argmax_p2']:.3f}.")


def self_test_verdict():
    def mk(frob, ap1=0.99, ap2=0.99):
        return {"frob_drift_rel": frob, "argmax_p1": ap1, "argmax_p2": ap2}
    cases = [
        ({"by_arm": {"kerdock": mk(0.001), "correlated": mk(0.2)}},
         "ORDER_INVARIANT_KERDOCK_COMMUTES"),
        ({"by_arm": {"kerdock": mk(0.001), "correlated": mk(0.001)}},
         "ORDER_INVARIANT_BOTH_COMMUTE"),
        ({"by_arm": {"kerdock": mk(0.1, ap1=0.99, ap2=0.99), "correlated": mk(0.5)}},
         "ORDER_INVARIANT_ARGMAX_STABLE_FROBENIUS_DRIFTS"),
        ({"by_arm": {"kerdock": mk(0.5, ap1=0.5, ap2=0.5), "correlated": mk(0.5)}},
         "ORDER_INVARIANT_FAILS"),
        ({}, "ORDER_INVARIANT_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def apply_edits(W, keys, v_new, edit_idx, alpha, N):
    W_curr = W.clone()
    for i in edit_idx:
        W_curr = yb.edit_fact(W_curr, keys[i], v_new[i], alpha, N)
    return W_curr


def run_arm(arm_name, codebook, config, device):
    N = config["N"]
    M = config["M_stored"]
    n_edit = config["n_edit"]
    seeds = config["seeds"]
    alpha = config["alpha"]
    per_seed = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        if codebook is not None:
            keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
        else:
            rank_L = max(2, int(M * 0.25))
            keys = v1.make_correlated_keys(M, N, rank_L, gen, device)
        v_orig = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        v_new = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N
        w_frob = float(W.norm())

        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        edit_idx_p1 = torch.randperm(M, generator=edit_gen)[:n_edit].tolist()
        edit_idx_p2 = list(reversed(edit_idx_p1))

        W_p1 = apply_edits(W, keys, v_new, edit_idx_p1, alpha, N)
        W_p2 = apply_edits(W, keys, v_new, edit_idx_p2, alpha, N)
        frob_diff = float((W_p1 - W_p2).norm())
        frob_drift_rel = frob_diff / w_frob if w_frob > 0 else 0.0

        v_after = v_orig.clone()
        for i in edit_idx_p1:
            v_after[i] = v_new[i]
        edit_keys = keys[edit_idx_p1]
        edit_target = torch.tensor(edit_idx_p1, device=device)

        ret_p1 = edit_keys @ W_p1.T
        pred_p1 = (ret_p1 @ v_after.T).argmax(dim=1)
        argmax_p1 = float((pred_p1 == edit_target).float().mean())
        ret_p2 = edit_keys @ W_p2.T
        pred_p2 = (ret_p2 @ v_after.T).argmax(dim=1)
        argmax_p2 = float((pred_p2 == edit_target).float().mean())

        per_seed.append({"seed": seed, "frob_drift_rel": frob_drift_rel,
                          "argmax_p1": argmax_p1, "argmax_p2": argmax_p2})

    return {"frob_drift_rel": sum(s["frob_drift_rel"] for s in per_seed) / len(per_seed),
             "argmax_p1": sum(s["argmax_p1"] for s in per_seed) / len(per_seed),
             "argmax_p2": sum(s["argmax_p2"] for s in per_seed) / len(per_seed),
             "per_seed": per_seed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "n_edit": 10 if smoke else 50,
              "seeds": [17] if smoke else [17, 23, 31, 41, 53],
              "alpha": 1.0}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = run_arm("kerdock", codebook, config, device)
    arm_c = run_arm("correlated", None, config, device)
    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
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
    out_dir = get_output_dir("wave14zn_edit_order_invariance_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    a1 = summary["by_arm"]["kerdock"]["argmax_p1"]
    oracle.assert_baseline_high("kerdock_argmax_p1", a1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zn_edit_order_invariance")
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
