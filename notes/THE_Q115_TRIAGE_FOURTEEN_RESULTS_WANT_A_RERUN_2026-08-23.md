<!-- SECOND CORRECTION 2026-08-23 -- THE QUESTION ITSELF WAS SLIGHTLY WRONG. READ THIS FIRST. -->
> # 🔻 **RE-RUNNING IS NOT THE FIX FOR MOST OF THESE. THEY DO NOT NEED A RE-RUN, THEY NEED A FLOOR.**
>
> I built this list by asking *"which un-rerunnable results want a re-run"*. **Running the first one
> exposed the flaw in the question: a re-run verifies the ARITHMETIC, not the ARGUMENT.** That cell
> reproduced to `132` of `132` fields and was still a `HARD_PASS` at `1.000` on `n=10`.
>
> **A RESULT WITH NO FLOOR WILL RE-RUN AND STILL HAVE NO FLOOR.** For every row selected *because it
> lacks a floor*, the useful action is **run the floor**, not re-run the cell. Those are different
> jobs with different costs, and I had merged them.
>
> ## 📖 THEN I READ WHAT CITES THE REMAINING 14, AS THIS NOTE ALREADY TOLD THE READER TO DO
> The citing documents were again more accurate than my key-regex, and they SPLIT the list:
>
> | disposition | rows | why |
> |---|---|---|
> | ✅ **HAS controls already** | `encoder_alltype_transfer_v1` (shortcut controls `global_last` `0.007-0.011`, `most_frequent` `0.057-0.070`), `encoder_alltype_transfer_stress_v1` (independent entity-file harness) | **come off the list** |
> | 🔻 **ALREADY SUPERSEDED / MISLABELLED -- a re-run proves nothing** | `encoder_retrain_persist_v1` (*"a measurement of a third, FAILED artifact"*, and *"the confound-removed cell REVERSES THE SIGN"*), `propara_schema_learned_grounded_binder_v1` (*"HARD_PASS, but msg is only SELFTEST_PASS"*), `kb_coarse_grain_at_promotion_v1` (*"task description references v2 which doesn't exist"*), `stated_entity_fate_..._highprecision` (verdict-field conflict; floor run separately today) | **come off the list** |
> | 🎯 **CONFIRMED NO FLOOR, AND LOAD-BEARING** | **`exp_hd_fact_store_source_trust_vet_v1`** | ORGAN_MAP, verbatim: *"reports **1.000/1.000/1.000, verdict PASS, no floor**"* and *"**BLOCKS:** every claim that rests on 'the foundation knows N things'"* |
> | ❓ uncited in any caveated context | `exp_kb_time_decay_eviction_with_reingest_v1`, `substrate_director_kb_ingest_v1` | check by hand before spending |
>
> ➡️ **THE ONE TO ACT ON IS `exp_hd_fact_store_source_trust_vet_v1`, AND THE ACTION IS A FLOOR, NOT A
> RE-RUN.** A `PASS` at `1.000/1.000/1.000` with no floor, which the organ map says blocks every
> claim resting on how much the foundation knows. *`1.000` on three metrics is exactly the shape that
> a trivial baseline usually also achieves.*
>
> ⚠️ **THE COUNT WAS NEVER THE DELIVERABLE.** `275` -> `20` -> `14` -> **one row worth acting on and a
> corrected question.** Each step came from looking at the actual rows rather than re-running a
> query. *Recorded in full below, including the two detector errors, because the sequence is the
> useful part.*

