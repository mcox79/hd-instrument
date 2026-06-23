# Research: 5x DEEPER substrate-as-LM drill — closing the bigram-gap (Path A pseudo-LM)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7)
**Trigger:** Path A pseudo-LM v2 calibrated landed MIDDLE_BAND BPC=7.864 (log-linear interp lambda=0.1 with unigram). Substrate raw BPC=11.614; substrate-temp-calibrated BPC=11.266; unigram baseline BPC=7.738; word-bigram BPC ~6.6 on text8. We are 0.126 bits BEHIND unigram standalone and 1.26 bits behind bigram. The log-linear lambda=0.1 solution means **unigram is the dominant signal in the calibrated arm; substrate adds at most ~0.05-0.10 bits of signal lift**. To be "an LLM", substrate must beat unigram standalone, then bigram. This is the V2 gap.
**Drill type:** 5x deeper drill on the substrate-as-LM gap; novel-synthesis-cap; lit-scan calibration penalty applied.
**Discipline:** query-privacy generic terms only; deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD_FAIL thresholds mandatory.

---

## HEADLINE

**The substrate-as-LM gap is structural, not calibration**: BPC of 11.614 raw vs unigram 7.738 means the substrate's softmax-over-next-token distribution has 3.876 bits of entropy excess; calibration (temperature, log-linear) closes 3.75 of those 3.876 bits BY SHIFTING WEIGHT ONTO THE UNIGRAM PRIOR (best lambda=0.1, i.e., **only 10% substrate, 90% unigram**). The substrate contribution at the optimal point is at most 0.05-0.10 bits — within noise of unigram. The substrate has *learned bigram top-1 structure* (raw_acc 0.225 vs unigram 0.217) but its distribution is mass-concentrated on one wrong neighbor, making BPC nearly worst-case. **The fix is NOT more calibration. The fix is moving from rank-1 Hebbian outer product to a HIGHER-ORDER predictive operator that contributes well-calibrated mass across the second-and-lower-rank candidates.**

**Top-2 next dispatch (rank-ordered, P deflated):**
1. **PC1 — substrate-native hierarchical-bigram with Eugenio-style smoothness constraint (renormalization-group tokenizer)** at vocab cap V=4000, N_DIM=4096; learns bigram-of-bigrams + 3-gram via composition; uses existing `hdlab/predictive_coding.py` + `hdlab/char_trigram_encoder.py`. **P_deflated=0.30** (capped from raw 0.50 because Eugenio 2025 published NO BPC numbers — Alice in Wonderland only — and lit verification is null for "forward-only Hebbian LM beats unigram on text8"). ~1hr GPU smoke; ~6hr GPU full. **HARD_PASS: BPC <= 7.50** (>=0.2 bits below unigram, with cv<=0.10 across 3 seeds). **HARD_FAIL: BPC >= 7.738** (cannot beat unigram even with the hierarchical n-gram refinement).
2. **PC2 — substrate-native CA3-style heteroassociative bigram-completion + Hopfield autoassociative cleanup composition** at same V=4000, N_DIM=4096; uses `hdlab/sequence_memory.py` + `hdlab/iterative_attractor.py`; tests whether autoassociative-cleanup post-binding rescues per-token distribution calibration (collapses spurious mass onto chain-attractor basin). **P_deflated=0.25**. ~1.5hr GPU smoke. HARD_PASS / HARD_FAIL same as PC1.

**Critical reframe:** The substrate's BPC fail is the mathematical signature of **rank-1 Hebbian's structural incompatibility with Shannon-entropy-defined targets**: BPC measures log P over the FULL distribution, but rank-1 outer product (next_token = argmax of `E[w_{t+1}] outer E[w_t]`) projects to a spike-distribution by construction. Eugenio 2025 (arxiv:2503.02057) — the closest published precedent — explicitly does NOT use BPC and does NOT compare to unigram/bigram; their architecture builds n-gram-of-n-gram via renormalization-group composition, which IS a structural escape from rank-1. The substrate has the right primitives (`predictive_coding.py`, `sequence_memory.py`, `char_trigram_encoder.py`) to build the same composition; the v2 calibrated cell only tested calibration, not composition.

**Calibrated probability of closing the unigram gap by ANY single mechanism in this drill:** 0.40 (P-bounded by novel-synthesis cap 0.50, deflated 0.10 for hard-fail-not-yet-pre-tested).
**Calibrated probability of closing the bigram gap (~1.26 bits to text8 word-bigram BPC):** 0.20 (deflated 0.30 from raw 0.50; the bigram gap is large and no published precedent exists for forward-only Hebbian beating word-bigram).
**Calibrated probability of HARD_FAIL on all top-2 candidates:** 0.35-0.45 (we may be at the Shannon floor of rank-1-plus-composition; deeper architectural change may be required).

---

## L1: Literature broad scan (forward-only Hebbian / VSA / brain-grounded LM candidates)

### L1.1 — Eugenio 2025 "Hebbian learning the local structure of language" (arxiv:2503.02057)

**Closest published precedent to Path A.** P. Myles Eugenio (March 2025). Forward-only unsupervised Hebbian; hierarchical n-gram tokenizer via renormalization-group composition; tested on Alice in Wonderland and synthetic random-language corpus only.

