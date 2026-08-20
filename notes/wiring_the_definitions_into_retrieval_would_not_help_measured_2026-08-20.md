# THE OBVIOUS FIX FOR THE READ-BACK GAP DOES NOT WORK: INDEXING BY THE DEFINITION RETRIEVES *WORSE* THAN THE PROFILE

**2026-08-20.** Today established that (a) the substrate's definitional phrases are good, and (b)
**nothing in the substrate reads them** -- so "improve the definitions" and "improve the read-out"
are disconnected problems. **The obvious response is to connect them. This is the measurement that
says not to.**

## THE RESULT

Same space, same cue, same candidate set, same scorer. **One variable: what the index row is made
of.** Ranks via `tools/rank_with_ties.py` (mandatory -- three tie artifacts in one day came from a
bare `1 + sum(scores > target)`).

| arm | optimistic | **midpoint** | pessimistic |
|---|---|---|---|
| **PROFILE** -- accumulated context vector. **THE SHIPPED ROUTE.** | 64.0 | **64.0** | 64.0 |
| **DEFINIENS** -- the term's own definition text. **THE PROPOSED FIX.** | 92.0 | **92.0** | 92.0 |
| **BOTH** -- normalised sum | 71.0 | **71.0** | 71.0 |
| SHUFFLE_DEF -- *another* term's definition | 99.0 | 99.0 | 99.0 |
| **COOC** -- corpus co-occurrence counting | 4.0 | **5.0** | 6.0 |

n = 133 items, 212 candidates, seed 7, 12,000 sentences. Ties were negligible in every arm except
COOC (1 item of 133).

**➡️ DEFINIENS IS 28 RANKS WORSE THAN THE PROFILE IT WOULD REPLACE. `BOTH` IS 7 WORSE.
CONNECTING THE TWO HALVES, THE OBVIOUS WAY, WOULD MAKE RETRIEVAL WORSE.**

## WHAT IT DOES *NOT* SAY, AND THE DISTINCTION IS THE WHOLE VALUE OF THE CONTROL

**The definitions are NOT noise.** DEFINIENS (92) beats SHUFFLE_DEF (99), so a term's own definition
does carry term-specific retrieval signal. **It simply carries LESS of it than the accumulated
profile does**, and the likely mechanism is volume, not quality: a definiens is ~7 words, while a
profile is the summed context of every encounter -- dozens of sentences. **A short, high-quality
signal loses to a long, low-quality one on a task that rewards breadth of association.**

**So this is a narrow negative and must not be widened.** It tests **ONE** way of consuming meaning
(as a retrieval index vector) on **ONE** task (retrieve the term from a sentence cue). It does not
show the content is useless. Untested and still open: using the definition to ANSWER "what is X",
using its GENUS for inference or type-checking, or using it to seed a term's representation at first
encounter rather than to replace it afterwards. *This project's own rule: a fair test of a WEAK
implementation proves that setup failed, not that the capability is impossible.*

## ⚠️ STATUS OF THE "BOUNDARY" BELOW: **NOT ESTABLISHED, AND NEITHER IS THE THING THAT REFUTED IT.**

**Read this before the two sections that follow, because they argue opposite things and BOTH rest on
single seeds.**

1. Below I claimed *"combining helps when channels are comparably strong; a strictly weaker one
   DILUTES."* One experiment, one seed.
2. An hour later I marked that REFUTED, on the strength of a `BOTH` arm that gained 16 ranks with a
   weaker second channel.
3. **That refuting result died on its second seed** -- `BOTH` fell to a 1-rank gain and an
   information-free NOISE blend beat it outright
   (`notes/a_definition_helps_when_it_is_LOOKED_UP_not_when_it_is_read_2026-08-20.md`).

**➡️ SO NEITHER STATEMENT IS ESTABLISHED. Combining behaved inconsistently across seeds and I have
no evidence for any boundary condition on it.** The owner's original "combining channels helps"
result stands on its own three-seed evidence elsewhere and is untouched by any of this; what is
withdrawn is MY attempt to say WHEN it helps -- twice, in opposite directions, each time from a
single run.

*The finding in this note -- that indexing BY the raw definiens text is 28 ranks worse -- is a
separate measurement and still stands.*

## [SUPERSEDED CORRECTION -- ITS EVIDENCE WAS ITSELF WITHDRAWN] THE "BOUNDARY" IS REFUTED

**I wrote below that "combining helps when the channels are comparably strong; when one is strictly
weaker it DILUTES." THAT WAS A GENERALISATION FROM ONE DATA POINT AND IT IS WRONG.**

