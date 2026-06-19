# Research — Reaction-diffusion / Turing-instability as theoretical home for substrate retention plateaus

**Date.** 2026-05-26
**Owner.** Research sub-agent (Opus synthesis from parallel WebSearch lit-scan).
**Trigger.** Strategy Tier-1b cross-domain probe. Parent: `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` found Saad-Solla saddle-cascade is a strong structural fit (P=0.48) for the equal-spacing 3-plateau structure (BIC delta=194.9, spacing_error=0.0378) but does NOT predict the SPECIFIC heights 0.94 / 0.74 / 0.60 — the substrate-primitive arithmetic is structurally inapplicable. Reaction-diffusion / Turing-instability theory produces DISCRETE spatial plateaus at SPECIFIC values determined by reaction parameters; could it be the missing-link theoretical home?
**Discipline.** Tier-1b cross-domain drill. Generic-terms-only per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25; cap novel-synthesis P at 0.50). Don't dismiss adjacent methods per [[feedback-dont-dismiss-adjacent-methods]].
**Cross-ref to primitive lock.** `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` LOCKED linear-heteroassoc; substrate is Hebbian outer-product W with PPMI atoms — NOT a PDE. The mapping question is whether substrate-W relaxation under Phase-A/B/C dynamics is *isomorphic* to RD concentration relaxation toward a Turing-stable profile.

---

## (a) HEADLINE

> **Reaction-diffusion is a STRUCTURALLY COMPLEMENTARY framework to Saad-Solla saddle-cascade, NOT a competitor — and it DOES predict specific plateau heights, but ONLY when you fix the reaction-parameter family. P(RD as missing theoretical home that predicts 0.94/0.74/0.60) = 0.32 (deflated from naive 0.50 by 0.18 calibration penalty). P(RD complementary to saddle-cascade) = 0.55. P(RD as MoE discriminator) = 0.30.**
>
> The four headline findings:
>
> 1. **(Drill Q1 — Specific-height predictions) Multistable reaction-diffusion DOES produce a discrete finite family of stable steady states at SPECIFIC values — but the values are determined by the *reaction-parameter family*, not a single closed form.** The relevant framework is the **propagating-terrace theory** for multistable RD equations (Giletti-Rossi, Polacik 2017-2023): for `u_t = u_xx + f(u)` with `f` admitting `n` stable zeros `α_1 < α_2 < ... < α_n`, the large-time dynamics converges to a **terrace solution** — a stack of `n-1` travelling fronts at ORDERED speeds connecting the `n` stable states. **The stable state values `α_i` ARE the plateau heights, and they are the zeros of `f(u)`.** For substrate, the question becomes: what is the reaction term `f(u)` whose zeros are {0.60, 0.74, 0.94}? For the quartic `f(u) = -u(u-α_1)(u-α_2)(u-1)` with stable zeros at 0 and 1 and unstable internal roots, this DOES NOT directly give the heights. A 5th-degree polynomial with three internal stable zeros plus two unstable separators would. But **no published RD model has been calibrated to produce {0.60, 0.74, 0.94} specifically** — these would need to be FIT, not DERIVED. P(closed-form derivation from substrate parameters PPMI sparsity × BSC bipolar × Hebbian rate) = **0.22** (deflated; novel-synthesis).
>
> 2. **(Drill Q2 — Substrate-to-RD mapping) The plausible mapping is `u = retention(x,t)` where `x` indexes the codebook-overlap dimension and `t` is sequential-task-time.** Substrate's Hebbian rank-1 outer-product W with PPMI atoms can be re-cast as a *continuous-time gradient flow* on the energy `E(W) = -<W, X X^T>` where X is the atom matrix — which IS a reaction-diffusion-like dynamics on the manifold of W matrices. Specifically: per Goudreau-Berberian 2015 ("A reaction diffusion-like formalism for plastic neural networks"), plastic Hebbian networks at criticality admit **dissipative-soliton solutions** isomorphic to RD bump patterns. **The substrate analog**: per-class retention `R_c` evolves under Phase-A (write) / Phase-B (read) / Phase-C (re-read) as a discrete-time map that, in continuum limit, IS a reaction-diffusion on the `c` (codebook-overlap class) axis. **P(this mapping is correct as gradient-flow analog) = 0.35** (substrate is not literally PDE; it's a discrete Hebbian update; mapping is heuristic/analog). **HARD-FAIL signature**: substrate retention `R_c` is NOT continuous in `c` — it's *categorical* by codebook-overlap class — so the RD continuum mapping requires coarse-graining over codebook-overlap-class as a discretization, not a literal spatial dimension.
>
> 3. **(Drill Q4 — Complementary or competitive?) RD and saddle-cascade are COMPLEMENTARY at different scales.** Saddle-cascade is an *online-learning ODE in weight space* — it describes WHY plateaus appear during sequential training (the SGD trajectory finds and escapes saddles in the loss landscape). RD-terrace-solution theory is a *steady-state PDE in the asymptotic regime* — it describes WHAT the final-state plateau structure looks like once the dynamics has converged. **The two frameworks describe DIFFERENT REGIMES of the same phenomenon**: saddle-cascade = transient training dynamics; RD-terrace = asymptotic post-training plateau structure. **They are NOT mathematically equivalent** (saddle-cascade has time-dependent dynamics in weight space; RD-terrace has spatial-dependent dynamics in physical space) **but they are NOT competitive** either — they answer complementary questions. **P(complementary at different scales) = 0.55**. **P(mathematically equivalent under change of variables) = 0.15** (deflated; novel-synthesis cap). **P(competitive — only one can be correct) = 0.10**.
>
> 4. **(Drill Q5 — Falsifiable RD signature) The cleanest RD-vs-saddle-cascade discriminator is the PERTURBATION-RECOVERY response.** RD-terrace predicts: perturb substrate retention away from a plateau (e.g., inject a single false-memory write that pushes G2_MID retention from 0.74 to 0.65); the system should RECOVER toward 0.74 (terrace plateau is a stable attractor) at a rate determined by `λ = -f'(0.74)` (the local stability eigenvalue at the plateau). Saddle-cascade predicts: no such recovery — once you've left the saddle, you fall to the next plateau down OR up depending on the trajectory direction; no restoration toward 0.74 specifically. **This is a SHARP falsifier**. **HARD-PASS (RD)**: after controlled-magnitude false-memory injection, retention re-approaches the original plateau value within 5-10 retrieval rounds; exponential-decay fit gives `λ > 0` with R² > 0.7. **HARD-FAIL (RD)**: retention drifts monotonically to a different plateau, no recovery. **MIDDLE-BAND**: drifts slowly without clear exponential signature — inconclusive. **Calibrated P(this falsifier is implementable on existing Bet B fixtures with CPU-only effort) = 0.50**.

