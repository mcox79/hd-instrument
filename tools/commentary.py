#!/usr/bin/env python
"""THE OWNER'S SIDE CHANNEL -- `notes/COMMENTARY.md`, append-only, and the read/unread mark on it.

WHY THIS EXISTS (owner, 2026-08-16, verbatim): *"a box that I can write any commentary I'd like you
to look at during a run without interrupting you... a hook on that that tells you that I've sent
something to look at during a computational run."*

Two halves, and BOTH are load-bearing:
  1. A place to write that does not interrupt anything -- one append-only file, newest last.
  2. SOMETHING THAT MAKES THE AGENT NOTICE. A note nobody reads is worse than no note, because the
     owner reasonably believes it landed. So the same unread set is surfaced by
     `tools/session_start_hook.py` (every session start / clear / compact) and by
     `data/hooks/staging/stop_hook.py` (every turn boundary, including inside an unattended
     overnight run, which is exactly the "during a computational run" case).

IT MUST WORK FROM THE MARKDOWN FILE ALONE. The owner writes from other devices. So UNREAD IS NOT A
FLAG SET AT WRITE TIME -- nothing about "was this seen" is recorded when a note is added. Instead the
FILE is parsed on every check and each entry is keyed by its own content; an entry whose key is not
in the read-mark file is unread. A note typed straight into the markdown on a phone, with a text
editor, over a sync folder, or by hand with no timestamp at all, is therefore noticed identically to
one submitted through the status window. There is no privileged writer.

  KEY = sha1(timestamp + body). An EDITED note becomes unread again, deliberately: the agent has not
  seen the new words, and quietly treating changed content as already-read is how a correction gets
  lost.

FILE SHAPE (an API, per CLAUDE.md "a doc parsed by code is coupled to it"; the doc side is the
PARSER CONTRACT comment this module writes into the head of the file):

    ## 2026-08-16T22:41:07Z  --  from the status window
    the body, any number of lines, until the next `## ` heading

Anything before the first `## ` heading is the header and is preserved verbatim. Text typed after
the last entry WITHOUT a heading is still read, as one entry marked as having no timestamp -- a
hand-written note with no heading is the most likely hand edit there is, and dropping it would be
the exact failure this file exists to prevent.

  python tools/commentary.py add "text"        # append an entry
  python tools/commentary.py unread            # what has not been surfaced yet
  python tools/commentary.py unread --json
  python tools/commentary.py report            # the block the hooks inject
  python tools/commentary.py mark-read         # mark everything surfaced
  python tools/commentary.py list
  python tools/commentary.py self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# HD_COMMENTARY_PATH / HD_COMMENTARY_MARK exist so the hooks' self-tests can exercise the real
# code path against throwaway files instead of the owner's actual notes.
DOC = Path(os.environ.get("HD_COMMENTARY_PATH") or (REPO / "notes" / "COMMENTARY.md"))
MARK = Path(os.environ.get("HD_COMMENTARY_MARK")
            or (REPO / "data" / "hook_state" / "commentary_read.json"))

MAX_BYTES = 4_000_000
MAX_MARKS = 2000          # bounded so the mark file cannot grow without limit

HEADER = """\
# COMMENTARY -- anything you want me to look at, without interrupting me

Type below. Newest goes at the BOTTOM. You do not need to run anything and you do not need to wait
for me to be idle: I am told about anything unread at every session start AND at every turn
boundary, including in the middle of an unattended overnight run.

You can write here from ANY device, in ANY markdown editor. A heading is nice but not required --
text typed at the end with no heading is still picked up and still marked as unread.

<!-- PARSER CONTRACT -- READ BEFORE REWORDING.
     This document is parsed by tools/commentary.py, and its unread entries are injected by
     tools/session_start_hook.py and data/hooks/staging/stop_hook.py.
     The API is ONE literal: an entry begins with a line starting `## `.
     Everything above the first such line is this header and is preserved verbatim.
     Editing or adding entry TEXT is always safe and is the intended use.
     (CLAUDE.md: "A doc parsed by code is coupled to it".) -->
