#!/usr/bin/env python3
"""Stop hook (Python rewrite; no jq dependency). REGISTERED AND LIVE -- see REGISTRATION below.

Per Director hardening proposal + Orchestrator runtime-owner spec + Skunkworks cert-integrity
input.

Purpose: prevent idle-one-by-one deaths by continuing the session when concrete work is pending.

REGISTRATION (corrected 2026-08-15; the previous line here read "STAGING ONLY -- not yet
registered", which had been FALSE for some time. It is exactly the stale coupling doc that causes
incidents in this repo, so it is now stated with its evidence):
  - `D:/AI/hd-instrument/.claude/settings.json`  -> hooks.Stop[0], timeout 10   (PROJECT scope)
  - `C:/Users/marsh/.claude/settings.json`       -> hooks.Stop[0], no timeout   (USER scope)
  THIS FILE IS THEREFORE REGISTERED TWICE AND FIRES TWICE PER STOP EVENT. That is a
  misconfiguration, not a design: see _should_count_this_fire() for the narrow mitigation applied
  to GUARD 2's counter, and notes/BOARD_AND_LOOP_README.md for the real fix (remove the USER-scope
  copy, which also wrongly applies this repo's hook to every other project on the machine).

CRITICAL safety guards (load-bearing per Orchestrator + documented ~50min Stop-hook loop bug):
  GUARD 1: stop_hook_active flag honored FIRST (loop prevention; THE load-bearing safety gate)
  GUARD 1D: DENIAL HARD-FAIL (2026-08-15). A denied tool call ENDS the loop. It is filed to
            notes/BOARD.md as a question and never routed around. Background subagents auto-deny
            anything not pre-allowed and then continue silently, which turns an unattended run
            into silently-skipped steps rather than a clean halt; this gate is what makes the
            halt clean. See _denial_gate().
  GUARD 2: continuation counter, cap CONFIGURABLE via tools/autoloop.py (per-session).
           The cap may be set to UNLIMITED (the owner's explicit 2026-08-15 choice). It is a
           VISIBLE SETTING, never a deleted guard: every block reason prints "continuation N/M"
           or "continuation N/unlimited", so an uncapped run announces itself on every turn.
  GUARD 3: Concrete signal gate (only block on real pending work; not "always block")
           3a unread inbox   3b uncollected scan-out fragment   3c single-dispatch turn
           3d AUTOLOOP (2026-08-15): re-read the plan from disk, update it, and continue.
              Fires ONLY when tools/autoloop.py reports ARMED. Default is DISARMED.

DISARM, ONE STEP:  python tools/autoloop.py disarm

Skunkworks cert-integrity invariant: this hook does NOT trigger Store-writes. Auto-continue
does NOT race the NULL-seam hazard.

Coexistence with v5 notes_monitor.sh: uses per-session `data/last_processed_<session>.timestamp`
the monitor does NOT touch -> no race.

Usage: stop_hook.py <session>
  stdin: hook input JSON (Claude Code hook protocol)
  stdout: hook decision JSON (only if blocking) OR nothing
  exit code: always 0 (per hook protocol expectation; decision is in stdout JSON)
  stop_hook.py --self-test   runs every gate self-test, including an END-TO-END subprocess run
                             of this hook against throwaway state. Arms nothing.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def _testbed_waiting_cycle_hint(repo_root: Path) -> str:
    """For testbed role only: if > 60min since last waiting-on-cycle round was fired,
    return '[WAITING-CYCLE-DUE: file next round per USER hourly protocol]'.
    Best-effort silent on errors. Cooldown via data/hook_state/waiting_cycle_last_fired_ts."""
    cooldown_file = repo_root / 'data' / 'hook_state' / 'waiting_cycle_last_fired_ts'
    try:
        if cooldown_file.exists():
            last_fired = float(cooldown_file.read_text().strip())
            if (time.time() - last_fired) < 3000:  # 50 min suppress
                return ''
    except (OSError, ValueError):
        pass
    return '[WAITING-CYCLE-DUE: file next waiting-on cycle round per USER hourly protocol]'


def _testbed_active_pulse(repo_root: Path) -> str:
    """For the testbed role only: run an active dashboard pulse on EVERY Stop fire
    and embed rich state in the block reason. Replaces the prior 'hint only when
    triggered' pattern -- the data is ALWAYS surfaced so I can't drift into
    standing-without-checking. Cooldown only suppresses the recommend-to-fire
    action, not the pulse data itself.

    Returns a single line like:
      [FLEET: agg=WARN | research(22m) exp_dev(35m STALE) skunkworks(active) orchestrator(active) | drift: 0 RED | ACTION: fire probe R12 narrowed to research+exp_dev]

    Silent only on dashboard-unreachable (no false-alarm).
    """
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen('http://localhost:8765/api/dashboard/v2/health', timeout=3) as r:
            data = json.loads(r.read().decode('utf-8'))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return '[PULSE-DASHBOARD-DOWN]'  # not silent -- I should know if dashboard is down

    agg = (data.get('aggregate') or {}).get('status', '?')
    fleet = (data.get('project_health') or {}).get('fleet') or {}
    red_drifts = [d.get('name', '?') for d in data.get('drift_detectors', []) if d.get('status') == 'RED']

    # Per-session age summary; mark stale (>15m)
    fleet_summary = []
    stale = []
    for role in ('research', 'exp_dev', 'skunkworks', 'orchestrator'):
        s = fleet.get(role, {})
        age = s.get('latest_substantive_note_age_s')
        if not isinstance(age, (int, float)):
            fleet_summary.append(f'{role}(?)')
            continue
        m = int(age / 60)
        if m > 15:
            fleet_summary.append(f'{role}({m}m STALE)')
            stale.append((role, m))
        else:
            fleet_summary.append(f'{role}({m}m)')

    # Cooldown check for lull-probe action recommendation
    lull_cd = repo_root / 'data' / 'hook_state' / 'lull_probe_last_fired_ts'
    lull_action_due = False
    if len(stale) >= 2:
        try:
            if lull_cd.exists():
                last = float(lull_cd.read_text().strip())
                if (time.time() - last) >= 2700:  # 45 min
                    lull_action_due = True
            else:
                lull_action_due = True
        except (OSError, ValueError):
            lull_action_due = True

    # Cycle-due check
    cycle_cd = repo_root / 'data' / 'hook_state' / 'waiting_cycle_last_fired_ts'
    cycle_action_due = False
    try:
        if cycle_cd.exists():
            last = float(cycle_cd.read_text().strip())
            if (time.time() - last) >= 3000:  # 50 min
                cycle_action_due = True
        else:
            cycle_action_due = True
    except (OSError, ValueError):
        cycle_action_due = True

    actions = []
    if lull_action_due and len(stale) >= 2:
        narrow = sorted(stale, key=lambda x: -x[1])
        narrow_desc = '+'.join(r for r, _ in narrow[:4])
        actions.append(f'fire LULL probe (narrow_to_{narrow_desc})')
    if cycle_action_due:
        if stale:
            narrow = sorted(stale, key=lambda x: -x[1])
            narrow_desc = '+'.join(r for r, _ in narrow[:4])
            actions.append(f'fire CYCLE round (narrow_to_{narrow_desc})')
        else:
            actions.append('fire CYCLE round (4/4 active; broad ok)')
    if red_drifts:
        actions.append(f'investigate RED drift: {",".join(red_drifts)}')

    action_str = ' | '.join(actions) if actions else 'pulse-only (no action due)'
    red_str = f'{len(red_drifts)} RED ({",".join(red_drifts)})' if red_drifts else '0 RED'
    return f"[FLEET: agg={agg} | {' '.join(fleet_summary)} | drift: {red_str} | ACTION: {action_str}]"


def _testbed_lull_check_hint(repo_root: Path) -> str:
    """DEPRECATED: kept for compatibility; replaced by _testbed_active_pulse.
    Returns '' always; _testbed_active_pulse now embeds lull state + action
    recommendation directly into the hook's block reason."""
    return ''


