# THE DOMINANT EXTRACTION PATTERN IS ~48% MEANINGFUL ON ORDINARY PROSE, AND **91% OF ITS FAILURES ARE ONE BUG**

**2026-08-20, late.** Tonight I measured the RAREST extraction pattern (`GLOSSARY_COLON`, 1-12% of
supply), got 92%, and had to retract it. **So I measured the DOMINANT one instead** -- `COPULA` is
**52-63% of every definitional extraction**, which makes it the only pattern whose quality decides
whether the extraction route is worth anything.

## THE RESULT, ON SIMPLEWIKI -- THE CORPUS EVERYTHING ELSE SCORES BADLY ON

**340 COPULA extractions per 6,000 sentences.** Forty sampled, scored on the DEFINIENS -- the field
the substrate actually banks (`substrate.py:538` stores `d.definiens`), and the field tonight
established is the right one to score:

| | count | rate |
|---|---|---|
| **MEANINGFUL** | 19 | **47.5%** |
| RELATED | 10 | 25.0% |
| NOISE | 11 | 27.5% |

> *"cell -> the small parts that make up all living things"* · *"cosmology -> the branch of
> astronomy that deals with the universe"* · *"death -> the end of a life in an organism"* ·
> *"population -> a group of living things of the same species that live in one area"* ·
> *"flanders -> the name of the northern half of Belgium"*

**➡️ ~48% ON PLAIN SIMPLE-WIKIPEDIA PROSE, from the pattern that supplies most of the volume.** For
comparison, every distributional number measured on this same corpus today sits at 0-4%.

## 🔧 AND THE FAILURES ARE NOT SCATTERED -- **10 OF 11 ARE THE SAME BUG**

**The DEFINIENS is almost always fine. The DEFINIENDUM -- the term being defined -- is a broken
span:**

| what it "defined" | with |
|---|---|
| `well-known example` | the Ring of Fire |
| `longest river` | the Gudena |
| `largest group` | the descendants of the Spanish settlers |
| `big change` | the development of atomic theory by John Dalton |
| `main sporting league` | the AFL |
| `second large` | the Encyclopaedia Britannica |
| `United Nations Cuba` | the only nation that met the WWF's definition |
| `example` | the Cumberland Plain where Sydney is now |
| `cooking breakfast saus` | an art |

**91% of the noise (10 of 11) is the extractor grabbing a MODIFIER PHRASE where the term should
be** -- *"Australia's **longest river** is the Gudena"* yields `longest river -> the Gudena` instead
of `Gudena -> Australia's longest river`. **Exactly one noise row has a genuinely wrong definiens**
(`style -> the couple dance`).

## ⭐ WHY THIS IS THE MOST ACTIONABLE FINDING OF THE DAY

**IT IS THE SAME BUG CLASS `exp_definitional_grounding_v5` ALREADY FIXED FOR OTHER PATTERNS.** That
cell repaired term-boundary corruption from **16.1% -> 1.0%** and, measured tonight, took its
sample's quality from **4% to 60%**. **The COPULA path is still losing ~28% of its output to the
same failure, on the dominant pattern, on the live corpus.**

**AND IT IS SIZED, NOT GUESSED.** Prevalence measured BEFORE proposing anything -- the rule that
killed two proposals today and rightly shrank a third:
- `GLOSSARY_COLON`: **7 hits per 6,000** simplewiki sentences -> a fix is a curiosity.
- **`COPULA`: 340 hits per 6,000 -> ~48x the volume, with ~95 noise rows per 6,000 attributable to
  one identifiable defect.**

## LIMITS, AND THEY ARE REAL

1. **n=40, one scorer (me), one corpus, one sitting.** After tonight, that is a HYPOTHESIS about the
   rate. It is **not** a hypothesis that the failures share a cause -- that is a qualitative reading
   of ten specific rows, and anyone can check them.
2. **Single arm. No floor.** A precision figure, not a floor-cleared comparison. It cannot clear the
   measurement bar and must not be quoted as though it had.
3. **Scored on the DEFINIENS**, so it is not comparable to any figure scored on the banked head. The
   standing prohibition on juxtaposing hand-score numbers applies.
4. **I have retracted a same-shaped finding once tonight already** (the 92%), on exactly this kind
   of evidence. **The 48% should be treated as provisional until re-scored on a second corpus.**

## TLDR

Earlier tonight I got excited about how well this system reads glossary lines, then discovered
glossary lines barely exist and it confuses them with bibliographies. So I went and measured the
sentence shape that actually does most of the work: plain *"X is a Y"* statements, which are more
than half of everything it extracts.

**On ordinary Simple Wikipedia prose it gets those right about half the time** -- *"cosmology: the
branch of astronomy that deals with the universe"*, *"death: the end of a life in an organism"*.
Everything else we measure on that same text scores between nothing and four percent.

**And its mistakes are almost all one mistake.** Nine times in ten, the explanation it extracted was
perfectly good -- it just attached it to the wrong word. From *"Australia's longest river is the
Gudena"* it learns that "longest river" means "the Gudena", instead of learning what the Gudena is.

That exact bug was already found and fixed for a different sentence shape a week ago, and fixing it
there took that shape's accuracy from 4% to 60%. **It is still unfixed on the shape that carries
most of the traffic.**

Caution, because I have already retracted one finding of this shape tonight: this is forty examples,
graded by me, on one source. Treat the number as provisional. **The fact that the failures share a
single cause is the durable part** -- those ten rows are on the page and anyone can look.

## QUESTIONS

None. This names a target; whether to spend on it is part of the Q89 decision already with the owner.

## NEXT STEPS

1. **Re-score COPULA on a second corpus** before the 48% is quoted anywhere. One scorer, one corpus,
   n=40 is exactly the shape of tonight's retraction.
2. **The definiendum-span defect is the named, sized target** -- ~95 noise rows per 6,000 sentences
   on the live corpus, one cause, already solved once for other patterns.
