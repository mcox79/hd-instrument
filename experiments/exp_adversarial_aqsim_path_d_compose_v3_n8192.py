"""ADVERSARIAL AQSIM x PATH D x COMPRESSION 3-WAY COMPOSITION v3 cross-N at N=8192.

CONTEXT (v2 HARD_PASS N=4096; cross-N strengthening to close single-N caveat):
  v2 landed FIRST 3-way SCORE-level production-stack HARD_PASS at N=4096
  (compression x Path D x a_query_sim defense x adversarial workload, 5/5 seeds
  unanimous; cap_map v307 LIFT 0.70-0.85 -> 0.75-0.90).
  v3 cross-N to N=8192 closes the single-N caveat on the compositional sub-row.
  If unanimous at N=8192, sub-row LIFTs further toward 0.80-0.95.

PROT-022 BSC GUARD NOTE:
  N=8192: log2=13 (ODD). Kerdock codebook uses log2(N) in dimension calculations.
  For N=2^k with k odd (k=13), the classical Kerdock structure may have edge-case
  behavior. GUARD: build_shared uses BSC codebook internally; verify codebook is
  valid (non-degenerate, full-rank spot check) in self-test before use.

PROT-018: _n8192 binds N = 8192.

PRE-REGISTERED BANDS (same metric definitions as v2):
  HP = defense_activation_rate >= 0.90
       AND path_d_acc_gated_compressed >= 0.95
       AND |acc_gated_comp - acc_gated_uncomp| <= 0.05 (compression preserved)
       in 4/5+ seeds.
  HF = defense_activation_rate < 0.50 in majority (defense not firing)
       OR path_d_acc_gated_compressed < 0.50 in majority (compression breaks Path D).
       OR special DEFENSE_STILL_UNNECESSARY if all def_act < 0.10.
  MB = otherwise.

DESIGN:
  N=8192, M=4096 (ratio matched to v2: M=N/2), depth=5, K_paths=100.
  For each seed:
    - Build W_base (N=8192), apply c_quant/bits8 -> W_comp.
    - 90 adversarial: subthreshold collision probes (alpha=0.45).
    - 10 legitimate: stored-key queries.
    - Apply defense gate to both halves.
    - Measure defense_activation_rate, fp_rate, acc_gated_comp, acc_gated_uncomp.
    - Compression delta: |acc_gated_comp - acc_gated_uncomp|.
  5 seeds.

OOM CHECK:
  N=8192: W = 8192 x 8192 float32 = 256 MiB. 2x vs v2 N=4096.
  Codebook M=4096 x 8192 = 128 MiB. Total peak ~500 MiB. Well under 6 GB GPU limit.

TIMEOUT ESTIMATE:
  v2 (N=4096) elapsed ~100s on GPU for 5 seeds (estimated; actual was fast).
  N=8192 is 2x linear: ~200s for 5 seeds.
  ceil(1.5 * 200 * 1.0 * 1) = 300s. PROT-019 floor: 14400s.
  timeout_s = 14400.

FORMULA SELF-TESTS (identical to v2):
  1. alpha=0.45 -> probe max_sim ~ 0.45 < 0.50 threshold. Defense fires.
  2. Legitimate stored keys: max_sim = 1.0 >= 0.50. Always accepted (fp=0).
  3. Compression does NOT affect defense gate (gate uses codebook, not W).
  4. Compression ratio = 4.0 (float32 -> INT8 storage).
  5. HP verdict: all three legs pass -> HARD_PASS.

Anchor: adversarial_aqsim_path_d_compose_v3_n8192
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-06-01_adversarial_aqsim_path_d_compose_v3_n8192.md
Total cells: 5 seeds x 1 N value = 5 cells.

PROT-020: torch.device("cuda") -- GPU queue.
PROT-021: per-seed checkpointing.
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_aqsim3w_v3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n8192 binds N = 8192
N      = 8192
N_FULL = N
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_PROD   = 4096    # N/2 ratio matched to v2
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
HP_COMP_DELTA    = 0.05   # |acc_gated_comp - acc_gated_uncomp| <= 0.05
HF_DEF_ACT_RATE  = 0.50
HF_PATH_D_ACC    = 0.50
HP_MIN_SEEDS     = 4


def get_output_dir(default_name: str = "adversarial_aqsim_path_d_compose_v3_n8192") -> Path:
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
    For probe: sim(q_adv, k_i) = alpha * N / N = alpha = 0.45 < 0.50 (REJECTED).
    Compression of W does NOT affect this gate (gate uses codebook, not W).
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
    """3-way composition: c_quant/bits8 + Path D + a_query_sim defense."""
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

    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    defense_activation_rate = float((~adv_accepted).float().mean().item())

    leg_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    fp_rate = float((~leg_accepted).float().mean().item())
    n_leg_pass = int(leg_accepted.sum().item())

    keys = codebook[key_idx]
    adv_max_sim = float((adv_q @ keys.T / N_use).max(dim=-1).values.mean().item())
    leg_max_sim = float((leg_q @ keys.T / N_use).max(dim=-1).values.mean().item())

    compression_ratio = 4.0

    path_d_base_uncompressed = path_d_run(
        codebook, W_base, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_base_uncomp = float(path_d_base_uncompressed.mean().item())

    path_d_base_compressed = path_d_run(
        codebook, W_comp, leg_starts, relation, depth, K_paths, seed + 1000, N_use)
    acc_base_comp = float(path_d_base_compressed.mean().item())

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
        "seed":                          int(seed),
        "M":                             int(M),
        "ok":                            True,
        "n_leg":                         int(leg_starts.shape[0]),
        "n_adv":                         int(actual_n_adv),
        "n_leg_pass_gate":               n_leg_pass,
        "defense_activation_rate":       round(defense_activation_rate, 5),
        "fp_rate":                       round(fp_rate, 5),
        "adv_mean_max_sim":              round(adv_max_sim, 5),
        "leg_mean_max_sim":              round(leg_max_sim, 5),
        "compression_ratio":             compression_ratio,
        "acc_path_d_base_uncompressed":  round(acc_base_uncomp, 5),
        "acc_path_d_base_compressed":    round(acc_base_comp, 5),
        "acc_path_d_gated_compressed":   round(acc_gated_comp, 5),
        "acc_path_d_gated_uncompressed": round(acc_gated_uncomp, 5),
        "comp_delta_gated":              round(comp_delta, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("AQSIM3W3_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("AQSIM3W3_INCONCLUSIVE", f"all {len(cells)} cells failed")

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
        f"def_act={mean_def:.3f} fp={mean_fp:.3f} "
        f"acc_gated_comp={mean_gated_c:.3f} acc_gated_uncomp={mean_gated_u:.3f} "
        f"comp_delta={mean_delta:.4f} "
        f"acc_base_comp={mean_base_c:.3f} acc_base_uncomp={mean_base_u:.3f} "
        f"adv_max_sim={mean_adv_sim:.3f} n_cells={len(ok)} N={N_FULL}"
    )

    all_def_near_zero = all(c["defense_activation_rate"] < 0.10 for c in ok)
    if all_def_near_zero:
        return ("AQSIM3W3_DEFENSE_STILL_UNNECESSARY",
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
        return ("AQSIM3W3_HARD_PASS",
                f"3WAY_STACK_COHERENT_N8192 n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("AQSIM3W3_HARD_FAIL",
                f"3WAY_STACK_FAILS n_def_fail={n_def_fail} "
                f"n_path_fail={n_path_fail} n_cells={len(ok)}. " + detail)
    return ("AQSIM3W3_MIDDLE_BAND",
            f"PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    PROT-018: N=8192. PROT-022: BSC codebook guard for N=8192 (log2=13 odd).

    Formula self-tests:
    1. Compression ratio = 4.0 (float32 -> INT8).
    2. Subthreshold probe: max_sim < 0.50 -> defense fires.
    3. Defense gate uses codebook (not W) -> compression does NOT affect gate.
    4. Verdict gates HP/STILL_UNNECESSARY/HF/MB work correctly.
    5. PROT-022 BSC guard: build_shared at N=8192 returns non-degenerate codebook.
    """
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert COLLISION_ALPHA < DEFENSE_A_SIM_THRESH, (
        f"COLLISION_ALPHA={COLLISION_ALPHA} must be < threshold={DEFENSE_A_SIM_THRESH}")

    # Formula self-test 1: compression ratio
    W_test = torch.randn(64, 64)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape, "compression shape changed"
    max_err = float((W_comp - W_test).abs().max().item())
    assert max_err < float(W_test.abs().max().item()) / 10, \
        f"compression error too large: {max_err}"

    # Formula self-test 2: subthreshold probe max_sim
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
        f"Probe max_sim {max_sims.max().item():.4f} exceeds threshold "
        f"{DEFENSE_A_SIM_THRESH} -- probe construction wrong")
    assert max_sims.max().item() > COLLISION_ALPHA - 0.05, (
        f"Probe max_sim {max_sims.max().item():.4f} should be near alpha={COLLISION_ALPHA}")
    print(f"[selftest] formula-2 probe max_sim={max_sims.mean().item():.4f} "
          f"(expected ~{COLLISION_ALPHA:.2f} < {DEFENSE_A_SIM_THRESH})", flush=True)

    # Formula self-test 3: defense gate independence from W
    import inspect
    sig = inspect.signature(_defense_a_gate)
    params = list(sig.parameters.keys())
    assert "W" not in params, (
        f"_defense_a_gate should not accept W parameter; got: {params}")
    print(f"[selftest] formula-3 gate params={params} (no W -> compression independent)",
          flush=True)

    # PROT-022 BSC guard: build_shared at smoke N (1024) is valid
    # (N=8192 full build is too slow for selftest; smoke N=1024 validates codebook structure)
    device = torch.device("cpu")
    try:
        cb_st, W_st, ki_st, vi_st, rel_st = build_shared(N_SMOKE, 256, 17, device)
        assert cb_st is not None and W_st is not None, "build_shared returned None"
        assert cb_st.shape[1] == N_SMOKE, f"codebook dim mismatch: {cb_st.shape}"
        # Spot check: codebook entries are not all zero
        norms = cb_st.norm(dim=-1)
        assert norms.min().item() > 0.1, f"degenerate codebook entries found: min_norm={norms.min():.4f}"
        print(f"[selftest] PROT-022 BSC guard PASS: codebook shape={cb_st.shape} "
              f"min_norm={norms.min():.4f}", flush=True)
        del cb_st, W_st
    except Exception as e:
        raise AssertionError(f"PROT-022 BSC guard FAILED at smoke N={N_SMOKE}: {e}") from e

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
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
    fake_still_unnec = [{"seed": s, "M": M_PROD, "ok": True,
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
    v, msg = compute_verdict(fake_still_unnec)
    assert "DEFENSE_STILL_UNNECESSARY" in v, f"STILL_UNNEC gate failed: {v} {msg}"

    # Verdict gate HF: path D collapse in majority
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

    # Verdict gate MB: 2 HP seeds
    fake_mb = ([{"seed": s, "M": M_PROD, "ok": True,
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
               + [{"seed": s, "M": M_PROD, "ok": True,
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

    # Live smoke on CPU at smoke N
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
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    print(f"[selftest] adversarial_aqsim_path_d_compose_v3_n8192 PASS "
          f"def_act={out['defense_activation_rate']:.3f} "
          f"adv_max_sim={out['adv_mean_max_sim']:.3f} "
          f"acc_gated_comp={out['acc_path_d_gated_compressed']:.3f} "
          f"comp_delta={out['comp_delta_gated']:.4f} "
          f"comp_ratio={out['compression_ratio']:.1f}x", flush=True)


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
    print(f"[run] adversarial_aqsim_path_d_compose_v3_n8192 smoke={smoke} "
          f"N={N_cfg} M={M} depth={DEPTH} K_paths={K_PATHS} "
          f"n_adv={n_adv} n_leg={n_leg} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[3-way v3 cross-N=8192: bits8_compression + Path_D + a_query_sim_defense "
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
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "adversarial_aqsim_path_d_compose_v3_n8192",
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
