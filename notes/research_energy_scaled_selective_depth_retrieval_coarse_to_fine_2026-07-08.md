# Research Drill: Energy-Scaled Selective-Depth Retrieval (Coarse-to-Fine as an Energy Dial) (2026-07-08)

**Author:** Research (Sonnet)
**Trigger:** USER strategic steer -- architectural-direction question, not routine lit-scan. Extend
`research_drill_encoder_target_metric_coarse_cosine_vs_fine_retrieval_2026-07-04.md` (which already
proposed a Tier1-coarse/Tier2-fine retrieval split) with the brain-grounded "energy=resolution" framing,
and connect it explicitly to the in-flight `exp_encoder_phase_traversal_spread_condense_v1.py` smoke and
to the certified `exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py` attention-routing gate.
**Method:** internal grounding (full read of the 07-04 note, full read of the phase-traversal cell source,
docstring read of the combinedgate cell + its own brain-grounding note
`research_content_gate_brain_grounding_2026-07-08.md`) + external web lit-scan (4 targeted searches, 2
fetches for primary-source verification), generic math/neuro terms only, no substrate-internal names or
numbers sent off-platform.
**Calibration:** per [[feedback-lit-scan-calibration-penalty]], all P estimates below are deflated
0.15-0.25 from raw confidence; novel-synthesis claims (the mapping onto the phase-traversal cell's
existing arms, the combinedgate composition argument) are capped at P<=0.50.

---

## HEADLINE

**The brain runs a genuinely GRADED, multi-level coarse-to-fine hierarchy (predictive-coding precision
weighting, reverse-hierarchy-theory feedback refinement, familiarity-then-recollection dual-process
memory) where "spend more energy" == "read more levels/iterations," gated LOCALLY by a
confidence/ambiguity signal computed at the point of decision -- not by a separate controller. The
substrate's in-flight `phase_traversal` cell is honestly NOT yet that dial: as coded, it is a FIXED
two-representation pair (spread-store, condense-retrieve), evaluated on the FULL V-item dictionary every
time, with no continuous or per-query resolution knob. But its own arm structure (`spread_static` =
cheap coarse cosine; `phase_traversal` = trained condenser) already IS the Tier1/Tier2 split from the
07-04 note, in code, today -- it is simply not yet GATED (Tier2 runs on all V, not a shortlist). The
single highest-value, near-zero-new-code change is: gate the condenser forward pass to a Tier1-ranked
top-k shortlist instead of all V. That change turns an existing fixed-cost cell into the brain-grounded
energy-scaled dial the task asked about, without inventing a new mechanism.**

