# PRE-REGISTRATION -- exp_perirhinal_conjunctive_readout_c3_v1

Authored 2026-08-15, BEFORE any arm of this cell was scored. Branch `dataprep/mcguffey-graded-corpus`.

## 0. PRIOR WORK -- WHAT IS ALREADY MEASURED, AND WHY THIS IS NOT A RE-RUN

Enumerated from disk, not recalled.

1. **`exp_structured_code_vs_flat_bag_c3_v1` ALREADY RAN THE OBVIOUS VERSION OF THIS AND IT LOST.**
   Full run, 2026-08-15T16:05Z, `elapsed_s=3505.77`, on this exact harness:
   `A2_STRUCTURED` (dependency-relation ROLE-BOUND code, `sum bind(REL:rel, filler)`) scored
   **0.03675** against `A1_BASE` **0.0480**; delta **-0.0113, CI [-0.0195,-0.0030]**, verdict
   **`STRUCTURE_HURTS`**. Its `frac_gold_in_top50` fell 0.5565 -> 0.4158 and its median rank rose
   37 -> 81. **Any claim that "a bound key was never connected to the read-out" is false.** It was,
   today, at full scale, and it lost.
2. Three ISOLATION wins stand and are not disputed here: factored 1.000 vs flat 0.003; conjunctive
   1.000 vs additive 0.273 at M=256; permutation binding 1.0000 vs FHRR 0.0629. **None ran on real
   text.** Result 1 above is what happened the first time one of them met real text.
3. The runtime premise check for this cell (`scratch/wall2_premises.json`) CONFIRMED that the live
   read-out profile is a bare unkeyed order-invariant sum, and **REFUTED** the claim that the fact
   store's exact index is disabled on the live path (the persisted foundation stores carry
   `use_index: true`, and the two retrieval branches are bit-identical anyway).

**What makes this cell a NEW test and not a rediscovery.** The refuted arm and the banked
isolation win use DIFFERENT operators. `A2_STRUCTURED` binds a RELATION LABEL to a filler and then
SUMS those pairs -- the top-level combination stays additive. The banked conjunctive win uses an
elementwise PRODUCT over the item's features so that overlapping feature sets become near
orthogonal. This cell tests the second operator, which has never been run on real text, and it
tests it in the form the anatomy actually has (feature units AND conjunction units) as well as in
the strict "conjunctions instead of features" form.

## 1. QUESTION

Does a conjunctive context code -- where the alphabet is "content word A AND content word B
occurred together in this context", not "content word A occurred" -- beat the live flat bag on the
identical C3 open-vocabulary known-answer read-out, and does it clear the strongest
no-understanding floor?

## 2. BRAIN-FIDELITY TAGS (stated before the result, so neither outcome can be re-labelled)

- **PINNED-BY-EVIDENCE, as architecture only:** perirhinal cortex is implicated in discriminating
  items that SHARE FEATURES; medial-temporal codes are sparse rather than dense.
- **OUR-INVENTION-BEING-TESTED:** the conjunction OPERATOR. The literature does not pin it.
  Elementwise product over unordered content-word pairs is our choice.
- **CONTESTED, and it must be said in the writeup either way:** the perirhinal feature-ambiguity
  account has real failed replications. **This cell is evidence about this operator on this task.
  It is NOT evidence about brain fidelity, in either direction.**

## 3. THE OPERATOR

For target lemma `L` in a sentence, let `w_1..w_m` be the content-word tokens with every token
whose lemma is `L` removed (the SAME masked list the live encoder uses) and `phi_w` the SAME
hashlib-seeded bipolar symbol vector.

    BAG   S = sum_i phi_i                        (live)
    PAIR  P = sum_{i<j} phi_i * phi_j = (S*S - m)/2   (exact for bipolar phi)

- `A2_CONJ_PAIR`   profile accumulates `P`            -- conjunctions INSTEAD of features
- `A3_CONJ_HYBRID` profile accumulates `S + P`        -- features AND conjunctions
- `A4_CONJ_SPARSE` profile accumulates `kwta(P, 0.10)` -- **TWO variables vs live; DIAGNOSTIC ONLY,
  carries no verdict weight**

