# **I RAN `git stash pop` WHEN MY OWN `git stash push` HAD SAVED NOTHING. IT APPLIED ONE FILE FROM A STASH BELONGING TO A DIFFERENT SESSION, FROM 2026-06-28. RESTORED; THE CANONICAL STORE WAS NOT TOUCHED.**

**Reporting this because I caused it, it was avoidable, and the rule it produces is general.**

---

## 1. WHAT I DID

*Trying to check whether a test failure predated my own change, I ran:*

```
git stash push -- hdlab/learner/registry.py     ->  "No local changes to save"
<run the test>
git stash pop                                    ->  applied someone else's stash
```

🔻 **The push saved NOTHING -- I had already COMMITTED that file.** *So `pop` did not undo my push. It
reached for the top of the stash stack, which was
`stash@{0}: On m3-phase1-router-scaffolding: orchestrator-pre-rebase-stash-2026-06-28T21-18Z` -- a
**different branch, a different session, two months old**.*

> ### **`git stash pop` IS NOT THE INVERSE OF `git stash push`. IF THE PUSH SAVED NOTHING, THE POP TARGETS A STRANGER'S WORK.**

## 2. THE DAMAGE, MEASURED FILE BY FILE

*The stash holds 20 files. I hashed each one three ways -- working tree vs stash vs HEAD -- rather
than trusting the pop's own message:*

| file | verdict |
|---|---|
| `.claude/agents/exp_dev.md` | differs from both -- pre-existing local edit |
| `data/director_plan.json` | differs from both -- pre-existing local edit |
| `data/session_key_map.json` | differs from both -- pre-existing local edit |
| 🔻 **`data/exp_r1_multihop_iterative_cleanup_v1/partial_seed23_full.json`** | 🔻 **MATCHES THE JUNE STASH EXACTLY -- APPLIED** |

✅ **The canonical store was NOT touched.** *`data/substrate_index/math/atoms.jsonl` (57,461 lines in
the stash) and `meta/atoms.jsonl` are both CLEAN -- the pop did not reach them, which is why this is a
near miss rather than an incident.*

**ONE file was overwritten with two-month-old content.**

## 3. WHAT I DID ABOUT IT

1. **Preserved BOTH versions to `scratch/_stash_incident/`** *(the applied-stash bytes and the HEAD
   bytes) before changing anything -- so nothing is irrecoverable either way.*
2. **Restored the file to HEAD**, verified by hash.
3. 🚫 **Did NOT drop the June stash.** *It is not mine, it is still `stash@{0}`, and deleting another
   session's saved work to tidy up my own mistake would be a second, worse error.*

⚠️ **ONE THING I CANNOT RECOVER: whether that file had a legitimate LOCAL edit before my pop
overwrote it.** *The pop destroyed that state. HEAD is the last known-good committed version, which is
the defensible restore point, but if someone had uncommitted work in that one file it is gone. It is a
`partial_seed23_full.json` from an experiment landed in June, so the likely loss is nil -- but "likely
nil" is not "none", and it is my doing.*

## 4. THE RULES THIS EARNS

1. 🔑 **CHECK THAT `git stash push` ACTUALLY CREATED AN ENTRY BEFORE POPPING.** *"No local changes to
   save" means there is nothing of yours on the stack. `git stash list` before and after, or use
   `git stash push` output as a precondition.*
2. **PREFER A NON-STASH METHOD TO TEST "did my change cause this".** *`git stash` mutates shared repo
   state. `git show <commit>:<path>` into a temp file, or a worktree, changes nothing.*
3. **A REPO WITH A DELIBERATELY DIRTY TREE MAKES STASH DANGEROUS.** *This one has 373 modified files by
   design (the canonical store is uncommitted, and `CLAUDE.md` forbids `git add -A` on it). Stash
   operations here have a large blast radius and no clean baseline to compare against.*

## TLDR

While checking whether a test failure was my fault, I used a git command to temporarily set aside one
of my own edits. **The command reported that I had nothing to set aside** — I'd already saved that work
properly. I then ran the matching "put it back" command anyway.

**With nothing of mine on the pile, it reached for what was already there: a set of changes another
session had parked in June, on a different branch.**

I checked all 20 files it contained, by comparing their contents rather than trusting the command's
own report. **One file got overwritten with two-month-old content.** The important data — the project's
main knowledge store, over fifty thousand lines of it in that same parked set — **was not touched.**

I saved copies of both versions before fixing anything, restored the file to its last properly-saved
state, and **left the other session's parked work alone** — deleting it to tidy up my own mistake would
be worse than the mistake.

**One thing I can't undo:** if that single file had unsaved edits before I overwrote it, they're gone. It
was a leftover partial result from an experiment finished in June, so the realistic loss is nothing —
but I can't prove that, and I caused it.

**The lesson generalises:** "put it back" is not the opposite of "set it aside" when there was nothing
to set aside. In a repository like this one — which deliberately keeps hundreds of files uncommitted —
that mistake reaches much further than it would elsewhere.

## QUESTIONS

None — Q106 (the scoring sheet) remains open and is unrelated.

## NEXT STEPS

1. 🚫 **Do not use `git stash` in this repo to isolate a change.** *Use `git show <commit>:<path>` into
   a temp location.*
2. **The June stash stays.** *It belongs to another session; it is `stash@{0}` and untouched.*
3. *Method note: **the pop's own message did not tell me what happened** -- "The stash entry is kept in
   case you need it again" reads like nothing was applied. **Hashing every file in the stash against
   both the working tree and HEAD is what found the one that was.***
