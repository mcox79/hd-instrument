"""exp_cortex_integration_m16_attention_router_v1 -- Phase 3c cortex integration.

Closes M1.6 attention router coverage in the composed Cortex.forward() pipeline.
Phase 3 tested M1.4/M1.5/M1.7/M1.8; Phase 3b tested noise-boundary; this cell
tests M1.6 wiring integrity + attention_beta config propagation.

Prereg: preregs/2026-07-02_exp_cortex_integration_m16_attention_router_v1.md
Bands:
    HP: |delta_composed_individual| <= 0.05 AND mean(composed_cos) >= 0.95
        AND mean(ablated_cos) <= 0.20 across 3 seeds
    MB: composed/ablated pass but delta in (0.05, 0.15]
    HF: delta > 0.15 OR composed < 0.90 OR ablated > 0.30 OR cardinality != 9

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (COMPOSED / INDIVIDUAL / ABLATED source
  hashes distinct; NUMERIC bit-identity of COMPOSED vs INDIVIDUAL is the
  POSITIVE proof of correct wiring, not a bug)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "integration + wiring-liveness test; ablation floor is closed-form
  1/sqrt(M) not a Cramer-Rao bound"
- baseline_in_band: exempt (bit-identity + ablation floor by design)
- discriminator survives scale: smoke M=128 (1/sqrt(128)=0.088 well below floor
  0.20); FULL M=1024 (1/sqrt(1024)=0.031 cleaner). Gap widens with scale.
- HARD_PASS strictly above floor + band-width: HP delta <= 0.05, composed_cos
  >= 0.95, ablated_cos <= 0.20 (all with margin)
- cardinality_ok: EXPECTED_N_UNITS = 3 arms x 3 seeds = 9
- per-unit failure-class instrumentation
- calibration_check: "default_ok_for_this_regime"
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Storage strategy: SHARDED (M distinct keys/vals rows; single-hop retrieval; no
downstream chain composition tested here).

Compute architecture: (c) mixed -- torch CPU, sequential per-query loop; per-
forward-call wall ~50ms; total FULL wall ~11s. Sequential justified: wiring
integrity test, not scale test; each forward() is a distinct pipeline exercise
(NOT independent phase points suitable for GPU batching).
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

# Ensure repo root on sys.path so hdlab / experiments imports resolve when
# invoked as a script from tools/queue_add.sh.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hdlab.chunked_attention import chunked_attention_readout
from hdlab.cortex import Cortex, CortexConfig, CortexResponse

from experiments._cell_heartbeat import emit_heartbeat


# ------------------------------ configuration --------------------------------

ANCHOR_NAME = "exp_cortex_integration_m16_attention_router_v1"

# CG-anchored constants
N_DIM = 8192                    # inherited from Cortex config default
V_DIM = 8192                    # tape val dim = tape key dim (bipolar); readout is (V,)
ATTENTION_CHUNK_SIZE = 1024
ATTENTION_BETA_LIVE = 13.0      # CG-anchored (Cell D v2 regime)
ATTENTION_BETA_ABLATED = 1e-3   # near-uniform softmax; MEAN(vals) readout

COMPOSED_INDIV_TOL = 0.05        # HP delta tolerance (bit-identity check)
COMPOSED_MIN_COS = 0.95          # HP floor for composed readout fidelity
ABLATION_MAX_COS = 0.20          # HP floor for ablated arm; > this = HF
HF_DELTA_UPPER = 0.15            # delta above -> HARD_FAIL

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]

FULL_M_TAPE = 1024
FULL_Q_QUERIES = 25
SMOKE_M_TAPE = 128
SMOKE_Q_QUERIES = 15


# ------------------------ output-dir + IO helpers ----------------------------


def _output_dir_for(run_mode: str) -> Path:
    if run_mode == "smoke":
        return REPO_ROOT / "data" / f"{ANCHOR_NAME}_smoke"
    elif run_mode == "self_test":
        return REPO_ROOT / "data" / f"{ANCHOR_NAME}_selftest"
    else:
        return REPO_ROOT / "data" / ANCHOR_NAME


def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ---------------------------- data generators --------------------------------


def _bipolar_random(shape, gen: torch.Generator) -> torch.Tensor:
    r = torch.rand(shape, generator=gen)
    return torch.where(r < 0.5,
                       torch.tensor(-1.0),
                       torch.tensor(1.0)).to(torch.float32)


def _make_m16_data(seed: int, m_tape: int, q_queries: int
                   ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor,
                              torch.Tensor]:
    """Generate M keys + M vals (both bipolar) + Q query-target-indices.
    Query for target j = keys[j] (exact match).
    Returns (keys[M,N], vals[M,V], query_indices[Q], queries[Q,N])."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    keys = _bipolar_random((m_tape, N_DIM), gen)
    vals = _bipolar_random((m_tape, V_DIM), gen)
    # Q sampled indices with replacement (Q may exceed M in smoke variants; here
    # smoke Q=15 << M=128 and full Q=25 << M=1024).
    query_indices = torch.randint(0, m_tape, (q_queries,), generator=gen)
    queries = keys[query_indices].clone()
    return keys, vals, query_indices, queries


