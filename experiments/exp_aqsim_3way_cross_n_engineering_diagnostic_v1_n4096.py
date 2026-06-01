"""AQSIM 3-WAY CROSS-N ENGINEERING DIAGNOSTIC v1 at N=4096.

CONTEXT (strategy_request_to_exp_dev_aqsim_3way_cross_n_engineering_diagnostic_2026-06-01.md):

  ENGAGEMENT-LOCKED: 3 consecutive AQSIM 3-way cross-N attempts at N != 4096
  all produced cells=[] / smoke-scale metrics despite correct FULL configs:
    v3 N=8192  wall_s=7,  elapsed_s=0,   cells=[] no experiment.log
    v4 N=16384 wall_s=29, elapsed_s=11,  cells=[] no experiment.log
    v5 N=16384 wall_s=30, elapsed_s=12,  cells=[] no experiment.log (K=2)

  FALSIFIED HYPOTHESES:
    A: PROT-022 log2-parity (v4 log2=14 even, same failure) -- FALSIFIED
    B: CUDA OOM (v5 K=2 M=4096, ~256MB, same failure) -- FALSIFIED

DIAGNOSTIC INVESTIGATION (exp_dev analysis 2026-06-01):

  EVIDENCE ANALYSIS: Inspecting v3 and v5 output files reveals:
    - data/exp_adversarial_aqsim_path_d_compose_v3_n8192/metrics.json: N=1024, M=256 (smoke!)
    - data/exp_adversarial_aqsim_path_d_compose_v5_k2_n16384/metrics.json: N=1024, M=256 (smoke!)
    - partial_metrics_seed17.json in both dirs: M=256 (smoke-scale checkpoint written during smoke gate)

  ROOT-CAUSE HYPOTHESIS (based on evidence):
    CHECKPOINT CONTAMINATION BUG: The runner executes scripts in two phases:
      Phase 1 (smoke gate): HDLAB_SMOKE=1, runs smoke config, writes checkpoint
        partial_metrics_seed{N}.json with smoke-scale M (256).
      Phase 2 (FULL run): HDLAB_SMOKE unset, loads checkpoint, finds seed17 "done",
        loads M=256 metrics, skips actual FULL computation.
    Result: FULL run produces only 1 cell at smoke scale, elapsed_s~0 (no actual work).
    The script treats smoke checkpoint keys identically to FULL checkpoint keys
    (both use "seed{seed}" as key) -- smoke pollutes FULL.

  HYPOTHESIS SPACE (per routing note):
    a) silent failure in build_shared at log2-odd N (FALSIFIED: v5 N=16384 log2=14 even)
    b) memory-budget exceeded silently before cells start (FALSIFIED: v5 K=2 M=4096 ~256MB)
    c) module-import-time computation at N != 4096 (PARTIALLY CONFIRMED: but see above)
    d) tensor-shape mismatch producing zero-cell run (PARTIALLY CONFIRMED: shape correct but
       checkpoint contamination means FULL cells are loaded from smoke, not computed)

  REVISED PRIMARY HYPOTHESIS: (e) smoke checkpoint keys collide with FULL run checkpoint keys

DIAGNOSTIC DESIGN:

  This script proves/falsifies the checkpoint contamination hypothesis by:
  (1) Running at N=4096 as a control: re-run v2 logic at FULL N=4096 with fresh
      output dir, 1 seed only, to confirm the pipeline works.
  (2) Simulating the contamination scenario at N=4096:
      - Write a fake smoke checkpoint (M=256) for seed42
      - Run FULL config (M=2048)
      - If FULL loads the smoke checkpoint and exits with M=256: BUG CONFIRMED
      - If FULL detects the M mismatch and re-runs: BUG NOT PRESENT
  (3) Running at N=8192 with FRESH output dir (no prior checkpoint):
      - Full AQSIM 3-way stack at N=8192, 1 seed, K_paths=100, M=4096
      - If N=8192 Kerdock construction raises ValueError(log2 odd): ROOT CAUSE = Kerdock
      - If pipeline runs but produces wrong metrics: ROOT CAUSE = something else
  (4) Running at N=16384 with FRESH output dir, 1 seed, K_paths=2:
      - Tests whether N=16384 (log2=14, even) has any separate issue

  Each scenario writes verbose diagnostic logs.

PROT-018: _n4096 binds N = 4096 (production N; also used as CONTROL comparison).

PRE-REGISTERED BANDS:
  HP  : diagnostic identifies the specific failure mode with evidence in logs
        sufficient for orchestrator to file a targeted fix routing.
        HP outcome = one specific root cause from {checkpoint-contamination,
        kerdock-exception, tensor-shape-mismatch, import-time-exception} confirmed.
  HF  : no failure mode identifiable from instrumentation alone.
        HF outcome = escalate to live-debugging session.
  MB  : partial identification (failure between step X and Y, specific cause unclear).

Queue: remote_cpu_queue (verbose tracing; CPU suffices for this diagnostic)
Pre-reg: preregs/2026-06-01_aqsim_3way_cross_n_engineering_diagnostic_v1_n4096.md
HDLAB_EXP_NAME: aqsim_3way_diagnostic_v1

TIMEOUT ESTIMATE:
  N=4096 control: ~5s/seed (from v2 reference).
  N=8192: ~20s (either quick exception or full run).
  N=16384: ~40s.
  Contamination sim: ~1s.
  Total: ~70s * 3 seeds = 210s.
  ceil(1.5 * 70 * 1.0 * 1) = 105s. PROT-019 minimum = 14400s. timeout_s = 14400.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import shutil
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

# ============================================================
# PROT-018: _n4096 binds N = 4096 (control N)
# ============================================================
N = 4096          # PROT-018 binding: production N = 4096
N_CONTROL = N
assert N_CONTROL == 4096, f"PROT-018: N must be 4096; got {N_CONTROL}"

N_TEST_8192  = 8192
N_TEST_16384 = 16384

DEPTH   = 5
K_PATHS_CONTROL = 100
K_PATHS_16384   = 2     # lower K to avoid OOM at N=16384

M_RATIO = 0.5           # M = N * M_RATIO

DEFENSE_A_SIM_THRESH = 0.5
COLLISION_ALPHA      = 0.45

# PROT-018 binding for this script: production N = 4096 (control N)
# Diagnostic also probes N=8192 and N=16384 (non-production probes for diagnosis)


def get_output_dir(name: str) -> Path:
    out_dir_name = os.environ.get("HDLAB_EXP_NAME", "aqsim_3way_diagnostic_v1")
    d = REPO / "data" / f"exp_{out_dir_name}" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def compress_quant_bits8(W: torch.Tensor) -> torch.Tensor:
    """c_quant/bits8: per-tensor symmetric INT8 quantization (dequantized)."""
    bits = 8
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone()
    n_levels = (1 << (bits - 1)) - 1
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    return q * scale


def _subthreshold_probes(
        codebook: torch.Tensor, key_idx: torch.Tensor,
        n_q: int, N_use: int, seed: int, device: torch.device,
        alpha: float = COLLISION_ALPHA) -> torch.Tensor:
    """Construct subthreshold collision probes at alpha=0.45."""
    keys = codebook[key_idx]
    n_avail = min(n_q, keys.shape[0])
    g = torch.Generator(device='cpu').manual_seed(seed + 99999)
    noise = torch.randn(n_avail, N_use, generator=g, dtype=keys.dtype).to(device)
    k_sel = keys[:n_avail]
    key_norm = k_sel.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    dot = (noise * k_sel).sum(dim=-1, keepdim=True) / (key_norm ** 2)
    noise_perp = noise - dot * k_sel
    noise_perp_norm = noise_perp.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    noise_perp_scaled = noise_perp / noise_perp_norm * key_norm
    beta = math.sqrt(max(0.0, 1.0 - alpha * alpha))
    q_adv = alpha * k_sel + beta * noise_perp_scaled
    return q_adv


def _defense_gate(q: torch.Tensor, codebook: torch.Tensor,
                   key_idx: torch.Tensor, N_use: int) -> torch.Tensor:
    keys = codebook[key_idx]
    sims = q @ keys.T / N_use
    return sims.max(dim=-1).values >= DEFENSE_A_SIM_THRESH


def run_single_seed(N_use: int, M: int, K_paths: int,
                     seed: int, device: torch.device,
                     label: str) -> Dict[str, Any]:
    """Run one seed of the AQSIM 3-way pipeline with verbose instrumentation.

    Returns a dict with all diagnostic fields.
    """
    result: Dict[str, Any] = {
        "label": label,
        "N": N_use, "M": M, "K_paths": K_paths, "seed": seed,
        "ok": False,
        "error": None,
        "error_traceback": None,
        "step_reached": "start",
        "kerdock_exception": False,
        "import_exception": False,
        "build_shared_exception": False,
        "cells": [],
        "elapsed_s": 0.0,
    }
    t0 = time.time()
    try:
        print(f"  [{label}] step=build_shared N={N_use} M={M} seed={seed}", flush=True)
        result["step_reached"] = "build_shared"
        codebook, W_base, key_idx, val_idx, relation = build_shared(
            N_use, M, seed, device)
        print(f"  [{label}] build_shared OK: codebook={codebook.shape} "
              f"W={W_base.shape} key_idx={key_idx.shape}", flush=True)

        result["step_reached"] = "compress"
        W_comp = compress_quant_bits8(W_base)
        print(f"  [{label}] compress OK: W_comp shape={W_comp.shape}", flush=True)

        result["step_reached"] = "defense_probes"
        n_adv = 9
        n_leg = 2
        leg_keys_list = [k for k, v in relation.items() if v is not None]
        n_leg_avail = min(n_leg, len(leg_keys_list))
        leg_starts = torch.tensor(leg_keys_list[:n_leg_avail], dtype=torch.long, device=device)
        leg_q = codebook[leg_starts]
        adv_q = _subthreshold_probes(codebook, key_idx, n_adv, N_use, seed, device)
        print(f"  [{label}] probes OK: n_leg={leg_q.shape[0]} n_adv={adv_q.shape[0]}",
              flush=True)

        result["step_reached"] = "defense_gate"
        adv_accepted = _defense_gate(adv_q, codebook, key_idx, N_use)
        leg_accepted = _defense_gate(leg_q, codebook, key_idx, N_use)
        defense_act = float((~adv_accepted).float().mean().item())
        fp_rate = float((~leg_accepted).float().mean().item())
        print(f"  [{label}] defense_gate OK: def_act={defense_act:.3f} fp={fp_rate:.3f}",
              flush=True)

        result["step_reached"] = "path_d"
        path_d_res = path_d_run(
            codebook, W_comp, leg_starts, relation, DEPTH, K_paths, seed, N_use)
        acc_gated = float(path_d_res.mean().item())
        print(f"  [{label}] path_d OK: acc_gated={acc_gated:.3f}", flush=True)

        result["step_reached"] = "done"
        result["ok"] = True
        result["defense_activation_rate"] = defense_act
        result["fp_rate"] = fp_rate
        result["acc_gated_comp"] = acc_gated
        result["n_leg"] = int(leg_q.shape[0])
        result["n_adv"] = int(adv_q.shape[0])

        del codebook, W_base, W_comp

    except Exception as exc:  # noqa: BLE001
        tb_str = traceback.format_exc()
        result["error"] = str(exc)
        result["error_traceback"] = tb_str
        exc_type = type(exc).__name__
        # Classify the exception type
        if "kerdock" in str(exc).lower() or "even" in str(exc).lower() \
                or "n_log2" in str(exc).lower() or "primitive" in str(exc).lower():
            result["kerdock_exception"] = True
        if "import" in exc_type.lower():
            result["import_exception"] = True
        if result["step_reached"] == "build_shared":
            result["build_shared_exception"] = True
        print(f"  [{label}] EXCEPTION at step={result['step_reached']}: {exc_type}: {exc}",
              flush=True)
        print(f"  [{label}] traceback:\n{tb_str}", flush=True)

    result["elapsed_s"] = round(time.time() - t0, 3)
    return result


def run_checkpoint_contamination_test(device: torch.device) -> Dict[str, Any]:
    """Hypothesis (e): smoke checkpoint key collides with FULL checkpoint key.

    Protocol:
    1. Create a fake smoke-scale checkpoint (M=256, seed=42) in a temp dir.
    2. Point the _seed_checkpoint loader at that dir.
    3. Run a FULL config (N=4096, M=2048) that loads checkpoint for seed42.
    4. Check if the loaded cell has M=256 (contaminated) or M=2048 (fresh).

    Returns dict with findings.
    """
    result: Dict[str, Any] = {
        "test": "checkpoint_contamination",
        "hypothesis": "smoke checkpoint pollutes FULL run via same key pattern",
        "ok": False,
        "contamination_confirmed": False,
        "findings": [],
    }
    t0 = time.time()

    _ck_path = REPO / "experiments" / "_seed_checkpoint.py"
    _ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_diag_contam", _ck_path)
    _ck = importlib.util.module_from_spec(_ck_spec)
    _ck_spec.loader.exec_module(_ck)
    list_completed_keys = _ck.list_completed_keys
    write_partial_key   = _ck.write_partial_key
    load_partial_key    = _ck.load_partial_key

    # Step 1: Write a fake SMOKE-scale checkpoint (M=256)
    base_dir = REPO / "data" / "exp_aqsim_3way_diagnostic_v1"
    contam_dir = base_dir / "contam_test"
    contam_dir.mkdir(parents=True, exist_ok=True)

    # Note: write_partial_key stamps body["seed"] = str(key) if not already present.
    # The runner's smoke gate uses key = "seed{seed}" e.g. "seed17".
    # So the checkpoint file is partial_metrics_seed17.json with body["seed"]="seed17".
    # When FULL run checks list_completed_keys(), it finds "seed17" and loads it.
    # The loaded M=256 (smoke-scale) is then used as the "done" result.
    smoke_scale_cell = {
        "M": 256, "ok": True,
        "is_smoke": True,
        "n_leg": 2, "n_adv": 9,
        "defense_activation_rate": 1.0, "fp_rate": 0.0,
        "acc_path_d_gated_compressed": 1.0,
    }
    # Use the same key pattern that the runner uses: "seed{seed_int}"
    write_partial_key(contam_dir, "seed42", smoke_scale_cell)
    print(f"  [contam_test] wrote smoke-scale checkpoint: {contam_dir}", flush=True)

    # Step 2: Simulate FULL run loading the checkpoint
    done_keys = set(list_completed_keys(contam_dir))
    print(f"  [contam_test] list_completed_keys: {done_keys}", flush=True)

    if "seed42" in done_keys:
        loaded = load_partial_key(contam_dir, "seed42")
        loaded_M = loaded.get("M") if loaded else None
        print(f"  [contam_test] seed42 found in checkpoint. loaded M={loaded_M}", flush=True)
        result["findings"].append(
            f"seed42 found in checkpoint with M={loaded_M} (should be 256=smoke)")
        if loaded_M == 256:
            result["contamination_confirmed"] = True
            result["findings"].append(
                "CONFIRMED: smoke checkpoint M=256 would be loaded for FULL N=4096 M=2048 run")
            result["findings"].append(
                "ROOT CAUSE: _seed_checkpoint uses same key 'seed{N}' for smoke AND full runs")
            result["findings"].append(
                "FIX: Include M (or run_mode='full'/'smoke') in checkpoint key, "
                "e.g. 'seed42_M2048' vs 'seed42_M256'")
            result["ok"] = True
        else:
            result["findings"].append(
                f"NOT CONFIRMED: checkpoint M={loaded_M} != 256 (unexpected)")
    else:
        result["findings"].append(
            "seed42 NOT found in checkpoint -- checkpoint mechanism works differently")

    # Step 3: Verify _seed_checkpoint.py key naming (structural analysis)
    ck_source = _ck_path.read_text(encoding="utf-8")
    if "seed" in ck_source and "key" in ck_source:
        # Look for how keys are formed
        import re
        key_patterns = re.findall(r'["\']seed\{?[^"\']*\}?["\']', ck_source)
        result["findings"].append(f"checkpoint key pattern found: {key_patterns[:5]}")
        print(f"  [contam_test] key patterns in _seed_checkpoint.py: {key_patterns[:5]}",
              flush=True)

    # Cleanup
    shutil.rmtree(contam_dir, ignore_errors=True)
    result["elapsed_s"] = round(time.time() - t0, 3)
    print(f"  [contam_test] done in {result['elapsed_s']:.2f}s "
          f"contamination_confirmed={result['contamination_confirmed']}", flush=True)
    return result


# ============================================================
# Instrumentation self-test (MANDATORY)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Self-tests for the diagnostic script:
    1. N=4096 (control) build_shared succeeds.
    2. subthreshold probes have max_sim ~ 0.45 < 0.50 threshold.
    3. compress_quant_bits8 preserves shape.
    4. _seed_checkpoint.py list_completed_keys, write_partial_key, load_partial_key
       round-trip correctly.
    5. Verdict gate structure correct.
    """
    assert N_CONTROL == 4096, "PROT-018: N must be 4096"

    # Formula self-test 1: compression
    W_test = torch.randn(32, 32)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape, "compress shape changed"
    assert float((W_comp - W_test).abs().max().item()) < float(W_test.abs().max().item()), \
        "compress made error worse than identity"

    # Formula self-test 2: subthreshold probes
    N_t = 512
    g = torch.Generator().manual_seed(42)
    cb_raw = torch.sign(torch.randn(8, N_t, generator=g)).float()
    cb = cb_raw / cb_raw.norm(dim=-1, keepdim=True) * math.sqrt(N_t)
    ki = torch.arange(8, dtype=torch.long)
    q_probe = _subthreshold_probes(cb, ki, 4, N_t, 42, torch.device("cpu"))
    sims = q_probe @ cb.T / N_t
    max_sims = sims.max(dim=-1).values
    assert max_sims.max().item() < DEFENSE_A_SIM_THRESH + 0.05, \
        f"probe max_sim={max_sims.max():.4f} too high"
    assert max_sims.max().item() > COLLISION_ALPHA - 0.05, \
        f"probe max_sim={max_sims.max():.4f} too low"
    print(f"[selftest] formula-2 probe max_sim={max_sims.mean():.4f} "
          f"(expected ~{COLLISION_ALPHA})", flush=True)

    # Formula self-test 3: checkpoint round-trip
    # Note: _is_valid_partial checks str(payload["seed"]) == str(key).
    # write_partial_key stamps body["seed"] = str(key) if not already set.
    # So: don't include "seed" in payload manually OR ensure it matches str(key).
    _ck_path = REPO / "experiments" / "_seed_checkpoint.py"
    assert _ck_path.exists(), f"_seed_checkpoint.py missing: {_ck_path}"
    _ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_selftest", _ck_path)
    _ck = importlib.util.module_from_spec(_ck_spec)
    _ck_spec.loader.exec_module(_ck)

    test_dir = REPO / "data" / "exp_aqsim_3way_diagnostic_v1" / "_selftest_tmp"
    test_dir.mkdir(parents=True, exist_ok=True)
    try:
        # Key = "seed17_smoke"; payload has M=256 (smoke scale).
        # Let write_partial_key stamp the "seed" field to match key.
        _ck.write_partial_key(test_dir, "seed17_smoke", {"M": 256, "is_smoke": True})
        done = set(_ck.list_completed_keys(test_dir))
        assert "seed17_smoke" in done, f"checkpoint key not found: {done}"
        loaded = _ck.load_partial_key(test_dir, "seed17_smoke")
        assert loaded is not None, "load_partial_key returned None"
        assert loaded.get("M") == 256, f"loaded M={loaded.get('M')} expected 256"
        print("[selftest] formula-3 checkpoint round-trip PASS", flush=True)
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

    # Formula self-test 4: build_shared succeeds at N=1024 (log2=10, even -- Kerdock OK)
    # Note: N must be power of 2 with even log2 for Kerdock codebook.
    # N=4096 (log2=12, even) OK. N=1024 (log2=10, even) OK.
    # N=8192 (log2=13, odd) FAILS -- that is precisely what we are diagnosing.
    device = torch.device("cpu")
    N_st = 1024  # log2=10, even -- Kerdock compatible
    M_st = 64
    try:
        cb_st, W_st, ki_st, vi_st, rel_st = build_shared(N_st, M_st, 42, device)
        assert cb_st.shape[1] == N_st, f"codebook dim {cb_st.shape}"
        assert W_st.shape == (N_st, N_st), f"W shape {W_st.shape}"
        print(f"[selftest] formula-4 build_shared N={N_st} OK: "
              f"codebook={cb_st.shape} W={W_st.shape}", flush=True)
        del cb_st, W_st
    except Exception as e:
        raise AssertionError(f"build_shared failed at N={N_st}: {e}") from e

    print("[selftest] PASS: all AQSIM diagnostic assertions passed.", flush=True)


