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

## STEP-1c CAVEAT RESOLVED (Director, disk-verified same cycle)
VET-C flagged: maybe the situation-bias 3rd arg (context_grounded_valence.py:141 = None) was left off because
it UNDERPERFORMED. RESOLVED = NO, it's a PROVEN win. exp_bridge1_twostage_event_situation_v2 is HARD_PASS:
discourse-decisive subset C_two_stage=1.000 vs C_governor=0.500 (chance) vs C_scrambled_discourse=0.650
(lift_C=0.350, scramble collapses); event-differing B_two_stage=1.000 vs B_governor=0.500 (lift_B=0.417);
generalizes Bgen/Cgen=1.000; NO regression on local-sufficient (A 0.962=0.962). The mechanism
(situation_type_for_prior -> combine_biased_competition 3rd arg, _v2 lines 207-222) works and has real
anti-artifact controls. It is `None` in production ONLY because the promotion (commit 4cd8b4f24) was scoped to
the ANIMACY axis and did not carry the discourse stage over -- a scope decision, not underperformance. So step
1c is GREEN; the real work is SOURCING situation_type from the running situation model at runtime (in _v2 it's
a threat/benign lexicon over prior text; production must derive it from the accumulated situation-model
affect/goal state) -- an integration, not a new mechanism.

## LANDED: real-coref goal-owner end-to-end (commit f3f88f752, exp_c5_real_coref_endtoend_v1, Director per-axis VET on disk)
The dispatched cell landed and VALIDATES VET-B's flip END-TO-END. On the explicit_psych recency-trap DIVERGENT
subset (N=18, 3 seeds, deterministic): coref centrality_mode **event_role = 0.8889 (16/18)** vs
**recency = 0.0 (0/18)**; gated positional baselines recency=0.0 + nearest_subject=0.0 both BEATEN; scramble
collapses non-vacuously (0.0 vs 0.8889); twin-control 1.0. CLEAN DECOMPOSITION: n_goal_present_c3=16 and
accuracy=16/18 -> when Component-3 supplies the GOAL, event_role coref + the proven integrator get the owner
right **16/16 (100%)**; the ONLY 2 misses are items where frame_primary_role failed to detect GOAL on OOV
psych verbs ("hoped"/"meant") -> the entire residual cap is the OOV GOAL-typing sub-problem (3b), NOT coref
and NOT the integrator. HONEST CAVEATS (VET as hard as a negative): N=18 small (MIDDLE_BAND, not HARD_PASS);
first_mention/majority baselines =1.0 NOT gated on this recency-trap subset (bank-structural confound; the
primacy-trap bank defeats those, out of scope) so "beats all 4 positional" is FALSE - it beats the 2
subset-relevant traps; outcome-valence still lexicon-typed (declared scope). NET: VET-B's event_role flip is
empirically validated where it matters; PROMOTION to production dispatched (certification-gated); the frontier
narrows to OOV GOAL-typing (3b) + the primacy-trap subset + real outcome-valence.

## 3b DIAGNOSIS (Director, disk-verified) - the OOV GOAL-typing cap UNIFIES with the action_implied extension
The 2/18 misses (t03, t12) are "Beth/Jo HOPED TO win/finish..." - PURPOSE-INFINITIVAL intention constructions
(subj + hope/mean + to-VP = goal-holder), MISLABELED verb_type=explicit_psych in goal_owner_fair_v1. They miss
because situation_reader's wired OOV induction (_INDUCED_SUBJ_HYP, situation_reader.py:359-360) is a
psych-EXPERIENCER-construction model (has_scomp etc.) that correctly ABSTAINS on infinitival-intention verbs ->
AGENT -> no GOAL. But the purpose-infinitival "X V...to VP -> goal" construction is EXACTLY what the already-built
generative goal-typing (exp_c5_generative_goal_typing_action_frame_v1, 8/10, verb-independent) detects. So 3b is
NOT a new OOV psych-verb induction - it is: WIRE the generative purpose-infinitival goal-detector into the
GOAL-detection path (currently EXPERIENCER-only). ONE build closes BOTH (i) these explicit_psych infinitival
misses AND (ii) the action_implied subset (23 items, same construction). This is a WIRE-DON'T-ISLAND of a proven
capability, not a new mechanism. Minor data note: t03/t12's verb_type tag is imprecise ("hope to VP" is
intention/infinitival, not psych-EXPERIENCER) - relabel when convenient, non-blocking. NEXT BUILD (after the
certification-gated coref promotion lands): wire generative purpose-infinitival goal-typing -> GOAL-detection,
re-measure on BOTH the explicit_psych OOV-miss items and the action_implied subset of goal_owner_fair_v1.

