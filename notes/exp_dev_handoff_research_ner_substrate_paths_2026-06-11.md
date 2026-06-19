# exp_dev hand-off -- research: NER substrate paths to >= 0.85

**Filed:** 2026-06-11 by research sub-agent (Opus) following 2x DEEP drill on NER F1 = 0.58 baseline.

**Trigger:** Research note `notes/research_drill_ner_substrate_paths_2x_2026-06-11.md` -- 5 RESCUE candidates rank-ordered by lit-grounded predicted lift; cheap CPU decisive test identified; substrate-classical NER path to >= 0.85 needs empirical validation.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If paused, hold and surface to user; if active, proceed.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N (training sentences), feature-stack composition, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters beyond the rank-order lift estimates already in the research note.

---

## Anchor candidates (rank-ordered by predicted lift x cost; exp_dev picks)

### Anchor 1 (TOP) -- RESCUE-2: BIO-constrained Viterbi (decoder-side structural prior)
- **Anchor pointer:** `notes/research_drill_ner_substrate_paths_2x_2026-06-11.md` Section (e) Rank 1; falsifiable prediction P1.
- **Substrate-product reading:** substrate temporal-policy Viterbi already exists for POS (PP-379). Adding BIO transition-mask (O->I-X illegal; B-X->I-Y illegal; I-X->I-Y illegal) is ~50 LOC structural prior; lit predicts +0.05-0.10 F1 alone.
- **Tier hint:** local CPU (cheap; substrate-CPU-only is the validated path).
- **Why now:** Highest predicted lift x lowest cost; tests substrate emission+transition primitive for span-bounded sequence labeling. Decisive on whether substrate handles BIO structure at all.

### Anchor 2 -- RESCUE-3: Gazetteer (Wikipedia entity lexicon) binary features
- **Anchor pointer:** research note Section (e) Rank 2 + Section (f) Gazetteer specifics; falsifiable prediction P2.
- **Substrate-product reading:** 4 binary features per token (PER/LOC/ORG/MISC, token/bigram/trigram match against Wikipedia category dumps). Lit precedent: +3-5 F1 on CoNLL-2003 (Florian 2003, Chieu 2003, Ratinov-Roth 2009).
- **Tier hint:** CPU (Wikipedia extract may want remote CPU; feature integration is local).
- **Why now:** independent path from Anchor 1; can run in parallel. Tests external-knowledge binding into substrate Tier-2 bundles.

### Anchor 3 -- RESCUE-1: Bigram boundary features (emission-side)
- **Anchor pointer:** research note Section (e) Rank 3; falsifiable prediction P3.
- **Substrate-product reading:** F[-1]F[0] and F[0]F[1] bigram emission features (Jurafsky SLP3 ch.8 canonical). Substrate already has unigram emission; bigram is extra states.
- **Tier hint:** local CPU.
- **Why now:** cheapest of all RESCUEs; small expected lift but stacks cleanly with Anchor 1 + Anchor 2.

### Anchor 4 -- RESCUE-4: training data 6K -> 15K (scaling)
- **Anchor pointer:** research note Section (e) Rank 4; falsifiable prediction P5.
- **Substrate-product reading:** CoNLL-2003 provides 15K training sentences (~203K tokens). Substrate has been using a 6K subset. Scaling to full 15K tests sample efficiency of count-based methods.
- **Tier hint:** local CPU.
- **Why now:** trivial to set up (data already available); measures the data-scarcity dimension independent of feature engineering.

### Anchor 5 (LAST) -- RESCUE-5: cascade POS -> NER
- **Anchor pointer:** research note Section (e) Rank 5; falsifiable prediction P4.
- **Substrate-product reading:** substrate POS (0.95 from PP-379) feeds NER as pre-filter / per-token feature. Lit precedent MIXED: +7.74 F1 in some settings, -4.63 F1 in others (error propagation).
- **Tier hint:** local CPU.
- **Why now:** deferred to LAST to avoid confounding diagnosis of Anchors 1-4 with cascade-noise. Run after isolated RESCUE measurements done.

### Stretch (if Anchors 1-5 stack to F1 < 0.85)
- **Brown clusters or phrase clusters** -- the Ratinov-Roth 2009 path from 88 to 91 F1; lit estimate +3-4 F1 cumulative.
- **Class-balanced loss weighting** -- inverse-frequency on emission counts; addresses O-class imbalance (~5x O over entity tokens).

---

## Cheap decisive test (per research note section b)

Two-cell CPU smoke (~30 min total) recommended as first dispatch:

- **CELL-1 (RESCUE-2 isolation):** substrate emission-only + BIO + class-balanced loss -> measure F1. Read: lift to >= 0.68 = BIO structural prior contributes; <= 0.62 = structural primitive insufficient.
- **CELL-2 (RESCUE-3 isolation):** substrate emission + gazetteer binary features -> measure F1. Read: gazetteer alone +1 F1 = correct feature binding; < +1 F1 = binding bug.

These two cells decide whether substrate-classical path to 0.85 exists or whether substrate-LLM cascade for NER is the honest answer.

---

## Context pointers (pointers, not summaries)

- `notes/research_drill_ner_substrate_paths_2x_2026-06-11.md` -- full drill note with rank-order, lift estimates, HARD-PASS/HARD-FAIL bars per RESCUE.
- `notes/substrate_capability_map.md` -- NER cap_map row state.
- Memory: `substrate_only_NL_pos_tagger_validated_2026-06-11` -- POS HARD_PASS 0.9499 precedent (same substrate mechanism, different task).
- Memory: `substrate_classical_NLP_methods_outperform_phasor_2026-06-11` -- Tier-2 bundle of HMM emission + transition + Viterbi is the validated substrate-NL primitive.
- Memory: `drill_pattern_temporal_contextual_not_structural_2026-06-11` -- predicts RESCUE-1 + RESCUE-2 (temporal/contextual) over RESCUE-5 (fixed-architecture cascade).

---

## Contract

exp_dev decides queue routing, smoke profile, FULL profile, anchor names, seed counts, threshold bands per existing `agents/exp_dev.md` policies. Research does not pre-specify these.

Research recommends dispatch order: Anchor 1 + Anchor 2 in parallel first (CELL-1 + CELL-2 of the cheap decisive test), then Anchor 3 + Anchor 4 (cheap stacking), then Anchor 5 last (avoid confounding earlier measurements). exp_dev is free to deviate per queue capacity and Tier A/B/C policy.

## Autonomy declaration

Research (Opus) filed this hand-off after 2x DEEP drill at user's explicit request. The 5-RESCUE rank-order, lift estimates, and HARD-PASS/HARD-FAIL bars are research's call. exp_dev's autonomy is over experiment design (numerical parameters, smoke gates, queue routing). User's autonomy is over whether to dispatch at all (pause flag respected).

End of hand-off.
