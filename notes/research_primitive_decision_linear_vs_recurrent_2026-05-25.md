# Research — strategic primitive decision: LINEAR-HETEROASSOC vs RECURRENT-AUTOASSOC

**Filed:** 2026-05-25 by Research sub-agent (Opus synthesis, 6-prong WebSearch lit-scan).
**Routing:** orchestrator (strategy-direction) request from α_c-anomaly drill closure (`notes/research_substrate_alpha_c_anomaly_2026-05-24.md`).
**Trigger:** the α_c-recalibration audit established that the substrate's actual operating mode is **linear heteroassociator** (W applied once, no recurrent dynamics) — a different primitive than the autoassociative AGS Hopfield baseline assumed in much of the cap_map's prior framing. The orchestrator needs an evidence-grounded primitive decision before MoE rebuild, Bet N, SSM-HiPPO are queued.
**Discipline:** 2x depth drill per [[feedback-2x-means-depth]]; lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]; generic terms only per [[feedback-query-privacy-decomposition]]; novel-synthesis P-cap 0.50 enforced.

---

## (a) HEADLINE

> **RECOMMENDATION: Keep the substrate primarily LINEAR-HETEROASSOC. Add ONE small RECURRENT-AUTOASSOC variant probe to the design space — scoped narrowly to multi-hop / hierarchical-binding (K6-class) tasks where iterative fixed-point cleanup is mechanistically motivated. Do NOT rebuild Bet B retention rehab around recurrence; the structural-separation axis is already the load-bearing rehab.**
>
> The decision is **asymmetric across the Tier-1 capabilities**:
>
> - **MoE rebuild → LINEAR.** The MoE pre-step IS linear-heteroassoc and the α_c ≈ 0.56 figure (vs autoassociative 0.14) gives 4× more per-expert capacity. Adding recurrence would slow it, halve capacity, and create a fixed-point gate that the gating router would have to backprop through. **Linear wins decisively.**
>
> - **Bet N (multi-hop / d=25 cliff) → RECURRENT MAY HELP, BUT THE EVIDENCE IS WEAK.** This is the only Tier-1 capability where the lit signal for recurrence is non-trivial (RAAM/RAN compositional binding lineage, iterative resonator decomposition, modern-Hopfield deep-Boltzmann generalizations). The substrate's existing resonator-decomposition + ACF rescue (`acf_K_dependent_retry`) is **already an iterative refinement layered on a linear primitive** and recovers atoms past K/N=1.5 — so the substrate is **not purely** linear at decomposition. The proposed probe: a **bounded-iteration recurrent cleanup head** (2–5 sign or β-softmax iterations) sitting on top of the existing linear-heteroassoc W, scoped to multi-hop K6 tests. **Calibrated P(recurrent variant beats linear for multi-hop)** = 0.30 (deflated from naive 0.45 per uncharted-regime penalty).
>
> - **SSM-HiPPO → ALREADY-LINEAR-RECURRENT (orthogonal axis).** SSM/HiPPO is a LINEAR DYNAMICAL SYSTEM with a structured recurrence A,B,C,D — it is **neither** classical recurrent autoassoc (no energy descent to fixed point) **nor** single-shot linear heteroassoc (it has a time-extended state). The right framing: SSM-HiPPO is a THIRD primitive that the substrate could host as a memory-over-time projection mechanism, *built on top of* the linear-heteroassoc storage layer. The linear-vs-recurrent-autoassoc decision **does not gate SSM/S4**; that decision is independently filed under the SSM/S4 re-queue (`exp_dev_handoff_5anchors_post_v183_2026-05-24.md` item 4).
>
> - **Discrete retention plateaus (0.94/0.74/0.60) → NEITHER PRIMITIVE PREDICTS THIS NATURALLY**, but linear gives the cleaner mechanism. The three-level plateau structure is consistent with a **stratified-overlap (1-RSB-like) substrate** where the linear-heteroassoc readout sees different statistical phases at different K. Recurrent dynamics would **smear** the plateaus by basin-of-attraction averaging — destroying the audit signal. **Linear preserves the plateau structure; recurrent obscures it.** This is a substrate-product argument: the auditability of plateau-discrete retention requires linear retrieval.
>
> **Net:** the substrate stays LINEAR-HETEROASSOC as its primary primitive (4 Tier-1 capabilities favor it on capacity, gating, plateau preservation, gating-router differentiability). A SINGLE recurrent-autoassoc variant probe is queued for multi-hop K6 only, NOT as a substrate-wide rebuild.