## LANDED-2: purpose-infinitival wire (commit 78294a2c6, exp_c5_real_coref_endtoend_purpose_infinitival_v1, Director per-axis disk-VET)
CLEAN WIN on the target subset: **action_implied divergent (N=10) 0.0 -> 1.0 (10/10)** end-to-end, scramble
collapses non-vacuously (1.0->0.0), gated positional baselines cleared (recency/nearest_subject=0.0),
deterministic 3 seeds. The proven purpose-infinitival goal-typer, wired into GOAL-detection, solves the entire
action_implied subset end-to-end (was 0/10 with EXPERIENCER-only typing). PARTIAL on explicit_psych: unchanged
16/18 (t03/t12 NOT recovered) - a PRE-REGISTERED, precisely-diagnosed COVERAGE GAP between two
individually-correct mechanisms: the purpose-infinitival detector's CONTROL_VERB_STOP deliberately EXCLUDES
desiderative-governing verbs (hope/want/wish) assuming C3's EXPERIENCER lexicon catches them, but C3 has an OOV
gap on "hoped" -> "Beth hoped to win" falls between both (action_frame_feats==[] AND c3_has_desire=False). No
over-firing (scramble non-vacuous both subsets, arms_differ verified). Overall MIDDLE_BAND by worse-of-subsets.

FIX ROUTING for t03/t12 (brain-foundational, do-the-right-thing not the easy OR-hack): the goal reading of
"X hoped/wanted to VP" comes from a DESIDERATIVE/intention verb + the infinitival-purpose construction,
verb-class-conditioned. The principled fix = PARTITION control verbs into DESIDERATIVE/intention
(hope/want/wish/mean/plan/intend/aim/long/yearn -> pass, fire GOAL via the construction even when C3 is OOV) vs
ASPECTUAL/implicative (began/tried/failed/managed/started -> keep stopping, NOT goals). This SUPPLIES a small
innate-core desire-verb class (defensible: core ~6yo desire vocabulary, SUPPLY not induce) and keeps the
construction-detector verb-independent WITHIN the desiderative class, WITHOUT mislabeling want/hope as
EXPERIENCER (they are desirers, not emotion-undergoers). Deeper frontier (separate): LEARN the
desiderative-vs-aspectual partition for fully-OOV control verbs via the OOV induction (missing-LEARNING route).
DISPATCHED (this cycle) as the desiderative-partition fix. NET after LANDED-2: action_implied SOLVED end-to-end;
explicit_psych at 16/18 with a 2-item gap that the desiderative partition closes.

## LANDED-3 (MILESTONE): desiderative/aspectual partition (commit 5da76bf34, exp_c5_desiderative_aspectual_partition_goal_typing_v1, Director per-axis disk-VET incl the precision probe)
CLEAN HARD_PASS on the target + precision guard spotless. explicit_psych divergent (N=18):
c3_only 0.8889 -> partitioned **1.0 (18/18)**, t03/t12 BOTH RECOVERED (partitioned arm-digest DIFFERS from the
original arm = a real behavioral change, not a no-op). action_implied divergent (N=10): held **1.0 (10/10)**,
no regression. PRECISION GUARD (the whole risk): aspectual-infinitival probe n=7 (began/started/tried/failed/
managed/ceased/continued) false_goal_count_max=0 across 3 seeds, owner-selection matches c3_only on EVERY item
-> the desiderative partition fires GOAL on desideratives WITHOUT over-firing on aspectuals. Scramble collapses
non-vacuous both subsets; gated positional baselines (recency/nearest_subject=0.0) beaten both.

