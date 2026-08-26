---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT for problem: organ_abstains_on_two_thirds_of_v2
STATUS: SOLVED  (diagnosis bar met in full; remedy located and shown to be an UPSTREAM meaning-supply
                 build, NOT a goal-organ patch — a local patch is proven to convert silence to noise)
LEDGER: awaiting strategy re-verify + integration; malformed/incomplete 0.
REVERIFY (scaffold-free; re-derives the whole headline DIRECTLY from the live organ, reads no artifact):
    .venv/Scripts/python.exe verification/test_goal_abstention_diagnosis.py

WHAT "SOLVED" MEANS HERE: the silence's mechanism is named, shown firing at runtime, partitioned, and
its remedy located, with controls. It does NOT mean the abstention is eliminated. The only route that
eliminates it without converting silence to noise is upstream (broad grounded meaning for arbitrary
goal-constructions and outcome verbs = reader_meaning_channel / Phase-1), which is hdlab/ and another
problem's territory — the solver does not write it.

================================================================================
WHAT WAS ASKED
================================================================================
On the new 124-question v2 bank the organ (hdlab.goal_typing.congruence_with_lexicon_fallback) says
"I don't know" 82 times; accuracy reads 0.2339 where always-guessing the commonest answer scores
0.6048. Bar: NAME THE MECHANISM THAT PRODUCES THE SILENCE, WITH THE LINE THAT DOES IT; show a cause
FIRING at runtime on specific items from the 82; PARTITION the 82; if you fix it, the deciding control
is whether the CONVERTED items are RIGHT (vs the converted subset's own base rate); recompute floors on
the scored population.

================================================================================
THE ANSWER
================================================================================
All 82 abstentions terminate at hdlab/goal_typing.py:1984 — lexicon_predict `return "NONE"` (2 return
"AMBIGUOUS") — surfaced by congruence_with_lexicon_fallback at goal_typing.py:2199-2201/2218. They
reach that line because the 4-tier congruence cascade (T1 congruence_outcome_valence_windowed / T2
referent_recurrence / T3 grounded_result_class / T4 request_response) abstained first, and the Levin
last-resort backoff also abstained (fired on 0 of the 82). Only 16/124 items are decided by the real
congruence machinery; 26 more by the flat lexicon; the other 82 are the silence.

================================================================================
PARTITION OF THE 82 (organ_base, no overlay; v2 124 scorable; reproduced to the digit, acc 0.2339)
  cell: experiments/exp_goal_abstention_cascade_trace_v1.py
================================================================================
  42  find_desired_state returns None      GOAL-SIDE coverage gap: goal construction not recognized
  32  find_actual_state_candidates empty   OUTCOME-SIDE coverage gap: outcome verb OOV of the ~60-verb
      (reason="actual_verb_class_unknown")   CLASS_REGISTRY
   4  verb_class_unrelated                 outcome class does not relate to the desired class
   3  referent_extraction_failed           goal/outcome referent could not be extracted
   1  insufficient_sentences               passage splits to <2 sentences
  --  ----
  82  total; terminal lexicon = NONE(80)/AMBIGUOUS(2); Levin backoff applied to 0.

WHAT IS MISSED (from the runtime samples):
  Class A (goal not recognized) = ordinary narrative goal grammar the ~5 construction families miss:
    questions ("what have you done to your hair"), 2nd-person wishes ("I do wish you'd stay"),
    future-will intentions ("I'll write ... promised Anne"), "determined ON learning" (vs covered
    "determined TO VP").
  Class B1 (outcome verb unknown) = social/psychological outcomes outside the 12 physical result
    classes: blushed, admitted, loved, swept by disdainfully, was glad, were promoted.
  Both are OOV misses of closed SUPPLY inventories — the module's OWN docstring already says
  "the closed-set verb lexicons ... are out-of-vocabulary (OOV) for real prose."

================================================================================
THE TWO GAPS COMPOUND -> A STRUCTURAL CEILING
  cell: experiments/exp_goal_abstention_fix_or_noise_v1.py
================================================================================
The brief names find_desired_state as "the likely upstream suspect." Disk says it is HALF the story
(42/82) and the outcome side is the harder wall:
  - even with PERFECT goal recognition only 3/42 Class-A items reach an outcome candidate; the other
    39 re-abstain at the outcome side.
  - only 7/82 abstentions have ANY outcome-side class candidate.
  - only 10/124 items have BOTH a recognized goal AND an outcome candidate -> the whole closed-inventory
    congruence family is ceilinged at ~10-16/124.
=> broadening goal recognition alone converts almost nothing; it just moves the silence downstream.

================================================================================
DOES FIXING IT HELP, OR JUST MAKE NOISE? (brief's 2nd inferred claim — DECIDING CONTROL)
================================================================================
- The abstention, not wrong answers, sinks accuracy: the 42 COMMITTED answers are 29/42 = 0.690, ABOVE
  their own 0.619 base rate. The 82 silences (scored wrong by omission) are the entire reason accuracy
  reads 0.2339 instead of ~0.60. "We've been treating this as an accuracy problem" is the error — it is
  a COVERAGE/abstention problem.
- Converting silence does NOT recover a signal. Majority-guessing all 82 lifts overall to 0.629, which
  only TIES the base rate by construction (the deciding control requires beating the converted subset's
  base rate, which a majority guess can never do).
- INFO-FREE TWIN control: the substrate's own grounded outcome-valence channel (verb_lexical_similarity)
  pushed past its abstain gate to always-answer covers only 13/82 and scores 0.5385 — BELOW that subset's
  base rate (0.6154) AND below its own random-pole info-free twin (mean 0.457, p95 0.6923). The grounded
  signal loses to noise -> the organ genuinely does not know; the abstention is information-bearing (the
  margin gate correctly withholds weak signals; when the grounded tier DOES commit it is 2/2 correct).

================================================================================
FLOORS (recomputed per converted subset; never imported)
================================================================================
  all 124            base rate 0.6048 (majority UNMET 75/124)   [nothing on v2 clears its own null]
  the 82 abstentions base rate 0.5976 (majority UNMET 49/82)
    Class A (42)     0.5952
    Class B1 (32)    0.6250
  the 42 committed   base rate 0.6190  — organ scores 29/42 = 0.690 ABOVE it

================================================================================
CONTROLS (what each EXCLUDED)
================================================================================
- INFO-FREE TWIN: grounded forced-answer (0.5385) < base rate (0.6154) < twin p95 (0.6923) -> excludes
  "the organ knows and is withholding"; the silence carries no reachable signal.
- COMPOUNDING: 3/42 convertible, 7/82 outcome-present, 10/124 both -> excludes "broaden goal recognition
  fixes it"; caps the closed-inventory family.
- REPRODUCTION: the witness re-derives 82/0.2339, the partition (A=42, B1=32), the silence line, base
  rate 0.5976, and the 7/82 ceiling directly from the production organ, reading no experiment artifact.
- NO-CROSS-POPULATION: every floor recomputed on the exact subset; no v1 number imported; the
  contaminated overlay arm (0.2984) not used.

================================================================================
KEY REALIZATIONS (the enabling moves)
================================================================================
1. THE per-prediction `reason` FIELD IS THE INSTRUMENT. All 82 carry one terminal reason
   ("abstain_fallback_to_lexicon") which HIDES the cause; decomposing the cascade tier-by-tier AT
   RUNTIME (not by grepping the module) turned one opaque "silence" into a 42/32/4/3/1 partition.
2. PARTITION BY FIRST POINT OF FAILURE, THEN TEST WHETHER THE GAPS STACK. Asking "if the goal WERE
   recognized, is the outcome even answerable?" (3/42) is what flipped the recommendation from
   "broaden find_desired_state" to "the outcome-side grounding is the real wall."
3. FORCE THE ABSTAINING MECHANISM TO ANSWER AND CHECK IT AGAINST ITS OWN INFO-FREE TWIN. Losing to a
   random-pole twin is what proves the silence is information-bearing, not withheld knowledge — the
   difference between "fix it" and "the organ correctly does not know."
4. RECOMPUTE THE BASE RATE ON THE EXACT CONVERTED SUBSET (0.5976) — that is what makes the 0.629
   "force-majority" number legible as noise-at-base-rate rather than a win.

================================================================================
CORRECTION TO THE BRIEF (disk outranks brief)
================================================================================
Brief §3 INFERRED: "the cause is pattern coverage ... find_desired_state failing to match Sherlock
Holmes-era constructions." CONFIRMED as to "coverage" but REFINED: (a) it is coverage on BOTH sides,
and the outcome side (32) is the structurally harder one, unnamed in the brief; (b) the missed
constructions are ordinary narrative grammar (questions, 2nd-person wishes, future-will intentions)
spread across the modern novels — only 19 items are Sherlock Holmes, so "Sherlock-era syntax" is too
narrow a framing. (Also confirms brief §2: abstention is uniform across classes — 33 MET / 49 UNMET
among the 82 — so NOT a majority-alignment artifact.)

================================================================================
WHAT I DID NOT ESTABLISH (withdraw first if wrong)
================================================================================
- The CEILING of the real fix (broad grounded meaning supply) is ESTIMATED (~0.69, from the committed-
  subset accuracy), not built. Withdraw this first; the diagnosis does not depend on it.
- The 4/3 tail (B2 verb_class_unrelated, B3 referent_extraction_failed) is characterized by count only.
- The grounded forced-answer control is on a 13-item covered subset — small; it supports only the weak
  claim "no reachable signal," not a precise effect size.

================================================================================
FILES
================================================================================
experiments/exp_goal_abstention_cascade_trace_v1.py         (cascade decomposition + 82 partition)
experiments/exp_goal_abstention_fix_or_noise_v1.py          (base rates + compounding + grounded twin)
verification/test_goal_abstention_diagnosis.py              (scaffold-free witness; REVERIFY)
data/exp_goal_abstention_cascade_trace_v1/metrics.json      (per-item trace)
data/exp_goal_abstention_fix_or_noise_v1/metrics.json       (controls)
notes/problems/organ_abstains_on_two_thirds_of_v2/SOLVED.md (full record)

================================================================================
FOR THE STRATEGY SESSION (you own hdlab + integration)
================================================================================
1. Re-verify: .venv/Scripts/python.exe verification/test_goal_abstention_diagnosis.py
2. Do NOT hand-extend DESIDERATIVE_PASS / CLASS_REGISTRY / V2_OUTCOME_* : not brain-faithful (a closed
   word list is not how a situation model grounds an outcome), and the compounding result shows it
   cannot close the gap.
3. THE PROPOSED hdlab CHANGE (brain-foundational): give find_desired_state and
   find_actual_state_candidates a GROUNDED membership test drawing on the reader_meaning_channel /
   Phase-1 meaning-supply asset — replace `lemma in members` with a grounded membership test — so the
   organ can type arbitrary goal-constructions and outcome verbs. Until then, the abstention is the
   organ CORRECTLY reporting it lacks the meaning to decide, and is preferable to base-rate noise.
4. IF any purely local change is wanted, prioritise the OUTCOME side (32 items, the harder wall) over
   the brief's named goal-side suspect (convertible yield 3), and gate every converted item on the
   deciding control here: converted-subset accuracy must beat that subset's base rate CI-separated,
   with an info-free twin losing.

================================================================================
PLAIN-LANGUAGE TLDR
================================================================================
We asked the system about 124 short passages, "did what the character wanted actually happen?" It said
"I don't know" 82 times, and we found exactly why: for 42 it never recognised the passage had a goal at
all (the goal was a question, a "wish you'd stay", an "I'll do it" promise — forms it doesn't know); for
32 more it spotted the goal but the outcome was everyday words (blushed, admitted, loved, swept past)
that aren't in its tiny built-in list. Same root: it only knows a few hundred hand-listed words and real
storybook English uses far more. The "I don't know"s are honest — forced to guess, it did no better than
a coin flip. And its actual answers, when it gives them, are ~70% right. So this was never an
"it's-getting-them-wrong" problem; it's a "doesn't-have-enough-meaning-to-speak" problem, and the cure is
to give it broad grounded word-meaning (the meaning-supply work already on the board), not to keep
hand-adding words.
