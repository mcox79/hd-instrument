# LIVE HOOK REGISTRATION -- TRACKED REFERENCE COPY

**Why this file exists.** The hooks that actually fire for this project are registered in
`D:\AI\.claude\settings.json`. **`D:\AI` IS NOT A GIT REPOSITORY** (verified 2026-08-18:
`git rev-parse --show-toplevel` -> `fatal: not a git repository`). So that file is **completely
unversioned**: if it is lost, edited, or replaced, every hook silently stops firing and **nothing
reports the loss**.

That is not hypothetical. On 2026-08-17 the Stop hook was registered ONLY in
`D:\AI\hd-instrument\.claude\settings.json` -- a SUBDIRECTORY, which Claude Code does not load as
project settings, because the session's project root is `D:\AI`. **The hook therefore never ran at
all.** The canary registered alongside it last fired **2026-08-13**. Diagnosing that cost hours,
and the only reason it was caught is that the canary is a two-line file append with no logic that
can fail -- so its silence was unambiguous.

**This file is a REFERENCE COPY, not the live file.** Editing it changes nothing. To restore, copy
the JSON below back to `D:\AI\.claude\settings.json` and start a new session (settings load at
session start).

## The three registrations, and what each is for

- **`SessionStart`** -> `tools/session_start_hook.py`. Injects the non-negotiables, the last
  capability-registry audit, and a live director-KB freshness check on every start/clear/compact.
- **`PostToolUse`** (matcher `Agent`) -> `tools/agent_dispatch_stop_hook.py`. Enforces YIELD AFTER
  DISPATCH.
- **`Stop`** -> `data/hooks/staging/stop_hook.py` **plus a canary**. The canary is deliberate: it is
  the only thing that can distinguish "the hook ran and chose not to block" from "the hook never
  ran". **Keep it.** Its output goes to `data/hook_state/_canary.txt`.

**Disarm the loop at any time, from anywhere, with one command:**
`python tools/autoloop.py disarm`

## Verified state as of 2026-08-18

- Stop hook self-test: **OVERALL PASS**, all five gates.
- Autoloop: **ARMED**, cap 200.
- GUARD 1D narrowed by owner ruling to halt on `permission-rule` and `user-rejected` only;
  `cancelled` teardowns are logged and do **not** halt.
- GUARD 1 reworked so an armed loop can continue past `stop_hook_active`, bounded by the
  continuation cap **and** a 20-second wall-clock floor between continuations.

## The live JSON

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "D:/AI/hd-instrument/.venv/Scripts/python.exe D:/AI/hd-instrument/tools/session_start_hook.py",
            "timeout": 60
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "command",
            "command": "C:/Users/marsh/AppData/Local/Programs/Python/Python312/python.exe -S -E D:/AI/hd-instrument/tools/agent_dispatch_stop_hook.py agent",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "D:/AI/hd-instrument/.venv/Scripts/python.exe D:/AI/hd-instrument/data/hooks/staging/stop_hook.py",
            "timeout": 15
          },
          {
            "type": "command",
            "command": "D:/AI/hd-instrument/.venv/Scripts/python.exe -c \"import time,os; os.makedirs('D:/AI/hd-instrument/data/hook_state', exist_ok=True); open('D:/AI/hd-instrument/data/hook_state/_canary.txt','a').write(f'{time.strftime(\\\"%Y-%m-%dT%H:%M:%SZ\\\", time.gmtime())} canary fired pid={os.getpid()} scope=D-AI-root\\n')\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## How to check the loop is actually alive

Do NOT infer it from the hook's own log -- that file is written even when the hook decides not to
block, and it was also written by direct invocations during debugging. **Check the canary:**

```bash
tail -3 D:/AI/hd-instrument/data/hook_state/_canary.txt
```

A recent timestamp means stop events are reaching the registration. **A stale timestamp means the
registration is not being loaded, no matter how green the hook's own self-test is** -- that is
exactly the state this project sat in from 2026-08-13 to 2026-08-18 without noticing.

## 2026-08-18 -- THE PROTECTIVE DENY RULES WERE NOT LOADING, AND NOBODY NOTICED

`hd-instrument/.claude/settings.json` carried 24 deny rules protecting `preregs/**` and
`arm_key*`. **They were never in force.** That file is a SUBDIRECTORY settings file, and the
session's project root is `D:\AI` -- the same reason the Stop hook silently never fired between
2026-08-13 and 2026-08-18. **The rules read as protection in code review and did nothing at
runtime.**

**How it was caught, and it was luck:** a subagent was asked to write a pre-registration and
SUCCEEDED. `Write(preregs/**)` should have blocked it. The success was the evidence.

**Fix applied:** all 24 rules copied into `D:/AI/.claude/settings.json`, which does load. Backup of
the prior state at `D:/AI/.claude/settings.json.bak_before_deny_merge`. **They take effect at the
NEXT session start** -- settings load at session start, so this session still runs unprotected.

**The general rule this is the third instance of: a control that lives in an unloaded file is not a
control, and nothing reports its absence.** Same class as the 11 scheduled tasks disabled for 12
days and the KB ingest disabled for 6. Verify enforcement by OBSERVING A DENIAL, never by reading
the rule.
