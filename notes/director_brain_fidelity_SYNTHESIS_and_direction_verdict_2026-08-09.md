# Brain-fidelity SYNTHESIS + direction verdict — are we on the right track?

**Author:** Director (main thread, opus), 2026-08-09. **Trigger:** USER "do a deep drill... brain
foundational fidelity to be sure we're on the right track" + "full auto all night, drill all negatives
3x and brain foundational 3x, the brain can do it so can we." **Inputs (3 independent brain-foundational
passes + 2 empirical probes + 1 primary-source VET):**
- Pass 1 (architecture): `notes/director_brain_fidelity_audit_shape_position_metric_2026-08-09.md` (my SHAPE+POSITION+METRIC audit) + `notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md` (agent drill A -- was slow not dead; LANDED, 4 independent lit-scans + adversarial counter-search, STRONGEST pass).
- Pass 2 (OOV/schema): `notes/research_brain_fidelity_oov_schema_prediction_2026-08-09.md`.
- Pass 3 (adversarial): `notes/research_brain_fidelity_adversarial_framing_2026-08-09.md`.
- Empirical: T2 referent-bound affect (2/39, 2/2); top-down goal-conditioned probe (FAILED cheap version).
- VET: DesireDB inter-annotator numbers, primary source ar5iv 1708.09040 (HIGH-confidence).

## The question, answered in one line

**We are on the right GOAL but a partially-wrong ARCHITECTURE with a mis-set success bar.** The fix is
a scoped, owned-organ-reusing upgrade -- not "stay the course," not "rebuild," not "pure top-down."

## What all three passes agree on (convergent, high-confidence)

1. **The binary class-match readout is the wrong mechanism.** Pass-2: the OOV wall is an artifact of
   OPEN bottom-up type-matching against a fixed ontology. Pass-3: binary same/opposed contradicts the
   Trabasso/van-den-Broek GRADED causal-connectivity evidence -- narrative goal->outcome linkage is a
   graded connection-count, not a binary flag. Pass-1: the OOV / referent-binding / affect-relevance
   walls are all artifacts of extract-then-compare-with-a-discrete-match.
2. **The readout, not the conditioning, is the bottleneck** -- confirmed EMPIRICALLY: my top-down
   goal-conditioned probe kept the binary/lexicon-polarity readout and FAILED its pairscramble gate
   (real 0.613 ~= scrambled 0.704 ~= baseline); and goal-relevant-affect selection (0.613) ~=
   whole-passage (0.615), so WHICH affect you count doesn't matter while the readout stays binary/lexical.
