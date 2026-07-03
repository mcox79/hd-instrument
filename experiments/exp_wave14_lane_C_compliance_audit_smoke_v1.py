"""Lane C compliance-audit smoke - composes Bet 2/C erase + Bet A edit + Bet G calibration.

Engineering integration of validated primitives into a compliance-audit demo
pipeline. NOT new substrate physics; tests composition.

Pipeline:
1. Build N=4096 substrate with M=100 enterprise-style facts via Kerdock keys
2. Apply N_edit edits via Bet A anti-Hebbian erase + insert
3. Apply M_del deletes via Bet 2/C anti-Hebbian erase
4. Mirage probes after each delete
5. TEMPSCALE β=32 calibration on the final substrate

Pre-reg: preregs/2026-05-21_wave14_lane_C_compliance_audit_smoke_v1.md
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

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)

PASS_MIRAGE_LEAK = 0.05
PASS_KEPT = 0.90
PASS_ECE = 0.10
PASS_SIDE_EFFECT = 0.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def compute_verdict(summary):
    if "delete_leak_max" not in summary:
        return ("LANE_C_INCONCLUSIVE", "Missing metrics.")
    delete_leak_max = summary["delete_leak_max"]
    edit_acc = summary["edit_acc"]
    side_effect = summary["side_effect_rate"]
    kept_acc = summary["kept_acc"]
    ece = summary["ece_post"]
    pass_delete = delete_leak_max <= PASS_MIRAGE_LEAK
    pass_edit = edit_acc >= PASS_KEPT and side_effect <= PASS_SIDE_EFFECT
    pass_kept = kept_acc >= PASS_KEPT
    pass_calib = ece <= PASS_ECE
    if pass_delete and pass_edit and pass_kept and pass_calib:
        return ("LANE_C_PRIMITIVES_COMPOSE",
                f"Lane C primitives compose into compliance-audit pipeline. "
                f"delete_leak_max={delete_leak_max:.4f} (<={PASS_MIRAGE_LEAK}), "
                f"edit_acc={edit_acc:.3f}, kept_acc={kept_acc:.3f}, "
                f"side_effect={side_effect:.4f}, ECE={ece:.4f}.")
    fails = []
    if not pass_delete: fails.append(f"delete_leak={delete_leak_max:.4f}")
    if not pass_edit: fails.append(f"edit_acc={edit_acc:.3f}/side_eff={side_effect:.4f}")
    if not pass_kept: fails.append(f"kept_acc={kept_acc:.3f}")
    if not pass_calib: fails.append(f"ECE={ece:.4f}")
    if len(fails) == 1:
        return (f"LANE_C_PARTIAL_{fails[0].split('=')[0].upper()}",
                f"Partial: {fails[0]} failed; others pass.")
    return ("LANE_C_INCOMPATIBLE",
            f"Multiple components fail composition: {'; '.join(fails)}.")


def self_test_verdict():
    def mk(d):
        return {"delete_leak_max": d.get("dl", 0.02),
                "edit_acc": d.get("ea", 0.95),
                "side_effect_rate": d.get("se", 0.02),
                "kept_acc": d.get("ka", 0.95),
                "ece_post": d.get("ece", 0.05)}
    cases = [
        (mk({}), "LANE_C_PRIMITIVES_COMPOSE"),
        (mk({"dl": 0.20}), "LANE_C_PARTIAL_DELETE_LEAK"),
        (mk({"dl": 0.20, "ece": 0.30}), "LANE_C_INCOMPATIBLE"),
        ({}, "LANE_C_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def compute_ece(probs, correct, n_bins=10):
    """Standard ECE on (probs, correct) pairs."""
    n = len(probs)
    if n == 0:
        return 0.0
    ece = 0.0
    for b in range(n_bins):
        lo, hi = b / n_bins, (b + 1) / n_bins
        in_bin = [(p, c) for p, c in zip(probs, correct) if lo <= p < hi or (b == n_bins - 1 and p == 1.0)]
        if not in_bin:
            continue
        mean_conf = sum(p for p, _ in in_bin) / len(in_bin)
        mean_acc = sum(1.0 if c else 0.0 for _, c in in_bin) / len(in_bin)
        ece += (len(in_bin) / n) * abs(mean_conf - mean_acc)
    return ece


def run_one_seed(seed, config, device):
    N = config["N"]
    M = config["M_facts"]
    N_edit = config["n_edits"]
    M_del = config["n_deletes"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
    v_orig = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    v_new = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (v_orig.T @ keys) / N

    # Step 1: Apply N_edit edits via Bet A
    edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
    edit_idx = sorted(torch.randperm(M, generator=edit_gen)[:N_edit].tolist())
    edit_set = set(edit_idx)
    W_edited = W.clone()
    for i in edit_idx:
        W_edited = yb.edit_fact(W_edited, keys[i], v_new[i], 1.0, N)
    v_after = v_orig.clone()
    for i in edit_idx:
        v_after[i] = v_new[i]

    # Step 2: Apply M_del deletes via Bet 2/C anti-Hebbian erase
    del_gen = torch.Generator().manual_seed(seed * 31 + 11)
    cands_after_edit = [i for i in range(M) if i not in edit_set]
    del_idx = sorted(torch.tensor(cands_after_edit)[torch.randperm(
        len(cands_after_edit), generator=del_gen)[:M_del]].tolist())
    W_deleted = W_edited.clone()
    for i in del_idx:
        # Anti-Hebbian rank-1 erase (no insert)
        Wk = W_deleted @ keys[i]
        knorm_sq = float((keys[i] * keys[i]).sum())
        W_deleted = W_deleted - torch.outer(Wk, keys[i]) / knorm_sq

    # Mirage probes on deleted facts: argmax leak (does v_after argmax return the OLD value?)
    deleted_keys = keys[del_idx]
    deleted_old_v = v_orig[del_idx]
    retrieved = deleted_keys @ W_deleted.T
    sims = retrieved @ v_orig.T  # against original v
    # Leakage: top sim being the deleted-fact original value
    pred = sims.argmax(dim=1)
    leak_rate = float((pred == torch.tensor(del_idx, device=device)).float().mean())

    # Kept facts (not edited, not deleted)
    kept_idx = sorted([i for i in range(M) if i not in edit_set and i not in set(del_idx)])
    n_kept_eval = min(50, len(kept_idx))
    kept_idx = kept_idx[:n_kept_eval]
    kept_target = torch.tensor(kept_idx, device=device)
    ret_k = keys[kept_idx] @ W_deleted.T
    pred_k = (ret_k @ v_after.T).argmax(dim=1)
    kept_acc = float((pred_k == kept_target).float().mean())

    # Edit-acc: edited facts still resolve to new value
    edit_target = torch.tensor(edit_idx, device=device)
    ret_e = keys[edit_idx] @ W_deleted.T
    pred_e = (ret_e @ v_after.T).argmax(dim=1)
    edit_acc = float((pred_e == edit_target).float().mean())

    # Side effect: kept facts that changed argmax due to deletes
    pre_pred = (keys[kept_idx] @ W_edited.T @ v_after.T).argmax(dim=1)
    side_effect = float(((pre_pred == kept_target) & (pred_k != kept_target)).float().mean())

    # Step 3: TEMPSCALE β=32 calibration on final substrate
    beta = 32.0
    all_probs, all_correct = [], []
    eval_idx = kept_idx + edit_idx
    eval_target = torch.tensor(eval_idx, device=device)
    ret_eval = keys[eval_idx] @ W_deleted.T
    sims_eval = (ret_eval @ v_after.T) / N
    scaled = sims_eval * beta
    scaled = scaled - scaled.max(dim=1, keepdim=True).values
    probs = torch.softmax(scaled, dim=1)
    max_probs = probs.max(dim=1).values
    pred_eval = probs.argmax(dim=1)
    correct_eval = (pred_eval == eval_target)
    all_probs.extend(max_probs.tolist())
    all_correct.extend(correct_eval.tolist())
    ece = compute_ece(all_probs, all_correct)

    return {"delete_leak_max": leak_rate, "edit_acc": edit_acc,
             "side_effect_rate": side_effect, "kept_acc": kept_acc,
             "ece_post": ece}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_facts": 30 if smoke else 100,
              "n_edits": 10 if smoke else 50,
              "n_deletes": 8 if smoke else 30,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: leak={r['delete_leak_max']:.4f} edit={r['edit_acc']:.3f} "
              f"kept={r['kept_acc']:.3f} side={r['side_effect_rate']:.4f} "
              f"ECE={r['ece_post']:.4f}", flush=True)
    # Aggregate (mean)
    summary = {
        "delete_leak_max": sum(r["delete_leak_max"] for r in per_seed.values()) / len(per_seed),
        "edit_acc": sum(r["edit_acc"] for r in per_seed.values()) / len(per_seed),
        "side_effect_rate": sum(r["side_effect_rate"] for r in per_seed.values()) / len(per_seed),
        "kept_acc": sum(r["kept_acc"] for r in per_seed.values()) / len(per_seed),
        "ece_post": sum(r["ece_post"] for r in per_seed.values()) / len(per_seed),
        "per_seed": per_seed,
    }
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
    out_dir = get_output_dir("wave14_lane_C_compliance_audit_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("kept_acc", summary["kept_acc"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_C_compliance_audit_smoke_v1")
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
