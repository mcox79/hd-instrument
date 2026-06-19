# exp_dev hand-off -- research: storage unconventional mechanisms 2x drill

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_storage_unconventional_mechanisms_2x_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev reads the research note and
designs the experiments from first principles. No inline design here.

---

## Pause state block

Pause-gated: check data/orchestrator_paused.flag before dispatching.
If paused: file this note for emergency-refill scan; do not dispatch.
If running: these are TIER-A tests (cheap, high information gain) and should be queued
before any existing TIER-B/TIER-C work.

---

## Anchor candidates (rank-ordered)

### 1. ANCHOR: modern-hopfield-n-sweep (TIER-A, <4h CPU)

Anchor pointer: mechanism (1) in research note above.
Substrate-product reading: if N can drop from 65536 to 4096-8192 with the exponential
energy function, W storage drops 64-256x. This is the single largest plausible win.
Tier hint: TIER-A -- run on local CPU, no GPU needed, N is small.
Why now: named as the next-drill candidate in prior research; 2-hour CPU test; cheap
decisive test is pre-registered; must run BEFORE committing 3-6 weeks engineering on
the write-rule derivation.
Pre-reg: HARD-PASS at retrieval accuracy > 0.90 at N=4096, M/N=0.30 with exponential
energy. HARD-FAIL at accuracy < 0.70 at M/N=0.20.

### 2. ANCHOR: predicate-ratio-audit (TIER-A, <1h CPU)

Anchor pointer: mechanism (2) in research note above.
Substrate-product reading: if customer KBs have >= 10 facts per predicate, delta encoding
gives 5-20x compression with near-zero engineering risk. The audit tells us what fraction
of customers are on the structured path.
Tier hint: TIER-A -- local CPU, no model needed, just count predicate/fact ratios in the
KB sample.
Why now: 30-minute test; directly scopes whether mechanism 2 is a product feature or a
niche optimization.
Pre-reg: HARD-PASS at >= 5x compression ratio for >= 60% of facts in structured KB sample.
HARD-FAIL at < 2x for structured KB.

### 3. ANCHOR: min-viable-n-retrieval-sweep (TIER-A, <2h GPU)

Anchor pointer: mechanisms (1) and (7) in research note above.
Substrate-product reading: establishes the empirical floor below which reducing vector
dimension hurts retrieval. Directly determines the ceiling for BOTH mechanism 1 (modern
Hopfield N-reduction) and mechanism 7 (encoder distillation).
Tier hint: TIER-A -- remote GPU, N in {4096, 8192, 16384}, current pseudoinverse write rule.
Why now: without this floor the engineering investment in mechanisms 1 and 7 cannot be
scoped. This is the prerequisite for both.
Pre-reg: HARD-PASS at F1 >= 0.85 at N=8192 (confirms 64x W reduction path is viable).
HARD-FAIL at F1 < 0.70 at N=16384 (closes the N-reduction axis entirely).

---

## Context pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_storage_unconventional_mechanisms_2x_2026-06-07.md
Production architecture lock: d:/AI/hd-instrument/notes/... (MEMORY.md production_architecture_locked_2026-06-07.md)
LoRA-hurts-retrieval finding: MEMORY.md index entry "PRODUCTION ARCHITECTURE LOCKED 2026-06-07"
Sparse-KEY cycle 142 validation: referenced in MEMORY.md production lock note

---

## Contract section

exp_dev reads the research note for full mechanism analysis. This hand-off provides anchor
rank-ordering and tier hints only. exp_dev designs experiment scripts from scratch per
[[feedback-no-experiment-design-in-prompts]]. Formula self-tests required per
[[feedback-strategy-spec-formula-selftests]] for any closed-form in the spec.

## Autonomy declaration

exp_dev has full autonomy on: script design, pre-reg band widths (within the HARD-PASS/
HARD-FAIL thresholds above), routing to CPU vs GPU per [[feedback-route-gpu-vs-cpu-by-
torch-not-N]], and sequencing of the three anchors. Preferred sequence: anchor 2 (30min,
free) -> anchor 3 (2h GPU, establishes floor) -> anchor 1 (2h CPU, tests exponential energy).
