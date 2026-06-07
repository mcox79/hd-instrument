# exp_dev hand-off -- research: substrate-native API design

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_substrate_native_API_design_2026-06-07.md

Pause state: this file is auto-discovered on emergency-refill cycles. Experiments below are
concrete and testable NOW on local substrate infrastructure. No cloud required for the cheap
decisive test.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the implementation.
This file provides anchors + context pointers only.

---

## Anchor Candidates (rank-ordered)

### 1. subscribe() proof-of-concept smoke (Tier-1, CPU, ~1 hr)

Anchor pointer: substrate reactive subscription primitive
Substrate-product reading: write() 100 facts; register subscribe(pattern, threshold=0.80); write
10 matching + 10 non-matching facts; confirm callback fires exactly for matches with merkle_path
included; latency < 100ms on local machine.
Tier hint: Tier-1 CPU smoke (no GPU needed; no cloud; ~50-100 lines Python)
Why now: this is the CHEAP DECISIVE TEST from the research note. Validates whether reactive
subscriptions are buildable on existing substrate write infrastructure before any product
investment. Binary result: tractable or not tractable.

Hard-pass: all matching facts delivered, zero false positives, merkle_path verifies, <100ms.
Hard-fail: any false positive, any merkle_path failure, latency >500ms.

### 2. verify() round-trip test (Tier-1, CPU, ~30 min)

Anchor pointer: Merkle proof round-trip
Substrate-product reading: write() a fact, capture merkle_path from WriteReceipt, call verify()
with that merkle_path against current accumulator_root; confirm grounded=True, confidence matches.
Then modify the fact externally (tamper test) and confirm verify() returns grounded=False.
Tier hint: Tier-1 CPU smoke
Why now: needed before reactive delivery can include merkle_path; establish that verify() is
correct and the tamper-detection works.

### 3. as_of() checkpoint test (Tier-2, CPU, ~2 hrs)

Anchor pointer: bitemporal as-of query
Substrate-product reading: write() N=50 facts; capture accumulator_root checkpoint; write() 50
more facts; call as_of(root=checkpoint, query="X"); confirm only pre-checkpoint facts appear in
results; no post-checkpoint facts leak through.
Tier hint: Tier-2 (more complex; requires accumulator state restoration)
Why now: validates the bitemporal semantics that differentiate substrate from every other vector
DB. Pre-condition: verify() test passes.

### 4. subscribe() + as_of() composition test (Tier-2, CPU, ~3 hrs)

Anchor pointer: reactive + bitemporal composition
Substrate-product reading: register a subscribe(); write N facts; record the accumulator_root at
subscription registration time; call as_of(root=subscription_root, recall(pattern)) and confirm
it returns exactly the same facts that were in the subscription delivery up to that root.
Tier hint: Tier-2; depends on anchors 1 and 3 passing
Why now: this is the "category-defining feature" composition from the research note.

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_native_API_design_2026-06-07.md
- Landscape map: Part 1 of research note (12 AI memory systems with gap analysis)
- Primitive signatures: Part 3 of research note (12 primitives with Python signatures)
- Reactive design: Part 4 of research note (Differential Dataflow literature + scaling analysis)
- Cheap decisive test: Part 0 (CHEAP DECISIVE TEST section) of research note

---

## Contract

exp_dev designs and queues the implementation. Research does not prescribe code.
exp_dev pre-registers hard-pass/hard-fail/middle-band bands per
[[feedback-envelope-expansion-fail-bands]] before queuing.

## Autonomy Declaration

exp_dev has full autonomy over: implementation approach, test harness structure, parameter
choices within the stated anchor scope, queue routing (CPU vs GPU), and sequencing of the 4
anchors above. The research note provides the "what to test" and the "why it matters"; exp_dev
owns the "how."
