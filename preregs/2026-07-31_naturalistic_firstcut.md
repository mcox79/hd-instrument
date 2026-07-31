# Pre-reg: Naturalistic FIRST-CUT -- wire gate for the certified encoder break (atom 29593)

Cell: `experiments/exp_situation_model_naturalistic_firstcut_v1.py`
Anchor: `situation_model_naturalistic_firstcut_v1`
Date: 2026-07-31. Director spawn a63300db. MEASUREMENT-FIRST. Director+USER gated (NOT wire/deploy/full-retrain).

## Question
Does the certified minimal-unfreeze (top-1-layer, 3.15M-param) fine-tune of the substrate's OWN v2 encoder
(atom 29593; lifts held-out situation-model loop 0.52->0.83 on the SYNTHETIC colors/templated harness via
cross-frame entity re-identification) HOLD on NON-TEMPLATED, cross-surface-coreference text, or was the
certified break SYNTHETIC-BOUND?

## LOAD-BEARING CORPUS/FAIRNESS FINDING (exp_dev owns the corpus call per contract)
The certified v2 encoder (`base.V2Transformer` + BPE tokenizer, ckpt
`data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt`) was trained on a CLOSED ~50-word vocabulary
(20 colors + 30 slot-nouns + ~12 function/role words) over ~3006 templated sentences, with SENT_CAP=16.
Consequence: OPEN-DOMAIN real text (GAP / WSC / OntoNotes / Wikipedia / news) is NOT a FAIR test on THIS
encoder -- every proper noun / real content word is OUT-OF-VOCABULARY, so frozen craters for TOKENIZATION
reasons and a 220-step top-1-layer fine-tune cannot learn new subword semantics; a crater there measures OOV,
not entity re-id (confounded, non-falsifiable). Genuinely open-domain naturalistic evaluation REQUIRES
re-pretraining the encoder on real text = the full grounding program (USER-strategic); this FIRST-CUT does
NOT do that.

The FAIR naturalistic test buildable on the certified encoder AS-IS is NON-TEMPLATED, cross-surface
coreference WITHIN the encoder's own proven vocabulary. "The corpus" = the encoder's own lexicon recomposed
into genuinely non-templated passages via:
- STRUCTURAL non-templating: each event/query frame rendered in one of several DISTINCT grammatical clause
  structures (event: set-then-placed vs placed-then-set role-order swap; query: ex-situ vs in-situ wh),
  selected DETERMINISTICALLY per (frame, entity, args) -> not one rigid template.
- CROSS-SURFACE reference: each entity mention is "the <MOD> <color>" with <MOD> from a shared 8-adjective
  pool, DETERMINISTICALLY keyed on (frame, entity, args), so the SAME entity has a DIFFERENT surface string
  across its statement / tag / query frames -> exact-token-copy on the ENT handle FAILS. Color word persists
  as the shared binding handle -> re-id stays rep-level FAIR on HELD-OUT colors.
- b-type (description-addressed "the one tagged X") frames LEFT UNMODIFIED = token-copy-IMMUNE control (target
  entity color absent from the query span).
HONEST SCOPE clause on every number: NATURALISTIC-WITHIN-ENCODER-VOCABULARY (structural + surface
non-templating), NOT open-domain real text. Strictly harder than the certified harness and than the
surface-only harder-construction cell (this ALSO varies clause structure).

## Design (ONE variable = ENCODER WEIGHTS: frozen vs minimal-unfreeze fine-tune)
Loop/oracle/floors/guard/geometry reused VERBATIM from the certified cell via hc/lt/eb/ef/ih/clean.
- TRANSFER (test 1, reported): certified fine-tune (trained on EASY template) evaluated on naturalistic.
- ROBUSTNESS (test 2, the GATED can-fail): fine-tune (same objective, depth=1) ON naturalistic.
- EASY-ANCHOR positive control: reproduce the certified frozen->tuned lift on EASY held-out.
- Held-out COLORS (SPLIT_SEED) = the fairness gate; all arms share identical naturalistic eval passages.

## Bands (INHERITED VERBATIM from the certified / harder-construction cells -- NOT chosen for this result;
## imported from hc.* so they cannot be retrofitted)
Gate on ROBUSTNESS; TRANSFER reported.
- HARD_PASS (HOLDS on naturalistic): robust_lift >= 0.05 AND capture >= 0.35 of (oracle-frozen) headroom AND
  every seed lifts (min>0) AND collapse-guard holds [C1 tuned>=frozen; C2 wc_drift<=0.15; C3 entcons>=0.85;
  C4 q_agree>=0.55] AND memorization gap <= 0.15.
- HARD_FAIL (SYNTHETIC-BOUND): robust_lift <= 0.02 OR collapse (guard C1/C3 fail with cratered loop).
- MIDDLE: moved but did not clear HARD_PASS.
- INVALID: a floor did not collapse OR POOLED reservoir-decodable OR construction not demonstrably harder
  (frozen-degradation < min) OR uninformative (oracle-frozen headroom < 0.05, e.g. structural OOD craters the
  oracle too).

## Falsifiability at smoke (must hold or FIX before trusting)
- exact-token-copy on the ENT handle FAILS: cross-frame ENT-surface repeat rate craters (easy 1.0 -> nat).
- POOLED_READER + deterministic floors + most-recent COLLAPSE (front-end-independent shortcut fails).
- frozen honestly BELOW oracle (informative headroom).
- construction demonstrably harder: frozen-representation degradation (loop and/or entcons) vs easy.

## Compute architecture
mixed -- top-layer SGD fine-tune (batched fwd+bwd, batch 128, CPU) + closed-form FHRR eval loop.
Storage: per-entity content-gated overwrite (sharded per slot) + FHRR-superposed roles. Resumable per-seed
(units.jsonl), atomic tmp_replace metrics, ASCII-only, deterministic seeding, no BaseException.
CPU-first, INLINE-LOCAL foreground-to-completion (--budget-sec keeps each call < 10 min), push-free.
EXPECTED_N_UNITS = 2 (seeds 7,13). progress_logging: print_flush_true.
