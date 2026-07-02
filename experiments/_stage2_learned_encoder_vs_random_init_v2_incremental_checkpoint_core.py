"""Core module v2 for stage2_learned_encoder_vs_random_init.

v1 (commit 48737275) TIMED OUT at 7200s on remote seed_7 (M=16000 contrastive
took much longer than estimated). v2 fixes:

FIX 1 -- Per-arm incremental metrics.json checkpoint (never lose completed
arms). After EACH arm completes, atomically write metrics.json with
verdict=SALVAGE_PARTIAL until all arms done. Copies pattern from
_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_core.py.

FIX 2 -- Reduce grid to focus on load-bearing question (LEARNED vs RANDOM
at cos05-wall). Drop noise-sweep (was {0.0, 0.30} 2 pts -> {0.0} 1 pt).
Drop M=16000 (extreme; had OOM risk anyway; keep 4000/8000/12000).
FULL grid: 2 arms x 3 M x 1 noise = 6 units/seed (down from 16).

FIX 3 -- Reduce SGD steps 500 -> 200. Empirical smoke at 100 steps showed
0.086 -> 0.082 max_cos_key convergence (nearly flat by step 100); doubling
to 200 gives 2x margin for further reduction without 5x cost of 500.

FIX 4 -- Timeout budget 14400s (4h) per USER course-correction. New
formula: 6 units/seed x LEARNED arm at M=12000 SGD 200 steps ~10-30min GPU
per arm; RANDOM arm ~seconds; total ~ 3 x 30min = 90min GPU with 60% budget
safety = 14400s cap. Salvage checkpoint means partial results land even
if timeout still hits.

Discriminator preserved: cos05 at M=12000 is where RANDOM shows 0.661 and
LEARNED with reduced max_pairwise_cos should preserve more. M=16000 was
the near-floor extreme (RANDOM cos05=0.0); dropping it does not remove
the discriminator, only the "extreme test" arm.

ASCII-only. torch import at top (Fix #24).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch


# ---------- Regime constants (v2: reduced grid) ----------

FULL_N = 4096
# Dropped M=16000 (near-floor extreme; not needed for discriminator);
# discriminator M=12000 preserved.
FULL_M_SWEEP = [4000, 8000, 12000]
# Dropped noise=0.30 (was HP_LEARNED_HIGHER_NOISE_TOL arm; not the load-bearing
# question per Director). Focus on capacity discriminator only.
FULL_NOISE_SWEEP = [0.0]

# Smoke: single below-wall M-point for cell mechanism verification.
SMOKE_N = 4096
SMOKE_M_SWEEP = [4000]
SMOKE_NOISE_SWEEP = [0.0]

# Encoder training hyperparameters (LEARNED arm)
LEARNED_N_STEPS_FULL = 200   # FIX 3: 500 -> 200
LEARNED_N_STEPS_SMOKE = 100
LEARNED_LR = 0.02
LEARNED_MARGIN = 0.05
LEARNED_LAMBDA_POS = 0.5
LEARNED_AUG_FLIP_FRAC = 0.01

METRIC_GATES = ["top1", "top5", "top10", "top50", "cos05", "cos08"]

HP_LEARNED_HIGHER_CAPACITY_DELTA = 0.10
HP_ORTHOGONALITY_MAX_COS = 0.20
HF_LEARNED_WORSE_GATE_COUNT = 4
HF_LEARNED_EQUIVALENT_DELTA = 0.03

BASELINE_IN_BAND_LOW = 0.05
BASELINE_IN_BAND_HIGH = 0.95

ARMS = ["RANDOM_INIT", "LEARNED_CONTRASTIVE"]

CROSS_SEED_CV_MAX_HP = 0.10
CROSS_SEED_CV_MAX_MB = 0.15


def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if strict_gpu:
        raise RuntimeError("GPU_REQUIRED: cuda not available in full-mode")
    return torch.device("cpu")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        try:
            return f"cuda:{torch.cuda.get_device_name(0)}"
        except Exception:
            return "cuda:unknown"
    return "cpu"


# ---------- Encoder construction ----------

def _make_random_init_keys(M: int, N: int, seed: int,
                            device: torch.device) -> torch.Tensor:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 11111)
    r = torch.randint(0, 2, (M, N), generator=g, dtype=torch.int8)
    return ((r * 2 - 1).to(torch.float32)).to(device)


def _make_learned_contrastive_keys(
    M: int, N: int, seed: int, device: torch.device,
    n_steps: int,
) -> Tuple[torch.Tensor, Dict[str, Any]]:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 22222)
    r = torch.randint(0, 2, (M, N), generator=g, dtype=torch.int8)
    K = ((r * 2 - 1).to(torch.float32)).to(device)
    K.requires_grad_(True)
    opt = torch.optim.SGD([K], lr=LEARNED_LR)

    losses = []
    max_cos_history = []
    t0 = time.perf_counter()
    for step in range(n_steps):
        opt.zero_grad()
        K_n = K / (K.norm(dim=1, keepdim=True) + 1e-8)
        C = K_n @ K_n.T
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C.masked_fill(eye, 0.0)
        neg_loss = torch.relu(C_off - LEARNED_MARGIN).sum() / (M * (M - 1))
        gg = torch.Generator(device="cpu")
        gg.manual_seed(seed + 33333 + step)
        flip_mask_cpu = (torch.rand((M, N), generator=gg) < LEARNED_AUG_FLIP_FRAC)
        neg_one = torch.tensor(-1.0, dtype=K.dtype, device=device)
        pos_one = torch.tensor(1.0, dtype=K.dtype, device=device)
        flip = torch.where(flip_mask_cpu.to(device), neg_one, pos_one)
        K_aug = K.detach() * flip
        K_aug_n = K_aug / (K_aug.norm(dim=1, keepdim=True) + 1e-8)
        pos_cos = (K_n * K_aug_n).sum(dim=1)
        pos_loss = torch.relu(LEARNED_MARGIN - pos_cos).mean()
        loss = neg_loss + LEARNED_LAMBDA_POS * pos_loss
        loss.backward()
        opt.step()
        with torch.no_grad():
            if step % max(1, n_steps // 20) == 0 or step == n_steps - 1:
                losses.append((step, float(loss.item())))
                max_cos = float(C_off.abs().max().item())
                max_cos_history.append((step, max_cos))
    train_wall = time.perf_counter() - t0

    with torch.no_grad():
        K_final = K.detach().clone()
        K_n = K_final / (K_final.norm(dim=1, keepdim=True) + 1e-8)
        C = K_n @ K_n.T
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C.masked_fill(eye, 0.0)
        final_max_cos = float(C_off.abs().max().item())
        final_mean_cos = float(C_off.abs().mean().item())
    diag = {
        "n_steps": n_steps, "lr": LEARNED_LR, "margin": LEARNED_MARGIN,
        "lambda_pos": LEARNED_LAMBDA_POS, "aug_flip_frac": LEARNED_AUG_FLIP_FRAC,
        "losses_by_step": losses, "max_cos_by_step": max_cos_history,
        "final_max_pairwise_cos": final_max_cos,
        "final_mean_pairwise_cos": final_mean_cos,
        "train_wall_s": round(train_wall, 3),
    }
    return K_final, diag


def _build_W(K: torch.Tensor, O: torch.Tensor) -> torch.Tensor:
    N = K.shape[1]
    return (O.T @ K) / float(N)


def _add_bipolar_noise(x: torch.Tensor, noise_frac: float,
                        seed: int) -> torch.Tensor:
    if noise_frac <= 0.0:
        return x.clone()
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 55555)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


def _run_one_arm(
    arm_name: str, M: int, noise: float, N: int, seed: int,
    device: torch.device, n_steps_learned: int,
) -> Dict[str, Any]:
    M = int(M)
    alpha = M / float(N)
    g_o = torch.Generator(device="cpu")
    g_o.manual_seed(seed + 77777)
    ro = torch.randint(0, 2, (M, N), generator=g_o, dtype=torch.int8)
    O = ((ro * 2 - 1).to(torch.float32)).to(device)

    train_diag: Dict[str, Any] = {}
    t_encoder = time.perf_counter()
    if arm_name == "RANDOM_INIT":
        K = _make_random_init_keys(M, N, seed, device)
    elif arm_name == "LEARNED_CONTRASTIVE":
        K, train_diag = _make_learned_contrastive_keys(
            M, N, seed, device, n_steps=n_steps_learned)
    else:
        raise ValueError(f"unknown arm: {arm_name}")
    encoder_wall = time.perf_counter() - t_encoder

    with torch.no_grad():
        K_n = K / (K.norm(dim=1, keepdim=True) + 1e-8)
        C_key = K_n @ K_n.T
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C_key.masked_fill(eye, 0.0)
        max_cos_key = float(C_off.abs().max().item())
        mean_cos_key = float(C_off.abs().mean().item())

    with torch.no_grad():
        W = _build_W(K, O)
    del K_n, C_key, C_off, eye

    with torch.no_grad():
        Kq = _add_bipolar_noise(K, noise, seed)
        Pred = (W @ Kq.T).T
        Pred_n = Pred / (Pred.norm(dim=1, keepdim=True) + 1e-8)
        O_n = O / (O.norm(dim=1, keepdim=True) + 1e-8)
        scores = Pred_n @ O_n.T
        gt = torch.arange(M, device=device)
        topk_max = min(50, M)
        topk_vals, topk_idx = torch.topk(scores, k=topk_max, dim=1)
        gt_expanded = gt.unsqueeze(1)
        def _topn(n):
            n_eff = min(n, topk_max)
            return float((topk_idx[:, :n_eff] == gt_expanded).any(dim=1).float().mean().item())
        top1 = _topn(1); top5 = _topn(5); top10 = _topn(10); top50 = _topn(50)
        diag_cos = scores.gather(1, gt.unsqueeze(1)).squeeze(1)
        cos05 = float((diag_cos >= 0.5).float().mean().item())
        cos08 = float((diag_cos >= 0.8).float().mean().item())

    del W, Pred, Pred_n, O_n, scores, Kq
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass

    fingerprint = hashlib.sha256(
        f"{arm_name}|N={N}|M={M}|noise={noise}|"
        f"top1={top1:.6f}|top5={top5:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name, "alpha": float(alpha), "M": int(M), "N": int(N),
        "noise": float(noise),
        "top1": top1, "top5": top5, "top10": top10, "top50": top50,
        "cos05": cos05, "cos08": cos08,
        "max_pairwise_cos_key": max_cos_key,
        "mean_pairwise_cos_key": mean_cos_key,
        "encoder_wall_s": round(encoder_wall, 3),
        "seed": int(seed),
        "mechanism_hash": fingerprint,
        "train_diag": train_diag,
    }


# ---------- Incremental checkpoint (FIX 1) ----------

def _write_incremental_metrics(
    out_dir: Path, seed: int, anchor_name: str, run_mode: str,
    per_arm_so_far: List[Dict], expected_n_units: int,
    t_start: float, is_partial: bool, config_version: str,
    backend: str,
) -> None:
    """Atomically write metrics.json reflecting all arms completed so far.
    Called after EACH arm so a timeout kill preserves data (FIX 1).
    """
    if is_partial:
        verdict = "SALVAGE_PARTIAL"
        vmsg = (f"SALVAGE_PARTIAL: {len(per_arm_so_far)}/{expected_n_units} arms complete "
                f"at wall={time.time()-t_start:.1f}s; metrics.json incrementally checkpointed")
    else:
        # Final: compute honest verdict from per_arm_so_far
        per_seed_stub = [{"seed": seed, "per_unit": {
            f"{r['arm']}__M{r['M']}__f{r['noise']:.2f}__N{r['N']}": r
            for r in per_arm_so_far
        }}]
        v = aggregate_and_verdict(per_seed_stub, run_mode=run_mode,
                                   from_incremental=True)
        verdict = v["verdict"]
        vmsg = v["verdict_msg"]

    total_wall = time.time() - t_start
    metrics = {
        "anchor_name": anchor_name,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": (vmsg[:400] +
                    f" | wall={total_wall:.1f}s "
                    f"arms={len(per_arm_so_far)}/{expected_n_units}"),
        "elapsed_s": round(total_wall, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": run_mode,
        "config_version": config_version,
        "seed": int(seed),
        "n_arms_complete": len(per_arm_so_far),
        "expected_n_units": expected_n_units,
        "n_seeds": 1,
        "per_arm": per_arm_so_far,
        "checkpoint_kind": ("per_arm_incremental" if is_partial
                            else "final_complete"),
        "cell_version": "v2_incremental_checkpoint",
        "backend": backend,
        "torch_available": True,
        "torch_cuda_available": torch.cuda.is_available(),
    }
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(str(tmp), str(final))


def _append_arm_result(out_dir: Path, arm_record: Dict) -> None:
    """Append arm record to _arm_results.jsonl (audit trail)."""
    p = out_dir / "_arm_results.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(arm_record, default=str) + "\n")


# ---------- Seed runner (M-major with per-arm checkpoint) ----------

def run_one_seed_all_units(
    seed: int, run_mode: str, device: torch.device,
    out_dir: Path, anchor_name: str, config_version: str, backend: str,
    t_start: float,
) -> Dict[str, Any]:
    smoke = (run_mode == "smoke")
    if smoke:
        N = SMOKE_N; M_sweep = SMOKE_M_SWEEP
        noise_sweep = SMOKE_NOISE_SWEEP; n_steps = LEARNED_N_STEPS_SMOKE
    else:
        N = FULL_N; M_sweep = FULL_M_SWEEP
        noise_sweep = FULL_NOISE_SWEEP; n_steps = LEARNED_N_STEPS_FULL

    expected_n_units = len(ARMS) * len(M_sweep) * len(noise_sweep)
    per_arm: List[Dict] = []
    per_unit: Dict[str, Dict] = {}
    t_seed_start = time.time()

    for M in M_sweep:
        for noise in noise_sweep:
            for arm in ARMS:
                key = f"{arm}__M{M}__f{noise:.2f}__N{N}"
                rec = _run_one_arm(arm, M, noise, N, seed, device,
                                    n_steps_learned=n_steps)
                per_unit[key] = rec
                per_arm.append(rec)
                elapsed = time.time() - t_seed_start
                print(f"[arm={arm} M={M} f={noise:.2f}] seed={seed} "
                      f"top1={rec['top1']:.3f} cos05={rec['cos05']:.3f} "
                      f"max_cos_key={rec['max_pairwise_cos_key']:.3f} "
                      f"enc_wall={rec['encoder_wall_s']:.2f}s "
                      f"seed_total={elapsed:.1f}s", flush=True)

                # FIX 1: append + incremental checkpoint after EACH arm
                _append_arm_result(out_dir, rec)
                _write_incremental_metrics(
                    out_dir=out_dir, seed=seed, anchor_name=anchor_name,
                    run_mode=run_mode, per_arm_so_far=per_arm,
                    expected_n_units=expected_n_units,
                    t_start=t_start, is_partial=(len(per_arm) < expected_n_units),
                    config_version=config_version, backend=backend,
                )
    return {
        "seed": int(seed), "run_mode": run_mode,
        "per_unit": per_unit,
        "N_fixed": N, "M_sweep": list(M_sweep),
        "noise_sweep": list(noise_sweep),
        "arms": list(ARMS), "n_steps_learned": n_steps,
    }


# ---------- Cross-seed + verdict ----------

def _cross_seed_stats(per_seed: List[Dict[str, Any]],
                       unit_keys: List[str]) -> Dict[str, Dict[str, float]]:
    out = {}
    for uk in unit_keys:
        top1s = [ps["per_unit"][uk]["top1"] for ps in per_seed if uk in ps["per_unit"]]
        top5s = [ps["per_unit"][uk]["top5"] for ps in per_seed if uk in ps["per_unit"]]
        top10s = [ps["per_unit"][uk]["top10"] for ps in per_seed if uk in ps["per_unit"]]
        top50s = [ps["per_unit"][uk]["top50"] for ps in per_seed if uk in ps["per_unit"]]
        cos05s = [ps["per_unit"][uk]["cos05"] for ps in per_seed if uk in ps["per_unit"]]
        cos08s = [ps["per_unit"][uk]["cos08"] for ps in per_seed if uk in ps["per_unit"]]
        max_cos_keys = [ps["per_unit"][uk]["max_pairwise_cos_key"] for ps in per_seed if uk in ps["per_unit"]]
        if not top1s: continue
        def _stats(xs):
            m = sum(xs) / len(xs)
            v = sum((x - m) ** 2 for x in xs) / len(xs)
            s = math.sqrt(v)
            return m, s, (s / m if m > 0 else 0.0)
        m_t1, s_t1, cv_t1 = _stats(top1s)
        m_t5, s_t5, cv_t5 = _stats(top5s)
        m_t10, s_t10, cv_t10 = _stats(top10s)
        m_t50, s_t50, cv_t50 = _stats(top50s)
        m_c5, s_c5, cv_c5 = _stats(cos05s)
        m_c8, s_c8, cv_c8 = _stats(cos08s)
        m_mck, _, _ = _stats(max_cos_keys)
        out[uk] = {
            "top1_mean": m_t1, "top1_std": s_t1, "top1_cv": cv_t1,
            "top5_mean": m_t5, "top5_cv": cv_t5,
            "top10_mean": m_t10, "top10_cv": cv_t10,
            "top50_mean": m_t50, "top50_cv": cv_t50,
            "cos05_mean": m_c5, "cos05_cv": cv_c5,
            "cos08_mean": m_c8, "cos08_cv": cv_c8,
            "max_pairwise_cos_key_mean": m_mck,
            "n_seeds": len(top1s),
        }
    return out


def _get_stat(stats, arm, M, noise, N, metric):
    key = f"{arm}__M{M}__f{noise:.2f}__N{N}"
    return stats.get(key, {}).get(f"{metric}_mean", float("nan"))


def aggregate_and_verdict(per_seed, run_mode: str,
                          from_incremental: bool = False) -> Dict[str, Any]:
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    N = SMOKE_N if smoke else FULL_N
    M_sweep = SMOKE_M_SWEEP if smoke else FULL_M_SWEEP
    noise_sweep = SMOKE_NOISE_SWEEP if smoke else FULL_NOISE_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            for noise in noise_sweep:
                unit_keys.append(f"{arm}__M{M}__f{noise:.2f}__N{N}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep) * len(noise_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    # ARMS_MUST_DIFFER
    arms_differ_details = {}
    for M in M_sweep:
        for noise in noise_sweep:
            r_t1 = _get_stat(stats, "RANDOM_INIT", M, noise, N, "top1")
            l_t1 = _get_stat(stats, "LEARNED_CONTRASTIVE", M, noise, N, "top1")
            differ = (not math.isnan(r_t1)) and (not math.isnan(l_t1)) and (abs(r_t1 - l_t1) > 1e-6)
            arms_differ_details[f"M{M}_f{noise:.2f}"] = {
                "RANDOM_top1": r_t1, "LEARNED_top1": l_t1, "differ": differ,
            }

    # HP_LEARNED_HIGHER_CAPACITY at cos05-wall M (FULL: M=12000; smoke: SMOKE_M[0])
    HP_CAPACITY_M = 12000 if not smoke else M_sweep[0]
    r_cap = _get_stat(stats, "RANDOM_INIT", HP_CAPACITY_M, 0.0, N, "cos05")
    l_cap = _get_stat(stats, "LEARNED_CONTRASTIVE", HP_CAPACITY_M, 0.0, N, "cos05")
    cap_delta = l_cap - r_cap if (not math.isnan(r_cap) and not math.isnan(l_cap)) else float("nan")
    hp_learned_higher_capacity = (not math.isnan(cap_delta)) and (cap_delta >= HP_LEARNED_HIGHER_CAPACITY_DELTA)

    # HP_ORTHOGONALITY
    max_learned_cos = 0.0
    for M in M_sweep:
        for noise in noise_sweep:
            key = f"LEARNED_CONTRASTIVE__M{M}__f{noise:.2f}__N{N}"
            v = stats.get(key, {}).get("max_pairwise_cos_key_mean", float("nan"))
            if not math.isnan(v) and v > max_learned_cos:
                max_learned_cos = v
    hp_orthogonality = max_learned_cos <= HP_ORTHOGONALITY_MAX_COS

    # HF gates
    total_pairs = len(M_sweep) * len(noise_sweep) * len(METRIC_GATES)
    learned_worse_count = 0
    learned_equivalent_count = 0
    per_gate_deltas = []
    for M in M_sweep:
        for noise in noise_sweep:
            for metric in METRIC_GATES:
                r = _get_stat(stats, "RANDOM_INIT", M, noise, N, metric)
                l = _get_stat(stats, "LEARNED_CONTRASTIVE", M, noise, N, metric)
                if math.isnan(r) or math.isnan(l): continue
                delta = l - r
                per_gate_deltas.append({
                    "M": M, "noise": noise, "metric": metric,
                    "RANDOM": r, "LEARNED": l, "delta": delta,
                })
                if delta < -HF_LEARNED_EQUIVALENT_DELTA:
                    learned_worse_count += 1
                if abs(delta) < HF_LEARNED_EQUIVALENT_DELTA:
                    learned_equivalent_count += 1

    hf_learned_worse_threshold = max(1, round(HF_LEARNED_WORSE_GATE_COUNT / 6.0 * total_pairs))
    hf_learned_worse = learned_worse_count >= hf_learned_worse_threshold
    hf_learned_equivalent = (learned_equivalent_count == total_pairs) and (total_pairs > 0)

    # Baseline-in-band on cos05
    baseline_in_band = False
    baseline_details = {}
    for M in M_sweep:
        for noise in noise_sweep:
            b = _get_stat(stats, "RANDOM_INIT", M, noise, N, "cos05")
            baseline_details[f"M{M}_f{noise:.2f}_cos05"] = b
            if (not math.isnan(b)) and (BASELINE_IN_BAND_LOW < b < BASELINE_IN_BAND_HIGH):
                baseline_in_band = True

    max_cv = 0.0
    for uk in unit_keys:
        for c in ["top1_cv", "top5_cv", "top10_cv", "top50_cv", "cos05_cv", "cos08_cv"]:
            v = stats.get(uk, {}).get(c, 0.0)
            if v > max_cv: max_cv = v
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # When called from incremental (partial) we skip cardinality/HF strictness
    if from_incremental and not cardinality_ok:
        verdict = "SALVAGE_PARTIAL"
        vmsg = (f"SALVAGE_PARTIAL(inc): {sum(observed_n_units_per_seed)}/{expected_n_units} arms; "
                f"orthogonality={hp_orthogonality} cap_delta={cap_delta:.3f}")
    elif not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} expected={expected_n_units}"
    elif not hashes_distinct:
        verdict = "HARD_FAIL_META_RULE_AX_HASH_COLLISION"
        vmsg = f"HARD_FAIL: mechanism_hash collision ({len(hashes)} distinct vs {expected_n_units} expected)"
    elif cv_hard_fail:
        verdict = "HARD_FAIL_CV_BREACH"
        vmsg = f"HARD_FAIL: cross-seed cv >= {CROSS_SEED_CV_MAX_MB} (max_cv={max_cv:.3f})"
    elif smoke:
        smoke_M = M_sweep[0]
        r_maxc = stats.get(f"RANDOM_INIT__M{smoke_M}__f0.00__N{N}", {}).get("max_pairwise_cos_key_mean", float("nan"))
        l_maxc = stats.get(f"LEARNED_CONTRASTIVE__M{smoke_M}__f0.00__N{N}", {}).get("max_pairwise_cos_key_mean", float("nan"))
        maxc_delta = (r_maxc - l_maxc) if (not math.isnan(r_maxc) and not math.isnan(l_maxc)) else float("nan")
        smoke_arms_measurable = (
            ((not math.isnan(cap_delta)) and abs(cap_delta) >= 0.02) or
            ((not math.isnan(maxc_delta)) and abs(maxc_delta) >= 0.02)
        )
        if not smoke_arms_measurable:
            verdict = "MIDDLE_BAND_ARMS_INDISTINGUISHABLE"
            vmsg = (f"SMOKE_MIDDLE_BAND: RANDOM and LEARNED indistinguishable at "
                    f"(M={smoke_M}, f=0.0) N={N}: cap_delta={cap_delta:.3f} "
                    f"maxc_delta={maxc_delta:.3f}; below-wall smoke expected result")
        else:
            direction = ("LEARNED_HIGHER" if (not math.isnan(cap_delta) and cap_delta > 0) else "RANDOM_HIGHER_OR_MAXC")
            verdict = "HARD_PASS_SMOKE_ARMS_MEASURABLE"
            vmsg = (f"SMOKE_HARD_PASS: arms measurable at (M={smoke_M}, f=0.0, N={N}); "
                    f"cap_delta={cap_delta:.3f} maxc_delta={maxc_delta:.3f} ({direction}); "
                    f"orthogonality={hp_orthogonality} max_cos_learned={max_learned_cos:.3f}")
    elif not baseline_in_band:
        verdict = "HARD_FAIL_META_RULE_AG_BASELINE_OUT_OF_BAND"
        vmsg = f"HARD_FAIL_META_RULE_AG: RANDOM baseline cos05 out of band at every sweep point (details={baseline_details})"
    elif hp_learned_higher_capacity:
        verdict = "HARD_PASS_LEARNED_ENCODER_HELPS_CAPACITY"
        vmsg = (f"HARD_PASS_LEARNED_HELPS_CAPACITY: cap_delta={cap_delta:.3f}>={HP_LEARNED_HIGHER_CAPACITY_DELTA}; "
                f"orthogonality={hp_orthogonality} (max_cos_learned={max_learned_cos:.3f})")
    elif hf_learned_worse:
        verdict = "HARD_FAIL_LEARNED_HURTS_SUBSTRATE_NATIVE_VALIDATED"
        vmsg = (f"HF_LEARNED_WORSE: {learned_worse_count}/{total_pairs} gates show LEARNED<RANDOM; "
                f"substrate-native simplicity validated; R21 5%-prediction closed with data")
    elif hf_learned_equivalent:
        verdict = "HARD_FAIL_LEARNED_EQUIVALENT_NO_LIFT"
        vmsg = (f"HF_LEARNED_EQUIVALENT: {learned_equivalent_count}/{total_pairs} gates within |delta|<{HF_LEARNED_EQUIVALENT_DELTA}; "
                f"learning does nothing at n_steps={LEARNED_N_STEPS_FULL} budget")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: HP not met but HF not fired; cap_delta={cap_delta:.3f} "
                f"orthogonality_max_cos={max_learned_cos:.3f} learned_worse_count={learned_worse_count}/{total_pairs}")

    return {
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:400],
        "run_mode": run_mode, "n_seeds": n_seeds,
        "arms": list(ARMS), "N_fixed": N, "M_sweep": list(M_sweep),
        "noise_sweep": list(noise_sweep), "metric_gates": list(METRIC_GATES),
        "hp_learned_higher_capacity": bool(hp_learned_higher_capacity),
        "hp_orthogonality": bool(hp_orthogonality),
        "hf_learned_worse": bool(hf_learned_worse),
        "hf_learned_equivalent": bool(hf_learned_equivalent),
        "cap_delta": cap_delta, "cap_random_cos05": r_cap, "cap_learned_cos05": l_cap,
        "max_learned_cos_key": max_learned_cos,
        "learned_worse_count": learned_worse_count,
        "learned_equivalent_count": learned_equivalent_count,
        "hf_learned_worse_threshold": hf_learned_worse_threshold,
        "total_gate_pairs": total_pairs,
        "per_gate_deltas": per_gate_deltas,
        "arms_differ_details": arms_differ_details,
        "baseline_in_band": bool(baseline_in_band),
        "baseline_details": baseline_details,
        "max_cv_across_arms": max_cv, "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "per_seed": per_seed,
        "HP_LEARNED_HIGHER_CAPACITY_DELTA": HP_LEARNED_HIGHER_CAPACITY_DELTA,
        "HP_ORTHOGONALITY_MAX_COS": HP_ORTHOGONALITY_MAX_COS,
        "HF_LEARNED_WORSE_GATE_COUNT": HF_LEARNED_WORSE_GATE_COUNT,
        "HF_LEARNED_EQUIVALENT_DELTA": HF_LEARNED_EQUIVALENT_DELTA,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    tiny_device = torch.device("cpu")
    N_tiny = 128; M_tiny = 32; noise_tiny = 0.0
    rec_random = _run_one_arm("RANDOM_INIT", M_tiny, noise_tiny, N_tiny, seed, tiny_device, n_steps_learned=10)
    rec_learned = _run_one_arm("LEARNED_CONTRASTIVE", M_tiny, noise_tiny, N_tiny, seed, tiny_device, n_steps_learned=10)
    for arm, rec in [("RANDOM", rec_random), ("LEARNED", rec_learned)]:
        for m in ["top1", "top5", "cos05"]:
            v = rec[m]
            if not (0.0 <= v <= 1.0):
                return False, f"selftest {arm} {m}={v} out of [0,1]"
    if rec_random["mechanism_hash"] == rec_learned["mechanism_hash"]:
        return False, "selftest hashes identical (arms should differ)"
    if not rec_learned.get("train_diag"):
        return False, "selftest LEARNED train_diag missing"
    msg = (f"SELFTEST_OK: RANDOM top1={rec_random['top1']:.3f} "
           f"LEARNED top1={rec_learned['top1']:.3f} "
           f"LEARNED_final_max_cos={rec_learned['train_diag']['final_max_pairwise_cos']:.3f} "
           f"train_wall={rec_learned['train_diag']['train_wall_s']:.2f}s")
    return True, msg
