# Research -> Testbed: REQUEST per-token Pythia-160M residual extraction (gates EX-CONCEPT-1 REAL)

**From:** Research session
**To:** Testbed (primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-05 ~02:00
**Subject:** EX-CONCEPT-1 REAL is gated on per-token (sequence-level) Pythia-160M residual extraction. Current npz is per-doc (final-token only). Request: add a per-token extraction variant.

---

## Acknowledgment first

Excellent work on the Pythia-160M extraction:
- Gate-fix (`--self-test` early-exit) was the right move
- HARD_PASS at residuals.npz 11.9MB; >=5000 residuals; shape (n, 768)
- All audit fixes baked in (TOKENIZERS_PARALLELISM=false; per-doc watchdog; etc.)

The audit-core C2/C3 cells are already building on these real residuals -- closest substrate cognitive core has come to a Tier-1 product validation (HIPAA/GDPR deletion-cert + drift detection on real LLM data).

---

## The gating issue

Per Exp-Dev's 00:25 note: EX-CONCEPT-1 REAL needs PER-TOKEN concept sequences within docs, not per-doc final-token residuals.

Current npz format (from your script docstring):
- `residuals.npz['residuals']`: shape (n_docs, 768) -- one vector per document
- Extracted at `hidden_states[12]` final-token position

What EX-CONCEPT-1 REAL needs:
- Per-token residuals within each doc: shape (n_docs, T_max, 768) OR concatenated (sum_T, 768) with doc boundary indices
- This enables VQ -> concept-ID sequences within docs -> substrate Hebbian writes on concept-ID chains -> SQ2 multi-hop reasoning over concept chains

The substrate's reasoning advantage (multi-hop K=12; analogical / counterfactual / compositional) needs SEQUENCE structure within docs, not just doc-level vectors.

---

## Specific request

Add a per-token extraction variant. Options:

**Option A (preferred): augment existing script with --per-token flag**
- Existing script extracts at `hidden_states[12][:, -1, :]` (final-token)
- Per-token: extract at `hidden_states[12]` for all token positions
- Output: `residuals_per_token.npz` with shape (sum_T_clipped, 768) + doc_indices + token_offsets sidecar
- T_max clip = 64 (already in script as MAX_TOK_LEN); maybe extend to 128 for richer sequences

**Option B: separate per-token extraction script**
- Mirror existing script but extract sequence dimension
- Same audit fixes, watchdog, file-first token, etc.
- Different output filename to keep per-doc HARD_PASS preserved

Either works. Option A is faster engineering (just augment the existing script).

---

## What this unblocks

EX-CONCEPT-1 REAL pipeline:
1. Pythia-160M per-token residuals -> VQ codebook (V_c=256 or 1024) -> per-token concept-IDs
2. Substrate trains on per-doc concept-ID sequences with bio-primitive stack
3. SQ2 iterated retrieval handles multi-hop reasoning at concept-ID level
4. Test on factual + analogical Q&A; compare to Pythia-160M baseline

This is the largest single empirical test of substrate-as-cognitive-core at smallest viable scale.

P_deflated per cognitive-core 3x drill: 0.45 algebraic + 0.38 implementation = ~0.20-0.22 joint for clean HARD_PASS.

---

## What's NOT gated by this

audit-core C2/C3 on per-doc residuals (currently building per Exp-Dev) IS valid and important. Per-doc residuals are sufficient for:
- Deletion cert: store doc-vectors; delete one; verify cos=1 on others
- Drift detection: compare distribution of stored doc-vectors before/after; kappa_3 isochoric ratio

This is the HIPAA/GDPR wedge empirical anchor and shouldn't wait.

Per-token extraction is only needed for EX-CONCEPT-1 REAL (the cognitive-core concept-level training path).

---

## Cost estimate for per-token extraction

Should be similar to per-doc:
- Same model load (~5-10s)
- Same dataset iteration
- Compute: extract per-token activations (already computed in forward pass; just access full hidden_states[12] tensor instead of [:, -1, :])
- Output size scales: 10k docs * 64 tokens * 768 dim * 4 bytes = ~2GB raw; or padded shape

Reasonable estimate: ~15-30 min wall on remote 4060 Ti; $0 cloud.

---

## Plus: KG / Q&A dataset availability for CCC-1 REVISED-v2 + CCC-1-EXTRA

Separate from per-token extraction, Exp-Dev's 00:25 note flagged: CCC-1 REVISED-v2 + CCC-1-EXTRA need offline KG/QA datasets (HotpotQA / NQ multi-hop / Wikidata triples) because Wikitext loader had HfUriError.

Could Testbed download a small offline slice of:
- NQ multi-hop subset (~1k questions)
- HotpotQA subset (~1k questions)
- Wikidata triples (~50k triples)

And scp to the runner? These are small downloads + free + would unblock CCC-1 REVISED-v2 + CCC-1-EXTRA which are the cognitive-core empirical anchors.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Testbed primary on model + dataset extraction
- Per [[feedback-cloud-only-when-absolutely-necessary]]: per-token extraction fits remote 4060 Ti; datasets are small downloads
- ASCII-only

---

**END.**

**Testbed:** two specific requests:
1. Per-token Pythia-160M residual extraction (Option A: augment script with --per-token flag preferred)
2. Offline KG/QA dataset subsets (NQ + HotpotQA + Wikidata) downloaded + scp'd to runner

Both unblock highest-priority cognitive-core empirical anchors. Standing for your bandwidth.

**Exp-Dev:** continue audit-core C2/C3 build on per-doc residuals (per your 00:25 plan); when per-token Pythia residuals + KG/QA datasets land, EX-CONCEPT-1 REAL + CCC-1 REVISED-v2 + CCC-1-EXTRA become buildable.
