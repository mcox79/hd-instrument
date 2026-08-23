"""Per-seed checkpoint helper for multi-seed experiments.

Lets a script that crashes mid-run (CUDA OOM, runner timeout, process kill)
resume from where it left off on the next ship instead of re-running every
completed seed from scratch.

Contract (script-side adoption) -- USE THE *_config ENTRY POINTS:

    from _seed_checkpoint import (
        resumable_seeds_config,
        write_partial_config,
        aggregate_partials_config,
    )

    out_dir = get_output_dir(ANCHOR_NAME)            # data/exp_<HDLAB_EXP_NAME>
    seeds = SEEDS_FULL                               # e.g. [7, 17, 23, 31, 41]

    # The RESOLVED config: every dimension that changes what is computed.
    # It is HASHED into the checkpoint key, so a field added here later is
    # part of the checkpoint identity automatically.
    cfg = {"run_mode": run_mode, "N": N, "D": D, "M": M}

    done, remaining = resumable_seeds_config(seeds, out_dir, cfg)
    print(f"[ckpt] {len(done)} of {len(seeds)} seeds already complete; "
          f"running {remaining}", flush=True)

    for seed in remaining:
        result = run_one_seed(seed, ...)             # whatever the script does
        write_partial_config(out_dir, seed, result, cfg)   # atomic .tmp+replace

    per_seed = aggregate_partials_config(out_dir, seeds, cfg)  # keyed by str(seed)
    # ... build summary / verdict / metrics.json from per_seed ...

    A checkpoint whose recorded config does not match `cfg` raises
    CheckpointConfigMismatchError. It is never skipped and never reloaded.

LEGACY contract (resumable_seeds / write_partial / aggregate_partials, keyed on
the SEED ALONE) is retained unchanged for callers already written against it,
but it is NOT SAFE when a smoke and a full share an out_dir: nothing in the key
records what was computed, so the full reloads the smoke's answer. See the
PROT-021b block further down for the reproduction and the incident.

PROT-021 config-mismatch guard (smoke-checkpoint contamination fix):

    When a FULL run resumes, it must NOT silently load smoke partials whose
    stored N, M, or run_mode do not match the FULL config.  Pass run_config
    to list_completed_keys / resumable_seeds / aggregate_partials:

        run_config = {"N": N_FULL, "run_mode": "full"}  # optional M check too
        done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)

    Any partial whose body fields contradict run_config is REJECTED with a
    warning printed to stdout.  The caller re-runs those seeds.

    Supported run_config keys (all optional; only those present are checked):
        "N"        -- int: rejects partials where body["N"] != N
        "M"        -- int: rejects partials where body["M"] != M
        "run_mode" -- str ("smoke"|"full"): rejects mode-mismatched partials

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

  - Config mismatch check (PROT-021): when run_config is supplied, a partial
    is additionally rejected if its stored N, M, or run_mode contradicts the
    caller's run_config. This prevents smoke checkpoints from being silently
    consumed by FULL runs sharing the same out_dir.

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
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Filename schema: partial_metrics_<seed>.json
_PARTIAL_RE = re.compile(r"^partial_metrics_(?P<key>[A-Za-z0-9_\-]+)\.json$")


def _partial_path(out_dir: Path, key: Any) -> Path:
    """Path to the partial-metrics file for a given key (typically seed int)."""
    return Path(out_dir) / f"partial_metrics_{key}.json"


def _is_valid_partial(p: Path, expected_key: str) -> bool:
    """Return True iff p loads as a dict with matching key field.

    Checks (in order):
      1. "_ckpt_key" field (authoritative compound key, e.g. "M256_seed17")
      2. "seed" / "key" field (legacy scalar, e.g. 17)
    A match on either field is accepted.  This handles both the compound-key
    PROT-021 pattern and the legacy bare-seed pattern.
    """
    try:
        with open(p, "r", encoding="utf-8") as fh:
            body = json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(body, dict):
        return False
    # Prefer _ckpt_key (authoritative compound key stamped by write_partial_key)
    ckpt_key = body.get("_ckpt_key")
    if ckpt_key is not None:
        return str(ckpt_key) == str(expected_key)
    # Fall back to legacy "seed" / "key" field
    recorded = body.get("seed", body.get("key"))
    if recorded is None:
        return False
    return str(recorded) == str(expected_key)


def _check_run_config(body: Dict[str, Any],
                      run_config: Dict[str, Any],
                      filename: str) -> bool:
    """Return True iff body fields do not contradict run_config.

    Supported run_config keys (all optional; only those present are checked):
      "N"        -- int: rejects partials where body["N"] != N
      "M"        -- int: rejects partials where body["M"] != M
      "run_mode" -- str ("smoke"|"full"): rejects mode-mismatched partials
      "anchor"   -- str: rejects partials where body["config_version"] ANCHOR=
                   string does not match (META_RULE_H_ANCHOR defense; PROT-021
                   extension catching cross-cell partial contamination from
                   import-time side effects -- see
                   notes/research_drill_stratified_replay_HARD_FAIL_3x_2026-06-27.md)

    When a mismatch is found, a REJECTED warning is printed to stdout and
    False is returned.  The caller must treat the partial as not-done and
    re-run the corresponding seed.

    This is the PROT-021 smoke-checkpoint contamination guard: smoke partials
    (N=small, M=smoke-M) must NOT be silently consumed by FULL runs that share
    the same out_dir but use different N/M/run_mode.

    RULE_PARTIAL_LOAD_MUST_CHECK_ANCHOR_NAME (added 2026-06-27): the anchor
    check defends against alien partials written by a different cell whose
    main-driver code ran at import time and wrote to the importing cell's
    HDLAB_EXP_NAME output dir.  Cell convention: pass run_config["anchor"]=
    ANCHOR_NAME and stamp body["config_version"] with "ANCHOR=<name>,..." so
    cross-cell contamination is caught at PARTIAL-LOAD time.
    """
    if not run_config:
        return True

    # Check N
    if "N" in run_config:
        stored_N = body.get("N")
        if stored_N is not None and int(stored_N) != int(run_config["N"]):
            print(
                f"[ckpt] REJECTED {filename}: stored N={stored_N} != "
                f"FULL N={run_config['N']}; ignoring smoke partial",
                flush=True,
            )
            return False

    # Check M
    if "M" in run_config:
        stored_M = body.get("M")
        if stored_M is not None and int(stored_M) != int(run_config["M"]):
            print(
                f"[ckpt] REJECTED {filename}: stored M={stored_M} != "
                f"FULL M={run_config['M']}; ignoring smoke partial",
                flush=True,
            )
            return False

    # Check run_mode (stored as bool "smoke" or string "run_mode")
    if "run_mode" in run_config:
        expected_mode = str(run_config["run_mode"]).lower()
        # Partials may encode mode as boolean "smoke" field (True/False)
        # or string "run_mode" field ("smoke"/"full").
        stored_smoke_bool = body.get("smoke")  # True -> smoke, False -> full
        stored_run_mode = body.get("run_mode")  # "smoke" or "full"
        if stored_smoke_bool is not None:
            actual_mode = "smoke" if stored_smoke_bool else "full"
        elif stored_run_mode is not None:
            actual_mode = str(stored_run_mode).lower()
        else:
            actual_mode = None
        if actual_mode is not None and actual_mode != expected_mode:
            print(
                f"[ckpt] REJECTED {filename}: stored run_mode={actual_mode!r} != "
                f"expected={expected_mode!r}; ignoring mismatched partial",
                flush=True,
            )
            return False

    # Check anchor name (META_RULE_H_ANCHOR defense; added 2026-06-27)
    # config_version is conventionally "ANCHOR=<name>,N=...,M=...".  When the
    # caller passes run_config["anchor"], reject partials whose stamped ANCHOR
    # string does not match -- this catches alien partials written by a
    # different cell that ran at import time into the importing cell's dir.
    if "anchor" in run_config:
        expected_anchor = str(run_config["anchor"])
        cv = body.get("config_version", "")
        if cv:
            m = re.match(r"ANCHOR=([^,]+)", str(cv))
            if m and m.group(1) != expected_anchor:
                print(
                    f"[ckpt] REJECTED {filename}: stored ANCHOR={m.group(1)!r} "
                    f"!= expected={expected_anchor!r}; ignoring alien partial "
                    f"(import-time-side-effect contamination per "
                    f"META_RULE_H_ANCHOR)",
                    flush=True,
                )
                return False
        # Also check explicit anchor_name field if present (alternate stamping)
        stored_anchor_field = body.get("anchor_name")
        if stored_anchor_field is not None and \
                str(stored_anchor_field) != expected_anchor:
            print(
                f"[ckpt] REJECTED {filename}: stored anchor_name="
                f"{stored_anchor_field!r} != expected={expected_anchor!r}; "
                f"ignoring alien partial (META_RULE_H_ANCHOR)",
                flush=True,
            )
            return False

    return True


def list_completed_keys(
    out_dir: Path,
    run_config: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Scan out_dir for valid partial_metrics_<key>.json files.

    Returns the list of keys (as strings) that have a well-formed partial
    AND (when run_config is supplied) whose stored N/M/run_mode fields are
    consistent with run_config.

    Partials that fail the schema check OR contradict run_config are silently
    skipped (with a stdout warning for config mismatches per PROT-021).

    Args:
        out_dir:    Directory to scan.
        run_config: Optional dict with keys "N", "M", "run_mode" (all
                    optional).  When provided, partials whose stored values
                    contradict these are REJECTED (PROT-021 contamination
                    guard).  Pass None (default) to use legacy behaviour with
                    no config check.
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
        if not _is_valid_partial(child, key):
            continue
        # PROT-021: config-mismatch guard
        if run_config:
            try:
                with open(child, "r", encoding="utf-8") as fh:
                    body = json.load(fh)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if not _check_run_config(body, run_config, child.name):
                continue
        done.append(key)
    if done and not run_config:
        _warn_unverified_legacy_reuse(out_dir, done)
    return done


_LEGACY_REUSE_WARNED = False


def _warn_unverified_legacy_reuse(out_dir: Path, done: List[str]) -> None:
    """One stderr line per process when checkpoints are reused with NO config check.

    Visibility only -- deliberately does not change which keys are returned, so
    a run already in flight against the legacy contract is unaffected. See the
    PROT-021b block below for why an unverified reuse is worth surfacing.
    """
    global _LEGACY_REUSE_WARNED
    if _LEGACY_REUSE_WARNED:
        return
    _LEGACY_REUSE_WARNED = True
    import sys as _sys
    _sys.stderr.write(
        f"[ckpt] UNVERIFIED REUSE: reloading {len(done)} checkpoint(s) from "
        f"{out_dir} with no run_config, so nothing checks that they were "
        f"computed under this run's config. If a smoke gate shares this "
        f"out_dir its answers will be reported as this run's. Migrate to "
        f"resumable_seeds_config(seeds, out_dir, cfg) (PROT-021b).\n"
    )


def resumable_seeds(
    seeds: Sequence[Any],
    out_dir: Path,
    run_config: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Any], List[Any]]:
    """Split seeds into (already_done, remaining) based on partials in out_dir.

    Preserves input order. Compares by str(seed) so int seeds and string keys
    interoperate.

    Args:
        seeds:      Full seed list for the current run.
        out_dir:    Directory to scan for partials.
        run_config: Optional dict passed to list_completed_keys for PROT-021
                    config-mismatch filtering.  Keys: "N", "M", "run_mode".
                    Partials contradicting run_config are treated as not-done.

    Returns:
        (done_seeds, remaining_seeds) -- both ordered subsequences of `seeds`.
    """
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
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
    # Always stamp _ckpt_key with the compound key (overwrite if present).
    # _is_valid_partial checks _ckpt_key first, enabling compound keys like
    # "M256_seed17" to coexist with body["seed"]=17 (PROT-021).
    body["_ckpt_key"] = str(key)
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
    run_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Load all valid partials under out_dir into a {str(key): payload} dict.

    If `seeds` is supplied, only those keys are returned (in input order).
    Otherwise all valid partials are returned in lexicographic key order.

    Missing seeds (when `seeds` is supplied) are silently omitted -- callers
    that need a presence check should compare against `resumable_seeds`
    output instead.

    Args:
        out_dir:    Directory to scan.
        seeds:      Optional seed filter.
        run_config: Optional PROT-021 config dict ("N", "M", "run_mode").
                    Partials contradicting run_config are excluded.
    """
    out_dir = Path(out_dir)
    if seeds is None:
        keys = list_completed_keys(out_dir, run_config=run_config)
    else:
        valid = set(list_completed_keys(out_dir, run_config=run_config))
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


