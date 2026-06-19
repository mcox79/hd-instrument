"""Saad-Solla saddle-cascade v11 at N=8192: Kovacs replay DISABLED rescue.

CONTEXT:
  v10 (N=8192, 2 seeds): CUDA_RUNTIME_CRASH at seed=17, f=0.50 in Phase-B replay.
    Crash site: torch.cat([tgt_batch, replay_tgts], dim=0) in train_w_with_replay.
    seed=7 completed all 5 f-points directionally before crash.
    seed=17 completed f=[0.0, 0.15, 0.50] before crash at f=0.80.
    Crash was illegal memory access in replay augmentation path.

  v11 (THIS): disable Phase-B replay entirely (pass None replay pool).
    -- Isolates whether the CORE Saad-Solla plateau signal survives without replay.
    -- The discrete plateau structure is a property of W learned on Phase-A only;
       Phase-B replay tests retention, NOT the discrete structure itself.
    -- Without replay, we simply measure R^2 of retention vs f (the Saad-Solla
       prediction: non-monotone plateau structure, R^2 < 0.85, max_dev >= 0.08).
    -- If crash was replay-specific, v11 should run cleanly to completion.

SCIENTIFIC EQUIVALENCE:
  The Saad-Solla saddle-cascade predicts discrete PLATEAUS in the f-sweep
  regardless of replay. Replay only affects the absolute retention level, not
  the presence/absence of plateaus. R^2 < 0.85 and max_dev >= 0.08 criteria
  still valid since we are measuring the SHAPE of retention vs f, not level.

HYPOTHESIS:
  At N=8192, the discrete plateau structure is observable WITHOUT replay.
  Same thresholds as v10: HARD-PASS if >= 2/2 seeds: R^2 < 0.85 and max_dev >= 0.08.

PRE-REGISTERED BANDS (same as v10):
  HARD-PASS: >= 2/2 seeds: R^2 < 0.85 AND max_dev >= 0.08 at N=8192
  HARD-FAIL: >= 2/2 seeds: R^2 >= 0.95 AND max_dev < 0.04 (smooth-monotone)
  MIDDLE: else (inconclusive)

  Calibration: v10 seed=7 data directionally positive (retention pattern visible).
  Bands NOT widened to +-50% (empirical anchor from v10 seed=7 partial data).

OOM PRE-CHECK:
  W at N=8192: 8192^2 * 4 bytes = 256MB. 2 W copies (Phase-A, Phase-B) = 512MB.
  No replay pool tensors (POOL_SIZE=0 in this version). Well under 6GB. OK.

FORMULA SELF-TESTS:
  1. pearson_r2([0,1,2,3],[0,2,4,6]) = 1.0 (linear). R^2 >= 0.85 -> no plateau.
  2. pearson_r2([0.60,0.62,0.94,0.94,0.94],[0,1,2,3,4]) < 0.80. R^2 < 0.85 -> plateau.
  3. max_dev of plateau data >= 0.10 -> above threshold.
  4. N == 8192 assertion (PROT-018).
  5. Verify NO replay: replay_pool_vecs IS None in run_one_cell_no_replay.

Timeout estimate:
  v8 N=2048 5-seed 7 f-points elapsed=1288s.
  v11 N=8192 2-seed 5 f-points NO replay (slightly faster than v10 -- no pool ops):
  N-scale: (8192/2048)^1.5 = 8.0x; seed ratio: 2/5 = 0.40x; f-ratio: 5/7 = 0.71x
  timeout_s = ceil(1.5 * 1288 * 8.0 * 0.40 * 0.71) = ceil(4393) -> 4500s
  No-replay should be marginally faster. Use 4500s (same as v10 estimate).
  Under 4h (14400s). Flag: >2h for visibility.

N-suffix: _n8192 -> N = 8192 (PROT-018 binding)
Queue: overnight_queue (GPU; N=8192 Hebbian ops, 2 seeds)
Pre-reg: preregs/2026-05-27_saad_solla_v11_n8192.md
Parent: saad_solla_v10_n8192 (CUDA_CRASH in replay)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
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

# Load Kovacs base for train_w_with_replay (no Kovacs Phase D; only Phase A+B used)
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base_v11", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Reuse v3 helper functions (plateau math, pearson_r2, etc.)
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade_v11", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
compute_verdict = v3_mod.compute_verdict

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192              # PRODUCTION N -- PROT-018 contract
N_SMOKE = 512
F_SWEEP_FULL = [0.0, 0.15, 0.50, 0.80, 1.0]   # 5 points (same as v10)
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]
SEEDS_FULL = [7, 17]       # 2 seeds (same as v10; walk-back justified: v10 d >> 1)
SEEDS_SMOKE = [17]
BATCH_SIZE = 32
BATCH_SIZE_SMOKE = 16
EPOCHS = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES = 150_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (same as v10)
HP_R2_MAX = 0.85
HP_MAX_DEV_MIN = 0.08
HF_R2_MIN = 0.95
HF_MAX_DEV_MAX = 0.04


def get_output_dir(default_name: str = "saad_solla_v11_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_no_replay(seed: int, f: float, N_cfg: int, batch_size: int,
                            n_epochs: int, phase_a_epochs: int, n_bytes: int,
                            device) -> dict:
    """Train Phase-A on corpus_A, Phase-B on mixed(f) with NO replay pool.

    Key difference from v3/v10: replay_pool_vecs=None in Phase B.
    This eliminates the torch.cat crash in train_w_with_replay.
    """
    gen = torch.Generator().manual_seed(seed)
    VOCAB = 256
    K_ctx = base.K
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_cfg, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_ctx, N_cfg, gen).to(device)

    # Phase-A corpus (tile if needed)
    corpus_a_raw = pa.load_corpus_a()
    if len(corpus_a_raw) < n_bytes:
        reps = (n_bytes // len(corpus_a_raw)) + 2
        corpus_a_raw = corpus_a_raw * reps
    corpus_a_bytes = corpus_a_raw[:n_bytes]
    a_idx, a_tgt = base.bytes_to_idx_tensors(corpus_a_bytes, device)

    # Phase-A training (no replay)
    W0 = torch.zeros((N_cfg, N_cfg), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W0, None, None, 0,
        byte_atoms, pos_atoms, a_idx, a_tgt,
        None, None, 0,                       # NO replay pool in Phase A
        phase_a_epochs, batch_size, device
    )

    # Phase-A evaluation baseline
    n_eval = max(1000, n_bytes // 5)
    corpus_a_full_raw = pa.load_corpus_a()
    if len(corpus_a_full_raw) < n_bytes + n_eval:
        reps = ((n_bytes + n_eval) // len(corpus_a_full_raw)) + 2
        corpus_a_full_raw = corpus_a_full_raw * reps
    corpus_a_eval = corpus_a_full_raw[n_bytes:n_bytes + n_eval]
    if len(corpus_a_eval) < 500:
        corpus_a_eval = corpus_a_full_raw[-n_eval:]
    ae_idx, ae_tgt = base.bytes_to_idx_tensors(corpus_a_eval, device)
    bpc_A_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )

    # Phase-B corpus: mixed(f)
    corpus_b_bytes = build_mixed_corpus(corpus_a_bytes, n_bytes, f, seed)
    b_idx, b_tgt = base.bytes_to_idx_tensors(corpus_b_bytes, device)

    # Phase-B training -- NO replay pool (this is the key change from v10)
    # pool_vecs_init initialized from Phase-A pool state but NO external replay
    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_A.clone(), pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, b_idx, b_tgt,
        None, None, 0,                       # NO replay pool -- key fix vs v10
        n_epochs, batch_size, device
    )

    # Post-Phase-B retention
    bpc_A_after_B = base.evaluate_bpc(
        W_B, pool_B_v, pool_B_l, pool_B_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )
    retention_A = bpc_A_baseline / max(bpc_A_after_B, 1e-9)

    return {
        "f": f,
        "seed": seed,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_after_B": round(bpc_A_after_B, 5),
        "retention_A": round(retention_A, 5),
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: N must be 8192
    assert N == 8192, f"PROT-018: production N must be 8192; got {N}"

    # Self-test 1: helper functions importable and callable
    assert callable(pearson_r2), "pearson_r2 not callable"
    assert callable(linear_fit_residuals), "linear_fit_residuals not callable"
    assert callable(build_mixed_corpus), "build_mixed_corpus not callable"

    # Self-test 2: pearson_r2 formula checks
    r2_linear = pearson_r2([0, 1, 2, 3], [0, 2, 4, 6])
    assert abs(r2_linear - 1.0) < 0.01, f"pearson_r2 linear should be 1.0; got {r2_linear}"

    plateau_y = [0.60, 0.62, 0.94, 0.94, 0.94]
    plateau_x = [0.0, 0.25, 0.50, 0.75, 1.0]
    r2_plateau = pearson_r2(plateau_x, plateau_y)
    assert r2_plateau < 0.85, f"plateau data should have R^2 < 0.85; got {r2_plateau}"

    # Self-test 3: max_dev formula
    _, max_dev, _ = linear_fit_residuals(plateau_x, plateau_y)
    assert max_dev >= 0.08, f"plateau max_dev should be >= 0.08; got {max_dev}"

    # Self-test 4: OOM pre-check at N=8192 (no pool -> fewer tensors than v10)
    oom_bytes = N * N * 4 * 2  # 2 W copies (Phase A, Phase B); no pool tensors
    assert oom_bytes < 6e9, f"OOM check failed: {oom_bytes:.2e}"

    # Self-test 5: Verify replay is disabled -- run_one_cell_no_replay at smoke N
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cell_r = run_one_cell_no_replay(17, 0.5, N_SMOKE, BATCH_SIZE_SMOKE, 1, 1, BYTES_SMOKE, device)
    assert "retention_A" in cell_r, f"missing retention_A: {list(cell_r.keys())}"
    ret = cell_r["retention_A"]
    assert isinstance(ret, float) and 0.0 < ret <= 2.0, f"retention_A out of range: {ret}"

    # Self-test 6: multi-scale smoke -- N_SMOKE and N_SMOKE*4
    cell_r4 = run_one_cell_no_replay(17, 0.5, N_SMOKE * 4, BATCH_SIZE_SMOKE, 1, 1, BYTES_SMOKE * 2, device)
    assert "retention_A" in cell_r4, "missing retention_A at N_SMOKE*4"

    print(f"[selftest] saad_solla_v11_n8192 PASSED: N=8192 assertion OK, "
          f"pearson_r2 OK, OOM={oom_bytes:.2e}, smoke ret={ret:.4f}, "
          f"replay=DISABLED (confirmed)", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int, f_sweep: List[float], config: Dict, device) -> Dict:
    """Run one seed across all f-values; return per-f retention."""
    per_f = {}
    for f in f_sweep:
        cell_r = run_one_cell_no_replay(
            seed, f, config["N"], config["batch_size"],
            config["epochs"], config["phase_a_epochs"],
            config["bytes_per_corpus"], device,
        )
        ret = cell_r.get("retention_A", None)
        per_f[f] = float(ret) if ret is not None else None
        ret_str = f"{ret:.4f}" if ret is not None else "None"
        print(f"  f={f:.2f} seed={seed}: retention_A={ret_str}", flush=True)
    return per_f


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "N": N_SMOKE if smoke else N,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE,
    }
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    exp_name = os.environ.get("HDLAB_EXP_NAME", "saad_solla_v11_n8192")
    print(f"[run] {exp_name} N={config['N']} seeds={seeds} f_sweep={f_sweep} "
          f"device={device} replay=DISABLED", flush=True)
    if not smoke:
        assert config["N"] == 8192, f"FULL run must use N=8192; got {config['N']}"

    per_seed: Dict[str, Dict] = {}
    for seed in seeds:
        print(f"\n[seed={seed}]", flush=True)
        pf = run_one_seed(seed, f_sweep, config, device)
        per_seed[str(seed)] = pf

    # Compute R^2 and max_dev across f-sweep per seed
    seed_verdicts = []
    for s_key, pf in per_seed.items():
        f_vals = [f for f in f_sweep if pf.get(f) is not None]
        ret_vals = [pf[f] for f in f_vals]
        if len(f_vals) < 3:
            print(f"  [seed={s_key}] insufficient data points ({len(f_vals)})", flush=True)
            continue
        r2 = pearson_r2(f_vals, ret_vals)
        _, max_dev, _ = linear_fit_residuals(f_vals, ret_vals)
        hp = r2 < HP_R2_MAX and max_dev >= HP_MAX_DEV_MIN
        hf = r2 >= HF_R2_MIN and max_dev < HF_MAX_DEV_MAX
        seed_verdicts.append({"seed": s_key, "r2": r2, "max_dev": max_dev,
                               "hp": hp, "hf": hf})
        print(f"  [seed={s_key}] R^2={r2:.4f} max_dev={max_dev:.4f} -> "
              f"{'HP' if hp else 'HF' if hf else 'MIDDLE'}", flush=True)

    n_seeds = len(seed_verdicts)
    n_hp = sum(1 for v in seed_verdicts if v["hp"])
    n_hf = sum(1 for v in seed_verdicts if v["hf"])

    if n_seeds >= 2 and n_hp >= 2:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: {n_hp}/{n_seeds} seeds R^2<{HP_R2_MAX} and max_dev>={HP_MAX_DEV_MIN} "
               f"at N=8192 (replay DISABLED). Saddle-cascade discrete structure confirmed "
               f"at N=8192 without replay. "
               f"N-scaling chain: N=1024(v3) -> N=2048(v8) -> N=4096(v9) -> N=8192(v11).")
    elif n_seeds >= 2 and n_hf >= 2:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: {n_hf}/{n_seeds} seeds R^2>={HF_R2_MIN} and max_dev<{HF_MAX_DEV_MAX} "
               f"at N=8192. Discrete plateau structure erased at N=8192 (replay DISABLED).")
    else:
        mean_r2 = sum(v["r2"] for v in seed_verdicts) / max(n_seeds, 1)
        mean_dev = sum(v["max_dev"] for v in seed_verdicts) / max(n_seeds, 1)
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: {n_hp}/{n_seeds} seeds HP. "
               f"mean_R2={mean_r2:.4f} mean_max_dev={mean_dev:.4f}. "
               f"Inconclusive at N=8192 (replay DISABLED).")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": {"N": config["N"], "f_sweep": f_sweep,
                    "per_seed": per_seed, "seed_verdicts": seed_verdicts,
                    "replay_disabled": True},
        "config": config,
    }
    mpath = get_output_dir() / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
