"""hd_metrics_atomize -- cron follow-on to hd_metrics_sync (Director RATIFY 2026-06-17; Action C pipeline half).

Runs AFTER each successful metrics sync: ingests any newly-synced metrics.json into the substrate as
EXPERIMENT_RECORD atoms by invoking the already-VET'd atomizer (tools/atomize_experiment_records.py) in APPLY mode.
Idempotent (Store.add_atom collision-skip) + per-batch cap_pres + axiom_term HARD-FAIL gates are INSIDE the atomizer
(this wrapper only orchestrates, records status, and raises the gate-fail flag). Mirrors the hd_metrics_sync
status/log/lock discipline (data/.metrics_atomize/).

Cert-discipline (Skunkworks SCHEMA-VET gate before Orchestrator install): bulk-mutating substrate-write infra;
axiom_term must stay 206/206, cap_pres 6/6, dup-qids 0, current_best unchanged -- all enforced by the atomizer's
per-batch HARD-FAIL gates (already in production + Skunkworks-VET'd). On any HARD_FAIL the atomizer HALTs (exit 1);
this wrapper then writes data/.substrate_gate_fail (dashboard-visible) and exits non-zero.

Run: python tools/hd_metrics_atomize.py   (system python; the atomizer's deps are present there, no .venv needed)
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATUS_DIR = REPO / "data" / ".metrics_atomize"
LOCK = STATUS_DIR / ".lock"
STATUS = STATUS_DIR / "status.json"
LOG = STATUS_DIR / "atomize.log"
GATE_FAIL_FLAG = REPO / "data" / ".substrate_gate_fail"
LOCK_STALE_S = 1800   # 30 min: a lock older than this is treated as abandoned (mirror sync concurrent-protection)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _acquire_lock() -> bool:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            age = (datetime.now(timezone.utc).timestamp() - LOCK.stat().st_mtime)
            if age < LOCK_STALE_S:
                return False                       # a fresh run holds the lock -> skip (concurrent-protection)
        except FileNotFoundError:
            pass
    LOCK.write_text(_now(), encoding="utf-8")
    return True


def _release_lock() -> None:
    try:
        LOCK.unlink()
    except FileNotFoundError:
        pass


def _parse(stdout: str) -> dict:
    """Deterministic parse of the atomizer's APPLY output (no LLM)."""
    added = 0
    m = re.search(r"APPLY DONE:\s*\+(\d+)\s+atoms", stdout)
    if m:
        added = int(m.group(1))
    at = re.findall(r"axiom_term=(\d+)/(\d+)", stdout)
    axiom_term = f"{at[-1][0]}/{at[-1][1]}" if at else None
    cap_pres = ("cap_pres(mod6/6)=True" in stdout)
    hard_fail = ("HARD_FAIL" in stdout)
    total = None
    mt = re.search(r"(\d+)\s+EXPERIMENT_RECORD atoms total in-store", stdout)
    if mt:
        total = int(mt.group(1))
    return dict(atoms_added=added, axiom_term=axiom_term, cap_pres=cap_pres,
                hard_fail=hard_fail, total_exp_atoms=total)


def main() -> int:
    if not _acquire_lock():
        print("[hd_metrics_atomize] another run holds the lock (fresh); skipping this tick.", flush=True)
        return 0
    try:
        env = dict(os.environ, HDLAB_ATOMIZE_APPLY="1", HDLAB_ATOMIZE_LIMIT="1000000")
        proc = subprocess.run([sys.executable, str(REPO / "tools" / "atomize_experiment_records.py")],
                              cwd=str(REPO), env=env, capture_output=True, text=True)
        info = _parse(proc.stdout)
        # gate_ok: clean exit + no HARD_FAIL + cap_pres confirmed -- OR nothing was added (0 batches => no per-batch
        # cap_pres line printed, which is NOT a failure; an idempotent no-op tick is trivially safe).
        gate_ok = (proc.returncode == 0) and (not info["hard_fail"]) and (info["cap_pres"] or info["atoms_added"] == 0)
        status = dict(
            last_run_utc=_now(),
            exit_code=proc.returncode,
            atoms_added=info["atoms_added"],
            total_exp_atoms=info["total_exp_atoms"],
            axiom_term=info["axiom_term"],
            cap_pres_6_6=info["cap_pres"],
            gate_ok=gate_ok,
        )
        STATUS.write_text(json.dumps(status, indent=2), encoding="utf-8")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{status['last_run_utc']}\t+{info['atoms_added']} atoms\taxiom_term={info['axiom_term']}\t"
                    f"cap_pres={info['cap_pres']}\tgate_ok={gate_ok}\texit={proc.returncode}\n")
        if not gate_ok:
            GATE_FAIL_FLAG.write_text(f"{status['last_run_utc']} hd_metrics_atomize gate_ok=False "
                                      f"exit={proc.returncode} hard_fail={info['hard_fail']} "
                                      f"cap_pres={info['cap_pres']}\n", encoding="utf-8")
            # surface the atomizer tail for diagnosis
            sys.stderr.write(proc.stdout[-2000:] + "\n" + proc.stderr[-1000:])
            print(f"[hd_metrics_atomize] GATE FAIL -> wrote {GATE_FAIL_FLAG.name}; HALT.", flush=True)
            return 1
        print(f"[hd_metrics_atomize] OK: +{info['atoms_added']} atoms; axiom_term={info['axiom_term']}; "
              f"cap_pres={info['cap_pres']}; total_exp={info['total_exp_atoms']}.", flush=True)
        return 0
    finally:
        _release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
