"""CLI entry point for the substrate memory testbed.

Subcommands:
    run    --scenario <name|all> --backend <name|all> --config <path> [--out-dir <path>]
    report --run-dir <path>
    audit  --backend <name> --state-dir <path>
    smoke  --backend <comma-sep names>

`smoke` is self-contained: it builds a tiny config, runs point_recall for
each named backend, and writes a one-page report.md. It is the Workstream E
definition-of-done gate.

`run` and `audit` defer to testbed.harness.run_matrix when available; if
harness.py has not yet landed (parallel workstream) `run` falls back to a
minimal inline matrix runner that produces a compatible summary.json.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import json
import sys
import time
import traceback
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


_SCENARIO_NAMES = [
    "point_recall",
    "edit_isolation",
    "deletion_verify",
    "hallu_detect",
    "continual_4stage",
    "storage_latency",
    "large_M_constant_cost",
    "audit_chain_validation",
    "multi_substrate_sharding",
    "write_heavy_stream",
    "edit_heavy_stream",
    "hot_path_skew",
    "mixed_crud_workload",
    "large_N_envelope",
    "approx_retrieve_sweep",
    "multi_signal_kf1",
    "factorized_vs_dense",
    "hierarchical_capacity",
    "cached_hot_path",
]


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _load_config(path: Path) -> dict:
    """Read a YAML file. Fall back to a minimal hand parser if PyYAML missing."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        return _minimal_yaml(text)


def _coerce_scalar(s: str) -> Any:
    s = s.strip()
    if s == "" or s.lower() == "null" or s == "~":
        return None
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        pass
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(x) for x in inner.split(",")]
    if s.startswith(("'", '"')) and s.endswith(("'", '"')):
        return s[1:-1]
    return s


def _minimal_yaml(text: str) -> dict:
    """Tiny YAML subset: key: value, lists as [a, b], list-of-strings via dash.
    No nesting beyond one level of dash-list. Sufficient for our configs.
    """
    out: dict[str, Any] = {}
    current_list_key: Optional[str] = None
    current_list: list[Any] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                continue
            current_list.append(_coerce_scalar(line[4:].strip()))
            continue
        if current_list_key is not None:
            out[current_list_key] = current_list
            current_list_key = None
            current_list = []
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                current_list_key = key
                current_list = []
            else:
                out[key] = _coerce_scalar(val)
    if current_list_key is not None:
        out[current_list_key] = current_list
    return out


# ---------------------------------------------------------------------------
# Backend factory
# ---------------------------------------------------------------------------

