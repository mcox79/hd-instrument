# Measurement-layer drift, 2026-08-13 -- a ruler changed while it was being used

READ-ONLY reconciliation. No `hdlab/` or `tools/` code was modified, no store was touched, nothing
was committed. Every number below was recomputed off disk with `.venv/Scripts/python.exe` from
`data/foundation/reading_grounding_v1/store/store_facts.json` (7966 rows) by a single script run
out-of-tree that evaluates BOTH rulers in ONE process.

---

## 1. What happened

The 2026-08-13T05:26Z quarantine report
(`data/foundation_provenance_v1/quarantine_report.json`) recorded that the READING_GROUNDING noise
counts did not reproduce the 05:03Z backfill report, **although not one of the 7966 stored rows
changed** (per-file sha256 identical before and after; `tree_sha256_before ==
tree_sha256_after == 0269bd96...`). Reported deltas: closed-class 119 -> 121, proper-noun
270 -> 255, unclassified 816 -> 718, unknown-too-rare 11 -> 125.

The measurement changed, not the data.

## 2. Root cause -- an ORCHESTRATION error, not a code defect

`hdlab/closed_class_lexicon.py` line 54 does `from hdlab.thematic_role_labeler import lemma_verb`,
and `is_closed_class()` (line 151) tests `w in s or lemma_verb(w) in s`. The corpus-derived
proper-noun table is keyed on `lemma_verb`-normalized lemmas as well. So BOTH noise buckets
normalize through one function.

The Director dispatched a fix to that function (`lemma_verb`: unguarded suffix stripper -> WordNet
morphy with a never-emit-a-non-word guard) at ~05:21Z, **concurrently with audits that measure
through it**. The fix is correct and desirable on its own terms. The error is that a measurement
instrument was being replaced while measurements were running through it.

The changed function is not defective in either version for its own purpose; there is nothing to
revert. What failed was serialization.

## 3. Was it recoverable? YES -- the "not reproducible" note in the quarantine report is WRONG

The quarantine report states: *"the pre-edit working-tree version of thematic_role_labeler.py was
never committed, so the 05:03Z numbers cannot be recomputed from disk."*

That is backwards. Because the fix is **uncommitted**, `HEAD` still holds the PRE-edit version.

Evidence (git, read-only):

```
$ git status --porcelain -- hdlab/thematic_role_labeler.py
 M hdlab/thematic_role_labeler.py          <- modified, UNSTAGED (empty `git diff --cached`)

$ git diff --stat -- hdlab/thematic_role_labeler.py
 hdlab/thematic_role_labeler.py | 72 +++++++++---  1 file changed, 59 insertions(+), 13 deletions(-)
```

The whole diff is ONE contiguous hunk, `@@ -298,33 +298,79 @@`, entirely inside `lemma_verb`.
`git show HEAD:hdlab/thematic_role_labeler.py` contains the old body verbatim, including the
un-excluded trailing-`s` rule that the fix later guarded:

```python
    if w.endswith("es") and len(w) > 3:
        return w[:-2]
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):     # <- no "us"/"is" exclusion
        return w[:-1]
```

`_IRREGULAR_LEMMA` -- the only other state `lemma_verb` reads -- is outside the hunk and therefore
identical in both versions. **The pre-edit ruler is fully retrievable and both sets of numbers are
recomputable.** The reproducibility loss was recoverable, not permanent.

(Method note: the old ruler was reconstructed as a verbatim copy of the HEAD `lemma_verb` body
rather than by importing the HEAD file, to avoid two live copies of the module in one process. The
closed-class SET itself did not drift -- it is frozen on disk in
`data/closed_class_lexicon_v1.json`, untouched, so only the runtime `lemma_verb` call varies.)

## 4. Reconciled numbers -- both rulers, ONE script, one process

Scope: the 1216 non-tautological `GROUNDED_MEANING` rows of `reading_grounding_v1`
(7966 rows -> 3544 GROUNDED_MEANING -> 2328 tautological -> 1216 non-tautological; all three
reproduce exactly). Proper-noun table rebuilt over the same 568 OneStop + `concepts_biology`
files, `>=2` non-sentence-initial occurrences, majority-capitalized.

| bucket (of 1216) | OLD ruler (HEAD) | NEW ruler (working copy) | delta |
|---|---|---|---|
| closed-class object | **119** | **121** | +2 |
| closed-class subject | 13 | 13 | 0 |
| proper-noun object | **266** | **251** | -15 |
| noise LOWER BOUND (union) | **385** | **369** | -16 |
| unclassified (neither) | **812** | **716** | -96 |
| UNKNOWN (too rare to classify) | **19** | **131** | +112 |
| distinct keys in proper-noun table | 18493 | 17300 | -1193 |

