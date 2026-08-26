---
problem: organ_abstains_on_two_thirds_of_v2
status: SOLVED
bar: "NAME THE MECHANISM THAT PRODUCES THE SILENCE, WITH THE LINE THAT DOES IT. This is a diagnosis problem first; a fix is only meaningful once the cause is identified." (PROBLEM.md sec.6; sub-requirements -- show a candidate cause FIRING at runtime on specific items from the 82; PARTITION the 82; if you fix it the deciding control is whether the converted items are RIGHT; recompute floors on the scored population -- all satisfied below.)
result: "All 82/124 abstentions terminate at hdlab/goal_typing.py:1984 -- lexicon_predict `return \"NONE\"` (2 return \"AMBIGUOUS\"), surfaced by congruence_with_lexicon_fallback at goal_typing.py:2199-2201/2218. They terminate there because the 4-tier congruence cascade abstained first. PARTITION of the 82 by first point of failure (organ_base, no overlay, v2's 124 scorable, reproduced to the digit -- acc 0.2339): 42 no goal construction recognized (find_desired_state returns None); 32 goal recognized but outcome verb class unknown (find_actual_state_candidates empty -- CLASS_REGISTRY OOV); 4 outcome class unrelated; 3 referent extraction failed; 1 passage < 2 sentences. Two coverage gaps (goal-side 42 + outcome-side 32) = 90% of the silence; both are OOV misses of hand-authored SUPPLY inventories, not a bias artifact or a scoring bug."
floor: "Base rates RECOMPUTED per converted subset (never imported): the 82 abstentions base rate 0.5976 (majority UNMET, 49/82); Class A (42) 0.5952; Class B1 (32) 0.6250; the 42 COMMITTED items base rate 0.6190 with the organ at 29/42 = 0.690 (ABOVE it); v2 all-124 majority floor 0.6048. Nothing on v2 clears its own null (strongest_that_clears_its_own_null=None, verified in the landed measurement), so no 'beats the majority' claim is made."
controls: "(1) INFO-FREE TWIN: the substrate's grounded outcome-valence channel (verb_lexical_similarity) pushed past its abstain gate to always-answer covers only 13/82 and scores 0.5385 -- BELOW that subset's base rate (0.6154) AND below its own random-pole info-free twin (mean 0.457, p95 0.6923); the grounded signal loses to noise, so the silent items carry no signal reachable by the current grounded asset. (2) COMPOUNDING control: even with PERFECT goal recognition only 3/42 Class-A items reach an outcome candidate (the other 39 re-abstain at the outcome side); only 7/82 abstentions have ANY outcome-side class candidate; only 10/124 items have both a recognized goal and an outcome candidate -- the closed-inventory congruence family is structurally ceilinged at ~10-16/124. (3) REPRODUCTION control: the scaffold-free witness re-derives 82/0.2339, the partition (A=42, B1=32), the silence line, the base rate 0.5976 and the 7/82 ceiling DIRECTLY from the production organ, reading no experiment artifact. (4) NO-CROSS-POPULATION: every floor recomputed on the exact subset scored; no v1 number imported; the contaminated overlay arm (0.2984) is not used."
files_changed: "experiments/exp_goal_abstention_cascade_trace_v1.py; experiments/exp_goal_abstention_fix_or_noise_v1.py; verification/test_goal_abstention_diagnosis.py; data/exp_goal_abstention_cascade_trace_v1/metrics.json; data/exp_goal_abstention_fix_or_noise_v1/metrics.json; notes/problems/organ_abstains_on_two_thirds_of_v2/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_goal_abstention_diagnosis.py"
---

## What the label means (read this before "SOLVED")

**SOLVED = the diagnosis bar is met in full** -- the silence's mechanism is named, shown firing at
runtime, partitioned, and its remedy located, with controls. It does **NOT** mean the abstention is
eliminated. The one route that eliminates it without converting silence into noise is an **upstream
meaning-supply build** (broad grounded meaning for arbitrary goal-constructions and outcome verbs),
which is another problem's territory (`reader_meaning_channel` + Phase-1 meaning supply) and is
`hdlab/`, which the solver does not write. I deliberately did **not** ship a coverage-patch fix here,
because the controls below prove a within-organ patch converts silence to noise.

## What produces the silence (the mechanism, with the line)

The production entry point `hdlab.goal_typing.congruence_with_lexicon_fallback` is a 4-tier congruence
cascade with a flat-lexicon fallback:

```
T1 congruence_outcome_valence_windowed     goal-congruence: find_desired_state ->
                                            find_actual_state_candidates -> referent link -> class
T2 congruence_referent_recurrence_windowed
T3 congruence_grounded_result_class
T4 congruence_request_response
->  lexicon_predict(sents[-1])              flat V2_OUTCOME_MET/_UNMET (~25 words) + Tier-2 pools
->  Levin last-resort backoff (retry once)
```

