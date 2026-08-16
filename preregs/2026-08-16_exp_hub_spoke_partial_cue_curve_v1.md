# PRE-REGISTRATION -- exp_hub_spoke_partial_cue_curve_v1

**Status: WRITTEN BEFORE ANY ARM OF THIS CELL WAS SCORED.** Author: exp_dev. Date: 2026-08-16.
Branch `dataprep/mcguffey-graded-corpus`. Runner: local CPU.
Parent result being SCOPED (not refuted): `data/exp_hub_spoke_word_representation_v1/metrics.json`.

> **PROVENANCE HONESTY, stated up front so it is not discovered later.** This file is written
> before the cell is run but is NOT git-witnessed at the moment of writing (the repository has a
> large uncommitted working tree and this agent does not push). The ordering rests on this file's
> mtime and on the report that cites it, which is strictly weaker than a commit. Same defect the
> parent cell disclosed for itself.

---

## 0. THE QUESTION, IN PLAIN LANGUAGE

Our hub-and-spoke word vector can be asked for one of its parts and gives the right part back
every single time -- facet recovery **1.000** against an unaddressed sum at **0.2483** (chance
0.25), measured at full scale, `data/exp_hub_spoke_word_representation_v1/metrics.json`.

**But that number was measured with the EXACT key the facet was stored under.** A sibling result
landed the same day (`c33e6d338`) showed that exact-key measurements are exactly the regime that
flatters addressing, and that the same structure loses when the cue is a never-seen, partly
overlapping one: conjunctive addressing went from 1.000 in isolation to CI-separated BELOW the
flat bag on the real read-out, and failed its own known-answer gate (0.6823 / 0.6990 / 0.6622
against a 0.70 floor, base 0.7860).

So the question here is one question: **does hub-and-spoke addressing hold up when the cue is
only partly right, or does it collapse the way conjunction did?**

If it collapses, the parent cell's headline is an artefact of the query model and must be
re-scoped tonight. If it holds, then per-spoke ROLE keys behave differently from CONJUNCTIVE
keys, and that difference is a real, separating fact about which kind of structure is worth
building on.

---

## 1. BRAIN FIDELITY (standing requirement, PLAN R13, enforced at `3e70c3ba4`)

Stated per component, and the invention is labelled as invention.

| component | (a) BRAIN STRUCTURE (a neural system, not a cognitive label) | (b) REUSE or parallel build | (c) pinned vs ours |
|---|---|---|---|
| the word code under test | **anterior temporal lobe hub + modality spokes** in sensory and motor cortex; word FORM in the **visual word form area** | REUSE `hdlab/hub_spoke_word.py` (owned) and `experiments/exp_hub_spoke_word_representation_v1.py::build_arm` (owned). Nothing rebuilt. | that form and meaning are separate systems with their own addresses, tied by a hub, evidenced by the double dissociation: **PINNED-BY-EVIDENCE**. That "ask for one facet" is unbind-by-role-key: **OUR-INVENTION-BEING-TESTED** |
| the partial cue itself | **hippocampal CA3 recurrent collaterals** -- the completer. The brain does not retrieve with an exact key; it completes a whole pattern from a fragment. CA3 is paired with **dentate gyrus** separation; the two are a matched pair | **NO COMPLETER IS BUILT HERE.** This cell does NOT add CA3. It measures how the code behaves under a partial cue **with no completer in front of it**, which is the honest description of the current substrate | that CA3 completes from a partial cue and DG separates: **PINNED-BY-EVIDENCE**. That "partial cue" is operationalised as *a fraction of the cue's dimensions carry a different item's value*: **OUR-INVENTION-BEING-TESTED**, and it is an operationalisation, not a brain fact |
| the conjunctive comparison operator | **perirhinal cortex** feature-conjunction coding (and the account has real failed replications -- **CONTESTED**, not pinned) | REUSE `hdlab/perirhinal_conjunctive.py` (owned, currently SHELVED). Imported, never edited. Its `pair_conjunction` is called and my batched form is asserted bit-identical to it | the elementwise-product conjunction operator is **OUR-INVENTION-BEING-TESTED**; nothing in the literature specifies it |

