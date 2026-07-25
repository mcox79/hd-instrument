# Pre-reg: arc_selection_answer_conditioned_contrastive_v1

**Date:** 2026-07-25  **Author:** exp_dev (agent)  **Contract:** INLINE-LOCAL foreground-to-completion; no push/remote-persist; ASCII-only; deterministic.

## Question
Does conditioning fact-SELECTION on EACH candidate answer (Q(x)C_i) and scoring by DIFFERENTIAL
support (how much a fact bridges Q->THIS choice MORE than its rivals) break the gold-vs-lure symmetry
that answer-AGNOSTIC selection provably cannot? The fair re-test
(exp_concept_featural_enrichment_v2) proved richer CONTENT raises topic-cosine SYMMETRICALLY across the
4 choices, so a read-out that never compares across choices cannot break the asymmetric gold-vs-lure
decision. The brain-drill (research_drill_answer_conditioned_selection_biology_2026-07-25.md) shows human
MC-reasoning is answer-CONDITIONED (PFC goal-biased competitive retrieval / illness-script differential
diagnosis / multi-alternative DDM-LCA / likelihood-ratio norm / ECHO inhibitory contrast).

## ONE variable = answer-AGNOSTIC vs answer-CONDITIONED SELECTION
INVARIANTS held FIXED (imported UNCHANGED): the WIDE re-retrieval pool (recall@100=0.69,
mr.reformulate_seeds / _rownorm_scores over ppr), the bind+bundle COMBINER (agg.aggregate 'bundle'),
retrieval, and the stratified TRAIN/TEST split (learned._split_train_test). Every combiner arm feeds the
SAME K_SEL=4 facts to the SAME combiner with the SAME answer-agnostic q_rel weight -- the ONLY thing that
differs is WHICH facts the selection stage picks.

## Metric (place / shape / metric of the gap, per drill)
- conditioned relevance (SUBSTRATE BIND, conjunctive): s_i(f) = <sign(fact_f)(x)sign(stem), sign(choice_i)>/N.
  Binding fact with the question and dotting with the bipolar choice is the substrate-native conjunctive
  read-out (drill's "conjunction for free"; TESTED here, not assumed).
- differential support (CONTRAST across choices): d_i(f) = s_i(f) - max_{j!=i} s_j(f)  (max-margin /
  likelihood-ratio-flavored, competitively normalized). disc(f) = max_i d_i(f).
- flat variant (robustness): s_flat_i(f)=cos(fact_f, choice_only_i) over the already-question-retrieved
  pool (pool provides question-grounding; choice-only differential provides answer-discrimination).

## Arms (can-fail, one-variable spine A_GEO -> COND_NONCONTRAST -> B_CONDITIONED)
- A_AGNOSTIC       -- current pipeline: 29545 flat learned relevance -> top-K_SEL -> combiner.
                      HARNESS ANCHOR: insample precision ~=0.1865, TEST Challenge ~=0.3663.
- A_AGNOSTIC_GEO   -- geometric question-relevance top-K_SEL (matched no-train scoring class for B).
- COND_NONCONTRAST -- bind-conditioned max_i s_i(f) top-K_SEL (conditioning WITHOUT the cross-choice
                      contrast; isolates whether CONTRAST -- not just conditioning -- breaks symmetry).
- B_CONDITIONED    -- bind-conditioned CONTRAST disc(f) top-K_SEL -> combiner. PRIMARY TEST ARM.
- B_COND_FLAT      -- flat-encoding conditioned CONTRAST -> combiner (robustness / representation check).
- B_DIRECT         -- literal DDM winner: answer = argmax_i max_f d_i(f) (per-choice competition, NO
                      combiner). The task's "choice whose best differential-support fact wins."
- MISCONDITIONED   -- bind-conditioned CONTRAST but with choices SHUFFLED (roll by 1) at conditioning
                      time; combiner uses TRUE choices. MUST-FAIL: proves it is the RIGHT conditioning.
- RND              -- random K_SEL -> combiner. MUST-FAIL.
- ORACLE           -- gold facts -> combiner. CEILING ~0.71.

## Bands (a priori)
PRIMARY = end-to-end TEST Challenge accuracy, B_CONDITIONED vs A_AGNOSTIC (0.3663), toward oracle ~0.71.
- HARD_PASS: primary conditioned arm TEST Challenge >= A + 0.05 AND its TEST sel_gold_precision > A's
  AND McNemar p < 0.05 AND MISCONDITIONED lift <= 0.02 AND RND lift <= 0.02 AND
  B_CONDITIONED >= COND_NONCONTRAST (contrast does not hurt vs conditioning-alone).
- MIDDLE_BAND: primary lift in [+0.02, +0.05) OR precision/mechanism real but end-to-end not significant;
  MISCONDITIONED still does not help. Real-but-partial -> report + residual diagnosis.
- HARD_FAIL: primary lift < +0.02 -> answer-conditioning ~= answer-agnostic. Report STRAIGHT. Residual
  diagnosis: (a) gold_in_pool_frac (retrieval reach), (b) gold_points_correct_frac = among test-chal Qs
  with gold in pool, does the gold fact's differential put it at the CORRECT choice? Low -> content-
  resolution wall (thin GloVe cannot express the fine feature) -> perceptual grounding. High but
  end-to-end fails -> combiner/aggregation.
- Integrity: arms_differ (>=5 distinct pick vectors); A_AGNOSTIC anchor regression WARN if
  |insample-0.1865|>0.03 or |chal-0.3663|>0.03; AG headroom (A_chal < 0.95).

## Compute architecture
mixed CPU: batched GloVe encode (store + questions + choices) + scipy sparse batched PPR (2 passes,
UNCHANGED) + numpy bipolar-bind conditioned scoring (elementwise sign product + matmul, cheap) +
per-question contrast reduction + ONE glass-box logreg train for A_AGNOSTIC only + UNCHANGED combiner.
Wall target < 5 min (ref cells 100-126s @ 987 Q / 9720 facts). No GPU needed (matmuls small).
Discriminator (geometric contrast) is a fixed per-question quantity; MORE dims = LESS noise -> survives
scale by construction. Smoke runs at FULL n_dim=2048 (only question-limit reduced) so the discriminator
fires at the real geometry.

## Schema-vet fields
storage=sharded; final_metrics_atomicity=tmp_replace; start_marker+crash_diagnostic+heartbeat present;
except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException/bare except);
arms_differ_verified at smoke; baseline_in_band + AG-guard on A_AGNOSTIC; calibration_check=
default_ok_for_this_regime (all scoring geometric+author-set a priori; A_AGNOSTIC learner hyperparams
inherited from 29545; NOT tuned to force a win; miscond+random must-fail controls present);
crlb_n/a="geometric selection, no learned noise floor; contrast is deterministic per pool";
real_code_path: self_test builds REAL SemanticHDEncoder + REAL pool encode + REAL conditioned scoring +
UNCHANGED combiner + PLANTED discriminator (a choice-specific fact is selected by the contrast and the
DDM winner points at the right choice; misconditioning breaks it; an on-topic-to-all fact is NOT
selected). progress_logging=line_buffered_stdout. NO tuning to force a win; clean HARD_FAIL fully
reportable.
