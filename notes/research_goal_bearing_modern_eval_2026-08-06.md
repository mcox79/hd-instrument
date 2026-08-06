# Research note: a fair, modern, goal-bearing eval for goal-owner + outcome-valence typing

Filed by: research (Sonnet), 2026-08-06. Replaces `experiments/data/real_text_goal_owner_diagnostic_v1.jsonl`
(10 hand-picked McGuffey items) as the real-text generalization diagnostic for the goal-owner-select
+ outcome-valence-congruence organs.

## HEADLINE

We are NOT data-starved for this eval. Seven already-on-disk corpora (5 goal-dense public-domain
novels + RACE + OneStop, none McGuffey) yielded **44 clean, hand-verified goal->attempt->outcome
narrative units** against a written, non-circular rubric -- more than the ~30-40 target, gathered by
four parallel corpus surveys. 82% of items (36/44) have an outcome verb that is OOV of the current
`hdlab.verb_lexical_similarity` outcome lexicon, i.e. they specifically probe the open-vocab
goal-relative typing gap the 2026-08-06 acquisition-increment-1 drill diagnosed. But the fairness
picture is mixed and must be reported honestly: **real narrative prose is much harder to make
"fully fair" than a hand-authored instrument.** `nearest_subject` sits near floor (0.30 overall,
0.25 on the trap subset) but `first_mention` (0.80 overall, 0.75 trap) and `majority` (0.73 overall,
0.67 trap) stay uncomfortably high, because in real prose the goal-owner is usually also the
passage's protagonist -- introduced first and mentioned most -- even in passages engineered to
defeat pure last-mention recency. Only 5/44 items defeat all four baselines simultaneously. This is
a real, structural property of narrative text (not a construction bug) and is reported as the
central fairness finding below, with a recommended discriminating subset.

## Trigger / why this exists

`notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` (ACQUISITION INCREMENT 1 entry): the
increment-1 acquisition test failed (HARD_FAIL) because it tested a goal-CONGRUENCE mechanism on
bare, goal-less clauses -- outcome valence is RELATIONAL ("earned a prize" vs "earned a scolding":
polarity is not in "earn", it's in the earn-vs-goal relation). USER steer (2026-08-06): make the eval
FAIR, drop McGuffey because it's ~170 years old, and empirically answer "do we have enough data."
This note answers that, then delivers the eval itself.

## STEP 1 -- goal-density survey (the "do we have enough" answer)

Four parallel Sonnet sub-agents each independently surveyed a slice of the candidate corpora,
applying the SAME written rubric (below) *before* looking at any organ output. Combined they read
~140 tool-calls worth of primary text (grep + close reads) across all 7 candidates named in the
task brief.

### Rubric applied (stated before any extraction)

A candidate unit is CLEAN + ANNOTATABLE iff: (1) one identifiable roster entity has a goal
(explicit desiderative, or a clearly goal-directed action); (2) the same short passage contains a
clause that unambiguously MEETS or fails to meet that goal; (3) the outcome's owner is resolvable
from the passage alone (simple coref is fine, cross-chapter tracking is not); (4) the unit can be
trimmed to roughly 2-6 sentences / <=150 words while staying self-contained and citable to a line
range; (5) trap structure (or its absence) is recorded honestly as found, never manufactured. Gold
labels (goal, owner, outcome verb lemma, MET/UNMET) were fixed by textual entailment before any
organ code ran.

### Per-corpus density + annotatability (measured, not estimated)

| Corpus | Era | Raw goal-marker hits (grep) | Clean units extracted | Verdict |
|---|---|---|---|---|
| `little_women` | 1868 novel | 168 | 12 | Richest source; could extend to 18-20+ with more budget |
| `anne_of_green_gables` | 1908 novel | 84 (106 w/ broader marker set) | 12 | Very rich; dense recurring cast makes natural traps common (not manufactured) |
| `tom_sawyer` | 1876 novel | 52 | 5 | Rich; strongest "gardener-pattern" owner/subject-mismatch items (whitewash fence, Becky's flogging) |
| `wizard_of_oz` | 1900 novel | 19 | 5 | Hidden strong source despite low raw count -- the 4-companion quest structure (brains/heart/courage/home) is the single richest naturally-occurring recency-trap vein found anywhere: 3 companions' wishes are resolved back-to-back in one chapter |
| `alice_in_wonderland` | 1865 novel | 15 | 1 (of 2 found; 1 kept) | Mostly NOT viable -- confirmed hypothesis. Nearly all desiderative hits are momentary/interrupted-by-nonsense or never resolved. One genuine multi-chapter exception (the "beautiful garden" arc) was found and kept; do not route further budget here. |
| RACE (`middle_test`+`high_test`) | 2017 dataset, contemporary-language passages | 290 across 1407 unique articles, ~220 articles with >=1 hit | 4 | Genuinely modern; needs hand-filtering (roughly half of marker-hit articles are essays/expository with no crisp resolution), but clears the bar -- more (30-60 est.) extractable with further budget |
| OneStop (`Ele-Txt`) | 2012-2015 news, graded-simplified | 52 across 189 files, 38 files w/ >=1 hit | 5 | Bimodal: human-interest profile pieces (1 named person, explicit want -> explicit resolution) are as clean as anything in this eval and genuinely contemporary; the majority-class policy/informational pieces fail the rubric exactly as the task brief predicted (no resolution, or a vague-crowd/organization "owner") |

**Answer to "do we have enough": yes, comfortably.** The combined pool is 44 clean items (dropped
from an original 45-candidate draft after a structural roster/text sanity gate removed and then
repaired all but zero -- see Step 2). None of the goal-dense novels turned out too hard to extract
from cleanly enough to abandon; Alice was the one predicted casualty and it was honestly flagged
and mostly excluded rather than forced. RACE/OneStop supply the genuinely-modern slice the task
explicitly asked for as a fallback -- they were not needed as a fallback (the novels alone would
have cleared 30 items) but are included because they materially improve the era-diversity honesty
of the instrument.

**Honest caveat on "modern":** the recommendation deliberately mixes two answers to "old McGuffey."
5 corpora are pre-1923 public-domain NOVELS (not modern by publication date), but they are *real
literary narrative prose*, not a 19th-century pedagogical basal reader built from short, stilted,
uniformly-moralizing drill paragraphs the way McGuffey is -- this is the meaningful axis the
increment-1 drill's complaint was actually about (construction diversity + real narrative
indirection, not literally publication year). 9 items (RACE + OneStop, ~20% of the set) are
genuinely contemporary (2012-2017) in both language and subject matter (a skydiving record, a
Chinese PE exam, a crowdfunding campaign, Wiffle balls) and are flagged as such per-item.

## STEP 2 -- the assembled eval

`experiments/data/goal_bearing_modern_eval_v1.jsonl` -- **44 items**, schema matching
`real_text_goal_owner_diagnostic_v1.jsonl` (`roster`, `gold_outcome_owner`, `gold_outcome_polarity`,
`text`) plus: `goal_owner`, `goal_text`, `goal_verb_lemma`, `goal_in_lexicon`, `outcome_verb_lemma`,
`outcome_in_lexicon`, `trap_type` (`natural` / `recency_trap` / `distractor_between`),
`difficulty` (`easy`/`medium`/`hard`), `corpus`, `line_citation`, `notes`.

Construction note on roster keys: `hdlab.goal_owner_select`'s structural resolvers tokenize text
with `[a-z']+`, so a roster key must be a single literal alpha token that actually occurs in the
item's own trimmed text (a key like `mr_laurence` or `aunt_polly` never matches anything and would
silently zero out every positional baseline for that item). All 44 items were passed through an
automated structural gate that normalizes compound keys to their matching single-token form (e.g.
`mr_laurence` -> `laurence`, `aunt_polly` -> `polly`) and verifies both `goal_owner` and
`gold_outcome_owner` are literal, present roster keys; 7 of the original 44 candidates initially
failed this gate (their trimmed excerpt had elided the character's own name, e.g. all-dialogue or
pronoun-only mentions) and were repaired by restoring one literal name mention rather than dropped,
since the underlying passages were good. Bracketed clauses like `[Glinda in turn grants the
Scarecrow's, Tin Woodman's, and Lion's own wishes...]` in 2 items are director/agent-authored
scene-bridging summaries (clearly delimited), not verbatim source text -- everything outside
brackets is verbatim-or-lightly-trimmed quotation with a line citation.

