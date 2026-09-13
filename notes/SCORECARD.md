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
- **13 Sep, 17:30 (awaiting your DONE on three solutions).** Three problems were solved today by solver sessions run as agents, with your probing rules applied: (a) the main-statement decision, which had no evidence in it (every verb tied), now competes among candidate predicates; at the landed training size the main word is right 78 times in 100 vs 72 and overall attachment 62.4 vs 61.3, nothing down; (b) harm carried by HOW an action is done (brutalize, manhandle): all six silent verbs read as harm, 46 more verbs decided at 6 of 6 agreement with human judgements, a new 36-sentence prose test from 16 to 23 right; (c) words never seen before: 75 to 80 in 100 right, overall word kinds 92.8 to 93.1; names vs common nouns only 163 to 154 errors because 58 carry no form cue (the fix needs what the passage already knows about the referent; filed as a new problem). I re-ran all three first-hand and every number reproduced. Also found: the 'who did the action' score on this card is computed by a word-order shortcut that never uses the reader's own grammar, which is why it sits just below the plain rule; the reader's own chain scores 0.80 there today vs the rule's 0.84, with the causes counted and handed to the session now working on roles.
- **13 Sep, 14:40.** Full re-check after the last two hand-out solutions were folded in (a verb's slots can each hold one filler, kept switchable and off because it cost the 'who was acted on' read; the reading-learned word classes now feed the live word-category organ): overall score 0.6346 -> 0.6352 out of 1; 'who was acted on' 0.789 -> 0.792, 'what things are like' 0.810 -> 0.815; nothing went down. A try at letting the word-category organ read the neighbouring words as a blanket extra vote was tested on the full test set and REJECTED with numbers (it trades one kind of verb mistake for another); a second form, storing frequent two-word units the way people do, is drafted and waits for your go.

**13 Sep, 13:05.** Final board with everything: 63.5 in 100 (stand-in 63.8). Unchanged from the previous run, so the coordination teaching and lemma-key consistency cost nothing. Nothing running; three hand-outs open (Pri 93, 94, 96).

**13 Sep, early afternoon.** The board is at 63.5 in 100 against 63.8 for the old hand-trained stand-in, with the entire reading chain
brain-foundational and live: word kinds settled in order, roots by the two-route organ, governor in order with decay and clause wrap-up,
roles by a competition whose cue strengths are now learned from the governor's own structures (that last step took who-was-affected
from 73 to 79). State reading equals the stand-in. Your coordination solution is integrated exactly as proposed ('and/or' links 30 to
38 in 100); its frontier, distant coordination, is filed as a meaning problem (Pri 96) in the hand-out tab. Running: a final full
board with everything. Risk: small named give-backs on subjects and clause complements from the coordination teaching signal.

**13 Sep, midday.** The in-order word governor is now the live default and the full board with it came in at 62.8 in 100 (the
whole-sentence search gave 62.2; the old hand-trained stand-in 63.8). State reading is back to the stand-in's level (81); the one
remaining gap is who-was-affected (73 vs 82). A lever for that is measured and queued: when the role-deciding organ learns its cue
strengths from the governor's OWN structures instead of from gold trees, who-was-affected rises from 75 to 79 in 100 on the same
items. Your DONE solution on helped-or-harmed is integrated with every upstream fix it named (35 of 36 live checks hold). Three
defects found on the way were fixed (a lemma collision that turned 'wound' into 'wind'; a crash in predicate recovery; an outdated
test). Two stores keyed on the old lemmatizer were rebuilt and swapped with no change to the board self-test. Running: the full
board with everything landed since 11 o'clock. Risk: the perceived-structure role table deliberately disagrees with textbook
conventions in one constructed case (a root noun read as the subject); the measured consumer gain outweighs it.

