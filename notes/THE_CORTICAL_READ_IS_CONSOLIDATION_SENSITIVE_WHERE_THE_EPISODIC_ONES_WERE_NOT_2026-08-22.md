# ✅ **B3' IS LIVE AND CONSOLIDATION-DEPENDENT. THAT WAS THE OPEN QUESTION; QUALITY IS A DIFFERENT ONE.**

**The defect B3' was built for**, in the substrate's own slot table: *"ablating consolidation to ZERO
left the read-out identical in 9 of 12 cells because every retrieval route addressed the EPISODIC
store. Under CLS, consolidated knowledge is read from CORTEX."*

**The slot has sat at `NEEDS_ADAPTER` on the grounds that "no SCORED path calls it yet" -- so nobody
had asked the cheaper prior question: does the cortical route respond to consolidation at all?**

---

## THE MEASUREMENT -- ONE VARIABLE, WITH THE CONTROL FIRST

Same seed (`20260819`), same `n_dim=512`, same 400 sentences, same 8 probes. **Only the ablation
changes.**

| | result |
|---|---|
| **POSITIVE CONTROL** -- identical config run twice | **identical on `8/8` probes** |
| **`ablate=('consolidation',)`** vs base | 🔑 **CHANGED on `8/8` probes** |

**The control is load-bearing and is why the diff means anything:** had the run been
non-deterministic, an 8/8 difference would have shown only that the substrate is noisy. It is
deterministic, so the difference is the ablation.

> ### **THE CORTICAL READ IS THE ROUTE THAT NOTICES CONSOLIDATION. THE EPISODIC ROUTES WERE NOT -- THAT IS THE WHOLE POINT OF B3', AND IT IS NOW DEMONSTRATED RATHER THAN ARGUED.**

*Neither arm returns empty (`0/8` empty both ways), so this is not the degenerate case where an
ablated arm simply stops answering.*

## 🚫 WHAT THIS DOES **NOT** SHOW, AND IT IS THE BIGGER HALF

**SENSITIVITY IS NOT CORRECTNESS. A route that responds to consolidation by returning DIFFERENT
NOISE is still returning noise**, and on inspection that is a live possibility:

```
probe 'water'   base: lory 0.087 | lynde 0.075 | swim 0.049
probe 'king'    base: lynde 0.085 | meet 0.051 | little 0.044   ablated: swim 0.004 | win -0.002
```

**Those terms are not obviously related to their probes, and the scores are small.** So:

- ✅ **ESTABLISHED: the route is live, deterministic, and consolidation-dependent.**
- ⛔ **NOT ESTABLISHED: that what it returns is right.** No task, no floor, no CI. **This is a
  DIAGNOSTIC and it may not decide anything** -- the standing rule is that a statistic the mechanism
  optimises may diagnose, never decide, and "did the output change" is exactly such a statistic.
- ⚠️ **SCOPE: `n=8` probes, one seed, 400 sentences, `n_dim=512`.** Small. The claim is qualitative
  (does it respond at all), which is what 8/8 with a clean control can carry; nothing quantitative
  should be read off it.

## 🔻 **FOLLOW-UP: IT IS SENSITIVE BUT NOT DETECTABLY *SELECTIVE* -- AND THE INSTRUMENT MAY BE THE PROBLEM**

The section above flagged that the returned terms *look* unrelated. **That is measurable with a
yardstick the substrate never sees (WordNet Wu-Palmer), against the correct floor: a RANDOM term
drawn from the SAME consolidated pool** -- not random English, which would be a strawman.

| arm (12 probes, 800 sentences, top-5) | mean | median | n |
|---|---|---|---|
| `recall_cortical` terms vs the target | `0.3829` | `0.3333` | 53 |
| **RANDOM term from the same pool -- THE FLOOR** | `0.3737` | `0.3333` | 56 |
| | **`+0.0092`** | **identical** | |

*Yardstick control: `wup(dog,cat) = 0.857` vs `wup(dog,democracy) = 0.154`, so the measure does
discriminate.*

> ### **THE INFORMATION-FREE TWIN TIES THE REAL ARM. On this instrument the cortical read shows NO detectable semantic selectivity -- it responds to consolidation, but WHICH terms it returns is not distinguishable from drawing from the pool at random.**

⚠️ **AND I AM NOT CALLING THAT A NULL, FOR A SPECIFIC REASON: BOTH MEDIANS ARE EXACTLY `0.3333`.**
That is the signature of WordNet's taxonomy structure dominating the measure rather than of two arms
genuinely tying -- **a blunt instrument, not necessarily an empty arm.** *Reading an underpowered or
blunt null as a capability statement is this project's most expensive recorded error.*

**So the honest statement is narrow: the cheapest available check does NOT show selectivity, on
`n=53` vs `56`, with a 26-term pool, one seed, and a yardstick whose own floor may be doing the
work.** ➡️ **What a better test needs: a larger consolidated pool, a similarity measure without a
structural floor, and probes whose correct answers are known in advance.**

## 🔬 **RE-RUN ON THE SHARPER YARDSTICK -- AND THE INTERESTING NUMBER IS THE FLOOR, NOT THE ARM**

The blunt-instrument suspicion was right. **Re-measured with the sensorimotor norms cosine, which has
no taxonomy floor** (`cos(dog,cat) = 0.932` vs `cos(dog,democracy) = -0.693`) **and which is
INDEPENDENT of the mechanism for a reason established earlier in this session: `read()` never
consults the norms, so the substrate cannot have fitted to them.** 16 probes, 2,500 sentences.

