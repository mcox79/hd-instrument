# DEEPER brain-foundation drill: is our fix the cheap version? what is the RIGHT store?

Second, deeper drill (owner: "do what's right, not what's cheap; is there further we can push this?").
Dispatched via `research` (4 parallel deep lit-scans, Q1-Q5). Full synthesis persisted here (the agent's own
deliverable wrote to a stale D:\ path). Each claim tagged PINNED / OUR-INVENTION / PLAUSIBLE-BUT-UNTESTED.
ASCII only.

## HEADLINE

Our finer-key + set-return fix is a real but IMPOVERISHED special case of the brain-faithful architecture,
NOT wrong in kind. It is the SAME SHAPE (index space separate from content, similarity retrieval into a set --
= the TEM/transformer key-value correspondence) but a degenerate case missing three properties the literature
independently converges on: the temporal key is DISCRETE where it should be GRADED (Q1), HAND-DESIGNED where it
should be LEARNED/multi-module (Q3), and applied UNIFORMLY where most events should never reach the episodic
index at all (Q5). And the earlier attractor-null-result is THEORY-CONSISTENT (Q2): decorrelated codes are
exactly what an attractor needs the ABSENCE of -- it was tested on the wrong kind of code, not proven useless.

## Q1 -- SEPARATION-vs-CONTIGUITY: the temporal key should be GRADED multi-timescale drift, not orthogonal sub-slots