P_deflated(predictive-coding energy economy + coarse-to-fine vision + familiarity/recollection memory
converge on the same "cheap coarse default, expensive detail on-demand, locally gated" shape) = **0.70**
(three independent, well-established literatures converge; deflated from a natural ~0.90-0.95 because
convergence-of-analogy across domains is not the same as convergence-of-mechanism).
P_deflated(phase_traversal's `spread_static`/`phase_traversal` arms are ALREADY an un-gated Tier1/Tier2
pair, and shortlist-gating the condenser would preserve SC while cutting condense-compute by >=10x) =
**0.45** (capped; directly verified on-disk that the arm STRUCTURE matches, but the compute-preservation
claim is an untested prediction, not yet measured).
P_deflated(binary Tier1/Tier2 is sufficient vs. brain lit demanding a continuous/multi-level cascade) =
**0.40** (capped novel-synthesis; the honest answer is "binary is a legitimate first step, but the lit
suggests more levels help further" -- see Part 3).

---

## Part 1 -- The brain mechanism, beyond Rao-Ballard (already cited in this corpus)

The corpus already has Rao & Ballard 1999 hierarchical predictive coding
(`research_drill_realtime_multimodal_biology_3x_2026-06-09.md`) and the Friston free-energy framing
(`research_drill_friston_fep_substrate_framework_2x_2026-06-04.md`). Three further, independent threads
extend past that baseline and were not previously in this corpus:

**1. Energy efficiency is SUFFICIENT to derive predictive coding, not just consistent with it.**
Recent theoretical work shows hierarchical predictive-coding-like dynamics (precision-weighted,
sparse-error propagation) EMERGE from optimizing a recurrent/spiking network purely for energy
efficiency, without independently assuming a Bayesian-inference objective ("Predictive coding is a
consequence of energy efficiency in recurrent neural networks," ScienceDirect / Patterns 2022; "Energy
optimization induces predictive-coding properties in a multi-compartment spiking neural network model,"
PMC 2026). This matters for the substrate framing: "energy = resolution" is not a heuristic overlay on
top of a separately-justified coarse/fine architecture -- it is what falls out when ANY hierarchical
system is optimized under a hard energy/compute budget. The corollary: precision weighting (how much a
given error signal is trusted / how hard the system tries to resolve it) is ITSELF the resolution dial,
implemented as a multiplicative gain on the error signal at each level of the hierarchy, not a separate
control loop bolted onto a fixed-resolution architecture.

**2. Coarse-to-fine vision is a GRADED, feedback-iterated cascade, not a single jump.**
Hochstein & Ahissar's Reverse Hierarchy Theory (Neuron 36:791-804, 2002; Ahissar & Hochstein, TICS 2004)
-- vision builds an implicit, fast, feedforward "gist" at HIGH cortical levels first (using low
spatial-frequency information that reaches association cortex fastest via the magnocellular pathway),
and explicit/conscious perception then walks BACKWARD down the hierarchy via feedback, recruiting
progressively lower (finer-detail, better signal-to-noise for FINE discrimination) areas only as task
demands require it. This is corroborated by direct neural evidence of coarse-to-fine dynamics in human
V1 via backward-masking (bioRxiv 2023) and by neuroimaging of spatial-frequency processing during scene
perception (Frontiers/PMC4019851, 2014). The key extension past Rao-Ballard: this is not a single
coarse-pass-then-fine-pass binary -- it is an ITERATIVE, multi-round feedback refinement, and perceptual
LEARNING follows the same reverse-hierarchy route (learning starts at high levels, drops down to lower
levels only when the high-level representation is insufficient).

**3. Memory retrieval has an empirically well-established coarse/fine SPLIT with a LOCAL gating signal.**
Yonelinas' dual-process model of recognition memory (Yonelinas 1994, 2001, 2002; meta-analytic support
in Yonelinas 2002 review) distinguishes: FAMILIARITY -- a fast, CONTINUOUS, signal-detection-style
"overall similarity" signal (perirhinal cortex), available for every candidate cheaply -- from
RECOLLECTION -- a slower, threshold-triggered, DETAILED contextual retrieval (hippocampus proper) that
fires only when familiarity is high enough or task demands (source memory, associative binding) require
it. This is the closest primary-neuroscience analog to "cheap coarse signal computed for everyone,
expensive detailed readout triggered locally by that same signal crossing a criterion." A direct modern
COMPUTATIONAL realization of exactly this split already exists in the ML literature: HippoMM (Lin et
al., arXiv:2504.10739, 2025) explicitly builds an artificial memory system with two retrieval modes --
"rapid semantic access through CA1" and "detailed pattern completion through CA3 recurrence" -- and
dynamically SELECTS which mode to run PER QUERY based on the query's demands. This is not a
neuroscience-primary source (it's an ML systems paper using hippocampal naming as inspiration), but it
is directly relevant: independent engineers, working from the same brain literature, already built the
Tier1/Tier2-with-gating architecture this drill is asking about, and it works well enough to publish.

**4. The ML/systems literature independently confirms the computational value, outside any brain framing.**
Cascade/early-exit systems (BranchyNet; CascadeBERT; "layered retrieval cascades"; adaptive-computation
early-exit dense retrieval) all show the same pattern: route the EASY majority through a cheap coarse
stage, escalate only the ambiguous minority to an expensive fine stage, gated by a confidence/entropy
threshold (fixed or learned). This is convergent, domain-general evidence (not brain-specific) that
coarse-first + selective-escalation dominates fixed-uniform-resolution on the accuracy/cost frontier.

---

## Part 2 -- What it buys computationally, and the tradeoff-curve shape

**Cost model.** Let V = number of candidates, C_coarse = cost of one coarse-signal evaluation (cheap:
sparse/quantized cosine, or a static code with no forward pass), C_fine = cost of one fine/detailed
evaluation (expensive: dense forward pass, learned condensation, full-precision compare). Fixed-uniform-
fine costs `V * C_fine`. Fixed-uniform-coarse costs `V * C_coarse` but is capped at whatever accuracy
ceiling the coarse signal alone supports (this cell's own `spread_static` control arm IS that ceiling --
the QE-1 "beta-knob" no-op corner). Coarse-first + selective-fine costs `V * C_coarse + k * C_fine` where
k = shortlist size. Since natural similarity distributions are SKEWED (most queries are not near a
decision boundary; only a minority are genuinely ambiguous -- this is the same empirical regularity that
makes early-exit ML systems work), k << V in the typical case, so the combined cost approaches
`V * C_coarse` (cheap) while the accuracy approaches the fine ceiling (expensive), as long as the coarse
signal reliably PUTS the true answer inside its top-k shortlist.

**Tradeoff-curve shape is a KNEE, not a line.** Fixed-resolution architectures are forced to pick ONE
point on the accuracy-vs-cost curve and pay that cost for EVERY query regardless of difficulty. A
selective-depth architecture instead traces close to the PARETO FRONTIER connecting the coarse corner
(cheap, capped accuracy) and the fine corner (expensive, ceiling accuracy) -- concretely, it can sit at
"cost near the coarse corner, accuracy near the fine corner" precisely because the two are decoupled by
routing compute conditionally rather than uniformly. This is why fixed-uniform-resolution is STRICTLY
worse in this framing: any single fixed point either overpays on the easy majority (uniform-fine) or
underpays on the hard minority (uniform-coarse); a query-conditional dial dominates both simultaneously.
This is a domain-general result (predictive coding, RHT, familiarity/recollection, and BranchyNet/
CascadeBERT all instantiate the identical curve-shape argument) -- not something specific to this
substrate.

---

## Part 3 -- The minimal substrate-implementable version: grounding against the LIVE cell, honestly

**What the phase-traversal cell IS, read directly from `experiments/exp_encoder_phase_traversal_spread_
condense_v1.py`:** it is NOT a continuous temperature/energy-as-resolution dial. There is no per-query
"spend more" knob. It is a FIXED pair of representations of the SAME stored item: (a) `s = WTA_topk(x @
W_up)` -- a sparse-bipolar spread code with a FIXED sparsity `k = N//32`, used for superposition/bundling
(SP), and (b) a trained 2-layer MLP condenser `c = gelu(s @ W1) @ W2` -- a FIXED, once-trained-per-run
structural transform, used for pointwise discrimination (SC), evaluated over the FULL V-item dictionary
every time (`dict_code = condense(z_dict)` runs on all V rows). The task brief's framing ("presumably a
temperature-like parameter that trades resolution for cost") does not match what is actually being
tested here -- flagging this explicitly per the filesystem-verify discipline rather than inventing a
disconnected dial or silently agreeing with an inaccurate premise.

**But the arm structure the cell ALREADY has is exactly Tier1/Tier2, un-gated.** Its `spread_static` arm
(SC computed directly on the raw spread code, no transform) IS Tier1 from the 07-04 note (cheap, coarse,
"is this in the right neighborhood at all" -- literally the QE-1 beta-knob ceiling, which this cell uses
as its own frontier/control corner). Its `phase_traversal` headline arm (SC computed after the trained
condenser) IS Tier2 (fine, expensive, "settle onto the discriminative semantic manifold"). The cell's own
pre-reg already frames these as a frontier ("spread_static" vs "semantic_static" corners) and measures a
`structural_gain` between them -- conceptually adjacent to what a Tier1-to-Tier2 gain would need to be,
but currently measured over ALL V, not a shortlist.

**The concrete, near-zero-new-mechanism change:** gate the condenser's forward pass (currently `O(V)`,
one MLP call per dictionary item on every read) to a Tier1-ranked shortlist. Concretely: (1) compute
`spread_static`-style raw cosine over the FULL V-item spread-code dictionary (already computed, already
cheap -- this is the coarse familiarity signal, analogous to Yonelinas' fast continuous signal); (2) take
the top-k by that cosine (k << V, e.g. k = O(sqrt(V)) or a small fixed constant); (3) run the condenser
ONLY on those k candidates plus the query, and argmax within that shortlist. This preserves the cell's
existing HARD-PASS/HARD-FAIL classification machinery (SP unaffected; SC now measured on a gated
pipeline instead of an all-V one) and requires no new trained parameters -- it is an evaluation-order
change on top of arms the cell already trains.

**Is binary Tier1/Tier2 the right shape, or does the brain literature want something more graded?**
Honest answer: BOTH are partially right. The Yonelinas familiarity/recollection split IS empirically a
clean binary two-system dual-process (not a strawman simplification -- it is the best-supported model in
that literature), so binary Tier1/Tier2 is a legitimate, minimal, BRAIN-GROUNDED first step, not an
under-powered compromise. But predictive coding and Reverse Hierarchy Theory are explicitly MULTI-LEVEL
and ITERATIVE (RHT's feedback walks DOWN through several cortical levels, not one jump; predictive coding
has as many levels as the cortical hierarchy has areas). The cell already contains the raw ingredients
for a richer, multi-level cascade WITHOUT new code: `phase_traversal` (wta_sign input, cheapest condense
input), `phase_traversal_mag` (topk_mag input, middle), `phase_traversal_dense` (dense input, most
expensive/most information-preserving) are currently run as three PARALLEL, independent enrichment arms
-- but they could instead be SEQUENCED as progressive stages (Tier1 raw cosine -> Tier1.5 condense on
`wta_sign` over a wide shortlist -> Tier2 condense on `dense` input over a narrow shortlist), which is
structurally closer to RHT's iterative-refinement shape than a flat two-tier split. Recommend: ship
binary Tier1/Tier2 gating first (cheapest, matches the best-evidenced brain analog, reuses zero new
training), and treat the 3-stage cascade as the NEXT lever if binary gating HARD-PASSes but leaves
headroom to the oracle ceiling.

---

## Part 4 -- Composition with the combinedgate attention-routing gate

The certified `exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py` cell answers "WHICH
context slot is relevant," via biased-competition arbitration (Desimone & Duncan 1995; Reynolds & Heeger
2009 normalization) between a recency prior and a content-cue bias, softmax over
`combined_logit_j = content_rel_j / GATE_TAU + recency_bias_j`. This drill's question is "AT WHAT
RESOLUTION should the winning (or top-few) slot be READ," once selected.

