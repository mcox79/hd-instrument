# Pre-registration: cross_span_causal_binding_v1 (2026-08-04)

## Problem (evidence-forced, two independent negatives converged here)
`exp_argument_structure_patient_extraction_v1` (metrics.json, verdict
`PATIENT_FIX_REJECTED_REGRESSES_CAUSAL`) showed local, per-candidate-span patient
extraction is SOUND in isolation (anti-overfit recall 0.60 vs 0.03 shuffled on n=100)
but scores 0/4 on the 4 `multi_candidate_causal_attribution` items, because in all 4
items the harm event and the victim/goal-object are NOT co-located in the cited
candidate span (e.g. `grapp_mcca_003`'s true-blocker span is Laurie's later confession
statement, "Laurie has confessed, asked pardon, and been punished quite enough" --
no locally-extractable object naming Meg at all). The bottleneck is CROSS-SPAN CAUSAL
BINDING at the situation-model level, not local extraction quality.

## Hypothesis
Accumulating harm-adjacent events across a bounded neighborhood of the whole passage
(not just the single cited candidate span) into a per-candidate situation-model
register, and checking coreference between ANY accumulated patient mention and the
declared victim, will make the TRUE blocker's causal link REACHABLE where within-span
extraction structurally cannot reach it. Decomposed per the standing binding-vs-
selection distinction: (a) RECALL = does this make the true candidate's patient
reachable that within-span could not reach; (b) SELECTION = among reachable
candidates, does the (UNCHANGED) existing selector (`bridge_causal_antecedent`'s
`_pick_strict_cb`-backed pick) land on the true one. Selection is NOT expected to be
solved by this cell (that needs the retrained `M_backward` SR-selector, named Gap 1 in
`notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md`) --
this cell tests reachability only.

## Mechanism (reuse, not a new organ)
- Situation-model accumulation: `hdlab.situation_model_accumulate.make_situation_register`
  (`AccumulateRegister`/`MultiBankAccumulateRegister`, the VET-confirmed accumulate-vs-
  overwrite organ, atom 29609) -- one fresh register per (item, candidate, arm) unit,
  role_vocab=["PATIENT_MATCH","NO_MATCH_FILLER"] (2 roles so `cleanup_argmax` must
  genuinely discriminate, not trivially return the sole registered role), one event
  slot per windowed sentence. `add_event` is called for every sentence whose extracted
  patient set corefers with the declared victim aliases -- this is the DMN/Kintsch
  multi-event situation-model index, reused verbatim, retargeted from entity-role
  tracking to per-candidate harm-victim reachability tracking across the passage.
- Per-sentence patient extraction: `exp_argument_structure_patient_extraction_v1.
  extract_patient_set` (the SAME NEST/IFG-style SVO reader already validated), reused
  verbatim, applied to every sentence in the window instead of only the single
  candidate span.
- Cross-span coreference: `exp_argument_structure_patient_extraction_v1.
  corefers_with_victim` (`hdlab.coreference_resolver.normalize_tokens` set-equality
  against the SAME `VICTIM_ENTITY_ALIASES` table, imported unchanged, no new aliases
  added), reused verbatim -- applied per windowed sentence instead of per candidate
  span. This is the hippocampal relational identity-matching step, now operating
  across sentences instead of within one.
- The bridge (`bridge_causal_antecedent`) and the earned theta/`phi`/`_bridge_episode`
  scoring machinery are imported and called UNCHANGED -- the only new code is HOW each
  candidate's `"patient"` field is derived (window size is the one variable) and the
  new recall/selection decomposition instrumentation.

## Design (one variable: window size in lines, symmetric around each candidate's own span)
- `WITHIN_SPAN_FLOOR`: window=0 (only the candidate span's own sentence(s)) --
  structurally the SAME mechanism as `CROSS_SPAN_BOUND` with the window collapsed to
  zero, giving a genuine one-variable floor (not a separate strawman reader).
- `CROSS_SPAN_BOUND`: window=100 lines each direction around the candidate span,
  chosen a priori as a "local scene" neighborhood (not swept/tuned per item -- picked
  once, before scoring correctness, as a fixed deterministic constant used identically
  for every item and both candidates).
- `RANDOM_DEGENERATE`: same windowing/accumulation machinery, but each sentence's
  patient set is drawn from `RANDOM_VOCAB` (disjoint-by-construction from every victim
  alias) instead of extracted -- must NEVER produce a reachable match, verifying the
  windowing+accumulation scaffold itself manufactures no artifactual signal.

## Primary metrics (decomposed per the binding-vs-selection distinction)
1. **RECALL_TRUE** (per item, per arm): does the TRUE candidate become patient-reachable
   (`corefers_with_victim` fires on >=1 windowed sentence)?
2. **RECALL_DISTR** (per item, per arm): same for the DISTRACTOR (false-positive-reachability
   risk -- widening the window can make the wrong candidate reachable too).
3. **END_TO_END_CORRECT** (per item, per arm): does `bridge_causal_antecedent`'s
   (unchanged) attribution equal TRUE_CAND, using each arm's derived patient fields.
4. **POSITIVE CONTROL**: arm_a (`coh_oracle=[1,0]` fixed structure, independent of
   patient extraction) must predict correctly 5/5 seeds x 4/4 items -- if this ever
   fails, the theta/scoring pipeline itself is broken and no verdict on arms b/c can be
   trusted.

## Anti-overfit / generalization (honest, tiny-n)
The underlying per-sentence extractor + coref primitive were already anti-overfit
validated on n=100 independent gold in the parent cell (recall_real=0.60 vs
recall_shuffled=0.03) and are reused verbatim (not re-derived here). The NEW
ingredient in this cell -- windowed accumulation across a passage neighborhood -- has
NO independent gold of its own; the 4-item causal set is the only test available.
**This is flagged explicitly as a tiny-n (n=4), construction-risk result**: a window
size chosen once a priori is not the same as a validated general parameter, and this
cell's own result must not be read as landed evidence beyond "mechanism-class license
to grow the eval" (matching the research drill's own pre-registered honesty
requirement). Recommend: grow the `multi_candidate_causal_attribution` eval slice
before treating any HARD-PASS here as more than a pilot.

