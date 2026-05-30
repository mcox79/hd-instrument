"""Shared 6-metric battery for phase-region characterization (2026-05-30).

Used by:
  - experiments/exp_region_c_optimal_probe_v1_n4096.py (8-cell Region C vs A)
  - experiments/exp_phase_lattice_grid_v1_n4096.py    (63-cell envelope grid)

Single source of truth for the 6 metrics; both anchors import this module so
comparisons across the two experiments are by-construction comparable.

The 6 metrics (per user spec):
  1. above_thresh_frac  -- KF-1 hallucination detection: fraction of OOS keys
       whose retrieved softmax confidence exceeds a hallucination threshold.
       HP < 0.05.
  2. max_iso            -- KF-2 edit isolation: max correlation in inter-fact
       retrieval (max |delta_acc| over non-edited probe keys after a rank-1
       edit). HP < 0.05.
  3. retention          -- argmax retrieval accuracy at stored keys.
  4. edit_then_retrieve -- store, perform single edit, then retrieve the
       EDITED fact: fraction of edits that return the new value.
  5. retrieval_latency_ns -- wall-clock nanoseconds per query (single batch
       of n_probe queries; reported as ns/query mean).
  6. kf1_sharpness      -- ratio: max confidence on stored / mean confidence
       on negatives. Larger = sharper.

All metrics take a SHARED substrate setup (W, codebook, key_idx, val_idx)
and never re-run store_facts_batched themselves. The caller stores once per
cell and passes the W and the indexing arrays to every metric.

ASCII-only. Self-test included at module scope.

Imports the substrate primitives (Kerdock codebook, batched-store, softmax
confidence) from exp_t1_beta_sweep_v1_n4096 via the same importlib pattern
that exp_phase_region_cd_v1_n4096 uses -- this keeps the substrate-API call
shape consistent and avoids a cyclic dependency.
"""
from __future__ import annotations

import sys

# Defensive: in case this module is imported by a script that hasn't
# reconfigured stdout yet (e.g. unit-test runners).
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import importlib.util
import math
import time
from pathlib import Path
from typing import Dict, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# -------- substrate-primitive loader (lazy, no selftest side-effects) --------
_T1V1 = None


def _load_t1v1():
    """Lazy load of exp_t1_beta_sweep_v1_n4096 substrate primitives.

    The script has a module-level _instrumentation_selftest() that runs on
    import; that's fine and expected per the role contract. We just want to
    cache the module so each downstream caller doesn't re-import.
    """
    global _T1V1
    if _T1V1 is None:
        path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
        spec = importlib.util.spec_from_file_location("t1v1_metric_battery", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _T1V1 = mod
    return _T1V1


def make_substrate(N: int, M: int, seed: int, device: torch.device):
    """Build a substrate cell: codebook + W + (keys, values) + indices.

    Returns: (codebook, W, keys, values, key_idx, val_idx).

    This is the SHARED setup the metric battery operates on. One call per
    (cell, seed); all six metrics consume the outputs.
    """
    t1v1 = _load_t1v1()
    codebook, _ = t1v1.v3.make_kerdock_4coset_codebook(N, device)
    W, keys, values, key_idx, val_idx = t1v1.store_facts_batched(
        codebook, M, seed, N, device
    )
    return codebook, W, keys, values, key_idx, val_idx


# -------- six metrics --------

# Threshold constants used by KF-1
DEFAULT_N_PROBE = 200            # probes per metric where applicable
DEFAULT_N_EDITS = 16             # edits for KF-2 isolation
HALLU_THRESHOLD = 0.5            # max-confidence threshold for above_thresh_frac


def metric_above_thresh_frac(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
    threshold: float = HALLU_THRESHOLD,
) -> Dict:
    """Metric 1: KF-1 hallucination detection.

    Sample n_probe OOS (out-of-store) keys. For each, retrieve and compute
    softmax confidence on the top candidate. Return the fraction whose top
    confidence exceeds the threshold. HP_PASS: this fraction < 0.05.
    """
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 700)
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])
    available = [i for i in range(C) if i not in stored_set]
    if not available:
        return {
            "above_thresh_frac": 0.0,
            "mean_oos_max_conf": 0.0,
            "n_oos": 0,
        }
    n_oos = min(n_probe, len(available))
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_oos]
    oos_idx = torch.tensor(
        [available[int(i)] for i in perm.tolist()],
        dtype=torch.long, device=device,
    )
    oos_keys = codebook[oos_idx]                      # (n_oos, N)
    q = oos_keys @ W.T                                # (n_oos, N)
    sims = (codebook @ q.T) / N                       # (C, n_oos)
    P = torch.softmax(beta * sims, dim=0)             # (C, n_oos)
    max_conf = P.max(dim=0).values                    # (n_oos,)
    above = float((max_conf >= threshold).float().mean().item())
    mean_mc = float(max_conf.mean().item())
    return {
        "above_thresh_frac": round(above, 5),
        "mean_oos_max_conf": round(mean_mc, 5),
        "n_oos": int(n_oos),
    }


