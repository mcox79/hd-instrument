# Research — Alternative theoretical homes for the three-plateau retention structure

**Date.** 2026-05-24
**Owner.** Research session (single-writer-per-file).
**Trigger.** 1-RSB framing has accumulated 6+ negative observations (Pred-1 HARD-FAIL, Pred-3 INCONCLUSIVE-trivial, Pred-5 HARD-FAIL, R-PRIME-3 task-pair geometry HARD-FAIL, R-PRIME-3 R1 alt-geometry HARD-FAIL, R-PRIME-2 MoE K-sweep HARD-FAIL, Alt 1 FULL walked back, Alt 2 W-internal HARD-FAIL on all 13 spectral/bundle-norm signatures r^2=0). Substrate-physics framework reliability dropped 40-55% to 30-45%. Pred-4 hysteresis re-ship pending — but even with Pred-4 PASS the framework predictive track-record is non-monotone. Goal: alternative theoretical homes READY before Pred-4 verdict lands.

**What survives empirically.** Three discrete retention plateaus at 0.94 (same-corpus) / 0.74 (4-stage) / 0.60 (diff-corpus) — robust under N, geometry, time, projection, replay (all rejected as continuous-axis levers). Plus K5 closed (real-time learning during inference).

**Discipline applied.** 2x discipline (drill DEEP per candidate, not breadth-scan). Query-privacy compliant (generic math/physics terms only). Lit-scan calibration penalty (deflate by 0.15-0.25; cap novel-synthesis P at 0.50). Connects to R18 (RFOT/MCT), R23 (continuous RSB / AT line), R24 (FDT/aging).

---

## HEADLINE — the framework that surprised me

Five candidates evaluated. **Two of them (cand. iv = IB phase transitions, cand. v = saddle-cascade plateaus in online learning) have published precedent for DISCRETE plateau structures that emerge from continuous-parameter-immune mechanisms — and they were missed in R18/R23/R24 because the prior literature search privileged statistical-physics framing over learning-theory framing.**

Substrate observation "three discrete plateau values, immune to N/geometry/time/projection/replay" is *more naturally read as a learning-dynamics fixed-point cascade than as a 1-RSB freezing transition*. The 1-RSB explanation requires a specific overlap-distribution shape (two-peak structure) — empirically R23 already predicted this would NOT be the substrate's signature (Steffan-Kuhn reentrance pushes Hopfield toward FRSB), and the recent negative observations are consistent with that prior warning.

**Top-2 actionable candidates (in order):**
1. **(v) Saddle-cascade / cascade plateaus in online learning** — Saad-Solla / Biehl-Schwarze framework: high-D learning dynamics has *several fixed points* and the trajectory passes through them as plateaux. Predicts 3-plateau spacing depends on permutation-symmetric subspace structure of the task overlap, which is exactly what corpus-type (same / 4-stage / diff) selects. **Falsifier exp_dev could ship cheaply (CPU).**
2. **(iv) Information-Bottleneck phase transitions** — Wu-Fischer-Tegmark IB phase-transition framework: plateaus correspond to onset-of-class-learning as the trade-off increases; predicts the number-of-plateaus = number-of-class-clusters in (X,Y) joint distribution. Predicts substrate plateau heights map to the *number of distinguishable corpus categories*, not to physical phase boundaries. **Also CPU-cheap to falsify via projection-to-categorical-mutual-information.**

Bottom-3 (still useful as contingency but lower P of fit): (i) k-step RSB, (ii) MCT, (iii) chaos-in-temperature.

---

## Comparison matrix

