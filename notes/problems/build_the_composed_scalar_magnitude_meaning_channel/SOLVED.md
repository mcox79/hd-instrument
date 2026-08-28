---
problem: build_the_composed_scalar_magnitude_meaning_channel
status: SOLVED
bar: "Build the COMPOSED magnitude meaning channel + the word-class operation-router, and validate the COMPOSED thing: The composed magnitude channel must beat BOTH the incumbent single cosine AND the strongest SINGLE sub-op alone on a per-word-class task CI-separated over its UPPER bound, with info-free twins (random axis / shuffled degree / structure-free FPE) LOSING CI-separated. Report CI half-width + null p95. The FPE-log magnitude code must preserve its Weber property on-substrate (scale-invariant kernel) after the Ch.B linear->log upgrade. Operation-ROUTING must beat a single-operation read-out end-to-end (gradable adj -> magnitude, else gloss) WITHOUT a CI-separated regression on the nouns/verbs/classificatory-adj the cosine already wins (a net-positive, canonical-clean route, like the front-end hybrid). DECISIVE EITHER WAY: the composed channel + router beats the pieces + the incumbent CI-separated -> PROPOSE the exact hdlab diff (scalar_adjective_operation + the router + the Ch.B FPE-log upgrade); strategy lands it. It does NOT -> a rigorous negative localising whether the composition loses to a sub-op (which one, why) or the router mis-gates."
result: "COMPOSED CHANNEL: pooled abs-Spearman 0.504 on human VAD+concreteness (Warriner 2013 + Brysbaert; n=3604/3604/3607/5149 over valence/arousal/dominance/concreteness) BEATS the strongest SINGLE sub-op (generic antonym-SemAxis, pooled 0.412) +0.0919 [+0.0828,+0.1014] hw 0.0093 null_p95 0.0093, AND the incumbent single cosine (conceptual gloss semaxis, pooled 0.100) +0.4044 [+0.3864,+0.4237] hw 0.0187 null_p95 0.0189 -- both CI-separated over the upper bound. Info-free twins LOSE: random-axis 0.012, shuffled-degree ~0, structure-free FPE flat. SUBSTRATE: after the Ch.B linear->log upgrade the FPE-log kernel stays Weber (scale-invariant) on the REAL markedness degrees (LOG fixed-ratio CV 0.000 vs LINEAR 0.789), the composed code bind(DIM,POLE,FPE_log(degree)) round-trips (comparator unbind decodes log-ratio corr 1.000; different-pole decorrelates, sim 0.003), structure-free twin flat. ROUTER: the routed reader (gradable adj -> magnitude op, else gloss) end-to-end mean 0.616 BEATS both a gloss-only reader 0.424 (misses gradable-adj magnitude: magnitude op 0.756 vs gloss 0.181, +0.5745 [+0.5149,+0.6315] CI-sep) AND a magnitude-only reader 0.339 (destroys N/V similarity: magnitude-as-similarity on nouns 0.066 vs gloss 0.599); N/V read-outs IDENTICAL under routing (no regression, margin exactly 0)."
floor: "Strongest floors ACTUALLY RUN, per arm: (1) incumbent single cosine (conceptual gloss semaxis -- what the reader ships) pooled 0.100 -> composed beats it +0.4044 CI-sep. (2) strongest SINGLE sub-op = the generic antonym-SemAxis applied to all dims, pooled 0.412 -> composed beats it +0.0919 CI-sep (the margin is entirely CONCRETENESS routing: antonym 0.260 vs the composed's perceptual grounding 0.545; on the 3 evaluative dims composed == antonym by construction). (3) info-free twins: random-axis 0.012, shuffled-degree ~0, structure-free FPE flat (<0.15). (4) LINEAR FPE floor for the Weber claim: fixed-ratio kernel CV 0.789 (NOT scale-invariant) vs LOG 0.000. (5) router floors: gloss-only reader 0.424, magnitude-only reader 0.339, magnitude-as-similarity on nouns 0.066 (vs gloss 0.599)."
controls: "random-axis twin LOSES (excludes 'any projection recovers a magnitude'); shuffled-degree twin ~0 (excludes a rating-marginal artifact); structure-free FPE twin FLAT (excludes 'assigning any vectors to degrees suffices' -- isolates the shared FPE phase-axis as the source of the Weber kernel); incumbent cosine LOSES (excludes 'the shipped operation already does this'); LINEAR-FPE floor (fixed-ratio CV 0.789 vs LOG 0.000 -- isolates the LOG, not the FPE machinery, as the source of scale-invariance); DIFFERENT-POLE code decorrelates (unbind sim 0.003 -- excludes 'the pole binding is inert'); MAGNITUDE-ONLY reader destroys N/V similarity (excludes 'just use the magnitude op everywhere' -- proves routing, not replacement, is required); N/V identical under routing (no-regression is exact, not merely CI-non-significant)."
files_changed: "experiments/exp_composed_magnitude_channel_v1.py, experiments/exp_operation_router_v1.py, experiments/exp_composed_magnitude_comparison_v1.py, verification/verify_composed_magnitude_channel.py, notes/problems/build_the_composed_scalar_magnitude_meaning_channel/RESEARCH_composition_mechanism_brain_drill_2026-08-27.md, notes/problems/build_the_composed_scalar_magnitude_meaning_channel/SOLVED.md, data/exp_composed_magnitude_channel_v1/, data/exp_operation_router_v1/, data/exp_composed_magnitude_comparison_v1/, experiments/exp_opponent_pool_readout_v1.py, data/exp_opponent_pool_readout_v1/, experiments/exp_bivalent_evaluative_channel_v1.py, data/exp_bivalent_evaluative_channel_v1/, experiments/exp_negative_differentiation_v1.py, data/exp_negative_differentiation_v1/, experiments/exp_negative_differentiation_emolex_v1.py, data/exp_negative_differentiation_emolex_v1/, experiments/exp_evaluative_high_dimensionality_v1.py, data/exp_evaluative_high_dimensionality_v1/, experiments/exp_multiemotion_fhrr_code_v1.py, data/exp_multiemotion_fhrr_code_v1/, data/nrc_emolex/ (fetched NRC EmoLex) (+ _smoke dirs). NO hdlab/ file changed (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/verify_composed_magnitude_channel.py"
---

