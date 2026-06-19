"""Scenario: large_N_envelope.

Empirically map the single-substrate capability envelope across (N, M) before
designing around sharding. The hypothesis under test is the user directive:

  "Test single substrate at production scale before designing around sharding.
   The substrate's real envelope might be substantially larger than what's
   been characterized."

Existing characterization is dominated by N=2048. This scenario sweeps
N in config["N_sweep"] (default [2048, 4096, 8192]) crossed with M/N ratios
in config["M_per_N_ratios"] (default [0.25, 0.5, 1.0, 2.0]) and reports for
every cell:

  recall_at_1            on 200 random stored keys
  near_uniform_frac      KF-1 OOS panel (200 OOS atoms)
  max_iso                KF-2 edit-isolation panel (16 edits)
  tcft_var_ratio         TCFT deletion panel (16 deletes)
  p50_retrieve_us        latency on 200 random queries
  peak_rss_mb            resident set size after build, via psutil if available
  W_bytes                exact W matrix bytes (N*N*4)
  codebook_bytes         exact codebook bytes (C*N*4)
  disk_MB                save() footprint on disk

Envelope analysis produced at the top level:
  max_M_at_95_recall_per_N        highest M for which recall_at_1 >= 0.95
  max_M_at_50_near_uniform_per_N  highest M for which near_uniform_frac >= 0.5

HARD-PASS bands (per envelope-expansion-fail-bands feedback, pre-registered):
  recall_at_1 >= 0.85 at M_ratio <= 1.0 for all N
  near_uniform_frac >= 0.5 at M_ratio <= 0.5 for all N
  tcft_var_ratio < 0.15 at all (N, M_ratio) cells

Codebook convention: C = 4 * N. BSC works at any N. Kerdock requires log2(N)
even; default kind is BSC so N=2048, 4096, 8192, 16384 all work.

Memory notes:
  N=8192 with C=32768: codebook ~ 1.0 GB, W = 256 MB. ~1.5 GB per cell.
  N=16384 with C=65536: codebook ~ 4.0 GB, W = 1.0 GB. ~5.5 GB per cell.
  We free each substrate (del + gc.collect()) between cells.

Default config skips N=16384. Pass extended_N: true to include it.
"""

from __future__ import annotations

import gc
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from testbed.api import MemoryBackend

try:
    import psutil  # type: ignore
    _HAVE_PSUTIL = True
except ImportError:
    psutil = None  # type: ignore
    _HAVE_PSUTIL = False


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            continue
    return total


def _rss_bytes() -> int:
    """Return current process RSS in bytes, or 0 if psutil unavailable."""
    if not _HAVE_PSUTIL:
        return 0
    try:
        return int(psutil.Process().memory_info().rss)
    except Exception:
        return 0


def _build_substrate(backend: MemoryBackend, N: int, codebook_kind: str,
                     codebook_scale: int, beta: float,
                     hallu_threshold: float, seed: int):
    """Construct a fresh substrate of the same class as `backend` at this N.

    Honors codebook_scale (default 4) so C = codebook_scale * N. Falls back to
    legacy kwargs if codebook_M_hint is not accepted.
    """
    cls = type(backend)
    kwargs = {
        "N": int(N),
        "codebook_kind": codebook_kind,
        "codebook_scale": int(codebook_scale),
        "beta": float(beta),
        "hallu_threshold": float(hallu_threshold),
        "device": "cpu",
        "seed": int(seed),
    }
    try:
        return cls(**kwargs)
    except TypeError:
        kwargs.pop("device", None)
        return cls(**kwargs)


