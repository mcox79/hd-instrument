---
review: EXCELLENT
review_text: EXCELLENT, re-integrated off owner-DONE final content. Headline re-verified (WITNESS PASS, ELABORATE_DOES_NOT_BEAT_TWO_LINE_REPLACE): the elaborate perceptron reader LOSES to a two-line word-order+voice rule at power (n=17,330) -> REPLACE (do NOT route patient selection through the perceptron; do not weight animacy for English). Best simple reader = word order + PRECISE voice (0.7950). Deeper (owner-directed): the two-line rule is NOT the ceiling -- it COLLAPSES on reversible object-relatives (the brain's dorsal-parser regime, below the twin), where a FILLER-GAP mechanism recovers it (oracle 1.000; real-parser +0.21 CI-separated); frontier = a STRONGER PARSER + construction gate. Brain-fidelity probe: structural point-to-antecedent is OVER-accurate; a CUE-BASED RETRIEVAL model reproduces the human similarity-interference drop (Gordon 2001). Only the headline witness was re-run this round; the filler-gap + cue-retrieval witnesses exist and should be re-verified before landing on them. Proven-ready landing: precise-voice selector in situation_reader.
---

> ## SOLVER REVIEW -- EXCELLENT (REPLACE + the two-line rule is not the ceiling; owner-DONE re-integration 2026-08-25)
> **Re-verified (WITNESS PASS):** `test_reader_vs_twoline_qasrl_power.py` reproduces `ELABORATE_DOES_NOT_BEAT_TWO_LINE_REPLACE`
> (elaborate 0.776 < two-line 0.793 at n=2685; twin loses; animacy-only ~= twin).
> **Headline:** at power (n=17,330 QA-SRL patient items) the elaborate perceptron reader LOSES to a two-line
> word-order+voice rule (0.7511 vs 0.7661, CI-separated) and collapses worst on reversible items -- the
> brain-predicted failure of its animacy cue for word-order-dominant English (Competition Model). REPLACE it;
> do NOT route patient selection through the perceptron; do not weight animacy as an English role cue. Best
> simple reader = word order + PRECISE voice morphology (0.7950).
> **The deeper, owner-directed reframe (the real payload):** the two-line rule is NOT the ceiling. On reversible
> object-relatives/clefts -- the brain's DORSAL-STREAM regime (BA44 + arcuate; Friederici 2011) -- the two-line
> rule COLLAPSES (0.001 synthetic / 0.080 real, BELOW the info-free twin), while a FILLER-GAP/movement mechanism
> recovers it (oracle-parse 1.000; real-parser +0.21 CI-separated ABOVE). The real-parser arm is net-negative
> overall from weak-parser false positives on canonical clauses -> the frontier is a STRONGER PARSER + a
> construction gate, NOT more cue-integration. Brain-fidelity probe: structural point-to-antecedent is
> OVER-accurate (the tell of a convenient substitute -- flat 1.000, no similarity effect), whereas a CUE-BASED
> RETRIEVAL mechanism reproduces the human similarity-interference drop (Gordon 2001, CI-separated across a
> temperature sweep).
> **Why EXCELLENT:** brain-foundational throughout (Competition Model; dorsal filler-gap; cue-based retrieval);
> full control stack (info-free twin, weight-scramble, single-cue ablations, reversibility stratification,
> oracle-vs-real-parser, the Gordon fidelity probe); caught the QA-SRL isPassive trap; and did NOT stop at the
> refutation -- it found the brain-faithful frontier.
> **HONEST RE-VERIFICATION SCOPE:** only the headline witness was re-run this round (PASS). The deeper findings
> have their own witnesses (`test_reader_fillergap_reversible_objrel.py`, `test_reader_cue_retrieval_interference.py`)
> -- re-verify those before landing anything on them.
> **hdlab landing (PROVEN-READY, deliberate -- Q111):** the ~4-line precise-voice flip in `hdlab/situation_reader.py`
> (passive -> PATIENT before the predicate); needs a `situation_reader` witness + downstream check. The
> filler-gap/cue-retrieval frontier is a NEW problem to package, not a landing.
> **Integration:** `owner_verdict: DONE` confirmed; re-integrated off final content; review recorded; priority cleared.

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
