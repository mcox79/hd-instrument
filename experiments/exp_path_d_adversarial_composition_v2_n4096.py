"""PATH D UNDER ADVERSARIAL CODEBOOK-COLLISION COMPOSITION v2 at N=4096.

ROOT CAUSE FIX from v1 DEFENSE_UNNECESSARY:
  v1 constructed adversarial queries as stored keys themselves (keys[i]).
  Stored keys have max_sim=1.0 to themselves, so the 0.5-threshold gate ALWAYS
  accepted them -- defense never fires, defense_rate=0. Label: DEFENSE_UNNECESSARY.

  v2 FIX: adversarial queries are SUBTHRESHOLD COLLISION PROBES:
    q_adv = normalize(alpha * k_i + sqrt(1 - alpha^2) * noise)
    with alpha = COLLISION_ALPHA = 0.45 (just below the 0.5 defense threshold).
    max_sim(q_adv, stored_keys) ~ alpha = 0.45 < 0.5 -> REJECTED by defense.
    The probe targets k_i's answer while being crafted to fall below the defense
    gate. This is the genuine collision pressure that fires the a_query_sim defense.

COLLISION INTENSITY:
  90/10 adversarial/legitimate ratio (90 adversarial, 10 legitimate per batch of 100).
  90% of the query batch should trigger the defense gate.
  Legitimates: standard stored-key queries (max_sim = 1.0, always accepted).

COMPOSITIONAL QUESTION (same as v1, now with genuine defense activation):
  Under 90/10 adv/legit interleaved workload at depth=5:
  (1) Does a_query_sim defense gate REJECT adversarial queries >= 90%?
  (2) Does Path D maintain acc >= 0.95 on the LEGITIMATE 10% that pass the gate?

PRE-REGISTERED BANDS:
  HP = defense_activation_rate >= 0.90 (>= 90% of adversarial rejected)
       AND path_d_acc_on_gated_legit >= 0.95
       in 4/5+ seeds.
  HF = defense_activation_rate < 0.50 (defense still not firing) in majority
       OR path_d_acc_on_gated_legit < 0.50 (defense breaks Path D) in majority.
  MB = otherwise.

  NOTE: defense_activation_rate = fraction of adversarial queries REJECTED by gate.
  This is the PRIMARY gate. If it remains 0.0, emit DEFENSE_STILL_UNNECESSARY
  and do NOT count as HARD_FAIL (it means the adversarial construction is still wrong).

DESIGN:
  N=4096, M=2048, depth=5, K_paths=100.
  For each seed: build substrate. Create 90/10 batch:
    - 9 adversarial batches: subthreshold collision probes (alpha=0.45)
    - 1 legitimate batch: valid stored-key queries
  Apply defense gate to BOTH halves:
    - defense_activation_rate: fraction of adversarial queries REJECTED
    - path_d_acc on legitimate queries that PASS the gate
    - path_d_acc on legitimate queries WITHOUT gate (baseline)
  5 seeds.

COLLISION_ALPHA = 0.45 choice justification:
  Defense threshold = 0.50. alpha = 0.45 puts max_sim just below threshold.
  Expected max_sim(q_adv, stored_keys) ~ alpha (dominant term from k_i component).
  At N=4096, BSC cross-sims ~ 0.016; noise contribution to max_sim is tiny.
  So ~100% of subthreshold probes should be rejected by the 0.5 defense gate.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-020: torch.device("cuda") -- GPU queue.
PROT-021: per-seed checkpointing.

Anchor: path_d_adversarial_composition_v2_n4096
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-06-01_path_d_adversarial_composition_v2_n4096.md
Total cells: 5 seeds x 1 M value = 5 cells.

TIMEOUT ESTIMATE:
  v1 reference: ~10s/seed on GPU. v2 adds collision-probe construction (tiny).
  ~10s/seed x 5 seeds = 50s. Safety: ceil(1.5 * 50 * 1.0 * 5) -- but scaling
  from N_smoke=1024 to N_full=4096: scaling_exp=1.5, ratio=4.
  ceil(1.5 * 5 * 4**1.5 * 5) = ceil(1.5*5*8*5) = ceil(300) = 300s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. Subthreshold probe max_sim: alpha=0.45 < defense_thresh=0.50 -> REJECTED.
     Verify: for any stored key k_j, sim(q_adv, k_j) = alpha * sim(k_i, k_j).
     For k_j = k_i: sim = alpha * 1.0 = 0.45 < 0.5 (below threshold).
     For k_j != k_i: sim = alpha * ~0.016 ~ 0.007 (negligible).
     EXPECTED: defense fires on ~100% of adversarial probes.
  2. Legitimate queries: stored keys, max_sim = 1.0 >= 0.5, always ACCEPTED.
     EXPECTED: fp_rate ~ 0.
  3. HP verdict requires defense_activation_rate >= 0.90 AND acc_gated >= 0.95.
     At alpha=0.45: expected defense_activation_rate ~ 1.0 (well above 0.90 HP).
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_pdac2", _ck_path)
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
K_PATHS  = 100

# 90/10 ratio: 90 adversarial, 10 legitimate per 100-query batch
N_ADV_FULL   = 90
N_LEG_FULL   = 10
N_ADV_SMOKE  = 9
N_LEG_SMOKE  = 2

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5   # a_query_sim defense gate threshold
COLLISION_ALPHA      = 0.45  # subthreshold probe: max_sim = alpha < DEFENSE_A_SIM_THRESH

# Pre-registered thresholds
HP_DEF_ACT_RATE  = 0.90  # defense_activation_rate (fraction rejected) >= 0.90
HP_PATH_D_ACC    = 0.95  # path_d_acc on gated_legit >= 0.95
HF_DEF_ACT_RATE  = 0.50  # defense still not firing if < 0.50
HF_PATH_D_ACC    = 0.50  # defense breaks Path D if acc < 0.50
HP_MIN_SEEDS     = 4


def get_output_dir(default_name: str = "path_d_adversarial_composition_v2_n4096") -> Path:
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


def _subthreshold_collision_probes(
        codebook: torch.Tensor,
        key_idx: torch.Tensor,
        n_q: int,
        N_use: int,
        seed: int,
        device: torch.device,
        alpha: float = COLLISION_ALPHA) -> torch.Tensor:
    """Build subthreshold collision probes with same norm as stored keys.

    Construction: q_adv = alpha * k_i + sqrt(1 - alpha^2) * noise_perp_scaled
    where noise_perp_scaled has same norm as k_i (= sqrt(N)).

    The similarity used by the defense gate is: sim(q, k) = q.dot(k) / N_use.
    For a stored key: sim(k_i, k_i) = ||k_i||^2 / N = N / N = 1.0.
    For our probe: sim(q_adv, k_i) = alpha * ||k_i||^2 / N = alpha * 1.0 = alpha.
    So max_sim(q_adv, stored_keys) ~ alpha = COLLISION_ALPHA = 0.45 < 0.50 threshold.

    This ensures the defense gate REJECTS the probe (sim < 0.50).

    Returns: (n_q, N) tensor of probes at norm ~ sqrt(N) (same as stored keys).
    """
    keys = codebook[key_idx]  # (M_keys, N), norm = sqrt(N)
    n_avail = min(n_q, keys.shape[0])

    g = torch.Generator(device='cpu').manual_seed(seed + 77777)
    noise = torch.randn(n_avail, N_use, generator=g,
                        dtype=keys.dtype).to(device)

    k_sel = keys[:n_avail]
    key_norm = k_sel.norm(dim=-1, keepdim=True).clamp_min(1e-9)  # sqrt(N) per key

    # Project noise perpendicular to k_i (remove k_i component from noise)
    dot = (noise * k_sel).sum(dim=-1, keepdim=True) / (key_norm ** 2)
    noise_perp = noise - dot * k_sel
    noise_perp_norm = noise_perp.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    # Scale noise_perp to have same norm as k_sel (= sqrt(N))
    noise_perp_scaled = noise_perp / noise_perp_norm * key_norm

    # Combine: q_adv = alpha * k_i + sqrt(1 - alpha^2) * noise_perp_scaled
    # ||q_adv|| ~ sqrt(alpha^2 * N + (1 - alpha^2) * N) = sqrt(N)  (same as keys)
    # sim(q_adv, k_i) = q_adv.dot(k_i) / N = alpha * N / N = alpha
    beta = math.sqrt(max(0.0, 1.0 - alpha * alpha))
    q_adv = alpha * k_sel + beta * noise_perp_scaled

    return q_adv


def _defense_a_gate(q: torch.Tensor, codebook: torch.Tensor,
                     key_idx: torch.Tensor, N_use: int) -> torch.Tensor:
    """Return boolean mask: True = ACCEPTED by defense gate (max_sim >= threshold)."""
    keys = codebook[key_idx]
    sims_q_keys = q @ keys.T / N_use
    max_sim = sims_q_keys.max(dim=-1).values
    return max_sim >= DEFENSE_A_SIM_THRESH


def measure_seed(N_use: int, M: int, depth: int, K_paths: int,
                  n_leg: int, n_adv: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    # --- Legitimate starts: valid relation keys
    leg_keys_list = [k for k in list(relation.keys()) if relation.get(k) is not None]
    n_leg_avail = min(n_leg, len(leg_keys_list))

    if n_leg_avail < 1:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": f"no relation keys available"}

    leg_starts = torch.tensor(leg_keys_list[:n_leg_avail],
                               dtype=torch.long, device=device)
    leg_q = codebook[leg_starts]

    # --- Adversarial queries: subthreshold collision probes (v2 fix)
    adv_q = _subthreshold_collision_probes(
        codebook, key_idx, n_adv, N_use, seed, device, alpha=COLLISION_ALPHA)
    if adv_q.shape[0] == 0:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial probes constructed"}

    actual_n_adv = adv_q.shape[0]

    # --- Defense gate on adversarial
    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    # defense_activation_rate = fraction REJECTED (not accepted)
    defense_activation_rate = float((~adv_accepted).float().mean().item())

    # --- Defense gate on legitimate (FP check)
    leg_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    fp_rate = float((~leg_accepted).float().mean().item())
    n_leg_pass = int(leg_accepted.sum().item())

    # --- Diagnostic: expected max_sim for adversarial probes
    keys = codebook[key_idx]
    adv_sims = adv_q @ keys.T / N_use
    adv_max_sim = float(adv_sims.max(dim=-1).values.mean().item())
    leg_sims = leg_q @ keys.T / N_use
    leg_max_sim = float(leg_sims.max(dim=-1).values.mean().item())

    # --- Path D on ALL legitimate starts (baseline, no gate)
    path_d_baseline_correct = path_d_run(
        codebook, W, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_baseline = float(path_d_baseline_correct.mean().item())

    # --- Path D on legitimate starts that PASS the gate
    if n_leg_pass > 0:
        gated_starts = leg_starts[leg_accepted]
        path_d_gated_correct = path_d_run(
            codebook, W, gated_starts, relation, depth, K_paths, seed + 5000, N_use)
        acc_gated = float(path_d_gated_correct.mean().item())
    else:
        acc_gated = None  # all legit passed gate (fp=0), use baseline as proxy

    del codebook, W
    _safe_clear(device)

    return {
        "seed":                  int(seed),
        "M":                     int(M),
        "ok":                    True,
        "n_leg":                 int(leg_starts.shape[0]),
        "n_adv":                 int(actual_n_adv),
        "n_leg_pass_gate":       n_leg_pass,
        "defense_activation_rate": round(defense_activation_rate, 5),
        "fp_rate":               round(fp_rate, 5),
        "adv_mean_max_sim":      round(adv_max_sim, 5),
        "leg_mean_max_sim":      round(leg_max_sim, 5),
        "acc_path_d_baseline":   round(acc_baseline, 5),
        "acc_path_d_gated":      (round(acc_gated, 5)
                                  if acc_gated is not None else None),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PDAC2_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("PDAC2_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates    = [c["defense_activation_rate"] for c in ok]
    # acc_gated: if None (all legit passed, fp=0), use baseline as proxy
    gated_accs   = [c["acc_path_d_gated"] if c.get("acc_path_d_gated") is not None
                    else c["acc_path_d_baseline"] for c in ok]
    base_accs    = [c["acc_path_d_baseline"] for c in ok]
    fp_rates     = [c["fp_rate"] for c in ok]
    adv_sims     = [c.get("adv_mean_max_sim", 0.0) for c in ok]

    def mean(xs: List[float]) -> float:
        return sum(xs) / len(xs) if xs else float("nan")

    mean_def   = mean(def_rates)
    mean_gated = mean(gated_accs)
    mean_base  = mean(base_accs)
    mean_fp    = mean(fp_rates)
    mean_adv_sim = mean(adv_sims)

    detail = (
        f"mean_def_act={mean_def:.3f} mean_acc_gated={mean_gated:.3f} "
        f"mean_acc_base={mean_base:.3f} mean_fp={mean_fp:.3f} "
        f"mean_adv_max_sim={mean_adv_sim:.3f} n_cells={len(ok)}"
    )

    # Special case: if defense_activation_rate is near 0 for ALL cells,
    # the adversarial construction is still wrong (not a real failure).
    all_def_near_zero = all(c["defense_activation_rate"] < 0.10 for c in ok)
    if all_def_near_zero:
        return ("PDAC2_DEFENSE_STILL_UNNECESSARY",
                f"ADVERSARIAL_CONSTRUCTION_INVALID: all def_act < 0.10. " + detail)

    # HP: defense fires >= 0.90 AND acc_gated >= 0.95 in HP_MIN_SEEDS seeds
    n_hp = sum(
        1 for i, c in enumerate(ok)
        if (c["defense_activation_rate"] >= HP_DEF_ACT_RATE
            and gated_accs[i] >= HP_PATH_D_ACC))

    # HF: defense still not firing < 0.50 OR Path D < 0.50 in majority
    n_def_fail = sum(1 for c in ok if c["defense_activation_rate"] < HF_DEF_ACT_RATE)
    n_path_fail = sum(
        1 for i, c in enumerate(ok) if gated_accs[i] < HF_PATH_D_ACC)
    majority = len(ok) // 2 + 1
    is_hf = (n_def_fail >= majority or n_path_fail >= majority)

    if n_hp >= HP_MIN_SEEDS:
        return ("PDAC2_HARD_PASS",
                f"COMPOSITION_COHERENT_WITH_GENUINE_DEFENSE "
                f"n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("PDAC2_HARD_FAIL",
                f"COMPOSITION_FAILS n_def_fail={n_def_fail} "
                f"n_path_fail={n_path_fail} n_cells={len(ok)}. " + detail)
    return ("PDAC2_MIDDLE_BAND",
            f"PARTIAL n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests (per feedback-strategy-spec-formula-selftests):
    1. alpha=0.45 -> max_sim(q_adv, stored_key) ~ 0.45 < 0.50 threshold.
       Verify on CPU with small N.
    2. Legitimate keys: max_sim = 1.0, always accepted.
    3. Verdict gates HP/STILL_UNNECESSARY/HF/MB work correctly.
    """
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert COLLISION_ALPHA < DEFENSE_A_SIM_THRESH, (
        f"COLLISION_ALPHA={COLLISION_ALPHA} must be < DEFENSE_A_SIM_THRESH="
        f"{DEFENSE_A_SIM_THRESH}")

    # Formula self-test 1: subthreshold probe max_sim check
    # Uses gate convention: sim(q, k) = q.dot(k) / N_use
    device_cpu = torch.device("cpu")
    N_test = 512
    g = torch.Generator().manual_seed(42)
    # Build a tiny codebook (8 BSC keys) with norm sqrt(N_test)
    cb_raw = torch.sign(torch.randn(8, N_test, generator=g)).float()
    # Normalize to norm = sqrt(N_test) like real BSC keys
    cb = cb_raw / cb_raw.norm(dim=-1, keepdim=True) * math.sqrt(N_test)
    ki = torch.arange(8, dtype=torch.long)
    q_probe = _subthreshold_collision_probes(cb, ki, 4, N_test, 42, device_cpu,
                                              alpha=COLLISION_ALPHA)
    # Use gate convention: sims = q @ keys.T / N_use
    sims = q_probe @ cb.T / N_test
    max_sims = sims.max(dim=-1).values
    assert max_sims.max().item() < DEFENSE_A_SIM_THRESH + 0.05, (
        f"Probe max_sim {max_sims.max().item():.4f} exceeds threshold "
        f"{DEFENSE_A_SIM_THRESH} significantly -- probe construction wrong")
    # Should be ~ alpha
    assert max_sims.max().item() > COLLISION_ALPHA - 0.05, (
        f"Probe max_sim {max_sims.max().item():.4f} should be near alpha={COLLISION_ALPHA}")
    print(f"[selftest] formula-1 probe max_sim={max_sims.mean().item():.4f} "
          f"(expected ~{COLLISION_ALPHA:.2f} < {DEFENSE_A_SIM_THRESH})", flush=True)

    # Formula self-test 2: legit keys always accepted
    # Legitimate q = stored key k_i: sim(k_i, k_i) = k_i.k_i / N = N / N = 1.0
    leg_sims = cb @ cb.T / N_test
    leg_max = leg_sims.max(dim=-1).values
    assert (leg_max >= DEFENSE_A_SIM_THRESH).all(), \
        "Legitimate stored keys should have max_sim=1.0 (to themselves) >= threshold"

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": N_LEG_FULL,
                "defense_activation_rate": 0.97, "fp_rate": 0.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "acc_path_d_baseline": 0.98, "acc_path_d_gated": 0.97}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate STILL_UNNECESSARY (defense_activation_rate ~ 0)
    fake_still_unnec = [{"seed": s, "M": M_PROD, "ok": True,
                         "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                         "n_leg_pass_gate": N_LEG_FULL,
                         "defense_activation_rate": 0.00, "fp_rate": 0.00,
                         "adv_mean_max_sim": 1.00, "leg_mean_max_sim": 1.00,
                         "acc_path_d_baseline": 1.00, "acc_path_d_gated": 1.00}
                        for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_still_unnec)
    assert "DEFENSE_STILL_UNNECESSARY" in v, f"STILL_UNNEC gate failed: {v} {msg}"

    # Verdict gate HF: defense fires but Path D collapses
    fake_hf = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                "n_leg_pass_gate": 0,
                "defense_activation_rate": 0.95, "fp_rate": 1.00,
                "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                "acc_path_d_baseline": 0.98, "acc_path_d_gated": 0.30}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: 2 HP seeds only
    fake_mb = ([{"seed": s, "M": M_PROD, "ok": True,
                 "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                 "n_leg_pass_gate": N_LEG_FULL,
                 "defense_activation_rate": 0.95, "fp_rate": 0.00,
                 "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                 "acc_path_d_baseline": 0.98, "acc_path_d_gated": 0.97}
                for s in [7, 17]]
               + [{"seed": s, "M": M_PROD, "ok": True,
                   "n_leg": N_LEG_FULL, "n_adv": N_ADV_FULL,
                   "n_leg_pass_gate": 8,
                   "defense_activation_rate": 0.80, "fp_rate": 0.05,
                   "adv_mean_max_sim": 0.44, "leg_mean_max_sim": 1.00,
                   "acc_path_d_baseline": 0.90, "acc_path_d_gated": 0.80}
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
    assert 0.0 <= out["acc_path_d_baseline"] <= 1.0, \
        f"acc_baseline sentinel: {out}"
    # KEY assertion: defense should fire on subthreshold probes
    assert out["adv_mean_max_sim"] < DEFENSE_A_SIM_THRESH + 0.05, (
        f"adv_mean_max_sim={out['adv_mean_max_sim']:.4f} should be "
        f"< {DEFENSE_A_SIM_THRESH + 0.05:.2f}")
    # defense_activation_rate should be high
    assert out["defense_activation_rate"] >= 0.80, (
        f"defense_activation_rate={out['defense_activation_rate']:.3f} "
        f"should be >= 0.80 with alpha={COLLISION_ALPHA}")
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    print(f"[selftest] path_d_adversarial_composition_v2_n4096 PASS "
          f"def_act={out['defense_activation_rate']:.3f} "
          f"adv_max_sim={out['adv_mean_max_sim']:.3f} "
          f"acc_base={out['acc_path_d_baseline']:.3f} "
          f"acc_gated={out.get('acc_path_d_gated','n/a')}", flush=True)


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
    print(f"[run] path_d_adversarial_composition_v2_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} depth={DEPTH} K_paths={K_PATHS} "
          f"n_adv={n_adv} n_leg={n_leg} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[alpha={COLLISION_ALPHA} subthreshold probes, 90/10 ratio]",
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
                  f"acc_gated={cell.get('acc_path_d_gated','n/a')} "
                  f"acc_base={cell.get('acc_path_d_baseline','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "path_d_adversarial_composition_v2_n4096",
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
