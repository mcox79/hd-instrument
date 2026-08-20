# THEORY DRILL 3: HARVESTED DEFINITIONS **DO** CARRY ENOUGH SIGNAL -- BUT THE PUBLISHED METHOD SITS CLOSE TO THE LINE THIS PROJECT HOLDS

**Continuing the owner's standing instruction to read the literature rather than derive everything
from our own output.** Drill 1 covered word-learning and pattern extraction; drill 2 the philosophy
of grounding. **This one asks the question our whole pipeline branch depends on: has anyone built
word meanings out of harvested definitions, and did it work?**

## THE ANSWER IS YES, AND IT IS A STRONGER RESULT THAN I EXPECTED

**Hill, Cho, Korhonen & Bengio, *Learning to Understand Phrases by Embedding the Dictionary*, TACL
2016.** Neural embedding models trained to map **dictionary definitions to representations of the
words they define** perform **as well or better than commercial systems that rely on significant
task-specific engineering**, on reverse-dictionary lookup and crossword solving, using only *"a
handful of freely-available lexical resources"*.

**➡️ SO THE PREMISE OF THE PIPELINE BRANCH IS SOUND: DEFINITIONS CONTAIN ENOUGH INFORMATION TO
SUPPORT REAL LEXICAL SEMANTICS.** That is not obvious and it is worth knowing -- **it means our
measured 32-68% MEANINGFUL harvest is a genuinely valuable raw material, not just a tidier way to be
wrong.**

## ⚠️ BUT TWO TENSIONS, AND BOTH MATTER FOR US SPECIFICALLY

**1. THE METHOD IS A LEARNED NEURAL ENCODER, WHICH IS NEAR OUR LINE.** Their result is obtained by
*training a model* to map definition text into a lexical embedding space. This project's charter
bars *"a borrowed embedding/parser/reader AS the meaning organ"* and forbids an LLM at inference.
**So the literature demonstrates the SIGNAL IS THERE while using a mechanism we have partly
foresworn.** *That is a real and uncomfortable position: it means our low numbers may reflect the
permitted mechanism rather than the material.* **It also means "definitions are useless" is NOT an
available conclusion** -- if we fail with them, the failure is ours, not the data's.

**2. THE DEMONSTRATED TASK RUNS IN THE OPPOSITE DIRECTION FROM OURS.** Their evaluation is
**reverse dictionary**: given a definition, retrieve the word. **The definition is the QUERY.** Our
substrate does the reverse -- given a word, produce and store a meaning -- and then, as measured
tonight, **never reads it back.** *Their success is evidence that definition text is richly
informative when something CONSUMES it. It is not evidence that storing definitions helps a system
that never consumes them, which is exactly our read-back gap.*

## 🔗 HOW THE THREE DRILLS FIT TOGETHER

| drill | finding | what it says about our branch |
|---|---|---|
| 1 (learning) | definitions alone teach humans poorly; **varied context** is what works | the harvest is a knowledge artefact, not a learner |
| 2 (philosophy) | meaning needs **a history of selection**; nothing here consumes the meanings | the read-back gap is the crux, not a missing feature |
| **3 (NLP)** | **definitions DO carry enough signal to build lexical semantics** | **the raw material is good; our extraction of it is the weak link** |

**➡️ ALL THREE POINT THE SAME WAY, FROM DIFFERENT DIRECTIONS: THE PROBLEM IS NOT THE MATERIAL WE
HARVEST. IT IS THAT NOTHING IN THE SYSTEM CONSUMES IT.** *Drill 1 says definitions need context to
teach; drill 2 says representations need use to mean; drill 3 says the information is present and
extractable by a consumer. **Three independent literatures, one conclusion, and it matches the gap I
measured empirically before reading any of them.***

## TLDR

I asked whether anyone has ever built word meanings out of harvested definitions, since that is what
this project's reading half does.

**They have, and it worked well** — a 2016 study trained on ordinary dictionaries and matched or beat
commercial systems at looking a word up from its description. So the raw material we have been
harvesting is genuinely good. **Our poor results are not the fault of definitions.**

**Two catches.** They got there by training a neural network on the definitions — which is close to a
line this project has deliberately drawn about not borrowing someone else's reader. So the
information is provably there; whether our permitted methods can get at it is a separate question.
And their task ran the other way round: they used a definition to *find* a word, whereas we produce
definitions and then, as I measured tonight, never read them again.

**Which is the same conclusion the other two readings reached from completely different directions.**
Educational research says definitions only teach when combined with varied encounters. Philosophy
says a representation only means something if something uses it and can be wrong. And now the
engineering literature says the information is there for anything that consumes it.

**Three separate fields, one answer: the material is fine, and nothing in our system uses it.**

## QUESTIONS

None. Q90 is open and unaffected by this -- it concerns the other branch.

## NEXT STEPS

1. **This raises the value of closing the read-back gap and lowers the value of harvesting more.**
   All three literatures agree the bottleneck is consumption, not supply.
2. **It also means a failure to make definitions useful would be OURS, not the material's** -- the
   signal is demonstrated to be present. That removes an excuse and should be recorded as such.
