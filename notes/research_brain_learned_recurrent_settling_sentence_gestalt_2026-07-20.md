# RESEARCH DRILL: Learned recurrent settling as the fix for the settling-parse-selector HARD_FAIL (Sentence-Gestalt / N400-update mechanism, glass-box VSA design)

**Date:** 2026-07-20. **Filed by:** research (3 parallel Sonnet lit-scans -- axis 1 Sentence-Gestalt/N400-update
mechanism; axis 2 predictive-coding precision-weighting + attractor-dynamics convergence theory; axis 3
learned energy-based/diffusion/attractor literature for a buildable fix -- synthesized by director). Trigger:
direct VET finding that the settling-parse-selector cell (`research_brain_settle_to_coherence_parse_selection_2026-07-20.md`,
`exp_dev_handoff_research_settling_parse_selector_2026-07-20.md`) HARD_FAILED because its coherence readout
(residual-of-change across a beta=20 softmax cleanup) sat exactly at the float32 numerical noise floor
(pooled 0.5000, chance) -- the cleanup converges to a near-fixed-point in ~1 iteration, so there is no
residual left to read. VET's named fix: replace the one-shot algebraic cleanup with a LEARNED RECURRENT
dynamic (Rabovsky Sentence-Gestalt / N400-as-update framing), not another hand-tuned one-shot rule.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature agreement;
novel-synthesis capped P<=0.50).

---

## HEADLINE

**The brain mechanism is well-documented and gives an EXACT, quantitative precedent for the missing
component: Rabovsky, Hansen & McClelland's Sentence-Gestalt model defines its N400/coherence proxy as
`SU = sum_i |a_i(word_n) - a_i(word_{n-1})|` -- the summed absolute change in a recurrent hidden "gestalt"
state -- and this stays graded specifically because the network's training NEVER specifies a target for that
hidden state; only the query network's cross-entropy loss (matched to graded conditional probabilities, not
one-hot targets) shapes it, and training progressively shifts "the work" from activation change to connection
weights, so activation deltas stay informative rather than collapsing to a fixed decision. This gives both the
diagnosis and the fix in one move: our HARD_FAIL is the DENSE-ASSOCIATIVE-MEMORY / near-zero-noise-limit
END of a single, well-characterized mathematical spectrum that also contains diffusion models and graded
predictive coding at the other end (Hopfield cleanup, EBM Langevin sampling, and denoising diffusion are the
SAME family, differing only in effective noise/temperature -- a 2026 unification result makes this precise).
Beta=20 sits at the zero-noise (one-step, maximally sharp) end; the fix is to move along that SAME axis
toward the graded end via a LEARNED scalar (or short schedule), not to invent new machinery. Two concrete,
cheap, glass-box components fall out of the literature, rank-ordered by cost: (1) fit a single scalar
effective-inverse-temperature (or short annealing schedule) to plausibility-labeled data, targeting the
sub-critical/near-beta_c graded regime that is a proven phase transition in this exact family of networks;
(2) cap the per-iteration step size with a damped update (`x <- x + alpha*(cleanup(x)-x)`, alpha<1), which
makes multi-step-by-construction independent of any training at all (the diffusion-model trick). Both are
inspectable scalars/coefficients -- no runtime LLM, no black-box learned network required to satisfy the
glass-box invariant. The genuine open risk, deflated hardest below: it is possible the codebook's current
geometry is ALREADY well-separated enough that any sub-beta=20 value still collapses in ~1-2 steps -- i.e.
the "informative graded regime" may not exist for this codebook's actual pattern-separation statistics without
also changing codebook construction. This must be checked empirically before claiming success.**

---

## (1) THE BRAIN MECHANISM: Sentence-Gestalt as a learned recurrent update, and why it does not collapse

**Architecture and training (St. John & McClelland 1990, *Artificial Intelligence* 46:217-257; Rabovsky,
Hansen & McClelland 2018, *Nature Human Behaviour* 2:693-705 -- canonical, direct primary-source):** an
UPDATE network (word input -> hidden-1 -> "sentence gestalt" (SG) layer, itself recurrently feeding hidden-1
-- a simple recurrent net) and a QUERY network (role/filler probe -> hidden-2, combined with the CURRENT,
frozen SG state -> output). All units are sigmoid; there is no discrete cleanup or argmax step anywhere in
the architecture. Training is plain backprop (through the query network's cross-entropy error, backpropagated
into the update network via the SG-layer error), no hand-set weights, no stipulated target for the hidden SG
state itself -- the SG representation is shaped ONLY indirectly, through gradient averaged over many probes.