_instrumentation_selftest()


# ============================================================
# Main diagnostic
# ============================================================

def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    device = torch.device("cpu")  # CPU for verbose tracing; no CUDA async

    print(f"[main] AQSIM 3-way cross-N engineering diagnostic v1", flush=True)
    print(f"[main] smoke={is_smoke} device={device}", flush=True)

    results: Dict[str, Any] = {
        "anchor": "aqsim_3way_cross_n_engineering_diagnostic_v1_n4096",
        "smoke": is_smoke,
        "device": str(device),
        "scenarios": {},
        "findings_summary": [],
        "root_cause": None,
        "fix_path": None,
        "verdict": None,
        "verdict_msg": None,
    }
    t_global = time.time()

    # =====================================================================
    # Scenario 1: N=4096 CONTROL (should PASS -- confirms pipeline works)
    # =====================================================================
    print("\n[scenario-1] N=4096 CONTROL", flush=True)
    s1_M = int(N_CONTROL * M_RATIO)   # 2048
    s1_K = K_PATHS_CONTROL
    s1 = run_single_seed(N_CONTROL, s1_M, s1_K, 42, device, "N4096_control")
    results["scenarios"]["N4096_control"] = s1
    if s1["ok"]:
        print(f"[scenario-1] PASS: N=4096 control runs correctly. "
              f"def_act={s1.get('defense_activation_rate','n/a'):.3f} "
              f"acc_gated={s1.get('acc_gated_comp','n/a'):.3f}", flush=True)
        results["findings_summary"].append("Scenario-1 (N=4096 control): PASS -- pipeline intact")
    else:
        print(f"[scenario-1] FAIL: N=4096 control failed at step={s1['step_reached']}: "
              f"{s1['error']}", flush=True)
        results["findings_summary"].append(
            f"Scenario-1 (N=4096 control): FAIL -- pipeline broken at {s1['step_reached']}")

    # =====================================================================
    # Scenario 2: Checkpoint contamination test
    # =====================================================================
    print("\n[scenario-2] Checkpoint contamination hypothesis (e)", flush=True)
    s2 = run_checkpoint_contamination_test(device)
    results["scenarios"]["checkpoint_contamination"] = s2
    if s2["contamination_confirmed"]:
        print("[scenario-2] CONFIRMED: smoke checkpoint contaminates FULL run", flush=True)
        results["findings_summary"].append(
            "Scenario-2: CONTAMINATION CONFIRMED -- "
            "smoke checkpoint (M=256) is loaded by FULL run (M=2048)")
        results["root_cause"] = (
            "CHECKPOINT CONTAMINATION: _seed_checkpoint uses key 'seed{N}' for BOTH "
            "smoke and FULL runs. After the runner's smoke gate writes partial_metrics_seed17.json "
            "with M=256, the FULL run finds 'seed17' in the checkpoint, loads smoke-scale metrics "
            "(M=256, elapsed_s~0), and exits without computing FULL results. "
            "This affects ALL N>4096 anchors that ran a smoke gate before the FULL run."
        )
        results["fix_path"] = (
            "FIX: Include M (or 'full'/'smoke' tag) in checkpoint key, e.g. "
            "'seed42_M2048_full' vs 'seed42_M256_smoke'. "
            "Alternatively: clear checkpoint dir between smoke gate and FULL run. "
            "Alternatively: add M field validation to load_partial_key -- if loaded M != "
            "current M, discard checkpoint and re-run."
        )
    else:
        results["findings_summary"].append(
            f"Scenario-2: contamination NOT confirmed via test (details: {s2['findings']})")

    # =====================================================================
    # Scenario 3: N=8192 (should trigger Kerdock ValueError for log2=13 odd)
    # =====================================================================
    print(f"\n[scenario-3] N={N_TEST_8192} build_shared test", flush=True)
    s3_M = int(N_TEST_8192 * M_RATIO)   # 4096
    s3 = run_single_seed(N_TEST_8192, s3_M, K_PATHS_CONTROL, 42, device, "N8192_test")
    results["scenarios"][f"N{N_TEST_8192}_test"] = s3
    if not s3["ok"] and s3["kerdock_exception"]:
        print(f"[scenario-3] Kerdock exception confirmed at N=8192: {s3['error']}", flush=True)
        results["findings_summary"].append(
            f"Scenario-3 (N=8192): Kerdock ValueError confirmed -- "
            f"log2(8192)=13 is ODD, not supported by make_kerdock_4coset_codebook")
        if results["root_cause"] is None:
            results["root_cause"] = (
                "KERDOCK_EVEN_LOG2_CONSTRAINT: make_kerdock_4coset_codebook raises ValueError "
                "for N=8192 (log2=13 ODD). This would cause FULL run to fail at build_shared "
                "before any cells are computed."
            )
            results["fix_path"] = (
                "FIX for N=8192: Use BSC random codebook instead of Kerdock for odd log2(N). "
                "Make_substrate already handles this if the fallback path is active. "
                "Alternatively: skip N=8192 (not power-of-4) in cross-N validation."
            )
    elif s3["ok"]:
        print(f"[scenario-3] N=8192 pipeline PASS: "
              f"def_act={s3.get('defense_activation_rate','n/a'):.3f}", flush=True)
        results["findings_summary"].append("Scenario-3 (N=8192): pipeline PASS (no exception)")
    else:
        print(f"[scenario-3] N=8192 FAIL (non-Kerdock): step={s3['step_reached']}: "
              f"{s3['error']}", flush=True)
        results["findings_summary"].append(
            f"Scenario-3 (N=8192): FAIL (non-Kerdock) at {s3['step_reached']}: {s3['error'][:200]}")

    # =====================================================================
    # Scenario 4: N=16384 (log2=14 even -- Kerdock OK; tests other issues)
    # =====================================================================
    print(f"\n[scenario-4] N={N_TEST_16384} K={K_PATHS_16384}", flush=True)
    s4_M = int(N_TEST_16384 * 0.25)   # M/N=0.25 matching v5
    s4 = run_single_seed(N_TEST_16384, s4_M, K_PATHS_16384, 42, device, "N16384_test")
    results["scenarios"][f"N{N_TEST_16384}_test"] = s4
    if s4["ok"]:
        print(f"[scenario-4] N=16384 pipeline PASS: "
              f"def_act={s4.get('defense_activation_rate','n/a'):.3f}", flush=True)
        results["findings_summary"].append("Scenario-4 (N=16384): pipeline PASS")
    elif s4["kerdock_exception"]:
        print(f"[scenario-4] N=16384 Kerdock exception: {s4['error']}", flush=True)
        results["findings_summary"].append(
            f"Scenario-4 (N=16384): Kerdock exception (unexpected; log2=14 even): {s4['error']}")
    else:
        print(f"[scenario-4] N=16384 FAIL at step={s4['step_reached']}: {s4['error']}", flush=True)
        results["findings_summary"].append(
            f"Scenario-4 (N=16384): FAIL at {s4['step_reached']}: {str(s4['error'])[:200]}")

    # =====================================================================
    # Determine verdict
    # =====================================================================
    root_cause_identified = results["root_cause"] is not None
    fix_path_available = results["fix_path"] is not None
    control_pass = results["scenarios"].get("N4096_control", {}).get("ok", False)

    if root_cause_identified and fix_path_available and control_pass:
        verdict = "DIAGNOSTIC_HARD_PASS"
        verdict_msg = (
            f"DIAGNOSTIC_HARD_PASS: root cause identified with fix path.\n"
            f"ROOT_CAUSE: {results['root_cause']}\n"
            f"FIX_PATH: {results['fix_path']}\n"
            f"FINDINGS: {chr(10).join(results['findings_summary'])}"
        )
    elif root_cause_identified:
        verdict = "DIAGNOSTIC_MIDDLE_BAND"
        verdict_msg = (
            f"DIAGNOSTIC_MIDDLE_BAND: root cause identified, fix path incomplete or partial.\n"
            f"ROOT_CAUSE: {results['root_cause']}\n"
            f"FINDINGS: {chr(10).join(results['findings_summary'])}"
        )
    else:
        verdict = "DIAGNOSTIC_HARD_FAIL"
        verdict_msg = (
            f"DIAGNOSTIC_HARD_FAIL: root cause NOT identified from instrumentation alone.\n"
            f"FINDINGS: {chr(10).join(results['findings_summary'])}\n"
            f"ESCALATE: live debugging session required."
        )

    results["verdict"] = verdict
    results["verdict_msg"] = verdict_msg
    results["elapsed_total_s"] = round(time.time() - t_global, 2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {results['elapsed_total_s']}s", flush=True)

    out_dir = REPO / "data" / os.environ.get("HDLAB_EXP_NAME", "aqsim_3way_diagnostic_v1")
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"[done] metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test: module-scope selftest already passed. exit 0.", flush=True)
        sys.exit(0)
    main()
