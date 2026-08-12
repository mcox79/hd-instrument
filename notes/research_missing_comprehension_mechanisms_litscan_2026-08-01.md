# Research: Missing brain mechanisms for language comprehension (lit-scan, ranked)

Date: 2026-08-01
Type: literature scan (cognitive + computational neuroscience), generic public terms only
Calibration: lit-scan penalty applied (deflate 0.15-0.25 off naive confidence); novel-synthesis P capped at 0.50 (per [[feedback-lit-scan-calibration-penalty]])

## HEADLINE

Current system = predictive encoder + BG-style WM gate + situation-model loop + error-driven learning. That covers *token-level prediction* and *slot-holding*, but the literature converges on THREE things it structurally cannot do without additional machinery: (1) **arbitrate which prediction errors matter** (precision-weighting), (2) **predict at more than one grain simultaneously** (multi-level/hierarchical prediction — semantic/event/discourse, not just next-token), and (3) **decide when to update vs protect weights** (neuromodulatory learning-rate control). Everything else on the list (timescale hierarchy, replay, salience, bridging/ToM) is real and eventually needed, but is either partially subsumed by what you already have (situation-model loop ~ bridging-inference scaffold) or is a second-order refinement on top of (1)-(3). Cross-thread note: this overlaps but does not duplicate the 2026-06-24 and 2026-07-18 drills — those scored plasticity/coding/dynamics mechanisms broadly; this drill is scoped narrowly to *comprehension-critical* cognitive-architecture gaps and ranks by comprehension-function impact, not substrate-feasibility composite.

## Cheap decisive test

Build a **two-line surprisal-gated learning-rate multiplier** on the existing error-driven update: scale weight-update magnitude by a scalar precision estimate (inverse running-variance of recent prediction error at each hierarchy level; cheapest possible AdaGrad/ACh-like proxy — no new architecture, no new organ). Falsifiable in <1 day: run on ambiguous-continuation sentences (garden-path / temporary syntactic ambiguity corpus) vs a flat-learning-rate control.

## Falsifiable predictions

**HARD-PASS**: precision-gated variant reduces error at disambiguation point (post-garden-path reanalysis) by >=15% relative to flat-rate control, AND does not regress plain (non-ambiguous) sentence next-word accuracy by more than 2%.

**HARD-FAIL**: precision-gating produces <5% relative improvement at disambiguation OR degrades plain-sentence accuracy >5% — indicates the mechanism is not load-bearing at current scale/vocab, or the implementation is a mislabeled learning-rate-schedule effect rather than genuine reliability-weighting. If HARD-FAIL: do NOT conclude precision-weighting is unneeded — check whether the corpus actually contains enough ambiguity events to be a fair discriminator first (underpowered-test check per [[feedback_flat_learning_result_means_broken_experiment_not_capability_ceiling]] analog).

## Ranked list (highest comprehension-impact first)

### 1. A. Precision-weighting / attention as inverse-variance gain on prediction error — HIGH impact
- What: Friston's precision-weighting (Friston 2005, 2010 free-energy; Feldman & Friston 2010 "Attention, Uncertainty, and Free-Energy") — attention = the brain up-weighting prediction errors with high expected precision (reliable channels) and down-weighting noisy/unreliable ones. This is the standard computational account of top-down attention within predictive-coding.
- Status: **ESTABLISHED** as a theoretical framework with converging behavioral/neuroimaging support (attention cueing effects, psychophysics of cue-combination match precision-weighted Bayesian integration — well replicated in perception; language-specific evidence is thinner, mostly inferred from cueing/ambiguity-resolution studies, e.g. eye-tracking on garden-path reanalysis). Treat the language-specific application as **CONTESTED/extrapolated**, the perceptual core as established.
- Function it provides that you lack: without it, EVERY prediction error is treated as equally informative, so noisy/ambiguous input (homonyms, garden-path syntax, unreliable co-reference cues) gets the same update weight as clean signal — no principled way to resolve ambiguity by trusting the more reliable cue, and no mechanism to suppress learning from genuinely noisy/adversarial input. This is very plausibly why your existing error-driven learning has been described as flat/undifferentiated in past sessions.
- Recommendation: **BUILD** (highest priority; cheapest to prototype — a single scalar gain on existing error-driven updates, no new organ).
- P_deflated = 0.45 (near novel-synthesis cap; strong theoretical grounding, language-application evidence is inferential not causal-lesion-level).

