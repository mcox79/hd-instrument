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
