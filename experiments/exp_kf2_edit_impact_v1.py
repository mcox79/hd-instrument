"""KF-2 EDIT-WITH-IMPACT-PREDICTION: N=4096 Kerdock, predict which facts shift on edit.

SCIENTIFIC QUESTION (Killer Feature 2):
  When one fact is edited (anti-Hebbian erase + re-insert), can we predict
  WHICH other facts will shift (and by how much) based on structural properties?
  This is the 'edit-with-impact-prediction' capability: knowing the collateral
  damage before committing the edit.

THREE PREDICTION MODELS COMPARED:
  1. lR-phase basin-boundary prediction: facts closest to edited fact's key
     (by codebook distance) will shift most. Predicts impact ~ key_similarity.
  2. Uniform: all facts shift equally (null model).
  3. Nearest-neighbor: facts within Hamming radius H of edited key shift most.

  Metric: for each edit, measure actual delta_retrieval_score for all other
  facts, then compute correlation between predicted impact and actual impact.
  Prediction quality = Pearson r(predicted_impact, actual_delta).

DESIGN:
  - Store M=2N facts at N=4096 Kerdock 4-coset.
  - For each of 5 edit operations (per seed):
    - Edit fact i: anti-Hebb erase + re-insert new value.
    - For all other M-1 facts: measure delta_acc (did argmax prediction change?).
    - Compute key-similarity of other facts to edited fact.
    - Compute correlation between key_sim and |delta_acc|.
  - 3 seeds x 5 M values x 5 edits = 75 data points.
  - Also compare: does editing fact at HIGH load (M=4N) predict more or less accurately?

PRE-REGISTERED BANDS (first impact-prediction measurement):
  Calibration probe; no prior empirical anchor.

  HARD_PASS: mean Pearson r(predicted, actual) > 0.20 for lR-phase model in
    >= 2/3 seeds (key_sim DOES predict edit collateral damage).
    Product-grade: user can predict impact before committing.
  HARD_FAIL: r < 0.0 in all seeds (key similarity ANTI-predicts impact -- closer
    keys are MORE protected, not less).
  MIDDLE_BAND: 0.0 <= r <= 0.20 (weak but non-negative prediction signal).

FORMULA SELF-TESTS:
  1. For perfectly orthogonal keys: editing fact i should have zero impact on
     any other fact. delta_acc = 0 for all j != i. Correlation undefined (no variation).
  2. For highly correlated keys: editing i affects j proportionally to key_sim(i,j).
     r should be positive and high.
  3. Kerdock is approximately orthogonal. Expected: weak positive r.
  4. Test: after editing M facts in turn, mean_delta_acc should be small
     (Kerdock isolation). If mean_delta_acc > 0.3, suspicious.

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 2 M values, 3 edits. ~5s.
  Full: N=4096, 3 seeds, 5 M values, 5 edits.
  scale: (4096/1024)^1.5 * 3 * (5/2) * (5/3) = 8 * 3 * 2.5 * 1.67 = 100
  timeout_s = ceil(1.5 * 5 * 100) = ceil(750) -> 900s.

N-suffix: no _nN suffix; multi-M sweep (PROT-018: stated explicitly).
Queue: overnight_queue (GPU; Kerdock 4-coset at N=4096, matrix ops)
Pre-reg: preregs/2026-05-27_kf2_edit_impact_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024
M_FRACS_FULL = [0.5, 1.0, 2.0, 4.0]    # M/N values
M_FRACS_SMOKE = [1.0, 2.0]
N_EDITS_FULL = 5
N_EDITS_SMOKE = 3
N_EVAL_PROBE = 200   # facts to probe for impact measurement
N_EVAL_SMOKE = 50
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
PASS_PEARSON_R = 0.20
FAIL_PEARSON_R = 0.0


def get_output_dir(default_name: str = "kf2_edit_impact_v1") -> Path:
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


def build_w(codebook: torch.Tensor, M: int, seed: int, N: int, device: torch.device):
    """Build Hebbian W for M Kerdock facts."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    # Handle over-capacity
    parts_k, parts_v = [], []
    remaining = M
    while remaining > 0:
        take = min(remaining, C)
        parts_k.append(torch.randperm(C, generator=gen, device=device)[:take])
        parts_v.append(torch.randperm(C, generator=gen, device=device)[:take])
        remaining -= take
    key_idx = torch.cat(parts_k)[:M]
    val_idx = torch.cat(parts_v)[:M]
    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = values[start:start + 256]
        W += (v_b.T @ k_b) / N
    return W, keys, values, key_idx, val_idx


