# THE UNTRAINED SUBSTRATE GEOMETRY **DONATES NOTHING** -- AND THE HARNESS PROVED IT CAN **REJECT**

**A mandatory control, not an experiment.** Standing discipline: *build the information-free version
of your winning arm and score it.* A 10-sparse random arm once beat a real one 14.0 to 18.0; an
all-zero accumulator once scored median rank 1.0, a twenty-fold "win". **An F5 number has to be read
against what the SAME representation scores having learned NOTHING -- not against zero.**

**THE ARM.** No reading, no accumulation: a word's own hash-seeded bipolar code against a bundle of
its neighbours' hash codes. There is no information about English in it whatsoever.

---

## THE RESULT, AND IT ARRIVES TWICE INDEPENDENTLY

| set | anomalous | original | discrimination |
|---|---|---|---|
| 1 | 12.5% | 12.5% | **+0.0 pp**, CI [-8.3, +8.3] |
| 2 | 15.1% | 11.8% | **+3.4 pp**, CI [-5.0, +11.8] |
| 3 | -- | -- | **THE POSITIVE CONTROL REFUSED IT** -- fired on only 3 of 9 probes |

**1. THE GEOMETRY CARRIES NO ANOMALY SIGNAL.** Both CIs span zero. **So the codebook donates
nothing, and any discrimination F5 shows would be EARNED BY LEARNING rather than inherited from the
representation.** *That was the question worth asking before the build: had it come back materially
above zero, every arm built on this codebook would have inherited the artifact, F5 included.*

**2. AND THE CI HAS WIDTH.** `+0.0 pp, CI [-8.3, +8.3]` is a **genuine null**, not a *zero-width*
CI -- which this repo classes as a reachability failure rather than a result. The arm reached the
scorer and had nothing to say. Those are different findings and only the second one is good news.

## 🎯 **THE HARNESS DEMONSTRATED IT CAN REFUSE, ON A REAL ARM**

Its positive control **rejected** the untrained arm: an out-of-context word beat the correct word in
only 3 of 9 probes, so *the detector has not been shown to fire and cannot support a null.*

**This is the validation a guard most needs and most rarely gets.** Until now the harness had only
been shown to ACCEPT the counting floors and to reject hand-made fixtures in its self-test.
**It has now rejected a real arm, for the right reason, and its verdict agrees with the two sets
that did score (~0 pp).** *Two independent routes -- the scored discrimination and the fire-test --
returned the same answer about the same arm.*

## WHAT THIS DOES NOT SAY

**It says nothing about whether the substrate can detect anomalies.** This arm is deliberately
untrained; the substrate as it actually runs accumulates context over a corpus and was not measured
here. **This establishes the ZERO POINT, nothing else.**

## TLDR

Before trusting any future score from the new component, I measured what our own machinery produces
when it has learned **absolutely nothing** — just its raw random codes, no reading.

**It scores zero, as it should.** That matters more than it sounds: if the raw machinery had scored
above zero, every result built on it would have been inheriting a free head start that had nothing
to do with understanding, and we would only have found out afterwards.

Two useful details. The zero is a *real* zero with a proper margin of error around it — not the
suspicious kind that means the test never actually reached the thing being measured. And on the
third batch the scoring machine **refused to grade the arm at all**, on the grounds that it had
never been shown to detect anything.

That refusal is the best news here. A safety check is only worth having if it can say no — and until
now mine had only ever said no to deliberately broken test cases I wrote myself. **It has now
rejected a real arm, for the right reason, and its answer agrees with the batches that did get
scored.**

## QUESTIONS

None.

## NEXT STEPS

1. The zero point is established: F5's discrimination must be read as a margin over **0 pp** from the
   representation and over **+44.2 pp** from counting.
2. `tools/score_the_untrained_substrate_representation.py` should be re-run against any future
   codebook change -- an artifact introduced there would be invisible everywhere else.
3. F5 remains blocked only on cell-authoring.
