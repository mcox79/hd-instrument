# Pre-registration: wave14zk_noisy_edit_keys

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new dimension — edits via approximate/perturbed key
Author: experiment_dev session, pipeline tick 47

## Why
yb tested edit-then-query with EXACT keys at edit time. In a deployed system,
the editor might not have the exact stored key — they might have a paraphrase
or noisy version. Snap-to-codebook handles paraphrase queries on Kerdock, but
what about paraphrase edits?

Test: at edit time, perturb keys[i] by Hamming radius h, then either snap to
codebook (Kerdock arm) or use raw (correlated). Run erase + insert. Then query
at exact k_i. Did the edit land correctly?

Edit landing at perturbed key is genuinely product-relevant — many real workflows
have inexact lookups.

## Verdict labels
- NOISY_EDIT_KERDOCK_PASS
- NOISY_EDIT_BOTH_PASS
- NOISY_EDIT_KERDOCK_DEGRADES_AT_H<H>
- NOISY_EDIT_BOTH_FAIL
- NOISY_EDIT_INCONCLUSIVE

## Runtime: ~5 min
