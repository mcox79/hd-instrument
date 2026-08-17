# THE READ-OUT CEILING -- why 0.0481 with a PERFECT cue, and what replaces the read-out

**Live file. Updated after EVERY arm.** Started 2026-08-17 at HEAD `258dd96dd`, branch
`dataprep/mcguffey-graded-corpus`. Written by the cell-author agent working alone (NO subagent
spawned, per brief). NO LLM anywhere in any path.

**THE RESULT THAT CREATED THIS DISPATCH.** `data/exp_cue_regime_one_variable_retrieval_v1/metrics.json`,
verdict `EXACTKEY_READOUT_BELOW_FLOOR__CUE_CARRIES_IDENTITY_YES__LAMBDA_STAR_0p05`: hand the system
the item's OWN stored row (addressing 1.0000, n=3,994 items over 5,491 anchors) and hit@1 against
WordNet gold is **0.0481**, CI-separated BELOW the constant floor **0.1390** by 7.3x its own CI
half-width, and below the spelling floor 0.0873. **The ceiling is INDEPENDENT OF THE CUE.**

---

## 0. DISCLOSURE (updated live)

- **No tool call has been denied at any point in this run.** If that changes, the exact denial text
  is pasted here verbatim and the run STOPS at that step.
- No deletion token issued, alone or bundled. No `git add -A`. No origin push. No subagent spawned.
- `data/foundation/**` never opened. Every protected path in the brief was READ-ONLY or untouched.
- `tools/floor_battery.py`, `tools/verdict_bar_check.py`, `experiments/exp_task_degeneracy_v1.py`,
  `experiments/exp_cue_to_store_translation_v1.py`, `experiments/dehub_transforms.py` are IMPORTED
  and NEVER EDITED.
- `experiments/exp_cue_regime_*` (sibling, LIVE) was READ for the population construction and never
  written to or imported.

---

## 1. PRIOR-WORK CHECK -- **ENUMERATED FROM DISK, NOT SEARCHED**, and it lands hard

`bash tools/substrate_query.sh` is not usable: the sibling agent recorded it failing to return
within 120 s, consistent with the documented `hd_director_kb_continuous_ingest` livelock, and the
08-16 theory drill measured the KB's own retrieval channel to be a CHAR-TRIGRAM SPELLING channel
that returns bare nodes for a concept query. **Enumeration is the stronger instrument here and is
the standing rule** ("an absence claim requires an enumeration, not a search").

Method: `ls experiments/` (**5,911 files**) filtered on readout / rerank / hub / csls / normal /
argmax / rank; `rg -il` over `notes/` and `hdlab/` for the same vocabulary.

**THIS IS NOT A GREENFIELD. Two of the four replacement families I intended to test have ALREADY
BEEN RUN IN THIS REPO AND FAILED**, and they are credited, not re-derived:

| prior work | what it did | landed verdict | why it does not settle this |
|---|---|---|---|
| `experiments/dehub_transforms.py` | **an OWNED, self-tested de-hubbing organ**: `nk_occurrence`, `nk_gini`, LOCAL_SCALING (Zelnik-Manor & Perona 2004), ZCA_WHITEN (Su 2021), ABTT (Mu & Viswanath 2018) | self-tests PASS | it is an `experiments/`-level module, **NOT in `hdlab/` and NOT registry-WIRED**; never applied to THIS read-out |
| `exp_rank1_common_mode_removal_v1` | ABTT D=1 / common-mode removal on the d=256 context space, n=4000 | **HARD_FAIL_NO_EFFECT** d=+0.0005 CI [-0.0043,+0.0053] | scored on the **2AFC** instrument (P0=0.6980), not open-pool hit@1 |
| `exp_task_local_normalisation_pool_v1` | task-local normalisation pool / shared-dimension suppression | **HARD_FAIL_GAIN_HURTS** -0.0220 CI [-0.0340,-0.0097], CI-separated NEGATIVE | same 2AFC instrument; "suppressing shared dimensions destroys signal the comparator needs" |
| `exp_substrate_csls_cleanup_recovery_gpu_v1` | CSLS re-rank for cleanup recovery | **HARD_FAIL**, lift 0.0 | corpus=241, codebook-collision task; its own verdict says the deficit was near-duplicates, NOT hubness |
| `exp_schema_relation_hubness_debias_rescore_v1` | post-hoc hubness de-bias rescore | `dehub_transforms` docstring records it as "already run, shown partially phantom" | different space, different task |
| `exp_readout_fix_v1` | FIX1 informativeness gate / FIX2 frequency-backbone correction (the `ReadoutConfig` path in `hdlab`) | **MIDDLE_BAND**, gated-flip BASE 0.5018 -> F1F2 0.3685 (a DROP) | the fixes exist in `hdlab/reading_grounding_loop.ReadoutConfig` and are OFF by default |