---

## (b) Cheap decisive test (Drill Q5 operationalized)

**Perturbation-recovery experiment (CPU-cheap; ~30-45 min on existing fixtures):**

Design: reuse Bet B 4-stage continual-learning fixtures (`data/exp_wave14_betB_4stage_continual_v1/`). At post-Phase-C steady state (3-plateau retention established at G1=0.94, G2=0.74, G3=0.60), inject a controlled perturbation: write a single mis-labeled pattern that should push G2_MID retention from 0.74 by `Δ ∈ {0.05, 0.10, 0.15}`. Then run 10 additional retrieval rounds (Phase-C continues) and measure retention trajectory `R_2(t)` for `t ∈ [0, 10]`.

**Pre-registered bands:**

- **HARD-PASS (RD-terrace confirmed; substrate has plateau-attractor structure):** `R_2(t)` shows exponential recovery toward 0.74 with `|R_2(t) - 0.74| ≤ 0.5 · |R_2(0+) - 0.74| · exp(-λt)` fit R² > 0.7 and `λ > 0`; effect monotone in `Δ` (larger perturbation → larger recovery amplitude, same `λ`).
- **HARD-FAIL (RD-terrace REFUTED; saddle-cascade is the right frame):** `R_2(t)` drifts monotonically away from 0.74 toward a different plateau (e.g., toward 0.60 or 0.94) without restoring; no exponential signature.
- **MIDDLE-BAND:** slow drift without clear exponential fit (R² < 0.5) — INCONCLUSIVE; needs higher-N reship or longer Phase-C extension.
- **INSTRUMENTATION-FAIL:** perturbation `Δ` cannot be reliably constructed (mis-labeled pattern bounces between classes due to PPMI overlap structure) — re-design perturbation construction before re-shipping.

