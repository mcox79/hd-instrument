"""K6 compositional generalization — hierarchical pre-binding axis 2.

Per cap_map v190 K6 4-axis rehab list, axis 2 (hierarchical pre-binding):
test whether substrate generalizes to UNSEEN compositional combinations of
seen atomic concepts when atomic concepts are PRE-BOUND hierarchically before
being stored.

Mechanism: define atomic-concept atoms a_1, ..., a_p ∈ {-1,+1}^N.
Define K compositional concepts c_k = a_{i_k} ⊗ a_{j_k} (Hadamard product —
the canonical BSC binding op). Store M_seen of the p*(p-1) total compositions
in W; test recall on M_held held-out unseen compositions.

Hypothesis: with hierarchical pre-binding (bind atomic pair BEFORE storing),
held-out compositions should recall with cosine similarly to seen ones
(generalization signature). WITHOUT pre-binding (control: random independent
codes per composition), held-out should recall at chance level (no
generalization).

Pre-reg HARD-PASS: held-out cosine(recall, target) >= 0.50 AND
   (seen_cosine - held_cosine) <= 0.15 (small gap; compositional
   generalization SUPPORTED) — held-out matches seen within 15 pp.
   -> K6 row promoted 🔬 -> 🟢.
Pre-reg HARD-FAIL: held-out cosine <= 0.10 (chance baseline) OR
   (seen_cosine - held_cosine) >= 0.40 (large gap; NO generalization).
   -> K6 axis 2 REJECTED.
Pre-reg MIDDLE: any intermediate; report bands.

GPU-suitable: scales to N=4096 with M_seen=200 multi-seed; ~5-15 GPU-min.

Pre-reg: preregs/2026-05-24_wave14_K6_compositional_holdout_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 4096
N_SMOKE = 512
P_ATOMS_FULL = 40          # atomic concepts
P_ATOMS_SMOKE = 10
M_SEEN_FULL = 200          # seen compositions stored
M_SEEN_SMOKE = 30
M_HELD_FULL = 100          # held-out compositions tested
M_HELD_SMOKE = 20
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_HELD_COSINE = 0.50
PASS_GAP = 0.15
FAIL_HELD_COSINE = 0.10
FAIL_GAP = 0.40


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def bsc_atoms(num: int, dim: int, gen: torch.Generator, device) -> torch.Tensor:
    return (torch.randint(0, 2, (num, dim), generator=gen, device=device).float() * 2 - 1)


def run_one_seed(seed: int, N: int, p: int, M_seen: int, M_held: int, device):
    gen = torch.Generator(device=device).manual_seed(seed)
    atoms = bsc_atoms(p, N, gen, device)  # (p, N)
    # Enumerate all p*(p-1) ordered pairs as candidate compositions; pick M_seen + M_held disjoint subsets.
    pairs = [(i, j) for i in range(p) for j in range(p) if i != j]
    perm = torch.randperm(len(pairs), generator=gen, device=device).tolist()
    seen_pairs = [pairs[k] for k in perm[:M_seen]]
    held_pairs = [pairs[k] for k in perm[M_seen:M_seen + M_held]]

    # ===== Hierarchical pre-binding (treatment): c_k = a_i * a_j (Hadamard) =====
    def make_compositions(pair_list):
        keys = torch.stack([atoms[i] for (i, _) in pair_list], dim=0)
        vals = torch.stack([atoms[i] * atoms[j] for (i, j) in pair_list], dim=0)  # composition = a_i ⊗ a_j
        return keys, vals
    keys_seen, vals_seen = make_compositions(seen_pairs)  # (M_seen, N) each
    W = (keys_seen.t() @ vals_seen) / max(M_seen, 1)      # (N, N)

    # Recall on SEEN.
    rec_seen = keys_seen @ W
    num = (rec_seen * vals_seen).sum(dim=1)
    den = rec_seen.norm(dim=1) * vals_seen.norm(dim=1) + 1e-9
    cos_seen = float((num / den).mean().item())

    # Recall on HELD-OUT (atoms seen, composition pair UNSEEN).
    keys_held, vals_held = make_compositions(held_pairs)
    rec_held = keys_held @ W
    num = (rec_held * vals_held).sum(dim=1)
    den = rec_held.norm(dim=1) * vals_held.norm(dim=1) + 1e-9
    cos_held = float((num / den).mean().item())

    # ===== Control: independent random vals per composition (NO pre-binding structure) =====
    rand_vals_seen = bsc_atoms(M_seen, N, gen, device)
    W_ctrl = (keys_seen.t() @ rand_vals_seen) / max(M_seen, 1)
    rec_seen_c = keys_seen @ W_ctrl
    num_c = (rec_seen_c * rand_vals_seen).sum(dim=1)
    den_c = rec_seen_c.norm(dim=1) * rand_vals_seen.norm(dim=1) + 1e-9
    cos_seen_ctrl = float((num_c / den_c).mean().item())

    rand_vals_held = bsc_atoms(M_held, N, gen, device)
    rec_held_c = keys_held @ W_ctrl
    num_c = (rec_held_c * rand_vals_held).sum(dim=1)
    den_c = rec_held_c.norm(dim=1) * rand_vals_held.norm(dim=1) + 1e-9
    cos_held_ctrl = float((num_c / den_c).mean().item())

    return {
        "cos_seen_treatment": cos_seen,
        "cos_held_treatment": cos_held,
        "cos_seen_control": cos_seen_ctrl,
        "cos_held_control": cos_held_ctrl,
        "gap_treatment": cos_seen - cos_held,
        "M_seen": M_seen,
        "M_held": M_held,
        "p_atoms": p,
    }


def compute_verdict(summary):
    per_seed = summary.get("per_seed")
    if not per_seed:
        return ("K6_INCONCLUSIVE", "Missing per_seed data.")
    cos_held = sum(s["cos_held_treatment"] for s in per_seed.values()) / len(per_seed)
    cos_seen = sum(s["cos_seen_treatment"] for s in per_seed.values()) / len(per_seed)
    cos_held_ctrl = sum(s["cos_held_control"] for s in per_seed.values()) / len(per_seed)
    gap = cos_seen - cos_held
    pts = (f"cos_held={cos_held:.3f}, cos_seen={cos_seen:.3f}, gap={gap:.3f}, "
           f"cos_held_control={cos_held_ctrl:.3f}")
    if cos_held >= PASS_HELD_COSINE and gap <= PASS_GAP:
        return ("K6_HARD_PASS_COMPOSITIONAL_GENERALIZATION",
                f"Compositional generalization SUPPORTED: held-out cosine={cos_held:.3f} >= "
                f"{PASS_HELD_COSINE} AND gap={gap:.3f} <= {PASS_GAP}. {pts}.")
    if cos_held <= FAIL_HELD_COSINE or gap >= FAIL_GAP:
        return ("K6_HARD_FAIL_NO_GENERALIZATION",
                f"No compositional generalization: held={cos_held:.3f} <= {FAIL_HELD_COSINE} OR "
                f"gap={gap:.3f} >= {FAIL_GAP}. K6 axis 2 REJECTED. {pts}.")
    return ("K6_MIDDLE_BAND",
            f"Intermediate: held={cos_held:.3f}, gap={gap:.3f}. {pts}.")


def self_test_verdict():
    def mk(cs, ch, cs_c, ch_c):
        return {"per_seed": {"17": {"cos_seen_treatment": cs, "cos_held_treatment": ch,
                                    "cos_seen_control": cs_c, "cos_held_control": ch_c}}}
    cases = [
        (mk(0.70, 0.60, 0.60, 0.05), "K6_HARD_PASS_COMPOSITIONAL_GENERALIZATION"),
        (mk(0.70, 0.05, 0.60, 0.04), "K6_HARD_FAIL_NO_GENERALIZATION"),
        (mk(0.70, 0.30, 0.60, 0.05), "K6_MIDDLE_BAND"),
        ({}, "K6_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    p = P_ATOMS_SMOKE if smoke else P_ATOMS_FULL
    M_seen = M_SEEN_SMOKE if smoke else M_SEEN_FULL
    M_held = M_HELD_SMOKE if smoke else M_HELD_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "p_atoms": p,
        "M_seen": M_seen,
        "M_held": M_held,
        "seeds": seeds,
        "device": str(device),
        "pass_held_cosine": PASS_HELD_COSINE,
        "pass_gap": PASS_GAP,
        "fail_held_cosine": FAIL_HELD_COSINE,
        "fail_gap": FAIL_GAP,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, N, p, M_seen, M_held, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: cos_held={r['cos_held_treatment']:.3f} gap={r['gap_treatment']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14_K6_compositional_holdout_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_K6_compositional_holdout_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
