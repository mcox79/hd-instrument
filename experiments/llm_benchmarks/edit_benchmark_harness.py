"""LLM Editing Benchmark Harness: substrate vs ROME / MEMIT / AlphaEdit / MEND.

SCAFFOLD ONLY: this file defines abstract interfaces (EditDataset, EditMethod),
their concrete subclasses with stub load/edit methods, the evaluate_edit driver,
and a CLI. The full implementations land in stages per
notes/llm_benchmark_harness_2026-05-29.md.

Conventions: ASCII-only, forward slashes in paths, atomic JSON writes,
HDLAB_EXP_NAME honored, all randomness via passed torch.Generator. Per CLAUDE.md.

CLI:
    python -m experiments.llm_benchmarks.edit_benchmark_harness \\
        --method substrate --dataset counterfact \\
        --N 4096 --max-edits 100 --seed 17 --output-dir data/exp_llm1_first_run

Phase-2 work: see notes/llm_benchmark_harness_2026-05-29.md roadmap.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import os
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


# ----------------------------------------------------------------------------
# Edit triple schema
# ----------------------------------------------------------------------------

@dataclass
class EditTriple:
    """Single (subject, relation, object) edit specification.

    Mirrors the MEMIT / ROME data format. `target_new` is the value to write;
    `target_true` is the pre-edit ground truth (for diagnostic / specificity).
    `paraphrase_prompts` and `neighborhood_prompts` are evaluated post-edit.
    """
    subject: str
    relation: str
    target_new: str
    target_true: Optional[str] = None
    prompt: Optional[str] = None
    paraphrase_prompts: List[str] = field(default_factory=list)
    neighborhood_prompts: List[str] = field(default_factory=list)
    case_id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


# ----------------------------------------------------------------------------
# Dataset abstraction
# ----------------------------------------------------------------------------

class EditDataset(ABC):
    """Abstract base: a stream of EditTriple cases."""

    name: str = "abstract"

    def __init__(self, path: Optional[Path] = None, max_edits: Optional[int] = None) -> None:
        self.path = Path(path) if path is not None else None
        self.max_edits = max_edits
        self._cases: List[EditTriple] = []
        self._loaded = False

    @abstractmethod
    def load(self) -> None:
        """Populate self._cases. Sets self._loaded = True when done.

        Subclasses MUST tolerate self.path = None (empty dataset OK for scaffold tests).
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[EditTriple]:
        if not self._loaded:
            self.load()
        for i, case in enumerate(self._cases):
            if self.max_edits is not None and i >= self.max_edits:
                return
            yield case

    def __len__(self) -> int:
        if not self._loaded:
            self.load()
        n = len(self._cases)
        if self.max_edits is not None:
            n = min(n, self.max_edits)
        return n


class CounterFactDataset(EditDataset):
    """CounterFact (Meng et al, ROME 2022).

    Expected JSON file: list of dicts with keys
        case_id, requested_rewrite { prompt, subject, target_new {str}, target_true {str} },
        paraphrase_prompts, neighborhood_prompts.

    Download: https://rome.baulab.info/data/dsets/counterfact.json (placeholder reference).
    See datasets/README.md for the canonical source list.
    """
    name = "counterfact"

    def load(self) -> None:
        if self.path is None or not self.path.exists():
            self._cases = []
            self._loaded = True
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cases: List[EditTriple] = []
        for entry in raw:
            rr = entry.get("requested_rewrite", {})
            cases.append(EditTriple(
                subject=rr.get("subject", ""),
                relation=rr.get("prompt", ""),
                target_new=rr.get("target_new", {}).get("str", "")
                    if isinstance(rr.get("target_new"), dict) else str(rr.get("target_new", "")),
                target_true=rr.get("target_true", {}).get("str")
                    if isinstance(rr.get("target_true"), dict) else rr.get("target_true"),
                prompt=rr.get("prompt"),
                paraphrase_prompts=list(entry.get("paraphrase_prompts", [])),
                neighborhood_prompts=list(entry.get("neighborhood_prompts", [])),
                case_id=str(entry.get("case_id", "")),
                meta=entry.get("meta", {}),
            ))
        self._cases = cases
        self._loaded = True


class ZsREDataset(EditDataset):
    """zsRE editing split (used by MEND, MEMIT).

    Expected JSON Lines or JSON list. STUB: schema parse not finalized.
    Download: see datasets/README.md.
    """
    name = "zsre"

    def load(self) -> None:
        if self.path is None or not self.path.exists():
            self._cases = []
            self._loaded = True
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cases: List[EditTriple] = []
        for entry in raw:
            cases.append(EditTriple(
                subject=entry.get("subject", ""),
                relation=entry.get("src", entry.get("prompt", "")),
                target_new=entry.get("alt", entry.get("target_new", "")),
                target_true=entry.get("answers", [None])[0]
                    if isinstance(entry.get("answers"), list) else entry.get("answer"),
                prompt=entry.get("src"),
                paraphrase_prompts=list(entry.get("rephrase", [])
                    if isinstance(entry.get("rephrase"), list)
                    else ([entry.get("rephrase")] if entry.get("rephrase") else [])),
                neighborhood_prompts=list(entry.get("loc", [])
                    if isinstance(entry.get("loc"), list)
                    else ([entry.get("loc")] if entry.get("loc") else [])),
                case_id=str(entry.get("case_id", entry.get("id", ""))),
            ))
        self._cases = cases
        self._loaded = True