**Architecture (verified from arxiv:2503.02057v1 HTML):**
- Layer 2 learns bigrams (`v_tilde^(2)`) from character pairs via Hebbian rule
- Layer 3+ compresses (n-1)-gram into compound tokens; learns n-gram from `(bigram, char)` or `((n-1)-gram, char)` pairs
- Projection mechanism: maps d^2 possible bigrams → d_2 learned bigrams via threshold epsilon_n
- **Smoothness constraint:** "all learned n-grams must be composed only of learned (n-1)-grams" (rank-bounded growth)
- Prediction rule: `partial_H / partial_v_k(N) = sum_n g^(n)_{mu_{n-1}, k} * v_tilde^(n-1)_{mu_{n-1}}` (Eq. 13)
- Sampling/measurement: `rho_k = v_k(N) / sum_j v_j(N)` (Eq. 14) — softmax-like normalization

**Critical finding for calibration penalty:** **Paper reports NO BPC, NO perplexity, NO unigram/bigram baseline comparison**. They report d_n (vocabulary size at each layer) peaks at n ∈ [3, 4] and collapses — a "memory bottleneck" prevents indefinite n-gram tokenization. They demonstrate the model "learns natural language morphology without data" but never benchmark against unigram-vs-bigram-vs-trigram BPC on a standard corpus.

**Implication for substrate:** The hierarchical-bigram + renormalization-group + smoothness-constraint mechanism IS structurally what Path A needs (escape rank-1 by composing n-gram-of-n-gram). But the literature precedent does NOT establish that this beats unigram BPC on a benchmark corpus. We are in genuinely-uncharted regime → **maximum calibration penalty**.

### L1.2 — Bengio 2003 NPLM (arxiv:0306030 / JMLR 3:1137)

Classical baseline. Feedforward neural net with softmax-over-vocab. Trained via backprop on cross-entropy loss. Beats interpolated Kneser-Ney by 10-20% perplexity on Brown/WSJ corpora. **NOT forward-only Hebbian** — backprop is load-bearing. The substrate cannot use this directly but the **softmax-over-vocab output structure** is the right target shape for BPC.

**Implication:** substrate needs a forward-only analog of "softmax over W^T h_context" where h_context is a hierarchical context vector. Eugenio's `rho_k` (Eq. 14) is exactly this shape; substrate's current Path A `softmax(W @ cue / T)` is also this shape but the W matrix is rank-bounded (Hebbian-outer-product).

### L1.3 — Predictive coding hierarchy (Rao-Ballard 1999; Friston 2005; Bastos 2012; Caucheteux 2022)

Cortical-microcircuit model where higher layers send predictions, lower layers send residual errors. **Hierarchical and forward+feedback, not pure forward-only.** Caucheteux-Goyal 2022 (arxiv:2111.14232) showed brain ROI activations correlate with up-to-8-token-future predictions during speech listening — biological evidence for hierarchical multi-token prediction.

**Substrate already has `hdlab/predictive_coding.py`** — verify if it's currently used in Path A. If not, this is an unexplored composition opportunity.

### L1.4 — Hippocampal CA3 sequence prediction (Tsodyks-Sejnowski 1995; Hasselmo 2002; recent Salvatori 2024)

CA3 is the canonical biological autoassociative-memory + sequence-completion structure. Recurrent autoassociative network for pattern completion; heteroassociative for sequence-binding to next pattern. Recent finding (Salk Salvatori 2024 — Cell:Neuron): **CA3 trained as self-supervised RNN to predict next input; spike-coupling between DG, CA3, CA1 confirms predictive structure**.

**Substrate already has `hdlab/sequence_memory.py` + `hdlab/iterative_attractor.py`.** The CA3 composition is: bind(prev_token, position) → recurrent-autoassoc-cleanup → heteroassociative-completion → next_token_distribution. This is structurally distinct from Path A v2's rank-1 Hebbian.

### L1.5 — Sparse Distributed Memory (Kanerva 1988; modern revival 2022+)

Hetero-associative chained-pointer prediction. Kanerva's foundational SDM demonstrated sequence-learning by chaining cues across stored pointers, each retrieved pattern serves as address for next prediction. **Critically:** SDM has been mapped to transformer attention layers (Bricken-Schick 2021). Critical distance at M=10000 / N=1000 is Hamming-209 — the noisy-recovery basin radius.

**Implication:** substrate's chain-grade KG portfolio (Path B) already implements heteroassoc-pointer-chaining at scale. The Path A + Path B HYBRID composition (USER's directive) is structurally an SDM-style chained-prediction LM, where Path A provides per-token distribution and Path B provides multi-step context. **No published precedent for SDM-as-LM beating unigram BPC on text8 either.**

### L1.6 — VSA / HRR LMs (Plate 1995; Frady-Sommer 2018; Schlag 2021)

Plate 1995 HRR: circular-convolution binding for sequence-encoding. Frady-Sommer 2018: capacity analysis of VSA storage (M ~ N for argmax cleanup at low noise). Schlag-Schmidhuber 2021 (arxiv:2102.11174): linear transformer ≡ outer-product Hebbian update. **Schlag-Schmidhuber is the key result** — they show modern transformers' attention is exactly the Hebbian rank-1 outer-product accumulation Path A uses. They train with backprop but ARGUE that the inference-time operator is rank-1 Hebbian.

