"""Continual editing stress test: 30 sequential edits, Kerdock vs correlated.

wave14yb showed ONE-SHOT edit-then-query works for both arms. This tests
the PRODUCTION-SCALE question: does the substrate hold up under 30
sequential edits? At each step, after editing one fact, we query ALL
facts and measure edited_acc + kept_acc.

The hypothesis: Kerdock structure protects against accumulated drift
across sequential edits, where correlated keys do not.

Pre-reg: preregs/2026-05-21_wave14yc_continual_editing_kerdock.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
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

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
M_STORED_FULL = 4096
M_STORED_SMOKE = 512
N_EDITS_FULL = 30
N_EDITS_SMOKE = 5
SEEDS_FULL = [17, 23, 31, 41, 53]
SEEDS_SMOKE = [17]
ALPHA = 1.0

PASS_EDITED = 0.95
PASS_KEPT = 0.95
KILL_EDIT_COUNT = 10  # both arms must fail by this edit count for KILL


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def edit_fact(W, k, v_new, alpha, N):
    Wk = W @ k
    k_norm_sq = float((k * k).sum())
    W = W - alpha * torch.outer(Wk, k) / k_norm_sq
    W = W + torch.outer(v_new, k) / N
    return W


def arm_passes(arm_data: dict) -> tuple[bool, list[str]]:
    fails = []
    if arm_data["min_edited_acc"] < PASS_EDITED:
        fails.append(f"min_edited_acc={arm_data['min_edited_acc']:.3f}<{PASS_EDITED}")
    if arm_data["min_kept_acc"] < PASS_KEPT:
        fails.append(f"min_kept_acc={arm_data['min_kept_acc']:.3f}<{PASS_KEPT}")
    return (len(fails) == 0, fails)


def first_fail_edit(per_edit_trajectory: list[dict], key: str, threshold: float) -> int | None:
    """Return the smallest edit step at which `key` drops below threshold (or None)."""
    for entry in per_edit_trajectory:
        if entry[key] < threshold:
            return entry["edit_step"]
    return None


def compute_verdict(summary: dict) -> tuple[str, str]:
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms or "correlated" not in arms:
        return ("CONTINUAL_INCONCLUSIVE", "Missing per-arm data.")
    kerdock = arms["kerdock"]
    correlated = arms["correlated"]
    if not kerdock.get("per_edit_trajectory") or not correlated.get("per_edit_trajectory"):
        return ("CONTINUAL_INCONCLUSIVE", "Missing trajectories.")

    k_ok, k_fails = arm_passes(kerdock)
    c_ok, c_fails = arm_passes(correlated)

    # Kill: both arms fail by KILL_EDIT_COUNT
    k_fail_edit = first_fail_edit(kerdock["per_edit_trajectory"], "edited_acc", PASS_EDITED)
    if k_fail_edit is None:
        k_fail_edit = first_fail_edit(kerdock["per_edit_trajectory"], "kept_acc", PASS_KEPT)
    c_fail_edit = first_fail_edit(correlated["per_edit_trajectory"], "edited_acc", PASS_EDITED)
    if c_fail_edit is None:
        c_fail_edit = first_fail_edit(correlated["per_edit_trajectory"], "kept_acc", PASS_KEPT)

    if (k_fail_edit is not None and k_fail_edit <= KILL_EDIT_COUNT and
        c_fail_edit is not None and c_fail_edit <= KILL_EDIT_COUNT):
        return ("CONTINUAL_BOTH_FAIL_FAST",
                f"Both arms fail by edit {KILL_EDIT_COUNT}: Kerdock at edit {k_fail_edit}, "
                f"correlated at edit {c_fail_edit}. Continual editing is fundamentally "
                f"broken in this regime; mechanism issue beyond key structure.")

    if k_ok and c_ok:
        return ("CONTINUAL_BOTH_HOLD",
                f"Both arms hold across all 30 edits. Kerdock min_edited="
                f"{kerdock['min_edited_acc']:.3f}, min_kept={kerdock['min_kept_acc']:.3f}; "
                f"correlated min_edited={correlated['min_edited_acc']:.3f}, "
                f"min_kept={correlated['min_kept_acc']:.3f}. 30 edits may not be "
                f"sufficient load; stress-extend in v2 (100+ edits).")

    if k_ok and not c_ok:
        c_fail_step = c_fail_edit
        return ("CONTINUAL_KERDOCK_HOLDS",
                f"Kerdock arm holds across all 30 edits: min_edited="
                f"{kerdock['min_edited_acc']:.3f}, min_kept={kerdock['min_kept_acc']:.3f}. "
                f"Correlated arm fails at edit {c_fail_step}: "
                f"{'; '.join(c_fails)}. Structured keys are load-bearing for "
                f"continual editing.")

    if not k_ok and c_ok:
        return ("CONTINUAL_KERDOCK_DRIFTS",
                f"Unexpected: Kerdock arm fails at edit {k_fail_edit}: "
                f"{'; '.join(k_fails)}, but correlated arm holds: "
                f"min_edited={correlated['min_edited_acc']:.3f}, "
                f"min_kept={correlated['min_kept_acc']:.3f}. Audit construction.")

    # Both fail but not within KILL window
    # Identify which arm fails which probe
    k_edited_step = first_fail_edit(kerdock["per_edit_trajectory"], "edited_acc", PASS_EDITED)
    k_kept_step = first_fail_edit(kerdock["per_edit_trajectory"], "kept_acc", PASS_KEPT)
    if k_edited_step is not None:
        return (f"CONTINUAL_KERDOCK_EDITED_CLIFF_AT_{k_edited_step}",
                f"Kerdock edited_acc drops below {PASS_EDITED} at edit step "
                f"{k_edited_step}. Continual edits accumulate drift even with "
                f"structured keys.")
    if k_kept_step is not None:
        return (f"CONTINUAL_KERDOCK_KEPT_CLIFF_AT_{k_kept_step}",
                f"Kerdock kept_acc drops below {PASS_KEPT} at edit step "
                f"{k_kept_step}. Side effects on unedited facts accumulate.")
    return ("CONTINUAL_INCONCLUSIVE",
            f"Couldn't classify: kerdock_fails={k_fails}, corr_fails={c_fails}")


def self_test_verdict() -> None:
    def mk_arm(min_edited, min_kept, fail_edited_step=None, fail_kept_step=None,
                 n_edits=30):
        traj = []
        for i in range(1, n_edits + 1):
            e = 1.0 if (fail_edited_step is None or i < fail_edited_step) else 0.5
            k = 1.0 if (fail_kept_step is None or i < fail_kept_step) else 0.5
            traj.append({"edit_step": i, "edited_acc": e, "kept_acc": k})
        return {"min_edited_acc": min_edited, "min_kept_acc": min_kept,
                "per_edit_trajectory": traj}

    cases = [
        # 1. KERDOCK_HOLDS: kerdock min>=0.95, correlated drops at edit 15
        ({"by_arm": {
            "kerdock": mk_arm(0.98, 0.99),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=15)}},
         "CONTINUAL_KERDOCK_HOLDS"),
        # 2. BOTH_HOLD
        ({"by_arm": {
            "kerdock": mk_arm(0.98, 0.99),
            "correlated": mk_arm(0.97, 0.98)}},
         "CONTINUAL_BOTH_HOLD"),
        # 3. BOTH_FAIL_FAST: both fail by edit 10
        ({"by_arm": {
            "kerdock": mk_arm(0.50, 0.99, fail_edited_step=5),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=6)}},
         "CONTINUAL_BOTH_FAIL_FAST"),
        # 4. KERDOCK_DRIFTS: kerdock fails, correlated holds
        ({"by_arm": {
            "kerdock": mk_arm(0.50, 0.99, fail_edited_step=20),
            "correlated": mk_arm(0.98, 0.99)}},
         "CONTINUAL_KERDOCK_DRIFTS"),
        # 5. EDITED_CLIFF_AT: kerdock drops at edit 18, correlated also drops at 15
        ({"by_arm": {
            "kerdock": mk_arm(0.50, 0.99, fail_edited_step=18),
            "correlated": mk_arm(0.50, 0.99, fail_edited_step=15)}},
         "CONTINUAL_KERDOCK_EDITED_CLIFF_AT_18"),
        # 6. INCONCLUSIVE
        ({}, "CONTINUAL_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_arm(arm_name: str, codebook: torch.Tensor | None, config: dict,
             device: torch.device) -> dict:
    N = config["N"]
    M = config["M_stored"]
    n_edits = config["n_edits"]
    seeds = config["seeds"]

    per_seed_trajectories = []
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
        v_after = v_orig.clone()

        edit_gen = torch.Generator().manual_seed(seed * 31 + 7)
        edit_idx_order = torch.randperm(M, generator=edit_gen)[:n_edits].tolist()
        edited_set = set()

        traj = []
        for step, i in enumerate(edit_idx_order, start=1):
            W = edit_fact(W, keys[i], v_new_pool[i], ALPHA, N)
            v_after[i] = v_new_pool[i]
            edited_set.add(i)

            # Query ALL M facts; compute edited_acc and kept_acc
            retrieved = keys @ W.T  # (M, N)
            sims = retrieved @ v_after.T  # (M, M)
            argmax = sims.argmax(dim=1)  # (M,) per-fact predicted index
            target = torch.arange(M, device=device)
            correct = (argmax == target)

            edited_list = list(edited_set)
            kept_list = [j for j in range(M) if j not in edited_set]
            edited_acc = float(correct[edited_list].float().mean()) if edited_list else 1.0
            kept_acc = float(correct[kept_list].float().mean()) if kept_list else 1.0
            traj.append({"edit_step": step, "edited_acc": edited_acc, "kept_acc": kept_acc})

        per_seed_trajectories.append(traj)

    # Aggregate across seeds: average each (edit_step, metric)
    n_edits = len(per_seed_trajectories[0])
    agg_traj = []
    for step_idx in range(n_edits):
        edited = sum(t[step_idx]["edited_acc"] for t in per_seed_trajectories) / len(per_seed_trajectories)
        kept = sum(t[step_idx]["kept_acc"] for t in per_seed_trajectories) / len(per_seed_trajectories)
        agg_traj.append({"edit_step": step_idx + 1, "edited_acc": edited, "kept_acc": kept})

    return {
        "per_edit_trajectory": agg_traj,
        "min_edited_acc": min(e["edited_acc"] for e in agg_traj),
        "min_kept_acc": min(e["kept_acc"] for e in agg_traj),
        "per_seed_trajectories": per_seed_trajectories,
    }


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_stored": M_STORED_SMOKE if smoke else M_STORED_FULL,
        "n_edits": N_EDITS_SMOKE if smoke else N_EDITS_FULL,
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

    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= TRAJECTORIES =========", flush=True)
    for arm_name, arm in summary["by_arm"].items():
        print(f"[{arm_name}]  min_edited={arm['min_edited_acc']:.3f}  "
              f"min_kept={arm['min_kept_acc']:.3f}", flush=True)
        # Print every 5th edit
        for entry in arm["per_edit_trajectory"][::5]:
            print(f"  step={entry['edit_step']:3d}  edited={entry['edited_acc']:.3f}  "
                  f"kept={entry['kept_acc']:.3f}", flush=True)

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
    out_dir = get_output_dir("wave14yc_continual_editing_kerdock_smoke")
    log_event("experiment_started", name="wave14yc_continual_editing_kerdock", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle 1: pre-edit-like accuracy at step 1 should be high on both arms
    # (after just 1 edit, the substrate is nearly clean)
    for arm_name in ["kerdock", "correlated"]:
        first_step = summary["by_arm"][arm_name]["per_edit_trajectory"][0]
        oracle.assert_baseline_high(f"{arm_name}_step1_edited_acc",
                                       first_step["edited_acc"], 0.70)

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yc_continual_editing_kerdock",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yc_continual_editing_kerdock")
    log_event("experiment_started", name="wave14yc_continual_editing_kerdock", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yc_continual_editing_kerdock",
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
