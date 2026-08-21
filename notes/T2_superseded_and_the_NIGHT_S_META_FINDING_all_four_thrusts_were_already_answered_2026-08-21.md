# T2 SUPERSEDED -- AND THE NIGHT'S META-FINDING: **ALL FOUR THRUSTS I PLANNED WERE ALREADY ANSWERED ON DISK. FOUR FOR FOUR. NONE NEEDED A RUN TO FIND OUT.**

---

## 1. T2 IS SUPERSEDED, AND IT IS THE CLEANEST OF THE FOUR

**T2 proposed:** *"replace our invented arithmetic (β=0.5, λ=0.1) with genuine **parallel cue-based
retrieval with similarity-based interference**, scored by the semantic comparator. Test on >=2
semantically plausible candidates, at n in the hundreds."*

**`tools/experiment_index.py query "cue based retrieval"` -> 4 cells, 4 landed.**
**`exp_coref_cue_based_retrieval_actr_activation_v1`, landed 2026-08-14: `HARD_FAIL`.**

> `delta vs base_principle_b = **-0.1348 (CI -0.2500..-0.0337)** | PRIMARY P = link-level pronoun
> accuracy on the **COMPETITIVE subset (>=2 gn-compatible candidates)**, pooled over both gold sets.`

**That is my proposed mechanism, on my proposed can-fail test, already run -- and it made
coreference 13.5 points WORSE with a CI that excludes zero.** Not a null. A CI-separated harm.
*Two neighbours agree it is worked ground: `exp_coref_actr_tiebreak_under_centering_v2` = `VACUOUS`,
`exp_coref_cb_tier_error_anatomy_v1` = `RANKING_DOMINATED`.*

### ⚠️ AND THE HONEST READING IS **NOT** "CUE-BASED RETRIEVAL IS WRONG"

The brain-side account (Lewis & Vasishth 2005; McElree SAT; Jäger et al. 2017) is **pinned as an
ORDERING**, and `ORGAN_MAP` is explicit that *"the cue weights and the activation equation are
UNPINNED -- the literature gives an ORDERING, not numbers."*

**So a brain-faithful mechanism lost to our invented arithmetic, which the standing rule says is
`presumed impl-bug until proven structural`.** The open question is therefore **"why did our ACT-R
activation lose 13.5 points?"** -- a diagnosis on an existing artifact -- **not "let us build
cue-based retrieval", which is done.**

## 2. 🔴 **THE META-FINDING, AND IT IS THE MOST USEFUL THING I FOUND TONIGHT**

| thrust | what I planned | what disk said | cost to find |
|---|---|---|---|
| **T1** foraging | "organ MISSING, math UNPINNED, run floors RANDOM + FROZEN" | **exists, WIRED, math PINNED (Charnov 1976), both floors already run at 10k sentences/arm** | 1 command |
| **T2** coreference | "replace our arithmetic with cue-based retrieval" | **`HARD_FAIL`, -0.1348 CI [-0.2500,-0.0337], on that exact test** | 1 command |
| **T3** graded codes | "three switches built and default-OFF -- turn them on" | **default-ON at `:103`; a landed cell carries a field named `premise_correction` recording a PRIOR dispatch making my identical mistake** | 1 grep |
| **T5** orthographic floor | *(not planned -- found by following T3)* | already measured; **and the floor named "MAX" is a z-SUM scoring 30% below its own component** | 2 reads |

**FOUR FOR FOUR. Every one found by READING, none by running. Total cost: minutes.**

**➡️ THE DEFECT IS NOT THAT I SKIPPED THE PRIOR-WORK CHECK -- IT IS THAT I WROTE THE ENTIRE PLAN
BEFORE RUNNING ANY OF THEM.** The three reads exist, are documented in `CLAUDE.md`, and I ran them
**per-thrust, after the plan was committed.** Every one of them fired. *A prior-work check performed
after the plan is written is a correction mechanism, not a planning input -- and it costs a plan
rewrite instead of costing one command.*

**RULE, and it is the cheapest one available: RUN THE THREE READS ON EVERY CANDIDATE *BEFORE*
RANKING THEM, NOT AFTER COMMITTING TO THEM.** *`organ_map_cite.py` alone answered T1 and T3 in its
FIRST LINE both times.*

### THE GENUINELY GOOD NEWS, STATED PLAINLY

**Nothing was wasted.** No compute was spent on any superseded thrust -- the reads caught all four
before a single experiment was launched. **And three of the four produced a BETTER finding than the
work they replaced:**
- T1 -> the anti-skew organ read its way to **63.2% biology** while winning on its own currency;
  MVT is a **leave** rule and is silent on **where to go**.
- T3 -> the live grounding path pairs a **graded field with a sign-quantised query**, the exact
  configuration the repo's own docstring calls *"worse than either"*.
- T5 -> **pure spelling beats the meaning read-out, CI-separated**, and the "strongest zero-meaning
  floor" is 30% weaker than its own component.

*The archive did not just refuse the plan; it handed back sharper questions than the ones I asked.*

## TLDR

I wrote a four-part plan tonight. **Every single part turned out to be already answered, sitting on
disk.** Finding that out cost about one command each.

The one I hadn't checked yet was "improve how the system works out who *he* refers to." The exact
change I proposed — swapping our home-made formula for the version from the reading research — **was
built a week ago and made things 13.5 points worse**, with the uncertainty range comfortably clear of
zero. So the open question isn't "should we build it" — it's "why did our version of it lose?"

**The pattern is the finding.** I didn't skip the checks — I ran them, and each one fired. **I just
ran them after writing the plan instead of before.** A check done afterwards costs a plan rewrite; the
same check done first costs one command. One tool answered two of the four **in its very first line**.

**Two things worth saying so this doesn't read as a bad night.** Nothing was wasted: no computing time
went into any of the dead ends, because the reading caught them all before anything was launched. And
three of the four dead ends handed back a *better* question than the one I'd asked — including that
the system's meaning-matching is currently beaten by simple letter-pattern comparison.

## QUESTIONS

None.

## NEXT STEPS

1. **Adopt the ordering rule:** three reads on every candidate **before** ranking, not after.
2. **The real coreference question** is a diagnosis of an existing artifact: *why did our ACT-R
   activation lose 13.5 points to our own arithmetic?* Brain-faithful losing is presumed an
   implementation bug until shown structural.
3. Two diagnostics are in flight: the corrected loaded-foundation read, and the tie mass that
   decides whether T5's spelling-beats-meaning result survives.
