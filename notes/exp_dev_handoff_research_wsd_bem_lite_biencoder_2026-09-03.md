# exp_dev hand-off — research: BEM-lite glass-box bi-encoder design validation

**Filed by:** research sub-agent, 2026-09-03.

**Trigger:** `notes/research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md` — validates a
user-proposed small glass-box bi-encoder (BiGRU-over-frozen-w2v context encoder + mean-w2v gloss
encoder, cosine argmax, candidate-restricted softmax on SemCor) against the WSD bi-encoder
literature. Finding: fair test of the contextual-encoding lever overall, but two of five design
choices are mis-targeted relative to BEM's (Blevins & Zettlemoyer 2020) own published ablation,
which shows the GLOSS encoder is the larger lever (-6.4 dev F1 when frozen) vs the CONTEXT encoder
(-4.4 when frozen) — the proposed design gives the gloss side the weakest treatment (untrained
mean-pooling) while giving the context side the more capable treatment (trained BiGRU). Candidate-
restricted softmax is verified NOT a flaw (identical to BEM's own training objective).

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent as of this filing).

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, seed count, threshold bands, corpus split sizes, queue choice, cell name,
smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **Gloss-side fix: replace mean-w2v gloss key with a BiGRU-over-gloss-tokens** (PRIMARY — highest
   expected value per BEM's own ablation asymmetry).
   - Anchor pointer: `notes/research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md`,
     sections "Architecture critique (b)" + "Cheap decisive test" fix 1 + falsifiable predictions.
   - Substrate-product reading: swap only the gloss-side representation (mean-pool → recurrent
     encoder over the same gloss/relation-word token sequence already assembled); everything else
     (context BiGRU, projection dims, cosine readout, candidate-restricted softmax, SemCor-even
     training split) held fixed. Even orthogonal-init/untrained recurrent weights are informative —
     isolates "sequence structure" from "learned weights" as a first cut.
   - Mechanism: Blevins & Zettlemoyer 2020 (ACL, gloss-informed bi-encoder) ablation Table 3, verified
     this pass via direct fetch: frozen gloss encoder costs -6.4 dev F1 vs -4.4 for frozen context
     encoder — the larger lever is on the gloss side.
   - Why now: single largest predicted-value correction identified this pass; does not require new
     training infrastructure beyond what the context-side BiGRU already establishes as buildable.
   - Tier: likely CPU/local (small recurrent net over short gloss token sequences, no GPU-scale need).

2. **Context-side fix: mask the target token's embedding before the BiGRU pass** (companion, cheap,
   near-zero additional infrastructure).
   - Anchor pointer: same research note, "Architecture critique (a)" + "Cheap decisive test" fix 2.
   - Substrate-product reading: zero/mask the target word's own frozen w2v vector at its sentence
     position before the context BiGRU forward pass (predict-the-blank / cloze framing), so the
     context representation cannot be dominated by the target's own (dominant-sense-biased) static
     embedding. Mechanism precedent: Melamud, Goldberger & Dagan 2016 (CoNLL, context2vec) — the
     architecturally closest precedent named in the user's own prompt — builds its context vector
     from boundary states that never observe the target token, for exactly this reason.
   - HARD-PASS/HARD-FAIL logic and the mandatory joint-vs-isolated run design are pre-registered in
     the research note's "Falsifiable predictions" section — run isolated (fix 1 alone, fix 2 alone)
     AND combined; BEM's ablation asymmetry predicts fix 1 alone recovers more ground than fix 2
     alone. If fix 2 alone beats fix 1 alone by a CI-separated margin, that HARD-FAILs the
     gloss-side-is-the-bigger-lever prediction (see note's HARD-FAIL clause) — flag as a genuine
     substrate-specific divergence from BEM (candidate reason given in the note: this substrate's
     WordNet gloss text may be information-poorer than BERT's sub-token gloss encoding).
   - Tier: local (one-line masking change, no new infra).

3. **Do NOT change candidate-restricted softmax to in-batch/full-vocabulary negatives** — explicitly
   NOT authorized as a fix. Verified this pass: BEM's own training loss is cross-entropy over the
   target lemma's own candidate senses only (`S_w`), identical to the proposed design. Changing this
   would be motivated by a misreading of BEM's actual objective, not by evidence. Keep as-is.

---

## Context pointers (pointers, not summaries)

- `notes/research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md` — this drill, full
  numeric comparison table (MFS/IMS/BERT-base/EWISE/GlossBERT/BEM), ablation numbers, citations.
- `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` — parent drill; this
  design is the concrete instantiation of that note's arm 3 (small recurrent contextual encoder,
  previously held with no falsifiable prediction — now supplied).
- `notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md` — the REFUTED additive
  frequency-prior arm; orthogonal to this design, does not block it.
- `notes/STATUS.md` (search "reader_meaning_channel") — current bag-of-words ceiling numbers
  (0.33-0.35 rare-sense accuracy) this design's cheap decisive test scores against.
- `notes/ORGAN_MAP.md` section B3 — "graded quantity built and thrown away one line before use"
  pattern; mean-pooling the gloss side (critique 2b) is this pattern's third occurrence on this
  substrate.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands already drafted
  in the research note; exp_dev finalizes exact N / seed count / thresholds before smoke.
- Self-test per [[feedback-formula-selftests]].
- Mandatory: run gloss-side fix and context-side fix BOTH isolated and combined — the asymmetry
  between them (not just the combined result) is the falsifiable prediction being tested.
- Multi-seed FULL on smoke clearance; replication gate per `tools/replication_gate.py`.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: cell name, N, seed count, threshold bands (within the HARD-PASS/HARD-FAIL
logic pre-registered above), queue choice, ETA, smoke profile, FULL profile, and whether to build
anchor 1, anchor 2, or both in this cycle. This hand-off passes anchor POINTERS + mandatory isolated-
vs-combined run design only — not numerical parameters.
