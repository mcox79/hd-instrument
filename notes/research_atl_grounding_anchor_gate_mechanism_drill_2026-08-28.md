# Research: precise brain mechanism for grounding the single-anchor cosine>=0.45 refusal gate

Date: 2026-08-28. Mode: 3 parallel Sonnet lit-scan sub-agents (graded/predictive N400 meaning
settlement; Gentner structure-mapping relational grounding; Kousta/Vigliocco/Borghi affective
embodiment verification) + self-executed disk audit of prior on-disk ATL/hub-spoke/meaning-fusion
work. Generic academic terms only in all external queries (named papers, public psycholinguistics
terminology) -- no substrate-novel mechanism names, configs or numbers went off-platform.

## HEADLINE

The measured gate is real and precisely located: `hdlab/reading_grounding_loop.py::canonicalize()`
does single-vector argmax cosine over all anchors in `space`, `thresh=SENSE_MATCH_THRESH` (0.45),
self-returning the target lemma as `TAUTOLOGY_NO_ANCHOR` below thresh. This is a structural mismatch
with the ATL's own mechanism: the hub grounds concepts by integrating MANY WEAK partial spoke
features (inverse-effectiveness: the combination gain is LARGEST exactly when each channel is weak),
never by requiring one strong single-referent match. The fix is compositional, not novel-mechanism
invention: this substrate ALREADY has a validated multi-channel fusion primitive
(`hdlab/meaning_fusion.py`, owner-accepted 2026-08-25, WordSim-353 0.4455 fused vs 0.3567/0.3801
solo, CI-separated, permutation-control-verified non-arithmetic) and an already-built but
currently-OFF graded/relative accept rule (`ReadoutConfig.margin_z_min`, FIX 1, 2026-08-12). Neither
is wired into `canonicalize()`'s accept/refuse decision. The one fix to build first is wiring the
fusion (extended with one new AFFECT spoke, Warriner/Kuperman/Brysbaert VAD norms) as the decision
statistic, with exposure-accumulated posterior sharpening riding on the existing PATIENCE multi-pass
loop -- not a threshold-lowering hack, and not a from-scratch hub-spoke build (the hub-spoke word
vector's OWN meaning spokes, tested in isolation on 2026-08-16, do NOT clear the meaning floor;
only cross-system fusion has actually won on this substrate).

## 1. HUB-AND-SPOKE computation (Q1)

PINNED-BY-EVIDENCE (Patterson, Nestor & Rogers 2007 *Nat Rev Neurosci* 8:976; Lambon Ralph,
Jefferies, Patterson & Rogers 2017 *Nat Rev Neurosci* 18:42; Cox, Rogers, Shimotake et al. 2024
*Imaging Neuroscience* PMC12224414, vATL ECoG feature-norm RSA, directly fetched): the ATL hub is a
graded, distributed, transmodal convergence code over modality-specific spokes (vision, audition,
action, affect, verbal). Concept identity = the correlation pattern across spokes, not a match to a
single referent. Cox et al. 2024 directly confirms the METRIC in the target region: two concepts are
neurally similar to the degree they share behavioral feature-norm content (wolf/coyote close via
shared furry/predatory/wild), graded, peaking 200-400ms post-stimulus.

PINNED-BY-EVIDENCE (multisensory integration: Ernst & Banks 2002 MLE cue combination, PMC9393257;
"law of inverse effectiveness," PMC5375642): robustness comes specifically from combining MANY
independently-noisy channels, and the proportional GAIN from adding a channel is LARGEST exactly
when each channel is individually weak -- the textbook description of the measured 0.22-0.45
sub-threshold regime, not evidence of an ungroundable domain.

PINNED-BY-EVIDENCE (semantic dementia degradation signature, Rogers et al. 2004 *Psychol Rev*
111:205; Lambon Ralph 2008 *Ann NY Acad Sci*): bilateral ATL damage produces GRACEFUL,
distributed-redundant degradation (typicality/frequency-weighted features survive longest,
atypical/distinctive features lost first, prototype-ward drift) -- the signature of a many-weak-
features representation, not a single-dominant-channel one; a dominant-channel architecture would
predict sharp category-specific collapse instead.