class SequentialEditDataset(EditDataset):
    """Sequential edit stream (MEMIT-style). Order is load order.

    Expected: same schema as CounterFact; sequence order matters.
    Download: see datasets/README.md.
    """
    name = "sequential"

    def load(self) -> None:
        # STUB: defer to CounterFact loader for now; the substrate-relevant
        # property is the IDENTITY of the stream, not the parser.
        if self.path is None or not self.path.exists():
            self._cases = []
            self._loaded = True
            return
        cf = CounterFactDataset(self.path, max_edits=None)
        cf.load()
        self._cases = list(cf)
        self._loaded = True


# ----------------------------------------------------------------------------
# Method abstraction
# ----------------------------------------------------------------------------

class EditMethod(ABC):
    """Abstract editor: apply (subject, relation, target_new) and answer queries."""

    name: str = "abstract"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self._initialised = False

    @abstractmethod
    def initialise(self) -> None:
        """Build / load the underlying model or substrate."""
        raise NotImplementedError

    @abstractmethod
    def apply_edit(self, triple: EditTriple) -> Dict[str, Any]:
        """Apply a single edit; return diagnostic info (timings, side metrics)."""
        raise NotImplementedError

    @abstractmethod
    def query(self, prompt: str) -> str:
        """Return the method's answer to `prompt` under its current edited state."""
        raise NotImplementedError

    def reset(self) -> None:
        """Optional: revert to pre-edit state. Default = re-initialise."""
        self._initialised = False
        self.initialise()


# Concrete substrate method lives in methods/substrate.py to keep this file
# light. The class is re-exported here for the registry.
def _import_substrate_method():
    from experiments.llm_benchmarks.methods.substrate import SubstrateEditMethod
    return SubstrateEditMethod


def _import_baselines():
    from experiments.llm_benchmarks.methods.baselines import (
        ROMEMethod, MEMITMethod, AlphaEditMethod, MENDMethod,
    )
    return ROMEMethod, MEMITMethod, AlphaEditMethod, MENDMethod


METHOD_REGISTRY = {
    "substrate": _import_substrate_method,
    "rome": lambda: _import_baselines()[0],
    "memit": lambda: _import_baselines()[1],
    "alphaedit": lambda: _import_baselines()[2],
    "mend": lambda: _import_baselines()[3],
}

DATASET_REGISTRY = {
    "counterfact": CounterFactDataset,
    "zsre": ZsREDataset,
    "sequential": SequentialEditDataset,
}


# ----------------------------------------------------------------------------
# Evaluation driver
# ----------------------------------------------------------------------------

DEFAULT_METRICS = ["efficacy", "specificity", "paraphrase", "sequential_count"]


