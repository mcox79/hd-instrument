"""PB-3 CRITICAL SLOWING v6: v3-IDENTICAL REPRODUCTION (rehabilitation gate R2).

PARENT: exp_pb3_extended_v3_n4096.py (PB3V3_HARD_PASS ratio=1.64).
  v4_n8192 HARD_FAIL (flat tau), v5_n4096 HARD_FAIL (flat tau).
  2nd-strike rehabilitation per notes/strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md.

SCIENTIFIC QUESTION (R2 rehabilitation gate):
  Re-run PB-3 at the EXACT v3 config (same N=4096, same seeds, same betas, same BSC codebook).
  If v6 REPRODUCES v3's positive result: v4/v5 failures are an N-extension regime issue.
  If v6 reproduces FLAT tau_recovery=0: v3 itself was an artifact (bug, fluke, precision issue).
  This binary outcome either closes PB-3 row (3rd strike) or opens R1 intermediate-N rescue.

PRE-REGISTERED BANDS (re-test of v3 config; NOT an envelope expansion):
  Prior anchor: v3 ratio=1.64, tau_recovery > 0 at {2,4,6,8,10,12,16}.
  HARD_PASS: ratio >= 1.5 AND tau_peak_beta in {6,8,10} (reproduces v3 positive result).
  HARD_FAIL: tau_recovery < 0.1 at ALL seeds at ALL betas (flat; v3 was an artifact).
  MIDDLE_BAND: ratio in [1.0, 1.5) or partial tau signal (weaker than v3).

  NOTE: NOT a calibration probe (prior empirical anchor exists from v3).
  Bands NOT widened. HP = 1.5 (same as v3).

FORMULA SELF-TESTS (inherited from v3 + added v6-specific):
  1. tau_ratio = max_tau / min_tau. For v3 reference: ratio=1.64.
     Input: tau_by_beta = {2:61, 4:85, 6:100, 8:90, 10:75, 12:64, 16:61}. ratio=1.639.
  2. HARD_PASS fires for ratio >= 1.5 AND peak in {6,8,10}.
  3. HARD_FAIL fires for ratio < 1.0.
  4. N == 4096 (PROT-018 binding).
  5. v3-identical config: N=4096, SEEDS=[7,17,23,31,41], BETAS=[2,4,6,8,10,12,16].
  6. v6 reproduction verdict should match v3 if substrate is deterministic at this N.

OOM CHECK: N=4096, W=64MB. CPU memory OK. GPU: far under 6GB. OK.

TIMEOUT ESTIMATE:
  v3 elapsed: ~10800s (3h) at N=4096, 5 seeds, 7 betas (from preregs).
  v6 is IDENTICAL config. timeout_s = 14400 (floor for _n4096, with safety margin vs v3's 10800s).
  PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: pb3_extended_v6_v3identical_n4096
Queue: overnight_queue (GPU; N=4096; v3-identical config; 5 seeds x 7 betas)
Pre-reg: preregs/2026-05-29_pb3_extended_v6_v3identical_n4096.md
Parent: exp_pb3_extended_v3_n4096.py (PB3V3_HARD_PASS ratio=1.64 -- the result to reproduce)
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
from typing import Dict, List
from collections import defaultdict

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v3 entirely -- run_one_seed, compute_verdict, pa all come from v3
_v3_path = REPO / "experiments" / "exp_pb3_extended_v3_n4096.py"
_v3_spec = importlib.util.spec_from_file_location("pb3v3_v6", _v3_path)
v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3)

pa = v3.pa

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
# v3-IDENTICAL config (must match v3 exactly for this to be a valid reproduction)
N_FULL  = 4096    # PROT-018 binding contract; also matches v3.N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
assert v3.N == 4096, f"v3 N must be 4096 for v3-identical config; got {v3.N}"

# Inherit EXACTLY from v3 (the reproduction guarantee)
BETA_SWEEP_FULL  = v3.BETA_SWEEP_FULL    # [2,4,6,8,10,12,16]
BETA_SWEEP_SMOKE = v3.BETA_SWEEP_SMOKE   # [4,8]
SEEDS_FULL  = v3.SEEDS_FULL              # [7,17,23,31,41]
SEEDS_SMOKE = v3.SEEDS_SMOKE             # [17]
K    = v3.K    # 4
VOCAB = v3.VOCAB  # 256

# v3 thresholds (reproduced verbatim)
SLOWING_RATIO  = v3.SLOWING_RATIO   # 1.5
PEAK_BETA_SET  = v3.PEAK_BETA_SET   # {6.0, 8.0, 10.0}

# Pre-registered thresholds for v6 (same as v3; not an envelope expansion)
HP_RATIO  = 1.5    # HARD_PASS: ratio >= 1.5 (v3 bar)
HF_RATIO  = 1.0    # HARD_FAIL: ratio < 1.0


def get_output_dir(default_name: str = "pb3_extended_v6_v3identical_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Identical to v3.run_one_seed: same codebook, same config."""
    return v3.run_one_seed(seed, config, device)


