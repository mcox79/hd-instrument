# T3 -- **THE LIVE GROUNDING PATH READS A *GRADED* FIELD WITH A *SIGN-QUANTISED* QUERY -- THE ONE CONFIGURATION THE REPO'S OWN DOCSTRING CALLS "WORSE THAN EITHER"**

**All of this is verified at HEAD by reading the source, not from a note.** No run.

---

## 0. 🔴 MY T3 PREMISE WAS WRONG. THE SWITCHES ARE ALREADY ON.

I wrote: *"Three switches are **already built and already default-OFF**. Turn them on."*

| line | reality at HEAD |
|---|---|
| `reading_grounding_loop.py:103` | `GRADED_COMPARATOR = os.environ.get("HD_GRADED_COMPARATOR", **"1"**)` -- **DEFAULT ON** |
| `:683` | `graded_query: bool = field(default_factory=lambda: GRADED_COMPARATOR)` -- **FOLLOWS IT, SO ON** |

And `data/exp_graded_path_vs_orthographic_floor_v1/metrics.json` carries a field literally named
`premise_correction`: *"GRADED_COMPARATOR is default-ON as of 38f7a0d5c, **NOT default-OFF as the
dispatch brief assumed**."* **A previous dispatch made my exact mistake and the cell recorded it.**
*Third plan item superseded tonight, all three by reading rather than by running.*

## 1. ✅ **BUT THERE IS A REAL DEFECT UNDERNEATH, AND IT IS SHARPER THAN THE THING I PLANNED**

**Two read-out functions. Only one of them can do a graded query.**

| | query handling |
|---|---|
| **`canonicalize_fast`** (`:821-825`) | `graded_q = GRADED_COMPARATOR if readout is None else readout.graded_query` -> **honours the switch** |
| **`canonicalize`** (`def :752`) | **`:776  new_bundle = np.sign(new_raw_sum)`** -- **UNCONDITIONAL. No branch, no switch, no config.** |

**AND THE GROUNDING DECISIONS GO THROUGH THE ONE THAT CANNOT:**

- `:1330` `canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=thresh, ...)`
- `:1593` `canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=SENSE_MATCH_THRESH)`
- `hdlab/definitional_extraction.py:19`: ***"The reading-grounding loop's only grounding signal is
  `canonicalize()`."***

**➡️ SO: THE ANCHOR FIELD IS GRADED (switch ON, `:520` returns `s.copy()`), AND THE QUERY IT IS
COMPARED AGAINST IS SIGN-QUANTISED TO ±1.**

## 2. 🚨 **THE REPO ALREADY KNOWS THIS IS THE WORST CASE. IT SAYS SO, IN THE SAME FILE.**

`reading_grounding_loop.py:663-664`, verbatim:

> *"Pair it with `ConceptSpace.freeze_graded()` -- **a graded field read by a signed query is worse
> than either**, because the query's magnitudes are exactly what the field's magnitudes are being
> compared to."*

And `:678-681` guards `ReadoutConfig` against precisely this:

> *"DEFAULT CHANGED 2026-08-14: follows the module switch ... so a bare `ReadoutConfig()` **does not
> silently pair a SIGNED query with a GRADED anchor field -- which is worse than either pure
> convention.**"*

**The guard was put on `ReadoutConfig`. `canonicalize` does not take a `ReadoutConfig`.** *The
protection exists, is deliberate, is documented -- and the only grounding signal in the loop sits
outside it.*

## 3. THE MEASURED SIZE OF WHAT IS UNREACHED (`:668-670`, verbatim)

> *"MEASURED (prereg d6c56353c, n=4000): graded query + graded field = **0.6997** vs **0.6395** for
> the fully quantised live path, **delta +0.0602 CI [+0.0440, +0.0762]**, with the scrambled-context
> floor still at chance (0.5065)."*

**A CI-separated effect, floored, already measured -- and structurally unavailable to the two calls
that decide what gets grounded.** *This is WIRE-DON'T-ISLAND with a specific line number.*

## 4. ⚠️ WHAT I AM **NOT** CLAIMING -- THREE BRAKES, ALL LOAD-BEARING

1. **THE +0.0602 DOES NOT TRANSFER BY ASSERTION.** It is a near-neighbour task at n=4000 under its
   own prereg. **The grounding call sites are a different scorer on a different population, and no
   number crosses scorers or populations.** Wiring may deliver nothing there.
2. **A LANDED CELL IS A LIVE CAUTION AGAINST EXPECTING A WIN.**
   `exp_graded_path_vs_orthographic_floor_v1`: graded ON vs OFF **delta 0.0015, CI [-0.0055,
   +0.0083]** -- a null -- and **both arms lost to the string control** (`A5_STRINGCTRL` hit@1
   **0.087** vs `A1_GRADED_ON` **0.048**). *Verdict: `DOES_NOT_CLEAR_ORTHOGRAPHIC_FLOOR`.*
   **A string-matching control beating the semantic path ~1.8x is the bigger problem, and graded-vs-
   signed does not touch it.**
3. **I HAVE NOT MEASURED THE FIX.** *This note reports a code fact and a documented prediction. It
   reports no result.*

## 5. 🧠 BRAIN FIDELITY, STATED PER Q95

**EQUATION PARITY, and the defect is a departure from it.** B4's pinned math: *"dense, graded, LOW
effective dimensionality ... **Explicitly NOT sparse, NOT binary**"* (Huth 2012; Binder 2016;
Tiesinga 2023; IT sparseness ~0.2-0.3). `ORGAN_MAP`'s own B4 fidelity label is **WRONG-OP (binary
where the brain is graded)**.
**`:776` is that label, as one line of code, on the only grounding signal the loop has.**
*Sparse ~0.2% binary coding is the MTL regime (Waydo 2006) -- **a different system**; the map flags
conflating them as a trap.*

## TLDR

Tonight's third item was "switch on the better word codes — three switches are built but turned
off." **They are already on.** The results file of an earlier experiment even contains a field
called "premise correction" recording that a previous attempt made the identical mistake.

**But reading the code turned up something sharper.** The system stores each word's meaning as a
rich pattern with strengths — some parts strongly on, some weakly. When it then asks *"which known
word does this new one match?"*, one of the two matching routines **throws away all the strengths in
the question**, flattening it to plain yes/no before comparing it against the detailed stored
patterns.

**And that flattening routine is the only one the grounding decisions use.**

The project already knows this is the worst of both worlds — there is a comment in the same file
saying so in as many words, and a guard was added to prevent it. **The guard was attached to the
other routine.**

Measured elsewhere, keeping the strengths is worth about six points (70% vs 64%) with a solid margin.
**Three honest brakes:** that was a different test, so it may not transfer; a landed experiment found
this whole family of changes made no difference on its task, where a crude spelling-similarity trick
beat the real system nearly two to one; and **I have not measured the fix — this reports a fact about
the code, not a result.**

Why it matters beyond the number: the brain's word codes are graded, **explicitly not binary** — the
organ map already labels this exact defect "wrong operation, binary where the brain is graded." Here
it is as a single line.

## QUESTIONS

None.

## NEXT STEPS

1. **Measure it before changing it:** run both read-outs over the same anchors and queries and
   compare grounding decisions. A parity harness already exists at `:1913-1919`.
2. **If it holds, the change is small** -- give `canonicalize` the same `graded_q` branch
   `canonicalize_fast` already has, or route `:1330`/`:1593` to the fast variant.
3. **Do not let it eclipse the bigger finding:** a string control beats the semantic path ~1.8x on
   the one task where both were floored. *That is the wall; this is a line of code.*