DG orthogonalizes CONTENT/item identity; temporal context is a SEPARATE, continuously + gradedly drifting
signal. Human free-recall temporal contiguity (Kahana 1996) is explained by TCM/CMR: a leaky-integrated context
vector whose similarity decays smoothly (~power-law/scale-invariant) with elapsed time. Shankar & Howard 2012
(Neural Comp): a population of leaky integrators spanning geometrically-spaced decay constants approximates a
Laplace transform of recent history, invertible into time-cell receptive fields that are scale-invariant and
OVERLAPPING for nearby times. Real time cells (MacDonald/Eichenbaum 2011, Neuron) tile time with graded,
overlapping fields -- NOT discrete non-overlapping indices. Fast WITHIN-moment ordering is supplied separately
by theta phase precession (O'Keefe & Recce 1993; Skaggs 1996). CA3 recurrent collaterals store directional
heteroassociative order links between separated content codes (order as a relational graph, not code-similarity;
Marr 1971; Nakazawa 2002).
- PINNED: Howard & Kahana 2002; Kahana 1996; Sederberg/Howard/Kahana 2008; Polyn/Norman/Kahana 2009; Shankar &
  Howard 2012 (comp proposal; neural ID untested); MacDonald 2011; O'Keefe&Recce 1993 + Skaggs 1996; Rangel 2014
  (DG context-selectivity graded by temporal separation); Tsao 2018 (LEC drift, qualit.); Nakazawa 2002; Marr 1971.
- BUILD: replace the discrete sub-slot key with a bank of leaky integrators at geometric decay constants
  (tau ~ {1,2,4,8,16,...}), bind graded context to the still-orthogonal content code, retrieve by
  similarity-WEIGHTED graded readout; add a fast within-moment order signal to separate co-temporal events
  (the theta-phase analog) -- NOT more orthogonal sub-slots.

## Q2 -- WHY THE ATTRACTOR-NULL WAS THEORY-CONSISTENT: completion needs STRUCTURED codes

(1) Classical Hopfield/Amit-Gutfreund-Sompolinsky 1985 / Treves & Rolls 1994 WANT decorrelated near-orthogonal
patterns (correlation = interference that cuts capacity -- WHY DG randomizes EC input). Under this theory i.i.d.
random codes are near-IDEAL and an iterative Hebbian dynamic just averages out crosstalk to reach the max-overlap
answer -- but if one-shot exhaustive NN already computes that, iteration has nothing left to clean up. THIS is
exactly our null. (2) Continuous attractor networks (grid cells; Burak & Fiete 2009; Khona & Fiete 2022) solve a
DIFFERENT problem -- a recurrent kernel that is a function of DISTANCE ON A MANIFOLD -- and REQUIRE manifold/
correlated codes, which i.i.d. random codes lack by construction. (3) Modern/dense Hopfield (Krotov & Hopfield
2016; Ramsauer 2020 = transformer attention) sharpen the energy nonlinearity for one-step high-capacity recall on
soft/ambiguous cues -- helps soft-cue COMBINATION, not beating a hard exhaustive search.
- ABSENCE FLAG: no paper directly benchmarks iterative-attractor vs exhaustive-one-shot as competing algorithms.
- BUILD: the attractor is not useless -- give the STRUCTURAL/index code manifold geometry, THEN completion earns
  its keep on cues that are NOT exact stored copies (the comparison our null never made). Or use dense-Hopfield
  energy for soft-cue disambiguation.

## Q3 -- TOLMAN-EICHENBAUM MACHINE: our fix is a degenerate TEM

TEM (Whittington et al. 2020, Cell 183:1249) factorizes STRUCTURE g (entorhinal, path-integrated over
transitions g_t=f(g_{t-1},a_t), reusable generic basis) x CONTENT x (LEC), conjunctively bound into hippocampal
p, stored in a Hebbian matrix, retrieved bidirectionally by attractor. In TEM's repeated-lap example, IDENTICAL
content at different laps gets DIFFERENT g (lap-phase) -> disambiguation FALLS OUT of training for next-obs
prediction, not hand-set granularity. Whittington 2021/22 (arXiv:2112.04035): formal correspondence g->attention
keys/queries, x->values -- TEM retrieval IS a key/value store (= transformer attention). So our finer-key +
set-return is the SAME SHAPE as TEM but single-scale, non-learned, content-blind. Vector-HaSH (Chandra/Sharma/
Chaudhuri/Fiete 2024/25, Nature): factorized scaffold+content avoids the associative-memory "memory cliff" via
combinatorial grid-module phase assignment.
- PINNED: Whittington 2020 (full text); Behrens 2018; Whittington 2021 correspondence; Chandra 2024/25 memory-
  cliff (repeated-entity ablation specifically UNTESTED). TEM 2020 never says "interference"; the repeated-entity
  collision-avoidance claim for our use case is PLAUSIBLE-BUT-UNTESTED extrapolation.
- BUILD: replace the flat temporal key with a LEARNED multi-module structural embedding (stacked periodic/
  recurrent codes at different scales -- "which routine / which occurrence / position-within"), trained via
  next-event prediction over the entity-event transition graph, bound to content, retrieved bidirectionally.

## Q4 -- RECALL TERMINATION: a RACE, not an oracle count

CMR/CMR2 (Polyn 2009; Lohnas 2015) treat "stop" as one more competing outcome in the SAME retrieval race.
Morton & Polyn 2015 (JML): P(stop,j)=theta_s * e^(j*theta_r) -- NO count anywhere. Empirical driver is CUE
DEGRADATION not a counter: Miller/Weidemann/Kahana 2012 -- people stop right after an intrusion/repetition (a
wrong item degrades the cue). IRTs grow exponentially with output position (Murdock & Okada 1970) -> usable
model-free stop signal. Foraging/MVT (Hills/Jones/Todd 2012): termination = patch-departure, no N needed.
- Hopfield-energy stopping bridge = OUR-INVENTION (not found).
- BUILD: replace the oracle set-size with a race -- a "stop" candidate whose activation rises with cue
  degradation (CMR) or local hit-rate below baseline (MVT), using signals retrieval already produces.

## Q5 -- SYSTEMS LEVEL (highest leverage): the fan tracks EVENT-MODEL COUNT; schematize the routine

Radvansky/O'Rear/Fisher 2017 (Mem Cogn 45:1028): the classical fan effect (Anderson 1974) tracks the number of
separate SITUATION/EVENT MODELS, NOT raw fact count -- facts integrated into ONE scene show NEAR-ZERO fan; facts
in separate situations show FULL fan. Maps directly: our every-event-a-separate-trace design = their MAX-
interference condition; an entity-state model updated IN PLACE = their near-zero-interference condition. Gilboa &
Marlatte 2017 (TiCS): schema-consistent instances integrate into a vmPFC-hippocampus-cortex network; repeated
exposure accelerates transfer into generalized CORTICAL representations -- regular material GRADUATES OUT of
episodic indexing. van Kesteren SLIMM 2012: mPFC congruency-detector suppresses hippocampal engagement for
schema-fit material (coarse division PINNED; fine mPFC-suppression mechanism PLAUSIBLE-BUT-CONTESTED, mixed
replication).
- BUILD (the cheap decisive one): a per-entity continuously-updated GIST/schema vector (EMA/leaky-integrated
  summary) absorbs ROUTINE events; route only NOVEL/atypical events (low similarity to current gist) to the
  episodic indexer. Pure ablation, no training.
- PRE-REGISTERED DECISIVE TEST: baseline vs gist-aggregation, split by entity event-COHERENCE. HARD-PASS =
  CI-separated interference reduction CONCENTRATED in high-routine entities, near-null on heterogeneous ones.
  HARD-FAIL = no separation anywhere, or UNIFORM improvement regardless of coherence.

## BOTTOM LINE + PRIORITY BUILDS

Finer-key+set-return is cheap-but-correct-in-SHAPE, not cheap-but-wrong. Priority order to push it to RIGHT:
1. (cheapest, highest leverage, TEST FIRST) TWO-TIER SCHEMA/GIST split (Q5) -- per-entity gist absorbs routine
   events; only atypical -> episodic. Decisive coherence-split test pre-registered above.
2. MULTI-TIMESCALE GRADED temporal key (Q1) -- leaky integrators tau~{1,2,4,8,16}, + fast within-moment order.
3. (larger) TEM/Vector-HaSH FACTORIZED learned structural key (Q3) -- build after 1-2.
4. DEFER iterative attractor/completion (Q2) until 3 gives manifold codes; then re-test on non-exact cues.
5. RACE-TO-STOP termination (Q4) -- parallel, independent.
