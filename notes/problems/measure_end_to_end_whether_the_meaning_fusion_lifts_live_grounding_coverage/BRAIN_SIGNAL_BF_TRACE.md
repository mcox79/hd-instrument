# BOTTOM-UP BRAIN-SIGNAL TRACE of word-meaning grounding (2026-09-10)

Owner: "we do NOT understand what we're working on -- understand deeply how the brain does this, ALL the signals,
then trace bottom-up where those signals are handled through the entire chain, and how brain-foundationally."

## THE FRAMING ERROR (the root cause of every failed lever)
We compute word-meaning as a NOUN -- a stored vector retrieved and compared ("which stored vector is nearest?").
The brain computes it as a VERB -- a PREDICTION made from the running context and updated by PREDICTION ERROR
("what update to my running model of the situation does this word imply, and how well does it fit what I
predicted?"). Meaning-in-context is the POSTERIOR over conceptual/situation states given the word AND the context
(Rabovsky Sentence-Gestalt 2018; predictive coding, Kutas-Federmeier 2011). Static word-similarity is the
DEGENERATE ZERO-CONTEXT special case -- what you compute after throwing the context away. This is WHY every static
lever (is-a W28/W29, confidence W23/25, componential W32/W33) won on the SimLex ranking proxy but did NOT transfer
to the live loop: the live loop's currency is PREDICTION ERROR over a running model, and a static-similarity channel
produces no prediction, hence no error, hence nothing for the loop to consume.

## THE TRACE -- every brain signal vs our sense-assignment chain (BU = bottom-up/stimulus-driven; TD = top-down/predictive/control)
| # | brain signal (source) | BU/TD | our sense-assignment chain | LANDED organ (if any) | status | BF fidelity / gap |
|---|---|---|---|---|---|---|
| 1 | visual word-form / morphology | BU | normalize_lemma (morphy) | -- | PRESENT | BF-spirit; WordNet-morphy residual (W30) |
| 2 | lemma / frequency / familiarity | BU prior | lemma + gain=log1p(tokens) | -- | PARTIAL | frequency-as-prior partial |
| 3 | ATL amodal HUB (feature-correlation metric) | BU | grounded = Lancaster sensorimotor = ONE SPOKE | `composed_hub_predictor` (ATL-hub, LANDED) | MISHANDLED | we use a SPOKE not the HUB; the hub organ exists but is UNWIRED to the decision |
| 4 | modality spokes | BU content | grounded (Lancaster) = sensorimotor spoke | valence_polarity (affect spoke, latent) | PARTIAL | one spoke live; others latent/absent |
| 5 | PREDICTIVE pre-activation of next meaning | TD | ABSENT from the decision | `predictive_reader`, `predictive_world_model`, `composed_hub_predictor` (LANDED) | ABSENT (organ exists, UNWIRED) | the load-bearing TD signal; not consumed by sense-assignment |
| 6 | N400 = integration PREDICTION ERROR | TD x BU | ABSENT | `n400_coherence_monitor` (LANDED) | ABSENT (organ exists, UNWIRED) | no prediction -> no error signal for the loop to consume |
| 7 | CONTEXTUAL sense SELECTION (biased competition) | TD | ABSENT -- static per-word vector = frequency-avg over senses = the PROTOTYPE | `graded_competition` (LANDED) | ABSENT (static version HARD_FAILed; PREDICTIVE version UNTESTED) | our vector structurally cannot represent "the context-licensed sense", only the dominant one |
| 8 | SEMANTIC CONTROL (IFG selection / pMTG retrieval) | TD | ABSENT | -- | ABSENT | no controlled amplify/suppress of context-(ir)relevant senses |
| 9 | reliability-weighted cue combination | TD gain | gain-ratio fusion (Ma-Pouget) | convergent_cue_reader | PRESENT | BF; but the gains measured weak/uninformative on this task |
| 10 | COMPOSITIONAL binding + feedback | TD constraint | ABSENT (bag/per-word; parser removed) | binding (FHRR), `bound_event_backbone` | ABSENT | argument structure does not constrain word meaning |
| 11 | RUNNING SITUATION MODEL (the TD state gating 5-8) | TD state | ABSENT from the decision | `predictive_world_model`, `bound_event_backbone`, `generalized_event_knowledge`, `graded_temporal_context` (LANDED) | ABSENT (organs exist, UNWIRED) | no running event/entity/time model gating sense-assignment |
| 12 | EPISODIC / hippocampal FAST-MAPPING (novel words) | BU+TD | count-ACCUMULATION over many exposures (grow-by-reading) | Library / consolidation gate | MISHANDLED | our loop's EXACT JOB (ground novel words) done by slow accumulation, NOT one-shot episodic binding |
| 13 | taxonomic vs thematic relational coding | BU (two stores) | co-occurrence PPMI = THEMATIC signal doing a TAXONOMIC job | (differentia W24 = weak taxonomic) | MISHANDLED | the relatedness-vs-identity wall, now precisely named |
| 14 | grounding DECISION (familiarity vs recollection) | BU+TD | SDT familiarity gate (+ recollection W25, weak) | convergent_cue_reader / SDT | PARTIAL | familiarity present; recollection weak/uncaptured |
| 15 | ERROR-DRIVEN learning (the N400 error IS the update) | TD->plasticity | ABSENT (Hebbian count accrual, not error-driven) | -- | ABSENT | learning is accumulation, not prediction-error-driven |

## SYNTHESIS -- what the trace reveals
Our sense-assignment chain faithfully implements the BOTTOM-UP / STATIC HALF (signals 1, 2, 4, 9, 14 present or
partial; each BF or BF-spirit). It is MISSING THE ENTIRE TOP-DOWN / PREDICTIVE HALF -- signals 5, 6, 7, 8, 10, 11,
15 -- which is precisely the machinery the brain's comprehension RUNS ON. And the ATL HUB (3) and EPISODIC one-shot
grounding (12) are MISHANDLED (we use a spoke for the hub; we accumulate counts where the brain binds in one
episode -- our loop's exact job). The decisive discovery of the trace: the top-down organs ALREADY EXIST as landed
BF modules -- `predictive_world_model` (running model + prediction), `n400_coherence_monitor` (prediction error),
`composed_hub_predictor` (ATL hub + forward prediction), `predictive_reader`, `graded_competition` (biased
competition/sense-selection), `bound_event_backbone` / `generalized_event_knowledge` / `graded_temporal_context`
(situation model) -- but the SENSE-ASSIGNMENT DECISION never routes through any of them. It is computed by static
nearest-vector cosine + fusion + SDT gate.

So the gap is ARCHITECTURAL, not a missing channel: we have been adding STATIC channels to a NOUN-shaped decision,
when the decision must be re-cast as a VERB -- a prediction-error / biased-competition computation that consumes the
running world-model. This is a category error, and it explains every non-transferring lever. The fix reuses landed
organs (the FULL-STACK-UPSTREAM directive): make the running world-model (predictive_world_model / bound_event_backbone)
the top-down PRIOR, let the incoming word's coactivated senses SETTLE under that prior (graded_competition, biased by
the situation model), score the PREDICTION ERROR (n400_coherence_monitor / composed_hub_predictor), and use that
error as the grounding-fit AND the learning signal (error-driven, signal 15). This is the FAIR test our two HARD_FAILed
STATIC context-conditioning cells (`exp_context_conditioned_sense_selection_v1/v2`) never ran, and it is the
already-designed-but-unbuilt ANGLE_B architecture ("the meaning IS the prediction").

## THE ONE-LINE ANSWER to "what are we working on"
Not "pick the nearest stored meaning" -- but "predict the meaning from the running situation and correct by the
error." We built the lookup; the brain runs the loop; the loop's organs are already on disk, unwired to the decision.
