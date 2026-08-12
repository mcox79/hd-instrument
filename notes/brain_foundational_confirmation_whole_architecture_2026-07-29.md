# WHOLE-ARCHITECTURE BRAIN-FOUNDATIONAL CONFIRMATION (2026-07-29)

Scope: strategic validity check, NOT a build, NOT a re-derivation of the per-component audit.
Question: is the stateful-core design (K recurrent full-d entity slots + PBWM PE-gated write +
role-general HRR binding + encoder unfrozen end-to-end + forward-predictive objective +
supplied KB world-model prior) the brain-foundational architecture for comprehension /
situation-model construction, at the WHOLE-SYSTEM level -- or are we mis-shaping / omitting a
system-level element? Adversarial stance: don't rubber-stamp. Calibration per
[[feedback-lit-scan-calibration-penalty]]: CITED@ literature claims carry full weight; REASONED@
claims about our own system deflated 0.15-0.25; novel-synthesis capped P<=0.50.

Sources read (not re-derived): stateful_core_situation_model_build_design.md,
brain_foundational_component_analysis.md, drill_language_world_model_framing.md,
forward_predictive_objective_from_wm_state_design_2026-07-29.md,
brain_fidelity_audit_as_built_stateful_core_2026-07-29.md,
multi_sentence_situation_model_plan_2026-07-24.md.

OUR DESIGN, ONE PARAGRAPH (as stated in the task, confirmed accurate against the docs): a
recurrent set of K full-d entity-state slots, maintained over a clause stream, updated by a
learned per-slot PBWM-style PE-gated write, role-general (content-key) HRR binding, encoder
trained end-to-end, a forward-predictive objective (predict next-clause latent from the
maintained state), and a supplied KB world-model prior the system learns to update (Arm B vs
blank Arm A).

---

## CONVERGENCE TABLE

