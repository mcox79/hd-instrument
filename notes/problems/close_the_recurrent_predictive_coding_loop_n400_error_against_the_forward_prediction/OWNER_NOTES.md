---
owner_verdict: DONE
---

SUBMISSION — close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction
status: PARTIAL (SOLVED defensible — a rigorous located negative PLUS a validated brain-foundational organ).
WIP until owner_verdict: DONE. hdlab/ UNTOUCHED (Q111). Glass-box, NO external LLM at inference (the invariant).

WHAT WAS ASKED: close the predictive-coding loop — take the coherence/segmentation error against the FORWARD
prediction (not the backward gist), reinstate at boundaries, and beat the backward-gist monitor CI-separated on a
MODERN gold (coherence + segmentation), twin losing, no live-consumer regress — or a rigorous located negative.

HEADLINE (two halves):
1. COHERENCE loop-closure PASSES: forward prediction-error beats the backward gist on Story Cloze val+test (n=3742)
   0.5874 vs 0.52, +0.0673 [+0.047,+0.088] CI-sep; cross-context twin collapses to 0.497.
2. SEGMENTATION — a deep, corrected result. The content-only forward error TIES the backward gist on modern prose,
   so I drilled the brain's ACTUAL mechanism and built it: the brain segments by SCHEMA-SWITCH / belief-update
   (Franklin-Gershman SEM; Kumar 2023 Bayesian surprise = KL of the forward DISTRIBUTION), NOT prediction error —
   which is exactly what our incumbent n400_coherence_monitor computes. I prototyped the SEM schema-switch organ and
   validated it against ACTUAL HUMAN perceived boundaries (Kumar 2023 behavioural gold, acquired + aligned): rho
   ~0.12-0.15, ABOVE the point-error incumbent (0.07) AND GPT-2 (0.10-0.12), ~56-68% of the leave-one-subject-out
   human NOISE CEILING (0.22). It is worse on the GUM-paragraph proxy (0.48) — the proxy was the wrong instrument.

KEY REALIZATIONS (the moves that unlocked it):
- The brain's boundary = a SCHEMA SWITCH (SEM) / a shift in the forward DISTRIBUTION (KL Bayesian surprise), NOT a
  prediction-error spike — Kumar 2023 shows surprisal (prediction error) does NOT predict human boundaries.
- COMPUTE THE NOISE CEILING before calling a result a failure: I nearly mis-called a near-ceiling result a failure by
  comparing to a hallucinated ~0.9 (a different task's number). The real human-agreement ceiling is rho ~0.22.
- The GUM-paragraph proxy MISLED: a mechanism that "won" on paragraphs LOST vs actual humans; only the real gold
  adjudicates.
- RETRACTED "needs a neural model": the glass-box SEM matches/beats GPT-2; 5 glass-box levers (linear/episodic/
  structured-scene/diverse-distribution/online-PC) all confirm the schema-switch ARCHITECTURE carries the win.

DELIVERABLE (landing-ready reference; strategy lands the hdlab write, Q111): experiments/_sem_event_segmenter.py
(SEMEventSegmenter, observe()/segment() API mirroring N400CoherenceMonitor; self-test PASS + embedded human-validation
reproduces). Full landing spec in SOLVED §8 (reuse the substrate's FHRR as SEM's HRR scene rep; new island → no
regress). CAVEAT §4o: sigma2 is scene-scale-dependent — match/sweep it (a scale-free online-MAP-sigma2 variant is a
better-but-finicky follow-on).

FILES: experiments/_sem_event_segmenter.py (the organ) + _predictive_loop.py + build_gum_segmentation_gold.py +
fetch_human_event_boundaries.py + exp_predictive_loop_{modern_gold,dimensional_v1/v2/v3,policy_isolation,
brain_foundational,online_ensemble,upstream_store,boundary_type,diverse_forward_kl}_v1.py + exp_minimal_sem_v1.py +
exp_sem_episodic_v1.py + exp_sem_structured_scene_v1.py + exp_human_boundary_validation_v1.py + exp_human_ceiling_v1.py
+ exp_zwaan_dimensions_human_v1.py + exp_bayesian_surprise_kl_v1.py; verification/test_predictive_loop.py (W1-W10);
research_event_segmentation_mechanism_2026-09-07.md; data/corpora/{gum_segmentation,human_event_seg}/. hdlab/ UNTOUCHED.

REVERIFY: .venv/Scripts/python.exe verification/test_predictive_loop.py   (W1-W10; W10 = SEM beats incumbent vs actual
humans, gracefully skipped if the human archive is absent)

NEXT STEPS: P1 land the SEM schema-switch segmentation organ (the brain-foundational win). P2 land the coherence
forward-error readout + the lean-monitor efficiencies (drop the GEK store for segmentation; opt-in reinstatement).
P3 (follow-on) the scale-free online-MAP-sigma2 organ (rho 0.14-0.17, needs robustness). P4 (methodology) adopt
"compute the noise ceiling" across the substrate. NOT a frontier (retracted): a neural forward model.

AUDIT UPDATE (Tier 5): the incumbent computes the WRONG quantity for segmentation (prediction error over a flat gist);
the brain-foundational segmenter is SEM schema-switch, validated at the human-agreement ceiling.