**These are not the same decision, but they share the identical mathematical primitive** (competitive
normalization / softmax arbitration over a per-candidate scalar), and that shared primitive gives a
nearly-free composition path: the combinedgate cell ALREADY computes `content_rel_j` for every candidate
as part of deciding the winner. The MARGIN of that softmax distribution (how much sharper the winning
slot's logit is than the runner-up's) is a confidence/ambiguity signal the gate computes FOR FREE, as a
byproduct of the WHICH-decision, not a new computation. That margin is a natural, already-available input
to the resolution decision: a sharp, well-separated winner (like the cell's own ALIGNED regime, or
CONFLICT above the arbitration boundary `q* = GATE_TAU * RECENCY_GAP_TARGET`) suggests the coarse
(Tier1) readout of that slot is already trustworthy -- no drill-down needed. A flat, ambiguous
distribution (like the cell's own CUE_ABSENT / sub-boundary low-q tail, where content is noise and the
gate falls back to a prior) is exactly the regime where the WHICH-decision itself was uncertain, and is a
natural (though not yet tested) trigger to escalate to Tier2 drill-down on the top-few candidates.

**Honest caveat:** this is analogical/architectural composition, not measured composition. The
combinedgate cell's low-q fallback is a WHICH-decision fallback (falls back to a recency PRIOR, does not
spend MORE compute), not a HOW-FINE-to-read decision -- no existing cell tests spending additional
condense-style compute when the gate's margin is low. The right framing is "one mechanism (competitive
normalization), two readouts (argmax for WHICH, margin for WHETHER-TO-DRILL)," reusing an already-
computed signal rather than layering a second, disconnected controller on top -- but this composition
itself is a new, untested prediction (P capped at 0.40, novel synthesis).

