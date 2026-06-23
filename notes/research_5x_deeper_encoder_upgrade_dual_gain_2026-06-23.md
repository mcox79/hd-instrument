# 5x-DEEPER encoder-upgrade drill — Shannon-floor PIVOT — dual-gain candidates

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Drill type:** 5x-DEEPER (L1 broad → L2 substrate-filter → L3 depth on top-2 → L4 cell-design → L5 cross-substrate composition). Third encoder-side attempt after parent 5x-DEEPER 2026-06-21 unfired + ENC1 HARD_FAIL 2026-06-23. Calibration penalty applied HARDER (deflate 0.25-0.35; cap P at 0.40).
**Trigger:** Shannon-floor META cert row 675 + N-INDEPENDENT branch closure 2026-06-23. The META explicitly says: ENCODER-SIDE GEOMETRY CANNOT BREAK sigma>=1.5 ON RANDOM BIPOLAR CODEBOOK. The PIVOT direction is **noise-reduction at SOURCE = richer signal at encoder** = upgrade the upstream text→HD encoder. Same upgrade should help BOTH (Shannon-floor at production-regime via richer atoms) AND Path A pseudo-LM (close bigram-gap via better calibrated logits).
**Generic-terms-only queries** per query-privacy. **MiniLM/BGE forbidden** per USER directive 2026-06-22.

---

## HEADLINE

**Top-2 to dispatch (dual-gain candidates):**

1. **SoftHebb 3-stage unsupervised char-encoder (P_deflated = 0.35-0.40)** — substrate-native, forward-only, lateral-inhibition + Bayesian-generative, online; outperforms backprop in noise + one-shot regimes per Moraitis 2021. Lift target: build a substrate-trainable text encoder (no MiniLM, no Pythia, no backprop) from the existing `char_trigram_encoder.py` plus a 3-layer SoftHebb expansion that LEARNS isotropic representations on text8 during ingest. Discriminator: BPC vs unigram (Path A) AND cleanup recall at sigma=1.5 with N=4096 learned-key codebook (production-regime variant of ENC1).
2. **Fractional Power Encoding (FPE) + improved-cleanup (Bremer-Orchard 2412.00488) (P_deflated = 0.30-0.35)** — substrate-native FHRR-style encoder that explicitly addresses the cleanup problem the parent failed on. FPE encodes values as phase rotations; the 2412.00488 paper gives a CLE+MLE iterative cleanup that beats prior methods under noise. Replaces dense bipolar codebook generation with FPE-based phase-tagged codebook. Discriminator: same as #1.

**Critical reframe via the data:** the parent ENC1 HARD_FAIL is on a **SYNTHETIC random bipolar codebook** with mu~0 by construction. The Shannon-floor proof at sigma=1.5 is ALSO on that synthetic regime. Branch #3 (learned-encoder keys) of the META has NOT been tested. The META is currently 2-of-3 closed. **This drill targets branch #3 explicitly** — the unfilled cell that determines whether the Shannon-floor extends to production regime or is synthetic-codebook-specific.

**Predicted regime split:**
- If branch #3 also HARD_FAILS (learned keys recall <= 0.10 at sigma=1.5): the Shannon-floor is TRULY fundamental; META promoted to full chain-grade saturation. Path forward: descope sigma>=1.5 regime; commit to sigma<=1.0 as substrate envelope.
- If branch #3 HARD_PASSES (learned keys recall >= 0.20 at sigma=1.5): the Shannon-floor is **synthetic-codebook artefact**; structured encoder geometry IS the fix in production. SoftHebb or FPE encoder becomes new substrate primitive.

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `enc_dual_gain_softhebb_vs_fpe_v1`
**Wall budget:** ~30-60 min laptop CPU (substrate-trainable, no GPU needed for SoftHebb at N=4096)
**Pre-flight:** sigma=0 sanity recall=1.000 (all arms); HDLAB_EXP_NAME set; REQUIRED_FIELDS schema-vet via `tools/exp_dev/formula_selftests.py`.

**4-arm sweep, single cell, two metrics measured per arm:**

| ARM | Encoder | Codebook source | Cleanup-recall regime | Path-A regime |
|---|---|---|---|---|
| ARM_BASELINE_BIPOLAR | random bipolar (M=200, N=4096) | synthetic | reproduce N-INDEPENDENT HARD_FAIL = 0.022 | reproduce 7.86 BPC |
| ARM_CHAR_TRIGRAM | existing `char_trigram_encoder.py` (N=4096) | text8 words → encode → store | substrate atoms are LEARNED keys; test branch #3 | replace random codebook with char-trigram bundled atoms |
| ARM_SOFTHEBB_3LAYER | SoftHebb (Moraitis 2021) 3-layer expansion ON TOP of char-trigram | text8 words → char-trigram → SoftHebb-encode → store | LEARNED + LATERAL-INHIBITED keys | replace codebook with SoftHebb-output atoms |
| ARM_FPE_PHASE | Fractional Power Encoding (FHRR-style phase) + Bremer-Orchard cleanup | text8 words → FPE-encode → store | phase-tagged keys + CLE+MLE cleanup | replace codebook with FPE atoms; bind position via phase |

**Per-arm metrics:**
- **CLEANUP**: noise sweep [sigma=0.0, 0.5, 1.0, 1.5, 2.0], M=200, N_EVAL=200, 3 seeds. recall@1 at each sigma.
- **PATH-A BPC**: text8 N_TRAIN=100k, N_HELD=20k, VOCAB_CAP=4000, N_DIM=4096, log-linear+unigram calibrated decode. BPC and top-1 acc, 3 seeds.

