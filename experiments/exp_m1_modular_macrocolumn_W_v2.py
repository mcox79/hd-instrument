"""M1 MODULAR K-MACROCOLUMN W v2 -- brain-drill #6 with FLOPS-cost tracking.

Source pre-reg: notes/research_brain_cortical_microcircuit_W_matrix_architecture_5x_drill_2026-06-22.md
v1 smoke ran 2026-06-22 (12 cells, 70s, MIDDLE_BAND): K=1 anchor + K=8/32 modular content_router
all hit recall=1.0 at N<=1000; nullability bracket cleanly validated (content beats random 2x at K=8,
7x at K=32). Anchor at N=1000 saturated recall=1.0 so sqrt(K) capacity multiplier was INCONCLUSIVE.
v1 full was queued but never dispatched.

v2 deltas vs v1 (per spawn-prompt brain-drill #6 ask):
  1. Adds per-arm FLOPS tracking (write_flops, read_flops) -- the "data-routing-invariance" benefit
     under test is whether modular Top-m=2 routing reads ONLY m*(N_per^2) FLOPS vs monolithic
     N_DIM_total^2 FLOPS at recall parity. Pre-reg HARD_PASS adds: at recall parity M=1000,
     modular retrieval-cost <= 50% monolithic.
  2. HARD_PASS retains v1 PRIMARY (content vs random ratio >= 1.5) + SECONDARY (sqrt(K) capacity
     multiplier >= 2.0x) BUT promotes the FLOPS-cost criterion to a parallel HARD_PASS path:
       HARD_PASS_capacity = K>1 effective_capacity >= 2.0x K=1 anchor + PRIMARY
       HARD_PASS_cost     = K>1 read_flops <= 0.5x K=1 read_flops at recall parity (M=1000) + PRIMARY
     Either path triggers HARD_PASS; both triggers HARD_PASS_PLUS (cap+cost benefit jointly).
  3. M=1000 facts is the headline anchor (spawn-prompt). N_ITEMS_SWEEP keeps the v1 push beyond
     anchor to bracket K=1 cliff, but adds M=1000 as a guaranteed measurement point and computes
     the FLOPS-cost metric only at that point.
  4. TODO #6 RESOLUTION in-cell smoke-name detection pattern adopted at module top.

ARMS per (K, N_items, seed):
  recall_content    -- content-routed Top-m=2 modular W (THE mechanism under test)
  recall_random     -- random-routed Top-m=2 modular W (NULLABILITY BRACKET per Prediction 4)
  per_shard_util    -- max-shard / mean-shard write-count ratio (diagnostic of router collapse)
  read_flops        -- per-query effective FLOPS for content-router arm (data-routing-invariance)
  write_flops       -- per-item effective FLOPS for content-router arm

CONFIGURATIONS:
  K=1   : N_eff = 4096                (MONOLITHIC_W; substrate anchor; reproduces ~327 baseline regime)
  K=8   : N_per = 1448 (8*1448^2 ~= 16,786,432 ~= 4096^2)
  K=32  : N_per = 724  (32*724^2 ~= 16,773,632 ~= 4096^2)

DISCRIMINATOR (per spawn-prompt brain-drill #6 + v1 strict pre-reg):
  HARD_PASS  = PRIMARY (content_router >= 1.5x random_router at K>1)
               AND (HARD_PASS_capacity OR HARD_PASS_cost)
               AND K=1 anchor present + per_shard_util <= 0.5
               AND cv across seeds <= 0.25
               AND zero LLM forward calls.
    HARD_PASS_capacity = at fixed P, K=8 OR K=32 effective_capacity >= 2.0x K=1 anchor.
    HARD_PASS_cost     = at M=1000 facts, modular read_flops <= 0.5x monolithic read_flops
                         AT recall parity (modular_recall >= 0.95 * monolithic_recall at M=1000).
  HARD_PASS_PLUS = BOTH HARD_PASS_capacity AND HARD_PASS_cost.
  HARD_FAIL  = PRIMARY fails (mechanism wrong) OR no modular arm matches monolithic recall.
  MIDDLE_BAND = PRIMARY passes but neither capacity nor cost reaches HARD_PASS.

FLOPS accounting (per content-router pass):
  WRITE per item: K_router_sims = K * N_DIM (router dot-prod; same for content/random)
                  m * (N_DIM * N_per + N_per * N_per) (per top-m shard: project + outer-product)
                = K * N_DIM + m * (N_DIM * N_per + N_per^2)
  READ  per query: K * N_DIM (router) + m * (N_DIM * N_per + N_per^2 + N_per * N_items)
                  (project + matmul + cosine-vs-codebook)
                = K * N_DIM + m * (N_DIM * N_per + N_per^2 + N_per * N_items)

  For K=1 (m_eff=1): write = N_DIM + (N_DIM^2 + N_DIM^2) = ~2 * N_DIM^2 (monolithic outer + project-identity)
  For K=8, m=2:      write = 8 * N_DIM + 2 * (N_DIM * 1448 + 1448^2) = ~2 * (N_DIM * 1448 + 1448^2)
  For K=32, m=2:     write = 32 * N_DIM + 2 * (N_DIM * 724 + 724^2)

  At N_DIM=4096, K=1: write ~= 33.6M FLOPS; K=8 m=2 write ~= 16.0M; K=32 m=2 write ~= 6.1M
  -> K=8 is 0.48x K=1; K=32 is 0.18x K=1 (the data-routing-invariance benefit headline numbers)

DISCIPLINES baked in:
  - ANCHOR_NAME = "m1_modular_macrocolumn_W_v2" at module scope
  - CONFIG_VERSION derived from runtime config
  - _LLM_CALL_COUNTER = [0] (substrate-only by construction; pure numpy)
  - run_mode detection: TODO #6 RESOLUTION pattern (in-cell smoke-name detection)
  - per-seed checkpoint via experiments._seed_checkpoint
  - per_unit per (seed, K, N_items, router) stored in metrics.json
  - cv <= 0.25 across seeds in compute_verdict (capacity-battery noise allowance)
  - K=1 anchor: discriminator-regime reproduces monolithic substrate behavior
  - Random-router NEGATIVE control (Prediction 4 NULLABILITY)
  - allow_synthetic=True (substrate-primitive isolation; matches baa06f0a battery)
  - Pre-reg direction: modular K>1 (content_router) HELPS at fixed P (capacity OR cost).

Substrate W vs S separation: this cell ONLY exercises modular W_k matrices.
No S sequence-binding matrix is created or touched.

CITES:
  - research_brain_cortical_microcircuit_W_matrix_architecture_5x_drill_2026-06-22 (pre-reg)
  - Rinkus 2010 PMC2889687 (macrocolumn-WTA modularity)
  - Bricken 2023 ICLR arxiv 2303.11934 (SDM-CL continual learning)
  - Kanerva 1988 SDM
  - baa06f0a (substrate Hebbian-superposition capacity ~327 anchor)
"""
from __future__ import annotations
import sys, os, argparse, time, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "m1_modular_macrocolumn_W_v2"
_LLM_CALL_COUNTER = [0]  # pure-numpy capacity battery; substrate-only by construction


