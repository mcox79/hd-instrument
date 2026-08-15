# The overnight loop and the decision board

Two things: a **loop** that keeps a session working without you, and a **board** where it asks you
things while you are asleep.

---

## STOP IT NOW

```
python tools/autoloop.py disarm
```

That is the whole thing. It takes effect on the very next turn boundary; nothing is queued.

If you cannot run a command: open `data/hook_state/autoloop.json` in any editor, change
`"armed": true` to `"armed": false`, save. Done.

If that file is missing, corrupt, truncated, or holds anything at all other than exactly
`"armed": true`, the loop is **OFF**. Off is the fail-safe direction, so half-saving the file in a
text editor stops it too. Disarming is a WRITE, never a delete, because every delete command in
this environment is auto-denied and a disarm that needs a delete would fail exactly when you need
it.

To check what it is doing right now:

```
python tools/autoloop.py status
```

---

## ARM IT

It is currently **DISARMED**. It was built and tested but deliberately not started.

```
python tools/autoloop.py arm --max 200 --by marshall     # a cap of 200 continuations
python tools/autoloop.py arm --max 0   --by marshall     # NO LIMIT (0 == unlimited)
```

`--max` is a real, visible setting, not a removed safety. Whatever you choose gets printed into
every single continuation (`continuation 37/200`, or `continuation 37/unlimited`), so an uncapped
run says so on every turn rather than being invisible. Change it later without re-arming:
`python tools/autoloop.py set-cap 500`.

**What the loop actually does.** At each turn boundary it tells the session: do not stop; re-read
`notes/PLAN_NEXT_12H.md`, `notes/STATUS.md` and `notes/BOARD.md` **from disk**; update the plan in
place; carry on with its top unblocked item. Nothing in that instruction relies on the
conversation, because after a compaction the conversation is gone.

**Four things stop it anyway:**

| | |
|---|---|
| you disarm | takes effect next turn |
| a tool call is **denied** | the loop halts and files the denial to the board as a question. It never retries a variant and never routes around it. This includes denials inside background subagents, which otherwise skip the step and carry on silently. |
| the cap is reached | if you set one |
| the harness's own loop guard fires | `stop_hook_active`, untouched |

---

## THE BOARD -- `notes/BOARD.md`

Open it in any markdown editor, on your phone or your desktop. **Type your decision into the
ANSWER cell. Save. That is the entire protocol.** You do not need to touch the `status` column and
you do not need to run anything: a non-empty ANSWER counts as answered, and the row moves down to
`## ANSWERED` next time the file is rewritten.

It is **rewritten in place, never appended**, so it does not scroll and does not grow.

You can mangle it. A raw `|` typed in an answer, a deleted trailing pipe, collapsed spacing, rows
reordered, the separator line removed, a `## MY NOTES` section of your own added at the bottom --
all of it round-trips without losing text. That is covered by `python tools/board.py self-test`.

`## STATUS` at the top mirrors `notes/STATUS.md` (position, top item, what is running) so the board
stands alone as a status read.

For the agent side:

```
python tools/board.py ask "<question>" --why "<what is blocked>" --rec "<recommendation>"
python tools/board.py open          # list what is waiting on you
python tools/board.py count         # just the number
python tools/board.py resolve Q3 --answer "do the second one"
python tools/board.py sync          # rewrite in place
```

Every session start prints `N open questions on the board`, so an unanswered question cannot be
forgotten across a compaction.

---

## The safety rule

`D:/AI/hd-instrument/.claude/settings.json` now denies **Write / Edit / MultiEdit / NotebookEdit**
against `preregs/**` and any `arm_key*` file.

The reason is structural, not hypothetical: a Stop hook removes an agent's ability to give up. A
stuck agent that cannot stop keeps generating approaches, and eventually one of them is "widen the
bands" or "regenerate the key". Prompt text does not protect against that; a harness rule does.
This is the rule your own `notes/PLAN_NEXT_12H.md` standing rule 8 asks for.

**Known gap, stated plainly:** this covers the file-editing tools, which is how agents actually
edit files. It does **not** cover a shell command that writes to those paths by redirect, because
shell rules match on a command prefix and cannot express "any command that writes here". If you
want that closed too, it needs a `PreToolUse` command hook inspecting `Bash`/`PowerShell` command
strings -- say the word and it can be added.

---

## Files

| path | what it is |
|---|---|
| `D:/AI/hd-instrument/tools/autoloop.py` | arm / disarm / cap |
| `D:/AI/hd-instrument/tools/board.py` | the board: ask, open, resolve, sync |
| `D:/AI/hd-instrument/notes/BOARD.md` | the board itself -- the file you read and answer |
| `D:/AI/hd-instrument/data/hooks/staging/stop_hook.py` | the loop (guards 1, 1D, 2, 3) |
| `D:/AI/hd-instrument/data/hook_state/autoloop.json` | armed yes/no + the cap |
| `D:/AI/hd-instrument/data/hook_state/_denial_halts.log` | every time a denial stopped the loop |
| `D:/AI/hd-instrument/.claude/settings.json` | hook registration + the prereg/arm-key deny rule |

Self-tests, all green as of 2026-08-15:

```
python tools/board.py self-test                      # 25 checks
python tools/autoloop.py self-test                   # 16 checks
python data/hooks/staging/stop_hook.py --self-test    # 4 suites, incl. end-to-end guard proofs
python tools/session_start_hook.py --self-test
```

---

## One thing needs your decision (it is Q1 on the board)

The Stop hook is registered **twice** -- once in this project's `.claude/settings.json` and again
in your user-level `C:/Users/marsh/.claude/settings.json`. So it fires twice per turn boundary, and
the user-level copy also applies this repo's hook to every other project on this machine. The
double-counting of the continuation cap is mitigated in code, but the cause is a config line in
your personal settings, which an agent should not edit. Deleting the `hooks` block from the
user-level file fixes it.