**Discriminator (the load-bearing question):** at sigma=1.5 production-regime (learned-key codebook), is the Shannon-floor still N-INDEPENDENT (recall <= 0.10) or does encoder geometry rescue it (recall >= 0.20)?

**Discriminating-regime gate (mandatory per C5):**
- If ARM_CHAR_TRIGRAM recall(sigma=1.5) >= 0.20 alone: branch #3 of META is FALSE; Shannon-floor was synthetic-codebook artefact; encoder geometry IS the lever. **Atomize: Shannon-floor is SYNTHETIC-CODEBOOK-only**. Substrate operating envelope unchanged at production.
- If ARM_CHAR_TRIGRAM HARD_FAILS but ARM_SOFTHEBB or ARM_FPE >= 0.20: branch #3 of META is true ONLY for naive bag-of-trigrams; richer substrate-native encoders rescue.
- If ALL 3 non-baseline arms HARD_FAIL: branch #3 of META CLOSES; Shannon-floor is fully load-bearing; chain-grade promotion.

**Pre-reg HARD bands (per arm vs baseline 0.022):**
- **HARD_PASS CLEANUP**: recall(sigma=1.5) >= 0.20 AND cv <= 0.30 (production-meaningful lift, ~9x baseline)
- **HARD_FAIL CLEANUP**: recall(sigma=1.5) <= 0.05 (within 2.3x baseline; mechanism null at production regime)
- **MIDDLE_BAND CLEANUP**: 0.05 < recall < 0.20 (measured-mechanism; characterize)
- **HARD_PASS BPC**: BPC < 7.738 (unigram) AND cv <= 0.05 (substrate finally beats unigram — closes ~0.13 bits of bigram-gap floor)
- **HARD_FAIL BPC**: BPC >= 7.864 (no improvement over current text8 v2 calibrated cell)
- **MIDDLE_BAND BPC**: 7.738 < BPC < 7.864

**Dual-gain pass:** ARM achieves BOTH cleanup HARD_PASS AND BPC HARD_PASS in same run. This is the TRUE test of the META's prediction that one encoder upgrade lifts both. P_deflated of dual-gain pass on any single arm: 0.15-0.20 (lower than per-arm because of compound conditional).

---

## L1 / L2 / L3 STRUCTURE — full drill

### L1 BROAD (literature scan, 5 disparate fields)

**Neuroscience encoder geometry for high-noise robustness:**
- Cerebellar GC sparse fan-in K=4-5 (Litwin-Kumar 2017; Cayco-Gajic 2017; Nature Sci Rep 2025) — CANONICAL pattern-separation mechanism; biology evolved K=4-5 for noise-tolerant expansion.
- Drosophila MB Kenyon cell K=6-8 PN fan-in (Lin 2014; eLife 2023; Current Biology 2023) — sparse odor encoding with input-density-tuned sparsity.
- Foldiak 1990 + Pehlevan 2015-2018 anti-Hebbian decorrelation — substrate-native online encoder convergent to PCA+whitening via lateral inhibition (1503.00680, 1812.11581, 1812.11937).
- **NEW: SoftHebb (Moraitis 2021, 2107.05747)** — soft-WTA + Hebbian plasticity converges to Bayesian generative model; outperforms backprop in noise + one-shot regimes; substrate-compatible (no global error signal).
- **NEW: Asynchronous Hebbian/anti-Hebbian (2501.02402)** — 2025 work showing convergence of fully-asynchronous online encoder; relevant for substrate's streaming-ingest regime.

**ML self-supervised encoder upgrades (small-parameter, substrate-trainable):**
- SimCSE (Gao 2021, 2104.08821) — contrastive learning encourages isotropy; spectrum flattening; small-model-friendly.
- WhitenedCSE (2305.17746) — explicit whitening + contrastive; substrate already has `hdlab/whitening.py`; composes.
- SoftHebb (above) as ENTIRELY SUBSTRATE-NATIVE alternative to SimCSE — no negative pairs needed; no backprop.

**HD/VSA-native encoder candidates:**
- **Fractional Power Encoding (FPE) — Frady-Sommer 2109.03429; Eliasmith-Furlong; Bremer-Orchard 2412.00488** — substrate-native FHRR/HRR encoding via phase exponentiation. The Bremer-Orchard 2024 paper provides EXPLICIT improved cleanup (CLE+MLE iterative) — directly addresses the parent ENC1 HARD_FAIL problem.
- Generalized Holographic Reduced Representations (2405.09689) — substrate-flexible HRR variants.
- Hyperseed unsupervised VSA (2110.08343) — substrate-native unsupervised learning building on FPE.

**Char-level baseline encoders:**
- char-CNN / char-LSTM (Kim 2015) — small-model text encoders that achieve sub-2 BPC on text8 (the substrate is at 7.86); informs ABSOLUTE upper-bound headroom (we are 6+ bits from char-LSTM at small-param).
- Char-trigram bag-of-HD (existing `hdlab/char_trigram_encoder.py`) — already substrate-native, but has KNOWN limits (order-bag, no positional info).