def _detect_run_mode():
    """Smoke vs full detection (TODO #6 RESOLUTION pattern).
    Priority: --smoke CLI flag > HDLAB_EXP_NAME ends-with _smoke > HDLAB_RUN_MODE env > full.
    The HDLAB_EXP_NAME suffix is load-bearing because the runner overrides HDLAB_RUN_MODE=full.
    """
    if "--smoke" in sys.argv or "--self-test" in sys.argv:
        return "smoke"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.lower().endswith("_smoke"):
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    return "full"


RUN_MODE = _detect_run_mode()
print("[smoke-detect] HDLAB_EXP_NAME=%r ends_with_smoke=%s -> RUN_MODE=%s" % (
    os.environ.get("HDLAB_EXP_NAME", ""),
    os.environ.get("HDLAB_EXP_NAME", "").lower().endswith("_smoke"),
    RUN_MODE), flush=True)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

# Config -- fixed total parameter budget P = N_DIM_TOTAL ** 2
N_DIM_TOTAL = 4096               # substrate baseline; sqrt(P) where P = 16.78M
TOTAL_PARAMS_P = N_DIM_TOTAL * N_DIM_TOTAL
M_TOP = 2                        # Top-m soft routing (m=2 per Rinkus / Bricken biological optimum)

# K values per spawn-prompt brain-drill #6: K=1 monolithic, K=8 + K=32 modular
# Query-side noise (capacity-battery convention): nonzero sigma forces cliff into measurable range
if RUN_MODE == "full":
    K_VALUES = [1, 8, 32]
    SEEDS = [7, 17, 23]
    # N_items sweep includes M=1000 (spawn-prompt anchor) + push beyond to find cliff
    N_ITEMS_SWEEP = [327, 1000, 2000, 4000, 8000, 16000]
    NOISE_SIGMA = 0.1            # query-side Gaussian noise in fraction of key norm
    N_QUERIES = 100              # eval-query cap per (K, N) -- subsampled if N > 100