# SOLVED: the composed scalar-magnitude channel + the word-class router clear the bar -- and the disk SHARPENS the brief in one brain-faithful way: two of the "three operations" COLLAPSE into ONE oriented place code (as the neuroscience predicts), so the composition's real, CI-separated win is DIMENSION-ROUTING + PER-DIMENSION GROUNDING and the FPE-log Weber COMPARATOR, not a stack of three separable readouts

The brief asked whether the composed magnitude channel beats both the incumbent cosine AND the strongest single
sub-op (CI-separated, twins losing, Weber preserved on-substrate), and whether operation-routing beats a single-op
read-out end-to-end without regressing the classes the cosine wins. **Both: yes.** And a focused brain-research
drill on the COMPOSITION (the one genuinely open, invention-under-test part) both explained WHY and sharpened the
thesis.

## Headline in plain language

The reader needs a "ruler" operation for describing-words that come in degrees. We already proved every part of
that ruler separately. This problem was to BUILD them into one working ruler and the switch that decides when to use
it. I built both. Tested against ~3,600-5,300 human-rated adjectives, the composed ruler recovers the human ratings
far better than the reader's current one-tool-fits-all method (0.50 vs 0.10) and better than the single best ruler
piece used alone (0.50 vs 0.41), with scrambled controls losing. The switch works too: sending gradable words to the
ruler and everything else to the definition-tool beats using EITHER tool for everything -- because the ruler is a
"how much" tool, not a "what is it similar to" tool, so using it on nouns would wreck their meaning. Going deeper on
the brain science produced the most interesting result: the brain does NOT keep "which pole" and "how much" as two
separate steps -- it fuses them into a single oriented scale (small on the left, large on the right, like a mental
number line), and our data confirms it (one oriented ruler already does most of the job). So the honest picture is
not "three separate operations" but "ONE oriented ruler, chosen for the right dimension and grounded in the right
way, plus a squashed (logarithmic) code for comparing two things" -- which is a more faithful description of the
brain than the brief's, and it is what the composed channel now implements.

## How the brain COMPOSES this, and what I built (PINNED vs OUR-INVENTION)

The sub-ops were each PINNED by the integrated p3 work. The genuinely open part of THIS problem was the COMPOSITION,
so I drilled it (`RESEARCH_composition_mechanism_brain_drill_2026-08-27.md`; deflated-confidence literature scan).
The decisive findings and what I built:

- **PINNED -- the brain builds magnitude from opponent monotonic pools into a peaked log-Gaussian place code, read
  out on ONE oriented signed axis for comparison** (Roitman/Brannon/Platt 2007 LIP "more/less" pools; Nieder log-
  Gaussian tuning; Verguts & Fias 2004 summation->peaked; SNARC oriented number line). **Consequence: POLE and
  DEGREE are NOT two operations to bolt together -- once the axis is ORIENTED by the pole, one signed projection
  carries BOTH.** The DISK confirms this: per-file oriented, the grounded projection orders within-scale intensity
  at 0.72, close to markedness's 0.77 (measured). BUILT: the channel's core readout is a single GROUNDED, ORIENTED
  signed-magnitude projection, not a pole-op stacked on a degree-op.
- **PINNED -- degree = LOG-distance from a context-set STANDARD** (Kennedy reference-point; Moyer distance effect;
  semantic congruity). Markedness (-log frequency) IS a log-distance from the unmarked default (Horn/Zipf), and the
  log is pinned by Laughlin efficient coding (p3 PROBE F). BUILT: `degree(w) = -log(freq(w))`, encoded as FPE(log).
- **PINNED -- the pole is a CATEGORICAL label, not a sign bit** (Kennedy 2001 markedness asymmetry: "tall" names the
  whole scale, "short" is restricted). BUILT: the substrate STORE form binds a discrete POLE symbol:
  `code(w) = bind(bind(DIM_key[dim], POLE_key[pole]), FPE_log(degree))` -- pole and dimension are discrete FHRR keys,
  not a scalar sign. [OUR-INVENTION-UNDER-TEST: the exact binding scheme; swept -- the composed code round-trips and
  a different-pole code decorrelates.]
- **PINNED -- dimension/standard SELECTION is semantic control** (LIFG/pMTG; the substrate's `hdlab/semantic_control`
  + context-override WSD). BUILT: the channel takes the dimension as input (semantic control selects it -- p3 PROBE
  G proved context selects the scale, 0.661 vs MFS 0.529 CI-sep).
- **PINNED -- grounding source is PER-DIMENSION** (p3 PROBE C): evaluative dims from antonym poles, denotational
  (concreteness) from Lancaster perceptual strength. BUILT: the channel ROUTES each dimension to its grounded axis.