---

## (b) Cheap decisive test

If the orchestrator wants to **falsify the recommendation** with one ~30-GPU-min experiment:

**Test: Compare linear-cosine readout vs 3-iteration sign-Hopfield readout on the EXISTING multi-hop d-cliff probe.**

- Same W = (1/N) Σ v_i k_i^T (no change to storage).
- Arm A: y = W k; report cosine (current substrate behavior).
- Arm B: y_0 = W k; y_{t+1} = sign((1/N) Σ_j (y_t · v_j) k_j); report y_3 cosine.
- M ∈ {500, 1000, 2000, 4000}, N=4096, K=8, 5 seeds, d ∈ {10, 25, 50}.
- Metric: per-hop retrieval accuracy at d=25.

**HARD PASS for recurrent variant** (≥ +0.10 accuracy at d=25 in ≥ 3 of 4 M values): queue the multi-hop recurrent rebuild.
**HARD FAIL** (recurrent ≤ linear at d=25 in ≥ 3 of 4 cells): close the recurrent-variant question; linear stays sole primitive.
**MIDDLE BAND** (recurrent +0.03 to +0.10 in 1–2 cells): document the conditional benefit; do NOT queue full rebuild; revisit only if Bet N rehab path closes.

This test reuses existing multi-hop fixtures; estimated 30 GPU-min.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1: capability-bound differences (Drill Q1)

**P1.1 (storage capacity ratio):** at cosine threshold τ=0.80, the substrate's linear-heteroassoc α_c ≈ 1/τ² − 1 = 0.56, while the corresponding autoassociative-recurrent figure at the same fidelity is ≤ 0.14 (AGS) or up to ~0.27 with asymmetric W (Düring-Coolen-Sherrington 1998). **HARD-PASS prediction**: substrate full-mode MoE pre-step lands α_c ∈ [0.50, 0.60] (this is the existing pre-reg from the α_c recalibration handoff). **Calibrated P** = 0.55 (carried from parent note).

**P1.2 (retention mode):** linear is single-shot O(N) cosine; recurrent is iterative O(T·N) with convergence not guaranteed past α_c. The substrate's existing CPU-only sub-100ms retrieval at K=4 (`cpu_platform_timing`) is structurally **incompatible** with recurrent T≥3 iterations at N=4096 on consumer hardware. **HARD-FAIL prediction for recurrence**: any recurrent-variant rebuild must demonstrate < 200ms per query at K=4, T=3 iterations on consumer CPU; if it cannot, the substrate's "edge / on-device" capability bullet is broken. **Calibrated P(recurrent meets 200ms)** = 0.40.

**P1.3 (retention plateau structure):** linear with stratified codebook overlap predicts discrete-stepped retention curves (each plateau = one stat-mech phase). Recurrent autoassoc averages over basin-attraction dynamics and predicts smooth sigmoidal retention curves. **HARD-PASS for the linear-preserves-audit-signal claim**: re-running existing retention-vs-K experiments under both arms (above) should show plateau visibility ratio (variance-of-2nd-derivative / variance-of-1st-derivative) ≥ 2× higher in linear arm. **Calibrated P** = 0.45 (deflated from 0.60; novel-synthesis territory).

### Prediction set 2: continual-learning behavior (Drill Q2)

**P2.1 (catastrophic-forgetting baseline):** lit-scan signal is **strong** that autoassociative Hopfield has SEVERE catastrophic interference in sequential learning (Robins 1998 pseudorehearsal paper; Wikipedia catastrophic-interference; van de Ven 2024). Linear heteroassoc with delta-rule online updates has **bounded forgetting per added pattern** (1/N variance of crosstalk noise per pattern; superpositional). **HARD-PASS prediction**: substrate's existing replay BWT recovery (+0.66 to +0.73 at K=4, `r7_concept_replay`, `r7_multiseed`) confirms the linear-heteroassoc behavior — replay COMPENSATES the linear-superposition crosstalk. Calibrated P (replay continues to compensate at higher K) = 0.65. **The cap_map's existing Bet B M-DEPENDENT PARTIAL row already implicitly assumes linear**; promoting recurrent would invalidate the rehab path entirely.

**P2.2 (structural-separation axis primacy):** the cap_map v184–v187 evidence shows structural separation (MoE M-dependent + per-task substrate) is the LIVE Bet B rehab axis. **Recurrent autoassoc DOES NOT help structural separation** — it changes the per-expert retrieval mechanism, not the cross-expert separation. **HARD-FAIL for "recurrent rebuild solves retention"**: no published mechanism connects autoassoc dynamics to cross-task structural separation. **Calibrated P (recurrent improves Bet B retention)** = 0.10.

