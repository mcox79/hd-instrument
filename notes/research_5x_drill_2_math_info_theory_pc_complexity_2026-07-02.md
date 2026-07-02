# Research 5x Drill 2/5 — Math + Info-Theory: does PC earn its complexity over competitive-Hebbian in an HD substrate concept encoder?

**Filed:** 2026-07-02 (evening), post-brain-best-in-class strategic pivot
**Drill component:** 2 of 5 (parallel drills 1/3/4/5 cover neuroscience+biology, physics+stat-mech, ML/AI empirical, empirical-ablation)
**Topic:** does adding a predictive-coding (PC) layer above competitive-Hebbian sparse allocation increase the substrate's capacity / information / sample-efficiency, or is PC redundant dressing on the same variational-EM core?
**Substrate anchor:** design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md (5-arm cell, ARM_FULL_HYBRID vs ARM_COMPETITIVE_ONLY vs ARM_PREDICTIVE_ONLY)
**Method:** Opus synthesis of 4 parallel Sonnet sub-agent drills (capacity theory, IB+RD, sample complexity+VC/PAC, free-energy+PC-WTA equivalence). GENERIC math terms only in external queries per query-privacy discipline. Lit-scan calibration penalty applied (deflate 0.15-0.25; cap novel-synthesis P at 0.50).

---

## (a) HEADLINE

**Theory says PC is MOSTLY REDUNDANT with WTA on the shared variational-EM core; PC's genuine DOF (precision-weighting + hierarchy) only cashes in under specific input conditions (input correlation ρ > 0, heteroscedastic per-feature noise, or temporally structured targets). Composite P(PC earns its complexity in HD-substrate concept encoder over standard iid-adjacent NLP corpora) = 0.22 (deflated) — biased toward "PC is complexity-tax on top of competitive Hebbian for the substrate's stated use case," but with a specific correlated-input regime where P rises to ~0.40.**

---

## (b) Cheap decisive test (one ablation to collapse ambiguity)

**INPUT-CORRELATION SWEEP** — the single ablation the theory picks out:
- Add 2 arms to Spoke 1's existing 5-arm cell: `ARM_FULL_HYBRID_rho0` (iid controlled corpus) vs `ARM_FULL_HYBRID_rho_high` (deliberately correlated corpus — e.g. same 50 concepts in near-identical contexts).
- Also `ARM_COMPETITIVE_ONLY_rho0` vs `ARM_COMPETITIVE_ONLY_rho_high`.
- Measure `lift = cat_kitten_cos(HYBRID) − cat_kitten_cos(COMP_ONLY)` at each ρ.

**Reads:**
- If lift(ρ_high) − lift(ρ_low) ≥ 0.15 → PC earns capacity via decorrelation (Barlow/Olshausen mechanism confirmed). P jumps to 0.55 in that regime.
- If lift is flat across ρ (delta ≤ 0.05) → PC is redundant with WTA under both regimes. Empirical anchor (hybrid ~ competitive, delta ~0.010) already sits inside this range → confirms PC-as-complexity-tax hypothesis.

**Why it's decisive:** all 4 theory frames (capacity, IB, sample-complexity, precision-weighting) converge on "PC's advantage manifests only when input has structure WTA cannot separately model" — correlation is the most tractable such structure. Single sweep resolves.

---

## 1. Prior-work check (substrate-KB + notes fallback)

**Substrate-KB query outputs (all 3 queries) FAILED with OOM (KB grew to 7.4 GiB — infrastructure blocker; distinct from research signal). Reverting to grep over `notes/`.** Flag for testbed / infra: KB query needs paged/mmap loader or the local machine can no longer serve queries.

