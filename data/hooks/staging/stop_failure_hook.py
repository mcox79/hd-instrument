#!/usr/bin/env python3
"""Phase 1.2 StopFailure hook (Python rewrite; no jq dependency).

Per Director hardening proposal. STAGING ONLY -- not yet registered.

Purpose: mitigate all-stop-at-once failures from Anthropic API transient overload (529) +
shared rate-limit contention. Exponential backoff + jitter + retry cap.

Per Orchestrator runtime-owner: hook does NOT trigger Store-writes; pure-decision logic.
Per Skunkworks: no cert-impact (infra).

Failure modes:
  - overloaded (HTTP 529): backoff base=30s; retry up to MAX_RETRIES
  - rate_limit (HTTP 429): backoff base=60s (longer); retry up to MAX_RETRIES
  - permission_denied / authentication_error / other: NO retry (give up immediately)

Backoff: base * 2^attempt + random[0..jitter_max] seconds
  attempt 0: 30 + 0..15 = 30-45s
  attempt 1: 60 + 0..15 = 60-75s
  attempt 2: 120 + 0..15 = 120-135s
  attempt 3: 240 + 0..15 = 240-255s
  attempt 4: 480 + 0..15 = 480-495s  (~8 min)
  total worst-case ~16 min before giving up

Usage: stop_failure_hook.py <session>
  stdin: error JSON
  stdout: retry decision JSON (only on retry) OR nothing
  exit: 0
"""
import json
import os
import random
import sys
import time
from pathlib import Path


def main() -> int:
    session = sys.argv[1] if len(sys.argv) >= 2 else 'unknown'

    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        hook_input = {}

    # Extract error class (best-effort; harness-format-dependent)
    err = hook_input.get('error', hook_input) if isinstance(hook_input, dict) else {}
    if not isinstance(err, dict):
        err = {}
    error_type = str(err.get('type', 'unknown'))
    error_msg = str(err.get('message', ''))
    try:
        http_status = int(err.get('status', 0))
    except (TypeError, ValueError):
        http_status = 0

    # Determine retry-eligible + base backoff
    retryable = False
    base_sec = 0
    et_lower = error_type.lower()
    if 'overloaded' in et_lower:
        retryable, base_sec = True, 30
    elif 'rate_limit' in et_lower or 'rate-limit' in et_lower:
        retryable, base_sec = True, 60
    elif http_status == 529:
        retryable, base_sec = True, 30
    elif http_status == 429:
        retryable, base_sec = True, 60

    max_retries = int(os.environ.get('HD_STOP_FAILURE_MAX_RETRIES', '5'))
    jitter_max = int(os.environ.get('HD_STOP_FAILURE_JITTER_MAX', '15'))

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    state_dir = repo_root / 'data' / 'api_failures'
    state_dir.mkdir(parents=True, exist_ok=True)
    log_file = state_dir / f'{session}.jsonl'
    attempt_file = state_dir / f'{session}.attempt'

    # Log the failure (best-effort)
    log_entry = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'session': session,
        'error_type': error_type,
        'message': error_msg,
        'http_status': http_status,
        'retryable': retryable,
    }
    try:
        with log_file.open('a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except OSError:
        pass

    if not retryable:
        # Non-retryable: reset attempt counter; exit (let harness surface).
        try:
            if attempt_file.exists():
                attempt_file.unlink()
        except OSError:
            pass
        return 0

    # Read current attempt counter
    try:
        attempt = int(attempt_file.read_text().strip()) if attempt_file.exists() else 0
    except (ValueError, OSError):
        attempt = 0

    if attempt >= max_retries:
        # Retry budget exhausted: reset counter; exit.
        try:
            if attempt_file.exists():
                attempt_file.unlink()
        except OSError:
            pass
        return 0

    # Compute backoff + jitter
    exp_sec = base_sec * (2 ** attempt)
    jitter = random.randint(0, jitter_max)
    wait_sec = exp_sec + jitter

    # Increment attempt counter
    try:
        attempt_file.write_text(str(attempt + 1))
    except OSError:
        pass

    # Emit retry decision
    reason = (f"{error_type} retry attempt {attempt + 1}/{max_retries}; "
              f"backoff {wait_sec}s (base {base_sec} + jitter {jitter})")
    decision = {"decision": "retry", "wait_sec": wait_sec, "reason": reason}
    print(json.dumps(decision))
    return 0


if __name__ == '__main__':
    sys.exit(main())
