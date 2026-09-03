# Research: design validation — "BEM-lite" glass-box bi-encoder for rare-sense WSD

Filed by: research sub-agent, 2026-09-03. Direct follow-up to
`research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` — that note flagged a small
recurrent contextual encoder as the "ceiling candidate, not first build" (arm 3, no falsifiable
prediction registered). USER has since specified a concrete, buildable version of that candidate
(BiGRU-over-frozen-w2v context encoder + mean-w2v gloss encoder, cosine bi-encoder, candidate-
restricted softmax on SemCor) and asked for direct precedent-grounding before committing engineering
time. This note validates that design against the pre-transformer and gloss-informed WSD literature.
Live WebSearch/WebFetch this pass (not from memory) for BEM's actual results/ablation tables.

## HEADLINE

**The design is a fair test of the contextual-encoding lever, not a strawman — but two of its five
simplifications are mis-targeted relative to where BEM's own ablations put the leverage, and will
produce an under-delivery that is about the simplifications, not about whether "small glass-box
contextual encoder" is a viable direction.** Verified from BEM's own ablation table (Blevins &
Zettlemoyer, ACL 2020): freezing the GLOSS encoder costs -6.4 dev F1 (74.5→68.1); freezing the
CONTEXT encoder costs -4.4 (74.5→70.1). The gloss side is the bigger lever in BEM's own accounting,
yet the proposed design gives the gloss side the weakest possible treatment (untrained mean-pooling)
while giving the context side comparatively more machinery (a trained BiGRU). Candidate-restricted
softmax — the one design choice the prompt flagged as a possible flaw — is verified NOT a deviation:
BEM's training loss is cross-entropy over the target lemma's own candidate senses only, identical to
the proposed design.

## Verified numbers (calibration ceiling)

All on the Raganato et al. (2017, EACL) unified all-words WSD evaluation framework unless noted.

| System | ALL F1 | MFS F1 | LFS F1 | Note |
|---|---|---|---|---|
| MFS baseline | 65.5 | — | — | frequency-only floor |
| IMS (Zhong & Ng 2010), SemCor-only | 65.3 (SE13) / 69.3 (SE15) | — | — | SVM + surface features, no embeddings |
| BERT-base (nearest-neighbor style, no gloss encoder) | 73.7 | 94.9 | 37.0 | contextual+subword input alone |
| EWISE (Kumar et al. 2019, ACL) | 71.8 | 93.5 | 31.2 | gloss-embedding space, generalized zero-shot |
| GlossBERT (Huang et al. 2019) | 77.0 | — | — | gloss+context concatenated into one BERT pass |
| BEM (Blevins & Zettlemoyer 2020, ACL) | 79.0 | 94.1 | 52.6 | gloss-informed bi-encoder, joint training |

BEM trained 20 epochs on full SemCor (226,036 instances / 33,362 senses); loss = cross-entropy over
`S_w`, the target lemma's own candidate senses only (verified from paper text via arXiv HTML fetch,
not the full-vocabulary or in-batch-negative alternative).

context2vec (Melamud, Goldberger & Dagan, CoNLL 2016, K16-1006) is architecturally close (BiLSTM
contextual encoder, non-transformer) but not a like-for-like numeric comparator: it is trained as a
bidirectional cloze/LM objective, so its context vector concatenates the FORWARD state stopping
just *before* the target with the BACKWARD state starting just *after* — boundary states that never
see the target token — and it is standardly reported on lexical substitution / sentence completion,
not the Raganato all-words benchmark. No directly comparable all-words F1 was found this pass
(flagging the gap rather than inventing a number). Yuan et al. (2016, COLING C16-1130, LSTM +
semi-supervised label propagation) and Raganato, Delli Bovi & Navigli (2017, EMNLP D17-1120, BiLSTM
sequence-tagging WSD) are the correct "non-transformer contextual encoder ceiling" precedents by
architecture, but their exact ALL-F1 values were not independently re-verified this pass (search
returned qualitative confirmation — "state-of-the-art, especially on verbs" for Yuan et al. — but
not the numeric table); treat any recalled number for these two as unverified until fetched directly.

**Ceiling read:** MFS(65.5) → BERT-base-no-gloss-encoder(73.7) is roughly half of the total gap to
BEM(79.0/LFS 52.6), and that half is attributable to the *input representation* (contextual+subword)
alone, independent of any gloss mechanism. A BiGRU-over-frozen-w2v encoder sits below that BERT-base
point on the input-representation axis. Realistic ceiling for the proposed prototype, if the query-
construction lever is real: high-60s to low-70s ALL F1, LFS meaningfully above the ~31-37 static/
BERT-no-gloss-encoder band but well below BEM's 52.6.

