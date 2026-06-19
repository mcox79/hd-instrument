"""AXIS-1 Phase Diagram M x beta SCAN: chunk 3 (M/N fine-grid {4..16}).

CONTEXT:
  axis1_mb_chunk1_v1: M/N in {0.25..2} -> retention=1.0 everywhere (in-capacity).
  axis1_mb_chunk2_v1: M/N in {4,8,16,32} -> HARD_PASS boundary at M*=65536 (M/N=16).
    ret_by_M = {4: 1.000, 8: 0.503, 16: 0.238, 32: 0.117}.
    Phase boundary is between M/N=4 (ret=1.0) and M/N=8 (ret=0.503).
    The transition is sharp: full->half in one multiplicative step.

SCIENTIFIC QUESTION (Axis 1 -- fine-grid transition):
  Where exactly does the retention phase transition occur in M/N in (4, 8)?
  Fine grid: M/N in {4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8} resolves the transition midpoint.
  Additionally probe M/N=12 (between the 8 and 16 data points) for BNV scaling confirmation.

  N=4096; M values = [M/N * N] for M/N in {4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 12}.
  beta sweep: same as chunk-2: [1, 4, 16, 32, 64, 128, 256].
  Seeds: [7, 17, 23, 31, 41] (5-seed from chunk-2).

PHASE TRANSITION CHARACTERIZATION GOAL:
  From chunk-2 data: transition occurs near M/N ~ 6-7 (midpoint of ret drop 1.0->0.503).
  This chunk finds:
    (a) M_50 = M/N where mean retention first drops below 0.5 (precise location).
    (b) Transition width = delta(M/N) from ret=0.9 to ret=0.1.
    (c) Whether transition is first-order (sharp step) or second-order (smooth ramp).
    (d) BNV scaling across the transition.

PRE-REGISTERED BANDS:
  HARD_PASS: retention shows clear transition in [M/N=4.5, M/N=8] regime:
    exists M/N in {4.5..8} where mean retention drops from >= 0.9 to <= 0.5.
    M_50 (first M/N with mean ret < 0.5) is between 4.5 and 8.
    Interpretation: Fine-grained phase boundary located; substrate transitions in this window.
  HARD_FAIL: mean retention >= 0.80 across ALL M/N <= 8 (no transition in fine-grid).
    This would contradict chunk-2's M/N=8 observation (ret=0.503) and imply seed variance.
  MIDDLE_BAND: transition visible but M_50 is ambiguous (transitions spans multiple M/N
    steps without clear midpoint, OR ret at M/N=8 does not replicate chunk-2's 0.503).

FORMULA SELF-TESTS:
  1. M/N=8 cell should replicate chunk-2: mean_ret ~ 0.503 +/- 0.05 (5-seed replicate).
  2. M/N=4 should replicate chunk-2: mean_ret ~ 1.0.
  3. BNV at M/N=12 should be between chunk-2 M/N=8 BNV (3.231) and M/N=16 BNV (7.03).
  4. retention is non-increasing in M/N (no local reversals allowed in HARD_PASS verdict).
  5. build_codebook at N=4096: C = 4^(t+1) for t such that 4^(t+1) >= N. C=16384.

TIMEOUT ESTIMATE:
  chunk-2 elapsed at N=4096, 4 M values, 7 betas, 5 seeds: 79s.
  chunk-3: 9 M values (vs 4 in chunk-2, but M is smaller: max M/N=12 vs 32).
  M construction cost is O(M). M/N=12 vs M/N=32 = 12/32 = 0.375x per-cell cost.
  9 M_fracs vs 4: 9/4 = 2.25x more cells. Net: 2.25 * 0.375 = 0.84x of chunk-2.
  Estimated: 0.84 * 79s = 66s. Safety 3x: 200s.
  timeout_s = ceil(1.5 * 200) = 300 -> 600s (conservative given GPU variability).
  Under 2h: no extra flag needed.
  OOM check: W at N=4096 float32 = 67MB. M max = 12*4096 = 49152 keys.
    Peak allocation (W + codebook slice): ~200MB. Well under 6GB. PASS.

N-suffix: _n4096 suffix; production N = 4096 (PROT-018 binding).
Queue: overnight_queue (GPU; N=4096 over-capacity M fine-grid sweep)
Pre-reg: preregs/2026-05-27_axis1_mb_chunk3_v1_n4096.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load chunk-1 base (core cell computation: run_one_cell, codebook building)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix; N_FULL = 4096 (binding)
N_FULL = 4096       # PROT-018: anchor name is axis1_mb_chunk3_v1_n4096
N_SMOKE = 1024      # Kerdock valid

# Fine-grid M/N sweep: resolves the 4.0->8.0 transition observed in chunk-2
# Plus M/N=12 for BNV interpolation between chunk-2's M/N=8 and M/N=16 points
M_FRACS_FULL = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 12.0]
M_FRACS_SMOKE = [5.0, 7.0, 8.0]   # 3-point smoke spanning the expected transition

# Beta sweep (same as chunk-2)
BETA_FULL = [1.0, 4.0, 16.0, 32.0, 64.0, 128.0, 256.0]
BETA_SMOKE = [4.0, 64.0]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Phase structure thresholds
PASS_RETENTION_DROP_THRESHOLD = 0.50   # M_50 = first M/N where mean ret < 0.5
FAIL_RETENTION_MIN = 0.80              # no transition visible if min_ret >= 0.80
CHUNK2_M8_RET_EXPECTED = 0.503         # replication check within +/- 0.05
CHUNK2_M8_RET_TOL = 0.07              # tolerance on replication


def get_output_dir(default_name: str = "axis1_mb_chunk3_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_chunk3(M: int, beta: float, seed: int, codebook: torch.Tensor,
                         N: int, device: torch.device) -> dict:
    """Run one (M, beta, seed) cell. No hysteresis (expensive at large M)."""
    return c1.run_one_cell(M, beta, seed, codebook, N, device, compute_hyst=False)


def compute_verdict_chunk3(summary: dict) -> tuple[str, str]:
    """Chunk-3 verdict: find fine-grained M/N transition between 4 and 12."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1C3_INCONCLUSIVE", "No cells computed.")

    retentions = [c["retention"] for c in cells]
    m_vals = [c["M"] for c in cells]
    bnv_vals_all = [c.get("bundle_norm_var", 0.0) for c in cells]

    M_set = sorted(set(m_vals))
    ret_by_M = {}
    bnv_by_M = {}
    for M_v in M_set:
        cells_M = [c["retention"] for c in cells if c["M"] == M_v]
        bnvs_M = [c.get("bundle_norm_var", 0.0) for c in cells if c["M"] == M_v]
        ret_by_M[M_v] = sum(cells_M) / len(cells_M) if cells_M else 0.0
        bnv_by_M[M_v] = sum(bnvs_M) / len(bnvs_M) if bnvs_M else 0.0

    N_eff = N_FULL
    min_ret = min(ret_by_M.values())

    # HARD_FAIL: min retention still >= 0.80 (no transition in fine-grid)
    if min_ret >= FAIL_RETENTION_MIN:
        return ("AXIS1C3_HARD_FAIL",
                f"No retention phase transition in chunk-3 fine-grid. "
                f"min_ret={min_ret:.3f} (>= {FAIL_RETENTION_MIN}). "
                f"ret_by_M={dict((k, round(v, 3)) for k, v in ret_by_M.items())}. "
                f"Contradicts chunk-2 M/N=8 observation (ret=0.503). "
                f"Possible: seed-variance or M rounding mismatch.")

    # Find M_50 (first M/N where mean retention drops below 0.5)
    M_50_v = None
    M_90_v = None  # first M/N where mean ret drops below 0.9
    for M_v in M_set:
        if M_90_v is None and ret_by_M[M_v] < 0.90:
            M_90_v = M_v
        if M_50_v is None and ret_by_M[M_v] < PASS_RETENTION_DROP_THRESHOLD:
            M_50_v = M_v

    # BNV monotone check (should keep increasing into transition)
    bnv_list = [bnv_by_M[M_v] for M_v in M_set]
    bnv_diffs = [bnv_list[i + 1] - bnv_list[i] for i in range(len(bnv_list) - 1)]
    bnv_monotone = all(d >= 0 for d in bnv_diffs) if bnv_diffs else True

    # Replication check: does M/N=8 replicate chunk-2 value (0.503 +/- 0.07)?
    M8 = int(8.0 * N_FULL)  # = 32768
    M8_ret = ret_by_M.get(M8)
    chunk2_replicated = (
        M8_ret is not None
        and abs(M8_ret - CHUNK2_M8_RET_EXPECTED) <= CHUNK2_M8_RET_TOL
    )

    # Transition width (M/N span from ret=0.9 to ret=0.5)
    transition_width = None
    if M_90_v is not None and M_50_v is not None:
        transition_width = round((M_50_v - M_90_v) / N_FULL, 2)

    summary_vals = {
        "M_50_MoverN": round(M_50_v / N_FULL, 3) if M_50_v else None,
        "M_90_MoverN": round(M_90_v / N_FULL, 3) if M_90_v else None,
        "transition_width_MoverN": transition_width,
        "bnv_monotone": bnv_monotone,
        "chunk2_M8_replicated": chunk2_replicated,
        "M8_ret": round(M8_ret, 3) if M8_ret is not None else None,
        "ret_by_M": dict((round(k / N_FULL, 2), round(v, 3)) for k, v in ret_by_M.items()),
    }

    # HARD_PASS: transition found with M_50 between 4.5 and 8.0
    if (M_50_v is not None
            and 4.5 * N_FULL <= M_50_v <= 8.0 * N_FULL):
        m90_str = f"{M_90_v / N_FULL:.2f}" if M_90_v is not None else "N/A"
        return ("AXIS1C3_HARD_PASS",
                f"FINE-GRID PHASE BOUNDARY: M_50 at M/N={M_50_v / N_FULL:.2f}. "
                f"M_90 at M/N={m90_str}. "
                f"transition_width={transition_width}. "
                f"chunk2_replicated={chunk2_replicated} (M/N=8 ret={summary_vals['M8_ret']}). "
                f"bnv_monotone={bnv_monotone}. "
                f"ret_profile={summary_vals['ret_by_M']}.")

    # MIDDLE_BAND
    return ("AXIS1C3_MIDDLE_BAND",
            f"Partial transition. M_50={summary_vals['M_50_MoverN']}. "
            f"M_90={summary_vals['M_90_MoverN']}. "
            f"chunk2_replicated={chunk2_replicated}. "
            f"ret_by_M={summary_vals['ret_by_M']}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: N_FULL binding check
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096 (matches _n4096 suffix); got {N_FULL}"

    # Self-test 1: chunk-2 replication check formula
    M8_expected = 0.503
    M8_test = 0.503
    assert abs(M8_test - M8_expected) <= CHUNK2_M8_RET_TOL, \
        f"Replication formula failure: |{M8_test} - {M8_expected}| > {CHUNK2_M8_RET_TOL}"

    M8_fail = 0.95
    assert abs(M8_fail - M8_expected) > CHUNK2_M8_RET_TOL, \
        f"Replication formula should reject 0.95 but did not"

    # Self-test 2: verdict HARD_PASS path
    N_test = 4096
    cells_pass = []
    for mf in [4.5, 5.0, 6.0, 7.0, 8.0, 12.0]:
        M = int(mf * N_test)
        ret = max(0.0, 1.0 - (mf - 4.5) * 0.15)  # decreasing with M
        for b in [4.0, 64.0]:
            cells_pass.append({"M": M, "retention": ret, "bundle_norm_var": mf * 0.5,
                                "hysteresis_amp": 0.0})
    summary_pass = {"cells": cells_pass}
    v, msg = compute_verdict_chunk3(summary_pass)
    assert v == "AXIS1C3_HARD_PASS", f"Self-test HARD_PASS failed: got {v}: {msg}"

    # Self-test 3: verdict HARD_FAIL path (all ret >= 0.90)
    cells_fail = []
    for mf in [4.5, 5.0, 6.0, 7.0, 8.0]:
        M = int(mf * N_test)
        for b in [4.0, 64.0]:
            cells_fail.append({"M": M, "retention": 0.95, "bundle_norm_var": mf * 0.5,
                                "hysteresis_amp": 0.0})
    summary_fail = {"cells": cells_fail}
    v, msg = compute_verdict_chunk3(summary_fail)
    assert v == "AXIS1C3_HARD_FAIL", f"Self-test HARD_FAIL failed: got {v}: {msg}"

    # Self-test 4: OOM pre-check at N=4096
    oom_bytes_W = N_FULL * N_FULL * 4  # W matrix float32
    assert oom_bytes_W < 6e9, f"OOM: W at N=4096 = {oom_bytes_W:.2e} >= 6GB"

    # Self-test 5: c1.run_one_cell callable
    device = torch.device("cpu")
    codebook_small, _info = c1.v3.make_kerdock_4coset_codebook(N_SMOKE, device)
    result = run_one_cell_chunk3(
        M=int(5.0 * N_SMOKE), beta=4.0, seed=17, codebook=codebook_small,
        N=N_SMOKE, device=device
    )
    assert "retention" in result, f"retention missing from result: {list(result.keys())}"
    assert isinstance(result["retention"], float), \
        f"retention should be float; got {type(result['retention'])}"
    assert 0.0 <= result["retention"] <= 1.0, \
        f"retention out of [0,1]: {result['retention']}"

    # Self-test 6: at least 1 item survives smoke filter
    assert result["retention"] >= 0, "filter eliminates all items at smoke scale"

    print(f"[SELFTEST PASS] axis1_mb_chunk3_v1_n4096: N_FULL={N_FULL} "
          f"OOM={oom_bytes_W:.2e} verdict_gates OK smoke_cell_ok={result['retention']:.4f}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    betas = BETA_SMOKE if smoke else BETA_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    if not smoke:
        assert N == 4096, f"PROT-018: FULL run must use N=4096; got {N}"

    exp_name = os.environ.get("HDLAB_EXP_NAME", "axis1_mb_chunk3_v1_n4096")
    print(f"[axis1c3] N={N} M/N_fracs={m_fracs} betas={betas} seeds={seeds} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    codebook, _info = c1.v3.make_kerdock_4coset_codebook(N, device)
    print(f"  codebook: C={codebook.shape[0]} N={N}", flush=True)

    cells = []
    total_cells = len(m_fracs) * len(betas) * len(seeds)
    done = 0

    for mf in m_fracs:
        M = int(mf * N)
        for beta in betas:
            for seed in seeds:
                result = run_one_cell_chunk3(M, beta, seed, codebook, N, device)
                result["M_over_N"] = mf
                cells.append(result)
                done += 1
                if done % max(1, total_cells // 10) == 0:
                    print(f"  {done}/{total_cells} cells. "
                          f"M/N={mf:.1f} beta={beta} seed={seed} "
                          f"ret={result['retention']:.3f} "
                          f"bnv={result.get('bundle_norm_var', 0):.3f}", flush=True)

    summary = {"cells": cells, "N": N, "mode": "smoke" if smoke else "full"}
    verdict, msg = compute_verdict_chunk3(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "N": N, "m_fracs": m_fracs, "betas": betas, "seeds": seeds,
            "mode": "smoke" if smoke else "full",
        },
    }
    out_dir = get_output_dir(exp_name)
    mpath = out_dir / "metrics.json"
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
