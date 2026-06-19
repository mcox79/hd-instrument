"""ADVERSARIAL AQSIM x PATH D x COMPRESSION 3-WAY COMPOSITION -- K=2 PRODUCTION OP-POINT at N=4096.

CONTEXT (v2 HARD_PASS at K=100; production-cost validation at K=2):
  V4 path_d_k_fine_grained_transition_v1_n4096 found K=1->K=2 cliff with K=2
  unanimous 1.000 at M=16N, N=4096. K=2 gives ~50x latency reduction vs K=100
  (fewer path candidates explored), but this has NOT been validated on the full
  production stack (v2's 5/5 unanimous HARD_PASS used K_paths=100).

  This anchor repeats the v2 3-way composition (c_quant/bits8 + Path D + a_query_sim
  defense + 90/10 subthreshold probes) with K_paths=2 instead of K=100.

  If still 5/5 unanimous HARD_PASS: production op-point K=2 is empirically validated
  for the full stack -- 50x latency reduction is product-ready.

PRODUCTION STACK (identical to v2 except K_paths=2):
  (1) c_quant/bits8 compressed W
  (2) Path D depth=5 on compressed W, K_paths=2
  (3) a_query_sim defense gate (reject sim < 0.5)
  (4) 90/10 adversarial/legitimate interleave with subthreshold probes alpha=0.45

COMPOSITIONAL QUESTION:
  With K_paths=2 instead of K_paths=100:
  (1) defense_activation_rate >= 0.90 (defense fires on adversarial)?
  (2) path_d_acc_gated_compressed >= 0.95 (Path D accuracy preserved at K=2)?
  (3) compression delta < 5pp (compression preserved at K=2)?

  If YES to all three: K=2 production downgrade validated.

PRE-REGISTERED BANDS (same as v2 -- unchanged HP/HF; only K changes):
  HP = defense_activation_rate >= 0.90
       AND path_d_acc_gated_compressed >= 0.95
       AND |acc_gated_comp - acc_gated_uncomp| <= 0.05
       in 4/5+ seeds.
  HF = defense_activation_rate < 0.50 in majority
       OR path_d_acc_gated_compressed < 0.50 in majority.
       OR special DEFENSE_STILL_UNNECESSARY if all def_act < 0.10.
  MB = otherwise.

DESIGN:
  N=4096, M=2048, depth=5, K_paths=2 (KEY DELTA vs v2's 100), 5-seed.
  Same subthreshold probes alpha=0.45.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout_s = 14400.
PROT-020: device=cuda (GPU queue).
PROT-021: per-seed checkpointing.
HDLAB_EXP_NAME=7d39e13 (enforced via env in queue dispatch).

FORMULA SELF-TESTS:
  1. alpha=0.45 -> probe max_sim ~ 0.45 < 0.50 threshold. Defense fires.
  2. Legitimate stored keys: max_sim = 1.0 >= 0.50. Always accepted (fp=0).
  3. Compression does NOT affect defense gate (gate uses codebook, not W).
  4. K=2: path_d_run explores only 2 candidate paths. Phase boundary result
     says K=2 achieves 1.000 acc at M=16N (2048 memories). Prediction: acc
     preserved at >= 0.95 on compressed W with defense gate.

TIMEOUT ESTIMATE:
  v2 reference elapsed ~100s for 5 seeds at K=100 on GPU.
  K=2 should be faster than K=100 (fewer paths explored per query).
  Upper bound: ceil(1.5 * 30 * (4096/1024)^1.5 * 5) = ceil(1.5*30*8*5) = 1800s.
  PROT-019 floor: 14400s. timeout_s = 14400.

Anchor: aqsim_path_d_compose_k2_production_v1_n4096
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-06-01_aqsim_path_d_compose_k2_production_v1_n4096.md
Total cells: 5 seeds x 1 M value = 5 cells.
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
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_k2prod_v1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N      = 4096
N_FULL = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD   = 2048
M_SMOKE  = 256
DEPTH    = 5
K_PATHS  = 2      # KEY DELTA: K=2 instead of v2's K=100

# 90/10 ratio
N_ADV_FULL   = 90
N_LEG_FULL   = 10
N_ADV_SMOKE  = 9
N_LEG_SMOKE  = 2

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5    # a_query_sim threshold
COLLISION_ALPHA      = 0.45   # probe sim ~ alpha < threshold -> rejected

# Pre-registered thresholds (same as v2 -- bands unchanged)
HP_DEF_ACT_RATE  = 0.90
HP_PATH_D_ACC    = 0.95
HP_COMP_DELTA    = 0.05   # |acc_gated_comp - acc_gated_uncomp| <= 0.05
HF_DEF_ACT_RATE  = 0.50
HF_PATH_D_ACC    = 0.50
HP_MIN_SEEDS     = 4


def get_output_dir(default_name: str = "aqsim_path_d_compose_k2_production_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


def compress_quant_bits8(W: torch.Tensor) -> torch.Tensor:
    """c_quant/bits8: per-tensor symmetric INT8 quantization (dequantized).

    Compression ratio = 4.0 (float32 -> INT8 storage).
    """
    bits = 8
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone()
    n_levels = (1 << (bits - 1)) - 1  # 127
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    return q * scale


def _subthreshold_collision_probes(
        codebook: torch.Tensor,
        key_idx: torch.Tensor,
        n_q: int,
        N_use: int,
        seed: int,
        device: torch.device,
        alpha: float = COLLISION_ALPHA) -> torch.Tensor:
    """Subthreshold collision probes with same norm as stored keys.

    Construction: q_adv = alpha * k_i + sqrt(1 - alpha^2) * noise_perp_scaled
    Gate convention: sim(q, k) = q.dot(k) / N_use.
    For probe: sim(q_adv, k_i) = alpha = 0.45 < 0.50 (REJECTED).
    """
    keys = codebook[key_idx]
    n_avail = min(n_q, keys.shape[0])

    g = torch.Generator(device='cpu').manual_seed(seed + 99999)
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
    """Return boolean mask: True = ACCEPTED (max_sim >= threshold).

    Uses codebook (not W) -- compression of W does NOT affect this.
    """
    keys = codebook[key_idx]
    sims = q @ keys.T / N_use
    return sims.max(dim=-1).values >= DEFENSE_A_SIM_THRESH


def measure_seed(N_use: int, M: int, depth: int, K_paths: int,
                  n_leg: int, n_adv: int, seed: int,
                  device: torch.device) -> Dict:
    """3-way composition: c_quant/bits8 + Path D + a_query_sim defense at K_paths.

    PRIMARY metric: defense_activation_rate + acc_path_d_gated_compressed.
    DIFFERENTIAL: acc_path_d_gated_comp vs acc_path_d_gated_uncomp.
    """
    codebook, W_base, key_idx, val_idx, relation = build_shared(
        N_use, M, seed, device)

    W_comp = compress_quant_bits8(W_base)

    leg_keys_list = [k for k in list(relation.keys()) if relation.get(k) is not None]
    n_leg_avail = min(n_leg, len(leg_keys_list))
    if n_leg_avail < 1:
        del codebook, W_base, W_comp
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no relation keys available"}

    leg_starts = torch.tensor(leg_keys_list[:n_leg_avail],
                               dtype=torch.long, device=device)
    leg_q = codebook[leg_starts]

    adv_q = _subthreshold_collision_probes(
        codebook, key_idx, n_adv, N_use, seed, device, alpha=COLLISION_ALPHA)
    if adv_q.shape[0] == 0:
        del codebook, W_base, W_comp
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial probes constructed"}

    actual_n_adv = adv_q.shape[0]

    # Defense gate on adversarial
    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    defense_activation_rate = float((~adv_accepted).float().mean().item())

    # Defense gate on legitimate (FP check)
    leg_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    fp_rate = float((~leg_accepted).float().mean().item())
    n_leg_pass = int(leg_accepted.sum().item())

    # Diagnostic: max_sim values
    keys = codebook[key_idx]
    adv_max_sim = float((adv_q @ keys.T / N_use).max(dim=-1).values.mean().item())
    leg_max_sim = float((leg_q @ keys.T / N_use).max(dim=-1).values.mean().item())

    compression_ratio = 4.0  # float32 -> INT8

    # Path D on W_base (uncompressed baseline)
    path_d_base_uncompressed = path_d_run(
        codebook, W_base, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_base_uncomp = float(path_d_base_uncompressed.mean().item())

    # Path D on W_comp (compressed baseline)
    path_d_base_compressed = path_d_run(
        codebook, W_comp, leg_starts, relation, depth, K_paths, seed + 1000, N_use)
    acc_base_comp = float(path_d_base_compressed.mean().item())

    # Path D on W_comp + gate (3-way primary metric)
    if n_leg_pass > 0:
        gated_starts = leg_starts[leg_accepted]
        path_d_gated_comp_correct = path_d_run(
            codebook, W_comp, gated_starts, relation, depth, K_paths,
            seed + 5000, N_use)
        acc_gated_comp = float(path_d_gated_comp_correct.mean().item())

        path_d_gated_base_correct = path_d_run(
            codebook, W_base, gated_starts, relation, depth, K_paths,
            seed + 6000, N_use)
        acc_gated_uncomp = float(path_d_gated_base_correct.mean().item())
    else:
        acc_gated_comp   = acc_base_comp
        acc_gated_uncomp = acc_base_uncomp

    comp_delta = abs(acc_gated_comp - acc_gated_uncomp)

    del codebook, W_base, W_comp
    _safe_clear(device)

    return {
        "seed":                      int(seed),
        "M":                         int(M),
        "K_paths":                   K_paths,
        "ok":                        True,
        "n_leg":                     int(leg_starts.shape[0]),
        "n_adv":                     int(actual_n_adv),
        "n_leg_pass_gate":           n_leg_pass,
        "defense_activation_rate":   round(defense_activation_rate, 5),
        "fp_rate":                   round(fp_rate, 5),
        "adv_mean_max_sim":          round(adv_max_sim, 5),
        "leg_mean_max_sim":          round(leg_max_sim, 5),
        "compression_ratio":         compression_ratio,
        "acc_path_d_base_uncompressed": round(acc_base_uncomp, 5),
        "acc_path_d_base_compressed":   round(acc_base_comp, 5),
        "acc_path_d_gated_compressed":  round(acc_gated_comp, 5),
        "acc_path_d_gated_uncompressed": round(acc_gated_uncomp, 5),
        "comp_delta_gated":          round(comp_delta, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("K2PROD_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("K2PROD_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates    = [c["defense_activation_rate"] for c in ok]
    gated_comp   = [c["acc_path_d_gated_compressed"] for c in ok]
    gated_uncomp = [c["acc_path_d_gated_uncompressed"] for c in ok]
    base_comp    = [c["acc_path_d_base_compressed"] for c in ok]
    base_uncomp  = [c["acc_path_d_base_uncompressed"] for c in ok]
    comp_deltas  = [c["comp_delta_gated"] for c in ok]
    fp_rates     = [c["fp_rate"] for c in ok]
    adv_sims     = [c.get("adv_mean_max_sim", 0.0) for c in ok]

    def mean(xs: List[float]) -> float:
        return sum(xs) / len(xs) if xs else float("nan")

    mean_def      = mean(def_rates)
    mean_gated_c  = mean(gated_comp)
    mean_gated_u  = mean(gated_uncomp)
    mean_base_c   = mean(base_comp)
    mean_base_u   = mean(base_uncomp)
    mean_delta    = mean(comp_deltas)
    mean_fp       = mean(fp_rates)
    mean_adv_sim  = mean(adv_sims)

    detail = (
        f"K_paths={K_PATHS} "
        f"def_act={mean_def:.3f} fp={mean_fp:.3f} "
        f"acc_gated_comp={mean_gated_c:.3f} acc_gated_uncomp={mean_gated_u:.3f} "
        f"comp_delta={mean_delta:.4f} "
        f"acc_base_comp={mean_base_c:.3f} acc_base_uncomp={mean_base_u:.3f} "
        f"adv_max_sim={mean_adv_sim:.3f} n_cells={len(ok)}"
    )

    # Special: defense not firing at all (construction still broken)
    all_def_near_zero = all(c["defense_activation_rate"] < 0.10 for c in ok)
    if all_def_near_zero:
        return ("K2PROD_DEFENSE_STILL_UNNECESSARY",
                f"ADVERSARIAL_CONSTRUCTION_INVALID: all def_act < 0.10. " + detail)

    # HP: all 3 legs pass in HP_MIN_SEEDS seeds
    n_hp = sum(
        1 for i, c in enumerate(ok)
        if (c["defense_activation_rate"] >= HP_DEF_ACT_RATE
            and gated_comp[i] >= HP_PATH_D_ACC
            and comp_deltas[i] <= HP_COMP_DELTA))

    # HF: defense fails or Path D collapses in majority
    n_def_fail  = sum(1 for c in ok if c["defense_activation_rate"] < HF_DEF_ACT_RATE)
    n_path_fail = sum(1 for c in gated_comp if c < HF_PATH_D_ACC)
    majority    = len(ok) // 2 + 1
    is_hf       = (n_def_fail >= majority or n_path_fail >= majority)

    if n_hp >= HP_MIN_SEEDS:
        return ("K2PROD_HARD_PASS",
                f"K=2_PRODUCTION_VALIDATED n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("K2PROD_HARD_FAIL",
                f"K=2_STACK_FAILS n_def_fail={n_def_fail} "
                f"n_path_fail={n_path_fail} n_cells={len(ok)}. " + detail)
    return ("K2PROD_MIDDLE_BAND",
            f"K=2_PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. K_PATHS = 2 (key delta from v2's K=100).
    2. Compression ratio = 4.0 (float32 -> INT8).
    3. Subthreshold probe: max_sim < 0.50 -> defense fires.
    4. Defense gate uses codebook (not W) -> compression does NOT affect gate.
    5. Verdict gates HP/STILL_UNNECESSARY/HF/MB work correctly.
    6. Live smoke forward pass: all metrics non-null/non-sentinel.
    """
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert K_PATHS == 2, f"KEY DELTA: K_PATHS must be 2; got {K_PATHS}"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert COLLISION_ALPHA < DEFENSE_A_SIM_THRESH, (
        f"COLLISION_ALPHA={COLLISION_ALPHA} must be < threshold={DEFENSE_A_SIM_THRESH}")

    # Formula self-test 1: K_PATHS binding
    assert K_PATHS == 2, "K_PATHS must be 2 for production op-point validation"

    # Formula self-test 2: compression
    W_test = torch.randn(64, 64)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape, "compression shape changed"
    max_err = float((W_comp - W_test).abs().max().item())
    assert max_err < float(W_test.abs().max().item()) / 10, \
        f"compression error too large: {max_err}"

    # Formula self-test 3: subthreshold probe max_sim
    N_test = 512
    g = torch.Generator().manual_seed(42)
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
    print(f"[selftest] formula-3 probe max_sim={max_sims.mean().item():.4f} "
          f"(expected ~{COLLISION_ALPHA:.2f} < {DEFENSE_A_SIM_THRESH})", flush=True)

    # Formula self-test 4: defense gate independence from W
    import inspect
    sig = inspect.signature(_defense_a_gate)
    params = list(sig.parameters.keys())
    assert "W" not in params, (
        f"_defense_a_gate should not accept W parameter; got: {params}")
    print(f"[selftest] formula-4 gate params={params} (no W -> compression independent)",
          flush=True)

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "K_paths": K_PATHS, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": N_LEG_FULL,
                "defense_activation_rate": 0.97, "fp_rate": 0.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "compression_ratio": 4.0,
                "acc_path_d_base_uncompressed": 0.98,
                "acc_path_d_base_compressed":   0.97,
                "acc_path_d_gated_compressed":  0.97,
                "acc_path_d_gated_uncompressed": 0.98,
                "comp_delta_gated": 0.01}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate STILL_UNNECESSARY
    fake_still = [{"seed": s, "M": M_PROD, "K_paths": K_PATHS, "ok": True,
                   "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                   "n_leg_pass_gate": N_LEG_FULL,
                   "defense_activation_rate": 0.00, "fp_rate": 0.00,
                   "adv_mean_max_sim": 1.00, "leg_mean_max_sim": 1.00,
                   "compression_ratio": 4.0,
                   "acc_path_d_base_uncompressed": 1.00,
                   "acc_path_d_base_compressed":   1.00,
                   "acc_path_d_gated_compressed":  1.00,
                   "acc_path_d_gated_uncompressed": 1.00,
                   "comp_delta_gated": 0.00}
                  for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_still)
    assert "DEFENSE_STILL_UNNECESSARY" in v, f"STILL_UNNEC gate failed: {v} {msg}"

    # Verdict gate HF (path fails)
    fake_hf = [{"seed": s, "M": M_PROD, "K_paths": K_PATHS, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": N_LEG_FULL,
                "defense_activation_rate": 0.97, "fp_rate": 0.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "compression_ratio": 4.0,
                "acc_path_d_base_uncompressed": 0.97,
                "acc_path_d_base_compressed":   0.96,
                "acc_path_d_gated_compressed":  0.30,
                "acc_path_d_gated_uncompressed": 0.95,
                "comp_delta_gated": 0.65}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB
    fake_mb = ([{"seed": s, "M": M_PROD, "K_paths": K_PATHS, "ok": True,
                 "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                 "n_leg_pass_gate": N_LEG_FULL,
                 "defense_activation_rate": 0.95, "fp_rate": 0.00,
                 "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                 "compression_ratio": 4.0,
                 "acc_path_d_base_uncompressed": 0.98,
                 "acc_path_d_base_compressed":   0.97,
                 "acc_path_d_gated_compressed":  0.97,
                 "acc_path_d_gated_uncompressed": 0.98,
                 "comp_delta_gated": 0.01}
                for s in [7, 17]]
               + [{"seed": s, "M": M_PROD, "K_paths": K_PATHS, "ok": True,
                   "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                   "n_leg_pass_gate": 8,
                   "defense_activation_rate": 0.80, "fp_rate": 0.05,
                   "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                   "compression_ratio": 4.0,
                   "acc_path_d_base_uncompressed": 0.90,
                   "acc_path_d_base_compressed":   0.88,
                   "acc_path_d_gated_compressed":  0.80,
                   "acc_path_d_gated_uncompressed": 0.89,
                   "comp_delta_gated": 0.09}
                  for s in [23, 31, 41]])
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, DEPTH, K_PATHS,
                        N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert 0.0 <= out["defense_activation_rate"] <= 1.0, \
        f"defense_activation_rate sentinel: {out}"
    assert 0.0 <= out["acc_path_d_base_uncompressed"] <= 1.0, \
        f"acc_base_uncomp sentinel: {out}"
    assert 0.0 <= out["acc_path_d_base_compressed"] <= 1.0, \
        f"acc_base_comp sentinel: {out}"
    assert 0.0 <= out["acc_path_d_gated_compressed"] <= 1.0, \
        f"acc_gated_comp sentinel: {out}"
    assert out["adv_mean_max_sim"] < DEFENSE_A_SIM_THRESH + 0.05, (
        f"adv_mean_max_sim={out['adv_mean_max_sim']:.4f} should be < threshold+0.05")
    assert out["defense_activation_rate"] >= 0.80, (
        f"defense_activation_rate={out['defense_activation_rate']:.3f} >= 0.80 expected")
    assert out["compression_ratio"] == 4.0, \
        f"compression_ratio not 4.0: {out['compression_ratio']}"
    assert out["K_paths"] == 2, f"K_paths not 2: {out['K_paths']}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    print(f"[selftest] aqsim_path_d_compose_k2_production_v1_n4096 PASS "
          f"K_paths={K_PATHS} "
          f"def_act={out['defense_activation_rate']:.3f} "
          f"adv_max_sim={out['adv_mean_max_sim']:.3f} "
          f"acc_gated_comp={out['acc_path_d_gated_compressed']:.3f} "
          f"comp_delta={out['comp_delta_gated']:.4f}", flush=True)


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
    M      = M_SMOKE     if smoke else M_PROD
    n_adv  = N_ADV_SMOKE if smoke else N_ADV_FULL
    n_leg  = N_LEG_SMOKE if smoke else N_LEG_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] aqsim_path_d_compose_k2_production_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} depth={DEPTH} K_paths={K_PATHS} "
          f"n_adv={n_adv} n_leg={n_leg} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[K=2 production op-point: bits8_compression + Path_D + a_query_sim_defense "
          f"alpha={COLLISION_ALPHA} 90/10 ratio]",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            cell = measure_seed(N_cfg, M, DEPTH, K_PATHS,
                                  n_leg, n_adv, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"def_act={cell.get('defense_activation_rate','n/a')} "
                  f"adv_max_sim={cell.get('adv_mean_max_sim','n/a')} "
                  f"acc_gated_comp={cell.get('acc_path_d_gated_compressed','n/a')} "
                  f"comp_delta={cell.get('comp_delta_gated','n/a')} "
                  f"K_paths={K_PATHS} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "aqsim_path_d_compose_k2_production_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M,
        "depth": DEPTH, "K_paths": K_PATHS,
        "n_adv": n_adv, "n_leg": n_leg, "seeds": seeds,
        "collision_alpha": COLLISION_ALPHA,
        "defense_thresh": DEFENSE_A_SIM_THRESH,
        "cells": cells,
        "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