**(d) Shelve / revival criterion, in BRAIN terms, declared before the result.** If hub-and-spoke
addressing collapses under a partial cue, the correct conclusion is **NOT** "role binding does not
work". It is that **we have built separators without a completer**, which is anatomically
incomplete: DG and CA3 are a matched pair and we own only the separating half. The revival
criterion is therefore **"re-test once a pattern-completion stage (CA3-shaped: recurrent
settling from a fragment to a stored whole) sits in front of the read-out"** -- not "re-test if
the number improves". This is the exact framing error that PLAN R13 was written to prevent, where
`hdlab/perirhinal_conjunctive.py` was shelved on "exact-key retrieval only" and thereby hid the
missing organ.

**Note a live tension in our own documents, recorded rather than resolved:** `notes/PLAN.md` line
251 carries an **explicit negative recommendation against building CA3 pattern completion**
(three cells floor it: +0.005, +0.003, one HARD_FAIL at -0.020), while R13 (line 780) says
conjunction is not testable until completion sits in front of it. This cell does not adjudicate
that; it supplies the missing measurement -- how far the code degrades before a completer would
have to do any work.

---

## 2. WHAT IS REUSED (enumerated from disk, then reconciled)

Enumeration: `ls hdlab/*.py` and `ls experiments/exp_hub_spoke*` read in full; the parent cell's
own REUSED-NOT-REBUILT list (`.claude/scan-out/wall1-hubspoke-word.json`) taken as the starting
inventory and each entry re-opened.

| reused | what it gives | how the reuse is PROVEN |
|---|---|---|
| `experiments/exp_hub_spoke_word_representation_v1.py` | `build_arm`, `shared`, `spoke_codes`, `facet_recovery`, `boot_mean`, `boot_diff`, `derangement`, and every config constant | imported as a module, **never edited**. Gate PV3 asserts my partial-cue read-out at overlap 1.00 is **bit-identical** to its unmodified `facet_recovery` |
| `hdlab/hub_spoke_word.py` | the codec, the keys, bind/unbind | imported, never edited |
| `hdlab/perirhinal_conjunctive.py` | `pair_conjunction`, the conjunctive operator | imported, **never edited** (a sibling agent owns it). Gate PV6 asserts my batched form is bit-identical to it row by row |
| `experiments/exp_encoding_quality_instrument_v2.py` | THE RULER: `_l2n`, `_hash_seed`, `build_vocab`, tiebreak convention | imported, never edited; tracked-and-clean asserted at HEAD |
| `experiments/exp_meaning_asset_fair_test_v1.py` | `N_BOOT`, `BOOT_SEED` | imported, never edited |
| `experiments/_seed_checkpoint.py` (fixed `ee7c42c0f`), `tools/exp_checkpoint.py` | output dir, atomic metrics, per-unit resume | not edited; the config-blind `unit_key` defect neutralised by a sha256 config fingerprint in every key |

**Built new: nothing durable.** This cell adds no `hdlab/` module. It is a measurement of code we
already own under a query model we had not tried.

---

## 3. CONFIG (inherited; nothing re-tuned by this cell)

Vocabulary, corpus, byte budget, dimensionalities and seeds are taken from the parent cell at
import time, which takes them from the ruler.

| | smoke | full |
|---|---|---|
| `V` | 512 | 4096 |
| `D_SWEEP` | [256] | [1024, 256] |
| `SEEDS` | [7] | [7, 17, 23] |
| `N_PROBE` (identification queries) | 256 | 1024 |
| store size for identification | all `V` words | all `V` words |
| `N_BOOT` | 2,000 | 10,000 |

`OVERLAPS = [1.00, 0.80, 0.50, 0.20, 0.00]`. The last is the **no-overlap control** and must land
at chance for every arm.

**The cue model, defined once and applied identically to every channel** (this is the one design
choice that decides what the numbers mean, so it is stated before the run):

> A cue at overlap `f` keeps a random fraction `f` of the cue vector's dimensions and fills the
> remaining `1-f` with **the corresponding dimensions of a different item's** vector.