## Architecture critique (per prompt's five points)

**(a) Hidden-at-target vs boundary-concat vs attention.** The BiGRU runs over the whole sentence
*including* the target word, so `h(target)` is dominated by the target's own frozen w2v vector —
which for a rare sense IS the dominant sense's vector (one embedding per surface form). context2vec
(Melamud et al. 2016) avoids exactly this by construction: boundary states that never observe the
target token, forcing the representation to be built entirely from surrounding context. **Fix:**
mask/zero the target position's embedding before the BiGRU pass (predict-the-blank framing), not
concatenate hidden-at-target. Cheap, one line.

**(b) Mean-w2v gloss key vs gloss sequence encoder.** Per BEM's own ablation, the gloss side is the
LARGER lever (-6.4 vs -4.4). An untrained mean-pool is weaker than even BEM's "frozen gloss encoder"
ablation arm, which still had contextualized BERT sub-token representations to average. **Most of
the design's headroom loss is predicted to come from here, not from the context side** — this is the
single most consequential critique in this note.

**(c) Candidate-restricted softmax vs in-batch negatives.** **Not a flaw** — verified identical to
BEM's own training objective (cross-entropy over `S_w` only). It does not damage generalization to
unseen senses because the output space is embedded (gloss vectors), not a fixed softmax head over a
closed class — a property the proposed design already has. Secondary, non-blocking concern:
two-candidate lemmas give a weak contrastive gradient per step.

**(d) Frozen w2v vs learned/subword input.** Per the ceiling read above, roughly HALF of BERT's total
WSD advantage over a static-embedding+MFS floor is attributable to the input representation itself
(contextual + subword), independent of the gloss mechanism — frozen w2v is a real, quantifiable
ceiling-lowering choice, not a cosmetic one.

**(e) SemCor-even only (~half corpus).** Full SemCor (226,036 instances / 33,362 senses) is what
IMS/EWISE/GAS/BEM all train on whole. Halving it hits hardest exactly where the design is being
evaluated: subordinate/rare senses, already the thinnest-covered category in full SemCor. EWISE's
answer to the rare-sense tail is architectural (generalized zero-shot via the gloss-embedding output
space, not more data). GAS (Luo, Liu, Lin & Zhang, 2018, EMNLP D18-1170, hierarchical co-attention)
answers it with an explicit, LEARNED context-gloss interaction plus gloss augmentation from WordNet
example sentences and hypernym/hyponym relation text — the proposed design's "gloss/relation words"
plan is directionally aligned with this but stops at unweighted mean-pooling instead of an
attention/co-attention interaction.

## Cheap decisive test

Two isolated one-line interventions on the existing design, scored independently and jointly, on the
same rare-sense (LFS-analog) held-out population already used for the 0.33/0.35 bag-of-words ceiling
in the companion 2026-09-03 note:
1. **Gloss-side fix only:** replace mean-w2v gloss key with a BiGRU-over-gloss-tokens (even
   orthogonal-init/untrained recurrent weights — isolates "sequence structure" from "learned
   weights").
2. **Context-side fix only:** mask the target token's embedding before the context BiGRU pass
   (boundary/cloze framing).
Run both isolated and combined. BEM's ablation predicts fix 1 alone should recover more ground than
fix 2 alone.

## Falsifiable predictions

**HARD-PASS:** combined (both fixes) accuracy on TOPIC-CONFOUNDED rare-sense items clears the
bag-of-words+gloss floor (0.33-0.35 from the companion note) by a CI-separated margin, AND fix 1
(gloss-side) alone recovers a larger share of that margin than fix 2 (context-side) alone —
reproducing BEM's own ablation asymmetry (-6.4 vs -4.4) as a structural prediction, not just a
generic "more machinery helps" result.

**HARD-FAIL:** no CI-separated gain over the bag-of-words+gloss floor from either fix, alone or
combined; OR fix 2 (context-side) alone outperforms fix 1 (gloss-side) alone by a CI-separated
margin — which would falsify the BEM-ablation-asymmetry prediction and mean the gloss-side critique
in this note is wrong for this substrate's specific gloss/relation-word data (candidate diagnosis:
WordNet gloss text here may already be information-poor relative to BERT's sub-token gloss encoding,
in which case a gloss sequence encoder over impoverished tokens has less to gain from).

P_deflated: **0.35** (raw ~0.50-0.55 — BEM's own published ablation directly supports the gloss>context
asymmetry prediction, which is unusually strong direct-precedent support for this project's research —
deflated 0.15-0.20 per the mandatory lit-scan penalty; no source tests this exact reduced-scale
BiGRU-over-frozen-w2v combination directly, only the full BERT-scale version).

## Cross-thread synthesis

