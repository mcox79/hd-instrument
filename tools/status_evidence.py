#!/usr/bin/env python
"""WHEN WAS THIS ROW'S EVIDENCE LAST UPDATED -- provenance stamps for the status window.

WHY THIS EXISTS (owner, 2026-08-16): *"I'd also like timestamps for each entry on the dash - when it
was last updated so I know what's new and what is old."*

THE ONE THING THIS MODULE MUST NOT DO, and the reason it is a module rather than three lines in the
renderer: **it must never show the refresh time.** The window refreshes every 20 seconds. Stamping
every row with the refresh clock would put a fresh timestamp under a number measured six days ago,
and a stale number under a fresh clock reads as current -- which is strictly worse than no timestamp
at all. So every stamp here is resolved from THE ARTIFACT THE ROW IS DERIVED FROM, and a row whose
artifact cannot be found is stamped UNKNOWN. There is no third option and no fallback to `now()`.

HOW A ROW'S ARTIFACT IS FOUND. The rows already say where they came from, in prose: the ledger rows
carry `evidence` strings like `exp_orthographic_floor_vet_v1 (58a125c88)`, the fidelity rows carry
`outcome_source` strings like `data/exp_ca3_completion_partial_cue_v1/metrics.json`, the organ rows
name `hdlab/*.py` modules, and several rows name a scan fragment under `.claude/scan-out/`. This
module reads those strings, pulls out every artifact reference, and stats it.

THE KIND RANKING IS THE WHOLE DESIGN, AND IT IS NOT COSMETIC.

A row typically cites SEVERAL things -- a measurement AND the note that discusses it. Taking the
newest of them would be wrong in a specific and damaging way: `notes/STATUS.md` is rewritten in full
every session, so every row that mentions it would show as minutes old regardless of when its
measurement was actually taken. That is the exact "fresh clock over a stale number" failure this
module exists to prevent, arriving through the back door.

So references are ranked by HOW DIRECTLY THEY EVIDENCE THE ROW, the strongest kind present wins, and
the timestamp is the newest artifact OF THAT KIND:

    MEASUREMENT  data/<experiment>/metrics.json (or units.jsonl / _heartbeat.jsonl while live)
                 -- the run's own output. This is evidence.
    FRAGMENT     .claude/scan-out/*.json -- an agent's recorded measurement.
    REGISTRY     data/capability_registry.jsonl -- the wire-or-shelve record.
    CODE         hdlab/ tools/ experiments/ verification/ -- when the thing itself last changed.
    NOTE         notes/*.md -- WEAKEST, and labelled as such on screen, because these documents are
                 rewritten wholesale; the mtime says when the DOCUMENT changed, which is not the
                 same as when the MEASUREMENT changed.
    CARRIER      the spec file that physically holds the transcribed row. Labelled distinctly: this
                 is when somebody last WROTE THE ROW, not when the evidence was produced.
    UNKNOWN      nothing resolved. Shown as UNKNOWN. Never as the refresh time.

COMMIT HASHES ARE DETECTED AND DELIBERATELY NOT DATED, and the omission is disclosed on screen
rather than hidden. Dating a commit needs a `git` subprocess; this window makes no subprocess and no
network call anywhere on its collection path, which is the property that keeps it from hanging at
3am. Every row in this repo that cites a commit also cites the experiment directory that commit
produced, so nothing is actually lost -- but a reference this module cannot date is REPORTED as
undated rather than silently dropped, because a silent drop is how "we looked and did not find it"
turns into a false absence claim.

WHAT "OLDER" MEANS ON SCREEN. Per panel, the newest resolved stamp is the reference point and every
row is measured against it, so "what is new and what is old" is answerable without arithmetic. A row
is flagged OLDER only when it is more than `STALE_TOL_S` behind that reference, because evidence
written in one working session lands within seconds of itself and flagging that spread would make
the marker meaningless. The tolerance is one hour and it is stated, not hidden in a branch.

COST. One `os.stat` per DISTINCT path per refresh, cached for the refresh. Measured on the live
repo: ~90 distinct paths, well under 10 ms. No subprocess, no network, no directory walk.

  python tools/status_evidence.py                # resolve the live window's rows and print them
  python tools/status_evidence.py --self-test    # runs with every artifact ABSENT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("HD_DATA_DIR") or (REPO / "data"))

# A row more than this far behind the newest evidence on its own panel is flagged OLDER. One hour:
# the artifacts behind one panel are typically written inside a single working session and land
# within seconds of each other, so a tighter tolerance would flag every row and mean nothing.
STALE_TOL_S = 3600.0

# Strongest evidence first. The rank IS the policy -- see the module docstring.
KIND_ORDER = ("ACTIVITY", "MEASUREMENT", "FRAGMENT", "REGISTRY", "CODE", "NOTE", "CARRIER")
KIND_RANK = {k: i for i, k in enumerate(KIND_ORDER)}
KIND_PLAIN = {
    "ACTIVITY": "the process's own live output -- observed directly, not self-reported",
    "MEASUREMENT": "the experiment's own output file",
    "FRAGMENT": "a recorded measurement fragment",
    "REGISTRY": "the capability record",
    "CODE": "the code itself",
    "NOTE": "a written document (rewritten wholesale, so this is when the DOCUMENT changed, "
            "not necessarily when the measurement did)",
    "CARRIER": "the file that holds this row -- when somebody last WROTE the row, NOT when the "
               "evidence behind it was produced",
}

# Top-level directories whose paths we recognise inside a prose evidence string.
_PATH_RE = re.compile(
    r"(?:\.claude/scan-out|notes|data|hdlab|tools|experiments|verification|preregs|reference|"
    r"scratch)/[A-Za-z0-9_.\-/]+")
# An experiment slug named on its own, e.g. `exp_orthographic_floor_vet_v1 (58a125c88)`.
_EXP_RE = re.compile(r"\bexp_[A-Za-z0-9_]{3,}\b")
# A git hash. Requires BOTH a digit and an a-f letter so that a bare number (0.0480, 259.5, 7769)
# and an ordinary lowercase word (deadbeef has no digit; "coffee" no digit) cannot be mistaken for
# one. Length 7-40, not glued to another word character.
_COMMIT_RE = re.compile(r"(?<![0-9A-Za-z])(?=[0-9a-f]{7,40}(?![0-9A-Za-z]))"
                        r"(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])([0-9a-f]{7,40})")

_TRIM = " \t\r\n.,;:!?)]}'\"`"


# ---------------------------------------------------------------------------
# the stat cache -- one syscall per distinct path per refresh
# ---------------------------------------------------------------------------

_stat_cache: dict[str, float | None] = {}
_stat_calls = {"n": 0, "hits": 0}


def begin_refresh() -> None:
    """Drop the per-refresh stat cache. Called once at the top of a collection.

    The cache is per-refresh and NOT longer-lived on purpose: an experiment that finishes between
    two refreshes must show its new time on the next one. A cache that outlived the refresh would
    reintroduce exactly the staleness this module exists to expose."""
    _stat_cache.clear()
    _stat_calls["n"] = 0
    _stat_calls["hits"] = 0


def cache_stats() -> dict:
    return {"distinct_paths": len(_stat_cache), "stat_calls": _stat_calls["n"],
            "cache_hits": _stat_calls["hits"]}


def mtime(path) -> float | None:
    """Modification time of `path`, or None. Never raises. Cached for this refresh."""
    key = str(path)
    if key in _stat_cache:
        _stat_calls["hits"] += 1
        return _stat_cache[key]
    _stat_calls["n"] += 1
    try:
        ts = os.stat(key).st_mtime
    except OSError:
        ts = None
    _stat_cache[key] = ts
    return ts


# ---------------------------------------------------------------------------
# formatting -- relative for the owner, absolute kept available
# ---------------------------------------------------------------------------

def iso(ts) -> str | None:
    """Absolute local time, kept available beside every relative one (owner asked for both)."""
    if not isinstance(ts, (int, float)) or ts <= 0:
        return None
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (OSError, OverflowError, ValueError):
        return None


def iso_utc(ts) -> str | None:
    if not isinstance(ts, (int, float)) or ts <= 0:
        return None
    try:
        return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")
    except (OSError, OverflowError, ValueError):
        return None


def relative(age_s) -> str:
    """'3h ago' / '2d ago'. UNKNOWN when there is no age -- never a guess and never the clock.

    A NEGATIVE age is reported as such rather than clamped to 'just now'. It means the artifact's
    timestamp is in the future, which happens with a clock skew or a copied file, and silently
    rounding it away would hide a real reason to distrust the stamp."""
    if not isinstance(age_s, (int, float)):
        return "UNKNOWN"
    if age_s < -60:
        return f"dated {relative(-age_s).replace(' ago', '')} IN THE FUTURE"
    a = max(age_s, 0)
    if a < 90:
        return "just now"
    if a < 3600:
        return f"{int(a // 60)}m ago"
    if a < 86400:
        return f"{int(a // 3600)}h ago"
    if a < 86400 * 14:
        d = a / 86400.0
        return f"{d:.1f}d ago" if d < 10 else f"{int(d)}d ago"
    if a < 86400 * 70:
        return f"{int(a // (86400 * 7))}w ago"
    return f"{int(a // 86400)}d ago"


def lag(seconds) -> str:
    """How far behind the panel's newest evidence -- a DURATION, never a point in time."""
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        return ""
    if seconds < 3600:
        return f"{int(seconds // 60)}m behind"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h behind"
    return f"{int(seconds // 86400)}d behind"