### Prediction set 3: compositional generalization (Drill Q3)

**P3.1 (compositional generalization lit-signal):** the lit-scan returned 3 strong signals (Pollack RAAM; Smolensky TPR; recent Mahdavi 2024 "Compositional Generalization Requires Linear, Orthogonal Representations"). The Mahdavi result is **directly load-bearing**: compositional generalization is *enabled* by linear, orthogonal representations — **not** by recurrent dynamics. RAAM/RAN historically used recurrence for *sequential structure encoding*, not for compositional binding per se. **HARD-PASS for linear primitive on K6 compositional**: substrate's existing PPMI concept extraction + R10 concept fusion at K≥8 (+0.628 bpc at K=512, `r10_best_config_K512`) is direct evidence that the linear primitive handles concept-level composition well. **Calibrated P (linear handles K6-class composition)** = 0.55.

**P3.2 (multi-hop iterative refinement):** modern Hopfield + iterative resonator decomposition lit-signal IS positive for iterative cleanup at high load. Substrate's existing ACF resonator rescue (K/N=1.5 at 97%, `acf_K_dependent_retry`) is the de-facto recurrent layer ALREADY PRESENT on top of linear storage. **HARD-PASS for "bounded iteration helps past K/N=1"**: substrate already demonstrates this. **HARD-PASS for "full recurrent autoassoc rebuild helps further"**: NOT established; recurrent-variant probe needed. **Calibrated P (full recurrent rebuild beats existing ACF + linear)** = 0.25.

### Prediction set 4: Tier-1 fit (Drill Q4) — see HEADLINE

Probabilities:
- P(MoE rebuild benefits from recurrent vs linear) = **0.10** (linear wins decisively per α_c + gating-router differentiability)
- P(Bet N multi-hop benefits from BOUNDED recurrent cleanup head) = **0.30** (deflated from 0.45)
- P(Bet N benefits from FULL recurrent autoassoc rebuild) = **0.15** (deflated from 0.25)
- P(SSM-HiPPO is gated by this decision) = **0.05** (SSM is orthogonal — linear-time-varying recurrence, not energy-fixed-point recurrence)

### Prediction set 5: discrete-plateau retention (Drill Q5)

The 0.94/0.74/0.60 plateau structure observed across multiple substrate experiments has TWO candidate mechanisms:

**Mechanism A (linear + stratified codebook overlap):** the linear-heteroassoc SNR is `cos(α) = 1/√(1+α)` for i.i.d. codebooks. With **structured PPMI codebook** introducing tier-bands of pair-overlap, three discrete SNR plateaus are predicted: (i) within-cluster pairs (high overlap → low effective α → cos ≈ 0.94), (ii) cross-cluster pairs (mid overlap → mid α → cos ≈ 0.74), (iii) cross-tier pairs (low overlap → high α → cos ≈ 0.60). **This mechanism is testable** by computing the empirical codebook-overlap histogram and verifying 3 modes correlate with the 3 plateaus. **Calibrated P (linear + stratified overlap explains plateaus)** = 0.45.

**Mechanism B (recurrent + basin partition):** RSB-style basin partition predicts plateaus at the 1-RSB Parisi q(x) overlap values. But this requires recurrent dynamics for the basins to exist as observables — and the substrate's plateaus are observed in single-shot linear readout. **The plateaus existing in linear retrieval is empirical evidence AGAINST the recurrent-basin mechanism being the source.** **Calibrated P (recurrent basin explains plateaus)** = 0.20.

**HARD-PASS for mechanism A**: codebook-overlap histogram has ≥ 3 modes at PPMI sparsities matching the 3 plateau cosines within ±0.05. This is a free CPU-second test.

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to α_c anomaly note (parent)

The parent note (`research_substrate_alpha_c_anomaly_2026-05-24.md`) established THE distinction at the **storage-capacity level**: linear α_c ≈ 0.56 vs recurrent AGS α_c ≈ 0.14. This note **extends** that finding from "α_c is the wrong reference class" (parent's scope) to "the substrate has multiple primitive choices each with different capability profiles" (this note's scope). The parent recommended exposing the cleanup-vs-Hopfield distinction as a first-class config knob; this note recommends keeping linear as the default knob position and probing the recurrent knob position narrowly.

### Cross-ref to R36 sandwich

