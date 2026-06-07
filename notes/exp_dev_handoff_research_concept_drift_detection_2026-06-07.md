# exp_dev hand-off -- research: concept drift detection + customer-facing alerting

**Filed:** 2026-06-07 by research sub-agent

**Trigger:** 2x drill on concept drift detection via Misra-Gries counters delivered. Three cheap pre-tests are immediately actionable at CPU/local scale. No cloud needed. Research note at: d:/AI/hd-instrument/notes/research_drill_concept_drift_detection_2x_2026-06-07.md

**Pause state:** check data/orchestrator_paused.flag before dispatching. All pre-tests are local/CPU; no GPU queue pressure.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: window sizes, K values, epsilon values, synthetic data parameters, threshold bands, queue choice, anchor names, ETA, smoke profile, full profile.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Misra-Gries window comparison on synthetic drift (Pre-test 1)

**Anchor pointer:** Research note section 8, Pre-test 1. Verified citation: Misra-Gries (1982) + ADWIN (Bifet/Gavalda 2007).

**Substrate-product reading:** Validates that L1 frequency distance D between Misra-Gries counter snapshots is sensitive to moderate topic distribution shifts. This is the core mechanism for v1.1 drift detection. If HARD-FAIL, the entire v1.1 drift detection capability needs a rescue (larger K or finer epsilon). If HARD-PASS (D_drift/D_baseline > 3.0), v1.1 architecture is confirmed.

**Tier hint:** local CPU (no GPU; synthetic data; 30-60 min wall). Highest priority because it gates all downstream drift work.

**Why now:** Drift detection is natively enabled by existing substrate architecture. Pre-test 1 is a 30-60 min CPU run that either confirms the capability or triggers an early rescue. No reason to defer.

---

### Anchor 2: Per-entity emergence/fading detection on 100 stored facts (Pre-test 2)

**Anchor pointer:** Research note section 8, Pre-test 2. Uses existing substrate KB fixture.

**Substrate-product reading:** Validates that the emergence/fading detector (set-difference between top-K lists across windows) has sufficient recall on a small-scale KB. HARD-PASS at recall >= 0.8 for 10 planted entities. HARD-FAIL at recall < 0.5 (threshold tuning rescue needed before v1.1 dashboard launch).

**Tier hint:** local CPU (uses existing fixture; 1 hr wall). Can run in parallel with Anchor 1.

**Why now:** The emergence/fading list is the primary customer-facing signal (most interpretable). Confirming recall before wiring to dashboard is the correct sequencing.

---

### Anchor 3: Drift narrative LLM on synthetic entity list (Pre-test 3)

**Anchor pointer:** Research note section 8, Pre-test 3. Use Pythia-160M or Llama-3.2-1B (whichever is on the local runner).

**Substrate-product reading:** Validates that a small constrained-generation LLM can summarize a top-K entity shift list without hallucinating entity names. HARD-PASS: 0 hallucinated entity names, coherent summary. HARD-FAIL: model hallucinates entity names or contradicts the input list. If HARD-FAIL, the narrative feature is deferred to v2.0 with a larger model.

**Tier hint:** local CPU or remote CPU (small LLM inference; 1 hr wall). Lowest priority of the three; can be scheduled after Anchors 1 and 2 complete.

**Why now:** Drift narrative is a v1.5 feature, but the pre-test is cheap and informs whether the small-LLM path is viable before committing to the integration work.

---

## Context pointers

- Research note (full drill): d:/AI/hd-instrument/notes/research_drill_concept_drift_detection_2x_2026-06-07.md
- Sleep defrag architecture (for Misra-Gries counter access): check hdlab/ for existing counter implementation
- EU AI Act Art 12 compliance context: research note section 4
- Self-improving routing (option k, v1.5+): research note final section
- Prior ADWIN lit-scan source: arxiv.org/pdf/1709.02457 (Bifet/Gavalda ADWIN)
- Federated drift comparison lit: arxiv:2206.00799 (Jothimurugesan et al. 2022)

---

## Contract

exp_dev picks up this hand-off during the next queue-refill cycle when local/CPU capacity is available. All three anchors are CPU/local; no cloud auth needed. Sequencing: Anchor 1 first (gates v1.1 architecture decision), Anchor 2 in parallel, Anchor 3 after 1 and 2 complete.

If Anchor 1 is HARD-FAIL: file a rescue note (larger K, smaller epsilon, or alternative counter structure) before proceeding to Anchor 2.

If Anchor 2 is HARD-FAIL: threshold tuning rescue (lower emergence threshold or larger window) before connecting to dashboard.

If Anchor 3 is HARD-FAIL: narrative feature deferred to v2.0; does not block v1.1 or v1.5 architecture.

---

## Autonomy declaration

exp_dev has full autonomy to:
- Choose K, epsilon, window size, synthetic data parameters
- Name anchors, set envelope bands, choose queue lane
- Sequence Anchors 1 and 2 as parallel or sequential depending on queue state
- Write HARD-PASS / HARD-FAIL bands per the research note thresholds (D_drift/D_baseline > 3.0; emergence recall >= 0.8; 0 hallucinated entity names)
- Defer Anchor 3 if queue is pressured

exp_dev does NOT modify the drift detection architecture spec or the v1.1/v1.5/v2.0 sequencing decision (those belong to orchestrator/strategy).
