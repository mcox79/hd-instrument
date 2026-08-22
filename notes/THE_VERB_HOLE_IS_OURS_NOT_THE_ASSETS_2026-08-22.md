# 🔑 **THE VERB HOLE IS A LEARNING DEFICIT, NOT A SUPPLY ONE. THE ASSET SPEAKS ABOUT VERBS FINE.**

**Our learned channel is the standing problem:** `+0.0000` on SimVerb-3500 and, within SimLex on one
scorer with only word class changing, **NOUN `0.1310` CLEARS its `0.0843` null while VERB sits
INSIDE.** *"Weak on nouns, absent on verbs."*

**The unexamined half: can the asset we plan to lean on say anything about verbs at all?** Phase 1 is
MEANING SUPPLY, and if the supply is silent on verbs then the whole route cannot touch our worst word
class. **Nobody had set the asset's verb number beside its noun number on one benchmark.**

---

## 1. IT CAN. AND ITS VERB SIGNAL IS INDISTINGUISHABLE FROM ITS NOUN SIGNAL.

**SimLex-999, one scorer, one benchmark, ONLY WORD CLASS CHANGING** -- the form the measurement bar
requires, because no number may cross populations:

| POS | n | rho (norm cosine vs human) | shuffled null p95 | verdict |
|---|---|---|---|---|
| **NOUN** | 666 | **`+0.2745`** | `0.0732` | ✅ **CLEARS** |
| **VERB** | 222 | **`+0.2607`** | `0.1241` | ✅ **CLEARS** |
| ADJECTIVE | 111 | `+0.1472` | `0.1952` | 🔻 inside its null |

> ### **NOUN vs VERB: Fisher `z = 0.192` -- NOT SEPARATED. THE ASSET HAS NO VERB DEFICIT.**

**And it is not a coverage artifact either: on SimVerb-3500 the asset covers `3,487` of `3,500` verb
pairs = `99.6%`, rho `+0.2676` on that covered set.** *400-shuffle nulls; positive control
`cos(w,w) = 1.0` for 300 words.*

## 2. WHAT THAT SETTLES

| channel | NOUN | VERB |
|---|---|---|
| **what we LEARN from text** | clears (`0.1310` vs null `0.0843`) | 🔻 **INSIDE NULL** |
| **what the asset SUPPLIES** | clears (`0.2745` vs null `0.0732`) | ✅ **CLEARS (`0.2607`)** |

> # 🔑 **THE VERB ZERO IS OURS. THE MEANING FOR VERBS IS AVAILABLE, ON 99.6% OF PAIRS, AND WE ARE NOT LEARNING IT.**

➡️ **So meaning-supply is not blocked on our worst word class -- it is precisely where supply has the
most to add**, because that is where the gap between supplied and learned is widest. *This does not
say supply is a substitute for learning; the standing rule stands -- **SUPPLY != LEARNING**.*

🧠 **Brain read, offered as a frame and not as evidence:** the ATL hub-and-spoke account has verb
meaning leaning on **sensorimotor/action spokes** rather than on distributional company, which is why
a sensorimotor asset having full verb signal is unsurprising and why a co-occurrence channel having
none is *also* unsurprising. **Our architecture reads text and expects verbs to fall out of it.**

## 3. ⚠️ THE ADJECTIVE ROW IS **NOT** A CAPABILITY STATEMENT, AND SAYING SO IS THE POINT

`A` reads `+0.1472` against a null p95 of `0.1952` -- inside. **THAT IS AN UNDERPOWERED NULL AT
`n=111`, NOT EVIDENCE THE ASSET LACKS ADJECTIVE MEANING.** The null band is *wider* than the noun
band (`0.1952` vs `0.0732`) purely because there are six times fewer pairs.

**This project's most expensive recorded error is reading an underpowered null as a capability
statement -- three times in one night.** So: **adjectives are UNRESOLVED here and need a bigger
adjective population before anything is claimed either way.** *It is a lead, and the only thing worth
saying is that it is the one class that did not clear.*

## 4. 🚫 A NUMBER THAT MUST NOT BE CROSSED WITH THIS ONE

The archive records **`SUPPLIED 0.2983` on SimVerb's `2,651` covered pairs**. **My `0.2676` is on
`3,487` pairs.** Different populations -- `2,651` is what OUR channel covers, `3,487` is what the
NORMS cover -- **so the two may not be quoted as a change, an improvement, or a discrepancy.** *Both
are real; they answer different questions.* ⚠️ *Incidentally the asset's verb coverage (`99.6%`)
exceeds our own channel's on the same benchmark (`2,651/3,500 = 75.7%`).*

## 5. LIMITS, STATED

- **This is the ASSET measured directly against human ratings. It is not the substrate**, and no
  reading run was involved. It says the information exists and is retrievable by cosine.
- **A word-similarity benchmark is the channel both plans of record already ruled out as a target.**
  It is the right instrument for *"is the meaning there"* and the wrong one for *"does the system
  comprehend"*.
- **Nothing here was learned.** The norms are human-rated and supplied.
- Adjectives: unresolved, see §3.

---

## TLDR

We have a long-standing problem: our system extracts meaning for nouns reasonably and gets **nothing
at all** for verbs. The plan's fix is to lean on a table of human-rated word descriptions.

Nobody had checked whether that table says anything useful about verbs. **It does — just as well as
it does for nouns, and it has an entry for 99.6% of the verb pairs we test on.** Statistically its
verb and noun performance are indistinguishable.

So the verb blind spot is *ours*, not a gap in what's available. The information is sitting there and
our reading process isn't picking it up. That's better news than the alternative, because it means
the meaning-supply plan works hardest exactly where we're weakest.

One thing I am deliberately **not** claiming: adjectives came out looking weak, but there were only
111 adjective pairs, which is too few to conclude anything. Calling that a weakness would repeat the
most expensive mistake in this project's record.

## QUESTIONS

None.

## NEXT STEPS

1. **This raises the priority of `lookup_does_not_lemmatise`**: the asset's verb signal is only
   reachable if the lookup can find the verb, and verbs are the most heavily inflected class in
   running text (`released`, `playing`, `began`). *The coverage fix and the verb hole are the same
   lever.*
2. **Adjectives need a bigger population** before the `+0.1472` is called anything.
3. 🚫 **Do not quote `0.2676` and `0.2983` together.** Different covered populations.
