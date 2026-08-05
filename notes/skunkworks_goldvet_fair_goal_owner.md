# Skunkworks independent GOLD-VET: exp_c5_fair_goal_owner_v1 (AUDIT-ONLY)

**Auditor:** hdi_skunkworks (independent, AUDIT-ONLY). **Date:** 2026-08-05.
**Verified OFF DATA:** raw bank JSONL + raw lexicons, independent tokenizer/recency recompute
(NOT trusting the cell's own harness or the exp_dev self-VET note). Self-test re-run fresh (6/6 pass)
AND a from-scratch recompute against `V2_DESIRE/V2_OUTCOME_*` reproduced every headline number.
**Verdict: CANONICAL-READY as a recency-trap goal-owner binding instrument, WITH ONE MANDATORY
FRAMING CAVEAT (primacy/subject confound). No bad core items. 0/10 action-implied is a REAL
generative-inference gap, mechanism-confirmed, not a harness artifact.**

## Independent recompute (from raw lexicons, not the harness)
28 core items, 3 sentences each. Per item I checked S1/S2/S3 against the bit-identical desire/outcome
lexicons with my own regex tokenizer + my own nearest-preceding-gender-compatible-mention recency
picker. Result: **0 bad items on ALL of axes 1-4 simultaneously.**
- explicit=18, action_implied=10 (matches).
- SYSTEM correct = 18/28 = **0.6429** (reproduced), and the 18 correct are EXACTLY the 18
  explicit-psych items; action_implied = **0/10** (reproduced).
- recency==gold = **0/28** (floor 0.0, genuine trap on every item).
- majority(primacy-tiebroken)==gold = **28/28** (1.0).
- Every core item: owner named exactly once, foil named exactly once — name-count set = {(1,1)}.

## AXIS-BY-AXIS

**1. GENUINE RECENCY TRAP — PASS (28/28).** On every core item a gender-matched distractor D is
introduced in S2, between the S1 goal and the S3 outcome; S3 refers to the owner by a bare pronoun
only, so the nearest-preceding gender-compatible mention is D. My independent nearest-mention picker
lands on the foil on 28/28 (recency floor = 0.0 by construction, reproduced, not hardcoded). No item
where recency accidentally picks the owner. Self-test 1/6 (same claim, their resolver) also 28/28.

**2. GOLD CORRECTNESS — PASS (28/28).** gold_outcome_owner == the S1 goal-holder P on all 28, and
P is decoupled from the S3 outcome-sentence's naive-recency subject (which is D). outcome_polarity
verified: every "unmet" S3 carries exactly one V2_OUTCOME_UNMET trigger and no MET trigger; every
"met" S3 the reverse. S1 never carries an outcome trigger; S2 (distractor) carries no goal/outcome
trigger; S3 carries no desire trigger. All hand-read + mechanically reconfirmed.

**3. EXPLICIT vs ACTION-IMPLIED + the 0/10 — PASS; 0/10 is a REAL gap, NOT a harness bug.**
18 explicit items each carry a real V2_DESIRE verb in S1; 10 action-implied carry NONE (verified 0
violations both directions). Mechanism trace of WHY 0/10 (recomputed by hand, two items):
`type_sentence_events` types a GOAL event only when a desire token is present. Action-implied S1
("Ruth set out at dawn to draw water...") has no desire token -> no GOAL event -> the ContentMatch
resolver has no open-goal to prefer -> it falls back to recency at the S3 pronoun -> lands on the
foil, identical to the baseline -> `directed_goal_outcome_score` = 0.0 for BOTH candidates ->
`decide_keep_or_revert` abstains -> final = baseline = foil = WRONG. The outcome IS still typed on
these items (they carry a valid outcome trigger), so they remain in the divergent subset and the
0/10 is a real, reportable finding: the lexicon typer cannot GENERATIVELY infer a goal from an
action. This is the exact gap named in DRILL_SYNTHESIS Part B — CONFIRMED as a representational /
generative-inference gap, the harness is behaving correctly.

**4. LEAKAGE / DEGENERACY — PASS on stated checks, but see the load-bearing caveat below.**
Owner is never the only roster entity (foil always present, real 2-way choice); the outcome word is
a name, never the label token (no label leakage); both candidates are gender-matched and plausible.
Templating IS heavy (identical 3-sentence skeleton, repeated "and was sorry"/"and won" tails) — a
non-issue for THIS glass-box lexicon+resolver pipeline (no learned pattern-matcher), but flag for
any FUTURE learned system trained/eval'd on this bank.

**5. VALIDITY GATES — PASS, arithmetic matches pre-reg.** recency_floor_divergent=0.0 (<0.5 ✓),
ceiling=1.0 (>=0.9 ✓), n_divergent=28 (>=10, stable across 3 seeds ✓), system=0.6429 reproduced,
scramble: gain_unscrambled=0.6429, gain_scrambled=0.0 <= 0.5*gain -> collapses, scramble_vacuous
=False. instrument_valid=True, pipeline_beats_recency_fair=True. All consistent with metrics.json.
The scramble collapse is the ONE result that redeems the number (see caveat): mislabeling the GOAL
onto the foil drags the system to 0.0, proving the system's 18/28 is genuinely GOAL-CONTENT-driven,
not primacy-driven.

**6. NO-DISTRACTOR TWINS — PASS as a control (1.0), with a scope note.** All 14 twins resolve to
the owner (single entity -> recency trivially lands on owner). They correctly isolate that the
action-implied failure is a bind-under-distraction failure (drop the distractor and recency itself
is right). But twins are a sanity control, not a capability measure — single-entity twins do not
discriminate goal-binding from any positional heuristic.

## CLEAN-CORE-ITEM COUNT
**28 / 28** core items are simultaneously genuine-trap + correct-gold + correctly-labeled +
non-leaky (on the stated leakage axes). Bad-item list: **NONE.**

## LOAD-BEARING DEFLATIONARY CAVEAT (symmetric anti-negativity — verify a positive as hard as a negative)
The headline "first fair goal-owner number 0.64, beats recency 0.0" is TRUE but **overstates the
achievement, and must not become canonical without this caveat:**

- On this exact bank a **trivial primacy / first-mention picker scores 28/28 (1.0)** — the reported
  majority baseline is 1.0, and my recompute shows it is 1.0 purely as a first-mention tiebreak
  (owner and foil each named once). The **S1-subject picker (ceiling baseline) also scores 1.0.**
- Cause: the owner P is confounded — it is ALWAYS simultaneously (a) the S1 grammatical subject,
  (b) the first-mentioned entity, and (c) the goal-holder. The instrument defeats the RECENCY
  confound (the old bank's flaw) but re-introduces / retains the **PRIMACY + SUBJECT confound** —
  the same class of degeneracy the fairness audit criticized in the auto-mined bank (there a
  subject-picker scored ~100%; here a subject/first-mention picker STILL scores 100%).
- Therefore **accuracy on this bank does NOT establish that goal-binding is REQUIRED to score.**
  What the instrument DOES rigorously establish (via the non-vacuous scramble collapse to 0.0) is
  that the SYSTEM's mechanism is goal-content-driven. Those are different claims; only the second
  is earned by this bank.
- The system's 0.6429 is in fact BELOW the trivial primacy ceiling of 1.0 — the honest read is
  "the system does genuine goal-binding but currently underperforms a first-mention heuristic on a
  bank where first-mention happens to be correct every time."

## RECOMMENDATION
- **Canonical-ready** as "the first FAIR (recency-trap-defeating) goal-owner instrument with a
  genuine goal-content scramble control." Numbers are honest and the majority=1.0 confound is
  already surfaced in metrics.json (transparent, not hidden) — no blocking defect.
- **Before the 0.64 is used as a capability headline**, add "primacy-trap" items where the
  goal-holder is NOT the first-mentioned / not the S1 subject (e.g. introduce the foil first, then
  P states the goal), so that primacy and subject baselines FAIL and only goal-binding wins. That
  is what would convert 0.64 from "beats recency" into "beats every position heuristic."
- **0/10 action-implied CONFIRMED** as a real generative-goal-inference gap (representational, not
  a bug) — a legitimate target for the missing-LEARNING-component fix, not something to paper over.

**Audit disposition:** instrument VALID + gold clean (28/28); primary capability CLAIM to be
framed as goal-content mechanism proven (scramble), NOT accuracy-supremacy (primacy confound).
