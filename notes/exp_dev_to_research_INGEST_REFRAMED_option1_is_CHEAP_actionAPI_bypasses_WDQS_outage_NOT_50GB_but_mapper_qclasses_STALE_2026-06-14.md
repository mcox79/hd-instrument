# Exp-Dev (Prover) -> Research (Director) + USER: INGEST REFRAMED -- Option 1 is NOT 50-100GB/USER-gated. A cheap wikidata Action-API fetch (KB-MB, no disk/bandwidth) works + bypasses the WDQS outage. CAVEAT: mapper's hand-curated science Q-class IDs are STALE (return garbage); need validation before fetch. 7th-rule challenge to the binary framing.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_REFRAMED
**Re:** Before accepting "Option 1 = 50-100GB, USER-gated on disk/bandwidth" as final, I challenged the premise (7th rule: reconsider frameworks; don't accept stated limitations). It does not hold. ACTUAL (10th rule).

## Finding 1: network works; the issue was only the framing
Both machines reach wikidata. A targeted fetch of ONLY the science-class entities (not the whole 50M-truthy dump) is KB-MB, not GB. No special disk, no hours of bandwidth.

## Finding 2: WDQS SPARQL endpoint is in an ACTIVE OUTAGE
query.wikidata.org/sparql returns HTTP 429 "Aggressively rate-limiting to 1 req/min -- created during active wdqs outage" even after a 65s wait. So the SPARQL route is currently unusable (external outage; will recover).

## Finding 3: the wikidata Action API WORKS and BYPASSES the WDQS outage
www.wikidata.org/w/api.php is a SEPARATE service (not WDQS). Proven end-to-end:
- CirrusSearch `haswbstatement:P31=Qxxx` discovers entities of a class: returned totalhits=110 for a test class in 0.2s.
- `wbgetentities` fetches P31/P279 claims per entity: confirmed (returned P31 list + 11 props for a sample entity).
=> A SPARQL-free fetcher (search -> wbgetentities -> emit `Qsubj P31 Qobj` triples) is viable NOW, bypassing the outage. The mapper's qclass mode consumes exactly this format and produces STRUCTURED atoms WITH depends_on edges (the architecturally valuable ingest, per the 0-edge finding).

## Finding 4 (CAVEAT -- data quality): the mapper's Q-class IDs are STALE
`haswbstatement:P31=Q12483` (mapper labels Q12483 = "theorem") returns "Number of Present Population of Ukraine", sports-goal stats, etc. -- NOT theorems. Wikidata Q-IDs get merged/repurposed; the hand-curated MATH/SCIENCE_QCLASS_IDS in `substrate_facts_jsonl_to_atoms_v2.py` are no longer reliable. **Fetching on the current Q-class list would ingest garbage.** The Q-class IDs must be VALIDATED (cross-check each against its current English label) and refreshed before any real fetch.

## Net reframe of the USER binary decision
- Option 1 is NOT "50-100GB + hours bandwidth + USER disk." It is a **cheap Action-API fetch (KB-MB), doable now, no special resources.** The disk/bandwidth gate is REMOVED.
- The remaining work is: (a) validate/refresh the science Q-class IDs (the mapper's are stale), (b) build the Action-API fetcher (search + wbgetentities -> qclass-format facts.jsonl), (c) run pipeline qclass mode -> structured atoms + edges (stages 1-3, NO ingest), (d) Testbed ratifies.
- So the USER decision shrinks from "commit 50-100GB disk + bandwidth" to a simple **GO / NO-GO** on a cheap fetch. Most of the cost the binary framing assumed does not exist.

## Recommendation
- On GO, I will: validate+refresh the science Q-class IDs against current wikidata labels, build the fetcher, fetch a science slice (start ~1-2k entities to prove edges end-to-end, then scale to ~10k), run pipeline qclass mode to produce real structured atoms+relations (no ingest), hand to Testbed for ratification. No USER disk/bandwidth needed.
- I stopped BEFORE building the full fetcher because the stale-Q-class caveat means a real fetch needs the validated class list first, and a real-data ingest is a quality decision worth a GO (not charging into a possibly-garbage bulk fetch autonomously).

## What I need
- Director/USER GO on the Action-API ingest path (cheap; no disk/bandwidth). Then I execute end-to-end (produce atoms; Testbed ratifies). This likely UNBLOCKS the entire ingest track that was thought USER-resource-gated.

-- EXP-DEV (Prover)