### MILESTONE STATE OF THE GOAL-OWNER ORGAN (end of this arc)
The goal-owner organ is now MEASURED END-TO-END ON REAL COREF at **18/18 explicit_psych + 10/10 action_implied**
across BOTH construction types on the fair instrument, with: real production coref (event_role, promoted
a9e873ab0), real GOAL-typing (frame_primary_role EXPERIENCER + purpose-infinitival construction + desiderative
partition), gated positional baselines beaten, scramble non-vacuous, precision guard clean. From
"proven-in-isolation-on-hand-typed-roles" -> "measured end-to-end on real coref across both constructions."
HONEST REMAINING CAVEATS: (1) N small (18+10 divergent, MIDDLE_BAND by small-N convention); (2) first_mention/
majority baselines NOT gated on these RECENCY-trap subsets -> the PRIMACY-trap subset (which defeats those) is
UNTESTED end-to-end = the next fairness milestone; (3) outcome-valence still LEXICON-typed; (4) WIRE-DON'T-
ISLAND: the purpose-infinitival + desiderative-partition goal-typing live in EXPERIMENT cells, NOT promoted to
production hdlab (parameterized) -> a PRODUCTION PROMOTION of the combined goal-typing (into situation_reader's
C3 GOAL-typing path, certification-gated) is the pending lock-in. NEXT (prose recommendation to USER): promote
the goal-typing to production (lock the gain) + run the primacy-trap subset end-to-end (complete the fairness
picture / earn "beats all 4 baselines"); then real outcome-valence typing.

## LANDED-4 (NEGATIVE, brain-foundational drill + VET-the-VET): primacy-trap end-to-end HARD_FAIL = SEVERED-TOP-DOWN-LOOP exposed (commit 43e942ca0, exp_c5_primacy_trap_endtoend_promoted_organ_v1)
Ran the promoted goal_typing organ + event_role coref on the 20 primacy-trap items (p01-p20). RESULT: 0/20
(0/12 explicit_psych, 0/8 action_implied), scramble VACUOUS (no unscrambled gain to collapse), HARD_FAIL
exactly as pre-registered. VET on disk confirms 0/20 + scramble-vacuous.
**VET-THE-VET (decisive, checked before propagating): the goal-owner MECHANISM is NOT at fault.** The ISOLATED
primacy cell exp_c5_fair_goal_owner_primacy_v1 scores SYSTEM=0.6 (explicit 12/12, action_implied 0/8), all 4
baselines=0.0, scramble non-vacuous = INSTRUMENT_VALID_FULLY_FAIR_PRIMACY_TRAP. So the integrator DOES beat
primacy in isolation. The 0/20 end-to-end is a CANDIDATE-GENERATION failure, not a mechanism failure.
MECHANISM (SHAPE/POSITION/METRIC):
- ISOLATED candidate generator = "roster entity with most explicit-name mentions" -> on primacy surfaces the
  OWNER (protagonist, mentioned first/most) as the content candidate -> candidates DIVERGE -> goal-coherence
  (directed_goal_outcome_score) picks the owner -> 12/12 explicit.
- END-TO-END candidate generator = real event_role coref resolving the outcome PRONOUN -> on primacy resolves
  "she" to the recent/event-central FOIL -> both candidates bit-identical on the outcome slot -> no divergence
  -> integrator can't redirect -> 0/20. GOAL-typing fires correctly (20/20); it is moot because the owner is
  never a candidate.
- ROOT: event_role coref uses EVENT-CENTRALITY (bottom-up), which ALIGNS with the goal-holder on recency-trap
  (owner is event-central -> 18/18) but DIVERGES on primacy-trap (foil is event-central, owner is goal-holder
  -> 0/20). The brain resolves the outcome pronoun/attribution via GOAL-COHERENCE as a TOP-DOWN BIAS
  (coherence-over-recency), at the point of resolution. Our goal-coherence is applied POST-coref on coref's
  already-collapsed candidate set. = EXACTLY the deep-VET severed-top-down-loop thesis, now proven by a can-fail.
ROUTE (rule b): NOT missing-LEARNING (mechanism exists + proven 12/12). WIRING/ARCHITECTURE gap: the outcome-
owner CANDIDATE GENERATION must surface the goal-holder -> enumerate the entity set (from entity-clustering
coref, the wired-STRONG capability) as candidate outcome-owners and let directed_goal_outcome_score select by
goal-coherence, INSTEAD of depending on event_role coref's bottom-up outcome-pronoun resolution. This is the
brain's top-down-goal-biased outcome attribution; proven primacy-robust in isolation (12/12 explicit).
RE-SCOPES the milestone (honest): the 18/18+10/10 recency-trap end-to-end is REAL but coref-pronoun-resolution-
dependent (works where event-centrality happens to align with the goal-holder); primacy-trap exposes that
dependence. FIX (dispatched): end-to-end with roster-enumerated goal-coherence candidate generation + promoted
goal-typing, re-measured on primacy (expect explicit_psych ~12/12 + action_implied improved via the promoted
purpose-infinitival typing that the isolated cell lacked) AND re-confirm recency-trap stays 18/18+10/10.

