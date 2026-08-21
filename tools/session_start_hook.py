"""SessionStart hook: inject the load-bearing rules + live durability-gate status.

Why this exists: the project's durability anchors were advisory reads ("run the audit at
session start") or OS scheduled tasks. Both failed silently -- 11 hd_* tasks disabled ~12
days unnoticed, director_kb ingest disabled 6 days unnoticed. A hook is neither: it fires
deterministically at every session start/clear/compact regardless of scheduler state or
whether the agent remembers to read anything.

Contract: prints ONE json object to stdout: {"additionalContext": "<text>"}.
Never blocks a session: every probe is timeout-bounded and failure is reported, not raised.

Usage: python tools/session_start_hook.py
"""
from __future__ import annotations
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = REPO / '.venv' / 'Scripts' / 'python.exe'
STATUS_MD = REPO / 'notes' / 'STATUS.md'
# Mirrors the cap in notes/STATUS_SPEC.md sec 7 (8192 -> 8704 on 2026-08-15;
# 8704 -> 28672 on 2026-08-21 by OWNER decision on board Q92, 'sure raise it'). Changing it
# there means changing it here in the same commit; see the SIZE GUARD note in status_summary().
STATUS_CAP_BYTES = 28672
PROBE_TIMEOUT_SEC = 25

# The non-negotiables. Kept SHORT on purpose: a wall of text gets skimmed, and these have to
# survive being read every single session. Detail lives in the charter, not here.
RULES = """\
== hd-instrument: NON-NEGOTIABLES (injected every session) ==
1. GLASS-BOX. No external LLM at inference. No borrowed embedding/parser/reader AS the
   meaning or comprehension organ. Supplying knowledge/data/structure is fine; supplying
   the mechanism is the forbidden shortcut.
2. BRAIN IS THE REFERENCE STANDARD + AN EXISTENCE PROOF. A shortfall is never a ceiling.
   On every negative: audit each element vs how the brain does that element
   (SHAPE + POSITION + METRIC), name the gap, build toward it.
3. RIGHT, NOT EASY. Select the next step by brain-foundational correctness, NOT by cost.
   Difficulty is irrelevant to the pick. If you are reaching for a frozen head, a cheap
   proxy, or a "deferred/escalation path" beside a hard component -- STOP, do the hard one.
   A cheap probe may MEASURE; it may never SET DIRECTION.
4. EVIDENCE BEFORE CLAIMS. Only held-out / public-benchmark numbers count. Verify on disk;
   never propagate an agent's claim unchecked. VET positives as hard as negatives.
   A single-seed win is a HYPOTHESIS. Flat learning result = broken experiment, not a ceiling.
5. WIRE, DON'T ISLAND. Query data/capability_registry.jsonl BEFORE building. At land-time,
   every cert/HARD_PASS gets WIRE (+target) or SHELVE (+revival criteria). No limbo.
6. DELEGATE. Director does judgment/strategy/verification; hdi_* subagents do the building.
   Tripwire: editing experiments/*.py or running smoke in main thread = spawn hdi_exp_dev.

== HOW TO TALK TO THE USER (USER directive 2026-08-12) ==
- PLAIN LANGUAGE. No jargon where an ordinary word works. Expand any term the first time.
- ANALOGIES only when they genuinely clarify. Never decorative.
- SUCCINCT. Lead with the answer. Cut preamble, restatement, and hedging. Long replies are
  themselves thread time -- depth only when asked.

== DELEGATION PROTOCOL (USER directive 2026-08-12, after repeated main-thread lockups) ==
The user QUEUES messages behind a busy thread. A blocked main thread blocks THEM. Measured
cause of the lockups was NOT the subagents -- it was the director chaining small inline calls,
typing documents by hand, and writing long replies.
- ONE TURN = ONE ACTION. Either a batch of dispatches OR a reply. Never a chain of tool calls
  followed by a reply.
- DELEGATE anything that takes >~10s, reads >~50 lines, or writes a file.
- JUDGEMENT stays with the director; TYPING does not. Have the agent pre-compact the input to
  the minimum needed to rule (a 50-line table, not a 3000-line JSON), rule in one pass, then
  have an agent persist the ruling.
- BATCH independent work -- 3-4 agents dispatched together, not one per turn. Serialising
  parallelisable work is the main source of wasted wall-clock.
- NEVER read a large artifact into the main thread to inspect it. Ask an agent for the digest.
"""


