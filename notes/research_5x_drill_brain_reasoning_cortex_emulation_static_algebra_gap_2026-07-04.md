# RESEARCH 5x DRILL (brain-grounding): how the brain reasons over stored memory, what the M3 cortex should emulate, and whether static VSA algebra supports it

**Date:** 2026-07-04
**Role:** research (Director), 5x-DEEPER brain-grounding angle
**Load-bearing question:** is the M3 glass-box cortex/reasoning-layer direction worth committing to? (encoder is mediocre/teacher-dependent; cortex is the claimed prize + only place real novelty could live)
**Deflation:** lit-scan calibration -0.15..-0.25; novel-synthesis P cap 0.50. Brain = best-in-class reference (existence proof), but MECHANISM-analog is NOT task-analog.
**Prior-arc consulted (concept-query-before-dispatch, canon-first):**
- `notes/research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md` — SR closure + TEM structural-sensory factorization + theta-gamma compound (r2_successor_TEM cell dispatched)
- `notes/research_drill_brain_multihop_M2_pfc_scratchpad_separate_W_3x_2026-06-27.md` — PFC scratchpad / register-file separation
- `notes/research_drill_cross_domain_revival_3x_2026-06-10.md::chunk011` — hippocampal schema-based generalization (Tse 2007, Eichenbaum 2017)
- `notes/exp_dev_to_skunkworks_..._within_domain_analogy_FORM_A_precheck_CLEAR_comp24_2026-06-16.md` — within-domain A:B::C:D **HARD_PASS >=0.85 substrate-internal** (bind+cleanup, no learned layer); cross-domain RETRACTED
- MEMORY: M3 cortex-above-substrate USER-LOCKED 2026-06-28; cortex-injects-stochastic-noise USER 2026-06-30
**Prior arc work on this concept: SUBSTANTIAL (multi-hop reasoning primitives drilled). NEW here: zoom out from narrow multi-hop-QA task to the CORTEX-AS-A-LAYER architecture + the honest static-algebra gap.**

---

## HEADLINE (intuitive first)

The brain does not reason "inside" its memory store. It reasons with a **separate recurrent controller (PFC + hippocampal dialogue) operating OVER a factorized relational memory**, and the two halves have genuinely different physics. The memory half — entorhinal-hippocampal relational codes — is a **factorized structural x sensory code** (grid/relation code `g` bound to content `x`), and *that half is essentially a VSA*. Whittington-Behrens' Tolman-Eichenbaum Machine conjunctive code `p = g (x) x` IS the substrate's `bind(R, E)`; TEM-as-VSA is now an explicit connection in the literature. So the substrate is a genuinely good realization of the brain's **memory** half — and we have the receipt: within-domain analogy `A:B::C:D` already HARD_PASSes >=0.85 substrate-internally via bind+cleanup alone.

The **reasoning** half is where the brain's real machinery lives, and it is NOT in the algebra. It is: (1) **recurrent settling** — the brain recombines factorized codes by letting an attractor network relax to a coherent joint interpretation (analogy mapping, constraint satisfaction, factoring a multi-bound vector); (2) **learned structural codes / schemas** — grid cells and cortical schemas are *learned* to be reusable structural bases that generalize one-shot to never-seen relations (transitive inference "for free"); (3) **offline replay** — sharp-wave-ripple replay does inference and consolidation while "offline," including replaying trajectories never experienced; (4) **stochastic sampling** — cortical/hippocampal reasoning is noisy on purpose (sampling-based inference; trial-to-trial variability is the computation, not a defect).

The honest map: our **static VSA algebra supplies the memory-half operations (bind/unbind/bundle/cleanup) but not the reasoning-half dynamics**. Of the four reasoning ingredients, **recurrent settling is VSA-native and merely not-yet-built** (resonator networks — Frady/Kent/Kanerva/Sommer 2020 — are a recurrent VSA attractor loop that factors distributed representations; this is the existence proof that "static algebra can't do recurrent inference" is FALSE); **stochastic sampling is USER-locked as a cortex-boundary noise-injection channel** (brain-grounded, buildable); **PFC-scratchpad control has been drilled**; but **learned structural codes + learned schema attractors are the genuine gap** — our R codebook is *random*, our cleanup basins are *stored items*, and we have Hebbian-accumulation, not gradient representation-learning. The brain's generalization comes from *learning* the structural code; we would have to either hand-design it (works for within-domain, empirically confirmed) or add a learning loop the substrate does not have (needed for cross-domain, which is exactly the piece that stays RETRACTED).