def _make_vecs(rng: np.random.Generator, M: int, N: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, N), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    extended = bool(config.get("extended_N", False))
    if extended:
        N_sweep_default = [2048, 4096, 8192, 16384]
    else:
        N_sweep_default = [2048, 4096, 8192]
    N_sweep = list(config.get("N_sweep", N_sweep_default))
    M_per_N_ratios = list(config.get("M_per_N_ratios", [0.25, 0.5, 1.0, 2.0]))
    codebook_kind = str(config.get("codebook_kind", "bsc"))
    codebook_scale = int(config.get("codebook_scale", 4))
    beta = float(config.get("beta", 32.0))
    hallu_threshold = float(config.get("hallu_threshold", 0.5))
    seed = _first_seed(config)
    n_recall_samples = int(config.get("envelope_n_recall_samples", 200))
    n_oos_samples = int(config.get("envelope_n_oos_samples", 200))
    n_edit_trials = int(config.get("envelope_n_edit_trials", 16))
    n_delete_trials = int(config.get("envelope_n_delete_trials", 16))
    n_latency_queries = int(config.get("envelope_n_latency_queries", 200))
    measure_disk = bool(config.get("envelope_measure_disk", True))

    return {
        "N_sweep": N_sweep,
        "M_per_N_ratios": M_per_N_ratios,
        "codebook_kind": codebook_kind,
        "codebook_scale": codebook_scale,
        "beta": beta,
        "hallu_threshold": hallu_threshold,
        "seed": seed,
        "n_recall_samples": n_recall_samples,
        "n_oos_samples": n_oos_samples,
        "n_edit_trials": n_edit_trials,
        "n_delete_trials": n_delete_trials,
        "n_latency_queries": n_latency_queries,
        "measure_disk": measure_disk,
        "extended_N": extended,
    }


def _is_substrate(backend: MemoryBackend) -> bool:
    nm = getattr(backend, "name", "")
    return nm == "substrate" or nm.startswith("substrate_v") or nm == "substrate_sharded"


