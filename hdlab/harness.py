"""Shared experiment harness -- re-export shim (promoted 2026-07-28, testbed).

Promotes the 5 highest-reuse exp-trapped helpers to a stable hdlab import
path. THIS IS A RE-EXPORT ONLY: the implementations still live in
experiments/_*.py exactly where they were (their 3653+ existing importers --
`from experiments._seed_checkpoint import ...` etc. -- are UNCHANGED and keep
working). NEW cells should import from `hdlab.harness` instead of reaching
into `experiments/_*` directly, so the harness has one canonical front door
going forward.

Promoted modules (rank = reuse count per notes/promotion_backlog.md
"SHARED HARNESS" + data/capability_registry.jsonl id=shared_harness_seed_checkpoint):
  - _seed_checkpoint      (3653+ importers) -- seed/checkpoint/partial-result
                            boilerplate every exp cell needs (get_output_dir,
                            write_metrics, record_gate, resumable_seeds, ...).
  - _validity_preflight   (97 importers)    -- can-fail / positive-control /
                            gate-exercised preflight assertions.
  - _multi_hop_mechanisms (67 importers)    -- path-B/D/E multihop derivation
                            mechanisms over a bound HRR codebook.
  - _cell_heartbeat       (50 importers)    -- long-run cell heartbeat emission.
  - _metric_battery       (50 importers)    -- substrate capacity/retention
                            metric battery (above-thresh, iso, retention, ...).

Each module is also exposed by name (harness.seed_checkpoint, etc.) for full
access beyond the flat re-exports below.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments import _seed_checkpoint as seed_checkpoint  # noqa: E402
from experiments import _validity_preflight as validity_preflight  # noqa: E402
from experiments import _cell_heartbeat as cell_heartbeat  # noqa: E402
from experiments import _metric_battery as metric_battery  # noqa: E402
from experiments import _multi_hop_mechanisms as multi_hop_mechanisms  # noqa: E402

# ---- flat re-exports of the most commonly used top-level symbols ---------- #

from experiments._seed_checkpoint import (  # noqa: E402,F401
    get_output_dir,
    write_metrics,
    record_gate,
    resumable_seeds,
    write_partial,
    write_partial_key,
    load_partial_key,
    aggregate_partials,
    clear_partials,
    list_completed_keys,
    assert_discriminator_fires,
    VacuousSmokeError,
)
from experiments._validity_preflight import (  # noqa: E402,F401
    run_validity_preflight,
    ValidityPreflightError,
    assert_positive_control_passes,
    assert_metric_moves,
    assert_negative_control_fails_with_margin,
    assert_real_code_path_exercised,
    assert_full_gates_exercised_at_selftest,
)
from experiments._cell_heartbeat import emit_heartbeat, CellHeartbeat  # noqa: E402,F401
from experiments._metric_battery import (  # noqa: E402,F401
    make_substrate,
    run_battery,
    metric_above_thresh_frac,
    metric_max_iso,
    metric_retention,
    metric_edit_then_retrieve,
    metric_retrieval_latency_ns,
    metric_kf1_sharpness,
)
from experiments._multi_hop_mechanisms import (  # noqa: E402,F401
    build_shared,
    path_b_run,
    path_d_run,
    path_e_run,
    run_all_paths_sequential,
    run_all_paths_joint,
)

__all__ = [
    "seed_checkpoint", "validity_preflight", "cell_heartbeat", "metric_battery",
    "multi_hop_mechanisms",
    "get_output_dir", "write_metrics", "record_gate", "resumable_seeds",
    "write_partial", "write_partial_key", "load_partial_key", "aggregate_partials",
    "clear_partials", "list_completed_keys", "assert_discriminator_fires",
    "VacuousSmokeError",
    "run_validity_preflight", "ValidityPreflightError",
    "assert_positive_control_passes", "assert_metric_moves",
    "assert_negative_control_fails_with_margin", "assert_real_code_path_exercised",
    "assert_full_gates_exercised_at_selftest",
    "emit_heartbeat", "CellHeartbeat",
    "make_substrate", "run_battery", "metric_above_thresh_frac", "metric_max_iso",
    "metric_retention", "metric_edit_then_retrieve", "metric_retrieval_latency_ns",
    "metric_kf1_sharpness",
    "build_shared", "path_b_run", "path_d_run", "path_e_run",
    "run_all_paths_sequential", "run_all_paths_joint",
]


def _selftest() -> None:
    """Import-only smoke: every re-export resolves and the 5 submodules are reachable."""
    for name in __all__:
        assert name in globals(), f"hdlab.harness re-export missing: {name}"
    assert callable(get_output_dir)
    assert callable(run_validity_preflight)
    assert callable(emit_heartbeat)
    assert callable(run_battery)
    assert callable(build_shared)
    print("[selftest] hdlab.harness re-export shim OK (5 modules, %d flat names)" % len(__all__))


if __name__ == "__main__":
    _selftest()
