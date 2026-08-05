# Deep VET — comprehension organ vs the brain (2026-08-05)

USER-requested deep brain-fidelity VET of the components we're actively working with, run as 4 parallel
per-component drills (each: READ THE CODE -> name the exact brain circuit's SHAPE+POSITION+METRIC -> hunt the
SLIGHT divergence that means success vs failure). All load-bearing code claims Director-VERIFIED on disk
(greps below). Sonnet drills; Opus synthesis. Triggered alongside the landed real-coref gate (commit 5cd27f385).

## HEADLINE (both meta-patterns converge across all 4 VETs)

**META-PATTERN 1 - we built a FEEDFORWARD/LOCAL pipeline where the brain runs a RECURRENT/TOP-DOWN-GATED loop.**
Every organ computes LOCALLY per clause from local cues and hands off a flat result. NONE is gated by the
running situation model's top-down prediction/bias. The brain's comprehension loop is: situation model
(DMN/mPFC) supplies top-down bias -> IFG/pMTG biased-competition selects the context-licensed sense/role ->
hippocampal CA3 RECOLLECTION binds/resolves the antecedent -> prediction-error updates the model. Our pipeline
severs that loop at four points simultaneously (each disk-verified):
- the situation-model top-down bias argument is hard-coded `None` (context_grounded_valence.py:141);
- the recollection coref arm is switched OFF in favor of the recency/familiarity arm (situation_reader.py:420);
- goal/affect are re-derived locally per clause and thrown away - no per-protagonist STATE persists;
- the forward-prediction organ is islanded (zero hdlab consumers).

**META-PATTERN 2 - this is largely a WIRING crisis, not a mechanism crisis (GOOD NEWS - cheaper fixes).**
The brain-faithful pieces mostly EXIST and several are already self-test-validated; they are switched to the
wrong mode, or never wired to each other. The single most important correction to our mental model: the
PROVEN goal-owner integrator (12/12 on the fair instrument) HAS NEVER BEEN FED A SINGLE REAL EVENT the
situation reader extracts - there is no wire. "Healthy integrator degrades on real prose" was never happening;
the wire doesn't exist.

## THE 6 SLIGHT DIFFERENCES (ranked by leverage x certainty; all code-verified on disk)

