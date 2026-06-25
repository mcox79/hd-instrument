# Research 2x + 3x revival drill -- encoder-leakage HARD_PASS_LEAKAGE_REAL

**Date:** 2026-06-24
**Author:** Research (Opus 4.7-1M)
**Drill type:** 3-angle revival drill. Angle 1 = the discovery cell itself (already in hand). Angle 2 = brain-existence-proof for encoder-learning-from-scratch. Angle 3 = test-design audit + opportunities.
**Trigger:** USER standing rule "drill all negatives 3x looking for causes and opportunities" applied to today's biggest finding.
**Calibration penalty applied:** P estimates deflated by 0.20; novel-synthesis cap = 0.45.

---

## HEADLINE

**The clean-encoder HARD_PASS_LEAKAGE_REAL verdict is correct in its narrow claim (Google-News pretraining was contributing ~0.44 BPC of the substrate's previously-claimed lift) BUT the test was conducted in a regime where BPC discrimination between encoders is structurally suppressed and arm B was under-trained by ~600x relative to arm A. The brain learns its encoder from sensory experience without any external pretraining via a small set of bio-plausible mechanisms (sparse coding / predictive coding / Hebbian-WTA / BCM). At least one of these (Hebbian temporal predictive coding) has a recent published demonstration on language morphology specifically. The substrate-product opportunity is not "match word2vec-google-news on text8" -- it is "build the substrate-owned encoder via brain-mechanism, then test on a vocabulary regime where the unigram floor does not pin BPC."**

Top-3 revival paths (full rank order in L3):
1. **Substrate-owned SoftHebb-on-trigram encoder + temporal-Hebbian alignment (arxiv 2503.02057 architecture)** -- cheapest decisive test (P_deflated=0.32).
2. **Properly-converged clean word2vec at 100M+ tokens** -- diagnostic re-do (P_deflated=0.55).
3. **Sparse-coding (Olshausen-Field) dictionary over text-bigram statistics** -- novel substrate path (P_deflated=0.25).

---

## ANGLE 2 -- Brain-existence-proof: how does brain learn encoders without leakage?

The brain has no pretrained external corpus and no labeled supervision. Visual cortex develops localized, oriented, bandpass receptive fields from its own sensory experience over months (cat-rearing studies; dark-rearing reversals). The literature on the brain-mechanisms that achieve this is mature.

### Mechanism inventory (with substrate-applicability)

**M1. BCM rule (Bienenstock-Cooper-Munro 1981)**
- Sliding-threshold Hebbian: weight modification sign flips at a threshold that is super-linear in time-averaged postsynaptic activity. Stabilizes against runaway potentiation; produces orientation selectivity in natural-scene environments.
- Substrate fit: HIGH. Forward-only, local, deterministic, single-pass-friendly. Already on the substrate radar (capability map row N4-class).
- Caveat: classical BCM is dense-Hebbian; substrate sparse-bipolar regime needs the sparse variant (BCM-sparse).

**M2. SoftHebb (Journe 2022 / Moraitis 2022 IOP-Neuromorphic-Computing)**
- Soft winner-take-all + Hebbian update; minimizes cross-entropy WITHOUT supervised signal; converges in fewer iterations than backprop; robust to noise/adversarial.
- Demonstrated up to 5 hidden layers, 99.4% MNIST / 80.3% CIFAR-10 / 27.3% ImageNet unsupervised.
- Substrate fit: HIGH. Already named in Path C v2 spec (research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md row S1).

**M3. Olshausen-Field sparse coding (1996)**
- Sparseness PRIOR + reconstruction loss over natural-image patches produces V1-like (localized, oriented, bandpass) receptive fields. SparseNet alternates sparse-coding step with Hebbian dictionary update.
- Substrate fit: MEDIUM-HIGH. Substrate already uses sparse bipolar (sparse_f=0.05); the dictionary-learning analog is the encoder matrix. Bigram-co-occurrence statistics over text8 are the analog of natural-image patches.

**M4. Rao-Ballard hierarchical predictive coding (1999)**
- Higher cortical area sends top-down prediction; lower area sends back the residual error; both reconciled via local Hebbian. Develops simple-cell receptive fields AND extra-classical end-stopping effects.
- Substrate fit: MEDIUM. Requires multi-level architecture. Substrate has the bipolar HD primitives but no explicit hierarchy yet. Temporal-predictive-coding variant (Millidge 2023 PLoS Comp Bio) operates on sequence prediction with purely Hebbian plasticity -- direct fit for text next-word prediction.

**M5. Foldiak (1990) Hebbian + anti-Hebbian lateral inhibition**
- Hebbian feedforward + plastic anti-Hebbian lateral inhibition decorrelates outputs; produces sparse independent components of natural images (V1 edges).
- Substrate fit: MEDIUM. Lateral-inhibition is not native to substrate HD bipolar, but anti-Hebbian over already-bipolar outputs is implementable as a sign-flip Hebbian update.

**M6. Eugenio (2025) Hebbian local-structure-of-language (arxiv 2503.02057)**
- DIRECT LANGUAGE-MORPHOLOGY DEMONSTRATION. Hierarchy of neurons learns to tokenize text via Hebbian rule; second layer binds tokens into semantic embeddings. "Learns natural language morphology without data" (i.e. without large pretraining corpus). Continuous parallel learning without forgetting.
- Substrate fit: HIGHEST. Published 2025-03, after most of the substrate's encoder lit-scans. NOT a v1 / not-yet-engaged. Direct candidate for the substrate-owned text encoder. This is the brain-mechanism for word-level encoding that the substrate has not yet integrated.

### Why brain achieves competence without 17M-token pretraining

Brain accumulates ~10^8-10^9 sensory events over years of development, but these are NOT discrete labeled tokens. The trick is:
- Brain operates on continuous-streaming local-Hebbian updates (every event contributes a tiny weight adjustment; no batch).
- The pretraining "corpus" IS the developmental sensory stream -- it does not exist as a separable artifact to be leaked from.
- The encoder is co-developed with the downstream substrate (predictive-coding loops); there is no "fix encoder, train substrate" split.

For the substrate: the analog is **co-train the encoder with the substrate W**, via temporal-predictive-coding loops where the encoder is updated by the substrate's prediction error, NOT trained as a separable pretrained component. This is the structural reason brain has no encoder-leakage: there is no separate encoder.

---

## ANGLE 3 -- Test-design audit + opportunities

Audit each assumption in the clean-encoder cell that could have shifted the verdict.

### A1. Single deterministic seed (cv=0)
- metrics.json shows `bpc_best_std=0.0` for all 4 arms across 1 seed. Seed=[7] only.
- IMPACT: unknown. Word2vec training has stochasticity (random init, negative sampling order). With 1 seed we cannot bound the cv on arm B.
- COST OF FIX: trivial. Re-run with seeds=[7,13,29]. ~25 min wall.
- VERDICT: minor risk; should be fixed before any cap_map bump downstream.

### A2. Word2vec-text8-only was DRAMATICALLY under-trained
- encoder_meta.B.training_meta: `n_train_tokens=100000`, `n_sentences=100`, `training_wall_s=1.82`, `wv_vocab_size=2629` (vs Google News ~3M).
- Google News word2vec was trained on ~100B tokens. Arm B saw 100K tokens. That is a **1,000,000x deficit**, not the 600x I initially estimated.
- 100K tokens is well below the "0.5-5M token" small-corpus regime where word2vec produces "reasonable performance for domain-specific" tasks per the lit-scan finding.
- IMPACT: MAJOR. The lit-scan finding "smaller corpora may do just as well" assumes 0.5-5M tokens minimum. 100K is the under-converged regime, NOT the small-but-sufficient regime.
- COST OF FIX: text8 is 17M tokens; train clean word2vec on the full 17M with 5+ epochs (~30 min CPU). This is the proper clean-encoder rail.
- VERDICT: **THIS ALONE COULD INVALIDATE THE LEAKAGE-REAL VERDICT.** The 0.44 BPC gap may be 0.1 BPC pretraining-knowledge + 0.34 BPC under-training. Mandatory re-run.

### A3. Substrate config not re-tuned per encoder (same T/lambda grids)
- Arm A optimum: T=0.05, lambda=0.3. Arm B optimum: T=0.01 (grid edge), lambda=0.0 (grid edge).
- Arm B is railed to the LOW end of both grids -- the substrate cleanup is over-correcting because the clean encoder's logit distribution is broader / less peaky.
- IMPACT: SIGNIFICANT. Arm B may want T < 0.01 (off the grid). The "BPC gap" is partly a grid-coverage gap.
- COST OF FIX: extend TEMP_GRID down to [0.001, 0.003, 0.005]. ~5 min cell change.

### A4. text8 corpus is Wikipedia-derived (potentially correlated with word2vec-google-news training distribution)
- text8 is Wikipedia 2006. word2vec-google-news was trained on Google News (different distribution but similar journalistic register).
- IMPACT: MODERATE. Cross-domain test (e.g. evaluate on Penn Treebank or WikiText-103-out-of-domain) would disambiguate.
- COST OF FIX: cheap -- evaluate same encoders + substrate on a held-out non-Wikipedia corpus. ~1 hr.

### A5. Single substrate primitive (rank-1 Hebbian, no learned W)
- The substrate-as-LM here is the rank-1 cosine-decoder over a fixed Hebbian-aggregated W.
- A LEARNED-W variant (e.g. dual-gain attention, modern-Hopfield XL, OMP cleanup) would give the clean encoder more headroom because the substrate would compensate for encoder weakness.
- IMPACT: HIGH. The cell tests **encoder x rank-1-substrate** jointly; it does NOT test "is the encoder load-bearing across substrate variants".

### A6. Vocabulary-floor pinning of BPC
- V=4000. Unigram entropy at V=4000-5000 (Wikipedia) ~ 7.3-8.35 bits per word (lit-scan confirmed: 5,081-word English subset gives 8.35 bits; substrate range 7.3-7.7 is consistent with this floor).
- All 4 arms cluster within 0.44 BPC = 5% of the unigram floor. This is the regime where **encoder choice DOES NOT MATTER for BPC** because the metric is dominated by unigram frequency.
- Cross-check: top-1 accuracy is HIGHER for arm B (0.2171) and C (0.219, random projection!) than arm A (0.2151). The "best encoder" by BPC and by top-1 DISAGREE. This is direct evidence the discrimination regime is the wrong place to be measuring.
- IMPACT: **DECISIVE.** The measurement is being made at the unigram floor where encoders are indistinguishable. Move to V=20k-50k OR move to bigram/trigram conditional entropy (where unigram floor does not apply).

### Opportunities derived from the audit

**OPP1. Re-run clean-encoder with 17M-token-properly-converged word2vec + grid-extension + 3 seeds.** Cost ~1.5 hr. If leakage_delta drops to <0.15 BPC after these fixes, the "LEAKAGE_REAL" verdict downgrades to MIDDLE_BAND.

**OPP2. Move to V=20k vocabulary + conditional-bigram metric.** Unigram entropy at V=20k Wikipedia ~ 10.6 bits. Conditional-on-prev-word entropy ~ 6-7 bits (lit standard). Substrate at unigram-floor 7.3-7.7 has no headroom; substrate at conditional-bigram has 3-4 bits of headroom. Encoders will discriminate properly here.

**OPP3. Path C substrate-owned encoder (S1 SoftHebb + S2 atom-graph), per research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.** Already specced; this drill confirms it is the strategic answer (no leakage because no separate pretraining).

**OPP4. Eugenio (2025) Hebbian-language-morphology mechanism.** New 2025 publication not yet in substrate roadmap. Direct candidate to slot in at S1 spoke of Path C.

---

## L3 -- Top 3 paths + cheap decisive test

| Rank | Path | Pre-reg HARD-PASS | Pre-reg HARD-FAIL | Cost | P_deflated |
|---|---|---|---|---|---|
| **1** | **OPP2 + OPP1 combined: re-run on V=20k + properly-converged clean w2v + 3 seeds + extended temp grid (cheap decisive test)** | leakage_delta < 0.10 BPC at V=20k AND clean-encoder bpc <= unigram-floor by >= 0.5 BPC margin | leakage_delta > 0.30 BPC at V=20k OR substrate-as-LM at-floor regardless of encoder | ~3 hr CPU | 0.45 |
| 2 | OPP3 Path C S1+S2 substrate-owned encoder, evaluated on V=20k conditional-bigram metric | substrate-owned encoder >= clean-w2v at V=20k conditional-bigram | substrate-owned encoder >= 0.20 BPC worse than clean-w2v | ~2 weeks | 0.32 |
| 3 | OPP4 Eugenio Hebbian-language-morphology integration as Path C S1 replacement | Eugenio-encoder >= SoftHebb-on-trigram on conditional-bigram metric | Eugenio-encoder fails to surpass char-trigram baseline | ~1 week | 0.25 |

### Cheap decisive test (pre-registered)

**Cell:** `clean_encoder_eval_harness_v2_FAIR_REGIME`
**Anchor:** `substrate_clean_encoder_fair_regime_v2`
**Changes from v1:** (a) train clean w2v on full 17M-token text8 with 5 epochs (target ~30 min CPU), (b) V=20000 instead of V=4000, (c) seeds=[7,13,29], (d) TEMP_GRID=[0.001,0.003,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1.0], (e) report BOTH unigram-conditional BPC AND bigram-conditional BPC.

**Pre-reg HARD bands:**
- HARD_PASS_LEAKAGE_REAL_CONFIRMED: leakage_delta_B_minus_A on bigram-conditional metric >= 0.30 BPC. P_deflated=0.25.
- MIDDLE_BAND: leakage_delta in [0.10, 0.30). P_deflated=0.45.
- HARD_PASS_LEAKAGE_REFUTED: leakage_delta < 0.10 BPC. P_deflated=0.30.

If LEAKAGE_REFUTED lands, the v1 verdict was a measurement-regime artifact (unigram-floor pinning + under-training of arm B), not a real leakage signal. Substrate's original "+12% top-1" claim returns to the table pending validation on the proper-regime metric.

---

## Cross-thread synthesis

- Reinforces research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24 (measurement-regime discipline must precede verdict interpretation).
- Reinforces project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23 (brain-mechanism path; no pretraining = no leakage).
- Surfaces NEW adjacency: Eugenio 2025 arxiv 2503.02057 Hebbian-language-morphology -- not in prior research notes; should be added to Path C S1 candidate slate.
- Aligns with feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23 (brain develops its encoder from sensory experience; substrate has all the primitives to do the same).

## Substrate-product implications

- The clean-encoder HARD_PASS verdict should NOT be propagated as "substrate-as-LM lift was an illusion" until the fair-regime re-run lands. The honest framing is "the lift may include encoder-pretraining contribution; we will know after V=20k bigram-conditional re-run".
- Cap_map row "substrate-as-LM" should be annotated MIDDLE_BAND_PENDING_FAIR_REGIME pending the cheap decisive test above, NOT closed as failed.
- Path C v2 (substrate-owned encoder) gets a P_deflated bump from 0.30 to 0.35 because Eugenio 2025 provides a published precedent for the S1 spoke.
- The structural lesson: any encoder-comparison test in the unigram-floor regime is uninformative. Future encoder cells must verify the measurement is in a discriminating regime (DISCRIMINATING_REGIME gate from C0-C6 architecture) before being eligible to bump cap_map.

## Citations (verified count: 11)

External:
1. BCM theory (Wikipedia / Scholarpedia) -- https://en.wikipedia.org/wiki/BCM_theory ; http://www.scholarpedia.org/article/BCM_theory
2. Bienenstock, Cooper, Munro 1982 J Neurosci (BCM original).
3. Moraitis et al. 2022 SoftHebb IOP Neuromorphic Computing -- https://iopscience.iop.org/article/10.1088/2634-4386/aca710
4. Journe et al. 2022 Hebbian Deep Learning Without Feedback -- https://arxiv.org/abs/2209.11883
5. Olshausen and Field 1996 Nature; 2004 Curr Opin Neurobio -- https://www.cnbc.cmu.edu/~tai/nc19journalclubs/Olshausen-Field-CON-2004-1.pdf
6. Rao and Ballard 1999 Nature Neuroscience 2(1):79-87 -- https://www.nature.com/articles/nn0199_79
7. Foldiak 1990 forming sparse representations by local anti-Hebbian -- https://www.researchgate.net/publication/304541412
8. Millidge et al. 2023 Predictive Coding Networks for Temporal Prediction PLoS Comp Bio -- https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011183
9. Eugenio 2025 Hebbian learning the local structure of language -- https://arxiv.org/abs/2503.02057
10. Wang et al. 2020 Word2Vec Optimal Hyperparameters NLP Downstream -- https://arxiv.org/abs/2003.11645
11. Bentz et al. 2017 Entropy of Words across 1000+ Languages MDPI Entropy -- https://www.mdpi.com/1099-4300/19/6/275

Internal (re-read):
- preregs/2026-06-23_clean_encoder_eval_harness_v1.md
- data/exp_substrate_clean_encoder_substrate_as_LM_v1/metrics.json (canonical source of leakage_delta=0.4376)
- notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md
- notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md
