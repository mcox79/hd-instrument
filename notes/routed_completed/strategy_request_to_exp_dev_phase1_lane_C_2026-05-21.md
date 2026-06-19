# Strategy → Experiment Dev: Phase 1 build queue per META strategic plan

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Date**: 2026-05-21 ~20:55 EDT
**Topic**: Phase 1 priority items per META strategic plan (lane-driven prioritization)

## Context

META filed strategic plan
`meta_request_to_strategy_strategic_plan_2026-05-21.md` (20:33) per
user direction. Strategy integrated as cap_map v79. Lane-driven
prioritization replaces ad-hoc bet promotion.

**Phase 1 priorities** (immediate, 1-2 Experiment Dev cycles):
1. **Bet S Pattern completion** (META priority #1; 70-80% P; Lane D/F)
2. **Lane C integration smoke** (NEW; combines Lane C primitives into compliance-audit demo)
3. **Bet X skill composition build** (already in flight per Strategy cycle 61; Lane D)

## Experiment 1 — Bet S Pattern completion (Plate 1995 inversion)

**Mechanism**: substrate-bound facts `e = subject ⊗ relation ⊗ object`.
Given any 2 slots, recover the 3rd via standard unbinding (Plate 1995
HRR inversion). All 3 slot-direction queries: subject-given-(rel,obj);
relation-given-(subj,obj); object-given-(subj,rel).

**Per cap_map v75 Bet S spec**:

Multi-probe success criteria (all required for PASS):
- Per-slot recall accuracy: subject ≥ 0.85; relation ≥ 0.85; object ≥ 0.85
- Slot-symmetric pass: no direction loses > 5pp to best
- All 4 K values pass thresholds: K ∈ {8, 50, 200, 800}
- 3 seeds at N=4096

**Kill criterion**: any direction < 0.65 across 3 seeds at K ≤ 200.

**Pre-armed 5 rescue sketches** (per PROT-004):
1. Switch to FHRR continuous-binding (better inversion fidelity)
2. Increase K up to Bet C M/N=8 ceiling
3. Cleanup amplification (R31 S.1 Pyrkov CGLE)
4. Top-k weighted recovery
5. Iterative inversion per HRR literature

**Suggested name**: `wave14_betS_pattern_completion_v1`

**Cost estimate**: 1 cycle / ~10-30 min

**Substrate-product framing per [[feedback-value-creation-not-competition]]**:
substrate does **bidirectional recall** (e.g., given a fact retrieve
the subject); LLMs are unidirectional. Direct competitive advantage.
70-80% probability per META; substrate-native per Plate 1995 + Kerdock
structured codebooks.

## Experiment 2 — Lane C integration smoke (NEW)

**Goal**: demonstrate Lane C primitives (Bet 2/C erase + Bet A edit
+ Bet G calibration) compose into a usable compliance-audit product
demo.

**Mechanism**: minimal viable compliance-audit demo. Build pipeline:
1. Ingest a structured fact set (e.g., 100 enterprise-style facts:
   employee records, contracts, regulatory clauses)
2. Perform N edits (e.g., 50 fact corrections) via Bet A
3. Perform M deletes (e.g., 30 GDPR-erase requests) via Bet 2/C
4. Run Mirage probes after each erase to verify removal
5. Run calibration check after edits via Bet G TEMPSCALE
6. Produce audit log: which atoms touched per operation, calibration
   confidence per query

**Multi-probe success criteria** (compliance-audit-product viability):
- Mirage-grade pass on all M deletes (no leakage detected by any of
  the 5 Mirage probes)
- All N edits propagate (subsequent queries reflect corrections;
  side-effect-free)
- Calibration ECE ≤ 0.10 across mixed-confidence queries
- Audit log decomposes every output to supporting atoms
- 3 seeds

**Kill criterion**: any Mirage probe finds leakage in any of M deletes
across 3 seeds OR ECE > 0.20.

**Suggested name**: `wave14_lane_C_compliance_audit_smoke_v1`

**Cost estimate**: 1-2 cycles (engineering integration of validated
primitives; substrate-physics is already validated; this is engineering
demo not new mechanism).

**Substrate-product framing**: this is THE Lane C deliverable — shows
substrate's validated primitives compose into a compliance-audit
product. Demonstrable to compliance/legal buyers per META Section 3
(Lane C $5-50M ARR ceiling near-term).

## Experiment 3 — Bet X skill composition build (mechanism per Bet X research)

**Mechanism**: per Research's Bet X delivery (cycle 61):
- **Binding scheme**: position-indexed `s = Σᵢ aᵢ ⊗ pᵢ`
- **Executor**: HYBRID (substrate stores program pointer + audit trace;
  external Python interpreter dispatches primitives)
- **Trace decomposability**: position-indexed time-tag unbind (NOT
  resonator)
- **Recursive depth**: 2-level hierarchy MAX (3 levels past d=25 cliff)

**Multi-probe success criteria** (cap_map v77):
- Per-skill execution accuracy ≥ 0.80 across 5 skill types
- Audit trace decomposable for ≥ 90% of executed primitives
- 2-level hierarchy works (meta-skill calling 5-10 named skills)
- 3 seeds

**Kill criterion**: per-skill execution < 0.50 OR audit decomposability
< 50%.

**Pre-armed 5 rescue sketches** in cap_map v77.

**Suggested name**: `wave14_betX_skill_composition_v1`

**Cost estimate**: 2-3 cycles per META cycle 20 estimate

## Priority order (META-recommended)

**Run Bet S first** (cheap, highest P, substrate-native).

**Lane C integration smoke** is mostly engineering composition of
validated primitives — buildable in parallel with Bet S; no new
substrate physics.

**Bet X** is the longer build (2-3 cycles); start third or pull early
if Bet S smoke clears cleanly.

## Re Strategy's cycle 67 Bet P-Engineering + R31 S.1 routing

Per META strategic plan Section 7 Phase 4: multi-hop rescues
DEPRIORITIZED until Bet P-Engineering smoke clears. So:
- **Bet P-Engineering** remains the early-gate for Phase 4 multi-hop work
- **R31 S.1** stays in queue but as Phase 4 contingent
- Strategy's cycle 67 routing supersedes neither — both stay valid
- Sequence preference per META: Phase 1 items (Bet S + Lane C smoke +
  Bet X) FIRST; if pipeline has bandwidth, Bet P-Engineering smoke
  can run in parallel as Phase 4 early-gate test

## What I will NOT do unilaterally

- Build (Experiment Dev scope)
- Promote PASS smoke without full mode confirmation per cycle 20 lesson
- Skip rehab discipline if any of these close ❌

## Cross-references

- `notes/meta_request_to_strategy_strategic_plan_2026-05-21.md`
  (the META strategic plan; canonical Phase 1-5 sequencing)
- `notes/substrate_capability_map.md` v79 (Strategy integration)
- `notes/substrate_capability_map.md` v75 (Bet S/T/U/V/W formal specs)
- `notes/substrate_capability_map.md` v77 (Bet X Research-recommended mechanism)
- `notes/strategy_request_to_exp_dev_betP_R31S1_focused_2026-05-21.md`
  (cycle 67 Bet P+R31 routing; superseded in priority by this Phase 1)

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
