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
    return done


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

    Self-test (called at module import):
        get_output_dir("foo")  -> Path("...data/exp_foo")
        get_output_dir("foo_smoke")  -> Path("...data/exp_foo_smoke")
        HDLAB_EXP_NAME="bar_smoke" with anchor_name="foo" -> Path("...data/exp_bar_smoke")
        get_output_dir("exp_foo") -> Path("...data/exp_foo")  (SH-4 normalized)

    Args:
        anchor_name: fallback name to use when HDLAB_EXP_NAME is unset.
                     Typically the script's ANCHOR_NAME constant.

    Returns:
        Path to the output directory (not yet created; caller must mkdir).
    """
    _REPO = Path(__file__).resolve().parent.parent
    name = os.environ.get("HDLAB_EXP_NAME", anchor_name)
    if name.startswith("exp_"):
        stripped = name[len("exp_"):]
        # Guard: don't strip when stripping empties the stem or when the raw
        # dir already exists (means a prior run wrote here; keep consistency).
        if stripped:
            legacy_dir = _REPO / "data" / f"exp_{name}"
            if not legacy_dir.exists():
                import sys as _sys
                _sys.stderr.write(
                    f"[SH-4-normalize] HDLAB_EXP_NAME={name!r} begins with 'exp_'; "
                    f"writing to data/exp_{stripped}/ (canonical) instead of "
                    f"data/exp_{name}/ (double-prefix). See "
                    f"experiments/_seed_checkpoint.get_output_dir docstring.\n"
                )
                name = stripped
    return _REPO / "data" / f"exp_{name}"


def write_metrics(out_dir: Path, metrics: Dict[str, Any],
                  results: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Write metrics.json guaranteeing the runner's REQUIRED_FIELDS.

    The runner (queue_add.py validate_metrics) rejects a run as
    metrics_invalid unless metrics.json has top-level: verdict, verdict_msg,
    elapsed_s, summary. Scripts often put elapsed_s only inside per_seed and
    omit summary; this helper injects the missing top-level fields so a clean
    science result is not failed on schema. Pass `results` (the per-seed list)
    to derive a total elapsed_s when not already present.

    Root cause of the 2026-06-04 3-anchor metrics_invalid batch.
    """
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
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def _selftest_get_output_dir() -> None:
    """Verify get_output_dir produces correct data/exp_<name> paths."""
    import os as _os

    # Save the original env value so we can restore it after the test.
    _orig = _os.environ.get("HDLAB_EXP_NAME")

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
    finally:
        # Restore original env state (set or absent) so subsequent imports
        # and tests see the same env the caller had.
        if _orig is None:
            _os.environ.pop("HDLAB_EXP_NAME", None)
        else:
            _os.environ["HDLAB_EXP_NAME"] = _orig


_selftest_get_output_dir()


__all__ = [
    "list_completed_keys",
    "resumable_seeds",
    "write_partial",
    "write_partial_key",
    "load_partial_key",
    "aggregate_partials",
    "clear_partials",
    "_check_run_config",
    "get_output_dir",
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

    print("[selftest] ALL 8 TESTS PASS -- PROT-021 + META_RULE_H_ANCHOR "
          "loader guard operational")
