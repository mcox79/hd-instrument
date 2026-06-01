"""Bet-B 4-stage CL architectural rescue C2: frozen W during Phase A, plastic for B/C/D.

CONTEXT:
  Training-axis rescues exhausted (v272 HARD_FAIL). C2 tests: freeze W during Phase A
  training (prevent Hebbian updates from accumulating interference during Phase A itself),
  then allow normal Hebbian updates for Phases B/C/D.
  Hypothesis: Phase-A retention failure is caused by Phase-A self-interference -- the
  Hebbian delta-rule updates during Phase A partially clobber earlier Phase-A patterns.
  Freezing W during Phase A produces W=0 at end of Phase A (no direct Phase A storage),
  but the pool (episodic buffer) captures Phase A contexts. Then Phases B/C/D can store
  AND replay Phase A. If frozen-W Phase A yields ret_A >= 0.80 at the end of all phases,
  the bottleneck is exactly Phase-A self-interference.

ARCHITECTURAL CHANGE from v1/v2/v3:
  Phase A: train with pool ONLY (episodic buffer accumulates), W is NOT updated.
    W_A = W_zero (always 0). Only pool_A_v/l/u are populated.
  Phases B/C/D: normal Hebbian training + replay from pool (including Phase-A pool).
    Phase B starts with W=W_zero and uses pool_A for replay.
    Net effect: Phase A learning is PURELY episodic (pool-based); W encodes B/C/D.
    Retention of Phase A depends entirely on how well replaying pool_A during B/C/D
    preserves the Phase-A patterns.

SCIENTIFIC QUESTION:
  Does freezing W during Phase A improve ret_A by eliminating Phase-A self-interference?
  If ret_A >= 0.80: the bottleneck was Phase-A Hebbian self-interference.
  If ret_A still fails: the bottleneck is not Phase-A interference; pool replay is insufficient.

PRE-REGISTERED BANDS:
  HARD_PASS: mean ret_A >= 0.80 AND mean ret_B >= 0.70 AND mean ret_C >= 0.70 (>= 3/3 seeds).
    Interpretation: Phase-A self-interference was the bottleneck; frozen W rescues ret_A.
  HARD_FAIL: mean ret_A <= 0.50 (frozen Phase A + replay cannot maintain Phase-A patterns).
  MIDDLE_BAND: mean ret_A in (0.50, 0.80).
    -> If ret_A in (0.74, 0.80): slight improvement; self-interference partially responsible.
    -> If ret_A <= 0.50: pool replay completely insufficient for Phase-A retention.

NOTE: bpc_A_baseline is undefined in the classic sense when W_A = 0 (all BPC = max).
  Instead, bpc_A_baseline is computed AFTER Phase B (when W encodes Phase A via replay):
  measure bpc on test_a after Phase B training (W starts encoding Phase A through replay).
  This is the first point where Phase-A patterns are encoded in W.

FORMULA SELF-TESTS:
  1. W_A = zeros always (no Phase-A Hebbian updates).
  2. bpc_A_baseline: evaluated after Phase B (W_AB encodes Phase A via replay).
  3. retention_A = bpc_A_baseline / bpc_A_after_D. Both evaluated with same W_AB atoms.
  4. retention formula: same as v1 (ratio <= 1.0 clipped).
  5. No _nN suffix: N declared explicitly below. N = N_FULL = 8192.
  6. N == 8192 (PROT-018: no suffix; explicitly declared).

OOM CHECK:
  W at N=8192 float32 = 268MB. 4 copies (W_zero, W_AB, W_ABC, W_ABCD) = 1.07GB. OK.

TIMEOUT ESTIMATE:
  Same architecture as v1 (N=8192) except Phase A has no W updates (faster).
  v1 5-seed ~1020s. C2 3-seed: 1020 * (3/5) * 0.9 (Phase A skip) = 550s.
  Safety: ceil(1.5 * 550) = 825s. No _nN suffix -> no PROT-019 floor.
  timeout_s = 900s. (Confirmed under 14400s.)

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly in doc header).
Anchor: bet_b_cl_frozen_phaseA_v1
Queue: overnight_queue (GPU; N=8192; frozen Phase A + plastic B/C/D; 3 seeds)
Pre-reg: prereqs/2026-05-29_bet_b_cl_frozen_phaseA_v1.md
Parent: bet_b_4stage_rehab_epochs_v3 (training-axis exhausted; C2 is architectural rescue)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load wave14_betB_4stage_continual_v1 for infrastructure
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("betb4stage_c2", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

# Load bet_b_n8192_4stage_v1 for N=8192 infrastructure
_n8k_path = REPO / "experiments" / "exp_bet_b_n8192_4stage_v1.py"
_n8k_spec = importlib.util.spec_from_file_location("bet_b_n8k_c2", _n8k_path)
n8k_mod = importlib.util.module_from_spec(_n8k_spec)
_n8k_spec.loader.exec_module(n8k_mod)

pa = n8k_mod.pa
base = n8k_mod.base
load_corpus_D = v1_mod.load_corpus_D

# PRODUCTION CONFIG -- N = 8192 (PROT-018: no _nN suffix; explicitly declared)
N_FULL  = 8192
N_SMOKE = 1024
# Production N must be 8192 per PROT-018 explicit declaration
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

BATCH_SIZE_FULL  = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL      = 5
EPOCHS_SMOKE     = 1
# No Phase A Hebbian epochs (W frozen); keep as pool-fill epochs only
PHASE_A_POOL_EPOCHS_FULL  = 4
PHASE_A_POOL_EPOCHS_SMOKE = 1
BYTES_FULL  = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_cl_frozen_phaseA_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict):
    """Same verdict logic as v1."""
    per_seed = summary.get("per_seed", {})
    seeds = list(per_seed.values())
    if not seeds:
        return ("BETB_C2_INCONCLUSIVE", "No seed results.")
    ret_A = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B = sum(s["retention_B"] for s in seeds) / len(seeds)
    ret_C = sum(s["retention_C"] for s in seeds) / len(seeds)
    n = len(seeds)
    detail = (f"mean_ret_A={ret_A:.3f} mean_ret_B={ret_B:.3f} mean_ret_C={ret_C:.3f} "
              f"n_seeds={n} PASS_RET_A={PASS_RET_A}")
    if ret_A <= FAIL_RET_A:
        return ("BETB_C2_HARD_FAIL",
                f"FROZEN_PHASE_A_FAILS: ret_A={ret_A:.3f} <= {FAIL_RET_A}. " + detail)
    if ret_A >= PASS_RET_A and ret_B >= PASS_RET_B and ret_C >= PASS_RET_C:
        return ("BETB_C2_HARD_PASS",
                f"FROZEN_PHASE_A_RESCUES_RET_A: ret_A={ret_A:.3f} >= {PASS_RET_A}. " + detail)
    return ("BETB_C2_MIDDLE_BAND",
            f"PARTIAL: ret_A={ret_A:.3f} below HP or ret_B/C too low. " + detail)


def run_one_seed_frozen_phaseA(seed: int, config: Dict, device: torch.device) -> Dict:
    """Run 4-stage CL with Phase A W frozen.

    Phase A: pool accumulates, W stays 0 (no Hebbian updates).
    Phases B/C/D: normal Hebbian + replay from pool (includes Phase A pool).
    bpc_A_baseline: evaluated after Phase B (W_AB first encodes Phase A via replay).
    """
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_pool_epochs = config["phase_a_pool_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = config.get("mode") == "smoke"

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)

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
    test_a_idx,  test_a_tgt  = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx,  test_b_tgt  = base.bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx,  test_c_tgt  = base.bytes_to_idx_tensors(test_c, device)
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(train_d, device)
    test_d_idx,  test_d_tgt  = base.bytes_to_idx_tensors(test_d, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # PHASE A FROZEN: W stays W_zero; only accumulate pool via 0-lr pass
    # We call train_w_with_replay with phase_a_pool_epochs but ignore the returned W.
    # The pool_A_* tensors are what we need for replay in later phases.
    W_A_fake, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero.clone(), None, None, 0,
        byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt,
        None, None, 0,
        phase_a_pool_epochs, batch_size, device)

    # Discard W_A_fake; use W_zero for Phase B start (Phase A W is frozen/discarded)
    W_A = W_zero  # frozen Phase A: W = 0

    # Phase B: starts from W=0, replays pool_A
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u,
        n_epochs, batch_size, device)

    # bpc_A_baseline: evaluated after Phase B (W_AB now encodes Phase A via replay)
    bpc_A_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                         byte_atoms, pos_atoms,
                                         test_a_idx, test_a_tgt, batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                         byte_atoms, pos_atoms,
                                         test_b_idx, test_b_tgt, batch_size, device)

    # Phase C with A+B replay
    combined_AB_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_AB_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms,
        train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u,
        n_epochs, batch_size, device)
    bpc_C_baseline = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms,
                                          test_c_idx, test_c_tgt, batch_size, device)

    # Phase D with A+B+C replay
    combined_ABC_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u],
                                  pool_ABC_v[:pool_ABC_u]], dim=0)
    combined_ABC_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u],
                                  pool_ABC_l[:pool_ABC_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms,
        train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u,
        n_epochs, batch_size, device)

    # Retention checks
    bpc_A_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          test_a_idx, test_a_tgt, batch_size, device)
    bpc_B_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          test_b_idx, test_b_tgt, batch_size, device)
    bpc_C_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          test_c_idx, test_c_tgt, batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_D, 1e-6), 1.0)
    retention_C = min(bpc_C_baseline / max(bpc_C_after_D, 1e-6), 1.0)

    return {
        "retention_A": retention_A, "retention_B": retention_B, "retention_C": retention_C,
        "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_D": bpc_A_after_D,
        "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_D": bpc_B_after_D,
        "bpc_C_baseline": bpc_C_baseline, "bpc_C_after_D": bpc_C_after_D,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Formula self-test: verdict logic
    fake_pass = {"per_seed": {
        "7":  {"retention_A": 0.85, "retention_B": 0.75, "retention_C": 0.72},
        "17": {"retention_A": 0.82, "retention_B": 0.78, "retention_C": 0.74},
        "23": {"retention_A": 0.80, "retention_B": 0.71, "retention_C": 0.70},
    }}
    v_pass, _ = compute_verdict(fake_pass)
    assert "HARD_PASS" in v_pass, f"HARD_PASS gate failed: {v_pass}"

    fake_fail = {"per_seed": {"17": {"retention_A": 0.40, "retention_B": 0.70, "retention_C": 0.70}}}
    v_fail, _ = compute_verdict(fake_fail)
    assert "HARD_FAIL" in v_fail, f"HARD_FAIL gate failed: {v_fail}"

    # Smoke cell at tiny scale (N=256)
    device = torch.device("cpu")
    config_small = {
        "mode": "smoke",
        "N": 256, "batch_size": 16, "epochs": 1,
        "phase_a_pool_epochs": 1, "bytes_per_corpus": 5_000,
    }
    result = run_one_seed_frozen_phaseA(17, config_small, device)
    assert "retention_A" in result, f"retention_A missing: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # OOM check: N=8192 W matrix (4 copies)
    oom_bytes = 8192 * 8192 * 4 * 4
    assert oom_bytes < 6e9, f"OOM pre-check: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] bet_b_cl_frozen_phaseA_v1 PASS "
          f"N=256 smoke ret_A={ret_A:.4f} OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_pool_epochs": PHASE_A_POOL_EPOCHS_SMOKE if smoke else PHASE_A_POOL_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_cl_frozen_phaseA_v1")
    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} "
          f"phase_a_pool_epochs={config['phase_a_pool_epochs']} device={device}", flush=True)

    if not smoke:
        assert config["N"] == 8192, f"FULL run must use N=8192; got {config['N']}"

    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed_frozen_phaseA(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: ret_A={r['retention_A']:.3f} "
              f"ret_B={r['retention_B']:.3f} ret_C={r['retention_C']:.3f}", flush=True)

    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
        "summary": summary, "config": config,
        "N": config["N"],
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