**13 Sep, morning (owner awake).** You asked whether organs should take data in, in order. They should, and two did not. (1) The word-kinds
organ settled each word's kind by reading the whole sentence first; it now settles it as the word arrives and revises it with the next two
words only. Measured on the full test set that is exactly as accurate (92.6 in 100 either way; no revision at all would cost 2.3 points) and
just as fast, so it is now the default. (2) The word-governor organ chose its structure by a whole-sentence search; it now has an arm that
attaches each word as it arrives, holding a word on a learned expectation when its governor has not come yet, with a handful of alternatives
alive. That arm scores 59.7 in 100 against 60.3 for the search: better on objects (75 vs 73) and noun modifiers (40 vs 37), worse on the
sentence's main word (69 vs 74); about a quarter of words are settled only at the sentence end. It is landed and switchable, not yet the
default: it replaces the search when it matches it. The main-word residual is being worked now (the main word as a clause-end decision).
Cost of the word-kinds flip: none measured; any reader that dips gets repaired, not reverted. Also: two new solver briefs in the hand-out tab
(Pri 95 coordination; Pri 93 one object per verb, re-scoped to roles), the prepositional-phrase brief (Pri 94) refreshed, two boards running.
- 2026-09-13 (morning, 06:00-08:00): the word-governor now commits to ONE connected sentence structure (before, it could hand the
  readers several disconnected pieces, and the shared hand-off even passed a non-structure built from per-word guesses); with that,
  its test score is 60 in 100 (57 at dawn, 48 yesterday morning), with clause-to-clause links up from 50 to 67 in 100. Punctuation
  is now attached by the writing convention (formatting, not meaning). The word-kind counter learned three more things it can
  count: the look of a word (capitals, digits), what rare words' endings and the system's own reading-derived word classes say,
  and two-step sequence patterns -- 91 -> 93 in 100 on the test set, and the tense tagger 91 -> 92. Two ideas were tried and
  honestly set aside with numbers: "one object per verb" at the governor (verbs legitimately take two bare nominals) and a
  "had ... -ed" tense repair (as many misfires as fixes). Four full checks are running to measure all of this on the readers.
- 2026-09-13 (morning, 05:00-08:30): four upstream steps, all switchable. (1) The brain-style word-governor now reads meaning at
  READ time as well as when it learns (before, meaning only shaped what it learned; only 2 in 100 word links changed between two
  learning runs, which is why the readers did not feel the governor's gains). First version: noun-modifier links 31 -> 38 in 100 and
  clause links 47 -> 50, but prepositional phrases were pushed off their verbs (47 -> 38); a corrected version that leaves
  prepositional phrases to their own cue is being measured. (2) The governor was made about five times faster with identical
  answers, so full checks with it no longer take three hours. (3) The last off-the-shelf part on the live reading path -- a
  borrowed tagger used for tenses inside the timeline reader -- is replaced by the system's own word-kind counter, which is also
  more accurate on the test set (91 vs 85 in 100, and equal or better on the tense-bearing verb forms); a full check confirms no
  reader regressed. (4) A word-root reader that prefers the stored or decomposed base over the surface form (the brain's
  words-and-rules route; 98.3 vs 96.0 in 100 on modern text) is landed as an alternative and being checked on the full board.
  Risk of my recommendations: each is a small measured step; the only un-measured one is the meaning cue's corrected version.
- 2026-09-13 (early morning, the full checks): with the brain-style word kinds feeding every reader, the whole-system check is
  63.6 in 100 (was 64.0); the agent reader's small dip was repaired by reading the word kinds as graded beliefs (82 -> 84, now above
  where it started). With the brain-style governor as well, the check is 62.2: coreference, salience and word sense are unchanged;
  who-was-affected drops 82 -> 73 and 'what is X' 83 -> 65, and both of those drops trace to the governor itself, not the readers
  (half of its object mistakes hand the object to the NEXT verb). The governor's own score is 57 in 100 (48 yesterday morning). One
  decision waits for you on the board: make the brain-style governor the default now (full checks then take hours until it is made
  fast) or after speeding it up. Everything is switchable either way.
