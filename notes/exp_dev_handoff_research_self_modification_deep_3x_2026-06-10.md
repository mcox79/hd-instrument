# exp_dev hand-off -- research: self_modification_deep_3x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: research note d:/AI/hd-instrument/notes/research_drill_self_modification_deep_3x_2026-06-10.md

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates and context pointers only. exp_dev designs experiment details autonomously.

---

## Pause State Block

This handoff does NOT require queue space to be cleared before pickup. All proposed anchors are CPU-feasible at Pythia-160M scale. No cloud dispatch anticipated for initial anchors.

---

## Anchor Candidates (Rank-Ordered)

### Anchor 1 (HIGHEST PRIORITY -- Cheap decisive test, ~1 hr CPU)
- Anchor pointer: PERIPHERY-RESTRICTED-WRITE-200
- Substrate-product reading: Partition Pythia-160M parameters into CORE (top-20% by diagonal Fisher) and PERIPHERY (remainder). Apply N=200 sequential sparse writes restricted to PERIPHERY only. Measure recall retention on held-out CORE-anchored facts.
- Tier hint: CPU local, Pythia-160M, ~1 hr
- Why-now: This is the exact cheap decisive test from the research note. It directly tests the K^2/N collapse avoidance hypothesis. No prior substrate anchor covers this. ROME/MEMIT collapse is empirically confirmed; this tests the fix.
- Pre-reg bands: HARD-PASS = >90% retention at N=200; MID = 70-90% (partial, refine partition); HARD-FAIL = <70% or collapse before N=200

### Anchor 2 (HIGH -- BCM adaptive learning rate, ~2 hr CPU)
- Anchor pointer: BCM-ADAPTIVE-LR-PERIPHERY
- Substrate-product reading: Implement BCM sliding threshold as eta(t) = eta_0 / (1 + alpha * EMA(write_volume, t)). Apply to PERIPHERY writes in a sequential edit scenario. Compare against fixed-eta baseline. Measure: retention at N=100, write acceptance rate, oscillation.
- Tier hint: CPU local, Pythia-160M, ~2 hr
- Why-now: Most tractable metaplasticity implementation. Zero architecture change. Plugs directly into existing optimizer. Research note P_deflated=0.50 for this mechanism -- needs empirical test to cross the threshold.
- Pre-reg bands: HARD-PASS = retention improvement >10% over fixed-eta at N=100; MID = 2-10%; HARD-FAIL = <2% improvement or oscillation instability

### Anchor 3 (MEDIUM -- Offline renormalization pass, ~1.5 hr CPU)
- Anchor pointer: OFFLINE-RENORM-SLEEP-PASS
- Substrate-product reading: After every 50 writes, apply global PERIPHERY weight rescaling by factor alpha=0.95, with CORE entries and recently-accessed (last 10 writes) PERIPHERY entries exempted. Measure: write N=200, compare retention profile against no-renorm baseline.
- Tier hint: CPU local, Pythia-160M, ~1.5 hr
- Why-now: Directly maps to the SHY sleep-renormalization mechanism. PMC 2025 two-factor consolidation paper gives the biological grounding. The exemption logic (two-factor tagging) is the key novel element.
- Pre-reg bands: HARD-PASS = retention improvement >15% at N=200 vs no-renorm; MID = 5-15%; HARD-FAIL = <5% or CORE contamination detected

### Anchor 4 (MEDIUM -- KFAC vs diagonal FIM partition quality, ~2 hr CPU)
- Anchor pointer: KFAC-VS-DIAG-FIM-PARTITION
- Substrate-product reading: Compare CORE identification quality using diagonal FIM (EWC-style) vs KFAC approximation. Metric: after CORE-restricted writes at N=100, which partition method better preserves CORE-anchored recall? Use same write set for both.
- Tier hint: CPU local, Pythia-160M, ~2 hr
- Why-now: "EWC Done Right" (2025) shows diagonal FIM has gradient vanishing problems for deeply entangled parameters. CLaRE-ty (2026) confirms that lower-layer parameters have higher entanglement. Testing whether KFAC gives a better CORE boundary is directly actionable and cheap.
- Pre-reg bands: HARD-PASS = KFAC retention >5% better than diagonal at N=100; MID = 0-5%; HARD-FAIL = diagonal matches or beats KFAC (would challenge the entanglement hypothesis)

### Anchor 5 (LOWER -- MoE routing task isolation, ~3 hr CPU)
- Anchor pointer: MOE-SPARSE-ROUTING-TASK-ISOLATION
- Substrate-product reading: Partition PERIPHERY into K=4 sparse expert slots. Route 4 sequential tasks to separate experts using a trainable router. Freeze expert weights after routing stabilizes. Measure: cross-task interference (editing task 2 should not change recall for task 1).
- Tier hint: CPU local, Pythia-160M, ~3 hr (slightly more setup)
- Why-now: SETA framework (arXiv 2601.17616) is already published and tested. This is a near-direct implementation. Addresses ripple-effect problem without Fisher computation overhead.
- Pre-reg bands: HARD-PASS = cross-task interference <5% after 100 edits per task; MID = 5-20%; HARD-FAIL = >20% interference (routing is not isolating)

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_self_modification_deep_3x_2026-06-10.md
- Prior exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md
- Prior research brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Key external papers: arXiv 2401.07453 (ROME/MEMIT collapse), arXiv 2601.17616 (SETA MoE), arXiv 2603.18596 (EWC Done Right)

---

## Contract Section

Research has completed the lit-scan and synthesis. exp_dev owns:
- Experiment design (cell structure, hyperparameters, evaluation protocol)
- Pre-registration per envelope-fail-bands
- Smoke gate before full run
- Queue dispatch and verdict collection
- Cap_map update based on verdicts

Research does NOT specify hyperparameters, optimizer details, or implementation choices. Those are exp_dev's domain per [[feedback-no-experiment-design-in-prompts]].

---

## Autonomy Declaration

exp_dev is authorized to pick any subset of the above anchors, reorder them, or replace them with functionally equivalent anchors derived from the research note, without returning to research for approval. The research note is the authoritative source; this handoff is a convenience summary for queue planning.
