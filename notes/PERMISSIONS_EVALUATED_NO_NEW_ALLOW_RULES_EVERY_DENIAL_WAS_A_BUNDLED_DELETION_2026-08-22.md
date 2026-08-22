# **PERMISSIONS EVALUATED ON THE OWNER'S INSTRUCTION. NO NEW ALLOW RULES ARE NEEDED, AND ADDING ANY WOULD HAVE PREVENTED NOTHING.**

**Owner, board Q107:** *"evaluate if we need new allow rules - you should be able to see if there's
theings we should allow that are currently not"*

**Evaluated from `data/hook_state/_denial_halts.log` -- the actual record of what was denied --
not from memory.**

---

## THE EVIDENCE, SELF-TEST NOISE EXCLUDED

| the denied command | why it was denied |
|---|---|
| `tail -8` + `echo ...` + **`rm -rf data/exp_corpus_scale_child_regime_ladder_v1_smoke`** | `Bash(rm -rf:*)`. **`tail` was innocent and rode along.** |
| `cd /d/AI/hd-instrument; timeout 60` **`rm -f scratch/_full_cert_run.txt`** `; nohup pytest ...` | `Bash(rm -f:*)`. *This is the one that produced Q107.* |
| a multi-line PowerShell detached launch (`$stdout = ...` / `$stderr = ...` / `$pidfile = ...`) | could not match the **deliberately narrow** `PowerShell(Start-Process -FilePath D:/AI/hd-instrument/.venv/Scripts/python.exe:*)` grant |

> # **EVERY REAL `permission-rule` DENIAL ON RECORD EITHER CONTAINS A DELETION TOKEN OR FAILED TO MATCH A GRANT THAT `CLAUDE.md` EXPLICITLY SAYS NOT TO BROADEN.**

**This reproduces the 2026-08-13 audit exactly** -- all 283 transcripts of session `139818eb`,
parsed on `toolDenialKind` rather than on text: **31 auto-denies, 31 of 31 contained `rm` or
`Remove-Item`, and ZERO came from a missing allow entry.** *Two independent samples, five days
apart, same answer.*

## WHY ADDING ALLOW RULES CANNOT HELP

**DENY BEATS ALLOW.** An allow entry for `tail` would not have saved the `tail` command above,
because the deny rule fired on the `rm -rf` welded onto the same call. *The read-only commands
these sessions want -- `ls`, `du`, `git status`, `grep`, `stat`, `Test-Path`, `tail` -- are already
reachable and died only as passengers.*

## THE ONE CASE THAT IS NOT A DELETION, AND WHY IT STILL IS NOT A GAP

The PowerShell launch is a genuine non-match: a multi-line script that begins `$stdout = ...`
cannot match a grant anchored on `Start-Process -FilePath ...python.exe`. **The fix is to write the
launch as a SINGLE `Start-Process` invocation**, which is how `CLAUDE.md` documents it -- **not to
widen the grant, which that file explicitly forbids** (*"Do NOT broaden this to a general
`PowerShell(Start-Process:*)` grant"*).

## 🚫 NO CHANGE MADE

`.claude/settings.json` (project) and `C:/Users/marsh/.claude/settings.json` (user, 103 allow
entries, 14 deny) are **untouched**. The operative rule is the one already written down:
**never bundle a deletion with real work in one call**, and write throwaway output to `scratch/`
rather than trying to delete anything.

---

## AND THE RELATED RULING, IMPLEMENTED THE SAME HOUR

**Owner, board Q110:** *"i don't want any more questions on bullshit like this here. you need to
figure out these kinds of things on your own"* -- said after two auto-filed denial questions
(Q107, Q110) reached their board.

✅ **DONE: `_record_denial_halt` no longer files to `notes/BOARD.md`.** Denials are logged to
`data/hook_state/_denial_halts.log` and surfaced to the session, which already carries the full
diagnosis procedure in `CLAUDE.md` (the three `toolDenialKind` values and what each means).
🔑 **THE HALT IS UNCHANGED** -- `GUARD 1D` still ends the loop on a real denial, which is the part
that protects a dropped precondition. **Only the notification channel moved.**
✅ *Three self-test assertions that asserted the OLD behaviour were **INVERTED, not deleted**, so
the new contract is enforced exactly as hard as the old one was.*

⚠️ **THE HOOK EDIT HAS NO COMMIT HASH: `data/hooks/staging/` is GITIGNORED, so the live Stop hook
exists only in the working tree.** *Any checkout, reset or clean destroys it. That is a standing
hazard, not a consequence of this change.*

---

## TLDR

You asked whether we need to allow things we currently do not. The answer is no, and the record is
unambiguous: every command that was actually blocked had a delete instruction welded onto it. The
harmless parts -- reading the end of a file, listing a folder -- were simply passengers on a call
that was going to be refused anyway. Adding permissions would not have saved a single one, because
a block always beats an allowance.

The one exception was a launch command written across several lines, which could not match a
deliberately narrow permission. The fix there is to write the command differently, not to loosen
the permission.

Separately: the loop no longer bothers you with these. It records them and works them out itself.

## QUESTIONS

None.

## NEXT STEPS

None on permissions. The standing rule stands: never bundle a deletion with real work.