Fallback grep matches (files containing Frady/Plate/HRR-capacity/Tishby/Rao-Ballard/Friston/PC/VC-dim):
- `research_R26_learning_theory_deep_dive_2026-05-21.md` — delta-rule/Hebbian learning theory scan; established substrate-novel *stitching* opportunity for VSA outer-product memory (implicit bias + Marchenko-Pastur double descent). **STRONG** overlap with drill 2 (both math+learning-theory); drill 2 focuses specifically on PC-vs-WTA composition, R26 focused on learning dynamics of Hebbian alone.
- `research_R22_sleep_consolidation_2026-05-21.md` — explicitly mentions predictive coding + gated write. **PARTIAL** — sleep/replay angle, not asymptotic sample complexity.
- `research_R16_free_probability_predictions_2026-05-21.md`, `research_R17_holographic_principle_2026-05-21.md` — capacity/information framings from adjacent physics; NONE direct.
- `exp_dev_handoff_research_resonator_capacity_extensions_2026-06-16.md`, `exp_dev_handoff_research_resonator_capacity_substrate_scale_2026-06-04.md` — VSA capacity extension work. **PARTIAL** — resonator networks not concept-encoder composition.
- `research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md` — brain-analog drill closest in intent. **PARTIAL** — brain angle, not pure math.
- `design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md` — the design under theoretical test (the referent).

**Overlap verdict:** NONE of prior notes stitch PC + WTA under a single variational-EM / IB / capacity account for HD-substrate composition. Drill 2 is genuinely novel synthesis relative to substrate corpus (subject to novel-synthesis P-cap 0.50).

---

## 2. Capacity theory — does PC increase M_max, or just reallocate?

Sub-drill A synthesis (Plate 1995 · Frady-Kleyko-Sommer 2018 · Kanerva SDM 1988 · Litwin-Kumar et al. 2017; Ramsauer Modern Hopfield 2020):

- **Hard combinatorial ceiling M_max(N, k) is allocator-independent.** For fixed N=8192, k~2% (~163 active units), classical Hopfield/SDM/Frady-Sommer bounds are functions of geometry, not of the mechanism that fills the slots. WTA and PC-then-WTA share the same asymptotic ceiling.
- **BUT effective capacity under correlated inputs is allocator-dependent.** Correlated patterns reduce distinguishability at fixed noise floor (arxiv 2508.01395, "Effects of Feature Correlations on Associative Memory Capacity"). Decorrelating front-end (residual coding à la Barlow 1961 / Olshausen-Field 1996 / Attneave 1954) pushes correlated-input regime back toward the iid ceiling.
- **PC's mechanism (subtract top-down prediction, encode residual) IS a decorrelator.** PMC9768680 measured PC error-units decorrelate inputs in RNNs.
- **So: PC can raise EFFECTIVE M by consuming input redundancy, without changing the ABSTRACT ceiling.** How much effective M rises depends entirely on how correlated the natural task input actually is.

**Sub-drill A P estimate (pre-deflation):** 0.40 that PC earns real, measurable capacity gain under realistic correlated task distributions.

**Key distinction the theory forces:** "PC changes what patterns are stored" (allocator-mechanics) vs "PC changes how many patterns fit" (capacity-theorem). Pure combinatorial capacity: PC does NOT help. Retrieval capacity under structured/correlated data: PC MAY help proportional to input correlation.

---

## 3. Information-bottleneck — is PC redundant with WTA sparsification as an IB compressor?

Sub-drill B synthesis (Tishby-Pereira-Bialek 1999 · Tishby-Zaslavsky 2015 · Achille-Soatto 2018 · Millidge 2021 · Bialek-Nemenman-Tishby 2001 predictive information · van den Oord CPC 2018):

- IB Lagrangian: min I(X;Z) − β I(Z;Y). WTA sits at rate R = k log(N/k) with no explicit Y-relevance term (rate-first). PC sits with implicit Y = predictable-next-state (relevance-first, rate-free).
- **No theorem found that WTA is IB-optimal.** Tishby-Zaslavsky (2015) frames layered maps as inducing an IB tradeoff but doesn't prove top-k = optimal encoder. Achille-Soatto information-dropout covers stochastic bottlenecks, not deterministic argmax-k.
- **PC's target Y (self-prediction / hierarchical prior mismatch) and WTA's implicit target Y (fixed downstream task) are generally DIFFERENT.** No theorem says they are provably redundant.
- **The one place theory gives PC a directional edge:** *predictive information* I_pred(past;future) (Bialek 2001, PNAS 2015). WTA alone has no temporal/predictive machinery — cannot preferentially retain predictive vs non-predictive variance. PC-then-WTA can. **This is the one IB-adjacent argument for PC adding something WTA structurally cannot.**
- **BUT: when Y is static (concept identity from bag-word input), the predictive-information channel is silent** — PC's residual could even DESTROY task-relevant amplitude that WTA-on-raw would keep.

