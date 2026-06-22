"""One-shot dry-run: compare pre-patch vs post-patch inbox-seed sizes per session.

Pre-patch logic = the prior _recent_inbox_for behavior (substring _<session>_ + _all_,
no age filter, no deprecated-pattern filter). Post-patch logic = current
_recent_inbox_for in hd_session_watchdog.

Prints per-session counts + a few sample-drop reasons. Used to verify the patch
produces zero false-positives on the current notes/ snapshot.
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import hd_session_watchdog as wd  # noqa: E402


NOTES_DIR = REPO_ROOT / 'notes'
SESSIONS = wd.SESSIONS


def pre_patch_inbox(session: str, max_items: int = 5) -> list:
    """Reproduces the PRIOR _recent_inbox_for behavior (no age + no deprecated filter +
    loose _<session>_ substring + _all_ broadcast token)."""
    candidates = []
    sess_lower = session.lower()
    own_prefix = f'{sess_lower}_'
    with os.scandir(NOTES_DIR) as it:
        for entry in it:
            if not entry.name.endswith('.md'):
                continue
            name_lower = entry.name.lower()
            if name_lower.startswith(own_prefix):
                continue
            if name_lower.startswith('watchdog_ping_to_'):
                continue
            addressed = (f'_to_{sess_lower}_' in name_lower
                         or f'_{sess_lower}_' in name_lower
                         or '_to_all_' in name_lower
                         or '_all_' in name_lower)
            if not addressed:
                continue
            try:
                mtime = entry.stat().st_mtime
            except OSError:
                continue
            candidates.append((mtime, entry.name))
    candidates.sort(reverse=True)
    return [name for (_, name) in candidates[:max_items]]


def main() -> int:
    now = time.time()
    print(f'Dry-run comparison (now = {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}; '
          f'24h floor = {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - wd.INBOX_MAX_AGE_SEC))})')
    print(f'notes dir: {NOTES_DIR}')
    print()
    total_before = 0
    total_after = 0
    for sess in SESSIONS:
        before = pre_patch_inbox(sess, max_items=5)
        after = wd._recent_inbox_for(sess, max_items=5, now=now)
        total_before += len(before)
        total_after += len(after)
        dropped = [n for n in before if n not in set(after)]
        print(f'=== {sess} ===')
        print(f'  pre-patch  ({len(before)}): {before}')
        print(f'  post-patch ({len(after)}): {after}')
        if dropped:
            print(f'  dropped    ({len(dropped)}):')
            for d in dropped:
                # Categorize drop reason
                reasons = []
                d_lower = d.lower()
                for p in wd.INBOX_DEPRECATED_PATTERNS:
                    if p.search(d_lower):
                        reasons.append(f'deprecated-pattern[{p.pattern}]')
                        break
                try:
                    mtime = (NOTES_DIR / d).stat().st_mtime
                    age_h = (now - mtime) / 3600.0
                    if mtime < now - wd.INBOX_MAX_AGE_SEC:
                        reasons.append(f'>24h-old ({age_h:.1f}h)')
                except OSError:
                    pass
                # Loose substring-only match? Check if explicit-addressed
                if (f'_to_{sess.lower()}_' not in d_lower
                        and '_to_all_' not in d_lower
                        and '_cc_all_' not in d_lower):
                    reasons.append('loose-substring-only (not explicitly addressed)')
                if not reasons:
                    reasons.append('unknown')
                print(f'    - {d}  [{"; ".join(reasons)}]')
        print()
    print(f'TOTALS: pre-patch={total_before}  post-patch={total_after}  reduction={total_before - total_after}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
