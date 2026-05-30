"""Bet-B K=1 ceiling stress test: single-W canonical overwrite protocol at N=8192.

CONTEXT:
  v272 Agent 4 forensic: Bet B substrate is Fusi-Drew-Abbott K=1 cascade synapse
  class. K=1 imposes a THEORETICAL ret_A ceiling of ~0.80 under overwrite stress.
  8x convergent confirmations across v265-v272 anchors.

  2026-05-30 verdict_handler batch (commit 919a901): three rescue architectures
  (bet_b_cl_wide_phaseA_v1, bet_b_cl_frozen_phaseA_v1, bet_b_cls_dual_w_smoke)
  ALL hit ret_A=1.000 exactly. Three independent perfect rescues at the same
  number is the warning sign -- label-vs-honest #140 ARCHITECTURE_CLASS_SWITCH_
  MASQUERADING flag.

HYPOTHESIS UNDER TEST:
  The rescue trio escapes K=1 by NOT exposing Phase A to genuine overwrite stress:
    wide Phase A:   trains Phase A at N=8192 (larger representation -- different class)
    frozen Phase A: W_A is frozen; Phase B/C/D train a SEPARATE W (not overwriting W_A)
    dual-W:         two separate weight matrices; Phase A memory isolated by design

  The STRESS TEST: single W matrix, no freezing, no width advantage.
  Phase B/C/D update the SAME W that stored Phase A. K=1 cascade theory predicts
  ret_A will decay toward 0.80 ceiling as B/C/D add load to shared W.

  HARD_PASS = ret_A < 0.80 in >= 4/5 seeds at Phase D CONFIRMS K=1 ceiling
  is respected -> rescue trio genuinely changes architecture class (interesting).
  HARD_FAIL = ret_A >= 0.95 in >= 4/5 seeds at Phase D CONTRADICTS K=1 framework
  -> framework recalc trigger (Agent 4 forensic wrong about K=1 class).

DESIGN:
  - Single W matrix (canonical K=1 setup)
  - No dual-W, no frozen phase, no wider Phase A
  - K=1 overwrite stress: Phases B/C/D consume shared W positions
  - 4-stage CL: Phase A (store) -> Phase B/C/D (overwrite with replay)
  - N=8192 (PROT-018 binding; _n8192 suffix)
  - 5 seeds for FULL run; smoke uses 1 seed at N=1024
  - Measure ret_A at Phase B, C, D endpoints (progression curve)
  - _seed_checkpoint wired (PROT-021 compliance)

PRE-REGISTERED BANDS (per task specification):
  HARD_PASS: ret_A_after_D < 0.80 in >= 4/5 seeds
    K=1 ceiling RESPECTED. Rescue trio escaped K=1 by changing architecture
    class. ret_A trajectory: ~0.80 or below under canonical overwrite stress.
  HARD_FAIL: ret_A_after_D >= 0.95 in >= 4/5 seeds
    K=1 ceiling VIOLATED. Agent 4's Fusi-Drew-Abbott K=1 framework is wrong;
    substrate is NOT K=1 limited. Framework recalculation trigger.
  MIDDLE_BAND: 0.80 <= ret_A_after_D < 0.95 in >= 3/5 seeds
    Partial ceiling -- substrate is K=1-like but stress not maximally imposed.
    Outcome plan: investigate replay fraction, batch schedule, and epoch count
    to determine if middle-band is genuine or stress-test artifact.

FORMULA SELF-TESTS (per feedback_strategy_spec_formula_selftests):
  1. retention = bpc_baseline / bpc_after_phase. For perfect retention: ratio = 1.0.
  2. retention = bpc_baseline / bpc_after capped at 1.0 (min(..., 1.0) guard).
  3. HARD_PASS fires when ret_A_after_D = [0.70, 0.72, 0.74, 0.68, 0.75] (all < 0.80).
     Count(< 0.80) = 5 >= 4 -> HARD_PASS.
  4. HARD_FAIL fires when ret_A_after_D = [0.96, 0.97, 0.95, 0.98, 0.96] (all >= 0.95).
     Count(>= 0.95) = 5 >= 4 -> HARD_FAIL.
  5. MIDDLE_BAND fires when ret_A_after_D = [0.82, 0.85, 0.81, 0.79, 0.90]:
     Count(>= 0.80 and < 0.95) = 4 (indices 0,1,2,4); Count(< 0.80) = 1 (index 3).
     -> middle-band condition: >= 3 in [0.80, 0.95) -> MIDDLE_BAND.
  6. N=8192 W matrix OOM: 8192^2 * 4 bytes = 268MB (single W). << 6GB. OK.

OOM PRE-CHECK:
  W at N=8192 float32: 8192^2 * 4 = 268MB (single W).
  Multiple W snapshots (W_A checkpoint, W_ABCD): 2 * 268MB = 536MB.
  Pool tensors: 1024 * 8192 * 4 = 32MB each; 4 pools = 128MB.
  Total peak: ~700MB. Well under 6GB. Ship allowed.

TIMEOUT ESTIMATE (PROT-019 floor for _n8192 = 21600s minimum):
  Reference: bet_b_n8192_4stage_v1 (N=8192, 5 seeds, similar protocol) ~ 1200s.
  K=1 stress test: same W size. No projection overhead. Slightly fewer epochs
  per phase (stress test is leaner -- no wide-phase overhead). Estimate similar.
  Formula: timeout = max(21600, ceil(1.5 * smoke_wall_s * (8192/1024)^1.5 * 5))
  Smoke timing TBD from actual run. Using reference: ceil(1.5 * 40 * 8^1.5 * 5)
  = ceil(1.5 * 40 * 22.6 * 5) = ceil(6792) = 6900s.
  PROT-019 floor for _n8192: 21600s. Use 21600s.
  Flag: 6h run, ties up GPU runner. Justified by disambiguation importance.

N-suffix: _n8192 (PROT-018 binding). Production N = 8192. Smoke N = 1024.
Queue: overnight_queue (GPU: torch+cuda, N=8192, 5 seeds, PROT-020 compliant)
Pre-reg: preregs/2026-05-30_bet_b_k1_ceiling_stress_n8192_v1.md
Parent: 919a901 verdict_handler batch (label-vs-honest #140 disambiguation)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# _seed_checkpoint: PROT-021 mandatory for long-timeout anchors
from _seed_checkpoint import (  # noqa: E402
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

# Load Kovacs base (train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors, etc.)
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("betb_k1_base", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Load 4-stage module for load_corpus_D and compute_verdict reference
_v4s_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v4s_spec = importlib.util.spec_from_file_location("betb_4stage_k1", _v4s_path)
v4s_mod = importlib.util.module_from_spec(_v4s_spec)
_v4s_spec.loader.exec_module(v4s_mod)

load_corpus_D = v4s_mod.load_corpus_D

# ===========================================================================
# PRODUCTION CONFIG -- PROT-018: N must match _n8192 suffix
# ===========================================================================
N_FULL = 8192        # PROT-018 binding: matches _n8192 anchor suffix
N_SMOKE = 1024

BATCH_SIZE_FULL  = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL      = 5
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS_FULL  = 8
PHASE_A_EPOCHS_SMOKE = 2
BYTES_FULL  = 200_000
BYTES_SMOKE = 20_000
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (PROT-018 / task spec)
# HARD_PASS: K=1 ceiling respected (ceiling is UPPER BOUND on ret_A)
HP_RET_A_CEILING = 0.80   # ret_A < this in >= 4/5 seeds -> HARD_PASS
HP_SEED_COUNT    = 4       # number of seeds required for HARD_PASS
# HARD_FAIL: K=1 ceiling violated (ret_A stays high under stress)
HF_RET_A_FLOOR   = 0.95   # ret_A >= this in >= 4/5 seeds -> HARD_FAIL
HF_SEED_COUNT    = 4
# MIDDLE_BAND: partial ceiling
MB_LOWER = 0.80
MB_UPPER = 0.95
MB_SEED_COUNT = 3


def get_output_dir(default_name: str = "bet_b_k1_ceiling_stress_n8192_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(per_seed_results: Dict) -> Tuple[str, str]:
    """Compute experiment verdict from per-seed ret_A_after_D values.

    Formula self-test:
      hp_vals = [0.70, 0.72, 0.74, 0.68, 0.75]: count(< 0.80) = 5 >= 4 -> HARD_PASS
      hf_vals = [0.96, 0.97, 0.95, 0.98, 0.96]: count(>= 0.95) = 5 >= 4 -> HARD_FAIL
      mb_vals = [0.82, 0.85, 0.81, 0.79, 0.90]: mb_count(in [0.80,0.95)) = 4 >= 3 -> MIDDLE_BAND
    """
    if not per_seed_results:
        return ("K1_STRESS_INCONCLUSIVE", "No per-seed results.")

    seed_vals = list(per_seed_results.values())
    ret_A_vals = [float(s["retention_A_after_D"]) for s in seed_vals]
    n_seeds = len(ret_A_vals)
    mean_ret_A = sum(ret_A_vals) / n_seeds

    # Progression curve averages
    mean_after_B = sum(float(s.get("retention_A_after_B", 0.0)) for s in seed_vals) / n_seeds
    mean_after_C = sum(float(s.get("retention_A_after_C", 0.0)) for s in seed_vals) / n_seeds

    count_below_hp = sum(1 for v in ret_A_vals if v < HP_RET_A_CEILING)
    count_above_hf = sum(1 for v in ret_A_vals if v >= HF_RET_A_FLOOR)
    count_middle   = sum(1 for v in ret_A_vals if MB_LOWER <= v < MB_UPPER)

    detail = (f"ret_A_after_D per seed: {[round(v, 3) for v in ret_A_vals]} "
              f"mean={mean_ret_A:.3f} "
              f"progression: after_B={mean_after_B:.3f} after_C={mean_after_C:.3f} after_D={mean_ret_A:.3f}")

    if count_above_hf >= HF_SEED_COUNT:
        return (
            "K1_STRESS_HARD_FAIL",
            f"K=1 ceiling VIOLATED: ret_A_after_D >= {HF_RET_A_FLOOR} in {count_above_hf}/{n_seeds} seeds. "
            f"Agent 4 K=1 framework wrong -- substrate is NOT K=1 limited. "
            f"Framework recalculation trigger. {detail}"
        )
    if count_below_hp >= HP_SEED_COUNT:
        return (
            "K1_STRESS_HARD_PASS",
            f"K=1 ceiling RESPECTED: ret_A_after_D < {HP_RET_A_CEILING} in {count_below_hp}/{n_seeds} seeds. "
            f"Rescue trio (wide/frozen/dual-W) genuinely changes architecture class. "
            f"{detail}"
        )
    if count_middle >= MB_SEED_COUNT:
        return (
            "K1_STRESS_MIDDLE_BAND",
            f"Partial K=1 ceiling: ret_A_after_D in [{MB_LOWER},{MB_UPPER}) for {count_middle}/{n_seeds} seeds. "
            f"Substrate is K=1-like but stress not maximally imposed. Investigate replay "
            f"fraction and epoch schedule. {detail}"
        )
    return (
        "K1_STRESS_INCONCLUSIVE",
        f"Mixed outcome: below_hp={count_below_hp}/{n_seeds} above_hf={count_above_hf}/{n_seeds} "
        f"middle={count_middle}/{n_seeds}. Does not fit any pre-registered band. {detail}"
    )


def _selftest_verdict() -> None:
    """Assert verdict logic matches formula self-tests."""
    def mk(vals_after_D, vals_after_B=None, vals_after_C=None):
        n = len(vals_after_D)
        if vals_after_B is None:
            vals_after_B = [0.9] * n
        if vals_after_C is None:
            vals_after_C = [0.85] * n
        seeds = [7, 17, 23, 31, 41][:n]
        return {
            str(s): {
                "retention_A_after_D": vD,
                "retention_A_after_B": vB,
                "retention_A_after_C": vC,
            }
            for s, vD, vB, vC in zip(seeds, vals_after_D, vals_after_B, vals_after_C)
        }

    # Self-test 1: HARD_PASS -- all below 0.80
    v1, _ = compute_verdict(mk([0.70, 0.72, 0.74, 0.68, 0.75]))
    assert v1 == "K1_STRESS_HARD_PASS", f"expected HARD_PASS got {v1}"

    # Self-test 2: HARD_FAIL -- all >= 0.95
    v2, _ = compute_verdict(mk([0.96, 0.97, 0.95, 0.98, 0.96]))
    assert v2 == "K1_STRESS_HARD_FAIL", f"expected HARD_FAIL got {v2}"

    # Self-test 3: MIDDLE_BAND -- [0.82, 0.85, 0.81, 0.79, 0.90]
    # count(< 0.80) = 1 (index 3: 0.79) -> not HARD_PASS (need 4)
    # count(>= 0.95) = 0 -> not HARD_FAIL
    # count(in [0.80, 0.95)) = 4 (indices 0,1,2,4) >= 3 -> MIDDLE_BAND
    v3, _ = compute_verdict(mk([0.82, 0.85, 0.81, 0.79, 0.90]))
    assert v3 == "K1_STRESS_MIDDLE_BAND", f"expected MIDDLE_BAND got {v3}"

    # Self-test 4: exactly 4/5 seeds below HP threshold -> HARD_PASS (count >= 4)
    v4, _ = compute_verdict(mk([0.75, 0.78, 0.73, 0.77, 0.82]))
    # count(< 0.80): 4 (indices 0,1,2,3) >= 4 -> HARD_PASS
    assert v4 == "K1_STRESS_HARD_PASS", f"expected HARD_PASS (4/5) got {v4}"

    # Self-test 5: OOM check
    oom_bytes = N_FULL * N_FULL * 4 * 2  # 2 W snapshots
    assert oom_bytes < 6e9, f"OOM pre-check: {oom_bytes:.2e} >= 6GB"

    # Self-test 6: empty dict -> INCONCLUSIVE
    v6, _ = compute_verdict({})
    assert v6 == "K1_STRESS_INCONCLUSIVE", f"expected INCONCLUSIVE got {v6}"

    print(f"[selftest] verdict_logic PASSED (6/6 cases). OOM check {oom_bytes:.2e} bytes.", flush=True)


def run_one_seed_k1_stress(seed: int, config: Dict,
                            device: torch.device) -> Dict:
    """Run canonical K=1 stress test for a single seed.

    Single W matrix, no dual-W, no frozen phase, no wider Phase A.
    Phases B/C/D overwrite the shared W that stores Phase A.
    Measure ret_A after each subsequent phase to track decay curve.
    """
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = config.get("mode") == "smoke"

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)

    # Load corpora
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)
    train_d, test_d = split(corpus_d)

    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx,  test_a_tgt  = base.bytes_to_idx_tensors(test_a,  device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx,  test_b_tgt  = base.bytes_to_idx_tensors(test_b,  device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx,  test_c_tgt  = base.bytes_to_idx_tensors(test_c,  device)
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(train_d, device)
    test_d_idx,  test_d_tgt  = base.bytes_to_idx_tensors(test_d,  device)

    # Single W matrix -- the canonical K=1 single-substrate setup
    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    # -----------------------------------------------------------------------
    # Phase A: store corpus A into W. No replay. Measure baseline.
    # -----------------------------------------------------------------------
    W, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0,
        byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt,
        None, None, 0,
        phase_a_epochs, batch_size, device)

    bpc_A_baseline = base.evaluate_bpc(
        W, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms,
        test_a_idx, test_a_tgt, batch_size, device)

    # -----------------------------------------------------------------------
    # Phase B: overwrite shared W with corpus B + A replay.
    # W is not reset -- this is the KEY overwrite stress.
    # -----------------------------------------------------------------------
    W, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u,
        n_epochs, batch_size, device)

    # Check ret_A after Phase B
    bpc_A_after_B = base.evaluate_bpc(
        W, pool_B_v, pool_B_l, pool_B_u,
        byte_atoms, pos_atoms,
        test_a_idx, test_a_tgt, batch_size, device)
    retention_A_after_B = min(bpc_A_baseline / max(bpc_A_after_B, 1e-6), 1.0)

    # -----------------------------------------------------------------------
    # Phase C: further overwrite shared W with corpus C + A+B replay.
    # -----------------------------------------------------------------------
    combined_AB_v = torch.cat([pool_A_v[:pool_A_u], pool_B_v[:pool_B_u]], dim=0)
    combined_AB_l = torch.cat([pool_A_l[:pool_A_u], pool_B_l[:pool_B_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]

    W, pool_C_v, pool_C_l, pool_C_u = base.train_w_with_replay(
        W, pool_B_v.clone(), pool_B_l.clone(), pool_B_u,
        byte_atoms, pos_atoms,
        train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u,
        n_epochs, batch_size, device)

    bpc_A_after_C = base.evaluate_bpc(
        W, pool_C_v, pool_C_l, pool_C_u,
        byte_atoms, pos_atoms,
        test_a_idx, test_a_tgt, batch_size, device)
    retention_A_after_C = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)

    # -----------------------------------------------------------------------
    # Phase D: maximum overwrite stress -- shared W with corpus D + A+B+C replay.
    # -----------------------------------------------------------------------
    combined_ABC_v = torch.cat([pool_A_v[:pool_A_u], pool_B_v[:pool_B_u],
                                 pool_C_v[:pool_C_u]], dim=0)
    combined_ABC_l = torch.cat([pool_A_l[:pool_A_u], pool_B_l[:pool_B_u],
                                 pool_C_l[:pool_C_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]

    W, pool_D_v, pool_D_l, pool_D_u = base.train_w_with_replay(
        W, pool_C_v.clone(), pool_C_l.clone(), pool_C_u,
        byte_atoms, pos_atoms,
        train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u,
        n_epochs, batch_size, device)

    bpc_A_after_D = base.evaluate_bpc(
        W, pool_D_v, pool_D_l, pool_D_u,
        byte_atoms, pos_atoms,
        test_a_idx, test_a_tgt, batch_size, device)
    retention_A_after_D = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)

    # Also measure B, C retention at final phase D
    bpc_B_baseline = base.evaluate_bpc(
        W, pool_B_v, pool_B_l, pool_B_u,
        byte_atoms, pos_atoms,
        test_b_idx, test_b_tgt, batch_size, device)
    # Re-evaluate B with final W
    bpc_B_after_D = base.evaluate_bpc(
        W, pool_D_v, pool_D_l, pool_D_u,
        byte_atoms, pos_atoms,
        test_b_idx, test_b_tgt, batch_size, device)

    return {
        "retention_A_after_B": float(retention_A_after_B),
        "retention_A_after_C": float(retention_A_after_C),
        "retention_A_after_D": float(retention_A_after_D),
        "bpc_A_baseline":      float(bpc_A_baseline),
        "bpc_A_after_B":       float(bpc_A_after_B),
        "bpc_A_after_C":       float(bpc_A_after_C),
        "bpc_A_after_D":       float(bpc_A_after_D),
        "retention_B_after_D": float(min(bpc_B_baseline / max(bpc_B_after_D, 1e-6), 1.0)),
        "N": N,
        "seed": seed,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    MANDATORY per role contract. Must be called at module scope.
    """
    # 1. Verdict logic self-test
    _selftest_verdict()

    # 2. One forward pass at tiny N to confirm all metrics non-null
    device = torch.device("cpu")
    cfg_tiny = {
        "mode": "smoke",
        "N": 256,
        "batch_size": 16,
        "epochs": 1,
        "phase_a_epochs": 1,
        "bytes_per_corpus": 5_000,
    }
    result = run_one_seed_k1_stress(17, cfg_tiny, device)

    required_keys = [
        "retention_A_after_B",
        "retention_A_after_C",
        "retention_A_after_D",
        "bpc_A_baseline",
        "bpc_A_after_D",
    ]
    for k in required_keys:
        assert k in result, f"[selftest] missing key: {k}"
        v = result[k]
        assert v is not None and not (isinstance(v, float) and v != v), \
            f"[selftest] {k} is null/NaN: {v}"
        assert isinstance(v, float) and v > 0.0, \
            f"[selftest] {k} <= 0 or wrong type: {v}"

    ret_A_D = result["retention_A_after_D"]
    assert 0.0 < ret_A_D <= 1.0, f"[selftest] retention_A_after_D out of (0,1]: {ret_A_D}"

    # 3. Verify _seed_checkpoint wiring (PROT-021)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        write_partial(tmp_path, 17, {"seed": 17, "retention_A_after_D": 0.75})
        done, remaining = resumable_seeds([17, 23], tmp_path)
        assert 17 in done, f"[selftest] seed 17 should be in done: {done}"
        assert 23 in remaining, f"[selftest] seed 23 should be in remaining: {remaining}"

    # 4. HDLAB_EXP_NAME parameterization
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_k1_stress_xyz"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_k1_stress_xyz", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    # 5. Import chain coverage: verify all from-experiments imports resolvable
    assert (_base_path).exists(), f"[selftest] base path missing: {_base_path}"
    assert (_v4s_path).exists(), f"[selftest] 4stage path missing: {_v4s_path}"

    print(f"[selftest] bet_b_k1_ceiling_stress_n8192_v1 PASSED: "
          f"verdict_logic OK, forward pass ret_A_after_D={ret_A_D:.4f}, "
          f"checkpoint_wiring OK, output_path OK, imports OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_k1_ceiling_stress_n8192_v1")
    out_dir = get_output_dir(exp_name)

    config = {
        "mode":              "smoke" if smoke else "full",
        "N":                 N_SMOKE if smoke else N_FULL,
        "batch_size":        BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs":            EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs":    PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus":  BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds":             SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    seeds = config["seeds"]

    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} device={device} "
          f"seeds={seeds}", flush=True)
    cfg_display = {k: v for k, v in config.items() if k != "seeds"}
    print(f"[config] {json.dumps(cfg_display, default=str)}", flush=True)

    # PROT-021: checkpoint-aware seed loop
    done, remaining = resumable_seeds(seeds, out_dir)
    if done:
        print(f"[ckpt] resuming: {len(done)}/{len(seeds)} seeds already complete: {done}",
              flush=True)

    for seed in remaining:
        print(f"[seed] starting seed={seed}", flush=True)
        r = run_one_seed_k1_stress(seed, config, device)
        write_partial(out_dir, seed, r)
        print(f"  seed={seed}: ret_A_B={r['retention_A_after_B']:.3f} "
              f"ret_A_C={r['retention_A_after_C']:.3f} "
              f"ret_A_D={r['retention_A_after_D']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, seeds)
    if len(per_seed) == 0:
        print("[ERROR] aggregate_partials returned empty -- no seeds completed.", flush=True)
        sys.exit(1)
    if len(per_seed) < len(seeds):
        print(f"[WARN] only {len(per_seed)}/{len(seeds)} seeds completed; "
              f"partial verdict follows.", flush=True)

    verdict, msg = compute_verdict(per_seed)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict":      verdict,
        "verdict_msg":  msg,
        "elapsed_s":    elapsed,
        "summary":      {"per_seed": per_seed},
        "config":       config,
        "n_seeds_done": len(per_seed),
        "n_seeds_total": len(seeds),
    }
    mpath = out_dir / "metrics.json"
    tmp = mpath.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, mpath)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke",     action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
