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
2. **POLARITY LOSS -- CONFIRMED AS A DEFECT, MECHANISM CORRECTED, AND THEN SIZED OUT OF
   PRIORITY.** `cell -> "a closed system"`. I hypothesised a dropped negation. **Retrieving the
   source sentence shows something subtler:**

   > *"**If a cell were a closed system**, its chemical reactions would reach equilibrium, and it
   > would die..."*

   **A COUNTERFACTUAL CONDITIONAL, not a negation.** The subjunctive *"were"* is the only signal
   that a cell is NOT a closed system -- **there is no negation token to detect**, so a
   negation-word filter would never catch it. *The defect is real and the output is confidently
   wrong; my proposed cause was wrong.*

   **AND THEN PREVALENCE KILLED IT AS A TARGET.** Sentences carrying counterfactual / negated /
   hypothetical markers account for **5 of 295 COPULA extractions on the textbook (1.7%) and 0 of
   340 on simplewiki (0.0%)** -- and **inspecting all five, only ONE is an actual polarity defect**.
   The other four extract correctly despite the marker (`proline -> "an exception to the amino
   acid's standard structure"`, `alkaptonuria -> "a recessive genetic disorder in which..."`), the
   marker sitting harmlessly in a subordinate clause.
   **➡️ REAL RATE ~1 IN 295 (0.3%) AGAINST ~28% FOR DEFINIENDUM-SPAN BUGS -- ROUGHLY 90x LESS
   PREVALENT. NAMED, CONFIRMED, AND NOT WORTH FIXING.** *Third time today prevalence has demoted a
   qualitatively alarming defect; the discipline is the reason this note recommends one target
   instead of four.*

**➡️ HONEST NET: the headline number survives a genre change and gets better; the "it is all one
bug" framing was too strong and is now "most of it is one bug, and there are at least two others".**

## 🔬 THE SPAN BUG DIAGNOSED -- IT IS THE **SPECIFICATIONAL COPULA**, AND THE POPULATION COUNT CORRECTS MY OWN PREVALENCE ESTIMATE **DOWN**

**DIAGNOSIS.** Every broken-span row is the same linguistic construction. English has two copulas:

- **PREDICATIONAL** -- *"A cell is the smallest unit of a living thing"*. Subject is the term,
  complement describes it. **The extractor is right.**
- **SPECIFICATIONAL** -- *"Australia's longest river is the Gudena"*. **The subject is a definite
  DESCRIPTION and the complement is the NAME.** The sentence defines *Gudena*, not
  *longest river*. **The extractor takes the pre-copula NP as the definiendum unconditionally,
  which is correct for the first kind only.**

Unambiguous instances from both corpora: `result -> "an element with an atomic number of two
less"`, `difference -> "the presence of the hydroxyl group on the ribose"`, `main sporting league ->
"the AFL"`, `third-largest group -> "the Hazaras"`, `net result -> "a low pH in the thylakoid
lumen"`.

**PREVALENCE, AND IT CONTRADICTS MY OWN EARLIER NUMBER.** A definite-description marker
(superlative / ordinal / `example` / `result` / `difference` / `main` / `key`...) in the definiendum:

| | flagged | of |
|---|---|---|
| simplewiki | **25** (7.4%) | 340 |
| textbook_biology_2e | 13 (4.4%) | 295 |

**That marker catches ~78% of the span bugs I hand-identified (7 of 9), which puts the true
specificational rate near 9-10% -- NOT the ~25-28% my 40-row sample implied.**
**➡️ THE 340-ROW POPULATION COUNT BEATS MY 40-ROW HAND SAMPLE FOR PREVALENCE, AND I AM CORRECTING
MY OWN ESTIMATE DOWNWARD.** *The sample over-represented span bugs; small samples do that, which is
the whole reason to count the population when you can.*

**AND THERE ARE AT LEAST TWO SPAN-BUG SUBTYPES, NOT ONE:**
1. **Specificational copula** -- ~7.4% / 4.4%, marker-detectable, **principled fix available**:
   detect it and either SWAP the roles or REFUSE (*"the difference is the presence of the hydroxyl
   group"* defines nothing and should be refused).
2. **Truncated or merged spans** -- `cooking breakfast saus`, `United Nations Cuba`. **No marker,
   different cause, not addressed by the same fix.**

**SO THE HONEST TARGET IS SMALLER AND SHARPER THAN I SAID ONE TURN AGO: ~7% of the dominant
pattern, one nameable construction, with a principled fix -- not "28% from one bug".**

### ✅ AND THE PROPOSED FIX IS SAFE: **96% PRECISION, CHECKED ON ALL 25 FLAGGED ROWS**

**A fix that refuses good extractions is worse than the bug.** So every marker-flagged simplewiki
row was checked -- not sampled, **all 25** -- asking *"would refusing or swapping this be RIGHT?"*

**24 of 25: YES.** `main sporting league -> the AFL` (swap defines the AFL), `result -> an element
with an atomic number of two less` (refuse -- defines nothing), `chief executive -> the marzpet`
(swap), `third-largest group -> the Hazaras` (swap), `best time -> the months of May and June`
(refuse).

**1 of 25: NO -- and the cause is a REGEX OVER-MATCH, not a linguistic error.**
`honest reporting -> "a key part of how science works today"` is a **perfectly good PREDICATIONAL
extraction.** The marker fired because **`\w+est` matches "hon-EST".** *`best time` on the same list
is a genuine superlative and correctly flagged; "honest" simply is not one.*

**➡️ THE FIX IS SAFE TO BUILD, AND ITS ONE FAILURE MODE IS ALREADY NAMED AND CLOSABLE** -- require a
real superlative (POS tag `JJS`, or a stoplist for the `-est` nouns: honest, earnest, modest,
forest, interest, harvest, request, contest, protest, priest, quest...). **Without this check that
over-match would have shipped inside the fix**, silently refusing good extractions -- the exact
shape of a repair that costs more than the defect.

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
and one case of the system recording the opposite of what the book said.

**I went back and checked that last one, and it is real but rarer than it looked.** The book had
written *"if a cell WERE a closed system, its reactions would reach equilibrium and it would die"* --
a hypothetical, the kind of sentence that describes something in order to rule it out. The system
read it as a plain statement of fact. There is no "not" anywhere in it, so nothing simple would
catch this. **But counting how often that kind of sentence fools it: once in about three hundred, and
never once in the Wikipedia text.** The misattached-explanation bug is roughly ninety times more
common. **So it is a genuine flaw, correctly diagnosed, and not worth anyone spending a day on** --
which is the third time today that counting how often something happens has demoted it.

## QUESTIONS

None. This names a target; whether to spend on it is part of the Q89 decision already with the owner.

## NEXT STEPS

1. **Re-score COPULA on a second corpus** before the 48% is quoted anywhere. One scorer, one corpus,
   n=40 is exactly the shape of tonight's retraction.
2. **The definiendum-span defect is the named, sized target** -- ~95 noise rows per 6,000 sentences
   on the live corpus, one cause, already solved once for other patterns.
