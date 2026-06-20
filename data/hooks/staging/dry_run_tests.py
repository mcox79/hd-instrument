#!/usr/bin/env python3
"""Dry-run-proof of Stop+StopFailure hook safety guards (Python rewrite; no jq).

Per Skunkworks: "verify the property, don't assert it -- like kill-restart resume tests".
Per Orchestrator: "verify-the-referent on these 3 guards in the design review BEFORE any
USER-auth register -- runaway Stop hook across 5 sessions is the worst failure mode".

Test scenarios (LOAD-BEARING marked):
  T1 LOAD-BEARING: stop_hook_active=true -> exit 0 (loop prevention)
  T2: continuation cap reached -> exit 0 (runaway prevention)
  T3: no concrete signal -> exit 0 + counter NOT incremented
  T4: pending unread inbox -> emits decision=block + counter +1
  T5: cap-exact-boundary (N-1 blocks; N exits)

  F1: non-retryable -> exit 0; no retry; counter reset
  F2: retryable -> emits decision=retry; counter +1
  F3: retry-cap exhausted -> exit 0; counter reset
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
STOP_HOOK = HOOK_DIR / 'stop_hook.py'
FAIL_HOOK = HOOK_DIR / 'stop_failure_hook.py'
REPO_ROOT = HOOK_DIR.parent.parent.parent

TS = 'testbed_dryrun'   # test session label

# Hook state files (live in real data/ paths; we clean up after)
REAL_HOOK_STATE = REPO_ROOT / 'data' / 'hook_state'
REAL_FAIL_STATE = REPO_ROOT / 'data' / 'api_failures'
CONT_FILE = REAL_HOOK_STATE / f'stop_continuations_{TS}'
TS_FILE = REPO_ROOT / 'data' / f'last_processed_{TS}.timestamp'
ATTEMPT_FILE = REAL_FAIL_STATE / f'{TS}.attempt'
LOG_FILE = REAL_FAIL_STATE / f'{TS}.jsonl'


def run_hook(hook, stdin_json, session, env_overrides=None):
    """Invoke hook with controlled stdin/args; return (stdout, returncode)."""
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    try:
        proc = subprocess.run(
            [sys.executable, str(hook), session],
            input=stdin_json,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        return proc.stdout, proc.returncode
    except subprocess.TimeoutExpired:
        return '', 99


def cleanup():
    for p in (CONT_FILE, TS_FILE, ATTEMPT_FILE, LOG_FILE):
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass


def check(name, ok):
    mark = 'PASS' if ok else 'FAIL'
    print(f'  [{mark}] {name}')
    return ok


def main() -> int:
    cleanup()
    REAL_HOOK_STATE.mkdir(parents=True, exist_ok=True)
    REAL_FAIL_STATE.mkdir(parents=True, exist_ok=True)

    results = []
    print('=' * 78)
    print('Stop hook + StopFailure hook dry-run-proof (Python; no jq dependency)')
    print('=' * 78)

    # === T1 LOAD-BEARING: stop_hook_active=true ===
    print()
    print('T1 LOAD-BEARING: stop_hook_active=true -> exit 0 (loop prevention)')
    stdout, rc = run_hook(STOP_HOOK, '{"stop_hook_active":true}', TS)
    results.append(check('T1 exit=0', rc == 0))
    results.append(check('T1 no decision JSON emitted', '"decision"' not in stdout))

    # === T2: cap reached ===
    print()
    print('T2: continuation cap reached -> exit 0 (HARD_CAP runaway prevention)')
    CONT_FILE.write_text('10')   # at default cap
    TS_FILE.touch()  # set to now so no unread
    stdout, rc = run_hook(STOP_HOOK, '{}', TS)
    results.append(check('T2 exit=0 (at cap; no block)', rc == 0 and '"decision"' not in stdout))

    # === T3: no concrete signal ===
    print()
    print('T3: no concrete signal -> exit 0 + counter NOT incremented')
    CONT_FILE.write_text('0')
    TS_FILE.touch()  # now; no notes newer
    stdout, rc = run_hook(STOP_HOOK, '{}', TS)
    results.append(check('T3 exit=0 + no decision', rc == 0 and '"decision"' not in stdout))
    count_after = int(CONT_FILE.read_text().strip()) if CONT_FILE.exists() else -1
    results.append(check(f'T3 counter NOT incremented (count={count_after})', count_after == 0))

    # === T4: pending unread inbox -> block ===
    print()
    print('T4: pending unread inbox -> emits decision=block + counter +1')
    CONT_FILE.write_text('0')
    # Set timestamp to long-ago via os.utime (avoid touch -t Windows quirk)
    long_ago = time.time() - 86400  # 1 day ago
    os.utime(TS_FILE, (long_ago, long_ago))
    # Create test note newer than timestamp
    test_note = REPO_ROOT / 'notes' / f'test_dryrun_to_{TS}_2026-06-20.md'
    test_note.write_text('test note for dry-run')
    stdout, rc = run_hook(STOP_HOOK, '{}', TS)
    results.append(check('T4 emits decision=block', '"decision": "block"' in stdout or '"decision":"block"' in stdout))
    results.append(check('T4 exit=0', rc == 0))
    count_after = int(CONT_FILE.read_text().strip()) if CONT_FILE.exists() else -1
    results.append(check(f'T4 counter incremented to 1 (count={count_after})', count_after == 1))
    test_note.unlink(missing_ok=True)

    # === T5: cap-exact-boundary ===
    print()
    print('T5: cap-exact-boundary (N-1 blocks; N exits)')
    test_note.write_text('test note')
    os.utime(TS_FILE, (long_ago, long_ago))
    hard_cap = 10
    CONT_FILE.write_text(str(hard_cap - 1))  # one below cap
    stdout, rc = run_hook(STOP_HOOK, '{}', TS)
    results.append(check('T5a at cap-1 blocks (still has budget)',
                         '"decision": "block"' in stdout or '"decision":"block"' in stdout))
    count_after = int(CONT_FILE.read_text().strip()) if CONT_FILE.exists() else -1
    results.append(check(f'T5a counter incremented to cap N={hard_cap} (count={count_after})',
                         count_after == hard_cap))
    stdout, rc = run_hook(STOP_HOOK, '{}', TS)
    results.append(check('T5b at cap exits 0 (cap-guard fires)',
                         rc == 0 and '"decision"' not in stdout))
    test_note.unlink(missing_ok=True)

    cleanup()

    print()
    print('=' * 78)
    print('StopFailure hook tests')
    print('=' * 78)

    # === F1: non-retryable ===
    print()
    print('F1: non-retryable (authentication_error) -> no retry; counter reset')
    err_json = '{"error":{"type":"authentication_error","message":"invalid","status":401}}'
    stdout, rc = run_hook(FAIL_HOOK, err_json, TS)
    results.append(check('F1 exit=0 + no retry decision',
                         rc == 0 and '"decision": "retry"' not in stdout and '"decision":"retry"' not in stdout))

    # === F2: retryable (529 overloaded) -> retry + counter increments ===
    print()
    print('F2: retryable (529 overloaded) -> emits decision=retry; counter +1')
    if ATTEMPT_FILE.exists():
        ATTEMPT_FILE.unlink()
    err_json = '{"error":{"type":"overloaded_error","message":"server overloaded","status":529}}'
    stdout, rc = run_hook(FAIL_HOOK, err_json, TS)
    results.append(check('F2 emits decision=retry',
                         '"decision": "retry"' in stdout or '"decision":"retry"' in stdout))
    count_after = int(ATTEMPT_FILE.read_text().strip()) if ATTEMPT_FILE.exists() else -1
    results.append(check(f'F2 attempt counter incremented to 1 (count={count_after})',
                         count_after == 1))

    # === F3: retry-cap exhausted -> exit 0; counter reset ===
    print()
    print('F3: retry-cap exhausted -> exit 0; counter file removed (reset)')
    ATTEMPT_FILE.write_text('5')  # at MAX_RETRIES default
    err_json = '{"error":{"type":"overloaded_error","status":529}}'
    stdout, rc = run_hook(FAIL_HOOK, err_json, TS)
    results.append(check('F3 exit=0 + no retry decision',
                         rc == 0 and '"decision": "retry"' not in stdout and '"decision":"retry"' not in stdout))
    results.append(check('F3 attempt counter file removed (reset)', not ATTEMPT_FILE.exists()))

    cleanup()

    print()
    print('=' * 78)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f'RESULTS: {passed} PASS / {total - passed} FAIL')
    print('=' * 78)
    if passed == total:
        print('ALL GUARDS DRY-RUN-PROVED. Ready for USER+Orchestrator design review.')
        return 0
    else:
        print('FAILURES DETECTED. NOT ready for register.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