- 2026-09-13 (overnight): the whole front of the reading chain now runs on brain-style parts, each one in a single shared place
  that every reader and every test uses. Word kinds come from a counting model that keeps a graded belief (91 in 100 right; the
  old hand-trained tagger was 94) and can also learn its kinds from plain reading (70 in 100 so far; the little words are the
  gap being worked). Word base forms come from an exact in-house port of the old dictionary tool (identical, 80x faster). Which
  word governs which is learned from reading plus meaning, with its meaning-knowledge now grown by our own reading rather than
  an outside parser, and with two long-known tricks folded in: copular sentences ("the soup was hot") now take the shape the
  downstream readers expect, and prepositional phrases get the verb-vs-noun preference learned from unambiguous sentences. On the
  state question ("what is X") the brain-style governor read went from 53 to 66 in 100 after its reader was taught the new shape
  (83 with the hand-trained governor). Four solver submissions were folded in tonight: the base-form port (used live), a quality
  instrument for meaning-grounding, a consolidated meaning representation (kept as a store, not a decision-maker, by its own
  test), and a careful negative on a table of cause-effect facts (its earlier +14 points was a measurement artefact; retired).
  Full-system checks with the new front end are running; dips in individual readers are expected and are being repaired one at a
  time rather than reverting the brain-style parts.
- 2026-09-12 (day): first step of the 'what happens next' story model landed. On the hard who-was-affected test I separated the
  real third-person cases (it/him/her/them, 596) from words that depend on who is speaking (you/me) and from this/that, which
  the brain handles with different machinery. Three established mechanisms were added to the live reader: every time a pronoun
  is resolved it counts as a fresh reference to that character (so often-referenced characters stay prominent); only things
  referenced in the last two sentences are considered first; and himself/themselves must point at the clause-mate. On the
  reader's own parse: 44 in 100 -> 48 in 100, clearly separated; scrambled controls fall to 39 and 18. Full check: pooled AGG 0.6408 -> 0.6408 (every dimension identical); who-was-affected row 0.3874 -> 0.3874; forward-half row 0.4789 on 593 third-person items; no regression.
  Also learned, with numbers: general word knowledge from encyclopedias does not decide among the top few candidates here; the
  brain's expectation is learned from who-did-what-to-whom event tuples, which is the next build.
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

- 2026-09-12 (late night): first result of the "make every upstream part brain-faithful" pass. The reader decides who is the
  subject, the object, the passive subject or the by-agent of a clause with a learned cue competition (word order, the preposition,
  be/get + participle, the copula, pronoun case — each weighed by how reliable it has proved), instead of a trained black-box label
  guesser. On held-out text with a correct parse it gets 92 in 100 of those roles right (by-agents 94 in 100; the old guesser got
  11 in 100 of those). On the hard who-was-affected test with the reader's own parse: 47 in 100 -> 49 in 100, clearly separated.
  Two simpler designs failed and are recorded with numbers so they are not retried. Also measured: with a correct parse the new
  labeler scores 84 in 100 on the test text, our own word tagging costs 6 points and our own attachment costs 8 more — those two
  parts are next. Full check: the new role reading is live; who-was-affected rose (39 -> 40 in 100; the third-person half 48 -> 50),
  two other abilities dipped about 2 in 100 because they were tuned to the old guesser's habits. Per your ruling that is not a
  failure but a repair job: tracing what those two readers need showed the dips came from the new reader lumping "gave HIM a book"
  recipients in with objects and double-counting two overlapping cues; fixing that upstream brought both back to within 1 in 100
  of before (full re-check done: overall 0.6408 -> 0.6377 -> 0.6395). The very top of the chain is now built too: word categories learned from reading a million lines
  with no labels agree with the reference on 74 in 100 words (the earlier try got 32), and they keep learning as text is read.
