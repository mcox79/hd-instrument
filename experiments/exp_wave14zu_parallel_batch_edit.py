"""Parallel batch edit vs sequential - single-transaction edit.

Sequential erase+insert applies n_edit rank-1 updates serially. Batched
version applies them as one update via projection. Compare final W and
retrieval accuracy on the same set of edits.

Pre-reg: preregs/2026-05-21_wave14zu_parallel_batch_edit.md
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
EQUIV_TOL = 0.02


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def batch_edit(W, K_edit, V_new, alpha, N):
    """One-shot edit: project off span of K_edit, add v_new outer products.
    K_edit: (n_edit, N) keys; V_new: (n_edit, N) new values."""
    # Gram matrix on the edit-key subspace: G = K K^T  (n_edit, n_edit)
    G = K_edit @ K_edit.T
    G_inv = torch.linalg.pinv(G)
    # Project W rows off span of K_edit: P = K^T G^-1 K  (N, N)
    # W_new = W - alpha * W @ K^T G^-1 K  =  W (I - alpha * K^T G^-1 K)
    W_proj_coef = K_edit.T @ G_inv @ K_edit  # (N, N)
    W_after = W - alpha * (W @ W_proj_coef)
    # Insert v_new at K_edit: W += V_new.T @ K_edit / N
    W_after = W_after + (V_new.T @ K_edit) / N
    return W_after


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("BATCH_VS_SEQ_INCONCLUSIVE", "Missing.")
    k = arms["kerdock"]
    if "seq_edit_acc" not in k:
        return ("BATCH_VS_SEQ_INCONCLUSIVE", "Missing acc.")
    seq_score = min(k["seq_edit_acc"], k["seq_kept_acc"])
    batch_score = min(k["batch_edit_acc"], k["batch_kept_acc"])
    diff = batch_score - seq_score
    frob_rel = k.get("frob_diff_rel", 0.0)
    if abs(diff) < EQUIV_TOL:
        return ("BATCH_VS_SEQ_EQUIVALENT",
                f"Batched and sequential equivalent: min(edit, kept) "
                f"seq={seq_score:.3f}, batch={batch_score:.3f}. "
                f"Frobenius drift_rel={frob_rel:.4f}.")
    if diff > 0:
        return ("BATCH_BETTER_THAN_SEQ",
                f"Batched outperforms: seq={seq_score:.3f}, batch={batch_score:.3f}. "
                f"Frob drift_rel={frob_rel:.4f}.")
    return ("BATCH_WORSE_THAN_SEQ",
            f"Sequential outperforms batched: seq={seq_score:.3f}, "
            f"batch={batch_score:.3f}. Frob drift_rel={frob_rel:.4f}.")


def self_test_verdict():
    def mk(seq_e, seq_k, b_e, b_k, frob=0.001):
        return {"seq_edit_acc": seq_e, "seq_kept_acc": seq_k,
                 "batch_edit_acc": b_e, "batch_kept_acc": b_k,
                 "frob_diff_rel": frob}
    cases = [
        ({"by_arm": {"kerdock": mk(0.99, 0.99, 0.99, 0.99)}},
         "BATCH_VS_SEQ_EQUIVALENT"),
        ({"by_arm": {"kerdock": mk(0.80, 0.85, 0.99, 0.99)}},
         "BATCH_BETTER_THAN_SEQ"),
        ({"by_arm": {"kerdock": mk(0.99, 0.99, 0.70, 0.80)}},
         "BATCH_WORSE_THAN_SEQ"),
        ({}, "BATCH_VS_SEQ_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_arm(arm_name, codebook, config, device):
    N = config["N"]
    M = config["M_stored"]
    n_edit = config["n_edit"]
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
        v_new = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N

        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        edit_idx = sorted(torch.randperm(M, generator=edit_gen)[:n_edit].tolist())
        edit_set = set(edit_idx)
        cands = [i for i in range(M) if i not in edit_set]
        kept_idx = sorted(torch.tensor(cands)[torch.randperm(
            len(cands), generator=kept_gen)[:min(n_kept, len(cands))]].tolist())

        # Sequential
        W_seq = W.clone()
        for i in edit_idx:
            W_seq = yb.edit_fact(W_seq, keys[i], v_new[i], alpha, N)

        # Batched
        K_edit = keys[edit_idx]
        V_new_subset = v_new[edit_idx]
        W_batch = batch_edit(W, K_edit, V_new_subset, alpha, N)

        v_after = v_orig.clone()
        for i in edit_idx:
            v_after[i] = v_new[i]

        et = torch.tensor(edit_idx, device=device)
        kt = torch.tensor(kept_idx, device=device)
        # Sequential accs
        seq_e = float(((keys[edit_idx] @ W_seq.T) @ v_after.T).argmax(dim=1).eq(et).float().mean())
        seq_k = float(((keys[kept_idx] @ W_seq.T) @ v_after.T).argmax(dim=1).eq(kt).float().mean())
        # Batched accs
        batch_e = float(((keys[edit_idx] @ W_batch.T) @ v_after.T).argmax(dim=1).eq(et).float().mean())
        batch_k = float(((keys[kept_idx] @ W_batch.T) @ v_after.T).argmax(dim=1).eq(kt).float().mean())
        # Frobenius drift relative to W
        w_frob = float(W.norm())
        frob_diff = float((W_seq - W_batch).norm())
        frob_diff_rel = frob_diff / w_frob if w_frob > 0 else 0.0

        per_seed.append({"seed": seed, "seq_edit_acc": seq_e, "seq_kept_acc": seq_k,
                          "batch_edit_acc": batch_e, "batch_kept_acc": batch_k,
                          "frob_diff_rel": frob_diff_rel})

    return {"seq_edit_acc": sum(s["seq_edit_acc"] for s in per_seed) / len(per_seed),
             "seq_kept_acc": sum(s["seq_kept_acc"] for s in per_seed) / len(per_seed),
             "batch_edit_acc": sum(s["batch_edit_acc"] for s in per_seed) / len(per_seed),
             "batch_kept_acc": sum(s["batch_kept_acc"] for s in per_seed) / len(per_seed),
             "frob_diff_rel": sum(s["frob_diff_rel"] for s in per_seed) / len(per_seed),
             "per_seed": per_seed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "n_edit": 5 if smoke else 30,
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
    out_dir = get_output_dir("wave14zu_parallel_batch_edit_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    e = summary["by_arm"]["kerdock"]["batch_edit_acc"]
    oracle.assert_baseline_high("batch_edit", e, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zu_parallel_batch_edit")
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
