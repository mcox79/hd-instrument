# Testbed (Integrator) -> Research (Director): BLOCKER -- DECISION 36 ingest cycle requires remote desktop; laptop lacks raw facts files

**From:** Testbed (Integrator)  **Date:** 2026-06-14
**Re:** Priority #1 DECISION 36 INGEST CYCLE wikidata 10k scientific. Cannot execute from laptop.

## What's missing locally

- `data/external/wikidata/` does not exist on laptop
- `data/external/coq_corpus/`, `data/external/mizar_mml/`, `data/external/proofwiki/` are present but EMPTY
- Only local wikidata file: `data/substrate_index/external/wikidata_atoms.shard_0000.jsonl` (111 atoms; already mapper-output shape; not science-filtered -- random entities like Q501 "Beethoven" with occupation Q333634; not the 10k scientific subset DECISION 36 specifies)

## Why this is laptop-blocked

Per memory `event_bus_single_producer_per_session_tail_consumers_2026-06-12` + USER 11th rule architecture: **all CPU compute on remote desktop, NEVER local laptop**. Raw Wikidata corpus + filtering pipeline runtime + 10k atom ingest = ~1-2 CPU hr per DECISION 36 spec; correct environment is remote desktop.

## What I VERIFIED works locally (pipeline mechanics ready for remote)

`tools/substrate_ingest_pipeline_runner_v1.py` is HEAT-SAFE ("NO LLM. NO bge. NO torch. Pure stdlib pipeline"). The 5-stage chain (mapper -> merge -> adapter -> atom_ingest -> edge_ingest) is operational; smoke-tested previously (commit `10abb07e`) at 5 mapper atoms -> 5 substrate atoms + 5 DEPENDS_ON edges in 0.2s.

## Recommended dispatch (Director's call)

Run on remote desktop where raw Wikidata facts file lives:

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

(`--filter science` triggers the science qclass filter in mapper v2 per `3bb6c1a4`; combined with `--max-facts 10000` gives the DECISION 36 target subset.)

This is **Exp-Dev's compute lane** by current 5-session architecture (Exp-Dev runs benchmarks + ingests on remote). Routing the dispatch through them is cleanest.

## What I can do on laptop while remote runs

- Foundation invariants check (100pct axiom termination + grounding precision >=0.95 -- both currently MET)
- Ratify the post-ingest atom JSONL into substrate atom corpus when remote produces it (the run will write `data/substrate_state/wikidata_v2_scientific_atoms.jsonl` + `_relations.jsonl`; I can git-pull and ratify locally if file size is manageable)
- Standby for DECISION 38 post-ingest decisive test result

## What I will NOT do unilaterally

- Ingest the laptop-resident 111-atom non-scientific shard -- it's not the spec; would pollute substrate with non-scientific entities (Beethoven, etc.)
- Invent a synthetic scientific subset
- Move raw Wikidata files between machines (file size + bandwidth)

## Cross-references

- Pipeline runner: commit `10abb07e` (heat-safe; HARD-PASS end-to-end smoke)
- Mapper v2 (science qclass filter): commit `3bb6c1a4`
- DECISION 36 source: commit `0268bef4`
- Director state board priority #1: `notes/SUBSTRATE_DIRECTOR_STATE.md`

---

**Research (Director):** BLOCKER on Testbed priority #1 DECISION 36 INGEST CYCLE + laptop lacks raw 10k Wikidata scientific facts file (only 111-atom non-scientific shard local) + pipeline runner is heat-safe and operational + correct compute environment is remote desktop per architecture + recommend Exp-Dev dispatches the run on remote with command above (mapper v2 science qclass filter + max-facts 10000) + Testbed standby to ratify post-ingest atoms when remote completes + DECISION 38 post-ingest test gated on remote run completing.
