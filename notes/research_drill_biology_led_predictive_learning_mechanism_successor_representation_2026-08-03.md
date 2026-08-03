# Research drill: biology-led predictive-learning mechanism (successor representation) for event relation inference (2026-08-03)

Filed by: Director. Task: arm the next brain-faithful build on the relation-inference frontier
after tonight's MSE event-predictor failed twice, and both VET gates
(`notes/skunkworks_audit_phase1_event_level_prediction_error_STAGE_B_FAILS_FAIR_BASELINE_2026-08-03.md`,
`notes/research_drill_brain_fidelity_audit_v2_HARD_FAIL_2026-08-03.md`) independently converged on
"MSE-regression-to-a-point mean-collapses; the fix is a contrastive/discriminative objective +
accumulated context" WITHOUT researching what the brain's own predictive-learning mechanism
actually is. This drill supplies that biology.

## 0. KB-check (mandatory, run before writing)

`bash tools/substrate_query.sh` run three times pre-drill:
- `"successor representation temporal difference predictive map"` -> top hit cosine=0.3916
  (WordNet "Representative"/"representation" lexical nodes — NOT conceptual overlap; no SR/TD
  content in KB).
- `"hippocampal replay contrastive Hebbian predictive coding"` -> top hit cosine=0.4365
  (`predictive_coding` capability-registry entry, already WIRED as a general predictive-coding
  module reference; no replay/contrastive-Hebbian/SR content).
- `"goal inference bridging inference mentalizing theory of mind reading comprehension"` -> top
  hits cosine 0.32-0.37, all from `notes/research_missing_comprehension_mechanisms_litscan_2026-08-01.md`
  (bridging-inference/RST citation, ESTABLISHED-status note, no mechanism detail) and
  `notes/research_social_interactive_language_acquisition_5x_2026-07-09.md` (RSA/ToM-for-reference,
  different question — word learning, not event-relation inference).

