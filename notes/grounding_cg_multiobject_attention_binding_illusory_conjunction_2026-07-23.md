# Grounding chain-grade shot: attention-gated MULTI-OBJECT feature binding (the Treisman binding problem) 2026-07-23

## WHY (brain-drill + dedup)
Grounding priority (#2 on the critical path). MECHANISM works (content-aware grounding 29438; soft-shard store 29444) but demonstrated narrowly. Dedup: existing attention cells = MEMORY-ROUTING (attention_binding_router RETRIEVE/REFUSE) + salience/reliability gates + grounding-SYSTEMATICITY (free-by-construction, bind_heldout=1.0/flat=0.0 = MM). UNTESTED: the actual TREISMAN BINDING PROBLEM -- multi-object scenes where features must bind to the RIGHT object without ILLUSORY CONJUNCTIONS.

BRAIN (fair-replication REQUIREMENTS -- must include ALL components the brain uses):
- **Barsalou** perceptual symbols: meaning = re-simulation of perceptual states; association/convergence zones bind distributed attributes (color, shape, ...).
- **Treisman Feature Integration Theory:** (1) PRE-ATTENTIVE stage -- features (color, shape, orientation) registered in PARALLEL in INDEPENDENT feature maps (free-floating); (2) FEATURE-INTEGRATION stage -- a SPOTLIGHT OF ATTENTION binds features from separate maps into an object. Attention is the brain's SOLUTION to the binding problem.
- KEY: artificial vision/VLMs are MARKEDLY WORSE at binding than the brain, esp. multi-object/cluttered/feature-sharing scenes (illusory conjunctions). Our native VSA bind + the crosstalk-fix (sharding/attention) is a plausible-UNPROVEN edge.

FAIRNESS DIRECTIVE (USER 07-23): replicate ALL the brain's components -- MUST include (a) parallel independent feature maps, (b) an ATTENTION spotlight that selects+binds, (c) the binding. Stripping attention = the same unfairness as stripping the depth cue from the parser. The can-fail control (no-attention) MUST fail via illusory conjunctions -> proves attention is load-bearing (the brain's component).

## WHAT to build
Multi-object visual-scene feature binding, glass-box:
- SCENE: >=2 objects, each = (color, shape) [+ optionally position], possibly cluttered / feature-sharing (e.g. red-circle + blue-square; hard case shares a feature: red-circle + red-square).
- LEARNED front-end: extract per-object feature activations (color map, shape map) from pixels (glass-box, no CNN -- reuse the content-aware grounding front-end 29438). Features free-floating (not yet bound).
- ATTENTION spotlight: select an object/location and bind ITS features (color_k (x) shape_k) into an object hypervector; iterate over objects (serial attention, Treisman).
- READOUT: query the scene rep for "what color is the circle?" / "is there a red square?" -- correct binding answers correctly; illusory conjunction answers wrong.

## ARMS (one variable = attention-gated binding)
- ARM_ATTN_BIND (the substrate + brain mechanism): attention spotlight + VSA bind per object.
- ARM_FLAT (must-fail, = the VLM/pre-attentive-only failure): bag of free-floating features, no attention binding -> should suffer ILLUSORY CONJUNCTIONS in multi-object/feature-sharing scenes.
- (control) ARM_ATTN_NOBIND or ARM_BIND_NOATTN: isolate that BOTH attention AND binding are needed.

## DISCRIMINATOR (can-fail, brain-faithful, fair)
- HARD_PASS: ARM_ATTN_BIND correctly answers object-feature queries in MULTI-OBJECT / feature-sharing scenes (few illusory conjunctions) WHILE ARM_FLAT fails (illusory conjunctions ~chance on the hard feature-sharing cases); AND generalizes to NOVEL feature-conjunctions (train red-circle/blue-square, test red-square); learned front-end -> LEARNING CURVE rises.
- HARD_FAIL (must be possible): ARM_ATTN_BIND ALSO suffers illusory conjunctions at scale (crosstalk beats attention) -> earned bound (additive superposition crosstalk defeats attention; the fix would be sharding per attended object).
- HONESTY on free-by-construction: the NOVEL-CONJUNCTION generalization alone may be free-by-construction (VSA gives red(x)square for free) -> that is NOT the headline. The headline = the NON-free part: MULTI-OBJECT binding WITHOUT illusory conjunctions in cluttered/feature-sharing scenes, where additive crosstalk is real and attention is load-bearing. Report both separately; the CG claim rests on the crosstalk/illusory-conjunction result, not the free algebra.
- ANTI-CHEAT: scramble attention (bind random objects' features) -> collapses; feature-sharing HARD subset must be included (else trivial); real image features (reuse 29438 Olivetti/shape front-end) not synthetic one-hots.
- FAIR: bit-exact baselines; ONE variable; difficulty-on (feature-sharing clutter); DEDUP vs exp_cortex_attention_binding_router (memory-routing, DIFFERENT), grounding_bind_chain_systematicity (free-by-construction, DIFFERENT), attention_salience gates (reliability, DIFFERENT) -- this is VISUAL multi-object feature binding / illusory conjunctions, novel.

## POINTERS
- experiments/exp_grounding_bind_chain_systematicity_v1.py -- systematicity harness (free-by-construction ref; differentiate).
- the 29438 content-aware grounding front-end + 29444 soft-shard store (reuse front-end + the per-object sharding as the crosstalk fix if HARD_FAIL fires).
- exp_cortex_attention_binding_router_v2*.py -- adjacent attention-routing (differentiate: that is memory routing, this is visual feature binding).

## AUTONOMY
exp_dev designs ALL params + does the final KB/prior-art dedup: scene generator, #objects, feature-sharing ratio, attention mechanism specifics, seeds, band VALUES, queue/inline, anchor, ETA. If dedup finds this exact test already banked, REPORT + do not re-run.
