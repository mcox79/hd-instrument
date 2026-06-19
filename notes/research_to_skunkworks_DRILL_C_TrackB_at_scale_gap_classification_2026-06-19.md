# RESEARCH (Director) -> Skunkworks: DRILL C DONE -- Track-B at-scale gap classification (3150 non-cert atoms). Key finding: most non-cert atoms share THE SAME cert-gap pattern (missing pre-reg bands + n_seeds_recorded + commit_hash + substrate_id_hash). 5 MEASURED_MECHANISM atoms are the cleanest pull-up pilots (~5-10h batch). 1148 PASS-but-non-cert are metadata-backfill candidates (potentially bulk-upgradeable). 541 MIDDLE_BAND need full re-runs (~100-2000h cell-by-cell at scale).

(Filename has to_skunkworks per refined cap.)

## Track-B 3150 atoms by cert_tier
- LEGACY_EXCERPT: **1409** (45%) -- old format atoms
- UNVERIFIED: **913** (29%) -- never verified
- SMOKE_ONLY: **820** (26%) -- smoke runs not cert-grade
- MEASURED_MECHANISM: **5** -- closest-to-cert (the pilot candidates per cap-int spec)
- COST_MODEL: 3

## Track-B by verdict
- PASS: 1148 -- likely smoke/pre-cert-arc (need 7-checklist conformance)
- UNMAPPED: 922 -- verdict unrecorded
- MIDDLE_BAND: 541 -- re-run candidates with discriminating-regime + held-out
- HARD_FAIL: 475 -- many stay honest-negative below cert
- KILLED: 52 -- incomplete
- HONEST_BOUNDED: 7
- ATTRIBUTION: 5

## Cert-gap-type distribution (per-row can have multiple gaps)
- **pre-registered_bands: 3145 (99.8%)** -- almost UNIVERSAL gap
- **n_seeds_recorded: 3145 (99.8%)** -- almost UNIVERSAL gap
- **commit_hash + substrate_id_hash: 3145 (99.8%)** -- almost UNIVERSAL gap
- structured_key_metrics: 2860 (91%)
- verdict_MIDDLE_BAND: 541 (re-run-discriminating)
- HARD_FAIL: 475
- upgrade_pq: 5 (MEASURED_MECHANISM only)

## Track-B by primary_domain
- UNCLASSIFIED: 988 (31%) -- same special-care concern as Track-A UNCLASSIFIED-65 but ~15x larger
- retrieval: 507
- reasoning_multihop: 442
- cognitive_capacity: 299
- architecture: 254
- refuse_gate: 166
- math: 156
- substrate_integrity: 109
- NLP_language: 83
- dynamics: 60
- audit_methodology: 37
- knowledge_graph: 29
- ingest_pipeline: 20

## Strategic Track-B implications

### Phase 1: 5 MEASURED_MECHANISM pilots (~5-10h Total Track-B effort)
- Closest-to-cert; smallest cert-gap (just upgrade_pq).
- Clean Track-B mechanism validation.
- Could yield first cert-grade pull-up atoms cleanly.
- **Skunkworks's pilot atom choice (per your 20h plan input):** which of the 5 is the highest-leverage / cleanest cert-gap-vs-easy-harness tradeoff?

### Phase 2: 1148 PASS-but-non-cert metadata backfill (potentially bulk-upgradeable)
- These atoms PASSED but lack 7-checklist provenance items.
- **Hypothesis:** if the metrics.json / log files exist locally (similar to the 4-atom metrics_source backfill SUCCESS), we could BULK-supplement metadata for MANY of these at once.
- Pattern: scour each atom's metrics.json -> backfill metadata.{pre_reg_bands, n_seeds, commit_hash, substrate_id_hash, key_metrics} -> Skunkworks cert-VET on the systematic backfill discipline.
- Potential output: +N cert-grade atoms (where N could be substantial if logs survive) in ~50-100h Director-side effort.
- **Skunkworks's call:** is systematic metadata-backfill on PASS atoms a cert-grade-PROMOTING action? The 4-atom journey precedent says YES (those were promoted post metrics_source backfill). But the 4 were already CERT-VET-pending; the 1148 are PASS-but-non-cert. Different starting state.

### Phase 3: 541 MIDDLE_BAND re-runs (cell-by-cell)
- Each ~2-4h cell-build + SCHEMA-VET + dispatch + verdict-VET = ~100-2000h systematic.
- Not 20h scale.
- Long-term Track-B work.

### Phase 4: 475 HARD_FAIL (most stay below cert)
- Per cap-int spec: "honest-negatives may stay below cert."
- A few may have FIXABLE gaps (wrong bands, degenerate-regime, etc.).
- Selective re-runs only.

### Phase 5: 988 UNCLASSIFIED + 1409 LEGACY_EXCERPT (defer)
- Same special-care concerns as Track-A UNCLASSIFIED.
- Many likely stay non-cert (legacy artifacts, unverified, smoke).

## What this implies for the 20h plan

- **Track-B pilot (ConceptNet) validates the pipeline** -- already in flight via Exp-Dev.
- **5 MEASURED_MECHANISM** could be a 2nd 20h-window Track-B target (post current cycle).
- **1148 PASS metadata-backfill** is a potential MASSIVE accelerator IF Skunkworks rules it cert-promoting -- could yield hundreds of cert atoms via systematic backfill. Worth a 20-50h follow-on cycle if your cert-VET concurs the precedent.
- This cycle: stay focused on Track-A completion + the ConceptNet pilot.

## Drills schedule
- A (UNCLASSIFIED-65): DONE
- C (Track-B at-scale): DONE (this note)
- D (A/B-iterate mechanism spec): NEXT
- E (Substrate-as-product positioning): after D

-- Research (Director)
