"""Check whether the Claude Code Windows console-popup regression is fixed yet.

Run: python tools/check_claude_code_popup_fix.py

What it checks:
1. Local Claude Code version (currently pinned at 2.1.123 to dodge the regression)
2. Latest npm-published version (any newer release available?)
3. Status of GitHub issue #61051 (closed? has staff comment? linked PR?)

What it prints:
- Current status summary
- Suggested action (stay pinned vs. upgrade-and-test)

Designed to be popup-safe — uses urllib (in-process) + subprocess with CREATE_NO_WINDOW for the npm/claude version calls.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

ISSUE_URL = "https://api.github.com/repos/anthropics/claude-code/issues/61051"
NPM_REGISTRY = "https://registry.npmjs.org/@anthropic-ai/claude-code"
KNOWN_BROKEN = "2.1.143"
KNOWN_GOOD = "2.1.123"


def run_silent(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout"


def fetch_json(url: str, timeout: int = 15) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "popup-fix-checker/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        print(f"  ! fetch failed: {e}")
        return None


def main() -> int:
    print("=" * 60)
    print("Claude Code popup-regression fix-status check")
    print("=" * 60)

    # 1. Local version
    print("\n[1/3] Local Claude Code version:")
    rc, out = run_silent(["claude", "--version"])
    local_version = out.split()[0] if rc == 0 else "unknown"
    print(f"  installed: {local_version}")
    print(f"  known-broken: {KNOWN_BROKEN} (popup regression)")
    print(f"  known-good:  {KNOWN_GOOD} (current pin)")

    # 2. Latest npm version
    print("\n[2/3] Latest npm-published version:")
    npm_data = fetch_json(NPM_REGISTRY)
    if not npm_data:
        latest_version = "?"
    else:
        latest_version = npm_data.get("dist-tags", {}).get("latest", "?")
        print(f"  latest on npm: {latest_version}")
        stable_version = npm_data.get("dist-tags", {}).get("stable")
        if stable_version:
            print(f"  stable channel: {stable_version}")

    # 3. Issue status
    print("\n[3/3] GitHub issue #61051 status:")
    issue = fetch_json(ISSUE_URL)
    if not issue:
        issue_state = "?"
    else:
        issue_state = issue.get("state", "?")
        title = issue.get("title", "")
        comments = issue.get("comments", 0)
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        closed_at = issue.get("closed_at")
        pull_request = issue.get("pull_request")
        print(f"  title: {title[:80]}")
        print(f"  state: {issue_state}")
        print(f"  comments: {comments}")
        print(f"  labels: {', '.join(labels)}")
        if closed_at:
            print(f"  closed_at: {closed_at}")
        if pull_request:
            print(f"  linked PR: {pull_request.get('html_url', '?')}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    if issue_state == "closed":
        print("Issue is CLOSED.")
        print(f"  -> Probably fixed in some version <= {latest_version}.")
        print(f"  -> Verify by upgrading + manually testing for popups:")
        print(f"       npm install -g @anthropic-ai/claude-code@latest")
        print(f"     Then close + reopen Claude Code, watch for popups.")
        print(f"  -> If fixed, revert pins in ~/.claude/settings.json:")
        print(f"       autoUpdatesChannel: 'latest'  (remove minimumVersion)")
    elif local_version == KNOWN_GOOD:
        print("Stay pinned. Issue still open; no fix shipped.")
        print(f"  -> Local Claude Code is on known-good {KNOWN_GOOD}.")
        print(f"  -> Next: re-run this check periodically (weekly).")
    elif local_version == KNOWN_BROKEN or local_version.startswith("2.1.14"):
        print("WARNING: local version may have the popup regression.")
        print(f"  -> Downgrade: npm install -g @anthropic-ai/claude-code@{KNOWN_GOOD}")
    else:
        print(f"Local version {local_version} is neither known-good nor known-broken.")
        print(f"  -> Test manually — close Claude Code, reopen, watch for popups.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
