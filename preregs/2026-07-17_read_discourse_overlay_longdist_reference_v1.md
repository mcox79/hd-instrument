# Pre-reg: read_discourse_overlay_longdist_reference_v1

Cell: `experiments/exp_read_discourse_overlay_longdist_reference_v1.py`
Date: 2026-07-17  Author: hdi_exp_dev  Status: ran inline (queues unavailable: local_cpu_queue DOWN, remote paused)

## Question
Redirect from the precision-with-context null (`exp_read_discourse_overlay_context_precision_reopen_v1`, 7e3acab66,
HARD_FAIL: single-relation UD precision is a zero-headroom null, n_cross_sentence_gold=0).
Does a MAINTAINED symbolic entity-state overlay STRUCTURALLY beat a strong recency baseline at
LONG-DISTANCE reference resolution -- pronouns whose true antecedent is beyond the recency window,
where recency structurally fails? Glass-box, NO runtime LLM.

## Corpus (real coref-gold; NOT synthetic -> avoids construction-determined outcome)
LitBank coreference (github.com/dbamman/litbank, coref/conll/*.conll), CC-BY 4.0. 25 literary works.
GOLD entity-mention spans + GOLD coref clusters spanning ~2000-token passages. GOLD mention BOUNDARIES
used (standard "gold mentions" eval); resolver NEVER sees gold coref LINKING. Gold cluster ids used ONLY to
(a) stratify the long-distance subset and (b) score correctness. Cached under data/corpora/litbank_coref_conll/.

## Glass-box mechanism (no spaCy-default / Stanza / torch / transformers)
Fixed pronoun lexicon (reused from precision cell) + title/gendered-noun cue lexicon + surface-head-string
entity grouping + salience arithmetic. Pure stdlib + numpy (bootstrap only).

## Arms (one primary variable = maintained state vs recency; extras isolate mechanism honestly)
- `recency_window` (window K): STRUCTURAL-WALL illustration. 0 on LD subset BY CONSTRUCTION (task-specified
  window-K recency; NOT the can-fail bar).
- `recency_unbounded`: PRIMARY BASELINE (classical Hobbs recency, gender-agreement filtered = steelmanned).
  Most-recent compatible mention, no window. NOT construction-pinned.
- `maintained_overlay`: MECHANISM. Frequency ACCUMULATOR over entities + recency tie-break (centering /
  attentional-state model). No window.
- `freq_only`: ABLATION (pure frequency; guards "is it just predict-the-protagonist?").

## Difficulty-ON
Evaluation subset = gold nearest-antecedent mention-distance > K (antecedent beyond window). K in {3,5,8}
(primary 5). Reported distance split (SHORT n_sd vs LONG n_ld). SHORT subset is the control where recency should win.

## Primary discriminator + bands (K=5; overlay vs recency_unbounded)
- HARD_PASS: delta_ld >= 0.05 AND bootstrap sign-stability(delta>0) >= 0.90 AND overlay precision >=
  recency_unbounded precision - 0.05 (abstention / zero-hallucination guardrail).
- HARD_FAIL: delta_ld <= 0 (recency dominates even at distance -> redirect textbook-comprehension).
- MIDDLE_BAND: 0 < delta_ld < 0.05.
NOTE: freq_only is a decomposition control; overlay ~ freq_only => win driven by frequency accumulation.

## Design-gate compliance (USER 2026-07-17)
1. REAL baseline: recency_unbounded is gender-steelmanned Hobbs recency, attempt-rate 1.0 (NOT abstain-all/strawman).
2. CAN-FAIL: mechanism arm CAN score ~0 (the earlier exp(-lam*dist) overlay variant scored 0.00 on LD in smoke).
   HARD_FAIL reachable + first-class.
3. DIFFICULTY-ON: LD subset = antecedent-distance > K; SHORT control reported separately.
4. ONE variable: same corpus, same gold mentions, same compatibility filter, same abstention; arms differ only
   in the scoring/persistence rule.

## Gates
crlb_n/a (symbolic accuracy metric; reachability shown empirically: recency low on LD leaves headroom).
final_metrics_atomicity: tmp_replace. arms_differ_verified (hash per-target picks). cardinality_ok.
except SystemExit: raise before except Exception (no BaseException / bare except). F.5 nondeterminism: CLEAN
(np.random.default_rng fixed seed; sorted; no hash()/list(set)). calibration: fixed lexicon + fixed decay (no
tuned-for-PASS knob; gender lexicon steelmans the BASELINE, not the mechanism).

## VET focus recommended
Book-clustered resampling (target-level bootstrap overstates robustness given within-book clustering);
mechanism decomposition (freq_only vs overlay); the SHORT/LONG crossover is the load-bearing evidence.
