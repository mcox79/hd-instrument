# **THE CA3 MERGING FAILURE DOES NOT ARISE ON OUR DATA -- REAL WITHIN-LEMMA OVERLAP IS 0.0056 AGAINST A FAILURE THRESHOLD OF 0.22. AND *THAT* IS THE FINDING: THE PROBLEM IS UPSTREAM OF BOTH DG AND CA3.**

**I spent five turns characterising a real failure. This is the scoping check that says where it
applies, and the answer is: not here. Reporting it because a finding without its scope is how the
B1 "cliff" happened.**

---

## 1. THE MEASUREMENT

**Natural families on real data: the DG codes of the SAME LEMMA encountered in DIFFERENT sentences.**
*80 lemmas x 20 contexts each = 1,600 codes, built with the live `context_vector_masked` and the
live `DGProjection`.*

| | value |
|---|---|
| **WITHIN-lemma code cosine** | **0.0056** |
| CROSS-lemma code cosine | 0.0015 *(≈ the 1/dg random floor)* |

**Against the synthetic sweep that found the failure:**

| within-family overlap | Hebbian margin | |
|---|---|---|
| **0.0056 (REAL DATA)** | -- | ⬅️ **we are here** |
| 0.044 | +0.7205 | Hebbian FINE |
| 0.222 | +0.1179 | Hebbian FAILS |
| 0.560 | −0.1021 | Hebbian MERGES |

> ### **REAL OVERLAP IS 40x BELOW THE FAILURE THRESHOLD AND 8x BELOW EVEN THE "HEBBIAN IS FINE" CONDITION. FIXING THE COMPLETION RULE WOULD CHANGE NOTHING ON OUR DATA TODAY.**

## 2. ✅ WHAT THIS CONFIRMS AND WHAT IT SCOPES OUT

| claim | status |
|---|---|
| the Hebbian rule merges correlated memories (margin −0.1021) | ✅ **stands -- real, reproduced in two implementations** |
| the local error-driven rule fixes it, and 16x expansion makes it affordable (8 passes) | ✅ **stands** |
| **"this explains why CA3 contributes nothing in our substrate"** | 🚫 **NO. Scoped out.** |
| why CA3 contributes nothing here | ✅ **arm 2's answer all along: our codes are so near-orthogonal that completion is never REQUIRED** |

## 3. 🎯 **AND THE REAL QUESTION THIS EXPOSES**

**Two encounters with the SAME WORD, in different sentences, produce DG codes with cosine 0.0056 --
against 0.0015 for two encounters with DIFFERENT words.** *A ratio of under four, both essentially at
the random floor.*

> ### ***OUR REPRESENTATION BARELY ENCODES THAT TWO ENCOUNTERS ARE OF THE SAME WORD.***

**That is upstream of both organs.** *It is not DG separating too hard -- the raw context vectors,
measured earlier tonight, already carry almost no same-word structure (mean cos `+0.0078`,
`E[cos^2] 0.00474`, i.e. 82% of the Welch bound and therefore close to random by construction).*
**DG cannot preserve a similarity structure that was never there, and CA3 cannot complete a pattern
whose siblings it cannot recognise.**

***So the episodic-memory organs are working on inputs that contain almost no episodic structure. The
failure everyone has been chasing downstream is an ENCODING failure.***

⚠️ **HYPOTHESIS-PENDING-VET, and I am labelling it:** *whether raising same-word context similarity
would make the completion machinery earn its place is UNMEASURED. It is a prediction of this
analysis, not a result of it.*

## 4. 🔁 THE PATTERN THIS MAKES, FOR THE THIRD TIME TONIGHT

*The B1 "cliff": a real number, wrong scope.* *The "63% past 0.79 recovery": a real curve, wrong
operation.* **Now: a real failure, wrong regime.** ***In all three the measurement was sound and the
question was "does this apply here?" -- which is cheap, and which I keep reaching last.***

## TLDR

I spent five turns tracking down why one of our memory components does nothing, and found a genuine
flaw: with overlapping memories it blurs them together instead of telling them apart. **This is the
check on whether that flaw actually occurs in our system. It doesn't.**

Real memories in our system — the same word met in different sentences — overlap by **0.0056**. The
blurring problem only starts around **0.22**, forty times higher. **So fixing it would change nothing
today.**

**But the number that scopes the finding out is more interesting than the finding.**

Two encounters with the *same word* produce internal patterns almost as different as two encounters
with *completely different words* — 0.0056 against 0.0015, both barely above pure chance. **Our
system hardly registers that it has seen the same word twice.**

**That's upstream of both memory components.** It isn't that the separation stage works too
aggressively; the raw representations going in already carry almost no same-word signal. **A
component that reconstructs memories can't help when the memories it stores barely resemble their own
siblings.**

**So the memory machinery is operating on inputs that contain almost no memory structure**, and the
failure everyone has been chasing downstream is really a failure of what goes in.

**And this is the third time tonight** that a sound measurement had the wrong scope: a real number in
the wrong context, a real curve for the wrong operation, and now a real flaw in a regime we never
enter. **Each time the missing question was the cheap one — "does this apply here?" — and each time I
reached it last.**

## QUESTIONS

None.

## NEXT STEPS

1. **Do not build the CA3 completion fix for our current data.** *The regime it repairs does not
   occur; it is a correct fix for a problem we do not have YET.*
2. **The measured gap is encoding: same-word contexts are near-orthogonal (0.0056 vs 0.0015 random).**
   *That is where the episodic story actually breaks, and it is upstream of every organ I have been
   testing.*
3. **Ask "does this apply here?" EARLY.** *Third instance tonight; it is the cheapest question and I
   keep asking it last.*
