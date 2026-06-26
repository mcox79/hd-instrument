"""GPU memory budget projection helper (T7-style; lifted from lang_ingest_vocab_bigram_meta_m7_v1).

Cells that allocate large GPU tensors (codebooks, S-matrix partitions, eval batches)
can call `project_peak_mb(config)` at module init to refuse-to-start when projected
peak resident GPU memory exceeds a safety budget. This complements the runtime
`mem_get_info` gate by catching OOMs WITHOUT requiring an actual GPU (closed-form
projection on the production config).

USAGE (module-init self-test pattern):

    from hdlab.gpu_memory_budget import project_peak_mb, assert_under_budget

    GPU_BUDGET_MB = 6 * 1024  # 6 GB safety margin under 8 GB RTX 4060 Ti

    proj = project_peak_mb(
        allocations=[
            ("codebook",         (V_TOK + 1, N_DIM),       "float32", "persistent"),
            ("cb_norm",          (V_TOK + 1, N_DIM),       "float32", "persistent"),
            ("S_part_one",       (N_DIM, N_DIM),           "float32", "persistent"),
            ("predicted_full",   (N_EVAL_PAIRS, N_DIM),    "float32", "persistent"),
            ("sims_batch",       (GPU_BATCH, V_TOK + 1),   "float32", "transient"),
        ],
        budget_mb=GPU_BUDGET_MB,
    )
    assert_under_budget(proj, GPU_BUDGET_MB)  # raises with breakdown if over

USAGE (runtime gate pattern, after device probe):

    import torch
    if torch.cuda.is_available():
        free_b, total_b = torch.cuda.mem_get_info(0)
        free_mb = free_b / (1024 * 1024)
        if proj["projected_peak_mb"] > free_mb:
            raise RuntimeError(
                f"GPU memory gate: projected {proj['projected_peak_mb']:.0f} MB "
                f"exceeds free {free_mb:.0f} MB on {torch.cuda.get_device_name(0)}"
            )

Reference: experiments/exp_lang_ingest_vocab_bigram_meta_m7_v1.py (T7 self-test +
runtime gate fix commits 1ea55da9 + 99f3a436).
ASCII-only. No emojis. No torch dependency in this module (closed-form arithmetic only).
"""
from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence, Tuple

# Bytes-per-element for each supported dtype string. Keep ASCII names that match
# the canonical numpy/torch dtype short names.
DTYPE_BYTES = {
    "float64": 8,
    "double": 8,
    "f64": 8,
    "float32": 4,
    "float": 4,
    "f32": 4,
    "float16": 2,
    "half": 2,
    "f16": 2,
    "bfloat16": 2,
    "bf16": 2,
    "int64": 8,
    "long": 8,
    "i64": 8,
    "int32": 4,
    "int": 4,
    "i32": 4,
    "int16": 2,
    "i16": 2,
    "int8": 1,
    "i8": 1,
    "uint8": 1,
    "bool": 1,
    "complex64": 8,
    "complex128": 16,
}

# Allocation lifetime classes:
#   "persistent" : resident for the whole compute window; counts toward peak always.
#   "transient"  : freed before next phase; max across transients counts ONCE.
#   "phase_<n>"  : peak counts within phase only; freed at phase boundary; the
#                  worst phase sum gets added to persistent sum.
PERSISTENT = "persistent"
TRANSIENT = "transient"


def _bytes_for(shape: Sequence[int], dtype: str) -> int:
    dtype_l = dtype.strip().lower()
    if dtype_l not in DTYPE_BYTES:
        raise ValueError(
            f"unknown dtype {dtype!r}; supported: {sorted(DTYPE_BYTES.keys())}"
        )
    elems = 1
    for d in shape:
        if d < 0:
            raise ValueError(f"negative dim in shape {shape!r}")
        elems *= int(d)
    return elems * DTYPE_BYTES[dtype_l]


def _mb(n_bytes: float) -> float:
    return float(n_bytes) / (1024.0 * 1024.0)