**The exact readout metric (direct quote-level precision):** `N400_n = SU_n = sum_i |a_i(word_n) - a_i(word_{n-1})|`
-- summed absolute (L1) unit-by-unit change in the SG layer, NOT Euclidean/L2, NOT cosine similarity. This
reproduces the N400 across ~16 ERP paradigms (semantic anomaly, cloze probability, plausibility, thematic-role
reversal).

**Why the update stays graded instead of collapsing -- three converging, directly-stated mechanisms:**
1. **The loss target is itself graded, not categorical.** Cross-entropy training drives each output feature
   toward the empirical CONDITIONAL PROBABILITY of that feature given context (activation ~0.7 when P~0.7)
   -- there is no winner-take-all target anywhere in the objective. A soft probability-matching optimum
   cannot produce a saturating, one-shot decision function; gradedness is baked into what "correct" even
   means for this network.
2. **Nothing forces the hidden state toward a small set of discrete attractor points.** The SG layer has no
   stipulated target vector; it settles wherever gradient descent leaves it under an indirect, probe-averaged
   error signal -- structurally the opposite of a fixed codebook cleanup, which is EXPLICITLY built to funnel
   every input to one of a small number of prototype points.
3. **"Shift of labour from activation to connection weights" (their own explicit finding, Fig. 4):** as
   training proceeds, OUTPUT-layer activation changes increase (sharpening toward true probabilities -- the
   output layer is where "committing to an answer" concentrates) while SG-LAYER update magnitude first rises
   then FALLS -- the query network's connection weights get strong enough that ever-smaller SG deltas produce
   the same output changes. The graded, informative quantity is preserved at the recurrent layer precisely
   because the network learns to amplify small state deltas downstream, rather than collapsing the state
   into a near-binary code. This is the single most direct, citable mechanistic answer to "why doesn't the
   residual go to zero" -- and it is the opposite bet from a hand-tuned high-gain cleanup, whose entire design
   goal is to eliminate residual in one step.

**Direct comparator already tested in this literature (not our exact contrast, but adjacent and informative):**
the SG model is directly compared against an SRN trained to predict next-word SURPRISAL (a softmax-based
scalar). Surprisal is shown to be a WORSE N400 model -- not semantics-specific (also driven by pure syntactic
anomaly), fails the developmental N400 DECREASE with training (surprisal keeps sharpening indefinitely since
softmax targets are one-hot/categorical), and under-responds on reversal-anomaly conflict items where SU shows
a graded increase. **No paper in this literature names a fixed/untrained associative-cleanup or codebook-argmax
model as an explicit alternative architecture** -- the closest documented competitor is exactly the
softmax/one-hot-target failure mode our cell exhibited, one level removed (output layer, not hidden-state
readout). Flag: this absence is itself informative -- fixed high-gain cleanups are not part of this literature's
model space at all; they belong to the separate dense-associative-memory literature below.

Follow-up: Rabovsky & McRae 2014 (*Cognition* 132) is an earlier, explicitly ATTRACTOR-based precursor
treating N400 as settling-error in word-meaning space -- worth noting because it shows the "attractor settling"
framing and the "trained recurrent update" framing are not mutually exclusive; Michaelov, Bardolph, Coulson &
Bergen (2020-2024, *Neurobiology of Language*/CogSci) extend to transformer-derived surprisal as an N400
analog -- a related but mechanistically DISTINCT (output-probability, not hidden-state-delta) proxy; whether
any of these compute a genuine hidden-state Δ-norm as an N400 analog was not fully verified in this pass
(flag as unverified beyond title/abstract level for the corpus-scale SG follow-up specifically).

## (2) PREDICTIVE-CODING SETTLING: precision-as-learned-gain and the dynamical-systems reason fast-vs-slow convergence happens