---

## Cheap decisive test

Re-analysis of already-produced `exp_encoder_phase_traversal_spread_condense_v1` artifacts (once the
in-flight smoke lands), no new cell required for the first pass:

1. Using the cell's existing per-seed dictionary codes (`spread_static` raw cosine dict, `phase_traversal`
   condensed dict), compute a SHORTLIST-GATED pipeline: rank all V items by `spread_static`-style raw
   cosine, take top-k (k = 5, 20, 50 as a sweep -- cheap, all off already-computed cosines), then within
   that shortlist find the argmax under the CONDENSED code (already computed for the full V, just
   restrict the argmax to the k indices).
2. Compare shortlist-gated SC@alpha_OP against (a) uniform-coarse (`spread_static` SC, the existing
   control arm) and (b) uniform-fine (`phase_traversal` SC over all V, the existing headline arm) at the
   SAME alpha_OP=1.2 operating point.
3. Cost-adjusted accuracy metric: `SC_shortlist_gated / (k / V)` normalized against
   `SC_uniform_fine / 1.0` -- i.e. does the gated pipeline recover most of the fine accuracy at a small
   fraction of the condense-compute.

**HARD-PASS:** shortlist-gated SC@alpha_OP is within 0.03 of uniform-fine (`phase_traversal`) SC@alpha_OP
at k <= 0.10 * V (condenser called on <=10% of the dictionary). This would show the coarse cosine
reliably contains the true near-neighbor in its shortlist, licensing gated condensation as a real
compute-savings lever with no meaningful accuracy cost.