else:
    # Smoke: 1 seed, 3 K values, 2 N points -- harness check + FLOPS-tracker self-test only
    K_VALUES = [1, 8, 32]
    SEEDS = [7]
    N_ITEMS_SWEEP = [327, 1000]
    NOISE_SIGMA = 0.1
    N_QUERIES = 60

CONFIG_VERSION = (
    "m1_v2; N_DIM_total=%d total_params_P=%d M_top=%d K_values=%s N_items=%s "
    "sigma=%.2f seeds=%s queries=%d"
) % (N_DIM_TOTAL, TOTAL_PARAMS_P, M_TOP, K_VALUES, N_ITEMS_SWEEP, NOISE_SIGMA, SEEDS, N_QUERIES)


def _per_shard_dim(K):
    """N_per such that K * N_per^2 ~= TOTAL_PARAMS_P (fixed total param budget across K)."""
    return max(1, int(round(math.sqrt(TOTAL_PARAMS_P / K))))


def _make_bipolar_hvs(n_vectors, dim, rng):
    """Synthetic bipolar +-1 HVs (substrate primitive; matches baa06f0a battery)."""
    return (rng.integers(0, 2, size=(n_vectors, dim)).astype(np.float32) * 2.0 - 1.0)


def _normalize_rows(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)).astype(np.float32)


def _make_shard_projections(K, n_dim_total, n_per, rng):
    """Per-shard random Gaussian projection matrices: shape (K, n_per, n_dim_total)."""
    return rng.standard_normal((K, n_per, n_dim_total)).astype(np.float32) * (1.0 / math.sqrt(n_dim_total))


def _softmax_topm(sims, m):
    """Top-m softmax weights. sims: (K,). Returns (top_idx [m], weights [m])."""
    top_idx = np.argpartition(-sims, m - 1)[:m] if m < len(sims) else np.arange(len(sims))
    top_sims = sims[top_idx]
    order = np.argsort(-top_sims)
    top_idx = top_idx[order]
    top_sims = top_sims[order]
    z = top_sims - top_sims.max()
    e = np.exp(z)
    w = e / (e.sum() + 1e-12)
    return top_idx, w.astype(np.float32)


def _compute_flops(K, n_per, n_items, m_eff, n_dim_total):
    """Per-write and per-read FLOPS estimate. Used to validate the data-routing-invariance
    benefit claim. FLOPS = floating-point multiply-add ops (so 2 ops counted as 1 mac unit).

    WRITE per item:
      router: K * n_dim_total (dot product sims vs K macrocolumn keys)
      project: m_eff * n_dim_total * n_per (project key + value to each top shard subspace)
      outer:  m_eff * n_per * n_per (Hebbian outer product per shard)

    READ per query:
      router: K * n_dim_total
      project: m_eff * n_dim_total * n_per (project query)
      matmul:  m_eff * n_per * n_per       (W_k @ q_sub)
      cleanup: m_eff * n_items * n_per     (cosine vs per-shard projected codebook)
    """
    write_flops = K * n_dim_total + m_eff * (n_dim_total * n_per + n_per * n_per)
    read_flops = (K * n_dim_total + m_eff *
                  (n_dim_total * n_per + n_per * n_per + n_items * n_per))
    return write_flops, read_flops


