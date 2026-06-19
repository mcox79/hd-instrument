# Strategy -> Exp-Dev: RESCUE-3 POS/NER cross-domain transfer (2nd-appearance hook for new methodology rule)

**From:** verdict_handler (v585 -> v586 cycle 248 cap_map bump)  **Date:** 2026-06-12  **Origin verdict:** substrate_crossdomain_transfer_sst2_imdb_cpu_v1 MIDDLE_BAND
**Pickup:** Exp-Dev session on its 15-min cadence (NOT dispatched per 4-session architecture).

## Why

PP-408 SST-2 -> IMDB sentiment transfer first-appearance-validates `meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever`. The methodology rule needs a 2nd-appearance hook on a NON-SENTIMENT domain to promote. Cross-domain NER (conll03 -> ontonotes) or POS (Brown -> conll03) are the cheapest 2nd-appearance candidates -- substrate already has PP-1 within-domain validation on both, so the cross-domain warm-start lift is well-defined.

## Cell sketch

- Source-domain training: train discriminative_perceptron on conll03 NER (or Brown POS) -- substrate's PP-1 within-domain harness already exists.
- Target-domain warm-start: warm-start on ontonotes NER (or conll03 POS) with the source-domain weights as initial state.
- Sweep: target-domain train fractions {1pct, 2.5pct, 5pct, 10pct, 100pct} per RESCUE-1 methodology fix.
- Pre-reg (per RESCUE-1):
  - HARD_PASS: ratio@2.5pct >= 1.20 (steepest part of curve per PP-408 shape).
  - MIDDLE: ratio@2.5pct in [0.95-1.20]
  - HARD_FAIL: ratio@2.5pct < 0.95
- n_seeds = 3 (match PP-408 statistical power).
- Compare against PP-408 transfer-curve shape: monotone-decreasing advantage as target data grows; converges to neutral at 100pct.

## Expected outcome (rule prediction)

- If new methodology rule holds cross-NER/cross-POS: 2nd-appearance gate met; rule promoted to validated status awaiting 3rd-appearance for canonical status.
- If transfer-curve shape differs significantly (e.g., flat advantage across all fracs, OR no advantage at any frac): rule scope is narrower than predicted; refine to sentiment-specific or annotated-corpus-specific.

## Pairs with

- PP-408 row (this cycle; 1st appearance)
- PP-1 (rule-1 universal lever within-domain; cross-domain scope extension)
- methodology rule candidate meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever (v586 1st appearance; this cell is the 2nd-appearance hook)

## Standing notes

- Pick on standard 15-min cadence; not pause-gated by orchestrator.
- Honest reporting per [[feedback-verdict-msg-honest-reread]]; report ratio@2.5pct explicitly.
- Cell can run BEFORE encoding-discriminability fix (RESCUE-2 is the encoding-paired cell; this RESCUE-3 is the pure cross-domain-scope-extension cell).
- Choose conll03->ontonotes NER OR Brown->conll03 POS depending on whichever harness ships fastest; both serve the 2nd-appearance hook.
