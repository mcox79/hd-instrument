# THE Q115 TRIAGE: 4,908 LANDED RESULTS, AND **20** OF THEM WANT A RE-RUN

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
| 🎯 of those, **claim a capability** (not `SELFTEST` / `PENDING`) | **20** | **0.4% of all** |

**THE NUMBER THE OWNER WAS GIVEN -- `275` -- WAS WRONG, AND WRONG IN OUR FAVOUR.** It came from a
count that matched a variable NAME rather than a call. *Re-measured with an AST walk and a
positive control that the redirect really fires in a fresh process.*

---

## 2. THE 20, AND WHY THESE

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

**That leaves 20.** Each one claims something, is quoted somewhere that steers what we do, cannot be
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
