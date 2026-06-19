# exp_dev hand-off -- research: immune DEEPER 3x (OAS + cross-reactive memory + vaccine pretraining)

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file hands TASK + WHY + CONTRACT + AUTONOMY.
It does NOT specify anchor names, sweep grids, threshold formulas, queue choice, or pre-committed
cap_map decisions. Exp_dev designs all of that.

---

## Pause State

No pause flag check required at hand-off write time. Exp_dev must check
data/orchestrator_paused.flag before dispatching any experiment.

---

## Why This Hand-off Is Urgent

The DEEPER 3x drill identified that the substrate has a structural analog of Original Antigenic Sin
(OAS) that is UNMITIGATED today. Seeded bindings (loaded during the initial KB construction phase)
accumulate confidence from validation-phase query traffic before deployment. Post-deployment new
bindings start at minimum confidence. When a post-deployment binding contradicts a seeded binding,
the adversarial ranking (Extension 2 from the 5x note) will systematically DEPRIORITIZE the correct
post-deployment correction because its confidence is lower than the entrenched seeded binding.

This is not a hypothetical risk -- it is a structural consequence of the current confidence
accumulation design and the confidence-weighted adversarial triage. No experiment has tested it.
If OAS bias is CONFIRMED (HARD-PASS on Prediction 1), then the substrate is systematically
biased against self-correction for outdated seeded facts, which is a production reliability problem.

The mitigation (two-tier confidence with age-weighted decay) is cheap to implement and test.

---

## Anchor Candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): OAS bias existence test
**Why now:** No experiment has tested whether seeded bindings resist correction by post-deployment
bindings. If the bias exists, it affects every production KB with a seeding window -- which is all
of them. This is a prerequisite for knowing whether Extensions 2-5 from the 5x note are safe to
deploy as designed.
**Substrate-product reading:** A substrate with unmitigated OAS will systematically preserve
outdated seeded facts against correct updates, degrading KB accuracy over time. This is a
production reliability claim that must be characterized before the product is deployed.
**Tier hint:** Local CPU; synthetic KB (1000 seeded facts, 100 post-deployment corrections with
known ground truth); ~1-2 hours. Pythia-160M pre-test applies per feedback-drill-pretest-required.
**Research context pointer:** notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
Section 3.1 (OAS mechanism) + Section 3.2 (substrate analog) + Prediction 1 (HARD-PASS/HARD-FAIL).

### Anchor 2: OAS mitigation -- confidence decay parameter sweep
**Why now:** If Anchor 1 confirms OAS bias exists, the decay alpha parameter needs empirical
calibration. Theory predicts alpha in [0.90, 0.98] should work, but the correct value depends on
KB size, query frequency distribution, and defrag cycle length -- all substrate-specific. The
pretest here should sweep alpha across the predicted range on the synthetic KB from Anchor 1.
**Substrate-product reading:** The memory freshness SLA product promise ("KB self-corrects within
N days of an update") requires knowing the alpha-to-correction-latency mapping.
**Tier hint:** Local CPU; extends Anchor 1 synthetic setup with alpha sweep; ~2-3 hours.
**Research context pointer:** notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
Section 3.3 (mitigation formulas) + Prediction 2 (HARD-PASS/HARD-FAIL).

### Anchor 3: Burial depth invariant -- load-bearing vs surface binding cross-variant recall
**Why now:** The burial-depth principle from bnAb structural biology predicts that bindings aligned
with the centroid of a concept cluster (load-bearing, present across paraphrases) will exhibit
significantly higher cross-variant recall than surface-specific bindings. This prediction has
never been tested on the substrate. If confirmed (Prediction 3 HARD-PASS), it justifies a
load-bearing binding classification feature and determines which bindings should be exempt from
the OAS confidence decay.
**Substrate-product reading:** Cross-variant recall (paraphrase robustness) is a key quality
metric for production KB retrieval. Knowing which bindings generalize vs specialize enables
a customer-facing "load-bearing fact" classification feature.
**Tier hint:** Local CPU; ~1-2 hours; 10 concept clusters x 10 surface paraphrase variants;
no new math beyond existing cosine similarity infrastructure.
**Research context pointer:** notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
Section 3.4 (burial depth principle) + Prediction 3 (HARD-PASS/HARD-FAIL).

### Anchor 4: Two-speed adversarial memory -- slow fingerprint day-1 vs day-7 TPR
**Why now:** The trained innate immunity analog (slow adversarial fingerprint updated hourly)
predicts that adversarial TPR improves monotonically from day 1 to day 7 as the fingerprint
accumulates contradiction pattern signal. This is a differentiating product claim ("gets better
without training") that has never been tested. Cheapest test: synthetic 7-day simulation with
controlled contradiction injection rate and slow fingerprint update.
**Substrate-product reading:** Day-30 adversarial performance is a product differentiator if
it can be demonstrated to improve without labeled training data. The day-1 vs day-7 delta is
the minimum viable demonstration.
**Tier hint:** Local CPU; ~2-4 hours; simulation not real deployment data; synthetic contradiction
stream with known TPR ground truth.
**Research context pointer:** notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
Section 3.5 (two-speed memory formalization) + Prediction 4 (HARD-PASS/HARD-FAIL).

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
- Prior 5x immune note: d:/AI/hd-instrument/notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md
- Substrate capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Adversarial mode HP confirmation: cycle 167 (adversarial contradiction detection HP)
- Concept drift detection HP: cycle 170

---

## Contract

Research hands off four anchor candidates rank-ordered by urgency and P_deflated. Exp_dev
owns ALL design decisions: anchor naming, sweep parameters, pre-test gates, queue routing,
pre-registration thresholds, and cap_map impact assessment. Research has pre-registered
HARD-PASS and HARD-FAIL bands in the research note; exp_dev should respect those as the
empirical decision criteria.

OAS bias existence test (Anchor 1) is the prerequisite for Anchor 2 and 3. If Anchor 1 returns
HARD-FAIL (no OAS bias), then Anchor 2 is unnecessary. Exp_dev decides whether to sequence
or batch.

## Autonomy Declaration

Exp_dev has full autonomy on: anchor implementation, test scale, pre-test design, queue
selection, YAML construction, smoke interpretation, and cap_map annotation. Exp_dev must NOT
make strategic decisions about which capabilities to deprecate or promote based solely on
these results -- those go to verdict_handler and orchestrator.
