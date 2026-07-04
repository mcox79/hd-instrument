# Research Drill: Sparse-Code Semantic-Fidelity Frontier (2026-07-04)

**Author:** Director (Research)
**Trigger:** Calibrate the planned R1-then-R5 empirical sequence (encoder_rescue_plan_converged_diagnosis_2026-07-04.md). Independent, literature-grounded prior for: is 0.85 cosine at ~2% active a SPARSITY-bound problem or an OBJECTIVE-bound problem?
**Method:** 4 parallel Sonnet lit-scans (k-sparse SAE / SDR-HTM / sparse-JL / sparse-VSA) under query-privacy discipline (generic math terms only), then Opus synthesis. Single load-bearing anchor (Morelli CLIP-SAE FVU) spot-verified directly via WebFetch against arXiv HTML (Table 2/7).
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25; novel-synthesis cap 0.50). Lit-anchored claims with direct data points are exempt from the 0.50 cap; extrapolation to our specific input pathway is NOT and is capped.
**Scope discipline:** This is a FIDELITY drill (how much of a continuous embedding's geometry survives k-sparse compression), NOT a CAPACITY drill (how many discrete patterns store without collision). The two lenses are separated explicitly in a dedicated section below. Conflating them is a known trap in this project's prior work (ref: research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md sec 5).

---

## HEADLINE

**Sparsity is NOT the binding constraint on 0.85. The 2% active operating point sits comfortably ABOVE any fidelity knee at ~4x dictionary expansion; the literature predicts the 2% sparsifier costs only a few cents of cosine relative to a dense readout. Whether 0.85 is reached is decided UPSTREAM, at the dense objective (R1), not at the sparsifier (R5's k-sweep). 0.85-at-2%-active is FEASIBLE conditional on the dense readout recovering to roughly >= 0.88 at scale; if the dense readout tops out near ~0.80, NO sparsity level rescues it and 2% vs 3.1% will land close together, both below 0.85.**

The single load-bearing, spot-verified data point: an SAE at EXACTLY 4x dictionary expansion, active fraction 0.78% of the dictionary (SPARSER than our 2%), reconstructs real CLIP sentence/image embeddings at FVU = 0.22 (Morelli et al., arXiv:2605.15961, Table 2). Under the stated approximation cosine ~= sqrt(1 - FVU), that is cosine-equivalent ~0.88 -- already above 0.85 -- at a sparsity TIGHTER than our target. Our 2% is looser, so on the sparsity axis alone the 0.85 bar is not where the difficulty lives.

**Main claim P_deflated = 0.55.**

---

## The decomposition that resolves the question

Model the achievable held-out cosine at k active as:

  cosine(k) ~= Dense_ceiling  x  sparsity_retention(k)

- **Dense_ceiling** = cosine the objective+input pathway reaches with NO sparsifier at scale. Empirically 0.825 at smoke (3k vocab) then collapsed to 0.368 at full 178k vocab -- confirmed an OBJECTIVE-SCALING bug (in-batch negative coverage 6.4% -> 0.32%), NOT a sparsity effect (it happened at zero sparsification). R1 aims to restore this to ~0.8+.
- **sparsity_retention(k)** = fraction of dense fidelity that survives k-sparse compression. This is THIS drill's question.

The literature says **sparsity_retention(2%) is HIGH at 4x expansion** -- the sparsifier costs little. Therefore the whole battle for 0.85 is fought at Dense_ceiling. This is the operational punchline: **fix and validate DENSE first (R1); the sparsifier (R5) is a cheap confirmatory sweep, not the risk.**

Three independent literatures converge on high sparsity-retention:

1. **k-sparse SAE (direct anchor, spot-verified).** Morelli et al. (arXiv:2605.15961): dict = 4x d, K = d/32 (= 0.78% of the 4d dictionary), zero-shot FVU = 0.22, SAE-FT FVU = 0.25 (Tables 2 and 7). cosine-equiv sqrt(1-0.22)=0.883, sqrt(1-0.25)=0.866. Both clear 0.85 at a sparsity TIGHTER than 2%, on real embeddings (not LLM activations), at OUR exact 4x expansion. OpenAI Gao et al. (arXiv:2406.04093) fit a SMOOTH power law in k (normalized-MSE = FVU); the law breaks down only at HIGH k (trivial reconstruction), so there is no low-k cliff near 2%.
2. **Sparse random projection (worst-case floor).** Li-Hastie-Church "Very Sparse Random Projections" (KDD 2006, full-text read by sub-agent): the ONLY fidelity penalty attributable purely to sparsity is a kurtosis term proportional to (s-3), which is EXACTLY ZERO at density 1/3 and asymptotically negligible for density down to ~1/sqrt(D). Kane-Nelson (arXiv:1012.1577): above s = Theta(eps^-1 log(1/delta)) nonzeros/column, sparse JL has NO worst-case distortion penalty vs dense. A ~2% density regime sits inside this safe zone. A LEARNED/distilled map is data-dependent and optimized for exactly the cosine target, so it should do at least as well as this data-independent random-map floor.
3. **Sparse VSA/HDC (end-task parity).** Schlegel et al. (arXiv:2001.11797): sparse BSDC needs ~320 dims for 99% 15-item bundling, on par with or better than dense binary. Frady-Kleyko-Sommer (arXiv:2009.06734): sparse block codes at 0.2-2% active hold classification accuracy across 121 UCI datasets (0.88 correlation with dense-VSA, both ~0.80). Sparse is not penalized on end-task fidelity -- BUT (see algebra caveat) only because the binding/similarity machinery was re-engineered for sparsity.

---

## Where 2% sits relative to the knee (narrow-pass answer)

- **No fidelity knee is found near 2% at 4x expansion.** The Morelli anchor works at 0.78% (well below 2%); the Gao power law is smooth through the low-k regime. The knee, if any, lies at MUCH sparser fractions (well below 1%) or shows up on a DIFFERENT axis -- feature-quality/monosemanticity degradation ("feature hedging" at low L0, arXiv:2508.16560), which is not the cosine-fidelity axis this drill asks about.
- **Sparsity needed for 0.85-equivalent RECONSTRUCTION is well below 2%.** cosine 0.85 requires FVU <= 0.2775 (EV >= 72.25%). Morelli hits FVU 0.22 (EV 78%) at 0.78% of dictionary. So 2% is generous headroom on the reconstruction axis.
- **The 2% vs 3.1% (k=82 vs k=128) gap should be SMALL,** not a cliff. On a smooth L0-vs-fidelity curve, 82 vs 128 active out of 4096 is a modest move; expect a few cents of cosine, not a step.
- **Caveat on bound direction (important).** SAE reconstruction is AUTOENCODING: the encoder has direct access to the exact target vector; the only error source is the sparsity bottleneck. Our distillation encodes from a DIFFERENT input pathway (orthography + sparse KB triples) to match a BGE teacher of different dimension, which STACKS additional error (input-pathway information + optimization). So the SAE/JL frontiers bound sparsity_retention (which is what we want), but they do NOT certify that our input pathway carries 0.85-worth of BGE semantics. That is the Dense_ceiling question, upstream, and is exactly what the prior drill (research_drill_concept_encoder_design_correctness_2026-07-04.md) flagged: orthography+triples may not carry 0.85 regardless of the bottleneck.

---

## Cheap decisive test

**Read the DENSE readout FIRST, before the k-sweep.** Post-R1, measure held-out cosine with NO sparsifier at full scale -> call it D. This is already the R1 validation target, so it is free.

- If D < 0.85: the 0.85 miss is UPSTREAM (objective/input pathway). Sparsity is irrelevant to the miss. R5's k-sweep is moot for the target; the fix is R1/R3/R4 (objective + input enrichment), not loosening sparsity. (This is the most likely near-term read and it CONFIRMS this drill's verdict that sparsity is not the bottleneck.)
- If D >= 0.88: run the k-sweep and expect cosine(k=82) within ~0.05 of D, i.e. still >= 0.83-0.85. Then 0.85-at-2% is live.

This single dense read discriminates "sparsity-bound" from "objective-bound" for near-zero marginal cost.

---

## Falsifiable predictions (R5 probe: DENSE vs k=128 vs k=82 on the fixed post-R1 objective)

Let D = dense cosine, C128 = cosine at k=128 (3.1% of N=4096), C82 = cosine at k=82 (2%).

**HARD-PASS (confirms verdict "sparsity is not the bottleneck; 2% is above the knee"):**
- C82 >= D - 0.05  (2% sparsifier costs < 5 cents vs dense), AND
- (C128 - C82) <= 0.03  (2% and 3.1% nearly indistinguishable; no knee between them).
- FULL SUCCESS overlay: if additionally D >= 0.88 AND C82 >= 0.85 -> 0.85-at-2%-active achieved.

**HARD-FAIL (refutes verdict; 2% sits BELOW a fidelity knee):**
- (C128 - C82) >= 0.10  (sharp cliff: 3.1% materially beats 2%), OR
- C82 <= D - 0.15  (2% sparsification destroys > 15 cents of dense fidelity).
- Action on hard-fail: widen to >= 3.1% and/or increase N (wider dictionary, per Numenta "make layers wider rather than reduce k"); the sparsity axis then IS load-bearing and 2% is too aggressive.

**MIDDLE BAND (partial; graded sparsifier cost, no cliff):**
- 0.03 < (C128 - C82) < 0.10, OR  D - 0.15 < C82 < D - 0.05.
- Action: adopt the looser 3.1% for margin; not a refutation, but 2% is buying a small fidelity discount.

**DIAGNOSTIC SEPARATION (the decisive read):**
- If D < 0.85 regardless of k: the target miss is OBJECTIVE-bound, not sparsity-bound. This CONFIRMS this drill even though 0.85 is not reached, because the k-sweep shows C82 ~= C128 ~= D (all clustered below target). Do not "fix" this by loosening sparsity -- fix Dense_ceiling.

---

## Recommended sparsity target

**Keep 2% (k=82 at N=4096) as the design target; carry k=128 (3.1%) as the R5 margin arm.** Reasoning:
- 2% is grounded (prior drill: Numenta ~2% canonical, brain 1-5%, substrate Spoke-1 sparse_rate [0.01,0.03] invariant) AND now fidelity-corroborated: a SAE at a TIGHTER 0.78% already clears 0.85-equivalent reconstruction at 4x expansion.
- The 82->128 move is cheap insurance, not a required loosening. Run both in R5; if HARD-PASS, ship 2%; if MIDDLE-BAND, ship 3.1%; if HARD-FAIL, escalate to wider N before looser k.
- Do NOT spend cycles re-deriving 2% (prior drill closed that). This drill's contribution is the fidelity-frontier prior, not the operating-point choice.

---

## CAPACITY lens vs FIDELITY lens (explicit separation for future citations)

These are DIFFERENT questions with DIFFERENT math. Do not cite one as an answer to the other.

| | CAPACITY lens | FIDELITY lens (THIS drill) |
|---|---|---|
| Question | How many discrete patterns store without collision? | How much of a continuous embedding's graded similarity survives k-sparse compression? |
| Math | Willshaw-Buckingham alpha_c(f) ~ f log(1/f) K_eff; compressed-sensing RIP M >= C k log(N/k)/eps^2; SDR overlap/false-positive (hypergeometric) | FVU / explained-variance -> cosine ~= sqrt(1-FVU); sparse-JL distortion (1 +- eps); SAE L0-vs-reconstruction Pareto |
| Reference | research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md sec 5 (pattern-storage, ~23x sparse gain) | Morelli/Gao SAE frontiers; Li-Hastie-Church; Kane-Nelson (this note) |
| What "2%" means | active fraction f that maximizes stored-pattern count (sparse gain) | active fraction that retains enough variance for target cosine |
| Verdict at 2% | ~23x capacity gain over dense (Drosophila-MB-class) | sparsifier cost small; 0.85 gated by objective, not sparsity |

The SDR/HTM literature (Ahmad-Hawkins arXiv:1503.07469; Ahmad-Scheinkman arXiv:1903.11257; Kanerva SDM) is rich on the CAPACITY lens (collision, noise-robustness) and essentially SILENT on the FIDELITY lens -- it gives no Spearman/cosine-preservation number at 2% active. The only lineage with rigorous fidelity-vs-similarity math (SimHash/WTA-Hash: Pr[sign-match] = 1 - theta/pi) operates at ~50% density, not 2%, and nobody published the fidelity-vs-sparsity curve down at 2%. So for the fidelity lens at 2%, the SAE and sparse-JL literatures (this drill) are the load-bearing sources, NOT SDR theory.

---

## Cross-thread synthesis

- **research_drill_concept_encoder_design_correctness_2026-07-04.md** (same-day prior): concluded the CURRENT unsupervised/no-teacher objective cannot reach 0.85 regardless of sparsity, and recommended BGE distillation. THIS drill sharpens and confirms that: the ceiling is at the OBJECTIVE/INPUT (Dense_ceiling), not the sparsifier. 2% as an operating point is corroborated on the fidelity axis, not just the capacity axis.
- **encoder_rescue_plan_converged_diagnosis_2026-07-04.md**: the DENSE_SIGN 0.825 -> 0.368 collapse (objective-scaling bug, zero sparsification) is exactly the Dense_ceiling failure this drill's decomposition isolates. R1 (global/landmark RKD) is the correct load-bearing fix; R5 (k-sweep) is correctly framed as a cheap diagnostic, and THIS drill predicts R5 will show C82 ~= C128 (no cliff), with the target verdict decided by D.
- **research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md sec 9 L-1** (one-sentence cross-ref): flags a SEPARATE, independent gate -- sparse coding conflicts with FHRR binding-algebra cancellation. This drill's sparse-VSA scan CORROBORATES that L-1 conflict is real and documented (see algebra caveat below); it is an algebra-survival gate, orthogonal to the cosine-fidelity question, and must be gated separately (recommendation #2 in the prior design-correctness drill).

**Algebra-survival cross-reference (SEPARATE gate, not this drill's main question).** Sparse-VSA lit documents a real tension: naive dense binding (elementwise multiply / circular convolution) is NOT dimensionality/sparsity-preserving on sparse codes (Frady et al.). Working sparse-VSA schemes REQUIRE new operators (block-local circular convolution; context-dependent thinning, Rachkovskij-Kussul 2001; SPTP, flagged "somewhat lossy") and even a non-standard similarity metric (Hersche et al. arXiv:2303.13957: plain dot-product "cannot solve any of the displayed problem sizes"; had to switch to L-infinity). Implication: high cosine at 2% does NOT guarantee the FHRR bind/unbind/cleanup survives; keep the algebra-fidelity gate independent of the cosine gate. P_deflated(algebra-survival tension is real) = 0.60.

---

## Substrate-product implications

- **Sequencing is validated.** Do R1 (fix + validate DENSE) FIRST; R5 (k-sweep) is confirmatory, not the risk-bearing step. Do not block on R5.
- **The cheapest signal is the dense readout.** Reading D post-R1 immediately tells us whether the 0.85 problem is sparsity (unlikely) or objective (likely). This is free -- it is already R1's own success metric.
- **2% ships.** No design change to the sparsity target is warranted on fidelity grounds. Carry 3.1% only as a margin arm.
- **Keep the algebra gate separate.** A passing cosine gate at 2% must still clear an independent bind/unbind-fidelity gate; the sparse-VSA lit says forcing sparsity onto a dense binding algebra is where that risk lives, and it is decoupled from the cosine number.
- **If R1 tops at ~0.80:** the strategic lever is the INPUT pathway (R3 internal self-teacher, R4 relational-graph densification) or a stronger teacher, NOT looser sparsity. A USER strategy call, framed by this drill as objective-bound not capacity-bound.

---

## Per-claim P_deflated

| Claim | Raw | P_deflated | Basis |
|---|---|---|---|
| At 4x expansion, 2% active sits comfortably ABOVE any fidelity knee | 0.80 | **0.62** | Direct spot-verified anchor at a TIGHTER 0.78% (Morelli FVU 0.22) + smooth Gao power law + sparse-JL safe zone. Lit-anchored, not novel-synthesis. |
| Sparsity is NOT the binding constraint; 0.85-at-2% feasible conditional on Dense_ceiling >= ~0.88 (MAIN) | 0.72 | **0.55** | Decomposition + 3-literature convergence; deflated for uncharted-for-us input pathway. |
| k=82 vs k=128 gap will be small (< ~0.03-0.05 cosine); no cliff between 2% and 3.1% | 0.72 | **0.58** | Smooth L0-vs-fidelity curves; modest move 82->128 of 4096. |
| If 0.85 is missed at 2%, cause is the dense objective/input pathway, not sparsity | 0.70 | **0.55** | Bound-direction argument (SAE autoencoding upper-bounds distillation) + empirical DENSE-collapse precedent. |
| Forcing 2% sparsity onto FHRR binding has a real, documented algebra-survival cost (SEPARATE gate) | 0.75 | **0.60** | Well-documented across sparse-VSA lit; corroborates ref L-1. |
| Distillation-from-orthography input pathway can itself carry 0.85 of BGE semantics (EXTRAPOLATION to our pathway) | -- | **<= 0.35** | Explicitly capped; NOT this drill's evidence; flagged upstream/objective-bound; prior drill put current unsupervised design at 0.05. |

---

## Citations (verified count)

**Spot-verified directly this session (WebFetch against source):**
1. Morelli, Uselis, Sonthalia, Oh. "Sparse Autoencoders enable Robust and Interpretable Fine-tuning of CLIP models." arXiv:2605.15961 (2026). VERIFIED: dict = 4x d; K = d/32; zero-shot FVU 0.22, SAE-FT FVU 0.25 (Tables 2, 7). LOAD-BEARING ANCHOR.

**Verified from sub-agent search (title/author/venue confirmed; numbers as reported by sub-agents):**
2. Gao et al. "Scaling and evaluating sparse autoencoders." arXiv:2406.04093 (2024, OpenAI). normalized-MSE=FVU; smooth power law in k.
3. Rajamanoharan et al. "Jumping Ahead: JumpReLU Sparse Autoencoders." arXiv:2407.14435 (2024, DeepMind).
4. Rajamanoharan et al. "Gated Sparse Autoencoders." arXiv:2404.16014 (2024, DeepMind).
5. Anthropic. "Towards Monosemanticity" (2023); "Scaling Monosemanticity" (2024). (loss-recovered metric; expansion 4x-2833x.)
6. Ahmad & Hawkins. "Properties of Sparse Distributed Representations..." arXiv:1503.07469 (2015). CAPACITY lens.
7. Ahmad & Scheinkman. "How Can We Be So Dense?" arXiv:1903.11257 (2019). ROBUSTNESS lens.
8. De Sousa Webber. "Semantic Folding Theory." arXiv:1511.08855 (2015). Fidelity claim qualitative only.
9. Rinkus & Leveille. "Superposed Episodic and Semantic Memory via SDR." arXiv:1710.07829 (2017).
10. Purdy. "Encoding Data for HTM Systems." arXiv:1602.05925 (2016).
11. Kanerva. Sparse Distributed Memory. MIT Press (1988). CAPACITY lens.
12. Charikar SimHash / random-hyperplane LSH (Pr[sign-match]=1-theta/pi); Yagnik et al. WTA-Hash. Fidelity math at ~50% density.
13. Johnson & Lindenstrauss (1984); Achlioptas "Database-friendly random projections" JCSS 2003.
14. Dasgupta, Kumar, Sarlos. "A Sparse JL Transform." STOC 2010 (arXiv:1004.4240).
15. Kane & Nelson. "Sparser JL Transforms." SODA 2012 (arXiv:1012.1577). s=Theta(eps^-1 log(1/delta)).
16. Nelson & Nguyen. "Sparsity Lower Bounds..." STOC 2013 (arXiv:1211.0995).
17. Larsen & Nelson. "JL is Optimal for Linear Dim. Reduction." arXiv:1411.2404.
18. Li, Hastie, Church. "Very Sparse Random Projections." KDD 2006. FULL-TEXT read by sub-agent; kurtosis (s-3) penalty; s=3 exact match to dense. LOAD-BEARING for JL floor.
19. Freksen. "An Introduction to JL Transforms." arXiv:2103.00564 (survey).
20. Laiho, Poikonen, Kanerva, Lehtonen. "High-Dimensional Computing with Sparse Vectors." BioCAS 2015.
21. Frady, Kleyko, Sommer. "Variable Binding for SDR: Theory and Applications." IEEE TNNLS 2021 (arXiv:2009.06734).
22. Hersche et al. "Factorizers for Distributed Sparse Block Codes." arXiv:2303.13957 (2025). L-infinity similarity fix.
23. Schlegel, Neubert, Protzel. "A Comparison of Vector Symbolic Architectures." AI Review 2021 (arXiv:2001.11797).
24. Rachkovskij & Kussul. "Binding and Normalization... Context-Dependent Thinning." Neural Computation 2001.
25. Frady, Kent, Olshausen, Sommer. "Capacity Analysis of VSAs." arXiv:2301.10352 (abstract-level).
26. Kenyon-cell (~5-10%) and cerebellar granule-cell (~14.5-17.7%) sparsity: PMC/eLife/RSOS (biological-range context).

**General field-knowledge (not numerically re-verified this session):**
- Feature-hedging at low L0 (arXiv:2508.16560, "Sparse but Wrong") -- interpretability-axis knee, distinct from cosine.
- cosine ~= sqrt(1-FVU) translation (valid when reconstruction error is isotropic/orthogonal to signal) -- STATED APPROXIMATION, not a citation.
- eps <-> cosine order-of-magnitude proxy for JL distortion.

**Verified-paper count: 26 distinct works** (1 spot-verified against source this session; ~5 full-text/table-verified by sub-agents; remainder title/venue-verified with numbers as sub-agent-reported). One arXiv ID (2605.15961) is 2026-dated and was the item explicitly re-verified against source.

---

## Intuitive summary (plain language)

Think of the encoder as trying to draw a rich picture (a concept's meaning, as captured by a strong off-the-shelf model) using only a small box of crayons -- it is allowed to use only about 2 crayons out of every 100. The worry was: maybe 2-out-of-100 is simply too few crayons to reproduce the picture faithfully, so the 0.85 "looks-like-the-original" score is physically out of reach no matter how good the artist is.

The literature says: no, that is not the problem. Other people have drawn very similar pictures with even FEWER crayons (fewer than 1 in 100) and still scored about 0.88 -- above the 0.85 target -- using the exact same size crayon box we plan to use. The math of sparse drawing (random-projection theory) agrees: using few crayons instead of many costs almost nothing in faithfulness, as long as you are above a low threshold, and 2% is safely above it. So 2 crayons out of 100 is a comfortable, not a risky, choice.

The real problem is upstream. Earlier this week we saw the artist's score crash from 0.83 (on a small practice set) to 0.37 (on the full job) EVEN WHEN GIVEN UNLIMITED CRAYONS. That means the artist was not failing because of too few crayons -- the artist was failing to understand the picture in the first place (a training bug where, at full scale, the lesson plan almost never showed it the fine distinctions it was being graded on). The fix in flight (R1) is a better lesson plan that teaches those distinctions directly.

So the sequencing is: fix the lesson plan first and confirm the artist can score ~0.88 with unlimited crayons (that is the R1 milestone, and reading that one number is basically free). ONLY THEN hand it the 2-crayon box and check the score (the R5 probe). This drill predicts that if the unlimited-crayon score is high, the 2-crayon score will be within a few percent of it, and the 2-crayon and 3-crayon versions will look almost the same -- no sudden cliff. If the unlimited-crayon score is still low, do not blame the crayons; go back and fix the lesson plan or give the artist better reference material (a richer input), which is a strategy decision, not a sparsity knob.

One separate warning, unrelated to the score: even if the picture looks right at 2 crayons, the algebra we layer on top (binding concepts together and pulling them apart again) can break under heavy sparsity unless we use sparsity-aware versions of those operations. That is a second, independent test we must keep -- a good-looking score does not by itself prove the algebra still works.

**Why it matters:** it removes a feared blocker (2% being too sparse) and redirects effort to the actual blocker (the training objective at scale). **Near-term decision:** proceed with R1 as the load-bearing fix, keep 2% as the target, run R5 as a cheap confirmation, and read the unlimited-crayon (dense) number first because it settles the whole question for almost no cost.

ASCII-only. No emojis. No em dashes.