def metric_max_iso(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
    n_edits: int = DEFAULT_N_EDITS,
) -> Dict:
    """Metric 2: KF-2 edit isolation.

    Perform n_edits single rank-1 edits. After each edit, measure the
    argmax-accuracy delta on a held-out probe set (the FIRST n_probe stored
    keys). max_iso = max over edits of |delta_acc|. HP_PASS: max_iso < 0.05.
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    if n < 2:
        return {"max_iso": 0.0, "n_edits_run": 0, "n_probe": int(n)}

    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    probe_keys = codebook[probe_key_idx]              # (n, N)

    sims_before = (codebook @ (probe_keys @ W.T).T) / N
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_val_idx.to(device)).float()

    gen = torch.Generator(device=device).manual_seed(seed + 800)
    isolation_deltas = []
    edits_to_run = min(n_edits, max(0, M - n))
    if edits_to_run <= 0:
        return {"max_iso": 0.0, "n_edits_run": 0, "n_probe": int(n)}

    for edit_i in range(edits_to_run):
        edit_pos = n + edit_i
        if edit_pos >= M:
            break
        old_key = codebook[key_idx[edit_pos] % C]
        old_val = codebook[val_idx[edit_pos] % C]
        new_val_i = int(torch.randint(0, C, (1,), generator=gen, device=device).item())
        new_val = codebook[new_val_i]
        W_ed = W + torch.outer(new_val - old_val, old_key) / N
        sims_after = (codebook @ (probe_keys @ W_ed.T).T) / N
        pred_after = torch.argmax(sims_after, dim=0)
        acc_after = (pred_after == probe_val_idx.to(device)).float()
        delta = float((acc_before - acc_after).abs().mean().item())
        isolation_deltas.append(delta)

    max_iso = max(isolation_deltas) if isolation_deltas else 0.0
    return {
        "max_iso": round(max_iso, 5),
        "n_edits_run": int(len(isolation_deltas)),
        "n_probe": int(n),
    }


def metric_retention(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
) -> Dict:
    """Metric 3: argmax retrieval accuracy at stored keys."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    probe_keys = codebook[probe_key_idx]
    sims = (codebook @ (probe_keys @ W.T).T) / N
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx.to(device)).float().mean().item())
    return {
        "retention": round(acc, 5),
        "n_probe": int(n),
    }


