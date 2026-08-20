# BRAIN-FOUNDATIONAL ANSWER (owner-directed): THE MISSING CONSUMER IS **F5**, AND WE **QUANTISE WHERE THE BRAIN IS GRADED**

**Owner, answering Q90:** *"if you've drilled this online and it points in other directions to be
brain foundational, follow those directions. if brain foundational points in this direction, do it
again and verify we're actually brain foundational."*

**So the deciding criterion is brain-fidelity, and my three earlier drills had covered learning
research, philosophy and NLP -- but NOT neuroscience. This is that drill, and it changes the
direction.**

## 1. THE NEUROSCIENCE NAMES THE CONSUMER THE OTHER THREE DRILLS DEMANDED

The convergent conclusion of drills 1-3 was: **nothing in this system consumes the meanings it
stores, so nothing can select them.** The obvious brain question is therefore: **what consumes
meaning in the brain, and what selects semantic representations?**

**The answer is the N400.** It is read in the current literature as **an implicit semantic
prediction error that drives adaptation of future expectations** -- a temporal-difference
prediction error *at the level of meaning*. And the learning consequence is measured, not assumed:
manipulating expectancy changes N400 amplitude **and later implicit memory** for the word, with
faster identification of previously **unexpected** words.

**➡️ THE BRAIN'S CONSUMER OF MEANING IS PREDICTION DURING COMPREHENSION, AND BEING WRONG IS THE
LEARNING SIGNAL.**

## 2. ⚠️ AND `ORGAN_MAP` ALREADY HAD IT -- MORE PRECISELY THAN I DID

**Fourth time tonight the answer was already in an artifact.** `ORGAN_MAP.md` **F5 — Coherence
monitor (the N400 generator)**, already flagged *(MISSING — and a legitimate PHASE-B target)*:

> **N400 amplitude = the MAGNITUDE OF UPDATE forced on a running probabilistic situation-model
> representation** by the incoming word -- `‖Δ situation_model‖`, a prediction error against the
> **CURRENT DISCOURSE STATE, not against a fixed template** (Rabovsky, Hansen & McClelland 2018;
> Kutas & Federmeier 2011). **The reference point is pinned; the norm and the update rule are
> UNPINNED.** The error is **precision-weighted** -- form pinned, precision estimator UNPINNED.
> **OURS: NONE.**

**THIS CORRECTS MY OWN FRAMING.** I described the mechanism as *"predict the next word's meaning and
learn from being wrong"*. **The pinned version is a prediction error against a RUNNING DISCOURSE
STATE, not against a word's stored meaning.** That is a different and larger object -- and it
depends on **F6 (Construction-Integration, also MISSING)**. *So this is not a small build, and I
should not present it as one.*

## 3. 🔴 **THE VERIFICATION THE OWNER ASKED FOR: WE ARE *NOT* BRAIN-FOUNDATIONAL HERE, AND IT IS MEASURABLE**

The closest organ we own is **G2 — prediction error / surprise gating of plasticity**
(`hdlab/predictive_coding.py`). `ORGAN_MAP`'s verdict:

> **FIDELITY: RIGHT-OP-WRONG-METRIC** — the residual-gated Hebbian shape is exactly the brain's, but
> the residual is computed on a **`sign()`-quantised prediction**, so **a large graded error and a
> small one that flips the same bits are indistinguishable.** **No precision term. WIRED: NO.**

**And the consequence was measured:** `exp_pc1_predictive_coding_residual_gate_v1` MIDDLE_BAND --
at threshold 0.3, **skip = 0.00, byte-identical to ungated. THE GATE NEVER FIRED.**

**➡️ THAT IS EXACTLY WHAT A QUANTISED ERROR SIGNAL PREDICTS.** Sign-quantising the prediction
collapses a graded residual into a few discrete values; a threshold over that either never fires or
always fires. **The organ has the brain's SHAPE and not its METRIC, and the null it produced is a
consequence of the infidelity rather than evidence about the mechanism.**