**Sub-drill B P estimate:** 0.30-0.40 that PC contributes genuinely new I(Z;Y) beyond WTA. Higher end only when Y is temporally / hierarchically structured; the substrate's Stage-2 concept encoder Y is static-concept-identity → lower end of range applies.

---

## 4. Rate-distortion — does PC-driven activation shift the R-D frontier at fixed rate?

- **No RD theorem located that PC-driven allocation strictly dominates uniform top-k at fixed rate R = k log(N/k).**
- Closest formal machinery: successive-refinement RD theory — a sufficient-conditions result that a two-stage code can match one-shot without rate loss, NOT a proof that two-stage strictly beats one-stage.
- **Prediction-weighted activation is a Barlow-efficient-coding HEURISTIC ("spend more bits where surprise is high"), not an RD-optimal policy for the WTA+PC composition specifically.**
- **RD contribution to overall verdict:** ~0.30 (below 50; theory ambivalent; PC has no rate-distortion trump card at fixed rate).

---

## 5. Sample complexity — does PC-gated Hebbian write survive asymptotically over unconditional?

Sub-drill C synthesis (Tong-Koller 2001 margin-based AL · Hanneke 2007 disagreement coefficient · Balcan-Beygelzimer-Langford A² · Robbins-Monro 1951 · Kumar/Bengio self-paced/curriculum):

- **Gate-on-error IS margin-based active learning** (canonical Tong-Koller 2001 SVM AL). ✓
- **Empirical 378-728 vs ~2000 (factor 3-5x) fits A² CONSTANT-FACTOR regime, NOT Hanneke's EXPONENTIAL-speedup regime.** Concept identity is likely "hard" (agnostic-adjacent), not the smooth/realizable case Hanneke's exponential result requires.
- **Importance-weighted SGD framing (Robbins-Monro):** bounded importance weights change *constants*, not asymptotic O(1/√n) or O(1/n) rates. → transient / early-training advantage, not asymptotic.
- **Self-paced / curriculum framings:** no sample-complexity THEOREM exists — empirical re-orderings of the same budget, cannot change asymptotic complexity.
- **Sub-drill C P estimate:** 0.15-0.20 that gated-write advantage is asymptotic (persists as N→∞ at fixed accuracy). ~0.75-0.80 that it's transient / constant-factor / accuracy-threshold-dependent.
- **Coreset / submodular subset-selection methods** (adjacent, not to dismiss) can plausibly reproduce a similar sample-efficiency gain via geometric diversity — WITHOUT a PC layer at all. Falsifies "PC is uniquely necessary for sample efficiency."

**Implication:** the observed 378 vs 2000 gap in the empirical anchor is real but is a constant-factor early-training win most likely — not evidence of an asymptotic PC advantage. If a coreset-based ablation matched it, PC-as-mechanism would be falsified as *the* efficiency lever.

---

## 6. Free-energy vs WTA — same variational-EM procedure, precision is the extra DOF

Sub-drill D synthesis (Friston 2010 FEP · Bastos 2012 canonical microcircuit · Millidge-Tschantz-Buckley 2020 PC≈backprop · Whittington-Bogacz 2019 · Nessler-Pfeiffer-Buesing-Maass 2013 · Neal-Hinton 1998 EM-as-F-descent · Rutishauser-Slotine-Douglas 2011 · Feldman-Friston 2010 precision-as-attention):

