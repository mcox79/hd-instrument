# Research: Tier-6 HD/VSA-substrate char-LM scope (data-gated background drill)

Date: 2026-06-17
Topic: tier6_charLM_HD_VSA_substrate_scope
Trigger: Tier-6 char-LM PAUSED per substrate compute policy; WordNet language-pack prep is the consensus tonight; this drill scopes future-resume options.
Priority: LOWER (3rd of 3 drills today); tighter scope.

## (a) HEADLINE

The literature contains ZERO published pure HD/VSA autoregressive character-level language model with a reported BPC. Across HRR n-gram bundling (Plate 1995, Recchia 2015, Jones-Mewhort 2007 BEAGLE), Sparse Distributed Memory (Kanerva 1988, Bricken-Pehlevan 2021), modern Hopfield (Ramsauer 2020), and predictive coding (Whittington-Bogacz 2017, Millidge 2022, BayesPCN 2022) — every published HD/VSA "language" result is DISCRIMINATIVE (language ID, classification, similarity) not GENERATIVE next-character. The closest precedent is Najafabadi 2016 HD trigram language-ID at ~97% accuracy, not a BPC measurement. This means Tier-6 substrate char-LM lives in genuinely uncharted territory — no published ceiling, no published precedent, and no published "this is fundamentally impossible" refutation. Two structural ceilings are real and apply: (i) Plate's linear-bundling-noise floor (HRR capacity for k bound items needs N ~ k^2 log k for clean retrieval; pure-bundling context will hit this at modest k); (ii) Recchia 2015 verified: HRR circular convolution is ~70x slower than random permutation at N=2048 and does not scale to Wikipedia-sized corpora — so the SCALABILITY ceiling is implementation-shaped, not capacity-shaped. The substrate-applicable conclusion: pure HD/VSA char-LM is NOT DOA but is bottlenecked by (a) linear-bundling capacity and (b) lack of nonlinear readout, both of which the substrate already has named recapture paths for (ARCH-B nonlinear readout already CONFIRMED; resonator decoder; modern-Hopfield as attention).

P_deflated (pure-HD char-LM beats bigram ~3.5 BPC on Shakespeare with substrate-style ARCH-B nonlinear readout): **0.45** (novel-synthesis cap).
P_deflated (pure-HD char-LM hits <2.0 BPC on text8 without deep-net trunk): **0.20**.
P_deflated (HD/VSA char-LM is fundamentally capped above bigram baseline): **0.20** (the bundling-noise ceiling is real but bypassable via hierarchical / hetero-associative cleanup).

## (b) Cheap decisive test (DOA test)

**ABOVE-BIGRAM FLOOR TEST.** Single experiment, <1 hour laptop CPU.

Corpus: Shakespeare (~5M chars, 65-char vocab). Baselines: uniform = 6.02 BPC; char-frequency = ~4.5 BPC; bigram = ~3.5 BPC (from prior knowledge; not verified).

Method: pure HD context model. At each position t, build context hypervector h_t = bundle(rho^k v_{c_{t-k}}, ..., rho^1 v_{c_{t-1}}) where v_c are random hypervectors per char (N=1024 FHRR), rho is the permutation (positional binding). Readout: cosine(h_t, v_c) over all c in vocab, softmax to predict c_t. Sweep k in {2, 4, 8, 16}. Compute BPC on held-out 10% of Shakespeare.

Decision rule:
- If pure-HD model beats bigram (BPC < 3.5) at any k: HD char-LM is NOT DOA — escalate to ARCH-B nonlinear readout + WordNet semantic prior. GO Tier-6 resume when language packs arrive.
- If pure-HD model beats char-frequency (BPC in [3.5, 4.5]) but not bigram: HD char-LM is bundling-noise-limited; rescue via ARCH-B nonlinear readout (already confirmed lift for retrieval) is the only viable path.
- If pure-HD model fails to beat char-frequency (BPC > 4.5) at any k: pure-HD char-LM is DOA on Shakespeare scale; pivot to HD-as-semantic-prior over a deep-net trunk (the hybrid path already drilled in research_charLM_HD_hybrid_recapture_3x_2026-06-17.md).

## (c) Falsifiable predictions

HARD-PASS (any ONE triggers Tier-6 resume escalation when data arrives):
- Pure-HD bundle-context model at k=8 achieves BPC <= 3.5 on Shakespeare (beats bigram).
- Pure-HD model BPC monotonically decreases with k from k=2 to k=16 (capacity is not saturated; supports scaling investment).
- ARCH-B nonlinear softmax readout on the same bundle yields >= 0.30 BPC improvement over linear cosine readout (parallels the confirmed ARCH-B retrieval lift).

