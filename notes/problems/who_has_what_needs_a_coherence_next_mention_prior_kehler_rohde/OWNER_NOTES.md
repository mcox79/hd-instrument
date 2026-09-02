---
owner_verdict: DONE
---

SUBMISSION — who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde

STATUS: PARTIAL. The brief's mechanism REFUTED; the real problem partially solved by the correct mechanism; the
wall drilled to its root and the optimization prototyped to its glass-box floor.
Reverify: .venv/Scripts/python.exe verification/test_coref_coherence_prior_on_chain_bucket.py   # 8/8
          .venv/Scripts/python.exe verification/test_coref_faithful_integrator_deltas.py        # 4/4
Ledger clean; deterministic (PYTHONHASHSEED 0/1/42). No hdlab/ written (Q111).

1. REFUTED (+ caught a near-DUPLICATE). The brief's coherence next-mention prior was already owner-DONE dead
   (2026-08-29 `the_reader_has_no_coherence_next_mention_prior`). I reproduced the premise EXACTLY via the parent
   harness (bucket 0.4809 = the brief's 0.481; 0.294 of errors dominated, n=445; 0.995 confident) and confirmed
   the prior stays dead AFTER entity-maintenance (prior-vs-twin +0.0009 NOT_SEP, oracle 6.9%, regresses
   non-dominated; positive control 8/8+8/8 = works, population lacks the cases). => do NOT re-derive; do NOT land
   a coherence prior; consolidate into priority-1.

2. THE IDEAL SOLUTION, RESEARCHED (full-text Kehler-Rohde: it's LEARNED cue integration, not a prior) +
   PROTOTYPED. A glass-box, LM-free conditional-softmax cue-integrator (wiring the EXISTING phi_agreement_keep +
   situation_model_accumulate) recovers the bucket 0.614 -> 0.668, +0.054 [0.008,0.110] CI-sep, shuffled-cue twin
   loses. It is LEARNABLE WITHOUT GOLD (self-supervised +0.060 ~= gold +0.063) and its posterior is CALIBRATED
   (entropy AUC 0.80 -> deferral 0.67->0.80 = the brain's Nref). 9 brain-fidelity deltas researched + prototyped
   (self-supervised + defer CLOSED; recurrent, multiplicative, interference, and the two-stage likelihood×prior
   [argmax-equivalent to flat] HARD-FAIL at our features).

3. WHERE WE LOSE SCORE, DRILLED TO THE ROOT (SCORE_LOSS_DECOMPOSITION). Integrator 0.677, oracle 0.905. Loss =
   9.5% "0 cues right" (external world-knowledge, no-LLM floor) + ~23% ">=1 cue right but wrong". The 23% is NOT
   the combiner (no combiner beats the learned integrator -> integration EXHAUSTED); tracing upstream, the
   grounded cue (the 12-dim individuation representation) is right on 68% of recoverable errors yet weakest
   standalone -> the ENTITY-INDIVIDUATION REPRESENTATION is the root. A representation wall pinned to one organ.

4. OPTIMIZATION PROTOTYPED TO ITS FLOOR. Sharper glass-box individuation reps (TF-IDF individuation = sharpest
   standalone cue 0.641) do NOT beat the integrator (0.677) -- redundant, not orthogonal. => breaking the wall
   needs a RICHER, ORTHOGONAL person-specific individuation code learned from reading = the North Star; glass-box
   enrichment is exhausted.

WHAT REMAINS TO REACH OPTIMAL (consolidated 14-item backlog in SOLVED.md, ranked): #1 the orthogonal
person-specific individuation representation (North Star / p1; THE lever, target = the 0.905 oracle) ; #2 the
9.5% external-knowledge floor ; #3-6 open deltas (recurrent two-pass + asymmetric salience; incremental
commitment; self-supervised learning = an OPEN empirical question; discrete fan nonlinearity) ; #7 coref quality
(the realized gains use gold-nominal grouping) ; #8 land the realized integrator (default-off Q111) ; #9-11
airtight-ness (cross-check the root on the clean bucket; fold the two-stage + optimization tests into the
witnessed core; run the fan-feature test) ; #12 OOD ; #13-14 research follow-ups.

HONEST BOUNDS: the +0.054/+0.060 are marginal, on the animacy-filtered person sub-pool + gold-nominal grouping,
wide CIs; the 0.905 oracle is UNREALIZABLE (needs the answer to gate) so the realizable glass-box ceiling is
~0.67; self-supervised learning is a genuinely OPEN question (a direct negative test exists). The clean, CI-tight
primary result is the refutation + duplicate catch + decomposition.

UNIFYING FINDING: this coref residual, the WSD a_s residual (my previous problem), and priority-1 are ONE wall --
the "which SPECIFIC one" problem, fixed by a rich learned individuation representation, not a coherence prior.

FILES: experiments/{exp_coref_coherence_prior_on_chain_bucket_v1, exp_coref_faithful_integrator_deltas_v1}.py ;
verification/{test_coref_coherence_prior_on_chain_bucket (8/8), test_coref_faithful_integrator_deltas (4/4)}.py ;
notes/problems/<slug>/{SOLVED.md, research_pronoun_resolution_mechanism_2026-09-02.md,
prototype_optimization_individuation_representation.py}. Reuses/WIRES existing organs; AUDIT UPDATE in SOLVED.md.

NEXT: (strategy) consolidate into priority-1; do NOT land a coherence prior; optional default-off Q111 wire of
the realized integrator. (priority-1 North Star) build the orthogonal person-specific individuation code -- this
problem is its instrument (SCORE_LOSS_DECOMPOSITION) + pre-registered target (0.905). Awaiting owner_verdict: DONE.
