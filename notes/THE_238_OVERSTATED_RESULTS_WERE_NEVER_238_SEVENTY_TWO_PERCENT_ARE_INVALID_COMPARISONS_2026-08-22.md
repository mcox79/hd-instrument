# **"238 OVERSTATED RESULTS" WAS A COUNT OF FLAGS, NOT OF OVERSTATEMENTS. 72.4% PAIR NUMBERS THAT MAY NOT BE COMPARED. THE REAL READ LIST IS 35.**

**Owner ruling that produced this (OP1 / board Q112, 2026-08-22):** *"re adjudicate them I think --
you can do it fast, and then put this behind us."* **That overrode my own recommendation, which was
to MARK ALL 238 in place because re-adjudicating them "is weeks of work". The owner was right and I
was wrong: it is fast, because it is mechanical.**

Reproduce: `python tools/adjudicate_floor_flags.py` (self-test `--self-test`, 7/7).

---

## 1. THE ADJUDICATION

**7,868 `metrics.json` scanned; 286 flagged by `tools/strongest_floor_audit.py`.**
*(The count is 286 today, not 238. **Quote neither from memory -- re-run it.**)*

| disposition | n | share |
|---|---|---|
| 🔻 **`INADMISSIBLE_COMPARISON`** | **207** | **72.4%** |
| `SELF_DECLARED_FAILURE` | 1 | 0.3% |
| ✅ **`UPHELD`** | **43** | 15.0% |
| 🎯 **`NOT_SUPPORTED`** | **35** | **12.2%** |

**Why the inadmissible ones are inadmissible** (a cell can carry more than one):

| reason | n |
|---|---|
| different top-level metric block | 174 |
| different `per_seed` / `per_condition` index | 113 |
| a `max_` statistic compared against a non-`max_` one | 13 |

## 2. WHAT WENT WRONG WITH THE ORIGINAL NUMBER

**The audit finds the largest floor-shaped number and the largest treatment-shaped number ANYWHERE
in a nested `metrics.json` and compares them. It never checks that the two are commensurable.**
Real flagged rows:

- one compares a **REJECT RATE** (`mean_reject_rate_gated_badsource`) against an **ACCURACY**
  (`mean_acc_strong.RANDOMIZED_LOOKUP`);
- one compares **condition 5's floor** (`per_condition[5].floors.no_coref.c_overwrite`) against
  **condition 0's treatment** (`per_condition[0].ref_type.a_name_maintenance`);
- one compares a **`max_err_gap`** against a **`mean_err_gap`**.

**The tool says so in its own output -- it prints "A READ LIST, NOT A VERDICT" every run.** That
caution was then carried into a standing operator decision as though the flag count WERE a count of
overstated results. **The number travelled and the caveat did not, on our own tooling, into a
decision put to the owner.**

> ### 🔑 **AND THE ACTION I RECOMMENDED WOULD HAVE MADE IT WORSE.** *"Mark all 238 as claim-not-supported"* would have stamped that label on **~207 results whose comparison was never valid** -- manufacturing exactly the no-number-crosses-populations error the standard exists to prevent, at scale, in the two indexes the rest of the project reads.

## 3. WHAT THE TWO REAL OUTCOMES MEAN

- **`UPHELD` (43).** The treatment DOES beat the strongest floor in its own metrics; the write-up
  merely QUOTED a weaker one. **A bookkeeping defect, not an overstatement.** Worth fixing in the
  text, not worth withdrawing.
- **`NOT_SUPPORTED` (35).** On a comparison that is actually valid, the cell's own strongest floor
  **beats its own best treatment.** Margins run `+0.9054` down to `+0.0106`. Named examples, and
  they are uncomfortable: `exp_read_grow_adaptor_pyp_kn_breadth_v1` (`+0.9054`, `HARD_PASS`),
  `exp_role_filler_factorization_conceptnet_cg_v1` (`+0.8800`, `HARD_PASS`),
  `exp_information_foraging_reading_v1` (`+0.1178`, `HARD_PASS`).

⚠️ **STILL A CANDIDATE LIST, NOT A VERDICT LIST.** The bottom of it (`+0.0106`, `+0.0230`,
`+0.0368`) sits where a single item flips the answer, and none of the 35 has been read for whether
its floor is the RIGHT floor for its question. **This bounds the problem; it does not close it.**