def evaluate_edit(method: EditMethod, dataset: EditDataset,
                  metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run `method` over `dataset` and aggregate `metrics`.

    Returns: dict with one entry per requested metric plus 'per_case', 'config',
    and 'n_cases'. Unknown metrics yield None so the schema is always complete.
    """
    metrics = list(metrics) if metrics is not None else list(DEFAULT_METRICS)
    if not method._initialised:
        method.initialise()

    # Import metric implementations lazily so the harness file stays light.
    from experiments.llm_benchmarks.metrics.edit_metrics import (
        score_efficacy, score_specificity, score_paraphrase, score_sequential_count,
    )

    metric_fns = {
        "efficacy": score_efficacy,
        "specificity": score_specificity,
        "paraphrase": score_paraphrase,
        "sequential_count": score_sequential_count,
    }

    per_case: List[Dict[str, Any]] = []
    successful_edits = 0
    for i, triple in enumerate(dataset):
        t_edit_0 = time.time()
        try:
            edit_info = method.apply_edit(triple)
            edit_ok = True
        except NotImplementedError:
            raise
        except Exception as exc:  # noqa: BLE001
            edit_info = {"error": repr(exc)}
            edit_ok = False
        edit_dt = time.time() - t_edit_0

        case_scores: Dict[str, Any] = {}
        for m in metrics:
            fn = metric_fns.get(m)
            if fn is None:
                case_scores[m] = None
                continue
            try:
                case_scores[m] = fn(method, triple)
            except NotImplementedError:
                raise
            except Exception as exc:  # noqa: BLE001
                case_scores[m] = {"error": repr(exc)}

        if edit_ok:
            successful_edits += 1
        per_case.append({
            "case_id": triple.case_id,
            "edit_info": edit_info,
            "edit_ok": edit_ok,
            "edit_time_s": edit_dt,
            "scores": case_scores,
        })

    # Aggregate: mean of float-valued cells per metric where possible.
    aggregate: Dict[str, Any] = {}
    for m in metrics:
        values = [p["scores"].get(m) for p in per_case]
        floats = [v for v in values if isinstance(v, (int, float))]
        aggregate[m] = (sum(floats) / len(floats)) if floats else None

    return {
        "method": method.name,
        "dataset": dataset.name,
        "n_cases": len(per_case),
        "successful_edits": successful_edits,
        "metrics_requested": metrics,
        "aggregate": aggregate,
        "per_case": per_case,
    }


# ----------------------------------------------------------------------------
# Atomic JSON writer (project pattern)
# ----------------------------------------------------------------------------

def atomic_json_write(obj: Any, path: Path) -> None:
    """Write JSON via tmp+rename so partial writes never corrupt metrics.json."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        "w", delete=False, dir=str(path.parent), suffix=".tmp", encoding="utf-8")
    try:
        json.dump(obj, tmp, indent=2, default=str)
        tmp.flush()
        os.fsync(tmp.fileno())
    finally:
        tmp.close()
    os.replace(tmp.name, str(path))


def get_output_dir(default_name: str = "llm_benchmark") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def build_method(method_name: str, N: int, seed: int,
                 extra: Optional[Dict[str, Any]] = None) -> EditMethod:
    key = method_name.lower()
    if key not in METHOD_REGISTRY:
        raise ValueError(f"unknown method: {method_name}; "
                         f"choices = {sorted(METHOD_REGISTRY)}")
    cls = METHOD_REGISTRY[key]()
    cfg = {"N": N, "seed": seed}
    if extra:
        cfg.update(extra)
    return cls(config=cfg)


def build_dataset(dataset_name: str, path: Optional[Path],
                  max_edits: Optional[int]) -> EditDataset:
    key = dataset_name.lower()
    if key not in DATASET_REGISTRY:
        raise ValueError(f"unknown dataset: {dataset_name}; "
                         f"choices = {sorted(DATASET_REGISTRY)}")
    return DATASET_REGISTRY[key](path=path, max_edits=max_edits)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="LLM editing benchmark harness (substrate vs baselines).",
    )
    parser.add_argument("--method", required=True,
                        choices=sorted(METHOD_REGISTRY.keys()))
    parser.add_argument("--dataset", required=True,
                        choices=sorted(DATASET_REGISTRY.keys()))
    parser.add_argument("--dataset-path", type=Path, default=None,
                        help="Path to dataset file (counterfact.json / zsre.json).")
    parser.add_argument("--N", type=int, default=4096,
                        help="Substrate dimensionality (substrate method only).")
    parser.add_argument("--max-edits", type=int, default=None,
                        help="Cap on number of edits to evaluate.")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--metrics", type=str, default=",".join(DEFAULT_METRICS),
                        help="Comma-separated list of metric names.")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run scaffold smoke (no real datasets).")
    args = parser.parse_args(argv)

    if args.self_test:
        # Tiny end-to-end smoke: empty dataset, substrate method, no metric calls.
        method = build_method(args.method, args.N, args.seed)
        method.initialise()
        ds = build_dataset(args.dataset, None, args.max_edits)
        result = evaluate_edit(method, ds, metrics=args.metrics.split(","))
        print(json.dumps({
            "self_test": True,
            "method": result["method"],
            "dataset": result["dataset"],
            "n_cases": result["n_cases"],
        }, indent=2))
        return 0

    method = build_method(args.method, args.N, args.seed)
    method.initialise()
    ds = build_dataset(args.dataset, args.dataset_path, args.max_edits)
    metric_list = [m.strip() for m in args.metrics.split(",") if m.strip()]

    t0 = time.time()
    result = evaluate_edit(method, ds, metrics=metric_list)
    result["elapsed_s"] = time.time() - t0
    result["config"] = {
        "method": args.method,
        "dataset": args.dataset,
        "dataset_path": str(args.dataset_path) if args.dataset_path else None,
        "N": args.N,
        "max_edits": args.max_edits,
        "seed": args.seed,
        "metrics": metric_list,
    }

    outdir = args.output_dir or get_output_dir()
    outdir.mkdir(parents=True, exist_ok=True)
    atomic_json_write(result, outdir / "metrics.json")

    print(f"method={args.method} dataset={args.dataset} n_cases={result['n_cases']} "
          f"successful_edits={result['successful_edits']} "
          f"elapsed={result['elapsed_s']:.2f}s")
    print(f"aggregate: {json.dumps(result['aggregate'])}")
    print(f"metrics -> {outdir / 'metrics.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