## 4. 🧩 **AND THE SAME DEFECT APPEARS TWICE -- WE QUANTISE WHERE THE BRAIN IS GRADED**

| site | the defect |
|---|---|
| `predictive_coding.py` | residual computed on a **`sign()`-quantised** prediction (G2, above) |
| `canonicalize` (`reading_grounding_loop.py:776`) | **`np.sign(new_raw_sum)`** on the query, while anchors are graded |

**Two independent organs, the same substitution: a graded quantity replaced by its sign.** *The
project already carries `GRADED_COMPARATOR=True` as a fix on the anchor side while the QUERY side is
still hard-signed.* **This is a candidate project-wide fidelity gap, and it is exactly the kind the
standing rule names: COPY THE COMPUTATION EXACTLY (graded, precision-weighted error), SWEEP THE
PARAMETER (thresholds, gains).** *Stated as a hypothesis linking two documented facts -- I have not
measured a shared cause.*

## 5. ➡️ **THE ANSWER TO THE OWNER'S FORK**

**Brain-foundational points AWAY from "supply more perceptual norms" and TOWARD the coherence
monitor.** Per their instruction -- *"if it points in other directions to be brain foundational,
follow those directions"* -- **that is the direction.**

**AND IT CONVERGES WITH EVERYTHING ELSE MEASURED TONIGHT, FROM FOUR INDEPENDENT DIRECTIONS:**

| source | conclusion |
|---|---|
| **measurement** (mine, tonight) | nothing reads the banked meanings; three attempts to make retrieval use them failed |
| **learning research** | definitions teach only alongside varied encounters |
| **philosophy** | referential grounding requires a **history of selection** -- i.e. use, with consequences |
| **neuroscience + ORGAN_MAP** | the consumer is **F5**, it is **MISSING**, and our nearest organ is **right-op-wrong-metric and never fires** |

**Four independent routes, one target.** *That is the strongest convergence this project has
produced tonight, and none of the four was chosen to agree with the others.*

## TLDR

You asked me to let brain-fidelity decide the direction. **It does decide, and it points somewhere
other than where we were heading.**

Everything I read and measured tonight kept saying the same thing: this system writes down meanings
and then nothing ever uses them, so nothing can ever correct them. **So I asked what plays that role
in a real brain.**

The answer is well established. As you read, your brain constantly predicts what is coming next, and
when a word does not fit, it produces a measurable jolt — one of the most-replicated signals in
neuroscience. **That jolt is the learning signal, and words that surprise you are remembered
better.** So the brain's consumer of meaning is prediction, and being wrong is how meaning gets
corrected.

**Our own notes already identified this organ, named it, wrote down its mathematics, and marked it
MISSING.** I rediscovered by reading the outside literature something this project had already
written down — the fourth time tonight the answer was sitting in a file nobody had read.

**And here is the verification you asked for: we are not being brain-faithful here, and it is
measurable.** We do have a rough version of the surprise mechanism, but it throws away the *size* of
the surprise and keeps only its direction — so a big shock and a tiny one look identical to it. When
it was tested, it never once fired. That is not a discovery about the brain; it is a consequence of
our shortcut.

**Most interesting: the same shortcut appears in a second place**, in the part that decides what a
word means. Both replace a graded quantity with a crude yes/no. **That may be a single flaw wearing
two costumes**, and it is the sort of thing worth checking before building anything new.

## QUESTIONS

None. This answers Q90 on the criterion you set; I have not opened a new fork.

## NEXT STEPS

1. **F5 is the target, and it is NOT small** -- it needs a running situation model (F6), also
   missing. **Do not let the convergence make it sound cheap.**
2. **G2's null is not evidence about prediction error** -- it is evidence about a sign-quantised
   residual. That should be recorded against the cell so nobody cites it as "surprise gating does
   not work here".
3. **Test the shared-defect hypothesis:** is the graded-vs-signed substitution one bug in two
   organs? Cheap to check, and it would reframe both.