# ---------------------------------------------------------------------------
# reference extraction and resolution
# ---------------------------------------------------------------------------

def _clean(tok: str) -> str:
    return tok.strip(_TRIM)


def refs_in(text) -> list[dict]:
    """Every artifact reference in one prose string, deduplicated, order preserved.

    Returns dicts of {kind_hint, raw}. `kind_hint` is provisional -- the true kind is decided in
    `resolve()`, because whether `data/foo/metrics.json` is a MEASUREMENT depends on it existing."""
    if not isinstance(text, str) or not text:
        return []
    out: list[dict] = []
    seen: set[str] = set()

    def add(kind_hint: str, raw: str) -> None:
        raw = _clean(raw)
        if not raw or raw in seen:
            return
        seen.add(raw)
        out.append({"kind_hint": kind_hint, "raw": raw})

    for m in _PATH_RE.finditer(text):
        add("path", m.group(0))
    for m in _EXP_RE.finditer(text):
        # Skip a slug already covered by an explicit path reference -- it would resolve to the
        # same file and double-count in the reference list the reader sees.
        if any(m.group(0) in r["raw"] for r in out if r["kind_hint"] == "path"):
            continue
        add("experiment", m.group(0))
    for m in _COMMIT_RE.finditer(text):
        tok = m.group(1)
        if any(tok in r["raw"] for r in out):
            continue
        add("commit", tok)
    return out