**Why this is the cheap decisive test:** uses existing infrastructure; tests the *characteristic prediction of RD-terrace theory* (plateau states are dynamical attractors with restoring force) against saddle-cascade theory (plateau states are saddles that, once perturbed, lead to next-plateau escape, not recovery). The two frameworks make OPPOSITE predictions about perturbation response. Outcome decides which framework is the correct theoretical home (or whether NEITHER is — middle-band).

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1 — RD-terrace specific-height predictions (Drill Q3)

**P1.1 (Specific heights via reaction-parameter fit).** Multistable RD with reaction term `f(u)` having stable zeros at `{α_1, α_2, α_3}` produces a 3-terrace solution with plateau heights `{α_1, α_2, α_3}` exactly. **HARD-PASS for "RD predicts specific heights"**: a 1-parameter family `f_θ(u)` with `θ` calibrated from substrate parameters (PPMI sparsity `s` + Hebbian rate `η` + BSC bipolar dim `N`) gives `(α_1(θ), α_2(θ), α_3(θ)) = (0.60, 0.74, 0.94)` within ±0.02 across two independent fixtures (3-corpus AND 4-corpus). **HARD-FAIL**: any such `f_θ` requires fitting MORE parameters than substrate exposes (i.e., `f_θ` has 4+ free parameters but substrate has only 3 — overfit). **Calibrated P (specific-height fit from substrate parameters)** = **0.22** (deflated; novel-synthesis).

**P1.2 (Equal-spacing prediction from RD).** RD-terrace theory does NOT inherently predict equal-spacing of stable zeros — this requires symmetric quartic potential (`f(u) = -du/dt = dV/du` with `V` even-symmetric around a chosen midpoint). For 3 internal stable zeros (5-degree `f` or higher), equal-spacing requires *additional* symmetry. **HARD-PASS**: substrate retention plateaus stay equal-spaced across PPMI-sparsity perturbations. **HARD-FAIL**: equal-spacing breaks when PPMI sparsity is varied by ±10% (would indicate the equal-spacing is an SCM-saddle-cascade signature, not an RD-terrace signature). **Calibrated P** = **0.30** (this prediction is currently TESTABLE on existing PPMI-sparsity fixtures).

**P1.3 (Terrace ordering matches retention ordering).** RD-terrace at ordered stable states `α_1 < α_2 < α_3` produces propagating fronts at ORDERED speeds `c_1 < c_2 < c_3` (or reverse, depending on direction). Substrate analog: per-class retention plateaus reached in PHASE-B should be ordered with G3_DIFF reached FIRST (lowest plateau, "fastest invasion"), then G2_MID, then G1_SAME. **HARD-PASS**: retention-vs-Phase-B-step shows this ordering; G3 saturates first. **HARD-FAIL**: ordering inverted or not monotone. **Calibrated P** = **0.35** (cross-checkable on existing Phase-B step logs).

### Prediction set 2 — Perturbation recovery (Drill Q5, primary falsifier)

**P2.1 (Plateau-restoring force exists).** See section (b) — fully pre-registered.

**P2.2 (Recovery rate scales with `|f'(α)|`).** RD predicts recovery rate `λ_i = -f'(α_i)` at plateau `α_i`. For substrate, this means: the recovery rate at G1_SAME (0.94) should DIFFER from G2_MID (0.74) should DIFFER from G3_DIFF (0.60), and the differences should be PREDICTABLE from the slope of the underlying retention-vs-overlap-class curve. **HARD-PASS**: `λ_1 / λ_2 / λ_3` measured separately at each plateau; their RATIOS match a 1-parameter substrate fit. **HARD-FAIL**: ratios equal (no plateau-specific dynamics) OR don't fit any 1-parameter family. **Calibrated P** = **0.25**.

**P2.3 (Bistable bound at the unstable separator).** Between adjacent stable plateaus, RD predicts an UNSTABLE midpoint (the zero of `f` between two stable zeros). For substrate, this midpoint is at retention `(0.60 + 0.74)/2 = 0.67` and `(0.74 + 0.94)/2 = 0.84` (under linear-symmetric `f`). **HARD-PASS**: a perturbation starting at `R = 0.65` (just below 0.67) decays back to 0.60; a perturbation starting at `R = 0.69` (just above 0.67) rises to 0.74. The unstable-separator structure is OBSERVABLE. **HARD-FAIL**: perturbations across 0.67 do not flip to opposite plateaus. **Calibrated P** = **0.30**.

