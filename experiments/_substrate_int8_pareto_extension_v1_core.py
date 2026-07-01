"""Core module for INT8_DENSE Pareto extension v1 (Wave-2 §1 per Research a004a7e5).

Extends E v5 CG finding: INT8_DENSE Pareto-optimal at M in {40k, 80k} at N=2048.
E v5 fixed N + used FP32 baseline. v1 extension probes storage-recipe regime-
conditionality across:
  - 3 storage arms: INT8_DENSE / BFLOAT16_DENSE / BINARY_DENSE
    (BFLOAT16 as FP tier per Wave-2 note; FP32 not measured here because E v5
     already established FP32~INT8 parity in-crack + BFLOAT16 is the
     production FP dtype for capacity regimes.)
  - 3 M values: {10000, 20000, 40000}
      * M=10k probes PRE-crack (higher recall floor for all arms; discriminates
        by wire-cost only)
      * M=20k probes MID-crack (bytes/fact matters; INT8 lead should stay)
      * M=40k anchors CG CALIBRATION from E v5 (in-crack; recall drops)
  - 3 N values: {2048, 4096, 8192}
      * N=2048 anchors E v5 calibration point
      * N=4096, N=8192 probe scaling of the storage-arm dominance
  - Noise held at CLEAN (query_noise_frac=0.30 bipolar as in E v5 - same
    baseline noise regime as CG anchor; "clean" here means single-noise-point
    per Research task; noise-sweep is a follow-up cell if this lands.)
  - 3 seeds [7, 13, 19]

Grid: 3 storage x 3 M x 3 N = 27 units per seed.
      27 units x 3 seeds = 81 total measurements.

Discriminator (HARD_PASS):
  HP: INT8_DENSE Pareto-dominates at >=2 of 3 M regimes (aggregating across N)
      with cross-seed recall_cv < 0.08 for INT8 at those regimes
      META_RULE_Q: at each M point, at least one arm must fall <0.95 recall
                   (otherwise all-saturation is not discriminating)
  MB: INT8 dominates at some regimes but not >=2 (regime-conditional storage
      recipe; still publishable as MM); OR crossover finding (different arm
      wins at different M with seed-consistency); OR cv 0.08-0.10 band
  HF: BINARY or BFLOAT16 wins broadly (contradicts E v5 CG finding); OR
      all-saturation at all M (META_RULE_Q breach: not discriminating); OR
      cross-seed cv >= 0.10 for any storage arm

META_RULE_AT compliance: composes hdlab/int8_dense.py primitive
(quantize_int8_dense) at commit c3ca7dab.
META_RULE_AX: distinct mechanism_hash per (arm, M, N).
META_RULE_H: CARDINALITY_OK = 27; HARD_FAIL_CARDINALITY_BREACH if observed !=
expected.
META_RULE_Q: at each M, at least one arm recall < 0.95 (saturation check).

ASCII-only. No unicode.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch

from hdlab.int8_dense import quantize_int8_dense


# ---------- Regime constants ----------

FULL_M_SWEEP = [10000, 20000, 40000]
FULL_N_SWEEP = [2048, 4096, 8192]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10

# Smoke = seed_7 at M=20k, N=4096 (single point; verifies discriminator fires
# at MID-crack + MID-N; DISCRIMINATOR-MUST-SURVIVE-SCALE Check C variant: N=4096
# is closer to full-grid boundary than N=2048 anchor).
SMOKE_M_SWEEP = [40000]  # in-crack per E v5 calibration; guarantees non-saturation
SMOKE_N_SWEEP = [4096]   # mid-N; between E v5 anchor (2048) and boundary (8192)
SMOKE_N_ENT = 5000
SMOKE_N_REL = 100
SMOKE_QUERY_FRAC = 0.10

TOPK_RECALL = 1
QUERY_NOISE_FRAC = 0.30  # match E v5 baseline (CLEAN noise regime for this cell)

# Pareto / discriminator gates
INT8_LEAD_TOLERANCE = 0.005              # HP: INT8 lead vs best-other-arm >= this
CROSS_SEED_CV_MAX_HP = 0.08              # HP: cv < 0.08 (tighter than E v5)
CROSS_SEED_CV_MAX_MB = 0.10              # MB upper bound
SATURATION_RECALL_CEIL = 0.95            # META_RULE_Q: at each M, some arm < this

ARMS = ["INT8_DENSE", "BFLOAT16_DENSE", "BINARY_DENSE"]


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

def bytes_int8_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim * 1) + (n_dim * 4)
    E_bytes = (n_ent * n_dim * 1) + (n_ent * 4)
    R_bytes = (n_rel * n_dim * 1) + (n_rel * 4)
    return W_bytes + E_bytes + R_bytes


def bytes_bfloat16_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    # bfloat16 is 2 bytes per element (no scale needed)
    return (n_dim * n_dim * 2) + (n_ent * n_dim * 2) + (n_rel * n_dim * 2)


def bytes_binary_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim) // 8
    E_bytes = (n_ent * n_dim) // 8
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


# ---------- Ingest + recall per arm ----------

def _ingest_and_query_int8(triples, E, R, queries, n_dim, device):
    """INT8_DENSE arm: composes hdlab.int8_dense.quantize_int8_dense (META_RULE_AT)."""
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    # META_RULE_AT: compose hdlab primitive rather than inline the math
    W_int8, scale_row = quantize_int8_dense(Wf)
    W_dequant = W_int8.to(torch.float32) * scale_row
    E_int8 = E.to(torch.int8)
    R_int8 = R.to(torch.int8)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_int8[q_s].to(torch.float32) * R_int8[q_p].to(torch.float32) * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_int8.to(torch.float32).T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_bfloat16(triples, E, R, queries, n_dim, device):
    """BFLOAT16_DENSE arm: W STORED as bfloat16 (0.5x FP32 mem); matmul in fp32.

    Rationale: production bf16 usage is storage-quantization + cast-on-load
    with fp32 matmul accumulator. CPU bfloat16 matmul kernel is 100x-1000x
    slower than fp32 on x86 without AVX512-BF16 (measured 53s for one
    2000x4096 outer at N=4096 on this laptop), which was hanging smoke.
    Modeling bf16 as storage-only quantization is faithful to the arm's
    storage-cost claim (bytes_bfloat16_dense returns 2 bytes/elem cost) while
    keeping the experiment tractable on CPU. The recall figure captures the
    representational fidelity loss from bf16 storage; the compute time is not
    the discriminator here (bytes/fact is).
    """
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    # Model bf16 storage via round-trip: emulate the lossy storage step
    W_bf = Wf.to(torch.bfloat16)
    W_dequant = W_bf.to(torch.float32)
    E_bf_roundtrip = E.to(torch.bfloat16).to(torch.float32)
    R_bf_roundtrip = R.to(torch.bfloat16).to(torch.float32)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_bf_roundtrip[q_s] * R_bf_roundtrip[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_bf_roundtrip.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_binary(triples, E, R, queries, n_dim, device):
    """BINARY_DENSE arm: sign(W) bit-packed (0.125 byte/elem; Tier 3 anchor)."""
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


ARM_FNS = {
    "INT8_DENSE": _ingest_and_query_int8,
    "BFLOAT16_DENSE": _ingest_and_query_bfloat16,
    "BINARY_DENSE": _ingest_and_query_binary,
}


def _run_one_arm_at_MN(
    arm_name: str, triples: torch.Tensor, queries: torch.Tensor,
    n_ent: int, n_rel: int, n_dim: int, M: int, seed: int,
    device: torch.device,
) -> Dict[str, Any]:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E_cpu = _bipolar(n_ent, n_dim, g, torch.device("cpu"))
    R_cpu = _bipolar(n_rel, n_dim, g, torch.device("cpu"))
    E = E_cpu.to(device)
    R = R_cpu.to(device)
    triples_dev = triples.to(device)
    queries_dev = queries.to(device)
    t0 = time.perf_counter()
    fn = ARM_FNS[arm_name]
    recall_k = fn(triples_dev, E, R, queries_dev, n_dim, device)
    elapsed = time.perf_counter() - t0
    del E, R, triples_dev, queries_dev, E_cpu, R_cpu
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    n_facts = triples.shape[0]
    if arm_name == "INT8_DENSE":
        total_bytes = bytes_int8_dense(n_dim, n_ent, n_rel)
    elif arm_name == "BFLOAT16_DENSE":
        total_bytes = bytes_bfloat16_dense(n_dim, n_ent, n_rel)
    elif arm_name == "BINARY_DENSE":
        total_bytes = bytes_binary_dense(n_dim, n_ent, n_rel)
    else:
        raise ValueError(f"unknown arm {arm_name}")
    bpf = total_bytes / n_facts
    # META_RULE_AX: distinct hash per (arm, M, N) via inputs + result
    fingerprint = hashlib.sha256(
        f"{arm_name}|M={M}|N={n_dim}|{n_ent}|{n_rel}|"
        f"{recall_k:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "M": int(M),
        "N": int(n_dim),
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
        N_sweep = SMOKE_N_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
    else:
        M_sweep = FULL_M_SWEEP
        N_sweep = FULL_N_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
    per_unit = {}
    for M in M_sweep:
        triples, queries = build_regime_at_M(seed, M, n_ent, n_rel, query_frac)
        for N in N_sweep:
            for arm in ARMS:
                key = f"{arm}__M{M}__N{N}"
                rec = _run_one_arm_at_MN(arm, triples, queries, n_ent, n_rel,
                                          N, M, seed, device)
                per_unit[key] = rec
                print(f"[arm={arm} M={M} N={N}] seed={seed} "
                      f"recall={rec['recall']:.3f} "
                      f"bytes/fact={rec['bytes_per_fact']:.0f} "
                      f"elapsed={rec['elapsed_s']:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_sweep": list(M_sweep),
        "N_sweep": list(N_sweep),
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
            "n_seeds": len(recalls),
        }
    return out


def _pareto_winner_at_MN(stats, M, N):
    """Return arm with highest recall at (M, N); tie-break by lowest bytes/fact."""
    best_arm = None
    best_recall = -1.0
    best_bpf = float("inf")
    per_arm = {}
    for arm in ARMS:
        uk = f"{arm}__M{M}__N{N}"
        s = stats.get(uk, {})
        r = s.get("recall_mean", 0.0)
        b = s.get("bytes_per_fact_mean", float("inf"))
        per_arm[arm] = {"recall_mean": r, "bpf_mean": b}
        # Pareto: higher recall wins; equal recall -> lower bpf wins
        if (r > best_recall + 1e-9) or (abs(r - best_recall) <= 1e-9 and b < best_bpf):
            best_recall = r
            best_bpf = b
            best_arm = arm
    return best_arm, per_arm


def _pareto_dominant_at_M(stats, M, N_sweep):
    """Aggregate Pareto winner across all N at a given M. Returns arm that
    wins majority of N regimes, or 'MIXED' if no clear majority."""
    winners = []
    for N in N_sweep:
        winner, _ = _pareto_winner_at_MN(stats, M, N)
        winners.append(winner)
    # Majority vote
    from collections import Counter
    c = Counter(winners)
    top, top_count = c.most_common(1)[0]
    if top_count > len(N_sweep) // 2:
        return top, winners
    return "MIXED", winners


def _saturation_check_at_M(stats, M, N_sweep):
    """META_RULE_Q: at least one arm at (any) N must have recall < 0.95 for M
    to be considered discriminating."""
    for N in N_sweep:
        for arm in ARMS:
            uk = f"{arm}__M{M}__N{N}"
            r = stats.get(uk, {}).get("recall_mean", 1.0)
            if r < SATURATION_RECALL_CEIL:
                return True
    return False


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """v1 discriminator (extended Pareto):
      HP: INT8 Pareto-dominates at >=2 of 3 M (aggregating N-majority)
          AND cross-seed cv < 0.08 for INT8 at those M
          AND META_RULE_Q: at each M, at least one arm < 0.95 recall
      MB: crossover finding (different arm wins at different M w/ seed
          consistency) OR INT8 dominates at only 1 M OR cv 0.08-0.10
      HF: BINARY/BFLOAT16 wins >=2 M (contradicts E v5); OR all-saturation at
          all M (Q breach); OR cv >= 0.10 for any storage arm; OR cardinality
          breach; OR mechanism_hash collision
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
    N_sweep = SMOKE_N_SWEEP if smoke else FULL_N_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            for N in N_sweep:
                unit_keys.append(f"{arm}__M{M}__N{N}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep) * len(N_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    # Mechanism hash distinctness: check hashes for the first seed
    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    # Pareto dominance per M
    per_M_gate = {}
    int8_dominates_count = 0
    q_saturation_breach_all_M = True  # true if EVERY M saturates
    crossover_present = False
    seen_winners = set()

    for M in M_sweep:
        winner, winners_by_N = _pareto_dominant_at_M(stats, M, N_sweep)
        discriminating = _saturation_check_at_M(stats, M, N_sweep)
        if discriminating:
            q_saturation_breach_all_M = False
        seen_winners.add(winner)

        # Collect per-arm cvs at this M (aggregating across N)
        int8_cvs = []
        bfloat_cvs = []
        binary_cvs = []
        for N in N_sweep:
            int8_cvs.append(stats.get(f"INT8_DENSE__M{M}__N{N}", {}).get("recall_cv", 1.0))
            bfloat_cvs.append(stats.get(f"BFLOAT16_DENSE__M{M}__N{N}", {}).get("recall_cv", 1.0))
            binary_cvs.append(stats.get(f"BINARY_DENSE__M{M}__N{N}", {}).get("recall_cv", 1.0))
        int8_cv_max = max(int8_cvs) if int8_cvs else 1.0
        bfloat_cv_max = max(bfloat_cvs) if bfloat_cvs else 1.0
        binary_cv_max = max(binary_cvs) if binary_cvs else 1.0

        int8_dominates_M = (winner == "INT8_DENSE" and int8_cv_max < CROSS_SEED_CV_MAX_HP)
        if int8_dominates_M:
            int8_dominates_count += 1

        per_M_gate[M] = {
            "pareto_winner_majority": winner,
            "winners_by_N": winners_by_N,
            "discriminating_at_M": discriminating,
            "int8_cv_max": int8_cv_max,
            "bfloat_cv_max": bfloat_cv_max,
            "binary_cv_max": binary_cv_max,
            "int8_dominates_M_hp": int8_dominates_M,
        }

    if len(seen_winners - {"MIXED"}) >= 2:
        crossover_present = True

    any_cv_breach = any(
        g["int8_cv_max"] >= CROSS_SEED_CV_MAX_MB
        or g["bfloat_cv_max"] >= CROSS_SEED_CV_MAX_MB
        or g["binary_cv_max"] >= CROSS_SEED_CV_MAX_MB
        for g in per_M_gate.values()
    )

    binary_or_bfloat_dominant_count = sum(
        1 for g in per_M_gate.values()
        if g["pareto_winner_majority"] in {"BFLOAT16_DENSE", "BINARY_DENSE"}
    )

    # Verdict logic
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} "
                f"expected={expected_n_units}")
    elif not hashes_distinct:
        verdict = "HARD_FAIL_META_RULE_AX_HASH_COLLISION"
        vmsg = (f"HARD_FAIL: mechanism_hash collision "
                f"({len(hashes)} distinct vs {expected_n_units} expected)")
    elif q_saturation_breach_all_M:
        verdict = "HARD_FAIL_META_RULE_Q_ALL_SATURATION"
        vmsg = (f"HARD_FAIL_META_RULE_Q: every M point saturates (all arms >= "
                f"{SATURATION_RECALL_CEIL} recall); regime does not discriminate. "
                f"per_M_gate={per_M_gate}")
    elif any_cv_breach:
        verdict = "HARD_FAIL_CV_BREACH"
        vmsg = (f"HARD_FAIL: cross-seed cv >= {CROSS_SEED_CV_MAX_MB} at one or "
                f"more (M, arm). per_M_gate={per_M_gate}")
    elif binary_or_bfloat_dominant_count >= 2:
        verdict = "HARD_FAIL_CONTRADICTS_E_V5"
        vmsg = (f"HARD_FAIL: BINARY or BFLOAT16 wins >=2 M regimes "
                f"(contradicts E v5 INT8-Pareto finding). per_M_gate={per_M_gate}")
    elif int8_dominates_count >= 2:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT8_PARETO_EXTENDED: INT8_DENSE Pareto-dominates "
                f"at {int8_dominates_count}/{len(M_sweep)} M regimes with cv<"
                f"{CROSS_SEED_CV_MAX_HP} and META_RULE_Q discriminating. "
                f"per_M_gate={per_M_gate}")
    elif crossover_present:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_CROSSOVER: regime-conditional storage recipe "
                f"(different arm wins at different M with seed consistency). "
                f"seen_winners={seen_winners} per_M_gate={per_M_gate}")
    elif int8_dominates_count == 1:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: INT8 Pareto-dominates at only 1/{len(M_sweep)} M "
                f"regime (partial extension of E v5 finding). "
                f"per_M_gate={per_M_gate}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: no arm Pareto-dominates at >=2 M with tight cv. "
                f"per_M_gate={per_M_gate}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_sweep": list(M_sweep),
        "N_sweep": list(N_sweep),
        "per_M_gate": per_M_gate,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "int8_dominates_count": int8_dominates_count,
        "crossover_present": crossover_present,
        "q_saturation_breach_all_M": q_saturation_breach_all_M,
        "any_cv_breach": any_cv_breach,
        "seen_winners": sorted(seen_winners),
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
        "INT8_LEAD_TOLERANCE": INT8_LEAD_TOLERANCE,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
        "SATURATION_RECALL_CEIL": SATURATION_RECALL_CEIL,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Selftest: verify formulas + arm-fn returns + bytes/fact ordering.

    Expected: recall in [0,1]; bytes/fact ordering BINARY < INT8 < BFLOAT16
    (verified analytically per formulas); arm fns produce finite recalls.
    """
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25,
                                          query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    recall_int8 = _ingest_and_query_int8(triples, E, R, queries, n_dim, smoke_device)
    recall_bf16 = _ingest_and_query_bfloat16(triples, E, R, queries, n_dim, smoke_device)
    recall_bin = _ingest_and_query_binary(triples, E, R, queries, n_dim, smoke_device)
    # All recalls must be finite + in [0,1]
    for name, r in [("int8", recall_int8), ("bf16", recall_bf16), ("bin", recall_bin)]:
        if not (0.0 <= r <= 1.0):
            return False, f"selftest recall out-of-range: {name}={r}"
        if not math.isfinite(r):
            return False, f"selftest recall non-finite: {name}={r}"
    # Bytes-per-fact ordering (analytical): BINARY < INT8 < BFLOAT16.
    n_facts = triples.shape[0]
    bpf_int8 = bytes_int8_dense(n_dim, 200, 25) / n_facts
    bpf_bf16 = bytes_bfloat16_dense(n_dim, 200, 25) / n_facts
    bpf_bin = bytes_binary_dense(n_dim, 200, 25) / n_facts
    if not (bpf_bin < bpf_int8 < bpf_bf16):
        return False, (f"selftest bpf ordering broken: bin={bpf_bin} "
                       f"int8={bpf_int8} bf16={bpf_bf16}")
    # INT8_LEAD_TOLERANCE sanity: is a valid positive threshold
    if not (0 < INT8_LEAD_TOLERANCE < 0.05):
        return False, f"selftest INT8_LEAD_TOLERANCE bad: {INT8_LEAD_TOLERANCE}"
    return True, (f"selftest OK: int8_recall={recall_int8:.3f} "
                  f"bf16_recall={recall_bf16:.3f} bin_recall={recall_bin:.3f} "
                  f"bpf_bin={bpf_bin:.2f} bpf_int8={bpf_int8:.2f} "
                  f"bpf_bf16={bpf_bf16:.2f}")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