### OOV-outcome-verb fraction

**36/44 = 0.818** of items have an outcome verb OOV of `hdlab.verb_lexical_similarity`'s current
99-word outcome lexicon (verified by calling `in_lexicon(lemma, "outcome")` directly, not
estimated). 8 items are deliberately in-lexicon as sanity-check controls (`forgive`, `win`,
`reach`, `break`, `punish`, `escape` appear as outcome verbs across those 8). Goal-verb OOV is
lower (most goal verbs -- want/wish/hope/try/mean/determine/decide -- are common enough to already
be lexicon members); several items also use goal verbs not currently in the goal lexicon at all
(`persuade`, `apologize`, `avoid`, `like`, `love`, `make`) which is a secondary, smaller coverage
gap worth noting for a future goal-lexicon expansion pass.

### Polarity and trap-structure distribution (honest, not engineered to a round split)

- Polarity: 27 MET / 17 UNMET (61% / 39%) -- skews MET because "the goal succeeds" is simply the
  more common resolution shape in children's/YA narrative and human-interest journalism; not
  balanced 50/50 by construction, reported as found.
- Trap type: 20 `natural` (goal-owner coincides with the naive positional guess), 14
  `distractor_between` (another named entity's action/speech intervenes between goal and outcome
  without being the true owner), 10 `recency_trap` (a different entity is more recently mentioned
  than the goal-owner at the point of resolution). 0 items were manufactured to hit a target split
  -- this is what the surveys actually found. `distractor_between` was in practice much easier to
  find naturally than pure `recency_trap`, because real multi-character scenes very often have a
  third party's action sit between a stated goal and its resolution (the "gardener let him in"
  pattern), whereas a resolution-sentence that names a DIFFERENT character than the goal-holder
  with no third party in between (pure recency swap) is a narrower naturally-occurring shape.

## FAIRNESS -- the load-bearing bar, reported honestly

All 4 positional baselines computed structurally and independently of any goal-typing lexicon
(reusing the PRODUCTION, bug-fixed `hdlab.goal_owner_select.GeneralRecencyEntityResolver` /
`_sentences` / `_ordered_tokens` verbatim -- byte-identical mechanism to what the fair-instrument
harness `experiments/exp_c5_fair_goal_owner_primacy_v1.py` uses, generalized to items of varying
sentence count rather than the fixed 3-4-sentence vignette shape): `recency` = last-mentioned
roster entity anywhere in the passage; `first_mention` = first-mentioned roster entity;
`nearest_subject` = the structurally-resolved subject of the sentence immediately preceding the
(final/outcome) sentence; `majority` = most-frequently-named entity, ties broken by earliest
mention.

| Baseline | Overall (N=44) | Trap subset (N=24) | Natural subset (N=20) |
|---|---|---|---|
| recency | 0.568 | 0.500 | 0.650 |
| first_mention | **0.795** | **0.750** | 0.850 |
| nearest_subject | 0.295 | **0.250** | 0.350 |
| majority | 0.727 | 0.667 | 0.800 |

**Do not read this as "fair" the way `goal_owner_fair_v1.jsonl` (all 4 baselines at 0.0) is fair.**
It is not, and hiding that would defeat the point of the exercise. The honest finding: `recency`
and `nearest_subject` are meaningfully suppressed on the trap subset (0.50 and 0.25), confirming
the trap construction worked for the mechanism it specifically targeted -- but `first_mention`
(0.75) and `majority` (0.67) stay high even on trap items. **Root cause, item-by-item traced:** in
real narrative prose, the goal-owner is almost always also the passage's PROTAGONIST -- the
character the excerpt is centrally about, hence introduced first and named most -- even in a
passage explicitly constructed to defeat last-mention recency (e.g. `agg_gilbert_porch_apology_ch15`:
Gilbert is the goal-owner AND the first name in the passage AND the more-frequently-named entity,
even though Anne is the more-recently-active/speaking character at the resolution). This is a
structural property of how narrative prose is written (protagonist-centric), not a construction
bug -- and it is exactly the property the *hand-authored* `goal_owner_fair_v1.jsonl` was
deliberately engineered to break (its foil is made BOTH more recent AND, in the primacy-trap half,
first-mentioned, so no single positional prior wins). Real prose does not hand you that for free.

