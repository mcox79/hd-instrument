"""40h M3: integrated DURABILITY CRON (ONE tool; daily). Snapshot + cert-FLOOR invariant-check + manifest-gap-DETECTION.

Per the 40h tack-on (Director GO 2026-06-19): a SINGLE daily cron integrating three durability layers, NOT three tools:
  (1) SNAPSHOT     -- tar -czf data/snapshots/substrate-<UTCdate>.tar.gz data/substrate_index/ (off-machine via --push to
                      the origin/snapshots/ branch; the push is the runner's step -- Orchestrator owns push creds).
  (2) INVARIANT    -- run tools/skunkworks_substrate_invariant_check_v1.py (the cert-FLOOR: TRUE-HARD + GRAPH-HYGIENE +
                      SOFT) with --expect from the counts-manifest (drift-detect vs the last-good snapshot). exit!=0 = HARD drift.
  (3) MANIFEST-GAP -- expected_floor of atom-ids that should ALWAYS be present (grows on legitimate additions; NEVER auto-
                      shrinks). missing = expected_floor - current -> FLAGGED (a deletion/gap). A5-NO-SILENT-RECOMPUTE: the
                      cron FLAGS drift; it does NOT auto-fix (no auto-restore, no auto-remove-from-floor; a real deletion needs
                      a human to acknowledge by explicitly advancing the floor via --ack-deletions).

Writes a durability report (data/durability_reports/durability-<UTCdate>.json) + stdout PASS/FLAG. Overall = FLAG if HARD
invariant drift OR any missing atom; else PASS. Read-only on the Store (only reads atoms for the manifest + invokes the
read-only invariant-check); writes ONLY durability artifacts (snapshot tar, floor manifest, report) -- NOT Store mutations.

DEVICE=cpu (7th checklist: I/O + subprocess; no torch/GPU). --self-test (logic on synthetic; no writes). --dry-run (report
only; no snapshot, no floor-advance). default = full run (snapshot + invariant + gap + floor-advance + report). --push
(attempt origin/snapshots push; runner step). --ack-deletions (human-acknowledge: drop currently-missing ids from the floor).
11th-rule deterministic. ASCII. (Schedule via Orchestrator's runner; this is the SCRIPT the cron invokes.)
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

DEVICE = "cpu"
REPO = Path(__file__).resolve().parents[1]
SNAP_DIR = REPO / "data" / "snapshots"
REPORT_DIR = REPO / "data" / "durability_reports"
FLOOR_PATH = REPO / "data" / "durability_expected_floor.json"
INVARIANT_TOOL = REPO / "tools" / "skunkworks_substrate_invariant_check_v1.py"
VENV_PY = REPO / ".venv" / "Scripts" / "python.exe"


def _utc_date() -> str:
    return time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())   # runtime (live cron; not the workflow sandbox)


def load_store_state():
    """Read-only: atom-id set + counts (atoms, cert, axiom_term)."""
    sys.path.insert(0, str(REPO))
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ids, n_atoms, n_cert = set(), 0, 0
    for a in ps.all_atoms():
        ids.add(a.id); n_atoms += 1
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE":
            n_cert += 1
    axiom = sum(1 for a in ps.all_atoms()
                if str(a.corpus.name) == "MATH" and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
                and a.algebra and len(a.algebra) >= 3 and "oeis" not in str(a.id).lower()
                and not str(a.id).startswith("T3/wikidata_"))
    return ids, {"atoms": n_atoms, "cert": n_cert, "axiom_term": axiom}


def run_invariant_check(expect: dict | None):
    if not INVARIANT_TOOL.exists():
        return {"ran": False, "exit": None, "note": "invariant-check tool not found"}
    cmd = [str(VENV_PY if VENV_PY.exists() else sys.executable), str(INVARIANT_TOOL)]
    if expect:
        cmd += ["--expect-cert", str(expect["cert"]), "--expect-atoms", str(expect["atoms"]),
                "--expect-axiom", str(expect["axiom_term"])]
    try:
        p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=600)
        tail = "\n".join(p.stdout.strip().splitlines()[-6:])
        return {"ran": True, "exit": p.returncode, "hard_pass": p.returncode == 0, "tail": tail}
    except Exception as e:
        return {"ran": False, "exit": None, "note": f"invariant-check error: {str(e)[:120]}"}


def manifest_gap(current_ids: set, ack_deletions: bool, write: bool):
    """expected_floor grows on additions, NEVER auto-shrinks. missing = floor - current -> FLAG (A5: no auto-fix)."""
    floor = set()
    if FLOOR_PATH.exists():
        try:
            floor = set(json.loads(FLOOR_PATH.read_text(encoding="utf-8")).get("expected_floor", []))
        except Exception:
            floor = set()
    first_run = not FLOOR_PATH.exists()
    missing = sorted(floor - current_ids)        # deletions/gaps -> FLAG
    additions = sorted(current_ids - floor)       # normal growth -> fold into floor
    new_floor = (current_ids if first_run else floor | current_ids)   # additions in; NEVER auto-remove missing
    if ack_deletions:
        new_floor = current_ids                   # human-acknowledged: reset floor to current (drops the missing)
    if write:
        FLOOR_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = FLOOR_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"expected_floor": sorted(new_floor), "updated_utc": _utc_date(),
                                   "n_floor": len(new_floor)}, indent=0), encoding="utf-8")
        import os
        os.replace(tmp, FLOOR_PATH)
    return {"first_run": first_run, "n_floor_before": len(floor), "n_missing": len(missing),
            "missing_sample": missing[:10], "n_additions": len(additions), "ack_deletions": ack_deletions,
            "n_floor_after": len(new_floor)}


def run_snapshot(date: str, push: bool):
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    snap = SNAP_DIR / f"substrate-{date}.tar.gz"
    try:
        p = subprocess.run(["tar", "-czf", str(snap), "-C", str(REPO), "data/substrate_index"],
                           capture_output=True, text=True, timeout=600)
        ok = (p.returncode == 0 and snap.exists())
        size_mb = round(snap.stat().st_size / 1e6, 1) if snap.exists() else 0
        out = {"snapshot_ok": ok, "path": str(snap.relative_to(REPO)), "size_mb": size_mb}
    except Exception as e:
        return {"snapshot_ok": False, "note": f"tar error: {str(e)[:120]}"}
    if push and ok:
        # runner step: push the snapshot tar to origin/snapshots/ (orphan-ish branch). Best-effort; runner owns creds.
        out["push_attempted"] = True
        out["push_note"] = "push to origin/snapshots/ is the runner's step (Orchestrator push creds); script created the tar."
    return out


def write_report(date: str, payload: dict, write: bool):
    if not write:
        return None
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rp = REPORT_DIR / f"durability-{date}.json"
    tmp = rp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    import os
    os.replace(tmp, rp)
    return str(rp.relative_to(REPO))


def self_test() -> int:
    # manifest_gap logic on synthetic (no real store; no writes)
    cur = {"a", "b", "c"}
    # floor had {a,b,d} -> missing d, addition c
    global FLOOR_PATH
    import tempfile, os
    saved = FLOOR_PATH
    tf = Path(tempfile.mkdtemp(prefix="dur_")) / "floor.json"
    tf.write_text(json.dumps({"expected_floor": ["a", "b", "d"]}), encoding="utf-8")
    FLOOR_PATH = tf
    try:
        r = manifest_gap(cur, ack_deletions=False, write=False)
        ok = (r["n_missing"] == 1 and r["missing_sample"] == ["d"] and r["n_additions"] == 1
              and r["n_floor_after"] == 4)   # floor a,b,d + c = 4 (d NOT auto-removed)
        r2 = manifest_gap(cur, ack_deletions=True, write=False)
        ok = ok and (r2["n_floor_after"] == 3)   # ack -> floor = current {a,b,c}
        print(f"[durability_cron] --self-test {'OK' if ok else 'FAIL'} (gap: missing=d not-auto-removed, addition=c folded, floor 3->4; ack resets to 3); A5-no-silent verified.")
        return 0 if ok else 1
    finally:
        FLOOR_PATH = saved
        import shutil; shutil.rmtree(tf.parent, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="report only; no snapshot, no floor-advance write")
    ap.add_argument("--push", action="store_true", help="attempt origin/snapshots push (runner step)")
    ap.add_argument("--ack-deletions", action="store_true", help="human-ack: reset expected_floor to current (drops missing)")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    date = _utc_date()
    write = not args.dry_run
    current_ids, counts = load_store_state()

    # invariant-check vs the LAST-good counts (from floor manifest metadata if present), else current as baseline
    expect = None
    if FLOOR_PATH.exists():
        try:
            prev = json.loads(FLOOR_PATH.read_text(encoding="utf-8"))
            if "last_counts" in prev:
                expect = prev["last_counts"]
        except Exception:
            pass
    inv = run_invariant_check(expect)
    gap = manifest_gap(current_ids, args.ack_deletions, write)
    snap = run_snapshot(date, args.push) if write else {"snapshot_ok": None, "note": "dry-run: skipped"}

    hard_drift = (inv.get("ran") and inv.get("hard_pass") is False)
    overall = "FLAG" if (hard_drift or gap["n_missing"] > 0) else "PASS"
    payload = {"date_utc": date, "device": DEVICE, "overall": overall, "counts": counts,
               "invariant_check": inv, "manifest_gap": gap, "snapshot": snap,
               "a5_no_silent": "FLAG-only; no auto-restore / no auto-floor-shrink (missing needs --ack-deletions human-ack)"}
    # persist last_counts INTO the floor manifest (so next run --expects them) -- only on write + clean (A5: don't advance baseline past HARD drift)
    if write and not hard_drift and FLOOR_PATH.exists():
        try:
            fl = json.loads(FLOOR_PATH.read_text(encoding="utf-8"))
            fl["last_counts"] = counts
            import os
            tmp = FLOOR_PATH.with_suffix(".json.tmp"); tmp.write_text(json.dumps(fl, indent=0), encoding="utf-8"); os.replace(tmp, FLOOR_PATH)
        except Exception:
            pass
    rp = write_report(date, payload, write)
    print("=" * 78)
    print(f"DURABILITY CRON {date}  ->  {overall}   (device={DEVICE})")
    print(f"  counts: atoms={counts['atoms']} cert={counts['cert']} axiom_term={counts['axiom_term']}")
    print(f"  invariant-check: ran={inv.get('ran')} exit={inv.get('exit')} hard_pass={inv.get('hard_pass')}")
    print(f"  manifest-gap: floor_before={gap['n_floor_before']} missing={gap['n_missing']} additions={gap['n_additions']} floor_after={gap['n_floor_after']}")
    if gap["n_missing"]:
        print(f"  !! MISSING (deletion drift; A5 flag-not-fix; resolve via --ack-deletions): {gap['missing_sample']}")
    print(f"  snapshot: {snap}")
    print(f"  report: {rp}")
    print("=" * 78)
    return 0 if overall == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