**Precision weighting controls step size, and precision is a LEARNED/estimated quantity, not a fixed knob
(canonical, Rao & Ballard 1999; Friston free-energy formalism; arXiv:2111.06942 "Predictive Coding, Precision
and Natural Gradients," 2021):** variational free energy decomposes into precision-weighted squared prediction
errors across hierarchy levels; precision plays the mathematical role of a Kalman gain, and because it gates
an error term feeding an iterative update, each pass only PARTIALLY corrects the error (proportional to the
gain) -- equilibrium is approached asymptotically, not solved in one jump. The precision-weighted update is
shown to be a local approximation to natural-gradient descent (Fisher-information-weighted), and precision
itself is estimated/learned (Friston's cholinergic-gain account casts it as something the brain estimates
online; ML formalizations build precision as a genuinely trainable parameter, reporting it beats fixed-gain
descent under noisy/uncertain conditions). **The crux answer for our design: "how fast/gradually beliefs
update" is architecturally treated as a co-adapted, learned quantity in this literature, not a fixed
hyperparameter** -- directly relevant since our failed cell used a hand-set beta=20 with no data-fitting step
at all.

**The dynamical-systems explanation for fast (1-step) vs slow (graded, multi-step) convergence (canonical,
dense-associative-memory / attractor-network literature):** the structural lever is the GAIN/TEMPERATURE
parameter's effect on the Jacobian's contraction eigenvalues near a fixed point. Modern/dense associative
memories (Krotov & Hopfield 2016 lineage) use a sharply-peaked exponential/softmax energy with a HAND-SET
HIGH inverse temperature; above a critical threshold, basins become steep and narrow, Jacobian eigenvalues
fall well below 1, and retrieval converges in essentially ONE step from a corrupted probe -- informative only
as a final identity, with no residual trajectory. This is EXACTLY our cell's failure mode, named precisely in
this literature rather than being a novel diagnosis. The opposite regime -- classical Hopfield networks, line
attractors, or systems near a bifurcation -- have a Jacobian eigenvalue approaching 1 ("critical slowing
down"), producing a near-flat slow manifold that lets the network integrate/retain graded, analog information
over many steps rather than snapping to a discrete state. **Precision-weighted predictive-coding models keep
gain moderate and adaptive because a too-sharp fixed gain both destabilizes learning and discards graded
uncertainty information** -- engineered one-shot associative memories deliberately push gain high for capacity
and robustness, sacrificing exactly the trajectory information our design needs.

**Is accumulated-trajectory error distinct from final-state error?** Partially established: current
predictive-coding-of-N400 work (2024, arXiv:2010.04844/2107.09648-adjacent) treats N400 as graded/cumulative
prediction error and finds SG-update and surprisal are "empirically dissociable but correlated" -- trajectory
information is not simply reducible to the final residual. A 2026 free-energy/integrated-information bridging
paper (single-study, more speculative) reports a hill-shaped trajectory of integrated information as free
energy decreases -- direct but thin evidence that the PATH, not just the endpoint, carries distinct
information. Treat this specific claim as weakly supported, not canonical.

## (3) THE UNIFYING BUILD-FIX: Hopfield cleanup, EBMs, and diffusion are ONE family differing only in effective noise/temperature

**The single most load-bearing citation for the buildable fix (2026, arXiv:2506.05178, "Associative Memory and
Generative Diffusion in the Zero-noise Limit"):** proves classical/modern Hopfield networks, energy-based
models, and denoising-diffusion models belong to the SAME mathematical family; a Hopfield-style cleanup is
formally a diffusion process taken to its ZERO-NOISE LIMIT. This gives a precise, principled name for our
failure: **beta=20 sits at the zero-noise end of exactly this spectrum, collapsing what could be a graded
multi-step diffusion-like settling process into instantaneous deterministic retrieval.** Restoring gradedness
is moving along this SAME, already-understood axis -- not inventing new machinery.

**Two concrete, ranked, cheap fixes, both glass-box (inspectable scalars/coefficients, no runtime LLM, no
opaque learned network required):**

1. **Learn a single scalar effective-beta (or a short annealing schedule) fit to plausibility-labeled data,
   targeting the sub-critical/near-beta_c graded regime.** Directly grounded: arXiv:2311.18434 ("Exploring the
   Temperature-Dependent Phase Transition in Modern Hopfield Networks," 2026) establishes a critical beta_c
   below which dynamics are graded/soft and above which they snap to sharp, near-1-step retrieval, and shows
   beta_c is a FITTABLE, DATA-DEPENDENT scalar (depends on stored-pattern separation), not a universal
   constant. This is the cheapest possible learned component: one number, fit by gradient descent (or a small
   grid search against labeled plausible/implausible items), replacing the hand-set beta=20.
2. **Cap the per-iteration step size with a damped update** (`x <- x + alpha*(cleanup(x) - x)`, alpha<1),
   forcing multi-step-by-construction REGARDLESS of gain. Directly grounded in discrete/graph diffusion
   literature (DIFUSCO, NeurIPS 2023; arXiv:2503.21592, 2026): each denoising step is structurally constrained
   to remove only a small amount of corruption, so 1-step collapse is architecturally impossible independent
   of any semantic training. This needs NO learning at all if alpha is hand-set (lowest risk, cheapest to
   implement), or can itself be a single learned scalar if a fixed value underperforms.

A third, more expensive but more semantically-grounded option surfaced (contrastive-divergence-style training
of the similarity/energy function itself on coherent-vs-corrupted composed-vector pairs, per canonical CD/EBM
literature) -- flagged as higher-cost (needs a genuine contrastive-pair training set that may not yet exist)
and held in reserve rather than recommended as the first cut.

**Minimal recommended first cut (per the lit-scan's own ranking): combine fix (1) + fix (2)** -- damped step
size guarantees gradedness mechanically (lowest risk), learned effective-beta targets the SPECIFIC graded
regime this codebook's separation statistics support (adds the semantic-fitting piece cheaply). Fix (3)
(trained similarity function) is held in reserve if (1)+(2) restore gradedness but not semantic tracking.

**Genuine open risk (must be checked empirically, not assumed away):** beta_c is pattern-distribution
dependent (arXiv:2311.18434) -- it is possible our codebook's current construction is separated enough that
EVERY beta below 20 down to some point still collapses in 1-2 steps, meaning the graded regime may not exist
for this codebook without ALSO changing codebook construction (not just the settling dynamic). This is the
single biggest reason to deflate P below the raw literature-agreement level.

## Cheap decisive test

Reuse the exact ambiguous-sentence item set + gold-preference labels already assembled in
`research_brain_settle_to_coherence_parse_selection_2026-07-20.md` (G5: genuinely underdetermined
PP-attachment / reversible-thematic-role items). For each candidate parse, run FOUR settling variants under
the SAME codebook, same item set, same seed policy:
(A) the ALREADY-MEASURED one-shot beta=20 cleanup (current HARD_FAIL baseline, residual pinned at noise
floor, pooled 0.5000);
(B) fix (2) alone -- damped step (alpha<1, hand-set, no learning) at the SAME beta=20;
(C) fix (1)+(2) -- damped step + effective-beta fit to a held-out slice of the gold-preference labels (grid
search or 1-parameter gradient fit; report the fitted beta relative to beta_c where estimable);
(D) MUST-FAIL CONTROL -- a RANDOM recurrent update (same damped-step structure, but the per-iteration
"cleanup" direction replaced by a random unit vector / randomly shuffled codebook match, decoupling
"multi-step recurrence" from "learned/meaningful direction").

Report, at every variant: (i) residual-of-change magnitude and its variance across items (is it above the
measured float32 noise floor from the failed cell, by how many orders of magnitude); (ii) iteration count to
convergence and the correct/spurious/non-convergent breakdown (per G8 of the prior note); (iii) correlation
(Spearman) between residual/selection-accuracy and gold plausibility labels.

## Falsifiable predictions

**HARD-PASS (all must hold, pre-registered):**
1. Variant (C) (learned-beta + damped-step) produces a residual-of-change distribution with variance
   spanning >=3 orders of magnitude above the noise floor measured in the original failed cell (i.e.
   demonstrably NOT pinned at the float32 chance value).
2. Variant (C)'s residual (or selection accuracy) correlates with gold plausibility at Spearman rho>=0.3, OR
   beats the one-shot thematic-fit baseline from the prior note's G3 by >=10 percentage points selection
   accuracy.
3. Variant (C) outperforms variant (A) (the original one-shot failure) by construction (A measured at exact
   chance, so any real correlation clears this bar) AND outperforms variant (D) (must-fail random-recurrent
   control) by a non-trivial, pre-registered margin -- confirming the LEARNED direction, not mere multi-step
   recurrence, carries the information.
4. The fitted effective-beta in variant (C) lands measurably below beta_c (or below the hand-set beta=20),
   confirmed via the iteration-count sweep showing genuine multi-step (not 1-2 step) convergence.

**HARD-FAIL (any one is sufficient to refute):**
1. Variant (C)'s residual stays pinned at/near the float32 noise floor regardless of the learned-beta /
   damped-step change -- mirrors the original failure exactly, meaning the fix did not touch the actual
   mechanism (most likely explanation: the codebook's pattern separation makes EVERY sub-beta=20 value still
   collapse in ~1 step -- the graded regime does not exist for this codebook without also changing codebook
   construction; this must be reported explicitly if it occurs, not silently re-tuned away).
2. Variant (C) does NOT beat variant (D) (must-fail random-recurrent control) -- multi-step recurrence alone,
   not the learned/meaningful update direction, explains any observed gain; the "learned" component is not
   doing real work.
3. Variant (C) shows nonzero residual variance (fix mechanically works) but null correlation with gold
   plausibility (|rho|<0.15) -- gradedness achieved but not semantically meaningful; damped-step-only (fix 2)
   without effective-beta fitting (fix 1) is the likely culprit, meaning fix (3) (trained similarity function)
   becomes necessary rather than optional.
4. The beta fit in variant (C) converges back to the SAME high-gain regime as the original beta=20 (i.e. the
   data-driven fit re-derives the one-shot collapse) -- meaning the fixed point WAS actually optimal for this
   codebook's geometry and the "informative graded residual" premise is false for this substrate as currently
   constructed.

## Cross-thread synthesis

- Directly resolves the open question at the end of `research_brain_settle_to_coherence_parse_selection_2026-07-20.md`
  and its companion `exp_dev_handoff_research_settling_parse_selector_2026-07-20.md`: that note already
  identified Rabovsky et al. as "the single most load-bearing citation" for the residual-as-coherence design
  but treated the settling MECHANISM itself as a placeholder (resonator-style unbind-clean-up OR
  Hopfield-style relaxation, beta as a fixed hyperparameter per its own G9 guard). This drill supplies the
  missing piece that guard anticipated but did not resolve: beta is not free to hand-tune, and the fix is
  specifically to make it a LEARNED, data-fit quantity targeting a proven phase-transition regime (beta_c),
  not merely "fix beta globally" as G9 originally specified.
- Extends `research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`'s "energy = resolution"
  framing: that note found predictive-coding precision-weighting is a LOCAL gain, not a separate controller.
  This drill adds the missing dynamical-systems mechanism for WHY that gain must stay moderate/adaptive rather
  than maximally sharp -- a too-high gain (our beta=20) is the zero-noise/zero-information limit of the same
  spectrum that gives coarse-to-fine its whole graded character elsewhere in the program.
- Relevant to the still-open forensic question in `SYNTHESIS_platform_maturity_and_the_missing_learning_loop_2026-07-20.md`
  (contrastive predictive-coding signal HARD_FAIL pending audit): this drill demonstrates a SECOND, independent
  instance of the same general failure class (a hand-set high-precision/high-gain rule collapsing to a
  construction-determined answer with zero information) now diagnosed with a named, well-understood
  mathematical cause (dense-associative-memory zero-noise limit) -- worth checking whether the stalled CPCL-v2
  loop exhibits the SAME symptom (a too-sharp comparison/contrast function) rather than treating the two as
  unrelated negatives.
- The three lit-scan axes converge on a single throughline: gradedness is not a property you get for free from
  "adding recurrence" -- it requires either (a) a LOSS FUNCTION with no discrete/one-hot target (the
  Sentence-Gestalt route), (b) a LEARNED, moderate, data-fit gain/precision parameter (the predictive-coding
  route), or (c) a STRUCTURAL step-size cap independent of gain (the diffusion route). The substrate's failed
  cell had none of the three. The recommended minimal fix supplies (c) immediately (near-zero risk, mechanical)
  and (b) cheaply (one fitted scalar), holding (a)/(the CD-trained-energy-function route) in reserve.

## Substrate-product implications

A working learned-recurrent settling readout would give the product a genuinely graded, inspectable
plausibility/coherence trace (per-iteration residual trajectory, not a single opaque score) -- directly
supporting the auditable glass-box value proposition: a user-facing "how confidently did this settle, and over
how many steps" trace, with the fitted effective-beta/damping coefficient as an inspectable, loggable number
(never a black-box learned network at runtime). This also directly informs the broader missing
learning-and-self-monitoring layer: a genuinely graded coherence signal is a prerequisite for the
metacognition/abstain and reliability-gate machinery already built in that layer to have a meaningful graded
input to gate on, rather than a chance-level one. If HARD-FAIL condition 4 above fires (codebook geometry
forces the collapse regardless of beta), that is itself a valuable, falsifiable finding about a REAL structural
limit of the current codebook construction, not this settling mechanism specifically -- and would redirect the
next drill toward codebook/pattern-separation construction rather than further settling-dynamics tuning.

## Citations (verified count: 20 distinct sources across the three lit-scans, cross-checked for
canonical-vs-speculative status by the synthesizing agent)

Sentence-Gestalt / N400-update: St. John & McClelland (1990, *Artificial Intelligence* 46); Rabovsky, Hansen &
McClelland (2018, *Nature Human Behaviour* 2); Rabovsky & McRae (2014, *Cognition* 132); Michaelov, Bardolph,
Coulson & Bergen (2020-2024, *Neurobiology of Language*/CogSci, surprisal-based N400 analog); Brouwer,
Crocker, Venhuizen & Hoeks (2017, retrieval-integration/P600 model, adjacent).

Predictive coding / precision / dynamical systems: Rao & Ballard (1999, *Nature Neuroscience*); Friston
free-energy/cholinergic-precision review (PMC4235126); "Predictive Coding, Precision and Natural Gradients"
(arXiv:2111.06942, 2021); predictive-coding-of-N400 2024 work (ScienceDirect S0010027724000416, PMC10984641);
line-attractor/bifurcation work (arXiv:2408.00109, NeurIPS 2024 "Back to the Continuous Attractor").

Energy-based / diffusion / Hopfield unification: Hinton contrastive divergence (canonical, pre-2020);
"Improved Contrastive Divergence Training of EBMs" (arXiv:2012.01316, ICML 2021); "Diffusion Contrastive
Divergences" (arXiv:2307.01668); DIFUSCO (NeurIPS 2023); discrete/graph diffusion (arXiv:2503.21592);
"Associative Memory and Generative Diffusion in the Zero-noise Limit" (arXiv:2506.05178, 2026 -- the
single most load-bearing unification citation); "Exploring the Temperature-Dependent Phase Transition in
Modern Hopfield Networks" (arXiv:2311.18434, 2026 -- establishes the fittable beta_c); "Adaptive Hopfield
Network: Rethinking Similarities in Associative Memory" (arXiv:2511.20609, 2026, most speculative/newest).

P_deflated(diagnosis: beta=20 one-shot collapse = zero-noise-limit of a well-characterized dense-associative-
memory/diffusion spectrum) = **0.60** (the underlying math -- high-gain Hopfield collapsing in ~1 step -- is
canonical and directly matches the measured symptom; deflated from a natural ~0.80 because the specific
zero-noise-limit UNIFICATION paper is single-study/2026 and not yet independently replicated).

P_deflated(recommended fix -- damped step + learned effective-beta -- HARD-PASSes the cheap decisive test above)
= **0.40** (novel-synthesis cap applies; genuine, undeflated risk that this codebook's pattern-separation
statistics place beta_c above beta=20's neighborhood entirely, in which case no beta below the current value
restores gradedness without also changing codebook construction -- this is a real, not hypothetical, failure
mode per arXiv:2311.18434's own finding that beta_c is pattern-distribution-dependent).