def _measure_cell(N: int, M: int, codebook_kind: str, codebook_scale: int,
                  beta: float, hallu_threshold: float, seed: int,
                  template_backend: MemoryBackend,
                  n_recall_samples: int, n_oos_samples: int,
                  n_edit_trials: int, n_delete_trials: int,
                  n_latency_queries: int,
                  measure_disk: bool) -> dict:
    """Build a substrate at (N, M), exercise it, return measurements."""
    rss_before = _rss_bytes()

    sub = _build_substrate(template_backend, N, codebook_kind, codebook_scale,
                           beta, hallu_threshold, seed)
    C = int(getattr(sub, "C", codebook_scale * N))

    # Honest skip: substrate cannot hold M >= C distinct value atoms.
    if M >= C:
        del sub
        gc.collect()
        return {
            "N": N,
            "M": M,
            "M_over_N": M / float(N) if N else None,
            "C": C,
            "skipped": True,
            "reason": f"M={M} >= C={C}; codebook would exhaust",
        }

    rng = np.random.default_rng(seed + 9000 + N * 17 + M)
    vecs = _make_vecs(rng, M, N)
    ids = [f"ln_{N}_{M}_{i:08d}" for i in range(M)]
    values = [f"v_{i}" for i in range(M)]

    # Store loop.
    store_us: list[float] = []
    store_sample_cap = min(n_latency_queries, M)
    t_store_start = time.perf_counter_ns()
    for i in range(M):
        t0 = time.perf_counter_ns()
        sub.store(ids[i], vecs[i], values[i])
        t1 = time.perf_counter_ns()
        if i < store_sample_cap:
            store_us.append((t1 - t0) / 1000.0)
    store_wall_s = (time.perf_counter_ns() - t_store_start) / 1e9

    rss_after_store = _rss_bytes()

    # Recall@1 on n_recall_samples random keys.
    r_count = min(n_recall_samples, M)
    r_idx = rng.choice(M, size=r_count, replace=False)
    hits = 0
    for i in r_idx:
        res = sub.retrieve(vecs[i], k=1)
        if res.key_id == ids[i]:
            hits += 1
    recall_at_1 = hits / max(r_count, 1)

    # Latency: n_latency_queries random retrieves.
    q_count = min(n_latency_queries, M)
    q_idx = rng.choice(M, size=q_count, replace=False)
    retr_us: list[float] = []
    for i in q_idx:
        t0 = time.perf_counter_ns()
        sub.retrieve(vecs[i], k=1)
        t1 = time.perf_counter_ns()
        retr_us.append((t1 - t0) / 1000.0)

    # Audit panels: KF-1, KF-2, TCFT via backend.audit().
    near_uniform_frac = None
    kf1_mean_max = None
    kf2_max_iso = None
    tcft_var_ratio = None
    try:
        audit = sub.audit(
            n_oos=n_oos_samples,
            n_edit=n_edit_trials,
            n_delete=n_delete_trials,
        )
        # Convention: kf1_above_thresh_frac is "above hallu_threshold"; we
        # report near_uniform_frac via 1 - that, since substrate's KF-1 win
        # is the OOS flagging fraction. Substrate audit() reports above-thresh
        # directly; we expose both and derive near_uniform_frac = 1 - above.
        above = audit.kf1_above_thresh_frac
        if above is not None:
            near_uniform_frac = 1.0 - float(above)
        kf1_mean_max = audit.kf1_mean_oos_max_conf
        kf2_max_iso = audit.kf2_max_isolation
        tcft_var_ratio = audit.tcft_mean_var_ratio
    except Exception as exc:
        # Don't fail the cell; record None and move on.
        audit_err = f"audit failed: {exc}"
    else:
        audit_err = None

    # Disk + W/codebook bytes.
    W_bytes = int(N) * int(N) * 4
    codebook_bytes = int(C) * int(N) * 4
    disk_bytes = 0
    if measure_disk:
        save_dir = Path(tempfile.mkdtemp(prefix=f"lN_{N}_{M}_"))
        try:
            sub.save(save_dir)
            disk_bytes = _dir_size_bytes(save_dir)
        except Exception:
            disk_bytes = 0
        finally:
            try:
                shutil.rmtree(save_dir, ignore_errors=True)
            except OSError:
                pass

    rss_peak = max(rss_before, rss_after_store, _rss_bytes())

    cell = {
        "N": int(N),
        "M": int(M),
        "M_over_N": M / float(N) if N else None,
        "C": int(C),
        "skipped": False,
        "recall_at_1": float(recall_at_1),
        "n_recall_samples": int(r_count),
        "near_uniform_frac": (
            float(near_uniform_frac) if near_uniform_frac is not None else None
        ),
        "kf1_mean_oos_max_conf": (
            float(kf1_mean_max) if kf1_mean_max is not None else None
        ),
        "max_iso": (
            float(kf2_max_iso) if kf2_max_iso is not None else None
        ),
        "tcft_var_ratio": (
            float(tcft_var_ratio) if tcft_var_ratio is not None else None
        ),
        "p50_store_us": _percentile(store_us, 50),
        "p95_store_us": _percentile(store_us, 95),
        "p50_retrieve_us": _percentile(retr_us, 50),
        "p95_retrieve_us": _percentile(retr_us, 95),
        "store_wall_s": float(store_wall_s),
        "W_bytes": int(W_bytes),
        "codebook_bytes": int(codebook_bytes),
        "disk_bytes": int(disk_bytes),
        "disk_MB": float(disk_bytes) / 1.0e6,
        "peak_rss_bytes": int(rss_peak),
        "peak_rss_mb": float(rss_peak) / 1.0e6,
        "rss_measured": bool(_HAVE_PSUTIL),
        "audit_error": audit_err,
    }

    # Free substrate memory between cells. The substrate holds two large
    # tensors (W and codebook); explicit del + gc + empty_cache is required
    # to keep RSS bounded across the sweep.
    del sub
    gc.collect()
    try:
        torch.cuda.empty_cache()
    except Exception:
        pass

    return cell