- 2026-09-12 (evening): the next part up the chain, deciding which word each word depends on, was rebuilt the brain's way: a
  competition of cues (closeness, word class pairs, verb habits, punctuation as written pauses, and learned phrase patterns) whose
  weights are learned from reading with no labelled examples. From nothing hand-written it reached 48 in 100 correct attachments — but a closer look showed it did not know that
  the verb governs its subject and object (objects right only 19 in 100). Late evening: letting the event's action claim its
  plausible participants (how children are thought to learn grammar from meaning) fixed that — 56 in 100 attachments right,
  objects 71, subjects 71, the sentence's main action 79 (was 41). Earlier, before that fix, the picture was:
  the previous best label-free method needed a hand-written table to reach 46. For honesty: a parser trained on forty thousand
  hand-corrected sentences reaches 78 here, people over 95, and the best anyone has published without labels is 68. Two research
  drills were kept; they show a third of our gap is bookkeeping convention (where the period or the preposition "attaches"), not
  comprehension, and that convention is now applied as a stated rule rather than pretended to be learned. Five things were tried
  and refuted with numbers so they are not retried (more reading text; a hard length penalty; second-order counting as built;
  two ways of inducing phrase patterns; meaning alone as the teacher).
## WHAT WE ARE WORKING ON
Short term (the next week or two):
- (Done 2026-09-12) The three finished pieces were folded in: helped-or-harmed, the part-of-speech finding, the verb-type organ.
- (Done 2026-09-12, night) The assault-verb wall: the reader now values the state the person ends up in (researched and built the same night).
- (Started 2026-09-12) The 'what happens next' story model: first arm landed (see above); next is the expectation learned from who-did-what-to-whom
  event tuples, applied only among the few candidates in focus.
- (Started 2026-09-12, late night) The upstream pass: make each part feeding who-was-affected brain-faithful and lossless, from the
  bottom up — roles (done, above), then word tagging, then attachment — before adding any new downstream mechanism.
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

Last full check: 2026-09-13T21:06:39.754895+00:00 (26 on record). Generated 2026-09-13T21:22:31+00:00.