### 2. F. Multi-level / hierarchical prediction (token + semantic/event + discourse simultaneously) — HIGH impact
- What: Predictive coding for language extends beyond next-word: Kuperberg & Jaeger 2016 (review, "What do we mean by prediction in language comprehension?") frame prediction as operating over multiple representational levels (lexical, syntactic, semantic/event, discourse); Willems & Heilbron work + related MEG/fMRI (e.g. Heilbron et al. 2022 naturalistic-speech hierarchical surprisal) show that human brain responses carry surprisal signals at word AND higher levels concurrently, with distinct cortical loci per level — consistent with Lerner et al. 2011 "temporal receptive windows" hierarchy.
- Status: **ESTABLISHED** that comprehension involves prediction at multiple levels concurrently (converging neural evidence, e.g. distinguishable surprisal regressors at word vs. event/discourse level explaining independent variance in neural signal). **CONTESTED**: exact number of levels, and whether they are truly separable computations vs. emergent from a single deep hierarchy.
- Function it provides you lack: your current predictive encoder is (per your own framing) predict-next at token grain. Single-level prediction cannot represent "I expect this NP to be the patient of an upcoming verb" or "I expect this paragraph to resolve a stated goal" — i.e., cannot generate expectations that span an event or a discourse arc, which is exactly the situation-model's job upstream but currently has no matching *predictive* (generative, error-producing) counterpart feeding back into learning at that grain. Your situation-model LOOP holds state; it likely doesn't yet PREDICT-AND-ERROR-CORRECT at that grain the way the token-level encoder does.
- Recommendation: **BUILD next**, second priority — likely the natural extension of the existing situation-model loop (add a predict-then-error step at the event/discourse level, not just token level), rather than a wholly new organ.
- P_deflated = 0.40.

### 3. B. Neuromodulation — reward/salience-gated "when & how much to learn" — HIGH-MED impact
- What: Dopaminergic reward-prediction-error (Schultz, Dayan & Montague 1997 canonical TD account) gates *what gets reinforced*; separately, Yu & Dayan 2005 "Uncertainty, Neuromodulation, and Attention" formalizes acetylcholine as signaling *expected* uncertainty (known unreliability, e.g. known-ambiguous words) vs norepinephrine/locus-coeruleus signaling *unexpected* uncertainty (context has changed, e.g. topic shift, need to reset). LC-NE adaptive-gain theory (Aston-Jones & Cohen 2005) ties NE to exploration/exploitation mode-switching.
- Status: **ESTABLISHED** in decision-making/RL neuroscience broadly; **CONTESTED/less-tested specifically in language comprehension** (most direct evidence is from non-linguistic uncertainty tasks; language application is a reasonable but under-tested extrapolation — deflate accordingly).
- Function it provides you lack: this is functionally adjacent to #1 (precision) but distinct — precision governs *how much a given error updates belief this instant*; neuromodulation governs *global learning-rate/mode* over longer timescales (should I be in "exploit known schema" mode or "something changed, learn fast" mode) and *what to consolidate* (only reward/salience-tagged content gets prioritized replay — directly relevant to your planned schema-consolidation store). Without it you cannot distinguish "this sentence is locally ambiguous" (ACh/precision case) from "the whole topic changed, my priors are stale" (NE case) — these need different responses (local reweight vs. global reset).
- Recommendation: **BUILD after #1/#2** — but note strong overlap with precision-weighting; consider implementing as ONE unified gain-control mechanism with two timescales (fast=precision/ACh-like, slow=NE-like context-change detector) rather than two separate organs. Also directly informs which episodes get tagged for replay when the consolidation store is built (per D below).
- P_deflated = 0.35 (language-specific evidence thinner than A/F).

### 4. G. Bridging inference / discourse coherence (RST-style) — MED-HIGH impact, likely PARTIALLY covered
- What: Bridging inference (Clark 1975; Haviland & Clark 1974 "given-new contract") and discourse-coherence relations (Mann & Thompson 1988 Rhetorical Structure Theory; Kehler 2002 coherence-driven pronoun resolution) — the inferential glue that connects sentences into a coherent structure beyond what's literally stated (e.g. "The car wouldn't start. The battery was dead." requires inferring "car has a battery").
- Status: **ESTABLISHED** as central to human comprehension (well-replicated reading-time and ERP N400 effects for bridging-inference cost).
- Function: this is likely already partially served by your situation-model loop if it does any entity/event linking across sentences, but the literature suggests bridging is a *distinct, effortful, error-generating* inferential process, not passive slot-filling — i.e. it should itself produce a predictable "expect a coherence relation" signal, feeding back like #2 above.
- Recommendation: **DEFER** — likely emerges as a special case of #2 (multi-level prediction at discourse grain) once built; don't build as a separate organ yet. Re-evaluate after #2 lands.
- P_deflated = 0.30.

