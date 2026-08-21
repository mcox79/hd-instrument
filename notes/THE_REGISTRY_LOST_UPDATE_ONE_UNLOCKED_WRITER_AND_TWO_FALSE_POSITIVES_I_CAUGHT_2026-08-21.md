# **CHASING THE LOST UPDATE: ONE GENUINELY UNLOCKED WRITER, AND TWO FALSE POSITIVES THAT WERE MY OWN. I STILL CANNOT NAME WHAT CLOBBERED TONIGHT'S AUDIT, AND SAY SO.**

**The audit computed the right answer at 10:00 and 10:03 this morning and the rows kept the 05:24
values eleven hours later. This is the hunt for the writer that discarded them.**

---

## 1. THE HAZARD IS REAL AND THE AUDIT NAMES IT ITSELF

*`capability_registry_audit.py:1495`, its own comment:* **it is a read-modify-write writer of this
file, *"the same class of race that caused the reported lost-update bug for one-off registration
scripts."*** **The correct primitives already exist** -- `RegistryLock` and, preferred,
`registry_transaction()`.

> ### **ATOMIC IS NOT THE SAME AS SAFE. An atomic `os.replace` guarantees nobody ever sees a HALF-WRITTEN file. It does nothing whatsoever about a LOST UPDATE -- and every writer here is already atomic.**

## 2. 🔻 **MY FIRST SCAN SAID "TWO UNLOCKED WRITERS". BOTH EXTRA HITS WERE MINE, AND I CHECKED BEFORE EDITING.**

| candidate | verdict |
|---|---|
| `substrate_capability_registry.py` | 🚫 **FALSE POSITIVE -- it writes `data/substrate_capability_registry.jsonl`, A DIFFERENT FILE.** *It merely mentions the other one in prose.* |
| `session_start_hook.py` | 🚫 **FALSE POSITIVE -- those writes are MY OWN self-test fixtures, into tempdirs.** *My detector flagged the tests I had written an hour earlier.* |
| `_skunkworks_atomize_2026_07_31_...py` | ✅ **REAL. `REGISTRY = "data/capability_registry.jsonl"`, read-modify-write (`reg_lines + [reg_line]`), NO lock.** |

***I was one step from adding a lock to a file that does not touch this registry.*** **The check that
stopped me was reading the `REGISTRY =` constant instead of trusting a filename match** -- which is
CLAUDE.md evidence discipline 5, *"right file"*, firing exactly as written.

## 3. ⚠️ **AND THE HONEST LIMIT: THE ONE REAL WRITER IS PROBABLY NOT THE CULPRIT**

**It is dated 2026-07-31 and is a one-off atomize script.** *Today's two registrations landed at
09:43 and 11:53 local and left rows carrying a hand-written `integration_status: None` that no audit
run produces.* **The scripts that did it were almost certainly ad-hoc and in `scratch/`, which is
gitignored -- so THERE IS NOTHING LEFT ON DISK TO INSPECT.**

> ### **I CANNOT NAME THE WRITER THAT DISCARDED TONIGHT'S AUDIT. The MECHANISM is established, the INSTANCE is not, and those are different claims.**

## 4. ✅ WHAT ACTUALLY MITIGATES IT

***You cannot add a lock to a script that does not exist yet.*** **So the mitigation for ad-hoc
writers is DETECTION, which shipped earlier tonight:** `session_start_hook.registry_report()` now
flags **rows older than the report** -- the exact fingerprint of a discarded audit -- with an hour of
tolerance because the audit stamps rows at START and names its report at FINISH.

## TLDR

Earlier tonight I found that our capability list had thrown away the results of its own check.
**This was the hunt for what threw them away.**

**The danger is real and the tool warns about it in its own comments:** two programs editing the same
file at once, where whichever saves last silently wins. Every writer already writes safely in the
sense that you never catch a half-finished file — **but that protects against a torn file, not
against one program quietly undoing another's work.**

**My first sweep said two programs were unsafe. Both were wrong, and one of them was my own test
code** flagging fixtures I had written an hour before. The other turned out to edit a *different*
file with a similar name. **I caught both by opening them and checking which file they actually
write, rather than trusting the name match** — and I was one step from "fixing" something unrelated.

**One genuinely unsafe program remains**, from three weeks ago.

**But I want to be straight about the limit:** that one is probably not what caused today's loss. The
likely culprits were throwaway scripts that aren't kept, **so there is nothing left to examine.** I
know the mechanism; I cannot name the instance.

**Which is why the fix is a detector rather than a lock** — you cannot lock a script nobody has
written yet. That detector went in earlier tonight and would catch the next one.

## QUESTIONS

None.

## NEXT STEPS

1. **The rule is now in `CLAUDE.md`** so the next one-off registration author sees it before writing.
2. *The remaining unlocked writer is a dated one-off; leaving it rather than editing a historical
   artifact, and it is recorded here.*
3. *Method note: **my own scan produced two false positives and I caught both by checking the
   target constant.** A filename appearing in a file is not evidence the file writes it.*