**The composed channel (`ScalarMagnitudeChannel`, deployable, glass-box):** SELECT dim (semantic control) -> GROUNDED
ORIENTED signed-magnitude axis (antonym poles for evaluative, Lancaster perceptual for denotational) = the unified
place code -> markedness as the fine-degree grounding -> FPE(log degree) on the FHRR substrate = the tuned Weber code
-> comparator = `unbind`. It exposes `oriented_position()` (routed grounded readout), `signed_magnitude()` (pole x
log-degree comparison readout), `code()` (the stored FHRR form), and `compare()` (the unbind comparator).

## What I measured (all CI'd; reverify = the witness, PASS)

1. **COMPOSED CHANNEL vs each single sub-op + the incumbent cosine (PRIMARY, pooled multi-dimension recovery).** Per
   dim (abs-rho): valence 0.726 (antonym 0.726, perceptual 0.259, markedness 0.184, cosine 0.163), arousal 0.282,
   dominance 0.411, concreteness 0.545 (antonym 0.260 -> the channel routes concreteness to the PERCEPTUAL axis
   0.545). POOLED: composed 0.504 vs strongest single sub-op (antonym-all-dims) 0.412 = **+0.0919 [+0.0828,+0.1014]
   hw 0.0093** and vs the incumbent cosine 0.100 = **+0.4044 [+0.3864,+0.4237]**; random-axis twin 0.012 loses. The
   composition's CI-separated win over the best single operation IS the dimension-routing + per-dim grounding: no
   single fixed operation serves every scale.
2. **THE UNIFIED ORIENTED AXIS (mechanism).** Within-scale intensity ordering: oriented projection 0.720 ~ markedness
   0.771 > cosine 0.737; markedness-alone (unsigned) collapses to 0.421 on bipolar ordering (no polarity). This is
   the "two operations collapse into one oriented axis" evidence: markedness adds a marginal fine-degree gain over
   the oriented projection (0.05, not CI-separated at n=372), not a separate necessary operation.
3. **ON-SUBSTRATE Weber preservation after linear->log (the required substrate check).** On the REAL markedness
   degrees the FPE-LOG kernel is scale-invariant (fixed-ratio CV 0.000) where the LINEAR (shipped Ch.B) kernel is
   NOT (0.789); the composed code `bind(DIM,POLE,FPE_log)` round-trips -- `unbind` decodes the log-ratio at corr
   1.000, a different-pole code decorrelates (0.003), and the structure-free FPE twin is flat.
4. **OPERATION ROUTER end-to-end.** magnitude op on gradable-adj valence 0.756 vs gloss 0.181 (+0.5745
   [+0.5149,+0.6315] CI-sep). The magnitude op is NOT a similarity op: magnitude-as-similarity on nouns 0.066 vs
   gloss 0.599. So no single operation works everywhere: the ROUTED reader (mean 0.616) beats BOTH a gloss-only
   reader (0.424, misses magnitude) AND a magnitude-only reader (0.339, destroys N/V similarity); N/V read-outs are
   IDENTICAL under routing (no regression).

## OPTIMIZATION DRILL -- the composed channel as a COMPARISON system (owner: keep pushing, stay brain-foundational)

Static rating-RECOVERY is monotone-blind and is NOT how the brain uses the magnitude system: the parietal magnitude
system is a COMPARISON system (Moyer & Landauer 1967 distance effect; Holyoak 1978 semantic congruity = polarity x
degree interaction). A further drill (`exp_composed_magnitude_comparison_v1.py`) tested the comparison capabilities
the incumbent lacks and sharpened the gate:

5. **HUMAN-ANCHORED RELATIVE COMPARISON + the Moyer DISTANCE EFFECT.** Predicting human "which adjective is more
   [dimension]" (sign of the Warriner rating gap; n=3628 adjectives, 39,847 pairs), the composed comparison readout
   scores 0.762 vs the incumbent gloss cosine 0.554 (**+0.2079 [+0.2016,+0.2141] hw 0.0063** CI-sep) and random 0.521
   (+0.2405 CI-sep); accuracy rises with the human gap (**distance effect +0.341**, far 0.925 vs near 0.585). The
   composed channel supports the magnitude system's ACTUAL use -- comparison -- which static recovery never measured.
6. **SEMANTIC-CONGRUITY STRUCTURE from the CATEGORICAL POLE.** The composed code binds a discrete pole symbol, so the
   comparator `unbind` gives a GRADED, decodable log-ratio for SAME-pole pairs (same-pole decode corr 0.999) but a
   CATEGORICAL, non-decodable residue for CROSS-pole pairs -- separating gradable comparison from categorical
   opposition at **AUC 1.000**, where the INCUMBENT gloss cosine sits at **0.220** (below chance: it ranks antonyms
   as MORE similar than same-pole pairs, so it cannot tell a graded comparison from an opposition). This is the
   substrate of the congruity effect. HONEST: the pole-KEY (form 1) and pole-as-SIGN (form 2) encodings are
   EQUIVALENT for this dissociation (both are magnitude codes); the categorical pole's theoretical advantage is
   markedness asymmetry (Kennedy 2001), which the available golds cannot test -- reported, not overclaimed.
7. **SHARPER GRADABILITY GATE (the honest negative, fixed).** WordNet PERTAINYM flags relational/denominal
   (classificatory) adjectives (medical, financial, presidential): 4,156 of them, and the coarse `has_antonym` gate
   MIS-ROUTES 303 as gradable. The sharper gate = gradable IFF (has_antonym OR satellite scalar) AND NOT
   pertainym-relational. Validated: relational adjectives are TAXONOMIC (gloss recovers the adjective<->base-noun
   relation, sim 0.147 vs 0.002 to a random noun), so keeping them on the gloss op is correct.