## 4. 🔻 A CORRECTION TO MY OWN FIRST PASS, MADE BEFORE PUBLISHING IT ANYWHERE ELSE

**I reported `32 NOT_SUPPORTED / 46 UPHELD` one turn earlier. The correct split is `35 / 43`.**
*The first pass was a scratch one-off; it printed "of the 79 admissible cells" and then split
`46 + 32 = 78`. **A cell vanished silently between its own count and its own split, and the
inconsistency was visible in the output I published.*** Reproduced three ways since -- the tool on a
live scan, the tool on the cached snapshot, and the scratch logic re-run on the cached snapshot --
**all three give `35 / 43`.**

*That is the "make outputs print quantities that CONSTRAIN EACH OTHER" rule paying out against me:
`79` and `46+32` could not both be true, and I published anyway.*

## 5. WHY THIS IS NOW A TOOL AND NOT AN ANALYSIS

`tools/adjudicate_floor_flags.py` imports the audit's own `scan()` rather than reimplementing it,
and its self-test asserts each disposition on a REAL flagged shape taken from disk -- including
**two positive controls** (a valid comparison the floor wins must read `NOT_SUPPORTED`; one the
treatment wins must read `UPHELD`) and a **negative control** (a commensurable pair must NOT be
flagged inadmissible, or the tool would excuse everything and be worthless).

---

## TLDR

We had a standing worry that 238 recorded results claimed more than their numbers supported, and
that they had already spread into two lists everyone quotes. Re-checking them mechanically: **that
number was never a count of bad results.** Nearly three quarters of the flagged cases compare two
numbers that cannot be compared -- an accuracy against a rejection rate, one experiment's condition
against a different one. The tool was pattern-matching, and we read its output as a judgement.

What is actually left is **35 results** where an experiment genuinely loses to its own baseline, and
**43** that are fine and merely cited the wrong number in their write-up.

The part worth remembering: **my recommended fix would have been actively harmful.** Marking all 238
would have branded about 200 innocent results as unsupported, committing the exact error the
standard exists to prevent.

## QUESTIONS

None. OP1 is answered.

## NEXT STEPS -- **ALL THREE DONE, SAME DAY. RECORDED HERE SO THE ITEM DOES NOT REOPEN.**

1. ✅ **The 35 are marked in place.** `tools/mark_floor_flag_candidates.py --apply` wrote a
   `FLOOR_FLAG_CANDIDATE.md` sidecar into each of the 35 cell directories -- **additive and
   reversible; no `metrics.json` was edited and no registry row was touched.** Each states the
   margin, both keys and both values, that **it is a candidate and the result is NOT withdrawn**,
   and how to discharge it. Verified 35 on disk, with a positive control (two marked cells) and a
   negative control (an UPHELD cell is NOT marked).
   *Its self-test asserts the WORDING, because the wording is the artifact -- and its negative
   control caught me twice: first I tried to exempt the one string that tripped it, which is a
   checker sharing a flaw with what it checks; then the note's own FILENAME tripped it, since the
   filename contains the word. The assertion is now scoped to the claim body, with a guard that the
   body is non-empty so it cannot pass vacuously.*

2. 🔻 **The 43 are deliberately NOT being edited, and that is the finding.** They already beat
   their strongest floor -- **nothing they claim is wrong**, they merely cited a weaker floor in
   prose. **43 hand-edits to write-ups buys no correctness**, and every one is a chance to
   introduce the transcription error this whole item was about. **They are cleared by being
   ADJUDICATED, not by being rewritten.** *If a specific one of the 43 is ever quoted as
   load-bearing, fix that one then.*

3. ✅ **The audit can no longer emit the bare number that started this.**
   `strongest_floor_audit.py` now prints the four-way decomposition **immediately beside the flag
   count**, not 20 lines below it. **The caution was always in its output -- at the BOTTOM -- and
   only the number travelled.** *That is the "print quantities that CONSTRAIN EACH OTHER" rule
   applied to the tool rather than to the reader, and it is the fifth time a prose caution here has
   been fixed by moving it into a code path.*
