# 5x-DRILL (theory/first-principles): what reasoning does VSA/HDC algebra support, and which limits are REAL walls?

Date: 2026-07-04
Angle: first-principles / capacity-theory angle on the load-bearing question "is the M3 glass-box cortex worth building on the substrate?"
Discipline: deflated-honest (USER no-smoke). Two USER anchors folded in mid-drill:
- **A1 (brain = existence proof):** do not accept a limit without PROOF; classify each as PROVEN-fundamental vs ASSERTED, and static-algebra vs substrate-PLUS-brain-mechanism. If the brain violates the limit -> it is config/method-specific, not fundamental.
- **A2 (high-energy regime):** biological efficiency is the *baseline we want to reach*, NOT the constraint on getting there. A limit that only binds under efficient/single-shot/biological operation is NOT a wall -- throw compute at it (iterate resonators to convergence, dense float, error-correcting redundancy, learned attractor cleanup, grow D). Classify each limit: **(a) survives UNLIMITED compute = true wall** vs **(b) binds only under cheap compute = surmountable cost.**

Grounding: mandatory substrate concept-query run first (cosine 0.33 top hit = our own `resonator_factorization_v1`; prior arc work exists -- see "Prior arc overlap" below, NOT a rediscovery, this is a synthesis memo). Anchored to our own measured cell + Plate/Frady/Kent/Eliasmith literature.

---

## Part 1 -- What reasoning the STATIC bind/bundle/permute/cleanup algebra genuinely supports

The primitive set: bind (multiply-like, invertible, dissimilar output) | bundle (add+normalize, similar output) | permute (order/quote) | similarity (cosine readout) | cleanup (nearest-neighbor to a codebook -> restores a noisy vector to a clean stored atom).

Five reasoning operations these support, with honest depth rating:

1. **Analogical mapping via bind/unbind (Kanerva "dollar of Mexico", Gayler, Rachkovskij).** Build records USA = CAP(x)WDC + MON(x)DOL + ...; MEX = CAP(x)MXC + MON(x)PES + ...; the holistic transform M = USA (x) MEX* maps a filler across frames: M (x) DOL ~ PES -- *without* knowing which role "dollar" plays. GENUINELY real, GENUINELY non-trivial (a single vector encodes a whole relational substitution). Depth rating: **strong for first-order / surface analogy; shallow for deep structural analogy** (mapping relations-of-relations, Gentner structure-mapping) in one shot.

2. **Cleanup-chained inference (pointer-chase).** unbind -> cleanup -> unbind... Transitive/relational lookup: each unbind injects crosstalk; cleanup restores the clean atom IF SNR clears the nearest-neighbor margin. Real. This is symbolic pointer-following implemented in vectors.

3. **Resonator-network factorization (Frady/Kent/Sommer/Olshausen 2020).** Given a product c = x(x)y(x)z with factors drawn from known codebooks, recover the factors by iterative in-superposition relaxation -- explores a combinatorial space |X|.|Y|.|Z| with ~linear resources instead of enumerating. This is the closest the algebra gets to genuine *search / constraint satisfaction*. Real and powerful. (Note: resonators are ALREADY a dynamical/recurrent mechanism, not "static" -- flag for Part 3.)

4. **Probabilistic reasoning in superposition.** A bundle = superposition of hypotheses; similarity readout approximates a marginal count/likelihood; evidence combines via bind (product) and bundle (sum) -- Bayesian-ish. Real but coarse (few bits of precision per single readout).

5. **Systematic variable binding (Fodor-Pylyshyn / Jackendoff; Gayler 2003).** Binding gives genuine role-filler variable binding -- loves(John,Mary) != loves(Mary,John), and one learned transform generalizes across fillers. This is the *representational* answer to the systematicity challenge (VSA = the randomized/compressed form of Smolensky tensor products). This is the load-bearing positive: **VSA solves compositional-systematic representation.** Real, important.

Static-algebra-alone verdict: **MEDIOCRE as an autonomous reasoner** -- real primitives but bounded and shallow (surface analogy + shallow chains + single-shot factorization + coarse probability). The algebra is a *compositional memory + a few transforms + associative cleanup*, not a processor. The actual control flow (what to bind/unbind, multi-step planning, alignment search) is NOT in the algebra. **BUT** (Part 3) this is precisely the "add-the-controller" gap that M3 exists to fill, and it is a proven-fillable gap.

---

## Part 2 -- The claimed hard limits, classified PROVEN vs ASSERTED (Anchor A1)