**The genuinely fully-fair discriminating subset:** 5/44 items defeat all four baselines
simultaneously (`lw_ice_rescue_amy`, `lw_laurie_proposal_rejected`, `agg_anne_diana_bosom_friend_ch12`,
`agg_anne_avery_scholarship_gilbert_medal_ch36`, `agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17`);
12/44 have at most 1 of 4 baselines correct. These are the items where a genuine capability win is
unambiguous. Recommendation for anyone scoring the organ against this eval: report the full-44
number (coverage/OOV story) AND the 12-item hardest-subset number (the "beats every position
heuristic" story) separately, exactly as `goal_owner_fair_v1.jsonl`'s harness already does for
`system_accuracy` vs `max_baseline`. Full per-item baseline predictions (all 4 baselines x all 44
items) are in `data/goal_bearing_modern_eval_v1_baselines.json`.

## Falsifiable predictions (for whoever runs increment 1b against this eval)

- **HARD-PASS:** the composed organ (`select_outcome_owner` + `congruence_with_lexicon_fallback`)
  beats `nearest_subject` (0.295 overall / 0.25 trap) by a material margin (>=0.15 absolute) on
  the full 44-item set, AND beats ALL FOUR baselines on the 12-item hardest-subset, AND scramble
  (goal relabeled to foil) collapses the gain by >=50%.
- **HARD-FAIL:** organ accuracy on the 5-item fully-fair subset is <= `max(baseline accuracies)` on
  that subset (i.e. it doesn't even clear the weakest positional heuristic on the items designed to
  have no positional heuristic available), OR `OUTCOME_NEVER_TYPED` fires on >40% of the 36
  OOV-outcome items (i.e. Tier-2 concept-similarity verb-typing doesn't generalize past its
  training/seed set to this corpus-drawn OOV vocabulary).
- Per lit-scan calibration discipline: this is real-text generalization measurement, not a novel
  synthesis claim, so no P-estimate deflation applies here (this note delivers DATA, not a
  probability-of-mechanism-success claim) -- but the mechanism-side P estimate for increment 1b
  clearing HARD-PASS should be treated as P<=0.50 (capped, novel-synthesis-adjacent: the Tier-2
  verb-similarity organ has only been validated on hand-tagged seed vocabulary + one 10-item real
  probe so far, not on a 44-item, 7-corpus-diverse OOV set like this one).

## Cross-thread synthesis

Directly continues the 2026-08-06 arc in `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`:
generalization probe (organ 0.30 vs recency 0.70 on 10 McGuffey items) -> open-vocab verb-typing
fix (owner-acc 0.30->0.50 on the same 10 items) -> USER steer (fair + modern + "do we have
enough") -> this note (yes, 44 items, but the fairness bar itself is harder to clear on real prose
than the hand-authored instrument, and that gap is itself informative about what "generalization"
will cost).

## Substrate-product implications

This is the eval increment 1b needs to be measured against once built -- not a new capability
claim itself. Product-relevant implication: the fairness finding (protagonist-centricity beats
naive positional priors on real text) means a production reading system cannot rely on
"first-mentioned wins" as an implicit fallback either -- it will look deceptively strong on natural
prose (85% on the natural subset here) while being structurally uninformative, exactly the trap the
increment-1 HARD_FAIL warned about for a different mechanism (Channel A carrying zero real signal
while still scoring on majority-class artifact). Any future real-prose eval for this organ family
should report the fully-fair subset number as the headline capability metric, not the full-set
number, to avoid the same self-flattering-baseline failure mode.

## Citations (verified count)

0 external literature citations (this is a corpus-construction + measurement note, not a
lit-scan). All numbers in this note are computed directly off disk: `in_lexicon()` calls against
`hdlab/verb_lexical_similarity.py`, grep counts against the corpora files under
`data/corpora/`, and the baseline table from a from-scratch structural computation reusing
`hdlab.goal_owner_select`'s production resolver verbatim (script:
`data/goal_bearing_modern_eval_v1_baselines.json` is the full machine-readable output; the
assembly + baseline scripts used are not committed, this note and the two data files are the
durable artifacts).
