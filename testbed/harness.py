"""Benchmark harness.

run_scenario: load a scenario module, drive a single backend through its
setup/run cycle, time it, write per-scenario JSON.
run_matrix: cross-product of scenarios x backends; writes summary.json under
testbed_data/benchmarks/results/<iso_timestamp>/.
build_backend: factory mapping string name to configured backend instance.

Per CLAUDE.md: ASCII only, no em-dashes, terse.
"""

from __future__ import annotations

import importlib
import json
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from testbed.api import MemoryBackend


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def _json_default(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "tolist"):
        try:
            return obj.tolist()
        except Exception:
            pass
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=_json_default)


# ---------------------------------------------------------------------------
# Backend factory
# ---------------------------------------------------------------------------


_DEFAULT_TESTBED_DATA = Path("testbed_data")


def _testbed_data_root(config: dict) -> Path:
    root = config.get("testbed_data_root")
    if root is None:
        return _DEFAULT_TESTBED_DATA
    return Path(root)


def _config_name(config: dict) -> str:
    return str(config.get("config_name", "default"))


def build_backend(name: str, config: dict) -> MemoryBackend:
    """Construct a configured backend by name.

    config keys consumed:
      - dim (int, default 4096)
      - config_name (str, default "default")
      - testbed_data_root (str/Path, default "testbed_data")
      - substrate: dict of kwargs forwarded to SubstrateMemory.__init__
      - faiss: { index_kind }
      - chroma: { collection_name }
      - sqlite_vec: { }
    """
    nm = name.strip().lower()
    dim = int(config.get("dim", 4096))
    config_name = _config_name(config)
    data_root = _testbed_data_root(config)

    if nm == "dict":
        from testbed.baselines.dict_adapter import DictMemory

        return DictMemory(dim=dim)

    if nm == "faiss":
        from testbed.baselines.faiss_adapter import FaissMemory

        opts = dict(config.get("faiss", {}) or {})
        return FaissMemory(dim=dim, index_kind=opts.get("index_kind", "Flat"))

    if nm == "chroma":
        from testbed.baselines.chroma_adapter import ChromaMemory

        opts = dict(config.get("chroma", {}) or {})
        persist_dir = data_root / "baselines" / "chroma_db" / config_name
        return ChromaMemory(
            persist_dir=persist_dir,
            collection_name=opts.get("collection_name", "testbed"),
            dim=dim,
        )

    if nm == "sqlite_vec":
        from testbed.baselines.sqlite_vec_adapter import SqliteVecMemory

        db_dir = data_root / "baselines" / "sqlite_vec"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / f"{config_name}.db"
        return SqliteVecMemory(db_path=db_path, dim=dim)

    # Substrate + variants. "substrate" is an alias for "substrate_v1".
    from testbed.variants import VARIANT_REGISTRY  # type: ignore

    if nm == "substrate":
        nm = "substrate_v1"

    if nm in VARIANT_REGISTRY:
        cls = VARIANT_REGISTRY[nm]
        opts = dict(config.get("substrate", {}) or {})
        opts.setdefault("N", dim)
        return cls(**opts)

    raise ValueError(
        f"build_backend: unknown backend {name!r} "
        "(expected substrate|substrate_v1|substrate_v2_softdelete|"
        "substrate_v3_kerdock|substrate_v4_double_hebbian|"
        "faiss|chroma|sqlite_vec|dict)"
    )


# ---------------------------------------------------------------------------
# Scenario runner
# ---------------------------------------------------------------------------


def _import_scenario(scenario_name: str):
    """Import a scenario module by short name or fully-qualified path."""
    if "." in scenario_name:
        mod_path = scenario_name
    else:
        mod_path = f"testbed.scenarios.{scenario_name}"
    return importlib.import_module(mod_path)


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def run_scenario(
    scenario_module: Any,
    backend: MemoryBackend,
    config: dict,
    out_dir: Path,
) -> dict:
    """Run one (scenario, backend) pair.

    scenario_module may be either an imported module object or a string name.
    Writes per_scenario/<scenario>_<backend>.json under out_dir.
    Returns the metrics dict (with timing fields added).
    """
    if isinstance(scenario_module, str):
        module = _import_scenario(scenario_module)
    else:
        module = scenario_module
    scenario_name = getattr(module, "__name__", "scenario").rsplit(".", 1)[-1]

    setup_fn = getattr(module, "setup")
    run_fn = getattr(module, "run")
    thresholds_fn = getattr(module, "thresholds", None)

    setup_t0 = time.perf_counter()
    data = setup_fn(config)
    setup_s = time.perf_counter() - setup_t0

    run_t0 = time.perf_counter()
    try:
        metrics = run_fn(backend, data)
        error = None
    except Exception as exc:  # do not let a single backend tank the matrix
        metrics = {"error": f"{type(exc).__name__}: {exc}"}
        error = str(exc)
    run_s = time.perf_counter() - run_t0

    if not isinstance(metrics, dict):
        metrics = {"result": metrics}

    metrics.setdefault("scenario", scenario_name)
    metrics.setdefault("backend", backend.name)
    metrics["setup_s"] = setup_s
    metrics["run_s"] = run_s
    metrics["wall_s"] = setup_s + run_s

    if thresholds_fn is not None:
        try:
            metrics["thresholds"] = thresholds_fn()
        except Exception as exc:
            metrics["thresholds_error"] = str(exc)

    if error is not None:
        metrics["error"] = error

    out_path = out_dir / "per_scenario" / f"{scenario_name}_{backend.name}.json"
    _write_json(out_path, metrics)
    return metrics


def run_matrix(
    scenarios: list[str],
    backends: list[MemoryBackend],
    config: dict,
    out_root: Path,
) -> Path:
    """Run every (scenario, backend) pair and write summary.json.

    Returns the out_dir path (out_root / "results" / <iso_timestamp>).
    """
    out_root = Path(out_root)
    timestamp = _iso_timestamp()
    out_dir = out_root / "results" / timestamp
    (out_dir / "per_scenario").mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict] = []
    for scenario_name in scenarios:
        try:
            module = _import_scenario(scenario_name)
        except Exception as exc:
            print(
                f"[harness] skipping scenario {scenario_name!r}: import failed "
                f"({type(exc).__name__}: {exc})"
            )
            continue
        for backend in backends:
            print(f"[harness] running {scenario_name} on {backend.name}")
            metrics = run_scenario(module, backend, config, out_dir)
            summary_rows.append(metrics)

    summary = {
        "timestamp": timestamp,
        "config": config,
        "scenarios": list(scenarios),
        "backends": [b.name for b in backends],
        "rows": summary_rows,
    }
    _write_json(out_dir / "summary.json", summary)
    print(f"[harness] wrote summary to {out_dir / 'summary.json'}")
    return out_dir
