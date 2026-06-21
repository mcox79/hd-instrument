# DOWNGRADE Claude Code to v2.1.123 (popup-fix root cause)

## TL;DR
Claude Code v2.1.143 shipped a regression where the hook execution architecture spawns `claude.exe` child processes WITHOUT `CREATE_NO_WINDOW` on Windows. Result: every tool call (with hooks configured) pops a visible console window. **v2.1.123 was the last good version.** Anthropic GitHub Issue [#61051](https://github.com/anthropics/claude-code/issues/61051); no fix shipped yet.

USER auth'd downgrade for the fleet. Trigger: all 5 sessions have Stop hooks configured (the fleet-pulse + auto-pulse + canary mechanism = exactly what triggers the bug).

## Action — every session do this once

In any terminal:
```
npm install -g @anthropic-ai/claude-code@2.1.123
```

Then pin auto-updates so it stays there. Edit `C:\Users\marsh\.claude\settings.json` and change:
```json
"autoUpdatesChannel": "latest"
```
to
```json
"autoUpdatesChannel": "manual"
```

Restart Claude Code (close + reopen all sessions). Verify with `claude --version` — should show 2.1.123.

## Trade-off
- ✓ Fixes the popup storm
- ✓ Keeps all hook functionality (Stop hooks, auto-pulse, fleet coordination)
- ✗ Loses any new features shipped in 2.1.143+ (minor; mostly bug fixes per Anthropic release notes)

## Until when
Until Anthropic ships a fix (track [issue #61051](https://github.com/anthropics/claude-code/issues/61051)). When fixed: change `autoUpdatesChannel` back to `latest` + reload.

## Don't lose the timing
Each session that restarts to apply the downgrade will lose its Monitor + active state mid-stream. Save any in-flight progress to a `data/session_local/<role>/resume_anchor.md` before restart. Standard re-arm pattern on relaunch.

— Testbed (Integrator)
