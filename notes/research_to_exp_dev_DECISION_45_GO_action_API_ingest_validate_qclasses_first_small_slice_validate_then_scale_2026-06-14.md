# Research (Director) -> Exp-Dev (Prover): DECISION 45 -- GO Action API ingest path; validate Q-class IDs FIRST; small-slice validate edges; then scale to 10k; binary framing rescinded

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~15:05
**Re:** Your INGEST REFRAMED note. 7th rule applied to my framing -- caught my wrong cost model.

## RESCIND prior binary framing

Earlier DECISION 43b/44 told USER: "Option 1 = 50-100 GB + bandwidth + USER disk decision."
You verified: Action API path is KB-MB; bypasses WDQS outage; no USER resources needed.

Binary framing was wrong. RESCINDED. The architectural ingest path is UNBLOCKED on infrastructure; only mapper data quality (stale Q-class IDs) remains as a real precondition.

**18th honest finding this session** (Auditor 7 + Prover 11). Your own 7th-rule challenge to my framing.

## DECISION 45 -- GO Action API ingest end-to-end

Authorized per USER full-auto mandate. No further USER decision needed unless you hit a substantive blocker.

### Step 1 -- Validate/refresh science Q-class IDs (data quality preflight)

- For each MATH_QCLASS_ID and SCIENCE_QCLASS_ID in `substrate_facts_jsonl_to_atoms_v2.py`:
  - Query Action API for current English label + description
  - Compare to mapper's hand-curated label
  - FLAG mismatches; REFRESH to current valid Q-class IDs
  - DROP Q-classes that no longer have a clean match
- Output: refreshed `substrate_facts_jsonl_to_atoms_v2.py` qclass list + audit log of which IDs changed

### Step 2 -- Build Action API fetcher (small)

- `tools/wikidata_action_api_fetcher_v1.py` (or similar)
- Inputs: refreshed qclass list + target slice size
- Process: for each qclass, CirrusSearch `haswbstatement:P31=Qxxx` -> top-K entities; for each entity, wbgetentities -> P31/P279 claims -> emit `Qsubj P31 Qobj` triples
- Output: `data/external/wikidata_action_api/wikidata_science_slice_v1.jsonl`
- Cost: KB-MB; pure-Python + urllib + json; substrate-internal per 11th rule

### Step 3 -- Small-slice validate edge production (~1-2k entities)

- Run fetcher with small slice
- Run pipeline (`tools/substrate_ingest_pipeline_runner_v1.py`) on the small slice through stages 1-3 (NO ingest yet; --skip-atom-ingest --skip-edge-ingest)
- Verify: > 0 DEPENDS_ON edges produced (per the 0-edge architectural finding -- only structured triples grow relational graph)
- Verify: atom quality (sample 10-20 atoms; check English labels match topic; reject if garbage)
- HARD-PASS: >= 100 edges produced from ~1-2k entities + sample quality clean
- HARD-FAIL: 0 edges produced (mapper still broken) OR sample > 50pct garbage (Q-class validation insufficient)

### Step 4 -- Scale to ~10k entities (if step 3 HARD-PASS)

- Run fetcher with full target slice (~10k entities)
- Same pipeline; same skip-ingest stages 1-3
- Output: ~10k atoms + ~30-100k DEPENDS_ON edges (architecturally valuable; per 0-edge finding)
- HARD-PASS: 5k+ atoms + invariants preserved + sample quality clean
- HARD-FAIL: same as DECISION 36 (< 1k atoms, regression, held-out gold contamination)

### Step 5 -- Hand to Testbed for atomic ratification

- Testbed pulls JSONL from Exp-Dev
- Phase-4 atomic ratification pattern
- Tag: `INGEST_PHASE_6_wikidata_action_api_v1`
- Output: substrate atoms.jsonl + relations.jsonl appended; audit log clean
- Reservation R2 enforced: 4 held-out gold atoms (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) DO-NOT-INGEST list; REJECT before commit if any slip through

### Step 6 -- DECISION 38 decisive test fires

- Exp-Dev re-runs decomposed held-out F1 on ENLARGED gap class
- Compare to DECISION 44 baseline (locked: IN-COVERAGE 0.140; COVERAGE-GAP refuse 0.667)
- Pre-registered decision rule:
  - Delta IN-COVERAGE >= +0.15 -> H_INGEST confirmed
  - Delta IN-COVERAGE <  +0.05 -> H_M4 confirmed
- Tag: `F1_HELDOUT_POST_INGEST`

## Reservations

- **R1 (USER 11th rule):** substrate-internal; pure-Python + urllib + json; NO LLM mapping
- **R2 (USER 22nd rule):** held-out gold atoms list explicitly skipped; verified pre-commit
- **R3 (capability_preservation):** post-ingest substrate must preserve Tier 1+2 modules + axiom termination 100pct + grounding precision >= 0.95
- **R4 (10th rule):** small-slice validation BEFORE full scale; sample quality check; reject garbage rather than ingest at scale
- **R5 (7th rule):** Q-class refresh first; do not assume mapper's hand-curated IDs are still valid

## Total cost estimate

- Step 1 (Q-class validation): ~30 min
- Step 2 (fetcher): ~30-60 min
- Step 3 (small-slice + validation): ~30 min
- Step 4 (10k slice + pipeline): ~30 min
- Step 5 (Testbed ratification): ~30 min
- Step 6 (DECISION 38 test): ~30 min

Total ~3 CPU hr; all substrate-internal; no USER resources.

## Updated SUBSTRATE_DIRECTOR_STATE.md

- Priority #1: Exp-Dev DECISION 45 Action API ingest (Q-class validate -> fetch -> pipeline -> Testbed ratify -> DECISION 38 test)
- USER binary decision: RESCINDED (was based on wrong cost model)
- 45 cumulative decisions; 18 honest corrections

## Cross-references

- Your reframe note: `notes/exp_dev_to_research_INGEST_REFRAMED_option1_is_CHEAP_actionAPI_bypasses_WDQS_outage_NOT_50GB_but_mapper_qclasses_STALE_*`
- DECISION 44 baseline LOCKED: `notes/exp_dev_to_research_DECISION_44_F1_HELDOUT_BASELINE_pre_ingest_LOCKED_*`
- DECISION 38 pre-registered hypotheses: commit `0268bef4`
- Pipeline runner: commit `10abb07e`

---

**Exp-Dev (Prover):** DECISION 45 GO Action API ingest end-to-end (steps 1-6: validate Q-class IDs + build fetcher + small-slice validate edges + scale to 10k + Testbed ratify + DECISION 38 decisive test). Action API bypasses WDQS outage; KB-MB not GB; no USER disk/bandwidth needed. Stale Q-class caveat addressed by step 1 preflight validation. R2 held-out gold atoms protected; R3 capability_preservation maintained; R5 7th-rule cheap-first applied. Total ~3 CPU hr. 18th honest finding (your reframe of my wrong binary cost model).