| # | Component | The slight difference that matters | Fix (size) | Verdict / conf |
|---|---|---|---|---|
| 1 | Goal-owner + situation-model maintenance [D] | The proven integrator takes hand-typed GO_ROLES; SituationReader emits a DIFFERENT vocab (EXPERIENCER/AGENT/PATIENT + HARM/HELP/NA) and NO path translates. Worse: goal/affect never ACCUMULATE per protagonist - only coref IDENTITY persists (TrackedEntity). A goal set in S1 is invisible when S3 needs the goal-holder. AccumulateRegister/GoalOutcomeRegister EXIST but SituationReader never instantiates them. | Persistent GoalOutcomeRegister keyed by coref-cluster + a `situation_events_to_go_roles` adapter -> feed the proven integrator real prose for the FIRST time (medium) | STRUCTURAL-GAP (wiring); 0.72-0.75 |
| 2 | Coreference tie-break [B] | Production coref passes `centrality_mode="recency"` (perirhinal FAMILIARITY) overriding the function's own `"event_role"` default (hippocampal CA3 RECOLLECTION). The module's OWN self-test proves recency picks the WRONG antecedent and event_role the RIGHT one when they diverge. They only diverge AT RANGE -> passes local-strong, caps cross-sentence. Selection problem, NOT candidate-gen or maintenance. | Flip situation_reader.py:420 recency -> event_role (ONE line, already built + self-test-validated) then re-measure | SLIGHT-DIVERGENCE; 0.55 |
| 3 | Sense-selection + grounded valence [C] | `combine_biased_competition(gov_type, event_type, None)` at line 141 hard-codes the discourse/situation-bias slot to `None` on every call. Choke point for BOTH word-sense selection AND valence completeness (stage3 valuation consumes stage2 output). This is the self-admitted necessary-not-sufficient stage-1; the peanut-in-love discourse-inversion case predicts it fails on exactly our target constructions. Plumbing (`situation_type_for_prior` in _v2) already exists + is imported. | Wire a real situation_type through the 3rd arg (small) - CAVEAT: verify it wasn't left `None` because it underperformed when tried | STRUCTURAL-GAP (self-admitted); 0.5 |
| 4 | Event extraction: hood + segmentation [A] | Wrong SHAPE at TWO stages. (a) Event-HOOD = static frame-dict membership with NO argument-realization confirmation (find_frame_verbs) -> over-generates on frame-bearing nominals/adjuncts (n_pred 61->113, P 0.180->0.159). (b) Segmentation = overgenerate-then-FILTER with a flat binary OR-of-3-booleans (is_boundary_gate), where the brain SOURCE-gates event-hood via a continuous RELATIVE prediction-error. The landed real-coref gate confirms: gated recall 0.294 FALLS BELOW ungated 0.324; the flat-OR drops true NON-BOUNDARY continuation events. | Collapse the two stages: gate event-hood by the frame's own argument-realization requirement AT generation time + make role assignment frame-conditioned, instead of over-generate-then-filter (larger) | STRUCTURAL-GAP; 0.4 |
| 5 | Thematic-role for KNOWN verbs [C] | frame_primary_role returns frame_slot_role UNCONDITIONALLY for in-vocab verbs (line 434) - no context check AT ALL; the override stage was removed WHOLESALE after a prior perceptron regression, not narrowed. Cannot flip a discourse-licensed non-default role (object-experiencer verbs, personification, non-canonical animacy). (The OOV path is by contrast the MOST brain-faithful - graded construction-cue induction, subj 0.833.) | Reintroduce the override as a CONDITIONAL, evidence-gated re-weighting (fire only on strong discourse/construction cue), not a hard re-rank (medium) | SLIGHT-DIVERGENCE; 0.55 |
| 6 | Predictive coding [D] | predict->residual->gated_write is internally forward-model-shaped (right ORDER) but has ZERO hdlab consumers - completely islanded. The reading loop has NO predict-then-observe step; every disambiguation is from local cues, never a prior expectation (no N400-analog). | Predict next protagonist-state from the accumulated register (needs #1) BEFORE extracting the next sentence; route residual as a disambiguation prior - for CONTINUOUS affect/valence only. CAVEAT: frame_induction.py:27 already (correctly) ruled the continuous residual WRONG-SHAPE for the DISCRETE frame/role decision - do NOT wire it there. | STRUCTURAL-GAP (islanded); 0.65 |

## PLUS a doc mislabel to correct [B]
The brain-audit (brain_audit_our_components_status.md) calls `coreference_resolver.py` the "strongest,
genuinely-WIRED" organ - but that is NOT the module feeding event extraction. Production
(situation_reader.py:412-420) uses a DIFFERENT lineage: EventCentralityReader (event_centrality_coref.py) ->
SuppressReader (coref_distractor_suppress.py) -> CorefReader/WorkingOverlay (coref.py). The "strongest organ"
verdict has been read onto the wrong module. Correct the component map.

## DISK VERIFICATION (Director, load-bearing claims)
- situation_reader.py:420 `centrality_mode="recency"`; event_centrality_coref.py:200 default `"event_role"`. CONFIRMED.
- context_grounded_valence.py:141 3rd arg `None`; _v2 imported line 52. CONFIRMED.
- predictive_coding: no functional import in hdlab/ (only a comment in char_positional_encoder.py:34 and an
  explicit NOT-this in frame_induction.py:27). CONFIRMED islanded.
- directed_goal_outcome_score / GoalOutcomeRegister referenced only in goal_owner_select.py; NOT in
  situation_reader.py; AccumulateRegister absent from situation_reader.py. CONFIRMED unwired.

## CORRECTED ROADMAP (this VET reorders the component-health roadmap)
The old #1 (grind event-extraction precision in isolation) is a hard multi-dependency slog. This VET says the
higher-leverage + higher-certainty moves are the WIRING fixes that connect already-proven organs the
brain-faithful way, THEN an end-to-end measurement:
1. **WIRE THE LOOP (cheap, high-certainty):** (a) flip coref to event_role [#2, 1 line]; (b) build the
   persistent per-protagonist GoalOutcomeRegister + GO_ROLES adapter and feed the proven integrator real prose
   [#1]; (c) wire the situation-bias 3rd arg [#3, after the history check].
2. **MEASURE END-TO-END on goal_owner_fair_v1.jsonl** - this converts "integrator proven in isolation" into
   the assembly-proof the plan (Section 4) wants, and tells us HOW MUCH extraction actually caps the real
   organ (the isolated F1~0.23 may over- OR under-state the end-to-end impact).
3. **THEN the SHAPE fixes** gated by what step 2 exposes: A's collapse-two-stages for extraction; C's
   conditional thematic-role override; D's forward predictive prior for affect (not discrete roles).

HONEST NOTE: wiring the integrator to real prose (1b) will INHERIT the upstream extraction/role error rate -
it will NOT reproduce 12/12 on real prose. That's the point: it produces the first HONEST end-to-end number
and localizes the true cap, instead of grinding an isolated-F1 that may not be the binding constraint.

## CORRECTION to VET-D (Director VET-the-VET, disk-verified 2026-08-05, self-drive cycle)
VET-D claimed "the proven integrator has NEVER been fed a single real event the reader extracts." That is
TOO STRONG. exp_component5_wired_endtoend_v1.py (landed, MIDDLE_BAND, N=23) already feeds
directed_goal_outcome_score Component-3's REAL GOAL-typing (frame_primary_role, the exact fn situation_reader
wires) and reproduces outcome_binding_accuracy=1.0 (recency floor 0.0435, beats_recency=True, scramble
collapse=True, gold_vs_real_delta=0.0). So the GOAL-typing half of the wire EXISTS and is GREEN. The PRECISE
remaining gap (code-verified): (i) cluster_ids in that cell come from TOY resolvers (RecencyEntityResolver /
ContentMatchResolver, method subject_entity) — NOT the production coref organ; (ii) outcome-valence is still
lexicon-typed (declared out of C3 scope); (iii) it runs on the N=23 recency bank, NOT the fully-fair
goal_owner_fair_v1.jsonl (all-4-baselines-0.0); (iv) real SituationReader.read() is not used (CoNLL
constraint). CONVERGENCE BONUS: that cell's RecencyEntityResolver-vs-ContentMatchResolver A/B maps EXACTLY
onto VET-B's coref recency->event_role flip. So step-1 is NOT a from-scratch adapter build — it is: swap the
toy resolvers for the REAL production coref organ (recency vs event_role arms) + run on the fair
explicit_psych subset. DISPATCHED (hdi_exp_dev, this cycle) as exactly that cell. This is why VET-the-VET is a
standing rule: a single grep-based "no wire" claim missed a landed green partial-wire cited in the promoted
module's own docstring.