- Direct continuation of `research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` arm 3
  (small recurrent contextual encoder, "ceiling candidate, not first build, no falsifiable prediction
  registered"). This note supplies the falsifiable prediction that note explicitly deferred, for the
  user-specified concrete version of that candidate.
- Does not conflict with that note's arms 1-2 (dependency-filtered second-order context vector;
  exemplar retrieval) — those remain the cheaper, no-training candidates to try first if this
  BiGRU-based design is deprioritized on build cost; all three attack the same diagnosed cap (query
  construction is the bottleneck, not the WordNet gloss candidate space) from different angles.
- `research_wsd_context_conditioned_sense_selection_2026-08-23.md`: additive frequency-prior arm
  REFUTED (0.4702 vs 0.4778, MFS floor not cleared) — orthogonal to this design (this changes query
  AND gloss representation jointly, not a scoring-term addition), does not bear on it directly.
- ORGAN_MAP B3 pattern ("graded quantity built and thrown away one line before use") recurs a third
  time: mean-pooling the gloss side is the same discard-before-use pattern already diagnosed for
  context accumulation (B3) and proposed as exemplar retrieval's fix (2026-09-03 note, arm 2).

## Substrate-product implications

If built, this is the first design on this problem that plausibly clears the ~0.35 bag-of-words
ceiling with a genuine architectural mechanism (contextual encoding) rather than a re-scored/
re-weighted version of the same flat representation (frequency-prior, C3 multiplicative gain — both
already exhausted). The single highest-leverage correction before building: do NOT mean-pool the
gloss side — that is where BEM's own ablation puts the larger lever, and the current design allocates
its one piece of learned recurrent machinery to the side BEM's evidence says matters less. Masking
the target token before the context BiGRU is a free correctness fix or context2vec's own precedent
does not apply. Candidate-restricted softmax should be KEPT as-is — changing it would be motivated by
a misreading of BEM's actual training objective, not by evidence.

## Citations (verified count)

**11 primary sources checked this pass** (live WebSearch/WebFetch, BEM tables read via arXiv HTML
fetch of 2005.02590, not from memory): Blevins & Zettlemoyer 2020 (ACL, 2020.acl-main.95 /
arXiv:2005.02590 — results Table 1/2, ablation Table 3, training objective, all read directly this
pass); Melamud, Goldberger & Dagan 2016 (CoNLL, K16-1006, context2vec — boundary-state architecture
confirmed via abstract/description, exact WSD numeric comparator NOT found this pass, flagged);
Zhong & Ng 2010 (IMS — SemCor-only numbers 65.3/69.3 verified via search); Kumar, Jat, Saxena &
Talukdar 2019 (ACL P19-1568, EWISE — ALL F1 71.8 verified, MFS/LFS breakdown cross-checked against
BEM's Table 2); Huang et al. 2019 (GlossBERT — 77.0 verified via BEM's own comparison table); Luo,
Liu, Lin & Zhang 2018 (EMNLP D18-1170, GAS/hierarchical co-attention — mechanism confirmed via
search+abstract, exact F1 table NOT independently fetched this pass, flagged); Yuan, Richardson,
Doherty, Evans & Altendorf 2016 (COLING C16-1130 — mechanism confirmed, exact numeric table NOT
fetched this pass, flagged); Raganato, Delli Bovi & Navigli 2017 (EMNLP D17-1120, neural sequence
WSD — mechanism confirmed, exact numeric table NOT fetched this pass, flagged); Raganato, Camacho-
Collados & Navigli 2017 (EACL E17-1010, unified evaluation framework — fetch failed to extract
readable text this pass, MFS/IMS numbers instead cross-verified via secondary search results);
Erk & Padó 2008/2010, Thater et al. 2011 — carried forward from the 2026-09-03 companion note, not
re-verified this pass.

## Caveats on this note

- Per the mandatory lit-scan calibration penalty, P estimate above is deflated 0.15-0.20 and capped
  well below 0.50 for the novel-synthesis portion (the specific reduced-scale BiGRU/frozen-w2v
  combination has no direct precedent — only the full BERT-scale ablation asymmetry, which is a
  strong but not identical analogy).
- Two numeric comparators (context2vec's own WSD F1; Yuan et al. 2016 and Raganato et al. 2017
  EMNLP's exact tables) were NOT independently fetched this pass — qualitative mechanism confirmed,
  exact numbers flagged as unverified rather than invented. Worth a follow-up fetch if a precise
  non-transformer-BiLSTM ceiling number becomes decision-relevant.
- GAS (Luo et al. 2018)'s exact F1 table was likewise not independently fetched — its co-attention
  mechanism and gloss-augmentation strategy were confirmed via abstract/secondary sources only.
