# ANNOTATION BRIEF — goal-outcome eval items (READ FULLY, take your time, do not truncate)

You are annotating candidate passages for a reading-comprehension eval: **can a reader tell whether a
character got what they wanted?** Your job is to turn RAW candidate windows into clean, gold-labelled
items, or reject them. Quality matters far more than quantity — a rejected junk candidate costs
nothing; a mislabelled kept item corrupts a durable benchmark.

## HARD RULES (violating any invalidates your whole batch)

1. **Judge ONLY from the passage text.** Do NOT run, import, read, or consult ANY model, organ,
   classifier, `verb_lexical_similarity`, goal-typing / outcome-valence code, or its outputs. Fix
   every label by **textual entailment from the words on the page**, nothing else.
2. **`text` must be VERBATIM.** You may TRIM (drop leading/trailing sentences or a dangling partial
   sentence) but you must NOT paraphrase, reorder, insert, or "fix" wording. The kept `text` must be
   a contiguous span copied from the candidate window. (A machine gate re-checks this against the
   source and drops any item that fails.)
3. **The outcome owner's NAME must appear as a literal word in `text`.** Roster keys, `goal_owner`,
   and `gold_outcome_owner` must each be a single lowercase alphabetic token (`jo`, `laurie`,
   `carson`) that OCCURS in `text`. If the passage only ever refers to the owner by a pronoun
   (he/she/they) and no name appears anywhere in the candidate window, **REJECT it** — do not invent
   a name. If a name appears elsewhere in the SAME window, extend your trim to include it.
4. **If a tool call is denied, STOP and report the exact denial text verbatim.** Do not retry a
   variant; do not silently proceed.

## THE RUBRIC — keep an item ONLY if ALL FIVE hold

1. **One identifiable roster entity has a goal** — an explicit desiderative (want/wish/hope/resolve/
   determine/decide/vow/promise/intend/long-to...) OR a clearly goal-directed action.
2. The **same short passage** contains a clause that **unambiguously MEETS or FAILS to meet** that
   goal. If you have to guess, or it needs later chapters, REJECT.
3. The **outcome's owner is resolvable from the passage alone** (simple pronoun coref is fine).
4. Trim to **2–6 sentences / ≤150 words**, self-contained.
5. **Record trap structure honestly as found. NEVER manufacture it.**

## GOLD LABEL — fix by entailment, write the justification

- `gold_outcome_polarity` = **"met"** iff the passage entails the desired state was ACHIEVED;
  **"unmet"** iff it entails the desired state was NOT achieved / was thwarted / abandoned.
- Give a one-line `entailment`: quote the goal clause, quote the outcome clause, state why it forces
  met/unmet. If you cannot write that line cleanly, the item is not clean — REJECT.

## WHAT TO PRIORITIZE (this is why the batch exists)

The existing bank has a cheat: failed goals are narrated tersely and with negation words ("But she
couldn't."), succeeded goals at length and affirmatively. So please **especially keep**, when they
occur naturally and unambiguously:
- **MET outcomes phrased WITH negation** — e.g. "she was **no** longer afraid", "**nothing** could
  stop her now", "he **never** doubted again" (goal achieved, negation words present).
- **UNMET outcomes phrased affirmatively and at length** — e.g. "he turned and walked away, leaving
  the medal on the table" (goal failed, no negation, several clauses).
Set `resolution_has_negation` honestly (does the OUTCOME sentence contain no/not/never/failed/
refuse/cannot/none/nothing?). Never relabel an item to fit a quadrant — honesty first.

## OUTPUT — write JSONL, one line per candidate, to your given output path

For a KEPT item:
```json
{"cand_id":"c0009","keep":true,"id":"race_carson_writer_award",
 "text":"<verbatim trimmed span>","roster":{"carson":"f"},
 "goal_owner":"carson","goal_text":"she decided she wanted to be a writer","goal_verb_lemma":"want",
 "outcome_verb_lemma":"win","gold_outcome_owner":"carson","gold_outcome_polarity":"met",
 "entailment":"Goal: wanted to be a writer. Outcome: her book won the National Book Award -> she became a published, prize-winning writer -> MET.",
 "trap_type":"natural","difficulty":"easy","resolution_has_negation":false,
 "corpus":"<copy corpus_file from input>","line_citation":"<copy source from input>","notes":""}
```
`trap_type` ∈ {natural, recency_trap, distractor_between}: `recency_trap` = a DIFFERENT entity is
mentioned more recently than the owner at the resolution; `distractor_between` = another entity's
action/speech sits between goal and outcome; `natural` = owner is also the obvious positional guess.
`difficulty` ∈ {easy, medium, hard} — your honest read of how hard the owner+valence are to get.

For a REJECTED candidate:
```json
{"cand_id":"c0007","keep":false,"reject_reason":"no clear goal — dialogue filler"}
```

**Emit exactly one line per input candidate (kept or rejected), same cand_id.** Roster values are
"m"/"f" gender guesses (used only for pronoun resolution; a wrong guess is harmless). Prefer specific
outcome verbs over generic win/lose/fail where the text offers one. Work through every candidate;
do not stop early or summarize instead of emitting rows.