**Implication:** Path A's current architecture IS the linear-transformer attention operator at inference. The gap to text8-bigram-BPC is the gap from linear-transformer to non-linear (softmax) transformer, which is the well-known ~1 bit/token degradation when restricted to linear attention. **This calibrates the substrate's gap: 1.26 bits to bigram ≈ the linear-vs-softmax transformer gap.** Not closeable without non-linear cleanup post-rank-1.

### L1.7 — Hopfield-as-LM (storing-natural-language-sentences in Hopfield — Stanev cmp-lg/9608001)

Stanev 1996 stored 50 sentences in a 100-bit Hopfield net; recall via energy minimization. Recall accuracy ~80% at low noise. **No BPC/perplexity, just recall accuracy.** Hopfield-as-LM has never been benchmarked as a standalone language model on standard corpora. The substrate's `iterative_attractor.py` is a Modern-Hopfield (Ramsauer) implementation but was rejected (att1 v1+v2 HARD_FAIL) for cleanup at high storage ratio.

**Implication:** Hopfield-as-LM is publicly unbenchmarked. If Path A + Hopfield-cleanup composition closes the bigram gap, it would be a novel result. **But:** att1 v1+v2 HARD_FAIL means substrate's Hopfield-cleanup primitive is broken at high noise/storage; cannot rely on it as the cleanup-of-Path-A-output without parallel encoder-side fix.

---

## L2: Substrate-applicable filter

### Filter criteria
- **Forward-only Hebbian** (substrate constraint; no backprop).
- **Composes with existing primitives**: `hdlab/char_trigram_encoder.py`, `hdlab/predictive_coding.py`, `hdlab/sequence_memory.py`, `hdlab/iterative_attractor.py`, `hdlab/whitening.py`, `hdlab/generation.py`.
- **Scales at V_C * N_DIM lever** vs requiring architectural change.

### Surviving candidates ranked

| # | Mechanism | Substrate primitive | Forward-only | Composes | Scaling |
|---|-----------|-------------------|--------------|----------|---------|
| 1 | Eugenio-style hierarchical-bigram + renormalization | `predictive_coding.py` + `char_trigram_encoder.py` | YES | YES | V_C lift |
| 2 | CA3-style heteroassoc + autoassoc cleanup | `sequence_memory.py` + `iterative_attractor.py` | YES | YES | N_DIM lift |
| 3 | SDM-style chained-pointer prediction | `sequence_memory.py` + Path B KG | YES | YES (cross-Path) | M-scale |
| 4 | Path A + sparse-fan-in encoder (ENC1 composition) | `whitening.py` + new sparse encoder | YES | YES | N_DIM lift |
| 5 | Predictive-coding hierarchy (Rao-Ballard forward+local) | `predictive_coding.py` | YES (local error) | YES | layer count |
| 6 | Linear-transformer attention (Schlag 2021) | already implemented as Path A v2 | YES | already done | already tested |
| - | Bengio NPLM | requires backprop | NO | NO | excluded |
| - | Hopfield-as-LM (att1 family) | `iterative_attractor.py` HARD_FAIL | YES | YES | excluded (att1 v1+v2 HF) |

**Top-2 chosen:** (1) Eugenio-style hierarchical + (2) CA3-style composition. Both are structural-additions-over-Path-A-v2 (additive, not replacement). #4 (sparse-fan-in encoder) is ALREADY in flight as the ENC1 cell — composes naturally once landed. #3 (SDM chained-pointer) is Path B's territory — deferred to HYBRID composition cycle.

---

## L3: Depth on top 2 candidates

### L3.1 — PC1: hierarchical-bigram + renormalization-group tokenizer

**Mathematical structure (substrate-native variant of Eugenio Eq. 13-14):**

```
Layer 1 (char-trigram, already shipped):
  v^(1)_i = char_trigram_encoder(char_window_i)  # existing hdlab/char_trigram_encoder.py

Layer 2 (bigram-of-token):
  W^(2)_{ij} = Hebbian outer product over (token_t, token_{t+1}) pairs:
                W^(2) = sum_t (E[token_{t+1}] outer E[token_t])   # rank-1 per pair
  prediction:  p_next_layer2 = softmax(W^(2) @ cue_token)         # current Path A v2

Layer 3 (trigram-of-bigram, NEW):
  Tokens at L3 are PAIRS of consecutive L2 atoms that BOTH passed a threshold epsilon_2
  on co-occurrence count (Eugenio's smoothness constraint).
  W^(3)_{ij} = sum_t (E[L3_token_{t+1}] outer E[L3_token_t])      # rank-1 per L3 pair
  prediction:  p_next_layer3 = softmax(W^(3) @ cue_L3_token)

Layer 4+ continues until d_n collapses (Eugenio Fig. 3 finding — peak at n in [3,4]).

Composed prediction:
  p_next = alpha_1 * p_layer1 + alpha_2 * p_layer2 + alpha_3 * p_layer3
         (Stolcke 1998 log-linear interp; alpha tuned on dev)

Verification: layer-1 alone should reproduce v2's calibrated 7.864 BPC.
              layer-2 added should approach unigram 7.738 (closing the 0.126 gap).
              layer-3 added should approach bigram ~6.6 (closing the 1.26 gap).
```