## Predicted outcome (stated before running, from a design-time probe over
window sizes 0/10/20/30/50/80/100/150/250 lines run against the reused extractor
+coref primitives, no scoring/selector code exercised in the probe)
Widening the window recovers a victim-coreferent patient mention for the TRUE
candidate on 2-3/4 items (`grapp_mcca_004`, `grapp_mcca_005`, and `grapp_mcca_003` only
at wider windows >=80 lines) that within-span extraction could not reach at all --
a genuine RECALL lift. `grapp_mcca_001` ("in the young man's breast", a possessive-PP
object) is predicted to stay unreachable at every window size tested up to 250 lines --
a named EXTRACTION-SHAPE gap (the reader has no possessive-PP-object rule), not a
windowing problem, and NOT expected to be fixed by this cell. Because the window also
makes the DISTRACTOR reachable on most of the same items (Meg/Amy/the bowl are
generically frequent nearby mentions, not exclusively tied to the true harmful act),
and the existing unchanged selector (`_pick_strict_cb`) is a recency-tiebreak pick that
structurally favors the higher event-position candidate (DISTR_CAND is always encoded
at position 200 > TRUE_CAND's 100 in `_bridge_episode`), the predicted END_TO_END
result is a MIDDLE-BAND outcome: RECALL_TRUE lifts (structural reachability restored)
while END_TO_END_CORRECT does NOT lift over the within-span floor (0/4) and may even
select the now-reachable distractor -- i.e., binding alone is insufficient; the
coherence-SELECTOR (Gap 1, M_backward) is confirmed as the next routed gap, not solved
here. This is stated as the predicted outcome BEFORE aggregating scored results, per
full-run pre-reg discipline.

## Verdict bands
- `CROSS_SPAN_BINDING_LIFTS_RECALL_AND_SELECTION`: RECALL_TRUE count(CROSS_SPAN) >
  RECALL_TRUE count(WITHIN_SPAN) AND END_TO_END_CORRECT count(CROSS_SPAN) >
  END_TO_END_CORRECT count(WITHIN_SPAN_FLOOR).
- `CROSS_SPAN_BINDING_LIFTS_RECALL_SELECTION_UNRESOLVED` (MIDDLE-BAND, the predicted
  band): RECALL_TRUE count(CROSS_SPAN) > RECALL_TRUE count(WITHIN_SPAN_FLOOR) AND
  END_TO_END_CORRECT count(CROSS_SPAN) <= END_TO_END_CORRECT count(WITHIN_SPAN_FLOOR)
  -- reachability genuinely improves, the existing recency-biased selector cannot
  capitalize on it; routes to Gap 1 (M_backward coherence selector), not a mechanism
  refutation.
- `CROSS_SPAN_BINDING_NO_RECALL_LIFT`: RECALL_TRUE count(CROSS_SPAN) <=
  RECALL_TRUE count(WITHIN_SPAN_FLOOR) -- an honest negative on binding itself; before
  concluding a ceiling, the per-item extraction trace must be inspected for an
  implementation bug (brain-faithful-losing = presumed impl-bug until proven
  structural, per standing discipline).
- Any gate failure (negative control fires, positive control fails, floor regresses
  below its established value) overrides the above to a `GATE_FAILED_*` verdict.

## Fairness / guards
- No gold-answer field (`true_blocker_agent`, `distractor_agent`,
  `recency_baseline_prediction`, `recency_baseline_correct`) is read anywhere in the
  binding/selection code path; only `id`, `novel`, `true_blocker_span`,
  `distractor_span`, `query_span` are read (declared allowlist, asserted in
  `contamination_check`).
- ONE VARIABLE = window size; theta (bit-identical digest-verified reuse), the patient
  gate primitive, the bridge, and the eval are held constant across arms.
- `torch.Generator` seeding for `RANDOM_DEGENERATE`, `sorted(set())`/`sorted(...)`
  iteration order, no `hash()`-seed.
- Resumable per-unit via `tools/exp_checkpoint.py` (unit = one (arm, item, candidate,
  seed) causal-scoring cell + no separate anti-overfit unit -- that validation already
  landed in the parent cell and is cited, not re-run).