<!-- CORRECTION 2026-08-23, SAME DAY, AFTER RUNNING THE FIRST ONE -- READ THIS FIRST -->
> # 🔻 **THE LIST IS `14`, NOT `20` -- AND THE FIRST RE-RUN IS WHAT FOUND THAT**
>
> I re-ran the cheapest row (`exp_read_coref_hobbs_centering_resolver_v1`, 0.5s) to prove the loop.
> **It reproduced exactly: `132` of `132` numeric fields identical, verdict `HARD_PASS` both times,
> and the landed record byte-identical with its mtime unchanged** (fresh run went to a sibling).
>
> **THEN I READ WHAT CITES IT, AND MY DETECTOR WAS WRONG ABOUT IT.** `ORGAN_MAP.md` describes it as
> *"HARD_PASS at 1.000 — on n=10, **with floors FULL-vs-OFF (10 vs 0) and NOGATE precision 0.949**"*.
> It HAS floors. My regex looked for `floor|null|baseline|shuffl|scrambl|permut` in key names and
> matched neither `metric_c_foundation_precision_nogate` nor `..._resolver_off`.
>
> **RE-SCORED WITH A WIDER PATTERN (adding `_off`, `nogate`, `random`, `control`, `ablat`, `twin`,
> `chance`): 6 of the 20 have a floor I missed** -- `cortex_integration_end_to_end_v1`/`v2`
> (ablation arms), `cortex_integration_with_noise_channel_v1` (noise-off), `hd_fact_store_capacity_and_index_v1`
> (positive control), `learned_codebook_generalization_gate_v1` (random-pair baseline), and the coref
> cell itself. **➡️ THE RE-RUN LIST IS `14`.**
>
> ⚠️ **AND IT MAY STILL BE AN OVER-COUNT.** A floor can be named anything, or live in another cell --
> `stated_entity_fate` is on the list and its floor was run separately today. **Check the citing
> documents before spending compute on any row; they are more reliable than my key regex.**
>
> ## 🧠 WHAT THE FIRST RE-RUN ACTUALLY TAUGHT, WHICH IS NOT ABOUT THE COUNT
> **A GENUINE REPRODUCTION VERIFIES THE ARITHMETIC, NOT THE ARGUMENT.** That cell reproduces to 132
> fields and is still a `HARD_PASS` at `1.000` **on `n=10`**. Re-running it changed nothing about how
> much it supports. *And its own record is scrupulous: `metric_c_precision_delta_on_minus_off = 0.0`
> -- the author measured that the resolver adds ZERO precision and wrote the zero down. The gain is
> COVERAGE (`10` bound vs `0`), which the verdict states.* **Both citing documents already lead with
> the `n=10` caveat.** *This row was well handled by everyone except my detector.*

# THE Q115 TRIAGE: 4,908 LANDED RESULTS, AND **14** OF THEM WANT A RE-RUN

*(Titled `20` when first written. The first re-run showed 6 of those 20 DO carry floors my
key-regex missed -- see the correction block above. The funnel below is unchanged and
correct down to the `29`; the last row is what moved.)*

**2026-08-23, strategy session.** The owner's answer to Q115 had two halves. The first -- require the
shared save-location helper for new experiments -- shipped as a pre-commit gate. **This is the
second half, in the owner's words:**

> *"I'd go back through the 275 older ones one at a time -- we need to know what those are and how
> they turned out. You can decide whether each one wants a rerun 1 by 1 and I think you'll be able to
> do it pretty quickly."*

---

## 1. THE FUNNEL, EACH STEP WITH ITS DENOMINATOR

| step | count | share |
|---|---|---|
| landed results (`data/*/metrics.json`, paired to a cell) | **4,908** | -- |
| of those, can be **genuinely re-run** today | 3,495 | **71.2%** |
| 🔻 would only **replay a saved answer** | **1,413** | 28.8% |
| of the replayers, **assert a result** (HARD_PASS / PASS / HOLD / CONFIRMED) | **425** | 8.7% of all |
| of those, **cited by a doc that steers work** (plan / STATUS / organ map / registry) | **135** | 2.8% of all |
| of those, carry **NEITHER a floor NOR an interval** | **29** | 0.6% of all |
| of those, **claim a capability** (not `SELFTEST` / `PENDING`) | 20 | 0.4% of all |
| 🎯 of those, **still lack a floor once floor-shaped keys are counted properly** | **14** | **0.3% of all** |

**THE NUMBER THE OWNER WAS GIVEN -- `275` -- WAS WRONG, AND WRONG IN OUR FAVOUR.** It came from a
count that matched a variable NAME rather than a call. *Re-measured with an AST walk and a
positive control that the redirect really fires in a fresh process.*

---

## 2. THE LIST, AND WHY THESE

🔻 **SIX OF THE TWENTY BELOW ARE STRUCK -- they have floors under key names my regex missed**
(`ablated`, `noise_off`, `nogate`, `resolver_off`, `control`, `mean_cos_random`):
`cortex_integration_end_to_end_v1`, `..._v2`, `cortex_integration_with_noise_channel_v1`,
`hd_fact_store_capacity_and_index_v1`, `learned_codebook_generalization_gate_v1`,
`read_coref_hobbs_centering_resolver_v1`. **The remaining 14 are the list.**

**Each is: cited by something that steers work + asserts a capability + cannot be re-run + carries
neither a floor nor an interval in its own record.** Nothing else holds them up.