| # | Claimed limit | PROVEN or ASSERTED? | Does brain violate it? |
|---|---|---|---|
| L1 | Flat superposition crossover: only K_max ~ D/eps^2 items bundle before cleanup fails | **PROVEN** (Plate HRR bounds; Frady-Kleyko-Sommer 2018 SNR theory; crosstalk variance ~ N(0, K/D) exactly computable; Thomas-Dasgupta-Rosing 2021 capacity theory grounded in Johnson-Lindenstrauss) -- **for the single-shot flat readout only** | YES -- human WM ~4-7 flat chunks, yet reasons over vast structures via hierarchy + episodic recall |
| L2 | Inference-chain depth bounded by SNR budget | **PROVEN per-hop** (crosstalk O(sqrt(K/D)) per unbind); **ASSERTED as cumulative** -- FALSE if you cleanup each hop | YES -- brain does arbitrarily long serial reasoning via per-step attractor cleanup |
| L3 | Resonator factorization cliff (spurious fixed points / limit cycles beyond operational capacity) | **PROVEN** (Kent et al. measured the operational-capacity curve; phase-transition-like cliff; near it, convergence time diverges = critical slowing down) | Partial -- cortical relaxation with noise/adaptation escapes minima; hierarchy decomposes big problems |
| L4 | Probabilistic readout precision coarse (~1/sqrt(D)) | **PROVEN + information-theoretically fundamental FOR A SINGLE D-vector at one instant** | YES -- brain accumulates over TIME (drift-diffusion evidence accumulation), variance ~1/sqrt(T) |
| L5 | Deep structural analogy degrades | **ASSERTED / empirical** (crosstalk grows with structural depth) | YES -- brain does structural analogy via recurrent alignment (LISA/DORA relaxation) |
| L6 | "The algebra doesn't do control flow / can't reason autonomously" | **TRUE but not a substrate limit** -- VSA + cleanup memory + a sequencer is **Turing-universal** (proven; pointer-machine construction). Reasoning then lives in the controller. | N/A -- brain IS substrate + cortical/BG control; the controller is the point, not a missing wall |
| L7 | Instantaneous D-bit information ceiling (one D-vector carries O(D) bits) | **PROVEN, information-theoretically fundamental** (Shannon; JL) -- **for one vector at one instant** | YES functionally -- brain computes over D.T (time) and grows effective D via sparse expansion (dentate gyrus) |

Reading of the table: **every capacity/depth limit is PROVEN only for the single-shot / flat / fixed-small-D / static-readout operation, and the brain routinely violates all of them** by NOT operating that way -- it uses recurrence, per-step cleanup, hierarchical chunking, sparse expansion, and temporal accumulation. Per Anchor A1, that makes L1-L5 **config/method-specific, not fundamental.** L6 is not a wall (it is the controller TODO = M3). L7 is fundamental *for one instant* but functionally dissolved by time+hierarchy.

---

## Part 3 -- Which limits survive UNLIMITED COMPUTE (Anchor A2): true walls vs compute-cost

The high-energy regime lets us spend: grow D (linear capacity), iterate resonators/cleanup to convergence, error-correcting redundancy (cleanup error decays EXPONENTIALLY in D per concentration/JL), dense-float intermediate reps, learned attractor dynamics (better basins), hierarchical/sequential decomposition (D.T). Re-classify:

**(a) TRUE WALLS that survive unlimited compute:**
- **NONE that are VSA-specific.** Under unlimited compute VSA+cleanup+sequencer is Turing-universal, so its reasoning ceiling EQUALS the universal computability ceiling.
- The only surviving walls are the **universal** ones that bind every computer AND the brain equally:
  - **Worst-case search hardness (P vs NP).** If a reasoning problem's underlying CSP is NP-hard, no substrate solves it in worst-case polynomial resources. Resonators give an *average-case* superposition-parallel speedup, not a worst-case escape. But this is not a VSA defect -- it walls the brain too, and useful reasoning lives in the tractable average/structured case.
  - **Undecidability (halting).** Any Turing-universal reasoner inherits it. Universal, not VSA-specific.
  - **Shannon storage lower bound.** To reliably hold N bits you must provision Omega(N) capacity (dimension x precision x redundancy). Trivially satisfiable by spending storage -- a scaling law, not a barrier.

**(b) COMPUTE-COST limits (NOT walls) -- bought off by spending energy/iterations:**
- L1 flat-K crossover -> grow D (capacity ~D) and/or hierarchical chunking. Cost linear.
- L2 chain depth -> per-hop cleanup makes it unbounded; cost linear in depth (each cleanup = one NN search).
- L3 factorization cliff -> more resonator iterations + restarts + annealing/noise + learned cleanup + hierarchical factoring. **Direct evidence in our own cell:** `data/exp_resonator_factorization_v1/metrics.json` -- K2 success 1.00, K3 success 0.733 at N=2048, M=30 in a **single-shot smoke (run_mode=smoke, n_seeds=1, 0.31s)**. The K3 dip is the textbook cheap-compute signature: one run at fixed D near the operational boundary. Lift it by growing D, more iterations, or better init. This is a cost curve, not a wall.
- L4 coarse precision -> temporal accumulation / ensemble averaging (variance ~1/sqrt(T)); dense float. Cost = more samples/dimension.
- L5 deep structural analogy -> recurrent alignment run to convergence (resonator-style); cost = iterations.
- L7 instantaneous D-bit ceiling -> grow D and/or compute over time (D.T). Cost = dimension x steps.