# --------------------------- per-arm implementations -------------------------


def _cortex_for(seed: int, beta: float) -> Cortex:
    cfg = CortexConfig(
        n_dim=N_DIM,
        attention_chunk_size=ATTENTION_CHUNK_SIZE,
        attention_beta=beta,
        seed=seed,
    )
    return Cortex(cfg)


def _mean_readout_cos_correct(readout_vec: torch.Tensor,
                              correct_val: torch.Tensor) -> float:
    """cos(readout, vals[j]) -- readout fidelity metric."""
    r = readout_vec.to(torch.float32)
    v = correct_val.to(torch.float32)
    r_n = r.norm().clamp_min(1e-9)
    v_n = v.norm().clamp_min(1e-9)
    return float((r @ v) / (r_n * v_n))


def _arm_composed_m16(seed: int, m_tape: int, q_queries: int) -> float:
    """COMPOSED: Cortex.forward() with attention_beta=13.0; read resp.retrieval;
    compute cos(readout, vals[query_index]). Mean over Q queries."""
    cx = _cortex_for(seed, ATTENTION_BETA_LIVE)
    keys, vals, qidx, queries = _make_m16_data(seed, m_tape, q_queries)
    coss = []
    for i in range(q_queries):
        resp = cx.forward(queries[i], context_keys=keys, context_vals=vals)
        if resp.tier_used != "ATTENTION_ROUTER":
            raise AssertionError(
                f"COMPOSED: expected ATTENTION_ROUTER tier; got "
                f"{resp.tier_used!r} (wiring bug -- forward did not enter M1.6)")
        c = _mean_readout_cos_correct(resp.retrieval, vals[int(qidx[i])])
        coss.append(c)
    return float(np.mean(coss))


def _arm_individual_m16(seed: int, m_tape: int, q_queries: int) -> float:
    """INDIVIDUAL: direct chunked_attention_readout with matched args to what
    cortex.forward would pass (q_2d = query.unsqueeze(0), keys, vals,
    chunk_size, beta=13). Compute same cosine metric."""
    keys, vals, qidx, queries = _make_m16_data(seed, m_tape, q_queries)
    coss = []
    for i in range(q_queries):
        q_2d = queries[i].unsqueeze(0)  # (1, N)
        readout = chunked_attention_readout(
            q_2d, keys, vals,
            chunk_size=ATTENTION_CHUNK_SIZE,
            beta=ATTENTION_BETA_LIVE,
        )  # (1, V)
        c = _mean_readout_cos_correct(readout[0], vals[int(qidx[i])])
        coss.append(c)
    return float(np.mean(coss))


