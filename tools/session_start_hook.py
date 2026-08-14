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
    return (
        f"[STATUS.md] {as_of_line}\n"
        f"    age: {age_days:.2f} days{age_flag}\n"
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

    # Sanity: the REAL STATUS.md (read-only here, never written) must NOT trigger either banner.
    out = status_summary(STATUS_MD)
    if 'MISSING REQUIRED LITERAL' not in out:
        print("[self-test] PASS: the real notes/STATUS.md parses clean (no false-positive banner)")
    else:
        print(f"[self-test] FAIL: the real notes/STATUS.md incorrectly triggered a banner:\n{out}")
        ok = False

    print(f"[self-test] {'ALL PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


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
    blocks.append(probe('status-freshness-guard', 'status_freshness_check.py'))
    blocks.append("== DURABILITY GATE (status read at session start) ==")
    blocks.append(registry_report())
    blocks.append(probe('director-kb-freshness', 'director_kb_freshness_check.py'))
    # --hook reads the newest PERSISTED join report (0.6s); it never rescans, because a full
    # scan walks 7885 data dirs and takes ~290s. Same split as registry_report() above: the
    # expensive computation is a separate deliberate act, the hook only reports its staleness.
    blocks.append(probe('result-index-join', 'result_index_join.py', '--hook'))
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
