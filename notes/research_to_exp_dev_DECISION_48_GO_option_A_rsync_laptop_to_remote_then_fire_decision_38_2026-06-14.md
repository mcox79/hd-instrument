# Research (Director) -> Exp-Dev (Prover): DECISION 48 -- GO Option A rsync laptop substrate state to remote + fire DECISION 38

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~16:55
**Re:** USER deferred to my recommendation. Option A authorized.

## DECISION 48 -- GO Option A (rsync laptop to remote)

### Spec

1. **rsync the new substrate state from laptop to remote desktop:**
   - `data/substrate_state/wikidata_action_api_v1_adapted_atoms.jsonl`
   - `data/substrate_state/wikidata_action_api_v1_adapted_relations.jsonl`
   - `data/substrate_state/wikidata_action_api_v1_atoms.jsonl` (raw if separate)
   - Updated `data/substrate_index/<corpus>/atoms.jsonl` files (post Phase-6 ratification)
   - Updated `data/substrate_index/<corpus>/relations.jsonl` files
   - Updated `data/substrate_index/<corpus>/audit.jsonl` files
   - `data/substrate_index/foundation_primitives_ratify_audit.jsonl`
   - `data/substrate_index/ingest_audit_wikidata_action_api_v1.jsonl`
   - 8 new foundation primitive atoms (from Phase 1 46b ratification)
   - 15 SPECIALIZES edges from 46b

2. **Verify remote state post-sync:**
   - Atom count on remote = laptop count (26,272)
   - Relation count on remote = laptop count (5,231)
   - File hashes match (or rsync confirms)

3. **Run DECISION 38 measurement on remote (with bge):**
   - Decomposed held-out F1 per DECISION 32 spec
   - IN-COVERAGE macro-F1 + per-axis
   - COVERAGE-GAP refuse-rate + FP count
   - Compare to locked DECISION 44 baseline (IN-COVERAGE 0.140; COVERAGE-GAP refuse 0.667)
   - Pre-registered decision rule (locked DECISION 44):
     - Delta IN-COVERAGE >= +0.15 -> H_INGEST confirmed
     - Delta IN-COVERAGE < +0.05 -> H_M4 confirmed
     - Mixed -> partition + report subsets

4. **Tag result:** `F1_HELDOUT_POST_INGEST` so both monitors fire

### Safety rails (R3 + USER 11th rule)

- **R3.1 (do not overwrite valid remote state):** if remote has any files NEWER than laptop (timestamp comparison), STOP + report; do not blindly overwrite
- **R3.2 (use additive sync where possible):** rsync with --update flag so only laptop-newer files overwrite remote
- **R3.3 (BACKUP remote canonical state before sync):** snapshot `data/substrate_index/` on remote to `data/substrate_index_backup_pre_sync_2026-06-14/` so we can rollback if something goes wrong
- **R3.4 (post-sync integrity check):** run a quick atom-count + relation-count + axiom-termination probe on remote BEFORE running DECISION 38; if any invariant fails, ROLL BACK to backup

### Cost

- rsync time: minimal (atoms.jsonl files are MB; foundation primitives are KB)
- backup time: ~1 min
- integrity check: ~5 min
- DECISION 38 measurement: ~10-20 min (bge cached on remote)

Total: <30 min including safety margin.

### Per USER 11th rule (substrate-on-its-own)

No LLM-assist anywhere in sync or measurement. Pure rsync + canonical scorer + bge primitive (allowable per 11th rule as representation primitive).

### Per USER 22nd rule (held-out integrity)

Held-out gold atoms (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) were already R2-protected during ingest and remain R2-protected post-sync. Verify in integrity check.

## What this unblocks

Once DECISION 38 result lands:
- We get F1_HELDOUT_POST_INGEST measurement on enlarged substrate (26,272 atoms; 8 foundation primitives)
- H_M4 vs H_INGEST verdict per DECISION 44 pre-registered decision rule
- Phase 2 sequencing CALL (axiom-authoring vs M4b query-side reformulation)
- Substrate-product positioning final F1 number for this session

## What stays stable regardless of DECISION 38 outcome

- Tier 1+2 production-verified on public held-out (HMM 0.90+ etc)
- 100pct axiom termination (213/213 + 8 foundation primitives + ingested atoms)
- Capability_preservation = 1.0
- 25 PROVABLY_EQUIVALENT integrations + 0 false-merges
- First cross-domain L6-PROOF complete (convolution_theorem)
- First autonomous-discovery edge (gradient -> derivative)
- BGE cache infrastructure
- 5 production-verified backend/hdlab modules

## Cross-references

- USER deferral: this turn
- DECISION 47 Phase 1 PARTIAL + Phase 2 deferral + Option A recommendation: commit `4081d5f0`
- DECISION 38 pre-registered hypotheses + decision rule: commit `0268bef4`
- DECISION 44 baseline locked (the reference): commit `b240b93b`
- Phase 1 46a Skunkworks + 46b Testbed ratification: commit `821a9640`
- INGEST_PHASE_6 ratification: commit `934be79e`

---

**Exp-Dev (Prover):** DECISION 48 GO Option A rsync laptop substrate state to remote + fire DECISION 38. Safety rails: R3.1 don't overwrite newer remote files / R3.2 additive --update / R3.3 backup remote pre-sync to data/substrate_index_backup_pre_sync_2026-06-14/ / R3.4 post-sync integrity check (atom count + relation count + axiom termination probe). Cost <30 min total. Tag F1_HELDOUT_POST_INGEST when measurement lands. Pre-registered decision rule: delta IN-COVERAGE >=+0.15 -> H_INGEST; <+0.05 -> H_M4. Phase 2 sequencing call follows from result.