| Model | What it says (CITED@) | Converges with ours? | Names a gap? | Load-bearing |
|---|---|---|---|---|
| **SEM** (Franklin, Norman, Ranganath, Zacks, Gershman 2020, *Psych Rev* 127:327-361, CITED@ live-verified) | A probabilistic generative model over event dynamics: symbolic scene structure embedded in a continuous vector space; scene *dynamics* parametrized in that space; event boundaries and schema identity are *inferred* (which event-type is this, has it changed) via prediction error; schemas are reused/generalized across episodes; scales to naturalistic video segmentation. | **YES, strongest convergence of all five models.** Structured-scene-in-vector-space + PE-driven update is close to our slot design; SEM's "event schema" concept is close to our KB-prior-as-schema idea. | **YES -- the single sharpest gap.** SEM's boundary/schema-identity inference is an explicit, discrete, model-selection-style decision ("is this still the same event, or has a new one begun"). Our design has no such decision: PE gates a *continuous write strength* per clause, never a discrete segment/reset event. SEM also learns a *library* of reusable event-dynamics schemas across episodes (generalization); our KB prior is a single static injection, not a learned, reusable dynamics-schema set. | **HIGH.** This is the one component SEM has that we structurally lack, and it independently corroborates the code-level audit's #1 finding (below). |
| **EST** (Zacks & Kurby event segmentation theory; Kurby & Zacks 2008; Zacks & Swallow 2007; CITED@ live-verified) | Perceivers maintain a *working event model* that generates ongoing predictions; when prediction error rises *transiently* (a spike, not a gradient), the event model is updated / the WM representation is reset at a discrete *event boundary*; within an event the model is comparatively stable (bistable: hold vs. replace), not continuously blended. | **PARTIAL.** We converge on "PE is both the update signal and (per PBWM analog) the gating signal" -- that's right in spirit. | **YES.** We have only per-clause *continuous* update (a graded convex blend per the as-built audit), not explicit event-BOUNDARY segmentation with a bistable hold-or-reset decision. EST's core empirical signature (WM update concentrated in a brief window at the boundary, near-flat between boundaries) has no analog in our current per-clause-uniform update rate. | **HIGH -- converges with, and sharpens, SEM's gap.** Two independent literatures point at the same missing element: discrete/bistable segmentation, not graded per-step blending. |
| **Zwaan-Radvansky event-indexing / Kintsch-van Dijk CI** (CITED@, carried from multi_sentence_situation_model_plan.md + drill_language_world_model_framing.md) | 5 monitored dimensions -- protagonist, time, space, causation, intentionality; the model updates (at a real cost, measurable as reading-time slowdown) when a dimension changes; CI = construct (bind + retrieve) then integrate (settle). | **PARTIAL.** Our K entity-slots are a faithful realization of the PROTAGONIST dimension (each slot = one tracked entity), and bind+settle maps to VSA bind + attractor settle (already noted in the prior plan). | **YES.** TIME and CAUSATION are, per `multi_sentence_situation_model_plan.md`, being built as a **SEPARATE SYMBOLIC pipeline** (SequenceMatrix toposort, causal-network reasoner) alongside -- not inside -- the neural slot-attention WM now being built. That plan's own VET note (29510) already flags this explicitly: "NOT yet substrate-native = MOTIVATES the bundle-integration." SPACE and INTENTIONALITY are unaddressed in either pipeline. | **MEDIUM-HIGH.** Not a missing capability (time/causation cells exist and HARD_PASS'd), but a missing **unification** -- two comprehension systems (neural stateful-core, symbolic event-dimension reasoner) that the brain runs as ONE integrated situation model. |
| **Predictive processing / N400-as-update** (Rao-Ballard 1999, Friston 2005, Rabovsky 2018, CITED@ carried, already independently audited this session) | PE is generated by an *anticipatory, generative* top-down prediction of what comes next, computed from persistent state BEFORE evidence arrives; PE drives both learning and gating. | **YES, design intent converges.** The already-existing `forward_predictive_objective_from_wm_state_design_2026-07-29.md` explicitly targets exactly this gap (our current `surprise` was a retrieval/familiarity match, not a generative prediction) and proposes a slot-conditioned predictor head, sequenced correctly AFTER the gating fix. | **Partially self-corrected already.** This gap was found and designed-around within the existing docs; no NEW divergence to report here. | **MEDIUM, already in the pipeline** -- not a fresh finding, confirmed still-open and correctly triaged. |
| **Hasson / Chien-Honey cortical hierarchy of timescales** (Lerner, Honey, Silbert & Hasson 2011, *J Neurosci* 31:2906; Chien & Honey 2020, *Neuron*; CITED@ live-verified) | Temporal receptive windows (TRWs) increase up a cortical hierarchy -- word-level areas integrate ~seconds, higher language/DMN areas integrate over paragraphs/whole narratives; comprehension of long-form narrative structurally REQUIRES multiple, concurrently-running timescales, not one. | **NO -- clean divergence.** Our design runs a SINGLE clause-level recurrent state (one set of K slots, one update cadence). There is no slower, coarser state above it. | **YES.** A genuine multi-timescale hierarchy (clause -> scene/paragraph -> narrative) is architecturally absent. Notably, the multi_sentence_situation_model_plan's own attempt at a coarser layer (DIMENSION 3, "scene/segment focus") was built and empirically found to reduce to plain LOCAL-WINDOW candidate restriction, NOT genuine scene-level state (VET 29514: "scene_structure_supported=FALSE") -- i.e., the one prior attempt at a coarser timescale layer did not land as a real hierarchical state either. | **MEDIUM for the CURRENT build scope** (short passages, few entities/boundaries -- current calibration constructions do not yet stress multi-scene narrative). **Would become HIGH once scaling past short passages** (chapters, multi-scene documents) -- this is a scaling-dependent gap, not an immediate blocker. |
| **Hippocampal event-boundary reinstatement / SWR replay** (DuBrow/Davachi-lineage boundary-reinstatement work; Baldassano et al. ripple-at-boundary findings; CITED@ live-verified this cycle) | At event boundaries, the hippocampus rapidly REINSTATES the just-completed event (boosting its consolidation into long-term memory); SWR replay during rest/sleep further consolidates and, per SEM, is plausibly where cross-episode SCHEMA generalization happens. | **NOT ADDRESSED -- explicitly deferred (component 10, "on-deck not the bottleneck" per brain_foundational_component_analysis.md).** | **Not a fresh gap -- confirms an existing, correct triage.** This machinery is about consolidation/schema-learning ACROSS many episodes/passages, genuinely separable from the ONLINE within-passage maintenance loop that is the current build's target. | **LOW for the current build; will become load-bearing when the target shifts from "comprehend one passage" to "learn reusable event schemas across many stories"** (which is precisely what SEM's schema-library capability requires, and what our current single-shot KB-prior injection does NOT yet provide -- see below). |

---

## THE KB-PRIOR ROUTE: brain-foundational or shortcut?

