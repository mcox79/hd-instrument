# SCORECARD -- how well the reading system is doing, in plain language

Kept up to date by the strategy session after every landing and every full check. The sections below the line
are written by hand; the table at the bottom is generated from the measurements on disk by `tools/scorecard.py`
(the owner's window `tools/scorecard_gui.py` shows both).

## THE SHORT VERSION
The system reads ordinary modern English and builds a running picture of who is who, who did what to whom, what
things are like, which meaning of each word is meant, and how events relate in time, place and cause. On the
seven headline abilities it is clearly better than a simple rule on five; on "who did the action" a plain
word-order rule is already near-perfect on modern prose so there is nothing to beat, and on "which character is
the passage about" it is better but the test set is small. Today's big step: the system now works out what a
NEW word means from what it reads, using its sense of how things feel and look, and it gets the right meaning
near the top about 38 times in 100 where the old method managed about 3.

## WHAT CHANGED LATELY
- 2026-09-12 (night): the wall left open earlier tonight is overcome. For helped-or-harmed, the reader now judges the STATE a person
  is left in (struck, strangled, injured), read from what the verb means in that sense, instead of how the word feels; how the word
  feels is only the second opinion. Batter, bludgeon, pummel, club and throttle are now judged 'harmed' (throttle and club used to be
  judged 'helped' because of their engine and golf senses); 31 other verbs that used to get no judgement now do; nothing neutral was
  mis-read; a scrambled control fails. Full check: pooled AGG 0.6408 -> 0.6408 (every dimension identical); helped-or-harmed 35/36 -> 36/36 (0.972 -> 1.000, twin 0.694); who-was-affected 0.387 unchanged; no regression. Two verbs (wrench, maul) still get
  no judgement because our reference names no result state for them; recorded honestly for the fleet.
- 2026-09-12 (overnight): helped-or-harmed judgements now come from the brain's own computation (how the force acts, how
  the outcome feels for the person affected, whether they were truly affected) instead of a fixed word list; 97 in 100 on the
  36-sentence test (was 78), scrambled control 58. Two upstream fixes came with it (a noun mistaken for an adjective after
  'the' is corrected; the subject of a passive sentence is labelled as the one acted on), and passive sentences now reach the
  judgement. Stand-ins fell from 7 to 6. A 'what kinds of things a verb acts on' knowledge organ was added (kept in reserve
  for the 'what happens next' model, because on its own it measured no better than grammar).
- 2026-09-11 (late): the pronoun-picker carried its own copy of the "how recent and how prominent was it" rule; it now uses
  the one shared rule every other part uses. Same answers on every check.
- 2026-09-11 (late): the three time-ordering components were merged into one, with identical results on every check (the
  brain keeps one sense of event order; we had three copies). Second duplicate-part merge done; next are salience, force, appraisal.
- 2026-09-11: learning word meanings from reading is now live and measured (38 in 100, old method 3 in 100); the
  word-meaning test now scores the real reading path (75 in 100 vs 50 for guessing); a second test of how meaning
  shifts with context was added. Pooled headline score rose 0.625 -> 0.641, entirely from the better word-meaning
  test, not from a change to the reader.
- 2026-09-11: six separate "who is this referring to" components were merged into one, with identical results.

## WHAT WE ARE WORKING ON
Short term (the next week or two):
- (Done 2026-09-12) The three finished pieces were folded in: helped-or-harmed, the part-of-speech finding, the verb-type organ.
- (Done 2026-09-12, night) The assault-verb wall: the reader now values the state the person ends up in (researched and built the same night).
- One shared "meaning store" that every part of the reader uses, instead of six separate copies (the brain keeps
  one). A strict pre-registered test decides whether the merged store is at least as good as the best copy.
- Replace the one remaining outside dictionary tool the reader calls while reading with our own word-stemming.
- (Done 2026-09-12) Checked every remaining suspected duplicate: time ordering merged; the recency rule single-sourced; roles, force and
  appraisal turned out NOT to be duplicates (each is one computation reused by import) — the audit was corrected.
- After every landing: a full check, and this scorecard updated.
Long term (the next few months):
- The generative "what happens next" model: the reader predicts the story as it goes, using the new in-context word
  meanings, and uses the prediction to resolve who is who and what caused what. This is where the remaining
  headroom is; the current parts are measured to their ceiling.
- Grounding beyond text: real perceptual and experiential knowledge (pictures today; more senses later) feeding the
  one shared meaning store, so meaning is not built from word company alone.
- Replace the sentence-structure stand-in with the reading-learned version once it matches on real prose.
- Every building block copying the brain's math, not just a defensible model: today 7 of 86 are pinned; each
  landing must move a part from "model" to "pinned" or remove a stand-in.

## WHAT IS NOT YET BRAIN-FAITHFUL
- The sentence-structure reader (five building blocks) is a trained stand-in, not the brain's method. A
  reading-learned replacement exists and matches it on familiar text; switching it on is a posted problem.
- Helped-or-harmed now reads the state a person is left in, but only where our reference names that state (about 1 verb in 25 of
  the verbs that act on people; the rest still rely on how the word feels, and 822 of 2,926 get no judgement). Picking WHICH sense of
  the verb applies from the sentence, rather than from the verb alone, is the next step (posted as the remaining scope of the problem).
- The "same dog as before" check still uses a surface-string component in one place; its replacement is awaiting review.
- The word-stemmer calls an outside dictionary tool while reading (computation right, implementation not ours).
- The rule for combining the senses when learning a word is a reasonable model, not yet pinned to the brain; the
  shared-meaning-store work above is designed to settle it.

<!-- AUTO:BEGIN (written by tools/scorecard.py; edit the sections ABOVE, not this) -->