# --- PROT-021b config-fingerprinted checkpoint keys (added 2026-08-15, Testbed) ---
#
# INCIDENT. The default checkpoint contract above keys a partial on the SEED
# ALONE (`partial_metrics_17.json`). Nothing in the key records WHAT WAS
# COMPUTED. A smoke gate that writes seed 17 at N=1024 and a FULL dispatch that
# wants seed 17 at N=16384 therefore address the SAME FILE, and when both share
# an out_dir the FULL reloads the smoke's answer and skips the work -- while
# still writing a metrics.json that reads like a completed FULL run.
#
# Reproduced off-disk against this module at HEAD before this fix was written
# (scratch/repro_checkpoint_collision.py, four arms):
#   A  default contract, shared out_dir: FULL saw done=[17], recomputed only
#      [7, 23], and its aggregate for seed 17 carried N=1024 / M=256 /
#      run_mode='smoke' / elapsed_s=0.01. If the smoke's seed list EQUALS the
#      FULL's, `remaining` is empty and the FULL computes NOTHING.
#   B  the 2026-06-01 PROT-021 run_config guard (19544ae79) does hold -- but
#      only when a caller remembers to pass run_config, and it prints rather
#      than raises.
#   C  a run_config listing {N, M} accepts a partial whose D disagrees, because
#      D is not in the guard's hand-written vocabulary. THIS is why the key
#      below is a HASH OF THE RESOLVED CONFIG and not a hand-listed tuple: a
#      config field added next year is in the key automatically, and cannot be
#      silently left out by whoever adds it.
#
# TWO DEFENCES, both required:
#   1. SEPARATION -- the key carries a fingerprint of the resolved config, so
#      smoke and full are DIFFERENT FILES and cannot collide even in one dir.
#   2. A LOUD GUARD -- if a checkpoint is nonetheless found whose recorded
#      config does not match the current config, the run RAISES. A silently
#      mismatched reload is the exact failure this exists to prevent, so it is
#      never downgraded to a skip or a warning.
#
# BACKWARD COMPATIBILITY (a run is in flight as this lands). Every function
# above is untouched: same signatures, same defaults, same bytes on disk. The
# new behaviour is reachable ONLY through the new *_config entry points below,
# which no existing caller invokes. A cell already running keeps resolving its
# own partials exactly as it did when it started.

class CheckpointConfigMismatchError(RuntimeError):
    """A checkpoint on disk does not match the config of the run loading it.

    Raised instead of skipping, because a mismatched checkpoint that is merely
    skipped is indistinguishable from one that was never there -- and a
    mismatched checkpoint that is LOADED is the smoke-contaminates-full defect
    itself. The run must stop so an operator decides.
    """


_CKPT_FP_FIELD = "_ckpt_config_fp"
_CKPT_CFG_FIELD = "_ckpt_config"

# Excluded from the fingerprint. These vary between two runs that compute the
# SAME thing, so including them would orphan a resuming run's own checkpoints.
# The seed is excluded because it is already carried explicitly in the key.
_CKPT_VOLATILE_KEYS = frozenset({
    "seed", "seeds", "elapsed_s", "elapsed", "timestamp", "started_at",
    "out_dir", "output_dir", "device", "resume", "host", "hostname", "pid",
})