**Verdict: genuinely new territory.** Nothing on SR, TD-learned predictive maps, hippocampal
replay, contrastive Hebbian learning, or Kintsch construction-integration exists in the KB under
any phrasing. Reusing without re-deriving: the Zacks/Trabasso/Zwaan/Mar citation set and the
event-grain conclusion already verified in
`notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md` (§2, "relation
inference operates over event/predicate-level bound structure") and the two same-day
brain-fidelity audits (`notes/research_drill_brain_fidelity_audit_event_relation_inference_phase1_2026-08-03.md`,
`notes/research_drill_brain_fidelity_audit_v2_HARD_FAIL_2026-08-03.md`) which independently
diagnosed the v1/v2 failures as context-starvation (window=1) + wrong target grain (literal
surface retrieval), not a refutation of prediction-error learning as a paradigm. This drill's job
is narrower: what IS the brain's predictive-learning mechanism, biology-first.

---

## 1. PRIMARY: the successor representation (SR)

**Definition and origin.** Dayan, 1993, *Neural Computation* 5(4):613-624, "Improving
Generalization for Temporal Difference Learning: The Successor Representation." SR(s) is the
discounted expected future state-occupancy vector from state s under policy pi:
`M(s) = E[ sum_k gamma^k * phi(s_{t+k}) | s_t = s ]` — a prediction of ALL future states reachable
from here, not a single target. Learned by **TD(0) bootstrapping**, not point regression:
`M(s_t) <- M(s_t) + alpha [ phi(s_t) + gamma*M(s_{t+1}) - M(s_t) ]` (error-driven, Rescorla-Wagner
family — the one element both VET audits already independently confirmed as brain-faithful in
our own predictor).

**Neural substrate.** Stachenfeld, Botvinick & Gershman, 2017, *Nature Neuroscience* 20:1643-1653,
"The hippocampus as a predictive map" (verified, gershmanlab.com/pubs/Stachenfeld17.pdf). Argues
hippocampal place cells encode the SR rather than a raw metric map — place-field shapes skew
against the direction of travel and compress around bottlenecks/barriers in ways a pure spatial
map does not predict but a discounted-future-occupancy map does; entorhinal grid cells are
proposed as a low-dimensional (eigenvector) basis for the SR, useful for noise suppression and
multiscale hierarchical planning. **Policy dependence and reward revaluation**: because SR
separates "what states are reachable" (M, policy-dependent) from "what's valuable there" (reward
weights), the brain can revalue a goal instantly (relearn only the reward vector) without
relearning the entire transition/occupancy structure — a specific, testable dissociation with
direct behavioral support (latent learning, reward-devaluation paradigms cited therein).

### (a) Does SR structurally avoid the mean-collapse that killed our MSE predictor?

**Yes, and the reason is mathematically load-bearing, not incidental.** Our MSE predictor's
objective (`(1/2)*||Wx - y||^2` averaged over training pairs with an under-informative x) has its
global optimum AT the conditional mean of y given x whenever x underdetermines y — exactly the
observed failure (`cosine_test_trained=0.578`, near-uniform across distinct contexts, per both
VET docs). SR's objective is structurally different in two ways that both cut against this: (i)
the TD target `phi(s_t) + gamma*M(s_{t+1})` is BOOTSTRAPPED from the network's own current
estimate at the NEXT state, so the loss landscape's fixed point is a self-consistent map over
every distinct state s (each state gets its own attractor, `M(s)`), not a single global average
over the training distribution; (ii) SR IS an expectation over a distribution of futures by
construction (a discounted sum over occupancy), so it never claims to predict "the" next state —
collapsing state-specific detail into a single point is not a failure mode you can even observe
in SR's own output, because state-differentiation (not point-accuracy) is the entire quantity
being fit. This is the single strongest biology-grounded reason to abandon point-regression MSE
in favor of a TD-bootstrapped map: the two VET audits' contrastive-objective recommendation was
right, but SR shows WHY at the level of the underlying learning target, not just "point
regression bad, discrimination good."

### (b) Does SR's reachability structure naturally encode causal + goal structure?

**Partially yes, with one caveat that is itself a novel-synthesis opportunity.** "What is reachable
from here, and how soon" is directly the CAUSE/ENABLE relation's operational content (Trabasso's
antecedent-consequent causal network is, structurally, a graph of "what leads to what" — the same
object SR estimates for spatial/state transitions). SR's eigendecomposition giving multiscale
"bottleneck"/subgoal structure (Stachenfeld et al.; Machado, Bellemare & Bowling 2017-2018 SR-based
option discovery, cited in follow-on RL literature) is a direct structural analog to GOAL
decomposition — a bottleneck state in the SR graph is functionally a subgoal a plan must pass
through. **The caveat**: SR is policy-DEPENDENT — `M` estimates reachability under a SPECIFIC
policy pi. For inferring an UNSTATED character goal, the natural move is INVERSE: given the
observed SR-like transition pattern (what a character's actions actually led to, over the
narrative), infer the POLICY (goal) that would make that transition pattern the accumulated
occupancy of a goal-directed agent — i.e., goal inference as inverse-RL-over-SR, not as a separate
add-on module. **This is genuinely novel synthesis, not established literature** (biology
supports SR's policy-dependence and inverse-RL as a general framework for goal inference from
behavior — Baker, Saxe & Tenenbaum 2009 *Cognition*, "Action understanding as inverse planning",
is the classic reference for the LATTER but was not, in the search performed here, found combined
with SR specifically in a single cited source) — flag P deflated, cap at 0.35 per calibration
discipline, and treat as the most promising but least-verified piece of this drill.

### (c) Can SR be built over our FHRR-bound event structures, glass-box, no borrow?

Yes, structurally straightforward: replace SR's scalar/vector state-occupancy target with the
substrate's OWN bound event-structure vectors (`build_event_struct_v6` output, or a richer
GOAL/OUTCOME-augmented version per the v1 audit's Deviation 4). `phi(s_t)` = the event's own FHRR
encoding (earned, not borrowed — this is the substrate's existing representation, not an external
embedding). `M(s_t)` = a learned map (linear or nonlinear, per the existing predictor scaffold)
trained via TD(0) bootstrap instead of MSE-to-a-fixed-target. Nothing here requires an external
oracle, encoder, or reader — it is a different LEARNING RULE over the substrate's own
representations, in the same category as the delta-rule the VET audits already certified as
faithful.

---

## 2. SECONDARY mechanisms and complements