That is the direct analogue of the sibling's context model, where a 20%-overlap cue was 2 of 10
context words shared and the other 8 replaced by different words. It is channel-agnostic, so
graded and bipolar arms are degraded on the same axis. At `f = 0` the cue is a different item's
vector and carries nothing. `f` is a nominal parameter; **the MEASURED cue cosine is reported
beside every point and is the number to read**, because a nominal parameter is not a cosine (the
parent cell already had to publish that correction once).

---

## 4. TWO CURVES, REPORTED SEPARATELY AND NEVER AVERAGED

They ask different questions and one can pass while the other fails.

**CURVE-A -- the ADDRESS axis: is the address still readable when the KEY is only partly right?**
Facet recovery exactly as the parent cell measures it -- unbind the single word vector, argmax
cosine against the word's OWN spoke codes, chance `1/F` -- except that the key presented is
degraded to overlap `f`. Arms: `HS4_GRADED`, `HS4_SIGNED`, `HS2_GRADED`, `HS5_EXTENDED`,
`N_NULLCONTENT`, `FLAT_SUM`, and floors `F_ORTHO`, `F_FREQ`, `F_SCRAMBLE`.

**CURVE-B -- the GENERALISATION axis: can a never-seen, partly-overlapping encounter with a word
find that word again?** The store holds one vector per word built from its stored spoke codes.
The query is a NEW encounter whose spoke codes overlap the stored ones at `f`, each spoke degraded
independently (a new occasion measures each facet afresh -- **OUR-INVENTION-BEING-TESTED**, not a
brain fact). Top-1 over the whole `V`-word store, chance `1/V`; median rank and top-50 recall also
reported, because those are the statistics the sibling result is reported in and a comparison
across differently-reported statistics is how a claim gets mis-carried.

CURVE-B operators, one variable = **how the facets are combined**, with content, words, cue model,
store, scorer and probe set held identical:

| operator | construction | role |
|---|---|---|
| `ADDRESSED` | `HubSpokeWord.bundle` -- bind each spoke to its role key, then sum | **THE MEASUREMENT** |
| `ADDRESSED_SIGNED` | the same with the terminal `sign()` | the production shape |
| `FLAT` | the same spoke codes summed with NO binding | the incumbent, and the reference the sibling's conjunctive arms lost to |
| `CONJUNCTIVE` | `P = (S*S - F)/2` over the same spoke codes, `S` = the flat sum -- the owned perirhinal operator | **POSITIVE CONTROL: the operator already known to collapse.** If it does NOT collapse here, this instrument cannot detect a collapse and CURVE-B publishes no scientific number |
| `SLOTTED` | the spoke codes concatenated, no superposition at all | **KNOWN-ANSWER ceiling** |
| `F_ORTHO_ONLY` | the FORM spoke alone, degraded identically | standalone spelling floor |
| `F_FREQ_ONLY` | the frequency lift alone, degraded identically | standalone frequency floor |
| `F_SCRAMBLE` | `ADDRESSED` with the meaning spokes' rows permuted across words | scramble floor |

Floors are **standalone channels**, never a shortcut bolted onto the system under test.

---

## 5. PRE-REGISTERED THRESHOLDS

### 5a. INSTRUMENT-VALIDITY GATES -- all must pass, or `PARTIAL_CUE_INSTRUMENT_LOOSE` and no scientific number is published