| Ability | Group | How well | Compared with a simple rule | Since the previous check | Brain-faithful? |
|---|---|---|---|---|---|
| Whether 'the dog' is the same dog mentioned earlier | People and things | right 57 in 100 | clearly better than the simple rule (54 in 100) | unchanged since the previous check | brain model; some details still open |
| Which character the passage is mainly about | People and things | right 26 in 100 | a little better than the simple rule (20 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Who 'he / she / it / they' refers to | People and things | right 47 in 100 | clearly better than the simple rule (36 in 100) | unchanged since the previous check | brain model; some details still open |
| Linking a description ('the painter') to a named person | People and things | right 55 in 100 | clearly better than the simple rule (45 in 100) | unchanged since the previous check | brain model; some details still open |
| Pronoun reference as the full reader actually runs it | People and things | right 59 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Resolving 'the animal' to the dog just mentioned | People and things | right 58 in 100 | clearly better than the simple rule (52 in 100) | unchanged since the previous check | brain model; some details still open |
| Who was affected by what happened | People and things | right 39 in 100 | clearly better than the simple rule (34 in 100) | up 0.006 since the previous check | brain model; some details still open |
| Which meaning of a word is meant in this sentence | Word meaning | right 75 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Drawing safe conclusions from 'is a kind of' facts | Word meaning | right 77 in 100 | clearly better than the simple rule (54 in 100) | unchanged since the previous check | brain model; some details still open |
| Handling 'all / some / none' correctly | Word meaning | right 83 in 100 | clearly better than the simple rule (17 in 100) | unchanged since the previous check | brain model; some details still open |
| Handling 'not' correctly | Word meaning | right 93 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| How a word's meaning shifts with its context (graded) | Word meaning | agreement with people 0.39 (out of 1) | clearly better than the simple rule (0.38) | unchanged since the previous check | brain model; some details still open |
| Picking the right broad sense of an ambiguous word (older test set) | Word meaning | right 52 in 100 | clearly better than the simple rule (35 in 100) | unchanged since the previous check | brain model; some details still open |
| What something is or is like ('the sky is blue') | Actions and roles | right 81 in 100 | clearly better than the simple rule (57 in 100) | unchanged since the previous check | brain model; some details still open |
| Who did the action in a sentence | Actions and roles | right 83 in 100 | not better than the simple rule (85 in 100) yet | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Who or what the action was done to | Actions and roles | right 79 in 100 | clearly better than the simple rule (65 in 100) | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Keeping a fact true until something changes it | Actions and roles | right 100 in 100 | clearly better than the simple rule (44 in 100) | unchanged since the previous check | brain model; some details still open |
| Event order when the text does not say it outright | Time and place | right 57 in 100 | clearly better than the simple rule (53 in 100) | unchanged since the previous check | brain model; some details still open |
| Noticing where one scene ends and another begins | Time and place | right 12 in 100 | a little better than the simple rule (7 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Picking out place information correctly | Time and place | right 59 in 100 | clearly better than the simple rule (52 in 100) | unchanged since the previous check | brain model; some details still open |
| Where things are relative to each other | Time and place | right 24 in 100 | clearly better than the simple rule (20 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether a state still holds at a later point | Time and place | right 41 in 100 | clearly better than the simple rule (11 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether two events happened at the same time | Time and place | right 99 in 100 | clearly better than the simple rule (50 in 100) | unchanged since the previous check | brain model; some details still open |
| Which of two events came first | Time and place | right 59 in 100 | clearly better than the simple rule (52 in 100) | unchanged since the previous check | brain model; some details still open |
| Answering 'why' when the cause is sentences away | Causes | right 25 in 100 | clearly better than the simple rule (0 in 100) | unchanged since the previous check | brain model; some details still open |
| Following a chain of causes across several steps | Causes | right 26 in 100 | clearly better than the simple rule (0 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether a cause makes an effect bigger or smaller | Causes | right 62 in 100 | a little better than the simple rule (61 in 100), not yet convincingly | unchanged since the previous check | brain model; some details still open |
| Whether one event was needed for another to happen | Causes | right 36 in 100 | clearly better than the simple rule (4 in 100) | unchanged since the previous check | brain model; some details still open |
| How a character probably feels about an event | Feelings, goals, beliefs | right 90 in 100 | clearly better than the simple rule (44 in 100) | unchanged since the previous check | brain model; some details still open |
| What a character believes, even when it is false | Feelings, goals, beliefs | right 65 in 100 | clearly better than the simple rule (49 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether an action helped or harmed someone | Feelings, goals, beliefs | right 100 in 100 | clearly better than the simple rule (33 in 100) | unchanged since the previous check | brain model; some details still open |
| Whether an event helps or blocks a character's goal | Feelings, goals, beliefs | right 98 in 100 | clearly better than the simple rule (49 in 100) | unchanged since the previous check | brain model; some details still open |
| Who is having the feeling | Feelings, goals, beliefs | right 20 in 100 | clearly better than the simple rule (14 in 100) | unchanged since the previous check | brain model; some details still open |
| Working out what a new word means from reading | Learning from reading | right meaning ranked near the top 42 in 100 | clearly better than the simple rule (16 in 100) | unchanged since the previous check | brain model; some details still open |
| Knowing when to hold back on 'who was acted on' | Knowing its limits | right 96 in 100 | clearly better than the simple rule (84 in 100) | unchanged since the previous check | brain model; one part is a stand-in we are replacing |
| Knowing when to hold back on a place or time attachment | Knowing its limits | right 84 in 100 | clearly better than the simple rule (76 in 100) | unchanged since the previous check | uses a stand-in we are replacing |

Brain-faithfulness of the 90 building blocks: 8 copy the brain's math exactly, 76 are brain models with open details, 6 are stand-ins being replaced (arc_labeler, arc_parser, arceager_parser, commonnoun_binder, parse_confidence, pos_tagger).

<!-- AUTO:END -->