def _scan_out_gate(repo_root: Path, session: str) -> tuple:
    """New signal (2026-08-14, owner directive on subagent fan-out): uncollected
    `.claude/scan-out/` fragments from the fire-and-forget scan-agent convention
    (see `.claude/scan-out/README.md`, `tools/scan_out_collect.py`, `.claude/agents/scan.md`).

    FRAGMENT COUNT IS THE GATE, and zero is the mandatory early exit. A scan that is still
    running in the background has written nothing yet -- an empty (or absent) scan-out
    directory must NEVER look like a block-worthy signal. That is precisely the "hook that
    won't let you stop" failure the owner's directive warns about: "with scans truly
    fire-and-forget, your main session may legitimately want to end a turn before they land
    ... gate the Stop hook on fragment count, as in that early exit 0."

    Only a fragment that has ALREADY been written (the scan finished) AND is newer than this
    session's last-collected mark can trigger a block -- mirrors the unread-inbox pattern
    above (own file, first-run-is-not-a-backlog, advance-on-block) rather than inventing a
    new idiom.

    Returns (should_block: bool, fragment_name: str | None).
    """
    scan_out_dir = repo_root / '.claude' / 'scan-out'
    if not scan_out_dir.is_dir():
        return False, None  # early exit 0: no scan-out dir at all == nothing to gate on

    try:
        fragments = list(scan_out_dir.glob('*.json'))
    except OSError:
        return False, None
    if not fragments:
        return False, None  # early exit 0: scans legitimately in flight have written nothing yet

    ts_file = repo_root / 'data' / f'last_scan_collected_{session}.timestamp'
    if not ts_file.exists():
        # First-run: pre-existing fragments are not a fresh backlog for THIS session --
        # matches the unread-inbox first-run behavior (avoid retroactively blocking on
        # history the session never saw appear).
        try:
            ts_file.touch()
        except OSError:
            pass
        return False, None
    try:
        ts_mtime = ts_file.stat().st_mtime
    except OSError:
        return False, None

    newest_name = None
    newest_mtime = ts_mtime
    for p in fragments:
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if m > newest_mtime:
            newest_mtime = m
            newest_name = p.name
    if newest_name is None:
        return False, None
    return True, newest_name


def _single_dispatch_turn_gate(repo_root: Path, session: str) -> tuple:
    """New signal (2026-08-15, owner directive on parallel-dispatch enforcement -- see
    notes/agent_usage_practices_audit_2026-08-14.md,
    which measured 0/235 Agent-tool-use messages in an audited transcript ever batched more than
    ONE Agent call). tools/agent_dispatch_stop_hook.py's PostToolUse/Agent hook increments
    data/hook_state/agent_dispatch_turn_count_<session>.txt on every MAIN-THREAD Agent dispatch
    (agent_type null -- subagent-originated Agent calls are filtered out there, not here). This
    function reads that counter at the turn boundary (a Stop-hook fire IS the turn boundary --
    see the calling site's reset-after-read, mirroring the unread-inbox / scan-out advance-on-
    block pattern already used above) and fires ONLY when the turn dispatched EXACTLY ONE
    main-thread Agent call while the ready-work queue (tools/dispatch_queue.py,
    data/dispatch_queue.jsonl) still holds unclaimed items -- i.e. concurrency capacity was
    available and not used.

    Deliberately narrow: count==0 (no dispatch this turn) and count>=2 (already batching) both
    return no-block. This is not a general nag-to-parallelize hook; it fires only on the exact
    single-dispatch-while-work-remains pattern the owner asked to detect.

    Returns (should_block: bool, message: str | None).
    """
    counter_file = repo_root / 'data' / 'hook_state' / f'agent_dispatch_turn_count_{session}.txt'
    try:
        count = int(counter_file.read_text().strip()) if counter_file.exists() else 0
    except (ValueError, OSError):
        count = 0
    if count != 1:
        return False, None

    queue_file = repo_root / 'data' / 'dispatch_queue.jsonl'
    if not queue_file.is_dir() and not queue_file.exists():
        return False, None  # queue not seeded yet -- nothing to recommend
    unclaimed = []
    try:
        with queue_file.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    it = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if it.get('status') == 'unclaimed':
                    unclaimed.append(it)
    except OSError:
        return False, None
    if not unclaimed:
        return False, None

    examples = unclaimed[:3]
    example_str = "; ".join(f"{it.get('id', '?')} ({it.get('category', '?')})" for it in examples)
    msg = (f"single-dispatch turn while {len(unclaimed)} ready-work item(s) remain unclaimed in "
           f"data/dispatch_queue.jsonl, e.g. {example_str} -- consider "
           f"`python tools/dispatch_batch.py --count K --by <name>` to batch K of them into "
           f"ONE message next time (budget: up to 5 concurrent)")
    return True, msg


def _reset_dispatch_turn_counter(repo_root: Path, session: str) -> None:
    """Zero the single-dispatch-turn counter at the Stop-hook turn boundary, whether or not
    _single_dispatch_turn_gate fired -- mirrors the ts_file.touch() advance-on-block pattern:
    this Stop-hook cycle IS the turn for counting purposes, so the next Agent dispatch starts a
    fresh count. GUARD 1 (stop_hook_active) returns before this runs, so a forced continuation
    keeps accumulating into the SAME count rather than resetting mid-continuation -- see this
    function's caller for why that is deliberate, not an oversight."""
    counter_file = repo_root / 'data' / 'hook_state' / f'agent_dispatch_turn_count_{session}.txt'
    try:
        if counter_file.exists():
            counter_file.write_text('0')
    except OSError:
        pass