**Contrastive Difference Predictive Coding (Zheng, Salter, Eysenbach et al., ICLR 2024,
arXiv:2310.20141)** — directly fuses TD learning with a contrastive (InfoNCE-style) objective:
learns representations whose INNER PRODUCT approximates SR-style future-reachability, trained via
noise-contrastive discrimination against negative (non-reachable / mismatched) future states,
rather than regressing a point target. This is, concretely, the exact recipe both VET audits
independently converged on ("contrastive objective + TD-style accumulation") — now with a named
method and a working implementation precedent (2x median improvement over prior goal-conditioned
RL baselines, better robustness under stochastic environments — stochastic/multi-valued futures
being precisely the property that sank our point-regression predictor, since real prose is
highly multi-valued at the surface-sentence level per the encoder-target drill's Q2 finding).
**This is the single most actionable citation in this drill**: it is a published, working fusion
of exactly the two ingredients (TD + contrastive) our own failure analysis derived independently,
giving us a concrete training-objective template rather than starting from scratch.

**Hippocampal replay as OFFLINE consolidation/refinement of the predictive map.** Levenstein et
al., 2024, bioRxiv 2024.04.28.591528, "Sequential predictive learning is a unifying theory for
hippocampal representation and replay" — argues that spatially-tuned (place-like) cells emerge
from ANY form of predictive learning, but REPLAY specifically (offline reactivation of sequences)
only emerges in networks with recurrent connections predicting MULTI-STEP sequences, and that
this is what forms a genuine continuous-attractor cognitive map (not just single-step
prediction). Separately: prioritized hippocampal replay of significant experiences on a
predictive map (Mattar & Daw 2018-line work, PMC7817193) shows replay preferentially reactivates
high-utility/high-error trajectories, INCLUDING optimized paths never actually traveled — i.e.,
replay GENERATES counterfactual/novel trajectory samples, not just literal reactivation. An
inhibitory-plasticity mechanism for "world structure inference by hippocampal replay" (bioRxiv
2022.11.02.514897) shows replay-driven remodeling of inhibitory synapses in CA3 learns the
statistical/causal STRUCTURE of the environment, not just individual episodes.
**Actionable implication**: replay is the brain's natural mechanism for generating NEGATIVES
(untraveled, counterfactual, or high-error trajectories) for exactly the kind of contrastive
objective in (1) above — this maps directly onto our `situation_model_multibank` accumulate
register (already built, WIRED_AND_PIPELINE_USED per MEMORY) as a natural buffer to replay FROM,
rather than needing a separately-designed negative-sampling scheme.

**Contrastive Hebbian learning as the biologically-plausible correspondent of the ML
"contrastive" step.** Verified (Wikipedia/Eyewire summary + Movellan 1991 origin; O'Reilly 1996
showed equivalence in representational power to backprop): CHL uses two phases (a "free" phase and
a "clamped"/contrastive phase) with local Hebbian-style updates, avoiding the biologically
implausible global error-backpropagation while still performing gradient-like credit assignment.
**One real tension, honestly flagged**: standard contrastive/negative-sampling objectives (as in
InfoNCE/CDPC above) are noted in the current ML-neuro literature as NOT fully biologically
plausible in their usual form because explicit negative samples break temporal contiguity;
alternatives without negative samples exist (variance-regularization approaches like LPL, or
architectural asymmetry + gradient-stopping non-contrastive methods) that avoid representational
collapse without an explicit negative set. **Resolution for our purposes**: hippocampal replay
(above) supplies a biologically-grounded SOURCE of negatives (counterfactual/untraveled
trajectories, naturally generated offline) that sidesteps the "breaks temporal contiguity"
objection — the negatives are not arbitrary out-of-distribution samples, they are the brain's own
replay-generated alternate continuations. This resolves the one plausibility gap in adopting an
InfoNCE-style objective directly.

---

## 3. THE GENERATIVE INFERENCE question: how does the brain GENERATE an unstated relation?

**Kintsch's Construction-Integration model** (Kintsch 1988 *Psychological Review*, 1998
*Comprehension: A Paradigm for Cognition*; verified via ScienceDirect/ResearchGate/Pitt.edu
summaries). Two-phase mechanism, directly answering "how is a bridging inference GENERATED,
mechanistically": **(1) Construction** — text input spreads activation into the reader's
long-term associative/knowledge network and pulls in a broad, relatively unconstrained set of
CANDIDATE propositions (including many that will turn out irrelevant or wrong — this is a loose,
overgenerate step, not a precise one); **(2) Integration** — a constraint-satisfaction /
spreading-activation settling process prunes the candidate set down to a coherent, stable subset
(a textbase), dropping weakly-connected candidates; readers additionally connect this textbase to
prior knowledge to form the SITUATION MODEL, and it is this situation-model-building specifically
that is associated with more coherent, elaborate bridging inference. **The mechanistic shape this
implies**: bridging/elaborative inference is NOT a single precise deductive step — it is
OVERGENERATE-THEN-COHERENCE-FILTER, a two-stage architecture.