**This reconstruction is independent of the two published scripts and matches their DELTAS almost
exactly**: published closed-class +2 (here +2), proper-noun -15 (here -15), union -16 (here -16),
unclassified -98 (here -96), unknown +114 (here +112). The small absolute offsets (my 266 vs the
published 265/270) are tokenizer/sentence-splitter differences -- neither original script survives;
both were run out-of-tree in temp dirs.

**Noted in passing, a second reproducibility problem:** the two OLD-ruler measurements published
tonight disagree with EACH OTHER. `notes/foundation_contents_audit_2026-08-13.md` reports
proper-noun 265 / union 384 / unclassified 821 / unknown 11; `quarantine_report.json`'s "before"
block reports 270 / 389 / 816 / 11. Same ruler, same store, different throwaway scripts, five-fact
disagreement. The instrument is not just unversioned across time, it is unversioned across agents.

### Which number is correct going forward

**The NEW ruler's, with the caveat that neither ruler measures this store cleanly.**

The NEW `lemma_verb` is the correct normalizer for text going forward. But `reading_grounding_v1`
was WRITTEN by the loop under the OLD stemmer, so its subjects and objects are frozen in the OLD
key space as literal non-words (`cal`, `appl`, `babi`, `allel`, `apparatu`, `billionair`,
`endocytosi`). The NEW ruler cannot classify those, and says so -- which is the honest answer.
The OLD ruler's UNKNOWN=11/19 was **falsely low**: it appeared to classify corrupted objects only
because it was normalizing the corpus into the same corrupted key space. It was grading corruption
against corruption.

So: use the NEW ruler, and read its 131 UNKNOWN as a MEASUREMENT OF STORE CORRUPTION, not as a
classifier weakness. Do not read the union dropping 385 -> 369 as a quality improvement -- the 112
rows that moved are un-adjudicated, not clean.

## 5. Mechanism of the 11 -> 125 (here 19 -> 131) UNKNOWN jump

**117 fact rows flipped from classified (COMMON or PROPER) to UNKNOWN. Of the distinct object
lemmas behind them, 95/95 are ABSENT from the new proper-noun table entirely; ZERO are
"present but below the 2-occurrence threshold."** It is a total lookup miss, not a thinning of
counts.

The chain, measured:

1. The store's object strings were minted by the OLD stemmer: `called -> cal`, `apples -> appl`,
   `babies -> babi`, `apparatus -> apparatu`, `alleles -> allel`.
2. Under the OLD ruler the proper-noun table was built with that SAME stemmer, so corpus tokens
   landed on the SAME keys (`apple`/`apples -> appl`). The store's `appl` found a table entry,
   scored majority-lowercase, and was recorded as COMMON -- i.e. it fell into "unclassified".
3. The NEW `lemma_verb` maps corpus text correctly instead (verified on disk:
   `apples -> apple`, `babies -> baby`, `apparatus -> apparatus`, `alleles -> allele`,
   `called -> call`). Keys `appl`, `babi`, `apparatu`, `allel`, `cal` no longer exist -- the table
   loses 1193 keys.
4. The store's object is STILL `appl`. Re-normalized by the NEW `lemma_verb` it stays `appl`
   (the guarded fallback returns the surface form unchanged when no rule lands on a known word).
   Lookup misses. -> UNKNOWN.

So the >10x jump is the ruler and the data falling out of alignment, and what it exposes is a
PRE-EXISTING defect: roughly 10% of the store's vocabulary is over-stemming corruption. That is the
same defect independently found in `notes/sensorimotor_anchoring_scope_2026-08-13.md` section 1e
(126/1216 subjects recovered by adding back a stripped letter) and carried in
`notes/stemmer_corruption_2026-08-13.md`. The ruler change did not create it; it made it visible.

## 6. Blast radius -- which published figures are ruler-dependent

Every figure computed through `is_closed_class` or the proper-noun table. Conclusions are judged
against the NEW ruler.

