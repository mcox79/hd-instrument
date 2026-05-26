"""Noisy edit keys - erase+insert applied at Hamming-perturbed key.

In deployed systems the editor may not have the exact stored key. Snap-to-codebook
handles noisy QUERIES on Kerdock (yb result); zk tests noisy EDIT keys.

Pipeline: perturb keys[i] by radius h, then (Kerdock arm) snap to codebook,
(correlated) use raw. Apply erase+insert. Query at exact k_i; did edit land?

Pre-reg: preregs/2026-05-21_wave14zk_noisy_edit_keys.md
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
_v2 = importlib.util.spec_from_file_location("v2", REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py")
v2 = importlib.util.module_from_spec(_v2); _v2.loader.exec_module(v2)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)

PASS_LAND = 0.90
PASS_KEPT = 0.95


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def first_fail_h(per_h, key, threshold):
    for h in sorted(per_h.keys()):
        if per_h[h].get(key, 1.0) < threshold:
            return h
    return None


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("NOISY_EDIT_INCONCLUSIVE", "Missing.")
    k = arms["kerdock"]
    c = arms.get("correlated", {})
    if not k.get("per_h"):
        return ("NOISY_EDIT_INCONCLUSIVE", "Missing per_h.")
    k_fail = first_fail_h(k["per_h"], "edit_land_acc", PASS_LAND)
    k_kept_fail = first_fail_h(k["per_h"], "kept_acc", PASS_KEPT)
    c_fail = first_fail_h(c.get("per_h", {}), "edit_land_acc", PASS_LAND)
    k_holds = (k_fail is None and k_kept_fail is None)
    c_holds = (c_fail is None)
    hs = sorted(k["per_h"].keys())
    if k_holds and not c_holds:
        return ("NOISY_EDIT_KERDOCK_PASS",
                f"Kerdock holds noisy edit across radii {hs}: edit_land_acc>="
                f"{min(k['per_h'][h]['edit_land_acc'] for h in hs):.3f}. Correlated "
                f"fails at h={c_fail}. Snap-to-codebook lands edits at intended key.")
    if k_holds and c_holds:
        return ("NOISY_EDIT_BOTH_PASS",
                f"Both arms tolerate noisy edits across radii {hs}.")
    if not k_holds and not c_holds:
        return ("NOISY_EDIT_BOTH_FAIL",
                f"Both arms fail noisy edits. Kerdock at h={k_fail or k_kept_fail}, "
                f"correlated at h={c_fail}.")
    return (f"NOISY_EDIT_KERDOCK_DEGRADES_AT_H{k_fail or k_kept_fail}",
            f"Kerdock edit landing degrades at h={k_fail or k_kept_fail}.")


def self_test_verdict():
    def mk(land_floor, kept_floor=1.0, hs=(4, 8, 16)):
        per_h = {h: {"edit_land_acc": 1.0 if land_floor >= PASS_LAND or h < 8 else 0.5,
                      "kept_acc": kept_floor} for h in hs}
        if land_floor < PASS_LAND:
            per_h[hs[-1]]["edit_land_acc"] = 0.5
        return {"per_h": per_h}
    cases = [
        ({"by_arm": {"kerdock": mk(1.0), "correlated": mk(0.5)}},
         "NOISY_EDIT_KERDOCK_PASS"),
        ({"by_arm": {"kerdock": mk(1.0), "correlated": mk(1.0)}},
         "NOISY_EDIT_BOTH_PASS"),
        ({"by_arm": {"kerdock": mk(0.5), "correlated": mk(0.5)}},
         "NOISY_EDIT_BOTH_FAIL"),
        ({"by_arm": {"kerdock": mk(0.5), "correlated": mk(1.0)}},
         "NOISY_EDIT_KERDOCK_DEGRADES_AT_H8"),
        ({}, "NOISY_EDIT_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def run_arm(arm_name, codebook, config, device):
    N = config["N"]
    M = config["M_stored"]
    n_edit = config["n_edit"]
    n_kept = config["n_kept"]
    hs = config["hamming_radii"]
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
        W_base = (v_orig.T @ keys) / N

        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        edit_idx = sorted(torch.randperm(M, generator=edit_gen)[:n_edit].tolist())
        edit_set = set(edit_idx)
        cands = [i for i in range(M) if i not in edit_set]
        kept_idx = sorted(torch.tensor(cands)[torch.randperm(
            len(cands), generator=kept_gen)[:min(n_kept, len(cands))]].tolist())
        edit_target = torch.tensor(edit_idx, device=device)
        kept_target = torch.tensor(kept_idx, device=device)

        edit_keys_exact = keys[edit_idx]
        per_h = {}
        for h in hs:
            W_curr = W_base.clone()
            edit_keys_noisy = v1.hamming_perturb(edit_keys_exact, 1, h, cpu_gen, device)
            if codebook is not None:
                edit_keys_use = v2.snap_to_codebook_batch(edit_keys_noisy, codebook)
            else:
                edit_keys_use = edit_keys_noisy
            for j, i in enumerate(edit_idx):
                W_curr = yb.edit_fact(W_curr, edit_keys_use[j], v_new[i], alpha, N)

            v_after = v_orig.clone()
            for i in edit_idx:
                v_after[i] = v_new[i]
            # Query at EXACT k_i; check edit_argmax_acc
            ret = edit_keys_exact @ W_curr.T
            sims = ret @ v_after.T
            pred = sims.argmax(dim=1)
            edit_land_acc = float((pred == edit_target).float().mean())

            ret_k = keys[kept_idx] @ W_curr.T
            sims_k = ret_k @ v_after.T
            pred_k = sims_k.argmax(dim=1)
            kept_acc = float((pred_k == kept_target).float().mean())
            per_h[h] = {"edit_land_acc": edit_land_acc, "kept_acc": kept_acc}
        per_seed.append({"seed": seed, "per_h": per_h})

    agg_h = {}
    for h in hs:
        agg_h[h] = {
            "edit_land_acc": sum(s["per_h"][h]["edit_land_acc"] for s in per_seed) / len(per_seed),
            "kept_acc": sum(s["per_h"][h]["kept_acc"] for s in per_seed) / len(per_seed),
        }
    return {"per_h": agg_h, "per_seed": per_seed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 512 if smoke else 4096,
              "n_edit": 5 if smoke else 30,
              "n_kept": 20 if smoke else 100,
              "hamming_radii": [8] if smoke else [4, 8, 16, 32],
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
    out_dir = get_output_dir("wave14zk_noisy_edit_keys_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    h = config["hamming_radii"][0]
    first = summary["by_arm"]["kerdock"]["per_h"][h]
    oracle.assert_baseline_high(f"kerdock_h{h}", first["edit_land_acc"], 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zk_noisy_edit_keys")
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