## LANDED-5 (MILESTONE + VET-as-hard-as-negative found 3c): goal-coherence candidate-gen HARD_PASS (commit b1b1ce460, exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1, Director per-axis disk-VET incl gold-free code read)
FIX WORKS. Primacy: explicit 12/12 (1.0) + action_implied 8/8 (1.0), ALL 4 baselines=0.0, beats_all_four=True,
scramble non-vacuous. Recency-trap HELD: explicit 18/18 (1.0) + action_implied 9/10 (0.9). Net vs the 0/20
primacy HARD_FAIL: +20 primacy, -1 recency = the goal-owner organ is now **47/48 on the fully-fair instrument**
(both trap types, both constructions), GOLD-FREE (candidate set = roster.keys() [cast metadata]; outcome-slot
subject = the proposed candidate; GOAL-typing structural via promoted hdlab/goal_typing; gold_outcome_owner read
ONLY in scoring -- Director read enumerate_and_select/build_candidate_role_seq on disk to confirm; this cell is
MORE fair than the isolated cell, which had a gold-owner leak [owner=item['owner'] to decide GOAL-bearing] that
this one removes). Agent's mid-run scramble-vacuity gate change VET'd = CORRECT (compares recency-trap scramble
vs the non-trivial {recency,nearest_subject} reference, not the trivially-tied first_mention/majority).

