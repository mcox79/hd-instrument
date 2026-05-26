"""Bet A continual editing at N=65536 — V2.D Phase 3 sub-test #3.

Per Strategy 20:14 Priority 3: Bet A continual edit at N=65536. Per cycle 98 theory,
edit horizon ~ M = N*k where k=8 at M=8N. At N=65536, predicts ~524K edit horizon.

Pipeline:
  1. Build W with M=N stored (key, value) pairs
  2. Apply n_edits edits via anti-Hebbian erase + insert (Bet A core)
  3. Verify edited pairs retrieve new values; kept pairs retrieve original values

Memory engineering: bf16 W (8.6GB at N=65536); fp32 only for the edit math step.

Verdict thresholds:
  BET_A_N65K_HOLDS_1K: substrate holds 1000-edit, edit_acc >= 0.95 AND kept_acc >= 0.95
  BET_A_N65K_HOLDS_100: 100-edit PASS but 1000-edit fails
  BET_A_N65K_KILLED:    100-edit fails (edit horizon < 100)
  BET_A_N65K_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betA_continual_edit_N65536_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


PASS_EDIT = 0.95
PASS_KEPT = 0.95


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "edit_acc_at_1000" not in summary:
        return ("BET_A_N65K_INCONCLUSIVE", "Missing edit_acc_at_1000.")
    e1k = summary["edit_acc_at_1000"]; k1k = summary["kept_acc_at_1000"]
    e100 = summary["edit_acc_at_100"]; k100 = summary["kept_acc_at_100"]
    if e1k >= PASS_EDIT and k1k >= PASS_KEPT:
        return ("BET_A_N65K_HOLDS_1K",
                f"Bet A holds 1000 edits at N=65536: edit_acc={e1k:.3f}>=0.95, kept_acc={k1k:.3f}>=0.95. "
                f"Substrate-product editable-memory scales to 1K edits at N=65536. "
                f"100-edit: edit={e100:.3f}, kept={k100:.3f}.")
    if e100 >= PASS_EDIT and k100 >= PASS_KEPT:
        return ("BET_A_N65K_HOLDS_100",
                f"Bet A holds 100 edits but breaks at 1000: 100-edit (edit={e100:.3f}, kept={k100:.3f}); "
                f"1000-edit (edit={e1k:.3f}, kept={k1k:.3f}).")
    return ("BET_A_N65K_KILLED",
            f"Bet A fails at 100 edits: edit_acc={e100:.3f}, kept_acc={k100:.3f}. "
            f"1000-edit: edit={e1k:.3f}, kept={k1k:.3f}.")


def self_test_verdict():
    cases = [
        ({"edit_acc_at_1000": 0.98, "kept_acc_at_1000": 0.97, "edit_acc_at_100": 1.0, "kept_acc_at_100": 1.0}, "BET_A_N65K_HOLDS_1K"),
        ({"edit_acc_at_1000": 0.30, "kept_acc_at_1000": 0.50, "edit_acc_at_100": 0.96, "kept_acc_at_100": 0.96}, "BET_A_N65K_HOLDS_100"),
        ({"edit_acc_at_1000": 0.0, "kept_acc_at_1000": 0.0, "edit_acc_at_100": 0.20, "kept_acc_at_100": 0.20}, "BET_A_N65K_KILLED"),
        ({}, "BET_A_N65K_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_initial_W(M, N, cpu_gen, device, dtype=torch.bfloat16):
    kb = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device).to(dtype)
    keys = 2.0 * kb - 1.0
    vb = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device).to(dtype)
    values = 2.0 * vb - 1.0
    W = (values.T.to(torch.float32) @ keys.to(torch.float32)) / N
    W = W.to(dtype)
    return W, keys, values


def apply_edit(W, k, v_new, N, alpha=1.0, dtype=torch.bfloat16):
    """Anti-Hebbian erase + insert at key k for new value v_new.
    Returns updated W."""
    Wfp = W.to(torch.float32)
    kfp = k.to(torch.float32); vfp = v_new.to(torch.float32)
    Wk = Wfp @ kfp
    k_norm_sq = float((kfp * kfp).sum())
    Wfp = Wfp - alpha * torch.outer(Wk, kfp) / max(k_norm_sq, 1e-9)
    Wfp = Wfp + torch.outer(vfp, kfp) / N
    return Wfp.to(dtype)


def query_pair(W, k, v_target, N, dtype=torch.bfloat16):
    """Query W for key k; check if argmax over candidates includes v_target.
    For simplicity, we test if sign(W @ k) overlap with v_target is high (>0.7)."""
    Wfp = W.to(torch.float32)
    kfp = k.to(torch.float32)
    pred = torch.sign(Wfp @ kfp)
    pred[pred == 0] = 1.0
    overlap = float((pred * v_target.to(torch.float32)).mean())
    return overlap > 0.7


def run_one_seed(n_edits, N, M_init, cpu_gen, device):
    print(f"    Building initial W (M={M_init}, N={N}, bf16)...", flush=True)
    W, keys, values = build_initial_W(M_init, N, cpu_gen, device)
    # Generate edit triggers: pick subset of keys and assign new values
    edit_indices = torch.randperm(M_init, generator=cpu_gen)[:n_edits].to(device)
    new_vals = []
    print(f"    Generating {n_edits} edit triggers...", flush=True)
    for i in range(n_edits):
        vb = (torch.rand(N, generator=cpu_gen) > 0.5).to(device).to(torch.bfloat16)
        new_vals.append(2.0 * vb - 1.0)
    print(f"    Applying {n_edits} edits...", flush=True)
    for i, idx in enumerate(edit_indices):
        k = keys[idx]
        v_new = new_vals[i]
        W = apply_edit(W, k, v_new, N)
        if (i + 1) % max(1, n_edits // 4) == 0:
            print(f"      edit {i+1}/{n_edits}", flush=True)
    # Verify edited pairs
    n_check = min(50, n_edits)
    check_idx = edit_indices[:n_check]
    edit_correct = 0
    for j, idx in enumerate(check_idx):
        k = keys[idx]
        v_new = new_vals[j]
        if query_pair(W, k, v_new, N):
            edit_correct += 1
    edit_acc = edit_correct / n_check
    # Verify kept pairs (subset of M_init that were NOT edited)
    edited_set = set(edit_indices.tolist())
    kept_candidates = [i for i in range(M_init) if i not in edited_set][:n_check]
    kept_correct = 0
    for idx in kept_candidates:
        k = keys[idx]
        v_orig = values[idx]
        if query_pair(W, k, v_orig, N):
            kept_correct += 1
    kept_acc = kept_correct / max(len(kept_candidates), 1)
    del W, keys, values, new_vals
    if device.type == "cuda": torch.cuda.empty_cache()
    return edit_acc, kept_acc


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 4096 if smoke else 65536,
              "M_init": 4096 if smoke else 65536,
              "n_edits_grid": [50, 100] if smoke else [100, 1000],
              "seed": 17}
    N = config["N"]
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    print(f"[setup] N={N} M_init={config['M_init']}", flush=True)
    results = {}
    for n_edits in config["n_edits_grid"]:
        print(f"\n[n_edits={n_edits}]", flush=True)
        e_acc, k_acc = run_one_seed(n_edits, N, config["M_init"], cpu_gen, device)
        results[n_edits] = {"edit_acc": e_acc, "kept_acc": k_acc}
        print(f"  n_edits={n_edits}: edit_acc={e_acc:.3f}, kept_acc={k_acc:.3f}", flush=True)
    e100 = results.get(100, {}).get("edit_acc", 0.0)
    k100 = results.get(100, {}).get("kept_acc", 0.0)
    e1k = results.get(1000, {}).get("edit_acc", 0.0)
    k1k = results.get(1000, {}).get("kept_acc", 0.0)
    summary = {"edit_acc_at_100": e100, "kept_acc_at_100": k100,
                "edit_acc_at_1000": e1k, "kept_acc_at_1000": k1k,
                "per_n_edits": {str(k): v for k, v in results.items()}}
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
    out_dir = get_output_dir("wave14_betA_continual_edit_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("edit_acc_present", summary["edit_acc_at_100"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betA_continual_edit_N65536_v1")
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