3. **A goal-as-preference/utility representation is entirely missing** (Pass-3, sharpest). The brain
   represents "what a character wants" as an inferred UTILITY/PREFERENCE FUNCTION (Baker/Saxe/Tenenbaum
   inverse planning; Jara-Ettinger naive utility calculus; Chandra et al. 2024 "Storytelling as Inverse
   Inverse Planning" applies it directly to narrative); "fulfilled" = SCORE the outcome under that
   function, not token-equality. This leg has NO analog in the current pipeline.

## The one big VET catch (VET-as-hard-as-positive)

Pass-3 recommended recalibrating success to the inter-annotator ceiling and implied we are near it.
Primary-source VET (ar5iv 1708.09040): 3 annotators, majority-vote gold; Krippendorff-alpha(pairwise)
**0.63**; three-way unanimity **66%**; per-label unanimity Fulfilled 75% / Unfulfilled 67% / Unknown 41%.
**Pass-3 conflated 66% three-way-unanimity with the accuracy ceiling.** The accuracy analog (single
annotator vs majority gold) = 66% + 32%x(2/3) ~= **0.87**; raw pairwise agreement ~= **0.77**. So the
human ACCURACY ceiling is ~0.77-0.87, NOT 0.66. Our 3-channel organ ~0.688 acc is **~8-18 points below
the human ceiling -> we are NOT at ceiling; there IS real reducible headroom.** What survives: alpha 0.63
< Krippendorff's 0.67 "tentative" floor, so the top ~13-23% is genuinely ambiguous even to humans ->
**honest target ~0.80-0.87, not 1.0.** "Recalibrate below 100%" = right; "stop, we're at ceiling" = wrong.

## Direction verdict (I am making the call per "full auto")

**Stay on the goal; upgrade the architecture along 3 owned-organ-reusing axes; gate the build on 2 cheap
probes; report against the ~0.85 human ceiling.** Ranked, with brain-foundational + owned-parts mapping:

1. **GRADED congruence scalar** replacing the binary class-relation. Signed causal-connectivity count
   (supporting minus opposing clauses between goal and outcome nodes) / appraisal-conduciveness.
   OWNED: situation-model register, biased-competition, superposition-collapse. Lit: Trabasso/Sperry,
   Scherer CPM. (Pass-3 Probe 1.)
2. **GOAL-AS-PREFERENCE-STRUCTURE (utility) leg** -- decompose the desire into 2-4 attribute-predicates,
   SCORE the outcome against them (satisfies-any / partial / via-unexpected-route), NOT exact class match.
   The genuinely new, brain-faithful piece; anchor Chandra 2024 + Baker/Saxe/Tenenbaum (glass-box
   Bayesian, no LLM). (Pass-3 Probe 2.) Dissolves the "partial/route-independent satisfaction" gap the
   class-token check structurally cannot express.
3. **CLOSED-SET schema-selection + graded fit for OOV** (Pass-2): stop open-typing against a fixed
   ontology; select among already-active schema candidates via biased competition + graded relational
   fit against the winning schema's predicted slot. OWNED: focus-vector, superposition-collapse,
   bind/bundle + the grounded concept/script layer PROVEN this arc (script_bridge / learned_script_bridge,
   all gates). This is where the readout gets GROUNDED -- the fix for my probe's lexicon-readout bottleneck.
4. **Recalibrate + report vs the ~0.77-0.87 human ceiling**, decompose the residual into irreducible
   (annotation-ambiguity-bounded) vs reducible (the ~8-18pt the upgrade targets).

REJECTED: (a) stay the course (all 3 passes contradict binary matching); (b) pure top-down conditioning
alone (empirically failed + Pass-3 rank-3 -- it's necessary infra, not sufficient without graded+utility).

## The empirical arbiter (next build -- can-fail, BEFORE committing to the full upgrade)

Run Pass-3's two cheap script-only probes on the DesireDB residual cohort, with the grounded concept
layer supplying the readout (my probe's lesson: not lexicon polarity):
- **Probe 1 (graded congruence):** does a signed graded congruence scalar predict the verdict on the
  abstain/wrong items better than the binary check? HARD-PASS >= 50% of currently-abstain/wrong items.
- **Probe 2 (utility-predicate):** decompose desires into attribute-predicates; does grounded
  satisfies-ANY recover verdicts where class-token equality fails? HARD-PASS >= 40% on OOV-failure items.
- Both with a pairscramble/wrong-goal control (must degrade). HARD-FAIL on either -> that axis is
  coverage-bound not architecture-bound; deprioritize it.

## UPDATE (drill A landed -- strengthens the verdict + adds a STAGED path)

Agent drill A (architecture) completed (slow, not dead) and is the strongest pass: 4 independent
lit-scans (RPE/OFC-vmPFC; PFC guided-activation/biased-competition/predictive-coding; situation-model;
ACC/PRO + adversarial counter-search) ALL converge on TOP-DOWN, with a clean existence-proof
(Babayan/Uchida/Gershman 2018 belief-state dopamine: identical physical outcomes get opposite-signed
interpretation depending on the pending expectation). The one bottom-up-first mechanism in the lit
(Corbetta & Shulman ventral salience circuit-breaker) is perceptual-orienting, not semantic -- does NOT
rescue a bottom-up design. So the direction verdict is now 4-of-4 convergent, not 3.

Two refinements from A:
1. **WHOLE-PIPELINE lesson:** the SAME bottom-up-vs-top-down divergence was independently found the same
   day at TWO other stages (event segmentation; thematic-role labeling, per
   notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md -- the concurrent goal-owner pipeline).
   Treat top-down goal-cued relevance-weighting as a WHOLE-PIPELINE architectural primitive, not 3 bugs.
2. **A STAGED path (cheap-first, then expensive):** A scopes the goal-blind valence_channel as ~HALF the
   DesireDB shortfall (the affect-present-but-unbound ~49% at 0.615 = exactly the T2 bucket), fixable by
   a goal-CUED valence channel reusing ONLY owned organs (state_of_mind, cleanup_argmax, UD-arcs,
   lexical_similarity) -- a WEEKS-scale drop-in, NOT the months-scale grounded foundation.
   - STAGE 1 (cheap, DISPATCHED to hdi_exp_dev now): exp_goal_cued_valence_channel_v1 -- goal-cued
     relevance-weighted valence vs (i) current uniform + (iii) scrambled-goal control; pre-registered
     >=10pt HARD-PASS on the mixed-polarity subset. My graded-utility probe already supports (ii)>(iii)
     but cautions the absolute lift is the real can-fail (readout may cap ~0.60). Addresses the BINDING
     half of the wall.
   - STAGE 2 (Direction B, expensive): grounded utility-scoring fit-check for the OOV/vocabulary half +
     the hard polarity -- Chandra-2024 inverse-planning feasibility drill IN FLIGHT to size it
     (weeks-minimal vs months) + name the cheapest first experiment.

So the strategic picture is better than "commit to a months-long build": there is a cheap, high-fidelity,
owned-organ STAGE-1 win (goal-cued valence) to bank first, gated on its pre-registered can-fail bands,
with Direction B (grounded utility-scoring) staged behind a feasibility drill.

## Answer to the USER

Right track on the goal and the glass-box invariant; a real, named, brain-foundational architecture
divergence (binary token-match where the brain does graded scoring under an inferred utility function);
and a mis-set bar (target ~0.85, not 1.0 -- but we are NOT at ceiling, ~8-18pt of real headroom remains).
The upgrade reuses owned organs + the grounded concept/script layer already proven this arc, and is gated
on two cheap can-fail probes before any large build. "The brain can do it, so can we" holds: the brain's
way here is graded utility-scoring, and that is buildable on what we own.
