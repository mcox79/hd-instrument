"""hd_index_refresh -- cron follow-on that keeps the bge semantic index fresh over the full substrate corpus (REMOTE GPU).

CACHE-ONLY (Skunkworks bar = the Action A bge-refresh cell bar, already VET'd GO). Delegates the heavy bge encode to
experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py (which writes cached_indices/*.npz ONLY -- ZERO substrate-atom
mutation -- and gates coverage == n_atoms). This wrapper adds the cron layer: an N-atom-delta / daily trigger (don't re-run
the heavy encode every tick), coverage-gap alerting, and unattended staleness observability.

UNATTENDED-SAFETY (the monitor lesson; same cross-cutting bar as hd_metrics_atomize): verify OUTPUT not liveness. status.json
records the coverage gate RESULT + atoms-indexed + index-staleness (atoms-since-last-embed); a coverage shortfall writes
data/.index_coverage_gap; the DASHBOARD reads last_success_utc + stale_after_s to raise a stall alert (no pipeline validates
its own death -- the freshness ground-truth does). REMOTE-ONLY: a laptop full-encode path is a HARD-FAIL of compute policy.

Run (REMOTE GPU): python tools/hd_index_refresh.py            (honors the N-delta trigger)
                  python tools/hd_index_refresh.py --force    (force re-embed now)
                  python tools/hd_index_refresh.py --dry-run  (trigger-decision + counts only; no encode; for Skunkworks VET)
ASCII-only.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO / "data" / "substrate_index"
STATUS_DIR = REPO / "data" / ".index_refresh"
LOCK = STATUS_DIR / ".lock"
STATUS = STATUS_DIR / "status.json"
LOG = STATUS_DIR / "refresh.log"
COVERAGE_GAP_FLAG = REPO / "data" / ".index_coverage_gap"
CELL = REPO / "experiments" / "exp_substrate_bge_index_refresh_full_corpus_v1.py"
LOCK_STALE_S = 3 * 3600       # 3h: bge encode is slow; a lock older than this is abandoned
N_DELTA_THRESHOLD = 200       # re-embed only when >= this many new atoms since last successful embed ...
DAILY_S = 24 * 3600           # ... OR if it has been > 24h since the last successful embed (daily floor)
STALE_AFTER_S = 36 * 3600     # no successful embed in 36h while atoms grew -> dashboard stall alert


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _acquire_lock() -> bool:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            if (_ts() - LOCK.stat().st_mtime) < LOCK_STALE_S:
                return False
        except FileNotFoundError:
            pass
    LOCK.write_text(_now(), encoding="utf-8")
    return True


def _release_lock() -> None:
    try:
        LOCK.unlink()
    except FileNotFoundError:
        pass


def _current_n_atoms() -> int:
    from backend.substrate_index.partition import PartitionedStore
    return len(PartitionedStore(DATA_ROOT).all_atoms())


def _prior() -> dict:
    try:
        return json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {}
    except Exception:
        return {}


def _should_run(n_now: int, prior: dict) -> tuple[bool, str]:
    last_n = prior.get("atoms_indexed_at_last_embed")
    last_t = prior.get("last_success_utc")
    if last_n is None or last_t is None:
        return True, "no prior successful embed"
    delta = n_now - int(last_n)
    if delta >= N_DELTA_THRESHOLD:
        return True, f"atom-delta {delta} >= {N_DELTA_THRESHOLD}"
    try:
        age = _ts() - datetime.fromisoformat(last_t).timestamp()
    except Exception:
        age = DAILY_S + 1
    if age > DAILY_S:
        return True, f"daily floor ({int(age)}s since last embed > {DAILY_S}s)"
    return False, f"no trigger (delta {delta} < {N_DELTA_THRESHOLD}; age {int(age)}s < {DAILY_S}s)"


def _run_cell() -> dict:
    """Delegate the heavy encode to the Action-A cell (CUDA-asserted, cache-only, coverage-gated). Returns its metrics."""
    env = dict(os.environ, HDLAB_RUN_MODE="full", HDLAB_EXP_NAME="bge_index_refresh_full_corpus_v1")
    proc = subprocess.run([sys.executable, str(CELL)], cwd=str(REPO), env=env, capture_output=True, text=True)
    out = REPO / "data" / "exp_bge_index_refresh_full_corpus_v1" / "metrics.json"
    metrics = {}
    if out.exists():
        try:
            metrics = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            metrics = {}
    return {"returncode": proc.returncode, "metrics": metrics, "stdout_tail": proc.stdout[-1500:], "stderr_tail": proc.stderr[-800:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="force re-embed regardless of the N-delta/daily trigger")
    ap.add_argument("--dry-run", action="store_true", help="trigger-decision + counts only; NO encode (Skunkworks VET)")
    args, _ = ap.parse_known_args()

    prior = _prior()
    try:
        n_now = _current_n_atoms()
    except Exception as e:
        print(f"[hd_index_refresh] cannot enumerate corpus: {str(e)[:120]}", flush=True)
        return 1
    should, why = (True, "forced") if args.force else _should_run(n_now, prior)

    if getattr(args, "dry_run", False):
        print(f"[hd_index_refresh] DRY-RUN: n_atoms={n_now}; would_run={should} ({why}); NO encode. "
              f"last_embed_n={prior.get('atoms_indexed_at_last_embed')} last_success={prior.get('last_success_utc')}", flush=True)
        return 0

    if not should:
        print(f"[hd_index_refresh] skip: {why} (n_atoms={n_now}).", flush=True)
        return 0
    if not _acquire_lock():
        print("[hd_index_refresh] another run holds the lock (fresh); skipping this tick.", flush=True)
        return 0
    try:
        r = _run_cell()
        m = r["metrics"]
        indexed = m.get("atoms_indexed")
        coverage_ok = (m.get("verdict") == "OK") and (indexed == n_now)
        now = _now()
        status = dict(
            last_run_utc=now,
            last_success_utc=(now if coverage_ok else prior.get("last_success_utc")),
            stale_after_s=STALE_AFTER_S,
            exit_code=r["returncode"],
            n_atoms=n_now,
            atoms_indexed=indexed,
            atoms_indexed_at_last_embed=(n_now if coverage_ok else prior.get("atoms_indexed_at_last_embed")),
            index_coverage_pct=m.get("index_coverage_pct"),
            target_cache_file=m.get("target_cache_file"),
            index_staleness_atoms=(0 if coverage_ok else (n_now - int(prior.get("atoms_indexed_at_last_embed", 0)))),
            coverage_ok=coverage_ok,
            trigger=why,
        )
        STATUS.write_text(json.dumps(status, indent=2), encoding="utf-8")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{now}\tn_atoms={n_now}\tindexed={indexed}\tcoverage_ok={coverage_ok}\texit={r['returncode']}\t{why}\n")
        if not coverage_ok:
            COVERAGE_GAP_FLAG.write_text(f"{now} hd_index_refresh coverage_ok=False indexed={indexed}/{n_now} "
                                         f"verdict={m.get('verdict')} exit={r['returncode']}\n", encoding="utf-8")
            sys.stderr.write(r["stdout_tail"] + "\n" + r["stderr_tail"])
            print(f"[hd_index_refresh] COVERAGE GAP -> wrote {COVERAGE_GAP_FLAG.name}; indexed {indexed}/{n_now}.", flush=True)
            return 1
        print(f"[hd_index_refresh] OK: indexed {indexed}/{n_now} (100%); cache={m.get('target_cache_file')}; trigger={why}.", flush=True)
        return 0
    finally:
        _release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
