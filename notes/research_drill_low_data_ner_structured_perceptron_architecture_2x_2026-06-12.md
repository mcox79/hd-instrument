# Research drill: low-data NER structured perceptron architecture (2x DEEP)

Date: 2026-06-12
Drill type: 2x deep literature drill, two independent rounds (5+ queries each)
Trigger: substrate-classical NER 5pct CoNLL-2003 missed pre-reg HARD-PASS ~0.55; achieved ~63pct of full-data F1 (moderate low-data signal). Need (a) architectural levers to lift 5pct F1 toward 0.55+, (b) LLM-0.5B-FT prior at 5pct CoNLL-2003 for the upcoming GPU follow-on baseline.

## HEADLINE

Literature predicts LLM-0.5B fine-tune at 5pct CoNLL-2003 (~600 sentences) lands in F1 ~0.65-0.78 with calibration headroom; structured-perceptron Tier-A architecture can plausibly close most of the gap to 0.55+ HARD-PASS via gazetteer-prior features + simple mention-replacement augmentation + self-training pseudo-labeling on the unused 95pct. Span-decomposition is NOT recommended at this stage (architectural rewrite, marginal at structured-perceptron scale). Net: 5pct HARD-PASS is reachable with additive feature/data interventions before any encoder swap.

## Round 1 findings (compact)

R1-a (low-resource benchmarks). ELLEN-style neuro-symbolic methods reach F1 ~0.85 at "5pct" CoNLL-2003 using rules+LM. ACE drops below 0.70 at the same fraction. Few-shot K=20-50 EntLM/Struct sits in 0.51-0.75 band, K=50 -> 0.748. Meta-embedding methods (FAME) add ~6.7 F1 at the 5pct (~600 sentences) point vs vanilla attention meta-emb. Takeaway: 0.55 is BELOW best-known 5pct; lift toolkit is rich.

R1-b (char-BiLSTM-CRF). End-to-end BiLSTM-CNN-CRF reaches F1 ~91 on full CoNLL-2003. Char-CNN representations are the dominant single architectural lever for OOV/rare-entity coverage. Low-data drop is roughly proportional to data (slightly sub-linear) -- char-features especially valuable at 5pct because lexical features alone collapse on unseen entities.

R1-c (structured-perceptron feature engineering). Averaged updates are standard. Templates: surrounding word context, POS-tags, orthography (capitalization, digits, prefix/suffix), word-shape. Rich overlapping features are the primary advantage over HMM. Substrate's current feature set (word + char-shape + prefix/suffix + cap) is a competent baseline but missing POS-cascade and gazetteer-feature -- two literature-validated additive lifts.

R1-d (small-LM fine-tune). EntLM + Struct hits F1 0.748 at K=50; FFF-NER (formulating fine-tune as pre-training objective) is the SOTA framing for sub-1B fine-tune. No literature point cleanly published for "0.5B at 5pct" -- best proxy is K=50 few-shot (0.748) and ELLEN (0.85 with rules); plain fine-tune of 0.5B-class at ~600 sentences likely 0.65-0.78 with calibration.

## Round 2 findings (compact)

R2-a (data augmentation). Mention-replacement (MR), label-wise token replacement (LwTR), shuffle-within-segments (SiS) are the canonical sequence-labeling augmentations. At 150 sentences, label-conditioned word replacement adds >40pct F1 over no-augmentation baselines. ENTDA shows +~2.97 F1 average lift across backbones in low-resource regimes. Back-translation is reported as low-resource augmentation but lift at CoNLL-EN specifically is smaller (~1-3 F1) because back-translation noise corrupts entity spans.

R2-b (gazetteers). Adding gazetteer features lifts vanilla RNN on CoNLL-2003 to F1 ~91.73. Reported lifts in the literature span +0.5 (large-data, ceilinged) to several F1 points in lower-data regimes. GEMNET-style gated gazetteer integration prevents overuse. For structured perceptron, gazetteer is a one-shot lookup indicator feature -- trivial to add, no architectural change.

R2-c (span-based vs BIO). Span-based outperforms BIO sequence-labeling in few-shot settings by ~0.2-6.6 F1; in 5/20/50-shot biomedical NER, span-based adds +10.2/14.4/15.2 F1 over prior SoTA. However span-based architectures are typically encoder-based; the gain over BIO sequence-tagging in a structured-perceptron stack is unverified by literature and would require an architectural rewrite. RECOMMENDATION: not at this stage.