"""

_HEAD = re.compile(r"^##\s+(.*)$")
_TS = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _key(stamp: str, body: str) -> str:
    return hashlib.sha1(f"{stamp}\n{body.strip()}".encode("utf-8")).hexdigest()[:16]


def parse(text: str) -> list[dict]:
    """Every entry in the document, oldest first. Never raises on anything a human might type."""
    entries: list[dict] = []
    cur: dict | None = None
    pre: list[str] = []
    for ln in (text or "").splitlines():
        m = _HEAD.match(ln)
        if m:
            if cur is not None:
                entries.append(cur)
            head = m.group(1).strip()
            ts = _TS.search(head)
            cur = {"heading": head, "stamp": ts.group(1) if ts else "",
                   "source": head.split("--", 1)[1].strip() if "--" in head else "",
                   "lines": []}
            continue
        if cur is None:
            pre.append(ln)
        else:
            cur["lines"].append(ln)
    if cur is not None:
        entries.append(cur)

    # A HAND-WRITTEN NOTE WITH NO HEADING AT ALL. The owner types at the end of the file from a
    # phone and does not add `## ...`; dropping that is precisely the failure this module exists to
    # stop. It is only taken from text that sits AFTER the header block, and never from the header
    # itself (which is prose this tool wrote).
    if not entries and pre:
        loose = _loose_body(pre)
        if loose:
            entries.append({"heading": "(typed by hand, with no heading)", "stamp": "",
                            "source": "hand-written", "lines": loose.splitlines()})

    out = []
    for e in entries:
        body = "\n".join(e.pop("lines")).strip()
        if not body and not e.get("stamp"):
            continue
        e["body"] = body
        e["key"] = _key(e.get("stamp", ""), body)
        out.append(e)
    return out


def _loose_body(pre: list[str]) -> str:
    """Text in the preamble that is NOT this tool's own header or its parser-contract comment."""
    known = {ln.strip() for ln in HEADER.splitlines() if ln.strip()}
    keep, in_comment = [], False
    for ln in pre:
        s = ln.strip()
        if s.startswith("<!--"):
            in_comment = True
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if not s or s in known or s.startswith("#"):
            continue
        keep.append(ln.rstrip())
    return "\n".join(keep).strip()


def load(doc: Path | None = None) -> list[dict]:
    p = Path(doc) if doc else DOC
    try:
        if p.stat().st_size > MAX_BYTES:
            return parse(p.read_text(encoding="utf-8", errors="replace")[-MAX_BYTES:])
        return parse(p.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return []


def _read_marks(mark: Path | None = None) -> set:
    p = Path(mark) if mark else MARK
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return set()
    seen = d.get("seen") if isinstance(d, dict) else None
    return set(seen) if isinstance(seen, list) else set()


def _write_marks(keys, mark: Path | None = None) -> None:
    p = Path(mark) if mark else MARK
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        keep = list(keys)[-MAX_MARKS:]
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps({"seen": keep, "updated": _now()}, indent=1), encoding="utf-8")
        os.replace(str(tmp), str(p))
    except OSError:
        pass


def add(text: str, source: str = "", doc: Path | None = None) -> dict:
    """Append one entry. Returns the entry, so the caller can quote back exactly what landed.

    APPEND-ONLY AND ATOMIC-ENOUGH: opened in append mode, so a concurrent reader sees either the
    old file or the old file plus a whole entry, and nothing that already exists is ever rewritten.
    That is a deliberately weaker guarantee than the board's rewrite-in-place -- this file is a log,
    and a log that can lose earlier entries during a rewrite is not a log."""
    p = Path(doc) if doc else DOC
    body = (text or "").strip()
    if not body:
        raise ValueError("refusing to record an empty note")
    stamp = _now()
    src = (source or "").strip()
    head = f"## {stamp}" + (f"  --  {src}" if src else "")
    p.parent.mkdir(parents=True, exist_ok=True)
    fresh = not p.exists() or p.stat().st_size == 0
    with p.open("a", encoding="utf-8", newline="\n") as fh:
        if fresh:
            fh.write(HEADER + "\n")
        fh.write(f"\n{head}\n\n{body}\n")
    return {"heading": head, "stamp": stamp, "source": src, "body": body,
            "key": _key(stamp, body), "path": str(p)}


