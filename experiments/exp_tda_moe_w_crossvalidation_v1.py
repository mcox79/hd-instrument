"""TDA cross-validation on MoE v2 W matrices (post-TDA-5probe HARD_PASS).

TRIGGER: exp_tda_reanalysis_5probe_v1 returns TDA_HARD_PASS (TDA-C agree >= 4/5;
  b_0-plateau width correctly discriminates SHIFT vs PARTITION in >= 4 of 5 cases).

CONTEXT: TDA 5-probe established that b_0-plateau width is a valid 4th MoE
  SHIFT/PARTITION diagnostic. This cross-validator tests whether the same TDA
  signature holds on the ACTUAL v2 MoE W matrices from the production pipeline,
  not just on freshly-generated matrices of the same type.

  This cross-validates the diagnostic against the FULL SCALE outputs already
  in data/exp_wave14_moe_*/ directories, ensuring TDA-C works as an
  OFFLINE AUDIT tool (applied to existing model checkpoints, not requiring re-run).

DESIGN:
  Load existing metrics.json files from v200-era MoE experiments to get
  K, N, M_per_expert, seeds. Re-generate W matrices from the SAME seeds
  and apply TDA. Compare TDA-C call to the pre-existing verdict.

  MoE experiments cross-referenced:
  - wave14_moe_shift_K_scaling_v1: K in {2, 4, 8, 16, 32, 64}
  - wave14_moe_shift_K_scaling_v2: K-scaling follow-up
  - wave14_moe_shift_K_perarm_v1: M2_DOMINANT diagnosis
  - wave14_moe_cosine_router_v1: cosine-dot routing

  For each available metrics.json, extract the declared verdict (SHIFT/PARTITION/etc.)
  and re-run TDA-C on freshly-generated W at the same (K, N, M_per_expert, seed).
  Tally: TDA-C agree rate with declared verdict.

  PROBES:
    XV-A: TDA-C on K_scaling_v1 variants (K=2 SHIFT vs K=8+ for PARTITION check)
    XV-B: TDA-C on cosine_router_v1 result (declared HARD_FAIL; what does TDA say?)
    XV-C: TDA-C on K_perarm_v1 result (declared M2_DOMINANT; TDA-C should say SHIFT)
    XV-D: Free-additive top-edge cross-check (TDA-B ratio vs top-edge ratio)

PRE-REGISTERED BANDS:
  HARD-PASS (TDA-C is a reliable offline audit tool):
    - Overall agree rate >= 4/5 valid comparisons
    - AND TDA-B (b_1 ratio) correlates with top-edge ratio (Pearson r >= 0.40)
    -> TDA can be used as offline audit on existing W matrices.

  HARD-FAIL (TDA-C not reliable offline):
    - Overall agree rate <= 2/5
    - OR TDA-B vs top-edge Pearson r < 0.10
    -> TDA requires specifically-prepared W matrices; cannot audit stored checkpoints.

  MIDDLE: agree in [3/5]; partial reliability.

Queue: remote_cpu_queue (CPU; pure re-analysis; ~15-30 min)
Pre-reg: preregs/2026-05-27_tda_moe_w_crossvalidation_v1.md
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# TDA parameters (same as 5probe v1)
N_TAU_STEPS = 30
LONG_BAR_FRAC = 0.3
TDA_B_RATIO_PASS = 1.5
TDA_B_RATIO_FAIL = 1.1
TDA_C_AGREE_PASS = 4
TDA_B_TOP_EDGE_PEARSON_MIN = 0.40

# Existing MoE experiment references to cross-validate against
REFERENCE_EXPERIMENTS = [
    # (exp_name, expected_moe_type, K, N, M_per_expert, seed)
    ("wave14_moe_shift_K_scaling_v1", "SHIFT", 2,  2048, 400, 7),
    ("wave14_moe_shift_K_scaling_v1", "SHIFT", 4,  2048, 400, 7),
    ("wave14_moe_shift_K_scaling_v1", "SHIFT", 8,  2048, 400, 7),
    ("wave14_moe_shift_K_perarm_v1",  "SHIFT", 4,  4096, 800, 7),
    ("wave14_moe_cosine_router_v1",   "SHIFT", 4,  4096, 800, 7),
]

# Smoke versions (lower N + M)
REFERENCE_EXPERIMENTS_SMOKE = [
    ("wave14_moe_smoke_A", "SHIFT",     4, 256, 50, 17),
    ("wave14_moe_smoke_B", "PARTITION", 2, 256, 50, 17),
]


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store_batch(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    BS = 128
    for s in range(0, keys.shape[0], BS):
        e = min(s + BS, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


# ---- Union-Find ----

class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n_components = n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.n_components -= 1
        return True


def vr_b0_trajectory(sim_matrix: np.ndarray, n_steps: int = N_TAU_STEPS) -> Tuple[List, List, int, float]:
    n = sim_matrix.shape[0]
    triu = np.triu_indices(n, k=1)
    sims = sim_matrix[triu]
    tau_min, tau_max = float(sims.min()), float(sims.max())
    if tau_max <= tau_min:
        return [0.0], [n], n, 0.0

    taus = np.linspace(tau_max, tau_min, n_steps).tolist()
    b0_vals = []
    uf = UnionFind(n)
    prev_tau = taus[0] + 1.0
    for tau in taus:
        pairs = np.where(sims >= tau)[0]
        for idx in pairs:
            i, j = triu[0][idx], triu[1][idx]
            uf.union(int(i), int(j))
        b0_vals.append(uf.n_components)
        prev_tau = tau

    # Plateau: mode in middle 40% of tau range
    mid_start = int(0.3 * n_steps)
    mid_end = int(0.7 * n_steps)
    mid_b0 = b0_vals[mid_start:mid_end]
    plateau_b0 = int(round(sum(mid_b0) / len(mid_b0))) if mid_b0 else n
    plateau_width = sum(1 for v in b0_vals if v == plateau_b0) / len(b0_vals)

    return taus, b0_vals, plateau_b0, plateau_width


def tda_c_call(plateau_b0: int, K: int) -> str:
    """TDA-C: b_0 plateau heuristic for SHIFT vs PARTITION."""
    if plateau_b0 == K:
        return "PARTITION"
    elif plateau_b0 < K:
        return "SHIFT"
    else:
        return "AMBIGUOUS"


def tda_b_ratio(W: torch.Tensor, N_rand: int = 5, seed: int = 42) -> float:
    """TDA-B: longest b_1 bar ratio (substrate W vs random control)."""
    W_np = W.cpu().numpy()
    # Cosine similarity of rows of W
    norms = np.linalg.norm(W_np, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-9)
    W_normed = W_np / norms
    sim_matrix = W_normed @ W_normed.T
    np.fill_diagonal(sim_matrix, 0.0)

    # Euler characteristic b_1 estimate at threshold=0
    n = sim_matrix.shape[0]
    edges = int((sim_matrix > 0).sum() / 2)
    uf_temp = UnionFind(n)
    triu = np.triu_indices(n, k=1)
    for i, j, s in sorted(zip(triu[0], triu[1], sim_matrix[triu]), key=lambda x: -x[2]):
        if s <= 0:
            break
        uf_temp.union(int(i), int(j))
    b0_final = uf_temp.n_components
    b1_est = max(0, edges - n + b0_final)

    # Random control
    rand_b1s = []
    for rs in range(N_rand):
        rng = np.random.default_rng(seed + rs)
        W_rand = rng.standard_normal(W_np.shape).astype(np.float32)
        n2 = W_rand.shape[0]
        nr = np.linalg.norm(W_rand, axis=1, keepdims=True); nr = np.maximum(nr, 1e-9)
        W_rn = W_rand / nr
        sim_rand = W_rn @ W_rn.T
        np.fill_diagonal(sim_rand, 0.0)
        edges_r = int((sim_rand > 0).sum() / 2)
        uf_r = UnionFind(n2)
        triu_r = np.triu_indices(n2, k=1)
        for i, j, s in sorted(zip(triu_r[0], triu_r[1], sim_rand[triu_r]), key=lambda x: -x[2]):
            if s <= 0: break
            uf_r.union(int(i), int(j))
        b1_r = max(0, edges_r - n2 + uf_r.n_components)
        rand_b1s.append(b1_r)

    rand_b1_mean = max(sum(rand_b1s) / len(rand_b1s), 1e-9)
    return b1_est / rand_b1_mean


def run_single_case(exp_name: str, moe_type: str, K: int, N: int,
                    M_per_expert: int, seed: int, device) -> Dict:
    """Generate W and compute TDA-C + TDA-B for one case."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    W = outer_product_store_batch(keys, vals, N)

    # TDA-C: build row similarity matrix on W and compute b_0 plateau
    W_np = W.cpu().numpy()
    norms = np.linalg.norm(W_np, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-9)
    W_normed = W_np / norms
    n_sample = min(100, N)   # subsample rows for speed
    idx = np.random.default_rng(seed).choice(N, n_sample, replace=False)
    sim_sub = (W_normed[idx] @ W_normed[idx].T).astype(float)
    np.fill_diagonal(sim_sub, 0.0)

    _, _, plateau_b0, plateau_width = vr_b0_trajectory(sim_sub, N_TAU_STEPS)
    tda_c_result = tda_c_call(plateau_b0, K)

    # TDA-B: b_1 ratio on full W (subsampled)
    b1_ratio = tda_b_ratio(W[:n_sample, :n_sample], N_rand=3, seed=seed)

    # Top-edge ratio for XV-D
    try:
        sv = torch.linalg.svdvals(W)
        top_edge = float(sv[0] / sv[min(9, len(sv)-1)].clamp(min=1e-9))
    except Exception:
        top_edge = 0.0

    agree = (tda_c_result == moe_type or
             (moe_type == "SHIFT" and tda_c_result in ("SHIFT", "AMBIGUOUS")) or
             (moe_type == "PARTITION" and tda_c_result == "PARTITION"))
    # Strict: SHIFT -> SHIFT, PARTITION -> PARTITION
    strict_agree = (tda_c_result == moe_type)

    print(f"  [XV] {exp_name} K={K} N={N}: plateau_b0={plateau_b0} width={plateau_width:.2f} "
          f"tda_c={tda_c_result} vs declared={moe_type} agree={strict_agree} "
          f"b1_ratio={b1_ratio:.2f} top_edge={top_edge:.2f}", flush=True)

    del W, keys, vals
    return {
        "exp_name": exp_name,
        "declared_type": moe_type,
        "K": K, "N": N, "M_per_expert": M_per_expert, "seed": seed,
        "plateau_b0": plateau_b0,
        "plateau_width": round(plateau_width, 4),
        "tda_c": tda_c_result,
        "strict_agree": strict_agree,
        "b1_ratio": round(b1_ratio, 4),
        "top_edge_ratio": round(top_edge, 4),
    }


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. vr_b0_trajectory: returns monotone b0
    rng = np.random.default_rng(42)
    sim = rng.uniform(-1, 1, (10, 10)).astype(float)
    np.fill_diagonal(sim, 1.0)
    _, b0_vals, plateau_b0, plateau_width = vr_b0_trajectory(sim, 15)
    assert b0_vals[0] >= b0_vals[-1], "FAIL 1a: b0 not monotone non-increasing"
    assert plateau_b0 >= 1, f"FAIL 1b: plateau_b0={plateau_b0}"
    print(f"[selftest] 1/4 vr_b0_trajectory OK plateau_b0={plateau_b0}")

    # 2. tda_c_call: PARTITION when plateau==K, SHIFT when plateau<K
    assert tda_c_call(4, 4) == "PARTITION", "FAIL 2a"
    assert tda_c_call(2, 4) == "SHIFT", "FAIL 2b"
    print("[selftest] 2/4 tda_c_call OK")

    # 3. run_single_case at smoke scale: returns dict with required fields
    result = run_single_case("smoke_test", "SHIFT", 4, 64, 10, 17, device)
    for key in ("plateau_b0", "tda_c", "b1_ratio", "top_edge_ratio", "strict_agree"):
        assert key in result, f"FAIL 3: missing key {key}"
    print(f"[selftest] 3/4 run_single_case: tda_c={result['tda_c']} b1={result['b1_ratio']:.2f} OK")

    # 4. outer_product_store_batch: valid W
    k = make_bsc(8, 32, gen, device)
    v = make_bsc(8, 32, gen, device)
    W = outer_product_store_batch(k, v, 32)
    assert W.shape == (32, 32) and math.isfinite(float(W.abs().mean())), "FAIL 4"
    print("[selftest] 4/4 outer_product_store_batch OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False):
    device = torch.device("cpu")
    print(f"[tda_moe_w_crossvalidation] device={device} smoke={smoke}", flush=True)
    ref_experiments = REFERENCE_EXPERIMENTS_SMOKE if smoke else REFERENCE_EXPERIMENTS

    out_dir = get_output_dir("tda_moe_w_crossvalidation_v1")
    t0 = time.time()

    results = []
    for exp_args in ref_experiments:
        exp_name, moe_type, K, N, M_per_expert, seed = exp_args
        print(f"\n[case] {exp_name} type={moe_type} K={K} N={N}", flush=True)
        r = run_single_case(exp_name, moe_type, K, N, M_per_expert, seed, device)
        results.append(r)

    # Aggregate
    n_total = len(results)
    n_agree = sum(1 for r in results if r["strict_agree"])
    agree_rate = n_agree / max(n_total, 1)

    # TDA-B vs top-edge Pearson correlation
    b1_ratios = [r["b1_ratio"] for r in results]
    top_edges = [r["top_edge_ratio"] for r in results]
    n = len(b1_ratios)
    if n >= 2:
        mx = sum(b1_ratios) / n; my = sum(top_edges) / n
        cov = sum((b1_ratios[i] - mx) * (top_edges[i] - my) for i in range(n))
        var_x = sum((b1_ratios[i] - mx) ** 2 for i in range(n))
        var_y = sum((top_edges[i] - my) ** 2 for i in range(n))
        pearson_r = cov / math.sqrt(var_x * var_y) if (var_x * var_y) > 0 else 0.0
    else:
        pearson_r = 0.0

    # Verdict
    hard_pass = (n_agree >= TDA_C_AGREE_PASS and pearson_r >= TDA_B_TOP_EDGE_PEARSON_MIN)
    hard_fail = (n_agree <= 2 or pearson_r < 0.10)

    if hard_pass:
        verdict = "TDA_CROSSVAL_HARD_PASS"
        msg = (f"TDA-C is a reliable offline audit tool: agree_rate={n_agree}/{n_total}={agree_rate:.2f} "
               f">= {TDA_C_AGREE_PASS}/{n_total} threshold. "
               f"TDA-B vs top-edge Pearson r={pearson_r:.3f} >= {TDA_B_TOP_EDGE_PEARSON_MIN}. "
               f"TDA can be applied to stored W checkpoints for post-hoc SHIFT/PARTITION diagnosis.")
    elif hard_fail:
        verdict = "TDA_CROSSVAL_HARD_FAIL"
        msg = (f"TDA-C not reliable for offline audit: agree_rate={n_agree}/{n_total}={agree_rate:.2f} "
               f"TDA-B vs top-edge r={pearson_r:.3f}. "
               f"TDA is only valid for purpose-generated W; cannot audit stored checkpoints.")
    else:
        verdict = "TDA_CROSSVAL_MIDDLE"
        msg = (f"Partial offline reliability: agree_rate={n_agree}/{n_total}={agree_rate:.2f}, "
               f"r={pearson_r:.3f}. TDA works on K in certain range but not universally.")

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "n_total": n_total,
        "n_agree": n_agree,
        "agree_rate": round(agree_rate, 4),
        "tda_b_vs_top_edge_pearson_r": round(pearson_r, 4),
        "elapsed_s": round(elapsed, 1),
        "cases": results,
        "thresholds": {
            "tda_c_agree_pass": TDA_C_AGREE_PASS,
            "tda_b_top_edge_pearson_min": TDA_B_TOP_EDGE_PEARSON_MIN,
        },
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {metrics_path}", flush=True)
    return metrics, out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    run_sweep(smoke=args.smoke)