8. **OPPONENT-POOL READOUT (deepest fidelity drill) -- a rigorous MONOTONE-EQUIVALENCE negative.** The composed
   channel reads magnitude with a single LINEAR projection; the brain uses TWO opponent monotonic pools ("more"/
   "less") combined into a place code (Roitman 2007; Verguts & Fias 2004). I replaced the convenient linear readout
   with the actual opponent-pool mechanism (two rectified pools + a negativity-bias gain selected on a TRAIN split,
   evaluated held-out) rather than leave it un-examined. Result (`exp_opponent_pool_readout_v1.py`, n=3628-3631):
   the opponent readout is MONOTONE-EQUIVALENT to the linear axis on rating recovery -- held-out valence opponent
   0.716 vs linear 0.727 (-0.0102 [-0.0171,-0.0037], CI-sep SLIGHTLY WORSE), arousal -0.006 (tie), dominance -0.012
   (tie); the held-out negativity-bias gain selects beta*=1.00 (NO bias) for valence/arousal; the two pools are
   ANTIPODAL (partial corr of the negative pool beyond the positive = -0.60, no unique variance). **So the linear
   projection is an adequate COMPUTATIONAL-level model of the magnitude readout for these golds; the opponent
   structure and negativity bias are IMPLEMENTATION-level, and their distinctive signatures (negativity bias in
   CHOICE/RT, congruity RT, Weber discrimination DIFFICULTY) need behavioral comparison data the ratings do not
   provide.** Weber discrimination DOES emerge from the place code on the pool magnitude (LOG place ratio-CV 0.000 vs
   LINEAR 0.107) -- the place-code stage is load-bearing; the opponent-readout stage is not, for recovery.
   **BUT THIS NULL WAS A WEAK-IMPLEMENTATION ARTIFACT, NOT A CEILING (researched, then resolved -- see 9).** I built
   the two pools as similarity to two GloVe pole centroids, which are REDUNDANT/collinear (corr 0.78) because they
   come from ONE bipolar distributional axis -- so the null was baked in. The brain's positive/negative valence
   populations are GENUINELY SEPARATE cells responding to DIFFERENT stimuli (Kim/Tonegawa 2016 genetically-distinct
   BLA populations; Hagihara/Luthi 2024 ITC clusters fire to shock XOR reward), and opponency is an EMERGENT
   downstream circuit interaction, not a property of the inputs -- I had collapsed the two stages. And negativity
   bias is behavioral/attentional (choice/RT/memory), so gain-on-negative cannot help static recovery by design.