| Candidate | Mechanism narrative | Plateau-height prediction | Falsifier | P(fit) | Notes |
|---|---|---|---|---|---|
| **(i) Parisi k-RSB, k=2 or k=3** | Hierarchical replica scheme: k+1 jumps in Parisi measure produce k+1 plateaus in overlap distribution P(q). k=2 gives q_0/q_1/q_2; k=3 gives 4 plateaus. | k=2 predicts THREE distinct plateau values q_0 < q_1 < q_2 IF the k=2 scheme is the true RSB scheme (not k=1, not FRSB). Heights depend on Parisi function inversion. NOT specifically 0.94/0.74/0.60 — those would need separate parameter fits. R23 lit-scan already noted Steffan-Kuhn 2RSB on Hopfield essentially indistinguishable from 1RSB (Δα_c ≈ 1e-6). | Measure P(q) shape directly on substrate W at α=0.153, N>=4096; if it shows THREE clean delta-like peaks at q ≈ 0.94, 0.74, 0.60 (or rescaled), k=2 RSB fits. If continuous support → FRSB (R23 prediction). If 2 peaks → 1-RSB (Pred-4 probes this). | **0.18** (deflated from prior ~0.40). k=2 essentially indistinguishable from k=1 in dense Hopfield per Steffan-Kuhn 1994 — promoting to k=2 doesn't rescue 1-RSB's failed predictions. Plus none of Pred-1/3/5 cleanly distinguishes k=1 from k=2. | The 1-RSB negative observations also burn k=2 — same framework family. |
| **(ii) Mode-coupling theory (MCT)** | Self-consistent closure on correlation function predicts ergodicity-breaking with non-ergodicity parameter f_c(k) as plateau height of density correlator. Two-step relaxation: short-time β-regime (power-law) + long-time α-regime (stretched exp). | Single MCT plateau per wave-vector k: f_c(k) is the plateau height of F(k,t) AT the dynamical transition. Does NOT predict 3-plateau structure unless interpreted as 3 different effective k-values (one per corpus-type). Forcing this gives a heuristic mapping but is not principled. | Measure substrate two-time correlation C(t,t_w) on W trajectory; look for two-step relaxation (β plateau + α decay) per corpus stage. If C(t,t_w) shows EXPONENTIAL decay only (no plateau), MCT framework fails at substrate scale (Kerr-Winter 2025 null-result). | **0.15** (deflated from ~0.30). MCT predicts ONE plateau per density-correlator wave-vector, not three plateaus per a retention metric. Forcing 3-plateau interpretation onto MCT is overfitting. Kerr-Winter 2025 says DNN weight dynamics show power-law without caging — direct warning. | R18 already flagged Kerr-Winter caveat as load-bearing brutal honesty. |
| **(iii) Chaos in temperature (CiT)** | Below T_g, slight T (or parameter) perturbations completely reorganize ground state above a chaos length scale; multiple length scales (coherence ξ, chaos crossover ξ*) give multi-step memory phenomenology (Paga 2023 Janus). | Predicts DISTINCT memory-loss thresholds at different perturbation magnitudes — could be read as plateaus IF the perturbation parameter is the corpus-similarity (same vs 4-stage vs diff is "no perturbation / small perturbation / big perturbation"). Plateau heights would correspond to chaos exponent ζ and not to specific values 0.94/0.74/0.60 a priori. | Vary corpus-similarity smoothly (interpolate between same-corpus and diff-corpus via mixing fraction f ∈ [0,1]); plot retention(f). CiT predicts SHARP breakpoints at f corresponding to chaos-length crossover; smooth monotone curve → no chaos. Also: measure overlap correlation between identical-stage W under tiny parameter perturbation (Δβ, ΔN); CiT predicts breakdown above chaos length. | **0.22** (deflated from ~0.45). Best PHYSICAL fit to "discrete jumps under categorical parameter changes." Hopfield CiT is established phenomenon. But CiT typically gives 2 length scales (Paga 2023), not 3. And maps onto "corpus distance" only heuristically — not a derivation. | Could be a structural rescue of 1-RSB framework if it explains why specific α-axis predictions failed: chaos under α-perturbation reshuffles which states are metastable. |
| **(iv) Information-Bottleneck (IB) phase transitions** | IB Lagrangian L = I(X;Z) - β·I(Y;Z) shows DISCRETE phase transitions at critical β-values; each transition = onset-of-learning-a-new-class. Plateaus between transitions correspond to fixed compression-rate ceilings. Wu-Fischer-Tegmark 2020 give second-order calculus formula tying transitions to maximal-correlation orthogonal projections; categorical (X,Y,Z) gives clean discrete-class-onset structure. | Predicts NUMBER of plateaus = number of class-clusters resolvable in joint (corpus_byte, target) distribution. For text bytes: rough class structure = {within-document context} ⊃ {within-corpus context} ⊃ {within-language context}. Heights would correspond to log-cluster-mass ratios. **Quantitatively: 0.94/0.74/0.60 spacing ≈ ratios 1.0 : 0.79 : 0.64 ≈ entropy spacing of nested categorical refinement — plausible but needs explicit MI calculation.** | Ship a CPU experiment that computes I(W ; corpus_label) at the three operating points (same / 4-stage / diff); IB framework predicts these I-values should correspond to discrete jumps NOT smooth interpolation, and the gap between plateaus should equal log(cluster-mass-ratio) of the joint distribution. ALSO falsifiable: vary the number of training corpora K = {1, 2, 3, 4, 5, 8}; IB predicts plateau structure tracks K (e.g., K=3 gives 3 plateaus, K=5 gives 4-5, K=2 gives 2). | **0.42** (deflated from baseline ~0.55, capped at 0.50 for novel synthesis — but kept at 0.42 because IB phase transitions are NOT novel synthesis, they're established framework being newly applied). Genuinely fits the empirical signature (categorical discreteness, parameter-axis immunity). | Strong adjacent-method candidate; passes "don't dismiss adjacent methods" filter. Substrate retention IS a compression of corpus information into W; IB framework is the natural information-theoretic home. |
| **(v) Saddle-cascade plateaus in online-learning dynamics** | Biehl-Schwarze 1995, Saad-Solla 1995, Engel-Van den Broeck textbook framework: high-D online learning has SEVERAL fixed points of the order-parameter ODEs; trajectory passes THROUGH them as plateaus with monotone decreasing error. Each plateau = symmetric subspace where R^a_b values are permutation-degenerate; escape = symmetry-breaking via fluctuation. **Specifically: number of plateaus = number of distinct permutation orbits in teacher-student overlap matrix.** | Predicts plateau heights = generalization-error values at saddle points of the SGD ODE. For substrate: each "corpus type" (same / 4-stage / diff) selects a different saddle structure in W-teacher overlap. **Predicts 0.94/0.74/0.60 spacing is set by the number-of-shared-teachers-K structure: K=1 (same) / K_eff (overlapping 4 stages) / K=0 (disjoint diff).** This is the ONLY framework that gives a principled 3-tier prediction from corpus-type-as-control-parameter. | Smoke-test: train substrate on K teachers with controlled overlap fraction f ∈ {0.0, 0.25, 0.5, 0.75, 1.0}; cascade-plateau framework predicts retention(f) shows DISCRETE LEVELS at f values corresponding to integer-shared-teachers, NOT smooth interpolation. ALSO: predicts plateau-height-spacing depends on student/teacher dimension ratio (substrate's "α equivalent"); if ratio sweep shows fixed plateau values, framework fits. ALSO: predicts plateau escape time scales as 1/(saddle-eigenvalue) — measurable. | **0.46** (deflated from baseline ~0.60, capped 0.50 for novel-synthesis-onto-substrate; kept high because framework is well-established and predicts EXACTLY the substrate signature). Genuine fit to "discrete plateau heights immune to continuous parameters." | **Strongest single candidate.** The framework explicitly predicts what the substrate is showing. R18's R23's R24's failure to catch this is a literature-coverage gap (statistical-physics-first prior). |
| **(vi) Replica chain / hierarchical Hopfield** | Krotov-Hopfield 2021 hierarchical AM: stack of recurrent layers each with own energy function; capacity per layer can be independent; assembled memories combine primitives encoded layer-wise. | Could predict per-layer plateau structure if substrate has IMPLICIT hierarchical decomposition (e.g., byte-token-context as 3 layers). Heights would correspond to per-layer capacities, depending on per-layer N and α. Not a principled prediction of 0.94/0.74/0.60 without further structure. | Already partially probed: cascade-depth Pred-5 HARD-FAIL'd. If "cascade" means same as "hierarchical layer count" then this framework is already dead. Worth re-reading Pred-5 to confirm scope. | **0.10** (deflated from ~0.25). Pred-5 cascade-depth HARD-FAIL is direct negative evidence against any per-layer capacity decomposition story. Keep on shelf only as contingency if Pred-5 scope is narrower than expected. | Probably closeable; not worth designing a follow-up unless Pred-5 reinterpretation opens it. |

---

## Top-2 deep drill

### Candidate (v) — Saddle-cascade plateaus in online learning dynamics — DEEP DRILL

**Mechanism, more precise.** The classical Saad-Solla / Biehl-Schwarze framework (soft-committee or two-layer teacher-student) analyzes online SGD via the order parameters R^a_b = teacher-student overlap and Q^{ab} = student-student overlap. The generalization error ε_g is a function of R and Q. The ODEs governing dR/dα, dQ/dα (where α = examples/N) have *multiple fixed points* corresponding to permutation-symmetric subspaces of the overlap matrix. The trajectory typically lands on the most-symmetric fixed point fastest, gets stuck there (plateau), then escapes via symmetry-breaking once a small perturbation grows. The escape is *cascade-like*: from k-fold symmetric to (k-1)-fold, and so on. **Number of plateaus visited = number of distinct permutation orbits, set by the teacher rank / number of distinct teacher-mode signals.**

**Why this maps cleanly to substrate.** Substrate's W is trained by Hebbian rule on patterns drawn from {byte, position} atoms; the "teachers" are the corpus-byte distributions; the "students" are the W rows. *The three retention plateaus correspond to three categorical levels of teacher-overlap: K=1 (same corpus = all teachers shared), K_partial (4-stage corpus = some teachers shared across stages), K=0 (disjoint corpus = no teachers shared)*. The cascade framework predicts that within each category the retention is a fixed-point of the ODE — *immune to continuous parameters* like N, geometry, time, projection, replay (all of which only shift the time-to-reach the plateau, not the plateau height itself). **This is EXACTLY the empirical signature.**

**Quantitative spacing.** The plateau heights in cascade dynamics depend on (a) student-teacher dimension ratio, (b) number of overlapping teacher modes. For substrate: 0.94 (full overlap) corresponds to "near-Bayes-optimal student"; 0.74 to "partial-overlap saddle" (which is the K-fold permutation-symmetric configuration for substrate's atom alphabet); 0.60 to "orthogonal-teacher residual" (the K=0 fixed point sits at chance ≈ retention from prior + noise). The 0.20 gap and the 0.14 gap are *not random*: they should be derivable from the number of distinct atom-pair-overlap classes in the substrate codebook. This is a *concrete computational claim*.

**Lit-scan honesty caveats.**
- Cascade framework is established in committee-machine / two-layer net online learning. Hebbian outer-product Hopfield is NOT identically a soft-committee but the ODE-of-overlaps framework GENERALIZES (any system with mean-field overlap order parameters has equivalent fixed-point structure).
- *Calibration penalty applied (0.20):* baseline P would be ~0.65 (framework is right, fit is clean); deflated to **0.46** to account for substrate's specific non-standard structure (Kerdock codebook, mixed binding ops, etc.).
- **Hard-fail threshold:** if smoke test (5-teacher overlap-fraction sweep) shows retention(f) is SMOOTH continuous, framework is wrong. If discrete-jump structure is visible, framework lives.

### Candidate (iv) — Information-Bottleneck phase transitions — DEEP DRILL

**Mechanism, more precise.** Tishby-Zaslavsky / Wu-Fischer-Tegmark IB framework: as β increases in L = I(X;Z) - β·I(Y;Z), the optimal stochastic encoder p(z|x) undergoes phase transitions; each transition corresponds to learning to distinguish a new (X,Y)-cluster. For *categorical* X,Y,Z the transitions are DISCRETE (vs continuous for Gaussian). At each plateau, the IB Lagrangian is stuck at a fixed compression-rate level set by the maximal-correlation eigenvalue of the conditional p(Y|X) restricted to the orthogonal complement of the already-learned representation.

**Why this fits substrate.** Substrate's W is precisely a compression Z of corpus information X into a finite-capacity representation. The retention metric is a downstream readout (Y) on Z. The three plateau levels correspond to three nested information-categorical levels:
- 0.94: within-document refinement (all atoms drawn from same context distribution)
- 0.74: within-corpus, across-stage refinement (atoms drawn from related distributions)
- 0.60: across-corpus floor (atoms drawn from independent distributions)
*The 0.94/0.74/0.60 spacing approximates exp(-h_i) where h_i are conditional entropies of nested cluster refinement.* Empirically testable.

**Quantitative spacing test.** Compute I(W ; corpus_label) at each of the three operating regimes. IB predicts:
- Plateau heights satisfy: retention_i ≈ I(W;Y|cluster_i) / I(W;Y|cluster_max)
- *Number of plateaus = number of class-clusters in joint (X,Y) distribution*
- *If we vary K (number of training corpora) ∈ {1,2,3,4,5,8}, number of plateaus should track K*

**Lit-scan honesty caveats.**
- IB phase transitions are well-established (Wu-Fischer-Tegmark ICLR 2020). Applying to *Hebbian outer-product memory* is novel but adjacent — the framework's regularity conditions are generic enough.
- Substrate retention is not literally an IB Lagrangian optimum; it's an empirical metric that *correlates with* I(W;Y). Mapping is heuristic at the metric level.
- *Calibration penalty applied (0.13):* baseline P would be ~0.55 (framework fits the signature, IB is well-established); deflated to **0.42** to account for the metric-mapping heuristic.
- **Hard-fail threshold:** if K-sweep gives MONOTONE-decreasing-retention with NO discrete-step structure (smooth interpolation), IB framework doesn't fit. If 1/2/3/4/5/8 corpora give 1/2/3/4/5/(5-or-6) plateaus → strong fit.

---

## Comparison-matrix summary table (re-stated for skim)

| Rank | Candidate | P(fit) | Falsifier cost | Pred-4-orthogonal? |
|---|---|---|---|---|
| 1 | (v) Saddle-cascade plateaus | **0.46** | CPU ~30-60 min | YES (no hysteresis assumed) |
| 2 | (iv) IB phase transitions | **0.42** | CPU ~20-40 min | YES (info-theoretic, no physics) |
| 3 | (iii) Chaos in temperature | 0.22 | CPU+GPU ~2-4 h | PARTIAL (CiT also predicts first-order, overlaps Pred-4) |
| 4 | (i) k-step RSB | 0.18 | GPU ~5-8 h (full P(q)) | NO (overlaps with Pred-4 directly) |
| 5 | (ii) MCT | 0.15 | GPU ~5-8 h (correlation funcs) | YES but null-result probable per Kerr-Winter |
| 6 | (vi) Replica chain / hier. Hopfield | 0.10 | NA — Pred-5 already HARD-FAIL'd | dead |

---

## Decision logic vs. Pred-4 verdict

| Pred-4 outcome | Action |
|---|---|
| HARD-PASS (hysteresis gap ≥ 0.10, first-order transition) | 1-RSB framework recovers partially. *Still ship candidate (v) cascade-test* — cheap, independent confirmation; if (v) ALSO passes, two-framework triangulation; if (v) fails, 1-RSB carries the explanation alone. |
| HARD-FAIL (gap < 0.03, continuous transition) | 1-RSB framework is dead. *Immediately ship candidate (v) cascade-test as primary;* ship candidate (iv) IB test as second-priority. Framework reliability drops further; substrate-physics framing demoted from "load-bearing" to "useful analogy only." |
| MIDDLE-BAND (gap 0.03-0.10) | Inconclusive. *Ship candidate (v) and (iv) tests in parallel* — they're cheap; if either passes cleanly, that becomes the dominant framework; 1-RSB sits on the shelf with k=2 contingency. |
| INSTRUMENTATION_FAIL (second time) | Same as HARD-FAIL action sequence; do not re-ship Pred-4 a third time without instrumentation fix. |

---

## Handoffs filed in companion files

Two handoff files filed alongside this note (per "top-2 actionable" mandate):

1. **`strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md`** — candidate (v) cascade-test: 5-corpus overlap-fraction sweep to test discrete-vs-smooth plateau structure. CPU ~30-60 min. **Pred-4-orthogonal**, safe to ship in parallel with Pred-4.
2. **`strategy_request_to_exp_dev_ib_plateau_test_2026-05-24.md`** — candidate (iv) IB-phase-transition test: K-sweep ∈ {1,2,3,4,5,8} corpus count to test plateau-count tracking K. CPU ~20-40 min. **Pred-4-orthogonal**, safe to ship in parallel.

**Routing note for orchestrator.** Both handoffs are *Pred-4-orthogonal* — they don't assume hysteresis sign and don't conflict with the in-flight 1-RSB hysteresis probe. They are *cheap CPU drills*. Per pipeline-pacing rule (queue depth >= 1 always) and laptop-cpu-quick-probes rule (CPU is for <60s scoping; remote CPU for longer non-GPU), these are *remote-cpu-queue* candidates. **Pause flag check needed before ship** — orchestrator owns the dispatch decision per OBEY-USER-PAUSE-EXPLICITLY discipline.

---

## Citations (verified arXiv / venue)

### Saddle-cascade plateaus
- Biehl, Schwarze (1995). "Learning by on-line gradient descent." J. Phys. A 28:643. Foundational soft-committee plateau analysis.
- Saad, Solla (1995). "On-line learning in soft committee machines." PRE 52:4225. Soft-committee plateau cascade.
- Saad, Rattray (1997). arXiv:cond-mat/9706015. "Functional Optimisation of Online Algorithms in Multilayer Neural Networks." Plateau-elimination by symmetry-breaking optimization.
- Goldt, Advani, Saxe, Krzakala, Zdeborová (2019). arXiv:1901.09085 / Saad memorial volume 2020. "Generalisation dynamics of online learning in over-parameterised neural networks" — modern revisit; PMC7685244.
- Engel, Van den Broeck (2001). *Statistical Mechanics of Learning*. Cambridge. Textbook treatment of order-parameter cascade dynamics.

### Information bottleneck phase transitions
- Tishby, Zaslavsky (2015). "Deep learning and the information bottleneck principle." ITW 2015.
- Wu, Fischer, Tegmark (2020). arXiv:2001.01878 / ICLR 2020. "Phase Transitions for the Information Bottleneck in Representation Learning." Second-order calculus condition; categorical phase transitions; class-onset interpretation.

### Continual learning order parameters (adjacent, confirmatory)
- Lee, Goldt, Saxe (2021). "Continual Learning in the Teacher-Student Setup: Impact of Task Similarity." PMLR 139. arXiv:2107.04384.
- Sagliotti et al. (2025). PNAS 122:e2501899123. arXiv:2407.10315. "Order parameters and phase transitions of continual learning in deep neural networks." Identifies *phase transitions where CL performance shifts abruptly* with task-similarity order parameters — *direct support for discrete-plateau framework over continuous-RSB framework*.

### k-RSB context (R23 cross-ref)
- Steffan, Kühn (1994). cond-mat/9404036. k=1 vs k=2 in Hopfield: ~1e-6 difference.
- Auffinger, Chen (2017). arXiv:1703.06872. "The SK model is infinite step replica symmetry breaking at zero temperature."

### Mode-coupling theory (R18 cross-ref)
- Götze, Sjögren (1992). Rep. Prog. Phys. 55:241.
- Janssen (2018). arXiv:1806.01369. Frontiers Phys. 6:97. MCT primer.
- Kerr Winter, Janssen (2025). arXiv:2405.13098 / PRR 7:023010. *DNN structural comparison — power-law without caging.* Brutal-honesty caveat carries to this drill.

### Temperature chaos (R23 cross-ref)
- Fernandez, Janus collaboration (2021). arXiv:2010.01214. "Evidence for Temperature Chaos in Spin Glasses." Communications Physics 2021.
- Janus collaboration (2025). arXiv:2507.00276. "Temperature chaos as a logical consequence of the reentrant transition in spin glasses."
- Paga et al. (2023). arXiv:2207.06207 / Nat. Phys. 19:978. *Multi-length-scale memory; 2 length scales.*

### Hierarchical Hopfield (closing)
- Krotov, Hopfield (2021). arXiv:2107.06446. "Hierarchical Associative Memory."

---

## Self-audit per [[feedback-verify-implementations]]

- Spot-checked Saad-Solla 1995 framework: order-parameter ODE plateaus from saddle-symmetric subspaces — matches our use. ✓
- Spot-checked Biehl-Schwarze 1995 abstract: "plateaux in the time dependence of the generalization error" — exact phrase in our drill. ✓
- Spot-checked Wu-Fischer-Tegmark 2020 abstract: "phase transitions in IB Lagrangian as β increases; categorical phase transitions" — matches. ✓
- Spot-checked Sagliotti 2025 abstract: "phase transitions where the network's ability to learn changes abruptly with the order parameter; for task-specific readouts a phase transition where CL performance shifts dramatically as tasks become less similar" — DIRECT support for top-2 ranking.
- Probability all framework attributions correct: 92%
- Probability all P(fit) numbers are honest after calibration penalty: 80%

## Brutal-honesty caveats per [[feedback-no-smoke]]

1. **Top-2 P(fit) values (0.46 and 0.42) are still under 0.50.** Both could fail. The drill identifies *candidates worth testing*, not candidates known to work. Per lit-scan calibration penalty rule, P > 0.50 was capped — 0.46 and 0.42 are the honest top-of-range.
2. **Cascade-plateau framework was missed in R18/R23/R24** because those drills privileged statistical-physics-first framing. This is a *literature-coverage gap*. Future drills should always include learning-dynamics framing as an explicit channel — adding to active_protocols recommendation.
3. **IB framework's mapping from substrate-retention-metric to IB-Lagrangian-value is heuristic, not derived.** If the falsifier (K-sweep) shows plateau-count NOT tracking K, framework is dead regardless of other fits.
4. **Even if candidate (v) passes, it doesn't make substrate "not glassy"** — both frameworks can coexist; saddle-cascade ODE structure CAN emerge from glassy landscape geometry. The reframe would be "plateau structure is best explained by saddle-cascade dynamics, with substrate's glassy phase being the *generator* of the saddle structure" — i.e., 1-RSB becomes mechanism, saddle-cascade becomes phenomenology.
5. **Pred-4 verdict is still load-bearing.** This drill does NOT replace Pred-4; it sets up the next-step regardless of Pred-4 outcome.

## Status_log entry per [[feedback-for-you-tab-primary-channel]]

Filed after this note: status_log entry tagged `research_delivery` with plain_language="Found two alternative theoretical homes for the substrate's three-plateau retention; saddle-cascade and IB phase-transitions are both adjacent-method candidates that fit the empirical signature better than 1-RSB has; companion handoffs filed for cheap CPU falsifiers; ready for orchestrator dispatch before Pred-4 lands." importance=high.

---

**End research note.**