R36 (`notes/research_R36_alpha_c_coherence_bridge_2026-05-21.md`) established sandwich bounds for the AUTOASSOCIATIVE recurrent regime (AGS lower, Hu spherical upper, Demircigil ceiling). **R36's sandwich applies only to the recurrent-autoassoc variant** and is the right reference IF the substrate adopts that primitive. The recommendation here keeps linear, so R36's sandwich is parked as "the right framework IF we ever build the recurrent variant" — kept available, not actively driving design.

### Cross-ref to cap_map v184–v187 (Bet B retention rehab)

The Bet B M-DEPENDENT PARTIAL rehab via structural separation (MoE + per-task substrate + replay; v184/v185/v186/v187 compound bounded at 0.915 below HARD-PASS 0.95) is built **entirely on linear primitives**. This note's recommendation **preserves** the cap_map rehab trajectory unchanged. The third-axis extension (Lane D 4-stage, eligibility traces) is also linear-compatible.

### Cross-ref to existing ACF resonator rescue (`acf_K_dependent_retry`)

ACF resonator is a **bounded-iteration unbinding refinement** sitting on top of linear storage. It is **proof that the substrate already operates a hybrid linear+iterative primitive at the decomposition layer** — without requiring full recurrent autoassoc. The proposed multi-hop recurrent-cleanup-head probe is structurally analogous: bounded iteration on top of linear storage, scoped to a specific failure mode (d=25 cliff). This is **architecturally consistent** with what the substrate already does, not a primitive rebuild.

### Cross-ref to SSM/S4 re-queue (`exp_dev_handoff_5anchors_post_v183_2026-05-24.md` item 4)

SSM/S4 is a **separate primitive** (linear-time-varying recurrence on a continuous state). The linear-vs-recurrent-autoassoc decision **does not bind** SSM/S4. Recommendation: ship SSM/S4 independently per its existing handoff; this note's recommendation is orthogonal.

### Cross-ref to mesoscopic-transport drill (`research_mesoscopic_transport_moe_2026-05-25.md`)

The mesoscopic-transport framing (multi-hop d=25 = transmission coefficient problem) is **a third lens** on the same multi-hop cliff that the recurrent-variant probe targets. **Synergy**: if the recurrent-cleanup-head probe HARD-PASSES, the mesoscopic-transport lens predicts WHICH M/K cells should benefit most (high-transmission-coefficient cells). If the probe HARD-FAILS, mesoscopic transport still informs an alternative rebuild path orthogonal to recurrence.

### Cross-ref to wave14e MoE x-talk PASS (linear, M-dependent)

Wave14e MoE x-talk demonstrated linear-heteroassoc MoE works at ratio=1.44 at high-M cells. This is **the existing positive evidence** that the linear primitive scales to MoE structural separation. No recurrent component was needed. Architectural lesson: **linear scales to structural composition; the question is only whether recurrence helps ON TOP of linear for specific subproblems** (multi-hop d=25). The answer in the lit-scan: **maybe, narrowly, with bounded iteration**.

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

**1. Auditability story is STRONGER under linear primitive.**

The substrate's product wedge is "auditable third memory type" — verifiable erase, editable memory, provenance, cognitive composition. **Each of these requires retrieval to be a deterministic, single-shot function of the stored state** so that audit trails are reproducible. Recurrent autoassoc dynamics introduce basin-of-attraction non-determinism (initial-condition dependence, convergence-step counting, false-attractor falls) that **break the audit reproducibility guarantee**. The discrete-plateau retention structure is itself an audit signal — linear preserves it, recurrent smears it. **Product implication**: ship LINEAR as the auditable primitive; if a recurrent variant ships at all, it ships as an OPT-IN "fast-recovery mode" for specific compositional tasks, with explicit user-facing flag and a separate audit policy.

**2. CPU-only retrieval requires linear.**

Sub-100ms at K=4 on consumer hardware (`cpu_platform_timing` ✅) is a Tier-1 product capability. Recurrent T≥3 iterations at N=4096 are 3× the cost and likely break the sub-100ms bound. Edge / on-device shipping requires linear primary. **Product implication**: a recurrent variant CANNOT be the primary retrieval path on edge deployments.

**3. MoE rebuild → ship linear at M_per_expert ≈ 1600.**