Every tier calls `find_desired_state`. When it finds no goal, T1-T4 are all dead and only the flat
lexicon can speak. **The literal line that emits the silence is `hdlab/goal_typing.py:1984`
(`return "NONE"` in `lexicon_predict`)**, surfaced at `goal_typing.py:2199-2201` / `:2218`. All 82
abstentions carry `detail["reason"] == "abstain_fallback_to_lexicon"` with `lexicon_raw` in
`{NONE (80), AMBIGUOUS (2)}`; the Levin backoff fired on **0** of them (it also abstained).

Only **16/124** items are decided by the real congruence machinery; **26** more are committed by the
flat lexicon; the remaining **82** are the silence.

## Partition of the 82 (shown firing at runtime -- `exp_goal_abstention_cascade_trace_v1.py`)

| n | first point of failure | what it is |
|---|---|---|
| **42** | `find_desired_state` returns None | **goal-side coverage gap** -- the goal construction is not recognized |
| **32** | `find_actual_state_candidates` empty (`actual_verb_class_unknown`) | **outcome-side coverage gap** -- the outcome verb is OOV of the ~60-verb CLASS_REGISTRY |
| 4 | `verb_class_unrelated` | outcome verb class does not relate to the desired class |
| 3 | `referent_extraction_failed` | goal/outcome referent could not be extracted |
| 1 | `insufficient_sentences` | passage splits to < 2 sentences |

**What is missed, from the runtime samples.** Class A (goal not recognized) is ordinary narrative
goal grammar the ~5 hand-authored construction families do not cover: questions ("what have you done
to your hair"), 2nd-person wishes ("I do wish you'd stay"), future-will intentions ("I'll write ...
promised Anne"), "determined **on** learning" (vs the covered "determined **to** VP"). Class B1 is
social/psychological outcomes outside the 12 physical result-state classes: *blushed, admitted, loved,
swept by disdainfully, was glad, were promoted*. Both are OOV misses of closed SUPPLY inventories --
the module's own docstring already names this: *"the closed-set verb lexicons ... are out-of-vocabulary
(OOV) for real prose."*

## The two gaps COMPOUND -> a structural ceiling (`exp_goal_abstention_fix_or_noise_v1.py`)

The brief names `find_desired_state` as "the likely upstream suspect." **The disk says it is only half
the story (42/82), and the outcome side is the harder wall:**

- Even with **perfect** goal recognition, only **3/42** Class-A items reach an outcome candidate; the
  other **39** would just re-abstain at the outcome side.
- Only **7/82** abstentions have any outcome-side class candidate at all.
- Only **10/124** items have both a recognized goal AND an outcome candidate -- the whole
  closed-inventory congruence family is ceilinged at ~10-16/124.

So a goal-recognition fix alone (the named suspect) converts almost nothing. Broadening goal
recognition without broadening outcome-verb grounding just moves the abstention downstream.

## Would fixing it help, or just make noise? (the brief's 2nd inferred claim -- deciding control)

**The abstention, not wrong answers, is what sinks accuracy.** The 42 committed answers are 29/42 =
**0.690** correct -- above their own 0.619 base rate. It is the 82 silences (scored wrong by omission)
that drag the aggregate to 0.2339. So "we have been treating this as an accuracy problem" is exactly
the error: it is a **coverage/abstention** problem.

**But converting the silence does not recover a real signal.** Majority-guessing all 82 would lift the
overall number to 0.629 -- which merely *equals* the base rate by construction and is not a capability
(and the deciding control is accuracy on the converted subset vs its same-class base rate, which a
majority guess ties, never beats). The one brain-faithful in-substrate route testable here -- the
grounded outcome-valence channel forced to always-answer -- covers only 13/82 and scores **0.5385**,
**below** the covered subset's base rate (0.6154) and **below its own info-free twin** (p95 0.6923).
The organ genuinely does not know on the silent items; **the abstention is information-bearing** (the
margin gate correctly withholds weak grounded signals -- when it does commit via the grounded tier it
is 2/2 correct on the committed set).

## KEY REALIZATIONS

- **The `reason` field on every prediction is the diagnostic instrument.** All 82 abstentions carry
  one terminal reason (`abstain_fallback_to_lexicon`), which hides the upstream cause; decomposing the
  cascade tier-by-tier at runtime (not by grepping the module) is what turned one opaque "silence" into
  a 42/32/4/3/1 partition. This repo's own rule that grep gets reachability wrong applied here.
- **Partition by FIRST point of failure, then test whether the gaps stack.** The move that changed the
  recommendation was asking, for the 42 goal-side misses, "if the goal WERE recognized, is the outcome
  even answerable?" -- 3/42. Without that compounding test, "broaden find_desired_state" looks like the
  fix; with it, the fix is shown to be structurally capped and the outcome-side grounding is the real
  wall.
- **Force the abstaining mechanism to answer and check it against its own info-free twin.** Pushing the
  grounded channel past its margin gate and finding it loses to a random-pole twin is what proves the
  silence is information-bearing rather than withheld knowledge -- the difference between "fix it" and
  "the organ correctly does not know."
- **Recompute the base rate on the exact converted subset.** The 82's base rate (0.5976) is what makes
  the 0.629 "force-majority" number legible as noise-at-base-rate rather than a win.

## What I did NOT establish (withdraw first if wrong)

- **The ceiling of the real fix (broad grounded meaning supply) is estimated, not measured.** If the
  organ had full goal+outcome coverage and kept its current committed-answer quality (~0.69), overall
  would land near ~0.69 -- but that is an INFERENCE from the committed-subset accuracy, not a built
  result. Withdraw this estimate first; the *diagnosis* (partition, line, compounding, info-free twin)
  does not depend on it.
- **The 4/3 tail (B2 verb_class_unrelated, B3 referent_extraction_failed) is characterized only by
  count**, not per-item traced to a specific verb/referent as thoroughly as A and B1.
- The grounded-channel forced-answer control is on a **13-item** covered subset -- small; the claim it
  supports is deliberately weak ("no reachable signal", consistent with the 0.5385 < base-rate <
  twin-p95 ordering), not a precise effect size.

## Correction to the brief (disk outranks brief)

The brief's INFERRED §3 -- *"the cause is pattern coverage on the new prose (find_desired_state failing
to match Sherlock Holmes-era constructions)"* -- is **confirmed as to "coverage"** but **refined**: (a)
it is coverage on BOTH sides, and the outcome side (32) is the structurally harder one, not named in
the brief; (b) the missed constructions are ordinary narrative grammar (questions, 2nd-person wishes,
future-will intentions) spread across the modern novels, only 19 items are Sherlock Holmes, so
"Sherlock-era syntax" is too narrow a framing.