| published figure | source | OLD | NEW | conclusion survives? |
|---|---|---|---|---|
| noise LOWER BOUND on the 1216 | `foundation_contents_audit` sec.5 + headline | 384 (31.58%) | ~369-373 (30.3-30.7%) | **YES** -- still ">=30% of non-tautological grounded facts are provably wrong-category" |
| closed-class objects | same | 119 | 121 | **YES** -- moves 2 rows; no claim depends on it |
| proper-noun objects | same (265 in the note, 270 in quarantine) | 265 / 270 / 266 | 251-255 | **YES** -- "the proper-noun band was NOT closed by the v2 fix" is unaffected |
| unclassified ("neither") | same | 816-821 | 716-718 | **YES** -- and the caveat "must never be reported as 68% good" is now MORE justified, since ~112 of those rows are non-words |
| UNKNOWN too rare | same | 11 | 125-131 | **conclusion CHANGED**: the note calls this "11 lemmas too rare to judge" and treats it as negligible. Under the correct ruler it is ~10% of the sample and is CORRUPTION, not rarity. This line should be re-read. |
| "2712 (76.52%) demonstrably contentless or wrong-category" of 3544 | `foundation_contents_audit` sec.5 | 2712 = 76.52% | 2697-2701 = 76.1-76.2% | **YES** -- headline claim intact |
| 7966 / 3544 / 2328 / 1216 / 65.69% tautology | `foundation_contents_audit` sec.2-4 | -- | identical | **YES -- NOT ruler-dependent.** Recomputed exactly. Tautology is a string comparison, and the note's own line 96 shows all three normalizations agree. |
| v2_qualityfix noise 54 = 8.52%; v5 noise 88 = 4.21% | `foundation_contents_audit` sec.5 | as published | **NOT RECOMPUTED** | ruler-dependent by construction; direction of change unknown |
| `quarantine_report.json` `per_pipeline.READING_GROUNDING.*` | 05:26Z report | see sec.4 | already NEW-ruler | the file's own numbers are the NEW ruler; only its `..._changes_for_existing_pipelines.before` block is OLD |
| `quarantine_report.json` `per_pipeline.DEFINITIONAL_EXTRACTOR.*` (cc 15, proper 2, unclassified 196, unknown 8) | 05:26Z report | -- | **NOT RECOMPUTED** | ruler-dependent; and its own `proper_noun_table_scope_caveat` already flags that ANAT/PSY are out of table scope |
| ALL of `notes/sensorimotor_anchoring_scope_2026-08-13.md` | -- | -- | -- | **NOT AFFECTED.** Verified by reading: that analysis matches "exact lowercase string match on the surface token as stored" against Lancaster/Brysbaert. It never calls `is_closed_class` and never builds a proper-noun table. Its 1216 / 2328 / 65.7% agree with the recompute here. Its SHELVED decision stands. |

Nothing that was BANKED changed. The quarantine report's own statement holds: "No banked or
backfilled fact was altered by this" -- 7966 rows bit-identical after reload.

## 7. The rule

**Do not run measurements through a function while another agent is modifying it. Serialize
measurement against instrument change: an audit takes the instrument, or the fix does, never both
at once.**

Two supporting corollaries this incident earned:

- **Pin the ruler in the artifact.** Any report whose numbers pass through shared normalization
  must record the git SHA of the tree AND whether the working tree was dirty in the files it
  measured through. Both of tonight's reports would have caught this at write time.
- **"Never committed" does not mean "never recoverable."** Check `git status` / `git show HEAD:`
  before declaring a number unreproducible. An uncommitted edit means HEAD still holds the old
  version -- that is the easiest recovery case, not the hardest.

---

## 8. IT HAPPENED AGAIN THE SAME DAY -- occurrence #2, and the strengthened rule

Section 7's rule was written for occurrence #1 and was already too narrow. A second instance of the
SAME error class occurred hours later, in the opposite direction. Both are recorded here so the
class -- not the instance -- is what gets remembered.

### 8.1 The two occurrences

**Occurrence #1 -- drift in the MEASURING INSTRUMENT (sections 1-7 above).**
The Director dispatched a fix to `lemma_verb` in `hdlab/thematic_role_labeler.py` at ~05:21Z
concurrently with provenance/quarantine audits that normalize through it -- `hdlab/closed_class_lexicon.py`
imports `lemma_verb` (line 54) and `is_closed_class()` calls it (line 151), and the corpus-derived
proper-noun table is keyed on `lemma_verb`-normalized lemmas. The 05:03Z backfill report and the
05:26Z quarantine report therefore disagree (closed-class 119 -> 121, proper-noun 270 -> 255,
unclassified 816 -> 718, unknown-too-rare 11 -> 125) **while not one of the 7966 stored rows
changed** (`tree_sha256_before == tree_sha256_after == 0269bd96...`). The ruler moved under the
measurement.

**Occurrence #2 -- drift in the MEASURED SUBJECT (2026-08-13, ~02:38-02:49).**
The Director dispatched `verification/test_all_witnesses_exit_clean.py` -- a driver that runs all
27 witnesses in sequence -- concurrently with a fix to `hdlab/goal_typing.py`.