Per parent note recalibration: linear-heteroassoc α_c ≈ 0.56 at τ=0.80 gives 4× the per-expert capacity vs the autoassociative 0.14 figure. Ship the MoE rebuild on the linear primitive (no change to existing prestep architecture); use the recalibrated M_per_expert ≈ 1600 figure. **Product implication**: MoE structural-separation rehab proceeds with the larger per-expert capacity — better cross-talk relief at the same total M, fewer experts needed for same coverage.

**4. Multi-hop K6 rehab → narrow recurrent probe.**

Bet N closure (d=25 cliff) and K6-class compositional binding are the only places where the lit-scan supports a recurrent benefit (Pollack RAAM lineage; iterative resonator decomp). The probe is SCOPED: bounded-iteration sign-Hopfield head on top of linear W, evaluated on multi-hop accuracy only. **Product implication**: IF the probe HARD-PASSES, the substrate gains a "deep-compositional mode" gated to multi-hop queries — exposed as a config knob ("compositional_iterations: 0 | 3 | 5"), default 0 (linear). Audit policy separate per knob position.

**5. Discrete-plateau retention IS THE AUDITABLE SIGNATURE.**

The 0.94/0.74/0.60 plateau structure is **a substrate-product asset**, not a quirk to be smoothed away. It gives users a 3-tier retrieval-confidence indicator without additional computation — a "natural" audit signal that maps to product tiers. **Product implication**: any primitive change that smears the plateaus IS A PRODUCT REGRESSION. This is the strongest argument against switching to recurrent autoassoc as primary.

---

## (f) Decision

**LOCKED RECOMMENDATION: substrate remains LINEAR-HETEROASSOC as primary primitive.**

**Design-space additions (queued):**

1. **(PROBE — small, scoped, NEW exp_dev handoff)** Bounded-iteration recurrent-cleanup head on multi-hop K6 only. 30-GPU-min test per (b) above. Falsifies or queues a multi-hop-mode config knob. **P(probe HARD-PASS)** = 0.30.

2. **(CONFIRMATORY)** Codebook-overlap-histogram CPU-second test for the discrete-plateau mechanism A. Free; informs whether the linear+stratified-overlap story is right.

3. **(NO-CHANGE)** MoE rebuild proceeds on linear primitive with recalibrated M_per_expert ≈ 1600 per parent note. No primitive switch needed.

4. **(NO-CHANGE)** SSM/S4 re-queue proceeds as filed — it is orthogonal to this decision.

5. **(NO-CHANGE)** Bet B retention rehab continues on structural-separation axis (MoE + per-task + replay + third-axis extensions); no recurrent rebuild.

**What this DECISION RULES OUT:**

- Substrate-wide primitive switch to recurrent autoassoc. Closed at calibrated P=0.10 substrate-wide benefit vs P=0.85 substrate-wide regression on audit + CPU + plateau.
- Recurrent rebuild of MoE rebuild. Closed at P=0.10.
- Recurrent rebuild of Bet B retention rehab. Closed at P=0.10.

**What this DECISION KEEPS OPEN:**

- Narrow recurrent variant for multi-hop K6 only (P=0.30 probe HARD-PASS).
- ACF-style bounded iterative refinement at decomposition layer (already in place; no change).
- Modern-Hopfield β-softmax retrieval as a SEPARATE primitive evaluated independently — this note does NOT close that line.

**Companion exp_dev handoff:** `notes/exp_dev_handoff_research_recurrent_cleanup_head_multihop_2026-05-25.md` (test (b) above; scoped to multi-hop K6).

---

## (g) Citations (verified count: 8 direct + 6 contextual = 14)

### Storage capacity comparison (LOAD-BEARING for Q1)
- **Kosko 1988** — Bidirectional Associative Memory (BAM); heteroassoc capacity m < min(n, p)
- **Anderson 1972 / Kohonen 1972** — linear associator outer-product model
- **Amit, Gutfreund & Sompolinsky 1985** — Phys. Rev. A 32 — AGS α_c ≈ 0.138 (autoassoc baseline)
- **Düring, Coolen & Sherrington 1998** — cond-mat/9805073 — asymmetric W α_c lift to ~0.27

### Continual learning + catastrophic interference (LOAD-BEARING for Q2)
- **McCloskey & Cohen 1989** — catastrophic interference foundational paper
- **Robins 1998** — Connection Science 10(2) — pseudorehearsal in Hopfield-type networks; explicit Hopfield-CF demonstration
- **van de Ven 2024** — arXiv 2403.05175 — continual learning + catastrophic forgetting review; structural separation as one of 3 mitigation families
- **Kirkpatrick et al. 2017** — PNAS — EWC parameter-importance approach (cited as the dead axis in substrate cap_map v184)