**This maps directly onto substrate capacity we have already built**, closing the loop with §1-2:
- **Construction** = the SR/TD-contrastive predictive map's natural output IS an overgenerated set
  of candidate reachable futures (SR is, by definition, a distribution/expectation over many
  possible successor states, not one) — this is architecturally the same shape as Kintsch's
  loose, associative construction step, for free, as a side effect of choosing SR/TD over point
  regression.
- **Integration** = the substrate's already-built coherence-gated self-improving loop (per MEMORY,
  "calibrated flag + coherence-gated autonomy, gold-free on dense") and the disk-verified
  `CausalLinkRegister` (0.9722 vs 0.0 baseline cross-chapter) are both, functionally, coherence
  vetting / constraint-satisfaction filters over candidate relations — exactly Kintsch's
  integration step, already built and validated, just not yet fed by a construction-stage
  generator that itself proposes UNSTATED candidates (today it presumably operates over
  STATED/structured relations, per the task brief's framing that our organs "work GIVEN
  structured relations").

**Mentalizing network (mPFC/TPJ) for the GOAL-specific content of the candidate set.** Mar, 2011,
*Annual Review of Psychology* 62:103-134 (ALE meta-analysis, already verified in the companion
drill) — core network mPFC/dmPFC + bilateral TPJ/pSTS + precuneus/PCC, substantially overlapping
DMN, engaged specifically by story-based ToM tasks. Newer work (2025-2026, Journal of
Neuroscience / Soc Cog Affect Neurosci, found this session) refines the division of labor: **TPJ**
tracks TRANSIENT beliefs/intentions (moment-to-moment, exactly the grain of "what does this
character want RIGHT NOW"), **mPFC** tracks STABLE traits/enduring characteristics, and dmPFC
engagement during intention-inference specifically is modulated by the READER'S OWN PRIOR
EXPECTATIONS (Bayesian-flavored, prior-weighted inference, not template matching) — a 2025 finding
(Uncertainty, not mental content, drives dmPFC engagement) reframes dmPFC's role as tracking
INFERENTIAL UNCERTAINTY about others' states specifically, which fits naturally as a confidence/
calibration signal layered on top of the construction-integration architecture above (candidate
goals generated, dmPFC-style uncertainty signal gates confidence, TPJ-style transience signal
distinguishes "goal active now" vs "settled trait"). **Contested, flagged honestly**: whether TPJ
engagement is ToM-specific or partly reflects domain-general attentional reorienting remains an
open dispute in the literature (2008 Cerebral Cortex critique, still cited as live in 2011 Mar
review) — do not oversell this piece as a solved mechanism, only as converging behavioral-grain
evidence (transient-vs-stable, uncertainty-gated) worth mirroring architecturally regardless of
the underlying neural-specificity dispute.

---

## 4. RANKED RECOMMENDATION for the next build

**Rank 1 (primary mechanism, P=0.40 novel-synthesis-capped): replace the MSE point-regression
event predictor with a TD-bootstrapped, contrastively-trained successor-representation-style
predictive map over bound FHRR event structures, fed by the accumulated situation-model context
(not a 1-event window), with replay-generated negatives.**

Concrete glass-box spec:
1. **Representation**: `phi(s_t)` = the substrate's own bound event-structure encoding (reuse
   `build_event_struct_v6`, ideally augmented with GOAL/OUTCOME slots per the v1 audit's
   Deviation 4 — not yet implicated in tonight's HARD_FAIL but load-bearing for Stage C).
2. **Context**: input to the predictor is the ACCUMULATED state from
   `hdlab/situation_model_accumulate.py` + `hdlab/situation_model_multibank.py` (already
   built, WIRED_AND_PIPELINE_USED, decode >=0.999 on durable multi-bank memory) — directly fixes
   the #1-ranked deviation from tonight's HARD_FAIL audit (context-window=1 starvation), per that
   audit's own §5 re-test spec, which this drill now supplies the missing biological mechanism
   for (the audit named the fix; this drill explains WHY TD+contrastive is the biology-correct
   training objective to pair it with, not just "any better predictor").
3. **Learning rule**: TD(0) bootstrap, `M(s_t) <- M(s_t) + alpha*[phi(s_t) + gamma*M(s_{t+1}) -
   M(s_t)]`, trained via a CONTRASTIVE (InfoNCE-style / CDPC-style) discriminative loss instead of
   squared error: score candidate futures by FHRR similarity to the predicted successor-vector,
   train to rank the TRUE eventual descendant (at variable horizon, not just t+1) above negatives.
4. **Negative source**: replay-generated counterfactual continuations from the accumulate
   register (biologically-grounded per the Levenstein/Mattar-Daw replay literature above), plus
   same-novel hard distractors as already used — NOT relying solely on the latter, since that is
   what let copy-context win in v2 (copy-context is not distinguishable from a true local
   continuation by vocabulary-sharing distractors alone; a replay-generated PLAUSIBLE-BUT-WRONG
   counterfactual is a harder, more informative negative).
5. **Success metric (directly fixes deviation #2 from the HARD_FAIL audit)**: multi-step
   reachability ranking, not literal-next-sentence surface retrieval — score whether the
   predicted successor-vector ranks the TRUE eventual causal descendant (at the horizon the
   relation actually resolves at, per `CausalLinkRegister` chain membership) above hard
   distractors, reusing the already-validated causal organ as the INTEGRATION-stage judge (Kintsch
   architecture: SR/TD-contrastive predictor = construction/candidate-generation stage;
   CausalLinkRegister = integration/coherence-filter stage).
6. **Can-fail test**: required margin over random/mean/copy-context baselines = 0.05 absolute
   (same envelope-fail-band convention as tonight's cells). **HARD-FAIL condition that would
   falsify SR/TD as the mechanism** (not just this operationalization): if the trained
   TD-contrastive predictor STILL shows the mean-collapse signature (near-uniform high cosine
   across distinct contexts) or still loses to copy-context even with full accumulated context and
   replay negatives, that is now a real negative against the paradigm itself (both previously
   identified confounds — context starvation, wrong target grain — would be resolved, so a third
   failure would not have an easy "it was mis-operationalized" escape and should be read as a
   genuine ceiling pending further audit).

**Rank 2 (secondary/necessary complement, not sufficient alone): the Kintsch
construction-integration two-stage architecture as the explicit frame for how "unstated relation
generation" is wired**, i.e. don't ask the predictor to directly output a single confident
SATISFY/THWART/CAUSE label — let it (construction) overgenerate ranked candidate successor/goal
states, and let the already-built coherence-gated loop + CausalLinkRegister (integration) filter
to the final relation. This is architecture, not a new learning rule, and is P=0.55 (higher
confidence than rank 1 because it reuses already-validated organs rather than proposing new
training machinery) — recommend building rank-1's predictor to OUTPUT INTO this frame from the
start rather than bolting the frame on after.

**Rank 3 (diagnostic/refinement lever, not load-bearing yet): mentalizing-style
transient-vs-stable + uncertainty-gated confidence signal** layered on top of whatever the
construction stage proposes for GOAL-specific (as opposed to plain causal/spatial) relations —
lower priority because Stage C (where GOAL/OUTCOME content would matter) never ran in either
failed cell; revisit once rank 1+2 clear Stage B.

## 5. Lock-compatibility

**TD-bootstrapped SR learning: EARNED, not borrowed.** `phi` is the substrate's own FHRR event
encoding; `M` is learned entirely from the substrate's own encountered narrative transitions via
an error-driven (TD/Rescorla-Wagner-family) update, with no external oracle, pretrained vector, or
supplied ground-truth relation table. This is a LEARNING RULE, in the same category the two VET
audits already certified the delta-rule as faithful — confirmed clean.

**Contrastive/InfoNCE-style objective: EARNED if negatives are self-generated (replay), a
judgment call if negatives are drawn from a fixed external corpus.** Per §2 above, the
biologically-cleaner version draws negatives from the substrate's OWN replay/accumulate buffer
(counterfactual continuations it itself represents), not an externally curated negative set —
recommend this framing explicitly to keep the objective inside the "own experience, own error"
principle the encoder-target drill already argued for. Flag for Director: if implementation
pressure leads toward supplying negatives from an external distractor bank rather than
self-generated replay, that edges toward the same kind of concern raised (and resolved AGAINST)
for Binder norms in the companion drill — my lean, consistent with that precedent, is
self-generated/replay-sourced negatives are the lock-compatible choice, not a curated external set.

**No borrowed reader/parser/embedding**: nothing in this spec introduces one. `build_event_struct_v6`
and the accumulate/multibank registers are already-built, already-audited substrate components.

## Citations (verified this session)

Dayan 1993, *Neural Computation* 5(4):613-624; Stachenfeld, Botvinick & Gershman 2017, *Nature
Neuroscience* 20:1643-1653 (gershmanlab.com/pubs/Stachenfeld17.pdf, directly fetched); Zheng et
al. 2024, ICLR, "Contrastive Difference Predictive Coding" (arXiv:2310.20141); Levenstein et al.
2024, bioRxiv 2024.04.28.591528, "Sequential predictive learning is a unifying theory for
hippocampal representation and replay"; Mattar & Daw-line prioritized-replay work (PMC7817193);
inhibitory-plasticity world-structure-inference replay paper (bioRxiv 2022.11.02.514897); Movellan
1991 / O'Reilly 1996 contrastive Hebbian learning equivalence-to-backprop result; Kintsch 1988
*Psychological Review*, 1998 *Comprehension: A Paradigm for Cognition*; Franklin, Norman,
Ranganath, Zacks & Gershman 2020, *Psychological Review* 127(3):327-361, "Structured Event Memory:
A Neuro-Symbolic Model of Event Cognition" (direct Gershman-lab bridge between SR-style predictive
learning and STRUCTURED SYMBOLIC event scenes — the closest existing published precedent to this
drill's rank-1 recommendation); Mar 2011, *Annual Review of Psychology* 62:103-134 (carried
forward from companion drill, not re-verified); Baker, Saxe & Tenenbaum 2009, *Cognition*, "Action
understanding as inverse planning" (cited for inverse-RL-style goal inference framing, flagged as
NOT found directly combined with SR in one source — the SR+inverse-RL synthesis in §1(b) is this
drill's own novel-synthesis contribution, capped P=0.35). Nguyen 2024, arXiv:2409.18992, "A Review
of Mechanistic Models of Event Comprehension" (reviews REPRISE/SEM/Lu/Gumbsch/Elman-McRae models;
consulted for landscape context, not deeply mined this session — candidate for a follow-up drill if
rank-1 is pursued and a comparison against these five existing computational models is wanted).

## HEADLINE

Biology says the brain's predictive-learning mechanism is NOT point-regression — it is the
successor representation, a TD-bootstrapped map over discounted future-state occupancy
(hippocampal place cells / entorhinal grid cells), which structurally cannot mean-collapse the way
our MSE predictor did because state-differentiation, not point-accuracy, is the quantity being
fit. A published fusion of TD + contrastive learning (Contrastive Difference Predictive Coding,
ICLR 2024) is the concrete training-objective template that matches what both tonight's VET gates
independently recommended. Hippocampal replay supplies a biologically-grounded source of
contrastive negatives (counterfactual/untraveled trajectories) and offline consolidation of the
predictive map. Kintsch's construction-integration model supplies the generative MECHANISM for
unstated relations: overgenerate candidates (which an SR-style map does natively, by definition)
then coherence-filter (which the already-built coherence-gated loop + CausalLinkRegister already
do) — meaning the next build is not "invent a new organ" but "feed the two organs we already
validated with a TD/contrastive-trained SR-style construction stage instead of the falsified
MSE point-predictor." Lock-compatibility: the core learning rule is earned, not borrowed;
negatives should be self-generated via replay rather than externally curated, to stay inside the
same principle. Two flags for Director: (1) the SR-as-goal-inference-via-inverse-policy idea
(§1b) is this drill's own novel synthesis, not established literature — treat as promising
hypothesis, not settled biology; (2) whether standard InfoNCE-style negative sampling itself
counts as "borrowed ML machinery" vs. "our own learning rule" is a judgment call, addressed but not
unilaterally resolved here.
