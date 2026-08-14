# LANDED-VET: the graded-comparator NUMBER survives; its MECHANISM CLAIM does not

Filed 2026-08-14, hours after `exp_graded_divisive_comparator_v1` was landed (`0f6459309`) and
wired into `hdlab/` (`542fb7754`). Produced by an adversarial review dispatched with the brief
"try to break this result, a finding that it is an artifact is more valuable than a confirmation."
Probes promoted out of `scratch/` to `experiments/adversarial_review_graded_comparator/`.

**This note SUPERSEDES the mechanism claim in
`notes/comparator_component_fidelity_audit_2026-08-13.md` row C1 and in the commit message of
`0f6459309`. The measured numbers are unchanged and confirmed; the explanation of them is not.**

---

## WHAT SURVIVED (independently re-derived, not taken on trust)

The reviewer rebuilt the pipeline from the cached corpus assets and re-scored every arm with its
own scoring loop:

- all 19 arms at n=600 reproduce with **zero mismatches**;
- at full scale `A_SSN 0.6395`, `A_GGZ 0.69975`, `d 0.06025` — **bit-exact** to the landed run.

Five artifact hypotheses were tested and **killed**:

1. **Leakage — none.** `_graded` is `_signed` minus its last two lines and both call `_kept_words`
   with the identical drop set, so the masks are identical by construction. 0/600 eval sentences
   appear in either candidate's profile pool. Word-identity channel is at chance (0.477 graded /
   0.462 sign). Sentence LENGTH is encoded in the graded magnitudes, but corr(length, correct) =
   -0.009 and the delta holds in both halves (short +0.067, long +0.088). Every anchor word has
   exactly 70 profile sentences, so there is no count asymmetry; "pick the larger anchor norm"
   scores 0.495.
2. **Normalisation statistics — not a channel.** Recomputing the pool from 600 DISJOINT
   non-candidate words moves the delta 0.0767 -> 0.0717 (<= 0.005).
3. **Tie-breaking — dead, and it points the other way.** LIVE has 9 ties at n=4000, PRIMARY 0; max
   possible shift 0.0033, and scoring ties as losses makes the delta LARGER.
4. **Floor validity — noise, not anti-correlation.** 20 random donor derangements give
   0.5083 +/- 0.020; the below-chance smoke floor is ~2.8 SE of donor noise.
5. **Zero rows / degenerate anchors — none in any arm.**

## WHAT DID NOT SURVIVE — four findings, in order of severity

### 1. THE DIMENSION CONFOUND. The unmodified `sign()` comparator at d=1024 BEATS the graded one at d=256.

    sign comparator @ d=1024  = 0.7030     >     graded comparator @ d=256 = 0.69975
    d(graded - sign):  0.0602 (d=256)  ->  0.047 (d=1024)  ->  0.041 (d=4096)

The graded code still wins at every dimensionality tested, but the advantage **shrinks with d and
falls below the pre-registered +0.05 band at d >= 1024**. The audit ranked C7 (representation
format / dimensionality) BELOW C1/C2 and explicitly declined to vary d in the same cell to avoid
confounding. That was the right call for isolation and the wrong call for interpretation: without
the d-sweep, a capacity effect reads as a quantisation effect.

### 2. THE TERM-SPACE ABLATION REFUTES THE STATED MECHANISM.

Scored in the UNPROJECTED term space, where "magnitude" means the actual co-occurrence counts:

    count cosine                                    0.8055
    presence-only cosine (ALL magnitude destroyed)  0.7890
    cost of destroying all magnitude                0.0165  = 27% of the measured 0.0602

And query-side magnitude is worth **exactly 0.000**, while removing the ENC-step `sign()` alone is
worth +0.0268 — so that gain **cannot** be magnitude preservation on the query side. The remaining
~73% is random-projection / quantisation INTERFERENCE at CTX_D=256, not the loss of graded evidence.

**The honest statement is "at CTX_D=256 the binary comparator is capacity-limited", not "sign() is
the bottleneck."**

