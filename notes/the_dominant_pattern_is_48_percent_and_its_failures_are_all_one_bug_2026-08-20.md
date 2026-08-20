# THE DOMINANT EXTRACTION PATTERN IS **48-68% MEANINGFUL ACROSS TWO CORPORA**, AND **MOST OF ITS FAILURES ARE ONE BUG**

> **⚠️ THE FILENAME SAYS "48 percent" AND "all one bug". BOTH WERE WRITTEN BEFORE THE SECOND
> CORPUS RAN AND BOTH ARE NOW TOO STRONG.** The rate is **47.5% (simplewiki) / 67.5% (biology
> textbook)**, and the single-bug share is **91% on one corpus, 63-75% on the other**, with two
> further failure classes found. *The filename is left alone because notes are cited by name; the
> title and TLDR are corrected here. See the replication section.*

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

## ✅ REPLICATED ON A SECOND CORPUS, AND THE REPLICATION REFINES THE CLAIM RATHER THAN JUST CONFIRMING IT

Re-scored on `textbook_biology_2e` -- a genuine genre change, not a re-run -- **because n=40 on one
corpus by one scorer is precisely the shape of the finding I retracted an hour earlier.**

| `COPULA`, definiens field, n=40 each | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| simplewiki | 47.5% | 25.0% | 27.5% |
| **textbook_biology_2e** | **67.5%** | 12.5% | 20.0% |

**THE RATE REPLICATES AND IMPROVES.** Both sit far above the 0-4% every distributional measurement
gives on the same corpora. *(295 COPULA hits per 6,000 textbook sentences vs 340 in simplewiki --
supply is comparable, so this is a quality difference, not a coverage one.)*

**THE FAILURE-MODE CLAIM REPLICATES BUT LESS ABSOLUTELY: ~5-6 of 8 noise rows (63-75%) are
definiendum-span bugs, against 10 of 11 (91%) on simplewiki** -- `factor -> "the size of the
cell"`, `resultant chemical struc... -> "a molecule"`, `rigidity -> "an important structural
component of the cell walls"` (should be *cellulose*).

**AND THE SECOND CORPUS EXPOSES TWO FAILURE CLASSES THE FIRST DID NOT:**
1. **VACUOUS DEFINIENS** -- `tonicity -> "a concern for all living things"`. The term is right, the
   span is right, and the sentence simply does not define anything. Nothing about term boundaries
   would fix it.
2. **POSSIBLE POLARITY LOSS** -- `cell -> "a closed system"`, where the textbook's own next entry is
   `closed system -> "one that can transfer energy but not matter"`. **A cell is NOT a closed
   system**, so this looks like a negated sentence read as an affirmative one. **Stated as a
   HYPOTHESIS: I did not retrieve the source sentence to confirm the negation.** If real, it is a
   correctness bug of a different and worse kind than a boundary slip, because the output is
   confidently wrong rather than merely misattached.

**➡️ HONEST NET: the headline number survives a genre change and gets better; the "it is all one
bug" framing was too strong and is now "most of it is one bug, and there are at least two others".**

## LIMITS, AND THEY ARE REAL

1. **n=40 per corpus, one scorer (me), two corpora, one sitting.** The RATE now has a genre
   replication (47.5% -> 67.5%), which is more than any other single-arm number tonight has. It is
   still one scorer.
2. **Single arm. No floor.** A precision figure, not a floor-cleared comparison. It cannot clear the
   measurement bar and must not be quoted as though it had.
3. **Scored on the DEFINIENS**, so it is not comparable to any figure scored on the banked head. The
   standing prohibition on juxtaposing hand-score numbers applies.
4. **I retracted a same-shaped finding once tonight** (the 92%), which is why the second corpus was
   run BEFORE quoting this anywhere. **It survived. The 92% did not.** That is the difference
   between a number that replicates and one that was a property of its sample.

## TLDR

Earlier tonight I got excited about how well this system reads glossary lines, then discovered
glossary lines barely exist and it confuses them with bibliographies. So I went and measured the
sentence shape that actually does most of the work: plain *"X is a Y"* statements, which are more
than half of everything it extracts.

**On ordinary Simple Wikipedia prose it gets those right about half the time** -- *"cosmology: the
branch of astronomy that deals with the universe"*, *"death: the end of a life in an organism"*.
Everything else we measure on that same text scores between nothing and four percent.

**And its mistakes are mostly one mistake.** Usually the explanation it extracted was perfectly
good -- it just attached it to the wrong word. From *"Australia's longest river is the Gudena"* it
learns that "longest river" means "the Gudena", instead of learning what the Gudena is.

That exact bug was already found and fixed for a different sentence shape a week ago, and fixing it
there took that shape's accuracy from 4% to 60%. **It is still unfixed on the shape that carries
most of the traffic.**

**I then checked it on a second, very different source before letting the number stand -- because I
had already retracted one finding of exactly this shape earlier tonight.** On a biology textbook it
did *better*, not worse: **roughly two in three right instead of one in two.** So the headline
survives a change of material, which the glossary claim did not.

**The second look also corrected me.** "Almost all one mistake" was too strong -- on the textbook
it is more like two in three, and two further kinds of error showed up that the first source never
revealed: sentences that define nothing at all (*"tonicity is a concern for all living things"*),
and one apparent case of the system dropping a **"not"** and recording the opposite of what the book
said. **That last one, if confirmed, is worse than a misattached explanation** -- it is confidently
wrong rather than merely pointing at the wrong word. I have flagged it as unconfirmed because I did
not go back to the original sentence.

## QUESTIONS

None. This names a target; whether to spend on it is part of the Q89 decision already with the owner.

## NEXT STEPS

1. **Re-score COPULA on a second corpus** before the 48% is quoted anywhere. One scorer, one corpus,
   n=40 is exactly the shape of tonight's retraction.
2. **The definiendum-span defect is the named, sized target** -- ~95 noise rows per 6,000 sentences
   on the live corpus, one cause, already solved once for other patterns.