CONTESTED (Jackson, Orban & Tiesinga 2026 *Neurobiology of Language*, synthesizing Jackson, Rogers &
Lambon Ralph 2021 *Nat Hum Behav* + Tiesinga et al. 2023 *Sci Rep*): whether ventrolateral ATL (VL)
or the temporal-pole tip is the deepest multimodal convergence point, and whether the hub performs
pattern-COMPLETION (recurrent, feedback-dominant) rather than simple averaging -- unresolved, but
irrelevant to the "graded, distributed, no single anchor" answer; both camps agree on that.

**Equation to copy (reliability/precision-weighted cue combination, MLE form, Ernst & Banks 2002):**
```
score(word, anchor) = sum_k [ w_k * cos_k(word_spoke_k, anchor_spoke_k) ]
w_k = 1 / var_k     (var_k = channel k's own measured unreliability, e.g. bootstrap variance
                      across seeds/exposures)
combined_variance = 1 / sum_k(1/var_k)   <   min_k(var_k)
```
No single `w_k * cos_k` component needs to individually clear any threshold; the FUSED score's
confidence interval is what gates acceptance.

**Parameters to sweep, not adopt:** number of spokes K, per-spoke reliability weight w_k (measured,
not assumed), and whether fusion is early (concatenate before scoring) vs late (fuse per-channel
scores) -- literature and this substrate's own `meaning_fusion.py` both point to late/reliability-
weighted fusion as the validated shape (Section 4).

## 2. ABSTRACT-word channels with numbers (Q2)

**(a) Affective (Kousta, Vigliocco, Vinson, Andrews & Del Campo 2011, *JEP:General* 140:14-34 --
PINNED-BY-EVIDENCE, full text verified this session):**
- Exp 1 (40/40 matched pairs): abstract words recognized faster (568ms vs 590ms), F1(1,57)=23.327
  p<.001.
- Regression I (903 ELP words): concreteness remains a significant INHIBITORY predictor after
  imageability + context availability partialled out, F(1,863)=5.51 p<.05, full model R^2=71.70%.
- Exp 2 (774 neutral-valence-only words): the abstractness effect DISAPPEARS when valence is held
  constant -- concreteness/imageability n.s.
- Exp 3 (480 words, full valence/arousal range): with valence+arousal in the model, concreteness/
  imageability n.s. (R^2 collapses to 4.69%), valence remains significant F(2,20790)=3.60 p<.05.
  Removing valence/arousal from the SAME data makes concreteness significant again,
  F(1,20793)=13.76 p<.01 -- direct mediation evidence that valence ACCOUNTS FOR the abstractness
  effect, not vice versa.
- Valence explains ~8% of variance in adult age-of-acquisition ratings for abstract words
  specifically (U-shaped, F(2,1026)=28.34, p<.001).
- Dual/multiple-representation account: concrete concepts = statistical preponderance of
  sensorimotor info; abstract concepts = statistical preponderance of AFFECTIVE + linguistic info
  (explicitly NOT Paivio dual-coding; affect is a third grounding channel standing in for the
  missing sensorimotor referent).

