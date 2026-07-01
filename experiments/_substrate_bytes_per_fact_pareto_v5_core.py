"""Core module for bytes-per-fact storage efficiency Pareto v5 INT8 SPECIALIZATION.

v5 targets the CG-eligible sub-claim from E v4 (MIDDLE_BAND, commit e04666ad):
  INT8 is Pareto-optimal in the M=40k-80k capacity crack.

v4 evidence (seed=7 at M=40k / M=80k, N=2048):
  FP32:   recall 0.386 / 0.117 at 1464 / 732 bytes/fact
  INT8:   recall 0.386 / 0.117 at  367 / 183 bytes/fact  (parity + 4x compression)
  INT4:   recall 0.376 / 0.114 at  184 /  92 bytes/fact  (~0.01 recall gap)
  BINARY: recall 0.215 / 0.063 at   46 /  23 bytes/fact  (Tier 3 anchor)

v5 design: strip to the minimum 4-arm cell that resolves the INT8=FP32-parity +
4x-compression claim across seeds. Drop BFLOAT16 / FP16_range_safe / INT4 /
SPARSE (v4 covered those; v5 is specialized).

Arms (4):
  1. FP32_DENSE                float32 W (baseline; 4 bytes/elem)
  2. INT8_DENSE                int8 W + per-row scale (~1 byte/elem storage)
  3. BINARY_DENSE              sign(W) bit-packed (0.125 byte/elem; Tier 3 anchor)
  4. POSITIVE_CONTROL_NO_QUANT float32 W identical to FP32 (positive-control
                               witness: verifies the identity path is stable
                               across seeds; must equal FP32_DENSE exactly)

M sweep: {40000, 80000}: 2 values x 4 arms = 8 units/seed.
Cross-seed: [7, 13, 19].

Discriminator (HARD_PASS):
  HP: INT8_recall_mean >= FP32_recall_mean - 0.005 AND
      INT8_bytes/fact <= 0.30 * FP32_bytes/fact at BOTH M=40k AND M=80k
      AND cross-seed recall_cv < 0.10 at both M
  MB: passes at M=40k but not M=80k, or fails cv<0.10 at either
  HF: INT8_recall_mean < FP32_recall_mean - 0.005 at either M
  Additionally required (positive controls):
    - POSITIVE_CONTROL_NO_QUANT recall equals FP32_DENSE recall exactly
    - BINARY recall < INT8 recall (Tier 3 anchor should visibly underperform)
    - cardinality_ok: 4 * 2 = 8 units per seed
    - All 4 mechanism_hash distinct

ASCII-only. No unicode.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch


# ---------- Regime constants ----------

N_DIM_DENSE = 2048

FULL_M_SWEEP = [40000, 80000]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10

# Smoke covers BOTH M values at reduced dims so the discriminator fires at
# both crack-band boundaries (DISCRIMINATOR-MUST-SURVIVE-SCALE per META audit).
SMOKE_M_SWEEP = [40000, 80000]
SMOKE_N_ENT = 5000
SMOKE_N_REL = 100
SMOKE_QUERY_FRAC = 0.10
SMOKE_N_DIM_DENSE = 2048  # match full N so parity claim is testable at true regime

TOPK_RECALL = 1
QUERY_NOISE_FRAC = 0.30

INT8_PARITY_TOLERANCE = 0.005          # HP gate: INT8_mean >= FP32_mean - 0.005
INT8_COMPRESSION_MAX_RATIO = 0.30      # HP gate: INT8_bpf <= 0.30 * FP32_bpf
CROSS_SEED_CV_MAX = 0.10               # HP gate: cv < 0.10 at each M

ARMS = ["FP32_DENSE", "INT8_DENSE", "BINARY_DENSE", "POSITIVE_CONTROL_NO_QUANT"]


def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if strict_gpu:
        raise RuntimeError("GPU_REQUIRED: cuda not available in full-mode")
    return torch.device("cpu")


def _bipolar(m: int, n: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    r = torch.randint(0, 2, (m, n), generator=gen, dtype=torch.int8).to(device)
    return (r * 2 - 1).to(torch.float32)


def _add_bipolar_noise(x: torch.Tensor, noise_frac: float, seed: int) -> torch.Tensor:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 99999)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


# ---------- Storage-cost formulas ----------

def bytes_fp32_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_int8_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim * 1) + (n_dim * 4)
    E_bytes = (n_ent * n_dim * 1) + (n_ent * 4)
    R_bytes = (n_rel * n_dim * 1) + (n_rel * 4)
    return W_bytes + E_bytes + R_bytes


def bytes_binary_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim) // 8
    E_bytes = (n_ent * n_dim) // 8
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


# ---------- Ingest + recall per arm ----------

def _ingest_and_query_fp32(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    W = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        W.add_((E[oe].T @ keys) / n_dim)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int8(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    row_max = Wf.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale_row = row_max / 127.0
    W_int8 = torch.round(Wf / scale_row).clamp_(-127, 127).to(torch.int8)
    E_int8 = E.to(torch.int8)
    R_int8 = R.to(torch.int8)
    W_dequant = W_int8.to(torch.float32) * scale_row
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_int8[q_s].to(torch.float32) * R_int8[q_p].to(torch.float32) * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_int8.to(torch.float32).T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_binary(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_bipolar = torch.sign(Wf).clamp_min(-1.0)
    W_bipolar[W_bipolar == 0] = 1.0
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_bipolar.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_positive_control(triples, E, R, queries, gt, n_dim, device):
    """Positive control: identity to FP32_DENSE path. Verifies the untouched
    baseline is stable across seeds. Distinct from FP32_DENSE only by a
    fingerprint tag so mechanism_hash differs by intent-of-inclusion, not
    computed result. Both paths should produce identical recall at each seed.
    """
    return _ingest_and_query_fp32(triples, E, R, queries, gt, n_dim, device)


ARM_FNS = {
    "FP32_DENSE": _ingest_and_query_fp32,
    "INT8_DENSE": _ingest_and_query_int8,
    "BINARY_DENSE": _ingest_and_query_binary,
    "POSITIVE_CONTROL_NO_QUANT": _ingest_and_query_positive_control,
}


def _run_one_arm_at_M(
    arm_name: str, triples: torch.Tensor, queries: torch.Tensor,
    n_ent: int, n_rel: int, n_dim: int, M: int, seed: int, device: torch.device,
) -> Dict[str, Any]:
    arm_device = device
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E_cpu = _bipolar(n_ent, n_dim, g, torch.device("cpu"))
    R_cpu = _bipolar(n_rel, n_dim, g, torch.device("cpu"))
    E = E_cpu.to(arm_device)
    R = R_cpu.to(arm_device)
    triples_dev = triples.to(arm_device)
    queries_dev = queries.to(arm_device)
    t0 = time.perf_counter()
    fn = ARM_FNS[arm_name]
    recall_k = fn(triples_dev, E, R, queries_dev, queries_dev[:, 2], n_dim, arm_device)
    elapsed = time.perf_counter() - t0
    del E, R, triples_dev, queries_dev, E_cpu, R_cpu
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    n_facts = triples.shape[0]
    if arm_name == "FP32_DENSE":
        total_bytes = bytes_fp32_dense(n_dim, n_ent, n_rel)
    elif arm_name == "INT8_DENSE":
        total_bytes = bytes_int8_dense(n_dim, n_ent, n_rel)
    elif arm_name == "BINARY_DENSE":
        total_bytes = bytes_binary_dense(n_dim, n_ent, n_rel)
    elif arm_name == "POSITIVE_CONTROL_NO_QUANT":
        total_bytes = bytes_fp32_dense(n_dim, n_ent, n_rel)
    else:
        raise ValueError(f"unknown arm {arm_name}")
    bpf = total_bytes / n_facts
    fingerprint = hashlib.sha256(
        f"{arm_name}|M={M}|{n_ent}|{n_rel}|{n_dim}|{recall_k:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "M": int(M),
        "recall": recall_k,
        "n_facts": int(n_facts),
        "n_ent": int(n_ent),
        "n_rel": int(n_rel),
        "n_dim": int(n_dim),
        "bytes_total": int(total_bytes),
        "bytes_per_fact": float(bpf),
        "elapsed_s": round(elapsed, 3),
        "mechanism_hash": fingerprint,
        "seed": int(seed),
    }


def build_regime_at_M(seed: int, M: int, n_ent: int, n_rel: int,
                      query_frac: float) -> Tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 1000 + M)
    max_keys = n_ent * n_rel
    if M > max_keys:
        raise ValueError(f"M={M} > n_ent*n_rel={max_keys}; unique-(s,p) infeasible")
    perm = torch.randperm(max_keys, generator=g)[:M]
    s = perm // n_rel
    p = perm % n_rel
    o = torch.randint(0, n_ent, (M,), generator=g)
    triples = torch.stack([s, p, o], dim=1).long()
    n_queries = max(1, int(M * query_frac))
    q_idx = torch.randperm(M, generator=g)[:n_queries]
    queries = triples[q_idx]
    return triples, queries


def run_one_seed_all_units(seed: int, run_mode: str, device: torch.device) -> Dict[str, Any]:
    smoke = (run_mode == "smoke")
    if smoke:
        M_sweep = SMOKE_M_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
        n_dim_dense = SMOKE_N_DIM_DENSE
    else:
        M_sweep = FULL_M_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
        n_dim_dense = N_DIM_DENSE
    per_unit = {}
    for M in M_sweep:
        triples, queries = build_regime_at_M(seed, M, n_ent, n_rel, query_frac)
        for arm in ARMS:
            n_dim = n_dim_dense
            key = f"{arm}__M{M}"
            rec = _run_one_arm_at_M(arm, triples, queries, n_ent, n_rel,
                                    n_dim, M, seed, device)
            per_unit[key] = rec
            print(f"[arm={arm} M={M}] seed={seed} recall={rec['recall']:.3f} "
                  f"bytes/fact={rec['bytes_per_fact']:.0f} "
                  f"elapsed={rec['elapsed_s']:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_sweep": list(M_sweep),
        "arms": list(ARMS),
    }


# ---------- Verdict logic ----------

def _cross_seed_stats(per_seed: List[Dict[str, Any]], unit_keys: List[str]) -> Dict[str, Dict[str, float]]:
    out = {}
    for uk in unit_keys:
        recalls = [ps["per_unit"][uk]["recall"] for ps in per_seed
                   if uk in ps["per_unit"]]
        bpfs = [ps["per_unit"][uk]["bytes_per_fact"] for ps in per_seed
                if uk in ps["per_unit"]]
        if not recalls:
            continue
        rmean = sum(recalls) / len(recalls)
        rvar = sum((r - rmean) ** 2 for r in recalls) / len(recalls)
        rstd = math.sqrt(rvar)
        bmean = sum(bpfs) / len(bpfs)
        out[uk] = {
            "recall_mean": rmean,
            "recall_std": rstd,
            "recall_cv": (rstd / rmean) if rmean > 0 else 0.0,
            "bytes_per_fact_mean": bmean,
        }
    return out


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """v5 HARD_PASS gates (INT8 specialization):
      1. cardinality_ok: 4 * 2 = 8 units per seed
      2. mechanism_hashes distinct (4 arms)
      3. INT8 recall_mean >= FP32 recall_mean - 0.005 at BOTH M=40k AND M=80k
      4. INT8 bytes/fact <= 0.30 * FP32 bytes/fact at BOTH M
      5. Cross-seed recall_cv < 0.10 for INT8_DENSE AND FP32_DENSE at BOTH M
      6. POSITIVE_CONTROL_NO_QUANT recall == FP32 recall (exact; identity path)
      7. BINARY recall < INT8 recall at both M (Tier 3 anchor sanity)
    """
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    M_sweep = SMOKE_M_SWEEP if smoke else FULL_M_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            unit_keys.append(f"{arm}__M{M}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for arm in ARMS:
            uk = f"{arm}__M{M_sweep[0]}"
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == len(ARMS)

    # Core INT8-Pareto claim per M
    per_M_gate = {}
    int8_parity_all_M = True
    int8_compression_all_M = True
    int8_cv_all_M = True
    fp32_cv_all_M = True
    binary_underperforms_all_M = True
    positive_control_matches_all_M = True

    for M in M_sweep:
        fp32_uk = f"FP32_DENSE__M{M}"
        int8_uk = f"INT8_DENSE__M{M}"
        bin_uk = f"BINARY_DENSE__M{M}"
        pc_uk = f"POSITIVE_CONTROL_NO_QUANT__M{M}"

        fp32_mean = stats.get(fp32_uk, {}).get("recall_mean", 0.0)
        int8_mean = stats.get(int8_uk, {}).get("recall_mean", 0.0)
        bin_mean = stats.get(bin_uk, {}).get("recall_mean", 0.0)
        pc_mean = stats.get(pc_uk, {}).get("recall_mean", 0.0)
        fp32_bpf = stats.get(fp32_uk, {}).get("bytes_per_fact_mean", 0.0)
        int8_bpf = stats.get(int8_uk, {}).get("bytes_per_fact_mean", 0.0)
        int8_cv = stats.get(int8_uk, {}).get("recall_cv", 1.0)
        fp32_cv = stats.get(fp32_uk, {}).get("recall_cv", 1.0)

        parity_ok = int8_mean >= (fp32_mean - INT8_PARITY_TOLERANCE)
        compression_ok = int8_bpf <= (INT8_COMPRESSION_MAX_RATIO * fp32_bpf)
        int8_cv_ok = int8_cv < CROSS_SEED_CV_MAX
        fp32_cv_ok = fp32_cv < CROSS_SEED_CV_MAX
        binary_under = bin_mean < int8_mean
        # Positive control: identical fn call to FP32 with same seed; recalls
        # must match exactly (per-seed). Check per-seed strict equality across
        # every seed present.
        pc_seed_match = True
        for ps in per_seed:
            fp32_r = ps["per_unit"].get(fp32_uk, {}).get("recall", None)
            pc_r = ps["per_unit"].get(pc_uk, {}).get("recall", None)
            if fp32_r is None or pc_r is None:
                pc_seed_match = False
                break
            if abs(fp32_r - pc_r) > 1e-9:
                pc_seed_match = False
                break

        per_M_gate[M] = {
            "fp32_recall_mean": fp32_mean,
            "int8_recall_mean": int8_mean,
            "binary_recall_mean": bin_mean,
            "positive_control_recall_mean": pc_mean,
            "fp32_bpf_mean": fp32_bpf,
            "int8_bpf_mean": int8_bpf,
            "int8_over_fp32_bpf_ratio": (int8_bpf / fp32_bpf) if fp32_bpf > 0 else float("inf"),
            "int8_recall_gap_vs_fp32": int8_mean - fp32_mean,
            "int8_cv": int8_cv,
            "fp32_cv": fp32_cv,
            "parity_ok": parity_ok,
            "compression_ok": compression_ok,
            "int8_cv_ok": int8_cv_ok,
            "fp32_cv_ok": fp32_cv_ok,
            "binary_underperforms": binary_under,
            "positive_control_matches": pc_seed_match,
        }
        if not parity_ok:
            int8_parity_all_M = False
        if not compression_ok:
            int8_compression_all_M = False
        if not int8_cv_ok:
            int8_cv_all_M = False
        if not fp32_cv_ok:
            fp32_cv_all_M = False
        if not binary_under:
            binary_underperforms_all_M = False
        if not pc_seed_match:
            positive_control_matches_all_M = False

    all_pass = (cardinality_ok and hashes_distinct
                and int8_parity_all_M and int8_compression_all_M
                and int8_cv_all_M and fp32_cv_all_M
                and binary_underperforms_all_M and positive_control_matches_all_M)

    # MIDDLE_BAND: parity holds at M=40k but not M=80k (partial claim)
    m40 = M_sweep[0]
    m80 = M_sweep[-1]
    partial_m40_ok = (per_M_gate.get(m40, {}).get("parity_ok", False)
                      and per_M_gate.get(m40, {}).get("compression_ok", False))
    partial_m80_ok = (per_M_gate.get(m80, {}).get("parity_ok", False)
                      and per_M_gate.get(m80, {}).get("compression_ok", False))

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} "
                f"expected={expected_n_units}")
    elif not positive_control_matches_all_M:
        verdict = "HARD_FAIL"
        vmsg = ("HARD_FAIL_POSITIVE_CONTROL: NO_QUANT arm did not match FP32_DENSE "
                "exactly per-seed; identity path is unstable")
    elif not int8_parity_all_M:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_INT8_PARITY: INT8 recall < FP32 - {INT8_PARITY_TOLERANCE} at "
                f"one or more M. per_M_gate={per_M_gate}")
    elif all_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT8_PARETO_OPTIMAL: INT8=FP32 within "
                f"{INT8_PARITY_TOLERANCE} recall at M={M_sweep} "
                f"| INT8_bpf<={INT8_COMPRESSION_MAX_RATIO}xFP32_bpf "
                f"| int8_cv<{CROSS_SEED_CV_MAX} at all M "
                f"| BINARY<INT8 anchor OK "
                f"| positive_control matches FP32 exactly "
                f"| n_seeds={n_seeds} | per_M={per_M_gate}")
    elif partial_m40_ok and not partial_m80_ok:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: INT8-Pareto holds at M={m40} but not M={m80}. "
                f"per_M_gate={per_M_gate}")
    elif not (int8_cv_all_M and fp32_cv_all_M):
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: cross-seed cv >= {CROSS_SEED_CV_MAX} at one or more M. "
                f"int8_cv_ok={int8_cv_all_M} fp32_cv_ok={fp32_cv_all_M} "
                f"per_M_gate={per_M_gate}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: parity={int8_parity_all_M} compression="
                f"{int8_compression_all_M} int8_cv={int8_cv_all_M} "
                f"fp32_cv={fp32_cv_all_M} binary_under={binary_underperforms_all_M} "
                f"pc_match={positive_control_matches_all_M} per_M_gate={per_M_gate}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_sweep": list(M_sweep),
        "per_M_gate": per_M_gate,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "int8_parity_all_M": int8_parity_all_M,
        "int8_compression_all_M": int8_compression_all_M,
        "int8_cv_all_M": int8_cv_all_M,
        "fp32_cv_all_M": fp32_cv_all_M,
        "binary_underperforms_all_M": binary_underperforms_all_M,
        "positive_control_matches_all_M": positive_control_matches_all_M,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
        "INT8_PARITY_TOLERANCE": INT8_PARITY_TOLERANCE,
        "INT8_COMPRESSION_MAX_RATIO": INT8_COMPRESSION_MAX_RATIO,
        "CROSS_SEED_CV_MAX": CROSS_SEED_CV_MAX,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25,
                                          query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    recall_fp32 = _ingest_and_query_fp32(triples, E, R, queries, queries[:, 2],
                                          n_dim, smoke_device)
    recall_int8 = _ingest_and_query_int8(triples, E, R, queries, queries[:, 2],
                                          n_dim, smoke_device)
    recall_bin = _ingest_and_query_binary(triples, E, R, queries, queries[:, 2],
                                           n_dim, smoke_device)
    recall_pc = _ingest_and_query_positive_control(triples, E, R, queries,
                                                    queries[:, 2], n_dim,
                                                    smoke_device)
    # Positive-control identity check: must equal FP32 exactly.
    if abs(recall_pc - recall_fp32) > 1e-9:
        return False, (f"selftest positive_control drift: "
                       f"pc={recall_pc} fp32={recall_fp32}")
    if not (recall_fp32 >= 0.0 and recall_int8 >= 0.0 and recall_bin >= 0.0):
        return False, (f"selftest recall <0: fp32={recall_fp32} "
                       f"int8={recall_int8} bin={recall_bin}")
    # Bytes-per-fact monotone: bin < int8 < fp32 (Tier ordering).
    bpf_fp32 = bytes_fp32_dense(n_dim, 200, 25) / triples.shape[0]
    bpf_int8 = bytes_int8_dense(n_dim, 200, 25) / triples.shape[0]
    bpf_bin = bytes_binary_dense(n_dim, 200, 25) / triples.shape[0]
    if not (bpf_bin < bpf_int8 < bpf_fp32):
        return False, (f"selftest bpf ordering broken: "
                       f"bin={bpf_bin} int8={bpf_int8} fp32={bpf_fp32}")
    return True, (f"selftest OK: fp32_recall={recall_fp32:.3f} "
                  f"int8_recall={recall_int8:.3f} bin_recall={recall_bin:.3f} "
                  f"pc==fp32 (identity) "
                  f"bpf_fp32={bpf_fp32:.0f} bpf_int8={bpf_int8:.0f} "
                  f"bpf_bin={bpf_bin:.0f}")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
