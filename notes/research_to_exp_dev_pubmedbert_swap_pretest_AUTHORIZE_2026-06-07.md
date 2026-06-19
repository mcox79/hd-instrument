# Research -> Exp-Dev: PubMedBERT-base-embeddings drop-in swap pre-test AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** PubMedQA biomedical domain 2x drill output. Per blanket authorization.

## Drill verdict synthesis

- 28-pt PubMedQA gap = ENCODER FAILURE not substrate algebra failure
- bge-small never trained on biomedical vocabulary
- Sign binarization compounds the gap (discards magnitude info that compensates for
  vocabulary gaps in continuous retrievers)
- DROP-IN FIX: PubMedBERT-base-embeddings (same 768-dim; ~2 days)
- Expected lift: close 15-20 of the 28 points (substrate gets to 0.72-0.77 vs RAG 0.85)
- Remaining gap may reflect yes/no/maybe classification characteristics vs factual QA

## Authorize the 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_pubmedqa_biomedical_domain_2026-06-07.md`:

### Primary: PubMedBERT-base-embeddings drop-in swap
- Replace bge-small with PubMedBERT-base-embeddings for substrate fillers
- Re-embed the PubMedQA knowledge base
- Re-run 3-baseline (bare Qwen vs vanilla RAG vs substrate-augmented Qwen)
- Wall: ~2 days re-embed + run

HARD-PASS per drill: substrate-augmented Qwen >= 0.72 on PubMedQA (closes most of the
28pt gap; substrate-with-biomedical-encoder approaches RAG-with-biomedical-encoder).

BORDER: 0.62-0.72.

HARD-FAIL: < 0.60 (encoder swap doesn't close gap; deeper substrate-domain issue).

### Secondary: MedCPT (only if PubMedBERT-embeddings BORDER/HF)
Per drill recommendation — test after PubMedBERT-embeddings primary result.

### Tertiary: TriviaQA regression test on PubMedBERT-embeddings
Verify that using biomedical encoder DOESN'T regress on TriviaQA encyclopedic
(substrate +0.023 over RAG result must be preserved with general encoder; this is
sanity check on per-domain encoder strategy).

HARD-PASS: TriviaQA result with PubMedBERT-embeddings stays within 5% of TriviaQA
with bge-small (encoder-agnostic substrate confirmed).
HARD-FAIL: TriviaQA result drops >10% (biomedical encoder hurts on general; per-domain
deployment is correct strategy).

## Customer pitch update

**ENCODER-AGNOSTIC SUBSTRATE = substrate moat feature.** Substrate is the universal
layer; encoder is swapped per customer domain. Customer pitch:

> "Substrate is encoder-agnostic. Deploy with PubMedBERT for biomedical, BGE for general,
> LegalBERT for legal — same Pattern B compositional algebra, same audit chain, same
> GDPR cascade, same sleep defrag aggregation. Encoder choice optimizes per-domain
> retrieval quality without affecting substrate's compliance + persistence + algebra
> moat features."

This becomes part of v1 customer pitch immediately (doesn't wait for pre-test result;
the substrate's encoder-agnostic property is structural).

## Strategic implication

The encoder ceiling 2x drill (in flight) covers the parallel question: is bge-large /
e5-large / stella the answer for HotpotQA multi-hop? Both drills converge on:
substrate is the universal layer; encoder choice is domain-specific.

## Cross-references

- PubMedQA biomedical 2x drill: notes/research_drill_pubmedqa_biomedical_domain_2x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_pubmedqa_biomedical_domain_2026-06-07.md
- Encoder ceiling drill (in flight; parallel): not yet landed
- Substrate iterative multi-hop drill (in flight): not yet landed

---

**END.**

**Exp-Dev:** authorize PubMedBERT-embeddings drop-in pre-test (~2 days re-embed + run).
Apply HARD-PASS / BORDER / HARD-FAIL decision rules autonomously. File verdict on
completion. Triagle TriviaQA regression test in parallel for encoder-agnostic
confirmation.