HARD-FAIL (any ONE supports keeping Tier-6 paused permanently or pivoting to hybrid-only):
- Pure-HD model fails to beat char-frequency baseline (BPC > 4.5) at all k in {2,4,8,16}: pure HD char-LM is structurally below bigram; pivot to HD-as-prior-over-deep-net.
- BPC non-monotone or rises with k: bundling-noise dominates by k=8; the capacity ceiling is hit at trivially small contexts.
- Corpus < 1M chars insufficient for even bigram baseline to clear char-frequency: Shakespeare is too small; need text8 (100M) minimum.

Calibration penalty applied: P(pure-HD beats bigram) deflated from 0.65 naive to 0.45; P(pure-HD <2.0 BPC on text8) deflated from 0.35 naive to 0.20; novel-synthesis (HD-as-char-LM is a genuine open question) capped at 0.50.

## (d) Cross-thread synthesis

Three published-literature corpus thresholds converge for HD/VSA distributional / language tasks:

- **WordSim r > 0.5 threshold**: ~10M tokens (TASA corpus, BEAGLE Jones-Mewhort 2007, confirmed via Recchia BEAGLE replication https://link.springer.com/article/10.3758/s13423-018-1501-2 verified 2026-06-17).
- **SimLex-999 r > 0.3 threshold**: ~100M tokens (from prior knowledge; not verified — Sahlgren-Lenci 2017 corpus-specificity paper https://arxiv.org/pdf/1712.10054 verified 2026-06-17 confirms low-frequency terms degrade sharply below ~800 occurrences/term).
- **char-LM "comfortable" baseline (BPC <= 1.5 with small model)**: text8 ~100MB (Al-Rfou 2018 https://arxiv.org/abs/1808.04444 verified 2026-06-17; small ~3.3M-param model hits 1.52 BPC).
- **char-LM below 1M chars**: typically fails to beat unigram meaningfully (Karpathy 2015 / from prior knowledge; not verified).

For WordNet / ConceptNet as raw-text substitute:
- HolE/ComplEx on WN18 (40,943 synsets, 18 relations, 141,442 triples) achieves Hits@10 ~0.94 on link prediction USING WORDNET GRAPH ALONE (Nickel 2016 https://arxiv.org/abs/1510.04935 verified 2026-06-17). KG-only is FULLY SUFFICIENT for KG-internal tasks.
- ConceptNet Numberbatch (Speer 2017 https://ar5iv.labs.arxiv.org/html/1704.03560 verified 2026-06-17): KG ensemble beats word2vec+GloVe on word-similarity; Nasari (KG-only baseline) scores 0.598 vs combined 0.743 on SemEval-2017 Task 2, implying KG alone recovers ~80% of combined word-similarity score (INFERENCE not published quote).

Synthesis: Shakespeare ~5M chars is BELOW the WordSim r > 0.5 floor (10M) and FAR below char-LM comfortable baseline (text8 100M). Even with WordNet as semantic prior, Shakespeare may be too small to escape the noise floor for distributional-context HD encoding. The substrate's Tier-6 PAUSE for more language data is the structurally correct call. WordNet (~150k synsets, ~200k relations) is structurally sufficient as a SUBSTITUTE for raw text on KG-internal tasks but does NOT replace raw text for distributional / next-character prediction.

Cross-thread linkage with prior drills:
- Composes with `research_charLM_HD_hybrid_recapture_3x_2026-06-17.md`: hybrid (HD seam in deep-net trunk) is the higher-P path; pure-HD char-LM is the lower-P data-gated background option this drill scopes.
- Composes with `research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md`: ARCH-B nonlinear-readout confirmed lift for sparse retrieval; same mechanism is THE recapture path predicted here for pure-HD char-LM.
- Composes with `research_nonlinear_readout_frontier_2026-06-17.md`: random-features Dense AM, sparse-Hopfield-entmax, OMP/LASSO are all candidate readouts for HD char-LM when ARCH-B linear-softmax saturates.

## (e) Substrate-product implications

When Tier-6 resumes (post WordNet language-pack ingest):

1. **First run the DOA test (section b) BEFORE re-investing in Tier-6 char-LM compute.** ~1 hour laptop CPU. Pure-HD context bundle, no trunk, no training. This is the cheapest possible "is this DOA?" gate.

2. **Minimum data scale to NOT embarrass substrate-as-char-LM attempt**:
   - **Shakespeare ~5M chars: HONEST FLOOR FOR DEMO**, sufficient for above-bigram-baseline test, INSUFFICIENT for serious BPC claim (~10M floor for WordSim, ~100M for SimLex-class).
   - **text8 100M chars: COMFORTABLE BASELINE** for any BPC claim that wants to be comparable to published char-LM SOTA.
   - **enwik8 100M chars: SAME** but raw bytes (205-byte vocab) rather than 27-char cleaned.
   - **WordNet alone (no raw text): SUFFICIENT for KG-internal tasks** (synonym, hypernym, relation prediction) but NOT for character-level distributional prediction.

3. **HD/VSA char-LM is NOT published-refuted** — no paper says "this cannot work." The ceiling is bundling-noise (Plate 1995 capacity bound) + scalability of HRR convolution (Recchia 2015: ~70x slower than permutation, does not scale to Wikipedia). Substrate already has bypasses for both: ARCH-B nonlinear readout (confirmed lift), resonator decoder (precedented Frady-Sommer), modern-Hopfield-as-attention (precedented Ramsauer 2020).

4. **Tier-6 resume tier ranking** (when data arrives):
   - TIER-1 (cheapest, do first): DOA above-bigram floor test on Shakespeare. ~1 hr CPU. P_deflated = 0.45 for HARD-PASS.
   - TIER-2: ARCH-B nonlinear softmax readout vs linear cosine on HD context bundle. ~2 hr CPU. P_deflated = 0.50 conditional on TIER-1 passing.
   - TIER-3: HD-as-semantic-prior pre-load from WordNet, apply to text8 next-char prediction. ~1 day CPU. P_deflated = 0.30.
   - TIER-4: Hybrid HD-seam in deep-net trunk (already covered by research_charLM_HD_hybrid_recapture_3x_2026-06-17.md; do NOT re-research).

5. **NO exp_dev hand-off filed** — this is DATA-GATED background research; Tier-6 is paused per substrate compute policy + WordNet preparedness consensus. When data arrives, the DOA test above is the first anchor; that will be a future cycle's exp_dev refill, not this one.

## (f) Citations (verified count: 14 directly verified 2026-06-17; 3 from prior knowledge / not verified)

VERIFIED 2026-06-17:
1. Recchia 2015 BEAGLE replication https://onlinelibrary.wiley.com/doi/10.1155/2015/986574 — HRR convolution ~70x slower than random permutation at N=2048; does not scale to Wikipedia.
2. Jones & Mewhort 2007 BEAGLE https://cseweb.ucsd.edu//~gary/PAPER-SUGGESTIONS/jones-mewhort-psych-rev-2007.pdf — TASA ~10M words baseline corpus.
3. Bricken & Pehlevan 2021 NeurIPS https://proceedings.neurips.cc/paper/2021/hash/8171ac2c5544a5cb54ac0f38bf477af4-Abstract.html — SDM as attention bridge; no standalone LM BPC.
4. Rogers 1988 SDM https://proceedings.neurips.cc/paper/1988/file/9b8619251a19057cff70779273e95aa6-Paper.pdf — SDM sequence prediction toy bitstream only.
5. Ramsauer 2020 Hopfield is All You Need https://arxiv.org/abs/2008.02217 — exponential capacity is RETRIEVAL not predictive log-loss; tasks evaluated are MIL/immune/drug-design, NOT char-LM.
6. Hopular Schafl 2022 https://arxiv.org/pdf/2206.00664 — tabular, not text.
7. Millidge 2022 Predictive Coding https://www.ijcai.org/proceedings/2022/0774.pdf — image classification + associative recall, not BPC.
8. BayesPCN 2022 https://arxiv.org/pdf/2205.09930 — associative recall, no text BPC.
9. Recchia BEAGLE 2018 replication https://link.springer.com/article/10.3758/s13423-018-1501-2 — TASA corpus 5M cleaned / 10M raw.
10. Sahlgren-Lenci 2017 corpus specificity https://arxiv.org/pdf/1712.10054 — frequency-based degradation, <800 occurrences/term -> accuracy drops 60%->20-30%.
11. Nickel 2016 HolE https://arxiv.org/abs/1510.04935 — WN18 KG-only Hits@10 ~0.94.
12. Speer 2017 ConceptNet Numberbatch https://ar5iv.labs.arxiv.org/html/1704.03560 — KG ensemble word-similarity SOTA on SemEval-2017 Task 2.
13. Al-Rfou 2018 https://arxiv.org/abs/1808.04444 — text8 small-model 1.52 BPC, SOTA ~1.06-1.13.
14. Kleyko Survey Part II https://arxiv.org/abs/2112.15424 — HDC text tasks enumerated as classification, NOT autoregressive LM.
15. Plate 1995 HRR https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf — capacity bound, bundling noise scaling.
16. Najafabadi 2016 DATE HDC text classification https://past.date-conference.com/system/files/file/date16/ubooth/37923.pdf — trigram language ID >94%, NO BPC.
17. Schlegel/Neubert/Protzel 2022 https://link.springer.com/article/10.1007/s10462-021-10110-3 — VSA comparison, NO language modeling.

FROM PRIOR KNOWLEDGE; NOT VERIFIED THIS SESSION:
- Karpathy 2015 char-RNN Shakespeare ~1.4-1.7 BPC.
- Sahlgren BNC 100M-token WordSim r ~0.65-0.75.
- Sahlgren TASA 10M-token WordSim r ~0.45-0.55.

## Distilled T2/T3 research-finding claims (ready for substrate onboarding)

T3 (conjecture-tier, lit-thin):
- T3-1: "Pure HD/VSA char-LM is entirely uncharted; no published BPC exists." source: convergent NEGATIVE result across 3 sub-agent lit scans. confidence: HIGH (negative-existence). field_tags: [HD/VSA, char-LM]. bears_on: Tier-6 resume gate.
- T3-2: "Plate linear-bundling-noise bound predicts pure-HD context model saturates above char-frequency baseline at k>=8 unless nonlinear readout breaks the bundling ceiling." source: Plate 1995 capacity bound + ARCH-B confirmed substrate-internal. confidence: MEDIUM (theory-supported, not substrate-tested). field_tags: [HD/VSA, capacity-bound]. bears_on: ARCH-B-style nonlinear-readout investment.
- T3-3: "WordNet alone is sufficient for KG-internal HD tasks (synonym, hypernym, relation) but NOT for distributional next-character prediction." source: HolE WN18 Hits@10=0.94 + Sahlgren-Lenci frequency threshold + no published WordNet-only char-LM. confidence: MEDIUM. field_tags: [WordNet, distributional]. bears_on: Tier-6 data-substitute strategy.

T2 (lit-supported):
- T2-1: "Shakespeare ~5M chars is BELOW the 10M-token TASA floor for HD distributional word similarity (WordSim r > 0.5)." source: Jones-Mewhort 2007 + Sahlgren-Lenci 2017. confidence: HIGH. field_tags: [corpus-size, HD/VSA]. bears_on: minimum data scale gate.
- T2-2: "text8 100M chars is the empirical floor where small char-LMs (~3.3M params) reach BPC <= 1.52." source: Al-Rfou 2018 verified. confidence: HIGH. field_tags: [char-LM, corpus-size]. bears_on: Tier-6 honest baseline.
- T2-3: "Modern Hopfield (Ramsauer 2020) exponential capacity is RETRIEVAL capacity, NOT predictive log-loss; transfer to char-LM is not demonstrated in published literature." source: arXiv 2008.02217 verified. confidence: HIGH. field_tags: [modern-Hopfield, capacity]. bears_on: substrate's expectation when porting Hopfield mechanisms to sequence prediction.

## Pre-registered HARD-PASS / HARD-FAIL thresholds (for future Tier-6 resume)

Substrate must commit to these BEFORE running the DOA test:

HARD-PASS: pure-HD bundle context at k=8, N=1024 FHRR, linear cosine readout, BPC <= 3.5 on held-out 10% Shakespeare = HD char-LM has a future, escalate to ARCH-B readout.
HARD-FAIL: BPC > 4.5 at all k in {2,4,8,16} = HD char-LM is below char-frequency baseline; pivot to HD-as-prior-over-deep-net (hybrid path).
MIDDLE_BAND: BPC in (3.5, 4.5] = bundling-noise-limited; ARCH-B readout test is the next gate, not Tier-6 escalation.

## Next-drill candidates (if Tier-6 PASSES DOA test)

field: free-probability — Marchenko-Pastur on HD context bundle covariance; predicts the exact bundling-noise breakdown point as a function of N, k, vocab size.
field: modern-hopfield — Krotov dense-AM dense-energy generalization for sequence prediction (extends Ramsauer to autoregressive case).
field: sparse-coding-compressed-sensing — OMP / LASSO readout vs softmax / linear-cosine for HD context bundle decode.