def _single_dispatch_turn_gate_self_test() -> int:
    """Prove _single_dispatch_turn_gate fires ONLY on count==1 AND unclaimed>0, and that
    _reset_dispatch_turn_counter zeroes the counter regardless of which branch fired. Runs
    against a tempfile root -- never touches the real repo's hook_state or dispatch_queue."""
    import tempfile
    ok = True
    root = Path(tempfile.mkdtemp(prefix="stop_hook_single_dispatch_selftest_"))
    (root / 'data' / 'hook_state').mkdir(parents=True, exist_ok=True)
    session = 'selftest_session'
    counter_file = root / 'data' / 'hook_state' / f'agent_dispatch_turn_count_{session}.txt'
    queue_file = root / 'data' / 'dispatch_queue.jsonl'

    # 1. No queue file at all -- must not block regardless of count.
    counter_file.write_text('1')
    should_block, msg = _single_dispatch_turn_gate(root, session)
    if should_block is False and msg is None:
        print("[self-test] PASS no queue file -> no block even at count==1")
    else:
        print(f"[self-test] FAIL no queue file should not block, got ({should_block!r}, {msg!r})", file=sys.stderr)
        ok = False

    # 2. Queue exists, all items done/claimed (none unclaimed) -- must not block.
    queue_file.write_text(json.dumps({"id": "x1", "status": "claimed", "category": "c"}) + "\n"
                           + json.dumps({"id": "x2", "status": "done", "category": "c"}) + "\n",
                           encoding='utf-8')
    should_block, msg = _single_dispatch_turn_gate(root, session)
    if should_block is False:
        print("[self-test] PASS queue with zero unclaimed items -> no block")
    else:
        print(f"[self-test] FAIL should not block with zero unclaimed, got ({should_block!r}, {msg!r})", file=sys.stderr)
        ok = False

    # 3. Queue has unclaimed items, count==1 -- MUST block, naming an example.
    queue_file.write_text(json.dumps({"id": "y1", "status": "unclaimed", "category": "organ-missing"}) + "\n",
                           encoding='utf-8')
    should_block, msg = _single_dispatch_turn_gate(root, session)
    if should_block is True and msg is not None and 'y1' in msg:
        print("[self-test] PASS count==1 + unclaimed items present -> blocks, names an example")
    else:
        print(f"[self-test] FAIL should block and name y1, got ({should_block!r}, {msg!r})", file=sys.stderr)
        ok = False

    # 4. Same queue state, but count==0 -- must NOT block (no dispatch happened this turn).
    counter_file.write_text('0')
    should_block, msg = _single_dispatch_turn_gate(root, session)
    if should_block is False:
        print("[self-test] PASS count==0 -> no block even with unclaimed items present")
    else:
        print(f"[self-test] FAIL count==0 should never block, got ({should_block!r}, {msg!r})", file=sys.stderr)
        ok = False

    # 5. Same queue state, count==2 (already batching) -- must NOT block.
    counter_file.write_text('2')
    should_block, msg = _single_dispatch_turn_gate(root, session)
    if should_block is False:
        print("[self-test] PASS count==2 (already batched) -> no block")
    else:
        print(f"[self-test] FAIL count==2 should not block, got ({should_block!r}, {msg!r})", file=sys.stderr)
        ok = False

    # 6. Reset zeroes the counter regardless of prior value.
    counter_file.write_text('7')
    _reset_dispatch_turn_counter(root, session)
    val = counter_file.read_text().strip()
    if val == '0':
        print("[self-test] PASS _reset_dispatch_turn_counter zeroes a nonzero counter")
    else:
        print(f"[self-test] FAIL counter after reset = {val!r}, expected '0'", file=sys.stderr)
        ok = False

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {root}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _denial_gate_self_test() -> int:
    """Prove GUARD 1D reads real transcript shape: top-level `toolDenialKind`, all three kinds,
    subagent files under <session>/subagents/, first-run-is-not-a-backlog, and no re-fire."""
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    root = Path(tempfile.mkdtemp(prefix="stop_hook_denial_selftest_"))
    (root / 'data' / 'hook_state').mkdir(parents=True, exist_ok=True)
    tdir = root / 'transcripts'
    tdir.mkdir(parents=True, exist_ok=True)
    tpath = tdir / 'sess.jsonl'
    session = 'selftest_denial'

    def rec(ts, kind=None, text='ordinary', sidechain=False):
        r = {"type": "user", "timestamp": ts, "isSidechain": sidechain,
             "message": {"content": [{"type": "tool_result", "content": text}]}}
        if kind:
            r["toolDenialKind"] = kind
        return json.dumps(r)

    tpath.write_text(
        rec('2026-08-15T10:00:00.000Z') + '\n' +
        rec('2026-08-15T10:01:00.000Z', 'permission-rule',
            'Permission to use Bash with command rm -f x has been denied.') + '\n',
        encoding='utf-8')

    out = _denial_gate(root, session, str(tpath))
    check(out == [], "first-ever check does NOT fire on pre-existing denials (not a backlog)")

    out = _denial_gate(root, session, str(tpath))
    check(out == [], "an unchanged transcript does not re-fire")

    with tpath.open('a', encoding='utf-8') as fh:
        fh.write(rec('2026-08-15T11:00:00.000Z', 'cancelled',
                     "The user doesn't want to take this action right now.") + '\n')
    out = _denial_gate(root, session, str(tpath))
    check(len(out) == 1 and out[0]['kind'] == 'cancelled',
          f"a NEW 'cancelled' denial fires (got {[d['kind'] for d in out]})")
    check(out and "doesn't want to take this action" in out[0]['text'],
          "the denial prose is recovered verbatim from the record")

    out = _denial_gate(root, session, str(tpath))
    check(out == [], "the same denial does not fire twice (mark advanced)")

    with tpath.open('a', encoding='utf-8') as fh:
        fh.write(rec('2026-08-15T12:00:00.000Z', 'user-rejected', 'nope') + '\n')
    out = _denial_gate(root, session, str(tpath))
    check(len(out) == 1 and out[0]['kind'] == 'user-rejected',
          "'user-rejected' fires too (all three kinds mean STOP)")

    # THE POINT OF THE GATE: a silent auto-deny inside a BACKGROUND SUBAGENT.
    sub = tdir / 'sess' / 'subagents'
    sub.mkdir(parents=True, exist_ok=True)
    (sub / 'agent-abc.jsonl').write_text(
        rec('2026-08-15T13:00:00.000Z', 'permission-rule',
            'Permission to use Write with file preregs/x.md has been denied.',
            sidechain=True) + '\n', encoding='utf-8')
    out = _denial_gate(root, session, str(tpath))
    check(len(out) == 1 and out[0]['sidechain'] is True,
          f"a denial inside a BACKGROUND SUBAGENT transcript fires (got {out})")
    check(out and out[0]['source'] == 'agent-abc.jsonl',
          "the firing fragment names the subagent transcript it came from")

    # Bounded read: a huge transcript must not be scanned whole.
    big = tdir / 'big.jsonl'
    filler = rec('2026-08-15T09:00:00.000Z', text='x' * 5000)
    with big.open('w', encoding='utf-8') as fh:
        for _ in range(2000):
            fh.write(filler + '\n')
        fh.write(rec('2026-08-15T14:00:00.000Z', 'permission-rule', 'late denial') + '\n')
    t0 = time.time()
    lines = _tail_lines(big, DENIAL_TAIL_BYTES, DENIAL_TAIL_LINES)
    dt = time.time() - t0
    check(len(lines) <= DENIAL_TAIL_LINES and dt < 2.0,
          f"_tail_lines is bounded ({len(lines)} lines, {dt*1000:.0f}ms on a "
          f"{big.stat().st_size/1e6:.1f}MB file)")
    check(any('late denial' in ln for ln in lines),
          "the tail read still catches the NEWEST record (reads from the end, not the start)")

    # A missing / empty transcript path must be a clean no-op, never a crash.
    check(_denial_gate(root, session, '') == [], "empty transcript_path is a clean no-op")
    check(_denial_gate(root, 'other', str(tdir / 'nope.jsonl')) == [],
          "a nonexistent transcript is a clean no-op")

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {root}")
    return 0 if ok else 1