**Declared in advance, so it cannot be presented later as a discovery:** at a single occurrence `P`
is a deterministic pointwise function of `S` and so carries no extra information. The claim under
test is that the METRIC (similarity superlinear in shared context) and the ACROSS-OCCURRENCE
accumulation (`sum_occ P(S_occ)` is not a function of `sum_occ S_occ`) change the read-out.

## 4. ARMS -- identical scorer, n, pool, gold, item set for every arm

| arm | what it is |
|---|---|
| `A1_BASE` | the live flat bag, unmodified. HARNESS-INTEGRITY GATE: must reproduce hit@1 0.0480 to 1e-9 |
| `A2_CONJ_PAIR` | conjunctive profile, primary |
| `A3_CONJ_HYBRID` | features + conjunctions, primary |
| `A4_CONJ_SPARSE` | sparsified conjunctions, diagnostic only |
| `A5_STRINGCTRL` | character-trigram-only. ZERO substrate signal. This is the 8.70% floor that beats the live system |
| `A7_PREFIX_ONLY` | longest-common-prefix only. Zero substrate signal |
| `F_FREQUENCY` | most frequent eligible anchor |
| `F_SCRAMBLE_<arm>` | per-arm donor-permuted query against that arm's own field (the NULL arm) |

## 5. FLOOR -- NEVER A BARE NUMBER

An arm WINS only if ALL of the following hold:

1. **CI-separated above `A1_BASE`** on a paired bootstrap over the identical items, **and** the
   delta exceeds `max(projection-draw sd of BASE, projection-draw sd of that arm)`.
2. **CI-separated above `max(A5_STRINGCTRL, A7_PREFIX_ONLY, F_FREQUENCY, its own F_SCRAMBLE)`** --
   the strongest no-understanding floor, on the identical scorer/n/pool/gold.
3. **Its own KNOWN-ANSWER arm passes**: self-retrieval (a held-out sentence of L, scored against
   L's own anchor versus a random other anchor) `>= 0.70` with `n >= 30`.

Gates 1 and 2 test the EFFECT; gate 3 tests the INSTRUMENT. They fail independently and both are
required. Any arm failing gate 3 is reported `VOID_PLUMBING` for that arm and publishes no
quality number.

## 6. PRE-DECLARED PREDICTIONS (so the write-up cannot be retrofitted)

- **P1.** `A2_CONJ_PAIR` sharpens: its `frac_gold_in_top50` will be LOWER than `A1_BASE` (the
  metric is superlinear, so partial matches are demoted) while its `separation_margin_z` will be
  HIGHER.
- **P2.** If `A2_CONJ_PAIR` falls below its own scramble floor, the honest reading is that a FULL
  pairwise conjunction destroys the graded partial overlap this task runs on -- **not** that
  "conjunction is refuted". `A3_CONJ_HYBRID` is the arm that tests conjunction WITHOUT removing
  the graded channel, and it is the one to read for that question.
- **P3.** The single most likely outcome, given prior result 1 in section 0, is that no
  conjunctive arm clears `A1_BASE`. **That is a publishable result and will be reported plainly.
  No tuning pass will be run to rescue it.**

## 7. STOP-IF

- `A1_BASE` fails to reproduce 0.0480 to 1e-9 -> `HARNESS_MISMATCH_STOP`, no conclusion drawn.
- `A1_BASE` self-retrieval below 0.70 -> `VOID_PLUMBING`, the whole comparison is void.
- Any floor arm lands above chance in a way that indicates a leak in item construction -> report
  the construction defect, not the number.
- Two arms produce a bit-identical correctness vector (`arms_must_differ`) -> the arms are not
  distinct and the delta between them is not a measurement.

## 8. WIRING DECLARATION

`hdlab/perirhinal_conjunctive.py` is landed **DEFAULT-OFF**. It reaches the reader only through the
pre-existing `process_sentence(encoder=...)` port; **no file on the live import closure is
edited**. Witness: `verification/verify_perirhinal_conjunctive_default_off.py`, 4/4 gates, which
asserts the live default path is BIT-IDENTICAL with the organ imported. **Turning the default on is
a separate decision after a verdict and is NOT taken by this cell.**

## 9. ROUTING / COST

Local CPU. The conjunctive code is an elementwise quadratic of the bag, so it costs the same as
the live encoder -- no re-parsing, no new corpus pass. Expected wall time comparable to
`exp_structured_code_vs_flat_bag_c3_v1` minus its dependency-parsing (which this cell does not do).
