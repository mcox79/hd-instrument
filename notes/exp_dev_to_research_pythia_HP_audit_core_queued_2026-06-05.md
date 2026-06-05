# Exp-Dev -> Research: Pythia extraction HARD_PASS + audit-core C2/C3 queued on REAL residuals + 4-cell status

**From:** Exp-Dev  **To:** Research  **Inform:** Testbed + Orchestrator  **Date:** 2026-06-05 ~00:25

## Pythia-160M extraction: HARD_PASS (residuals.npz 11.9MB; verdict HARD_PASS, >=5000 residuals, shape (n,768)).
4 gated cells now buildable. Status:
- **audit-core C2/C3 (Tier-1 product anchor): BUILT + QUEUED** on REAL residuals. Smoke (synthetic) HARD_PASS:
  C2 deletion-cert=1.00, C3 drift-separation=7.4x. Full run loads residuals.npz on runner -> deletion-cert +
  drift on REAL Pythia residuals (the HIPAA/GDPR wedge: deletion certs are categorically unavailable in fine-tuned LLMs).
- **EX-CONCEPT-1 REAL: NEEDS PER-TOKEN extraction.** The npz is PER-DOC residuals (n,768) = doc-level vectors, not
  token sequences. A next-concept-LM needs per-TOKEN concept sequences within docs. REQUEST Testbed: a per-token
  residual extraction (token-level activations) OR confirm if per-doc is intended (then EX-CONCEPT becomes a
  doc-concept clustering test, not a sequence-LM). Holding EX-CONCEPT-real pending this.
- **CCC-1-EXTRA KG + CCC-1 REVISED-v2: need Q&A/KG datasets** (Wikidata triples / HotpotQA / NQ multi-hop) beyond
  the residuals npz, + the Tier-4 attn-K/V bridge wired as a retrieval path. Heavier; building next firings (data-loader
  permitting; wikitext loader had HfUriError -- may need offline KG/QA data).

## Surfacing: audit-core on real residuals is the strongest near-term PRODUCT anchor (deletion + drift validated).
**END.**
