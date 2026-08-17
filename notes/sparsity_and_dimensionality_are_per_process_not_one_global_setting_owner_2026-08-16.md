# SPARSITY AND DIMENSIONALITY ARE PER-PROCESS SETTINGS, NOT ONE GLOBAL SETTING

**Owner, 2026-08-16.** Recorded here because it was nearly lost twice: the owner typed it into the
status window's answer panel and the panel silently failed to write it (three defects, since fixed
-- `verification/test_board_answer_panel.py`), and a Director attempt to write a rescue note was
itself cancelled. It existed nowhere on disk until this file. Mirrored onto `notes/BOARD.md` under
ANSWERED so it is visible from the surface the owner actually reads.

---

## THE ANSWER, VERBATIM

> "remember that we have a phase diagram for substrate - we can set all variables, including
> dimensionality, wherever we want for each process. The brain does some in sparse space, some in
> dense, and we have the ability to change them on the fly."

---

## WHAT IT CORRECTS

**We had been treating sparsity and dimensionality as ONE GLOBAL SETTING.** Every sweep we have run
asks "what is OUR sparsity" and answers it with a single number applied everywhere. The owner's
point is that this is a self-imposed constraint, not a property of the substrate: we own a phase
diagram, every variable in it including dimensionality is settable independently, and it can be
changed on the fly. **They are per-process settings. The brain does exactly that -- some processes
in a sparse regime, some in a dense one.**

**CONSEQUENCE, and it is the operational part: stop asking "what is OUR sparsity" and specify it
PER ORGAN.**

### One number NOT to quote in support of this, and why

It is tempting to support the biology with "cortex ~0.2-0.3 dense, medial temporal ~0.2%". **Do not
put those two side by side.** `notes/drill_computational_theory_what_each_organ_computes_2026-08-16.md`
(sec 3a, lines 300-306) measured this and flagged it: the cortical **~0.2-0.3 is a Treves-Rolls
SPARSENESS STATISTIC over a tuning distribution** (Rolls & Tovee), while the **MTL ~0.2% is an
ACTIVE FRACTION** (Waydo et al. 2006). They are different quantities. Quoting them as a contrast is
the project's own "a number may not be carried between populations" fault committed in the biology
instead of in our metrics. `ORGAN_MAP` B4 gets this right; several downstream summaries do not.

**The owner's claim does not need that pairing and is not weakened by dropping it.** "The brain does
some in sparse space, some in dense" is supported by the regime difference between hippocampal
storage and cortical representation without asserting a numeric comparison between two different
statistics.

---

## WHY THIS MATTERS NOW: IT CONVERGES WITH TWO INDEPENDENT 2026-08-16 FINDINGS

Neither of these was derived from the owner's remark, and neither was derived from the other. That
is what makes the convergence worth recording rather than merely agreeing with.

### 1. SPARSIFY THE ADDRESS, KEEP THE VALUE DENSE

From the computational-theory drill
(`notes/drill_computational_theory_what_each_organ_computes_2026-08-16.md`, item B4). The theory
statement is that **separation IS the destruction of similarity** -- it is the function of a sparse
code, not a side effect. A code optimised to make two similar things orthogonal is optimised to make
a similarity judgement impossible. So the address and the value want OPPOSITE regimes: a **sparse
KEY** addressing a **dense graded VALUE**, returned by link and never reconstructed.

This is the **`LINK-NOT-RECONSTRUCT`** design, and it is not new -- it was banked on **2026-07-04**
in `notes/research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md` and
**has never been implemented**. It is carried as `A8_LINK_NOT_RECONSTRUCT` in
`notes/drill_brain_partial_cue_retrieval_what_the_cue_actually_is_2026-08-16.md` and as ITEM 4 in
`notes/PLAN_NEXT_24H.md`. **It is a two-regime design, and it sat unimplemented for six weeks while
we ran one-regime sweeps.** That is the cost of the global-setting assumption, stated concretely.

### 2. THE SPARSITY SWEEP: THE PINNED MTL BAND WAS THE WORST MEANING ZONE

Measured (`sparsify-right-object.json`, POP_FULL, exact key, d=1024, hit@1; transcribed in the drill
at sec 3b):

```
f=0.002  0.0396   <- the PINNED MTL band
f=0.005  0.0496
f=0.010  0.0606
f=0.020  0.0706
f=0.050  0.0696
f=0.100  0.0774   <- best
f=0.200  0.0749
f=0.300  0.0769
f=0.500  0.0759
DENSE (no cap) 0.0744
```

The cell's own note: *"the PINNED MTL band (0.2-1%) was the WORST meaning zone in the sweep."*

**This LOOKED like a contradiction of the biology** -- we copied the brain's most explicitly cited
sparsity parameter and it was the worst point on the curve. **It is what the theory predicts once
you stop applying a single regime everywhere.** We applied the optimum for *storing many patterns
without interference* and then measured *similarity structure for a meaning judgement*. Those are
different objectives. The right reading is not "the brain's number is wrong" and not "sparse coding
fails"; it is **we applied one organ's regime to another organ's job**, which is precisely the error
the owner's remark names.

SCOPE, stated: one sweep, exact-key operating point, hit@1, d=1024, one population. It is a
diagnostic that explains a shape; it clears no floor and decides no gate.

---

## WHAT CHANGES

1. **Sparsity and dimensionality become PER-ORGAN parameters in the organ map, not one global
   knob.** Any future sweep names the ORGAN it is sweeping for and the OBJECTIVE it is optimising
   (store-many-without-interference vs preserve-similarity-for-judgement), because those two have
   opposite optima and a single number cannot serve both.
2. **`LINK-NOT-RECONSTRUCT` stops being a shelved design.** It is the first concrete two-regime
   build and it is already specified in three documents.
3. **A retired question: "what is OUR sparsity".** It has no answer, and asking it produced a sweep
   whose best single compromise (~10%) is statistically at parity with doing nothing at all
   (0.0774 vs 0.0744 DENSE) -- which is what a single setting forced to serve two opposite
   objectives should look like.

**NOT claimed here:** that per-organ settings will raise any score. Nothing has been run under this
framing. This note records a correction to an assumption and the two findings that converge with
it. It is a design position, not a result, and it should be re-read as one until a can-fail cell
with a real floor says otherwise.

---

**Provenance.** Owner's words: quoted verbatim above, and recorded on `notes/BOARD.md` (ANSWERED).
Reasoning: recorded by `hdi_testbed` 2026-08-16 while fixing the panel that lost the answer. Every
number above is quoted from the named artifact and was re-read on disk on 2026-08-16; none is from
recollection. The cortical-sparseness caveat is this note's own correction to the framing it was
handed, on the authority of the drill's sec 3a.
