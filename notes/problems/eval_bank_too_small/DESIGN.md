# DESIGN — goal_bearing_modern_eval_v2 (written BEFORE any extraction)

**slug:** `eval_bank_too_small` · **author:** solver session (opus 4.8) · **date:** 2026-08-22

This document states the rubric, the anti-cheat design principle, and the acceptance gates
**before** any item is extracted, per bar #3 ("state the rubric before extracting, not after") and
the contamination rule ("build the items first; if you read the system's per-item output you
disqualify yourself"). Nothing in the build pipeline consults the goal-typing organ's per-item
predictions.

---

## 0. WHAT WAS VERIFIED FIRST (disk outranks the brief)

Re-measured on the existing 36-item scored subset (`outcome_in_lexicon is False`) with
`tools/floor_battery.py`:

- `text_length_chars` = **0.8056**, clears its own permutation null by only **+0.0556** (null p95 0.75).
- `negation_cue_last_sentence` = **0.8056**, clears its own null by **+0.1111** (null p95 0.6944).
- majority floor = 0.6389.

**Both cheats reproduce exactly. The brief is not stale.** The negation cheat is the *stronger* of
the two (bigger margin over its own null).

**Why they work (measured, 2x2 on the 36):**

| | negation in final sentence: NO | YES |
|---|---|---|
| **MET** (23) | 22 | 1 |
| **UNMET** (13) | 7 | 6 |

- Negation-in-resolution is an UNMET tell: P(neg\|UNMET)=0.46 vs P(neg\|MET)=0.04.
- Length: MET mean 411 chars vs UNMET mean 340 (+20.7%).

Both are the same underlying fact about narrative prose: **a failed goal is narrated tersely and
often with explicit negation ("But she couldn't."), a fulfilled one is narrated at length and
affirmatively.** This may be a property of the TASK, not just this bank (brief failure mode (a)) —
which is exactly why it must be *designed against by selection* and *reported beside every number*,
not assumed away.

---

## 1. HOW A READER ACTUALLY RESOLVES THIS (the north star, and why it dictates the design)

A human decides whether a character got what they wanted by building a **situation model** (Zwaan &
Radvansky; Kintsch construction-integration): they represent the goal as a desired state, integrate
the subsequent events, and check whether the resulting state **satisfies or violates** that desired
state. This is a *relational* judgment ("earned a prize" vs "earned a scolding" — the polarity is in
the earn-vs-goal relation, not in the verb), and it is exactly the capability the line of work is
trying to measure.

Length and negation-word counts are **surface features of the text stream**, not of the situation
model. A reader who has understood the passage is not helped by, and not fooled by, either one.
Therefore **a valid eval must make the surface features uninformative**, so that only a genuine
goal-outcome integration separates the classes. That is the single design principle below.

**Consequence:** the eval is not "harder text" — it is text where the surface shortcuts point the
*wrong* way or *nowhere*. Concretely: fulfilled goals that are stated with negation ("she was **no**
longer afraid"; "**nothing** could stop her now"), and failed goals stated affirmatively and at
length ("he turned and walked away, leaving the medal on the table").

---

## 2. THE RUBRIC (reused verbatim from the 2026-08-06 build, which worked once)

A candidate unit is CLEAN + ANNOTATABLE iff **all** hold:

1. **one identifiable roster entity has a goal** — explicit desiderative, or a clearly goal-directed
   action;
2. the **same short passage** contains a clause that **unambiguously MEETS or fails to meet** that
   goal;
3. the **outcome's owner is resolvable from the passage alone** (simple coref is fine; cross-chapter
   tracking is not);
4. trimmable to **2–6 sentences / ≤150 words** while staying self-contained and citable to a line
   range;
5. **trap structure recorded honestly as found, never manufactured.**

**Gold labels (goal, owner, outcome verb lemma, MET/UNMET) are fixed by textual entailment BEFORE
any organ code runs.** MET means the passage entails the desired state was achieved; UNMET means it
entails the desired state was not achieved (or was thwarted). If entailment is ambiguous, the item
is REJECTED, not guessed.

**Structural roster-key gate (required — 7 of the original 44 failed it and were repaired):** every
roster key, `goal_owner`, and `gold_outcome_owner` must be a **single literal alpha token that
occurs in the item's own trimmed text**. `mr_laurence` never matches anything and silently zeroes
every positional baseline for that item; normalize to `laurence`.

---

## 3. THE ANTI-CHEAT DESIGN PRINCIPLE (the actual difficulty of this job)

The final assembled scored subset must satisfy, **as a global property enforced by code**, not by
hope:

- **A. Negation ⊥ label.** The rate of negation-in-resolution must be ~equal across MET and UNMET,
  so `negation_cue_last_sentence` (and `_whole_text`) sit at their own permutation nulls. Achieved
  by deliberately over-sourcing the two rare quadrants: **MET-with-negation** and
  **UNMET-without-negation**, then balancing by selection.
- **B. Length ⊥ label.** The MET and UNMET char-length distributions must be statistically
  indistinguishable (target: `text_length_chars` sits at its own null; two-sided difference-in-means
  permutation p > ~0.2). Achieved by (i) trimming every item to the same 2–6-sentence envelope and
  (ii) selecting so long-UNMET and short-MET are represented, *not* by padding UNMET artificially.
- **C. Report, do not hide, the residual.** If the pool cannot supply enough of a rare quadrant to
  balance, that shortfall is a **finding about the task** (failure mode (a)), reported with the
  per-quadrant yield — not silently absorbed.

**The acceptance test is `tools/floor_battery.py` on the NEW bank: `text_length_chars` and the
negation counter must have `clears_own_null == False` (i.e. sit at their nulls), not merely
`clears_majority`.** `clears_majority` alone flatters (quote_marks/comma_count "beat majority" while
sitting at their nulls).

---

## 4. THE PIPELINE (no organ output touched at any stage)

1. **MINE (code, `verification/` / `scratch/`):** deterministic miner over each corpus finds
   goal-marker sentences and emits **verbatim** candidate windows (real text + exact line range).
   No LLM, so text and citations cannot be hallucinated.
2. **ANNOTATE (subagents, judgment):** each candidate window is judged against the rubric →
   REJECT, or produce a clean item with gold fixed by entailment + honest cheat metadata
   (negation-in-resolution y/n) + entailment justification. Briefs forbid reading any organ output
   and carry the standing denial-disclosure rule. Rare quadrants are prioritized.
3. **GATE (code):** verbatim-substring gate (kills any hallucinated/paraphrased text), roster-key
   structural gate, dedup vs v1, entailment spot-check by the solver on a sample.
4. **CURATE (code):** select ≥120 scorable items so length ⊥ label and negation ⊥ label; iterate
   against `floor_battery` until both cheats sit at their nulls.
5. **BASELINES (code, reads `hdlab.goal_owner_select` resolver — READ ONLY, never written):** four
   positional baselines + how many items defeat all four simultaneously; write
   `data/goal_bearing_modern_eval_v2_baselines.json`.

**"Scorable"** = the `outcome_in_lexicon is False` subset, matching v1's definition, so the count is
apples-to-apples with the current 36. Target ≥120 in that subset.

---

## 5. HOW WE WOULD KNOW IT FAILED (from the brief — planned for, not feared)

- **(a) cheats survive at scale** → finding about the TASK (goal fulfilment is length/negation
  correlated in prose). Report per-quadrant yield and stop.
- **(b) not enough clean items** → report yield per corpus; that bounds every future plan.
- **(c) items clean but artificial** → a bank no positional baseline can touch may not resemble
  reading. Flag the trade-off explicitly; do not silently choose.
- **(d) organ per-item output read during build** → bank contaminated; hand over diagnostic-only.
  *Mitigation: the pipeline never calls the organ. Enforced by not importing it.*

---

## 6. WHAT COUNTS AS DONE

`experiments/data/goal_bearing_modern_eval_v2.jsonl` with ≥120 scorable items;
`data/goal_bearing_modern_eval_v2_baselines.json`; both cheats at their nulls on the new bank
(reported with margins and how many items each control removed); fairness reported honestly incl.
the all-four-baselines-defeated count; population saved, not just counts.