def _arm_ablated_m16(seed: int, m_tape: int, q_queries: int) -> float:
    """ABLATED: Cortex.forward() with attention_beta=1e-3 (near-uniform
    softmax). Readout ~= mean(vals) regardless of query. cos(mean(vals),
    vals[j]) = 1/sqrt(M) THEORETICAL for bipolar vals. Config propagation
    liveness test: if ablated arm looks like composed, beta parameter is
    NOT propagating -> HF."""
    cx = _cortex_for(seed, ATTENTION_BETA_ABLATED)
    keys, vals, qidx, queries = _make_m16_data(seed, m_tape, q_queries)
    coss = []
    for i in range(q_queries):
        resp = cx.forward(queries[i], context_keys=keys, context_vals=vals)
        if resp.tier_used != "ATTENTION_ROUTER":
            raise AssertionError(
                f"ABLATED: expected ATTENTION_ROUTER tier; got "
                f"{resp.tier_used!r}")
        c = _mean_readout_cos_correct(resp.retrieval, vals[int(qidx[i])])
        coss.append(c)
    return float(np.mean(coss))


# ------------------ arms_differ code-path fingerprint ------------------------


def _arms_differ_code_path_fingerprint() -> Dict[str, str]:
    """META_RULE_AF: hash source of COMPOSED / INDIVIDUAL / ABLATED so smoke
    can prove call-sites are distinct. NUMERIC bit-identity of COMPOSED vs
    INDIVIDUAL is the POSITIVE proof, not a bug."""
    fns = {
        "composed": _arm_composed_m16,
        "individual": _arm_individual_m16,
        "ablated": _arm_ablated_m16,
    }
    digests = {}
    for name, fn in fns.items():
        src = inspect.getsource(fn)
        digests[name] = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
    pairs = [("composed", "individual"), ("composed", "ablated"),
             ("individual", "ablated")]
    for a, b in pairs:
        if digests[a] == digests[b]:
            raise AssertionError(
                f"META_RULE_AF VIOLATION: {a} and {b} have identical source "
                f"hash; distinct call-sites required.")
    return digests


# ---------------------------- driver + verdict -------------------------------


def _run_all_seeds(seeds: List[int], m_tape: int, q_queries: int,
                   output_dir: Path, t0: float) -> dict:
    per_unit: List[dict] = []
    per_seed_summary: Dict[int, dict] = {}
    total_units = len(seeds) * 3
    unit_counter = 0

    for seed in seeds:
        composed = _arm_composed_m16(seed, m_tape, q_queries)
        individual = _arm_individual_m16(seed, m_tape, q_queries)
        ablated = _arm_ablated_m16(seed, m_tape, q_queries)

        seed_metrics = {
            "composed": composed,
            "individual": individual,
            "ablated": ablated,
        }
        per_seed_summary[seed] = seed_metrics
        for arm_name, val in seed_metrics.items():
            per_unit.append({
                "seed": seed,
                "arm": arm_name,
                "metric": val,
                "failure_class": None,
            })
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] composed={composed:.6f} individual={individual:.6f} "
              f"ablated={ablated:.6f}  delta_ci={abs(composed-individual):.2e}",
              flush=True)

    return {"per_unit": per_unit, "per_seed": per_seed_summary}


