# exp_dev hand-off -- research: Chain 2 bitemporal + GDPR cross-shard coordinator

Filed-by: research sub-agent (Drill 5 FINAL)
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill5_FINAL_2026-06-07.md
Date: 2026-06-07

## Pause state block

Experiments are gated on orchestrator_paused.flag. Read data/orchestrator_paused.flag before
dispatching. If paused: queue the cells below but do not dispatch until resume signal.
Per [[feedback-obey-user-pause-explicitly]]: "looks great" is not a resume signal.

## Per [[feedback-no-experiment-design-in-prompts]]

This file contains anchor candidates and context pointers only. Exp_dev designs the
experiment implementation independently. No implementation code, no parameter values,
no specific result expectations are encoded here.

## Anchor candidates (rank-ordered)

### Anchor 1 (Week 4 gate -- implement first, lowest dependency)
Pointer: Cell 2 from Drill 5 note, Section 9
Substrate-product reading: HMAC key deletion renders all linked facts anonymous; audit log
  integrity must hold under concurrent delete operations.
Tier hint: Tier 2 (CPU-only; pure crypto operations; no GPU needed)
Why-now: Component 8 (HMAC keystore) is the dependency for all erasure functionality;
  it must be validated before Component 9 (coordinator) can be tested.
Pre-reg bands (from note Section 6.1 HP-4 / 6.2 HF-2):
  HARD-PASS: 100% of linked facts fail HMAC verify post-deletion AND audit log entry count == deletion count
  MIDDLE: verify failure rate in [95%, 100%)
  HARD-FAIL: any linked fact passes HMAC verify after key deletion (implies key zeroing failure)

### Anchor 2 (Week 6 gate -- builds on Anchor 1)
Pointer: Cell 1 from Drill 5 note, Section 9
Substrate-product reading: 2PC across 3 shards completes in < 5 sec; coordinator recovery
  after simulated crash completes COMMIT within 60 sec of restart.
Tier hint: Tier 2 (CPU-only; 3-shard in-process simulation; TCP loopback)
Why-now: Component 9 is the final Chain 2 component; validates the cross-shard guarantee
  that closes the GDPR window for Position B jurisdictions.
Pre-reg bands (from note Section 6.1 HP-6 / 6.2 HF-3):
  HARD-PASS: normal 2PC COMMIT < 5 sec AND coordinator recovery COMMIT < 60 sec
  MIDDLE: normal 2PC in [5, 30] sec
  HARD-FAIL: 2PC hung > 30 sec under normal shard availability

### Anchor 3 (cheapest decisive test -- can run standalone, no prior components needed)
Pointer: Section 10 (Cheap decisive test) from Drill 5 note
Substrate-product reading: Three-thread in-process simulation validates filter ordering
  invariant: key_id absence check MUST precede ErasureRecord check; any post-deletion
  read returning fact value indicates filter ordering bug.
Tier hint: Tier 1 (laptop CPU; ~30 min implementation; no infra)
Why-now: Validates the architectural soundness of the Layer 1/Layer 2 ordering before
  committing to full 6-week build. Cheapest possible falsification test.
Pre-reg bands:
  HARD-PASS: zero post-deletion reads return fact value in 1000-trial concurrent loop
  HARD-FAIL: any post-deletion read returns fact value (filter ordering bug)

## Context pointers

Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill5_FINAL_2026-06-07.md
Prior drills (context):
  Drill 4: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill4_2026-06-07.md
  Drill 3: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md
  Drill 2: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill2_2026-06-07.md
  Drill 1: d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill1_2026-06-07.md

## Contract section

- Exp_dev owns implementation decisions (language, library choices, test structure).
- Research note is the spec; exp_dev does NOT need to re-read prior drills unless stuck.
- Anchor 3 is the go/no-go gate: if Anchor 3 HARD-FAILs, re-route to research before
  building Components 6-9.
- Anchor 1 gates Anchor 2: do not run 2PC test until HMAC keystore passes HP-4.

## Autonomy declaration

Exp_dev has full autonomy over: implementation structure, test harness, component ordering
within the week plan, performance optimization choices. Exp_dev does NOT have autonomy over:
anchor pre-reg bands (fixed above), cap_map updates (orchestrator/verdict_handler), or
re-design of the Layer 1/Layer 2/Layer 3 split (research-owned).
