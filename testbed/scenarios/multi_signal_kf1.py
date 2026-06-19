"""Scenario: multi_signal_kf1 (Path-15 multi-signal KF-1 hallucination detection).

Probes the Path-15 hypothesis: KF-1's hallucination MECHANISM shifts across
operating regimes. At low M/N the posterior-entropy flag fires reliably; at
M/N near saturation the response is dominated by competing stored facts,
posterior entropy looks ordinary, and the substrate's correct-rejection
behavior shows up via different-key-high-confidence rather than near-uniform.
A composite of 4 internal signals captures the rejection regardless of which
regime dominates.

The 4 signals (all populated on RetrievalResult.hallu_signals by
SubstrateMemory at retrieve time):

  (a) posterior_entropy_flag: (max_prob * C) < 50  (existing KF-1 single-
      signal flag, preserved bit-for-bit by substrate_memory.retrieve).
  (b) low_norm_flag: response_norm < 0.5 * median_stored_response_norm.
      Low ||W @ q|| -> the substrate did not activate any stored fact in
      proportion to a typical stored retrieval, so the query is OOS.
  (c) low_concentration_flag: top_2_prob_ratio < 2.0. When two codebook
      atoms have nearly-equal softmax mass the response is split across
      multiple stored values, indicating an ambiguous / OOS read.
  (d) high_distance_flag: min_dist_to_stored = 1 - max cosine over stored
      key atoms > 0.5. Query atom geometrically far from any stored key.

  composite_flag: at least 2 of the 4 individual flags fire.
  composite_score: weighted sum in [0, 1] using heuristic weights
                   0.4*posterior + 0.3*low_norm + 0.2*low_conc + 0.1*high_dist.

Heuristic note: per feedback-dont-overextend-theorems, the composite_score
weights are NOT derived from first principles; they reflect an initial
ranking of signal-strength (posterior most informative, geometric-distance
least). The composite_flag is the more honest top-line summary. Re-tune
weights per deployment when scenario evidence shows drift.

Sweep:
  M/N in {0.25, 0.5, 1.0, 2.0}. For each ratio:
    1. Store M facts (atoms drawn from a deterministic RNG).
    2. Sample n_oos OOS queries (disjoint from stored).
    3. Sample n_stored stored queries (subset of stored, for false-positive).
    4. For both OOS and stored panels, compute per-signal fire rate and
       composite_flag fire rate.

HARD_PASS (definition of done, pre-registered):
  composite fire rate on OOS >= 0.90 at every M/N ratio,
  AND composite false positive rate on stored <= 0.10 at every ratio.

HARD_FAIL:
  composite fire rate on OOS < 0.60 at any M/N ratio
  OR composite false positive rate on stored > 0.30 at any ratio.

Honest framing: under the original spec, posterior_entropy alone reaches
high fire rates only at low M/N; at high M/N the substrate increasingly
returns a "wrong stored key with high confidence" which posterior entropy
does NOT flag. The composite is expected to hold up because at least one
of low_norm, low_concentration, or high_distance fires in that regime.

This scenario is substrate-only by construction. Baselines do not populate
hallu_signals (their retrieval result has hallu_signals=None) so the
scenario returns an empty per_subrun for non-substrate backends with a
clear marker.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from testbed.api import MemoryBackend


_SIGNAL_KEYS = (
    "posterior_entropy",
    "low_norm",
    "low_concentration",
    "high_distance",
)


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    dim = int(config.get("dim", 4096))
    N = int(config.get("N", dim))
    seed = _first_seed(config)
    n_oos = int(config.get("multi_signal_n_oos", config.get("hallu_n_oos", 200)))
    n_stored = int(
        config.get("multi_signal_n_stored", config.get("hallu_n_oos", 200))
    )
    ratios = list(
        config.get(
            "multi_signal_M_per_N",
            config.get("hallu_M_fracs", [0.25, 0.5, 1.0, 2.0]),
        )
    )
    codebook_C = int(config.get("codebook_C", 4 * N))
    return {
        "dim": dim,
        "N": N,
        "seed": seed,
        "n_oos": n_oos,
        "n_stored": n_stored,
        "ratios": ratios,
        "codebook_C": codebook_C,
    }


def _backend_factory(backend: MemoryBackend):
    """Return a callable that produces a fresh substrate instance.

    The scenario is substrate-only by construction (multi-signal panel is
    only emitted by SubstrateMemory). For non-substrate backends we still
    return a factory so the scenario degrades cleanly to a no-result run.
    """
    cls = type(backend)

    def make() -> MemoryBackend:
        if backend.name == "substrate" or backend.name.startswith("substrate_v"):
            kwargs: dict[str, Any] = {}
            for attr in (
                "N",
                "codebook_kind",
                "codebook_scale",
                "beta",
                "hallu_threshold",
                "device",
            ):
                if hasattr(backend, attr):
                    kwargs[attr] = getattr(backend, attr)
            return cls(**kwargs)
        if backend.name == "dict":
            return cls(dim=getattr(backend, "dim", None))
        # Fallback.
        return cls()

    return make


def _per_signal_counters() -> dict:
    return {k: 0 for k in _SIGNAL_KEYS}


def _is_substrate_backend(backend: MemoryBackend) -> bool:
    return (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )


def run(backend: MemoryBackend, data: dict) -> dict:
    dim = int(data["dim"])
    N = int(data["N"])
    seed = int(data["seed"])
    n_oos = int(data["n_oos"])
    n_stored = int(data["n_stored"])
    ratios = list(data["ratios"])

    is_substrate = _is_substrate_backend(backend)
    if not is_substrate:
        # Baselines do not populate hallu_signals. The scenario surfaces a
        # marker rather than fabricating numbers from None.
        return {
            "scenario": "multi_signal_kf1",
            "backend": backend.name,
            "substrate_only_scenario": True,
            "note": (
                "multi_signal_kf1 measures substrate-internal hallu_signals "
                "that baselines do not populate. Run with backend=substrate."
            ),
            "per_subrun": [],
        }

    factory = _backend_factory(backend)
    per_subrun: list[dict] = []

    for ratio in ratios:
        M = max(1, int(round(ratio * N)))
        rng_store = np.random.default_rng(seed + 31000 + int(ratio * 10_000))
        rng_oos = np.random.default_rng(seed + 32000 + int(ratio * 10_000))

        stored_vecs = _make_vecs(rng_store, M, dim)
        stored_ids = [f"ms_r{int(ratio * 1000):04d}_{i:06d}" for i in range(M)]
        oos_vecs = _make_vecs(rng_oos, n_oos, dim)

        sub_backend = factory()
        # Use store_batch where available for speed at higher M.
        try:
            sub_backend.store_batch(
                [(stored_ids[i], stored_vecs[i], f"v_{i}") for i in range(M)]
            )
        except Exception:
            for i in range(M):
                sub_backend.store(stored_ids[i], stored_vecs[i], f"v_{i}")

        # --- OOS panel: each signal should fire (true positive) ---
        oos_per_signal = _per_signal_counters()
        oos_composite = 0
        oos_composite_scores: list[float] = []
        oos_posterior_alone = 0

        # Batch retrieve OOS queries.
        try:
            oos_results = sub_backend.retrieve_batch(oos_vecs, k=1)
        except Exception:
            oos_results = [sub_backend.retrieve(q, k=1) for q in oos_vecs]
        for res in oos_results:
            hs = res.hallu_signals
            if hs is None:
                continue
            if hs.get("posterior_entropy_flag"):
                oos_per_signal["posterior_entropy"] += 1
                oos_posterior_alone += 1
            if hs.get("low_norm_flag"):
                oos_per_signal["low_norm"] += 1
            if hs.get("low_concentration_flag"):
                oos_per_signal["low_concentration"] += 1
            if hs.get("high_distance_flag"):
                oos_per_signal["high_distance"] += 1
            if hs.get("composite_flag"):
                oos_composite += 1
            oos_composite_scores.append(float(hs.get("composite_score", 0.0)))

        # --- Stored panel: signals should NOT fire (false positive rate) ---
        n_stored_use = min(n_stored, M)
        if n_stored_use > 0:
            # Deterministic stratified subsample of stored vecs.
            step = max(1, M // n_stored_use)
            stored_query_idx = list(range(0, M, step))[:n_stored_use]
            stored_query_vecs = stored_vecs[stored_query_idx]
        else:
            stored_query_vecs = np.zeros((0, dim), dtype=np.float32)

        stored_per_signal = _per_signal_counters()
        stored_composite = 0
        stored_composite_scores: list[float] = []
        stored_posterior_alone = 0

        if n_stored_use > 0:
            try:
                stored_results = sub_backend.retrieve_batch(
                    stored_query_vecs, k=1
                )
            except Exception:
                stored_results = [
                    sub_backend.retrieve(q, k=1) for q in stored_query_vecs
                ]
            for res in stored_results:
                hs = res.hallu_signals
                if hs is None:
                    continue
                if hs.get("posterior_entropy_flag"):
                    stored_per_signal["posterior_entropy"] += 1
                    stored_posterior_alone += 1
                if hs.get("low_norm_flag"):
                    stored_per_signal["low_norm"] += 1
                if hs.get("low_concentration_flag"):
                    stored_per_signal["low_concentration"] += 1
                if hs.get("high_distance_flag"):
                    stored_per_signal["high_distance"] += 1
                if hs.get("composite_flag"):
                    stored_composite += 1
                stored_composite_scores.append(
                    float(hs.get("composite_score", 0.0))
                )

        def _rate(numer: int, denom: int) -> float:
            return float(numer / denom) if denom > 0 else 0.0

        per_subrun.append({
            "M_over_N": float(ratio),
            "M": int(M),
            "n_oos": int(n_oos),
            "n_stored_probed": int(n_stored_use),
            "oos_per_signal_fire_rate": {
                k: _rate(oos_per_signal[k], n_oos) for k in _SIGNAL_KEYS
            },
            "oos_composite_fire_rate": _rate(oos_composite, n_oos),
            "oos_posterior_entropy_alone_rate": _rate(
                oos_posterior_alone, n_oos
            ),
            "oos_mean_composite_score": (
                float(np.mean(oos_composite_scores))
                if oos_composite_scores else 0.0
            ),
            "stored_per_signal_fire_rate": {
                k: _rate(stored_per_signal[k], n_stored_use)
                for k in _SIGNAL_KEYS
            },
            "stored_composite_fire_rate": _rate(
                stored_composite, n_stored_use
            ),
            "stored_posterior_entropy_alone_rate": _rate(
                stored_posterior_alone, n_stored_use
            ),
            "stored_mean_composite_score": (
                float(np.mean(stored_composite_scores))
                if stored_composite_scores else 0.0
            ),
        })

    # Aggregate gate values across sub-runs (worst-cell convention).
    if per_subrun:
        min_composite_oos = min(
            s["oos_composite_fire_rate"] for s in per_subrun
        )
        max_composite_stored = max(
            s["stored_composite_fire_rate"] for s in per_subrun
        )
        min_posterior_oos = min(
            s["oos_posterior_entropy_alone_rate"] for s in per_subrun
        )
        max_posterior_stored = max(
            s["stored_posterior_entropy_alone_rate"] for s in per_subrun
        )
    else:
        min_composite_oos = 0.0
        max_composite_stored = 0.0
        min_posterior_oos = 0.0
        max_posterior_stored = 0.0

    composite_minus_posterior_oos = float(
        min_composite_oos - min_posterior_oos
    )
    hard_pass = bool(
        min_composite_oos >= 0.90 and max_composite_stored <= 0.10
    )
    hard_fail = bool(
        min_composite_oos < 0.60 or max_composite_stored > 0.30
    )

    return {
        "scenario": "multi_signal_kf1",
        "backend": backend.name,
        "per_subrun": per_subrun,
        "min_oos_composite_fire_rate": min_composite_oos,
        "max_stored_composite_fire_rate": max_composite_stored,
        "min_oos_posterior_alone_rate": min_posterior_oos,
        "max_stored_posterior_alone_rate": max_posterior_stored,
        "composite_minus_posterior_oos_at_worst_regime": (
            composite_minus_posterior_oos
        ),
        "hard_pass": hard_pass,
        "hard_fail": hard_fail,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "min_oos_composite_fire_rate_ge": 0.90,
                "max_stored_composite_fire_rate_le": 0.10,
            },
            "hard_fail": {
                "min_oos_composite_fire_rate_lt": 0.60,
                "max_stored_composite_fire_rate_gt": 0.30,
            },
        },
        "baselines": {
            "hard_pass": {"substrate_only_scenario": True},
            "hard_fail": {"substrate_only_scenario": True},
        },
    }