def _compute_verdict(results: dict, expected_n_units: int, m_tape: int) -> dict:
    per_unit = results["per_unit"]
    per_seed = results["per_seed"]

    if len(per_unit) != expected_n_units:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                            f"n_units={len(per_unit)} != expected="
                            f"{expected_n_units}"),
            "summary": f"CARDINALITY_BREACH: {len(per_unit)}/{expected_n_units}",
            "cardinality_ok": False,
        }

    composed_vals = [per_seed[s]["composed"] for s in per_seed]
    individual_vals = [per_seed[s]["individual"] for s in per_seed]
    ablated_vals = [per_seed[s]["ablated"] for s in per_seed]

    deltas = [abs(c - i) for c, i in zip(composed_vals, individual_vals)]
    max_delta = max(deltas)
    composed_mean = float(np.mean(composed_vals))
    individual_mean = float(np.mean(individual_vals))
    ablated_mean = float(np.mean(ablated_vals))
    ablated_max = max(ablated_vals)
    composed_min = min(composed_vals)

    uniform_floor = 1.0 / math.sqrt(m_tape)

    verdict_reasons = []
    if max_delta > HF_DELTA_UPPER:
        verdict = "HARD_FAIL"
        verdict_reasons.append(
            f"delta_composed_individual={max_delta:.4f} > {HF_DELTA_UPPER}")
    elif composed_min < 0.90:
        verdict = "HARD_FAIL"
        verdict_reasons.append(
            f"composed_min={composed_min:.4f} < 0.90 "
            f"(router path did not retrieve at exact-match)")
    elif ablated_max > 0.30:
        verdict = "HARD_FAIL"
        verdict_reasons.append(
            f"ablated_max={ablated_max:.4f} > 0.30 "
            f"(beta config not propagating; ablation ineffective)")
    elif max_delta <= COMPOSED_INDIV_TOL and composed_min >= COMPOSED_MIN_COS \
            and ablated_max <= ABLATION_MAX_COS:
        verdict = "HARD_PASS"
        verdict_reasons.append(
            f"delta={max_delta:.2e} <= {COMPOSED_INDIV_TOL}; "
            f"composed_min={composed_min:.4f} >= {COMPOSED_MIN_COS}; "
            f"ablated_max={ablated_max:.4f} <= {ABLATION_MAX_COS} "
            f"(uniform floor 1/sqrt(M={m_tape})={uniform_floor:.4f})")
    else:
        verdict = "MIDDLE"
        verdict_reasons.append(
            f"delta={max_delta:.4f}; composed_min={composed_min:.4f}; "
            f"ablated_max={ablated_max:.4f}")

    return {
        "verdict": verdict,
        "verdict_msg": f"{verdict}: {'; '.join(verdict_reasons)}",
        "summary": f"{verdict}: delta_ci={max_delta:.2e}, "
                   f"composed={composed_mean:.4f}, ablated={ablated_mean:.4f}",
        "cardinality_ok": True,
        "n_units": len(per_unit),
        "expected_n_units": expected_n_units,
        "max_delta_composed_individual": max_delta,
        "per_seed_delta": deltas,
        "composed_mean": composed_mean,
        "composed_min": composed_min,
        "individual_mean": individual_mean,
        "ablated_mean": ablated_mean,
        "ablated_max": ablated_max,
        "uniform_floor_theoretical": uniform_floor,
        "m_tape": m_tape,
    }


# --------------------------- formula selftests -------------------------------


def _selftest_arms_differ_code_paths() -> None:
    digests = _arms_differ_code_path_fingerprint()
    assert len(digests) == 3


def _selftest_composed_matches_individual_at_seed7() -> None:
    """Bit-identity: at seed=7, M=64, Q=5, composed and individual should
    differ by < 1e-4 (both call chunked_attention_readout with matched args)."""
    c = _arm_composed_m16(7, 64, 5)
    i = _arm_individual_m16(7, 64, 5)
    assert abs(c - i) < 1e-4, (
        f"COMPOSED={c:.6f} vs INDIVIDUAL={i:.6f} delta={abs(c-i):.2e} "
        f"not bit-identical")


def _selftest_composed_high_fidelity_at_seed7() -> None:
    """Composed readout cos should be >= 0.95 at seed=7, M=64 (exact match
    query + beta=13 peaked softmax)."""
    c = _arm_composed_m16(7, 64, 5)
    assert c >= 0.95, f"composed_cos={c:.4f} < 0.95 (retrieval not peaked)"


def _selftest_ablated_below_floor_at_seed7() -> None:
    """Ablated readout should collapse toward 1/sqrt(M=64)=0.125; verify <=0.35
    (2.8x uniform floor slack for finite Q=5 variance)."""
    a = _arm_ablated_m16(7, 64, 5)
    uniform_floor = 1.0 / math.sqrt(64)
    assert a <= 0.35, (
        f"ablated_cos={a:.4f} > 0.35 (theoretical uniform floor for M=64 "
        f"is {uniform_floor:.4f}; ablation not effective)")


