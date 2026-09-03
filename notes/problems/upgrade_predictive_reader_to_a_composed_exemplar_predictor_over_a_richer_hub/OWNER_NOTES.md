---
owner_verdict: DONE
---

SOLVED — upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub (opus 4.8 solver)

Full write-up: notes/problems/upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub/
  {SOLVED.md, OWNER_NOTES.md, BRAIN_FIDELITY_AND_ADJACENT_COMPONENTS.md}
Reverify (neither re-runs a landed cell):
  .venv/Scripts/python.exe verification/test_composedhub_signal_loss.py       # 11/11
  .venv/Scripts/python.exe verification/test_composedhub_no_regression.py

RESULT: the ~200-d ATL hub + precision-weighted composed-exemplar predictor beats the 12-d spoke organ
+0.076 MRR held-out (2.4x) AND +0.069 on the LIVE reader (measured brain-faithfully — broad graded
pre-activation, n=12,463), all info-free twins losing CI-sep. Transfers to WiC sense discrimination
+0.027 CI-sep (the shared representation the north-star P1 needs). Fully assembled ideal predictor
(hub + 2-arg composition + Resnik coverage) = 3.0x the organ; components compose. NO hdlab writes; default-off
byte-identical (witnessed).

LAND (strategy, Q111, default-off):
  1. Promote experiments/_composed_hub_predictor.py:HubComposedPredictor → hdlab/; ship the ~200-d hub as a
     static asset (data/frontend_assets/hub_ppmi_svd_200d.pkl) — the SAME asset P1 reads, build once.
  2. situation_reader: add predict_surprisal_hub (default False) → load the hub predictor; wire into the
     anticipation signal (keep the error-flag as-is — it's parser/ambiguity-bound, not representation-bound).
  3. Fold the optimized recipe: 2-bound-argument composition + Resnik/Clark-Weir taxonomic coverage backoff
     (OOV tail 88%→96%) — both BUILT + CI-sep.
  Fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md §2b.

NEXT PROBLEM (not this one): the top-down situation-model prior (north-star P1). The compositional route ends
at ~2 bound arguments (bounded-tuple ceiling, measured); the generative situation model is architecturally
distinct. Plug-in seam documented in IdealBrainFaithfulPredictor.score_pool (situation_prior hook).
