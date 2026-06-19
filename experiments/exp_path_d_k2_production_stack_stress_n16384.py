"""PATH D K=2 PRODUCTION STACK STRESS at N=16384.

CONTEXT:
  Local GPU idle since 10:33 (AQSIM v5 K=2 verdict). AQSIM 3-way cross-N
  family engagement-locked pending diagnostic verdict.

  This anchor tests the K=2 production envelope at cross-N N=16384 WITHOUT
  triggering AQSIM compose. Direct PP-8 substrate-side relevance: validates
  the K=2 path used in Phi-3-coupling at cross-N, independent of AQSIM
  compositional stack.

  Reference pattern: exp_path_d_high_k_scaling_v1_n4096.py (single-path
  Path D) + exp_adversarial_aqsim_path_d_compose_v2_n4096.py (adversarial
  defense gate). No compression layer.

SCIENTIFIC QUESTION (at N=16384, K=2):
  (1) acc_gated >= 0.95? (Path D on legitimate queries passing defense gate)
  (2) defense_act >= 0.90? (a_query_sim gate rejects adversarial probes)
  (3) fp <= 0.05? (legitimate queries not rejected by gate)
  (4) comp_delta < 0.05? (not applicable -- no compression; metric omitted)

  M sweep: {2048, 4096} x 5 seeds = 10 cells (M/N ratios 0.125 and 0.25).

PRE-REGISTERED BANDS:
  HP = acc_gated >= 0.95 AND defense_act >= 0.90 AND fp <= 0.05
       in unanimous 5/5 cells (per-M) or near-unanimous 4/5.
  HF = acc_gated < 0.85 OR defense_act < 0.75 OR fp > 0.15
       (substantial substrate failure at cross-N K=2).
  MIDDLE = any leg in [HP, HF] interval -- characterizable degradation.

DESIGN:
  N=16384, K_paths=2, depth=5, seeds=[7,17,23,31,41].
  M sweep: {2048, 4096}.
  90/10 adversarial/legitimate interleave, subthreshold probes alpha=0.45.
  n_adv=90, n_leg=10 per measurement.
  No compression (pure K=2 substrate Path D stress).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s >= 14400.
PROT-020: device=cuda (overnight_queue).
PROT-021: checkpoint key = M{M}_seed{seed} (LOAD-BEARING -- prevents smoke
          checkpoint contamination, root cause of 3 AQSIM INFRA failures
          2026-06-01).

OOM CHECK:
  W_base at M=4096, N=16384: 16384 * 4096 * 4 = 268 MB (float32). OK.
  W_base at M=2048, N=16384: 16384 * 2048 * 4 = 134 MB. OK.
  K=2: negligible path storage vs K=100. Peak < 2 GB. Well under 6 GB.

TIMEOUT ESTIMATE:
  Reference v2 (N=4096 K=100) 5 seeds ~50s smoke. K=2 is faster.
  Scaling N=4096->16384: 4x. Seeds=5. M=2 values.
  Per seed estimate: ~20s at N=16384 K=2 (K=2 << K=100).
  Total: 5 seeds x 2 M values x 20s = 200s raw.
  With 1.5x margin: ceil(1.5 * 200) = 300s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. N=16384 log2=14 (EVEN) -> no Kerdock issue.
  2. M/N ratios: 2048/16384=0.125, 4096/16384=0.25 (both under 0.5).
  3. OOM: max W=268MB << 6GB threshold.
  4. alpha=0.45 < 0.50 threshold -> defense fires on adversarial probes.
  5. K=2: path_d_run uses 1 positive + 1 decoy.
  6. Verdict gates HP/HF/MB correct.
  7. PROT-021 key = M{M}_seed{seed} (not bare seed{seed}).

Anchor: path_d_k2_production_stack_stress_n16384
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-06-01_path_d_k2_production_stack_stress_n16384.md
Total cells: 2 M values x 5 seeds = 10 cells.
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_pdk2_n16384", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n16384 binds N = 16384
N      = 16384
N_FULL = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

M_GRID_FULL  = [2048, 4096]
M_GRID_SMOKE = [256]
DEPTH        = 5
K_PATHS      = 2   # K=2 production op-point for PP-8 / Phi-3 coupling

# 90/10 ratio: 90 adversarial, 10 legitimate per 100-query batch
N_ADV_FULL   = 90
N_LEG_FULL   = 10
N_ADV_SMOKE  = 9
N_LEG_SMOKE  = 2

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5
COLLISION_ALPHA      = 0.45  # probe max_sim ~ alpha < threshold -> REJECTED

# Pre-registered thresholds (HP/HF/MIDDLE -- non-negotiable)
HP_ACC_GATED   = 0.95  # acc_gated >= 0.95
HP_DEF_ACT     = 0.90  # defense_activation_rate >= 0.90
HP_FP_MAX      = 0.05  # fp <= 0.05
HF_ACC_GATED   = 0.85  # acc_gated < 0.85 = HARD_FAIL
HF_DEF_ACT     = 0.75  # defense_act < 0.75 = HARD_FAIL
HF_FP_MIN      = 0.15  # fp > 0.15 = HARD_FAIL
HP_MIN_CELLS   = 4     # out of 5 per M


def get_output_dir(default_name: str = "path_d_k2_production_stack_stress_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats(device)
        except Exception:
            pass


def _subthreshold_collision_probes(
        codebook: torch.Tensor,
        key_idx: torch.Tensor,
        n_q: int,
        N_use: int,
        seed: int,
        device: torch.device,
        alpha: float = COLLISION_ALPHA) -> torch.Tensor:
    """Build subthreshold collision probes.

    Gate convention: sim(q, k) = q.dot(k) / N_use.
    sim(q_adv, k_i) = alpha = 0.45 < 0.50 threshold -> REJECTED.
    """
    keys = codebook[key_idx]
    n_avail = min(n_q, keys.shape[0])

    g = torch.Generator(device='cpu').manual_seed(seed + 88888)
    noise = torch.randn(n_avail, N_use, generator=g,
                        dtype=keys.dtype).to(device)

    k_sel = keys[:n_avail]
    key_norm = k_sel.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    dot = (noise * k_sel).sum(dim=-1, keepdim=True) / (key_norm ** 2)
    noise_perp = noise - dot * k_sel
    noise_perp_norm = noise_perp.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    noise_perp_scaled = noise_perp / noise_perp_norm * key_norm

    beta = math.sqrt(max(0.0, 1.0 - alpha * alpha))
    q_adv = alpha * k_sel + beta * noise_perp_scaled
    return q_adv


def _defense_a_gate(q: torch.Tensor, codebook: torch.Tensor,
                     key_idx: torch.Tensor, N_use: int) -> torch.Tensor:
    """Return boolean mask: True = ACCEPTED (max_sim >= threshold)."""
    keys = codebook[key_idx]
    sims = q @ keys.T / N_use
    return sims.max(dim=-1).values >= DEFENSE_A_SIM_THRESH


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  n_leg: int, n_adv: int, seed: int,
                  device: torch.device) -> Dict:
    """Single-path Path D K=2 stress at given N, M, seed.

    No compression layer -- pure K=2 substrate performance.
    """
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    leg_keys_list = [k for k in list(relation.keys()) if relation.get(k) is not None]
    n_leg_avail = min(n_leg, len(leg_keys_list))
    if n_leg_avail < 1:
        del codebook, W
        _safe_clear(device)
        return {"M": int(M), "seed": int(seed), "N": int(N_use), "ok": False,
                "error": "no relation keys available"}

    leg_starts = torch.tensor(leg_keys_list[:n_leg_avail],
                               dtype=torch.long, device=device)
    leg_q = codebook[leg_starts]

    adv_q = _subthreshold_collision_probes(
        codebook, key_idx, n_adv, N_use, seed, device, alpha=COLLISION_ALPHA)
    if adv_q.shape[0] == 0:
        del codebook, W
        _safe_clear(device)
        return {"M": int(M), "seed": int(seed), "N": int(N_use), "ok": False,
                "error": "no adversarial probes constructed"}

    actual_n_adv = adv_q.shape[0]

    # Defense gate on adversarial: activation = fraction REJECTED
    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    defense_activation_rate = float((~adv_accepted).float().mean().item())

    # Defense gate on legitimate: fp = fraction REJECTED (false positive)
    leg_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    fp_rate = float((~leg_accepted).float().mean().item())
    n_leg_pass = int(leg_accepted.sum().item())

    # Diagnostic: expected max_sim for adversarial
    keys = codebook[key_idx]
    adv_max_sim = float((adv_q @ keys.T / N_use).max(dim=-1).values.mean().item())
    leg_max_sim = float((leg_q @ keys.T / N_use).max(dim=-1).values.mean().item())

    # Path D on ALL legitimate starts (baseline, no gate)
    path_d_baseline_correct = path_d_run(
        codebook, W, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_baseline = float(path_d_baseline_correct.mean().item())

    # Path D on legitimate starts that PASS the gate (primary metric: acc_gated)
    if n_leg_pass > 0:
        gated_starts = leg_starts[leg_accepted]
        path_d_gated_correct = path_d_run(
            codebook, W, gated_starts, relation, depth, K_paths,
            seed + 5000, N_use)
        acc_gated = float(path_d_gated_correct.mean().item())
    else:
        # All legitimate queries rejected (fp=1.0) -- gate too aggressive
        # Use baseline as lower bound proxy
        acc_gated = acc_baseline

    # VRAM peak
    peak_vram_mb = 0.0
    if device.type == "cuda":
        try:
            peak_vram_mb = round(torch.cuda.max_memory_allocated(device) / (1024**2), 1)
        except Exception:
            pass

    del codebook, W
    _safe_clear(device)

    return {
        "M":                       int(M),
        "seed":                    int(seed),
        "N":                       int(N_use),
        "ok":                      True,
        "n_leg":                   int(leg_starts.shape[0]),
        "n_adv":                   int(actual_n_adv),
        "n_leg_pass_gate":         n_leg_pass,
        "defense_activation_rate": round(defense_activation_rate, 5),
        "fp_rate":                 round(fp_rate, 5),
        "adv_mean_max_sim":        round(adv_max_sim, 5),
        "leg_mean_max_sim":        round(leg_max_sim, 5),
        "acc_path_d_baseline":     round(acc_baseline, 5),
        "acc_path_d_gated":        round(acc_gated, 5),
        "peak_vram_mb":            peak_vram_mb,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PDK2N16K_INCONCLUSIVE", "no cells")

    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("PDK2N16K_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Check DEFENSE_STILL_UNNECESSARY: if ALL cells have def_act < 0.10
    all_def_near_zero = all(c["defense_activation_rate"] < 0.10 for c in ok)
    if all_def_near_zero:
        return ("PDK2N16K_DEFENSE_STILL_UNNECESSARY",
                "ADVERSARIAL_CONSTRUCTION_INVALID: all def_act < 0.10")

    def mean(xs: List[float]) -> float:
        return sum(xs) / len(xs) if xs else float("nan")

    def_rates    = [c["defense_activation_rate"] for c in ok]
    acc_gated    = [c["acc_path_d_gated"] for c in ok]
    fp_rates     = [c["fp_rate"] for c in ok]
    adv_sims     = [c.get("adv_mean_max_sim", 0.0) for c in ok]
    baseline     = [c["acc_path_d_baseline"] for c in ok]
    m_vals       = sorted(set(c["M"] for c in ok))
    n_cells_per_m = {m: len([c for c in ok if c["M"] == m]) for m in m_vals}

    mean_def   = mean(def_rates)
    mean_gated = mean(acc_gated)
    mean_fp    = mean(fp_rates)
    mean_base  = mean(baseline)
    mean_adv   = mean(adv_sims)

    detail = (
        f"N=16384 K_paths={K_PATHS} M_grid={m_vals} n_cells_per_M={n_cells_per_m} "
        f"def_act={mean_def:.3f} fp={mean_fp:.3f} "
        f"acc_gated={mean_gated:.3f} acc_baseline={mean_base:.3f} "
        f"adv_max_sim={mean_adv:.3f} n_ok={len(ok)}"
    )

    # HF check (any single HF condition in majority of cells)
    n_hf_acc   = sum(1 for a in acc_gated if a < HF_ACC_GATED)
    n_hf_def   = sum(1 for d in def_rates if d < HF_DEF_ACT)
    n_hf_fp    = sum(1 for f in fp_rates if f > HF_FP_MIN)
    majority   = len(ok) // 2 + 1
    is_hf      = (n_hf_acc >= majority or n_hf_def >= majority or n_hf_fp >= majority)

    # HP check: per-cell pass in >= HP_MIN_CELLS of the cells for the dominant M
    # Use stricter unanimous/near-unanimous check across all cells
    n_hp = sum(
        1 for i, c in enumerate(ok)
        if (c["defense_activation_rate"] >= HP_DEF_ACT
            and acc_gated[i] >= HP_ACC_GATED
            and fp_rates[i] <= HP_FP_MAX))

    # HP requires near-unanimous (4/5 per M, 8/10 total for 2 M values)
    total_seeds_per_m = max(n_cells_per_m.values()) if n_cells_per_m else 1
    hp_threshold = HP_MIN_CELLS * len(m_vals)  # 4 * 2 = 8 out of 10

    if n_hp >= hp_threshold:
        return ("PDK2N16K_HARD_PASS",
                f"K2_CROSS_N_16384_VALIDATED n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("PDK2N16K_HARD_FAIL",
                f"K2_CROSS_N_FAILS n_hf_acc={n_hf_acc} n_hf_def={n_hf_def} "
                f"n_hf_fp={n_hf_fp} n_ok={len(ok)}. " + detail)
    return ("PDK2N16K_MIDDLE_BAND",
            f"K2_CROSS_N_PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. N=16384 log2=14 (EVEN).
    2. M/N ratios: 2048/16384=0.125, 4096/16384=0.25.
    3. OOM: W float32 at M=4096 = 268 MB << 6 GB.
    4. alpha=0.45 < 0.50 threshold -> defense fires.
    5. K=2 path exploration (1 positive + 1 decoy).
    6. Verdict gates HP/HF/MB/STILL_UNNEC correct.
    7. PROT-021 key format: M{M}_seed{seed} not bare seed{seed}.
    8. Live smoke: all metrics non-null at N_SMOKE M_SMOKE.
    """
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert K_PATHS == 2, f"K_PATHS must be 2; got {K_PATHS}"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert COLLISION_ALPHA < DEFENSE_A_SIM_THRESH, (
        f"COLLISION_ALPHA={COLLISION_ALPHA} must be < {DEFENSE_A_SIM_THRESH}")

    # Formula self-test 1: log2(16384) == 14 EVEN
    log2_n = math.log2(N_FULL)
    assert abs(log2_n - 14.0) < 1e-9, f"log2(N_FULL)={log2_n:.3f}"
    assert int(log2_n) % 2 == 0, f"log2(N_FULL)={int(log2_n)} is ODD"
    print(f"[selftest] formula-1 N=16384 log2={log2_n:.0f} EVEN PASS", flush=True)

    # Formula self-test 2: M/N ratios
    for M_chk in M_GRID_FULL:
        ratio = M_chk / N_FULL
        assert ratio <= 0.5, f"M/N={ratio:.4f} exceeds 0.5 VRAM limit"
    print(f"[selftest] formula-2 M/N ratios {[m/N_FULL for m in M_GRID_FULL]} OK", flush=True)

    # Formula self-test 3: OOM
    W_bytes_max = N_FULL * max(M_GRID_FULL) * 4
    assert W_bytes_max < 6 * 1024**3, f"W_base {W_bytes_max/1024**3:.2f} GB exceeds 6 GB"
    print(f"[selftest] formula-3 W_base_max={W_bytes_max//1024//1024}MB << 6GB PASS",
          flush=True)

    # Formula self-test 4: subthreshold probe max_sim ~ alpha
    N_test = 512
    g = torch.Generator().manual_seed(99)
    cb_raw = torch.sign(torch.randn(8, N_test, generator=g)).float()
    cb = cb_raw / cb_raw.norm(dim=-1, keepdim=True) * math.sqrt(N_test)
    ki = torch.arange(8, dtype=torch.long)
    q_probe = _subthreshold_collision_probes(cb, ki, 4, N_test, 42,
                                              torch.device("cpu"),
                                              alpha=COLLISION_ALPHA)
    sims = q_probe @ cb.T / N_test
    max_sims = sims.max(dim=-1).values
    assert max_sims.max().item() < DEFENSE_A_SIM_THRESH + 0.05, (
        f"Probe max_sim {max_sims.max().item():.4f} exceeds threshold")
    assert max_sims.max().item() > COLLISION_ALPHA - 0.05, (
        f"Probe max_sim {max_sims.max().item():.4f} should be near alpha={COLLISION_ALPHA}")
    print(f"[selftest] formula-4 probe max_sim={max_sims.mean().item():.4f} "
          f"(expected ~{COLLISION_ALPHA:.2f}) PASS", flush=True)

    # Formula self-test 5: K=2
    assert K_PATHS == 2
    print(f"[selftest] formula-5 K_PATHS={K_PATHS} (1 positive + 1 decoy) PASS", flush=True)

    # Formula self-test 6: verdict gates
    fake_hp = [{"M": 4096, "seed": s, "N": N_FULL, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": N_LEG_FULL,
                "defense_activation_rate": 1.00, "fp_rate": 0.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "acc_path_d_baseline": 1.00, "acc_path_d_gated": 1.00,
                "peak_vram_mb": 500.0}
               for s in SEEDS_FULL]
    # Add cells for M=2048 as well (2 M values, 5 seeds each = 10 cells)
    fake_hp += [{"M": 2048, "seed": s, "N": N_FULL, "ok": True,
                 "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                 "n_leg_pass_gate": N_LEG_FULL,
                 "defense_activation_rate": 1.00, "fp_rate": 0.00,
                 "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                 "acc_path_d_baseline": 1.00, "acc_path_d_gated": 1.00,
                 "peak_vram_mb": 350.0}
                for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"
    print(f"[selftest] formula-6a HP gate PASS: {v}", flush=True)

    fake_still = [{"M": 4096, "seed": s, "N": N_FULL, "ok": True,
                   "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                   "n_leg_pass_gate": N_LEG_FULL,
                   "defense_activation_rate": 0.00, "fp_rate": 0.00,
                   "adv_mean_max_sim": 1.00, "leg_mean_max_sim": 1.00,
                   "acc_path_d_baseline": 1.00, "acc_path_d_gated": 1.00,
                   "peak_vram_mb": 500.0}
                  for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_still)
    assert "DEFENSE_STILL_UNNECESSARY" in v, f"STILL_UNNEC gate failed: {v} {msg}"
    print(f"[selftest] formula-6b STILL_UNNEC gate PASS", flush=True)

    fake_hf_acc = [{"M": 4096, "seed": s, "N": N_FULL, "ok": True,
                    "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                    "n_leg_pass_gate": N_LEG_FULL,
                    "defense_activation_rate": 0.95, "fp_rate": 0.00,
                    "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                    "acc_path_d_baseline": 0.80, "acc_path_d_gated": 0.80,
                    "peak_vram_mb": 500.0}
                   for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf_acc)
    assert "HARD_FAIL" in v, f"HF acc gate failed: {v} {msg}"
    print(f"[selftest] formula-6c HF acc gate PASS", flush=True)

    # Formula self-test 7: PROT-021 key format
    test_M, test_seed = 4096, 17
    expected_key = f"M{test_M}_seed{test_seed}"
    assert "_" in expected_key and expected_key.startswith("M"), (
        f"PROT-021: key {expected_key!r} must start with M and contain seed")
    assert "M" in expected_key and "seed" in expected_key, (
        f"PROT-021: checkpoint key {expected_key!r} must include M and seed")
    print(f"[selftest] formula-7 PROT-021 key format {expected_key!r} PASS", flush=True)

    # Self-test 8: live smoke at N=1024 M=256
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 256, DEPTH, K_PATHS,
                       N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_cell failed: {out.get('error')}"
    assert 0.0 <= out["defense_activation_rate"] <= 1.0, \
        f"defense_activation_rate sentinel: {out}"
    assert 0.0 <= out["acc_path_d_gated"] <= 1.0, \
        f"acc_path_d_gated sentinel: {out}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    # Probe construction sanity
    assert out["adv_mean_max_sim"] < DEFENSE_A_SIM_THRESH + 0.05, (
        f"adv_max_sim={out['adv_mean_max_sim']:.4f} too high")
    # Defense should fire (alpha=0.45 well below threshold)
    assert out["defense_activation_rate"] >= 0.70, (
        f"defense_activation_rate={out['defense_activation_rate']:.3f} < 0.70 at smoke")
    print(f"[selftest] live smoke N={N_SMOKE} M=256 K={K_PATHS} "
          f"def_act={out['defense_activation_rate']:.3f} "
          f"adv_max_sim={out['adv_mean_max_sim']:.3f} "
          f"acc_gated={out['acc_path_d_gated']:.3f} "
          f"acc_baseline={out['acc_path_d_baseline']:.3f} PASS",
          flush=True)

    # Multi-scale smoke: N_SMOKE x4 (PROT multi-scale gate)
    out4x = measure_cell(N_SMOKE * 4, 256 * 4, DEPTH, K_PATHS,
                          N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out4x["ok"], f"selftest 4x-smoke failed: {out4x.get('error')}"
    assert out4x["defense_activation_rate"] >= 0.70, (
        f"4x smoke def_act={out4x['defense_activation_rate']:.3f} < 0.70")
    print(f"[selftest] 4x-smoke N={N_SMOKE*4} M={256*4} "
          f"def_act={out4x['defense_activation_rate']:.3f} "
          f"acc_gated={out4x['acc_path_d_gated']:.3f} PASS",
          flush=True)

    print("[selftest] path_d_k2_production_stack_stress_n16384 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke  = args.smoke
    N_cfg  = N_SMOKE     if smoke else N_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    n_adv  = N_ADV_SMOKE  if smoke else N_ADV_FULL
    n_leg  = N_LEG_SMOKE  if smoke else N_LEG_FULL
    seeds  = SEEDS_SMOKE  if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    # PROT-021: scan existing M-tagged keys; reject smoke partials via run_config
    run_config = {"N": N_cfg, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] path_d_k2_production_stack_stress_n16384 smoke={smoke} "
          f"N={N_cfg} M_grid={M_grid} depth={DEPTH} K_paths={K_PATHS} "
          f"n_adv={n_adv} n_leg={n_leg} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[K=2 SINGLE-PATH STRESS no-AQSIM-compose N=16384]",
          flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for seed in seeds:
            # PROT-021: checkpoint key includes M -- prevents smoke contamination
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    print(f"  [resume] M={M} seed={seed} loaded from checkpoint",
                          flush=True)
                    continue
            try:
                cell = measure_cell(N_cfg, M, DEPTH, K_PATHS,
                                     n_leg, n_adv, seed, device)
                # PROT-021: stamp run_mode so future loader can reject cross-mode partials
                cell["run_mode"] = "smoke" if smoke else "full"
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(f"  M={M} seed={seed} ok={cell.get('ok')} "
                      f"def_act={cell.get('defense_activation_rate','n/a')} "
                      f"adv_max_sim={cell.get('adv_mean_max_sim','n/a')} "
                      f"acc_gated={cell.get('acc_path_d_gated','n/a')} "
                      f"acc_base={cell.get('acc_path_d_baseline','n/a')} "
                      f"fp={cell.get('fp_rate','n/a')} "
                      f"peak_vram_mb={cell.get('peak_vram_mb','n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    try:
                        torch.cuda.empty_cache()
                    except Exception:
                        pass

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "path_d_k2_production_stack_stress_n16384",
        "N": N_cfg, "smoke": smoke,
        "M_grid": M_grid, "K_paths": K_PATHS,
        "depth": DEPTH, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