def probe(label: str, script: str, *args: str) -> str:
    """Run a repo tool, return a one-block summary. Never raises."""
    path = REPO / 'tools' / script
    if not path.exists():
        return f"[{label}] SKIP - {script} not found"
    if not PY.exists():
        return f"[{label}] SKIP - venv python not found"
    try:
        proc = subprocess.run(
            [str(PY), str(path), *args],
            cwd=str(REPO), capture_output=True, text=True, timeout=PROBE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return f"[{label}] TIMEOUT after {PROBE_TIMEOUT_SEC}s (probe skipped, not a failure)"
    except OSError as exc:
        return f"[{label}] ERROR launching: {exc}"
    out = (proc.stdout or '').strip().splitlines()
    err = (proc.stderr or '').strip().splitlines()
    tail = out[-12:] if out else err[-12:]
    status = 'OK' if proc.returncode == 0 else f'EXIT {proc.returncode} <-- ATTENTION'
    body = '\n'.join(f'    {line}' for line in tail) if tail else '    (no output)'
    return f"[{label}] {status}\n{body}"


def _missing_literal_banner(literal: str, desc: str, path: Path) -> str:
    """Unmissable banner for a required-literal parse failure. FAIL LOUD, not a placeholder
    that reads like ordinary output -- that is exactly how the 2026-08-13 reword survived
    undetected (see CLAUDE.md "A doc parsed by code is coupled to it"). Kept to plain string
    formatting (no logging config, no extra deps) so it stays fast and dependency-free."""
    bar = '=' * 78
    return (
        f"{bar}\n"
        f"*** MISSING REQUIRED LITERAL {literal!r} ({desc}) ***\n"
        f"    file: {path}\n"
        f"    tools/session_start_hook.py status_summary() parses this EXACT string; it is\n"
        f"    an API, not a formatting choice. Read notes/STATUS_SPEC.md sec 2 before\n"
        f"    rewording it, and update this parser in the same commit if you must.\n"
        f"{bar}"
    )


def status_summary(path: Path = STATUS_MD) -> str:
    """Cheap summary of notes/STATUS.md: its AS-OF line, its WHAT IS RUNNING section, and
    days since it was last modified (loud warning past 1 day).

    Deliberately a plain file read + line scan + a single os.stat call -- no subprocess, no
    git call, no parsing beyond splitting on section headers. The staleness GUARD (which does
    need a git call) lives in status_freshness_check.py and is reported separately via probe().

    `path` defaults to the real STATUS_MD but is overridable so `_self_test()` below can point
    this at a fixture file without ever touching the real notes/STATUS.md.
    """
    if not path.exists():
        return f"[STATUS.md] MISSING <-- ATTENTION\n    create {path} (see task history)"

    try:
        text = path.read_text(encoding='utf-8')
        mtime = path.stat().st_mtime
    except OSError as exc:
        return f"[STATUS.md] unreadable ({exc})"

    # CONTRACT: the two literals below ('AS OF:' and '## WHAT IS RUNNING') are parsed out of the
    # human-edited notes/STATUS.md. They are an API, not a formatting choice. Both were reworded
    # away on 2026-08-13 ('AS OF' without the colon, '## RUNNING / BLOCKED'); this function did not
    # error, it silently injected placeholders into every compaction recovery until someone read
    # the injected text closely. Doc-side record: notes/STATUS_SPEC.md sec 2. If either literal
    # changes, change it here in the same commit. FAILS LOUDLY below instead of substituting a
    # quiet placeholder -- see CLAUDE.md "A doc parsed by code is coupled to it".
    lines = text.splitlines()
    as_of_match = next((ln.strip() for ln in lines if ln.strip().startswith('AS OF:')), None)
    as_of_line = as_of_match if as_of_match is not None else \
        _missing_literal_banner('AS OF:', 'the AS-OF header line', path)

    running_lines: list[str] = []
    in_running = False
    found_running_heading = False
    for ln in lines:
        if ln.strip().startswith('## WHAT IS RUNNING'):
            in_running = True
            found_running_heading = True
            continue
        if in_running and ln.strip().startswith('## '):
            break
        if in_running and ln.strip():
            running_lines.append(ln)
    if not found_running_heading:
        banner = _missing_literal_banner('## WHAT IS RUNNING', 'the WHAT IS RUNNING heading', path)
        running_body = '\n'.join(f'    {ln}' for ln in banner.splitlines())
    elif running_lines:
        running_body = '\n'.join(f'    {ln}' for ln in running_lines)
    else:
        # Heading IS present, just has no non-empty lines under it -- a real (if unusual) empty
        # section, not a parse failure. Distinct from the missing-heading case above.
        running_body = '    (section present but empty)'

    age_days = (time.time() - mtime) / 86400.0
    age_flag = ' <-- STALE, over 1 day old, rewrite it' if age_days > 1.0 else ''
    # SIZE GUARD, added 2026-08-21. On that date STATUS.md was found at 308,692 B against this cap
    # -- 35x -- because sessions had been APPENDING findings instead of rewriting in place, and
    # NOTHING EVER REPORTED IT. The trim moved 135 sections out (nothing deleted); this line is the
    # part that stops it silently recurring. Same lesson as rank_with_ties.py and
    # replication_gate.py: WRITE THE CONTROL INTO THE CODE, NOT THE CAUTION INTO THE PROSE.
    # Costs one f-string on a stat() this function already makes, so the <10s hook budget is safe.
    # CONTRACT: STATUS_CAP_BYTES mirrors the cap in notes/STATUS_SPEC.md sec 7. If that cap is
    # changed there, change it HERE in the same commit -- doc parsed by code, marked on both sides.
    n_bytes = len(text.encode('utf-8'))
    over = n_bytes / STATUS_CAP_BYTES
    size_flag = ('  <-- %.1fx OVER CAP. Do NOT byte-shave: STATUS_SPEC.md sec 7 escalation is '
                 'MOVE-to-STATUS_LESSONS first, and sec 6 forbids the agent that needs the room '
                 'from raising the cap.' % over) if over > 1.5 else ''

    # THE OTHER TWO LITERALS, ADDED 2026-08-21 BECAUSE THIS GUARD HANDED OUT A FALSE GREEN.
    # notes/STATUS_SPEC.md sec 2 names FOUR machine-parsed literals. This function guarded only the
    # two IT consumes ('AS OF:' and '## WHAT IS RUNNING'), leaving '## POSITION' and '## TOP ITEM'
    # guarded solely by tools/board.py. On 2026-08-21 BOTH of those headings were destroyed -- two
    # unterminated backticks absorbed them, and their whole sections, into the STATUS.md header
    # paragraph -- and board.py DID fail loud, exactly as designed... into notes/BOARD.md, which
    # nothing re-reads at session start. Meanwhile _self_test() below asserted "the real
    # notes/STATUS.md parses clean" and PASSED THE WHOLE TIME, because A CHECKER THAT CHECKS A
    # SUBSET REPORTS GREEN ON A BROKEN FILE (STATUS.md standing discipline 3, 5th instance).
    # TWO LESSONS, both cheap to state and expensive to re-learn:
    #   1. A CONTROL THAT FIRES INTO A FILE NOBODY READS IS NOT YET A CONTROL. Fire it where the
    #      reading is guaranteed -- which for this project is the session-start injection.
    #   2. A POSITIVE CONTROL IS ONLY AS BROAD AS ITS ASSERTION. "Parses clean" meant "clean on the
    #      two literals I happen to parse", and it read like "clean".
    # CONTRACT: all four literals are now checked here. If any changes, change notes/STATUS_SPEC.md
    # sec 2, tools/board.py AND this file in the same commit.
    heading_banners = [
        _missing_literal_banner(lit, desc, path)
        for lit, desc in (('## POSITION', 'the POSITION heading'),
                          ('## TOP ITEM', 'the TOP ITEM heading'))
        if not any(ln.strip().startswith(lit) for ln in lines)
    ]
    heading_body = ('\n' + '\n'.join(heading_banners)) if heading_banners else ''

    return (
        f"[STATUS.md] {as_of_line}\n"
        f"    age: {age_days:.2f} days{age_flag}\n"
        f"    size: {n_bytes:,} B of {STATUS_CAP_BYTES:,} B cap{size_flag}{heading_body}\n"
        f"  WHAT IS RUNNING:\n{running_body}"
    )


def _self_test() -> int:
    """Prove status_summary() fails LOUDLY (unmissable banner), not silently (a placeholder
    that reads like ordinary output), when a required literal is missing. Uses FIXTURE files
    in a tempdir -- never reads or mutates the real notes/STATUS.md for the failure cases.
    Run: .venv/Scripts/python.exe tools/session_start_hook.py --self-test
    """
    import tempfile
    ok = True

    with tempfile.TemporaryDirectory() as td:
        fixture = Path(td) / 'STATUS_fixture_no_as_of.md'
        fixture.write_text(
            "# STATUS\n\nNo as-of header on this fixture.\n\n## WHAT IS RUNNING\n- nothing\n",
            encoding='utf-8',
        )
        out = status_summary(fixture)
        if 'MISSING REQUIRED LITERAL' in out and 'AS OF:' in out:
            print("[self-test] PASS: missing 'AS OF:' triggers the loud banner")
        else:
            print(f"[self-test] FAIL: missing 'AS OF:' did NOT trigger the loud banner:\n{out}")
            ok = False

    with tempfile.TemporaryDirectory() as td:
        fixture = Path(td) / 'STATUS_fixture_no_running.md'
        fixture.write_text(
            "# STATUS\n\nAS OF: 2099-01-01 | fixture\n\n## SOMETHING ELSE\n- x\n",
            encoding='utf-8',
        )
        out = status_summary(fixture)
        if 'MISSING REQUIRED LITERAL' in out and 'WHAT IS RUNNING' in out:
            print("[self-test] PASS: missing '## WHAT IS RUNNING' triggers the loud banner")
        else:
            print(f"[self-test] FAIL: missing '## WHAT IS RUNNING' did NOT trigger the loud banner:\n{out}")
            ok = False

    # THE TWO LITERALS board.py OWNS -- both directions, added 2026-08-21. These are the ones that
    # actually went missing, and NOTHING in this file noticed for hours. A fixture that is complete
    # except for ONE heading is the honest test: it proves the guard is per-literal rather than
    # firing on any old malformed file.
    _COMPLETE = ("# STATUS\n\nAS OF: 2099-01-01 | fixture\n\n## POSITION\n- p\n\n"
                 "## TOP ITEM\n- t\n\n## WHAT IS RUNNING\n- nothing\n")
    for literal in ('## POSITION', '## TOP ITEM'):
        with tempfile.TemporaryDirectory() as td:
            fixture = Path(td) / 'STATUS_fixture_missing_heading.md'
            # Drop exactly ONE heading line; everything else stays valid.
            fixture.write_text(
                '\n'.join(ln for ln in _COMPLETE.splitlines() if ln.strip() != literal) + '\n',
                encoding='utf-8',
            )
            out = status_summary(fixture)
            if 'MISSING REQUIRED LITERAL' in out and literal in out:
                print(f"[self-test] PASS: missing '{literal}' triggers the loud banner")
            else:
                print(f"[self-test] FAIL: missing '{literal}' did NOT trigger the loud banner:\n{out}")
                ok = False

    # ...and the negative direction, which is the half that would have caught the 2026-08-21 break:
    # a file with ALL FOUR literals must stay silent, or the guard is cry-wolf and gets ignored.
    with tempfile.TemporaryDirectory() as td:
        fixture = Path(td) / 'STATUS_fixture_complete.md'
        fixture.write_text(_COMPLETE, encoding='utf-8')
        if 'MISSING REQUIRED LITERAL' not in status_summary(fixture):
            print("[self-test] PASS: a file with all four literals triggers NO banner")
        else:
            print("[self-test] FAIL: a complete fixture wrongly triggered a banner")
            ok = False

    # SIZE GUARD -- both directions. An over-cap fixture MUST warn, and an under-cap fixture MUST
    # NOT, because a guard that fires on a compliant file is a guard that gets ignored (the exact
    # cry-wolf failure that made read_what_the_cell_told_you.py flag 708 cells).
    # Fixture carries all four literals so this tests the SIZE dimension ALONE.
    with tempfile.TemporaryDirectory() as td:
        head = _COMPLETE
        big = Path(td) / 'STATUS_fixture_over_cap.md'
        big.write_text(head + ("x" * (STATUS_CAP_BYTES * 2)), encoding='utf-8')
        out_big = status_summary(big)
        small = Path(td) / 'STATUS_fixture_under_cap.md'
        small.write_text(head, encoding='utf-8')
        out_small = status_summary(small)
        if 'OVER CAP' in out_big and 'OVER CAP' not in out_small:
            print("[self-test] PASS: size guard fires over cap and stays silent under it")
        else:
            print("[self-test] FAIL: size guard over=%s under=%s"
                  % ('OVER CAP' in out_big, 'OVER CAP' in out_small))
            ok = False
        if 'size:' not in out_small:
            print("[self-test] FAIL: the size line is absent from a compliant file")
            ok = False

    # Sanity: the REAL STATUS.md (read-only here, never written) must NOT trigger either banner.
    out = status_summary(STATUS_MD)
    if 'MISSING REQUIRED LITERAL' not in out:
        print("[self-test] PASS: the real notes/STATUS.md parses clean (no false-positive banner)")
    else:
        print(f"[self-test] FAIL: the real notes/STATUS.md incorrectly triggered a banner:\n{out}")
        ok = False

    # board_report(): must count open questions, and must never raise on a missing/garbage board.
    with tempfile.TemporaryDirectory() as td:
        missing = Path(td) / 'no_board.md'
        out = board_report(missing)
        if 'no board yet' in out:
            print("[self-test] PASS: board_report reports a missing board without raising")
        else:
            print(f"[self-test] FAIL: board_report on a missing board said:\n{out}")
            ok = False

        garbage = Path(td) / 'garbage_board.md'
        garbage.write_text("## QUESTIONS FOR YOU\n\nthe owner deleted the table\n", encoding='utf-8')
        out = board_report(garbage)
        if 'ERROR' not in out:
            print("[self-test] PASS: board_report survives a hand-destroyed board table")
        else:
            print(f"[self-test] FAIL: board_report raised on a destroyed table:\n{out}")
            ok = False

        two = Path(td) / 'two_open.md'
        two.write_text(
            "## QUESTIONS FOR YOU\n\n"
            "| ID | Question | What's blocked on it | My recommendation | ANSWER | status |\n"
            "|---|---|---|---|---|---|\n"
            "| Q1 | first? | a | b |  | open |\n"
            "| Q2 | second? | a | b |  | open |\n"
            "| Q3 | third? | a | b | already answered by hand | open |\n",
            encoding='utf-8')
        out = board_report(two)
        if '2 OPEN QUESTION(S)' in out:
            print("[self-test] PASS: board_report counts 2 open (the hand-answered row is not open)")
        else:
            print(f"[self-test] FAIL: board_report miscounted:\n{out}")
            ok = False

    # commentary_report(): must surface an unread note verbatim, mark it read, and never raise.
    with tempfile.TemporaryDirectory() as td:
        doc = Path(td) / 'COMMENTARY.md'
        mk = Path(td) / 'read.json'
        out = commentary_report(doc, mk)
        if 'no unread notes' in out:
            print("[self-test] PASS commentary_report on an absent file says so without raising")
        else:
            print(f"[self-test] FAIL commentary_report on an absent file said:\n{out}")
            ok = False

        doc.write_text("## 2026-08-16T23:00:00Z  --  typed on my phone\n\n"
                       "look at the affect channel before another night on bridging\n",
                       encoding='utf-8')
        out = commentary_report(doc, mk)
        if 'affect channel' in out and 'UNREAD' in out:
            print("[self-test] PASS commentary_report surfaces a hand-written note VERBATIM")
        else:
            print(f"[self-test] FAIL commentary_report did not surface the note:\n{out}")
            ok = False

        out2 = commentary_report(doc, mk)
        if 'no unread notes' in out2:
            print("[self-test] PASS and it is marked read, so it surfaces ONCE, not every session")
        else:
            print(f"[self-test] FAIL the note surfaced twice:\n{out2}")
            ok = False

        with doc.open('a', encoding='utf-8') as fh:
            fh.write("\n## 2026-08-16T23:30:00Z\n\nand a second, newer one\n")
        out3 = commentary_report(doc, mk)
        if 'second, newer one' in out3 and 'affect channel' not in out3:
            print("[self-test] PASS a NEW note surfaces while the already-seen one stays quiet")
        else:
            print(f"[self-test] FAIL new-note handling wrong:\n{out3}")
            ok = False

    print(f"[self-test] {'ALL PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


def board_report(board_path: Path | None = None) -> str:
    """Surface the count of open questions on notes/BOARD.md.

    CONTRACT / COUPLING (CLAUDE.md "A doc parsed by code is coupled to it"): the parsing of
    notes/BOARD.md lives in ONE place, `tools/board.py`, and this function calls it rather than
    re-implementing a second table parser. That is deliberate: two parsers for one document is
    how the literals drift apart. The literals themselves (`## QUESTIONS FOR YOU`, `## ANSWERED`,
    the column orders) are documented on the doc side in the PARSER CONTRACT comment that
    board.py writes into the top of BOARD.md.

    Imported by absolute path, not by name: this hook is invoked with an absolute script path and
    an unpredictable cwd. Never raises -- a broken board must not block a session start.
    """
    import importlib.util
    bp = board_path
    try:
        mod_path = REPO / 'tools' / 'board.py'
        if not mod_path.exists():
            return "[board] SKIP - tools/board.py not found"
        spec = importlib.util.spec_from_file_location('_sessionstart_board', mod_path)
        if spec is None or spec.loader is None:
            return "[board] SKIP - could not load tools/board.py"
        board = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(board)
        if bp is None:
            bp = board.DEFAULT_BOARD
        if not Path(bp).exists():
            return ("[board] no board yet (notes/BOARD.md absent)\n"
                    "    create one: python tools/board.py sync")
        rows = board.open_questions(Path(bp))
    except Exception as exc:
        return f"[board] ERROR reading the board ({type(exc).__name__}: {exc})"

    if not rows:
        return "[board] 0 open questions on the board"
    lines = [f"[board] {len(rows)} OPEN QUESTION(S) ON THE BOARD <-- the owner has not answered these",
             "    they are waiting on the OWNER, not on you: do not block on them, work around them"]
    for r in rows[:6]:
        lines.append(f"    {r.get('id', '?')}: {str(r.get('question', ''))[:110]}")
    if len(rows) > 6:
        lines.append(f"    ... and {len(rows) - 6} more (python tools/board.py open)")
    return '\n'.join(lines)


def commentary_report(doc: Path | None = None, mark: Path | None = None) -> str:
    """Surface anything the owner has written to notes/COMMENTARY.md and not been shown yet.

    WHY IT IS HERE (owner, 2026-08-16): *"a box that I can write any commentary I'd like you to look
    at during a run without interrupting you... a hook on that that tells you that I've sent
    something to look at."* This is one of the two places that promise is kept; the other is
    data/hooks/staging/stop_hook.py, which fires at every turn boundary and therefore reaches an
    unattended overnight run mid-flight. Both read the SAME unread set, so a note surfaces once and
    a new one is never missed.

    IT IS MARKED READ HERE, because being injected into the session IS being shown -- the same
    advance-on-surface idiom the board and scan-out gates already use. Costs one small file read
    plus one json read (measured 0.32 ms), so it cannot push this hook toward its 10s budget.
    Never raises: a broken side channel must not block a session start."""
    import importlib.util
    try:
        mod_path = REPO / 'tools' / 'commentary.py'
        if not mod_path.exists():
            return "[commentary] SKIP - tools/commentary.py not found"
        spec = importlib.util.spec_from_file_location('_sessionstart_commentary', mod_path)
        if spec is None or spec.loader is None:
            return "[commentary] SKIP - could not load tools/commentary.py"
        commentary = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(commentary)
        rows = commentary.unread(doc, mark)
        if not rows:
            return "[commentary] no unread notes from the owner"
        text = commentary.report(doc, mark)
        commentary.mark_read(rows, doc, mark)
        return text
    except Exception as exc:
        return f"[commentary] ERROR reading the side channel ({type(exc).__name__}: {exc})"


def registry_report() -> str:
    """Report the newest registry-audit result + its age. Does NOT re-run the audit.

    capability_registry_audit.py takes >3 min (it walks the import graph), which is far too
    slow to block session start. It already persists each run to
    data/capability_registry_reports/registry-audit-<ts>.json -- so read the result and
    report staleness. Recomputing is the director's call, not the hook's.
    """
    import time
    rep_dir = REPO / 'data' / 'capability_registry_reports'
    if not rep_dir.is_dir():
        return ("[capability-registry] NO REPORTS DIR <-- ATTENTION\n"
                "    run: python tools/capability_registry_audit.py")
    reports = sorted(rep_dir.glob('registry-audit-*.json'))
    if not reports:
        return ("[capability-registry] NO AUDIT EVER RECORDED <-- ATTENTION\n"
                "    run: python tools/capability_registry_audit.py")
    newest = max(reports, key=lambda p: p.stat().st_mtime)
    age_h = (time.time() - newest.stat().st_mtime) / 3600.0
    try:
        data = json.loads(newest.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        return f"[capability-registry] report unreadable ({exc}); file={newest.name}"
    interesting = ('unregistered_hdlab_modules', 'islands', 'undecided',
                   'vet_pending', 'orphans', 'n_rows', 'total_rows')
    bits = [f'{k}={data[k] if not isinstance(data[k], list) else len(data[k])}'
            for k in interesting if k in data]
    flag = ' <-- STALE, re-run the audit' if age_h > 24 else ''
    return (f"[capability-registry] last audit {age_h:.1f}h ago{flag}\n"
            f"    {newest.name}\n"
            f"    {'  '.join(bits) if bits else '(no summary keys matched)'}")


def main() -> int:
    blocks = [RULES, "== STATUS (single source of truth -- notes/STATUS.md) =="]
    blocks.append(status_summary())
    # In-process (no subprocess): the board parse is a single small file read, so it costs
    # milliseconds and cannot push this hook toward its 10s budget.
    blocks.append(board_report())
    # The owner's side channel. In-process like board_report above (one small file read), and
    # placed immediately after it because the two answer the same question -- "has the owner said
    # anything to me" -- and reading one without the other is how a note goes unanswered.
    blocks.append(commentary_report())
    blocks.append(probe('status-freshness-guard', 'status_freshness_check.py'))
    # Sits directly under WHAT IS RUNNING because it CORRECTS that section. A pid file is
    # written once at startup and never touched again, so nothing on disk distinguished
    # "still running" from "finished hours ago" from "crashed in 16 seconds" -- on 2026-08-16
    # all 39 scratch/*.pid pointed at dead processes while briefs described three of them as
    # live runs not to disturb. Reads pid files + one ctypes liveness call each (~1s measured,
    # no subprocess, no console-window flash); it never rescans data/, so it stays inside the
    # hook budget. Bounded output: header plus at most 6 alarm lines.
    blocks.append(probe('pid-reconcile', 'pid_reconcile.py', '--hook'))
    blocks.append("== DURABILITY GATE (status read at session start) ==")
    blocks.append(registry_report())
    blocks.append(probe('director-kb-freshness', 'director_kb_freshness_check.py'))
    # --hook reads the newest PERSISTED join report (0.6s); it never rescans, because a full
    # scan walks 7885 data dirs and takes ~290s. Same split as registry_report() above: the
    # expensive computation is a separate deliberate act, the hook only reports its staleness.
    blocks.append(probe('result-index-join', 'result_index_join.py', '--hook'))
    # --hook reads the newest PERSISTED verdict-bar report (<1s); it never rescans, because a
    # full recompute walks 7,769 metrics.json. Same split as registry_report() and
    # result-index-join above: the expensive computation is a deliberate act
    # (`python tools/verdict_bar_check.py --scan`), the hook only reports its result + staleness.
    # WHY IT IS IN THE HOOK AT ALL: a cell's verdict STRING can say PASS while its claim does
    # not survive the standing bar, and the string is what every triage tool keys on. That is
    # only useful if someone SEES the count without remembering to ask for it.
    blocks.append(probe('verdict-bar', 'verdict_bar_check.py', '--hook'))
    # progress_snapshot.py --hook: full derive (fast -- no recursive data/ walk, one bounded
    # git log call, ~1s measured) that rewrites notes/PROGRESS_SNAPSHOT.md every session and
    # prints only its headline here. This IS the "periodic without a cron" mechanism for the
    # owner-facing snapshot: the hook is proven to fire every session, unlike three prior
    # mechanisms that went silently disabled (11 hd_* tasks 12 days, KB ingest 6 days,
    # hd_session_watchdog writing 1585 unread ping files).
    blocks.append(probe('progress-snapshot', 'progress_snapshot.py', '--hook'))
    blocks.append(
        "== ORIENT ==\n"
        "  notes/STATUS.md (read this FIRST -- cheap, current, sourced; <=6KB by design)\n"
        "  notes/SUBSTRATE_CHARTER_read_first.md (rules + current frontier)\n"
        "  notes/WHERE_WE_ARE_NOW.md (live state)  |  notes/THE_PLAN.md (the plan)\n"
        "  Search prior work: python tools/director_kb_query.py --help"
    )
    print(json.dumps({'additionalContext': '\n\n'.join(blocks)}))
    return 0


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(_self_test())
    sys.exit(main())