def _run_one_config(K, N_items, seed, rng_master, router_type="content"):
    """One (K, N_items, seed, router) run.
    router_type: "content" (similarity argmax) or "random" (NULLABILITY BRACKET).

    Returns dict with recall, per_shard_util, routing_entropy, wall_s, write_flops, read_flops.
    """
    rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
    n_per = _per_shard_dim(K)
    m_eff = min(M_TOP, K)

    keys_full = _make_bipolar_hvs(N_items, N_DIM_TOTAL, rng)
    values_full = _make_bipolar_hvs(N_items, N_DIM_TOTAL, rng)
    macrocol_keys = _make_bipolar_hvs(K, N_DIM_TOTAL, rng)
    macrocol_keys_norm = _normalize_rows(macrocol_keys)
    shard_projs = _make_shard_projections(K, N_DIM_TOTAL, n_per, rng)

    Ws = [np.zeros((n_per, n_per), dtype=np.float32) for _ in range(K)]

    keys_full_norm = _normalize_rows(keys_full)
    if router_type == "content":
        sims = keys_full_norm @ macrocol_keys_norm.T
    elif router_type == "random":
        sims = rng.standard_normal((N_items, K)).astype(np.float32)
    else:
        raise ValueError("router_type must be 'content' or 'random'")

    shard_write_count = np.zeros(K, dtype=np.int64)
    entropies = []
    top_indices = np.empty((N_items, m_eff), dtype=np.int64)
    top_weights = np.empty((N_items, m_eff), dtype=np.float32)
    for i in range(N_items):
        top_idx, w = _softmax_topm(sims[i], m_eff)
        top_indices[i] = top_idx
        top_weights[i] = w
        for j in range(m_eff):
            if w[j] > 1e-9:
                entropies.append(-w[j] * math.log(w[j] + 1e-12))

    keys_sub_all = np.empty((K, N_items, n_per), dtype=np.float32)
    vals_sub_all = np.empty((K, N_items, n_per), dtype=np.float32)
    for k_idx in range(K):
        keys_sub_all[k_idx] = keys_full @ shard_projs[k_idx].T
        vals_sub_all[k_idx] = values_full @ shard_projs[k_idx].T
    keys_sub = keys_sub_all
    vals_sub = vals_sub_all

    for k_idx in range(K):
        mask = top_indices == k_idx
        if not mask.any():
            continue
        item_rows, slot_cols = np.where(mask)
        items = item_rows
        wts = top_weights[item_rows, slot_cols].astype(np.float32)
        K_k = keys_sub[k_idx, items]
        V_k = vals_sub[k_idx, items]
        Ws[k_idx] += (V_k * wts[:, None]).T @ K_k
        shard_write_count[k_idx] += len(items)
    mean_writes = shard_write_count.mean()
    max_writes = shard_write_count.max()
    per_shard_util = float((max_writes - mean_writes) / max(mean_writes, 1e-6))
    avg_entropy = float(np.mean(entropies)) if entropies else 0.0

    n_q = min(N_items, N_QUERIES)
    q_idx = rng.choice(N_items, n_q, replace=False) if n_q < N_items else np.arange(N_items)
    correct = 0
    V_proj_norm = vals_sub / (np.linalg.norm(vals_sub, axis=2, keepdims=True) + 1e-12)
    query_norm_avg = float(np.mean(np.linalg.norm(keys_full, axis=1)))
    for qi in q_idx:
        if NOISE_SIGMA > 0:
            noise = rng.standard_normal(N_DIM_TOTAL).astype(np.float32) * NOISE_SIGMA * query_norm_avg / math.sqrt(N_DIM_TOTAL)
            query_full = keys_full[qi] + noise
        else:
            query_full = keys_full[qi]
        query_full_n = query_full / (np.linalg.norm(query_full) + 1e-12)
        if router_type == "content":
            q_sims = query_full_n @ macrocol_keys_norm.T
        else:
            q_sims = rng.standard_normal(K).astype(np.float32)
        top_idx, w = _softmax_topm(q_sims, m_eff)
        label_scores = np.zeros(N_items, dtype=np.float32)
        for j, k_idx in enumerate(top_idx):
            q_sub = shard_projs[k_idx] @ query_full
            recalled_sub = Ws[k_idx] @ q_sub
            r_norm = recalled_sub / (np.linalg.norm(recalled_sub) + 1e-12)
            shard_cos = V_proj_norm[k_idx] @ r_norm
            label_scores += w[j] * shard_cos
        pred = int(np.argmax(label_scores))
        if pred == qi:
            correct += 1
    recall = float(correct / max(n_q, 1))

    write_flops, read_flops = _compute_flops(K, n_per, N_items, m_eff, N_DIM_TOTAL)

    return {
        "K": K,
        "N_items": N_items,
        "n_per_shard": n_per,
        "router_type": router_type,
        "noise_sigma": NOISE_SIGMA,
        "recall": round(recall, 4),
        "per_shard_util": round(per_shard_util, 4),
        "routing_entropy_avg": round(avg_entropy, 4),
        "shard_writes_mean": float(mean_writes),
        "shard_writes_max": int(max_writes),
        "n_queries": n_q,
        "write_flops_per_item": int(write_flops),
        "read_flops_per_query": int(read_flops),
        "m_eff": m_eff,
    }


