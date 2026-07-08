# Research (brain-first): how does the brain bound compounding error over many sequential reasoning steps

**Date:** 2026-07-08. **Trigger:** de-risking the headline deep-prize build (scaling the certified glass-box
reasoning loop onto the real ingested KB) on its most likely failure axis — hop-depth. Reviving a CONFIRMED
genuine negative: `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` landed
`HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL` at FULL (`data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json`,
verified off-disk below) — the two standard, literature-ranked, ML-side fixes (coarse-to-fine multi-resolution
decomposition + verify-before-commit gating) BOTH returned almost exactly zero lift over the already-failed
open-bisection baseline. This drill asks a different question than the last one: not "what does ML do about
compounding error" (already asked, already tried, already failed twice) but **"what does the BRAIN actually
do, mechanistically, that ML's standard fixes do not capture" — and does that suggest a genuinely different,
buildable substrate mechanism.** Per USER directive: brain leads, deep, from first principles; ML/LLM framings
are a weak secondary check only, flagged where the brain diverges. No sub-agents dispatched — this is a
direct director-authored drill using WebSearch for citation grounding, per task instruction.

**Verified off-disk (do not re-quote the two prior notes' numbers without re-deriving):**
`data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json`, `run_mode=full`,
`verdict=HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`. At FOCUS (`op4_V1200_d8`, entropy=16.0, chain_steps=3):
`OPEN` (already-failed baseline) `recovery_ratio=0.019`; best rescue arm (`wp_bisect_coarse2fine`)
`recovery_ratio=0.023`; `DELTA=0.004`; `sign_p=0.1797` (not significant); `index_artifact_gap=0.001`,
`anti_tautology_corr=0.001` (honesty guards clean — the null is real, not an artifact of a broken
discriminator). `n_hp_ok=0/5` regimes cleared HARD-PASS. This is a clean, honest, dispositive null on BOTH
attempted fixes, not an ambiguous or under-powered result.

---

## HEADLINE

**The two failed ML-side fixes (coarse-to-fine, verify-gate) share one structural property the brain's
error-bounding mechanisms do NOT have: both correct a noisy estimate using MORE OF THE SAME noisy estimate.**
`wp_bisect_verify`'s gate checks a candidate against `R[anchor,c]` and `R[c,goal]` — the *same* SR-derived
reach matrix that produced the noisy pick in the first place. `wp_bisect_coarse2fine` re-derives a coarser
pick from the *same* `M`/`R` machinery at a different gamma, then commits to it before ever revisiting it.
Neither introduces one bit of information that isn't already inside the single noisy estimator. Every brain
mechanism reviewed below that actually caps drift shares the opposite structural property: **the correcting
signal is drawn from a source that is informationally INDEPENDENT of the accumulator being corrected** —
an external boundary/landmark cue (not more self-motion integration), a second grid module at a different
physical scale (not a re-check of the same module), a reverse-direction replay pass (not a second forward
pass), or a fixed-parameter physical prediction (not a data-driven percentile of the same noisy signal).
Grid-cell path integration is the closest, best-quantified biological analog to this exact failure: raw
path integration accumulates error as an *unbounded, growing function of time/distance since last
correction* — mathematically the same qualitative shape as Ross-Bagnell's `O(T^2)` — and the brain's fix is
never "check the drifted estimate against itself more carefully," it is always "inject an independent
reference" (boundary cells, redundant grid modules, hippocampal-cortical reciprocal correction). **This
reframes the ranked shortlist below around one governing principle: build a genuinely INDEPENDENT
second information channel, not a smarter filter on the one channel that already failed twice.**

The single highest-ranked NEW candidate (not yet tried, structurally distinct from both failed attempts) is
**replay-generate-then-select**: generate several complete candidate trajectories independently (forward
AND reverse), score each COMPLETE candidate by bidirectional (forward-reverse) agreement, and commit only
the best-scoring whole trajectory — never a single greedy per-hop pick. This is the literal reading of
Pfeiffer & Foster (2013): hippocampal replay composes a *full* path across a choice point, correlated with
the route the animal actually takes next, before any single step is committed. It is also exactly what
today's parallel drill (`notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md`, thread 4)
independently converged on for the general reasoning loop ("multi-hop composition is done offline, before
commitment, via forward/backward replay over the same weights") — this drill supplies the FIRST concrete,
already-HARD_FAIL-tested substrate regime where that general claim can be pressure-tested empirically, not
just proposed architecturally.

---

## THE BIOLOGY, IN DEPTH (five threads, ranked by how directly each maps to the failure mode)

### 1. Grid-cell path integration + boundary-vector-cell reset — the closest quantitative analog

Path integration is a literal continuous-time analog of the substrate's chained, uncorrected bisection: a
running estimate of position is updated by integrating self-motion (velocity) with no external check, and
the update at each instant depends on the PREVIOUS estimate, not ground truth — structurally identical to
Ross-Bagnell's behavior-cloning setting. Continuous-attractor models of the grid network (Burak & Fiete)
show this recursive updating causes attractor drift that, left uncorrected, breaks down the periodic code
within minutes. The measured, decisive finding (Hardcastle, Chen & Giocomo 2015, "Environmental Boundaries
as an Error Correction Mechanism for Grid Cells," *Neuron*, PMID 25892299): **grid-cell error accumulates as
a function of time/distance since the animal last contacted an environmental boundary**, and boundary contact
triggers direction-dependent error correction via border cells — i.e., the correction is keyed to an
external, independently-sensed landmark event, not to more path-integration compute. Complementary continuous-
attractor modeling (Zhang et al., *Scientific Reports* 2022, "Place cells dynamically refine grid cell
activities to reduce error accumulation... in a continuous attractor model," PMC9744848) shows the specific
circuit mechanism: reciprocal grid-cell <-> place-cell connectivity, with place cells anchored to sensory/
boundary landmarks, actively pulls drifted grid activity back via Hebbian plasticity — again, correction
flows FROM an independently-grounded representation (place cells tied to sensory landmarks) INTO the
self-referential integrator (grid cells), never the integrator checking itself. Keinath et al. (*Current
Biology* 2024, "Visual boundary cues suffice to anchor place and grid cells in virtual reality") confirms
this generalizes across sensory modalities (vision alone suffices) — the key property is independence of
source, not any specific modality.

**A second, equally important sub-mechanism: modular redundancy as an error-correcting code.** Grid cells are
organized into several independent modules at different spatial scales (Fiete/Burak/Sreenivasan program).
Sreenivasan & Fiete (2011, *Nature Neuroscience*, "Grid cells generate an analog error-correcting code for
singularly precise neural computation") show the multi-module code is formally analogous to a redundant
residue/CRT-style error-correcting code: because each module encodes position modulo a different scale,
independent modules' phases must be MUTUALLY CONSISTENT for a decoded position to be accepted, and combining
several independently-noisy, differently-scaled estimates gives both far larger effective range AND graceful,
bounded degradation under noise — a structurally different correction principle from thresholding one
estimator against itself. This is a second, independent instantiation of the same governing principle:
**cross-validate across informationally-independent channels, don't re-filter one channel.**

### 2. Hippocampal replay — full-trajectory generation and bidirectional consistency, not per-step gating

Pfeiffer & Foster (2013, *Nature*) is the decisive piece: at a choice point, decoded hippocampal sequences
depict a COMPLETE path to a remembered goal — including start-goal combinations the animal never directly
traversed together — meaning the hippocampus composes a full candidate route from independently-learned local
segments BEFORE the animal commits to a single step, and the composed sequence predicts the path subsequently
taken. This is categorically different in structure from both failed substrate fixes: `wp_bisect_open`,
`wp_bisect_verify`, and `wp_bisect_coarse2fine` are ALL single-pass, commit-as-you-go procedures — even
coarse-to-fine still locks in the coarse pick once made and never revisits it against a competing full
alternative. The brain generates (at minimum) a *population* of candidate trajectories and selects among
complete candidates, never irrevocably committing to a partial one.

Two further, directly relevant sub-findings:
- **Reverse replay** (Foster & Wilson 2006, *Nature*, "Reverse replay of behavioural sequences in
  hippocampal place cells during the awake state"): the same trajectory is replayed in BOTH forward and
  reverse direction, at different behavioral moments, proposed to solve the temporal credit-assignment
  problem (reward information propagating backward through a trajectory that offered no signal en route).
  Forward and reverse replay traverse the SAME stored associative weights from opposite ends — a structurally
  independent cross-check (front-to-back vs back-to-front) of the same underlying relational structure,
  analogous to a parity/consistency check on a code.
- **Prioritized replay as a gain x need schedule** (Mattar & Daw 2018, *Nature Neuroscience*, "Prioritized
  memory access explains planning and hippocampal replay"): replay content is not random or exhaustive — it
  is prioritized by how much reactivating a given transition would change future behavior (gain) times how
  likely that state is to be visited soon (need), modeled as a Bellman backup applied to stored transitions.
  This gives a principled, cheap way to decide WHICH of many candidate trajectories/segments are worth
  generating and scoring, rather than generating an unbounded population.

(This entire thread is independently corroborated, same day, by `notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md`
thread 4, arrived at via a completely separate lit-scan for a different purpose — general reasoning-loop
architecture, not compounding-error rescue. Convergent evidence from an independent drill strengthens, not
just repeats, this thread's weight.)

### 3. Cortico-striatal action chunking — reducing the NUMBER of decision points, not their resolution

Graybiel's chunking account (1998, "The basal ganglia and chunking of action repertoires") describes
cortico-basal-ganglia circuits compressing sequences of individually-selected movements into a single,
atomically-executed unit, with neural activity specifically bracketing sequence START and STOP (Jin & Costa,
*Nature* 2010, "Start/stop signals emerge in nigrostriatal circuits during sequence learning") rather than
firing at every intermediate step. The functional consequence for error compounding: once a sequence is
chunked, the number of independent, error-prone SELECTION events collapses from one-per-step to one-per-chunk
— fewer places for compounding error to be injected at all, rather than a better filter at each of the same
number of places. This is now independently confirmed as a formal, quantitative claim in the ML compounding-
error literature itself: a 2025 result (arXiv:2507.09061, "Action Chunking and Exploratory Data Collection
Yield Exponential Improvements in Behavior Cloning for Continuous Control") proves that a sufficiently
chunked imitator policy accrues **horizon-free**, not horizon-growing, compounding error relative to its
per-chunk error — a materially stronger and differently-shaped guarantee than either coarse-to-fine
(still horizon-dependent, still one decision per level) or verify-gating (still one decision per hop). This
is important: it is NOT the same mechanism as "coarse-to-fine," even though both sound hierarchical —
coarse-to-fine still makes `chain_steps` sequential, revisable-only-in-principle decisions; true chunking
makes ONE decision that atomically commits several hops at once, from a single high-confidence inference.

### 4. Predictive coding — accumulate the bounded residual against a model-based expectation, not raw state

Hierarchical predictive coding (Friston's free-energy framework; Bastos et al.'s laminar cortical
prediction-error circuits) frames cortical hierarchies as propagating only the MISMATCH between a top-down
prediction and bottom-up evidence, with the mismatch signal itself compared against an explicit generative
model of how error SHOULD grow (a model-based expectation), not against an empirically-tuned percentile of
the observed data (which is what `wp_bisect_verify`'s `tau` — a 70th-percentile cutoff of `R`'s own
distribution — actually is). This is a real, if secondary, distinction: a percentile-of-self-signal threshold
adapts to whatever the noisy signal happens to look like at that moment (self-referential, per the headline
diagnosis); a model-based bound compares the observed decay against the INDEPENDENTLY-derivable
`1/(1-gamma)`-style effective-horizon curve (already measured and reported in the prior note: uplift-over-
chance decays 0.551->0.368->0.261 roughly linearly with horizon) and only flags a hop as suspect when it
deviates from that independently-known expected decay — a strictly stronger, externally-grounded check.

### 5. Why the substrate's existing per-hop CA3-style re-clean helped interpolation-depth but does not help here

This is the mechanistic gap the drill was specifically asked to close. Per-hop cleanup (`cleanup_batched`)
corrects **representation fidelity** — is this vector a valid, low-noise codeword close to something actually
stored — and that is exactly the axis on which the substrate's certified reasoning-depth-interpolation result
is CG: composing/binding operations accumulate VECTOR noise, and cleaning up after each hop keeps the vector
on-manifold, so the representation of a KNOWN-CORRECT compositional structure survives many hops. But
Ross-Bagnell compounding error, and the waypoint-discovery HARD_FAIL specifically, is a **selection/decision**
error, not a representation error: the substrate can represent a WRONG waypoint choice with perfect vector
fidelity — cleanup makes the wrong pick more confidently, more cleanly represented, it does nothing to tell
the substrate the pick itself was wrong. This is precisely why `bwp_cv` (cross-seed instability of the picked
waypoint identity, the actual decision) rises sharply with chain length while `reach_rank_test` uplift (a
signal-quality measure) declines only gracefully — cleanup operates on the axis that stays fine; the failure
is entirely on the axis cleanup cannot touch. Every brain mechanism above (boundary reset, modular
cross-validation, bidirectional replay, chunking, model-based residual bound) targets the SELECTION axis
directly, which is the structurally correct place to intervene and the reason none of them is "more cleanup."

---

## RANKED SHORTLIST — buildable substrate mechanisms to bound deep-chain compounding error

Each entry: brain mechanism + source; how it caps drift; composition with the certified reasoning loop
(CA3-cleanup stays as the representation-fidelity layer; these mechanisms all operate on the
selection/decision layer above it) + the bimodal working-memory / retained-trace structure identified in
today's parallel drill; honest prior; kill-test sketch (full spec below for rank 1).

**Rank 1 (HIGH-PROBABILITY-SUPERIOR NEW — flagged per task instruction).**
**Replay-generate-then-select (bidirectional full-candidate scoring).** Brain: Pfeiffer & Foster 2013 (full-
path composition pre-commitment) + Foster & Wilson 2006 (reverse replay as an independent directional
cross-check) + Mattar & Daw 2018 (gain x need prioritization of which candidates are worth generating).
Caps drift by: never committing to a partial trajectory — the correction signal is agreement between two
INDEPENDENTLY-generated estimates of the same route (forward-from-start vs reverse-from-goal), which is
informationally different from checking one direction against itself (this is exactly the property both
failed fixes lacked). Composition: CA3-cleanup denoises each candidate's constituent vectors during
generation (representation layer, unchanged); the bimodal WM structure (thread 2 of today's reasoning-loop
inventory) naturally holds the top-scoring candidate as the active attractor while remaining candidates sit
in the activity-silent background trace, pending final bidirectional score. Honest prior: mechanistically the
most different-from-both-failed-attempts option available, but two independent ML-precedented fixes already
returned essentially zero lift on this exact regime, which is a real, sobering empirical prior update, not
just a theory update — P kept modest accordingly (below).

**Rank 2.** **Independent redundant-module cross-validation (grid-module analog).** Brain: Sreenivasan &
Fiete 2011 (multi-module error-correcting code) + Zhang et al. 2022 (place-grid reciprocal correction).
Caps drift by: requiring agreement between multiple SEPARATELY-seeded/separately-trained SR estimators
(independent noise draws) rather than a threshold on one estimator's own output. Composition: a second
(or third) `train_sr_transport` pass with an independent RNG stream and independently-shuffled minibatch
order, at the SAME gamma as the primary `M` (isolating "independence of noise draw" from "different horizon,"
which mechanism 3/multi-gamma already conflates). Honest prior: real and well-precedented, but shares some
of rank 1's sobering empirical update; ranked below rank 1 because it corrects only WITHIN a single forward
pass (still commits per-hop), whereas rank 1 corrects across a WHOLE candidate trajectory.

**Rank 3.** **True action chunking (atomic multi-hop commitment, not multi-resolution sequential commitment).**
Brain: Graybiel 1998 + Jin & Costa 2010 (start/stop bracketing, not per-step firing); ML-side: arXiv:2507.09061
(2025, horizon-free bound under chunking, formally distinct guarantee from anything already tried). Caps
drift by: reducing the COUNT of sequential, individually-fallible decisions (the actual variable the ancestor
note's own data showed tracks the outcome — recovery groups cleanly by `chain_steps`) rather than improving
each decision's quality. Composition: chunk size becomes a tunable span parameter in the existing bisection
recursion — instead of always bisecting to single waypoints, commit segments of `k>1` hops at once from a
single joint inference over the SR-derived reach signal spanning the whole segment. Honest prior: distinct
and well-precedented mechanism, cheap to add as a parameter sweep on the already-built recursion; independent
enough from rank 1/2 to combine with either.

**Rank 4.** **Boundary/landmark reset to an independent ground-referenced anchor.** Brain: Hardcastle, Chen &
Giocomo 2015; Keinath et al. 2024. Caps drift by: re-anchoring periodically to the ORIGINAL stored KB atom
(start/goal encoding, independently retrievable) rather than to the chain's own most-recent, possibly-wrong
intermediate pick — literally re-querying the retained trace instead of trusting the accumulated path.
Composition: at every `k`-th hop, discard dependence on the intermediate discovered-anchor chain beyond the
window and recompute the remaining plan fresh from the immutable start/goal KB atom + `R`. Honest prior:
simplest to implement, but weakest fit to THIS specific failure mode — the substrate's "boundary" analog
(the original start/goal atoms) is already available every step via `R`'s direct entries, so this may already
be partially present in the existing bisection procedure and not add much beyond rank 1-3; worth testing
cheaply as a floor/sanity check, not as the primary bet.

**Rank 5.** **Model-based bounded-residual gating (predictive-coding style).** Brain: Friston/Bastos
hierarchical predictive-coding. Caps drift by: replacing `wp_bisect_verify`'s empirical-percentile `tau`
(self-referential) with a `tau` derived from the independently-measurable `1/(1-gamma)`-horizon decay curve
— a small, cheap, mechanically simple change to the already-built verify-gate. Honest prior: lowest-cost to
test (literally one line — swap `tau`'s source), but the underlying failed mechanism (per-hop, single-
direction gating) is unchanged, so expected to inherit most of `wp_bisect_verify`'s already-measured
near-zero lift; ranked last because it does not address the headline diagnosis (self-referential vs
independent signal) at all, only a minor tuning detail of the loser mechanism.

---

## (b) Cheap decisive test

**Smoke first** (reuse ancestor's existing smoke grid, `N=2048`, `V=300`, 3 seeds, `op4_V300_d6` FOCUS,
`chain_steps=2`) before any FULL dispatch, per standing discipline. Reuse ALL primitives verbatim from both
ancestors (`make_bipolar_E`, `hebbian_W`, `cleanup_batched`, `make_kb_and_chains`, `train_sr_transport`,
`reach_value`, `build_reach_matrix`, `run_hier_arm_wp`, `oracle_trajectory_idx`, `build_waypoint_idx`,
`gamma_for_span`, `coarse2fine_boundaries`). Add ONE new primitive family implementing rank 1
(replay-generate-then-select), reusing `train_sr_transport` verbatim for the reverse pass (swap
start/goal roles in the transition set fed to the same function — no new training-loop shape):

```
M_rev, _ = train_sr_transport(E, transitions_reversed, n, steps, batch, base_lr, gamma=0.85, gen)  # verbatim call, reversed transitions
R_rev = build_reach_matrix(M_rev, E)   # verbatim call
def generate_candidates(start, goal, R_fwd, n_cand) -> list[boundary_seq]:
    # n_cand independent forward bisections from wp_bisect_open's own procedure,
    # using n_cand independently-perturbed argmax tie-breaks (different RNG draws) -- cheap, no retrain
def score_bidirectional(cand, R_fwd, R_rev) -> float:
    # harmonic mean of forward-direction reach score (start->...->goal) and
    # reverse-direction reach score computed from R_rev over the SAME candidate boundaries traversed goal->start
def wp_replay_generate_select(start, goal, R_fwd, R_rev, n_cand=5) -> boundary_seq:
    cands = generate_candidates(start, goal, R_fwd, n_cand)
    return max(cands, key=lambda c: score_bidirectional(c, R_fwd, R_rev))
```

Re-run `wp_bisect_open`, `wp_bisect_verify`, `wp_bisect_coarse2fine`, `wp_bisect_combo` in-cell on IDENTICAL
seeds (all four already measured at FULL in the parent/rescue cells — re-running them here is for a clean
paired comparison, not new information) as the required must-decay / already-failed controls. Cost: one
extra `M_rev` SR-training pass (identical cost class to the already-added `M_long`), `n_cand=5` cheap
re-bisections reusing existing argmax machinery, and one scoring function — no new representational
machinery, no quadratic blowup (compute is linear in `n_cand`).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL, locked; FOCUS = `op4_V1200_d8`, entropy=16, chain_steps=3)

**HARD-PASS (independent-signal hypothesis confirmed; genuine rescue):**
- `recovery_ratio(wp_replay_generate_select)` at FOCUS `>= 0.20` **AND**
- `recovery_ratio(wp_replay_generate_select) - recovery_ratio(wp_bisect_verify)` (the already-measured,
  already-failed SELF-REFERENTIAL control, `0.023` at FOCUS per the landed FULL run) `>= 0.15` **AND**
- **flatness ratio** `recovery_ratio(FOCUS, chain_steps=3) / recovery_ratio(op4_V1200_d4, chain_steps=1)
  >= 0.5` (retains at least half its shallow-chain recovery at the deepest tested chain length — the direct
  operationalization of "stays flat vs hop-depth where the baseline decays") **AND**
- honesty guards at the SAME thresholds as both ancestors (`index_artifact_gap < 0.05`, `anti_tautology_corr
  < 0.85`, `degenerate_rate < 0.10`) **AND**
- `cv(wp_replay_generate_select) < 0.15` at FULL **AND** `sign_p < 0.05` (paired, vs `wp_bisect_verify`, the
  most direct already-failed comparator).
=> the compounding-error bound was an artifact of self-referential correction specifically, not a
fundamental property of the domain; an informationally-independent (bidirectional) correction signal, drawn
directly from brain-first replay/reverse-replay theory, recovers real autonomous-decomposition capability
where two ML-precedented single-channel fixes could not.

**HARD-FAIL (the bound survives even independent-signal correction — genuinely, doubly confirmed structural):**
- `recovery_ratio(wp_replay_generate_select)` at FOCUS `<= recovery_ratio(wp_bisect_verify) + 0.05` (i.e.
  `<= 0.073` — no material improvement over the already-failed self-referential control despite an
  informationally-independent, brain-precedented correction signal) **OR**
- flatness ratio `< 0.2` (still an accelerating, not bounded, collapse).
=> honest stopping point, stronger than the prior note's: the compounding-error bound is not merely
insensitive to WHICH ML-side fix is tried, it is insensitive to whether the correction signal is
self-referential or genuinely independent — this rules out the headline diagnosis's own best hypothesis and
leaves only oracle-in-the-loop correction (out of scope by the capability's own "autonomous, no-oracle"
definition) as a remaining lever. Recommend accepting the bound as fundamental for this domain/training-budget
after this second, more mechanistically-targeted attempt, and redirecting the cerebellar/replay
brain-component build effort toward the GENERAL reasoning-loop architecture (today's parallel drill) rather
than this specific narrow capability line.

**MIDDLE_BAND:** real lift over `wp_bisect_verify` in `[0.05, 0.15)`, OR flatness ratio in `[0.2, 0.5)` —
report as "independent-signal correction is real but partial," an honest intermediate finding.

**P_deflated:**
- P(any real lift over `wp_bisect_verify` at FOCUS, i.e. clears MIDDLE-band): raw ~0.45-0.50. This is
  LOWER than the prior note's raw ~0.70-0.75 for its own (now-refuted) hypothesis — the sobering empirical
  update from two independent, well-precedented, cheap-to-implement ML-side fixes BOTH returning
  near-exactly-zero lift is real evidence, not just a reason to try a third theory harder. The
  mechanistic case for rank 1 (informational independence, not self-reference) is genuinely different and
  well-grounded in a decisive biological analog (grid-cell boundary reset, reverse replay), which is why
  this isn't driven all the way down to chance, but the base rate for "third attempt succeeds after two
  clean failures on the same regime" should be treated with real skepticism. -> **P_deflated ~0.25-0.30**
  after the mandatory 0.15-0.25 calibration penalty.
- P(clears full HARD-PASS bar, flatness ratio >= 0.5 AND delta >= 0.15 AND recovery >= 0.20 at the deepest
  corner): raw ~0.30 (compounding on top of the above, requiring BOTH a real effect AND a large one) ->
  **P_deflated ~0.15-0.20**, well under the mandatory novel-synthesis cap of 0.50.
- P(rank 3, true action chunking, shows real lift as a SEPARATE/combinable mechanism): raw ~0.45 (distinct,
  well-precedented, but addresses a related-not-identical axis — decision COUNT, not decision independence)
  -> P_deflated ~0.25-0.30. Recommend testing rank 1 and rank 3 as a COMBINED arm
  (`wp_replay_generate_select` operating over chunked, not single-hop, candidate segments) if both show any
  independent lift at MIDDLE-band or better — the two mechanisms are non-redundant by the biology (fewer
  decisions AND better-corrected decisions are different levers) and combining well-precedented, independently-
  positive mechanisms is the standard next move per this drill's own governing principle.

---

## (d) Cross-thread synthesis

- Directly supersedes the ML-only diagnosis in `notes/research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md`
  for WHY the two ML-precedented fixes failed: that note correctly identified Ross-Bagnell `O(T^2)`
  compounding as the mechanism and correctly ranked coarse-to-fine + verify-gate as the standard ML answer —
  but "standard ML answer" and "brain's actual answer" turned out to be structurally different in a way that
  matters empirically (both landed near-zero lift), not just theoretically. This drill's contribution is
  identifying WHAT property both failed fixes shared (self-reference) that the brain's mechanisms uniformly
  lack (informational independence), which the prior note could not have surfaced because its lit-scan was
  ML/CS-only (per that drill's own scope), not brain-first.
- Directly extends and cross-validates `notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md`
  (same day, independent lit-scan, different purpose — general reasoning-loop architecture, not this specific
  HARD_FAIL). That note's thread 4 concluded, from a completely separate literature pass, that multi-hop
  composition should be "offline, before commitment, via forward/backward replay... reactivation-over-stored-
  weights... not a separate discrete planning module" — this drill supplies the FIRST concrete, already-
  characterized, already-HARD_FAILed empirical regime where that general architectural claim can be tested,
  and predicts the SAME mechanism (bidirectional replay-generate-then-select) as this drill's independently-
  derived rank 1. Two independent lit-scans converging on the same specific mechanism from different starting
  questions is a real, if still uncertain, confidence boost (reflected in keeping P above the naive floor
  despite the sobering two-failed-attempts prior).
- Also cross-validates that same note's thread 2 (bimodal working memory: one active attractor + backgrounded
  activity-silent traces) as the natural HOME for holding multiple replay-generated candidates pending
  bidirectional scoring — this drill is a concrete consumer of that architectural primitive, not a
  duplicate proposal.
- Does not reopen the DIFFERENT-mechanism-class option-critic / BlocksWorld hierarchical-planning closures
  (2026-06-27/28, 2026-07-08) — those are a different domain and a different (discrete-option-library)
  mechanism, untouched by this finding, per `[[feedback-prior-work-informs-not-constrains]]`.

## (e) Substrate-product implications

- **If HARD-PASS:** the product-facing claim sharpens from "a rescue mechanism was tried and failed" (the
  current honest state) to "the substrate can recover a specific, quantified fraction of autonomous multi-
  step decomposition capability by adding a brain-grounded independent-verification mechanism (bidirectional
  candidate scoring) that off-the-shelf ML fixes did not supply" — a genuinely differentiated, brain-fidelity-
  driven capability claim, not a repeat of a generic hierarchical-planning story.
- **If HARD-FAIL:** the honest bound sharpens to its strongest form yet — "autonomous decomposition at 3+
  sequential no-oracle discovery steps is closed, and closed specifically in a way that survives BOTH
  self-referential and informationally-independent correction attempts" — this is a materially stronger,
  more defensible capability-map closure than either prior state, and correctly redirects future effort:
  the scaling build's hop-depth risk should be managed by (a) keeping real deployment chains SHORT (favor
  chunking/fewer, larger steps per the rank-3 finding, orthogonal to this HARD-FAIL) and (b) treating any
  deep multi-hop KB traversal as requiring either a bounded depth budget or an accept-degradation framing,
  rather than assuming a rescue mechanism will eventually be found for arbitrary depth.
- Either outcome, the rank-3 (chunking) and rank-4 (boundary reset) findings stand on their own and are cheap
  enough to test regardless of rank 1's outcome — recommend NOT gating rank 3/4 on rank 1's result, since
  they target a different, non-redundant axis (decision count / re-anchoring frequency vs decision
  independence) per the governing-principle analysis above.

---

## CELL SPEC — `exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1` (ready for exp_dev; NOT built yet)

**Inherits verbatim** from `exp_pfc_gate_autonomous_waypoint_discovery_v1.py` AND
`exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py`: all primitives listed in section (b) above, plus
the full entropy/regime grid and ALL existing arms as fixed, already-measured reference points
(`flat_gonogo`, `oracle_exec`, `hier_oracle`, `hier_shuffled`, `wp_bisect_open`, `wp_bisect_verify`,
`wp_bisect_coarse2fine`, `wp_bisect_combo` — all re-run in-cell on identical seeds for a proper paired
comparison, exactly as both ancestors did).

**New primitives (additive only):** `train_sr_transport` call on reversed transitions (`M_rev`/`R_rev`),
`generate_candidates`, `score_bidirectional`, `wp_replay_generate_select` — as specified in section (b).
Optional combined arm `wp_replay_generate_select_chunked` (rank 1 + rank 3) if smoke shows either alone
clears MIDDLE-band.

**Discriminators:** identical formula family to both ancestors (`recovery_ratio`, `autonomous_closure`,
`lift_flat`, `lift_random`, `lift_open`, `index_artifact_gap`, `anti_tautology_corr`, `degenerate_rate`,
`sign_test_p`, `cv`), PLUS `flatness_ratio` (`recovery_ratio(chain_steps=3) / recovery_ratio(chain_steps=1)`,
the direct operationalization of "stays flat vs hop-depth"), PLUS `bidirectional_agreement` (mean
`score_bidirectional` of the SELECTED candidate vs the mean over all `n_cand` generated candidates — reported
regardless, a high value with no recovery lift would itself be informative: bidirectional agreement is
possible but not predictive of correctness at this depth, a different, sharper negative than "no independent
signal available at all").

**HARD-PASS / HARD-FAIL / MIDDLE-BAND:** exactly as specified in section (c), evaluated at `op4_V1200_d8`
(identical FOCUS regime to both ancestors, for a clean three-way before/after/after-again comparison) and
reported for the full grid regardless.

**Smoke:** as specified in section (b) — reuse both ancestors' smoke grid + FOCUS at `op4_V300_d6`
(chain_steps=2) before any FULL dispatch.

**Compute:** one extra SR-training pass (`M_rev`, identical cost class to `M`/`M_long`), `n_cand=5` cheap
re-bisections per pick (reusing existing argmax/tie-break machinery, no retraining), one scoring function.
Should fit comfortably inside both ancestors' existing smoke/FULL wall-clock budget (rescue ancestor's FULL:
comparable unit count to the parent's 1789.5s/405 units; this cell adds units linearly).

---

## Dispatch readiness

Cell spec is complete and additive to both ancestor cells on disk. Per USER-locked discipline, no separate
hand-off routing file is written — this note is the complete, actionable deliverable. Director should read
this note directly and dispatch `hdi_exp_dev` with a pointer to this file plus both ancestor cell paths
(`experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py`,
`experiments/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py`) for verbatim-reused primitives.

---

## Citations (verified count: 15, all live-URL-confirmed via WebSearch this session, generic neuroscience/CS
terms only, no substrate-specific framing exposed off-platform per `[[feedback-query-privacy-decomposition]]`)

1. Hardcastle, Chen & Giocomo (2015), "Environmental Boundaries as an Error Correction Mechanism for Grid
   Cells," *Neuron*, PMID 25892299.
2. Zhang et al. (2022), "Place cells dynamically refine grid cell activities to reduce error accumulation
   during path integration in a continuous attractor model," *Scientific Reports*, PMC9744848.
3. Keinath et al. (2024), "Visual boundary cues suffice to anchor place and grid cells in virtual reality,"
   *Current Biology*.
4. Sreenivasan & Fiete (2011), "Grid cells generate an analog error-correcting code for singularly precise
   neural computation," *Nature Neuroscience*.
5. Burak & Fiete continuous-attractor grid-cell modeling program (drift/breakdown under uncorrected path
   integration), cross-referenced via "Robust and Efficient Coding with Grid Cells" (bioRxiv).
6. Mattar & Daw (2018), "Prioritized memory access explains planning and hippocampal replay," *Nature
   Neuroscience*.
7. Foster & Wilson (2006), "Reverse replay of behavioural sequences in hippocampal place cells during the
   awake state," *Nature*.
8. Pfeiffer & Foster (2013), full-path prospective replay at choice points (cited independently and
   consistently in today's parallel reasoning-loop drill, thread 4).
9. Graybiel (1998), "The basal ganglia and chunking of action repertoires."
10. Jin & Costa (2010), "Start/stop signals emerge in nigrostriatal circuits during sequence learning,"
    *Nature*.
11. arXiv:2507.09061 (2025), "Action Chunking and Exploratory Data Collection Yield Exponential Improvements
    in Behavior Cloning for Continuous Control" — horizon-free compounding-error bound under chunking.
12. arXiv:2603.22713 (2026), "Non-Adversarial Imitation Learning Provably Free of Compounding Errors: The
    Role of Bellman Constraints" — noted as a candidate future angle, not yet drilled.
13. Ross & Bagnell (2010), "Efficient Reductions for Imitation Learning," AISTATS (reused from the prior
    note's confirmed diagnosis, re-verified live this session).
14. Ross, Gordon & Bagnell (2011), DAgger (reused/re-verified).
15. Friston free-energy / Bastos et al. hierarchical predictive-coding laminar circuit literature (general
    framework citation for rank-5 mechanism, drawn from this session's "predictive coding bounded prediction
    error" search results).

All searches used generic terms ("grid cell path integration error correction," "hippocampal replay
prioritized sweeps," "predictive coding bounded error hierarchical," "cortico-striatal action chunking,"
"imitation learning compounding error reset") — no substrate-novel mechanism names, configs, or numerical
parameters were exposed off-platform, per `[[feedback-query-privacy-decomposition]]`.
