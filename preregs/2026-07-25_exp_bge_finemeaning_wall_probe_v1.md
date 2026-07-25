# Pre-reg: bge_finemeaning_wall_probe_v1

Author: hdi_exp_dev | Date: 2026-07-25 | Contract: INLINE-LOCAL, foreground-to-completion, no push/remote-persist.

## Question (one variable = the representation / meaning SOURCE)
Is the WorldTree fine-content discrimination signal PRESENT in text (reachable by a strong text encoder)
vs absent from raw co-occurrence, on the SAME wall that frozen GloVe hit (VET-confirmed abda1634 / seq
29558: GloVe held-out-to-NEW-concepts ~0.106 below chance, in-vocab ~0.324 = memorization)?

Frame (Director re-scope 2026-07-25): BGE-large is a DIAGNOSTIC CEILING, NOT a candidate encoder to
adopt/distill (a borrowed vector is the shortcut we reject). The number answers ONE routing question for
OUR OWN grounding build: does the fine-discrimination signal exist in text via relational/contrastive
supervision (BGE) vs raw co-occurrence (GloVe) vs substrate-native char-overlap (char_trigram)?

## Design (reuses exp_learned_meaning_frontend_realslice_v1 harness; swaps ONLY the encoder)
- Shared item set = the GloVe-in-vocab items (identical to the GloVe cell). Per-relation value pool =
  GloVe-in-vocab values (identical pool for all reps). ONE VARIABLE = representation, scored on IDENTICAL
  candidate sets.
- Encoders: GloVe(300d, raw co-occurrence) / BGE-large `BAAI/bge-large-en-v1.5`(1024d, relational text
  supervision; local HF, offline; the underlying `bge_large_v2_name_*` teacher generation) / char_trigram
  (`hdlab/char_trigram_encoder`, 4096d, substrate-native deterministic; NOT composed/concept encoders which
  need corpus fitting). BGE tests the SOURCE directly (encode WorldTree strings fresh); NOT the distilled
  student encoder.
- Two distractor constructions from the IDENTICAL pool (fairness / can-fail):
  GLOVE-NATIVE = nearest-K wrong values by GloVe cosine (original wall; rigged for GloVe);
  BGE-NATIVE   = nearest-K wrong values by BGE cosine (honest-HARDEST for BGE; can-fail).
- PRIMARY = ZERO-FIT cosine on BGE-NATIVE candidate sets, BGE vs GloVe vs chance (memorization-proof, no
  held-out split needed). SECONDARY = learned-linear (converged ridge) with the SAME held-out-to-NEW-
  concepts protocol + shuffled-target control (reported, NOT gated).
- Tier: gate on FINE (distinctive content). COARSE = KINDOF (reported).

## Bands (a priori)
- CLEAR_OVER_CHANCE = 0.15 ; MARGIN_OVER_GLOVE = 0.10 ; THIN_OVER_CHANCE = 0.05 ; FROZEN_SAT = 0.85 ;
  DIST_NEAR_MIN = 0.30 ; MIN_EVAL_FINE = 60.
- HARD-PASS (BGE-CLEARS-WALL): BGE zero-fit fine (bge-native) CI-lower > chance AND (BGE-chance) >= 0.15
  AND (BGE - GloVe same candidate set) >= 0.10 -> the fine signal exists in text via relational supervision
  where raw co-occurrence cannot reach it. ROUTING FACT: aim OUR grounding at that signal; do NOT adopt BGE.
- HARD-FAIL (BGE-ALSO-THIN): (BGE-chance) < 0.05 OR CI-lower <= chance -> signal not cheaply present in text
  similarity; wall deeper than any off-the-shelf embedder -> grounding/structure required.
- MIDDLE: materially above chance but below the CLEAR bar (partial fine signal in text).
- INVALID: BGE-native distractors not near (<0.30) OR BGE fine saturates (>=0.85) OR < 60 fine items.

## Design gates
- Real baseline (GloVe frozen = the wall) YES; can-fail (BGE-native = hardest-for-BGE; BGE genuinely can
  land near chance) YES; difficulty-on (report mean BGE cos(gold,distractor)) YES; one-variable (identical
  items + identical candidates; only encoder) YES. No memorization confound (zero-fit primary). Learned arm:
  no-leak held-out concepts + shuffled-target control.
- DISCRIMINATOR-SURVIVES-SCALE: zero-fit is scale-INVARIANT (no training) -> smoke mirrors full at smaller
  N/CI; the BGE-vs-GloVe direction shows at smoke (analytical justification, confirmed: smoke MIDDLE == full
  MIDDLE).

## Self-test
Planted zero-fit env (structured concept=own value+noise -> acc 1.0; destroyed=random -> acc 0.08:
fires AND fails). Real path: parse 2 tables + GloVe + BGE + char_trigram encode + shared env + zero-fit +
converged-linear; determinism + arms-differ asserted. PASS.

## Result (MEASURED @ data/exp_bge_finemeaning_wall_probe_v1/metrics.json; full, 1821 items / 1125 fine)
- Zero-fit FINE, BGE-native cands: BGE 0.374 (CI 0.346-0.403) vs GloVe 0.354 vs char_trigram 0.232 vs
  chance 0.171. Lift over chance 0.203 (CI-lower > chance); margin over GloVe (same set) 0.020 (< 0.10).
- Zero-fit FINE, GloVe-native cands (original wall): GloVe 0.328 ; BGE 0.468 (inflated, GloVe-near!=BGE-near).
- Difficulty-on: BGE-native mean cos(gold,distractor) 0.756 (hard); not saturated.
- Learned-linear (secondary): BGE in-vocab 0.859 / held-out 0.228 / shuffled 0.111 ; GloVe in-vocab 0.450 /
  held-out 0.128. BGE learning GENERALIZES to new concepts (0.228 > chance) where GloVe memorizes
  (held-out 0.128 <= chance = the wall reproduced); shuffled below chance (no leak).
- VERDICT: MIDDLE. Partial fine signal in text: BGE beats raw co-occurrence and the substrate-native floor
  in absolute terms, but only modestly on the honest-hard (BGE-native) comparison (~0.02-0.05 over GloVe).
  Text-similarity alone (even a strong relationally-supervised encoder) does NOT dramatically clear this
  fine-content wall. The sharper differentiator is under LEARNING (held-out generalization). BGE = DIAGNOSTIC.

VET-PENDING (skunkworks owns landed-VET; this cell banks NO atoms).
