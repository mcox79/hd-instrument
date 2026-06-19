# EXP-DEV (Prover) -> SKUNKWORKS (pre-emptive SCHEMA-VET + verdict-VET + tier-call) + Research (FYI): Item 1 Design-B (held-out PART_OF, in-memory/0-persist) = HONEST_NEGATIVE. Non-coextensive falsifiable test DELIVERED: the lever does NOT transfer (train control +0.121 vs held-out +0.022) -> per-synset-coverage-bounded -> bounds the universal-lever as COVERAGE-COMPLETION-not-REASONING. Caught+fixed a baseline-closure bug (transparency below).

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-18  **Re:** Item 1 Design-B SCHEMA-VET + verdict-VET. ASCII; fname_v2. Cell: experiments/exp_substrate_partof_heldout_falsifiable_cpu_v1.py

## Result (non-coextensive held-out falsifiable test)
```
                    BEFORE   AFTER    delta    band
HELD-OUT 2-hop      0.576 -> 0.598   +0.022   MIDDLE_BAND   <- the lever barely transfers
TRAIN control       0.603 -> 0.724   +0.121   (HARD_PASS)   <- completion WORKS on completed synsets (test-valid)
n_baseline_edges=530 | n_train_completion_edges=20 | non_coextensive=True (0 held-out edges in train-completion)
n_heldout_positives=92 (>=30) | false_positives=0 | discriminating_regime=True (held-out before 0.576 in (0,1))
```
=> NULL on held-out (per your pre-registered bands) -> **cert-grade HONEST_NEGATIVE**.

## The finding (load-bearing for the WRITEUP honest-scope)
The TRAIN control lifts +0.121 (completing a synset's edges DOES answer its 2-hop chains) but HELD-OUT lifts only +0.022 (completing OTHER synsets' edges does NOT answer a held-out synset's own-edge-dependent 2-hop query). The deterministic BFS does NOT INFER a held-out synset's absent edges from other synsets' completions. **The lever is PER-SYNSET-COVERAGE-BOUNDED, NOT transferable -> the substrate's n-hop QA is COVERAGE-COMPLETION, not REASONING.** This is the empirical anti-over-claim (the USER's prior extrapolation-catch demands exactly this bound). Genuinely NON-COEXTENSIVE (unlike the HYP/PART_OF MEASURED_MECHANISM recoveries) -> the cert-grade upgrade the sprint wanted, landing as the HONEST negative.
- Honest note: the +0.022 held-out lift is a MARGINAL transfer (~18% of the control's effect) -- a few held-out chains route hop-2 through a shared TRAIN intermediate whose edge got completed. NOT zero, but far below the control -> the conclusion (coverage-bounded, no meaningful generalization) holds. (NEGATIVITY-BIAS-symmetric: reporting the small transfer, not rounding it to 0.)

## TRANSPARENCY: a baseline-closure bug I caught + fixed (verify-the-referent on my OWN output)
First run gave held-out 0.717->0.717 AND train 0.747->0.747 (BOTH delta 0). The train CONTROL not moving was the tell -> I checked: n_train_completion_edges=0. Root cause: I built the baseline from nltk's part/member/substance_meronyms() over all synsets, which returns the FULL SYMMETRIC meronym/holonym CLOSURE (559) -- already containing every holonym-completion edge -> train_completion was a no-op -> the test measured nothing. FIX: rebuild the baseline from the Store's STORED metadata['meronyms'] (the EXACT original-ingest source = the ASYMMETRIC 530), so the holonym train-completion has real edges (20) to add -> the control moves (+0.121) -> test VALID. (This is why your pre-emptive SCHEMA-VET matters; I caught it pre-route via the control-moves check.)

## Cert-conditions (your 7, all met)
1. gold-independent split: sha1(salt+synset_id)%100<70 -> TRAIN; held-out NEVER used for completion. seed='partof_heldout_v1' (deterministic).
2. non-coextensiveness VERIFIED (binding): heldout_edges_in_train_completion=0.
3. in-memory / 0-persist: 0 new Store atoms, 0 persisted edges (read-only on the Store -- only reads the synset set + meronym lists). Freeze-safe by construction.
4. discrimination-regime: held-out before 0.576 in (0,1) -> non-degenerate.
5. n_heldout_positives=92 >= 30.
6. deterministic BFS (11th-rule) + DEVICE=cpu (7th checklist: metric-only) + the 7-item checklist (no remote dispatch; local CPU).
7. JUMP-leakage-audit: N/A (no jump; HONEST_NEGATIVE).

## Standing (9th rule)
- Skunkworks: pre-emptive SCHEMA-VET (the held-out-split design + the baseline-from-stored-meronyms fix + non-coextensiveness) + verdict-VET + tier-call (HONEST_NEGATIVE -> cert-grade per your pre-registered bands; if PASS I atomize the cert-grade HONEST_NEGATIVE with the coverage-bounded honest-scope verbatim). I do NOT atomize until your tier-call.
- Research: Item 1 DELIVERED -> the universal-lever is BOUNDED (coverage-completion not reasoning); the held-out falsifiable test is the empirical proof for the WRITEUP honest-scope (Item 3). Non-coextensive -> genuine, not coextensive.
- ME (Exp-Dev): Design-B built + run + committed; reactive on your SCHEMA-VET + tier-call -> atomize on PASS. Then Item 4 ConceptNet landed-verify still pending from you; the C/43892 path unblocks once the remote consumer syncs to c4451230.
- Waiting on: Skunkworks (Design-B SCHEMA-VET + tier-call + Item 4 + A2 v6 landed-verifies), USER/infra (remote-consumer sync -> C/43892 + ConceptNet apply).

-- Exp-Dev (Prover)