def _end_to_end_self_test() -> int:
    """Run THIS FILE as a real subprocess against throwaway state and prove, from the outside,
    that GUARD 1 / GUARD 1D / GUARD 2 / GUARD 3 all still do what they claim.

    Arms nothing real: the loop state is redirected with HD_AUTOLOOP_STATE and the board with
    HD_BOARD_PATH, both to temp files. The only real-repo residue is a handful of
    data/hook_state/*_selftest_* bookkeeping files under a unique session name.
    """
    import subprocess
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="stop_hook_e2e_"))
    state = td / 'autoloop.json'
    board_md = td / 'BOARD.md'
    tpath = td / 'sess.jsonl'
    tpath.write_text('', encoding='utf-8')
    session = f'_selftest_e2e_{os.getpid()}'

    autoloop = _load_tool('autoloop')
    if autoloop is None:
        print("[self-test] FAIL tools/autoloop.py could not be loaded", file=sys.stderr)
        return 1

    def fire(stop_hook_active=False, transcript=None):
        env = dict(os.environ)
        env['CLAUDE_SESSION_NAME'] = session
        env['HD_AUTOLOOP_STATE'] = str(state)
        env['HD_BOARD_PATH'] = str(board_md)
        env['HD_STOP_DEDUPE_WINDOW_S'] = '0'
        env.pop('HD_STOP_HOOK_HARD_CAP', None)
        payload = {"stop_hook_active": stop_hook_active,
                   "transcript_path": str(transcript if transcript else tpath)}
        # env=env is LOAD-BEARING. Omitting it (caught 2026-08-15 by this suite failing) makes the
        # subprocess inherit the parent environment: the redirects are lost, the hook reads the
        # REAL autoloop state and the REAL board, and every assertion below passes vacuously
        # because a disarmed hook never blocks. A green test that proves nothing is worse than a
        # red one.
        p = subprocess.run([sys.executable, str(Path(__file__).resolve())], env=env,
                           input=json.dumps(payload), capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            print(f"[self-test] hook subprocess exit {p.returncode}; stderr:\n{p.stderr}",
                  file=sys.stderr)
        return p.stdout.strip()

    def blocked(out):
        if not out:
            return None
        try:
            return json.loads(out.splitlines()[-1])
        except (json.JSONDecodeError, ValueError):
            return None

    # --- baseline: DISARMED, no signals -> GUARD 3 must let the session stop ---
    autoloop.disarm(state)
    fire()                       # first fire also establishes this session's marks
    out = fire()
    check(out == "", f"GUARD 3 INTACT: disarmed + no concrete signal -> no block (got {out!r})")

    # --- ARMED -> GUARD 3d fires, with the plan-update instruction ---
    autoloop.arm(0, 'self-test', state)      # 0 == unlimited
    d = blocked(fire())
    check(d is not None and d.get('decision') == 'block', "ARMED -> the hook blocks")
    reason = (d or {}).get('reason', '')
    check('RE-READ FROM DISK' in reason, "the continuation prompt orders a RE-READ FROM DISK")
    for want in ('notes/STATUS.md', 'notes/BOARD.md', 'UPDATE THE PLAN IN PLACE'):
        check(want in reason, f"the continuation prompt names {want}")
    check('PLAN_NEXT_12H.md' in reason or 'PLAN.md' in reason,
          "the continuation prompt names the plan file that actually exists on disk")
    check('preregs' in reason and 'arm_key' in reason,
          "the continuation prompt states the prereg / arm-key prohibition")
    check('autoloop.py disarm' in reason, "every block reason carries the one-step disarm command")
    check('/unlimited)' in reason,
          f"an UNCAPPED run says so on every turn (GUARD 2 visible, not deleted)")

    # --- GUARD 1: stop_hook_active wins even while ARMED ---
    out = fire(stop_hook_active=True)
    check(out == "", f"GUARD 1 INTACT: stop_hook_active -> no block even while ARMED (got {out!r})")

    # --- GUARD 2: a finite cap still stops the loop ---
    session_capped = session + '_cap'
    autoloop.arm(2, 'self-test', state)
    saved, session = session, session_capped
    outs = [blocked(fire()), blocked(fire()), blocked(fire())]
    session = saved
    check(outs[0] is not None and outs[1] is not None and outs[2] is None,
          f"GUARD 2 INTACT: cap=2 blocks twice then stops (got {[bool(o) for o in outs]})")
    check(outs[0] and '(continuation 1/2)' in outs[0]['reason'],
          "the cap is printed in the block reason")

    # --- GUARD 1D: a denial ENDS the loop even while ARMED and uncapped ---
    autoloop.arm(0, 'self-test', state)
    session_d = session + '_den'
    saved, session = session, session_d
    fire()                                   # establish the denial mark (first run != backlog)
    tpath.write_text(json.dumps({
        "type": "user", "timestamp": "2099-01-01T00:00:00.000Z", "isSidechain": False,
        "toolDenialKind": "permission-rule",
        "message": {"content": [{"type": "tool_result",
                                 "content": "Permission to use Write with file preregs/x.md "
                                            "has been denied."}]}}) + '\n', encoding='utf-8')
    out = fire()
    session = saved
    check(out == "",
          f"GUARD 1D: a DENIED tool call stops the loop even while ARMED+uncapped (got {out!r})")
    check(board_md.exists(), "the denial was filed to the board")
    if board_md.exists():
        txt = board_md.read_text(encoding='utf-8')
        check('DENIED' in txt and 'permission-rule' in txt,
              "the filed board question names the denial and its kind")
        board = _load_tool('board')
        check(board is not None and board.count_open(board_md) >= 1,
              "the filed question counts as OPEN on the board")

    autoloop.disarm(state)
    print(f"[self-test] leftover temp dir (not auto-removed, by design): {td}")
    print(f"[self-test] real-repo residue: data/hook_state/*{session}* bookkeeping files only; "
          f"nothing armed.")
    return 0 if ok else 1


def _scan_out_gate_self_test() -> int:
    """Prove _scan_out_gate both ways: exits clean (False) when scans are legitimately in
    flight (no fragments written yet), and blocks (True) once a fragment has actually landed.
    Runs entirely against a tempfile root -- never touches the real repo's hook_state."""
    import tempfile
    ok = True

    root = Path(tempfile.mkdtemp(prefix="stop_hook_scan_gate_selftest_"))
    (root / 'data').mkdir(parents=True, exist_ok=True)
    session = 'selftest_session'

    # 1. No .claude/scan-out/ directory at all -- must be the early exit 0.
    should_block, name = _scan_out_gate(root, session)
    if should_block is False and name is None:
        print("[self-test] PASS no scan-out dir -> early exit 0 (no block)")
    else:
        print(f"[self-test] FAIL no scan-out dir should not block, got ({should_block!r}, {name!r})", file=sys.stderr)
        ok = False

    # 2. scan-out dir exists but empty -- scans "legitimately in flight" -- must not block.
    scan_out = root / '.claude' / 'scan-out'
    scan_out.mkdir(parents=True, exist_ok=True)
    should_block, name = _scan_out_gate(root, session)
    if should_block is False and name is None:
        print("[self-test] PASS empty scan-out dir (scans in flight) -> no block")
    else:
        print(f"[self-test] FAIL empty scan-out dir should not block, got ({should_block!r}, {name!r})", file=sys.stderr)
        ok = False

    # 3. First fragment appears -- first-ever check for this session must NOT retroactively
    #    block (matches unread-inbox first-run behavior); it should establish the mark instead.
    frag1 = scan_out / 'probe_scan_1.json'
    frag1.write_text('{"agent": "scan", "task": "t", "timestamp": "x", "findings": []}', encoding='utf-8')
    should_block, name = _scan_out_gate(root, session)
    if should_block is False:
        print("[self-test] PASS pre-existing fragment on first check -> no retroactive block")
    else:
        print(f"[self-test] FAIL first check should not retroactively block, got ({should_block!r}, {name!r})", file=sys.stderr)
        ok = False

    # 4. A NEW fragment lands after the mark was set -- this is the real "blocks when it
    #    should" case: a completed scan sitting uncollected.
    import time as _t
    _t.sleep(0.05)
    ts_file = root / 'data' / f'last_scan_collected_{session}.timestamp'
    # nudge the mark slightly into the past relative to the next write, deterministically
    os.utime(ts_file, None)
    _t.sleep(0.05)
    frag2 = scan_out / 'probe_scan_2.json'
    frag2.write_text('{"agent": "scan", "task": "t2", "timestamp": "y", "findings": []}', encoding='utf-8')
    should_block, name = _scan_out_gate(root, session)
    if should_block is True and name == 'probe_scan_2.json':
        print("[self-test] PASS new completed fragment after the mark -> blocks, names the fragment")
    else:
        print(f"[self-test] FAIL new fragment should block and name itself, got ({should_block!r}, {name!r})", file=sys.stderr)
        ok = False

    # 5. Re-check immediately (no new fragment) -- must NOT block again until the mark is
    #    advanced (mirrors main()'s advance-on-block; this self-test does not call main(), so
    #    simulate the advance directly to prove the mark, once touched, silences the repeat).
    os.utime(ts_file, None)
    should_block, name = _scan_out_gate(root, session)
    if should_block is False:
        print("[self-test] PASS after mark is advanced, same fragments no longer block")
    else:
        print(f"[self-test] FAIL advancing the mark should silence repeat blocking, got ({should_block!r}, {name!r})", file=sys.stderr)
        ok = False

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {root}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ===========================================================================
# 2026-08-15 additions: repo-tool loading, the DENIAL HARD-FAIL gate (GUARD 1D),
# the AUTOLOOP signal (GUARD 3d), and the configurable cap for GUARD 2.
# ===========================================================================

def _repo_root() -> Path:
    """Script lives in data/hooks/staging/ -> repo root is four parents up."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _load_tool(module_name: str):
    """Import tools/<module_name>.py by absolute path. Returns the module, or None.

    NEVER RAISES. This hook runs under a bare system pythonw.exe (not the repo .venv) with no
    cwd guarantee, so a normal import would not find these. More importantly: a Stop hook that
    dies on an import error stops firing silently, which is the failure class this whole file
    exists to prevent. Every caller must handle None by falling back to pre-2026-08-15 behaviour.
    """
    import importlib.util
    try:
        p = _repo_root() / 'tools' / f'{module_name}.py'
        if not p.exists():
            return None
        spec = importlib.util.spec_from_file_location(f'_stophook_{module_name}', p)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


# --- GUARD 1D: denial hard-fail -------------------------------------------
# Transcript records carry a TOP-LEVEL `toolDenialKind` field with one of three values
# (verified 2026-08-15 by parsing the live transcript, not from documentation):
#   permission-rule | cancelled | user-rejected
# CLAUDE.md "Reading a denied tool call" documents that `cancelled` and `user-rejected` share
# identical user-visible prose and are separable ONLY by this field. ALL THREE mean STOP here:
#   permission-rule -> a rule fired; routing around it is the exact 2026-08-13 defect
#   cancelled       -> the owner pressed ESC; that is a stop request by definition
#   user-rejected   -> the owner said no
DENIAL_TAIL_BYTES = 4_000_000     # transcripts reach 3 GB here; this MUST be a seek, not a scan
DENIAL_TAIL_LINES = 800
DENIAL_MAX_SUBAGENT_FILES = 25


def _tail_lines(path: Path, max_bytes: int, max_lines: int) -> list:
    """Last complete JSONL lines of a file, bounded by BYTES then by LINES.

    Measured 2026-08-15: the live project transcript directory holds a 3,163,126,075-byte .jsonl.
    Reading it whole inside a 10s hook timeout is impossible, so this seeks to (size - max_bytes)
    and discards the first fragment (a partial line) whenever it did not start at byte 0.
    """
    try:
        size = path.stat().st_size
    except OSError:
        return []
    start = max(0, size - max_bytes)
    try:
        with path.open('rb') as fh:
            fh.seek(start)
            data = fh.read()
    except OSError:
        return []
    lines = data.decode('utf-8', errors='replace').split('\n')
    if start > 0 and lines:
        lines = lines[1:]
    return [ln for ln in lines if ln.strip()][-max_lines:]


def _denial_text(rec: dict) -> str:
    """Pull the human-visible denial prose out of a transcript record. Best-effort."""
    try:
        content = (rec.get('message') or {}).get('content')
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                c = item.get('content')
                if isinstance(c, str) and c.strip():
                    return c
                if isinstance(c, list):
                    for sub in c:
                        if isinstance(sub, dict) and isinstance(sub.get('text'), str):
                            return sub['text']
    except Exception:
        pass
    return '(denial text not recoverable from the transcript record)'


def _scan_denials(path: Path, since_ts: str) -> list:
    """Denial records in this file newer than since_ts (ISO-8601 strings sort correctly)."""
    out = []
    for ln in _tail_lines(path, DENIAL_TAIL_BYTES, DENIAL_TAIL_LINES):
        if 'toolDenialKind' not in ln:
            continue            # cheap substring prefilter before any json.loads
        try:
            rec = json.loads(ln)
        except (json.JSONDecodeError, ValueError):
            continue
        kind = rec.get('toolDenialKind')
        if not kind:
            continue
        ts = str(rec.get('timestamp') or '')
        if since_ts and ts <= since_ts:
            continue
        out.append({
            'timestamp': ts,
            'kind': str(kind),
            'text': _denial_text(rec)[:600],
            'source': path.name,
            'sidechain': bool(rec.get('isSidechain')),
        })
    return out


def _denial_gate(repo_root: Path, session: str, transcript_path: str) -> list:
    """Return NEW denials since this session's last check. Empty list on the first-ever check.

    Scans the session transcript AND its subagent transcripts. The subagent files are the point:
    verified 2026-08-15, subagent records live in `<session-uuid>/subagents/agent-*.jsonl`, NOT in
    the parent transcript (the parent contained 4508 records, every one isSidechain=false). A gate
    that read only the parent would miss precisely the silent background auto-denies it exists to
    catch.

    First-run is NOT a backlog -- same idiom as _scan_out_gate and the unread-inbox mark above.
    """
    if not transcript_path:
        return []
    try:
        tpath = Path(transcript_path)
    except (TypeError, ValueError):
        return []

    mark = repo_root / 'data' / 'hook_state' / f'last_denial_seen_{session}.txt'
    mark.parent.mkdir(parents=True, exist_ok=True)
    first_run = not mark.exists()
    since_ts = ''
    mark_mtime = 0.0
    if not first_run:
        try:
            since_ts = mark.read_text(encoding='utf-8').strip()
            mark_mtime = mark.stat().st_mtime
        except OSError:
            pass

    files = []
    if tpath.exists():
        files.append(tpath)
    sub_dir = tpath.with_suffix('') / 'subagents'
    if sub_dir.is_dir():
        try:
            subs = [(p.stat().st_mtime, p) for p in sub_dir.glob('*.jsonl')]
        except OSError:
            subs = []
        # Only files touched since the last check can hold a new denial. Bounded either way.
        subs = [(m, p) for m, p in subs if m >= mark_mtime - 1.0]
        subs.sort(key=lambda t: -t[0])
        files.extend(p for _m, p in subs[:DENIAL_MAX_SUBAGENT_FILES])

    found = []
    for f in files:
        found.extend(_scan_denials(f, since_ts))

    newest = since_ts
    for d in found:
        if d['timestamp'] > newest:
            newest = d['timestamp']
    try:
        mark.write_text(newest or time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
                        encoding='utf-8')
    except OSError:
        pass

    if first_run:
        return []           # pre-existing denials are history, not this session's backlog
    found.sort(key=lambda d: d['timestamp'])
    return found


def _record_denial_halt(repo_root: Path, session: str, denials: list, armed: bool) -> str:
    """Log every denial halt; file it to notes/BOARD.md when the loop is ARMED (unattended).

    Deliberately NOT filed when disarmed: a `cancelled` denial means the owner pressed ESC, and
    they are at the keyboard -- a board question would be noise. When ARMED, nobody is watching,
    so the board is the only channel that reaches them. Deduped so one recurring denial cannot
    flood the board.
    """
    import hashlib
    log = repo_root / 'data' / 'hook_state' / '_denial_halts.log'
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('a', encoding='utf-8') as fh:
            for d in denials:
                fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                         f"session={session} armed={armed} kind={d['kind']} "
                         f"sidechain={d['sidechain']} src={d['source']} "
                         f"ts={d['timestamp']} text={d['text'][:200]!r}\n")
    except OSError:
        pass

    if not armed:
        return 'logged (loop disarmed; not filed to the board)'

    board = _load_tool('board')
    if board is None:
        return 'logged (tools/board.py not loadable; NOT filed)'

    filed_keys = repo_root / 'data' / 'hook_state' / f'denial_filed_keys_{session}.txt'
    try:
        seen = set(filed_keys.read_text(encoding='utf-8').split()) if filed_keys.exists() else set()
    except OSError:
        seen = set()

    filed = 0
    for d in denials:
        key = hashlib.sha1((d['kind'] + '|' + d['text'][:160]).encode('utf-8')).hexdigest()[:16]
        if key in seen:
            continue
        where = 'a background subagent' if d['sidechain'] else 'the main session'
        try:
            board.ask(
                question=(f"A tool call was DENIED in {where} (kind: {d['kind']}). The overnight "
                          f"loop STOPPED rather than routing around it. Denial text: "
                          f"{d['text'][:300]}"),
                why=("Whatever step that call was part of did not happen. Per CLAUDE.md, a dropped "
                     "precondition invalidates the declared gate even when the result looks fine, "
                     "so nothing downstream of it should be trusted until you rule."),
                rec=("If this was an ESC interrupt (kind 'cancelled'), answer 'ignore' and re-arm. "
                     "If a permission rule fired (kind 'permission-rule'), the step needs either a "
                     "narrow allow-rule or a different approach -- say which."),
            )
            seen.add(key)
            filed += 1
        except Exception:
            pass
    try:
        filed_keys.write_text('\n'.join(sorted(seen)), encoding='utf-8')
    except OSError:
        pass
    return f'logged; {filed} filed to notes/BOARD.md'


def _should_count_this_fire(repo_root: Path, session: str, window_s: float = 2.0) -> bool:
    """MITIGATION, NOT A FIX, for the double registration documented at the top of this file.

    This hook is registered in BOTH the project and the user settings.json, so it fires twice per
    Stop event. Without this, GUARD 2's counter advances by 2 per turn and a cap of 10 silently
    behaves like a cap of 5. This suppresses the counter increment (only) for a second fire inside
    a short window. The correct fix is to remove the USER-scope registration -- see
    notes/BOARD_AND_LOOP_README.md. Returns True when this fire should count.
    """
    try:
        window_s = float(os.environ.get('HD_STOP_DEDUPE_WINDOW_S', window_s))
    except ValueError:
        pass
    f = repo_root / 'data' / 'hook_state' / f'last_stop_fire_{session}.txt'
    now = time.time()
    try:
        if f.exists() and window_s > 0:
            if now - float(f.read_text(encoding='utf-8').strip()) < window_s:
                return False
    except (OSError, ValueError):
        pass
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(str(now), encoding='utf-8')
    except OSError:
        pass
    return True


# --- GUARD 3d: the autoloop plan-update continuation -----------------------

def _plan_path(repo_root: Path) -> str:
    """The plan file, by either accepted name. Another agent may rename PLAN_NEXT_12H.md ->
    PLAN.md; both are valid and the prompt must name the one that actually exists."""
    for name in ('PLAN_NEXT_12H.md', 'PLAN.md'):
        if (repo_root / 'notes' / name).exists():
            return f'notes/{name}'
    return 'notes/PLAN_NEXT_12H.md (or notes/PLAN.md -- NEITHER EXISTS ON DISK, find the plan)'


def _autoloop_prompt(repo_root: Path) -> str:
    """The continuation instruction. NOTHING HERE MAY RELY ON CONVERSATION MEMORY -- after a
    compaction it is gone, which is the whole reason this text re-reads from disk by path."""
    plan = _plan_path(repo_root)
    board = _load_tool('board')
    n_open = board.count_open() if board is not None else 0
    open_note = (f"{n_open} question(s) are OPEN on the board and the owner has not answered them; "
                 f"do NOT block on them, work around them"
                 if n_open else "no open questions on the board")
    return (
        "AUTOLOOP IS ARMED. Do not end the turn. Do not rely on anything from earlier in this\n"
        "conversation -- after a compaction it is gone. RE-READ FROM DISK, IN THIS ORDER:\n"
        f"  1. {plan}   <- the plan\n"
        "  2. notes/STATUS.md          <- position, top item, what is running\n"
        f"  3. notes/BOARD.md           <- {open_note}\n"
        "THEN, IN THIS ORDER:\n"
        "  a. UPDATE THE PLAN IN PLACE to reflect what has actually landed since it was written\n"
        "     (edit the file; a plan you did not update is a plan you did not read).\n"
        "  b. RESUME WORK on its top unblocked item.\n"
        "  c. If an owner decision is blocking you, DO NOT STOP AND WAIT. File it and move on:\n"
        "     python tools/board.py ask \"<question>\" --why \"<what is blocked>\" "
        "--rec \"<your recommendation>\"\n"
        "  d. If a tool call is DENIED: STOP. Report the denial text verbatim. Do not retry a\n"
        "     variant and do not proceed without the denied step. This hook detects the denial\n"
        "     and ends the loop on its own; routing around it is the defect.\n"
        "NEVER edit preregs/** or any arm_key* file. Those are harness-denied for a reason: an\n"
        "agent that cannot stop eventually proposes adjusting the bands. Adjusting the bands is\n"
        "not a result. If the only move left is to weaken a gate, file it on the board instead.\n"
        "Owner stops this with: python tools/autoloop.py disarm"
    )


def _derive_session_from_transcript(transcript_path: str) -> str:
    """Derive a stable per-VS-Code-window session key from the Claude transcript path.

    Transcript paths are unique per Claude conversation. We hash to get a short stable key
    that survives session restarts but distinguishes different VS Code windows. This is the
    fallback when CLAUDE_SESSION_NAME env var isn't set (e.g. session launched without the
    launcher).
    """
    import hashlib
    h = hashlib.sha256(transcript_path.encode('utf-8')).hexdigest()[:10]
    return f'auto_{h}'


def main() -> int:
    # --self-test: run all gate self-tests and exit, before any stdin/hook-protocol handling
    # below (this is a maintenance entrypoint, not a hook firing).
    if len(sys.argv) >= 2 and sys.argv[1] == '--self-test':
        rcs = [
            ('scan-out gate (GUARD 3b)', _scan_out_gate_self_test()),
            ('single-dispatch gate (GUARD 3c)', _single_dispatch_turn_gate_self_test()),
            ('denial gate (GUARD 1D)', _denial_gate_self_test()),
            ('END-TO-END guards 1 / 1D / 2 / 3', _end_to_end_self_test()),
        ]
        print()
        for label, rc in rcs:
            print(f"[self-test] {'PASS' if rc == 0 else 'FAIL'}  {label}")
        overall = 0 if all(rc == 0 for _l, rc in rcs) else 1
        print("[self-test] OVERALL:", "PASS" if overall == 0 else "FAIL")
        return overall

    # DEBUG: prove invocation independent of all other logic (first thing; can't be missed)
    try:
        from pathlib import Path as _P
        debug_log = _P(__file__).resolve().parent.parent.parent.parent / 'data' / 'hook_state' / '_invocation_log.txt'
        debug_log.parent.mkdir(parents=True, exist_ok=True)
        import time as _t
        with debug_log.open('a', encoding='utf-8') as _df:
            _df.write(f"{_t.strftime('%Y-%m-%dT%H:%M:%SZ', _t.gmtime())} stop_hook invoked  argv={sys.argv[1:]} pid={os.getpid()}\n")
    except Exception:
        pass

    # Read stdin JSON FIRST (so we can fall back to transcript_path for session key)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            hook_input = {}
        else:
            hook_input = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        hook_input = {}

    # Session resolution priority:
    #   1. CLAUDE_SESSION_NAME env var (per-launcher; human-readable)
    #   2. Derived from transcript_path in hook input (per-VS-Code-window; auto-stable)
    #   3. Positional arg (manual override)
    #   4. None -> fail-safe no-op
    session = os.environ.get('CLAUDE_SESSION_NAME', '').strip()
    if not session:
        transcript_path = str(hook_input.get('transcript_path', '')).strip()
        if transcript_path:
            session = _derive_session_from_transcript(transcript_path)
    if not session and len(sys.argv) >= 2:
        session = sys.argv[1]
    if not session:
        return 0

    # Heartbeat-on-every-turn-end: if we can resolve a role, touch its heartbeat file so
    # the watchdog has a current liveness signal without needing to ping (eliminates the
    # self-stale-ping loop that wastes a turn just to touch a file). Done early + tolerant
    # of failures (the hook's decision logic continues regardless).
    repo_root_hb = Path(__file__).resolve().parent.parent.parent.parent
    key_map_file_hb = repo_root_hb / 'data' / 'session_key_map.json'
    role_for_hb = None
    if key_map_file_hb.exists():
        try:
            with key_map_file_hb.open('r', encoding='utf-8') as f:
                km_hb = json.load(f)
            v = km_hb.get(session)
            if isinstance(v, str) and v.strip():
                role_for_hb = v.strip()
        except (json.JSONDecodeError, OSError):
            pass
    if role_for_hb:
        try:
            hb_dir = repo_root_hb / 'data' / 'heartbeats'
            hb_dir.mkdir(parents=True, exist_ok=True)
            hb_file = hb_dir / f'{role_for_hb}.timestamp'
            hb_file.touch()
        except OSError:
            pass

    # Resolve the auto_<hash> key to a role name via data/session_key_map.json if mapped.
    # Without this, own-outgoing exclude breaks: session_lower='auto_abc...' never matches
    # the role-prefixed notes (e.g. 'orchestrator_to_...') the session itself emits ->
    # self-firing on own broadcasts. Map is owned by the launcher / user-bootstrap.
    repo_root_early = Path(__file__).resolve().parent.parent.parent.parent
    key_map_file = repo_root_early / 'data' / 'session_key_map.json'
    role_name = None
    if key_map_file.exists():
        try:
            with key_map_file.open('r', encoding='utf-8') as f:
                key_map = json.load(f)
            mapped = key_map.get(session)
            if isinstance(mapped, str) and mapped.strip():
                role_name = mapped.strip()
        except (json.JSONDecodeError, OSError):
            pass

    # === GUARD 1: stop_hook_active (THE load-bearing loop prevention) ===
    if bool(hook_input.get('stop_hook_active', False)):
        # Already in a Stop-hook-triggered continuation; never recurse.
        # UNCHANGED 2026-08-15 and deliberately so: it is the one guard that cannot be configured
        # away from here, and it runs BEFORE the denial gate and before any cap arithmetic.
        return 0

    # Script lives in data/hooks/staging/; repo root = ../../..
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    state_dir = repo_root / 'data' / 'hook_state'
    state_dir.mkdir(parents=True, exist_ok=True)
    cont_file = state_dir / f'stop_continuations_{session}'

    # Resolve the loop's arm state + cap once, from tools/autoloop.py. If that module cannot be
    # loaded, fall back EXACTLY to pre-2026-08-15 behaviour: disarmed, env-or-10 cap.
    _autoloop = _load_tool('autoloop')
    if _autoloop is not None:
        armed = _autoloop.is_armed()
        hard_cap = _autoloop.resolve_cap()          # int, or None for UNLIMITED
        cap_str = _autoloop.cap_label(hard_cap)
    else:
        armed = False
        hard_cap = int(os.environ.get('HD_STOP_HOOK_HARD_CAP', '10'))
        cap_str = str(hard_cap)

    # === GUARD 1D: DENIAL HARD-FAIL (2026-08-15) ===
    # A denied tool call ENDS the loop. Runs before the cap and before the signal gate so that no
    # signal, however concrete, can talk the session past a denial.
    try:
        _denials = _denial_gate(repo_root, session, str(hook_input.get('transcript_path', '')))
    except Exception:
        _denials = []           # a broken gate must never wedge the hook
    if _denials:
        try:
            _record_denial_halt(repo_root, session, _denials, armed)
        except Exception:
            pass
        try:
            cont_file.write_text('0')       # a halt is a clean cycle boundary
        except OSError:
            pass
        return 0                            # exit 0 with no decision == let the session STOP

    # === GUARD 2: continuation counter, CONFIGURABLE cap (runaway prevention) ===
    # The cap is now a visible setting (tools/autoloop.py; data/hook_state/autoloop.json) and may
    # be UNLIMITED at the owner's explicit choice. The guard itself is NOT removed: the counter
    # still runs, and cap_str is printed into every block reason, so an uncapped run says so on
    # every single turn instead of being invisible.
    try:
        count = int(cont_file.read_text().strip()) if cont_file.exists() else 0
    except (ValueError, OSError):
        count = 0

    if hard_cap is not None and count >= hard_cap:
        # Cap reached. Let session truly stop. (Counter reset on real-USER-input cycle TBD.)
        return 0

    # === GUARD 3: Concrete signal gate ===
    # 3a: Unread inbox newer than per-session last-processed timestamp
    notes_dir = repo_root / 'notes'
    ts_file = repo_root / 'data' / f'last_processed_{session}.timestamp'

    if not ts_file.exists():
        # First-run: set timestamp to NOW so existing notes don't all count as "unread".
        # Without this, the very first hook fire would see 6000+ notes as newer than the
        # (just-created) timestamp file, blocking the session repeatedly until cap.
        try:
            ts_file.touch()
        except OSError:
            pass
        # Use current time as ts_mtime so existing notes are "already processed".
        try:
            ts_mtime = ts_file.stat().st_mtime
        except OSError:
            import time as _t
            ts_mtime = _t.time()
    else:
        try:
            ts_mtime = ts_file.stat().st_mtime
        except OSError:
            ts_mtime = 0

    have_unread = False
    have_unread_name = None
    have_watchdog_ping = False
    have_watchdog_ping_name = None
    session_lower = session.lower()
    role_lower = role_name.lower() if role_name else None
    # Prefixes a note can start with that mean "I wrote this" -- exclude.
    own_prefixes = {f'{session_lower}_'}
    if role_lower:
        own_prefixes.add(f'{role_lower}_')
    # Tokens that mean "this is for me" in the v5 unread filter -- include.
    self_tokens = {session_lower}
    if role_lower:
        self_tokens.add(role_lower)
    if notes_dir.is_dir():
        # Single scandir pass for BOTH unread + watchdog-ping signals.
        # Uses os.scandir for fast DirEntry traversal (much faster than iterdir+stat on Windows
        # for ~6000+ note directories; DirEntry caches stat info from the directory entry).
        try:
            with os.scandir(notes_dir) as it:
                for entry in it:
                    if not entry.name.endswith('.md'):
                        continue
                    name_lower = entry.name.lower()
                    # Exclude own outgoing (under EITHER the hash key or the resolved role)
                    if any(name_lower.startswith(p) for p in own_prefixes):
                        continue
                    # FIX (Orchestrator finding #1, 2026-06-20): watchdog pings are filed as
                    # `watchdog_ping_to_<X>_to_all_*` -- the `to_all` substring would otherwise
                    # trip have_unread on EVERY session, not just the targeted one. Exclude
                    # other-targeted watchdog pings explicitly before the unread match.
                    if name_lower.startswith('watchdog_ping_to_'):
                        if not any(tok in name_lower for tok in self_tokens):
                            continue
                    # First: cheap watchdog-ping filter (highest signal)
                    is_watchdog = (name_lower.startswith('watchdog_ping_to_')
                                   and any(tok in name_lower for tok in self_tokens))
                    # Then: v5 unread filter
                    is_unread_match = (any(tok in name_lower for tok in self_tokens)
                                       or 'to_all' in name_lower
                                       or '_all_' in name_lower)
                    if not (is_watchdog or is_unread_match):
                        continue
                    # Only stat() if filename matched (much less stat traffic)
                    try:
                        mtime = entry.stat().st_mtime
                    except OSError:
                        continue
                    if mtime <= ts_mtime:
                        continue
                    if is_watchdog and not have_watchdog_ping:
                        have_watchdog_ping = True
                        have_watchdog_ping_name = entry.name
                    if is_unread_match and not have_unread:
                        have_unread = True
                        have_unread_name = entry.name
                    if have_unread and have_watchdog_ping:
                        break
        except OSError:
            pass

    # NOTE: removed recent-commit-activity gate -- it over-fires across sessions during
    # active commit cycles (any session's git commit triggers .git/index mtime).
    # The watchdog-ping signal is the more-targeted external wake-up trigger.

    # 3b: uncollected .claude/scan-out/ fragments (2026-08-14 fan-out fix). See
    # _scan_out_gate's docstring for the early-exit-0 rationale -- an empty/absent scan-out
    # dir (scans still in flight) must never reach here as a block signal.
    have_scan_fragment, scan_fragment_name = _scan_out_gate(repo_root, session)

    # 3c: single-dispatch-turn detector (2026-08-15 fan-out fix). See
    # _single_dispatch_turn_gate's docstring -- fires only when this turn dispatched exactly
    # one main-thread Agent call while the ready-work queue still holds unclaimed items.
    have_single_dispatch, single_dispatch_msg = _single_dispatch_turn_gate(repo_root, session)

    # 3d: AUTOLOOP (2026-08-15). The owner's standing overnight-autonomy directive. Fires ONLY
    # when tools/autoloop.py reports ARMED; DISARMED is the default and the fail-safe, so this
    # signal changes nothing at all until the loop is deliberately armed.
    have_autoloop = bool(armed)

    if have_unread or have_watchdog_ping or have_scan_fragment or have_single_dispatch \
            or have_autoloop:
        # Concrete signal: increment counter + emit block decision
        if _should_count_this_fire(repo_root, session):
            try:
                cont_file.write_text(str(count + 1))
            except OSError:
                pass
        else:
            count = count - 1   # second fire of a double registration; keep the reason honest
        # Advance last_processed to NOW so subsequent Stop fires don't re-block on the
        # SAME notes (the block itself surfaces them to the session as Stop hook feedback;
        # the session's continuation turn IS the response). Without this, the hook
        # re-blocks on the same unread note every cycle until cap, even though the
        # session already saw it.
        try:
            ts_file.touch()
        except OSError:
            pass
        signals = []
        if have_unread:
            signals.append(f"unread inbox ({have_unread_name})")
        if have_watchdog_ping:
            signals.append(f"watchdog ping ({have_watchdog_ping_name})")
        if have_scan_fragment:
            signals.append(f"scan fragment ready ({scan_fragment_name}) -- run "
                            f"`python tools/scan_out_collect.py`")
            # Advance this session's mark so the SAME fragment doesn't reblock every cycle
            # (mirrors ts_file.touch() below for the unread-inbox signal).
            try:
                (repo_root / 'data' / f'last_scan_collected_{session}.timestamp').touch()
            except OSError:
                pass
        if have_single_dispatch:
            signals.append(f"PARALLEL-DISPATCH: {single_dispatch_msg}")
        if have_autoloop and not signals:
            signals.append("autoloop armed (no other pending signal)")
        # Reset the dispatch-turn counter regardless of whether this signal itself fired --
        # this Stop-hook cycle is the turn boundary either way (see
        # _reset_dispatch_turn_counter's docstring for why GUARD 1 above makes this safe
        # against resetting mid-forced-continuation).
        _reset_dispatch_turn_counter(repo_root, session)
        reason = (f"Pending work for {session}: " + " + ".join(signals) +
                  f"; continuing. (continuation {count + 1}/{cap_str})")
        # Layer 1 of the lull-breaker enforcement (per USER 2026-06-21 + my own
        # protocol commit). For the testbed (audit) role only: query the dashboard
        # health endpoint + check if >= 2 OTHER sessions have substantive-note age
        # > 15 min. If so AND no probe was fired in the last 90 min, INJECT a
        # "LULL DETECTED" hint into the block reason. The hint becomes Stop hook
        # feedback text in the next turn -- mechanical, not memory-dependent.
        if role_for_hb == 'testbed':
            # Auto-execute pulse (replaces both prior hint helpers; ALWAYS runs +
            # embeds rich fleet data + action recommendation -- no reliance on me
            # remembering to check). Per USER 2026-06-21 #1 improvement.
            try:
                pulse = _testbed_active_pulse(repo_root_hb)
                if pulse:
                    reason = reason + " " + pulse
                # Self-test (#4): log success to debug file so any silent failure
                # of the helpers is visible within minutes (the lull-hint NameError
                # bug went undetected for hours because no self-test ran).
                try:
                    st_log = repo_root_hb / 'data' / 'hook_state' / '_hint_selftest.log'
                    st_log.parent.mkdir(parents=True, exist_ok=True)
                    with st_log.open('a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} OK pulse_len={len(pulse)}\n")
                except OSError:
                    pass
            except Exception as e:
                # Self-test (#4): record the failure so it's visible
                try:
                    st_log = repo_root_hb / 'data' / 'hook_state' / '_hint_selftest.log'
                    st_log.parent.mkdir(parents=True, exist_ok=True)
                    with st_log.open('a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} FAIL {type(e).__name__}: {str(e)[:100]}\n")
                except OSError:
                    pass
        # GUARD 3d body, appended LAST so it is the final thing the continuation turn reads.
        # Kept out of the " + ".join(signals) line above because it is multi-line instructions,
        # not a signal name.
        if have_autoloop:
            try:
                reason = reason + "\n\n" + _autoloop_prompt(repo_root)
            except Exception as e:
                reason = (reason + "\n\n[AUTOLOOP PROMPT FAILED TO BUILD: "
                          f"{type(e).__name__}: {str(e)[:120]} -- re-read notes/PLAN_NEXT_12H.md, "
                          "notes/STATUS.md and notes/BOARD.md from disk, update the plan, continue]")
        decision = {"decision": "block", "reason": reason}
        print(json.dumps(decision))
        return 0

    # No concrete signal: exit (true stop). Also RESET the continuation counter to 0 -- a
    # clean stop is the natural cycle boundary (equivalent to "session caught up + handed
    # back to USER"); the counter should fresh-start the next time work shows up. Without
    # this, the counter accumulates across DIFFERENT pings/notes during a long reactive
    # session and eventually hits cap on unrelated notes. (Written as "0" rather than
    # unlinked so the dry-run tests' count_after read remains valid.)
    try:
        if count != 0:
            cont_file.write_text('0')
    except OSError:
        pass
    # A true stop is also a turn boundary for the single-dispatch-turn counter -- reset it
    # here too (this branch is reached when count==1 but the queue happened to be empty, or
    # when count==0/2+ never entered the block above at all).
    _reset_dispatch_turn_counter(repo_root, session)
    return 0


if __name__ == '__main__':
    sys.exit(main())