def _build_backend(name: str, config: dict):
    dim = int(config.get("dim", 4096))
    # substrate + variants: name in {substrate, substrate_v1, substrate_v2_softdelete,
    # substrate_v3_kerdock, substrate_v4_double_hebbian, substrate_sharded}.
    # "substrate" aliases v1.
    nm = name.strip().lower() if isinstance(name, str) else name
    if nm == "substrate_sharded":
        try:
            from testbed.variants import VARIANT_REGISTRY  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"substrate variants not available: {exc}. "
                "Expected testbed/variants/__init__.py."
            ) from exc
        cls = VARIANT_REGISTRY["substrate_sharded"]
        opts = dict(config.get("sharded", {}) or {})
        opts.setdefault("N", int(config.get("N", dim)))
        opts.setdefault("K_shards", int(config.get("shard_K", 10)))
        opts.setdefault(
            "codebook_C", int(config.get("shard_codebook_C", 8192))
        )
        opts.setdefault("codebook_kind", config.get("codebook_kind", "bsc"))
        opts.setdefault("beta", float(config.get("beta", 32.0)))
        opts.setdefault(
            "hallu_threshold", float(config.get("hallu_threshold", 0.5))
        )
        opts.setdefault(
            "shared_codebook", bool(config.get("shard_shared_codebook", True))
        )
        opts.setdefault("routing", "hash")
        opts.setdefault("device", str(config.get("substrate_device", "cpu")))
        seeds = config.get("seeds") or [0]
        opts.setdefault("seed", int(seeds[0]) if seeds else 0)
        return cls(**opts)
    if nm == "substrate_hierarchical":
        try:
            from testbed.variants import VARIANT_REGISTRY  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"substrate variants not available: {exc}. "
                "Expected testbed/variants/__init__.py."
            ) from exc
        cls = VARIANT_REGISTRY["substrate_hierarchical"]
        opts = dict(config.get("hierarchical", {}) or {})
        opts.setdefault("N_top", int(config.get("hier_N_top", 512)))
        opts.setdefault("N_leaf", int(config.get("hier_N_leaf",
                                                 config.get("N", dim))))
        opts.setdefault("K_topics", int(config.get("hier_K_topics", 10)))
        opts.setdefault(
            "codebook_C_top", int(config.get("hier_codebook_C_top", 2048))
        )
        opts.setdefault(
            "codebook_C_leaf", int(config.get("hier_codebook_C_leaf", 8192))
        )
        opts.setdefault("codebook_kind", config.get("codebook_kind", "bsc"))
        opts.setdefault("codebook_scale",
                        int(config.get("codebook_scale", 4)))
        opts.setdefault("beta", float(config.get("beta", 32.0)))
        opts.setdefault(
            "hallu_threshold", float(config.get("hallu_threshold", 0.5))
        )
        m_cap = config.get("hier_M_capacity_per_leaf")
        if m_cap is not None:
            opts.setdefault("M_capacity_per_leaf", int(m_cap))
        opts.setdefault("routing", "hash")
        opts.setdefault("device", str(config.get("substrate_device", "cpu")))
        seeds = config.get("seeds") or [0]
        opts.setdefault("seed", int(seeds[0]) if seeds else 0)
        return cls(**opts)
    if nm == "substrate_cached":
        try:
            from testbed.variants import VARIANT_REGISTRY  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"substrate variants not available: {exc}."
            ) from exc
        cls = VARIANT_REGISTRY["substrate_cached"]
        cached_opts = dict(config.get("cached", {}) or {})
        kwargs = {
            "N": int(config.get("N", 4096)),
            "codebook_kind": str(config.get("codebook_kind", "bsc")),
            "codebook_scale": int(config.get("codebook_scale", 4)),
            "beta": float(config.get("beta", 32.0)),
            "hallu_threshold": float(config.get("hallu_threshold", 0.5)),
            "device": str(config.get("substrate_device", "cpu")),
            "cache_size": int(cached_opts.get("cache_size", 1000)),
            "eviction_policy": str(cached_opts.get("eviction_policy", "lru")),
        }
        seeds = config.get("seeds") or [0]
        kwargs["seed"] = int(seeds[0]) if seeds else 0
        m_hint = config.get("codebook_M_hint")
        if (m_hint is None) and bool(config.get("codebook_M_hint_auto", False)):
            candidates = [
                int(config.get("M_total", 0) or 0),
                int(config.get("hot_path_M", 0) or 0),
            ]
            m_hint = max(candidates) if candidates else 0
        if m_hint:
            try:
                kwargs["codebook_M_hint"] = int(m_hint)
            except (TypeError, ValueError):
                pass
        return cls(**kwargs)
    if nm == "substrate" or nm.startswith("substrate_v") or nm == "substrate_factorized":
        try:
            from testbed.variants import VARIANT_REGISTRY  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"substrate variants not available: {exc}. "
                "Expected testbed/variants/__init__.py."
            ) from exc
        resolved = "substrate_v1" if nm == "substrate" else nm
        if resolved not in VARIANT_REGISTRY:
            raise ValueError(
                f"unknown substrate variant {name!r} "
                f"(registered: {sorted(VARIANT_REGISTRY)})"
            )
        cls = VARIANT_REGISTRY[resolved]
        # v3_kerdock defaults its kind to 'kerdock' internally; do NOT force
        # codebook_kind from the config for that variant.
        cfg_kind = str(config.get("codebook_kind", "bsc"))
        if resolved == "substrate_v3_kerdock":
            cfg_kind = "kerdock"
        kwargs = {
            "N": int(config.get("N", 4096)),
            "codebook_kind": cfg_kind,
            "codebook_scale": int(config.get("codebook_scale", 4)),
            "beta": float(config.get("beta", 32.0)),
            "hallu_threshold": float(config.get("hallu_threshold", 0.5)),
            "device": str(config.get("substrate_device", "cpu")),
        }
        # Factorized needs M_capacity at construction.
        if resolved == "substrate_factorized":
            m_cap = config.get("M_capacity")
            if m_cap is None:
                # Default to max stored M across scenario knobs, else N.
                candidates = [
                    int(config.get("M_total", 0) or 0),
                    int(config.get("edit_isolation_M", 0) or 0),
                    int(config.get("deletion_M", 0) or 0),
                    int(config.get("continual_M", 0) or 0),
                ]
                ms_list = config.get("storage_latency_Ms") or []
                candidates += [int(x) for x in ms_list if isinstance(x, (int, float))]
                m_cap = max(candidates) if any(candidates) else int(config.get("N", 4096))
            kwargs["M_capacity"] = int(m_cap)
        # Shine plan A.3.1: pass codebook_M_hint when present. Auto-derive from
        # the largest scenario M when codebook_M_hint_auto is True. v1 reference
        # accepts the kwarg; older variants do not, so pass it conditionally.
        m_hint = config.get("codebook_M_hint")
        if (m_hint is None) and bool(config.get("codebook_M_hint_auto", False)):
            candidates = [
                int(config.get("M_total", 0) or 0),
                int(config.get("edit_isolation_M", 0) or 0),
                int(config.get("deletion_M", 0) or 0),
                int(config.get("continual_M", 0) or 0),
            ]
            ms_list = config.get("storage_latency_Ms") or []
            candidates += [int(x) for x in ms_list if isinstance(x, (int, float))]
            large_ms = config.get("large_M_Ms") or []
            candidates += [int(x) for x in large_ms if isinstance(x, (int, float))]
            m_hint = max(candidates) if candidates else 0
        if m_hint:
            try:
                kwargs["codebook_M_hint"] = int(m_hint)
            except (TypeError, ValueError):
                pass
        try:
            return cls(**kwargs)
        except TypeError:
            # Variant subclass that does not accept codebook_M_hint kwarg.
            kwargs.pop("codebook_M_hint", None)
            return cls(**kwargs)
    if name == "faiss":
        from testbed.baselines.faiss_adapter import FaissMemory
        return FaissMemory(dim=dim)
    if name == "dict":
        from testbed.baselines.dict_adapter import DictMemory
        return DictMemory(dim=dim)
    if name == "sqlite_vec":
        try:
            from testbed.baselines.sqlite_vec_adapter import SqliteVecMemory  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"sqlite_vec backend not yet available: {exc}. "
                "Workstream B ships testbed/baselines/sqlite_vec_adapter.py."
            ) from exc
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="testbed_sqlite_"))
        return SqliteVecMemory(db_path=tmp / "scratch.db", dim=dim)
    if name == "chroma":
        try:
            from testbed.baselines.chroma_adapter import ChromaMemory  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"chroma backend not yet available: {exc}. "
                "Workstream B ships testbed/baselines/chroma_adapter.py."
            ) from exc
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="testbed_chroma_"))
        return ChromaMemory(persist_dir=tmp)
    raise ValueError(f"unknown backend: {name!r}")