## What would have to change in hdlab/ (proposed, not landed -- strategy session owns the live substrate)

The diagnosis says do **not** hand-extend `DESIDERATIVE_PASS` / `CLASS_REGISTRY` / `V2_OUTCOME_*`: it is
not brain-faithful (a closed word list is not how a situation model grounds an outcome) and the
compounding result shows it cannot close the gap. The brain-foundational fix is to supply **broad
grounded meaning** so `find_desired_state` and `find_actual_state_candidates` can type arbitrary
goal-constructions and outcome verbs -- i.e. wire the meaning-supply asset that `reader_meaning_channel`
/ Phase-1 is building into these two functions, replacing `lemma in members` with a grounded
membership test. Until then, the abstention is the organ **correctly** reporting it lacks the meaning to
decide, and is preferable to base-rate noise. If a purely local improvement is wanted, the highest-
yield single change is outcome-side coverage (32 > the goal side's convertible 3), not the named
goal-side suspect.

---

## TLDR (plain language)

We asked the system, about 124 short passages, "did what the character wanted actually happen?" It said
"I don't know" 82 times. We found exactly why: for 42 of them it never recognised that the passage
contained a wish or goal at all (the goal was phrased as a question, a "wish you'd stay", an "I'll do
it" promise -- forms it doesn't know); for 32 more it spotted the goal but the *outcome* was described
with everyday words (blushed, admitted, loved, swept past) that aren't in its tiny built-in word list.
Both are the same thing: it only knows a few hundred hand-listed words and constructions, and real
storybook English uses far more. Crucially, the "I don't know"s are honest -- when we forced it to
guess anyway, its guesses were no better than a coin-flip, so it truly doesn't know rather than knowing
and withholding. Its *actual answers*, when it gives them, are good (about 70% right). So this was never
an "it's getting them wrong" problem; it's a "it doesn't have enough vocabulary/meaning to speak"
problem -- and the real cure is to give it broad grounded word-meaning (the meaning-supply work already
on the board), not to keep hand-adding words.

## QUESTIONS

None.

## NEXT STEPS

1. **Strategy session: re-verify** with `.venv/Scripts/python.exe verification/test_goal_abstention_diagnosis.py`
   (re-derives the whole headline from the live organ; reads no artifact).
2. **Route the remedy to meaning supply, not a goal-organ patch.** The fix is to give
   `find_desired_state` and `find_actual_state_candidates` a grounded membership test drawing on the
   `reader_meaning_channel` / Phase-1 asset -- the same bottleneck those problems already own.
3. **If any local change is made, prioritise the OUTCOME side** (32 items, the harder wall) over the
   brief's named goal-side suspect (whose convertible yield is 3), and gate every converted item on the
   deciding control here: accuracy on the converted subset must beat that subset's base rate
   CI-separated, with an info-free twin losing.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT. Re-verified scaffold-free (test_goal_abstention_diagnosis.py: 82/124, partition 42/32/7/1, silence line goal_typing.py:1984, base rate 0.5976, 7/82 compounding ceiling). Adversarial audit passed: the CORE diagnosis is independent of the small (n=13) forced-answer control, which the solver correctly scoped its claim to. Corrects my brief (both sides; outcome side harder; not Sherlock-specific). Remedy routed UPSTREAM to broad grounded meaning supply (the SAME missing organ the meaning line re-opened) -- NOT a local lexicon patch. Review written into PROBLEM.md; priority cleared. Committed (no push).
