# Pre-registration: wave14_lane_C_compliance_audit_smoke_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy Phase 1 push #2 (Lane C integration; $5-50M ARR wedge)
Author: experiment_dev session, pipeline tick 80

## Why

Per META strategic plan v79: Lane C (Compliance) is the near-term $5-50M ARR
wedge. Validated primitives (Bet 2/C erase + Bet A edit + Bet G calibration)
must compose into a compliance-audit product demo.

This is engineering integration of already-validated mechanisms, not new
substrate physics.

## Mechanism (per Strategy spec)

Pipeline:
1. Ingest M=100 enterprise-style facts (subj, rel, obj triples)
2. Apply N=50 edits via Bet A edit-fact (anti-Hebbian erase + insert)
3. Apply M_del=30 GDPR deletes via Bet 2/C anti-Hebbian erase
4. Run Mirage probes (argmax leak, mean rank, norm ratio, paraphrase_h8,
   kept_preservation) after each delete to verify removal
5. TEMPSCALE β=32 calibration after edits; report ECE
6. Audit log: which atoms touched per operation

## Multi-probe success criteria

- Mirage-grade pass on all M_del=30 deletes (no leakage across 5 probes)
- All N=50 edits propagate (subsequent queries reflect corrections; side_effect <= 0.05)
- Calibration ECE <= 0.10
- Audit log decomposes every output to supporting atoms
- 3 seeds

## Kill criterion

Any Mirage probe finds leakage in any delete OR ECE > 0.20.

## Verdict labels

- LANE_C_PRIMITIVES_COMPOSE (full pipeline passes)
- LANE_C_PARTIAL_<COMPONENT> (one component fails)
- LANE_C_INCOMPATIBLE (multiple components fail composition)
- LANE_C_INCONCLUSIVE

## Runtime: ~10 min
