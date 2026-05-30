"""N-SCALING MODERN HOPFIELD RESCUE v3 -- DIAGNOSTIC at N=16384.

CONTEXT (F4 + F4-rescue follow-up):
  v1 ran 116s and produced "No completed seeds" (instrumentation failure).
  v2 ran 21s and also produced "No completed seeds" (still failing fast,
  before the first seed metric was written). Both crashes happened
  EARLY -- before any cell-write -- so we have zero diagnostic data.

  v3 is a DIAGNOSTIC anchor. The goal is NOT to measure max_M but to
  ROOT-CAUSE the v1+v2 crash. We build the substrate incrementally
  and emit a partial-result file at EVERY step, so even a partial
  failure leaves actionable data on disk.

  Stages (each writes its own partial_metrics_<stage>.json):
    Step 1 -- construct codebook + W at N=16384 (no facts stored).
              Log: codebook bytes, W bytes, RAM used, success bool.
    Step 2 -- store 1 fact at M=1 (single seed). Single key/val.
              Log: store-op success, RAM after, retrieved recall.
    Step 3 -- store M=N/4=4096 facts single seed. Full store-loop.
              Log: per-batch RAM if a batch fails; recall at M=N/4.
    Step 4 -- run 1 seed of reduced M-sweep [N/8, N/4, N/2, N].
              SKIP 2N (where v2 likely OOM'd / hung on the desktop).
              Log: recall per M, per-cell mem.

  Each step independently writes a partial; the FINAL verdict
  describes which step succeeded and where the failure was. Even
  HARD_FAIL with proper error reporting is the success outcome.

SCIENTIFIC QUESTION:
  At which step does the v1+v2 pipeline crash at N=16384, and is the
  root cause (a) substrate construction OOM, (b) store-op crash,
  (c) sweep-loop crash, or (d) something else?

PRE-REGISTERED BANDS:
  HARD_PASS: all 4 steps succeed AND max_M_at_95_recall identified.
  HARD_FAIL: any step crashes WITH explicit error info (note: this
    crash-with-info is the desired diagnostic outcome -- the test
    is meant to FIND the bug, not pass HP).
  MIDDLE_BAND: partial steps succeed; diagnostic value but not full
    result.

  NOTE: this is a DIAGNOSTIC anchor; HARD_FAIL with proper error
  reporting is also a "successful" outcome scientifically.

FORMULA SELF-TESTS:
  1. N == 16384 (PROT-018).
  2. Steps 1..4 exist as discrete functions.
  3. M sweep = [N/8, N/4, N/2, N] = [2048, 4096, 8192, 16384].
     SKIP 2N (in v2; where the OOM almost certainly hit).
  4. Each step writes its own partial_metrics_<stage>.json.

OOM CHECK (this is CPU queue, but same memory budget applies):
  N=16384 BSC codebook (49152 * 16384 floats float32) = 3.2GB.
  W = 16384 * 16384 * 4 = 1.07GB.
  M=N=16384: keys = 16384 * 16384 * 4 = 1.07GB.
  Peak (codebook + W + keys + W @ keys.T) ~6-7GB. Tight on 8GB-budget
  desktop. Diagnostic: explicit mem logging at each transition.

TIMEOUT ESTIMATE:
  Step 1 (no store): ~5s.
  Step 2 (1 fact):   ~5s.
  Step 3 (4096 facts): ~60-300s CPU.
  Step 4 (4 M-points * 1 seed): ~300-1800s CPU at N=16384.
  Total estimated wall: ~2000-4000s. Budget 14400s.

N-suffix: _n16384 -> production N = 16384 (PROT-018 binding).
Anchor: n_scaling_modern_hopfield_rescue_v3_n16384
Queue: remote_cpu_queue (CPU; diagnostic incremental construction)
Pre-reg: preregs/2026-05-30_n_scaling_modern_hopfield_rescue_v3_n16384.md
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
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Substrate primitives via t1_beta_sweep loader (same pattern as v1/v2)
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_nscale_rescue_v3", _t1_path)
t1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1)
store_facts_batched = t1.store_facts_batched
v3 = t1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_nscale_v3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n16384 binds N = 16384
N = 16384       # PROT-018 production-N anchor (queue_add.py regex hits this)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

SEED = 7          # single seed for diagnostic
SEED_SMOKE = 17
RECALL_THRESHOLD = 0.95
N_PROBE = 200

# M sweep at FULL: skip 2N (where v2 OOM'd). 4 M-points.
def _m_sweep_full(N_use: int) -> List[int]:
    return [N_use // 8, N_use // 4, N_use // 2, N_use]

M_SWEEP_FULL  = _m_sweep_full(N_FULL)       # [2048, 4096, 8192, 16384]
M_SWEEP_SMOKE = [N_SMOKE // 4, N_SMOKE]     # [256, 1024]


def get_output_dir(default_name: str = "n_scaling_modern_hopfield_rescue_v3_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _mem_stat_str(device: torch.device) -> str:
    """Memory usage string. CPU uses psutil-style RSS via os; falls back gracefully."""
    if device.type == 'cuda':
        try:
            alloc = torch.cuda.memory_allocated() / (1024**3)
            reserved = torch.cuda.memory_reserved() / (1024**3)
            return f"cuda_alloc={alloc:.2f}GB cuda_reserved={reserved:.2f}GB"
        except Exception as e:
            return f"cuda_mem_query_failed: {e}"
    # CPU: try psutil; fall back to "n/a"
    try:
        import psutil
        rss = psutil.Process().memory_info().rss / (1024**3)
        return f"cpu_rss={rss:.2f}GB"
    except Exception:
        return "cpu_rss=n/a"


def _safe_clear(device: torch.device) -> None:
    if device.type == 'cuda':
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


# ------ STEP 1: construct codebook + W (no facts stored) ------

def step1_construct(N_use: int, seed: int, device: torch.device) -> Dict:
    """Build codebook + zero W. Diagnose construction failure."""
    t0 = time.time()
    pre_mem = _mem_stat_str(device)
    try:
        codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
        cb_mem = _mem_stat_str(device)
        cb_bytes = codebook.element_size() * codebook.nelement()
        W = torch.zeros(N_use, N_use, dtype=torch.float32, device=device)
        W_mem = _mem_stat_str(device)
        W_bytes = W.element_size() * W.nelement()
        out = {
            "step": "step1_construct",
            "success": True,
            "codebook_shape": list(codebook.shape),
            "codebook_bytes": int(cb_bytes),
            "W_shape": list(W.shape),
            "W_bytes": int(W_bytes),
            "pre_mem": pre_mem,
            "cb_mem": cb_mem,
            "W_mem": W_mem,
            "elapsed_s": round(time.time() - t0, 2),
        }
        del codebook, W
        _safe_clear(device)
        return out
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        tb = traceback.format_exc(limit=12)
        return {
            "step": "step1_construct",
            "success": False,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": tb,
            "pre_mem": pre_mem,
            "fail_mem": _mem_stat_str(device),
            "elapsed_s": round(time.time() - t0, 2),
        }


# ------ STEP 2: store 1 fact (M=1) and check retrieval ------

def step2_one_fact(N_use: int, seed: int, device: torch.device) -> Dict:
    """Store 1 fact, retrieve, compute single-fact recall."""
    t0 = time.time()
    pre_mem = _mem_stat_str(device)
    try:
        codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
        W, keys, values, key_idx, val_idx = store_facts_batched(
            codebook, 1, seed, N_use, device)
        post_store_mem = _mem_stat_str(device)
        # Retrieve the single stored key
        r = keys[0:1] @ W.T   # (1, N)
        sims = (codebook @ r.T) / N_use  # (C, 1)
        pred = int(torch.argmax(sims, dim=0).item())
        target = int((val_idx[0] % codebook.shape[0]).item())
        recall = 1.0 if pred == target else 0.0
        out = {
            "step": "step2_one_fact",
            "success": True,
            "M": 1,
            "recall": recall,
            "pre_mem": pre_mem,
            "post_store_mem": post_store_mem,
            "elapsed_s": round(time.time() - t0, 2),
        }
        del W, keys, values, codebook, r, sims
        _safe_clear(device)
        return out
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        tb = traceback.format_exc(limit=12)
        return {
            "step": "step2_one_fact",
            "success": False,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": tb,
            "pre_mem": pre_mem,
            "fail_mem": _mem_stat_str(device),
            "elapsed_s": round(time.time() - t0, 2),
        }


# ------ STEP 3: store M=N/4 facts single seed ------

def step3_quarter_n(N_use: int, seed: int, device: torch.device) -> Dict:
    """Store M=N/4 facts and measure recall."""
    t0 = time.time()
    pre_mem = _mem_stat_str(device)
    M_target = N_use // 4
    try:
        codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
        W, keys, values, key_idx, val_idx = store_facts_batched(
            codebook, M_target, seed, N_use, device)
        post_store_mem = _mem_stat_str(device)
        n = min(N_PROBE, M_target)
        probe_keys = keys[:n]
        probe_val_idx = val_idx[:n] % codebook.shape[0]
        out_response = probe_keys @ W.T
        sims = (codebook @ out_response.T) / N_use
        pred = torch.argmax(sims, dim=0)
        recall = float((pred == probe_val_idx.to(device)).float().mean().item())
        out = {
            "step": "step3_quarter_n",
            "success": True,
            "M": M_target,
            "recall": round(recall, 5),
            "pre_mem": pre_mem,
            "post_store_mem": post_store_mem,
            "elapsed_s": round(time.time() - t0, 2),
        }
        del W, keys, values, codebook, out_response, sims, pred
        _safe_clear(device)
        return out
    except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
        tb = traceback.format_exc(limit=12)
        return {
            "step": "step3_quarter_n",
            "success": False,
            "M_target": M_target,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": tb,
            "pre_mem": pre_mem,
            "fail_mem": _mem_stat_str(device),
            "elapsed_s": round(time.time() - t0, 2),
        }


# ------ STEP 4: run 1 seed of reduced M-sweep ------

def step4_m_sweep(N_use: int, seed: int, M_sweep: List[int],
                   device: torch.device) -> Dict:
    """For each M in sweep, build substrate, measure recall, log mem."""
    t0 = time.time()
    per_M_results: List[Dict] = []
    max_M_pass = 0
    for M in M_sweep:
        cell_t0 = time.time()
        pre_mem = _mem_stat_str(device)
        try:
            codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
            W, keys, values, key_idx, val_idx = store_facts_batched(
                codebook, M, seed, N_use, device)
            n = min(N_PROBE, M)
            probe_keys = keys[:n]
            probe_val_idx = val_idx[:n] % codebook.shape[0]
            out_response = probe_keys @ W.T
            sims = (codebook @ out_response.T) / N_use
            pred = torch.argmax(sims, dim=0)
            recall = float((pred == probe_val_idx.to(device)).float().mean().item())
            cell_result = {
                "M": M,
                "success": True,
                "recall": round(recall, 5),
                "pre_mem": pre_mem,
                "post_mem": _mem_stat_str(device),
                "cell_elapsed_s": round(time.time() - cell_t0, 2),
            }
            if recall >= RECALL_THRESHOLD:
                max_M_pass = max(max_M_pass, M)
            del W, keys, values, codebook, out_response, sims, pred
            _safe_clear(device)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            cell_result = {
                "M": M,
                "success": False,
                "error_type": type(e).__name__,
                "error_msg": str(e),
                "pre_mem": pre_mem,
                "fail_mem": _mem_stat_str(device),
                "cell_elapsed_s": round(time.time() - cell_t0, 2),
            }
            _safe_clear(device)
        per_M_results.append(cell_result)
        print(f"  [step4] M={M} {cell_result.get('success')}: "
              f"recall={cell_result.get('recall', 'fail')} "
              f"mem={cell_result.get('post_mem', cell_result.get('fail_mem'))}",
              flush=True)
    return {
        "step": "step4_m_sweep",
        "M_sweep": M_sweep,
        "per_M": per_M_results,
        "max_M_at_95_recall": max_M_pass,
        "any_success": any(c.get("success") for c in per_M_results),
        "elapsed_s": round(time.time() - t0, 2),
    }


def compute_verdict(step_results: Dict[str, Dict]) -> Tuple[str, str]:
    s1 = step_results.get("step1_construct", {})
    s2 = step_results.get("step2_one_fact", {})
    s3 = step_results.get("step3_quarter_n", {})
    s4 = step_results.get("step4_m_sweep", {})
    s1_ok = bool(s1.get("success"))
    s2_ok = bool(s2.get("success"))
    s3_ok = bool(s3.get("success"))
    s4_full_ok = bool(s4.get("any_success")) and len(s4.get("per_M", [])) > 0 and \
        all(c.get("success") for c in s4.get("per_M", []))
    max_M = s4.get("max_M_at_95_recall", 0)

    detail = (f"s1_ok={s1_ok} s2_ok={s2_ok} s3_ok={s3_ok} "
              f"s4_full_ok={s4_full_ok} max_M={max_M} N={N_FULL}")

    if s1_ok and s2_ok and s3_ok and s4_full_ok and max_M > 0:
        return ("NSCALE_R_V3_HARD_PASS",
                f"ALL_STEPS_OK_max_M={max_M}: " + detail)
    # Diagnostic outcome: any explicit failure with error info is HF (the desired
    # diagnostic outcome). Identify the first failing step.
    for step_name, step_dict, ok in [
        ("step1_construct", s1, s1_ok),
        ("step2_one_fact",  s2, s2_ok),
        ("step3_quarter_n", s3, s3_ok),
    ]:
        if not ok:
            err_t = step_dict.get("error_type", "MISSING")
            err_m = (step_dict.get("error_msg", "step did not run") or "")[:200]
            return ("NSCALE_R_V3_HARD_FAIL",
                    f"DIAG_FAIL_AT_{step_name}: {err_t}: {err_m}; " + detail)
    if not s4_full_ok:
        return ("NSCALE_R_V3_MIDDLE_BAND",
                f"STEPS_1-3_OK_S4_PARTIAL: max_M={max_M}; " + detail)
    return ("NSCALE_R_V3_MIDDLE_BAND",
            f"UNEXPECTED_STATE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"
    assert len(M_SWEEP_FULL) == 4, f"M sweep should be 4 (no 2N): {M_SWEEP_FULL}"
    assert M_SWEEP_FULL == [2048, 4096, 8192, 16384], M_SWEEP_FULL

    # Verdict gates
    fake_pass = {
        "step1_construct": {"success": True},
        "step2_one_fact":  {"success": True},
        "step3_quarter_n": {"success": True},
        "step4_m_sweep":   {"any_success": True,
                             "per_M": [{"success": True}],
                             "max_M_at_95_recall": 8192},
    }
    v, _ = compute_verdict(fake_pass); assert "HARD_PASS" in v, v

    fake_step1_fail = {
        "step1_construct": {"success": False,
                             "error_type": "RuntimeError",
                             "error_msg": "CUDA out of memory"},
        "step2_one_fact":  {"success": False},
        "step3_quarter_n": {"success": False},
        "step4_m_sweep":   {"any_success": False, "per_M": [],
                             "max_M_at_95_recall": 0},
    }
    v, _ = compute_verdict(fake_step1_fail); assert "HARD_FAIL" in v, v
    assert "step1" in v.lower() or "step1_construct" in compute_verdict(fake_step1_fail)[1]

    fake_step4_partial = {
        "step1_construct": {"success": True},
        "step2_one_fact":  {"success": True},
        "step3_quarter_n": {"success": True},
        "step4_m_sweep":   {"any_success": True,
                             "per_M": [{"success": True}, {"success": False}],
                             "max_M_at_95_recall": 2048},
    }
    v, _ = compute_verdict(fake_step4_partial); assert "MIDDLE_BAND" in v, v

    # Smoke at small N: 1 fact succeeds
    device = torch.device("cpu")
    r = step2_one_fact(N_SMOKE, SEED_SMOKE, device)
    assert r["success"] and r["recall"] in (0.0, 1.0), r
    print(f"[selftest] n_scaling_modern_hopfield_rescue_v3_n16384 PASS "
          f"step2_one_fact at N={N_SMOKE} recall={r['recall']}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    # Diagnostic anchor: CPU only on remote_cpu_queue, but allow CUDA if available
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg   = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seed    = SEED_SMOKE if smoke else SEED

    out_dir = get_output_dir()
    done_keys = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] n_scaling_modern_hopfield_rescue_v3_n16384 smoke={smoke} "
          f"N={N_cfg} seed={seed} M_sweep={M_sweep} "
          f"device={device_str} done={len(done_keys)} "
          f"initial_mem={_mem_stat_str(device)}", flush=True)

    step_results: Dict[str, Dict] = {}

    for step_name, step_fn in [
        ("step1_construct", lambda: step1_construct(N_cfg, seed, device)),
        ("step2_one_fact",  lambda: step2_one_fact(N_cfg, seed, device)),
        ("step3_quarter_n", lambda: step3_quarter_n(N_cfg, seed, device)),
    ]:
        if step_name in done_keys:
            body = load_partial_key(out_dir, step_name)
            if body is not None:
                step_results[step_name] = body
                print(f"  [resume] {step_name} loaded from partial "
                      f"success={body.get('success')}", flush=True)
                continue
        print(f"  [run-step] {step_name} starting "
              f"mem={_mem_stat_str(device)}", flush=True)
        body = step_fn()
        write_partial_key(out_dir, step_name, body)
        step_results[step_name] = body
        print(f"  [run-step] {step_name} success={body.get('success')} "
              f"elapsed={body.get('elapsed_s')}s mem={_mem_stat_str(device)}",
              flush=True)
        # Hard-stop if step1 fails -- no point running the rest
        if step_name == "step1_construct" and not body.get("success"):
            print(f"  [stop] step1 failed; skipping step2/3/4 "
                  f"(error: {body.get('error_type')}: "
                  f"{(body.get('error_msg') or '')[:200]})", flush=True)
            break

    # Step 4 only runs if step1-3 all succeeded
    s1_ok = bool(step_results.get("step1_construct", {}).get("success"))
    s2_ok = bool(step_results.get("step2_one_fact", {}).get("success"))
    s3_ok = bool(step_results.get("step3_quarter_n", {}).get("success"))

    if s1_ok and s2_ok and s3_ok:
        step_name = "step4_m_sweep"
        if step_name in done_keys:
            body = load_partial_key(out_dir, step_name)
            if body is not None:
                step_results[step_name] = body
        else:
            print(f"  [run-step] step4_m_sweep starting "
                  f"M_sweep={M_sweep} mem={_mem_stat_str(device)}", flush=True)
            body = step4_m_sweep(N_cfg, seed, M_sweep, device)
            write_partial_key(out_dir, step_name, body)
            step_results[step_name] = body
    else:
        print(f"  [skip] step4_m_sweep skipped (earlier step failed)",
              flush=True)
        step_results.setdefault("step4_m_sweep", {
            "step": "step4_m_sweep",
            "skipped": True,
            "reason": "earlier_step_failed",
            "any_success": False,
            "per_M": [],
            "max_M_at_95_recall": 0,
        })

    verdict, verdict_msg = compute_verdict(step_results)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "n_scaling_modern_hopfield_rescue_v3_n16384",
        "N": N_cfg, "smoke": smoke, "seed": seed,
        "M_sweep": M_sweep,
        "steps": step_results,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": verdict_msg,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