| time | event | code state seen |
|---|---|---|
| ~02:38 | `verify_goal_typing.py` executed by the driver | **PRE-fix** `hdlab/goal_typing.py` -> FAILED |
| 02:41 | the `hdlab/goal_typing.py` fix LANDED (mtime), mid-run | -- |
| ~02:46 | `verify_levin_lastresort_backoff`, `verify_path_unification_2a_part1`, `verify_speaker_attribution_goal_holder_2a_part2` executed | **POST-fix** -> all PASSED |

The driver reported **6 failed / 23 passed**. That number corresponds to **no single state of the
codebase**: it mixes witnesses run against pre-fix `goal_typing.py` with witnesses run against
post-fix `goal_typing.py`. The true current state is **5 failing**, all Class-B stale `==` pins --
and that was established only by a follow-up re-run, not by the 6/23 run.

### 8.2 The shared shape

**A measurement was running while the code it measures was being modified, so the result describes
no single state of the repository.**

- In #1 the moving part was the **measuring instrument** (`lemma_verb`, reached transitively).
- In #2 the moving part was the **measured subject** (`hdlab/goal_typing.py`, a witness target).

The direction is irrelevant to the outcome. Both produce a completed run whose numbers are a
temporal blend across two code states, and therefore **cannot be reproduced by checking out any
commit**. There is no tree that yields 6/23, and no tree that yields the 05:03Z bucket counts
alongside the 05:26Z ones.

### 8.3 Why this class is insidious

Nothing errors. The run completes, exits, and emits plausible, well-formed numbers in the expected
range. There is no traceback, no missing file, no failed import, no assertion -- the only symptom
is that the number is wrong in a way that is invisible from the number itself. A stale or crashed
run announces itself; a raced run does not.

Occurrence #2 was caught **only** because an agent cross-checked module file mtimes against
per-witness execution times and noticed the fix landed between two of them. Had nobody done that
arithmetic, "6 failed / 23 passed" would have entered the record as the state of the witness suite
and driven downstream triage against four phantom failures.

### 8.4 The strengthened rule, stated operationally

**Before dispatching any agent that MEASURES -- an audit, a witness run or driver, an experiment
cell, or hand-score sample generation -- confirm that no concurrently-running agent OWNS or may
WRITE any code path the measurement depends on. "Depends on" includes TRANSITIVE dependencies.**

The transitive clause is not decoration: it is exactly how #1 happened. Nobody thought of a
lemmatiser buried two imports deep as "part of the measurement", yet the classifier normalized
every lookup through it, so editing it silently re-scaled two noise buckets.

Operationally, before dispatch:

1. Enumerate the modules the measurement imports, **including their imports** -- not just the file
   named in the task.
2. Cross-check that set against every in-flight agent's declared write scope.
3. If the sets intersect, or if you cannot cheaply establish that they don't:
   **SERIALIZE. The measurement waits.** A delayed measurement costs minutes; a raced one costs
   the run plus a re-run plus the risk that nobody notices.

This supersedes section 7's rule, which covered only the instrument-side case.

### 8.5 Proposed detection practice -- NOT IMPLEMENTED

**Proposal only. Nothing below exists in the repo today; no code was written for this note.**

A long-running measurement should snapshot, at START, the `mtime` + content hash of every module
it has imported (walk `sys.modules` for entries under the repo root, record path/mtime/sha256),
write that manifest into its output directory, and **re-take the same snapshot at FINISH**. If any
entry moved between the two snapshots, the run must **fail loudly** -- not warn -- and mark its own
metrics as VOID, because by construction its numbers span more than one code state.

The same manifest doubles as the "pin the ruler in the artifact" corollary from section 7: it
records exactly which version of every dependency produced the number.

If built, this would have caught both occurrences automatically: #1 via the `thematic_role_labeler`
hash changing, #2 via the `goal_typing` mtime changing.

### 8.6 Cost, concretely

Occurrence #2 burned a **653-second full driver run** (all 27 witnesses) whose headline number was
uninterpretable, **plus the full cost of a re-run** to establish the real 5-failing state. Two
serial full-suite runs to obtain one usable number. Occurrence #1's cost was the reconciliation
work recorded in sections 1-6 of this note: an out-of-tree dual-ruler recompute, plus two published
reports left carrying numbers that must now be read with a ruler caveat attached.

### 8.7 Relation to `notes/shared_flaw_invisibility_2026-08-13.md`

**These are related but DISTINCT failure modes and must not be conflated: a shared flaw makes a
real error invisible because every path is wrong the same way, whereas a concurrent edit makes the
measurement meaningless because it describes no single state of the code at all.**

(As of this writing `notes/shared_flaw_invisibility_2026-08-13.md` does not exist on disk -- the
distinguishing sentence is recorded here so it survives regardless of whether that note lands.)
