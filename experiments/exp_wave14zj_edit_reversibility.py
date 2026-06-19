"""Edit reversibility - repeated erase+insert cycles at same key.

yb established edit-then-query KERDOCK_PASS for one-shot edits at distinct keys.
yc/zh tested continual editing across different keys. zj tests algebra closure
under REPEATED edits at the SAME key: cycle (erase v_orig, insert v_new),
(erase v_new, insert v_orig). After many cycles, does v_orig still retrieve cleanly?

Pre-reg: preregs/2026-05-21_wave14zj_edit_reversibility.md
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

PASS_FINAL_ACC = 0.95
PASS_KEPT_ACC = 0.95


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def first_drift_cycle(traj, key, threshold):
    for r in traj:
        if r.get(key, 1.0) < threshold:
            return r["cycle"]
    return None


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("REVERSIBLE_INCONCLUSIVE", "Missing kerdock arm.")
    k = arms["kerdock"]
    c = arms.get("correlated", {})
    if not k.get("per_cycle_trajectory"):
        return ("REVERSIBLE_INCONCLUSIVE", "Missing traj.")
    n_cycles = len(k["per_cycle_trajectory"])
    k_drift = first_drift_cycle(k["per_cycle_trajectory"], "orig_recovery_acc", PASS_FINAL_ACC)
    k_kept_drift = first_drift_cycle(k["per_cycle_trajectory"], "kept_acc", PASS_KEPT_ACC)
    c_drift = first_drift_cycle(c.get("per_cycle_trajectory", []), "orig_recovery_acc", PASS_FINAL_ACC)

    k_holds = k_drift is None and k_kept_drift is None
    c_holds = c_drift is None

    if k_holds and not c_holds:
        return (f"REVERSIBLE_KERDOCK_HOLDS_TO_{n_cycles}",
                f"Kerdock survives {n_cycles} reversal cycles: final orig_recovery="
                f"{k['final_orig_recovery_acc']:.3f}, final kept={k['final_kept_acc']:.3f}. "
                f"Correlated drifts at cycle {c_drift}. Algebra closure under repeated "
                f"same-key edits requires structured keys.")
    if k_holds and c_holds:
        return ("REVERSIBLE_BOTH_HOLD",
                f"Both arms survive {n_cycles} reversal cycles. Correlated control held "
                f"unexpectedly; algebra closure may be substrate-wide, not Kerdock-specific.")
    if not k_holds and not c_holds:
        return ("REVERSIBLE_BOTH_DRIFT",
                f"Both arms drift. Kerdock at cycle {k_drift or k_kept_drift}, "
                f"correlated at cycle {c_drift}. Repeated same-key editing accumulates error "
                f"regardless of key structure.")
    return (f"REVERSIBLE_KERDOCK_DRIFTS_AT_{k_drift or k_kept_drift}",
            f"Kerdock drifts at cycle {k_drift or k_kept_drift}. Same-key edit reversal "
            f"accumulates rank-1 perturbations even with structured keys.")


def self_test_verdict():
    def mk(orig_floor, kept_floor=1.0, n=50):
        traj = [{"cycle": i,
                 "orig_recovery_acc": 1.0 if orig_floor >= PASS_FINAL_ACC else (1.0 if i < n // 2 else 0.5),
                 "kept_acc": kept_floor} for i in range(1, n + 1)]
        return {"per_cycle_trajectory": traj,
                "final_orig_recovery_acc": orig_floor,
                "final_kept_acc": kept_floor}
    cases = [
        ({"by_arm": {"kerdock": mk(0.99), "correlated": mk(0.5)}},
         "REVERSIBLE_KERDOCK_HOLDS_TO_50"),
        ({"by_arm": {"kerdock": mk(0.99), "correlated": mk(0.99)}},
         "REVERSIBLE_BOTH_HOLD"),
        ({"by_arm": {"kerdock": mk(0.5), "correlated": mk(0.5)}},
         "REVERSIBLE_BOTH_DRIFT"),
        ({"by_arm": {"kerdock": mk(0.5), "correlated": mk(0.99)}},
         "REVERSIBLE_KERDOCK_DRIFTS_AT_25"),
        ({}, "REVERSIBLE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def run_arm(arm_name, codebook, config, device):
    """One arm: build substrate, run N_CYCLES reversal cycles on a subset of keys."""
    N = config["N"]
    M = config["M_stored"]
    n_subj = config["n_subjects"]
    n_cycles = config["n_cycles"]
    n_kept = config["n_kept"]
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
        v_alt = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N

        subj_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        subj_idx = sorted(torch.randperm(M, generator=subj_gen)[:n_subj].tolist())
        subj_set = set(subj_idx)
        cands = [i for i in range(M) if i not in subj_set]
        kept_idx = sorted(torch.tensor(cands)[torch.randperm(
            len(cands), generator=kept_gen)[:min(n_kept, len(cands))]].tolist())
        subj_target = torch.tensor(subj_idx, device=device)
        kept_target = torch.tensor(kept_idx, device=device)

        traj = []
        W_curr = W.clone()
        for cyc in range(1, n_cycles + 1):
            for i in subj_idx:
                W_curr = yb.edit_fact(W_curr, keys[i], v_alt[i], alpha, N)
            for i in subj_idx:
                W_curr = yb.edit_fact(W_curr, keys[i], v_orig[i], alpha, N)
            if cyc == n_cycles or cyc % max(1, n_cycles // 10) == 0:
                subj_keys = keys[subj_idx]
                ret = subj_keys @ W_curr.T
                sims = ret @ v_orig.T
                pred = sims.argmax(dim=1)
                orig_acc = float((pred == subj_target).float().mean())

                kept_keys = keys[kept_idx]
                ret_k = kept_keys @ W_curr.T
                sims_k = ret_k @ v_orig.T
                pred_k = sims_k.argmax(dim=1)
                kept_acc = float((pred_k == kept_target).float().mean())
                traj.append({"cycle": cyc, "orig_recovery_acc": orig_acc,
                              "kept_acc": kept_acc})

        per_seed.append({"seed": seed, "trajectory": traj})

    # Aggregate
    n_pts = len(per_seed[0]["trajectory"])
    agg_traj = []
    for j in range(n_pts):
        cyc = per_seed[0]["trajectory"][j]["cycle"]
        o = sum(s["trajectory"][j]["orig_recovery_acc"] for s in per_seed) / len(per_seed)
        k = sum(s["trajectory"][j]["kept_acc"] for s in per_seed) / len(per_seed)
        agg_traj.append({"cycle": cyc, "orig_recovery_acc": o, "kept_acc": k})
    return {"per_cycle_trajectory": agg_traj,
             "final_orig_recovery_acc": agg_traj[-1]["orig_recovery_acc"],
             "final_kept_acc": agg_traj[-1]["kept_acc"],
             "per_seed": per_seed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 512 if smoke else 4096,
              "n_subjects": 5 if smoke else 20,
              "n_cycles": 10 if smoke else 50,
              "n_kept": 20 if smoke else 100,
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
    out_dir = get_output_dir("wave14zj_edit_reversibility_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = summary["by_arm"]["kerdock"]["per_cycle_trajectory"][0]
    oracle.assert_baseline_high("kerdock_cycle1", first["orig_recovery_acc"], 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zj_edit_reversibility")
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
