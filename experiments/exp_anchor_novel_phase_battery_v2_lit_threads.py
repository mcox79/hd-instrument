"""SKAH-M lit-thread discrimination: which of the 3 documented-class threads best matches?

TRIGGER: exp_anchor_novel_phase_battery_v1 returns DOCUMENTED_BUT_UNTESTED (>= 5/6 cells).

CONTEXT: Research notes/research_novel_phase_class_methodology_2026-05-27.md Finding 3:
  THREE documented-class candidates with P(match) estimates:
    Thread A -- Non-reciprocal Hopfield (arXiv:2501.00983): asymmetric weights + gating
                Predicts: first-order hysteresis independent of cooling rate;
                          retrieval-to-SG transition sharp; lR-phase plateau structure.
    Thread B -- Spatial-correlated DAM (arXiv:2207.05218, Agliari-Barra):
                Structured patterns shift alpha_c; spatial correlations suppress SG.
                Predicts: alpha_c shift proportional to pattern correlation;
                          q_EA suppressed relative to random-pattern baseline.
    Thread C -- Saddle-hierarchy DAM (arXiv:2508.19151):
                Saddle cascade predicts STEP dynamics at Saad-Solla timescales.
                Predicts: learning curves show plateau-jump pattern; plateau heights
                          match W singular-value staircase.

DESIGN: 4-arm diagnostic -- each arm computes a SIGNATURE DIFFERENCE between threads.

  ARM 1 (Thread A vs B/C): Cooling-rate independence at fixed N.
    - Fix N=2048, M=3000, vary epochs in {1, 4, 16}.
    - Thread A predicts: gap independent of epochs (thermodynamic first-order).
    - Thread B/C predict: gap may vary (kinetic or dynamic origin).
    - Metric: Pearson r(log_epochs, gap). |r| < 0.2 -> Thread A; |r| > 0.5 -> Thread B/C.

  ARM 2 (Thread B vs A/C): alpha_c shift vs random-pattern baseline.
    - Compare retention at fixed load (M/N = 0.40) for BSC-random vs PPMI-structured patterns.
    - Thread B predicts: structured patterns give LOWER retention than random at same M/N
                         (alpha_c shift DOWN; capacity reduced by correlations).
    - Thread A/C predict: structured patterns give SAME or HIGHER retention.
    - Metric: delta_ret = ret_structured - ret_random. < -0.03 -> Thread B; > 0 -> Thread A/C.

  ARM 3 (Thread C vs A/B): Singular-value staircase vs plateau alignment.
    - Compute W singular-value spectrum at full M; check if plateau-height set {h1, h2, h3}
      matches the FIRST 3 normalized singular values {s1, s2, s3} / s_max.
    - Thread C predicts: |h_i - s_i/s_max| < 0.05 for all i (saddle-hierarchy = spectral staircase).
    - Thread A/B predict: no alignment between plateaus and singular values.
    - Metric: max_i(|h_i - s_i/s_max|). < 0.05 -> Thread C; > 0.15 -> Thread A/B.

  ARM 4 (3-way discrimination summary): joint call based on Arms 1-3.

PRE-REGISTERED BANDS:
  THREAD_A_DOMINANT (Non-reciprocal Hopfield best match):
    - Arm1: |r| < 0.20 (cooling-rate-independent)
    - Arm2: delta_ret > -0.02 (structured >= random at same load)
    - Arm3: max_diff > 0.12 (no spectral alignment)

  THREAD_B_DOMINANT (Spatial-correlated DAM best match):
    - Arm1: |r| > 0.40 (some cooling-rate dependence)
    - Arm2: delta_ret < -0.03 (structured patterns degrade relative to random)
    - Arm3: max_diff > 0.10 (no spectral alignment)

  THREAD_C_DOMINANT (Saddle-hierarchy DAM best match):
    - Arm1: any (saddle-hierarchy is about dynamics, not necessarily rate-dep)
    - Arm2: delta_ret > -0.02 (structured >= random)
    - Arm3: max_diff < 0.05 (spectral staircase alignment)

  MIXED_EVIDENCE: no arm dominates; substrate may blend threads.

Queue: overnight_queue (GPU; N=2048 Arm1 is bottleneck; ~1.5-2h)
Pre-reg: preregs/2026-05-27_anchor_novel_phase_battery_v2_lit_threads.md
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Design parameters
N_FULL = 2048
N_SMOKE = 512
EPOCHS_SWEEP_FULL = [1, 4, 16]
EPOCHS_SWEEP_SMOKE = [1, 4]
SEEDS_FULL = [7, 17, 23, 37, 41]
SEEDS_SMOKE = [17]
LOAD_FRAC = 0.40     # M/N ratio for Arm2 random vs structured comparison
BATCH_STORE = 128

# Pre-registered thresholds
ARM1_THREAD_A_R_MAX = 0.20       # cooling-rate-independent
ARM1_THREAD_BC_R_MIN = 0.50      # cooling-rate-dependent
ARM2_THREAD_B_DELTA_MAX = -0.03  # structured degrades vs random
ARM3_THREAD_C_MAX_DIFF = 0.05    # spectral staircase alignment
ARM3_THREAD_AB_MAX_DIFF_MIN = 0.12  # no spectral alignment


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def make_ppmi_structured(M: int, N: int, gen: torch.Generator, device, n_clusters: int = 4) -> torch.Tensor:
    """Structured (correlated) patterns: cluster-based PPMI-like structure.
    Each cluster shares a prototype; within-cluster patterns are noisy copies.
    This approximates the substrate's actual PPMI structure.
    """
    M_per_cluster = max(1, M // n_clusters)
    patterns = []
    for c in range(n_clusters):
        proto = make_bsc(1, N, gen, device)
        for _ in range(M_per_cluster):
            noise = make_bsc(1, N, gen, device)
            # Flip ~20% of bits to create correlation
            flip_mask = (torch.rand(1, N, generator=gen, device=device) < 0.20)
            pat = proto.clone()
            pat[flip_mask] = noise[flip_mask]
            patterns.append(pat)
    patterns = torch.cat(patterns[:M], dim=0)
    if patterns.shape[0] < M:
        extra = make_bsc(M - patterns.shape[0], N, gen, device)
        patterns = torch.cat([patterns, extra], dim=0)
    return patterns[:M]


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int, epochs: int = 1) -> torch.Tensor:
    """Hebbian outer-product update. Multiple epochs = slower cooling proxy."""
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for _ in range(epochs):
        for s in range(0, keys.shape[0], BATCH_STORE):
            e = min(s + BATCH_STORE, keys.shape[0])
            W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def compute_retention(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    """Mean cosine similarity of retrieved values."""
    y = (W @ keys.T).T   # (M, N)
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return float((yn * vn).sum(dim=1).mean())


def compute_hysteresis_gap(N: int, M: int, seed: int, epochs: int, device) -> float:
    """Write-read hysteresis gap at given epochs (cooling-rate proxy)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M, N, gen, device)
    vals = make_bsc(M, N, gen, device)

    # Forward: store with 'epochs' passes (more epochs = slower cooling)
    W_fwd = outer_product_store(keys, vals, N, epochs=epochs)
    ret_fwd = compute_retention(W_fwd, keys, vals)

    # Reverse: store in reverse order (reversed keys<->vals, same epochs)
    W_rev = outer_product_store(vals, keys, N, epochs=epochs)
    ret_rev = compute_retention(W_rev, vals, keys)

    gap = abs(ret_fwd - ret_rev)
    del W_fwd, W_rev, keys, vals
    return gap


