# Routing: strategy v270 back-validation cap_map deltas (2026-05-29)

**Recipient:** strategy (or verdict_handler when it next runs cap_map-bump phase)
**Source:** main-thread back-validation drive 2026-05-29
**Trigger:** 32b1337 runner schema-gate fix + user prompt "did you see the
potential experiments we could do with old experimental results?"
**Status:** ANALYSIS COMPLETE. RECOMMENDED ACTION = ZERO-DELTA ANNOTATION.

## Summary

Back-validation of all 18 label-vs-honest catches in the DISPATCH_FAILURE_MISCLASSIFICATION
sub-flavor scope (catches 106..123 in v265+v266+v267+v268+v269) found:

- 13 VERIFIED_HARD_PASS at production scale on remote metrics
- 5 PARTIAL (honest MIDDLE_BAND, no conversion warranted)
- 0 GENUINE_FAILURE
- 0 UNRECOVERABLE

**ZERO cap_map row LIFTS recommended.** Every VERIFIED_HARD_PASS catch was
already absorbed into the cap_map at the time the verdict_handler processed
the verdict (the honest re-read protocol + remote-first contract worked as
designed; the cap_map state already reflects the honest reading).

Full audit at: `notes/label_vs_honest_back_validation_2026-05-29.md`

## Recommended cap_map row LIFTS

NONE.

## Recommended cap_map annotations

Optional v270 annotation entry (zero-cost; visibility only):

> v270 ANNOTATION-ONLY: back-validation of 18 label-vs-honest catches scope
> 106..123 (DFM + DISPATCH_HEADLINE_OVER_CLAIM + MIDDLE_BAND_HIDES_DIRECTIONAL_
> CORROBORATION sub-flavors) re-applied 32b1337 schema gate to remote metrics:
> 13 VERIFIED_HARD_PASS + 5 PARTIAL + 0 GENUINE_FAILURE + 0 UNRECOVERABLE.
> 0 row deltas; all 13 HARD_PASS already absorbed at verdict-time via honest
> re-read remote-first contract. Confirms the forward verdict_handler pipeline
> worked correctly under the broken-runner regime. 32b1337 prevents the
> verdict_handler tax going forward but does not unlock past-state corrections.

## Open follow-ups

NONE within the back-validation scope. The audit closes cleanly.

If the user / next strategy cycle wants to extend the back-validation to
catches 1..105 (other sub-flavors -- OVER-CLAIM, headline-framing, MMD-vs-MP-KS,
dispatch-context-vs-queue.json), file a new routing note. Expected yield is
similarly zero because those catches were also verdict_handler honest reads
that overrode literal labels at verdict-time. No schema-gate dependency.

## ONE-line summary

back-validated 18/123 (DFM scope): 13 VERIFIED_HARD_PASS / 0 GENUINE_FAILURE
/ 5 PARTIAL / 0 UNRECOVERABLE; 0 cap_map row LIFTS recommended.