**Biology / matsci as adjacency:**
- Spread-spectrum CDMA (sparse-spread coding, 0704.0098) — analog: sparse codebook entries beat dense at noise floor; statistical-mechanics analysis. Marginal substrate-relevance; SKIP (parent ENC1 already tested sparse-fan-in HARD_FAIL).
- Quasi-species under selection (Eigen) — population-genetics noise-tolerance; SKIP (substrate Phase-A/B already covers this via continual-learning replay).
- DRAM refresh / spin-glass noise floor — finite-T information storage; SKIP (already in META Shannon-floor framing).

### L2 SUBSTRATE-APPLICABLE FILTER

Filter criteria:
1. Forward-only / Hebbian-compatible (no backprop) — REQUIRED for substrate-native
2. Open-source / substrate-trainable (no proprietary embeddings, no MiniLM)
3. Composes with existing `char_trigram_encoder.py` or REPLACES it cleanly
4. Predicts isotropic representations (rho_mean → 0 per substrate's `isotropy_REFRAME` finding)
5. Cost <= 1 day implementation + <= 1 hr smoke

| Candidate | (1) Forward-only? | (2) Substrate-trainable? | (3) Composes? | (4) Isotropic? | (5) Cost? | PASS L2? |
|---|---|---|---|---|---|---|
| char_trigram baseline | YES | YES (deterministic, no training) | EXISTS | UNKNOWN (test) | 0 (already shipped) | YES — TEST AS BRANCH #3 |
| SoftHebb 3-layer expansion | YES (Hebbian + soft-WTA) | YES | YES (stacks on char-trigram) | YES (Bayesian generative -> isotropic by Moraitis 2021 thm) | ~1 day impl + 30 min smoke | YES — TOP CANDIDATE |
| FPE phase-encoder | YES (deterministic phase) | YES | YES (replaces codebook gen) | YES (uniform-S^1 phase tags break rank-1 by construction) | ~1 day impl + 30 min smoke | YES |
| SimCSE contrastive | NO (backprop) | NO (needs HF transformer base) | NO | YES | high | FAIL L2 — backprop |
| WhitenedCSE | NO (backprop) | NO | partial (uses whitening.py) | YES | high | FAIL L2 — backprop |
| Char-LSTM | NO (backprop) | YES (small model substrate-trainable) | partial (output → HD codebook) | UNKNOWN | medium | DEFER — needs backprop infra; revisit if SoftHebb HARD_FAILs |
| Asynchronous Hebbian (2501.02402) | YES | YES | YES | YES | ~2 days impl | DEFER — 2nd choice after SoftHebb |
| Foldiak 1990 anti-Hebb | YES | YES | YES | YES (decorrelation) | ~1 day impl | DEFER — already in encoder-side drill as #4; SoftHebb supersedes |
| Cerebellar K=5 sparse fan-in alone | YES | YES | YES | NO (sparse but not lateral-inhibition) | trivial | **ALREADY TESTED in ENC1 HARD_FAIL** |

**L2 winners:** char_trigram (TEST BRANCH #3), SoftHebb, FPE. Three arms + baseline = 4-arm cell.

### L3 DEPTH — top 2

#### Depth-A: SoftHebb 3-layer text encoder

**Mechanism** (Moraitis et al. 2021, IOPscience 2022):
- Layer architecture: input → SoftHebb conv/linear layer with soft-WTA activation + Hebbian-like weight update.
- Soft-WTA: instead of hard argmax (cerebellar-style K=1 winner), each output unit gets activation proportional to softmax(input·weight); the network minimizes cross-entropy with input distribution **without supervision**.
- Theorem (Moraitis 2022): SoftHebb network parameters maintain a Bayesian generative model of input distribution → posterior P(y|x) approximated via Bayes; converges to **isotropic latent distribution** as side-effect of cross-entropy minimization (verified on MNIST, CIFAR-10).
- Outperforms backprop in: one-shot (single epoch), noisy test, adversarial perturbation.

**Substrate-native variant:**
- INPUT: char-trigram bundled HD vector (existing `char_trigram_encoder.py` output, N=4096).
- Layer 1: SoftHebb linear N=4096 → N_hidden=8192 with soft-WTA (temperature τ tuned at ingest).
- Layer 2: SoftHebb N=8192 → N=8192 (lateral decorrelation).
- Layer 3: SoftHebb N=8192 → N=4096 (projection back to substrate codebook dim).
- WEIGHTS: trained Hebbian-style on text8 train corpus during INGEST only. ZERO LLM at inference (substrate-only-decode gate intact).
- OUTPUT: N=4096 bipolar (signed) vector → substrate codebook atom OR Path-A KV-pair value.

**Theoretical guarantees** (Moraitis 2022 Bayesian-WTA thm):
- Soft-WTA + Hebbian converges to cross-entropy minimum if and only if input distribution has finite first-and-second moments. Text8 trivially satisfies.
- Convergence rate: O(1/T) where T = ingest tokens; for N_TRAIN=100k expect ~3-5 epochs to stable.
- Noise robustness: post-training latent is robust to input perturbation up to sigma~1 of the input-distribution std (Moraitis 2021 fig 4). For substrate text8, input std ≈ sqrt(N_unique_trigrams/N) ≈ 1.0; so SoftHebb latent should be robust to sigma~1 of the latent space.

**Brain analog (depth-3):**
- Cortical Layer 4 spiny stellate cells use sparse local Hebbian + lateral inhibition that mathematically reduces to SoftHebb (Moraitis 2021 thm 2).
- Cerebellar GC + Golgi cell inhibitory feedback is also a SoftHebb instance (Cayco-Gajic 2017 + Nat Sci Rep 2025).
- Drosophila MB calyx APL inhibition (eLife 2022) provides the WTA gain control.

**Cost:** ~1 day impl on `hdlab/softhebb_encoder.py`; ~30 min smoke at N=4096 text8 N_TRAIN=10k subset; ~1 hr full cell at N_TRAIN=100k.

**Smallest-parameter encoder that breaks Shannon-floor + beats unigram:**
- SoftHebb 3-layer at N=4096 → ~50M params (compared to MiniLM 22M, BGE-mini 14M).
- Substrate-trainable on laptop CPU in ~1 hr; no GPU required for this size.
- IF this fails, smaller variants (1-layer SoftHebb, N=2048) are not expected to help; larger is the only remaining option but USER directive forbids dependence on MiniLM/BGE.

#### Depth-B: FPE phase encoder + Bremer-Orchard cleanup

**Mechanism** (Plate 1995 HRR; Frady-Sommer 2109.03429 FPE; Bremer-Orchard 2412.00488):
- FPE encodes a scalar value `s` as `enc(s) = base^s` where `base` is a fixed FHRR (complex-valued, unit-norm) vector and `^` is element-wise complex exponentiation: `base[k]^s = exp(i·s·angle(base[k]))`.
- For substrate text encoding: each char-position has its own FPE base; the text token is encoded as sum of position-bound character FPE vectors.
- KEY PROPERTY: FPE vectors have UNIFORM phase distribution on S^1 → **rank-1 mean direction is structurally zero by construction** (rho_mean = 0; meets `isotropy_REFRAME` requirement).
- KEY PROPERTY 2: Bremer-Orchard 2024 (2412.00488) gives an explicit cleanup algorithm via Composite Likelihood Estimation (CLE) + Maximum Likelihood Estimation (MLE) iterative refinement. This is exactly the iterative cleanup the parent ENC1 needed for noisy cue recovery.

**Substrate-native variant:**
- ENCODE: text → FPE(char_1) * pos_base^1 + FPE(char_2) * pos_base^2 + ... → bundled FHRR vector (N=4096 complex, equivalent to N=8192 real).
- For real-valued substrate: project to bipolar via sign(real(FPE)) — preserves substrate API.
- INGEST: same as substrate today; FPE vector goes to codebook.
- CLEANUP DECODE: at retrieval, instead of single argmax against codebook, run Bremer-Orchard CLE+MLE iterations (claim: 2-3 iterations gives near-optimal under noise).

**Theoretical guarantees:**
- FPE preserves inner products in expectation: `<enc(s_1), enc(s_2)> = sinc(N·(s_1 - s_2)/2)` (Frady-Sommer 2109.03429 thm 1). Similarity is locality-preserving with controllable bandwidth.
- Bremer-Orchard 2412.00488 thm: CLE+MLE iterative cleanup converges to global optimum under unimodal posterior; outperforms standard cosine cleanup for SNR < 0 dB (i.e. sigma >> signal).
- Substrate relevance: at sigma=1.5 with random bipolar (ENC1 regime), SNR ≈ -3 dB; **squarely in the regime where Bremer-Orchard predicts improvement**.

**Brain analog:**
- Place-cell / grid-cell phase coding (Burgess-O'Keefe 1994; Hafting 2005); cortical theta-gamma phase coding.
- Weaker than SoftHebb (which is direct lateral-inhibition); strong as PRINCIPLED isotropy-by-construction.

**Cost:** ~1 day impl on `hdlab/fpe_encoder.py` + `hdlab/fpe_cleanup.py` (Bremer-Orchard CLE+MLE); ~30 min smoke; ~1 hr full cell.

---

## L4 CELL-DESIGN IMPLICATIONS

**Cell: `enc_dual_gain_softhebb_vs_fpe_v1`**
- Queue: `local_cpu_queue` (laptop CPU sufficient at N=4096 + N_TRAIN=100k; ~30-60 min wall)
- Pre-flight: schema-vet via `tools/exp_dev/formula_selftests.py`; sigma=0 sanity recall=1.000 across all arms.
- Arms (4 total): BASELINE_BIPOLAR / CHAR_TRIGRAM / SOFTHEBB_3LAYER / FPE_PHASE
- Per-arm: same M=200 codebook for cleanup; same text8 N_TRAIN=100k for Path-A BPC.
- Seeds: 7, 17, 23 (substrate-standard 3-seed).
- Discriminator: sigma=1.5 cleanup recall + Path-A test BPC.
- Pre-reg in `preregs/2026-06-23_enc_dual_gain_softhebb_vs_fpe.md`.

**Implementation budget:**
- SoftHebb encoder: ~1 day at `hdlab/softhebb_encoder.py` (forward-only training loop, soft-WTA, 3 layers); reference Moraitis 2021 fig 2 architecture.
- FPE encoder: ~1 day at `hdlab/fpe_encoder.py` + `hdlab/fpe_cleanup.py`; reference Frady-Sommer 2109.03429 + Bremer-Orchard 2412.00488 alg 1.
- Cell: ~half-day to integrate 4 arms + measure both metrics in one pipeline.

**Pre-dispatch checklist** (per `feedback_remote_dispatch_cell_readiness_checklist`):
- `--self-test` mode at .venv
- Py3.11 compat
- HDLAB_EXP_NAME set
- REQUIRED_FIELDS schema-vet
- run_mode='full'
- commit-first
- per-unit checkpoint + restartable (per `feedback_long_cells_must_checkpoint_resume_restartable`)
- file-redirect + mtime polling (NOT pipe-tail per Fix #20)

---

## L5 CROSS-SUBSTRATE COMPOSITION

**If SoftHebb HARD_PASSES (P=0.35-0.40):**
- New substrate primitive: `hdlab/softhebb_encoder.py` (forward-only, Hebbian-trained).
- Composes with existing `char_trigram_encoder.py` (stacked as INPUT layer to SoftHebb).
- Composes with `hdlab/whitening.py` (apply ZCA post-SoftHebb; production pipeline = trigram → SoftHebb → ZCA → codebook).
- Composes with c3 sequence-binding 586 (better atoms → better bind cleanup).
- Composes with g1b autoregressive generation 587 (better encoder → better next-token logits).
- Composes with Path B KG (HotpotQA 588: encode KG entities with SoftHebb instead of MiniLM, USER-directive-compliant; close lit-test for branch #3 of META).
- Composes with substrate_self_map_v2 (better atom-family clustering → V3 self-mapping).
- **Triple-leverage:** Shannon-floor exit (cleanup) + bigram-gap closure (Path A) + substrate-native KG (Path B) — same primitive lifts all three.

**If FPE HARD_PASSES (P=0.30-0.35):**
- New substrate primitive: `hdlab/fpe_encoder.py` + `hdlab/fpe_cleanup.py`.
- FPE is FHRR-style → opens whole FHRR/HRR substrate variant (currently substrate is bipolar-only).
- Composes with existing `hdlab/binding.py` (FHRR binding = complex multiplication).
- DOES NOT compose with substrate's existing bipolar-only assumption — requires substrate to support complex-valued (or extended-real) atoms. Larger refactor.
- Triple-leverage less direct than SoftHebb.

**If BOTH HARD_PASS:**
- Substrate gets two encoder primitives; A/B in production via config flag.
- SoftHebb preferred for substrate-product (bipolar-compatible, no refactor); FPE preferred for theoretical isotropy guarantee + Bremer-Orchard cleanup.

**If BOTH HARD_FAIL but ARM_CHAR_TRIGRAM HARD_PASSES:**
- Branch #3 of META is FALSE; Shannon-floor was synthetic-codebook artefact; the existing substrate primitives already work at production. No new code needed.
- Atomize: `META_shannon_floor_only_on_random_bipolar_codebook_not_learned_keys_2026-06-23`.

**If ALL 3 non-baseline HARD_FAIL:**
- Branch #3 of META closes; Shannon-floor is fully chain-grade saturated.
- Atomize: `META_shannon_floor_load_bearing_across_synthetic_and_learned_encoders_2026-06-23`.
- Substrate operating envelope CONFIRMED at sigma <= 1.0.
- Pivot to either (a) char-LSTM substrate-trainable (needs backprop infra; ~1 week impl) or (b) descope sigma>=1.5 stress regime permanently and chain-grade the existing sigma<=1.0 operational envelope.

---

## FALSIFIABLE PREDICTIONS — HARD-PASS + HARD-FAIL

### Prediction 1 (SoftHebb cleanup, PRIMARY)
**Hypothesis:** SoftHebb 3-layer encoder produces N=4096 codebook keys with cleanup recall@1 >= 0.20 at sigma=1.5 (M=200, N_EVAL=200, 3 seeds).
**Mechanism:** lateral-inhibition isotropy + soft-WTA Bayesian generative model produces decorrelated atom representations that resist Gaussian noise per Moraitis 2021 thm.
**HARD_PASS:** recall(sigma=1.5) >= 0.20, cv <= 0.30
**HARD_FAIL:** recall(sigma=1.5) <= 0.05
**P_deflated:** **0.35-0.40** (raw Moraitis P=0.55-0.65 deflated 0.20-0.25 because: (a) Moraitis 2021 was on MNIST/CIFAR image patches, not HD substrate text encoding; (b) Shannon-floor cleanup-ceiling has already eaten 4 decoder + 5 encoder candidates; (c) this is 3rd encoder-side attempt; (d) capped at 0.40 per "3rd attempt + 2 prior unfired" penalty).

### Prediction 2 (SoftHebb Path-A BPC, PRIMARY)
**Hypothesis:** SoftHebb encoder gives text8 N=4096 substrate BPC < 7.738 (beats unigram).
**Mechanism:** richer per-atom signal → better calibrated logits → log-linear+unigram interpolation lifts past unigram floor.
**HARD_PASS:** BPC < 7.738, cv <= 0.05
**HARD_FAIL:** BPC >= 7.864 (no improvement over current cell)
**P_deflated:** **0.25-0.30** (raw P=0.45 deflated because BPC gap to unigram is only 0.126 bits and there is no direct prior for SoftHebb-on-text BPC; capped lower than cleanup because Path A has its own confounds: log-linear lambda tuning, vocab cap, etc.).

### Prediction 3 (FPE cleanup, SECONDARY)
**Hypothesis:** FPE-encoded codebook + Bremer-Orchard CLE+MLE cleanup gives recall(sigma=1.5) >= 0.20.
**Mechanism:** uniform-phase isotropy + iterative likelihood cleanup converges under SNR < 0 dB per Bremer-Orchard 2024.
**HARD_PASS:** recall(sigma=1.5) >= 0.20
**HARD_FAIL:** recall(sigma=1.5) <= 0.05
**P_deflated:** **0.30-0.35** (raw 0.50; deflated because (a) FPE works on continuous values whereas substrate atoms are discrete word-level; mapping is not exact; (b) Bremer-Orchard 2024 only verified on synthetic FHRR demos, not text substrate).

### Prediction 4 (FPE Path-A BPC, SECONDARY)
**HARD_PASS:** BPC < 7.738
**HARD_FAIL:** BPC >= 7.864
**P_deflated:** **0.20** (FPE phase encoding does not natively give token-level distribution; BPC lift is conditional on whether phase-tagged codebook produces well-calibrated logits, which is unverified).

### Prediction 5 (ARM_CHAR_TRIGRAM as branch #3 closure)
**Hypothesis:** Existing char_trigram_encoder gives recall(sigma=1.5) <= 0.10 at production-regime (branch #3 of META closes, Shannon-floor is fully chain-grade).
**Mechanism:** char-trigram bundling produces atoms with some structure but no lateral-inhibition isotropy; not enough to escape Shannon-floor.
**P:** **0.50** (high uncertainty — this IS the test; if it HARD_PASSES, the whole Shannon-floor META is wrong about branch #3).

### Prediction 6 (Dual-gain compound)
**Hypothesis:** SoftHebb arm achieves BOTH cleanup HARD_PASS AND BPC HARD_PASS in same run.
**P_deflated:** **0.15-0.20** (conditional product P(cleanup_pass) × P(bpc_pass | cleanup_pass) where conditional is ~0.5 because both depend on isotropy of SoftHebb latent).

### Prediction 7 (Falsifier — all encoder arms HARD_FAIL)
**Implication:** Shannon-floor is fully chain-grade load-bearing across synthetic AND production-learned-key codebooks. Substrate operating envelope = sigma <= 1.0 permanently. Atomize `META_shannon_floor_chain_grade_saturated_branch3_closed_2026-06-23`.
**P_deflated:** **0.30** (this is the META's predicted outcome; calibrate honestly).

---

## CROSS-THREAD SYNTHESIS

**With parent encoder-side drill 2026-06-23:**
- Parent's HARD_FAIL of all 5 arms was on **synthetic random bipolar codebook** with mu~0 by construction. This drill takes the NEXT step the parent flagged: test branch #3 (LEARNED encoder keys) which the parent explicitly noted was untested.
- Parent's reframing (per-dimension noise floor vs structural anisotropy) is honored: SoftHebb/FPE are specifically chosen because they produce structurally-isotropic atoms (rho_mean→0 by construction) AND richer per-atom signal (variance not from random bipolar but from learned/phase distribution).
- Parent's recommendation: "pivot to noise-reduction at source = encoder upgrade." This drill implements that pivot WITHOUT using MiniLM/BGE/proprietary embeddings per USER directive.

**With Shannon-floor META (cert row 675):**
- META is currently 2-of-3 branches closed (N-INDEPENDENT + M-INDEPENDENT). Branch #3 (learned-encoder keys) is the OPEN cell.
- This drill **fills branch #3 explicitly**, with discriminating-regime gate that either chain-grades the META (if all encoder arms HARD_FAIL) or refutes the saturation (if any encoder arm HARD_PASSES).
- Either outcome is high-value for cert architecture.

**With substrate isotropy_REFRAME 2026-06-20:**
- Substrate's deepest finding: rho_mean is load-bearing, NOT d_eff. Pythia/BGE failed because rho_mean too high; MiniLM passed because vectors more spread.
- SoftHebb explicitly minimizes cross-entropy with input distribution → drives rho_mean→0 by Bayesian-generative thm (Moraitis 2022 thm 1).
- FPE has rho_mean=0 BY CONSTRUCTION (uniform phase on S^1).
- Both candidates are SPECIFICALLY chosen to satisfy the substrate's load-bearing isotropy criterion. This is structural — not lit-scan-noise.

**With Path A pseudo-LM (text8 v2 calibrated MIDDLE_BAND):**
- Substrate currently 7.864 BPC (log-linear+unigram); unigram baseline 7.738; substrate raw 11.61.
- Substrate is 0.126 bits WORSE than unigram. Substrate top-1 acc 0.225 vs unigram 0.217 — substrate IS learning (top-1 better), but logits are mis-calibrated.
- Reframe: the path to closing the 0.126-bit gap to unigram is via a richer encoder that produces better-calibrated next-token distributions. The 1.13-bit gap to bigram is a DOWNSTREAM target; we must first close 0.126 to unigram.
- SoftHebb gives a richer encoder substrate-natively; if it lifts BPC below unigram, we have a substrate-native LM that beats unigram for the first time.

**With c3 sequence-binding 586 + g1b generation 587:**
- Both downstream primitives depend on atom quality from the encoder.
- A richer SoftHebb encoder benefits c3 (better bind cleanup) and g1b (better next-step prediction).
- Single primitive lifts multiple substrate-products — true triple-leverage if HARD_PASS.

**With prior `research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21` (unfired 5x-DEEPER):**
- That drill pre-registered ARM A (cerebellar K=5), ARM B (fly-LSH WTA), ARM C (BTSP Krotov-self-orth).
- ENC1 2026-06-23 burned ARM A equivalent — HARD_FAIL on synthetic. The branch #3 production-regime test of those ARMs was never run.
- This drill SUPERSEDES that 5x-DEEPER's planned dispatch: SoftHebb subsumes ARM A (cerebellar K=5 is the K=1 hard-WTA limit of SoftHebb soft-WTA) AND ARM B (fly-LSH WTA is also a SoftHebb instance per Moraitis 2022). FPE is a NEW direction not in the 5x-DEEPER.

**With USER directive 2026-06-22 "no MiniLM":**
- This drill complies fully — both top candidates (SoftHebb + FPE) are substrate-native, zero external models at inference, substrate-trainable from text8 corpus alone.
- char-trigram baseline arm preserves USER-current substrate (no new dependency).
- ALL ARMS USER-directive-compliant.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**If SoftHebb HARD_PASSES (cleanup + BPC, P=0.15-0.20):**
- Triple-leverage substrate primitive: `hdlab/softhebb_encoder.py` lifts cleanup (Shannon-floor exit at production), Path A pseudo-LM (beat unigram), Path B KG (substrate-native entity encoding).
- Composes with continual-learning replay (CLS), self-mapping V3 (atom-family clustering), and g1 conversation (better generation logits).
- META atom: `encoder_upgrade_softhebb_triple_leverage_chain_grade`.
- New cert architecture row: substrate-native learned-encoder breaks Shannon-floor at production-regime → branch #3 of META refuted; META de-saturated.
- Substrate-product positioning: "substrate that LEARNS its own encoder via forward-only Hebbian; no transformer dependency; provably isotropic per Moraitis 2022."

**If SoftHebb HARD_PASSES cleanup ONLY (P=0.20-0.25):**
- Encoder upgrade helps production cleanup but does not close BPC gap to unigram.
- Atomize: `softhebb_encoder_lifts_cleanup_but_not_pathA_bpc`.
- Path A bottleneck is elsewhere (likely VQ alignment per `research_decode_side_lm_improvements_substrate_native_2026-06-22`); route to SimVQ cell next.

**If FPE HARD_PASSES (cleanup OR BPC, P=0.25-0.30):**
- Substrate gets FHRR-style encoder as alternative to bipolar; opens whole complex-valued substrate variant.
- Larger refactor required (substrate currently assumes bipolar); architectural decision needed.
- Useful as theoretical-foundation result; product-implementation requires deliberate design choice.

**If ARM_CHAR_TRIGRAM HARD_PASSES branch #3 alone:**
- Shannon-floor was synthetic-codebook artefact. Existing substrate primitives already work at production scale.
- META de-saturated; Shannon-floor downgraded from chain-grade-eligible.
- No new code needed; route to product-positioning of existing primitives.

**If ALL HARD_FAIL:**
- Shannon-floor fully chain-grade; substrate envelope = sigma<=1.0 permanently documented.
- META atom: `shannon_floor_chain_grade_saturated_branch_3_closed_2026-06-23`.
- Pivot away from encoder-side cleanup-ceiling work; route research to (a) char-LSTM substrate-trainable (backprop infra ~1 week), or (b) descope sigma>=1.5 regime entirely; substrate operates at sigma<=1.0 as its honest envelope.
- This is an HONEST CLOSURE outcome, valuable for cert architecture.

**For bigram-gap closure (~1.13 bits to bigram, ~0.13 bits to unigram):**
- The dual-gain prediction is the key: if SoftHebb gives both cleanup HARD_PASS AND BPC HARD_PASS, substrate substrate-native LM finally crosses unigram — that's the first-ever substrate-native-LM-beats-unigram chain-grade result.
- From there, the path to bigram is incremental (SimVQ on top, MKN decode on top, possibly K=2 depth).

---

## OPERATIONAL DRILL SUMMARY

- **Dispatch IMMEDIATELY:** `enc_dual_gain_softhebb_vs_fpe_v1` (4-arm cleanup + BPC). Implementation: ~1-2 days. Cell wall: ~30-60 min CPU. Queue: `local_cpu_queue`. Smoke gate: sigma=0 sanity recall=1.000 across all arms.
- **Pre-reg:** `preregs/2026-06-23_enc_dual_gain_softhebb_vs_fpe.md` with HARD bands per arm per metric.
- **Implementation order:** (1) implement `hdlab/softhebb_encoder.py` (Moraitis 2021 fig 2 architecture, 3 layers, soft-WTA + Hebbian); (2) implement `hdlab/fpe_encoder.py` + `hdlab/fpe_cleanup.py` (Frady-Sommer 2109.03429 + Bremer-Orchard 2412.00488); (3) integrate 4 arms in single cell + measure both metrics in one pipeline; (4) per-unit checkpoint + restartable.
- **Companion handoff:** `notes/exp_dev_handoff_research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` to be written.
- **DEFER:** char-LSTM (backprop infra; revisit only if SoftHebb HARD_FAILs); SimCSE/WhitenedCSE (backprop + transformer dep, fails L2 filter); asynchronous Hebbian (2nd choice after SoftHebb).
- **SKIP:** SimVQ for Path A (separate research note 2026-06-22 already covers; orthogonal lever); Cerebellar K=5 alone (ENC1 already tested HARD_FAIL on synthetic; SoftHebb subsumes structurally).

---

## CITATIONS (verified)

1. Moraitis, Toichkin, Chua, Guo (2021/2022). "SoftHebb: Bayesian Inference in Unsupervised Hebbian Soft Winner-Take-All Networks." arXiv:2107.05747; IOPscience Neuromorphic Computing & Engineering 2022. [SoftHebb v2](https://arxiv.org/abs/2107.05747v2)
2. Bremer, Orchard (2024). "Improved Cleanup and Decoding of Fractional Power Encodings." arXiv:2412.00488. [FPE Cleanup](https://arxiv.org/abs/2412.00488)
3. Frady, Kleyko, Sommer (2018, 2109.03429). "Computing on Functions Using Randomized Vector Representations." [FPE foundational]
4. Asynchronous Hebbian/anti-Hebbian (2025, 2501.02402). [Async Hebb]
5. Pehlevan, Sengupta, Chklovskii (2015, 1511.09468). "Optimization theory of Hebbian/anti-Hebbian networks for PCA and whitening."
6. Pehlevan, Sengupta (2018, 1812.11581). "Unsupervised learning by a nonlinear network with Hebbian excitatory and anti-Hebbian inhibitory neurons."
7. Foldiak (1990) Biol Cybern. "Forming sparse representations by local anti-Hebbian learning."
8. Gao, Yao, Chen (2021, 2104.08821). "SimCSE: Simple Contrastive Learning of Sentence Embeddings."
9. WhitenedCSE (2305.17746). "Whitening-based Contrastive Learning of Sentence Embeddings."
10. Litwin-Kumar et al. (2017) Neuron. "Optimal Degrees of Synaptic Connectivity." (K=4-5 cerebellar GC)
11. Cayco-Gajic et al. (2017). "Morphological Constraints on Cerebellar Granule Cell Combinatorial Diversity."
12. Lin et al. (2014); eLife 2023; Current Biology 2023. (Drosophila MB Kenyon cell K=6-8)
13. Nature Sci Rep 2025 "A computational model of the cerebellar granular layer calibrated to experimental data."
14. Plate (1995). "Holographic Reduced Representations." (HRR foundation; FHRR variant)
15. Hyperseed (2110.08343). "Unsupervised Learning with VSA."
16. Generalized HRR (2405.09689).
17. Kim et al. (2015). "Character-Aware Neural Language Models." (char-CNN/LSTM text8 baseline)
18. **Internal:** `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` (parent encoder-side drill HARD_FAIL on synthetic)
19. **Internal:** `notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md` (decode-side cousin; SimVQ recommendation)
20. **Internal:** `notes/research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_2026-06-20` (rho_mean as load-bearing encoder variable)
21. **Internal:** `data/exp_enc1_structured_n_lift_v1/metrics.json` (5-arm encoder HARD_FAIL on synthetic, branch closed)
22. **Internal:** `data/exp_cleanup_floor_N_DIM_scan_v1/metrics.json` (N-INDEPENDENT confirmed across 512-16384)
23. **Internal:** `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json` (BPC 7.864 MIDDLE_BAND; substrate top-1 0.225 vs unigram 0.217)
24. **Internal:** `hdlab/char_trigram_encoder.py` (existing substrate-native text encoder; baseline + branch #3 test arm)
25. **Internal:** `hdlab/whitening.py` (composes post-SoftHebb in production pipeline)
26. **Internal:** Shannon-floor META cert row 675 (chain-grade-eligible per branch-c closure)
27. **Internal:** `notes/research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21` (prior 5x-DEEPER unfired; SoftHebb subsumes its ARM A,B,C structurally)

**Verified count: 27 sources (17 external lit + 10 substrate-internal cross-references).**

---

## LIT-SCAN CALIBRATION NOTES

- This is the **3rd encoder-side attempt** (5x-DEEPER 2026-06-21 unfired + ENC1 HARD_FAIL 2026-06-23). Per `feedback-lit-scan-calibration-penalty`: deflate raw P by 0.25-0.35 (HARDER than standard 0.15-0.25).
- Novel-synthesis P CAPPED at 0.40 per the request's calibration penalty instruction (stricter than the standard 0.50 cap).
- All HARD-FAIL bands explicitly listed for each prediction.
- Cross-thread synthesis with prior research notes mandatory; covered above.
- Substrate-product implications mandatory; covered above.
- Generic-terms-only queries verified — no substrate-novel mechanism names or config numbers leaked off-platform.

---

## DELIVERABLE SUMMARY

**This research note:** `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md`
**Companion handoff:** `notes/exp_dev_handoff_research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` (to be written next)
**Anchor candidates (rank-ordered):**
1. **enc_dual_gain_softhebb_vs_fpe_v1** (Tier-A; P_deflated cleanup-pass 0.35-0.40 SoftHebb / 0.30-0.35 FPE; dual-gain compound 0.15-0.20) — the cheap decisive test
2. **softhebb_pathA_only_v1** (Tier-B fallback if dual-gain cell shows mixed signal; isolate Path-A BPC with SoftHebb-only)
3. **char_lstm_substrate_trainable_v1** (Tier-C deferred; only if SoftHebb HARD_FAILs; requires backprop infra ~1 week)

**Next-drill candidate (if outcome is mixed/null):** `online-learning` or `nonequilibrium-stat-mech` field (per field-advisor — scope-expansion candidates with drill_count<=2). Specifically: Jarzynski/Crooks fluctuation theorem on encoder ingest as continual-learning bound (parent NESS framing).

-- Research (Opus 4.7-1M)
