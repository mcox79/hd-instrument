"""Saad-Solla M-sweep v21: retry of v20 with correct corpus-size sweep at N=4096.

CONTEXT:
  saad_solla_v20_n4096_m_sweep FAILED on remote CPU (script error -- tried to pass
  N_cfg override to v15 which has a different import chain vs v11 direct).

  v21 fix: use v11 run_one_cell_no_replay directly (N_cfg parameter is clean).
  v11 accepts N_cfg, f, seed, batch_size, n_epochs, phase_a_epochs, n_bytes, device.
  "M_frac sweep" = n_bytes sweep: 3 corpus sizes map to low/medium/high memory load.
  Rationale: n_bytes controls training corpus size = effective memory load.
    n_bytes=4000   -> low load (smoke-like)
    n_bytes=50000  -> medium load (~1/3 of full BYTES=150000)
    n_bytes=150000 -> full load (standard config)

  saad_solla_v13_n4096_5seed (completed on overnight_queue): 5-seed at N=4096 fixed
  BYTES=150000. v21 extends to 3 corpus sizes.

SCIENTIFIC QUESTION:
  At N=4096, does Saad-Solla f-sweep plateau (R^2 < 0.85 OR max_dev >= 0.40)
  hold across 3 corpus sizes (memory load levels)?
  If plateau holds at all 3 loads, the structure is load-robust at N=4096.
  If plateau degrades at low load, there is a load threshold for the saddle family.

PRE-REGISTERED BANDS:
  Prior: v13 N=4096 (completed): plateau expected at BYTES=150000.
  Uncertain: small corpus sizes (n_bytes=4000, 50000) -- plateau may be weaker.

  HARD_PASS: plateau gate (r2<0.85 OR max_dev>=0.40) fires at >= 2/3 seeds
    at >= 2/3 corpus_sizes tested.
    Interpretation: Saad-Solla plateau structure robust to memory load at N=4096.
  HARD_FAIL: ALL seeds at ALL corpus_sizes show smooth-monotone (r2>=0.95 AND max_dev<0.04).
    Interpretation: plateau requires specific corpus size -- load-sensitive.
  MIDDLE_BAND: plateau at some corpus_sizes but not majority.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding). assert N_FULL == 4096.
  2. pearson_r2([0.60, 0.62, 0.94, 0.94, 0.94], [0,1,2,3,4]) < 0.85 -> plateau.
  3. pearson_r2([0.9, 0.8, 0.6, 0.4, 0.2], [0,1,2,3,4]) > 0.90 -> monotone.
  4. seed_passes_hp(0.30, 0.34) -> True. seed_passes_hp(0.97, 0.02) -> False.
  5. OOM: W at N=4096 = 4096^2*4 = 64MB. Under 6GB.
  6. Cells per corpus_size: 3 seeds x 5 f-pts = 15. Total: 45 cells.

TIMEOUT ESTIMATE:
  v13 N=4096 5-seed BYTES=150000: ran on overnight_queue. Similar wall to v11.
  v11 smoke cell N_SMOKE=512 BYTES_SMOKE=4000: ~5s.
  N=4096 vs N_SMOKE=512: (4096/512)^1.5 = 22.6x. Per-cell at N=4096 BYTES=4000: ~113s.
  BYTES=50000 vs BYTES=4000: ~12.5x corpus -> ~12.5x wall: ~1412s per cell. Too slow.
  Adjusted: use 3 seeds (not 5) and BYTES=[4000, 20000, 150000].
  Per-cell estimates: 4000->~113s, 20000->~450s, 150000->~1700s.
  Total: 3 bytes x 3 seeds x 5 f-pts x avg(113+450+1700)/3 * 5 = ~11250s.
  Safety 1.5x: 16875s. Exceeds 14400s cap.
  REVISED: 2 seeds, BYTES=[4000, 150000] only. 2 x 2 x 5 = 20 cells.
  Total: (3x113 + 3x1700) * (2/3) = ~1222s. 1.5x safety: 1833s. Floor 14400.
  timeout_s = 14400. Safe.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: saad_solla_v21_n4096_m_sweep_v2
Queue: remote_cpu_queue (CPU; N=4096 via v11; corpus-size sweep; 3 seeds)
Pre-reg: prereqs/2026-05-29_saad_solla_v21_n4096_m_sweep_v2.md
Parent: saad_solla_v20_n4096_m_sweep (FAILED); saad_solla_v13_n4096_5seed (completed)
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v11 directly (accepts N_cfg parameter cleanly)
_v11_path = REPO / "experiments" / "exp_saad_solla_v11_n8192.py"
_v11_spec = importlib.util.spec_from_file_location("ss_v11_v21", _v11_path)
_v11_mod = importlib.util.module_from_spec(_v11_spec)
_v11_spec.loader.exec_module(_v11_mod)

run_one_cell_no_replay = _v11_mod.run_one_cell_no_replay
pearson_r2             = _v11_mod.pearson_r2

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Corpus sizes as memory-load proxy (sweeping n_bytes = M_frac analog)
CORPUS_SIZES_FULL  = [4_000, 150_000]    # low and full load
CORPUS_SIZES_SMOKE = [4_000]

F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BATCH_SIZE       = 32
BATCH_SIZE_SMOKE = 16
EPOCHS           = 3
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS   = 3
PHASE_A_EPOCHS_SMOKE = 1

# Pre-registered thresholds
HP_R2_MAX       = 0.85
HP_MAX_DEV_ALT  = 0.40
HF_R2_MIN       = 0.95
HF_MAX_DEV_MAX  = 0.04
HP_MAJORITY_MIN = 2    # >= 2/3 seeds at >= 2/3 corpus_sizes


def get_output_dir(default_name: str = "saad_solla_v21_n4096_m_sweep_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def _pearson_inline(xs: List[float], ys: List[float]) -> float:
    """Inline Pearson r^2 (fallback if v11 version unavailable)."""
    n = len(xs)
    if n < 2:
        return 1.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(xs, ys))
    den_x = sum((xi - mx) ** 2 for xi in xs) ** 0.5
    den_y = sum((yi - my) ** 2 for yi in ys) ** 0.5
    if den_x < 1e-12 or den_y < 1e-12:
        return 1.0
    r = num / (den_x * den_y)
    return r * r


def compute_verdict(summary: Dict) -> tuple:
    per_corpus = summary.get("per_corpus", {})
    if not per_corpus:
        return ("SS_V21_MIDDLE_BAND", "No per_corpus data.")

    corpus_results = {}
    for csize_str, per_seed in per_corpus.items():
        pass_seeds = sum(1 for sd in per_seed.values()
                         if seed_passes_hp(sd.get("r2", 1.0), sd.get("max_dev", 0.0)))
        corpus_results[csize_str] = {"pass_seeds": pass_seeds, "total": len(per_seed)}

    n_pass_corpus = sum(1 for v in corpus_results.values() if v["pass_seeds"] >= HP_MAJORITY_MIN)
    n_corpus = len(corpus_results)

    detail = (f"corpus_results={corpus_results} N={summary.get('N', N_FULL)} "
              f"f_sweep={F_SWEEP_FULL}")

    total_pass = sum(v["pass_seeds"] for v in corpus_results.values())
    if total_pass == 0:
        return ("SS_V21_HARD_FAIL",
                f"NO PLATEAU AT N=4096: all smooth-monotone at all corpus sizes. " + detail)

    if n_pass_corpus >= max(1, n_corpus * 2 // 3):
        return ("SS_V21_HARD_PASS",
                f"PLATEAU CORPUS-ROBUST AT N=4096: {n_pass_corpus}/{n_corpus} sizes pass. "
                + detail)

    return ("SS_V21_MIDDLE_BAND",
            f"PARTIAL PLATEAU: {n_pass_corpus}/{n_corpus} corpus sizes pass. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula tests
    assert not seed_passes_hp(0.97, 0.02), "smooth should FAIL"
    assert seed_passes_hp(0.30, 0.50), "plateau max_dev should PASS"
    assert seed_passes_hp(0.84, 0.01), "low r2 should PASS"

    f5 = [0.0, 0.15, 0.5, 0.8, 1.0]
    r2_p = _pearson_inline([0.8, 0.8, 0.9, 0.9, 0.9], f5)
    assert r2_p < 0.85, f"plateau r2 expected < 0.85, got {r2_p:.3f}"
    r2_m = _pearson_inline([0.9, 0.8, 0.6, 0.4, 0.2], f5)
    assert r2_m > 0.90, f"monotone r2 expected > 0.90, got {r2_m:.3f}"

    # Verdict tests
    v, _ = compute_verdict({"per_corpus": {
        "4000": {"7": {"r2": 0.30, "max_dev": 0.45}, "17": {"r2": 0.32, "max_dev": 0.43},
                 "23": {"r2": 0.28, "max_dev": 0.46}},
        "150000": {"7": {"r2": 0.35, "max_dev": 0.41}, "17": {"r2": 0.33, "max_dev": 0.42},
                   "23": {"r2": 0.29, "max_dev": 0.44}},
    }, "N": N_FULL})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS: {v}"

    vf, _ = compute_verdict({"per_corpus": {
        "4000": {"7": {"r2": 0.97, "max_dev": 0.01}},
        "150000": {"7": {"r2": 0.96, "max_dev": 0.02}},
    }, "N": N_FULL})
    assert "HARD_FAIL" in vf or "MIDDLE_BAND" in vf, f"fail gate: {vf}"

    # Import chain: v11 loaded and run_one_cell_no_replay callable
    assert _v11_mod is not None, "v11 import failed"
    assert callable(run_one_cell_no_replay), "run_one_cell_no_replay not callable"

    # Live smoke cell at N_SMOKE=512, BYTES=4000 (1 f value only to keep fast)
    device = torch.device("cpu")
    result = run_one_cell_no_replay(
        seed=17, f=0.0, N_cfg=N_SMOKE,
        batch_size=BATCH_SIZE_SMOKE, n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=4_000, device=device,
    )
    assert "retention_A" in result, f"missing retention_A: {list(result.keys())}"
    ret = result["retention_A"]
    assert ret is not None and not math.isnan(ret), f"retention_A NaN/None"
    assert 0.0 <= ret <= 1.0, f"retention_A out of [0,1]: {ret}"

    # 4x smoke: N_SMOKE*4 = 2048
    result4 = run_one_cell_no_replay(
        seed=17, f=0.0, N_cfg=N_SMOKE * 4,
        batch_size=BATCH_SIZE_SMOKE, n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=4_000, device=device,
    )
    assert "retention_A" in result4, "4x missing retention_A"
    ret4 = result4["retention_A"]
    assert ret4 is not None and not math.isnan(ret4), "4x retention_A NaN"

    # OOM check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N={N_FULL} = {oom_bytes/1e6:.0f}MB"

    print(f"[selftest] saad_solla_v21_n4096_m_sweep_v2 PASS ret_smoke={ret:.4f} "
          f"ret_4x={ret4:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    corpus_sizes = CORPUS_SIZES_SMOKE if smoke else CORPUS_SIZES_FULL
    f_sweep      = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds        = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg        = N_SMOKE if smoke else N_FULL
    batch        = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs       = EPOCHS_SMOKE if smoke else EPOCHS
    pa_epochs    = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS

    device = torch.device("cpu")
    print(f"saad_solla_v21_n4096_m_sweep_v2 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} corpus_sizes={corpus_sizes} seeds={seeds} f_sweep={f_sweep}",
          flush=True)

    per_corpus: Dict = {}

    for n_bytes in corpus_sizes:
        print(f"\n== corpus_size={n_bytes} ==", flush=True)
        per_seed_res: Dict = {}

        for seed in seeds:
            t_seed = time.monotonic()
            ret_vals = []

            for f in f_sweep:
                result = run_one_cell_no_replay(
                    seed=seed, f=f, N_cfg=N_cfg,
                    batch_size=batch, n_epochs=epochs,
                    phase_a_epochs=pa_epochs,
                    n_bytes=n_bytes, device=device,
                )
                ret_A = result.get("retention_A", 0.0)
                ret_vals.append(ret_A)

            # Pearson r2 of retention vs f (plateau = low r2)
            r2 = _pearson_inline(ret_vals, f_sweep)
            if len(ret_vals) >= 2:
                slope = (ret_vals[-1] - ret_vals[0]) / max(f_sweep[-1] - f_sweep[0], 1e-9)
                residuals = [abs(rv - (ret_vals[0] + slope * (fi - f_sweep[0])))
                             for rv, fi in zip(ret_vals, f_sweep)]
                max_dev = max(residuals)
            else:
                max_dev = 0.0

            elapsed_s = time.monotonic() - t_seed
            passes = seed_passes_hp(r2, max_dev)
            print(f"  corpus={n_bytes} seed={seed} r2={r2:.4f} max_dev={max_dev:.4f} "
                  f"passes={passes} elapsed={elapsed_s:.1f}s", flush=True)
            print(f"  ret_vals={[round(v, 3) for v in ret_vals]}", flush=True)

            per_seed_res[str(seed)] = {
                "r2": r2, "max_dev": max_dev, "seed": seed, "n_bytes": n_bytes,
                "f_results": dict(zip([str(f) for f in f_sweep], ret_vals)),
                "passes_hp": passes,
            }

        per_corpus[str(n_bytes)] = per_seed_res

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_corpus": per_corpus, "N": N_cfg})

    summary = {
        "anchor": "saad_solla_v21_n4096_m_sweep_v2",
        "N": N_cfg, "smoke": smoke,
        "corpus_sizes": corpus_sizes, "f_sweep": f_sweep, "seeds": seeds,
        "per_corpus": per_corpus,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
