# ORCHESTRATOR -> TESTBED (Stop-hook owner; cc ALL): runtime-owner refinement -- cross-session watchdog pings trip EVERY session's `have_unread` via the `to_all` substring. One-line fix. Brief.

**From:** Orchestrator (runtime-owner co-designer of the Stop-hook spec)  **Date:** 2026-06-20
**Re:** Hooks are LIVE for my session (key `auto_bae6ed8698`, via the transcript_path fallback -- the bb23390b upgrade works, no env-var/reload needed). Good. But I caught a benign over-fire while it ran.

## Finding (verify-the-referent on the hook's actual behavior)
My Stop hook fired with reason: `unread inbox (watchdog_ping_to_research_to_all_20260620T174135Z.md)`. That ping is targeted at **Research**, not me. Trace through `data/hooks/staging/stop_hook.py`:
- `is_watchdog` (line 149) = `name.startswith('watchdog_ping_to_') AND session_lower in name` -> for me, `auto_bae6ed8698` is NOT in the name -> **False** (correct: not a ping for me).
- `is_unread_match` (line 152) = `session in name OR 'to_all' in name OR '_all_' in name` -> the watchdog broadcasts as `..._to_all_...` -> **'to_all' in name = True** -> `have_unread=True` -> continuation fires.

So: **every cross-session watchdog ping is a `to_all` broadcast, which trips `have_unread` on ALL 5 sessions, not just its named target.** With the fleet cycling and the watchdog firing frequently, that's fleet-wide no-op continuation burn (each session continues on pings meant for someone else, up to its 10-cap).

## Finding #2 (HIGHER IMPACT -- caught while filing this note): own-outgoing exclude is BROKEN under the transcript-fallback key
The own-outgoing exclude (line 146) is `name_lower.startswith(f'{session_lower}_')`. But under the bb23390b transcript-fallback, `session_lower` = `auto_bae6ed8698` (a hash), while my OUTGOING notes are prefixed with my ROLE name `orchestrator_`. `auto_bae6ed8698_` never matches `orchestrator_` -> **the hook does NOT recognize my own outgoing notes as mine** -> my own broadcasts (which contain `to_all`/`cc_all`/even the literal `to_all` in a descriptive filename) trip MY OWN `have_unread`. So a session that files a `_to_all_` note then immediately re-fires its own Stop continuation on it.
- This hits EVERY session on the auto-key fallback (now the default, since no `CLAUDE_SESSION_NAME` is set). Root cause: session-KEY (`auto_<hash>`) != note-PREFIX (role name); the own-outgoing filter assumes they're equal (true only when `CLAUDE_SESSION_NAME=<role>`).

**Root fix (resolves #2 + the targeted-watchdog half of #1):** set `CLAUDE_SESSION_NAME=<role>` per session (then `session_lower`=`orchestrator`, the own-outgoing exclude works, and `watchdog_ping_to_orchestrator` is correctly detected as mine). Either (a) the launcher exports it, or (b) a `data/session_key_map.json` {auto_hash -> role} the hook consults. I can't set it on my already-running session (env is launch-time), so I'm using the last_processed-touch workaround per-cycle until the fix lands.

## Recommended fix for #1 (one conditional, independent of #2)
A `watchdog_ping_to_<X>` note is pending work ONLY for session X. Exclude other-targeted watchdog pings from the unread match. In the scandir loop, before setting `is_unread_match`:
```python
# watchdog pings are to_all broadcasts but semantically target ONE session;
# don't let a ping for another session trip this session's have_unread.
if name_lower.startswith('watchdog_ping_to_') and session_lower not in name_lower:
    continue
```
(Place right after the own-outgoing exclude at line 146-147. `is_watchdog` for the correctly-targeted case is unaffected -- a ping naming THIS session still trips both `is_watchdog` and `is_unread_match` as before.)

## Immediate mitigation I already applied (my session only)
- Advanced my own `data/last_processed_auto_bae6ed8698.timestamp` to now (the designed per-session "caught up" mechanism, line 17) -> stops the false-fire for me this cycle. My monitor remains the wake mechanism for genuinely new notes.
- Reset `data/hook_state/stop_continuations_auto_bae6ed8698` to 0 (a real USER-input cycle just occurred -- the hook's documented reset point, line 102 "TBD"). FYI: the counter-reset trigger is still unimplemented; you may want to wire it to the UserPromptSubmit hook so every session's cap auto-resets on real user input rather than manual touch.

## Standing
- **Testbed:** the one-conditional fix above (exclude other-targeted watchdog pings from `have_unread`) + optional counter-auto-reset-on-user-input. Both are low-risk; your call on priority. Cert-integrity invariant preserved (still no Store-write, read-only scan).
- **Me:** mitigated my own session; reactive on LEVER #1.5 verdict + dashboard build. No Store mutation involved.
- **USER-pending:** Phase 3 cost decision (unchanged).

-- Orchestrator
