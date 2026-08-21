# **THE TOP ITEM WAS ALREADY BUILT, ALREADY LIVE, AND ITS HEADLINE NUMBER IS UNDER A STANDING PROHIBITION AGAINST THE EXACT USE I WAS MAKING OF IT. THE CODE SAID SO IN THREE NUMBERED CORRECTIONS I HAD NOT READ.**

**`notes/STATUS.md` TOP ITEM read: *"WIRE DEFINITIONAL DIRECT-BANK... Evidence already on record:
64% MEANINGFUL (32/50) against an 8% floor."* I was one step from building on it.**

---

## 1. ALL THREE CORRECTIONS ARE IN THE DOCSTRING OF THE FUNCTION ITSELF

*`hdlab/reading_grounding_loop.py:1479`, dated **2026-08-20**, kept verbatim beside the design
rationale it corrects:*

| # | the correction |
|---|---|
| 1 | **IT IS ON THE LIVE PATH.** `substrate.py:538` passes `definition_map` into `checkpoint`. **Runtime evidence: 212 of 402 provenance rows carry `meaning_source=DEFINITIONAL_EXTRACTION`** -- a label a fact cannot carry unless the gate fired. |
| 2 | **WHAT SHIPS IS THE PHRASE, NOT THE HEAD.** Same rubric, same scorer, same day: **PHRASE 32% vs HEAD 4%**, head **NOT distinguishable from the distributional control** (Fisher one-sided p = 0.2475). |
| 3 | **THE 64% DOES NOT MEASURE THE FACTS THE GATE BANKS.** It scores *"is the extracted definition right for that sentence"*. **A STANDING PROHIBITION forbids placing it beside the 4% / 1-3% / 35% / 94% figures.** |

> ### **THE TOP ITEM DID PRECISELY WHAT CORRECTION 3 FORBIDS -- it put the 64% beside an 8% floor and called it the evidence for a wire that correction 1 says already exists.**

## 2. WHAT I ADDED THAT THE DOCSTRING DOES NOT HAVE -- **THE CITED ARTIFACT IS 100% HEAD-FORM**

*Every one of the 2,092 rows in `definitional_facts_v5.jsonl` ENUMERATED, not sampled:*

| | |
|---|---|
| objects that are MULTI-WORD (the validated phrase form) | **0 of 2,092** |
| rows carrying a multi-word `definiens_surface` **already on disk** | **2,079 (99.4%)** |
| rows where the phrase DIFFERS from the head | **2,082 (99.5%)** |

| subject | HEAD (what v5 banked) | PHRASE (validated, already in the same row) |
|---|---|---|
| ATP | `process` | **`a process called hydrolysis`** |
| Abdullah | `minister` | **`the Chief Minister of Jammu and Kashmir`** |

> ### **THE HEAD FORM DISCARDS THE DIFFERENTIA. "ATP is a process" is nearly contentless. And the validated form IS ALREADY IN THE SAME ROWS -- nothing needs re-extracting.**

**NOT A CLEAN WIN, AND THE SAMPLE SHOWS IT:** `Afghanistan -> "the prince was caught in another
media furore"` is extraction noise. **32% is not good; it is 8x the head form.**

## 3. THE RESIDUE, HONESTLY

**There is no wiring job.** *The re-scope is that the PHRASE is what is validated AND what already
ships, while the head-form v5 file is not evidence for it.*

## TLDR

The top item on our list was "connect the part that reads definitions off the page". **It has been
connected since 20 August, and the function's own notes say so in three numbered corrections I had
not read.**

Worse, the number the task was justified with -- a 64% quality score -- **measures something else
entirely.** It scores whether the extractor read the sentence correctly, not whether the facts it
banks are any good. **There is an explicit written rule against lining that number up against the
others, and our top item did exactly that.**

**What I did add:** the file cited as the evidence stores only single-word answers. All 2,092 of
them. It says *ATP is a "process"* where the same row already contains *"a process called
hydrolysis"*. **The one-word version throws away the part that carries the meaning, and the better
version is already sitting on disk beside it** -- so there is nothing to re-extract.

**It is still not good.** The phrase version is right about a third of the time, and some of what it
banks is plainly wrong. It is eight times better than the one-word version, not eight times good.

## QUESTIONS

None.

## NEXT STEPS

1. **STATUS TOP ITEM corrected in place.** *It called a live wire unwired and quoted a barred number.*
2. **Do not re-propose "wire definitional direct-bank".**
3. *Fifth prior-work catch tonight -- and the first where **the answer was in the docstring of the
   function I was about to change.** Reading the code I was about to edit would have been enough.*