def unread(doc: Path | None = None, mark: Path | None = None) -> list[dict]:
    seen = _read_marks(mark)
    return [e for e in load(doc) if e["key"] not in seen]


def mark_read(entries=None, doc: Path | None = None, mark: Path | None = None) -> int:
    """Mark entries surfaced. With no argument, marks everything currently in the file."""
    seen = _read_marks(mark)
    add_keys = [e["key"] for e in (entries if entries is not None else load(doc))]
    before = len(seen)
    seen.update(add_keys)
    _write_marks(sorted(seen), mark)
    return len(seen) - before


def count_unread(doc: Path | None = None, mark: Path | None = None) -> int:
    """Cheap and never raises -- the hooks call this on every fire."""
    try:
        return len(unread(doc, mark))
    except Exception:
        return 0


def report(doc: Path | None = None, mark: Path | None = None, limit: int = 6,
           body_chars: int = 900) -> str:
    """The block the hooks inject. Returns '' when there is nothing unread.

    Returns the owner's words VERBATIM (only truncated, and visibly so). This text is the whole
    point of the channel; paraphrasing it in a summary would defeat it."""
    try:
        rows = unread(doc, mark)
    except Exception as exc:                    # pragma: no cover - a hook must never die here
        return f"[commentary] could not be read ({type(exc).__name__}: {exc})"
    if not rows:
        return ""
    p = Path(doc) if doc else DOC
    L = [f"[commentary] {len(rows)} UNREAD NOTE(S) FROM THE OWNER <-- READ THESE BEFORE CONTINUING",
         f"    they wrote them in {p} while you were working; they are NOT a question on the board",
         "    and they are not blocking -- but they are the owner talking to you, so act on them."]
    for e in rows[-limit:]:
        when = e.get("stamp") or "no timestamp (typed by hand)"
        src = f" ({e['source']})" if e.get("source") else ""
        body = e.get("body", "")
        if len(body) > body_chars:
            body = body[:body_chars] + f" [...{len(body) - body_chars} more characters]"
        L.append(f"    --- {when}{src} ---")
        L.extend(f"      {ln}" for ln in body.splitlines())
    if len(rows) > limit:
        L.append(f"    ... and {len(rows) - limit} older unread note(s); "
                 f"run: python tools/commentary.py unread")
    return "\n".join(L)


# ---------------------------------------------------------------------------