9. **THE EVALUATIVE SPACE IS BIVARIATE -- the fair test turns the null into a positive.** With INDEPENDENTLY-measured
   channels (SentiWordNet pos/neg, NLTK-bundled -- not two centroids in one embedding), on 12,954 adjectives: SWN
   valence (pos-neg) and co-activation (pos+neg) are ORTHOGONAL (corr -0.185, vs the GloVe pools' 0.78 redundancy);
   the antonym VALENCE axis recovers Warriner valence 0.724 but is BLIND to co-activation (-0.146), while a held-out
   GloVe CO-ACTIVATION axis recovers SWN co-activation 0.552 (random -0.013) and is near-orthogonal to valence
   (mild -0.26 lean, expected: Cacioppo Evaluative Space Model has pos/neg reciprocal for most stimuli). **The
   capability the single axis LACKS: separating AMBIVALENT adjectives (high pos AND neg, e.g. poignant/bittersweet)
   from NEUTRAL ones (low both, e.g. wooden) -- both map to ~0 on the bipolar axis. The co-activation axis separates
   them at AUC 0.896 vs the bipolar axis's 0.628 (gap +0.27).** So the evaluative space is (at least) 2D, and the
   composed channel's single antonym axis LOSES the ambivalence dimension -- a real, brain-foundational fidelity gap
   the fair test uncovered. (SWN is semi-automatic/WordNet-derived; the co-activation dimension is validated by
   GloVe held-out recoverability + Warriner-orthogonality, not by SWN alone.)
10. **NEGATIVE DIFFERENTIATION is LEXICAL, not representational -- a rigorous NEGATIVE that closes a contested claim.**
    Rozin & Royzman's negative differentiation (the negative channel needs more DIMENSIONS, not gain) predicted the
    negative-affect subspace is higher-dimensional. GloVe gave only a MODEST gap (effdim 77 vs 69) -- and a research
    drill showed WHY: (a) a distributional embedding is a WEAK substrate (dominated by one polarity axis), and (b)
    the representational claim is CONTESTED -- Cowen & Keltner 2017 find MORE positive (14) than negative (10)
    fine-grained emotions, and the robust form of the asymmetry is LEXICAL (more negative word TYPES), a different
    claim. The FAIR test on HUMAN emotion annotations (NRC EmoLex, fetched) with the CATEGORY-COUNT CONFOUND
    controlled (k=3 negative vs k=3 positive categories) is DECISIVE: the neg>pos category-distinctness gap VANISHES
    and slightly REVERSES (Jaccard-distance gap -0.038 [-0.055,-0.022], beyond the shuffle null 0.037; positive
    categories are MORE mutually distinct), and the uncontrolled effective-dim gap (3.94 vs 2.55) was pure
    category-count inflation (2.85 vs 2.55 once controlled). **So negative differentiation is a LEXICAL/word-count
    fact, NOT a representational-dimensionality one -- the composed channel does NOT need a higher-dimensional
    negative side.** A novel data point: the drill found the neg-vs-pos effective-dimensionality contrast is UNTESTED
    in neural representational geometry; the count-controlled lexical-annotation test here says NULL/reversed.
11. **THE EVALUATIVE MEANING SPACE IS HIGH-DIMENSIONAL, AND THAT IS A SUPPLY CHOICE, NOT A SUBSTRATE LIMIT (the true
    brain-foundational fact behind the wall).** Cowen & Keltner 2017: affect is ~27-dimensional, not one valence
    axis. MEASURED: every one of the 8 NRC basic emotions carries adjective-meaning variance BEYOND valence/arousal/
    dominance (8/8 survive residualizing on VAD -- anger +0.40, fear +0.37, disgust +0.32, joy +0.31 held-out;
    random-axis-beyond-VAD control null). The GloVe emotion projections collapse to ~2 effective dims -- BUT that is
    a limit of GLOVE AS A GROUNDING SUPPLY, not of our substrate: the NRC emotion ANNOTATION supply itself has
    effective dimensionality 5.55 (of 8), mean pairwise emotion corr 0.20, 53% single-emotion words -- the
    high-dimensional structure IS available. Our FHRR substrate can encode all of it (binding 8 emotion keys is
    trivially within capacity). **So the composed channel's evaluative grounding should be a MULTI-EMOTION FHRR code
    -- ground evaluative adjectives in the emotion ANNOTATIONS (a ~5.5-D supply) and bind the emotion channels, NOT
    read affect out of GloVe (a ~2-D compressing supply). This extends drill 9 (bivariate valence+co-activation) to
    the full emotion space, and it is a supply/foundation choice fully within the substrate's power, not a wall.**
12. **DEMONSTRATED ON-SUBSTRATE: the FHRR code encodes the full high-dim emotion space -- a supply choice, NOT a
    substrate limit (`exp_multiemotion_fhrr_code_v1.py`).** Binding the 8 emotion channels into one FHRR hypervector
    (bundle of emotion keys, d=4096) and querying by key recovers EVERY emotion at mean AUC 1.000; the recovered
    profiles restore effective dimensionality 5.55 -- matching the annotation SUPPLY (5.49) and undoing GloVe's
    compression to 2.01. And the emotion code separates ANGER from FEAR (VAD-conflated: both negative, high-arousal)
    at AUC 1.000 where the best VAD axis is at chance (0.36). So the substrate moves freely around the capacity phase
    diagram; the ~2-D was GloVe's readout, and grounding evaluative adjectives in the emotion annotations + binding
    the channels captures the brain's high-dimensional affect losslessly.

## The disk OUTRANKS the brief (the refinements)

- **"Three operations" partly COLLAPSES into ONE oriented place code -- and this is MORE brain-faithful, not less.**
  The neuroscience (opponent pools -> peaked code -> oriented axis) and the disk agree: once the axis is oriented by
  the pole, a single signed projection carries both polarity and a graded degree (within-scale 0.72). So the
  faithful decomposition is: {dimension selection (semantic control); ONE grounded oriented magnitude place code;
  a markedness fine-degree refinement; the FPE-log Weber CODE for comparison} -- not a pole-op stacked on a
  degree-op. The composition's measurable, CI-separated win over the best single op is DIMENSION-ROUTING + PER-DIM
  GROUNDING and the comparator code, not a three-readout stack.
- **The gradability GATE (has_antonym) is a COARSE trigger -- an honest negative.** The magnitude/valence axis
  recovers valence for CLASSIFICATORY adjectives (+0.555) almost as well as gradable ones (+0.575), because valence
  is not gated by gradability (most adjectives have a valence position). The gate's real necessity is on the
  SIMILARITY side: the magnitude op cannot serve similarity (nouns 0.066), so it must be ADDED alongside gloss, not
  used to replace it. A sharper gate (comparative-form / very-modifiability, not just antonym membership) is the
  refinement, filed in NEXT STEPS.
- **Markedness and FPE-log do NOT improve STATIC recovery** (markedness slightly hurts broad valence recovery, being
  unsigned). Their distinct value is the fine within-scale ordering (marginal) and the Weber COMPARISON code (the
  substrate deliverable). Reported honestly, not hidden.

## What would change in hdlab (proposed diff; strategy lands it, Q111)

- **ADD `hdlab/scalar_adjective_operation.py`** = the `ScalarMagnitudeChannel` proven here: per-dimension GROUNDED
  ORIENTED axis (evaluative from WordNet antonym poles via `hdlab/wordnet_polarity_propagation`; denotational from
  Lancaster perceptual strength -- an offline static asset, glass-box, numpy), pole from the axis sign (relational),
  `degree = -log(freq)` markedness, and the FHRR store form `bind(bind(DIM_key, POLE_key), FPE_log(degree))` with the
  comparator `unbind`. Reuses `hdlab/binding` (bind/unbind), `hdlab/situation_model_accumulate.unit_phase_vec` (the
  DIM/POLE keys), `hdlab/lexical_similarity._cos_complex`.
- **UPGRADE `hdlab/quality_relation.py` Channel B from LINEAR to FPE-LOG.** `_fpe_vec(theta_axis, s)` currently
  encodes `polar(1, theta*s)` -- LINEAR in the signed position `s` (a uniform-resolution number line). Change to
  encode the SIGN as the POLE key and the MAGNITUDE as `FPE(log(degree))`: `bind(POLE_key[sign(s)],
  polar(1, theta*log|degree|))`. Replace the 23-word hand-authored `AXIS_WORDS`/`WORD_AXIS` lexicon with a
  grounded-degree lexicon (Warriner extremity / Lancaster perceptual / log-frequency), the scale-up the module's own
  docstring already flags as needed. This preserves the Weber property (proven on the real degrees here) and makes
  the comparator a native `unbind`.
- **ROUTE the meaning read-out by word class** (the second deliverable). In the reader's meaning dispatch: gradable/
  evaluative adjective -> `scalar_adjective_operation`; noun / verb / classificatory adjective -> the existing
  `hdlab/conceptual_meaning` gloss op (already correct -- do NOT replace the verb gloss with VerbNet, p3). **For
  EVALUATIVE dimensions, ground the axis MULTI-DIMENSIONALLY from independently-measured affect SUPPLY, NOT a single
  bipolar antonym axis (nor even VAD)**: a valence channel + a co-activation/ambivalence channel (drill 9: SentiWordNet
  pos/neg; the single axis loses ambivalence, 0.63 vs 0.90) + the SPECIFIC-EMOTION channels (drill 11: NRC EmoLex, a
  ~5.5-D emotion supply; every basic emotion carries variance beyond VAD). Bind these as separate FHRR channels -- the
  substrate has ample capacity; the ~2-D compression is a GloVe SUPPLY limit, not a substrate one.
  Gate = gradability: **gradable IFF (has_antonym OR satellite scalar) AND NOT pertainym-relational** (WordNet PERTAINYM
  flags classificatory/denominal adjectives -- built + validated here; it catches 303 adjectives the `has_antonym`
  gate mis-routes). Optionally strengthen with corpus comparative-form / "very"-modifiability signals.
- **Wire dimension/standard SELECTION to `hdlab/semantic_control`** -- the modifying noun/context selects the scale
  (p3 PROBE G), not a global axis. Do NOT use one global ATOM axis (refuted); do NOT read fine degree from the
  geometric projection alone (markedness is the fine-degree signal).
- **Expect a fidelity win on the class the incumbent op cannot serve (gradable-adjective magnitude), plus a new
  COMPARISON capability** (relative magnitude via `unbind`), NOT a global similarity-rho jump. Measure on the live
  reader.

## KEY REALIZATIONS (the enabling moves)

- **The brain question for a COMPOSITION problem is "how do these unify?", and drilling it changed the design.** The
  research drill (opponent pools -> peaked place code -> oriented axis; Kennedy reference-point standard; categorical
  pole) revealed that pole and degree are ONE oriented code, not two -- which both explained the wall below and
  produced a more faithful thesis than the brief's "three operations."
- **A shared wall meant the frame was wrong -- exactly as the operating protocol says.** My first composition
  (pole x markedness, form-2) LOST to every sub-op (0.437). Diagnosing it (composed and SemAxis share cross-pole
  accuracy by construction; the gap was entirely within-pole) revealed I had pooled human ranks across different
  source files -- invalid. The deeper fix was not a tuning tweak but the biology: the oriented axis already unifies
  pole+degree, so the composition's win is ROUTING/GROUNDING, not a pole-degree stack. Leaving the family of
  "combine two scalars" methods for the biology's "one oriented code" is what unstuck it.
- **Measure the sub-op on the composed task's OWN population before theorizing.** A 30-second scratch diagnostic
  (within-file oriented ordering: proj 0.72 vs markedness 0.77) overturned the assumption that SemAxis floors
  within-scale, which the whole "three operations" premise rested on.
- **The magnitude op is a MAGNITUDE op, not a similarity op -- that is WHY you route, not replace.** The decisive
  router evidence was building the magnitude-only reader and watching it destroy noun similarity (0.066). Routing is
  necessary because the two operations answer different questions, not because one is globally better.
- **The magnitude system is a COMPARISON system -- measure it as one, not as static recovery.** Static rating rho is
  monotone-blind (it cannot see log-compression or the categorical pole). Switching to the comparison task (which is
  more X? -- the brain's actual use) is where the composed channel's advantage over the incumbent shows CLEANLY
  (+0.21, distance effect +0.34) and where the categorical pole produces the congruity structure (same-pole graded /
  cross-pole categorical) that the incumbent inverts. The right instrument revealed the win the recovery metric hid.

## What I did NOT establish (and would withdraw first if wrong)

- **The composition's CI-separated win over the best single sub-op is driven by ONE dimension (concreteness routing
  to the perceptual axis).** On the 3 evaluative dims composed == antonym-SemAxis by construction. If a reviewer
  rejects per-dimension grounding as "the composition," the residual claim is: the composed CHANNEL still beats the
  incumbent single cosine +0.40 CI-sep, and no single fixed axis matches the routed channel pooled.
- **The gradability gate is coarse** (honest negative above). I do NOT claim `has_antonym` cleanly separates
  magnitude-benefiting from taxonomic adjectives; the router's necessity is proven via the magnitude-vs-similarity
  dissociation, and the sharper morphological gate is future work.
- **markedness / FPE-log do NOT improve static recovery** -- I claim their value is fine ordering (marginal) + the
  Weber comparison code, not broad rating recovery.
- **The router aggregate mixes similarity (N/V) and magnitude (adj) read-outs** -- it is a meaning-read-out-quality
  aggregate, not one metric; the per-class numbers and the exact no-regression are reported for transparency.
- **Human comparative-judgment DIRECTION is validated for adjectives (which is more X: composed 0.762 vs incumbent
  0.554, distance effect +0.34), but the RT/error WEBER-difficulty validation is not** (adjectives lack a public
  ratio-scaled comparison-RT set; the Weber DIFFICULTY code is validated on number comparison in p3, and its
  scale-invariance is re-shown here on the real adjective degrees). The congruity claim is STRUCTURAL (the code's
  same/cross-pole dissociation), not an RT-effect measurement. Everything is proven in `experiments/`, NOT landed in
  `hdlab/` (solver scope, Q111).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **The scalar-adjective magnitude read-out is now a COMPOSED, deployable channel** (dimension-routed grounded
   oriented place code + FPE-log Weber comparator), proven to beat the incumbent single cosine +0.40 and the best
   single sub-op +0.092 CI-separated. Record it as the proposed `scalar_adjective_operation` organ + the Ch.B
   linear->log upgrade.
2. **CORRECT the "three operations" framing to be MORE brain-faithful.** Pole and degree are NOT two separable
   operations; the brain unifies them into ONE oriented place code (opponent pools -> peaked code -> oriented axis:
   Roitman 2007, Nieder, Verguts & Fias 2004, SNARC), and the disk confirms it (oriented projection orders
   within-scale 0.72 ~ markedness 0.77). The faithful decomposition is {dimension-select; ONE grounded oriented
   magnitude place code; markedness fine-degree refinement; FPE-log Weber code for comparison}.
3. **`hdlab/quality_relation` Channel B is LINEAR FPE = uniform-resolution = the wrong magnitude code.** The upgrade
   to `FPE(log degree)` + pole/dim binding preserves the Weber property on the real degrees (proven here) and turns
   the comparator into a native `unbind`. Record as a queued deviation-fix.
4. **The word-class meaning read-out should OPERATION-ROUTE** (gradable adj -> magnitude; else gloss), a net-positive
   canonical-clean route (no N/V regression). The gate is now SHARPER: gradable IFF (has_antonym OR satellite) AND NOT
   pertainym-relational (WordNet PERTAINYM flags classificatory adjectives; catches 303 coarse-gate misroutes).
5. **NEW: the composed magnitude channel is a COMPARISON system, and this is where it beats the incumbent CLEANLY.**
   On human-anchored relative comparison (which adjective is more X) it scores 0.762 vs the incumbent 0.554 (+0.21
   CI-sep) with the Moyer distance effect (+0.34); the categorical-pole code reproduces the semantic-congruity
   structure (same-pole graded / cross-pole categorical, AUC 1.000) that the incumbent gloss cosine INVERTS (0.220,
   ranking antonyms as more similar than same-pole pairs). Record: measure the magnitude organ on COMPARISON, not
   static recovery (rho is monotone-blind); the incumbent cosine's inability to separate graded comparison from
   categorical opposition is a concrete, measured instance of "opposition is irreducible / a cosine is the wrong
   operator." HONEST: pole-KEY vs pole-as-SIGN encodings are equivalent for congruity; the categorical pole's
   markedness-asymmetry advantage remains untested on available golds.
6. **NEW: the EVALUATIVE space is BIVARIATE, not a single bipolar axis (drill 8/9).** The brain's positive and
   negative valence populations are genuinely separate (Kim/Tonegawa 2016; Hagihara/Luthi 2024), and affect is
   bivariate (Cacioppo Evaluative Space Model). Measured: a single antonym VALENCE axis recovers valence 0.724 but
   is blind to a second, ORTHOGONAL, embedding-recoverable CO-ACTIVATION/AMBIVALENCE dimension (co-activation axis
   0.552 held-out; separates ambivalent-vs-neutral at 0.90 vs the bipolar axis's 0.63). Record: for EVALUATIVE
   dimensions the grounding should be BIVARIATE (valence + co-activation from independently-measured pos/neg), and
   opponent pools must be GENUINELY SEPARATE (not two centroids in one embedding -- those are redundant, corr 0.78,
   which was a weak-implementation null that a fair test overturned). Negativity bias is behavioral, and the negative
   channel's representational facet is DIMENSIONALITY (negative differentiation), not gain -- untested here.

---

## TLDR
The reader currently judges every word's meaning with one tool -- how much two words' definitions overlap. That is
right for nouns and verbs, wrong for describing-words that come in degrees (hot/cold, big/small). I built the "ruler"
tool those need -- as ONE working operation, plus the switch that decides which tool to use per word -- and showed
the composed thing works. On ~3,600-5,300 human-rated adjectives the ruler recovers the human ratings far better than
the reader's current one-tool method (0.50 vs 0.10) and better than the single best ruler-piece used alone (0.50 vs
0.41), with scrambled controls losing. The switch beats using EITHER tool for everything, because the ruler measures
"how much" and cannot measure "similar to what" -- so you must ADD it, not replace the definition tool. The deepest
result came from going deeper on the brain: it does NOT keep "which end of the scale" and "how far along" as two
steps -- it fuses them into a single oriented mental ruler, and our data agrees. So the honest, more brain-faithful
picture is "ONE oriented ruler, aimed at the right dimension and anchored the right way, plus a squashed code for
comparing two amounts" -- which is what the channel now implements, ready for the strategy session to land.

## QUESTIONS
None. One judgement call for integration: I read the bar as MET -- the composed channel beats the incumbent cosine
AND the strongest single sub-op CI-separated (the latter via dimension-routing + per-dim grounding), the FPE-log code
preserves Weber on-substrate, and routing beats every single-operation reader with no N/V regression. I have
deliberately surfaced two honest refinements (the "three operations partly collapse into one oriented code" finding,
and the coarse gradability gate) rather than claim a cleaner story than the disk supports.

## NEXT STEPS
1. Land `hdlab/scalar_adjective_operation.py` (the composed channel) and the `hdlab/quality_relation` Ch.B
   linear->log + pole/dim-binding upgrade; re-verify with the witness on the live substrate.
2. Make the meaning read-out OPERATION-ROUTE by word class (gradable adj -> magnitude; else gloss) with the SHARPER
   gradability gate now BUILT (gradable IFF (has_antonym OR satellite) AND NOT pertainym-relational; catches 303
   coarse-gate misroutes) -- optionally strengthen with corpus comparative-form / "very"-modifiability. Wire
   dimension selection to `hdlab/semantic_control`.
3. Replace the 23-word hand `AXIS_WORDS` lexicon with the grounded-degree lexicon (Warriner extremity / Lancaster /
   log-frequency); keep independent per-dimension axes (one global ATOM axis is refuted).
4. Add a human COMPARATIVE-judgment validation for the adjective Weber code when a ratio-scaled adjective-comparison
   set can be sourced (the number-comparison validation is in p3; scale-invariance on the real adjective degrees is
   shown here).
5. Measure the composed channel + router on the LIVE reader (fidelity win on gradable-adjective magnitude + the new
   relative-magnitude comparison capability, not a global similarity-rho jump).
6. UPGRADE THE EVALUATIVE GROUNDING TO A MULTI-EMOTION FHRR CODE (drills 9+11): valence + co-activation/ambivalence
   (SentiWordNet) + the specific-emotion channels (NRC EmoLex, fetched -- a ~5.5-D emotion supply; every basic emotion
   carries variance beyond VAD). Bind these as separate FHRR channels (ample substrate capacity). The single antonym
   axis loses the ambivalence dimension (0.63 vs 0.90) and GloVe compresses the emotion space to ~2-D -- but that is a
   GLOVE-SUPPLY limit, not a substrate one; ground in the annotation supply, which preserves the dimensionality. A
   real, non-data-blocked fidelity gain fully within the substrate's power.
7. THE READOUT'S REMAINING FRONTIER IS DATA-BLOCKED, NOT MECHANISM-BLOCKED: the opponent-POOL readout is
   monotone-equivalent for SCALAR recovery once the channels are non-redundant (drill 8/9); the next gains --
   context-set STANDARD / comparison-class re-anchoring ("big mouse" vs "big elephant"), negativity bias (behavioral),
   negative DIFFERENTIATION (the negative channel needs more DIMENSIONS, not gain -- Rozin & Royzman), semantic-
   congruity RT, Weber discrimination DIFFICULTY -- need BEHAVIORAL data (choice/RT/error, adjective-noun absolute-
   magnitude norms, or an ambivalence-rating set) the static rating golds cannot provide. Source such a set to
   validate these behaviorally.

---
INTEGRATED_BY_STRATEGY: 2026-08-28 (grade EXCELLENT, owner-DONE + authorized in-session). Re-verified FIRST-HAND
(verify_composed_magnitude_channel.py ALL CHECKS PASS): composed magnitude channel beats every sub-op + the incumbent
cosine CI-sep; operation-router beats gloss-only + magnitude-only with no N/V regression; FPE-log preserves Weber
(ratio-CV 0.000 vs 0.686); comparison-system 0.758 vs 0.552 (+0.206), distance effect +0.340, congruity AUC 1.000 vs
incumbent 0.215. The solver corrected the brief to be MORE brain-faithful (pole+degree = ONE oriented place code). Honest
deflations upheld (sub-op win = concreteness routing; coarse gate; markedness/FPE value = comparison+Weber; frontier
DATA-blocked). Review + SOLVER REVIEW block written to PROBLEM.md; priority cleared. AUDIT UPDATE folded (§2b).
🔌 hdlab LANDING ACCEPTED + QUEUED as a careful MULTI-MODULE port (NOT landed tonight -- ScalarMagnitudeChannel imports 4
experiment modules that must be relocated to hdlab first: FPE encoding + the semantic-axis machinery + the offline loaders,
then ADD scalar_adjective_operation.py + UPGRADE quality_relation Ch.B linear->FPE-log + ROUTE by word class + wire
dimension-selection to semantic_control). The immediate-next dedicated landing; the learner problem's substrate-validation
half depends on it.

---
hdlab LANDING (2026-08-28, strategy, Q111) -- the two HEADLINE deliverables + the FPE foundation are LANDED + witnessed
(default-off islands), so the learner's substrate-validation dependency (conceptual_meaning + scalar_adjective_operation +
the operation-router) is SATISFIED:
  * `hdlab/fractional_power_encoding.py` (step 1: the log-Weber magnitude code) -- witness test_fractional_power_encoding_organ.py PASS; registered fractional_power_encoding_v1.
  * `hdlab/scalar_adjective_operation.py` (step 2: the composed magnitude "ruler" = deliverable 1) -- witness test_scalar_adjective_operation_organ.py PASS; registered scalar_adjective_operation_v1.
  * `hdlab/meaning_operation_router.py` (step 3: word-class routing = deliverable 2) -- witness test_meaning_operation_router_organ.py PASS; registered meaning_operation_router_v1.
FOLLOW-ON refinements (NOT in the learner's dependency, tracked): the `quality_relation` Channel-B linear->FPE-log upgrade
(needs regrounding its 23-word lexicon with the grounded-degree data) + wiring dimension-select to `hdlab/semantic_control`.
