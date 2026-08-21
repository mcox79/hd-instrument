# **THE PREDICTION-ERROR WRITE GATE WAS ALREADY TESTED AND DISSOCIATED -- A *RANDOM* GATE AT THE SAME RATE TIES IT**

**Tonight I designed a meaning-consumption link whose core was: the banked meaning supplies the
PREDICTION, the gap becomes the error, and that error decides what is worth writing.
`exp_predictive_coding_write_gate_dissociation_v1` (2026-08-18) tested exactly that, with the exact
control that kills it.**

Its verdict string states the finding without needing the numbers:
**`STOP_IF_ii_P1_BEATS_A0_BUT_NOT_N1__GAIN_IS_GATING_RATE_NOT_PREDICTION_ERROR`**

---

## 1. THE ARMS, AND THE ONE THAT MATTERS

| arm | AUC | CI95 |
|---|---|---|
| `A0_INCUMBENT` (no gate) | 0.0710 | [0.0507, 0.0930] |
| `P2_PREDICTION_WEIGHTED` | 0.0728 | [0.0523, 0.0954] |
| **`P1_PREDICTION_GATED`** | **0.0961** | [0.0723, 0.1230] |
| **`N1_RANDOM_GATE`** *(rate-matched)* | **0.0971** | [0.0717, 0.1243] |
| `N2_ANTI_GATE` | 0.5000 | **[0.5, 0.5]** |

**PAIRED, WHICH IS HOW IT SHOULD BE READ:**

| comparison | point diff | CI95 | band |
|---|---|---|---|
| **P1 vs N1 (random, same rate)** | **-0.0010** | **[-0.0204, +0.0181]** | **`NOT_SEPARATED`** |
| P1 vs A0 (incumbent) | +0.0251 | [+0.0087, +0.0418] | `A_ABOVE_B` |

**➡️ THE PREDICTION GATE BEATS DOING NOTHING. IT DOES NOT BEAT GATING AT RANDOM AT THE SAME RATE --
AND THE RANDOM GATE'S POINT ESTIMATE IS *HIGHER*.**

**THE BENEFIT IS FROM WRITING *LESS*, NOT FROM WRITING THE *RIGHT THINGS*.** *That is a dissociation,
not a null: the effect is real, and it belongs to a variable nobody proposed.*

## 2. THE INSTRUMENTATION IS THE BEST I HAVE SEEN IN THIS ARCHIVE

| check | result |
|---|---|
| **regression gate, 11 arms recomputed** | `F_ORTHOGRAPHIC` 0.5, `F_FREQUENCY` 0.4901, `F_SCRAMBLE` 0.4664, `F_CONSTANT_PROTOTYPE` 0.5431, `RANDOM_VECTOR_STORE` 0.4862 -- **every delta exactly 0.0** |
| **known-answer positive control** | `KNOWN_ANSWER_WORDNET_PATH_SIM` **0.9599** -- the instrument CAN detect signal |
| **stream fidelity** | rebuilt store vs LANDED anchor matrix **cos = 1.0** over **5,491 anchors**; AUC delta **-1e-06** |
| **surprise non-degeneracy** | n=33,907, median 0.4497, p90-p10 0.1595 -> **`SURPRISE_DEGENERATE: false`**, *and it names a PRIOR cell where the same signal WAS near-degenerate on a different population* |
| **invariant** | `NO_LLM_IN_OPERATIONAL_FLOW: true` |

**The surprise signal was verified NON-DEGENERATE before the verdict was read** -- i.e. this is not
G2's dead-gate failure repeating. *The gate fired, the signal varied, and the result is still that
randomness matches it.*

## 3. ⚠️ TWO THINGS TO CARRY

**EVERY ARM SITS IN BAND `BELOW_0.5_COOCCURRENCE`.** *The whole family -- incumbent, weighted, gated
and random -- is below the co-occurrence reference. **Counting again**, for the sixth time tonight.*

**`N2_ANTI_GATE` READS EXACTLY 0.5000 WITH A CI HALF-WIDTH OF 0.0.** *A zero-width interval is the
reachability signature this repo already documents. The anti-gate almost certainly wrote nothing or
everything; **it should not be cited as a control that passed.***

## 4. WHAT THIS DOES TO MY ANGLE B DESIGN

**The half that said "a wrong meaning must COST something, and prediction error is that cost" is
REFUTED as a WRITE GATE.** *Gating on error is indistinguishable from gating on a coin flip at the
same rate.*

**What survives:** the *consumption* half -- that a banked meaning should feed the prediction at all
-- **was never the thing tested here.** This cell gated WRITES by error; it did not test whether
supplying meaning IMPROVES the prediction. **Those are different claims and I should not let this
kill both.**

**But the honest weight has shifted hard.** *If error-gating writes buys nothing over a coin flip,
the burden on "error is the useful signal" is now substantially higher.*

## TLDR

Tonight I designed a mechanism whose centrepiece was: **let the system's surprise decide what's worth
remembering.** That was tested three days ago, with exactly the control that settles it.

**Gating on surprise does beat storing everything.** But the experiment also included a version that
**throws away the same proportion of material at random** — and that scores just as well. Very
slightly better, in fact.

**So the benefit comes from writing less, not from writing the right things.** Which is a genuinely
interesting result rather than a flat failure: the improvement is real, it just belongs to a variable
nobody was proposing.

**The experiment is the most carefully built one I've seen here.** It re-derives eleven reference
points and matches every one exactly; it includes a known-answer check that scores 96%, proving it can
detect a real signal; it verifies its rebuilt copy of the system matches the real one perfectly across
5,491 entries; and it explicitly confirms the surprise signal was varied rather than flat before
reading any verdict.

**Two cautions.** Every version tested, including the winner, scores **below plain word-counting** —
the sixth time tonight. And one control reports a suspiciously perfect 0.5 with **zero uncertainty**,
which usually means it did nothing at all; it shouldn't be cited.

**What this means for my proposal:** the part where surprise decides what to store is **refuted**. The
part where stored meaning feeds the prediction in the first place **wasn't tested here** — but the
burden on it just got heavier.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not build an error-gated write path.** *It is dissociated: rate is the active ingredient.*
2. **If write-rate is the real lever, that is testable directly and cheaply** -- sweep the rate with a
   random gate and find where it peaks. *Nobody has to believe anything about prediction error to run
   that.*
3. The consumption half of Angle B is untouched by this and remains open.
