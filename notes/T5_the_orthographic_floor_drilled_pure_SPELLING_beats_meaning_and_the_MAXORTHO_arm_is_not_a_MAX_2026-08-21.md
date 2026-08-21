# T5 -- **PURE SPELLING BEATS THE SUBSTRATE'S MEANING READ-OUT, CI-SEPARATED. AND THE ARM BUILT TO BE "THE STRONGEST ZERO-MEANING ATTACK" IS NOT THE STRONGEST — IT IS 30% WEAKER THAN ITS OWN COMPONENT.**

**Owner, dash 02:54Z:** *"your plan to expand to other sections of the substrate overnight as needed.
Don't wander, but be diligent and with purpose."* **This is the expansion.** T3 ended by naming this
as *"the wall"*; drilling it took no new run.

---

## 0. 🔴 FIRST, CORRECTING MYSELF: I NAMED THE WRONG ARM AN HOUR AGO

T3 said *"a string-matching control beats the semantic path ~1.8x."* **The arm I cited does not
support that sentence.** `tools/orthographic_floor_vet_v1.py` exists specifically because of this
misreading, and says so in its own docstring:

> *"`A5_STRINGCTRL` is `z(base) + w*z(trigram)` -- **the substrate read-out PLUS an orthographic
> channel, NOT orthography alone.** So 0.1027 cannot be read as 'a spell-checker scores 0.1027'."*

**A tool was promoted out of `scratch/` to prevent exactly the claim I made.**

## 1. ✅ **BUT THE CLAIM IS TRUE WITH THE RIGHT ARM, AND THE REPO HAD ALREADY MEASURED IT**

`A6_TRIGRAM_ONLY` is **character-trigram cosine alone, zero substrate signal**, on IDENTICAL items,
pool, gold and scorer, with `a1_base_reproduces_c3_headline_exactly: true` (n=4000, 5491 anchors):

| arm | hit@1 | 95% CI | median rank |
|---|---|---|---|
| **A1_BASE** — the substrate's meaning read-out | **0.048** | [0.04125, **0.05475**] | **37.0** |
| **A6_TRIGRAM_ONLY** — spelling, no meaning at all | **0.087** | [**0.07825**, 0.09600] | **37.0** |
| A7_PREFIX_ONLY | 0.05875 | [0.05150, 0.06600] | 33.5 |
| A8_MAXORTHO | 0.061 | [0.05374, 0.06850] | 43.0 |

**➡️ THE CIs DO NOT OVERLAP: spelling's LOWER bound (0.078) sits above meaning's UPPER bound
(0.055).** *Comparing letter-shapes, with no semantics whatsoever, picks the right word at rank 1
almost twice as often as everything this project has built to represent meaning.*

## 2. 🚨 **THE FLOOR LABELLED "MAX" IS NOT A MAX -- AND ANY VERDICT THAT USED IT USED A FLOOR 30% TOO WEAK**

The docstring: *"A8_MAXORTHO (**max-attack blend of both, since a FLOOR should be the strongest
available zero-meaning attack**)"*. The code, `tools/orthographic_floor_vet_v1.py:129`:

```python
"A8_MAXORTHO": MS._z(trig) + MS._z(pre)
```

**That is a z-score SUM, not a max** -- and empirically it is **weaker than its own best component**:
**A8 = 0.061 vs A6 = 0.087.** Blending the strong channel with the weak one **dilutes** it.

**➡️ THE STRONGEST ZERO-MEANING FLOOR ACTUALLY RUN IS `A6 = 0.087`, UPPER BOUND `0.096` -- NOT
`A8 = 0.061`.** *The standing measurement bar says gate on `max(floors actually run)` **and on its
UPPER bound**. Anything that treated `A8` as "the strongest orthographic attack" because of its name
and its stated rationale gated against a floor **30% too low**.*

## 3. ⚠️ **THE ONE CHECK THAT COULD OVERTURN THIS WAS NEVER RUN — IN EITHER CELL**

**The entire advantage lives at rank 1. Median rank is IDENTICAL: 37.0 vs 37.0.** Two completely
different similarity functions, 4000 items, the same median to the decimal. **Over the full ranking
the two are indistinguishable; only the top slot separates them.**