```
exp_cortex_integration_end_to_end_v1                 exp_learned_codebook_generalization_gate_v1
exp_cortex_integration_end_to_end_v2                 exp_propara_process_keyed_lookup_v1
exp_cortex_integration_with_noise_channel_v1         exp_propara_schema_learned_grounded_binder_v1
exp_encoder_alltype_transfer_stress_v1               exp_read_coref_hobbs_centering_resolver_v1
exp_encoder_alltype_transfer_v1                      exp_stage2_int2_binary_pareto_at_cliff_v2 (x3)
exp_encoder_retrain_persist_v1                       exp_stated_entity_fate_reading_extractor_v2_highprecision
exp_exp_kb_time_decay_eviction_with_reingest_v1      exp_substrate_director_kb_bio_trio_ingest_v1
exp_hd_fact_store_capacity_and_index_v1              exp_substrate_director_kb_ingest_v1
exp_hd_fact_store_source_trust_vet_v1
exp_kb_coarse_grain_at_promotion_v1
```

**THE OTHER 9 OF THE 29 SAY SO THEMSELVES** -- `SELFTEST_PASS`, `STRUCTURAL_PASS_PENDING_B3`,
`STRUCTURAL_PASS_PENDING_HANDSCORE`. **A provisional verdict is not an over-claim, and re-running one
as if it were a capability result would be the mistake.**

---

## 3. TWO HONEST LIMITS ON THIS LIST

- 🔻 **A FLOOR RUN IN A DIFFERENT CELL DOES NOT COUNT HERE, AND ONE ROW PROVES IT.**
  `exp_stated_entity_fate_reading_extractor_v2_highprecision` is on the list, but its trivial floor
  **was run** -- in a separate cell (`exp_grow_by_reading_trivial_floor_v1`), by a solver, today. The
  detector reads each cell's OWN `metrics.json`, so **the 20 is an upper bound**; some will already
  have evidence elsewhere. *Check before re-running, not after.*
- ⚠️ **"CITED" IS A SUBSTRING MATCH OF THE DIRECTORY NAME** in five steering documents. It is
  positive-controlled (a known-cited cell is found, an invented name is not) but it will miss a
  result referred to by a description rather than by its name.

---

## 4. THE MEASUREMENT MISTAKE I MADE GETTING HERE, BECAUSE IT NEARLY SET THE PRIORITIES

My first pass scored the evidence by searching the whole JSON **as text** for `null`, `confidence`
and `ci_`. It reported **39% of the 135 carry both a CI and a null** -- which contradicts the
standing audit's *"99.5% of HARD_PASS carry neither"*.

**The contradiction was the tell.** `"key": null` is a JSON literal, not a null hypothesis. Sampling
400 files: **24 contain a JSON `null`, and only 5 have a KEY naming a null, shuffle or permutation.**
The real rate is ~1%, not 30%.

**Scored on KEY NAMES instead, the 135 read: `FLOOR only` 90, `NEITHER` 29, `CI+FLOOR` 15,
`CI only` 1.** *Same error class as the coverage figure this triage corrects -- matching text where
structure was needed. Third time today.*

---

## TLDR

You asked me to go back through the un-recheckable experiments one at a time and decide which want
re-running. There were fewer than we thought, and the ones that matter are fewer still.

Of about **4,900** stored results, roughly **three quarters can already be re-checked properly** --
the "275 can't" figure was wrong, and wrong in our favour. Of the rest, most either don't claim
anything or aren't referred to by any document that guides our work.

**That leaves 14.** *(I first wrote 20; running the cheapest one showed six of them already had a baseline recorded under a name my search did not recognise.)* Each one claims something, is quoted somewhere that steers what we do, cannot be
re-run, and has nothing else propping it up -- no comparison against a dumb baseline, no error bars.
Those are the ones worth the compute.

Nine more looked equally bare until I read their verdicts: they say *"self-test"* or *"pending"*
about themselves. Being honest about being provisional is not the same fault, and re-running them as
if they were finished results would be my error, not theirs.

One caution: at least one of the 20 has already been checked properly, just in a different file. So
**20 is a ceiling, not a target** — look before you spend.

## QUESTIONS

None. `Q116` remains open.

## NEXT STEPS

1. **The 20 are the re-run list.** They are ordinary cells; each needs `HDI_FRESH_RUN` and a look at
   whether a floor already exists elsewhere first.
2. `tools/reproducibility_inventory.py` regenerates the whole funnel; the per-cell table is at
   `data/triage_135_cited_unverifiable.tsv`.
3. *The `1,413` un-rerunnable results are not growing: new cells are gated at commit.*