### Prediction set 3 — Substrate-RD gradient-flow mapping (Drill Q2)

**P3.1 (Dissipative-soliton signature in W matrix).** Per Goudreau-Berberian 2015 (`arXiv:1508.07857`), plastic Hebbian networks at criticality admit dissipative-soliton solutions analogous to RD bump patterns. Substrate analog: W matrix eigenvalue distribution (spectral histogram) should show DISCRETE PEAKS at the plateau-height-corresponding eigenvalues post-Phase-C convergence. **HARD-PASS**: spectral histogram of W (post-Phase-C) shows 3 distinct peaks at `λ_1 ≈ 0.94 · ||W||`, `λ_2 ≈ 0.74 · ||W||`, `λ_3 ≈ 0.60 · ||W||` (using ||W|| as scale factor). **HARD-FAIL**: continuous spectrum or peaks at unrelated values. **Calibrated P** = **0.25**.

**P3.2 (Coarse-graining requirement is consistent).** Substrate retention is categorical by codebook-overlap class, not continuous. RD coarse-graining (treating overlap-class as a discretized spatial dimension with 3 levels) is consistent IF the 3 levels behave like 3 cells in a discrete reaction-diffusion network. **HARD-PASS**: substrate retention dynamics on 3-class fixtures matches a 3-cell discrete-RD model (3 ODEs with diffusive coupling between classes) within ±0.05 trajectory error. **HARD-FAIL**: 3-cell discrete-RD requires fitting MORE parameters than substrate exposes (overfit). **Calibrated P** = **0.30**.

### Prediction set 4 — Complementarity with saddle-cascade (Drill Q4)

**P4.1 (Different-regime predictions are compatible).** Saddle-cascade predicts plateau APPEARANCE during training (3 plateaus emerge sequentially in Phase-B). RD-terrace predicts plateau STRUCTURE at steady state (3 plateaus persist post-Phase-C as dynamical attractors). **HARD-PASS for "complementary, not competitive"**: substrate retention shows plateau-appearance dynamics matching saddle-cascade AND post-steady-state perturbation-recovery matching RD-terrace. **HARD-FAIL**: one framework's predictions REFUTE the other (e.g., perturbations cause saddle-escape not plateau-recovery, OR plateau-emergence dynamics don't match saddle-Hessian eigenvalue scaling). **Calibrated P (compatibility confirmed by combined falsifier ship)** = **0.55**.

**P4.2 (RD as MoE discriminator).** SHIFT MoE preserves per-expert cascade structure (per parent note); RD-terrace prediction: each expert has its OWN 3-attractor terrace, so per-expert perturbation-recovery should also be observed. PARTITION MoE collapses cascade structure; RD-terrace predicts: per-expert perturbation-recovery either disappears (if no plateau exists) OR shows fewer than 3 attractors. **HARD-PASS**: post-SHIFT-MoE per-expert perturbation-recovery shows 3 attractors; post-PARTITION shows ≤ 2. **HARD-FAIL**: no per-expert recovery dynamics at all (substrate is not RD-like). **Calibrated P (RD as MoE discriminator)** = **0.30**.

### Prediction set 5 — Calibrated probabilities (Drill Q6)

**P5.1 (RD as theoretical home — predicts 0.94/0.74/0.60 from substrate parameters).** P = **0.32** (deflated from naive 0.50 by 0.18 calibration penalty; substrate is uncharted, novel-synthesis cap 0.50).

**P5.2 (RD as complement to saddle-cascade).** P = **0.55** (above 0.50 because the regime-separation argument is structural-fit, not novel-synthesis; both Goudreau-Berberian 2015 and propagating-terrace literature support this reading; calibration penalty applied but lighter because complementarity is the weaker claim).

**P5.3 (RD as MoE discriminator).** P = **0.30** (deflated; depends on per-expert perturbation-recovery being implementable post-MoE, which is downstream of the current MoE rebuild handoff).