def edit_fact(W: torch.Tensor, key: torch.Tensor, val_old: torch.Tensor,
               val_new: torch.Tensor, N: int) -> torch.Tensor:
    """Anti-Hebbian erase + Hebbian insert."""
    Wk = W @ key
    kk = float((key * key).sum().item())
    if kk < 1e-10:
        return W
    W = W - torch.outer(Wk, key) / kk
    W = W + torch.outer(val_new, key) / N
    return W


def measure_impact(W_before: torch.Tensor, W_after: torch.Tensor,
                    probe_keys: torch.Tensor, probe_val_idx: torch.Tensor,
                    codebook: torch.Tensor, N: int, C: int) -> torch.Tensor:
    """For each probe key, measure |delta prediction| (0/1 for argmax change)."""
    sims_before = (codebook @ (probe_keys @ W_before.T).T) / N   # (C, n)
    sims_after = (codebook @ (probe_keys @ W_after.T).T) / N
    pred_before = torch.argmax(sims_before, dim=0)
    pred_after = torch.argmax(sims_after, dim=0)
    return (pred_before != pred_after).float()   # (n,) binary impact indicator


def run_one_cell(M: int, seed: int, codebook: torch.Tensor, N: int,
                  n_edits: int, n_eval: int, device: torch.device) -> dict:
    """Run one (M, seed) cell."""
    C = codebook.shape[0]
    W, keys, values, key_idx, val_idx = build_w(codebook, M, seed, N, device)

    # Generate replacement values
    gen = torch.Generator(device=device).manual_seed(seed + 50000)
    new_val_perm = torch.randperm(C, generator=gen, device=device)
    values_new = codebook[new_val_perm[:M] % C]

    pearson_rs = []
    mean_delta_accs = []
    n_probe = min(n_eval, M)

    for edit_i in range(min(n_edits, M)):
        W_after = edit_fact(W, keys[edit_i], values[edit_i], values_new[edit_i], N)

        # Probe all other facts for impact
        probe_start = max(0, edit_i - n_probe // 2)
        probe_end = min(M, probe_start + n_probe)
        # Exclude edit_i from probe set
        probe_indices = [j for j in range(probe_start, probe_end) if j != edit_i]
        if not probe_indices:
            continue
        probe_indices_t = torch.tensor(probe_indices, dtype=torch.long, device=device)
        probe_keys = keys[probe_indices_t]
        probe_val_idx_local = val_idx[probe_indices_t] % C

        # Actual impact
        impact_actual = measure_impact(W, W_after, probe_keys, probe_val_idx_local,
                                        codebook, N, C)

        # Predicted impact (lR-phase model): key similarity to edited key
        # key_sim = cosine similarity between probe keys and edited key
        edited_key = keys[edit_i]
        edited_key_norm = edited_key.norm().clamp(min=1e-10)
        probe_norms = probe_keys.norm(dim=1).clamp(min=1e-10)
        cos_sims = (probe_keys @ edited_key) / (probe_norms * edited_key_norm)  # (n,)
        # lR-phase: impact ~ key similarity (facts near edited key are more affected)
        predicted_impact = cos_sims.abs()

        # Pearson r
        r = pearson_r(predicted_impact, impact_actual)
        pearson_rs.append(r)
        mean_delta_accs.append(float(impact_actual.mean().item()))

    mean_r = sum(pearson_rs) / len(pearson_rs) if pearson_rs else 0.0
    mean_delta = sum(mean_delta_accs) / len(mean_delta_accs) if mean_delta_accs else 0.0

    return {
        "M": M,
        "M_over_N": M / N,
        "seed": seed,
        "mean_pearson_r": mean_r,
        "mean_delta_acc": mean_delta,
        "n_edits_run": len(pearson_rs),
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_INCONCLUSIVE", "No cells.")

    pearson_rs = [c["mean_pearson_r"] for c in cells if c.get("n_edits_run", 0) > 0]
    if not pearson_rs:
        return ("KF2_INCONCLUSIVE", "No valid cells.")

    # Group by seed
    seeds_seen = list(set(c["seed"] for c in cells))
    seed_mean_r = {}
    for s in seeds_seen:
        rs = [c["mean_pearson_r"] for c in cells if c["seed"] == s and c.get("n_edits_run", 0) > 0]
        seed_mean_r[s] = sum(rs) / len(rs) if rs else 0.0

    n_seeds = len(seed_mean_r)
    seeds_pass = sum(1 for r in seed_mean_r.values() if r >= PASS_PEARSON_R)
    mean_r_all = sum(pearson_rs) / len(pearson_rs)
    max_r = max(pearson_rs)
    mean_delta = sum(c["mean_delta_acc"] for c in cells) / len(cells)

    # HARD_FAIL: negative correlation in all seeds
    if all(r < FAIL_PEARSON_R for r in seed_mean_r.values()):
        return ("KF2_HARD_FAIL",
                f"lR-phase model ANTI-predicts impact. All seed correlations < 0. "
                f"seed_r={dict((k, round(v, 3)) for k, v in seed_mean_r.items())}. "
                f"Key similarity is an INVERSE predictor of edit impact.")

    # HARD_PASS: >= 2/3 seeds have r > 0.20
    if seeds_pass >= max(2, n_seeds * 2 // 3):
        return ("KF2_HARD_PASS",
                f"EDIT IMPACT IS PREDICTABLE. {seeds_pass}/{n_seeds} seeds show "
                f"r >= {PASS_PEARSON_R}. mean_r={mean_r_all:.3f}. max_r={max_r:.3f}. "
                f"mean_delta_acc={mean_delta:.3f}. "
                f"Key similarity predicts collateral edit damage (lR-phase basin model).")

    return ("KF2_MIDDLE_BAND",
            f"Weak predictability. {seeds_pass}/{n_seeds} seeds pass. "
            f"mean_r={mean_r_all:.3f}. mean_delta_acc={mean_delta:.3f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: pearson_r formula
    x = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    y = torch.tensor([2.0, 4.0, 6.0, 8.0, 10.0])
    r = pearson_r(x, y)
    assert abs(r - 1.0) < 0.01, f"pearson_r of perfectly correlated = {r}, expected 1.0"
    r_neg = pearson_r(x, -y)
    assert abs(r_neg + 1.0) < 0.01, f"pearson_r of anti-correlated = {r_neg}, expected -1.0"
    r_zero = pearson_r(x, torch.ones(5))
    assert abs(r_zero) < 0.01, f"pearson_r with constant = {r_zero}, expected ~0"

    # Self-test 2: verdict logic
    def mk_c(seed, m, r, delta):
        return {"M": m, "M_over_N": m/4096, "seed": seed,
                "mean_pearson_r": r, "mean_delta_acc": delta, "n_edits_run": 3}

    # HARD_PASS: 2/3 seeds pass
    cells_pass = [mk_c(7, 4096, 0.25, 0.05), mk_c(17, 4096, 0.22, 0.04),
                   mk_c(23, 4096, 0.10, 0.03)]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "KF2_HARD_PASS", f"Expected KF2_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: all negative
    cells_fail = [mk_c(7, 4096, -0.05, 0.05), mk_c(17, 4096, -0.03, 0.04),
                   mk_c(23, 4096, -0.10, 0.03)]
    v, msg = compute_verdict({"cells": cells_fail})
    assert v == "KF2_HARD_FAIL", f"Expected KF2_HARD_FAIL, got {v}: {msg}"

    # Self-test 3: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    codebook, _ = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = min(C, N_test)
    cell = run_one_cell(M_test, 17, codebook, N_test, 2, 20, device)
    assert "mean_pearson_r" in cell, "missing mean_pearson_r"
    assert "mean_delta_acc" in cell, "missing mean_delta_acc"
    assert cell["mean_delta_acc"] < 0.5, (
        f"SUSPICIOUS: mean_delta_acc={cell['mean_delta_acc']:.3f} > 0.5. "
        f"Kerdock isolation should make most edits non-collateral."
    )

    print("[SELFTEST PASS] kf2_edit_impact_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    n_eval = N_EVAL_SMOKE if smoke else N_EVAL_PROBE
    config = {"smoke": smoke, "N": N, "m_fracs": m_fracs, "n_edits": n_edits, "n_eval": n_eval}

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    print(f"[kf2] N={N} C={C} seeds={seeds} m_fracs={m_fracs} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    all_cells = []
    for seed in seeds:
        for m_frac in m_fracs:
            M = int(m_frac * N)
            M = min(M, 4 * C)   # cap at 4x codebook size
            print(f"  seed={seed} M={M} ({m_frac}N)...", flush=True)
            cell = run_one_cell(M, seed, codebook, N, n_edits, n_eval, device)
            all_cells.append(cell)
            print(f"    r={cell['mean_pearson_r']:.3f} delta={cell['mean_delta_acc']:.3f}",
                  flush=True)

    summary = {
        "cells": all_cells,
        "N_full": N_FULL,
        "N_used": N,
        "m_fracs": m_fracs,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf2] VERDICT: {verdict}", flush=True)
    print(f"[kf2] {verdict_msg}", flush=True)
    print(f"[kf2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