R2-d (self-training/pseudo-labeling). Self-training with the unlabeled 95pct can match labeled-data baselines using 3x-8x less labeled data. On CoNLL-2003 finetuning with 10pct entities labeled reaches baseline performance of 50pct labeled. ContProto, prototype-based pseudo-labeling, and contrastive self-training reduce pseudo-label noise. For structured perceptron: confidence-thresholded Viterbi self-labeling on the 95pct unused sentences is cheap and additive.

R2-e (distant supervision). Gazetteer-based distant labeling on unlabeled corpus + noise-robust learning (e.g. expected-entity-ratio loss, partial-supervision) is the dominant low-data lever where labeled data is scarce. Pairs well with gazetteer features (R2-b).

## Synthesis

LLM-0.5B-FT expected F1 at 5pct CoNLL-2003 (prior for GPU follow-on):
- Point estimate (literature prior): F1 ~0.70-0.75 with calibration
- Range: 0.65 (uncalibrated, naive token-classification head) to 0.78 (calibrated + appropriate format)
- ELLEN-style hybrid LM+rules: ~0.85 (but uses external rules; not a clean 0.5B-FT comparison)
- Calibration penalty per literature-is-not-oracle: deflate by 0.05-0.10 because most published 5pct numbers use BERT-base (110M) or larger; sub-1B class is under-published
- Final prior: F1 0.65-0.75 (median ~0.70) -- DEFLATED novel-synthesis P at 0.45 that substrate-classical beats this without architectural change

Architectural improvements ranked by predicted lift x cheapness (substrate-classical structured perceptron at 5pct CoNLL-2003):

1. STRONG. Gazetteer indicator features (Wikidata/DBpedia/GeoNames lists for PER/LOC/ORG). Predicted lift +0.03 to +0.07 F1 at 5pct. Uncertainty: 0.02. Cost: <1 day. Mechanism: substrate already supports indicator-feature additions; gazetteer is one-shot lookup. Substrate-product fit: aux-features-shrink-with-data rule says gazetteer marginal lift will be LARGER at 5pct than at full-data, consistent with substrate aux-features-shrink-with-data prior.

2. STRONG. Mention-replacement / label-wise token replacement augmentation on the 600 sentences (10x synthetic expansion). Predicted lift +0.04 to +0.08 F1 at 5pct. Uncertainty: 0.03. Cost: <1 day. Mechanism: lexical-coverage expansion mimicking what char-CNN does implicitly. CAUTION: known to interact with gazetteer (R2-b + R2-e) -- combined lift NOT additive; estimate combined +0.06 to +0.10.

3. MODERATE. POS-cascade feature (POS tag as substrate feature; substrate has POS at F1 0.957). Predicted lift +0.01 to +0.03 F1 at 5pct (per prior substrate aux-features-shrink-with-data: POS gave +0.078 at 300 train, +0.013 at 5982 train; 5pct is ~600 train -- interpolate ~+0.03 to +0.05). Uncertainty: 0.02. Cost: <0.5 day (POS tagger already shipped). Substrate-product fit: pre-existing primitive composition, aligns with two-stage-decomposition-beats-joint.

4. MODERATE. Self-training pseudo-labeling on the 95pct unlabeled CoNLL-train using high-confidence Viterbi marginals. Predicted lift +0.02 to +0.06 F1 at 5pct. Uncertainty: 0.04 (pseudo-label noise is the variance driver). Cost: 1 day. CAUTION: requires confidence-threshold calibration; if conformal prediction already wired in substrate, this is cheap.

5. SPECULATIVE. CRF-style transition-feature learning (substrate currently uses unstructured tag scoring? Verify; if just Viterbi over unstructured emissions, structured-perceptron already learns transition features through structured updates -- may already be in). Predicted lift +0.0 to +0.02 if missing; otherwise no-op. Cost: 0.5-1 day.

NOT RECOMMENDED:
- Span-based architectural rewrite (R2-c). Strong evidence in neural span-encoders, no direct evidence at structured-perceptron stack; rewrite cost > expected lift at this stage.
- Back-translation augmentation. R2-a notes entity-span corruption; small lift on CoNLL-EN.
- Brown clusters at scale (substrate aux-features-shrink-with-data already showed shrinkage).

Combined predicted 5pct F1 with all STRONG + MODERATE interventions:
- Baseline (current substrate): not stated but inferred ~0.55*0.63 mapping -- treating baseline as the missed HARD-PASS proxy of 0.40-0.45 range
- + Gazetteer + MR: +0.06-0.10 -> 0.46-0.55
- + POS-cascade: +0.03-0.05 -> 0.49-0.60
- + Self-training: +0.02-0.06 -> 0.51-0.66
- Combined point estimate at 5pct: F1 0.55-0.62 (HARD-PASS reachable)
- Deflated P(reaches 0.55+) = 0.45-0.55 per lit-scan calibration penalty