# ---------------------------------------------------------------------------
# Scenario module loader
# ---------------------------------------------------------------------------

def _scenario_module(name: str):
    return importlib.import_module(f"testbed.scenarios.{name}")


def _json_safe(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if is_dataclass(obj):
        return _json_safe(asdict(obj))
    try:
        import numpy as np  # type: ignore
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return obj.item()
        if isinstance(obj, np.bool_):
            return bool(obj)
    except ImportError:
        pass
    return str(obj)


# ---------------------------------------------------------------------------
# Inline matrix runner (used when harness.py isn't present)
# ---------------------------------------------------------------------------

def _inline_run_matrix(scenarios: list[str], backends: list[str],
                       config: dict, out_root: Path,
                       cli_command: str) -> Path:
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    run_dir = Path(out_root) / "results" / timestamp
    (run_dir / "per_scenario").mkdir(parents=True, exist_ok=True)

    results_by_backend: dict[str, dict] = {b: {} for b in backends}
    thresholds_by_scenario: dict[str, dict] = {}
    errors: list[dict] = []

    for s in scenarios:
        try:
            mod = _scenario_module(s)
        except ImportError as exc:
            errors.append({"scenario": s, "stage": "import", "error": str(exc)})
            continue
        try:
            thresholds_by_scenario[s] = mod.thresholds()
        except Exception as exc:
            thresholds_by_scenario[s] = {}
            errors.append({"scenario": s, "stage": "thresholds", "error": str(exc)})
        try:
            data = mod.setup(config)
        except Exception as exc:
            errors.append({"scenario": s, "stage": "setup",
                           "error": f"{exc}\n{traceback.format_exc()}"})
            continue
        for b in backends:
            try:
                backend = _build_backend(b, config)
            except Exception as exc:
                errors.append({"scenario": s, "backend": b, "stage": "build",
                               "error": str(exc)})
                continue
            try:
                t0 = time.perf_counter_ns()
                metrics = mod.run(backend, data)
                wall_ns = time.perf_counter_ns() - t0
                metrics = _json_safe(metrics)
                metrics["wall_s"] = wall_ns / 1e9
            except Exception as exc:
                errors.append({"scenario": s, "backend": b, "stage": "run",
                               "error": f"{exc}\n{traceback.format_exc()}"})
                continue
            results_by_backend[b][s] = metrics
            per_file = run_dir / "per_scenario" / f"{s}_{b}.json"
            try:
                with open(per_file, "w", encoding="utf-8") as f:
                    json.dump(metrics, f, indent=2)
            except OSError:
                pass

    summary = {
        "timestamp": timestamp,
        "cli_command": cli_command,
        "config": _json_safe(config),
        "scenarios": scenarios,
        "backends": backends,
        "results_by_backend": _json_safe(results_by_backend),
        "thresholds_by_scenario": _json_safe(thresholds_by_scenario),
        "errors": errors,
    }
    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return run_dir


def _dispatch_run_matrix(scenarios: list[str], backends: list[str],
                         config: dict, out_root: Path,
                         cli_command: str) -> Path:
    """Run the (scenario x backend) matrix.

    The Workstream-B harness emits a different summary.json shape (rows
    list) than the report module expects (results_by_backend dict). To
    keep report.render_markdown happy we always go through the inline
    runner. The harness module can still be used directly by other code
    paths that want its rows-shaped output.
    """
    return _inline_run_matrix(scenarios, backends, config, out_root, cli_command)


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _resolve_list(arg_value: str, all_values: list[str]) -> list[str]:
    if arg_value == "all":
        return list(all_values)
    return [s.strip() for s in arg_value.split(",") if s.strip()]


def _cmd_run(args: argparse.Namespace) -> int:
    config = _load_config(Path(args.config))
    cfg_scenarios = config.get("scenarios", _SCENARIO_NAMES)
    cfg_backends = config.get("backends", ["dict"])
    scenarios = _resolve_list(args.scenario, cfg_scenarios)
    backends = _resolve_list(args.backend, cfg_backends)

    out_root = Path(args.out_dir) if args.out_dir else Path(
        config.get("out_root", "testbed_data/benchmarks"))

    cli_command = "python -m testbed " + " ".join(sys.argv[1:])
    run_dir = _dispatch_run_matrix(scenarios, backends, config, out_root, cli_command)

    from testbed import report as report_mod
    md = report_mod.render_markdown(run_dir / "summary.json")
    print(f"[run] wrote {run_dir}")
    print(f"[run] report: {run_dir / 'report.md'}")
    print(f"[run] {len(md)} chars of markdown emitted")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    summary = run_dir / "summary.json"
    if not summary.exists():
        print(f"[report] no summary.json at {summary}", file=sys.stderr)
        return 2
    from testbed import report as report_mod
    md = report_mod.render_markdown(summary)
    print(md)
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    name = args.backend
    state_dir = Path(args.state_dir)
    config: dict = {}
    cfg_yaml = state_dir / "config.yaml"
    if cfg_yaml.exists():
        try:
            config = _load_config(cfg_yaml)
        except Exception:
            config = {}
    try:
        backend = _build_backend(name, config)
    except Exception as exc:
        print(f"[audit] failed to build backend {name!r}: {exc}", file=sys.stderr)
        return 3
    try:
        backend.load(state_dir)
    except Exception as exc:
        print(f"[audit] backend.load failed: {exc}", file=sys.stderr)
        return 4
    rep = backend.audit()
    if dataclasses.is_dataclass(rep):
        payload = dataclasses.asdict(rep)
    else:
        payload = {"summary": str(rep)}
    payload = _json_safe(payload)
    out_path = state_dir / "audit.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass
    print(json.dumps(payload, indent=2))
    print(f"[audit] wrote {out_path}")
    return 0


def _smoke_config() -> dict:
    return {
        "N": 512,
        "dim": 512,
        "codebook_kind": "bsc",
        "codebook_C": 2048,
        "codebook_scale": 4,
        "beta": 32.0,
        "hallu_threshold": 0.5,
        "M_total": 64,
        "edit_isolation_M": 8,
        "deletion_M": 8,
        "deletion_k_probes": 4,
        "hallu_M_fracs": [0.25, 0.5],
        "hallu_n_oos": 64,
        "continual_M": 16,
        "storage_latency_Ms": [64],
        "storage_latency_n_queries": 16,
        "seeds": [7],
    }


def _cmd_smoke(args: argparse.Namespace) -> int:
    requested = [s.strip() for s in args.backend.split(",") if s.strip()]
    if not requested:
        print("[smoke] no backends listed", file=sys.stderr)
        return 2
    config = _smoke_config()
    out_root = Path(args.out_dir) if args.out_dir else Path("testbed_data/benchmarks")
    scenarios = ["point_recall"]
    cli_command = "python -m testbed " + " ".join(sys.argv[1:])
    t0 = time.perf_counter_ns()
    run_dir = _inline_run_matrix(scenarios, requested, config, out_root, cli_command)
    wall_s = (time.perf_counter_ns() - t0) / 1e9

    summary_path = run_dir / "summary.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    bad = 0
    for b in requested:
        r = summary["results_by_backend"].get(b, {}).get("point_recall")
        if not r:
            print(f"[smoke] backend {b}: NO RESULT (build or run failure)")
            bad += 1
            continue
        r1 = r.get("recall_at_1", 0.0)
        is_substrate = (
            (b == "substrate")
            or b.startswith("substrate_v")
            or b == "substrate_sharded"
            or b == "substrate_factorized"
            or b == "substrate_hierarchical"
            or b == "substrate_cached"
        )
        ok = (r1 >= 0.5) if is_substrate else (r1 >= 0.95)
        flag = "PASS" if ok else "FAIL"
        print(f"[smoke] backend {b}: recall_at_1={r1:.4f} [{flag}]")
        if not ok:
            bad += 1

    from testbed import report as report_mod
    report_mod.render_markdown(summary_path)
    print(f"[smoke] report: {run_dir / 'report.md'}")
    print(f"[smoke] wall {wall_s:.2f}s; errors={len(summary.get('errors', []))}; failures={bad}")

    if summary.get("errors"):
        for e in summary["errors"][:5]:
            short = (e.get("error") or "").splitlines()[0]
            print(f"[smoke] error: scenario={e.get('scenario')} backend={e.get('backend')} stage={e.get('stage')} :: {short}")

    if wall_s > 30.0:
        print(f"[smoke] WARNING wall {wall_s:.2f}s > 30s budget")

    return 0 if bad == 0 else 1


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="testbed",
                                description="Substrate memory testbed CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run a (scenario, backend) matrix")
    p_run.add_argument("--scenario", required=True,
                       help="scenario name or 'all' or comma-separated names")
    p_run.add_argument("--backend", required=True,
                       help="backend name or 'all' or comma-separated names")
    p_run.add_argument("--config", required=True, help="path to YAML config")
    p_run.add_argument("--out-dir", default=None,
                       help="override out_root (default: config[out_root])")
    p_run.set_defaults(func=_cmd_run)

    p_rep = sub.add_parser("report", help="render markdown from a run dir")
    p_rep.add_argument("--run-dir", required=True)
    p_rep.set_defaults(func=_cmd_report)

    p_aud = sub.add_parser("audit", help="audit a persisted backend state")
    p_aud.add_argument("--backend", required=True)
    p_aud.add_argument("--state-dir", required=True)
    p_aud.set_defaults(func=_cmd_audit)

    p_sm = sub.add_parser("smoke", help="tiny sanity sweep gate")
    p_sm.add_argument("--backend", required=True,
                      help="comma-separated backend names, e.g. dict,faiss,sqlite_vec")
    p_sm.add_argument("--out-dir", default=None)
    p_sm.set_defaults(func=_cmd_smoke)

    p_sw = sub.add_parser("sweep",
                          help="cross-product parameter sweep with response surface")
    p_sw.add_argument("--grid", required=True,
                      help="path to sweep YAML (base_config + grid)")
    p_sw.add_argument("--backend", default=None,
                      help="comma-separated backend names (overrides YAML)")
    p_sw.add_argument("--out-dir", default=None,
                      help="override out_root (default: testbed_data/benchmarks)")
    from testbed.sweep import cmd_sweep as _cmd_sweep
    p_sw.set_defaults(func=_cmd_sweep)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
