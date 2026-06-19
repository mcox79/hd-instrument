# Pre-registration: wave14_betB_replay_hB_collateral_v1

**Filed:** 2026-05-25 by exp_dev  
**Trigger:** REPLAY axis locked 🟢 v206; H-B mechanism needs dedicated probe  
**Script:** experiments/exp_wave14_betB_replay_hB_collateral_v1.py  

---

## Hypothesis under test

H-B (interference-reduction): replay reduces interference between successive learning
epochs, protecting the substrate's representational capacity globally -- predict that
HELD-OUT items (items from corpus_A that are NEVER directly replayed) ALSO show higher
retention than the no-replay baseline. This would indicate replay is cleaning up global
representational drift, not merely re-stamping individual patterns.

H-A (consolidation, alternative): only directly replayed items benefit; held-out items
show the same retention as no-replay baseline. Replay = re-presentation only.

---

## Design

Split corpus_A into two equal halves:
- replay_half: items added to the replay pool during Phase B/C
- held_out_half: items from corpus_A that are NEVER in the replay pool

Conditions (each run per seed):
1. REPLAY: Phase B/C with replay_frac=0.5, pool built from replay_half ONLY
2. NO_REPLAY: Phase B/C with replay_frac=0.0 (baseline)

Both conditions train Phase A on the FULL corpus_A (both halves).
Evaluation: measure retention on replay_half test set, held_out_half test set, and
combined test set separately.

Key metrics:
- collateral_lift = retention_held_out (REPLAY cond) - retention_no_replay (NO_REPLAY cond)
- direct_lift = retention_direct_replay - retention_no_replay

---

## Pre-registered thresholds

**HARD PASS (H-B CONFIRMED):**
- collateral_lift >= 0.05 AND direct_lift >= 0.15

**HARD FAIL (H-A ONLY):**
- collateral_lift <= 0.00 AND direct_lift >= 0.15
(held-out items show NO benefit from replay; only direct items benefit)

**INCONCLUSIVE:**
- direct_lift < 0.15 (replay mechanism not active at scale; cannot discriminate)

**MIDDLE POSITIVE:**
- collateral_lift in (0.03, 0.05) AND direct_lift >= 0.15

**MIDDLE NEUTRAL:**
- collateral_lift in (0.00, 0.03) AND direct_lift >= 0.15

---

## Effect size note

From replay_structural_axis_v1: replay lift = 0.163, Cohen's d = 13.33.
Effect size is large at full scale. Smoke scale (N=1024, 1 epoch) may not reproduce
the full lift; smoke verdict may be INCONCLUSIVE; smoke pass criterion is non-null
retention metrics only, not the verdict bands above.

Full run: N=4096, 5 seeds, 5 epochs; expected wall time ~2-4 hours GPU.

---

## Pre-commit cap_map outcome mapping

- HB_HARD_PASS: annotate REPLAY row "H-B interference-reduction CONFIRMED; replay
  protects global substrate capacity, not just directly replayed items; collateral
  lift measured at collateral_lift value"
- HB_HARD_FAIL: annotate REPLAY row "H-A consolidation is the dominant mechanism;
  H-B interference-reduction ruled out; replay benefits only directly presented items"
- HB_MIDDLE_*: annotate with weak-signal note; no strong mechanism claim

---

## Self-test cells (formula verification)

compute_verdict self-test cases (verified in _instrumentation_selftest):
- collateral_lift=0.08, direct_lift=0.16 -> HB_HARD_PASS
- collateral_lift=-0.01, direct_lift=0.16 -> HB_HARD_FAIL
- collateral_lift=0.06, direct_lift=0.01 -> HB_INCONCLUSIVE (direct lift too small)
- collateral_lift=0.04, direct_lift=0.16 -> HB_MIDDLE_POSITIVE
