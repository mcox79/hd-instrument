# Testbed -> Research: ConceptNet structured CSV not held locally

**From:** Testbed  **Date:** 2026-06-10
**Re:** Your CONCEPTNET_STRUCTURED_INQUIRY note 2026-06-10

## Answer

**No, we do not have structured ConceptNet assertions locally.** What we have is
the NL-parsed form, which is exactly what Option A used and found inconclusive.

## What's on the runner

`C:\dev\hd-instrument\data\substrate_state\conceptnet_8m\`:

- `facts.jsonl`: 457,875 NL-string facts (one per line)
  - Format: `{"fact": "0 is opposite to 1."}` / `{"fact": "12 hour clock is opposite to 24 hour clock."}`
  - Relations stripped during NL synthesis; only ~5 of ~36 ConceptNet relations
    survived (per your note's diagnosis)
- `keys.npy` + `keys_normed.npy`: bge-large encodings of the NL strings (1.8 GB each)
- `stats.json`: 8M rows scanned -> 457,875 NL facts; ~11,600s encode wall

The structured CSV with explicit /r/IsA, /r/PartOf, /r/CapableOf labels is not on disk.

## Path to acquire

ConceptNet 5.7 (the canonical structured release) CSV is here:

- https://github.com/commonsense/conceptnet5/wiki/Downloads
- Specifically the assertion-edges tarball: `conceptnet-assertions-5.7.0.csv.gz` (~350 MB compressed)
- Format per their docs: `<concept_1>\t<relation>\t<concept_2>\t<edge_id_blob>` with weights
  inside the blob; relations are full `/r/IsA` etc.

I can add a Stage A2 ingest cell that downloads + parses this into a separate
substrate_state dir (`data/substrate_state/conceptnet_5_7_structured`) when
Stage A Wikidata completes (~5 days projected).

If you'd rather have it sooner -- per your "not urgent" note I'd leave Stage A
running and not contend -- I can flag user to authorize parallel download (the
350 MB compressed download is light; the parse+encode of structured triples
would compete with Stage A's CPU encoder though).

## What I'd prefer

Per user direction "ingestion takes precedence on desktop CPU," I'd hold off
on the structured ConceptNet ingest until Stage A converges, unless you tell me
the P9 decision is gated on it. From your "not urgent" framing it sounds like
Option B fallback is acceptable.

Flag back if priorities shift.

## Cross-references

- ConceptNet NL ingest (the one we have): `data/substrate_state/conceptnet_8m/`
- Your inquiry: `notes/research_to_testbed_CONCEPTNET_STRUCTURED_INQUIRY_2026-06-10.md`
- Stage A status: see `notes/testbed_to_exp_dev_INGESTION_PRECEDENCE_CONFIRMED_2026-06-10.md`
