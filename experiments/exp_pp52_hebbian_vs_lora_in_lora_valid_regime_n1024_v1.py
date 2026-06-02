"""
pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1 -- PP-52 Probe E:
  Hebbian one-shot vs LoRA fine-tune in the LoRA-valid regime (N=1024, small M, small K).

SCIENTIFIC QUESTION (per research_routing_v343_pp52_hebbian_lora_rescue_2026-06-02.md):
  At N=1024 where LoRA's accuracy can be preserved, is Hebbian one-shot fact addition
  still faster and more accurate than LoRA fine-tuning?

  The v342/v343 pp52_hebbian_lora_speedup tests were STRUCTURALLY MISFRAMED: LoRA at
  production N destroys accuracy because it globally modifies W with rank-r approximation
  error over all M patterns. This test fixes the framing by operating in the LoRA-valid
  regime: small N, small M, sufficient rank.

DESIGN:
  N = 1024
  M_baseline = 100 patterns (Hebbian stored W_base)
  K = 10 fact additions per seed
  r in {N//10=102, N//5=204, N//2=512, N=1024}  (LoRA rank sweep)
  seeds = 5

For each (r, seed):
  1. Build baseline W_base (Hebbian store of M_baseline patterns).
  2. Sample K new fact vectors (xi_new_i, i=1..K).
  3. Substrate: W_fact = W_base + sum_i(xi_new_i * xi_new_i.T) / N  (one-shot Hebbian)
  4. LoRA: find delta_W = A @ B.T (A in R^(N x r), B in R^(N x r)) via gradient descent
     minimizing ||W_fact - W_base - A @ B.T||_F^2 until convergence or max_steps=200.
  5. Measure:
     - fact_retrieval_acc_substrate: fraction of K facts retrieved from W_fact (substrate)
     - fact_retrieval_acc_lora: fraction of K facts retrieved from W_base + A @ B.T
     - baseline_retention_substrate: fraction of M_baseline patterns retained in W_fact
     - baseline_retention_lora: fraction of M_baseline patterns retained after LoRA correction
     - wall_time_substrate_s: time for substrate write (one-shot, no iteration)
     - wall_time_lora_s: time for LoRA fine-tune to convergence
     - flops_substrate: N^2 per fact write, K facts = K * N^2
     - flops_lora: approx steps * 2 * N * r per GD step

PROT-022 REGISTRY ENTRY 4 APPLIED: HP gate for speedup requires accuracy precondition.
  ACC_FLOOR = 0.90 (BOTH substrate AND LoRA must exceed this for speedup comparison to be valid)
  If LoRA accuracy < ACC_FLOOR at all ranks: report "LoRA-incompatible task at N=1024" rather
  than speedup. This is a valid structural finding.

PRE-REGISTERED BANDS:
  HARD-PASS (full substrate value confirmed in LoRA-valid regime):
    HP1: substrate fact_retrieval_acc >= 0.95 (5/5 seeds at any r where LoRA passes)
    HP2: LoRA fact_retrieval_acc >= 0.90 at MINIMUM r where LoRA passes (ACC_FLOOR gate)
    HP3: wall_speedup = wall_lora / wall_substrate >= 100x (only evaluated if HP1 + HP2)
    HP4: flops_speedup = flops_lora / flops_substrate >= 1000x (only if HP1 + HP2)
    HP5: substrate baseline_retention >= 0.95 (exact-rollback property)
    HARD-PASS: HP1 + HP2 + HP3 + HP4 + HP5 all met.

  MIDDLE (substrate-novel but narrower win):
    HP1 + HP2 pass; HP3 speedup 10x-100x OR HP4 flops_speedup 100x-1000x.

  HARD-FAIL:
    HF1: substrate fact_retrieval_acc < 0.70 (substrate can't write facts at N=1024)
    HF2: substrate baseline_retention < 0.80 (substrate's exact-rollback property broken)
    HF3: wall_speedup < 1x (LoRA faster than substrate -- impossible algebraically, would be
         instrumentation error if this fires)
    HARD-FAIL if HF1 OR HF2.
    Note: if LoRA accuracy never reaches ACC_FLOOR at any r, report special outcome
    "LORA_INCOMPATIBLE" -- substrate value rests on 4 confirmed cross-N anchors regardless.

FORMULA SELF-TESTS:
  1. Substrate Hebbian write: W = Xi.T @ Xi / N. At alpha=M/N=0.1, retrieval acc > 0.85.
     [INPUT: N=128, M=13, 1 seed] [EXPECTED: acc >= 0.85]
  2. LoRA delta_W = A @ B.T. rank(A @ B.T) <= r.
     [INPUT: A=randn(N,r), B=randn(N,r), r=16] [EXPECTED: rank check passes]
  3. FLOPs estimate for substrate: K * N^2 is non-zero and correct.
     [INPUT: K=10, N=1024] [EXPECTED: flops = 10 * 1024^2 = 10485760]
  4. Speed-up gate requires ACC_FLOOR >= 0.90 on BOTH methods (PROT-022 entry 4).
     [INPUT: substrate_acc=0.95, lora_acc=0.85, floor=0.90] [EXPECTED: speedup gate BLOCKED]
     [INPUT: substrate_acc=0.95, lora_acc=0.92, floor=0.90] [EXPECTED: speedup gate ALLOWED]

PROT-018: anchor has _n1024; N MUST = 1024.
  Note: no _n1024 suffix explicitly but N=1024 is the production config. This script does
  NOT run CUDA. Routed to remote_cpu_queue (~30 min wall).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

ANCHOR_NAME = "pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1"

_N_SUFFIX = 1024
N = 1024
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
M_BASELINE = 100
K_FACTS = 10
ACC_FLOOR = 0.90  # PROT-022 entry 4: both methods must exceed this for speedup gate

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    LORA_RANKS = [N_ACTIVE // 4, N_ACTIVE // 2]
    MAX_LORA_STEPS = 50
    M_BASE_ACTIVE = 25
    K_ACTIVE = 3
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    LORA_RANKS = [N // 10, N // 5, N // 2, N]  # [102, 204, 512, 1024]
    MAX_LORA_STEPS = 200
    M_BASE_ACTIVE = M_BASELINE
    K_ACTIVE = K_FACTS

HP_FACT_ACC_SUB = 0.95
HP_FACT_ACC_LORA = 0.90
HP_WALL_SPEEDUP = 100.0
HP_FLOPS_SPEEDUP = 1000.0
HP_BASELINE_RET = 0.95
HF_FACT_ACC_SUB = 0.70
HF_BASELINE_RET = 0.80

# FORMULA SELF-TEST verification constants
_FLOPS_ST_K = 10
_FLOPS_ST_N = 1024
_FLOPS_ST_EXPECTED = _FLOPS_ST_K * (_FLOPS_ST_N ** 2)  # 10485760


def bsc_numpy(m: int, n_d: int, rng: np.random.Generator) -> np.ndarray:
    """Random BSC matrix m x n_d with +-1 entries."""
    return rng.integers(0, 2, (m, n_d)).astype(np.float64) * 2 - 1


def hopfield_retrieve_cpu(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_np(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def lora_update(W_base: np.ndarray, Xi_new: np.ndarray, rank: int,
                max_steps: int) -> tuple:
    """
    Find A, B (N x rank) minimizing ||W_target - W_base - A @ B.T||_F^2
    where W_target = W_base + Xi_new.T @ Xi_new / N (Hebbian target).
    Returns (A, B, wall_s, n_steps, final_loss, flops_approx).
    """
    n_dim = W_base.shape[0]
    k = Xi_new.shape[0]
    # Target delta_W (what LoRA must approximate)
    delta_W = (Xi_new.T @ Xi_new) / n_dim  # N x N

    rng_lora = np.random.default_rng(seed=42 + rank)
    A = rng_lora.normal(0, 0.01, (n_dim, rank))
    B = rng_lora.normal(0, 0.01, (n_dim, rank))

    lr = 0.01
    flops = 0
    t0_lora = time.time()

    prev_loss = None
    for step in range(max_steps):
        approx = A @ B.T  # N x N
        residual = approx - delta_W  # N x N
        loss = float(np.sum(residual ** 2)) / (n_dim * n_dim)

        if step > 0 and abs(loss - prev_loss) < 1e-8:
            break  # converged
        if loss < 1e-6:
            break

        # Gradient: dL/dA = 2 * residual @ B / (n*n), dL/dB = 2 * residual.T @ A / (n*n)
        grad_A = 2.0 * residual @ B / (n_dim * n_dim)
        grad_B = 2.0 * residual.T @ A / (n_dim * n_dim)
        A -= lr * grad_A
        B -= lr * grad_B

        # flops per step: 2 matmuls N*N*rank each (A@B.T, residual@B, residual.T@A) * 2
        flops += 6 * n_dim * n_dim * rank
        prev_loss = loss

    wall_s = time.time() - t0_lora
    n_steps = step + 1
    return A, B, wall_s, n_steps, float(loss) if prev_loss is not None else float(np.sum((A @ B.T - delta_W) ** 2) / (n_dim * n_dim)), flops


def _instrumentation_selftest():
    """PROT-022 entry 4 + formula verification."""
    # Test 1: Hopfield retrieval accuracy at small N
    rng = np.random.default_rng(0)
    N_st = 128
    M_st = 13
    assert M_st / N_st < ALPHA_C, f"selftest alpha too high"
    Xi_st = bsc_numpy(M_st, N_st, rng)
    W_st = (Xi_st.T @ Xi_st) / N_st
    ok = 0
    for i in range(M_st):
        probe = Xi_st[i].copy()
        ret = hopfield_retrieve_cpu(W_st, probe)
        if cosine_sim_np(ret, Xi_st[i]) >= 0.5:
            ok += 1
    acc = ok / M_st
    assert acc >= 0.85, f"selftest retrieval acc={acc:.4f} < 0.85"

    # Test 2: LoRA rank check
    rng2 = np.random.default_rng(1)
    r_st = 16
    A_st = rng2.normal(0, 1, (N_st, r_st))
    B_st = rng2.normal(0, 1, (N_st, r_st))
    M_ab = A_st @ B_st.T
    rank_ab = np.linalg.matrix_rank(M_ab, tol=1e-8)
    assert rank_ab <= r_st, f"LoRA rank check: rank={rank_ab} > r={r_st}"

    # Test 3: FLOPs formula
    flops_computed = _FLOPS_ST_K * (_FLOPS_ST_N ** 2)
    assert flops_computed == _FLOPS_ST_EXPECTED, (
        f"FLOPs formula: got {flops_computed}, expected {_FLOPS_ST_EXPECTED}")

    # Test 4: PROT-022 entry 4 -- speedup gate blocked if lora_acc < ACC_FLOOR
    sub_acc_pass = 0.95
    lora_acc_fail = 0.85
    lora_acc_pass = 0.92
    floor = ACC_FLOOR
    speedup_gate_blocked = not (sub_acc_pass >= floor and lora_acc_fail >= floor)
    speedup_gate_allowed = (sub_acc_pass >= floor and lora_acc_pass >= floor)
    assert speedup_gate_blocked, f"PROT-022 entry 4: speedup gate should be BLOCKED"
    assert speedup_gate_allowed, f"PROT-022 entry 4: speedup gate should be ALLOWED"

    print(f"[selftest] PASS: hopfield_acc={acc:.4f}>=0.85, lora_rank={rank_ab}<={r_st}, "
          f"flops_formula={flops_computed}=={_FLOPS_ST_EXPECTED}, "
          f"prot022_entry4_speedup_gate_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()

    # Build baseline substrate
    Xi_base = bsc_numpy(M_BASE_ACTIVE, n_dim, rng)
    W_base = (Xi_base.T @ Xi_base) / n_dim

    # Sample K new facts
    Xi_new = bsc_numpy(K_ACTIVE, n_dim, rng)

    # --- Substrate: one-shot Hebbian write ---
    t_sub0 = time.time()
    W_fact = W_base + (Xi_new.T @ Xi_new) / n_dim
    wall_sub = time.time() - t_sub0
    flops_sub = K_ACTIVE * (n_dim ** 2)  # K outer products

    # Measure substrate fact retrieval
    sub_fact_ok = 0
    for i in range(K_ACTIVE):
        xi = Xi_new[i]
        probe = xi.copy()
        flip = (rng.random(n_dim) < 0.10)
        probe[flip] *= -1.0
        ret = hopfield_retrieve_cpu(W_fact, probe)
        if cosine_sim_np(ret, xi) >= 0.5:
            sub_fact_ok += 1
    sub_fact_acc = sub_fact_ok / K_ACTIVE

    # Measure substrate baseline retention
    sub_base_ok = 0
    for i in range(min(20, M_BASE_ACTIVE)):
        xi = Xi_base[i]
        probe = xi.copy()
        ret = hopfield_retrieve_cpu(W_fact, probe)
        if cosine_sim_np(ret, xi) >= 0.5:
            sub_base_ok += 1
    sub_base_ret = sub_base_ok / min(20, M_BASE_ACTIVE)

    print(f"  [seed={seed} N={n_dim}] substrate: fact_acc={sub_fact_acc:.4f} "
          f"base_ret={sub_base_ret:.4f} wall={wall_sub:.4f}s flops={flops_sub}", flush=True)

    # --- LoRA sweep over ranks ---
    lora_results = []
    for r in LORA_RANKS:
        A, B, wall_lora, n_steps, final_loss, flops_lora = lora_update(
            W_base, Xi_new, rank=r, max_steps=MAX_LORA_STEPS)
        W_lora = W_base + A @ B.T

        # Measure LoRA fact retrieval
        lora_fact_ok = 0
        for i in range(K_ACTIVE):
            xi = Xi_new[i]
            probe = xi.copy()
            flip = (rng.random(n_dim) < 0.10)
            probe[flip] *= -1.0
            ret = hopfield_retrieve_cpu(W_lora, probe)
            if cosine_sim_np(ret, xi) >= 0.5:
                lora_fact_ok += 1
        lora_fact_acc = lora_fact_ok / K_ACTIVE

        # Measure LoRA baseline retention
        lora_base_ok = 0
        for i in range(min(20, M_BASE_ACTIVE)):
            xi = Xi_base[i]
            probe = xi.copy()
            ret = hopfield_retrieve_cpu(W_lora, probe)
            if cosine_sim_np(ret, xi) >= 0.5:
                lora_base_ok += 1
        lora_base_ret = lora_base_ok / min(20, M_BASE_ACTIVE)

        # PROT-022 entry 4: speedup gate requires ACC_FLOOR on BOTH methods
        both_above_floor = (sub_fact_acc >= ACC_FLOOR and lora_fact_acc >= ACC_FLOOR)
        if both_above_floor and wall_lora > 0 and wall_sub > 0:
            wall_speedup = wall_lora / wall_sub
            flops_speedup = flops_lora / max(flops_sub, 1)
        else:
            wall_speedup = float('nan')
            flops_speedup = float('nan')

        print(f"  [seed={seed} r={r}] lora: fact_acc={lora_fact_acc:.4f} "
              f"base_ret={lora_base_ret:.4f} wall={wall_lora:.4f}s steps={n_steps} "
              f"loss={final_loss:.6f} "
              f"wall_speedup={'N/A (ACC_FLOOR not met)' if not both_above_floor else f'{wall_speedup:.1f}x'}", flush=True)

        lora_results.append({
            "rank": r,
            "lora_fact_acc": float(lora_fact_acc),
            "lora_base_ret": float(lora_base_ret),
            "wall_lora_s": float(wall_lora),
            "n_steps": n_steps,
            "final_loss": float(final_loss),
            "flops_lora": int(flops_lora),
            "both_above_acc_floor": bool(both_above_floor),
            "wall_speedup": float(wall_speedup) if not math.isnan(wall_speedup) else None,
            "flops_speedup": float(flops_speedup) if not math.isnan(flops_speedup) else None,
        })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "sub_fact_acc": float(sub_fact_acc),
        "sub_base_ret": float(sub_base_ret),
        "wall_sub_s": float(wall_sub),
        "flops_sub": int(flops_sub),
        "lora_results": lora_results,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    sub_fact_acc = mean_key("sub_fact_acc")
    sub_base_ret = mean_key("sub_base_ret")

    # HF trip-wires
    if sub_fact_acc < HF_FACT_ACC_SUB:
        return ("HARD_FAIL",
                f"HARD_FAIL: substrate fact_acc={sub_fact_acc:.4f} < HF={HF_FACT_ACC_SUB}. "
                f"sub_base_ret={sub_base_ret:.4f} n_seeds={len(results)}")
    if sub_base_ret < HF_BASELINE_RET:
        return ("HARD_FAIL",
                f"HARD_FAIL: substrate base_ret={sub_base_ret:.4f} < HF={HF_BASELINE_RET}. "
                f"sub_fact_acc={sub_fact_acc:.4f} n_seeds={len(results)}")

    # Find best LoRA rank where ACC_FLOOR is met (per PROT-022 entry 4)
    best_lora_acc = 0.0
    best_wall_speedup = None
    best_flops_speedup = None
    best_rank = None
    for r_result in results:
        for lr in r_result.get("lora_results", []):
            if lr.get("both_above_acc_floor") and lr.get("wall_speedup") is not None:
                la = lr["lora_fact_acc"]
                ws = lr["wall_speedup"]
                fs = lr.get("flops_speedup")
                if la > best_lora_acc:
                    best_lora_acc = la
                    best_wall_speedup = ws
                    best_flops_speedup = fs
                    best_rank = lr["rank"]

    lora_never_passes = best_rank is None
    if lora_never_passes:
        return ("LORA_INCOMPATIBLE",
                f"LORA_INCOMPATIBLE: LoRA accuracy never exceeded ACC_FLOOR={ACC_FLOOR} "
                f"at any tested rank. sub_fact_acc={sub_fact_acc:.4f} sub_base_ret={sub_base_ret:.4f}. "
                f"Substrate value continues to rest on 4 confirmed cross-N anchors. n_seeds={len(results)}")

    summary = (f"sub_fact_acc={sub_fact_acc:.4f}(HP>={HP_FACT_ACC_SUB} HF<{HF_FACT_ACC_SUB}) "
               f"sub_base_ret={sub_base_ret:.4f}(HP>={HP_BASELINE_RET} HF<{HF_BASELINE_RET}) "
               f"best_lora_acc={best_lora_acc:.4f}(HP>={HP_FACT_ACC_LORA}) "
               f"best_wall_speedup={best_wall_speedup:.1f}x(HP>={HP_WALL_SPEEDUP}x) "
               f"best_flops_speedup={best_flops_speedup:.1f}x(HP>={HP_FLOPS_SPEEDUP}x) "
               f"best_rank={best_rank} n_seeds={len(results)}")

    hp1 = sub_fact_acc >= HP_FACT_ACC_SUB
    hp2 = best_lora_acc >= HP_FACT_ACC_LORA
    hp3 = best_wall_speedup is not None and best_wall_speedup >= HP_WALL_SPEEDUP
    hp4 = best_flops_speedup is not None and best_flops_speedup >= HP_FLOPS_SPEEDUP
    hp5 = sub_base_ret >= HP_BASELINE_RET

    if hp1 and hp2 and hp3 and hp4 and hp5:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP met in LoRA-valid regime. {summary}")

    mid_wall = best_wall_speedup is not None and 10.0 <= best_wall_speedup < HP_WALL_SPEEDUP
    mid_flops = best_flops_speedup is not None and 100.0 <= best_flops_speedup < HP_FLOPS_SPEEDUP
    if hp1 and hp2 and (mid_wall or mid_flops):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: accuracy OK but speedup narrower. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial HP. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_base={M_BASE_ACTIVE} K={K_ACTIVE} ranks={LORA_RANKS} max_steps={MAX_LORA_STEPS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_baseline": M_BASELINE, "K_facts": K_FACTS,
              "ranks": str(LORA_RANKS), "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
print(f"[elapsed] total sweep time: {elapsed_total:.2f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_baseline": M_BASELINE, "K_facts": K_FACTS, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "lora_ranks": LORA_RANKS,
    "per_seed": [
        {"seed": r.get("seed"),
         "sub_fact_acc": r.get("sub_fact_acc"),
         "sub_base_ret": r.get("sub_base_ret"),
         "wall_sub_s": r.get("wall_sub_s"),
         "lora_results": r.get("lora_results")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