Last full check: 2026-09-12T04:15:39.605699+00:00 (3 on record). Generated 2026-09-12T04:16:59+00:00.

| Ability | Group | How well | Compared with a simple rule | Since the previous check | Brain-faithful? |
|---|---|---|---|---|---|
| Whether 'the dog' is the same dog mentioned earlier | People and things | right 57 in 100 | clearly better than the simple rule (54 in 100) | unchanged since the previous check | brain model; some details still open |
| Which character the passage is mainly about | People and things | right 26 in 100 | a little better than the simple rule (20 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Who 'he / she / it / they' refers to | People and things | right 47 in 100 | clearly better than the simple rule (36 in 100) | unchanged since the previous check | brain model; some details still open |
| Linking a description ('the painter') to a named person | People and things | right 55 in 100 | clearly better than the simple rule (45 in 100) | unchanged since the previous check | brain model; some details still open |
| Pronoun reference as the full reader actually runs it | People and things | right 59 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Resolving 'the animal' to the dog just mentioned | People and things | right 58 in 100 | clearly better than the simple rule (52 in 100) | unchanged since the previous check | brain model; some details still open |
| Who was affected by what happened | People and things | right 39 in 100 | clearly better than the simple rule (34 in 100) | unchanged since the previous check | brain model; some details still open |
| Which meaning of a word is meant in this sentence | Word meaning | right 75 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Drawing safe conclusions from 'is a kind of' facts | Word meaning | right 77 in 100 | clearly better than the simple rule (54 in 100) | unchanged since the previous check | brain model; some details still open |
| Handling 'all / some / none' correctly | Word meaning | right 83 in 100 | clearly better than the simple rule (17 in 100) | unchanged since the previous check | brain model; some details still open |
| Handling 'not' correctly | Word meaning | right 93 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| How a word's meaning shifts with its context (graded) | Word meaning | agreement with people 0.39 (out of 1) | clearly better than the simple rule (0.38) | unchanged since the previous check | brain model; some details still open |
| Picking the right broad sense of an ambiguous word (older test set) | Word meaning | right 52 in 100 | clearly better than the simple rule (35 in 100) | unchanged since the previous check | brain model; some details still open |
| What something is or is like ('the sky is blue') | Actions and roles | right 83 in 100 | clearly better than the simple rule (57 in 100) | unchanged since the previous check | brain model; some details still open |
| Who did the action in a sentence | Actions and roles | right 83 in 100 | not better than the simple rule (85 in 100) yet | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Who or what the action was done to | Actions and roles | right 83 in 100 | clearly better than the simple rule (75 in 100) | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Keeping a fact true until something changes it | Actions and roles | right 100 in 100 | clearly better than the simple rule (44 in 100) | unchanged since the previous check | brain model; some details still open |
| Event order when the text does not say it outright | Time and place | right 57 in 100 | clearly better than the simple rule (53 in 100) | unchanged since the previous check | brain model; some details still open |
| Noticing where one scene ends and another begins | Time and place | right 12 in 100 | a little better than the simple rule (7 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Picking out place information correctly | Time and place | right 59 in 100 | clearly better than the simple rule (51 in 100) | unchanged since the previous check | brain model; some details still open |
| Where things are relative to each other | Time and place | right 28 in 100 | clearly better than the simple rule (22 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether a state still holds at a later point | Time and place | right 41 in 100 | clearly better than the simple rule (11 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether two events happened at the same time | Time and place | right 99 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Which of two events came first | Time and place | right 59 in 100 | clearly better than the simple rule (52 in 100) | unchanged since the previous check | brain model; some details still open |
| Answering 'why' when the cause is sentences away | Causes | right 23 in 100 | clearly better than the simple rule (0 in 100) | unchanged since the previous check | brain model; some details still open |
| Following a chain of causes across several steps | Causes | right 26 in 100 | clearly better than the simple rule (0 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether a cause makes an effect bigger or smaller | Causes | right 62 in 100 | a little better than the simple rule (61 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Whether one event was needed for another to happen | Causes | right 36 in 100 | clearly better than the simple rule (4 in 100) | unchanged since the previous check | brain model; some details still open |
| How a character probably feels about an event | Feelings, goals, beliefs | right 94 in 100 | clearly better than the simple rule (44 in 100) | unchanged since the previous check | brain model; some details still open |
| What a character believes, even when it is false | Feelings, goals, beliefs | right 65 in 100 | clearly better than the simple rule (49 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether an action helped or harmed someone | Feelings, goals, beliefs | right 100 in 100 | clearly better than the simple rule (33 in 100) | up 0.028 since the previous check | brain model; some details still open |
| Whether an event helps or blocks a character's goal | Feelings, goals, beliefs | right 98 in 100 | clearly better than the simple rule (49 in 100) | unchanged since the previous check | brain model; some details still open |
| Who is having the feeling | Feelings, goals, beliefs | right 20 in 100 | clearly better than the simple rule (14 in 100) | unchanged since the previous check | brain model; some details still open |
| Working out what a new word means from reading | Learning from reading | right meaning ranked near the top 38 in 100 | clearly better than the simple rule (16 in 100) | unchanged since the previous check | brain model; some details still open |
| Knowing when to hold back on 'who was acted on' | Knowing its limits | right 97 in 100 | clearly better than the simple rule (88 in 100) | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Knowing when to hold back on a place or time attachment | Knowing its limits | right 84 in 100 | clearly better than the simple rule (76 in 100) | unchanged since the previous check | uses a stand-in we are replacing |

Brain-faithfulness of the 85 building blocks: 7 copy the brain's math exactly, 72 are brain models with open details, 6 are stand-ins being replaced (arc_labeler, arc_parser, arceager_parser, commonnoun_binder, parse_confidence, pos_tagger).

<!-- AUTO:END -->