**Why this works structurally where v2 didn't:** v2 tested temperature-calibration and log-linear-with-unigram on the SAME rank-1 Hebbian W. The result lambda=0.1 means the substrate W contributed at most ~10% of the signal. **The bug is rank-1 itself** — a single outer-product per token-pair stores at most |V|^2 floats of information at rank-1, but text8 bigram statistics have entropy of |V| * H_bigram bits, which is much higher. Composing rank-1 layers across n-gram orders IS the way to escape — each layer adds rank-1 in a separate variable, total rank = sum_n d_n. Eugenio's smoothness constraint keeps d_n bounded (collapses at n ~ 4), giving a structurally-finite n-gram-product LM at forward-only Hebbian cost.

**Substrate-native discriminators (mandatory per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]):**
- **Per-layer BPC** (not just aggregate): layer-1 BPC, layer-2 BPC, layer-3 BPC (each standalone)
- **Per-layer lift over layer-1**: layer-2 lift, layer-3 lift (should be monotonically improving until d_n collapses)
- **Layer-coverage**: fraction of test tokens whose L3 context is in the L3 vocabulary (the smoothness-bottleneck Eugenio identified)

**Pre-flight smoke gate (mandatory):** at V=4000 N_DIM=4096 N_TRAIN=10000 (10x reduction): layer-2 BPC should be within 0.1 of v2's calibrated BPC 7.864 (sanity-check the rank-1-Hebbian is reproducible). If layer-2 deviates by >0.3 from v2 measured baseline, the implementation has a bug.

**Cost:** ~1hr GPU smoke; ~6hr GPU full at N_TRAIN=100k V=4000 N_DIM=4096 3 seeds.

### L3.2 — PC2: CA3-style heteroassoc + autoassoc cleanup composition

**Mathematical structure (substrate-native variant of Tsodyks-Sejnowski 1995 + Hasselmo 2002):**

```
Encoder: chunks input stream into (position, token) pairs
  pos_t = position_encoder(t)             # phase-encoded uniform-S^1
  tok_t = char_trigram_encoder(token_t)

Layer A — autoassociative cleanup (substrate's existing iterative_attractor):
  context_clean_t = iterative_attractor(bind(pos_t, tok_t))
                  # cleans up noisy bound-token to nearest stored-context attractor

Layer B — heteroassociative prediction (substrate's existing sequence_memory):
  W_hetero = sum_t (E[tok_{t+1}] outer E[context_clean_t])
  p_next = softmax(W_hetero @ context_clean_{T+1})

Layer C — autoassociative cleanup of next-token distribution:
  p_next_cleaned = renormalize(iterative_attractor_softmax(p_next, T=temp))
                  # at zero-T this is argmax (collapse to spike); at finite-T softens
                  # the prediction toward nearby-in-codebook tokens
```

**Why this works structurally where v2 didn't:** v2's softmax-over-rank-1-W has structurally-narrow distributions. Layer C's autoassociative cleanup on `p_next` SPREADS the distribution across the codebook-attractor-basin of the argmax token — i.e., the distribution gets mass on tokens that are similar-in-encoded-space to the predicted-token. **This is exactly the SOFT distribution that BPC favors** — give mass to plausible alternatives, not just argmax.

**Substrate-native discriminators:**
- **Per-stage BPC**: stage A clean-only, stage B hetero-only, stage C cleanup-distribution
- **Distribution sharpness**: KL(p_next || uniform), KL(p_next_cleaned || uniform), expected to drop after C
- **Top-5 acc**: should increase after C (cleanup adds mass to runner-ups)

**Pre-flight smoke gate:** stage B alone (no C) should match v2 BPC=11.614 raw (sanity check identical mechanism). If different, implementation bug.

**Risk:** Layer A uses substrate's `iterative_attractor.py` which is the att1 family. att1 v1+v2 HARD_FAIL means the cleanup is broken at high-noise / high-storage. **For PC2 we must verify the cleanup is operating in its working regime** — at M/N = V/N_DIM = 4000/4096 = 0.98 (which is OVER capacity for linear-Hopfield alpha_c=0.138). **This is a major risk for PC2.** Mitigation: use much larger N_DIM (16384) OR test PC2 with att1-substituted-by-argmax (no cleanup) to isolate hetero contribution.

**Cost:** ~1.5hr GPU smoke; ~8hr GPU full.

---

## L4: Cell-design implications (pre-registrable bands)

### PC1 cell `text8_substrate_pseudoLM_v3_hierarchical_bigram_v1`

**Config:**
- V=4000, N_DIM=4096, N_TRAIN=100000, N_HELD=20000
- 3 seeds: [7, 17, 23]
- Arms:
  - UNIGRAM_BASELINE (BPC=7.738 measured)
  - LAYER1_CHARTRIGRAM_ONLY (sanity)
  - LAYER2_HEBBIAN_BIGRAM (matches v2 calibrated)
  - LAYER12_LOG_LINEAR (v2 baseline; BPC=7.864)
  - LAYER123_HIERARCHICAL (NEW; PC1 candidate)
- d_2 threshold epsilon_2: sweep {2, 4, 8, 16} co-occurrence count (Eugenio finding peak at n=3-4 with d_n collapse means threshold is critical)
- alpha mixing weights: log-linear interp tuned on dev split
- device: cuda (GPU); already in flight per text8_pseudoLM_v2 infrastructure

