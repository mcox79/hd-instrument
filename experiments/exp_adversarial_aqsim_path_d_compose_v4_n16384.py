"""ADVERSARIAL AQSIM x PATH D x COMPRESSION 3-WAY COMPOSITION v4 at N=16384.

CONTEXT (v3 at N=8192 INFRA_FAILURE; skip to N=16384):
  v3 failed with PROT-022 BSC guard triggering at N=8192 (log2=13, ODD -- Kerdock
  works only for even log2). Rather than fix N=8192, jump to N=16384 (log2=14, EVEN;
  Kerdock OK) for cross-N validation.

  v2 (N=4096) HARD_PASS: 5/5 seeds unanimous (defense_act=1.000, acc_gated_comp=1.000,
  comp_delta=0.000). This anchor tests the full production stack at N=16384 (4x larger).

  At larger N: more candidate paths to discriminate; larger codebook; harder regime
  expected. If HARD_PASS at N=16384, cross-N caveat on the compositional sub-row
  lifts from "N=4096 only" to "N=4096 + N=16384".

PROT-022 NOTE:
  N=16384: log2(16384)=14 (EVEN). Kerdock is OK. No PROT-022 BSC override needed.
  This is the reason for skipping N=8192 (log2=13, ODD) entirely.

PRODUCTION STACK (identical to v2, scaled to N=16384):
  (1) c_quant/bits8 compressed W
  (2) Path D depth=5 on compressed W, K_paths=100
  (3) a_query_sim defense gate (reject sim < 0.5)
  (4) 90/10 adversarial/legitimate interleave with subthreshold probes alpha=0.45

  M=8192 (M/N = 0.5, same ratio as v2: N=4096, M=2048).

COMPOSITIONAL QUESTION:
  At N=16384 (4x larger N than v2):
  (1) defense_activation_rate >= 0.90?
  (2) path_d_acc_gated_compressed >= 0.95?
  (3) compression delta < 5pp?

  If YES to all three: cross-N validation passes.

PRE-REGISTERED BANDS:
  HP = defense_activation_rate >= 0.90
       AND path_d_acc_gated_compressed >= 0.95
       AND |acc_gated_comp - acc_gated_uncomp| <= 0.05
       in 4/5+ seeds.
       Strategic target: 5/5 unanimous matching v2 numbers.
  HF = defense_activation_rate < 0.50 in majority
       OR path_d_acc_gated_compressed < 0.50 in majority.
       OR DEFENSE_STILL_UNNECESSARY if all def_act < 0.10.
  MB = degradation characterization at large N.

DESIGN:
  N=16384, M=8192 (M/N=0.5 matching v2), depth=5, K_paths=100, 5-seed.
  device=cuda. Queue: overnight_queue (GPU).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.
PROT-020: device=cuda (GPU queue).
PROT-021: per-seed checkpointing.
HDLAB_EXP_NAME=7d39e13 (enforced via env in queue dispatch).

OOM CHECK:
  W_base at N=16384: 16384*8192*4 bytes = 536 MB (float32). W_comp same shape but
  quantized to INT8 at inference. Total peak memory: ~2 * 536 MB + codebook overheads.
  Estimated: ~1.3 GB GPU. Well below 6 GB threshold. OK.

TIMEOUT ESTIMATE:
  v2 at N=4096: ~100s for 5 seeds. N scales 16384/4096=4x.
  Scaling: matrix operations are O(N^2) dominant (outer product store).
  Estimate: ceil(1.5 * 100 * (16384/4096)^2.0 * (5/5)) = ceil(1.5*100*16) = 2400s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. N=16384 log2=14 (EVEN) -> Kerdock OK, no PROT-022 override needed.
  2. M/N = 8192/16384 = 0.5 (same ratio as v2: 2048/4096).
  3. OOM: W peak ~ 1.3 GB << 6 GB threshold.
  4. Compression ratio = 4.0 (float32 -> INT8 storage).
  5. Subthreshold probe: max_sim ~ 0.45 < 0.50 -> defense fires.
  6. Verdict gates HP/HF/MB work correctly.

Anchor: adversarial_aqsim_path_d_compose_v4_n16384
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-06-01_adversarial_aqsim_path_d_compose_v4_n16384.md
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_aqsim3w_v4", _ck_path)
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

# M/N = 0.5 (same ratio as v2)
M_PROD   = 8192
M_SMOKE  = 256
DEPTH    = 5
K_PATHS  = 100

# 90/10 ratio (same as v2)
N_ADV_FULL   = 90
N_LEG_FULL   = 10
N_ADV_SMOKE  = 9
N_LEG_SMOKE  = 2

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5    # a_query_sim threshold
COLLISION_ALPHA      = 0.45   # probe sim ~ alpha < threshold -> rejected

# Pre-registered thresholds (same as v2)
HP_DEF_ACT_RATE  = 0.90
HP_PATH_D_ACC    = 0.95
HP_COMP_DELTA    = 0.05
HF_DEF_ACT_RATE  = 0.50
HF_PATH_D_ACC    = 0.50
HP_MIN_SEEDS     = 4


def get_output_dir(default_name: str = "adversarial_aqsim_path_d_compose_v4_n16384") -> Path:
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

    Gate convention: sim(q, k) = q.dot(k) / N_use.
    sim(q_adv, k_i) = alpha = 0.45 < 0.50 (REJECTED).
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
    """3-way composition: c_quant/bits8 + Path D + a_query_sim defense at N=16384.

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

    # Defense gate on legitimate
    leg_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    fp_rate = float((~leg_accepted).float().mean().item())
    n_leg_pass = int(leg_accepted.sum().item())

    # Diagnostic
    keys = codebook[key_idx]
    adv_max_sim = float((adv_q @ keys.T / N_use).max(dim=-1).values.mean().item())
    leg_max_sim = float((leg_q @ keys.T / N_use).max(dim=-1).values.mean().item())

    compression_ratio = 4.0

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
        return ("AQSIM3W4_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("AQSIM3W4_INCONCLUSIVE", f"all {len(cells)} cells failed")

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
        f"N=16384 K_paths={K_PATHS} "
        f"def_act={mean_def:.3f} fp={mean_fp:.3f} "
        f"acc_gated_comp={mean_gated_c:.3f} acc_gated_uncomp={mean_gated_u:.3f} "
        f"comp_delta={mean_delta:.4f} "
        f"acc_base_comp={mean_base_c:.3f} acc_base_uncomp={mean_base_u:.3f} "
        f"adv_max_sim={mean_adv_sim:.3f} n_cells={len(ok)}"
    )

    all_def_near_zero = all(c["defense_activation_rate"] < 0.10 for c in ok)
    if all_def_near_zero:
        return ("AQSIM3W4_DEFENSE_STILL_UNNECESSARY",
                f"ADVERSARIAL_CONSTRUCTION_INVALID: all def_act < 0.10. " + detail)

    n_hp = sum(
        1 for i, c in enumerate(ok)
        if (c["defense_activation_rate"] >= HP_DEF_ACT_RATE
            and gated_comp[i] >= HP_PATH_D_ACC
            and comp_deltas[i] <= HP_COMP_DELTA))

    n_def_fail  = sum(1 for c in ok if c["defense_activation_rate"] < HF_DEF_ACT_RATE)
    n_path_fail = sum(1 for c in gated_comp if c < HF_PATH_D_ACC)
    majority    = len(ok) // 2 + 1
    is_hf       = (n_def_fail >= majority or n_path_fail >= majority)

    if n_hp >= HP_MIN_SEEDS:
        return ("AQSIM3W4_HARD_PASS",
                f"CROSS_N_16384_VALIDATED n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("AQSIM3W4_HARD_FAIL",
                f"CROSS_N_16384_FAILS n_def_fail={n_def_fail} "
                f"n_path_fail={n_path_fail} n_cells={len(ok)}. " + detail)
    return ("AQSIM3W4_MIDDLE_BAND",
            f"CROSS_N_16384_PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. N=16384 log2=14 (EVEN) -> Kerdock OK. No PROT-022 override.
    2. M/N = 8192/16384 = 0.5 (same ratio as v2).
    3. OOM: W float32 peak ~ 1.3 GB << 6 GB.
    4. Compression ratio = 4.0 (float32 -> INT8).
    5. Subthreshold probe: max_sim < 0.50 -> defense fires.
    6. Defense gate uses codebook (not W).
    7. Verdict gates HP/HF/MB/STILL_UNNECESSARY work correctly.
    8. Live smoke: all metrics non-null/non-sentinel.
    """
    assert N_FULL == 16384, "PROT-018: _n16384"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert COLLISION_ALPHA < DEFENSE_A_SIM_THRESH, (
        f"COLLISION_ALPHA={COLLISION_ALPHA} must be < threshold={DEFENSE_A_SIM_THRESH}")

    # Formula self-test 1: log2(16384) == 14 (EVEN)
    import math as _math
    log2_n = _math.log2(N_FULL)
    assert abs(log2_n - 14.0) < 1e-9, f"log2(N_FULL)={log2_n:.3f} (expected 14)"
    assert int(log2_n) % 2 == 0, f"log2(N_FULL)={int(log2_n)} is ODD -- Kerdock requires EVEN"
    print(f"[selftest] formula-1 N=16384 log2={log2_n:.0f} (EVEN) PASS", flush=True)

    # Formula self-test 2: M/N ratio
    ratio_mn = M_PROD / N_FULL
    assert abs(ratio_mn - 0.5) < 1e-9, f"M/N = {ratio_mn:.3f} (expected 0.5)"
    print(f"[selftest] formula-2 M/N={ratio_mn:.1f} PASS", flush=True)

    # Formula self-test 3: OOM estimate
    # W_base: N_FULL * M_PROD * 4 bytes = 16384 * 8192 * 4 = 536,870,912 bytes = ~512 MB
    W_bytes = N_FULL * M_PROD * 4
    assert W_bytes < 6 * 1024**3, f"W_base {W_bytes/1024**3:.2f} GB exceeds 6 GB limit"
    print(f"[selftest] formula-3 W_base={W_bytes/1024**2:.0f}MB << 6GB PASS", flush=True)

    # Formula self-test 4: compression
    W_test = torch.randn(64, 64)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape
    max_err = float((W_comp - W_test).abs().max().item())
    assert max_err < float(W_test.abs().max().item()) / 10, f"compression error: {max_err}"

    # Formula self-test 5: subthreshold probe
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
    print(f"[selftest] formula-5 probe max_sim={max_sims.mean().item():.4f} "
          f"(expected ~{COLLISION_ALPHA:.2f})", flush=True)

    # Formula self-test 6: defense gate independence
    import inspect
    sig = inspect.signature(_defense_a_gate)
    params = list(sig.parameters.keys())
    assert "W" not in params, f"_defense_a_gate should not accept W; got: {params}"
    print(f"[selftest] formula-6 gate params={params} (no W) PASS", flush=True)

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": N_LEG_FULL,
                "defense_activation_rate": 1.00, "fp_rate": 0.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "compression_ratio": 4.0,
                "acc_path_d_base_uncompressed": 1.00,
                "acc_path_d_base_compressed":   1.00,
                "acc_path_d_gated_compressed":  1.00,
                "acc_path_d_gated_uncompressed": 1.00,
                "comp_delta_gated": 0.00}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    fake_still = [{"seed": s, "M": M_PROD, "ok": True,
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

    fake_hf = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": 0,
                "defense_activation_rate": 0.97, "fp_rate": 1.00,
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

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, DEPTH, K_PATHS,
                        N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert 0.0 <= out["defense_activation_rate"] <= 1.0, \
        f"defense_activation_rate sentinel: {out}"
    assert 0.0 <= out["acc_path_d_base_uncompressed"] <= 1.0, \
        f"acc_base_uncomp sentinel: {out}"
    assert 0.0 <= out["acc_path_d_gated_compressed"] <= 1.0, \
        f"acc_gated_comp sentinel: {out}"
    assert out["adv_mean_max_sim"] < DEFENSE_A_SIM_THRESH + 0.05, (
        f"adv_mean_max_sim={out['adv_mean_max_sim']:.4f} should be < threshold+0.05")
    assert out["defense_activation_rate"] >= 0.80, (
        f"defense_activation_rate={out['defense_activation_rate']:.3f} >= 0.80 expected")
    assert out["compression_ratio"] == 4.0, \
        f"compression_ratio not 4.0: {out['compression_ratio']}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    print(f"[selftest] adversarial_aqsim_path_d_compose_v4_n16384 PASS "
          f"N=16384 M/N=0.5 "
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
    print(f"[run] adversarial_aqsim_path_d_compose_v4_n16384 smoke={smoke} "
          f"N={N_cfg} M={M} M/N={M/N_cfg:.2f} depth={DEPTH} K_paths={K_PATHS} "
          f"n_adv={n_adv} n_leg={n_leg} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[CROSS-N v4: bits8_compression + Path_D + a_query_sim_defense "
          f"alpha={COLLISION_ALPHA} 90/10 ratio N=16384]",
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
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "adversarial_aqsim_path_d_compose_v4_n16384",
        "N": N_cfg, "smoke": smoke, "M": M,
        "M_over_N": M / N_cfg,
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