**(b) Vigliocco, Kousta, Della Rosa, Vinson, Tettamanti, Devlin & Cappa 2014, *Cerebral Cortex*
24:1767-1777 -- PINNED-BY-EVIDENCE for the qualitative finding (corroborated by 3 independent
sources including the Kousta 2011 paper's own account of this study); exact fMRI inferential
statistics NOT independently re-verified this session (paywalled):**
- Rostral ACC (rACC) activation elevated abstract > concrete.
- Valence-specific to abstract words: ratings of affective association predicted rACC BOLD
  modulation FOR ABSTRACT WORDS. Entering valence/arousal as regressors makes the abstract>concrete
  rACC difference non-significant -- the same mediation logic as the 2011 behavioral result.
- Left IFG also elevated for abstract words -- a parallel linguistic-grounding channel, not
  competing with the affective one.
- Interpretation: rACC = an affective/interoceptive grounding channel, standing in for the missing
  sensorimotor referent concrete concepts have.

**(c) Borghi & Binkofski 2014, *Words as Social Tools*, Springer (WAT) -- PLAUSIBLE-MODEL
(synthetic theory monograph, not a single new experiment):**
- Claim: abstract concepts lack a single perceptual referent, so acquisition/representation relies
  more on LINGUISTIC/SOCIAL input (being told, asking others) than concrete concepts do.
- Mechanism: mouth/lip motor-system activation during abstract-word processing, proposed as an
  embodied trace of re-enacted linguistic experience (inner speech). Empirical support: Ponari,
  Norbury & Vigliocco and PeerJ 2019 (PMC6287580) mouth/hand effector studies.
- Follow-up: Borghi, Barca, Binkofski & Tummolini 2018, *Phil Trans R Soc B* 373:20170134 -- extends
  WAT to acquisition/inner speech specifically.

**(d) Numbers for a 3-way affective/linguistic/sensorimotor variance split: NOT FOUND, flagged as a
genuine literature gap (all 3 lit-scan sub-agents independently searched and did not find one).**
Closest proxies: Troche, Crutch & Reilly 2013 (PMC3662089) 3-factor model (perceptual salience,
emotion/social cognition, magnitude) from 12-dim ratings, no variance % in the original; a 2014
follow-up (PMC4009417) reports the 3 factors jointly explain R^2=0.81 of the 12-DIMENSION RATING
SPACE -- a dimension-compression number, NOT a causal decomposition of abstractness/processing
variance, and must not be conflated with one. Binder et al. 2016 (arXiv:1711.05516): 57/65 features
significantly distinguish abstract from concrete (higher on temporal/causal/social/emotional
attributes) but no % variance partition reported.

**Affective-feature computation to add:** one new spoke, VAD norms (Warriner, Kuperman & Brysbaert
2013, ~14k words), z-scored, lifted to `d` via the SAME fixed-random-projection + SimHash pattern
already used for SENSORY/ACTION/CONCRETE in `hdlab/hub_spoke_word.py`. `SPOKE_KEY[AFFECT] =
blake2b(seed || 'AFFECT')` -- zero new mechanism, matches the extension-without-invalidation
contract (G2) already proven for that module.

## 3. GRADED/PREDICTIVE commitment replacing the hard cutoff (Q3)

PINNED-BY-EVIDENCE (Rabovsky, Hansen & McClelland 2018, *Nat Hum Behav*, Sentence Gestalt model):
N400 amplitude = the magnitude of change in an implicit probability distribution over semantic
features ("Semantic Update") between successive processing steps -- the same error-like quantity
that drives the network's own error-driven learning. Reproduces 16 distinct empirical N400 findings;
explicitly framed as an alternative to threshold/symbolic meaning access.

PINNED-BY-EVIDENCE (Lindborg, Rabovsky et al., "Semantic surprise predicts the N400," bioRxiv/
ScienceDirect 2023): explicit Dirichlet-Categorical Bayesian learner over semantic categories.
Bayesian Surprise at trial t = KL(posterior_t || prior_t). Dirichlet concentration alpha increases
~1 per exemplar observed, mathematically SHARPENING the posterior (posterior variance ~
1/(alpha_0+n)), plus an exponential memory-decay parameter tau for forgetting. This graded KL-
surprise measure explains 97.25% of variance vs only 2.75% for a hard binary category-switch
detector -- a direct, quantitative refutation of threshold/binary-switch models of meaning access.

PINNED-BY-EVIDENCE (Norris 2006, *Psychol Rev*, "The Bayesian Reader"): word recognition = ideal-
observer Bayesian accumulation of noisy evidence over time; posterior over candidate words = prior
x accumulated likelihood; precision of the estimate grows roughly linearly with accumulated evidence
samples n (precision_n ~ n/sigma^2) -- a formally fit "sharpens with exposure" account. Decision
emerges from the evolving posterior/relative margin, not a fixed absolute similarity value.

PLAUSIBLE-MODEL (Bornkessel-Schlesewsky & Schlesewsky 2019, PMC6393377; Nour Eddine, Brothers,
Wang, Spratling & Kuperberg 2024, *Cognition*, an actually-implemented hierarchical predictive-
coding network): N400 = precision-weighted prediction error, precision = inverse variance,
Kalman-filter-style trust-weighting between existing model and new input. PLAUSIBLE-MODEL (Bhandari,
Lopopolo, Rabovsky & Reich 2025, arXiv:2505.02590, ensemble Kalman filter applied to the Sentence
Gestalt model): explicit precision-weighting formula, posterior = prior + Kalman_gain x
(observation - prediction), gain = prior_covariance / total_covariance.

CONTESTED: Kuperberg & Jaeger 2016 (*Lang Cogn Neurosci*, PMC4850025) leaves the precision-weighting
mechanism formally unspecified ("instantiated in many different ways") and explicitly rejects pure
structural-reanalysis for P600 in favor of model-adaptation/model-switching -- an open debate about
what P600 (as opposed to N400) computes, not load-bearing for this drill's answer.

**Computation to copy:**
```
P(anchor_i | evidence) ~ softmax( cos_i / tau )              -- relative, not absolute
tau shrinks as exposure count n grows, e.g. tau ~ 1 / sqrt(alpha_0 + n)
commit when: margin(top candidate, 2nd-best) is CI-separated AND CI-separated above floor
```
This is a relative, evidence-accumulated margin test across exposures, never an absolute fixed
cosine value scored on a single exposure.

**Already on disk, currently unused:** `ReadoutConfig.margin_z_min` in
`hdlab/reading_grounding_loop.py` (FIX 1, 2026-08-12) already REPLACES `best_cos >= thresh` with a
field-relative statistic -- `margin_stat="z_top"`: `(s_best - mean(s_field)) / sd(s_field)`, or
`margin_stat="margin"`: `s_best - s_second` -- exactly the relative-margin shape above. It was built
because the magnitude test was MEASURED blind to lemma identity (a different lemma's context window
scored 0.416808 vs the true one's 0.416687, enrichment 1.0000x;
`data/exp_context_vector_signal_v1/metrics.json`). "Every field defaults OFF." `GRADED_COMPARATOR`
(default ON since 2026-08-14) already makes the underlying query graded rather than sign-quantized.
No exposure-count posterior-sharpening term exists yet, despite `canonicalize()` already running
across multiple PATIENCE passes that could carry it.

## 4. RELATIONAL/analogical grounding (Q4 in the original 5-question brief; folds into the fix)

PINNED-BY-EVIDENCE (Gentner 1983, *Cognitive Science*; Falkenhainer, Forbus & Gentner 1989,
*Artificial Intelligence*, "The Structure-Mapping Engine"): analogy/relational meaning = alignment
of RELATIONAL structure (predicate-calculus expressions: attributes, first-order relations, higher-
order relations over relations) between a base and target, not a tally of shared surface features.
Systematicity principle: a relation embedded in a connected system of higher-order relations is
preferred over an equal-weight isolated match. SME algorithm: local match construction -> kernel
formation (bottom-up structurally-consistent clusters) -> greedy merge into global mappings ("gmaps"),
seeded from the largest/deepest kernel. Structural evaluation score: a "trickle-down" process
propagates evidential support DOWN from a matched relation to the match-hypotheses between its
arguments, so relations nested under other matched relations accumulate more support than flat,
isolated feature matches -- goodness of alignment is literally the depth/connectivity of the matched
relational chain, not a flat feature-overlap count. Constraints (Gentner & Markman 1997, *American
Psychologist* 52:45): one-to-one mapping, parallel connectivity (matching relations force matching
arguments, recursively).

PINNED-BY-EVIDENCE for relational-word learning generally (Gentner & Kurtz 2005, "Relational
categories"; Christie & Gentner 2010; Gentner, Anggoro & Klibanoff 2011, *Child Development*):
relational categories (predator, bridge, verbs, prepositions) are learned via PROGRESSIVE ALIGNMENT
-- comparison across 2+ exemplars sharing relational structure but differing in surface fillers,
which highlights the common relational skeleton and suppresses idiosyncratic surface features.
Demonstrated experimentally (3-year-olds learned relational categories only with BOTH relational
language AND a comparison sequence; single exemplars failed), not merely theorized. Gentner 2006
"Why Verbs Are Hard to Learn": nouns pick out cohesive perceptual object-packages (learnable by
ostension); verbs/relational terms partition diffuse, cross-linguistically-variable relational
components of a scene and resist single-referent/perceptual learning, requiring multi-scene
comparison instead.

GAP, explicitly flagged: no study directly tests "allow"/"access"/"afford" specifically, or frames
permission/capability verbs as AGENT-enables-THEME-to-reach-GOAL. Tag: PLAUSIBLE-MODEL (mechanism
pinned for the general relational-word class; direct extension to permission/capability verbs is
inference by category membership, not itself tested).

Computational bridge to vector semantics (PINNED that such models exist and fit human data; CONTESTED
as neurally-implemented binding, consistent with this project's own standing FHRR anchor): Plate
1993/1994 (HRR, NeurIPS) -- relational structures encoded via circular-convolution binding into
fixed-width vectors, dot-product similarity approximates both surface and structural similarity.
Doumas, Hummel & Sandhofer 2008 (DORA, *Psychol Rev*) -- relational concepts as role-filler bindings
via temporal synchrony, discoverable from unstructured features. Eliasmith's Semantic Pointer
Architecture -- concepts as recursively-bindable role-filler vectors, explicitly not points in a flat
similarity space.

**Relevance to the fix:** relational/permission words like "allow"/"access" are the class the
literature says featural/perceptual-referent grounding structurally cannot reach -- their meaning is
a bound argument-role structure (AGENT enables THEME to reach GOAL), not a point to correlate against
a spoke vector. This is a SEPARATE residual mechanism from Q1/Q2's channel-fusion fix, reserved for
whatever residual remains after the fusion fix (Section 5) -- not a reason to defer the fusion fix,
which should close a large fraction of the measured 0.22-0.45 band (concrete/experiential-leaning
words like "activity") without needing relational-structure machinery at all.

## 5. SYNTHESIS -- the concrete fix, ranked, and the adjacency call

**Rank-ordered fidelity upgrades:**
1. Distributed multi-weak-channel integration (reliability-weighted fusion) -- BUILD FIRST.
2. Add an AFFECTIVE spoke (Warriner VAD norms) -- cheap, same pattern as existing spokes, folds into (1).
3. Graded/predictive commitment (relative margin + exposure-sharpening) replacing the hard cutoff --
   wire alongside (1), reuses `ReadoutConfig.margin_z_min` (already built, OFF by default).
4. Relational/structural grounding (Gentner-style role-binding) -- reserved for the residual after
   (1)-(3); a separate, later mechanism for genuinely relational words the fusion fix cannot reach.

**The ONE to build first: (1)+(2)+(3) as a single wiring change**, not four separate builds.
`hdlab/meaning_fusion.py` (owner-accepted 2026-08-25) already validates the core claim on THIS
substrate: `z(cos_reading_spoke) + z(cos_grounded_spoke)` beats both solo channels on WordSim-353
(0.4455 fused vs 0.3567 raw / 0.3801 grounded, CI-separated for 2/3 readers, permutation-control-
verified non-arithmetic: FUSION_EQUAL - FUSION_SHUFFLE +0.19 CI [0.0639, 0.3141]).

**Computation:**
```
fused_score(word, anchor_i) = w1*z(cos_reading) + w2*z(cos_grounded) + w3*z(cos_affect)
w_k = 1 / cross-validated variance of channel k (measured, not assumed)
accept iff: fused_score's top candidate is CI-separated above BOTH the 2nd-best candidate
            (softmax-margin, Q3) AND the floor (F_ORTHO / F_SCRAMBLE / permuted-channel controls)
posterior sharpens across canonicalize()'s existing multi-pass PATIENCE loop (tau shrinks with
exposure count, Q3's Dirichlet/Kalman-gain shape)
```

**Can-fail test (precision-validated, distinguishing this from mere threshold-lowering):** score
every item currently measured at cosine 0.22-0.45 (the 36% abstract/relational refusal band) under
(i) naive threshold-lowering alone (thresh -> 0.20, no channel change) vs (ii) 3-channel fusion +
affect spoke + graded margin. HARD-PASS requires ALL of:
- (a) precision of newly-accepted anchors (held-out gold sense-match) for (ii) is CI-separated ABOVE
  (i) at matched acceptance rate -- proves distributed integration adds real information, not just
  noise inflation from a looser gate;
- (b) an affect-channel-scrambled control (VAD values permuted across words) collapses (ii)'s gain;
- (c) (i) shows a precision DROP at the same expanded coverage -- the mandatory negative control
  proving naive threshold-lowering is not equivalent to this fix.

HARD-FAIL (any): (ii)'s precision on the 0.22-0.45 band is NOT CI-separated above (i); OR the
affect-scramble control does not collapse the gain (channel is not doing real work, matches the
independence-verification discipline already established in
`notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md`); OR (i) and (ii) tie --
would mean the band's low score is a genuine content floor (real missing grounding, not a gate-shape
artifact), and the next lever shifts to coverage (denser norms) or Section 4's relational/structural
grounding for the residual, not more fusion channels.

**Adjacency call: this is BOTH the READER problem and the reader_meaning_channel/ATL-grounding
problem -- it is the seam between them, not two separate builds.** `canonicalize()` is the reader's
per-word commit step (`hdlab/reading_grounding_loop.py`); the fix requires ATL-hub-shaped multi-spoke
evidence (`hdlab/hub_spoke_word.py`, `hdlab/meaning_fusion.py`,
`hdlab/distributional_meaning_channel.py`). The fix wires the reader's decision rule to consume the
ATL-grounding channel's fused evidence.

**Composes directly with prior on-disk ATL work -- reuse, not new build, for 3 of 4 pieces:**
- REUSE `hdlab/hub_spoke_word.py` (FORM/SENSORY/ACTION/CONCRETE spokes, role-bound, extension-
  without-invalidation already proven, G2 pass) -- add one AFFECT spoke.
- REUSE `hdlab/meaning_fusion.py`'s validated z-fusion as the base combiner.
- REUSE `ReadoutConfig.margin_z_min` (FIX 1, already built, currently OFF) for the graded/relative
  accept rule instead of `best_cos >= thresh`.
- REUSE the existing multi-pass PATIENCE loop in `reading_grounding_loop.py` as the exposure-
  accumulation substrate for posterior sharpening.
- NEW construction, small: one AFFECT spoke (VAD norms, same pattern as existing spokes) + wiring
  the fusion as `canonicalize()`'s decision statistic + an exposure-sharpening term for `tau`.

**Load-bearing caveat, found this session (`preregs/exp_hub_spoke_word_representation_v1.md`, gate
G3, rescored `experiments/exp_hub_spoke_word_g3_cleanup_rescore_v1.py`, full-scale result recorded
2026-08-16):** the hub-spoke word vector's OWN meaning spokes, tested ALONE (unbind -> cleanup ->
recovered code), do NOT clear the meaning floor -- SimLex rho 0.1961 vs strongest floor
(HARDENED_FREQ_MIN) 0.0797, margin +0.1164 but **95% CI [-0.0308, +0.2653] crosses zero** ->
NOT_SEPARATED, G3 = FAIL as pre-registered. The rescored row also lands essentially ON the ceiling
of the direct (unbundled) spoke codes, meaning the result is really a statement about the 12-dim
Lancaster sensorimotor-norm asset's own coverage, not about the bundling mechanism. **Consequence:
do not wire `hub_spoke_word.py`'s meaning spoke into `canonicalize()` in isolation expecting a win.**
The only place multi-channel integration has actually WON on THIS substrate is
`hdlab/meaning_fusion.py`'s cross-SYSTEM fusion (an independent distributional/reading channel x an
independent grounded/norms channel), not the hub-spoke bundle's internal multi-spoke integration by
itself. The fix above wires the proven-winning shape (cross-system fusion), extended with one more
channel, not the not-yet-winning shape (hub-spoke-alone).