**Pre-reg HARD_PASS thresholds:**
- LAYER123_HIERARCHICAL BPC <= 7.500 (>=0.2 bits below unigram) AND cv across 3 seeds <= 0.10
- AND LAYER123 lift over LAYER12 >= +0.30 bits (confirms layer-3 is doing meaningful work, not just re-discovering layer-2 signal)
- AND coverage (fraction of test tokens with valid L3 context) >= 0.40

**Pre-reg HARD_FAIL thresholds:**
- LAYER123_HIERARCHICAL BPC >= 7.738 (does NOT beat unigram) — substrate-as-LM mechanism rejected for hierarchical-bigram family
- OR coverage < 0.10 (smoothness constraint kills the layer; Eugenio bottleneck dominates at text8 vocab=4000)

**MIDDLE_BAND** (7.500 < BPC < 7.738): partial lift; substrate beats unigram by <0.2 bits; queue larger N_TRAIN sweep at V=4000 before declaration.

### PC2 cell `text8_substrate_pseudoLM_v3_CA3_hetero_autoassoc_v1`

**Config:**
- V=4000, N_DIM=16384 (LARGER than PC1 to give Hopfield cleanup capacity room; M/N = 4000/16384 = 0.24 — still above alpha_c=0.138 but in finite-T retrieval regime)
- 3 seeds: [7, 17, 23]
- Arms:
  - UNIGRAM_BASELINE
  - PATH_A_V2_BASELINE (calibrated; BPC=7.864)
  - PC2_HETERO_ONLY (substrate hetero with phase-positions, no autoassoc cleanup)
  - PC2_HETERO_PLUS_CLEANUP (full PC2; autoassoc cleanup of p_next at temp=0.5)
- Temp grid for layer-C cleanup: {0.2, 0.5, 1.0, 2.0}

**Pre-reg HARD_PASS thresholds:**
- PC2_HETERO_PLUS_CLEANUP BPC <= 7.500 AND cv <= 0.10
- AND PC2 lift over PC2_HETERO_ONLY >= +0.20 bits (confirms layer-C cleanup is load-bearing)

**Pre-reg HARD_FAIL thresholds:**
- PC2_HETERO_PLUS_CLEANUP BPC >= 7.738 — CA3-composition family rejected
- OR PC2_HETERO_PLUS_CLEANUP regresses vs PC2_HETERO_ONLY (cleanup HURTS the distribution; expected given att1 v1+v2 HF risk)

**Risk-tier note:** PC2 has higher prior risk than PC1 because the cleanup substrate (`iterative_attractor.py`) is in HARD_FAIL family from att1. Run PC1 first; only dispatch PC2 if PC1 HARD_PASSes (confirming substrate-as-LM is workable) OR if PC1 HARD_FAILs with clear "rank-1-composition is fundamental" signature (then PC2 tests the orthogonal cleanup-side fix).

---

## L5: Cross-substrate composition (Path A + Path B HYBRID)

### USER directive: Path A + Path B in same matrix W per HYBRID architecture

**Composition mechanism:**
- Path A populates W with `sum_t E[w_{t+1}] outer E[w_t]` (next-token Hebbian)
- Path B populates same W with `sum_(s,r,t) E[s] outer bind(E[r], E[t])` (KG triple Hebbian)
- At inference time, query = `q = bind(prev_token, position) + bind(query_relation, query_subject)` — substrate decides per-query which structure to read.

**Why this might help the BPC gap:** Path A's failure mode is rank-1-spike distribution. Path B's KG structure provides ALTERNATIVE candidate next-tokens via semantic relations. If `next_token` is co-bound to relations during ingest (e.g., synonym-of, hypernym-of), then the W matrix gets cross-terms that put mass on semantic-neighbor tokens — which is exactly what BPC favors.

**Substrate-product implication:** Path A + Path B HYBRID is structurally equivalent to a "language model conditioned on a knowledge graph" — well-established LLM-augmentation idea (RAG, retrieval-augmented generation) but here baked INTO the W matrix not bolted on at inference. If this works, it's substrate-novel.

**P_deflated for HYBRID closing the bigram gap:** 0.15 (deflated 0.30 from raw 0.45; no published precedent for in-matrix LM+KG composition at forward-only Hebbian; risk that the two contributions interfere destructively).

**Cell to test (deferred until PC1 verdict):**
- `text8_substrate_pseudoLM_v3_HYBRID_path_a_path_b_v1`
- Config: same as PC1 + Path B KG seeded with WordNet synonym/hypernym relations on text8 vocab
- Pre-reg: HARD_PASS requires HYBRID BPC <= PC1 BPC by >=0.3 bits (HYBRID adds >=0.3 bits over PC1 alone)

### Encoder-side composition: does PC1 break encoder Shannon-floor too?

**Reference META atom (cert ledger row 675):** `T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23` — substrate operates at sigma <= 1.0 for cleanup; cleanup-ceiling at sigma>=1.5 is information-theoretic floor.

**Key question:** does PC1's hierarchical-bigram add signal in the per-token noise regime that breaks the encoder Shannon-floor? Mechanism: hierarchical-bigram puts mass across multiple L3 tokens; if the encoder-input noise is at sigma=1.0, then the L3 prediction is averaged-over-noise which acts as a soft denoising step. PC1's per-layer-BPC discriminator measures exactly this — layer-1 BPC at sigma=1.0 vs layer-123 BPC at sigma=1.0.