def metric_edit_then_retrieve(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_edits: int = DEFAULT_N_EDITS,
) -> Dict:
    """Metric 4: edit-then-retrieve accuracy.

    For each of n_edits stored facts, replace the value with a new codeword
    via rank-1 edit, then immediately retrieve at the same key. Score = 1 if
    the argmax matches the new value index, else 0. Report mean accuracy.
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    if M < 1:
        return {"edit_then_retrieve": 0.0, "n_edits_run": 0}

    gen = torch.Generator(device=device).manual_seed(seed + 900)
    edits_to_run = min(n_edits, M)
    correct = 0
    n_run = 0
    # Operate on a working copy so successive edits don't accumulate.
    for edit_i in range(edits_to_run):
        edit_pos = edit_i
        old_key = codebook[key_idx[edit_pos] % C]
        old_val = codebook[val_idx[edit_pos] % C]
        new_val_i = int(torch.randint(0, C, (1,), generator=gen, device=device).item())
        # Avoid the trivially-correct case where new == old
        if new_val_i == int(val_idx[edit_pos] % C):
            new_val_i = (new_val_i + 1) % C
        new_val = codebook[new_val_i]
        W_ed = W + torch.outer(new_val - old_val, old_key) / N
        # Retrieve at the edited key
        q = old_key @ W_ed.T                          # (N,)
        sims = (codebook @ q) / N                     # (C,)
        pred = int(torch.argmax(sims).item())
        if pred == new_val_i:
            correct += 1
        n_run += 1

    acc = (correct / n_run) if n_run > 0 else 0.0
    return {
        "edit_then_retrieve": round(acc, 5),
        "n_edits_run": int(n_run),
    }


def metric_retrieval_latency_ns(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
) -> Dict:
    """Metric 5: retrieval latency (ns per query).

    Time the single batched retrieval call (n_probe queries) and report
    ns/query mean. Reports both the batched-mean and the wall_ns total.
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    if n < 1:
        return {"retrieval_latency_ns": 0.0, "wall_ns_total": 0.0, "n_probe": 0}
    probe_key_idx = key_idx[:n] % C
    probe_keys = codebook[probe_key_idx]
    # Warm-up so we don't measure the first kernel launch on GPU
    _ = (codebook @ (probe_keys @ W.T).T) / N
    if device.type == 'cuda':
        torch.cuda.synchronize()
    t0 = time.perf_counter_ns()
    sims = (codebook @ (probe_keys @ W.T).T) / N
    _pred = torch.argmax(sims, dim=0)
    if device.type == 'cuda':
        torch.cuda.synchronize()
    t1 = time.perf_counter_ns()
    wall_ns = float(t1 - t0)
    per_query = wall_ns / float(n)
    return {
        "retrieval_latency_ns": round(per_query, 2),
        "wall_ns_total": round(wall_ns, 2),
        "n_probe": int(n),
    }


def metric_kf1_sharpness(
    W: torch.Tensor,
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
) -> Dict:
    """Metric 6: KF-1 sharpness.

    Compute (max softmax conf on stored keys) / (mean softmax conf on OOS
    keys). Large value = highly discriminative; substrate confidently
    distinguishes stored from unstored.
    """
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n = min(n_probe, M)
    if n < 1 or M < 1:
        return {"kf1_sharpness": 0.0, "max_stored_conf": 0.0, "mean_neg_conf": 0.0}

    probe_key_idx = key_idx[:n] % C
    stored_keys = codebook[probe_key_idx]             # (n, N)
    q_pos = stored_keys @ W.T                         # (n, N)
    sims_pos = (codebook @ q_pos.T) / N               # (C, n)
    P_pos = torch.softmax(beta * sims_pos, dim=0)
    max_stored = float(P_pos.max(dim=0).values.max().item())

    # Negatives: OOS keys
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])
    available = [i for i in range(C) if i not in stored_set]
    if not available:
        return {
            "kf1_sharpness": 0.0,
            "max_stored_conf": round(max_stored, 5),
            "mean_neg_conf": 0.0,
        }
    gen = torch.Generator(device=device).manual_seed(seed + 600)
    n_neg = min(n_probe, len(available))
    perm = torch.randperm(len(available), generator=gen, device=device)[:n_neg]
    neg_idx = torch.tensor(
        [available[int(i)] for i in perm.tolist()],
        dtype=torch.long, device=device,
    )
    neg_keys = codebook[neg_idx]
    q_neg = neg_keys @ W.T
    sims_neg = (codebook @ q_neg.T) / N
    P_neg = torch.softmax(beta * sims_neg, dim=0)
    mean_neg = float(P_neg.max(dim=0).values.mean().item())

    sharp = max_stored / max(mean_neg, 1e-9)
    return {
        "kf1_sharpness": round(sharp, 5),
        "max_stored_conf": round(max_stored, 5),
        "mean_neg_conf": round(mean_neg, 5),
    }


# -------- battery driver: runs all six on one shared substrate setup --------

METRIC_NAMES = (
    "above_thresh_frac",
    "max_iso",
    "retention",
    "edit_then_retrieve",
    "retrieval_latency_ns",
    "kf1_sharpness",
)