def compute_verdict(summary: dict) -> tuple:
    """Compute verdict; reuse v3 verdict logic; prefix with V6 for tracking."""
    v3_verdict, v3_msg = v3.compute_verdict(summary)
    # Re-label to V6 while preserving outcome semantics
    v6_verdict = v3_verdict.replace("PB3V3", "PB3V6")
    return (v6_verdict, "[V3-IDENTICAL REPRO] " + v3_msg)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(BETA_SWEEP_FULL) == 7, f"v3-identical: should have 7 betas; got {BETA_SWEEP_FULL}"
    assert len(SEEDS_FULL) == 5, f"v3-identical: should have 5 seeds; got {SEEDS_FULL}"

    # Formula self-test 1: tau_ratio formula (v3 reference point)
    tau_v3_ref = {2: 61, 4: 85, 6: 100, 8: 90, 10: 75, 12: 64, 16: 61}
    max_t = max(tau_v3_ref.values())
    min_t = max(1, min(tau_v3_ref.values()))
    ratio = max_t / min_t
    assert abs(ratio - 1.639) < 0.01, f"v3 reference ratio should be ~1.64; got {ratio}"

    # Formula self-test 2: HARD_PASS gate
    def mk_pass_seed(seed: int) -> dict:
        per_beta = {str(b): {"tau_recovery": tau_v3_ref.get(b, 70)} for b in [2, 4, 6, 8, 10, 12, 16]}
        return {"per_beta": per_beta}
    summary_p = {"per_seed": {str(s): mk_pass_seed(s) for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_p)
    assert "HARD_PASS" in v, f"Expected HARD_PASS for v3-reference data; got {v}: {msg}"

    # Formula self-test 3: HARD_FAIL gate
    def mk_fail_seed(seed: int) -> dict:
        per_beta = {str(b): {"tau_recovery": 0} for b in [2, 4, 6, 8, 10, 12, 16]}
        return {"per_beta": per_beta}
    summary_f = {"per_seed": {str(s): mk_fail_seed(s) for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_f)
    assert "HARD_FAIL" in v, f"Expected HARD_FAIL for flat-tau data; got {v}: {msg}"

    # Formula self-test 4: smoke forward pass at tiny N
    device = torch.device("cpu")
    cfg_smoke = {
        "smoke": True,
        "N": N_SMOKE,
        "beta_sweep": BETA_SWEEP_SMOKE,
        "n_edits": v3.N_EDITS_SMOKE,
        "n_recovery": v3.N_RECOVERY_SMOKE,
        "t_train": v3.T_TRAIN_SMOKE,
        "t_eval": v3.T_EVAL_SMOKE,
    }
    result = run_one_seed(17, cfg_smoke, device)
    assert "per_beta" in result, f"Missing per_beta: {list(result.keys())}"
    betas_found = list(result["per_beta"].keys())
    assert len(betas_found) >= 2, f"Expected >= 2 betas; got {betas_found}"
    for bk in betas_found:
        cell = result["per_beta"][bk]
        assert "tau_recovery" in cell, f"Missing tau_recovery in beta={bk}"
        tau = cell["tau_recovery"]
        assert isinstance(tau, (int, float)) and tau >= 0, f"tau_recovery invalid: {tau}"

    print(f"[SELFTEST PASS] pb3_extended_v6_v3identical_n4096: "
          f"v3_ref_ratio={ratio:.3f} HARD_PASS/FAIL gates OK "
          f"smoke_betas_found={betas_found} tau_sample={result['per_beta'][betas_found[0]]['tau_recovery']}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    config = {
        "smoke": smoke,
        "N": N,
        "beta_sweep": beta_sweep,
        "n_edits": v3.N_EDITS_SMOKE if smoke else v3.N_EDITS_FULL,
        "n_recovery": v3.N_RECOVERY_SMOKE if smoke else v3.N_RECOVERY_FULL,
        "t_train": v3.T_TRAIN_SMOKE if smoke else v3.T_TRAIN_FULL,
        "t_eval": v3.T_EVAL_SMOKE if smoke else v3.T_EVAL_FULL,
    }
    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[pb3v6] V3-IDENTICAL REPRO N={N} seeds={seeds} betas={beta_sweep} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        pb = result.get("per_beta", {})
        taus = [pb[bk].get("tau_recovery", 0) for bk in pb]
        print(f"  seed {seed}: {te:.1f}s taus={taus}", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "beta_sweep": beta_sweep,
        "smoke": smoke,
        "v3_identical": True,
        "rehabilitation_gate": "R2",
    }

    out_dir2 = get_output_dir()
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[pb3v6] VERDICT: {verdict}", flush=True)
    print(f"[pb3v6] {verdict_msg}", flush=True)
    print(f"[pb3v6] elapsed={elapsed}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
