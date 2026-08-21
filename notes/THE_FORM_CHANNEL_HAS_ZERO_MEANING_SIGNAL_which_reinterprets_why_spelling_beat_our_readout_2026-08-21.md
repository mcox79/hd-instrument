# **THE FORM CHANNEL SCORES rho = −0.026 ON HUMAN MEANING JUDGEMENTS -- EXACTLY ZERO, AS IT SHOULD. AND THAT REINTERPRETS WHY SPELLING BEAT OUR MEANING READ-OUT: THE READ-OUT TASK HAS AN ORTHOGRAPHIC SHORTCUT.**

**I established the only valid way to judge the form channel for Q102: measure it where the word is
the QUESTION, not the answer. This is that measurement, and it produces both the answer and a
reinterpretation of a standing archive result.**

---

## 1. THE MEASUREMENT

*`CharTrigramEncoder` cosine between the two words of every SimLex-999 pair, against the human
similarity ratings. n = 999, the full set, nothing sampled.*

| channel | rho vs human meaning judgements |
|---|---|
| **FORM (spelling trigrams)** | **−0.0259** *(p = 0.41)* |
| `ASSET_NORMS12` (12 human dims) | 0.2701 |
| `P_LIVE_CONCEPT` (our live encoding) | 0.1048 *(CI crosses zero)* |

> ### **THE FORM CHANNEL CARRIES NO MEANING SIGNAL WHATSOEVER. Not weak -- ZERO, on 999 human judgements.**

## 2. ✅ **AND THAT IS A GOOD RESULT FOR Q102, NOT A BAD ONE**

**The risk I filed with Q102 was that wiring the form organs would give "a better index rather than
better understanding".** *This confirms the first half and DISARMS the danger in it:*

***The form channel is a PURE index. It cannot inflate a meaning score, contaminate a meaning
comparison, or be mistaken for understanding by any measurement -- because it has no meaning signal
to contribute.*** **That makes it SAFE to wire as a separate channel, and it makes blending it INTO
the meaning vector clearly wrong: the form component would be pure noise on every meaning task.**

## 3. 🔄 **THE REINTERPRETATION -- TWO NUMBERS THAT CONSTRAIN EACH OTHER**

**Standing archive result: pure SPELLING beats our MEANING read-out at rank 1, `0.0767` vs `0.0480`,
surviving the strictest tie convention.** *That has been read as an indictment of our meaning
representation, and `notes/PLAN.md` cites it as evidence for the form/meaning confusion.*

**Put it beside rho = −0.026 and it cannot mean what it appeared to mean:**

> ### **A CHANNEL WITH ZERO MEANING SIGNAL BEAT OUR MEANING READ-OUT. SO THE READ-OUT TASK IS PARTLY SOLVABLE WITHOUT MEANING -- IT HAS AN ORTHOGRAPHIC SHORTCUT.**

*The likely mechanism is mundane and checkable: gold answers that are morphological or orthographic
relatives of the cue, which spelling similarity finds for free.*

⚠️ **THE HONEST ALTERNATIVE READING, which I cannot separate with what I have: our meaning read-out
may simply be so weak that a zero-meaning signal beats it on task artefacts alone.** *Both readings
imply the same thing -- **the read-out task contains non-meaning signal and cannot be scored as a
pure meaning test** -- so the conclusion holds either way, but the CAUSE is not settled.*

## 4. WHAT THIS CHANGES

| claim | status |
|---|---|
| the form channel is a pure FORM code | ✅ **now measured, rho = −0.026 on n=999** |
| wiring it risks "a better index, not understanding" | ✅ **TRUE AND SAFE -- it is a pure index and cannot fake understanding** |
| blending form INTO the meaning vector | 🚫 **clearly wrong -- it would be pure noise on meaning tasks** |
| **"spelling beats our meaning read-out" as evidence about our MEANING representation** | ⚠️ **WEAKENED. It is at least as much evidence about the TASK.** |
| `PLAN.md`'s form/meaning confusion anchor | ✅ **UNTOUCHED and arguably strengthened** -- it says a form code is not a meaning code, which is exactly what rho = −0.026 shows |

## TLDR

I said the only fair way to judge the word-recognition components is to test them where the word is
the *question* — what it means — rather than where the word is the answer. **I ran that test.**

**They score essentially zero at predicting human judgements of what words mean** — a correlation of
−0.03 across 999 word pairs rated by people. **That is exactly right.** Recognising a word by its
spelling shouldn't tell you what it means, and ours doesn't.

**And that turns the worry I raised into a reassurance.** I warned that switching these on might just
give us a better lookup table rather than better understanding. **It confirms they are purely a lookup
— and that is why they're safe.** A channel with no meaning signal cannot inflate a meaning score or
be mistaken for comprehension. It also settles a design point: these must stay a *separate* channel,
because mixing them into the meaning representation would add pure noise.

**It also forces a rethink of something we've been quoting.** We have a standing result that plain
spelling beats our meaning read-out. That's been treated as evidence our meaning representation is
poor. **But if spelling carries zero meaning signal and still wins, then that test can be partly
solved without meaning at all** — most likely because some right answers are just spelling-relatives
of the question.

**One honest limit:** I can't yet separate "the test has a shortcut" from "our meaning read-out is so
weak that even a meaningless signal beats it". **Both lead to the same conclusion — that test isn't a
pure measure of meaning — but the cause isn't settled.**

## QUESTIONS

*Q102 remains open; this strengthens the recommendation and disarms its stated risk.*

## NEXT STEPS

1. **Wire form as a SEPARATE channel, never blended into the meaning vector.** *rho = −0.026 makes
   blending clearly wrong.*
2. **Stop citing "spelling beats our meaning read-out" as evidence about our meaning representation
   without the caveat** -- it is at least as much evidence about that task.
3. **The cheap follow-up that would settle the cause:** *check whether the read-out's gold answers are
   orthographic or morphological relatives of their cues. If they are, the shortcut is confirmed.*