**Separately flagged, out of scope for this fix:** `exp_hub_spoke_partial_cue_curve_v1` (2026-08-16)
established no CA3-shaped pattern-completion organ exists yet for noisy/partial per-spoke cues --
relevant only if the fused evidence itself needs to be robust to missing/degraded spoke content
later, not blocking for this fix (which operates on whatever spoke content IS present).

## Cross-thread synthesis

Converges with and sharpens three same-day-family notes already on disk:
`notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md` (established the inverse-
effectiveness/MLE-cue-combination biology and the independence-verification discipline this drill's
can-fail test inherits), `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md`
(established that abstract domains resist a sensorimotor-only core and need categorically different
channels -- affect, magnitude, social-relational, metaphor-structural -- not denser sensorimotor
coverage; this drill supplies the affective channel's exact numbers and the wiring target), and
`notes/research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md` (grounding-reach as the
acceptance criterion; this drill's can-fail test is the same discipline applied to one specific gate).
The load-bearing NEW finding this drill contributes: the substrate already HAS a working instance of
the exact fusion mechanism the neuroscience prescribes (`meaning_fusion.py`, landed 2026-08-25, after
the three prior notes were written) -- so the recommended next step is wiring an existing win into an
existing gate, not designing a new mechanism from the literature cold.

## Substrate-product implications

If the fusion-wiring fix HARD-PASSes: a meaningful fraction of the 36% abstract/relational refusal
rate converts to correctly-grounded anchors (precision-validated, not just coverage-inflated),
directly using a mechanism already proven to beat single-channel scoring on this substrate. If it
HARD-FAILs: it cheaply localizes whether the 0.22-0.45 band is a gate-shape artifact (fixable) or a
genuine content/coverage floor (requires the relational/structural path or denser norms) -- either
outcome is actionable and both are far cheaper to have measured than not knowing, per the standing
research discipline to drill every finding for mechanism before building further on top of it.

## Citations (verified count)

**Disk-verified this session (12 artifacts, read directly):** `hdlab/reading_grounding_loop.py`
(canonicalize/canonicalize_fast/ReadoutConfig, full read of relevant sections);
`hdlab/hub_spoke_word.py`-adjacent preregs: `preregs/exp_hub_spoke_word_representation_v1.md`,
`preregs/2026-08-16_exp_hub_spoke_partial_cue_curve_v1.md`; `hdlab/meaning_fusion.py` (docstring +
brain-fidelity labelling section); `hdlab/distributional_meaning_channel.py`;
`notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md`;
`notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md`;
`notes/research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md`;
`notes/research_outcome_valence_detector_design_2026-08-05.md`;
`notes/lit_scan_atl_hub_and_spoke_2026-08-13.md`; `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`.

**External, fetched/search-verified this session via 3 parallel Sonnet lit-scan sub-agents (generic
academic terms only):** Rabovsky, Hansen & McClelland 2018 *Nat Hum Behav*; Kuperberg & Jaeger 2016
PMC4850025; Bornkessel-Schlesewsky & Schlesewsky 2019 PMC6393377; Nour Eddine et al. 2024 *Cognition*;
Lindborg/Rabovsky "Semantic Surprise Predicts N400"; Bhandari, Lopopolo, Rabovsky & Reich 2025
arXiv:2505.02590; Norris 2006 "The Bayesian Reader"; Rodd, Gaskell & Marslen-Wilson 2004 *Cognitive
Science*; Griffiths & Steyvers 2007 *Psychol Rev*; Rumelhart & McClelland 1981/82; Narayanan &
Jurafsky Bayesian sentence processing; Gentner 1983 *Cognitive Science*; Falkenhainer, Forbus &
Gentner 1989 *Artificial Intelligence*; Gentner & Markman 1997 *American Psychologist*; Gentner &
Kurtz 2005; Christie & Gentner 2010; Gentner, Anggoro & Klibanoff 2011 *Child Development*; Gentner
2006 "Why Verbs Are Hard to Learn"; Plate 1993/1994 NeurIPS (HRR); Doumas, Hummel & Sandhofer 2008
*Psychol Rev* (DORA); Blouw, Solodkin, Thagard & Eliasmith 2016 *Cognitive Science*; Kousta, Vigliocco,
Vinson, Andrews & Del Campo 2011 *JEP:General* (full text obtained); Vigliocco, Kousta, Della Rosa
et al. 2014 *Cerebral Cortex* (qualitative corroborated, exact stats not independently re-verified);
Borghi & Binkofski 2014 *Words as Social Tools*; Borghi, Barca, Binkofski & Tummolini 2018 *Phil Trans
R Soc B*; Troche, Crutch & Reilly 2013 PMC3662089; Binder et al. 2016 arXiv:1711.05516; Patterson,
Nestor & Rogers 2007 *Nat Rev Neurosci*; Lambon Ralph, Jefferies, Patterson & Rogers 2017 *Nat Rev
Neurosci*; Cox, Rogers, Shimotake et al. 2024 PMC12224414; Ernst & Banks 2002 (MLE cue combination,
PMC9393257); law of inverse effectiveness PMC5375642.

**Genuine gaps flagged, not papered over:** no study tests "allow"/"access"/"afford" specifically
under a featural-vs-structural contrast; no clean 3-way affective/linguistic/sensorimotor variance-
partition number exists anywhere found; Vigliocco 2014's exact fMRI inferential statistics not
independently re-verified this session (source paywalled).

**P_deflated = 0.40** (below the 0.50 novel-synthesis cap; deflated from an undeflated ~0.65 read of
strong convergent evidence because: (i) the specific claim that wiring `meaning_fusion.py`'s already-
proven shape, extended with one more channel, will produce a CI-separated precision gain specifically
on the 0.22-0.45 abstract/relational band is a novel-synthesis prediction with no direct precedent
testing exactly this composition; (ii) the affect-channel's expected contribution size is inferred
from Kousta/Vigliocco's mediation numbers, not measured on this substrate's own joined VAD-norm data;
(iii) the hub-spoke-alone G3 null result is a real, load-bearing negative that could generalize to
"more spokes doesn't help without denser per-spoke coverage," which the can-fail test is designed to
detect but has not yet ruled out).

**HARD-PASS / HARD-FAIL thresholds:** as stated in Section 5's can-fail test above -- repeated here
for the required standalone falsifiable-predictions section per role contract:

HARD-PASS (all required): (a) fused+affect arm's precision on the 0.22-0.45 band CI-separated above
naive threshold-lowering at matched acceptance rate; (b) affect-scramble control collapses the gain;
(c) naive threshold-lowering shows a precision drop at matched expanded coverage.

HARD-FAIL (any): fused+affect arm not CI-separated above naive threshold-lowering; OR affect-scramble
does not collapse; OR the two arms tie on precision at matched coverage.

---

**research: delivered atl_grounding_anchor_gate_mechanism_drill ->
notes/research_atl_grounding_anchor_gate_mechanism_drill_2026-08-28.md ; HEADLINE: the single-anchor
cosine>=0.45 gate (hdlab/reading_grounding_loop.py::canonicalize) is a structural mismatch with the
ATL's many-weak-channel integration mechanism; substrate already owns the fix's core pieces
(meaning_fusion.py's proven cross-channel fusion, ReadoutConfig.margin_z_min's graded-margin gate,
hub_spoke_word.py's extensible spoke architecture) unwired from canonicalize's decision; build =
wire fusion + one AFFECT spoke (VAD norms) + exposure-sharpened graded margin into canonicalize,
NOT a from-scratch hub-spoke build (hub-spoke-alone's own meaning spokes failed G3, CI crosses
zero) ; P_deflated=0.40 ; next-drill candidate: Gentner relational/structural grounding for the
residual band (permission/capability verbs) if the fusion fix's can-fail test HARD-FAILs, OR
affect-channel independence pre-flight (measure VAD-vs-existing-spoke correlation on this
substrate's own joined data before trusting the fusion gain, per the standing independence-
verification discipline).**