def self_test() -> int:
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="commentary_selftest_"))
    doc, mk = td / "COMMENTARY.md", td / "read.json"

    # 1. Nothing yet: never a crash, never a phantom note.
    check(unread(doc, mk) == [] and report(doc, mk) == "",
          "an absent file reports nothing unread, and does not raise")

    # 2. Add -> unread -> surfaced -> read. Exactly once.
    e1 = add("the first thing I want you to look at", "the status window", doc)
    check(doc.exists() and "PARSER CONTRACT" in doc.read_text(encoding="utf-8"),
          "the file is created WITH its parser contract at the top")
    u = unread(doc, mk)
    check(len(u) == 1 and u[0]["body"] == e1["body"], f"a new note is unread ({len(u)})")
    check("the first thing I want you to look at" in report(doc, mk),
          "and the hook block quotes it VERBATIM, not as a summary")
    mark_read(u, doc, mk)
    check(unread(doc, mk) == [], "once surfaced it is read, so it cannot nag forever")

    # 3. THE HAND EDIT IS THE POINT. A note typed straight into the markdown, from another device,
    #    with its own heading, must be noticed with no help from this tool.
    with doc.open("a", encoding="utf-8") as fh:
        fh.write("\n## 2026-08-16T23:00:00Z  --  typed on my phone\n\n"
                 "check the affect channel before you spend another night on bridging\n")
    u2 = unread(doc, mk)
    check(len(u2) == 1 and "affect channel" in u2[0]["body"],
          f"a note hand-written into the file is unread with no tool involved ({len(u2)})")
    check(u2 and u2[0]["source"] == "typed on my phone",
          f"and its source line survives ({u2 and u2[0]['source']!r})")
    mark_read(u2, doc, mk)

    # 4. A HAND EDIT WITH NO HEADING AT ALL -- the likeliest phone edit there is.
    doc2, mk2 = td / "loose.md", td / "loose.json"
    doc2.write_text(HEADER + "\n\nI just typed this at the bottom with no heading\n",
                    encoding="utf-8")
    u3 = unread(doc2, mk2)
    check(len(u3) == 1 and "no heading" in u3[0]["body"],
          f"text with NO heading is still picked up rather than dropped ({len(u3)}: "
          f"{[e['body'][:40] for e in u3]})")

    # 5. AN EDIT TO AN ALREADY-READ NOTE RESURFACES IT. Changed words have not been seen.
    txt = doc.read_text(encoding="utf-8").replace("check the affect channel",
                                                  "ACTUALLY, check the affect channel")
    doc.write_text(txt, encoding="utf-8")
    u4 = unread(doc, mk)
    check(len(u4) == 1 and "ACTUALLY" in u4[0]["body"],
          f"editing a note the agent had already seen makes it unread again ({len(u4)})")
    mark_read(u4, doc, mk)
    check(unread(doc, mk) == [], "and marking it read settles it again")

    # 6. APPEND-ONLY: an older entry is never lost by a later write.
    n_before = len(load(doc))
    add("a third note", "cli", doc)
    entries = load(doc)
    check(len(entries) == n_before + 1, f"appending adds exactly one entry ({len(entries)})")
    check(any("ACTUALLY" in e["body"] for e in entries),
          "and the earlier entries are all still there -- this file is a log, never rewritten")
    check(entries[-1]["body"] == "a third note", "newest is last, which is where a log grows")

    # 7. Multi-line bodies, and a `#`-bearing line inside one, survive whole.
    add("line one\nline two with a # in it\nline three", "window", doc)
    got = load(doc)[-1]["body"]
    check(got == "line one\nline two with a # in it\nline three",
          f"a multi-line note round-trips exactly (got {got!r})")

    # 8. Never raises on garbage, and refuses to record nothing.
    (td / "garbage.md").write_bytes(b"\xff\xfe not utf8 at all \x00\x00## \n")
    check(isinstance(load(td / "garbage.md"), list), "a corrupt file yields a list, not an exception")
    try:
        add("   ", "x", doc)
        check(False, "an empty note is refused")
    except ValueError:
        check(True, "an empty note is refused")

    # 9. Cheap enough for a 10 s hook budget.
    import time as _t
    t0 = _t.time()
    for _ in range(50):
        count_unread(doc, mk)
    dt = (_t.time() - t0) / 50
    check(dt < 0.05, f"one unread check costs {dt*1000:.2f} ms -- safe inside the hook budget")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="the owner's side channel")
    ap.add_argument("--doc", default=None)
    ap.add_argument("--mark", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add")
    p_add.add_argument("text")
    p_add.add_argument("--source", default="the command line")
    p_un = sub.add_parser("unread")
    p_un.add_argument("--json", action="store_true")
    sub.add_parser("report")
    sub.add_parser("mark-read")
    sub.add_parser("list")
    sub.add_parser("self-test")
    args = ap.parse_args(argv)
    doc = Path(args.doc) if args.doc else None
    mark = Path(args.mark) if args.mark else None

    if args.cmd == "self-test":
        return self_test()
    if args.cmd == "add":
        e = add(args.text, args.source, doc)
        print(f"[commentary] recorded at {e['stamp']} in {e['path']}")
        print(f"[commentary] what was written: {e['body']}")
        return 0
    if args.cmd == "unread":
        rows = unread(doc, mark)
        if args.json:
            print(json.dumps(rows, indent=2))
        elif not rows:
            print("[commentary] nothing unread.")
        else:
            print(report(doc, mark))
        return 0
    if args.cmd == "report":
        out = report(doc, mark)
        print(out if out else "[commentary] nothing unread.")
        return 0
    if args.cmd == "mark-read":
        n = mark_read(None, doc, mark)
        print(f"[commentary] marked {n} newly-seen note(s) as read")
        return 0
    if args.cmd == "list":
        for e in load(doc):
            print(f"{e.get('stamp') or '(no timestamp)'}  {e['key']}  "
                  f"{e['body'][:100].splitlines()[0] if e['body'] else ''}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