def project_peak_mb(
    allocations: Iterable[Tuple[str, Sequence[int], str, str]],
    budget_mb: float | None = None,
) -> dict:
    """Project resident peak GPU memory in MB from an allocation manifest.

    Each allocation is a 4-tuple: (name, shape, dtype, lifetime).
      name     : human-readable identifier (used in breakdown)
      shape    : tuple/list of ints
      dtype    : one of DTYPE_BYTES keys (e.g. "float32", "float16", "int64")
      lifetime : "persistent" | "transient" | "phase_<n>" for n in 1..9

    Peak model (matches T7 in lang_ingest_vocab_bigram_meta_m7_v1):
      peak = sum(persistent allocations)
           + max(0, max sum-within-each-phase across phases, max single transient)

    Rationale: persistent buffers coexist with whichever phase's working set is
    largest. Per-phase allocations within a single phase coexist with each other
    but get freed before the next phase begins. Generic transients (no phase tag)
    are treated as the worst single transient peak.

    Returns dict with keys:
      projected_peak_mb : worst-case peak MB
      persistent_mb     : sum of persistent allocations
      phase_peaks_mb    : dict[phase -> sum within that phase]
      transient_peak_mb : worst single transient
      breakdown         : list of {name, shape, dtype, lifetime, mb}
      budget_mb         : echoed budget (or None)
      headroom_mb       : budget_mb - projected_peak_mb (if budget given)
      over_budget       : bool (if budget given)
    """
    persistent_bytes = 0
    phase_bytes: dict[str, int] = {}
    transient_max_bytes = 0
    breakdown: List[dict] = []

    for name, shape, dtype, lifetime in allocations:
        nb = _bytes_for(shape, dtype)
        breakdown.append({
            "name": name,
            "shape": tuple(int(d) for d in shape),
            "dtype": dtype,
            "lifetime": lifetime,
            "mb": _mb(nb),
        })
        lt = lifetime.strip().lower()
        if lt == PERSISTENT:
            persistent_bytes += nb
        elif lt == TRANSIENT:
            if nb > transient_max_bytes:
                transient_max_bytes = nb
        elif lt.startswith("phase_"):
            phase_bytes[lt] = phase_bytes.get(lt, 0) + nb
        else:
            raise ValueError(
                f"unknown lifetime {lifetime!r} for {name!r}; "
                f"use 'persistent', 'transient', or 'phase_<n>'"
            )

    phase_peak_bytes = max(phase_bytes.values(), default=0)
    working_peak_bytes = max(phase_peak_bytes, transient_max_bytes)
    peak_bytes = persistent_bytes + working_peak_bytes

    out = {
        "projected_peak_mb": _mb(peak_bytes),
        "persistent_mb": _mb(persistent_bytes),
        "phase_peaks_mb": {k: _mb(v) for k, v in phase_bytes.items()},
        "transient_peak_mb": _mb(transient_max_bytes),
        "breakdown": breakdown,
        "budget_mb": budget_mb,
    }
    if budget_mb is not None:
        out["headroom_mb"] = float(budget_mb) - out["projected_peak_mb"]
        out["over_budget"] = out["projected_peak_mb"] > float(budget_mb)
    return out


def assert_under_budget(projection: Mapping, budget_mb: float) -> None:
    """Raise RuntimeError with full breakdown if projection exceeds budget.

    Mirrors the T7 selftest assertion shape in lang_ingest_vocab_bigram_meta_m7_v1
    so cells can swap call sites with minimal churn.
    """
    peak = float(projection["projected_peak_mb"])
    if peak > float(budget_mb):
        raise RuntimeError(
            f"GPU memory projection {peak:.0f} MB exceeds budget {budget_mb:.0f} MB; "
            f"breakdown={projection}"
        )


def project_simple(
    n_dim: int,
    v_tok: int,
    gpu_batch: int,
    n_eval: int,
    n_partitions: int,
    dtype: str = "float32",
) -> dict:
    """Convenience wrapper that recreates the exact lang_ingest M7 T7 projection.

    Useful for cells that mirror the lang_ingest pipeline (codebook + S
    partitions + predicted_full + sims_batch). For arbitrary topology use
    project_peak_mb() directly.
    """
    allocations = [
        ("codebook",       (v_tok + 1, n_dim),     dtype, PERSISTENT),
        ("cb_norm",        (v_tok + 1, n_dim),     dtype, PERSISTENT),
        ("S_part_one",     (n_dim, n_dim),         dtype, PERSISTENT),
        ("predicted_full", (n_eval, n_dim),        dtype, PERSISTENT),
        ("cues_full",      (n_eval, n_dim),        dtype, "phase_1"),
        ("sims_batch",     (gpu_batch, v_tok + 1), dtype, "transient"),
        ("pred_batch_norm", (gpu_batch, n_dim),    dtype, "transient"),
    ]
    proj = project_peak_mb(allocations)
    # Sanity: full S-resident pre-fix would have been catastrophic.
    pre_fix_resident_mb = n_partitions * n_dim * n_dim * DTYPE_BYTES[dtype.lower()] / (1024 * 1024)
    proj["pre_fix_full_S_resident_mb"] = pre_fix_resident_mb
    proj["n_partitions"] = n_partitions
    return proj


__all__ = [
    "DTYPE_BYTES",
    "PERSISTENT",
    "TRANSIENT",
    "project_peak_mb",
    "assert_under_budget",
    "project_simple",
]
