# Alt3 Placeholder: PAC-Bayes KL-Posterior Retention Predictor

**Filed:** 2026-05-24 by exp_dev sub-agent (current cycle)
**Status:** DEFERRED — blocked on R-PRIME-1 derivation
**Recipient:** exp_dev (when R-PRIME-1 PAC-Bayes posterior-over-W KL derivation lands)

---

## What this is

Alt3 of the three alternative predictor families to replace R-PRIME-3 (task-pair
geometry, HARD-FAIL r^2=0.103). R-PRIME-3 elimination eliminated continuous-geometry
prediction but NOT the broader prediction question.

Alt3 hypothesis: compute PAC-Bayes-derived KL term for each corpus pair
**NOT input-data KL — posterior-over-W KL** between Phase-A and Phase-B trained models.
Test retention against THIS KL specifically.

This is distinct from:
- Alt1 (discrete shift-class predictor — SHIPPED this cycle, results pending)
- Alt2 (W-internal signatures from Phase-A — SHIPPED this cycle, results pending)
- R-PRIME-1 (PAC-Bayes floor theoretical drill — SHIPPED at v195, HARD-FAIL on floor)

Alt3 is the APPLIED use of the R-PRIME-1 derivation: if the KL between posterior
distributions over W (not just input data) correlates with retention, this is a
geometry-free mechanism for retention prediction.

---

## What is needed before shipping

R-PRIME-1 PAC-Bayes KL derivation (formal derivation of posterior-over-W KL between
Phase-A and Phase-B W distributions, as a function of corpus-pair properties):
- Filed as `notes/research_R_PRIME_directions_2026-05-24.md` Section R-PRIME-1
- R-PRIME-1 floor HARD-FAIL (v195) was for the CONSERVATIVE bound, not the
  posterior-over-W KL itself
- The derivation needs to specify: how to compute KL(P_W^A || P_W^B) from
  observable W matrices without full Bayesian posterior

**Trigger for Alt3 ship:** when research delivers R-PRIME-1 posterior-over-W KL
derivation in `notes/research_R_PRIME_1_kl_derivation_*.md` (or equivalent).

---

## Experiment design sketch (for when trigger lands)

Script: `exp_wave14_betB_pac_bayes_kl_predictor_v1.py`

Method:
1. Run Phase-A and Phase-B for each of 5 corpus pairs (can reuse Alt2's runs)
2. Compute KL(P_W^A || P_W^B) using the derivation from R-PRIME-1 research delivery
   - Expected form: KL(W_A || W_B) ≈ ||W_A - W_B||_F^2 / (2 sigma^2) for Gaussian
     posterior approximation, or spectral-divergence form
3. Correlate this per-pair KL against measured retention_A
4. Test r^2 vs geometry (spectral distance) and vs Alt1/Alt2 signatures

HARD-PASS: r^2 >= 0.50 AND r^2 significantly above spectral distance baseline
HARD-FAIL: r^2 < 0.20 (no information from posterior-KL)

Queue: overnight_queue (GPU, ~same as Alt2)
ETA: ~2-3h (shares Phase-A/B runs with Alt2 infrastructure)

---

## Sequencing notes

Per [[feedback-rescue-sketch-first-sequencing]]:
- Alt1 (cheapest CPU re-analysis) shipped first
- Alt2 (GPU internal-signature pilot) shipped second
- Alt3 (needs derivation) deferred — this placeholder

When R-PRIME-1 derivation lands, exp_dev should:
1. Read the derivation
2. Implement the KL computation
3. Ship with same infrastructure as Alt2 (reuse train_w_with_replay)

---

## Cross-references

- R-PRIME-3 HARD-FAIL: cap_map v193
- Alt1 shipped: exp_wave14_betB_shift_class_predictor_v1 (2026-05-24)
- Alt2 shipped: exp_wave14_betB_W_internal_signature_v1 (2026-05-24)
- R-PRIME-1 derivation request: notes/research_R_PRIME_directions_2026-05-24.md

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