| id | condition | why it can fail |
|---|---|---|
| PV1 | at `f = 1.00`, EVERY CURVE-B operator identifies its own item at `>= 0.99` | this is the known-answer arm the sibling's conjunctive arms failed. An operator that cannot find an item from the item itself publishes no curve |
| PV2 | at `f = 0.00`, EVERY CURVE-B operator is at `<= max(0.01, 10/V)` | a no-overlap cue that still retrieves means the cue model leaks |
| PV3 | at `f = 1.00`, CURVE-A facet recovery is **bit-identical** to the parent cell's unmodified `facet_recovery` for `HS4_GRADED`, `FLAT_SUM` and `N_NULLCONTENT` | proves the curve is an extension of the published measure, not a re-implementation of it |
| PV4 | measured `cos(cue, true)` is monotone in `f` and within 0.05 of `f` at every point | proves the x-axis is what it is labelled |
| PV5 | `FLAT_SUM` CURVE-A facet recovery stays within chance +- 0.05 at EVERY `f` | no address means no sensitivity to the key at all -- if it moves, the read-out is leaking through something other than the address |
| PV6 | the batched conjunction is bit-identical to `hdlab/perirhinal_conjunctive.pair_conjunction`, and to an explicit `O(F^2)` double loop | reuse proven, not claimed |
| PV7 | every arm's vectors differ from every other arm's | a silent alias makes every comparison vacuous |
| PV8 | no external-LLM module anywhere in `sys.modules` | project invariant, asserted at runtime |

### 5b. SCIENTIFIC GATES -- evaluated only if every PV gate passes

**P1 -- THE ADDRESS SURVIVES A PARTIAL CUE.** At every `f >= 0.20`, `HS4_GRADED` facet-recovery
95% CI **lower** bound exceeds the CI **upper** bound of `max(F_ORTHO, F_FREQ, F_SCRAMBLE)`
measured at the SAME `f` on the identical scorer, n, pool and gold.

> *Declared before the run, so a pass cannot be over-read:* `F_SCRAMBLE` scores **1.000** on the
> facet axis at full scale, because scrambling which word owns which meaning does not touch
> addressing. It is a floor for the MEANING axis and **not** for the facet axis. Including it makes
> P1 essentially impossible to pass, and that is the same defect that makes the parent cell's G1
> fail as written. **The threshold is NOT changed to dodge this.** P1 is reported as written, AND a
> clearly-labelled second row `P1_MEANINGFUL_FLOORS` restricted to `max(F_ORTHO, F_FREQ)` is
> reported beside it. Both rows, never averaged, never one substituted for the other.

**P2 -- HUB-AND-SPOKE DOES NOT INHERIT THE CONJUNCTIVE COLLAPSE.** Two conditions, both required,
paired bootstrap over the identical probe words:
  - (i) **positive control:** at `f = 0.20`, `CONJUNCTIVE` identification is CI-separated BELOW
    `FLAT`. If this fails, the instrument has no discriminating power at this overlap and P2
    publishes no number.
  - (ii) **the claim:** at `f = 0.20`, `ADDRESSED` identification is NOT CI-separated below `FLAT`.

**P3 -- reported, not gated.** The full decay shape for every operator: measured cue cosine, top-1,
median rank, top-50 recall at each `f`.

### 5c. PRE-DECLARED EXPECTATION, so neither outcome can be spun

I expect `ADDRESSED` to track `FLAT` closely and `CONJUNCTIVE` to collapse superlinearly, because
bipolar bind is an **isometry** and the addressed bundle is a **linear** function of the spoke
codes, whereas the conjunction is **quadratic** in them. **If that is what happens it is a WEAK,
LARGELY ALGEBRAIC result and must be labelled one** -- a construction proof about the operator, not
a capability win, and specifically not evidence that hub-and-spoke helps any downstream task.

The part that is genuinely not predictable from the algebra: addressing **suppresses cross-spoke
crosstalk** (the cross terms `k_s . k_t` randomise), while the flat sum keeps it. Our real spoke
codes are **correlated, not near-orthogonal** -- at `V = 512` the `CONCRETE` spoke has only 111
distinct codes across the vocabulary. Whether suppressing that crosstalk helps or hurts at partial
overlap is an empirical question, and it is where this cell can genuinely surprise.

### 5d. STOP-IF

- Any PV gate fails -> `PARTIAL_CUE_INSTRUMENT_LOOSE`, no scientific number, stop.
- `ADDRESSED` CI-separated below `FLAT` at any `f <= 0.50` -> verdict
  `ADDRESSING_COLLAPSES_UNDER_PARTIAL_CUE`. That is the **headline**, reported first and plainly,
  never inside a gate table -- it would mean the parent cell's 1.000 is an exact-key artefact.