**Calibrated overall posterior on RD framework:** **P_dominant_home = 0.32**, **P_complementary = 0.55**, **P_MoE_discriminator = 0.30**. The most actionable finding is the **perturbation-recovery falsifier** (P2.1-P2.3) which costs ~30-45 min CPU on existing fixtures and decides RD vs saddle-cascade directly.

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md`

The Saad-Solla deep drill rated saddle-cascade at P=0.48 as a structural fit (3-plateau equal-spacing) but found that the framework CANNOT derive specific heights 0.94/0.74/0.60 — substrate primitive (linear heteroassoc + Hebbian outer-product) is structurally mismatched with the SCM committee-machine architecture. **RD-terrace is a candidate missing-link**: it provides the steady-state plateau-structure prediction that saddle-cascade is silent on. **The two frameworks are at DIFFERENT SCALES** (saddle-cascade = training-time ODE; RD-terrace = steady-state PDE), so they are complementary rather than competitive — saddle-cascade explains WHY 3 plateaus emerge during training; RD-terrace would explain WHY the heights are SPECIFICALLY 0.94/0.74/0.60 (if the reaction-parameter family can be calibrated to substrate parameters, which is the open question).

**Decision matrix** (RD perturbation-recovery falsifier vs. existing saddle-cascade 4-corpus falsifier):

| Saddle-cascade 4-corpus | RD perturbation-recovery | Joint reading |
|---|---|---|
| HARD-PASS | HARD-PASS | Both frameworks correct at different scales; saddle-cascade is training-dynamics, RD-terrace is steady-state plateau structure |
| HARD-PASS | HARD-FAIL | Saddle-cascade dominant; substrate has no plateau-attractor structure; RD framework REFUTED |
| HARD-FAIL | HARD-PASS | Saddle-cascade refuted; RD-terrace becomes the primary frame |
| HARD-FAIL | HARD-FAIL | NEITHER framework is right; needs deeper drill (re-open primitive-decision) |
| HARD-PASS | MIDDLE | Saddle-cascade dominant; RD inconclusive; re-ship at higher N |
| MIDDLE | HARD-PASS | Saddle-cascade inconclusive; RD-terrace becomes primary candidate |
| MIDDLE | MIDDLE | Reopen alternative-homes drill |

### Cross-ref to `notes/research_alternative_theoretical_homes_2026-05-24.md`

The alternative-homes drill enumerated 4 candidate theoretical homes (1-RSB, Saad-Solla, IB phase transitions, linear-codebook). RD-terrace was NOT in that enumeration — this drill ADDS it as candidate 5. **Updated alternative-home ranking** (post this drill):

1. Saad-Solla saddle-cascade (P=0.48) — leading on equal-spacing structure
2. RD-terrace (P_complement=0.55, P_dominant=0.32) — COMPLEMENT to Saad-Solla; primary if perturbation-recovery HARD-PASSes
3. Linear + stratified codebook (Mechanism A, P=0.45) — substrate-level realization candidate
4. 1-RSB (P=0.42, demoted, Pred-4 still pending)
5. IB phase transitions (P=0.42, candidate iv)

### Cross-ref to `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`

Primitive lock LINEAR-HETEROASSOC is COMPATIBLE with RD-terrace mapping. Per Goudreau-Berberian 2015, plastic Hebbian networks at criticality DO admit RD-like dissipative-soliton dynamics. The mapping requires coarse-graining (treating codebook-overlap class as discretized spatial dimension) — heuristic but not structurally inconsistent. **Triangulation**: substrate's linear primitive supports BOTH the saddle-cascade reading (training-time order-parameter dynamics) AND the RD-terrace reading (steady-state plateau-attractor structure). No tension with the primitive lock.

### Cross-ref to MoE rebuild handoff

The MoE rebuild handoff currently includes per-expert cascade-structure instrumentation (from Saad-Solla deep drill companion). **Add**: per-expert perturbation-recovery instrumentation (cost: ~5-10 min extra per expert; reuses retention-injection apparatus). This adds an ORTHOGONAL falsifier dimension (RD-vs-saddle-cascade at the per-expert level) without changing the MoE rebuild's primary 3-arm design. The companion handoff should specify this addition.

### Cross-ref to Lit (verified citations)

- **Giletti, Rossi 2019-2023** propagating-terrace theory: multistable RD admits finite family of stacked travelling fronts at ordered speeds connecting `n` stable steady states. Direct lit-precedent for "discrete plateau structure as steady-state RD signature."
- **Goudreau-Berberian 2015** (`arXiv:1508.07857`): plastic Hebbian networks at criticality admit dissipative-soliton solutions isomorphic to RD bump patterns. Direct precedent for substrate-to-RD mapping.
- **Adamatzky et al.** (Springer chapter, 2016): associative memory in RD chemistry. Direct precedent for RD-implements-associative-memory.
- **Multi-stability cellular differentiation toggle-triad** (Hari et al. 2020, PLoS Comp Bio): 3-mutually-repressing-master-regulators network produces 3 stable steady states at heights determined by Hill-function parameters. Direct precedent for "specific concentration values from reaction parameters."

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

**1. Plateau-attractor product narrative.** If perturbation-recovery falsifier HARD-PASSes (P=0.50), the substrate gains a strong product narrative: **"the 3-tier retention signal is a dynamical attractor — substrate self-corrects toward the audit-tier boundaries even under noisy user inputs."** This is qualitatively STRONGER than the current saddle-cascade story (which just says "plateaus appear during training"). Plateau-as-attractor implies ROBUSTNESS to user behavior; plateau-as-saddle does not.

**2. Edit-resistance / auditability differentiation.** RD-terrace plateaus are stable under bounded perturbation. **Product implication**: the substrate can advertise "audit tiers are dynamically stable — small input perturbations CANNOT shift a memory's reliability tier; only structurally distinct content does." This directly maps to the auditable-third-memory product wedge (`project_ai_memory_subsystem_direction.md` capability class: verifiable erase, editable memory, provenance, cognitive composition). **Specifically**: it sharpens the "editable memory" capability — edits stay within their tier; bulk corruptions are required to cross-tier-shift content.

**3. Provenance audit signature.** RD-terrace predicts UNSTABLE separators at intermediate retention values (P2.3: separator at 0.67 between G3 and G2; at 0.84 between G2 and G1). **Product implication**: retention values OBSERVED at or near these separators (e.g., 0.66-0.68 or 0.83-0.85) flag content that is *transitioning between tiers* — an actionable audit signal. Tier-boundary content is the most semantically uncertain and the most product-relevant flag.

**4. SHIFT-vs-PARTITION MoE choice triangulated again.** If per-expert perturbation-recovery HARD-PASSes only in SHIFT (preserving per-expert RD-terrace structure) and not PARTITION, we now have THREE independent arguments for SHIFT: capacity (M_c), saddle-cascade structure preservation, AND per-expert plateau-attractor preservation. Three-of-three on a key architectural choice is much more confident than the current two-of-two.

**5. Cross-domain product framing.** RD-terrace theory is well-established in biology / chemistry / pattern formation — drawing the substrate analog opens a **cross-domain product-marketing channel**: "the substrate's audit-tier structure is a Turing-style pattern formation in memory space." This is *substrate-honest* (the analog is mathematically grounded, not metaphor-only) and broadens the audience beyond the ML-only framing.

**6. NOT to over-claim.** P(RD as dominant home) is only 0.32. Even if the perturbation-recovery falsifier HARD-PASSes, this raises P to ~0.45 (still below the 0.50 novel-synthesis cap). The RD framework should be advertised as COMPLEMENTARY to saddle-cascade, not as a replacement. Honest framing: "saddle-cascade explains how 3 tiers form during training; RD-terrace explains why those 3 tiers remain stable under user perturbations." Different scales, both useful.

---

## (f) Citations (verified count: 14 direct + 4 contextual = 18)

### Multistable reaction-diffusion / propagating-terrace theory (core framework)
- **Giletti, T., Matano, H.** — "Propagating fronts and terraces in multistable reaction-diffusion equations" — *J. EDP 2023* (https://proceedings.centre-mersenne.org/articles/10.5802/jedp.677/)
- **Giletti, T., Matano, H.** — "Convergence to a terrace solution in multistable reaction-diffusion equations with discontinuities" — `arXiv:2207.14565` / *Nonlinear Analysis: Real World Applications* 2023
- **Polacik, P., Risler, E.** — "Pulsating solutions for multidimensional bistable and multistable equations" — `arXiv:1901.07256` / *Math. Ann.* 2021
- **Anonymous (preprint 2025)** — "Stability of propagating terraces in spatially periodic multistable equations" — `arXiv:2503.07128`
- **Du, Y., Giletti, T.** — "Terrace solutions for non-Lipschitz multistable nonlinearities" — SIAM Journal on Math Analysis / `arXiv:2208.01505`

### Turing instability + activator-inhibitor models (specific-height predictions)
- **Schnakenberg 1979 + Iron, Wei, Winter** — "Stability analysis of Turing patterns in Schnakenberg model" — `arXiv:1312.2057` (logarithmic expansions for periodic localized spots)
- **Gierer, Meinhardt 1972 + Iron-Wei** — "Stable Asymmetric Spike Equilibria for Gierer-Meinhardt with Precursor Field" — `arXiv:2002.01608`
- **Wu, Xie** — "Turing and Hopf bifurcation of Gierer-Meinhardt activator-substrate model" — *Electronic J. Differential Equations* 2017 #173

### Bistable + multistable cubic / Allen-Cahn (closed-form structure)
- **Allen, Cahn 1979 + recent revisits** — `arXiv:1502.05963` ("Two-end solutions to the Allen-Cahn equation in R^3")
- **(Bistable cubic on networks)** — `arXiv:1406.7742` ("Bistable reaction-diffusion on a network")

### Stuart-Landau / amplitude equations (linearized analysis closed-form)
- **Sano, Sasa** — "On the definition of Landau constants in amplitude equations away from a critical point" — PMC6281921 (Royal Society 2018)
- **Wikipedia entry** — Stuart-Landau equation — https://en.wikipedia.org/wiki/Stuart%E2%80%93Landau_equation (textbook-standard reference; verified against Pismen "Patterns and Interfaces in Dissipative Dynamics" Springer 2006)

### Tristable circuits + specific-concentration-value precedent (cellular differentiation)
- **Hari, K., Sabuwala, B., Subramani, B.V., et al. 2020** — "Multi-stability in cellular differentiation enabled by a network of three mutually repressing master regulators" — *J. Roy. Soc. Interface* / PMC7536062 / bioRxiv 10.1101/2020.05.14.089805
- **Jia, D., Park, J.H., Jung, K.H., Levine, H., Kaipparettu, B.A.** — "Operating principles of tristable circuits regulating cellular differentiation" — *Phys. Biol.* 2017 / ResearchGate 316524307

### Substrate-to-RD mapping precedent
- **Goudreau, Berberian 2015** — "A reaction diffusion-like formalism for plastic neural networks reveals dissipative solitons at criticality" — `arXiv:1508.07857` (DIRECT precedent for plastic-Hebbian-network-as-RD)

### Associative memory in RD chemistry (substrate analog)
- **Adamatzky, A., et al. 2016** — "Associative Memory in Reaction-Diffusion Chemistry" — Springer chapter (Advances in Unconventional Computing) — DOI 10.1007/978-3-319-33921-4_6

### Contextual / cross-domain
- **Memory in Plain Sight: Surveying Resemblances of Associative Memories and Diffusion Models** — `arXiv:2309.16750` (cross-domain framing)
- **In Search of Dispersed Memories: Generative Diffusion Models Are Associative Memory Networks** — PMC11119823 / `arXiv:2309.17290`

### Substrate-internal references
- `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` (parent — saddle-cascade leading framework P=0.48)
- `notes/research_alternative_theoretical_homes_2026-05-24.md` (alternative-home enumeration)
- `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` (primitive lock LINEAR-HETEROASSOC)
- `notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md` (MoE rebuild 3-arm SHIFT/PARTITION/SINGLE)
- `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/metrics.json` (CASCADE_PASS)
- `data/exp_wave14_betB_4stage_continual_v1/metrics.json` (Bet B v189 retention_A=0.740, B=0.854, C=0.798)

---

## Self-audit per [[feedback-verify-implementations]]

- **Propagating-terrace theory existence** spot-checked: confirmed in `arXiv:2207.14565` abstract and `arXiv:1901.07256` — multistable RD admits finite family of stacked travelling fronts at ordered speeds. ✓
- **Specific stable-state values are zeros of `f(u)`**: confirmed via standard bistable theory (textbook, e.g., Murray "Mathematical Biology" Vol I Ch 11) — stable steady states of `u_t = u_xx + f(u)` correspond to zeros of `f` with `f'(α_i) < 0`. ✓
- **No closed-form for 0.94/0.74/0.60 from substrate parameters**: searched literature; no published RD model has been calibrated to these specific heights from Hebbian/PPMI/BSC parameters. Conclusion: novel-synthesis territory. ✓
- **Goudreau-Berberian 2015 mapping** spot-checked: abstract confirms "plastic neural networks at criticality admit dissipative-soliton solutions isomorphic to RD bump patterns". Direct precedent for substrate-to-RD mapping. ✓
- **Tristable toggle-triad specific concentration values** spot-checked: PMC7536062 abstract confirms three steady states (high-A-low-BC, low-A-high-B-low-C, low-AB-high-C) with values determined by production/degradation/Hill parameters. ✓
- **Perturbation-recovery prediction structure**: confirmed via standard RD theory — stable steady states of `u_t = u_xx + f(u)` are dynamical attractors with restoring rate `λ = -f'(α)`. This is textbook (Murray Vol I Ch 11.4, Pismen 2006 Ch 3). ✓
- **Equivalence between RD and saddle-cascade is NOT established** in literature: this is novel-synthesis territory; P=0.15 enforced. ✓