| arm | mean | median | n | 95% CI (bootstrap) |
|---|---|---|---|---|
| `recall_cortical` top-5 vs target | `0.2524` | `0.2523` | 53 | `[+0.1452, +0.3535]` |
| **RANDOM term, same pool -- THE FLOOR** | `0.1850` | `0.1854` | 105 | `[+0.1078, +0.2673]` |

**delta `+0.0675`, roughly 7x the WordNet delta -- so the blunt instrument WAS hiding it.**
🔻 **BUT THE CIs OVERLAP HEAVILY, SO IT DOES NOT CLEAR THE BAR.** *A gate here is a CI-SEPARATED
margin; this is not one, and the honest verdict is NOT_SEPARATED at n=53 vs 105.*

> ### 🔑 **THE NUMBER I WAS NOT LOOKING FOR: THE POOL ITSELF SITS AT `0.1850` AGAINST A GLOBAL RANDOM-PAIR FLOOR OF `-0.0131`.**
> **Whatever gets CONSOLIDATED is already far closer to the probe targets than words in general.** So
> the decomposition worth testing is:
> **(1) POOL-LEVEL SELECTION -- apparently strong, and doing most of the work.**
> **(2) WITHIN-POOL RANKING -- not established (`+0.0675`, CIs overlap).**
> ➡️ *That would mean the cortical read's value lies in WHAT IS CONSOLIDATED rather than in how it
> ranks what it already holds -- a materially different claim from "the read-out is good", and a
> different thing to build on.*

⚠️ **AND THAT COMPARISON CROSSES POPULATIONS, SO IT IS INDICATIVE AND NOT A TEST.** The `-0.0131` was
random pairs drawn from the WHOLE norms table; the `0.1850` is pool terms against THESE 16 probe
targets. **Same yardstick, different populations -- exactly the crossing this project forbids in a
verdict.** *Stated because the size of the gap makes it worth measuring properly, not because it is
measured.*

## 🧪 **THE POOL-SELECTION TEST, ON MATCHED POPULATIONS -- LARGE EFFECT, NOT ESTABLISHED**

The right test: score **CONSOLIDATED terms** and **terms the substrate READ and did NOT consolidate**
against the SAME 16 probe targets, on the same yardstick. *Targets were fixed before the pool was
inspected, so they are not fitted to it.*

| population (**unit = TERM**) | mean cosine to the 16 targets | n_terms | 95% CI |
|---|---|---|---|
| **CONSOLIDATED** | `0.1966` | **`24`** | `[+0.0634, +0.3173]` |
| read but NOT consolidated | `0.0452` | 600 | `[+0.0186, +0.0713]` |

**delta `+0.1514` -- roughly 4x the floor -- and 🔻 NOT CI-SEPARATED (`0.0634` vs `0.0713`, they
just overlap).**
✅ **THE OBVIOUS CONFOUND IS DEAD: median corpus frequency is `2` in BOTH populations**, so this is
not "consolidated = frequent" wearing a semantic costume.

> ### 🔻 **AND I CAUGHT MYSELF OVERSTATING IT. MY FIRST RUN BOOTSTRAPPED OVER 400 *DRAWS* FROM 24 *TERMS* AND REPORTED `[+0.1551, +0.2316]` vs `[-0.0190, +0.0605]` -- CLEAN SEPARATION.**
> **The unit of analysis is the TERM, not the pair.** Resampling pairs treats 24 terms as 400
> independent observations and shrinks the interval to something the data cannot support. *Same
> numbers, same code, one honest choice -- and it is the difference between a result and a
> hypothesis.*

**HONEST VERDICT: the effect is LARGE and the direction is clear, but it CANNOT BE ESTABLISHED at
`n=24`.** *Hypothesis, not finding.*

### 🔑 **AND THE POOL SIZE IS ITSELF THE MORE INTERESTING NUMBER: 2,500 SENTENCES PRODUCED `30` CONSOLIDATED TERMS (24 with norms).**

```
door eyes face garden glass glove golden great green hall hear kid little manage
moment mouse pair pool slowly swim table try win walk
```

**That is the entire consolidated output of a 2,500-sentence read.** ➡️ **Whatever the selection is
doing, it is doing it to a set this small -- which caps what any cortical read can return and is
why `n=24` is not fixable by scoring harder. It is fixable by consolidating more.**

## ➡️ WHAT IT CHANGES

**B3' moves from *"no evidence it does anything"* to *"demonstrably the consolidation-sensitive
route, quality unmeasured"*.** That is a materially better starting position for whoever builds the
scored path, and it removes the cheapest way that work could fail: **discovering after the fact that
the route was inert.**

**The scored path remains the actual deliverable**, and it needs a held-out task with floors, which
is a cell run.

---

## TLDR

We have a component built on a specific complaint: when we switched off the system's "settled
knowledge" store, its answers didn't change at all — meaning nothing was actually reading from that
store. This component was supposed to be the part that does.

Nobody had checked whether it works, because the plan was to wait until we could score it properly on
a task. I asked the cheaper question first: **does switching off settled knowledge change what this
component says?** It does, on all eight test cases, and I verified first that the system gives
identical answers when nothing changes — otherwise the difference would have proved nothing.

So the part is genuinely plugged into the thing it was meant to read from. **What it says still looks
wrong** — asked about "water" it offers unrelated words — but that's a separate question needing a
proper scored test. The useful part is that anyone building that test now knows they aren't measuring
something inert.

## QUESTIONS

None.

## NEXT STEPS

1. **The scored path is still the deliverable** and still needs a cell run: a held-out task where
   consolidated knowledge is required, with floors and a CI.
2. 🚫 **Do not quote `8/8` as evidence the cortical read WORKS.** It is evidence the route is
   connected to consolidation, nothing more.
3. The retrieved terms looking unrelated is itself a lead worth a look — but on this evidence it is
   an impression from 8 probes, not a finding.
