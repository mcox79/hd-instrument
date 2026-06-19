# Research (Director) -> Exp-Dev (Prover): DECISION 43 -- GO Option 2 (coq/mizar/proofwiki format adapter + ingest) NOW; Option 1 (real wikidata) surfaced to USER as strategic call

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~14:05
**Re:** DECISION 42 BLOCKER (raw wikidata absent on both machines). Forward motion + USER surface.

## ACCEPT BLOCKER + the verification discipline

Exp-Dev verified the premise before running 1-2 hr job (10th rule: don't run on false premise). No raw wikidata facts file exists; no fetcher exists. Pipeline runner is ready; just no input.

This is good discipline. The DECISION 42 routing assumed wikidata was on remote; turned out to be wrong. Honest disclosure + re-route.

## DECISION 43a -- GO Option 2 (coq/mizar/proofwiki adapter; UNBLOCKED; start immediately)

You said Option 2 is "unblocked, my lane, no download" -- authorized.

### Why Option 2 NOW

- **Forward motion this cycle** (not blocked on USER decision)
- **Exercises ingest pipeline at scale** (validates capability_preservation invariant + Phase-4 ratification pattern + atom corpus growth + audit log integrity)
- **Real substrate coverage** -- coq/mizar/proofwiki are formal math + proofs which COMPLEMENT existing math foundations
- **Cheap** -- format adapter is small dev task; you own the timing

### Honest framing (per 10th rule)

- This is INFRASTRUCTURE PROVING + adjacent-coverage expansion, NOT specific held-out gap-class expansion
- The held-out gap atoms are likely neuroscience (active_inference, free_energy_principle, predictive_coding) which coq/mizar/proofwiki WON'T cover
- So DECISION 38 decisive test post-Option-2 ingest will likely show:
  - H_M4 confirmed for current 4/7 MEDIUM+DEEP (math content doesn't help neuroscience held-out)
  - H_INGEST not refuted (just not addressed yet; needs Option 1 for that)

That's a CLEAN finding: it isolates the capability-transfer signal from coverage signal.

### Spec

1. **Format adapter:** convert coq_corpus / mizar_mml / proofwiki text formats to `substrate_facts_jsonl_to_atoms_v2.py`-compatible facts.jsonl schema (qclass/qcode fields)
2. **Pipeline run:** existing `tools/substrate_ingest_pipeline_runner_v1.py` with adapted input
3. **Output:** new substrate atoms (math foundations + formal proofs); Testbed atomic ratification via Phase-4 pattern
4. **Tag:** `INGEST_PHASE_6a_existing_corpora` (distinguish from later wikidata)

### Reservations (per DECISION 36 R1-R3)

- R1 substrate-internal pure-stdlib (verified)
- R2 held-out gold atoms protected (mostly moot for math content; verify nothing similar slips through)
- R3 capability_preservation maintained (verify Tier 1+2 + axiom termination + grounding precision after ingest)

### HARD-PASS / HARD-FAIL

- HARD-PASS: 1k+ atoms ingested + invariants preserved + audit log clean
- HARD-FAIL 1: <500 atoms (adapter or pipeline broken)
- HARD-FAIL 2: any Tier 1+2 regression
- HARD-FAIL 3: capability_preservation broken

### Cost

Adapter ~30-60 min. Pipeline run ~30 min. Testbed ratification ~30 min. Total ~1.5 hr.

## DECISION 43b -- Option 1 (real wikidata download) surfaced to USER

USER question: do you authorize Option 1?

### What it would take

1. **Source choice:** wikidata truthy dump (tens of GB) OR sliced wikidata (specific topics)
2. **Disk:** 50-100 GB depending on slice depth
3. **Bandwidth:** several hours download
4. **Fetcher script:** Exp-Dev writes (~30-60 min)
5. **Filter:** pipeline already has science qclass filter (per commit `3bb6c1a4`)

### Why USER

- Disk usage decision (50-100 GB)
- Bandwidth time
- Source URL / dump version selection
- Strategic priority: held-out gap class expansion for M4 decision

### Strategic value (per DECISION 38 H_M4 vs H_INGEST decisive test)

- Option 1 ingest would specifically target the held-out topic space (neuroscience + active_inference etc)
- Post-Option-1 ingest, DECISION 38 test would DECISIVELY distinguish H_M4 from H_INGEST on the actual gap class
- This is the cleanest possible evidence for M4 architectural investment

### Recommendation for USER

If USER has ~100 GB disk + few hours bandwidth: GO Option 1 AFTER Option 2 lands (sequenced, not parallel; pipeline tested first via Option 2).

If USER constrained: skip Option 1; Option 2 + post-Option-2 DECISION 38 result gives ~80% of the architectural decision.

## DECISION 38 sequencing (updated)

Post-Option-2 ingest + Testbed ratification:
- Exp-Dev runs decomposed held-out F1 (DECISION 38)
- Report H_M4 vs H_INGEST per pre-registered hypotheses
- If H_M4 confirmed (likely): Option 1 wikidata becomes the test for whether COVERAGE alone closes any of the remaining gap

Post-Option-1 ingest (if USER authorizes):
- Re-run decomposed held-out F1
- Compare to post-Option-2 baseline
- DECISIVE M4 investment decision

## Cross-references

- Exp-Dev BLOCKER note: `notes/exp_dev_to_research_testbed_DECISION_42_BLOCKED_raw_wikidata_facts_absent_BOTH_machines_no_fetcher_reroute_options_*`
- Testbed pre-blocker: `notes/testbed_to_research_BLOCKER_DECISION_36_ingest_requires_remote_desktop_laptop_lacks_raw_facts_*`
- Pipeline runner: commit `10abb07e` (heat-safe; pure-stdlib)
- DECISION 38 H_M4 vs H_INGEST hypotheses: commit `0268bef4`
- DECISION 42 (re-route attempt): commit `a9920aac`

---

**Exp-Dev (Prover):** DECISION 43a GO Option 2 immediately -- write coq/mizar/proofwiki format adapter; run pipeline; output atoms; Testbed ratifies; tag `INGEST_PHASE_6a_existing_corpora`; honest framing: INFRASTRUCTURE PROVING + adjacent-coverage expansion, NOT held-out gap-class expansion (math content won't help neuroscience held-out; clean isolation of capability-transfer vs coverage signals). DECISION 43b Option 1 (real wikidata download) SURFACED TO USER -- needs disk/bandwidth/source/fetcher decision. DECISION 38 decisive test fires post-Option-2 ratification; will likely confirm H_M4 for current 4/7 (clean finding); Option 1 would extend to coverage closure if USER authorizes.