**And no tie diagnostic exists in either artifact.** Verified by searching both `metrics.json` files
for `tie` / `n_tied` / `pessimist`: **absent from both.**

| | tie mass | n_tied | pessimistic rank |
|---|---|---|---|
| `exp_orthographic_floor_vet_v1` | ❌ | ❌ | ❌ |
| `exp_graded_path_vs_orthographic_floor_v1` | ❌ | ❌ | ❌ |

**`CLAUDE.md` mandates it in two separate sections** -- *"assert TIE DENSITY, report both tie
conventions"* and *"report both tie conventions whenever ties are possible"* -- both written after
tie degeneracy produced three false results in one day. **A statistic that lives entirely in the top
slot is the most tie-sensitive statistic there is, and it is the only one carrying this finding.**

**HONEST WEIGHING, BOTH WAYS.** *Against* an artifact: the CIs are separated, and a trigram cosine
over real words is fairly continuous, so exact ties at the TOP should be rarer than at the bottom.
*For* an artifact: the identical medians say the ranking as a whole does not distinguish the arms,
and nobody counted. **I cannot settle it from the artifacts and I am not going to pretend otherwise
-- it needs the diagnostic, which is cheap.**

## 4. 🧠 BRAIN FIDELITY (Q95) AND WHAT THIS MEANS IF IT SURVIVES

`ORGAN_MAP` labels B4 **WRONG-OP: binary where the brain is graded**, over a 256-dim context space
holding 2,377 concepts. **A spelling channel outscoring the meaning channel is the standing
diagnostic tell verbatim -- *"similarity-proxy where the brain reasons = ARCHITECTURE FIX"*, not a
tuning problem.**
*It also reframes T3: making the query graded is a refinement to a read-out that is currently losing
to letter-shape comparison. **Worth doing, but it is not the wall.***

## TLDR

The owner said to expand into other parts of the system, with purpose. The purposeful target was the
thing I flagged an hour ago as the real problem — and drilling it needed no new run, just reading
results we already had.

**First I had to correct myself.** I'd written that "a spelling-matching trick beats the real
system," citing a comparison that was actually *the system plus spelling*, not spelling alone. There
is a tool in this repo that exists purely to stop people making that exact claim.

**But the repo had already measured the honest version, and the claim survives.** Comparing words
purely by their letter patterns — no meaning involved at any point — picks the right answer **8.7% of
the time against the meaning system's 4.8%**, on identical questions, with the uncertainty ranges not
overlapping. **Letter-shapes beat meaning, nearly two to one.**

**Then a genuine defect in the test itself.** One comparison arm is named "MAXORTHO" and justified as
*"the strongest possible no-meaning attack"* — the toughest bar the system must clear. It is not the
strongest. It averages a strong signal with a weak one and comes out **30% below the strong one
alone**. Anything judged against it was judged against a bar set too low.

**And the check that could overturn all of this was never run.** The whole difference sits in "was
the very first guess right?" — and by every other measure the two are *identical* (median position
37th for both). When results hinge on a single top slot, you must count how often scores are exactly
tied, because ties get resolved by list order rather than by knowledge. **Our own rules demand that
count in two separate places. Neither experiment computed it.** I can argue it both ways and I won't
pretend to settle it.

**If it holds, it is an architecture problem, not a tuning one** — and it means the graded-query fix
I found earlier is a polish on a read-out currently losing to a spell-checker.

## QUESTIONS

None.

## NEXT STEPS

1. **Compute tie mass and both tie conventions for `A1_BASE` and `A6_TRIGRAM_ONLY`.** Cheap, and it
   is the only thing standing between this and a solid finding. **Until then this is a strong
   hypothesis, not a verdict.**
2. **Stop quoting `A8_MAXORTHO` as the strongest orthographic floor.** The strongest run is
   **`A6 = 0.087`, gate on its upper bound `0.096`.** Its name and docstring should be corrected --
   `_z(trig) + _z(pre)` is a sum.
3. **If it survives: this outranks T3.** A read-out beaten by letter-shape comparison is an
   architecture finding; a signed-vs-graded query is a refinement to that same read-out.