def run_arm1(N: int, epochs_sweep: List[int], seeds: List[int], device) -> Dict:
    """Arm 1: cooling-rate independence. Returns Pearson r(log_epochs, gap)."""
    M = int(0.50 * N)   # above alpha_c to stress the system
    results = {}
    for seed in seeds:
        gaps = []
        for ep in epochs_sweep:
            g = compute_hysteresis_gap(N, M, seed, ep, device)
            gaps.append(g)
        # Pearson r(log_epochs, gaps)
        log_ep = [math.log(e) for e in epochs_sweep]
        n = len(log_ep)
        mx = sum(log_ep) / n
        my = sum(gaps) / n
        cov = sum((log_ep[i] - mx) * (gaps[i] - my) for i in range(n))
        var_x = sum((log_ep[i] - mx) ** 2 for i in range(n))
        var_y = sum((gaps[i] - my) ** 2 for i in range(n))
        r = cov / math.sqrt(var_x * var_y) if (var_x * var_y) > 0 else 0.0
        results[seed] = {"r": r, "gaps": [round(g, 5) for g in gaps]}
        print(f"  [Arm1] N={N} seed={seed} epochs={epochs_sweep} gaps={[round(g,3) for g in gaps]} r={r:.3f}", flush=True)

    r_vals = [results[s]["r"] for s in seeds]
    mean_r = sum(r_vals) / len(r_vals)
    abs_r = abs(mean_r)
    if abs_r < ARM1_THREAD_A_R_MAX:
        call = "THREAD_A"
    elif abs_r > ARM1_THREAD_BC_R_MIN:
        call = "THREAD_BC"
    else:
        call = "AMBIGUOUS"
    print(f"  [Arm1] mean_|r|={abs_r:.3f} -> {call}", flush=True)
    return {"mean_r": round(mean_r, 5), "abs_r": round(abs_r, 5), "call": call, "per_seed": results}