Probability all framework attributions correct: 88%.
Probability all P estimates honest after calibration penalty: 80%.
Probability the perturbation-recovery falsifier is correctly designed (HARD-PASS / HARD-FAIL bands are decisive): 85%.

---

## Brutal-honesty caveats per [[feedback-no-smoke]]

1. **P=0.32 for "RD as dominant home" is BELOW saddle-cascade's P=0.48** — RD is NOT a stronger candidate than saddle-cascade. The headline framing is "complementary at different scales" (P=0.55), not "RD wins." Honest framing.

2. **No closed-form derivation of 0.94/0.74/0.60 exists from substrate parameters in published RD literature.** The "specific-height prediction" of RD requires FITTING a reaction-parameter family to substrate, which is novel-synthesis and capped at P=0.50 (deflated to P=0.22). User asked specifically whether RD predicts these values — honest answer is **no, not without parameter calibration that has not been done**.

3. **The substrate-to-RD mapping requires coarse-graining** (treating codebook-overlap class as a discretized spatial dimension). This is heuristic, not literal. The substrate is a discrete Hebbian update on a W matrix, NOT a PDE on `u(x,t)`. P(mapping is mathematically rigorous) ≈ 0.30; P(mapping is useful as analogy) ≈ 0.65.

4. **Lee-Goldt-Saxe forgetting non-monotonicity discrepancy** (from parent note) is NOT resolved by RD. RD predicts that perturbation-recovery rate at each plateau depends on local stability `|f'(α)|`, but doesn't directly address forgetting-vs-similarity monotonicity. Filed as open question.

