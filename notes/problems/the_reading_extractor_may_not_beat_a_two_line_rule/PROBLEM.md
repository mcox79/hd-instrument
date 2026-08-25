---
priority: 5
review:
review_text:
---

# PROBLEM: the elaborate "read the text" step may be no better than a two-line rule -- prove it earns its keep, or replace it

## 1. THE PROBLEM IN PLAIN LANGUAGE

The first stage pulls out what happened to things in a sentence (which substance dissolved, which
object moved). It scores 90% correct on hand-checked items. But a trivial TWO-LINE rule -- use only
word order and active/passive voice, with all the elaborate filters removed -- reaches 83% on the SAME
items, and the elaborate reader beats that by somewhere between 0 and 14 points, which does NOT
exclude zero. So most of the 90% may be the filters plus two lines of code, not the elaborate
machinery. Either the elaborate reader genuinely beats the two-line rule (prove it AT POWER), or it
does not and should be REPLACED -- freeing the effort for the one stage that is actually broken
(deciding what words mean).

## 2. WHY THIS ONE

It is a SIMPLIFICATION decision with real payoff either way. If the elaborate reader wins at power, we
stop second-guessing it. If it does not, replacing it with two lines removes a large amount of
machinery that is not earning its keep and redirects effort to stage 2 (the wall). The stage's own
goal names exactly this: "Either show the elaborate reading beats the two-line rule at power, or
replace it with the two-line rule and spend the effort on stage 2."

## 3. HOW THE BRAIN DOES THIS (frame)

The brain assigns thematic roles (who did what to whom) using syntax (word order, voice) AND
verb-specific knowledge -- it is not purely positional. The two-line rule captures the
positional/voice part (a PINNED-simple baseline). The question is whether the elaborate reader's extra
machinery adds real thematic-role signal OVER that, or merely reproduces the positional default. Keep
the OPERATION the brain adds (verb-conditioned role assignment) ONLY if it MEASURABLY beats the
positional rule; do not keep machinery that reproduces the default at 10x the code.

## 4. MEASURED vs INFERRED

MEASURED (`the_grow_by_reading_pass_has_no_floor`, SOLVED): elaborate reader 0.90 on 100 hand-checked
items; the two-line rule (word-order + voice, filters OFF) 0.83 on the SAME items; elaborate-minus-
two-line = +0.00 to +0.14, NOT excluding zero. Strongest trivial floor (first_noun_after_verb /
syntactic_object) = 0.7053.
INFERRED (open): whether, at adequate POWER (larger held-out set), the elaborate reader beats the
two-line rule CI-separated. If it does not, the elaborate machinery is not earning its keep.

## 5. ALREADY TRIED (do not re-run)

- `the_grow_by_reading_pass_has_no_floor` (SOLVED) established 0.90 vs 0.83 vs 0.71 on n=100. Do NOT
  re-run that; POWER it up (a larger held-out hand-adjudicated set, or a corpus-scale proxy with a
  controlled floor).
Query `experiment_index.py query "role"`, `query "thematic"`, and check the ledger first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `notes/problems/the_grow_by_reading_pass_has_no_floor/SOLVED.md`; confirm the two-line rule
  (word-order + voice) and the 0.90 / 0.83 / 0.71 numbers still hold at HEAD.
- Confirm the elaborate reader and the two-line rule are both runnable on the same items.

## 7. THE BAR

On a held-out, hand-adjudicated (or controlled-proxy) role-assignment set LARGER than n=100, floor
recomputed on that population: the elaborate reader must beat the two-line rule (word-order + voice,
elaborate filters OFF) CI-separated over its UPPER bound, information-free twin LOSING. HOW WE WOULD
KNOW IT FAILED, and this is a full PASS for the brief: it ties or loses the two-line rule at power ->
the elaborate machinery does not earn its keep, and the recommendation is to REPLACE it and redirect
the effort to stage 2.

## 8. FILES AND ENTRY POINTS

- `notes/problems/the_grow_by_reading_pass_has_no_floor/SOLVED.md` -- the n=100 result + the two-line rule.
- `hdlab/thematic_role_labeler.py`, `hdlab/definitional_extraction.py` -- the elaborate reader / role
  assignment. Prove in `experiments/` + `verification/`; propose any hdlab change in `SOLVED.md`
  (strategy lands it, board Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the 0.90 as the elaborate reader's merit -- most of it is the filters + two lines; the
  merit is the elaborate-minus-two-line margin, which is what to power up.
- Do NOT re-run the n=100 comparison; the question is POWER, on a larger population.
