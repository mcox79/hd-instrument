# TESTBED -> ALL: blocker ping #166 reply. CLEAR.

**Status:** CLEAR. Stretch: popup root-cause SOLVED (Claude Code v2.1.143 regression Anthropic issue #61051; hook-architecture missing CREATE_NO_WINDOW). Downgraded global Claude Code to 2.1.123; pinned `autoUpdatesChannel: stable` + `minimumVersion: 2.1.123` in user settings. **All 5 sessions must close+reopen to pick up the fixed binary** — running processes still have v2.1.143 in memory. Status-check tool at `tools/check_claude_code_popup_fix.py` for future upgrade decision. Dashboard fix (parsers.py str() coerce) + 3D auto-refresh + cron task launcher all uncommitted pending USER batch-commit.

-- Testbed (Integrator)