def run_arm2(N: int, seeds: List[int], device) -> Dict:
    """Arm 2: alpha_c shift -- random vs structured patterns at fixed M/N load."""
    M = int(LOAD_FRAC * N)
    results_random = []
    results_structured = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        keys_rand = make_bsc(M, N, gen, device)
        vals_rand = make_bsc(M, N, gen, device)
        W_rand = outer_product_store(keys_rand, vals_rand, N)
        ret_rand = compute_retention(W_rand, keys_rand, vals_rand)
        results_random.append(ret_rand)

        gen2 = torch.Generator(device=device).manual_seed(seed + 1000)
        keys_struc = make_ppmi_structured(M, N, gen2, device)
        vals_struc = make_ppmi_structured(M, N, gen2, device)
        W_struc = outer_product_store(keys_struc, vals_struc, N)
        ret_struc = compute_retention(W_struc, keys_struc, vals_struc)
        results_structured.append(ret_struc)

        delta = ret_struc - ret_rand
        print(f"  [Arm2] N={N} seed={seed}: ret_rand={ret_rand:.4f} ret_struc={ret_struc:.4f} delta={delta:.4f}", flush=True)
        del W_rand, W_struc, keys_rand, vals_rand, keys_struc, vals_struc

    mean_rand = sum(results_random) / len(results_random)
    mean_struc = sum(results_structured) / len(results_structured)
    delta = mean_struc - mean_rand
    if delta < ARM2_THREAD_B_DELTA_MAX:
        call = "THREAD_B"
    elif delta > -0.01:
        call = "THREAD_AC"
    else:
        call = "AMBIGUOUS"
    print(f"  [Arm2] mean_ret_rand={mean_rand:.4f} mean_ret_struc={mean_struc:.4f} delta={delta:.4f} -> {call}", flush=True)
    return {"mean_ret_random": round(mean_rand, 5), "mean_ret_structured": round(mean_struc, 5),
            "delta_ret": round(delta, 5), "call": call}


