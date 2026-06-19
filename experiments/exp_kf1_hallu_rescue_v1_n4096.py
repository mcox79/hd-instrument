"""KF1 hallucination-detection rescue v1: entropy-based OOS discrimination.

CONTEXT:
  c1_kf_battery_phase_v1_n4096 (v267 C1_MIDDLE_BAND): KF1 margin-based mechanism FAILS
  at ALL M values including in-capacity M=20K. Mean_oos_max_conf was high (not 0.03 as
  expected) across all M, indicating OOS queries returned HIGH softmax confidence.

  ROOT CAUSE HYPOTHESIS: the margin-based mechanism (1 - max_oos_conf) used softmax over
  the full codebook at M=20K. When M=20K >> C_effective at N=4096 (C~49K but M uses
  M > C_eff_usable at high M), softmax saturates = all queries return high confidence.
  The KF1 claim "OOS queries return low confidence" was tied to an undercap assumption
  that does NOT hold at M=20K with Kerdock codebook geometry.

  RESCUE ARM 1 (CHEAPEST per [[feedback-rehabilitation-after-rejection]]):
  Use ENTROPY-based discrimination instead of max_confidence.
  Entropy H(softmax(logits)) is HIGH for OOS queries (soft over many codewords)
  and LOW for in-distribution queries (concentrates on correct codeword).
  This is the posterior-entropy-based mechanism noted in v267 routing.

SCIENTIFIC QUESTION:
  Does entropy-based discrimination distinguish in-store (IS) queries from OOS queries
  at N=4096, M=20K (in-capacity)?
  H(IS) << H(OOS) = "hallucination detection via entropy" = KF1 rescue.

PRE-REGISTERED BANDS (new mechanism; calibration probe; first entropy-based KF1 test):
  No prior anchor for entropy-based KF1. Calibration-probe policy: bands +/-50%.

  HARD_PASS: mean H(OOS) - mean H(IS) >= 1.0 bit (at least 1-bit entropy gap between
    OOS and IS queries) at >= 2/3 seeds at M=20K.
    Interpretation: entropy gap is detectable and large enough to use as a threshold.
  HARD_FAIL: entropy gap < 0.1 bit OR H(IS) >= H(OOS) (no discrimination).
    Interpretation: entropy cannot rescue KF1 at this operating point.
  MIDDLE_BAND: gap >= 0.1 but < 1.0 bit (partial discrimination, needs further work).

FORMULA SELF-TESTS:
  1. H(uniform over C=49152) = log2(49152) ~ 15.6 bits (max entropy = OOS upper bound).
  2. H(delta at 1 item) = 0 bits (min entropy = IS lower bound ideally).
  3. Expected at M=20K undercap: H(IS) ~ 0.5-2 bits, H(OOS) ~ 8-15 bits.
  4. entropy_gap = mean_H_oos - mean_H_is. HARD_PASS gate: entropy_gap >= 1.0 bit.
  5. N == 4096 (PROT-018 binding).

OOM CHECK:
  Softmax over C=49152 at N=4096, M=20K: codebook (49152*4096*4 = 768MB).
  Query batch: N_PROBE=200 queries x N=4096 = 3MB. Total << 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell: store M=20K + evaluate N_PROBE=200 OOS + 200 IS queries.
  Store M=20K at N=4096 in batches: ~0.5s per seed.
  Eval 400 queries x softmax(49152): ~0.5s.
  Per cell: ~1s. 2 M_vals x 3 seeds = 6 cells x 1s = 6s.
  FULL estimate: 6s. 1.5x = 9s. PROT-019 _n4096 floor: timeout >= 14400.
  timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf1_hallu_rescue_v1_n4096
Queue: overnight_queue (GPU; N=4096 entropy-based KF1 rescue, 2 M_vals x 3 seeds)
Pre-reg: preregs/2026-05-28_kf1_hallu_rescue_v1_n4096.md
Parent: c1_kf_battery_phase_v1_n4096 (v267 C1_MIDDLE_BAND KF1 failure -> rescue arm 1)
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load axis1_mb_chunk1 for store_facts_batched, Kerdock builder
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_kf1resc", _c1_path)
c1_mod = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1_mod)

store_facts_batched = c1_mod.store_facts_batched
v3 = c1_mod.v3   # Kerdock codebook builder

# Bit-precision helper (BE-1 plumbing; fp32 default = no-op = backwards compat).
sys.path.insert(0, str(REPO / "experiments"))
import _bit_precision as bp  # noqa: E402

# Process-global precision (set from CLI in run()).
_BIT_PRECISION = "fp32"

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M values: in-capacity baseline + near-boundary
M_VALS_FULL  = [20000, 45000]   # in-cap + near-boundary (same as c1 baseline)
M_VALS_SMOKE = [20000]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE_IS  = 200   # in-store probes
N_PROBE_OOS = 200   # out-of-store probes
BETA_OP     = 32.0  # standard operating beta

# Pre-registered thresholds
HP_ENTROPY_GAP_MIN = 1.0   # mean H(OOS) - mean H(IS) >= 1.0 bit
HF_ENTROPY_GAP_MAX = 0.1   # gap < 0.1 bit = no discrimination
HP_SEEDS_MIN       = 2     # >= 2/3 seeds


def get_output_dir(default_name: str = "kf1_hallu_rescue_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_entropy_bits(logits: torch.Tensor, beta: float) -> float:
    """Compute mean entropy H(softmax(beta*sims)) in bits over probe queries."""
    # logits: (C, n_probe)
    scaled = logits * beta
    log_z = torch.logsumexp(scaled, dim=0, keepdim=True)
    log_probs = scaled - log_z    # (C, n_probe)
    probs = log_probs.exp()       # (C, n_probe)
    # Entropy per probe: -sum(p * log2(p))
    H = -(probs * log_probs).sum(dim=0) / math.log(2)  # (n_probe,) in bits
    return float(H.mean().item())


def eval_entropy_gap(W: torch.Tensor, codebook: torch.Tensor,
                     key_idx: torch.Tensor, val_idx: torch.Tensor,
                     N: int, seed: int, device: torch.device) -> Dict:
    """Evaluate entropy gap between in-store (IS) and OOS queries."""
    C = codebook.shape[0]
    M = key_idx.shape[0]

    # --- IS queries: use stored keys ---
    n_is = min(N_PROBE_IS, M)
    is_key_idx = key_idx[:n_is] % C
    is_keys = codebook[is_key_idx]    # (n_is, N)
    is_q = is_keys @ W.T              # (n_is, N)
    is_sims = (codebook @ is_q.T) / N  # (C, n_is)
    H_is = compute_entropy_bits(is_sims, BETA_OP)

    # --- OOS queries: random noise vectors NOT from the codebook ---
    # Use random unit vectors (out-of-distribution = not any stored codebook vector).
    # This is more robust than trying to find "non-stored" codebook indices at high M.
    gen = torch.Generator(device=device).manual_seed(seed + 1000)
    # Random Gaussian vectors (OOS = not from codebook geometry)
    oos_vecs = torch.randn(N_PROBE_OOS, N, generator=gen, device=device)
    oos_vecs = oos_vecs / (oos_vecs.norm(dim=1, keepdim=True) + 1e-8) * (N ** 0.5)
    n_oos = N_PROBE_OOS

    oos_q = oos_vecs @ W.T              # (n_oos, N)
    oos_sims = (codebook @ oos_q.T) / N  # (C, n_oos)
    H_oos = compute_entropy_bits(oos_sims, BETA_OP)

    entropy_gap = H_oos - H_is
    return {
        "H_is": round(H_is, 4),
        "H_oos": round(H_oos, 4),
        "entropy_gap": round(entropy_gap, 4),
        "n_is": n_is,
        "n_oos": n_oos,
        "passes_hp": entropy_gap >= HP_ENTROPY_GAP_MIN,
        "passes_hf": entropy_gap < HF_ENTROPY_GAP_MAX,
    }


def run_one_cell(N: int, M: int, seed: int, device: torch.device) -> Dict:
    """Run entropy-gap KF1 rescue at one (N, M, seed)."""
    t0 = time.monotonic()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    W, keys, _vals, key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    # Precision intercept: quantize W after storage, before retrieval.
    # fp32 path is a true no-op (returns W unchanged) so backwards compat is exact.
    if _BIT_PRECISION != "fp32":
        W = bp.quantize_roundtrip(W, _BIT_PRECISION)

    gap_result = eval_entropy_gap(W, codebook, key_idx, val_idx, N, seed, device)

    del keys, _vals, key_idx, val_idx
    if device.type == "cuda":
        torch.cuda.empty_cache()

    elapsed = time.monotonic() - t0
    print(f"    [N={N} M={M} seed={seed}] C={C} H_is={gap_result['H_is']:.2f} "
          f"H_oos={gap_result['H_oos']:.2f} gap={gap_result['entropy_gap']:.2f} "
          f"({elapsed:.1f}s)", flush=True)

    return {
        "N": N, "M": M, "M_over_N": round(M / N, 3), "seed": seed, "C": C,
        "elapsed_s": round(elapsed, 2),
        **gap_result,
    }


def compute_verdict(all_cells: List[Dict]) -> Tuple[str, str]:
    if not all_cells:
        return ("KF1_RESCUE_INCONCLUSIVE", "No cells.")

    from collections import defaultdict
    by_M: Dict = defaultdict(list)
    for c in all_cells:
        by_M[c["M"]].append(c)

    m_sorted = sorted(by_M.keys())
    M_BASE = m_sorted[0]  # should be 20K

    base_cells = by_M[M_BASE]
    pass_seeds = sum(1 for c in base_cells if c["passes_hp"])
    fail_seeds = sum(1 for c in base_cells if c["passes_hf"])
    mean_gap = sum(c["entropy_gap"] for c in base_cells) / max(1, len(base_cells))
    mean_H_is = sum(c["H_is"] for c in base_cells) / max(1, len(base_cells))
    mean_H_oos = sum(c["H_oos"] for c in base_cells) / max(1, len(base_cells))

    detail = (f"M_BASE={M_BASE} pass_seeds={pass_seeds}/{len(base_cells)} "
              f"mean_entropy_gap={mean_gap:.3f}bits mean_H_is={mean_H_is:.2f} "
              f"mean_H_oos={mean_H_oos:.2f} HP_min={HP_ENTROPY_GAP_MIN}")

    if fail_seeds >= len(base_cells):
        return ("KF1_RESCUE_HARD_FAIL",
                f"ENTROPY_NO_DISCRIMINATION: gap < {HF_ENTROPY_GAP_MAX} bits. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("KF1_RESCUE_HARD_PASS",
                f"ENTROPY_DISCRIMINATION: gap={mean_gap:.2f} bits >= {HP_ENTROPY_GAP_MIN}. "
                + detail)

    return ("KF1_RESCUE_MIDDLE_BAND",
            f"PARTIAL_ENTROPY_GAP: gap={mean_gap:.2f} bits (below threshold). " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-test 1: entropy of uniform over C
    C_test = 1024
    uniform_logits = torch.zeros(C_test, 10)  # (C, n_probe)
    H_uniform = compute_entropy_bits(uniform_logits, 32.0)
    H_expected = math.log2(C_test)   # = 10 bits
    assert abs(H_uniform - H_expected) < 0.01, f"Uniform entropy: {H_uniform} vs {H_expected}"

    # Formula self-test 2: delta (concentrated) distribution
    delta_logits = torch.full((C_test, 1), -1000.0)
    delta_logits[0, 0] = 1000.0
    H_delta = compute_entropy_bits(delta_logits, 1.0)
    assert H_delta < 0.01, f"Delta entropy should be ~0: {H_delta}"

    # Formula self-test 3: gates
    assert HP_ENTROPY_GAP_MIN > HF_ENTROPY_GAP_MAX, "HP > HF gate ordering violated"

    # Verdict self-tests
    cells_pass = [{"M": 20000, "entropy_gap": 2.5, "H_is": 1.0, "H_oos": 3.5,
                   "passes_hp": True, "passes_hf": False, "M_over_N": 4.88, "seed": s}
                  for s in [7, 17, 23]]
    v, msg = compute_verdict(cells_pass)
    assert "HARD_PASS" in v, f"HARD_PASS verdict test failed: {v}"

    cells_fail = [{"M": 20000, "entropy_gap": 0.05, "H_is": 10.0, "H_oos": 10.05,
                   "passes_hp": False, "passes_hf": True, "M_over_N": 4.88, "seed": s}
                  for s in [7, 17, 23]]
    v2, _ = compute_verdict(cells_fail)
    assert "HARD_FAIL" in v2, f"HARD_FAIL verdict test failed: {v2}"

    # Smoke forward pass at N_SMOKE (use smaller M to avoid M >> C scenario at N_SMOKE)
    device = torch.device("cpu")
    # At N_SMOKE=1024, C=4096 (Kerdock). Use M=2000 < C to get meaningful results.
    M_smoke_test = 2000
    cell = run_one_cell(N_SMOKE, M_smoke_test, 17, device)
    assert "entropy_gap" in cell, f"entropy_gap missing: {list(cell.keys())}"
    assert not math.isnan(cell["entropy_gap"]), f"entropy_gap NaN: {cell}"
    assert cell["H_is"] >= 0, f"H_is negative: {cell['H_is']}"
    assert cell["H_oos"] >= 0, f"H_oos negative: {cell['H_oos']}"
    assert cell["n_is"] > 0, f"n_is zero"
    assert cell["n_oos"] > 0, f"n_oos zero"

    # Multi-scale smoke N_SMOKE x4
    cell_4x = run_one_cell(N_SMOKE * 4, M_VALS_SMOKE[0], 17, device)
    assert "entropy_gap" in cell_4x, f"4x smoke missing entropy_gap"

    print(f"[selftest] kf1_hallu_rescue_v1_n4096 PASS "
          f"entropy_gap_smoke={cell['entropy_gap']:.3f}bits "
          f"H_is={cell['H_is']:.2f} H_oos={cell['H_oos']:.2f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False, precision: str = "fp32") -> None:
    global _BIT_PRECISION
    _BIT_PRECISION = precision
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    N      = N_SMOKE if smoke else N_FULL
    m_vals = M_VALS_SMOKE if smoke else M_VALS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "kf1_hallu_rescue_v1_n4096")
    print(f"[run] {exp_name} smoke={smoke} N={N} m_vals={m_vals} "
          f"seeds={seeds} device={device} precision={precision}", flush=True)
    if not smoke:
        assert N == 4096, f"FULL run must use N=4096 (PROT-018); got {N}"

    all_cells: List[Dict] = []
    for M in m_vals:
        print(f"\n  [M={M} M/N={M/N:.2f}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N, M, seed, device)
            all_cells.append(cell)

    verdict_str, verdict_msg = compute_verdict(all_cells)
    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    precision_md = bp.precision_metadata(N * N, precision)

    out_dir = get_output_dir(exp_name)
    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds, "m_vals": m_vals,
                   "beta_op": BETA_OP, "HP_ENTROPY_GAP_MIN": HP_ENTROPY_GAP_MIN,
                   "bit_precision": precision},
        "all_cells": all_cells,
        **precision_md,
    }
    out_path = out_dir / "metrics.json"
    tmp_path = out_path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, out_path)
    print(f"[output] {out_path}", flush=True)
    print(f"[precision] {precision} W_bytes={precision_md['precision_memory_bytes']} "
          f"baseline={precision_md['precision_baseline_bytes']} "
          f"ratio={precision_md['precision_compression_ratio']}x", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--bit-precision", dest="bit_precision", default="fp32",
                    choices=list(bp.VALID_PRECISIONS),
                    help="W-matrix precision for BE-1 sweep (default fp32 = no-op)")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke, precision=args.bit_precision)
else:
    run(smoke=False)