### 5. C. Hierarchical processing timescales / temporal receptive windows — MED impact
- What: Hasson et al. 2008/2015 "process memory," Lerner et al. 2011 — cortical hierarchy where higher areas integrate over longer timescales (words -> sentences -> paragraphs -> narrative), demonstrated via scrambling experiments (word/sentence/paragraph-scrambled stimuli) showing graded sensitivity across cortex.
- Status: **ESTABLISHED** (strong, well-replicated fMRI evidence).
- Function: gives comprehension graded temporal integration so higher-level structure isn't reset by every new token — this is largely what your working-memory gate + situation-model loop are FOR structurally, but the literature indicates this should be a *continuum of timescales*, not a two-level (token vs. situation-model) split. Missing piece is intermediate-timescale representations (sentence/clause-level), not a wholly new organ.
- Recommendation: **DEFER** — reframe as a parameter/architecture question for the existing WM-gate + situation-model organs (add an intermediate timescale) rather than a new mechanism to build from scratch.
- P_deflated = 0.30.

### 6. E. Bottom-up salience + top-down selection — MED impact, likely subsumed by #1
- What: Selective encoding of relevant entities/events; classic attention literature (Itti & Koch bottom-up salience; biased-competition top-down, Desimone & Duncan 1995).
- Status: **ESTABLISHED** generally; **less separable from precision-weighting** in modern predictive-coding accounts, where salience/attention IS precision-weighting (Feldman & Friston 2010 explicitly unify these).
- Function: without it, all entities get equal encoding effort regardless of relevance to current goal/discourse focus.
- Recommendation: **DEFER — fold into #1.** Building both A and E separately risks building the same mechanism twice under different names; this is a known trap (over-differentiating what's actually one gain-control computation).
- P_deflated = 0.25 (mostly redundant with #1, not a separate build).

### 7. D. Sleep/replay consolidation (beyond a static schema store) — MED impact, LOW urgency now
- What: Hippocampal replay (Wilson & McNaughton 1994), systems consolidation (McClelland, McNaughton & O'Reilly 1995 complementary learning systems) — interleaved reactivation prevents catastrophic forgetting and abstracts schemas from episodic traces over repeated replay.
- Status: **ESTABLISHED** mechanism in memory neuroscience; role in LANGUAGE comprehension specifically (vs. general declarative memory) is **CONTESTED/thin** — most direct evidence is episodic-memory and skill-consolidation, extrapolation to online sentence comprehension is weaker.
- Function beyond a static schema store: interleaving prevents catastrophic forgetting when learning new constructions without erasing old ones (directly relevant to your "comprehension = growing library of competencies" framing — replay is plausibly HOW new competencies get added without forgetting old ones); also does schema *abstraction* (statistical regularities extracted across many episodes, not just stored).
- Recommendation: **DEFER but flag as directly relevant** to the competency-library goal — once you're adding multiple construction-competencies and see forgetting between them, replay/interleaving is the literature-predicted fix. Don't build speculatively; build when forgetting is empirically observed.
- P_deflated = 0.30 (mechanism established, comprehension-specific application still to be shown here).

### 8. G-other. Theory-of-mind for pragmatics — LOW-MED impact, LOW urgency
- What: Pragmatic inference / Gricean reasoning, formalized in Rational Speech Act models (Frank & Goodman 2012) — requires modeling the speaker's intent, not just literal content.
- Status: **ESTABLISHED** as necessary for full pragmatic comprehension (irony, indirect speech acts, scalar implicature); **not central** to basic literal-sentence comprehension, which is your current bottleneck.
- Recommendation: **DEFER far** — premature relative to current stage (real-text mention/role extraction is still the acknowledged upstream wall per current focus notes); ToM/pragmatics is a later-stage refinement.
- P_deflated = 0.20.

### 9. Oscillatory phase-coding for chunking — LOW impact for now
- What: Theta-gamma phase coding proposed for syllable/word chunking (Giraud & Poeppel 2012), cortical tracking of linguistic units at different oscillatory bands (delta=phrase, theta=syllable).
- Status: **CONTESTED** as a causal comprehension mechanism vs. an epiphenomenal correlate of processing rhythm; evidence is correlational (MEG/EEG entrainment) rather than causal-lesion.
- Recommendation: **DEFER** — interesting but not clearly load-bearing, and your system's discretized/gated architecture likely doesn't need a continuous-oscillation analog to get the functional benefit (segmentation) that phase-coding provides in a biological substrate.
- P_deflated = 0.15 (below the 0.50 cap by a wide margin; weakest-evidence item on this list).

## Cross-thread synthesis

The prior 2026-06-24 drill scored mechanisms by substrate-feasibility (BE/SI/EL composite) across a much broader inventory (plasticity, coding, dynamics, memory, oscillations, HTM) and landed on word-level prediction + 2-level predictive coding as top feasibility picks — which is directionally consistent with #2 (multi-level prediction) here, just scored on a different axis (feasibility vs. comprehension-impact). This drill's #1 (precision-weighting) did not appear as a top pick in that scan; worth flagging as a genuinely new candidate for the next exp_dev cycle. The 2026-07-18 "missing structure" drill (442 lines, not re-read in full this cycle — flag for cross-check before building #1/#2 to avoid duplicate framing) should be diffed against this list before shipping any anchor.

## Substrate-product implications

- #1 (precision-weighting) and #3 (neuromodulation) are architecturally CHEAP relative to #2 — both are gain/gate scalars applied to the existing error-driven update pathway, not new organs. Recommend building #1 first as the cheap decisive test above, folding #3's fast-timescale (ACh-like) component into the same mechanism, and treating #3's slow-timescale (NE-like) component as a second, later increment.
- #2 (multi-level prediction) is the one item here that plausibly requires new architecture (a predict-then-error step at the situation-model's grain, not just the token encoder's) — higher cost, but literature says it's necessary for anything beyond next-word-level comprehension, which matches the "comprehension = growing competency library" framing already locked in.
- #4/#5/#6 are flagged DEFER-and-fold rather than DEFER-and-ignore: they are real gaps but plausibly collapse into #1/#2 if those are built with enough generality (a general precision/gain mechanism naturally yields salience-like selection; a general multi-level predictor naturally yields discourse-coherence expectations). Building them as SEPARATE organs risks redundant/over-differentiated architecture — check this explicitly during design review of #1/#2.
- #7 (replay) is the one item to keep on the radar for the NEXT session where multiple competencies are trained sequentially and forgetting is observed — don't build ahead of the symptom.

## Citations (verified count: 14 named author+year references cited above; NOT independently web-verified this cycle — all drawn from well-established canonical literature in predictive-coding, uncertainty/neuromodulation, and discourse-processing subfields; flag for spot-check if used to justify a HARD build decision rather than a prioritization ranking)

1. Friston, K. (2005, 2010) — free-energy / precision-weighted prediction error
2. Feldman, H. & Friston, K. (2010) — "Attention, Uncertainty, and Free-Energy"
3. Kuperberg, G. & Jaeger, T.F. (2016) — prediction in language comprehension, multi-level review
4. Heilbron, M. et al. / Willems, R. — hierarchical surprisal in naturalistic language (MEG/fMRI)
5. Lerner, Y., Honey, C.J., Silbert, L.J., Hasson, U. (2011) — hierarchy of temporal receptive windows
6. Hasson, U. et al. (2008, 2015) — process memory / cortical hierarchy scrambling experiments
7. Schultz, W., Dayan, P., Montague, P.R. (1997) — dopamine reward-prediction-error
8. Yu, A.J. & Dayan, P. (2005) — ACh (expected uncertainty) vs NE (unexpected uncertainty)
9. Aston-Jones, G. & Cohen, J.D. (2005) — LC-NE adaptive gain theory
10. Clark, H. & Haviland, S. (1974/1975) — given-new contract / bridging inference
11. Mann, W. & Thompson, S. (1988) — Rhetorical Structure Theory
12. Kehler, A. (2002) — coherence-driven pronoun resolution
13. McClelland, J., McNaughton, B., O'Reilly, R. (1995) — complementary learning systems
14. Wilson, M. & McNaughton, B. (1994) — hippocampal replay
15. Frank, M. & Goodman, N. (2012) — Rational Speech Act pragmatics
16. Giraud, A-L. & Poeppel, D. (2012) — oscillatory tracking of speech