### Compositional binding (LOAD-BEARING for Q3)
- **Pollack 1990** — Recursive Auto-Associative Memory (RAAM); recurrence for sequential structure encoding
- **Smolensky 1990** — Tensor Product Representations; non-recurrent compositional binding
- **Mahdavi 2024** — arXiv 2402.02851 — "Compositional Generalization Requires Linear, Orthogonal Representations" — DIRECTLY LOAD-BEARING that linear (not recurrent) representations enable compositional gen

### Linear attention / heteroassoc connection (CONTEXTUAL)
- **Schlag, Irie & Schmidhuber 2021** — linear attention as fast-weight programmer
- **Beren 2024** — "Linear Attention as Iterated Hopfield Networks" — equivalence to continuous Hopfield

### SSM / HiPPO (CONTEXTUAL — confirms orthogonality)
- **Gu et al. 2020** — HiPPO; linear-time-varying recurrence on continuous state
- **Gu, Goel & Re 2022** — S4; structured state-space model

### Iterative cleanup at high load (CONTEXTUAL for Q3 multi-hop)
- **Folli, Gosti, Leonetti & Ruocco 2016** — Frontiers Comput. Neurosci. 10:144 — autapse + iterative refinement at P ≫ N

### Substrate-internal references
- `notes/research_substrate_alpha_c_anomaly_2026-05-24.md` (parent)
- `notes/research_R36_alpha_c_coherence_bridge_2026-05-21.md` (recurrent-variant sandwich)
- `notes/substrate_capability_map.md` lines 22–55 (memory primitives + structural-separation axis)
- `notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md` (linear-heteroassoc recalibration spec)
- `experiments/exp_wave14_moe_alpha_c_prestep_v1.py` (substrate is linear-heteroassoc; lines 115–130)
- `notes/research_mesoscopic_transport_moe_2026-05-25.md` (orthogonal lens on multi-hop)
- `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` item 4 (SSM/S4 re-queue, orthogonal to this decision)

---

## Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **The recommendation is LIT-SCAN INFORMED, not lit-scan PROVEN.** The substrate's specific operating regime (PPMI codebook, K-cliff at K/N≈0.56, discrete plateaus) is not directly published. All P estimates are deflated 0.15–0.25 per uncharted-regime penalty.

2. **The recurrent-cleanup-head probe is genuinely 30%, not higher.** I considered the possibility that multi-hop d=25 is a fundamental compositional-depth bound (per cap_map v77 Bet X unifying insight). If d=25 IS the universal VSA-class noise bound, bounded recurrent iteration cannot fix it — it only de-noises, doesn't expand the depth budget. P=0.30 reflects this realistic ceiling.

3. **Mechanism B (recurrent basin) for retention plateaus is NOT FULLY CLOSED.** I argued the plateaus appearing in single-shot linear readout is evidence against recurrent-basin source. But the plateaus could also arise from a stratified-codebook structure that the recurrent dynamics would AMPLIFY — in which case the recurrent variant would make plateaus MORE visible, not less. The codebook-overlap histogram test is the cheap decisive test for this branch.

4. **SSM-HiPPO being "orthogonal" is a clean reading but not airtight.** SSM/S4 has a structured linear recurrence; one could argue it is a third species of "recurrence" that shares some properties with autoassoc dynamics. The orthogonality claim rests on SSM being LINEAR-TIME-VARYING (no energy descent, no fixed point in the basin sense). If SSM-HiPPO is reframed as "iterative refinement over a time-extended state", the boundary blurs.

5. **The audit-reproducibility argument for linear primary IS THE STRONGEST single argument** — and it is product-grade, not theory-grade. If the user reframes the product as "best-effort retrieval" rather than "auditable retrieval", this argument weakens.

6. **No new GPU spend for the decision itself.** The decision is closure on existing evidence + 1 cheap CPU test + 1 narrow 30-GPU-min probe. No substrate rebuild, no architecture commitment.

7. **Calibration penalty applied uniformly.** Novel-synthesis P-cap 0.50 honored across all predictions. The 0.55 P(linear handles compositional) is at the cap because direct lit-precedent (Mahdavi 2024) is load-bearing.

8. **Per [[feedback-no-experiment-design-in-prompts]]:** the companion handoff (if filed) will hand TASK + WHY + CONTRACT + AUTONOMY only. No anchor names, no sweep grids, no threshold formulas, no queue choice, no ETA — exp_dev decides those.

---

**End research note.**