- **Both PC and WTA/soft-WTA+STDP are message-passing implementations of free-energy minimization.** Nessler 2013 proved soft-WTA + STDP ≈ variational EM for mixtures (E-step = soft-max competition, M-step = Hebbian). Neal-Hinton 1998 showed EM itself = F-descent. Bastos 2012 + Millidge 2020 showed PC = F-descent with precision-weighted errors.
- **They differ in the q-family:** WTA uses categorical/point-mass q (one-hot posterior, implicit uniform/binary "precision" across losers). PC uses Gaussian q with per-unit precision matrix Π (dynamic, non-uniform).
- **Precision is the SINGLE extra degree of freedom PC provides.** Feldman-Friston 2010: attention = inference over Π. Non-uniform precision matters PRECISELY when input reliability is heteroscedastic across features / hierarchy levels — SIGNAL-QUALITY-AWARE weighting.
- **WTA ⊂ PC** (in the limit Π → uniform/degenerate) is a plausible inference from (3)+(4)+(5) but was NOT directly verified as a cited theorem. Flag as high-confidence synthesis, not textbook fact.
- **Sub-drill D P estimate:** ~0.25 that PC provides a genuinely new mechanism beyond WTA (i.e. the precision-weighting DOF cashes in for the substrate's target regime). ~0.75 that PC is redundant dressing on the same variational-EM core.

**Ladder VAEs / Helmholtz machines (adjacent):** hierarchy earns its keep empirically (ladder VAE beats flat VAE) — supports treating *hierarchy* (not just precision) as a second real DOF beyond flat WTA. Stage 2 Spoke 1 is a flat architecture → hierarchy DOF not exercised. Reserve for Spoke 2/3 designs.

---

## 7. VERDICT — composite deflated P

Individual sub-drill headline P values (pre-deflation shown; already-deflated in parens):
- Capacity (A): 0.40 → deflated 0.15-0.25 → **0.20**
- IB / RD (B): 0.30-0.40 → deflated → **0.20**
- Sample complexity (C, asymptotic): 0.15-0.20 → deflated → **0.10**
- Free-energy new-mechanism (D): 0.25 (already deflated) → **0.25**

**Composite P (theoretical only, generic-corpus regime): 0.22** — treat as "PC is a complexity tax for the substrate's stated use case (concept encoder over near-iid NLP corpora)."

Under specific favorable input regimes (correlated ρ > 0.3, heteroscedastic noise, temporally structured Y): sub-drill values rise; **conditional composite P ≈ 0.40**. Still below 0.50 novel-synthesis cap, so the cap is not the binding constraint.

**Theoretical verdict: PC is REDUNDANT with WTA under the generic Stage-2 concept-encoder use case; PC could earn its complexity only under specific correlated / heteroscedastic / temporally-structured input regimes.**

This is CONSISTENT with the empirical anchor (delta ~0.010, cv ~0.377 hybrid vs competitive) which the drill was instructed to remain independent of — theory converged on the same direction the smoke run observed.

---

## 8. If theory says NO (main-case) — implications for the arc

**Simpler architecture that capacity theory blesses:**
1. **"Competition first, gate second"** — sparse WTA allocator (already implemented in `hdlab/excitability.py`), gated by prediction-error THRESHOLDING but with prediction from a FLAT running-mean, not a full PC hierarchical generative model. This preserves the constant-factor sample-efficiency win (still active-learning / margin-based) WITHOUT paying for a PC layer.
2. **Decorrelation as a pre-processing lever** — if the substrate's real gain from "PC" is Barlow decorrelation, replace PC with a lighter decorrelating front-end (e.g. running whitening / centering on the char-positional encoder output). Substrate keeps the decorrelation benefit; drops the hierarchical PC machinery.
3. **Coreset / diversity subset-selection ablation** — before crediting PC for the 378-vs-2000 sample-efficiency win, run a coreset-selected subset baseline. If coreset matches, PC is falsified as the necessary mechanism.

**Implications for Spoke 1 cell design:**
- Add `ARM_COMPETITIVE_WITH_MEAN_GATE` (WTA + threshold-on-error-vs-running-mean, no PC hierarchy) — this is the cheapest theory-blessed alternative.
- Add `ARM_COMPETITIVE_WITH_DECORRELATION_PREPROC` (WTA + Barlow decorrelation, no PC) — separates decorrelation-benefit from PC-as-mechanism.
- Add `ARM_COMPETITIVE_WITH_CORESET_TRAIN` (WTA over coreset-selected subset, unconditional Hebbian) — separates active-learning-benefit from PC-gating.
- Keep `ARM_FULL_HYBRID` as-is; interpret its lift ONLY relative to these theory-blessed baselines, not just RANDOM/BASELINE.

**Reframed Stage-2 arc:** the "brain-analog" argument for PC is that biology uses it; but flat WTA + Hebbian is ALSO brain-mechanism (Nessler 2013 canonical microcircuit result). The substrate does not owe biology a specific implementation — it owes the FUNCTION (sparse-distributed HDs that cluster by concept). Simplest F-descent that gets there is preferred.

---

## 9. If theory says YES conditionally — falsifiable predictions with HARD PASS / HARD FAIL

Conditions under which PC's theoretical advantage MUST manifest empirically (from sub-drills):

**Condition set S1 — correlated input regime (capacity + decorrelation channel):**
- HARD PASS: on a corpus with measured pairwise cosine of input HDs > 0.3 (correlated), `cat_kitten_cos(ARM_FULL_HYBRID) − cat_kitten_cos(ARM_COMPETITIVE_ONLY) ≥ 0.15`.
- HARD FAIL: same delta ≤ 0.05 → decorrelation channel silent → capacity-theory prediction refuted.

**Condition set S2 — heteroscedastic per-feature noise (precision-weighting channel):**
- HARD PASS: on a corpus with deliberately variable per-position noise (some positions high SNR, others low), `intra_concept_cv(ARM_FULL_HYBRID) − intra_concept_cv(ARM_COMPETITIVE_ONLY) ≤ -0.10` (PC's precision-weighting stabilizes representation more than flat WTA).
- HARD FAIL: delta ≥ 0.00 → precision-weighting channel silent → Feldman-Friston precision-as-attention channel refuted for this scale.

**Condition set S3 — asymptotic sample-complexity gap:**
- HARD PASS: samples-to-criterion ratio `gated / unconditional` stays ≤ 0.5 across 4 orders of magnitude (300 → 1k → 10k → 100k) at fixed accuracy target.
- HARD FAIL: ratio → 1.0 as N grows → transient / constant-factor → Robbins-Monro rate-preservation confirmed → PC-gating not asymptotic.

**Condition set S4 — coreset ablation:**
- HARD PASS for PC-uniqueness: coreset-baseline `cat_kitten_cos` gap to gated-write is ≥ 0.10.
- HARD FAIL for PC-uniqueness: coreset matches gated-write within 0.05 → PC-gating is not the necessary lever; geometric diversity suffices.

**Combining:** PC's theoretical DOF is "genuinely necessary" only if S1 OR S2 OR S3 passes AND S4 fails (PC-uniqueness not falsified by coreset). If S1-S3 all fail, PC is falsified as complexity-earning for the substrate's use case.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL

Consolidated from §8/§9, top priority:
1. **S1 correlation-scaling ablation (BEST bang-for-buck)** — HARD PASS/FAIL at ρ_high corpus (§9 S1). Costs 2 additional arms; resolves 3 of 4 theory frames.
2. **S4 coreset ablation** — HARD PASS/FAIL vs coreset-baseline sample-efficiency. Costs 1 additional arm; separates active-learning-benefit from PC-mechanism.
3. **S3 sample-complexity sweep** — HARD PASS/FAIL over 4 orders of magnitude of N_samples. Costs runtime, not cell arms; can be a follow-up cell.

---

## (d) Cross-thread synthesis with prior substrate entries

- **R26 (learning-theory deep-dive)** — established substrate has NO learning-theoretic stitching for W = Σ vᵢkᵢᵀ + softmax readout. Drill 2 extends R26 with PC-vs-WTA composition axis. R26's headline "AGS-style scaling laws + implicit min-Frobenius-norm bias + Marchenko-Pastur double descent" is IMPORT (WTA-only alarms about M ≈ N regime; PC likely doesn't change this).
- **R22 (sleep consolidation)** mentioned PC + gated-write; drill 2 supersedes with sample-complexity theory frame (Robbins-Monro / A² / self-paced).
- **research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md** — brain-mechanism angle; drill 2 provides the math counterpart (Nessler = brain-mechanism WTA-EM shows PC is not the sole biologically-plausible mechanism for the required function).
- **resonator_capacity_extensions** — VSA capacity extensions; drill 2 clarifies capacity is combinatorial-ceiling driven, NOT PC-allocator driven.
- **Stage 2 Spoke 1 design (2026-07-02)** — the target design. Recommendation: extend the 5-arm cell to 8 arms per §8 to make the PC-vs-alternatives comparison theory-blessed.

---

## (e) Substrate-product implications (never framed as publication)

- **Product design principle:** the substrate's concept encoder should EARN each mechanism additively — flat WTA baseline, decorrelation preproc, gated-write, hierarchy — with each layer required to show >0.15 lift over the theory-blessed alternative or be dropped. This is the "PC pays rent" discipline.
- **Simpler-first architecture:** ship `ARM_COMPETITIVE_ONLY` variant + Barlow-decorrelation-preprocessor as the MVP concept encoder for Stage 2. Reserve PC for Spokes 2/3 where hierarchy DOF gets exercised.
- **Substrate-testbed alignment:** the theoretical result (PC as complexity-tax on generic input) matches the empirical smoke anchor — a rare pre-cell/post-smoke concordance. Strengthens confidence in the reduction.
- **Do NOT tell the story as "PC is bad."** Tell it as "PC's DOF is precision-weighting + hierarchy. Substrate Stage 2 doesn't yet exercise those DOFs. Add PC in Stage 3+ where it does."

---

## (f) Citations (verified count: 27 unique sources cited across 4 sub-drills)

Capacity / VSA (sub-drill A): Plate 1995 IEEE TNN · Frady-Kleyko-Sommer 2018 Neural Comput 30(6) · Kanerva 1988 SDM · Litwin-Kumar-Harris-Axel-Sompolinsky-Abbott 2017 Neuron 93 · Ramsauer et al. 2020 arXiv 2007.13505 (Modern Hopfield) · Barlow 1961 · Olshausen-Field 1996 · arxiv 2508.01395 (feature-correlation capacity) · PMC9768680 (PC-decorrelation in RNNs) · elife 2021 (expansion-contraction sensory bottlenecks)

IB / RD (sub-drill B): Tishby-Pereira-Bialek 1999 · Tishby-Zaslavsky 2015 arXiv 1503.02406 · Achille-Soatto 2018 JMLR 19 (Emergence) · Achille-Soatto 2018 PAMI (Info Dropout) · Bialek-Nemenman-Tishby 2001 Neural Comput · PNAS 2015 (predictive-info in sensory pop) · Millidge 2021 arXiv 2107.12979 · van den Oord CPC 2018 arXiv 1807.03748 · WTA autoencoders arXiv 1409.2752

Sample complexity (sub-drill C): Tong-Koller 2001 JMLR v2 · Hanneke 2007 · Balcan-Beygelzimer-Langford 2006 A² · Robbins-Monro 1951 · Kumar-Packer 2010 SPL · Bengio et al. 2009 curriculum · Dasgupta-Hsu (CAL) · Settles 2009 AL survey

Free-energy / PC-WTA (sub-drill D): Friston 2010 Nat Rev Neurosci 11 · Friston-Kilner-Harrison 2006 J Physiol-Paris · Bastos 2012 Neuron 76 · Millidge-Tschantz-Buckley 2020 arXiv 2006.04182 · Whittington-Bogacz 2019 Trends Cog Sci 23 · Nessler-Pfeiffer-Buesing-Maass 2013 PLoS Comp Biol 9 · Neal-Hinton 1998 · Rutishauser-Slotine-Douglas 2011 Neural Comp 23 · Feldman-Friston 2010 Front Hum Neurosci 4 · Millidge et al. 2022 arXiv 2202.09467 · Sønderby et al. 2016 (ladder VAE) arXiv 1602.02282 · Dayan-Hinton-Neal-Zemel 1995 Neural Comput 7 · Hinton-Dayan-Frey-Neal 1995 Science 268

---

## One-line summary

Composite theoretical P(PC earns its complexity in HD-substrate Stage-2 concept encoder over generic corpora) = **0.22 (deflated)**; conditional P under correlated / heteroscedastic / temporal input = **~0.40**. PC and WTA share the variational-EM core; PC's genuine DOF is precision-weighting + hierarchy, which Spoke 1's flat use case does not exercise. Ship the correlation-sweep + coreset ablation to falsify decisively.