**Hypothesis (deflated P=0.20):** PC1 layer-123 simultaneously breaks (a) the V2 bigram-BPC gap AND (b) the encoder Shannon-floor at sigma~1.0. This would be a double-unblock — V2 and V3 simultaneous progress.

**Falsifier:** if PC1 layer-123 HARD_PASSes BPC <= 7.500 in clean-input regime but degrades to >7.738 at sigma=1.0 — confirms PC1 closes V2 but not V3, and the encoder Shannon-floor is structurally independent.

---

## Cheap decisive test (pre-registered)

**Cell:** `text8_substrate_pseudoLM_v3_hierarchical_bigram_v1` (PC1)

**Why this is the cheapest decisive test:**
- Reuses entire v2 infrastructure (text8 ingest, GPU pipeline, per-seed sweep, log-linear interp)
- Adds only one new code path: L3 token construction (pairs of (bigram, char) above threshold epsilon_2)
- Eugenio's smoothness constraint guarantees d_n is bounded (no memory blowup)
- 1hr GPU smoke + 6hr GPU full = ~7hr total compute; fits in one overnight slot

**Decisive metric:** LAYER123_HIERARCHICAL BPC vs UNIGRAM_BASELINE 7.738 vs PATH_A_V2 7.864 vs (target) WORD_BIGRAM ~6.6.

**Pre-reg outcome bands:**
- HARD_PASS: BPC <= 7.500 → substrate-as-LM is alive; Path A v3 ships to hdlab/; queue HYBRID composition next
- HARD_FAIL: BPC >= 7.738 → hierarchical-bigram family rejected at text8 V=4000 N_DIM=4096; PC2 becomes next candidate
- MIDDLE_BAND: 7.500 < BPC < 7.738 → partial lift; queue larger-N_TRAIN sweep + atomize "PC1 closes 0.x bits of unigram gap"

---

## Falsifiable predictions (HARD_PASS + HARD_FAIL)

### PC1 (hierarchical-bigram + renormalization-group)
- HARD_PASS: LAYER123_HIERARCHICAL BPC <= 7.500 AND cv <= 0.10 AND coverage >= 0.40 AND layer-3 lift >= +0.30 bits over layer-12
- HARD_FAIL: LAYER123_HIERARCHICAL BPC >= 7.738 (does not beat unigram) OR coverage < 0.10 (smoothness bottleneck dominates)
- MIDDLE_BAND: 7.500 < BPC < 7.738 → partial; route to follow-up V/N_TRAIN sweep

### PC2 (CA3-style heteroassoc + autoassoc cleanup)
- HARD_PASS: PC2_HETERO_PLUS_CLEANUP BPC <= 7.500 AND cv <= 0.10 AND cleanup lift over hetero-only >= +0.20 bits
- HARD_FAIL: PC2 BPC >= 7.738 OR cleanup REGRESSES vs hetero-only (att1-family broken composition risk)
- MIDDLE_BAND: 7.500 < BPC < 7.738 → partial; suggests cleanup contributes but not enough

### HYBRID Path A + Path B
- HARD_PASS: HYBRID BPC <= PC1_BPC - 0.30 (substantive lift over PC1 alone) AND cv <= 0.10
- HARD_FAIL: HYBRID BPC >= PC1_BPC (no benefit from KG augmentation)
- DEFERRED until PC1 verdict

### Encoder Shannon-floor secondary test
- HARD_PASS: PC1 layer-123 BPC at sigma=1.0 <= 7.738 (V3 broken simultaneously with V2)
- HARD_FAIL: PC1 layer-123 BPC at sigma=1.0 >= 8.0 (substantial degradation; encoder floor independent)
- TERTIARY: only run if PC1 primary HARD_PASSes

---

## Cross-thread synthesis

### With prior text8_pseudoLM_v2 (this drill's parent)
- v2 finding: log-linear interp at lambda=0.1 gives BPC=7.864 vs unigram 7.738 — substrate at most 10% of signal. **Indicates rank-1 Hebbian is structurally weak; composition is needed.** PC1 directly addresses this by adding rank-1 layers across n-gram orders.
- v2's `best_T=0.5` for temperature-calibration is informative: substrate's natural softmax is too SHARP at T=1.0 — temperature flattening helps. PC1's per-layer composition naturally adds mass to runner-ups without needing aggressive temperature flattening.

### With prior att1 v1+v2 HARD_FAIL
- att1 family failure means PC2's cleanup-side fix is risky. PC1 is the safer first dispatch because it doesn't rely on `iterative_attractor.py`.
- If PC1 HARD_PASSes and PC2 HARD_FAILs, that's an informative double-result: composition works; cleanup-side does not. Atomize as "substrate-as-LM closes via compositional rank-stacking, not via cleanup-of-output-distribution".

### With ENC1 cell (in flight per encoder_side_cleanup_ceiling_break drill)
- ENC1 tests sparse-fan-in encoder. If ENC1 HARD_PASSes, PC1 should be re-tested with sparse-fan-in codebook (replaces dense bipolar with K=5 sparse rows). Expected lift: ~0.2 bits additional BPC reduction (encoder dimension + structural lift compose with hierarchical-bigram).
- Composition order: PC1 first (validates LM mechanism); ENC1 second (validates encoder lift); PC1 + ENC1 third (combined).

