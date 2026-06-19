# exp_dev hand-off — research: composed reasoning over typed-edge KGs

Filed-by: research (Opus), 2026-06-18 PM
Trigger: USER strategic question on composed-reasoning support; lit-scan delivered actionable anchors
Source research note: d:/AI/hd-instrument/notes/research_composed_reasoning_kg_architectures_2026-06-18.md
Pause state: respect data/orchestrator_paused.flag; this is an anchor-CANDIDATE hand-off, not an emergency-refill

Per [[feedback-no-experiment-design-in-prompts]]: no design here, only anchor pointers + substrate-product readings + tier hints. exp_dev owns the design.

## Anchor candidates (rank-ordered)

### A1 — multi-hop-provenance cert-gate prototype (NEAR-TERM, lowest cost)
- Pointer: MINERVA path-walking RL (Das+18, arxiv.org/abs/1711.05851) instantiated over the 41k-atom typed-edge graph
- Substrate-product reading: converts the 4-gate self-cert engine into a 5-gate engine; the new gate verifies each hop against the persisted (src, rel_type, tgt) tuple in the Store. No LLM. Directly composes with existing gate-0-both-ends + corpus-completeness pattern.
- Tier hint: MEASURED_MECHANISM (it's a deterministic structural check; cert-chain-grade if oracle path is golden)
- Why-now: the typed-edge graph IS the architectural substrate this family needs; existing rel_TYPE persistence is sound (per [[reference_store_drops_relation_edge_metadata_role_on_source_atom_2026-06-18]]); USER-strategic alignment
- Pre-reg bands: HARD-PASS >=70% answer-found on held-out 2-hop test built from HYPERNYM/IS_A/PART_OF chains + 100% paths edge-verifiable; HARD-FAIL <40% OR ANY returned path contains an edge not in Store

### A2 — AMIE 3 offline rule-mining consolidation pass (MID-TERM)
- Pointer: AMIE 3 (Lajus+20, link.springer.com/chapter/10.1007/978-3-030-49461-2_3; code github.com/dig-team/amie); AnyBURL (Meilicke+23, link.springer.com/article/10.1007/s00778-023-00800-5)
- Substrate-product reading: sleep-consolidation v0 — offline pass over the 41k-atom snapshot mines closed Horn rules with PCA-confidence; materializes a delta of inferred edges + candidate new schema rel_types via rule-head promotion. Reviewed before merge. Per [[feedback_refresh_must_not_silently_recompute_cert_classification_snapshot_before_mass_mutation_2026-06-18]]: snapshot per-record state before any mutation; classification is the cert-owner's deliberate call.
- Tier hint: COST_MODEL or MEASURED_MECHANISM depending on review protocol
- Why-now: composes cleanly with the typed-edge graph; PCA refuses to treat absent=false (matches our 0-phantom discipline); USER-strategic alignment with substrate-autonomy directive
- Pre-reg bands: HARD-PASS >=50 rules with PCA-confidence >=0.7 AND head-coverage >=0.3; HARD-FAIL <10 rules above those thresholds (would indicate edge density too low; rescue = drill edge-density gap)

### A3 — active-ingest uncertainty layer on Bucket B (MID-TERM)
- Pointer: Kajino+15 active learning for multi-relational data (dl.acm.org/doi/10.1145/2736277.2741103); AMIE+PCA cardinality flagging (Galarraga+20, luisgalarraga.de/docs/amie3.pdf)
- Substrate-product reading: self-driven gap-id + next-ingest selection layered on top of Bucket B's existing edge-budget + 0-phantom + cross-corpus completeness gates. KG identifies its own coverage gaps via PCA confidence drops + cardinality-bound estimators.
- Tier hint: MEASURED_MECHANISM
- Why-now: Bucket B already has the cert-conditions this family needs; integration is mechanical; substrate-autonomy directive
- Pre-reg bands: anchor-shape decision deferred to exp_dev; suggested band = >=N flagged gaps with PCA<0.5 AND fill-success >=50% on oracle confirmation

## Context pointers (paths, not summaries)

- d:/AI/hd-instrument/notes/research_composed_reasoning_kg_architectures_2026-06-18.md (source research note; tables + citations)
- d:/AI/hd-instrument/data/substrate_index/*/atoms.jsonl (41k atoms; typed-edge corpus)
- 4 LIVE self-cert gates (gate-0-both-ends + discrimination-regime + working-baseline-cliff + corpus-completeness) — the new multi-hop-provenance gate sits at the same layer
- [[reference_store_drops_relation_edge_metadata_role_on_source_atom_2026-06-18]] — rel_type persistence is sound; first-class rel_types preferred over edge-metadata roles
- [[reference_remote_dispatch_cell_readiness_checklist_2026-06-17]] — pre-dispatch checklist for any remote cell
- [[feedback_substrate_autonomy_path_encode_audit_discipline_as_self_certification_USER_2026-06-17]] — composed-reasoning anchors all serve this directive

## Contract

- exp_dev owns the experiment design (anchor selection, cell shape, smoke/full split, queue routing)
- research has NOT designed cells in this hand-off (per [[feedback-no-experiment-design-in-prompts]])
- exp_dev is free to re-rank A1/A2/A3 or split into sub-anchors per its own autonomy
- pause-flag honored; if data/orchestrator_paused.flag exists, exp_dev should NOT ship and instead file an annotation-only reading

## Autonomy declaration

This hand-off is exp_dev-actionable per the v195-template criterion: each anchor proposes a concrete experiment with pre-reg bands, names a mechanism ready for empirical test, and is gated by structurally-derived HARD-PASS/HARD-FAIL bands rather than aspirational targets.
