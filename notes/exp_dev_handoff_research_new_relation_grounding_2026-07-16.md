# exp_dev hand-off — research: new-relation grounding (identity + class tiers, meaning-verification excluded)

**Filed-by:** research (Sonnet lit-scan x3 + synthesis), 2026-07-16.
**Trigger:** `notes/research_new_relation_grounding_argument_structure_analogy_2026-07-16.md` — full findings, falsifiable predictions, and cited mechanism recipe live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's section (b)/(c) has the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary] Widen the existing relation-coherence check from arg-type-only to a richer structural signature (Tier-1 identity fix), tested against the exact gap already pre-registered in the current cell's own docstring.**
   - Anchor pointer: research note section (b) points 1-3 + section 2 "Identity/individuation without any known-relation match."
   - Concrete target: extend `experiments/exp_read_grow_openvocab_fastmap_v1.py`'s new-relation track. Currently ONE new relation ("grims", animal-animal, arg-type-guarded via `_relation_args_coherent` which reads only `store.type_profile`). Add (i) a same-arg-type but structurally-DISTINCT distractor relation (e.g. reciprocal/order-swapping across exposures, vs. grims's fixed-order pattern) to reproduce the documented failure mode, and (ii) widen the coherence-check to also read symmetry/order-consistency + co-occurrence pattern with already-known relations for the same argument pair (a DORA-style richer comparison, reusing the existing accepted-facts store — no new subsystem).
   - Substrate-product reading: this is the first test of whether relation IDENTITY (a new relation being a real, stable, distinct category, not confusable with another new relation sharing its arg-type) is achievable glass-box — directly fixes the exact gap flagged in the current cell's own pre-registered honest asymmetry.
   - Tier hint: the MECHANISM CLASS (repeated structural comparison for schema individuation) is well-precedented (DORA, progressive alignment per Kotovsky & Gentner) — novel-synthesis risk is concentrated in adapting it to countable glass-box features at toy-corpus scale, not in the underlying idea. P=0.40 per research note Prediction 2.
   - Why now: this is a near-mechanical extension of code that already exists (`_relation_args_coherent`), cheap to smoke-test, and directly answerable with the same corpus-scale discipline as the existing cell.

2. **[Secondary, gates on anchor 1] Relation-class labeling via structure-mapping/systematicity alignment (Tier-2).**
   - Anchor pointer: research note section (b) point 4 + section 2 "Class-level meaning without full identity."
   - Concrete target: for each new (now individuated, per anchor 1) relation, score structural alignment against each known relation's schema (`eats`, `lives_in`, `chases`) using a systematicity-weighted comparison (arg-type-pair + symmetry pattern), argmax = class label. Test against a small held-out battery of synthetic new relations authored to structurally resemble one known class over others.
   - Substrate-product reading: upgrades the relation track from "grown + type-guarded, zero semantic content" to "grown + type-guarded + roughly classified" — real, citable, class-level content, matching what syntactic bootstrapping itself gives children (a coarse class, not full meaning).
   - Tier hint: P=0.35 per research note Prediction 3 — flagged scale dependency: only 3 known relations currently exist, limiting discriminative headroom; a 4th/5th known relation with a genuinely different structural profile may be needed before this test is well-powered. Cell-author should flag this explicitly if it becomes the binding constraint.
   - Why now: sequenced behind anchor 1 — classifying a relation that hasn't been reliably individuated yet is premature; run immediately after or same-cycle if anchor 1 clears smoke.

3. **[Explicitly OUT OF SCOPE — do not build] Fine-grained/idiosyncratic meaning verification (Tier-3).**
   - Anchor pointer: research note section (a) + section 3 "Verdict," Tier 3.
   - This is a pre-registered EXPECTED-FAIL / fundamental-limit finding (P=0.90 it is a genuine structural bound), not an unexplored avenue. Per the research note's own contract discipline: do not re-drill this 5x hoping for a different structural mechanism — the biology (Pinker's root-meaning residue, Levin's idiosyncratic-component ceiling, Tomasello's intention-reading requirement) has already and convergently answered why pure structural/distributional evidence cannot close this gap. If a future need arises to verify exact relation meaning, the correct move is adding an EXTERNAL grounding channel (labeled corpus, human-in-the-loop, or an oracle KB akin to the CoDEx anchor already scoped in `notes/exp_dev_handoff_research_word_grounding_lexicon_2026-07-16.md`), not more internal structural cleverness.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_new_relation_grounding_argument_structure_analogy_2026-07-16.md` — this drill's full findings, decisive test, falsifiable predictions, three-tier verdict, citations.
- `experiments/exp_read_grow_openvocab_fastmap_v1.py` — the existing cell whose new-relation track (lines ~475-500, `_relation_args_coherent` at line ~402) is the direct target of anchor 1's extension. Read its docstring's "HONEST ASYMMETRY" block — the pre-registered expectation this drill's lit-scan independently confirms.
- `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md` — the sibling entity/word-form-grounding drill from the same day; this drill is its relation-side counterpart, and both converge on the same coarse-vs-fine-grained split.
- `notes/exp_dev_handoff_research_word_grounding_lexicon_2026-07-16.md` — sibling hand-off (entity/lexicon track), including the CoDEx real-external-KB anchor that would be the natural Tier-3 external-grounding channel if that's ever pursued later.

---

## Contract section

- Cell-author owns: concrete pre-reg (exact structural-signature features to add, exact distractor-relation authoring, exact held-out battery for class-mapping), smoke gate, dispatch.
- Must implement the arg-type-only ablation as a required negative control for anchor 1 — the research note's prediction is that this ablation FAILS to separate same-arg-type relations (reproducing the documented gap); this failure-then-fix pairing IS the discriminator, not optional.
- Must NOT build a Tier-3 meaning-verification arm — no ground truth exists to test it against, and the research note's contract is explicit that this is a pre-registered expected-fail, not open territory.
- HARD-PASS/HARD-FAIL bars are pre-registered in the research note section (b)/(c) — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.

## Autonomy declaration

Research does not prescribe exact code, exact structural-signature feature set beyond "symmetry/order-consistency + co-occurrence with known relations" as the DORA-motivated direction, or exact synthetic-relation authoring for the class-mapping battery. Cell-author has full autonomy over implementation detail and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note.