### With META atom cleanup-ceiling-shannon-floor (cert ledger row 675)
- META atom says substrate operates at sigma <= 1.0; cleanup-ceiling at sigma >= 1.5 is Shannon floor.
- PC1 tested at clean-input regime initially; sigma=1.0 secondary test (per L5 above) discriminates whether PC1 also breaks the encoder Shannon-floor.

### With CERT 588 / 177284 atoms / U1+n8+HotpotQA chain-grade KG portfolio
- Path B (KG) is chain-grade at 1M facts (per `exp_substrate_as_llm_scaling_million_facts_v1_resume`).
- HYBRID Path A + Path B composes Path A (next-token LM) with Path B (KG fact recall) — load-bearing test for the "glass-box LM inside substrate" L2 vision.
- If PC1 HARD_PASSes, HYBRID becomes top priority next-cycle.

### With Schlag-Schmidhuber 2021 (linear-transformer ≡ Hebbian)
- Reframes Path A v2's gap to bigram-BPC as "linear-vs-softmax transformer gap" — ~1 bit/token in published work.
- This calibrates HARD_PASS thresholds: closing 0.5 bits of the 1.26 bit gap (HARD_PASS BPC=7.5) is reasonable; closing the full 1.26 bits (BPC ~6.6) is heroic.

### With Eugenio 2025 arxiv:2503.02057 (the published precedent)
- Eugenio's NO-BPC-no-baseline finding means the substrate is operating in genuinely-uncharted regime. Calibration penalty maximum applies.
- Eugenio's smoothness constraint (only n-grams composed of existing (n-1)-grams) is directly portable to PC1; sets the threshold epsilon_2 mechanism.
- Eugenio's d_n peak at n in [3, 4] predicts PC1's layer-4+ will not add meaningful signal at text8 V=4000. PC1 should test layers 1-2-3 not 1-2-3-4-5 (avoid wasted compute on bottlenecked layers).

---

## Substrate-product implications

### If PC1 HARD_PASSes (P_deflated=0.30)
- Substrate beats unigram BPC at V=4000 N_DIM=4096 forward-only Hebbian → first substrate-native LM that meets minimum "LLM" bar
- New `hdlab/` primitive: `hierarchical_ngram_substrate_lm(V, N_DIM, max_n=3, epsilon=4)` ships substrate-flat
- META atom: `substrate_as_LM_unigram_gap_closes_via_hierarchical_rank_stacking`
- Cert atom (CERT chain-grade if 3 seeds + held-out passes): adds to U1+n8+HotpotQA portfolio as fourth chain-grade capability
- Path A v3 unblocks bigram-gap closure attempt at GPU full scale (~6hr); next milestone = BPC <=7.0 = within 0.4 bits of word-bigram

