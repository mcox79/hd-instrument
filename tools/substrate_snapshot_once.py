#!/usr/bin/env python3
"""On-demand local substrate snapshot (Research SPEC #2, refined: button-triggered, NOT a 60s poller).

Single source of truth (Skunkworks constraint): this does NOT reimplement the CERT/axiom/invariant/
capint logic. It SHELLS OUT to Skunkworks's authoritative checks with --json and caches a merged VIEW:
  tools/skunkworks_substrate_invariant_check_v1.py --json   -> {atoms_total, atoms_by_kind,
       cert_chain_grade_count, axiom_count, cap_pres_count, graph_hygiene_flags, true_hard_pass_invariant}
  tools/skunkworks_capint_integration_check_v1.py --json    -> {capint_integrated_count,
       capint_cluster_count, I1..I9_pass, track_a_by_domain}
Writes an ATOMIC merged JSON to data/local_substrate_snapshot.json with a ts + a staleness caption.

GRACEFUL: if a check does not yet support --json (Skunkworks adds it on her side), the snapshot records
status="awaiting_json_flag" for that source instead of crashing -- so the dashboard button degrades
cleanly until the --json flags land. Invoked on-demand by the dashboard /refresh-substrate endpoint.

Usage: python tools/substrate_snapshot_once.py [--self-test]
ASCII-only.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "local_substrate_snapshot.json"
PY = sys.executable
CHECKS = {
    "invariant": REPO / "tools" / "skunkworks_substrate_invariant_check_v1.py",
    "capint": REPO / "tools" / "skunkworks_capint_integration_check_v1.py",
}
CAPTION = "POLLED-ON-DEMAND snapshot (button-triggered; NOT live). Authoritative gate = on-demand invariant-check."


def run_check_json(name, path, timeout=120):
    """Shell out to a check with --json; return (status, parsed_dict_or_error)."""
    if not path.exists():
        return "missing_tool", {"error": "tool not found: %s" % path.name}
    try:
        proc = subprocess.run([PY, str(path), "--json"], cwd=str(REPO), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "timeout", {"error": "check timed out after %ds" % timeout}
    out = (proc.stdout or "").strip()
    # find the JSON object in stdout (the check may print other lines)
    parsed = None
    for chunk in (out, _last_json_line(out)):
        if not chunk:
            continue
        try:
            parsed = json.loads(chunk); break
        except (ValueError, json.JSONDecodeError):
            continue
    if parsed is None:
        # --json not supported yet (Skunkworks adds it her side) OR no JSON emitted
        return "awaiting_json_flag", {"rc": proc.returncode, "stdout_tail": out[-200:]}
    return "ok", parsed


def _last_json_line(s):
    for line in reversed(s.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return line
    return None


def build_snapshot(invariant_status, invariant_data, capint_status, capint_data, ts):
    return {
        "ts": ts,
        "caption": CAPTION,
        "source": "single-source: delegates to skunkworks_substrate_invariant_check_v1 + "
                  "skunkworks_capint_integration_check_v1 (--json); no inline reimplementation",
        "invariant": {"status": invariant_status, **(invariant_data or {})},
        "capint": {"status": capint_status, **(capint_data or {})},
        "all_sources_ok": invariant_status == "ok" and capint_status == "ok",
    }


def atomic_write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp.%d" % os.getpid())
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


def take_snapshot():
    ts = datetime.now().isoformat(timespec="seconds")
    inv_status, inv_data = run_check_json("invariant", CHECKS["invariant"])
    cap_status, cap_data = run_check_json("capint", CHECKS["capint"])
    snap = build_snapshot(inv_status, inv_data, cap_status, cap_data, ts)
    atomic_write_json(OUT, snap)
    return snap


def _selftest():
    import tempfile
    # merge logic
    s = build_snapshot("ok", {"cert_chain_grade_count": 587, "true_hard_pass_invariant": True},
                       "ok", {"capint_integrated_count": 457}, "2026-06-19T17:50:00")
    assert s["all_sources_ok"] is True
    assert s["invariant"]["cert_chain_grade_count"] == 587
    assert s["capint"]["capint_integrated_count"] == 457
    assert s["ts"] == "2026-06-19T17:50:00"
    # graceful degradation
    s2 = build_snapshot("awaiting_json_flag", {"rc": 0}, "ok", {"capint_integrated_count": 457}, "t")
    assert s2["all_sources_ok"] is False
    assert s2["invariant"]["status"] == "awaiting_json_flag"
    # _last_json_line picks the JSON among noise
    assert _last_json_line("log line\n{\"a\": 1}\nmore") == '{"a": 1}'
    # atomic write round-trips
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "snap.json"
        atomic_write_json(p, s)
        assert json.loads(p.read_text())["invariant"]["cert_chain_grade_count"] == 587
    print("[selftest] PASS: snapshot merge + graceful-degrade + last-json-line + atomic-write", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _selftest()
        return 0
    snap = take_snapshot()
    print(json.dumps(snap, indent=2))
    if not snap["all_sources_ok"]:
        print("\n[note] one or more checks lack --json yet (Skunkworks adds it her side) -> snapshot is "
              "partial/graceful until then. invariant=%s capint=%s" %
              (snap["invariant"]["status"], snap["capint"]["status"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
