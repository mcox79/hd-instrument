"""Calibration after editing - does anti-Hebbian erase break temperature scaling?

yx established BETA=8 rescues ECE to ~0.04 on unedited substrate. yb showed
edit-then-query lands cleanly. zl asks: after edits land, is calibration still
clean? Or do the rank-1 perturbations introduce overconfidence/underconfidence?

Pipeline: build substrate, compute ECE at BETA in {1,4,8,16,32}, apply N_EDITS
anti-Hebbian edits, recompute ECE. Compare pre vs post. Also split by whether
the queried fact was edited or kept.

Pre-reg: preregs/2026-05-21_wave14zl_calibration_after_edit.md
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
_yd = importlib.util.spec_from_file_location("yd", REPO / "experiments" / "exp_wave14yd_calibration_fact_retrieval.py")
yd = importlib.util.module_from_spec(_yd); _yd.loader.exec_module(yd)
_yb = importlib.util.spec_from_file_location("yb", REPO / "experiments" / "exp_wave14yb_edit_then_query_kerdock.py")
yb = importlib.util.module_from_spec(_yb); _yb.loader.exec_module(yb)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "pre_ece_best" not in summary or "post_ece_kept_best" not in summary:
        return ("CALIB_INCONCLUSIVE", "Missing pre/post ECE.")
    pre = summary["pre_ece_best"]
    post_kept = summary["post_ece_kept_best"]
    post_edit = summary.get("post_ece_edit_best", post_kept)
    delta_kept = post_kept - pre
    delta_edit = post_edit - pre
    if abs(delta_kept) < 0.03 and abs(delta_edit) < 0.05:
        return ("CALIB_PRESERVED_AFTER_EDIT",
                f"ECE preserved. pre={pre:.4f}, post_kept={post_kept:.4f} "
                f"(delta={delta_kept:+.4f}), post_edit={post_edit:.4f} "
                f"(delta={delta_edit:+.4f}). Edits don't break calibration.")
    if abs(delta_edit) >= 0.05 and abs(delta_kept) < 0.03:
        return ("CALIB_DEGRADED_ON_EDITED_FACTS",
                f"Edited-fact calibration degrades. pre={pre:.4f}, "
                f"post_edit={post_edit:.4f} (delta={delta_edit:+.4f}). "
                f"Kept calibration intact (post_kept={post_kept:.4f}).")
    return ("CALIB_DEGRADED_GLOBALLY",
            f"Global calibration degrades after edits. pre={pre:.4f}, "
            f"post_kept={post_kept:.4f} (delta={delta_kept:+.4f}), "
            f"post_edit={post_edit:.4f} (delta={delta_edit:+.4f}).")


def self_test_verdict():
    cases = [
        ({"pre_ece_best": 0.04, "post_ece_kept_best": 0.05, "post_ece_edit_best": 0.06},
         "CALIB_PRESERVED_AFTER_EDIT"),
        ({"pre_ece_best": 0.04, "post_ece_kept_best": 0.05, "post_ece_edit_best": 0.20},
         "CALIB_DEGRADED_ON_EDITED_FACTS"),
        ({"pre_ece_best": 0.04, "post_ece_kept_best": 0.30, "post_ece_edit_best": 0.30},
         "CALIB_DEGRADED_GLOBALLY"),
        ({}, "CALIB_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def ece_on_subset(W, keys, values, idx, hamming_radii, beta, cpu_gen, device):
    """ECE computed only on the subset of facts indexed by idx."""
    N = keys.size(-1)
    keys_sub = keys[idx]
    target_sub = torch.tensor(idx, device=device)
    all_confs, all_correct = [], []
    for h in hamming_radii:
        probe = keys_sub if h == 0 else v1.hamming_perturb(keys_sub, 1, h, cpu_gen, device)
        retrieved = probe @ W.T
        sims = retrieved @ values.T / N
        scaled = sims * beta
        scaled = scaled - scaled.max(dim=1, keepdim=True).values
        exp_s = torch.exp(scaled)
        probs = exp_s / exp_s.sum(dim=1, keepdim=True)
        max_probs = probs.max(dim=1).values
        argmax = probs.argmax(dim=1)
        correct = (argmax == target_sub)
        all_confs.extend(max_probs.tolist())
        all_correct.extend(correct.tolist())
    ece, _ = yd.compute_ece(all_confs, all_correct, n_bins=10)
    return ece


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "n_edit": 5 if smoke else 30,
              "betas": [1, 8] if smoke else [1, 2, 4, 8, 16, 32],
              "hamming_radii": [0, 8] if smoke else [0, 4, 8, 16],
              "seeds": [17] if smoke else [17, 23, 31],
              "alpha": 1.0}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    pre_per_beta, post_kept_per_beta, post_edit_per_beta = [], [], []
    for beta in config["betas"]:
        per_seed_pre, per_seed_kept, per_seed_edit = [], [], []
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
                len(cands), generator=kept_gen)[:min(100, len(cands))]].tolist())

            # Pre-edit ECE on all facts
            pre_idx = list(range(config["M_stored"]))
            pre_ece = ece_on_subset(W, keys, v_orig, pre_idx, config["hamming_radii"],
                                       beta, cpu_gen, device)

            # Apply edits
            W_edit = W.clone()
            for i in edit_idx:
                W_edit = yb.edit_fact(W_edit, keys[i], v_new[i], config["alpha"],
                                        config["N"])

            v_after = v_orig.clone()
            for i in edit_idx:
                v_after[i] = v_new[i]

            # Post-edit ECE split by kept vs edited
            post_kept_ece = ece_on_subset(W_edit, keys, v_after, kept_idx,
                                             config["hamming_radii"], beta, cpu_gen, device)
            post_edit_ece = ece_on_subset(W_edit, keys, v_after, edit_idx,
                                             config["hamming_radii"], beta, cpu_gen, device)

            per_seed_pre.append(pre_ece)
            per_seed_kept.append(post_kept_ece)
            per_seed_edit.append(post_edit_ece)

        pre_per_beta.append(sum(per_seed_pre) / len(per_seed_pre))
        post_kept_per_beta.append(sum(per_seed_kept) / len(per_seed_kept))
        post_edit_per_beta.append(sum(per_seed_edit) / len(per_seed_edit))

    betas = config["betas"]
    pre_best = min(pre_per_beta)
    post_kept_best = min(post_kept_per_beta)
    post_edit_best = min(post_edit_per_beta)
    pre_best_beta = betas[pre_per_beta.index(pre_best)]
    summary = {"pre_ece_best": pre_best,
                "pre_ece_best_beta": pre_best_beta,
                "post_ece_kept_best": post_kept_best,
                "post_ece_edit_best": post_edit_best,
                "pre_per_beta": {b: e for b, e in zip(betas, pre_per_beta)},
                "post_kept_per_beta": {b: e for b, e in zip(betas, post_kept_per_beta)},
                "post_edit_per_beta": {b: e for b, e in zip(betas, post_edit_per_beta)}}
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
    out_dir = get_output_dir("wave14zl_calibration_after_edit_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zl_calibration_after_edit")
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