**Bottom line: commit to the cortex direction (it is empirically forced, brain-matched, and USER-accepted), but with clear eyes that the cortex's real novelty and its hardest gap are the SAME object — learned/stochastic/recurrent reasoning dynamics that generalize. The algebra gives you the memory for free; it does not give you the reasoning, and the reasoning is the whole point.**

---

## L1 - HOW THE BRAIN ACTUALLY REASONS OVER STORED MEMORY (four mechanisms, deflated)

### 1.1 Systems consolidation + schemas: inference-by-assimilation (hippocampal-neocortical dialogue)
- **CLS (McClelland-McNaughton-O'Reilly 1995):** hippocampus = fast, sparse, pattern-separated one-shot binding; neocortex = slow interleaved learning of *overlapping distributed schemas*. Two systems by necessity: fast learning in one net would catastrophically overwrite; the split is the solution.
- **Schemas (Tse et al. 2007, Science):** once a cortical schema exists, new *consistent* facts consolidate in ~48h instead of weeks. A schema is an **active assimilation template** — new items bind INTO it and the binding fills in unobserved relations. That fill-in IS inference.
- **Replay-based inference (Foster-Wilson 2006; Gupta 2010; Olafsdottir 2015; Liu-Behrens-Dolan 2019 "human replay"):** hippocampal sharp-wave-ripple replay reinstates trajectories offline — INCLUDING trajectories never physically experienced (shortcuts, novel recombinations, reverse sweeps). This is model-based inference / planning via *generative* replay, and it does credit assignment without backprop.
- **Cortex-relevance:** the cortex's "consolidation" is not a storage optimization — it is where **generalization is manufactured**. Schema = the learned attractor that is NOT any single episode.

### 1.2 Relational / analogical reasoning: factorized structural codes (the TEM result)
- **Relational memory theory (Eichenbaum, Cohen):** hippocampus binds *arbitrary* relations; the "cognitive map" measures **relational distance**, not perceptual similarity. Two episodes are "near" if they share relational structure regardless of surface features.
- **Grid cells as structural code (Stachenfeld 2017; Constantinescu-O'Reilly-Behrens 2016; Bellmund 2018):** medial-entorhinal grid code is a **reusable basis** that generalizes across environments with the same structure — and grid-like codes appear over *abstract/conceptual* spaces, not just physical space. The brain reasons over concept spaces by mapping them onto a reusable structural code.
- **TEM (Whittington-Behrens 2020, Cell):** factorize **structural `g`** (grid/MEC, learned transition rules) x **sensory `x`** (content) -> conjunctive `p = g (x) x` (CA3/CA1). Result: **immediate one-shot generalization to unseen transitive-inference / relational queries** ("Bob's niece" without ever seeing it) via structural reuse. Whittington's follow-on explicitly relates TEM to VSA/HRR — **the conjunctive code is a VSA bind.**
- **Analogy machinery (Gentner structure-mapping; Hummel-Holyoak LISA):** analogy = mapping relational structure across domains via role-filler binding settled by mutual excitation/inhibition. Frontopolar/rostrolateral PFC (Bunge, Christoff) does the relational integration.
- **Cortex-relevance:** this is the mechanism most *aligned* with VSA. Factorization = bind/unbind. Structural reuse = applying an R-chain to new E-content. The substrate's within-domain-analogy HARD_PASS is the substrate doing exactly this.

### 1.3 One-shot / transitive inference: encode-time integration vs retrieval-time recombination
- **Two routes debated (both real):** (a) **integrative encoding** (Shohamy-Wagner 2008) — overlapping representations merge offline so A>C is *pre-computed*; (b) **flexible retrieval** — recombine A>B and B>C *at query time*. The brain uses both; replay is the offline route.
- **Cortex-relevance:** the substrate's SR-closure `M = sum gamma^k W^k` (drilled) is the algebraic analogue of route (a) — pre-compute the K-step transitive closure once. The PFC-scratchpad multi-hop chain is route (b). Both are cortex mechanisms already on the board.

### 1.4 The dynamics are recurrent and stochastic (the load-bearing "physics" difference)
- **Recurrent settling:** cortical/hippocampal reasoning is a *dynamical relaxation* — the network settles into the joint interpretation that best satisfies the constraints (Hopfield-style, but over a STRUCTURED multi-slot state, not a single vector). Analogy, factoring "which g and which x produced this p", disambiguation — all are settle-to-coherence.
- **Stochastic sampling (Buesing 2011; Orban-Berkes-Fiser-Lengyel 2016; Hoyer-Hyvarinen 2003):** neural variability is not noise-to-be-removed — the brain represents *probability distributions by sampling*. Trial-to-trial variability = draws from the posterior. Reasoning is Monte-Carlo, not deterministic argmax.
- **Cortex-relevance:** this is precisely the USER-locked cortex design constraint (2026-06-30): substrate is structurally deterministic (cleanup is identity on clean input), so the **cortex must inject stochasticity at the boundary** and IS "the stochastic compensation channel." The brain grounds this exactly — sampling-based inference needs the noise.

---

## L2 - CONCRETE M3 CORTEX DESIGN (map each brain mechanism to a module over the substrate)

The USER architecture is already fixed: cortex is a **separate organ that calls substrate primitives** (2026-06-28, brain analog accepted verbatim: "hippocampus+cortex memory vs basal ganglia+PFC planning — different computations, different structures"). This drill fills in WHAT the organ should compute.

| Brain mechanism | Cortex module | Substrate primitive it calls | Build status |
|---|---|---|---|
| Factorized structural x sensory code (TEM `p=g(x)x`) | **Relational memory format** | `bind(R,E)` / `unbind` — IS the conjunctive code | **HAVE IT** (within-domain analogy HARD_PASS) |
| Recurrent settle to joint interpretation (analogy, factoring, constraint-sat) | **Resonator loop** (cortex recurrent core) | iterative `cleanup` over a multi-factor state; VSA resonator network dynamics | **VSA-native, NOT built** (engineerable) |
| PFC persistent-activity scratchpad (clean intermediates, separate physics) | **Scratchpad controller** (K<=8 slots, index-addressed, exact write) | separate `W_pfc`; reads main-W by content, holds by index | **DRILLED** (pfc_scratchpad cell) |
| Transitive closure / schema (route-a integrative encoding) | **SR-closure precompute** `M=sum gamma^k W^k` | matmul over substrate W | **DRILLED** (r2_successor_TEM dispatched) |
| Sampling-based / stochastic inference | **Boundary noise-injection** (Gaussian at cortex-substrate interface) | inject before cleanup so attractor hops sample the posterior | **USER-LOCKED design; not built** |
| Offline replay / consolidation (generalization manufacture) | **Replay-consolidate** (SWR analogue: re-bundle exemplars -> schema; reverse-sweep credit) | `bundle` + `W.T` backward pass | design sketch only |
| Termination / goal decomposition (PFC-BG planning) | **Planner** (Phase-1 LLM router -> Phase-2 learned) | sequences all of the above | USER Phase-1 LLM; substrate-native CLOSED (5-cell HARD_FAIL) |

**The cortex, assembled:** a recurrent controller that (i) holds a query-frame in a PFC-scratchpad, (ii) probes the substrate's factorized relational memory, (iii) **settles a resonator loop with injected boundary noise** to recombine/factor the retrieved codes into an inferred answer, (iv) replays to consolidate the inference into a reusable schema, (v) is sequenced by a planner. The glass-box property: **every bound role, every cleanup step, every settle iteration, every sample is inspectable** — the reasoning trace is a sequence of readable hypervector operations, not opaque activations. THAT is the defensible novelty axis (see L4).

---

## L3 - THE HONEST GAP: does static VSA algebra support the brain's reasoning mechanism?

**Verdict: PARTIAL. The memory-half maps excellently; the reasoning-half splits into an engineerable gap and a fundamental gap.**

### 3.1 What the static algebra HAS (maps well)
- **Factorized relational code** = `bind`/`unbind`. This is the single strongest brain->substrate mapping in the whole project — TEM's conjunctive code is literally a VSA bind, and it is published as such. GOOD.
- **Single-object attractor / pattern completion** = `cleanup` (codebook-NN / Modern-Hopfield). The brain's hippocampal pattern completion has a clean VSA analogue. GOOD.
- **Prototype/schema-by-bundling** = `bundle`. A bundle of exemplars IS a category centroid whose cleanup basin captures the prototype. This is a *first-order* schema. PARTIAL (see 3.3).
- **Within-domain analogy** = bind+unbind+cleanup, **empirically HARD_PASS >=0.85, no learned layer.** The substrate already does structural-reuse analogy. GOOD (receipt on disk).

### 3.2 The engineerable gap: recurrent settling ("static algebra lacks recurrent processing" is FALSE)
- The premise that our algebra is "static / feed-forward, no recurrent dynamics" is **half-wrong**. Iterative cleanup IS a recurrent attractor step (each pass is a Hopfield update). More decisively, **resonator networks (Frady-Kent-Kanerva-Sommer 2020, "Resonator Networks for factoring distributed representations")** are a fully recurrent VSA dynamics that solves the multi-factor unbinding / constraint-satisfaction problem by settling — the exact "recombine factorized codes by relaxation" the brain does for analogy/inference.
- So recurrent inference is **VSA-native and simply not yet in our substrate.** This is a *not-built* gap, not a *fundamental* gap. Cost: a resonator loop over the existing bind/unbind/cleanup + boundary noise. MEDIOCRE-leaning-GOOD.
- Deflation: resonator networks solve *factoring*, not general reasoning; do not oversell them as "the reasoning engine." They are the existence proof + a concrete recurrent core, not a universal solver.

### 3.3 The fundamental gap: LEARNED structural codes + LEARNED schema attractors
- **This is the real one.** TEM's one-shot generalization comes from **learning `g` by gradient descent through many environments** so that `g` becomes a structural basis that transfers. Our **R codebook is random hypervectors** — they compose algebraically but do NOT encode transition/ordinal/hierarchical structure unless we *hand-build* it (e.g., fractional-power encoding for ordinal -> transitive inference works algebraically; but that is design, not learning).
- **Our attractor basins are stored items** (or bundles of them). The brain's schema attractor is a *learned nonlinear manifold* that is NOT any stored episode. Bundling gives first-order prototypes; it does NOT give learned higher-order relational schemas (transitivity, hierarchy, cross-domain structure) as attractors.
- **Our learning is Hebbian outer-product accumulation, not gradient representation-learning.** The substrate has no mechanism to *learn a structural code that generalizes to unseen relations across domains.* This is exactly why **within-domain analogy PASSes (reuse of existing hand/random codes) but cross-domain analogy stays RETRACTED (P9 confound)** — cross-domain requires *learning the shared abstract structure*, which is the missing capability.
- **Honest framing of the gap:** "learned attractor dynamics" is a genuine gap vs our no-gradient / Hebbian-only constraint. BUT it is not a wall — it is the USER's own **Phase-2 "learned planner module"** on the roadmap. The cortex is *where* the learned dynamics would go; the substrate stays the deterministic capacity-bounded memory. The gap is real, located, and roadmapped — not a surprise.

### 3.4 Where the flagged premise lands
"The brain's reasoning may need learned attractor dynamics / recurrent processing our static algebra lacks."
- **Recurrent processing:** NOT a gap (resonator networks; iterative cleanup). Engineerable.
- **Learned attractor dynamics:** a REAL gap (random codes + Hebbian-only + stored-item basins vs learned structural codes + learned schema manifolds). This is the piece that keeps cross-domain generalization out of reach and is the honest ceiling on the cortex's novelty-as-capability.

---

## L4 - DEFLATED VERDICT + COMMIT RECOMMENDATION

### Good / mediocre / bad on brain-grounding the cortex
- **Cortex DIRECTION (separate reasoning organ over factorized relational memory): GOOD.** Empirically forced (5-cell / 4-mechanism-class planning closure + r1b multi-hop HARD_FAIL), brain-matched (hippocampal/entorhinal memory vs PFC/BG control is textbook division of labor), USER-accepted verbatim, and the memory-half is a genuinely excellent VSA fit (TEM-as-VSA; within-domain analogy HARD_PASS on disk). This is the highest-confidence architectural claim in the project.
- **Cortex MECHANISM (what it computes): MEDIOCRE-to-GOOD.** Concrete, mostly-mappable design exists (resonator recurrent core + PFC-scratchpad + SR-closure + boundary-noise sampling + replay-consolidate). Several pieces are drilled or VSA-native. But two honest discounts: (i) most of the *tractable* pieces are KNOWN VSA techniques (bind-analogy, resonator factoring, HRR composition) - competent, not novel; (ii) the *novel* piece (learned schema attractors enabling cross-domain generalization) is the hardest and least-supported by static algebra.
- **The novelty honesty:** the cortex's real novelty is NOT a reasoning-capability breakthrough (VSA reasoning engines exist; capability will likely be competitive-not-superior). It is **glass-box observability of brain-grounded relational reasoning** — the reasoning trace is a readable sequence of hypervector ops. Given the mediocre encoder, *this observability thesis is the defensible prize*, and it holds even if raw capability only matches neural approaches. That aligns with the USER-locked project goal (glass-box LLM, substrate-native) rather than a raw-benchmark claim.

### Is the M3 cortex direction worth committing to? YES — with a scoped novelty claim.
- Commit, because: it is the brain's own architecture, it is empirically the only place the failed-in-substrate functions (planning, multi-hop control, cross-domain) can live, and the substrate genuinely supplies the memory-half so the cortex is additive not redundant.
- Commit to the **glass-box-observability novelty**, NOT a capability-superiority novelty. The raw-reasoning-capability ceiling is set by the learned-schema gap, which our no-gradient constraint makes hard.
- Sequence: the tractable/VSA-native pieces first (resonator recurrent core + boundary noise = the recurrent-settling cortex primitive, directly addresses the "static-algebra-lacks-dynamics" objection and reuses drilled scratchpad/SR work); defer the learned-schema piece to Phase-2 with explicit acknowledgement that it is the hard gap and the true frontier.

### Cheapest decisive next probe (falsifiable, discriminator-must-survive-scale)
**Cell `cortex_resonator_boundary_noise_v1`:** a minimal cortex recurrent core = resonator-network settle loop over the substrate's existing `bind/unbind/cleanup`, with Gaussian boundary-noise injection (the USER-locked stochastic channel), tested on a **multi-factor disambiguation / within-vs-cross-domain analogy** task where the answer requires recombining >=2 factored codes.
- **Arms:** (A) FEED_FORWARD_UNBIND (no recurrence, current substrate) = anchor; (B) RESONATOR_SETTLE (recurrent, deterministic); (C) RESONATOR_SETTLE + BOUNDARY_NOISE (the sampling cortex).
- **HARD_PASS:** C recovers multi-factor answers at >=1.3x arm-A accuracy AND the settle trace is fully inspectable (every iteration's per-factor cleanup logged) AND boundary-noise arm C beats deterministic arm B on the *ambiguous* subset (proves sampling helps where argmax is degenerate — the brain's claim).
- **HARD_FAIL:** resonator settle does not beat feed-forward unbind (recurrence adds nothing at substrate scale) OR noise only hurts (sampling story wrong for this regime).
- **Discriminator-at-smoke:** at full-N, arm C must beat arm A by >=0.05 on a 2-factor ambiguous smoke set or abort (per USER SMOKE=FULL branches rule).
- **P(HARD_PASS): 0.40** (deflated: resonator/VSA is well-validated for factoring -> directionality high; magnitude + the noise-helps-on-ambiguous claim novel on our bipolar substrate -> capped). This probe is decisive on whether "recurrent settling" is a real cortex primitive on OUR substrate before investing in the learned-schema hard part.

---

## CALIBRATION / DEFLATION NOTES
- Novel-synthesis cap 0.50 applied to the resonator-cortex probe (0.40).
- Mechanism-analog is NOT task-analog: TEM/grid/schema are the brain's *mechanisms*; our task is synthetic relational recall, not the brain's task. Grounding-strength claims are about mechanism-fit, deflated accordingly.
- The single most load-bearing honest correction to the framing: **"static algebra lacks recurrent processing" is FALSE (resonator networks are VSA-native recurrent inference); the true gap is "lacks LEARNED structural codes / schema attractors."** Do not let the recurrent-dynamics red herring hide the real learned-generalization gap.
- Cross-domain analogy stays RETRACTED (P9 confound) — consistent with the learned-schema gap being the ceiling; do not reopen without a genuine learning mechanism.
- Substrate KNOWS NOTHING (no general-knowledge ingest): all "reasoning" here is over synthetic relational codes, not language/world-knowledge. The cortex reasons over the substrate's structure, not over facts it does not have.

-- Research (Director), 5x brain-grounding drill; deflated-honest; canon-first (4 prior-arc memos + 2 USER-locked cortex constraints consulted)