**Judgment: brain-foundational, PROVIDED it is used as a persistent prior, not a one-shot seed.**
This was already argued carefully in `drill_language_world_model_framing.md` section 4-6 (Lambon
Ralph hub-and-spoke: amodal ATL hub as a modality-invariant conceptual store that language
addresses into; Bartlett-schema-as-prior) and that argument holds up under this cross-check:
supplying KNOWLEDGE (the KB's relational content) is the sanctioned side of the
supply-structure-not-mechanism line; supplying the COMPREHENSION MECHANISM (a parser/reader) would
not be, and isn't what's being done here. **New corroboration from SEM (this cycle):** SEM's own
generative model explicitly contains a *library of learned event schemas* that are retrieved and
reused as priors across episodes -- structurally the same idea as "a supplied concept prior that
biases inference." This is independent convergence that a schema/prior-as-bias is a
brain-foundational computational move, not a hand-built shortcut.

**BUT** the as-built audit (`brain_fidelity_audit_as_built_stateful_core_2026-07-29.md`, section D,
REASONED@ P~0.45 deflated) found our actual implementation violates the "persistent prior" reading:
the KB vector seeds slot 0 ONCE at t=0 and is then diluted by the same convex-blend write every
subsequent clause, with no protection mechanism -- functionally an initial condition that decays,
not a hub that stays continuously available (Lambon Ralph's hub is repeatedly reactivated, not
consumed). **This is the SAME structural mechanism (C: mean-pool + convex-blend write) implicated
in the SEM/EST segmentation gap above** -- one fix (per-slot gating with a protected/exempt KB
slot, sharpened toward bistable hold-or-replace) plausibly resolves both the segmentation gap and
the KB-erosion gap simultaneously. This convergence across three independent lines of evidence
(SEM's discrete schema-inference, EST's bistable boundary update, and the code-level audit's
convex-blend diagnosis) is the strongest single finding of this drill.

---

## VERDICT

**PARTIAL.** The whole-architecture design converges strongly with the leading computational
models of human comprehension -- SEM in particular is close to a pre-existing literature
validation of the "structured, vector-embedded, PE-updated latent state" approach we are building,
and predictive-processing / hub-and-spoke give independent biological grounding for the
objective and the KB-prior route respectively. There is no evidence we are on the wrong hill;
nothing here argues for abandoning the stateful-core direction.

It is not CONFIRMED outright because three system-level elements are genuinely missing or
mis-shaped, ranked by how load-bearing they are for comprehension:

1. **[HIGHEST] Discrete, bistable event-boundary segmentation (SEM + EST convergent finding).**
   Our design has continuous per-clause graded write-strength; the brain (both models) performs a
   discrete hold-vs-reset decision gated by a PE *spike*, not a smoothly blended update every step.
   This reframes the as-built audit's #1 code-level bug (mean-pool + convex-blend, gap C) from "an
   engineering defect" to "the literal absence of the EST/SEM segmentation mechanism" -- raising its
   priority rather than changing its prescribed fix.
2. **[MEDIUM-HIGH] Unification of the neural stateful core with the symbolic
   time/causation/space/intentionality reasoning pipeline.** Zwaan's 5 dimensions are currently
   split across two un-integrated systems (neural entity-slots here; symbolic toposort + causal
   reasoner elsewhere) rather than one coupled situation model.
3. **[MEDIUM, scale-dependent] Multi-timescale hierarchy (Hasson).** A single clause-level state
   with no coarser scene/narrative-level layer above it; the one prior attempt at a coarser layer
   (scene/segment focus) did not land as genuine hierarchical state. Not yet a blocker at
   current (short-passage) task scale, but will become one when scaling to longer documents.

Hippocampal replay/consolidation and the forward-predictive-objective gap are both already
correctly triaged in the existing docs (deferred-and-separable, and in-progress-and-sequenced,
respectively) -- this drill found no reason to re-rank either.

## THE SINGLE HIGHEST-VALUE SYSTEM-LEVEL ELEMENT TO ADD/RESHAPE

**Reshape the already-planned audit-C fix into an explicit, literature-named EVENT-BOUNDARY
SEGMENTATION mechanism, not merely "sharper gating."** Concretely: add a discrete/bistable
decision alongside the existing per-slot PE score -- e.g., a boundary flag `b_t = 1[max_k
PE_k > threshold]` (or a learned bistable gate annealed toward {hold, replace} rather than a free
sigmoid blend) that, when tripped, (a) performs a hard-er per-slot replace instead of a convex
blend, and (b) exempts/protects the KB-prior slot from ordinary write competition (fixing gap D by
the same mechanism). This is the SAME code change already prescribed in the as-built audit
(section C fix) and already next in the build sequence -- this drill's contribution is confirming,
from independent literature (SEM's schema/boundary inference + EST's bistable update), that this
is not just a bug fix but IS the missing brain-foundational element, and that its scope should
explicitly include protecting the KB slot, not just sharpening the entity-write gate. The
multi-timescale hierarchy (Hasson) and the symbolic/neural unification are real but lower-urgency
system additions to name on the roadmap for AFTER this fix lands, not to build now (avoiding the
compounding-confound trap the forward-predictive design doc already flagged for its own sequencing).

## KEEP-GOING VS COURSE-CORRECT RECOMMENDATION

**KEEP GOING, with a calibration (not a course-correction).** The architecture is not mis-shaped at
the level of "wrong hill" -- SEM alone is close to an independent literature pre-validation of the
overall approach. Proceed with the existing sequence (audit-C per-slot gating fix -> re-smoke ->
forward-predictive objective -> KD/MES re-eval), but (a) explicitly frame and implement the
audit-C fix as bistable event-boundary segmentation with a protected KB slot (not generic
"sharper gate"), and (b) add two named, deferred roadmap items from this drill --
multi-timescale hierarchy and neural/symbolic dimension unification -- so they are tracked rather
than silently dropped, to be picked up after the segmentation fix's HARD_PASS/HARD_FAIL verdict
lands (one-variable discipline, same reasoning the forward-predictive design doc already applied
to its own sequencing).

---

## Citations (verified count: 6 CITED@ live-verified this cycle + 5 carried CITED@ from prior session docs = 11 anchors; 0 uncited claims presented as fact)
- Franklin, Norman, Ranganath, Zacks & Gershman (2020), *Psychological Review* 127(3):327-361, "Structured Event Memory: A Neuro-Symbolic Model of Event Cognition" -- CITED@, live-verified (Princeton/WashU profiles, gershmanlab.com PDF, PMID 32223284).
- Zacks & Swallow (2007); Kurby & Zacks (2008), event segmentation theory, prediction-error-triggered working-memory update at boundaries -- CITED@, live-verified (ScienceDirect, GVSU PDF).
- Zwaan, Langston & Graesser (1995); Zwaan & Radvansky (1998); Kintsch (1988) construction-integration -- CITED@, carried from multi_sentence_situation_model_plan.md / drill_language_world_model_framing.md (previously live-verified).
- Rao & Ballard (1999); Friston (2005); Rabovsky, Hansen & McClelland (2018, *Nat Hum Behav*) -- CITED@, carried from brain_foundational_component_analysis.md / forward_predictive_objective design doc.
- Lerner, Honey, Silbert & Hasson (2011), *J Neurosci* 31(8):2906, topographic mapping of temporal receptive windows -- CITED@, live-verified (jneurosci.org, PubMed 21414912). Chien & Honey (2020, *Neuron*), constructing/forgetting temporal context -- CITED@, live-verified this cycle (search-result-confirmed, not full-text-fetched -- P_deflated for this specific pairing).
- DuBrow/Davachi-lineage event-boundary reinstatement (Sols, DuBrow, Davachi & Fuentemilla) and Baldassano et al. movie-boundary ripple findings -- CITED@, live-verified this cycle (biorxiv/JNeurosci/Nature Communications search results; specific author-paper pairing REASONED@ from search snippets, not full-text-confirmed -- deflate accordingly, P~0.5 on exact attribution details though the core empirical claim (boundary-triggered reinstatement) is well-established).
- Lambon Ralph, Jefferies, Patterson & Rogers (2017), *Nature Reviews Neuroscience* 18:42-55, hub-and-spoke -- CITED@, carried from drill_language_world_model_framing.md (previously live-verified).
- Frankland & Greene (2015, *PNAS*) role-general binding -- CITED@, carried.

All claims about our OWN system (slot-attention design, the convex-blend/mean-pool diagnosis, the
scene-segment-reduces-to-locality finding, the symbolic/neural pipeline split) are REASONED@,
carried from the cited session docs (already code-verified there, not re-derived this cycle) --
deflated 0.15-0.25 per the lit-scan calibration penalty; no new P estimate is asserted above
P<=0.50 for any novel-synthesis claim in this note.
