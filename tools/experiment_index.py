"""EXPERIMENT INDEX -- a prior-work check that actually returns something.

WHY THIS EXISTS (2026-08-18 incident, and it cost a full night).

`tools/substrate_query.sh` -- the MANDATORY prior-work check -- returns ZERO BYTES and EXITS 0.
Every agent that ran it got an empty answer and reported "no prior work found". So did the
Director. On 2026-08-18 that produced a night of work rediscovering a conclusion reached on
2026-08-17: that our write rule `self._sums[lemma] += ctx_vec` is a FIRST-ORDER (syntagmatic)
statistic while the task scores SUBSTITUTABILITY (paradigmatic). Two cells had already tested the
paradigmatic write rule and the second-order read-out and reported them in their own docstrings.

The archive was never the problem. It holds 5,877 experiment files spanning 2026-05-17 to
2026-08-18 and 7,786 landed results. RETRIEVAL was the problem. An absence claim requires an
ENUMERATION, and there was no working way to enumerate.

WHAT THIS DOES, and what it deliberately does NOT do.
  DOES     walk experiments/*.py and data/exp_*/metrics.json, pull each cell's VERDICT, its
           docstring headline, its dates, and whether it LANDED; write one JSONL row per cell;
           and answer keyword queries over that index in about a second, offline, no服务.
  DOES NOT embed anything, call any model, or depend on the livelocked director_kb. It is a
           grep over a flat file, which is precisely why it cannot silently return nothing:
           `query` prints the number of rows scanned every time, so an empty result is
           distinguishable from a broken tool. THAT DISTINCTION IS THE WHOLE POINT.

USAGE
  python tools/experiment_index.py build              # rebuild data/experiment_index.jsonl
  python tools/experiment_index.py query paradigmatic substitutability
  python tools/experiment_index.py query --all-terms write rule paradigmatic
  python tools/experiment_index.py verdicts           # verdict-vocabulary histogram

READ THE OUTPUT LINE "scanned N rows". If N is 0 the INDEX is broken, not the archive.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "experiments"
DATA = REPO / "data"
INDEX = DATA / "experiment_index.jsonl"

_DOC = re.compile(r'^\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', re.S)


def _headline(src: str) -> str:
    m = _DOC.match(src)
    if not m:
        return ""
    body = " ".join(l.strip() for l in m.group(1).strip().splitlines()[:6])
    return re.sub(r"\s+", " ", body)[:400]


def _ran_date(mp: Path):
    """WHEN THE CELL ACTUALLY RAN -- from the metrics' OWN internal timestamp, never the file mtime.

    THIS FUNCTION EXISTS BECAUSE THE FIRST VERSION OF THIS INDEX USED mtime AND PRODUCED A FALSE
    HEADLINE WITHIN THE HOUR. Exactly 60 metrics.json share the minute 2026-08-17 17:44 and 3,850
    share 2026-07-03 14:28 -- bulk touches, not runs. Ranked on mtime, July work resurfaced as
    "landed 2026-08-17", and the Director reported to the owner that 25 results had been ignored
    the day after they landed. NONE of them ran that day; those six ran 2026-07-17 to 07-23.

    A FILE'S MTIME IS WHEN IT WAS LAST WRITTEN, NOT WHEN THE SCIENCE HAPPENED. Any copy, checkout,
    sync or chmod rewrites it. Returns (date, source) so every consumer can see which it got.
    """
    try:
        d = json.loads(mp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None, "unreadable"
    for k in ("ts_iso", "timestamp", "ts", "run_ts", "started_utc", "completed_utc"):
        v = d.get(k)
        if isinstance(v, str) and len(v) >= 10 and v[4] == "-" and v[7] == "-":
            return v[:10], "ts_iso"
    return time.strftime("%Y-%m-%d", time.localtime(mp.stat().st_mtime)), "mtime_FALLBACK"


def _verdict(mp: Path):
    try:
        d = json.loads(mp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    for k in ("verdict", "VERDICT", "verdict_msg", "result", "branch"):
        v = d.get(k)
        if isinstance(v, str):
            return v[:300]
        if isinstance(v, dict):
            for kk in ("verdict", "label", "name"):
                if isinstance(v.get(kk), str):
                    return v[kk][:300]
    return None


def build() -> int:
    rows, n_src = [], 0
    t0 = time.time()
    for f in sorted(os.listdir(EXP)):
        if not f.endswith(".py"):
            continue
        n_src += 1
        p = EXP / f
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        stem = f[:-3]
        row = {
            "cell": stem,
            "mtime": time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime)),
            "headline": _headline(src),
            "landed": False, "verdict": None, "landed_date": None,
        }
        for cand in (DATA / stem, DATA / (stem + "_v1")):
            mp = cand / "metrics.json"
            if mp.exists():
                row["landed"] = True
                row["verdict"] = _verdict(mp)
                # NOT `src` -- that name already holds this file's SOURCE TEXT a few lines above.
                ran_d, ran_src = _ran_date(mp)
                row["landed_date"] = ran_d
                row["date_source"] = ran_src
                break
        rows.append(row)

    # results whose directory has no matching source file are still evidence -- keep them
    known = {r["cell"] for r in rows}
    for d in sorted(os.listdir(DATA)):
        if not d.startswith("exp_") or d in known:
            continue
        mp = DATA / d / "metrics.json"
        if mp.exists():
            dt, src = _ran_date(mp)
            rows.append({"cell": d, "mtime": None, "headline": "(result only, no source file)",
                         "landed": True, "verdict": _verdict(mp),
                         "landed_date": dt, "date_source": src})
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8", newline="") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    landed = sum(1 for r in rows if r["landed"])
    print(f"[build] {n_src:,} source files, {len(rows):,} index rows, {landed:,} landed "
          f"({time.time()-t0:.0f}s) -> {INDEX}")
    return 0


def _load():
    if not INDEX.exists():
        print("[query] INDEX MISSING -- run `build` first. This is a TOOL failure, "
              "NOT evidence that no prior work exists.", file=sys.stderr)
        return []
    out = []
    with open(INDEX, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def query(terms, all_terms=False, limit=40) -> int:
    rows = _load()
    # The count is printed FIRST and ALWAYS. A tool that can return nothing without saying how
    # much it looked at is how "no prior work found" became meaningless in this repo.
    print(f"[query] scanned {len(rows):,} indexed cells for {terms} "
          f"({'ALL' if all_terms else 'ANY'} must match)")
    if not rows:
        return 1
    terms_l = [t.lower() for t in terms]
    hits = []
    for r in rows:
        blob = f"{r['cell']} {r.get('headline') or ''} {r.get('verdict') or ''}".lower()
        n = sum(1 for t in terms_l if t in blob)
        if (n == len(terms_l)) if all_terms else (n > 0):
            hits.append((n, r))
    hits.sort(key=lambda x: (-x[0], not x[1]["landed"], x[1]["cell"]))
    print(f"[query] {len(hits)} matching cells "
          f"({sum(1 for _, r in hits if r['landed'])} landed)\n")
    for n, r in hits[:limit]:
        flag = "LANDED" if r["landed"] else "  ----"
        print(f"{flag} {r.get('landed_date') or r.get('mtime') or '?':10s} {r['cell'][:70]}")
        if r.get("verdict"):
            print(f"         verdict: {r['verdict'][:150]}")
    if len(hits) > limit:
        print(f"\n  ... {len(hits)-limit} more (raise --limit)")
    return 0


def verdicts(limit=40) -> int:
    import collections
    rows = _load()
    print(f"[verdicts] scanned {len(rows):,} indexed cells")
    c = collections.Counter()
    for r in rows:
        v = r.get("verdict")
        if v:
            c[re.split(r"[_\s]", v.strip())[0][:40].upper()] += 1
    for k, n in c.most_common(limit):
        print(f"  {n:>5,}  {k}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "build":
        return build()
    if cmd == "verdicts":
        return verdicts()
    if cmd == "query":
        args = sys.argv[2:]
        all_terms = "--all-terms" in args
        args = [a for a in args if not a.startswith("--")]
        if not args:
            print("give at least one term", file=sys.stderr)
            return 2
        return query(args, all_terms=all_terms)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