### 3. AN UNCONTROLLED CONFOUND WORTH ~30% OF THE SMOKE DELTA: the two zero conventions.

`context_vector` maps sign-zero to +1 (bipolar); `ConceptSpace.anchor_matrix` leaves it 0
(ternary). 13.2% of sign-query dimensions are exactly zero and all receive the same +1 — a constant
component in every query. Making the convention consistent lifts LIVE 0.6567 -> **0.6800** at
n=600, cutting the smoke delta 0.0767 -> 0.0533. The cell DOCUMENTED this mismatch (its own
byte-identity control discovered it) and then failed to CONTROL for it. Documenting a confound is
not controlling for it.

### 4. PROJECTION-DRAW VARIANCE IS INVISIBLE TO THE ITEM BOOTSTRAP.

10 independent draws of the random-indexing word code at d=256/n=600: delta mean 0.065, **sd
0.015**, range 0.043-0.090 (the cell's draw ranks 3rd of 10). This component is shared across items,
so it does NOT shrink with n the way the item CI does. The reported CI [+0.0440,+0.0762] is a valid
ITEM-level interval for THIS projection draw and is too narrow for a claim about the mechanism in
general. Note also that the CI's lower bound 0.0440 sits BELOW the +0.05 band: the band is cleared
by the point estimate, as pre-registered, but not with confidence.

Minor, recorded: the n=150 smoke would have returned `HARD_FAIL_BINARISATION_NOT_THE_LEVER` by the
cell's own rule (CI [0.0000,0.1600]); the multi-scale smoke gate checks instrumentation but never
the verdict, so it still printed "SMOKE=PASS (all scales)". Underpowered rather than contradictory,
but "smoke HARD_PASS" was an incomplete citation and is corrected here.

---

## REVISED CLAIM, deflated to what the evidence supports

**LICENSED:** on a held-out near-neighbour 2AFC in context at n=4000, replacing the substrate's
fully quantised comparator with a graded one raises accuracy 0.6395 -> 0.6997 at the substrate's
live d=256, with the scrambled-context floor at chance; the effect is not leakage, ties, length,
pool statistics or a broken floor; it reproduces bit-exactly; and the graded code is better than
the quantised one at every dimensionality tested.

**NOT LICENSED:** that per-component magnitude destruction is THE binding constraint on
near-neighbour discrimination. Three independent measurements contradict that reading (the d-sweep,
the term-space ablation, the zero-convention confound), and a fourth (projection-draw variance)
says the interval was too narrow to carry a mechanism claim at all.

**BEST CURRENT READING:** quantisation and random-projection crosstalk are the same limitation seen
from two sides, and at d=256 the substrate is operating where they bind. Graded coding relieves it;
so does more dimensions; neither is "the" mechanism. The audit's C7 row (representation format /
capacity), which I ranked LAST, is promoted to the head of the queue by this evidence.

## WHAT THIS CHANGES ON DISK

1. `hdlab/grounding_acquisition_loop.py` and `hdlab/reading_grounding_loop.py` docstrings: the
   measured payoff stays; the mechanism sentence is corrected and points here.
2. `data/capability_registry.jsonl` row `graded_divisive_comparator_path`: `gate_decision_target`
   corrected, and the d-confound recorded as a live caveat.
3. `notes/comparator_component_fidelity_audit_2026-08-13.md`: superseded-by line added to row C1.
4. **The landing itself STANDS.** The change is additive and default-off, the number is real and
   reproduces, and the graded path wins at every d. What is withdrawn is the explanation, not the
   capability.

## METHOD NOTE — this is the audit method working, not failing

The component-by-component method produced three corrections to its own author within one session:
(a) the log-IDF mechanism I predicted was refuted by numerical recompute; (b) I transposed
Carandini-Heeger and re-designated a primary arm by amendment before scoring; (c) this review. Each
came from a control or a recompute that was ASKED to break the claim. The failure mode the method
is guarding against is a fidelity story that explains a number without being the cause of it, and
that is exactly what happened here — the prototype-operator argument is mathematically correct, it
predicts the right direction, and it is still not the dominant cause of the measured effect.
