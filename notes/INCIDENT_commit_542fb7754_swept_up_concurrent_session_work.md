# INCIDENT: commit `542fb7754` swept up a CONCURRENT SESSION's uncommitted work

Filed 2026-08-14 by the session that made the mistake, on finding it during a self-audit of its own
diff scope. Nothing was lost or overwritten; the defect is ATTRIBUTION and REVIEW SCOPE.

## WHAT HAPPENED

Landing the graded comparator, I ran `git add hdlab/reading_grounding_loop.py` and committed. That
file also contained UNCOMMITTED edits from a concurrent session working on a different feature (a
definitional-extraction gate). Those edits went into my commit, under my commit message, which
describes only my four additions.

Measured, not estimated. `git show 542fb7754 -- hdlab/reading_grounding_loop.py` has 13 hunks:

**MINE** (the graded comparator landing, all additive and default-off):
- `@@ -79` import line, `@@ -201` `context_vector_masked(..., graded=)`
- `@@ -475` `ConceptSpace.freeze_graded`
- `@@ -539` / `@@ -547` `ReadoutConfig` docstring + `graded_query` field
- `@@ -662` `canonicalize_fast` query-quantiser branch

**NOT MINE** (the concurrent session's definitional-gate work, ~130 of the 215 added lines):
- `@@ -1223` `_make_definitional_gate`
- `@@ -1244`, `@@ -1263`, `@@ -1274`, `@@ -1310` `_provenance_rows` / `checkpoint` changes
- `@@ -1943` `_selftest_definitional_wire_is_off_by_default`
- `@@ -1965` its registration in `_run_all_selftests`

## STATE OF THE TREE — VERIFIED, NOT ASSUMED

- The other session's code is INTACT and coherent. `hdlab.reading_grounding_loop._run_all_selftests()`
  runs **21 self-tests with 0 failures**, including that session's own
  `definitional_wire_off_by_default_ok`.
- My own witness `verification/verify_graded_divisive_comparator.py` is 5/5 PASS, and
  `verify_grounded_word_acquisition_increment1` / `1b` report ALL CHECKS PASS.
- No line of the other session's work was edited by me; the two changes touch disjoint regions of
  the file.

## WHAT I DID NOT DO, AND WHY

**I did not revert, rewrite or split the commit.** The other session may still be live. Rewriting
history or resetting the file is precisely the operation that destroys concurrent uncommitted work,
and the standing rule is to only stop/undo what this session started. A misattributed commit is a
bookkeeping problem; a lost working tree is not recoverable. Disclosure is the correct remedy here
and the decision belongs to the operator, not to me.

## THE RULE THIS BUYS

`git add <specific file>` is NOT sufficient isolation on a repo with a concurrent session — the
existing rule ("never `git add -A` on the canonical store") is about the wrong unit. **Before
committing a shared module, diff it and confirm every hunk is yours** (`git diff -- <file>` and read
the hunk headers), or commit with an explicit path+hunk check. The cost of the check is one tool
call; the cost of skipping it is a commit message that lies about its own contents, which is worse
than a messy diff because it corrupts the record future sessions read.

This is the same class as the rule this session already violated once and recorded: documenting a
confound is not controlling for it. Noticing that a file is shared is not isolating your change from
it.
