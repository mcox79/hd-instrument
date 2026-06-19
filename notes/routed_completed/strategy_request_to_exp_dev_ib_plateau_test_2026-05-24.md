# strategy_request_to_exp_dev: IB-phase-transition plateau falsifier (candidate iv)

**Filed.** 2026-05-24 by Research (deep-drill alt-theoretical-homes).
**Trigger.** Research-drill candidate (iv) Information-Bottleneck phase transitions identified as second-highest-P alternative theoretical home for substrate's three-plateau retention (P=0.42 after lit-scan calibration penalty). Pred-4-orthogonal; Pred-4 verdict still pending.
**Pause-flag check.** Orchestrator must verify `data/orchestrator_paused.flag` absent before queue_add. At file-write time: ABSENT.
**Source note.** notes/research_alternative_theoretical_homes_2026-05-24.md (see Top-2 deep drill, candidate iv).

---

## TASK

Test whether substrate's three retention plateaus (0.94 / 0.74 / 0.60) emerge from Information-Bottleneck phase transitions (Tishby-Zaslavsky framework, Wu-Fischer-Tegmark 2020 categorical version). IB framework predicts plateau-COUNT equals the number of distinguishable class-clusters in the joint (corpus_byte, target) distribution — so varying the number of training corpora K should produce a discrete-plateau-count response: K=1 → 1 plateau, K=2 → 2 plateaus, K=3 → 3 plateaus, etc.

## WHY (without designing the experiment)

If candidate (iv) fits, the plateaus have a clean information-theoretic interpretation (compression-rate ceilings at categorical task-similarity boundaries) — separate physics-framework-independent home. Together with candidate (v) cascade-plateau test (filed separately), these are the two leading alternatives if 1-RSB is dead.

Both can ship in parallel with Pred-4. Both are cheap CPU drills.

## CONTRACT

Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds before queue_add. Per envelope-fail-bands rule:

- **HARD-PASS:** K-sweep ∈ {1, 2, 3, 4, 5, 8} yields plateau-count ∈ {1, 2, 3, 4, 5, ≤6} that monotonically tracks K (counts may saturate at substrate's compression-rate ceiling). Plateau-internal-variance < 0.02 within each plateau. **Bonus:** the K=3 case reproduces the empirical 0.94/0.74/0.60 spacing (within 0.03 of each height).
- **HARD-FAIL:** plateau-count does NOT track K — e.g., all K values give same plateau structure, OR plateau-count is random-looking, OR retention is smooth-continuous across K with no discrete-step structure.
- **MIDDLE-BAND:** weak tracking (rank-correlation > 0.5 but not monotone), OR plateau-count tracks K only for some K values.

Self-test cells required per [[feedback-strategy-spec-formula-selftests]] — exp_dev derives the predicted plateau-count formula from Wu-Fischer-Tegmark 2020 and verifies 3-4 (input K, expected count) pairs before coding.

## AUTONOMY

Exp_dev owns: anchor names, K-sweep grid (the {1,2,3,4,5,8} values are illustrative; exp_dev may refine for cost), seed count, N choice, queue choice (CPU vs remote-CPU), ETA, threshold numerical bounds, self-test design, all script-level decisions.

Per [[feedback-no-experiment-design-in-prompts]]: this is TASK + WHY + CONTRACT + AUTONOMY only.

## Falsifier cost estimate (informational)

Research's drill estimated ~20-40 min CPU per K value, so total ~2-4 CPU-hours across K-sweep. Could be parallelized across seeds.

## Pred-4 orthogonality

This test sweeps K (number of training corpora), not M (bytes per stage), and uses an information-theoretic readout (plateau-count vs K) rather than a hysteresis-gap readout. Pred-4-orthogonal. **If both this and Pred-4 pass, two-framework triangulation strengthens substrate-physics framing back up. If both fail, framework reliability drops further and substrate becomes "useful analogy" tier.**

## Routing

To orchestrator: dispatch via routing_handler / orchestrator-routing skill. exp_dev_handoff file filed by exp_dev once design set.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
