"""Per-seed checkpoint helper for multi-seed experiments.

Lets a script that crashes mid-run (CUDA OOM, runner timeout, process kill)
resume from where it left off on the next ship instead of re-running every
completed seed from scratch.

Contract (script-side adoption):

    from _seed_checkpoint import (
        resumable_seeds,
        write_partial,
        aggregate_partials,
    )

    out_dir = get_output_dir()                       # data/exp_<HDLAB_EXP_NAME>
    seeds = SEEDS_FULL                               # e.g. [7, 17, 23, 31, 41]
    done, remaining = resumable_seeds(seeds, out_dir)
    print(f"[ckpt] {len(done)} of {len(seeds)} seeds already complete; "
          f"running {remaining}", flush=True)

    for seed in remaining:
        result = run_one_seed(seed, ...)             # whatever the script does
        write_partial(out_dir, seed, result)         # atomic .tmp + replace

    per_seed = aggregate_partials(out_dir, seeds)    # dict keyed by str(seed)
    # ... build summary / verdict / metrics.json from per_seed ...

Disk layout under out_dir = data/exp_<name>/ :

    partial_metrics_<seed>.json     -- one per completed seed
    partial_metrics_<seed>.json.tmp -- crash residue (ignored on reload)
    metrics.json                    -- final aggregate (written at end)

Design choices:

  - Atomicity: .tmp + os.replace. If a crash occurs mid-write, the .tmp may
    exist but the .json does not -- recovery scan ignores .tmp and the seed
    re-runs. If a partial_metrics_<seed>.json fails json.load (truncated /
    corrupted), recovery treats it as not-done and re-runs the seed.

  - Schema check: a partial is accepted only if it loads, is a dict, and
    has a "seed" field matching the filename. Older / foreign files are
    rejected (seed re-runs).

  - Granularity: per-seed is the canonical level (matches the dominant
    pattern across saad_solla / tcft / bid / wave14 scripts). For
    inverted-loop scripts (outer = param, inner = seed) the helper still
    works -- callers can use any hashable key by calling the lower-level
    write_partial_key() / load_partial_key() functions.

  - No deletion of partials at end: the aggregator leaves partial files
    in place for audit. Operators can clean up via:
        rm data/exp_<name>/partial_metrics_*.json
    after the experiment is fully consumed.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

# Filename schema: partial_metrics_<seed>.json
_PARTIAL_RE = re.compile(r"^partial_metrics_(?P<key>[A-Za-z0-9_\-]+)\.json$")


def _partial_path(out_dir: Path, key: Any) -> Path:
    """Path to the partial-metrics file for a given key (typically seed int)."""
    return Path(out_dir) / f"partial_metrics_{key}.json"


def _is_valid_partial(p: Path, expected_key: str) -> bool:
    """Return True iff p loads as a dict with matching 'seed'/'key' field."""
    try:
        with open(p, "r", encoding="utf-8") as fh:
            body = json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(body, dict):
        return False
    recorded = body.get("seed", body.get("key"))
    if recorded is None:
        return False
    return str(recorded) == str(expected_key)


def list_completed_keys(out_dir: Path) -> List[str]:
    """Scan out_dir for valid partial_metrics_<key>.json files.

    Returns the list of keys (as strings) that have a well-formed partial.
    Corrupted / truncated / schema-mismatched partials are skipped.
    """
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return []
    done: List[str] = []
    for child in sorted(out_dir.iterdir()):
        m = _PARTIAL_RE.match(child.name)
        if m is None:
            continue
        key = m.group("key")
        if _is_valid_partial(child, key):
            done.append(key)
    return done


def resumable_seeds(
    seeds: Sequence[Any],
    out_dir: Path,
) -> Tuple[List[Any], List[Any]]:
    """Split seeds into (already_done, remaining) based on partials in out_dir.

    Preserves input order. Compares by str(seed) so int seeds and string keys
    interoperate.

    Returns:
        (done_seeds, remaining_seeds) -- both ordered subsequences of `seeds`.
    """
    done_keys = set(list_completed_keys(out_dir))
    done: List[Any] = []
    remaining: List[Any] = []
    for s in seeds:
        if str(s) in done_keys:
            done.append(s)
        else:
            remaining.append(s)
    return done, remaining


def write_partial_key(
    out_dir: Path,
    key: Any,
    payload: Dict[str, Any],
) -> Path:
    """Atomically write payload to partial_metrics_<key>.json under out_dir.

    The 'seed'/'key' field of payload is stamped with str(key) so reloads
    can verify schema. tmp file is os.replace()d -- on POSIX this is atomic
    within a filesystem, on Windows os.replace overwrites atomically.

    On crash mid-write: the .tmp may exist but the .json does not, so
    list_completed_keys will not list the key, and the seed will re-run.

    Returns the final path.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    body = dict(payload)
    body.setdefault("seed", str(key))
    body.setdefault("_partial_written_at", time.time())

    final = _partial_path(out_dir, key)
    tmp = final.with_suffix(final.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(body, fh, indent=2, default=str)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            # fsync unsupported on some platforms / filesystems; tolerate.
            pass
    os.replace(tmp, final)
    return final


def write_partial(out_dir: Path, seed: Any, payload: Dict[str, Any]) -> Path:
    """Alias of write_partial_key for the common per-seed case."""
    return write_partial_key(out_dir, seed, payload)


def load_partial_key(out_dir: Path, key: Any) -> Dict[str, Any] | None:
    """Load a single partial by key, returning None if missing/corrupt."""
    p = _partial_path(out_dir, key)
    if not _is_valid_partial(p, str(key)):
        return None
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def aggregate_partials(
    out_dir: Path,
    seeds: Sequence[Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Load all valid partials under out_dir into a {str(key): payload} dict.

    If `seeds` is supplied, only those keys are returned (in input order).
    Otherwise all valid partials are returned in lexicographic key order.

    Missing seeds (when `seeds` is supplied) are silently omitted -- callers
    that need a presence check should compare against `resumable_seeds`
    output instead.
    """
    out_dir = Path(out_dir)
    if seeds is None:
        keys = list_completed_keys(out_dir)
    else:
        valid = set(list_completed_keys(out_dir))
        keys = [str(s) for s in seeds if str(s) in valid]
    out: Dict[str, Dict[str, Any]] = {}
    for k in keys:
        body = load_partial_key(out_dir, k)
        if body is not None:
            out[k] = body
    return out


def clear_partials(out_dir: Path) -> int:
    """Delete all partial_metrics_*.json[.tmp] under out_dir. Returns count.

    Optional cleanup utility; the contract does NOT require post-aggregate
    deletion -- partials are kept for audit by default.
    """
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return 0
    n = 0
    for child in list(out_dir.iterdir()):
        if _PARTIAL_RE.match(child.name) or child.name.endswith(".json.tmp"):
            try:
                child.unlink()
                n += 1
            except OSError:
                pass
    return n


__all__ = [
    "list_completed_keys",
    "resumable_seeds",
    "write_partial",
    "write_partial_key",
    "load_partial_key",
    "aggregate_partials",
    "clear_partials",
]
