"""Landing notifier — scheduled-task companion to hd_metrics_sync.

USER 2026-06-22: "I don't understand how you find out when things complete. I think you
should have the remote pc ping you or something. you have experiments that ended, and
remote cpu and gpu are idle."

The substrate's compute architecture has a structural visibility gap:
  - hdi_exp_dev / hdi_orchestrator spawns fire task-notifications when MY SPAWN completes,
    NOT when the remote cell that spawn dispatched actually lands
  - hd_metrics_sync (scheduled task) pulls metrics from remote → local but emits no signal
  - Dashboard auto-refreshes but Director doesn't see the dashboard
  - Result: I miss landings for 10-60+ minutes

This tool: scan `data/exp_*/metrics.json` for files modified since last invocation; for each
new arrival emit a JSONL line to `data/recent_landings.jsonl`. Director checks that file at
every turn-start (will be added to standing-discipline; see Fix #25).

Run periodically via scheduled task (cron / Windows Task Scheduler) — every 1-5 min.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANDINGS = REPO / "data" / "recent_landings.jsonl"
STATE_FILE = REPO / "data" / ".landing_notifier_state.json"
# Director-visible surface — small human-readable pane refreshed every cron tick.
# Turn-start ritual: `Read data/latest_landings.md` (cheaper than tailing JSONL).
LATEST_PANE = REPO / "data" / "latest_landings.md"
PANE_N = 12  # tail depth


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"last_check_ts": 0.0, "seen": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _canonical_anchor(dirname: str) -> tuple[str, bool]:
    """Return (canonical_anchor, sh4_double_prefix).

    Landing dirs come in two shapes:
      canonical:   data/exp_<anchor>/          (dirname="exp_<anchor>")
      SH-4 double: data/exp_exp_<anchor>/      (dirname="exp_exp_<anchor>")
    SH-4 fires when a cell was registered with an entry_name that already began
    with 'exp_' — the runner (runner_v2_prod.py::HDLAB_EXP_NAME=name) then
    passes that through to _seed_checkpoint.get_output_dir which does
    f"exp_{name}", producing a double-prefixed landing dir. Cosmetic; the
    metrics.json is still there. Skunkworks caught 2 back-to-back landings
    on 2026-07-03 (M-sweep FULL, Exp 3E FULL). Landing pane must handle both.
    """
    if dirname.startswith("exp_exp_"):
        return dirname[len("exp_exp_"):], True
    if dirname.startswith("exp_"):
        return dirname[len("exp_"):], False
    return dirname, False


def scan() -> list[dict]:
    """Scan all data/exp_*/metrics.json (canonical AND SH-4 double-prefix) for
    arrivals since last check; append to landings file.

    Both `data/exp_<anchor>/metrics.json` and `data/exp_exp_<anchor>/metrics.json`
    are picked up (the startswith("exp_") gate matches both — kept explicit here
    so future refactors don't accidentally drop double-prefix coverage). Each
    arrival records `sh4_double_prefix: True` when the on-disk dir is
    double-prefixed so process-health audits can trend the cosmetic bug's
    recurrence rate without inspecting every dir.
    """
    state = load_state()
    seen = state.get("seen", {})  # path → mtime
    now = time.time()
    arrivals = []
    data_dir = REPO / "data"
    if not data_dir.exists():
        return []
    for d in data_dir.iterdir():
        if not d.is_dir() or not d.name.startswith("exp_"):
            continue
        mp = d / "metrics.json"
        if not mp.exists():
            continue
        mtime = mp.stat().st_mtime
        path_str = str(mp)
        if path_str in seen and seen[path_str] >= mtime:
            continue  # already-seen
        seen[path_str] = mtime
        anchor, sh4 = _canonical_anchor(d.name)
        try:
            m = json.loads(mp.read_text(encoding="utf-8"))
            # `verdict` is a STRING for older cells but a DICT/LIST for newer ones. `dict[:80]` raises
            # `KeyError: slice(...)` -- exactly what silently broke this notifier ~2026-08-14 (state frozen
            # since; task disabled after repeated exit-1). Coerce to a short string, and guard the WHOLE
            # per-file block so ONE malformed metrics.json can never crash the scan (the docstring invariant).
            _v = m.get("verdict")
            if isinstance(_v, (dict, list)):
                _v = json.dumps(_v, sort_keys=True)
            arrivals.append({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime)),
                "cell": d.name,
                "anchor": anchor,
                "sh4_double_prefix": sh4,
                "verdict": (str(_v) if _v not in (None, "") else "?")[:80],
                "run_mode": m.get("run_mode"),
                "n_seeds": m.get("n_seeds"),
                "elapsed_s": m.get("elapsed_s"),
            })
        except Exception:
            continue  # malformed / unexpected-shape metrics.json -> skip this one, never abort the scan
    # Append arrivals to landings file
    if arrivals:
        with open(LANDINGS, "a", encoding="utf-8") as f:
            for a in arrivals:
                f.write(json.dumps(a) + "\n")
    state["last_check_ts"] = now
    state["seen"] = seen
    save_state(state)
    _refresh_pane()
    return arrivals


def _refresh_pane() -> None:
    """Write last PANE_N landings to LATEST_PANE (Director turn-start surface).

    Called every scan tick. Overwrite semantics — no history retained here; full history
    stays in recent_landings.jsonl. Purpose: give Director a one-Read landing digest.
    """
    if not LANDINGS.exists():
        return
    try:
        lines = LANDINGS.read_text(encoding="utf-8").strip().split("\n")
    except OSError:
        return
    parsed = []
    for line in lines[-2000:]:   # bound the parse cost to a recent window
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    # Show the genuinely MOST-RECENT by timestamp -- append order != time order (a one-time backfill,
    # or out-of-order directory iteration, would otherwise surface stale rows). ISO ts sorts chronologically.
    tail = sorted(parsed, key=lambda r: r.get("ts", ""), reverse=True)[:PANE_N]
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sh4_hits = sum(1 for r in tail if r.get("sh4_double_prefix"))
    sh4_note = (f"  |  **SH-4 double-prefix hits in tail:** {sh4_hits}"
                if sh4_hits else "")
    out = [
        "# Latest landings (auto-refreshed by tools/landing_notifier.py)",
        "",
        f"**Pane refreshed:** {now_iso} (UTC)  |  **Tail depth:** {PANE_N}"
        f"  |  **Full log:** `data/recent_landings.jsonl`{sh4_note}",
        "",
        "| ts (UTC) | cell | verdict | run_mode | seeds | elapsed_s |",
        "|---|---|---|---|---|---|",
    ]
    for r in tail:
        cell_raw = (r.get("cell") or "").replace("|", "/")
        # Flag SH-4 double-prefix landings inline so operators see the cosmetic
        # bug rather than silently displaying the double-prefixed dir name.
        cell = f"[SH-4] {cell_raw}" if r.get("sh4_double_prefix") else cell_raw
        verdict = (r.get("verdict") or "").replace("|", "/")
        rm = r.get("run_mode") or ""
        seeds = r.get("n_seeds")
        seeds_s = "" if seeds is None else str(seeds)
        el = r.get("elapsed_s")
        try:
            el_s = "" if el is None else f"{float(el):.1f}"
        except (TypeError, ValueError):
            el_s = str(el)
        out.append(f"| {r.get('ts','')} | {cell} | {verdict} | {rm} | {seeds_s} | {el_s} |")
    try:
        LATEST_PANE.write_text("\n".join(out) + "\n", encoding="utf-8")
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Substrate landing notifier")
    parser.add_argument("--recent", type=int, default=0,
                        help="Print last N landings from recent_landings.jsonl (don't scan)")
    args = parser.parse_args()
    if args.recent > 0:
        if not LANDINGS.exists():
            return
        lines = LANDINGS.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-args.recent:]:
            try:
                r = json.loads(line)
                print(f"  [{r['ts']}] {r['cell']}: {r['verdict']} (run_mode={r['run_mode']}, seeds={r['n_seeds']})")
            except (json.JSONDecodeError, KeyError):
                continue
        return
    arrivals = scan()
    if arrivals:
        print(f"[landing_notifier] {len(arrivals)} new arrivals appended to {LANDINGS.name}")
        for a in arrivals[:5]:
            print(f"  {a['cell']}: {a['verdict']} ({a['run_mode']})")


if __name__ == "__main__":
    main()
