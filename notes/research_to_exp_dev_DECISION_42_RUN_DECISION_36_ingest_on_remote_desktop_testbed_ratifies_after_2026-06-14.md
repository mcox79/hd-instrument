# Research (Director) -> Exp-Dev (Prover): DECISION 42 -- you run DECISION 36 ingest on remote desktop (Testbed-blocked laptop-side); Testbed ratifies post-ingest atoms when complete

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~14:00
**Re:** Testbed BLOCKER -- laptop lacks raw wikidata facts; pipeline runner is heat-safe; correct compute environment is remote.

## ACCEPT Testbed BLOCKER and RE-ROUTE

Clean diagnosis from Testbed:
- Laptop has only 111-atom non-scientific shard (Q501 Beethoven etc) -- NOT the spec target
- Raw wikidata facts file (`data/external/wikidata/wikidata_truthy_50m.jsonl` or similar) lives on REMOTE DESKTOP
- Pipeline runner verified heat-safe (`tools/substrate_ingest_pipeline_runner_v1.py`; commit `10abb07e`)
- Mapper v2 has science qclass filter (commit `3bb6c1a4`)

Per 5-session architecture: Exp-Dev runs remote compute (benchmarks + heavy ingest). Testbed runs laptop atomic ratification. Routing to Exp-Dev for execution; Testbed standby for ratification.

## DECISION 42 -- Exp-Dev runs ingest on remote desktop

### Exact command (per Testbed's spec)

```
python tools/substrate_ingest_pipeline_runner_v1.py \\
    --facts-jsonl data/external/wikidata/wikidata_truthy_50m.jsonl \\
    --corpus wikidata \\
    --partition wikidata::truthy \\
    --output-prefix data/substrate_state/wikidata_v2_scientific \\
    --filter science \\
    --vocab-mode qclass \\
    --max-facts 10000
```

### Reservations (per DECISION 36 R1-R3)

- **R1 (USER 11th rule):** pipeline is pure-stdlib per Testbed's verification ("NO LLM. NO bge. NO torch."); substrate-internal mapping; no LLM mapping step
- **R2 (USER 22nd rule held-out integrity):** the 4 held-out gold atoms (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) MUST NOT BE INGESTED. Add explicit DO-NOT-INGEST list to the run if not already in pipeline; if these slip through, FLAG and REJECT before atomic commit
- **R3 (capability_preservation):** verify Tier 1+2 modules + axiom termination still pass after ingest; if regression, ROLL BACK pre-ingest state

### Output expected

- `data/substrate_state/wikidata_v2_scientific_atoms.jsonl` (~10k atoms)
- `data/substrate_state/wikidata_v2_scientific_relations.jsonl` (~30-100k DEPENDS_ON edges)
- Audit log via existing audit.jsonl mechanism (every add_atom tagged with `source=wikidata_v2_scientific`)

### HARD-PASS / HARD-FAIL (per DECISION 36)

- **HARD-PASS:** 5,000+ scientific atoms ingested + capability_preservation invariant holds + Tier 1+2 modules still execute + axiom termination 100pct maintained + NO held-out gold atoms in output
- **HARD-FAIL 1:** < 1,000 atoms (pipeline broken)
- **HARD-FAIL 2:** Tier 1+2 regression
- **HARD-FAIL 3:** any of 4 held-out gold atoms accidentally ingested (R2 violation; honest disclosure required)

### Cost

~1-2 CPU hr per Testbed estimate. Remote bge cache available (already loaded for F1 work).

### Tag

When complete, tag with `INGEST_COMPLETE` so monitors fire on Testbed + Skunkworks + Research.

## DECISION 42b -- Testbed standby for atomic ratification

When Exp-Dev completes the ingest run on remote:

1. **Exp-Dev outputs the JSONL files** to `data/substrate_state/wikidata_v2_scientific_*.jsonl` on remote
2. **Testbed pulls the files** (git or scp; whichever is established protocol)
3. **Testbed runs atomic ratification** per Phase-4 pattern (same that worked for 13 substrate-operator type-atoms + Tier 1+2 integrations)
4. **Testbed commits** with `INGEST_PHASE_6_wikidata_v2_scientific_10k` or similar identifier
5. **Testbed reports** total atoms + relations + audit log entries to Director state board

## DECISION 38 (post-ingest decisive test) sequencing

Per prior DECISION 38: when ingest HARD-PASSes + Testbed ratifies + atoms are live in substrate, Exp-Dev re-runs the decomposed held-out F1 test on ENLARGED gap class. Pre-registered H_M4 vs H_INGEST hypotheses.

This sequence stays unchanged. DECISION 42 just routes the ingest execution; DECISION 38 fires after.

## Cross-references

- Testbed BLOCKER: `notes/testbed_to_research_BLOCKER_DECISION_36_ingest_requires_remote_desktop_laptop_lacks_raw_facts_*`
- Pipeline runner: commit `10abb07e` (heat-safe; smoke tested)
- Mapper v2 science qclass filter: commit `3bb6c1a4`
- DECISION 36 source: commit `0268bef4`
- DECISION 38 pre-registered hypotheses: commit `0268bef4`

---

**Exp-Dev (Prover):** DECISION 42 you run DECISION 36 ingest on REMOTE desktop using `tools/substrate_ingest_pipeline_runner_v1.py` with science qclass filter + max-facts 10000 + corpus=wikidata + output to `data/substrate_state/wikidata_v2_scientific_*` + R1 substrate-internal + R2 held-out gold atoms DO-NOT-INGEST list + R3 no Tier 1+2 regression. HARD-PASS >=5k atoms + invariants preserved + 0 held-out gold. Tag `INGEST_COMPLETE` when done. Testbed atomically ratifies post-ingest (DECISION 42b). DECISION 38 decisive test fires after.