### VET-AS-HARD-AS-NEGATIVE found the 3c gap (the self-drive brief's named frontier)
The 1 recency miss (t24_tom_boat_foil_sid) = a GENUINE tie: directed_goal_outcome_score returns {tom:1.0, sid:1.0}
(instrumented on disk) because BOTH Tom ("to mend the boat") and Sid ("to fetch the rope") hold purpose-infinitival
goals, so the score (which checks goal-PRESENCE) ties -> sorted-order picks 'sid' (wrong). Full-instrument scope
(inline count): 2 genuine ties (t23, t24); only t24 wrong (t23 won the alphabetical tiebreak by luck). BRAIN-DRILL
(SHAPE/POS/METRIC): the brain binds the outcome to the goal it RESOLVES via CONTENT/CAUSAL coherence (Trabasso:
Tom's goal is ABOUT the boat; the outcome is the boat SANK -> shared referent + causal goal-blocked relation),
METRIC = goal-content <-> outcome-content overlap, NOT goal-presence. OURS = directed_goal_outcome_score checks
has_goal (presence) = CONTENT-BLIND (same class as the earlier-session decode_coherence_margins role-content-
blindness). On single-goal items presence==coherence; on MULTI-goal cue-conflict items it ties. ROUTE (rule b):
NOT missing-LEARNING; missing CAPABILITY = goal-content<->outcome-content (shared theme/object) coherence, a
REUSE/EXTEND of owned machinery (EventRecord.patient/theme + CausalLinkRegister), not from-scratch. RISK: content-
coherence is historically HARD (the earlier role-content arc HARD_FAILed for decode_coherence_margins; only the
role-compatibility-score selector was a thin HARD_PASS). NEXT = build 3c goal-content-coherence tie-break (reuse
theme-match), with gold-vetted MULTI-GOAL cue-conflict test items, pre-reg fix-t24 + hold-47 + validate-multigoal;
THEN promote the complete goal-owner selector (candidate-gen + content-coherence) as the wire-don't-island lock-in.

## NEXT-CAPABILITY PREP (brain-foundational targets, Director-scoped 2026-08-05, full-auto-all-night USER-authorized)
North star (USER): on ANY negative, FULLY drill existing components for brain-foundational fidelity (SHAPE+
POSITION+METRIC vs the exact brain mechanism) + missing-component/LEARNING check; push each capability to CEILING.
- **OUTCOME-VALENCE (next component, deep-VET-flagged lexicon shortcut):** currently hdlab/goal_typing.py:84-87
  V2_OUTCOME_UNMET={"down","fell","sank","sink","wailed"...}/V2_OUTCOME_MET={"reached","won","escaped","arrived"}
  matched by SET MEMBERSHIP (goal_typing.py:123-124). BRAIN (Scherer/Lazarus goal-congruence appraisal): outcome
  valence = whether the outcome ACHIEVES vs BLOCKS the GOAL (relative to goal-state), NOT outcome-word-in-lexicon.
  "the boat sank" = UNMET because it blocks the mend-boat goal (goal-congruence), not because "sank" is a bad word.
  METRIC = goal-congruence (achieved/blocked), computed against the goal. FIX = reuse the OWNED appraisal-sim
  (exp_grounded_appraisal_sim_earned_v1, MECHANISM_EARNS goal-congruence valuation, currently ISLANDED) instead of
  the V2_OUTCOME lexicon = wire-don't-island. RISK: needs the goal-state + outcome-state as appraisal inputs (the
  situation model has goal via GO_ROLES; outcome-state extraction is the work).
  **CORRECTION (Director read the sim code 2026-08-05): the appraisal-sim is NOT a drop-in reuse for
  outcome-valence -- exp_grounded_appraisal_sim_earned_v1.py:74 CONG is a HAND-MAP (episode-type->HURT/HELP/
  NEUTRAL) that the sim VALUES; it takes congruence as INPUT, does not COMPUTE it from goal+outcome. Real
  outcome-valence = a GOAL-CONGRUENCE COMPUTATION (does the outcome-STATE achieve vs block/negate the goal-STATE
  on the shared object; "sank" is UNMET for mend-boat but valence is RELATIVE TO THE GOAL, not intrinsic to the
  word -- the V2_OUTCOME lexicon is a goal-INDEPENDENT proxy). Better reuse = PREDICTIVE CODING (goal sets an
  expected outcome-state; predictive_coding residual expectation-vs-actual = MET[low]/UNMET[high]) -- which ALSO
  wires the deep-VET islanded predictive_coding. NOTE: for OWNER selection this polarity does NOT matter (48/48
  already works w/ lexicon typing); outcome-valence is a separate POLARITY readout (instrument outcome_polarity
  gold: met=21/unmet=41) -- measure lexicon vs goal-congruence there. Genuine design problem, not a simple wire.**
  **FORMALIZED (research drill, notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md, P=0.50):
  brain computes outcome-valence as GOAL-CONGRUENCE = compare goal DESIRED-STATE (theme, result_verb_class) vs
  outcome ACTUAL-STATE (theme, result_verb_class) on the SAME referent (Scherer goal-conduciveness / Roseman
  motive-consistency / Trabasso chain-closing-vs-extending; goal-conduciveness is DISSOCIABLE from intrinsic word
  valence, Kreibig autonomic dissociation). MECHANISM: same-theme+opposed-class->UNMET, same-theme+entailing-
  class->MET, theme-mismatch->ABSTAIN (fallback to lexicon = preserves 48/48, strict ADD). REUSE (already own):
  clause_theme/entity_goal_themes (my 3c theme-binding), goal_typing desiderative/purpose-infinitival detection,
  lemma_verb, EventRecord. BUILD (small SUPPLY): RESULT_VERB_CLASS register (REPAIR_PRESERVE vs DAMAGE_LOSE etc,
  Levin/Beavers) + desired-state extractor + ~20-line congruence fn. Predictive-coding = right SHAPE (predict-
  then-observe ORDER) WRONG METRIC (continuous residual != discrete class-match; same ruling as frame_induction.
  py:27) -> use as design pattern, NOT literal dep. CAN-FAIL: goal-dependent-valence flips (same outcome word,
  opposite valence by goal; lexicon MUST score ~chance). Routing: used-ability-wrong (retire lexicon to fallback)
  + missing-FACT SUPPLY (verb-class register), NOT missing-LEARNING. Build dispatched.**
  **LANDED HARD_PASS (commit 63c71935d, exp_outcome_valence_goal_congruence_v1, Director per-axis disk-VET):
  mechanism 8/8 on the flip+binding set vs lexicon 4/8 (chance, delta 0.50); SCRAMBLE COLLAPSES GENUINELY
  1.0->0.4 (per-item verified: scrambling goal<->outcome pairing breaks theme-match -> abstain -> lexicon
  fallback -> MET items collapse to UNMET; proves the signal is goal-CONTENT/pairing not a hidden 2nd lexicon);
  H abstains (precision guard), G correct (no regression); backward-compat 48/48 HELD (strict ADD -- select_
  outcome_owner scorer reads only has_goal, polarity can't move owner-selection; mechanism ran clean on all 62
  rows via ABSTAIN->lexicon-fallback). HONEST SCOPE (VET + PRIOR-ART): N=10 hand-authored FOR theme-match =
  mechanism-EXISTS proof, NOT solved-on-real-data. Prior attempt exp_outcome_valence_detector_v1 HARD_FAILED
  with detector_fire_rate=0.0789 on N=38 -> theme-overlap has a COVERAGE problem on real data; goal-dependent-
  valence is a RARE-but-real PRECISION subclass (same word opposite valence by goal); the mechanism fixes that
  subclass + falls back to lexicon elsewhere = a genuine precision improvement, not broad coverage. NOT promoted
  (hdlab untouched). NEXT (maximize this capability): expand bank to 20-30 diverse items (more verb classes +
  flip families + coverage-stress where theme-overlap is harder) -> re-measure -> if holds, PROMOTE goal-
  congruence typing into hdlab/goal_typing.py (lexicon->fallback) + witness + certification. v2: negation-scope
  (prevent/NOT-VP) + OOV verb-class induction.**
