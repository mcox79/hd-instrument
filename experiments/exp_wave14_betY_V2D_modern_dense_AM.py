"""End-to-end edit-then-query test with Kerdock vs correlated keys.

Composes Bet 2's validated erase primitive with an insert step to test
the full product capability: store -> edit -> query -> return new value.

Two arms:
  Kerdock: 4-coset MM codebook (from v3); paraphrase queries use snap
  Correlated: rank-L correlated keys (matches v1-v4 control)

Pipeline per fact i to be edited:
  W = W - alpha * outer(W @ k_i, k_i) / (k_i . k_i)   # anti-Hebbian erase
  W = W + outer(v_new_i, k_i) / N                       # insert new value

After all edits, query each fact (subj * rel = k_i) and check argmax over
the COMBINED value codebook (v_new for edited, v_orig for kept) returns
the expected value. Paraphrase robustness via Hamming perturb + snap.

Pre-reg: preregs/2026-05-21_wave14yb_edit_then_query_kerdock.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


_v1_path = REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py"
spec1 = importlib.util.spec_from_file_location("orthkeys_v1", _v1_path)
v1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(v1)

_v2_path = REPO / "experiments" / "exp_wave14v_erase_kerdock_v2.py"
spec2 = importlib.util.spec_from_file_location("kerdock_v2", _v2_path)
v2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(v2)

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 4096
M_STORED_SMOKE = 512
N_EDIT_FULL = 30
N_EDIT_SMOKE = 5
N_KEPT_PROBE_FULL = 100
N_KEPT_PROBE_SMOKE = 20
HAMMING_RADII_FULL = [4, 8, 16]
HAMMING_RADII_SMOKE = [8]
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_EDIT_ARGMAX = 0.95
PASS_KEPT_ARGMAX = 0.95
PASS_EDIT_PARAPHRASE = 0.90
PASS_KEPT_PARAPHRASE = 0.95
PASS_SIDE_EFFECT_MAX = 0.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def edit_fact(W: torch.Tensor, k: torch.Tensor, v_new: torch.Tensor,
                alpha: float, N: int) -> torch.Tensor:
    """In-place style edit: erase via anti-Hebbian, then insert v_new at the same k.
    Returns updated W (not in-place; caller assigns)."""
    Wk = W @ k
    k_norm_sq = float((k * k).sum())
    W = W - alpha * torch.outer(Wk, k) / k_norm_sq
    W = W + torch.outer(v_new, k) / N
    return W


def cell_passes_per_seed(row: dict) -> tuple[bool, list[str]]:
    fails = []
    if row["edit_argmax_acc"] < PASS_EDIT_ARGMAX:
        fails.append(f"edit_argmax={row['edit_argmax_acc']:.3f}<{PASS_EDIT_ARGMAX}")
    if row["kept_argmax_acc"] < PASS_KEPT_ARGMAX:
        fails.append(f"kept_argmax={row['kept_argmax_acc']:.3f}<{PASS_KEPT_ARGMAX}")
    para_e = row.get("edit_paraphrase_acc_h8", 0.0)
    if para_e < PASS_EDIT_PARAPHRASE:
        fails.append(f"edit_para_h8={para_e:.3f}<{PASS_EDIT_PARAPHRASE}")
    para_k = row.get("kept_paraphrase_acc_h8", 0.0)
    if para_k < PASS_KEPT_PARAPHRASE:
        fails.append(f"kept_para_h8={para_k:.3f}<{PASS_KEPT_PARAPHRASE}")
    if row.get("side_effect_rate", 0.0) > PASS_SIDE_EFFECT_MAX:
        fails.append(f"side_effect={row['side_effect_rate']:.3f}>{PASS_SIDE_EFFECT_MAX}")
    return (len(fails) == 0, fails)


def compute_verdict(summary: dict) -> tuple[str, str]:
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("EDIT_QUERY_INCONCLUSIVE", "Missing per-arm data.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    if not kerdock or not correlated:
        return ("EDIT_QUERY_INCONCLUSIVE", "Empty arm row.")

    kerdock_ok, kerdock_fails = cell_passes_per_seed(kerdock)
    corr_ok, corr_fails = cell_passes_per_seed(correlated)

    # Sub-failures for Kerdock
    edits_ok = kerdock["edit_argmax_acc"] >= PASS_EDIT_ARGMAX
    kept_ok = kerdock["kept_argmax_acc"] >= PASS_KEPT_ARGMAX
    para_ok = (kerdock.get("edit_paraphrase_acc_h8", 0.0) >= PASS_EDIT_PARAPHRASE
                and kerdock.get("kept_paraphrase_acc_h8", 0.0) >= PASS_KEPT_PARAPHRASE)
    side_ok = kerdock.get("side_effect_rate", 0.0) <= PASS_SIDE_EFFECT_MAX

    # Kill criterion
    if not edits_ok and not (correlated["edit_argmax_acc"] >= PASS_EDIT_ARGMAX):
        return ("EDIT_QUERY_BOTH_BROKEN",
                f"Both arms fail edit_argmax_acc. Kerdock={kerdock['edit_argmax_acc']:.3f}, "
                f"correlated={correlated['edit_argmax_acc']:.3f}. Edit-then-query doesn't "
                f"work; mechanism issue beyond key structure.")

    if kerdock_ok and corr_ok:
        return ("EDIT_QUERY_BOTH_PASS",
                f"Both arms pass edit-then-query. Kerdock edit={kerdock['edit_argmax_acc']:.3f}, "
                f"correlated edit={correlated['edit_argmax_acc']:.3f}. "
                f"wave14d_query_side_integration's 93% leak doesn't reproduce here; "
                f"audit setup divergence.")

    if kerdock_ok and not corr_ok:
        return ("EDIT_QUERY_KERDOCK_PASS",
                f"Kerdock arm passes all 5 criteria. edit_argmax={kerdock['edit_argmax_acc']:.3f}, "
                f"kept_argmax={kerdock['kept_argmax_acc']:.3f}, "
                f"edit_paraphrase_h8={kerdock.get('edit_paraphrase_acc_h8', 0.0):.3f}, "
                f"kept_paraphrase_h8={kerdock.get('kept_paraphrase_acc_h8', 0.0):.3f}, "
                f"side_effect={kerdock.get('side_effect_rate', 0.0):.3f}. "
                f"Correlated arm fails with: {'; '.join(corr_fails)}. "
                f"Bet 2's Kerdock wins translate to product-grade edit-then-query.")

    # Kerdock not fully passing - identify which criterion
    if edits_ok and kept_ok and not para_ok:
        return ("EDIT_QUERY_KERDOCK_PARAPHRASE_FAIL",
                f"Kerdock arm passes edit/kept argmax but paraphrase under snap fails. "
                f"edit_para_h8={kerdock.get('edit_paraphrase_acc_h8', 0.0):.3f}, "
                f"kept_para_h8={kerdock.get('kept_paraphrase_acc_h8', 0.0):.3f}. "
                f"Snap-to-codebook is partially failing for perturbed queries.")
    if edits_ok and kept_ok and para_ok and not side_ok:
        return ("EDIT_QUERY_KERDOCK_SIDE_EFFECTS",
                f"Kerdock arm passes 4 of 5 but side_effect_rate="
                f"{kerdock.get('side_effect_rate', 0.0):.3f} > {PASS_SIDE_EFFECT_MAX}. "
                f"Edits leak into kept facts.")

    return ("EDIT_QUERY_INCONCLUSIVE",
            f"Kerdock arm fails: {'; '.join(kerdock_fails)}. "
            f"Correlated arm: {'; '.join(corr_fails) if corr_fails else 'passes'}. "
            f"Pattern doesn't match a clean verdict label.")


def self_test_verdict() -> None:
    def mk(args):
        return {"edit_argmax_acc": args.get("edit_argmax", 0.99),
                "kept_argmax_acc": args.get("kept_argmax", 0.99),
                "edit_paraphrase_acc_h8": args.get("edit_para", 0.96),
                "kept_paraphrase_acc_h8": args.get("kept_para", 0.98),
                "side_effect_rate": args.get("side", 0.01)}

    cases = [
        # 1. KERDOCK_PASS: kerdock all pass, correlated fails edit
        ({"by_arm": {"kerdock": mk({}),
                       "correlated": mk({"edit_argmax": 0.30, "kept_argmax": 0.50})}},
         "EDIT_QUERY_KERDOCK_PASS"),
        # 2. BOTH_PASS: both arms pass
        ({"by_arm": {"kerdock": mk({}), "correlated": mk({})}},
         "EDIT_QUERY_BOTH_PASS"),
        # 3. BOTH_BROKEN: kill
        ({"by_arm": {"kerdock": mk({"edit_argmax": 0.40}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_BOTH_BROKEN"),
        # 4. PARAPHRASE_FAIL: kerdock argmax + kept pass but paraphrase fails
        ({"by_arm": {"kerdock": mk({"edit_para": 0.50}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_KERDOCK_PARAPHRASE_FAIL"),
        # 5. SIDE_EFFECTS: passes other criteria but side effects high
        ({"by_arm": {"kerdock": mk({"side": 0.15}),
                       "correlated": mk({"edit_argmax": 0.30})}},
         "EDIT_QUERY_KERDOCK_SIDE_EFFECTS"),
        # 6. INCONCLUSIVE: missing
        ({}, "EDIT_QUERY_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_arm(arm_name: str, codebook: torch.Tensor | None, config: dict,
             device: torch.device) -> dict:
    """Run edit-then-query for one arm, aggregate across seeds."""
    N = config["N"]
    M = config["M_stored"]
    n_edit = config["n_edit"]
    n_kept = config["n_kept"]
    hamming = config["hamming_radii"]
    seeds = config["seeds"]

    per_seed_metrics = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)

        if codebook is not None:
            keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
        else:
            rank_L = max(2, int(M * 0.25))
            keys = v1.make_correlated_keys(M, N, rank_L, gen, device)

        v_orig = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        v_new_pool = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (v_orig.T @ keys) / N

        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        kept_gen = torch.Generator().manual_seed(seed * 31 + 11)
        edit_idx = sorted(torch.randperm(M, generator=edit_gen)[:n_edit].tolist())
        edit_set = set(edit_idx)
        candidates = [i for i in range(M) if i not in edit_set]
        n_kept_actual = min(n_kept, len(candidates))
        kept_idx = sorted(torch.tensor(candidates)[torch.randperm(
            len(candidates), generator=kept_gen)[:n_kept_actual]].tolist())

        # Pre-edit kept retrieval (for side-effect baseline)
        pre_retrieved = keys[kept_idx] @ W.T  # (n_kept, N)
        pre_sims = pre_retrieved @ v_orig.T  # (n_kept, M)
        pre_argmax = pre_sims.argmax(dim=1)  # (n_kept,) - should be kept_idx for sanity

        # Apply edits
        W_edit = W.clone()
        for i in edit_idx:
            W_edit = edit_fact(W_edit, keys[i], v_new_pool[i], ALPHA, N)

        # Build combined value codebook: v_orig for kept, v_new for edited
        v_after = v_orig.clone()
        for i in edit_idx:
            v_after[i] = v_new_pool[i]

        # Query edited facts (exact)
        edit_keys_t = keys[edit_idx]
        edit_retrieved = edit_keys_t @ W_edit.T
        edit_sims = edit_retrieved @ v_after.T
        edit_argmax = edit_sims.argmax(dim=1)
        edit_target = torch.tensor(edit_idx, device=device)
        edit_argmax_acc = float((edit_argmax == edit_target).float().mean())

        # Query kept facts (exact)
        kept_keys_t = keys[kept_idx]
        kept_retrieved = kept_keys_t @ W_edit.T
        kept_sims = kept_retrieved @ v_after.T
        kept_argmax = kept_sims.argmax(dim=1)
        kept_target = torch.tensor(kept_idx, device=device)
        kept_argmax_acc = float((kept_argmax == kept_target).float().mean())

        # Side-effect: how many kept facts changed argmax vs pre-edit?
        side_changes = (kept_argmax != pre_argmax).float().mean().item()
        # Pre-edit baseline: kept_argmax should equal kept_target (idx) on a healthy substrate
        # so pre_argmax == kept_target. Side effect = (post_argmax != pre_argmax) - which is
        # essentially (post_argmax != kept_target) for an unbroken pre-edit baseline.
        # Use simpler def: side effect = (kept_argmax shifted off its target due to edits) =
        # fraction of kept facts where post-edit prediction is wrong but pre-edit was right.
        pre_correct = (pre_argmax == kept_target)
        post_wrong = (kept_argmax != kept_target)
        side_effect_rate = float((pre_correct & post_wrong).float().mean())

        # Paraphrase queries: Hamming-perturb keys for edited and kept; snap (Kerdock arm only)
        per_hamming = {}
        for h in hamming:
            # Edit-side paraphrase
            edit_para = v1.hamming_perturb(edit_keys_t, 1, h, cpu_gen, device)
            if codebook is not None:
                edit_para = v2.snap_to_codebook_batch(edit_para, codebook)
            edit_para_ret = edit_para @ W_edit.T
            edit_para_sims = edit_para_ret @ v_after.T
            edit_para_argmax = edit_para_sims.argmax(dim=1)
            edit_para_acc = float((edit_para_argmax == edit_target).float().mean())

            # Kept-side paraphrase
            kept_para = v1.hamming_perturb(kept_keys_t, 1, h, cpu_gen, device)
            if codebook is not None:
                kept_para = v2.snap_to_codebook_batch(kept_para, codebook)
            kept_para_ret = kept_para @ W_edit.T
            kept_para_sims = kept_para_ret @ v_after.T
            kept_para_argmax = kept_para_sims.argmax(dim=1)
            kept_para_acc = float((kept_para_argmax == kept_target).float().mean())

            per_hamming[h] = {"edit_para_acc": edit_para_acc,
                                "kept_para_acc": kept_para_acc}

        per_seed_metrics.append({
            "seed": seed,
            "edit_argmax_acc": edit_argmax_acc,
            "kept_argmax_acc": kept_argmax_acc,
            "side_effect_rate": side_effect_rate,
            "per_hamming": per_hamming,
        })

    # Aggregate across seeds
    def avg(key, source=None):
        if source is None:
            source = per_seed_metrics
        vals = [r[key] for r in source if key in r]
        return sum(vals) / len(vals) if vals else 0.0

    out = {
        "edit_argmax_acc": avg("edit_argmax_acc"),
        "kept_argmax_acc": avg("kept_argmax_acc"),
        "side_effect_rate": avg("side_effect_rate"),
        "per_seed": per_seed_metrics,
    }
    for h in hamming:
        e_vals = [r["per_hamming"][h]["edit_para_acc"] for r in per_seed_metrics]
        k_vals = [r["per_hamming"][h]["kept_para_acc"] for r in per_seed_metrics]
        out[f"edit_paraphrase_acc_h{h}"] = sum(e_vals) / len(e_vals)
        out[f"kept_paraphrase_acc_h{h}"] = sum(k_vals) / len(k_vals)

    return out


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_edit": N_EDIT_SMOKE if smoke else N_EDIT_FULL,
        "n_kept": N_KEPT_PROBE_SMOKE if smoke else N_KEPT_PROBE_FULL,
        "hamming_radii": HAMMING_RADII_SMOKE if smoke else HAMMING_RADII_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "alpha": ALPHA,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    print(f"[codebook] building 4-coset MM codebook at N={config['N']}...", flush=True)
    codebook, info = v3.make_kerdock_4coset_codebook(config["N"], device)
    print(f"[codebook] {info}", flush=True)

    print(f"[arm=kerdock] running...", flush=True)
    arm_k = run_arm("kerdock", codebook, config, device)
    print(f"[arm=correlated] running...", flush=True)
    arm_c = run_arm("correlated", None, config, device)

    summary = {
        "N": config["N"],
        "by_arm": {"kerdock": arm_k, "correlated": arm_c},
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ARM COMPARISON =========", flush=True)
    for arm_name, arm in summary["by_arm"].items():
        paras = " ".join(f"e_h{h}={arm[f'edit_paraphrase_acc_h{h}']:.3f}"
                          f" k_h{h}={arm[f'kept_paraphrase_acc_h{h}']:.3f}"
                          for h in config["hamming_radii"])
        print(f"  [{arm_name}]  edit_argmax={arm['edit_argmax_acc']:.3f}  "
              f"kept_argmax={arm['kept_argmax_acc']:.3f}  "
              f"side_effect={arm['side_effect_rate']:.3f}  {paras}", flush=True)

    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14yb_edit_then_query_kerdock_smoke")
    log_event("experiment_started", name="wave14yb_edit_then_query_kerdock", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle: on the Kerdock arm at smoke scale, kept_argmax should be high
    # (this is the strongest sanity check - if kept retrieval is broken
    # even pre-edit, the test is invalid)
    k_kept = summary["by_arm"]["kerdock"]["kept_argmax_acc"]
    oracle.assert_baseline_high("kerdock_kept_argmax_smoke", k_kept, 0.70)

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yb_edit_then_query_kerdock",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yb_edit_then_query_kerdock")
    log_event("experiment_started", name="wave14yb_edit_then_query_kerdock", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yb_edit_then_query_kerdock",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
