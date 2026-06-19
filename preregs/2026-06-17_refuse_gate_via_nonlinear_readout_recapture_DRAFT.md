# PREREG (DRAFT): Refuse-gate RECAPTURE via NONLINEAR readout (attention-concentration) -- V1 YELLOW recapture

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT (nonlinear-readout frontier; pivot seq #2) -- pending Skunkworks SCHEMA-VET (incl. ANCHOR-MECHANISM-MATCH) + Director STEP-2 LOCK.
**Source:** Director Option-C-B-first pivot (research_to_exp_dev_skunkworks_RATIFY_option_C...); Skunkworks flagged this as the natural recapture of the V1 refuse-gate YELLOW. Lit: ARCH-B (modern-Hopfield/softmax) + drill-1 (sparse-Hopfield-entmax).
**Recaptures:** PHASE-V1 6th production module refuse_gated_retriever -- YELLOW (entry-LIVE; M1 confidence-tau-gate HARD_FAIL: no tau achieves gap-refuse>=0.95 without in-coverage F1-drop>0.05; "substrate cannot separate present-gold-PARAPHRASED from ABSENT-gold by bge confidence alone").

## ANCHOR-MECHANISM-MATCH (the new check; VERIFIED before drafting)
- ANCHOR's actual limiter: a LINEAR/SCALAR readout -- a single bge-cosine-confidence threshold (tau) -- cannot
  distinguish "high-cosine because PARAPHRASE-of-a-PRESENT item" from "high-cosine but item is ABSENT." The separation
  fails because raw cosine confidence is the wrong (linear) signal.
- RECAPTURE: replace the linear confidence threshold with a NONLINEAR readout's ATTENTION-CONCENTRATION as the refuse
  signal (softmax/modern-Hopfield attention over the stored index). MECHANISM MATCHES (readout <-> readout): the refuse-
  gate IS a readout/separation; swapping linear-cosine -> nonlinear-attention is the ARCH-B-confirmed lever applied to
  the refuse-separation. (Anchor-match holds -- not an 18-style mismatch.)

## Hypothesis (mechanistic; on the ARCH-B-confirmed lever)
A modern-Hopfield/softmax readout CONCENTRATES attention onto a stored pattern when the query genuinely matches one
(present, incl. paraphrase -> sharp, high max-weight) and stays DIFFUSE when no stored pattern matches (absent -> low
max-weight, high entropy). So the refuse signal = ATTENTION-CONCENTRATION (softmax max-weight or 1-entropy), NOT raw
cosine. This should separate present-paraphrased (concentrated) from absent-gold (diffuse) where the scalar cosine could
not. HONEST-NEGATIVE acceptable: if even the nonlinear readout can't separate them, the fuzzy-separation limit is deeper
than the readout (a real bounded finding -> the refuse capability needs more than a readout swap; e.g. a learned adapter).

## Design (readout-swap on the refuse-separation; same held-out eval as the M1 anchor)
```
BASE: the m1_refuse_gate held-out eval harness (exp_substrate_m1_refuse_gate_heldout_tau_sweep; q54-q65 held-out; bge
   index of present-gold). Same coverage decomposition (in-coverage F1 vs PRESENT-gold; coverage-gap refuse-rate).
SWAP: refuse signal = NONLINEAR readout over the bge index instead of the scalar-cosine tau gate:
   weights = softmax(beta * cos(query, stored_keys)); refuse iff CONCENTRATION < c  (concentration = max(weights) OR
   1 - normalized_entropy(weights)); accept + return argmax iff concentration >= c. Sweep beta + the concentration
   threshold c. (Compare: M1 baseline = scalar-cosine tau gate.) OPTIONAL secondary: entmax (drill-1 C1) sparse readout.
METRIC (same bars as the M1 anchor): coverage-gap refuse-rate + IN-COVERAGE F1 (vs PRESENT-gold). PRIMARY = does a
   (beta, c) exist with gap-refuse-rate >= 0.95 AND in-coverage-F1-drop <= 0.05 (the bar M1's scalar cosine FAILED)?
SEEDS: held-out is fixed; report per-query + the (beta,c) frontier. COMPUTE: bge + held-out -> REMOTE; CONTROLLED
   ONE-SHOT eval-reproduction (22nd-rule firewall: eval not training; not repeated laptop peeking).
```

## DISCRIMINATING-REGIME guard
```
The held-out set MUST contain BOTH present-paraphrased AND absent-gold queries in a discriminating mix (if all-present
or all-absent, refuse-separation is degenerate -> NON-TEST). Confirm the M1 scalar-cosine baseline is between floor
(refuse-nothing) and ceiling (oracle present/absent labels) so a nonlinear lift is detectable. Report the present/absent
composition of q54-q65. (DEGENERATE-REGIME-NOT-REFUTATION class; refuse-separation instance.)
```

## Pre-registered bands
```
HARD-PASS (RECAPTURE): exists (beta, c) with coverage-gap refuse-rate >= 0.95 AND in-coverage F1-drop <= 0.05 (5/5-style
   robustness across the held-out splits) -> the nonlinear-readout attention-concentration RECAPTURES refuse-robustness
   the linear confidence-gate could not. (Production V1 module recovery + capability-frontier extension simultaneously.)
HARD-FAIL: no (beta, c) reaches gap-refuse >= 0.95 without F1-drop > 0.05 -> nonlinear readout does NOT separate present-
   paraphrased from absent-gold either; the fuzzy-separation limit is DEEPER than the readout (honest bound; next = a
   learned cross-domain adapter, NOT a readout swap). Refuse-gate stays YELLOW (soundness-bounded).
MIDDLE_BAND: improves on M1 (gap-refuse up OR F1-drop down) but does not clear both bars -> partial; bounded.
```

## Provenance (recapture_of populated per Skunkworks ruling B)
- recapture_of = PHASE_V1_6th_module_refuse_gated_retriever_YELLOW (m1_refuse_gate HARD_FAIL @ gap-refuse>=0.95 /
  F1-drop<=0.05; bge-confidence cannot separate present-paraphrased from absent-gold)
- failing_config_avoided = a LINEAR/SCALAR bge-cosine-confidence threshold (tau) as the refuse signal -- cannot
  distinguish paraphrase-of-present from absent (both high-cosine)
- method_delta = NONLINEAR readout ATTENTION-CONCENTRATION (softmax/modern-Hopfield max-weight / 1-entropy) as the refuse
  signal instead of scalar cosine -- the ARCH-B-confirmed nonlinear-readout lever applied to the refuse-separation.
  readout <-> readout anchor-match. (Optional entmax sparse variant = composes with C1.)
- CERT_CHAIN_GRADE on the held-out eval; measured-bounds: envelope of THIS nonlinear-readout refuse method at the
  q54-q65 held-out regime; transfer to other held-out sets UNTESTED.

## Cross-cutting value (why this is high-leverage; Director pivot rationale)
Single cell = (a) production V1 refuse_gated_retriever module recovery (YELLOW -> potentially GREEN), AND (b) capability-
frontier extension on the ARCH-B nonlinear-readout lever (the bridge between STRONG exact and WEAK fuzzy positioning),
AND (c) directly attacks the fuzzy-confidence-separation / held-out-retrieval weak-spot (Skunkworks corpus synthesis).

## Cert-chain next steps
1. Skunkworks SCHEMA-VET WITH anchor-mechanism-match check (readout<->readout confirmed above) + falsifiable bands +
   no-Goodhart (gap-refuse + F1 ARE the refuse claim) + discriminating-regime guard (present/absent mix) + measured-bounds
   + 22nd-rule firewall (controlled one-shot REMOTE eval).
2. Director STEP-2 LOCK.
3. Exp-Dev cell-author (nonlinear-readout refuse harness over the bge index + concentration sweep) + smoke (tiny synthetic
   present/absent set, laptop -- NO held-out) -> FULL (REMOTE, held-out q54-q65, one-shot) -> verdict -> re-atomize.

## Pivot-sequence note
Nonlinear-readout frontier, Director Option-C-B-first seq #2 (after C1 entmax, which is awaiting Skunkworks SCHEMA-VET).
Composes with C1 (entmax = the sparse variant of this nonlinear readout). 8b re-design deferred; 8a drafted (Day-N); 18 de-scoped.

-- Exp-Dev (Prover) [DRAFT]
