# RESEARCH — where SOTA parsers get their accuracy, and a glass-box route to recover the difference (2026-09-12)

Research drill dispatched by strategy (Opus agent, 53 lookups) after the owner asked to "look at the aggressive SOTA systems to
understand how they get such high scores, and then design a glass-box method to recover the difference". Substance kept; numbers cited.

## 1. What the labelled systems actually buy
- Dozat & Manning (ICLR 2017): 95.74 UAS / 94.08 LAS on PTB-SD with a BiLSTM + biaffine scorer over ~40k labelled trees. Ablations:
  deep biaffine 95.75, shallow 95.74, MLP attention 95.53, 2 LSTM layers 95.62, GRU 93.18; **no POS tags at all beats tags without
  dropout** — the tag channel is worth tenths, not points. Anderson & Gómez-Rodríguez (CoNLL 2020): predicted UPOS helps only at very
  high tagging accuracy.
- Pretrained encoders add ~1.7 UAS at the top: Mrini et al. 2020 97.42 (XLNet + label attention); Zhou & Zhao 97.3. Kulmizev et al.
  (EMNLP 2019): the gain is global-structure-in-local-features. Second-order structure in the supervised regime: modest (CRF2o).
- Error shape (McDonald & Nivre 2007/2011; UD error analyses): accuracy falls with sentence and arc length; hardest relations conj,
  acl/relcl, advcl, obl/nmod (PP attachment), xcomp/ccomp; det/aux/case/nsubj/root above 90.

## 2. Labels vs representation — how cheap the labelled signal is
- Rotman & Reichart (TACL 2019): the same biaffine parser on **100 labelled sentences already reaches ~74–80 UAS**; 500 → 79–82; 1000 →
  81–84. Resource-spectrum study (2026): 81.70 UAS with 369 sentences (Xhosa), 95.53 with 10k (French); the knee is at 800–1,400
  sentences (COLING 2018). **~100 gold trees would beat our 0.53; ~400 would match a supervised perceptron.**
- Label-free reads of rich predictive models are weak once the PROBE is unsupervised: Hewitt & Manning 2019 UUAS 82.5 uses a probe
  fit on gold trees; without labels: Clark et al. 2019 attention heads 77 UAS (with GloVe) vs 58 baseline, `prep` only 66.7; Perturbed
  Masking (Wu et al., ACL 2020) 58.6 UAS on WSJ10, 41.7 UAS on PUD; StructFormer 46.2 UAS without gold POS.
- Classical label-free induction is BETTER than LM probes: **67.9 UAS all lengths (Sib&L-NDMV, Yang, Jiang, Han & Tu, COLING 2020),
  ensemble 68.8 (Lin et al. 2025)**; first-order NE-DMV 51.0 → L-NDMV 62.4 → sibling second-order 67.9: **second-order (sibling)
  factorisation = +13.3, the biggest published label-free lever.** Tri-training +3.0 LAS (no pretrained) / +1.2 (ELMo); self-training
  +5 UAS at 100 labels, +1–3 at 1000 — amplifiers of a ≥75 seed, not creators of one.

## 3. Per failure type: the label-free knowledge that supplies the distinction
- **PP attachment (obl/nmod):** Ratnaparkhi 1998 mines UNAMBIGUOUS attachments from ~970k raw sentences by proximity → **81.91%** on the
  PTB PP set (baseline 70.39; supervised 84.5); Hindle & Rooth 1993 lexical association. Brain: constraint integration (MacDonald
  1994), referential context (Altmann & Steedman 1988).
- **Coordination (conj/cc):** parallelism is PINNED (Frazier, Munn & Clifton 2000); Dubey, Keller & Sturt (Cognition 2008) model it as
  SYNTACTIC PRIMING — rule probability conditioned on prior use in context — directly a cue; Hogan (ACL 2007) conjunct symmetry.
- **Clausal complements (ccomp/xcomp):** verb subcategorisation acquired from reading (Briscoe & Carroll 1997; Korhonen 2002).
- **Long arcs:** dependency-length minimisation (functional deps mean 1.71, lexical 2.87; Futrell et al. 2015); Smith & Eisner 2006
  learning-only length penalty 41.6 → 61.8 on WSJ10 F1.
- **NP internals / relatives:** item-based constructions and chunking (Ponvert 2011 NPs F 76.7); definiteness/referential cues.

## 4. Self-generated supervision
Prediction-based signal alone tops out low (41.7 / 46.2 UAS); agreement/confidence methods add 1–5 points to a good parser. The
generalising form of Ratnaparkhi: **mine the cases the competition finds unambiguous (high posterior margin), learn lexical/frame
statistics from them, re-decode** — self-training restricted to a cue channel.

## 5. Ranked recovery plan (no labelled trees)
1. **Second-order cue competition (sibling + grandparent)** — +13.3 documented; brain: cue-based retrieval whose cue includes what the
   head already attached (valence occupancy). Needs the projective second-order inside–outside (Matrix-Tree is first-order).
2. **Learning-time length bias + curriculum** — +20.2 F1 (Smith & Eisner) in the DMV regime; OUR first test (contrast-learned competition,
   three mechanisms combined) did NOT beat the plain path (0.400 vs 0.437 at r2) — disentangle before concluding.
3. **Unambiguous-case mining for PP attachment** — 81.9% from raw text on our worst comprehension-relevant class.
4. **Parallelism-as-priming for coordination.** 5. **Valence/frame occupancy learned from our own posteriors** (ccomp/xcomp).
6. **Token-level categories.** 7. **Confidence/agreement self-training last** (1–5 points).
**Ceiling, honestly:** 67.9–68.8 UAS is the documented label-free ceiling for all-length English; nothing above ~0.70 has been
published without labelled trees. What labels buy irreplaceably is ANNOTATION CONVENTION (which item heads a copula / coordination /
case construction) — which our own error anatomy (2026-09-12) confirms: a third of our gap to the supervised parser is function-word
convention (punct 0.056, case 0.037, cop 0.017, det 0.015, cc 0.015, flat 0.012) → stated as item-based constructions, no labels
needed (`attachment_arm.function_word_arcs`).

## 6. Owner question raised by the drill
"A hundred hand-checked trees would add ~25 points but buy bookkeeping convention, not understanding — stay strictly label-free
(realistic target ~0.68) or allow a tiny convention-calibration set?" Strategy's answer: the conventions are deterministic frames we
can state as constructions (done); the comprehension-relevant gap (nsubj/obj/obl/nmod/clausal ≈ 0.10) is where learning must work.

Sources: Dozat & Manning 2017; Mrini et al. 2020; Zhang, Li & Zhang 2020; Kulmizev et al. 2019; Anderson & Gómez-Rodríguez 2020;
McDonald & Nivre 2007/2011; Hewitt & Manning 2019; Clark et al. 2019; Htut et al. 2019; Wu et al. 2020; Shen et al. 2021; Yang et al.
2020; Lin et al. 2025; Rotman & Reichart 2019; Revisiting Tri-training 2021; Ratnaparkhi 1998; Hindle & Rooth 1993; Hogan 2007;
Dubey, Keller & Sturt 2008; Briscoe & Carroll 1997; Futrell, Mahowald & Gibson 2015; Frazier, Munn & Clifton 2000; Altmann & Steedman 1988.
