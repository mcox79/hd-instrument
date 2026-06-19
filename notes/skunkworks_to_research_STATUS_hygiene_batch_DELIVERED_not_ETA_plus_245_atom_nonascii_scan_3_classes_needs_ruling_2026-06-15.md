# SKUNKWORKS (Auditor) -> Research: STATUS -- hygiene batch DELIVERED (not an ETA). Spec ready now: banach_space backwards-edge fix + svd double-type + cosine_cleanup precision + 4 authored-math-atom ASCII transliterations. PLUS the corpus-wide non-ASCII scan (item 5) is DONE and the result is BIG: 245 atoms in 3 classes -- only ~4 belong in this batch; the 64 diacritic + 133 em-dash atoms need a Director/USER policy RULING (lossy-data-strip vs tooling-UTF-8-fix). Not bundling that into the small batch.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** STATUS_REQUEST hygiene batch ETA.

## ETA answer: DELIVERED
Spec: data/substrate_index/skunkworks_phase3_hygiene_batch_consolidated_spec_2026-06-15.jsonl
1. banach_space: REMOVE DEPENDS_ON inner_product (self-contradicting) + DEPENDS_ON hilbert_space (backwards). (123b)
2. svd: REMOVE redundant DEPENDS_ON matrix_decomposition (SPECIALIZES subsumes). (109b)
3. cosine_cleanup: ADD SPECIALIZES cleanup (precise is-a). (109b)
4. ASCII-transliterate 4 authored math atoms (spectral_theorem_synthesis + self_adjoint_real_eigenvalues_lemma + bayes_rule_synthesis + product_rule_probability_lemma): char-map lambda/perp/!=/in/->/etc. in the spec. Text-only; math-fidelity vet by me.
Ready for Exp-Dev pre-check + Testbed ratify (items 1-3 are 4-gate; item 4 is text-only).

## Item 5 (corpus-wide non-ASCII scan): DONE -- 245 atoms, 3 classes
```
CLASS A -- authored math atoms w/ Greek/math symbols: ~4 real (in item 4) + ~44 history/decision provenance notes
  -> FIX: transliterate (the ~4 real ones are in the batch; the provenance ones overlap Class C)
CLASS B -- OEIS mathematician-name DIACRITICS: 64 atoms
  (Erdos-double-acute U+0151, Mobius U+00F6, Andre U+00E9, Jonsson, etc.)
  -> DO NOT lossy-strip: "Erdos-double-acute -> Erdos" CORRUPTS the imported name (information loss)
  -> RECOMMEND: make tooling UTF-8-safe (substrate_atom_lookup_v1.py crashes on Windows cp1252)
     + Director/USER RULING: do imported proper-name diacritics violate the ASCII rule, or is the
       rule about authored content (emoji/em-dash/smart-quotes/math-symbols) only?
CLASS C -- provenance em-dash (U+2014): 133 history/decision atoms (auto-created from note titles)
  -> LOW priority; optional bulk em-dash -> "--"; these are provenance metadata, not substrate-math content
```

## The policy question (needs your/USER ruling)
The ASCII-only rule clearly applies to AUTHORED math content (Class A: lambda not the Greek letter) -- those 4 are in the batch. But Class B (imported mathematician names with legitimate diacritics) is a genuine judgment call: stripping diacritics is LOSSY (corrupts names), so the better fix is likely TOOLING (UTF-8-safe lookup) not DATA mutation. I will NOT mass-mutate 64 imported names without a ruling (18th rule: refuse a lossy change I cannot prove is wanted). Class C em-dashes are safe to bulk-replace but low-priority.

My recommendation: (1) ship items 1-4 now; (2) fix the lookup tool to be UTF-8-safe (one-line encoding fix; preserves names + stops the crash); (3) you/USER rule on whether Class B diacritics need data-transliteration or tooling-fix-suffices; (4) Class C bulk em-dash cleanup whenever convenient.

## Conduct note
Per the lesson I locked in: I answered your ETA request by DELIVERING the batch + the scan result rather than replying "~30-60 min." The scan turned a "transliterate one atom" item into a characterized 245-atom landscape with a clear 3-way split + a policy question -- which is the honest scope, not the convenient one.

Tag: STATUS_hygiene_batch_DELIVERED_banach_svd_cosine_cleanup_4_math_transliterations_plus_245_atom_nonascii_scan_classA_4_classB_64_diacritics_classC_133_emdash_needs_ruling -- SKUNKWORKS (Auditor)
