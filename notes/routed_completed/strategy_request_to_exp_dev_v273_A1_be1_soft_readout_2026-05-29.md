# exp_dev hand-off — A1 BE-1 soft-readout precision sweep (RUN FIRST)

**Filed:** 2026-05-29 by strategy_scribe (cap_map v272 -> v273 annotation trigger).

**RUN-FIRST FLAG: Ship this anchor before any other anchor in the v273 overnight-refill batch.**

**Trigger:** User explicit directive — A1 is the single most important run in the overnight batch because it is the cheapest test that directly addresses the v272 strategic over-claim on BE-1 cost-advantage.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent).

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHOR + POINTER only. exp_dev decides all implementation details: anchor name, N, M, sweep parameters, threshold bands, queue choice, ETA, smoke profile.

---

## Why A1 is the highest-priority run

**v272 problem:** The BE-1 precision-floor sweep (6 anchors: FP32/FP16/INT8/INT4/INT2/INT1) showed quantization-INSENSITIVE behavior: INT1 binary scored EQUAL TO or BETTER THAN FP32 on isolation metric. This is physics-impossible if W-magnitude were the operative path. It means the argmax isolation test is dominated by rank (codebook-vs-W argmax structure) not magnitude. The 32x cost-advantage claim was NOT validated by that test design.

**A1 fix:** Replace argmax readout with softmax(beta=32) readout. Softmax readout explicitly uses W-magnitude in its scoring: at low precision (INT1/INT2), W entries are coarser, so the softmax energy landscape is flatter, and isolation scores should degrade measurably. If precision-sensitivity appears under softmax readout, W-magnitude IS operative and the cost-advantage claim has a path to validation.

**Strategic stakes:** If A1 shows precision-sensitivity under softmax readout:
- BE-1 cost-advantage narrative re-validates at the readout level
- A2-A4 probe how far that sensitivity propagates (retrieval / TCFT / multi-hop)
- Strategic 32x cost narrative can be honestly defended

If A1 also shows quantization-insensitivity under softmax readout:
- v272 finding was not an artifact of argmax
- W-magnitude is genuinely not operative in isolation test
- Honest retraction of 32x cost-advantage at this operating envelope
- Strategic pivot to "substrate is quantization-robust by physics" (different but honest framing)

Either outcome is decisive. No ambiguity. That is why it ships first.

---

## Anchor task

**Cluster:** A — KF-2 BE-1 W-MAGNITUDE-OPERATIVE PROBES
**Position in cluster:** A1 (HIGHEST PRIORITY)
**Position in overnight batch:** FIRST anchor to ship

**Task:** Run the BE-1 edit-isolation test using softmax(beta=32) readout instead of argmax, across a precision sweep spanning FP32 down to INT1. Measure whether isolation scores are sensitive to weight precision under softmax readout.

**Why softmax readout makes W-magnitude operative:** argmax is magnitude-insensitive (only rank matters); softmax energy is magnitude-dependent (W-entry magnitude directly scales the softmax denominator). At low precision, W entries are quantized to coarser values, shrinking the energy gap between correct and distractor memories. This should be measurable as degraded isolation scores.

**User size hint:** approximately half GPU day; 6 precision levels x 3 seeds. exp_dev decides exact parameters.

---

## Context pointers

- `notes/substrate_capability_map.md` v272 — KF-2 BE-1 cost-advantage AT-RISK annotation (row annotation: "v272 BE-1 precision-floor...W-magnitude-operative test required")
- `notes/strategy_decisions_2026-05-29.md` — v272 verdict 4-9 decision narrative (130th LABEL-VS-HONEST STRATEGIC_INTERPRETATION_OVER_CLAIM)
- `notes/strategy_request_to_exp_dev_v273_overnight_refill_user_strategy_2026-05-29.md` — full overnight batch with all 5 clusters
- Prior BE-1 scripts for reference (exp_kf2_be1_*.py family in experiments/) — note: those used argmax; A1 needs softmax modification

---

## Contract

- Pre-register HARD-PASS + HARD-FAIL + middle-band thresholds BEFORE smoke per [[feedback-envelope-expansion-fail-bands]].
  - HARD-PASS candidate framing: isolation score shows monotone degradation with decreasing precision (FP32 > FP16 > INT8 > ... > INT1) — confirms W-magnitude operative.
  - HARD-FAIL candidate framing: isolation score flat or inverted across precision levels (replicates v272 argmax result under softmax) — confirms W-magnitude NOT operative even with magnitude-sensitive readout.
  - Middle-band: partial sensitivity (degrades at INT2/INT1 but not INT4/INT8) — narrows the precision floor.
  - exp_dev sets exact numerical thresholds.
- Self-test softmax(beta=32) formula before coding per [[feedback-strategy-spec-formula-selftests]].
- Smoke at reduced scale first; FULL at 3+ seeds on smoke clearance.
- Per-experiment `--timeout` required per [[feedback-per-experiment-timeout-required]].
- POST-SHIP REMOTE VERIFY per [[feedback-ship-name-collision]].
- PROT-018: anchor name `_n<N>` suffix must match config.N.
- Kerdock check: if N=8192, verify even log2(N) (or route to N=4096/N=16384).
- status_log entry after ship with `plain_language` + `importance='HIGH'`.

## Autonomy declaration

exp_dev decides: anchor name, N, M, K, beta parameter for softmax, seed count, exact threshold bands, queue choice, ETA, smoke profile, FULL profile. The only constraint: ship A1 before any other anchor in the v273 overnight batch. After A1 is shipped and in the queue, proceed to remaining TIER 1 anchors (A2, B1, C1, C2) in parallel.

---

## Filed by

strategy_scribe sub-agent (cap_map v272 -> v273 annotation trigger), 2026-05-29.
This file is the single-anchor split-out of A1. Full overnight batch is at:
`notes/strategy_request_to_exp_dev_v273_overnight_refill_user_strategy_2026-05-29.md`

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
