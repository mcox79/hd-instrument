# T1 -- **I SPENT THE NIGHT RE-DERIVING A WEEK-OLD AUDIT. HERE IS WHAT WAS ALREADY THERE, WHAT I ADDED, AND WHAT I MISSED.**

`ORGAN_MAP` **§10.1/H2b**, dated **2026-08-15**, already contains the T1 finding I reported tonight
as new -- and contains **more of it than I found**.

---

## 1. WHAT WAS ALREADY WRITTEN DOWN

> **"The three passing checks each use a DIFFERENT comparator, and in each case it is the one FORAGE
> can beat."** -- and the full all-arms-all-metrics table, and **"Honest tier:
> MIDDLE_BAND_COMPARATOR_SELECTED."**

**That is my headline, verbatim, six days early.** It also names the confound I later quantified:

> *"I do not know how the held-out probe range [1000,4000] was sampled -- if the probes are drawn
> from the frozen corpora, the coverage metric favours FROZEN by construction. **That single check
> decides this.**"*

**AND THE TOOL TOLD ME.** `organ_map_cite.py H2` returns *"§6 STEP 1 (H2) is superseded"* as its
**first line**. I read that, recorded it, and then **re-derived §10.1 by hand over several hours
anyway.** *Running the check is not the same as reading the answer.*

## 2. ⚠️ WHAT I MISSED THAT WAS ALREADY THERE -- AND IT IS THE STRONGER POINT

> **"RANDOM 0.2675 and FIXED_LEAVE 0.2364 also crush the dominant share. Any non-frozen schedule
> spreads sources, so D1 CANNOT DISCRIMINATE FORAGING FROM A COIN FLIP."**

**I reported that FORAGE beats RANDOM on hit rate and called that "the organ doing its job."** The
existing audit had already shown that **the gate FORAGE actually passed -- D1 -- is one a coin flip
passes too.** *That is a sharper statement than mine and it was on disk.*

## 3. ✅ WHAT I GENUINELY ADDED

| | |
|---|---|
| **I RAN H2b'S DECIDING CHECK.** It was flagged as unchecked; I measured it. **Not corpus overlap** -- the probe is an external frequency list -- **but REGISTER: FROZEN banked 88.2% news/conversational, FORAGE 11.6%**, against a SUBTLEX-US-backed probe. **A 7.6x bias under a 1.20x margin.** | **closes H2b-5's open question** |
| **The attempt decomposition.** All arms read 10,000 sentences; FROZEN generated **4,568** extraction attempts at a **15.2%** hit rate, FORAGE **2,237** at **27.0%** -- the best of any arm. **It loses on volume, not on selection.** | new |
| 🔴 **H2b'S RECOMMENDED NEXT STEP IS IMPOSSIBLE.** It says the re-score *"is a re-scoring of an existing cell, **not a new run**."* **It is a new run.** Verified: zero list-valued per-arm fields in `metrics.json`, none in `units.jsonl`'s 5 units, a 9,482-byte stdout log. **The banked terms exist nowhere.** | **corrects the audit** |

## 4. ON THE PINNING, CAREFULLY -- BECAUSE I HAVE ALREADY OVERCLAIMED THREE TIMES TONIGHT

H2b-3 reverses the map's old "UNPINNED" label: **"THE BRAIN MATH IS PINNED."** The citations are
**Charnov 1976** (`leave when g'(t) < ρ`), **Constantino & Daw 2015** (discrete form + timed delta
rule), **Hayden 2011** (travel time RAISES the threshold, so a fixed threshold is a broken organ),
**Wittmann 2016** (two ρ timescales, **mixing weight UNPINNED and declared a fallback by the module
itself** -- correct handling).

**⚠️ EVERY ONE OF THOSE IS A *LEAVE-RULE* CITATION.** They pin *when to abandon the current source*.
**None of them addresses which source to open next** -- and the same map entry records **zero
occurrences** of `select_corpus` / `choose_corpus` / `next_corpus` / `pick_corpus` /
`corpus_selection` / `corpus_scheduler` repo-wide, with the readable universe a **hard-coded 4-entry
dict** against **36 corpora on disk**.

**➡️ SO: THE LEAVE OPERATION IS PINNED AND BUILT. THE CHOICE OPERATION IS NEITHER, AND THE
CITATIONS THAT REVERSED THE "UNPINNED" LABEL DO NOT COVER IT.** *Stated as a reading of the
citations, not a correction to the map -- I have been wrong three times tonight in exactly this
direction, and someone should check me.*

## 5. THE PROCESS FINDING, WHICH IS WORTH MORE THAN THE ORGAN FINDING

**The three-read rule worked. I ran read 3, it printed "superseded" in line one, and I proceeded to
re-derive the superseding document by hand.** The rule cannot make you read the thing it points at.

**The cheap fix is one habit: when a citation tool says "superseded -- see §X", OPEN §X BEFORE doing
any analysis of your own.** *Tonight that would have saved several hours and produced a better
result, because §10.1 contains a sharper version of my conclusion plus one I missed entirely.*

## TLDR

I spent tonight carefully working out that our "choose what to read next" experiment passed by being
graded against whichever baseline it could beat. **That exact conclusion was already written down a
week ago**, in the same document I consulted at the start — which told me, in its first line, that my
plan was out of date and pointed me to the page with the answer. **I noted that and then worked it
all out again from scratch.**

The old note is also sharper than mine: it points out that the one test our system passed is a test
**a coin flip also passes**. I'd missed that.

**Three things I did add.** The old note flagged one unchecked thing and said it *"decides this"* — I
ran it, and it does: **the winning setup was being tested in its own dialect, by about seven and a
half to one.** I found that the clever selector actually has the **best success rate of anything
tested** and loses only on volume. And I found that the old note's recommended next step **cannot be
done** — it assumes the data is still there, and it isn't.

**The real lesson is about me, not the system:** the tool that's supposed to stop me duplicating work
did fire, correctly, in its first line. I read the warning and didn't open the document it pointed
to. Running the check isn't the same as reading the answer.

## QUESTIONS

None.

## NEXT STEPS

1. **The gap is CHOICE, not LEAVE** — and the citations that pin this organ are all leave-rule
   citations. Worth a second pair of eyes before anyone builds on it.
2. **H2b-5's "re-score, not a new run" should be corrected in the map** — the data is gone.
3. Any foraging re-run must dump its banked terms, or the same wall arrives a third time.