def run_unit(seed):
    """One seed's full sweep over K_VALUES x N_ITEMS_SWEEP x {content, random}."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    cells = []
    for K in K_VALUES:
        for N in N_ITEMS_SWEEP:
            for router in ("content", "random"):
                t_cell = time.time()
                cell = _run_one_config(K, N, seed, rng, router_type=router)
                cell["wall_s_cell"] = round(time.time() - t_cell, 2)
                cells.append(cell)
                print("  [seed=%d K=%d N=%d router=%-7s] recall=%.3f util=%.3f wall=%.2fs "
                      "write_FLOPS=%.2eM read_FLOPS=%.2eM" % (
                    seed, K, N, router, cell["recall"], cell["per_shard_util"],
                    cell["wall_s_cell"],
                    cell["write_flops_per_item"] / 1e6,
                    cell["read_flops_per_query"] / 1e6), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "cells": cells,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s": round(elapsed, 2),
    }


def compute_verdict(units, recall_thresh=0.90, recall_parity_floor=0.95):
    """Aggregate per (K, N_items, router) across seeds; compute disposition per pre-reg bands."""
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_cell_agg = {}
    for u in units:
        for c in u["cells"]:
            key = (c["K"], c["N_items"], c["router_type"])
            if key not in by_cell_agg:
                by_cell_agg[key] = {
                    "K": c["K"], "N_items": c["N_items"], "router_type": c["router_type"],
                    "n_per_shard": c["n_per_shard"], "recalls": [], "utils": [], "entropies": [],
                    "write_flops": c["write_flops_per_item"], "read_flops": c["read_flops_per_query"],
                    "m_eff": c["m_eff"],
                }
            by_cell_agg[key]["recalls"].append(c["recall"])
            by_cell_agg[key]["utils"].append(c["per_shard_util"])
            by_cell_agg[key]["entropies"].append(c["routing_entropy_avg"])
    summary = {}
    for key, agg in by_cell_agg.items():
        r_mean = float(np.mean(agg["recalls"]))
        r_std = float(np.std(agg["recalls"]))
        r_cv = r_std / max(r_mean, 1e-6)
        summary[key] = {
            "K": agg["K"], "N_items": agg["N_items"], "router_type": agg["router_type"],
            "n_per_shard": agg["n_per_shard"],
            "recall_mean": round(r_mean, 4),
            "recall_std": round(r_std, 4),
            "recall_cv": round(r_cv, 4),
            "per_shard_util_mean": round(float(np.mean(agg["utils"])), 4),
            "routing_entropy_mean": round(float(np.mean(agg["entropies"])), 4),
            "n_seeds_agg": len(agg["recalls"]),
            "write_flops_per_item": agg["write_flops"],
            "read_flops_per_query": agg["read_flops"],
            "m_eff": agg["m_eff"],
        }
    cells_flat = sorted(summary.values(), key=lambda c: (c["K"], c["N_items"], c["router_type"]))

    def eff_cap(K, router):
        max_N = 0
        for c in cells_flat:
            if c["K"] == K and c["router_type"] == router and c["recall_mean"] >= recall_thresh:
                if c["N_items"] > max_N:
                    max_N = c["N_items"]
        return max_N

    eff_cap_table = {}
    for K in K_VALUES:
        eff_cap_table[K] = {
            "content": eff_cap(K, "content"),
            "random": eff_cap(K, "random"),
        }

    anchor_eff_cap = eff_cap_table.get(1, {}).get("content", 0)
    best_modular_eff_cap = max(
        eff_cap_table.get(K, {}).get("content", 0) for K in K_VALUES if K > 1
    )

    K_disc = 0
    best_modular_router_eff_cap_random = 0
    for K in K_VALUES:
        if K > 1 and eff_cap_table[K]["content"] == best_modular_eff_cap and best_modular_eff_cap > 0:
            K_disc = K
            best_modular_router_eff_cap_random = eff_cap_table[K]["random"]
            break

    util_at_K_disc = 0.0
    if K_disc > 0:
        per_K_disc_content = [c for c in cells_flat if c["K"] == K_disc and c["router_type"] == "content"]
        if per_K_disc_content:
            util_at_K_disc = max(c["per_shard_util_mean"] for c in per_K_disc_content)

    worst_cv = 0.0
    for c in cells_flat:
        if c["K"] > 1 and c["router_type"] == "content":
            if c["recall_cv"] > worst_cv:
                worst_cv = c["recall_cv"]

    # FLOPS-COST analysis at the spawn-prompt anchor M=1000
    M_ANCHOR = 1000
    closest_M = min(N_ITEMS_SWEEP, key=lambda n: abs(n - M_ANCHOR))
    flops_cost_table = {}
    monolithic_at_M = next((c for c in cells_flat
                            if c["K"] == 1 and c["router_type"] == "content"
                            and c["N_items"] == closest_M), None)
    if monolithic_at_M is not None:
        monolithic_read_flops = monolithic_at_M["read_flops_per_query"]
        monolithic_recall = monolithic_at_M["recall_mean"]
        for K in K_VALUES:
            if K == 1:
                continue
            mod_at_M = next((c for c in cells_flat
                             if c["K"] == K and c["router_type"] == "content"
                             and c["N_items"] == closest_M), None)
            if mod_at_M is None:
                continue
            flops_ratio = mod_at_M["read_flops_per_query"] / max(monolithic_read_flops, 1)
            recall_ratio = mod_at_M["recall_mean"] / max(monolithic_recall, 1e-6)
            parity_held = mod_at_M["recall_mean"] >= recall_parity_floor * monolithic_recall
            flops_cost_table[K] = {
                "N_items": closest_M,
                "monolithic_read_flops": monolithic_read_flops,
                "modular_read_flops": mod_at_M["read_flops_per_query"],
                "flops_ratio_modular_over_monolithic": round(flops_ratio, 4),
                "monolithic_recall": monolithic_recall,
                "modular_recall": mod_at_M["recall_mean"],
                "recall_parity_held": parity_held,
                "cost_pass": parity_held and flops_ratio <= 0.5,
            }

    target_alpha = 0.3
    target_N = int(target_alpha * N_DIM_TOTAL)
    closest_N_in_sweep = min(N_ITEMS_SWEEP, key=lambda n: abs(n - target_N))
    recall_at_alpha = {}
    for K in K_VALUES:
        for router in ("content", "random"):
            match = [c for c in cells_flat if c["K"] == K and c["N_items"] == closest_N_in_sweep
                     and c["router_type"] == router]
            if match:
                recall_at_alpha[(K, router)] = match[0]["recall_mean"]

    detail = {
        "K_values": K_VALUES,
        "N_items_sweep": N_ITEMS_SWEEP,
        "M_top": M_TOP,
        "N_DIM_total": N_DIM_TOTAL,
        "total_params_P": TOTAL_PARAMS_P,
        "cells_flat": cells_flat,
        "effective_capacity_at_recall_0.90": eff_cap_table,
        "anchor_eff_cap_K1_content": anchor_eff_cap,
        "best_modular_eff_cap": best_modular_eff_cap,
        "K_disc": K_disc,
        "random_router_eff_cap_at_K_disc": best_modular_router_eff_cap_random,
        "per_shard_util_at_K_disc": util_at_K_disc,
        "worst_cv_modular_content": round(worst_cv, 4),
        "closest_N_in_sweep_to_alpha_0.3": closest_N_in_sweep,
        "recall_at_alpha_0.3_approx_by_K_router": {
            "K=%d_%s" % (k, r): v for (k, r), v in recall_at_alpha.items()
        },
        "flops_cost_at_M_anchor": flops_cost_table,
        "M_anchor": closest_M,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("synthetic-bipolar HVs (substrate primitive; matches baa06f0a battery); "
                         "fixed P=4096^2; K in {1,8,32}; Top-m=2 soft router; "
                         "K=1 anchor reproduces monolithic substrate; random-router NULLABILITY BRACKET (Pred 4); "
                         "FLOPS-cost metric measures data-routing-invariance per spawn-prompt brain-drill #6"),
        "substrate_W_vs_S_separation": ("This cell exercises ONLY modular W_k matrices; "
                                        "no sequence-binding S matrix is created or modified."),
        "cites": [
            "research_brain_cortical_microcircuit_W_matrix_architecture_5x_drill_2026-06-22",
            "Rinkus_2010_PMC2889687",
            "Bricken_2023_ICLR_arxiv_2303.11934_SDM_CL",
            "Kanerva_1988_SDM",
            "baa06f0a_substrate_Hebbian_capacity_anchor",
        ],
    }

    primary_pass = False
    primary_detail = {}
    for K in K_VALUES:
        if K <= 1:
            continue
        c_cells = [c for c in cells_flat if c["K"] == K and c["router_type"] == "content"]
        r_cells = [c for c in cells_flat if c["K"] == K and c["router_type"] == "random"]
        if not c_cells or not r_cells:
            continue
        c_mean_recall = float(np.mean([c["recall_mean"] for c in c_cells]))
        r_mean_recall = float(np.mean([c["recall_mean"] for c in r_cells]))
        ratio = c_mean_recall / max(r_mean_recall, 1e-6)
        primary_detail["K=%d" % K] = {
            "content_avg_recall": round(c_mean_recall, 4),
            "random_avg_recall": round(r_mean_recall, 4),
            "ratio_content_over_random": round(ratio, 3),
        }
        if c_mean_recall >= 0.90 and ratio >= 1.5:
            primary_pass = True
    detail["primary_nullability_bracket"] = primary_detail

    anchor_ok = anchor_eff_cap >= min(N_ITEMS_SWEEP)
    secondary_capacity_pass = (anchor_ok and best_modular_eff_cap >= 2.0 * anchor_eff_cap)
    secondary_capacity_partial = (anchor_ok and 1.1 * anchor_eff_cap < best_modular_eff_cap < 2.0 * anchor_eff_cap)
    secondary_capacity_inconclusive = (anchor_ok and best_modular_eff_cap <= 1.1 * anchor_eff_cap
                                       and anchor_eff_cap == max(N_ITEMS_SWEEP))
    detail["secondary_capacity_test"] = {
        "anchor_eff_cap": anchor_eff_cap,
        "best_modular_eff_cap": best_modular_eff_cap,
        "ratio": round(best_modular_eff_cap / max(anchor_eff_cap, 1), 3),
        "capacity_pass": secondary_capacity_pass,
        "capacity_partial": secondary_capacity_partial,
        "capacity_inconclusive": secondary_capacity_inconclusive,
        "rationale": ("INCONCLUSIVE: K=1 anchor reaches max swept N (cliff above tested range); "
                      "capacity-multiplier untestable in this regime") if secondary_capacity_inconclusive else "tested",
    }

    cost_pass_any = any(v.get("cost_pass", False) for v in flops_cost_table.values())
    cost_pass_K = [K for K, v in flops_cost_table.items() if v.get("cost_pass", False)]
    detail["secondary_cost_test"] = {
        "M_anchor": closest_M,
        "cost_pass_any": cost_pass_any,
        "cost_pass_K_list": cost_pass_K,
        "per_K": flops_cost_table,
    }

    headline = ("anchor_K1_eff_cap=%d best_modular_eff_cap=%d (K=%d) random_router_eff_cap=%d "
                "util=%.2f cv=%.3f content_vs_random_ratio=%.2fx cost_pass_K=%s") % (
        anchor_eff_cap, best_modular_eff_cap, K_disc, best_modular_router_eff_cap_random,
        util_at_K_disc, worst_cv,
        best_modular_eff_cap / max(best_modular_router_eff_cap_random, 1),
        cost_pass_K if cost_pass_K else "none")

    if not anchor_ok:
        return ("HARD_FAIL",
                "HARD_FAIL[anchor-broken]: K=1 effective_capacity=%d below min(N_sweep)=%d; "
                "harness corruption or N_ITEMS_SWEEP too narrow. %s" % (
                    anchor_eff_cap, min(N_ITEMS_SWEEP), headline),
                detail)
    if not primary_pass:
        return ("HARD_FAIL",
                "HARD_FAIL[primary-routing-mechanism]: content_router fails to materially outperform "
                "random_router (need content_mean_recall>=0.90 AND content/random>=1.5 at K>1). "
                "Routing mechanism does NOT work as claimed. %s" % headline,
                detail)
    if worst_cv > 0.25:
        return ("HARD_FAIL",
                "HARD_FAIL[cv-too-high]: worst CV across content-router cells = %.3f > 0.25; "
                "seed-unstable; cannot ratify. %s" % (worst_cv, headline),
                detail)
    if util_at_K_disc > 0.5:
        return ("HARD_FAIL",
                "HARD_FAIL[router-collapse]: per_shard_util at K=%d = %.3f > 0.5; "
                "router collapses to few shards. %s" % (K_disc, util_at_K_disc, headline),
                detail)

    # PRIMARY pass + sanity gates clear -> compose HARD_PASS via capacity OR cost path
    if secondary_capacity_pass and cost_pass_any:
        return ("HARD_PASS_PLUS",
                "HARD_PASS_PLUS: PRIMARY content_router beats random (nullability bracket); BOTH SECONDARY "
                "paths validated -- capacity multiplier best_modular=%d >= 2.0x anchor=%d AND read_flops "
                "cost <= 0.5x monolithic at recall parity (M=%d) at K=%s. Modular K-macrocolumn W is both "
                "a capacity AND a routing-cost lever. %s" % (
                    best_modular_eff_cap, anchor_eff_cap, closest_M, cost_pass_K, headline),
                detail)
    if secondary_capacity_pass:
        return ("HARD_PASS",
                "HARD_PASS[capacity-path]: PRIMARY content_router beats random; SECONDARY capacity "
                "multiplier validated: best_modular_eff_cap=%d >= 2.0x K=1 anchor=%d. (FLOPS-cost path "
                "not triggered at this regime.) %s" % (
                    best_modular_eff_cap, anchor_eff_cap, headline),
                detail)
    if cost_pass_any:
        return ("HARD_PASS",
                "HARD_PASS[cost-path]: PRIMARY content_router beats random; SECONDARY read_flops cost "
                "<= 0.5x monolithic at recall parity (M=%d) at K=%s. Modular routing delivers "
                "data-routing-invariance benefit at recall parity. (Capacity multiplier inconclusive or "
                "partial in this regime.) %s" % (closest_M, cost_pass_K, headline),
                detail)
    if secondary_capacity_inconclusive:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND[measured-mechanism]: PRIMARY content_router beats random (mechanism validated). "
                "SECONDARY capacity multiplier INCONCLUSIVE: K=1 anchor reaches max swept N=%d at "
                "recall>=0.90 (no cliff observed). SECONDARY cost-path also failed parity bar. Routes to "
                "research: push N higher to bring K=1 cliff into measurable range, OR sparsify keys to "
                "force cliff down. %s" % (max(N_ITEMS_SWEEP), headline),
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND[partial-mechanism]: PRIMARY content_router beats random (mechanism validated). "
            "SECONDARY capacity multiplier = %.2fx K=1 anchor (below 2.0x bar). SECONDARY cost-path: "
            "no K achieved <=0.5x flops at recall parity. Partial sqrt(K) scaling. %s" % (
                best_modular_eff_cap / max(anchor_eff_cap, 1), headline),
            detail)


def _selftest():
    """Mechanism selftest: shard sizing, round-trip, top-m softmax, FLOPS sanity."""
    global N_DIM_TOTAL, TOTAL_PARAMS_P
    for K in (1, 8, 32):
        n_per = _per_shard_dim(K)
        actual_P = K * n_per * n_per
        rel_err = abs(actual_P - TOTAL_PARAMS_P) / TOTAL_PARAMS_P
        assert rel_err < 0.02, "K=%d shard sizing off by %.4f" % (K, rel_err)
    saved_N, saved_P = N_DIM_TOTAL, TOTAL_PARAMS_P
    rng = np.random.default_rng(0)
    try:
        N_DIM_TOTAL = 256
        TOTAL_PARAMS_P = 256 * 256
        cell = _run_one_config(K=1, N_items=20, seed=0, rng_master=rng, router_type="content")
        assert cell["recall"] >= 0.80, "K=1 tiny round-trip recall=%.3f; expected >=0.80" % cell["recall"]
        # FLOPS sanity at small config
        assert cell["write_flops_per_item"] > 0
        assert cell["read_flops_per_query"] > 0
    finally:
        N_DIM_TOTAL = saved_N
        TOTAL_PARAMS_P = saved_P
    sims = np.array([0.1, 0.5, 0.9, 0.3, 0.7], dtype=np.float32)
    top, w = _softmax_topm(sims, 2)
    assert top[0] == 2 and top[1] == 4
    assert abs(w.sum() - 1.0) < 1e-4
    # FLOPS-formula sanity: K=32 m=2 read should be < K=1 read at same N_items
    wf1, rf1 = _compute_flops(K=1, n_per=4096, n_items=1000, m_eff=1, n_dim_total=4096)
    wf32, rf32 = _compute_flops(K=32, n_per=724, n_items=1000, m_eff=2, n_dim_total=4096)
    assert rf32 < rf1, "K=32 read FLOPS (%d) should be < K=1 read FLOPS (%d)" % (rf32, rf1)
    assert wf32 < wf1, "K=32 write FLOPS (%d) should be < K=1 write FLOPS (%d)" % (wf32, wf1)
    flops_ratio = rf32 / rf1
    print("[selftest] PASS: shard-sizing OK; K=1 tiny round-trip recall=%.3f; "
          "top-m softmax OK; K=32/K=1 read FLOPS ratio=%.3f (data-routing-invariance OK)." % (
              cell["recall"], flops_ratio), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d K=%s N_items=%s seeds=%s queries=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM_TOTAL, K_VALUES, N_ITEMS_SWEEP, SEEDS, N_QUERIES, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM_TOTAL, "schema": "m1-modular-W-v2"}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM_total": N_DIM_TOTAL,
        "total_params_P": TOTAL_PARAMS_P,
        "K_values": K_VALUES,
        "N_items_sweep": N_ITEMS_SWEEP,
        "noise_sigma": NOISE_SIGMA,
        "M_top": M_TOP,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_m1_modular_macrocolumn_W_v2",
        "per_seed": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": ("substrate-only by construction (pure numpy; "
                                       "zero LLM forward calls; no encoder)"),
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "allow_synthetic": True,
        "corpus_provenance": "synthetic_bipolar_HVs_per_substrate_primitive_baa06f0a_anchor",
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
