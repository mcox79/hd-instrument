#!/usr/bin/env python3
"""Register this Claude Code session as a named role in data/session_key_map.json.

Usage: python tools/register_session.py <role>
  role: testbed | research | exp_dev | orchestrator | skunkworks

Reads the most recent stop_hook invocation_log line attributed to the running
Claude Code process (matched by pid; falls back to the most recent line if pid
not present) and learns the auto_<hash> session key from the timing window.
Writes/updates data/session_key_map.json with {auto_<hash>: <role>}.

This is for the on-demand activation path: each session runs it once after the
hook fix lands. With CLAUDE_SESSION_NAME set in the launcher, this is unnecessary.
"""
import json
import os
import sys
from pathlib import Path


VALID_ROLES = {'testbed', 'research', 'exp_dev', 'orchestrator', 'skunkworks'}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description='Register a Claude Code session role -> auto_<hash> mapping.')
    ap.add_argument('role', help=f'one of: {sorted(VALID_ROLES)}')
    ap.add_argument('--hash', dest='hash_arg', default=None,
                    help='Explicit auto_<hex> key (copy from your Stop hook output: '
                         '"Pending work for auto_XXX"). Bypasses timestamp inference; '
                         'recommended when other sessions are firing concurrently.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Show what would be written without modifying session_key_map.json.')
    args = ap.parse_args()
    role = args.role.strip().lower()
    if role not in VALID_ROLES:
        print(f'invalid role {role!r}; must be one of {sorted(VALID_ROLES)}', file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parent.parent

    # Resolve auto_<hash> key:
    #   1. --hash explicit (safest; copy-paste from Stop hook output)
    #   2. fallback: most-recently-touched data/last_processed_auto_*.timestamp (racy)
    if args.hash_arg:
        h = args.hash_arg.strip()
        if not h.startswith('auto_'):
            print(f'--hash must look like auto_<hex>, got {h!r}', file=sys.stderr)
            return 2
        auto_key = h
    else:
        log_file = repo_root / 'data' / 'hook_state' / '_invocation_log.txt'
        if not log_file.exists():
            print(f'no invocation log at {log_file}; has the hook fired yet for this session?',
                  file=sys.stderr)
            return 1
        candidates = []
        ts_dir = repo_root / 'data'
        for f in ts_dir.glob('last_processed_auto_*.timestamp'):
            try:
                mtime = f.stat().st_mtime
            except OSError:
                continue
            key = f.stem.replace('last_processed_', '')
            candidates.append((mtime, key))
        if not candidates:
            print('no auto_<hash> timestamps found; has the hook fired yet?', file=sys.stderr)
            return 1
        candidates.sort(reverse=True)
        auto_key = candidates[0][1]
        print(f'INFO: timestamp inference picked {auto_key} (most-recently-touched). '
              f'If wrong, re-run with --hash <auto_XXX> from your Stop hook output.',
              file=sys.stderr)

    map_file = repo_root / 'data' / 'session_key_map.json'
    if map_file.exists():
        try:
            with map_file.open('r', encoding='utf-8') as f:
                key_map = json.load(f)
        except (json.JSONDecodeError, OSError):
            key_map = {}
    else:
        key_map = {}

    prev = key_map.get(auto_key)
    if prev and prev != role:
        print(f'WARN: {auto_key} was {prev}, now claiming {role}', file=sys.stderr)
        if not args.hash_arg:
            print(f'  HINT: timestamp inference likely picked the wrong key. Confirm via '
                  f'your Stop hook output ("Pending work for auto_XXX") and re-run with '
                  f'--hash <auto_XXX> to override safely.', file=sys.stderr)

    if args.dry_run:
        print(f'DRY-RUN: would register {auto_key} -> {role} (previous: {prev!r})')
        return 0

    key_map[auto_key] = role
    tmp = map_file.with_suffix('.json.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(key_map, f, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(tmp, map_file)
    print(f'registered: {auto_key} -> {role}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
