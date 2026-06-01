"""KF-2 EDIT-WITH-IMPACT-PREDICTION: CPU scoping probe at N=1024.

CONTEXT (Killer Feature 2):
  exp_kf2_edit_impact_v1.py targets GPU (N=4096, Kerdock, matrix ops).
  This CPU version runs the same experiment at N=1024 (CPU-feasible Kerdock),
  providing a design-space scan and confirming the Pearson-r measurement works
  before GPU FULL.

  QUESTION: Can we predict which other facts shift when one is edited, based on
  key-similarity structure? Uses lR-phase basin-boundary model: collateral damage
  ~ key-cosine-similarity to edited fact.

DESIGN:
  - N=1024 Kerdock 4-coset codebook.
  - M_fracs = [0.5, 1.0, 2.0, 4.0] * N.
  - 3 seeds, 5 edits each, probe 100 other facts.
  - Primary metric: Pearson r(predicted_impact, actual_delta_argmax).

PRE-REGISTERED BANDS (CPU scoping; CPU calibrates GPU FULL):
  Same pre-reg as kf2_edit_impact_v1.md (same hypothesis, smaller N).
  HARD_PASS: mean Pearson r > 0.20 in >= 2/3 seeds.
  HARD_FAIL: r < 0.0 in all seeds.
  MIDDLE_BAND: 0.0 <= r <= 0.20.

  Prior anchor: kf2_edit_impact_v1 is the GPU version (not yet run).
  This is the first empirical measurement -> calibration probe, bands +-50%.
  Theory: lR-phase model predicts r > 0. If confirmed at N=1024, submit kf2_edit_impact_v1
  to GPU queue with confidence.

FORMULA SELF-TESTS:
  1. Pearson r of [1,2,3,4,5] vs [2,4,6,8,10] = 1.0.
  2. Pearson r of [1,2,3] vs [3,2,1] = -1.0.
  3. Pearson r with constant y = 0.
  4. For orthogonal keys (Kerdock): editing fact i should cause 0 or near-0
     collateral, regardless of key similarity. Expected r~0 but not negative.

TIMEOUT ESTIMATE:
  N=1024, C=4096 codebook, M_fracs=[0.5,1,2,4], 3 seeds, 5 edits, 100 probe facts.
  Per cell: M keys x 100 probes x C=4096 codebook argmax = M*100*4096 ops.
  At M=4096: 4096*100*4096 = 1.6e9 ops per cell. 5 edits * 3 seeds = 15 cells per M.
  Rough: 15s per M level * 4 = 60s total.
  smoke: 1 seed, 2 M values, 3 edits. ~5s.
  timeout_s = ceil(1.5 * 5 * (3*4/2)*(5/3)) = ceil(1.5*5*6*1.67) = ceil(75) = 300s.
  Safety: 600s.

N-suffix: no _nN suffix; production N = 1024 (PROT-018: CPU scoping probe).
Queue: remote_cpu_queue (CPU; N=1024 Kerdock; KF-2 design-space scan)
Pre-reg: preregs/2026-05-27_kf2_cpu_v1.md
Parent: kf2_edit_impact_v1 (GPU N=4096; this CPU version scopes before GPU FULL)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)

# PRODUCTION CONFIG
N = 1024           # PROT-018: production N = 1024 (CPU scoping probe)
M_FRACS_FULL = [0.5, 1.0, 2.0, 4.0]
M_FRACS_SMOKE = [1.0, 2.0]
N_EDITS_FULL = 5
N_EDITS_SMOKE = 3
N_EVAL_FULL = 100
N_EVAL_SMOKE = 50
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_PEARSON_R = 0.20
FAIL_PEARSON_R = 0.0


def get_output_dir(default_name: str = "kf2_cpu_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pearson_r(x: torch.Tensor, y: torch.Tensor) -> float:
    """Pearson correlation coefficient."""
    if x.std() < 1e-10 or y.std() < 1e-10:
        return 0.0
    xm = x - x.mean()
    ym = y - y.mean()
    denom = float((xm.norm() * ym.norm()).item())
    if denom < 1e-10:
        return 0.0
    return float((xm * ym).sum().item() / denom)


def build_w(codebook: torch.Tensor, M: int, seed: int, N: int) -> tuple:
    C = codebook.shape[0]
    import math
    gen = torch.Generator().manual_seed(seed)
    parts_k, parts_v = [], []
    remaining = M
    while remaining > 0:
        take = min(remaining, C)
        parts_k.append(torch.randperm(C, generator=gen)[:take])
        parts_v.append(torch.randperm(C, generator=gen)[:take])
        remaining -= take
    key_idx = torch.cat(parts_k)[:M]
    val_idx = torch.cat(parts_v)[:M]
    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]
    W = torch.zeros(N, N, dtype=torch.float32)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = values[start:start + 256]
        W += (v_b.T @ k_b) / N
    return W, keys, values, key_idx, val_idx


def edit_fact(W: torch.Tensor, key: torch.Tensor, val_old: torch.Tensor,
               val_new: torch.Tensor, N: int) -> torch.Tensor:
    kk = float((key * key).sum().item())
    if kk < 1e-10:
        return W
    W = W - torch.outer(W @ key, key) / kk
    W = W + torch.outer(val_new, key) / N
    return W


def measure_impact(W_before: torch.Tensor, W_after: torch.Tensor,
                    probe_keys: torch.Tensor, codebook: torch.Tensor, N: int) -> torch.Tensor:
    """For each probe key, measure 0/1 argmax change after edit."""
    sims_before = (codebook @ (probe_keys @ W_before.T).T) / N   # (C, n)
    sims_after = (codebook @ (probe_keys @ W_after.T).T) / N
    pred_before = torch.argmax(sims_before, dim=0)
    pred_after = torch.argmax(sims_after, dim=0)
    return (pred_before != pred_after).float()


def run_one_cell(M: int, seed: int, codebook: torch.Tensor, N: int,
                  n_edits: int, n_eval: int) -> Dict:
    C = codebook.shape[0]
    W, keys, values, key_idx, val_idx = build_w(codebook, M, seed, N)
    gen = torch.Generator().manual_seed(seed + 50000)
    new_val_perm = torch.randperm(C, generator=gen)[:M]
    values_new = codebook[new_val_perm[:M] % C]

    pearson_rs = []
    mean_delta_accs = []
    n_probe = min(n_eval, M)

    for edit_i in range(min(n_edits, M)):
        W_after = edit_fact(W, keys[edit_i], values[edit_i], values_new[edit_i], N)

        probe_start = max(0, edit_i - n_probe // 2)
        probe_end = min(M, probe_start + n_probe)
        probe_indices = [j for j in range(probe_start, probe_end) if j != edit_i]
        if not probe_indices:
            continue
        probe_keys = keys[torch.tensor(probe_indices)]

        impact_actual = measure_impact(W, W_after, probe_keys, codebook, N)
        edited_key = keys[edit_i]
        edited_key_norm = edited_key.norm().clamp(min=1e-10)
        probe_norms = probe_keys.norm(dim=1).clamp(min=1e-10)
        cos_sims = (probe_keys @ edited_key) / (probe_norms * edited_key_norm)
        predicted_impact = cos_sims.abs()

        r = pearson_r(predicted_impact, impact_actual)
        pearson_rs.append(r)
        mean_delta_accs.append(float(impact_actual.mean().item()))

    mean_r = sum(pearson_rs) / len(pearson_rs) if pearson_rs else 0.0
    mean_delta = sum(mean_delta_accs) / len(mean_delta_accs) if mean_delta_accs else 0.0

    return {
        "M": M, "M_over_N": M / N, "seed": seed,
        "mean_pearson_r": mean_r,
        "mean_delta_acc": mean_delta,
        "n_edits_run": len(pearson_rs),
    }


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_CPU_INCONCLUSIVE", "No cells.")
    pearson_rs = [c["mean_pearson_r"] for c in cells if c.get("n_edits_run", 0) > 0]
    if not pearson_rs:
        return ("KF2_CPU_INCONCLUSIVE", "No valid cells.")
    seeds_seen = list(set(c["seed"] for c in cells))
    seed_mean_r = {}
    for s in seeds_seen:
        rs = [c["mean_pearson_r"] for c in cells if c["seed"] == s
              and c.get("n_edits_run", 0) > 0]
        seed_mean_r[s] = sum(rs) / len(rs) if rs else 0.0
    n_seeds = len(seed_mean_r)
    seeds_pass = sum(1 for r in seed_mean_r.values() if r >= PASS_PEARSON_R)
    mean_r_all = sum(pearson_rs) / len(pearson_rs)
    max_r = max(pearson_rs)
    mean_delta = sum(c["mean_delta_acc"] for c in cells) / len(cells)

    if all(r < FAIL_PEARSON_R for r in seed_mean_r.values()):
        return ("KF2_CPU_HARD_FAIL",
                f"lR-phase model anti-predicts impact. All seed r < 0. "
                f"seed_r={dict((k, round(v, 3)) for k, v in seed_mean_r.items())}.")

    if seeds_pass >= max(2, n_seeds * 2 // 3):
        return ("KF2_CPU_HARD_PASS",
                f"Edit impact IS predictable at N=1024. {seeds_pass}/{n_seeds} seeds: "
                f"r>={PASS_PEARSON_R}. mean_r={mean_r_all:.3f}. max_r={max_r:.3f}. "
                f"mean_delta_acc={mean_delta:.3f}.")

    return ("KF2_CPU_MIDDLE_BAND",
            f"Weak predictability at N=1024. {seeds_pass}/{n_seeds} seeds pass. "
            f"mean_r={mean_r_all:.3f}. mean_delta_acc={mean_delta:.3f}.")


def _instrumentation_selftest() -> None:
    # 1. Pearson r formulas
    x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    r = pearson_r(x, 2 * x)
    assert abs(r - 1.0) < 0.01, f"pearson_r perfectly correlated: {r}"
    r_neg = pearson_r(x, -x)
    assert abs(r_neg + 1.0) < 0.01, f"pearson_r anti-correlated: {r_neg}"
    r_zero = pearson_r(x, torch.ones(5))
    assert abs(r_zero) < 0.01, f"pearson_r constant: {r_zero}"
    print("[selftest 1/3] pearson_r formulas OK", flush=True)

    # 2. Verdict formula
    def mk_c(seed, r, delta):
        return {"M": 1024, "M_over_N": 1.0, "seed": seed,
                "mean_pearson_r": r, "mean_delta_acc": delta, "n_edits_run": 3}
    cells_pass = [mk_c(7, 0.25, 0.05), mk_c(17, 0.22, 0.04), mk_c(23, 0.10, 0.03)]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "KF2_CPU_HARD_PASS", f"Expected KF2_CPU_HARD_PASS, got {v}"
    cells_fail = [mk_c(7, -0.05, 0.05), mk_c(17, -0.03, 0.04), mk_c(23, -0.10, 0.03)]
    v, msg = compute_verdict({"cells": cells_fail})
    assert v == "KF2_CPU_HARD_FAIL", f"Expected KF2_CPU_HARD_FAIL, got {v}"
    print("[selftest 2/3] verdict formulas OK", flush=True)

    # 3. Forward pass smoke
    device = torch.device("cpu")
    codebook, _ = _v3.make_kerdock_4coset_codebook(N, device)
    M_test = min(1024, codebook.shape[0])
    cell = run_one_cell(M_test, 17, codebook, N, 2, 30)
    assert "mean_pearson_r" in cell, "missing mean_pearson_r"
    assert cell["n_edits_run"] > 0, "n_edits_run = 0"
    # Kerdock is orthogonal -> mean_delta_acc should be small
    print(f"[selftest 3/3] forward pass M={M_test} r={cell['mean_pearson_r']:.3f} "
          f"delta={cell['mean_delta_acc']:.3f} OK", flush=True)

    print("[SELFTEST PASS] kf2_cpu_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    n_eval = N_EVAL_SMOKE if smoke else N_EVAL_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _ = _v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    print(f"[kf2_cpu] N={N} C={C} m_fracs={m_fracs} n_edits={n_edits} "
          f"seeds={seeds} mode={'smoke' if smoke else 'full'}", flush=True)

    all_cells = []
    for seed in seeds:
        for mf in m_fracs:
            M = int(mf * N)
            M = min(M, 4 * C)
            print(f"  seed={seed} M={M} ({mf}N)...", flush=True)
            cell = run_one_cell(M, seed, codebook, N, n_edits, n_eval)
            all_cells.append(cell)
            print(f"    r={cell['mean_pearson_r']:.3f} delta={cell['mean_delta_acc']:.3f}",
                  flush=True)

    summary = {"cells": all_cells, "N": N, "m_fracs": m_fracs, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "m_fracs": m_fracs, "n_edits": n_edits, "seeds": seeds,
                    "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf2_cpu] VERDICT: {verdict}", flush=True)
    print(f"[kf2_cpu] {verdict_msg}", flush=True)
    print(f"[kf2_cpu] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