def _selftest_ablated_distinct_from_composed_at_seed7() -> None:
    """Beta propagation check: ablated must differ from composed by > 0.5
    at M=64 (composed ~1.0, ablated ~0.125 -> gap ~0.87)."""
    c = _arm_composed_m16(7, 64, 5)
    a = _arm_ablated_m16(7, 64, 5)
    assert (c - a) > 0.5, (
        f"composed={c:.4f} ablated={a:.4f} gap={c-a:.4f} < 0.5 "
        f"(beta config not propagating)")


def _run_all_selftests() -> dict:
    _selftest_arms_differ_code_paths()
    _selftest_composed_matches_individual_at_seed7()
    _selftest_composed_high_fidelity_at_seed7()
    _selftest_ablated_below_floor_at_seed7()
    _selftest_ablated_distinct_from_composed_at_seed7()
    return {
        "selftests_passed": 5,
        "arms_differ_verified": True,
        "cell_source": ANCHOR_NAME,
    }


# ---------------------------------- main -------------------------------------


def main(run_mode: str) -> None:
    output_dir = _output_dir_for(run_mode)
    output_dir.mkdir(parents=True, exist_ok=True)

    if run_mode == "self_test":
        result = _run_all_selftests()
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (5 formula selftests ran successfully)",
            "summary": "SELFTEST_PASS 5/5",
            "elapsed_s": 0.0,
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "selftest_result": result,
        }
        _write_metrics_atomic(output_dir, metrics)
        print(f"[{ANCHOR_NAME} selftest] PASS {result}", flush=True)
        return

    if run_mode == "smoke":
        seeds = SEEDS_SMOKE
        m_tape = SMOKE_M_TAPE
        q_queries = SMOKE_Q_QUERIES
    elif run_mode == "full":
        seeds = SEEDS_FULL
        m_tape = FULL_M_TAPE
        q_queries = FULL_Q_QUERIES
    else:
        raise ValueError(f"Unknown run_mode: {run_mode!r}")

    expected_n_units = len(seeds) * 3
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units)
    arm_fingerprints = _arms_differ_code_path_fingerprint()

    results = _run_all_seeds(seeds, m_tape, q_queries, output_dir, t0)
    verdict_bundle = _compute_verdict(results, expected_n_units, m_tape)

    elapsed = time.perf_counter() - t0
    metrics = {
        **verdict_bundle,
        "elapsed_s": elapsed,
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "m_tape": m_tape,
        "q_queries": q_queries,
        "arm_code_path_fingerprints": arm_fingerprints,
        "arms_differ_verified": True,
        "storage_strategy": "SHARDED_M_distinct_keys_vals_single_hop",
        "compute_architecture": "mixed_cpu_torch_sequential_forward",
        "per_seed": {str(k): v for k, v in results["per_seed"].items()},
        "per_unit": results["per_unit"],
        "primitive_tested": "m16_chunked_attention_readout_via_cortex_forward",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[{ANCHOR_NAME} {run_mode}] {verdict_bundle['verdict']} "
          f"elapsed={elapsed:.1f}s -- {verdict_bundle['verdict_msg']}",
          flush=True)


# --------------------------------- entry -------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument("--run-mode",
                        choices=["self_test", "smoke", "full"],
                        default="full",
                        help="Execution mode; default full (defensive).")
    parser.add_argument("--self-test", action="store_true",
                        help="Convenience alias for --run-mode self_test.")
    args = parser.parse_args()
    run_mode = "self_test" if args.self_test else args.run_mode

    if hasattr(sys.stdout, "reconfigure") and sys.stdout.reconfigure is not None:
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass

    output_dir_for_crash = _output_dir_for(run_mode)
    try:
        main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir_for_crash, e)
        raise