def _canonical_config(config: Dict[str, Any],
                      exclude: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """Drop volatile / caller-excluded / underscore-prefixed keys, sorted."""
    if not isinstance(config, dict):
        raise TypeError(
            f"config must be a dict of resolved run parameters, got "
            f"{type(config).__name__}")
    drop = set(_CKPT_VOLATILE_KEYS) | set(exclude or ())
    return {k: config[k] for k in sorted(config)
            if k not in drop and not str(k).startswith("_")}


def config_fingerprint(config: Dict[str, Any],
                       exclude: Optional[Sequence[str]] = None,
                       length: int = 12) -> str:
    """Stable short hash of a RESOLVED run config.

    A hash of the whole config rather than a hand-listed tuple, so that a
    config field introduced later is part of the checkpoint identity without
    anyone having to remember to add it (repro arm C above).

    Deterministic across processes and platforms: canonical JSON with sorted
    keys, non-JSON values coerced via str(), then sha256. Does NOT depend on
    Python's per-process hash randomisation.
    """
    import hashlib
    canon = json.dumps(_canonical_config(config, exclude),
                       sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:length]


def checkpoint_key(seed: Any, config: Dict[str, Any],
                   exclude: Optional[Sequence[str]] = None) -> str:
    """Checkpoint key for one seed under one resolved config: cfg<fp>_seed<seed>.

    Every dimension that changes what is computed is in `config` and therefore
    in `fp`; the seed is appended in clear so a directory listing stays legible.
    Smoke and full differ in at least run_mode, so they can never collide.
    """
    return f"cfg{config_fingerprint(config, exclude)}_seed{seed}"


def _config_contradictions(body: Dict[str, Any],
                           config: Dict[str, Any]) -> List[str]:
    """Fields present in BOTH the stored partial and the current config that disagree.

    Compares the partial's own top-level fields and its stamped _ckpt_config.
    Absent fields are not contradictions -- only a field the partial actually
    recorded, whose value differs, counts.
    """
    stored: Dict[str, Any] = {}
    embedded = body.get(_CKPT_CFG_FIELD)
    if isinstance(embedded, dict):
        stored.update(embedded)
    for k, v in body.items():
        if not str(k).startswith("_"):
            stored.setdefault(k, v)
    out: List[str] = []
    for k in sorted(_canonical_config(config)):
        if k not in stored:
            continue
        if str(stored[k]) != str(config[k]):
            out.append(f"{k}: stored={stored[k]!r} current={config[k]!r}")
    return out


def list_completed_keys_config(
    seeds: Sequence[Any],
    out_dir: Path,
    config: Dict[str, Any],
    exclude: Optional[Sequence[str]] = None,
) -> List[Any]:
    """Seeds with a checkpoint written under THIS EXACT config. Raises on mismatch.

    For each seed, looks only at cfg<fp>_seed<seed>. A partial found there whose
    recorded fingerprint disagrees raises CheckpointConfigMismatchError rather
    than being skipped.

    Legacy bare-key partials (partial_metrics_<seed>.json, the pre-fix layout)
    are also inspected, because they are exactly what the smoke gate left behind
    on the affected runs:
      * one that CONTRADICTS the current config RAISES -- this is the original
        defect, now loud instead of silent;
      * one carrying nothing comparable is reported on stderr and ignored, so
        the seed is recomputed. Worst case is recomputation, never wrong reuse.
    """
    import sys as _sys
    out_dir = Path(out_dir)
    fp = config_fingerprint(config, exclude)
    done: List[Any] = []
    for seed in seeds:
        key = checkpoint_key(seed, config, exclude)
        p = _partial_path(out_dir, key)
        if p.is_file() and _is_valid_partial(p, key):
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    body = json.load(fh)
            except (OSError, ValueError):
                continue
            stored_fp = body.get(_CKPT_FP_FIELD)
            if stored_fp is None or str(stored_fp) != fp:
                raise CheckpointConfigMismatchError(
                    f"{p.name} sits at the key for config fingerprint {fp} but "
                    f"records {stored_fp!r}. Refusing to reload a checkpoint "
                    f"whose config does not match this run. Contradictions: "
                    f"{_config_contradictions(body, config) or '(fingerprint only)'}. "
                    f"Delete the stale partial or dispatch into a fresh out_dir."
                )
            done.append(seed)
            continue

        legacy = _partial_path(out_dir, seed)
        if legacy.is_file():
            try:
                with open(legacy, "r", encoding="utf-8") as fh:
                    lbody = json.load(fh)
            except (OSError, ValueError):
                continue
            if not isinstance(lbody, dict):
                continue
            clashes = _config_contradictions(lbody, config)
            if clashes:
                raise CheckpointConfigMismatchError(
                    f"{legacy.name} is a pre-fix bare-seed checkpoint whose "
                    f"recorded config contradicts this run: {clashes}. This is "
                    f"the smoke-contaminates-full defect: reloading it would "
                    f"skip seed {seed} and report another run's numbers as this "
                    f"run's. Refusing. Re-run this seed into a clean out_dir, or "
                    f"remove the stale partial once its provenance is recorded."
                )
            _sys.stderr.write(
                f"[ckpt] IGNORING {legacy.name}: pre-fix bare-seed checkpoint "
                f"with no comparable config fields, so it cannot be shown to "
                f"match this run (fingerprint {fp}). Seed {seed} will be "
                f"recomputed.\n"
            )
    return done


def resumable_seeds_config(
    seeds: Sequence[Any],
    out_dir: Path,
    config: Dict[str, Any],
    exclude: Optional[Sequence[str]] = None,
) -> Tuple[List[Any], List[Any]]:
    """(done, remaining) under THIS config. Config-safe replacement for resumable_seeds."""
    done_set = {str(s) for s in
                list_completed_keys_config(seeds, out_dir, config, exclude)}
    done: List[Any] = []
    remaining: List[Any] = []
    for s in seeds:
        (done if str(s) in done_set else remaining).append(s)
    return done, remaining


def write_partial_config(
    out_dir: Path,
    seed: Any,
    payload: Dict[str, Any],
    config: Dict[str, Any],
    exclude: Optional[Sequence[str]] = None,
) -> Path:
    """Write one seed's partial under a config-fingerprinted key.

    Stamps the fingerprint AND the canonical config into the body, so a later
    run can say exactly what it disagrees with rather than only that it does.
    """
    body = dict(payload)
    body[_CKPT_FP_FIELD] = config_fingerprint(config, exclude)
    body[_CKPT_CFG_FIELD] = _canonical_config(config, exclude)
    return write_partial_key(out_dir, checkpoint_key(seed, config, exclude), body)


def aggregate_partials_config(
    out_dir: Path,
    seeds: Sequence[Any],
    config: Dict[str, Any],
    exclude: Optional[Sequence[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Load the partials for `seeds` under THIS config, keyed by str(seed).

    Same mismatch guarantee as list_completed_keys_config: raises rather than
    quietly returning another run's numbers.
    """
    out_dir = Path(out_dir)
    done = list_completed_keys_config(seeds, out_dir, config, exclude)
    out: Dict[str, Dict[str, Any]] = {}
    for seed in done:
        body = load_partial_key(out_dir, checkpoint_key(seed, config, exclude))
        if body is not None:
            out[str(seed)] = body
    return out


def _selftest_config_keys() -> None:
    """Fingerprint/key invariants; runs at module import (pure, no file I/O)."""
    smoke = {"run_mode": "smoke", "N": 1024, "D": 64, "M": 256}
    full = {"run_mode": "full", "N": 16384, "D": 512, "M": 2048}
    # 1. The original collision cannot recur: distinct keys for the same seed.
    assert checkpoint_key(17, smoke) != checkpoint_key(17, full), \
        "PROT-021b FAIL: smoke and full still share a checkpoint key"
    # 2. Each dimension alone is enough to separate.
    for field, other in (("run_mode", "full"), ("N", 4096), ("D", 128), ("M", 512)):
        variant = dict(smoke)
        variant[field] = other
        assert checkpoint_key(17, smoke) != checkpoint_key(17, variant), \
            f"PROT-021b FAIL: {field} does not affect the key"
    # 3. An unforeseen config field is in the key automatically (repro arm C).
    assert checkpoint_key(17, smoke) != checkpoint_key(
        17, dict(smoke, some_field_invented_later=3)), \
        "PROT-021b FAIL: a new config field does not reach the key"
    # 4. Deterministic, and independent of dict insertion order.
    assert config_fingerprint({"N": 1, "D": 2}) == config_fingerprint({"D": 2, "N": 1}), \
        "PROT-021b FAIL: fingerprint is order-dependent"
    assert checkpoint_key(17, smoke) == checkpoint_key(17, dict(smoke)), \
        "PROT-021b FAIL: fingerprint is not deterministic"
    # 5. Volatile fields do not fragment a resuming run's own checkpoints.
    assert config_fingerprint(dict(smoke, elapsed_s=1.0, device="cuda")) == \
        config_fingerprint(smoke), "PROT-021b FAIL: volatile key entered the fingerprint"
    # 6. Seeds stay distinct under one config.
    assert checkpoint_key(7, full) != checkpoint_key(17, full), \
        "PROT-021b FAIL: two seeds share a key"


_selftest_config_keys()


# SH-7 environment variable, named ONCE. It is read by get_output_dir and unset around the
# import-time self-test; a literal in two places is how those two drifted apart.
_FRESH_ENV = "HDI_FRESH_RUN"


def get_output_dir(anchor_name: str) -> Path:
    """Return the canonical output directory for an experiment anchor.

    Convention (enforced by queue_add.py + runner):
        data/exp_<HDLAB_EXP_NAME>/

    The runner sets HDLAB_EXP_NAME to the queued anchor name before launching
    the script.  If the env var is absent (direct local runs / unit tests),
    fall back to the provided anchor_name so the path is still well-formed.

    ALL experiment scripts MUST call this function to obtain their out_dir
    instead of constructing the path manually.  Manual construction using
    "data/results/<name>/" or "data/<name>/" will NOT match the runner's
    expected path and will cause a metrics-not-found failure (the root cause
    of the Round 5 batch failure, 2026-06-01).

    SH-4 normalization (Testbed 2026-07-03): if HDLAB_EXP_NAME or anchor_name
    already begins with "exp_", strip it before prefixing so the on-disk dir
    is single-prefix `data/exp_<stem>/` rather than double-prefix
    `data/exp_exp_<stem>/`. Historical data at double-prefix dirs remains
    readable via the SH-4 fallback in verify_landing.py, runner_status.py,
    healer.py, purge_pending_reruns.py, remote_state.py, poller.py, and
    scp_recover_landing.py. Emits a stderr warning on normalization so
    process-health audits can trend residual double-prefix queue entries.

    SH-5 run-mode isolation (Testbed 2026-07-03): if the process was invoked
    with `--self-test` or `--smoke` in sys.argv, and HDLAB_EXP_NAME lacks the
    corresponding `_selftest` / `_smoke` suffix, auto-append the suffix so
    selftest / smoke output is ALWAYS isolated from the FULL output path.
    Defense-in-depth against Fix #28 hit #25 (phantom-selftest bug 2026-07-03):
    the queue_add.py 2026-06-30 fix (d4eb28057) isolates selftest_name at the
    queue_add.py caller, but any OTHER caller (exp_dev spawn manual verify,
    ship_anchor.py pre-ship smoke, legacy scripts) that runs
    `python wrapper.py --self-test` with HDLAB_EXP_NAME=<entry_name> (no
    suffix) writes SELFTEST content to data/exp_<entry>/metrics.json,
    polluting the FULL path. This centralized guard closes the class at
    the shared library layer regardless of caller discipline.

    Self-test (called at module import):
        get_output_dir("foo")  -> Path("...data/exp_foo")
        get_output_dir("foo_smoke")  -> Path("...data/exp_foo_smoke")
        HDLAB_EXP_NAME="bar_smoke" with anchor_name="foo" -> Path("...data/exp_bar_smoke")
        get_output_dir("exp_foo") -> Path("...data/exp_foo")  (SH-4 normalized)
        HDLAB_EXP_NAME="foo" with --self-test in argv -> Path("...data/exp_foo_selftest")  (SH-5)
        HDLAB_EXP_NAME="foo" with --smoke in argv -> Path("...data/exp_foo_smoke")  (SH-5)

    Args:
        anchor_name: fallback name to use when HDLAB_EXP_NAME is unset.
                     Typically the script's ANCHOR_NAME constant.

    Returns:
        Path to the output directory (not yet created; caller must mkdir).
    """
    import sys as _sys
    _REPO = Path(__file__).resolve().parent.parent
    name = os.environ.get("HDLAB_EXP_NAME", anchor_name)

    # SH-5 run-mode isolation: defensive-in-depth suffix enforcement.
    # Applied BEFORE SH-4 exp_ strip so both interact cleanly.
    argv = getattr(_sys, "argv", []) or []
    if "--self-test" in argv and not name.endswith("_selftest"):
        _sys.stderr.write(
            f"[SH-5-selftest-isolate] --self-test in argv but HDLAB_EXP_NAME="
            f"{name!r} lacks '_selftest' suffix; auto-appending to isolate "
            f"selftest output from FULL path (data/exp_{name}_selftest/ "
            f"instead of data/exp_{name}/). Defense-in-depth vs Fix #28 "
            f"phantom-selftest recurrence. Callers should set "
            f"HDLAB_EXP_NAME={name}_selftest explicitly.\n"
        )
        name = f"{name}_selftest"
    elif "--smoke" in argv and not name.endswith("_smoke"):
        _sys.stderr.write(
            f"[SH-5-smoke-isolate] --smoke in argv but HDLAB_EXP_NAME="
            f"{name!r} lacks '_smoke' suffix; auto-appending to isolate "
            f"smoke output from FULL path (data/exp_{name}_smoke/ instead "
            f"of data/exp_{name}/). Callers should set HDLAB_EXP_NAME="
            f"{name}_smoke explicitly.\n"
        )
        name = f"{name}_smoke"

    if name.startswith("exp_"):
        stripped = name[len("exp_"):]
        # Guard: don't strip when stripping empties the stem or when the raw
        # dir already exists (means a prior run wrote here; keep consistency).
        if stripped:
            legacy_dir = _REPO / "data" / f"exp_{name}"
            if not legacy_dir.exists():
                _sys.stderr.write(
                    f"[SH-4-normalize] HDLAB_EXP_NAME={name!r} begins with 'exp_'; "
                    f"writing to data/exp_{stripped}/ (canonical) instead of "
                    f"data/exp_{name}/ (double-prefix). See "
                    f"experiments/_seed_checkpoint.get_output_dir docstring.\n"
                )
                name = stripped

    base = _REPO / "data" / f"exp_{name}"

    # --- SH-7 fresh-recompute isolation (added 2026-08-22) -------------------
    # Incident: notes/problems/harness_cannot_recompute/. A landed cell cannot be falsified by
    # re-running it -- completed_units() finds every unit already recorded, the cell skips all of
    # them, and the SAME verdict comes back in ~0.0s having computed nothing. Measured: 403 of
    # 7,875 landed cells replay. "I re-ran it and it matched" is currently not evidence.
    #
    # The only lever that turns a replay into a recompute WITHOUT deleting checkpoints (separately
    # forbidden here, and auto-denied) is to point the cell at a DIFFERENT, EMPTY directory.
    # HDI_FRESH_RUN=<tag> returns a NEW sibling, so completed_units() reads empty and the cell
    # recomputes every unit; the landed dir is never opened for writing, so byte-identity is BY
    # CONSTRUCTION rather than by cleanup. Unset env -> base unchanged, so on-disk behaviour is
    # byte-identical to before this block for every existing cell. Same shape as SH-4/5/6.
    #
    # PROVEN TO BE ABLE TO FAIL, which was the whole deliverable: corrupt one input and re-run
    # fresh -> the verdict FLIPS HARD_PASS to HARD_FAIL; re-run fresh unmodified -> it REPRODUCES.
    # Witness: verification/test_recompute_can_fail.py.
    #
    # COVERAGE IS PARTIAL AND THE NUMBER IS RECOUNTED, NOT INHERITED: of 421 cells carrying a
    # units.jsonl, 87 route output through this function (covered here for free), 275 hold a bare
    # module-level OUTPUT_DIR (each needs a one-line wrap in fresh_run_output_dir), and 59 sources
    # were not located. So this block covers ~21%; the rest keep replaying until migrated.
    _fresh_tag = os.environ.get(_FRESH_ENV, "").strip()
    if _fresh_tag and not base.name.endswith(f"__fresh_{_fresh_tag}"):
        base = base.with_name(f"{base.name}__fresh_{_fresh_tag}")
    return base


# --- SH-6 resolved-run-mode output isolation (added 2026-08-13) --------------
# Incident: notes/metrics_overwrite_forensics_2026-08-13.md. Four cells had a
# real lite/full result overwritten on disk by a later SELF-TEST run, turning
# three genuine negatives (HARD_FAIL / LOCALIZED_WALL / MIDDLE) into
# SELFTEST_PASS:
#   exp_situation_model_assembly_learned_identity_head_v1   (-457 leaf keys)
#   exp_situation_model_assembly_encoder_backed_v1          (-238)
#   exp_situation_model_assembly_encoder_retrain_lite_v1    (-198)
#   exp_syntactic_role_agent_patient_voice_probe_v1         (-81)
#
# Why SH-5 above did NOT catch it, two independent reasons:
#   1. Those cells never call get_output_dir(); they hold a bare module-level
#      OUTPUT_DIR = data/exp_<ANCHOR_NAME> and pass it to every writer.
#   2. SH-5 keys off the STRING "--self-test" in sys.argv. All four cells
#      DEFAULT to self-test when no mode flag is given
#      (`run_mode = "self_test" if args.self_test or not args.full else ...`),
#      so a bare `python exp_foo.py` resolves to self_test with an argv that
#      contains no flag at all -- SH-5 is structurally blind to it.
#
# SH-6 therefore keys off the RESOLVED run_mode the cell actually computed,
# not off argv, and is applied to the bare OUTPUT_DIR constant.

_SELFTEST_RUN_MODES = frozenset({"self_test", "selftest", "self-test"})
_SELFTEST_DIR_SUFFIX = "_selftest"


def isolate_selftest_output_dir(base_output_dir: Any, run_mode: str) -> Any:
    """Return an output dir that a self-test run can never use to clobber a full run.

    SH-6. Keys off the RESOLVED run_mode, not sys.argv (see block comment above).

    self_test -> `<base>_selftest`; every other run_mode -> `<base>` unchanged.
    Idempotent: a base already ending in `_selftest` is returned as-is.
    Preserves the input type (str in -> str out, Path in -> Path out) so it can
    be dropped into cells that use either.

        isolate_selftest_output_dir("d/data/exp_foo", "self_test")
            -> "d/data/exp_foo_selftest"
        isolate_selftest_output_dir("d/data/exp_foo", "lite")
            -> "d/data/exp_foo"
        isolate_selftest_output_dir("d/data/exp_foo_selftest", "self_test")
            -> "d/data/exp_foo_selftest"   (no double-append)
    """
    if run_mode not in _SELFTEST_RUN_MODES:
        return base_output_dir
    was_path = isinstance(base_output_dir, Path)
    text = str(base_output_dir)
    if not text.endswith(_SELFTEST_DIR_SUFFIX):
        text = text + _SELFTEST_DIR_SUFFIX
    return Path(text) if was_path else text


def _selftest_isolate_selftest_output_dir() -> None:
    """Verify SH-6 isolation; runs at module import."""
    base = "/tmp/data/exp_zzz_v1"
    got = isolate_selftest_output_dir(base, "self_test")
    assert got == base + "_selftest", f"SH-6 T1 FAIL: {got}"
    assert got != base, "SH-6 T1 FAIL: self-test dir must differ from full dir"
    for mode in ("full", "lite", "smoke"):
        assert isolate_selftest_output_dir(base, mode) == base, f"SH-6 T2 FAIL: {mode}"
    assert isolate_selftest_output_dir(base + "_selftest", "self_test") == base + "_selftest", (
        "SH-6 T3 FAIL: double-append"
    )
    p = isolate_selftest_output_dir(Path(base), "self_test")
    assert isinstance(p, Path) and p.name == "exp_zzz_v1_selftest", f"SH-6 T4 FAIL: {p}"
    assert isinstance(isolate_selftest_output_dir(base, "full"), str), "SH-6 T4 FAIL: str type"


_selftest_isolate_selftest_output_dir()


# --- OPT-IN structured gate claims (added 2026-07-05, Testbed) --------------
# Machine-clean self-documentation of a cell's HARD-PASS/HARD-FAIL bands so the
# Tier-2 self-audit can read each gate as an exact JSON field instead of
# regex-parsing "metric op threshold -> verdict" out of free-text verdict_msg.
# Spec: notes/research_tier2_selfcheck_structured_field_2026-07-05.md
# (commit 4feca27e3). The CELL computes each claim (it already knows its gate
# math via record_gate); write_metrics just VALIDATES + PERSISTS -- NO regex,
# NO re-derivation from a string. Fully opt-in and backward-compatible: a caller
# that passes no gate_claims produces byte-identical metrics.json to before.

# The five comparison operators a structured gate may use. gate_verdict is
# computed at the source cell's own runtime from its in-scope measured/threshold
# locals -- never inferred later.
_GATE_OP_FUNCS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}
_VALID_GATE_OPS = frozenset(_GATE_OP_FUNCS)


def _gate_number(x: Any, label: str) -> Any:
    """Coerce x to a plain JSON-safe number (int/float); raise on bool/non-numeric.

    Preserves Python int-ness (so a count stays 5, not 5.0); coerces numpy
    scalars / numeric strings to float so json.dumps can serialize them. bool is
    rejected -- a gate measured/threshold is never a boolean (gate_verdict is).
    """
    if isinstance(x, bool):
        raise ValueError(f"{label} must be numeric, not bool")
    if isinstance(x, (int, float)):
        return x
    try:
        return float(x)
    except (TypeError, ValueError):
        raise ValueError(
            f"{label} must be numeric, got {type(x).__name__}: {x!r}")


def record_gate(gate_name: str, measured: Any, threshold: Any, op: str,
                note: Optional[str] = None) -> Dict[str, Any]:
    """Build one normalized structured gate-claim dict with a COMPUTED verdict.

    The gate_verdict is computed HERE, at the cell's own runtime, from the
    cell's own in-scope measured/threshold values -- never re-derived from a
    string later. This is the machine-clean alternative to free-text parsing of
    "metric op threshold -> PASS/FAIL" bands out of verdict_msg.

    Args:
        gate_name: identifier for the gate (e.g. "op_agreement", "flag_recall").
        measured:  measured value (int/float, or numpy scalar / numeric string
                   coercible to one).
        threshold: gate threshold (same numeric contract).
        op:        one of ">=", "<=", "==", ">", "<".
        note:      optional free-text annotation (stored verbatim, never parsed).

    Returns:
        {"gate_name", "measured", "threshold", "op", "gate_verdict"[, "note"]}
        -- a claim that passes write_metrics' validation by construction.

    Raises:
        ValueError on unknown op, empty gate_name, or non-numeric operands.
    """
    if op not in _GATE_OP_FUNCS:
        raise ValueError(
            f"record_gate: op={op!r} not in {sorted(_VALID_GATE_OPS)}")
    if not isinstance(gate_name, str) or not gate_name:
        raise ValueError("record_gate: gate_name must be a non-empty str")
    m = _gate_number(measured, "measured")
    t = _gate_number(threshold, "threshold")
    claim: Dict[str, Any] = {
        "gate_name": gate_name,
        "measured": m,
        "threshold": t,
        "op": op,
        "gate_verdict": bool(_GATE_OP_FUNCS[op](m, t)),
    }
    if note is not None:
        claim["note"] = str(note)
    return claim


def _validate_gate_claims(gate_claims: Any) -> List[Dict[str, Any]]:
    """Validate an opt-in gate_claims list; return a fresh normalized list.

    Each claim MUST be a dict carrying:
        gate_name    -- non-empty str
        measured     -- int/float (not bool)
        threshold    -- int/float (not bool)
        op           -- one of ">=", "<=", "==", ">", "<"
        gate_verdict -- bool
    Optional: note (str, stored verbatim).

    Fail-fast: raises TypeError/ValueError on any malformed input. Does NOT
    mutate the caller's objects and does NOT recompute gate_verdict (record_gate
    owns that computation) -- write_metrics only validates schema + persists.
    Returns a list of dicts with a canonical, deterministic key order.
    """
    if isinstance(gate_claims, (dict, str, bytes)):
        raise TypeError(
            "gate_claims must be a list of claim dicts, "
            f"got {type(gate_claims).__name__}")
    try:
        items = list(gate_claims)
    except TypeError as exc:
        raise TypeError(
            f"gate_claims must be an iterable of claim dicts: {exc}")
    out: List[Dict[str, Any]] = []
    for i, claim in enumerate(items):
        if not isinstance(claim, dict):
            raise TypeError(
                f"gate_claims[{i}] must be a dict, got {type(claim).__name__}")
        required = {"gate_name", "measured", "threshold", "op", "gate_verdict"}
        missing = required - set(claim.keys())
        if missing:
            raise ValueError(
                f"gate_claims[{i}] missing required keys: {sorted(missing)}")
        gate_name = claim["gate_name"]
        if not isinstance(gate_name, str) or not gate_name:
            raise ValueError(
                f"gate_claims[{i}].gate_name must be a non-empty str")
        op = claim["op"]
        if op not in _VALID_GATE_OPS:
            raise ValueError(
                f"gate_claims[{i}].op={op!r} not in {sorted(_VALID_GATE_OPS)}")
        measured = claim["measured"]
        if isinstance(measured, bool) or not isinstance(measured, (int, float)):
            raise ValueError(
                f"gate_claims[{i}].measured must be a non-bool number")
        threshold = claim["threshold"]
        if isinstance(threshold, bool) or \
                not isinstance(threshold, (int, float)):
            raise ValueError(
                f"gate_claims[{i}].threshold must be a non-bool number")
        if not isinstance(claim["gate_verdict"], bool):
            raise ValueError(
                f"gate_claims[{i}].gate_verdict must be a bool")
        norm: Dict[str, Any] = {
            "gate_name": gate_name,
            "measured": measured,
            "threshold": threshold,
            "op": op,
            "gate_verdict": claim["gate_verdict"],
        }
        if claim.get("note") is not None:
            norm["note"] = str(claim["note"])
        out.append(norm)
    return out


def write_metrics(out_dir: Path, metrics: Dict[str, Any],
                  results: Optional[Sequence[Dict[str, Any]]] = None,
                  gate_claims: Optional[Sequence[Dict[str, Any]]] = None
                  ) -> Dict[str, Any]:
    """Write metrics.json guaranteeing the runner's REQUIRED_FIELDS.

    The runner (queue_add.py validate_metrics) rejects a run as
    metrics_invalid unless metrics.json has top-level: verdict, verdict_msg,
    elapsed_s, summary. Scripts often put elapsed_s only inside per_seed and
    omit summary; this helper injects the missing top-level fields so a clean
    science result is not failed on schema. Pass `results` (the per-seed list)
    to derive a total elapsed_s when not already present.

    Root cause of the 2026-06-04 3-anchor metrics_invalid batch.

    OPT-IN structured gate claims (added 2026-07-05, Testbed): pass
    `gate_claims` -- a list of dicts built by record_gate(), each carrying a
    COMPUTED gate_verdict -- to persist them under a NEW top-level key
    "structured_gate_claims". This gives the Tier-2 self-audit an exact
    machine-readable record of each HARD-PASS/HARD-FAIL band instead of
    regex-parsing verdict_msg. Contract:
      * gate_claims=None (default) -> byte-identical output to the pre-2026-07-05
        writer; NOT a single existing caller is affected.
      * gate_claims supplied -> each claim is VALIDATED (schema + op + numeric)
        FAIL-FAST *before* any file write or metrics mutation, so a malformed
        claim surfaces in SMOKE (per the SMOKE=FULL discipline) and can never
        silently corrupt a FULL metrics.json. NO regex, NO verdict re-derivation.
    """
    # Validate opt-in gate_claims FIRST (before mutating metrics / writing the
    # file) so a malformed claim raises with zero side effects. When
    # gate_claims is None this is skipped entirely and the code below is
    # byte-for-byte the original writer.
    validated_gate_claims = (
        _validate_gate_claims(gate_claims) if gate_claims is not None else None)

    if metrics.get("elapsed_s") is None:
        tot = 0.0
        for r in (results or []):
            try:
                tot += float(r.get("elapsed_s") or 0.0)
            except (TypeError, ValueError, AttributeError):
                pass
        metrics["elapsed_s"] = tot
    if not metrics.get("summary"):
        metrics["summary"] = metrics.get("verdict_msg") or metrics.get("verdict") or ""
    if validated_gate_claims is not None:
        metrics["structured_gate_claims"] = validated_gate_claims
    out_dir.mkdir(parents=True, exist_ok=True)
    # Atomic write (tmp + os.replace): a concurrent metrics-sync tar / verify_landing
    # read can otherwise catch a half-written metrics.json (partial JSON -> the
    # orchestrator frames a landed FULL as unreadable/incomplete). os.replace is
    # atomic within a filesystem on POSIX and overwrites atomically on Windows.
    final = out_dir / "metrics.json"
    tmp = final.with_suffix(final.suffix + ".tmp")
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, final)
    return metrics


# --- Vacuous-smoke discriminator-fires guard (added 2026-07-08, Testbed) ------
# Highest-leverage cell-template gate: prevents a green-but-vacuous smoke from
# passing silently. Root cause it closes: at small smoke V/N the frontier /
# negative CONTROL arm (the arm that MUST fail for the experiment to be
# discriminating) also passes -> the smoke tests NOTHING -> the FULL then
# HARD_FAILs. Hit twoband (all arms both=True incl frontier control at V=1500)
# and twohead (achieves-both at smoke, HARD_FAIL at V=40000), 2026-07-08.
# Enforces DISCRIMINATOR-MUST-SURVIVE-SCALE at the smoke's OWN gate.

class VacuousSmokeError(AssertionError):
    """A smoke/self-test's negative control PASSED the headline gate.

    Means the discriminator does not fire at this V/N (every arm passes, incl.
    the one that must fail) -> the smoke is vacuous and a green verdict is
    meaningless. The cell must raise V (and/or N) before any FULL dispatch.
    """


def assert_discriminator_fires(control_passed_headline_gate: bool, *,
                               control_name: str,
                               headline_name: str = "headline",
                               run_mode: str = "smoke",
                               remedy: str = "raise smoke V (and/or N) until the "
                                             "control fails, or route the smoke "
                                             "remote if it cannot be both fast "
                                             "and discriminating",
                               extra: str = "") -> bool:
    """MANDATORY smoke gate: the negative/frontier CONTROL must FAIL the headline.

    Call this in self_test()/smoke AFTER computing arm metrics at the smoke V.
    `control_passed_headline_gate` is a single bool: did the arm that MUST fail
    (the frontier / negative control) actually MEET the headline pass gate at
    this smoke's V/N? If True, the discriminator is doing no work here, so this
    raises VacuousSmokeError and the smoke HARD-fails loudly instead of passing
    on a meaningless green.

    No-op pass-through for FULL runs (run_mode not in smoke/self_test): the FULL
    result IS the science, not a gate self-check.

    Returns True when the guard passes (control correctly failed), so callers can
    fold it into a boolean self-test chain: ok &= assert_discriminator_fires(...).
    """
    if str(run_mode).lower().replace("-", "_") not in (
            "smoke", "self_test", "selftest"):
        return True
    if control_passed_headline_gate:
        raise VacuousSmokeError(
            f"VACUOUS SMOKE: negative/frontier control {control_name!r} PASSED "
            f"the {headline_name!r} gate at run_mode={run_mode} -- the "
            f"discriminator does not fire at this V/N (the arm that MUST fail "
            f"passed). The smoke tests NOTHING; a green verdict is meaningless. "
            f"Remedy: {remedy}." + (f" {extra}" if extra else ""))
    return True


def _selftest_get_output_dir() -> None:
    """Verify get_output_dir produces correct data/exp_<name> paths."""
    import os as _os
    import sys as _sys

    # Save the original env value so we can restore it after the test.
    _orig = _os.environ.get("HDLAB_EXP_NAME")

    # SH-7: NEUTRALISE HDI_FRESH_RUN FOR THE WHOLE SELF-TEST, AND THIS IS NOT A COSMETIC FIX.
    # This self-test runs AT IMPORT. T1 asserts get_output_dir("myanchor_v1") ends in
    # "exp_myanchor_v1"; with HDI_FRESH_RUN set, SH-7 appends "__fresh_<tag>" and the assertion
    # fails -- so EVERY CELL THAT IMPORTS THIS MODULE CRASHED AT IMPORT the moment a fresh run was
    # requested. The switch did not merely fail to redirect; it broke the harness it lives in.
    #
    # Measured 2026-08-23 by running a real landed cell end to end, which is the first time anyone
    # had. THE WITNESS COULD NOT HAVE CAUGHT IT: verification/test_fresh_recompute_redirect.py
    # imports this module and THEN sets the env, so the import-time self-test always ran clean. A
    # real cell has the variable set before Python starts. That ordering is the whole bug.
    #
    # T1-T6 are about SH-4/5/6 naming; SH-7 is tested separately and must not perturb them.
    _orig_fresh = _os.environ.pop(_FRESH_ENV, None)
    # SH-5: neutralize sys.argv for T1-T5 (they pre-date SH-5 and assume no
    # --self-test / --smoke in argv). T6 restores its own argv scope.
    _orig_argv = list(_sys.argv)
    _sys.argv = ["_seed_checkpoint_selftest"]

    try:
        # Test 1: env var absent -> uses anchor_name
        _os.environ.pop("HDLAB_EXP_NAME", None)
        p = get_output_dir("myanchor_v1")
        assert p.name == "exp_myanchor_v1", f"T1 FAIL: got {p.name}"
        assert p.parent.name == "data", f"T1 parent FAIL: got {p.parent.name}"

        # Test 2: env var set -> uses env var (runner path)
        _os.environ["HDLAB_EXP_NAME"] = "myanchor_v1_smoke"
        p2 = get_output_dir("myanchor_v1")
        assert p2.name == "exp_myanchor_v1_smoke", f"T2 FAIL: got {p2.name}"

        # Test 3: runner sets env to full anchor name (non-smoke FULL run)
        _os.environ["HDLAB_EXP_NAME"] = "myanchor_v1"
        p3 = get_output_dir("myanchor_v1")
        assert p3.name == "exp_myanchor_v1", f"T3 FAIL: got {p3.name}"

        # Test 4: path segment is always data/exp_<name>, never data/results/<name>
        _os.environ.pop("HDLAB_EXP_NAME", None)
        p4 = get_output_dir("ne1_mct_aging_signature_v1")
        parts = p4.parts
        assert "exp_ne1_mct_aging_signature_v1" in parts, f"T4 FAIL: parts={parts}"
        assert "results" not in parts, f"T4 FAIL: 'results' found in path: {p4}"

        # Test 5 (SH-4 normalization): env var already begins with 'exp_' -> strip.
        # Only fires when data/exp_exp_<stem>/ does NOT exist on disk (avoids
        # breaking cells with existing checkpoints at the double-prefix dir).
        # Uses a very-unlikely stem so the legacy-dir guard never fires here.
        _os.environ["HDLAB_EXP_NAME"] = "exp_sh4_normalize_selftest_zzz_v1"
        p5 = get_output_dir("fallback_anchor_unused")
        assert p5.name == "exp_sh4_normalize_selftest_zzz_v1", (
            f"T5 (SH-4) FAIL: got {p5.name} (expected single-prefix)"
        )

        # Test 6 (SH-5 selftest isolation): --self-test in argv + HDLAB_EXP_NAME
        # without _selftest suffix -> auto-append. Defense vs Fix #28 hit #25.
        import sys as _sys_t6
        _t6_saved_argv = list(_sys_t6.argv)
        try:
            _sys_t6.argv = ["wrapper.py", "--self-test"]
            _os.environ["HDLAB_EXP_NAME"] = "sh5_probe_zzz_v1_s7"
            p6 = get_output_dir("fallback_unused")
            assert p6.name == "exp_sh5_probe_zzz_v1_s7_selftest", (
                f"T6 (SH-5 selftest auto-append) FAIL: got {p6.name}"
            )
            # Already-suffixed case: no double-append.
            _os.environ["HDLAB_EXP_NAME"] = "sh5_probe_zzz_v1_s7_selftest"
            p6b = get_output_dir("fallback_unused")
            assert p6b.name == "exp_sh5_probe_zzz_v1_s7_selftest", (
                f"T6b (SH-5 no double-append) FAIL: got {p6b.name}"
            )
            # Smoke branch: --smoke without _smoke suffix -> auto-append.
            _sys_t6.argv = ["wrapper.py", "--smoke"]
            _os.environ["HDLAB_EXP_NAME"] = "sh5_probe_zzz_v1_s7"
            p6c = get_output_dir("fallback_unused")
            assert p6c.name == "exp_sh5_probe_zzz_v1_s7_smoke", (
                f"T6c (SH-5 smoke auto-append) FAIL: got {p6c.name}"
            )
            # FULL dispatch: no --self-test / --smoke in argv -> no suffix mutation.
            _sys_t6.argv = ["wrapper.py"]
            _os.environ["HDLAB_EXP_NAME"] = "sh5_probe_zzz_v1_s7"
            p6d = get_output_dir("fallback_unused")
            assert p6d.name == "exp_sh5_probe_zzz_v1_s7", (
                f"T6d (SH-5 FULL passthrough) FAIL: got {p6d.name}"
            )
        finally:
            _sys_t6.argv = _t6_saved_argv
    finally:
        # Restore original env state (set or absent) so subsequent imports
        # and tests see the same env the caller had.
        if _orig is None:
            _os.environ.pop("HDLAB_EXP_NAME", None)
        else:
            _os.environ["HDLAB_EXP_NAME"] = _orig
        if _orig_fresh is not None:
            _os.environ[_FRESH_ENV] = _orig_fresh
        _sys.argv = _orig_argv


_selftest_get_output_dir()


__all__ = [
    "config_fingerprint",
    "checkpoint_key",
    "write_partial_config",
    "resumable_seeds_config",
    "list_completed_keys_config",
    "aggregate_partials_config",
    "CheckpointConfigMismatchError",
    "list_completed_keys",
    "resumable_seeds",
    "write_partial",
    "write_partial_key",
    "load_partial_key",
    "aggregate_partials",
    "clear_partials",
    "_check_run_config",
    "get_output_dir",
    "isolate_selftest_output_dir",
    "write_metrics",
    "record_gate",
    "assert_discriminator_fires",
    "VacuousSmokeError",
]


if __name__ == "__main__":
    # Self-test: write a fake smoke partial with mismatched N/M, run the loader,
    # verify it gets REJECTED when run_config specifies FULL N/M.
    import tempfile

    print("[selftest] _seed_checkpoint.py PROT-021 config-mismatch guard")

    with tempfile.TemporaryDirectory() as tmpdir:
        td = Path(tmpdir)

        # --- Test 1: smoke partial (N=1024, M=256) rejected by FULL run_config ---
        smoke_payload = {
            "seed": "M256_seed17",
            "N": 1024,
            "M": 256,
            "run_mode": "smoke",
            "ok": True,
            "acc_gated": 1.0,
            "_partial_written_at": time.time(),
        }
        write_partial_key(td, "M256_seed17", smoke_payload)
        assert (td / "partial_metrics_M256_seed17.json").exists(), "write failed"

        # Without run_config: should be accepted (legacy behaviour)
        keys_no_cfg = list_completed_keys(td)
        assert "M256_seed17" in keys_no_cfg, f"legacy accept failed: {keys_no_cfg}"
        print("[selftest] T1a PASS: smoke partial accepted when no run_config")

        # With FULL run_config (N=16384, M=2048): should be REJECTED
        full_cfg = {"N": 16384, "M": 2048, "run_mode": "full"}
        keys_full = list_completed_keys(td, run_config=full_cfg)
        assert "M256_seed17" not in keys_full, (
            f"FAIL: smoke partial was NOT rejected by FULL run_config: {keys_full}")
        print("[selftest] T1b PASS: smoke partial REJECTED by FULL run_config N=16384 M=2048")

        # --- Test 2: matching partial accepted ---
        full_payload = {
            "seed": "M2048_seed17",
            "N": 16384,
            "M": 2048,
            "run_mode": "full",
            "ok": True,
            "acc_gated": 0.97,
            "_partial_written_at": time.time(),
        }
        write_partial_key(td, "M2048_seed17", full_payload)
        keys_full2 = list_completed_keys(td, run_config=full_cfg)
        assert "M2048_seed17" in keys_full2, (
            f"FAIL: matching FULL partial was incorrectly rejected: {keys_full2}")
        assert "M256_seed17" not in keys_full2, "smoke still leaking after T2"
        print("[selftest] T2 PASS: matching FULL partial M=2048 N=16384 accepted")

        # --- Test 3: N-only run_config (no M key) ---
        n_only_cfg = {"N": 16384}
        keys_n_only = list_completed_keys(td, run_config=n_only_cfg)
        # M256_seed17 has N=1024 -> rejected
        assert "M256_seed17" not in keys_n_only, "N-only check failed to reject smoke"
        # M2048_seed17 has N=16384 -> accepted
        assert "M2048_seed17" in keys_n_only, "N-only check incorrectly rejected FULL"
        print("[selftest] T3 PASS: N-only run_config filters correctly")

        # --- Test 4: resumable_seeds with run_config ---
        seeds_test = ["M2048_seed17", "M2048_seed23", "M256_seed17"]
        done, remaining = resumable_seeds(seeds_test, td, run_config=full_cfg)
        assert "M2048_seed17" in done, f"should be done: {done}"
        assert "M256_seed17" not in done, f"smoke should NOT be done: {done}"
        assert "M2048_seed23" in remaining, f"should be remaining: {remaining}"
        assert "M256_seed17" in remaining, f"smoke should be remaining: {remaining}"
        print(f"[selftest] T4 PASS: resumable_seeds done={done} remaining={remaining}")

        # --- Test 5: run_mode "smoke" rejection by run_mode="full" ---
        mode_cfg = {"run_mode": "full"}
        keys_mode = list_completed_keys(td, run_config=mode_cfg)
        # M256_seed17 has run_mode="smoke" -> rejected
        assert "M256_seed17" not in keys_mode, "run_mode check failed to reject smoke"
        # M2048_seed17 has run_mode="full" -> accepted
        assert "M2048_seed17" in keys_mode, "run_mode check incorrectly rejected full"
        print("[selftest] T5 PASS: run_mode filter correct")

        # --- Test 6: aggregate_partials with run_config ---
        agg = aggregate_partials(td, run_config=full_cfg)
        assert "M2048_seed17" in agg, f"agg missing FULL key: {list(agg.keys())}"
        assert "M256_seed17" not in agg, f"agg should not contain smoke key: {list(agg.keys())}"
        assert agg["M2048_seed17"]["acc_gated"] == 0.97, "agg data mismatch"
        print("[selftest] T6 PASS: aggregate_partials filters smoke with run_config")

        # --- Test 7: anchor-name guard rejects alien partials (added 2026-06-27)
        # META_RULE_H_ANCHOR: partial whose config_version ANCHOR= mismatches
        # the caller's anchor must be rejected.  Catches cross-cell partial
        # contamination from import-time-side-effect bugs.
        alien_payload = {
            "seed": "seed42",
            "N": 16384,
            "M": 2048,
            "run_mode": "full",
            "config_version": "ANCHOR=other_cell_v9,N=16384,M=2048,alpha=1.5",
            "anchor_name": "other_cell_v9",
            "ok": True,
            "acc_gated": 0.88,
        }
        write_partial_key(td, "seed42", alien_payload)
        # Without anchor check: accepted (legacy)
        cfg_no_anchor = {"N": 16384, "M": 2048, "run_mode": "full"}
        keys_no_anchor = list_completed_keys(td, run_config=cfg_no_anchor)
        assert "seed42" in keys_no_anchor, "legacy w/o anchor should accept"
        # With anchor check: rejected (alien cell wrote this partial)
        cfg_with_anchor = {"N": 16384, "M": 2048, "run_mode": "full",
                           "anchor": "my_real_cell_v1"}
        keys_with_anchor = list_completed_keys(td, run_config=cfg_with_anchor)
        assert "seed42" not in keys_with_anchor, (
            f"FAIL: alien partial NOT rejected by anchor check: "
            f"{keys_with_anchor}")
        # Matching anchor: accepted
        cfg_match = {"N": 16384, "M": 2048, "run_mode": "full",
                     "anchor": "other_cell_v9"}
        keys_match = list_completed_keys(td, run_config=cfg_match)
        assert "seed42" in keys_match, (
            f"FAIL: matching-anchor partial incorrectly rejected: {keys_match}")
        print("[selftest] T7 PASS: META_RULE_H_ANCHOR rejects alien partial; "
              "accepts matching anchor")

        # --- Test 8: config_version ANCHOR=<name>,... pattern parsing ---
        cv_payload = {
            "seed": "seed99",
            "N": 16384,
            "M": 2048,
            "run_mode": "full",
            "config_version": "ANCHOR=alien_v2,N=16384,M=2048,alpha=2.0",
            "ok": True,
        }
        write_partial_key(td, "seed99", cv_payload)
        cfg_anchor_a = {"N": 16384, "M": 2048, "run_mode": "full",
                        "anchor": "expected_cell"}
        keys_a = list_completed_keys(td, run_config=cfg_anchor_a)
        assert "seed99" not in keys_a, (
            "FAIL: config_version-only ANCHOR mismatch not caught")
        cfg_anchor_b = {"N": 16384, "M": 2048, "run_mode": "full",
                        "anchor": "alien_v2"}
        keys_b = list_completed_keys(td, run_config=cfg_anchor_b)
        assert "seed99" in keys_b, "matching ANCHOR via config_version rejected"
        print("[selftest] T8 PASS: ANCHOR= regex parses config_version field")

        # --- Test 9: assert_discriminator_fires (vacuous-smoke guard) ---------
        # Control that FAILS the headline (passed=False) -> guard passes (True).
        assert assert_discriminator_fires(
            False, control_name="frontier", run_mode="smoke") is True, \
            "T9a FAIL: guard should pass when control fails headline"
        # Control that PASSES the headline at smoke -> VacuousSmokeError.
        try:
            assert_discriminator_fires(
                True, control_name="frontier", run_mode="smoke")
            raise AssertionError("T9b FAIL: expected VacuousSmokeError")
        except VacuousSmokeError:
            pass
        # FULL run -> no-op pass-through even when control 'passes'.
        assert assert_discriminator_fires(
            True, control_name="frontier", run_mode="full") is True, \
            "T9c FAIL: FULL must be a no-op pass-through"
        # self_test / self-test aliases behave like smoke.
        for _m in ("self_test", "self-test", "selftest"):
            try:
                assert_discriminator_fires(True, control_name="c", run_mode=_m)
                raise AssertionError(f"T9d FAIL: {_m} should gate like smoke")
            except VacuousSmokeError:
                pass
        print("[selftest] T9 PASS: assert_discriminator_fires gates vacuous "
              "smoke; no-ops on FULL")

        # --- Test 10: write_metrics atomicity + required-field injection ------
        wm_dir = td / "wm_atomic"
        m = write_metrics(wm_dir, {"verdict": "HARD_PASS", "verdict_msg": "ok"},
                          results=[{"elapsed_s": 1.5}, {"elapsed_s": 2.5}])
        assert (wm_dir / "metrics.json").exists(), "T10a FAIL: metrics.json absent"
        assert not (wm_dir / "metrics.json.tmp").exists(), \
            "T10b FAIL: .tmp residue left after atomic write"
        assert m["elapsed_s"] == 4.0, f"T10c FAIL: elapsed_s={m['elapsed_s']}"
        assert m["summary"], "T10d FAIL: summary not injected"
        print("[selftest] T10 PASS: write_metrics atomic (tmp+replace, no residue)")

        # --- Tests 11-14: PROT-021b config-fingerprinted keys ----------------
        # T11 is the REGRESSION TEST for the original collision: it drives the
        # exact smoke-then-full sequence that produced it and asserts the full
        # actually computes. T12 proves the loud guard. T13 covers the pre-fix
        # bare-seed artifact still on disk in the affected dirs. T14 proves the
        # legacy contract is untouched for a run already in flight.
        SMOKE_CFG = {"run_mode": "smoke", "N": 1024, "D": 64, "M": 256}
        FULL_CFG = {"run_mode": "full", "N": 16384, "D": 512, "M": 2048}

        # --- Test 11: smoke and full share an out_dir and DO NOT collide -----
        t11 = td / "t11_shared_out_dir"
        computed = []

        def _run(seeds, cfg, tag):
            done, remaining = resumable_seeds_config(seeds, t11, cfg)
            for s in remaining:
                computed.append((tag, s))
                write_partial_config(t11, s, {"N": cfg["N"], "M": cfg["M"],
                                              "run_mode": cfg["run_mode"],
                                              "acc": 0.5 if tag == "smoke" else 0.97},
                                     cfg)
            return done, remaining

        _run([17], SMOKE_CFG, "smoke")           # the smoke gate
        computed.clear()
        done11, rem11 = _run([7, 17, 23], FULL_CFG, "full")   # the FULL dispatch
        assert done11 == [], (
            f"T11 FAIL (ORIGINAL COLLISION IS BACK): FULL treated {done11} as "
            f"already complete off the smoke's checkpoints")
        assert sorted(s for _, s in computed) == [7, 17, 23], (
            f"T11 FAIL: FULL did not compute every seed; computed={computed}")
        agg11 = aggregate_partials_config(t11, [7, 17, 23], FULL_CFG)
        assert set(agg11) == {"7", "17", "23"}, f"T11 FAIL: agg={sorted(agg11)}"
        assert all(v["N"] == 16384 and v["run_mode"] == "full"
                   for v in agg11.values()), (
            f"T11 FAIL: FULL aggregate carries smoke-scale data: {agg11}")
        # The smoke's own partial still exists, untouched, at its own key.
        assert load_partial_key(t11, checkpoint_key(17, SMOKE_CFG))["N"] == 1024, \
            "T11 FAIL: FULL overwrote the smoke's partial"
        print("[selftest] T11 PASS: smoke+full in ONE out_dir -> distinct keys, "
              "FULL computed all 3 seeds, both artifacts preserved")

        # --- Test 12: a config-mismatched checkpoint RAISES, never reloads ---
        t12 = td / "t12_mismatch"
        # A partial parked at the FULL key but stamped with the smoke config.
        write_partial_key(t12, checkpoint_key(17, FULL_CFG),
                          {"N": 1024, "run_mode": "smoke",
                           "_ckpt_config_fp": config_fingerprint(SMOKE_CFG),
                           "_ckpt_config": _canonical_config(SMOKE_CFG)})
        try:
            resumable_seeds_config([17], t12, FULL_CFG)
            raise AssertionError(
                "T12 FAIL: mismatched checkpoint was accepted instead of raising")
        except CheckpointConfigMismatchError as exc:
            assert "17" in str(exc), f"T12 FAIL: unhelpful message: {exc}"
        # aggregate_partials_config must refuse on the same footing.
        try:
            aggregate_partials_config(t12, [17], FULL_CFG)
            raise AssertionError("T12b FAIL: aggregate accepted a mismatch")
        except CheckpointConfigMismatchError:
            pass
        print("[selftest] T12 PASS: mismatched checkpoint RAISES "
              "CheckpointConfigMismatchError (not skipped, not reloaded)")

        # --- Test 13: pre-fix bare-seed smoke artifact -> loud, not silent ---
        t13 = td / "t13_legacy_bare"
        write_partial(t13, 17, {"seed": 17, "N": 1024, "M": 256,
                                "run_mode": "smoke", "acc": 0.5})
        try:
            resumable_seeds_config([17], t13, FULL_CFG)
            raise AssertionError(
                "T13 FAIL: pre-fix bare-seed smoke partial silently tolerated")
        except CheckpointConfigMismatchError as exc:
            assert "N" in str(exc) and "run_mode" in str(exc), \
                f"T13 FAIL: message does not name the contradicting fields: {exc}"
        # A bare partial with nothing comparable is ignored (recompute), not fatal.
        t13b = td / "t13b_opaque"
        write_partial(t13b, 17, {"seed": 17, "acc": 0.5})
        assert resumable_seeds_config([17], t13b, FULL_CFG) == ([], [17]), \
            "T13b FAIL: opaque legacy partial should be ignored, seed recomputed"
        print("[selftest] T13 PASS: pre-fix bare-seed partial RAISES when it "
              "contradicts; recomputes when unverifiable")

        # --- Test 14: legacy contract byte-unchanged (in-flight run safety) --
        t14 = td / "t14_legacy_compat"
        p14 = write_partial(t14, 17, {"seed": 17, "N": 1024, "acc": 0.5})
        assert p14.name == "partial_metrics_17.json", \
            f"T14 FAIL: legacy write_partial changed its filename: {p14.name}"
        assert list_completed_keys(t14) == ["17"], \
            "T14 FAIL: legacy list_completed_keys changed behaviour"
        assert resumable_seeds([17, 23], t14) == ([17], [23]), \
            "T14 FAIL: legacy resumable_seeds changed behaviour"
        assert list_completed_keys(t14, run_config={"N": 16384}) == [], \
            "T14 FAIL: legacy PROT-021 run_config filter changed behaviour"
        assert "17" in aggregate_partials(t14, [17]), \
            "T14 FAIL: legacy aggregate_partials changed behaviour"
        print("[selftest] T14 PASS: legacy API unchanged (filenames, keys, "
              "PROT-021 filter) -- a run already in flight is unaffected")

    print("[selftest] ALL 14 TESTS PASS -- PROT-021 + META_RULE_H_ANCHOR "
          "loader guard + vacuous-smoke guard + atomic write + PROT-021b "
          "config-fingerprinted keys operational")