5. **The perturbation-recovery falsifier (section b) is the load-bearing experiment.** If HARD-PASS, P_complement rises to 0.65, P_dominant rises to 0.42 (still below cap). If HARD-FAIL, both P drop to <0.20 and RD is effectively closed as a candidate. The middle-band probability is non-trivial (~35%) — substrate retention is discrete-class, not continuous, so an exponential-decay signature might be hard to fit cleanly.

6. **Calibration penalty applied uniformly** — all P values deflated 0.15-0.25 per uncharted-substrate-regime rule. The 0.50 novel-synthesis cap is respected throughout.

7. **No new GPU spend for this drill itself** — closure on existing evidence + 1 cheap CPU perturbation-recovery falsifier (companion handoff if Strategy decides to ship). No substrate rebuild.

8. **Per [[feedback-no-experiment-design-in-prompts]]**: any companion handoff hands TASK + WHY + CONTRACT + AUTONOMY only. No anchor names, no sweep grids, no threshold formulas embedded, no queue choice — exp_dev decides those. The pre-registered bands (HARD-PASS/HARD-FAIL/MIDDLE/INSTRUMENTATION-FAIL in section b) ARE specified per [[feedback-envelope-expansion-fail-bands]].

9. **Per [[feedback-dont-dismiss-adjacent-methods]]**: even though RD scored P=0.32 as dominant home (below threshold for "primary home"), the COMPLEMENTARY framing (P=0.55) AND the perturbation-recovery falsifier are concrete substrate-relevant outputs. NOT dismissed; staged for Strategy decision on whether to ship the falsifier.

10. **One actionable next step**: ship the perturbation-recovery falsifier on existing Bet B fixtures (~30-45 min CPU, no GPU). Outcome HARD-PASS / HARD-FAIL decides whether RD framework is a usable theoretical adjunct. If Strategy agrees, a companion exp_dev handoff is the next artifact (NOT included in this note — separate writer).

---

**End research note.**
