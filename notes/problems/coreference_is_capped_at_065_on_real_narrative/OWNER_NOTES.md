---
owner_verdict: DONE
---

SOLVED: coreference_is_capped_at_065_on_real_narrative (SOLVER, opus 4.8)

The ~0.65 cap is broken and diagnosed. On 100 real novels (LitBank, 50 held-out), on the hard cases with ≥2 plausible referents, I replaced the reader's rigid pronoun rule with the brain's actual mechanism — graded cue-based retrieval (softmax over the pinned Lewis-Vasishth/ACT-R activation, reusing the landed graded_competition organ).

Track A (the bar) PASSES: graded 0.775 [0.731, 0.818] vs the incumbent's hard-tiered strict-Cb pick recomputed on the same population 0.603 [0.545, 0.654] — +0.172 CI-separated (half-width 0.031, null-p95 0.031). Info-free twins collapse (random 0.055, shuffled-cue 0.044, both lose by +0.72). Positive control: graded fixes 1073 incumbent errors, breaks 265. The cap's mechanism, measured: the incumbent's rigid subject-first tier scores below plain recency (0.603 < 0.717) — on 2012 error cases it grabs a subject 2.2 sentences too stale, because it lacks the graded memory-fade ACT-R has.

Honesty (a theorem, volunteered): graded ties ACT-R base-level activation (−0.007, NOT_SEP) — graded_competition's MAP-optimality theorem forbids beating the argmax of the same net. The win is over the incumbent's TIER; the unique added value of the graded form is the DISTRIBUTION.

Track B (bonus) passes at the resolver output: the posterior's entropy (softmax gain tuned on DEV for calibration — gain-invariant for argmax, so Track A untouched) predicts its own errors at AUC 0.806 vs the incumbent's own margin signal 0.617 on the same population; deferring the hardest 33% raises kept accuracy 0.775 → 0.894 CI-sep, random-abstain twin flat. Track B item (c) NOT met on the who-did-what downstream — correctly diagnosed as name-clustering + register-capacity bottlenecked, not link-bottlenecked (a mapped adjacency, not a coref failure).

Levers tested and rejected (with numbers): parallelism, extra Centering cues, faithful gender/animacy pre-filter (pool 39.9→39.3, null), ACT-R role-weighting, lexical implicit-causality (decisive frame occurs n=0 in real prose). The ~0.78 structural ceiling is demonstrated; the only remaining accuracy lever is the coherence next-mention prior (the second Kehler-Rohde Bayesian term) = a separate situation-model build.

Adjacent tools flagged to strategy (on-disk evidence): (1) name/entity clustering shatters 65.6% of multi-name characters and caps the whole entity-tracking stack (who-did-what 0.17 vs oracle 0.62) — highest-leverage follow-on; (2) the landed pronoun confidence signal (AUC 0.617) — fixed free by this diff; (3) the LitBank cache stores single head tokens (root cause of #1).

Files: experiments/exp_coref_graded_cue_retrieval_litbank_v1.py, exp_coref_abstain_downstream_whodidwhat_v1.py, exp_coref_agreement_animacy_filter_v1.py + verification/test_coref_graded_cue_retrieval.py (8/8 PASS) + SOLVED.md. Reverify: .venv/Scripts/python.exe verification/test_coref_graded_cue_retrieval.py

Proposed hdlab diff (Q111 — you land it): opt-in run_graded_retrieval in hdlab/coreference_resolver.py (default-off) — ACT-R activation over gn-compatible entities → graded_pick argmax + entropy abstain; beats _pick_strict_cb +0.17 and replaces the 0.617 margin signal with the 0.806 entropy. AUDIT UPDATE: this reverses the small-corpus §2b "cue-based-activation coref pick HARD_FAILED" finding — on real narrative the graded activation wins and the hard tier is the worst arm.

WIP until you set owner_verdict: DONE.