`notes/a_definition_helps_when_it_is_LOOKED_UP_not_when_it_is_read_2026-08-20.md`: represent the
definition NOT as its raw text vector but as **the mean of the already-learned profiles of the words
it names** -- borrowed volume instead of seven thin tokens. Then:

| ALL, n=132, 211 candidates | midpoint rank |
|---|---|
| PROFILE | 54.5 |
| DEF_LOOKUP (weaker channel) | 67.0 |
| **BOTH** | **38.5** |

**The second channel is WEAKER (67 vs 54.5) and combining still gains 16 RANKS.** So weakness does
not imply dilution, and my boundary was false.

**THE CORRECTED STATEMENT: combining helps when the second channel is an INDEPENDENT ESTIMATE OF THE
SAME THING IN A COMPARABLE REPRESENTATION.** That is what differs between the two experiments -- here
the second channel is a mean of LEARNED PROFILES, the same kind of object as the first, built from
different evidence. In the experiment below it was a raw context vector over seven tokens: not an
independent estimate of the term, just more text. **INDEPENDENCE, NOT COMPARABLE STRENGTH, IS THE
CONDITION** -- which is what the owner's original "combine channels" hypothesis said, and my
amendment made it worse rather than sharper.

*The finding below -- that indexing BY the raw definiens text is 28 ranks worse -- still stands. It
is the INFERENCE I drew about combining that was wrong.*

## THE (REFUTED) BOUNDARY IT SEEMED TO PUT ON THE ONE RESULT THAT KEEPS WORKING

**"Combining channels beats either alone" is this project's most reproducible positive** -- the
owner's own hypothesis, confirmed on three seeds. **Here it fails: `BOTH` (71) is WORSE than
`PROFILE` (64).** The boundary condition is visible and worth keeping: **combining helps when the
channels are comparably strong and independent; when one is strictly weaker it DILUTES.** Averaging
a good vector with a worse one lands between them, which is exactly what 71 sits between 64 and 92.

## AND COO C STILL CRUSHES EVERYTHING: 5.0 AGAINST THE BEST ARM'S 64.0

Reproduced yet again, on a fresh task built today. **The headline is unchanged and none of today's
good news touches it:** on retrieval, plain co-occurrence counting is more than ten times better
than anything this substrate computes. *That is the number to keep in view when reading the phrase
result -- the phrases are good OUTPUT; the RETRIEVAL machinery remains far below counting.*

## CONTROLS, AND ONE OF THEM DID REAL WORK

- **LEAK CONTROL: 3,269 cue sentences were EXCLUDED** as being the very sentence a definition was
  read from. Without it the DEFINIENS arm would have been scored against its own source. **The
  count is printed precisely because a control that excludes nothing is not a control** -- and this
  session already had a 600-of-600 leak that manufactured a thirty-fold fake win.
- **79 of 212 terms were DROPPED** for having no non-source cue sentence left, which is a real
  coverage cost and is reported rather than absorbed.
- **Every arm scores the IDENTICAL candidate set** (212 terms usable in all four vector arms), so no
  arm is advantaged by a smaller or easier pool.
- **SHUFFLE_DEF** is the arm that makes the result interpretable: without it, "DEFINIENS is worse"
  could not be distinguished from "definition-shaped text is worse".

## TLDR

We found this morning that the system writes decent definitions and that nothing reads them. The
obvious fix is to make the system look them up. **I tested that before building it, and it makes
things worse.**

Asked to find the right word from a sentence, the system does better using everything it has ever
seen about that word than using the one tidy definition it wrote down. **That is a size effect, not
a quality one**: the definition is seven words, and the accumulated experience is hundreds. The
definition is not noise -- using the *right* one beats using a *random other* one -- there is just
not enough of it.

Two things worth carrying away. Combining the two sources did not help either, which is a limit on
the one trick that has reliably worked for us: **blending helps when both sources are good, and
hurts when one is clearly weaker.** And plain word-counting still beat every version of our system
by more than ten to one on this task.

## QUESTIONS

None. This closes a route rather than opening a choice.

## NEXT STEPS

1. **Do not build the definition-indexed read.** Measured, one variable, leak-controlled.
2. **If the read-back gap is worth closing, it is not by swapping the index vector.** The untested
   routes are: use the definition to ANSWER rather than to RETRIEVE; use its genus for inference;
   or use it to SEED a new term's representation at first encounter, where volume is zero and seven
   good words may beat nothing.
3. **Still do not spend on extractor recall.** Nothing yet reads the material we already have.