# The files an experiment directory can carry, strongest first. `metrics.json` is the run's verdict;
# the other two exist only while it is still running, and a live run's freshness is genuine news.
_EXP_FILES = ("metrics.json", "units.jsonl", "_heartbeat.jsonl")


def _kind_for_path(rel: str) -> str:
    r = rel.replace("\\", "/")
    if r.startswith(".claude/scan-out/"):
        return "FRAGMENT"
    if r == "data/capability_registry.jsonl":
        return "REGISTRY"
    if r.startswith("data/"):
        return "MEASUREMENT"
    if r.startswith(("hdlab/", "tools/", "experiments/", "verification/")):
        return "CODE"
    if r.startswith(("notes/", "preregs/", "reference/")):
        return "NOTE"
    return "CODE"


def resolve(ref: dict) -> dict:
    """Resolve one reference to (kind, path, ts). Never raises; never invents a time.

    An unresolvable reference comes back with `ts=None` AND a stated reason, so the caller can show
    that the row named something it could not date rather than pretending the reference was never
    there."""
    hint = ref.get("kind_hint")
    raw = str(ref.get("raw") or "")
    out = dict(ref, ts=None, path=None, kind=None, why="")

    if hint == "commit":
        out["kind"] = "COMMIT"
        out["why"] = ("a commit date needs a git subprocess; this window makes no subprocess call "
                      "anywhere on its collection path, so the commit is named but not dated")
        return out

    if hint == "experiment":
        base = DATA_DIR / raw
        best_ts, best_path = None, None
        for fn in _EXP_FILES:
            ts = mtime(base / fn)
            if ts is not None and (best_ts is None or ts > best_ts):
                best_ts, best_path = ts, base / fn
        if best_ts is None:
            ts = mtime(base)
            if ts is not None:
                best_ts, best_path = ts, base
        if best_ts is None:
            out["why"] = f"no directory {base} on this machine"
            return out
        out.update(ts=best_ts, path=str(best_path), kind="MEASUREMENT")
        return out

    # an explicit repo-relative path
    p = REPO / raw
    ts = mtime(p)
    if ts is None:
        # A path with a trailing fragment ("notes/PLAN.md section 3" is already trimmed by the
        # regex, but "data/x/" or a doubled slash can still miss). Try the parent once.
        parent = p.parent
        ts = mtime(parent) if str(parent) != str(REPO) else None
        if ts is None:
            out["why"] = f"not found on disk: {raw}"
            return out
        out.update(ts=ts, path=str(parent), kind=_kind_for_path(raw.rsplit("/", 1)[0]))
        return out
    out.update(ts=ts, path=str(p), kind=_kind_for_path(raw))
    return out