### If PC1 HARD_PASSes AND HYBRID HARD_PASSes
- Substrate gets in-matrix LM + KG composition; product-grade for auditable-AI-memory subsystem positioning
- Composes with continual-learning CLS-replay (each replayed atom contributes to W's per-layer rank-stack)
- Atomize as: `substrate_as_LM_and_KG_in_same_W_matrix_HYBRID_chain_grade`

### If PC1 HARD_FAILs and PC2 HARD_FAILs
- Substrate-as-LM at forward-only Hebbian + composition + cleanup all rejected at V=4000 N_DIM=4096
- Atomize as: `substrate_as_LM_unigram_gap_cannot_close_at_V4000_N4096_forward_only_hebbian`
- Pivot to: (a) larger V/N_DIM scaling sweep (Path A v3 at V=16000 N_DIM=16384); (b) encoder-input quality (pythia/BGE preprocessing); (c) accept substrate-as-KG-only (Path B chain-grade) as substrate-product positioning, deprecate Path A

### If PC1 HARD_PASSes but at MIDDLE_BAND
- Substrate substantively contributes to LM but not chain-grade
- Atomize as TIERED non-load-bearing (T2 measured-mechanism per [[feedback-research-can-be-wrong-only-proven-fully-believed]])
- Continue refining: PC1 + ENC1 encoder composition; PC1 + Path B HYBRID; PC1 at larger V/N_DIM

---

## Calibration-penalty discipline applied

Per [[feedback-lit-scan-calibration-penalty]]:
- **PC1 P_deflated=0.30 (raw 0.50 deflated 0.20):** Eugenio 2025 is closest precedent but published NO BPC + NO unigram/bigram baseline + only Alice in Wonderland; we are in uncharted regime for "forward-only Hebbian beats unigram on text8". The mechanism is principled (hierarchical rank-stacking IS the right answer to rank-1 Hebbian's limit) but no precedent guarantees it works on text8.
- **PC2 P_deflated=0.25 (raw 0.45 deflated 0.20):** CA3-style hetero+autoassoc is well-precedented in biological literature; substrate has the primitives; BUT the cleanup substrate (`iterative_attractor.py`) is in HARD_FAIL family (att1 v1+v2). Risk is that the cleanup-of-output-distribution does not work where the cleanup-of-noisy-cue did not.
- **HYBRID P_deflated=0.15 (raw 0.45 deflated 0.30):** zero published precedent for in-matrix LM+KG forward-only Hebbian composition; novel-synthesis; cap 0.50 with extra deflation for risk that the two contributions interfere destructively.
- **All HARD_FAIL thresholds explicitly named** (BPC >= 7.738 absolute, not relative)
- **Novel-synthesis cap 0.50 enforced**

---

## Citations (verified count: 15)

1. Eugenio, P.M. "Hebbian learning the local structure of language." arXiv:2503.02057 (March 2025). **VERIFIED via WebFetch — no BPC reported; Alice in Wonderland + synthetic random language only; renormalization-group tokenizer hierarchy structure.**
2. Bengio et al. "A Neural Probabilistic Language Model." JMLR 3:1137-1155 (2003).
3. Rao & Ballard. "Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects." Nature Neuroscience 2(1):79-87 (1999).
4. Friston, K. "A theory of cortical responses." Phil. Trans. R. Soc. B 360:815-836 (2005).
5. Bastos et al. "Canonical microcircuits for predictive coding." Neuron 76(4):695-711 (2012).
6. Caucheteux, Goyal. "Long-range and hierarchical language predictions in brains and algorithms." arXiv:2111.14232 (2021).
7. Salvatori et al. "Predictive sequence learning in the hippocampal formation." Cell:Neuron (2024). Salk Institute PDF papers.cnl.salk.edu.
8. Tsodyks, M. "Associative memory in a network with 'topographically' organized connections." Network 6:177-194 (1995).
9. Kanerva, P. "Sparse Distributed Memory." MIT Press (1988).
10. Plate, T. "Holographic reduced representations: Convolution algebra for compositional distributed representations." IJCAI 1995.
11. Frady, F., Sommer, F. "Robust computation with rhythmic spike patterns." PNAS 2019.
12. Schlag, Schmidhuber. "Linear Transformers Are Secretly Fast Weight Programmers." arXiv:2102.11174 (2021). **VERIFIED — establishes linear-transformer ≡ Hebbian outer-product equivalence.**
13. Stanev. "Storage of Natural Language Sentences in a Hopfield Network." arXiv:cmp-lg/9608001 (1996).
14. Ramsauer et al. "Hopfield Networks Is All You Need." ICLR 2021. arXiv:2008.02217.
15. Stolcke, A. "Entropy-based pruning of backoff language models." SRILM (1998). Log-linear interp standard.

**Substrate-internal cross-references:**
- `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json` (parent measured baseline)
- `data/exp_text8_substrate_pseudoLM_gpu_v1_smoke_remote/metrics.json` (v1 HARD_FAIL)
- `data/exp_substrate_as_llm_scaling_million_facts_v1_resume/metrics.json` (Path B chain-grade at 1M)
- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (parent v2 revival drill)
- `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` (att1 rejection context)
- `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` (encoder-side fix in flight)
- `hdlab/predictive_coding.py` (PC1 primitive base)
- `hdlab/sequence_memory.py` (PC2 hetero base)
- `hdlab/iterative_attractor.py` (PC2 autoassoc base; in HARD_FAIL family)
- `hdlab/char_trigram_encoder.py` (PC1 layer-1 base)
- `hdlab/whitening.py` (composition with ENC1)
- `hdlab/generation.py` (downstream LM sampling)
- CERT ledger row 675: `T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23`

**Verified count: 15 external + 13 substrate-internal cross-references.**

---

## Operational drill summary

- **DISPATCH FIRST:** PC1 `text8_substrate_pseudoLM_v3_hierarchical_bigram_v1` — ~1hr GPU smoke + 6hr GPU full. Reuses v2 infrastructure; adds hierarchical L3 token construction; tests HARD_PASS BPC <= 7.500 vs HARD_FAIL BPC >= 7.738. **P_deflated=0.30.**
- **DISPATCH SECOND (conditional on PC1 verdict):** PC2 `text8_substrate_pseudoLM_v3_CA3_hetero_autoassoc_v1` — ~1.5hr GPU smoke + 8hr GPU full. Tests CA3-style cleanup composition. Run only if PC1 HARD_FAILs (orthogonal mechanism) OR PC1 HARD_PASSes (then PC2 tests additive lift). **P_deflated=0.25.**
- **DISPATCH THIRD (deferred to PC1 HARD_PASS):** HYBRID Path A + Path B in-matrix composition. **P_deflated=0.15.**
- **Composition with ENC1 (in flight):** if ENC1 HARD_PASSes sparse-fan-in encoder, rerun PC1 with sparse encoder. Expected additional lift: ~0.2 bits.
- **Tertiary encoder-floor test:** if PC1 HARD_PASSes, run PC1 at sigma=1.0 input to test if V2+V3 simultaneously break.

**Cross-thread synthesis with substrate state:** PC1 is the single highest-leverage next-cycle dispatch because (a) it directly addresses the v2 calibrated-MIDDLE_BAND finding; (b) it composes with multiple existing substrate primitives without code rewrites; (c) it has the lowest implementation risk among 5 surviving L2 candidates; (d) it tests a structurally-different mechanism class (rank-stacking vs rank-1-with-calibration). If PC1 HARD_PASSes, substrate-as-LM is alive and the L2 vision (glass-box LM inside substrate) gains its first chain-grade win.

**Honest caveat:** all P estimates are bounded by novel-synthesis cap 0.50 and deflated for absence of direct published precedent. The substrate may be at a fundamental Shannon floor for forward-only-Hebbian-without-backprop LMs on text8. The HARD_FAIL bands are explicit and named precisely so that a clean negative result is informative (not just "didn't work").