**The one honest cost-texture to flag (still not a wall):** near the resonator/attractor operational-capacity boundary, convergence time DIVERGES (critical slowing down -- this is measured/proven, L3). So "surmountable by compute" has a NONLINEAR cost near boundaries. The cheap discipline is to provision D so you operate BELOW the cliff -- a provisioning rule, not a reasoning limit.

---

## Part 4 -- Existence proof (settles toy-vs-real empirically)

**Eliasmith et al., Spaun (Science 2012), Semantic Pointer Architecture** = a working brain-scale VSA/HRR substrate (bind/bundle/cleanup) + Neural Engineering Framework recurrent control, that performs genuine multi-step reasoning: inductive rule-induction on **Raven's Progressive Matrices** (fluid intelligence), serial working memory, reinforcement bandit learning, and question answering -- all from the substrate primitives + a controller. This is the demonstrated existence proof that **substrate + mechanism reasons**, not toys. It empirically settles the load-bearing question in favor of *real, bounded* reasoning, and it validates the M3 thesis (substrate + a control/gating cortex = reasoner).

Contrast with Part 1's static-alone MEDIOCRE: the delta between mediocre-static and real-reasoning-Spaun IS the controller + recurrent cleanup dynamics -- exactly what M3 proposes to add.

---

## Part 5 -- The glass-box dividend (why THIS substrate for a cortex, vs dense NN)

Every binding is role(x)filler; you can unbind by role and cleanup to a discrete named atom -> the reasoning trace is **inspectable/auditable at every hop**. Dense-NN hidden states cannot offer this: their superposition has no canonical unbind + codebook cleanup, so intermediate reasoning is not namable. The substrate's proven-Turing-universality means it loses NO reasoning power for the glass-box property -- you get auditable reasoning at (compute) cost, not at a capability discount. This is the genuine strategic reason the M3 cortex is worth building on THIS substrate rather than bolting a controller onto opaque activations.

---

## Prior arc overlap (concept-query honesty)

Concept-query top hits confirm this is SYNTHESIS over existing arc work, not rediscovery:
- `data/exp_resonator_factorization_v1/metrics.json` (cosine 0.34) -- our measured K2/K3 cell (used above).
- `notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md` -- resonator capacity scaling.
- `notes/research_drill_slipnet_13_untested_paths_2x_2026-06-11.md` -- "Family B: iterative factorization / resonator-style cleanup."
- `notes/research_drill_substrate_code_synthesis_higher_ceiling_2x_2026-06-11.md::chunk003` -- resonator CFG decoder (|V|^depth -> polynomial via superposition convergence).
- Plus prior handoffs: `exp_dev_handoff_research_d_eff_capacity_ceiling_theory_2026-06-07.md`, `..._drill_hrr_capacity_vs_depth_2026-06-23.md`, `..._multi_iter_cleanup_brain_analog_2026-06-23.md`, `..._gap2_capacity_side_analysis_2026-06-26.md`.
This memo's NEW contribution: the three-way classification (proven-fundamental / brain-surmountable / compute-cost) applied uniformly, and the conclusion that NO VSA-specific wall survives unlimited compute.

---

## VERDICT (deflated-honest)

- **Static algebra as autonomous reasoner:** MEDIOCRE (real but bounded/shallow -- surface analogy + shallow chains + single-shot factorization + coarse probability).
- **Substrate + brain-mechanisms + high-energy compute (= the M3 proposition):** **GOOD / worth building.** No proven-fundamental VSA-specific wall stands in the way; every capacity/depth limit is compute-cost we can pay down (grow D, iterate to convergence, error-correcting redundancy, learned cleanup, hierarchy, temporal accumulation). The only surviving walls are UNIVERSAL (P!=NP worst-case, undecidability, Shannon) and bind the brain equally. Spaun is the existence proof that the architecture reasons.
- **Residual risk is ENGINEERING, not theory:** building the glass-box controller + provisioning D below the convergence cliff. That is a cost/provisioning problem, not a capability wall.
- **Deflation to keep:** reasoning stays RESOURCE-METERED (every hop spends SNR; every problem has a provisioning-D and, near boundaries, a nonlinear convergence cost). Scope = brain-like BOUNDED compositional reasoning, not free unbounded symbolic AI. But bounded != toy: the brain (best-in-class) is also bounded.
</content>
</invoke>
