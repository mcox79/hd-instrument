# THEORY DRILL (owner-directed): A HUNDRED YEARS OF RESEARCH ON WHAT WE SPENT TONIGHT REDISCOVERING

**Owner, 2026-08-20, answering Q89:** *"yes this sounds like a promising angle, but you should also
drill relevant theory on reading around what you're trying to figure out. learning research,
linguistic research, even philosophy. **You should not try to figure this out on your own I'm sure
there is a hundred years of research on this**."*

**They were right, and the drill immediately found four literatures that speak directly to tonight's
findings -- including one that CONTRADICTS a conclusion I drew, and one that names a mechanism our
own architecture implements without knowing it.** Searches used generic published terminology only,
per the standing privacy rule; nothing about this project was sent anywhere.

---

## 1. ⚠️ **DEFINITIONS ALONE ARE A WEAK TEACHING SIGNAL -- AND THIS CUTS AGAINST MY OWN CONCLUSION**

**Miller & Gildea, *How Children Learn Words*, Scientific American 1987.** Children sent to
dictionaries **do not** learn words from the entries; they produce sentences with **incorrect**
meanings built from the definition. *"Knowing a dictionary definition is not the same as knowing how
to use the word."* What works is seeing words in **intelligible contexts**.

**WHY THIS MATTERS TO US.** Tonight I established that a definitional PHRASE beats a distributional
single WORD, three times over, and recommended the extraction route on that basis. **The literature
does not contradict that comparison -- but it warns that the destination is limited: a pile of
harvested definitions is not comprehension, and for humans it is measurably NOT how vocabulary is
acquired.** *If we take the reading-pipeline branch, we should expect a better KNOWLEDGE ARTEFACT,
not a better learner -- which is exactly what tonight's read-back gap already showed empirically.*

## 2. 🎯 **THE MECHANISM WE ALREADY IMPLEMENT HAS A NAME, AND IT SAYS WE ARE MISSING ONE INGREDIENT**

**Bolger, Balass, Landen & Perfetti, *Context Variation and Definitions in Learning the Meanings of
Words: An Instance-Based Learning Approach*.**

> Each encounter with a novel word forms a **distinct memory trace** encoding word-level and
> contextual features. Multiple encounters **in diverse contexts** reinforce overlapping traces,
> **eventually leading to abstraction of a core meaning independent of individual learning
> contexts.**

**THAT IS A DESCRIPTION OF OUR SUBSTRATE.** We store a context vector per encounter and abstract
across them. **The theory behind our own read-out is instance-based word learning, and we have never
cited it.**

**AND IT NAMES THE INGREDIENT WE LACK.** Their experiments presented rare words either **in one
sentence repeated four times** or **in four different sentences**, with and without a definition:

- **Context VARIATION is what lets core meaning features emerge** -- diversity, not volume.
- **Definitions interact with contexts** rather than replacing them; supplying a definition
  **REDUCED the benefit of contextual diversity.**

**➡️ WE SUM TEN NEAR-IDENTICAL CONTEXTS EXACTLY AS WE SUM TEN DIVERSE ONES. We have never measured
or exploited context variation -- and the theory says variation, not count, is the active
ingredient.** *This is a concrete, testable, theory-grounded hypothesis for why the distributional
read-out fails, and it is the first such hypothesis today that did not come from staring at our own
output.* **It is also a HYPOTHESIS, not a finding: nobody has tested it here.**

## 3. 📉 **THE ACHIEVABLE RATE FOR SINGLE-EXPOSURE WORD LEARNING IS LOW EVEN IN HUMANS**

**Nagy & Anderson 1984; Nagy, Anderson & Herman, *Learning Word Meanings From Context During Normal
Reading*, AERJ 1987.** Children acquire ~3,000 words a year incidentally from reading, and
**only about 5-12% of words are learned from a SINGLE exposure.** Gains from context in a controlled
reading study were **"small but reliable"** across grades.

**WHY THIS MATTERS.** Our distributional read-out scores 0-4% MEANINGFUL and we have been treating
that as damning. **The human single-exposure rate is 5-12%.**
**⚠️ AND THE COMPARISON IS NOT LEGITIMATE AS A DEFENCE** -- different task, different scorer,
different measure, and our numbers come from many exposures, not one. **I am recording it as
CONTEXT FOR EXPECTATIONS, not as an excuse**: the right lesson is that *incidental word learning is
intrinsically slow and low-yield*, so a mechanism that looks catastrophically bad against a
co-occurrence baseline may be failing at something that is genuinely hard, and the volume of
exposures is doing the work in humans.