**HONEST CONSEQUENCE, WRITTEN BEFORE THE RUN: my prior on the comparator-replacement arm is LOW.**
Two adjacent instruments already say normalisation-family transforms do nothing or hurt here. That
is a reason to run the DIAGNOSIS first and to deflate the replacement arm, not a reason to skip it
-- every one of those was scored on a **2-candidate forced choice**, where a per-anchor calibration
has almost nothing to do (a component shared by both candidates nearly cancels in a 2-way argmax,
as `freeze_graded`'s own docstring records). The open 5,491-way pool is precisely the regime where
a per-anchor calibration COULD matter and where hubness is defined.

**WHAT IS GENUINELY NEW:** nobody has ever measured **WHERE THE GOLD RANKS** under a perfect cue on
this instrument. Every prior number is hit@1 -- a single point of a distribution. The rank curve is
the measurement that separates "the store does not contain the answer" from "the store contains it
and the selector cannot reach it", and those two have OPPOSITE programme consequences.

---

## 2. PRE-REGISTRATION (written BEFORE any number was read)

### 2.1 The question, decomposed into STAGES so the answer can be a STAGE and not "it is bad"

With addressing pinned at 1.0000, the path from a correct address to a correct answer is:

```
  S1  IS THE ANSWER IN THE POOL AT ALL?        does >=1 WordNet-gold anchor survive eligibility?
  S2  WHERE DOES IT RANK?                      rank of the BEST gold under the exact-key cosine
  S3  WHAT WINS INSTEAD, AND WHY?              identity/degeneracy/genericity/frequency of the top-1
  S4  IS THE SCORE MISCALIBRATED ACROSS ANCHORS? per-anchor hubness statistics
```

**S2 IS THE DECISIVE ONE AND IT IS CHEAP.** It is the brief's "read the content at a perfectly
addressed location and ask whether the answer is present in it at all".

### 2.2 THE PRE-REGISTERED READING OF S2, fixed before the number exists

Let `n_elig` be the item's eligible pool and `n_gold` its number of eligible gold anchors. Under a
ranking that ignores the query, `P(hit@k) = 1 - C(n_elig - n_gold, k) / C(n_elig, k)`, computed
PER ITEM from that item's own `n_elig` and `n_gold` and averaged. That is the RANDOM-RANKING curve.

- **(A) The exact-key rank curve is AT OR BELOW the random-ranking curve** -> the store's
  neighbourhood carries **no synonym information at all**. **THE DEFECT IS IN WHAT WE WROTE, NOT IN
  HOW WE READ.** No comparator, verifier, shortlist or cleanup can help. **The programme redirects
  from READING to WRITING.** This is the loudest available outcome and the brief asks for it to be
  said loudly.
- **(B) The curve is CI-separated ABOVE random but hit@1 is below the constant floor** -> the
  information IS in the store and the SELECTOR cannot reach it. A two-stage propose-and-verify with
  a shortlist of size k has a computable ceiling: exactly the hit@k of stage one. **The defect is
  in the read-out and the fix is architectural.**
- **(C) The curve is above random AND hit@1 clears the binding floor** -> the landed 0.0481 is an
  artefact of this population and the whole dispatch is re-scoped. (Ruled out in advance by the
  regression gate, but it is a real branch and it is listed so no branch is chosen after the fact.)

### 2.3 THE BAR, and every floor recomputed here

Every arm is judged on a **CI-SEPARATED margin over
`max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE)`**, all four recomputed on THIS
population, on the IDENTICAL scorer / n / pool / gold, with the paired bootstrap over the common
scored items. **`0.1382`, `0.2070` and `-0.1959` are NEVER imported.** The constant/prototype floor
is published under **all three tie conventions**. `ORACLE_CONSTANT` is reported and is **NOT a
floor**. The pool is the **LANDED OPEN pool**; `eligB` is not used (on record admitting a constant
at 0.1715 against chance 0.0101), and the open pool's own oracle-constant value is published so
nobody reads a margin over it as a margin over chance.

### 2.4 Validity arms -- must pass, and must fail INDEPENDENTLY

- `KA_SELF_ADDRESS`: query = the item's own stored row, gold = the item's OWN anchor, own anchor
  ELIGIBLE. Must be >= 0.95. **Sensitive to the scorer/pool/comparator; INSENSITIVE to the WordNet
  gold pairing.**
- `NULL_PERMUTED`: identical pipeline, cue-to-item assignment deranged, WordNet gold. Must sit at
  this pool's own chance. **Sensitive to the pairing; INSENSITIVE to whether the scorer is right.**
- A comparator bug drops KA while leaving NULL at chance; a pairing/leak bug leaves KA at ceiling
  while lifting NULL. **Neither single bug can make both pass.**
- `REGRESSION`: reproduce the landed **0.0223** (partial cue) and **0.0481** (exact key) on the full
  landed open pool, tol 5e-4. If it fails, this is not the landed instrument and nothing is read.

### 2.5 Reporting rules this run is bound by

- **Every margin is published beside its CI half-width AND the analytic null width
  `1.96*sqrt(p(1-p)/n)` at that n.** A WIDTH IS NOT AN EFFECT.
- No number crosses scorers, pools or populations. Every table names scorer, n, pool, gold.
- `grounded_similarity()` is NEVER the scorer.
- `ruler_mode_gate()` (`experiments/exp_task_degeneracy_v1.py:121`, reached via
  `exp_cue_to_store_translation_v1.ruler_mode_gate`) is CALLED, not reimplemented. The token
  `--smoke` never enters argv; the reduced-grid flag is `--grid reduced`.
- `verdict_bar_check.py` is run and its class reported and **NOT relied on** (four false passes on
  record); arm-by-arm margins are stated independently.

---

## 3. BRAIN-FIDELITY BLOCK (mandatory, written before the build)

**(a) BRAIN STRUCTURE per component -- a neural system, not a cognitive-theory label, and honest
where nothing pins it.**

| our component | brain structure | status |
|---|---|---|
| exhaustive cosine argmax over 5,491 anchors | **NONE. Nothing in the brain compares a query against every stored item and takes the maximum.** Serial scanning of a lexicon is REFUTED (Forster 1976 vs the parallel family; the field settled on parallel activation with competitive selection on near-simultaneous 100-250 ms electrophysiology). | **OUR INVENTION, and it was never chosen -- it was assumed.** It heads the 08-16 drill's ten-row no-theoretical-justification list. |
| competitive selection among co-activated candidates | **divisive normalisation** -- Carandini & Heeger 2012 *Nat Rev Neurosci* "Normalization as a canonical neural computation"; measured in V1, MT, IT, olfactory bulb, and in lexical selection as the Luce ratio (Levelt/Roelofs/Meyer WEAVER++). | **PINNED-BY-EVIDENCE as a computation.** Its PARAMETERS (pool membership, exponent, semi-saturation) are constraint-derived and are SWEPT, never adopted. |
| per-candidate gain set by that candidate's own recent activation | **adaptation / gain control** (contrast adaptation; firing-rate homeostasis). | PINNED as a phenomenon; the exact form is OURS. |
| generate -> rank -> TEST against a criterion that is NOT the generator -> reject -> re-propose | tip-of-the-tongue literature (Burke & MacKay 1991 transmission deficit; Brown & McNeill 1966) and PROPOSE-BUT-VERIFY word learning (Medina 2011 *PNAS*; Trueswell 2013). **Two literatures, one control structure.** | PINNED as a control structure; the VERIFIER's content is UNPINNED and is the owner's Q8/Q10 "feeling of the word". |

**THE COMPUTATION/PARAMETER SPLIT, applied.** The COMPUTATION here is problem-derived and shared:
*a graded population response must be reduced to one selection, and the reduction must not be
dominated by units that respond to everything.* Any system solving that problem needs a
normalisation. **That is copied exactly.** The PARAMETERS -- how many neighbours are in the pool,
the exponent, the semi-saturation constant -- are constraint-derived and are **SWEPT**. Our worst
result copied a number; our best copied an operation.

**A HONESTY POINT I AM PRE-COMMITTING TO BECAUSE IT IS EASY TO LAUNDER:** normalising over the
CANDIDATES OF ONE QUERY is a **monotone transform within that query and CANNOT CHANGE THE ARGMAX**.
It is arithmetically incapable of moving hit@1 and will be reported as such, not run as if it
could. The direction that CAN change the argmax is normalising each candidate by **its own response
across the query population** -- and that is the same object as hubness correction. Presenting the
first as a brain-derived fix would be exactly the laundering the fidelity gate bans.

**(b) ORGAN REUSE -- enumerated from disk, then reconciled to the registry, verified by RUNTIME.**
`experiments/dehub_transforms.py` is IMPORTED, not reimplemented; `tools/floor_battery.py` supplies
every floor, both tie conventions, `rank_of_best_gold` and the paired bootstrap and is NEVER edited;
`exp_cue_to_store_translation_v1` supplies the cache loaders, the ruler gate and the landed
regression constant. The registry reconciliation and the runtime witness (`sys.modules` after the
run, not grep) are recorded in the arm log.

**(c) PINNED vs OURS.** Divisive normalisation: PINNED as a computation, parameters OURS-swept.
CSLS: **OURS** (Conneau et al. 2017, a machine-translation retrieval method) and is run as the
STANDARD ENGINEERING BASELINE for the same job, labelled as such -- it is not biology and no brain
structure is claimed for it. The exhaustive argmax: OURS, and it is the thing under test.
**VSA algebraic binding, the substrate's core operation, is UNPINNED IN THE BRAIN with three live
accounts and published objections to each; nothing in this run depends on it and nothing tests it.**

**(d) SHELVE / REVIVAL CRITERIA, BRAIN-FRAMED (never performance-framed).** If the normalisation
family does not move hit@1, the shelving criterion is NOT "it did not score". It is: *the brain's
competitive selection operates over a candidate set that a separate PROPOSE stage has already
narrowed, and over a representation built by an ERROR-DRIVEN objective. We applied it to an
un-narrowed 5,491-way pool over a Hebbian-sum representation.* **Revival condition: re-test once a
propose stage narrows the pool, or once the value code is built by a residual update.**

---

## 4. ARM LOG (appended after every arm; newest last)

### ARM 0 -- BUILD + SELF-TEST. **PASS.**

File: `D:\AI\hd-instrument\experiments\exp_readout_ceiling_diagnosis_v1.py`.
`--self-test --grid reduced` ALL PASS. `ruler_mode_gate()` PASS
(`RUN_MODE=full, V=4096, CORPUS_BYTES=64,000,000`); **the token `--smoke` never entered argv.**
`floor_battery.self_test()` S1-S8 PASS (including S8 rejecting the known-broken legacy pool).
`dehub_transforms.formula_selftests()` PASS.

Asserted, not assumed: the random-ranking curve exact on three known answers and monotone in k; the
rank curve FIRES on a planted store (1.0000) and FAILS on a planted null (0.0050) and **agrees with
`floor_battery.hit_at_1_both_tie_conventions` bit-for-bit at k=1**; the 26 comparators produce 22
distinct argmax patterns (they are not one function in disguise); the bootstrap both fires and
fails.

**THREE THINGS THE SELF-TEST CAUGHT, ALL DISCLOSED RATHER THAN QUIETLY FIXED:**

1. **I wrote an assertion that was FALSE ABOUT GEOMETRY, and it fired.** I asserted a planted-null
   store sits within 0.06 of its own random-ranking curve. It does not: random Gaussian data at
   d=32 **has its own hubness**, which is the very phenomenon this cell measures. Asserting an
   exact match would have been asserting a false fact about high-dimensional geometry. The guard
   was rewritten to a factor-of-2.5 band -- which still catches an order-of-magnitude error, an
   off-by-one in k, or an inverted tie convention. Measured ratios: 0.45 / 0.60 / 0.795 at
   k=10/50/100.
2. **`grounded_similarity` IS LOADED DURING EVERY COMPLIANT RUN, AND THE MANDATED GATE IS WHAT
   LOADS IT.** My first check asserted the module was absent from `sys.modules`. It fired. Traced
   by observation, not inference: **`False` before `ruler_mode_gate()`, `True` after it** --
   `ruler_mode_gate` -> `exp_encoding_quality_instrument_v2` -> `hdlab.grounded_similarity`. So
   "is it imported" is the WRONG question and would fail every cell in the repo that obeys the
   ruler gate. **LOADED IS NOT CALLED.** Replaced with a **LIVE TRIPWIRE**: the function is swapped
   in-process for a stub that raises, and the self-test proves the tripwire fires. Nothing on disk
   is modified. The honour-system control is now a mechanical one.
3. My first version of the same check was a SOURCE SCAN, which read the cell's own docstring
   prohibition as a violation. Grep is wrong in both directions on this repo's own measured
   evidence; runtime observation decides.

### ARM 1 -- REDUCED-GRID SMOKE. **LANDED. n=400 items.**

**SCOPE, STATED FIRST: `n = 400` items, `N_BOOT = 2000`. THESE ARE SMOKE NUMBERS ON A 400-ITEM
SUBSET AND MUST NOT BE QUOTED AS RESULTS.** The full run is the one that counts. They are recorded
because **they changed the design**, twice.

Gates, all read BEFORE any treatment number:

| gate | value | verdict |
|---|---|---|
| REGRESSION -- landed partial-cue read-out | **0.0223** vs expected 0.0223, tol 5e-4 | PASS |
| REGRESSION -- landed **exact-key** read-out | **0.0481** vs expected 0.0481 | PASS |
| REGRESSION -- exact-key addressing | **1.0000** | PASS |
| KA_SELF_ADDRESS | **1.0000** (gate 0.95) | PASS |
| NULL_PERMUTED addressing | **0.00000000** against chance 0.00018212 | PASS |

**AND THE SMOKE ALREADY OVERTURNS THE SIMPLE READING OF THE DISPATCH.**

**(a) THE STORE DOES CONTAIN THE ANSWER. BRANCH A IS FALSIFIED.** The exact-key rank curve is
CI-separated **ABOVE** the per-item random-ranking null at **every one of 11 values of k**:

| k | 1 | 2 | 3 | 5 | 10 | 20 | 50 | 100 | 250 | 500 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exact-key cosine | 0.0275 | 0.0800 | 0.1150 | 0.1625 | 0.2300 | 0.3375 | 0.4900 | 0.6400 | 0.7950 | 0.8700 | 0.9175 |
| RANDOM-RANKING null | 0.0091 | 0.0180 | 0.0267 | 0.0435 | 0.0825 | 0.1494 | 0.2900 | 0.4240 | 0.6017 | 0.7210 | 0.8237 |
| lift | **3.02x** | 4.44x | 4.31x | 3.73x | 2.79x | 2.26x | 1.69x | 1.51x | 1.32x | 1.21x | 1.11x |

Median rank of the best gold: **52 of 5,491 eligible**, against a random expectation of **224**.
**So "the store does not contain the answer" is FALSE at smoke scale.** The answer is present and
the ranking is genuinely query-conditional. **The programme is NOT redirected from reading to
writing on this evidence** -- which is the opposite of what the dispatch's leading hypothesis
expected, and it is recorded before the full run so it cannot be re-framed afterwards.

**(b) BUT THE SIGNAL DOES NOT LIVE AT THE TOP OF THE RANKING, AND THAT IS THE ACTUAL DEFECT.**
Put the query-using curve beside the query-IGNORING constant floor's own curve:

| k | 1 | 2 | 5 | 10 | 50 | 100 | 500 |
|---|---|---|---|---|---|---|---|
| EXACT-KEY (uses the query) | 0.0275 | 0.0800 | 0.1625 | 0.2300 | **0.4900** | **0.6400** | **0.8700** |
| F_CONSTANT_PROTOTYPE (ignores it) | **0.1250** | **0.1250** | 0.1650 | 0.3025 | 0.4275 | 0.5425 | 0.8250 |

**The query-using ranking does not overtake a ranking that ignores the query until roughly k=50.**
The store's query-conditional information is real, and it is systematically ABSENT FROM THE TOP OF
THE RANKING. hit@1 alone cannot say that; the rank curve can. **This is the specific stage the
dispatch asked for: not "the read-out is bad" but "the top of the ranking is not where our query
signal is".**

**(c) IT IS NOT HUBNESS, NOT DEGENERACY, NOT FREQUENCY, AND NOT GENERICITY -- FOUR HYPOTHESES DEAD
AT SMOKE.** Measured with the OWNED organ `dehub_transforms`:
- **Nk-Gini REAL 0.7130 vs SCRAMBLE NULL 0.6973.** Essentially identical. **The k-occurrence
  concentration is what a scrambled store already has**, so there is no excess hubness to correct.
- **364 distinct top-1 answers for 400 queries.** The read-out is NOT degenerate.
- corr(times an anchor wins, genericity) = **0.045**; corr(times it wins, log frequency) = **0.042**.
  **The winners are not generic and not frequent.**

**The read-out returns a SPECIFIC, query-conditional, plausible word that is not a WordNet
synonym.** That is a completely different defect from the one the four standard corrections
address, and it independently predicts the de-hubbing family will do nothing -- which is exactly
what `exp_rank1_common_mode_removal_v1` and `exp_task_local_normalisation_pool_v1` already found.

**(d) ALL 29 REPLACEMENT ARMS FAIL AT SMOKE.** 0 of 29 CI-separated above the binding floor. The
sweeps do reach their own failure regimes (KA collapses to 0.3850 at `DIVNORM sigma=0.01` and to
0.7850 at `SUBTRACT_CONSTANT alpha=2.0`), so the parameter grids bracket the usable range rather
than sitting in a flat corner -- the sweep is a real sweep.

**(e) A WARNING ABOUT THE BINDING FLOOR THAT HAS TO BE PUBLISHED.** `F_CONSTANT_PROTOTYPE`'s own
rank curve is **FLAT from k=1 to k=2 (0.1250 -> 0.1250)**. A constant ranking answers the same word
to every question, so a flat step means its second choice adds nothing: its whole score is
essentially ONE anchor that is a WordNet gold for ~12.5% of all items. With a **mean of 50 correct
answers per item** out of 5,491 (the deliberately generous gold: synonyms + hypernyms 2 up +
sisters + hyponyms), that is partly a fact about the GOLD, not only about the read-out. **This does
NOT lower the bar** -- the bar is the bar, and the read-out is still below it. It changes what
clearing it would prove, and it is why the **random-ranking curve**, which uses each item's OWN
pool size and OWN gold count, is the better-calibrated instrument here.

### DESIGN CORRECTIONS FORCED BY THIS SMOKE -- DISCLOSED, NOT QUIETLY FIXED

Three arms were **ADDED** before the full run. **No floor, population, threshold, seed or existing
arm changed**, and every addition can only make the treatment look WORSE, never better:

1. **THE PERMUTED-CUE NULL NOW GETS ITS OWN FULL RANK CURVE**, with a PAIRED margin against the
   exact key at every k. The smoke read `NULL hit@1 = 0.0275` against the exact key's `0.0275` --
   **identical**. A single point cannot distinguish a coincidence at n=400 from the whole top of
   the ranking carrying no item-specific information, and that difference is the entire finding.
2. **THE CROSSOVER k** -- the smallest k at which the query-using curve overtakes the binding
   floor's own curve -- is now computed and published, because it is the number that says *how far
   below the top* the signal lives.
3. **S1b, A CENSUS OF WHAT THE CONSTANT FLOOR IS EXPLOITING** -- the gold-degree distribution over
   anchors and the top generic anchors, so the binding floor is interpretable rather than merely
   large.

### ARM 2 -- **FULL RUN LANDED. 130 s.** `data/exp_readout_ceiling_diagnosis_v1/metrics.json`

Verdict: **`BRANCH_B_ANSWER_IS_PRESENT_BUT_THE_SELECTOR_CANNOT_REACH_IT__REPLACEMENT_CLEARS_FLOOR_NO__KA_PASS`**

**Population, stated once and never crossed:** 5,491 anchors, **n = 3,994 items**, the LANDED OPEN
pool, WordNet generous gold, hit@1 tie-corrected primary, `floor_battery` scorer, N_BOOT=10,000.

**GATES, all passed and read BEFORE any treatment number:**

| gate | value | verdict |
|---|---|---|
| REGRESSION -- landed partial-cue read-out | **0.0223** vs 0.0223, tol 5e-4, n=3994 | PASS |
| REGRESSION -- landed **exact-key** read-out | **0.0481** vs 0.0481 | PASS |
| REGRESSION -- exact-key addressing | **1.0000** | PASS |
| KA_SELF_ADDRESS | **1.0000** (gate 0.95) | PASS |
| NULL_PERMUTED addressing | **0.0000** against chance 0.00018212 | PASS |
| grounded_similarity tripwire | installed, never fired | PASS |

---

#### FINDING A -- **THE STORE DOES CONTAIN THE ANSWER. THE DISPATCH'S LEADING HYPOTHESIS IS FALSIFIED.**

**BRANCH A -- "the stored content does not contain what the task asks for" -- IS FALSE.** The
exact-key rank curve is CI-separated **ABOVE** the per-item random-ranking null at **all 11 values
of k**, and above the **permuted-cue null** at all 11 as well:

| k | 1 | 2 | 3 | 5 | 10 | 20 | 50 | 100 | 250 | 500 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **EXACT-KEY cosine** | **0.0481** | 0.0931 | 0.1249 | 0.1715 | 0.2604 | 0.3861 | 0.5566 | 0.6855 | 0.8067 | 0.8823 | 0.9307 |
| RANDOM-RANKING null | 0.0101 | 0.0199 | 0.0295 | 0.0478 | 0.0897 | 0.1600 | 0.3041 | 0.4402 | 0.6224 | 0.7441 | 0.8443 |
| lift | **4.77x** | 4.68x | 4.24x | 3.59x | 2.90x | 2.41x | 1.83x | 1.56x | 1.30x | 1.19x | 1.10x |
| PERMUTED-CUE null | 0.0120 | 0.0225 | 0.0318 | 0.0533 | 0.0997 | 0.1948 | 0.3535 | 0.4995 | 0.6725 | 0.7804 | 0.8618 |
| margin vs permuted cue / **own CI half-width** | **4.9x** | 7.0x | 8.1x | 8.8x | **10.2x** | 11.2x | **11.3x** | 11.0x | 9.0x | 7.9x | 6.4x |

Median rank of the best gold: **37 of 5,491 eligible**, against a random expectation of **203**.

**These are effects, not widths.** Every margin is 4.9x to 11.3x its own CI half-width, and the
half-widths are published in the metrics beside each one.

**IMPORTANT RETRACTION OF MY OWN SMOKE READING, MADE BEFORE ANYONE ELSE HAD TO CATCH IT.** At
n=400 the permuted-cue null read **0.0275 against the exact key's 0.0275 -- identical** -- and I
flagged that as possibly meaning the top of the ranking carried no item-specific information at
all. **At n=3,994 that is measured and FALSE: 0.0481 vs 0.0120, separated by 4.9x its own CI
half-width.** The smoke's identity was a small-n coincidence. This is exactly the error pattern the
handoff names -- an underpowered comparison read as a capability statement -- and the only reason
it did not become a claim is that the null was given its own full curve and its own n before
anything was written down.

#### FINDING B -- **THE DEFECT IS A SPECIFIC STAGE, AND ITS NAME IS THE TOP OF THE RANKING.**

The dispatch asked for a stage, not "the read-out is bad". Here it is. Put the query-USING ranking
beside the query-IGNORING constant:

| k | 1 | 2 | 5 | 10 | 20 | **50** | 100 | 500 |
|---|---|---|---|---|---|---|---|---|
| EXACT-KEY (uses the query) | 0.0481 | 0.0931 | 0.1715 | 0.2604 | 0.3861 | **0.5566** | 0.6855 | 0.8823 |
| F_CONSTANT_PROTOTYPE (ignores it) | **0.1390** | **0.1395** | **0.1788** | **0.3282** | **0.3896** | 0.4767 | 0.5886 | 0.8368 |

**CROSSOVER k = 50.** The store's query-conditional signal is real, is 4.77x random at the very top,
and **still does not overtake a ranking that ignores the question until the 50th candidate.**

**THE STAGE IS: WE HAVE A GOOD SHORTLIST AND NO SELECTOR.** The information needed to answer is
in the top ~50 of 5,491 for most items; the operation we perform on that shortlist -- take the
maximum -- is the one operation that throws it away.

#### FINDING C -- **AND HERE IS WHAT THE READ-OUT ACTUALLY RETURNS. THIS IS THE MECHANISM.**

`example_query_to_winner`, verbatim from the metrics, first 18 items:

```
ability -> work        absence -> presence     abbey -> highclere     abnormality -> chromosomal
absorb -> pigment      abundance -> endemic    academy -> proceedings academic -> findings
abandon -> palm        abroad -> gain          absent -> limitation   accelerate -> tness
```

**These are not failed synonyms. They are COLLOCATES.** `abbey -> highclere` (Highclere Abbey),
`abnormality -> chromosomal`, `absorb -> pigment`, `academy -> proceedings`, `academic -> findings`
-- every one is a word that OCCURS WITH the query, not one that SUBSTITUTES FOR it. And
`absence -> presence` is an **ANTONYM**, the single most famous failure mode of a distributional
space, because antonyms share nearly all their contexts.

**FOUR CANDIDATE CAUSES MEASURED AND ALL FOUR DEAD:**

| hypothesis | measurement | dead? |
|---|---|---|
| **degeneracy** (it returns the same thing) | **2,331 distinct answers for 3,994 queries**; the top 25 winners take only **6.08%** | DEAD |
| **genericity** (it returns generic hubs) | corr(times won, constant-prototype score) = **0.137** | DEAD |
| **frequency** (it returns common words) | corr(times won, log corpus count) = **0.146** | DEAD |
| **hubness** (a few anchors absorb every ranking) | Nk-Gini REAL **0.5058** vs SCRAMBLE NULL **0.4610**; the single largest hub takes **0.348%** of all top-10 slots | MOSTLY DEAD -- a modest real excess, far too small to explain a 3x shortfall |

**The read-out is confidently, specifically and consistently returning the wrong KIND of word.**
Its winners score a mean cosine of **0.4757** against the best gold's **0.2844** -- a gap of
**+0.1914**. It is not uncertain. It is certain and wrong.

#### FINDING D -- **THE BINDING FLOOR IS PARTLY A FACT ABOUT THE GOLD, AND THAT HAS TO BE SAID.**

`F_CONSTANT_PROTOTYPE`'s own rank curve is **FLAT from k=1 to k=2 (0.13896 -> 0.13946)**. S1b names
the mechanism exactly: the most generic anchor is the word **`work`**, and **`work` is a WordNet
gold for 555 of 3,994 items (13.9%)**. One anchor. The most gold-connected anchor of all is gold
for **684 items (17.1%)** -- which is precisely the ORACLE constant, 0.17151. **228 anchors are a
correct answer for at least 5% of all items**, and the gold averages **55.4 correct answers per
item** out of 5,491.

**THIS DOES NOT LOWER THE BAR.** The read-out is still below the floor and the floor is still the
bar. It changes what CLEARING it would have proved, and it is why the **random-ranking curve** --
which uses each item's OWN pool size and OWN gold count -- is the better-calibrated instrument on
this population, and why FINDING A is stated against that curve rather than against the floor.

#### FINDING E -- **ALL 29 REPLACEMENT COMPARATORS FAIL. 0 OF 29 CLEAR THE FLOOR.**

| arm | hit@1 |
|---|---|
| ORACLE_CONSTANT (fitted on golds, **NOT a floor**) | 0.17151 |
| **F_CONSTANT_PROTOTYPE (binding floor)** | **0.13896** |
| F_ORTHOGRAPHIC (spelling) | 0.08731 |
| best replacement: R1_CSLS_k10 | 0.05058 |
| **R0_COSINE_ARGMAX_INCUMBENT** | **0.04807** |
| worst swept: R4_DIVNORM sigma=0.01 | 0.01703 |
| F_SCRAMBLE | 0.01327 |

The best of 29 arms moves the incumbent by **+0.0025**, against a binding floor **0.0909 above**.
The sweeps reach their own failure regimes (KA collapses on 3 arms), so the grids bracket the
usable range. **The normalisation family is refuted on this instrument** -- consistent with, and
now extending to the open 5,491-way pool, the prior HARD_FAILs of `exp_rank1_common_mode_removal_v1`
and `exp_task_local_normalisation_pool_v1` credited in section 1.

**A PRE-REGISTERED ANALYTIC CLAIM, NOW CONFIRMED ON REAL DATA:** I wrote before the run that the
anchor's mean similarity over a probe population IS the constant/prototype floor, i.e. that the
hubness correction and the binding floor are the same object from two sides. **Measured:
corr = 0.9995.** So subtracting the hubness correction is subtracting the floor's own channel --
and doing it monotonically DESTROYS the read-out (alpha 0.25 -> 2.0 drives hit@1 0.0438 -> 0.0273).
**The generic component our read-out shares with the floor is not noise sitting on top of the
signal; removing it removes signal.** That independently reproduces
`exp_task_local_normalisation_pool_v1`'s "suppressing shared dimensions destroys signal the
comparator needs" on a completely different scorer and pool.

---

### ARM 3 -- THE MECHANISM CELL (C1-C4), SMOKE IN FLIGHT

File `D:\AI\hd-instrument\experiments\exp_readout_second_order_v1.py`. Detached, **PID 3404**,
logs `scratch/readout_ceiling/C_SMOKE.out` / `.err`. Self-tests ALL PASS.

Arms: **C1** winner forensics (WordNet relation of the winner to the query); **C2** the
SYNTAGMATIC TEST -- do winners co-occur with the query in the corpus more than gold synonyms do
(corpus re-read for COUNTS ONLY; **the store is never rebuilt**); **C3** second-order read-out
(profile truncation k SWEPT); **C4** the **SUCCESSOR REPRESENTATION** `M = (I - gamma*A)^-1` on our
own anchor graph, gamma SWEPT -- which `ORGAN_MAP` D7 lists as MISSING and the 08-16 theory drill
describes as *"cheap, glass-box, uses no external asset, and it has never been run."*

**TWO SELF-TEST FAILURES IN THIS CELL, BOTH DISCLOSED, AND THE SECOND CHANGED THE METHOD:**
1. My first T1 fixture was **wrong and would have tested nothing** -- both arms read 0.0000,
   because every word sharing a context direction was closer to the query than its own partner.
   Rebuilt so partners are strictly ORTHOGONAL to each other and share only mediators, plus an
   added assertion that first-order MUST fail on it (`h1 < 0.10`) so a second-order win cannot be
   vacuous.
2. **The SELF term had to be removed from the profiles**, and the self-test is how I found out.
   With the diagonal left in, a DIRECTLY ADJACENT word outscores the query's true profile-twin,
   because the two big self entries pair with the direct similarities and hand the neighbour a
   spurious overlap. On the fixture that alone was the difference between the arm working and
   reading 0.0000. **A word's similarity to itself carries no information about its
   NEIGHBOURHOOD**, which is the quantity a second-order measure is defined on, so this is the
   correct operation and not a tuning knob -- but it was discovered, not designed, and it is
   recorded as discovered.

---

### ARM 4 -- C-CELL SMOKE. **THE PRE-REGISTERED PREDICTION FIRED, AND IT NAMES THE CAUSE.**

**SCOPE FIRST: `n = 400` items. SMOKE NUMBERS. NOT RESULTS.** The full run follows.

#### C2 -- **THE SYNTAGMATIC TEST. `SYNTAGMATIC_CONFIRMED`.**

The prediction was written into the cell BEFORE the run: *"the top-1 WINNER co-occurs with the
query word in the same sentence far more than the best GOLD synonym does."* Measured over the
**34,169-sentence corpus the store was built from**, re-read for COUNTS ONLY (**the store was never
rebuilt** -- the identical-instrument invariant holds and the regression gate re-passed at 0.0223 /
0.0481 inside this cell):

| sentence-level Jaccard with the query word | mean |
|---|---|
| sentence-level Jaccard with the query word | mean | median | **fraction that EVER co-occur** |
|---|---|---|---|
| **the read-out's TOP-1 WINNER** | **0.08668** | 0.06487 | **91.5%** |
| the BEST GOLD SYNONYM | 0.01992 | **0.0000** | **44.25%** |
| a RANDOM ELIGIBLE ANCHOR | 0.00035 | 0.0000 | -- |

**The word our read-out returns co-occurs with the query 4.35x more than the correct answer does,
and 248x more than chance.**

**AND THE DEEPEST FORM OF THE FINDING IS IN THE LAST COLUMN, WHICH I DID NOT ANTICIPATE.** The
read-out's answer shares a sentence with the query for **91.5%** of items. **The CORRECT answer
does so for only 44.25%, and its MEDIAN co-occurrence is EXACTLY ZERO** -- meaning **for more than
half of all items, the right answer is a word that NEVER APPEARS IN THE SAME SENTENCE AS THE QUERY
ANYWHERE IN THE 34,169-SENTENCE CORPUS.**

**TWO CONFOUNDS A REVIEWER WOULD RAISE, BOTH CHECKED, AND THE FIRST MAKES THE RESULT STRONGER.**
(1) The "BEST GOLD SYNONYM" arm is the **highest-scoring gold in our own space** -- i.e. the gold
that is MOST similar to the query by our own metric, and therefore the gold most likely to
co-occur. **The comparison is deliberately stacked against the finding and it fires anyway**: the
winner is the most-similar-overall candidate and the gold arm is the most-similar-among-correct, so
this is a matched most-vs-most contrast, not a best-vs-average one. (2) Frequency: a very common
winner would co-occur with everything. **Jaccard normalises by the union**, so a high-frequency
word's large denominator suppresses rather than inflates its score -- the measure already controls
the direction of that confound, and S3 independently measured corr(times won, log frequency) =
0.146.

**A store built exclusively from co-occurrence cannot represent a relation whose instances mostly
never co-occur.** That is not a tuning shortfall, a comparator shortfall, or a capacity shortfall.
It is a **representational impossibility given the write rule**, and it holds for the majority of
the task. It also explains, without any further measurement, why the answer is nonetheless
recoverable at rank ~37: the residual signal comes from the minority of pairs that DO co-occur plus
second-order leakage, which is exactly the faint 4.77x we measured.

#### C1 -- WINNER FORENSICS: the winners are not near-misses, they are a different relation

| what the top-1 pick IS | fraction |
|---|---|
| TAXONOMICALLY DISTANT | **0.5150** |
| **NO WORDNET PATH AT ALL** | **0.3075** |
| winner not in WordNet | 0.0875 |
| taxonomically close but outside the generous gold | 0.0625 |
| in the generous gold (= the hit) | 0.0275 |

**82% of the winners are taxonomically distant or have no WordNet path whatsoever.** They are not
failed synonyms. They are not almost-right. They are a **different relation**.

---

### ARM 5 -- **C-CELL FULL RUN LANDED. 132 s.** `data/exp_readout_second_order_v1/metrics.json`

Verdict: **`SYNTAGMATIC_CONFIRMED__NEW_READOUT_CLEARS_FLOOR_NO__BEATS_INCUMBENT_NO`**

n = 3,994 items, N_BOOT = 10,000. Regression re-passed inside this cell (0.0223 / 0.0481),
KA 1.0000, NULL 0.012018.

#### C2 CONFIRMED AT FULL SCALE

| sentence-level Jaccard with the query | mean | median | fraction that EVER co-occur |
|---|---|---|---|
| **read-out's TOP-1 WINNER** | **0.08090** | 0.05714 | **89.87%** |
| BEST GOLD SYNONYM | 0.01908 | **0.0000** | **46.73%** |
| RANDOM ELIGIBLE ANCHOR | 0.00043 | 0.0000 | 4.93% |

**Ratio 4.24x.** The ordering winner >> gold >> random is the honest one: gold DOES co-occur far
more than random (9.5x), so co-occurrence is not orthogonal to meaning. But what we RETURN
co-occurs almost twice as often as what is CORRECT, and **the median correct answer never shares a
sentence with the query at all.**

#### C1 AT FULL SCALE -- 79.3% of winners are not a taxonomic relation

`TAXONOMICALLY_DISTANT` 0.534, `NO_WORDNET_PATH_AT_ALL` 0.259, winner not in WordNet 0.097,
taxonomically close but outside the gold 0.0635, **in the gold (the hit) 0.0465**. With the
path-similarities printed: `able -> might (0.000)`, `abnormality -> chromosomal (0.000)`,
`abroad -> gain (0.000)`, `absolutely -> farm (0.000)`, `absorb -> pigment (0.200)`.

#### C3 / C4 -- **BOTH NEW READ-OUTS FAIL, AND THE SUCCESSOR REPRESENTATION FAILS CI-SEPARATED BELOW**

| arm | hit@1 | margin vs incumbent |
|---|---|---|
| **F_CONSTANT_PROTOTYPE (binding floor)** | **0.13896** | -- |
| F_ORTHOGRAPHIC | 0.08731 | -- |
| C3_SECOND_ORDER_profileK0 (untruncated) | 0.05358 | +0.0055 [-0.0013,+0.0125] NOT_SEPARATED |
| C3_SECOND_ORDER_profileK250 | 0.05183 | +0.0038 NOT_SEPARATED |
| **R0_COSINE_ARGMAX_INCUMBENT** | **0.04807** | -- |
| C4_SR_gamma0.5 | 0.03806 | **-0.0100 [-0.0168,-0.0035] BELOW** |
| C4_SR_gamma0.3 | 0.03756 | **-0.0105 BELOW** |
| C4_SR_gamma0.7 | 0.03631 | **-0.0117 BELOW** |
| C4_SR_gamma0.9 | 0.03506 | **-0.0130 BELOW** |
| C3_SECOND_ORDER_profileK10 | 0.03430 | **-0.0137 BELOW** |

**0 of 10 arms clear the floor. 0 beat the incumbent. The SUCCESSOR REPRESENTATION is CI-separated
BELOW the incumbent at ALL FOUR values of gamma.**

**THE SUCCESSOR REPRESENTATION HAS NOW BEEN RUN.** `ORGAN_MAP` D7 lists it as MISSING and the
08-16 theory drill said of it *"it is cheap, it is glass-box (a matrix inverse of a graph we own),
it uses no external asset, and it has never been run"*, with a deflated P ~ 0.35. **It is run, on
our own anchor graph, in closed form, with gamma swept over four values, and it LOSES -- not
narrowly, but CI-separated below a read-out that is itself 0.35x its floor.** The drill's own
stated reason for the deflation is the one that bit: propagating through a graph whose multi-hop
tail is noise adds noise, and every increase in gamma (more propagation) makes it monotonically
worse -- 0.03806 -> 0.03506 as gamma goes 0.5 -> 0.9. That monotone ordering is itself the
mechanism, and it is evidence rather than an excuse.

**AND TRUNCATION HURTS, WHICH IS THE OPPOSITE OF WHAT THE METHOD PREDICTS.** The
distributional-semantics expectation is that truncating profiles to their top-k is what makes a
second-order measure express paradigmatic similarity. Measured here: k=10 is the WORST arm
(-0.0137, CI-separated BELOW), and performance rises monotonically with k until the UNTRUNCATED
profile is the best of the family. **Our top-k neighbourhoods are the syntagmatic part; the
paradigmatic residue is in the tail.** That is consistent with everything else in this log and it
was not predicted.

#### **A THIRD RETRACTION OF MY OWN, AND IT IS THE SAME LESSON AS THE FIRST TWO**

At n=400 this cell reported **`BEATS_INCUMBENT_YES`** with two arms CI-separated above the
incumbent (`profileK0` +0.0251 [+0.0075,+0.0450]; `profileK250` +0.0227 [+0.0075,+0.0400]).
**At n=3,994 both collapse to NOT_SEPARATED** (+0.0055 [-0.0013,+0.0125] and +0.0038
[-0.0033,+0.0108]).

**That is the third time tonight a small-n reading did not survive scaling** -- the permuted-cue
null's apparent identity to the exact key (retracted in ARM 2), and now two apparent wins. **In one
case the smoke was pessimistic and in two it was optimistic**, which is exactly what a width does:
it moves in both directions. **A WIDTH IS NOT AN EFFECT**, and the only reason none of these three
became a claim is that every smoke number in this log was labelled SMOKE and the full run was
always the one that counted.

---

## 5. THE DIAGNOSIS, STATED AS ONE SENTENCE

**OUR STORE COMPUTES A SYNTAGMATIC NEIGHBOURHOOD -- WORDS THAT OCCUR WITH THE QUERY -- AND THE TASK
ASKS A PARADIGMATIC QUESTION -- WORDS THAT SUBSTITUTE FOR IT. THOSE ARE DIFFERENT RELATIONS, AND
THE DEFECT IS IN THE WRITE RULE, NOT IN THE COMPARATOR.**

Every measurement above converges on it and none of them was designed to find it:

- the answer IS in the store (4.77x random at k=1, median rank 37 of 5,491) -- so it is **not** a
  supply failure and **not** a "we never wrote it down" failure;
- but the top of the ranking is owned by something else, and the crossover against a
  question-ignoring constant is at **k=50**;
- the winners are specific (2,331 distinct), not generic (r=0.137), not frequent (r=0.146), not
  hubs (Nk-Gini barely above scramble), and **confident** (cosine +0.1914 above the true answer);
- 82% of them have no close WordNet relation to the query at all;
- and they co-occur with the query **4.35x more than the right answer does**.

**`self._sums[lemma] += ctx_vec` IS A FIRST-ORDER CO-OCCURRENCE SUM, SO FIRST-ORDER COSINE OVER IT
RETURNS CO-OCCURRENCE PARTNERS BY CONSTRUCTION.** `absence -> presence` is the tell: an antonym is
the hardest case for a co-occurrence space and the easiest for a substitutability space, because
antonyms share almost all their contexts and can never substitute.

**WHAT THIS MEANS FOR THE PROGRAMME, and it is neither of the two outcomes the dispatch anticipated.**
The dispatch's decision-relevant branch was "if the stored content does not contain the answer, say
so loudly, because that redirects the programme from reading to writing." **The content DOES
contain the answer -- so that exact redirection is not licensed.** But the cause is still in the
WRITE: not in what was stored, but in **what relation the write rule encodes**. The store faithfully
encodes the relation it was told to encode. Nobody ever checked that it was the relation the task
needs.

**This is the 2026-08-16 theory drill's section 4d and 6c arriving as a measurement rather than an
argument.** That drill wrote that our slow store accumulates a raw first-order co-occurrence sum,
that **"it is not the statistic CLS names"**, that every implemented cortical model in that lineage
uses an **ERROR-DRIVEN** objective rather than a Hebbian sum, and that taxonomic (substitutability)
and thematic (complementarity) *"are different metrics over the same vocabulary, and no single
vector space can express both as high cosine without collapsing them."* The drill predicted this
number. We are now measuring it.

*Section 5 is a strategic read and is labelled **HYPOTHESIS PENDING VET**. Findings A-E and C1/C2
are measured.*

---

## 6. THE ONE ACTIONABLE NUMBER: WHAT A PROPOSE-AND-VERIFY READ-OUT WOULD BE WORTH

The brain does not take an argmax over a lexicon. The owner's Q8 answer, the tip-of-the-tongue
literature (Burke & MacKay 1991) and the PROPOSE-BUT-VERIFY word-learning literature (Medina 2011
*PNAS*; Trueswell 2013) specify the same control structure: **generate candidates in parallel, then
TEST each against a criterion that is NOT the generator, reject, re-propose.** The 08-16 drill named
the missing organ precisely: *"`canonicalize_fast` is `argmax` over cosine: a generator with no
verifier and no reject step."*

**hit@k of the first stage IS the exact ceiling of a two-stage read-out with a PERFECT verifier at
shortlist size k.** It is an ORACLE, not a floor -- it presumes a verifier we have not built -- but
it is measured, on the full population, and it is the number that says whether the missing organ is
worth building:

| shortlist size k | 1 (= today) | 3 | **5** | 10 | 20 | 50 |
|---|---|---|---|---|---|---|
| ceiling of a perfect verifier | **0.0481** | 0.1249 | **0.1715** | **0.2604** | **0.3861** | **0.5566** |
| binding floor `F_CONSTANT_PROTOTYPE` | 0.1390 | 0.1390 | 0.1390 | 0.1390 | 0.1390 | 0.1390 |

**A PERFECT VERIFIER OVER A SHORTLIST OF FIVE ALREADY CLEARS THE BINDING FLOOR (0.1715 vs 0.1390),
AND OVER TEN IT IS 1.9x THE FLOOR.** Today's single argmax is at **0.35x the floor.**

**So the two defects are separable and only one of them is a wall:**
- the **WRITE-RULE** defect (syntagmatic where the task is paradigmatic) caps how good the shortlist
  can get, and for the >50% of items whose correct answer never co-occurs with the query it is a
  hard representational limit of a co-occurrence store;
- the **READ-OUT** defect (argmax with no verifier) is throwing away information that is
  demonstrably present, and the size of what it throws away is the gap between 0.0481 and 0.5566.

**NEITHER IS FIXED BY A BETTER COMPARATOR, which is what all 29 ARM B arms and both prior landed
HARD_FAILs were.** That family is now refuted three times on three different instruments and should
be shelved -- with a BRAIN-FRAMED revival criterion, not a performance one: *competitive
normalisation in the brain operates over a candidate set a separate PROPOSE stage has already
narrowed, and over a representation built by an error-driven objective. We applied it to an
un-narrowed 5,491-way pool over a Hebbian sum. Revive it when either of those two conditions is
repaired -- not before, and not because it "did not score".*

**WHAT I AM NOT CLAIMING.** That a verifier can be built to that ceiling: a perfect verifier is an
oracle and the honest expectation is far below it. That the verifier's criterion is known: the
owner's Q10 ("the FEELING of the word") points at register/formality, a sibling found the profile
rejector generalises where attestation is structurally blind, and **AFFECT contributed nothing once
width-matched** -- so the verifier's content is UNPINNED and is its own build. And nothing here
tests VSA binding, which remains UNPINNED in the brain with three live accounts.

---

## 7. WHAT WAS TESTED AND WHAT IT COST -- the scoreboard

**39 read-out arms across two cells, all on the identical scorer / n / pool / gold. NONE clears the
binding floor. NONE beats the incumbent CI-separated.**

| family | arms | brain status | result |
|---|---|---|---|
| exhaustive cosine argmax (incumbent) | 1 | **OURS, never chosen -- assumed** | 0.04807, **0.35x its floor** |
| CSLS (Conneau 2017) | 6 | OURS, engineering baseline | best +0.0025, none clears |
| subtract the constant/genericity channel | 6 | divisive normalisation PINNED as a computation, parameters SWEPT | monotonically WORSE (0.0438 -> 0.0273) |
| per-anchor z-normalisation | 1 | same | 0.03756, worse |
| divisive normalisation, sigma x exponent | 12 | same | best 0.04932, none clears; KA collapses at sigma=0.01 |
| second-order profile, truncation swept | 6 | OURS (Ruge / distributional tradition) | best +0.0055 NOT_SEPARATED; truncation HURTS |
| **successor representation, gamma swept** | 4 | **PINNED as a representational signature; using M as a retrieval score is OURS** | **CI-separated BELOW at all four gammas** |

**The one thing that was never tried is the one the brain actually does: a shortlist plus a
verifier that is not the generator.** Its measured ceiling is 0.1715 at k=5 and 0.2604 at k=10,
against a floor of 0.1390 and an incumbent of 0.0481.

---

## 8. BRAIN-FIDELITY CLOSE-OUT

**(a) STRUCTURE PER COMPONENT.** The read-out under test has **no brain structure** -- nothing in
the brain compares a query against every stored item and takes the maximum, and serial lexicon
scanning is refuted. Competitive selection by divisive normalisation is PINNED as a computation
(Carandini & Heeger 2012) and its parameters were swept, not adopted. The successor representation
is PINNED as a representational signature (Stachenfeld et al. 2017) and CONTESTED in its learning
rule; using M's rows as a retrieval score is OURS and is now a measured negative. **Where nothing
pins a choice, this log says so rather than inventing an anatomy for it.**

**(b) ORGAN REUSE -- enumerated from disk, then reconciled, verified by RUNTIME.** `dehub_transforms`
(the owned de-hubbing organ), `tools/floor_battery`, `exp_cue_to_store_translation_v1`,
`tools/exp_checkpoint`, and the diagnosis cell itself were IMPORTED and **none was edited**. The
runtime witness is `sys.modules` after the work, recorded in both metrics files -- not grep.
**`dehub_transforms` is an `experiments/`-level module, NOT in `hdlab/` and NOT registry-WIRED**,
which a registry-first audit would have missed entirely.

**(c) PINNED vs OURS.** Stated per arm in section 7. **VSA algebraic binding -- the substrate's core
operation -- is UNPINNED in the brain, with three live accounts and published objections to each.
Nothing in this run depends on it and nothing in this run tests it.**

**(d) SHELVE / REVIVAL, BRAIN-FRAMED.** The **normalisation family** is shelved: revive when a
PROPOSE stage has narrowed the pool, or when the value code is built by a residual rather than a
uniform sum -- because that is the regime the brain's normalisation actually operates in. The
**successor representation** is shelved: revive on a graph whose multi-hop tail is not noise, since
the monotone gamma ordering shows propagation is adding noise, not structure. **Neither is shelved
for "not scoring."**

---

## 9. WHAT THIS RUN DOES **NOT** CLAIM

- **No number here crosses scorers, pools or populations.** Everything is hit@1 tie-corrected over
  5,491 anchors on 3,994 items, landed OPEN pool, WordNet generous gold. The 0.0481 / 0.1390 /
  0.0873 / 0.17151 are facts about **this** population only.
- **It does not claim the read-out ceiling is a CEILING.** Children acquire most of their
  vocabulary this way, so the capability is DEMONSTRATED. Every negative here is a fact about our
  implementation, and section 6 names the specific implementation that was never built.
- **It does not claim the store is worthless.** It claims the store encodes a DIFFERENT RELATION
  from the one the task scores, and that the target relation's instances mostly do not co-occur.
- **It does not claim a verifier will work.** The 0.1715/0.2604 figures are ORACLE ceilings.
- `verdict_bar_check.py` was run on the landed diagnosis metrics and returned
  **`disagreement_class: AGREES`, `declared_clearing_arms: []`**. **Reported, NOT relied on** -- it
  has four false passes on record. Every margin in this log is stated arm-by-arm with its own CI
  half-width independently of it.

---

## 10. ARM 6 -- THE WRITE RULE, NOT THE COMPARATOR: `exp_readout_writerule_paradigmatic_v1`

**FULL RUN LANDED. 84.2s.** `data/exp_readout_writerule_paradigmatic_v1/metrics.json`, commit
`a8fdc968f`. n=3994, N_BOOT=10000, W0 regression gate PASS (0.0223/0.0481), K1 addressing 1.0000 on
ALL seven arms (W0, W1, three W2 alphas, N1, F_FREQ_MATCHED), NULL_PERMUTED near chance on all seven
(0.0055-0.0085 vs chance ~0.0002... actually vs the item-count-scaled chance, all far below the real
arms' own values). No K1 failure -- the instrument did not need to void this run.

**HOW THIS DIFFERS FROM ARM 5 (`exp_readout_second_order_v1`), STATED PRECISELY.** ARM 5 applied
second-order structure AT READ TIME: an unmodified first-order store, comparator = cosine of
similarity PROFILES over that store. This cell applies it AT WRITE TIME: a NEW store is built where
each word's code sums its neighbours' own first-order PROFILE ROWS (reused from the incumbent's
cached `mat`, never rebuilt) instead of their identity draws. The comparator (plain cosine argmax) is
unchanged in every arm. ARM 5's own conclusion -- "a second-order READ of a first-order store cannot
manufacture a distinction the WRITE never encoded" -- is the exact hypothesis this cell tests by
changing the WRITE instead.

**ARM-BY-ARM, PARTIAL-CUE hit@1 (primary), margins with CI half-width and analytic null half-width
beside each:**

| arm | value | own binding floor | margin vs own floor | margin vs W0 |
|---|---|---|---|---|
| W0_SYNTAGMATIC (incumbent) | 0.02228 | F_CONSTANT_PROTOTYPE 0.13896 | -0.1167 [-0.1282,-0.1054] hw=0.0114, BELOW | -- |
| **W1_PARADIGMATIC** | **0.02979** | F_ORTHOGRAPHIC 0.08731 | -0.0575 [-0.0673,-0.0478] hw=0.00975, BELOW | **+0.0075 [0.0023,0.0128] hw=0.00525, ABOVE (1.4x)** |
| W2_HYBRID alpha=0.25 | 0.02879 | F_ORTHOGRAPHIC 0.08731 | -0.0586 hw=0.00975, BELOW | +0.0065 [0.0028,0.0105] hw=0.00385, ABOVE |
| W2_HYBRID alpha=0.5 | 0.02929 | F_ORTHOGRAPHIC 0.08731 | -0.0581 hw=0.00995, BELOW | +0.0070 [0.0023,0.0118] hw=0.00475, ABOVE |
| W2_HYBRID alpha=0.75 | 0.02904 | F_ORTHOGRAPHIC 0.08731 | -0.0583 hw=0.00985, BELOW | +0.0068 [0.0018,0.0118] hw=0.005, ABOVE |
| N1_NULL (random-profile perm) | 0.01878 | F_CONSTANT_PROTOTYPE 0.14472 | -0.1260 hw=0.01155, BELOW | -0.0035 [-0.0078,0.0008] hw=0.0043, NOT_SEPARATED |
| F_FREQ_MATCHED_PROFILE | 0.02253 | F_CONSTANT_PROTOTYPE 0.12318 | -0.1006 hw=0.01105, BELOW | +0.0002 [-0.0048,0.0053] hw=0.00505, NOT_SEPARATED |

Analytic null half-widths at n=3994 are all 0.0046-0.0109, close to the CI half-widths above -- these
margins are real effects, not artifacts of an underpowered comparison, but they are SMALL effects.

**WHICH STOP-IF FIRED: NONE OF THE THREE CLEANLY.** (i) did not fire -- W1 does not clear its own
floor (0.02979 vs 0.08731, still 2.9x short). (ii) did not fire -- W1 CI-separates ABOVE W0, it does
not tie it. (iii) did not fire in the form pre-registered -- F_FREQ_MATCHED_PROFILE does NOT beat W0
(NOT_SEPARATED, point +0.0002), so W1's lift is not explained away as a frequency effect in costume.
N1_NULL (pure random-profile smoothing) also does not beat W0. **The honest fourth reading, not
anticipated in the stop-if list: the write rule was PART of the defect -- swapping identity for
profile buys a small, real, non-frequency, non-smoothing lift (+0.0075, about 34% relative) -- but it
is nowhere near enough to close a gap that is still 2-3x the floor.** The write rule is not innocent,
and it is not sufficient either.

**ORTHOGRAPHIC LEAKAGE CHECK (standing rule 12): CLEAN.** Mean trigram-cosine of each arm's top-1
winner to the query: W0 0.02684, W1 0.02939, W2 alphas 0.02711-0.02825, N1 0.02640, FREQ_MATCHED
0.02691 -- all clustered near W0's own value and nowhere near the orthographic floor's own reference
point (1.0, i.e. that floor's own top-1 pick is essentially a spelling match to the query, as
expected for a construction that ranks purely on trigram similarity). W1's small lift over W0 is NOT
a floor cleared by encoding spelling; the write rule was not gamed into a disguised orthographic
channel.

**SELF-TEST CAUGHT TWO REAL BUGS BEFORE ANY NUMBER WAS TRUSTED, BOTH DISCLOSED IN THE CELL'S OWN
COMMENTS.** (1) `hdlab.reading_grounding_loop.content_words()` extracts only alphabetic runs of
length>2 via regex on lowercased text; a first fixture using tokens like `"c0"` and single-letter
`"A"` silently vanished at tokenization, and T2 read `cos_P=0.0000` -- caught, not silently patched
around. (2) A first fixture drew both targets' filler words from ONE shared pool, so the
"first-order-orthogonal" control read `cos_I=0.2414`, not the near-zero the fixture intended --
literal token overlap, not sampling noise. Fixed by giving each target a disjoint filler pool.
Post-fix: `cos_I=-0.0263` (unrelated, first-order), `cos_P=0.9912` (near-total recovery,
second-order), `N1_NULL` destroys it back to `0.0452`, hybrid alpha interpolates monotonically
`-0.026 -> 0.41 -> 0.85 -> 0.97 -> 0.99`, masking is load-bearing, and PROFILE does NOT fire on a
flat/unrelated-profile fixture (`-0.0263 -> -0.0397`, falsifiable). The full-scale corpus/bucket
reconstruction was also re-verified inside the self-test (not just the pre-authoring probe):
5491/5491 anchors match the cache exactly.

**Prior-work check (per the standing rule):** `exp_readout_second_order_v1` (ARM 3-5 above) is the
one directly relevant prior cell and is credited throughout as the read-time sibling this cell's
write-time construction is contrasted against; no other cell in this repo changes the write rule
itself (enumerated via the same `experiments/` filter used in section 1: readout / rerank / hub /
csls / normal / argmax / rank / write / second_order / profile turned up nothing else that rebuilds
the store).

**WHAT THIS DOES AND DOES NOT LICENSE.** It does NOT license "the write rule was the defect" in the
strong form the dispatch's stop-if (i) described -- that would require clearing a floor, and nothing
here does. It DOES license retiring the narrower claim that the relation encoded is irrelevant to the
ceiling: a controlled, frequency-ruled-out, orthography-ruled-out change to what gets written moved
hit@1 by a small but CI-separated amount. The remaining ~2-3x gap to the floor is not explained by
this cell and is not claimed to be.