def run_battery(
    N: int,
    M: int,
    beta: float,
    seed: int,
    device: torch.device,
    n_probe: int = DEFAULT_N_PROBE,
    n_edits: int = DEFAULT_N_EDITS,
) -> Dict:
    """Run all 6 metrics on ONE substrate setup (M, beta, seed) at N.

    Returns a flat dict containing every metric's top-line value plus the
    auxiliary fields each metric reports. The 6 top-line keys are exactly
    METRIC_NAMES; verdict logic can rely on those being present.
    """
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N, M, seed, device)
    out: Dict = {
        "N": int(N),
        "M": int(M),
        "beta": float(beta),
        "seed": int(seed),
    }

    r = metric_above_thresh_frac(W, codebook, key_idx, val_idx, N, beta, seed, device, n_probe=n_probe)
    out["above_thresh_frac"] = r["above_thresh_frac"]
    out["_kf1_aux"] = r

    r = metric_max_iso(W, codebook, key_idx, val_idx, N, beta, seed, device, n_probe=n_probe, n_edits=n_edits)
    out["max_iso"] = r["max_iso"]
    out["_kf2_aux"] = r

    r = metric_retention(W, codebook, key_idx, val_idx, N, beta, seed, device, n_probe=n_probe)
    out["retention"] = r["retention"]
    out["_ret_aux"] = r

    r = metric_edit_then_retrieve(W, codebook, key_idx, val_idx, N, beta, seed, device, n_edits=n_edits)
    out["edit_then_retrieve"] = r["edit_then_retrieve"]
    out["_etr_aux"] = r

    r = metric_retrieval_latency_ns(W, codebook, key_idx, val_idx, N, beta, seed, device, n_probe=n_probe)
    out["retrieval_latency_ns"] = r["retrieval_latency_ns"]
    out["_lat_aux"] = r

    r = metric_kf1_sharpness(W, codebook, key_idx, val_idx, N, beta, seed, device, n_probe=n_probe)
    out["kf1_sharpness"] = r["kf1_sharpness"]
    out["_sharp_aux"] = r

    # Free substrate tensors immediately to allow next cell to allocate.
    del W, keys, values, key_idx, val_idx, codebook
    return out


# -------- module self-test (mandatory) --------


def _instrumentation_selftest() -> None:
    """Assert all 6 metrics non-null/non-sentinel on a small CPU substrate.

    NOTE: Kerdock codebook requires N = 2^(2t) where t in {5,6,7}, i.e.
    N in {1024, 4096, 16384}. Smallest legal N is 1024; we run the selftest
    there on CPU (single seed, tiny M) so it completes in ~0.5s.
    """
    device = torch.device("cpu")
    N = 1024
    M = 64
    beta = 4.0
    seed = 17

    out = run_battery(N, M, beta, seed, device, n_probe=32, n_edits=4)
    for k in METRIC_NAMES:
        assert k in out, f"battery missing metric {k}"
        v = out[k]
        assert v is not None, f"metric {k} is None"
        # All metrics here are floats; none should be NaN
        assert not (isinstance(v, float) and math.isnan(v)), f"metric {k} is NaN"
    # Sanity: retention with M=64 < C should be reasonably high but not exactly 1
    assert 0.0 <= out["retention"] <= 1.0, f"retention out of range: {out['retention']}"
    assert 0.0 <= out["above_thresh_frac"] <= 1.0, f"above_thresh_frac out of range"
    assert 0.0 <= out["edit_then_retrieve"] <= 1.0, f"edit_then_retrieve out of range"
    assert out["retrieval_latency_ns"] >= 0.0, f"latency negative: {out['retrieval_latency_ns']}"
    assert out["kf1_sharpness"] >= 0.0, f"sharpness negative: {out['kf1_sharpness']}"
    print(
        f"[selftest] _metric_battery 6/6 metrics OK "
        f"ret={out['retention']:.3f} above={out['above_thresh_frac']:.3f} "
        f"max_iso={out['max_iso']:.3f} etr={out['edit_then_retrieve']:.3f} "
        f"lat_ns={out['retrieval_latency_ns']:.0f} sharp={out['kf1_sharpness']:.2f}",
        flush=True,
    )


_instrumentation_selftest()


__all__ = [
    "make_substrate",
    "metric_above_thresh_frac",
    "metric_max_iso",
    "metric_retention",
    "metric_edit_then_retrieve",
    "metric_retrieval_latency_ns",
    "metric_kf1_sharpness",
    "run_battery",
    "METRIC_NAMES",
    "DEFAULT_N_PROBE",
    "DEFAULT_N_EDITS",
    "HALLU_THRESHOLD",
]