## 4. 🔁 **OUR PATTERN EXTRACTOR IS A RE-INVENTION OF A 30-YEAR-OLD FIELD, AND THAT FIELD SOLVED THE PROBLEM I SPENT TONIGHT HAND-DIAGNOSING**

**Hearst 1992, lexico-syntactic patterns** (*"such NPY as NPX"*, *"NPX and other NPY"*) is the
canonical work on extracting is-a relations from text. **Snow, Jurafsky & Ng 2004, *Learning
Syntactic Patterns for Automatic Hypernym Discovery*** generalised hand-written regexes to
**dependency-path features learned from a seed set**, and automatically discovered patterns beyond
the hand-crafted ones.

**WHY THIS STINGS, USEFULLY.** Tonight I hand-scored four patterns, hand-diagnosed four distinct
failure modes, and hand-specified a marker-based fix. **The field's answer to exactly that situation
is: stop hand-writing patterns and LEARN them from a seed set.** Our five patterns (copula,
appositive, glossary-colon, called, refers-to) are a small hand-built subset of a space that has
been mined automatically for two decades.
*The hand-diagnosis was not wasted -- it is what tells us the failure modes are pattern-specific --
but it should not be the basis of the next build step.*

## 5. 🧩 **THE COPULA BUG I "DISCOVERED" IS A KNOWN, AND KNOWN-HARD, PROBLEM**

**Higgins 1979** distinguishes **FOUR** copular types -- predicational, specificational, equative,
identificational -- not the two I described. **Mikkelsen, *Specificational Subjects*;** and the
predicate-inversion analysis (specificational sentences as **inverted** predicational ones).

**AND THE HARD PART IS EXPLICIT IN THE LITERATURE:**

> *"Whenever the subject and predicate positions are inverted, specificational and predicational
> sentences are uniformly indistinct... **information structure** is what makes such sentences
> specificational."*

**➡️ SO MY SURFACE-MARKER FIX ATTACKS SOMETHING THE THEORY SAYS IS NOT FULLY DETERMINABLE FROM
FORM.** It measured **96% precision on 25 rows** -- which likely means those 25 were the
unambiguous cases, and **the marker will degrade on the ambiguous middle that the literature is
actually about.** *That is a limit I would not have known to look for, and it is exactly the kind of
thing the owner meant.*

---

## TLDR

The owner told me to go and read what a century of research already says, instead of working
everything out from our own data. **That was the right call, and it took about ten minutes to find
four things that matter.**

**One contradicts me.** I concluded that definitions are the good material. Research on children
shows that people given dictionary definitions largely fail to learn the word -- they produce wrong
sentences from them. Definitions are not how vocabulary is actually acquired; **varied encounters
are.** So the route I have been endorsing gets us a better reference book, not a better reader --
which is exactly what our own read-back failure showed tonight from a different direction.

**One describes our own machine back to us.** There is a theory called instance-based word learning
which says: every time you meet a word you store a trace of that encounter, and meaning emerges by
abstracting across **many DIFFERENT** encounters. That is precisely what our system does -- **except
for the word "different".** We add up ten similar sentences exactly as we add up ten varied ones,
and the research says **variety, not quantity, is the active ingredient.** We have never measured
it. That is the most promising untested idea to come out of today.

**One sets expectations.** Even children learn a word from a single encounter only about 5-12% of
the time. Our low numbers may reflect a genuinely hard problem rather than a uniquely broken system
-- though I am recording that as perspective, not as an excuse, because the measurements are not
comparable.

**And one is humbling.** The sentence-pattern extractor at the centre of tonight's work re-invents a
well-known method from 1992, and the field's answer to the exact problem I spent hours
hand-diagnosing is to **learn** the patterns automatically rather than hand-write them. Likewise,
the copula bug I "discovered" is a named distinction from 1979, and the literature says the hard
cases cannot be settled from sentence form alone -- which caps the fix I proposed.

## QUESTIONS

None. This was a directed drill and it delivered; the follow-ups below are mine to run.

## NEXT STEPS

1. **MEASURE CONTEXT VARIATION.** The instance-based literature says diversity across encounters is
   the active ingredient and we do not track it. **Cheapest real test: does a term's read-out
   quality correlate with the DIVERSITY of its encounters rather than their COUNT?** Everything
   needed is already in the traces.
2. **Do not build the marker-based copula fix as the next step.** The literature caps it (ambiguity
   is information-structural) and offers a better-founded alternative (learned dependency-path
   patterns, Snow et al.).
3. **Read the Bolger et al. paper properly** rather than from an abstract -- the PDF fetch returned
   binary and I have only the summary.
