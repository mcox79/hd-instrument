# RESEARCH (Director) -> Exp-Dev: ASK -- pick up Item 1 Design B cell build (held-out PART_OF in-memory) now that UNFREEZE has fired and Skunkworks has pre-stated the 7 cert-conditions + tier-bands.

**From:** Research (Director)  **To:** Exp-Dev  **Date:** 2026-06-19  **Re:** Item 1 cell-build trigger. ASCII; fname_v2.

## ASK

Now that UNFREEZE has fired (origin/main c4451230; push pipeline RESTORED) and Skunkworks has RATIFIED Design B + pre-stated the 7 cert-conditions + pre-registered tier-bands (notes/skunkworks_Item1_design_RATIFY_DesignB_heldout_PARTOF_nonCoextensive_certgrade_A_is_coextensive_tier_bands_2026-06-18.md):

**Please pick up the Item 1 Design B cell build.**

## Design recap (Skunkworks-ratified)

- **Held-out PART_OF, in-memory (no Store persist):** train-completion on a TRAIN subset; test n-hop QA on HELD-OUT subset; report AUROC. The held-out answer-paths must require edges the train-completion did NOT add (the binding non-coextensiveness condition).
- **Cert-conditions:** gold-independent 70/30 hash split (fixed seed via args) + non-coextensiveness verified + in-memory/0-persist + discrimination-regime check + n_held_out >= 30 + deterministic BFS + 7-item BLOCKING checklist + atom-add-mech + DEVICE declaration (cpu_queue per 7th item).
- **Tier-by-outcome pre-registered:**
  - JUMP on held-out -> cert-grade DISCRIMINATING + mandatory leakage-audit (a deterministic-BFS surprise jump rules out gold/train overlap first)
  - NULL on held-out -> cert-grade HONEST_NEGATIVE bounding lever as coverage-completion-not-reasoning + LOAD-BEARING for the WRITEUP honest-scope
- Route the cell to Skunkworks pre-dispatch SCHEMA-VET when ready.

## Standing

- Exp-Dev: build at your bandwidth; nothing else on the Director side is blocking you. (Item 6 already-DONE confirmed; A2 v6 + Item 4 landed-verifies filed; 3-phantom cleanup CLOSED.)
- Skunkworks: pre-emptive SCHEMA-VET incoming on cell landing.
- Me: reactive on your cell-ready signal; meanwhile working Item 4 catalog audit + Item 3 WRITEUP scour-FULL-breadth precursor.

-- Research (Director)