def _envelope_analysis(cells: list[dict], recall_threshold: float = 0.95,
                       near_uniform_threshold: float = 0.5) -> dict:
    """For each N, return the largest M that meets recall + near-uniform gates."""
    max_M_recall: dict[str, int | None] = {}
    max_M_near_uniform: dict[str, int | None] = {}
    by_N: dict[int, list[dict]] = {}
    for c in cells:
        if c.get("skipped"):
            continue
        N = int(c["N"])
        by_N.setdefault(N, []).append(c)
    for N, lst in by_N.items():
        lst_sorted = sorted(lst, key=lambda c: int(c["M"]))
        best_recall: int | None = None
        best_nu: int | None = None
        for c in lst_sorted:
            r = c.get("recall_at_1")
            if r is not None and r >= recall_threshold:
                best_recall = int(c["M"])
            nu = c.get("near_uniform_frac")
            if nu is not None and nu >= near_uniform_threshold:
                best_nu = int(c["M"])
        max_M_recall[str(N)] = best_recall
        max_M_near_uniform[str(N)] = best_nu
    return {
        "max_M_at_95_recall_per_N": max_M_recall,
        "max_M_at_50_near_uniform_per_N": max_M_near_uniform,
        "recall_threshold": recall_threshold,
        "near_uniform_threshold": near_uniform_threshold,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    """Run the envelope sweep. Substrate-only scenario.

    For non-substrate backends, returns an explicit skip payload so the run
    matrix still produces a row.
    """
    if not _is_substrate(backend):
        return {
            "scenario": "large_N_envelope",
            "backend": backend.name,
            "skipped": True,
            "reason": "large_N_envelope is substrate-only (probes W matrix scaling)",
            "per_cell": [],
            "envelope": {},
        }

    N_sweep: list[int] = [int(x) for x in data["N_sweep"]]
    ratios: list[float] = [float(x) for x in data["M_per_N_ratios"]]
    codebook_kind: str = str(data["codebook_kind"])
    codebook_scale: int = int(data["codebook_scale"])
    beta: float = float(data["beta"])
    hallu_threshold: float = float(data["hallu_threshold"])
    seed: int = int(data["seed"])

    cells: list[dict] = []
    for N in N_sweep:
        for ratio in ratios:
            M = max(1, int(round(ratio * N)))
            cell = _measure_cell(
                N=N,
                M=M,
                codebook_kind=codebook_kind,
                codebook_scale=codebook_scale,
                beta=beta,
                hallu_threshold=hallu_threshold,
                seed=seed,
                template_backend=backend,
                n_recall_samples=int(data["n_recall_samples"]),
                n_oos_samples=int(data["n_oos_samples"]),
                n_edit_trials=int(data["n_edit_trials"]),
                n_delete_trials=int(data["n_delete_trials"]),
                n_latency_queries=int(data["n_latency_queries"]),
                measure_disk=bool(data["measure_disk"]),
            )
            cell["M_ratio"] = float(ratio)
            cells.append(cell)

    envelope = _envelope_analysis(cells)

    return {
        "scenario": "large_N_envelope",
        "backend": backend.name,
        "N_sweep": N_sweep,
        "M_per_N_ratios": ratios,
        "codebook_kind": codebook_kind,
        "codebook_scale": codebook_scale,
        "per_cell": cells,
        "envelope": envelope,
        "extended_N": bool(data.get("extended_N", False)),
        "rss_measured": bool(_HAVE_PSUTIL),
    }


def thresholds() -> dict:
    """Pre-registered HARD-PASS bands per envelope-expansion-fail-bands feedback.

    Gates fire on aggregate envelope metrics, not on individual cells, so the
    run dashboard can show one verdict per (scenario, backend) pair.
    """
    return {
        "substrate": {
            "hard_pass": {
                # recall_at_1 >= 0.85 at M_ratio <= 1.0 across all N tested
                "recall_at_1_at_M_over_N_le_1": 0.85,
                # near_uniform_frac >= 0.5 at M_ratio <= 0.5 across all N
                "near_uniform_frac_at_M_over_N_le_0p5": 0.5,
                # tcft_var_ratio < 0.15 at every cell
                "tcft_var_ratio_max": 0.15,
            },
            "hard_fail": {
                # If recall collapses below 0.50 at any under-cap cell the
                # substrate envelope has not expanded beyond its previous
                # characterization.
                "recall_at_1_at_M_over_N_le_1": 0.50,
                "tcft_var_ratio_max": 0.50,
            },
        },
        "baselines": {
            # Non-substrate backends are skipped by construction.
            "hard_pass": {},
            "hard_fail": {},
        },
    }