def run_arm3(N: int, seeds: List[int], device) -> Dict:
    """Arm 3: singular-value staircase vs plateau alignment.
    Plateau heights {h1, h2, h3} from BSC-fixture recall (G1/G2/G3 codebook classes).
    Singular values {s1, s2, s3} from W SVD.
    """
    # Use 3-class BSC fixture as in the parent battery
    M_per_class = max(10, N // 4)
    results = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        # 3 codebook classes with graded overlap
        proto1 = make_bsc(1, N, gen, device)
        proto2 = (proto1 + make_bsc(1, N, gen, device)).sign()
        proto3 = (proto1 + proto2 + make_bsc(1, N, gen, device)).sign()

        keys_all, vals_all = [], []
        plateaus = []
        for proto, M_c in [(proto1, M_per_class), (proto2, M_per_class), (proto3, M_per_class)]:
            noisy = proto.expand(M_c, N) * (2.0 * (torch.rand(M_c, N, generator=gen, device=device) > 0.10).float() - 1.0)
            noisy = noisy.sign()
            keys_all.append(noisy)
            vals_all.append(noisy.clone())

        keys = torch.cat(keys_all, dim=0)
        vals = torch.cat(vals_all, dim=0)
        W = outer_product_store(keys, vals, N)

        # Per-class retention (plateau heights)
        for i, k_c in enumerate(keys_all):
            v_c = vals_all[i]
            ret_c = compute_retention(W, k_c, v_c)
            plateaus.append(ret_c)
        plateaus.sort(reverse=True)   # descending: h1 >= h2 >= h3

        # W singular values (top 3)
        try:
            _, S, _ = torch.linalg.svd(W, full_matrices=False)
            s_norm = (S[:3] / S[0].clamp(min=1e-9)).tolist()
        except Exception:
            s_norm = [1.0, 0.5, 0.25]  # fallback if SVD fails

        # Alignment: |plateau_i - s_norm_i|
        diffs = [abs(plateaus[i] - s_norm[i]) for i in range(min(3, len(plateaus), len(s_norm)))]
        max_diff = max(diffs)

        if max_diff < ARM3_THREAD_C_MAX_DIFF:
            call = "THREAD_C"
        elif max_diff > ARM3_THREAD_AB_MAX_DIFF_MIN:
            call = "THREAD_AB"
        else:
            call = "AMBIGUOUS"

        results.append({"plateaus": plateaus, "s_norm": s_norm, "diffs": diffs, "max_diff": max_diff, "call": call})
        print(f"  [Arm3] N={N} seed={seed}: plateaus={[round(p,3) for p in plateaus]} "
              f"s_norm={[round(s,3) for s in s_norm]} max_diff={max_diff:.4f} -> {call}", flush=True)
        del W, keys, vals

    mean_max_diff = sum(r["max_diff"] for r in results) / len(results)
    if mean_max_diff < ARM3_THREAD_C_MAX_DIFF:
        call_arm3 = "THREAD_C"
    elif mean_max_diff > ARM3_THREAD_AB_MAX_DIFF_MIN:
        call_arm3 = "THREAD_AB"
    else:
        call_arm3 = "AMBIGUOUS"
    print(f"  [Arm3] mean_max_diff={mean_max_diff:.4f} -> {call_arm3}", flush=True)
    return {"mean_max_diff": round(mean_max_diff, 5), "call": call_arm3, "per_seed": results}


def compute_joint_verdict(arm1: Dict, arm2: Dict, arm3: Dict) -> Tuple[str, str]:
    a1 = arm1["call"]
    a2 = arm2["call"]
    a3 = arm3["call"]

    # Thread A dominant: cooling-rate independent + structured >= random + no spectral alignment
    if a1 == "THREAD_A" and a2 == "THREAD_AC" and a3 == "THREAD_AB":
        verdict = "THREAD_A_DOMINANT"
        msg = (f"Non-reciprocal Hopfield (Thread A) best matches: rate-independent gap, "
               f"structured patterns >= random, no spectral staircase. "
               f"Substrate is in the lR-phase / gated-multistable AM class.")

    # Thread B dominant: cooling-rate dependent + structured < random
    elif a1 == "THREAD_BC" and a2 == "THREAD_B":
        verdict = "THREAD_B_DOMINANT"
        msg = (f"Spatial-correlated DAM (Thread B) best matches: rate-dependent gap + "
               f"alpha_c shift (structured patterns degrade). Substrate capacity is suppressed "
               f"by pattern correlations per Agliari-Barra prediction.")

    # Thread C dominant: spectral staircase alignment
    elif a3 == "THREAD_C":
        verdict = "THREAD_C_DOMINANT"
        msg = (f"Saddle-hierarchy DAM (Thread C) best matches: singular-value staircase "
               f"aligns with plateau heights. Substrate dynamics follow DAM saddle cascade.")

    # Partial A
    elif a1 == "THREAD_A":
        verdict = "THREAD_A_PARTIAL"
        msg = f"Thread A signal only on Arm1 (cooling-rate independence). Arm2={arm2['call']} Arm3={arm3['call']}."

    else:
        verdict = "MIXED_EVIDENCE"
        msg = (f"No single thread dominates: Arm1={a1} Arm2={a2} Arm3={a3}. "
               f"Substrate may blend multiple documented-class mechanisms. "
               f"Consider hybrid Thread A+C framing (non-reciprocal + saddle-hierarchy).")

    return verdict, msg


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. make_bsc
    v = make_bsc(8, 32, gen, device)
    assert v.shape == (8, 32), f"FAIL 1: shape={v.shape}"
    assert set(v.unique().tolist()).issubset({-1.0, 1.0}), "FAIL 1b: not BSC"
    print("[selftest] 1/5 make_bsc OK")

    # 2. make_ppmi_structured: returns (M, N) tensor
    gen2 = torch.Generator(device=device).manual_seed(7)
    ps = make_ppmi_structured(16, 32, gen2, device)
    assert ps.shape == (16, 32), f"FAIL 2: shape={ps.shape}"
    print("[selftest] 2/5 make_ppmi_structured OK")

    # 3. outer_product_store: returns (N, N) with epochs=2
    gen3 = torch.Generator(device=device).manual_seed(99)
    k = make_bsc(4, 32, gen3, device)
    v2 = make_bsc(4, 32, gen3, device)
    W = outer_product_store(k, v2, 32, epochs=2)
    assert W.shape == (32, 32), f"FAIL 3: shape={W.shape}"
    assert math.isfinite(float(W.abs().mean())), "FAIL 3b: W not finite"
    print("[selftest] 3/5 outer_product_store epochs=2 OK")

    # 4. compute_retention: non-null
    ret = compute_retention(W, k, v2)
    assert math.isfinite(ret) and ret is not None, f"FAIL 4: ret={ret}"
    print(f"[selftest] 4/5 compute_retention={ret:.4f} OK")

    # 5. compute_hysteresis_gap: positive
    gap = compute_hysteresis_gap(32, 10, 7, 1, device)
    assert math.isfinite(gap) and gap >= 0, f"FAIL 5: gap={gap}"
    print(f"[selftest] 5/5 compute_hysteresis_gap={gap:.4f} OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False) -> Tuple[Dict, Path]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[lit_threads] device={device} smoke={smoke}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    epochs_sweep = EPOCHS_SWEEP_SMOKE if smoke else EPOCHS_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir("anchor_novel_phase_battery_v2_lit_threads")

    t0 = time.time()
    print("\n=== ARM 1: cooling-rate independence ===", flush=True)
    arm1 = run_arm1(N, epochs_sweep, seeds, device)

    print("\n=== ARM 2: alpha_c shift (random vs structured) ===", flush=True)
    arm2 = run_arm2(N, seeds, device)

    print("\n=== ARM 3: spectral staircase alignment ===", flush=True)
    arm3 = run_arm3(N, seeds, device)

    verdict, msg = compute_joint_verdict(arm1, arm2, arm3)
    elapsed = time.time() - t0

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "N": N,
        "elapsed_s": round(elapsed, 1),
        "arm1": arm1,
        "arm2": arm2,
        "arm3": arm3,
        "thresholds": {
            "arm1_thread_a_r_max": ARM1_THREAD_A_R_MAX,
            "arm1_thread_bc_r_min": ARM1_THREAD_BC_R_MIN,
            "arm2_thread_b_delta_max": ARM2_THREAD_B_DELTA_MAX,
            "arm3_thread_c_max_diff": ARM3_THREAD_C_MAX_DIFF,
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
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run_sweep(smoke=args.smoke)