**HARD-FAIL:** shortlist-gated SC@alpha_OP is more than 0.10 BELOW uniform-fine SC@alpha_OP at k = 0.10 *
V (or requires k > 0.50 * V to close within 0.03). This would show the coarse signal is not predictive
enough of true near-neighbor membership to safely gate the expensive step at useful shortlist sizes --
i.e. the coarse and fine geometries are too decoupled for staged retrieval to help here, and the two-tier
architecture would need a better (not just cheaper) coarse signal before gating pays off.

**MIDDLE:** shortlist-gated SC lands in the gap between HARD-PASS and HARD-FAIL bands (0.03-0.10 below
uniform-fine at k=0.10*V) -- gating helps but needs a larger k or a stronger coarse signal (e.g. the
`topk_mag` enrichment arm's cosine instead of `wta_sign`) before it is a clean win.

---

## Falsifiable predictions

**HARD-PASS** (coarse-to-fine gating is a real, brain-consistent lever for this substrate, worth
building into the phase-traversal cell's read path):
- Shortlist-gated SC@alpha_OP within 0.03 of uniform-fine SC@alpha_OP at k <= 0.10*V (per cheap decisive
  test above), AND
- The shortlist HIT RATE (fraction of queries where the true nearest concept, per the condensed dict, is
  actually inside the coarse top-k) is itself >= 0.90 at that same k -- confirming the coarse signal is
  doing real filtering work, not passing by accident of a saturated/easy corpus.

**HARD-FAIL** (coarse-to-fine gating does NOT transfer to this substrate's current code; a different
coarse signal or a non-staged architecture is needed):
- Shortlist hit rate stays below 0.70 even at k = 0.25*V -- the raw spread cosine ranking is too weakly
  correlated with the condensed/semantic ranking to serve as a cheap filter at any useful shortlist size,
  meaning Tier1 and Tier2 geometries are closer to independent than nested.

---

## Cross-thread synthesis

- **`research_drill_encoder_target_metric_coarse_cosine_vs_fine_retrieval_2026-07-04.md`**: this drill
  directly extends Part 2 of that note. That note proposed Tier1/Tier2 in the abstract and cited it as
  P_deflated=0.50 novel synthesis; this drill (a) grounds it in three brain literatures beyond the
  regime-switching directive alone, (b) finds the phase-traversal cell (authored AFTER that note, same
  week) already implements the Tier1/Tier2 REPRESENTATION split as arms, just not yet the GATING, and (c)
  proposes the cheap re-analysis test to close that gap using already-collected artifacts.
- **`research_content_gate_brain_grounding_2026-07-08.md`** (combinedgate's own grounding note): the
  biased-competition/normalization framing there is the SAME primitive this drill leans on in Part 4 for
  the WHICH-vs-HOW-FINE composition argument -- both drills independently converge on Desimone & Duncan
  / Reynolds & Heeger as the substrate-relevant attention primitive, from two different questions (WHICH
  slot vs WHAT resolution).
- **`research_drill_realtime_multimodal_biology_3x_2026-06-09.md` / `research_drill_friston_fep_
  substrate_framework_2x_2026-06-04.md`**: this drill does not re-derive Rao-Ballard/Friston; it adds the
  energy-efficiency-implies-predictive-coding result (Ali et al. 2022; PMC 2026), Reverse Hierarchy
  Theory, and Yonelinas dual-process memory as three NEW threads not previously in this corpus, plus the
  HippoMM direct computational precedent.
- **`substrate_capability_map.md` "Free hierarchical retrieval index via RSB" / SKAH-M rows**: those
  findings are about the substrate's STORAGE-side multi-basin discrete structure (a phase-classification
  question). This drill's coarse-to-fine mechanism is a READ-TIME resolution-allocation question,
  orthogonal to but potentially compatible with that structure -- a multi-basin store could plausibly
  serve as a natural coarse-Tier1 index (basin membership as a cheap first filter) with fine discrimination
  happening within-basin, but this is speculative and not tested here; flagged as a candidate follow-on
  adjacency, not a claim.

---

## Substrate-product implications

- **No new mechanism needs to be invented.** The phase-traversal cell's existing arm structure already
  contains a Tier1 (spread_static) and Tier2 (phase_traversal condense) pair; the missing piece is GATING
  Tier2 to a Tier1-ranked shortlist rather than running it over the full dictionary. This is an
  evaluation-order change, testable on already-collected artifacts once the smoke lands, per the Cheap
  decisive test above.
- **Honest correction of the task's premise**: there is currently no continuous energy/temperature dial
  in the substrate's encoder work -- the phase-traversal cell is a fixed two-representation pair, not a
  gradient. If the substrate wants an actual per-query graded dial (not just binary gating), that is a
  DIFFERENT, larger build (e.g. an iterative/recurrent condenser with a variable number of settling
  steps, closer to RHT's iterative feedback) and should be scoped separately from the near-zero-cost
  gating change proposed here.
- **Composition with combinedgate is a genuine, cheap-to-test, not-yet-tested prediction**: the gate's
  own arbitration margin (already computed) is a candidate free confidence signal for the resolution
  decision. This should be filed as a follow-on empirical question (does low arbitration margin predict
  cases where drill-down actually helps?), not assumed.
- **No separate real-time controller is needed for the coarse-to-fine decision itself** (see Part 4 /
  opinion below) -- recommend shipping a local, reflexive threshold first; treat a budget/neuromodulatory
  controller as a later, separate build gated on observed misallocation under load, not built pre-
  emptively.

---

## Explicit opinion: local reflexive threshold vs. separate controller

**No separate controller is needed for the coarse-to-fine decision itself.** A local, per-item reflexive
threshold -- a confidence/ambiguity signal computed AT the point of decision (the coarse cosine gap
between top-1 and top-2 candidates, or the combinedgate's own arbitration margin) -- is both sufficient
and the better brain-grounded match: familiarity DIRECTLY gates recollection onset (no separate arbiter
sits between them); RHT's implicit-to-explicit switch is driven by feedforward-pass ambiguity or task
demand at the point of perception, not a homunculus deciding for the visual system. This also matches
the substrate's existing discipline of preferring PARAMETER-FREE mechanisms (the combinedgate cell is
explicitly parameter-free biased-competition, not a learned controller) -- a local threshold is the same
philosophy applied one level down, to resolution instead of slot-selection.

A SEPARATE controller earns its cost only when the decision needs information NOT locally available at
the retrieval site: a global compute BUDGET shared across many concurrent queries (a scheduler problem,
not a perception mechanism), a slow-changing THRESHOLD itself that needs retuning based on aggregate
state (task urgency, error-rate history, resource pressure) rather than per-item content, or
cross-subsystem calibration when confidence signals from different pipelines are not directly comparable
and need a shared scale. This maps onto real neuromodulatory systems (locus coeruleus / noradrenergic
gain control, ACC effort-cost monitoring) which RETUNE the local gate's threshold based on aggregate
state, but do not make the per-item decision themselves -- the local reflex still fires the actual
gate, just with a moved criterion.

**Tradeoff:** a purely local, fixed threshold is cheap and immediately buildable but will misallocate
under changing aggregate load (e.g. if many queries simultaneously look "ambiguous," a fixed per-item
threshold has no way to know the drill-down budget is oversubscribed and will happily escalate all of
them). Recommend building the LOCAL reflex first (cheap, testable now, matches parameter-free
discipline) and deferring any budget/neuromodulatory controller until telemetry from the local-only
version demonstrates an actual misallocation problem under realistic concurrent load -- build the cheap
thing, observe whether the expensive thing is actually needed, per [[feedback-drive-all-night-facilitate-
when-idle]] discipline of not pre-building unproven infrastructure.

---

## Citations (verified count)

External (verified via WebSearch, generic terms only; 2 fetched for primary-source confirmation):
1. "Predictive coding is a consequence of energy efficiency in recurrent neural networks," ScienceDirect
   / Patterns, 2022. https://www.sciencedirect.com/science/article/pii/S2666389922002719
2. "Energy optimization induces predictive-coding properties in a multi-compartment spiking neural
   network model," PMC. https://pmc.ncbi.nlm.nih.gov/articles/PMC12180623/
3. Hochstein, S. & Ahissar, M. "View from the Top: Hierarchies and Reverse Hierarchies in the Visual
   System," Neuron 36(5):791-804, 2002. https://www.sciencedirect.com/science/article/pii/S0896627302010917
4. Ahissar, M. & Hochstein, S. "The reverse hierarchy theory of visual perceptual learning," Trends in
   Cognitive Sciences, 2004. https://www.sciencedirect.com/science/article/abs/pii/S1364661304002153
   (verified via PubMed abstract 15450510 and Princeton course-hosted PDF)
5. "Backward masking reveals coarse-to-fine dynamics in human V1," bioRxiv, 2023.
   https://www.biorxiv.org/content/10.1101/2023.02.08.525486.full.pdf
6. "The neural bases of spatial frequency processing during scene perception," Frontiers in Integrative
   Neuroscience / PMC4019851, 2014. https://pmc.ncbi.nlm.nih.gov/articles/PMC4019851/
7. Yonelinas, A.P. "Components of episodic memory: the contribution of recollection and familiarity,"
   2001 (UC Davis hosted PDF, verified). https://hmlpubs.faculty.ucdavis.edu/wp-content/uploads/sites/214/2017/05/2001_Yonelinas_Components.pdf
8. Yonelinas, A.P. "The Nature of Recollection and Familiarity: A Review of 30 Years of Research," 2002,
   plus 2022 update review (UC Davis hosted PDF, verified).
   https://hmlpubs.faculty.ucdavis.edu/wp-content/uploads/sites/214/2022/05/2022_Yonelinas.pdf
9. Lin, Y. et al. "HippoMM: Hippocampal-inspired Multimodal Memory for Long Audiovisual Event
   Understanding," arXiv:2504.10739, 2025 (fetched directly; ML systems paper, not neuroscience-primary,
   cited as a direct computational precedent for query-gated dual-mode retrieval).
   https://arxiv.org/pdf/2504.10739
10. BranchyNet / CascadeBERT / layered-retrieval-cascade / adaptive-computation early-exit literature
    (general ML confirmation of the coarse-first/selective-escalation cost-accuracy pattern; surveyed via
    search, not individually fetched -- lower-confidence citation, general-pattern support only).

Internal (direct on-disk reads, this cycle):
- `d:/AI/hd-instrument/notes/research_drill_encoder_target_metric_coarse_cosine_vs_fine_retrieval_2026-07-04.md`
  (full read)
- `d:/AI/hd-instrument/experiments/exp_encoder_phase_traversal_spread_condense_v1.py` (full read,
  docstring + core loop + arm definitions + pre-reg bands)
- `d:/AI/hd-instrument/experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py`
  (docstring read, lines 1-140)
- `d:/AI/hd-instrument/notes/research_content_gate_brain_grounding_2026-07-08.md` (headline + grounding
  paragraph read)
- `d:/AI/hd-instrument/notes/substrate_capability_map.md` (grep for "hierarchical," hierarchical
  retrieval index / SKAH-M rows read for cross-thread synthesis)
- `d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py` (run at cycle start per role
  contract; no directly-adjacent field candidate for this specific brain-mechanism question, noted and
  not force-fit)

**10 external sources, 6 internal artifacts, directly read/verified this cycle.**

---

## Intuitive summary (plain language)

Brains do not look at everything in full detail all the time -- that would be too expensive. Instead
they get a fast, cheap, blurry sense of the whole picture first (gist), and only spend the expensive,
detailed processing on the parts that are surprising, ambiguous, or important -- vision does this with
spatial frequency (blurry-fast, then sharp-slow), and memory does it too (a fast "does this feel
familiar" signal, and only when that's not enough, a slower "let me actually recall the details" step).
The substrate has a new encoder mechanism in flight right now (phase-traversal) that stores things in a
cheap "spread out" form and has a separate, trained "condense" step that pulls out fine detail -- but as
built today it runs that expensive condense step on EVERYTHING, every time, not just on the few things
that need it. This drill's main finding: we don't need to invent anything new -- we just need to only run
the expensive step on a small shortlist picked by the cheap step first, the same way the brain does it.
That's a cheap, testable change on data the cell will already produce, not a new architecture.

**Why it matters:** if this works, retrieval gets both cheaper AND stays accurate, instead of having to
choose one or the other -- and it's a pattern (cheap-filter-then-expensive-refine) with strong support
both in how real brains work and in how modern AI retrieval systems are built, so it's a low-risk,
high-plausibility next step.
**Near-term decision:** once the phase-traversal smoke lands, re-analyze its OWN output (no new cell) to
check whether a cheap coarse ranking reliably contains the right answer in its top few candidates --
if yes, gate the expensive step to that shortlist; if no, the coarse signal needs to be stronger first.

ASCII-only. No emojis. No em dashes.
