# T5b -- **THE TIE DIAGNOSTIC IS IN. SPELLING'S RANK-1 WIN *SURVIVES* THE STRICTEST CONVENTION — AND THE "IDENTICAL MEDIAN RANK" THAT MADE ME SUSPICIOUS WAS ITSELF THE ARTIFACT: CORRECTED, THE SUBSTRATE WINS THE FULL RANKING 37.0 vs 54.0**

**Ran:** `tools/orthographic_floor_tie_mass_v1.py` (n=4000, 5491 anchors, 621 s), reusing the VET
tool's construction **by import**. **The check neither landed cell performed.**
**Artifact:** `data/exp_orthographic_floor_tie_mass_v1/metrics.json`

---

## 1. THE RESULT

| | **A1_BASE** (meaning read-out) | **A6_TRIGRAM_ONLY** (pure spelling) |
|---|---|---|
| mean candidates tied at max | **1.000** | 1.253 |
| max tied at max | **1** | **11** |
| **items with ANY tie at max** | **0.0%** | **15.6%** |
| items with all scores 0.0 | 0.0% | 0.0% |
| **hit@1 optimistic** | 0.0480 | 0.0988 |
| **hit@1 pessimistic** | **0.0480** | **0.0767** |
| **median rank optimistic** | 37.0 | 37.0 |
| **median rank pessimistic** | **37.0** | **54.0** |

**POSITIVE CONTROL: my `A1_BASE` optimistic hit@1 reproduces the landed VET's `0.048` exactly** --
so this harness is measuring the same thing on the same items, not a different measurement dressed
up as a comparison.

## 2. ✅ **THE HEADLINE SURVIVES. THE SUBSTRATE ARM IS COMPLETELY TIE-FREE, SO IT HAS NO DEFENCE HERE.**

**`A1_BASE` has ties on 0.0% of items -- max tied = 1.** Its `0.0480` is identical under both
conventions. *There is no tie-breaking artifact propping up the meaning read-out, and no version of
the tie argument rescues it.*

**And spelling wins at rank 1 even when EVERY tie is scored against it:**
**`0.0767` pessimistic vs `0.0480`** -- still **1.60x**, and still clear of `A1`'s landed CI upper
bound (**0.05475**).
*The VET's reported `0.087` sits between my optimistic `0.0988` and pessimistic `0.0767`, exactly as
it must: `argmax` breaks ties by array position, which lands between "gold counts if tied" and "gold
must be unique".*

**➡️ T5'S CLAIM STANDS: COMPARING LETTER-SHAPES, WITH NO MEANING, PICKS THE RIGHT WORD AT RANK 1
MORE OFTEN THAN EVERYTHING THIS PROJECT HAS BUILT TO REPRESENT MEANING.**

## 3. 🔄 **BUT THE THING THAT MADE ME SUSPICIOUS WAS ITSELF THE ARTIFACT — AND CORRECTING IT REVERSES THE OTHER HALF**

T5 flagged: *"median rank is IDENTICAL, 37.0 vs 37.0 -- the whole effect lives in the top slot."*
**That identity was manufactured by the strict-inequality rank**, which counts every tie as beaten
and therefore flatters the tie-heavy arm. Scored honestly:

| | A1_BASE | A6_TRIGRAM_ONLY |
|---|---|---|
| median rank, **pessimistic** | **37.0** | **54.0** |

**➡️ OVER THE FULL RANKING THE SUBSTRATE IS *BETTER* THAN SPELLING -- 37.0 vs 54.0 -- AND THE
LANDED CELLS COULD NOT SEE THIS BECAUSE NEITHER COMPUTED IT.**

## 4. 🧠 **THE REAL SHAPE OF THE PROBLEM, AND IT IS NOT "THE SUBSTRATE KNOWS LESS"**

| | rank 1 | whole ranking |
|---|---|---|
| **spelling** | **better** (0.0767 vs 0.0480) | worse (54.0) |
| **substrate** | worse | **better** (37.0) |

**The substrate carries BROAD, DIFFUSE knowledge and CANNOT SHARPEN TO A WINNER. Spelling is
NARROW BUT SHARP** -- it nails the top slot when a real morphological relative exists and ranks
badly everywhere else.

**➡️ THE DEFECT IS PRECISION AT THE TOP, NOT COVERAGE.** *That is a different build target from the
one "spelling beats meaning" implies on its own -- and it points straight at **T3**: the live
grounding path throws away the query's magnitudes (`np.sign` at `:776`) **at exactly the comparison
step where sharpening would have to happen**, pairing a graded field with a binary query in the
configuration the repo's own docstring calls "worse than either". **B4's fidelity label is
WRONG-OP, binary where the brain is graded**, and this is what that costs, measured.*
*Stated as a hypothesis, not a result: **the magnitude discarded at `:776` is precisely the
information that would separate a top-1 from a near-miss.** It is now a testable prediction rather
than an aesthetic preference.*

## 5. WHAT THIS DOES NOT SETTLE

- **Whether wiring the graded query fixes the top-1 gap.** *Unmeasured. T3's `+0.0602` is a
  different scorer and population.*
- **Whether spelling's rank-1 wins are "real" senses.** *A morphological relative can be the right
  answer for the wrong reason; the gold set decides, and it scored them as hits.*
- **`A8_MAXORTHO` remains mislabelled** -- `_z(trig) + _z(pre)` is a SUM, `0.061`, below its own
  component. **The strongest zero-meaning floor actually run is `A6`.** *Under the pessimistic
  convention that floor is `0.0767`; under argmax `0.087`.*

## TLDR

I said earlier that comparing words by their letter patterns beats our meaning system, then flagged
one reason to doubt it: the whole difference sat in "was the first guess right," and nobody had
counted how often scores were exactly tied. **I ran that count. It took ten minutes and it settles
the question — both ways.**

**The headline holds.** Our meaning system turns out to have **no ties at all** — zero percent — so
there is no bookkeeping excuse available to it. And even when every single tie is scored *against*
spelling, spelling still wins the top slot **7.7% to 4.8%.**

**But the thing that made me suspicious turned out to be the actual error, and fixing it flips the
other half of the picture.** I'd noticed both methods had an identical average position — 37th. That
identity was fake: it came from a scoring convention that quietly credits ties as wins, which
flatters the tie-heavy method. Counted honestly, our meaning system averages **37th and spelling
averages 54th.**

**So the real picture is sharper than "spelling beats meaning."** Our system knows *more* — it
consistently puts the right answer higher up the list. **What it cannot do is close the deal and put
it first.** Spelling is the opposite: usually poor, but when a word looks like its answer, it nails
it outright.

**That changes what needs fixing.** Not "the system knows too little" — **"the system cannot sharpen
to a winner."** And that lands exactly on the flaw I found earlier tonight: at the moment of
comparison, the code throws away the strength information in the question and flattens it to plain
yes/no. **That is the step where sharpening would have to happen.** It is now a testable prediction
rather than a preference.

## QUESTIONS

None.

## NEXT STEPS

1. **This makes T3 a testable prediction:** if the discarded magnitudes are what separate a top-1
   from a near-miss, restoring them should move **hit@1** specifically, and leave median rank
   roughly alone. **That is a sharp, falsifiable shape.**
2. **Report both conventions in any future cell touching this floor.** Two landed cells missed a
   17-rank difference by omitting one line.
3. **Quote the floor as `A6`, not `A8`** -- and say which convention.