- `CONJUNCTIVE` failing to collapse -> say the instrument cannot detect a collapse and publish no
  P2 number. Do not reinterpret.
- No tuning pass after seeing any number. No default flipped.

---

## 6. WHAT THIS CELL DOES NOT MEASURE (declared before the run)

- **No meaning claim.** Both curves score synthetic and norm-derived spoke codes for
  self-identification and facet addressing. Neither is a meaning measurement. This remains a
  **CONSTRUCTION PROOF**.
- **No downstream number.** No store beyond a one-vector-per-word table, no reading loop, no
  open-vocabulary hit@1. Whether any of this moves the 4.80% read-out is NOT measured and cannot
  be inferred.
- **No completer.** CA3 pattern completion is not built and not simulated. A result here is
  "how the code behaves with no completer", which is the current substrate, not the brain.
- **No claim about the sibling's task.** The sibling measured naming from a never-seen sentence;
  this measures item identification from a degraded facet cue. They are different tasks on
  different objects and the numbers are **not interchangeable**. Only the SHAPE of the degradation
  is compared, and that comparison is labelled structural, not numeric.
- **No external LLM**, at build time or inference. Sources are a character n-gram encoder and two
  published human-rating norm sets.

---

## 8. AMENDMENTS -- made BEFORE any data run, found by this cell's OWN self-test

**A1 (2026-08-16) -- `F_FREQ_ONLY` is removed from CURVE-B because it fails the PV1 known-answer
gate.**

*Found by:* self-test `ST_PV1`, **before any data run**, on the first pre-flight execution. The
run aborted rather than proceeding.

*Measured:* `F_FREQ_ONLY` identifies its own item **from the item itself** at **0.5938** (and
0.6406 on a second probe draw) against the PV1 threshold of 0.99.

*Why:* a frequency lift cannot distinguish two words that share a frequency band. This is a
property of the CHANNEL, knowable a priori, and I should have caught it when designing the arm
rather than discovering it at pre-flight.

*What was done, and what was deliberately NOT done:* the channel is **removed from CURVE-B**, so
PV1 keeps reading "EVERY CURVE-B operator" with **no carve-out inside the gate**. I did not add
an exception clause to PV1, because a gate with an exception for the arm that failed it is not a
gate. `F_FREQ` is **retained on CURVE-A**, where it is evaluable and sits at chance as a floor
should. The measured number is **recorded in the metrics** at
`selftest.ST_A1_excluded_channel_self_identification`, not dropped.

*Direction:* **LOOSENS**, and it is stated as loosening rather than dressed up. It removes one
channel from the CURVE-B floor set. The remaining CURVE-B floors are `F_ORTHO_ONLY` -- which is
the historically strongest floor in this project, the one the live read-out loses to -- and
`F_SCRAMBLE`. **No threshold in section 5 was changed.**

**A2 (2026-08-16) -- a real construction bug caught by `ST_PV7`, before any data run.** The
self-test built the `F_SCRAMBLE` arm without applying its permutation, so it collided
bit-for-bit with `ADDRESSED` (identical sha256 digest). Arm construction is now a single
function, `arm_codes()`, used by the measurement path and the self-test path alike, so the
scramble arm cannot be built without its scramble. *Direction:* **TIGHTENS** -- it makes a
degenerate floor impossible rather than merely detected. No threshold changed.

---

## 7. HAZARDS HONOURED

`data/foundation/**` never opened. No `git add -A`; explicit path list at commit. No origin push.
`hdlab/hd_fact_store.py`, `hdlab/reading_grounding_loop.py`, `hdlab/perirhinal_conjunctive.py`,
`tools/status_gui.py`, `tools/status_state.py`, `tools/dispatch_batch.py`,
`data/capability_registry.jsonl`, `CLAUDE.md`,
`data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` and
`data/exp_structured_comparator_v1/probes/` are never written. No deletion is bundled with any
run. `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` pinned at the top of the .py before numpy is
imported, never as a shell prefix. ASCII only. `sorted(set())` discipline for every iteration
order. Per-unit checkpoint/resume per CLAUDE.md.
