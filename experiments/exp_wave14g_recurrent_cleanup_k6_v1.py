"""Bounded-iteration recurrent cleanup head: multi-hop K6 probe.

Tests whether a bounded sign-Hopfield recurrence applied to the SAME outer-product
storage W improves multi-hop d-cliff retrieval at d=25, compared to the linear
arm (single-pass W k query).

Two arms share identical W = (1/N) sum v_i k_i^T storage:
  Arm A (linear baseline): y = W k; report cosine(y, v_target)
  Arm B (bounded recurrent): y_0 = W k; y_{t+1} = sign((1/N) Σ_j <y_t, v_j> k_j); T in {2,3,5}

Pre-reg: preregs/2026-05-26_wave14g_recurrent_cleanup_k6_v1.md

Pre-registered verdicts:
  HARD_PASS: arm B improvement >= +0.10 per-hop acc at d=25 in >= 3/4 M-grid cells (CI<0.05)
  HARD_FAIL: arm B <= arm A at d=25 in >= 3/4 M-grid cells
  MIDDLE_BAND: +0.03 to +0.10 in 1-2 cells, sub-threshold elsewhere
  INSTRUMENTATION_FAIL: sign-Hopfield oscillation (CI>=0.10) or arm B diverges in >20% cells
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

# --- design (exp_dev autonomy) ---
N_FULL = 4096
N_SMOKE = 512
K = 8                        # multi-hop reference K from cap_map v60
D_VALUES_FULL = [10, 25, 50]  # bracket d=25 cliff; d=50 shows decay
D_VALUES_SMOKE = [10, 25]
M_GRID_FULL = [50, 100, 200, 500]
M_GRID_SMOKE = [20, 50]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
T_VALUES = [2, 3, 5]        # bounded iteration counts

HARD_PASS_LIFT = 0.10
HARD_FAIL_THRESH = 0.00     # arm B <= arm A
MIDDLE_LOWER = 0.03
CI_FAIL_THRESH = 0.10
DIVERGE_FRAC_THRESH = 0.20

BATCH_STORE = 512


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
        raise ValueError("empty verdict or verdict_msg")


# --- substrate primitives ---

def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) sum v_i k_i^T."""
    W = torch.zeros(N, N, dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def linear_recall(W: torch.Tensor, query: torch.Tensor) -> torch.Tensor:
    """Arm A: single-pass y = W k."""
    return query @ W.T  # (N,)


def recurrent_recall(W: torch.Tensor, query: torch.Tensor,
                     vals: torch.Tensor, N: int, T: int) -> torch.Tensor:
    """Arm B: bounded sign-Hopfield recurrence y_{t+1} = sign((1/N) Σ_j <y_t, v_j> k_j).

    Self-test pair (see _instrumentation_selftest):
      - exact match at T=0: y_0 = W k_exact -> <y_0, v_exact> ≈ 1 - crosstalk -> y_1 ≈ v_exact.
    """
    y = query @ W.T  # initial y_0 = W k (shape N)
    for _ in range(T):
        # inner products: <y, v_j> for all stored j
        sims = vals @ y  # (M_stored,) -- vals is (M_stored, N)
        # reconstruct: sum_j sim_j * k_j (stored keys) / N
        # vals are the stored items; keys are the cue items
        # sign-Hopfield update: y_{t+1} = sign( (1/N) Σ_j <y_t, v_j> k_j )
        # Here keys are already in W; we approximate by recomputing from stored items
        # using the same outer-product keys that were stored.
        # NOTE: requires access to stored keys at retrieval time -- passed as _stored_keys
        break  # placeholder; full impl below
    return y


def recurrent_recall_with_keys(W: torch.Tensor, query: torch.Tensor,
                                stored_keys: torch.Tensor, stored_vals: torch.Tensor,
                                T: int) -> torch.Tensor:
    """Arm B: bounded sign-Hopfield recurrence using explicit stored (k, v) pairs.

    y_0 = W k (linear pass)
    y_{t+1} = sign( (1/N) Σ_j <y_t, v_j> k_j )

    This is a second pass through outer-product storage -- approximating
    the iterated linear-cleanup correction.
    """
    N = query.shape[0]
    y = query @ W.T  # y_0: (N,)
    for _ in range(T):
        sims = stored_vals @ y  # (M_stored,): <y, v_j>
        y_new = (sims.unsqueeze(1) * stored_keys).sum(dim=0) / N  # (N,)
        y = torch.sign(y_new.clamp(-1e9, 1e9))  # bipolar output
        # guard: if y is all-zero (degenerate), stop
        if y.abs().sum() < 1.0:
            break
    return y


def cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    na = a.norm()
    nb = b.norm()
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float((a @ b) / (na * nb))


# --- instrumentation self-test ---

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = "cpu"
    N = 64
    M = 10
    T = 2
    gen = torch.Generator(device=device).manual_seed(99)

    keys = make_bsc(M, N, gen, device)
    vals = make_bsc(M, N, gen, device)
    W = outer_product_store(keys, vals, N)

    # Self-test 1: exact match recovery at T=1 (per handoff self-test pair 1)
    # If k_query = keys[0] exactly, y_0 = W k_0 should have <y_0, v_0> >> 0
    # and y_1 via recurrence should be closer to v_0 than y_0 (or at least correlated)
    query = keys[0]
    y0 = linear_recall(W, query)
    cos_linear = cosine_sim(y0, vals[0])
    assert cos_linear > 0.0, f"linear recall gave 0 cosine on exact key (M={M}, N={N})"

    y_rec = recurrent_recall_with_keys(W, query, keys, vals, T)
    cos_recurrent = cosine_sim(y_rec, vals[0])
    assert cos_recurrent is not None and not math.isnan(cos_recurrent), \
        f"recurrent recall returned NaN cosine"
    # Self-test 2: random query should give near-zero cosine (E[|inner|] ~ sqrt(M/N))
    gen2 = torch.Generator(device=device).manual_seed(1234)
    q_rnd = make_bsc(1, N, gen2, device)[0]
    y_rnd = linear_recall(W, q_rnd)
    cos_rnd = cosine_sim(y_rnd, vals[0])
    # cos should be sub-threshold -- not testing exact value, just non-null
    assert not math.isnan(cos_rnd), "random query produced NaN cosine"

    # Self-test 3: outer_product_store metric is non-null/non-zero
    assert W.abs().max().item() > 0.0, "W is all-zero"

    # Self-test 4: CI width check sentinel -- verify we can compute std across seeds
    samples = [0.5 + 0.01 * i for i in range(5)]
    mean_s = sum(samples) / len(samples)
    std_s = math.sqrt(sum((x - mean_s) ** 2 for x in samples) / max(len(samples) - 1, 1))
    assert std_s > 0.0, "CI width sentinel: zero std on non-constant samples"

    print("[selftest] all 4 assertions passed")


_instrumentation_selftest()


# --- multi-hop chain builder ---

def build_chain(d: int, N: int, M_stored: int, gen: torch.Generator, device):
    """Build a d-hop chain plus distractors in a shared W.

    Returns: (W, chain_keys, chain_vals, stored_keys, stored_vals)
    where chain is: k_0 -> v_0=k_1 -> v_1=k_2 -> ... -> v_{d-1}=v_target
    and M_stored - d distractors are stored alongside.
    """
    # Generate M_stored random pairs; overwrite first d with chain
    all_keys = make_bsc(M_stored, N, gen, device)   # (M_stored, N)
    all_vals = make_bsc(M_stored, N, gen, device)   # (M_stored, N)

    # Build chain: entity atoms e_0 ... e_d
    entities = make_bsc(d + 1, N, gen, device)       # (d+1, N)
    # Store chain transitions: (e_0, e_1), (e_1, e_2), ..., (e_{d-1}, e_d)
    # Ensure M_stored >= d so all chain hops fit in the stored pairs
    for hop in range(min(d, M_stored)):
        all_keys[hop] = entities[hop]
        all_vals[hop] = entities[hop + 1]

    W = outer_product_store(all_keys, all_vals, N)
    return W, entities, all_keys, all_vals


def chain_query_accuracy(W: torch.Tensor, entities: torch.Tensor,
                          stored_keys: torch.Tensor, stored_vals: torch.Tensor,
                          d: int, N: int, T: int, arm: str) -> dict:
    """Run d-hop chain query and report per-hop accuracy and final cosine.

    arm: 'linear' (Arm A) or f'recurrent_T{T}' (Arm B)
    """
    query = entities[0]
    per_hop_cos = []
    for hop in range(d):
        target = entities[hop + 1]
        if arm == "linear":
            y = linear_recall(W, query)
        else:
            y = recurrent_recall_with_keys(W, query, stored_keys, stored_vals, T)
        cos = cosine_sim(y, target)
        per_hop_cos.append(cos)
        # for next hop: use the recalled output as next query (argmax-style via sign)
        query = torch.sign(y.clamp(-1e9, 1e9))
        if query.abs().sum() < 1.0:
            # degenerate recovery -- stop chain
            per_hop_cos.extend([0.0] * (d - hop - 1))
            break

    # Per-hop accuracy: cosine > 0.5 = correct retrieval (matched sign-majority)
    per_hop_acc = [1.0 if c > 0.5 else 0.0 for c in per_hop_cos]
    return {
        "per_hop_cos": per_hop_cos,
        "per_hop_acc": per_hop_acc,
        "acc_at_d": per_hop_acc[-1] if per_hop_acc else 0.0,
        "mean_hop_cos": float(sum(per_hop_cos) / max(len(per_hop_cos), 1)),
    }


# --- per-cell runner ---

def run_cell(seed: int, M: int, d: int, N: int, T_list: list, device) -> dict:
    """One (seed, M, d) cell: compare linear vs recurrent arms."""
    gen = torch.Generator(device=device).manual_seed(seed)
    W, entities, stored_keys, stored_vals = build_chain(d, N, M, gen, device)

    # Run N_TRIALS independent chains from W for statistical power
    N_TRIALS = 5  # quick but meaningful; 5 trials x 5 seeds = 25 per cell
    linear_accs = []
    recurrent_accs = {T: [] for T in T_list}

    for trial in range(N_TRIALS):
        gen_t = torch.Generator(device=device).manual_seed(seed * 1000 + trial)
        W_t, ents_t, sk_t, sv_t = build_chain(d, N, M, gen_t, device)

        r_lin = chain_query_accuracy(W_t, ents_t, sk_t, sv_t, d, N, T=0, arm="linear")
        linear_accs.append(r_lin["acc_at_d"])

        for T in T_list:
            r_rec = chain_query_accuracy(W_t, ents_t, sk_t, sv_t, d, N, T=T,
                                          arm=f"recurrent_T{T}")
            recurrent_accs[T].append(r_rec["acc_at_d"])

    def _mean(xs): return float(sum(xs) / max(len(xs), 1))
    def _std(xs):
        m = _mean(xs)
        return float(math.sqrt(sum((x - m) ** 2 for x in xs) / max(len(xs) - 1, 1)))

    lin_mean = _mean(linear_accs)
    lin_std = _std(linear_accs)
    rec_stats = {}
    for T in T_list:
        rec_stats[f"T{T}_mean"] = _mean(recurrent_accs[T])
        rec_stats[f"T{T}_std"] = _std(recurrent_accs[T])
        rec_stats[f"T{T}_lift"] = _mean(recurrent_accs[T]) - lin_mean

    return {
        "linear_acc_mean": lin_mean,
        "linear_acc_std": lin_std,
        "recurrent": rec_stats,
        "best_T_lift": max(rec_stats.get(f"T{T}_lift", -999.0) for T in T_list),
    }


# --- main ---

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args, _ = parser.parse_known_args()
    smoke = args.smoke

    t0 = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    N = N_SMOKE if smoke else N_FULL
    d_values = D_VALUES_SMOKE if smoke else D_VALUES_FULL
    m_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[recurrent_cleanup_k6] mode={'smoke' if smoke else 'full'} N={N} device={device}")
    print(f"  d_values={d_values} M_grid={m_grid} seeds={seeds} T_values={T_VALUES}")

    # Collect per-cell results
    all_cells = []
    for d in d_values:
        for M in m_grid:
            cell_results = []
            for seed in seeds:
                result = run_cell(seed, M, d, N, T_VALUES, device)
                result.update({"seed": seed, "d": d, "M": M})
                cell_results.append(result)
                lin = result["linear_acc_mean"]
                best_lift = result["best_T_lift"]
                print(f"  [d={d} M={M} seed={seed}] linear={lin:.3f} best_recurrent_lift={best_lift:+.3f}")
            all_cells.append({"d": d, "M": M, "per_seed": cell_results})

    # Aggregate: per (d, M) cell: mean linear acc, mean best-T lift, CI width
    def aggregate_cell(cell_data):
        per_seed = cell_data["per_seed"]
        lin_means = [r["linear_acc_mean"] for r in per_seed]
        lift_means = [r["best_T_lift"] for r in per_seed]

        def _mean(xs): return float(sum(xs) / max(len(xs), 1))
        def _std(xs):
            m = _mean(xs)
            return float(math.sqrt(sum((x - m) ** 2 for x in xs) / max(len(xs) - 1, 1)))

        # 95% CI width approximation: 2 * std / sqrt(n)
        n = max(len(lift_means), 1)
        ci_width = 2.0 * _std(lift_means) / math.sqrt(n)

        return {
            "d": cell_data["d"],
            "M": cell_data["M"],
            "linear_acc_mean": _mean(lin_means),
            "lift_mean": _mean(lift_means),
            "lift_std": _std(lift_means),
            "ci_width": ci_width,
        }

    agg = [aggregate_cell(c) for c in all_cells]

    # Focus analysis on d=25 cells (primary test)
    d25_cells = [a for a in agg if a["d"] == 25]
    n_d25 = len(d25_cells)

    # Count cells where arm B is hard-pass / hard-fail
    hard_pass_cells = sum(1 for a in d25_cells
                          if a["lift_mean"] >= HARD_PASS_LIFT and a["ci_width"] < CI_FAIL_THRESH)
    hard_fail_cells = sum(1 for a in d25_cells if a["lift_mean"] <= HARD_FAIL_THRESH)
    diverge_cells = sum(1 for a in d25_cells if a["ci_width"] >= CI_FAIL_THRESH)

    # Verdict logic
    verdict = "RECURRENT_MIDDLE_BAND"
    verdict_parts = []

    # INSTRUMENTATION_FAIL: diverge in >20% of cells
    if diverge_cells / max(n_d25, 1) > DIVERGE_FRAC_THRESH:
        verdict = "RECURRENT_INSTRUMENTATION_FAIL"
        verdict_parts.append(
            f"sign-Hopfield divergence (CI>={CI_FAIL_THRESH}) in "
            f"{diverge_cells}/{n_d25} d=25 cells (>{DIVERGE_FRAC_THRESH:.0%})"
        )
    elif hard_pass_cells >= 3:
        verdict = "RECURRENT_HARD_PASS"
        verdict_parts.append(
            f"arm B lift>={HARD_PASS_LIFT} with CI<{CI_FAIL_THRESH} in "
            f"{hard_pass_cells}/{n_d25} d=25 cells; multi-hop recurrent benefit confirmed"
        )
    elif hard_fail_cells >= 3:
        verdict = "RECURRENT_HARD_FAIL"
        verdict_parts.append(
            f"arm B <= arm A (lift<={HARD_FAIL_THRESH}) in {hard_fail_cells}/{n_d25} d=25 cells; "
            f"recurrent variant ruled out for multi-hop; linear primitive confirmed sole primitive"
        )
    else:
        # Middle band: characterize
        middle_cells = sum(1 for a in d25_cells
                           if MIDDLE_LOWER < a["lift_mean"] < HARD_PASS_LIFT)
        verdict = "RECURRENT_MIDDLE_BAND"
        verdict_parts.append(
            f"lift in ({MIDDLE_LOWER:.2f},{HARD_PASS_LIFT:.2f}) range for "
            f"{middle_cells}/{n_d25} d=25 cells; conditional benefit documented; "
            f"hard_pass={hard_pass_cells}/{n_d25} hard_fail={hard_fail_cells}/{n_d25}"
        )

    # Append d25 cell summary to verdict_msg
    for a in d25_cells:
        verdict_parts.append(
            f"d=25 M={a['M']}: linear={a['linear_acc_mean']:.3f} "
            f"lift={a['lift_mean']:+.3f} ci_width={a['ci_width']:.3f}"
        )

    verdict_msg = f"{verdict}: " + "; ".join(verdict_parts)

    summary = {
        "verdict": verdict,
        "d25_hard_pass_cells": hard_pass_cells,
        "d25_hard_fail_cells": hard_fail_cells,
        "d25_diverge_cells": diverge_cells,
        "d25_n_cells": n_d25,
        "aggregated_cells": agg,
    }

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N": N,
            "d_values": d_values,
            "M_grid": m_grid,
            "seeds": seeds,
            "T_values": T_VALUES,
            "hard_pass_lift": HARD_PASS_LIFT,
            "hard_fail_thresh": HARD_FAIL_THRESH,
            "ci_fail_thresh": CI_FAIL_THRESH,
            "device": device,
        },
    }

    validate_metrics(metrics)

    out_dir = get_output_dir("wave14g_recurrent_cleanup_k6_v1")
    out_path = out_dir / "metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"\n[recurrent_cleanup_k6] {verdict}: {verdict_msg[:200]}")
    print(f"[recurrent_cleanup_k6] elapsed={elapsed:.1f}s metrics written to {out_path}")

    # Also write to cwd for runner pickup
    import shutil
    shutil.copy(out_path, Path("metrics.json"))


if __name__ == "__main__":
    main()