def stamp(texts, carrier=None, carrier_label: str | None = None) -> dict:
    """THE STAMP FOR ONE ROW. Resolved from the row's own artifacts; UNKNOWN if there are none.

    `texts`    -- the prose fields that name where the row came from (evidence, source, module...).
    `carrier`  -- the file that physically holds the row, used ONLY when nothing else resolves and
                  labelled distinctly on screen so it can never be read as a measurement date.
    """
    if isinstance(texts, str):
        texts = [texts]
    refs: list[dict] = []
    seen: set[str] = set()
    for t in texts or []:
        for r in refs_in(t):
            if r["raw"] in seen:
                continue
            seen.add(r["raw"])
            refs.append(r)

    resolved = [resolve(r) for r in refs]
    dated = [r for r in resolved if r.get("ts") is not None]
    undated = [r for r in resolved if r.get("ts") is None]

    if dated:
        # The STRONGEST kind present wins; within it, the newest artifact.
        best_kind = min((r["kind"] for r in dated), key=lambda k: KIND_RANK.get(k, 99))
        pool = [r for r in dated if r["kind"] == best_kind]
        win = max(pool, key=lambda r: r["ts"])
        return _finish(win["ts"], best_kind, win["path"], dated, undated,
                       weaker=[r for r in dated if r["kind"] != best_kind])

    if carrier is not None:
        ts = mtime(carrier)
        if ts is not None:
            return _finish(ts, "CARRIER", str(carrier), [], undated, weaker=[],
                           carrier_label=carrier_label)

    return {
        "ts": None, "age_s": None, "rel": "UNKNOWN", "when": None, "when_utc": None,
        "kind": "UNKNOWN", "kind_plain": "no artifact could be found for this row",
        "source": None, "n_refs": len(refs), "refs": resolved, "undated": undated,
        "detail": ("This row names no artifact this window can date, so its age is UNKNOWN. "
                   "UNKNOWN is shown rather than the refresh time -- a fresh clock over an "
                   "undated number is worse than no clock at all."),
    }


def stamp_known(ts, kind: str, source: str, detail: str = "") -> dict:
    """A stamp for a row whose artifact time is ALREADY known, so it is not stat'd twice.

    Used by the two panels that already hold the artifact's mtime: the results panel stats each
    `metrics.json` while ranking them, and the running panel derives an agent's idle time from its
    transcript mtime. Re-resolving those would be a second syscall for a number already in hand --
    and, worse, a second code path that could disagree with the first."""
    if not isinstance(ts, (int, float)) or ts <= 0:
        return {"ts": None, "age_s": None, "rel": "UNKNOWN", "when": None, "when_utc": None,
                "kind": "UNKNOWN", "kind_plain": "no artifact time was supplied for this row",
                "source": source, "n_refs": 0, "refs": [], "undated": [],
                "detail": "UNKNOWN rather than the refresh time."}
    age = time.time() - ts
    return {"ts": ts, "age_s": round(age, 1), "rel": relative(age), "when": iso(ts),
            "when_utc": iso_utc(ts), "kind": kind,
            "kind_plain": detail or KIND_PLAIN.get(kind, ""), "source": source,
            "n_refs": 1, "refs": [], "weaker": [], "undated": [],
            "oldest_ref_ts": ts, "oldest_ref_rel": relative(age),
            "detail": detail or KIND_PLAIN.get(kind, "")}