## Cheap decisive test

Smoke pre-reg: at 5pct CoNLL-2003 (~600 sentences):
- Run substrate-Tier-A baseline (current feature set) -> measure F1_base
- Add gazetteer features (PER/LOC/ORG lists from public Wikidata dumps) -> measure F1_gaz
- Add MR augmentation (3x synthetic expansion) -> measure F1_mr
- Combined gaz+MR+POS-cascade -> measure F1_combined
- LLM-0.5B-FT comparison at same 600 sentences with calibrated decoding

HARD-PASS: F1_combined >= 0.55 AND F1_combined > F1_LLM-0.5B-FT
HARD-FAIL: F1_combined < 0.50 OR F1_combined < F1_LLM-0.5B-FT - 0.05
MIDDLE: anything in between -> 2x research on remaining gap (char-CNN replacement of char-shape; CRF transition learning; encoder hybrid)

## Falsifiable predictions

- P(gazetteer alone adds >= 0.03 F1 at 5pct) = 0.65 (literature consensus strong)
- P(MR alone adds >= 0.04 F1 at 5pct) = 0.55 (label-conditioned variant adds more)
- P(combined STRONG+MODERATE reaches 0.55 HARD-PASS) = 0.45 (deflated novel-synthesis cap 0.50)
- P(substrate-classical >= LLM-0.5B-FT at 5pct after interventions) = 0.40 (deflated; depends on LLM-FT calibration quality)
- HARD-FAIL threshold: if gazetteer alone adds <0.01 F1 then substrate gazetteer-integration is mis-wired (NOT a literature failure)

## Cross-thread synthesis

- Generalizes substrate aux-features-shrink-with-data rule: gazetteer is the OPPOSITE -- at 5pct it should add MORE than at full-data, consistent with the inverse of the shrinkage axis. Distinguishes "implicit-features-shrink" (POS, Brown) from "explicit-knowledge-features-grow at low data" (gazetteer, distant supervision). New methodology-rule candidate: "explicit-prior-knowledge features have INVERSE shrinkage relative to derived-statistical features."
- Aligns with two-stage-decomposition-beats-joint: gazetteer-feature is a SEPARATE knowledge stage from POS-cascade; do not blob into one feature.
- Aligns with brain-can-do-it: gazetteer lookup is hippocampal-memory analogue; substrate has cleanup_layer + KB-fact atoms -- the same mechanism class is available substrate-side.
- Consistent with substrate-extracted rules-are-PRIOR-not-ORACLE: literature lifts are directional; actual substrate lift will deviate.

## Substrate-product implications

Substrate-classical structured perceptron at low-data has architectural advantages:
- Gazetteer integration is trivial indicator-feature add (LLM equivalent requires re-training or in-context demonstration; substrate just adds a feature)
- Self-training via Viterbi confidence + conformal calibration is cheap-CPU (LLM self-training is GPU-expensive)
- Decomposed feature stages (POS -> gaz -> char-shape) compose cleanly -- LLM black-box does not

Substrate-classical disadvantages at low-data:
- Lacks pre-trained encoder semantic-coverage; relies on explicit feature engineering
- Char-shape is a weak substitute for char-CNN -- the largest single residual gap
- BIO sequence-labeling cannot exploit span-encoder gains observed in literature

Substrate-product positioning: at 5pct labeled + 95pct unlabeled + public gazetteers, substrate-classical structured perceptron is positioned to BEAT calibrated LLM-0.5B-FT if all three interventions ship. If only one intervention ships, substrate-classical likely LOSES by 0.05-0.10 F1 -- the combined-intervention bet is the substrate-product story for the GPU follow-on.

## Citations (verified count: 10)

R1: ELLEN (arXiv:2403.17385); FAME (arXiv:2010.12305); LightNER (arXiv:2109.00720); BiLSTM-CNN-CRF reproducibility (arXiv:2510.10936); Collins 2002 / averaged perceptron (Suster lecture notes; aclanthology N10-1069); EntLM / template-free prompt tuning (arXiv:2109.13532); FFF-NER (NSF biblio 10403517).
R2: ENTDA (arXiv:2210.10343); MELM (arXiv:2108.13655); back-translation augmentation (arXiv:2108.11703); gazetteer-generation (arXiv:2003.03072); GEMNET (Amazon Science); soft gazetteers (arXiv:2005.01866); ContProto / contrastive self-training (arXiv:2305.13628); confidence-based MCPU (arXiv:2204.09589); ANEA distant supervision (arXiv:2102.13129); EER loss partial-supervision (TACL 2022).

Total verified count of distinct relevant citations: ~18 across two rounds.
