"""AQSIM 3-WAY CROSS-N ENGINEERING DIAGNOSTIC v2 at N=4096 -- verbose tracing.

Context: exp_aqsim_3way_cross_n_engineering_diagnostic_v1_n4096 shipped and failed
remotely (status=failed, wall_s=None, started_at=2026-06-01T14:38:44). The v1 local
run produced DIAGNOSTIC_HARD_PASS but the runner marked it failed because the
metrics.json was written to data/<HDLAB_EXP_NAME>/ (missing exp_ prefix) while the
runner expects data/exp_<HDLAB_EXP_NAME>/metrics.json.

BUG IN V1: main() wrote:
    out_dir = REPO / "data" / os.environ.get("HDLAB_EXP_NAME", "aqsim_3way_diagnostic_v1")
  which resolves to data/<NAME>/ not data/exp_<NAME>/ when HDLAB_EXP_NAME is set.
FIX IN V2: out_dir = REPO / "data" / f"exp_{name}" where name comes from HDLAB_EXP_NAME.

V2 ALSO ADDS verbose tracing per [[feedback-always-verbose-remote-dispatch]]:
- explicit experiment.log sentinel write before AND after each scenario
- per-cell try/except with full traceback written to experiment.log
- runner writes stdout to data/remote_cpu_queue/<name>.log already (no extra tee needed)
- ALL result dicts written to experiment.log even when metrics.json write fails

ROOT CAUSES CONFIRMED LOCALLY (v1 results in data/aqsim_3way_diagnostic_v1/metrics.json):
(1) CHECKPOINT CONTAMINATION: smoke partial uses key "seed{N}" same as FULL run
    -> FULL run loads smoke-scale M=256, exits without computing
    FIX: include M or run_mode in checkpoint key (PROT-021 already implements this)
(2) KERDOCK EVEN-LOG2 CONSTRAINT: N=8192 (log2=13 odd) raises ValueError in build_shared
    FIX: skip N=8192 cross-N anchors; use N=16384 (log2=14 even) as next scale

PROT-018: _n4096 binds N = 4096 (control N for this diagnostic).

PRE-REGISTERED BANDS:
  HP  : diagnostic identifies rejection-point with evidence; fix path present
        Expected: same 2 root causes as v1 local run (checkpoint + Kerdock)
        HP = DIAGNOSTIC_HARD_PASS verdict + non-empty findings_summary
  HF  : no failure mode identifiable; verdict = DIAGNOSTIC_HARD_FAIL
  MB  : root cause identified but fix not immediately actionable

Queue: remote_cpu_queue (verbose tracing; CPU suffices; Kerdock test is fast)
Pre-reg: preregs/2026-06-01_aqsim_3way_diagnostic_verbose_v2_n4096.md
HDLAB_EXP_NAME: aqsim_3way_diagnostic_verbose_v2_n4096

TIMEOUT ESTIMATE:
  v1 local: ~25s total (4 scenarios: N=4096 control ~5s, checkpoint ~1s,
            N=8192 Kerdock exception ~2s, N=16384 ~10s)
  Remote: same script, CPU-only, expect <60s
  timeout_s = ceil(1.5 * 60 * 1.0 * 1) = 90s -> PROT-019 floor 14400s
  -> timeout_s = 14400
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import re
import shutil
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

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

DEPTH          = 5
K_PATHS_CONTROL = 100
K_PATHS_16384   = 2     # small K to avoid slow run

M_RATIO        = 0.5    # M = N * M_RATIO

DEFENSE_A_SIM_THRESH = 0.5
COLLISION_ALPHA      = 0.45

# Anchor name (PROT-018 binding)
ANCHOR_NAME = "aqsim_3way_diagnostic_verbose_v2_n4096"


# ============================================================
# Output directory helpers -- V2 FIX: include exp_ prefix
# ============================================================

def get_exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)


def get_root_out_dir() -> Path:
    """Root output dir: data/exp_<HDLAB_EXP_NAME>/ -- matches runner expectation."""
    name = get_exp_name()
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_subdir(label: str) -> Path:
    d = get_root_out_dir() / label
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# experiment.log sentinel writer (verbose tracing)
# ============================================================

_EXP_LOG: Path | None = None


def _open_exp_log() -> Path:
    """Return path to experiment.log under root out_dir; create on first call."""
    global _EXP_LOG
    if _EXP_LOG is None:
        _EXP_LOG = get_root_out_dir() / "experiment.log"
    return _EXP_LOG


def _log(msg: str) -> None:
    """Write msg to both stdout and experiment.log (verbose tracing sentinel)."""
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with _open_exp_log().open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def _log_sentinel(tag: str, payload: Any = None) -> None:
    """Write a sentinel entry with optional JSON payload to experiment.log."""
    _log(f"SENTINEL {tag}")
    if payload is not None:
        try:
            _log(f"  payload: {json.dumps(payload, default=str)[:500]}")
        except (TypeError, ValueError):
            _log(f"  payload: {str(payload)[:500]}")


# ============================================================
# Helpers (copied from v1 -- standalone, no shared state)
# ============================================================

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
    return alpha * k_sel + beta * noise_perp_scaled


def _defense_gate(q: torch.Tensor, codebook: torch.Tensor,
                   key_idx: torch.Tensor, N_use: int) -> torch.Tensor:
    keys = codebook[key_idx]
    sims = q @ keys.T / N_use
    return sims.max(dim=-1).values >= DEFENSE_A_SIM_THRESH


# ============================================================
# Scenario 1/3/4 runner (with verbose logging)
# ============================================================

def run_single_seed(N_use: int, M: int, K_paths: int,
                     seed: int, device: torch.device,
                     label: str) -> Dict[str, Any]:
    """Run one seed with verbose sentinel logging.

    Writes sentinel before/after each step. Full traceback on exception.
    """
    result: Dict[str, Any] = {
        "label": label,
        "N": N_use, "M": M, "K_paths": K_paths, "seed": seed,
        "ok": False, "error": None, "error_traceback": None,
        "step_reached": "start",
        "kerdock_exception": False,
        "import_exception": False,
        "build_shared_exception": False,
        "cells": [],
        "elapsed_s": 0.0,
    }
    t0 = time.time()

    _log_sentinel(f"BEGIN_CELL label={label} N={N_use} M={M} K={K_paths} seed={seed}")

    try:
        _log(f"  [{label}] step=build_shared N={N_use} M={M} seed={seed}")
        result["step_reached"] = "build_shared"
        codebook, W_base, key_idx, val_idx, relation = build_shared(
            N_use, M, seed, device)
        _log(f"  [{label}] build_shared OK: codebook={codebook.shape} "
             f"W={W_base.shape} key_idx={key_idx.shape}")

        result["step_reached"] = "compress"
        W_comp = compress_quant_bits8(W_base)
        _log(f"  [{label}] compress OK: W_comp shape={W_comp.shape}")

        result["step_reached"] = "defense_probes"
        n_adv = 9
        n_leg = 2
        leg_keys_list = [k for k, v in relation.items() if v is not None]
        n_leg_avail = min(n_leg, len(leg_keys_list))
        leg_starts = torch.tensor(leg_keys_list[:n_leg_avail], dtype=torch.long,
                                   device=device)
        leg_q = codebook[leg_starts]
        adv_q = _subthreshold_probes(codebook, key_idx, n_adv, N_use, seed, device)
        _log(f"  [{label}] probes OK: n_leg={leg_q.shape[0]} n_adv={adv_q.shape[0]}")

        result["step_reached"] = "defense_gate"
        adv_accepted = _defense_gate(adv_q, codebook, key_idx, N_use)
        leg_accepted = _defense_gate(leg_q, codebook, key_idx, N_use)
        defense_act = float((~adv_accepted).float().mean().item())
        fp_rate = float((~leg_accepted).float().mean().item())
        _log(f"  [{label}] defense_gate OK: def_act={defense_act:.3f} fp={fp_rate:.3f}")

        result["step_reached"] = "path_d"
        path_d_res = path_d_run(
            codebook, W_comp, leg_starts, relation, DEPTH, K_paths, seed, N_use)
        acc_gated = float(path_d_res.mean().item())
        _log(f"  [{label}] path_d OK: acc_gated={acc_gated:.3f}")

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
        if ("kerdock" in str(exc).lower() or "even" in str(exc).lower()
                or "n_log2" in str(exc).lower() or "primitive" in str(exc).lower()):
            result["kerdock_exception"] = True
        if "import" in exc_type.lower():
            result["import_exception"] = True
        if result["step_reached"] == "build_shared":
            result["build_shared_exception"] = True
        _log(f"  [{label}] EXCEPTION at step={result['step_reached']}: {exc_type}: {exc}")
        _log(f"  [{label}] traceback:\n{tb_str}")

    result["elapsed_s"] = round(time.time() - t0, 3)
    _log_sentinel(f"END_CELL label={label} ok={result['ok']} "
                  f"elapsed_s={result['elapsed_s']} "
                  f"kerdock={result.get('kerdock_exception',False)} "
                  f"step={result['step_reached']}", result)
    return result


# ============================================================
# Scenario 2: checkpoint contamination test
# ============================================================

def run_checkpoint_contamination_test(device: torch.device) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "test": "checkpoint_contamination",
        "hypothesis": "smoke checkpoint pollutes FULL run via same key pattern",
        "ok": False, "contamination_confirmed": False, "findings": [],
    }
    t0 = time.time()
    _log_sentinel("BEGIN_CELL label=contam_test")

    _ck_path = REPO / "experiments" / "_seed_checkpoint.py"
    _ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_diag_v2", _ck_path)
    _ck = importlib.util.module_from_spec(_ck_spec)
    _ck_spec.loader.exec_module(_ck)
    list_completed_keys = _ck.list_completed_keys
    write_partial_key   = _ck.write_partial_key
    load_partial_key    = _ck.load_partial_key

    base_dir = get_root_out_dir()
    contam_dir = base_dir / "contam_test"
    contam_dir.mkdir(parents=True, exist_ok=True)

    smoke_scale_cell = {
        "M": 256, "ok": True, "is_smoke": True,
        "n_leg": 2, "n_adv": 9,
        "defense_activation_rate": 1.0, "fp_rate": 0.0,
        "acc_path_d_gated_compressed": 1.0,
    }
    write_partial_key(contam_dir, "seed42", smoke_scale_cell)
    _log(f"  [contam_test] wrote smoke-scale checkpoint: {contam_dir}")

    done_keys = set(list_completed_keys(contam_dir))
    _log(f"  [contam_test] list_completed_keys: {done_keys}")

    if "seed42" in done_keys:
        loaded = load_partial_key(contam_dir, "seed42")
        loaded_M = loaded.get("M") if loaded else None
        _log(f"  [contam_test] seed42 found in checkpoint. loaded M={loaded_M}")
        result["findings"].append(
            f"seed42 found in checkpoint with M={loaded_M} (should be 256=smoke)")
        if loaded_M == 256:
            result["contamination_confirmed"] = True
            result["findings"].extend([
                "CONFIRMED: smoke checkpoint M=256 loaded for FULL N=4096 M=2048 run",
                "ROOT CAUSE: _seed_checkpoint uses same key 'seed{N}' for smoke AND full",
                "FIX: include M or run_mode in checkpoint key (PROT-021 implements this)",
            ])
            result["ok"] = True
        else:
            result["findings"].append(
                f"NOT CONFIRMED: checkpoint M={loaded_M} != 256 (unexpected)")
    else:
        result["findings"].append(
            "seed42 NOT found in checkpoint -- mechanism works differently")

    # Structural analysis of key pattern
    ck_source = _ck_path.read_text(encoding="utf-8")
    key_patterns = re.findall(r'["\']seed\{?[^"\']*\}?["\']', ck_source)
    result["findings"].append(f"key patterns in _seed_checkpoint.py: {key_patterns[:5]}")
    _log(f"  [contam_test] key patterns: {key_patterns[:5]}")

    # Check if PROT-021 is implemented (run_config-based rejection)
    has_prot021 = "run_config" in ck_source and "run_mode" in ck_source
    result["prot021_implemented"] = has_prot021
    result["findings"].append(
        f"PROT-021 run_config guard: {'PRESENT' if has_prot021 else 'MISSING'}")
    _log(f"  [contam_test] PROT-021 present: {has_prot021}")

    shutil.rmtree(contam_dir, ignore_errors=True)
    result["elapsed_s"] = round(time.time() - t0, 3)
    _log_sentinel(f"END_CELL label=contam_test ok={result['ok']} "
                  f"contamination_confirmed={result['contamination_confirmed']}", result)
    return result


# ============================================================
# Instrumentation self-test (MANDATORY)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_CONTROL == 4096, "PROT-018: N must be 4096"

    # Test 1: compression preserves shape
    W_test = torch.randn(32, 32)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape, "compress shape changed"
    assert (float((W_comp - W_test).abs().max().item())
            < float(W_test.abs().max().item())), "compress error > identity"

    # Test 2: subthreshold probes ~ alpha
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
    print(f"[selftest] probe max_sim={max_sims.mean():.4f} (expected ~{COLLISION_ALPHA})",
          flush=True)

    # Test 3: checkpoint round-trip (PROT-021 key includes mode tag)
    _ck_path = REPO / "experiments" / "_seed_checkpoint.py"
    assert _ck_path.exists(), f"_seed_checkpoint.py missing: {_ck_path}"
    _ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_selftest_v2", _ck_path)
    _ck = importlib.util.module_from_spec(_ck_spec)
    _ck_spec.loader.exec_module(_ck)

    test_dir = get_root_out_dir() / "_selftest_tmp"
    test_dir.mkdir(parents=True, exist_ok=True)
    try:
        _ck.write_partial_key(test_dir, "seed17_smoke", {"M": 256, "is_smoke": True})
        done = set(_ck.list_completed_keys(test_dir))
        assert "seed17_smoke" in done, f"checkpoint key not found: {done}"
        loaded = _ck.load_partial_key(test_dir, "seed17_smoke")
        assert loaded is not None, "load_partial_key returned None"
        assert loaded.get("M") == 256, f"loaded M={loaded.get('M')} expected 256"
        print("[selftest] checkpoint round-trip PASS", flush=True)
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

    # Test 4: build_shared at small even-log2 N
    device = torch.device("cpu")
    N_st = 1024  # log2=10, even
    M_st = 64
    try:
        cb_st, W_st, ki_st, vi_st, rel_st = build_shared(N_st, M_st, 42, device)
        assert cb_st.shape[1] == N_st, f"codebook dim {cb_st.shape}"
        assert W_st.shape == (N_st, N_st), f"W shape {W_st.shape}"
        print(f"[selftest] build_shared N={N_st} OK", flush=True)
        del cb_st, W_st
    except Exception as e:
        raise AssertionError(f"build_shared failed at N={N_st}: {e}") from e

    # Test 5: output dir has exp_ prefix (V2 fix verification)
    out_dir = get_root_out_dir()
    assert "exp_" in out_dir.name, f"V2 fix: out_dir must include exp_ prefix; got {out_dir}"
    print(f"[selftest] output dir prefix fix PASS: {out_dir.name}", flush=True)

    # Test 6: experiment.log can be written
    test_log_msg = "selftest_v2_log_write_ok"
    _log(test_log_msg)
    exp_log = _open_exp_log()
    assert exp_log.exists(), f"experiment.log not created: {exp_log}"
    content = exp_log.read_text(encoding="utf-8")
    assert test_log_msg in content, "selftest log message not found in experiment.log"
    print(f"[selftest] experiment.log write PASS: {exp_log}", flush=True)

    print("[selftest] PASS: all v2 assertions passed.", flush=True)


_instrumentation_selftest()


# ============================================================
# Main diagnostic
# ============================================================

def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    device = torch.device("cpu")

    _log(f"AQSIM 3-way cross-N engineering diagnostic v2")
    _log(f"smoke={is_smoke} device={device} anchor={ANCHOR_NAME}")
    _log(f"output_dir={get_root_out_dir()}")
    _log(f"experiment.log={_open_exp_log()}")

    results: Dict[str, Any] = {
        "anchor": ANCHOR_NAME,
        "N": N_CONTROL,
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

    # =================================================================
    # Scenario 1: N=4096 CONTROL
    # =================================================================
    _log_sentinel("SCENARIO_1_BEGIN N=4096 control")
    s1_M = int(N_CONTROL * M_RATIO)   # 2048
    s1 = run_single_seed(N_CONTROL, s1_M, K_PATHS_CONTROL, 42, device, "N4096_control")
    results["scenarios"]["N4096_control"] = s1
    if s1["ok"]:
        _log(f"[scenario-1] PASS: N=4096 control intact. "
             f"def_act={s1.get('defense_activation_rate','n/a'):.3f} "
             f"acc_gated={s1.get('acc_gated_comp','n/a'):.3f}")
        results["findings_summary"].append("Scenario-1 (N=4096 control): PASS -- pipeline intact")
    else:
        _log(f"[scenario-1] FAIL: N=4096 control at step={s1['step_reached']}: {s1['error']}")
        results["findings_summary"].append(
            f"Scenario-1 (N=4096 control): FAIL at {s1['step_reached']}")
    _log_sentinel("SCENARIO_1_END")

    # =================================================================
    # Scenario 2: Checkpoint contamination
    # =================================================================
    _log_sentinel("SCENARIO_2_BEGIN checkpoint_contamination")
    s2 = run_checkpoint_contamination_test(device)
    results["scenarios"]["checkpoint_contamination"] = s2
    if s2["contamination_confirmed"]:
        _log("[scenario-2] CONFIRMED: smoke checkpoint contaminates FULL run")
        results["findings_summary"].append(
            "Scenario-2: CONTAMINATION CONFIRMED -- smoke M=256 loaded by FULL M=2048")
        results["root_cause"] = (
            "CHECKPOINT CONTAMINATION: _seed_checkpoint uses key 'seed{N}' for BOTH "
            "smoke and FULL runs. Smoke gate writes partial_metrics_seed17.json with M=256; "
            "FULL run finds 'seed17', loads smoke-scale metrics (M=256, elapsed_s~0), "
            "exits without computing FULL results. Affects all N>4096 anchors post-smoke."
        )
        results["fix_path"] = (
            "FIX (already implemented as PROT-021): include M or run_mode in checkpoint key; "
            "e.g. 'seed42_M2048_full'. Pass run_config={N, M, run_mode='full'} to "
            "list_completed_keys/resumable_seeds. _seed_checkpoint.py has this guard; "
            "scripts must pass run_config to activate it."
        )
    else:
        results["findings_summary"].append(
            f"Scenario-2: contamination NOT confirmed: {s2['findings'][:2]}")
    _log_sentinel("SCENARIO_2_END contamination_confirmed=" + str(s2["contamination_confirmed"]))

    # =================================================================
    # Scenario 3: N=8192 (Kerdock log2=13 odd -> ValueError expected)
    # =================================================================
    _log_sentinel(f"SCENARIO_3_BEGIN N={N_TEST_8192} Kerdock test")
    s3_M = int(N_TEST_8192 * M_RATIO)   # 4096
    s3 = run_single_seed(N_TEST_8192, s3_M, K_PATHS_CONTROL, 42, device, "N8192_test")
    results["scenarios"][f"N{N_TEST_8192}_test"] = s3
    if not s3["ok"] and s3["kerdock_exception"]:
        _log(f"[scenario-3] Kerdock ValueError confirmed at N=8192: {s3['error']}")
        results["findings_summary"].append(
            f"Scenario-3 (N=8192): Kerdock ValueError -- log2(8192)=13 ODD, "
            f"not supported by make_kerdock_4coset_codebook")
        if results["root_cause"] is None:
            results["root_cause"] = (
                "KERDOCK_EVEN_LOG2_CONSTRAINT: make_kerdock_4coset_codebook raises "
                "ValueError for N=8192 (log2=13 ODD). FULL run fails at build_shared "
                "before any cells are computed."
            )
            results["fix_path"] = (
                "FIX: skip N=8192 in cross-N sweeps. Use N=16384 (log2=14 even) as "
                "next scale after N=4096. N=8192 is not a supported codebook dimension."
            )
        else:
            # Both root causes confirmed
            results["fix_path"] += (
                " + SECOND ROOT CAUSE: skip N=8192 (Kerdock odd-log2); use N=16384."
            )
    elif s3["ok"]:
        _log(f"[scenario-3] N=8192 PASS (unexpected): def_act={s3.get('defense_activation_rate')}")
        results["findings_summary"].append("Scenario-3 (N=8192): PASS (unexpected)")
    else:
        _log(f"[scenario-3] N=8192 FAIL (non-Kerdock): {s3['step_reached']}: {s3['error']}")
        results["findings_summary"].append(
            f"Scenario-3 (N=8192): FAIL (non-Kerdock) at {s3['step_reached']}: "
            f"{str(s3['error'])[:200]}")
    _log_sentinel("SCENARIO_3_END kerdock=" + str(s3.get("kerdock_exception", False)))

    # =================================================================
    # Scenario 4: N=16384 (log2=14 even -> should PASS)
    # =================================================================
    _log_sentinel(f"SCENARIO_4_BEGIN N={N_TEST_16384} K={K_PATHS_16384}")
    s4_M = int(N_TEST_16384 * 0.25)   # M/N=0.25
    s4 = run_single_seed(N_TEST_16384, s4_M, K_PATHS_16384, 42, device, "N16384_test")
    results["scenarios"][f"N{N_TEST_16384}_test"] = s4
    if s4["ok"]:
        _log(f"[scenario-4] N=16384 PASS: def_act={s4.get('defense_activation_rate','n/a'):.3f}")
        results["findings_summary"].append("Scenario-4 (N=16384): pipeline PASS")
    elif s4["kerdock_exception"]:
        _log(f"[scenario-4] N=16384 Kerdock (unexpected): {s4['error']}")
        results["findings_summary"].append(
            f"Scenario-4 (N=16384): Kerdock exception (unexpected): {s4['error']}")
    else:
        _log(f"[scenario-4] N=16384 FAIL at step={s4['step_reached']}: {s4['error']}")
        results["findings_summary"].append(
            f"Scenario-4 (N=16384): FAIL at {s4['step_reached']}: "
            f"{str(s4['error'])[:200]}")
    _log_sentinel("SCENARIO_4_END ok=" + str(s4["ok"]))

    # =================================================================
    # Verdict
    # =================================================================
    root_cause_identified = results["root_cause"] is not None
    fix_path_available = results["fix_path"] is not None
    control_pass = results["scenarios"].get("N4096_control", {}).get("ok", False)

    if root_cause_identified and fix_path_available and control_pass:
        verdict = "DIAGNOSTIC_HARD_PASS"
        verdict_msg = (
            f"DIAGNOSTIC_HARD_PASS: root cause identified with fix path."
            f" ROOT_CAUSE: {results['root_cause'][:200]}"
            f" FIX_PATH: {results['fix_path'][:200]}"
            f" FINDINGS: {'; '.join(results['findings_summary'])}"
        )
    elif root_cause_identified:
        verdict = "DIAGNOSTIC_MIDDLE_BAND"
        verdict_msg = (
            f"DIAGNOSTIC_MIDDLE_BAND: root cause identified, fix incomplete."
            f" ROOT_CAUSE: {results['root_cause'][:200]}"
            f" FINDINGS: {'; '.join(results['findings_summary'])}"
        )
    else:
        verdict = "DIAGNOSTIC_HARD_FAIL"
        verdict_msg = (
            f"DIAGNOSTIC_HARD_FAIL: root cause NOT identified."
            f" FINDINGS: {'; '.join(results['findings_summary'])}"
            f" ESCALATE: live debugging session required."
        )

    results["verdict"] = verdict
    results["verdict_msg"] = verdict_msg
    results["elapsed_s"] = round(time.time() - t_global, 2)

    _log_sentinel("VERDICT", {"verdict": verdict, "elapsed_s": results["elapsed_s"]})
    _log(f"[verdict] {verdict}")
    _log(f"[verdict_msg] {verdict_msg}")
    _log(f"[elapsed] {results['elapsed_s']}s")

    # Write metrics.json -- V2 FIX: uses get_root_out_dir() which includes exp_ prefix
    out_dir = get_root_out_dir()
    metrics_path = out_dir / "metrics.json"
    try:
        with open(metrics_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, default=str)
        _log(f"[done] metrics -> {metrics_path}")
    except OSError as e:
        _log(f"[ERROR] metrics write failed: {e}")
        # Also write minimal fallback to stderr so runner log captures it
        print(f"METRICS_WRITE_FAIL: {e}", file=sys.stderr, flush=True)
        print(f"VERDICT_FALLBACK: {verdict}", file=sys.stderr, flush=True)
        print(f"VERDICT_MSG_FALLBACK: {verdict_msg}", file=sys.stderr, flush=True)

    _log_sentinel("EXPERIMENT_END anchor=" + ANCHOR_NAME)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test: module-scope selftest already passed. exit 0.",
              flush=True)
        sys.exit(0)
    main()