def _finish(ts, kind, path, dated, undated, weaker, carrier_label=None) -> dict:
    age = time.time() - ts
    rel_path = path
    try:
        rel_path = str(Path(path).relative_to(REPO)).replace("\\", "/")
    except (ValueError, TypeError):
        pass
    detail = KIND_PLAIN.get(kind, "")
    if kind == "CARRIER" and carrier_label:
        detail = f"{carrier_label}: {detail}"
    oldest = min((r["ts"] for r in dated), default=ts)
    return {
        "ts": ts,
        "age_s": round(age, 1),
        "rel": relative(age),
        "when": iso(ts),
        "when_utc": iso_utc(ts),
        "kind": kind,
        "kind_plain": detail,
        "source": rel_path,
        "n_refs": len(dated) + len(undated),
        "refs": dated,
        "weaker": weaker,
        "undated": undated,
        "oldest_ref_ts": oldest,
        "oldest_ref_rel": relative(time.time() - oldest) if oldest else None,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# per-panel roll-up -- "what is new and what is old" without arithmetic
# ---------------------------------------------------------------------------

def mark_panel(rows, key: str = "evidence", tol_s: float = STALE_TOL_S) -> dict:
    """Compare every row on ONE panel against the newest evidence on that panel, in place.

    Sets on each row's stamp: `behind_s`, `behind` (bool), `behind_text`. Returns the summary the
    panel header renders. Rows with no stamp are counted as `n_unknown` and are NEVER counted as
    up to date -- an unknown age is not a fresh one.

    A CARRIER STAMP DOES NOT SET THE REFERENCE POINT, and that is a correction made after seeing the
    first live output rather than a precaution. A carrier stamp is the mtime of the spec file that
    holds a row, which is touched whenever ANY row in that file is edited -- so one carrier row was
    making six genuinely-recent measurements read as OLDER than a row that cites no evidence at all.
    The reference is therefore the newest REAL evidence on the panel; carriers are still compared
    against it, they just cannot define it."""
    rows = [r for r in (rows or []) if isinstance(r, dict)]
    stamps = [r.get(key) for r in rows]
    stamps = [s for s in stamps if isinstance(s, dict)]
    dated = [s for s in stamps if isinstance(s.get("ts"), (int, float))]
    n_unknown = len(rows) - len(dated)
    if not dated:
        return {"n_rows": len(rows), "n_dated": 0, "n_unknown": n_unknown, "n_behind": 0,
                "newest_rel": "UNKNOWN", "oldest_rel": "UNKNOWN", "newest_ts": None,
                "oldest_ts": None, "span_s": None, "tol_s": tol_s,
                "plain": ("No row on this panel could be dated from an artifact, so nothing here "
                          "can be called new or old.")}
    real = [s for s in dated if s.get("kind") != "CARRIER"] or dated
    newest = max(s["ts"] for s in real)
    oldest = min(s["ts"] for s in dated)
    n_behind = 0
    for s in dated:
        behind_s = newest - s["ts"]
        s["behind_s"] = round(behind_s, 1)
        s["behind"] = behind_s > tol_s
        s["behind_text"] = lag(behind_s) if behind_s > tol_s else ""
        if s["behind"]:
            n_behind += 1
    for s in stamps:
        s.setdefault("behind", False)
        s.setdefault("behind_s", None)
        s.setdefault("behind_text", "")
    now = time.time()
    return {
        "n_rows": len(rows), "n_dated": len(dated), "n_unknown": n_unknown,
        "n_behind": n_behind,
        "newest_ts": newest, "oldest_ts": oldest,
        "newest_rel": relative(now - newest), "oldest_rel": relative(now - oldest),
        "newest_when": iso(newest), "oldest_when": iso(oldest),
        "span_s": round(newest - oldest, 1), "span_text": lag(newest - oldest),
        "tol_s": tol_s,
        "plain": (f"Newest evidence on this panel: {relative(now - newest)}. "
                  f"Oldest: {relative(now - oldest)}. "
                  f"{n_behind} row(s) rest on evidence more than "
                  f"{int(tol_s // 60)} minutes behind the newest"
                  + (f"; {n_unknown} row(s) could not be dated at all." if n_unknown
                     else ".")),
    }


def line(st) -> str:
    """The one cell the owner reads: '3h ago' plus the OLDER marker when it applies."""
    if not isinstance(st, dict):
        return "UNKNOWN"
    txt = st.get("rel") or "UNKNOWN"
    if st.get("behind") and st.get("behind_text"):
        txt += f"   OLDER ({st['behind_text']})"
    if st.get("kind") == "CARRIER":
        txt += "   (row written)"
    return txt


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    """Four properties, each with a NEGATIVE CONTROL proving the rule can actually fail.

      1. a real artifact resolves, and the strongest kind wins over a fresher weak one
      2. an absent artifact resolves to UNKNOWN -- never to the clock
      3. the OLDER flag fires on a genuinely older row and does NOT fire on a same-batch one
      4. every required file absent: nothing raises, nothing is dated, nothing hangs
    """
    import tempfile
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="status_evidence_selftest_"))
    g = globals()
    keep_repo, keep_data = g["REPO"], g["DATA_DIR"]

    # ---- reference extraction, on REAL strings from this repo --------------
    r = refs_in("exp_orthographic_floor_vet_v1 (58a125c88), reproduced off disk 2026-08-16")
    kinds = [x["kind_hint"] for x in r]
    check("experiment" in kinds and "commit" in kinds,
          f"extract: an evidence line yields both the experiment and the commit (got {r})")
    check([x["raw"] for x in r if x["kind_hint"] == "experiment"]
          == ["exp_orthographic_floor_vet_v1"],
          f"extract: the experiment slug is taken whole, without the trailing text (got {r})")
    r2 = refs_in("data/exp_ca3_completion_partial_cue_v1/metrics.json (PAIRING_HYPOTHESIS_REFUTED, "
                 "run_mode=full); notes/LONG_TERM_PLAN.md PHASE 4")
    raws = [x["raw"] for x in r2]
    check("data/exp_ca3_completion_partial_cue_v1/metrics.json" in raws
          and "notes/LONG_TERM_PLAN.md" in raws,
          f"extract: explicit paths are read out of prose and trailing words dropped ({raws})")
    check("exp_ca3_completion_partial_cue_v1" not in raws,
          f"extract: a slug already inside an explicit path is NOT counted twice ({raws})")
    check(refs_in("hit@1 4.80% vs 8.70%, 0 of 7,769 cells, ratio 259.5") == [],
          f"extract NEGATIVE CONTROL: bare numbers are NOT mistaken for commit hashes "
          f"(got {refs_in('hit@1 4.80% vs 8.70%, 0 of 7,769 cells, ratio 259.5')})")
    check(refs_in("the deadbeef arm and the coffee baseline") == [],
          "extract NEGATIVE CONTROL: an all-letter hex-looking word is not a commit")
    check([x["raw"] for x in refs_in("see d62acfe58 for the foundation number")]
          == ["d62acfe58"],
          "extract: a real commit hash IS found (the control above can fail)")

    # ---- resolution + the KIND RANKING, which is the load-bearing rule -----
    (td / "data" / "exp_fake_measurement_v1").mkdir(parents=True, exist_ok=True)
    (td / "notes").mkdir(parents=True, exist_ok=True)
    (td / ".claude" / "scan-out").mkdir(parents=True, exist_ok=True)
    mpath = td / "data" / "exp_fake_measurement_v1" / "metrics.json"
    npath = td / "notes" / "FAKE_STATUS.md"
    cpath = td / "notes" / "fake_carrier.json"
    mpath.write_text("{}", encoding="utf-8")
    npath.write_text("x", encoding="utf-8")
    cpath.write_text("{}", encoding="utf-8")
    old = time.time() - 6 * 86400
    os.utime(mpath, (old, old))                       # the MEASUREMENT is six days old
    os.utime(npath, (time.time(), time.time()))       # the NOTE was rewritten seconds ago
    try:
        g["REPO"] = td
        g["DATA_DIR"] = td / "data"
        begin_refresh()
        s = stamp(["exp_fake_measurement_v1; notes/FAKE_STATUS.md discusses it"], carrier=cpath)
        check(s["kind"] == "MEASUREMENT",
              f"RANKING: a six-day-old measurement BEATS a note rewritten seconds ago "
              f"(got kind={s['kind']!r}, {s['rel']})")
        check(s["age_s"] > 5 * 86400,
              f"RANKING: the stamp is the MEASUREMENT's age, not the note's "
              f"(got {s['age_s']}s = {s['rel']})")
        check("d ago" in s["rel"], f"RANKING: rendered as days, not 'just now' (got {s['rel']!r})")
        check(any(x["kind"] == "NOTE" for x in s.get("weaker") or []),
              "RANKING: the weaker note reference is still CARRIED, not discarded")

        # NEGATIVE CONTROL for the ranking: with no measurement present, the note DOES win.
        begin_refresh()
        s_note = stamp(["notes/FAKE_STATUS.md and nothing else"], carrier=cpath)
        check(s_note["kind"] == "NOTE" and s_note["age_s"] < 3600,
              f"RANKING NEGATIVE CONTROL: with no measurement, the note is used and is fresh "
              f"(got {s_note['kind']!r}, {s_note['rel']})")
        check("rewritten wholesale" in (s_note.get("kind_plain") or ""),
              "RANKING: a note-based stamp SAYS the document is rewritten wholesale")

        # CARRIER fallback, labelled so it cannot read as a measurement date.
        begin_refresh()
        s_car = stamp(["this row cites nothing at all"], carrier=cpath,
                      carrier_label="notes/fake_carrier.json")
        check(s_car["kind"] == "CARRIER",
              f"a row citing nothing falls back to its carrier file (got {s_car['kind']!r})")
        check("NOT when the evidence" in (s_car.get("kind_plain") or ""),
              "the carrier stamp SAYS it is not the evidence date")
        check("(row written)" in line(s_car),
              f"and the RENDERED CELL says so too (got {line(s_car)!r})")

        # THE RULE THAT MATTERS MOST: no artifact, no carrier -> UNKNOWN, never the clock.
        begin_refresh()
        t_before = time.time()
        s_none = stamp(["nothing here"], carrier=td / "does_not_exist.json")
        check(s_none["ts"] is None and s_none["rel"] == "UNKNOWN",
              f"UNKNOWN: an undatable row is UNKNOWN (got {s_none['rel']!r})")
        check(s_none.get("when") is None,
              "UNKNOWN: no absolute time is emitted either")
        check(abs((s_none.get("ts") or 0) - t_before) > 1e6 or s_none.get("ts") is None,
              "UNKNOWN NEGATIVE CONTROL: the refresh clock was NOT substituted for the stamp")

        # An undatable COMMIT is reported, not silently dropped.
        begin_refresh()
        s_c = stamp(["58a125c88 only"], carrier=None)
        check(s_c["ts"] is None and any(u.get("kind") == "COMMIT" for u in s_c.get("undated") or []),
              f"a commit-only row is UNKNOWN but the commit is REPORTED as undated "
              f"(got {s_c.get('undated')})")

        # ---- the OLDER flag, with its negative control ---------------------
        now = time.time()
        rows = [
            {"evidence": {"ts": now, "rel": "just now"}},
            {"evidence": {"ts": now - 600, "rel": "10m ago"}},      # same batch -> NOT older
            {"evidence": {"ts": now - 5 * 86400, "rel": "5d ago"}},  # genuinely older
            {"evidence": {"ts": None, "rel": "UNKNOWN"}},
        ]
        summ = mark_panel(rows)
        check(summ["n_behind"] == 1,
              f"OLDER: exactly the one genuinely-older row is flagged (got {summ['n_behind']})")
        check(rows[2]["evidence"]["behind"] is True,
              "OLDER: the five-day-old row IS flagged")
        check(rows[1]["evidence"]["behind"] is False,
              "OLDER NEGATIVE CONTROL: a row 10 minutes behind is NOT flagged -- the tolerance "
              "actually holds and the marker is not fired on everything")
        check(summ["n_unknown"] == 1,
              f"OLDER: an undated row counts as UNKNOWN, never as up to date "
              f"(got {summ['n_unknown']})")
        check("OLDER" in line(rows[2]["evidence"]) and "OLDER" not in line(rows[1]["evidence"]),
              "OLDER: the marker reaches the RENDERED CELL, and only for the older row")
        check(summ["newest_rel"] == "just now" and "d ago" in summ["oldest_rel"],
              f"OLDER: the panel summary states newest AND oldest "
              f"(got {summ['newest_rel']!r} / {summ['oldest_rel']!r})")

        # A CARRIER stamp must not become the reference point. Live output caught this: one
        # row citing nothing at all was the newest thing on the panel, which made six real
        # measurements read as OLDER than a row with no evidence behind it.
        carrier_rows = [
            {"evidence": {"ts": now, "rel": "just now", "kind": "CARRIER"}},
            {"evidence": {"ts": now - 2 * 3600, "rel": "2h ago", "kind": "MEASUREMENT"}},
        ]
        cs = mark_panel(carrier_rows)
        check(cs["n_behind"] == 0,
              f"CARRIER: a freshly-written spec file does NOT make a real measurement read as "
              f"OLDER (got n_behind={cs['n_behind']})")
        check(carrier_rows[0]["evidence"]["behind_s"] < 0,
              "CARRIER: the carrier row is still compared against the real reference")
        mixed = [{"evidence": {"ts": now, "rel": "just now", "kind": "MEASUREMENT"}},
                 {"evidence": {"ts": now - 5 * 86400, "rel": "5d ago", "kind": "MEASUREMENT"}}]
        check(mark_panel(mixed)["n_behind"] == 1,
              "CARRIER NEGATIVE CONTROL: with two real measurements the older one IS still "
              "flagged, so the carrier rule did not disable the flag")

        # ---- every artifact absent ----------------------------------------
        g["REPO"] = td / "gone"
        g["DATA_DIR"] = td / "gone" / "data"
        begin_refresh()
        t0 = time.time()
        s_abs = stamp(["exp_anything_v1; notes/STATUS.md; data/x/metrics.json; 58a125c88"],
                      carrier=td / "gone" / "carrier.json")
        took = time.time() - t0
        check(took < 2.0, f"files-absent: returned in {took:.3f}s, did not hang")
        check(s_abs["ts"] is None and s_abs["rel"] == "UNKNOWN",
              f"files-absent: UNKNOWN, not a fabricated time (got {s_abs['rel']!r})")
        check(len(s_abs.get("undated") or []) >= 3,
              f"files-absent: every reference it could not date is NAMED "
              f"(got {len(s_abs.get('undated') or [])})")
        empty = mark_panel([])
        check(empty["n_rows"] == 0 and empty["newest_rel"] == "UNKNOWN",
              "files-absent: an empty panel summarises without raising")
        check(mark_panel(None)["n_rows"] == 0, "files-absent: None rows do not raise")
        check(stamp(None)["rel"] == "UNKNOWN", "files-absent: a None text list does not raise")
        check(stamp([{"not": "a string"}])["rel"] == "UNKNOWN",
              "garbage: a non-string reference field does not raise")
    finally:
        g["REPO"] = keep_repo
        g["DATA_DIR"] = keep_data
        begin_refresh()

    # ---- formatting ------------------------------------------------------
    check(relative(None) == "UNKNOWN", "format: no age renders UNKNOWN")
    check(relative(30) == "just now" and relative(600) == "10m ago"
          and relative(7200) == "2h ago" and relative(86400 * 3) == "3.0d ago",
          f"format: the relative ladder reads plainly "
          f"({relative(30)}, {relative(600)}, {relative(7200)}, {relative(86400 * 3)})")
    check("FUTURE" in relative(-86400),
          f"format: a future-dated artifact SAYS so instead of being rounded to 'just now' "
          f"(got {relative(-86400)!r})")
    check(iso(0) is None and iso("x") is None, "format: a nonsense timestamp yields no absolute")
    check(isinstance(iso(time.time()), str), "format: the absolute value is kept available")

    # ---- stamp_known, for the two panels that already hold the mtime ------
    k = stamp_known(time.time() - 7200, "ACTIVITY", "the agent's own transcript")
    check(k["rel"] == "2h ago" and k["kind"] == "ACTIVITY" and k["when"],
          f"known: a pre-resolved artifact time is stamped without a second stat (got {k['rel']})")
    check(stamp_known(None, "ACTIVITY", "x")["rel"] == "UNKNOWN",
          "known NEGATIVE CONTROL: a missing pre-resolved time is UNKNOWN, not the clock")
    check(stamp_known(0, "ACTIVITY", "x")["ts"] is None,
          "known: a zero timestamp is UNKNOWN rather than 1970")

    # ---- live repo -------------------------------------------------------
    begin_refresh()
    t0 = time.time()
    live = stamp(["exp_orthographic_floor_vet_v1 (58a125c88), reproduced off disk 2026-08-16"],
                 carrier=REPO / "notes" / "progress_ledger.json")
    took_live = time.time() - t0
    check(took_live < 1.0, f"live: one stamp costs {took_live * 1000:.1f} ms")
    check(live["ts"] is not None,
          f"live: a real evidence line off this repo resolves ({live['rel']}, {live['kind']})")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evidence-age stamps for the status window")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    begin_refresh()
    demo = [
        ("headline readout", "exp_orthographic_floor_vet_v1 (58a125c88)"),
        ("CA3 completer", "data/exp_ca3_completion_partial_cue_v1/metrics.json"),
        ("thematic hub", "notes/STATUS.md TWO HUBS; .claude/scan-out/relation-supply.json"),
        ("nothing at all", "no artifact named here"),
    ]
    rows = [{"title": t, "evidence": stamp([e],
                                           carrier=REPO / "notes" / "progress_ledger.json")}
            for t, e in demo]
    summ = mark_panel(rows)
    if a.json:
        print(json.dumps({"rows": rows, "summary": summ, "cache": cache_stats()},
                         indent=2, default=str))
        return 0
    for r in rows:
        st = r["evidence"]
        print(f"{r['title']:<22} {line(st):<28} {st.get('kind')}  {st.get('source')}")
    print(f"\n{summ['plain']}")
    print(f"cache: {cache_stats()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