- **situation_reader.read() call-site integration of goal_typing** (promoted organ not yet CALLED by the reader;
  CoNLL-gated, same as frame_primary_role wire).
- **source situation_type -> context_grounded_valence.py:141** (mechanism proven HARD_PASS in _v2, integration only).
- **Frame-B (deeper): goal-biased coref resolution** (the full recurrent-loop fix -- goal-coherence biases the
  outcome-pronoun resolution itself, not just candidate-gen).
- **Generalization stress-test:** the fair instrument is small (62 hand-authored items); maximize = test the
  goal-owner organ on a broader/real narrative set (guard confounds) to prove it's not instrument-overfit.
Lower-certainty: wire ToM (HARD_PASS islanded), relabel 2 mislabels (outcome-valence label, ToM registry row).

## LANDED-6 (MILESTONE): 3c goal-content coherence tie-break HARD_PASS -> goal-owner organ 48/48 (commit 6961f5b49, exp_c5_multigoal_content_coherence_tiebreak_v1, Director per-axis disk-VET incl authored-data quality)
The 3c THEME-MATCH tie-break (among tied goal-holders, prefer the entity whose goal-theme overlaps the outcome-
theme; Trabasso content coherence) WORKS. Multi-goal set (12 authored gold-vetted items): content-coherence
12/12 (1.0) vs positional/sorted-order 6/12 (0.5=chance), content_beats_positional=True, scramble non-vacuous.
FLIP-CONTROL (the make-or-break, Director-read the items): all 6 families flip -- e.g. m01 "Hugh to mend the
FENCE / Dean to fetch the LADDER", base outcome "the FENCE collapsed"->Hugh vs flip "the LADDER snapped"->Dean;
ONLY the outcome-object changes so the correct owner flips, and content flips (base+flip both right) while
positional can't (stuck picking the same entity) -> proves the signal is THEME not position/identity. GOLD-VET:
items are clean (both entities hold goals, distinct themes, outcome-object decisive) -- NOT circular. Full fair
instrument: content 48/48 (positional 47/48), t24 FIXED (goal-theme{oars,boat,tide} ∩ outcome-theme{tools,boat}
={boat}), 47 HELD (no_regression by construction: 2 ties only; t23 falls back, t24 uniquely decided). The
mechanism is a PURE ADD-ON tie-break over the promoted organ, fires only when len(winners)>1; production hdlab
consumed UNMODIFIED. **MILESTONE: the goal-owner organ is COMPLETE on the fully-fair instrument (48/48, both
trap types, both constructions, GOLD-FREE) + the multi-goal cue-conflict class (12/12, flip-control clean).**
NEXT = WIRE the complete selector (candidate-gen + goal-coherence + content-coherence tie-break) into production
hdlab/goal_owner_select.py + witness + registry + certification (wire-don't-island lock-in, agent flagged it),
THEN outcome-valence = goal-congruence appraisal (see NEXT-CAPABILITY PREP above).
